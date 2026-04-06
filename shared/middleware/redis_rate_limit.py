"""
SAHOOL Redis-backed Rate Limiter
==================================
محدد المعدل المدعوم بـ Redis للبيئات متعددة النسخ

Drop-in replacement for the in-memory RateLimiter that uses Redis
for distributed rate limiting across multiple service instances.

Implements the same dual algorithm (Token Bucket + Sliding Window)
as the in-memory version, preserving all tier, burst, and hourly
limit behavior — but with Redis as the shared state store.

Usage:
    from shared.middleware.redis_rate_limit import RedisRateLimiter
    from shared.middleware.rate_limit import TierConfig

    limiter = RedisRateLimiter(
        redis_url="redis://redis:6379",
        tier_config=TierConfig(),
        key_prefix="sahool:rl",
    )

    # Use in setup_rate_limiting
    from shared.middleware.rate_limiter import setup_rate_limiting
    setup_rate_limiting(app, limiter=limiter)
"""

from __future__ import annotations

import logging
import time

from fastapi import Request

from .rate_limit import RateLimiter, TierConfig

logger = logging.getLogger(__name__)

# Lazy import redis
_redis_available = False
try:
    import redis.asyncio as aioredis

    _redis_available = True
except ImportError:
    aioredis = None


# Lua script for atomic sliding window check + record
# This runs atomically in Redis, preventing race conditions
_SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

-- Remove expired entries
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

-- Count current entries
local count = redis.call('ZCARD', key)

if count >= limit then
    return {0, count}
end

-- Add new entry
redis.call('ZADD', key, now, now .. ':' .. math.random(1000000))

-- Set TTL to window + buffer
redis.call('EXPIRE', key, math.ceil(window) + 10)

return {1, count + 1}
"""

# Lua script for atomic token bucket
_TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local refill_rate = tonumber(ARGV[3])

-- Get current state
local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(data[1]) or capacity
local last_refill = tonumber(data[2]) or now

-- Refill tokens
local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * refill_rate)

-- Try to consume
if tokens < 1 then
    return 0
end

tokens = tokens - 1
redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
redis.call('EXPIRE', key, 120)

return 1
"""


class RedisRateLimiter(RateLimiter):
    """
    Redis-backed rate limiter with sliding window + token bucket.

    Extends the base RateLimiter to use Redis for distributed state,
    while preserving the same tier system, algorithms, and API.

    All Redis operations use Lua scripts for atomicity, preventing
    race conditions in multi-instance deployments.

    Args:
        redis_url: Redis connection URL
        tier_config: Rate limit tier configuration
        key_prefix: Redis key prefix for namespacing
        socket_timeout: Redis socket timeout in seconds
    """

    def __init__(
        self,
        redis_url: str = "redis://redis:6379",
        tier_config: TierConfig | None = None,
        key_prefix: str = "sahool:rl",
        socket_timeout: float = 2.0,
    ):
        if not _redis_available:
            raise RuntimeError(
                "redis[async] package is required for RedisRateLimiter. Install with: pip install redis[hiredis]"
            )

        super().__init__(tier_config=tier_config)
        self._redis_url = redis_url
        self._key_prefix = key_prefix
        self._socket_timeout = socket_timeout
        self._redis: aioredis.Redis | None = None
        self._sliding_window_sha: str | None = None
        self._token_bucket_sha: str | None = None
        self._fallback_active = False

    async def _get_redis(self) -> aioredis.Redis:
        """Lazy-initialize Redis connection."""
        if self._redis is None:
            self._redis = aioredis.from_url(
                self._redis_url,
                socket_connect_timeout=self._socket_timeout,
                socket_timeout=self._socket_timeout,
                decode_responses=False,
            )
            # Pre-load Lua scripts for performance
            self._sliding_window_sha = await self._redis.script_load(_SLIDING_WINDOW_LUA)
            self._token_bucket_sha = await self._redis.script_load(_TOKEN_BUCKET_LUA)
        return self._redis

    async def check_rate_limit(self, request: Request) -> tuple[bool, dict]:
        """
        Check rate limits using Redis (distributed).

        Falls back to in-memory rate limiting if Redis is unavailable,
        ensuring the service continues to work (degraded) rather than
        failing open with no rate limiting.
        """
        try:
            r = await self._get_redis()
            if self._fallback_active:
                logger.info("redis_rate_limit_recovered")
                self._fallback_active = False
            return await self._check_redis(request, r)
        except Exception as e:
            if not self._fallback_active:
                logger.warning(
                    "redis_rate_limit_fallback",
                    extra={"error": str(e), "fallback": "in_memory"},
                )
                self._fallback_active = True
            # Close existing connection (best-effort) then reset state
            # so we can reconnect when Redis recovers
            if self._redis:
                try:
                    await self._redis.close()
                except Exception:
                    pass  # Already broken, just discard
            self._redis = None
            self._sliding_window_sha = None
            self._token_bucket_sha = None
            # Fall back to parent in-memory implementation
            return await super().check_rate_limit(request)

    async def _check_redis(self, request: Request, r: aioredis.Redis) -> tuple[bool, dict]:
        """Execute rate limit checks against Redis."""
        # Get client identifier (same logic as parent)
        client_ip = request.client.host if request.client else "unknown"
        tenant_id = "default"
        if hasattr(request.state, "user") and request.state.user:
            tenant_id = getattr(request.state.user, "tenant_id", None) or "default"
        key = f"{tenant_id}:{client_ip}"

        # Honor per-request config override (set by tier_func in setup_rate_limiting)
        config_override = getattr(getattr(request, "state", None), "rate_limit_config_override", None)
        if config_override and getattr(getattr(request, "state", None), "is_service_request", False):
            tier = "override"
            config = config_override
        else:
            tier = self._get_tier(request)
            config = self._get_config(tier)

        now = time.time()

        # 1. Check per-minute sliding window
        minute_key = f"{self._key_prefix}:min:{key}"
        allowed_min, count_min = await r.evalsha(
            self._sliding_window_sha,
            1,
            minute_key,
            str(now),
            "60",
            str(config.requests_per_minute),
        )
        if not int(allowed_min):
            remaining = 0
            return False, self._build_headers(key, config, tier, exceeded=True, remaining=remaining)

        # 2. Check hourly sliding window
        hour_key = f"{self._key_prefix}:hr:{key}"
        allowed_hr, count_hr = await r.evalsha(
            self._sliding_window_sha,
            1,
            hour_key,
            str(now),
            "3600",
            str(config.requests_per_hour),
        )
        if not int(allowed_hr):
            remaining = 0
            return False, self._build_headers(key, config, tier, exceeded=True, remaining=remaining)

        # 3. Check token bucket (burst)
        bucket_key = f"{self._key_prefix}:tb:{key}"
        allowed_burst = await r.evalsha(
            self._token_bucket_sha,
            1,
            bucket_key,
            str(now),
            str(config.burst_limit),
            str(config.requests_per_minute / 60.0),
        )
        if not int(allowed_burst):
            remaining = 0
            return False, self._build_headers(key, config, tier, exceeded=True, remaining=remaining)

        remaining = max(0, config.requests_per_minute - int(count_min))
        return True, self._build_headers(key, config, tier, exceeded=False, remaining=remaining)

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
