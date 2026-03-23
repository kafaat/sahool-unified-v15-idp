"""
Unit tests for Task Service Cache Adapter
اختبارات الوحدة لمحول التخزين المؤقت لخدمة المهام

Tests:
- In-memory cache operations
- Cache key generation
- TTL handling
- Astronomical cache specific methods
- Task cache specific methods
"""

import time
from datetime import UTC, datetime, timezone

import pytest

# Import from the src package (conftest.py sets up the path)
try:
    from src.cache import (
        AstronomicalCache,
        CacheAdapter,
        InMemoryCache,
        TaskCache,
    )
except ModuleNotFoundError:
    pytest.skip("Task service src module not found - run tests from service directory", allow_module_level=True)


class TestInMemoryCache:
    """Test InMemoryCache class"""

    def test_set_and_get(self):
        """Test basic set and get operations"""
        cache = InMemoryCache()
        cache.set("key1", "value1")

        assert cache.get("key1") == "value1"

    def test_get_nonexistent(self):
        """Test getting non-existent key returns None"""
        cache = InMemoryCache()

        assert cache.get("nonexistent") is None

    def test_delete(self):
        """Test delete operation"""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        result = cache.delete("key1")

        assert result is True
        assert cache.get("key1") is None

    def test_delete_nonexistent(self):
        """Test deleting non-existent key returns False"""
        cache = InMemoryCache()

        assert cache.delete("nonexistent") is False

    def test_clear(self):
        """Test clear operation"""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size() == 0

    def test_size(self):
        """Test size method"""
        cache = InMemoryCache()
        assert cache.size() == 0

        cache.set("key1", "value1")
        assert cache.size() == 1

        cache.set("key2", "value2")
        assert cache.size() == 2

    def test_max_size_eviction(self):
        """Test that oldest entries are evicted when max size reached"""
        cache = InMemoryCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict key1

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key4") == "value4"
        assert cache.size() == 3

    def test_ttl_expiration(self):
        """Test that expired entries are not returned"""
        cache = InMemoryCache()
        cache.set("key1", "value1", ttl_seconds=1)

        assert cache.get("key1") == "value1"

        time.sleep(1.1)  # Wait for expiration

        assert cache.get("key1") is None

    def test_complex_values(self):
        """Test storing complex values"""
        cache = InMemoryCache()
        complex_value = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }

        cache.set("complex", complex_value)
        result = cache.get("complex")

        assert result == complex_value


class TestCacheAdapter:
    """Test CacheAdapter class"""

    @pytest.mark.asyncio
    async def test_make_key_with_namespace(self):
        """Test key generation with namespace"""
        adapter = CacheAdapter(namespace="test")
        key = adapter._make_key("mykey")

        assert "test" in key
        assert "mykey" in key

    @pytest.mark.asyncio
    async def test_make_key_without_namespace(self):
        """Test key generation without namespace"""
        adapter = CacheAdapter()
        key = adapter._make_key("mykey")

        assert "mykey" in key

    @pytest.mark.asyncio
    async def test_hash_key(self):
        """Test hash key generation"""
        adapter = CacheAdapter()

        hash1 = adapter._hash_key("arg1", "arg2")
        hash2 = adapter._hash_key("arg1", "arg2")
        hash3 = adapter._hash_key("arg1", "arg3")

        assert hash1 == hash2  # Same args = same hash
        assert hash1 != hash3  # Different args = different hash
        assert len(hash1) == 12  # Fixed length

    @pytest.mark.asyncio
    async def test_set_and_get_fallback_to_memory(self):
        """Test set and get with in-memory fallback"""
        adapter = CacheAdapter(namespace="test")

        result = await adapter.set("key1", {"value": 1})
        assert result is True

        value = await adapter.get("key1")
        assert value == {"value": 1}

    @pytest.mark.asyncio
    async def test_delete_fallback_to_memory(self):
        """Test delete with in-memory fallback"""
        adapter = CacheAdapter(namespace="test")

        await adapter.set("key1", "value1")
        result = await adapter.delete("key1")

        assert result is True
        assert await adapter.get("key1") is None

    @pytest.mark.asyncio
    async def test_get_or_set_cache_hit(self):
        """Test get_or_set when value is cached"""
        adapter = CacheAdapter(namespace="test")

        # Pre-populate cache
        await adapter.set("key1", "cached_value")

        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return "computed_value"

        result = await adapter.get_or_set("key1", factory)

        assert result == "cached_value"
        assert call_count == 0  # Factory not called

    @pytest.mark.asyncio
    async def test_get_or_set_cache_miss(self):
        """Test get_or_set when value is not cached"""
        adapter = CacheAdapter(namespace="test_miss")

        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return "computed_value"

        result = await adapter.get_or_set("new_key", factory)

        assert result == "computed_value"
        assert call_count == 1

        # Value should now be cached
        result2 = await adapter.get_or_set("new_key", factory)
        assert result2 == "computed_value"
        assert call_count == 1  # Factory not called again

    @pytest.mark.asyncio
    async def test_get_or_set_with_async_factory(self):
        """Test get_or_set with async factory function"""
        adapter = CacheAdapter(namespace="test_async")

        async def async_factory():
            return "async_value"

        result = await adapter.get_or_set("async_key", async_factory)

        assert result == "async_value"


