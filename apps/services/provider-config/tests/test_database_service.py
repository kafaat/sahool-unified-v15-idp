"""
Tests for provider-config database_service.py
اختبارات خدمة قاعدة البيانات لتكوين المزودين
"""

import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.database_service import CacheManager, ProviderConfigService


# ═══════════════════════════════════════════════════════════════════════════════
# CACHE MANAGER TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestCacheManagerInit:
    """Tests for CacheManager initialization"""

    def test_init_stores_config(self):
        """Test that CacheManager stores redis_url and cache_ttl"""
        cm = CacheManager("redis://localhost:6379/0", cache_ttl=600)
        assert cm._redis_url == "redis://localhost:6379/0"
        assert cm.cache_ttl == 600
        assert cm.redis_client is None

    def test_init_default_ttl(self):
        """Test default cache TTL is 300 seconds"""
        cm = CacheManager("redis://localhost:6379/0")
        assert cm.cache_ttl == 300


class TestCacheManagerGetKey:
    """Tests for CacheManager._get_key"""

    def test_get_key_with_provider_type(self):
        """Test key generation with provider type"""
        cm = CacheManager("redis://localhost:6379/0")
        key = cm._get_key("tenant-001", "map")
        assert key == "provider_config:tenant-001:map"

    def test_get_key_without_provider_type(self):
        """Test key generation without provider type"""
        cm = CacheManager("redis://localhost:6379/0")
        key = cm._get_key("tenant-001")
        assert key == "provider_config:tenant-001:all"

    def test_get_key_none_provider_type(self):
        """Test key generation with None provider type"""
        cm = CacheManager("redis://localhost:6379/0")
        key = cm._get_key("tenant-001", None)
        assert key == "provider_config:tenant-001:all"


