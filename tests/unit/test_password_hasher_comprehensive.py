"""
Comprehensive Password Hasher Tests for SAHOOL Platform
اختبارات شاملة لمعالج كلمات المرور لمنصة سهول

Tests cover:
- Password hashing with multiple algorithms
- Password verification
- Algorithm detection
- Migration between algorithms (bcrypt -> Argon2id)
- PBKDF2 fallback
- Empty/invalid password handling
- OTP and secure token generation
- Needs rehash detection
"""

from __future__ import annotations

import hashlib
import secrets

import pytest

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


@pytest.mark.unit
class TestPasswordHasherInit:
    """Tests for PasswordHasher initialization"""

    def test_default_initialization(self):
        """Test default hasher initialization with OWASP parameters"""
        hasher = PasswordHasher()
        assert hasher.time_cost == 2
        assert hasher.memory_cost == 65536
        assert hasher.parallelism == 4
        assert hasher.hash_len == 32
        assert hasher.salt_len == 16

    def test_custom_initialization(self):
        """Test hasher with custom parameters"""
        hasher = PasswordHasher(
            time_cost=3,
            memory_cost=131072,
            parallelism=8,
            hash_len=64,
            salt_len=32,
        )
        assert hasher.time_cost == 3
        assert hasher.memory_cost == 131072


