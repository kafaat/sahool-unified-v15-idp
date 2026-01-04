"""
SAHOOL Password Hashing
Secure password handling with bcrypt
"""

from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_password(password: str, salt: bytes | None = None) -> str:
    """
    Hash a password using PBKDF2-SHA256.

    Args:
        password: Plain text password
        salt: Optional salt (generated if not provided)

    Returns:
        Hashed password in format: salt$hash (hex encoded)
    """
    if salt is None:
        salt = secrets.token_bytes(32)

    # Use PBKDF2 with SHA256
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations=100_000,
        dklen=32,
    )

    return f"{salt.hex()}${hashed.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password to verify
        hashed: Stored hash in format: salt$hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        salt_hex, hash_hex = hashed.split("$")
        salt = bytes.fromhex(salt_hex)

        # Recreate hash with same salt
        check_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations=100_000,
            dklen=32,
        )

        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(check_hash.hex(), hash_hex)

    except (ValueError, AttributeError):
        return False


def generate_otp(length: int = 4) -> str:
    """
    Generate a numeric OTP code.

    Args:
        length: Number of digits (default 4)

    Returns:
        Numeric OTP string
    """
    return "".join(secrets.choice("0123456789") for _ in range(length))


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.

    Args:
        length: Token length in bytes

    Returns:
        Hex-encoded token string
    """
    return secrets.token_hex(length)
