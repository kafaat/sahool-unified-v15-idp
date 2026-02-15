"""
Configuration management for AI Chat Assistant service.
إدارة التكوين لخدمة مساعد الشات الذكي.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Service
    PORT: int = 8260
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SERVICE_NAME: str = "ai-chat-assistant"
    
    # NATS
    NATS_URL: str = "nats://localhost:4222"
    NATS_RECONNECT_TIME_WAIT: int = 2
    NATS_MAX_RECONNECT_ATTEMPTS: int = 60
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DECODE_RESPONSES: bool = True
    
    # LLM Orchestrator
    LLM_ORCHESTRATOR_URL: str = "http://localhost:8164"
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
