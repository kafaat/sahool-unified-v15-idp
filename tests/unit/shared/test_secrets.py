"""
Tests for Secrets Manager
اختبارات مدير الأسرار
"""

import os

import pytest

from shared.secrets.manager import (
    EnvironmentSecretsProvider,
    SecretBackend,
    SecretKey,
    SecretsManager,
    SecretsManagerConfig,
)


class TestSecretKey:
    """Tests for SecretKey enum"""

    def test_database_password_value(self):
        """Test DATABASE_PASSWORD key value"""
        assert SecretKey.DATABASE_PASSWORD.value == "database/password"

    def test_jwt_secret_value(self):
        """Test JWT_SECRET key value"""
        assert SecretKey.JWT_SECRET.value == "auth/jwt_secret"

    def test_stripe_api_key_value(self):
        """Test STRIPE_API_KEY key value"""
        assert SecretKey.STRIPE_API_KEY.value == "external/stripe_api_key"

    def test_redis_password_value(self):
        """Test REDIS_PASSWORD key value"""
        assert SecretKey.REDIS_PASSWORD.value == "cache/redis_password"

    def test_env_var_property(self):
        """Test env_var property conversion"""
        assert SecretKey.DATABASE_PASSWORD.env_var == "DATABASE_PASSWORD"
        assert SecretKey.JWT_SECRET.env_var == "AUTH_JWT_SECRET"
        assert SecretKey.STRIPE_API_KEY.env_var == "EXTERNAL_STRIPE_API_KEY"

    def test_all_keys_have_values(self):
        """Test all SecretKey members have non-empty values"""
        for key in SecretKey:
            assert key.value is not None
            assert len(key.value) > 0


class TestSecretBackend:
    """Tests for SecretBackend enum"""

    def test_environment_backend(self):
        """Test ENVIRONMENT backend value"""
        assert SecretBackend.ENVIRONMENT.value == "environment"

    def test_vault_backend(self):
        """Test VAULT backend value"""
        assert SecretBackend.VAULT.value == "vault"

    def test_aws_backend(self):
        """Test AWS_SECRETS_MANAGER backend value"""
        assert SecretBackend.AWS_SECRETS_MANAGER.value == "aws_secrets_manager"

    def test_azure_backend(self):
        """Test AZURE_KEY_VAULT backend value"""
        assert SecretBackend.AZURE_KEY_VAULT.value == "azure_key_vault"

    def test_from_env_default(self):
        """Test from_env() returns ENVIRONMENT by default"""
        original = os.environ.get("SECRET_BACKEND")
        if "SECRET_BACKEND" in os.environ:
            del os.environ["SECRET_BACKEND"]

        try:
            backend = SecretBackend.from_env()
            assert backend == SecretBackend.ENVIRONMENT
        finally:
            if original:
                os.environ["SECRET_BACKEND"] = original

    def test_from_env_vault(self):
        """Test from_env() returns VAULT when set"""
        original = os.environ.get("SECRET_BACKEND")
        os.environ["SECRET_BACKEND"] = "vault"

        try:
            backend = SecretBackend.from_env()
            assert backend == SecretBackend.VAULT
        finally:
            if original:
                os.environ["SECRET_BACKEND"] = original
            else:
                del os.environ["SECRET_BACKEND"]

    def test_from_env_invalid_falls_back(self):
        """Test from_env() falls back to ENVIRONMENT for invalid values"""
        original = os.environ.get("SECRET_BACKEND")
        os.environ["SECRET_BACKEND"] = "invalid_backend"

        try:
            backend = SecretBackend.from_env()
            assert backend == SecretBackend.ENVIRONMENT
        finally:
            if original:
                os.environ["SECRET_BACKEND"] = original
            else:
                del os.environ["SECRET_BACKEND"]


