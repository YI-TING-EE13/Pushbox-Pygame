"""Audio manager for sound effects and music."""

import sys
from typing import Optional

import pygame

from .paths import get_resource_path


class AudioManager:
    """Manages game audio (sound effects and music).

    Provides robust loading, playback, and volume control with crash resilience.
    """

    _instance: Optional["AudioManager"] = None

    def __new__(cls) -> "AudioManager":
        """Singleton pattern instantiation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize audio manager."""
        if hasattr(self, "_initialized_state"):
            return
        self._initialized_state = True
        self._enabled = True  # Default to True
        self._sound_volume = 0.5
        self._music_volume = 0.3
        self._initialized = False
        self._sounds: dict[str, pygame.mixer.Sound] = {}

    def initialize(self) -> bool:
        """Initialize pygame.mixer and pre-load sound assets safely.

        Returns:
            True if initialization was successful.
        """
        if self._initialized:
            return True

        try:
            # Initialize pygame mixer defensively
            pygame.mixer.init()
            self._initialized = True
            self._load_all_sounds()
            return True
        except Exception as e:
            # System errors or missing sound cards should not crash the game
            print(
                f"Warning: Audio system failed to initialize (Silent Mode): {e}",
                file=sys.stderr,
            )
            self._initialized = False
            return False

    def is_enabled(self) -> bool:
        """Check if audio is enabled and successfully initialized."""
        return self._enabled and self._initialized

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable audio."""
        self._enabled = enabled

    def _load_all_sounds(self) -> None:
        """Pre-load sound effects safely.

        Missing/invalid assets must not crash the game.
        """
        sound_files = {
            "move": "move.wav",
            "push": "push.wav",
            "bump": "bump.wav",
            "target": "target.wav",
            "undo": "undo.wav",
            "redo": "redo.wav",
            "win": "win.wav",
            "click": "click.wav",
        }

        # Resolve assets path: src/pushbox/assets/sounds in dev
        assets_dir = get_resource_path("assets/sounds")

        for name, filename in sound_files.items():
            sound_path = assets_dir / filename
            try:
                if sound_path.exists():
                    # Load sound safely
                    sound = pygame.mixer.Sound(str(sound_path))
                    sound.set_volume(self._sound_volume)
                    self._sounds[name] = sound
            except Exception as e:
                print(
                    f"Warning: Failed to load sound {filename}: {e}",
                    file=sys.stderr,
                )

    def set_sound_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0) and update cached sounds."""
        self._sound_volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            try:
                sound.set_volume(self._sound_volume)
            except Exception:
                pass

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0). Currently unused, kept as a placeholder."""
        self._music_volume = max(0.0, min(1.0, volume))

    def play_sound(self, sound_name: str) -> None:
        """Play a sound effect safely by name.

        Args:
            sound_name: Name of the sound to play.
        """
        if not self.is_enabled():
            return

        sound = self._sounds.get(sound_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                # Catch-all exception to handle any runtime sound driver exceptions
                print(
                    f"Warning: Failed to play sound {sound_name}: {e}",
                    file=sys.stderr,
                )

    def play_move(self) -> None:
        """Play move sound effect."""
        self.play_sound("move")

    def play_push(self) -> None:
        """Play push sound effect."""
        self.play_sound("push")

    def play_bump(self) -> None:
        """Play bump (wall collision) sound effect."""
        self.play_sound("bump")

    def play_target(self) -> None:
        """Play box-on-target sound effect."""
        self.play_sound("target")

    def play_undo(self) -> None:
        """Play undo sound effect."""
        self.play_sound("undo")

    def play_redo(self) -> None:
        """Play redo sound effect."""
        self.play_sound("redo")

    def play_win(self) -> None:
        """Play game win sound effect."""
        self.play_sound("win")

    def play_click(self) -> None:
        """Play click sound effect."""
        self.play_sound("click")
