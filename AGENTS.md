# Pushbox-Pygame Agent Guide

Use this file to get productive quickly in a new coding session.

## Project Snapshot

Pushbox-Pygame is a modern Sokoban puzzle game built with Python and Pygame.
Current release: v0.9.3 (English + Traditional Chinese UI localization is complete).

- Entry point and main loop: `main.py`
- Controllers (game flow, input): `src/pushbox/controllers/`
- Models (level data, game state, saves): `src/pushbox/models/`
- Views (renderer, UI screens, editor): `src/pushbox/views/`
- Utilities (constants, config, audio stub): `src/pushbox/utils/`
- Built-in level grids and metadata: `src/pushbox/utils/constants.py`
- Tests: `tests/`
- Main development record and roadmap: `DEVELOPMENT.md`

## Current Product Direction

The next product goal is to elevate the app from a functional demo to a polished casual game.

Prioritize:

- Settings screen accessible from main menu and pause overlay.
- Config values actually wired to runtime behavior (window size, show_tutorial, animation toggle).
- Tutorial only on first launch; returning users go straight to menu.
- Completion progress indicator on the main menu (e.g., ★ 12/30).
- Maintain i18n completeness: no mixed-language UI on any single screen; keep translations in sync.
- Screen transition animations (fade/slide between screens).
- Dynamic cell sizing so large levels fit any window.
- Version number displayed on the main menu.

Audio is **intentionally deferred**. Keep the `AudioManager` stub and empty `assets/sounds/` as-is. Do not implement audio playback or source audio files unless the user explicitly requests it.

## Core Gameplay Rules

- Cell types: `EMPTY=0, WALL=1, TARGET=2, BOX=3, PLAYER=4, BOX_ON_TARGET=5`.
- Solved when every `TARGET` cell is occupied by a box (`BOX_ON_TARGET`).
- Player can push boxes but not pull them.
- Move direction is where the player walks, not where the box goes.
- `GameState.move(direction)` is a single-step move.
- Undo/redo uses the command pattern; history capped at 100 moves.
- Deadlock detection triggers `GAME_OVER` status when a box is stuck in an unsolvable corner.
- Reset restores the level to `initial_grid` and clears move history.
- Progress auto-saves on level completion; best records compare fewer moves first, then lower time.

## Working Style

- Communicate with the user in Chinese unless they ask otherwise.
- Write code comments, docstrings, README content, and development docs in clear English.
- Read existing code and `DEVELOPMENT.md` before implementing.
- Prefer small, coherent changes with focused verification.
- Use existing project patterns before adding abstractions.
- Update `DEVELOPMENT.md` for planning, roadmap, workflow, or behavior changes.
- Keep public/API behavior documented with English docstrings.
- Do not push to a remote unless the user explicitly asks.

## Verification Commands

Use `uv` as the primary workflow:

