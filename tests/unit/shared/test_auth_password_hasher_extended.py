"""
Extended unit tests for shared/auth/password_hasher.py
Covers _hash_pbkdf2, needs_rehash edge cases, PBKDF2 fallback,
malformed PBKDF2 hashes, and module-level functions.
"""

import hashlib
import secrets
import sys

import pytest

sys.path.insert(0, "/home/user/sahool-unified-v15-idp")

from shared.auth.password_hasher import (
    ARGON2_AVAILABLE,
    BCRYPT_AVAILABLE,
    HashAlgorithm,
    PasswordHasher,
    generate_otp,
    generate_secure_token,
    get_password_hasher,
    hash_password,
    needs_rehash,
    verify_password,
)


class TestPBKDF2Fallback:
    """Tests for PBKDF2 fallback hashing (when Argon2/bcrypt unavailable)."""

    def test_pbkdf2_hash_format(self):
        """_hash_pbkdf2 produces salt$hash format."""
        hasher = PasswordHasher()
        result = hasher._hash_pbkdf2("test_password")
        parts = result.split("$")
        assert len(parts) == 2
        # Salt is 32 bytes = 64 hex chars
        assert len(parts[0]) == 64
        # Hash is 32 bytes = 64 hex chars
        assert len(parts[1]) == 64

    def test_pbkdf2_verify_correct(self):
        """_verify_pbkdf2 verifies correct password."""
        hasher = PasswordHasher()
        hashed = hasher._hash_pbkdf2("my_password")
        is_valid, needs_migration = hasher._verify_pbkdf2("my_password", hashed)
        assert is_valid is True
        assert needs_migration is True  # PBKDF2 always needs migration

    def test_pbkdf2_verify_incorrect(self):
        """_verify_pbkdf2 rejects incorrect password."""
        hasher = PasswordHasher()
        hashed = hasher._hash_pbkdf2("my_password")
        is_valid, needs_migration = hasher._verify_pbkdf2("wrong_password", hashed)
        assert is_valid is False

    def test_pbkdf2_verify_malformed_single_part(self):
        """_verify_pbkdf2 returns False for hash without $ separator."""
        hasher = PasswordHasher()
        is_valid, needs_migration = hasher._verify_pbkdf2("password", "nohashseparator")
        assert is_valid is False
        assert needs_migration is False

    def test_pbkdf2_verify_malformed_three_parts(self):
        """_verify_pbkdf2 returns False for hash with too many $ separators."""
        hasher = PasswordHasher()
        is_valid, needs_migration = hasher._verify_pbkdf2("password", "a$b$c")
        assert is_valid is False

    def test_pbkdf2_verify_invalid_hex(self):
        """_verify_pbkdf2 returns False for invalid hex in salt."""
        hasher = PasswordHasher()
        is_valid, needs_migration = hasher._verify_pbkdf2("password", "not_hex_salt$" + "a" * 64)
        assert is_valid is False

    def test_pbkdf2_unique_salts(self):
        """_hash_pbkdf2 produces different hashes for same password."""
        hasher = PasswordHasher()
        h1 = hasher._hash_pbkdf2("same_password")
        h2 = hasher._hash_pbkdf2("same_password")
        assert h1 != h2


class TestNeedsRehash:
    """Tests for needs_rehash function."""

    def test_unknown_format_returns_true(self):
        """needs_rehash returns True for non-Argon2 formats (including unknown)."""
        hasher = PasswordHasher()
        # "plaintext_password" has no $ so it's UNKNOWN -> not ARGON2ID -> needs rehash
        result = hasher.needs_rehash("plaintext_password")
        assert result is True

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_fresh_argon2_does_not_need_rehash(self):
        """Fresh Argon2id hash does not need rehash."""
        hasher = PasswordHasher()
        hashed = hasher.hash_password("password123")
        assert hasher.needs_rehash(hashed) is False

    def test_pbkdf2_always_needs_rehash(self):
        """PBKDF2 hashes always need rehash."""
        hasher = PasswordHasher()
        hashed = hasher._hash_pbkdf2("password123")
        assert hasher.needs_rehash(hashed) is True

    @pytest.mark.skipif(not BCRYPT_AVAILABLE, reason="bcrypt not available")
    def test_bcrypt_always_needs_rehash(self):
        """bcrypt hashes always need rehash."""
        import bcrypt

        hasher = PasswordHasher()
        legacy = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode("utf-8")
        assert hasher.needs_rehash(legacy) is True

    def test_module_level_needs_rehash(self):
        """Module-level needs_rehash function works."""
        hasher = PasswordHasher()
        hashed = hasher._hash_pbkdf2("password123")
        assert needs_rehash(hashed) is True


