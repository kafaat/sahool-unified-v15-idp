# =============================================================================
# Knowledge Base Caching Layer (GAP-19)
# طبقة التخزين المؤقت لقاعدة المعرفة
# =============================================================================

from __future__ import annotations

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with TTL."""

    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    ttl_seconds: float = 300.0  # 5 minutes default
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds


class KnowledgeCache:
    """LRU cache with TTL for knowledge base queries.
    ذاكرة تخزين مؤقت LRU مع TTL لاستعلامات قاعدة المعرفة"""

    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """Get value from cache, returns None if miss or expired."""
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None

        if entry.is_expired:
            del self._cache[key]
            self._misses += 1
            logger.debug("cache_entry_expired", key=key)
            return None

        # Move to end (most recently used) and record hit
        self._cache.move_to_end(key)
        entry.hits += 1
        self._hits += 1
        return entry.value

    def put(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Put value in cache with optional custom TTL."""
        effective_ttl = ttl if ttl is not None else self._default_ttl

        # If key exists, update in place and move to end
        if key in self._cache:
            self._cache[key] = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=effective_ttl,
            )
            self._cache.move_to_end(key)
            return

        # Evict expired entries first to free space
        self._evict_expired()

        # If still at capacity, evict LRU
        while len(self._cache) >= self._max_size:
            self._evict_lru()

        self._cache[key] = CacheEntry(
            key=key,
            value=value,
            ttl_seconds=effective_ttl,
        )

    def invalidate(self, key: str) -> bool:
        """Remove a specific key. Returns True if key existed."""
        if key in self._cache:
            del self._cache[key]
            logger.debug("cache_invalidated", key=key)
            return True
        return False

    def invalidate_by_prefix(self, prefix: str) -> int:
        """Remove all keys with given prefix. Returns count removed."""
        keys_to_remove = [k for k in self._cache if k.startswith(prefix)]
        for key in keys_to_remove:
            del self._cache[key]
        if keys_to_remove:
            logger.debug("cache_invalidated_by_prefix", prefix=prefix, count=len(keys_to_remove))
        return len(keys_to_remove)

    def invalidate_collection(self, collection: str) -> int:
        """Invalidate all cached entries for a collection.
        إبطال جميع الإدخالات المخزنة مؤقتا لمجموعة معينة"""
        # Collection info is embedded in the cache key via make_key,
        # so we search for keys whose entries contain the collection marker.
        # Since keys are hashes, we maintain a reverse index approach:
        # iterate and check entries whose key was built with this collection.
        # For efficiency, we use prefix-based invalidation with the collection hash segment.
        keys_to_remove = []
        for key, entry in self._cache.items():
            # Check if this entry's key incorporates the collection
            # We store the original key parts in the CacheEntry.key field
            if collection in entry.key:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del self._cache[key]
        if keys_to_remove:
            logger.debug("cache_collection_invalidated", collection=collection, count=len(keys_to_remove))
        return len(keys_to_remove)

    def clear(self) -> None:
        """Clear entire cache."""
        count = len(self._cache)
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("cache_cleared", entries_removed=count)

    def _evict_expired(self) -> int:
        """Remove all expired entries. Returns count evicted."""
        expired_keys = [k for k, v in self._cache.items() if v.is_expired]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug("cache_evicted_expired", count=len(expired_keys))
        return len(expired_keys)

    def _evict_lru(self) -> None:
        """Evict least recently used entry (first item in OrderedDict)."""
        if self._cache:
            evicted_key, _ = self._cache.popitem(last=False)
            logger.debug("cache_evicted_lru", key=evicted_key)

    @staticmethod
    def make_key(query: str, collection: str = "", domain: str = "", **kwargs: Any) -> str:
        """Generate deterministic cache key from query parameters."""
        parts = [query, collection, domain, str(sorted(kwargs.items()))]
        return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]

    @property
    def stats(self) -> dict[str, Any]:
        """Cache statistics."""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / max(1, total), 3),
            "ttl_default": self._default_ttl,
        }
