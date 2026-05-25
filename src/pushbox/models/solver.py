"""Sokoban pathfinding solver using Breadth-First Search (BFS).

This module implements a solver that computes the Shortest Action Path
(least number of player movements, i.e., walk and push steps) to solve
a given level. It does not guarantee the optimal number of box pushes.
"""

from collections import deque
from enum import Enum
from typing import Any, NamedTuple, Optional

import numpy as np

from ..utils.constants import CellType, Direction
from .level import Level

# Maximum number of unique generated states (nodes) during the BFS search.
# Configured as a module-level constant to prevent infinite search on complex levels.
MAX_SOLVER_NODES = 50_000


class SolverStatus(Enum):
    """The status outcome of the solver execution."""

    SOLVED = "solved"
    UNSOLVED = "unsolved"
    NODE_LIMIT_EXCEEDED = "node_limit_exceeded"
    INVALID_LEVEL = "invalid_level"


class SolverResult(NamedTuple):
    """Structure containing the result of a solver search."""

    status: SolverStatus
    path: Optional[list[tuple[int, int]]]
    nodes_explored: int


def is_dead_corner(
    pos: tuple[int, int],
    targets: set[tuple[int, int]],
    walls: set[tuple[int, int]],
    rows: int,
    cols: int,
) -> bool:
    """Determine if a grid position is a dead corner for a box.

    A position is a dead corner if:
    - It is not a target position.
    - It has wall/out-of-bounds obstacles on two adjacent perpendicular sides
      (e.g., both top and left are walls/out), making it impossible to move
      a box out of this position or push it to any target.

    Args:
        pos: The position (row, col) to check.
        targets: Set of target positions.
        walls: Set of static wall positions.
        rows: Total rows in grid.
        cols: Total columns in grid.

    Returns:
        True if the position is a dead corner, False otherwise.
    """
    if pos in targets:
        return False

    r, c = pos

    def is_blocked(nr: int, nc: int) -> bool:
        """Check if neighbor position is a wall or out of grid bounds."""
        return not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in walls

    up = is_blocked(r - 1, c)
    down = is_blocked(r + 1, c)
    left = is_blocked(r, c - 1)
    right = is_blocked(r, c + 1)

    # A box is stuck if blocked horizontally (left/right) AND vertically (up/down)
    if (up or down) and (left or right):
        return True

    return False


def parse_level(
    level_or_grid: Any,
) -> tuple[
    tuple[int, int],
    set[tuple[int, int]],
    set[tuple[int, int]],
    set[tuple[int, int]],
    int,
    int,
]:
    """Parse the level or grid state into structured positions with strict validation.

    Supports parsing from:
    1. A Level model instance (uses level.grid and level.initial_grid).
    2. A 2D list of integers.
    3. A 2D numpy array of integers.

    Performs defense checks:
    - Verifies grid is non-empty and rectangular (equal columns in all rows).
    - Verifies all cell values reside within the valid enum range [0, 5].
    - Verifies exactly one player exists.
    - Verifies targets exist.

    Args:
        level_or_grid: The game level representation.

    Returns:
        A tuple of:
        (player_pos, box_positions, target_positions, wall_positions, rows, cols)

    Raises:
        ValueError: If grid is invalid, missing elements, or dimensions are wrong.
    """
    # 1. Non-empty & Rectangular Checks (For list types)
    if isinstance(level_or_grid, list):
        if len(level_or_grid) == 0:
            raise ValueError("Grid cannot be empty.")
        first_len = len(level_or_grid[0])
        if first_len == 0:
            raise ValueError("Row cannot be empty.")
        if not all(
            isinstance(row, list) and len(row) == first_len for row in level_or_grid
        ):
            raise ValueError("Grid must be rectangular (non-jagged list).")

    # Adapt duck-typed Level or Numpy array
    if isinstance(level_or_grid, Level):
        grid = np.array(level_or_grid.grid)
        initial_grid = np.array(level_or_grid.initial_grid)
    elif hasattr(level_or_grid, "grid") and hasattr(level_or_grid, "initial_grid"):
        grid = np.array(level_or_grid.grid)
        initial_grid = np.array(level_or_grid.initial_grid)
    else:
        grid = np.array(level_or_grid)
        initial_grid = grid

    if grid.ndim != 2:
        raise ValueError("Grid must be a 2-dimensional array.")

    rows, cols = grid.shape
    if rows == 0 or cols == 0:
        raise ValueError("Grid size cannot be 0.")

    # 2. Strict Cell Value Verification [0, 5]
    for r in range(rows):
        for c in range(cols):
            val = grid[r, c]
            if not (0 <= val <= 5):
                raise ValueError(f"Invalid cell value {val} at ({r}, {c}).")

    # Parse static walls and targets (using initial_grid to avoid dynamic shifts)
    wall_positions = set()
    target_positions = set()

    for r in range(rows):
        for c in range(cols):
            init_val = initial_grid[r, c]
            if init_val == CellType.WALL:
                wall_positions.add((r, c))
            elif init_val in [CellType.TARGET, CellType.BOX_ON_TARGET]:
                target_positions.add((r, c))

    # Parse current player and boxes (using current grid)
    player_pos = None
    box_positions = set()

    for r in range(rows):
        for c in range(cols):
            val = grid[r, c]
            if val == CellType.PLAYER:
                if player_pos is not None:
                    raise ValueError("Multiple players detected.")
                player_pos = (r, c)
            elif val == CellType.BOX:
                box_positions.add((r, c))
            elif val == CellType.BOX_ON_TARGET:
                box_positions.add((r, c))
                # Fallback to ensure target is recorded
                target_positions.add((r, c))

    if player_pos is None:
        raise ValueError("No player detected.")

    if len(target_positions) < 1:
        raise ValueError("No targets detected.")

    return player_pos, box_positions, target_positions, wall_positions, rows, cols


