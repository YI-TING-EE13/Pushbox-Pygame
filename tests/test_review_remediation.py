"""Regression coverage for v1.0.0 review remediation."""

from unittest.mock import MagicMock, patch

import pygame
import pytest

from main import GameApp
from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level, LevelManager
from src.pushbox.utils import i18n
from src.pushbox.utils.constants import CellType
from src.pushbox.views.level_editor import LevelEditor
from src.pushbox.views.renderer import Renderer
from src.pushbox.views.ui_components import LevelSelector, Menu


@pytest.fixture(autouse=True)
def initialize_headless_pygame(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()


def _make_editor_app() -> GameApp:
    app = GameApp()
    app.current_screen = "editor"
    editor = LevelEditor(app.screen)
    editor.set_on_exit(app._complete_editor_exit)
    editor.grid[0][0] = CellType.WALL
    app.editor = editor
    return app


@pytest.mark.parametrize("exit_action", ["menu", "escape", "button", "quit", "ctrl_q"])
def test_dirty_editor_exit_routes_require_confirmation(
    exit_action: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = _make_editor_app()
    monkeypatch.setattr(app.controller.config, "is_animation_enabled", lambda: False)

    if exit_action == "menu":
        events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)]
    elif exit_action == "escape":
        events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
    elif exit_action == "quit":
        events = [pygame.event.Event(pygame.QUIT)]
    elif exit_action == "ctrl_q":
        events = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, mod=pygame.KMOD_CTRL)
        ]
    else:
        exit_button = next(
            button
            for button in app.editor.buttons
            if getattr(button.callback, "__name__", "") == "_request_exit"
        )
        pos = exit_button.rect.center
        events = [
            pygame.event.Event(
                pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)
            ),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1),
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1),
        ]

    with patch("pygame.event.get", return_value=events):
        app.handle_events()

    assert app.editor.show_confirm_dialog is True
    assert app.running is True
    assert app.current_screen == "editor"

    with patch(
        "pygame.event.get",
        return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_y)],
    ):
        app.handle_events()

    if exit_action in ("quit", "ctrl_q"):
        assert app.running is False
    else:
        assert app.current_screen == "menu"
        assert app.editor is None


def test_cancel_editor_exit_keeps_editor_open() -> None:
    app = _make_editor_app()
    with patch(
        "pygame.event.get",
        return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)],
    ):
        app.handle_events()
    with patch(
        "pygame.event.get",
        return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_n)],
    ):
        app.handle_events()

    assert app.current_screen == "editor"
    assert app.editor.show_confirm_dialog is False
    assert app._pending_editor_exit is None


def test_pause_settings_return_preserves_pause_and_active_timer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = GameApp()
    monkeypatch.setattr(app.controller.config, "is_animation_enabled", lambda: False)
    app.controller.load_level("Level 1")
    app.current_screen = "game"
    app.controller.set_gameplay_active(True)
    app.controller.is_paused = True
    app.controller.game_state.elapsed_time = 4.0

    app._show_settings()
    assert app.current_screen == "settings"
    app.update(2.0)
    assert app.controller.game_state.elapsed_time == 4.0

    app.settings.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert app.current_screen == "game"
    assert app.controller.is_paused is True
    app.update(3.0)
    assert app.controller.game_state.elapsed_time == 4.0

    app.controller.toggle_pause()
    app.update(0.25)
    assert app.controller.game_state.elapsed_time == 4.25


def test_controller_timer_uses_only_active_gameplay_delta() -> None:
    controller = GameController()
    level = Level("Timer", [[1, 1, 1], [1, 4, 1], [1, 1, 1]])
    controller.current_level = level
    controller.game_state = GameState(level)

    controller.update(10.0)
    assert controller.game_state.elapsed_time == 0.0

    controller.set_gameplay_active(True)
    controller.update(0.3)
    controller.set_gameplay_active(False)
    controller.update(8.0)
    assert controller.game_state.elapsed_time == pytest.approx(0.3)


def test_loading_next_level_keeps_active_gameplay_clock_running() -> None:
    controller = GameController()
    controller.set_gameplay_active(True)

    assert controller.load_level("Level 1") is True
    controller.update(0.2)

    assert controller.game_state.elapsed_time == pytest.approx(0.2)


def test_animation_setting_clears_and_blocks_optional_renderer_effects() -> None:
    pygame.init()
    renderer = Renderer(pygame.Surface((640, 480)))
    renderer.add_win_animation()
    renderer.trigger_screen_shake()
    assert renderer.animations
    assert renderer.shake_duration > 0

    renderer.set_animation_enabled(False)
    assert renderer.animations == []
    assert renderer.shake_duration == 0
    assert (renderer.shake_offset_x, renderer.shake_offset_y) == (0, 0)
    renderer.add_win_animation()
    renderer.trigger_screen_shake()
    assert renderer.animations == []
    assert renderer.shake_duration == 0


