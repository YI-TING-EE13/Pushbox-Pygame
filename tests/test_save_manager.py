"""Tests for SaveManager: progress tracking, high scores, and file I/O."""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pushbox.models.save_manager import SaveManager

# ---------------------------------------------------------------------------
# 1. Default state (no files)
# ---------------------------------------------------------------------------


class TestSaveManagerDefaults:
    """Test SaveManager behavior with no pre-existing files."""

    def test_empty_progress_on_init(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        assert mgr.get_all_progress() == {}

    def test_default_level_progress(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        progress = mgr.get_level_progress("Level 1")
        assert progress["completed"] is False
        assert progress["best_moves"] is None
        assert progress["best_time"] is None
        assert progress["best_pushes"] is None
        assert progress["attempts"] == 0

    def test_empty_high_scores(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        assert mgr.get_high_scores("Level 1") == []

    def test_completion_stats_empty(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        stats = mgr.get_completion_stats()
        assert stats["total_levels"] == 0
        assert stats["completed"] == 0
        assert stats["percentage"] == 0


# ---------------------------------------------------------------------------
# 2. Malformed JSON fallback
# ---------------------------------------------------------------------------


class TestSaveManagerMalformedData:
    """Test malformed JSON files don't crash and are safely backed up."""

    def test_malformed_progress_json(self, tmp_path, capsys):
        progress_file = tmp_path / "progress.json"
        progress_file.write_text("{broken json", encoding="utf-8")

        mgr = SaveManager(save_dir=str(tmp_path))
        assert mgr.get_all_progress() == {}

        # Original corrupted file backed up
        bak_file = tmp_path / "progress.json.bak"
        assert bak_file.exists()
        assert bak_file.read_text(encoding="utf-8") == "{broken json"

        # Rebuilt file exists on disk as empty dict
        assert progress_file.exists()
        assert json.loads(progress_file.read_text(encoding="utf-8")) == {}

        # Stderr captures the warning
        captured = capsys.readouterr()
        assert "Could not load progress" in captured.err

    def test_malformed_scores_json(self, tmp_path, capsys):
        scores_file = tmp_path / "scores.json"
        scores_file.write_text("not valid json!", encoding="utf-8")

        mgr = SaveManager(save_dir=str(tmp_path))
        assert mgr.get_high_scores("Level 1") == []

        # Original corrupted file backed up
        bak_file = tmp_path / "scores.json.bak"
        assert bak_file.exists()
        assert bak_file.read_text(encoding="utf-8") == "not valid json!"

        # Rebuilt file exists on disk as empty dict
        assert scores_file.exists()
        assert json.loads(scores_file.read_text(encoding="utf-8")) == {}

        # Stderr captures the warning
        captured = capsys.readouterr()
        assert "Could not load scores" in captured.err

    def test_non_dict_progress_json(self, tmp_path, capsys):
        """A JSON array instead of object should be treated as empty and backed up."""
        progress_file = tmp_path / "progress.json"
        progress_file.write_text("[1, 2, 3]", encoding="utf-8")

        mgr = SaveManager(save_dir=str(tmp_path))
        assert mgr.get_all_progress() == {}

        bak_file = tmp_path / "progress.json.bak"
        assert bak_file.exists()
        assert json.loads(bak_file.read_text(encoding="utf-8")) == [1, 2, 3]

        captured = capsys.readouterr()
        assert "Progress file is not a dictionary" in captured.err

    def test_non_dict_scores_json(self, tmp_path, capsys):
        scores_file = tmp_path / "scores.json"
        scores_file.write_text('"just a string"', encoding="utf-8")

        mgr = SaveManager(save_dir=str(tmp_path))
        assert mgr.get_high_scores("Level 1") == []

        bak_file = tmp_path / "scores.json.bak"
        assert bak_file.exists()
        assert json.loads(bak_file.read_text(encoding="utf-8")) == "just a string"

        captured = capsys.readouterr()
        assert "Scores file is not a dictionary" in captured.err

    def test_existing_backup_increment(self, tmp_path):
        """Test that save manager does not overwrite existing .bak files."""
        progress_file = tmp_path / "progress.json"

        # 1. Existing backup
        bak_file = tmp_path / "progress.json.bak"
        bak_file.write_text("old progress backup", encoding="utf-8")

        # 2. Write new corrupted progress
        progress_file.write_text("{broken 2", encoding="utf-8")

        mgr = SaveManager(save_dir=str(tmp_path))
        assert mgr.get_all_progress() == {}

        # 3. Old backup intact
        assert bak_file.read_text(encoding="utf-8") == "old progress backup"

        # 4. New backup is progress.json.bak.1
        bak_file_1 = tmp_path / "progress.json.bak.1"
        assert bak_file_1.exists()
        assert bak_file_1.read_text(encoding="utf-8") == "{broken 2"

    def test_normal_operations_after_rebuild(self, tmp_path):
        """Test that we can safely save records normally after a corrupted rebuild."""
        progress_file = tmp_path / "progress.json"
        progress_file.write_text("{broken json", encoding="utf-8")

        mgr = SaveManager(save_dir=str(tmp_path))

        # Perform save normally
        is_record = mgr.update_level_progress(
            "Level 1", moves=12, time_seconds=15.0, pushes=4
        )
        assert is_record is True

        progress = mgr.get_level_progress("Level 1")
        assert progress["completed"] is True
        assert progress["best_moves"] == 12

        # Verify it was correctly written to the rebuilt progress.json file
        with open(progress_file, encoding="utf-8") as f:
            data = json.load(f)
        assert "Level 1" in data
        assert data["Level 1"]["best_moves"] == 12


# ---------------------------------------------------------------------------
# 3. Save and load progress
# ---------------------------------------------------------------------------


class TestSaveManagerProgress:
    """Test saving and loading progress data."""

    def test_update_creates_progress(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)

        progress = mgr.get_level_progress("Level 1")
        assert progress["completed"] is True
        assert progress["best_moves"] == 10
        assert progress["best_pushes"] == 5
        assert progress["attempts"] == 1

    def test_progress_persisted_to_file(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)

        # Create a new SaveManager pointing to same directory
        mgr2 = SaveManager(save_dir=str(tmp_path))
        progress = mgr2.get_level_progress("Level 1")
        assert progress["completed"] is True
        assert progress["best_moves"] == 10

    def test_lower_moves_overwrites_best(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        is_record = mgr.update_level_progress(
            "Level 1", moves=20, time_seconds=60.0, pushes=10
        )
        assert is_record is True  # First completion is always a record

        is_record = mgr.update_level_progress(
            "Level 1", moves=15, time_seconds=45.0, pushes=8
        )
        assert is_record is True  # 15 < 20

        progress = mgr.get_level_progress("Level 1")
        assert progress["best_moves"] == 15
        assert progress["best_pushes"] == 8

    def test_higher_moves_does_not_overwrite_best(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)

        is_record = mgr.update_level_progress(
            "Level 1", moves=20, time_seconds=60.0, pushes=10
        )
        assert is_record is False

        progress = mgr.get_level_progress("Level 1")
        assert progress["best_moves"] == 10  # Unchanged
        assert progress["best_pushes"] == 5  # Unchanged

    def test_attempts_increment(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)
        mgr.update_level_progress("Level 1", moves=20, time_seconds=60.0, pushes=10)
        mgr.update_level_progress("Level 1", moves=15, time_seconds=45.0, pushes=8)

        progress = mgr.get_level_progress("Level 1")
        assert progress["attempts"] == 3

    def test_multiple_levels_independent(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)
        mgr.update_level_progress("Level 2", moves=20, time_seconds=60.0, pushes=10)

        p1 = mgr.get_level_progress("Level 1")
        p2 = mgr.get_level_progress("Level 2")
        assert p1["best_moves"] == 10
        assert p2["best_moves"] == 20


# ---------------------------------------------------------------------------
# 4. High scores
# ---------------------------------------------------------------------------


class TestSaveManagerHighScores:
    """Test high score tracking."""

    def test_score_added_on_update(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)

        scores = mgr.get_high_scores("Level 1")
        assert len(scores) == 1
        assert scores[0]["moves"] == 10

    def test_scores_sorted_by_moves(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=20, time_seconds=60.0, pushes=10)
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)
        mgr.update_level_progress("Level 1", moves=15, time_seconds=45.0, pushes=8)

        scores = mgr.get_high_scores("Level 1", limit=10)
        assert len(scores) == 3
        assert scores[0]["moves"] == 10
        assert scores[1]["moves"] == 15
        assert scores[2]["moves"] == 20

    def test_scores_limited_to_10(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        for i in range(15):
            mgr.update_level_progress(
                "Level 1", moves=100 - i, time_seconds=float(i), pushes=i
            )

        # Internal storage is capped at 10
        all_scores = mgr.get_high_scores("Level 1", limit=20)
        assert len(all_scores) <= 10

    def test_get_high_scores_with_limit(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        for i in range(5):
            mgr.update_level_progress(
                "Level 1", moves=10 + i, time_seconds=float(i), pushes=i
            )

        scores = mgr.get_high_scores("Level 1", limit=3)
        assert len(scores) == 3


# ---------------------------------------------------------------------------
# 5. Completion stats
# ---------------------------------------------------------------------------


class TestSaveManagerCompletionStats:
    """Test overall completion statistics."""

    def test_completion_percentage(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)
        mgr.update_level_progress("Level 2", moves=20, time_seconds=60.0, pushes=10)

        stats = mgr.get_completion_stats()
        assert stats["total_levels"] == 2
        assert stats["completed"] == 2
        assert stats["percentage"] == 100.0


# ---------------------------------------------------------------------------
# 6. Reset
# ---------------------------------------------------------------------------


class TestSaveManagerReset:
    """Test progress reset."""

    def test_reset_clears_all(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)
        mgr.update_level_progress("Level 2", moves=20, time_seconds=60.0, pushes=10)

        mgr.reset_progress()

        assert mgr.get_all_progress() == {}
        assert mgr.get_high_scores("Level 1") == []
        assert mgr.get_high_scores("Level 2") == []

    def test_reset_persisted(self, tmp_path):
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)
        mgr.reset_progress()

        # New manager should see empty data
        mgr2 = SaveManager(save_dir=str(tmp_path))
        assert mgr2.get_all_progress() == {}


# ---------------------------------------------------------------------------
# 7. File isolation
# ---------------------------------------------------------------------------


class TestSaveManagerIsolation:
    """Verify tests don't write to real project data."""

    def test_uses_tmp_path(self, tmp_path):
        """Confirm SaveManager writes only within tmp_path."""
        mgr = SaveManager(save_dir=str(tmp_path))
        mgr.update_level_progress("Level 1", moves=10, time_seconds=30.0, pushes=5)

        # Verify files exist only in tmp_path
        assert (tmp_path / "progress.json").exists()
        assert (tmp_path / "scores.json").exists()

        # Verify content is valid JSON
        with open(tmp_path / "progress.json", encoding="utf-8") as f:
            data = json.load(f)
        assert "Level 1" in data
