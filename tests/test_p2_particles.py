import os
import sys

import pygame
import pytest

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import GameApp
from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.level import Level
from src.pushbox.views.renderer import TargetSparkAnimation


@pytest.fixture(autouse=True)
def setup_pygame():
    """Setup headless pygame environment for testing."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


def test_box_on_target_event_trigger():
    """Test that box_on_target event triggers when pushing box to target."""
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 3, 2, 1],  # Player at (1,1), Box at (1,2), Target at (1,3)
        [1, 1, 1, 1, 1],
    ]
    level = Level("Test Target", grid)
    controller = GameController()
    controller.load_level_instance(level)

    box_on_target_triggered = False
    triggered_pos = None

    def on_box_on_target(pos):
        nonlocal box_on_target_triggered, triggered_pos
        box_on_target_triggered = True
        triggered_pos = pos

    controller.register_callback("box_on_target", on_box_on_target)

    # 1. Player moves but does not push box (e.g. moves into wall or down)
    controller._on_move((1, 0))  # Try down
    assert box_on_target_triggered is False

    # 2. Player pushes box onto target (RIGHT)
    controller._on_move((0, 1))
    assert box_on_target_triggered is True
    assert triggered_pos == (1, 3)


def test_target_spark_animation_physics():
    """Test TargetSparkAnimation initialization and particle decay."""
    anim = TargetSparkAnimation(pos=(1, 3), start_time=1.0, duration=0.25)

    assert anim.pos == (1, 3)
    assert len(anim.particles) == 12

    # Check that initially all particles are alive with life = 1.0
    for p in anim.particles:
        assert p["life"] == 1.0
        assert p["decay"] > 0

    # Update animation to progress time
    anim.update(current_time=1.1)

    # Particles should have decayed
    for p in anim.particles:
        assert p["life"] < 1.0

    # Progress till completion
    anim.update(current_time=1.3)
    assert anim.finished is True


def test_attract_mode_loop_and_reset(monkeypatch):
    """Test attract mode timer updates, path moves, and resets."""
    # Headless GameApp initialization
    app = GameApp()
    app.current_screen = "menu"

    # Call update which will load Level 1 automatically
    app.update()

    assert app.attract_game_state is not None
    assert app.attract_index == 0

    # Simulate time progression to trigger step (timer threshold is 1.2)
    app.attract_timer = 1.25
    app.update()

    # Should have executed step 1, index increased
    assert app.attract_index == 1
    assert app.attract_timer == 0.0  # Reset

    # Simulate completion of all steps to trigger reset
    app.attract_index = len(app.attract_path)
    app.attract_reset_timer = 0.01  # Trigger countdown

    # Let countdown pass (dt will be approx 1/60s = 0.016s)
    app.update()

    # Should have triggered reset timer countdown, eventually resetting state to None
    assert app.attract_reset_timer < 0.01
