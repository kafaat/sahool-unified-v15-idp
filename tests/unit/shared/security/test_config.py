"""
Tests for shared/security/config.py
Security configuration management with secrets externalization
"""

import json
import os
import time
from unittest.mock import MagicMock, patch

import pytest

from shared.security.config import (
    SecretBackend,
    SecretConfig,
    SecretManager,
    get_config,
    get_cors_origins,
    get_environment,
    get_jwt_secret,
    get_log_level,
    get_nats_url,
    get_secret_manager,
    is_development,
    is_production,
)


# ---------------------------------------------------------------------------
# SecretBackend enum
# ---------------------------------------------------------------------------


class TestSecretBackend:
    def test_enum_values(self):
        assert SecretBackend.ENVIRONMENT == "environment"
        assert SecretBackend.VAULT == "vault"
        assert SecretBackend.AWS_SECRETS_MANAGER == "aws_secrets_manager"
        assert SecretBackend.AZURE_KEY_VAULT == "azure_key_vault"


# ---------------------------------------------------------------------------
# SecretConfig dataclass
# ---------------------------------------------------------------------------


class TestSecretConfig:
    def test_defaults(self):
        config = SecretConfig()
        assert config.backend == SecretBackend.ENVIRONMENT
        assert config.vault_addr is None
        assert config.vault_token is None
        assert config.vault_role_id is None
        assert config.vault_secret_id is None
        assert config.vault_namespace is None
        assert config.vault_mount_point == "secret"
        assert config.vault_path_prefix == "sahool"
        assert config.allow_env_fallback is True
        assert config.cache_ttl_seconds == 300
        assert config.cache_enabled is True

    def test_custom_values(self):
        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            cache_ttl_seconds=600,
            cache_enabled=False,
        )
        assert config.backend == SecretBackend.VAULT
        assert config.vault_addr == "http://vault:8200"
        assert config.cache_ttl_seconds == 600
        assert config.cache_enabled is False


# ---------------------------------------------------------------------------
# SecretManager - Environment Backend
# ---------------------------------------------------------------------------


class TestSecretManagerEnvironment:
    def test_init_default_config(self):
        manager = SecretManager()
        assert manager.config.backend == SecretBackend.ENVIRONMENT
        assert manager._cache == {}
        assert manager._vault_client is None

    def test_init_explicit_config(self):
        config = SecretConfig(backend=SecretBackend.ENVIRONMENT)
        manager = SecretManager(config)
        assert manager.config is config

    def test_get_secret_from_env(self):
        manager = SecretManager()
        with patch.dict(os.environ, {"MY_SECRET": "my_value"}):
            result = manager.get_secret("MY_SECRET")
            assert result == "my_value"

    def test_get_secret_not_found_returns_none(self):
        manager = SecretManager()
        result = manager.get_secret("NONEXISTENT_KEY_12345")
        assert result is None

    def test_get_secret_with_default(self):
        manager = SecretManager()
        result = manager.get_secret("NONEXISTENT_KEY_12345", default="fallback")
        assert result == "fallback"

    def test_get_secret_required_missing_raises(self):
        manager = SecretManager()
        with pytest.raises(ValueError, match="Required secret"):
            manager.get_secret("NONEXISTENT_KEY_12345", required=True)

    def test_get_secret_required_with_value(self):
        manager = SecretManager()
        with patch.dict(os.environ, {"REQUIRED_KEY": "present"}):
            result = manager.get_secret("REQUIRED_KEY", required=True)
            assert result == "present"

    def test_caching_enabled(self):
        config = SecretConfig(cache_enabled=True, cache_ttl_seconds=300)
        manager = SecretManager(config)
        with patch.dict(os.environ, {"CACHED_KEY": "value1"}):
            # First call - fetches from env
            result1 = manager.get_secret("CACHED_KEY")
            assert result1 == "value1"

        # Second call - should return cached value even though env var removed
        result2 = manager.get_secret("CACHED_KEY")
        assert result2 == "value1"

    def test_cache_expired(self):
        config = SecretConfig(cache_enabled=True, cache_ttl_seconds=0)
        manager = SecretManager(config)

        with patch.dict(os.environ, {"TTL_KEY": "first"}):
            manager.get_secret("TTL_KEY")

        # Cache TTL is 0 so it should be expired immediately
        # Without the env var, it falls through
        result = manager.get_secret("TTL_KEY", default="expired_fallback")
        # The cache_ttl is 0, so cache_age >= cache_ttl always, so it refetches
        # TTL_KEY is no longer in env, so returns default
        assert result == "expired_fallback"

    def test_caching_disabled(self):
        config = SecretConfig(cache_enabled=False)
        manager = SecretManager(config)
        with patch.dict(os.environ, {"NO_CACHE_KEY": "val"}):
            result = manager.get_secret("NO_CACHE_KEY")
            assert result == "val"
        # Value not cached, so should not be found
        result2 = manager.get_secret("NO_CACHE_KEY")
        assert result2 is None

    def test_clear_cache(self):
        manager = SecretManager()
        with patch.dict(os.environ, {"CK": "v"}):
            manager.get_secret("CK")
        assert "CK" in manager._cache
        manager.clear_cache()
        assert manager._cache == {}
        assert manager._cache_timestamps == {}

    def test_get_secrets_batch(self):
        manager = SecretManager()
        with patch.dict(os.environ, {"K1": "v1", "K2": "v2"}):
            result = manager.get_secrets_batch(["K1", "K2", "K3"])
            assert result == {"K1": "v1", "K2": "v2", "K3": None}

    def test_set_secret_on_environment_backend_returns_false(self):
        manager = SecretManager()
        assert manager.set_secret("key", "value") is False


