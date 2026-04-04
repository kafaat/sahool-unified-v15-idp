"""
SAHOOL Advisory Service - Rate Limiting
========================================
Provides endpoint-specific rate limiting for advisory service.

Features:
- Token bucket algorithm for burst protection
- Different limits for different endpoint types
- Tenant-based rate limiting
- Bypass for internal service calls
- Redis-backed distributed rate limiting with in-memory fallback
"""

from __future__ import annotations

import logging
import os
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


class _RedisBackend:
    """Redis-backed sliding window rate limiter.

    Uses Redis sorted sets for accurate distributed rate limiting
    across multiple service instances.
    """

    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis = None
        self._initialized = False

    async def _ensure_connection(self) -> bool:
        if self._initialized:
            return self._redis is not None
        self._initialized = True
        try:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            await self._redis.ping()
            logger.info("advisory_rate_limiter_redis_connected")
            return True
        except ImportError:
            logger.warning("redis package not installed, falling back to in-memory")
            return False
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            self._redis = None
            return False

    async def check_window(self, key: str, window_seconds: int, limit: int) -> tuple[bool, int]:
        """Check sliding window. Returns (allowed, current_count)."""
        if not self._redis:
            raise RuntimeError("Redis not available")
        now = time.time()
        window_key = f"advisory:ratelimit:{key}:{window_seconds}"
        try:
            pipe = self._redis.pipeline()
            pipe.zremrangebyscore(window_key, 0, now - window_seconds)
            pipe.zcard(window_key)
            pipe.zadd(window_key, {str(now): now})
            pipe.expire(window_key, window_seconds * 2)
            results = await pipe.execute()
            current_count = results[1]
            if current_count >= limit:
                # Remove the request we just added
                await self._redis.zrem(window_key, str(now))
                return False, current_count
            return True, current_count + 1
        except Exception:
            raise

    async def check_burst(self, key: str, burst_limit: int, window: float = 5.0) -> bool:
        """Check burst via token bucket stored in Redis hash."""
        if not self._redis:
            raise RuntimeError("Redis not available")
        bucket_key = f"advisory:ratelimit:burst:{key}"
        now = time.time()
        try:
            data = await self._redis.hgetall(bucket_key)
            if not data:
                await self._redis.hset(bucket_key, mapping={"tokens": str(burst_limit - 1), "last_update": str(now)})
                await self._redis.expire(bucket_key, int(window * 4))
                return True

            tokens = float(data.get("tokens", "0"))
            last_update = float(data.get("last_update", str(now)))
            elapsed = now - last_update
            refill = int(elapsed / window * burst_limit)
            tokens = min(burst_limit, tokens + refill)

            if tokens > 0:
                await self._redis.hset(bucket_key, mapping={"tokens": str(tokens - 1), "last_update": str(now)})
                await self._redis.expire(bucket_key, int(window * 4))
                return True
            return False
        except Exception:
            raise


