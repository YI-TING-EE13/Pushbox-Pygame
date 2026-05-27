"""Unit tests for the defensive AudioManager."""

from unittest.mock import MagicMock, patch

import pygame
import pytest

from src.pushbox.utils.audio import AudioManager


@pytest.fixture(autouse=True)
def reset_audio_singleton() -> None:
    """Reset the AudioManager singleton instance before and after each test."""
    AudioManager._instance = None
    yield
    AudioManager._instance = None


def test_audio_manager_singleton() -> None:
    """Verify that AudioManager implements the Singleton pattern."""
    audio1 = AudioManager()
    audio2 = AudioManager()
    assert audio1 is audio2


def test_mixer_init_success() -> None:
    """Test successful initialization of the pygame mixer."""
    with (
        patch("pygame.mixer.init") as mock_init,
        patch("pygame.mixer.Sound") as mock_sound_class,
        patch("pathlib.Path.exists", return_value=True),
    ):
        audio = AudioManager()
        result = audio.initialize()

        assert result is True
        assert audio._initialized is True
        mock_init.assert_called_once()
        # Verify it attempted to load all 8 sounds
        assert mock_sound_class.call_count == 8


def test_mixer_init_failure() -> None:
    """Test that mixer init failure is caught safely without crashes.

    Should transition directly to a silent fallback mode.
    """
    with patch(
        "pygame.mixer.init", side_effect=pygame.error("No sound card driver found")
    ) as mock_init:
        audio = AudioManager()
        result = audio.initialize()

        assert result is False
        assert audio._initialized is False
        assert audio.is_enabled() is False
        mock_init.assert_called_once()


def test_missing_assets() -> None:
    """Test that missing audio assets do not cause crashes during init.

    Should gracefully bypass loading of any non-existent files.
    """
    with (
        patch("pygame.mixer.init") as mock_init,
        patch("pygame.mixer.Sound") as mock_sound_class,
        patch("pathlib.Path.exists", return_value=False),
    ):
        audio = AudioManager()
        result = audio.initialize()

        assert result is True
        assert audio._initialized is True
        assert len(audio._sounds) == 0
        mock_init.assert_called_once()
        mock_sound_class.assert_not_called()


def test_unknown_sound_key() -> None:
    """Test that requesting an unknown sound key is handled safely without crashes."""
    audio = AudioManager()
    # Initialize in silent/uninitialized mode
    audio.play_sound("invalid_nonexistent_key")
    # No exception raised


def test_disabled_audio() -> None:
    """Test that disabled audio prevents sounds from being played."""
    mock_sound = MagicMock()
    audio = AudioManager()
    audio._initialized = True
    audio._sounds["move"] = mock_sound

    # When enabled, it should play
    audio.set_enabled(True)
    audio.play_move()
    mock_sound.play.assert_called_once()

    # When disabled, it should not play
    mock_sound.reset_mock()
    audio.set_enabled(False)
    audio.play_move()
    mock_sound.play.assert_not_called()


def test_volume_clamping() -> None:
    """Test that sound and music volumes are correctly clamped between 0.0 and 1.0."""
    audio = AudioManager()

    # Clamp low values to 0.0
    audio.set_sound_volume(-0.5)
    assert audio._sound_volume == 0.0

    audio.set_music_volume(-1.2)
    assert audio._music_volume == 0.0

    # Clamp high values to 1.0
    audio.set_sound_volume(1.5)
    assert audio._sound_volume == 1.0

    audio.set_music_volume(3.0)
    assert audio._music_volume == 1.0

    # Valid values are set normally
    audio.set_sound_volume(0.7)
    assert audio._sound_volume == 0.7

    audio.set_music_volume(0.45)
    assert audio._music_volume == 0.45


def test_volume_updates_applied_to_cached_sounds() -> None:
    """Test that setting volume updates all preloaded Sound volumes.

    Verifies volume changes dynamically affect already loaded cached buffers.
    """
    mock_sound1 = MagicMock()
    mock_sound2 = MagicMock()

    audio = AudioManager()
    audio._sounds["move"] = mock_sound1
    audio._sounds["push"] = mock_sound2

    audio.set_sound_volume(0.85)
    assert audio._sound_volume == 0.85
    mock_sound1.set_volume.assert_called_once_with(0.85)
    mock_sound2.set_volume.assert_called_once_with(0.85)


def test_sound_play_exception_caught() -> None:
    """Test that any exceptions raised during Sound.play are caught safely."""
    mock_sound = MagicMock()
    mock_sound.play.side_effect = pygame.error("Sound channel allocation failed")

    audio = AudioManager()
    audio._initialized = True
    audio.set_enabled(True)
    audio._sounds["win"] = mock_sound

    # Should catch exception internally and not raise/crash
    audio.play_win()
    mock_sound.play.assert_called_once()


def test_all_shortcut_methods_map_correctly() -> None:
    """Test that all SFX shortcut helper methods route to play_sound correctly."""
    audio = AudioManager()
    with patch.object(audio, "play_sound") as mock_play:
        audio.play_move()
        mock_play.assert_called_with("move")

        audio.play_push()
        mock_play.assert_called_with("push")

        audio.play_bump()
        mock_play.assert_called_with("bump")

        audio.play_target()
        mock_play.assert_called_with("target")

        audio.play_undo()
        mock_play.assert_called_with("undo")

        audio.play_redo()
        mock_play.assert_called_with("redo")

        audio.play_win()
        mock_play.assert_called_with("win")

        audio.play_click()
        mock_play.assert_called_with("click")
