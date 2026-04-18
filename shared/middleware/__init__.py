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
- Security Headers: Essential HTTP security headers
- Input Sanitization: XSS and injection attack prevention
"""

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
from .cors import DEFAULT_ORIGINS, get_cors_config, get_cors_origins, setup_cors
from .idempotency import IdempotencyMiddleware
from .input_sanitizer import (
    InputSanitizationMiddleware,
    sanitize_string,
    sanitize_value,
    setup_input_sanitization,
)
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
from .security_headers import (
    SecurityHeadersMiddleware,
    get_security_headers_config,
    setup_security_headers,
)
from .tenant_context import TenantContextMiddleware

__all__ = [
    # CORS
    "DEFAULT_ORIGINS",
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
    # Security Headers
    "setup_security_headers",
    "SecurityHeadersMiddleware",
    "get_security_headers_config",
    # Input Sanitization
    "InputSanitizationMiddleware",
    "setup_input_sanitization",
    "sanitize_string",
    "sanitize_value",
    # Idempotency
    "IdempotencyMiddleware",
]
