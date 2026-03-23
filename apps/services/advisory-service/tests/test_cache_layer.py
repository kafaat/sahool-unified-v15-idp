"""
Cache Layer Tests - Advisory Service
Tests for AdvisoryCache, decorators, and invalidation helpers.
"""

import time

import pytest

try:
    from src.cache_layer import (
        AdvisoryCache,
        _generate_cache_key,
        cache_async_result,
        cache_crop_requirements,
        cache_disease_lookup,
        cache_fertilizer_plan,
        get_advisory_cache,
        invalidate_all_caches,
        invalidate_crop_cache,
        invalidate_disease_cache,
        invalidate_fertilizer_cache,
    )
except ImportError:
    pytest.skip("advisory-service dependencies not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# AdvisoryCache core
# ---------------------------------------------------------------------------


class TestAdvisoryCache:
    """Test the in-memory cache."""

    @pytest.fixture
    def cache(self):
        return AdvisoryCache(max_size=10, default_ttl=60)

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_missing_key(self, cache):
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_ttl_expiry(self, cache):
        # Set with a very short TTL and manually expire
        await cache.set("key1", "value1", ttl=1)
        # Manually set expiry to the past
        cache._cache["key1"] = (cache._cache["key1"][0], time.time() - 1)
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_existing(self, cache):
        await cache.set("key1", "value1")
        deleted = await cache.delete("key1")
        assert deleted is True
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, cache):
        deleted = await cache.delete("nonexistent")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_delete_pattern(self, cache):
        await cache.set("disease:1", "v1")
        await cache.set("disease:2", "v2")
        await cache.set("fertilizer:1", "v3")
        count = await cache.delete_pattern("disease:")
        assert count == 2
        assert await cache.get("disease:1") is None
        assert await cache.get("fertilizer:1") == "v3"

    @pytest.mark.asyncio
    async def test_clear(self, cache):
        await cache.set("a", 1)
        await cache.set("b", 2)
        count = await cache.clear()
        assert count == 2
        assert await cache.get("a") is None

    @pytest.mark.asyncio
    async def test_eviction_at_capacity(self, cache):
        """When at max_size, oldest entries should be evicted."""
        for i in range(10):
            await cache.set(f"key{i}", f"val{i}")
        # Cache is full (10). Adding one more should evict the oldest.
        await cache.set("key10", "val10")
        # key0 should have been evicted
        assert await cache.get("key0") is None
        assert await cache.get("key10") == "val10"

    @pytest.mark.asyncio
    async def test_lru_order(self, cache):
        """Accessed keys should move to end, surviving eviction."""
        for i in range(10):
            await cache.set(f"key{i}", f"val{i}")
        # Access key0 to move it to end
        await cache.get("key0")
        # Now add a new key, key1 should be evicted (oldest not-accessed)
        await cache.set("key10", "val10")
        assert await cache.get("key0") == "val0"  # survived
        assert await cache.get("key1") is None  # evicted

    def test_get_stats_initial(self, cache):
        stats = cache.get_stats()
        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate_percent"] == 0

    @pytest.mark.asyncio
    async def test_get_stats_after_operations(self, cache):
        await cache.set("k", "v")
        await cache.get("k")  # hit
        await cache.get("miss")  # miss
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate_percent"] == 50.0


# ---------------------------------------------------------------------------
# Cache key generation
# ---------------------------------------------------------------------------


class TestGenerateCacheKey:
    def test_same_inputs_same_key(self):
        k1 = _generate_cache_key("func", "arg1", x=1)
        k2 = _generate_cache_key("func", "arg1", x=1)
        assert k1 == k2

    def test_different_inputs_different_key(self):
        k1 = _generate_cache_key("func", "arg1")
        k2 = _generate_cache_key("func", "arg2")
        assert k1 != k2

    def test_key_is_32_chars(self):
        k = _generate_cache_key("f", "a")
        assert len(k) == 32


# ---------------------------------------------------------------------------
# get_advisory_cache singleton
# ---------------------------------------------------------------------------


class TestGetAdvisoryCache:
    def test_returns_cache_instance(self):
        import src.cache_layer as cl

        cl._advisory_cache = None
        cache = get_advisory_cache()
        assert isinstance(cache, AdvisoryCache)
        cl._advisory_cache = None  # cleanup

    def test_returns_same_instance(self):
        import src.cache_layer as cl

        cl._advisory_cache = None
        c1 = get_advisory_cache()
        c2 = get_advisory_cache()
        assert c1 is c2
        cl._advisory_cache = None


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------


