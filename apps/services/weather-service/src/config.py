"""
SAHOOL Weather Service Configuration
إعدادات خدمة الطقس

Configuration for weather providers, API keys, and service settings
"""

import os
from dataclasses import dataclass, field
from enum import Enum


class WeatherProviderPriority(Enum):
    """
    Weather provider priority levels
    مستويات أولوية مزودي الطقس
    """

    PRIMARY = 1  # الأساسي
    SECONDARY = 2  # الثانوي
    FALLBACK = 3  # الاحتياطي


@dataclass
class ProviderConfig:
    """
    Weather provider configuration
    إعدادات مزود الطقس
    """

    name: str
    enabled: bool = True
    api_key: str | None = None
    priority: WeatherProviderPriority = WeatherProviderPriority.FALLBACK
    rate_limit_per_day: int = 1000
    timeout_seconds: int = 30
    max_retries: int = 3


@dataclass
class CacheConfig:
    """
    Cache configuration
    إعدادات التخزين المؤقت
    """

    enabled: bool = True
    current_weather_ttl_minutes: int = 10  # وقت التخزين المؤقت للطقس الحالي
    forecast_ttl_minutes: int = 60  # وقت التخزين المؤقت للتوقعات
    hourly_ttl_minutes: int = 30  # وقت التخزين المؤقت للتوقعات الساعية
    max_cache_size_mb: int = 100


@dataclass
class AlertThresholds:
    """
    Alert threshold configuration
    عتبات التنبيهات
    """

    # Temperature thresholds - عتبات الحرارة
    frost_critical_c: float = 0  # صقيع حرج
    frost_high_c: float = 2  # صقيع مرتفع
    frost_medium_c: float = 5  # صقيع متوسط

    heat_wave_critical_c: float = 45  # موجة حر حرجة
    heat_wave_high_c: float = 42  # موجة حر مرتفعة
    heat_wave_medium_c: float = 38  # موجة حر متوسطة
    heat_wave_min_days: int = 3  # الحد الأدنى من الأيام لموجة الحر

    # Precipitation thresholds - عتبات الأمطار
    heavy_rain_critical_mm: float = 50  # أمطار غزيرة حرجة
    heavy_rain_high_mm: float = 30  # أمطار غزيرة مرتفعة
    heavy_rain_medium_mm: float = 15  # أمطار غزيرة متوسطة

    drought_days_threshold: int = 14  # عتبة أيام الجفاف
    drought_precip_threshold_mm: float = 5  # عتبة الأمطار للجفاف

    # Wind thresholds - عتبات الرياح
    wind_critical_kmh: float = 60  # رياح حرجة
    wind_high_kmh: float = 45  # رياح مرتفعة
    wind_medium_kmh: float = 30  # رياح متوسطة

    # Disease risk - خطر الأمراض
    disease_humidity_threshold: float = 75  # عتبة الرطوبة للأمراض
    disease_temp_min_c: float = 18  # الحد الأدنى لحرارة الأمراض
    disease_temp_max_c: float = 32  # الحد الأقصى لحرارة الأمراض


@dataclass
class AgriculturalIndicesConfig:
    """
    Agricultural weather indices configuration
    إعدادات المؤشرات الزراعية
    """

    # Growing Degree Days (GDD) - أيام درجة النمو
    gdd_base_temp_c: float = 10  # درجة الحرارة الأساسية
    gdd_upper_limit_c: float = 30  # الحد الأعلى

    # Chill hours - ساعات البرودة
    chill_hours_threshold_c: float = 7.2  # عتبة ساعات البرودة

    # Evapotranspiration - التبخر والنتح
    eto_calculation_method: str = "penman_monteith"  # طريقة حساب التبخر
    eto_enabled: bool = True


@dataclass
class WeatherServiceConfig:
    """
    Main weather service configuration
    إعدادات خدمة الطقس الرئيسية
    """

    # Provider configurations - إعدادات المزودين
    providers: dict[str, ProviderConfig] = field(default_factory=dict)

    # Cache configuration - إعدادات التخزين المؤقت
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Alert thresholds - عتبات التنبيهات
    thresholds: AlertThresholds = field(default_factory=AlertThresholds)

    # Agricultural indices - المؤشرات الزراعية
    ag_indices: AgriculturalIndicesConfig = field(default_factory=AgriculturalIndicesConfig)

    # Service settings - إعدادات الخدمة
    enable_alerts: bool = True  # تفعيل التنبيهات
    enable_ag_indices: bool = True  # تفعيل المؤشرات الزراعية
    forecast_default_days: int = 7  # الأيام الافتراضية للتوقعات
    forecast_max_days: int = 16  # الحد الأقصى للأيام

    # Yemen-specific settings - إعدادات خاصة باليمن
    enable_yemen_met: bool = False  # تفعيل هيئة الأرصاد اليمنية
    default_timezone: str = "Asia/Aden"  # المنطقة الزمنية الافتراضية


