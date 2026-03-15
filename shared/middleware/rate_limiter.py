"""
SAHOOL Rate Limiter — High-level setup API
واجهة إعداد محدد المعدل لخدمات سهول

Provides RateLimitTier enum and setup_rate_limiting() used by services
to configure rate limiting as middleware.

Usage:
    from shared.middleware.rate_limiter import RateLimitTier, setup_rate_limiting

    setup_rate_limiting(app, use_redis=True, tier_func=my_tier_func)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from enum import StrEnum

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from .rate_limit import RateLimitConfig, RateLimiter, TierConfig

logger = logging.getLogger(__name__)


class RateLimitTier(StrEnum):
    """Rate limit tier levels matching platform subscription packages"""

    FREE = "free"
    STARTER = "starter"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    INTERNAL = "internal"
    RESEARCH = "research"


# Tier → RateLimitConfig mapping (requests_per_minute, requests_per_hour, burst)
_TIER_CONFIGS: dict[RateLimitTier, RateLimitConfig] = {
    RateLimitTier.FREE: RateLimitConfig(requests_per_minute=15, requests_per_hour=250, burst_limit=3),
    RateLimitTier.STARTER: RateLimitConfig(requests_per_minute=30, requests_per_hour=500, burst_limit=5),
    RateLimitTier.STANDARD: RateLimitConfig(requests_per_minute=60, requests_per_hour=2000, burst_limit=10),
    RateLimitTier.PROFESSIONAL: RateLimitConfig(requests_per_minute=60, requests_per_hour=2000, burst_limit=10),
    RateLimitTier.PREMIUM: RateLimitConfig(requests_per_minute=120, requests_per_hour=5000, burst_limit=20),
    RateLimitTier.ENTERPRISE: RateLimitConfig(requests_per_minute=120, requests_per_hour=5000, burst_limit=20),
    RateLimitTier.INTERNAL: RateLimitConfig(requests_per_minute=1000, requests_per_hour=50000, burst_limit=100),
    RateLimitTier.RESEARCH: RateLimitConfig(requests_per_minute=120, requests_per_hour=10000, burst_limit=20),
}


def setup_rate_limiting(
    app: FastAPI,
    *,
    use_redis: bool = False,
    tier_func: Callable[[Request], RateLimitTier] | None = None,
    exclude_paths: list[str] | None = None,
) -> RateLimiter:
    """
    Configure rate limiting middleware on a FastAPI application.

    Args:
        app: FastAPI application instance
        use_redis: Whether to use Redis for distributed rate limiting (future)
        tier_func: Optional callable to determine tier from request
        exclude_paths: Paths to exclude from rate limiting

    Returns:
        The configured RateLimiter instance
    """
    excluded = set(exclude_paths or ["/healthz", "/readyz", "/metrics", "/health"])

    limiter = RateLimiter(
        tier_config=TierConfig(
            free=_TIER_CONFIGS[RateLimitTier.FREE],
            standard=_TIER_CONFIGS[RateLimitTier.STANDARD],
            premium=_TIER_CONFIGS[RateLimitTier.PREMIUM],
            internal=_TIER_CONFIGS[RateLimitTier.INTERNAL],
        )
    )

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
        if request.url.path in excluded:
            return await call_next(request)

        # Determine tier and store on request.state for the limiter
        if tier_func:
            try:
                tier = tier_func(request)
                config = _TIER_CONFIGS.get(tier, _TIER_CONFIGS[RateLimitTier.FREE])
                # Store resolved config on request state to avoid mutating shared limiter
                request.state.rate_limit_config_override = config
            except Exception:
                pass  # Fall back to default tier detection

        allowed, headers = await limiter.check_rate_limit(request)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "error_ar": "تم تجاوز حد الطلبات",
                    "message": "Too many requests. Please try again later.",
                    "message_ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
                },
                headers=headers,
            )

        response = await call_next(request)
        for key, value in headers.items():
            response.headers[key] = value
        return response

    logger.info(
        "Rate limiting configured",
        extra={"use_redis": use_redis, "excluded_paths": list(excluded)},
    )

    return limiter
