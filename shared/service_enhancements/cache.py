"""
SAHOOL Caching Module
=====================
Provides flexible caching with Redis and in-memory fallback.

Features:
- Redis caching with automatic serialization
- In-memory LRU cache fallback
- TTL-based expiration
- Cache key prefixing by tenant
- Cache invalidation patterns
- Decorator-based caching for endpoints

Usage:
    from shared.service_enhancements.cache import (
        cache,
        cache_response,
        get_cache_manager,
        invalidate_cache,
    )

    # Decorator usage
    @cache(ttl=300, prefix="weather")
    async def get_weather_data(location_id: str):
        ...

    # Manual cache usage
    cache_manager = get_cache_manager()
    await cache_manager.set("key", data, ttl=300)
    data = await cache_manager.get("key")
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class CacheConfig:
    """Configuration for cache manager."""

    redis_url: str | None = None
    default_ttl: int = 300  # 5 minutes
    max_memory_items: int = 1000
    key_prefix: str = "sahool"
    serialize_method: str = "json"

    @classmethod
    def from_env(cls) -> CacheConfig:
        """Create config from environment variables."""
        return cls(
            redis_url=os.getenv("REDIS_URL"),
            default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", "300")),
            max_memory_items=int(os.getenv("CACHE_MAX_ITEMS", "1000")),
            key_prefix=os.getenv("CACHE_KEY_PREFIX", "sahool"),
            serialize_method="json",
        )


class InMemoryCache:
    """
    Thread-safe LRU cache with TTL support.
    Used as fallback when Redis is not available.
    """

    def __init__(self, max_items: int = 1000):
        self.max_items = max_items
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Get value from cache, returns None if expired or missing."""
        async with self._lock:
            if key not in self._cache:
                return None

            value, expires_at = self._cache[key]

            if time.time() > expires_at:
                del self._cache[key]
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            return value

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL."""
        async with self._lock:
            expires_at = time.time() + ttl

            # Evict oldest if at capacity
            while len(self._cache) >= self.max_items:
                self._cache.popitem(last=False)

            self._cache[key] = (value, expires_at)
            return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> int:
        """Clear all cache entries."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern (simple prefix match)."""
        async with self._lock:
            prefix = pattern.rstrip("*")
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)


class RedisCache:
    """Redis cache implementation with automatic connection handling."""

    def __init__(self, redis_url: str, serialize_method: str = "json"):  # noqa: ARG002
        self.redis_url = redis_url
        self._client = None
        self._connected = False

    async def _ensure_connection(self):
        """Ensure Redis connection is established."""
        if self._connected and self._client:
            return True

        try:
            import redis.asyncio as redis

            self._client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,
            )
            await self._client.ping()
            self._connected = True
            logger.info("Redis cache connected")
            return True
        except ImportError:
            logger.warning("redis package not installed, falling back to memory cache")
            return False
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self._connected = False
            return False

    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage using JSON."""
        return json.dumps(value, default=str).encode("utf-8")

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage using JSON."""
        return json.loads(data.decode("utf-8"))

    async def get(self, key: str) -> Any | None:
        """Get value from Redis cache."""
        if not await self._ensure_connection():
            return None

        try:
            data = await self._client.get(key)
            if data is None:
                return None
            return self._deserialize(data)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in Redis cache with TTL."""
        if not await self._ensure_connection():
            return False

        try:
            data = self._serialize(value)
            await self._client.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.warning(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        if not await self._ensure_connection():
            return False

        try:
            result = await self._client.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")
            return False

    async def clear(self) -> int:
        """Clear all cache entries (with prefix)."""
        if not await self._ensure_connection():
            return 0

        try:
            keys = await self._client.keys("*")
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis clear error: {e}")
            return 0

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern."""
        if not await self._ensure_connection():
            return 0

        try:
            keys = await self._client.keys(pattern)
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Redis delete_pattern error: {e}")
            return 0


