"""Tests for Settings language option, main menu localization, and i18n."""

import os
import sys
from unittest.mock import MagicMock

import pygame
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import GameApp
from src.pushbox.utils import i18n
from src.pushbox.utils.config import Config
from src.pushbox.views.ui_components import SettingsScreen


@pytest.fixture(autouse=True)
def restore_language():
    """Ensure global active language is restored to 'en' after each test."""
    yield
    i18n.set_language("en")


def test_main_menu_defaults_to_english(monkeypatch):
    """Verify main menu button labels default to English."""
    monkeypatch.setattr(
        pygame.display, "set_mode", MagicMock(return_value=pygame.Surface((1024, 768)))
    )

    app = GameApp()
    # Reset language
    i18n.set_language("en")
    app._setup_menu()

    labels = [btn.text for btn in app.menu.buttons]
    assert "Start Game" in labels
    assert "Settings" in labels
    assert "About Game" in labels
    assert "Quit" in labels


def test_main_menu_rebuilds_to_zh_tw(monkeypatch):
    """Verify main menu buttons rebuild to zh-TW correctly."""
    monkeypatch.setattr(
        pygame.display, "set_mode", MagicMock(return_value=pygame.Surface((1024, 768)))
    )

    app = GameApp()
    i18n.set_language("zh-TW")
    app._setup_menu()

    labels = [btn.text for btn in app.menu.buttons]
    assert "開始遊戲" in labels
    assert "設定" in labels
    assert "關於遊戲" in labels
    assert "退出" in labels


def test_settings_screen_options_structure():
    """Verify SettingsScreen exposes exactly 7 options and contains Language option."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    # Mock Config and SaveManager
    mock_config = MagicMock(spec=Config)
    mock_config.get_control_scheme.return_value = "arrows"
    mock_config.get_string.return_value = "nord_blue"
    mock_config.get_bool.return_value = True
    mock_config.get_language.return_value = "en"

    mock_save = MagicMock()

    settings = SettingsScreen(screen, mock_config, mock_save)

    assert settings.options_count == 7
    # Options: 0: Control, 1: Theme, 2: Animation, 3: Show Tutorial,
    # 4: Language, 5: Reset Progress, 6: Back
    assert settings.selected_index == 0


def test_settings_language_toggle_and_sync():
    """Verify toggling language updates config, syncs i18n, and cycles back."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    config = Config()
    config.set_language("en")  # Start with English
    assert i18n.get_language() == "en"

    mock_save = MagicMock()
    settings = SettingsScreen(screen, config, mock_save)

    # Option index 4 is Language
    # 1. Cycle to zh-TW
    settings._trigger_option(4)
    assert config.get_language() == "zh-TW"
    assert i18n.get_language() == "zh-TW"

    # 2. Cycle back to en
    settings._trigger_option(4)
    assert config.get_language() == "en"
    assert i18n.get_language() == "en"

    # 3. Ensure triggering Language does not reset progress
    settings._trigger_option(4)
    assert mock_save.reset_progress.call_count == 0


def test_settings_adjust_option_via_keys():
    """Verify left/right key adjustment triggers language toggle."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    config = Config()
    config.set_language("en")

    mock_save = MagicMock()
    settings = SettingsScreen(screen, config, mock_save)

    # 1. Toggle via right key adjustment on index 4
    settings._adjust_option(4, right=True)
    assert config.get_language() == "zh-TW"
    assert i18n.get_language() == "zh-TW"

    # 2. Toggle via left key adjustment on index 4
    settings._adjust_option(4, right=False)
    assert config.get_language() == "en"
    assert i18n.get_language() == "en"


def test_settings_screen_draw_no_crash():
    """Verify that drawing the settings screen in both languages does not crash."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    config = Config()
    mock_save = MagicMock()
    settings = SettingsScreen(screen, config, mock_save)

    # Draw in English
    config.set_language("en")
    settings.draw()

    # Draw in Traditional Chinese
    config.set_language("zh-TW")
    settings.draw()


