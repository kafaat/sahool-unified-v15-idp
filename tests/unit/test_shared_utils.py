"""
Unit Tests for Shared Utility Functions
Tests caching, pagination, and other utility functions from shared/libs
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.libs.caching import (
    CacheConfig,
    CacheManager,
    InMemoryCache,
    cached,
    get_cache_manager,
    invalidate_field_cache,
    invalidate_tenant_cache,
    invalidate_user_cache,
)
from shared.libs.pagination import (
    Cursor,
    OffsetPage,
    Page,
    PageInfo,
    PaginationHelper,
    SortOrder,
)

# ═══════════════════════════════════════════════════════════════════════════
# Cache Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestCacheConfig:
    """Test CacheConfig class"""

    def test_default_config(self):
        """Test default cache configuration"""
        config = CacheConfig()
        assert config.enabled is True
        assert config.ttl_seconds == 300
        assert config.max_size == 10000
        assert config.key_prefix == "sahool:"

    def test_custom_config(self):
        """Test custom cache configuration"""
        config = CacheConfig(enabled=False, ttl_seconds=600, max_size=5000, key_prefix="test:")
        assert config.enabled is False
        assert config.ttl_seconds == 600
        assert config.max_size == 5000
        assert config.key_prefix == "test:"

    @patch.dict(
        "os.environ",
        {
            "CACHE_ENABLED": "false",
            "CACHE_TTL_SECONDS": "1200",
            "CACHE_MAX_SIZE": "20000",
            "CACHE_KEY_PREFIX": "custom:",
        },
    )
    def test_from_env(self):
        """Test configuration from environment variables"""
        config = CacheConfig.from_env()
        assert config.enabled is False
        assert config.ttl_seconds == 1200
        assert config.max_size == 20000
        assert config.key_prefix == "custom:"


class TestInMemoryCache:
    """Test InMemoryCache class"""

    @pytest.fixture
    def cache(self):
        """Create InMemoryCache instance"""
        return InMemoryCache(max_size=10)

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        """Test setting and getting cache values"""
        await cache.set("key1", "value1")
        value = await cache.get("key1")
        assert value == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key returns None"""
        value = await cache.get("nonexistent")
        assert value is None

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache):
        """Test TTL expiration"""
        await cache.set("key1", "value1", ttl=1)
        value = await cache.get("key1")
        assert value == "value1"

        # Wait for expiration
        await asyncio.sleep(1.1)
        value = await cache.get("key1")
        assert value is None

    @pytest.mark.asyncio
    async def test_delete(self, cache):
        """Test deleting cache entry"""
        await cache.set("key1", "value1")
        await cache.delete("key1")
        value = await cache.get("key1")
        assert value is None

    @pytest.mark.asyncio
    async def test_clear(self, cache):
        """Test clearing entire cache"""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.clear()

        value1 = await cache.get("key1")
        value2 = await cache.get("key2")
        assert value1 is None
        assert value2 is None

    @pytest.mark.asyncio
    async def test_exists(self, cache):
        """Test checking if key exists"""
        await cache.set("key1", "value1")
        exists = await cache.exists("key1")
        assert exists is True

        exists = await cache.exists("nonexistent")
        assert exists is False

    @pytest.mark.asyncio
    async def test_max_size_limit(self, cache):
        """Test cache size limit enforcement"""
        # Fill cache to max
        for i in range(10):
            await cache.set(f"key{i}", f"value{i}")

        # Add one more, should evict oldest
        await cache.set("key10", "value10")

        # First key should be evicted
        value = await cache.get("key0")
        assert value is None

        # Last key should exist
        value = await cache.get("key10")
        assert value == "value10"


