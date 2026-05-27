"""Enforce a single running instance of the application."""

import os
import sys
import tempfile
import traceback
from typing import Any, Optional

ERROR_ALREADY_EXISTS = 183


class SingleInstanceGuard:
    """Guard to prevent multiple instances of the application from running concurrently.

    Uses a Win32 named mutex on Windows, and fcntl lockfiles on Unix-like platforms.
    """

    def __init__(self, app_id: str = "PushboxPygame") -> None:
        """Initialize and acquire the single-instance guard.

        Args:
            app_id: A unique identifier for the application.
        """
        self.app_id = app_id
        self._already_running = False
        self._mutex: Optional[int] = None
        self._lock_file: Optional[Any] = None
        self._lock_path: Optional[str] = None

        if sys.platform == "win32":
            self._acquire_windows()
        else:
            self._acquire_unix()

    def _acquire_windows(self) -> None:
        """Acquire a Win32 named mutex using ctypes."""
        try:
            import ctypes

            # Use Local\ namespace as requested by user to avoid
            # permission/session errors
            mutex_name = f"Local\\{self.app_id}SingleInstanceMutex"

            # Setup CreateMutexW function prototype
            create_mutex_w = ctypes.windll.kernel32.CreateMutexW
            create_mutex_w.argtypes = [
                ctypes.c_void_p,
                ctypes.c_bool,
                ctypes.c_wchar_p,
            ]
            create_mutex_w.restype = ctypes.c_void_p

            # Setup GetLastError prototype
            get_last_error = ctypes.windll.kernel32.GetLastError
            get_last_error.argtypes = []
            get_last_error.restype = ctypes.c_uint32

            # Attempt to create/acquire named mutex
            self._mutex = create_mutex_w(None, True, mutex_name)

            if not self._mutex:
                # Fallback: if CreateMutexW returns NULL/0, log warning but do not crash
                print("Warning: CreateMutexW returned NULL.", file=sys.stderr)
                return

            last_error = get_last_error()
            if last_error == ERROR_ALREADY_EXISTS:
                self._already_running = True

        except Exception as e:
            # Under any ctypes exception, print warning in source/debug mode
            # but do not block startup
            print(
                f"Warning: SingleInstanceGuard exception on Windows: {e}",
                file=sys.stderr,
            )
            traceback.print_exc()

    def _acquire_unix(self) -> None:
        """Acquire a tempfile-based flock on Unix/Linux/macOS platforms."""
        try:
            self._lock_path = os.path.join(
                tempfile.gettempdir(), f"{self.app_id.lower()}_single.lock"
            )
            import fcntl

            self._lock_file = open(self._lock_path, "w")
            # Try to acquire non-blocking exclusive lock
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[attr-defined]
        except OSError:
            # Lock is already held by another process
            self._already_running = True
        except ImportError:
            # fcntl is not available, fallback silently to no-op
            pass
        except Exception as e:
            print(
                f"Warning: SingleInstanceGuard exception on Unix: {e}", file=sys.stderr
            )

    @property
    def already_running(self) -> bool:
        """Check if another instance is already running."""
        return self._already_running

    def close(self) -> None:
        """Release the acquired named mutex or lockfile."""
        if sys.platform == "win32":
            if self._mutex:
                try:
                    import ctypes

                    close_handle = ctypes.windll.kernel32.CloseHandle
                    close_handle.argtypes = [ctypes.c_void_p]
                    close_handle.restype = ctypes.c_bool
                    close_handle(self._mutex)
                except Exception:
                    pass
                self._mutex = None
        else:
            if self._lock_file:
                try:
                    import fcntl

                    fcntl.flock(self._lock_file, fcntl.LOCK_UN)  # type: ignore[attr-defined]
                    self._lock_file.close()
                except Exception:
                    pass
                self._lock_file = None

            if self._lock_path and os.path.exists(self._lock_path):
                try:
                    os.unlink(self._lock_path)
                except Exception:
                    pass

    def __enter__(self) -> "SingleInstanceGuard":
        """Support for context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Support for context manager."""
        self.close()
