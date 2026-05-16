"""Game state management with history for undo/redo."""

import time
from typing import Any, Optional

from ..utils.constants import MAX_UNDO_HISTORY, CellType
from ..utils.constants import GameState as GameStateEnum
from .level import Level


class MoveCommand:
    """Represents a move command for undo/redo."""

    def __init__(
        self,
        player_from: tuple[int, int],
        player_to: tuple[int, int],
        box_from: Optional[tuple[int, int]] = None,
        box_to: Optional[tuple[int, int]] = None,
    ) -> None:
        """Initialize move command.

        Args:
            player_from: Player start position.
            player_to: Player end position.
            box_from: Box start position (if pushed).
            box_to: Box end position (if pushed).
        """
        self.player_from = player_from
        self.player_to = player_to
        self.box_from = box_from
        self.box_to = box_to
        self.timestamp = time.time()

    def is_push(self) -> bool:
        """Check if this move involved pushing a box."""
        return self.box_from is not None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "player_from": self.player_from,
            "player_to": self.player_to,
            "box_from": self.box_from,
            "box_to": self.box_to,
            "timestamp": self.timestamp,
        }


class GameState:
    """Manages the current game state."""

    def __init__(self, level: Level) -> None:
        """Initialize game state.

        Args:
            level: Level to play.
        """
        self.level = level
        self.level.reset()
        self.status = GameStateEnum.PLAYING
        self.move_history: list[MoveCommand] = []
        self.redo_stack: list[MoveCommand] = []
        self.move_count = 0
        self.push_count = 0
        self.start_time = time.time()
        self.elapsed_time = 0.0

    def reset(self) -> None:
        """Reset game state."""
        self.level.reset()
        self.status = GameStateEnum.PLAYING
        self.move_history.clear()
        self.redo_stack.clear()
        self.move_count = 0
        self.push_count = 0
        self.start_time = time.time()
        self.elapsed_time = 0.0

    def update_time(self) -> None:
        """Update elapsed time."""
        if self.status == GameStateEnum.PLAYING:
            self.elapsed_time = time.time() - self.start_time

    def get_formatted_time(self) -> str:
        """Get formatted elapsed time string.

        Returns:
            Time string in MM:SS format.
        """
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def move(self, direction: tuple[int, int]) -> bool:
        """Execute a move in given direction.

        Args:
            direction: Direction tuple (dr, dc).

        Returns:
            True if move was successful.
        """
        if self.status != GameStateEnum.PLAYING:
            return False

        player_pos = self.level.get_player_position()
        if not player_pos:
            return False

        pr, pc = player_pos
        dr, dc = direction
        nr, nc = pr + dr, pc + dc
        nnr, nnc = pr + 2 * dr, pc + 2 * dc

        # Check bounds
        if not self.level.is_valid_position(nr, nc):
            return False

        cell = self.level.get_cell(nr, nc)

        # Determine what happens based on target cell
        if cell in [CellType.EMPTY, CellType.TARGET]:
            # Simple move
            self._execute_move(pr, pc, nr, nc)
            return True

        elif cell in [CellType.BOX, CellType.BOX_ON_TARGET]:
            # Try to push box
            if not self.level.is_valid_position(nnr, nnc):
                return False

            next_cell = self.level.get_cell(nnr, nnc)
            if next_cell in [CellType.EMPTY, CellType.TARGET]:
                self._execute_push(pr, pc, nr, nc, nnr, nnc)
                return True

        return False

    def _execute_move(self, pr: int, pc: int, nr: int, nc: int) -> None:
        """Execute a simple player move.

        Args:
            pr, pc: Player current position.
            nr, nc: Player new position.
        """
        # Record move
        command = MoveCommand((pr, pc), (nr, nc))
        self.move_history.append(command)
        self.redo_stack.clear()
        self.move_count += 1

        # Update grid
        self.level.set_cell(
            pr,
            pc,
            CellType.TARGET
            if self.level.initial_grid[pr, pc] == CellType.TARGET
            else CellType.EMPTY,
        )
        self.level.set_cell(nr, nc, CellType.PLAYER)

        # Trim history if too long
        if len(self.move_history) > MAX_UNDO_HISTORY:
            self.move_history.pop(0)

    def _execute_push(
        self, pr: int, pc: int, br: int, bc: int, nbr: int, nbc: int
    ) -> None:
        """Execute a push move.

        Args:
            pr, pc: Player position.
            br, bc: Box position.
            nbr, nbc: New box position.
        """
        # Record move
        command = MoveCommand((pr, pc), (br, bc), (br, bc), (nbr, nbc))
        self.move_history.append(command)
        self.redo_stack.clear()
        self.move_count += 1
        self.push_count += 1

        # Update grid
        self.level.set_cell(
            pr,
            pc,
            CellType.TARGET
            if self.level.initial_grid[pr, pc] == CellType.TARGET
            else CellType.EMPTY,
        )
        self.level.set_cell(br, bc, CellType.PLAYER)

        # Place box
        target_cell = self.level.get_cell(nbr, nbc)
        self.level.set_cell(
            nbr,
            nbc,
            CellType.BOX_ON_TARGET if target_cell == CellType.TARGET else CellType.BOX,
        )

        # Check win condition
        if self.level.is_complete():
            self.status = GameStateEnum.WON
        elif self.level.is_deadlocked():
            self.status = GameStateEnum.GAME_OVER

        # Trim history
        if len(self.move_history) > MAX_UNDO_HISTORY:
            self.move_history.pop(0)

    def undo(self) -> bool:
        """Undo last move.

        Returns:
            True if undo was successful.
        """
        if not self.move_history or self.status == GameStateEnum.WON:
            return False

        command = self.move_history.pop()
        self.redo_stack.append(command)

        # Restore player position
        self.level.set_cell(
            command.player_to[0],
            command.player_to[1],
            CellType.TARGET
            if self.level.initial_grid[command.player_to[0], command.player_to[1]]
            == CellType.TARGET
            else CellType.EMPTY,
        )
        self.level.set_cell(
            command.player_from[0], command.player_from[1], CellType.PLAYER
        )

        # Restore box if pushed
        if command.is_push() and command.box_from and command.box_to:
            self.level.set_cell(
                command.box_to[0],
                command.box_to[1],
                CellType.TARGET
                if self.level.initial_grid[command.box_to[0], command.box_to[1]]
                == CellType.TARGET
                else CellType.EMPTY,
            )
            self.level.set_cell(
                command.box_from[0],
                command.box_from[1],
                CellType.BOX_ON_TARGET
                if self.level.initial_grid[command.box_from[0], command.box_from[1]]
                == CellType.TARGET
                else CellType.BOX,
            )
            self.push_count -= 1

        self.move_count -= 1
        self.status = GameStateEnum.PLAYING
        return True

    def redo(self) -> bool:
        """Redo last undone move.

        Returns:
            True if redo was successful.
        """
        if not self.redo_stack or self.status == GameStateEnum.WON:
            return False

        command = self.redo_stack.pop()

        # Re-execute the move
        if command.is_push() and command.box_from and command.box_to:
            self._execute_push(
                command.player_from[0],
                command.player_from[1],
                command.box_from[0],
                command.box_from[1],
                command.box_to[0],
                command.box_to[1],
            )
        else:
            self._execute_move(
                command.player_from[0],
                command.player_from[1],
                command.player_to[0],
                command.player_to[1],
            )

        # Remove from history since _execute adds it
        self.move_history.pop()
        self.move_history.append(command)

        return True

    def get_stats(self) -> dict[str, Any]:
        """Get game statistics.

        Returns:
            Dictionary with game stats.
        """
        return {
            "moves": self.move_count,
            "pushes": self.push_count,
            "time": self.get_formatted_time(),
            "time_seconds": self.elapsed_time,
        }
