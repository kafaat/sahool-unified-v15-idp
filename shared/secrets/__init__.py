"""
SAHOOL Secrets Management Package
إدارة الأسرار لمنصة سهول

Multi-backend secrets management supporting:
- Environment variables (default/development)
- HashiCorp Vault (recommended for production)
- AWS Secrets Manager
- Azure Key Vault

Usage:
    from shared.secrets import get_secrets_manager, SecretKey

    # Get secrets manager (auto-detects backend from SECRET_BACKEND env var)
    secrets = get_secrets_manager()

    # Retrieve a secret
    db_password = await secrets.get_secret(SecretKey.DATABASE_PASSWORD)
"""

from .manager import (
    SecretBackend,
    SecretKey,
    SecretsManager,
    get_secrets_manager,
    initialize_secrets,
)
from .vault import VaultClient, VaultConfig

__all__ = [
    "SecretBackend",
    "SecretKey",
    "SecretsManager",
    "get_secrets_manager",
    "initialize_secrets",
    "VaultClient",
    "VaultConfig",
]
