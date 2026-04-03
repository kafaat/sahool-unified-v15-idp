"""
Configuration settings for Terrain Core Service
إعدادات خدمة تحليل التضاريس

Supports multiple DEM sources:
- Copernicus DEM (30m/90m global coverage)
- SRTM (30m/90m resolution)
- ALOS PALSAR (12.5m resolution)
- Local uploaded DEMs
"""

import os
from enum import Enum, StrEnum
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DEMSource(StrEnum):
    """Supported DEM data sources | مصادر بيانات الارتفاعات"""

    COPERNICUS = "copernicus"  # Copernicus DEM GLO-30/GLO-90
    SRTM = "srtm"  # NASA SRTM 30m/90m
    ALOS_PALSAR = "alos_palsar"  # JAXA ALOS PALSAR 12.5m
    LOCAL = "local"  # User-uploaded DEM files


class ResamplingMethod(StrEnum):
    """Resampling methods for DEM processing | طرق إعادة التشكيل"""

    BILINEAR = "bilinear"
    CUBIC = "cubic"
    CUBIC_SPLINE = "cubic_spline"
    LANCZOS = "lanczos"
    NEAREST = "nearest"


class Settings(BaseSettings):
    """
    Application settings for Terrain Core Service
    إعدادات تطبيق خدمة تحليل التضاريس
    """

    # Service Configuration
    SERVICE_NAME: str = "terrain-core-service"
    SERVICE_NAME_AR: str = "خدمة تحليل التضاريس"
    VERSION: str = "16.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode | وضع التصحيح")
    PORT: int = Field(default=8185, description="Service port | منفذ الخدمة")
    ENVIRONMENT: str = Field(default="development", description="Environment | البيئة")

    # Database Configuration
    DATABASE_URL: str | None = Field(
        default=None,
        description="PostgreSQL connection URL | رابط اتصال قاعدة البيانات",
    )
    DB_POOL_MIN_SIZE: int = Field(default=2, description="Min pool size")
    DB_POOL_MAX_SIZE: int = Field(default=10, description="Max pool size")

    # NATS Configuration
    NATS_URL: str | None = Field(default=None, description="NATS server URL | رابط خادم NATS")
    NATS_SUBJECT_PREFIX: str = Field(default="sahool.terrain", description="NATS subject prefix")

    # Redis Configuration
    REDIS_URL: str | None = Field(default=None, description="Redis URL | رابط Redis")
    CACHE_TTL_SECONDS: int = Field(default=3600, description="Cache TTL in seconds | مدة التخزين المؤقت")

    # DEM Data Sources
    DEFAULT_DEM_SOURCE: DEMSource = Field(
        default=DEMSource.COPERNICUS,
        description="Default DEM source | مصدر الارتفاعات الافتراضي",
    )
    COPERNICUS_API_URL: str = Field(
        default="https://prism-dem-open.copernicus.eu/pd-desk-open-access/prismDownload",
        description="Copernicus DEM API URL",
    )
    SRTM_API_URL: str = Field(
        default="https://e4ftl01.cr.usgs.gov/MEASURES/SRTMGL1.003",
        description="NASA SRTM API URL",
    )
    ALOS_API_URL: str = Field(
        default="https://www.eorc.jaxa.jp/ALOS/aw3d30/data",
        description="ALOS World 3D API URL",
    )

    # Processing Configuration
    DEFAULT_RESOLUTION_M: float = Field(
        default=30.0, description="Default output resolution in meters | الدقة الافتراضية"
    )
    MAX_PROCESSING_AREA_KM2: float = Field(
        default=1000.0, description="Maximum processing area in km² | أقصى مساحة معالجة"
    )
    DEFAULT_CRS: str = Field(default="EPSG:32637", description="Default CRS (UTM 37N for Middle East)")
    RESAMPLING_METHOD: ResamplingMethod = Field(
        default=ResamplingMethod.BILINEAR,
        description="Default resampling method | طريقة إعادة التشكيل الافتراضية",
    )

    # Terrain Analysis Configuration
    CONTOUR_INTERVAL_M: float = Field(default=5.0, description="Contour interval in meters | فترة خطوط الكنتور")
    MIN_SLOPE_DEGREES: float = Field(default=0.0, description="Minimum slope threshold | أدنى حد للميل")
    MAX_SLOPE_DEGREES: float = Field(default=90.0, description="Maximum slope threshold | أقصى حد للميل")
    FLOW_THRESHOLD: int = Field(default=100, description="Flow accumulation threshold | عتبة تراكم التدفق")

    # Storage Configuration
    TEMP_DIR: str = Field(default="/tmp/terrain", description="Temporary directory | المجلد المؤقت")  # nosec B108 - configurable default, overridden by env var
    MAX_UPLOAD_SIZE_MB: int = Field(default=500, description="Maximum upload size in MB | أقصى حجم للرفع")
    DEM_CACHE_DIR: str = Field(
        default="/tmp/terrain/dem_cache",  # nosec B108 - configurable default, overridden by env var
        description="DEM cache directory | مجلد تخزين الارتفاعات",
    )

    # S3 Configuration (for DEM storage)
    S3_BUCKET: str | None = Field(default=None, description="S3 bucket for DEM files")
    AWS_ACCESS_KEY_ID: str | None = Field(default=None)
    AWS_SECRET_ACCESS_KEY: str | None = Field(default=None)
    AWS_REGION: str = Field(default="me-south-1", description="AWS region")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level | مستوى التسجيل")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance | الحصول على نسخة الإعدادات المخزنة"""
    return Settings()


# Global settings instance
settings = get_settings()
