"""
Caching Layer with TTL and Invalidation
طبقة التخزين المؤقت مع TTL والإبطال

Provides caching utilities with:
1. Redis-based caching
2. In-memory caching (fallback)
3. TTL (Time To Live) support
4. Cache invalidation strategies
5. Cache warming
"""

import os
import logging
import time
import json
import hashlib
from typing import Optional, Any, Callable, List
from dataclasses import dataclass
from functools import wraps
import asyncio

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Cache configuration"""

    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes default
    max_size: int = 10000
    redis_url: Optional[str] = None
    key_prefix: str = "sahool:"

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Create configuration from environment variables"""
        return cls(
            enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
            max_size=int(os.getenv("CACHE_MAX_SIZE", "10000")),
            redis_url=os.getenv("REDIS_URL"),
            key_prefix=os.getenv("CACHE_KEY_PREFIX", "sahool:"),
        )


class InMemoryCache:
    """
    Simple in-memory cache with TTL.
    ذاكرة تخزين مؤقت في الذاكرة بسيطة مع TTL.
    """

    def __init__(self, max_size: int = 10000):
        self._cache: dict = {}
        self._expiry: dict = {}
        self._max_size = max_size

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Check if key exists and not expired
        if key in self._cache:
            if key in self._expiry:
                if time.time() > self._expiry[key]:
                    # Expired, remove it
                    del self._cache[key]
                    del self._expiry[key]
                    return None
            return self._cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        # Check size limit
        if len(self._cache) >= self._max_size and key not in self._cache:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if oldest_key in self._expiry:
                del self._expiry[oldest_key]

        self._cache[key] = value

        if ttl is not None:
            self._expiry[key] = time.time() + ttl

    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]

    async def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        value = await self.get(key)
        return value is not None


class RedisCache:
    """
    Redis-based cache.
    ذاكرة تخزين مؤقت قائمة على Redis.
    """

    def __init__(self, redis_url: str):
        if not REDIS_AVAILABLE:
            raise ImportError("redis is required. Install with: pip install redis")

        self._redis: Optional[aioredis.Redis] = None
        self._redis_url = redis_url

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        if self._redis is None:
            self._redis = await aioredis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("Redis cache initialized")

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._redis:
            await self.initialize()

        value = await self._redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        if not self._redis:
            await self.initialize()

        # Serialize value
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, str):
            value = str(value)

        if ttl:
            await self._redis.setex(key, ttl, value)
        else:
            await self._redis.set(key, value)

    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        if not self._redis:
            await self.initialize()

        await self._redis.delete(key)

    async def clear(self, pattern: str = "*") -> None:
        """Clear cache by pattern"""
        if not self._redis:
            await self.initialize()

        keys = await self._redis.keys(pattern)
        if keys:
            await self._redis.delete(*keys)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._redis:
            await self.initialize()

        return await self._redis.exists(key) > 0


class CacheManager:
    """
    Unified cache manager with Redis and in-memory fallback.
    مدير التخزين المؤقت الموحد مع Redis والذاكرة الاحتياطية.
    """

    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache = None

        if not config.enabled:
            logger.info("Caching is disabled")
            return

        # Try to use Redis if available
        if config.redis_url and REDIS_AVAILABLE:
            try:
                self._cache = RedisCache(config.redis_url)
                logger.info("Using Redis cache")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Redis cache: {e}, falling back to in-memory"
                )
                self._cache = InMemoryCache(config.max_size)
        else:
            self._cache = InMemoryCache(config.max_size)
            logger.info("Using in-memory cache")

    def _make_key(self, key: str) -> str:
        """Add prefix to key"""
        return f"{self.config.key_prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        الحصول على قيمة من ذاكرة التخزين المؤقت.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.config.enabled or not self._cache:
            return None

        try:
            return await self._cache.get(self._make_key(key))
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """
        Set value in cache.
        تعيين قيمة في ذاكرة التخزين المؤقت.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = use default)
        """
        if not self.config.enabled or not self._cache:
            return

        try:
            ttl = ttl or self.config.ttl_seconds
            await self._cache.set(self._make_key(key), value, ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    async def delete(self, key: str) -> None:
        """
        Delete value from cache.
        حذف قيمة من ذاكرة التخزين المؤقت.

        Args:
            key: Cache key
        """
        if not self.config.enabled or not self._cache:
            return

        try:
            await self._cache.delete(self._make_key(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    async def clear(self, pattern: Optional[str] = None) -> None:
        """
        Clear cache by pattern.
        مسح ذاكرة التخزين المؤقت حسب النمط.

        Args:
            pattern: Key pattern (None = clear all)
        """
        if not self.config.enabled or not self._cache:
            return

        try:
            if pattern:
                await self._cache.clear(self._make_key(pattern))
            else:
                await self._cache.clear()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

    async def invalidate_pattern(self, pattern: str) -> None:
        """
        Invalidate all keys matching a pattern.
        إبطال جميع المفاتيح المطابقة لنمط.

        Args:
            pattern: Key pattern (e.g., "user:*", "field:123:*")
        """
        await self.clear(pattern)


# Global cache manager
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(config: Optional[CacheConfig] = None) -> CacheManager:
    """
    Get the global cache manager instance.
    الحصول على نسخة مدير التخزين المؤقت العامة.

    Args:
        config: Optional configuration (used on first call)

    Returns:
        CacheManager instance
    """
    global _cache_manager

    if _cache_manager is None:
        if config is None:
            config = CacheConfig.from_env()
        _cache_manager = CacheManager(config)

    return _cache_manager


# Caching decorator
def cached(
    key_func: Optional[Callable[..., str]] = None,
    ttl: Optional[int] = None,
    key_prefix: str = "",
):
    """
    Decorator for caching function results.
    مزخرف لتخزين نتائج الدالة مؤقتًا.

    Args:
        key_func: Function to generate cache key from arguments
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key

    Example:
        @cached(key_func=lambda user_id: f"user:{user_id}", ttl=600)
        async def get_user(user_id: str):
            return await db.query(User).filter(User.id == user_id).first()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default key: function name + arguments hash
                args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
                args_hash = hashlib.md5(args_str.encode()).hexdigest()
                key = f"{func.__name__}:{args_hash}"

            # Add prefix
            if key_prefix:
                key = f"{key_prefix}:{key}"

            # Try to get from cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value

            # Execute function
            logger.debug(f"Cache miss: {key}")
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(key, result, ttl)

            return result

        return wrapper

    return decorator


# Invalidation helpers
async def invalidate_user_cache(user_id: str) -> None:
    """Invalidate all cache entries for a user"""
    cache = get_cache_manager()
    await cache.invalidate_pattern(f"user:{user_id}:*")


async def invalidate_field_cache(field_id: str) -> None:
    """Invalidate all cache entries for a field"""
    cache = get_cache_manager()
    await cache.invalidate_pattern(f"field:{field_id}:*")


async def invalidate_tenant_cache(tenant_id: str) -> None:
    """Invalidate all cache entries for a tenant"""
    cache = get_cache_manager()
    await cache.invalidate_pattern(f"tenant:{tenant_id}:*")
