"""
JWT Authentication Configuration for SAHOOL Platform
Centralized configuration for JWT token handling

Note: This configuration only supports HS256 algorithm.
RS256 with RSA keys has been deprecated.
"""

from __future__ import annotations

import logging
import os
import secrets
from typing import Dict, List

logger = logging.getLogger(__name__)

# Security constants
MIN_SECRET_KEY_LENGTH = 32
MIN_ACCESS_TOKEN_MINUTES = 1
MAX_ACCESS_TOKEN_MINUTES = 60  # 1 hour — industry standard max for access tokens
MIN_REFRESH_TOKEN_DAYS = 1
MAX_REFRESH_TOKEN_DAYS = 30  # 30 days max
MIN_RATE_LIMIT_REQUESTS = 1
MAX_RATE_LIMIT_REQUESTS = 10000
MIN_RATE_LIMIT_WINDOW_SECONDS = 1
MAX_RATE_LIMIT_WINDOW_SECONDS = 3600  # 1 hour
MIN_REDIS_PORT = 1
MAX_REDIS_PORT = 65535
MIN_REDIS_DB = 0
MAX_REDIS_DB = 15  # Redis typically supports 0-15


class JWTConfigError(Exception):
    """JWT Configuration validation error"""

    pass


def _resolve_jwt_secret() -> str:
    """Resolve JWT secret from environment with security-safe fallback.

    - production/staging: MUST have JWT_SECRET_KEY set, raises RuntimeError otherwise
    - development/test: generates a random per-process secret and warns loudly
    """
    value = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")
    if value:
        return value

    env = os.getenv("ENVIRONMENT", "development")
    if env in ("production", "staging"):
        raise RuntimeError(
            "JWT_SECRET_KEY must be set in production/staging environments. "
            "An empty or missing secret allows token forgery."
        )

    # Generate a random per-process secret for dev/test - NOT a hardcoded constant
    fallback = secrets.token_hex(32)
    logger.warning(
        "JWT_SECRET_KEY not set - using random per-process fallback. "
        "Tokens will NOT survive restarts. Set JWT_SECRET_KEY for persistence."
    )
    return fallback


