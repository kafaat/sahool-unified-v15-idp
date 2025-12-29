"""
SAHOOL Shared Middleware
ميدلوير مشترك لخدمات سهول

This module provides reusable middleware components for FastAPI services.
"""

from .rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitTier,
    setup_rate_limiting,
    get_rate_limit_headers,
)
from .health import (
    setup_health_endpoints,
    HealthStatus,
)
from .csrf import (
    CSRFConfig,
    CSRFProtection,
    get_csrf_token,
)

__all__ = [
    # Rate Limiting
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitTier",
    "setup_rate_limiting",
    "get_rate_limit_headers",
    # Health Checks
    "setup_health_endpoints",
    "HealthStatus",
    # CSRF Protection
    "CSRFConfig",
    "CSRFProtection",
    "get_csrf_token",
]
