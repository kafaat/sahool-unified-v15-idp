"""
Configuration Management with Secrets Externalization
إدارة التكوين مع إخراج الأسرار

Supports multiple secret backends:
- Environment variables (default)
- HashiCorp Vault
- AWS Secrets Manager (future)
- Azure Key Vault (future)
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import json


logger = logging.getLogger(__name__)


class SecretBackend(str, Enum):
    """Supported secret backends"""
    ENVIRONMENT = "environment"
    VAULT = "vault"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    AZURE_KEY_VAULT = "azure_key_vault"


@dataclass
class SecretConfig:
    """Configuration for secret management"""
    backend: SecretBackend = SecretBackend.ENVIRONMENT
    
    # Vault configuration
    vault_addr: Optional[str] = None
    vault_token: Optional[str] = None
    vault_role_id: Optional[str] = None
    vault_secret_id: Optional[str] = None
    vault_namespace: Optional[str] = None
    vault_mount_point: str = "secret"
    vault_path_prefix: str = "sahool"
    
    # Fallback configuration
    allow_env_fallback: bool = True  # Allow fallback to environment variables on Vault failure
    
    # Cache configuration
    cache_ttl_seconds: int = 300  # 5 minutes
    cache_enabled: bool = True


class SecretManager:
    """
    Unified secret manager with multiple backend support.
    مدير الأسرار الموحد مع دعم الخلفيات المتعددة.
    """
    
    def __init__(self, config: Optional[SecretConfig] = None):
        self.config = config or SecretConfig()
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._vault_client = None
        
        # Initialize backend
        if self.config.backend == SecretBackend.VAULT:
            self._init_vault()
    
    def _init_vault(self) -> None:
        """Initialize HashiCorp Vault client"""
        try:
            import hvac
            
            vault_addr = self.config.vault_addr or os.getenv("VAULT_ADDR")
            if not vault_addr:
                if self.config.allow_env_fallback:
                    logger.warning(
                        "Vault address not configured, falling back to environment variables. "
                        "Set VAULT_ADDR or disable Vault backend."
                    )
                    self.config.backend = SecretBackend.ENVIRONMENT
                else:
                    raise ValueError("Vault address not configured and env fallback is disabled")
                return
            
            self._vault_client = hvac.Client(url=vault_addr)
            
            # Authenticate using token or AppRole
            if self.config.vault_token or os.getenv("VAULT_TOKEN"):
                token = self.config.vault_token or os.getenv("VAULT_TOKEN")
                self._vault_client.token = token
            elif self.config.vault_role_id or os.getenv("VAULT_ROLE_ID"):
                role_id = self.config.vault_role_id or os.getenv("VAULT_ROLE_ID")
                secret_id = self.config.vault_secret_id or os.getenv("VAULT_SECRET_ID")
                
                auth_response = self._vault_client.auth.approle.login(
                    role_id=role_id,
                    secret_id=secret_id,
                )
                self._vault_client.token = auth_response["auth"]["client_token"]
            else:
                if self.config.allow_env_fallback:
                    logger.warning(
                        "Vault authentication not configured, falling back to environment variables. "
                        "Set VAULT_TOKEN or VAULT_ROLE_ID/VAULT_SECRET_ID."
                    )
                    self.config.backend = SecretBackend.ENVIRONMENT
                else:
                    raise ValueError("Vault authentication not configured and env fallback is disabled")
                return
            
            # Verify connection
            if not self._vault_client.is_authenticated():
                if self.config.allow_env_fallback:
                    logger.warning(
                        "Vault authentication failed, falling back to environment variables. "
                        "Set allow_env_fallback=False to make this an error."
                    )
                    self.config.backend = SecretBackend.ENVIRONMENT
                else:
                    raise RuntimeError("Vault authentication failed and env fallback is disabled")
                
        except ImportError:
            if self.config.allow_env_fallback:
                logger.warning(
                    "hvac library not installed, falling back to environment variables. "
                    "Install with: pip install hvac"
                )
                self.config.backend = SecretBackend.ENVIRONMENT
            else:
                raise ImportError("hvac library required for Vault backend. Install with: pip install hvac")
        except Exception as e:
            if self.config.allow_env_fallback:
                logger.error(
                    f"Failed to initialize Vault: {e}, falling back to environment variables. "
                    "Set allow_env_fallback=False to make this an error."
                )
                self.config.backend = SecretBackend.ENVIRONMENT
            else:
                raise RuntimeError(f"Failed to initialize Vault: {e}") from e
    
    def get_secret(
        self,
        key: str,
        default: Optional[str] = None,
        required: bool = False,
    ) -> Optional[str]:
        """
        Get a secret value.
        الحصول على قيمة سرية.
        
        Args:
            key: Secret key name
            default: Default value if secret not found
            required: Raise exception if secret not found
            
        Returns:
            Secret value or default
            
        Raises:
            ValueError: If required=True and secret not found
        """
        import time
        
        # Check cache first
        if self.config.cache_enabled and key in self._cache:
            cache_age = time.time() - self._cache_timestamps.get(key, 0)
            if cache_age < self.config.cache_ttl_seconds:
                return self._cache[key]
        
        # Fetch from backend
        value = None
        if self.config.backend == SecretBackend.VAULT:
            value = self._get_from_vault(key)
        else:
            value = self._get_from_environment(key)
        
        # Use default if not found
        if value is None:
            value = default
        
        # Raise if required and not found
        if required and value is None:
            raise ValueError(f"Required secret '{key}' not found")
        
        # Cache the value
        if value is not None and self.config.cache_enabled:
            self._cache[key] = value
            self._cache_timestamps[key] = time.time()
        
        return value
    
    def _get_from_environment(self, key: str) -> Optional[str]:
        """Get secret from environment variable"""
        return os.getenv(key)
    
    def _get_from_vault(self, key: str) -> Optional[str]:
        """Get secret from HashiCorp Vault"""
        if not self._vault_client:
            return None
        
        try:
            # Construct vault path
            path = f"{self.config.vault_path_prefix}/{key}"
            
            # Read secret
            response = self._vault_client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.config.vault_mount_point,
            )
            
            # Extract value
            data = response.get("data", {}).get("data", {})
            return data.get("value")
            
        except Exception as e:
            logger.warning(f"Failed to read secret '{key}' from Vault: {e}")
            return None
    
    def get_secrets_batch(self, keys: List[str]) -> Dict[str, Optional[str]]:
        """
        Get multiple secrets at once.
        الحصول على أسرار متعددة دفعة واحدة.
        
        Args:
            keys: List of secret keys
            
        Returns:
            Dictionary of key-value pairs
        """
        return {key: self.get_secret(key) for key in keys}
    
    def set_secret(self, key: str, value: str) -> bool:
        """
        Set a secret value (Vault only).
        تعيين قيمة سرية (Vault فقط).
        
        Note: Only supported for Vault backend.
        Environment variables cannot be set at runtime.
        
        Args:
            key: Secret key name
            value: Secret value
            
        Returns:
            True if successful, False otherwise
        """
        if self.config.backend != SecretBackend.VAULT:
            logger.warning("set_secret only supported for Vault backend")
            return False
        
        if not self._vault_client:
            return False
        
        try:
            # Construct vault path
            path = f"{self.config.vault_path_prefix}/{key}"
            
            # Write secret
            self._vault_client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={"value": value},
                mount_point=self.config.vault_mount_point,
            )
            
            # Update cache
            if self.config.cache_enabled:
                import time
                self._cache[key] = value
                self._cache_timestamps[key] = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write secret '{key}' to Vault: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear the secret cache"""
        self._cache.clear()
        self._cache_timestamps.clear()


