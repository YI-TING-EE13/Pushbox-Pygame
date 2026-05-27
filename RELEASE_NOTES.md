# Pushbox-Pygame Release Notes

All notable changes to this project are documented in this file.

---

## v0.9.3.dev0 — Unreleased

### Added
* Added translation utility module `src/pushbox/utils/i18n.py` implementing Python dictionary-based translations supporting English (`en`) as default and Traditional Chinese (`zh-TW`).
* Added fallback translation lookup API supporting normalization of language identifiers, custom language overrides, missing key fallbacks, and safe error-free handling for unsupported languages.
* Added `tests/test_i18n.py` testing language defaults, supported sets, translation lookups, overrides, fallback chains, normalization variations, and safe non-mutating context isolated lookups.
* Added "Language" option to `SettingsScreen` as index 4, displaying current active language (English or 繁體中文) and cycling between "en" and "zh-TW" instantly.
* Added `tests/test_language_ui.py` to comprehensively test Settings language row structure (7 options), language cycling, config saving, i18n state synchronization, and main menu localized label rebuilding.
* Added localized AboutScreen support using dynamic translations (`about.*`) and dynamic blit width calculation to prevent overlapping.
* Added localized TutorialScreen support using dynamic translations (`tutorial.*`) in `TutorialScreen.draw()`.
* Added three new integration tests verifying About screen, Tutorial screen, and bottom gameplay buttons localization.
* Added translation keys for `level_selector.*`, `custom_level.*`, `difficulty.*`, and `theme.*` namespaces to `src/pushbox/utils/i18n.py` for both English (`en`) and Traditional Chinese (`zh-TW`).
* Added localized Level Selector title, paginated controls, Back/Import buttons, page indicators, details panel labels, and built-in difficulties/themes mappings using dynamic translation cycles.
* Added localized Level Selector Import Dialog with localized titles, instruction descriptions, error messages, and confirm/cancel action labels.
* Implemented automatic layout refresh in `LevelSelector.draw()` that automatically detects changes in `get_language()` and rebuilds all buttons exactly once.
* Added `test_level_selector_screen_localization`, `test_level_selector_custom_levels_buttons_localization`, `test_import_dialog_localization`, and `test_i18n_fallback_robustness` to `tests/test_language_ui.py` to comprehensively cover selector localization and fallback behavior.
* Added translation keys for `editor.*` namespace to `src/pushbox/utils/i18n.py` for English and Traditional Chinese locales.
* Added localized Level Editor sidebar labels, tool lists, rows/columns counts, and shortcut operation tips dynamically using `t(...)` translations.
* Refactored Level Editor toolbar buttons and resizing buttons to use a dynamic language switch check that rebuilds buttons exactly once upon language change.
* Localized exit confirmation dialog and export sharing code dialog overlays with localized title, text, input box placeholder, and confirmation buttons.
* Localized all Level Editor validation error messages, save results, playtest validations, and export boundary conditions inside `_save_level()`, `_playtest_level()`, and `_export_level()`.
* Added integration test `test_level_editor_ui_localization` to `tests/test_language_ui.py` to cover editor screen localizations, and updated `tests/test_level_share_ui.py` to support dynamic zh-TW testing and language restore.

### Changed
* Integrated active translation language configuration into `src/pushbox/utils/config.py` defaulting to `"en"`.
* Implemented automatic configuration synchronization in `Config.load()`, `Config.reset_to_defaults()`, and `Config.set_language()`.
* Automatically normalizes/falls back unsupported language values inside `config.json` to English safely.
* Extended `tests/test_config.py` verifying language defaults, partial configuration merges, corrupted json recoveries, and active i18n synchronization.
* Refactored `_setup_menu()` in `main.py` to use `t(...)` keys for all main menu buttons.
* Implemented transition-based menu rebuild strategy to automatically refresh main menu button labels in the correct active language exactly once when returning from Settings without rebuilding every frame.
* Adjusted `tests/test_about.py` button text check using `t("main_menu.about")` instead of hardcoded Chinese text to keep the test robust under localized menus.
* Refactored `_init_game_buttons()` in `main.py` to localize the four bottom gameplay buttons (Undo, Reset, Redo, Hint) dynamically, rebuilt automatically on transition to the game screen.