class TestAstronomicalCache:
    """Test AstronomicalCache class"""

    @pytest.mark.asyncio
    async def test_get_set_best_days(self):
        """Test getting and setting best days cache"""
        cache = AstronomicalCache()

        data = {
            "best_days": [
                {"date": "2024-01-15", "score": 8},
                {"date": "2024-01-18", "score": 9},
            ]
        }

        result = await cache.set_best_days("زراعة", 30, data)
        assert result is True

        cached = await cache.get_best_days("زراعة", 30)
        assert cached == data

    @pytest.mark.asyncio
    async def test_get_nonexistent_best_days(self):
        """Test getting non-existent best days"""
        cache = AstronomicalCache()

        result = await cache.get_best_days("nonexistent", 30)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_set_daily_data(self):
        """Test getting and setting daily astronomical data"""
        cache = AstronomicalCache()

        data = {
            "moon_phase": {"name": "Full Moon"},
            "lunar_mansion": {"name": "Test"},
            "overall_farming_score": 8,
        }

        result = await cache.set_daily_data("2024-01-15", data)
        assert result is True

        cached = await cache.get_daily_data("2024-01-15")
        assert cached == data

    @pytest.mark.asyncio
    async def test_get_set_date_validation(self):
        """Test getting and setting date validation results"""
        cache = AstronomicalCache()

        data = {
            "is_suitable": True,
            "score": 8,
            "recommendation": "Good day for planting",
        }

        result = await cache.set_date_validation("2024-01-15", "زراعة", data)
        assert result is True

        cached = await cache.get_date_validation("2024-01-15", "زراعة")
        assert cached == data


class TestTaskCache:
    """Test TaskCache class"""

    @pytest.mark.asyncio
    async def test_get_set_stats(self):
        """Test getting and setting task statistics"""
        cache = TaskCache()

        stats = {
            "total": 100,
            "pending": 30,
            "completed": 60,
            "cancelled": 10,
        }

        result = await cache.set_stats("tenant_123", stats)
        assert result is True

        cached = await cache.get_stats("tenant_123")
        assert cached == stats

    @pytest.mark.asyncio
    async def test_invalidate_stats(self):
        """Test invalidating task statistics"""
        cache = TaskCache()

        await cache.set_stats("tenant_123", {"total": 100})
        result = await cache.invalidate_stats("tenant_123")

        assert result is True
        assert await cache.get_stats("tenant_123") is None

    @pytest.mark.asyncio
    async def test_get_set_field_health(self):
        """Test getting and setting field health data"""
        cache = TaskCache()

        health_data = {
            "health_score": 7.5,
            "ndvi_mean": 0.65,
            "needs_attention": False,
        }

        result = await cache.set_field_health("field_123", health_data)
        assert result is True

        cached = await cache.get_field_health("field_123")
        assert cached == health_data

    @pytest.mark.asyncio
    async def test_get_set_suggestions(self):
        """Test getting and setting task suggestions"""
        cache = TaskCache()

        suggestions = [
            {"task_type": "irrigation", "priority": "high"},
            {"task_type": "scouting", "priority": "medium"},
        ]

        result = await cache.set_suggestions("field_123", suggestions)
        assert result is True

        cached = await cache.get_suggestions("field_123")
        assert cached == suggestions


class TestCacheSerializationEdgeCases:
    """Test cache serialization edge cases"""

    @pytest.mark.asyncio
    async def test_datetime_serialization(self):
        """Test that datetime objects are serialized properly"""
        adapter = CacheAdapter(namespace="datetime_test")

        data = {
            "timestamp": datetime.now(UTC),
            "date": datetime.now(UTC).date(),
        }

        # Should not raise
        result = await adapter.set("datetime_key", data)
        assert result is True

    @pytest.mark.asyncio
    async def test_non_serializable_value(self):
        """Test handling non-serializable values"""
        adapter = CacheAdapter(namespace="non_serial")

        # Lambdas are not serializable for JSON but in-memory cache
        # stores them directly (just can't serialize for Redis)
        # So this test checks that it doesn't raise and stores in memory
        data = {"func": lambda x: x}

        # In-memory cache can store lambdas (it stores object refs)
        # The set operation returns True for in-memory cache
        result = await adapter.set("lambda_key", data)
        # In-memory cache stores anything, JSON serialization only matters for Redis
        assert result is True

    @pytest.mark.asyncio
    async def test_unicode_values(self):
        """Test handling Unicode values (Arabic text)"""
        adapter = CacheAdapter(namespace="unicode_test")

        data = {
            "title_ar": "مهمة اختبار",
            "description_ar": "هذا وصف المهمة بالعربية",
        }

        result = await adapter.set("arabic_key", data)
        assert result is True

        cached = await adapter.get("arabic_key")
        assert cached == data
