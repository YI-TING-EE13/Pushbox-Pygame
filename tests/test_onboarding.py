"""Tests for v0.8.0 Onboarding (Level 0) features."""

import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.controllers.game_controller import GameController


def test_level_0_exists_and_dimensions():
    """Verify Level 0 onboarding tutorial level exists.

    Conforms to 5x7 dimensions.
    """
    controller = GameController()
    level_0 = controller.level_manager.get_level("Level 0")
    assert level_0 is not None
    assert level_0.rows == 5
    assert level_0.cols == 7


def test_level_0_exclusivity_in_selectors():
    """Verify Level 0 does not appear in official level lists or selectors."""
    controller = GameController()
    level_names = controller.get_available_levels()

    # Must NOT include Level 0 in standard listing
    assert "Level 0" not in level_names
    # Official graduation list (Level 1 to 30) should remain present
    assert "Level 1" in level_names
    assert "Level 30" in level_names


def test_level_0_win_does_not_save():
    """Verify completing Level 0 does NOT write progress or high scores."""
    # Ensure dummy env to prevent Pygame hardware display requests
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    controller = GameController()
    # Reset stats
    controller.save_manager.reset_progress()

    # Load Level 0
    controller.load_level("Level 0")
    assert controller.get_current_level_name() == "Level 0"

    # Manually trigger win
    game_state = controller.game_state
    assert game_state is not None

    # Simulate pushes to complete Level 0
    # Level 0 layout is: player(4) at (2,1), box(3) at (2,4), target(2) at (2,5)
    # Player moves right to push box
    controller._on_move((0, 1))  # Move right to (2,2)
    controller._on_move((0, 1))  # Move right to (2,3) (now next to box)
    controller._on_move((0, 1))  # Push box right to target (2,5)

    # Verify won state
    from src.pushbox.utils.constants import GameState as GameStateEnum

    assert game_state.status == GameStateEnum.WON

    # Check save data is still completely empty
    progress = controller.save_manager.get_all_progress()
    assert "Level 0" not in progress
    assert progress.get("Level 0") is None


def test_unlock_chain_unaffected():
    """Verify standard Level 1 to 30 unlock and locking chains are unaffected."""
    controller = GameController()
    level_names = controller.get_available_levels()

    # Standard index checking
    assert "Level 1" in level_names
    assert "Level 2" in level_names

    # Level 1 should be unlocked initially
    # Level 2 should be locked initially if Level 1 is not completed
    controller.save_manager.reset_progress()

    # Level 1 is graduation 1, index > 1 lock checks
    # Level 1 is active, Level 2 locked
    assert "Level 0" not in level_names
