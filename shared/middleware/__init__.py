"""
SAHOOL Middleware Package
مجموعة middleware لمنصة سهول

Available middlewares:
- CORS: Secure cross-origin configuration
- Rate Limiting: Tiered API rate limiting
- Request Size: Payload size validation
- Tenant Context: Multi-tenancy isolation
- Request Logging: Structured JSON logging with correlation ID tracking
"""

from .cors import setup_cors, get_cors_origins, get_cors_config
from .rate_limit import (
    rate_limit_middleware,
    rate_limit,
    rate_limit_by_user,
    rate_limit_by_api_key,
    rate_limit_by_tenant,
    RateLimiter,
    RateLimitConfig,
    TierConfig,
    TokenBucket,
)
from .request_size import (
    request_size_middleware,
    configure_size_limits,
    RequestSizeLimiter,
)
from .tenant_context import TenantContextMiddleware
from .request_logging import (
    RequestLoggingMiddleware,
    get_correlation_id,
    get_request_context,
)

__all__ = [
    # CORS
    "setup_cors",
    "get_cors_origins",
    "get_cors_config",
    # Rate Limiting
    "rate_limit_middleware",
    "rate_limit",
    "rate_limit_by_user",
    "rate_limit_by_api_key",
    "rate_limit_by_tenant",
    "RateLimiter",
    "RateLimitConfig",
    "TierConfig",
    "TokenBucket",
    # Request Size
    "request_size_middleware",
    "configure_size_limits",
    "RequestSizeLimiter",
    # Tenant
    "TenantContextMiddleware",
    # Request Logging
    "RequestLoggingMiddleware",
    "get_correlation_id",
    "get_request_context",
]