class TestCacheManagerInitialize:
    """Tests for CacheManager.initialize"""

    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful Redis connection"""
        cm = CacheManager("redis://localhost:6379/0")

        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)

        with patch("src.database_service.aioredis.from_url", return_value=mock_redis):
            await cm.initialize()

        assert cm.redis_client == mock_redis
        mock_redis.ping.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_initialize_failure_sets_client_none(self):
        """Test that failed Redis connection sets client to None"""
        cm = CacheManager("redis://localhost:6379/0")

        with patch("src.database_service.aioredis.from_url", side_effect=ConnectionError("refused")):
            await cm.initialize()

        assert cm.redis_client is None


class TestCacheManagerClose:
    """Tests for CacheManager.close"""

    @pytest.mark.asyncio
    async def test_close_with_client(self):
        """Test closing an active Redis connection"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()

        await cm.close()

        assert cm.redis_client is None

    @pytest.mark.asyncio
    async def test_close_without_client(self):
        """Test closing when no client is connected"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = None
        await cm.close()  # Should not raise


class TestCacheManagerGet:
    """Tests for CacheManager.get"""

    @pytest.mark.asyncio
    async def test_get_returns_none_when_no_client(self):
        """Test get returns None when Redis is not connected"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = None
        result = await cm.get("tenant-001", "map")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_cache_hit(self):
        """Test get returns parsed JSON on cache hit"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()
        cached_data = [{"provider_name": "osm", "enabled": True}]
        cm.redis_client.get = AsyncMock(return_value=json.dumps(cached_data))

        result = await cm.get("tenant-001", "map")
        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_cache_miss(self):
        """Test get returns None on cache miss"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()
        cm.redis_client.get = AsyncMock(return_value=None)

        result = await cm.get("tenant-001", "map")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_redis_error(self):
        """Test get returns None on Redis error"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()
        cm.redis_client.get = AsyncMock(side_effect=Exception("Redis down"))

        result = await cm.get("tenant-001", "map")
        assert result is None


class TestCacheManagerSet:
    """Tests for CacheManager.set"""

    @pytest.mark.asyncio
    async def test_set_returns_false_when_no_client(self):
        """Test set returns False when Redis is not connected"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = None
        result = await cm.set("tenant-001", {"data": "test"})
        assert result is False

    @pytest.mark.asyncio
    async def test_set_success(self):
        """Test successful cache set"""
        cm = CacheManager("redis://localhost:6379/0", cache_ttl=120)
        cm.redis_client = AsyncMock()
        cm.redis_client.setex = AsyncMock()

        result = await cm.set("tenant-001", {"data": "test"}, "map")
        assert result is True
        cm.redis_client.setex.assert_awaited_once_with(
            "provider_config:tenant-001:map",
            120,
            json.dumps({"data": "test"}),
        )

    @pytest.mark.asyncio
    async def test_set_handles_redis_error(self):
        """Test set returns False on Redis error"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()
        cm.redis_client.setex = AsyncMock(side_effect=Exception("Redis error"))

        result = await cm.set("tenant-001", {"data": "test"})
        assert result is False


class TestCacheManagerInvalidate:
    """Tests for CacheManager.invalidate"""

    @pytest.mark.asyncio
    async def test_invalidate_no_client(self):
        """Test invalidate does nothing when no client"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = None
        await cm.invalidate("tenant-001")  # Should not raise

    @pytest.mark.asyncio
    async def test_invalidate_specific_provider_type(self):
        """Test invalidating a specific provider type key"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()
        cm.redis_client.delete = AsyncMock()

        await cm.invalidate("tenant-001", "map")

        cm.redis_client.delete.assert_awaited_once_with("provider_config:tenant-001:map")

    @pytest.mark.asyncio
    async def test_invalidate_all_provider_types(self):
        """Test invalidating all keys for a tenant using SCAN"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()
        # Simulate SCAN returning keys then finishing
        cm.redis_client.scan = AsyncMock(
            return_value=(0, ["provider_config:tenant-001:map", "provider_config:tenant-001:weather"])
        )
        cm.redis_client.delete = AsyncMock()

        await cm.invalidate("tenant-001")

        cm.redis_client.scan.assert_awaited_once()
        cm.redis_client.delete.assert_awaited_once_with(
            "provider_config:tenant-001:map",
            "provider_config:tenant-001:weather",
        )

    @pytest.mark.asyncio
    async def test_invalidate_scan_no_keys(self):
        """Test invalidation when SCAN returns no keys"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()
        cm.redis_client.scan = AsyncMock(return_value=(0, []))

        await cm.invalidate("tenant-001")
        cm.redis_client.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_invalidate_handles_redis_error(self):
        """Test invalidation handles Redis errors gracefully"""
        cm = CacheManager("redis://localhost:6379/0")
        cm.redis_client = AsyncMock()
        cm.redis_client.scan = AsyncMock(side_effect=Exception("Redis error"))

        await cm.invalidate("tenant-001")  # Should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# PROVIDER CONFIG SERVICE TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestProviderConfigServiceCreate:
    """Tests for ProviderConfigService.create_config"""

    def _make_service(self):
        mock_db = MagicMock()
        mock_cache = MagicMock()
        # Make cache.invalidate a coroutine-like (it's called without await in create_config)
        mock_cache.invalidate = MagicMock()
        return ProviderConfigService(mock_db, mock_cache), mock_db, mock_cache

    def test_create_config_success(self):
        """Test successful config creation"""
        from src.models import ProviderConfig

        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        result = service.create_config(
            session=mock_session,
            tenant_id="tenant-001",
            provider_type="map",
            provider_name="openstreetmap",
            priority="primary",
            enabled=True,
            created_by="admin",
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        mock_cache.invalidate.assert_called_once_with("tenant-001", "map")

    def test_create_config_integrity_error(self):
        """Test duplicate config raises ValueError"""
        from sqlalchemy.exc import IntegrityError

        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()
        mock_session.commit.side_effect = IntegrityError("dup", {}, None)

        with pytest.raises(ValueError, match="Configuration already exists"):
            service.create_config(
                session=mock_session,
                tenant_id="tenant-001",
                provider_type="map",
                provider_name="openstreetmap",
            )
        mock_session.rollback.assert_called_once()

    def test_create_config_generic_error(self):
        """Test generic error during creation"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()
        mock_session.commit.side_effect = RuntimeError("DB down")

        with pytest.raises(RuntimeError):
            service.create_config(
                session=mock_session,
                tenant_id="tenant-001",
                provider_type="map",
                provider_name="openstreetmap",
            )
        mock_session.rollback.assert_called_once()