# ---------------------------------------------------------------------------
# SecretManager - Vault Backend (mocked)
# ---------------------------------------------------------------------------


class TestSecretManagerVault:
    def test_vault_init_no_hvac_with_fallback(self):
        """When hvac not installed and fallback allowed, falls back to env"""
        config = SecretConfig(
            backend=SecretBackend.VAULT,
            allow_env_fallback=True,
        )
        with patch.dict("sys.modules", {"hvac": None}):
            # _init_vault will get ImportError, fallback to env
            manager = SecretManager(config)
            assert manager.config.backend == SecretBackend.ENVIRONMENT

    def test_vault_init_no_hvac_no_fallback_raises(self):
        """When hvac not installed and fallback disabled, raises"""
        config = SecretConfig(
            backend=SecretBackend.VAULT,
            allow_env_fallback=False,
        )
        with patch.dict("sys.modules", {"hvac": None}):
            with pytest.raises(ImportError, match="hvac"):
                SecretManager(config)

    def test_vault_init_no_addr_with_fallback(self):
        """No vault addr configured, falls back to env"""
        mock_hvac = MagicMock()
        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr=None,
            allow_env_fallback=True,
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            with patch.dict(os.environ, {}, clear=False):
                # Remove VAULT_ADDR if present
                os.environ.pop("VAULT_ADDR", None)
                manager = SecretManager(config)
                assert manager.config.backend == SecretBackend.ENVIRONMENT

    def test_vault_init_no_addr_no_fallback_raises(self):
        """No vault addr and no fallback raises RuntimeError (wraps ValueError)"""
        mock_hvac = MagicMock()
        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr=None,
            allow_env_fallback=False,
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac}):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("VAULT_ADDR", None)
                with pytest.raises(RuntimeError, match="Failed to initialize Vault"):
                    SecretManager(config)

    def test_vault_init_token_auth(self):
        """Vault init with token authentication"""
        mock_hvac_module = MagicMock()
        mock_client = MagicMock()
        mock_client.is_authenticated.return_value = True
        mock_hvac_module.Client.return_value = mock_client

        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            vault_token="test-token",
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac_module}):
            manager = SecretManager(config)
            assert manager.config.backend == SecretBackend.VAULT
            assert mock_client.token == "test-token"

    def test_vault_init_approle_auth(self):
        """Vault init with AppRole authentication"""
        mock_hvac_module = MagicMock()
        mock_client = MagicMock()
        mock_client.is_authenticated.return_value = True
        mock_client.auth.approle.login.return_value = {
            "auth": {"client_token": "app-token-123"}
        }
        mock_hvac_module.Client.return_value = mock_client

        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            vault_role_id="role-id",
            vault_secret_id="secret-id",
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac_module}):
            manager = SecretManager(config)
            assert manager.config.backend == SecretBackend.VAULT
            assert mock_client.token == "app-token-123"

    def test_vault_init_no_auth_with_fallback(self):
        """No vault auth configured, falls back to env"""
        mock_hvac_module = MagicMock()
        mock_client = MagicMock()
        mock_hvac_module.Client.return_value = mock_client

        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            allow_env_fallback=True,
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac_module}):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("VAULT_TOKEN", None)
                os.environ.pop("VAULT_ROLE_ID", None)
                manager = SecretManager(config)
                assert manager.config.backend == SecretBackend.ENVIRONMENT

    def test_vault_init_no_auth_no_fallback_raises(self):
        """No vault auth and no fallback raises RuntimeError (wraps ValueError)"""
        mock_hvac_module = MagicMock()
        mock_client = MagicMock()
        mock_hvac_module.Client.return_value = mock_client

        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            allow_env_fallback=False,
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac_module}):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("VAULT_TOKEN", None)
                os.environ.pop("VAULT_ROLE_ID", None)
                with pytest.raises(RuntimeError, match="Failed to initialize Vault"):
                    SecretManager(config)

    def test_vault_init_auth_failed_with_fallback(self):
        """Vault auth fails, falls back to env"""
        mock_hvac_module = MagicMock()
        mock_client = MagicMock()
        mock_client.is_authenticated.return_value = False
        mock_hvac_module.Client.return_value = mock_client

        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            vault_token="bad-token",
            allow_env_fallback=True,
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac_module}):
            manager = SecretManager(config)
            assert manager.config.backend == SecretBackend.ENVIRONMENT

    def test_vault_init_auth_failed_no_fallback_raises(self):
        """Vault auth fails without fallback raises RuntimeError"""
        mock_hvac_module = MagicMock()
        mock_client = MagicMock()
        mock_client.is_authenticated.return_value = False
        mock_hvac_module.Client.return_value = mock_client

        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            vault_token="bad-token",
            allow_env_fallback=False,
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac_module}):
            with pytest.raises(RuntimeError, match="Failed to initialize Vault"):
                SecretManager(config)

    def test_vault_init_generic_exception_with_fallback(self):
        """Generic exception during init, falls back to env"""
        mock_hvac_module = MagicMock()
        mock_hvac_module.Client.side_effect = ConnectionError("connection refused")

        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            vault_token="token",
            allow_env_fallback=True,
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac_module}):
            manager = SecretManager(config)
            assert manager.config.backend == SecretBackend.ENVIRONMENT

    def test_vault_init_generic_exception_no_fallback_raises(self):
        """Generic exception without fallback raises RuntimeError"""
        mock_hvac_module = MagicMock()
        mock_hvac_module.Client.side_effect = ConnectionError("connection refused")

        config = SecretConfig(
            backend=SecretBackend.VAULT,
            vault_addr="http://vault:8200",
            vault_token="token",
            allow_env_fallback=False,
        )
        with patch.dict("sys.modules", {"hvac": mock_hvac_module}):
            with pytest.raises(RuntimeError, match="Failed to initialize Vault"):
                SecretManager(config)

    def test_get_from_vault_no_client(self):
        """_get_from_vault returns None when client is None"""
        manager = SecretManager()  # env backend, no vault client
        result = manager._get_from_vault("some_key")
        assert result is None

    def test_get_from_vault_success(self):
        """_get_from_vault reads from vault KV v2"""
        manager = SecretManager()
        mock_client = MagicMock()
        mock_client.secrets.kv.v2.read_secret_version.return_value = {
            "data": {"data": {"value": "vault_secret"}}
        }
        manager._vault_client = mock_client

        result = manager._get_from_vault("my_key")
        assert result == "vault_secret"
        mock_client.secrets.kv.v2.read_secret_version.assert_called_once_with(
            path="sahool/my_key",
            mount_point="secret",
        )

    def test_get_from_vault_exception(self):
        """_get_from_vault returns None on exception"""
        manager = SecretManager()
        mock_client = MagicMock()
        mock_client.secrets.kv.v2.read_secret_version.side_effect = Exception("timeout")
        manager._vault_client = mock_client

        result = manager._get_from_vault("key")
        assert result is None

    def test_get_secret_vault_backend(self):
        """get_secret routes to vault when backend is VAULT"""
        config = SecretConfig(backend=SecretBackend.VAULT, cache_enabled=False)
        manager = SecretManager.__new__(SecretManager)
        manager.config = config
        manager._cache = {}
        manager._cache_timestamps = {}
        manager._vault_client = MagicMock()
        manager._vault_client.secrets.kv.v2.read_secret_version.return_value = {
            "data": {"data": {"value": "from_vault"}}
        }

        result = manager.get_secret("vault_key")
        assert result == "from_vault"

    def test_set_secret_vault_success(self):
        """set_secret writes to vault"""
        config = SecretConfig(backend=SecretBackend.VAULT, cache_enabled=True)
        manager = SecretManager.__new__(SecretManager)
        manager.config = config
        manager._cache = {}
        manager._cache_timestamps = {}
        manager._vault_client = MagicMock()

        result = manager.set_secret("key", "value")
        assert result is True
        assert manager._cache["key"] == "value"

    def test_set_secret_vault_no_client(self):
        """set_secret returns False when vault client is None"""
        config = SecretConfig(backend=SecretBackend.VAULT)
        manager = SecretManager.__new__(SecretManager)
        manager.config = config
        manager._cache = {}
        manager._cache_timestamps = {}
        manager._vault_client = None

        result = manager.set_secret("key", "value")
        assert result is False

    def test_set_secret_vault_exception(self):
        """set_secret returns False on exception"""
        config = SecretConfig(backend=SecretBackend.VAULT)
        manager = SecretManager.__new__(SecretManager)
        manager.config = config
        manager._cache = {}
        manager._cache_timestamps = {}
        manager._vault_client = MagicMock()
        manager._vault_client.secrets.kv.v2.create_or_update_secret.side_effect = Exception("err")

        result = manager.set_secret("key", "value")
        assert result is False


