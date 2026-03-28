# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Configuration settings for LLM Orchestrator Service.

This service orchestrates all SAHOOL AI agents intelligently,
routing user requests to appropriate agents and combining results.

إعدادات التكوين لخدمة تنسيق نماذج اللغة الكبيرة.
تقوم هذه الخدمة بتنسيق جميع وكلاء الذكاء الاصطناعي في سهول بذكاء،
وتوجيه طلبات المستخدمين إلى الوكلاء المناسبين ودمج النتائج.
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
        default="llm-orchestrator-service",
        description="Service name | اسم الخدمة",
    )
    service_name_ar: str = Field(
        default="خدمة تنسيق نماذج اللغة الكبيرة",
        description="Service name in Arabic",
    )
    version: str = Field(default="16.0.0", description="Service version | إصدار الخدمة")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8164, description="Server port")
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development",
        description="Deployment environment | بيئة النشر",
    )
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # Database configuration
    database_url: str = Field(
        default="",
        description="PostgreSQL connection URL | رابط اتصال PostgreSQL",
    )
    db_pool_min_size: int = Field(default=2, description="Minimum DB pool size")
    db_pool_max_size: int = Field(default=10, description="Maximum DB pool size")

    # Redis configuration
    redis_url: str = Field(
        default="redis://redis:6379",
        description="Redis connection URL for caching | رابط اتصال Redis للتخزين المؤقت",
    )
    redis_cache_ttl: int = Field(
        default=300,
        description="Cache TTL in seconds | مدة التخزين المؤقت بالثواني",
    )

    # NATS configuration
    nats_url: str = Field(
        default="nats://localhost:4222",
        description="NATS server URL",
    )

    # LLM Provider Settings
    ollama_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL | رابط خادم Ollama",
    )
    llm_model_name: str = Field(
        default="codellama:7b",
        description="Default LLM model name | اسم نموذج اللغة الافتراضي",
    )
    llm_temperature: float = Field(
        default=0.1,
        description="LLM temperature for responses",
    )
    llm_timeout: int = Field(
        default=60,
        description="LLM request timeout in seconds",
    )
    intent_model_name: str = Field(
        default="codellama:7b",
        description="Model for intent classification | نموذج تصنيف النوايا",
    )

    # Agent Endpoints Configuration
    agent_timeout: int = Field(
        default=30,
        description="Agent call timeout in seconds | مهلة استدعاء الوكيل بالثواني",
    )
    agent_max_retries: int = Field(
        default=3,
        description="Maximum retries for agent calls | الحد الأقصى لإعادة المحاولة",
    )
    agent_parallel_limit: int = Field(
        default=5,
        description="Maximum parallel agent calls | الحد الأقصى للاستدعاءات المتوازية",
    )

    # Agent Service URLs (can be overridden via environment)
    crop_intelligence_url: str = Field(
        default="http://crop-intelligence-service:8095",
        description="Crop Intelligence Service URL",
    )
    advisory_url: str = Field(
        default="http://advisory-service:8093",
        description="Advisory Service URL",
    )
    irrigation_url: str = Field(
        default="http://irrigation-smart:8094",
        description="Irrigation Smart Service URL",
    )
    pest_detection_url: str = Field(
        default="http://pest-detection-service:8125",
        description="Pest Detection Service URL",
    )
    weather_url: str = Field(
        default="http://weather-service:8092",
        description="Weather Service URL",
    )
    yield_engine_url: str = Field(
        default="http://yield-engine:8098",
        description="Yield Engine Service URL",
    )
    field_intelligence_url: str = Field(
        default="http://field-intelligence:8120",
        description="Field Intelligence Service URL",
    )
    indicators_url: str = Field(
        default="http://indicators-service:8091",
        description="Indicators Service URL",
    )
    yolo_vision_url: str = Field(
        default="http://yolo26-vision-service:8150",
        description="YOLO Vision Service URL",
    )
    terrain_url: str = Field(
        default="http://terrain-core-service:8185",
        description="Terrain Core Service URL",
    )
    hydrology_url: str = Field(
        default="http://hydrology-service:8165",
        description="Hydrology Service URL",
    )
    leveling_url: str = Field(
        default="http://leveling-optimizer-service:8170",
        description="Leveling Optimizer Service URL",
    )

    # JWT Authentication
    jwt_secret_key: str = Field(
        default="",
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


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
