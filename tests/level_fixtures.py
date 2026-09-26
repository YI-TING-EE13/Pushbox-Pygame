"""Helpers for small, isolated gameplay test boards."""


def with_isolated_objectives(grid: list[list[int]]) -> list[list[int]]:
    """Add a sealed box/goal room when a movement test omits valid objectives."""
    rows = [list(row) for row in grid]
    width = len(rows[0])
    targets = sum(value == 2 for row in rows for value in row)
    boxes = sum(value == 3 for row in rows for value in row)

    if targets == boxes and targets > 0:
        return rows

    if targets == 0 and boxes == 0:
        add_targets = 1
        add_boxes = 1
    else:
        add_targets = max(boxes - targets, 0)
        add_boxes = max(targets - boxes, 0)

    room_cells = [2] * add_targets + [3] * add_boxes
    room_width = max(width, len(room_cells) + 2, 5)
    for row in rows:
        row.extend([1] * (room_width - width))

    room = [1] * room_width
    room[1 : 1 + len(room_cells)] = room_cells
    rows.extend([[1] * room_width, room, [1] * room_width])
    return rows