class TestCacheManager:
    """Test CacheManager class"""

    @pytest.fixture
    def config(self):
        """Create cache config"""
        return CacheConfig(enabled=True, ttl_seconds=60, max_size=100)

    @pytest.fixture
    def manager(self, config):
        """Create CacheManager instance"""
        return CacheManager(config)

    @pytest.mark.asyncio
    async def test_get_and_set(self, manager):
        """Test cache manager get and set"""
        await manager.set("test_key", {"data": "value"})
        value = await manager.get("test_key")
        assert value == {"data": "value"}

    @pytest.mark.asyncio
    async def test_key_prefix(self, manager):
        """Test key prefix is applied"""
        await manager.set("key1", "value1")
        # Check that prefix is used internally
        assert manager._make_key("key1") == "sahool:key1"

    @pytest.mark.asyncio
    async def test_delete(self, manager):
        """Test cache manager delete"""
        await manager.set("key1", "value1")
        await manager.delete("key1")
        value = await manager.get("key1")
        assert value is None

    @pytest.mark.asyncio
    async def test_clear(self, manager):
        """Test cache manager clear"""
        await manager.set("key1", "value1")
        await manager.set("key2", "value2")
        await manager.clear()

        value1 = await manager.get("key1")
        value2 = await manager.get("key2")
        assert value1 is None
        assert value2 is None

    @pytest.mark.asyncio
    async def test_disabled_cache(self):
        """Test disabled cache returns None"""
        config = CacheConfig(enabled=False)
        manager = CacheManager(config)

        await manager.set("key1", "value1")
        value = await manager.get("key1")
        assert value is None


class TestCacheDecorator:
    """Test @cached decorator"""

    @pytest.mark.asyncio
    async def test_cached_function(self):
        """Test caching function results"""
        call_count = 0

        @cached(key_func=lambda x: f"test:{x}", ttl=60)
        async def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call - cache miss
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call - cache hit
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment

    @pytest.mark.asyncio
    async def test_cached_with_different_args(self):
        """Test caching with different arguments"""
        call_count = 0

        @cached(key_func=lambda x: f"test:{x}")
        async def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = await test_func(5)
        result2 = await test_func(10)

        assert result1 == 10
        assert result2 == 20
        assert call_count == 2  # Both should miss cache


class TestInvalidationHelpers:
    """Test cache invalidation helper functions"""

    @pytest.mark.asyncio
    async def test_invalidate_user_cache(self):
        """Test invalidating user cache"""
        cache = get_cache_manager()
        await cache.set("user:123:profile", {"name": "Test"})
        await invalidate_user_cache("123")
        # After invalidation, key should not exist
        value = await cache.get("user:123:profile")
        assert value is None

    @pytest.mark.asyncio
    async def test_invalidate_field_cache(self):
        """Test invalidating field cache"""
        cache = get_cache_manager()
        await cache.set("field:456:data", {"area": 100})
        await invalidate_field_cache("456")
        value = await cache.get("field:456:data")
        assert value is None

    @pytest.mark.asyncio
    async def test_invalidate_tenant_cache(self):
        """Test invalidating tenant cache"""
        cache = get_cache_manager()
        await cache.set("tenant:789:settings", {"theme": "dark"})
        await invalidate_tenant_cache("789")
        value = await cache.get("tenant:789:settings")
        assert value is None


# ═══════════════════════════════════════════════════════════════════════════
# Pagination Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestCursor:
    """Test Cursor encoding/decoding"""

    def test_encode_decode_string(self):
        """Test encoding and decoding string cursor"""
        value = "test_id_123"
        cursor = Cursor.encode(value)
        decoded = Cursor.decode(cursor)
        assert decoded == value

    def test_encode_decode_number(self):
        """Test encoding and decoding numeric cursor"""
        value = 12345
        cursor = Cursor.encode(value)
        decoded = Cursor.decode(cursor)
        assert decoded == value

    def test_encode_decode_dict(self):
        """Test encoding and decoding dictionary cursor"""
        value = {"id": 123, "timestamp": "2024-01-01"}
        cursor = Cursor.encode(value)
        decoded = Cursor.decode(cursor)
        assert decoded == value

    def test_decode_invalid_cursor(self):
        """Test decoding invalid cursor returns None"""
        decoded = Cursor.decode("invalid_base64!!!")
        assert decoded is None


class TestPageInfo:
    """Test PageInfo dataclass"""

    def test_page_info_creation(self):
        """Test creating PageInfo"""
        page_info = PageInfo(
            has_next_page=True,
            has_previous_page=False,
            start_cursor="cursor1",
            end_cursor="cursor2",
            total_count=100,
        )

        assert page_info.has_next_page is True
        assert page_info.has_previous_page is False
        assert page_info.start_cursor == "cursor1"
        assert page_info.end_cursor == "cursor2"
        assert page_info.total_count == 100


