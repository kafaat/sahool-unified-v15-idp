"""
Configuration for Hydrology Service
إعدادات خدمة الهيدرولوجيا

Environment-based configuration with defaults.
"""

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Info
    service_name: str = "hydrology-service"
    service_name_ar: str = "خدمة الهيدرولوجيا"
    version: str = "16.0.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")  # nosec B104 - default for containerized deployment, overridden by env
    port: int = Field(default=8165, alias="PORT")

    # Database
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    db_pool_min_size: int = Field(default=2, alias="DB_POOL_MIN_SIZE")
    db_pool_max_size: int = Field(default=10, alias="DB_POOL_MAX_SIZE")

    # NATS Messaging
    nats_url: str | None = Field(default=None, alias="NATS_URL")
    nats_cluster_id: str = Field(default="sahool-cluster", alias="NATS_CLUSTER_ID")

    # External Services
    terrain_service_url: str = Field(default="http://terrain-core-service:8164", alias="TERRAIN_SERVICE_URL")
    weather_service_url: str = Field(default="http://weather-service:8108", alias="WEATHER_SERVICE_URL")

    # Hydrology Analysis Settings
    default_dem_resolution: float = Field(
        default=30.0, alias="DEFAULT_DEM_RESOLUTION", description="Default DEM resolution in meters"
    )
    flow_accumulation_threshold: int = Field(
        default=100,
        alias="FLOW_ACCUMULATION_THRESHOLD",
        description="Minimum flow accumulation for stream detection",
    )
    depression_fill_max_depth: float = Field(
        default=2.0,
        alias="DEPRESSION_FILL_MAX_DEPTH",
        description="Maximum depth (m) for depression filling",
    )
    wetness_index_high_threshold: float = Field(
        default=12.0,
        alias="WETNESS_INDEX_HIGH_THRESHOLD",
        description="TWI threshold for high wetness areas",
    )
    basin_area_min_hectares: float = Field(
        default=0.5, alias="BASIN_AREA_MIN_HECTARES", description="Minimum basin area in hectares"
    )

    # Caching
    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Expose settings for easy import
settings = get_settings()