# ---------------------------------------------------------------------------
# get_secret_manager (global singleton)
# ---------------------------------------------------------------------------


class TestGetSecretManager:
    def setup_method(self):
        # Reset global singleton before each test
        import shared.security.config as cfg_mod
        cfg_mod._global_secret_manager = None

    def teardown_method(self):
        import shared.security.config as cfg_mod
        cfg_mod._global_secret_manager = None

    def test_returns_singleton(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}):
            mgr1 = get_secret_manager()
            mgr2 = get_secret_manager()
            assert mgr1 is mgr2

    def test_auto_detect_env_backend(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}, clear=False):
            mgr = get_secret_manager()
            assert mgr.config.backend == SecretBackend.ENVIRONMENT

    def test_auto_detect_unknown_backend_falls_back(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "unknown_backend"}, clear=False):
            mgr = get_secret_manager()
            assert mgr.config.backend == SecretBackend.ENVIRONMENT

    def test_custom_config(self):
        config = SecretConfig(backend=SecretBackend.ENVIRONMENT, cache_ttl_seconds=999)
        mgr = get_secret_manager(config)
        assert mgr.config.cache_ttl_seconds == 999


# ---------------------------------------------------------------------------
# get_config with type casting
# ---------------------------------------------------------------------------


class TestGetConfig:
    def setup_method(self):
        import shared.security.config as cfg_mod
        cfg_mod._global_secret_manager = None

    def teardown_method(self):
        import shared.security.config as cfg_mod
        cfg_mod._global_secret_manager = None

    def test_string_type(self):
        with patch.dict(os.environ, {"TEST_STR": "hello", "SECRET_BACKEND": "environment"}):
            result = get_config("TEST_STR")
            assert result == "hello"

    def test_int_type(self):
        with patch.dict(os.environ, {"TEST_INT": "8080", "SECRET_BACKEND": "environment"}):
            result = get_config("TEST_INT", cast_type=int)
            assert result == 8080

    def test_float_type(self):
        with patch.dict(os.environ, {"TEST_FLOAT": "3.14", "SECRET_BACKEND": "environment"}):
            result = get_config("TEST_FLOAT", cast_type=float)
            assert result == pytest.approx(3.14)

    def test_bool_true_values(self):
        for val in ["true", "1", "yes", "on", "True", "YES"]:
            with patch.dict(os.environ, {"TEST_BOOL": val, "SECRET_BACKEND": "environment"}):
                import shared.security.config as cfg_mod
                cfg_mod._global_secret_manager = None
                result = get_config("TEST_BOOL", cast_type=bool)
                assert result is True, f"Expected True for '{val}'"

    def test_bool_false_values(self):
        for val in ["false", "0", "no", "off"]:
            with patch.dict(os.environ, {"TEST_BOOL": val, "SECRET_BACKEND": "environment"}):
                import shared.security.config as cfg_mod
                cfg_mod._global_secret_manager = None
                result = get_config("TEST_BOOL", cast_type=bool)
                assert result is False, f"Expected False for '{val}'"

    def test_list_type(self):
        with patch.dict(os.environ, {"TEST_LIST": "a, b, c", "SECRET_BACKEND": "environment"}):
            result = get_config("TEST_LIST", cast_type=list)
            assert result == ["a", "b", "c"]

    def test_list_type_strips_whitespace(self):
        with patch.dict(os.environ, {"TEST_LIST": " x , y , z ", "SECRET_BACKEND": "environment"}):
            result = get_config("TEST_LIST", cast_type=list)
            assert result == ["x", "y", "z"]

    def test_dict_type(self):
        data = {"key": "value", "num": 42}
        with patch.dict(os.environ, {"TEST_DICT": json.dumps(data), "SECRET_BACKEND": "environment"}):
            result = get_config("TEST_DICT", cast_type=dict)
            assert result == data

    def test_returns_none_when_not_found(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}):
            result = get_config("NONEXISTENT_CONFIG_XYZ")
            assert result is None

    def test_default_value(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}):
            result = get_config("NONEXISTENT", default="42", cast_type=int)
            assert result == 42

    def test_default_value_string(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}):
            result = get_config("NONEXISTENT", default="fallback")
            assert result == "fallback"