# Global secret manager instance
_global_secret_manager: Optional[SecretManager] = None


def get_secret_manager(config: Optional[SecretConfig] = None) -> SecretManager:
    """
    Get the global secret manager instance.
    الحصول على نسخة مدير الأسرار العامة.
    
    Args:
        config: Optional configuration (used on first call)
        
    Returns:
        SecretManager instance
    """
    global _global_secret_manager
    
    if _global_secret_manager is None:
        # Auto-detect backend from environment
        if config is None:
            backend_str = os.getenv("SECRET_BACKEND", "environment")
            try:
                backend = SecretBackend(backend_str.lower())
            except ValueError:
                logger.warning(f"Unknown secret backend '{backend_str}', using environment")
                backend = SecretBackend.ENVIRONMENT
            
            config = SecretConfig(
                backend=backend,
                vault_addr=os.getenv("VAULT_ADDR"),
                vault_token=os.getenv("VAULT_TOKEN"),
                vault_role_id=os.getenv("VAULT_ROLE_ID"),
                vault_secret_id=os.getenv("VAULT_SECRET_ID"),
                vault_namespace=os.getenv("VAULT_NAMESPACE"),
            )
        
        _global_secret_manager = SecretManager(config)
    
    return _global_secret_manager


def get_config(
    key: str,
    default: Optional[str] = None,
    required: bool = False,
    cast_type: type = str,
) -> Any:
    """
    Get a configuration value with type casting.
    الحصول على قيمة تكوين مع تحويل النوع.
    
    Args:
        key: Configuration key
        default: Default value
        required: Raise exception if not found
        cast_type: Type to cast to (str, int, bool, float, list)
        
    Returns:
        Configuration value
        
    Examples:
        >>> get_config("PORT", default="8000", cast_type=int)
        8000
        >>> get_config("DEBUG", default="false", cast_type=bool)
        False
        >>> get_config("ALLOWED_HOSTS", cast_type=list)
        ["localhost", "127.0.0.1"]
    """
    manager = get_secret_manager()
    value = manager.get_secret(key, default=default, required=required)
    
    if value is None:
        return None
    
    # Cast to requested type
    if cast_type == bool:
        return value.lower() in ("true", "1", "yes", "on")
    elif cast_type == int:
        return int(value)
    elif cast_type == float:
        return float(value)
    elif cast_type == list:
        # Parse comma-separated list
        return [item.strip() for item in value.split(",") if item.strip()]
    elif cast_type == dict:
        # Parse JSON
        return json.loads(value)
    else:
        return value


# Common configuration getters
def get_database_url() -> str:
    """Get database URL"""
    return get_config("DATABASE_URL", required=True)


def get_redis_url() -> str:
    """Get Redis URL"""
    return get_config("REDIS_URL", required=True)


def get_nats_url() -> str:
    """Get NATS URL"""
    return get_config("NATS_URL", default="nats://localhost:4222")


def get_jwt_secret() -> str:
    """Get JWT secret key"""
    return get_config("JWT_SECRET_KEY", required=True)


def get_cors_origins() -> List[str]:
    """Get CORS allowed origins"""
    return get_config(
        "CORS_ALLOWED_ORIGINS",
        default="http://localhost:3000",
        cast_type=list,
    )


def get_environment() -> str:
    """Get current environment"""
    return get_config("ENVIRONMENT", default="development")


def get_log_level() -> str:
    """Get log level"""
    return get_config("LOG_LEVEL", default="INFO")


def is_production() -> bool:
    """Check if running in production"""
    return get_environment().lower() == "production"


def is_development() -> bool:
    """Check if running in development"""
    return get_environment().lower() == "development"
