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

    def __init__(self, levels_dir: str = "levels") -> None:
        """Initialize level manager.

        Args:
            levels_dir: Directory containing level files.
        """
        self.levels_dir = Path(levels_dir)
        self.levels: dict[str, Level] = {}
        self._load_default_levels()
        self._load_custom_levels()

    def _load_default_levels(self) -> None:
        """Load default built-in levels."""
        for name, grid in DEFAULT_LEVELS.items():
            self.levels[name] = Level(name, grid)

    def _load_custom_levels(self) -> None:
        """Load custom levels from files."""
        if not self.levels_dir.exists():
            return

        for level_file in self.levels_dir.glob("*.json"):
            try:
                with open(level_file, encoding="utf-8") as f:
                    data = json.load(f)
                    level = Level.from_dict(data)
                    self.levels[level.name] = level
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load level {level_file}: {e}")

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
        return list(self.levels.keys())

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
