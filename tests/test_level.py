"""Tests for Level and LevelManager models."""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.models.level import Level, LevelManager
from src.pushbox.utils.constants import DEFAULT_LEVELS, CellType

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
        grid = [
            [1, 1, 1, 1, 1],
            [1, 4, 5, 0, 1],
            [1, 1, 1, 1, 1],
        ]
        level = Level("Complete", grid)
        assert level.is_complete() is True

    def test_complete_level_empty_grid(self):
        """A grid with no boxes at all is technically complete."""
        grid = [
            [1, 1, 1],
            [1, 4, 1],
            [1, 1, 1],
        ]
        level = Level("No Boxes", grid)
        assert level.is_complete() is True

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
        grid = [
            [1, 1, 1, 1],
            [1, 5, 4, 1],
            [1, 1, 1, 1],
        ]
        level = Level("BOT corner", grid)
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

        grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
        custom = Level("Custom Test", grid)
        mgr.save_level(custom)

        # Verify file was written
        expected_file = levels_dir / "Custom_Test.json"
        assert expected_file.exists()

        # Verify data is correct
        with open(expected_file, encoding="utf-8") as f:
            data = json.load(f)
        assert data["name"] == "Custom Test"

        # Verify in-memory access
        loaded = mgr.get_level("Custom Test")
        assert loaded is not None
        assert loaded.name == "Custom Test"

    def test_delete_custom_level(self, tmp_path):
        levels_dir = tmp_path / "levels"
        mgr = LevelManager(levels_dir=str(levels_dir))

        grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
        custom = Level("To Delete", grid)
        mgr.save_level(custom)

        assert mgr.delete_level("To Delete") is True
        assert mgr.get_level("To Delete") is None

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

        level_data = {
            "name": "Disk Level",
            "grid": [[1, 1, 1], [1, 4, 1], [1, 1, 1]],
        }
        with open(levels_dir / "Disk_Level.json", "w", encoding="utf-8") as f:
            json.dump(level_data, f)

        mgr = LevelManager(levels_dir=str(levels_dir))
        loaded = mgr.get_level("Disk Level")
        assert loaded is not None
        assert loaded.name == "Disk Level"

    def test_malformed_json_skipped(self, tmp_path):
        """Malformed JSON files should be skipped without crashing."""
        levels_dir = tmp_path / "levels"
        levels_dir.mkdir()

        with open(levels_dir / "bad.json", "w", encoding="utf-8") as f:
            f.write("{invalid json content")

        # Should not raise
        mgr = LevelManager(levels_dir=str(levels_dir))
        # Default levels should still be there
        assert "Level 1" in mgr.get_level_names()


class TestDefaultLevelsIntegrity:
    """Test all default levels meet game-design constraints."""

    def test_default_levels_exist_and_are_valid(self):
        # 1. 10 default levels exist
        assert len(DEFAULT_LEVELS) == 10
        for i in range(1, 11):
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
