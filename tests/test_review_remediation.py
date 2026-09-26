"""Regression coverage for v1.0.0 review remediation."""

import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

import pygame
import pytest

from main import GameApp
from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level, LevelManager, LevelPersistenceError
from src.pushbox.utils import i18n
from src.pushbox.utils.constants import CellType
from src.pushbox.utils.constants import GameState as GameStateEnum
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


@pytest.mark.parametrize(
    "exit_event",
    [
        pygame.event.Event(pygame.QUIT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, mod=pygame.KMOD_CTRL),
    ],
    ids=["window-close", "ctrl-q"],
)
def test_dirty_editor_testplay_exit_prompts_and_cancel_preserves_draft(
    exit_event: pygame.event.Event,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _make_editor_app()
    draft = [row[:] for row in app.editor.grid]
    monkeypatch.setattr(app.controller.config, "is_animation_enabled", lambda: False)
    app._on_editor_playtest(Level("Valid Playtest", VALID_EDITOR_GRID))

    assert app.current_screen == "game"
    assert app.controller.is_playtest is True
    app.controller.game_state.elapsed_time = 2.5
    app.controller.is_paused = True
    app.transition_state = "fade_in"
    app.transition_alpha = 90
    app.transition_target = "game"
    testplay_grid = app.controller.game_state.level.grid.copy()
    with patch("pygame.event.get", return_value=[exit_event]):
        app.handle_events()

    assert app.current_screen == "editor"
    assert app.editor.show_confirm_dialog is True
    assert app.running is True
    assert app.editor.grid == draft
    assert app.controller.gameplay_active is False

    with patch(
        "pygame.event.get",
        return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_n)],
    ):
        app.handle_events()

    assert app.current_screen == "game"
    assert app.editor.show_confirm_dialog is False
    assert app.editor.grid == draft
    assert app.running is True
    assert app.controller.gameplay_active is True
    assert app.controller.is_playtest is True
    assert app.controller.is_paused is True
    assert app.controller.game_state.elapsed_time == 2.5
    assert (app.controller.game_state.level.grid == testplay_grid).all()
    assert app.transition_state == "fade_in"
    assert app.transition_alpha == 90
    assert app.transition_target == "game"


@pytest.mark.parametrize(
    "exit_event",
    [
        pygame.event.Event(pygame.QUIT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q, mod=pygame.KMOD_CTRL),
    ],
    ids=["window-close", "ctrl-q"],
)
def test_confirmed_dirty_editor_testplay_exit_quits(
    exit_event: pygame.event.Event,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _make_editor_app()
    monkeypatch.setattr(app.controller.config, "is_animation_enabled", lambda: False)
    app._on_editor_playtest(Level("Valid Playtest", VALID_EDITOR_GRID))
    with patch("pygame.event.get", return_value=[exit_event]):
        app.handle_events()
    assert app.editor.show_confirm_dialog is True

    with patch(
        "pygame.event.get",
        return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_y)],
    ):
        app.handle_events()

    assert app.running is False


def test_clean_editor_testplay_quit_does_not_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _make_editor_app()
    app.editor.grid = [row[:] for row in app.editor.original_grid]
    monkeypatch.setattr(app.controller.config, "is_animation_enabled", lambda: False)
    app._on_editor_playtest(Level("Valid Playtest", VALID_EDITOR_GRID))

    with patch("pygame.event.get", return_value=[pygame.event.Event(pygame.QUIT)]):
        app.handle_events()

    assert app.running is False
    assert app.editor.show_confirm_dialog is False


