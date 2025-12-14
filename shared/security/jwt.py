"""
JWT Token Verification and Creation
RS256/HS256 support with standard claims
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass

import jwt
from jwt import PyJWTError

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY", "")
JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # HS256 for dev, RS256 for prod
JWT_ISSUER = os.getenv("JWT_ISSUER", "sahool-idp")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "sahool-platform")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))


class AuthError(Exception):
    """Authentication error"""
    def __init__(self, message: str, code: str = "auth_error"):
        self.message = message
        self.code = code
        super().__init__(message)


@dataclass
class TokenPayload:
    """Decoded token payload"""
    sub: str  # user_id
    tid: str  # tenant_id
    roles: list[str]
    scopes: list[str]
    exp: datetime
    iat: datetime
    iss: str
    aud: str
    jti: Optional[str] = None  # token id for revocation
    extra: Optional[dict] = None


# ─────────────────────────────────────────────────────────────────────────────
# Token Verification
# ─────────────────────────────────────────────────────────────────────────────

def _get_verify_key() -> str:
    """Get the key for verification"""
    if JWT_ALGORITHM.startswith("RS"):
        return JWT_PUBLIC_KEY
    return JWT_SECRET_KEY


def _get_sign_key() -> str:
    """Get the key for signing"""
    if JWT_ALGORITHM.startswith("RS"):
        return JWT_PRIVATE_KEY
    return JWT_SECRET_KEY


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string

    Returns:
        Decoded payload dictionary

    Raises:
        AuthError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            _get_verify_key(),
            algorithms=[JWT_ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={
                "require": ["sub", "tid", "exp", "iat"],
            },
        )

        # Ensure required fields exist
        if "sub" not in payload:
            raise AuthError("missing_subject", "invalid_token")
        if "tid" not in payload:
            raise AuthError("missing_tenant", "invalid_token")

        # Set defaults for optional fields
        payload.setdefault("roles", [])
        payload.setdefault("scopes", [])

        return payload

    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired", "token_expired")
    except jwt.InvalidIssuerError:
        raise AuthError("Invalid token issuer", "invalid_issuer")
    except jwt.InvalidAudienceError:
        raise AuthError("Invalid token audience", "invalid_audience")
    except PyJWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise AuthError(f"Invalid token: {str(e)}", "invalid_token")


def decode_token_unsafe(token: str) -> dict:
    """
    Decode token WITHOUT verification.
    Use only for debugging/logging, never for authorization.
    """
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except PyJWTError:
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# Token Creation
# ─────────────────────────────────────────────────────────────────────────────

def create_token(
    user_id: str,
    tenant_id: str,
    roles: list[str],
    scopes: list[str],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access",
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Create a new JWT token.

    Args:
        user_id: User identifier (sub claim)
        tenant_id: Tenant identifier (tid claim)
        roles: List of role names
        scopes: List of permission scopes
        expires_delta: Custom expiration time
        token_type: "access" or "refresh"
        extra_claims: Additional claims to include

    Returns:
        Encoded JWT token string
    """
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    elif token_type == "refresh":
        expire = now + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        expire = now + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "tid": tenant_id,
        "roles": roles,
        "scopes": scopes,
        "exp": expire,
        "iat": now,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "type": token_type,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, _get_sign_key(), algorithm=JWT_ALGORITHM)


def create_access_token(
    user_id: str,
    tenant_id: str,
    roles: list[str],
    scopes: list[str],
) -> str:
    """Create an access token"""
    return create_token(user_id, tenant_id, roles, scopes, token_type="access")


def create_refresh_token(
    user_id: str,
    tenant_id: str,
) -> str:
    """Create a refresh token (minimal claims)"""
    return create_token(
        user_id,
        tenant_id,
        roles=[],
        scopes=[],
        token_type="refresh",
    )


def create_token_pair(
    user_id: str,
    tenant_id: str,
    roles: list[str],
    scopes: list[str],
) -> dict[str, str]:
    """Create both access and refresh tokens"""
    return {
        "access_token": create_access_token(user_id, tenant_id, roles, scopes),
        "refresh_token": create_refresh_token(user_id, tenant_id),
        "token_type": "bearer",
        "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