class TestVerifyPasswordEdgeCases:
    """Edge cases for verify_password."""

    def test_both_empty_returns_false(self):
        """Empty password and empty hash returns False."""
        hasher = PasswordHasher()
        is_valid, _ = hasher.verify_password("", "")
        assert is_valid is False

    def test_none_password_returns_false(self):
        """None-like empty password returns False."""
        hasher = PasswordHasher()
        is_valid, _ = hasher.verify_password("", "some_hash")
        assert is_valid is False

    def test_none_hash_returns_false(self):
        """Empty hash returns False."""
        hasher = PasswordHasher()
        is_valid, _ = hasher.verify_password("password", "")
        assert is_valid is False

    def test_unknown_algorithm_returns_false(self):
        """Unknown hash algorithm returns (False, False)."""
        hasher = PasswordHasher()
        is_valid, needs = hasher.verify_password("password", "plaintext_password_no_format")
        assert is_valid is False
        assert needs is False

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_argon2_wrong_password(self):
        """Argon2 verify with wrong password returns False."""
        hasher = PasswordHasher()
        hashed = hasher.hash_password("correct_password")
        is_valid, needs = hasher.verify_password("wrong_password", hashed)
        assert is_valid is False
        assert needs is False


class TestDetectAlgorithm:
    """Extended algorithm detection tests."""

    def test_argon2i_detected_as_argon2(self):
        """$argon2i$ prefix detected as ARGON2ID."""
        hasher = PasswordHasher()
        assert hasher._detect_algorithm("$argon2i$v=19$...") == HashAlgorithm.ARGON2ID

    def test_argon2d_detected_as_argon2(self):
        """$argon2d$ prefix detected as ARGON2ID."""
        hasher = PasswordHasher()
        assert hasher._detect_algorithm("$argon2d$v=19$...") == HashAlgorithm.ARGON2ID

    def test_bcrypt_2a_detected(self):
        """$2a$ prefix detected as BCRYPT."""
        hasher = PasswordHasher()
        assert hasher._detect_algorithm("$2a$12$...") == HashAlgorithm.BCRYPT

    def test_bcrypt_2b_detected(self):
        """$2b$ prefix detected as BCRYPT."""
        hasher = PasswordHasher()
        assert hasher._detect_algorithm("$2b$12$...") == HashAlgorithm.BCRYPT

    def test_bcrypt_2y_detected(self):
        """$2y$ prefix detected as BCRYPT."""
        hasher = PasswordHasher()
        assert hasher._detect_algorithm("$2y$12$...") == HashAlgorithm.BCRYPT


class TestGenerateOTP:
    """Extended OTP generation tests."""

    def test_otp_length_8(self):
        """OTP of custom length 8."""
        otp = generate_otp(8)
        assert len(otp) == 8
        assert otp.isdigit()

    def test_otp_length_4(self):
        """OTP of custom length 4."""
        otp = generate_otp(4)
        assert len(otp) == 4
        assert otp.isdigit()

    def test_otp_length_1(self):
        """OTP of minimum length 1."""
        otp = generate_otp(1)
        assert len(otp) == 1
        assert otp.isdigit()


class TestGenerateSecureToken:
    """Extended secure token tests."""

    def test_token_16_bytes(self):
        """16-byte token produces 32 hex chars."""
        token = generate_secure_token(16)
        assert len(token) == 32

    def test_token_64_bytes(self):
        """64-byte token produces 128 hex chars."""
        token = generate_secure_token(64)
        assert len(token) == 128

    def test_tokens_unique(self):
        """Multiple tokens are unique."""
        tokens = {generate_secure_token(32) for _ in range(10)}
        assert len(tokens) == 10


class TestHashAlgorithmEnum:
    """Tests for HashAlgorithm enum."""

    def test_enum_values(self):
        assert HashAlgorithm.ARGON2ID == "argon2id"
        assert HashAlgorithm.BCRYPT == "bcrypt"
        assert HashAlgorithm.PBKDF2_SHA256 == "pbkdf2_sha256"
        assert HashAlgorithm.UNKNOWN == "unknown"


class TestPasswordHasherInit:
    """Tests for PasswordHasher initialization."""

    def test_default_parameters(self):
        """Default parameters are set correctly."""
        hasher = PasswordHasher()
        assert hasher.time_cost == 2
        assert hasher.memory_cost == 65536
        assert hasher.parallelism == 4
        assert hasher.hash_len == 32
        assert hasher.salt_len == 16

    def test_custom_parameters(self):
        """Custom parameters are accepted."""
        hasher = PasswordHasher(
            time_cost=3,
            memory_cost=32768,
            parallelism=2,
            hash_len=64,
            salt_len=32,
        )
        assert hasher.time_cost == 3
        assert hasher.memory_cost == 32768
        assert hasher.parallelism == 2

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_argon2_hasher_initialized(self):
        """Argon2 hasher is initialized when available."""
        hasher = PasswordHasher()
        assert hasher.argon2_hasher is not None

    def test_get_password_hasher_singleton(self):
        """get_password_hasher returns singleton."""
        h1 = get_password_hasher()
        h2 = get_password_hasher()
        assert h1 is h2


class TestModuleLevelFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_hash_password_module_level(self):
        """Module-level hash_password works."""
        hashed = hash_password("test_password")
        assert hashed.startswith("$argon2")

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_verify_password_module_level(self):
        """Module-level verify_password works."""
        hashed = hash_password("test_password")
        is_valid, needs = verify_password("test_password", hashed)
        assert is_valid is True
        assert needs is False

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_verify_password_module_level_wrong(self):
        """Module-level verify_password rejects wrong password."""
        hashed = hash_password("test_password")
        is_valid, _ = verify_password("wrong_password", hashed)
        assert is_valid is False