class AdvisoryRateLimiter:
    """
    Rate limiter with token bucket and sliding window algorithms.
    Tracks requests per client (tenant + IP).
    Supports Redis backend for distributed deployments with in-memory fallback.
    """

    def __init__(self, redis_url: str | None = None):
        # In-memory fallback storage
        self._minute_windows: dict[str, list[float]] = defaultdict(list)
        self._hour_windows: dict[str, list[float]] = defaultdict(list)
        self._burst_tokens: dict[str, tuple[int, float]] = {}

        # Redis backend (optional)
        url = redis_url or os.getenv("REDIS_URL")
        self._redis_backend: _RedisBackend | None = _RedisBackend(url) if url else None

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
            # Do NOT trust X-Tenant-ID header — an attacker can forge it to
            # distribute rate-limit counters across fake tenant IDs.
            # Use "anonymous" bucket; IP-based limiting still applies.
            tenant_id = "anonymous"
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
        """Check token bucket for burst protection (in-memory)."""
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

    async def check_async(self, request: Request, tier: str = "default") -> tuple[bool, dict[str, str]]:
        """Async check supporting Redis backend with in-memory fallback."""
        # Bypass for internal service calls
        if self._is_internal_request(request):
            return True, {"X-RateLimit-Bypass": "internal"}

        tier_config = TIERS.get(tier, TIERS["default"])
        key = self._get_client_key(request, tier)

        # Try Redis backend first
        if self._redis_backend:
            try:
                connected = await self._redis_backend._ensure_connection()
                if connected:
                    return await self._check_redis(key, tier_config)
            except Exception as e:
                logger.warning("redis_rate_limit_fallback", error=str(e))

        # Fall back to in-memory
        return self._check_in_memory(key, tier_config)

    async def _check_redis(self, key: str, tier_config: RateLimitTier) -> tuple[bool, dict[str, str]]:
        """Check rate limits using Redis backend."""
        assert self._redis_backend is not None

        # Check burst
        if not await self._redis_backend.check_burst(key, tier_config.burst_limit):
            logger.warning("burst_limit_exceeded_redis", key=key)
            return False, self._build_headers(key, tier_config, exceeded=True, source="redis")

        # Check per-minute
        allowed, count = await self._redis_backend.check_window(key, 60, tier_config.requests_per_minute)
        if not allowed:
            logger.warning("per_minute_limit_exceeded_redis", key=key)
            return False, self._build_headers(key, tier_config, exceeded=True, source="redis")

        # Check per-hour
        allowed, _ = await self._redis_backend.check_window(key, 3600, tier_config.requests_per_hour)
        if not allowed:
            logger.warning("per_hour_limit_exceeded_redis", key=key)
            return False, self._build_headers(key, tier_config, exceeded=True, source="redis")

        remaining = max(0, tier_config.requests_per_minute - count)
        return True, self._build_headers_remaining(tier_config, remaining, source="redis")

    def _check_in_memory(self, key: str, tier_config: RateLimitTier) -> tuple[bool, dict[str, str]]:
        """Check rate limits using in-memory storage."""
        now = time.time()

        # Check burst limit
        if not self._check_burst(key, tier_config):
            logger.warning(
                f"Burst limit exceeded for {key}",
                extra={"limit": tier_config.burst_limit},
            )
            return False, self._build_headers(key, tier_config, exceeded=True)

        # Check per-minute limit
        self._minute_windows[key] = self._clean_window(self._minute_windows[key], 60)
        if len(self._minute_windows[key]) >= tier_config.requests_per_minute:
            logger.warning(
                f"Per-minute limit exceeded for {key}",
                extra={"limit": tier_config.requests_per_minute},
            )
            return False, self._build_headers(key, tier_config, exceeded=True)

        # Check per-hour limit
        self._hour_windows[key] = self._clean_window(self._hour_windows[key], 3600)
        if len(self._hour_windows[key]) >= tier_config.requests_per_hour:
            logger.warning(
                f"Per-hour limit exceeded for {key}",
                extra={"limit": tier_config.requests_per_hour},
            )
            return False, self._build_headers(key, tier_config, exceeded=True)

        # Record this request
        self._minute_windows[key].append(now)
        self._hour_windows[key].append(now)

        return True, self._build_headers(key, tier_config, exceeded=False)

    def check(self, request: Request, tier: str = "default") -> tuple[bool, dict[str, str]]:
        """
        Synchronous check (in-memory only). Used by sync endpoints and tests.

        Returns:
            (allowed, headers) - allowed is True if within limits, headers for response
        """
        # Bypass for internal service calls
        if self._is_internal_request(request):
            return True, {"X-RateLimit-Bypass": "internal"}

        tier_config = TIERS.get(tier, TIERS["default"])
        key = self._get_client_key(request, tier)
        return self._check_in_memory(key, tier_config)

    def _build_headers(
        self,
        key: str,
        tier: RateLimitTier,
        exceeded: bool,
        source: str = "memory",
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

    def _build_headers_remaining(
        self,
        tier: RateLimitTier,
        remaining: int,
        source: str = "memory",
    ) -> dict[str, str]:
        """Build rate limit headers with known remaining count."""
        return {
            "X-RateLimit-Limit": str(tier.requests_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time()) + 60),
        }


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
            allowed, headers = await limiter.check_async(request, tier)

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