class TestCacheDecorators:
    def setup_method(self):
        import src.cache_layer as cl

        cl._advisory_cache = None

    def teardown_method(self):
        import src.cache_layer as cl

        cl._advisory_cache = None

    def test_cache_disease_lookup_caches(self):
        call_count = 0

        @cache_disease_lookup(ttl=60)
        def lookup(disease_id):
            nonlocal call_count
            call_count += 1
            return {"id": disease_id}

        r1 = lookup("d1")
        r2 = lookup("d1")
        assert r1 == {"id": "d1"}
        assert r2 == {"id": "d1"}
        assert call_count == 1  # second call from cache

    def test_cache_disease_lookup_none_not_cached(self):
        call_count = 0

        @cache_disease_lookup(ttl=60)
        def lookup(disease_id):
            nonlocal call_count
            call_count += 1
            return None

        lookup("d1")
        lookup("d1")
        assert call_count == 2  # None not cached

    def test_cache_fertilizer_plan_caches(self):
        call_count = 0

        @cache_fertilizer_plan(ttl=60)
        def plan(crop, stage):
            nonlocal call_count
            call_count += 1
            return {"crop": crop, "stage": stage}

        r1 = plan("tomato", "vegetative")
        r2 = plan("tomato", "vegetative")
        assert r1 == r2
        assert call_count == 1

    def test_cache_crop_requirements_caches(self):
        call_count = 0

        @cache_crop_requirements(ttl=60)
        def reqs(crop):
            nonlocal call_count
            call_count += 1
            return {"crop": crop}

        reqs("wheat")
        reqs("wheat")
        assert call_count == 1

    def test_cache_decorator_expired_entry(self):
        call_count = 0

        @cache_disease_lookup(ttl=0)  # expires immediately
        def lookup(disease_id):
            nonlocal call_count
            call_count += 1
            return {"id": disease_id}

        lookup("d1")
        # Entry is expired, should re-compute
        lookup("d1")
        assert call_count == 2


# ---------------------------------------------------------------------------
# cache_async_result
# ---------------------------------------------------------------------------


class TestCacheAsyncResult:
    def setup_method(self):
        import src.cache_layer as cl

        cl._advisory_cache = None

    def teardown_method(self):
        import src.cache_layer as cl

        cl._advisory_cache = None

    @pytest.mark.asyncio
    async def test_caches_sync_func(self):
        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return 42

        r1 = await cache_async_result("k1", 60, compute)
        r2 = await cache_async_result("k1", 60, compute)
        assert r1 == 42
        assert r2 == 42
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_caches_async_func(self):
        call_count = 0

        async def compute():
            nonlocal call_count
            call_count += 1
            return "async_val"

        r1 = await cache_async_result("k2", 60, compute)
        r2 = await cache_async_result("k2", 60, compute)
        assert r1 == "async_val"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_none_not_cached(self):
        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return None

        await cache_async_result("k3", 60, compute)
        await cache_async_result("k3", 60, compute)
        assert call_count == 2


# ---------------------------------------------------------------------------
# Invalidation helpers
# ---------------------------------------------------------------------------


class TestInvalidation:
    def setup_method(self):
        import src.cache_layer as cl

        cl._advisory_cache = None

    def teardown_method(self):
        import src.cache_layer as cl

        cl._advisory_cache = None

    @pytest.mark.asyncio
    async def test_invalidate_disease_cache(self):
        cache = get_advisory_cache()
        await cache.set("disease:abc", "v1")
        await cache.set("disease:def", "v2")
        await cache.set("fertilizer:xyz", "v3")
        count = await invalidate_disease_cache()
        assert count == 2
        assert await cache.get("fertilizer:xyz") == "v3"

    @pytest.mark.asyncio
    async def test_invalidate_fertilizer_cache(self):
        cache = get_advisory_cache()
        await cache.set("fertilizer:abc", "v1")
        count = await invalidate_fertilizer_cache()
        assert count == 1

    @pytest.mark.asyncio
    async def test_invalidate_crop_cache(self):
        cache = get_advisory_cache()
        await cache.set("crop_req:abc", "v1")
        count = await invalidate_crop_cache()
        assert count == 1

    @pytest.mark.asyncio
    async def test_invalidate_all_caches(self):
        cache = get_advisory_cache()
        await cache.set("disease:1", "v1")
        await cache.set("fertilizer:1", "v2")
        await cache.set("crop_req:1", "v3")
        result = await invalidate_all_caches()
        assert result["total_invalidated"] == 3
        assert cache._hits == 0
        assert cache._misses == 0
