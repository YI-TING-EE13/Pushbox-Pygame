# PushBox Release Notes

All notable changes to this project are documented in this file.

---

## v0.5.0 - Expanded Levels and Selector Metadata (2026-05-17)

This release significantly expands the default gameplay content, enhances UI typography and feedback, introduces strictly typed default level metadata, and resolves a layout regression on completed level selector cards.

### Added
* **Levels 16–20:** Added five brand new advanced default levels to the built-in catalog, expanding default levels from 15 to 20.
* **Level Selector Metadata Badges:** Default levels display a clear metadata subtitle badge (e.g. `Advanced · 2 boxes`) beneath the level title.
* **Selected Level Details Panel:** Created a dynamic bottom info area that displays detailed level profiles (Theme, Difficulty, Box count, descriptive explanation notes, and high record moves) for the currently highlighted grid button.
* **Strictly Typed Metadata Schema:** Added type-safe `LevelMetadata` dictionary structures utilizing `typing.TypedDict` inside `constants.py` to prevent data drifting or format inconsistencies.

### Improved & Refined
* **Graduating Level Grid Layouts:** Specially configured and refined grid matrices for Levels 16–20 to present graduations in scale, complex path layouts, and unique box/target distributions.
* **Level Selector Layout Hotfix:** Resolved vertical text overlaps on completed level cards:
  * Replaced full on-card text stack with a compact success-colored completion star (`★`) badge in the top-right corner of the cards.
  * Relocated full best-moves records (e.g. `★ 最佳: 10 步`) to the bottom selected details panel.
* **Code Quality & View layer docstrings:** Significantly improved documentation comments and docstrings in all core rendering/UI components to satisfy professional engineering standards.
* **Documentation Synchronization:** Updated `README.md` and `TESTING.md` to cleanly align with the metadata architecture and paginated selector improvements.

### Quality Assurance & Automated Tests
* Appended comprehensive consistency test coverage in `test_level.py` to guarantee 1-to-1 default level key mapping and ensure programmatically counted grid box counts exactly match metadata entries.
* Added drawing and pagination integration tests in `test_input.py` verifying that rendering completed default levels and custom level progress executes flawlessly.
* *Note on Scope:* Automated tests validate data structures, format integrity, and general UI/movement states, but do not mathematically prove formal Sokoban puzzle solvability.

---

## v0.5.0 Manual Smoke Test Checklist

Use this checklist to verify that all v0.5.0 features run correctly after a local pull or build.

### 1. Game Boot and Main Menu
* [ ] **Launch Game:** Run `uv run python main.py` or `python main.py`. Confirm the game boots in `800x720` resolution with zero console exceptions.
* [ ] **Menu Navigation:** Confirm you can select menu items ("開始遊戲", "選擇關卡", "地圖編輯器", "結束遊戲") using mouse clicks and keyboard (Arrow keys/WASD) followed by `Enter`/`Space`.

### 2. Gameplay and Control Mechanics
* [ ] **Start Default Level:** Launch "開始遊戲" (Level 1).
* [ ] **Movement:** Confirm the player moves cleanly using both Arrow keys and WASD.
* [ ] **Undo / Redo / Reset:**
  * Push a box and perform multiple moves. Press `U` or `Backspace` to undo actions.
  * Press `R` to redo undone actions.
  * Press `Escape` or the on-screen "重設" button to reset the level grid to its initial state.
* [ ] **Pause and Resume:** Press `P` or click "暫停" to pause the game. Confirm movement is frozen. Click "繼續" or press `P` to resume.
* [ ] **Help Overlay:** Press `H` or click "幫助". Confirm the overlay card dismisses cleanly on any key tap or mouse click.

### 3. Level Selector and Metadata Badges
* [ ] **Paginated Grid:** Click "選擇關卡" or press `M` to exit. Confirm a cleanly structured 3x3 button layout.
* [ ] **Metadata Badges:** Confirm default level cards show Level Name and the `[Difficulty] · [Boxes] boxes` badge in a dual-line layout.
* [ ] **Page Switching:**
  * Navigate to Page 2 using the bottom `"下一頁"` button or keyboard shortcuts (`Tab` or `PageDown`).
  * Navigate to Page 3. Confirm `Level 19` and `Level 20` display their correct metadata badges safely.
* [ ] **Detail Panel Updates:** Move the highlighted selection index across cards. Verify that the bottom selected level panel updates dynamically with correct Theme, Difficulty, Box count, descriptive explanation notes, and high record moves.
* [ ] **Completed Level Corner Star:**
  * Play and win any default level.
  * Re-enter the Level Selector and verify that the completed card displays a compact success-colored completion star (`★`) in its top-right corner, and full high scores appear in the details panel when highlighted.
* [ ] **Custom Levels Preservation:** Create a custom level in the editor. Open the selector on Page 3, and confirm that custom level cards do not show metadata badges but correctly show `"編輯"` and `"刪除"` button overlays.

### 4. Level Editor
* [ ] **Open and Exit:** Click "地圖編輯器" from the main menu. Confirms grid coordinates draw, painting controls are operational, and exiting the editor returns to the menu safely.

---

## v0.4.0 - Paginated Level Selector UX (2026-05-17)
* Integrated grid-based selector navigation for all arrow/WASD inputs.
* Implemented cross-page paginated layout rendering.
* Synchronized input routing boundaries.

## v0.3.0 - Level Editor and Custom Map Storage (2026-05-16)
* Created fully-featured Grid Painting Level Editor.
* Implemented custom level save/load mechanisms.
* Prevented text overlaps on tutorial screen layouts.
