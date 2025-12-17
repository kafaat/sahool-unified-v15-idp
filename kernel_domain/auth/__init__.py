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

__all__ = [
    "AuthError",
    "create_token",
    "verify_token",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
]
