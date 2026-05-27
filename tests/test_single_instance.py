"""Unit tests for SingleInstanceGuard."""

from unittest.mock import MagicMock, patch

import pytest

from src.pushbox.utils.single_instance import SingleInstanceGuard


def test_windows_first_instance_success() -> None:
    """Test that the first instance on Windows successfully acquires the mutex."""
    # Mock sys.platform to be win32
    with (
        patch("sys.platform", "win32"),
        patch("ctypes.windll.kernel32.CreateMutexW") as mock_create_mutex,
        patch("ctypes.windll.kernel32.GetLastError") as mock_get_last_error,
    ):
        mock_create_mutex.return_value = 12345  # Dummy valid handle
        mock_get_last_error.return_value = 0  # No error (first instance)

        guard = SingleInstanceGuard(app_id="TestApp")

        assert guard.already_running is False
        assert guard._mutex == 12345

        # Verify CreateMutexW call arguments
        mock_create_mutex.assert_called_once()
        args = mock_create_mutex.call_args[0]
        assert args[1] is True
        assert args[2] == "Local\\TestAppSingleInstanceMutex"


def test_windows_second_instance_blocks() -> None:
    """Test that subsequent instances on Windows detect the existing mutex."""
    with (
        patch("sys.platform", "win32"),
        patch("ctypes.windll.kernel32.CreateMutexW") as mock_create_mutex,
        patch("ctypes.windll.kernel32.GetLastError") as mock_get_last_error,
    ):
        mock_create_mutex.return_value = 12345
        mock_get_last_error.return_value = 183  # ERROR_ALREADY_EXISTS

        guard = SingleInstanceGuard(app_id="TestApp")

        assert guard.already_running is True


def test_windows_creation_fails_handles_gracefully() -> None:
    """Test that if CreateMutexW fails/returns NULL, it does not crash."""
    with (
        patch("sys.platform", "win32"),
        patch("ctypes.windll.kernel32.CreateMutexW") as mock_create_mutex,
        patch("ctypes.windll.kernel32.GetLastError") as mock_get_last_error,
    ):
        mock_create_mutex.return_value = 0  # NULL handle (failure)
        mock_get_last_error.return_value = 0

        # Should not raise exception
        guard = SingleInstanceGuard(app_id="TestApp")

        assert guard.already_running is False
        assert guard._mutex == 0


def test_windows_exception_handles_gracefully() -> None:
    """Test that if ctypes raises an exception, the app does not crash."""
    with (
        patch("sys.platform", "win32"),
        patch(
            "ctypes.windll.kernel32.CreateMutexW",
            side_effect=AttributeError("DLL error"),
        ),
    ):
        # Should catch exception and not raise it
        guard = SingleInstanceGuard(app_id="TestApp")

        assert guard.already_running is False


def test_windows_close_is_safe_and_reentrant() -> None:
    """Test that closing releases resources and is safe to call multiple times."""
    with (
        patch("sys.platform", "win32"),
        patch("ctypes.windll.kernel32.CreateMutexW") as mock_create_mutex,
        patch("ctypes.windll.kernel32.GetLastError") as mock_get_last_error,
        patch("ctypes.windll.kernel32.CloseHandle") as mock_close_handle,
    ):
        mock_create_mutex.return_value = 12345
        mock_get_last_error.return_value = 0
        mock_close_handle.return_value = True

        guard = SingleInstanceGuard(app_id="TestApp")

        # First close call
        guard.close()
        mock_close_handle.assert_called_once_with(12345)
        assert guard._mutex is None

        # Second close call should not call CloseHandle again
        guard.close()
        assert mock_close_handle.call_count == 1


def test_unix_first_instance_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that flock lockfile works on non-Windows platforms."""
    # Ensure platform is NOT win32
    monkeypatch.setattr("sys.platform", "linux")

    mock_open = MagicMock()
    mock_fcntl = MagicMock()

    with (
        patch("builtins.open", mock_open),
        patch.dict("sys.modules", {"fcntl": mock_fcntl}),
        patch("os.path.exists", return_value=True),
        patch("os.unlink") as mock_unlink,
    ):
        guard = SingleInstanceGuard(app_id="TestApp")

        assert guard.already_running is False
        assert guard._lock_file is not None

        # Save reference before close sets it to None
        lock_file_ref = guard._lock_file

        # Close should release the flock and delete file
        guard.close()
        mock_fcntl.flock.assert_any_call(lock_file_ref, mock_fcntl.LOCK_UN)
        mock_unlink.assert_called_once_with(guard._lock_path)


def test_unix_second_instance_blocks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that a second instance on Unix blocks if flock raises IOError."""
    monkeypatch.setattr("sys.platform", "linux")

    mock_open = MagicMock()
    mock_fcntl = MagicMock()
    # Simulate locked file (raises BlockingIOError/OSError)
    mock_fcntl.flock.side_effect = BlockingIOError("Resource temporarily unavailable")

    with (
        patch("builtins.open", mock_open),
        patch.dict("sys.modules", {"fcntl": mock_fcntl}),
    ):
        guard = SingleInstanceGuard(app_id="TestApp")

        assert guard.already_running is True


def test_unix_missing_fcntl_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that Unix fallback works gracefully if fcntl is missing."""
    monkeypatch.setattr("sys.platform", "linux")

    # Simulate missing fcntl package
    with patch.dict("sys.modules", {"fcntl": None}, clear=True):
        guard = SingleInstanceGuard(app_id="TestApp")
        assert guard.already_running is False


def test_context_manager_usage() -> None:
    """Test that context manager enters and exits safely."""
    with (
        patch("sys.platform", "win32"),
        patch("ctypes.windll.kernel32.CreateMutexW") as mock_create_mutex,
        patch("ctypes.windll.kernel32.GetLastError") as mock_get_last_error,
        patch("ctypes.windll.kernel32.CloseHandle") as mock_close_handle,
    ):
        mock_create_mutex.return_value = 12345
        mock_get_last_error.return_value = 0
        mock_close_handle.return_value = True

        with SingleInstanceGuard(app_id="TestApp") as guard:
            assert guard.already_running is False

        mock_close_handle.assert_called_once_with(12345)
