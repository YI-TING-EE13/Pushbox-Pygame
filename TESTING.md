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

> [!NOTE]
> When adding or refining default built-in levels, please check them against the design constraints, patterns, and checklists detailed in [LEVEL_DESIGN.md](file:///c:/Users/LAB-606/Desktop/Software%20Side%20Project/PushBox_v1/LEVEL_DESIGN.md).

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

### Level 16–20 Manual Playtest Startup Checks
13. **Level 16 Startup**: Go to page 2 of the level selector, select "Level 16", and press Enter. Verify the level board centers correctly and standard controls work perfectly.
14. **Level 17 Startup**: Select "Level 17" on page 2. Verify grid scaling and ensure player is positioned correctly on the initial board state.
15. **Level 18 Startup**: Select "Level 18" on page 2. Verify all targets and boxes are placed correctly.
16. **Level 19 Startup**: Flip to page 3, select "Level 19" (index 0). Verify that board dimensions fit standard boundaries safely.
17. **Level 20 Startup**: Select "Level 20" on page 3. Verify standard playability features (movement, undo, redo, timer) initialize successfully.

### Win & Game Over Conditions
18. **Win Condition**: Push all boxes onto targets. Verify the green "MISSION COMPLETE!" overlay appears.
19. **Win Screen Actions**: Test `N` (Next Level), `R` (Restart), and `M` (Menu) on the win screen.
20. **Deadlock (Game Over)**: Push a box into a corner where it cannot be moved (e.g., against two perpendicular walls).
21. **Game Over Overlay**: Verify the red "死鎖!" card appears.
22. **Game Over Actions**: Test `Z` (Undo), `R` (Restart), and `M` (Menu) on the game over screen.

### UI & Persistence
23. **Level Selection**: From the main menu, go to "選擇關卡". Verify all levels are listed.
24. **Progress Display**: Verify that completed levels show a green background and a "★ 最佳: X 步" indicator.
25. **Persistence**: Complete a level, exit the game, and restart. Verify that your progress and best moves are still saved.

### Pause Screen Overlay
26. **Triggering Pause**: Start a game, then press `Esc` or `P` during standard gameplay. Verify the yellow "暫停" card appears and the background game board is dimmed behind the semi-transparent overlay.
27. **Gameplay Blocked**: While paused, try pressing movement keys or action buttons. Confirm that the player does not move, boxes cannot be pushed, and the game timer is completely frozen (does not increment).
28. **Overlay Keys**: Verify the three available actions listed on the pause card work as expected:
    - **Esc / P**: Continues gameplay exactly from the current state (timer resumes without jumping forward by the duration of the pause).
    - **R**: Resets the level state and immediately exits the pause screen to playing mode.
    - **M**: Safely exits the game screen back to the main menu (clearing the pause state).
29. **Priority of Overlays**:
    - **Help priority**: If the help overlay (`H`) is open, pressing `Esc` should close the help card instead of triggering the pause overlay.
    - **Ignore trigger**: Pressing `Esc` or `P` must have no effect when the green "Win" screen or the red "Deadlock" screen is active.

### Keyboard Navigation & UX Polish
30. **Main Menu Keyboard Navigation**:
    - On the main menu, press `↓` or `S`. Verify that the highlight moves to the next option and the button lifts up slightly.
    - Press `↑` or `W`. Verify the highlight moves to the previous option.
    - Verify wrap-around: pressing `↑` or `W` on the first option wraps the highlight to the last option. Pressing `↓` or `S` on the last option wraps back to the first option.
    - Hover the mouse over any button. Verify the keyboard selection highlights that button, synchronizing the input states.
    - Press `Enter` or `Space` to activate the highlighted button callback.
31. **Help Overlay Dismissal (Any Key)**:
    - During gameplay, press `H` to open the help overlay. Verify it displays `"按任意鍵返回遊戲"` at the bottom.
    - Press `R`, direction keys, or `P`. Verify that the help overlay closes, and that the key does not trigger its gameplay action (i.e., the level is not reset, the player does not move, and the game does not pause).
    - Press a gameplay key again. Verify that the subsequent keypress triggers normally.
32. **Global Ctrl+Q Quit**:
    - On any screen (Main Menu, Gameplay, Level Selector, Tutorial, Editor, Pause overlay, Help overlay), press `Ctrl+Q`. Verify the game application closes immediately.
    - Verify that pressing `Q` alone does not exit.
33. **Level Selector Keyboard Navigation & Pagination**:
    - Go to the "選擇關卡" screen. Verify that `Level 1` is highlighted by default.
    - Confirm the layout has spacious margins and zero overlaps at the default `800x720` resolution.
    - Confirm the helper prompt `"換頁：Tab / Shift+Tab 或 PageUp / PageDown"` is displayed in small grey text below the Page Indicator (`"頁面: 1 / 3"`).
    - Page 1 must list exactly `Level 1` to `Level 9`. Page 2 lists exactly `Level 10` to `Level 18`. Page 3 lists exactly `Level 19` and `Level 20` (plus custom levels if any).
    - **Cross-page keyboard navigation (Down/S)**:
      - Navigate to the bottom row on Page 1 (e.g., `Level 8` at index 7).
      - Press `↓` or `S`. Verify that the page switches automatically to Page 2, and the selection correctly focuses on `Level 11` (retaining column 1).
      - Navigate to the bottom row on Page 2 (e.g., `Level 17` at index 7).
      - Press `↓` or `S`. Verify that the page switches automatically to Page 3, and the selection correctly focuses on `Level 20` (retaining column 1).
    - **Cross-page keyboard navigation (Up/W)**:
      - While on Page 3, select `Level 20` (index 1, column 1).
      - Press `↑` or `W`. Verify that the page switches back to Page 2, focusing on `Level 17` (retaining column 1 in the bottom row).
      - While on Page 2, select `Level 11` (index 1, column 1).
      - Press `↑` or `W`. Verify that the page switches back to Page 1, focusing on `Level 8` (retaining column 1).
    - **Cross-page keyboard navigation (Right/D & Left/A)**:
      - On Page 1, navigate to the last item (`Level 9` at index 8).
      - Press `→` or `D`. Verify that the page switches to Page 2, focusing on the first element (`Level 10`).
      - Press `←` or `A` on `Level 10`. Verify that the page switches back to Page 1, focusing on `Level 9`.
    - **Page boundary clamping**:
      - Navigate to `Level 1` (Page 1, index 0). Press `↑`/`W` or `←`/`A`. Confirm you stay on Page 1 safely.
      - Navigate to the last item on Page 3 (`Level 20` or a custom level). Press `↓`/`S` or `→`/`D`. Confirm you stay on Page 3 safely and the selection highlight clamps without any crashes.
    - **Tab / PageDown / Shift+Tab / PageUp**:
      - Confirm Tab or PageDown transitions to Page 2 (Level 10 highlighted), and pressing it again transitions to Page 3 (Level 19 highlighted).
      - Confirm Shift+Tab or PageUp transitions back Page-by-Page, resetting highlight correctly.
    - **Mouse Interoperability**:
      - Click the `"◀ 上一頁"` and `"下一頁 ▶"` mouse buttons at the bottom. Verify they transition pages correctly without causing text overlays.
      - Click the `"返回"` button at the bottom. Verify it returns to the main menu.
    - **Correct Level Launching**:
      - Navigate to Page 3, highlight `Level 19` or `Level 20`, and press `Enter` or `Space`. Verify the level starts correctly and is fully playable.
    - **Custom Levels Preservation**:
      - Create a custom level in the editor. Verify it appears on Page 3 (as the 3rd card), displaying `"編輯"` and `"刪除"` buttons correctly on its card, while default levels `Level 1` to `Level 20` never display them.
    - **Level Selector Metadata Badges & Polished Details Panel**:
      - Navigate to the "選擇關卡" screen. Verify that default levels (Levels 1–20) display a clear metadata badge (e.g. `Intro · 3 boxes` or `Advanced · 2 boxes`) beneath the level title.
      - Verify that custom levels do not display any metadata badges on cards and do not cause the selector to crash.
      - Verify that default level cards do not show "編輯" (Edit) or "刪除" (Delete) buttons, whereas custom level cards display them correctly.
      - Confirm that there is no vertical or horizontal text overlap at the default resolution of `800x720`.
      - Play and complete any default level. Return to the "選擇關卡" screen and verify that the completed card displays a compact success-colored completion star (`★`) in its top-right corner, completely eliminating card-level overlaps.
      - **Keyboard Interoperability:** Use arrow keys or WASD to navigate the selector. Verify that the bottom selected level detail panel updates dynamically and instantly to reflect the newly highlighted level.
      - **Mouse Hover Interoperability:** Hover the mouse over different cards. Verify that the selection index updates and the bottom detail panel changes in real-time.
      - **Default Level Detail Panel Layout:** Select a default level. Confirm the bottom panel prints exactly three clean, well-spaced lines:
        * Line 1: `[Level Name] · [Difficulty] · [Theme] · [Boxes] boxes` (e.g. `Level 16 · Advanced · L-Corridor · 2 boxes`) in high-contrast highlighted color.
        * Line 2: `說明: [Note]` in dimmed text (confirm notes longer than 65 characters are truncated with `...` safely).
        * Line 3: `狀態: 未完成` (dimmed) or `狀態: 已完成 · 最佳: X 步` (success green).
      - **Custom Level Fallback Display:** Select a custom level. Confirm it displays exactly three lines:
        * Line 1: `[Custom Level Name]` in highlighted color.
        * Line 2: `類型: 自訂關卡` in dimmed text.
        * Line 3: `狀態: 未完成` (dimmed) or `狀態: 已完成 · 最佳: X 步` (success green).
      - Verify that Page 1, Page 2, and Page 3 all render properly without crashes, and there is no overlap between the bottom detail panel and the page indicators, pagination hints, Prev/Next buttons, or the Back button.

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
5. **Sidebar Layout & Hints**: Confirm that all 6 lines of shortcut hints (左鍵/右鍵, 1-5, Z/Y/R, Ctrl+S, C, Esc) are visible on the default window size (800x720) without overlapping other controls.
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
