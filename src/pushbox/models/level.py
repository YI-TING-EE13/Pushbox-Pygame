"""Level data model."""

import json
from pathlib import Path
from typing import Any, Optional

import numpy as np

from ..utils.constants import DEFAULT_LEVELS, CellType


class Level:
    """Represents a game level."""

    def __init__(self, name: str, grid: list[list[int]]) -> None:
        """Initialize a level.

        Args:
            name: Level name.
            grid: 2D grid representing the level.
        """
        self.name = name
        self.initial_grid = np.array(grid)
        self.grid = np.array(grid)
        rows, cols = self.grid.shape
        self.rows = int(rows)
        self.cols = int(cols)

    def reset(self) -> None:
        """Reset level to initial state."""
        self.grid = np.array(self.initial_grid)

    def get_player_position(self) -> Optional[tuple[int, int]]:
        """Find player position.

        Returns:
            Player position (row, col) or None if not found.
        """
        positions = np.where(self.grid == CellType.PLAYER)
        if len(positions[0]) > 0:
            return (int(positions[0][0]), int(positions[1][0]))
        return None

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within grid bounds.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            True if position is valid.
        """
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_cell(self, row: int, col: int) -> int:
        """Get cell value at position.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            Cell value.
        """
        if self.is_valid_position(row, col):
            return int(self.grid[row, col])
        return CellType.WALL

    def set_cell(self, row: int, col: int, value: int) -> None:
        """Set cell value at position.

        Args:
            row: Row index.
            col: Column index.
            value: Cell value to set.
        """
        if self.is_valid_position(row, col):
            self.grid[row, col] = value

    def is_complete(self) -> bool:
        """Check if level is complete (all boxes on targets).

        Returns:
            True if level is complete.
        """
        return bool(CellType.BOX not in self.grid)

    def is_deadlocked(self) -> bool:
        """Check if level is in deadlock (box stuck in corner).

        Returns:
            True if deadlock detected.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row, col] == CellType.BOX:
                    # Check if box is stuck in corner
                    up = self.get_cell(row - 1, col) == CellType.WALL
                    down = self.get_cell(row + 1, col) == CellType.WALL
                    left = self.get_cell(row, col - 1) == CellType.WALL
                    right = self.get_cell(row, col + 1) == CellType.WALL

                    # Box is stuck if blocked on both vertical and horizontal
                    if (up or down) and (left or right):
                        return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert level to dictionary.

        Returns:
            Dictionary representation of level.
        """
        return {"name": self.name, "grid": self.initial_grid.tolist()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Level":
        """Create level from dictionary.

        Args:
            data: Dictionary with level data.

        Returns:
            Level instance.
        """
        return cls(data["name"], data["grid"])


class LevelManager:
    """Manages all game levels."""

    def __init__(self, levels_dir: Optional[str] = None) -> None:
        """Initialize level manager.

        Args:
            levels_dir: Directory containing level files.
        """
        from ..utils.paths import get_app_data_path

        if levels_dir is None:
            self.levels_dir = get_app_data_path("levels")
        else:
            self.levels_dir = Path(levels_dir)
        self.levels: dict[str, Level] = {}
        self._load_default_levels()
        self._load_custom_levels()

    def _load_default_levels(self) -> None:
        """Load default built-in levels."""
        # Load Onboarding Level 0 (5x7)
        level_0_grid = [
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 4, 0, 0, 3, 2, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1],
        ]
        self.levels["Level 0"] = Level("Level 0", level_0_grid)

        for name, grid in DEFAULT_LEVELS.items():
            self.levels[name] = Level(name, grid)

    def _load_custom_levels(self) -> None:
        """Load custom levels from files."""
        import sys

        if not self.levels_dir.exists():
            return

        for level_file in self.levels_dir.glob("*.json"):
            try:
                with open(level_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Pre-validation checks to protect against early crashes
                if not isinstance(data, dict):
                    raise ValueError("Loaded JSON is not a dictionary.")
                if "name" not in data or "grid" not in data:
                    raise KeyError("Missing required keys 'name' or 'grid'.")

                name = data["name"]
                grid = data["grid"]

                if not isinstance(name, str):
                    raise TypeError("Level name must be a string.")
                if not isinstance(grid, list) or not grid:
                    raise TypeError("Level grid must be a non-empty list of lists.")

                rows = len(grid)
                if rows == 0:
                    raise ValueError("Level grid has 0 rows.")

                # Check list of lists and rectangularity
                if not isinstance(grid[0], list):
                    raise TypeError("Level grid must be a list of lists.")
                cols = len(grid[0])
                if cols == 0:
                    raise ValueError("Level grid rows cannot be empty.")

                for r_idx, row in enumerate(grid):
                    if not isinstance(row, list):
                        raise TypeError(f"Row {r_idx} in level grid is not a list.")
                    if len(row) != cols:
                        raise ValueError("Level grid must be rectangular.")
                    for c_idx, cell in enumerate(row):
                        if not isinstance(cell, int) or cell < 0 or cell > 4:
                            raise ValueError(
                                f"Invalid cell value {cell} at "
                                f"row {r_idx}, col {c_idx}. "
                                "Must be between 0 and 4."
                            )

                # Unpacking safety
                level = Level.from_dict(data)
                # Verify unpacking shape
                if level.rows != rows or level.cols != cols:
                    raise ValueError("Level grid shape unpacking mismatch.")

                self.levels[level.name] = level

            except Exception as e:
                # Output details to stderr as requested
                err_type = type(e).__name__
                print(
                    f"Warning: Could not load custom level from {level_file.name} "
                    f"[{err_type}]: {e}",
                    file=sys.stderr,
                )

    def get_level(self, name: str) -> Optional[Level]:
        """Get a level by name.

        Args:
            name: Level name.

        Returns:
            Level instance or None.
        """
        return self.levels.get(name)

    def get_level_names(self) -> list[str]:
        """Get list of all level names.

        Returns:
            List of level names.
        """
        return [name for name in self.levels.keys() if name != "Level 0"]

    def save_level(self, level: Level) -> None:
        """Save a custom level.

        Args:
            level: Level to save.
        """
        self.levels_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_name = "".join(
            c for c in level.name if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_name = safe_name.replace(" ", "_")

        filepath = self.levels_dir / f"{safe_name}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(level.to_dict(), f, indent=2, ensure_ascii=False)

        self.levels[level.name] = level

    def delete_level(self, name: str) -> bool:
        """Delete a custom level.

        Args:
            name: Level name to delete.

        Returns:
            True if deleted successfully.
        """
        if name in DEFAULT_LEVELS:
            return False  # Cannot delete default levels

        if name in self.levels:
            del self.levels[name]

            # Try to delete file
            safe_name = "".join(
                c for c in name if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            safe_name = safe_name.replace(" ", "_")
            filepath = self.levels_dir / f"{safe_name}.json"

            if filepath.exists():
                filepath.unlink()
            return True

        return False
