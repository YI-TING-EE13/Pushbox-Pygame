"""Lightweight internationalization (i18n) module for Pushbox-Pygame."""

from typing import Optional

SUPPORTED_LANGUAGES = ["en", "zh-TW"]
DEFAULT_LANGUAGE = "en"

_current_language = DEFAULT_LANGUAGE

TRANSLATIONS = {
    "en": {
        # Common / Buttons
        "button.back": "Back",
        "button.cancel": "Cancel",
        "button.close": "Close",
        "button.confirm": "Confirm",
        "button.apply": "Apply",
        # Main Menu
        "main_menu.start": "Start Game",
        "main_menu.level_select": "Select Level",
        "main_menu.editor": "Level Editor",
        "main_menu.tutorial": "How to Play",
        "main_menu.settings": "Settings",
        "main_menu.about": "About Game",
        "main_menu.quit": "Quit",
        "main_menu.unselected": "None",
        "main_menu.feedback.all_completed": "Congratulations! Completed all levels!",
        # Settings Screen
        "settings.title": "Settings",
        "settings.control": "Control Scheme",
        "settings.control.arrows": "Keyboard ↑↓←→",
        "settings.control.wasd": "Keyboard WASD",
        "settings.theme": "Theme",
        "settings.animation": "Animations",
        "settings.tutorial": "Tutorial",
        "settings.language": "Language",
        "settings.danger_zone": "Reset Game Progress",
        "settings.danger_zone_lbl": "Danger Zone",
        "settings.back_to_menu": "Back to Menu",
        "settings.theme.nord_blue": "Nord Blue",
        "settings.theme.classic_green": "Classic Green",
        "settings.theme.dracula_purple": "Dracula Purple",
        "settings.reset_progress": "Reset Progress",
        "settings.feedback.progress_reset": "Progress Reset Successfully!",
        "settings.toggle.on": "On",
        "settings.toggle.off": "Off",
        "settings.language.en": "English",
        "settings.language.zh_tw": "繁體中文",
        # About Screen
        "about.title": "About / Credits",
        "about.intro_lbl": "Description: ",
        "about.intro_desc": (
            "A modern Sokoban puzzle game with onboarding, "
            "solver hints, and custom level sharing."
        ),
        "about.credits_lbl": "Development & Credits:",
        "about.back": "Back to Menu (Esc)",
        "about.version": "Version",
        "about.built_with": "Built with Python & Pygame",
        "about.license": "License",
        "about.github": "GitHub",
        "about.code_design": "Code & Design: Project contributors",
        "about.thanks": "Thanks: Python, Pygame, and the open-source community",
        "about.external_assets": (
            "External assets: See project documentation for asset source records."
        ),
        # Tutorial Screen
        "tutorial.title": "How to Play",
        "tutorial.goal.title": "🎯 Objective",
        "tutorial.goal.line1": "Push all boxes onto target points.",
        "tutorial.goal.line2": "Boxes can only be pushed, not pulled.",
        "tutorial.goal.line3": "Plan moves carefully to avoid deadlock.",
        "tutorial.control.title": "🎮 Controls",
        "tutorial.control.line1": "Arrows / WASD : Move",
        "tutorial.control.line2": "Z / Backspace : Undo",
        "tutorial.control.line3": "Y / R : Redo",
        "tutorial.control.line4": "F5 / Delete : Reset",
        "tutorial.control.line5": "Ctrl + Q : Quit Game",
        "tutorial.tip.title": "💡 Tips",
        "tutorial.tip.line1": "Click buttons at the bottom to operate.",
        "tutorial.tip.line2": "Press H in-game for layout help.",
        "tutorial.start_prompt": "Press any key to start...",
        # Gameplay Overlay Controls (Shell Portion)
        "game.buttons.undo": "Undo (Z)",
        "game.buttons.reset": "Reset (F5)",
        "game.buttons.redo": "Redo (Y)",
        "game.buttons.hint": "💡 Hint (I)",
        "game.feedback.controls": "Control Scheme: {scheme}",
        "game.win.all_done": "Congratulations! Completed all levels",
        # Level Selector
        "level_selector.title": "Select Level",
        "level_selector.back": "Back",
        "level_selector.import": "Import Level",
        "level_selector.prev_page": "◀ Prev",
        "level_selector.next_page": "Next ▶",
        "level_selector.page_indicator": "Page: {current} / {total}",
        "level_selector.page_hint": "Page: Tab / Shift+Tab or PageUp / PageDown",
        "level_selector.edit": "Edit",
        "level_selector.delete": "Delete",
        "level_selector.no_map": "No Map",
        "level_selector.custom_level": "Custom Level",
        "level_selector.locked": "🔒 Locked",
        "level_selector.completed": "Completed · Best: {moves} moves",
        "level_selector.uncompleted": "Uncompleted",
        "level_selector.note_label": "Note: {note}",
        "level_selector.type_label": "Type: {type}",
        "level_selector.status_label": "Status: {status}",
        "level_selector.boxes": "boxes",
        # Built-in difficulty and theme mapping
        "difficulty.Tutorial": "Tutorial",
        "difficulty.Easy": "Easy",
        "difficulty.Medium": "Medium",
        "difficulty.Hard": "Hard",
        "difficulty.Expert": "Expert",
        "theme.Tutorial": "Tutorial",
        "theme.Factory": "Factory",
        "theme.Garden": "Garden",
        "theme.Warehouse": "Warehouse",
        # Custom Level Dialog
        "custom_level.import_title": "Import Level",
        "custom_level.import_msg": "Paste (Ctrl+V) or type PBX_ share code below:",
        "custom_level.import_fail": "Import failed: {error}",
        "custom_level.import_hint": ("Press Enter or click 'Confirm Import' to load."),
        "custom_level.confirm": "Confirm Import",
        "custom_level.cancel": "Cancel",
        # Level Editor
        "editor.title": "Level Editor",
        "editor.label_name": "Level Name:",
        "editor.label_tools": "Select Tool:",
        "editor.label_size": "Map Size:",
        "editor.label_rows": "Rows: {rows}",
        "editor.label_cols": "Cols: {cols}",
        "editor.hints_title": "Operations:",
        "editor.hint_mouse": "L-Click: Paint | R-Click: Erase",
        "editor.hint_tools": "1-5: Switch Tools",
        "editor.hint_undoredo": "Z: Undo | Y/R: Redo",
        "editor.hint_save": "Ctrl + S: Save Level",
        "editor.hint_clear": "C: Clear Grid",
        "editor.hint_playtest": "T: Playtest",
        "editor.hint_export": "E: Export Level",
        "editor.hint_exit": "Esc: Exit Editor",
        "editor.tool_wall": "Wall (1)",
        "editor.tool_floor": "Floor (2)",
        "editor.tool_target": "Target (3)",
        "editor.tool_box": "Box (4)",
        "editor.tool_player": "Player (5)",
        "editor.btn_undo": "Undo(Z)",
        "editor.btn_redo": "Redo(Y)",
        "editor.btn_clear": "Clear(C)",
        "editor.btn_playtest": "Playtest(T)",
        "editor.btn_save": "Save(S)",
        "editor.btn_exit": "Exit",
        "editor.btn_export": "Export (E)",
        "editor.status_undo": "Undo",
        "editor.status_redo": "Redo",
        "editor.status_cleared": "Grid cleared",
        "editor.status_error_player": "Error: Player is required!",
        "editor.status_error_box": "Error: At least one box is required!",
        "editor.status_error_counts": (
            "Cannot Save: Boxes ({box_count}) and targets ({target_count}) must match!"
        ),
        "editor.status_error_playtest_counts": (
            "Cannot Playtest: Boxes ({box_count}) and "
            "targets ({target_count}) must match!"
        ),
        "editor.status_error_perimeter": (
            "Cannot Export: Perimeter must be fully sealed with walls!"
        ),
        "editor.status_error_name": "Please enter a level name!",
        "editor.status_copied": "Copied to clipboard!",
        "editor.status_generated_manual": (
            "Share code generated. Please copy manually!"
        ),
        "editor.status_export_fail": "Export failed: {error}",
        "editor.confirm_title": "Confirm Exit",
        "editor.confirm_message": ("Unsaved changes will be lost. Exit anyway?"),
        "editor.confirm_yes": "Exit (Y)",
        "editor.confirm_no": "Cancel (N)",
        "editor.export_title": "Export Level Code",
        "editor.export_success": ("Share code successfully copied to clipboard!"),
        "editor.export_manual_hint": (
            "Otherwise, select and copy from the input box below:"
        ),
        "editor.btn_copy_code": "Copy Code",
        "editor.btn_close_window": "Close",
    },
    "zh-TW": {
        # Common / Buttons
        "button.back": "返回",
        "button.cancel": "取消返回",
        "button.close": "關閉視窗",
        "button.confirm": "確認",
        "button.apply": "套用",
        # Main Menu
        "main_menu.start": "開始遊戲",
        "main_menu.level_select": "選擇關卡",
        "main_menu.editor": "編輯器",
        "main_menu.tutorial": "教學說明",
        "main_menu.settings": "設定",
        "main_menu.about": "關於遊戲",
        "main_menu.quit": "退出",
        "main_menu.unselected": "未選擇",
        "main_menu.feedback.all_completed": "恭喜! 已完成所有關卡",
        # Settings Screen
        "settings.title": "設定",
        "settings.control": "控制方式",
        "settings.control.arrows": "鍵盤 ↑↓←→",
        "settings.control.wasd": "鍵盤 WASD",
        "settings.theme": "主題配色",
        "settings.animation": "動畫效果",
        "settings.tutorial": "新手教學",
        "settings.language": "語言設定",
        "settings.danger_zone": "重置所有遊戲進度",
        "settings.danger_zone_lbl": "危險區域",
        "settings.back_to_menu": "返回主選單",
        "settings.theme.nord_blue": "極光冰川",
        "settings.theme.classic_green": "經典綠",
        "settings.theme.dracula_purple": "德古拉暗紫",
        "settings.reset_progress": "重置進度",
        "settings.feedback.progress_reset": "進度已重置！",
        "settings.toggle.on": "開啟",
        "settings.toggle.off": "關閉",
        "settings.language.en": "English",
        "settings.language.zh_tw": "繁體中文",
        # About Screen
        "about.title": "關於遊戲 / Credits",
        "about.intro_lbl": "遊戲簡介: ",
        "about.intro_desc": (
            "使用 Pygame 重新設計的推箱子遊戲，"
            "支援引導教學、自動解碼器提示與關卡分享碼。"
        ),
        "about.credits_lbl": "開發與授權致謝 (Credits):",
        "about.back": "返回主選單 (Esc)",
        "about.version": "版本",
        "about.built_with": "基於 Python 與 Pygame 開發",
        "about.license": "授權方式",
        "about.github": "開源專案",
        "about.code_design": "程式與設計：專案貢獻者",
        "about.thanks": "致謝：Python, Pygame 與開源社群",
        "about.external_assets": "外部資源：請參考專案文件中的素材來源紀錄。",
        # Tutorial Screen
        "tutorial.title": "遊戲教學",
        "tutorial.goal.title": "🎯 遊戲目標",
        "tutorial.goal.line1": "將所有箱子推到目標點上",
        "tutorial.goal.line2": "箱子只能推，不能拉",
        "tutorial.goal.line3": "精準規劃路線，避免卡死",
        "tutorial.control.title": "🎮 控制方式",
        "tutorial.control.line1": "方向鍵 / WASD：移動",
        "tutorial.control.line2": "Z / Backspace：撤銷",
        "tutorial.control.line3": "Y / R：重做",
        "tutorial.control.line4": "F5 / Delete：重置",
        "tutorial.control.line5": "Ctrl+Q：退出遊戲",
        "tutorial.tip.title": "💡 提示",
        "tutorial.tip.line1": "點擊按鈕亦可操作",
        "tutorial.tip.line2": "按 H 鍵查看說明",
        "tutorial.start_prompt": "按任意鍵開始遊戲...",
        # Gameplay Overlay Controls (Shell Portion)
        "game.buttons.undo": "撤銷 (Z)",
        "game.buttons.reset": "重置 (F5)",
        "game.buttons.redo": "重做 (Y)",
        "game.buttons.hint": "💡 提示 (I)",
        "game.feedback.controls": "控制方式: {scheme}",
        "game.win.all_done": "恭喜! 已完成所有關卡",
        # Level Selector
        "level_selector.title": "選擇關卡",
        "level_selector.back": "返回",
        "level_selector.import": "匯入關卡",
        "level_selector.prev_page": "◀ 上一頁",
        "level_selector.next_page": "下一頁 ▶",
        "level_selector.page_indicator": "頁面: {current} / {total}",
        "level_selector.page_hint": "換頁：Tab / Shift+Tab 或 PageUp / PageDown",
        "level_selector.edit": "編輯",
        "level_selector.delete": "刪除",
        "level_selector.no_map": "無地圖",
        "level_selector.custom_level": "自訂關卡",
        "level_selector.locked": "🔒 尚未解鎖",
        "level_selector.completed": "已完成 · 最佳: {moves} 步",
        "level_selector.uncompleted": "未完成",
        "level_selector.note_label": "說明: {note}",
        "level_selector.type_label": "類型: {type}",
        "level_selector.status_label": "狀態: {status}",
        "level_selector.boxes": "箱子",
        # Built-in difficulty and theme mapping
        "difficulty.Tutorial": "新手教學",
        "difficulty.Easy": "簡單",
        "difficulty.Medium": "中等",
        "difficulty.Hard": "困難",
        "difficulty.Expert": "專家",
        "theme.Tutorial": "新手村",
        "theme.Factory": "工業廠房",
        "theme.Garden": "綠意庭園",
        "theme.Warehouse": "古老倉庫",
        # Custom Level Dialog
        "custom_level.import_title": "匯入關卡",
        "custom_level.import_msg": "請在下方框內貼上（Ctrl+V）或輸入 PBX_ 關卡分享碼：",
        "custom_level.import_fail": "匯入失敗，請確認分享碼完整。({error})",
        "custom_level.import_hint": ("按下 Enter 鍵或點擊下方「確認匯入」即可載入。"),
        "custom_level.confirm": "確認匯入",
        "custom_level.cancel": "取消返回",
        # Level Editor
        "editor.title": "關卡編輯器",
        "editor.label_name": "關卡名稱:",
        "editor.label_tools": "選擇工具:",
        "editor.label_size": "地圖大小:",
        "editor.label_rows": "行數: {rows}",
        "editor.label_cols": "列數: {cols}",
        "editor.hints_title": "操作提示:",
        "editor.hint_mouse": "左鍵：放置 | 右鍵：清除",
        "editor.hint_tools": "1-5：切換工具",
        "editor.hint_undoredo": "Z：撤銷 | Y / R：重做",
        "editor.hint_save": "Ctrl + S：儲存關卡",
        "editor.hint_clear": "C：清空地圖",
        "editor.hint_playtest": "T：試玩關卡",
        "editor.hint_export": "E：匯出關卡",
        "editor.hint_exit": "Esc：離開編輯器",
        "editor.tool_wall": "牆壁 (1)",
        "editor.tool_floor": "地板 (2)",
        "editor.tool_target": "目標 (3)",
        "editor.tool_box": "箱子 (4)",
        "editor.tool_player": "玩家 (5)",
        "editor.btn_undo": "撤銷(Z)",
        "editor.btn_redo": "重做(Y)",
        "editor.btn_clear": "清除(C)",
        "editor.btn_playtest": "試玩(T)",
        "editor.btn_save": "儲存(S)",
        "editor.btn_exit": "退出",
        "editor.btn_export": "匯出關卡 (E)",
        "editor.status_undo": "撤銷",
        "editor.status_redo": "重做",
        "editor.status_cleared": "網格已清除",
        "editor.status_error_player": "錯誤: 必須放置玩家!",
        "editor.status_error_box": "錯誤: 至少需要一個箱子!",
        "editor.status_error_counts": (
            "無法儲存: 箱子({box_count})與目標({target_count})數量必須相同!"
        ),
        "editor.status_error_playtest_counts": (
            "無法試玩: 箱子({box_count})與目標({target_count})數量必須相同!"
        ),
        "editor.status_error_perimeter": ("無法匯出: 外圍邊界必須完全封閉為牆壁!"),
        "editor.status_error_name": "請輸入關卡名稱!",
        "editor.status_copied": "已複製至剪貼簿！",
        "editor.status_generated_manual": "分享碼已生成，請手動複製！",
        "editor.status_export_fail": "匯出失敗: {error}",
        "editor.confirm_title": "防呆警告",
        "editor.confirm_message": "地圖有未儲存的變更，確定要退出嗎？",
        "editor.confirm_yes": "確定退出 (Y)",
        "editor.confirm_no": "留在編輯 (N)",
        "editor.export_title": "匯出關卡分享碼",
        "editor.export_success": "分享碼已自動複製到您的剪貼簿！",
        "editor.export_manual_hint": (
            "若未成功，請點擊下方輸入框選取，或使用 Ctrl+C 手動複製："
        ),
        "editor.btn_copy_code": "複製分享碼",
        "editor.btn_close_window": "關閉視窗",
    },
}


def normalize_language(language: Optional[str]) -> str:
    """Normalize a language string to a supported language, defaulting to 'en'.

    Args:
        language: The raw language string.

    Returns:
        A supported language string.
    """
    if not language:
        return DEFAULT_LANGUAGE

    if language in SUPPORTED_LANGUAGES:
        return language

    # Check normalized string representation
    # (case-insensitive and handles underscores/hyphens)
    normalized = language.lower().replace("_", "-")
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower().replace("_", "-") == normalized:
            return lang

    return DEFAULT_LANGUAGE


def set_language(language: str) -> bool:
    """Set the active i18n language if supported.

    Args:
        language: The language key to set.

    Returns:
        True if set successfully, False otherwise.
    """
    if not language:
        return False

    if language in SUPPORTED_LANGUAGES:
        global _current_language
        _current_language = language
        return True

    # Try case-insensitive and dash-underscore normalization
    normalized = language.lower().replace("_", "-")
    for lang in SUPPORTED_LANGUAGES:
        if lang.lower().replace("_", "-") == normalized:
            _current_language = lang
            return True

    return False


def get_language() -> str:
    """Get current active language.

    Returns:
        The active language key.
    """
    return _current_language


def t(key: str, language: Optional[str] = None) -> str:
    """Translate a key into the target language with robust fallback.

    Args:
        key: The lookup translation key.
        language: Optional explicit language override.

    Returns:
        The translated string, fallback value, or key itself.
    """
    if language is not None:
        target_lang = normalize_language(language)
    else:
        target_lang = _current_language

    # 1. Look up in targeted language dictionary
    lang_dict = TRANSLATIONS.get(target_lang, {})
    if key in lang_dict:
        return lang_dict[key]

    # 2. If selected language lacks key and is not English, fallback to English
    if target_lang != DEFAULT_LANGUAGE:
        en_dict = TRANSLATIONS.get(DEFAULT_LANGUAGE, {})
        if key in en_dict:
            return en_dict[key]

    # 3. Fallback to key string itself to prevent crash
    return key