def solve(
    level_or_grid: Any,
    max_nodes: int = MAX_SOLVER_NODES,
    pruning: bool = True,
) -> SolverResult:
    """Solve the Sokoban level finding the Shortest Action Path.

    Finds the shortest sequence of player action vectors (UP, DOWN, LEFT, RIGHT)
    using BFS.

    Detailed Max Node & Node Explored definition:
    - `max_nodes`: Limits the maximum number of unique generated states
      registered in the `visited` set. The check triggers at the beginning
      of each loop pop iteration (i.e. 'if len(visited) > max_nodes').
      For max_nodes=1, if the start state is not solved, expanding children will
      grow `len(visited)` and trigger the limit on the next loop, safely yielding
      NODE_LIMIT_EXCEEDED.
    - `nodes_explored`: Represents the total number of unique generated states
      accumulated in the `visited` set during search.

    Args:
        level_or_grid: A Level instance or 2D list/array representing the level.
        max_nodes: Maximum unique generated states to track before aborting.
        pruning: Set True to enable safe corner deadlock pruning on pushed box.

    Returns:
        A SolverResult tuple containing SolverStatus, the path of actions, and
        the number of explored unique generated states.
    """
    try:
        parsed = parse_level(level_or_grid)
        player_pos, box_positions, target_positions, wall_positions, rows, cols = parsed
    except Exception:
        return SolverResult(SolverStatus.INVALID_LEVEL, None, 0)

    # Basic validations
    if len(box_positions) < 1:
        return SolverResult(SolverStatus.INVALID_LEVEL, None, 0)
    if len(box_positions) != len(target_positions):
        return SolverResult(SolverStatus.INVALID_LEVEL, None, 0)

    # Define the target boxes state we want to achieve
    target_boxes = frozenset(target_positions)
    initial_boxes = frozenset(box_positions)

    # Edge case: Level is already solved
    if initial_boxes == target_boxes:
        return SolverResult(SolverStatus.SOLVED, [], 0)

    # State: (player_pos, box_positions_frozenset)
    start_state = (player_pos, initial_boxes)

    # BFS queues and visited sets
    # queue stores tuple: (state, path_so_far)
    queue: deque[
        tuple[tuple[tuple[int, int], frozenset[tuple[int, int]]], list[tuple[int, int]]]
    ] = deque([(start_state, [])])
    visited = {start_state}

    directions = [
        (Direction.UP, (-1, 0)),
        (Direction.DOWN, (1, 0)),
        (Direction.LEFT, (0, -1)),
        (Direction.RIGHT, (0, 1)),
    ]

    while queue:
        # Check node exploration limit (measured as unique generated states)
        if len(visited) > max_nodes:
            return SolverResult(SolverStatus.NODE_LIMIT_EXCEEDED, None, len(visited))

        (curr_player, curr_boxes), path = queue.popleft()

        for dir_val, (dr, dc) in directions:
            nr, nc = curr_player[0] + dr, curr_player[1] + dc

            # Wall and bounds check
            if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in wall_positions:
                continue

            # Push check
            if (nr, nc) in curr_boxes:
                nnr, nnc = nr + dr, nc + dc

                # Verify box can be pushed (not blocked by wall,
                # grid bounds, or another box)
                if (
                    not (0 <= nnr < rows and 0 <= nnc < cols)
                    or (nnr, nnc) in wall_positions
                    or (nnr, nnc) in curr_boxes
                ):
                    continue

                # Corner deadlock pruning (only performed when enabled)
                if pruning and is_dead_corner(
                    (nnr, nnc), target_positions, wall_positions, rows, cols
                ):
                    continue

                # State transition with push
                new_boxes = frozenset((curr_boxes - {(nr, nc)}) | {(nnr, nnc)})
                new_state = ((nr, nc), new_boxes)
            else:
                # Ordinary walk
                new_state = ((nr, nc), curr_boxes)

            if new_state not in visited:
                # Check for win condition
                if new_state[1] == target_boxes:
                    return SolverResult(
                        SolverStatus.SOLVED, path + [dir_val], len(visited) + 1
                    )

                visited.add(new_state)
                queue.append((new_state, path + [dir_val]))

    return SolverResult(SolverStatus.UNSOLVED, None, len(visited))
