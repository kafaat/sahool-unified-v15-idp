"""
JWT Token Handler for SAHOOL Platform
Token creation and verification using PyJWT
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt import PyJWTError

from .config import config
from .models import AuthErrors, AuthException, TokenPayload

# SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
# Never trust algorithm from environment variables or token header
ALLOWED_ALGORITHMS = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]


def create_access_token(
    user_id: str,
    roles: list[str],
    expires_delta: Optional[timedelta] = None,
    tenant_id: Optional[str] = None,
    permissions: Optional[list[str]] = None,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: Unique user identifier
        roles: List of user roles
        expires_delta: Custom expiration time (default: 30 minutes)
        tenant_id: Optional tenant identifier
        permissions: List of user permissions
        extra_claims: Additional claims to include in the token

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token(
        ...     user_id="user123",
        ...     roles=["farmer", "admin"],
        ...     permissions=["farm:read", "farm:write"]
        ... )
    """
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Generate unique token ID for revocation support
    jti = str(uuid.uuid4())

    payload = {
        "sub": user_id,
        "roles": roles,
        "exp": expire,
        "iat": now,
        "iss": config.JWT_ISSUER,
        "aud": config.JWT_AUDIENCE,
        "jti": jti,
        "type": "access",
    }

    if tenant_id:
        payload["tid"] = tenant_id

    if permissions:
        payload["permissions"] = permissions

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        config.get_signing_key(),
        algorithm=config.JWT_ALGORITHM
    )


def create_refresh_token(
    user_id: str,
    tenant_id: Optional[str] = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        user_id: Unique user identifier
        tenant_id: Optional tenant identifier

    Returns:
        Encoded JWT refresh token string

    Example:
        >>> refresh_token = create_refresh_token(user_id="user123")
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)

    # Generate unique token ID for revocation support
    jti = str(uuid.uuid4())

    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": now,
        "iss": config.JWT_ISSUER,
        "aud": config.JWT_AUDIENCE,
        "jti": jti,
        "type": "refresh",
    }

    if tenant_id:
        payload["tid"] = tenant_id

    return jwt.encode(
        payload,
        config.get_signing_key(),
        algorithm=config.JWT_ALGORITHM
    )


def verify_token(token: str) -> TokenPayload:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload object with decoded claims

    Raises:
        AuthException: If token is invalid, expired, or malformed

    Example:
        >>> payload = verify_token(token)
        >>> print(payload.user_id, payload.roles)

    Security: Uses hardcoded algorithm whitelist to prevent algorithm confusion attacks
    """
    try:
        # SECURITY FIX: Decode header to validate algorithm before verification
        unverified_header = jwt.get_unverified_header(token)

        if not unverified_header or "alg" not in unverified_header:
            raise AuthException(AuthErrors.INVALID_TOKEN)

        algorithm = unverified_header["alg"]

        # Reject 'none' algorithm explicitly
        if algorithm.lower() == "none":
            raise AuthException(AuthErrors.INVALID_TOKEN)

        # Verify algorithm is in whitelist
        if algorithm not in ALLOWED_ALGORITHMS:
            raise AuthException(AuthErrors.INVALID_TOKEN)

        # SECURITY FIX: Use hardcoded whitelist instead of environment variable
        payload = jwt.decode(
            token,
            config.get_verification_key(),
            algorithms=ALLOWED_ALGORITHMS,
            issuer=config.JWT_ISSUER,
            audience=config.JWT_AUDIENCE,
            options={
                "require": ["sub", "exp", "iat"],
            }
        )

        # Extract required fields
        user_id = payload.get("sub")
        if not user_id:
            raise AuthException(AuthErrors.INVALID_TOKEN)

        # Convert timestamps to datetime objects
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

        return TokenPayload(
            user_id=user_id,
            roles=payload.get("roles", []),
            exp=exp,
            iat=iat,
            tenant_id=payload.get("tid"),
            jti=payload.get("jti"),
            token_type=payload.get("type", "access"),
            permissions=payload.get("permissions", []),
        )

    except jwt.ExpiredSignatureError:
        raise AuthException(AuthErrors.EXPIRED_TOKEN)
    except jwt.InvalidIssuerError:
        raise AuthException(AuthErrors.INVALID_ISSUER)
    except jwt.InvalidAudienceError:
        raise AuthException(AuthErrors.INVALID_AUDIENCE)
    except PyJWTError as e:
        raise AuthException(AuthErrors.INVALID_TOKEN)


def decode_token_unsafe(token: str) -> dict:
    """
    ⚠️ UNSAFE: Decode a JWT token WITHOUT signature verification.

    SECURITY WARNING: This function does NOT verify the token signature!
    - NEVER use for authorization decisions
    - NEVER trust data from this function for access control
    - Use ONLY for debugging, logging, or extracting non-sensitive metadata

    Args:
        token: JWT token string

    Returns:
        Decoded token payload as dictionary (UNVERIFIED!)

    Example:
        >>> # For debugging only - data cannot be trusted
        >>> payload = decode_token_unsafe(token)
        >>> print(f"Debug: user_id={payload.get('sub')}")
    """
    try:
        # This function is intentionally unverified for debugging purposes only
        return jwt.decode(  # nosemgrep: python.jwt.security.unverified-jwt-decode.unverified-jwt-decode
            token,
            options={"verify_signature": False}
        )
    except PyJWTError:
        return {}


def create_token_pair(
    user_id: str,
    roles: list[str],
    tenant_id: Optional[str] = None,
    permissions: Optional[list[str]] = None,
) -> dict:
    """
    Create both access and refresh tokens.

    Args:
        user_id: Unique user identifier
        roles: List of user roles
        tenant_id: Optional tenant identifier
        permissions: List of user permissions

    Returns:
        Dictionary containing access_token, refresh_token, token_type, and expires_in

    Example:
        >>> tokens = create_token_pair(
        ...     user_id="user123",
        ...     roles=["farmer"],
        ...     permissions=["farm:read"]
        ... )
        >>> print(tokens["access_token"])
        >>> print(tokens["refresh_token"])
    """
    access_token = create_access_token(
        user_id=user_id,
        roles=roles,
        tenant_id=tenant_id,
        permissions=permissions,
    )

    refresh_token = create_refresh_token(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
    }


def refresh_access_token(refresh_token: str, roles: list[str], permissions: Optional[list[str]] = None) -> str:
    """
    Create a new access token using a refresh token.

    Args:
        refresh_token: Valid refresh token
        roles: User roles (must be fetched from database)
        permissions: User permissions (must be fetched from database)

    Returns:
        New access token

    Raises:
        AuthException: If refresh token is invalid or expired

    Example:
        >>> new_access_token = refresh_access_token(
        ...     refresh_token=refresh_token,
        ...     roles=["farmer"],
        ...     permissions=["farm:read"]
        ... )
    """
    payload = verify_token(refresh_token)

    if payload.token_type != "refresh":
        raise AuthException(AuthErrors.INVALID_TOKEN)

    return create_access_token(
        user_id=payload.user_id,
        roles=roles,
        tenant_id=payload.tenant_id,
        permissions=permissions,
    )
