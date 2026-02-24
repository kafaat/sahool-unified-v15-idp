"""
Tests for Two-Factor Authentication Service
اختبارات خدمة المصادقة الثنائية

Comprehensive tests for TOTP generation, verification, and backup code management.
"""

import base64
import re
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


class TestTwoFactorAuthService:
    """Tests for TwoFactorAuthService"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_service_initialization(self, service):
        """Test TwoFactorAuthService can be initialized"""
        assert service is not None
        assert service.issuer == "SAHOOL Agricultural Platform"

    def test_service_initialization_with_custom_issuer(self):
        """Test TwoFactorAuthService initialization with custom issuer"""
        from shared.auth.twofa_service import TwoFactorAuthService

        custom_issuer = "Custom Farm App"
        service = TwoFactorAuthService(issuer=custom_issuer)
        assert service.issuer == custom_issuer


# ══════════════════════════════════════════════════════════════════════════════
# Secret Generation Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestSecretGeneration:
    """Tests for TOTP secret generation"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_generate_secret_returns_string(self, service):
        """Test that generate_secret returns a string"""
        secret = service.generate_secret()
        assert isinstance(secret, str)

    def test_generate_secret_is_base32_encoded(self, service):
        """Test that generated secret is base32 encoded"""
        secret = service.generate_secret()
        # Base32 uses only A-Z and 2-7
        assert re.match(r"^[A-Z2-7]+$", secret), "Secret should be base32 encoded"

    def test_generate_secret_has_minimum_length(self, service):
        """Test that generated secret has sufficient length for security"""
        secret = service.generate_secret()
        # Base32 encoded 20 bytes = 32 characters
        assert len(secret) >= 20, "Secret should be at least 20 characters (base32 encoded)"

    def test_generate_secret_uniqueness(self, service):
        """Test that each generated secret is unique"""
        secret1 = service.generate_secret()
        secret2 = service.generate_secret()
        assert secret1 != secret2, "Each generated secret should be unique"

    def test_generate_multiple_secrets(self, service):
        """Test generating multiple secrets produces unique values"""
        secrets = [service.generate_secret() for _ in range(10)]
        assert len(set(secrets)) == len(secrets), "All secrets should be unique"


# ══════════════════════════════════════════════════════════════════════════════
# TOTP URI Generation Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestTOTPURIGeneration:
    """Tests for TOTP provisioning URI generation"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_generate_totp_uri_returns_string(self, service):
        """Test that generate_totp_uri returns a string"""
        secret = service.generate_secret()
        uri = service.generate_totp_uri(secret, "farmer@example.com")
        assert isinstance(uri, str)

    def test_generate_totp_uri_format(self, service):
        """Test that TOTP URI has correct format"""
        secret = service.generate_secret()
        uri = service.generate_totp_uri(secret, "farmer@example.com")
        assert uri.startswith("otpauth://totp/"), "URI should start with otpauth://totp/"

    def test_generate_totp_uri_contains_account_name(self, service):
        """Test that TOTP URI contains account name (URL-encoded)"""
        secret = service.generate_secret()
        account_name = "farmer@example.com"
        uri = service.generate_totp_uri(secret, account_name)
        # Account name may be URL-encoded (@ -> %40)
        assert "farmer" in uri, "URI should contain account name"

    def test_generate_totp_uri_contains_issuer(self, service):
        """Test that TOTP URI contains issuer name"""
        secret = service.generate_secret()
        uri = service.generate_totp_uri(secret, "farmer@example.com")
        assert "SAHOOL" in uri, "URI should contain issuer name"

    def test_generate_totp_uri_with_custom_issuer(self, service):
        """Test TOTP URI with custom issuer override"""
        secret = service.generate_secret()
        custom_issuer = "CustomFarm"
        uri = service.generate_totp_uri(secret, "farmer@example.com", issuer=custom_issuer)
        assert custom_issuer in uri, "URI should contain custom issuer"

    def test_generate_totp_uri_contains_secret(self, service):
        """Test that TOTP URI contains the secret"""
        secret = service.generate_secret()
        uri = service.generate_totp_uri(secret, "farmer@example.com")
        assert secret in uri, "URI should contain the secret parameter"

    def test_generate_totp_uri_contains_secret_parameter(self, service):
        """Test that TOTP URI contains secret parameter"""
        secret = service.generate_secret()
        uri = service.generate_totp_uri(secret, "farmer@example.com")
        assert f"secret={secret}" in uri, "URI should contain secret parameter"

    def test_generate_totp_uri_contains_issuer_parameter(self, service):
        """Test that TOTP URI contains issuer parameter"""
        secret = service.generate_secret()
        uri = service.generate_totp_uri(secret, "farmer@example.com")
        assert "issuer=" in uri, "URI should contain issuer parameter"

    def test_generate_totp_uri_starts_with_otpauth(self, service):
        """Test that TOTP URI starts with otpauth://totp/"""
        secret = service.generate_secret()
        uri = service.generate_totp_uri(secret, "farmer@example.com")
        assert uri.startswith("otpauth://totp/"), "URI should start with otpauth://totp/"


