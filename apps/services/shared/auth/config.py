"""
Authentication Configuration
تكوين المصادقة
"""

import logging
import os
import secrets
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


def _resolve_secret_key(prefix: str = "AUTH") -> str:
    """Resolve auth secret key with a unified, env-aware fallback chain.

    Order of precedence:
    1. ``{prefix}_SECRET_KEY`` (prefix-specific, e.g. ``AUTH_SECRET_KEY``) —
       wins first because callers may instantiate multiple ``AuthConfig``s
       with different prefixes.
    2. ``JWT_SECRET_KEY`` (platform-wide canonical name, matches
       ``shared/auth/config.py``).
    3. ``JWT_SECRET`` (deprecated alias, retained for backward compatibility).
    4. Random per-process token **only** in development/test environments.
       In ``production`` / ``staging`` an empty string is returned and an
       error is logged — downstream validation is expected to reject empty
       secrets, mirroring the behavior of ``shared/auth/config.py``.
    """
    value = os.getenv(f"{prefix}_SECRET_KEY") or os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")
    if value:
        return value

    env = os.getenv("ENVIRONMENT", "development")
    if env in ("production", "staging"):
        logger.error(  # nosemgrep: python-logger-credential-disclosure
            "SECURITY: No auth secret env var set in %s environment "
            "(checked %s_SECRET_KEY, JWT_SECRET_KEY, JWT_SECRET). "
            "Service will reject all auth until configured.",
            env,
            prefix,
        )
        return ""

    logger.warning(
        "%s_SECRET_KEY not set - using random per-process fallback. "
        "Tokens will NOT survive restarts. Set %s_SECRET_KEY or JWT_SECRET_KEY.",
        prefix,
        prefix,
    )
    return secrets.token_urlsafe(32)


@dataclass
class AuthConfig:
    """Authentication configuration settings"""

    # JWT Settings
    secret_key: str = field(default_factory=_resolve_secret_key)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # JWT Issuer and Audience (for token validation)
    issuer: str = "sahool-auth"
    audience: str = "sahool-api"

    # API Key Settings
    api_key_header: str = "X-API-Key"
    api_keys: list[str] = field(default_factory=list)

    # Password Settings
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = False

    # Session Settings
    session_max_age: int = 86400  # 24 hours

    # OAuth2 Settings (for external providers)
    oauth2_enabled: bool = False
    google_client_id: str | None = None
    google_client_secret: str | None = None

    @classmethod
    def from_env(cls, prefix: str = "AUTH") -> "AuthConfig":
        """Load configuration from environment variables"""
        api_keys_str = os.getenv(f"{prefix}_API_KEYS", "")
        api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]

        return cls(
            secret_key=_resolve_secret_key(prefix),
            algorithm=os.getenv(f"{prefix}_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv(f"{prefix}_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            refresh_token_expire_days=int(os.getenv(f"{prefix}_REFRESH_TOKEN_EXPIRE_DAYS", "7")),
            issuer=os.getenv(f"{prefix}_ISSUER", "sahool-auth"),
            audience=os.getenv(f"{prefix}_AUDIENCE", "sahool-api"),
            api_key_header=os.getenv(f"{prefix}_API_KEY_HEADER", "X-API-Key"),
            api_keys=api_keys,
            password_min_length=int(os.getenv(f"{prefix}_PASSWORD_MIN_LENGTH", "8")),
            password_require_uppercase=os.getenv(f"{prefix}_PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
            password_require_lowercase=os.getenv(f"{prefix}_PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true",
            password_require_digit=os.getenv(f"{prefix}_PASSWORD_REQUIRE_DIGIT", "true").lower() == "true",
            password_require_special=os.getenv(f"{prefix}_PASSWORD_REQUIRE_SPECIAL", "false").lower() == "true",
            session_max_age=int(os.getenv(f"{prefix}_SESSION_MAX_AGE", "86400")),
            oauth2_enabled=os.getenv(f"{prefix}_OAUTH2_ENABLED", "false").lower() == "true",
            google_client_id=os.getenv(f"{prefix}_GOOGLE_CLIENT_ID"),
            google_client_secret=os.getenv(f"{prefix}_GOOGLE_CLIENT_SECRET"),
        )


# Global config instance
_config: AuthConfig | None = None


def get_auth_config() -> AuthConfig:
    """Get or create the auth configuration"""
    global _config
    if _config is None:
        _config = AuthConfig.from_env()
    return _config


def set_auth_config(config: AuthConfig) -> None:
    """Set the auth configuration"""
    global _config
    _config = config
