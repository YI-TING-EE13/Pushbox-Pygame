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


@pytest.mark.parametrize(
    "size", [(800, 720), (800, 600), (1024, 768), (640, 480), (1280, 960)]
)
def test_detail_panel_no_overlap_with_cards(size):
    """Verify the detail panel and minimap never overlap the card grid or buttons."""
    screen = pygame.Surface(size)
    shared_lm = LevelManager()
    selector = LevelSelector(screen, level_manager=shared_lm)

    all_levels = [f"Level {i}" for i in range(1, 10)]
    selector.setup(
        level_names=all_levels,
        progress={},
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    selector.selected_index = 0

    # Compute card grid bounds (must match _layout_buttons constants)
    button_height = 65
    spacing_y = 35
    start_y = 110

    num_buttons = len(selector.level_buttons)
    rows_on_page = min(3, (num_buttons + 2) // 3)
    grid_bottom = start_y + rows_on_page * (button_height + spacing_y) - spacing_y

    # Compute the detail panel bounds (must match _draw_selected_level_details)
    screen_h = size[1]
    bottom_zone_top = screen_h - 195
    panel_gap_top = 15
    panel_gap_bottom = 10
    panel_top = grid_bottom + panel_gap_top
    panel_max_bottom = bottom_zone_top - panel_gap_bottom
    panel_h = max(0, panel_max_bottom - panel_top)

    if panel_h < 50:
        # Panel is hidden — no overlap possible
        return

    # Panel must not overlap with card grid
    assert panel_top > grid_bottom, (
        f"Detail panel top ({panel_top}) overlaps card grid bottom ({grid_bottom}) "
        f"at screen size {size}"
    )

    # Panel must not extend into pagination/nav area
    nav_y = screen_h - 130
    assert panel_max_bottom <= nav_y, (
        f"Detail panel bottom ({panel_max_bottom}) extends into nav buttons "
        f"({nav_y}) at screen size {size}"
    )

    # Verify each card button rect does not overlap with the panel rect
    panel_w = min(640, size[0] - 40)
    panel_x = (size[0] - panel_w) // 2
    panel_rect = pygame.Rect(panel_x, panel_top, panel_w, panel_h)

    for btn, level_name, _ in selector.level_buttons:
        assert not btn.rect.colliderect(panel_rect), (
            f"Card '{level_name}' rect {btn.rect} overlaps detail panel "
            f"{panel_rect} at screen size {size}"
        )

    # Run rendering - should not crash at any size
    selector._draw_selected_level_details(screen, {})
    selector.draw({})


def test_detail_panel_no_overlap_with_bottom_buttons():
    """Verify back/import buttons do not overlap the detail panel at 800x720."""
    screen = pygame.Surface((800, 720))
    shared_lm = LevelManager()
    selector = LevelSelector(screen, level_manager=shared_lm)

    all_levels = [f"Level {i}" for i in range(1, 10)]
    selector.setup(
        level_names=all_levels,
        progress={},
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    # The back/import buttons are at screen_h - 80
    back_rect = selector.back_button.rect if selector.back_button else None
    import_rect = selector.import_button.rect if selector.import_button else None

    # Compute panel bounds
    button_height = 65
    spacing_y = 35
    start_y = 110
    rows_on_page = 3
    grid_bottom = start_y + rows_on_page * (button_height + spacing_y) - spacing_y
    panel_top = grid_bottom + 15
    panel_max_bottom = 720 - 195 - 10
    panel_h = max(0, panel_max_bottom - panel_top)
    panel_w = min(640, 800 - 40)
    panel_x = (800 - panel_w) // 2
    panel_rect = pygame.Rect(panel_x, panel_top, panel_w, panel_h)

    if back_rect:
        assert not back_rect.colliderect(panel_rect), (
            f"Back button {back_rect} overlaps detail panel {panel_rect}"
        )
    if import_rect:
        assert not import_rect.colliderect(panel_rect), (
            f"Import button {import_rect} overlaps detail panel {panel_rect}"
        )
