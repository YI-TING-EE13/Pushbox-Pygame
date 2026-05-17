import os
import sys
import time

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level
from src.pushbox.utils.constants import CellType
from src.pushbox.utils.constants import GameState as GameStateEnum


def test_pause_toggle_during_playing():
    """Test that toggle_pause switches is_paused during PLAYING state."""
    controller = GameController()
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    assert controller.game_state.status == GameStateEnum.PLAYING
    assert not controller.is_paused

    # Toggle pause
    controller.toggle_pause()
    assert controller.is_paused

    # Toggle again (resume)
    controller.toggle_pause()
    assert not controller.is_paused


def test_pause_blocked_during_non_playing():
    """Test that toggle_pause does not enter pause in WON or GAME_OVER state."""
    controller = GameController()
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Test WON state blocking pause
    controller.game_state.status = GameStateEnum.WON
    controller.toggle_pause()
    assert not controller.is_paused

    # Test GAME_OVER state blocking pause
    controller.game_state.status = GameStateEnum.GAME_OVER
    controller.toggle_pause()
    assert not controller.is_paused


def test_pause_blocks_movement_and_resume_restores_it():
    """Test that movement input is ignored during pause and restored after resume."""
    controller = GameController()
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Move normally
    controller._on_move((0, 1))
    assert controller.game_state.level.get_cell(1, 2) == CellType.PLAYER
    assert controller.game_state.move_count == 1

    # Pause and try to move
    controller.toggle_pause()
    controller._on_move((0, 1))
    # Player position should not change, and move count should not increase
    assert controller.game_state.level.get_cell(1, 2) == CellType.PLAYER
    assert controller.game_state.move_count == 1

    # Resume and try to move
    controller.toggle_pause()
    controller._on_move((0, 1))
    # Player position should change, and move count should increase
    assert controller.game_state.level.get_cell(1, 3) == CellType.PLAYER
    assert controller.game_state.move_count == 2


def test_pause_freezes_timer_and_offset_adjusts():
    """Test timer update suspension under pause and offset adjustment."""
    controller = GameController()
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Start and wait briefly
    time.sleep(0.05)
    controller.update()
    t1 = controller.game_state.elapsed_time
    assert t1 > 0

    # Pause and update
    controller.toggle_pause()
    time.sleep(0.05)
    controller.update()
    t2 = controller.game_state.elapsed_time
    # Time must not increment when paused
    assert t2 == t1

    # Resume and update
    controller.toggle_pause()
    time.sleep(0.05)
    controller.update()
    t3 = controller.game_state.elapsed_time
    # Time must resume incrementing
    assert t3 > t2
    # The elapsed time should not include the pause duration (less than total time)
    # Total physical time elapsed from start: > 0.15s,
    # but elapsed_time should be around 0.1s because we paused for 0.05s
    assert t3 < 0.13


def test_reset_exits_pause():
    """Test that resetting the level clears the pause state."""
    controller = GameController()
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    controller.toggle_pause()
    assert controller.is_paused

    controller._on_reset()
    assert not controller.is_paused
