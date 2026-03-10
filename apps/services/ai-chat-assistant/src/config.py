"""
Configuration management for AI Chat Assistant service.
إدارة التكوين لخدمة مساعد الشات الذكي.
"""

import logging

from pydantic_settings import BaseSettings
from typing import Optional

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings."""

    # Service
    PORT: int = 8260
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SERVICE_NAME: str = "ai-chat-assistant"

    # NATS
    NATS_URL: str = ""
    NATS_RECONNECT_TIME_WAIT: int = 2
    NATS_MAX_RECONNECT_ATTEMPTS: int = 60

    # Redis
    REDIS_URL: str = ""
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    REDIS_DECODE_RESPONSES: bool = True

    # LLM Orchestrator
    LLM_ORCHESTRATOR_URL: str = ""
    LLM_ORCHESTRATOR_TIMEOUT: int = 30

    # Caching
    CACHE_TTL_SECONDS: int = 604800  # 7 days
    CACHE_SIMILARITY_THRESHOLD: float = 0.9
    CACHE_ENABLED: bool = True

    # AI Behavior
    MIN_CONFIDENCE_THRESHOLD: float = 0.6
    HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    AUTO_SEND_CONFIDENCE_THRESHOLD: float = 0.85

    # Rate Limiting
    RATE_LIMIT_PER_USER_HOUR: int = 10
    RATE_LIMIT_ENABLED: bool = True

    # Query Constraints
    MAX_QUERY_LENGTH: int = 1000
    MIN_QUERY_LENGTH: int = 3

    # Monitoring
    METRICS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 8261

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Warn about missing external service URLs
if not settings.NATS_URL:
    logger.warning("NATS_URL not set, NATS features disabled")
if not settings.REDIS_URL:
    logger.warning("REDIS_URL not set, Redis features disabled")
if not settings.LLM_ORCHESTRATOR_URL:
    logger.warning("LLM_ORCHESTRATOR_URL not set, LLM orchestrator features disabled")
