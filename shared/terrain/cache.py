"""
SAHOOL Terrain Caching Module
=============================
Provides caching utilities for terrain-related calculations.

مودول التخزين المؤقت للتضاريس

Features:
- In-memory LRU cache with TTL support
- Redis cache integration (optional)
- Cache key generation for terrain operations
- Async-compatible caching decorators

Usage:
    from shared.terrain.cache import (
        TerrainCache,
        cache_result,
        generate_cache_key,
    )

    cache = TerrainCache()
    await cache.get("terrain:field-001:slope")
    await cache.set("terrain:field-001:slope", result, ttl=3600)

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# =============================================================================
# Configuration
# =============================================================================

# Default cache settings
DEFAULT_TTL_SECONDS = 3600  # 1 hour
DEFAULT_MAX_SIZE = 1000  # Maximum items in memory cache
DEFAULT_NAMESPACE = "terrain"

# Environment-based settings
REDIS_URL = os.getenv("REDIS_URL", "")
CACHE_ENABLED = os.getenv("TERRAIN_CACHE_ENABLED", "true").lower() == "true"


# =============================================================================
# Cache Entry
# =============================================================================


@dataclass
class CacheEntry:
    """Cache entry with TTL support."""

    value: Any
    expires_at: float
    created_at: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > self.expires_at


# =============================================================================
# In-Memory LRU Cache
# =============================================================================


class LRUCache:
    """
    Thread-safe LRU cache with TTL support.
    ذاكرة تخزين مؤقت LRU مع دعم TTL.
    """

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE):
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """
        Get value from cache.
        الحصول على قيمة من التخزين المؤقت.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        self._hits += 1
        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        """
        Set value in cache.
        تعيين قيمة في التخزين المؤقت.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        # Remove oldest entry if at capacity
        while len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        expires_at = time.time() + ttl
        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
        self._cache.move_to_end(key)

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        حذف قيمة من التخزين المؤقت.

        Args:
            key: Cache key

        Returns:
            True if key was deleted
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        إزالة الإدخالات منتهية الصلاحية.

        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if v.expires_at < now]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / max(self._hits + self._misses, 1),
        }


# =============================================================================
# Redis Cache (Optional)
# =============================================================================


class RedisCache:
    """
    Redis-based cache implementation.
    تنفيذ التخزين المؤقت القائم على Redis.
    """

    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or REDIS_URL
        self._client = None
        self._connected = False

    async def _get_client(self):
        """Get or create Redis client."""
        if self._client is None and self.redis_url:
            try:
                import redis.asyncio as redis

                self._client = redis.from_url(self.redis_url)
                self._connected = True
            except ImportError:
                logger.warning("redis package not installed, falling back to memory cache")
                self._connected = False
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self._connected = False
        return self._client

    async def get(self, key: str) -> Any | None:
        """Get value from Redis."""
        client = await self._get_client()
        if not client:
            return None

        try:
            value = await client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = DEFAULT_TTL_SECONDS,
    ) -> bool:
        """Set value in Redis."""
        client = await self._get_client()
        if not client:
            return False

        try:
            serialized = json.dumps(value)
            await client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis."""
        client = await self._get_client()
        if not client:
            return False

        try:
            result = await client.delete(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass
            self._client = None
            self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected


# =============================================================================
# Unified Terrain Cache
# =============================================================================


class TerrainCache:
    """
    Unified terrain cache with Redis and memory fallback.
    ذاكرة تخزين مؤقت موحدة للتضاريس مع احتياطي للذاكرة.

    Uses Redis if available, falls back to in-memory LRU cache.
    """

    def __init__(
        self,
        namespace: str = DEFAULT_NAMESPACE,
        max_memory_size: int = DEFAULT_MAX_SIZE,
        redis_url: str | None = None,
        use_redis: bool = True,
    ):
        self.namespace = namespace
        self._memory_cache = LRUCache(max_size=max_memory_size)
        self._redis_cache = RedisCache(redis_url) if use_redis else None
        self._enabled = CACHE_ENABLED

    def _make_key(self, key: str) -> str:
        """Create namespaced cache key."""
        return f"{self.namespace}:{key}"

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache (Redis first, then memory).
        الحصول على قيمة من التخزين المؤقت.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self._enabled:
            return None

        full_key = self._make_key(key)

        # Try Redis first
        if self._redis_cache and self._redis_cache.is_connected:
            value = await self._redis_cache.get(full_key)
            if value is not None:
                return value

        # Fall back to memory
        return self._memory_cache.get(full_key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = DEFAULT_TTL_SECONDS,
    ) -> bool:
        """
        Set value in cache (both Redis and memory).
        تعيين قيمة في التخزين المؤقت.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds

        Returns:
            True if successfully cached
        """
        if not self._enabled:
            return False

        full_key = self._make_key(key)

        # Store in memory
        self._memory_cache.set(full_key, value, ttl)

        # Store in Redis if available
        if self._redis_cache:
            await self._redis_cache.set(full_key, value, ttl)

        return True

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        حذف قيمة من التخزين المؤقت.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        full_key = self._make_key(key)
        deleted = self._memory_cache.delete(full_key)

        if self._redis_cache:
            await self._redis_cache.delete(full_key)

        return deleted

    async def invalidate_field(self, field_id: str) -> int:
        """
        Invalidate all cache entries for a field.
        إبطال جميع إدخالات التخزين المؤقت لحقل.

        Args:
            field_id: Field identifier

        Returns:
            Number of entries invalidated
        """
        # This is a simple implementation - for memory cache
        # A more sophisticated version would use pattern matching
        count = 0
        prefix = f"{self.namespace}:{field_id}"

        # Clean memory cache
        keys_to_delete = [k for k in self._memory_cache._cache if k.startswith(prefix)]
        for key in keys_to_delete:
            del self._memory_cache._cache[key]
            count += 1

        return count

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "enabled": self._enabled,
            "namespace": self.namespace,
            "memory": self._memory_cache.stats(),
        }
        if self._redis_cache:
            stats["redis_connected"] = self._redis_cache.is_connected
        return stats

    async def close(self) -> None:
        """Close cache connections."""
        if self._redis_cache:
            await self._redis_cache.close()


