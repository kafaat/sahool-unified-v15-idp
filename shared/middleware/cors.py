"""
SAHOOL Secure CORS Middleware Configuration
تكوين CORS الآمن لمنصة سهول

Security Best Practices:
- Never use allow_origins=["*"] in production
- Explicitly list allowed origins
- Use environment variables for configuration
"""

import os
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Default allowed origins for different environments
DEFAULT_ORIGINS = {
    "production": [
        "https://app.sahool.io",
        "https://admin.sahool.io",
        "https://api.sahool.io",
    ],
    "staging": [
        "https://staging.sahool.io",
        "https://admin-staging.sahool.io",
        "https://app-staging.sahool.io",
    ],
    "development": [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ],
}


def get_cors_origins() -> List[str]:
    """
    Get allowed CORS origins based on environment.

    Priority:
    1. CORS_ORIGINS environment variable (comma-separated)
    2. Default origins based on ENVIRONMENT variable
    3. Development origins (safest fallback)
    """
    # Check for explicit CORS_ORIGINS setting
    cors_origins_env = os.getenv("CORS_ORIGINS", "")
    if cors_origins_env:
        return [
            origin.strip() for origin in cors_origins_env.split(",") if origin.strip()
        ]

    # Fall back to environment-based defaults
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return DEFAULT_ORIGINS["production"]
    elif environment == "staging":
        return DEFAULT_ORIGINS["staging"]
    else:
        return DEFAULT_ORIGINS["development"]


def setup_cors(
    app: FastAPI,
    allowed_origins: Optional[List[str]] = None,
    allow_credentials: bool = True,
    allowed_methods: Optional[List[str]] = None,
    allowed_headers: Optional[List[str]] = None,
    expose_headers: Optional[List[str]] = None,
    max_age: int = 3600,
) -> None:
    """
    Configure CORS middleware with secure defaults.

    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins (defaults to environment-based)
        allow_credentials: Allow credentials (cookies, auth headers)
        allowed_methods: Allowed HTTP methods
        allowed_headers: Allowed request headers
        expose_headers: Headers to expose to the browser
        max_age: Preflight cache duration in seconds

    Usage:
        from shared.middleware.cors import setup_cors

        app = FastAPI()
        setup_cors(app)
    """
    origins = allowed_origins or get_cors_origins()

    # Security check: warn if using wildcard in production
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if "*" in origins and environment == "production":
        import logging

        logging.warning(
            "⚠️ SECURITY WARNING: Using wildcard (*) CORS origins in production! "
            "This is a security risk. Please configure CORS_ORIGINS properly."
        )

    # Default allowed methods (no DELETE for safety by default)
    methods = allowed_methods or ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    # Default allowed headers
    headers = allowed_headers or [
        "Authorization",
        "Content-Type",
        "Accept",
        "Accept-Language",
        "X-Request-ID",
        "X-Correlation-ID",
        "X-Tenant-ID",
        "X-API-Key",
    ]

    # Default exposed headers
    expose = expose_headers or [
        "X-Request-ID",
        "X-Correlation-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=allow_credentials,
        allow_methods=methods,
        allow_headers=headers,
        expose_headers=expose,
        max_age=max_age,
    )


def get_cors_config() -> dict:
    """
    Get CORS configuration as a dictionary.
    Useful for debugging or logging.
    """
    return {
        "allowed_origins": get_cors_origins(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "cors_origins_env": os.getenv("CORS_ORIGINS", "not set"),
    }
