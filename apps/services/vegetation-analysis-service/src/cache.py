"""
SAHOOL Satellite Service - Redis Cache Layer
طبقة الـCache للأقمار الصناعية

Provides caching for:
- NDVI calculations (TTL: 24 hours)
- Satellite imagery metadata (TTL: 6 hours)
- Time series data (TTL: 1 hour)
- Field analysis results (TTL: 12 hours)
"""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)

# Async Redis client - lazy initialization
_redis_client = None
_redis_available = False
_redis_lock = asyncio.Lock()


async def _get_redis_client():
    """Get or initialize async Redis client."""
    global _redis_client, _redis_available

    if _redis_client is not None:
        return _redis_client

    async with _redis_lock:
        # Double-check after acquiring lock
        if _redis_client is not None:
            return _redis_client

        try:
            from redis.asyncio import from_url as redis_from_url

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            _redis_client = redis_from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            await _redis_client.ping()
            _redis_available = True
            logger.info(f"Redis connected (async): {redis_url}")
            return _redis_client
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Caching disabled.")
            _redis_available = False
            return None


async def is_cache_available() -> bool:
    """Check if Redis cache is available."""
    await _get_redis_client()
    return _redis_available


# =============================================================================
# Cache Key Generation
# =============================================================================


def _generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a unique cache key from parameters."""
    # Sort kwargs for consistent key generation
    sorted_items = sorted(kwargs.items())
    key_data = json.dumps(sorted_items, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()[:12]
    return f"satellite:{prefix}:{key_hash}"


def _ndvi_cache_key(field_id: str, date: str, satellite: str) -> str:
    """Generate cache key for NDVI data."""
    return f"satellite:ndvi:{field_id}:{date}:{satellite}"


def _analysis_cache_key(field_id: str, satellite: str) -> str:
    """Generate cache key for field analysis."""
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    return f"satellite:analysis:{field_id}:{date_str}:{satellite}"


def _timeseries_cache_key(field_id: str, days: int, satellite: str) -> str:
    """Generate cache key for time series."""
    return f"satellite:timeseries:{field_id}:{days}:{satellite}"


# =============================================================================
# Cache TTL Configuration
# =============================================================================


class CacheTTL:
    """Cache TTL constants in seconds."""

    NDVI = 24 * 60 * 60  # 24 hours
    ANALYSIS = 12 * 60 * 60  # 12 hours
    IMAGERY_METADATA = 6 * 60 * 60  # 6 hours
    TIMESERIES = 1 * 60 * 60  # 1 hour
    HEALTH_STATUS = 30 * 60  # 30 minutes


# =============================================================================
# Cache Operations
# =============================================================================


async def cache_get(key: str) -> dict[str, Any] | None:
    """Get value from cache."""
    client = await _get_redis_client()
    if not client:
        return None

    try:
        data = await client.get(key)
        if data:
            logger.debug(f"Cache HIT: {key}")
            return json.loads(data)
        logger.debug(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


async def cache_set(
    key: str,
    value: dict[str, Any],
    ttl: int = CacheTTL.NDVI,
) -> bool:
    """Set value in cache with TTL."""
    client = await _get_redis_client()
    if not client:
        return False

    try:
        data = json.dumps(value, default=str)
        await client.setex(key, ttl, data)
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete key from cache."""
    client = await _get_redis_client()
    if not client:
        return False

    try:
        await client.delete(key)
        logger.debug(f"Cache DELETE: {key}")
        return True
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False


async def cache_invalidate_field(field_id: str) -> int:
    """Invalidate all cache entries for a field using SCAN (non-blocking)."""
    client = await _get_redis_client()
    if not client:
        return 0

    try:
        pattern = f"satellite:*:{field_id}:*"
        deleted = 0
        cursor = 0

        # Use SCAN instead of KEYS to avoid blocking Redis
        while True:
            cursor, keys = await client.scan(cursor, match=pattern, count=100)
            if keys:
                deleted += await client.delete(*keys)
            if cursor == 0:
                break

        if deleted > 0:
            logger.info(f"Cache INVALIDATE: {deleted} keys for field {field_id}")
        return deleted
    except Exception as e:
        logger.error(f"Cache invalidate error: {e}")
        return 0


# =============================================================================
# NDVI Cache Functions
# =============================================================================