def test_m_from_editor_testplay_returns_to_preserved_draft(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _make_editor_app()
    draft = [row[:] for row in app.editor.grid]
    monkeypatch.setattr(app.controller.config, "is_animation_enabled", lambda: False)
    app._on_editor_playtest(Level("Valid Playtest", VALID_EDITOR_GRID))

    with patch(
        "pygame.event.get",
        return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m)],
    ):
        app.handle_events()

    assert app.current_screen == "editor"
    assert app.editor.grid == draft
    assert app.editor.show_confirm_dialog is False
    assert app.controller.is_playtest is False


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
    level = Level("Timer", VALID_EDITOR_GRID)
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
    level = Level("Campaign-Looking Name", VALID_EDITOR_GRID)
    controller.current_level = level
    controller.game_state = GameState(level)
    controller.save_manager.update_level_progress = lambda *_args: pytest.fail(
        "custom levels must not update built-in campaign progress"
    )

    controller._handle_win()

    completed_builtin = Level("Level 1", VALID_EDITOR_GRID, source="builtin")
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


VALID_EDITOR_GRID = [
    [1, 1, 1, 1, 1],
    [1, 4, 3, 2, 1],
    [1, 1, 1, 1, 1],
]


def test_transition_out_blocks_events_time_and_progress(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = GameApp()
    monkeypatch.setattr(app.controller.config, "is_animation_enabled", lambda: True)
    app.current_screen = "game"
    app.game_buttons = []
    level = Level(
        "Level 1",
        [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 2, 1],
            [1, 1, 1, 1, 1],
        ],
        source="builtin",
    )
    app.controller.load_level_instance(level)
    app.controller.set_gameplay_active(True)
    app.controller.game_state.elapsed_time = 0.75
    save_progress = MagicMock(return_value=False)
    app.controller.save_manager.update_level_progress = save_progress
    initial_grid = app.controller.game_state.level.grid.copy()

    app._start_transition("menu")
    with patch(
        "pygame.event.get",
        return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)],
    ):
        app.handle_events()
    app.update(0.5)

    assert (app.controller.game_state.level.grid == initial_grid).all()
    assert app.controller.game_state.status == GameStateEnum.PLAYING
    assert app.controller.game_state.elapsed_time == pytest.approx(0.75)
    save_progress.assert_not_called()
    assert app.transition_state == "fade_out"


def test_active_game_still_accepts_transition_test_move() -> None:
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
    controller.load_level_instance(level)
    controller.set_gameplay_active(True)
    update_progress = MagicMock(return_value=False)
    controller.save_manager.update_level_progress = update_progress

    assert (
        controller.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
        is True
    )

    assert controller.game_state.status == GameStateEnum.WON
    update_progress.assert_called_once()


def test_editor_save_reports_expected_persistence_failure() -> None:
    app = _make_editor_app()
    app.controller.level_manager.save_level = MagicMock(
        side_effect=LevelPersistenceError("disk failure")
    )
    previous_language = i18n.get_language()
    i18n.set_language("en")
    level = Level("Save Failure", VALID_EDITOR_GRID)

    assert app._on_editor_save(level) is False
    assert app.editor.status_message == (
        "Could not save the level. Check that the levels folder is writable."
    )
    assert app.editor.grid[0][0] == CellType.WALL
    i18n.set_language(previous_language)


def test_remediation_annotations_remain_python39_compatible() -> None:
    module_path = Path(__file__).resolve().parents[1] / "main.py"
    syntax_tree = ast.parse(module_path.read_text(encoding="utf-8"))

    annotation_nodes = []
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.AnnAssign):
            annotation_nodes.append(node.annotation)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            annotation_nodes.extend(
                argument.annotation
                for argument in [
                    *node.args.posonlyargs,
                    *node.args.args,
                    *([node.args.vararg] if node.args.vararg else []),
                    *node.args.kwonlyargs,
                    *([node.args.kwarg] if node.args.kwarg else []),
                ]
                if argument.annotation is not None
            )
            if node.returns is not None:
                annotation_nodes.append(node.returns)

    assert not any(
        isinstance(part, ast.BinOp) and isinstance(part.op, ast.BitOr)
        for annotation in annotation_nodes
        for part in ast.walk(annotation)
    )
