"""
SAHOOL CORS Configuration - Root Shared Module
تكوين CORS المركزي - الوحدة المشتركة الجذرية

This module provides centralized CORS configuration accessible from the root
shared package. Services importing from shared.cors_config will resolve here.

Version: 1.0.0
"""

import logging
import os

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Origin Whitelists
# ═══════════════════════════════════════════════════════════════════════════════

PRODUCTION_ORIGINS = [
    "https://sahool.app",
    "https://admin.sahool.app",
    "https://api.sahool.app",
    "https://www.sahool.app",
]

DEVELOPMENT_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

STAGING_ORIGINS = [
    "https://staging.sahool.app",
    "https://admin-staging.sahool.app",
    "https://api-staging.sahool.app",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Environment-Based Origin Selection
# ═══════════════════════════════════════════════════════════════════════════════


def get_allowed_origins() -> list[str]:
    """
    Get allowed CORS origins based on the current environment.

    Priority:
    1. CORS_ORIGINS environment variable (comma-separated)
    2. Environment-specific defaults (ENVIRONMENT variable)
    3. Development origins (safest fallback)
    """
    cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
    if cors_origins_env:
        origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
        environment = os.getenv("ENVIRONMENT", "development").lower()
        if "*" in origins and environment == "production":
            logger.critical(
                "SECURITY ALERT: Wildcard (*) CORS origin in production. Falling back to PRODUCTION_ORIGINS."
            )
            return PRODUCTION_ORIGINS
        return origins

    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment == "production":
        return PRODUCTION_ORIGINS
    elif environment == "staging":
        return STAGING_ORIGINS
    return DEVELOPMENT_ORIGINS


def get_cors_config() -> dict:
    """Get current CORS configuration as a dictionary."""
    origins = get_allowed_origins()
    cors_env = os.getenv("CORS_ORIGINS", "")
    return {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "allowed_origins": origins,
        "cors_origins_env": cors_env if cors_env else "not set",
        "has_wildcard": "*" in origins,
        "origin_count": len(origins),
    }


def validate_origin(origin: str) -> bool:
    """Validate if an origin is in the allowed list."""
    allowed = get_allowed_origins()
    return origin in allowed or "*" in allowed


def setup_cors_middleware(app, **kwargs):
    """Configure CORS middleware for a FastAPI application."""
    try:
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        logger.warning("FastAPI not available, cannot setup CORS middleware")
        return

    origins = kwargs.pop("allow_origins", None) or get_allowed_origins()
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if "*" in origins and environment == "production":
        logger.critical("Wildcard CORS blocked in production")
        origins = PRODUCTION_ORIGINS

    defaults = {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        "allow_headers": [
            "Accept",
            "Accept-Language",
            "Authorization",
            "Content-Type",
            "Content-Language",
            "X-Request-ID",
            "X-Correlation-ID",
            "X-Tenant-ID",
            "X-API-Key",
            "X-User-ID",
        ],
        "expose_headers": [
            "X-Request-ID",
            "X-Correlation-ID",
            "X-Total-Count",
            "X-Page-Count",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ],
        "max_age": 3600,
    }
    defaults.update(kwargs)
    app.add_middleware(CORSMiddleware, **defaults)
    logger.info("CORS configured: environment=%s, origins=%s", environment, origins)


# ═══════════════════════════════════════════════════════════════════════════════
# Lazy-loaded CORS_SETTINGS for backward compatibility
# ═══════════════════════════════════════════════════════════════════════════════


class _CORSSettings:
    """Lazy loader for CORS settings dict interface."""

    def __init__(self):
        self._settings = None

    def _ensure_loaded(self):
        if self._settings is None:
            self._settings = {
                "allow_origins": get_allowed_origins(),
                "allow_credentials": True,
                "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
                "allow_headers": [
                    "Accept",
                    "Accept-Language",
                    "Authorization",
                    "Content-Type",
                    "Content-Language",
                    "X-Request-ID",
                    "X-Correlation-ID",
                    "X-Tenant-ID",
                    "X-API-Key",
                    "X-User-ID",
                ],
                "expose_headers": [
                    "X-Request-ID",
                    "X-Correlation-ID",
                    "X-Total-Count",
                    "X-Page-Count",
                    "X-RateLimit-Limit",
                    "X-RateLimit-Remaining",
                    "X-RateLimit-Reset",
                ],
                "max_age": 3600,
            }

    def __getitem__(self, key):
        self._ensure_loaded()
        return self._settings[key]

    def __iter__(self):
        self._ensure_loaded()
        return iter(self._settings)

    def keys(self):
        self._ensure_loaded()
        return self._settings.keys()

    def values(self):
        self._ensure_loaded()
        return self._settings.values()

    def items(self):
        self._ensure_loaded()
        return self._settings.items()

    def get(self, key, default=None):
        self._ensure_loaded()
        return self._settings.get(key, default)


CORS_SETTINGS = _CORSSettings()

__all__ = [
    "CORS_SETTINGS",
    "DEVELOPMENT_ORIGINS",
    "PRODUCTION_ORIGINS",
    "STAGING_ORIGINS",
    "get_allowed_origins",
    "get_cors_config",
    "setup_cors_middleware",
    "validate_origin",
]
