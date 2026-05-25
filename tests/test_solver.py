"""Automated unit tests for the Sokoban BFS solver core."""

import copy

import numpy as np

from src.pushbox.models.game_state import GameState
from src.pushbox.models.level import Level
from src.pushbox.models.solver import SolverStatus, is_dead_corner, solve


def verify_replay(initial_level: Level, path: list[tuple[int, int]]) -> bool:
    """Helper function to replay the action path on a GameState copy and verify victory.

    Args:
        initial_level: The starting Level object.
        path: The sequence of direction action tuples.

    Returns:
        True if all actions were valid and led to a won/completed state.
    """
    level_copy = copy.deepcopy(initial_level)
    state = GameState(level_copy)

    for action in path:
        success = state.move(action)
        if not success:
            return False

    return state.level.is_complete()


def test_level_0_solvable() -> None:
    """Test that Onboarding Level 0 is solvable and successfully replayed."""
    level_0_grid = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 4, 0, 0, 3, 2, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    level = Level("Level 0 Test", level_0_grid)

    result = solve(level)
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None
    assert len(result.path) > 0

    # Ensure path replay leads to successful completion
    assert verify_replay(level, result.path)


def test_simple_5x5_single_box() -> None:
    """Test a simple 5x5 custom map with 1 box and a push action."""
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 0, 0, 1],
        [1, 0, 3, 2, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    level = Level("Simple 5x5", grid)

    result = solve(level)
    assert result.status == SolverStatus.SOLVED
    assert result.path is not None

    # Replay verification
    assert verify_replay(level, result.path)

    # Confirm solver did not mutate the original level grids
    assert np.array_equal(level.grid, level.initial_grid)


def test_unsolvable_level() -> None:
    """Test that a clearly unsolvable layout returns UNSOLVED."""
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 0, 1, 1],
        [1, 0, 0, 3, 1],
        [1, 0, 1, 2, 1],
        [1, 1, 1, 1, 1],
    ]
    level = Level("Unsolvable Test", grid)

    result = solve(level)
    assert result.status == SolverStatus.UNSOLVED
    assert result.path is None


