"""
Caching Module for YOLO26 Vision Service.

Provides multi-level caching for inference results with support for:
- In-memory LRU cache
- Redis distributed cache
- Content-based cache keys
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Any, TypeVar

import numpy as np
import structlog
from PIL import Image

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class CacheLevel(StrEnum):
    """Cache level."""

    MEMORY = "memory"
    REDIS = "redis"
    DISABLED = "disabled"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    expires_at: float
    hits: int = 0
    size_bytes: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > self.expires_at

    @property
    def ttl_remaining(self) -> float:
        """Get remaining TTL in seconds."""
        return max(0, self.expires_at - time.time())


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
            "memory_used_mb": round(self.memory_used_bytes / (1024 * 1024), 2),
        }


class InMemoryCache:
    """
    In-memory LRU cache for fast result retrieval.

    Features:
    - LRU eviction policy
    - TTL-based expiration
    - Size-based limits
    - Statistics tracking
    """

    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: float = 500.0,
        default_ttl_seconds: int = 3600,
    ):
        self.max_size = max_size
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.default_ttl_seconds = default_ttl_seconds

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
        self._lock = asyncio.Lock()

        logger.info(
            "memory_cache_initialized",
            max_size=max_size,
            max_memory_mb=max_memory_mb,
            default_ttl=default_ttl_seconds,
        )

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None

            entry = self._cache[key]

            # Check expiration
            if entry.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            entry.hits += 1
            self._stats.hits += 1

            logger.debug("cache_hit", key=key[:16], hits=entry.hits)
            return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: TTL in seconds (uses default if None)
            metadata: Optional metadata

        Returns:
            True if successfully cached
        """
        ttl = ttl_seconds or self.default_ttl_seconds

        # Estimate size
        size_bytes = self._estimate_size(value)

        async with self._lock:
            # Evict if necessary
            await self._evict_if_needed(size_bytes)

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                expires_at=time.time() + ttl,
                size_bytes=size_bytes,
                metadata=metadata or {},
            )

            self._cache[key] = entry
            self._stats.total_entries = len(self._cache)
            self._stats.memory_used_bytes += size_bytes

            logger.debug(
                "cache_set",
                key=key[:16],
                size_bytes=size_bytes,
                ttl=ttl,
            )
            return True

    async def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        async with self._lock:
            if key in self._cache:
                entry = self._cache.pop(key)
                self._stats.memory_used_bytes -= entry.size_bytes
                self._stats.total_entries = len(self._cache)
                return True
            return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._stats = CacheStats()
            logger.info("cache_cleared")

    async def _evict_if_needed(self, new_size: int) -> None:
        """Evict entries if cache is full."""
        # Size-based eviction
        while len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            entry = self._cache.pop(oldest_key)
            self._stats.evictions += 1
            self._stats.memory_used_bytes -= entry.size_bytes
            logger.debug("cache_evicted", key=oldest_key[:16], reason="size_limit")

        # Memory-based eviction
        while self._stats.memory_used_bytes + new_size > self.max_memory_bytes and self._cache:
            oldest_key = next(iter(self._cache))
            entry = self._cache.pop(oldest_key)
            self._stats.evictions += 1
            self._stats.memory_used_bytes -= entry.size_bytes
            logger.debug("cache_evicted", key=oldest_key[:16], reason="memory_limit")

        # TTL-based cleanup (opportunistic)
        expired_keys = [k for k, v in self._cache.items() if v.is_expired][:10]
        for key in expired_keys:
            entry = self._cache.pop(key)
            self._stats.evictions += 1
            self._stats.memory_used_bytes -= entry.size_bytes

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes."""
        try:
            if isinstance(value, (dict, list)):
                return len(json.dumps(value, default=str).encode())
            elif isinstance(value, np.ndarray):
                return value.nbytes
            elif isinstance(value, bytes):
                return len(value)
            elif isinstance(value, str):
                return len(value.encode())
            else:
                # Rough estimate for other objects
                return 1024
        except Exception:
            return 1024

    async def invalidate_by_metadata(
        self,
        match: dict[str, Any],
    ) -> int:
        """
        Invalidate entries whose metadata matches all given key-value pairs.

        Args:
            match: Metadata key-value pairs to match against.

        Returns:
            Number of entries invalidated.
        """
        async with self._lock:
            keys_to_remove = [
                key for key, entry in self._cache.items() if all(entry.metadata.get(k) == v for k, v in match.items())
            ]
            for key in keys_to_remove:
                entry = self._cache.pop(key)
                self._stats.memory_used_bytes -= entry.size_bytes
                self._stats.evictions += 1

            self._stats.total_entries = len(self._cache)
            return len(keys_to_remove)

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats


class RedisCache:
    """
    Redis-based distributed cache.

    Features:
    - Distributed caching
    - Automatic serialization
    - TTL support
    - Cluster-aware
    """

    def __init__(
        self,
        redis_url: str = "",
        prefix: str = "yolo26:",
        default_ttl_seconds: int = 3600,
    ):
        self.redis_url = redis_url
        self.prefix = prefix
        self.default_ttl_seconds = default_ttl_seconds
        self._client = None
        self._connected = False

    async def connect(self) -> bool:
        """Connect to Redis."""
        if not self.redis_url:
            logger.info("redis_not_configured")
            return False

        try:
            import redis.asyncio as redis

            self._client = redis.from_url(self.redis_url)
            await self._client.ping()
            self._connected = True
            logger.info("redis_connected", url=self.redis_url[:20] + "...")
            return True
        except Exception as e:
            logger.warning("redis_connection_failed", error=str(e))
            self._connected = False
            return False

    async def get(self, key: str) -> Any | None:
        """Get value from Redis."""
        if not self._connected or not self._client:
            return None

        try:
            full_key = f"{self.prefix}{key}"
            data = await self._client.get(full_key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.debug("redis_get_failed", key=key[:16], error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
    ) -> bool:
        """Set value in Redis."""
        if not self._connected or not self._client:
            return False

        try:
            full_key = f"{self.prefix}{key}"
            ttl = ttl_seconds or self.default_ttl_seconds
            data = json.dumps(value, default=str)
            await self._client.setex(full_key, ttl, data)
            return True
        except Exception as e:
            logger.debug("redis_set_failed", key=key[:16], error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis."""
        if not self._connected or not self._client:
            return False

        try:
            full_key = f"{self.prefix}{key}"
            await self._client.delete(full_key)
            return True
        except Exception as e:
            logger.debug("redis_delete_failed", key=key[:16], error=str(e))
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._connected = False
            logger.info("redis_disconnected")


