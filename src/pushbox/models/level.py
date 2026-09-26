"""Level data model."""

import json
from contextlib import suppress
from pathlib import Path
from typing import Any, Optional, cast
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

    @staticmethod
    def _validate_serialized_grid(raw_grid: Any) -> list[list[int]]:
        """Validate raw JSON grid values before NumPy can coerce their types."""
        if not isinstance(raw_grid, list) or not raw_grid:
            raise TypeError("Level grid must be a non-empty list of lists.")
        if not isinstance(raw_grid[0], list):
            raise TypeError("Level grid must be a list of lists.")

        column_count = len(raw_grid[0])
        if column_count == 0:
            raise ValueError("Level grid rows cannot be empty.")

        minimum_cell = int(CellType.EMPTY)
        maximum_cell = int(CellType.PLAYER)
        validated_grid: list[list[int]] = []
        for row_index, row in enumerate(raw_grid):
            if not isinstance(row, list):
                raise TypeError(f"Row {row_index} in level grid is not a list.")
            if len(row) != column_count:
                raise ValueError("Level grid must be rectangular.")

            validated_row: list[int] = []
            for cell in row:
                if type(cell) is not int:
                    raise TypeError("Level grid cells must be integers.")
                if cell < minimum_cell or cell > maximum_cell:
                    raise ValueError("Level grid contains an invalid cell value.")
                validated_row.append(cast(int, cell))
            validated_grid.append(validated_row)

        return validated_grid

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

    def _migration_marker_path(self, level_id: str) -> Path:
        """Return the transaction marker path for a persistent level ID."""
        return self.levels_dir / f".{level_id}.migration"

    def _read_migration_marker(self, marker_path: Path) -> dict[str, Any]:
        """Read and validate a migration marker without trusting stored paths."""
        marker_id = marker_path.name[1 : -len(".migration")]
        if UUID(marker_id).hex != marker_id:
            raise ValueError("Migration marker has an invalid level ID.")

        with marker_path.open(encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Migration marker must contain a JSON object.")
        if type(data.get("version")) is not int or data["version"] != 1:
            raise ValueError("Migration marker version is unsupported.")
        if data.get("level_id") != marker_id:
            raise ValueError("Migration marker level ID does not match its filename.")
        if data.get("phase") not in ("prepared", "committed"):
            raise ValueError("Migration marker phase is invalid.")

        legacy_name = data.get("legacy")
        staged_name = data.get("staged")
        canonical_name = data.get("canonical")
        if not isinstance(legacy_name, str) or Path(legacy_name).name != legacy_name:
            raise ValueError("Migration marker legacy path is invalid.")
        if not isinstance(staged_name, str) or Path(staged_name).name != staged_name:
            raise ValueError("Migration marker staged path is invalid.")
        if not staged_name.startswith(f".{marker_id}.") or not staged_name.endswith(
            ".pending"
        ):
            raise ValueError("Migration marker staged path does not match its ID.")
        if canonical_name != f"{marker_id}.json":
            raise ValueError("Migration marker canonical path is invalid.")
        return data

    def _write_json_file(
        self, destination: Path, data: dict[str, Any], *, replace_existing: bool
    ) -> None:
        """Write JSON through a same-directory temporary file."""
        temporary = self.levels_dir / f".{uuid4().hex}.tmp"
        try:
            with temporary.open("x", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if replace_existing:
                temporary.replace(destination)
            else:
                if destination.exists():
                    raise FileExistsError(destination)
                temporary.rename(destination)
        finally:
            with suppress(OSError):
                if temporary.exists():
                    temporary.unlink()

    def _finish_migration(self, marker_path: Path, metadata: dict[str, Any]) -> Path:
        """Promote a committed staged level when possible; retain recoverable state."""
        committed_metadata = dict(metadata)
        committed_metadata["phase"] = "committed"
        try:
            self._write_json_file(
                marker_path, committed_metadata, replace_existing=True
            )
        except OSError:
            # A prepared marker plus a missing legacy file also recovers forward.
            pass

        staged_path = self.levels_dir / str(metadata["staged"])
        canonical_path = self.levels_dir / str(metadata["canonical"])
        if staged_path.exists() and not canonical_path.exists():
            try:
                staged_path.rename(canonical_path)
            except OSError:
                pass

        if staged_path.exists():
            return staged_path
        if canonical_path.exists():
            with suppress(OSError):
                marker_path.unlink()
            return canonical_path
        return staged_path

    def _load_custom_levels(self) -> None:
        """Load custom levels from files."""
        import sys

        if not self.levels_dir.exists():
            return

        migration_states: dict[str, dict[str, Any]] = {}
        blocked_ids: set[str] = set()
        for marker_path in sorted(
            self.levels_dir.glob(".*.migration"), key=lambda path: path.name.casefold()
        ):
            marker_id = marker_path.name[1 : -len(".migration")]
            try:
                if UUID(marker_id).hex != marker_id:
                    raise ValueError("Migration marker has an invalid level ID.")
                metadata = self._read_migration_marker(marker_path)
                legacy_path = self.levels_dir / metadata["legacy"]
                staged_path = self.levels_dir / metadata["staged"]
                canonical_path = self.levels_dir / metadata["canonical"]

                if metadata["phase"] == "prepared" and legacy_path.exists():
                    selected_path = legacy_path
                elif staged_path.exists():
                    selected_path = staged_path
                elif canonical_path.exists():
                    selected_path = canonical_path
                else:
                    selected_path = None

                metadata["selected_path"] = selected_path
                migration_states[marker_id] = metadata
                if selected_path is None:
                    blocked_ids.add(marker_id)
                    print(
                        f"Warning: Migration for level {marker_id} has no recoverable "
                        "representation; preserving its transaction marker.",
                        file=sys.stderr,
                    )
            except (OSError, TypeError, ValueError) as e:
                blocked_ids.add(marker_id)
                print(
                    f"Warning: Could not read migration marker {marker_path.name} "
                    f"[{type(e).__name__}]: {e}",
                    file=sys.stderr,
                )

        load_paths = {
            path.name.casefold(): path for path in self.levels_dir.glob("*.json")
        }
        expected_id_by_path: dict[str, str] = {}
        for marker_id, metadata in migration_states.items():
            selected_path = metadata["selected_path"]
            if selected_path is not None:
                expected_id_by_path[selected_path.name.casefold()] = marker_id
                if selected_path.suffix.casefold() != ".json":
                    load_paths[selected_path.name.casefold()] = selected_path

        candidates: list[Level] = []
        for level_file in sorted(
            load_paths.values(), key=lambda path: path.name.casefold()
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
                grid = Level._validate_serialized_grid(grid)
                raw_id = data.get("id")
                try:
                    level_id = UUID(raw_id).hex if isinstance(raw_id, str) else None
                except ValueError:
                    level_id = None
                if level_id is None:
                    level_id = uuid5(NAMESPACE_URL, level_file.name.casefold()).hex

                expected_id = expected_id_by_path.get(level_file.name.casefold())
                if expected_id is not None and level_id != expected_id:
                    raise ValueError(
                        "Migration representation has a mismatched level ID."
                    )
                if level_id in blocked_ids:
                    continue
                migration_state = migration_states.get(level_id)
                if migration_state is not None:
                    selected_path = migration_state["selected_path"]
                    if (
                        selected_path is None
                        or selected_path.name.casefold() != level_file.name.casefold()
                    ):
                        continue

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

        selected_by_id: dict[str, Level] = {}
        ambiguous_ids: set[str] = set()
        for candidate in candidates:
            candidate_id = candidate.level_id
            if candidate_id is None or candidate_id in ambiguous_ids:
                continue
            current = selected_by_id.get(candidate_id)
            if current is None:
                selected_by_id[candidate_id] = candidate
                continue

            candidate_path = candidate.storage_path
            current_path = current.storage_path
            same_content = candidate.name == current.name and np.array_equal(
                candidate.initial_grid, current.initial_grid
            )
            if not same_content:
                ambiguous_ids.add(candidate_id)
                del selected_by_id[candidate_id]
                print(
                    f"Warning: Conflicting custom level files share logical ID "
                    f"{candidate_id}; preserving both files and loading neither.",
                    file=sys.stderr,
                )
                continue

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

        data = level.to_dict()
        data["name"] = display_name
        data["id"] = level_id
        data["source"] = "custom"

        try:
            self.levels_dir.mkdir(parents=True, exist_ok=True)
            levels_root = self.levels_dir.resolve()
            destination = self.levels_dir / f"{level_id}.json"
            resolved_destination = destination.resolve()
            source_path = storage_path.resolve() if storage_path is not None else None
            marker_path = self._migration_marker_path(level_id)
            marker_metadata: Optional[dict[str, Any]] = None
            is_recovered_stage = False
            is_recovered_canonical = False

            if marker_path.exists():
                marker_metadata = self._read_migration_marker(marker_path)
                staged_path = self.levels_dir / marker_metadata["staged"]
                legacy_path = self.levels_dir / marker_metadata["legacy"]
                canonical_path = self.levels_dir / marker_metadata["canonical"]
                if (
                    source_path == staged_path.resolve()
                    and staged_path.exists()
                    and (
                        marker_metadata["phase"] == "committed"
                        or not legacy_path.exists()
                    )
                ):
                    is_recovered_stage = True
                elif (
                    source_path == canonical_path.resolve()
                    and canonical_path.exists()
                    and not staged_path.exists()
                    and (
                        marker_metadata["phase"] == "committed"
                        or not legacy_path.exists()
                    )
                ):
                    is_recovered_canonical = True
                elif (
                    source_path == legacy_path.resolve()
                    and marker_metadata["phase"] == "prepared"
                    and legacy_path.exists()
                ):
                    if staged_path.exists():
                        staged_path.unlink()
                    marker_path.unlink()
                    marker_metadata = None
                else:
                    raise LevelPersistenceError(
                        "An unfinished level migration must be recovered before saving."
                    )

            is_legacy_migration = (
                source_path is not None
                and source_path != resolved_destination
                and source_path.parent == levels_root
                and source_path.exists()
                and not is_recovered_stage
            )

            if destination.exists() and source_path != resolved_destination:
                if is_legacy_migration or is_recovered_stage:
                    raise LevelPersistenceError(
                        "The level's canonical path is occupied by another file."
                    )
                while destination.exists():
                    level_id = uuid4().hex
                    destination = self.levels_dir / f"{level_id}.json"
                data["id"] = level_id
                resolved_destination = destination.resolve()
                marker_path = self._migration_marker_path(level_id)
        except LevelPersistenceError:
            raise
        except (OSError, TypeError, ValueError) as exc:
            raise LevelPersistenceError("The level could not be saved.") from exc

        if is_recovered_stage:
            if source_path is None or marker_metadata is None:
                raise LevelPersistenceError("The staged level could not be identified.")
            try:
                self._write_json_file(source_path, data, replace_existing=True)
            except OSError as exc:
                raise LevelPersistenceError("The level could not be saved.") from exc
            saved_path = self._finish_migration(marker_path, marker_metadata)
        elif is_recovered_canonical and marker_metadata is not None:
            try:
                self._write_json_file(destination, data, replace_existing=True)
            except OSError as exc:
                raise LevelPersistenceError("The level could not be saved.") from exc
            saved_path = self._finish_migration(marker_path, marker_metadata)
        elif is_legacy_migration and source_path is not None:
            staged_path = self.levels_dir / f".{level_id}.{uuid4().hex}.pending"
            marker_metadata = {
                "version": 1,
                "level_id": level_id,
                "phase": "prepared",
                "legacy": source_path.name,
                "staged": staged_path.name,
                "canonical": destination.name,
            }
            try:
                self._write_json_file(staged_path, data, replace_existing=False)
                self._write_json_file(
                    marker_path, marker_metadata, replace_existing=False
                )
            except OSError as exc:
                with suppress(OSError):
                    if staged_path.exists():
                        staged_path.unlink()
                raise LevelPersistenceError("The level could not be saved.") from exc

            try:
                source_path.unlink()
            except OSError as exc:
                if source_path.exists():
                    try:
                        staged_path.unlink()
                    except OSError:
                        # The prepared marker keeps this residue uncommitted.
                        pass
                    else:
                        with suppress(OSError):
                            marker_path.unlink()
                    raise LevelPersistenceError(
                        "The level could not be saved."
                    ) from exc

            # Removing the old representation is the transaction commit point.
            # A prepared marker plus a missing legacy file recovers forward.
            saved_path = self._finish_migration(marker_path, marker_metadata)
        else:
            try:
                replace_existing = source_path == resolved_destination
                self._write_json_file(
                    destination, data, replace_existing=replace_existing
                )
            except OSError as exc:
                raise LevelPersistenceError("The level could not be saved.") from exc
            saved_path = destination

        if previous_name is not None and previous_name != display_name:
            del self.levels[previous_name]
        level.name = display_name
        level.source = "custom"
        level.level_id = level_id
        level.storage_path = saved_path
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
