"""Tests for paths resolution, directory configuration, and environment isolation."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.models.level import LevelManager
from src.pushbox.models.save_manager import SaveManager
from src.pushbox.utils.config import Config
from src.pushbox.utils.paths import (
    ensure_runtime_dirs,
    get_app_base_path,
    get_app_data_path,
    get_bundle_root,
    get_project_root,
    get_resource_path,
    is_frozen,
)


def test_dev_mode_paths():
    """Verify paths resolution behavior in dev environment."""
    # 1. Dev mode flags
    assert is_frozen() is False

    # 2. project_root contains main.py
    project_root = get_project_root()
    assert project_root.exists()
    assert (project_root / "main.py").exists()

    # 3. bundle_root points to src/pushbox
    bundle_root = get_bundle_root()
    assert bundle_root.exists()
    assert (bundle_root / "assets/images/player.jpeg").exists()

    # 4. get_resource_path maps to get_bundle_root() / path
    res_path = get_resource_path("assets/images/player.jpeg")
    assert res_path.exists()
    assert res_path == bundle_root / "assets/images/player.jpeg"

    # 5. get_app_data_path in dev maps to project_root / path
    assert (
        get_app_data_path("data/config.json") == project_root / "data" / "config.json"
    )
    assert get_app_data_path("levels") == project_root / "levels"


def test_frozen_mode_paths_with_mocking(tmp_path, monkeypatch):
    """Verify path mapping in PyInstaller simulated environment."""
    mock_bundle_dir = tmp_path / "bundle"
    mock_bundle_dir.mkdir()
    mock_dist_dir = tmp_path / "dist"
    mock_dist_dir.mkdir()
    mock_exe = mock_dist_dir / "Pushbox.exe"

    # Mock sys attributes
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(mock_bundle_dir), raising=False)
    monkeypatch.setattr(sys, "executable", str(mock_exe), raising=False)

    # 1. Frozen environment properties
    assert is_frozen() is True
    assert get_bundle_root() == mock_bundle_dir
    assert get_app_base_path() == mock_dist_dir

    # 2. Resource paths point to _MEIPASS bundle
    res_path = get_resource_path("assets/images/player.jpeg")
    assert res_path == mock_bundle_dir / "assets/images/player.jpeg"

    # 3. App data paths point to executable directory (not _MEIPASS)
    config_path = get_app_data_path("data/config.json")
    levels_path = get_app_data_path("levels")

    assert config_path == mock_dist_dir / "data" / "config.json"
    assert levels_path == mock_dist_dir / "levels"

    # Ensure no bleeding of meipass into write directories
    assert str(mock_bundle_dir) not in str(config_path)
    assert str(mock_bundle_dir) not in str(levels_path)

    # 4. ensure_runtime_dirs creates appropriate folders in base write dir
    assert not (mock_dist_dir / "data").exists()
    assert not (mock_dist_dir / "levels").exists()

    ensure_runtime_dirs()

    assert (mock_dist_dir / "data").exists()
    assert (mock_dist_dir / "levels").exists()


def test_manual_path_injection_override(tmp_path):
    """Verify manual parameters override path helpers for isolation."""
    custom_config = tmp_path / "custom_config.json"
    custom_save = tmp_path / "custom_save_dir"
    custom_levels = tmp_path / "custom_levels_dir"

    # 1. Config override
    assert not custom_config.exists()
    cfg = Config(config_path=str(custom_config))
    assert cfg.config_path == custom_config
    assert custom_config.exists()

    # 2. SaveManager override
    assert not custom_save.exists()
    mgr = SaveManager(save_dir=str(custom_save))
    assert mgr.save_dir == custom_save
    assert custom_save.exists()
    # Perform a save to verify it writes to the custom directory
    mgr.update_level_progress("Level 1", moves=10, time_seconds=20.0, pushes=5)
    assert (custom_save / "progress.json").exists()

    # 3. LevelManager override
    assert not custom_levels.exists()
    lvl_mgr = LevelManager(levels_dir=str(custom_levels))
    assert lvl_mgr.levels_dir == custom_levels
    # Perform a custom level save to verify it writes to the custom directory
    from src.pushbox.models.level import Level

    custom_lvl = Level("Injected Level", [[1, 1, 1], [1, 4, 1], [1, 1, 1]])
    lvl_mgr.save_level(custom_lvl)
    assert custom_levels.exists()
    assert (custom_levels / "Injected_Level.json").exists()
