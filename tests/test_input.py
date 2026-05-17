import os
import sys

import pygame

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level
from src.pushbox.utils.constants import ControlScheme
from src.pushbox.utils.constants import GameState as GameStateEnum


def test_arrow_keys_movement_in_arrows_mode():
    """Test that arrow keys move the player when control scheme is ARROWS."""
    controller = GameController()
    controller.config.set_control_scheme(ControlScheme.ARROWS)

    grid = [[1, 1, 1, 1, 1], [1, 0, 4, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Position starts at (1, 2)
    assert controller.game_state.level.get_player_position() == (1, 2)

    # Simulate pressing K_RIGHT
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    handled = controller.handle_event(event)

    assert handled is True
    # Should have moved to (1, 3)
    assert controller.game_state.level.get_player_position() == (1, 3)
    assert controller.game_state.move_count == 1


def test_wasd_blocked_in_arrows_mode():
    """Test that WASD keys do NOT move the player when control scheme is ARROWS."""
    controller = GameController()
    controller.config.set_control_scheme(ControlScheme.ARROWS)

    grid = [[1, 1, 1, 1, 1], [1, 0, 4, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Simulate pressing K_d (WASD Right)
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
    handled = controller.handle_event(event)

    assert handled is False
    # Player position should still be (1, 2)
    assert controller.game_state.level.get_player_position() == (1, 2)
    assert controller.game_state.move_count == 0


def test_wasd_keys_movement_in_wasd_mode():
    """Test that WASD keys move the player when control scheme is WASD."""
    controller = GameController()
    controller.config.set_control_scheme(ControlScheme.WASD)

    grid = [[1, 1, 1, 1, 1], [1, 0, 4, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Simulate pressing K_d (WASD Right)
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
    handled = controller.handle_event(event)

    assert handled is True
    # Should have moved to (1, 3)
    assert controller.game_state.level.get_player_position() == (1, 3)
    assert controller.game_state.move_count == 1


def test_arrows_blocked_in_wasd_mode():
    """Test that arrow keys do NOT move the player when control scheme is WASD."""
    controller = GameController()
    controller.config.set_control_scheme(ControlScheme.WASD)

    grid = [[1, 1, 1, 1, 1], [1, 0, 4, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Simulate pressing K_RIGHT
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    handled = controller.handle_event(event)

    assert handled is False
    # Player position should still be (1, 2)
    assert controller.game_state.level.get_player_position() == (1, 2)
    assert controller.game_state.move_count == 0


def test_key_tap_twice_with_release_works():
    """Test that tapping a key twice with release works immediately."""
    controller = GameController()
    controller.config.set_control_scheme(ControlScheme.ARROWS)

    grid = [[1, 1, 1, 1, 1, 1], [1, 0, 4, 0, 0, 1], [1, 1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # First press
    event_down1 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    assert controller.handle_event(event_down1) is True
    assert controller.game_state.level.get_player_position() == (1, 3)

    # Release key
    event_up1 = pygame.event.Event(pygame.KEYUP, key=pygame.K_RIGHT)
    controller.handle_event(event_up1)

    # Second press immediately (within repeat delay)
    event_down2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    assert controller.handle_event(event_down2) is True
    # Should have moved to (1, 4)
    assert controller.game_state.level.get_player_position() == (1, 4)


def test_global_shortcuts_active_in_arrows_mode():
    """Test that global shortcuts are triggered in ARROWS mode."""
    controller = GameController()
    controller.config.set_control_scheme(ControlScheme.ARROWS)

    triggered_actions = []

    # Register test callbacks
    for action in ["undo", "redo", "reset", "pause", "help"]:
        controller.input_handler.register_callback(
            action, lambda a=action: triggered_actions.append(a)
        )

    # Trigger Z (undo)
    event_z = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
    assert controller.handle_event(event_z) is True
    assert "undo" in triggered_actions
    triggered_actions.clear()

    # Trigger Y (redo)
    event_y = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_y)
    assert controller.handle_event(event_y) is True
    assert "redo" in triggered_actions
    triggered_actions.clear()

    # Trigger R (redo)
    event_r = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
    assert controller.handle_event(event_r) is True
    assert "redo" in triggered_actions
    triggered_actions.clear()

    # Trigger F5 (reset)
    event_f5 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F5)
    assert controller.handle_event(event_f5) is True
    assert "reset" in triggered_actions
    triggered_actions.clear()

    # Trigger H (help)
    event_h = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h)
    assert controller.handle_event(event_h) is True
    assert "help" in triggered_actions
    triggered_actions.clear()

    # Trigger Esc (pause)
    event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    assert controller.handle_event(event_esc) is True
    assert "pause" in triggered_actions


def test_global_shortcuts_active_in_wasd_mode():
    """Test that global shortcuts are triggered in WASD mode."""
    controller = GameController()
    controller.config.set_control_scheme(ControlScheme.WASD)

    triggered_actions = []

    # Register test callbacks
    for action in ["undo", "redo", "reset", "pause", "help"]:
        controller.input_handler.register_callback(
            action, lambda a=action: triggered_actions.append(a)
        )

    # Trigger Z (undo)
    event_z = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z)
    assert controller.handle_event(event_z) is True
    assert "undo" in triggered_actions
    triggered_actions.clear()

    # Trigger Y (redo)
    event_y = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_y)
    assert controller.handle_event(event_y) is True
    assert "redo" in triggered_actions
    triggered_actions.clear()

    # Trigger R (redo)
    event_r = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
    assert controller.handle_event(event_r) is True
    assert "redo" in triggered_actions
    triggered_actions.clear()

    # Trigger F5 (reset)
    event_f5 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F5)
    assert controller.handle_event(event_f5) is True
    assert "reset" in triggered_actions
    triggered_actions.clear()

    # Trigger H (help)
    event_h = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h)
    assert controller.handle_event(event_h) is True
    assert "help" in triggered_actions
    triggered_actions.clear()

    # Trigger Esc (pause)
    event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    assert controller.handle_event(event_esc) is True
    assert "pause" in triggered_actions


def test_reset_behavior_and_input_cleanup():
    """Test that reset returns status to PLAYING, sets is_paused to False,

    clears input state, and allows movement again.
    """
    controller = GameController()
    controller.config.set_control_scheme(ControlScheme.ARROWS)

    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Pause the game and add some key repeat state
    controller.is_paused = True
    controller.input_handler._last_key_time[pygame.K_RIGHT] = pygame.time.get_ticks()
    controller.input_handler._key_states[pygame.K_RIGHT] = True

    # Check state before reset
    assert controller.is_paused is True
    assert len(controller.input_handler._last_key_time) > 0

    # Call _on_reset
    controller._on_reset()

    # Verify state after reset
    assert controller.is_paused is False
    assert controller.game_state.status == GameStateEnum.PLAYING
    assert len(controller.input_handler._last_key_time) == 0
    assert len(controller.input_handler._key_states) == 0

    # Verify movement is immediately allowed
    event_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    assert controller.handle_event(event_right) is True
    assert controller.game_state.level.get_player_position() == (1, 2)


def test_reset_callbacks_consistency():
    """Verify that keyboard action 'reset' and direct reset call trigger

    the same underlying _on_reset logic.
    """
    controller = GameController()
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Make a move
    controller._on_move((0, 1))
    assert controller.game_state.move_count == 1

    # Trigger keyboard reset action
    event_f5 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F5)
    controller.handle_event(event_f5)
    assert controller.game_state.move_count == 0

    # Make another move
    controller._on_move((0, 1))
    assert controller.game_state.move_count == 1

    # Trigger button callback directly (as the UI reset button does)
    controller._on_reset()
    assert controller.game_state.move_count == 0