### Notes
* v0.9.3 Phase B1 (Settings Language Option + Main Menu Refresh) and Phase B2 (About Screen, Tutorial Screen, and bottom gameplay buttons) are completed.
* Phase C is planned for deeper gameplay UI translation (Level Selector, Level Editor, custom sharing dialogs, gameplay deep messages).
* v0.9.5 audio remains deferred.

---

## v0.9.2 — Launch Stability Hotfix (2026-05-27)

### Fixed

* Fixed a critical multi-window launch bug on Windows standalone packaged executables by introducing a cross-platform `SingleInstanceGuard`.
* Enforces that only a single game window instance can run concurrently, preventing file lock contentions and progress file corruption.
* Leverages Win32 Named Mutex (`Local\PushboxPygameSingleInstanceMutex`) on Windows for robust system-managed lifecycle locks with automatic recycling on unexpected termination.
* Leverages Unix flock lockfile on non-Windows platforms as a lightweight fallback.

### Added

* Added `src/pushbox/utils/single_instance.py` containing the `SingleInstanceGuard` class.
* Added comprehensive unit test suite `tests/test_single_instance.py` verifying named mutexes, lockfiles, DLL exception catch, and safe re-entrant exit releases.
* Added Section 9 — Multi-Window Prevention & Single-Instance Guard manual QA checklist to `TESTING.md`.

### Changed

* Updated version metadata to `0.9.2` across `pyproject.toml`, `src/pushbox/__init__.py`, `scripts/build_windows.py`, and `constants.py`.
* Integrated `SingleInstanceGuard` check inside `main.py` entry point.

### Notes

* No gameplay logic changes.
* No audio or translation changes in this hotfix release.

---

## v0.9.1 — 2026-05-27

### Added

* Added custom packaged application icon: a procedurally generated **Nord geometric bear pushing a crate** multi-resolution `.ico` file (`src/pushbox/assets/icon/pushbox.ico`).
* Added `scripts/generate_icon.py` for fully reproducible icon generation using only Pygame and the Python standard library (no Pillow dependency).
* Added `docs/icon-source.md` documenting the icon's generation tool, prompt, creation date, post-processing steps, and redistribution terms.
* Added `docs/images/` directory with 3 game screenshots for the Visual Showcase gallery: `main-menu.png`, `gameplay-hint.png`, `level-editor.png`.
* Added Visual Showcase (畫面展示) section to `README.md` with a 3-column screenshot table.
* Added Section 6 — Packaged Standalone Release Smoke-Test Checklist to `TESTING.md`.

### Changed

* Updated version metadata to `0.9.1` across `pyproject.toml`, `src/pushbox/__init__.py`, `scripts/build_windows.py`, and `constants.py`.
* Updated `pushbox.spec` to embed the custom `.ico` icon into the PyInstaller packaging pipeline.
* Updated `scripts/build_windows.py` with a pre-build existence check for the icon file.
* Updated `tests/test_about.py` to dynamically compare against `APP_VERSION` from `constants.py`.
* Updated `README.md` roadmap, status, and features to reflect the official v0.9.1 release.

### Notes

* Official Polish Release, featuring an elegant packaged application icon, visual showcases, and comprehensive release QA validation.
* Audio/BGM/SFX remain deferred and planned for v0.9.5.

---

## v0.9.0 — Windows Standalone Packaging (2026-05-26)

### Added

* Added Windows onedir packaging infrastructure using PyInstaller.
* Added `pushbox.spec` as the reproducible packaging configuration.
* Added `scripts/build_windows.py` to generate the packaged app folder, zip archive, quick-start guide, and SHA256 checksum.
* Added `build` optional dependency group for PyInstaller.

### Changed

* Updated version metadata (pyproject.toml, src/pushbox/__init__.py) and UI version string (constants.py) to the formal release version `0.9.0`.
* Configured PyInstaller to build in pure GUI windowed mode (`console=False`) to hide the diagnostic CMD console for general players.
* Removed `player.jpeg` from packaged assets because its redistribution license was unclear; the game now relies on procedural player fallback rendering.

### Verified

* Packaged build passed clean local smoke tests from a clean extracted folder under pure GUI mode.
* Verified launch from extreme directory paths containing spaces and Chinese characters.
* Verified runtime `data/` and `levels/` creation in the exact folder adjacent to the executable.
* Verified no `player.jpeg` is included in dist/release artifacts.

### Notes

