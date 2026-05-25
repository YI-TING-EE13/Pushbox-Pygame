import os
import sys

import pygame
import pytest

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.views.ui_components import LevelSelector, ModernButton


@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup headless pygame environment for testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


def test_modern_button_locked_behavior():
    """Test locked ModernButton click suppression and offsets."""
    screen = pygame.Surface((800, 720))

    clicked = False

    def on_click():
        nonlocal clicked
        clicked = True

    # 1. Create a locked button
    btn = ModernButton(
        x=50,
        y=50,
        width=100,
        height=40,
        text="Locked Level",
        callback=on_click,
        is_locked=True,
    )

    assert btn.is_locked is True

    # 2. Try drawing (offsets must be 0)
    btn.selected = True
    btn.hovered = True
    btn.draw(screen)
    assert btn.hover_anim == 0.0

    # 3. Simulate mouse click (callback must NOT be called)
    event_down = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"pos": (70, 70), "button": 1}
    )
    event_up = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": (70, 70), "button": 1})

    # Should ignore click
    assert btn.handle_event(event_down) is False
    assert btn.handle_event(event_up) is False
    assert clicked is False


def test_level_selector_lock_chain_logic():
    """Test LevelSelector sequential locking rules and Developer Mode override."""
    screen = pygame.Surface((800, 720))
    selector = LevelSelector(screen)
    selector.developer_mode = False

    levels = ["Level 1", "Level 2", "Level 3"]

    # 1. No levels completed (Level 1 should be unlocked, Level 2 & 3 locked)
    progress_none = {}
    selector.setup(
        level_names=levels,
        progress=progress_none,
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    btn1, name1, is_cust1 = selector.level_buttons[0]
    btn2, name2, is_cust2 = selector.level_buttons[1]
    btn3, name3, is_cust3 = selector.level_buttons[2]

    assert name1 == "Level 1"
    assert btn1.is_locked is False

    assert name2 == "Level 2"
    assert btn2.is_locked is True

    assert name3 == "Level 3"
    assert btn3.is_locked is True

    # 2. Level 1 completed (Level 1 & 2 should be unlocked, Level 3 locked)
    progress_one = {"Level 1": {"completed": True}}
    selector.setup(
        level_names=levels,
        progress=progress_one,
        on_select=lambda name: None,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    btn1, _, _ = selector.level_buttons[0]
    btn2, _, _ = selector.level_buttons[1]
    btn3, _, _ = selector.level_buttons[2]

    assert btn1.is_locked is False
    assert btn2.is_locked is False
    assert btn3.is_locked is True

    # 3. Test Developer Mode Override
    # Toggle dev mode
    selector.developer_mode = True
    # Re-layout
    selector._layout_buttons(levels, progress_one)

    btn1, _, _ = selector.level_buttons[0]
    btn2, _, _ = selector.level_buttons[1]
    btn3, _, _ = selector.level_buttons[2]

    # All levels should be unlocked under dev mode!
    assert btn1.is_locked is False
    assert btn2.is_locked is False
    assert btn3.is_locked is False


def test_level_selector_keyboard_navigation_protection():
    """Test that locked level cards cannot be entered via keyboard shortcuts."""
    screen = pygame.Surface((800, 720))
    selector = LevelSelector(screen)
    selector.developer_mode = False

    levels = ["Level 1", "Level 2"]
    progress = {}

    selected_name = None

    def on_select(name):
        nonlocal selected_name
        selected_name = name

    selector.setup(
        level_names=levels,
        progress=progress,
        on_select=on_select,
        on_back=lambda: None,
        on_edit=lambda name: None,
        on_delete=lambda name: None,
    )

    # Selected index is 0 initially (Level 1, unlocked)
    selector.selected_index = 0
    event_enter = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN, "mod": 0})

    # Enter on Level 1 -> should succeed
    assert selector.handle_event(event_enter) is True
    assert selected_name == "Level 1"

    # Reset selected
    selected_name = None

    # Move selection to Index 1 (Level 2, locked)
    selector.selected_index = 1
    # Enter on Level 2 -> should be blocked by protection
    assert selector.handle_event(event_enter) is False
    assert selected_name is None
