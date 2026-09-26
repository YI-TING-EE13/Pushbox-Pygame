"""Level data model."""

import json
from contextlib import suppress
from pathlib import Path
from typing import Any, Optional
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import numpy as np

from ..utils.constants import DEFAULT_LEVELS, CellType


class LevelPersistenceError(Exception):
    """Raised when a level could not be persisted without losing consistency."""


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

    @staticmethod
    def _validate_grid_values(grid: np.ndarray, *, allow_box_on_target: bool) -> None:
        """Validate grid shape and cell representation without checking counts."""
        if grid.ndim != 2 or grid.shape[0] == 0 or grid.shape[1] == 0:
            raise ValueError("Level grid must be a non-empty rectangular grid.")
        if not np.issubdtype(grid.dtype, np.integer):
            raise ValueError("Level grid cells must be integers.")

        maximum_cell = (
            CellType.BOX_ON_TARGET if allow_box_on_target else CellType.PLAYER
        )
        if np.any(grid < CellType.EMPTY) or np.any(grid > maximum_cell):
            raise ValueError("Level grid contains an invalid cell value.")

    def validate_structure(self) -> None:
        """Validate the level's starting and current grids against Sokoban rules.

        Raises:
            ValueError: If either grid is malformed or has invalid player, box, or
                goal counts.
        """
        self._validate_grid_values(self.initial_grid, allow_box_on_target=False)
        self._validate_grid_values(self.grid, allow_box_on_target=True)
        if self.grid.shape != self.initial_grid.shape:
            raise ValueError(
                "Runtime level grid shape does not match its initial grid."
            )

        initial_players = int(np.count_nonzero(self.initial_grid == CellType.PLAYER))
        initial_boxes = int(np.count_nonzero(self.initial_grid == CellType.BOX))
        goal_count = int(np.count_nonzero(self.initial_grid == CellType.TARGET))
        if initial_players != 1:
            raise ValueError("A level must contain exactly one player.")
        if goal_count == 0:
            raise ValueError("A level must contain at least one goal.")
        if initial_boxes != goal_count:
            raise ValueError(
                "Custom levels need matching, non-zero box and target counts."
            )

        current_players = int(np.count_nonzero(self.grid == CellType.PLAYER))
        current_boxes = int(
            np.count_nonzero(np.isin(self.grid, [CellType.BOX, CellType.BOX_ON_TARGET]))
        )
        if current_players != 1:
            raise ValueError("A runtime level must contain exactly one player.")
        if current_boxes != goal_count:
            raise ValueError("Runtime box count must match the number of goals.")

    def is_complete(self) -> bool:
        """Check if level is complete (all boxes on targets).

        Returns:
            True if level is complete.
        """
        try:
            self.validate_structure()
        except (AttributeError, TypeError, ValueError):
            return False

        target_positions = zip(*np.where(self.initial_grid == CellType.TARGET))
        return all(
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

        candidates: list[Level] = []
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
                raw_id = data.get("id")
                try:
                    level_id = UUID(raw_id).hex if isinstance(raw_id, str) else None
                except ValueError:
                    level_id = None
                if level_id is None:
                    level_id = uuid5(NAMESPACE_URL, level_file.name.casefold()).hex

                level = Level(
                    name,
                    grid,
                    level_id=level_id,
                    source="custom",
                    storage_path=level_file,
                )
                level.validate_structure()
                candidates.append(level)

            except Exception as e:
                # Output details to stderr as requested
                err_type = type(e).__name__
                print(
                    f"Warning: Could not load custom level from {level_file.name} "
                    f"[{err_type}]: {e}",
                    file=sys.stderr,
                )

        # A migration can be interrupted after the canonical file is written but
        # before its legacy source is removed. Keep one deterministic record per ID.
        selected_by_id: dict[str, Level] = {}
        for candidate in candidates:
            candidate_id = candidate.level_id
            if candidate_id is None:
                continue
            current = selected_by_id.get(candidate_id)
            if current is None:
                selected_by_id[candidate_id] = candidate
                continue

            candidate_path = candidate.storage_path
            current_path = current.storage_path
            candidate_is_canonical = (
                candidate_path is not None
                and candidate_path.stem.casefold() == candidate_id.casefold()
            )
            current_is_canonical = (
                current_path is not None
                and current_path.stem.casefold() == candidate_id.casefold()
            )
            if candidate_is_canonical and not current_is_canonical:
                selected_by_id[candidate_id] = candidate
            elif candidate_is_canonical == current_is_canonical:
                candidate_key = candidate_path.name.casefold() if candidate_path else ""
                current_key = current_path.name.casefold() if current_path else ""
                if candidate_key < current_key:
                    selected_by_id[candidate_id] = candidate

        builtin_names = {"level 0"}
        builtin_names.update(name.casefold() for name in DEFAULT_LEVELS)
        used_names = set(builtin_names)
        for level in sorted(
            selected_by_id.values(),
            key=lambda item: (
                item.storage_path.name.casefold() if item.storage_path else ""
            ),
        ):
            display_name = level.name.strip()
            if display_name.casefold() in builtin_names:
                display_name = f"{display_name} (Custom)"
            suffix = 2
            base_name = display_name
            while display_name.casefold() in used_names:
                display_name = f"{base_name} ({suffix})"
                suffix += 1
            level.name = display_name
            self.levels[level.name] = level
            used_names.add(level.name.casefold())

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
        level.validate_structure()
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

        previous_name = None
        level_id = level.level_id
        storage_path = level.storage_path
        if level.level_id is not None:
            for name, existing in self.levels.items():
                if existing.source == "custom" and existing.level_id == level.level_id:
                    previous_name = name
                    if storage_path is None:
                        storage_path = existing.storage_path
                    break

        normalized_name = display_name.casefold()
        for existing_name in self.levels:
            if existing_name == previous_name:
                continue
            if existing_name.casefold() == normalized_name:
                raise ValueError("A level with this name already exists.")

        if level_id is None:
            level_id = uuid4().hex

        try:
            self.levels_dir.mkdir(parents=True, exist_ok=True)
            destination = self.levels_dir / f"{level_id}.json"
            source_path = storage_path
            if source_path is not None:
                source_path = source_path.resolve()
            resolved_destination = destination.resolve()

            if destination.exists() and source_path != resolved_destination:
                # Do not overwrite a file not loaded as this level.
                while destination.exists():
                    level_id = uuid4().hex
                    destination = self.levels_dir / f"{level_id}.json"
                resolved_destination = destination.resolve()

            is_legacy_migration = (
                source_path is not None
                and source_path != resolved_destination
                and source_path.parent == self.levels_dir.resolve()
                and source_path.exists()
            )
        except OSError as exc:
            raise LevelPersistenceError("The level could not be saved.") from exc

        destination_created = False
        data = level.to_dict()
        data["name"] = display_name
        data["id"] = level_id
        data["source"] = "custom"
        temporary = self.levels_dir / f".{uuid4().hex}.tmp"
        try:
            with temporary.open("x", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if destination.exists() and source_path == resolved_destination:
                temporary.replace(destination)
            else:
                temporary.rename(destination)
                destination_created = True

            if is_legacy_migration and source_path is not None:
                source_path.unlink()
        except OSError as exc:
            if (
                destination_created
                and is_legacy_migration
                and source_path is not None
                and source_path.exists()
            ):
                try:
                    destination.unlink()
                except OSError as rollback_error:
                    raise LevelPersistenceError(
                        "Level migration failed and its rollback was incomplete."
                    ) from rollback_error
            raise LevelPersistenceError("The level could not be saved.") from exc
        finally:
            if temporary.exists():
                with suppress(OSError):
                    temporary.unlink()

        if previous_name is not None and previous_name != display_name:
            del self.levels[previous_name]
        level.name = display_name
        level.source = "custom"
        level.level_id = level_id
        level.storage_path = destination
        self.levels[display_name] = level

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
