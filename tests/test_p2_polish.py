import os
import sys

import pygame
import pytest

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.level import Level
from src.pushbox.utils.constants import CellType
from src.pushbox.views.level_editor import LevelEditor
from src.pushbox.views.renderer import Renderer


@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup headless pygame environment for testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


def test_game_controller_load_level_instance():
    """Test load_level_instance and is_playtest behavior in GameController."""
    controller = GameController()
    grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
    level = Level("Test Playtest Level", grid)

    # 1. Load instance without playtest
    controller.load_level_instance(level, is_playtest=False)
    assert controller.current_level == level
    assert controller.is_playtest is False
    assert controller.is_paused is False

    # 2. Load instance with playtest
    controller.load_level_instance(level, is_playtest=True)
    assert controller.current_level == level
    assert controller.is_playtest is True


def test_playtest_does_not_save_progress():
    """Test that playtest sessions do not save progress on win."""
    controller = GameController()

    # Setup callbacks
    win_called = False

    def on_win(stats, is_record):
        nonlocal win_called
        win_called = True
        # Since it is a playtest, is_record must be False
        assert is_record is False

    controller.register_callback("win", on_win)

    # A simple single-push win level
    grid = [[1, 1, 1, 1], [1, 4, 3, 2], [1, 1, 1, 1]]
    level = Level("Win Test", grid)
    controller.load_level_instance(level, is_playtest=True)

    # Move right to push box to target and win
    controller._on_move((0, 1))

    assert win_called is True


def test_invalid_move_event_trigger():
    """Test invalid_move event is triggered on invalid moves."""
    controller = GameController()

    invalid_move_triggered = False

    def on_invalid_move():
        nonlocal invalid_move_triggered
        invalid_move_triggered = True

    controller.register_callback("invalid_move", on_invalid_move)

    grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
    level = Level("Invalid Test", grid)
    controller.load_level_instance(level, is_playtest=False)

    # Move into wall (invalid)
    controller._on_move((0, 1))

    assert invalid_move_triggered is True


def test_level_editor_is_dirty():
    """Test LevelEditor dirty state detection."""
    screen = pygame.Surface((800, 720))
    editor = LevelEditor(screen)

    # 1. Clean initially
    assert editor.is_dirty() is False

    # 2. Modify grid -> should be dirty
    editor.grid[1][1] = CellType.WALL
    editor._save_state()
    assert editor.is_dirty() is True

    # 3. Undo -> back to clean
    editor._undo()
    assert editor.is_dirty() is False

    # 4. Modify name -> should be dirty
    editor.name_input.text = "New Name"
    assert editor.is_dirty() is True

    # 5. Clear name back -> clean
    editor.name_input.text = "Custom Level"
    assert editor.is_dirty() is False


def test_renderer_screen_shake():
    """Test Renderer screen shake triggers and updates."""
    screen = pygame.Surface((800, 720))
    renderer = Renderer(screen)

    # 1. Initially no shake
    assert renderer.shake_duration == 0.0
    assert renderer.shake_offset_x == 0
    assert renderer.shake_offset_y == 0

    # 2. Trigger shake
    renderer.trigger_screen_shake(duration=0.2, intensity=5)
    assert renderer.shake_duration == 0.2
    assert renderer.shake_intensity == 5

    # 3. Update animations to process shake
    # Simulate first update to set last_update_time
    renderer.update_animations()

    # Simulate delta time step by setting last update time back in time
    renderer._last_update_time = pygame.time.get_ticks() / 1000.0 - 0.1
    renderer.update_animations()

    # Duration should decrease
    assert renderer.shake_duration < 0.2
    assert renderer.shake_duration > 0

    # Offset should be generated randomly within [-5, 5]
    assert -5 <= renderer.shake_offset_x <= 5
    assert -5 <= renderer.shake_offset_y <= 5

    # 4. Finish shake
    renderer._last_update_time = pygame.time.get_ticks() / 1000.0 - 0.2
    renderer.update_animations()
    assert renderer.shake_duration == 0.0
    assert renderer.shake_offset_x == 0
    assert renderer.shake_offset_y == 0
