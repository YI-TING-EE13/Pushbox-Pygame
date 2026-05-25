import os
import sys

import pygame
import pytest

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.models.level import LevelManager
from src.pushbox.views.ui_components import LevelSelector


@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup headless pygame environment for testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


def test_level_selector_level_manager_shared():
    """Test that LevelSelector correctly shares or creates its own LevelManager."""
    screen = pygame.Surface((800, 720))

    # 1. Fallback creation when level_manager=None
    selector_default = LevelSelector(screen)
    assert selector_default.level_manager is not None
    assert isinstance(selector_default.level_manager, LevelManager)

    # 2. Shared creation when passing level_manager instance
    shared_lm = LevelManager()
    selector_shared = LevelSelector(screen, level_manager=shared_lm)
    assert selector_shared.level_manager is shared_lm


def test_minimap_rendering_unlocked():
    """Test drawing unlocked level details and minimap without crash."""
    screen = pygame.Surface((800, 720))
    shared_lm = LevelManager()
    selector = LevelSelector(screen, level_manager=shared_lm)

    levels = ["Level 1", "Level 2"]
    # Level 1 is unlocked. Setup selector.
    selector.setup(
        level_names=levels,
        progress={},
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    # Selected index is 0 (Level 1, unlocked)
    selector.selected_index = 0

    # Run rendering - should not crash
    selector._draw_selected_level_details(screen, {})


def test_minimap_rendering_locked():
    """Test drawing locked level details and lock icon without crash."""
    screen = pygame.Surface((800, 720))
    shared_lm = LevelManager()
    selector = LevelSelector(screen, level_manager=shared_lm)
    selector.developer_mode = False

    levels = ["Level 1", "Level 2"]
    # Level 2 is locked since progress is empty
    selector.setup(
        level_names=levels,
        progress={},
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    # Selected index is 1 (Level 2, locked)
    selector.selected_index = 1

    # Run rendering - should not crash
    selector._draw_selected_level_details(screen, {})


def test_minimap_rendering_missing_level():
    """Test details rendering fallback to 'No Map' if level is missing."""
    screen = pygame.Surface((800, 720))
    shared_lm = LevelManager()
    selector = LevelSelector(screen, level_manager=shared_lm)

    levels = ["NonExistentLevel"]
    selector.setup(
        level_names=levels,
        progress={},
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    selector.selected_index = 0
    # Run rendering - should not crash
    selector._draw_selected_level_details(screen, {})
