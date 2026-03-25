"""
SAHOOL Advisory Service - Rate Limiting
========================================
Provides endpoint-specific rate limiting for advisory service.

Features:
- Token bucket algorithm for burst protection
- Different limits for different endpoint types
- Tenant-based rate limiting
- Bypass for internal service calls
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


@dataclass
class RateLimitTier:
    """Rate limit configuration for a tier."""

    requests_per_minute: int
    requests_per_hour: int
    burst_limit: int  # Max requests in 5 seconds


# Define tiers for different endpoint types
TIERS = {
    # Disease assessment - computationally intensive
    "disease_assess": RateLimitTier(
        requests_per_minute=30,
        requests_per_hour=500,
        burst_limit=5,
    ),
    # Symptom assessment - moderate
    "symptom_assess": RateLimitTier(
        requests_per_minute=60,
        requests_per_hour=1000,
        burst_limit=10,
    ),
    # Fertilizer planning - moderate
    "fertilizer_plan": RateLimitTier(
        requests_per_minute=60,
        requests_per_hour=1000,
        burst_limit=10,
    ),
    # NDVI assessment - resource intensive
    "ndvi_assess": RateLimitTier(
        requests_per_minute=20,
        requests_per_hour=300,
        burst_limit=3,
    ),
    # Lookup endpoints - fast, higher limits
    "lookup": RateLimitTier(
        requests_per_minute=120,
        requests_per_hour=3000,
        burst_limit=20,
    ),
    # Default tier
    "default": RateLimitTier(
        requests_per_minute=60,
        requests_per_hour=1000,
        burst_limit=10,
    ),
}


class AdvisoryRateLimiter:
    """
    Rate limiter with token bucket and sliding window algorithms.
    Tracks requests per client (tenant + IP).
    """

    def __init__(self):
        # Sliding window for per-minute tracking
        self._minute_windows: dict[str, list[float]] = defaultdict(list)
        # Sliding window for per-hour tracking
        self._hour_windows: dict[str, list[float]] = defaultdict(list)
        # Token bucket for burst protection (5-second window)
        self._burst_tokens: dict[str, tuple[int, float]] = {}

    def _get_client_key(self, request: Request, tier: str) -> str:
        """Get client identifier from request.

        SECURITY: Prefer tenant_id from verified JWT (request.state) over
        untrusted X-Tenant-ID header to prevent rate limit evasion.
        """
        # Try verified JWT context first (set by auth middleware)
        tenant_id = "default"
        if hasattr(request.state, "tenant_id") and request.state.tenant_id:
            tenant_id = request.state.tenant_id
        elif (
            hasattr(request.state, "user") and hasattr(request.state.user, "tenant_id") and request.state.user.tenant_id
        ):
            tenant_id = request.state.user.tenant_id
        else:
            # Fallback to header only for unauthenticated routes;
            # rate limit by IP will still apply
            tenant_id = request.headers.get("X-Tenant-ID", "default")
        client_ip = request.client.host if request.client else "unknown"
        return f"{tier}:{tenant_id}:{client_ip}"

    def _is_internal_request(self, request: Request) -> bool:
        """Check if request is from an internal service.

        SECURITY: Uses request.state.is_service_request set by
        ServiceAuthMiddleware (validated service token), not raw headers.
        """
        return getattr(request.state, "is_service_request", False)

    def _clean_window(self, window: list[float], max_age: float) -> list[float]:
        """Remove entries older than max_age seconds."""
        cutoff = time.time() - max_age
        return [t for t in window if t > cutoff]

    def _check_burst(self, key: str, tier: RateLimitTier) -> bool:
        """Check token bucket for burst protection."""
        now = time.time()
        bucket_window = 5.0  # 5 second window for burst

        if key not in self._burst_tokens:
            self._burst_tokens[key] = (tier.burst_limit - 1, now)
            return True

        tokens, last_update = self._burst_tokens[key]

        # Refill tokens based on elapsed time
        elapsed = now - last_update
        refill = int(elapsed / bucket_window * tier.burst_limit)
        tokens = min(tier.burst_limit, tokens + refill)

        if tokens > 0:
            self._burst_tokens[key] = (tokens - 1, now)
            return True

        return False

    def check(self, request: Request, tier: str = "default") -> tuple[bool, dict[str, str]]:
        """
        Check if request is within rate limits.

        Returns:
            (allowed, headers) - allowed is True if within limits, headers for response
        """
        # Bypass for internal service calls
        if self._is_internal_request(request):
            return True, {"X-RateLimit-Bypass": "internal"}

        tier_config = TIERS.get(tier, TIERS["default"])
        key = self._get_client_key(request, tier)
        now = time.time()

        # Check burst limit
        if not self._check_burst(key, tier_config):
            logger.warning(
                f"Burst limit exceeded for {key}",
                extra={"tier": tier, "limit": tier_config.burst_limit},
            )
            return False, self._build_headers(key, tier_config, exceeded=True)

        # Check per-minute limit
        self._minute_windows[key] = self._clean_window(self._minute_windows[key], 60)
        if len(self._minute_windows[key]) >= tier_config.requests_per_minute:
            logger.warning(
                f"Per-minute limit exceeded for {key}",
                extra={"tier": tier, "limit": tier_config.requests_per_minute},
            )
            return False, self._build_headers(key, tier_config, exceeded=True)

        # Check per-hour limit
        self._hour_windows[key] = self._clean_window(self._hour_windows[key], 3600)
        if len(self._hour_windows[key]) >= tier_config.requests_per_hour:
            logger.warning(
                f"Per-hour limit exceeded for {key}",
                extra={"tier": tier, "limit": tier_config.requests_per_hour},
            )
            return False, self._build_headers(key, tier_config, exceeded=True)

        # Record this request
        self._minute_windows[key].append(now)
        self._hour_windows[key].append(now)

        return True, self._build_headers(key, tier_config, exceeded=False)

    def _build_headers(
        self,
        key: str,
        tier: RateLimitTier,
        exceeded: bool,
    ) -> dict[str, str]:
        """Build rate limit response headers."""
        minute_remaining = max(
            0,
            tier.requests_per_minute - len(self._minute_windows.get(key, [])),
        )

        headers = {
            "X-RateLimit-Limit": str(tier.requests_per_minute),
            "X-RateLimit-Remaining": str(minute_remaining),
            "X-RateLimit-Reset": str(int(time.time()) + 60),
        }

        if exceeded:
            headers["Retry-After"] = "60"

        return headers


# Global rate limiter instance
_rate_limiter: AdvisoryRateLimiter | None = None


def get_rate_limiter() -> AdvisoryRateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = AdvisoryRateLimiter()
    return _rate_limiter


def rate_limit(tier: str = "default"):
    """
    Decorator for rate limiting endpoints.

    Usage:
        @app.post("/disease/assess")
        @rate_limit(tier="disease_assess")
        async def assess_disease(request: Request, ...):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Find request in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                request = kwargs.get("request")

            if request is None:
                # No request found, skip rate limiting
                logger.warning(f"No request found for rate limiting in {func.__name__}")
                return await func(*args, **kwargs)

            limiter = get_rate_limiter()
            allowed, headers = limiter.check(request, tier)

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "message_ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
                        "tier": tier,
                        "retry_after": 60,
                    },
                    headers=headers,
                )

            # Execute function
            result = await func(*args, **kwargs)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Find request in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                request = kwargs.get("request")

            if request is None:
                return func(*args, **kwargs)

            limiter = get_rate_limiter()
            allowed, headers = limiter.check(request, tier)

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "message_ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
                        "tier": tier,
                    },
                    headers=headers,
                )

            return func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
