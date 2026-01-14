"""
SAHOOL Shared Utilities
أدوات مشتركة لخدمات سهول

Provides:
- FallbackManager: Circuit breaker and fallback patterns
- Retry utilities with exponential backoff
- Utility functions for resilience
"""

from .fallback_manager import (
    CircuitBreaker,
    FallbackManager,
    circuit_breaker,
    get_fallback_manager,
    with_fallback,
)
from .retry import (
    RETRY_AGGRESSIVE,
    RETRY_DATABASE,
    RETRY_FAST,
    RETRY_HTTP,
    RETRY_STANDARD,
    RetryConfig,
    RetryContext,
    async_retry,
    calculate_delay,
    retry,
    sync_retry,
)

__all__ = [
    # Fallback
    "FallbackManager",
    "CircuitBreaker",
    "circuit_breaker",
    "with_fallback",
    "get_fallback_manager",
    # Retry
    "RetryConfig",
    "RetryContext",
    "async_retry",
    "sync_retry",
    "retry",
    "calculate_delay",
    "RETRY_FAST",
    "RETRY_STANDARD",
    "RETRY_AGGRESSIVE",
    "RETRY_DATABASE",
    "RETRY_HTTP",
]
