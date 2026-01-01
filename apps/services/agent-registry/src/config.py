"""
Agent Registry Service Configuration
تكوين خدمة سجل الوكلاء
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Service configuration / تكوين الخدمة"""

    # Service
    service_name: str = "agent-registry"
    service_port: int = 8080
    log_level: str = "INFO"
    environment: str = "production"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_prefix: str = "sahool:registry:"

    # Registry
    health_check_interval_seconds: int = 60
    health_check_timeout_seconds: int = 5
    enable_auto_discovery: bool = False
    agent_ttl_seconds: int = 3600

    # Security
    require_api_key: bool = True
    api_key: Optional[str] = None

    # CORS
    cors_origins: str = (
        "https://sahool.app,https://admin.sahool.app,https://api.sahool.app"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