class ResultCache:
    """
    Multi-level result cache for inference results.

    Combines in-memory and Redis caching with intelligent key generation
    based on image content and inference parameters.
    """

    def __init__(
        self,
        memory_cache: InMemoryCache | None = None,
        redis_cache: RedisCache | None = None,
        enable_memory: bool = True,
        enable_redis: bool = True,
    ):
        self.memory_cache = memory_cache or InMemoryCache()
        self.redis_cache = redis_cache
        self.enable_memory = enable_memory
        self.enable_redis = enable_redis and redis_cache is not None

        logger.info(
            "result_cache_initialized",
            memory_enabled=enable_memory,
            redis_enabled=self.enable_redis,
        )

    async def connect_redis(self, redis_url: str) -> bool:
        """Connect Redis cache."""
        if not redis_url:
            return False

        self.redis_cache = RedisCache(redis_url=redis_url)
        connected = await self.redis_cache.connect()
        self.enable_redis = connected
        return connected

    def generate_cache_key(
        self,
        image: np.ndarray | Image.Image | bytes,
        task: str,
        variant: str,
        confidence: float,
        iou: float,
        image_size: int,
    ) -> str:
        """
        Generate cache key from image content and parameters.

        Uses perceptual hashing for similar image matching.
        """
        # Get image hash
        image_hash = self._compute_image_hash(image)

        # Combine with parameters
        params_str = f"{task}_{variant}_{confidence:.2f}_{iou:.2f}_{image_size}"
        params_hash = hashlib.md5(params_str.encode(), usedforsecurity=False).hexdigest()[:8]

        return f"{image_hash}_{params_hash}"

    def _compute_image_hash(self, image: np.ndarray | Image.Image | bytes) -> str:
        """
        Compute perceptual hash of image.

        Uses average hash (aHash) for speed and reasonable accuracy.
        """
        try:
            # Convert to PIL Image
            if isinstance(image, np.ndarray):
                pil_image = Image.fromarray(image)
            elif isinstance(image, bytes):
                pil_image = Image.open(io.BytesIO(image))
            else:
                pil_image = image

            # Resize to 16x16 for hashing
            resized = pil_image.convert("L").resize((16, 16), Image.Resampling.LANCZOS)
            pixels = np.array(resized)

            # Compute average hash
            avg = pixels.mean()
            bits = (pixels > avg).flatten()
            hash_value = "".join("1" if b else "0" for b in bits)

            # Convert to hex
            return format(int(hash_value, 2), "016x")

        except Exception as e:
            # Fallback to random hash
            logger.debug("image_hash_failed", error=str(e))
            return hashlib.md5(str(time.time()).encode(), usedforsecurity=False).hexdigest()[:16]

    async def get(
        self,
        image: np.ndarray | Image.Image | bytes,
        task: str,
        variant: str,
        confidence: float,
        iou: float,
        image_size: int,
    ) -> Any | None:
        """
        Get cached result for image and parameters.

        Checks memory cache first, then Redis.
        """
        key = self.generate_cache_key(image, task, variant, confidence, iou, image_size)

        # Check memory cache
        if self.enable_memory:
            result = await self.memory_cache.get(key)
            if result is not None:
                logger.debug("cache_hit_memory", key=key[:16])
                return result

        # Check Redis cache
        if self.enable_redis and self.redis_cache:
            result = await self.redis_cache.get(key)
            if result is not None:
                # Populate memory cache
                if self.enable_memory:
                    await self.memory_cache.set(key, result)
                logger.debug("cache_hit_redis", key=key[:16])
                return result

        logger.debug("cache_miss", key=key[:16])
        return None

    async def set(
        self,
        image: np.ndarray | Image.Image | bytes,
        task: str,
        variant: str,
        confidence: float,
        iou: float,
        image_size: int,
        result: Any,
        ttl_seconds: int | None = None,
    ) -> bool:
        """
        Cache inference result.

        Stores in both memory and Redis caches.
        """
        key = self.generate_cache_key(image, task, variant, confidence, iou, image_size)

        success = True

        # Store in memory with task/variant metadata for pattern invalidation
        if self.enable_memory:
            metadata = {"task": task, "variant": variant}
            memory_success = await self.memory_cache.set(key, result, ttl_seconds, metadata=metadata)
            success = success and memory_success

        # Store in Redis
        if self.enable_redis and self.redis_cache:
            redis_success = await self.redis_cache.set(key, result, ttl_seconds)
            success = success and redis_success

        return success

    async def invalidate(
        self,
        task: str | None = None,
        variant: str | None = None,
    ) -> int:
        """
        Invalidate cached results.

        If task/variant specified, only invalidates matching entries.
        Otherwise clears all.
        """
        if task is None and variant is None:
            await self.memory_cache.clear()
            logger.info("cache_invalidated_all")
            return -1

        # Pattern-based invalidation: remove entries matching task/variant
        match_filter: dict[str, Any] = {}
        if task is not None:
            match_filter["task"] = task
        if variant is not None:
            match_filter["variant"] = variant

        count = await self.memory_cache.invalidate_by_metadata(match_filter)

        logger.info(
            "cache_invalidated_pattern",
            task=task,
            variant=variant,
            invalidated_count=count,
        )
        return count

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "memory": self.memory_cache.get_stats().to_dict(),
            "redis_enabled": self.enable_redis,
        }


