"""
SAHOOL Authentication Module
Password hashing, JWT, OTP, Session management
"""

from shared.security.jwt import (
    AuthError,
    create_access_token,
    create_refresh_token,
    create_token,
    create_token_pair,
    verify_token,
)

from .passwords import (
    hash_password,
    verify_password,
    generate_otp,
    generate_secure_token,
)

# Alias for backward compatibility
decode_token = verify_token

__all__ = [
    # JWT
    "AuthError",
    "create_token",
    "verify_token",
    "decode_token",  # alias for verify_token
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    # Passwords
    "hash_password",
    "verify_password",
    "generate_otp",
    "generate_secure_token",
]
