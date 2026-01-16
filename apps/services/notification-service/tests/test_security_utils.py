"""
Tests for SAHOOL Security Utilities
اختبارات أدوات الأمان

Tests for:
- Log injection prevention (sanitize_for_log)
- Phone number masking (mask_phone)
- Email address masking (mask_email)
- Identifier masking (mask_identifier)
- Dictionary sanitization (sanitize_dict_for_log)
"""

import pytest
from src.security_utils import (
    mask_email,
    mask_identifier,
    mask_phone,
    sanitize_dict_for_log,
    sanitize_for_log,
)


# ═══════════════════════════════════════════════════════════════════════════════
# sanitize_for_log Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSanitizeForLog:
    """Tests for sanitize_for_log function"""

    def test_removes_newlines(self):
        """Should replace newlines with escaped version"""
        input_value = "line1\nline2\nline3"
        result = sanitize_for_log(input_value)
        assert "\n" not in result
        assert "\\n" in result

    def test_removes_carriage_returns(self):
        """Should replace carriage returns with escaped version"""
        input_value = "line1\rline2"
        result = sanitize_for_log(input_value)
        assert "\r" not in result
        assert "\\r" in result

    def test_removes_control_characters(self):
        """Should remove control characters (ASCII 0-31 and 127)"""
        input_value = "test\x00\x01\x1f\x7fvalue"
        result = sanitize_for_log(input_value)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x1f" not in result
        assert "\x7f" not in result
        assert "testvalue" in result

    def test_truncates_long_values(self):
        """Should truncate values exceeding max_length"""
        long_value = "a" * 200
        result = sanitize_for_log(long_value, max_length=100)
        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")

    def test_handles_none(self):
        """Should handle None values"""
        result = sanitize_for_log(None)
        assert result == "[None]"

    def test_handles_non_string_types(self):
        """Should convert non-string types to string"""
        assert sanitize_for_log(123) == "123"
        assert sanitize_for_log(12.5) == "12.5"
        assert sanitize_for_log(True) == "True"

    def test_prevents_log_forging_attack(self):
        """Should prevent log forging attacks with embedded newlines"""
        # Attack: try to inject fake log entry
        attack = "normal value\n[CRITICAL] fake log entry"
        result = sanitize_for_log(attack)
        # The newline should be escaped, preventing log forging
        assert "[CRITICAL]" in result  # Still present
        assert "\n" not in result  # But newline is escaped


# ═══════════════════════════════════════════════════════════════════════════════
# mask_phone Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMaskPhone:
    """Tests for mask_phone function"""

    def test_masks_phone_showing_last_4_digits(self):
        """Should show only last 4 digits"""
        result = mask_phone("+967712345678")
        assert result == "***5678"

    def test_handles_short_phone(self):
        """Should handle phones shorter than 4 digits"""
        result = mask_phone("123")
        assert result == "****"

    def test_handles_none(self):
        """Should handle None"""
        result = mask_phone(None)
        assert result == "****"

    def test_handles_empty_string(self):
        """Should handle empty string"""
        result = mask_phone("")
        assert result == "****"

    def test_sanitizes_before_masking(self):
        """Should sanitize phone before masking (prevent log injection)"""
        # Try to inject via phone number
        malicious_phone = "+967712\nFAKE LOG ENTRY\n5678"
        result = mask_phone(malicious_phone)
        assert "\n" not in result


# ═══════════════════════════════════════════════════════════════════════════════
# mask_email Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMaskEmail:
    """Tests for mask_email function"""

    def test_masks_email_correctly(self):
        """Should mask email showing first and last char of local part"""
        result = mask_email("user@example.com")
        assert result == "u***r@example.com"

    def test_handles_short_local_part(self):
        """Should handle short local parts (2 or fewer chars)"""
        result = mask_email("ab@example.com")
        assert result == "***@example.com"

    def test_handles_single_char_local_part(self):
        """Should handle single character local part"""
        result = mask_email("a@example.com")
        assert result == "***@example.com"

    def test_handles_none(self):
        """Should handle None"""
        result = mask_email(None)
        assert result == "***@***"

    def test_handles_empty_string(self):
        """Should handle empty string"""
        result = mask_email("")
        assert result == "***@***"

    def test_handles_invalid_email_no_at(self):
        """Should handle invalid email without @"""
        result = mask_email("invalid_email")
        assert result == "***@***"

    def test_sanitizes_before_masking(self):
        """Should sanitize email before masking (prevent log injection)"""
        malicious_email = "user\nFAKE LOG@example.com"
        result = mask_email(malicious_email)
        assert "\n" not in result


