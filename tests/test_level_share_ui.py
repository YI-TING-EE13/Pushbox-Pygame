"""Integration and UI tests for level exporting and importing interfaces."""

import os

import pytest

# Ensure dummy video driver is loaded for headless Pygame initialization
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

from src.pushbox.models.level import LevelManager
from src.pushbox.utils.constants import CellType
from src.pushbox.utils.level_share import export_level_to_code
from src.pushbox.views.level_editor import LevelEditor
from src.pushbox.views.ui_components import InputBox, LevelSelector


@pytest.fixture(autouse=True)
def init_pygame() -> None:
    """Headless Pygame initialization fixture."""
    from src.pushbox.utils import i18n

    i18n.set_language("zh-TW")
    pygame.init()
    pygame.display.set_mode((800, 720))
    yield
    i18n.set_language("en")


def test_level_editor_export_valid() -> None:
    """Test that a valid editor layout exports successfully and triggers the dialog."""
    editor = LevelEditor(pygame.display.get_surface())
    # Fill perimeter with walls
    for c in range(10):
        editor.grid[0][c] = CellType.WALL
        editor.grid[9][c] = CellType.WALL
    for r in range(10):
        editor.grid[r][0] = CellType.WALL
        editor.grid[r][9] = CellType.WALL

    # Place player and box/target inside
    editor.grid[2][2] = CellType.PLAYER
    editor.grid[3][3] = CellType.BOX
    editor.grid[4][4] = CellType.TARGET

    editor._export_level()

    assert editor.show_export_dialog is True
    assert editor.export_code.startswith("PBX_")
    assert isinstance(editor.export_input, InputBox)
    assert editor.export_input.text == editor.export_code
    assert editor.export_input.max_length == 2000


def test_level_editor_export_invalid_perimeter() -> None:
    """Test that an open boundary layout fails validation and displays error."""
    editor = LevelEditor(pygame.display.get_surface())
    editor.grid[2][2] = CellType.PLAYER
    editor.grid[3][3] = CellType.BOX
    editor.grid[3][4] = CellType.TARGET
    # Boundary is completely empty (0), so perimeter check fails

    editor._export_level()

    assert editor.show_export_dialog is False
    assert "外圍邊界必須完全封閉為牆壁" in editor.status_message


def test_level_editor_export_invalid_player() -> None:
    """Test that layout without player fails validation and displays error."""
    editor = LevelEditor(pygame.display.get_surface())
    for c in range(10):
        editor.grid[0][c] = CellType.WALL
        editor.grid[9][c] = CellType.WALL
    editor.grid[3][3] = CellType.BOX
    editor.grid[3][4] = CellType.TARGET
    # No player

    editor._export_level()

    assert editor.show_export_dialog is False
    assert "必須放置玩家" in editor.status_message


def test_level_selector_import_flow() -> None:
    """Test that level selector import flow saves custom level and refreshes UI."""
    manager = LevelManager()
    # Ensure a fresh slate in manager by backing up and restoring custom levels
    # But manager uses isolated memory dict or disk folder during headless runs
    selector = LevelSelector(pygame.display.get_surface(), level_manager=manager)

    # Initialize selector setup
    selector.setup(
        manager.get_level_names(),
        {},
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    # Click Import Level button
    selector._on_import_button_click()

    assert selector.show_import_dialog is True
    assert isinstance(selector.import_input, InputBox)
    assert selector.import_input.text == ""
    assert selector.import_input.max_length == 2000
    assert selector.import_error_message is None

    # Generate valid share code
    name = "ImportedSokoban"
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 0, 2, 1],
        [1, 0, 3, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    valid_code = export_level_to_code(name, grid)

    # Submit valid import
    selector._import_level(valid_code)

    assert selector.show_import_dialog is False
    assert selector.import_error_message is None
    assert name in selector.level_names_all
    assert manager.get_level(name) is not None


def test_level_selector_import_invalid() -> None:
    """Test that level selector import shows error message for malformed share codes."""
    manager = LevelManager()
    selector = LevelSelector(pygame.display.get_surface(), level_manager=manager)
    selector.setup(
        manager.get_level_names(),
        {},
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    selector._on_import_button_click()

    # Submit bad prefix code
    selector._import_level("PBX_!!!badbase64!!!")

    assert selector.show_import_dialog is True  # Stays open
    assert "無法進行 Base64 解碼" in selector.import_error_message
