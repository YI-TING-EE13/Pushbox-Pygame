# PushBox

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Code%20Style](https://img.shields.io/badge/Code%20Style-Ruff-black.svg)

## Overview

PushBox is a modern Sokoban puzzle game built with Python and Pygame. It focuses
on a clean UI, keyboard-friendly controls, and a built-in level editor for custom
puzzles.

## Target Users / Use Cases

- Puzzle players who enjoy classic Sokoban mechanics
- Developers looking for a small, readable Pygame project
- Designers who want to build and test custom levels quickly

## Key Features

- Modern dark UI with pseudo-3D wall and box rendering
- Resizable window with responsive layout
- Tutorial screen and in-game help overlay
- Undo/redo history (up to 100 steps) and level reset
- Move, push, and time statistics
- In-game pause overlay (Esc/P) with resume, restart, and menu options
- Level selector with per-level best move record
- Deadlock feedback overlay with recovery options
- Built-in level editor with mouse tools and shortcuts

## Installation

This project uses `uv` for dependency management.

```bash
uv sync
uv sync --extra dev
```

## Usage

```bash
uv run python main.py
```

## Controls

| Action | Keys | Notes |
| --- | --- | --- |
| Move | Arrow keys or WASD | In-game movement |
| Undo | Z or Backspace | Also available via UI button |
| Redo | Y or R | Also available via UI button |
| Reset level | F5 or Delete | Also available via UI button |
| Help overlay | H or F1 | In-game only |
| Pause | Esc or P | In-game only (Resume/Restart/Menu) |
| Menu | M | Returns to main menu |
| Next level | N | On win screen |
| Restart | R | On win screen |

Level editor shortcuts:

- 1-5: select tool (wall, floor, target, box, player)
- Left click: paint, Right click: erase
- Ctrl+S: save level, Z/Y: undo/redo, C: clear, Esc: exit

## Project Structure

```
pushbox/
├── main.py
├── pyproject.toml
├── src/pushbox/
│   ├── controllers/
│   ├── models/
│   ├── utils/
│   └── views/
├── levels/
├── data/
├── examples/
└── assets/
```

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy src/
```

## Testing and Code Quality

- Tests: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type check: `uv run mypy src/`

## Requirements and Limitations

- Python 3.9+ and Pygame 2.5+ required
- Audio is a stub (no sound output yet)
- Undo/redo history is capped at 100 moves
- Progress and score data are stored locally in `data/` and ignored by git
  (see `examples/` for sample formats)
- Settings shortcut is not implemented yet

## Future Work

- In-game settings screen
- Audio playback (music and sound effects)
- High score UI and history browser
- Additional built-in levels and tutorial steps

## Contributing

Issues and pull requests are welcome. Please keep changes small and focused, and
run the test and lint commands before submitting.

## License

MIT License. See LICENSE.

## Acknowledgements

- Sokoban for the original puzzle concept
- Pygame and NumPy communities
