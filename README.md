# PushBox

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-black.svg)

## Overview

PushBox is a modern Sokoban puzzle game built with Python and Pygame. It offers a clean, fluid interface, robust keyboard/mouse controls, local progression saving, and a built-in custom level editor.

## Key Features

- **Built-in Levels**: 20 pre-configured default levels of graduating difficulty, featuring concise difficulty, theme, and box count metadata badges visible in the Level Selector.
- **Modern Dark UI**: Fluid layout design with pseudo-3D wall shadows and elegant box animations.
- **Level Selector**: Fully paginated grid selection across 3 pages (9 levels per page) displaying a compact completion star on cards, with comprehensive metadata (difficulty, theme, box counts, description, and best moves record) rendered below the grid for the highlighted level.
- **Fluid Keyboard Controls**: Dual-scheme movement (Arrow keys and WASD), with native menus and page navigation.
- **Undo / Redo / Reset**: Infinite-depth undo stack (capped at 100 moves for performance) with full action recovery and level reset capabilities.
- **In-Game Help Card**: Fast-dismiss help card overlay detailing game controls on demand.
- **Pause System**: DIM-shaded game pause overlay screen that freezes gameplay state and time counters.
- **Stalemate Detection**: Real-time deadlock monitoring and immediate "死鎖!" card overlay feedback when a puzzle enters an unsolvable state.
- **Level Editor**: Built-in interactive map canvas supporting tool pickers (1-5), paint/erase, undo/redo, dynamic resizing (5x5 to 20x20), and canvas validation prior to local storage.
- **Progression Persistence**: Local progression auto-save capability tracking attempts and high scores.
- **Quality Assurance**: 100% passing test coverage suite verifying gameplay, inputs, editor, and save engines.

## Installation

This project utilizes `uv` to manage environments and dependencies smoothly.

```bash
# Sync dependencies
uv sync
uv sync --extra dev
```

## Usage

Start the game from the workspace root directory:

```bash
uv run python main.py
```

## Controls

| Category | Action | Key Shortcut | Notes / Interactions |
| --- | --- | --- | --- |
| **Global** | Quit Game | `Ctrl+Q` | Closes the application instantly from any screen |
| **Main Menu** | Navigation | `↑` / `↓` / `W` / `S` | Moves menu selection button highlights with visual feedback |
| | Activation | `Enter` / `Space` | Triggers the highlighted menu item action |
| **Selector** | Navigation | Arrow keys or `WASD` | Moves selectors in a 3x3 grid; auto-flips pages at bounds |
| | Prev Page | `PageUp` or `Shift+Tab` | Flips back to the previous page of levels |
| | Next Page | `PageDown` or `Tab` | Flips forward to the next page of levels |
| | Activation | `Enter` / `Space` | Selects and launches the highlighted level |
| | Return to Menu | `Esc` or `M` | Exits the selector back to the main menu screen |
| **In-Game** | Movement | Arrow keys or `WASD` | Moves the player character on the board |
| | Undo Move | `Z` or `Backspace` | Reverts the last player step or box push (up to 100 steps) |
| | Redo Move | `Y` or `R` | Re-applies the last undone step |
| | Reset Level | `F5` or `Delete` | Reverts the map to its starting state and resets timer |
| | Toggle Help | `H` or `F1` | Shows/hides the in-game control guide overlay card |
| | Dismiss Help | Any keypress | Immediately hides the help overlay card |
| | Pause Game | `Esc` or `P` | Enters pause mode; blocks inputs and freezes game timer |
| | Menu Exit | `M` | Returns to the main menu screen directly |
| **Pause Screen** | Resume | `Esc` or `P` | Exits pause mode and resumes timer |
| | Restart | `R` | Restores starting map state and exits pause mode |
| | Menu Exit | `M` | Returns to the main menu |
| **Win Screen** | Next Level | `N` | Proceeds directly to the next level in sequence |
| | Restart | `R` | Restarts the current level to try for a better record |
| | Menu Exit | `M` | Returns to the main menu |
| **Stalemate Screen**| Undo | `Z` or `Backspace` | Reverts the deadlock-inducing move to keep playing |
| | Restart | `R` or `F5` | Restarts the level |
| | Menu Exit | `M` | Returns to the main menu |
| **Level Editor** | Select Tool | `1` - `5` | Selects drawing tiles: Wall (1), Floor (2), Target (3), Box (4), Player (5) |
| | Mouse Draw | `Left Click` | Paints the selected tile onto the targeted grid cell |
| | Mouse Erase | `Right Click` | Clears/erases the targeted grid cell |
| | Undo Paint | `Z` | Undoes the last canvas modification step |
| | Redo Paint | `Y` or `R` | Redoes the last undone canvas modification step |
| | Clear Grid | `C` | Clears the entire drawing grid to start fresh |
| | Save Map | `Ctrl+S` | Validates map layout rules and saves local custom level |
| | Exit Editor | `Esc` | Exits the editor and returns to the main menu |

## Project Structure

```
pushbox/
├── main.py
├── pyproject.toml
├── README.md
├── TESTING.md
├── DEVELOPMENT.md
├── AGENTS.md
├── LEVEL_DESIGN.md
├── RELEASE_NOTES.md
├── src/pushbox/
│   ├── controllers/
│   │   ├── game_controller.py
│   │   └── input_handler.py
│   ├── models/
│   │   ├── game_state.py
│   │   ├── level.py
│   │   └── save_manager.py
│   ├── utils/
│   │   ├── audio.py
│   │   ├── config.py
│   │   └── constants.py
│   └── views/
│       ├── level_editor.py
│       ├── renderer.py
│       └── ui_components.py
├── tests/
│   ├── test_game.py
│   ├── test_game_state.py
│   ├── test_input.py
│   ├── test_level.py
│   ├── test_pause.py
│   └── test_save_manager.py
├── data/
└── examples/
```

## Quality Assurance & Testing

Run all standard quality assurance and unit tests locally:

```bash
# Run unit tests
uv run pytest -v

# Run linting rules
uv run ruff check .

# Check file formatting
uv run ruff format --check .

# Validate static typing
uv run mypy src/
```

## Limitations

- **Sokoban Solvability**: Automated testing checks grid layouts, level metadata consistency, and boundary integrity, but **does not mathematically prove or guarantee** that default or custom puzzles are solvable. Solvability must be validated manually. Difficulty labels are intended as lightweight player guidance and are not formal mathematical proofs of complexity.
- **Audio Stubs**: The audio manager contains stubs; full sound effects and ambient tracks are planned for future releases.
- **Undo History Limit**: Moves history is capped at 100 steps to maintain runtime performance and bounds memory footprint.
- **Local Progression Storage**: Player progress, statistics, and custom levels are saved locally in the `data/` and `levels/` directories and are omitted from version control.
- **Desktop Session Required**: Pygame requires an active display server session (X11, Wayland, or Windows Desktop) to initialize the graphical display.

## Future Development

- In-game options and configuration settings panel.
- Rich sound effects and custom music tracks.
- Online level sharing and cloud-sync achievements.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
