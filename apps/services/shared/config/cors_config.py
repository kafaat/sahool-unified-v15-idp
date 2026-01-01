"""
SAHOOL Services - Centralized CORS Configuration
تكوين CORS المركزي لخدمات سهول

Security Best Practices:
- Never use allow_origins=["*"] in production
- Explicitly list allowed origins
- Use environment variables for configuration
- Separate production and development origins

Version: 1.0.0
Created: 2024
"""

import os
import logging
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Production Origins Whitelist
# ═══════════════════════════════════════════════════════════════════════════════

PRODUCTION_ORIGINS = [
    "https://sahool.app",
    "https://admin.sahool.app",
    "https://api.sahool.app",
    "https://www.sahool.app",
]

# ═══════════════════════════════════════════════════════════════════════════════
# Development Origins Whitelist
# ═══════════════════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════════════════
# Staging Origins Whitelist
# ═══════════════════════════════════════════════════════════════════════════════

STAGING_ORIGINS = [
    "https://staging.sahool.app",
    "https://admin-staging.sahool.app",
    "https://api-staging.sahool.app",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Environment-Based Origin Selection
# ═══════════════════════════════════════════════════════════════════════════════


def get_allowed_origins() -> List[str]:
    """
    Get allowed CORS origins based on the current environment.

    Priority:
    1. CORS_ORIGINS environment variable (comma-separated list)
    2. Environment-specific defaults (ENVIRONMENT variable)
    3. Development origins (safest fallback)

    Returns:
        List[str]: List of allowed origin URLs

    Environment Variables:
        CORS_ORIGINS: Comma-separated list of allowed origins (highest priority)
        ENVIRONMENT: Environment name (production, staging, development)

    Examples:
        # Explicit origins
        CORS_ORIGINS="https://example.com,https://app.example.com"

        # Environment-based
        ENVIRONMENT=production  # Uses PRODUCTION_ORIGINS
        ENVIRONMENT=staging     # Uses STAGING_ORIGINS
        ENVIRONMENT=development # Uses DEVELOPMENT_ORIGINS

    Security:
        - Never returns ["*"] in production
        - Logs warning if wildcard detected in production
        - Falls back to development origins if configuration is invalid
    """
    # Priority 1: Explicit CORS_ORIGINS environment variable
    cors_origins_env = os.getenv("CORS_ORIGINS", "").strip()
    if cors_origins_env:
        # Remove wildcard in production for security
        origins = [
            origin.strip() for origin in cors_origins_env.split(",") if origin.strip()
        ]

        environment = os.getenv("ENVIRONMENT", "development").lower()
        if "*" in origins and environment == "production":
            logger.critical(
                "🚨 SECURITY ALERT: Wildcard (*) CORS origin detected in production! "
                "This is a critical security vulnerability. Falling back to PRODUCTION_ORIGINS."
            )
            return PRODUCTION_ORIGINS

        return origins

    # Priority 2: Environment-based defaults
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        logger.info(f"Using PRODUCTION_ORIGINS: {PRODUCTION_ORIGINS}")
        return PRODUCTION_ORIGINS
    elif environment == "staging":
        logger.info(f"Using STAGING_ORIGINS: {STAGING_ORIGINS}")
        return STAGING_ORIGINS
    else:
        logger.info(f"Using DEVELOPMENT_ORIGINS for environment: {environment}")
        return DEVELOPMENT_ORIGINS


# ═══════════════════════════════════════════════════════════════════════════════
# CORS Middleware Configuration
# ═══════════════════════════════════════════════════════════════════════════════


def setup_cors_middleware(
    app: FastAPI,
    allowed_origins: List[str] = None,
    allow_credentials: bool = True,
    allowed_methods: List[str] = None,
    allowed_headers: List[str] = None,
    expose_headers: List[str] = None,
    max_age: int = 3600,
) -> None:
    """
    Configure CORS middleware for a FastAPI application with secure defaults.

    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins (defaults to environment-based)
        allow_credentials: Allow credentials (cookies, authorization headers)
        allowed_methods: Allowed HTTP methods (defaults to common REST methods)
        allowed_headers: Allowed request headers (defaults to common headers)
        expose_headers: Headers to expose to the browser
        max_age: Preflight cache duration in seconds (default: 1 hour)

    Usage:
        from apps.services.shared.config.cors_config import setup_cors_middleware

        app = FastAPI(title="My Service")
        setup_cors_middleware(app)

    Security Features:
        - No wildcard origins in production
        - Explicit origin whitelisting
        - Credential support with proper origin validation
        - Security headers exposure control
        - Logging of CORS configuration

    Examples:
        # Use environment-based defaults
        setup_cors_middleware(app)

        # Custom origins
        setup_cors_middleware(
            app,
            allowed_origins=["https://custom.sahool.app"]
        )

        # Disable credentials
        setup_cors_middleware(
            app,
            allow_credentials=False
        )
    """
    # Get allowed origins
    origins = allowed_origins or get_allowed_origins()

    # Validate: No wildcard in production
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if "*" in origins and environment == "production":
        logger.critical(
            "🚨 CRITICAL SECURITY VIOLATION: Attempting to use wildcard CORS in production! "
            "This configuration has been blocked. Update CORS_ORIGINS or ENVIRONMENT variable."
        )
        origins = PRODUCTION_ORIGINS

    # Default allowed methods
    methods = allowed_methods or [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
        "HEAD",
    ]

    # Default allowed headers
    headers = allowed_headers or [
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
    ]

    # Default exposed headers
    expose = expose_headers or [
        "X-Request-ID",
        "X-Correlation-ID",
        "X-Total-Count",
        "X-Page-Count",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ]

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=methods,
        allow_headers=headers,
        expose_headers=expose,
        max_age=max_age,
    )

    # Log CORS configuration
    logger.info(
        f"CORS configured: environment={environment}, "
        f"origins={origins}, credentials={allow_credentials}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════════════


def get_cors_config() -> dict:
    """
    Get current CORS configuration as a dictionary.
    Useful for debugging, logging, or health checks.

    Returns:
        dict: CORS configuration details

    Example:
        {
            "environment": "production",
            "allowed_origins": ["https://sahool.app", ...],
            "cors_origins_env": "not set",
            "has_wildcard": false
        }
    """
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
    """
    Validate if an origin is in the allowed list.

    Args:
        origin: Origin URL to validate

    Returns:
        bool: True if origin is allowed, False otherwise

    Example:
        if validate_origin("https://sahool.app"):
            # Origin is allowed
            pass
    """
    allowed = get_allowed_origins()
    return origin in allowed or "*" in allowed
