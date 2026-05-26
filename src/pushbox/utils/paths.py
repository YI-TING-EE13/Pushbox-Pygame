"""Path resolution utilities for development and packaged environments."""

import sys
from pathlib import Path
from typing import Union


def is_frozen() -> bool:
    """Check if the application is running in a PyInstaller frozen environment."""
    return getattr(sys, "frozen", False)


def get_project_root() -> Path:
    """Get the absolute path to the project root directory (repository root).

    Since paths.py is located at src/pushbox/utils/paths.py, the project root
    is 4 levels up: parent.parent.parent.parent.
    """
    return Path(__file__).parent.parent.parent.parent.resolve()


def get_bundle_root() -> Path:
    """Get the root directory containing read-only bundled assets.

    - In frozen environment: returns sys._MEIPASS.
    - In development environment: returns project_root / "src" / "pushbox".
    """
    if is_frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    # dev environment: project_root / src / pushbox
    return Path(__file__).parent.parent.resolve()


def get_resource_path(relative_path: Union[str, Path]) -> Path:
    """Get the absolute path to a read-only bundled resource file.

    Maps to get_bundle_root() / relative_path.
    """
    return get_bundle_root() / relative_path


def get_app_base_path() -> Path:
    """Get the base directory for writing runtime app data.

    - In frozen environment: returns the parent directory of the .exe executable.
    - In development environment: returns the project repository root.
    """
    if is_frozen():
        return Path(sys.executable).parent.resolve()
    return get_project_root()


def get_app_data_path(relative_path: Union[str, Path]) -> Path:
    """Get the absolute path to a writable runtime data file/dir.

    Maps to get_app_base_path() / relative_path.
    """
    return get_app_base_path() / relative_path


def ensure_runtime_dirs() -> None:
    """Ensure necessary writable runtime directories exist on the disk.

    Creates 'data/' and 'levels/' directories inside the active
    get_app_base_path() folder.
    """
    get_app_data_path("data").mkdir(parents=True, exist_ok=True)
    get_app_data_path("levels").mkdir(parents=True, exist_ok=True)
