"""Tests for AboutScreen integration, theme compliance, and navigation flow."""

import os
import sys
from unittest.mock import MagicMock

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import GameApp
from src.pushbox.utils.constants import APP_VERSION, set_theme
from src.pushbox.views.ui_components import AboutScreen


def test_about_screen_attributes_and_content():
    """Verify that AboutScreen exposes correct testable attributes."""
    # Initialize pygame fonts for text rendering in screen init
    pygame.init()
    screen = pygame.Surface((1024, 768))

    about = AboutScreen(screen)
    assert about.app_version == APP_VERSION
    assert APP_VERSION in about.app_version
    assert about.github_url == "https://github.com/YI-TING-EE13/Pushbox-Pygame"
    assert about.license_info == "MIT License"

    # Verify content lines structure contains all key specifications
    content_joined = "\n".join(about.content_lines)
    assert about.app_version in content_joined
    assert about.github_url in content_joined
    assert about.license_info in content_joined
    assert "Sokoban" in content_joined

    # Verify credit lines structure
    credit_joined = "\n".join(about.credit_lines)
    assert "contributors" in credit_joined
    assert "External asset" in credit_joined


def test_about_screen_theme_rendering():
    """Verify that AboutScreen.draw() executes successfully under themes."""
    pygame.init()
    screen = pygame.Surface((1024, 768))
    about = AboutScreen(screen)

    # Test all 3 game design themes
    themes = ["nord_blue", "classic_green", "dracula_purple"]
    for theme in themes:
        set_theme(theme)
        # Should render onto the canvas successfully without any KeyError or crash
        about.draw()


def test_about_screen_navigation_callbacks():
    """Verify that back callbacks are triggered via Esc key and mouse clicks."""
    pygame.init()
    screen = pygame.Surface((1024, 768))
    about = AboutScreen(screen)

    back_mock = MagicMock()
    about.set_on_back(back_mock)

    # 1. Esc Key Press
    event_esc = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    handled = about.handle_event(event_esc)
    assert handled is True
    assert back_mock.call_count == 1

    # 2. Mouse click on back button rect
    about.back_button_rect = pygame.Rect(100, 100, 200, 50)
    event_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(150, 120))
    handled_click = about.handle_event(event_click)
    assert handled_click is True
    assert back_mock.call_count == 2

    # 3. Mouse click outside button has no effect
    event_miss = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(50, 50))
    handled_miss = about.handle_event(event_miss)
    assert handled_miss is False
    assert back_mock.call_count == 2


def test_about_screen_integration_in_main_app(monkeypatch):
    """Verify integration of AboutScreen in GameApp and routing logic."""
    pygame.init()
    # Mock display.set_mode to prevent spawning a real OS window in test env
    monkeypatch.setattr(
        pygame.display, "set_mode", MagicMock(return_value=pygame.Surface((1024, 768)))
    )

    app = GameApp()
    # Check that "關於遊戲" exists in menu buttons
    about_btn = None
    for btn in app.menu.buttons:
        if btn.text == "關於遊戲":
            about_btn = btn
            break
    assert about_btn is not None, "About game button must exist on the menu."

    # Verify selection trigger shifts transition target
    assert app.current_screen == "menu"
    about_btn.callback()

    assert app.transition_target == "about"
    assert app.transition_state == "fade_out"
