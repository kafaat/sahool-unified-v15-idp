"""
Tests for Password Hasher - Argon2id Migration
اختبارات معالج كلمات المرور - ترحيل Argon2id

Tests cover:
- Argon2id hashing and verification
- Backward compatibility with bcrypt
- Backward compatibility with PBKDF2
- Migration detection
- Security properties
"""

import pytest
import hashlib
import secrets
from typing import Tuple

# Import the password hasher
import sys

sys.path.insert(0, "/home/user/sahool-unified-v15-idp")

from shared.auth.password_hasher import (
    PasswordHasher,
    HashAlgorithm,
    get_password_hasher,
    hash_password,
    verify_password,
    needs_rehash,
    generate_otp,
    generate_secure_token,
    ARGON2_AVAILABLE,
    BCRYPT_AVAILABLE,
)


class TestPasswordHasher:
    """Test suite for PasswordHasher class"""

    def setup_method(self):
        """Setup test fixtures"""
        self.hasher = PasswordHasher()
        self.test_password = "TestPassword123!@#"
        self.test_passwords = [
            "SimplePass123",
            "Complex!Pass@2024#",
            "العربية123!",  # Arabic password
            "P@ssw0rd",
            "VeryLongPasswordWithManyCharacters123!@#$%^&*()",
        ]

    # ========== Argon2id Tests ==========

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_argon2_hash_password(self):
        """Test hashing with Argon2id"""
        hashed = self.hasher.hash_password(self.test_password)

        # Verify format
        assert hashed.startswith("$argon2")
        assert len(hashed) > 50

        # Verify algorithm detection
        algorithm = self.hasher._detect_algorithm(hashed)
        assert algorithm == HashAlgorithm.ARGON2ID

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_argon2_verify_correct_password(self):
        """Test verification of correct Argon2id password"""
        hashed = self.hasher.hash_password(self.test_password)
        is_valid, needs_migration = self.hasher.verify_password(
            self.test_password, hashed
        )

        assert is_valid is True
        assert needs_migration is False  # New hash shouldn't need migration

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_argon2_verify_incorrect_password(self):
        """Test verification of incorrect Argon2id password"""
        hashed = self.hasher.hash_password(self.test_password)
        is_valid, needs_migration = self.hasher.verify_password(
            "WrongPassword123!", hashed
        )

        assert is_valid is False
        assert needs_migration is False

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_argon2_unique_salts(self):
        """Test that each hash uses a unique salt"""
        hash1 = self.hasher.hash_password(self.test_password)
        hash2 = self.hasher.hash_password(self.test_password)

        # Same password should produce different hashes (different salts)
        assert hash1 != hash2

        # But both should verify correctly
        is_valid1, _ = self.hasher.verify_password(self.test_password, hash1)
        is_valid2, _ = self.hasher.verify_password(self.test_password, hash2)

        assert is_valid1 is True
        assert is_valid2 is True

    # ========== Bcrypt Compatibility Tests ==========

    @pytest.mark.skipif(not BCRYPT_AVAILABLE, reason="bcrypt not available")
    def test_bcrypt_backward_compatibility(self):
        """Test verification of legacy bcrypt hashes"""
        import bcrypt

        # Create a legacy bcrypt hash
        legacy_hash = bcrypt.hashpw(
            self.test_password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        # Verify it can be validated
        is_valid, needs_migration = self.hasher.verify_password(
            self.test_password, legacy_hash
        )

        assert is_valid is True
        assert needs_migration is True  # Should need migration to Argon2id

        # Verify algorithm detection
        algorithm = self.hasher._detect_algorithm(legacy_hash)
        assert algorithm == HashAlgorithm.BCRYPT

    @pytest.mark.skipif(not BCRYPT_AVAILABLE, reason="bcrypt not available")
    def test_bcrypt_incorrect_password(self):
        """Test bcrypt verification with incorrect password"""
        import bcrypt

        legacy_hash = bcrypt.hashpw(
            self.test_password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        is_valid, needs_migration = self.hasher.verify_password(
            "WrongPassword", legacy_hash
        )

        assert is_valid is False

    # ========== PBKDF2 Compatibility Tests ==========

    def test_pbkdf2_backward_compatibility(self):
        """Test verification of legacy PBKDF2 hashes"""
        # Create a legacy PBKDF2 hash
        salt = secrets.token_bytes(32)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            self.test_password.encode("utf-8"),
            salt,
            iterations=100_000,
            dklen=32,
        )
        legacy_hash = f"{salt.hex()}${hashed.hex()}"

        # Verify it can be validated
        is_valid, needs_migration = self.hasher.verify_password(
            self.test_password, legacy_hash
        )

        assert is_valid is True
        assert needs_migration is True  # Should need migration to Argon2id

        # Verify algorithm detection
        algorithm = self.hasher._detect_algorithm(legacy_hash)
        assert algorithm == HashAlgorithm.PBKDF2_SHA256

    def test_pbkdf2_incorrect_password(self):
        """Test PBKDF2 verification with incorrect password"""
        salt = secrets.token_bytes(32)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            self.test_password.encode("utf-8"),
            salt,
            iterations=100_000,
            dklen=32,
        )
        legacy_hash = f"{salt.hex()}${hashed.hex()}"

        is_valid, needs_migration = self.hasher.verify_password(
            "WrongPassword", legacy_hash
        )

        assert is_valid is False

    # ========== Migration Detection Tests ==========

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_needs_rehash_argon2(self):
        """Test rehash detection for Argon2id hashes"""
        hashed = self.hasher.hash_password(self.test_password)

        # New hash with current parameters shouldn't need rehash
        assert self.hasher.needs_rehash(hashed) is False

    @pytest.mark.skipif(not BCRYPT_AVAILABLE, reason="bcrypt not available")
    def test_needs_rehash_bcrypt(self):
        """Test that bcrypt hashes always need rehash"""
        import bcrypt

        legacy_hash = bcrypt.hashpw(
            self.test_password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        assert self.hasher.needs_rehash(legacy_hash) is True

    def test_needs_rehash_pbkdf2(self):
        """Test that PBKDF2 hashes always need rehash"""
        salt = secrets.token_bytes(32)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            self.test_password.encode("utf-8"),
            salt,
            iterations=100_000,
            dklen=32,
        )
        legacy_hash = f"{salt.hex()}${hashed.hex()}"

        assert self.hasher.needs_rehash(legacy_hash) is True

    # ========== Algorithm Detection Tests ==========

    def test_detect_algorithm_argon2(self):
        """Test detection of Argon2id algorithm"""
        test_hashes = [
            "$argon2id$v=19$m=65536,t=2,p=4$...",
            "$argon2i$v=19$m=4096,t=3,p=1$...",
        ]

        for hash_str in test_hashes:
            algorithm = self.hasher._detect_algorithm(hash_str)
            assert algorithm == HashAlgorithm.ARGON2ID

    def test_detect_algorithm_bcrypt(self):
        """Test detection of bcrypt algorithm"""
        test_hashes = [
            "$2a$12$abcdefghijklmnopqrstuv",
            "$2b$10$abcdefghijklmnopqrstuv",
            "$2y$12$abcdefghijklmnopqrstuv",
        ]

        for hash_str in test_hashes:
            algorithm = self.hasher._detect_algorithm(hash_str)
            assert algorithm == HashAlgorithm.BCRYPT

    def test_detect_algorithm_pbkdf2(self):
        """Test detection of PBKDF2 algorithm"""
        test_hash = "a" * 64 + "$" + "b" * 64  # salt$hash format

        algorithm = self.hasher._detect_algorithm(test_hash)
        assert algorithm == HashAlgorithm.PBKDF2_SHA256

    def test_detect_algorithm_unknown(self):
        """Test detection of unknown algorithm"""
        test_hashes = [
            "plaintext_password",  # No proper format
            "unknown_format_12345",
        ]

        for hash_str in test_hashes:
            algorithm = self.hasher._detect_algorithm(hash_str)
            assert algorithm == HashAlgorithm.UNKNOWN

    # ========== Security Tests ==========

    def test_empty_password_raises_error(self):
        """Test that empty password raises error"""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            self.hasher.hash_password("")

    def test_empty_verification_returns_false(self):
        """Test that empty password/hash returns False"""
        is_valid1, _ = self.hasher.verify_password("", "some_hash")
        is_valid2, _ = self.hasher.verify_password("password", "")

        assert is_valid1 is False
        assert is_valid2 is False

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_timing_attack_resistance(self):
        """Test timing attack resistance (basic check)"""
        import time

        hashed = self.hasher.hash_password(self.test_password)

        # Measure time for correct password
        start = time.perf_counter()
        self.hasher.verify_password(self.test_password, hashed)
        time_correct = time.perf_counter() - start

        # Measure time for incorrect password
        start = time.perf_counter()
        self.hasher.verify_password("WrongPassword", hashed)
        time_incorrect = time.perf_counter() - start

        # Times should be similar (within 10x factor)
        # Note: This is a basic check, not a comprehensive timing analysis
        ratio = max(time_correct, time_incorrect) / min(time_correct, time_incorrect)
        assert ratio < 10.0

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_multiple_passwords(self):
        """Test hashing and verification of multiple passwords"""
        for password in self.test_passwords:
            hashed = self.hasher.hash_password(password)
            is_valid, _ = self.hasher.verify_password(password, hashed)
            assert is_valid is True

            # Wrong password should fail
            is_valid, _ = self.hasher.verify_password(password + "wrong", hashed)
            assert is_valid is False

    # ========== Global Function Tests ==========

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_global_hash_password(self):
        """Test global hash_password function"""
        hashed = hash_password(self.test_password)
        assert hashed.startswith("$argon2")

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_global_verify_password(self):
        """Test global verify_password function"""
        hashed = hash_password(self.test_password)
        is_valid, needs_migration = verify_password(self.test_password, hashed)

        assert is_valid is True
        assert needs_migration is False

    def test_global_get_password_hasher(self):
        """Test that get_password_hasher returns same instance"""
        hasher1 = get_password_hasher()
        hasher2 = get_password_hasher()

        assert hasher1 is hasher2  # Should be singleton

    # ========== Utility Function Tests ==========

    def test_generate_otp(self):
        """Test OTP generation"""
        otp = generate_otp(6)

        assert len(otp) == 6
        assert otp.isdigit()

        # Test default length
        otp_default = generate_otp()
        assert len(otp_default) == 4

    def test_generate_secure_token(self):
        """Test secure token generation"""
        token = generate_secure_token(32)

        # Should be hex string of length 64 (32 bytes = 64 hex chars)
        assert len(token) == 64
        assert all(c in "0123456789abcdef" for c in token)

        # Test uniqueness
        token2 = generate_secure_token(32)
        assert token != token2

    def test_otp_randomness(self):
        """Test that OTPs are random"""
        otps = [generate_otp(6) for _ in range(100)]

        # Should have variety (not all the same)
        unique_otps = set(otps)
        assert len(unique_otps) > 50  # At least 50% unique

    # ========== Edge Cases ==========

    def test_malformed_hash_formats(self):
        """Test handling of malformed hash formats"""
        malformed_hashes = [
            "invalid",
            "$invalid$format",
            "no_dollar_sign",
            "$",
            "$$",
        ]

        for bad_hash in malformed_hashes:
            is_valid, _ = self.hasher.verify_password(self.test_password, bad_hash)
            assert is_valid is False

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_unicode_passwords(self):
        """Test Unicode password support"""
        unicode_passwords = [
            "مرحبا123!",  # Arabic
            "你好123!",  # Chinese
            "Привет123!",  # Russian
            "🔐Password123!",  # Emoji
        ]

        for password in unicode_passwords:
            hashed = self.hasher.hash_password(password)
            is_valid, _ = self.hasher.verify_password(password, hashed)
            assert is_valid is True