* Official GitHub Release published with tag `v0.9.0` pointing to commit `817cca1`.
* Release assets: `Pushbox-Pygame-v0.9.0-windows-x64.zip` and `.sha256` checksum file.
* Custom application desktop icon was deferred and defaults to standard system executable icons in this release.
* Audio/BGM/SFX, macOS/Linux packaging, and MSI installers remain deferred.

---

## v0.8.1 — Release Hardening (2026-05-26)

### Added
- Added About / Credits screen with version, license, repository, and attribution placeholder.
- Added runtime path helpers for packaging readiness, separating bundled read-only resources from writable runtime data.
- Added README split for players and developers.

### Changed
- Updated README to clearly separate player-facing and developer-facing instructions.
- Improved runtime path handling so future packaged builds can write data/ and levels/ next to the executable instead of bundled resource directories.

### Fixed
- Hardened config, progress, score, and custom level loading against corrupted JSON files.
- Corrupted config/save files now rebuild safely, with backup files preserved where applicable.
- Malformed custom level files are skipped with warnings instead of crashing the game.

### Notes
- This release does not add packaged Windows binaries yet; packaging is planned for v0.9.0.
- Audio and BGM are still not implemented; optional SFX is planned for v0.9.5.
- PBX_ level sharing remains local text-code / clipboard exchange, not an online server.
- Solver hints use BFS shortest action path, not necessarily minimum push-count optimization.

---

## v0.8.0 (Unreleased) - Onboarding Level & Path Solver (2026-05-26)

### Phase 1: Onboarding 互動引導關卡 [已完成]
* **教學專用 Level 0**：新增了一個獨立、符合 `5x7` 尺寸規範的極簡 Onboarding 關卡。
* **物理隔離設計**：`Level 0` 不會列入正式的 30 關進度與 `LevelSelector` 一般卡片中，亦不在主選單完成數中統計，為教學專屬的 tutorial-only設計。
* **無縫直退通關流程**：在玩家完成 `Level 0` 時，不彈出勝利 overlay 與煙火，不更新本地 progress.json，而是直接將 `show_tutorial` 設為 `False` 並以淡出轉場回到主選單。
* **HUD 動態教學提示橫幅**：在 `Level 0` 遊玩時，於畫面頂端渲染圓角半透明、帶有高亮主色調的教學提示橫幅，動態辨識步數與玩家-箱子相鄰位置給予極致的互動指引。
* **高品質 QA 通過**：新增 `test_onboarding.py` 全面驗證教學導引與隔離性。 pytest、ruff lint/format、mypy 全數通過！

### Phase 2: Solver 最短行動路徑核心 [已完成]
* **求解器純邏輯模組 (`solver.py`)**：新增獨立、不依賴 Pygame 畫面的 BFS 求解器。藉由將關卡狀態封裝成 `(player_pos, box_positions_frozenset)` 進行極速的廣度優先搜尋。
* **定義 Shortest Action Path**：明確採用「最少玩家單步移動數」的 BFS 行動路徑解，而不是宣稱最少推箱數的最優 Sokoban 解，完美契合玩家的提示指引需求。
* **安全保守剪枝 (Corner Deadlock Pruning)**：針對被推動後的箱子，若非處於目標點且落在兩垂直方向均靠牆的死角中，自動進行狀態剪枝，極大提升搜尋速度且絕對不會誤殺正解。
* **搜尋節點限制常數**：定義 `MAX_SOLVER_NODES = 50,000` 模組級常數，搜尋走訪節點數超限時優雅回傳 `SolverStatus.NODE_LIMIT_EXCEEDED`，避免記憶體溢出或程式無回應。
* **完整的單元測試與驗證**：新增 `test_solver.py` 自動化測試。包含 Level 0 求解、5x5 單箱地圖求解、無解地圖檢驗、超時限制測試、BOX_ON_TARGET 預置相容性，以及 **Replay 驗證 Helper**（完整還原移動步驟至 GameState 複本上，確保通關狀態 WON 且地圖未受污染）。
### Phase 3: Hint UI & I 鍵提示 [已完成]
* **I 鍵智慧求解提示**：遊戲中按 `I` 鍵即可異步呼叫 BFS 求解器，實時解算當前盤面的 Shortest Action Path，為卡關玩家提供最優單步指引。
* **高亮發光與呼吸脈衝**：使用 `math.sin` 與當前 ticks 設計高質感脈衝呼吸燈。提示時在第一步目標格渲染圓角高亮呼吸外框，並以半透明粗引導線渲染前 3 步行動路徑。與動態縮放格線和 offset 完美對齊。
* **視覺高度統一的玻璃提示橫幅**：在 stats HUD 下方，採用與 Onboarding 一致的半透明玻璃微光面板，動態印出當前盤面状态提示（Moves>0：高亮方向引導；無解：建議撤銷/重設；超限：局面較複雜提示），1.5 秒自動淡出消失。
* **物理隔離與安全阻斷**：
  * **Onboarding 隔離**：教學關 Level 0 遊玩時，💡 提示 HUD 按鈕會自動隱形，且 `I` 鍵觸發被攔截，防止教學與提示系統衝突。
  * **行動清理**：一旦玩家移動、撤銷 (Undo)、重寫或重置 (Reset)，已顯示的提示路徑和 banner 會瞬間乾淨清除，防過期提示造成誤導。
  * **狀態優先權阻斷**：在 win overlay, deadlock overlay, pause overlay, help overlay 處於開啟狀態時，`I` 鍵觸發被完美阻斷，杜絕 UI 衝突。