# ═══════════════════════════════════════════════════════════════════════════════
# mask_identifier Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMaskIdentifier:
    """Tests for mask_identifier function"""

    def test_detects_email_and_masks_appropriately(self):
        """Should detect email and use email masking"""
        result = mask_identifier("user@example.com")
        assert "@" in result
        assert "u***r@example.com" == result

    def test_detects_phone_and_masks_appropriately(self):
        """Should detect phone and use phone masking"""
        result = mask_identifier("+967712345678")
        assert "@" not in result
        assert "***5678" == result

    def test_handles_none(self):
        """Should handle None"""
        result = mask_identifier(None)
        assert result == "***"


# ═══════════════════════════════════════════════════════════════════════════════
# sanitize_dict_for_log Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSanitizeDictForLog:
    """Tests for sanitize_dict_for_log function"""

    def test_sanitizes_regular_values(self):
        """Should sanitize regular values"""
        data = {"name": "test\nvalue", "count": 123}
        result = sanitize_dict_for_log(data)
        assert "\n" not in str(result)

    def test_redacts_password_field(self):
        """Should redact password fields"""
        data = {"password": "secret123"}
        result = sanitize_dict_for_log(data)
        assert result["password"] == "[REDACTED]"

    def test_redacts_token_field(self):
        """Should redact token fields"""
        data = {"token": "abc123xyz"}
        result = sanitize_dict_for_log(data)
        assert result["token"] == "[REDACTED]"

    def test_masks_phone_fields(self):
        """Should mask phone fields"""
        data = {"phone": "+967712345678"}
        result = sanitize_dict_for_log(data)
        assert "***" in result["phone"]
        assert "5678" in result["phone"]

    def test_masks_email_fields(self):
        """Should mask email fields"""
        data = {"email": "user@example.com"}
        result = sanitize_dict_for_log(data)
        assert "@" in result["email"]
        assert "***" in result["email"]

    def test_handles_nested_dict(self):
        """Should handle nested dictionaries"""
        data = {"user": {"password": "secret", "name": "test"}}
        result = sanitize_dict_for_log(data)
        assert result["user"]["password"] == "[REDACTED]"
        assert result["user"]["name"] == "test"

    def test_handles_identifier_field(self):
        """Should handle identifier field (email or phone)"""
        # Email identifier
        result = sanitize_dict_for_log({"identifier": "user@example.com"})
        assert "@" in result["identifier"]

        # Phone identifier
        result = sanitize_dict_for_log({"identifier": "+967712345678"})
        assert "***" in result["identifier"]

    def test_custom_sensitive_keys(self):
        """Should use custom sensitive keys when provided"""
        data = {"custom_secret": "hidden", "other": "visible"}
        result = sanitize_dict_for_log(data, sensitive_keys={"custom_secret"})
        assert result["custom_secret"] == "[REDACTED]"
        assert result["other"] == "visible"


# ═══════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSecurityIntegration:
    """Integration tests for security utilities"""

    def test_full_log_sanitization_workflow(self):
        """Test complete workflow of sanitizing user data for logging"""
        # Simulate user data that might be logged
        user_data = {
            "email": "attacker\n[CRITICAL] FAKE@example.com",
            "phone": "+967\nFAKE LOG712345678",
            "password": "super_secret",
            "otp": "123456",
            "message": "Normal message\nwith newlines",
        }

        result = sanitize_dict_for_log(user_data)

        # Verify no raw newlines in output
        result_str = str(result)
        assert "\n" not in result_str

        # Verify sensitive data is protected
        assert "super_secret" not in result_str
        assert "123456" not in result_str

        # Verify email and phone are masked
        assert "@" in result["email"]  # Email still recognizable as email
        assert result["password"] == "[REDACTED]"
        assert result["otp"] == "[REDACTED]"

    def test_prevents_log_injection_attack_scenario(self):
        """
        Test realistic log injection attack scenario.

        Attack: Attacker tries to inject fake log entries through user input
        to hide malicious activity or frame others.
        """
        # Attacker submits this as their phone number
        attack_payload = "+967712345678\n2025-01-16 10:00:00 [INFO] Admin user logged in from 192.168.1.1"

        # When this goes through our sanitization
        result = mask_phone(attack_payload)

        # The "fake log entry" should not appear on its own line
        assert "\n" not in result
        # Only last 4 chars should be visible
        assert "***" in result
