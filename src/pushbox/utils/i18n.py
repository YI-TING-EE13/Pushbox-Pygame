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