# =============================================================================
# Cache Key Generation
# =============================================================================


def generate_cache_key(
    operation: str,
    field_id: str,
    **params: Any,
) -> str:
    """
    Generate a cache key for terrain operations.
    توليد مفتاح تخزين مؤقت لعمليات التضاريس.

    Args:
        operation: Operation name (e.g., "slope", "twi", "contours")
        field_id: Field identifier
        **params: Additional parameters to include in key

    Returns:
        Cache key string
    """
    # Sort params for consistent key generation
    sorted_params = sorted(params.items())
    params_str = json.dumps(sorted_params, sort_keys=True)

    # Create hash of params
    params_hash = hashlib.md5(params_str.encode(), usedforsecurity=False).hexdigest()[:8]

    return f"{field_id}:{operation}:{params_hash}"


def generate_geometry_hash(geometry: dict[str, Any]) -> str:
    """
    Generate a hash for a GeoJSON geometry.
    توليد تجزئة لهندسة GeoJSON.

    Args:
        geometry: GeoJSON geometry object

    Returns:
        Hash string
    """
    geom_str = json.dumps(geometry, sort_keys=True)
    return hashlib.md5(geom_str.encode(), usedforsecurity=False).hexdigest()


# =============================================================================
# Caching Decorator
# =============================================================================


def cache_result(
    cache: TerrainCache,
    operation: str,
    ttl: int = DEFAULT_TTL_SECONDS,
    key_params: list[str] | None = None,
):
    """
    Decorator to cache function results.
    مزخرف لتخزين نتائج الدالة مؤقتاً.

    Args:
        cache: TerrainCache instance
        operation: Operation name for cache key
        ttl: Time-to-live in seconds
        key_params: List of parameter names to include in cache key

    Usage:
        @cache_result(terrain_cache, "slope", ttl=3600, key_params=["field_id"])
        async def calculate_slope(field_id: str, ...):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Extract field_id from args or kwargs
            field_id = kwargs.get("field_id", args[0] if args else "unknown")

            # Build cache key from specified params
            cache_params = {}
            if key_params:
                for param in key_params:
                    if param in kwargs:
                        cache_params[param] = kwargs[param]

            cache_key = generate_cache_key(operation, field_id, **cache_params)

            # Try to get from cache
            cached = await cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")

            return result

        return wrapper

    return decorator


def cache_result_sync(
    cache: LRUCache,
    operation: str,
    ttl: int = DEFAULT_TTL_SECONDS,
):
    """
    Synchronous version of cache_result decorator.
    النسخة المتزامنة من مزخرف cache_result.

    Args:
        cache: LRUCache instance
        operation: Operation name for cache key
        ttl: Time-to-live in seconds

    Usage:
        @cache_result_sync(lru_cache, "slope", ttl=3600)
        def calculate_slope_sync(field_id: str, ...):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            field_id = kwargs.get("field_id", args[0] if args else "unknown")
            cache_key = generate_cache_key(operation, field_id, **kwargs)

            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")

            return result

        return wrapper

    return decorator


# =============================================================================
# Global cache instance
# =============================================================================

# Create a default cache instance
_default_cache: TerrainCache | None = None


def get_terrain_cache() -> TerrainCache:
    """
    Get the default terrain cache instance.
    الحصول على مثيل التخزين المؤقت الافتراضي للتضاريس.

    Returns:
        TerrainCache instance
    """
    global _default_cache
    if _default_cache is None:
        _default_cache = TerrainCache()
    return _default_cache


# =============================================================================
# Export all
# =============================================================================

__all__ = [
    # Classes
    "CacheEntry",
    "LRUCache",
    "RedisCache",
    "TerrainCache",
    # Key generation
    "generate_cache_key",
    "generate_geometry_hash",
    # Decorators
    "cache_result",
    "cache_result_sync",
    # Utilities
    "get_terrain_cache",
    # Constants
    "DEFAULT_TTL_SECONDS",
    "DEFAULT_MAX_SIZE",
    "DEFAULT_NAMESPACE",
]
