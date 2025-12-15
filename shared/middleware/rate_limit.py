"""
SAHOOL Rate Limiting Middleware
Provides tiered rate limiting for API endpoints
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional
from functools import wraps

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse


@dataclass
class RateLimitConfig:
    """Rate limit configuration for different tiers"""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10  # Max requests in 1 second


@dataclass
class TierConfig:
    """Tiered rate limiting configuration"""

    free: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(
            requests_per_minute=30, requests_per_hour=500, burst_limit=5
        )
    )
    standard: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(
            requests_per_minute=60, requests_per_hour=2000, burst_limit=10
        )
    )
    premium: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(
            requests_per_minute=120, requests_per_hour=5000, burst_limit=20
        )
    )
    internal: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(
            requests_per_minute=1000, requests_per_hour=50000, burst_limit=100
        )
    )


class TokenBucket:
    """Token bucket algorithm for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens, returns True if successful"""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now


class RateLimiter:
    """Rate limiter with sliding window and token bucket"""

    def __init__(self, tier_config: Optional[TierConfig] = None):
        self.tier_config = tier_config or TierConfig()
        self._buckets: dict[str, TokenBucket] = {}
        self._request_counts: dict[str, list[float]] = defaultdict(list)

    def _get_bucket(self, key: str, config: RateLimitConfig) -> TokenBucket:
        """Get or create token bucket for a key"""
        if key not in self._buckets:
            # Refill rate = requests_per_minute / 60 seconds
            self._buckets[key] = TokenBucket(
                capacity=config.burst_limit,
                refill_rate=config.requests_per_minute / 60.0,
            )
        return self._buckets[key]

    def _clean_old_requests(self, key: str, window_seconds: int):
        """Remove requests older than the window"""
        cutoff = time.time() - window_seconds
        self._request_counts[key] = [t for t in self._request_counts[key] if t > cutoff]

    def _get_tier(self, request: Request) -> str:
        """Get rate limit tier from request headers or default"""
        # Check for internal service calls
        if request.headers.get("X-Internal-Service"):
            return "internal"

        # Check for API key tier
        tier = request.headers.get("X-Rate-Limit-Tier", "free").lower()
        if tier not in ["free", "standard", "premium", "internal"]:
            tier = "free"

        return tier

    def _get_config(self, tier: str) -> RateLimitConfig:
        """Get rate limit config for tier"""
        return getattr(self.tier_config, tier, self.tier_config.free)

    def check_rate_limit(self, request: Request) -> tuple[bool, dict]:
        """
        Check if request is within rate limits
        Returns (allowed, headers_dict)
        """
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        tenant_id = request.headers.get("X-Tenant-ID", "default")
        key = f"{tenant_id}:{client_ip}"

        tier = self._get_tier(request)
        config = self._get_config(tier)

        # Check token bucket (burst protection)
        bucket = self._get_bucket(key, config)
        if not bucket.consume():
            return False, self._build_headers(key, config, tier, exceeded=True)

        # Check sliding window (per-minute)
        self._clean_old_requests(key, 60)
        if len(self._request_counts[key]) >= config.requests_per_minute:
            return False, self._build_headers(key, config, tier, exceeded=True)

        # Check hourly limit
        hourly_key = f"{key}:hourly"
        self._clean_old_requests(hourly_key, 3600)
        if len(self._request_counts[hourly_key]) >= config.requests_per_hour:
            return False, self._build_headers(key, config, tier, exceeded=True)

        # Record this request
        now = time.time()
        self._request_counts[key].append(now)
        self._request_counts[hourly_key].append(now)

        return True, self._build_headers(key, config, tier, exceeded=False)

    def _build_headers(
        self, key: str, config: RateLimitConfig, tier: str, exceeded: bool
    ) -> dict:
        """Build rate limit response headers"""
        remaining = max(
            0, config.requests_per_minute - len(self._request_counts.get(key, []))
        )

        headers = {
            "X-RateLimit-Limit": str(config.requests_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time()) + 60),
            "X-RateLimit-Tier": tier,
        }

        if exceeded:
            headers["Retry-After"] = "60"

        return headers


# Global rate limiter instance
_rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """FastAPI middleware for rate limiting"""

    # Skip rate limiting for health checks
    if request.url.path in ["/healthz", "/readyz", "/metrics"]:
        return await call_next(request)

    allowed, headers = _rate_limiter.check_rate_limit(request)

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

    # Add rate limit headers to response
    for key, value in headers.items():
        response.headers[key] = value

    return response


def rate_limit(
    requests_per_minute: int = 60, requests_per_hour: int = 1000, burst_limit: int = 10
):
    """
    Decorator for endpoint-specific rate limiting

    Usage:
        @app.get("/expensive-endpoint")
        @rate_limit(requests_per_minute=10)
        async def expensive_endpoint():
            ...
    """
    config = RateLimitConfig(
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour,
        burst_limit=burst_limit,
    )

    limiter = RateLimiter()
    limiter.tier_config = TierConfig(
        free=config, standard=config, premium=config, internal=config
    )

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            allowed, headers = limiter.check_rate_limit(request)

            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "error_ar": "تم تجاوز حد الطلبات",
                    },
                    headers=headers,
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