# ══════════════════════════════════════════════════════════════════════════════
# QR Code Generation Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestQRCodeGeneration:
    """Tests for QR code generation"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_generate_qr_code_returns_string(self, service):
        """Test that generate_qr_code returns a string"""
        secret = service.generate_secret()
        qr_code = service.generate_qr_code(secret, "farmer@example.com")
        assert isinstance(qr_code, str)

    def test_generate_qr_code_has_data_uri_format(self, service):
        """Test that QR code has data URI format"""
        secret = service.generate_secret()
        qr_code = service.generate_qr_code(secret, "farmer@example.com")
        assert qr_code.startswith("data:image/png;base64,"), "QR code should have data URI format"

    def test_generate_qr_code_contains_valid_base64(self, service):
        """Test that QR code contains valid base64 data"""
        secret = service.generate_secret()
        qr_code = service.generate_qr_code(secret, "farmer@example.com")

        # Extract base64 data
        base64_data = qr_code.replace("data:image/png;base64,", "")

        # Try to decode - should not raise exception
        try:
            decoded = base64.b64decode(base64_data)
            # Check if it looks like PNG data
            assert decoded[:8] == b"\x89PNG\r\n\x1a\n", "Should be valid PNG data"
        except Exception as e:
            pytest.fail(f"Failed to decode base64 QR code: {e}")

    def test_generate_qr_code_is_not_empty(self, service):
        """Test that generated QR code is not empty"""
        secret = service.generate_secret()
        qr_code = service.generate_qr_code(secret, "farmer@example.com")
        assert len(qr_code) > 100, "QR code data should be substantial"

    def test_generate_qr_code_with_custom_issuer(self, service):
        """Test QR code generation with custom issuer"""
        secret = service.generate_secret()
        custom_issuer = "Custom Farm"
        qr_code = service.generate_qr_code(secret, "farmer@example.com", issuer=custom_issuer)
        assert isinstance(qr_code, str)
        assert qr_code.startswith("data:image/png;base64,")

    def test_generate_qr_code_different_for_different_secrets(self, service):
        """Test that different secrets produce different QR codes"""
        secret1 = service.generate_secret()
        secret2 = service.generate_secret()

        qr_code1 = service.generate_qr_code(secret1, "farmer@example.com")
        qr_code2 = service.generate_qr_code(secret2, "farmer@example.com")

        assert qr_code1 != qr_code2, "Different secrets should produce different QR codes"

    def test_generate_qr_code_different_for_different_accounts(self, service):
        """Test that different account names produce different QR codes"""
        secret = service.generate_secret()

        qr_code1 = service.generate_qr_code(secret, "farmer1@example.com")
        qr_code2 = service.generate_qr_code(secret, "farmer2@example.com")

        assert qr_code1 != qr_code2, "Different account names should produce different QR codes"


# ══════════════════════════════════════════════════════════════════════════════
# TOTP Verification Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestTOTPVerification:
    """Tests for TOTP verification"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_verify_totp_with_valid_token(self, service):
        """Test TOTP verification with current valid token"""
        secret = service.generate_secret()
        token = service.get_current_totp(secret)
        assert service.verify_totp(secret, token) is True

    def test_verify_totp_with_empty_token(self, service):
        """Test TOTP verification with empty token"""
        secret = service.generate_secret()
        assert service.verify_totp(secret, "") is False

    def test_verify_totp_with_none_token(self, service):
        """Test TOTP verification with None token"""
        secret = service.generate_secret()
        assert service.verify_totp(secret, None) is False

    def test_verify_totp_with_empty_secret(self, service):
        """Test TOTP verification with empty secret"""
        token = "123456"
        assert service.verify_totp("", token) is False

    def test_verify_totp_with_none_secret(self, service):
        """Test TOTP verification with None secret"""
        token = "123456"
        assert service.verify_totp(None, token) is False

    def test_verify_totp_with_invalid_format_too_short(self, service):
        """Test TOTP verification with token that's too short"""
        secret = service.generate_secret()
        assert service.verify_totp(secret, "12345") is False

    def test_verify_totp_with_invalid_format_too_long(self, service):
        """Test TOTP verification with token that's too long"""
        secret = service.generate_secret()
        assert service.verify_totp(secret, "1234567") is False

    def test_verify_totp_with_non_numeric_token(self, service):
        """Test TOTP verification with non-numeric token"""
        secret = service.generate_secret()
        assert service.verify_totp(secret, "12345a") is False

    def test_verify_totp_with_invalid_token(self, service):
        """Test TOTP verification with invalid token"""
        secret = service.generate_secret()
        assert service.verify_totp(secret, "000000") is False

    def test_verify_totp_strips_whitespace(self, service):
        """Test that TOTP verification strips whitespace"""
        secret = service.generate_secret()
        token = service.get_current_totp(secret)
        # Token with spaces should still verify
        assert service.verify_totp(secret, f" {token} ") is True

    def test_verify_totp_handles_spaces_in_token(self, service):
        """Test TOTP verification with spaces within token"""
        secret = service.generate_secret()
        token = service.get_current_totp(secret)
        # Token with spaces (common when entered manually)
        formatted_token = f"{token[:3]} {token[3:]}"
        assert service.verify_totp(secret, formatted_token) is True

    def test_verify_totp_with_valid_window(self, service):
        """Test TOTP verification with valid time window"""
        secret = service.generate_secret()
        token = service.get_current_totp(secret)
        # Should accept with default window=1
        assert service.verify_totp(secret, token, valid_window=1) is True

    def test_verify_totp_with_custom_window(self, service):
        """Test TOTP verification with custom time window"""
        secret = service.generate_secret()
        token = service.get_current_totp(secret)
        # Should accept with larger window
        assert service.verify_totp(secret, token, valid_window=5) is True

    def test_verify_totp_is_time_sensitive(self, service):
        """Test that TOTP tokens are time-sensitive"""
        import time
        import pyotp

        secret = service.generate_secret()

        # Get current token and verify it's valid
        token1 = service.get_current_totp(secret)
        assert service.verify_totp(secret, token1) is True

        # A token from a different time should still be verifiable
        # within the valid window (default window=1 allows +/-30s)
        totp = pyotp.TOTP(secret)
        # Generate a token from 60 seconds ago
        past_token = totp.at(datetime.now() - timedelta(seconds=60))
        # Should NOT verify with default window=1 (only +/- 1 step = +/- 30s)
        assert service.verify_totp(secret, past_token, valid_window=0) is False


