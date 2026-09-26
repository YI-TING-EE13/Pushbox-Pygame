"""Tests for Level and LevelManager models."""

import json
import os
import sys
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import numpy as np
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level, LevelManager, LevelPersistenceError
from src.pushbox.utils.constants import DEFAULT_LEVEL_METADATA, DEFAULT_LEVELS, CellType

VALID_CUSTOM_GRID = [
    [1, 1, 1, 1, 1],
    [1, 4, 3, 2, 1],
    [1, 1, 1, 1, 1],
]

# ---------------------------------------------------------------------------
# Level creation and basic properties
# ---------------------------------------------------------------------------


class TestLevelCreation:
    """Test level initialization and basic properties."""

    def test_level_name(self):
        grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
        level = Level("My Level", grid)
        assert level.name == "My Level"

    def test_level_dimensions(self):
        grid = [
            [1, 1, 1, 1],
            [1, 4, 0, 1],
            [1, 1, 1, 1],
        ]
        level = Level("3x4", grid)
        assert level.rows == 3
        assert level.cols == 4

    def test_level_grid_values(self):
        grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 2, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("Types", grid)
        assert level.get_cell(1, 1) == CellType.PLAYER
        assert level.get_cell(1, 2) == CellType.BOX
        assert level.get_cell(1, 3) == CellType.TARGET
        assert level.get_cell(0, 0) == CellType.WALL

    def test_level_reset_restores_initial_grid(self):
        grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("Reset", grid)
        # Mutate the grid
        level.set_cell(1, 1, CellType.EMPTY)
        level.set_cell(1, 2, CellType.PLAYER)
        assert level.get_cell(1, 1) == CellType.EMPTY

        # Reset should restore
        level.reset()
        assert level.get_cell(1, 1) == CellType.PLAYER
        assert level.get_cell(1, 2) == CellType.EMPTY


# ---------------------------------------------------------------------------
# Player position
# ---------------------------------------------------------------------------