class CacheManager:
    """
    Unified cache manager with Redis and in-memory fallback.
    Provides a consistent interface regardless of backend.
    """

    def __init__(self, config: CacheConfig | None = None):
        self.config = config or CacheConfig.from_env()
        self._memory_cache = InMemoryCache(self.config.max_memory_items)
        self._redis_cache: RedisCache | None = None

        if self.config.redis_url:
            self._redis_cache = RedisCache(
                self.config.redis_url,
                self.config.serialize_method,
            )

    def _build_key(self, key: str, prefix: str | None = None) -> str:
        """Build full cache key with prefix."""
        parts = [self.config.key_prefix]
        if prefix:
            parts.append(prefix)
        parts.append(key)
        return ":".join(parts)

    async def get(
        self,
        key: str,
        prefix: str | None = None,
    ) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key
            prefix: Optional key prefix

        Returns:
            Cached value or None
        """
        full_key = self._build_key(key, prefix)

        # Try Redis first
        if self._redis_cache:
            value = await self._redis_cache.get(full_key)
            if value is not None:
                return value

        # Fall back to memory cache
        return await self._memory_cache.get(full_key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        prefix: str | None = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default from config)
            prefix: Optional key prefix

        Returns:
            True if cached successfully
        """
        full_key = self._build_key(key, prefix)
        ttl = ttl or self.config.default_ttl

        # Try Redis first
        if self._redis_cache:
            success = await self._redis_cache.set(full_key, value, ttl)
            if success:
                return True

        # Fall back to memory cache
        return await self._memory_cache.set(full_key, value, ttl)

    async def delete(
        self,
        key: str,
        prefix: str | None = None,
    ) -> bool:
        """Delete key from cache."""
        full_key = self._build_key(key, prefix)

        redis_deleted = False
        if self._redis_cache:
            redis_deleted = await self._redis_cache.delete(full_key)

        memory_deleted = await self._memory_cache.delete(full_key)

        return redis_deleted or memory_deleted

    async def delete_pattern(
        self,
        pattern: str,
        prefix: str | None = None,
    ) -> int:
        """Delete keys matching pattern."""
        full_pattern = self._build_key(pattern, prefix)

        count = 0
        if self._redis_cache:
            count += await self._redis_cache.delete_pattern(full_pattern)

        count += await self._memory_cache.delete_pattern(full_pattern)

        return count

    async def clear(self) -> int:
        """Clear all cache entries."""
        count = 0
        if self._redis_cache:
            count += await self._redis_cache.clear()
        count += await self._memory_cache.clear()
        return count


# Global cache manager instance
_cache_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def _generate_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    # Create a string representation of arguments
    key_data = {
        "args": [str(arg) for arg in args],
        "kwargs": {k: str(v) for k, v in sorted(kwargs.items())},
    }

    # Hash for shorter keys
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()


def cache(
    ttl: int = 300,
    prefix: str | None = None,
    key_func: Callable[..., str] | None = None,
) -> Callable[[F], F]:
    """
    Decorator for caching function results.

    Args:
        ttl: Time-to-live in seconds
        prefix: Cache key prefix
        key_func: Custom function to generate cache key

    Usage:
        @cache(ttl=300, prefix="weather")
        async def get_weather(location_id: str):
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()

            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Exclude 'self' or 'cls' from key generation
                clean_args = args[1:] if args and hasattr(args[0], "__class__") else args
                cache_key = f"{func.__name__}:{_generate_cache_key(*clean_args, **kwargs)}"

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key, prefix=prefix)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)

            if result is not None:
                await cache_manager.set(cache_key, result, ttl=ttl, prefix=prefix)
                logger.debug(f"Cached result for {cache_key}")

            return result

        return wrapper

    return decorator


def cache_response(
    ttl: int = 300,
    prefix: str = "response",
    vary_on: list[str] | None = None,
) -> Callable[[F], F]:
    """
    Decorator for caching API responses.
    Varies cache key based on query parameters and headers.

    Args:
        ttl: Time-to-live in seconds
        prefix: Cache key prefix
        vary_on: List of request attributes to vary on (query params, headers)

    Usage:
        @app.get("/api/v1/fields")
        @cache_response(ttl=60, vary_on=["tenant_id", "page"])
        async def list_fields(request: Request):
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to find Request in args
            request = None
            for arg in args:
                if hasattr(arg, "url") and hasattr(arg, "query_params"):
                    request = arg
                    break
            if request is None:
                request = kwargs.get("request")

            # Generate cache key
            key_parts = [func.__name__]

            if request:
                # Add path
                key_parts.append(str(request.url.path))

                # Add varied parameters
                if vary_on:
                    for param in vary_on:
                        if param in request.query_params:
                            key_parts.append(f"{param}={request.query_params[param]}")
                        elif hasattr(request.headers, "get"):
                            header_value = request.headers.get(f"x-{param}")
                            if header_value:
                                key_parts.append(f"{param}={header_value}")

            cache_key = ":".join(key_parts)
            cache_key_hash = hashlib.sha256(cache_key.encode()).hexdigest()

            cache_manager = get_cache_manager()

            # Try cache
            cached = await cache_manager.get(cache_key_hash, prefix=prefix)
            if cached is not None:
                return cached

            # Execute and cache
            result = await func(*args, **kwargs)

            if result is not None:
                await cache_manager.set(cache_key_hash, result, ttl=ttl, prefix=prefix)

            return result

        return wrapper

    return decorator


async def invalidate_cache(
    pattern: str = "*",
    prefix: str | None = None,
) -> int:
    """
    Invalidate cache entries matching pattern.

    Args:
        pattern: Key pattern (supports * wildcard)
        prefix: Optional key prefix

    Returns:
        Number of keys deleted
    """
    cache_manager = get_cache_manager()
    return await cache_manager.delete_pattern(pattern, prefix=prefix)
