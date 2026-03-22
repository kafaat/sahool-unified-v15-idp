"""
Extended tests for src/cache.py
"""

import time
from unittest.mock import AsyncMock

import pytest

from src.cache import (
    AstronomicalCache,
    CacheAdapter,
    InMemoryCache,
    TaskCache,
    close_redis,
)


class TestInMemoryCache:
    def test_get_nonexistent(self):
        cache = InMemoryCache()
        assert cache.get("missing") is None

    def test_set_and_get(self):
        cache = InMemoryCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_ttl_expiry(self):
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl_seconds=0)
        time.sleep(0.01)
        assert cache.get("key1") is None

    def test_delete_existing(self):
        cache = InMemoryCache()
        cache.set("key1", "value1")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None

    def test_delete_nonexistent(self):
        cache = InMemoryCache()
        assert cache.delete("missing") is False

    def test_clear(self):
        cache = InMemoryCache()
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.size() == 0

    def test_size(self):
        cache = InMemoryCache()
        assert cache.size() == 0
        cache.set("k1", "v1")
        assert cache.size() == 1

    def test_max_size_eviction(self):
        cache = InMemoryCache(max_size=3)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        cache.set("k4", "v4")
        assert cache.size() == 3
        assert cache.get("k1") is None
        assert cache.get("k4") == "v4"

    def test_evict_expired(self):
        cache = InMemoryCache()
        cache.set("k1", "v1", ttl_seconds=0)
        time.sleep(0.01)
        cache.set("k2", "v2", ttl_seconds=3600)
        evicted = cache._evict_expired()
        assert evicted == 1

    def test_overwrite_value(self):
        cache = InMemoryCache()
        cache.set("k1", "v1")
        cache.set("k1", "v2")
        assert cache.get("k1") == "v2"

    def test_complex_values(self):
        cache = InMemoryCache()
        data = {"nested": [1, 2, {"key": "val"}]}
        cache.set("complex", data)
        assert cache.get("complex") == data


class TestCacheAdapter:
    @pytest.fixture(autouse=True)
    def reset_redis(self):
        import src.cache as cache_module
        old_client = cache_module._redis_client
        old_available = cache_module._redis_available
        cache_module._redis_client = None
        cache_module._redis_available = False
        cache_module._memory_cache.clear()
        yield
        cache_module._redis_client = old_client
        cache_module._redis_available = old_available

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        adapter = CacheAdapter(namespace="test")
        await adapter.set("key1", {"data": "value"})
        result = await adapter.get("key1")
        assert result == {"data": "value"}

    @pytest.mark.asyncio
    async def test_get_missing(self):
        adapter = CacheAdapter(namespace="test")
        assert await adapter.get("nonexistent") is None

    @pytest.mark.asyncio
    async def test_delete(self):
        adapter = CacheAdapter(namespace="test")
        await adapter.set("key1", "val")
        assert await adapter.delete("key1") is True
        assert await adapter.get("key1") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        adapter = CacheAdapter(namespace="test")
        assert await adapter.delete("missing") is False

    @pytest.mark.asyncio
    async def test_make_key(self):
        adapter = CacheAdapter(namespace="myns")
        key = adapter._make_key("mykey")
        assert "myns" in key and "mykey" in key

    @pytest.mark.asyncio
    async def test_hash_key(self):
        adapter = CacheAdapter()
        h1 = adapter._hash_key("a", "b")
        h2 = adapter._hash_key("a", "b")
        h3 = adapter._hash_key("c", "d")
        assert h1 == h2
        assert h1 != h3
        assert len(h1) == 12

    @pytest.mark.asyncio
    async def test_get_or_set_cached(self):
        adapter = CacheAdapter(namespace="test")
        await adapter.set("key1", "cached_val")
        result = await adapter.get_or_set("key1", lambda: "new_val")
        assert result == "cached_val"

    @pytest.mark.asyncio
    async def test_get_or_set_factory(self):
        adapter = CacheAdapter(namespace="test")
        result = await adapter.get_or_set("key1", lambda: "computed")
        assert result == "computed"
        assert await adapter.get("key1") == "computed"

    @pytest.mark.asyncio
    async def test_get_or_set_async_factory(self):
        adapter = CacheAdapter(namespace="test")

        async def async_factory():
            return "async_result"

        result = await adapter.get_or_set("key1", async_factory)
        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_get_or_set_static_value(self):
        adapter = CacheAdapter(namespace="test")
        result = await adapter.get_or_set("key1", "static_val")
        assert result == "static_val"

    @pytest.mark.asyncio
    async def test_clear_namespace(self):
        adapter = CacheAdapter(namespace="test")
        await adapter.set("k1", "v1")
        count = await adapter.clear_namespace()
        assert count >= 0

    @pytest.mark.asyncio
    async def test_serialization_fallback(self):
        """json.dumps with default=str converts any object to string, so set always succeeds."""
        adapter = CacheAdapter(namespace="test")

        class Bad:
            pass

        result = await adapter.set("key1", Bad())
        assert result is True  # default=str makes serialization always succeed


