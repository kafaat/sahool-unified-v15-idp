"""
Tests for Cache Layer - advisory-service
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import time
from unittest.mock import patch

import pytest

from src.cache_layer import (
    AdvisoryCache,
    _generate_cache_key,
    cache_async_result,
    cache_disease_lookup,
    cache_fertilizer_plan,
    cache_crop_requirements,
    get_advisory_cache,
    invalidate_all_caches,
    invalidate_disease_cache,
    invalidate_fertilizer_cache,
    invalidate_crop_cache,
)


class TestAdvisoryCache:
    """Tests for AdvisoryCache class"""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        cache = AdvisoryCache(max_size=100, default_ttl=60)
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_missing_key(self):
        cache = AdvisoryCache()
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        cache = AdvisoryCache(default_ttl=1)
        await cache.set("key1", "value1", ttl=1)
        # Manually expire by manipulating the entry
        key = "key1"
        value, _ = cache._cache[key]
        cache._cache[key] = (value, time.time() - 1)  # Already expired
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        cache = AdvisoryCache(max_size=2, default_ttl=3600)
        await cache.set("a", 1)
        await cache.set("b", 2)
        await cache.set("c", 3)  # Should evict "a"
        assert await cache.get("a") is None
        assert await cache.get("b") == 2
        assert await cache.get("c") == 3

    @pytest.mark.asyncio
    async def test_move_to_end_on_access(self):
        cache = AdvisoryCache(max_size=2, default_ttl=3600)
        await cache.set("a", 1)
        await cache.set("b", 2)
        await cache.get("a")  # Access "a" to make it recent
        await cache.set("c", 3)  # Should evict "b" not "a"
        assert await cache.get("a") == 1
        assert await cache.get("b") is None

    @pytest.mark.asyncio
    async def test_delete(self):
        cache = AdvisoryCache()
        await cache.set("key1", "value1")
        result = await cache.delete("key1")
        assert result is True
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_delete_missing(self):
        cache = AdvisoryCache()
        result = await cache.delete("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_pattern(self):
        cache = AdvisoryCache()
        await cache.set("disease:abc", 1)
        await cache.set("disease:def", 2)
        await cache.set("fertilizer:ghi", 3)
        count = await cache.delete_pattern("disease:")
        assert count == 2
        assert await cache.get("disease:abc") is None
        assert await cache.get("fertilizer:ghi") == 3

    @pytest.mark.asyncio
    async def test_clear(self):
        cache = AdvisoryCache()
        await cache.set("a", 1)
        await cache.set("b", 2)
        count = await cache.clear()
        assert count == 2
        assert await cache.get("a") is None

    def test_get_stats(self):
        cache = AdvisoryCache()
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate_percent"] == 0

    @pytest.mark.asyncio
    async def test_stats_tracking(self):
        cache = AdvisoryCache()
        await cache.set("key1", "val")
        await cache.get("key1")  # hit
        await cache.get("missing")  # miss
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate_percent"] == 50.0


class TestCacheKeyGeneration:
    """Tests for _generate_cache_key function"""

    def test_deterministic(self):
        k1 = _generate_cache_key("func", "a", "b", key="val")
        k2 = _generate_cache_key("func", "a", "b", key="val")
        assert k1 == k2

    def test_different_args_different_keys(self):
        k1 = _generate_cache_key("func", "a")
        k2 = _generate_cache_key("func", "b")
        assert k1 != k2

    def test_key_length(self):
        key = _generate_cache_key("func", "arg1")
        assert len(key) == 32


class TestCacheDecorators:
    """Tests for cache decorators"""

    def test_cache_disease_lookup_decorator(self):
        # Reset global cache
        import src.cache_layer as cl
        cl._advisory_cache = None

        call_count = 0

        @cache_disease_lookup(ttl=3600)
        def lookup_disease(disease_id):
            nonlocal call_count
            call_count += 1
            return {"id": disease_id, "name": "test"}

        result1 = lookup_disease("test_disease")
        result2 = lookup_disease("test_disease")
        assert result1 == result2
        assert call_count == 1  # Second call should be cached

    def test_cache_fertilizer_plan_decorator(self):
        import src.cache_layer as cl
        cl._advisory_cache = None

        call_count = 0

        @cache_fertilizer_plan(ttl=1800)
        def compute_plan(crop, stage):
            nonlocal call_count
            call_count += 1
            return {"crop": crop, "stage": stage}

        result1 = compute_plan("tomato", "vegetative")
        result2 = compute_plan("tomato", "vegetative")
        assert result1 == result2
        assert call_count == 1

    def test_cache_crop_requirements_decorator(self):
        import src.cache_layer as cl
        cl._advisory_cache = None

        call_count = 0

        @cache_crop_requirements(ttl=7200)
        def get_reqs(crop):
            nonlocal call_count
            call_count += 1
            return {"crop": crop}

        result1 = get_reqs("wheat")
        result2 = get_reqs("wheat")
        assert result1 == result2
        assert call_count == 1

    def test_none_result_not_cached(self):
        import src.cache_layer as cl
        cl._advisory_cache = None

        call_count = 0

        @cache_disease_lookup(ttl=3600)
        def lookup_none(x):
            nonlocal call_count
            call_count += 1
            return None

        lookup_none("a")
        lookup_none("a")
        assert call_count == 2  # None should not be cached


class TestCacheAsyncResult:
    """Tests for cache_async_result function"""

    @pytest.mark.asyncio
    async def test_caches_result(self):
        import src.cache_layer as cl
        cl._advisory_cache = None

        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return {"data": "test"}

        result1 = await cache_async_result("test_key", 300, compute)
        result2 = await cache_async_result("test_key", 300, compute)
        assert result1 == result2
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_async_compute_func(self):
        import src.cache_layer as cl
        cl._advisory_cache = None

        async def async_compute():
            return {"async": True}

        result = await cache_async_result("async_key", 300, async_compute)
        assert result == {"async": True}

    @pytest.mark.asyncio
    async def test_none_not_cached(self):
        import src.cache_layer as cl
        cl._advisory_cache = None

        call_count = 0

        def compute_none():
            nonlocal call_count
            call_count += 1
            return None

        await cache_async_result("none_key", 300, compute_none)
        await cache_async_result("none_key", 300, compute_none)
        assert call_count == 2


class TestCacheInvalidation:
    """Tests for cache invalidation functions"""

    @pytest.mark.asyncio
    async def test_invalidate_disease_cache(self):
        import src.cache_layer as cl
        cl._advisory_cache = None
        cache = get_advisory_cache()
        await cache.set("disease:abc", 1)
        await cache.set("disease:def", 2)
        await cache.set("fertilizer:xyz", 3)
        count = await invalidate_disease_cache()
        assert count == 2

    @pytest.mark.asyncio
    async def test_invalidate_fertilizer_cache(self):
        import src.cache_layer as cl
        cl._advisory_cache = None
        cache = get_advisory_cache()
        await cache.set("fertilizer:abc", 1)
        count = await invalidate_fertilizer_cache()
        assert count == 1

    @pytest.mark.asyncio
    async def test_invalidate_crop_cache(self):
        import src.cache_layer as cl
        cl._advisory_cache = None
        cache = get_advisory_cache()
        await cache.set("crop_req:abc", 1)
        count = await invalidate_crop_cache()
        assert count == 1

    @pytest.mark.asyncio
    async def test_invalidate_all_caches(self):
        import src.cache_layer as cl
        cl._advisory_cache = None
        cache = get_advisory_cache()
        await cache.set("disease:a", 1)
        await cache.set("fertilizer:b", 2)
        result = await invalidate_all_caches()
        assert result["total_invalidated"] == 2
        # Stats should be reset
        assert cache._hits == 0
        assert cache._misses == 0
