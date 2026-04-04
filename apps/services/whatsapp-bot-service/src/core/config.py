# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Configuration settings for WhatsApp Bot Service.
إعدادات التكوين لخدمة روبوت واتساب.

This service handles WhatsApp messaging for SAHOOL farmers using
the WhatsApp Business API (Cloud API).

Port: 8240
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service identification
    service_name: str = Field(
        default="whatsapp-bot-service",
        description="Service name | اسم الخدمة",
    )
    service_name_ar: str = Field(
        default="خدمة روبوت واتساب",
        description="Service name in Arabic",
    )
    version: str = Field(default="16.0.0", description="Service version | إصدار الخدمة")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")  # nosec B104 - default for containerized deployment, overridden by env
    port: int = Field(default=8240, description="Server port")
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        description="Deployment environment | بيئة النشر",
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # WhatsApp Business API Configuration
    whatsapp_token: str = Field(
        default="",
        description="WhatsApp Business API access token | رمز الوصول لـ API واتساب للأعمال",
    )
    whatsapp_phone_id: str = Field(
        default="",
        description="WhatsApp Business phone number ID | معرف رقم الهاتف التجاري",
    )
    whatsapp_verify_token: str = Field(
        default="",
        description="Webhook verification token (MUST be set via env) | رمز التحقق من webhook (يجب تعيينه عبر متغير البيئة)",
    )
    whatsapp_app_secret: str = Field(
        default="",
        description="WhatsApp App Secret for X-Hub-Signature-256 HMAC verification (MUST be set via env) | سر التطبيق للتحقق من توقيع HMAC",
    )
    whatsapp_api_version: str = Field(
        default="v17.0",
        description="WhatsApp Cloud API version | إصدار API واتساب السحابي",
    )
    whatsapp_business_account_id: str = Field(
        default="",
        description="WhatsApp Business Account ID | معرف حساب الأعمال",
    )

    # LLM Orchestrator Service Configuration
    llm_orchestrator_url: str = Field(
        default="http://llm-orchestrator-service:8220",
        description="LLM Orchestrator Service URL | رابط خدمة تنسيق نماذج اللغة",
    )
    llm_timeout: int = Field(
        default=60,
        description="LLM request timeout in seconds | مهلة طلب LLM بالثواني",
    )

    # Vision Service Configuration (for image analysis)
    vision_service_url: str = Field(
        default="http://yolo26-vision-service:8150",
        description="Vision Service URL for crop disease detection | رابط خدمة الرؤية لكشف أمراض المحاصيل",
    )

    # Database configuration
    database_url: str = Field(
        default="",
        description="PostgreSQL connection URL | رابط اتصال PostgreSQL",
    )
    db_pool_min_size: int = Field(default=2, description="Minimum DB pool size")
    db_pool_max_size: int = Field(default=10, description="Maximum DB pool size")

    # Redis configuration (for session management)
    redis_url: str = Field(
        default="redis://redis:6379",
        description="Redis connection URL for session management | رابط اتصال Redis لإدارة الجلسات",
    )
    session_ttl: int = Field(
        default=3600,
        description="Session TTL in seconds (1 hour) | مدة الجلسة بالثواني",
    )
    context_messages_limit: int = Field(
        default=10,
        description="Number of recent messages to keep in context | عدد الرسائل الأخيرة للاحتفاظ بها في السياق",
    )

    # NATS configuration
    nats_url: str = Field(
        default="nats://localhost:4222",
        description="NATS server URL",
    )

    # JWT Authentication
    jwt_secret_key: str = Field(
        default="development-secret-key-change-in-production-32chars",
        description="JWT secret key | مفتاح JWT السري",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=60,
        description="Rate limit requests per minute | الحد الأقصى للطلبات في الدقيقة",
    )
    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window in seconds | نافذة الحد من المعدل بالثواني",
    )

    # Default language for responses
    default_language: str = Field(
        default="ar",
        description="Default response language (ar/en) | لغة الاستجابة الافتراضية",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def whatsapp_api_base_url(self) -> str:
        """Get WhatsApp API base URL."""
        return f"https://graph.facebook.com/{self.whatsapp_api_version}"

    @property
    def whatsapp_configured(self) -> bool:
        """Check if WhatsApp is properly configured."""
        return bool(self.whatsapp_token and self.whatsapp_phone_id)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