class TestPlayerPosition:
    """Test player position detection."""

    def test_find_player(self):
        grid = [
            [1, 1, 1, 1, 1],
            [1, 0, 4, 0, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("Player", grid)
        pos = level.get_player_position()
        assert pos == (1, 2)

    def test_no_player_returns_none(self):
        """A grid with no player should return None."""
        grid = [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1],
        ]
        level = Level("No Player", grid)
        assert level.get_player_position() is None

    def test_multiple_players_returns_first(self):
        """Multiple players: get_player_position returns the first found."""
        grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 0, 4, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("Multi Player", grid)
        pos = level.get_player_position()
        # Should return a valid player position (first one in row-major order)
        assert pos is not None
        assert level.get_cell(pos[0], pos[1]) == CellType.PLAYER


# ---------------------------------------------------------------------------
# Grid bounds and cell access
# ---------------------------------------------------------------------------


class TestGridBounds:
    """Test position validation and out-of-bounds access."""

    def test_valid_positions(self):
        grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
        level = Level("Bounds", grid)
        assert level.is_valid_position(0, 0) is True
        assert level.is_valid_position(2, 2) is True
        assert level.is_valid_position(1, 1) is True

    def test_invalid_positions(self):
        grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
        level = Level("Bounds", grid)
        assert level.is_valid_position(-1, 0) is False
        assert level.is_valid_position(0, -1) is False
        assert level.is_valid_position(3, 0) is False
        assert level.is_valid_position(0, 3) is False

    def test_out_of_bounds_get_cell_returns_wall(self):
        grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
        level = Level("OOB", grid)
        assert level.get_cell(-1, 0) == CellType.WALL
        assert level.get_cell(0, 99) == CellType.WALL

    def test_set_cell_out_of_bounds_is_noop(self):
        grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
        level = Level("OOB Set", grid)
        # Should not raise
        level.set_cell(-1, 0, CellType.EMPTY)
        level.set_cell(99, 0, CellType.EMPTY)
        # Grid unchanged
        assert level.get_cell(1, 1) == CellType.PLAYER


# ---------------------------------------------------------------------------
# Completion and deadlock detection
# ---------------------------------------------------------------------------


class TestLevelCompletion:
    """Test level completion and deadlock detection."""

    def test_incomplete_level(self):
        grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 2, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("Incomplete", grid)
        assert level.is_complete() is False

    def test_complete_level_no_free_boxes(self):
        """Level is complete when no CellType.BOX exists (all are BOX_ON_TARGET)."""
        initial_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 2, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("Complete", initial_grid)
        level.grid = np.array([[1, 1, 1, 1, 1], [1, 0, 4, 5, 1], [1, 1, 1, 1, 1]])
        assert level.is_complete() is True

    def test_complete_level_empty_grid(self):
        """A level without goals or boxes is invalid and cannot be complete."""
        grid = [
            [1, 1, 1],
            [1, 4, 1],
            [1, 1, 1],
        ]
        level = Level("No Boxes", grid)
        assert level.is_complete() is False
        with pytest.raises(ValueError, match="at least one goal"):
            level.validate_structure()
        with pytest.raises(ValueError, match="at least one goal"):
            GameState(level)

    @pytest.mark.parametrize(
        "grid",
        [
            [
                [1, 1, 1, 1, 1, 1],
                [1, 4, 3, 2, 2, 1],
                [1, 1, 1, 1, 1, 1],
            ],
            [
                [1, 1, 1, 1, 1, 1],
                [1, 4, 3, 3, 2, 1],
                [1, 1, 1, 1, 1, 1],
            ],
            [
                [1, 1, 1, 1, 1, 1],
                [1, 4, 4, 3, 2, 1],
                [1, 1, 1, 1, 1, 1],
            ],
        ],
        ids=["one-box-two-goals", "two-boxes-one-goal", "multiple-players"],
    )
    def test_invalid_structure_cannot_be_complete_or_enter_gameplay(self, grid):
        level = Level("Invalid", grid)

        assert level.is_complete() is False
        with pytest.raises(ValueError):
            GameState(level)

    def test_extra_box_prevents_completion_when_all_targets_are_filled(self):
        grid = [
            [1, 1, 1, 1, 1, 1],
            [1, 4, 5, 3, 1, 1],
            [1, 1, 1, 1, 1, 1],
        ]
        level = Level("Extra Box", grid)
        assert level.is_complete() is False

    def test_mismatched_runtime_grid_shape_is_not_complete(self):
        level = Level("Resized Runtime Grid", VALID_CUSTOM_GRID)
        level.grid = np.array([[CellType.BOX_ON_TARGET]])
        assert level.is_complete() is False

    def test_deadlock_corner(self):
        """Box in a corner (wall above and wall to the left) => deadlocked."""
        grid = [
            [1, 1, 1, 1, 1],
            [1, 3, 0, 0, 1],
            [1, 0, 0, 4, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("Deadlock", grid)
        # Box at (1,1) has wall above (0,1) and wall to left (1,0) => deadlocked
        assert level.is_deadlocked() is True

    def test_no_deadlock(self):
        """Box in middle with open space on both axes => not deadlocked."""
        grid = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 3, 0, 1],
            [1, 0, 4, 0, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("No Deadlock", grid)
        assert level.is_deadlocked() is False

    def test_box_on_target_not_counted_as_deadlock_or_incomplete(self):
        """BOX_ON_TARGET should not trigger deadlock (it's not CellType.BOX)."""
        initial_grid = [[1, 1, 1, 1, 1], [1, 2, 4, 3, 1], [1, 1, 1, 1, 1]]
        level = Level("BOT corner", initial_grid)
        level.grid = np.array([[1, 1, 1, 1, 1], [1, 5, 4, 0, 1], [1, 1, 1, 1, 1]])
        # BOX_ON_TARGET at (1,1) is in a corner but is_deadlocked
        # only checks CellType.BOX, not BOX_ON_TARGET
        assert level.is_deadlocked() is False
        assert level.is_complete() is True


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


class TestLevelSerialization:
    """Test Level to_dict / from_dict round-trip."""

    def test_to_dict(self):
        grid = [
            [1, 1, 1],
            [1, 4, 1],
            [1, 1, 1],
        ]
        level = Level("Serialize", grid)
        d = level.to_dict()
        assert d["name"] == "Serialize"
        assert d["grid"] == grid

    def test_from_dict(self):
        data = {
            "name": "From Dict",
            "grid": [[1, 1, 1], [1, 4, 1], [1, 1, 1]],
        }
        level = Level.from_dict(data)
        assert level.name == "From Dict"
        assert level.rows == 3
        assert level.cols == 3
        assert level.get_cell(1, 1) == CellType.PLAYER

    def test_round_trip(self):
        grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 3, 2, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
        ]
        original = Level("Round Trip", grid)
        restored = Level.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.rows == original.rows
        assert restored.cols == original.cols
        for r in range(original.rows):
            for c in range(original.cols):
                assert restored.get_cell(r, c) == original.get_cell(r, c)


# ---------------------------------------------------------------------------
# LevelManager with tmp_path
# ---------------------------------------------------------------------------


class TestLevelManager:
    """Test LevelManager loading and saving custom levels."""

    def test_default_levels_loaded(self, tmp_path):
        """LevelManager should load built-in default levels."""
        mgr = LevelManager(levels_dir=str(tmp_path / "levels"))
        names = mgr.get_level_names()
        assert "Level 1" in names
        assert "Level 5" in names

    def test_get_nonexistent_level_returns_none(self, tmp_path):
        mgr = LevelManager(levels_dir=str(tmp_path / "levels"))
        assert mgr.get_level("Does Not Exist") is None

    def test_save_and_load_custom_level(self, tmp_path):
        levels_dir = tmp_path / "levels"
        mgr = LevelManager(levels_dir=str(levels_dir))

        custom = Level("Custom Test", VALID_CUSTOM_GRID)
        mgr.save_level(custom)

        # Custom files use persistent IDs instead of display-name-derived paths.
        level_files = list(levels_dir.glob("*.json"))
        assert len(level_files) == 1
        expected_file = level_files[0]
        assert expected_file.stem == custom.level_id

        # Verify data is correct
        with open(expected_file, encoding="utf-8") as f:
            data = json.load(f)
        assert data["name"] == "Custom Test"
        assert data["id"] == custom.level_id
        assert data["source"] == "custom"

        # Verify in-memory access
        loaded = mgr.get_level("Custom Test")
        assert loaded is not None
        assert loaded.name == "Custom Test"

    def test_delete_custom_level(self, tmp_path):
        levels_dir = tmp_path / "levels"
        mgr = LevelManager(levels_dir=str(levels_dir))

        custom = Level("To Delete", VALID_CUSTOM_GRID)
        mgr.save_level(custom)
        orphan_pending = levels_dir / f".{custom.level_id}.orphan.pending"
        orphan_pending.write_text("stale", encoding="utf-8")

        assert mgr.delete_level("To Delete") is True
        assert not orphan_pending.exists()
        assert mgr.get_level("To Delete") is None
        assert LevelManager(levels_dir=str(levels_dir)).get_level("To Delete") is None

    def test_delete_legacy_level_without_migration_residue(self, tmp_path):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        legacy_path = levels_dir / "Legacy_Only.json"
        legacy_path.write_text(
            json.dumps({"name": "Legacy Only", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )
        mgr = LevelManager(levels_dir=str(levels_dir))

        assert mgr.delete_level("Legacy Only") is True
        assert not legacy_path.exists()
        assert LevelManager(levels_dir=str(levels_dir)).get_level("Legacy Only") is None

    def test_cannot_delete_default_level(self, tmp_path):
        mgr = LevelManager(levels_dir=str(tmp_path / "levels"))
        assert mgr.delete_level("Level 1") is False
        assert mgr.get_level("Level 1") is not None

    def test_delete_nonexistent_returns_false(self, tmp_path):
        mgr = LevelManager(levels_dir=str(tmp_path / "levels"))
        assert mgr.delete_level("Ghost Level") is False

    def test_load_custom_levels_from_disk(self, tmp_path):
        """Custom levels saved to disk should be picked up by a new LevelManager."""
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()

        level_data = {"name": "Disk Level", "grid": VALID_CUSTOM_GRID}
        with open(levels_dir / "Disk_Level.json", "w", encoding="utf-8") as f:
            json.dump(level_data, f)

        mgr = LevelManager(levels_dir=str(levels_dir))
        loaded = mgr.get_level("Disk Level")
        assert loaded is not None
        assert loaded.name == "Disk Level"

    def test_malformed_json_skipped(self, tmp_path, capsys):
        """Malformed JSON files should be skipped and reported to stderr."""
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()

        with open(levels_dir / "bad.json", "w", encoding="utf-8") as f:
            f.write("{invalid json content")

        # Should not raise
        mgr = LevelManager(levels_dir=str(levels_dir))
        assert "Level 1" in mgr.get_level_names()

        captured = capsys.readouterr()
        assert "bad.json" in captured.err
        assert "JSONDecodeError" in captured.err

    def test_empty_custom_json_file_skipped(self, tmp_path, capsys):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        (levels_dir / "empty.json").write_text("", encoding="utf-8")

        mgr = LevelManager(levels_dir=str(levels_dir))
        assert "Level 1" in mgr.get_level_names()

        captured = capsys.readouterr()
        assert "empty.json" in captured.err
        assert "JSONDecodeError" in captured.err

    def test_non_dict_json_skipped(self, tmp_path, capsys):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        with open(levels_dir / "array.json", "w", encoding="utf-8") as f:
            json.dump([1, 2, 3], f)

        mgr = LevelManager(levels_dir=str(levels_dir))
        assert "Level 1" in mgr.get_level_names()

        captured = capsys.readouterr()
        assert "array.json" in captured.err
        assert "ValueError" in captured.err

    def test_missing_name_skipped(self, tmp_path, capsys):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        with open(levels_dir / "no_name.json", "w", encoding="utf-8") as f:
            json.dump({"grid": [[1, 1, 1], [1, 4, 1], [1, 1, 1]]}, f)

        mgr = LevelManager(levels_dir=str(levels_dir))
        assert "Level 1" in mgr.get_level_names()

        captured = capsys.readouterr()
        assert "no_name.json" in captured.err
        assert "KeyError" in captured.err

    def test_missing_grid_skipped(self, tmp_path, capsys):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        with open(levels_dir / "no_grid.json", "w", encoding="utf-8") as f:
            json.dump({"name": "No Grid"}, f)

        mgr = LevelManager(levels_dir=str(levels_dir))
        assert "Level 1" in mgr.get_level_names()

        captured = capsys.readouterr()
        assert "no_grid.json" in captured.err
        assert "KeyError" in captured.err

    def test_jagged_grid_skipped(self, tmp_path, capsys):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        # Row 1 has 3 elements, Row 2 has 2 elements (jagged)
        bad_data = {"name": "Jagged", "grid": [[1, 1, 1], [1, 4], [1, 1, 1]]}
        with open(levels_dir / "jagged.json", "w", encoding="utf-8") as f:
            json.dump(bad_data, f)

        mgr = LevelManager(levels_dir=str(levels_dir))
        assert "Level 1" in mgr.get_level_names()

        captured = capsys.readouterr()
        assert "jagged.json" in captured.err
        assert "ValueError" in captured.err
        assert "rectangular" in captured.err

    def test_invalid_cell_value_skipped(self, tmp_path, capsys):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        # Cell value 5 (BOX_ON_TARGET) is not allowed in custom level starting grids
        bad_data = {"name": "Bad Cell", "grid": [[1, 1, 1], [1, 5, 1], [1, 1, 1]]}
        with open(levels_dir / "bad_cell.json", "w", encoding="utf-8") as f:
            json.dump(bad_data, f)

        mgr = LevelManager(levels_dir=str(levels_dir))
        assert "Level 1" in mgr.get_level_names()

        captured = capsys.readouterr()
        assert "bad_cell.json" in captured.err
        assert "ValueError" in captured.err
        assert "value" in captured.err

    @pytest.mark.parametrize(
        "bad_value",
        [True, False, "1", 1.0, None, 99],
        ids=["true", "false", "string", "float", "null", "out-of-range"],
    )
    def test_raw_non_integer_grid_cells_are_rejected(self, tmp_path, capsys, bad_value):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        grid = [row[:] for row in VALID_CUSTOM_GRID]
        grid[0][0] = bad_value
        level_path = levels_dir / "malformed.json"
        level_path.write_text(
            json.dumps({"name": "Malformed", "grid": grid}), encoding="utf-8"
        )

        manager = LevelManager(levels_dir=str(levels_dir))

        custom_levels = [
            level for level in manager.levels.values() if level.source == "custom"
        ]
        assert custom_levels == []
        assert manager.get_level("Malformed") is None
        assert level_path.exists()
        assert (
            "Could not load custom level from malformed.json" in capsys.readouterr().err
        )

    def test_raw_integer_grid_loads_without_coercion(self, tmp_path):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        (levels_dir / "valid.json").write_text(
            json.dumps({"name": "Valid Integer Grid", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )

        manager = LevelManager(levels_dir=str(levels_dir))

        loaded = manager.get_level("Valid Integer Grid")
        assert loaded is not None
        assert loaded.initial_grid.tolist() == VALID_CUSTOM_GRID

    def test_one_bad_does_not_block_one_good_level(self, tmp_path):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()

        # 1. Write one bad level
        (levels_dir / "bad.json").write_text("{broken", encoding="utf-8")

        # 2. Write one good level
        good_data = {"name": "Good Level", "grid": VALID_CUSTOM_GRID}
        with open(levels_dir / "good.json", "w", encoding="utf-8") as f:
            json.dump(good_data, f)

        mgr = LevelManager(levels_dir=str(levels_dir))

        # Good level must be loaded successfully
        assert mgr.get_level("Good Level") is not None
        # Default levels also loaded
        assert "Level 1" in mgr.get_level_names()

    def test_normalized_names_have_distinct_persistent_identity(self, tmp_path):
        levels_dir = tmp_path / "levels"
        manager = LevelManager(levels_dir=str(levels_dir))
        other_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 0, 3, 2],
            [1, 1, 1, 1, 1],
        ]

        first = Level("A B", VALID_CUSTOM_GRID)
        second = Level("A_B", other_grid)
        manager.save_level(first)
        first_saved_grid = manager.get_level("A B").initial_grid.copy()
        manager.save_level(second)

        assert first.level_id != second.level_id
        assert len(list(levels_dir.glob("*.json"))) == 2
        assert (manager.get_level("A B").initial_grid == first_saved_grid).all()

        reloaded = LevelManager(levels_dir=str(levels_dir))
        assert reloaded.get_level("A B") is not None
        assert reloaded.get_level("A_B") is not None
        assert reloaded.get_level("A B").level_id == first.level_id
        assert reloaded.get_level("A_B").level_id == second.level_id
        assert reloaded.get_level("A B").get_cell(1, 2) == CellType.BOX
        assert reloaded.get_level("A_B").get_cell(1, 3) == CellType.BOX

    def test_new_same_name_level_cannot_overwrite_existing_level(self, tmp_path):
        levels_dir = tmp_path / "levels"
        manager = LevelManager(levels_dir=str(levels_dir))
        first = Level("Foo", VALID_CUSTOM_GRID)
        manager.save_level(first)
        first_path = first.storage_path
        original_bytes = first_path.read_bytes()
        second_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 2, 3, 1],
            [1, 1, 1, 1, 1],
        ]

        with pytest.raises(ValueError, match="already exists"):
            manager.save_level(Level("Foo", second_grid))

        assert first_path.read_bytes() == original_bytes
        restored = LevelManager(levels_dir=str(levels_dir)).get_level("Foo")
        assert restored is not None
        assert restored.level_id == first.level_id
        assert restored.initial_grid.tolist() == VALID_CUSTOM_GRID

    @pytest.mark.parametrize("second_name", ["foo", "FOO"])
    def test_new_level_name_conflict_is_case_insensitive(self, tmp_path, second_name):
        manager = LevelManager(levels_dir=str(tmp_path / "levels"))
        manager.save_level(Level("Foo", VALID_CUSTOM_GRID))

        with pytest.raises(ValueError, match="already exists"):
            manager.save_level(Level(second_name, VALID_CUSTOM_GRID))

    def test_loaded_level_can_be_renamed_without_changing_identity(self, tmp_path):
        levels_dir = tmp_path / "levels"
        manager = LevelManager(levels_dir=str(levels_dir))
        manager.save_level(Level("Foo", VALID_CUSTOM_GRID))
        loaded_manager = LevelManager(levels_dir=str(levels_dir))
        loaded = loaded_manager.get_level("Foo")
        assert loaded is not None
        original_id = loaded.level_id

        loaded.name = "Renamed Foo"
        loaded_manager.save_level(loaded)

        restored = LevelManager(levels_dir=str(levels_dir)).get_level("Renamed Foo")
        assert restored is not None
        assert restored.level_id == original_id

    def test_custom_name_cannot_replace_builtin_level(self, tmp_path):
        levels_dir = tmp_path / "levels"
        manager = LevelManager(levels_dir=str(levels_dir))
        original = manager.get_level("Level 1").initial_grid.copy()

        with pytest.raises(ValueError, match="built-in"):
            manager.save_level(Level("Level 1", VALID_CUSTOM_GRID))

        reloaded = LevelManager(levels_dir=str(levels_dir))
        assert reloaded.get_level("Level 1").source == "builtin"
        assert (reloaded.get_level("Level 1").initial_grid == original).all()
        assert not list(levels_dir.glob("*.json"))

    def test_legacy_levels_remain_loadable_and_migrate_safely(self, tmp_path):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        legacy_path = levels_dir / "Legacy_Name.json"
        legacy_path.write_text(
            json.dumps({"name": "Legacy Name", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )

        manager = LevelManager(levels_dir=str(levels_dir))
        legacy = manager.get_level("Legacy Name")
        assert legacy is not None
        assert legacy.source == "custom"
        assert legacy.storage_path == legacy_path

        previous_id = legacy.level_id
        changed_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 2, 3, 1],
            [1, 1, 1, 1, 1],
        ]
        legacy.name = "Renamed Legacy"
        legacy.initial_grid = np.array(changed_grid)
        legacy.reset()
        manager.save_level(legacy)

        assert not legacy_path.exists()
        migrated_files = list(levels_dir.glob("*.json"))
        assert len(migrated_files) == 1
        assert migrated_files[0].stem == previous_id
        assert not list(levels_dir.glob("*.pending"))
        assert not list(levels_dir.glob(".*.migration"))
        restored = LevelManager(levels_dir=str(levels_dir)).get_level("Renamed Legacy")
        assert restored is not None
        assert restored.level_id == previous_id
        assert restored.initial_grid.tolist() == changed_grid

    def test_failed_legacy_cleanup_rolls_back_canonical_file(
        self, tmp_path, monkeypatch
    ):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        legacy_path = levels_dir / "Legacy_Name.json"
        legacy_path.write_text(
            json.dumps({"name": "Legacy Name", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )
        manager = LevelManager(levels_dir=str(levels_dir))
        original = manager.get_level("Legacy Name")
        assert original is not None
        original_id = original.level_id
        changed_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 2, 3, 1],
            [1, 1, 1, 1, 1],
        ]
        edited = Level(
            "Renamed Legacy",
            changed_grid,
            level_id=original_id,
            storage_path=legacy_path,
        )
        original_unlink = Path.unlink

        def fail_legacy_unlink(path, *args, **kwargs):
            if path == legacy_path:
                raise OSError("injected legacy cleanup failure")
            return original_unlink(path, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", fail_legacy_unlink)

        with pytest.raises(LevelPersistenceError, match="could not be saved"):
            manager.save_level(edited)

        assert legacy_path.exists()
        assert list(levels_dir.glob("*.json")) == [legacy_path]
        assert not list(levels_dir.glob("*.pending"))
        assert not list(levels_dir.glob(".*.migration"))
        assert manager.get_level("Legacy Name") is original
        assert manager.get_level("Renamed Legacy") is None
        assert original.level_id == original_id

        restarted = LevelManager(levels_dir=str(levels_dir))
        assert restarted.get_level("Legacy Name") is not None
        assert restarted.get_level("Renamed Legacy") is None

    def test_dual_legacy_cleanup_failure_delete_does_not_resurrect_stage(
        self, tmp_path, monkeypatch
    ):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        legacy_path = levels_dir / "Legacy_Name.json"
        legacy_path.write_text(
            json.dumps({"name": "Legacy Name", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )
        manager = LevelManager(levels_dir=str(levels_dir))
        unrelated = Level("Unrelated", VALID_CUSTOM_GRID)
        manager.save_level(unrelated)
        unrelated_id = unrelated.level_id
        unrelated_pending = levels_dir / f".{unrelated_id}.orphan.pending"
        unrelated_pending.write_text("unrelated", encoding="utf-8")
        original = manager.get_level("Legacy Name")
        assert original is not None
        original_id = original.level_id
        changed_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 2, 3, 1],
            [1, 1, 1, 1, 1],
        ]
        edited = Level(
            "Renamed Legacy",
            changed_grid,
            level_id=original_id,
            storage_path=legacy_path,
        )
        original_unlink = Path.unlink
        canonical_path = levels_dir / f"{original_id}.json"

        def fail_both_cleanup_operations(path, *args, **kwargs):
            if (
                path == legacy_path
                or path == canonical_path
                or path.suffix == ".pending"
            ):
                raise OSError("injected migration cleanup failure")
            return original_unlink(path, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", fail_both_cleanup_operations)

        with pytest.raises(LevelPersistenceError, match="could not be saved"):
            manager.save_level(edited)

        marker_path = levels_dir / f".{original_id}.migration"
        assert legacy_path.exists()
        staged_representations = [
            path for path in levels_dir.glob("*.pending") if path != unrelated_pending
        ]
        assert len(staged_representations) == 1
        assert (
            json.loads(staged_representations[0].read_text(encoding="utf-8"))["grid"]
            == changed_grid
        )
        assert edited.name == "Renamed Legacy"
        assert edited.storage_path == legacy_path
        assert manager.get_level("Legacy Name") is original
        assert manager.get_level("Renamed Legacy") is None

        restarted = LevelManager(levels_dir=str(levels_dir))
        custom_levels = [
            level for level in restarted.levels.values() if level.source == "custom"
        ]
        restored_originals = [
            level for level in custom_levels if level.level_id == original_id
        ]
        assert len(restored_originals) == 1
        assert restored_originals[0].name == "Legacy Name"
        assert restored_originals[0].initial_grid.tolist() == VALID_CUSTOM_GRID
        assert restarted.get_level("Unrelated") is not None
        assert restarted.get_level("Unrelated").level_id == unrelated_id
        assert unrelated_pending.exists()
        assert marker_path.exists()
        assert not canonical_path.exists()

        monkeypatch.undo()
        assert restarted.delete_level("Legacy Name") is True

        after_delete = LevelManager(levels_dir=str(levels_dir))
        remaining_custom_levels = [
            level for level in after_delete.levels.values() if level.source == "custom"
        ]
        assert [level.level_id for level in remaining_custom_levels] == [unrelated_id]
        assert after_delete.get_level("Legacy Name") is None
        assert after_delete.get_level("Renamed Legacy") is None
        assert unrelated_pending.exists()

    @pytest.mark.parametrize("failed_artifact", ["pending", "marker", "legacy"])
    def test_delete_failure_keeps_legacy_authoritative(
        self, tmp_path, monkeypatch, failed_artifact
    ):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        legacy_path = levels_dir / "Legacy_Name.json"
        legacy_path.write_text(
            json.dumps({"name": "Legacy Name", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )
        logical_id = uuid5(NAMESPACE_URL, legacy_path.name.casefold()).hex
        staged_path = levels_dir / f".{logical_id}.0123456789abcdef.pending"
        new_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 2, 3, 1],
            [1, 1, 1, 1, 1],
        ]
        staged_path.write_text(
            json.dumps(
                {
                    "name": "New Failed Save",
                    "grid": new_grid,
                    "id": logical_id,
                    "source": "custom",
                }
            ),
            encoding="utf-8",
        )
        marker_path = levels_dir / f".{logical_id}.migration"
        marker_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "level_id": logical_id,
                    "phase": "prepared",
                    "legacy": legacy_path.name,
                    "staged": staged_path.name,
                    "canonical": f"{logical_id}.json",
                }
            ),
            encoding="utf-8",
        )
        manager = LevelManager(levels_dir=str(levels_dir))
        original = manager.get_level("Legacy Name")
        assert original is not None
        original_unlink = Path.unlink
        failed_path = {
            "pending": staged_path,
            "marker": marker_path,
            "legacy": legacy_path,
        }[failed_artifact]

        def fail_delete_cleanup(path, *args, **kwargs):
            if path == failed_path:
                raise OSError(f"injected {failed_artifact} cleanup failure")
            return original_unlink(path, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", fail_delete_cleanup)
        with pytest.raises(LevelPersistenceError, match="could not be deleted"):
            manager.delete_level("Legacy Name")

        assert legacy_path.exists()
        assert staged_path.exists() is (failed_artifact == "pending")
        assert marker_path.exists() is (failed_artifact in ("pending", "marker"))
        assert manager.get_level("Legacy Name") is original
        restarted = LevelManager(levels_dir=str(levels_dir))
        restored = restarted.get_level("Legacy Name")
        assert restored is not None
        assert restored.level_id == logical_id
        assert restored.initial_grid.tolist() == VALID_CUSTOM_GRID
        assert restarted.get_level("New Failed Save") is None

        monkeypatch.undo()
        assert manager.delete_level("Legacy Name") is True
        assert not [
            level
            for level in LevelManager(levels_dir=str(levels_dir)).levels.values()
            if level.level_id == logical_id
        ]

    def test_crash_after_legacy_removal_recovers_staged_edit(self, tmp_path):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        legacy_path = levels_dir / "Legacy_Name.json"
        legacy_path.write_text(
            json.dumps({"name": "Legacy Name", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )
        logical_id = uuid5(NAMESPACE_URL, legacy_path.name.casefold()).hex
        edited_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 2, 3, 1],
            [1, 1, 1, 1, 1],
        ]
        staged_path = levels_dir / f".{logical_id}.0123456789abcdef.pending"
        staged_path.write_text(
            json.dumps(
                {
                    "name": "Renamed Legacy",
                    "grid": edited_grid,
                    "id": logical_id,
                    "source": "custom",
                }
            ),
            encoding="utf-8",
        )
        marker_path = levels_dir / f".{logical_id}.migration"
        marker_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "level_id": logical_id,
                    "phase": "prepared",
                    "legacy": legacy_path.name,
                    "staged": staged_path.name,
                    "canonical": f"{logical_id}.json",
                }
            ),
            encoding="utf-8",
        )
        legacy_path.unlink()

        manager = LevelManager(levels_dir=str(levels_dir))
        custom_levels = [
            level for level in manager.levels.values() if level.source == "custom"
        ]

        assert len(custom_levels) == 1
        assert custom_levels[0].name == "Renamed Legacy"
        assert custom_levels[0].level_id == logical_id
        assert custom_levels[0].storage_path == staged_path
        assert custom_levels[0].initial_grid.tolist() == edited_grid
        assert marker_path.exists()

    def test_committed_marker_residue_keeps_canonical_level_resavable(
        self, tmp_path, monkeypatch
    ):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        legacy_path = levels_dir / "Legacy_Name.json"
        legacy_path.write_text(
            json.dumps({"name": "Legacy Name", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )
        manager = LevelManager(levels_dir=str(levels_dir))
        level = manager.get_level("Legacy Name")
        assert level is not None
        logical_id = level.level_id
        marker_path = levels_dir / f".{logical_id}.migration"
        original_unlink = Path.unlink

        def fail_marker_cleanup(path, *args, **kwargs):
            if path == marker_path:
                raise OSError("injected transaction marker cleanup failure")
            return original_unlink(path, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", fail_marker_cleanup)

        level.name = "Migrated Legacy"
        manager.save_level(level)
        assert not legacy_path.exists()
        assert marker_path.exists()
        assert level.storage_path == levels_dir / f"{logical_id}.json"

        edited_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 2, 3, 1],
            [1, 1, 1, 1, 1],
        ]
        level.initial_grid = np.array(edited_grid)
        level.reset()
        manager.save_level(level)

        restored_manager = LevelManager(levels_dir=str(levels_dir))
        restored = restored_manager.get_level("Migrated Legacy")
        assert restored is not None
        assert restored.level_id == logical_id
        assert restored.initial_grid.tolist() == edited_grid

        monkeypatch.undo()
        assert restored_manager.delete_level("Migrated Legacy") is True
        after_delete = LevelManager(levels_dir=str(levels_dir))
        assert not [
            level
            for level in after_delete.levels.values()
            if level.level_id == logical_id
        ]
        assert not marker_path.exists()

    def test_delete_committed_staged_level_after_promotion_failure(self, tmp_path):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        logical_id = uuid5(NAMESPACE_URL, "committed-staged-level").hex
        staged_path = levels_dir / f".{logical_id}.0123456789abcdef.pending"
        staged_path.write_text(
            json.dumps(
                {
                    "name": "Committed Staged",
                    "grid": VALID_CUSTOM_GRID,
                    "id": logical_id,
                    "source": "custom",
                }
            ),
            encoding="utf-8",
        )
        marker_path = levels_dir / f".{logical_id}.migration"
        marker_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "level_id": logical_id,
                    "phase": "committed",
                    "legacy": "Legacy_Only.json",
                    "staged": staged_path.name,
                    "canonical": f"{logical_id}.json",
                }
            ),
            encoding="utf-8",
        )
        manager = LevelManager(levels_dir=str(levels_dir))

        assert manager.get_level("Committed Staged") is not None
        assert manager.delete_level("Committed Staged") is True
        restarted = LevelManager(levels_dir=str(levels_dir))
        assert not [
            level for level in restarted.levels.values() if level.level_id == logical_id
        ]
        assert not staged_path.exists()
        assert not marker_path.exists()

    @pytest.mark.parametrize("active_kind", ["staged", "canonical"])
    def test_delete_failure_preserves_committed_representation_for_retry(
        self, tmp_path, monkeypatch, active_kind
    ):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        logical_id = uuid5(NAMESPACE_URL, f"committed-{active_kind}").hex
        active_path = (
            levels_dir / f".{logical_id}.0123456789abcdef.pending"
            if active_kind == "staged"
            else levels_dir / f"{logical_id}.json"
        )
        active_path.write_text(
            json.dumps(
                {
                    "name": "Committed Level",
                    "grid": VALID_CUSTOM_GRID,
                    "id": logical_id,
                    "source": "custom",
                }
            ),
            encoding="utf-8",
        )
        marker_path = levels_dir / f".{logical_id}.migration"
        marker_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "level_id": logical_id,
                    "phase": "committed",
                    "legacy": "Legacy_Only.json",
                    "staged": f".{logical_id}.0123456789abcdef.pending",
                    "canonical": f"{logical_id}.json",
                }
            ),
            encoding="utf-8",
        )
        manager = LevelManager(levels_dir=str(levels_dir))
        assert manager.get_level("Committed Level") is not None
        original_unlink = Path.unlink

        def fail_active_cleanup(path, *args, **kwargs):
            if path == active_path:
                raise OSError(f"injected {active_kind} cleanup failure")
            return original_unlink(path, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", fail_active_cleanup)
        with pytest.raises(LevelPersistenceError, match="could not be deleted"):
            manager.delete_level("Committed Level")

        assert active_path.exists()
        assert marker_path.exists()
        assert manager.get_level("Committed Level") is not None
        assert LevelManager(levels_dir=str(levels_dir)).get_level("Committed Level")

        monkeypatch.undo()
        assert manager.delete_level("Committed Level") is True
        restarted = LevelManager(levels_dir=str(levels_dir))
        assert not [
            level for level in restarted.levels.values() if level.level_id == logical_id
        ]

    @pytest.mark.parametrize("active_kind", ["staged", "canonical"])
    def test_delete_committed_level_succeeds_when_marker_cleanup_fails(
        self, tmp_path, monkeypatch, active_kind
    ):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        logical_id = uuid5(NAMESPACE_URL, f"committed-marker-residue-{active_kind}").hex
        staged_path = levels_dir / f".{logical_id}.0123456789abcdef.pending"
        canonical_path = levels_dir / f"{logical_id}.json"
        active_path = staged_path if active_kind == "staged" else canonical_path
        active_path.write_text(
            json.dumps(
                {
                    "name": "Committed Level",
                    "grid": VALID_CUSTOM_GRID,
                    "id": logical_id,
                    "source": "custom",
                }
            ),
            encoding="utf-8",
        )
        marker_path = levels_dir / f".{logical_id}.migration"
        marker_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "level_id": logical_id,
                    "phase": "committed",
                    "legacy": "Legacy_Only.json",
                    "staged": staged_path.name,
                    "canonical": canonical_path.name,
                }
            ),
            encoding="utf-8",
        )
        manager = LevelManager(levels_dir=str(levels_dir))
        assert manager.get_level("Committed Level") is not None
        original_unlink = Path.unlink

        def fail_marker_unlink(path, *args, **kwargs):
            if path == marker_path:
                assert not active_path.exists()
                raise OSError("injected migration marker cleanup failure")
            return original_unlink(path, *args, **kwargs)

        monkeypatch.setattr(Path, "unlink", fail_marker_unlink)
        assert manager.delete_level("Committed Level") is True

        assert not active_path.exists()
        assert marker_path.exists()
        assert manager.get_level("Committed Level") is None
        assert not [
            level for level in manager.levels.values() if level.level_id == logical_id
        ]
        restarted = LevelManager(levels_dir=str(levels_dir))
        assert not [
            level for level in restarted.levels.values() if level.level_id == logical_id
        ]

        monkeypatch.undo()
        assert manager.delete_level("Committed Level") is False
        assert marker_path.exists()
        assert not [
            level
            for level in LevelManager(levels_dir=str(levels_dir)).levels.values()
            if level.level_id == logical_id
        ]

    def test_unmarked_conflicting_duplicate_id_is_not_guessed(self, tmp_path, capsys):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        legacy_path = levels_dir / "Legacy_Name.json"
        legacy_path.write_text(
            json.dumps({"name": "Legacy Name", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )
        logical_id = uuid5(NAMESPACE_URL, legacy_path.name.casefold()).hex
        conflicting_path = levels_dir / f"{logical_id}.json"
        conflicting_path.write_text(
            json.dumps(
                {
                    "name": "Renamed Legacy",
                    "grid": [
                        [1, 1, 1, 1, 1],
                        [1, 4, 2, 3, 1],
                        [1, 1, 1, 1, 1],
                    ],
                    "id": logical_id,
                    "source": "custom",
                }
            ),
            encoding="utf-8",
        )

        manager = LevelManager(levels_dir=str(levels_dir))
        custom_levels = [
            level for level in manager.levels.values() if level.source == "custom"
        ]

        assert custom_levels == []
        assert legacy_path.exists()
        assert conflicting_path.exists()
        assert (
            "Conflicting custom level files share logical ID" in capsys.readouterr().err
        )

    def test_ambiguous_legacy_names_are_kept_with_deterministic_labels(self, tmp_path):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        second_grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 0, 3, 2],
            [1, 1, 1, 1, 1],
        ]
        (levels_dir / "a.json").write_text(
            json.dumps({"name": "Duplicate", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )
        (levels_dir / "b.json").write_text(
            json.dumps({"name": "Duplicate", "grid": second_grid}),
            encoding="utf-8",
        )

        manager = LevelManager(levels_dir=str(levels_dir))

        first = manager.get_level("Duplicate")
        second = manager.get_level("Duplicate (2)")
        assert first is not None
        assert second is not None
        assert first.level_id != second.level_id
        assert first.get_cell(1, 2) == CellType.BOX
        assert second.get_cell(1, 3) == CellType.BOX

    def test_legacy_custom_name_cannot_shadow_builtin(self, tmp_path):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        (levels_dir / "legacy-level-1.json").write_text(
            json.dumps({"name": "Level 1", "grid": VALID_CUSTOM_GRID}),
            encoding="utf-8",
        )

        manager = LevelManager(levels_dir=str(levels_dir))

        assert manager.get_level("Level 1").source == "builtin"
        custom = manager.get_level("Level 1 (Custom)")
        assert custom is not None
        assert custom.source == "custom"

    def test_invalid_custom_level_counts_are_rejected(self, tmp_path, capsys):
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()
        invalid_grid = [
            [1, 1, 1, 1, 1, 1],
            [1, 4, 3, 2, 0, 2],
            [1, 1, 1, 1, 1, 1],
        ]
        (levels_dir / "unbalanced.json").write_text(
            json.dumps({"name": "Unbalanced", "grid": invalid_grid}),
            encoding="utf-8",
        )

        manager = LevelManager(levels_dir=str(levels_dir))

        assert manager.get_level("Unbalanced") is None
        assert "matching, non-zero box and target counts" in capsys.readouterr().err


class TestDefaultLevelsIntegrity:
    """Test all default levels meet game-design constraints."""

    def test_default_levels_exist_and_are_valid(self):
        # 1. 30 default levels exist
        assert len(DEFAULT_LEVELS) == 30
        for i in range(1, 31):
            assert f"Level {i}" in DEFAULT_LEVELS

        for name, grid in DEFAULT_LEVELS.items():
            level = Level(name, grid)
            # 2. Rectangular check
            rows = len(grid)
            cols = len(grid[0])
            for row in grid:
                assert len(row) == cols, f"{name} is not rectangular"

            # 3. Outer borders are walls
            for c in range(cols):
                assert grid[0][c] == CellType.WALL, (
                    f"{name} top border has non-wall at col {c}"
                )
                assert grid[rows - 1][c] == CellType.WALL, (
                    f"{name} bottom border has non-wall at col {c}"
                )
            for r in range(rows):
                assert grid[r][0] == CellType.WALL, (
                    f"{name} left border has non-wall at row {r}"
                )
                assert grid[r][cols - 1] == CellType.WALL, (
                    f"{name} right border has non-wall at row {r}"
                )

            # 4. Exactly one player
            player_count = sum(row.count(CellType.PLAYER) for row in grid)
            assert player_count == 1, (
                f"{name} has {player_count} players (expected exactly 1)"
            )

            # 5. At least one box
            box_count = sum(row.count(CellType.BOX) for row in grid)
            assert box_count > 0, f"{name} has 0 boxes (expected at least 1)"

            # 6. Box count equals target count
            target_count = sum(row.count(CellType.TARGET) for row in grid)
            assert box_count == target_count, (
                f"{name} has box count {box_count} != target count {target_count}"
            )

            # 7. No initial BOX_ON_TARGET
            bot_count = sum(row.count(CellType.BOX_ON_TARGET) for row in grid)
            assert bot_count == 0, f"{name} has initial BOX_ON_TARGET"

            # 8. Not complete initially
            assert not level.is_complete(), f"{name} is complete initially"
            level.validate_structure()


class TestDefaultLevelsMetadata:
    """Test that default level metadata is consistent and valid."""

    def test_metadata_completeness(self):
        # 1. exactly 30 metadata entries
        assert len(DEFAULT_LEVEL_METADATA) == 30

        # 2. every level in DEFAULT_LEVELS has metadata and vice versa
        for name in DEFAULT_LEVELS:
            assert name in DEFAULT_LEVEL_METADATA, f"{name} is missing metadata"
        for name in DEFAULT_LEVEL_METADATA:
            assert name in DEFAULT_LEVELS, (
                f"Metadata entry {name} does not correspond to a default level"
            )

    def test_metadata_fields(self):
        for name, meta in DEFAULT_LEVEL_METADATA.items():
            # 3. metadata contains required fields
            for field in ["difficulty", "theme", "boxes", "note"]:
                assert field in meta, f"{name} metadata is missing field: {field}"

            # 4. metadata strings are non-empty
            assert (
                isinstance(meta["difficulty"], str) and meta["difficulty"].strip() != ""
            )
            assert isinstance(meta["theme"], str) and meta["theme"].strip() != ""
            assert isinstance(meta["note"], str) and meta["note"].strip() != ""
            assert isinstance(meta["boxes"], int)

            # 5. boxes equals actual number of CellType.BOX cells in that level
            grid = DEFAULT_LEVELS[name]
            box_count = sum(row.count(CellType.BOX) for row in grid)
            assert meta["boxes"] == box_count, (
                f"{name} metadata box count {meta['boxes']} != actual count {box_count}"
            )
