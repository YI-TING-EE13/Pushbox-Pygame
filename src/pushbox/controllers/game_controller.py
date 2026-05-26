"""Main game controller managing game flow."""

import time
from typing import Any, Callable, Optional

import pygame

from ..models.game_state import GameState
from ..models.level import Level, LevelManager
from ..models.save_manager import SaveManager
from ..utils.audio import AudioManager
from ..utils.config import Config
from ..utils.constants import CellType
from ..utils.constants import GameState as GameStateEnum
from .input_handler import InputHandler


class GameController:
    """Main controller for the game."""

    def __init__(self) -> None:
        """Initialize game controller."""
        from ..utils.paths import ensure_runtime_dirs

        ensure_runtime_dirs()

        # Initialize systems
        self.config = Config()
        self.audio = AudioManager()
        self.save_manager = SaveManager()
        self.level_manager = LevelManager()

        # Initialize pygame
        pygame.init()
        self.audio.initialize()

        # Game state
        self.current_level: Optional[Level] = None
        self.game_state: Optional[GameState] = None
        self.input_handler = InputHandler(self.config)
        self.is_paused = False
        self.is_playtest = False

        # Callbacks
        self._state_callbacks: dict[str, list[Callable[..., None]]] = {
            "win": [],
            "game_over": [],
            "move": [],
            "undo": [],
            "redo": [],
            "reset": [],
            "invalid_move": [],
            "box_on_target": [],
        }

        # Setup input callbacks
        self._setup_input_callbacks()

    def _setup_input_callbacks(self) -> None:
        """Setup input handler callbacks."""
        self.input_handler.register_callback("move", self._on_move)
        self.input_handler.register_callback("undo", self._on_undo)
        self.input_handler.register_callback("redo", self._on_redo)
        self.input_handler.register_callback("reset", self._on_reset)
        self.input_handler.register_callback("pause", self.toggle_pause)

    def register_callback(self, event: str, callback: Callable[..., None]) -> None:
        """Register a state change callback.

        Args:
            event: Event name.
            callback: Function to call.
        """
        if event in self._state_callbacks:
            self._state_callbacks[event].append(callback)

    def _trigger_event(self, event: str, *args: object, **kwargs: object) -> None:
        """Trigger event callbacks."""
        for callback in self._state_callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Error in event callback {event}: {e}")

    def load_level(self, level_name: str) -> bool:
        """Load a level.

        Args:
            level_name: Name of the level to load.

        Returns:
            True if level loaded successfully.
        """
        level = self.level_manager.get_level(level_name)
        if not level:
            return False

        self.current_level = level
        self.game_state = GameState(level)
        self.is_paused = False
        self.is_playtest = False
        self.input_handler.clear_input_state()
        return True

    def load_level_instance(self, level: Level, is_playtest: bool = False) -> None:
        """Directly load a Level instance (useful for level editor playtest).

        Args:
            level: Level instance to load.
            is_playtest: Whether this is a playtest session.
        """
        self.current_level = level
        self.game_state = GameState(level)
        self.is_paused = False
        self.is_playtest = is_playtest
        self.input_handler.clear_input_state()

    def get_current_level_name(self) -> Optional[str]:
        """Get current level name.

        Returns:
            Level name or None.
        """
        return self.current_level.name if self.current_level else None

    def get_available_levels(self) -> list[str]:
        """Get list of available level names.

        Returns:
            List of level names.
        """
        return self.level_manager.get_level_names()

    def _on_move(self, direction: tuple[int, int]) -> None:
        """Handle move input.

        Args:
            direction: Direction tuple (dr, dc).
        """
        if not self.game_state or self.is_paused:
            return

        success = self.game_state.move(direction)
        if success:
            self._trigger_event("move", direction)

            # Check if box was pushed onto a target
            if self.game_state.move_history:
                last_cmd = self.game_state.move_history[-1]
                if last_cmd.box_to:
                    br, bc = last_cmd.box_to
                    if (
                        self.current_level
                        and self.current_level.initial_grid[br, bc] == CellType.TARGET
                    ):
                        self._trigger_event("box_on_target", (br, bc))

            # Check for win/game over
            if self.game_state.status == GameStateEnum.WON:
                self._handle_win()
            elif self.game_state.status == GameStateEnum.GAME_OVER:
                self._trigger_event("game_over")
        else:
            if self.game_state.status == GameStateEnum.PLAYING:
                self._trigger_event("invalid_move")

    def _handle_win(self) -> None:
        """Handle level completion."""
        if not self.game_state or not self.current_level:
            return

        # Update save data
        stats = self.game_state.get_stats()
        is_record = False
        if not self.is_playtest and self.current_level.name != "Level 0":
            is_record = self.save_manager.update_level_progress(
                self.current_level.name,
                stats["moves"],
                stats["time_seconds"],
                stats["pushes"],
            )

        # Trigger callback
        self._trigger_event("win", stats, is_record)

    def _on_undo(self) -> None:
        """Handle undo input."""
        if self.is_paused:
            return
        if self.game_state and self.game_state.move_history:
            command = self.game_state.move_history[-1]
            if self.game_state.undo():
                self._trigger_event("undo", command)

    def _on_redo(self) -> None:
        """Handle redo input."""
        if self.is_paused:
            return
        if self.game_state and self.game_state.redo_stack:
            command = self.game_state.redo_stack[-1]
            if self.game_state.redo():
                self._trigger_event("redo", command)

    def _on_reset(self) -> None:
        """Handle reset input."""
        self.is_paused = False
        self.input_handler.clear_input_state()
        if self.game_state:
            self.game_state.reset()
            self._trigger_event("reset")

    def get_level_stats(self) -> dict[str, Any]:
        """Get current level statistics.

        Returns:
            Statistics dictionary.
        """
        if not self.game_state:
            return {}
        return self.game_state.get_stats()

    def get_level_progress(self) -> dict[str, Any]:
        """Get progress for current level.

        Returns:
            Progress dictionary.
        """
        if not self.current_level:
            return {}
        return self.save_manager.get_level_progress(self.current_level.name)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame event.

        Args:
            event: Pygame event.

        Returns:
            True if event was handled.
        """
        return self.input_handler.handle_event(event)

    def toggle_pause(self) -> None:
        """Toggle the pause state of the game."""
        if not self.game_state or self.game_state.status != GameStateEnum.PLAYING:
            return

        self.is_paused = not self.is_paused
        self.input_handler.clear_input_state()

        if self.is_paused:
            self._pause_start_time = time.time()
        else:
            if hasattr(self, "_pause_start_time"):
                pause_duration = time.time() - self._pause_start_time
                self.game_state.start_time += pause_duration

    def update(self) -> None:
        """Update game state."""
        self.input_handler.update()

        if self.game_state and not self.is_paused:
            self.game_state.update_time()

    def get_control_scheme(self) -> str:
        """Get current control scheme name.

        Returns:
            Control scheme name.
        """
        return self.input_handler.get_control_scheme_name()

    def toggle_control_scheme(self) -> str:
        """Toggle control scheme.

        Returns:
            New scheme name.
        """
        return self.input_handler.toggle_control_scheme()
