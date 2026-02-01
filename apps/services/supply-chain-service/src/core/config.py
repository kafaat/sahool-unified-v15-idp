"""Configuration settings for Supply Chain Service."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Supply Chain Service configuration settings."""

    # Service settings
    SERVICE_NAME: str = "supply-chain-service"
    SERVICE_NAME_AR: str = "خدمة سلسلة التوريد"
    VERSION: str = "16.0.0"
    PORT: int = 8230
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")

    # Database settings
    DATABASE_URL: str | None = Field(default=None)
    DB_MIN_CONNECTIONS: int = Field(default=2)
    DB_MAX_CONNECTIONS: int = Field(default=10)

    # NATS settings
    NATS_URL: str | None = Field(default=None)

    # Redis settings
    REDIS_URL: str | None = Field(default=None)
    REDIS_PASSWORD: str | None = Field(default=None)

    # Payment gateway settings
    PAYMENT_GATEWAY_URL: str = Field(default="https://payment.sahool.local/api/v1")
    PAYMENT_GATEWAY_API_KEY: str | None = Field(default=None)
    PAYMENT_GATEWAY_TIMEOUT: int = Field(default=30)
    PAYMENT_ENABLED: bool = Field(default=True)

    # Delivery service integration
    DELIVERY_SERVICE_URL: str = Field(default="https://delivery.sahool.local/api/v1")
    DELIVERY_SERVICE_API_KEY: str | None = Field(default=None)
    DELIVERY_SERVICE_TIMEOUT: int = Field(default=30)
    DELIVERY_TRACKING_ENABLED: bool = Field(default=True)

    # Notification settings
    NOTIFICATION_SERVICE_URL: str = Field(default="http://notification-service:8110")
    SMS_ENABLED: bool = Field(default=True)
    PUSH_ENABLED: bool = Field(default=True)
    EMAIL_ENABLED: bool = Field(default=True)

    # Supplier settings
    SUPPLIER_SEARCH_RADIUS_KM: float = Field(default=50.0)
    MAX_SUPPLIERS_PER_QUERY: int = Field(default=10)
    QUOTE_VALIDITY_HOURS: int = Field(default=24)

    # Order settings
    ORDER_TIMEOUT_HOURS: int = Field(default=48)
    MAX_ORDER_ITEMS: int = Field(default=50)
    AUTO_PURCHASE_ENABLED: bool = Field(default=True)

    # JWT settings
    JWT_SECRET_KEY: str = Field(default="")
    JWT_ALGORITHM: str = Field(default="HS256")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
