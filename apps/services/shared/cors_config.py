"""
SAHOOL CORS Configuration - Compatibility Shim
تكوين CORS - طبقة التوافق

This file provides backward compatibility for services importing from shared.cors_config.
Attempts to load from shared/config/cors_config.py first, then falls back to a
self-contained implementation so that services never crash on import.

Version: 1.1.0
"""

try:
    # Primary: re-export from the detailed config module
    from .config.cors_config import (
        CORS_SETTINGS,
        DEVELOPMENT_ORIGINS,
        PRODUCTION_ORIGINS,
        STAGING_ORIGINS,
        get_allowed_origins,
        get_cors_config,
        setup_cors_middleware,
        validate_origin,
    )
except (ImportError, SystemError):
    # Fallback: self-contained CORS configuration when config subpackage is
    # unavailable (e.g. Docker overlay copies root shared/ without the
    # apps/services/shared/config/ subtree).
    import logging as _logging
    import os as _os

    _logger = _logging.getLogger(__name__)

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

    def get_allowed_origins() -> list[str]:
        cors_origins_env = _os.getenv("CORS_ORIGINS", "").strip()
        if cors_origins_env:
            origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
            environment = _os.getenv("ENVIRONMENT", "development").lower()
            if "*" in origins and environment == "production":
                _logger.critical(
                    "SECURITY ALERT: Wildcard (*) CORS origin in production. Falling back to PRODUCTION_ORIGINS."
                )
                return PRODUCTION_ORIGINS
            return origins
        environment = _os.getenv("ENVIRONMENT", "development").lower()
        if environment == "production":
            return PRODUCTION_ORIGINS
        elif environment == "staging":
            return STAGING_ORIGINS
        return DEVELOPMENT_ORIGINS

    def get_cors_config() -> dict:
        origins = get_allowed_origins()
        cors_env = _os.getenv("CORS_ORIGINS", "")
        return {
            "environment": _os.getenv("ENVIRONMENT", "development"),
            "allowed_origins": origins,
            "cors_origins_env": cors_env if cors_env else "not set",
            "has_wildcard": "*" in origins,
            "origin_count": len(origins),
        }

    def validate_origin(origin: str) -> bool:
        allowed = get_allowed_origins()
        return origin in allowed or "*" in allowed

    def setup_cors_middleware(app, **kwargs):
        try:
            from fastapi.middleware.cors import CORSMiddleware
        except ImportError:
            _logger.warning("FastAPI not available, cannot setup CORS middleware")
            return
        origins = kwargs.pop("allow_origins", None) or get_allowed_origins()
        environment = _os.getenv("ENVIRONMENT", "development").lower()
        if "*" in origins and environment == "production":
            _logger.critical("Wildcard CORS blocked in production")
            origins = PRODUCTION_ORIGINS
        defaults = {
            "allow_origins": origins,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
            "allow_headers": [
                "Accept", "Accept-Language", "Authorization", "Content-Type",
                "Content-Language", "X-Request-ID", "X-Correlation-ID",
                "X-Tenant-ID", "X-API-Key", "X-User-ID",
            ],
            "expose_headers": [
                "X-Request-ID", "X-Correlation-ID", "X-Total-Count", "X-Page-Count",
                "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset",
            ],
            "max_age": 3600,
        }
        defaults.update(kwargs)
        app.add_middleware(CORSMiddleware, **defaults)
        _logger.info("CORS configured: environment=%s, origins=%s", environment, origins)

    class _CORSSettings:
        def __init__(self):
            self._settings = None

        def _ensure_loaded(self):
            if self._settings is None:
                self._settings = {
                    "allow_origins": get_allowed_origins(),
                    "allow_credentials": True,
                    "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
                    "allow_headers": [
                        "Accept", "Accept-Language", "Authorization", "Content-Type",
                        "Content-Language", "X-Request-ID", "X-Correlation-ID",
                        "X-Tenant-ID", "X-API-Key", "X-User-ID",
                    ],
                    "expose_headers": [
                        "X-Request-ID", "X-Correlation-ID", "X-Total-Count", "X-Page-Count",
                        "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset",
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
