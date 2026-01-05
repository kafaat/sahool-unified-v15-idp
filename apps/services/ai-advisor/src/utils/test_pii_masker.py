"""
Test script for PII Masker
برنامج اختبار لإخفاء المعلومات الشخصية

Run this script to verify PII masking is working correctly:
    python -m src.utils.test_pii_masker
"""

from pii_masker import PIIMasker, safe_log


def test_email_masking():
    """Test email masking"""
    text = "Contact me at john.doe@example.com for more info"
    masked = PIIMasker.mask_text(text)
    print(f"Original: {text}")
    print(f"Masked:   {masked}\n")
    assert "[EMAIL]" in masked
    assert "john.doe@example.com" not in masked


def test_phone_masking():
    """Test phone number masking"""
    text = "Call me at +1-555-123-4567 or (555) 987-6543"
    masked = PIIMasker.mask_text(text)
    print(f"Original: {text}")
    print(f"Masked:   {masked}\n")
    assert "[PHONE]" in masked


def test_api_key_masking():
    """Test API key masking"""
    text = "Use this key: sk-1234567890abcdefghij1234567890"
    masked = PIIMasker.mask_text(text)
    print(f"Original: {text}")
    print(f"Masked:   {masked}\n")
    assert "[API_KEY]" in masked
    assert "sk-1234567890abcdefghij1234567890" not in masked


def test_password_masking():
    """Test password masking"""
    text = 'password="SuperSecret123"'
    masked = PIIMasker.mask_text(text)
    print(f"Original: {text}")
    print(f"Masked:   {masked}\n")
    assert "[PASSWORD]" in masked
    assert "SuperSecret123" not in masked


def test_jwt_masking():
    """Test JWT token masking"""
    text = "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    masked = PIIMasker.mask_text(text)
    print(f"Original: {text}")
    print(f"Masked:   {masked}\n")
    assert "[JWT]" in masked


def test_dict_masking():
    """Test dictionary masking"""
    data = {
        "username": "farmer1",
        "email": "farmer@example.com",
        "password": "secret123",
        "api_key": "sk-abc123def456ghi789",
        "phone": "+966-555-1234",
        "nested": {
            "credit_card": "4532-1234-5678-9010",
            "authorization": "Bearer token123",
        },
    }

    print("Original dict:")
    print(data)

    masked = PIIMasker.mask_dict(data)
    print("\nMasked dict:")
    print(masked)
    print()

    assert masked["email"] == "[EMAIL]"
    assert masked["password"] == "[REDACTED]"
    assert masked["api_key"] == "[REDACTED]"
    assert "[PHONE]" in masked["phone"]
    assert "[CARD]" in masked["nested"]["credit_card"]
    assert masked["nested"]["authorization"] == "[REDACTED]"


def test_safe_log_helper():
    """Test safe_log helper function"""
    # Test with string
    sensitive_text = "User john@example.com logged in with password: secret123"
    safe = safe_log(sensitive_text)
    print(f"Safe log (string): {safe}\n")
    assert "[EMAIL]" in safe
    assert "[PASSWORD]" in safe

    # Test with dict
    sensitive_data = {
        "user": "john@example.com",
        "token": "abc123xyz",
        "action": "login",
    }
    safe = safe_log(sensitive_data)
    print(f"Safe log (dict): {safe}\n")
    assert "[EMAIL]" in safe
    assert "[REDACTED]" in safe


if __name__ == "__main__":
    print("=" * 60)
    print("PII Masker Test Suite")
    print("مجموعة اختبارات إخفاء المعلومات الشخصية")
    print("=" * 60)
    print()

    try:
        test_email_masking()
        print("✓ Email masking test passed")

        test_phone_masking()
        print("✓ Phone masking test passed")

        test_api_key_masking()
        print("✓ API key masking test passed")

        test_password_masking()
        print("✓ Password masking test passed")

        test_jwt_masking()
        print("✓ JWT masking test passed")

        test_dict_masking()
        print("✓ Dictionary masking test passed")

        test_safe_log_helper()
        print("✓ Safe log helper test passed")

        print()
        print("=" * 60)
        print("All tests passed! PII masking is working correctly.")
        print("جميع الاختبارات نجحت! إخفاء المعلومات الشخصية يعمل بشكل صحيح.")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise
