# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Configuration settings for Edge Orchestrator Service.

This service manages edge devices (Jetson Orin Nano) for agricultural
AI inference at the edge, supporting offline-first operations.

إعدادات التكوين لخدمة تنسيق الحافة.
تدير هذه الخدمة أجهزة الحافة (Jetson Orin Nano) لاستدلال الذكاء الاصطناعي
الزراعي على الحافة، مع دعم العمليات دون اتصال.
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
        default="edge-orchestrator-service",
        description="Service name | اسم الخدمة",
    )
    service_name_ar: str = Field(
        default="خدمة تنسيق الحافة",
        description="Service name in Arabic",
    )
    version: str = Field(default="16.0.0", description="Service version | إصدار الخدمة")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server host")  # nosec B104 - default for containerized deployment, overridden by env
    port: int = Field(default=8180, description="Server port")
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
        description="Redis connection URL",
    )

    # NATS configuration
    nats_url: str = Field(
        default="nats://localhost:4222",
        description="NATS server URL",
    )
    nats_cluster_id: str = Field(
        default="sahool-cluster",
        description="NATS cluster ID",
    )

    # JWT Authentication
    jwt_secret_key: str = Field(
        default="development-secret-key-change-in-production-32chars",
        description="JWT secret key | مفتاح JWT السري",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiry_hours: int = Field(default=24, description="JWT token expiry in hours")

    # Edge Device Configuration
    edge_heartbeat_interval: int = Field(
        default=30,
        description="Heartbeat interval in seconds | فترة نبض القلب بالثواني",
    )
    edge_timeout_threshold: int = Field(
        default=120,
        description="Device timeout threshold in seconds | عتبة مهلة الجهاز بالثواني",
    )
    max_devices_per_farm: int = Field(
        default=50,
        description="Maximum edge devices per farm | الحد الأقصى لأجهزة الحافة لكل مزرعة",
    )

    # Model Configuration
    default_model: str = Field(
        default="yolo26-s",
        description="Default AI model for edge deployment | نموذج الذكاء الاصطناعي الافتراضي",
    )
    model_storage_path: str = Field(
        default="/models",
        description="Path to model storage",
    )
    supported_models: list[str] = Field(
        default=[
            "yolo26-s",
            "yolo26-n",
            "yolo11-s",
            "crop-disease-v3",
            "pest-detection-v2",
            "weed-classifier-v1",
        ],
        description="List of supported models | قائمة النماذج المدعومة",
    )

    # Jetson Orin Nano Specific Settings
    jetson_ssh_port: int = Field(default=22, description="SSH port for Jetson devices")
    jetson_api_port: int = Field(
        default=8000,
        description="API port on Jetson devices",
    )
    jetson_max_power_mode: int = Field(
        default=15,
        description="Maximum power mode in watts (15W for Orin Nano)",
    )

    # Sync Configuration
    sync_batch_size: int = Field(
        default=100,
        description="Batch size for data sync | حجم الدفعة للمزامنة",
    )
    sync_retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for sync",
    )
    sync_retry_delay: float = Field(
        default=1.0,
        description="Delay between retries in seconds",
    )

    # WebSocket Configuration
    ws_ping_interval: int = Field(
        default=30,
        description="WebSocket ping interval in seconds",
    )
    ws_ping_timeout: int = Field(
        default=10,
        description="WebSocket ping timeout in seconds",
    )
    ws_max_connections: int = Field(
        default=1000,
        description="Maximum WebSocket connections",
    )

    # Storage Configuration
    upload_dir: str = Field(
        default="/data/uploads",
        description="Directory for file uploads",
    )
    max_upload_size_mb: int = Field(
        default=500,
        description="Maximum upload size in MB",
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
