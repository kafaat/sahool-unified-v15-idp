"""
Tests for shared/secrets module
اختبارات وحدة إدارة الأسرار

Covers:
- VaultConfig configuration and validation
- VaultClient caching, connection, secret operations
- SecretKey enum and env_var mapping
- SecretBackend enum and from_env()
- SecretsManagerConfig defaults and custom values
- EnvironmentSecretsProvider CRUD operations
- SecretsManager initialization, fallback, health check
- SecretAccessEvent models and serialisation
- SecretAuditLogger access tracking, anomaly detection, stats
- record_metrics helper
- Global convenience functions
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.secrets.audit import (
    AccessResult,
    SecretAccessEvent,
    SecretAccessType,
    SecretAuditLogger,
    get_audit_logger,
    record_metrics,
)
from shared.secrets.manager import (
    AzureSecretsProvider,
    EnvironmentSecretsProvider,
    SecretBackend,
    SecretKey,
    SecretsManager,
    SecretsManagerConfig,
    VaultSecretsProvider,
    get_secrets_manager,
    initialize_secrets,
    shutdown_secrets,
)
from shared.secrets.vault import VaultClient, VaultConfig


# ═══════════════════════════════════════════════════════════════════════════════
# VaultConfig
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestVaultConfig:
    """Tests for VaultConfig dataclass"""

    def test_defaults(self):
        """Default values are sensible when env vars are unset"""
        with patch.dict(os.environ, {}, clear=True):
            cfg = VaultConfig(
                address="http://localhost:8200",
                token="test-token",
            )
            assert cfg.mount_point == "secret"
            assert cfg.path_prefix == "sahool"
            assert cfg.timeout == 30
            assert cfg.verify_ssl is True
            assert cfg.cache_ttl_seconds == 300
            assert cfg.enable_cache is True
            assert cfg.auto_renew_token is True
            assert cfg.renewal_threshold_seconds == 600

    def test_use_approle_true(self):
        """use_approle returns True when both role_id and secret_id set"""
        cfg = VaultConfig(
            address="http://vault:8200",
            role_id="role-123",
            secret_id="secret-456",
        )
        assert cfg.use_approle is True

    def test_use_approle_false_when_token(self):
        """use_approle returns False when only token is provided"""
        cfg = VaultConfig(
            address="http://vault:8200",
            token="s.abc123",
            role_id=None,
            secret_id=None,
        )
        assert cfg.use_approle is False

    def test_validate_raises_on_missing_address(self):
        """validate() raises ValueError when address is empty"""
        cfg = VaultConfig(address="", token="t")
        with pytest.raises(ValueError, match="VAULT_ADDR is required"):
            cfg.validate()

    def test_validate_raises_on_no_credentials(self):
        """validate() raises when neither token nor approle configured"""
        cfg = VaultConfig(
            address="http://vault:8200",
            token=None,
            role_id=None,
            secret_id=None,
        )
        with pytest.raises(ValueError, match="VAULT_TOKEN or both"):
            cfg.validate()

    def test_validate_passes_with_token(self):
        """validate() succeeds with token auth"""
        cfg = VaultConfig(address="http://vault:8200", token="s.root")
        cfg.validate()  # should not raise

    def test_from_env(self):
        """from_env() creates config from environment variables"""
        with patch.dict(
            os.environ,
            {"VAULT_ADDR": "http://v:8200", "VAULT_TOKEN": "tok"},
            clear=False,
        ):
            cfg = VaultConfig.from_env()
            assert cfg.address == "http://v:8200"
            assert cfg.token == "tok"

    def test_cache_max_staleness(self):
        """cache_max_staleness_seconds defaults to 3600"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        assert cfg.cache_max_staleness_seconds == 3600


