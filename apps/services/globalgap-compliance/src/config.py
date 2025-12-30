"""
GlobalGAP Compliance Service Configuration
إعدادات خدمة الامتثال لمعايير GlobalGAP

This module manages all environment variables and service configuration.
تدير هذه الوحدة جميع متغيرات البيئة وإعدادات الخدمة.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    إعدادات التطبيق المحملة من متغيرات البيئة
    """

    # Service Configuration | إعدادات الخدمة
    service_name: str = "globalgap-compliance"
    service_version: str = "1.0.0"
    service_port: int = 8120
    log_level: str = "INFO"

    # Database Configuration | إعدادات قاعدة البيانات
    database_url: str = "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_compliance"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # NATS Messaging | نظام الرسائل NATS
    nats_url: str = "nats://nats:4222"
    nats_subject_prefix: str = "sahool.compliance"
    nats_stream_name: str = "COMPLIANCE"

    # GlobalGAP API Configuration | إعدادات واجهة برمجة GlobalGAP
    globalgap_api_url: str = "https://api.globalgap.org/v1"
    globalgap_api_key: Optional[str] = None
    globalgap_api_timeout: int = 30  # seconds | ثواني

    # IFA Standards Version | إصدار معايير IFA
    ifa_version: str = "6.0"  # IFA v6 standards
    ggn_check_interval: int = 86400  # 24 hours in seconds | التحقق من GGN كل 24 ساعة

    # Compliance Settings | إعدادات الامتثال
    audit_retention_days: int = 1825  # 5 years | 5 سنوات
    certificate_renewal_warning_days: int = 90  # Warn 90 days before expiry | تحذير قبل 90 يوم من انتهاء الصلاحية

    # Checklist Configuration | إعدادات قوائم المراجعة
    enable_auto_checklist_generation: bool = True
    checklist_language: str = "ar"  # ar, en | عربي، إنجليزي

    # External Services | الخدمات الخارجية
    field_service_url: str = "http://field-service:8080"
    notification_service_url: str = "http://notification-service:8086"

    # Cache Settings | إعدادات التخزين المؤقت
    enable_cache: bool = True
    cache_ttl: int = 3600  # seconds | ثواني

    # Security | الأمان
    api_key_header: str = "X-API-Key"
    enable_cors: bool = True
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance | مثيل الإعدادات العام
settings = Settings()