# ---------------------------------------------------------------------------
# Convenience getters
# ---------------------------------------------------------------------------


class TestConvenienceGetters:
    def setup_method(self):
        import shared.security.config as cfg_mod
        cfg_mod._global_secret_manager = None

    def teardown_method(self):
        import shared.security.config as cfg_mod
        cfg_mod._global_secret_manager = None

    def test_get_nats_url_default(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}, clear=False):
            os.environ.pop("NATS_URL", None)
            result = get_nats_url()
            assert result == "nats://localhost:4222"

    def test_get_cors_origins(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}, clear=False):
            os.environ.pop("CORS_ALLOWED_ORIGINS", None)
            result = get_cors_origins()
            assert result == ["http://localhost:3000"]

    def test_get_environment_default(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}, clear=False):
            os.environ.pop("ENVIRONMENT", None)
            result = get_environment()
            assert result == "development"

    def test_get_log_level_default(self):
        with patch.dict(os.environ, {"SECRET_BACKEND": "environment"}, clear=False):
            os.environ.pop("LOG_LEVEL", None)
            result = get_log_level()
            assert result == "INFO"

    def test_is_production(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_BACKEND": "environment"}):
            assert is_production() is True

    def test_is_development(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "development", "SECRET_BACKEND": "environment"}):
            assert is_development() is True

    def test_is_production_false(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "staging", "SECRET_BACKEND": "environment"}):
            assert is_production() is False

    def test_get_jwt_secret(self):
        with patch.dict(
            os.environ,
            {
                "JWT_SECRET_KEY": "test-secret-key-for-unit-tests-only-32chars",
                "SECRET_BACKEND": "environment",
            },
        ):
            result = get_jwt_secret()
            assert result == "test-secret-key-for-unit-tests-only-32chars"
