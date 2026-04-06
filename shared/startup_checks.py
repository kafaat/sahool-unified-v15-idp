"""
SAHOOL Startup Environment Validation
=======================================
فحص متغيرات البيئة عند بدء التشغيل - فشل سريع

Validates required environment variables at service startup.
Fails fast with clear error messages instead of crashing later
with cryptic errors deep in the service lifecycle.

Usage:
    from shared.startup_checks import validate_startup, ServiceProfile

    # In service main.py or lifespan
    validate_startup(
        service_name="billing-core",
        profile=ServiceProfile.DATABASE | ServiceProfile.NATS,
    )

    # Or validate specific variables
    from shared.startup_checks import require_env
    db_url = require_env("DATABASE_URL")
"""

from __future__ import annotations

import logging
import os
from enum import Flag, auto

logger = logging.getLogger(__name__)


class ServiceProfile(Flag):
    """
    Service dependency profiles.
    Combine with | to specify which infrastructure a service needs.

    Examples:
        DATABASE | NATS          # Service needs DB + messaging
        DATABASE | REDIS | NATS  # Service needs all three
        MINIMAL                  # Health-check only service
    """

    MINIMAL = 0
    DATABASE = auto()
    REDIS = auto()
    NATS = auto()
    JWT_AUTH = auto()

    @classmethod
    def full_stack(cls) -> ServiceProfile:
        """All infrastructure components."""
        return cls.DATABASE | cls.REDIS | cls.NATS | cls.JWT_AUTH


# Required env vars per profile
_PROFILE_REQUIREMENTS: dict[ServiceProfile, list[tuple[str, str]]] = {
    ServiceProfile.DATABASE: [
        ("DATABASE_URL", "PostgreSQL connection string (e.g., postgresql://user:pass@host:5432/db)"),
    ],
    ServiceProfile.REDIS: [
        ("REDIS_URL", "Redis connection URL (e.g., redis://redis:6379)"),
    ],
    ServiceProfile.NATS: [
        ("NATS_URL", "NATS server URL (e.g., nats://nats:4222)"),
    ],
    ServiceProfile.JWT_AUTH: [
        ("JWT_SECRET_KEY", "JWT signing key (minimum 32 characters)"),
    ],
}

# Always required
_ALWAYS_REQUIRED: list[tuple[str, str]] = [
    ("ENVIRONMENT", "Deployment environment (development|staging|production|test)"),
]

# Valid environments
_VALID_ENVIRONMENTS = {"development", "staging", "production", "test", "dev", "testing"}


class StartupValidationError(SystemExit):
    """Raised when startup validation fails. Exits with code 1."""

    def __init__(self, errors: list[str], service_name: str):
        message = (
            f"\n{'=' * 60}\n"
            f" STARTUP VALIDATION FAILED: {service_name}\n"
            f" فشل التحقق من الإعدادات عند بدء التشغيل\n"
            f"{'=' * 60}\n\n" + "\n".join(f"  - {e}" for e in errors) + f"\n\n{'=' * 60}\n"
        )
        logger.critical(message)
        super().__init__(1)


def require_env(name: str, description: str = "") -> str:
    """
    Get a required environment variable or raise an error.

    Args:
        name: Environment variable name
        description: Human-readable description for error message

    Returns:
        The environment variable value

    Raises:
        StartupValidationError: If the variable is not set or empty
    """
    value = os.getenv(name, "").strip()
    if not value:
        desc = f" ({description})" if description else ""
        raise StartupValidationError(
            [f"Missing required: {name}{desc}"],
            service_name="unknown",
        )
    return value


def validate_startup(
    service_name: str,
    profile: ServiceProfile = ServiceProfile.MINIMAL,
    extra_required: list[tuple[str, str]] | None = None,
) -> dict[str, str]:
    """
    Validate all required environment variables for a service.

    Call this at the very start of service initialization (in lifespan
    or before FastAPI app creation). Fails fast with clear error
    messages listing ALL missing variables at once.

    Args:
        service_name: Service name for error messages
        profile: Infrastructure profile flags
        extra_required: Additional (name, description) pairs

    Returns:
        Dict of validated variable names → values

    Raises:
        StartupValidationError: If any required variable is missing
    """
    errors: list[str] = []
    validated: dict[str, str] = {}

    # Collect all requirements
    requirements: list[tuple[str, str]] = list(_ALWAYS_REQUIRED)

    for flag in ServiceProfile:
        if flag == ServiceProfile.MINIMAL:
            continue
        if flag in profile:
            requirements.extend(_PROFILE_REQUIREMENTS.get(flag, []))

    if extra_required:
        requirements.extend(extra_required)

    # Check each requirement
    for name, description in requirements:
        value = os.getenv(name, "").strip()
        if not value:
            errors.append(f"Missing: {name} — {description}")
        else:
            validated[name] = value

    # Validate ENVIRONMENT value
    env = validated.get("ENVIRONMENT", "")
    if env and env.lower() not in _VALID_ENVIRONMENTS:
        errors.append(f"Invalid ENVIRONMENT='{env}'. Must be one of: {', '.join(sorted(_VALID_ENVIRONMENTS))}")

    # Validate JWT_SECRET_KEY length
    jwt_key = validated.get("JWT_SECRET_KEY", "")
    if jwt_key and len(jwt_key) < 32:
        errors.append(
            f"JWT_SECRET_KEY is too short ({len(jwt_key)} chars). Minimum 32 characters required for security."
        )

    if errors:
        raise StartupValidationError(errors, service_name)

    logger.info(
        "startup_validation_passed",
        extra={
            "service": service_name,
            "profile": str(profile),
            "validated_vars": len(validated),
        },
    )

    return validated