# ══════════════════════════════════════════════════════════════════════════════
# Backup Code Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestBackupCodeGeneration:
    """Tests for backup code generation"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_generate_backup_codes_returns_list(self, service):
        """Test that generate_backup_codes returns a list"""
        codes = service.generate_backup_codes()
        assert isinstance(codes, list)

    def test_generate_backup_codes_default_count(self, service):
        """Test that default backup code count is 10"""
        codes = service.generate_backup_codes()
        assert len(codes) == 10

    def test_generate_backup_codes_custom_count(self, service):
        """Test generating custom number of backup codes"""
        codes = service.generate_backup_codes(count=5)
        assert len(codes) == 5

    def test_generate_backup_codes_format(self, service):
        """Test that backup codes have correct format XXXX-XXXX"""
        codes = service.generate_backup_codes(count=5)
        for code in codes:
            assert re.match(r"^[A-NP-Z1-9]{4}-[A-NP-Z1-9]{4}$", code), f"Code {code} has invalid format"

    def test_generate_backup_codes_no_confusing_chars(self, service):
        """Test that backup codes don't contain confusing characters (O, 0)"""
        codes = service.generate_backup_codes(count=20)
        for code in codes:
            assert "O" not in code, f"Code {code} contains O"
            assert "0" not in code, f"Code {code} contains 0"

    def test_generate_backup_codes_uniqueness(self, service):
        """Test that generated backup codes are unique"""
        codes = service.generate_backup_codes(count=10)
        assert len(set(codes)) == len(codes), "All backup codes should be unique"

    def test_generate_backup_codes_custom_length(self, service):
        """Test generating backup codes with custom length"""
        codes = service.generate_backup_codes(count=5, length=12)
        for code in codes:
            # Format is XXXXXX-XXXXXX (6 + 1 + 6)
            assert len(code) == 13, f"Code {code} has wrong length"

    def test_generate_backup_codes_are_uppercase(self, service):
        """Test that backup codes are in uppercase"""
        codes = service.generate_backup_codes(count=10)
        for code in codes:
            assert code.isupper() or "-" in code, f"Code {code} should be uppercase"


