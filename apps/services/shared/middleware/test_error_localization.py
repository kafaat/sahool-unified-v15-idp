"""
Test Error Localization System
اختبار نظام توطين الأخطاء

Simple tests to verify error localization is working correctly.
"""

from error_translations import (
    get_translation,
    get_bilingual_translation,
    parse_accept_language,
    ERROR_TRANSLATIONS,
)


def test_get_translation_english():
    """Test getting English translation"""
    message = get_translation("NOT_FOUND", "en")
    assert message == "Resource not found."
    print("✅ English translation works")


def test_get_translation_arabic():
    """Test getting Arabic translation"""
    message = get_translation("NOT_FOUND", "ar")
    assert message == "المورد غير موجود."
    print("✅ Arabic translation works")


def test_get_translation_fallback():
    """Test fallback for unknown error code"""
    message = get_translation("UNKNOWN_CODE", "en", "Default message")
    assert message == "Default message"
    print("✅ Translation fallback works")


def test_get_bilingual_translation():
    """Test getting both translations at once"""
    translations = get_bilingual_translation("VALIDATION_ERROR")
    assert "en" in translations
    assert "ar" in translations
    assert translations["en"] == "Validation failed. Please check your input."
    assert translations["ar"] == "فشل التحقق من الصحة. يرجى التحقق من المدخلات."
    print("✅ Bilingual translation works")


def test_parse_accept_language_simple():
    """Test parsing simple Accept-Language header"""
    # Test Arabic
    lang = parse_accept_language("ar")
    assert lang == "ar"

    # Test English
    lang = parse_accept_language("en")
    assert lang == "en"

    print("✅ Simple Accept-Language parsing works")


def test_parse_accept_language_complex():
    """Test parsing complex Accept-Language header"""
    # Arabic with higher priority
    lang = parse_accept_language("ar-SA,ar;q=0.9,en;q=0.8")
    assert lang == "ar"

    # English with higher priority
    lang = parse_accept_language("en-US,en;q=0.9,ar;q=0.5")
    assert lang == "en"

    print("✅ Complex Accept-Language parsing works")


def test_parse_accept_language_default():
    """Test default language when header is missing"""
    lang = parse_accept_language(None)
    assert lang == "en"

    lang = parse_accept_language("")
    assert lang == "en"

    print("✅ Default language fallback works")


def test_all_error_codes_have_translations():
    """Verify all error codes have both English and Arabic translations"""
    missing = []
    for code, translations in ERROR_TRANSLATIONS.items():
        if "en" not in translations:
            missing.append(f"{code} missing 'en'")
        if "ar" not in translations:
            missing.append(f"{code} missing 'ar'")
        if not translations.get("en"):
            missing.append(f"{code} has empty 'en'")
        if not translations.get("ar"):
            missing.append(f"{code} has empty 'ar'")

    if missing:
        print("❌ Missing translations:")
        for m in missing:
            print(f"  - {m}")
        assert False, f"Missing translations: {missing}"
    else:
        print(f"✅ All {len(ERROR_TRANSLATIONS)} error codes have complete translations")


def test_common_error_codes_exist():
    """Test that common error codes exist"""
    required_codes = [
        "VALIDATION_ERROR",
        "NOT_FOUND",
        "UNAUTHORIZED",
        "FORBIDDEN",
        "INTERNAL_ERROR",
        "BAD_REQUEST",
        "CONFLICT",
        "RATE_LIMIT_EXCEEDED",
    ]

    for code in required_codes:
        assert code in ERROR_TRANSLATIONS, f"Missing required error code: {code}"

    print(f"✅ All {len(required_codes)} common error codes exist")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SAHOOL Error Localization Tests")
    print("اختبارات توطين الأخطاء لنظام سهول")
    print("=" * 60 + "\n")

    # Run tests
    try:
        test_get_translation_english()
        test_get_translation_arabic()
        test_get_translation_fallback()
        test_get_bilingual_translation()
        test_parse_accept_language_simple()
        test_parse_accept_language_complex()
        test_parse_accept_language_default()
        test_all_error_codes_have_translations()
        test_common_error_codes_exist()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("✅ جميع الاختبارات نجحت!")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60 + "\n")
        raise