* **新增專屬整合測試**：新增 `test_hint_ui.py`。全面覆蓋 SOLVED 狀態 timer、移動/撤銷/重置清理 hint、Help/Pause 覆蓋阻斷、Level 0 攔截及各類 solver 狀態的 UI 提示文案映射，100% 測試覆蓋率！

### Phase 4: 自訂關卡 Export / Import 與分享碼系統 [已完成]
* **分享編解碼系統 (`level_share.py`)**：新增獨立純邏輯模組，實作自訂關卡匯出為 `zlib + base64` 壓縮編碼，固定以 `PBX_` 前綴開頭，支援 0 成本在社群拓寬可玩性。
* **8 點防禦性驗證機制**：匯入時實施最嚴格的防禦性邊界檢查。包含：字串格式檢查、20,000 長度上限、網格非空與 Rectangular 檢查、`5x5` 至 `20x20` 尺寸極限限制、合法 Cell 值約束（僅允許 0-4）、唯一玩家 (exactly one)、箱子與目標配對一致性、外圍邊界牆壁完全封閉檢查。
* **名稱安全淨化與去重**：匯入名稱實施去點/去斜線防路徑穿越淨化（Sanitization）；若與現有自訂關卡重名，自動採用數字遞增後綴（如 `(2)`, `(3)`）進行去重（Deduplication），避免任何檔案覆蓋風險。
* **極致體驗的雙 Dialog 介面**：
  * **編輯器匯出**：在編輯器 sidebar 整合漂亮的 `ModernButton` 和 `E` 鍵快捷鍵。點擊後觸發關卡 Layout 驗證，成功則生成並快照分享碼，呼叫 Tkinter 與 PowerShell 進程進行 **雙通道 Best-effort 自動寫入剪貼簿**，並彈出圓角玻璃分享視窗供玩家 Ctrl+C 選取複製。
  * **選擇器匯入**：在選擇器底部與返回鍵對稱整合 `ModernButton` 匯入按鈕。點擊後彈出高級的毛玻璃 Dialog，**支援 Ctrl+V 從系統剪貼簿貼上分享碼**，解析成功時自動重新 Setup 關卡列表，並動態將分頁跳轉並聚焦在該自訂關卡 Minimap 上；解析失敗則彈出紅色保守警告且不崩潰。
* **完整的雙重自動化測試**：
  * 新增 `test_level_share.py` 測試套件：全面覆蓋 round-trip 還原、各類規格邊界越界攔截、非法 cell 判定、多玩家與無玩家報錯、未封閉牆壁判定、名稱淨化與遞增去重等 16 項單元測試。
  * 新增 `test_level_share_ui.py` 測試套件：全面模擬 headless 下 Editor 匯出事件、Selector 點擊匯入、文字框貼上及錯誤捕捉等 5 項 UI 整合測試。
  * 全套 177 個測試 100% 綠燈通過！ ruff/mypy 100% 綠燈通過！

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
* [ ] **Launch Game:** Run `uv run python main.py` or `python main.py`. Confirm the game boots in `1024x768` resolution with zero console exceptions.
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
