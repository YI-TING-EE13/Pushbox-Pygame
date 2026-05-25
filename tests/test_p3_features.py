import os
import sys

import pygame
import pytest

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.level import Level
from src.pushbox.utils.constants import COLORS, THEMES, set_theme


@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup headless pygame environment for testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()


def test_theme_switching_logic():
    """Test that dynamic theme switching correctly updates the COLORS dictionary."""
    # 1. Test setting nord_blue
    set_theme("nord_blue")
    assert COLORS["background"] == THEMES["nord_blue"]["background"]
    assert COLORS["wall"] == THEMES["nord_blue"]["wall"]
    assert COLORS["player"] == THEMES["nord_blue"]["player"]

    # 2. Test setting classic_green
    set_theme("classic_green")
    assert COLORS["background"] == THEMES["classic_green"]["background"]
    assert COLORS["wall"] == THEMES["classic_green"]["wall"]
    assert COLORS["player"] == THEMES["classic_green"]["player"]

    # 3. Test setting dracula_purple
    set_theme("dracula_purple")
    assert COLORS["background"] == THEMES["dracula_purple"]["background"]
    assert COLORS["wall"] == THEMES["dracula_purple"]["wall"]
    assert COLORS["player"] == THEMES["dracula_purple"]["player"]

    # 4. Test fallback to default
    set_theme("default")
    assert COLORS["background"] == THEMES["nord_blue"]["background"]


def test_undo_redo_events_with_command_context():
    """Test that undo and redo events are triggered with the correct command details."""
    controller = GameController()

    # Simple single-push level with an extra box that is not deadlocked
    grid = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 4, 3, 2, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 3, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    level = Level("Test Level", grid)
    controller.load_level_instance(level, is_playtest=False)

    # 1. Execute a move (push right)
    controller._on_move((0, 1))
    assert controller.game_state.move_count == 1
    assert len(controller.game_state.move_history) == 1

    # 2. Track undo callback
    undo_called = False
    undo_cmd = None

    def on_undo(cmd):
        nonlocal undo_called, undo_cmd
        undo_called = True
        undo_cmd = cmd

    controller.register_callback("undo", on_undo)

    # Trigger undo
    controller._on_undo()
    assert undo_called is True
    assert undo_cmd is not None
    assert undo_cmd.player_from == (1, 1)
    assert undo_cmd.player_to == (1, 2)
    assert undo_cmd.box_from == (1, 2)
    assert undo_cmd.box_to == (1, 3)

    # 3. Track redo callback
    redo_called = False
    redo_cmd = None

    def on_redo(cmd):
        nonlocal redo_called, redo_cmd
        redo_called = True
        redo_cmd = cmd

    controller.register_callback("redo", on_redo)

    # Trigger redo
    controller._on_redo()
    assert redo_called is True
    assert redo_cmd is not None
    assert redo_cmd.player_from == (1, 1)
    assert redo_cmd.player_to == (1, 2)
    assert redo_cmd.box_from == (1, 2)
    assert redo_cmd.box_to == (1, 3)
