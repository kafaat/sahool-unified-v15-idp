"""
Caching Module for Crop Intelligence Service.

Provides caching for disease detection, nutrient analysis, and yield predictions
with support for Redis and in-memory fallback.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    expires_at: float
    hits: int = 0
    size_bytes: int = 0

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > self.expires_at


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_entries: int = 0
    memory_used_bytes: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": round(self.hit_rate, 4),
            "total_entries": self.total_entries,
            "memory_used_kb": round(self.memory_used_bytes / 1024, 2),
        }


class IntelligenceCache:
    """
    Multi-purpose cache for crop intelligence results.

    Supports:
    - Disease detection results
    - Nutrient deficiency analysis
    - Yield predictions
    - Zone diagnostics
    """

    def __init__(
        self,
        max_size: int = 500,
        default_ttl_seconds: int = 1800,  # 30 minutes
        redis_url: str = "",
    ):
        self.max_size = max_size
        self.default_ttl_seconds = default_ttl_seconds
        self.redis_url = redis_url

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
        self._lock = asyncio.Lock()
        self._redis_client = None

        logger.info(
            "intelligence_cache_initialized",
            max_size=max_size,
            default_ttl=default_ttl_seconds,
        )

    async def connect_redis(self) -> bool:
        """Connect to Redis if configured."""
        if not self.redis_url:
            return False

        try:
            import redis.asyncio as redis

            self._redis_client = redis.from_url(self.redis_url)
            await self._redis_client.ping()
            logger.info("redis_connected")
            return True
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            self._redis_client = None
            return False

    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters."""
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        hash_value = hashlib.md5(params_str.encode()).hexdigest()[:12]
        return f"crop_intel:{prefix}:{hash_value}"

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        # Try Redis first
        if self._redis_client:
            try:
                data = await self._redis_client.get(key)
                if data:
                    self._stats.hits += 1
                    return json.loads(data)
            except Exception:
                pass

        # Try memory cache
        async with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None

            entry = self._cache[key]

            if entry.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None

            self._cache.move_to_end(key)
            entry.hits += 1
            self._stats.hits += 1

            return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Set value in cache."""
        ttl = ttl_seconds or self.default_ttl_seconds

        # Store in Redis
        if self._redis_client:
            try:
                data = json.dumps(value, default=str)
                await self._redis_client.setex(key, ttl, data)
            except Exception:
                pass

        # Store in memory
        size_bytes = len(json.dumps(value, default=str).encode())

        async with self._lock:
            # Evict if needed
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                entry = self._cache.pop(oldest_key)
                self._stats.evictions += 1
                self._stats.memory_used_bytes -= entry.size_bytes

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                expires_at=time.time() + ttl,
                size_bytes=size_bytes,
            )

            self._cache[key] = entry
            self._stats.total_entries = len(self._cache)
            self._stats.memory_used_bytes += size_bytes

            return True

    async def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        deleted = False

        if self._redis_client:
            try:
                await self._redis_client.delete(key)
                deleted = True
            except Exception:
                pass

        async with self._lock:
            if key in self._cache:
                entry = self._cache.pop(key)
                self._stats.memory_used_bytes -= entry.size_bytes
                self._stats.total_entries = len(self._cache)
                deleted = True

        return deleted

    async def clear(self) -> None:
        """Clear all cache entries using SCAN (safe for production)."""
        if self._redis_client:
            try:
                cursor = 0
                while True:
                    cursor, keys = await self._redis_client.scan(cursor, match="crop_intel:*", count=100)
                    if keys:
                        await self._redis_client.delete(*keys)
                    if cursor == 0:
                        break
            except Exception:
                pass

        async with self._lock:
            self._cache.clear()
            self._stats = CacheStats()

        logger.info("intelligence_cache_cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self._stats.to_dict()

    # Convenience methods for specific cache types

    async def get_disease_detection(
        self,
        ndvi: float,
        evi: float,
        ndre: float,
        ndwi: float,
        lci: float,
        savi: float,
        crop_type: str = "unknown",
    ) -> Any | None:
        """Get cached disease detection result."""
        key = self._generate_key(
            "disease",
            ndvi=round(ndvi, 3),
            evi=round(evi, 3),
            ndre=round(ndre, 3),
            ndwi=round(ndwi, 3),
            lci=round(lci, 3),
            savi=round(savi, 3),
            crop_type=crop_type,
        )
        return await self.get(key)

    async def set_disease_detection(
        self,
        ndvi: float,
        evi: float,
        ndre: float,
        ndwi: float,
        lci: float,
        savi: float,
        crop_type: str,
        result: Any,
        ttl_seconds: int = 1800,
    ) -> bool:
        """Cache disease detection result."""
        key = self._generate_key(
            "disease",
            ndvi=round(ndvi, 3),
            evi=round(evi, 3),
            ndre=round(ndre, 3),
            ndwi=round(ndwi, 3),
            lci=round(lci, 3),
            savi=round(savi, 3),
            crop_type=crop_type,
        )
        return await self.set(key, result, ttl_seconds)

    async def get_nutrient_analysis(
        self,
        ndvi: float,
        evi: float,
        ndre: float,
        ndwi: float,
        lci: float,
        savi: float,
    ) -> Any | None:
        """Get cached nutrient analysis result."""
        key = self._generate_key(
            "nutrient",
            ndvi=round(ndvi, 3),
            evi=round(evi, 3),
            ndre=round(ndre, 3),
            ndwi=round(ndwi, 3),
            lci=round(lci, 3),
            savi=round(savi, 3),
        )
        return await self.get(key)

    async def set_nutrient_analysis(
        self,
        ndvi: float,
        evi: float,
        ndre: float,
        ndwi: float,
        lci: float,
        savi: float,
        result: Any,
        ttl_seconds: int = 1800,
    ) -> bool:
        """Cache nutrient analysis result."""
        key = self._generate_key(
            "nutrient",
            ndvi=round(ndvi, 3),
            evi=round(evi, 3),
            ndre=round(ndre, 3),
            ndwi=round(ndwi, 3),
            lci=round(lci, 3),
            savi=round(savi, 3),
        )
        return await self.set(key, result, ttl_seconds)

    async def get_yield_prediction(
        self,
        crop_type: str,
        ndvi: float,
        evi: float,
        ndre: float,
        field_area: float,
    ) -> Any | None:
        """Get cached yield prediction."""
        key = self._generate_key(
            "yield",
            crop_type=crop_type,
            ndvi=round(ndvi, 3),
            evi=round(evi, 3),
            ndre=round(ndre, 3),
            field_area=round(field_area, 2),
        )
        return await self.get(key)

    async def set_yield_prediction(
        self,
        crop_type: str,
        ndvi: float,
        evi: float,
        ndre: float,
        field_area: float,
        result: Any,
        ttl_seconds: int = 3600,
    ) -> bool:
        """Cache yield prediction."""
        key = self._generate_key(
            "yield",
            crop_type=crop_type,
            ndvi=round(ndvi, 3),
            evi=round(evi, 3),
            ndre=round(ndre, 3),
            field_area=round(field_area, 2),
        )
        return await self.set(key, result, ttl_seconds)

    async def get_zone_diagnosis(
        self,
        field_id: str,
        zone_id: str,
        date_str: str,
    ) -> Any | None:
        """Get cached zone diagnosis."""
        key = self._generate_key(
            "diagnosis",
            field_id=field_id,
            zone_id=zone_id,
            date=date_str,
        )
        return await self.get(key)

    async def set_zone_diagnosis(
        self,
        field_id: str,
        zone_id: str,
        date_str: str,
        result: Any,
        ttl_seconds: int = 900,  # 15 minutes
    ) -> bool:
        """Cache zone diagnosis."""
        key = self._generate_key(
            "diagnosis",
            field_id=field_id,
            zone_id=zone_id,
            date=date_str,
        )
        return await self.set(key, result, ttl_seconds)


def cached_analysis(
    cache: IntelligenceCache,
    cache_type: str,
    ttl_seconds: int = 1800,
) -> Callable:
    """
    Decorator for caching analysis results.

    Usage:
        @cached_analysis(cache, "disease", ttl_seconds=1800)
        async def detect_diseases(...):
            ...
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Generate cache key from arguments
            cache_key = cache._generate_key(
                cache_type,
                **{k: v for k, v in kwargs.items() if v is not None},
            )

            # Try cache first
            cached = await cache.get(cache_key)
            if cached is not None:
                return cached

            # Run function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(cache_key, result, ttl_seconds)

            return result

        return wrapper

    return decorator


# Global cache instance
_intelligence_cache: IntelligenceCache | None = None


def get_intelligence_cache() -> IntelligenceCache:
    """Get the global intelligence cache instance."""
    global _intelligence_cache
    if _intelligence_cache is None:
        _intelligence_cache = IntelligenceCache()
    return _intelligence_cache


async def init_intelligence_cache(
    redis_url: str = "",
    max_size: int = 500,
    default_ttl: int = 1800,
) -> IntelligenceCache:
    """Initialize the global intelligence cache."""
    global _intelligence_cache
    _intelligence_cache = IntelligenceCache(
        max_size=max_size,
        default_ttl_seconds=default_ttl,
        redis_url=redis_url,
    )

    if redis_url:
        await _intelligence_cache.connect_redis()

    return _intelligence_cache
