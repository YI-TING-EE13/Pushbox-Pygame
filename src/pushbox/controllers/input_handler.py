"""Input handling for keyboard controls."""

from typing import Callable

import pygame

from ..utils.config import Config
from ..utils.constants import ControlScheme, Direction


class InputHandler:
    """Handles keyboard input for the game."""

    # Key mappings for different control schemes
    ARROW_KEYS = {
        pygame.K_UP: Direction.UP,
        pygame.K_DOWN: Direction.DOWN,
        pygame.K_LEFT: Direction.LEFT,
        pygame.K_RIGHT: Direction.RIGHT,
    }

    WASD_KEYS = {
        pygame.K_w: Direction.UP,
        pygame.K_s: Direction.DOWN,
        pygame.K_a: Direction.LEFT,
        pygame.K_d: Direction.RIGHT,
    }

    # Common action keys
    # Note: Some actions (pause, settings, global editor shortcut) are defined here
    # but the full UI flow for them is not yet implemented in v0.1.0.
    ACTION_KEYS = {
        "undo": [pygame.K_z, pygame.K_BACKSPACE],
        "redo": [pygame.K_y, pygame.K_r],
        "reset": [pygame.K_F5, pygame.K_DELETE],
        "pause": [pygame.K_ESCAPE, pygame.K_p],
        "menu": [pygame.K_m],
        "editor": [pygame.K_e],
        "help": [pygame.K_h, pygame.K_F1],
        "settings": [pygame.K_F2],
    }

    def __init__(self, config: Config) -> None:
        """Initialize input handler.

        Args:
            config: Game configuration.
        """
        self.config = config
        self._key_repeat_delay = 200  # milliseconds
        self._key_repeat_interval = 50
        self._last_key_time: dict[int, int] = {}
        self._key_states: dict[int, bool] = {}

        # Callbacks
        self._callbacks: dict[str, list[Callable[..., None]]] = {
            "move": [],
            "undo": [],
            "redo": [],
            "reset": [],
            "pause": [],
            "menu": [],
            "editor": [],
            "help": [],
            "settings": [],
        }

    def register_callback(self, action: str, callback: Callable[..., None]) -> None:
        """Register a callback for an action.

        Args:
            action: Action name.
            callback: Function to call.
        """
        if action in self._callbacks:
            self._callbacks[action].append(callback)

    def unregister_callback(self, action: str, callback: Callable[..., None]) -> None:
        """Unregister a callback.

        Args:
            action: Action name.
            callback: Function to remove.
        """
        if action in self._callbacks and callback in self._callbacks[action]:
            self._callbacks[action].remove(callback)

    def _trigger(self, action: str, *args: object, **kwargs: object) -> None:
        """Trigger all callbacks for an action."""
        for callback in self._callbacks.get(action, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Error in callback for {action}: {e}")

    def get_movement_keys(self) -> dict[int, tuple[int, int]]:
        """Get current movement key mapping.

        Returns:
            Dictionary mapping keys to directions.
        """
        scheme = self.config.get_control_scheme()

        if scheme == ControlScheme.WASD:
            return self.WASD_KEYS.copy()
        else:  # Default to arrows
            return self.ARROW_KEYS.copy()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a pygame event.

        Args:
            event: Pygame event.

        Returns:
            True if event was handled.
        """
        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self._key_states[event.key] = False
            self._last_key_time.pop(event.key, None)

        return False

    def _handle_keydown(self, key: int) -> bool:
        """Handle key down event.

        Args:
            key: Key code.

        Returns:
            True if handled.
        """
        current_time = pygame.time.get_ticks()

        # Check for key repeat
        if key in self._last_key_time:
            elapsed = current_time - self._last_key_time[key]
            if elapsed < self._key_repeat_delay:
                return False

        self._last_key_time[key] = current_time
        self._key_states[key] = True

        # Check movement keys
        movement_keys = self.get_movement_keys()
        if key in movement_keys:
            direction = movement_keys[key]
            self._trigger("move", direction)
            return True

        # Check action keys
        for action, keys in self.ACTION_KEYS.items():
            if key in keys:
                self._trigger(action)
                return True

        return False

    def update(self) -> None:
        """Update input state (for continuous key handling)."""
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        movement_keys = self.get_movement_keys()

        # Handle key repeat for movement
        for key, direction in movement_keys.items():
            if keys[key]:
                if key in self._last_key_time:
                    elapsed = current_time - self._last_key_time[key]
                    if elapsed >= self._key_repeat_delay + self._key_repeat_interval:
                        self._last_key_time[key] = current_time - self._key_repeat_delay
                        self._trigger("move", direction)

    def get_control_scheme_name(self) -> str:
        """Get human-readable control scheme name.

        Returns:
            Scheme name.
        """
        scheme = self.config.get_control_scheme()
        if scheme == ControlScheme.WASD:
            return "WASD"
        return "方向鍵"

    def toggle_control_scheme(self) -> str:
        """Toggle between control schemes.

        Returns:
            New scheme name.
        """
        current = self.config.get_control_scheme()
        new_scheme = (
            ControlScheme.WASD
            if current == ControlScheme.ARROWS
            else ControlScheme.ARROWS
        )
        self.config.set_control_scheme(new_scheme)
        return self.get_control_scheme_name()
