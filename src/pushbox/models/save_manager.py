"""Save data management for game progress and high scores."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, cast

ProgressValue = Optional[Union[int, float, bool]]
ProgressEntry = dict[str, ProgressValue]
ScoreValue = Union[str, int, float]
ScoreEntry = dict[str, ScoreValue]


class SaveManager:
    """Manages game save data and high scores."""

    def __init__(self, save_dir: str = "data") -> None:
        """Initialize save manager.

        Args:
            save_dir: Directory for save files.
        """
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.progress_file = self.save_dir / "progress.json"
        self.scores_file = self.save_dir / "scores.json"

        self.progress: dict[str, ProgressEntry] = {}
        self.scores: dict[str, list[ScoreEntry]] = {}

        self._load_progress()
        self._load_scores()

    def _backup_file(self, filepath: Path) -> None:
        """Safely backup a corrupted file with incrementing suffix."""
        if not filepath.exists():
            return
        import sys

        # Try .bak
        bak_path = filepath.with_suffix(filepath.suffix + ".bak")
        if not bak_path.exists():
            try:
                filepath.replace(bak_path)
                return
            except Exception as e:
                print(
                    f"Warning: Could not backup {filepath.name} to {bak_path}: {e}",
                    file=sys.stderr,
                )
                try:
                    import shutil

                    shutil.copy2(filepath, bak_path)
                    filepath.unlink()
                    return
                except Exception as e2:
                    print(
                        f"Warning: Fallback backup for {filepath.name} failed: {e2}",
                        file=sys.stderr,
                    )

        # Try .bak.1, .bak.2, etc.
        idx = 1
        while True:
            candidate = filepath.with_suffix(filepath.suffix + f".bak.{idx}")
            if not candidate.exists():
                try:
                    filepath.replace(candidate)
                    return
                except Exception as e:
                    print(
                        f"Warning: Could not backup {filepath.name} "
                        f"to {candidate}: {e}",
                        file=sys.stderr,
                    )
                    try:
                        import shutil

                        shutil.copy2(filepath, candidate)
                        filepath.unlink()
                        return
                    except Exception as e2:
                        print(
                            f"Warning: Fallback backup for "
                            f"{filepath.name} failed: {e2}",
                            file=sys.stderr,
                        )
                break
            idx += 1

    def _load_progress(self) -> None:
        """Load progress data."""
        import sys

        if self.progress_file.exists():
            try:
                with open(self.progress_file, encoding="utf-8") as f:
                    raw = json.load(f)
                    if isinstance(raw, dict):
                        self.progress = cast(dict[str, ProgressEntry], raw)
                    else:
                        print(
                            "Warning: Progress file is not a dictionary. Rebuilding.",
                            file=sys.stderr,
                        )
                        self._backup_file(self.progress_file)
                        self.progress = {}
                        self._save_progress()
            except (json.JSONDecodeError, OSError) as e:
                print(
                    f"Warning: Could not load progress: {e}. Rebuilding.",
                    file=sys.stderr,
                )
                self._backup_file(self.progress_file)
                self.progress = {}
                self._save_progress()

    def _load_scores(self) -> None:
        """Load high scores."""
        import sys

        if self.scores_file.exists():
            try:
                with open(self.scores_file, encoding="utf-8") as f:
                    raw = json.load(f)
                    if isinstance(raw, dict):
                        self.scores = cast(dict[str, list[ScoreEntry]], raw)
                    else:
                        print(
                            "Warning: Scores file is not a dictionary. Rebuilding.",
                            file=sys.stderr,
                        )
                        self._backup_file(self.scores_file)
                        self.scores = {}
                        self._save_scores()
            except (json.JSONDecodeError, OSError) as e:
                print(
                    f"Warning: Could not load scores: {e}. Rebuilding.", file=sys.stderr
                )
                self._backup_file(self.scores_file)
                self.scores = {}
                self._save_scores()

    def _save_progress(self) -> None:
        """Save progress data."""
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"Warning: Could not save progress: {e}")

    def _save_scores(self) -> None:
        """Save high scores."""
        try:
            with open(self.scores_file, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"Warning: Could not save scores: {e}")

    def get_level_progress(self, level_name: str) -> ProgressEntry:
        """Get progress for a specific level.

        Args:
            level_name: Name of the level.

        Returns:
            Progress dictionary.
        """
        return self.progress.get(
            level_name,
            {
                "completed": False,
                "best_moves": None,
                "best_time": None,
                "best_pushes": None,
                "attempts": 0,
            },
        )

    def update_level_progress(
        self, level_name: str, moves: int, time_seconds: float, pushes: int
    ) -> bool:
        """Update progress after completing a level.

        Args:
            level_name: Level name.
            moves: Number of moves taken.
            time_seconds: Time taken in seconds.
            pushes: Number of pushes made.

        Returns:
            True if new record was set.
        """
        progress = self.get_level_progress(level_name)
        progress["completed"] = True
        attempts_value = progress.get("attempts")
        attempts_count = (
            int(attempts_value) if isinstance(attempts_value, (int, bool)) else 0
        )
        progress["attempts"] = attempts_count + 1

        is_new_record = False

        # Check if this is a new best
        if progress["best_moves"] is None or moves < progress["best_moves"]:
            progress["best_moves"] = moves
            is_new_record = True

        if progress["best_time"] is None or time_seconds < progress["best_time"]:
            progress["best_time"] = time_seconds

        if progress["best_pushes"] is None or pushes < progress["best_pushes"]:
            progress["best_pushes"] = pushes

        self.progress[level_name] = progress
        self._save_progress()

        # Add to high scores
        self._add_score(level_name, moves, time_seconds, pushes)

        return is_new_record

    def _add_score(
        self, level_name: str, moves: int, time_seconds: float, pushes: int
    ) -> None:
        """Add score to high scores list.

        Args:
            level_name: Level name.
            moves: Number of moves.
            time_seconds: Time taken.
            pushes: Number of pushes.
        """
        if level_name not in self.scores:
            self.scores[level_name] = []

        score_entry: ScoreEntry = {
            "date": datetime.now().isoformat(),
            "moves": moves,
            "time": time_seconds,
            "pushes": pushes,
        }

        self.scores[level_name].append(score_entry)

        # Keep only top 10 scores (sorted by moves)
        self.scores[level_name].sort(key=lambda x: (x["moves"], x["time"]))
        self.scores[level_name] = self.scores[level_name][:10]

        self._save_scores()

    def get_high_scores(self, level_name: str, limit: int = 5) -> list[ScoreEntry]:
        """Get high scores for a level.

        Args:
            level_name: Level name.
            limit: Maximum number of scores to return.

        Returns:
            List of high score entries.
        """
        return self.scores.get(level_name, [])[:limit]

    def get_all_progress(self) -> dict[str, ProgressEntry]:
        """Get all progress data.

        Returns:
            Dictionary with all progress.
        """
        return self.progress.copy()

    def get_completion_stats(self) -> dict[str, Union[int, float]]:
        """Get overall completion statistics.

        Returns:
            Statistics dictionary.
        """
        total = len(self.progress)
        completed = sum(1 for p in self.progress.values() if p.get("completed", False))

        return {
            "total_levels": total,
            "completed": completed,
            "percentage": (completed / total * 100) if total > 0 else 0,
        }

    def reset_progress(self) -> None:
        """Reset all progress."""
        self.progress = {}
        self.scores = {}
        self._save_progress()
        self._save_scores()