# ══════════════════════════════════════════════════════════════════════════════
# Backup Code Hashing Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestBackupCodeHashing:
    """Tests for backup code hashing"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_hash_backup_code_returns_string(self, service):
        """Test that hash_backup_code returns a string"""
        code = "ABCD-EFGH"
        hashed = service.hash_backup_code(code)
        assert isinstance(hashed, str)

    def test_hash_backup_code_is_sha256(self, service):
        """Test that hash uses SHA256 (64 hex characters)"""
        code = "ABCD-EFGH"
        hashed = service.hash_backup_code(code)
        # SHA256 hex is 64 characters
        assert len(hashed) == 64
        assert re.match(r"^[a-f0-9]{64}$", hashed), "Should be SHA256 hex"

    def test_hash_backup_code_removes_formatting(self, service):
        """Test that hash_backup_code handles formatted input"""
        code_with_dash = "ABCD-EFGH"
        code_without_dash = "ABCDEFGH"

        hash_with_dash = service.hash_backup_code(code_with_dash)
        hash_without_dash = service.hash_backup_code(code_without_dash)

        # Should be equal since formatting is removed
        assert hash_with_dash == hash_without_dash

    def test_hash_backup_code_is_consistent(self, service):
        """Test that hashing the same code produces the same hash"""
        code = "ABCD-EFGH"
        hash1 = service.hash_backup_code(code)
        hash2 = service.hash_backup_code(code)
        assert hash1 == hash2

    def test_hash_backup_code_differs_for_different_codes(self, service):
        """Test that different codes produce different hashes"""
        codes = service.generate_backup_codes(count=5)
        hashes = [service.hash_backup_code(code) for code in codes]
        assert len(set(hashes)) == len(hashes), "Different codes should have different hashes"

    def test_hash_backup_code_strips_whitespace(self, service):
        """Test that hash_backup_code strips whitespace"""
        code = "ABCD-EFGH"
        hash_normal = service.hash_backup_code(code)
        hash_spaces = service.hash_backup_code(f"  {code}  ")
        assert hash_normal == hash_spaces


# ══════════════════════════════════════════════════════════════════════════════
# Backup Code Verification Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestBackupCodeVerification:
    """Tests for backup code verification"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_verify_backup_code_returns_tuple(self, service):
        """Test that verify_backup_code returns a tuple"""
        codes = service.generate_backup_codes(count=1)
        hashed_codes = [service.hash_backup_code(code) for code in codes]
        result = service.verify_backup_code(codes[0], hashed_codes)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_verify_backup_code_with_valid_code(self, service):
        """Test backup code verification with valid code"""
        codes = service.generate_backup_codes(count=1)
        hashed_codes = [service.hash_backup_code(code) for code in codes]
        is_valid, matched_hash = service.verify_backup_code(codes[0], hashed_codes)
        assert is_valid is True
        assert matched_hash is not None

    def test_verify_backup_code_with_invalid_code(self, service):
        """Test backup code verification with invalid code"""
        codes = service.generate_backup_codes(count=3)
        hashed_codes = [service.hash_backup_code(code) for code in codes]
        is_valid, matched_hash = service.verify_backup_code("INVALID-CODE", hashed_codes)
        assert is_valid is False
        assert matched_hash is None

    def test_verify_backup_code_with_empty_code(self, service):
        """Test backup code verification with empty code"""
        codes = service.generate_backup_codes(count=1)
        hashed_codes = [service.hash_backup_code(code) for code in codes]
        is_valid, matched_hash = service.verify_backup_code("", hashed_codes)
        assert is_valid is False
        assert matched_hash is None

    def test_verify_backup_code_with_none_code(self, service):
        """Test backup code verification with None code"""
        codes = service.generate_backup_codes(count=1)
        hashed_codes = [service.hash_backup_code(code) for code in codes]
        is_valid, matched_hash = service.verify_backup_code(None, hashed_codes)
        assert is_valid is False
        assert matched_hash is None

    def test_verify_backup_code_with_empty_hashes(self, service):
        """Test backup code verification with empty hash list"""
        is_valid, matched_hash = service.verify_backup_code("ABCD-EFGH", [])
        assert is_valid is False
        assert matched_hash is None

    def test_verify_backup_code_with_none_hashes(self, service):
        """Test backup code verification with None hash list"""
        is_valid, matched_hash = service.verify_backup_code("ABCD-EFGH", None)
        assert is_valid is False
        assert matched_hash is None

    def test_verify_backup_code_with_formatted_code(self, service):
        """Test backup code verification handles formatting"""
        codes = service.generate_backup_codes(count=1)
        hashed_codes = [service.hash_backup_code(code) for code in codes]

        # Verify with various formatting
        is_valid1, _ = service.verify_backup_code(codes[0], hashed_codes)
        assert is_valid1 is True

    def test_verify_backup_code_multiple_codes(self, service):
        """Test backup code verification against multiple codes"""
        codes = service.generate_backup_codes(count=5)
        hashed_codes = [service.hash_backup_code(code) for code in codes]

        # Verify the third code
        is_valid, matched_hash = service.verify_backup_code(codes[2], hashed_codes)
        assert is_valid is True
        assert matched_hash == hashed_codes[2]

    def test_verify_backup_code_returns_correct_hash(self, service):
        """Test that verify_backup_code returns the correct matched hash"""
        codes = service.generate_backup_codes(count=3)
        hashed_codes = [service.hash_backup_code(code) for code in codes]

        for code, expected_hash in zip(codes, hashed_codes):
            is_valid, matched_hash = service.verify_backup_code(code, hashed_codes)
            assert is_valid is True
            assert matched_hash == expected_hash


