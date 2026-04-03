"""
Configuration settings for Leveling Optimizer Service.

إعدادات خدمة تحسين التسوية
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service configuration settings."""

    # Service info
    SERVICE_NAME: str = "leveling-optimizer-service"
    SERVICE_NAME_AR: str = "خدمة تحسين التسوية"
    VERSION: str = "16.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"  # nosec B104 - default for containerized deployment, overridden by env
    PORT: int = 8170

    # Database
    DATABASE_URL: str | None = None

    # NATS
    NATS_URL: str | None = None

    # Redis
    REDIS_URL: str | None = None

    # JWT - must be provided via environment variable, no hardcoded default
    # يجب توفير مفتاح JWT عبر متغير البيئة، بدون قيمة افتراضية مشفرة
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        env = os.getenv("ENVIRONMENT", "production")
        if env != "test" and (not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32):
            raise ValueError(
                "JWT_SECRET_KEY must be set via environment variable and be at least 32 characters. "
                "يجب تعيين JWT_SECRET_KEY عبر متغير البيئة وأن يكون 32 حرفاً على الأقل"
            )

    # Equipment costs in SAR (Saudi Riyal) per hour
    # تكاليف المعدات بالريال السعودي في الساعة
    BULLDOZER_COST_PER_HOUR: float = 350.0  # جرافة
    SCRAPER_COST_PER_HOUR: float = 400.0  # كاشطة
    GRADER_COST_PER_HOUR: float = 300.0  # ممهدة
    LASER_LEVELER_COST_PER_HOUR: float = 450.0  # مسوي ليزر
    EXCAVATOR_COST_PER_HOUR: float = 380.0  # حفارة
    DUMP_TRUCK_COST_PER_HOUR: float = 200.0  # شاحنة قلابة

    # Equipment productivity (cubic meters per hour)
    # إنتاجية المعدات (متر مكعب في الساعة)
    BULLDOZER_PRODUCTIVITY: float = 80.0
    SCRAPER_PRODUCTIVITY: float = 120.0
    GRADER_PRODUCTIVITY: float = 60.0
    LASER_LEVELER_PRODUCTIVITY: float = 40.0
    EXCAVATOR_PRODUCTIVITY: float = 100.0

    # Soil expansion/compaction factors
    # معاملات انتفاخ/دمك التربة
    SOIL_EXPANSION_FACTOR: float = 1.25  # معامل الانتفاخ
    SOIL_COMPACTION_FACTOR: float = 0.90  # معامل الدمك

    # Cost factors
    FUEL_COST_PER_LITER: float = 2.18  # تكلفة الوقود بالريال
    OPERATOR_COST_PER_HOUR: float = 50.0  # تكلفة المشغل بالريال
    SURVEYING_COST_PER_HECTARE: float = 500.0  # تكلفة المسح بالريال

    # Default haul distance (meters)
    DEFAULT_HAUL_DISTANCE: float = 100.0

    # Minimum grade for drainage (%)
    MIN_DRAINAGE_GRADE: float = 0.1

    # Maximum recommended grade for irrigation (%)
    MAX_IRRIGATION_GRADE: float = 0.5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
