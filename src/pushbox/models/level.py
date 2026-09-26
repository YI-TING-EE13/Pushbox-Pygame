"""Level data model."""

import json
from pathlib import Path
from typing import Any, Optional
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import numpy as np

from ..utils.constants import DEFAULT_LEVELS, CellType


class Level:
    """Represents a game level."""

    def __init__(
        self,
        name: str,
        grid: list[list[int]],
        level_id: Optional[str] = None,
        source: str = "custom",
        storage_path: Optional[Path] = None,
    ) -> None:
        """Initialize a level.

        Args:
            name: Level name.
            grid: 2D grid representing the level.
        """
        self.name = name
        self.level_id = level_id
        self.source = source
        self.storage_path = storage_path
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
        if self.grid.shape != self.initial_grid.shape:
            return False

        target_mask = np.isin(
            self.initial_grid, [CellType.TARGET, CellType.BOX_ON_TARGET]
        )
        target_positions = list(zip(*np.where(target_mask)))
        box_count = int(
            np.count_nonzero(np.isin(self.grid, [CellType.BOX, CellType.BOX_ON_TARGET]))
        )
        if not target_positions:
            return box_count == 0

        return box_count == len(target_positions) and all(
            self.grid[row, col] == CellType.BOX_ON_TARGET
            for row, col in target_positions
        )

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
        data = {
            "name": self.name,
            "grid": self.initial_grid.tolist(),
            "source": self.source,
        }
        if self.level_id is not None:
            data["id"] = self.level_id
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Level":
        """Create level from dictionary.

        Args:
            data: Dictionary with level data.

        Returns:
            Level instance.
        """
        level_id = data.get("id")
        source = data.get("source", "custom")
        return cls(
            data["name"],
            data["grid"],
            level_id=level_id if isinstance(level_id, str) else None,
            source=source if source in ("builtin", "custom") else "custom",
        )


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
        self.levels["Level 0"] = Level("Level 0", level_0_grid, source="builtin")

        for name, grid in DEFAULT_LEVELS.items():
            self.levels[name] = Level(name, grid, source="builtin")

    def _load_custom_levels(self) -> None:
        """Load custom levels from files."""
        import sys

        if not self.levels_dir.exists():
            return

        builtin_names = {"level 0"}
        builtin_names.update(name.casefold() for name in DEFAULT_LEVELS)
        used_names = set(builtin_names)

        for level_file in sorted(
            self.levels_dir.glob("*.json"), key=lambda path: path.name.casefold()
        ):
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
                name = name.strip()
                if not name:
                    raise ValueError("Level name cannot be empty.")
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

                player_count = 0
                box_count = 0
                target_count = 0
                for r_idx, row in enumerate(grid):
                    if not isinstance(row, list):
                        raise TypeError(f"Row {r_idx} in level grid is not a list.")
                    if len(row) != cols:
                        raise ValueError("Level grid must be rectangular.")
                    for c_idx, cell in enumerate(row):
                        if (
                            not isinstance(cell, int)
                            or isinstance(cell, bool)
                            or cell < 0
                            or cell > 4
                        ):
                            raise ValueError(
                                f"Invalid cell value {cell} at "
                                f"row {r_idx}, col {c_idx}. "
                                "Must be between 0 and 4."
                            )
                        player_count += cell == CellType.PLAYER
                        box_count += cell == CellType.BOX
                        target_count += cell == CellType.TARGET

                if player_count != 1:
                    raise ValueError("Custom levels must contain exactly one player.")
                if box_count < 1 or box_count != target_count:
                    raise ValueError(
                        "Custom levels need matching, non-zero box and target counts."
                    )

                raw_id = data.get("id")
                try:
                    level_id = UUID(raw_id).hex if isinstance(raw_id, str) else None
                except ValueError:
                    level_id = None
                if level_id is None:
                    level_id = uuid5(NAMESPACE_URL, level_file.name.casefold()).hex

                if any(
                    existing.level_id == level_id
                    for existing in self.levels.values()
                    if existing.source == "custom"
                ):
                    level_id = uuid5(
                        NAMESPACE_URL, f"duplicate:{level_file.name.casefold()}"
                    ).hex

                display_name = name
                if display_name.casefold() in builtin_names:
                    display_name = f"{name} (Custom)"
                suffix = 2
                base_name = display_name
                while display_name.casefold() in used_names:
                    display_name = f"{base_name} ({suffix})"
                    suffix += 1

                # Built-in levels have a separate, immutable source identity.
                level = Level(
                    display_name,
                    grid,
                    level_id=level_id,
                    source="custom",
                    storage_path=level_file,
                )
                # Verify unpacking shape
                if level.rows != rows or level.cols != cols:
                    raise ValueError("Level grid shape unpacking mismatch.")

                self.levels[level.name] = level
                used_names.add(level.name.casefold())

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
        return [
            name
            for name, level in self.levels.items()
            if not (level.source == "builtin" and name == "Level 0")
        ]

    def get_campaign_level_names(self) -> list[str]:
        """Return the built-in campaign levels, excluding the onboarding level."""
        return [
            name
            for name, level in self.levels.items()
            if level.source == "builtin" and name != "Level 0"
        ]

    def save_level(self, level: Level) -> None:
        """Save a custom level.

        Args:
            level: Level to save.
        """
        display_name = level.name.strip()
        if not display_name:
            raise ValueError("Custom level name cannot be empty.")

        reserved_names = {name.casefold() for name in DEFAULT_LEVELS}
        reserved_names.add("level 0")
        if display_name.casefold() in reserved_names:
            raise ValueError("Custom levels cannot use built-in level names.")

        same_name = self.levels.get(display_name)
        if same_name is not None and same_name.source == "builtin":
            raise ValueError("Custom levels cannot replace built-in levels.")
        if level.level_id is None and same_name is not None:
            level.level_id = same_name.level_id
            level.storage_path = same_name.storage_path

        previous_name = None
        if level.level_id is not None:
            for name, existing in self.levels.items():
                if existing.source == "custom" and existing.level_id == level.level_id:
                    previous_name = name
                    if level.storage_path is None:
                        level.storage_path = existing.storage_path
                    break

        normalized_name = display_name.casefold()
        for existing_name in self.levels:
            if existing_name == previous_name:
                continue
            if existing_name.casefold() == normalized_name:
                raise ValueError("A level with this name already exists.")

        level.name = display_name
        level.source = "custom"
        if level.level_id is None:
            level.level_id = uuid4().hex

        self.levels_dir.mkdir(parents=True, exist_ok=True)
        destination = self.levels_dir / f"{level.level_id}.json"
        source_path = level.storage_path
        if source_path is not None:
            source_path = source_path.resolve()
        resolved_destination = destination.resolve()

        if destination.exists() and source_path != resolved_destination:
            # Do not overwrite a file that this manager did not load as this level.
            while destination.exists():
                level.level_id = uuid4().hex
                destination = self.levels_dir / f"{level.level_id}.json"
            resolved_destination = destination.resolve()

        data = level.to_dict()
        data["id"] = level.level_id
        data["source"] = "custom"
        temporary = self.levels_dir / f".{uuid4().hex}.tmp"
        try:
            with temporary.open("x", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if destination.exists() and source_path == resolved_destination:
                temporary.replace(destination)
            else:
                temporary.rename(destination)
        finally:
            if temporary.exists():
                temporary.unlink()

        if (
            source_path is not None
            and source_path != resolved_destination
            and source_path.parent == self.levels_dir.resolve()
            and source_path.exists()
        ):
            source_path.unlink()

        if previous_name is not None and previous_name != level.name:
            del self.levels[previous_name]
        level.storage_path = destination
        self.levels[level.name] = level

    def delete_level(self, name: str) -> bool:
        """Delete a custom level.

        Args:
            name: Level name to delete.

        Returns:
            True if deleted successfully.
        """
        level = self.levels.get(name)
        if level is None or level.source == "builtin":
            return False

        if level.storage_path is not None and level.storage_path.exists():
            storage_path = level.storage_path.resolve()
            if storage_path.parent == self.levels_dir.resolve():
                storage_path.unlink()
        del self.levels[name]
        return True
