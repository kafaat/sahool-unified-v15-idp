"""
SAHOOL NDVI Caching Strategy
Unified caching layer for NDVI data fetching

Sprint 8: Reduce API calls by ~70% with intelligent caching
"""

from __future__ import annotations

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with expiration"""

    value: dict[str, Any]
    created_at: datetime
    expires_at: datetime
    hits: int = 0

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) >= self.expires_at

    @property
    def age_seconds(self) -> float:
        return (datetime.now(UTC) - self.created_at).total_seconds()


class CacheBackend(ABC):
    """Abstract cache backend interface"""

    @abstractmethod
    def get(self, key: str) -> dict[str, Any] | None:
        """Get value from cache"""
        pass

    @abstractmethod
    def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        """Set value in cache with TTL"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        pass

    @abstractmethod
    def clear(self) -> int:
        """Clear all entries, return count cleared"""
        pass


class InMemoryCache(CacheBackend):
    """
    In-memory cache implementation.

    Suitable for development and single-instance deployments.
    For production, replace with Redis backend using same interface.
    """

    def __init__(self, max_entries: int = 10000):
        self._store: dict[str, CacheEntry] = {}
        self._max_entries = max_entries
        self._stats = {"hits": 0, "misses": 0, "sets": 0, "evictions": 0}

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._store.get(key)

        if entry is None:
            self._stats["misses"] += 1
            return None

        if entry.is_expired:
            self._store.pop(key, None)
            self._stats["misses"] += 1
            return None

        entry.hits += 1
        self._stats["hits"] += 1
        return entry.value

    def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        # Evict old entries if at capacity
        if len(self._store) >= self._max_entries:
            self._evict_expired()

        if len(self._store) >= self._max_entries:
            self._evict_lru()

        now = datetime.now(UTC)
        self._store[key] = CacheEntry(
            value=value,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl_seconds),
        )
        self._stats["sets"] += 1

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> int:
        count = len(self._store)
        self._store.clear()
        return count

    def _evict_expired(self) -> int:
        """Remove all expired entries"""
        expired = [k for k, v in self._store.items() if v.is_expired]
        for key in expired:
            del self._store[key]
        self._stats["evictions"] += len(expired)
        return len(expired)

    def _evict_lru(self, count: int = 100) -> int:
        """Remove least recently used entries"""
        # Sort by hits (ascending) and age (descending)
        sorted_keys = sorted(
            self._store.keys(),
            key=lambda k: (self._store[k].hits, -self._store[k].age_seconds),
        )

        evicted = 0
        for key in sorted_keys[:count]:
            del self._store[key]
            evicted += 1

        self._stats["evictions"] += evicted
        return evicted

    @property
    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0.0
        total = self._stats["hits"] + self._stats["misses"]
        if total > 0:
            hit_rate = self._stats["hits"] / total

        return {
            **self._stats,
            "entries": len(self._store),
            "hit_rate": round(hit_rate, 4),
        }


def make_cache_key(
    *,
    field_id: str,
    start_date: str,
    end_date: str,
    source: str = "sentinel2",
    extra: dict[str, Any] | None = None,
) -> str:
    """
    Generate a stable, unique cache key for NDVI queries.

    Uses SHA-256 for consistent key length and collision resistance.

    Args:
        field_id: Field UUID
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        source: Data source identifier
        extra: Additional parameters to include in key

    Returns:
        64-character hex cache key
    """
    key_data = {
        "field_id": field_id,
        "start": start_date,
        "end": end_date,
        "source": source,
    }

    if extra:
        key_data["extra"] = extra

    raw = json.dumps(key_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def make_observation_key(*, field_id: str, obs_date: str, source: str) -> str:
    """Generate cache key for a single observation"""
    raw = f"{field_id}:{obs_date}:{source}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Cache TTL Strategy
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class CacheTTLConfig:
    """
    TTL configuration for different cache scenarios.

    Longer TTL for historical data (won't change).
    Shorter TTL for recent data (may be updated).
    """

    # Historical data (>30 days old) - rarely changes
    historical_ttl: int = 86400 * 7  # 7 days

    # Recent data (7-30 days old) - may be revised
    recent_ttl: int = 86400  # 24 hours

    # Current data (<7 days old) - may update frequently
    current_ttl: int = 3600  # 1 hour

    # Failed/error responses - short cache to allow retry
    error_ttl: int = 300  # 5 minutes


DEFAULT_TTL_CONFIG = CacheTTLConfig()


def calculate_ttl(
    obs_date: datetime,
    config: CacheTTLConfig = DEFAULT_TTL_CONFIG,
) -> int:
    """
    Calculate appropriate TTL based on observation date.

    Args:
        obs_date: Observation date
        config: TTL configuration

    Returns:
        TTL in seconds
    """
    now = datetime.now(UTC)
    age_days = (now - obs_date).days

    if age_days > 30:
        return config.historical_ttl
    elif age_days > 7:
        return config.recent_ttl
    else:
        return config.current_ttl


# ─────────────────────────────────────────────────────────────────────────────
# Global Cache Instance
# ─────────────────────────────────────────────────────────────────────────────

# Default in-memory cache instance
# In production, replace with Redis:
#   from redis import Redis
#   _cache = RedisCache(Redis.from_url(os.environ["REDIS_URL"]))
_cache: CacheBackend = InMemoryCache()


def get_cache() -> CacheBackend:
    """Get the global cache instance"""
    return _cache


def set_cache(backend: CacheBackend) -> None:
    """Set a custom cache backend (for testing or Redis)"""
    global _cache
    _cache = backend