class TestPage:
    """Test Page dataclass"""

    def test_page_creation(self):
        """Test creating Page"""
        items = [{"id": 1}, {"id": 2}]
        page_info = PageInfo(has_next_page=True, has_previous_page=False)
        page = Page(items=items, page_info=page_info)

        assert len(page.items) == 2
        assert page.page_info.has_next_page is True

    def test_page_to_dict(self):
        """Test converting Page to dictionary"""
        items = [{"id": 1}, {"id": 2}]
        page_info = PageInfo(
            has_next_page=True, has_previous_page=False, start_cursor="c1", end_cursor="c2"
        )
        page = Page(items=items, page_info=page_info)

        result = page.to_dict()
        assert "items" in result
        assert "page_info" in result
        assert result["page_info"]["has_next_page"] is True
        assert result["page_info"]["start_cursor"] == "c1"


class TestOffsetPage:
    """Test OffsetPage dataclass"""

    def test_offset_page_creation(self):
        """Test creating OffsetPage"""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        page = OffsetPage(items=items, total=100, page=1, page_size=10, total_pages=10)

        assert len(page.items) == 3
        assert page.total == 100
        assert page.page == 1
        assert page.page_size == 10
        assert page.total_pages == 10

    def test_offset_page_to_dict(self):
        """Test converting OffsetPage to dictionary"""
        items = [{"id": 1}, {"id": 2}]
        page = OffsetPage(items=items, total=50, page=2, page_size=10, total_pages=5)

        result = page.to_dict()
        assert "items" in result
        assert "pagination" in result
        assert result["pagination"]["total"] == 50
        assert result["pagination"]["page"] == 2
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_previous"] is True


class TestPaginationHelper:
    """Test PaginationHelper utilities"""

    def test_get_page_size_default(self):
        """Test getting default page size"""
        size = PaginationHelper.get_page_size(None, default=50)
        assert size == 50

    def test_get_page_size_custom(self):
        """Test getting custom page size"""
        size = PaginationHelper.get_page_size(25, default=50)
        assert size == 25

    def test_get_page_size_max_limit(self):
        """Test page size respects max limit"""
        size = PaginationHelper.get_page_size(2000, default=50, max_size=1000)
        assert size == 1000

    def test_get_page_size_min_limit(self):
        """Test page size respects min limit (1)"""
        size = PaginationHelper.get_page_size(-5, default=50)
        assert size == 1

    def test_calculate_offset(self):
        """Test offset calculation"""
        offset = PaginationHelper.calculate_offset(page=1, page_size=10)
        assert offset == 0

        offset = PaginationHelper.calculate_offset(page=2, page_size=10)
        assert offset == 10

        offset = PaginationHelper.calculate_offset(page=5, page_size=20)
        assert offset == 80

    def test_calculate_total_pages(self):
        """Test total pages calculation"""
        total_pages = PaginationHelper.calculate_total_pages(total_items=100, page_size=10)
        assert total_pages == 10

        total_pages = PaginationHelper.calculate_total_pages(total_items=105, page_size=10)
        assert total_pages == 11

        total_pages = PaginationHelper.calculate_total_pages(total_items=0, page_size=10)
        assert total_pages == 0

    def test_calculate_total_pages_edge_case(self):
        """Test total pages calculation with zero page size"""
        total_pages = PaginationHelper.calculate_total_pages(total_items=100, page_size=0)
        assert total_pages == 0


class TestSortOrder:
    """Test SortOrder enum"""

    def test_sort_order_values(self):
        """Test SortOrder enum values"""
        assert SortOrder.ASC.value == "asc"
        assert SortOrder.DESC.value == "desc"


# ═══════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestCachePaginationIntegration:
    """Test integration between caching and pagination"""

    @pytest.mark.asyncio
    async def test_cache_paginated_results(self):
        """Test caching paginated results"""
        cache = get_cache_manager()

        # Create paginated data
        items = [{"id": i} for i in range(10)]
        page = OffsetPage(items=items, total=100, page=1, page_size=10, total_pages=10)

        # Cache the page
        cache_key = "page:1:10"
        await cache.set(cache_key, page.to_dict())

        # Retrieve from cache
        cached_page = await cache.get(cache_key)
        assert cached_page["pagination"]["total"] == 100
        assert len(cached_page["items"]) == 10