```bash
# Install dependencies
uv sync
uv sync --extra dev

# Run the game
uv run python main.py

# Run tests (always run before committing)
uv run pytest

# Run tests verbose
uv run pytest -v

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

Run the smallest relevant test set first, then broaden when changing shared behavior.

## Git Rules

- Git is initialized locally on branch `main`.
- Commit cohesive changes after implementation and verification.
- Do not rewrite history, reset, rebase, squash, or force-push unless explicitly requested.
- Do not track generated files, local saves, IDE files, or machine-specific config.
- `.gitignore` is part of the workflow and should remain respected.

Useful status checks:

```bash
git status --short
git log --oneline --decorate -5
```

## Code Style Guidelines

### Imports

- Group imports: stdlib → third-party → local.
- Use absolute imports.
- One import per line for clarity.

### Formatting

- 4 spaces for indentation.
- Max line length: 88 characters (Ruff default).
- Single quotes for strings unless double quotes needed.
- No trailing whitespace.
- One blank line between class methods.
- Two blank lines between top-level definitions.

### Naming Conventions

- Constants: `UPPER_CASE` (e.g., `CELL_SIZE`, `MAX_UNDO_HISTORY`).
- Classes: `PascalCase` (e.g., `GameState`, `LevelSelector`).
- Functions/Methods: `snake_case` (e.g., `find_player`, `load_level`).
- Variables: `snake_case` (e.g., `current_page`, `game_state`).
- Private methods: `_leading_underscore`.

### Types

- Use type hints for function parameters and return values.
- Use `Optional[]` for nullable values.
- Use built-in generics (`list[str]`, `dict[str, Any]`) — Python 3.9+ style.

### Error Handling

- Use explicit checks rather than try/except when possible.
- Validate array bounds before access.
- Use early returns for guard clauses.
- Avoid bare except clauses.

### Comments

- Minimal inline comments; prefer self-documenting code.
- Use English docstrings for classes and public methods.
- Explain "why" not "what" when comments are needed.

### Dependencies

- pygame: Window, input, and rendering.
- numpy: Array operations and level grid.
- copy: Deep copying for undo history.

## Architecture Notes

- `main.py` owns the `GameApp` class with the main loop, screen routing, and event dispatch.
- Screen state is tracked by `GameApp.current_screen` string: `"tutorial"`, `"menu"`, `"game"`, `"level_select"`, `"editor"`, `"settings"`.
- `GameController` manages game logic, input routing, pause, save/load, and level transitions.
- `Renderer` handles board drawing, overlays (win/pause/deadlock), and animations.
- `LevelSelector` manages paginated 3×3 grid of level cards with metadata badges.
- `LevelEditor` provides paint/erase tools, grid resizing, validation, and save.
- `Config` reads/writes `data/config.json`. All config values should be wired to runtime behavior.
- `SaveManager` persists `data/progress.json` and `data/scores.json`.
- Custom levels are stored as JSON files in `levels/`.

## Manual Smoke Tests

Run these after UI or gameplay changes.

### 1. Game Boot and Main Menu

- [ ] Launch with `uv run python main.py`. Confirm boot with zero console exceptions.
- [ ] First launch: tutorial screen appears. Press any key → menu.
- [ ] Menu shows all buttons with correct labels. Keyboard (↑↓/WS + Enter) and mouse both work.
- [ ] Completion progress indicator visible on menu (if implemented).

### 2. Settings Screen

- [ ] Open Settings from main menu. All toggles and controls render correctly.
- [ ] Change a setting; confirm it persists after returning to menu.
- [ ] Open Settings from pause overlay during gameplay.

### 3. Gameplay

- [ ] Start Level 1. Move with arrow keys and WASD.
- [ ] Undo (Z/Backspace), Redo (Y), Reset (F5/Delete) all function correctly.
- [ ] Push box onto target → turns green. All boxes on targets → win screen.
- [ ] Win screen shows stats. Press N for next level, R to replay, M for menu.
- [ ] Pause (Esc/P) → overlay freezes timer. Resume, Restart, Menu all work.
- [ ] Help (H/F1) → overlay shows controls. Any key dismisses.
- [ ] Trigger deadlock → "死鎖!" overlay. Undo (Z) recovers, R resets, M exits.

### 4. Level Selector

- [ ] 3×3 grid with pagination. Navigate with arrows/WASD + Enter.
- [ ] Page switching: Tab, Shift+Tab, PageUp, PageDown, nav buttons.
- [ ] Completed levels show ★ star. Selected level shows detail panel.
- [ ] Custom levels show 編輯/刪除 buttons.

### 5. Level Editor

- [ ] Open from menu. Paint with left-click, erase with right-click.
- [ ] Tool switching with keys 1-5 and sidebar clicks.
- [ ] Resize grid with +/- buttons (5-20 range).
- [ ] Save validates: player required, boxes == targets.
- [ ] Undo/Redo/Clear work correctly.
- [ ] Exit editor returns to menu.

## Files To Keep In Mind

- `DEVELOPMENT.md`: single source of truth for roadmap, UX analysis, TODO items, and session logs.
- `README.md`: user-facing project overview and usage.
- `RELEASE_NOTES.md`: version history and changelog.
- `main.py`: entry point, screen routing, event dispatch, and game loop.
- `src/pushbox/utils/constants.py`: cell types, colors, all 30 default level grids, and level metadata.
- `src/pushbox/utils/config.py`: config schema, load/save, and default values.
- `src/pushbox/views/ui_components.py`: Menu, TutorialScreen, LevelSelector, ModernButton, InputBox.
- `src/pushbox/views/renderer.py`: board rendering, overlays, and animation system.
- `src/pushbox/controllers/game_controller.py`: game flow, input callbacks, pause, save.
- `src/pushbox/models/game_state.py`: move/undo/redo command pattern, win/deadlock detection.

## Common Pitfalls

- Do not implement audio playback; keep `AudioManager` as a stub until explicitly requested.
- Do not add config values without wiring them to actual runtime behavior.
- Do not hardcode window dimensions; use `self.screen.get_width()` / `get_height()`.
- Do not hardcode `CELL_SIZE`; large levels on small windows will overflow.
- Do not mix Chinese and English in UI button labels; pick one language consistently.
- Do not let the tutorial show on every launch; respect the `show_tutorial` config flag.
- Do not break existing keyboard navigation; every screen must work with keyboard-only input.
- Do not commit `data/`, `levels/`, `.venv/`, `__pycache__/`, or cache directories.
- Do not duplicate game rules outside `GameState` and `Level` models.
- Do not change `DEFAULT_LEVELS` grid data without verifying solvability manually.