class TestProviderConfigServiceRead:
    """Tests for ProviderConfigService read methods"""

    def _make_service(self):
        mock_db = MagicMock()
        mock_cache = MagicMock()
        mock_cache.get = MagicMock(return_value=None)
        mock_cache.set = MagicMock()
        return ProviderConfigService(mock_db, mock_cache), mock_db, mock_cache

    def test_get_tenant_configs_cache_hit(self):
        """Test that cached results are returned directly"""
        service, mock_db, mock_cache = self._make_service()
        cached = [{"provider_name": "osm"}]
        mock_cache.get = MagicMock(return_value=cached)
        mock_session = MagicMock()

        result = service.get_tenant_configs(mock_session, "tenant-001", "map")
        assert result == cached
        # Should not query the database
        mock_session.query.assert_not_called()

    def test_get_tenant_configs_cache_miss(self):
        """Test database query on cache miss"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_config = MagicMock()
        mock_config.to_dict.return_value = {"provider_name": "osm"}
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_config]
        mock_session.query.return_value = mock_query

        result = service.get_tenant_configs(mock_session, "tenant-001", "map")
        assert result == [mock_config]
        mock_cache.set.assert_called_once()

    def test_get_tenant_configs_no_provider_type_filter(self):
        """Test get_tenant_configs without provider_type"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query

        service.get_tenant_configs(mock_session, "tenant-001")
        # filter is called once (for tenant_id only)
        assert mock_query.filter.call_count == 1

    def test_get_config_by_name(self):
        """Test getting a specific provider config by name"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_config = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_config
        mock_session.query.return_value = mock_query

        result = service.get_config_by_name(mock_session, "tenant-001", "map", "openstreetmap")
        assert result == mock_config

    def test_get_config_by_name_not_found(self):
        """Test get_config_by_name returns None when not found"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query

        result = service.get_config_by_name(mock_session, "tenant-001", "map", "nonexistent")
        assert result is None

    def test_get_enabled_providers(self):
        """Test getting enabled providers ordered by priority"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_config = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_config]
        mock_session.query.return_value = mock_query

        result = service.get_enabled_providers(mock_session, "tenant-001", "map")
        assert result == [mock_config]


class TestProviderConfigServiceUpdate:
    """Tests for ProviderConfigService.update_config"""

    def _make_service(self):
        mock_db = MagicMock()
        mock_cache = MagicMock()
        mock_cache.invalidate = MagicMock()
        return ProviderConfigService(mock_db, mock_cache), mock_db, mock_cache

    def test_update_config_success(self):
        """Test successful config update"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_config = MagicMock()
        mock_config.tenant_id = "tenant-001"
        mock_config.provider_type = "map"

        with patch.object(service, "get_config_by_name", return_value=mock_config):
            result = service.update_config(
                mock_session,
                "tenant-001",
                "map",
                "openstreetmap",
                api_key="new-key",
                priority="secondary",
                enabled=False,
                config_data={"foo": "bar"},
                updated_by="admin",
            )

        assert result is not None
        assert mock_config.api_key == "new-key"
        assert mock_config.priority == "secondary"
        assert mock_config.enabled is False
        assert mock_config.config_data == {"foo": "bar"}
        assert mock_config.updated_by == "admin"
        mock_session.commit.assert_called_once()
        mock_cache.invalidate.assert_called_once()

    def test_update_config_not_found(self):
        """Test update returns None when config not found"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        with patch.object(service, "get_config_by_name", return_value=None):
            result = service.update_config(mock_session, "t", "map", "x")

        assert result is None

    def test_update_config_partial_update(self):
        """Test that None values are not applied"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_config = MagicMock()
        mock_config.api_key = "old-key"
        mock_config.priority = "primary"

        with patch.object(service, "get_config_by_name", return_value=mock_config):
            service.update_config(
                mock_session,
                "t",
                "map",
                "osm",
                api_key=None,  # Should not change
                priority="secondary",
            )

        # api_key should not have been overwritten since we passed None
        assert mock_config.api_key == "old-key"
        assert mock_config.priority == "secondary"

    def test_update_config_error_rollback(self):
        """Test update rolls back on error"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_config = MagicMock()
        with patch.object(service, "get_config_by_name", return_value=mock_config):
            mock_session.commit.side_effect = RuntimeError("DB error")
            with pytest.raises(RuntimeError):
                service.update_config(mock_session, "t", "map", "osm", priority="secondary")

        mock_session.rollback.assert_called_once()


class TestProviderConfigServiceDelete:
    """Tests for ProviderConfigService.delete_config"""

    def _make_service(self):
        mock_db = MagicMock()
        mock_cache = MagicMock()
        mock_cache.invalidate = MagicMock()
        return ProviderConfigService(mock_db, mock_cache), mock_db, mock_cache

    def test_delete_config_success(self):
        """Test successful config deletion"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()
        mock_config = MagicMock()

        with patch.object(service, "get_config_by_name", return_value=mock_config):
            result = service.delete_config(mock_session, "tenant-001", "map", "openstreetmap")

        assert result is True
        mock_session.delete.assert_called_once_with(mock_config)
        mock_session.commit.assert_called_once()

    def test_delete_config_not_found(self):
        """Test delete returns False when config not found"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        with patch.object(service, "get_config_by_name", return_value=None):
            result = service.delete_config(mock_session, "t", "map", "nonexistent")

        assert result is False

    def test_delete_config_error_rollback(self):
        """Test delete rolls back on error"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()
        mock_config = MagicMock()

        with patch.object(service, "get_config_by_name", return_value=mock_config):
            mock_session.commit.side_effect = RuntimeError("DB error")
            with pytest.raises(RuntimeError):
                service.delete_config(mock_session, "t", "map", "osm")

        mock_session.rollback.assert_called_once()