class TestAstronomicalCache:
    @pytest.fixture(autouse=True)
    def reset_redis(self):
        import src.cache as cache_module
        cache_module._redis_client = None
        cache_module._redis_available = False
        cache_module._memory_cache.clear()
        yield

    @pytest.mark.asyncio
    async def test_best_days_set_and_get(self):
        cache = AstronomicalCache()
        data = {"best_days": [{"date": "2024-01-15", "score": 9}]}
        await cache.set_best_days("irrigation", 30, data)
        result = await cache.get_best_days("irrigation", 30)
        assert result == data

    @pytest.mark.asyncio
    async def test_best_days_miss(self):
        cache = AstronomicalCache()
        assert await cache.get_best_days("x", 30) is None

    @pytest.mark.asyncio
    async def test_daily_data_set_and_get(self):
        cache = AstronomicalCache()
        data = {"moon_phase": {"name": "Full Moon"}}
        await cache.set_daily_data("2024-01-15", data)
        assert await cache.get_daily_data("2024-01-15") == data

    @pytest.mark.asyncio
    async def test_daily_data_miss(self):
        cache = AstronomicalCache()
        assert await cache.get_daily_data("2024-01-01") is None

    @pytest.mark.asyncio
    async def test_date_validation_set_and_get(self):
        cache = AstronomicalCache()
        data = {"is_suitable": True, "score": 8}
        await cache.set_date_validation("2024-01-15", "planting", data)
        assert await cache.get_date_validation("2024-01-15", "planting") == data

    @pytest.mark.asyncio
    async def test_date_validation_miss(self):
        cache = AstronomicalCache()
        assert await cache.get_date_validation("2024-01-01", "x") is None

    @pytest.mark.asyncio
    async def test_clear(self):
        cache = AstronomicalCache()
        await cache.set_best_days("x", 30, {"data": True})
        count = await cache.clear()
        assert count >= 0


class TestTaskCache:
    @pytest.fixture(autouse=True)
    def reset_redis(self):
        import src.cache as cache_module
        cache_module._redis_client = None
        cache_module._redis_available = False
        cache_module._memory_cache.clear()
        yield

    @pytest.mark.asyncio
    async def test_stats_set_and_get(self):
        cache = TaskCache()
        await cache.set_stats("t1", {"total": 10})
        assert await cache.get_stats("t1") == {"total": 10}

    @pytest.mark.asyncio
    async def test_stats_miss(self):
        cache = TaskCache()
        assert await cache.get_stats("x") is None

    @pytest.mark.asyncio
    async def test_invalidate_stats(self):
        cache = TaskCache()
        await cache.set_stats("t1", {"total": 10})
        assert await cache.invalidate_stats("t1") is True
        assert await cache.get_stats("t1") is None

    @pytest.mark.asyncio
    async def test_field_health(self):
        cache = TaskCache()
        await cache.set_field_health("f1", {"ndvi": 0.72})
        assert await cache.get_field_health("f1") == {"ndvi": 0.72}

    @pytest.mark.asyncio
    async def test_suggestions(self):
        cache = TaskCache()
        await cache.set_suggestions("f1", [{"type": "irrigation"}])
        assert await cache.get_suggestions("f1") == [{"type": "irrigation"}]

    @pytest.mark.asyncio
    async def test_clear(self):
        cache = TaskCache()
        await cache.set_stats("t1", {"total": 5})
        count = await cache.clear()
        assert count >= 0


class TestCloseRedis:
    @pytest.mark.asyncio
    async def test_close_when_no_client(self):
        import src.cache as cache_module
        cache_module._redis_client = None
        cache_module._redis_available = False
        await close_redis()

    @pytest.mark.asyncio
    async def test_close_with_mock_client(self):
        import src.cache as cache_module
        mock_client = AsyncMock()
        cache_module._redis_client = mock_client
        cache_module._redis_available = True
        await close_redis()
        mock_client.close.assert_called_once()
        assert cache_module._redis_client is None

    @pytest.mark.asyncio
    async def test_close_handles_error(self):
        import src.cache as cache_module
        mock_client = AsyncMock()
        mock_client.close.side_effect = Exception("fail")
        cache_module._redis_client = mock_client
        cache_module._redis_available = True
        await close_redis()
        assert cache_module._redis_client is None
