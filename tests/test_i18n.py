"""Unit tests for the i18n translation system."""

from src.pushbox.utils.i18n import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    TRANSLATIONS,
    get_language,
    normalize_language,
    set_language,
    t,
)


def test_i18n_default_language():
    """Verify that the default language is English."""
    # Reset to default state
    set_language("en")
    assert get_language() == "en"
    assert DEFAULT_LANGUAGE == "en"


def test_i18n_supported_languages():
    """Verify supported languages set includes en and zh-TW."""
    assert "en" in SUPPORTED_LANGUAGES
    assert "zh-TW" in SUPPORTED_LANGUAGES


def test_i18n_t_returns_english_by_default():
    """Verify t() returns English translation by default."""
    set_language("en")
    assert t("main_menu.start") == "Start Game"
    assert t("main_menu.level_select") == "Select Level"


def test_i18n_explicit_language_override():
    """Verify explicit language override t(key, "zh-TW") works."""
    set_language("en")  # active is English
    # override should return Chinese
    assert t("main_menu.start", "zh-TW") == "開始遊戲"


def test_i18n_fallback_to_english(monkeypatch):
    """Verify missing zh-TW key falls back to English."""
    # Create isolated translation dictionaries for the test
    mock_en = {
        "test.only_in_english": "English Only",
    }
    mock_zh = {
        # Absent key
    }

    # Safely isolate TRANSLATIONS mutations using monkeypatch
    monkeypatch.setitem(TRANSLATIONS, "en", mock_en)
    monkeypatch.setitem(TRANSLATIONS, "zh-TW", mock_zh)

    set_language("zh-TW")
    # Should fall back to English
    assert t("test.only_in_english") == "English Only"


def test_i18n_fallback_to_key_itself():
    """Verify key is returned if absent in both English and active language."""
    set_language("en")
    assert t("nonexistent.key.name") == "nonexistent.key.name"

    set_language("zh-TW")
    assert t("nonexistent.key.name") == "nonexistent.key.name"


def test_i18n_unsupported_language_no_crash():
    """Verify normalize and t do not crash on unsupported language."""
    assert normalize_language("fr") == "en"
    assert t("main_menu.start", "fr") == "Start Game"


def test_i18n_set_language_unsupported_fails():
    """Verify set_language('fr') returns False and does not alter active language."""
    set_language("zh-TW")
    assert get_language() == "zh-TW"

    # Attempt to set unsupported language
    success = set_language("fr")
    assert success is False
    assert get_language() == "zh-TW"  # remains Chinese


def test_i18n_normalization():
    """Verify normalization of language strings works for common case variations."""
    assert normalize_language("zh_tw") == "zh-TW"
    assert normalize_language("ZH-TW") == "zh-TW"
    assert normalize_language("zh-TW") == "zh-TW"
    assert normalize_language("en_US") == "en"
    assert normalize_language("en") == "en"
    assert normalize_language(None) == "en"
