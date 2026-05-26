"""Configuration management for the game."""

import json
from pathlib import Path
from typing import Any

from .constants import ControlScheme


class Config:
    """Game configuration manager."""

    DEFAULT_CONFIG = {
        "control_scheme": ControlScheme.ARROWS,
        "sound_enabled": True,
        "sound_volume": 0.5,
        "music_enabled": True,
        "music_volume": 0.3,
        "fullscreen": False,
        "window_width": 1024,
        "window_height": 768,
        "animation_enabled": True,
        "show_tutorial": True,
        "theme": "default",
    }

    def __init__(self, config_path: str = "data/config.json") -> None:
        """Initialize configuration.

        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not load config: {e}")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self.save()

        # Synchronize active theme with loaded config
        from .constants import set_theme

        set_theme(self.get_string("theme", "nord_blue"))

    def save(self) -> None:
        """Save configuration to file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"Warning: Could not save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)

    def get_string(self, key: str, default: str = "") -> str:
        """Get a string configuration value with type safety."""
        value = self.get(key, default)
        return value if isinstance(value, str) else default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value with type safety."""
        value = self.get(key, default)
        return value if isinstance(value, bool) else default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key.
            value: Value to set.
        """
        self._config[key] = value
        self.save()
        if key == "theme":
            from .constants import set_theme

            set_theme(value)

    def get_control_scheme(self) -> str:
        """Get current control scheme."""
        return self.get_string("control_scheme", ControlScheme.ARROWS)

    def set_control_scheme(self, scheme: str) -> None:
        """Set control scheme."""
        if scheme in [ControlScheme.ARROWS, ControlScheme.WASD]:
            self.set("control_scheme", scheme)

    def is_animation_enabled(self) -> bool:
        """Check if animations are enabled."""
        return self.get_bool("animation_enabled", True)

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()
        from .constants import set_theme

        set_theme(self.get_string("theme", "nord_blue"))
