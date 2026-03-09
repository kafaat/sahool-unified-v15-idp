"""
SAHOOL Advisory Service - Caching Layer
========================================
Provides caching for advisory computations and knowledge base queries.

Features:
- Disease lookup caching
- Fertilizer plan caching
- Crop requirements caching
- NDVI assessment caching with invalidation
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class AdvisoryCache:
    """
    In-memory cache for advisory service with TTL support.
    Designed for fast lookups of knowledge base data and computed recommendations.
    """

    def __init__(self, max_size: int = 5000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = asyncio.Lock()

        # Cache statistics
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expires_at = self._cache[key]

            if time.time() > expires_at:
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        async with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl

            # Evict oldest if at capacity
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)

            self._cache[key] = (value, expires_at)

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def delete_pattern(self, prefix: str) -> int:
        """Delete keys matching prefix."""
        async with self._lock:
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete)

    async def clear(self) -> int:
        """Clear all cache entries."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
        }


# Global cache instance
_advisory_cache: AdvisoryCache | None = None


def get_advisory_cache() -> AdvisoryCache:
    """Get the global advisory cache instance."""
    global _advisory_cache
    if _advisory_cache is None:
        max_size = int(os.getenv("ADVISORY_CACHE_SIZE", "5000"))
        default_ttl = int(os.getenv("ADVISORY_CACHE_TTL", "3600"))
        _advisory_cache = AdvisoryCache(max_size=max_size, default_ttl=default_ttl)
    return _advisory_cache


def _generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """Generate a cache key from function name and arguments."""
    key_data = {
        "func": func_name,
        "args": [
            str(arg)
            for arg in args
            if not hasattr(arg, "__class__") or str(type(arg).__name__) not in ("Request", "User")
        ],
        "kwargs": {k: str(v) for k, v in sorted(kwargs.items()) if k not in ("user", "request")},
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()[:32]


# ─────────────────────────────────────────────────────────────────────────────
# Caching Decorators
# ─────────────────────────────────────────────────────────────────────────────


def cache_disease_lookup(ttl: int = 3600):
    """
    Decorator for caching disease lookups.
    Disease data changes infrequently, so longer TTL is appropriate.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_advisory_cache()
            cache_key = f"disease:{_generate_cache_key(func.__name__, *args, **kwargs)}"

            # Check cache synchronously (sync function)
            if cache_key in cache._cache:
                value, expires_at = cache._cache[cache_key]
                if time.time() <= expires_at:
                    cache._hits += 1
                    logger.debug(f"Cache hit for disease lookup: {cache_key[:16]}...")
                    return value
                else:
                    del cache._cache[cache_key]

            cache._misses += 1

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            if result is not None:
                while len(cache._cache) >= cache.max_size:
                    cache._cache.popitem(last=False)
                cache._cache[cache_key] = (result, time.time() + ttl)

            return result

        return wrapper

    return decorator


def cache_fertilizer_plan(ttl: int = 1800):
    """
    Decorator for caching fertilizer plan computations.
    Plans depend on crop/stage, so moderate TTL is appropriate.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_advisory_cache()
            cache_key = f"fertilizer:{_generate_cache_key(func.__name__, *args, **kwargs)}"

            # Check cache synchronously
            if cache_key in cache._cache:
                value, expires_at = cache._cache[cache_key]
                if time.time() <= expires_at:
                    cache._hits += 1
                    logger.debug(f"Cache hit for fertilizer plan: {cache_key[:16]}...")
                    return value
                else:
                    del cache._cache[cache_key]

            cache._misses += 1

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            if result is not None:
                while len(cache._cache) >= cache.max_size:
                    cache._cache.popitem(last=False)
                cache._cache[cache_key] = (result, time.time() + ttl)

            return result

        return wrapper

    return decorator


def cache_crop_requirements(ttl: int = 7200):
    """
    Decorator for caching crop requirements.
    Requirements are static, so longer TTL is appropriate.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_advisory_cache()
            cache_key = f"crop_req:{_generate_cache_key(func.__name__, *args, **kwargs)}"

            # Check cache synchronously
            if cache_key in cache._cache:
                value, expires_at = cache._cache[cache_key]
                if time.time() <= expires_at:
                    cache._hits += 1
                    return value
                else:
                    del cache._cache[cache_key]

            cache._misses += 1
            result = func(*args, **kwargs)

            if result is not None:
                while len(cache._cache) >= cache.max_size:
                    cache._cache.popitem(last=False)
                cache._cache[cache_key] = (result, time.time() + ttl)

            return result

        return wrapper

    return decorator


async def cache_async_result(
    key: str,
    ttl: int,
    compute_func: Callable[[], Any],
) -> Any:
    """
    Cache helper for async computations.

    Usage:
        result = await cache_async_result(
            key=f"ndvi:{field_id}",
            ttl=300,
            compute_func=lambda: compute_ndvi_assessment(field_id)
        )
    """
    cache = get_advisory_cache()

    # Check cache
    cached = await cache.get(key)
    if cached is not None:
        return cached

    # Compute result
    if asyncio.iscoroutinefunction(compute_func):
        result = await compute_func()
    else:
        result = compute_func()

    # Cache result
    if result is not None:
        await cache.set(key, result, ttl)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Cache Invalidation
# ─────────────────────────────────────────────────────────────────────────────


async def invalidate_disease_cache() -> int:
    """Invalidate all disease lookup caches."""
    cache = get_advisory_cache()
    count = await cache.delete_pattern("disease:")
    logger.info(f"Invalidated {count} disease cache entries")
    return count


async def invalidate_fertilizer_cache() -> int:
    """Invalidate all fertilizer plan caches."""
    cache = get_advisory_cache()
    count = await cache.delete_pattern("fertilizer:")
    logger.info(f"Invalidated {count} fertilizer cache entries")
    return count


async def invalidate_crop_cache() -> int:
    """Invalidate all crop requirements caches."""
    cache = get_advisory_cache()
    count = await cache.delete_pattern("crop_req:")
    logger.info(f"Invalidated {count} crop requirement cache entries")
    return count


async def invalidate_all_caches() -> dict[str, int]:
    """Invalidate all advisory caches."""
    cache = get_advisory_cache()
    count = await cache.clear()

    # Reset statistics
    cache._hits = 0
    cache._misses = 0

    logger.info(f"Invalidated all {count} cache entries")

    return {"total_invalidated": count}