def cached_inference(
    cache: ResultCache,
    task: str,
    variant: str,
    confidence: float = 0.25,
    iou: float = 0.45,
    image_size: int = 640,
    ttl_seconds: int = 3600,
) -> Callable:
    """
    Decorator for caching inference results.

    Usage:
        @cached_inference(cache, task="pest_detection", variant="m")
        async def detect(image):
            return await model.predict(image)
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(image: np.ndarray | Image.Image | bytes, *args, **kwargs):
            # Try cache first
            cached = await cache.get(image, task, variant, confidence, iou, image_size)
            if cached is not None:
                return cached

            # Run inference
            result = await func(image, *args, **kwargs)

            # Cache result
            await cache.set(image, task, variant, confidence, iou, image_size, result, ttl_seconds)

            return result

        return wrapper

    return decorator


# Global cache instance
_result_cache: ResultCache | None = None


def get_result_cache() -> ResultCache:
    """Get the global result cache instance."""
    global _result_cache
    if _result_cache is None:
        _result_cache = ResultCache()
    return _result_cache


async def init_cache(redis_url: str = "") -> ResultCache:
    """Initialize the global cache with optional Redis."""
    global _result_cache
    _result_cache = ResultCache()

    if redis_url:
        await _result_cache.connect_redis(redis_url)

    return _result_cache
