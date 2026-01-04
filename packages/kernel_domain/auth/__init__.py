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

from .passwords import generate_otp, hash_password, verify_password

# Alias for compatibility
decode_token = verify_token

__all__ = [
    "AuthError",
    "create_token",
    "verify_token",
    "decode_token",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "hash_password",
    "verify_password",
    "generate_otp",
]
