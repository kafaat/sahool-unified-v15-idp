"""
SAHOOL CORS Configuration - Compatibility Shim
تكوين CORS - طبقة التوافق

This file provides backward compatibility for services importing from shared.cors_config
Real implementation is in shared/config/cors_config.py

Version: 1.0.0
"""

# Re-export from the actual config module
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
