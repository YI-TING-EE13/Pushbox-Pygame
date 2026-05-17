import os
import sys

import pygame

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level
from src.pushbox.utils.constants import CellType
from src.pushbox.utils.constants import GameState as GameStateEnum


def test_level_creation():
    """Test creating a level."""
    grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
    level = Level("Test Level", grid)
    assert level.name == "Test Level"
    assert level.rows == 3
    assert level.cols == 3
    assert level.get_cell(1, 1) == CellType.PLAYER


def test_game_state_initialization():
    """Test initializing game state."""
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 3, 1], [1, 0, 0, 2, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    game = GameState(level)

    assert game.status == GameStateEnum.PLAYING
    assert game.move_count == 0
    assert game.push_count == 0


def test_player_movement():
    """Test player movement."""
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    game = GameState(level)

    # Move Right (0, 1)
    success = game.move((0, 1))
    assert success is True
    assert game.level.get_cell(1, 2) == CellType.PLAYER
    assert game.level.get_cell(1, 1) == CellType.EMPTY
    assert game.move_count == 1


def test_wall_collision():
    """Test player hitting a wall."""
    grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
    level = Level("Test Level", grid)
    game = GameState(level)

    # Try to move Right into a wall
    success = game.move((0, 1))
    assert success is False
    assert game.level.get_cell(1, 1) == CellType.PLAYER
    assert game.move_count == 0


def test_box_push():
    """Test pushing a box."""
    grid = [[1, 1, 1, 1, 1], [1, 4, 3, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    game = GameState(level)

    # Push Box Right
    success = game.move((0, 1))
    assert success is True
    assert game.level.get_cell(1, 1) == CellType.EMPTY
    assert game.level.get_cell(1, 2) == CellType.PLAYER
    assert game.level.get_cell(1, 3) == CellType.BOX
    assert game.push_count == 1


def test_renderer_hud_no_crash():
    """Test that the gameplay HUD handles level names without crashing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.font.init()

    from src.pushbox.views.renderer import Renderer

    # Create dummy surface
    screen = pygame.Surface((800, 720))
    renderer = Renderer(screen)

    # 1. Test with default level (Level 23)
    grid_default = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
    level_default = Level("Level 23", grid_default)
    state_default = GameState(level_default)
    renderer.render_ui(state_default)

    # 2. Test with normal custom level
    level_custom_short = Level("對稱自訂圖", grid_default)
    state_custom_short = GameState(level_custom_short)
    renderer.render_ui(state_custom_short)

    # 3. Test with very long custom level (truncation path)
    level_custom_long = Level(
        "ThisIsAVeryLongCustomLevelNameThatExceedsTwentyCharacters", grid_default
    )
    state_custom_long = GameState(level_custom_long)
    renderer.render_ui(state_custom_long)

    # Clean up
    pygame.quit()
