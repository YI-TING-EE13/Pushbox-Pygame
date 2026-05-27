"""Tests for Config manager: robustness, corrupted rebuilding, and key merging."""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.utils.config import Config


def test_missing_config_uses_default(tmp_path):
    """Test fallback to DEFAULT_CONFIG and write when config doesn't exist."""
    config_file = tmp_path / "config.json"
    assert not config_file.exists()

    cfg = Config(config_path=str(config_file))
    assert cfg.get("fullscreen") is False
    assert cfg.get("window_width") == 1024
    assert cfg.get("window_height") == 768

    # File should be automatically written to disk
    assert config_file.exists()
    with open(config_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data["window_width"] == 1024


def test_corrupted_config_json_rebuilds_and_backs_up(tmp_path, capsys):
    """Test corrupted config.json triggers safe backup and rebuilds."""
    config_file = tmp_path / "config.json"
    config_file.write_text("{corrupted json", encoding="utf-8")

    cfg = Config(config_path=str(config_file))
    assert cfg.get("window_width") == 1024

    # The corrupted file must have been backed up as config.json.bak
    bak_file = tmp_path / "config.json.bak"
    assert bak_file.exists()
    assert bak_file.read_text(encoding="utf-8") == "{corrupted json"

    # Original config file should be successfully rebuilt
    assert config_file.exists()
    with open(config_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data["window_width"] == 1024

    # Verify a warning was output to stderr
    captured = capsys.readouterr()
    assert "Could not load config" in captured.err or "Rebuilding" in captured.err


def test_corrupted_config_bak_increment(tmp_path):
    """Test that corrupted backups do not overwrite existing .bak files."""
    config_file = tmp_path / "config.json"

    # 1. Create an existing .bak file
    bak_file = tmp_path / "config.json.bak"
    bak_file.write_text("old backup content", encoding="utf-8")

    # 2. Write new corrupted config
    config_file.write_text("{broken 2", encoding="utf-8")

    cfg = Config(config_path=str(config_file))
    assert cfg.get("window_width") == 1024

    # 3. Old backup must remain intact
    assert bak_file.read_text(encoding="utf-8") == "old backup content"

    # 4. New backup should be at config.json.bak.1
    bak_file_1 = tmp_path / "config.json.bak.1"
    assert bak_file_1.exists()
    assert bak_file_1.read_text(encoding="utf-8") == "{broken 2"


def test_partial_config_merges_defaults(tmp_path):
    """Test partial config merges missing keys instead of clearing all."""
    config_file = tmp_path / "config.json"
    # User only saved sound_enabled and a customized window_width
    partial_data = {"sound_enabled": False, "window_width": 1280}
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(partial_data, f)

    cfg = Config(config_path=str(config_file))

    # Custom values should be preserved
    assert cfg.get("sound_enabled") is False
    assert cfg.get("window_width") == 1280

    # Missing keys should be merged from DEFAULT_CONFIG
    assert cfg.get("fullscreen") is False  # default
    assert cfg.get("window_height") == 768  # default
    assert cfg.get("show_tutorial") is True  # default


def test_invalid_config_type_fallback(tmp_path, capsys):
    """Test non-dict config triggers fallback and rebuilds."""
    config_file = tmp_path / "config.json"

    # Write a JSON list
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump([1, 2, 3], f)

    cfg = Config(config_path=str(config_file))
    assert cfg.get("window_width") == 1024

    # Rebuilt config file should be a valid dictionary
    with open(config_file, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert data["window_width"] == 1024

    # Backup should exist
    bak_file = tmp_path / "config.json.bak"
    assert bak_file.exists()
    with open(bak_file, encoding="utf-8") as f:
        bak_data = json.load(f)
    assert bak_data == [1, 2, 3]

    # Verify a warning was output to stderr
    captured = capsys.readouterr()
    assert "Config is not a dictionary" in captured.err


def test_config_default_has_language(tmp_path):
    """Verify that DEFAULT_CONFIG has language 'en' and missing config
    defaults to 'en'.
    """
    config_file = tmp_path / "config.json"
    cfg = Config(config_path=str(config_file))

    assert cfg.get_language() == "en"

    with open(config_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data["language"] == "en"


def test_config_partial_merge_restores_language(tmp_path):
    """Verify that loading a partial config without language merges it back to 'en'."""
    config_file = tmp_path / "config.json"
    # Save a config with only theme customized
    partial_data = {"theme": "dracula_purple"}
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(partial_data, f)

    cfg = Config(config_path=str(config_file))
    assert cfg.get("theme") == "dracula_purple"
    assert cfg.get_language() == "en"


def test_config_synchronizes_i18n_state(tmp_path):
    """Verify that loading a config with language 'zh-TW' syncs
    the i18n module state.
    """
    config_file = tmp_path / "config.json"
    data = {"language": "zh-TW"}
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    from src.pushbox.utils import i18n

    # Set active language to English first
    i18n.set_language("en")
    assert i18n.get_language() == "en"

    cfg = Config(config_path=str(config_file))
    assert cfg.get_language() == "zh-TW"
    assert i18n.get_language() == "zh-TW"  # Synced successfully!


def test_config_unsupported_language_falls_back_safely(tmp_path):
    """Verify that a config with unsupported language (e.g. 'fr')
    normalizes/falls back to 'en'.
    """
    config_file = tmp_path / "config.json"
    data = {"language": "fr"}
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    from src.pushbox.utils import i18n

    # Set to Chinese first
    i18n.set_language("zh-TW")

    cfg = Config(config_path=str(config_file))
    # Loaded value should normalize to 'en'
    assert cfg.get_language() == "en"
    assert i18n.get_language() == "en"


def test_config_corrupted_json_recovery_defaults_language(tmp_path):
    """Verify corrupted json rebuilds and defaults language to 'en'."""
    config_file = tmp_path / "config.json"
    config_file.write_text("{corrupted json", encoding="utf-8")

    from src.pushbox.utils import i18n

    i18n.set_language("zh-TW")

    cfg = Config(config_path=str(config_file))
    assert cfg.get_language() == "en"
    assert i18n.get_language() == "en"