def test_campaign_progress_and_level_types_use_source_metadata() -> None:
    level_manager = LevelManager()
    custom_prefixed = Level(
        "Custom_Imported",
        [[1, 1, 1], [1, 4, 1], [1, 1, 1]],
        source="custom",
    )
    custom_campaign_like = Level(
        "Level 42", [[1, 1, 1], [1, 4, 1], [1, 1, 1]], source="custom"
    )
    level_manager.levels[custom_prefixed.name] = custom_prefixed
    level_manager.levels[custom_campaign_like.name] = custom_campaign_like
    level_manager.levels["Custom Builtin"] = Level(
        "Custom Builtin", [[1, 1, 1], [1, 4, 1], [1, 1, 1]], source="builtin"
    )
    assert "Custom_Imported" not in level_manager.get_campaign_level_names()
    assert "Level 42" not in level_manager.get_campaign_level_names()
    assert "Level 1" in level_manager.get_campaign_level_names()

    selector = LevelSelector(pygame.Surface((800, 720)), level_manager)
    selector.setup(
        ["Custom Builtin", "Custom_Imported", "Level 42"],
        {},
        lambda _name: None,
        lambda: None,
        lambda _name: None,
        lambda _name: None,
    )
    assert selector.level_buttons[0][2] is False
    assert selector.level_buttons[1][2] is True
    assert selector.level_buttons[2][2] is True


def test_menu_campaign_progress_is_localized_and_excludes_custom_entries() -> None:
    menu = Menu(pygame.Surface((800, 600)), "PushBox")
    rendered: list[str] = []

    class FontCapture:
        def render(self, text: str, _antialias: bool, _color: tuple[int, ...]):
            rendered.append(text)
            return pygame.Surface((200, 24))

    menu.font = FontCapture()
    progress = {
        "Level 1": {"completed": True},
        "Custom_Imported": {"completed": True},
        "Level 42": {"completed": True},
    }
    previous_language = i18n.get_language()
    i18n.set_language("en")
    menu.draw(
        level_names=["Level 1", "Custom_Imported", "Level 42"],
        current_level="Custom_Imported",
        progress=progress,
        campaign_level_names=["Level 1"],
    )
    assert "★ 1 / 1 levels" in rendered
    assert "Current level: Custom_Imported" in rendered

    rendered.clear()
    menu.draw(
        level_names=["Level 1"],
        current_level="None",
        progress={},
        campaign_level_names=["Level 1"],
    )
    assert "★ 0 / 1 levels" in rendered

    rendered.clear()
    i18n.set_language("zh-TW")
    menu.draw(
        level_names=["Level 1", "Custom_Imported", "Level 42"],
        current_level="自訂匯入",
        progress=progress,
        campaign_level_names=["Level 1"],
    )
    assert "★ 1 / 1 關" in rendered
    assert "當前關卡：自訂匯入" in rendered
    i18n.set_language(previous_language)


def test_share_import_errors_follow_active_ui_language() -> None:
    selector = LevelSelector(pygame.Surface((800, 600)), level_manager=MagicMock())
    previous_language = i18n.get_language()
    i18n.set_language("zh-TW")
    selector._import_level("invalid")
    assert selector.import_error_message is not None
    assert "分享碼格式不正確" in selector.import_error_message
    assert "Invalid share code" not in selector.import_error_message
    i18n.set_language(previous_language)


def test_custom_level_completion_does_not_record_campaign_progress() -> None:
    controller = GameController()
    level = Level("Campaign-Looking Name", [[1, 1, 1], [1, 4, 1], [1, 1, 1]])
    controller.current_level = level
    controller.game_state = GameState(level)
    controller.save_manager.update_level_progress = lambda *_args: pytest.fail(
        "custom levels must not update built-in campaign progress"
    )

    controller._handle_win()

    completed_builtin = Level(
        "Level 1", [[1, 1, 1], [1, 4, 1], [1, 1, 1]], source="builtin"
    )
    controller.current_level = completed_builtin
    controller.game_state = GameState(completed_builtin)
    progress_calls: list[tuple[object, ...]] = []
    controller.save_manager.update_level_progress = lambda *args: (
        progress_calls.append(args) or False
    )
    controller._handle_win()
    assert len(progress_calls) == 1
    assert progress_calls[0][0] == "Level 1"


def test_completion_records_injected_active_gameplay_time() -> None:
    controller = GameController()
    level = Level(
        "Level 1",
        [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 2, 1],
            [1, 1, 1, 1, 1],
        ],
        source="builtin",
    )
    controller.current_level = level
    controller.game_state = GameState(level)
    controller.set_gameplay_active(True)
    update_progress = MagicMock(return_value=False)
    controller.save_manager.update_level_progress = update_progress

    controller.update(0.35)
    controller._on_move((0, 1))

    assert update_progress.call_count == 1
    assert update_progress.call_args.args == ("Level 1", 1, 0.35, 1)
