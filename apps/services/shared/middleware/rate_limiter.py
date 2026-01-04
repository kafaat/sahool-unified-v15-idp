"""
SAHOOL Services - Rate Limiting Middleware
ميدلوير التحكم في معدل الطلبات

Provides configurable rate limiting for FastAPI services with:
- Multiple rate limit tiers (free, standard, premium, internal)
- Redis-backed distributed rate limiting (optional)
- In-memory fallback for development
- Automatic header injection (X-RateLimit-*)

Version: 1.0.0
Created: 2024
"""

import logging
import os
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Rate Limit Tiers
# ═══════════════════════════════════════════════════════════════════════════════


class RateLimitTier(str, Enum):
    """Rate limit tiers for different user/service types."""

    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"
    INTERNAL = "internal"
    UNLIMITED = "unlimited"


@dataclass
class RateLimitConfig:
    """Configuration for a rate limit tier.

    Attributes:
        requests_per_minute: Maximum requests per minute
        requests_per_hour: Maximum requests per hour
        burst_limit: Maximum burst requests (short-term spike)
        enabled: Whether rate limiting is active
    """

    requests_per_minute: int = 60
    requests_per_hour: int = 2000
    burst_limit: int = 10
    enabled: bool = True


# Default configurations per tier (from .env.example)
DEFAULT_TIER_CONFIGS: dict[RateLimitTier, RateLimitConfig] = {
    RateLimitTier.FREE: RateLimitConfig(
        requests_per_minute=int(os.getenv("RATE_LIMIT_FREE_RPM", "30")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_FREE_RPH", "500")),
        burst_limit=int(os.getenv("RATE_LIMIT_FREE_BURST", "5")),
    ),
    RateLimitTier.STANDARD: RateLimitConfig(
        requests_per_minute=int(os.getenv("RATE_LIMIT_STANDARD_RPM", "60")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_STANDARD_RPH", "2000")),
        burst_limit=int(os.getenv("RATE_LIMIT_STANDARD_BURST", "10")),
    ),
    RateLimitTier.PREMIUM: RateLimitConfig(
        requests_per_minute=int(os.getenv("RATE_LIMIT_PREMIUM_RPM", "120")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_PREMIUM_RPH", "5000")),
        burst_limit=int(os.getenv("RATE_LIMIT_PREMIUM_BURST", "20")),
    ),
    RateLimitTier.INTERNAL: RateLimitConfig(
        requests_per_minute=int(os.getenv("RATE_LIMIT_INTERNAL_RPM", "1000")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_INTERNAL_RPH", "50000")),
        burst_limit=int(os.getenv("RATE_LIMIT_INTERNAL_BURST", "100")),
    ),
    RateLimitTier.UNLIMITED: RateLimitConfig(
        requests_per_minute=0,
        requests_per_hour=0,
        burst_limit=0,
        enabled=False,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Rate Limiter (Development/Fallback)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class RateLimitState:
    """State for a single rate limit window."""

    requests: int = 0
    window_start: float = field(default_factory=time.time)


class InMemoryRateLimiter:
    """Simple in-memory rate limiter using sliding window algorithm.

    Note: This is suitable for single-instance deployments.
    For distributed deployments, use RedisRateLimiter.
    """

    def __init__(self):
        self._minute_windows: dict[str, RateLimitState] = defaultdict(RateLimitState)
        self._hour_windows: dict[str, RateLimitState] = defaultdict(RateLimitState)
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes

    def _cleanup_old_entries(self):
        """Remove expired entries to prevent memory leaks."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        # Cleanup minute windows older than 2 minutes
        expired_minute = [
            k for k, v in self._minute_windows.items() if now - v.window_start > 120
        ]
        for key in expired_minute:
            del self._minute_windows[key]

        # Cleanup hour windows older than 2 hours
        expired_hour = [
            k for k, v in self._hour_windows.items() if now - v.window_start > 7200
        ]
        for key in expired_hour:
            del self._hour_windows[key]

        self._last_cleanup = now

    def check_rate_limit(
        self, key: str, config: RateLimitConfig
    ) -> tuple[bool, int, int, int]:
        """Check if request is within rate limits.

        Args:
            key: Unique identifier for the client (e.g., IP, user_id)
            config: Rate limit configuration

        Returns:
            Tuple of (allowed, remaining, limit, reset_time)
        """
        if not config.enabled:
            return True, -1, -1, 0

        self._cleanup_old_entries()
        now = time.time()

        # Check minute window
        minute_state = self._minute_windows[f"{key}:minute"]
        if now - minute_state.window_start >= 60:
            minute_state.requests = 0
            minute_state.window_start = now

        # Check hour window
        hour_state = self._hour_windows[f"{key}:hour"]
        if now - hour_state.window_start >= 3600:
            hour_state.requests = 0
            hour_state.window_start = now

        # Check limits
        minute_remaining = config.requests_per_minute - minute_state.requests
        hour_remaining = config.requests_per_hour - hour_state.requests

        if minute_remaining <= 0:
            reset_time = int(minute_state.window_start + 60 - now)
            return False, 0, config.requests_per_minute, reset_time

        if hour_remaining <= 0:
            reset_time = int(hour_state.window_start + 3600 - now)
            return False, 0, config.requests_per_hour, reset_time

        # Increment counters
        minute_state.requests += 1
        hour_state.requests += 1

        # Return the more restrictive remaining count
        remaining = min(minute_remaining - 1, hour_remaining - 1)
        reset_time = int(60 - (now - minute_state.window_start))

        return True, remaining, config.requests_per_minute, reset_time


# ═══════════════════════════════════════════════════════════════════════════════
# Redis Rate Limiter (Distributed)
# ═══════════════════════════════════════════════════════════════════════════════


class RedisRateLimiter:
    """Redis-backed rate limiter for distributed deployments.

    Uses Redis sorted sets with sliding window algorithm for accurate
    rate limiting across multiple service instances.
    """

    def __init__(self, redis_url: str | None = None):
        self._redis_url = redis_url or os.getenv("REDIS_URL")
        self._redis = None
        self._initialized = False

    async def _ensure_connection(self):
        """Lazily initialize Redis connection."""
        if self._initialized:
            return

        if not self._redis_url:
            logger.warning("Redis URL not configured, rate limiting disabled")
            return

        try:
            import redis.asyncio as redis

            self._redis = redis.from_url(self._redis_url, decode_responses=True)
            await self._redis.ping()
            self._initialized = True
            logger.info("Redis rate limiter connected successfully")
        except ImportError:
            logger.warning("redis package not installed, falling back to in-memory")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, falling back to in-memory")

    async def check_rate_limit(
        self, key: str, config: RateLimitConfig
    ) -> tuple[bool, int, int, int]:
        """Check if request is within rate limits using Redis.

        Args:
            key: Unique identifier for the client
            config: Rate limit configuration

        Returns:
            Tuple of (allowed, remaining, limit, reset_time)
        """
        if not config.enabled:
            return True, -1, -1, 0

        await self._ensure_connection()

        if not self._redis:
            # Fallback to allowing requests if Redis unavailable
            return True, config.requests_per_minute, config.requests_per_minute, 60

        now = time.time()
        minute_key = f"ratelimit:{key}:minute"

        try:
            pipe = self._redis.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(minute_key, 0, now - 60)

            # Count current requests in window
            pipe.zcard(minute_key)

            # Add current request
            pipe.zadd(minute_key, {str(now): now})

            # Set expiry
            pipe.expire(minute_key, 120)

            results = await pipe.execute()
            current_requests = results[1]

            remaining = config.requests_per_minute - current_requests - 1

            if remaining < 0:
                # Remove the request we just added
                await self._redis.zrem(minute_key, str(now))
                return False, 0, config.requests_per_minute, 60

            return True, remaining, config.requests_per_minute, 60

        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fail open - allow request if Redis errors
            return True, config.requests_per_minute, config.requests_per_minute, 60


# ═══════════════════════════════════════════════════════════════════════════════
# Rate Limiter Facade
# ═══════════════════════════════════════════════════════════════════════════════


class RateLimiter:
    """Unified rate limiter that uses Redis when available, else in-memory.

    Usage:
        limiter = RateLimiter()

        # Check rate limit
        allowed, remaining, limit, reset = await limiter.check(
            key="user:123",
            tier=RateLimitTier.STANDARD
        )
    """

    def __init__(
        self,
        use_redis: bool = True,
        redis_url: str | None = None,
        tier_configs: dict[RateLimitTier, RateLimitConfig] | None = None,
    ):
        self._tier_configs = tier_configs or DEFAULT_TIER_CONFIGS
        self._in_memory = InMemoryRateLimiter()
        self._redis: RedisRateLimiter | None = None

        if use_redis:
            self._redis = RedisRateLimiter(redis_url)

    def get_config(self, tier: RateLimitTier) -> RateLimitConfig:
        """Get rate limit configuration for a tier."""
        return self._tier_configs.get(tier, self._tier_configs[RateLimitTier.STANDARD])

    async def check(
        self, key: str, tier: RateLimitTier = RateLimitTier.STANDARD
    ) -> tuple[bool, int, int, int]:
        """Check rate limit for a key.

        Args:
            key: Unique client identifier
            tier: Rate limit tier to apply

        Returns:
            Tuple of (allowed, remaining, limit, reset_seconds)
        """
        config = self.get_config(tier)

        if self._redis:
            try:
                return await self._redis.check_rate_limit(key, config)
            except Exception:
                pass

        return self._in_memory.check_rate_limit(key, config)


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Middleware
# ═══════════════════════════════════════════════════════════════════════════════


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic rate limiting."""

    def __init__(
        self,
        app,
        limiter: RateLimiter,
        key_func: Callable[[Request], str] | None = None,
        tier_func: Callable[[Request], RateLimitTier] | None = None,
        exclude_paths: list | None = None,
    ):
        super().__init__(app)
        self.limiter = limiter
        self.key_func = key_func or self._default_key_func
        self.tier_func = tier_func or self._default_tier_func
        self.exclude_paths = exclude_paths or [
            "/healthz",
            "/readyz",
            "/livez",
            "/metrics",
        ]

    def _default_key_func(self, request: Request) -> str:
        """Default: Use client IP as rate limit key."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _default_tier_func(self, request: Request) -> RateLimitTier:
        """Default: Determine tier from request headers or auth."""
        # Check for internal service header
        if request.headers.get("X-Internal-Service"):
            return RateLimitTier.INTERNAL

        # Check for API key tier header
        tier_header = request.headers.get("X-Rate-Limit-Tier", "").lower()
        if tier_header in [t.value for t in RateLimitTier]:
            return RateLimitTier(tier_header)

        return RateLimitTier.STANDARD

    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiter."""
        # Skip excluded paths
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        # Get rate limit key and tier
        key = self.key_func(request)
        tier = self.tier_func(request)

        # Check rate limit
        allowed, remaining, limit, reset = await self.limiter.check(key, tier)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please slow down.",
                    "retry_after": reset,
                },
                headers=get_rate_limit_headers(remaining, limit, reset),
            )

        # Process request and add rate limit headers to response
        response = await call_next(request)

        # Add rate limit headers
        for header, value in get_rate_limit_headers(remaining, limit, reset).items():
            response.headers[header] = value

        return response


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════


def get_rate_limit_headers(remaining: int, limit: int, reset: int) -> dict[str, str]:
    """Generate rate limit headers for HTTP response."""
    if limit < 0:
        return {}

    return {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(max(0, remaining)),
        "X-RateLimit-Reset": str(reset),
    }


def setup_rate_limiting(
    app: FastAPI,
    use_redis: bool = True,
    redis_url: str | None = None,
    key_func: Callable[[Request], str] | None = None,
    tier_func: Callable[[Request], RateLimitTier] | None = None,
    exclude_paths: list | None = None,
) -> RateLimiter:
    """Set up rate limiting middleware for a FastAPI application.

    Args:
        app: FastAPI application instance
        use_redis: Whether to use Redis for distributed rate limiting
        redis_url: Redis connection URL (defaults to REDIS_URL env var)
        key_func: Custom function to extract rate limit key from request
        tier_func: Custom function to determine rate limit tier from request
        exclude_paths: Paths to exclude from rate limiting

    Returns:
        RateLimiter instance for manual checks if needed

    Usage:
        from apps.services.shared.middleware import setup_rate_limiting

        app = FastAPI()
        limiter = setup_rate_limiting(app)
    """
    limiter = RateLimiter(use_redis=use_redis, redis_url=redis_url)

    app.add_middleware(
        RateLimitMiddleware,
        limiter=limiter,
        key_func=key_func,
        tier_func=tier_func,
        exclude_paths=exclude_paths,
    )

    logger.info(f"Rate limiting configured: redis={use_redis}")

    return limiter
