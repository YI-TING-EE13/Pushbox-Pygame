import os
import sys

import pygame

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level
from src.pushbox.utils.constants import ControlScheme


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