class JWTConfig:
    """JWT Configuration Settings - HS256 Only"""

    # JWT Secret Key (required) - JWT_SECRET_KEY is the canonical name.
    # JWT_SECRET is accepted as a deprecated fallback for backward compatibility.
    # Note: Use get_signing_key()/get_verification_key() methods instead of reading
    # this attribute directly, as they re-read from env at call time.
    # SECURITY: In production/staging, JWT_SECRET_KEY MUST be set via environment.
    # In development/test, a per-process random fallback is generated to prevent
    # using a known hardcoded secret that would allow token forgery.
    JWT_SECRET: str = _resolve_jwt_secret()

    # JWT Algorithm - HS256 only (RS256 deprecated)
    JWT_ALGORITHM: str = "HS256"

    # Token expiration times
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # JWT Issuer and Audience
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "sahool-platform")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "sahool-api")

    # Token header name
    TOKEN_HEADER: str = "Authorization"
    TOKEN_PREFIX: str = "Bearer"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

    # Token revocation
    TOKEN_REVOCATION_ENABLED: bool = os.getenv("TOKEN_REVOCATION_ENABLED", "true").lower() == "true"

    # Redis configuration for token revocation
    REDIS_URL: str | None = os.getenv("REDIS_URL")
    # Default to "redis" (Docker service name) instead of "localhost" so that
    # services running inside Docker containers can reach the Redis container
    # without explicitly setting REDIS_URL.  Local development can override via
    # REDIS_HOST=localhost in the shell environment.
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD")

    @classmethod
    def validate(cls) -> None:
        """
        Validate JWT configuration and raise errors for invalid settings.

        Performs comprehensive validation including:
        - JWT secret key strength and length
        - Token expiration times (reasonable ranges)
        - Rate limiting parameters
        - Redis configuration when needed
        - JWT issuer and audience non-empty

        Raises:
            JWTConfigError: If any critical configuration is invalid
        """
        env = os.getenv("ENVIRONMENT", "development")
        errors: list[str] = []
        warnings: list[str] = []

        # Warn if JWT_SECRET is used instead of JWT_SECRET_KEY
        if not os.getenv("JWT_SECRET_KEY") and os.getenv("JWT_SECRET"):
            warnings.append("DEPRECATION: JWT_SECRET is deprecated. Use JWT_SECRET_KEY instead.")

        # Validate JWT Secret
        if not cls.JWT_SECRET:
            msg = "JWT_SECRET_KEY is not set"
            if env in ("production", "staging"):
                errors.append(msg)
            else:
                warnings.append(f"WARNING: {msg} (development mode)")
        elif len(cls.JWT_SECRET) < MIN_SECRET_KEY_LENGTH:
            msg = f"JWT_SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters (currently {len(cls.JWT_SECRET)} characters)"
            if env in ("production", "staging"):
                errors.append(msg)
            else:
                warnings.append(f"WARNING: {msg} (development mode)")
        elif cls.JWT_SECRET.startswith("MUST_SET") or cls.JWT_SECRET.startswith("change_"):
            msg = "JWT_SECRET_KEY appears to be a placeholder value — set a real secret"
            if env in ("production", "staging"):
                errors.append(msg)
            else:
                warnings.append(f"WARNING: {msg} (development mode)")

        # Validate token expiration times
        if not (MIN_ACCESS_TOKEN_MINUTES <= cls.ACCESS_TOKEN_EXPIRE_MINUTES <= MAX_ACCESS_TOKEN_MINUTES):
            errors.append(
                f"ACCESS_TOKEN_EXPIRE_MINUTES must be between {MIN_ACCESS_TOKEN_MINUTES} and {MAX_ACCESS_TOKEN_MINUTES} "
                f"(currently {cls.ACCESS_TOKEN_EXPIRE_MINUTES})"
            )

        if not (MIN_REFRESH_TOKEN_DAYS <= cls.REFRESH_TOKEN_EXPIRE_DAYS <= MAX_REFRESH_TOKEN_DAYS):
            errors.append(
                f"REFRESH_TOKEN_EXPIRE_DAYS must be between {MIN_REFRESH_TOKEN_DAYS} and {MAX_REFRESH_TOKEN_DAYS} "
                f"(currently {cls.REFRESH_TOKEN_EXPIRE_DAYS})"
            )

        # Validate issuer and audience are non-empty
        if not cls.JWT_ISSUER:
            errors.append("JWT_ISSUER cannot be empty")

        if not cls.JWT_AUDIENCE:
            errors.append("JWT_AUDIENCE cannot be empty")

        # Validate rate limiting parameters
        if cls.RATE_LIMIT_ENABLED:
            if not (MIN_RATE_LIMIT_REQUESTS <= cls.RATE_LIMIT_REQUESTS <= MAX_RATE_LIMIT_REQUESTS):
                errors.append(
                    f"RATE_LIMIT_REQUESTS must be between {MIN_RATE_LIMIT_REQUESTS} and {MAX_RATE_LIMIT_REQUESTS} "
                    f"(currently {cls.RATE_LIMIT_REQUESTS})"
                )

            if not (MIN_RATE_LIMIT_WINDOW_SECONDS <= cls.RATE_LIMIT_WINDOW_SECONDS <= MAX_RATE_LIMIT_WINDOW_SECONDS):
                errors.append(
                    f"RATE_LIMIT_WINDOW_SECONDS must be between {MIN_RATE_LIMIT_WINDOW_SECONDS} and {MAX_RATE_LIMIT_WINDOW_SECONDS} "
                    f"(currently {cls.RATE_LIMIT_WINDOW_SECONDS})"
                )

        # Validate Redis configuration when token revocation is enabled
        if cls.TOKEN_REVOCATION_ENABLED:
            if not (MIN_REDIS_PORT <= cls.REDIS_PORT <= MAX_REDIS_PORT):
                errors.append(
                    f"REDIS_PORT must be between {MIN_REDIS_PORT} and {MAX_REDIS_PORT} (currently {cls.REDIS_PORT})"
                )

            if not (MIN_REDIS_DB <= cls.REDIS_DB <= MAX_REDIS_DB):
                errors.append(f"REDIS_DB must be between {MIN_REDIS_DB} and {MAX_REDIS_DB} (currently {cls.REDIS_DB})")

            # Warn if neither REDIS_URL nor HOST is properly configured
            if not cls.REDIS_URL and not cls.REDIS_HOST:
                errors.append("Either REDIS_URL or REDIS_HOST must be configured when TOKEN_REVOCATION_ENABLED is true")

        # Log warnings
        for warning in warnings:
            logger.warning(warning)

        # Raise error if any validation failed
        if errors:
            error_message = "JWT Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise JWTConfigError(error_message)

        logger.info("JWT Configuration validation passed")

    @classmethod
    def validate_with_report(cls) -> dict[str, bool | list[str]]:
        """
        Validate JWT configuration and return detailed report.

        Returns:
            Dict containing:
                - 'valid': True if all checks pass, False otherwise
                - 'errors': List of error messages (if any)
                - 'warnings': List of warning messages (if any)
                - 'summary': Summary of configuration
        """
        env = os.getenv("ENVIRONMENT", "development")
        errors: list[str] = []
        warnings: list[str] = []

        # Validate JWT Secret
        if not cls.JWT_SECRET:
            msg = "JWT_SECRET_KEY is not set"
            if env in ("production", "staging"):
                errors.append(msg)
            else:
                warnings.append(msg)
        elif len(cls.JWT_SECRET) < MIN_SECRET_KEY_LENGTH:
            msg = f"JWT_SECRET_KEY length is {len(cls.JWT_SECRET)}, minimum recommended is {MIN_SECRET_KEY_LENGTH}"
            if env in ("production", "staging"):
                errors.append(msg)
            else:
                warnings.append(msg)

        # Validate token expiration times
        if not (MIN_ACCESS_TOKEN_MINUTES <= cls.ACCESS_TOKEN_EXPIRE_MINUTES <= MAX_ACCESS_TOKEN_MINUTES):
            errors.append(
                f"ACCESS_TOKEN_EXPIRE_MINUTES {cls.ACCESS_TOKEN_EXPIRE_MINUTES} out of range "
                f"[{MIN_ACCESS_TOKEN_MINUTES}, {MAX_ACCESS_TOKEN_MINUTES}]"
            )

        if not (MIN_REFRESH_TOKEN_DAYS <= cls.REFRESH_TOKEN_EXPIRE_DAYS <= MAX_REFRESH_TOKEN_DAYS):
            errors.append(
                f"REFRESH_TOKEN_EXPIRE_DAYS {cls.REFRESH_TOKEN_EXPIRE_DAYS} out of range "
                f"[{MIN_REFRESH_TOKEN_DAYS}, {MAX_REFRESH_TOKEN_DAYS}]"
            )

        # Validate issuer and audience
        if not cls.JWT_ISSUER:
            errors.append("JWT_ISSUER cannot be empty")

        if not cls.JWT_AUDIENCE:
            errors.append("JWT_AUDIENCE cannot be empty")

        # Validate rate limiting
        if cls.RATE_LIMIT_ENABLED:
            if not (MIN_RATE_LIMIT_REQUESTS <= cls.RATE_LIMIT_REQUESTS <= MAX_RATE_LIMIT_REQUESTS):
                errors.append(
                    f"RATE_LIMIT_REQUESTS {cls.RATE_LIMIT_REQUESTS} out of range "
                    f"[{MIN_RATE_LIMIT_REQUESTS}, {MAX_RATE_LIMIT_REQUESTS}]"
                )

            if not (MIN_RATE_LIMIT_WINDOW_SECONDS <= cls.RATE_LIMIT_WINDOW_SECONDS <= MAX_RATE_LIMIT_WINDOW_SECONDS):
                errors.append(
                    f"RATE_LIMIT_WINDOW_SECONDS {cls.RATE_LIMIT_WINDOW_SECONDS} out of range "
                    f"[{MIN_RATE_LIMIT_WINDOW_SECONDS}, {MAX_RATE_LIMIT_WINDOW_SECONDS}]"
                )

        # Validate Redis configuration
        if cls.TOKEN_REVOCATION_ENABLED:
            if not (MIN_REDIS_PORT <= cls.REDIS_PORT <= MAX_REDIS_PORT):
                errors.append(f"REDIS_PORT {cls.REDIS_PORT} out of valid range [1, 65535]")

            if not (MIN_REDIS_DB <= cls.REDIS_DB <= MAX_REDIS_DB):
                errors.append(f"REDIS_DB {cls.REDIS_DB} out of valid range [0, 15]")

            if not cls.REDIS_URL and not cls.REDIS_HOST:
                errors.append("Redis configuration incomplete: neither REDIS_URL nor REDIS_HOST configured")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "environment": env,
            "summary": {
                "jwt_secret_configured": bool(cls.JWT_SECRET),
                "jwt_secret_length": len(cls.JWT_SECRET) if cls.JWT_SECRET else 0,
                "access_token_minutes": cls.ACCESS_TOKEN_EXPIRE_MINUTES,
                "refresh_token_days": cls.REFRESH_TOKEN_EXPIRE_DAYS,
                "rate_limiting_enabled": cls.RATE_LIMIT_ENABLED,
                "token_revocation_enabled": cls.TOKEN_REVOCATION_ENABLED,
                "redis_configured": bool(cls.REDIS_URL or cls.REDIS_HOST),
            },
        }

    @classmethod
    def _resolve_secret(cls) -> str:
        """Resolve JWT secret from environment at call time.

        Reads from environment to support dynamic configuration
        (e.g., test fixtures that set JWT_SECRET_KEY after module import).

        Raises:
            JWTConfigError: If JWT_SECRET_KEY env var is not set or too short
        """
        secret = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET") or cls.JWT_SECRET
        if not secret or len(secret) < MIN_SECRET_KEY_LENGTH:
            raise JWTConfigError(
                f"JWT_SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters. "
                "Set JWT_SECRET_KEY environment variable."
            )
        return secret

    @classmethod
    def get_signing_key(cls) -> str:
        """Get the key for signing tokens (HS256 only)."""
        return cls._resolve_secret()

    @classmethod
    def get_verification_key(cls) -> str:
        """Get the key for verifying tokens (HS256 only)."""
        return cls._resolve_secret()


# Singleton instance
config = JWTConfig()