def test_invalid_level_scenarios() -> None:
    """Test that invalid layout inputs correctly return INVALID_LEVEL."""
    # Scenario A: No player
    no_player = [
        [1, 1, 1],
        [1, 3, 2],
        [1, 1, 1],
    ]
    assert solve(no_player).status == SolverStatus.INVALID_LEVEL

    # Scenario B: Multiple players
    multi_player = [
        [1, 1, 1, 1],
        [1, 4, 4, 1],
        [1, 3, 2, 1],
        [1, 1, 1, 1],
    ]
    assert solve(multi_player).status == SolverStatus.INVALID_LEVEL

    # Scenario C: Box and Target mismatch (boxes = 2, targets = 1)
    mismatch = [
        [1, 1, 1, 1, 1],
        [1, 4, 3, 2, 1],
        [1, 0, 3, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    assert solve(mismatch).status == SolverStatus.INVALID_LEVEL

    # Scenario D: Zero boxes
    zero_boxes = [
        [1, 1, 1, 1],
        [1, 4, 2, 1],
        [1, 1, 1, 1],
    ]
    assert solve(zero_boxes).status == SolverStatus.INVALID_LEVEL

    # Scenario E: Non-rectangular jagged list
    jagged_list = [
        [1, 1, 1, 1],
        [1, 4, 2],  # jagged row
        [1, 1, 1, 1],
    ]
    assert solve(jagged_list).status == SolverStatus.INVALID_LEVEL

    # Scenario F: Empty grid
    empty_grid = []  # type: list
    assert solve(empty_grid).status == SolverStatus.INVALID_LEVEL

    # Scenario G: Invalid cell value (e.g. 99)
    invalid_value = [
        [1, 1, 1, 1],
        [1, 4, 99, 1],  # 99 is invalid
        [1, 3, 2, 1],
        [1, 1, 1, 1],
    ]
    assert solve(invalid_value).status == SolverStatus.INVALID_LEVEL

    # Scenario H: No targets
    no_targets = [
        [1, 1, 1, 1],
        [1, 4, 3, 1],  # 3 is BOX, but no targets exist
        [1, 1, 1, 1],
    ]
    assert solve(no_targets).status == SolverStatus.INVALID_LEVEL


def test_node_limit_exceeded() -> None:
    """Test that limiting max_nodes triggers NODE_LIMIT_EXCEEDED."""
    grid = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 4, 0, 0, 0, 0, 1],
        [1, 0, 1, 3, 1, 2, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    level = Level("Node Limit Test", grid)

    # With max_nodes=2, the search will hit the limit immediately
    result = solve(level, max_nodes=2)
    assert result.status == SolverStatus.NODE_LIMIT_EXCEEDED
    assert result.path is None
    assert result.nodes_explored >= 2


def test_box_on_target_parsing() -> None:
    """Test that BOX_ON_TARGET (5) layouts parse and solve without crashing."""
    grid = [
        [1, 1, 1, 1, 1],
        [1, 4, 0, 0, 1],
        [1, 0, 5, 0, 1],  # 5 is BOX_ON_TARGET
        [1, 1, 1, 1, 1],
    ]
    result = solve(grid)
    # Already solved since the only box is already on the only target
    assert result.status == SolverStatus.SOLVED
    assert result.path == []


def test_dead_corner_helper() -> None:
    """Test dead corner identification functionality."""
    # Simple 5x5 room with borders
    walls = {
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (1, 0),
        (1, 4),
        (2, 0),
        (2, 4),
        (3, 0),
        (3, 4),
        (4, 0),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
    }
    targets = {(3, 3)}
    rows, cols = 5, 5

    # (1, 1) is a corner: bounded by top wall (0, 1) and left wall (1, 0).
    # Since it is not a target, it should be a dead corner.
    assert is_dead_corner((1, 1), targets, walls, rows, cols) is True

    # (1, 2) is not a corner: only bounded by top wall (0, 2). Left/right are open.
    assert is_dead_corner((1, 2), targets, walls, rows, cols) is False

    # (2, 2) is not a corner: it has no adjacent walls.
    assert is_dead_corner((2, 2), targets, walls, rows, cols) is False

    # (3, 3) is a corner: bounded by bottom wall (4, 3) and right wall (3, 4).
    # However, it IS a target position, so it must NOT be identified as a dead corner.
    assert is_dead_corner((3, 3), targets, walls, rows, cols) is False


def test_box_on_target_fully_or_partially_solved() -> None:
    """Test that BOX_ON_TARGET (5) is treated as BOTH a box and a target.

    We verify two scenarios:
    1. Fully starting solved (all targets occupied by BOX_ON_TARGET).
    2. Partially solved (one box on target, another box not on target).
    """
    # Scenario 1: Fully solved initially
    fully_solved = [
        [1, 1, 1, 1, 1],
        [1, 4, 5, 5, 1],  # two boxes already on targets
        [1, 1, 1, 1, 1],
    ]
    res1 = solve(fully_solved)
    assert res1.status == SolverStatus.SOLVED
    assert res1.path == []

    # Scenario 2: Partially solved initially
    partially_solved = [
        [1, 1, 1, 1, 1, 1],
        [1, 4, 3, 0, 2, 1],  # 3 is free box, 2 is target
        [1, 1, 1, 5, 1, 1],  # 5 is box_on_target
        [1, 1, 1, 1, 1, 1],
    ]
    level = Level("Partially Solved", partially_solved)
    res2 = solve(level)
    assert res2.status == SolverStatus.SOLVED
    assert res2.path is not None
    # Replay must successfully solve the puzzle
    assert verify_replay(level, res2.path)


def test_corner_pruning_target_vs_non_target() -> None:
    """Test that corner pruning is extremely conservative.

    - Pushing a box to a target corner is a VALID/REQUIRED path, so corner pruning
      MUST NOT prune it (level should be SOLVED).
    - Pushing a box to a non-target corner is INVALID/DEADLOCKED, so corner pruning
      MUST block it (meaning if that was the only route, the solver should
      return UNSOLVED).
    """
    # Target corner: Box must be pushed to (1, 1) which is a target and corner.
    # 1 1 1
    # 1 T 1  <- T at (1, 1) is a corner
    # 1 B 1
    # 1 P 1
    # 1 1 1
    target_corner = [
        [1, 1, 1],
        [1, 2, 1],  # target at (1, 1)
        [1, 3, 1],  # box at (2, 1)
        [1, 4, 1],  # player at (3, 1)
        [1, 1, 1],
    ]
    level_tc = Level("Target Corner", target_corner)
    res_tc = solve(level_tc, pruning=True)
    assert res_tc.status == SolverStatus.SOLVED
    assert verify_replay(level_tc, res_tc.path)

    # Non-target corner: Box must be pushed to (1, 1) which is NOT a target.
    # Target is elsewhere (3, 1), but player can only push box UP into (1, 1).
    # 1 1 1
    # 1 . 1  <- (1, 1) is non-target corner
    # 1 B 1
    # 1 P 1
    # 1 T 1  <- target is at (4, 1), but box can never go down because player is there
    # 1 1 1
    non_target_corner = [
        [1, 1, 1],
        [1, 0, 1],  # empty at (1, 1)
        [1, 3, 1],  # box at (2, 1)
        [1, 4, 1],  # player at (3, 1)
        [1, 2, 1],  # target at (4, 1)
        [1, 1, 1],
    ]
    level_ntc = Level("Non-Target Corner", non_target_corner)
    res_ntc = solve(level_ntc, pruning=True)
    # The only push option is pushing the box into the corner (1, 1) which deadlocks,
    # so with pruning enabled, it should return UNSOLVED.
    assert res_ntc.status == SolverStatus.UNSOLVED