def load_config_from_env() -> WeatherServiceConfig:
    """
    Load configuration from environment variables
    تحميل الإعدادات من متغيرات البيئة

    Returns:
        WeatherServiceConfig: Loaded configuration
    """
    config = WeatherServiceConfig()

    # Provider: Open-Meteo (Free - always enabled)
    # مزود Open-Meteo (مجاني - مفعل دائماً)
    config.providers["open_meteo"] = ProviderConfig(
        name="Open-Meteo",
        enabled=True,
        priority=WeatherProviderPriority.PRIMARY,
        api_key=None,  # No API key required
        rate_limit_per_day=10000,
    )

    # Provider: OpenWeatherMap
    # مزود OpenWeatherMap
    owm_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    config.providers["openweathermap"] = ProviderConfig(
        name="OpenWeatherMap",
        enabled=bool(owm_api_key),
        api_key=owm_api_key,
        priority=WeatherProviderPriority.SECONDARY,
        rate_limit_per_day=1000,
    )

    # Provider: WeatherAPI
    # مزود WeatherAPI
    weatherapi_key = os.getenv("WEATHERAPI_KEY")
    config.providers["weatherapi"] = ProviderConfig(
        name="WeatherAPI",
        enabled=bool(weatherapi_key),
        api_key=weatherapi_key,
        priority=WeatherProviderPriority.SECONDARY,
        rate_limit_per_day=1000,
    )

    # Provider: Yemen Met Service (Mock for future)
    # مزود هيئة الأرصاد اليمنية (نموذج للمستقبل)
    yemen_met_enabled = os.getenv("YEMEN_MET_ENABLED", "false").lower() == "true"
    config.providers["yemen_met"] = ProviderConfig(
        name="Yemen Met Service",
        enabled=yemen_met_enabled,
        api_key=os.getenv("YEMEN_MET_API_KEY"),
        priority=WeatherProviderPriority.FALLBACK,
        rate_limit_per_day=500,
    )

    # Cache settings from environment
    # إعدادات التخزين المؤقت من البيئة
    config.cache.enabled = os.getenv("WEATHER_CACHE_ENABLED", "true").lower() == "true"
    config.cache.current_weather_ttl_minutes = int(os.getenv("WEATHER_CACHE_CURRENT_TTL", "10"))
    config.cache.forecast_ttl_minutes = int(os.getenv("WEATHER_CACHE_FORECAST_TTL", "60"))

    # Alert settings from environment
    # إعدادات التنبيهات من البيئة
    config.enable_alerts = os.getenv("WEATHER_ALERTS_ENABLED", "true").lower() == "true"
    config.enable_ag_indices = os.getenv("WEATHER_AG_INDICES_ENABLED", "true").lower() == "true"

    # Alert thresholds customization
    # تخصيص عتبات التنبيهات
    config.thresholds.frost_critical_c = float(os.getenv("FROST_CRITICAL_TEMP", "0"))
    config.thresholds.heat_wave_critical_c = float(os.getenv("HEAT_WAVE_CRITICAL_TEMP", "45"))
    config.thresholds.heavy_rain_critical_mm = float(os.getenv("HEAVY_RAIN_CRITICAL_MM", "50"))

    # Agricultural indices settings
    # إعدادات المؤشرات الزراعية
    config.ag_indices.gdd_base_temp_c = float(os.getenv("GDD_BASE_TEMP", "10"))
    config.ag_indices.chill_hours_threshold_c = float(os.getenv("CHILL_HOURS_THRESHOLD", "7.2"))

    return config


# Global configuration instance
# مثيل الإعدادات العامة
_global_config: WeatherServiceConfig | None = None


def get_config() -> WeatherServiceConfig:
    """
    Get global configuration instance
    الحصول على مثيل الإعدادات العامة

    Returns:
        WeatherServiceConfig: Configuration instance
    """
    global _global_config
    if _global_config is None:
        _global_config = load_config_from_env()
    return _global_config


def reset_config():
    """
    Reset global configuration (useful for testing)
    إعادة تعيين الإعدادات العامة (مفيد للاختبار)
    """
    global _global_config
    _global_config = None


# Export configuration classes
# تصدير فئات الإعدادات
__all__ = [
    "WeatherServiceConfig",
    "ProviderConfig",
    "CacheConfig",
    "AlertThresholds",
    "AgriculturalIndicesConfig",
    "WeatherProviderPriority",
    "get_config",
    "reset_config",
    "load_config_from_env",
]
