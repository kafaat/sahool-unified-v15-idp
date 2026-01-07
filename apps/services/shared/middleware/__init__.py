"""
SAHOOL Shared Middleware
ميدلوير مشترك لخدمات سهول

This module provides reusable middleware components for FastAPI services.
"""

from .cors import setup_cors
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
from .request_logging import RequestLoggingMiddleware
from .tenant_context import TenantContextMiddleware

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
    # Request Logging
    "RequestLoggingMiddleware",
    # Tenant Context
    "TenantContextMiddleware",
    # CORS
    "setup_cors",
]