class TestProviderConfigServiceHistory:
    """Tests for ProviderConfigService version history methods"""

    def _make_service(self):
        mock_db = MagicMock()
        mock_cache = MagicMock()
        mock_cache.invalidate = MagicMock()
        return ProviderConfigService(mock_db, mock_cache), mock_db, mock_cache

    def test_get_config_history(self):
        """Test get_config_history queries correctly"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query

        result = service.get_config_history(mock_session, "tenant-001", "map", 50)
        assert result == []

    def test_get_config_history_no_provider_type(self):
        """Test get_config_history without provider_type filter"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query

        service.get_config_history(mock_session, "tenant-001", None, 100)
        # filter should be called once for tenant_id only
        assert mock_query.filter.call_count == 1

    def test_get_config_version(self):
        """Test get_config_version returns specific version"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_version = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_version
        mock_session.query.return_value = mock_query

        result = service.get_config_version(mock_session, "config-id", 2)
        assert result == mock_version

    def test_rollback_to_version_success(self):
        """Test successful version rollback"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_version = MagicMock()
        mock_version.api_key = "old-key"
        mock_version.api_secret = "old-secret"
        mock_version.priority = "secondary"
        mock_version.enabled = False
        mock_version.config_data = {"old": True}

        mock_config = MagicMock()
        mock_config.tenant_id = "tenant-001"
        mock_config.provider_type = "map"

        with patch.object(service, "get_config_version", return_value=mock_version):
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = mock_config
            mock_session.query.return_value = mock_query

            result = service.rollback_to_version(mock_session, "config-id", 1, "admin")

        assert result == mock_config
        assert mock_config.api_key == "old-key"
        assert mock_config.priority == "secondary"
        assert mock_config.enabled is False
        mock_session.commit.assert_called_once()

    def test_rollback_version_not_found(self):
        """Test rollback returns None when version not found"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        with patch.object(service, "get_config_version", return_value=None):
            result = service.rollback_to_version(mock_session, "config-id", 99)

        assert result is None

    def test_rollback_config_not_found(self):
        """Test rollback returns None when config not found"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_version = MagicMock()
        with patch.object(service, "get_config_version", return_value=mock_version):
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = None
            mock_session.query.return_value = mock_query

            result = service.rollback_to_version(mock_session, "config-id", 1)

        assert result is None

    def test_rollback_error_rollback(self):
        """Test rollback rolls back session on error"""
        service, mock_db, mock_cache = self._make_service()
        mock_session = MagicMock()

        mock_version = MagicMock()
        mock_config = MagicMock()
        mock_config.tenant_id = "t"
        mock_config.provider_type = "map"

        with patch.object(service, "get_config_version", return_value=mock_version):
            mock_query = MagicMock()
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = mock_config
            mock_session.query.return_value = mock_query
            mock_session.commit.side_effect = RuntimeError("DB error")

            with pytest.raises(RuntimeError):
                service.rollback_to_version(mock_session, "config-id", 1)

        mock_session.rollback.assert_called_once()
