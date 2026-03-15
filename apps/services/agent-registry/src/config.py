"""
Agent Registry Service Configuration
تكوين خدمة سجل الوكلاء
"""

import logging
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Service configuration / تكوين الخدمة"""

    # Service
    service_name: str = "agent-registry"
    service_port: int = 8160
    log_level: str = "INFO"
    environment: str = "production"

    # Redis - supports both REDIS_URL (preferred) and individual REDIS_HOST/PORT/PASSWORD vars.
    # REDIS_URL takes precedence when set. Format: redis://:password@host:port/db
    redis_url: str = ""
    redis_host: str = ""
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_prefix: str = "sahool:registry:"

    # FIX: Use Redis for persistence in all environments (not just production).
    # Set to false to force in-memory storage (useful for testing only).
    use_redis: bool = True

    # Registry
    health_check_interval_seconds: int = 60
    health_check_timeout_seconds: int = 5
    enable_auto_discovery: bool = False
    agent_ttl_seconds: int = 3600

    # Security
    require_api_key: bool = True
    api_key: str | None = None

    # CORS
    cors_origins: str = "https://sahool.app,https://admin.sahool.app,https://api.sahool.app"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    def get_redis_url(self) -> str | None:
        """
        Build Redis URL from REDIS_URL or individual components.
        Returns None if Redis is not configured.
        """
        # Prefer REDIS_URL if explicitly set
        if self.redis_url:
            return self.redis_url

        # Fall back to individual components
        if self.redis_host:
            if self.redis_password:
                return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
            return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

        return None

    def should_use_redis(self) -> bool:
        """Determine whether Redis storage should be used."""
        return self.use_redis and self.get_redis_url() is not None


settings = Settings()

# Parse REDIS_URL into host/port/password if individual vars are not set
# This ensures backward compatibility with code that reads redis_host directly
if settings.redis_url and not settings.redis_host:
    try:
        parsed = urlparse(settings.redis_url)
        if parsed.hostname:
            settings.redis_host = parsed.hostname
        if parsed.port:
            settings.redis_port = parsed.port
        if parsed.password:
            settings.redis_password = parsed.password
        if parsed.path and len(parsed.path) > 1:
            settings.redis_db = int(parsed.path.lstrip("/"))
    except Exception as e:
        logger.warning("Failed to parse REDIS_URL: %s", e)

# Warn about missing external service configuration
if not settings.should_use_redis():
    logger.warning(
        "Redis not configured or disabled. Agent registry will use in-memory storage "
        "(data lost on restart). Set REDIS_URL to enable persistent storage."
    )
