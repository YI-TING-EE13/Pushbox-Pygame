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
