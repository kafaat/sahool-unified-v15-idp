"""
SAHOOL Shared Library
=====================
مكتبة سهول المشتركة

Common utilities and modules for the SAHOOL agricultural platform.
This library provides:

- Authentication & Authorization (auth/)
- Caching with Redis Sentinel (cache/)
- Event-driven architecture with NATS (events/)
- AI/ML utilities and circuit breakers (ai/)
- Observability and logging (observability/)
- Unified exception handling (exceptions)

Author: SAHOOL Platform Team
Updated: January 2026
"""

__version__ = "16.0.0"

# Re-export common exceptions for convenience
from .exceptions import (
    AIServiceError,
    AuthenticationError,
    AuthorizationError,
    CacheError,
    ConflictError,
    DatabaseError,
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
    InferenceTimeoutError,
    MessagingError,
    ModelNotAvailableError,
    NotFoundError,
    RateLimitExceededError,
    SahoolBaseException,
    ServiceUnavailableError,
    ValidationError,
)

__all__ = [
    "__version__",
    # Base exceptions
    "SahoolBaseException",
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorContext",
    # Common exceptions
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ServiceUnavailableError",
    "DatabaseError",
    "CacheError",
    "MessagingError",
    "AIServiceError",
    "ModelNotAvailableError",
    "InferenceTimeoutError",
    "RateLimitExceededError",
    "ConflictError",
]
