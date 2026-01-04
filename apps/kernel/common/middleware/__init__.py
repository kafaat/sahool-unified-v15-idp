"""
SAHOOL Kernel - Common Middleware Package
حزمة الميدلوير المشتركة

Provides common middleware components for SAHOOL services:
- Rate limiting with multiple strategies
- Request/response logging
- Error handling
- Authentication/Authorization

Version: 1.0.0
Created: 2026
"""

from .rate_limiter import (
    # الفئات الرئيسية - Main Classes
    RateLimiter,
    RateLimitMiddleware,
    ClientIdentifier,
    # استراتيجيات حد المعدل - Rate Limit Strategies
    RateLimitStrategy,
    FixedWindowLimiter,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    # التكوينات - Configurations
    EndpointConfig,
    ENDPOINT_CONFIGS,
    # دوال مساعدة - Helper Functions
    setup_rate_limiting,
    get_rate_limit_stats,
    rate_limit,
)

__all__ = [
    # Main Classes
    "RateLimiter",
    "RateLimitMiddleware",
    "ClientIdentifier",
    # Strategies
    "RateLimitStrategy",
    "FixedWindowLimiter",
    "SlidingWindowLimiter",
    "TokenBucketLimiter",
    # Configurations
    "EndpointConfig",
    "ENDPOINT_CONFIGS",
    # Helper Functions
    "setup_rate_limiting",
    "get_rate_limit_stats",
    "rate_limit",
]

__version__ = "1.0.0"
__author__ = "SAHOOL Development Team"
__description__ = (
    "Advanced rate limiting middleware with multiple strategies and Redis support"
)
