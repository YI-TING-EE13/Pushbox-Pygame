# Agent Guidelines for Pushbox-Pygame

This repository contains a Sokoban puzzle game implemented in Python with Pygame.

## Build/Lint/Test Commands

Use `uv` as the primary workflow:

```bash
# Install dependencies
uv sync
uv sync --extra dev

# Run the game
uv run python main.py

# Run tests
uv run pytest

# Lint / format
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src/
```

Fallback (when `uv` is unavailable):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python main.py
```

## Code Style Guidelines

### Imports
- Group imports: stdlib → third-party → local
- Use absolute imports
- One import per line for clarity

Example:
```python
import copy

import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
import ipywidgets as widgets
```

### Formatting
- 4 spaces for indentation
- Max line length: 88 characters (Black/Ruff default)
- Single quotes for strings unless double quotes needed
- No trailing whitespace
- One blank line between class methods
- Two blank lines between top-level definitions

### Naming Conventions
- Constants: `UPPER_CASE` (e.g., `FREE`, `WALL`, `BOX_ON_TARGET`)
- Classes: `PascalCase` (e.g., `SokobanGame`)
- Functions/Methods: `snake_case` (e.g., `find_player`, `check_game_over`)
- Variables: `snake_case` (e.g., `current_map`, `game_over`)
- Private methods: `_leading_underscore` optional

### Types
- Use type hints for function parameters and return values
- Use `Optional[]` for nullable values
- Use `List[]`, `Dict[]` from `typing` module for complex types

Example:
```python
from typing import Tuple, Optional, Dict, List

def find_player(self) -> Tuple[int, int]:
def load_level(self, level_name: str) -> None:
```

### Error Handling
- Use explicit checks rather than try/except when possible
- Validate array bounds before access
- Use early returns for guard clauses
- Avoid bare except clauses

Example:
```python
if not (0 <= nr < self.current_map.shape[0]):
    return
cell = self.current_map[nr, nc]
```

### Code Structure
- Keep functions focused and single-purpose
- Use list/dict literals directly (no unnecessary constructors)
- Use `copy.deepcopy()` for mutable object copying
- Prefer concise conditional expressions for simple assignments

### Game Constants
```python
FREE, WALL, TARGET, BOX, PLAYER, BOX_ON_TARGET = 0, 1, 2, 3, 4, 5
```

### Widget Event Handlers
- Use descriptive lambda names or named functions
- Button callbacks accept unused parameter with `_` convention

Example:
```python
undo.on_click(game.undo)
up.on_click(lambda x: game.move(-1, 0))
```

### Comments
- Minimal inline comments; prefer self-documenting code
- Use docstrings for class and method documentation
- Explain "why" not "what" when comments are needed

### Dependencies
- pygame: Window, input, and rendering
- numpy: Array operations and level grid
- copy: Deep copying for undo history

## Architecture Notes

- `main.py` provides the `GameApp` entry point and the main loop
- `src/pushbox/controllers/` contains game flow and input handling
- `src/pushbox/models/` contains level data and game state logic
- `src/pushbox/views/` contains renderer, UI screens, and level editor
- `src/pushbox/utils/` contains constants, config, and save helpers

## Development Workflow

1. Make changes in small, focused commits
2. Run `uv run pytest` before touching UI code
3. Keep rendering logic inside view classes
4. Preserve undo/redo behavior and history limits
5. Add type hints for public functions and core logic