def test_about_screen_localization():
    """Verify AboutScreen draw and localized labels."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    from src.pushbox.views.ui_components import AboutScreen

    about = AboutScreen(screen)

    # 1. English Mode
    i18n.set_language("en")
    assert i18n.t("about.title") == "About / Credits"
    assert i18n.t("about.intro_lbl") == "Description: "
    about.draw()

    # 2. Chinese Mode
    i18n.set_language("zh-TW")
    assert i18n.t("about.title") == "關於遊戲 / Credits"
    assert i18n.t("about.intro_lbl") == "遊戲簡介: "
    about.draw()


def test_tutorial_screen_localization():
    """Verify TutorialScreen draw and localized labels."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    from src.pushbox.views.ui_components import TutorialScreen

    tutorial = TutorialScreen(screen)

    # 1. English Mode
    i18n.set_language("en")
    assert i18n.t("tutorial.title") == "How to Play"
    assert i18n.t("tutorial.goal.title") == "🎯 Objective"
    tutorial.draw()

    # 2. Chinese Mode
    i18n.set_language("zh-TW")
    assert i18n.t("tutorial.title") == "遊戲教學"
    assert i18n.t("tutorial.goal.title") == "🎯 遊戲目標"
    tutorial.draw()


def test_bottom_gameplay_buttons_localization(monkeypatch):
    """Verify bottom gameplay buttons localization and re-init."""
    monkeypatch.setattr(
        pygame.display,
        "set_mode",
        MagicMock(return_value=pygame.Surface((1024, 768))),
    )

    app = GameApp()

    # 1. English Mode
    i18n.set_language("en")
    app._init_game_buttons()
    assert app.btn_undo.text == "Undo (Z)"
    assert app.btn_reset.text == "Reset (F5)"
    assert app.btn_redo.text == "Redo (Y)"
    assert app.btn_hint.text == "💡 Hint (I)"

    # 2. Chinese Mode
    i18n.set_language("zh-TW")
    app._init_game_buttons()
    assert app.btn_undo.text == "撤銷 (Z)"
    assert app.btn_reset.text == "重置 (F5)"
    assert app.btn_redo.text == "重做 (Y)"
    assert app.btn_hint.text == "💡 提示 (I)"


def test_level_selector_screen_localization():
    """Verify LevelSelector layout and detail panels are localized."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    from src.pushbox.views.ui_components import LevelSelector

    # Create dummy LevelManager mock to prevent scanning disk levels
    mock_lm = MagicMock()
    mock_lm.get_level_names.return_value = ["Level 1", "Level 2"]
    mock_lm.get_level.return_value = None

    selector = LevelSelector(screen, level_manager=mock_lm)

    levels = [
        "Level 1",
        "Level 2",
        "Level 3",
        "Level 4",
        "Level 5",
        "Level 6",
        "Level 7",
        "Level 8",
        "Level 9",
        "Level 10",
    ]
    progress = {"Level 1": {"completed": True, "best_moves": 12}}

    on_select = MagicMock()
    on_back = MagicMock()
    on_edit = MagicMock()
    on_delete = MagicMock()

    # 1. English Mode
    i18n.set_language("en")
    selector.setup(levels, progress, on_select, on_back, on_edit, on_delete)

    # Re-trigger to populate button list
    assert selector._last_language == "en"
    assert selector.back_button.text == "Back"
    assert selector.import_button.text == "Import Level"
    # Over 9 levels will render navigation buttons
    assert len(selector.nav_buttons) == 2
    assert selector.nav_buttons[0].text == "◀ Prev"
    assert selector.nav_buttons[1].text == "Next ▶"

    # Detail panel texts in English
    selector.selected_index = 0
    selector.draw(progress)  # Ensure no crash

    # 2. Traditional Chinese Mode
    i18n.set_language("zh-TW")
    # Draw triggers layout refresh automatically
    selector.draw(progress)
    assert selector._last_language == "zh-TW"
    assert selector.back_button.text == "返回"
    assert selector.import_button.text == "匯入關卡"
    assert selector.nav_buttons[0].text == "◀ 上一頁"
    assert selector.nav_buttons[1].text == "下一頁 ▶"


def test_level_selector_custom_levels_buttons_localization():
    """Verify custom levels edit and delete buttons are localized correctly."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    from src.pushbox.views.ui_components import LevelSelector

    mock_lm = MagicMock()
    mock_lm.get_level.return_value = None
    selector = LevelSelector(screen, level_manager=mock_lm)

    levels = ["Custom 1"]
    progress = {}

    on_select = MagicMock()
    on_back = MagicMock()
    on_edit = MagicMock()
    on_delete = MagicMock()

    # 1. English Mode
    i18n.set_language("en")
    selector.setup(levels, progress, on_select, on_back, on_edit, on_delete)
    # Custom levels have edit/delete action buttons
    assert len(selector.action_buttons) == 2
    assert selector.action_buttons[0].text == "Edit"
    assert selector.action_buttons[1].text == "Delete"

    # 2. Chinese Mode
    i18n.set_language("zh-TW")
    selector.draw(progress)  # Auto refresh buttons
    assert selector.action_buttons[0].text == "編輯"
    assert selector.action_buttons[1].text == "刪除"


