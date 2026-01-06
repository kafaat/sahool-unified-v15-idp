"""
SAHOOL Middleware Package
مجموعة middleware لمنصة سهول

Available middlewares:
- CORS: Secure cross-origin configuration
- Rate Limiting: Tiered API rate limiting
- Request Size: Payload size validation
- Tenant Context: Multi-tenancy isolation
- Request Logging: Structured JSON logging with correlation ID tracking
- API Versioning: URL-based API versioning (/api/v1/, /api/v2/, etc.)
"""

from .cors import get_cors_config, get_cors_origins, setup_cors
from .rate_limit import (
    RateLimitConfig,
    RateLimiter,
    TierConfig,
    TokenBucket,
    rate_limit,
    rate_limit_by_api_key,
    rate_limit_by_tenant,
    rate_limit_by_user,
    rate_limit_middleware,
)
from .request_logging import (
    RequestLoggingMiddleware,
    get_correlation_id,
    get_request_context,
)
from .request_size import (
    RequestSizeLimiter,
    configure_size_limits,
    request_size_middleware,
)
from .tenant_context import TenantContextMiddleware
from .api_versioning import (
    APIVersion,
    APIVersionMiddleware,
    VersionedRouter,
    create_versioned_routers,
    get_api_version,
    get_version_info,
    require_version,
    version_router,
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
    # API Versioning
    "APIVersion",
    "APIVersionMiddleware",
    "VersionedRouter",
    "create_versioned_routers",
    "get_api_version",
    "get_version_info",
    "require_version",
    "version_router",
]
