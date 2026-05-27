"""Configuration management for the game."""

import json
from pathlib import Path
from typing import Any, Optional

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
        "language": "en",
    }

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize configuration.

        Args:
            config_path: Path to the configuration file.
        """
        from .paths import get_app_data_path

        if config_path is None:
            self.config_path = get_app_data_path("data/config.json")
        else:
            self.config_path = Path(config_path)
        self._config: dict[str, Any] = {}
        self.load()

    def _backup_file(self) -> None:
        """Safely backup the corrupted config file with incrementing suffix."""
        if not self.config_path.exists():
            return
        import sys

        # Try .bak
        bak_path = self.config_path.with_suffix(self.config_path.suffix + ".bak")
        if not bak_path.exists():
            try:
                self.config_path.replace(bak_path)
                return
            except Exception as e:
                print(
                    f"Warning: Could not backup config to {bak_path}: {e}",
                    file=sys.stderr,
                )
                try:
                    import shutil

                    shutil.copy2(self.config_path, bak_path)
                    self.config_path.unlink()
                    return
                except Exception as e2:
                    print(
                        f"Warning: Fallback config backup failed: {e2}", file=sys.stderr
                    )

        # Try .bak.1, .bak.2, etc.
        idx = 1
        while True:
            candidate = self.config_path.with_suffix(
                self.config_path.suffix + f".bak.{idx}"
            )
            if not candidate.exists():
                try:
                    self.config_path.replace(candidate)
                    return
                except Exception as e:
                    print(
                        f"Warning: Could not backup config to {candidate}: {e}",
                        file=sys.stderr,
                    )
                    try:
                        import shutil

                        shutil.copy2(self.config_path, candidate)
                        self.config_path.unlink()
                        return
                    except Exception as e2:
                        print(
                            f"Warning: Fallback config backup failed: {e2}",
                            file=sys.stderr,
                        )
                break
            idx += 1

    def load(self) -> None:
        """Load configuration from file."""
        import sys

        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Merge default values for missing keys to preserve other keys
                        self._config = self.DEFAULT_CONFIG.copy()
                        for k, v in data.items():
                            self._config[k] = v
                    else:
                        print(
                            "Warning: Config is not a dictionary. Fallback to default.",
                            file=sys.stderr,
                        )
                        self._backup_file()
                        self._config = self.DEFAULT_CONFIG.copy()
                        self.save()
            except (json.JSONDecodeError, OSError) as e:
                print(
                    f"Warning: Could not load config: {e}. Rebuilding.", file=sys.stderr
                )
                self._backup_file()
                self._config = self.DEFAULT_CONFIG.copy()
                self.save()
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self.save()

        # Synchronize active theme with loaded config
        from .constants import set_theme

        set_theme(self.get_string("theme", "nord_blue"))

        # Synchronize active language with loaded config
        from .i18n import normalize_language, set_language

        raw_lang = self.get_string("language", "en")
        normalized_lang = normalize_language(raw_lang)
        self._config["language"] = normalized_lang
        set_language(normalized_lang)

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

    def get_language(self) -> str:
        """Get current language setting."""
        return self.get_string("language", "en")

    def set_language(self, language: str) -> None:
        """Set language setting and sync i18n state."""
        from .i18n import normalize_language, set_language

        normalized = normalize_language(language)
        self.set("language", normalized)
        set_language(normalized)

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()
        from .constants import set_theme

        set_theme(self.get_string("theme", "nord_blue"))

        # Synchronize active language
        from .i18n import set_language

        set_language(self.get_string("language", "en"))