def test_import_dialog_localization():
    """Verify Level Import Dialog contains localized titles, hints, and button texts."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    from src.pushbox.views.ui_components import LevelSelector

    mock_lm = MagicMock()
    mock_lm.get_level.return_value = None
    selector = LevelSelector(screen, level_manager=mock_lm)

    selector.show_import_dialog = True
    selector._on_import_button_click()

    # 1. English Mode
    i18n.set_language("en")
    selector._draw_import_dialog()  # Ensure no crash

    # 2. Chinese Mode
    i18n.set_language("zh-TW")
    selector._draw_import_dialog()  # Ensure no crash


def test_i18n_fallback_robustness():
    """Verify nonexistent keys return key itself and unsupported language falls back."""
    i18n.set_language("en")

    # Missing keys fallback safely without crash
    assert i18n.t("nonexistent.dummy.key") == "nonexistent.dummy.key"

    # Set unsupported language remains on English
    i18n.set_language("fr")
    assert i18n.get_language() == "en"


def test_level_editor_ui_localization():
    """Verify LevelEditor UI components localize correctly and do not crash on draw."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    from src.pushbox.utils.constants import CellType
    from src.pushbox.views.level_editor import LevelEditor

    editor = LevelEditor(screen)

    # 1. English Mode
    i18n.set_language("en")
    editor.draw()  # Triggers button layout refresh and draw

    assert editor._last_language == "en"
    # Sidebar export button is at index 4
    # (0: rows-, 1: rows+, 2: cols-, 3: cols+, 4: export)
    assert editor.buttons[4].text == "Export (E)"
    # Bottom toolbar functional buttons
    assert editor.buttons[5].text == "Undo(Z)"
    assert editor.buttons[6].text == "Redo(Y)"
    assert editor.buttons[7].text == "Clear(C)"
    assert editor.buttons[8].text == "Exit"
    assert editor.buttons[9].text == "Save(S)"
    assert editor.buttons[10].text == "Playtest(T)"

    # Test error status and overlays
    editor.grid[2][2] = CellType.BOX
    editor.grid[3][3] = CellType.TARGET
    editor._save_level()
    assert editor.status_message == "Error: Player is required!"

    editor.show_confirm_dialog = True
    editor.show_export_dialog = True
    editor._draw_confirm_dialog()
    editor._draw_export_dialog()

    # 2. Traditional Chinese Mode
    i18n.set_language("zh-TW")
    editor.draw()

    assert editor._last_language == "zh-TW"
    assert editor.buttons[4].text == "匯出關卡 (E)"
    assert editor.buttons[5].text == "撤銷(Z)"
    assert editor.buttons[6].text == "重做(Y)"
    assert editor.buttons[7].text == "清除(C)"
    assert editor.buttons[8].text == "退出"
    assert editor.buttons[9].text == "儲存(S)"
    assert editor.buttons[10].text == "試玩(T)"

    editor._save_level()
    assert editor.status_message == "錯誤: 必須放置玩家!"

    editor._draw_confirm_dialog()
    editor._draw_export_dialog()


