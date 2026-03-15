"""
JWT Token Verification and Creation
HS256 support with standard claims

Note: RS256 with RSA keys has been deprecated. Only HS256 is supported.

Security Features:
- JTI (Token ID) for revocation support
- Integration with TokenRevocationService
- HS256 symmetric encryption
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from jwt import PyJWTError

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Security: JWT_SECRET_KEY is REQUIRED in production - no default value
# ─────────────────────────────────────────────────────────────────────────────


def _get_required_env(key: str, default: str | None = None) -> str:
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
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # HS256 for symmetric encryption
JWT_ISSUER = os.getenv("JWT_ISSUER", "sahool-idp")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "sahool-platform")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
JWT_LEEWAY_SECONDS = int(os.getenv("JWT_LEEWAY_SECONDS", "30"))  # Clock skew tolerance

# SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
# Only HS256 is allowed - RS256 has been deprecated
ALLOWED_ALGORITHMS = ["HS256"]


def validate_jwt_configuration() -> bool:
    """Validate JWT configuration on startup"""
    env = os.getenv("ENVIRONMENT", "development")

    if env in ("production", "staging"):
        if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
            raise RuntimeError("JWT_SECRET_KEY must be at least 32 characters in production")

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
    jti: str | None = None  # token id for revocation
    extra: dict | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Token Verification
# ─────────────────────────────────────────────────────────────────────────────


def verify_token(token: str, check_revocation: bool = True, leeway: int | None = None) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string
        check_revocation: Whether to check if token is revoked (default: True)
        leeway: Clock skew tolerance in seconds for expiry check.
                Defaults to JWT_LEEWAY_SECONDS env var (30s).

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
            raise AuthError("Invalid token: none algorithm not allowed", "invalid_token")

        # Verify algorithm is in whitelist (HS256 only)
        if algorithm not in ALLOWED_ALGORITHMS:
            raise AuthError(f"Invalid token: unsupported algorithm {algorithm}", "invalid_token")

        # SECURITY FIX: Use hardcoded whitelist instead of environment variable
        effective_leeway = leeway if leeway is not None else JWT_LEEWAY_SECONDS
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=ALLOWED_ALGORITHMS,
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            leeway=timedelta(seconds=effective_leeway),
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
                    iat = datetime.fromtimestamp(iat, tz=UTC)

                # NOTE: is_revoked() is a synchronous call that may block if the
                # revocation store uses I/O (e.g., Redis). Since verify_token() is itself
                # synchronous (not async def), wrapping with asyncio.to_thread() is not
                # applicable here. If this function is called from an async context (e.g.,
                # FastAPI endpoint), consider migrating verify_token to an async version
                # or offloading the entire call via asyncio.to_thread(verify_token, ...).
                is_revoked, reason = revocation_svc.is_revoked(
                    jti=jti,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    issued_at=iat,
                )

                if is_revoked:
                    logger.warning(f"Revoked token used: user={user_id}, jti={jti}, reason={reason}")
                    raise AuthError(f"Token has been revoked: {reason}", "token_revoked")

            except AuthError:
                # Re-raise auth errors (e.g., token_revoked) without catching them
                raise
            except ImportError:
                # Module genuinely not installed - log warning
                logger.warning("token_revocation module not installed, skipping revocation check")
            except Exception as e:
                # Code error in revocation service - fail closed (reject token)
                logger.error(f"Token revocation check failed: {e}")
                raise AuthError("Token revocation check failed", "revocation_check_failed")

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


def _get_unsafe_decode_options() -> dict:
    """Get decode options for debugging (no verification)."""
    return {"verify_signature": False}


def decode_token_unsafe(token: str) -> dict:
    """
    UNSAFE: Decode token WITHOUT signature verification.

    SECURITY WARNING: This function does NOT verify the token signature!
    - NEVER use for authorization decisions
    - NEVER trust data from this function for access control
    - Use ONLY for debugging, logging, or extracting non-sensitive metadata
    """
    try:
        # nosemgrep: python.jwt.security.unverified-jwt-decode
        return jwt.decode(token, options=_get_unsafe_decode_options(), algorithms=["HS256", "HS384", "HS512"])
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
    expires_delta: timedelta | None = None,
    token_type: str = "access",
    extra_claims: dict | None = None,
    jti: str | None = None,
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
    now = datetime.now(UTC)

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

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


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
