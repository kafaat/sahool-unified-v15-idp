"""
SAHOOL Shared Middleware
ميدلوير مشترك لخدمات سهول

This module provides reusable middleware components for FastAPI services.
"""

from .health import (
    HealthStatus,
    setup_health_endpoints,
)
from .rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    RateLimitTier,
    get_rate_limit_headers,
    setup_rate_limiting,
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
]