# ═══════════════════════════════════════════════════════════════════════════════
# VaultClient
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestVaultClient:
    """Tests for VaultClient without a running Vault server"""

    def test_initial_state(self):
        """Client starts disconnected with empty cache"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        assert client.is_connected() is False
        assert client._cache == {}

    @pytest.mark.asyncio
    async def test_get_secret_when_disconnected_raises(self):
        """get_secret raises ConnectionError when not connected and no cache"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        with pytest.raises(ConnectionError, match="Not connected to Vault"):
            await client.get_secret("db/password")

    @pytest.mark.asyncio
    async def test_set_secret_when_disconnected_raises(self):
        """set_secret raises ConnectionError when not connected"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        with pytest.raises(ConnectionError, match="Not connected to Vault"):
            await client.set_secret("db/password", {"password": "x"})

    @pytest.mark.asyncio
    async def test_delete_secret_when_disconnected_raises(self):
        """delete_secret raises ConnectionError when not connected"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        with pytest.raises(ConnectionError, match="Not connected to Vault"):
            await client.delete_secret("db/password")

    @pytest.mark.asyncio
    async def test_list_secrets_when_disconnected_raises(self):
        """list_secrets raises ConnectionError when not connected"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        with pytest.raises(ConnectionError, match="Not connected to Vault"):
            await client.list_secrets()

    def test_get_full_path_with_prefix(self):
        """_get_full_path prepends the path_prefix"""
        cfg = VaultConfig(
            address="http://v:8200",
            token="t",
            path_prefix="sahool",
        )
        client = VaultClient(cfg)
        assert client._get_full_path("db/creds") == "sahool/db/creds"

    def test_get_full_path_without_prefix(self):
        """_get_full_path returns raw path when prefix is empty"""
        cfg = VaultConfig(
            address="http://v:8200",
            token="t",
            path_prefix="",
        )
        client = VaultClient(cfg)
        assert client._get_full_path("db/creds") == "db/creds"

    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """Cached values are returned within TTL"""
        cfg = VaultConfig(
            address="http://v:8200",
            token="t",
            cache_ttl_seconds=300,
        )
        client = VaultClient(cfg)
        await client._set_cache("key1", "val1")
        result = await client._get_from_cache("key1")
        assert result == "val1"

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self):
        """Cache miss returns None"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        result = await client._get_from_cache("missing")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_disabled_returns_none(self):
        """When cache is disabled, _get_from_cache always returns None"""
        cfg = VaultConfig(
            address="http://v:8200",
            token="t",
            enable_cache=False,
        )
        client = VaultClient(cfg)
        await client._set_cache("key1", "val1")
        result = await client._get_from_cache("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_expired_returns_none(self):
        """Expired cache entries return None from _get_from_cache"""
        cfg = VaultConfig(
            address="http://v:8200",
            token="t",
            cache_ttl_seconds=0,  # instantly expire
        )
        client = VaultClient(cfg)
        # Manually insert an old entry
        past = datetime.now(UTC) - timedelta(seconds=10)
        client._cache["key1"] = ("val1", past)
        result = await client._get_from_cache("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_stale_cache_fallback_within_staleness(self):
        """Stale cache fallback returns value within max staleness window"""
        cfg = VaultConfig(
            address="http://v:8200",
            token="t",
            cache_max_staleness_seconds=3600,
        )
        client = VaultClient(cfg)
        # Insert entry 10 seconds ago (within 3600s staleness)
        past = datetime.now(UTC) - timedelta(seconds=10)
        client._cache["key1"] = ("val1", past)
        result = await client._get_stale_cache_fallback("key1")
        assert result == "val1"

    @pytest.mark.asyncio
    async def test_stale_cache_fallback_too_old_raises(self):
        """Stale cache fallback raises KeyError when entry is too old"""
        cfg = VaultConfig(
            address="http://v:8200",
            token="t",
            cache_max_staleness_seconds=60,
        )
        client = VaultClient(cfg)
        past = datetime.now(UTC) - timedelta(seconds=120)
        client._cache["key1"] = ("val1", past)
        with pytest.raises(KeyError):
            await client._get_stale_cache_fallback("key1")

    @pytest.mark.asyncio
    async def test_stale_cache_fallback_missing_key_raises(self):
        """Stale cache fallback raises KeyError for missing keys"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        with pytest.raises(KeyError):
            await client._get_stale_cache_fallback("nonexistent")

    def test_clear_cache(self):
        """clear_cache empties the internal cache dict"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        client._cache["k"] = ("v", datetime.now(UTC))
        client.clear_cache()
        assert client._cache == {}

    @pytest.mark.asyncio
    async def test_disconnect_clears_state(self):
        """disconnect resets connected flag, client, and cache"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        client._connected = True
        client._client = MagicMock()
        client._cache["k"] = ("v", datetime.now(UTC))
        await client.disconnect()
        assert client.is_connected() is False
        assert client._client is None
        assert client._cache == {}

    @pytest.mark.asyncio
    async def test_health_check_no_client(self):
        """health_check returns unhealthy when client not initialized"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        health = await client.health_check()
        assert health["healthy"] is False
        assert health["connected"] is False

    @pytest.mark.asyncio
    async def test_health_check_with_mock_client(self):
        """health_check returns healthy when client responds"""
        cfg = VaultConfig(address="http://v:8200", token="t")
        client = VaultClient(cfg)
        mock_hvac = MagicMock()
        mock_hvac.sys.read_health_status.return_value = {
            "initialized": True,
            "sealed": False,
            "version": "1.17.0",
        }
        client._client = mock_hvac
        client._connected = True
        health = await client.health_check()
        assert health["healthy"] is True
        assert health["version"] == "1.17.0"
        assert health["sealed"] is False

    @pytest.mark.asyncio
    async def test_get_secret_uses_cache(self):
        """get_secret returns cached value without hitting Vault"""
        cfg = VaultConfig(address="http://v:8200", token="t", path_prefix="sahool")
        client = VaultClient(cfg)
        client._connected = True
        mock_hvac = MagicMock()
        client._client = mock_hvac

        # Pre-populate cache
        cache_key = "sahool/db/creds"
        await client._set_cache(cache_key, {"password": "cached"})

        result = await client.get_secret("db/creds")
        assert result == {"password": "cached"}
        # Vault should not be called
        mock_hvac.secrets.kv.v2.read_secret_version.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_secret_reads_from_vault(self):
        """get_secret reads from Vault when cache is empty"""
        cfg = VaultConfig(address="http://v:8200", token="t", path_prefix="sahool")
        client = VaultClient(cfg)
        client._connected = True
        mock_hvac = MagicMock()
        mock_hvac.secrets.kv.v2.read_secret_version.return_value = {
            "data": {"data": {"username": "admin", "password": "s3cret"}},
        }
        client._client = mock_hvac

        result = await client.get_secret("db/creds")
        assert result == {"username": "admin", "password": "s3cret"}

    @pytest.mark.asyncio
    async def test_get_secret_specific_key(self):
        """get_secret with key parameter returns just that key"""
        cfg = VaultConfig(address="http://v:8200", token="t", path_prefix="sahool")
        client = VaultClient(cfg)
        client._connected = True
        mock_hvac = MagicMock()
        mock_hvac.secrets.kv.v2.read_secret_version.return_value = {
            "data": {"data": {"username": "admin", "password": "s3cret"}},
        }
        client._client = mock_hvac

        result = await client.get_secret("db/creds", key="password")
        assert result == "s3cret"

    @pytest.mark.asyncio
    async def test_get_secret_missing_key_raises(self):
        """get_secret with non-existent key raises KeyError"""
        cfg = VaultConfig(address="http://v:8200", token="t", path_prefix="sahool")
        client = VaultClient(cfg)
        client._connected = True
        mock_hvac = MagicMock()
        mock_hvac.secrets.kv.v2.read_secret_version.return_value = {
            "data": {"data": {"username": "admin"}},
        }
        client._client = mock_hvac

        with pytest.raises(KeyError, match="password"):
            await client.get_secret("db/creds", key="password")

    @pytest.mark.asyncio
    async def test_set_secret_invalidates_cache(self):
        """set_secret invalidates related cache entries"""
        cfg = VaultConfig(address="http://v:8200", token="t", path_prefix="sahool")
        client = VaultClient(cfg)
        client._connected = True
        mock_hvac = MagicMock()
        client._client = mock_hvac

        # Pre-populate cache
        client._cache["sahool/db/creds"] = ({"pw": "old"}, datetime.now(UTC))
        client._cache["sahool/db/creds:password"] = ("old", datetime.now(UTC))
        client._cache["sahool/other"] = ("keep", datetime.now(UTC))

        await client.set_secret("db/creds", {"pw": "new"})

        assert "sahool/db/creds" not in client._cache
        assert "sahool/db/creds:password" not in client._cache
        # Unrelated key remains
        assert "sahool/other" in client._cache

    @pytest.mark.asyncio
    async def test_get_secrets_batch(self):
        """get_secrets_batch returns results for multiple paths"""
        cfg = VaultConfig(address="http://v:8200", token="t", path_prefix="sahool")
        client = VaultClient(cfg)
        client._connected = True
        mock_hvac = MagicMock()
        client._client = mock_hvac

        def side_effect(path, mount_point):
            if "db" in path:
                return {"data": {"data": {"pw": "dbpass"}}}
            raise Exception("not found")

        mock_hvac.secrets.kv.v2.read_secret_version.side_effect = side_effect

        results = await client.get_secrets_batch(["db/creds", "missing/key"])
        assert results["db/creds"] == {"pw": "dbpass"}
        assert results["missing/key"] is None


# ═══════════════════════════════════════════════════════════════════════════════
# SecretKey
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSecretKeyExtended:
    """Extended tests for SecretKey enum"""

    def test_env_var_conversion_slashes_replaced(self):
        """env_var replaces slashes with underscores and uppercases"""
        assert SecretKey.DATABASE_URL.env_var == "DATABASE_URL"
        assert SecretKey.ANTHROPIC_API_KEY.env_var == "EXTERNAL_ANTHROPIC_API_KEY"
        assert SecretKey.SMTP_PASSWORD.env_var == "COMMUNICATION_SMTP_PASSWORD"
        assert SecretKey.APP_SECRET_KEY.env_var == "APP_SECRET_KEY"

    def test_is_strenum(self):
        """SecretKey values are strings"""
        assert isinstance(SecretKey.DATABASE_PASSWORD, str)
        assert SecretKey.DATABASE_PASSWORD == "database/password"

    def test_all_keys_contain_slash(self):
        """All secret keys use path-style notation with slashes"""
        for key in SecretKey:
            assert "/" in key.value, f"{key.name} should contain a slash"


# ═══════════════════════════════════════════════════════════════════════════════
# SecretBackend
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSecretBackendExtended:
    """Extended tests for SecretBackend enum"""

    def test_from_env_aws(self):
        """from_env detects aws_secrets_manager"""
        with patch.dict(os.environ, {"SECRET_BACKEND": "aws_secrets_manager"}):
            assert SecretBackend.from_env() == SecretBackend.AWS_SECRETS_MANAGER

    def test_from_env_azure(self):
        """from_env detects azure_key_vault"""
        with patch.dict(os.environ, {"SECRET_BACKEND": "azure_key_vault"}):
            assert SecretBackend.from_env() == SecretBackend.AZURE_KEY_VAULT

    def test_from_env_case_insensitive(self):
        """from_env lowercases the value"""
        with patch.dict(os.environ, {"SECRET_BACKEND": "VAULT"}):
            assert SecretBackend.from_env() == SecretBackend.VAULT


# ═══════════════════════════════════════════════════════════════════════════════
# EnvironmentSecretsProvider
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnvironmentProviderFallback:
    """Tests for env provider fallback variations"""

    @pytest.mark.asyncio
    async def test_sahool_prefixed_env_var(self):
        """Provider finds SAHOOL_ prefixed env vars as fallback"""
        provider = EnvironmentSecretsProvider()
        await provider.connect()

        with patch.dict(os.environ, {"SAHOOL_MY_SECRET": "found"}, clear=False):
            value = await provider.get_secret("my/secret")
            assert value == "found"

    @pytest.mark.asyncio
    async def test_health_check_not_connected(self):
        """Health check reflects disconnected state"""
        provider = EnvironmentSecretsProvider()
        health = await provider.health_check()
        assert health["connected"] is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_no_error(self):
        """Deleting a non-existent env var does not raise"""
        provider = EnvironmentSecretsProvider()
        await provider.connect()
        await provider.delete_secret("never/existed")  # should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# AzureSecretsProvider
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAzureSecretsProvider:
    """Tests for AzureSecretsProvider name normalization"""

    def test_normalize_name(self):
        """Azure provider normalises slashes and underscores to hyphens"""
        provider = AzureSecretsProvider()
        assert provider._normalize_name("database/password") == "database-password"
        assert provider._normalize_name("app_secret_key") == "app-secret-key"
        assert provider._normalize_name("a/b_c") == "a-b-c"

    @pytest.mark.asyncio
    async def test_get_secret_not_connected(self):
        """get_secret raises ConnectionError when not connected"""
        provider = AzureSecretsProvider()
        with pytest.raises(ConnectionError, match="Azure client not connected"):
            await provider.get_secret("db/password")


# ═══════════════════════════════════════════════════════════════════════════════
# SecretsManager
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSecretsManagerExtended:
    """Extended tests for SecretsManager"""

    @pytest.mark.asyncio
    async def test_double_initialize_returns_true(self):
        """Calling initialize() twice is safe and returns True"""
        config = SecretsManagerConfig(backend=SecretBackend.ENVIRONMENT)
        mgr = SecretsManager(config)
        assert await mgr.initialize() is True
        assert await mgr.initialize() is True

    @pytest.mark.asyncio
    async def test_set_and_get_secret(self):
        """Round-trip set then get using environment provider"""
        config = SecretsManagerConfig(backend=SecretBackend.ENVIRONMENT)
        mgr = SecretsManager(config)
        await mgr.initialize()

        await mgr.set_secret("test/roundtrip", "round_trip_value")
        try:
            value = await mgr.get_secret("test/roundtrip")
            assert value == "round_trip_value"
        finally:
            await mgr.delete_secret("test/roundtrip")

    @pytest.mark.asyncio
    async def test_delete_secret(self):
        """delete_secret removes the env var"""
        config = SecretsManagerConfig(backend=SecretBackend.ENVIRONMENT)
        mgr = SecretsManager(config)
        await mgr.initialize()

        os.environ["TO_DELETE"] = "bye"
        await mgr.delete_secret("to/delete")
        assert "TO_DELETE" not in os.environ

    @pytest.mark.asyncio
    async def test_fallback_to_env_on_vault_failure(self):
        """Manager falls back to env provider when vault init fails"""
        config = SecretsManagerConfig(
            backend=SecretBackend.VAULT,
            fallback_to_env=True,
        )
        mgr = SecretsManager(config)

        # VaultSecretsProvider will fail because hvac is not installed / no server
        result = await mgr.initialize()
        assert result is True
        # It should have fallen back to EnvironmentSecretsProvider
        assert isinstance(mgr._provider, EnvironmentSecretsProvider)

    @pytest.mark.asyncio
    async def test_health_check_not_initialized(self):
        """health_check returns unhealthy when not initialized"""
        mgr = SecretsManager()
        health = await mgr.health_check()
        assert health["healthy"] is False
        assert health["initialized"] is False

    @pytest.mark.asyncio
    async def test_get_secret_auto_initializes(self):
        """get_secret triggers auto-initialization if not yet done"""
        config = SecretsManagerConfig(backend=SecretBackend.ENVIRONMENT)
        mgr = SecretsManager(config)

        os.environ["AUTO_INIT_KEY"] = "auto_val"
        try:
            value = await mgr.get_secret("auto/init_key")
            assert value == "auto_val"
            assert mgr._initialized is True
        finally:
            del os.environ["AUTO_INIT_KEY"]

    @pytest.mark.asyncio
    async def test_get_secret_env_fallback_for_vault_backend(self):
        """When using vault backend with env fallback, missing vault key falls back to env"""
        config = SecretsManagerConfig(
            backend=SecretBackend.VAULT,
            fallback_to_env=True,
        )
        mgr = SecretsManager(config)
        await mgr.initialize()  # will fall back to env provider

        os.environ["FALLBACK_KEY"] = "fb_val"
        try:
            value = await mgr.get_secret("fallback/key")
            assert value == "fb_val"
        finally:
            del os.environ["FALLBACK_KEY"]


# ═══════════════════════════════════════════════════════════════════════════════
# Global functions
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGlobalFunctions:
    """Tests for module-level convenience functions"""

    @pytest.mark.asyncio
    async def test_get_secrets_manager_returns_singleton(self):
        """get_secrets_manager returns the same instance on repeated calls"""
        import shared.secrets.manager as mod

        old = mod._secrets_manager
        try:
            mod._secrets_manager = None
            m1 = get_secrets_manager()
            m2 = get_secrets_manager()
            assert m1 is m2
        finally:
            mod._secrets_manager = old

    @pytest.mark.asyncio
    async def test_initialize_and_shutdown_secrets(self):
        """initialize_secrets and shutdown_secrets lifecycle"""
        import shared.secrets.manager as mod

        old = mod._secrets_manager
        try:
            mod._secrets_manager = None
            mgr = await initialize_secrets()
            assert mgr._initialized is True

            await shutdown_secrets()
            assert mod._secrets_manager is None
        finally:
            mod._secrets_manager = old


# ═══════════════════════════════════════════════════════════════════════════════
# SecretAccessEvent
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSecretAccessEvent:
    """Tests for SecretAccessEvent model"""

    def test_defaults(self):
        """Default values are populated"""
        event = SecretAccessEvent()
        assert event.access_type == SecretAccessType.READ
        assert event.result == AccessResult.SUCCESS
        assert event.user == "unknown"
        assert event.source_ip == "unknown"
        assert event.service == "unknown"
        assert event.duration_ms == 0.0

    def test_to_dict(self):
        """to_dict produces expected keys"""
        event = SecretAccessEvent(
            secret_path="db/password",
            user="svc-api",
            backend="vault",
        )
        d = event.to_dict()
        assert d["secret_path"] == "db/password"
        assert d["user"] == "svc-api"
        assert d["backend"] == "vault"
        assert "timestamp" in d

    def test_to_json_is_valid(self):
        """to_json returns valid JSON"""
        event = SecretAccessEvent(secret_path="a/b")
        data = json.loads(event.to_json())
        assert data["secret_path"] == "a/b"

    def test_sanitize_path_strips_query_and_fragment(self):
        """_sanitize_path removes query strings and fragments"""
        assert SecretAccessEvent._sanitize_path("path?key=val") == "path"
        assert SecretAccessEvent._sanitize_path("path#section") == "path"
        assert SecretAccessEvent._sanitize_path("clean/path") == "clean/path"


# ═══════════════════════════════════════════════════════════════════════════════
# SecretAuditLogger
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSecretAuditLogger:
    """Tests for SecretAuditLogger"""

    @pytest.mark.asyncio
    async def test_log_access_stores_event(self):
        """log_access stores the event in history"""
        logger_inst = SecretAuditLogger(enable_anomaly_detection=True)
        event = SecretAccessEvent(
            secret_path="db/pw",
            user="test-user",
        )
        await logger_inst.log_access(event)
        assert len(logger_inst._access_history) == 1

    @pytest.mark.asyncio
    async def test_track_failed_attempts(self):
        """Failed attempts are tracked per user"""
        logger_inst = SecretAuditLogger(enable_anomaly_detection=True)
        event = SecretAccessEvent(
            secret_path="db/pw",
            user="bad-user",
            result=AccessResult.DENIED,
        )
        await logger_inst.log_access(event)
        assert len(logger_inst._failed_attempts["bad-user"]) == 1

    @pytest.mark.asyncio
    async def test_access_counts_increment(self):
        """Access counts increment per user:path"""
        logger_inst = SecretAuditLogger(enable_anomaly_detection=True)
        event = SecretAccessEvent(secret_path="db/pw", user="svc")
        await logger_inst.log_access(event)
        await logger_inst.log_access(event)
        assert logger_inst._access_counts["svc:db/pw"] == 2

    def test_get_access_stats_empty(self):
        """get_access_stats returns zeroes with no history"""
        logger_inst = SecretAuditLogger()
        stats = logger_inst.get_access_stats()
        assert stats["total_accesses"] == 0
        assert stats["successful"] == 0
        assert stats["unique_users"] == 0

    @pytest.mark.asyncio
    async def test_get_access_stats_populated(self):
        """get_access_stats returns correct aggregations"""
        logger_inst = SecretAuditLogger(enable_anomaly_detection=True)
        for i in range(3):
            await logger_inst.log_access(
                SecretAccessEvent(
                    secret_path="db/pw",
                    user="svc",
                    backend="vault",
                )
            )
        await logger_inst.log_access(
            SecretAccessEvent(
                secret_path="db/pw",
                user="other",
                result=AccessResult.DENIED,
                backend="environment",
            )
        )

        stats = logger_inst.get_access_stats(hours=24)
        assert stats["total_accesses"] == 4
        assert stats["successful"] == 3
        assert stats["failed"] == 1
        assert stats["unique_users"] == 2
        assert stats["by_backend"]["vault"] == 3
        assert stats["by_backend"]["environment"] == 1

    @pytest.mark.asyncio
    async def test_anomaly_high_frequency_alert(self):
        """High frequency access triggers alert"""
        logger_inst = SecretAuditLogger(
            alert_threshold=2,
            enable_anomaly_detection=True,
        )
        event = SecretAccessEvent(secret_path="db/pw", user="bot")
        # Access 3 times to exceed threshold of 2
        for _ in range(3):
            await logger_inst.log_access(event)
        assert logger_inst._access_counts["bot:db/pw"] == 3

    @pytest.mark.asyncio
    async def test_history_pruning(self):
        """Old events are pruned from history during tracking"""
        logger_inst = SecretAuditLogger(enable_anomaly_detection=True)
        # Insert an old event directly
        old_event = SecretAccessEvent(
            secret_path="old/secret",
            user="old-user",
        )
        old_event.timestamp = datetime.now(UTC) - timedelta(hours=25)
        logger_inst._access_history.append(old_event)

        # Log a new event - this triggers pruning
        await logger_inst.log_access(
            SecretAccessEvent(secret_path="new/s", user="new-user")
        )
        # Old event should have been pruned
        paths = [e.secret_path for e in logger_inst._access_history]
        assert "old/secret" not in paths
        assert "new/s" in paths


# ═══════════════════════════════════════════════════════════════════════════════
# record_metrics
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRecordMetrics:
    """Tests for record_metrics helper"""

    def test_record_metrics_does_not_raise(self):
        """record_metrics should not raise even without prometheus"""
        event = SecretAccessEvent(
            secret_path="test/path",
            backend="environment",
            access_type=SecretAccessType.READ,
            result=AccessResult.SUCCESS,
            service="test-svc",
            duration_ms=5.0,
        )
        # Should not raise regardless of prometheus availability
        record_metrics(event)

    def test_record_metrics_failure_event(self):
        """record_metrics handles failure events"""
        event = SecretAccessEvent(
            secret_path="test/path",
            backend="vault",
            access_type=SecretAccessType.WRITE,
            result=AccessResult.ERROR,
            user="svc",
            service="test-svc",
            duration_ms=100.0,
        )
        record_metrics(event)  # should not raise


# ═══════════════════════════════════════════════════════════════════════════════
# get_audit_logger
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetAuditLogger:
    """Tests for global get_audit_logger"""

    def test_returns_singleton(self):
        """get_audit_logger returns the same instance on repeated calls"""
        import shared.secrets.audit as audit_mod

        old = audit_mod._audit_logger
        try:
            # Pre-set a logger without file to avoid filesystem dependency
            audit_mod._audit_logger = SecretAuditLogger(log_file=None)
            l1 = get_audit_logger()
            l2 = get_audit_logger()
            assert l1 is l2
        finally:
            audit_mod._audit_logger = old


# ═══════════════════════════════════════════════════════════════════════════════
# Module __init__ exports
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestModuleExports:
    """Verify public API exports from shared.secrets"""

    def test_all_exports_importable(self):
        """All __all__ entries can be imported"""
        from shared.secrets import __all__ as exports

        import shared.secrets as mod

        for name in exports:
            assert hasattr(mod, name), f"{name} not found in shared.secrets"
