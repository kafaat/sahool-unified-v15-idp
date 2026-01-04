"""
SAHOOL Password Hasher - Argon2id Migration
معالج كلمات المرور - الترحيل إلى Argon2id

This module provides secure password hashing using Argon2id with backward compatibility
for bcrypt and PBKDF2 hashes. Supports automatic migration on successful login.

يوفر هذا الوحدة تشفير آمن لكلمات المرور باستخدام Argon2id مع التوافق
للخلف مع bcrypt و PBKDF2. يدعم الترحيل التلقائي عند تسجيل الدخول الناجح.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from enum import Enum

logger = logging.getLogger(__name__)

# Import password hashing libraries
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import (
        InvalidHashError,
        VerificationError,
        VerifyMismatchError,
    )

    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False
    logger.warning("argon2-cffi not available. Please install: pip install argon2-cffi")

try:
    import bcrypt

    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt not available")


class HashAlgorithm(str, Enum):
    """Supported password hashing algorithms"""

    ARGON2ID = "argon2id"
    BCRYPT = "bcrypt"
    PBKDF2_SHA256 = "pbkdf2_sha256"
    UNKNOWN = "unknown"


class PasswordHasher:
    """
    Secure password hasher with migration support

    Features:
    - Primary: Argon2id (recommended by OWASP)
    - Legacy support: bcrypt, PBKDF2-SHA256
    - Automatic migration on successful verification
    - Constant-time comparison
    """

    def __init__(
        self,
        time_cost: int = 2,
        memory_cost: int = 65536,  # 64 MB
        parallelism: int = 4,
        hash_len: int = 32,
        salt_len: int = 16,
    ):
        """
        Initialize password hasher

        Args:
            time_cost: Number of iterations (Argon2 time cost)
            memory_cost: Memory usage in KiB (Argon2 memory cost)
            parallelism: Number of parallel threads (Argon2 parallelism)
            hash_len: Length of the hash in bytes
            salt_len: Length of the salt in bytes
        """
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.hash_len = hash_len
        self.salt_len = salt_len

        if ARGON2_AVAILABLE:
            self.argon2_hasher = PasswordHasher(
                time_cost=time_cost,
                memory_cost=memory_cost,
                parallelism=parallelism,
                hash_len=hash_len,
                salt_len=salt_len,
            )
        else:
            self.argon2_hasher = None
            logger.warning("Argon2 not available, falling back to bcrypt/PBKDF2")

    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id (primary) or fallback algorithms

        Args:
            password: Plain text password

        Returns:
            Hashed password with algorithm identifier
        """
        if not password:
            raise ValueError("Password cannot be empty")

        # Primary: Use Argon2id
        if ARGON2_AVAILABLE and self.argon2_hasher:
            return self.argon2_hasher.hash(password)

        # Fallback 1: bcrypt
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed.decode("utf-8")

        # Fallback 2: PBKDF2-SHA256
        return self._hash_pbkdf2(password)

    def verify_password(self, password: str, hashed_password: str) -> tuple[bool, bool]:
        """
        Verify a password against its hash

        Args:
            password: Plain text password to verify
            hashed_password: Stored hash

        Returns:
            Tuple of (is_valid, needs_rehash)
            - is_valid: Whether the password matches
            - needs_rehash: Whether the password should be rehashed with current algorithm
        """
        if not password or not hashed_password:
            return False, False

        try:
            algorithm = self._detect_algorithm(hashed_password)

            if algorithm == HashAlgorithm.ARGON2ID:
                return self._verify_argon2(password, hashed_password)
            elif algorithm == HashAlgorithm.BCRYPT:
                return self._verify_bcrypt(password, hashed_password)
            elif algorithm == HashAlgorithm.PBKDF2_SHA256:
                return self._verify_pbkdf2(password, hashed_password)
            else:
                logger.warning("Unknown hash algorithm for password")
                return False, False

        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False, False

    def _detect_algorithm(self, hashed_password: str) -> HashAlgorithm:
        """
        Detect the algorithm used for a hashed password

        Args:
            hashed_password: The hashed password string

        Returns:
            HashAlgorithm enum value
        """
        if hashed_password.startswith("$argon2"):
            return HashAlgorithm.ARGON2ID
        elif (
            hashed_password.startswith("$2a$")
            or hashed_password.startswith("$2b$")
            or hashed_password.startswith("$2y$")
        ):
            return HashAlgorithm.BCRYPT
        elif "$" in hashed_password and len(hashed_password.split("$")) >= 2:
            # PBKDF2 format: salt$hash
            return HashAlgorithm.PBKDF2_SHA256
        else:
            return HashAlgorithm.UNKNOWN

    def _verify_argon2(self, password: str, hashed_password: str) -> tuple[bool, bool]:
        """Verify Argon2id password"""
        if not ARGON2_AVAILABLE or not self.argon2_hasher:
            logger.error("Argon2 not available but hash is Argon2 format")
            return False, False

        try:
            self.argon2_hasher.verify(hashed_password, password)
            # Check if rehash is needed (parameters changed)
            needs_rehash = self.argon2_hasher.check_needs_rehash(hashed_password)
            return True, needs_rehash
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False, False

    def _verify_bcrypt(self, password: str, hashed_password: str) -> tuple[bool, bool]:
        """Verify bcrypt password - always needs migration to Argon2id"""
        if not BCRYPT_AVAILABLE:
            logger.error("bcrypt not available but hash is bcrypt format")
            return False, False

        try:
            is_valid = bcrypt.checkpw(
                password.encode("utf-8"), hashed_password.encode("utf-8")
            )
            # Always migrate bcrypt to Argon2id
            return is_valid, is_valid
        except Exception as e:
            logger.error(f"bcrypt verification error: {e}")
            return False, False

    def _verify_pbkdf2(self, password: str, hashed_password: str) -> tuple[bool, bool]:
        """Verify PBKDF2-SHA256 password - always needs migration to Argon2id"""
        try:
            parts = hashed_password.split("$")
            if len(parts) != 2:
                return False, False

            salt_hex, stored_hash_hex = parts
            salt = bytes.fromhex(salt_hex)

            # Compute hash with same salt
            computed_hash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, iterations=100_000, dklen=32
            )

            # Constant-time comparison
            is_valid = hmac.compare_digest(computed_hash.hex(), stored_hash_hex)
            # Always migrate PBKDF2 to Argon2id
            return is_valid, is_valid

        except (ValueError, AttributeError) as e:
            logger.error(f"PBKDF2 verification error: {e}")
            return False, False

    def _hash_pbkdf2(self, password: str) -> str:
        """
        Hash password using PBKDF2-SHA256 (fallback only)

        Args:
            password: Plain text password

        Returns:
            Hashed password in format: salt$hash (hex encoded)
        """
        salt = secrets.token_bytes(32)
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations=100_000, dklen=32
        )
        return f"{salt.hex()}${hashed.hex()}"

    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if a password hash needs to be rehashed

        Args:
            hashed_password: The hashed password to check

        Returns:
            True if the password should be rehashed
        """
        try:
            algorithm = self._detect_algorithm(hashed_password)

            # Always rehash non-Argon2 hashes
            if algorithm != HashAlgorithm.ARGON2ID:
                return True

            # Check if Argon2 parameters have changed
            if ARGON2_AVAILABLE and self.argon2_hasher:
                return self.argon2_hasher.check_needs_rehash(hashed_password)

            return False
        except Exception:
            return False


# Global instance with recommended parameters
_default_hasher: PasswordHasher | None = None


def get_password_hasher() -> PasswordHasher:
    """
    Get the default password hasher instance

    Returns:
        PasswordHasher instance with recommended settings
    """
    global _default_hasher
    if _default_hasher is None:
        _default_hasher = PasswordHasher(
            time_cost=2,  # OWASP recommended minimum
            memory_cost=65536,  # 64 MB
            parallelism=4,  # 4 parallel threads
            hash_len=32,  # 256 bits
            salt_len=16,  # 128 bits
        )
    return _default_hasher


def hash_password(password: str) -> str:
    """
    Hash a password using the default hasher

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return get_password_hasher().hash_password(password)


def verify_password(password: str, hashed_password: str) -> tuple[bool, bool]:
    """
    Verify a password using the default hasher

    Args:
        password: Plain text password
        hashed_password: Stored hash

    Returns:
        Tuple of (is_valid, needs_rehash)
    """
    return get_password_hasher().verify_password(password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password needs rehashing

    Args:
        hashed_password: Stored hash

    Returns:
        True if rehashing is recommended
    """
    return get_password_hasher().needs_rehash(hashed_password)


# Backward compatibility functions
def generate_otp(length: int = 4) -> str:
    """
    Generate a numeric OTP code

    Args:
        length: Number of digits (default 4)

    Returns:
        Numeric OTP string
    """
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token

    Args:
        length: Token length in bytes

    Returns:
        Hex-encoded token string
    """
    return secrets.token_hex(length)
