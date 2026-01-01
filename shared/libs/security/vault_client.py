"""
SAHOOL Vault Client
Unified HashiCorp Vault client for secrets management
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Optional dependency
try:
    import hvac

    HAS_HVAC = True
except ImportError:
    hvac = None  # type: ignore
    HAS_HVAC = False


@dataclass(frozen=True)
class VaultConfig:
    """
    Vault connection configuration.

    In production, use AppRole or Kubernetes auth instead of token.
    """

    addr: str
    token: Optional[str] = None
    namespace: Optional[str] = None
    # For AppRole auth
    role_id: Optional[str] = None
    secret_id: Optional[str] = None


class VaultClient:
    """
    Unified Vault client for secrets management.

    Provides a consistent interface for reading secrets from Vault
    across all SAHOOL services.

    Example:
        ```python
        from shared.libs.security.vault_client import VaultClient, VaultConfig

        cfg = VaultConfig(addr="http://localhost:8200", token="dev-token")
        client = VaultClient(cfg)

        db_creds = client.read_kv("database/postgres")
        print(db_creds["username"])
        ```
    """

    def __init__(self, cfg: VaultConfig):
        if not HAS_HVAC:
            raise RuntimeError("hvac is not installed. Install with: pip install hvac")

        self._cfg = cfg
        self._client = hvac.Client(
            url=cfg.addr,
            token=cfg.token,
            namespace=cfg.namespace,
        )

        # Use AppRole auth if configured
        if cfg.role_id and cfg.secret_id:
            self._authenticate_approle()

    def _authenticate_approle(self) -> None:
        """Authenticate using AppRole"""
        response = self._client.auth.approle.login(
            role_id=self._cfg.role_id,
            secret_id=self._cfg.secret_id,
        )
        self._client.token = response["auth"]["client_token"]
        logger.info("Authenticated with Vault using AppRole")

    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated"""
        return self._client.is_authenticated()

    def read_kv(self, path: str, mount_point: str = "secret") -> dict[str, Any]:
        """
        Read a secret from KV v2 secrets engine.

        Args:
            path: Secret path (e.g., 'database/postgres')
            mount_point: KV mount point (default: 'secret')

        Returns:
            Dictionary of secret key-value pairs

        Raises:
            hvac.exceptions.InvalidPath: If secret doesn't exist
        """
        response = self._client.secrets.kv.v2.read_secret_version(
            path=path,
            mount_point=mount_point,
        )
        return response["data"]["data"]

    def write_kv(
        self,
        path: str,
        data: dict[str, Any],
        mount_point: str = "secret",
    ) -> None:
        """
        Write a secret to KV v2 secrets engine.

        Args:
            path: Secret path
            data: Secret data to write
            mount_point: KV mount point
        """
        self._client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=data,
            mount_point=mount_point,
        )
        logger.info(f"Wrote secret to {mount_point}/{path}")

    def read_database_creds(self, role: str) -> dict[str, str]:
        """
        Read dynamic database credentials.

        Requires database secrets engine to be configured.

        Args:
            role: Database role name

        Returns:
            Dict with 'username' and 'password'
        """
        response = self._client.secrets.database.generate_credentials(name=role)
        return {
            "username": response["data"]["username"],
            "password": response["data"]["password"],
        }

    def get_secret_or_env(
        self,
        vault_path: str,
        vault_key: str,
        env_var: str,
        mount_point: str = "secret",
    ) -> str:
        """
        Get a secret from Vault, falling back to environment variable.

        Useful during migration from ENV-based to Vault-based secrets.

        Args:
            vault_path: Vault secret path
            vault_key: Key within the secret
            env_var: Environment variable to fall back to
            mount_point: KV mount point

        Returns:
            Secret value

        Raises:
            ValueError: If secret not found in Vault or ENV
        """
        try:
            secrets = self.read_kv(vault_path, mount_point)
            if vault_key in secrets:
                return secrets[vault_key]
        except Exception as e:
            logger.warning(f"Failed to read from Vault: {e}")

        value = os.getenv(env_var)
        if value:
            logger.info(f"Using {env_var} from environment (Vault fallback)")
            return value

        raise ValueError(
            f"Secret not found in Vault ({vault_path}/{vault_key}) "
            f"or environment ({env_var})"
        )


def from_env() -> VaultClient:
    """
    Create a VaultClient from environment variables.

    Environment variables:
        VAULT_ADDR: Vault server address (default: http://localhost:8200)
        VAULT_TOKEN: Vault token (for token auth)
        VAULT_NAMESPACE: Vault namespace (optional)
        VAULT_ROLE_ID: AppRole role ID (for AppRole auth)
        VAULT_SECRET_ID: AppRole secret ID (for AppRole auth)

    Returns:
        Configured VaultClient

    Raises:
        RuntimeError: If neither token nor AppRole credentials are provided
    """
    addr = os.getenv("VAULT_ADDR", "http://localhost:8200")
    token = os.getenv("VAULT_TOKEN")
    namespace = os.getenv("VAULT_NAMESPACE")
    role_id = os.getenv("VAULT_ROLE_ID")
    secret_id = os.getenv("VAULT_SECRET_ID")

    if not token and not (role_id and secret_id):
        raise RuntimeError("VAULT_TOKEN or (VAULT_ROLE_ID + VAULT_SECRET_ID) required")

    return VaultClient(
        VaultConfig(
            addr=addr,
            token=token,
            namespace=namespace,
            role_id=role_id,
            secret_id=secret_id,
        )
    )


class MockVaultClient:
    """
    Mock Vault client for testing.

    Use this in tests to avoid requiring a real Vault server.
    """

    def __init__(self, secrets: Optional[dict[str, dict[str, Any]]] = None):
        self._secrets = secrets or {}

    @property
    def is_authenticated(self) -> bool:
        return True

    def read_kv(self, path: str, mount_point: str = "secret") -> dict[str, Any]:
        key = f"{mount_point}/{path}"
        if key not in self._secrets:
            raise KeyError(f"Secret not found: {key}")
        return self._secrets[key]

    def write_kv(
        self,
        path: str,
        data: dict[str, Any],
        mount_point: str = "secret",
    ) -> None:
        key = f"{mount_point}/{path}"
        self._secrets[key] = data