def test_gameplay_hud_and_onboarding_localization(monkeypatch):
    """Verify that HUD stats, prompts, and onboarding tip banners localize."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    from src.pushbox.models.game_state import GameState
    from src.pushbox.models.level import Level
    from src.pushbox.views.renderer import Renderer

    renderer = Renderer(screen)
    # Mock game state and Level 0
    level_0_grid = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 4, 0, 0, 3, 2, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    level = Level("Level 0", level_0_grid)
    game_state = MagicMock(spec=GameState)
    game_state.level = level
    game_state.get_stats.return_value = {"moves": 5, "pushes": 3, "time": "00:15"}

    # 1. English Mode
    i18n.set_language("en")
    # Call render_ui with show_help=False
    renderer.render_ui(game_state, show_help=False, control_scheme="方向鍵 / WASD")

    # Check that translations match English
    assert "Moves: 5" in i18n.t("gameplay.hud_moves").format(moves=5)
    assert "Pushes: 3" in i18n.t("gameplay.hud_pushes").format(pushes=3)
    assert "Time: 00:15" in i18n.t("gameplay.hud_time").format(time="00:15")
    assert "Press H for Help" in i18n.t("gameplay.hud_help_prompt")

    # 2. Chinese Mode
    i18n.set_language("zh-TW")
    renderer.render_ui(game_state, show_help=False, control_scheme="方向鍵 / WASD")

    # Check that translations match Chinese
    assert "步數: 5" in i18n.t("gameplay.hud_moves").format(moves=5)
    assert "推動: 3" in i18n.t("gameplay.hud_pushes").format(pushes=3)
    assert "時間: 00:15" in i18n.t("gameplay.hud_time").format(time="00:15")
    assert "按 H 顯示說明" in i18n.t("gameplay.hud_help_prompt")


def test_gameplay_overlays_localization():
    """Verify that Help, Win, Deadlock, and Pause overlays render safely."""
    pygame.init()
    screen = pygame.Surface((1024, 768))

    from src.pushbox.views.renderer import Renderer

    renderer = Renderer(screen)

    # 1. English Mode
    i18n.set_language("en")
    renderer._render_help_overlay()
    renderer.render_win_screen(
        {"moves": 10, "pushes": 5, "time": "00:30"}, is_record=True, best_moves=8
    )
    renderer.render_game_over_screen()
    renderer.render_pause_screen()

    # Assert English texts are resolved correctly
    assert i18n.t("gameplay.help_title") == "Game Controls"
    assert i18n.t("gameplay.deadlock_title") == "DEADLOCK!"
    assert i18n.t("gameplay.pause_title") == "PAUSED"

    # 2. Chinese Mode
    i18n.set_language("zh-TW")
    renderer._render_help_overlay()
    renderer.render_win_screen(
        {"moves": 10, "pushes": 5, "time": "00:30"}, is_record=True, best_moves=8
    )
    renderer.render_game_over_screen()
    renderer.render_pause_screen()

    # Assert Chinese texts are resolved correctly
    assert i18n.t("gameplay.help_title") == "遊戲控制"
    assert i18n.t("gameplay.deadlock_title") == "死鎖!"
    assert i18n.t("gameplay.pause_title") == "暫停"


def test_solver_hint_localization():
    """Verify that BFS solver feedback messages are localized correctly."""
    # 1. English Mode
    i18n.set_language("en")
    assert i18n.t("hint.move") == "Hint: Please move along the highlighted path"
    assert i18n.t("hint.completed") == "Hint: Level is already solved!"
    assert (
        i18n.t("hint.complex")
        == "Hint: State space is too complex, no reliable hint found."
    )
    assert (
        i18n.t("hint.unsolvable")
        == "Hint: Level may be unsolvable. Press Z to Undo or F5 to Reset."
    )
    assert i18n.t("hint.invalid") == "Hint: Current level data cannot generate hints."

    # 2. Chinese Mode
    i18n.set_language("zh-TW")
    assert i18n.t("hint.move") == "提示：請沿著高亮方向移動"
    assert i18n.t("hint.completed") == "目前已在完成狀態"
    assert i18n.t("hint.complex") == "此局面較複雜，暫時找不到可靠提示。"
    assert (
        i18n.t("hint.unsolvable") == "目前局面可能無法完成，建議按 Z 撤銷或 F5 重置。"
    )
    assert i18n.t("hint.invalid") == "目前關卡資料無法產生提示。"
