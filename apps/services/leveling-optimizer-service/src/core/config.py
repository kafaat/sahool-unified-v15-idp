"""
Configuration settings for Leveling Optimizer Service.

إعدادات خدمة تحسين التسوية
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Service configuration settings."""

    # Service info
    SERVICE_NAME: str = "leveling-optimizer-service"
    SERVICE_NAME_AR: str = "خدمة تحسين التسوية"
    VERSION: str = "16.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8170

    # Database
    DATABASE_URL: str | None = None

    # NATS
    NATS_URL: str | None = None

    # Redis
    REDIS_URL: str | None = None

    # JWT
    JWT_SECRET_KEY: str = "test-secret-key-for-unit-tests-only-32chars"
    JWT_ALGORITHM: str = "HS256"

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
