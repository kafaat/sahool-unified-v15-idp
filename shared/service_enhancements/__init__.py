"""
SAHOOL Service Enhancements Module
===================================
Provides common patterns for Python backend services:
- Input validation with Pydantic
- Structured logging with context
- Response caching with Redis/in-memory fallback
- Database query optimization helpers
- API response formatting

Usage:
    from shared.service_enhancements import (
        setup_service,
        cache,
        validate_input,
        ServiceLogger,
        OptimizedQuery,
    )
"""

from .cache import (
    CacheConfig,
    CacheManager,
    cache,
    cache_response,
    get_cache_manager,
    invalidate_cache,
)
from .database import (
    DatabaseOptimizer,
    PaginatedQuery,
    QueryBuilder,
    batch_insert,
    with_retry,
)
from .logging_utils import (
    ServiceLogger,
    get_service_logger,
    log_operation,
    log_performance,
)
from .response import (
    ApiResponse,
    ErrorResponse,
    PaginatedResponse,
    SuccessResponse,
    create_response,
)
from .setup import (
    ServiceConfig,
    setup_service,
)
from .validation import (
    ValidatedModel,
    validate_arabic_text,
    validate_coordinates,
    validate_date_range,
    validate_field_id,
    validate_input,
    validate_phone,
    validate_uuid,
)

__all__ = [
    # Cache
    "CacheConfig",
    "CacheManager",
    "cache",
    "cache_response",
    "get_cache_manager",
    "invalidate_cache",
    # Database
    "DatabaseOptimizer",
    "PaginatedQuery",
    "QueryBuilder",
    "batch_insert",
    "with_retry",
    # Logging
    "ServiceLogger",
    "get_service_logger",
    "log_operation",
    "log_performance",
    # Response
    "ApiResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "SuccessResponse",
    "create_response",
    # Setup
    "ServiceConfig",
    "setup_service",
    # Validation
    "ValidatedModel",
    "validate_arabic_text",
    "validate_coordinates",
    "validate_date_range",
    "validate_field_id",
    "validate_input",
    "validate_phone",
    "validate_uuid",
]

__version__ = "1.0.0"
