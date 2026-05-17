# Testing Guide for PushBox

This document outlines the testing procedures for the PushBox project, including automated checks and manual smoke tests.

## 1. Automated Checks

Before submitting changes, ensure all automated quality gates pass. We use `uv` to manage the environment and run these commands.

```bash
# Run all unit tests
uv run pytest -v

# Run linting and style checks
uv run ruff check .

# Check code formatting
uv run ruff format --check .

# Run static type checking
uv run mypy src/
```

## 2. Manual Smoke Test

Since this is a graphical game, many UX elements must be verified manually. Follow these steps to ensure the core game loop is functional.

### Core Gameplay Flow
1. **Startup**: Run `uv run python main.py`.
2. **Tutorial**: Verify the tutorial screen appears on first launch or via the menu. Confirm it explains goals and controls.
3. **Main Menu**: Navigate from the tutorial to the main menu.
4. **Resize Centering**: Drag and resize the game window vertically and horizontally. Verify that the main menu buttons dynamically reposition to maintain a centered layout.
5. **Start Game**: Select "開始遊戲" and verify the level loads.
6. **Movement**: Test movement using both **Arrow Keys** and **WASD**.
7. **Pushing**: Push a box and verify it moves.
8. **Undo**: Move or push, then press `Z` or `Backspace`. Verify the state reverts correctly.
9. **Redo**: After undoing, press `Y` or `R`. Verify the action is reapplied.
10. **Reset**: Press `F5` or `Delete`. Verify the level restores to its initial state.
11. **Help Overlay**: Press `H` during gameplay. Verify the help card appears and correctly lists controls.
12. **Return to Menu**: Press `M` during gameplay or after winning. Verify it returns to the main menu.

### Win & Game Over Conditions
12. **Win Condition**: Push all boxes onto targets. Verify the green "MISSION COMPLETE!" overlay appears.
13. **Win Screen Actions**: Test `N` (Next Level), `R` (Restart), and `M` (Menu) on the win screen.
14. **Deadlock (Game Over)**: Push a box into a corner where it cannot be moved (e.g., against two perpendicular walls).
15. **Game Over Overlay**: Verify the red "死鎖!" card appears.
16. **Game Over Actions**: Test `Z` (Undo), `R` (Restart), and `M` (Menu) on the game over screen.

### UI & Persistence
17. **Level Selection**: From the main menu, go to "選擇關卡". Verify all levels are listed.
18. **Progress Display**: Verify that completed levels show a green background and a "★ 最佳: X 步" indicator.
19. **Persistence**: Complete a level, exit the game, and restart. Verify that your progress and best moves are still saved.

### Pause Screen Overlay
20. **Triggering Pause**: Start a game, then press `Esc` or `P` during standard gameplay. Verify the yellow "暫停" card appears and the background game board is dimmed behind the semi-transparent overlay.
21. **Gameplay Blocked**: While paused, try pressing movement keys or action buttons. Confirm that the player does not move, boxes cannot be pushed, and the game timer is completely frozen (does not increment).
22. **Overlay Keys**: Verify the three available actions listed on the pause card work as expected:
    - **Esc / P**: Continues gameplay exactly from the current state (timer resumes without jumping forward by the duration of the pause).
    - **R**: Resets the level state and immediately exits the pause screen to playing mode.
    - **M**: Safely exits the game screen back to the main menu (clearing the pause state).
23. **Priority of Overlays**:
    - **Help priority**: If the help overlay (`H`) is open, pressing `Esc` should close the help card instead of triggering the pause overlay.
    - **Ignore trigger**: Pressing `Esc` or `P` must have no effect when the green "Win" screen or the red "Deadlock" screen is active.

## 3. Editor Manual Test

The level editor allows creating and managing custom puzzles.

1. **Tool Selection**: Use keys `1-5` or click sidebar buttons to select tools (Wall, Floor, Target, Box, Player).
2. **Painting**: Left-click on the grid to place the selected element.
3. **Erasing**: Right-click on the grid to clear a cell.
4. **Validation**:
   - Try to save a level without a player.
   - Try to save a level without boxes.
   - Try to save a level where the number of boxes does not match the number of targets.
   - **Verify**: Clear error messages appear in the status bar.
5. **Sidebar Layout & Hints**: Confirm that all 6 lines of shortcut hints (左鍵/右鍵, 1-5, Z/Y/R, Ctrl+S, C, Esc) are visible on the default window size (800x720) without overlapping other controls (note: on extremely small heights below 720px, some bottom items may clip as expected).
6. **Saving**: Provide a name and save a valid level.
7. **Custom Levels**: Verify the new level appears in the "選擇關卡" screen and can be played, edited, or deleted. Confirm the layout reduces the risk of custom level cards overlapping the back button.

## 4. Runtime Data Notes

The following files are used for local persistence and should **not** be committed to version control:
- `progress.json` / `data/progress.json`: Stores level completion status and best scores.
- `scores.json` / `data/scores.json`: Stores high score history.

Refer to `examples/progress.example.json` and `examples/scores.example.json` for the data structure.

## 5. Known Manual Test Gaps

The following items currently require manual visual inspection as they are not covered by automated unit tests:
- **Rendering Quality**: Visual artifacts, pseudo-3D wall shadows, and box glow effects.
- **Font Fallback**: Correct display of Chinese characters across different operating systems.
- **Window Resizing**: UI element centering and grid scaling when the window is resized.
- **Animations**: Smoothness of the win screen transition and feedback timers.
- **Input Responsiveness**: Lack of delay or dropped inputs during rapid movement.
