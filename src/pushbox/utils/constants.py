"""Game constants and enumerations."""

from enum import IntEnum
from typing import Union

Color = tuple[int, int, int]
ColorWithAlpha = tuple[int, int, int, int]
ColorLike = Union[Color, ColorWithAlpha]


class CellType(IntEnum):
    """Cell types in the game grid."""

    EMPTY = 0
    WALL = 1
    TARGET = 2
    BOX = 3
    PLAYER = 4
    BOX_ON_TARGET = 5


class Direction:
    """Direction vectors."""

    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class GameState:
    """Game states."""

    PLAYING = "playing"
    WON = "won"
    GAME_OVER = "game_over"
    PAUSED = "paused"
    MENU = "menu"
    EDITOR = "editor"


class ControlScheme:
    """Control scheme types."""

    ARROWS = "arrows"  # ↑↓←→
    WASD = "wasd"  # WASD


# Game constants
CELL_SIZE = 50
ANIMATION_SPEED = 0.15  # seconds per cell movement
MAX_UNDO_HISTORY = 100

# Modern Color Palette (Dracula / Nord inspired)
COLORS: dict[str, ColorLike] = {
    # Backgrounds
    "background": (40, 44, 52),  # Dark Blue-Grey
    "grid_lines": (50, 54, 62),  # Slightly lighter
    "panel_bg": (33, 37, 43),  # Darker panel
    # Game Elements
    "wall": (97, 175, 239),  # Soft Blue
    "wall_shadow": (57, 115, 179),  # Darker Blue
    "floor": (40, 44, 52),  # Same as BG
    "floor_light": (45, 49, 57),  # Checkerboard pattern
    "target": (224, 108, 117),  # Soft Red
    "target_glow": (255, 150, 160),
    "box": (229, 192, 123),  # Soft Yellow/Gold
    "box_shadow": (189, 152, 83),
    "box_outline": (100, 80, 40),
    "box_on_target": (152, 195, 121),  # Soft Green
    "box_on_target_shadow": (112, 155, 81),
    "player": (198, 120, 221),  # Soft Purple
    "player_shadow": (158, 80, 181),
    # UI Elements
    "text_main": (220, 223, 228),  # Off-white
    "text_dim": (150, 150, 160),  # Grey text
    "text_highlight": (97, 175, 239),  # Blue text
    "button_default": (50, 54, 62),
    "button_hover": (70, 74, 82),
    "button_active": (97, 175, 239),
    "button_shadow": (30, 34, 42),
    "overlay": (0, 0, 0, 180),  # Semi-transparent black
    "success": (152, 195, 121),  # Green
    "warning": (229, 192, 123),  # Yellow
    "error": (224, 108, 117),  # Red
}

# Default level data (Unchanged)
DEFAULT_LEVELS = {
    "Level 1": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 2, 1, 1, 1, 1, 1],
        [1, 0, 2, 0, 4, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 3, 0, 1, 1, 1, 1],
        [1, 0, 3, 2, 0, 0, 0, 1, 1, 1],
        [1, 1, 1, 1, 0, 3, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 2": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 1, 1, 1, 1],
        [1, 0, 3, 3, 3, 1, 1, 1, 1],
        [1, 0, 0, 1, 2, 2, 1, 1, 1],
        [1, 1, 0, 0, 2, 2, 3, 0, 1],
        [1, 1, 0, 0, 0, 0, 4, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 3": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 1, 1],
        [1, 0, 0, 3, 0, 1, 0, 1, 1],
        [1, 0, 3, 0, 1, 0, 3, 0, 1],
        [1, 1, 3, 0, 3, 0, 3, 0, 1],
        [1, 1, 0, 0, 4, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 4": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 2, 0, 0, 4, 1],
        [1, 0, 0, 3, 3, 3, 0, 0, 1],
        [1, 2, 1, 1, 2, 1, 1, 2, 1],
        [1, 0, 0, 0, 3, 0, 0, 0, 1],
        [1, 0, 0, 3, 2, 1, 0, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 5": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 2, 0, 3, 1, 1, 0, 1, 1],
        [1, 2, 2, 3, 0, 3, 0, 4, 0, 1],
        [1, 2, 2, 0, 3, 0, 3, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 6": [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 2, 0, 0, 1],
        [1, 0, 0, 3, 3, 0, 0, 1],
        [1, 0, 0, 4, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 7": [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 2, 0, 0, 0, 0, 1],
        [1, 0, 3, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 4, 0, 3, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 8": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 2, 0, 2, 0, 2, 0, 1],
        [1, 0, 3, 0, 3, 0, 3, 0, 1],
        [1, 0, 0, 0, 4, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 9": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 2, 0, 2, 0, 0, 1],
        [1, 0, 0, 0, 3, 0, 3, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 4, 0, 3, 0, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 10": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 0, 2, 0, 0, 0, 1],
        [1, 0, 0, 3, 0, 3, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 3, 0, 3, 0, 0, 0, 1],
        [1, 0, 0, 2, 0, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 4, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
}
