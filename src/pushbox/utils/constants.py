"""Game constants and enumerations."""

from enum import IntEnum
from typing import TypedDict, Union

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
    "Level 11": [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 2, 0, 0, 1],
        [1, 0, 1, 0, 3, 0, 0, 1],
        [1, 0, 4, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 3, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 12": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 2, 0, 0, 0, 1],
        [1, 0, 1, 0, 3, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 2, 0, 1],
        [1, 0, 4, 0, 3, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 13": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 2, 0, 2, 0, 0, 0, 1],
        [1, 0, 3, 3, 1, 0, 0, 0, 1],
        [1, 0, 0, 4, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 3, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 14": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 0, 2, 0, 0, 0, 1],
        [1, 0, 0, 3, 0, 3, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 0, 4, 0, 0, 0, 0, 1],
        [1, 0, 0, 3, 0, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 15": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 2, 0, 2, 0, 2, 0, 0, 1],
        [1, 0, 3, 0, 3, 0, 3, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 4, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 3, 0, 0, 0, 0, 1],
        [1, 0, 2, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 16": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 2, 2, 1],
        [1, 0, 3, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 3, 0, 1],
        [1, 1, 1, 0, 1, 1, 0, 0, 1],
        [1, 0, 0, 0, 4, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 17": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 0, 0, 1, 0, 0, 0, 2, 1],
        [1, 0, 3, 0, 1, 0, 3, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
        [1, 0, 0, 0, 4, 0, 0, 0, 0, 1],
        [1, 0, 0, 3, 0, 0, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 18": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 0, 0, 2, 0, 0, 1],
        [1, 0, 3, 0, 0, 1, 0, 3, 0, 1],
        [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 4, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
        [1, 0, 3, 0, 0, 1, 0, 3, 0, 1],
        [1, 0, 0, 2, 0, 0, 2, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 19": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 2, 1, 0, 0, 2, 0, 0, 1],
        [1, 0, 3, 0, 1, 0, 3, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 4, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 3, 0, 0, 1, 0, 3, 0, 1],
        [1, 0, 2, 0, 0, 0, 1, 0, 0, 2, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 20": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 2, 0, 0, 1, 0, 0, 2, 0, 1],
        [1, 0, 3, 0, 0, 1, 0, 3, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
        [1, 1, 0, 1, 0, 3, 0, 1, 0, 0, 1],
        [1, 0, 0, 1, 0, 4, 0, 1, 0, 0, 1],
        [1, 0, 2, 0, 0, 3, 0, 0, 3, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 2, 1],
        [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 21": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 4, 0, 0, 1, 0, 0, 2, 1],
        [1, 0, 3, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 0, 1, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 3, 0, 1, 0, 3, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 22": [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 4, 0, 1, 0, 2, 1],
        [1, 0, 3, 1, 3, 2, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 23": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 4, 0, 0, 0, 0, 2, 0, 2, 0, 1],
        [1, 0, 0, 3, 0, 0, 3, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 3, 0, 0, 3, 0, 0, 0, 1],
        [1, 0, 0, 2, 0, 0, 2, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 24": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 4, 0, 0, 1, 0, 2, 0, 1],
        [1, 0, 3, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 1, 0, 1, 3, 0, 1],
        [1, 1, 0, 1, 0, 1, 0, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 3, 0, 1, 0, 2, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
    "Level 25": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 4, 0, 0, 2, 0, 2, 0, 2, 0, 1],
        [1, 0, 0, 0, 3, 0, 3, 0, 3, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 3, 0, 0, 3, 0, 0, 1],
        [1, 0, 0, 0, 2, 0, 0, 2, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ],
}


class LevelMetadata(TypedDict):
    """Metadata dictionary schema for default built-in levels."""

    difficulty: str
    theme: str
    boxes: int
    note: str


DEFAULT_LEVEL_METADATA: dict[str, LevelMetadata] = {
    "Level 1": {
        "difficulty": "Intro",
        "theme": "Basic Route",
        "boxes": 3,
        "note": "Introduces movement, pushing, and target matching.",
    },
    "Level 2": {
        "difficulty": "Intro",
        "theme": "Cluster Pushes",
        "boxes": 4,
        "note": "Uses grouped boxes and nearby targets.",
    },
    "Level 3": {
        "difficulty": "Intro+",
        "theme": "Target Row",
        "boxes": 6,
        "note": "Practices organizing several boxes toward a shared target area.",
    },
    "Level 4": {
        "difficulty": "Intermediate",
        "theme": "Blocked Center",
        "boxes": 5,
        "note": "Adds wall-separated lanes and more careful ordering.",
    },
    "Level 5": {
        "difficulty": "Intermediate",
        "theme": "Compact Cluster",
        "boxes": 5,
        "note": "Uses a denser room with multiple nearby targets.",
    },
    "Level 6": {
        "difficulty": "Intro",
        "theme": "Twin Push",
        "boxes": 2,
        "note": "Simple two-box alignment practice.",
    },
    "Level 7": {
        "difficulty": "Intro+",
        "theme": "Split Targets",
        "boxes": 2,
        "note": "Introduces separated goals across a wider room.",
    },
    "Level 8": {
        "difficulty": "Intro+",
        "theme": "Three Columns",
        "boxes": 3,
        "note": "Practices repeated vertical alignment with three boxes.",
    },
    "Level 9": {
        "difficulty": "Intermediate",
        "theme": "Obstacle Spacing",
        "boxes": 3,
        "note": "Adds simple interior walls that affect positioning.",
    },
    "Level 10": {
        "difficulty": "Intermediate",
        "theme": "Four-Box Grid",
        "boxes": 4,
        "note": "Combines vertical push lanes with a larger open space.",
    },
    "Level 11": {
        "difficulty": "Intermediate",
        "theme": "Offset Goals",
        "boxes": 2,
        "note": "Uses separated boxes and targets with interior obstruction.",
    },
    "Level 12": {
        "difficulty": "Intermediate",
        "theme": "Staggered Paths",
        "boxes": 2,
        "note": "Requires navigating around staggered wall positions.",
    },
    "Level 13": {
        "difficulty": "Intermediate+",
        "theme": "Tight Cluster",
        "boxes": 3,
        "note": "Places boxes close together near blocked lanes.",
    },
    "Level 14": {
        "difficulty": "Advanced",
        "theme": "Lane Control",
        "boxes": 3,
        "note": "Uses separated lanes and interior walls to constrain movement.",
    },
    "Level 15": {
        "difficulty": "Advanced",
        "theme": "Mixed Columns",
        "boxes": 4,
        "note": "Combines multiple vertical lanes with central positioning.",
    },
    "Level 16": {
        "difficulty": "Advanced",
        "theme": "L-Corridor",
        "boxes": 2,
        "note": "Focuses on turning movement and angled access routes.",
    },
    "Level 17": {
        "difficulty": "Advanced",
        "theme": "Split Warehouse",
        "boxes": 3,
        "note": "Uses left and right sections connected through shared space.",
    },
    "Level 18": {
        "difficulty": "Advanced",
        "theme": "Central Island",
        "boxes": 4,
        "note": "Uses a central obstacle island to shape approach routes.",
    },
    "Level 19": {
        "difficulty": "Advanced+",
        "theme": "Small Rooms",
        "boxes": 4,
        "note": "Uses narrow doors and separated rooms to constrain order.",
    },
    "Level 20": {
        "difficulty": "Advanced+",
        "theme": "Mixed Warehouse",
        "boxes": 5,
        "note": "Combines multiple boxes, wall segments, and target regions.",
    },
    "Level 21": {
        "difficulty": "Advanced",
        "theme": "Long Reposition Route",
        "boxes": 3,
        "note": "Requires traveling long loops to steer boxes from behind.",
    },
    "Level 22": {
        "difficulty": "Advanced",
        "theme": "Two-Box Ordering Lock",
        "boxes": 2,
        "note": "Uses a single-column corridor exit where box order affects access.",
    },
    "Level 23": {
        "difficulty": "Advanced+",
        "theme": "Three-Zone Warehouse",
        "boxes": 4,
        "note": "Connects three chambers in sequence for multi-stage box transfers.",
    },
    "Level 24": {
        "difficulty": "Advanced+",
        "theme": "Narrow Door Recovery",
        "boxes": 3,
        "note": "Uses tight door frames that require careful recovery positioning.",
    },
    "Level 25": {
        "difficulty": "Advanced+",
        "theme": "Mixed Final Challenge",
        "boxes": 5,
        "note": "Combines routing loops, ordering locks, and narrow doorway planning.",
    },
}
