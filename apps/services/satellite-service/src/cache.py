"""
SAHOOL Satellite Service - Redis Cache Layer
طبقة الـCache للأقمار الصناعية

Provides caching for:
- NDVI calculations (TTL: 24 hours)
- Satellite imagery metadata (TTL: 6 hours)
- Time series data (TTL: 1 hour)
- Field analysis results (TTL: 12 hours)
"""

import json
import hashlib
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from functools import wraps
import os

logger = logging.getLogger(__name__)

# Redis client - lazy initialization
_redis_client = None
_redis_available = False


def _get_redis_client():
    """Get or initialize Redis client."""
    global _redis_client, _redis_available

    if _redis_client is not None:
        return _redis_client

    try:
        import redis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        # Test connection
        _redis_client.ping()
        _redis_available = True
        logger.info(f"Redis connected: {redis_url}")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis not available: {e}. Caching disabled.")
        _redis_available = False
        return None


def is_cache_available() -> bool:
    """Check if Redis cache is available."""
    _get_redis_client()
    return _redis_available


# =============================================================================
# Cache Key Generation
# =============================================================================


def _generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate a unique cache key from parameters."""
    # Sort kwargs for consistent key generation
    sorted_items = sorted(kwargs.items())
    key_data = json.dumps(sorted_items, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
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


async def cache_get(key: str) -> Optional[Dict[str, Any]]:
    """Get value from cache."""
    client = _get_redis_client()
    if not client:
        return None

    try:
        data = client.get(key)
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
    value: Dict[str, Any],
    ttl: int = CacheTTL.NDVI,
) -> bool:
    """Set value in cache with TTL."""
    client = _get_redis_client()
    if not client:
        return False

    try:
        data = json.dumps(value, default=str)
        client.setex(key, ttl, data)
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete key from cache."""
    client = _get_redis_client()
    if not client:
        return False

    try:
        client.delete(key)
        logger.debug(f"Cache DELETE: {key}")
        return True
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False


async def cache_invalidate_field(field_id: str) -> int:
    """Invalidate all cache entries for a field."""
    client = _get_redis_client()
    if not client:
        return 0

    try:
        pattern = f"satellite:*:{field_id}:*"
        keys = client.keys(pattern)
        if keys:
            deleted = client.delete(*keys)
            logger.info(f"Cache INVALIDATE: {deleted} keys for field {field_id}")
            return deleted
        return 0
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
) -> Optional[Dict[str, Any]]:
    """Get cached NDVI data for a field."""
    key = _ndvi_cache_key(field_id, date, satellite)
    return await cache_get(key)


async def cache_ndvi(
    field_id: str,
    date: str,
    satellite: str,
    ndvi_data: Dict[str, Any],
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
) -> Optional[Dict[str, Any]]:
    """Get cached field analysis."""
    key = _analysis_cache_key(field_id, satellite)
    return await cache_get(key)


async def cache_analysis(
    field_id: str,
    satellite: str,
    analysis_data: Dict[str, Any],
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
) -> Optional[Dict[str, Any]]:
    """Get cached time series data."""
    key = _timeseries_cache_key(field_id, days, satellite)
    return await cache_get(key)


async def cache_timeseries(
    field_id: str,
    days: int,
    satellite: str,
    timeseries_data: Dict[str, Any],
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


async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    client = _get_redis_client()
    if not client:
        return {"available": False, "error": "Redis not connected"}

    try:
        info = client.info("stats")
        memory = client.info("memory")

        # Count satellite keys
        ndvi_keys = len(client.keys("satellite:ndvi:*"))
        analysis_keys = len(client.keys("satellite:analysis:*"))
        timeseries_keys = len(client.keys("satellite:timeseries:*"))

        return {
            "available": True,
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0)
                / max(
                    info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1
                )
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


async def cache_health_check() -> Dict[str, Any]:
    """Check cache health for monitoring."""
    client = _get_redis_client()

    if not client:
        return {
            "status": "unhealthy",
            "message": "Redis not connected",
        }

    try:
        # Ping Redis
        start = datetime.utcnow()
        client.ping()
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
