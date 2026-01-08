"""
Unified Secrets Manager for SAHOOL Platform
مدير الأسرار الموحد لمنصة سهول

Multi-backend secrets management with automatic backend detection.
Supports environment variables, HashiCorp Vault, AWS Secrets Manager,
and Azure Key Vault.

Usage:
    from shared.secrets import get_secrets_manager, SecretKey

    # Auto-detect backend from SECRET_BACKEND env var
    secrets = get_secrets_manager()

    # Get a secret
    db_password = await secrets.get_secret(SecretKey.DATABASE_PASSWORD)

    # Or get by custom path
    api_key = await secrets.get_secret("external/api_key")
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Secret Keys
# ═══════════════════════════════════════════════════════════════════════════════


class SecretKey(str, Enum):
    """
    Standard secret keys used by SAHOOL platform.

    Maps logical names to paths/environment variables.
    """

    # Database
    DATABASE_PASSWORD = "database/password"
    DATABASE_URL = "database/url"

    # JWT
    JWT_SECRET = "auth/jwt_secret"
    JWT_PRIVATE_KEY = "auth/jwt_private_key"
    JWT_PUBLIC_KEY = "auth/jwt_public_key"

    # API Keys
    OPENWEATHER_API_KEY = "external/openweather_api_key"
    STRIPE_API_KEY = "external/stripe_api_key"
    STRIPE_WEBHOOK_SECRET = "external/stripe_webhook_secret"
    ANTHROPIC_API_KEY = "external/anthropic_api_key"
    OPENAI_API_KEY = "external/openai_api_key"
    GOOGLE_API_KEY = "external/google_api_key"

    # Satellite Imagery
    SENTINEL_HUB_CLIENT_ID = "external/sentinel_hub_client_id"
    SENTINEL_HUB_CLIENT_SECRET = "external/sentinel_hub_client_secret"
    PLANET_API_KEY = "external/planet_api_key"

    # Communication
    SMTP_PASSWORD = "communication/smtp_password"
    TWILIO_AUTH_TOKEN = "communication/twilio_auth_token"
    FCM_SERVER_KEY = "communication/fcm_server_key"

    # Redis
    REDIS_PASSWORD = "cache/redis_password"

    # App Secrets
    APP_SECRET_KEY = "app/secret_key"
    SIGNATURE_SECRET_KEY = "app/signature_secret"
    ENCRYPTION_KEY = "app/encryption_key"

    # OAuth
    GOOGLE_CLIENT_SECRET = "oauth/google_client_secret"
    FACEBOOK_CLIENT_SECRET = "oauth/facebook_client_secret"

    @property
    def env_var(self) -> str:
        """Get environment variable name for this secret"""
        return self.value.replace("/", "_").upper()


# ═══════════════════════════════════════════════════════════════════════════════
# Backend Enum
# ═══════════════════════════════════════════════════════════════════════════════


class SecretBackend(str, Enum):
    """Supported secrets backends"""

    ENVIRONMENT = "environment"
    VAULT = "vault"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"

    @classmethod
    def from_env(cls) -> "SecretBackend":
        """Get backend from environment"""
        backend = os.getenv("SECRET_BACKEND", "environment").lower()
        try:
            return cls(backend)
        except ValueError:
            logger.warning(f"Unknown SECRET_BACKEND '{backend}', defaulting to environment")
            return cls.ENVIRONMENT


# ═══════════════════════════════════════════════════════════════════════════════
# Base Provider
# ═══════════════════════════════════════════════════════════════════════════════


class SecretsProvider(ABC):
    """Abstract base class for secrets providers"""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the secrets backend"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the secrets backend"""
        pass

    @abstractmethod
    async def get_secret(self, path: str) -> Any:
        """Get a secret value"""
        pass

    @abstractmethod
    async def set_secret(self, path: str, value: Any) -> None:
        """Set a secret value"""
        pass

    @abstractmethod
    async def delete_secret(self, path: str) -> None:
        """Delete a secret"""
        pass

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Check provider health"""
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# Environment Provider
# ═══════════════════════════════════════════════════════════════════════════════


class EnvironmentSecretsProvider(SecretsProvider):
    """
    Secrets provider using environment variables.

    Best for development and simple deployments.
    Maps paths like 'database/password' to 'DATABASE_PASSWORD' env var.
    """

    def __init__(self):
        self._connected = False

    async def connect(self) -> bool:
        self._connected = True
        logger.info("Environment secrets provider initialized")
        return True

    async def disconnect(self) -> None:
        self._connected = False

    def _path_to_env_var(self, path: str) -> str:
        """Convert path to environment variable name"""
        return path.replace("/", "_").upper()

    async def get_secret(self, path: str) -> Any:
        env_var = self._path_to_env_var(path)
        value = os.getenv(env_var)

        if value is None:
            # Try common variations
            variations = [
                env_var,
                env_var.replace("_", ""),
                f"SAHOOL_{env_var}",
            ]
            for var in variations:
                value = os.getenv(var)
                if value is not None:
                    break

        if value is None:
            raise KeyError(f"Secret not found: {path} (env: {env_var})")

        return value

    async def set_secret(self, path: str, value: Any) -> None:
        env_var = self._path_to_env_var(path)
        os.environ[env_var] = str(value)
        logger.warning(f"Set secret in environment (not persistent): {env_var}")

    async def delete_secret(self, path: str) -> None:
        env_var = self._path_to_env_var(path)
        if env_var in os.environ:
            del os.environ[env_var]

    async def health_check(self) -> dict[str, Any]:
        return {
            "healthy": True,
            "backend": "environment",
            "connected": self._connected,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Vault Provider
# ═══════════════════════════════════════════════════════════════════════════════


class VaultSecretsProvider(SecretsProvider):
    """
    Secrets provider using HashiCorp Vault.

    Recommended for production environments.
    """

    def __init__(self):
        from .vault import VaultClient

        self._client = VaultClient()

    async def connect(self) -> bool:
        return await self._client.connect()

    async def disconnect(self) -> None:
        await self._client.disconnect()

    async def get_secret(self, path: str) -> Any:
        return await self._client.get_secret(path)

    async def set_secret(self, path: str, value: Any) -> None:
        if isinstance(value, dict):
            await self._client.set_secret(path, value)
        else:
            await self._client.set_secret(path, {"value": value})

    async def delete_secret(self, path: str) -> None:
        await self._client.delete_secret(path)

    async def health_check(self) -> dict[str, Any]:
        result = await self._client.health_check()
        result["backend"] = "vault"
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# AWS Secrets Manager Provider (Stub)
# ═══════════════════════════════════════════════════════════════════════════════


class AWSSecretsProvider(SecretsProvider):
    """
    Secrets provider using AWS Secrets Manager.

    Requirements:
        pip install boto3

    Note: Full implementation requires boto3 library.
    """

    def __init__(self):
        self._client = None
        self._connected = False
        self._prefix = os.getenv("AWS_SECRETS_PREFIX", "sahool/")

    async def connect(self) -> bool:
        try:
            import boto3

            self._client = boto3.client(
                "secretsmanager",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
            )
            self._connected = True
            logger.info("AWS Secrets Manager provider initialized")
            return True
        except ImportError:
            raise ImportError(
                "boto3 library required for AWS Secrets Manager. Install with: pip install boto3"
            )

    async def disconnect(self) -> None:
        self._connected = False
        self._client = None

    async def get_secret(self, path: str) -> Any:
        if not self._client:
            raise ConnectionError("AWS client not connected")

        secret_name = f"{self._prefix}{path}"
        try:
            response = self._client.get_secret_value(SecretId=secret_name)
            return response.get("SecretString")
        except Exception as e:
            raise KeyError(f"Secret not found: {path}") from e

    async def set_secret(self, path: str, value: Any) -> None:
        if not self._client:
            raise ConnectionError("AWS client not connected")

        import json

        secret_name = f"{self._prefix}{path}"
        secret_value = json.dumps(value) if isinstance(value, dict) else str(value)

        try:
            self._client.put_secret_value(SecretId=secret_name, SecretString=secret_value)
        except self._client.exceptions.ResourceNotFoundException:
            self._client.create_secret(Name=secret_name, SecretString=secret_value)

    async def delete_secret(self, path: str) -> None:
        if not self._client:
            raise ConnectionError("AWS client not connected")

        secret_name = f"{self._prefix}{path}"
        self._client.delete_secret(SecretId=secret_name, ForceDeleteWithoutRecovery=True)

    async def health_check(self) -> dict[str, Any]:
        return {
            "healthy": self._connected,
            "backend": "aws_secrets_manager",
            "connected": self._connected,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Azure Key Vault Provider (Stub)
# ═══════════════════════════════════════════════════════════════════════════════


class AzureSecretsProvider(SecretsProvider):
    """
    Secrets provider using Azure Key Vault.

    Requirements:
        pip install azure-keyvault-secrets azure-identity

    Note: Full implementation requires Azure SDK.
    """

    def __init__(self):
        self._client = None
        self._connected = False
        self._vault_url = os.getenv("AZURE_KEY_VAULT_URL")

    async def connect(self) -> bool:
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            if not self._vault_url:
                raise ValueError("AZURE_KEY_VAULT_URL is required")

            credential = DefaultAzureCredential()
            self._client = SecretClient(vault_url=self._vault_url, credential=credential)
            self._connected = True
            logger.info("Azure Key Vault provider initialized")
            return True
        except ImportError:
            raise ImportError(
                "Azure SDK required for Azure Key Vault. "
                "Install with: pip install azure-keyvault-secrets azure-identity"
            )

    async def disconnect(self) -> None:
        self._connected = False
        self._client = None

    def _normalize_name(self, path: str) -> str:
        """Azure doesn't allow / in names, convert to -"""
        return path.replace("/", "-").replace("_", "-")

    async def get_secret(self, path: str) -> Any:
        if not self._client:
            raise ConnectionError("Azure client not connected")

        name = self._normalize_name(path)
        try:
            secret = self._client.get_secret(name)
            return secret.value
        except Exception as e:
            raise KeyError(f"Secret not found: {path}") from e

    async def set_secret(self, path: str, value: Any) -> None:
        if not self._client:
            raise ConnectionError("Azure client not connected")

        import json

        name = self._normalize_name(path)
        secret_value = json.dumps(value) if isinstance(value, dict) else str(value)
        self._client.set_secret(name, secret_value)

    async def delete_secret(self, path: str) -> None:
        if not self._client:
            raise ConnectionError("Azure client not connected")

        name = self._normalize_name(path)
        self._client.begin_delete_secret(name)

    async def health_check(self) -> dict[str, Any]:
        return {
            "healthy": self._connected,
            "backend": "azure_key_vault",
            "connected": self._connected,
            "vault_url": self._vault_url,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Unified Secrets Manager
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SecretsManagerConfig:
    """Secrets manager configuration"""

    backend: SecretBackend = SecretBackend.ENVIRONMENT
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    fallback_to_env: bool = True  # Fall back to env vars if secret not found


class SecretsManager:
    """
    Unified secrets manager for SAHOOL platform.

    Provides a single interface for accessing secrets from multiple backends.
    Automatically detects backend from SECRET_BACKEND environment variable.

    Usage:
        manager = SecretsManager()
        await manager.initialize()

        # Get secret by key enum
        password = await manager.get_secret(SecretKey.DATABASE_PASSWORD)

        # Get secret by path
        api_key = await manager.get_secret("external/custom_api_key")
    """

    def __init__(self, config: SecretsManagerConfig | None = None):
        self.config = config or SecretsManagerConfig(backend=SecretBackend.from_env())
        self._provider: SecretsProvider | None = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the secrets manager"""
        if self._initialized:
            return True

        # Create provider based on backend
        provider_map = {
            SecretBackend.ENVIRONMENT: EnvironmentSecretsProvider,
            SecretBackend.VAULT: VaultSecretsProvider,
            SecretBackend.AWS_SECRETS_MANAGER: AWSSecretsProvider,
            SecretBackend.AZURE_KEY_VAULT: AzureSecretsProvider,
        }

        provider_class = provider_map.get(self.config.backend)
        if not provider_class:
            raise ValueError(f"Unknown backend: {self.config.backend}")

        self._provider = provider_class()

        try:
            await self._provider.connect()
            self._initialized = True
            logger.info(f"Secrets manager initialized with {self.config.backend.value} backend")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize secrets manager: {e}")

            # Fall back to environment if configured
            if self.config.fallback_to_env and self.config.backend != SecretBackend.ENVIRONMENT:
                logger.warning("Falling back to environment secrets provider")
                self._provider = EnvironmentSecretsProvider()
                await self._provider.connect()
                self._initialized = True
                return True

            raise

    async def shutdown(self) -> None:
        """Shutdown the secrets manager"""
        if self._provider:
            await self._provider.disconnect()
        self._initialized = False

    async def get_secret(self, key: SecretKey | str, default: Any = None) -> Any:
        """
        Get a secret value.

        Args:
            key: SecretKey enum or string path
            default: Default value if secret not found

        Returns:
            Secret value or default
        """
        if not self._initialized:
            await self.initialize()

        path = key.value if isinstance(key, SecretKey) else key

        try:
            return await self._provider.get_secret(path)
        except KeyError:
            if default is not None:
                return default

            # Try fallback to environment
            if self.config.fallback_to_env and self.config.backend != SecretBackend.ENVIRONMENT:
                env_var = path.replace("/", "_").upper()
                value = os.getenv(env_var)
                if value is not None:
                    return value

            raise

    async def set_secret(self, key: SecretKey | str, value: Any) -> None:
        """Set a secret value"""
        if not self._initialized:
            await self.initialize()

        path = key.value if isinstance(key, SecretKey) else key
        await self._provider.set_secret(path, value)

    async def delete_secret(self, key: SecretKey | str) -> None:
        """Delete a secret"""
        if not self._initialized:
            await self.initialize()

        path = key.value if isinstance(key, SecretKey) else key
        await self._provider.delete_secret(path)

    async def health_check(self) -> dict[str, Any]:
        """Check secrets manager health"""
        if not self._provider:
            return {"healthy": False, "initialized": False}

        result = await self._provider.health_check()
        result["initialized"] = self._initialized
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# Global Instance
# ═══════════════════════════════════════════════════════════════════════════════

_secrets_manager: SecretsManager | None = None


def get_secrets_manager() -> SecretsManager:
    """
    Get or create the global secrets manager.

    Note: Call initialize() before using.

    Returns:
        SecretsManager instance
    """
    global _secrets_manager

    if _secrets_manager is None:
        _secrets_manager = SecretsManager()

    return _secrets_manager


async def initialize_secrets() -> SecretsManager:
    """
    Initialize and return the global secrets manager.

    Convenience function that creates and initializes the manager.
    """
    manager = get_secrets_manager()
    await manager.initialize()
    return manager


async def shutdown_secrets() -> None:
    """Shutdown the global secrets manager"""
    global _secrets_manager

    if _secrets_manager:
        await _secrets_manager.shutdown()
        _secrets_manager = None