class TestSecretsManagerConfig:
    """Tests for SecretsManagerConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = SecretsManagerConfig()
        assert config.cache_enabled is True
        assert config.cache_ttl_seconds == 300
        assert config.fallback_to_env is True

    def test_custom_config(self):
        """Test custom configuration"""
        config = SecretsManagerConfig(
            backend=SecretBackend.VAULT,
            cache_enabled=False,
            cache_ttl_seconds=600,
            fallback_to_env=False,
        )
        assert config.backend == SecretBackend.VAULT
        assert config.cache_enabled is False
        assert config.cache_ttl_seconds == 600
        assert config.fallback_to_env is False


class TestEnvironmentSecretsProvider:
    """Tests for EnvironmentSecretsProvider"""

    @pytest.fixture
    def provider(self):
        """Create provider instance"""
        return EnvironmentSecretsProvider()

    @pytest.mark.asyncio
    async def test_connect(self, provider):
        """Test connect() returns True"""
        result = await provider.connect()
        assert result is True

    @pytest.mark.asyncio
    async def test_disconnect(self, provider):
        """Test disconnect() works"""
        await provider.connect()
        await provider.disconnect()
        # Should not raise

    @pytest.mark.asyncio
    async def test_get_secret_from_env(self, provider):
        """Test getting secret from environment variable"""
        await provider.connect()

        os.environ["TEST_SECRET_VALUE"] = "my_test_secret"
        try:
            value = await provider.get_secret("test/secret_value")
            assert value == "my_test_secret"
        finally:
            del os.environ["TEST_SECRET_VALUE"]

    @pytest.mark.asyncio
    async def test_get_secret_not_found(self, provider):
        """Test getting non-existent secret raises KeyError"""
        await provider.connect()

        with pytest.raises(KeyError):
            await provider.get_secret("nonexistent/secret/path")

    @pytest.mark.asyncio
    async def test_set_secret(self, provider):
        """Test setting secret in environment"""
        await provider.connect()

        await provider.set_secret("test/new_secret", "new_value")
        assert os.environ.get("TEST_NEW_SECRET") == "new_value"

        # Cleanup
        del os.environ["TEST_NEW_SECRET"]

    @pytest.mark.asyncio
    async def test_delete_secret(self, provider):
        """Test deleting secret from environment"""
        await provider.connect()

        os.environ["TEST_DELETE_SECRET"] = "to_delete"
        await provider.delete_secret("test/delete_secret")
        assert "TEST_DELETE_SECRET" not in os.environ

    @pytest.mark.asyncio
    async def test_health_check(self, provider):
        """Test health check returns correct structure"""
        await provider.connect()

        health = await provider.health_check()
        assert health["healthy"] is True
        assert health["backend"] == "environment"
        assert health["connected"] is True

    def test_path_to_env_var(self, provider):
        """Test path to environment variable conversion"""
        assert provider._path_to_env_var("database/password") == "DATABASE_PASSWORD"
        assert provider._path_to_env_var("auth/jwt_secret") == "AUTH_JWT_SECRET"
        assert provider._path_to_env_var("external/api/key") == "EXTERNAL_API_KEY"


class TestSecretsManager:
    """Tests for SecretsManager"""

    @pytest.fixture
    def manager(self):
        """Create manager instance with environment backend"""
        config = SecretsManagerConfig(backend=SecretBackend.ENVIRONMENT)
        return SecretsManager(config)

    @pytest.mark.asyncio
    async def test_initialize(self, manager):
        """Test manager initialization"""
        result = await manager.initialize()
        assert result is True
        assert manager._initialized is True

    @pytest.mark.asyncio
    async def test_shutdown(self, manager):
        """Test manager shutdown"""
        await manager.initialize()
        await manager.shutdown()
        assert manager._initialized is False

    @pytest.mark.asyncio
    async def test_get_secret_with_key_enum(self, manager):
        """Test getting secret using SecretKey enum"""
        await manager.initialize()

        os.environ["DATABASE_PASSWORD"] = "test_db_pass"
        try:
            value = await manager.get_secret(SecretKey.DATABASE_PASSWORD)
            assert value == "test_db_pass"
        finally:
            del os.environ["DATABASE_PASSWORD"]

    @pytest.mark.asyncio
    async def test_get_secret_with_string_path(self, manager):
        """Test getting secret using string path"""
        await manager.initialize()

        os.environ["CUSTOM_SECRET"] = "custom_value"
        try:
            value = await manager.get_secret("custom/secret")
            assert value == "custom_value"
        finally:
            del os.environ["CUSTOM_SECRET"]

    @pytest.mark.asyncio
    async def test_get_secret_with_default(self, manager):
        """Test getting non-existent secret returns default"""
        await manager.initialize()

        value = await manager.get_secret("nonexistent/path", default="default_value")
        assert value == "default_value"

    @pytest.mark.asyncio
    async def test_health_check(self, manager):
        """Test health check"""
        await manager.initialize()

        health = await manager.health_check()
        assert health["healthy"] is True
        assert health["initialized"] is True
