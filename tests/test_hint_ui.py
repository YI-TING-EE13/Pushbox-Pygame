"""Automated unit and integration tests for the Solver Hint UI."""

import os

import pytest

# Ensure dummy video driver is loaded for headless Pygame initialization
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

from main import GameApp
from src.pushbox.models.solver import SolverResult, SolverStatus


@pytest.fixture
def app() -> GameApp:
    """Fixture to initialize a headless GameApp instance."""
    pygame.init()
    # Force show_tutorial to False to boot directly to menu during test
    pygame.display.set_mode((800, 720))
    app_instance = GameApp()
    app_instance.controller.config.set("show_tutorial", False)
    app_instance.current_screen = "game"
    app_instance.controller.load_level("Level 1")
    return app_instance


def test_hint_trigger_solved(app: GameApp) -> None:
    """Test that trigger_hint correctly triggers the solver on a solved level."""
    # Ensure game is running and clear of overlays
    assert app.current_screen == "game"
    assert not app.show_help
    assert not app.controller.is_paused

    # Trigger hint
    app._trigger_hint()

    # Verify that solver solved it and path is cached
    assert len(app.renderer.hint_path) > 0
    assert len(app.renderer.hint_path) <= 3
    assert app.renderer.hint_message == "提示：請沿著高亮方向移動"
    assert app.renderer.hint_end_time > pygame.time.get_ticks()


def test_hint_clears_on_actions(app: GameApp) -> None:
    """Test that hint path/message clear instantly on moves, undos, or resets."""
    app._trigger_hint()
    assert len(app.renderer.hint_path) > 0

    # Action 1: Move clears hint
    app.controller._on_move((0, 1))
    assert app.renderer.hint_path == []
    assert app.renderer.hint_message is None
    assert app.renderer.hint_end_time == 0

    # Action 2: Undo clears hint
    app._trigger_hint()
    assert len(app.renderer.hint_path) > 0
    app.controller._on_undo()
    assert app.renderer.hint_path == []

    # Action 3: Reset clears hint
    app._trigger_hint()
    assert len(app.renderer.hint_path) > 0
    app.controller._on_reset()
    assert app.renderer.hint_path == []


def test_hint_blocked_by_overlays(app: GameApp) -> None:
    """Verify that hint does not trigger when help, pause, or overlays are active."""
    # Scenario A: Help Overlay is active
    app.show_help = True
    app._trigger_hint()
    assert app.renderer.hint_path == []

    # Scenario B: Paused State is active
    app.show_help = False
    app.controller.is_paused = True
    app._trigger_hint()
    assert app.renderer.hint_path == []

    # Scenario C: Not on Game Screen
    app.controller.is_paused = False
    app.current_screen = "menu"
    app._trigger_hint()
    assert app.renderer.hint_path == []


def test_hint_blocked_on_level_0(app: GameApp) -> None:
    """Verify that hint does not trigger on Onboarding Level 0 to prevent UX noise."""
    app.controller.load_level("Level 0")
    app.current_screen = "game"

    app._trigger_hint()
    assert app.renderer.hint_path == []
    assert app.renderer.hint_message is None


def test_hint_message_mapping_states(
    app: GameApp, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify correct status-to-message mapping for solver outcome scenarios."""
    # Test Scenario 1: NODE_LIMIT_EXCEEDED
    monkeypatch.setattr(
        "main.solve",
        lambda *args, **kwargs: SolverResult(
            SolverStatus.NODE_LIMIT_EXCEEDED, None, 100
        ),
    )
    app._trigger_hint()
    assert app.renderer.hint_path == []
    assert app.renderer.hint_message == "此局面較複雜，暫時找不到可靠提示。"

    # Test Scenario 2: UNSOLVED
    monkeypatch.setattr(
        "main.solve",
        lambda *args, **kwargs: SolverResult(SolverStatus.UNSOLVED, None, 100),
    )
    app._trigger_hint()
    assert app.renderer.hint_path == []
    assert (
        app.renderer.hint_message == "目前局面可能無法完成，建議按 Z 撤銷或 F5 重置。"
    )

    # Test Scenario 3: INVALID_LEVEL
    monkeypatch.setattr(
        "main.solve",
        lambda *args, **kwargs: SolverResult(SolverStatus.INVALID_LEVEL, None, 0),
    )
    app._trigger_hint()
    assert app.renderer.hint_path == []
    assert app.renderer.hint_message == "目前關卡資料無法產生提示。"

    # Test Scenario 4: SOLVED but empty path (already solved)
    monkeypatch.setattr(
        "main.solve",
        lambda *args, **kwargs: SolverResult(SolverStatus.SOLVED, [], 0),
    )
    app._trigger_hint()
    assert app.renderer.hint_path == []
    assert app.renderer.hint_message == "目前已在完成狀態"