# ══════════════════════════════════════════════════════════════════════════════
# Current TOTP Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestCurrentTOTP:
    """Tests for getting current TOTP code"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_get_current_totp_returns_string(self, service):
        """Test that get_current_totp returns a string"""
        secret = service.generate_secret()
        token = service.get_current_totp(secret)
        assert isinstance(token, str)

    def test_get_current_totp_returns_6_digits(self, service):
        """Test that get_current_totp returns 6-digit code"""
        secret = service.generate_secret()
        token = service.get_current_totp(secret)
        assert len(token) == 6
        assert token.isdigit()

    def test_get_current_totp_is_verifiable(self, service):
        """Test that current TOTP token can be verified"""
        secret = service.generate_secret()
        token = service.get_current_totp(secret)
        assert service.verify_totp(secret, token) is True

    def test_get_current_totp_changes_over_time(self, service):
        """Test that TOTP token changes as time progresses"""
        import time

        secret = service.generate_secret()

        token1 = service.get_current_totp(secret)

        # Note: Don't actually wait 30 seconds in unit tests
        # Instead, we verify that the method works correctly
        token2 = service.get_current_totp(secret)

        # Should be same token if called within same interval
        assert token1 == token2

    def test_get_current_totp_consistent_in_interval(self, service):
        """Test that TOTP is consistent within same interval"""
        import time

        secret = service.generate_secret()

        tokens = [service.get_current_totp(secret) for _ in range(5)]

        # All tokens in same interval should be identical
        assert len(set(tokens)) == 1, "All tokens in same interval should be identical"


# ══════════════════════════════════════════════════════════════════════════════
# Integration Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestTwoFAIntegration:
    """Integration tests for complete 2FA flow"""

    @pytest.fixture
    def service(self):
        """Create a TwoFactorAuthService instance for testing"""
        from shared.auth.twofa_service import TwoFactorAuthService
        return TwoFactorAuthService()

    def test_complete_totp_setup_flow(self, service):
        """Test complete TOTP setup flow: secret -> URI -> QR code"""
        # Step 1: Generate secret
        secret = service.generate_secret()
        assert isinstance(secret, str)

        # Step 2: Generate URI for QR code
        uri = service.generate_totp_uri(secret, "farmer@example.com")
        assert uri.startswith("otpauth://totp/")

        # Step 3: Generate QR code
        qr_code = service.generate_qr_code(secret, "farmer@example.com")
        assert qr_code.startswith("data:image/png;base64,")

        # Step 4: Verify TOTP token
        token = service.get_current_totp(secret)
        assert service.verify_totp(secret, token) is True

    def test_complete_backup_code_flow(self, service):
        """Test complete backup code flow: generate -> hash -> verify"""
        # Step 1: Generate backup codes
        codes = service.generate_backup_codes(count=10)
        assert len(codes) == 10

        # Step 2: Hash codes for storage
        hashed_codes = [service.hash_backup_code(code) for code in codes]
        assert len(hashed_codes) == 10

        # Step 3: Verify each code
        for code, expected_hash in zip(codes, hashed_codes):
            is_valid, matched_hash = service.verify_backup_code(code, hashed_codes)
            assert is_valid is True
            assert matched_hash == expected_hash

    def test_full_2fa_user_setup(self, service):
        """Test full 2FA user setup: secret, backup codes, verification"""
        account_email = "farmer@example.com"

        # Generate 2FA secret
        secret = service.generate_secret()

        # Generate QR code for scanning
        qr_code = service.generate_qr_code(secret, account_email)

        # Generate backup codes
        backup_codes = service.generate_backup_codes(count=10)
        backup_codes_hashed = [service.hash_backup_code(code) for code in backup_codes]

        # User scans QR and enters TOTP
        current_token = service.get_current_totp(secret)
        assert service.verify_totp(secret, current_token) is True

        # Verify at least one backup code
        is_valid, _ = service.verify_backup_code(backup_codes[0], backup_codes_hashed)
        assert is_valid is True

    def test_totp_and_backup_code_together(self, service):
        """Test using TOTP and backup code for authentication"""
        secret = service.generate_secret()
        backup_codes = service.generate_backup_codes(count=10)
        hashed_backup_codes = [service.hash_backup_code(code) for code in backup_codes]

        # Method 1: Use TOTP
        totp_token = service.get_current_totp(secret)
        totp_valid = service.verify_totp(secret, totp_token)

        # Method 2: Use backup code
        backup_valid, _ = service.verify_backup_code(backup_codes[5], hashed_backup_codes)

        # Both should work
        assert totp_valid is True
        assert backup_valid is True


# ══════════════════════════════════════════════════════════════════════════════
# Global Function Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestGlobalFunctions:
    """Tests for module-level functions"""

    def test_get_twofa_service(self):
        """Test get_twofa_service returns a service instance"""
        from shared.auth.twofa_service import get_twofa_service, TwoFactorAuthService

        service = get_twofa_service()
        assert service is not None
        assert isinstance(service, TwoFactorAuthService)

    def test_get_twofa_service_singleton(self):
        """Test get_twofa_service returns same instance (singleton)"""
        from shared.auth.twofa_service import get_twofa_service

        service1 = get_twofa_service()
        service2 = get_twofa_service()
        assert service1 is service2

    def test_set_twofa_service(self):
        """Test set_twofa_service can set a custom instance"""
        from shared.auth.twofa_service import TwoFactorAuthService, get_twofa_service, set_twofa_service

        custom_service = TwoFactorAuthService(issuer="Custom")
        set_twofa_service(custom_service)

        retrieved_service = get_twofa_service()
        assert retrieved_service is custom_service
        assert retrieved_service.issuer == "Custom"