# ========== Integration Tests ==========


class TestPasswordMigrationScenarios:
    """Test realistic migration scenarios"""

    def setup_method(self):
        """Setup test fixtures"""
        self.hasher = PasswordHasher()
        self.test_password = "UserPassword123!"

    @pytest.mark.skipif(
        not (ARGON2_AVAILABLE and BCRYPT_AVAILABLE),
        reason="Both Argon2 and bcrypt required",
    )
    def test_full_migration_flow_bcrypt_to_argon2(self):
        """Test complete migration from bcrypt to Argon2id"""
        import bcrypt

        # Step 1: User has old bcrypt password
        old_hash = bcrypt.hashpw(
            self.test_password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        # Step 2: User logs in - verify old password
        is_valid, needs_migration = self.hasher.verify_password(
            self.test_password, old_hash
        )

        assert is_valid is True
        assert needs_migration is True

        # Step 3: Generate new Argon2id hash
        new_hash = self.hasher.hash_password(self.test_password)

        # Step 4: Verify new hash works
        is_valid, needs_migration = self.hasher.verify_password(
            self.test_password, new_hash
        )

        assert is_valid is True
        assert needs_migration is False

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_full_migration_flow_pbkdf2_to_argon2(self):
        """Test complete migration from PBKDF2 to Argon2id"""
        # Step 1: User has old PBKDF2 password
        salt = secrets.token_bytes(32)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            self.test_password.encode("utf-8"),
            salt,
            iterations=100_000,
            dklen=32,
        )
        old_hash = f"{salt.hex()}${hashed.hex()}"

        # Step 2: User logs in - verify old password
        is_valid, needs_migration = self.hasher.verify_password(
            self.test_password, old_hash
        )

        assert is_valid is True
        assert needs_migration is True

        # Step 3: Generate new Argon2id hash
        new_hash = self.hasher.hash_password(self.test_password)

        # Step 4: Verify new hash works
        is_valid, needs_migration = self.hasher.verify_password(
            self.test_password, new_hash
        )

        assert is_valid is True
        assert needs_migration is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
