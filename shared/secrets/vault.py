"""
HashiCorp Vault Client for SAHOOL Platform
عميل HashiCorp Vault لمنصة سهول

Provides secure secrets management using HashiCorp Vault.
Supports both token-based and AppRole authentication.

Requirements:
    pip install hvac

Usage:
    from shared.secrets.vault import VaultClient, VaultConfig

    # Using token authentication
    config = VaultConfig(
        address="http://localhost:8200",
        token="your-vault-token"
    )
    client = VaultClient(config)
    await client.connect()
    secret = await client.get_secret("database/password")

    # Using AppRole authentication (recommended for production)
    config = VaultConfig(
        address="http://localhost:8200",
        role_id="your-role-id",
        secret_id="your-secret-id"
    )
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class VaultConfig:
    """HashiCorp Vault configuration"""

    # Vault server address
    address: str = field(
        default_factory=lambda: os.getenv("VAULT_ADDR", "http://localhost:8200")
    )

    # Authentication - Token based
    token: str | None = field(default_factory=lambda: os.getenv("VAULT_TOKEN"))

    # Authentication - AppRole based (recommended for production)
    role_id: str | None = field(default_factory=lambda: os.getenv("VAULT_ROLE_ID"))
    secret_id: str | None = field(default_factory=lambda: os.getenv("VAULT_SECRET_ID"))

    # Namespace (for Vault Enterprise)
    namespace: str | None = field(
        default_factory=lambda: os.getenv("VAULT_NAMESPACE")
    )

    # KV secrets engine configuration
    mount_point: str = field(
        default_factory=lambda: os.getenv("VAULT_MOUNT_POINT", "secret")
    )
    path_prefix: str = field(
        default_factory=lambda: os.getenv("VAULT_PATH_PREFIX", "sahool")
    )

    # Connection settings
    timeout: int = 30
    verify_ssl: bool = True
    ca_cert: str | None = None

    # Caching
    cache_ttl_seconds: int = 300  # 5 minutes
    enable_cache: bool = True

    # Token renewal
    auto_renew_token: bool = True
    renewal_threshold_seconds: int = 600  # Renew 10 minutes before expiry

    @property
    def use_approle(self) -> bool:
        """Check if AppRole authentication should be used"""
        return bool(self.role_id and self.secret_id)

    @classmethod
    def from_env(cls) -> "VaultConfig":
        """Create config from environment variables"""
        return cls()

    def validate(self) -> None:
        """Validate configuration"""
        if not self.address:
            raise ValueError("VAULT_ADDR is required")

        if not self.token and not (self.role_id and self.secret_id):
            raise ValueError(
                "Either VAULT_TOKEN or both VAULT_ROLE_ID and VAULT_SECRET_ID are required"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Vault Client
# ═══════════════════════════════════════════════════════════════════════════════


class VaultClient:
    """
    HashiCorp Vault client for SAHOOL platform.

    Provides async interface for secrets management with:
    - Token and AppRole authentication
    - Automatic token renewal
    - Secret caching
    - KV v2 secrets engine support
    """

    def __init__(self, config: VaultConfig | None = None):
        self.config = config or VaultConfig.from_env()
        self._client: Any = None
        self._connected = False
        self._cache: dict[str, tuple[Any, datetime]] = {}
        self._token_expiry: datetime | None = None
        self._renewal_task: asyncio.Task | None = None

    async def connect(self) -> bool:
        """
        Connect to Vault and authenticate.

        Returns:
            True if connection successful
        """
        try:
            # Import hvac here to make it optional
            try:
                import hvac
            except ImportError:
                logger.error(
                    "hvac library not installed. Install with: pip install hvac"
                )
                raise ImportError(
                    "hvac library required for Vault integration. "
                    "Install with: pip install hvac"
                )

            self.config.validate()

            # Create client
            self._client = hvac.Client(
                url=self.config.address,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl if self.config.ca_cert is None else self.config.ca_cert,
                namespace=self.config.namespace,
            )

            # Authenticate
            if self.config.use_approle:
                await self._authenticate_approle()
            else:
                self._client.token = self.config.token
                if not self._client.is_authenticated():
                    raise ConnectionError("Invalid Vault token")

            self._connected = True
            logger.info(f"Connected to Vault at {self.config.address}")

            # Start token renewal if enabled
            if self.config.auto_renew_token:
                self._start_token_renewal()

            return True

        except Exception as e:
            logger.error(f"Failed to connect to Vault: {e}")
            self._connected = False
            raise

    async def _authenticate_approle(self) -> None:
        """Authenticate using AppRole"""
        try:
            response = self._client.auth.approle.login(
                role_id=self.config.role_id,
                secret_id=self.config.secret_id,
            )
            self._client.token = response["auth"]["client_token"]

            # Store token expiry
            ttl = response["auth"].get("lease_duration", 3600)
            self._token_expiry = datetime.now(UTC) + timedelta(seconds=ttl)

            logger.info("Successfully authenticated with AppRole")

        except Exception as e:
            logger.error(f"AppRole authentication failed: {e}")
            raise

    def _start_token_renewal(self) -> None:
        """Start background task for token renewal"""
        if self._renewal_task is not None:
            return

        async def renewal_loop():
            while self._connected:
                try:
                    await asyncio.sleep(60)  # Check every minute

                    if self._token_expiry is None:
                        continue

                    # Check if renewal is needed
                    time_until_expiry = (
                        self._token_expiry - datetime.now(UTC)
                    ).total_seconds()

                    if time_until_expiry < self.config.renewal_threshold_seconds:
                        await self._renew_token()

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Token renewal error: {e}")

        self._renewal_task = asyncio.create_task(renewal_loop())

    async def _renew_token(self) -> None:
        """Renew the current token"""
        try:
            if self.config.use_approle:
                # Re-authenticate with AppRole
                await self._authenticate_approle()
            else:
                # Renew existing token
                response = self._client.auth.token.renew_self()
                ttl = response["auth"].get("lease_duration", 3600)
                self._token_expiry = datetime.now(UTC) + timedelta(seconds=ttl)

            logger.info("Vault token renewed successfully")

        except Exception as e:
            logger.error(f"Failed to renew Vault token: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Vault"""
        if self._renewal_task:
            self._renewal_task.cancel()
            try:
                await self._renewal_task
            except asyncio.CancelledError:
                pass
            self._renewal_task = None

        self._connected = False
        self._client = None
        self._cache.clear()
        logger.info("Disconnected from Vault")

    def is_connected(self) -> bool:
        """Check if connected to Vault"""
        return self._connected and self._client is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Secret Operations
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_full_path(self, path: str) -> str:
        """Get full secret path with prefix"""
        if self.config.path_prefix:
            return f"{self.config.path_prefix}/{path}"
        return path

    def _get_from_cache(self, path: str) -> Any | None:
        """Get secret from cache if valid"""
        if not self.config.enable_cache:
            return None

        if path not in self._cache:
            return None

        value, cached_at = self._cache[path]
        age = (datetime.now(UTC) - cached_at).total_seconds()

        if age > self.config.cache_ttl_seconds:
            del self._cache[path]
            return None

        return value

    def _set_cache(self, path: str, value: Any) -> None:
        """Store secret in cache"""
        if self.config.enable_cache:
            self._cache[path] = (value, datetime.now(UTC))

    async def get_secret(self, path: str, key: str | None = None) -> Any:
        """
        Get a secret from Vault.

        Args:
            path: Secret path (e.g., "database/credentials")
            key: Specific key within the secret (optional)

        Returns:
            Secret value or entire secret dict if key not specified

        Example:
            # Get entire secret
            creds = await client.get_secret("database/credentials")
            # {"username": "admin", "password": "secret123"}

            # Get specific key
            password = await client.get_secret("database/credentials", "password")
            # "secret123"
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Vault")

        full_path = self._get_full_path(path)
        cache_key = f"{full_path}:{key}" if key else full_path

        # Check cache
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # Read from Vault (KV v2)
            response = self._client.secrets.kv.v2.read_secret_version(
                path=full_path,
                mount_point=self.config.mount_point,
            )

            data = response["data"]["data"]

            if key:
                if key not in data:
                    raise KeyError(f"Key '{key}' not found in secret '{path}'")
                value = data[key]
            else:
                value = data

            # Cache the result
            self._set_cache(cache_key, value)

            return value

        except Exception as e:
            logger.error(f"Failed to get secret '{path}': {e}")
            raise

    async def set_secret(self, path: str, data: dict[str, Any]) -> None:
        """
        Set a secret in Vault.

        Args:
            path: Secret path
            data: Secret data as dictionary

        Example:
            await client.set_secret("database/credentials", {
                "username": "admin",
                "password": "new-secure-password"
            })
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Vault")

        full_path = self._get_full_path(path)

        try:
            self._client.secrets.kv.v2.create_or_update_secret(
                path=full_path,
                secret=data,
                mount_point=self.config.mount_point,
            )

            # Invalidate cache
            keys_to_remove = [k for k in self._cache if k.startswith(full_path)]
            for k in keys_to_remove:
                del self._cache[k]

            logger.info(f"Secret '{path}' updated successfully")

        except Exception as e:
            logger.error(f"Failed to set secret '{path}': {e}")
            raise

    async def delete_secret(self, path: str) -> None:
        """
        Delete a secret from Vault.

        Args:
            path: Secret path to delete
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Vault")

        full_path = self._get_full_path(path)

        try:
            self._client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=full_path,
                mount_point=self.config.mount_point,
            )

            # Invalidate cache
            keys_to_remove = [k for k in self._cache if k.startswith(full_path)]
            for k in keys_to_remove:
                del self._cache[k]

            logger.info(f"Secret '{path}' deleted successfully")

        except Exception as e:
            logger.error(f"Failed to delete secret '{path}': {e}")
            raise

    async def list_secrets(self, path: str = "") -> list[str]:
        """
        List secrets at a path.

        Args:
            path: Path to list (empty for root)

        Returns:
            List of secret names/paths
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Vault")

        full_path = self._get_full_path(path) if path else self.config.path_prefix

        try:
            response = self._client.secrets.kv.v2.list_secrets(
                path=full_path,
                mount_point=self.config.mount_point,
            )
            return response["data"]["keys"]

        except Exception as e:
            logger.error(f"Failed to list secrets at '{path}': {e}")
            raise

    # ═══════════════════════════════════════════════════════════════════════════
    # Batch Operations
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_secrets_batch(
        self, paths: list[str]
    ) -> dict[str, Any]:
        """
        Get multiple secrets in batch.

        Args:
            paths: List of secret paths

        Returns:
            Dictionary mapping paths to their values
        """
        results = {}
        for path in paths:
            try:
                results[path] = await self.get_secret(path)
            except Exception as e:
                logger.warning(f"Failed to get secret '{path}': {e}")
                results[path] = None
        return results

    # ═══════════════════════════════════════════════════════════════════════════
    # Health & Status
    # ═══════════════════════════════════════════════════════════════════════════

    async def health_check(self) -> dict[str, Any]:
        """
        Check Vault health status.

        Returns:
            Health status dictionary
        """
        if not self._client:
            return {
                "healthy": False,
                "connected": False,
                "error": "Client not initialized",
            }

        try:
            status = self._client.sys.read_health_status(method="GET")
            return {
                "healthy": True,
                "connected": self._connected,
                "initialized": status.get("initialized", False),
                "sealed": status.get("sealed", True),
                "version": status.get("version", "unknown"),
            }
        except Exception as e:
            return {
                "healthy": False,
                "connected": self._connected,
                "error": str(e),
            }

    def clear_cache(self) -> None:
        """Clear the secret cache"""
        self._cache.clear()
        logger.info("Vault secret cache cleared")


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience Functions
# ═══════════════════════════════════════════════════════════════════════════════

_vault_client: VaultClient | None = None


async def get_vault_client() -> VaultClient:
    """
    Get or create the global Vault client.

    Returns:
        Connected VaultClient instance
    """
    global _vault_client

    if _vault_client is None or not _vault_client.is_connected():
        _vault_client = VaultClient()
        await _vault_client.connect()

    return _vault_client


async def close_vault_client() -> None:
    """Close the global Vault client"""
    global _vault_client

    if _vault_client:
        await _vault_client.disconnect()
        _vault_client = None
