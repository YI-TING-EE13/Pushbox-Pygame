# Testing Guide for Pushbox-Pygame

This document outlines the testing procedures for the Pushbox-Pygame project, including automated checks and manual smoke tests.

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

### Solver Core Automated Tests (v0.8.0 Phase 2)

The pathfinding solver core (`src/pushbox/models/solver.py`) is covered by comprehensive unit tests inside [test_solver.py](file:///C:/Users/LAB-606/Desktop/Software%20Side%20Project/PushBox/tests/test_solver.py). These tests validate the solver logic independently of Pygame rendering:

- **Level 0 Solvability**: Verifies that the onboarding tutorial-only Level 0 returns a successful `SolverStatus.SOLVED` and a valid action path.
- **Shortest Action Path Replay**: Uses a test helper to copy a level, replay the actions step-by-step on `GameState`, and assert that the level completes successfully (victory/won state).
- **Corner Deadlock Pruning**: Checks that a box pushed to a non-target dead-corner is immediately pruned to optimize BFS without dropping correct paths.
- **Search Constraints**: Limits the maximum searched nodes using `max_nodes` to verify `SolverStatus.NODE_LIMIT_EXCEEDED` is returned rather than hanging.
- **State Integrity**: Ensures that the solver execution does not mutate the original `Level` grid or state.
- **Layout Safety**: Confirms layouts containing pre-placed boxes on targets (`BOX_ON_TARGET`) parse and solve correctly.

Run these tests specifically using:
```bash
uv run python -m pytest tests/test_solver.py -v
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
6. **HUD Level Label Display**:
   - Launch a default level (e.g., `Level 23`). Verify that `"Level 23"` is clearly displayed in a highlighted soft blue color in the top-left gameplay HUD.
   - Confirm the label does not overlap move counts, timer, pause indicators, or help overlay.
   - Launch a custom level (e.g., `"對稱自訂圖"`), and verify the custom name is correctly shown. Confirm long custom names are safely truncated.
7. **Movement**: Test movement using both **Arrow Keys** and **WASD**.
8. **Pushing**: Push a box and verify it moves.
9. **Undo**: Move or push, then press `Z` or `Backspace`. Verify the state reverts correctly.
10. **Redo**: After undoing, press `Y` or `R`. Verify the action is reapplied.
11. **Reset**: Press `F5` or `Delete`. Verify the level restores to its initial state.
12. **Help Overlay**: Press `H` during gameplay. Verify the help card appears and correctly lists controls.
13. **Return to Menu**: Press `M` during gameplay or after winning. Verify it returns to the main menu.

### Level 16–30 Manual Playtest Startup Checks
1. **Level 16 Startup**: Go to page 2 of the level selector, select "Level 16", and press Enter. Verify the level board centers correctly and standard controls work perfectly.
2. **Level 17 Startup**: Select "Level 17" on page 2. Verify grid scaling and ensure player is positioned correctly on the initial board state.
3. **Level 18 Startup**: Select "Level 18" on page 2. Verify all targets and boxes are placed correctly.
4. **Level 19 Startup**: Flip to page 3, select "Level 19" (index 0). Verify that board dimensions fit standard boundaries safely.
5. **Level 20 Startup**: Select "Level 20" on page 3. Verify standard playability features (movement, undo, redo, timer) initialize successfully.
6. **Level 21–30 Startup & Playability**: Select "Level 21" through "Level 30" on Page 3 and Page 4. Verify that metadata badges, bottom detail panel, grid scaling, and playability work correctly. Manually playtest Level 26–30 to confirm they are structurally valid and designed to be playable.

### Win & Game Over Conditions
1. **Win Condition**: Push all boxes onto targets. Verify the green "MISSION COMPLETE!" overlay appears.
2. **Win Screen Actions**: Test `N` (Next Level), `R` (Restart), and `M` (Menu) on the win screen.
3. **Deadlock (Game Over)**: Push a box into a corner where it cannot be moved (e.g., against two perpendicular walls).
4. **Game Over Overlay**: Verify the red "死鎖!" card appears.
5. **Game Over Actions**: Test `Z` (Undo), `R` (Restart), and `M` (Menu) on the game over screen.

### UI & Persistence
1. **Level Selection**: From the main menu, go to "選擇關卡". Verify all levels are listed.
2. **Progress Display**: Verify that completed levels show a green background and a "★ 最佳: X 步" indicator.
3. **Persistence**: Complete a level, exit the game, and restart. Verify that your progress and best moves are still saved.

### Solver Hint UI Flow (v0.8.0 Phase 3)
1. **Triggering Hint via Button**: Start a default game (e.g. `Level 1`). Locate the `"💡 提示 (I)"` HUD button at the bottom of the screen.
   - Click the button. Confirm that a high-contrast highlighted text banner `"提示：請沿著高亮方向移動"` fades in at the top (below stats bar) and that **a beautiful pulsing/glowing border appears around the cell for the first step** and **a semi-transparent highlighted guide line is drawn for the first 3 steps of the path**.
2. **Triggering Hint via Key**: Press the `I` key. Confirm that the exact same glowing path, pulsed border, and instruction text are rendered instantly.
3. **Pulsing Highlight and Guide Line**: Verify the guide line follows the center of grid cells, respects dynamic cell sizing, and aligns correctly after window resizing.
4. **Auto Fade Out**: Confirm that the hint path, pulsed target border, and text banner **automatically disappear after 1.5 seconds**.
5. **Action Clearing**: Press `I` to show the path, then make a move, undo (`Z`), or reset (`F5`). Verify the hint path and text banner **disappear instantly**, preventing outdated instructions.
6. **Overlay Blocks**: Try pressing `I` when help (`H`), pause (`Esc`), win, or deadlock screen is open. Confirm no hints are triggered.
7. **Onboarding Level 0 Exclusivity**: Play Level 0. Look at the HUD buttons: the `"💡 提示 (I)"` button must be **completely hidden** and pressing `I` key must do nothing.
8. **Solver Status Wording Check**:
   - **SOLVED with empty path**: Confirm it prints `"目前已在完成狀態"`.
   - **UNSOLVED**: Push a box to an unsolvable non-target dead corner. Press `I`. Confirm it displays `"目前局面可能無法完成，建議按 Z 撤銷或 F5 重置。"` instead of "no solution".
   - **NODE_LIMIT_EXCEEDED**: Confirm it displays `"此局面較複雜，暫時找不到可靠提示。"`.

### Onboarding (Level 0) Tutorial-Only Flow
1. **Reset to Tutorial State**: Delete the `data/config.json` file if it exists, or edit it to set `"show_tutorial": true`.
2. **Startup Redirect**: Launch the game (`uv run python main.py`). Verify that the game **directly boots into gameplay showing "Level 0"**, completely skipping the main menu and static tutorial card.
3. **Instruction Banner display**: Confirm that a high-contrast highlighted text banner (e.g. `"提示：按 WASD 或方向鍵進行移動"`) is beautifully centered inside a rounded semi-transparent window at the top of the gameplay board.
4. **Adjacency detection & feedback**:
   - Move the player at least one step. Verify that the top instruction updates to `"提示：走到箱子旁，將它推向紅色的目標點"`.
   - Walk next to the box. Verify that the instruction instantly switches to `"提示：走到箱子旁，繼續向前推動它"`.
5. **No Win Overlay & Direct-Exit**: Push the box onto the target to solve the puzzle.
   - Verify that **no win fireworks animation** is played.
   - Verify that **no stats overlay card** (MISSION COMPLETE) appears.
   - Confirm that the game **immediately and smoothly fades out and exits back to the Main Menu**.
6. **Persistence & Exclusivity Verification**:
   - Check the Main Menu: The completion indicator must show `★ 0 / 30 關` (Level 0 is ignored from progress).
   - Check the level select: Go to "選擇關卡" and confirm that `Level 0` is **completely invisible** on any card page.
   - Restart the game: Verify it boots straight to the Main Menu now (and `show_tutorial` config was correctly written to `false`).
   - Click "開始遊戲": Verify it successfully loads `Level 1` instead.
   - Click "教學說明": Verify it opens the static `TutorialScreen` card overlay for review as normal.

### Pause Screen Overlay
1. **Triggering Pause**: Start a game, then press `Esc` or `P` during standard gameplay. Verify the yellow "暫停" card appears and the background game board is dimmed behind the semi-transparent overlay.
2. **Gameplay Blocked**: While paused, try pressing movement keys or action buttons. Confirm that the player does not move, boxes cannot be pushed, and the game timer is completely frozen (does not increment).
3. **Overlay Keys**: Verify the three available actions listed on the pause card work as expected:
    - **Esc / P**: Continues gameplay exactly from the current state (timer resumes without jumping forward by the duration of the pause).
    - **R**: Resets the level state and immediately exits the pause screen to playing mode.
    - **M**: Safely exits the game screen back to the main menu (clearing the pause state).
4. **Priority of Overlays**:
    - **Help priority**: If the help overlay (`H`) is open, pressing `Esc` should close the help card instead of triggering the pause overlay.
    - **Ignore trigger**: Pressing `Esc` or `P` must have no effect when the green "Win" screen or the red "Deadlock" screen is active.

### Keyboard Navigation & UX Polish
1. **Main Menu Keyboard Navigation**:
    - On the main menu, press `↓` or `S`. Verify that the highlight moves to the next option and the button lifts up slightly.
    - Press `↑` or `W`. Verify the highlight moves to the previous option.
    - Verify wrap-around: pressing `↑` or `W` on the first option wraps the highlight to the last option. Pressing `↓` or `S` on the last option wraps back to the first option.
    - Hover the mouse over any button. Verify the keyboard selection highlights that button, synchronizing the input states.
    - Press `Enter` or `Space` to activate the highlighted button callback.
2. **Help Overlay Dismissal (Any Key)**:
    - During gameplay, press `H` to open the help overlay. Verify it displays `"按任意鍵返回遊戲"` at the bottom.
    - Press `R`, direction keys, or `P`. Verify that the help overlay closes, and that the key does not trigger its gameplay action (i.e., the level is not reset, the player does not move, and the game does not pause).
    - Press a gameplay key again. Verify that the subsequent keypress triggers normally.
3. **Global Ctrl+Q Quit**:
    - On any screen (Main Menu, Gameplay, Level Selector, Tutorial, Editor, Pause overlay, Help overlay), press `Ctrl+Q`. Verify the game application closes immediately.
    - Verify that pressing `Q` alone does not exit.
4. **Level Selector Keyboard Navigation & Pagination**:
    - Go to the "選擇關卡" screen. Verify that `Level 1` is highlighted by default.
    - Confirm the layout has spacious margins and zero overlaps at the default `1024x768` resolution.
    - Confirm the helper prompt `"換頁：Tab / Shift+Tab 或 PageUp / PageDown"` is displayed in small grey text below the Page Indicator (`"頁面: 1 / 4"`).
    - Page 1 must list exactly `Level 1` to `Level 9`. Page 2 lists exactly `Level 10` to `Level 18`. Page 3 lists exactly `Level 19` to `Level 27`. Page 4 lists exactly `Level 28` to `Level 30` (plus custom levels if any).
    - **Cross-page keyboard navigation (Down/S)**:
      - Navigate to the bottom row on Page 1 (e.g., `Level 8` at index 7).
      - Press `↓` or `S`. Verify that the page switches automatically to Page 2, and the selection correctly focuses on `Level 11` (retaining column 1).
      - Navigate to the bottom row on Page 2 (e.g., `Level 17` at index 7).
      - Press `↓` or `S`. Verify that the page switches automatically to Page 3, and the selection correctly focuses on `Level 20` (retaining column 1).
      - Navigate to the bottom row on Page 3 (e.g., `Level 26` at index 7).
      - Press `↓` or `S`. Verify that the page switches automatically to Page 4, and the selection correctly focuses on `Level 29` (retaining column 1).
    - **Cross-page keyboard navigation (Up/W)**:
      - While on Page 4, select `Level 29` (index 1, column 1).
      - Press `↑` or `W`. Verify that the page switches back to Page 3, focusing on `Level 26` (retaining column 1).
      - While on Page 3, select `Level 20` (index 1, column 1).
      - Press `↑` or `W`. Verify that the page switches back to Page 2, focusing on `Level 17` (retaining column 1).
      - While on Page 2, select `Level 11` (index 1, column 1).
      - Press `↑` or `W`. Verify that the page switches back to Page 1, focusing on `Level 8` (retaining column 1).
    - **Cross-page keyboard navigation (Right/D & Left/A)**:
      - On Page 1, navigate to the last item (`Level 9` at index 8).
      - Press `→` or `D`. Verify that the page switches to Page 2, focusing on the first element (`Level 10`).
      - Press `←` or `A` on `Level 10`. Verify that the page switches back to Page 1, focusing on `Level 9`.
    - **Page boundary clamping**:
      - Navigate to `Level 1` (Page 1, index 0). Press `↑`/`W` or `←`/`A`. Confirm you stay on Page 1 safely.
      - Navigate to the last item on Page 4 (`Level 30` or a custom level). Press `↓`/`S` or `→`/`D`. Confirm you stay on Page 4 safely and the selection highlight clamps without any crashes.
    - **Tab / PageDown / Shift+Tab / PageUp**:
      - Confirm Tab or PageDown transitions to Page 2 (Level 10 highlighted), and pressing it again transitions to Page 3 (Level 19 highlighted), and again to Page 4.
      - Confirm Shift+Tab or PageUp transitions back Page-by-Page, resetting highlight correctly.
    - **Mouse Interoperability**:
      - Click the `"◀ 上一頁"` and `"下一頁 ▶"` mouse buttons at the bottom. Verify they transition pages correctly without causing text overlays.
      - Click the `"返回"` button at the bottom. Verify it returns to the main menu.
    - **Correct Level Launching**:
      - Navigate to Page 4, highlight `Level 28` through `Level 30`, and press `Enter` or `Space`. Verify the level starts correctly and is fully playable.
    - **Custom Levels Preservation**:
      - Create a custom level in the editor. Verify it appears on Page 4 (as the 4th card), displaying `"編輯"` and `"刪除"` buttons correctly on its card, while default levels `Level 1` to `Level 30` never display them.
    - **Level Selector Metadata Badges & Polished Details Panel**:
      - Navigate to the "選擇關卡" screen. Verify that default levels (Levels 1–30) display a clear metadata badge (e.g. `Intro · 3 boxes` or `Advanced · 2 boxes`) beneath the level title.
      - Verify that custom levels do not display any metadata badges on cards and do not cause the selector to crash.
      - Verify that default level cards do not show "編輯" (Edit) or "刪除" (Delete) buttons, whereas custom level cards display them correctly.
      - Confirm that there is no vertical or horizontal text overlap at the default resolution of `1024x768`.
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
      - Verify that Page 1, Page 2, Page 3, and Page 4 all render properly without crashes, and there is no overlap between the bottom detail panel and the page indicators, pagination hints, Prev/Next buttons, or the Back button.

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
5. **Sidebar Layout & Hints**: Confirm that all 6 lines of shortcut hints (左鍵/右鍵, 1-5, Z/Y/R, Ctrl+S, C, Esc) are visible on the default window size (1024x768) without overlapping other controls.
6. **Saving**: Provide a name and save a valid level.
7. **Custom Levels**: Verify the new level appears in the "選擇關卡" screen and can be played, edited, or deleted. Confirm the layout reduces the risk of custom level cards overlapping the back button.

### Custom Level Share Code Export & Import (v0.8.0 Phase 4)
1. **Valid Level Export**: Go to "自訂關卡" (Level Editor). Create a valid level (e.g. wall perimeter, exactly 1 player, at least 1 box, boxes == targets).
   - Press `E` or click `"匯出關卡 (E)"` in the sidebar.
   - Confirm that a beautiful dialog `"匯出關卡分享碼"` fades in showing `"分享碼已自動複製到您的剪貼簿！"` and displays a text box with the code starting with `PBX_`.
   - Click `"複製分享碼"` in the dialog. Verify that status feedback `"已複製至剪貼簿！"` appears.
   - Click `"關閉視窗"` or press `Esc`. Verify the dialog closes.
2. **Invalid Level Export Validation**:
   - Clear the editor grid, or remove the wall perimeter, or remove the player. Press `E`.
   - Verify that an error message like `"無法匯出: 外圍邊界必須完全封閉為牆壁!"` or `"錯誤: 必須放置玩家!"` is displayed in the status bar, and no dialog is triggered.
3. **Valid Level Import**: Go to "選擇關卡" (Level Selector). Scroll to Page 4 where custom levels are shown.
   - Click `"匯入關卡"` button at the bottom.
   - Confirm that a dialog `"匯入關卡"` fades in.
   - Paste (Ctrl+V) the copied valid `PBX_` code into the input box.
   - Click `"確認匯入"` or press `Enter`.
   - Verify that the dialog closes successfully, and the newly imported level appears selected on the custom levels page.
   - Select the imported card and click `"開始遊戲"` to verify it loads and plays perfectly.
4. **Name Deduplication & Sanitization**:
   - Paste the same code again and click `"確認匯入"`.
   - Verify it successfully imports the level, appending ` (2)` to the name (e.g. `My Level (2)`) instead of overwriting the existing level.
   - Create a sharing code with a malicious name like `"../../Hack"`. Import it and verify it sanitizes the name to `"Hack"`, preventing path traversal.
5. **Import Defenses & Validation Errors**:
   - Click `"匯入關卡"`. Paste a bad sharing code, e.g. `"PBX_!!!notbase64!!!"`. Click `"確認匯入"`.
   - Verify that it shows a clear red error message `"分享碼格式不正確（無法進行 Base64 解碼）。"` inside the dialog and stays open.
   - Try importing a layout with 2 players, 0 boxes, or open boundaries. Verify the corresponding defensive error messages (e.g., `"必須恰好只有 1 位玩家"`, `"外圍邊界必須完全封閉為牆壁"`) are displayed correctly and no crash occurs.
   - Click `"取消返回"` to close the import dialog.

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

## 6. Packaged Standalone Release Smoke-Test Checklist

這是一個專為打包後的 Windows 獨立發佈版本（Standalone Exe Release）設計的冒煙測試清單。每次重新打包發佈前，應在乾淨的 Windows 測試機或獨立虛擬機中完成以下所有項目的手動驗證：

### 1. Clean Directory Launch (全新乾淨目錄啟動)
- [ ] 將打包產出的 ZIP 壓縮檔（例如 `Pushbox-Pygame-v0.9.0-windows-x64.zip`）複製到一個乾淨的、不包含任何舊版遊戲殘留或 Python 環境的暫存目錄。
- [ ] 完整解壓縮 ZIP 檔。
- [ ] 驗證解壓縮後的資料夾結構乾淨，不包含 `data/`（存檔與設定）或 `levels/`（自訂關卡）目錄。
- [ ] 雙擊執行 `Pushbox-Pygame.exe`，確認遊戲能正常開啟並成功顯示開頭的 Tutorial 畫面。

### 2. Standalone Save & Portability (存檔與資料可攜性)
- [ ] 在初次啟動遊戲後，關閉遊戲。
- [ ] 檢查 EXE 同級目錄，驗證 `data/` 和 `levels/` 資料夾已**自動且成功建立在與 EXE 相同的目錄下**。
- [ ] 驗證 `data/` 內包含 `config.json`，且**沒有**寫入 PyInstaller 的內部暫存目錄（如 `_internal/`）中。
- [ ] 重新開啟遊戲，完成 Level 1，然後關閉遊戲。
- [ ] 驗證 `data/` 下是否成功產生了 `progress.json`、`scores.json` 以及對應的 `.bak` 備份檔案。

### 3. SmartScreen & Security Verification (安全警告防禦)
- [ ] 在全新下載或首次雙擊時，確認 Windows SmartScreen 是否出現「未知的發行商」警告。
- [ ] 點擊「其他資訊（More info）」，確認顯示的檔案名稱正確，然後點擊「仍要執行（Run anyway）」，確認可順利啟動遊戲。
- [ ] 確保殺毒軟體（如 Windows Defender）在啟動和遊玩過程中不會報毒或阻攔 EXE 的行為。

### 4. Non-English & Space Paths (特殊路徑相容性)
- [ ] 將遊戲整個資料夾移動到包含**中文/非英文字元**的路徑下（例如 `C:\Users\測試使用者\桌面\推箱子遊戲\`）。雙擊 EXE 啟動，確認遊戲完全正常執行且無崩潰。
- [ ] 將遊戲整個資料夾移動到包含**半形空格**的路徑下（例如 `C:\Program Files\Pushbox Pygame Standalone\`）。雙擊 EXE 啟動，確認遊戲能正常讀寫設定與存檔。

### 5. Packaging Quality & GUI Window Mode (打包品質與純 GUI 驗證)
- [ ] 雙擊執行 `Pushbox-Pygame.exe` 時，確認**沒有任何命令提示字元（CMD/Console）黑視窗伴隨出現**。
- [ ] 遊戲視窗在開啟、遊玩和關閉時，均應為純粹的 Pygame GUI 視窗。
- [ ] 驗證 `scripts/build_windows.py` 中的 `console=False` 參數運作正確。

### 6. Executable Icon Verification (獨立圖標驗證)
- [ ] 在 Windows 檔案總管中，將檢視模式切換為「大圖示」或「中等圖示」。
- [ ] 驗證 `Pushbox-Pygame.exe` 檔案圖標已正確顯示為自訂設計的幾何小熊推木箱（Nord geometric bear pushing a crate）圖標。
- [ ] 將 `Pushbox-Pygame.exe` 傳送捷徑到桌面，驗證桌面捷徑的圖標依然顯示正確且高解析度不失真（256x256 縮小至 32x32 等多解析度適配）。

### 7. Clean Assets Verification (乾淨資產驗證)
- [ ] 在解壓縮後的 `_internal/` 或 EXE 目錄中，搜索驗證 **沒有** `player.jpeg` 或其他未授權的外部測試圖片。
- [ ] 進入遊戲的 "關於 (About)" 畫面，確認版本號顯示與當前 build 設定相符。

### 8. Release SHA256 Verification (哈希校驗)
- [ ] 每次打包後，手動或使用自動化腳本計算 ZIP 檔案的 SHA256 哈希值。
- [ ] 驗證產出的 `.sha256` 檔案內容格式正確：
  `SHA256哈希值  Pushbox-Pygame-v[版本]-windows-x64.zip`

### 9. Multi-Window Prevention & Single-Instance Guard (v0.9.2 Hotfix)
- [ ] Launch `Pushbox-Pygame.exe` once. Confirm that a single game window boots up perfectly.
- [ ] While the first game window is still open, try launching `Pushbox-Pygame.exe` again (both rapidly and slowly).
- [ ] Confirm that no additional game window appears, and the second instance process exits silently and immediately without crashing or spawning any debug console window.
- [ ] Open Windows Task Manager (Ctrl+Shift+Esc), locate active processes, and verify that only exactly one `Pushbox-Pygame.exe` process is running.
- [ ] Kill the primary process in Task Manager, then double-click `Pushbox-Pygame.exe` again. Verify that the game launches successfully without being locked out (stale mutex handle successfully recycled by the OS).
- [ ] Move the game folder to a Chinese/Unicode path or a path containing spaces. Repeat the single-instance test and verify it still prevents duplicate instances flawlessly.