@pytest.mark.unit
class TestHashPassword:
    """Tests for password hashing"""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a non-empty string"""
        hasher = PasswordHasher()
        result = hasher.hash_password("SecurePassword123!")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_password_different_each_time(self):
        """Test that hashing the same password produces different hashes (salt)"""
        hasher = PasswordHasher()
        hash1 = hasher.hash_password("SamePassword123!")
        hash2 = hasher.hash_password("SamePassword123!")
        assert hash1 != hash2

    def test_hash_password_empty_raises_error(self):
        """Test that empty password raises ValueError"""
        hasher = PasswordHasher()
        with pytest.raises(ValueError, match="Password cannot be empty"):
            hasher.hash_password("")

    def test_hash_password_unicode(self):
        """Test hashing Unicode/Arabic password"""
        hasher = PasswordHasher()
        result = hasher.hash_password("كلمة_المرور_123!")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_password_long_password(self):
        """Test hashing a very long password"""
        hasher = PasswordHasher()
        long_pwd = "A" * 1000
        result = hasher.hash_password(long_pwd)
        assert isinstance(result, str)

    def test_hash_password_special_characters(self):
        """Test hashing password with special characters"""
        hasher = PasswordHasher()
        special_pwd = "P@$$w0rd!#%^&*()_+-=[]{}|;':\",./<>?"
        result = hasher.hash_password(special_pwd)
        assert isinstance(result, str)


@pytest.mark.unit
class TestVerifyPassword:
    """Tests for password verification"""

    def test_verify_correct_password(self):
        """Test verifying a correct password"""
        hasher = PasswordHasher()
        hashed = hasher.hash_password("CorrectPassword123!")
        is_valid, needs_rehash = hasher.verify_password("CorrectPassword123!", hashed)
        assert is_valid is True

    def test_verify_wrong_password(self):
        """Test verifying an incorrect password"""
        hasher = PasswordHasher()
        hashed = hasher.hash_password("CorrectPassword123!")
        is_valid, needs_rehash = hasher.verify_password("WrongPassword!", hashed)
        assert is_valid is False

    def test_verify_empty_password(self):
        """Test verifying empty password returns False"""
        hasher = PasswordHasher()
        is_valid, needs_rehash = hasher.verify_password("", "some-hash")
        assert is_valid is False
        assert needs_rehash is False

    def test_verify_empty_hash(self):
        """Test verifying with empty hash returns False"""
        hasher = PasswordHasher()
        is_valid, needs_rehash = hasher.verify_password("password", "")
        assert is_valid is False
        assert needs_rehash is False

    def test_verify_unicode_password(self):
        """Test verifying Unicode/Arabic password"""
        hasher = PasswordHasher()
        hashed = hasher.hash_password("كلمة_المرور_الآمنة_123")
        is_valid, _ = hasher.verify_password("كلمة_المرور_الآمنة_123", hashed)
        assert is_valid is True


@pytest.mark.unit
class TestAlgorithmDetection:
    """Tests for hash algorithm detection"""

    def test_detect_argon2(self):
        """Test detecting Argon2 hash"""
        hasher = PasswordHasher()
        algo = hasher._detect_algorithm("$argon2id$v=19$m=65536,t=2,p=4$salt$hash")
        assert algo == HashAlgorithm.ARGON2ID

    def test_detect_bcrypt_2a(self):
        """Test detecting bcrypt $2a$ hash"""
        hasher = PasswordHasher()
        algo = hasher._detect_algorithm("$2a$12$somesaltandhashvalue")
        assert algo == HashAlgorithm.BCRYPT

    def test_detect_bcrypt_2b(self):
        """Test detecting bcrypt $2b$ hash"""
        hasher = PasswordHasher()
        algo = hasher._detect_algorithm("$2b$12$somesaltandhashvalue")
        assert algo == HashAlgorithm.BCRYPT

    def test_detect_bcrypt_2y(self):
        """Test detecting bcrypt $2y$ hash"""
        hasher = PasswordHasher()
        algo = hasher._detect_algorithm("$2y$12$somesaltandhashvalue")
        assert algo == HashAlgorithm.BCRYPT

    def test_detect_pbkdf2(self):
        """Test detecting PBKDF2 hash (salt$hash format)"""
        hasher = PasswordHasher()
        algo = hasher._detect_algorithm("abcdef0123456789$fedcba9876543210")
        assert algo == HashAlgorithm.PBKDF2_SHA256

    def test_detect_unknown(self):
        """Test detecting unknown hash format"""
        hasher = PasswordHasher()
        algo = hasher._detect_algorithm("justsomestringwithoutdollarsign")
        assert algo == HashAlgorithm.UNKNOWN


@pytest.mark.unit
class TestPBKDF2Fallback:
    """Tests for PBKDF2 fallback hashing"""

    def test_pbkdf2_hash_format(self):
        """Test PBKDF2 hash is in salt$hash format"""
        hasher = PasswordHasher()
        result = hasher._hash_pbkdf2("TestPassword123!")
        parts = result.split("$")
        assert len(parts) == 2
        # Both parts should be hex strings
        assert all(c in "0123456789abcdef" for c in parts[0])
        assert all(c in "0123456789abcdef" for c in parts[1])

    def test_pbkdf2_verify(self):
        """Test PBKDF2 password verification"""
        hasher = PasswordHasher()
        hashed = hasher._hash_pbkdf2("TestPassword123!")
        is_valid, needs_migration = hasher._verify_pbkdf2("TestPassword123!", hashed)
        assert is_valid is True
        assert needs_migration is True  # Always migrate to Argon2

    def test_pbkdf2_verify_wrong_password(self):
        """Test PBKDF2 verification with wrong password"""
        hasher = PasswordHasher()
        hashed = hasher._hash_pbkdf2("CorrectPassword!")
        is_valid, _ = hasher._verify_pbkdf2("WrongPassword!", hashed)
        assert is_valid is False

    def test_pbkdf2_verify_invalid_format(self):
        """Test PBKDF2 verification with invalid hash format"""
        hasher = PasswordHasher()
        is_valid, _ = hasher._verify_pbkdf2("password", "not-a-valid-hash-format")
        assert is_valid is False


@pytest.mark.unit
class TestNeedsRehash:
    """Tests for needs_rehash detection"""

    def test_pbkdf2_needs_rehash(self):
        """Test that PBKDF2 hash needs rehashing"""
        hasher = PasswordHasher()
        pbkdf2_hash = hasher._hash_pbkdf2("password")
        assert hasher.needs_rehash(pbkdf2_hash) is True

    def test_unknown_hash_needs_rehash(self):
        """Test that unknown/non-Argon2 hash format needs rehashing"""
        hasher = PasswordHasher()
        # Any non-Argon2 hash should be flagged for rehash to migrate to Argon2
        assert hasher.needs_rehash("unknownformat") is True

    @pytest.mark.skipif(not ARGON2_AVAILABLE, reason="Argon2 not available")
    def test_current_argon2_does_not_need_rehash(self):
        """Test that current Argon2 hash does not need rehashing"""
        hasher = PasswordHasher()
        hashed = hasher.hash_password("password123!")
        assert hasher.needs_rehash(hashed) is False


@pytest.mark.unit
class TestModuleLevelFunctions:
    """Tests for module-level convenience functions"""

    def test_get_password_hasher_singleton(self):
        """Test that get_password_hasher returns consistent instance"""
        hasher1 = get_password_hasher()
        hasher2 = get_password_hasher()
        assert hasher1 is hasher2

    def test_module_hash_password(self):
        """Test module-level hash_password function"""
        result = hash_password("TestPassword123!")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_module_verify_password(self):
        """Test module-level verify_password function"""
        hashed = hash_password("TestPassword123!")
        is_valid, _ = verify_password("TestPassword123!", hashed)
        assert is_valid is True

    def test_module_needs_rehash(self):
        """Test module-level needs_rehash function"""
        hashed = hash_password("password")
        result = needs_rehash(hashed)
        assert isinstance(result, bool)


@pytest.mark.unit
class TestGenerateOTP:
    """Tests for OTP generation"""

    def test_default_otp_length(self):
        """Test default OTP is 6 digits"""
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()

    def test_custom_otp_length(self):
        """Test OTP with custom length"""
        otp = generate_otp(length=8)
        assert len(otp) == 8
        assert otp.isdigit()

    def test_otp_randomness(self):
        """Test that OTPs are random"""
        otps = {generate_otp() for _ in range(100)}
        assert len(otps) > 50  # Should have high uniqueness

    def test_otp_only_digits(self):
        """Test that OTP contains only digits"""
        for _ in range(50):
            otp = generate_otp()
            assert all(c in "0123456789" for c in otp)


@pytest.mark.unit
class TestGenerateSecureToken:
    """Tests for secure token generation"""

    def test_default_token_length(self):
        """Test default token is 64 hex chars (32 bytes)"""
        token = generate_secure_token()
        assert len(token) == 64  # 32 bytes * 2 hex chars
        assert all(c in "0123456789abcdef" for c in token)

    def test_custom_token_length(self):
        """Test token with custom byte length"""
        token = generate_secure_token(length=16)
        assert len(token) == 32  # 16 bytes * 2 hex chars

    def test_token_uniqueness(self):
        """Test that tokens are unique"""
        tokens = {generate_secure_token() for _ in range(100)}
        assert len(tokens) == 100  # All should be unique


@pytest.mark.unit
class TestHashAlgorithmEnum:
    """Tests for HashAlgorithm enum"""

    def test_algorithm_values(self):
        """Test that all algorithm values are correct"""
        assert HashAlgorithm.ARGON2ID == "argon2id"
        assert HashAlgorithm.BCRYPT == "bcrypt"
        assert HashAlgorithm.PBKDF2_SHA256 == "pbkdf2_sha256"
        assert HashAlgorithm.UNKNOWN == "unknown"

    def test_algorithm_count(self):
        """Test total number of algorithms"""
        assert len(HashAlgorithm) == 4
