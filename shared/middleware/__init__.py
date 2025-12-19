"""
SAHOOL Middleware Package
مجموعة middleware لمنصة سهول

Available middlewares:
- CORS: Secure cross-origin configuration
- Rate Limiting: Tiered API rate limiting
- Request Size: Payload size validation
- Tenant Context: Multi-tenancy isolation
"""

from .cors import setup_cors, get_cors_origins, get_cors_config
from .rate_limit import (
    rate_limit_middleware,
    rate_limit,
    RateLimiter,
    RateLimitConfig,
    TierConfig,
)
from .request_size import (
    request_size_middleware,
    configure_size_limits,
    RequestSizeLimiter,
)
from .tenant_context import TenantContextMiddleware

__all__ = [
    # CORS
    "setup_cors",
    "get_cors_origins",
    "get_cors_config",
    # Rate Limiting
    "rate_limit_middleware",
    "rate_limit",
    "RateLimiter",
    "RateLimitConfig",
    "TierConfig",
    # Request Size
    "request_size_middleware",
    "configure_size_limits",
    "RequestSizeLimiter",
    # Tenant
    "TenantContextMiddleware",
]
