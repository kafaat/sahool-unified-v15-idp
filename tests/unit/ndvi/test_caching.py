"""
SAHOOL NDVI Caching Tests
Sprint 8: Unit tests for caching strategy
"""

import sys
import time

sys.path.insert(0, "archive/kernel-legacy/kernel/services/ndvi_engine/src")

from datetime import UTC, datetime, timedelta

from caching import (
    CacheEntry,
    CacheTTLConfig,
    InMemoryCache,
    calculate_ttl,
    make_cache_key,
    make_observation_key,
)


class TestCacheKey:
    """Test cache key generation"""

    def test_deterministic_key(self):
        """Same inputs produce same key"""
        key1 = make_cache_key(
            field_id="abc123",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sentinel2",
        )
        key2 = make_cache_key(
            field_id="abc123",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sentinel2",
        )

        assert key1 == key2

    def test_different_inputs_different_key(self):
        """Different inputs produce different keys"""
        key1 = make_cache_key(
            field_id="abc123",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sentinel2",
        )
        key2 = make_cache_key(
            field_id="xyz789",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sentinel2",
        )

        assert key1 != key2

    def test_key_length(self):
        """Key is SHA-256 hex (64 chars)"""
        key = make_cache_key(
            field_id="test",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sentinel2",
        )

        assert len(key) == 64

    def test_extra_params_in_key(self):
        """Extra parameters affect key"""
        key1 = make_cache_key(
            field_id="abc123",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sentinel2",
            extra={"bands": ["B04", "B08"]},
        )
        key2 = make_cache_key(
            field_id="abc123",
            start_date="2024-01-01",
            end_date="2024-01-31",
            source="sentinel2",
            extra={"bands": ["B04"]},
        )

        assert key1 != key2


class TestObservationKey:
    """Test observation cache key generation"""

    def test_observation_key_format(self):
        """Observation key is 64 char hex"""
        key = make_observation_key(
            field_id="abc123",
            obs_date="2024-01-15",
            source="sentinel2",
        )

        assert len(key) == 64


class TestInMemoryCache:
    """Test InMemoryCache implementation"""

    def test_set_and_get(self):
        """Basic set and get works"""
        cache = InMemoryCache()
        cache.set("key1", {"value": 42}, ttl_seconds=60)

        result = cache.get("key1")

        assert result == {"value": 42}

    def test_missing_key_returns_none(self):
        """Missing key returns None"""
        cache = InMemoryCache()

        assert cache.get("nonexistent") is None

    def test_expired_entry_returns_none(self):
        """Expired entry returns None"""
        cache = InMemoryCache()
        cache.set("key1", {"value": 42}, ttl_seconds=1)

        # Wait for expiration
        time.sleep(1.1)

        assert cache.get("key1") is None

    def test_delete(self):
        """Delete removes entry"""
        cache = InMemoryCache()
        cache.set("key1", {"value": 42}, ttl_seconds=60)

        assert cache.delete("key1") is True
        assert cache.get("key1") is None

    def test_delete_nonexistent(self):
        """Delete nonexistent returns False"""
        cache = InMemoryCache()

        assert cache.delete("nonexistent") is False

    def test_clear(self):
        """Clear removes all entries"""
        cache = InMemoryCache()
        cache.set("key1", {"value": 1}, ttl_seconds=60)
        cache.set("key2", {"value": 2}, ttl_seconds=60)

        count = cache.clear()

        assert count == 2
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_stats_tracking(self):
        """Statistics are tracked"""
        cache = InMemoryCache()

        # Generate some activity
        cache.set("key1", {"value": 1}, ttl_seconds=60)
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("missing")  # Miss

        stats = cache.stats

        assert stats["sets"] == 1
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["entries"] == 1

    def test_hit_rate_calculation(self):
        """Hit rate is calculated correctly"""
        cache = InMemoryCache()
        cache.set("key1", {"value": 1}, ttl_seconds=60)

        cache.get("key1")  # Hit
        cache.get("missing")  # Miss

        stats = cache.stats
        # 1 hit / (1 hit + 1 miss) = 0.5
        assert stats["hit_rate"] == 0.5


class TestCacheTTL:
    """Test cache TTL calculation"""

    def test_historical_data_long_ttl(self):
        """Data >30 days old gets long TTL"""
        config = CacheTTLConfig()
        old_date = datetime.now(UTC) - timedelta(days=60)

        ttl = calculate_ttl(old_date, config)

        assert ttl == config.historical_ttl

    def test_recent_data_medium_ttl(self):
        """Data 7-30 days old gets medium TTL"""
        config = CacheTTLConfig()
        recent_date = datetime.now(UTC) - timedelta(days=15)

        ttl = calculate_ttl(recent_date, config)

        assert ttl == config.recent_ttl

    def test_current_data_short_ttl(self):
        """Data <7 days old gets short TTL"""
        config = CacheTTLConfig()
        current_date = datetime.now(UTC) - timedelta(days=3)

        ttl = calculate_ttl(current_date, config)

        assert ttl == config.current_ttl


class TestCacheEntry:
    """Test CacheEntry dataclass"""

    def test_is_expired_false_when_fresh(self):
        """Fresh entry is not expired"""
        now = datetime.now(UTC)
        entry = CacheEntry(
            value={"test": 1},
            created_at=now,
            expires_at=now + timedelta(hours=1),
        )

        assert entry.is_expired is False

    def test_is_expired_true_when_old(self):
        """Old entry is expired"""
        now = datetime.now(UTC)
        entry = CacheEntry(
            value={"test": 1},
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
        )

        assert entry.is_expired is True

    def test_age_seconds(self):
        """Age is calculated correctly"""
        now = datetime.now(UTC)
        entry = CacheEntry(
            value={"test": 1},
            created_at=now - timedelta(seconds=30),
            expires_at=now + timedelta(hours=1),
        )

        assert 29 <= entry.age_seconds <= 31
