"""
JWT Token Management
إدارة رموز JWT
"""

import logging
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from .config import get_auth_config

logger = logging.getLogger(__name__)


def generate_jti() -> str:
    """
    Generate a unique JWT ID (JTI)

    Returns:
        Cryptographically secure random token ID
    """
    return secrets.token_urlsafe(32)


@dataclass
class TokenData:
    """Decoded token data"""

    user_id: str
    email: str | None = None
    tenant_id: str | None = None
    roles: list[str] = None
    permissions: list[str] = None
    token_type: str = "access"
    jti: str | None = None  # JWT ID for revocation tracking
    family_id: str | None = None  # Token family for refresh token rotation
    exp: datetime | None = None
    iat: datetime | None = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = []
        if self.permissions is None:
            self.permissions = []

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role"""
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in self.permissions

    def has_any_role(self, roles: list[str]) -> bool:
        """Check if user has any of the specified roles"""
        return any(role in self.roles for role in roles)

    def has_all_roles(self, roles: list[str]) -> bool:
        """Check if user has all specified roles"""
        return all(role in self.roles for role in roles)


def create_access_token(
    user_id: str,
    email: str | None = None,
    tenant_id: str | None = None,
    roles: list[str] | None = None,
    permissions: list[str] | None = None,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
    jti: str | None = None,
) -> tuple[str, str]:
    """
    Create a new access token
    إنشاء رمز وصول جديد

    Returns:
        Tuple of (token, jti) for revocation tracking
    """
    config = get_auth_config()

    if expires_delta is None:
        expires_delta = timedelta(minutes=config.access_token_expire_minutes)

    # Generate JTI if not provided
    if jti is None:
        jti = generate_jti()

    now = datetime.now(UTC)
    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "type": "access",
        "jti": jti,
        "iat": now,
        "exp": expire,
    }

    if email:
        payload["email"] = email
    if tenant_id:
        payload["tenant_id"] = tenant_id
    if roles:
        payload["roles"] = roles
    if permissions:
        payload["permissions"] = permissions
    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, config.secret_key, algorithm=config.algorithm)
    logger.debug(f"Created access token for user {user_id}, jti={jti[:8]}..., expires at {expire}")

    return token, jti


def create_refresh_token(
    user_id: str,
    tenant_id: str | None = None,
    expires_delta: timedelta | None = None,
    family_id: str | None = None,
    jti: str | None = None,
) -> tuple[str, str, str]:
    """
    Create a new refresh token
    إنشاء رمز تحديث جديد

    Args:
        user_id: User identifier
        tenant_id: Tenant identifier
        expires_delta: Token expiration time
        family_id: Token family ID for rotation (generated if None)
        jti: JWT ID (generated if None)

    Returns:
        Tuple of (token, jti, family_id) for revocation tracking
    """
    config = get_auth_config()

    if expires_delta is None:
        expires_delta = timedelta(days=config.refresh_token_expire_days)

    # Generate JTI and family_id if not provided
    if jti is None:
        jti = generate_jti()
    if family_id is None:
        family_id = generate_jti()

    now = datetime.now(UTC)
    expire = now + expires_delta

    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": jti,
        "family_id": family_id,
        "iat": now,
        "exp": expire,
    }

    if tenant_id:
        payload["tenant_id"] = tenant_id

    token = jwt.encode(payload, config.secret_key, algorithm=config.algorithm)
    logger.debug(f"Created refresh token for user {user_id}, jti={jti[:8]}..., family={family_id[:8]}..., expires at {expire}")

    return token, jti, family_id


def verify_token(token: str, token_type: str = "access") -> bool:
    """
    Verify a token is valid
    التحقق من صحة الرمز
    """
    try:
        data = decode_token(token)
        if data.token_type != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {data.token_type}")
            return False
        return True
    except Exception:
        return False


def decode_token(token: str, verify_audience: bool = True) -> TokenData:
    """
    Decode and validate a JWT token with issuer and audience verification.
    فك تشفير والتحقق من رمز JWT مع التحقق من المُصدر والجمهور.
    """
    config = get_auth_config()

    # Expected issuer and audience for SAHOOL platform
    expected_issuer = getattr(config, "issuer", "sahool-auth")
    expected_audience = getattr(config, "audience", "sahool-api")

    try:
        # Build decode options with security validations
        decode_options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
            "require": ["exp", "iat", "sub"],
        }

        # Add issuer/audience verification if configured
        decode_kwargs = {
            "algorithms": [config.algorithm],
            "options": decode_options,
        }

        # Verify issuer if present in token
        if expected_issuer:
            decode_kwargs["issuer"] = expected_issuer
            decode_options["verify_iss"] = True

        # Verify audience if enabled and configured
        if verify_audience and expected_audience:
            decode_kwargs["audience"] = expected_audience
            decode_options["verify_aud"] = True

        payload = jwt.decode(
            token,
            config.secret_key,
            **decode_kwargs,
        )

        return TokenData(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            tenant_id=payload.get("tenant_id"),
            roles=payload.get("roles", []),
            permissions=payload.get("permissions", []),
            token_type=payload.get("type", "access"),
            jti=payload.get("jti"),
            family_id=payload.get("family_id"),
            exp=datetime.fromtimestamp(payload.get("exp", 0), tz=UTC),
            iat=datetime.fromtimestamp(payload.get("iat", 0), tz=UTC),
        )

    except ExpiredSignatureError:
        logger.warning("Token has expired")
        raise ValueError("Token has expired")
    except InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise ValueError(f"Invalid token: {e}") from e


def refresh_access_token(refresh_token: str) -> tuple[str, str]:
    """
    Use a refresh token to create a new access token
    استخدام رمز التحديث لإنشاء رمز وصول جديد

    Returns:
        Tuple of (token, jti) for revocation tracking
    """
    token_data = decode_token(refresh_token)

    if token_data.token_type != "refresh":
        raise ValueError("Invalid token type. Expected refresh token.")

    return create_access_token(
        user_id=token_data.user_id,
        email=token_data.email,
        tenant_id=token_data.tenant_id,
        roles=token_data.roles,
        permissions=token_data.permissions,
    )