async def get_cached_ndvi(
    field_id: str,
    date: str,
    satellite: str,
) -> dict[str, Any] | None:
    """Get cached NDVI data for a field."""
    key = _ndvi_cache_key(field_id, date, satellite)
    return await cache_get(key)


async def cache_ndvi(
    field_id: str,
    date: str,
    satellite: str,
    ndvi_data: dict[str, Any],
) -> bool:
    """Cache NDVI data for a field."""
    key = _ndvi_cache_key(field_id, date, satellite)
    return await cache_set(key, ndvi_data, CacheTTL.NDVI)


# =============================================================================
# Analysis Cache Functions
# =============================================================================


async def get_cached_analysis(
    field_id: str,
    satellite: str,
) -> dict[str, Any] | None:
    """Get cached field analysis."""
    key = _analysis_cache_key(field_id, satellite)
    return await cache_get(key)


async def cache_analysis(
    field_id: str,
    satellite: str,
    analysis_data: dict[str, Any],
) -> bool:
    """Cache field analysis results."""
    key = _analysis_cache_key(field_id, satellite)
    return await cache_set(key, analysis_data, CacheTTL.ANALYSIS)


# =============================================================================
# Time Series Cache Functions
# =============================================================================


async def get_cached_timeseries(
    field_id: str,
    days: int,
    satellite: str,
) -> dict[str, Any] | None:
    """Get cached time series data."""
    key = _timeseries_cache_key(field_id, days, satellite)
    return await cache_get(key)


async def cache_timeseries(
    field_id: str,
    days: int,
    satellite: str,
    timeseries_data: dict[str, Any],
) -> bool:
    """Cache time series data."""
    key = _timeseries_cache_key(field_id, days, satellite)
    return await cache_set(key, timeseries_data, CacheTTL.TIMESERIES)


# =============================================================================
# Cache Decorator
# =============================================================================


def cached(
    prefix: str,
    ttl: int = CacheTTL.NDVI,
    key_params: list = None,
):
    """
    Decorator for caching function results.

    Usage:
        @cached("ndvi", ttl=CacheTTL.NDVI, key_params=["field_id", "date"])
        async def get_ndvi(field_id: str, date: str):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from specified parameters
            if key_params:
                cache_kwargs = {k: kwargs.get(k) for k in key_params if k in kwargs}
            else:
                cache_kwargs = kwargs

            cache_key = _generate_cache_key(prefix, **cache_kwargs)

            # Try to get from cache
            cached_value = await cache_get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function and cache result
            result = await func(*args, **kwargs)

            if result is not None:
                await cache_set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator


# =============================================================================
# Cache Statistics
# =============================================================================


async def _count_keys_by_pattern(client, pattern: str) -> int:
    """Count keys matching pattern using SCAN (non-blocking)."""
    count = 0
    cursor = 0
    while True:
        cursor, keys = await client.scan(cursor, match=pattern, count=100)
        count += len(keys)
        if cursor == 0:
            break
    return count


async def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    client = await _get_redis_client()
    if not client:
        return {"available": False, "error": "Redis not connected"}

    try:
        info = await client.info("stats")
        memory = await client.info("memory")

        # Count satellite keys using SCAN (non-blocking)
        ndvi_keys = await _count_keys_by_pattern(client, "satellite:ndvi:*")
        analysis_keys = await _count_keys_by_pattern(client, "satellite:analysis:*")
        timeseries_keys = await _count_keys_by_pattern(client, "satellite:timeseries:*")

        return {
            "available": True,
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0)
                / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1)
                * 100,
                2,
            ),
            "memory_used": memory.get("used_memory_human", "N/A"),
            "keys": {
                "ndvi": ndvi_keys,
                "analysis": analysis_keys,
                "timeseries": timeseries_keys,
                "total": ndvi_keys + analysis_keys + timeseries_keys,
            },
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# =============================================================================
# Cache Health Check
# =============================================================================


async def cache_health_check() -> dict[str, Any]:
    """Check cache health for monitoring."""
    client = await _get_redis_client()

    if not client:
        return {
            "status": "unhealthy",
            "message": "Redis not connected",
        }

    try:
        # Ping Redis
        start = datetime.utcnow()
        await client.ping()
        latency = (datetime.utcnow() - start).total_seconds() * 1000

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "message": "Redis connection OK",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e),
        }
