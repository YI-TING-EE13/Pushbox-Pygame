# Pushbox-Pygame

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#🎮-for-players)
[![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green.svg)](#🎮-for-players)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-200+%20passing-green.svg)](#🛠️-for-developers)
[![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-black.svg)](#🛠️-for-developers)
[![Version](https://img.shields.io/badge/Version-v0.8.1--dev-orange.svg)](#-roadmap)

## Overview

Pushbox-Pygame is a modern Sokoban puzzle game built with Python and Pygame. It offers a clean, fluid interface, robust keyboard/mouse controls, local progression saving, options and configuration settings, an interactive solver hint system, PBX share code level imports/exports, and a built-in custom level editor.

## Screenshots / Demo

> [!NOTE]
> *Screenshots and gameplay recordings will be officially updated in the upcoming **v0.9.0** release alongside the pre-packaged Windows binary download.*

---

## Key Features

- **30 Built-in Levels**: High-quality hand-crafted levels of graduating difficulty, complete with difficulty, theme, and box count metadata badges in the Level Selector.
- **Interactive Onboarding (Level 0)**: A tutorial-only 5x7 introductory level automatically triggered on first-launch to guide new players through fundamental walking and pushing mechanics with dynamic instruction banners.
- **AI Solver & Hint Overlay**: Integrated a high-performance BFS shortest-action-path solver displaying a guided breathing path and grid highlight cues.
- **Level Sharing System**: Export custom maps from the editor or import them in the selector using `PBX_` prefixed compressed Base64 codes, guarded by an 8-point defense validation suite.
- **Settings Screen**: Accessible from the main menu or pause overlay, allowing real-time adjustment of screen dimensions, visual theme packs, tutorial flags, and transition animations.
- **Visual Theme Packs**: Real-time hot-swapping between "Nord Blue" (Aurora Ice), "Classic Green", and "Dracula Purple" modern sleek themes.
- **Level Selector**: Fully paginated grid selection displaying completion stars on cards and detailed level stats.
- **Fluid Controls**: Dual-scheme movement (Arrow keys and WASD) with smooth native menus and page navigation.
- **Undo / Redo / Reset**: Infinite-depth undo stack (capped at 100 moves for performance) with full action recovery and level reset capabilities.
- **In-Game Help & Pause Card**: DIM-shaded game pause overlay screen and help guide detailing controls on demand.
- **Stalemate & Deadlock Detection**: Real-time deadlock monitoring and immediate "死鎖!" card overlay feedback when a puzzle enters an unsolvable state.
- **Level Editor**: Built-in interactive map canvas supporting tool pickers (1-5), paint/erase, undo/redo, dynamic resizing (5x5 to 20x20), and canvas validation prior to local storage.
- **About / Credits Screen**: In-game credits screen displaying project version, license details, and open-source contributions.
- **Config / Save Hardening**: Bulletproof local save resilience with automatic `.bak` backups and active data integrity guards.
- **Runtime Path Helpers**: Pre-wired path resolution routing for future Windows standalone packaging readiness.

---

## 🎮 For Players

### Current Status

> [!IMPORTANT]
> **Packaged Windows binary (.exe) is not yet released; planned for v0.9.0.**
> Currently, the game is launched from source code and requires a local desktop Python environment.

### How to Run from Source for Now

To play the game, make sure you have **Python 3.9** (or newer) installed on your system.

1. **Clone or Download** this repository.
2. **Open a terminal** in the project root directory.
3. Install dependencies and start the game:
   ```bash
   # If using uv (recommended):
   uv run python main.py

   # If using standard Python virtual environment:
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -e .
   python main.py
   ```

### Controls

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
| | Return to Menu | `Esc` | Exits the selector back to the main menu screen |
| **In-Game** | Movement | Arrow keys or `WASD` | Moves the player character on the board |
| | Action Hint | `I` | Triggers AI solver to show the next critical steps |
| | Undo Move | `Z` or `Backspace` | Reverts the last player step or box push (up to 100 steps) |
| | Redo Move | `Y` or `R` | Re-applies the last undone step |
| | Reset Level | `F5` or `Delete` | Reverts the map to its starting state and resets timer |
| | Toggle Help | `H` or `F1` | Shows/hides the in-game control guide overlay card |
| | Dismiss Help | Any keypress | Immediately hides the help overlay card |
| | Pause Game | `Esc` or `P` | Enters pause mode; blocks inputs and freezes game timer |
| **Pause Screen**| Resume | `Esc` or `P` | Exits pause mode and resumes timer |
| | Restart | `R` | Restores starting map state and exits pause mode |
| | Menu Exit | `M` | Returns to the main menu |
| **Win Screen** | Next Level | `N` | Proceeds directly to the next level in sequence |
| | Restart | `R` | Restarts the current level to try for a better record |
| | Menu Exit | `M` | Returns to the main menu |
| **Stalemate** | Undo | `Z` or `Backspace` | Reverts the deadlock-inducing move to keep playing |
| | Restart | `R` or `F5` | Restarts the level |
| | Menu Exit | `M` | Returns to the main menu |
| **Level Editor**| Select Tool | `1` - `5` | Selects drawing tiles: Wall (1), Floor (2), Target (3), Box (4), Player (5) |
| | Mouse Draw | `Left Click` | Paints the selected tile onto the targeted grid cell |
| | Mouse Erase | `Right Click` | Clears/erases the targeted grid cell |
| | Undo Paint | `Z` | Undoes the last canvas modification step |
| | Redo Paint | `Y` or `R` | Redoes the last undone canvas modification step |
| | Clear Grid | `C` | Clears the entire drawing grid to start fresh |
| | Export Level | `E` | Generates a custom PBX share code to clipboard |
| | Save Map | `Ctrl+S` | Validates map layout rules and saves local custom level |
| | Exit Editor | `Esc` | Exits the editor and returns to the main menu |

### Custom Level Sharing Quick Guide

1. **Creating a level**: Go to the **Level Editor** from the main menu, paint your map, make sure it has exactly one player, and equal counts of boxes and targets.
2. **Exporting**: Click the `Export Level` button (or press `E`). A `PBX_` share code will be copied to your clipboard.
3. **Importing**: In the **Level Selector**, click `匯入關卡` (or press `I`). Paste your code to play custom levels immediately.
4. *Note*: **PBX_ sharing is a local text-code / clipboard exchange format, not an online level server.** No online server or network database is used.

---

## 🛠️ For Developers

### Prerequisites

- **Python**: `>=3.9` (matching configuration in `pyproject.toml`)
- **uv**: A fast Python package installer and manager (recommended).

### Setup

Clone the repository and synchronize the environment:

```bash
# Sync standard dependencies (Pygame, NumPy)
uv sync

# Sync development tools (pytest, ruff, mypy)
uv sync --extra dev
```

### Run the Game

Launch the application using `uv`:

```bash
uv run python main.py
```

### Test / lint / type check

Ensure code quality and run the automated test suite locally:

```bash
# Run the complete test suite (200+ tests)
uv run python -m pytest -v

# Run Ruff linter checks
uv run ruff check .

# Check Ruff formatting styling
uv run ruff format --check .

# Validate MyPy strict static typing
uv run python -m mypy src/ --explicit-package-bases
```

---

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
│   │   ├── level_share.py
│   │   └── paths.py
│   └── views/
│       ├── level_editor.py
│       ├── renderer.py
│       └── ui_components.py
├── tests/
│   ├── test_about.py
│   ├── test_game.py
│   ├── test_game_state.py
│   ├── test_input.py
│   ├── test_level.py
│   ├── test_level_share.py
│   ├── test_level_share_ui.py
│   ├── test_pause.py
│   ├── test_paths.py
│   ├── test_save_manager.py
│   └── test_solver.py
├── data/
└── examples/
```

---

## Configuration and Runtime Data

All user settings, progressions, high scores, and custom maps are stored locally and are excluded from git tracking:
- **`data/config.json`**: Standard settings (active visual theme, show_tutorial, screen resolution).
- **`data/progress.json`**: List of completed level names.
- **`data/scores.json`**: Level speedruns and push counts leaderboard.
- **`data/*.bak` repair backups**: Automated robust `.bak` backup files for progress and scores. In case of unexpected file corruption or parse failures, the system recovers data dynamically from these backup duplicates.
- **`levels/*.json`**: Custom levels exported and saved from the Level Editor.

> [!NOTE]
> The `data/` and `levels/` directories are dynamically created at runtime in the active workspace. When operating in future **packaged mode (.exe)**, all runtime configurations are saved relative to the directory containing the executable rather than internal temporary resource directories, maintaining full user save portability.

---

## Roadmap

- **v0.8.1 (Current)**: Release hardening (paths refactoring, config/save robustness, About screen, decoupled README).
- **v0.9.0 (Upcoming)**: Windows standalone packaging and release zips, official screenshots and recording updates.
- **v0.9.5**: Optional SFX activation (sound effects and ambient background music).
- **v1.0.0**: Stable official player-facing release.

---

## Requirements & Limitations

- **No Packed Windows Exe Yet**: Active Python environment is required for source execution.
- **Audio and BGM are not implemented yet**: Optional SFX is planned for v0.9.5. AudioManager currently contains stubs and does not emit audio.
- **PBX_ sharing is local only**: Custom levels are shared by transferring text codes manually; no central server hosting is present.
- **BFS Solver Shortest Action Path**: The solver provides a BFS shortest action path hint, not necessarily the minimum push-count solution. The search budget is capped at `50,000` nodes to keep the game UI responsive.

---

## Contributing

Contributions, bug reports, and features are welcome! Feel free to open issues or pull requests.

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## Credits / Acknowledgements

- **Python & Pygame**: For the robust game engine framework.
- **Open-source community**: Contributors and supporters of standard Python game architectures.
- *External Asset Credits*: Will be fully documented in this section before the official player-facing release.
