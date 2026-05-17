import os
import sys
from unittest.mock import MagicMock, patch

import pygame

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import GameApp
from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level
from src.pushbox.utils.constants import ControlScheme
from src.pushbox.utils.constants import GameState as GameStateEnum
from src.pushbox.views.ui_components import LevelSelector


def test_arrow_keys_movement():
    """Test that arrow keys move the player."""
    controller = GameController()

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


def test_wasd_keys_movement():
    """Test that WASD keys move the player."""
    controller = GameController()

    grid = [[1, 1, 1, 1, 1], [1, 0, 4, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Position starts at (1, 2)
    assert controller.game_state.level.get_player_position() == (1, 2)

    # Simulate pressing K_d (WASD Right)
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
    handled = controller.handle_event(event)

    assert handled is True
    # Should have moved to (1, 3)
    assert controller.game_state.level.get_player_position() == (1, 3)
    assert controller.game_state.move_count == 1


def test_movement_unaffected_by_legacy_control_scheme():
    """Test both arrows and WASD are active, ignoring legacy config values."""
    controller = GameController()

    grid = [[1, 1, 1, 1, 1, 1, 1], [1, 0, 4, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    controller.current_level = level
    controller.game_state = GameState(level)

    # Check arrow key movement works
    event_arrow = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    assert controller.handle_event(event_arrow) is True
    assert controller.game_state.level.get_player_position() == (1, 3)

    # Check WASD key movement works
    event_wasd = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
    assert controller.handle_event(event_wasd) is True
    assert controller.game_state.level.get_player_position() == (1, 4)


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


def test_menu_navigation():
    """Verify menu keyboard navigation (W/S, arrows, Enter/Space, wrap-around)."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    app = GameApp()
    app.current_screen = "menu"
    app.menu_selected_index = 0
    btn_count = len(app.menu.buttons)
    assert btn_count > 0

    # Down arrow
    evt_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    with patch("pygame.event.get", return_value=[evt_down]):
        app.handle_events()
    assert app.menu_selected_index == 1

    # S key
    evt_s = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)
    with patch("pygame.event.get", return_value=[evt_s]):
        app.handle_events()
    assert app.menu_selected_index == 2

    # Up arrow
    evt_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    with patch("pygame.event.get", return_value=[evt_up]):
        app.handle_events()
    assert app.menu_selected_index == 1

    # W key
    evt_w = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
    with patch("pygame.event.get", return_value=[evt_w]):
        app.handle_events()
    assert app.menu_selected_index == 0

    # Wrap around UP (0 - 1 = btn_count - 1)
    with patch("pygame.event.get", return_value=[evt_up]):
        app.handle_events()
    assert app.menu_selected_index == btn_count - 1

    # Wrap around DOWN (back to 0)
    with patch("pygame.event.get", return_value=[evt_down]):
        app.handle_events()
    assert app.menu_selected_index == 0

    # Enter callback trigger
    app.menu_selected_index = 0
    mock_callback = MagicMock()
    app.menu.buttons[0].callback = mock_callback
    evt_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    with patch("pygame.event.get", return_value=[evt_enter]):
        app.handle_events()
    mock_callback.assert_called_once()

    # Space callback trigger
    mock_callback_space = MagicMock()
    app.menu.buttons[1].callback = mock_callback_space
    app.menu_selected_index = 1
    evt_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    with patch("pygame.event.get", return_value=[evt_space]):
        app.handle_events()
    mock_callback_space.assert_called_once()


def test_help_overlay_dismissal():
    """Verify help overlay closes on any key without triggering other actions."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    app = GameApp()
    app.current_screen = "game"

    app.controller = GameController()
    grid = [[1, 1, 1, 1, 1], [1, 4, 0, 0, 1], [1, 1, 1, 1, 1]]
    level = Level("Test Level", grid)
    app.controller.current_level = level
    app.controller.game_state = GameState(level)

    # 1. Open help overlay
    app.show_help = True
    assert app.show_help is True

    # 2. Press Right arrow. Help should close, but player should NOT move.
    assert app.controller.game_state.level.get_player_position() == (1, 1)
    evt_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    with patch("pygame.event.get", return_value=[evt_right]):
        app.handle_events()
    assert app.show_help is False
    assert app.controller.game_state.level.get_player_position() == (1, 1)

    # 3. Next keypress should move the player normally
    with patch("pygame.event.get", return_value=[evt_right]):
        app.handle_events()
    assert app.controller.game_state.level.get_player_position() == (1, 2)

    # 4. Open help overlay again and test Reset key (R). Should close help, not reset.
    app.show_help = True
    evt_r = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
    with patch("pygame.event.get", return_value=[evt_r]):
        app.handle_events()
    assert app.show_help is False
    assert app.controller.game_state.move_count == 1

    # 5. Open help overlay again and test Pause key (P). Should close help, not pause.
    app.show_help = True
    assert not app.controller.is_paused
    evt_p = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)
    with patch("pygame.event.get", return_value=[evt_p]):
        app.handle_events()
    assert app.show_help is False
    assert not app.controller.is_paused


def test_quit_shortcut():
    """Verify Ctrl+Q exits the game while Q alone does not, works everywhere."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    app = GameApp()
    assert app.running is True

    # 1. Single Q key should NOT quit
    evt_q = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q)
    with patch("pygame.event.get", return_value=[evt_q]):
        app.handle_events()
    assert app.running is True

    # 2. Ctrl+Q should quit on Main Menu
    app.current_screen = "menu"
    evt_ctrl_q = pygame.event.Event(
        pygame.KEYDOWN, key=pygame.K_q, mod=pygame.KMOD_CTRL
    )
    with patch("pygame.event.get", return_value=[evt_ctrl_q]):
        app.handle_events()
    assert app.running is False

    # 3. Ctrl+Q should quit during Pause or Help
    app2 = GameApp()
    app2.current_screen = "game"
    app2.show_help = True
    assert app2.running is True
    with patch("pygame.event.get", return_value=[evt_ctrl_q]):
        app2.handle_events()
    assert app2.running is False


def test_level_selector_keyboard_navigation():
    """Test keyboard and mouse motion navigation in LevelSelector."""
    from src.pushbox.views.ui_components import LevelSelector

    pygame.init()
    screen = pygame.Surface((800, 720))
    selector = LevelSelector(screen)

    selected_level = None
    back_triggered = False

    def on_select(name: str) -> None:
        nonlocal selected_level
        selected_level = name

    def on_back() -> None:
        nonlocal back_triggered
        back_triggered = True

    levels = [f"Level {i}" for i in range(1, 10)]  # 9 levels (fills exactly 1 page)
    progress = {}

    selector.setup(
        level_names=levels,
        progress=progress,
        on_select=on_select,
        on_back=on_back,
        on_edit=lambda x: None,
        on_delete=lambda x: None,
    )

    # 1. Initial selected index is 0
    assert selector.selected_index == 0

    # 2. Right (D) moves to 1
    evt_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    assert selector.handle_event(evt_right) is True
    assert selector.selected_index == 1

    evt_d = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
    assert selector.handle_event(evt_d) is True
    assert selector.selected_index == 2

    # 3. Down (S) moves to 5 (index + 3)
    evt_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    assert selector.handle_event(evt_down) is True
    assert selector.selected_index == 5

    evt_s = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)
    assert selector.handle_event(evt_s) is True
    assert selector.selected_index == 8

    # 4. Left (A) moves to 7
    evt_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    assert selector.handle_event(evt_left) is True
    assert selector.selected_index == 7

    evt_a = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)
    assert selector.handle_event(evt_a) is True
    assert selector.selected_index == 6

    # 5. Up (W) moves to 3
    evt_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    assert selector.handle_event(evt_up) is True
    assert selector.selected_index == 3

    evt_w = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
    assert selector.handle_event(evt_w) is True
    assert selector.selected_index == 0

    # 6. Bounds check: left when index is 0 should be no-op (not handled)
    assert (
        selector.handle_event(evt_left) is False
    )  # selected_index - 1 >= 0 is false, not handled
    assert selector.selected_index == 0

    # Move to last item (index 8)
    selector.selected_index = 8
    # Right on index 8 should be no-op (not handled)
    assert selector.handle_event(evt_right) is False
    assert selector.selected_index == 8

    # Down on index 8 should be no-op (not handled)
    assert selector.handle_event(evt_down) is False
    assert selector.selected_index == 8

    # 7. Enter triggers callback
    selector.selected_index = 5  # Level 6
    evt_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    assert selector.handle_event(evt_enter) is True
    assert selected_level == "Level 6"

    # 8. Space triggers callback
    selected_level = None
    selector.selected_index = 0  # Level 1
    evt_space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    assert selector.handle_event(evt_space) is True
    assert selected_level == "Level 1"

    # 9. Esc triggers back callback
    evt_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    assert selector.handle_event(evt_esc) is True
    assert back_triggered is True

    # M triggers back callback
    back_triggered = False
    evt_m = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)
    assert selector.handle_event(evt_m) is True
    assert back_triggered is True

    # 10. Mouse motion hover syncs selected_index
    button, _, _ = selector.level_buttons[3]  # Index 3 (Level 4)
    original_rect = button.rect
    mock_rect = MagicMock()
    mock_rect.collidepoint.return_value = True
    button.rect = mock_rect

    evt_mouse = pygame.event.Event(pygame.MOUSEMOTION, pos=(100, 100))
    selector.handle_event(evt_mouse)
    assert selector.selected_index == 3

    button.rect = original_rect


def test_level_selector_pagination():
    """Verify LevelSelector pagination bounds, custom levels, reset states.

    Also verify page transition key triggers.
    """
    from src.pushbox.views.ui_components import LevelSelector

    pygame.init()
    screen = pygame.Surface((800, 720))
    selector = LevelSelector(screen)

    selected_level = None
    on_edit_called = False
    on_delete_called = False

    def on_select(name: str) -> None:
        nonlocal selected_level
        selected_level = name

    def on_edit(name: str) -> None:
        nonlocal on_edit_called
        on_edit_called = True

    def on_delete(name: str) -> None:
        nonlocal on_delete_called
        on_delete_called = True

    # =========================================================================
    # PART 1: Page 3 with ONLY default levels (Level 19 and Level 20)
    # =========================================================================
    # Exactly 20 default levels total => 3 pages (Page 1: 9, Page 2: 9, Page 3: 2)
    default_levels_only = [f"Level {i}" for i in range(1, 21)]
    progress = {}

    selector.setup(
        level_names=default_levels_only,
        progress=progress,
        on_select=on_select,
        on_back=lambda: None,
        on_edit=on_edit,
        on_delete=on_delete,
    )

    assert selector.current_page == 0
    assert len(selector.level_buttons) == 9  # exactly 9 items on Page 0
    assert selector.selected_index == 0

    # Flip to Page 2
    evt_pagedown = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEDOWN)
    assert selector.handle_event(evt_pagedown) is True
    assert selector.current_page == 1
    assert len(selector.level_buttons) == 9  # Level 10-18 (9 items)

    # Flip to Page 3
    assert selector.handle_event(evt_pagedown) is True
    assert selector.current_page == 2
    assert len(selector.level_buttons) == 2  # Level 19 and Level 20 (2 items)

    # Ensure Level 19 and Level 20 are classified as default (is_custom is False)
    # and no custom action buttons exist
    for _, name, is_custom in selector.level_buttons:
        assert is_custom is False
        assert name in ["Level 19", "Level 20"]
    assert len(selector.action_buttons) == 0

    # Test clamping on Page 3 (only two items exist: index 0 and 1)
    selector.selected_index = 0  # Level 19
    evt_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    assert selector.handle_event(evt_right) is True
    assert selector.selected_index == 1  # Level 20

    # Right at the end of the last page should be clamped (not handled)
    assert selector.handle_event(evt_right) is False
    assert selector.selected_index == 1

    # Down on the last page with only 2 items should clamp
    evt_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    assert selector.handle_event(evt_down) is False
    assert selector.selected_index == 1

    # Space/Enter launches Level 20 from Page 3
    evt_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    assert selector.handle_event(evt_enter) is True
    assert selected_level == "Level 20"
    selected_level = None

    # =========================================================================
    # PART 2: Page 3 with default levels AND custom levels (Level 19, 20 + Custom 1)
    # =========================================================================
    # 20 default levels + 1 custom level = 21 levels total
    levels_with_custom = [f"Level {i}" for i in range(1, 21)] + ["Custom 1"]

    selector = LevelSelector(screen)
    selector.setup(
        level_names=levels_with_custom,
        progress=progress,
        on_select=on_select,
        on_back=lambda: None,
        on_edit=on_edit,
        on_delete=on_delete,
    )

    # Initial page
    assert selector.current_page == 0
    assert len(selector.level_buttons) == 9

    # Flip to Page 3
    selector.handle_event(evt_pagedown)  # Page 1 -> 2
    selector.handle_event(evt_pagedown)  # Page 2 -> 3
    assert selector.current_page == 2
    assert len(selector.level_buttons) == 3  # Level 19, Level 20, Custom 1

    # Verify classification on Page 3
    for idx, (_, name, is_custom) in enumerate(selector.level_buttons):
        if name == "Custom 1":
            assert is_custom is True
            assert idx == 2
        else:
            assert is_custom is False

    # Custom buttons (Edit/Delete) exist only for custom level on Page 3
    assert len(selector.action_buttons) == 2  # Edit + Delete buttons

    # Navigate: Level 20 (index 1) -> Custom 1 (index 2) via Right/D
    selector.selected_index = 1
    assert selector.handle_event(evt_right) is True
    assert selector.selected_index == 2

    # Clamped at index 2
    assert selector.handle_event(evt_right) is False
    assert selector.selected_index == 2

    # Return to Page 2 using Shift+Tab
    evt_shift_tab = pygame.event.Event(
        pygame.KEYDOWN, key=pygame.K_TAB, mod=pygame.KMOD_SHIFT
    )
    assert selector.handle_event(evt_shift_tab) is True
    assert selector.current_page == 1
    assert selector.selected_index == 0

    # Flip to Page 3 using Tab (without Shift)
    evt_tab = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB, mod=0)
    assert selector.handle_event(evt_tab) is True
    assert selector.current_page == 2
    assert selector.selected_index == 0

    # Bounds verification: cannot go past the last page
    assert selector.handle_event(evt_pagedown) is False
    assert selector.current_page == 2

    # Returns to Page 2 using PageUp
    evt_pageup = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEUP)
    assert selector.handle_event(evt_pageup) is True
    assert selector.current_page == 1

    # Returns to Page 1 using PageUp
    assert selector.handle_event(evt_pageup) is True
    assert selector.current_page == 0

    # Bounds verification: cannot go before first page
    assert selector.handle_event(evt_pageup) is False
    assert selector.current_page == 0


def test_level_selector_pagination_auto_cross_page():
    """Verify keyboard direction keys transition pages dynamically at boundaries."""
    pygame.init()
    screen = pygame.display.set_mode((800, 720))

    selected_level = None

    def on_select(name):
        nonlocal selected_level
        selected_level = name

    # 20 default levels + 1 custom level = 21 levels total
    # (Page 1: 9, Page 2: 9, Page 3: 3)
    level_names = [f"Level {i}" for i in range(1, 21)] + ["Custom 1"]
    progress = {}

    selector = LevelSelector(screen)
    selector.setup(
        level_names,
        progress,
        on_select=on_select,
        on_back=lambda: None,
        on_edit=lambda x: None,
        on_delete=lambda x: None,
    )

    # Starts on page 0 (Page 1) with selected_index = 0
    assert selector.current_page == 0
    assert selector.selected_index == 0

    # 1. UP/W boundary check on Page 1 first row
    evt_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    assert selector.handle_event(evt_up) is False
    assert selector.current_page == 0
    assert selector.selected_index == 0

    # LEFT/A boundary check on Page 1 first item
    evt_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    assert selector.handle_event(evt_left) is False
    assert selector.current_page == 0
    assert selector.selected_index == 0

    # 2. Down on last row of Page 1 (index 7 corresponds to Level 8, column 1)
    selector.selected_index = 7
    evt_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    assert selector.handle_event(evt_down) is True
    assert selector.current_page == 1  # Flipped to Page 2
    assert selector.selected_index == 1  # Retained column 1 (Level 11)

    # 3. Up on first row of Page 2 (index 1 corresponds to Level 11, column 1)
    assert selector.current_page == 1
    assert selector.selected_index == 1
    assert selector.handle_event(evt_up) is True
    assert selector.current_page == 0  # Flipped back to Page 1
    assert selector.selected_index == 7  # Column 1, last row (index 7)

    # 4. Right on last item of Page 1 (index 8 corresponds to Level 9)
    selector.selected_index = 8
    evt_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    assert selector.handle_event(evt_right) is True
    assert selector.current_page == 1  # Flipped to Page 2
    assert selector.selected_index == 0  # Reset to first item of Page 2 (Level 10)

    # 5. Left on first item of Page 2 (index 0 corresponds to Level 10)
    assert selector.current_page == 1
    assert selector.selected_index == 0
    assert selector.handle_event(evt_left) is True
    assert selector.current_page == 0  # Flipped back to Page 1
    assert selector.selected_index == 8  # Last item of Page 1 (index 8)

    # 6. Flip to Page 3 and do boundary checks
    # Move to last row of Page 2 (index 7 corresponds to Level 17, column 1)
    selector.current_page = 1
    selector._layout_buttons(level_names, progress)
    selector.selected_index = 7
    assert selector.handle_event(evt_down) is True
    assert selector.current_page == 2  # Flipped to Page 3
    assert selector.selected_index == 1  # Retained column 1 (Level 20)

    # Down boundary check on Page 3 (clamped since index 1 is last row for Level 20)
    assert selector.handle_event(evt_down) is False
    assert selector.current_page == 2
    assert selector.selected_index == 1

    # Right to Custom 1 (index 2)
    assert selector.handle_event(evt_right) is True
    assert selector.selected_index == 2

    # Down/S and Right/D boundary check on Page 3 last item (index 2 Custom 1)
    assert selector.handle_event(evt_down) is False
    assert selector.handle_event(evt_right) is False
    assert selector.current_page == 2
    assert selector.selected_index == 2

    # 7. Enter launches correct level after cross-page transitions
    selector.selected_index = 1  # Level 20 on Page 3
    evt_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    assert selector.handle_event(evt_enter) is True
    assert selected_level == "Level 20"
