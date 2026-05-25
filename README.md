# Pushbox-Pygame

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://img.shields.io/badge/Tests-177%20passing-green.svg)
![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-black.svg)

## Overview

Pushbox-Pygame is a modern Sokoban puzzle game built with Python and Pygame. It offers a clean, fluid interface, robust keyboard/mouse controls, local progression saving, options and configuration settings, an interactive solver hint system, PBX share code level imports/exports, and a built-in custom level editor.

## Key Features

- **Interactive Onboarding (Level 0)**: A tutorial-only 5x7 introductory level automatically triggered on first-launch. Dynamic Chinese banners change in real-time according to player movement to teach fundamental walking and pushing. Progress is isolated from official high-scores.
- **Built-in Levels**: 30 pre-configured default levels of graduating difficulty, with the gameplay HUD clearly displaying the active level name. Concise difficulty, theme, and box count metadata badges are visible in the Level Selector.
- **AI Solver & Hint Overlay**: Integrated a high-performance BFS shortest-action-path solver (`I` key or HUD lightbulb button) displaying a Sin-wave breathing guided path and high-contrast pulse animations on the next critical grid cell for 1.5 seconds.
- **Level Sharing System**: Export custom maps from the editor or import them in the selector using `PBX_` prefixed compressed Base64 codes, guarded by an 8-point defense validation suite (exact single-player check, matching box/target counts, and secure walled perimeter enclosure).
- **Settings Screen**: Accessible from the main menu or pause overlay, allowing real-time adjustment of screen dimensions, visual theme packs, tutorial flags, and transition animations.
- **Visual Theme Packs**: Real-time hot-swapping between "Nord Blue" (Aurora Ice), "Classic Green", and "Dracula Purple" modern sleek themes.
- **Level Selector**: Fully paginated grid selection across 4 pages (9 levels per page) displaying a completion star on cards, with comprehensive metadata (difficulty, theme, box counts, description, and best moves record) rendered below the grid for the highlighted level.
- **Fluid Keyboard Controls**: Dual-scheme movement (Arrow keys and WASD), with native menus and page navigation.
- **Undo / Redo / Reset**: Infinite-depth undo stack (capped at 100 moves for performance) with full action recovery and level reset capabilities.
- **In-Game Help Card**: Fast-dismiss help card overlay detailing game controls on demand.
- **Pause System**: DIM-shaded game pause overlay screen that freezes gameplay state and time counters.
- **Stalemate Detection**: Real-time deadlock monitoring and immediate "死鎖!" card overlay feedback when a puzzle enters an unsolvable state.
- **Level Editor**: Built-in interactive map canvas supporting tool pickers (1-5), paint/erase, undo/redo, dynamic resizing (5x5 to 20x20), and canvas validation prior to local storage.
- **Progression Persistence**: Local progression auto-save capability tracking attempts and high scores.
- **Quality Assurance**: 177 automated pytest test cases, Ruff linting/formatting checks, and MyPy strict package typing.

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
| | Import Level | `I` button (bottom) | Triggers the Import dialog for custom PBX codes |
| | Activation | `Enter` / `Space` | Selects and launches the highlighted level |
| | Return to Menu | `Esc` or `M` | Exits the selector back to the main menu screen |
| **In-Game** | Movement | Arrow keys or `WASD` | Moves the player character on the board |
| | Action Hint | `I` | Triggers AI solver to show the next 3 steps (呼吸燈呼吸導引) |
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
| | Export Level | `E` | Generates a custom PBX share code to clipboard |
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
├── LEVEL_21_25_PLAN.md
├── RELEASE_NOTES.md
├── src/pushbox/
│   ├── controllers/
│   │   ├── game_controller.py
│   │   └── input_handler.py
│   ├── models/
│   │   ├── game_state.py
│   │   ├── level.py
│   │   ├── save_manager.py
│   │   └── solver.py
│   ├── utils/
│   │   ├── audio.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   └── level_share.py
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
│   ├── test_save_manager.py
│   ├── test_solver.py
│   ├── test_hint_ui.py
│   ├── test_level_share.py
│   └── test_level_share_ui.py
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
uv run mypy src/ --explicit-package-bases
```

## Limitations

- **BFS Solver Limits**: The lightbulb hint system provides the *shortest action path* for player steps, not necessarily the theoretically minimal push counts. The search budget is capped at `50,000` nodes (`MAX_SOLVER_NODES`) to guarantee UI responsiveness. Unsolved or excessively complex custom grids will display a conservative alert banner.
- **Audio Stubs**: The audio manager contains stubs; full sound effects and ambient tracks are planned for future major releases.
- **Undo History Limit**: Moves history is capped at 100 steps to maintain runtime performance and bounds memory footprint.
- **Local Progression Storage**: Player progress, statistics, and custom levels are saved locally in the `data/` and `levels/` directories and are omitted from version control.
- **Desktop Session Required**: Pygame requires an active display server session (X11, Wayland, or Windows Desktop) to initialize the graphical display.

## Future Development

- Rich sound effects and custom music tracks.
- Online cloud level sharing and global leaderboard achievements.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
