"""
SAHOOL Shared CORS Configuration
إعدادات CORS المشتركة لجميع الخدمات

Usage:
    from shared.cors_config import get_cors_middleware, CORS_SETTINGS

    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
"""

import os
from typing import List

# Environment-based configuration
ENV = os.getenv("ENV", "development")
IS_PRODUCTION = ENV in ("production", "prod")

# Allowed origins based on environment
PRODUCTION_ORIGINS: List[str] = [
    "https://sahool.io",
    "https://www.sahool.io",
    "https://admin.sahool.io",
    "https://app.sahool.io",
    "https://api.sahool.io",
]

DEVELOPMENT_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://10.0.2.2:3000",  # Android emulator
]

# Custom origins from environment (comma-separated)
CUSTOM_ORIGINS_ENV = os.getenv("CORS_ALLOWED_ORIGINS", "")
CUSTOM_ORIGINS = [o.strip() for o in CUSTOM_ORIGINS_ENV.split(",") if o.strip()]


def get_allowed_origins() -> List[str]:
    """
    Get allowed origins based on environment
    الحصول على المصادر المسموح بها حسب البيئة
    """
    if IS_PRODUCTION:
        origins = PRODUCTION_ORIGINS.copy()
    else:
        origins = PRODUCTION_ORIGINS + DEVELOPMENT_ORIGINS

    # Add custom origins from environment
    if CUSTOM_ORIGINS:
        origins.extend(CUSTOM_ORIGINS)

    return list(set(origins))  # Remove duplicates


# CORS Settings for FastAPI
CORS_SETTINGS = {
    "allow_origins": get_allowed_origins(),
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": [
        "Authorization",
        "Content-Type",
        "Accept",
        "Accept-Language",
        "X-Tenant-Id",
        "X-Request-Id",
        "X-Correlation-Id",
        "If-Match",
        "If-None-Match",
    ],
    "expose_headers": [
        "X-Request-Id",
        "X-Correlation-Id",
        "ETag",
        "X-Total-Count",
        "X-Page",
        "X-Page-Size",
    ],
    "max_age": 600,  # Cache preflight for 10 minutes
}


def get_cors_middleware_config() -> dict:
    """
    Get CORS middleware configuration
    Use with: app.add_middleware(CORSMiddleware, **get_cors_middleware_config())
    """
    return CORS_SETTINGS.copy()
