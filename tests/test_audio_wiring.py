"""Integration tests for gameplay SFX event wiring."""

from unittest.mock import MagicMock, patch

import numpy as np
import pygame
import pytest

from src.pushbox.controllers.game_controller import GameController
from src.pushbox.models.level import Level


@pytest.fixture
def mock_audio() -> MagicMock:
    """Fixture to mock AudioManager entirely."""
    # Reset singleton state before each test
    from src.pushbox.utils.audio import AudioManager

    AudioManager._instance = None

    with patch("src.pushbox.controllers.game_controller.AudioManager") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_level() -> Level:
    """Fixture to create a mock playable Sokoban level."""
    # 5x5 Grid:
    # 1 1 1 1 1
    # 1 4 0 3 1
    # 1 0 2 0 1
    # 1 1 1 1 1
    grid = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 4, 0, 3, 1],
            [1, 0, 2, 0, 1],
            [1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
        ]
    )
    # Player at (1, 1), Box at (1, 3), Target at (2, 2)
    lvl = Level("TestLevel", grid)
    return lvl


def test_successful_move_calls_play_move(
    mock_audio: MagicMock, mock_level: Level
) -> None:
    """Verify that a normal successful move plays move.wav only."""
    controller = GameController()
    controller.load_level_instance(mock_level)

    # Move Down (1, 1) -> (2, 1) which is empty floor (0)
    # direction Down is (1, 0)
    controller._on_move((1, 0))

    mock_audio.play_move.assert_called_once()
    mock_audio.play_push.assert_not_called()
    mock_audio.play_bump.assert_not_called()


def test_invalid_move_calls_play_bump(mock_audio: MagicMock, mock_level: Level) -> None:
    """Verify that an invalid move (hitting wall) plays bump.wav only."""
    controller = GameController()
    controller.load_level_instance(mock_level)

    # Move Left (1, 1) -> (1, 0) which is a wall (1)
    controller._on_move((0, -1))

    mock_audio.play_bump.assert_called_once()
    mock_audio.play_move.assert_not_called()
    mock_audio.play_push.assert_not_called()


def test_successful_push_calls_play_push_only(
    mock_audio: MagicMock, mock_level: Level
) -> None:
    """Verify that a successful box push plays push.wav only (no move.wav)."""
    # Create grid with a box directly in player's path
    # 1 1 1 1 1
    # 1 4 3 0 1
    # 1 1 1 1 1
    grid = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 0, 1],
            [1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    lvl = Level("PushLevel", grid)
    controller = GameController()
    controller.load_level_instance(lvl)

    # Move Right (1, 1) -> (1, 2) which is a box, pushing it to (1, 3)
    controller._on_move((0, 1))

    mock_audio.play_push.assert_called_once()
    mock_audio.play_move.assert_not_called()
    mock_audio.play_bump.assert_not_called()


def test_push_onto_target_plays_push_and_target(
    mock_audio: MagicMock, mock_level: Level
) -> None:
    """Verify that pushing a box onto a target triggers both push and target SFX."""
    # Create grid with a box adjacent to target
    # 1 1 1 1 1
    # 1 4 3 2 1
    # 1 1 1 1 1
    grid = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 2, 1],
            [1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    lvl = Level("TargetPushLevel", grid)
    controller = GameController()
    controller.load_level_instance(lvl)

    # Move Right (1, 1) -> (1, 2) pushing box onto target (1, 3)
    controller._on_move((0, 1))

    mock_audio.play_push.assert_called_once()
    mock_audio.play_target.assert_called_once()
    mock_audio.play_move.assert_not_called()


def test_undo_success_calls_play_undo(mock_audio: MagicMock, mock_level: Level) -> None:
    """Verify that a successful undo operation triggers undo.wav."""
    controller = GameController()
    controller.load_level_instance(mock_level)

    # Make a move first
    controller._on_move((1, 0))
    mock_audio.reset_mock()

    # Trigger undo
    controller._on_undo()

    mock_audio.play_undo.assert_called_once()


def test_redo_success_calls_play_redo(mock_audio: MagicMock, mock_level: Level) -> None:
    """Verify that a successful redo operation triggers redo.wav."""
    controller = GameController()
    controller.load_level_instance(mock_level)

    # Make a move and undo it
    controller._on_move((1, 0))
    controller._on_undo()
    mock_audio.reset_mock()

    # Trigger redo
    controller._on_redo()

    mock_audio.play_redo.assert_called_once()


def test_win_transition_calls_play_win_once(mock_audio: MagicMock) -> None:
    """Verify that winning a level triggers win.wav exactly once."""
    # Create simple level already 1 step away from victory
    grid = np.array(
        [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 2, 1],
            [1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    lvl = Level("WinLevel", grid)
    controller = GameController()
    controller.load_level_instance(lvl)

    # Move box to target -> completes level and transitions to WON
    controller._on_move((0, 1))

    # Assert win was played
    mock_audio.play_win.assert_called_once()
    # It should also play push and target chimes
    mock_audio.play_push.assert_called_once()
    mock_audio.play_target.assert_called_once()


def test_uninitialized_or_failed_audio_manager_does_not_crash(
    mock_level: Level,
) -> None:
    """Verify that GameController is safe if AudioManager fails to init.

    All controller operations must execute gracefully in silent fallback mode.
    """
    # Reset singleton state
    from src.pushbox.utils.audio import AudioManager

    AudioManager._instance = None

    # Force mixer initialization failure
    with patch("pygame.mixer.init", side_effect=pygame.error("Driver missing")):
        controller = GameController()
        controller.load_level_instance(mock_level)

        # Confirm audio manager is disabled/failed
        assert controller.audio.is_enabled() is False

        # Attempt gameplay operations - must complete smoothly without exceptions
        controller._on_move((1, 0))
        controller._on_undo()
        controller._on_redo()
        # All actions must execute gracefully in silent fallback mode
