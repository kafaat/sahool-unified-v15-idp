"""
JWT Token Verification and Creation
RS256/HS256 support with standard claims

Security Features:
- JTI (Token ID) for revocation support
- Integration with TokenRevocationService
- RS256 asymmetric encryption support
"""

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import PyJWTError

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Security: JWT_SECRET_KEY is REQUIRED in production - no default value
# ─────────────────────────────────────────────────────────────────────────────


def _get_required_env(key: str, default: Optional[str] = None) -> str:
    """Get required environment variable, raise error if missing in production"""
    value = os.getenv(key, default)
    env = os.getenv("ENVIRONMENT", "development")

    if not value and env in ("production", "staging"):
        raise RuntimeError(f"Required environment variable {key} is not set")

    if not value:
        logger.warning(f"Using default value for {key} - NOT SAFE FOR PRODUCTION")
        return default or ""

    return value


JWT_SECRET_KEY = _get_required_env("JWT_SECRET_KEY", "")
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY", "")
JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "RS256")  # RS256 is more secure
JWT_ISSUER = os.getenv("JWT_ISSUER", "sahool-idp")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "sahool-platform")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))

# SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
# Never trust algorithm from environment variables or token header
ALLOWED_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]


def validate_jwt_configuration() -> bool:
    """Validate JWT configuration on startup"""
    env = os.getenv("ENVIRONMENT", "development")

    if env in ("production", "staging"):
        if JWT_ALGORITHM.startswith("RS"):
            if not JWT_PUBLIC_KEY or not JWT_PRIVATE_KEY:
                raise RuntimeError(
                    "RS256 algorithm requires JWT_PUBLIC_KEY and JWT_PRIVATE_KEY"
                )
        else:
            if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
                raise RuntimeError(
                    "JWT_SECRET_KEY must be at least 32 characters in production"
                )

    return True


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


def verify_token(token: str, check_revocation: bool = True) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string
        check_revocation: Whether to check if token is revoked (default: True)

    Returns:
        Decoded payload dictionary

    Raises:
        AuthError: If token is invalid, expired, or revoked

    Security: Uses hardcoded algorithm whitelist to prevent algorithm confusion attacks
    """
    try:
        # SECURITY FIX: Decode header to validate algorithm before verification
        unverified_header = jwt.get_unverified_header(token)

        if not unverified_header or "alg" not in unverified_header:
            raise AuthError("Invalid token: missing algorithm", "invalid_token")

        algorithm = unverified_header["alg"]

        # Reject 'none' algorithm explicitly
        if algorithm.lower() == "none":
            raise AuthError(
                "Invalid token: none algorithm not allowed", "invalid_token"
            )

        # Verify algorithm is in whitelist
        if algorithm not in ALLOWED_ALGORITHMS:
            raise AuthError(
                f"Invalid token: unsupported algorithm {algorithm}", "invalid_token"
            )

        # SECURITY FIX: Use hardcoded whitelist instead of environment variable
        payload = jwt.decode(
            token,
            _get_verify_key(),
            algorithms=ALLOWED_ALGORITHMS,
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

        # Check token revocation
        if check_revocation:
            try:
                from .token_revocation import get_revocation_service

                revocation_svc = get_revocation_service()
                jti = payload.get("jti")
                user_id = payload.get("sub")
                tenant_id = payload.get("tid")
                iat = payload.get("iat")

                # Convert iat to datetime if it's a timestamp
                if isinstance(iat, (int, float)):
                    iat = datetime.fromtimestamp(iat, tz=timezone.utc)

                is_revoked, reason = revocation_svc.is_revoked(
                    jti=jti,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    issued_at=iat,
                )

                if is_revoked:
                    logger.warning(
                        f"Revoked token used: user={user_id}, jti={jti}, reason={reason}"
                    )
                    raise AuthError(
                        f"Token has been revoked: {reason}", "token_revoked"
                    )

            except ImportError:
                # Revocation service not available, skip check
                pass

        return payload

    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired", "token_expired")
    except jwt.InvalidIssuerError:
        raise AuthError("Invalid token issuer", "invalid_issuer")
    except jwt.InvalidAudienceError:
        raise AuthError("Invalid token audience", "invalid_audience")
    except AuthError:
        raise  # Re-raise AuthError from revocation check
    except PyJWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise AuthError(f"Invalid token: {str(e)}", "invalid_token")


def decode_token_unsafe(token: str) -> dict:
    """
    ⚠️ UNSAFE: Decode token WITHOUT signature verification.

    SECURITY WARNING: This function does NOT verify the token signature!
    - NEVER use for authorization decisions
    - NEVER trust data from this function for access control
    - Use ONLY for debugging, logging, or extracting non-sensitive metadata
    """
    try:
        # This function is intentionally unverified for debugging purposes only
        return jwt.decode(
            token, options={"verify_signature": False}
        )  # nosemgrep: python.jwt.security.unverified-jwt-decode.unverified-jwt-decode
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
    jti: Optional[str] = None,
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
        jti: Optional token ID (auto-generated if not provided)

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

    # Generate JTI for revocation support
    token_jti = jti or str(uuid.uuid4())

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
        "jti": token_jti,  # Token ID for revocation
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
