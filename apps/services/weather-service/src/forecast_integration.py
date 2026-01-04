"""
SAHOOL Weather Forecast Integration Service
خدمة تكامل توقعات الطقس

Comprehensive weather forecast integration with multiple providers,
agricultural alerts, and weather indices for Yemen.

Features:
- Multi-provider forecast aggregation (تجميع التوقعات من مزودين متعددين)
- Agricultural weather alerts (تنبيهات الطقس الزراعية)
- Weather indices for crop management (مؤشرات الطقس لإدارة المحاصيل)
- Yemen-specific meteorological data (بيانات الأرصاد الجوية الخاصة باليمن)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .config import AlertThresholds, get_config
from .providers import (
    DailyForecast,
    HourlyForecast,
    OpenMeteoProvider,
    OpenWeatherMapProvider,
    WeatherAPIProvider,
    WeatherData,
    WeatherProvider,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Data Models - نماذج البيانات
# ═══════════════════════════════════════════════════════════════════════════════


class AlertSeverity(Enum):
    """
    Weather alert severity levels
    مستويات خطورة التنبيهات
    """

    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # مرتفع
    CRITICAL = "critical"  # حرج


class AlertCategory(Enum):
    """
    Weather alert categories
    فئات التنبيهات الجوية
    """

    TEMPERATURE = "temperature"  # الحرارة
    PRECIPITATION = "precipitation"  # الأمطار
    WIND = "wind"  # الرياح
    DROUGHT = "drought"  # الجفاف
    DISEASE = "disease"  # الأمراض


@dataclass
class AgriculturalAlert:
    """
    Agricultural weather alert
    تنبيه الطقس الزراعي
    """

    alert_id: str
    alert_type: str
    category: AlertCategory
    severity: AlertSeverity
    title_en: str
    title_ar: str
    description_en: str
    description_ar: str
    start_date: str
    end_date: str | None = None
    affected_days: int = 1
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)
    impact_score: float = 0.0  # 0-10 scale
    confidence: float = 1.0  # 0-1 scale

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "category": self.category.value,
            "severity": self.severity.value,
            "title_en": self.title_en,
            "title_ar": self.title_ar,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "affected_days": self.affected_days,
            "recommendations_en": self.recommendations_en,
            "recommendations_ar": self.recommendations_ar,
            "impact_score": self.impact_score,
            "confidence": self.confidence,
        }


@dataclass
class AgriculturalIndices:
    """
    Agricultural weather indices
    المؤشرات الزراعية
    """

    date: str
    gdd: float = 0.0  # Growing Degree Days - أيام درجة النمو
    chill_hours: float = 0.0  # Chill Hours - ساعات البرودة
    eto: float = 0.0  # Evapotranspiration - التبخر والنتح
    heat_stress_hours: float = 0.0  # ساعات الإجهاد الحراري
    moisture_deficit_mm: float = 0.0  # عجز الرطوبة

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "date": self.date,
            "gdd": round(self.gdd, 2),
            "chill_hours": round(self.chill_hours, 1),
            "eto": round(self.eto, 2),
            "heat_stress_hours": round(self.heat_stress_hours, 1),
            "moisture_deficit_mm": round(self.moisture_deficit_mm, 2),
        }


@dataclass
class ForecastSummary:
    """
    Forecast summary for a location
    ملخص التوقعات لموقع
    """

    location: dict[str, float]
    forecast_days: list[DailyForecast]
    hourly_forecast: list[HourlyForecast]
    alerts: list[AgriculturalAlert]
    indices: list[AgriculturalIndices]
    provider: str
    providers_used: list[str]
    generated_at: str


# ═══════════════════════════════════════════════════════════════════════════════
# Provider Adapters - محولات المزودين
# ═══════════════════════════════════════════════════════════════════════════════


class YemenMetAdapter(WeatherProvider):
    """
    Yemen Meteorological Service Adapter (Mock for future implementation)
    محول هيئة الأرصاد الجوية اليمنية (نموذج للتطبيق المستقبلي)

    This is a placeholder for integration with Yemen's national weather service.
    هذا عنصر نائب للتكامل مع خدمة الطقس الوطنية في اليمن.
    """

    def __init__(self, api_key: str | None = None):
        super().__init__("Yemen Met Service", api_key)
        self.is_mock = True  # Flag to indicate this is a mock implementation

    @property
    def is_configured(self) -> bool:
        # For now, always return False as this is a mock
        return False

    async def get_current(self, lat: float, lon: float) -> WeatherData:
        """
        Get current weather (mock implementation)
        الحصول على الطقس الحالي (تطبيق نموذجي)
        """
        raise NotImplementedError(
            "Yemen Met Service integration not yet implemented - "
            "تكامل هيئة الأرصاد اليمنية لم يتم تطبيقه بعد"
        )

    async def get_daily_forecast(
        self, lat: float, lon: float, days: int = 7
    ) -> list[DailyForecast]:
        """
        Get daily forecast (mock implementation)
        الحصول على التوقعات اليومية (تطبيق نموذجي)
        """
        raise NotImplementedError(
            "Yemen Met Service integration not yet implemented - "
            "تكامل هيئة الأرصاد اليمنية لم يتم تطبيقه بعد"
        )

    async def get_hourly_forecast(
        self, lat: float, lon: float, hours: int = 24
    ) -> list[HourlyForecast]:
        """
        Get hourly forecast (mock implementation)
        الحصول على التوقعات الساعية (تطبيق نموذجي)
        """
        raise NotImplementedError(
            "Yemen Met Service integration not yet implemented - "
            "تكامل هيئة الأرصاد اليمنية لم يتم تطبيقه بعد"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Weather Forecast Service - خدمة توقعات الطقس
# ═══════════════════════════════════════════════════════════════════════════════


class WeatherForecastService:
    """
    Weather forecast integration service
    خدمة تكامل توقعات الطقس

    Aggregates forecasts from multiple providers and generates agricultural alerts.
    يجمع التوقعات من مزودين متعددين ويولد تنبيهات زراعية.
    """

    def __init__(self):
        self.config = get_config()
        self.providers: dict[str, WeatherProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """
        Initialize weather providers
        تهيئة مزودي الطقس
        """
        # Open-Meteo (always available)
        if self.config.providers.get("open_meteo", {}).enabled:
            self.providers["open_meteo"] = OpenMeteoProvider()

        # OpenWeatherMap
        owm_config = self.config.providers.get("openweathermap")
        if owm_config and owm_config.enabled and owm_config.api_key:
            self.providers["openweathermap"] = OpenWeatherMapProvider(
                owm_config.api_key
            )

        # WeatherAPI
        wa_config = self.config.providers.get("weatherapi")
        if wa_config and wa_config.enabled and wa_config.api_key:
            self.providers["weatherapi"] = WeatherAPIProvider(wa_config.api_key)

        # Yemen Met (mock)
        yemen_config = self.config.providers.get("yemen_met")
        if yemen_config and yemen_config.enabled:
            self.providers["yemen_met"] = YemenMetAdapter(yemen_config.api_key)

    async def fetch_forecast(
        self, lat: float, lon: float, days: int = 7
    ) -> tuple[list[DailyForecast] | None, list[HourlyForecast] | None, str]:
        """
        Fetch weather forecast from providers with automatic fallback
        جلب توقعات الطقس من المزودين مع التبديل التلقائي

        Args:
            lat: Latitude - خط العرض
            lon: Longitude - خط الطول
            days: Number of forecast days - عدد أيام التوقعات

        Returns:
            Tuple of (daily_forecast, hourly_forecast, provider_name)
        """
        days = min(days, self.config.forecast_max_days)

        # Try providers in priority order
        # جرب المزودين حسب ترتيب الأولوية
        sorted_providers = sorted(
            self.providers.items(),
            key=lambda x: self.config.providers.get(x[0], {}).priority.value
            if hasattr(self.config.providers.get(x[0], {}), "priority")
            else 999,
        )

        for provider_name, provider in sorted_providers:
            if not provider.is_configured:
                continue

            try:
                daily = await provider.get_daily_forecast(lat, lon, days)
                hourly = await provider.get_hourly_forecast(lat, lon, 72)  # 3 days
                return daily, hourly, provider_name
            except Exception as e:
                print(f"⚠️ Provider {provider_name} failed: {e}")
                continue

        return None, None, "none"

    def parse_openweather_response(self, response: dict[str, Any]) -> list[DailyForecast]:
        """
        Parse OpenWeatherMap API response
        تحليل استجابة OpenWeatherMap API

        Args:
            response: Raw API response

        Returns:
            List of DailyForecast objects
        """
        forecasts = []

        # Group by day
        daily_data: dict[str, list[Any]] = {}
        for item in response.get("list", []):
            day = item["dt_txt"].split(" ")[0]
            daily_data.setdefault(day, []).append(item)

        for day, items in daily_data.items():
            temps = [i["main"]["temp"] for i in items]
            precips = [i.get("rain", {}).get("3h", 0) for i in items]
            condition = items[0]["weather"][0]["main"]

            forecasts.append(
                DailyForecast(
                    date=day,
                    temp_max_c=max(temps),
                    temp_min_c=min(temps),
                    precipitation_mm=sum(precips),
                    precipitation_probability_pct=int((items[0].get("pop", 0) or 0) * 100),
                    wind_speed_max_kmh=max(
                        i["wind"]["speed"] * 3.6 for i in items
                    ),
                    uv_index_max=0,
                    condition=condition,
                    condition_ar=self._translate_condition(condition),
                    icon=items[0]["weather"][0]["icon"],
                )
            )

        return forecasts

    def parse_weatherapi_response(self, response: dict[str, Any]) -> list[DailyForecast]:
        """
        Parse WeatherAPI.com response
        تحليل استجابة WeatherAPI.com

        Args:
            response: Raw API response

        Returns:
            List of DailyForecast objects
        """
        forecasts = []

        for day in response.get("forecast", {}).get("forecastday", []):
            day_data = day.get("day", {})
            forecasts.append(
                DailyForecast(
                    date=day.get("date"),
                    temp_max_c=day_data.get("maxtemp_c", 0),
                    temp_min_c=day_data.get("mintemp_c", 0),
                    precipitation_mm=day_data.get("totalprecip_mm", 0),
                    precipitation_probability_pct=day_data.get("daily_chance_of_rain", 0),
                    wind_speed_max_kmh=day_data.get("maxwind_kph", 0),
                    uv_index_max=day_data.get("uv", 0),
                    condition=day_data.get("condition", {}).get("text", "Unknown"),
                    condition_ar=day_data.get("condition", {}).get("text", "غير معروف"),
                    icon=day_data.get("condition", {}).get("icon", ""),
                    sunrise=day.get("astro", {}).get("sunrise"),
                    sunset=day.get("astro", {}).get("sunset"),
                )
            )

        return forecasts

    def aggregate_forecasts(self, sources: list[tuple[str, list[DailyForecast]]]) -> list[DailyForecast]:
        """
        Aggregate forecasts from multiple sources
        تجميع التوقعات من مصادر متعددة

        Takes the average of forecasts from different providers for better accuracy.
        يأخذ متوسط التوقعات من مزودين مختلفين لدقة أفضل.

        Args:
            sources: List of (provider_name, forecast_list) tuples

        Returns:
            Aggregated forecast list
        """
        if not sources:
            return []

        if len(sources) == 1:
            return sources[0][1]

        # Group forecasts by date
        # تجميع التوقعات حسب التاريخ
        forecast_by_date: dict[str, list[DailyForecast]] = {}

        for provider_name, forecasts in sources:
            for forecast in forecasts:
                forecast_by_date.setdefault(forecast.date, []).append(forecast)

        # Aggregate each day
        # تجميع كل يوم
        aggregated = []
        for date_str, day_forecasts in sorted(forecast_by_date.items()):
            if not day_forecasts:
                continue

            # Average numeric values
            # متوسط القيم الرقمية
            aggregated.append(
                DailyForecast(
                    date=date_str,
                    temp_max_c=sum(f.temp_max_c for f in day_forecasts) / len(day_forecasts),
                    temp_min_c=sum(f.temp_min_c for f in day_forecasts) / len(day_forecasts),
                    precipitation_mm=sum(f.precipitation_mm for f in day_forecasts) / len(day_forecasts),
                    precipitation_probability_pct=sum(
                        f.precipitation_probability_pct for f in day_forecasts
                    ) / len(day_forecasts),
                    wind_speed_max_kmh=sum(f.wind_speed_max_kmh for f in day_forecasts) / len(day_forecasts),
                    uv_index_max=sum(f.uv_index_max for f in day_forecasts) / len(day_forecasts),
                    condition=day_forecasts[0].condition,  # Use first provider's condition
                    condition_ar=day_forecasts[0].condition_ar,
                    icon=day_forecasts[0].icon,
                    sunrise=day_forecasts[0].sunrise,
                    sunset=day_forecasts[0].sunset,
                )
            )

        return aggregated

    @staticmethod
    def _translate_condition(condition: str) -> str:
        """
        Translate weather condition to Arabic
        ترجمة حالة الطقس إلى العربية
        """
        translations = {
            "Clear": "صافي",
            "Clouds": "غائم",
            "Rain": "مطر",
            "Drizzle": "رذاذ",
            "Thunderstorm": "عاصفة رعدية",
            "Snow": "ثلج",
            "Mist": "ضباب خفيف",
            "Fog": "ضباب",
            "Haze": "ضباب دخاني",
        }
        return translations.get(condition, condition)

    async def close(self):
        """
        Close all provider connections
        إغلاق جميع اتصالات المزودين
        """
        for provider in self.providers.values():
            await provider.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Alert Generation - توليد التنبيهات
# ═══════════════════════════════════════════════════════════════════════════════


def detect_frost_risk(
    forecast: list[DailyForecast], thresholds: AlertThresholds | None = None
) -> list[AgriculturalAlert]:
    """
    Detect frost risk in forecast
    كشف خطر الصقيع في التوقعات

    Args:
        forecast: Daily forecast list
        thresholds: Alert thresholds configuration

    Returns:
        List of frost risk alerts
    """
    if thresholds is None:
        thresholds = get_config().thresholds

    alerts = []

    for day_forecast in forecast:
        temp = day_forecast.temp_min_c
        severity = None
        impact = 0.0

        if temp <= thresholds.frost_critical_c:
            severity = AlertSeverity.CRITICAL
            impact = 10.0
        elif temp <= thresholds.frost_high_c:
            severity = AlertSeverity.HIGH
            impact = 8.0
        elif temp <= thresholds.frost_medium_c:
            severity = AlertSeverity.MEDIUM
            impact = 5.0

        if severity:
            alerts.append(
                AgriculturalAlert(
                    alert_id=f"frost_{day_forecast.date}",
                    alert_type="frost_risk",
                    category=AlertCategory.TEMPERATURE,
                    severity=severity,
                    title_en=f"Frost Risk - {temp}°C expected",
                    title_ar=f"خطر الصقيع - متوقع {temp}°س",
                    description_en=f"Minimum temperature of {temp}°C expected on {day_forecast.date}. "
                    f"Risk of frost damage to crops.",
                    description_ar=f"درجة الحرارة الدنيا المتوقعة {temp}°س في {day_forecast.date}. "
                    f"خطر تلف المحاصيل بسبب الصقيع.",
                    start_date=day_forecast.date,
                    recommendations_en=[
                        "Cover sensitive crops with protective materials",
                        "Irrigate before frost to protect root systems",
                        "Avoid harvesting until frost melts completely",
                        "Monitor temperature closely overnight",
                    ],
                    recommendations_ar=[
                        "تغطية المحاصيل الحساسة بمواد واقية",
                        "الري قبل الصقيع لحماية الجذور",
                        "تجنب الحصاد حتى ذوبان الصقيع بالكامل",
                        "مراقبة الحرارة عن كثب طوال الليل",
                    ],
                    impact_score=impact,
                    confidence=0.85,
                )
            )

    return alerts


def detect_heat_wave(
    forecast: list[DailyForecast], thresholds: AlertThresholds | None = None
) -> list[AgriculturalAlert]:
    """
    Detect heat wave conditions
    كشف موجات الحر

    A heat wave is defined as 3+ consecutive days above threshold temperature.
    موجة الحر تُعرف بأنها 3 أيام متتالية أو أكثر فوق درجة الحرارة العتبة.

    Args:
        forecast: Daily forecast list
        thresholds: Alert thresholds configuration

    Returns:
        List of heat wave alerts
    """
    if thresholds is None:
        thresholds = get_config().thresholds

    alerts = []
    consecutive_hot_days = 0
    hot_days_start = None
    max_temp_in_wave = 0.0

    for i, day_forecast in enumerate(forecast):
        temp = day_forecast.temp_max_c

        if temp >= thresholds.heat_wave_medium_c:
            if consecutive_hot_days == 0:
                hot_days_start = day_forecast.date
                max_temp_in_wave = temp
            else:
                max_temp_in_wave = max(max_temp_in_wave, temp)

            consecutive_hot_days += 1

            # Check if we have a heat wave (3+ days)
            if consecutive_hot_days >= thresholds.heat_wave_min_days:
                severity = None
                impact = 0.0

                if max_temp_in_wave >= thresholds.heat_wave_critical_c:
                    severity = AlertSeverity.CRITICAL
                    impact = 10.0
                elif max_temp_in_wave >= thresholds.heat_wave_high_c:
                    severity = AlertSeverity.HIGH
                    impact = 8.0
                elif max_temp_in_wave >= thresholds.heat_wave_medium_c:
                    severity = AlertSeverity.MEDIUM
                    impact = 6.0

                if severity and consecutive_hot_days == thresholds.heat_wave_min_days:
                    alerts.append(
                        AgriculturalAlert(
                            alert_id=f"heatwave_{hot_days_start}",
                            alert_type="heat_wave",
                            category=AlertCategory.TEMPERATURE,
                            severity=severity,
                            title_en=f"Heat Wave Alert - {consecutive_hot_days} days",
                            title_ar=f"تنبيه موجة حر - {consecutive_hot_days} أيام",
                            description_en=f"Heat wave expected from {hot_days_start} with "
                            f"temperatures reaching {max_temp_in_wave}°C for {consecutive_hot_days}+ days.",
                            description_ar=f"موجة حر متوقعة من {hot_days_start} مع "
                            f"درجات حرارة تصل إلى {max_temp_in_wave}°س لمدة {consecutive_hot_days}+ أيام.",
                            start_date=hot_days_start,
                            end_date=day_forecast.date,
                            affected_days=consecutive_hot_days,
                            recommendations_en=[
                                "Increase irrigation frequency significantly",
                                "Irrigate early morning or evening only",
                                "Use shade nets for sensitive crops",
                                "Avoid field work during peak heat (11 AM - 4 PM)",
                                "Monitor soil moisture daily",
                            ],
                            recommendations_ar=[
                                "زيادة وتيرة الري بشكل كبير",
                                "الري في الصباح الباكر أو المساء فقط",
                                "استخدام شبكات التظليل للمحاصيل الحساسة",
                                "تجنب العمل الميداني وقت الذروة (11 ص - 4 م)",
                                "مراقبة رطوبة التربة يومياً",
                            ],
                            impact_score=impact,
                            confidence=0.9,
                        )
                    )
        else:
            # Reset counter if streak breaks
            consecutive_hot_days = 0
            hot_days_start = None
            max_temp_in_wave = 0.0

    return alerts


def detect_heavy_rain(
    forecast: list[DailyForecast], thresholds: AlertThresholds | None = None
) -> list[AgriculturalAlert]:
    """
    Detect heavy rain and flooding risk
    كشف الأمطار الغزيرة وخطر الفيضانات

    Args:
        forecast: Daily forecast list
        thresholds: Alert thresholds configuration

    Returns:
        List of heavy rain alerts
    """
    if thresholds is None:
        thresholds = get_config().thresholds

    alerts = []

    for day_forecast in forecast:
        precip = day_forecast.precipitation_mm
        severity = None
        impact = 0.0

        if precip >= thresholds.heavy_rain_critical_mm:
            severity = AlertSeverity.CRITICAL
            impact = 10.0
        elif precip >= thresholds.heavy_rain_high_mm:
            severity = AlertSeverity.HIGH
            impact = 7.0
        elif precip >= thresholds.heavy_rain_medium_mm:
            severity = AlertSeverity.MEDIUM
            impact = 4.0

        if severity:
            alerts.append(
                AgriculturalAlert(
                    alert_id=f"heavy_rain_{day_forecast.date}",
                    alert_type="heavy_rain",
                    category=AlertCategory.PRECIPITATION,
                    severity=severity,
                    title_en=f"Heavy Rain Alert - {precip}mm expected",
                    title_ar=f"تنبيه أمطار غزيرة - متوقع {precip} ملم",
                    description_en=f"Heavy rainfall of {precip}mm expected on {day_forecast.date}. "
                    f"Risk of flooding and waterlogging.",
                    description_ar=f"أمطار غزيرة {precip} ملم متوقعة في {day_forecast.date}. "
                    f"خطر الفيضانات والتشبع المائي.",
                    start_date=day_forecast.date,
                    recommendations_en=[
                        "Ensure proper field drainage systems are clear",
                        "Postpone spraying and fertilization activities",
                        "Harvest mature crops if possible before rain",
                        "Secure equipment and materials",
                        "Monitor for signs of waterlogging",
                    ],
                    recommendations_ar=[
                        "التأكد من تنظيف أنظمة الصرف في الحقول",
                        "تأجيل أنشطة الرش والتسميد",
                        "حصاد المحاصيل الناضجة إن أمكن قبل المطر",
                        "تأمين المعدات والمواد",
                        "مراقبة علامات التشبع المائي",
                    ],
                    impact_score=impact,
                    confidence=day_forecast.precipitation_probability_pct / 100.0,
                )
            )

    return alerts


def detect_drought_conditions(
    forecast: list[DailyForecast],
    history: list[DailyForecast] | None = None,
    thresholds: AlertThresholds | None = None,
) -> list[AgriculturalAlert]:
    """
    Detect drought conditions
    كشف ظروف الجفاف

    Drought is detected when there's minimal precipitation over an extended period.
    يتم اكتشاف الجفاف عندما تكون الأمطار ضئيلة لفترة ممتدة.

    Args:
        forecast: Daily forecast list
        history: Historical weather data (optional)
        thresholds: Alert thresholds configuration

    Returns:
        List of drought alerts
    """
    if thresholds is None:
        thresholds = get_config().thresholds

    alerts = []

    # Combine history and forecast
    all_days = (history or []) + forecast

    if len(all_days) < thresholds.drought_days_threshold:
        return alerts

    # Check last N days for drought conditions
    recent_days = all_days[-thresholds.drought_days_threshold :]
    total_precip = sum(day.precipitation_mm for day in recent_days)

    if total_precip < thresholds.drought_precip_threshold_mm:
        # Calculate severity based on precipitation deficit
        deficit = thresholds.drought_precip_threshold_mm - total_precip
        severity = None
        impact = 0.0

        if deficit >= 40:
            severity = AlertSeverity.CRITICAL
            impact = 9.0
        elif deficit >= 25:
            severity = AlertSeverity.HIGH
            impact = 7.0
        elif deficit >= 10:
            severity = AlertSeverity.MEDIUM
            impact = 5.0

        if severity:
            alerts.append(
                AgriculturalAlert(
                    alert_id=f"drought_{recent_days[-1].date}",
                    alert_type="drought",
                    category=AlertCategory.DROUGHT,
                    severity=severity,
                    title_en=f"Drought Conditions - {thresholds.drought_days_threshold} days with minimal rain",
                    title_ar=f"ظروف جفاف - {thresholds.drought_days_threshold} يوم مع أمطار ضئيلة",
                    description_en=f"Only {total_precip}mm of rain in the last {thresholds.drought_days_threshold} days. "
                    f"Drought conditions affecting crop water availability.",
                    description_ar=f"فقط {total_precip} ملم من الأمطار في آخر {thresholds.drought_days_threshold} يوم. "
                    f"ظروف الجفاف تؤثر على توفر الماء للمحاصيل.",
                    start_date=recent_days[0].date,
                    end_date=recent_days[-1].date,
                    affected_days=thresholds.drought_days_threshold,
                    recommendations_en=[
                        "Implement water conservation measures immediately",
                        "Increase irrigation to compensate for rainfall deficit",
                        "Use mulch to reduce soil moisture evaporation",
                        "Consider drought-resistant crop varieties",
                        "Monitor soil moisture levels closely",
                    ],
                    recommendations_ar=[
                        "تطبيق تدابير الحفاظ على المياه فوراً",
                        "زيادة الري للتعويض عن نقص الأمطار",
                        "استخدام الغطاء النباتي لتقليل تبخر رطوبة التربة",
                        "النظر في أصناف محاصيل مقاومة للجفاف",
                        "مراقبة مستويات رطوبة التربة عن كثب",
                    ],
                    impact_score=impact,
                    confidence=0.95,
                )
            )

    return alerts


# ═══════════════════════════════════════════════════════════════════════════════
# Agricultural Weather Indices - المؤشرات الزراعية
# ═══════════════════════════════════════════════════════════════════════════════


def calculate_gdd(
    tmin: float,
    tmax: float,
    base_temp: float | None = None,
    upper_limit: float | None = None,
) -> float:
    """
    Calculate Growing Degree Days (GDD)
    حساب أيام درجة النمو

    GDD = ((Tmax + Tmin) / 2) - Tbase
    Where temperatures are clamped to base and upper limits.

    Args:
        tmin: Minimum temperature (°C)
        tmax: Maximum temperature (°C)
        base_temp: Base temperature (default: 10°C)
        upper_limit: Upper temperature limit (default: 30°C)

    Returns:
        Growing degree days value
    """
    config = get_config().ag_indices

    if base_temp is None:
        base_temp = config.gdd_base_temp_c

    if upper_limit is None:
        upper_limit = config.gdd_upper_limit_c

    # Clamp temperatures
    tmin_adj = max(tmin, base_temp)
    tmax_adj = min(max(tmax, base_temp), upper_limit)

    # Calculate GDD
    gdd = ((tmax_adj + tmin_adj) / 2.0) - base_temp

    return max(0, gdd)  # GDD cannot be negative


def calculate_chill_hours(
    hourly_temps: list[float], threshold: float | None = None
) -> float:
    """
    Calculate chill hours
    حساب ساعات البرودة

    Chill hours are the number of hours with temperature between 0°C and 7.2°C.
    ساعات البرودة هي عدد الساعات بدرجة حرارة بين 0°س و 7.2°س.

    Args:
        hourly_temps: List of hourly temperatures (°C)
        threshold: Temperature threshold (default: 7.2°C)

    Returns:
        Number of chill hours
    """
    if threshold is None:
        threshold = get_config().ag_indices.chill_hours_threshold_c

    chill_hours = sum(1 for temp in hourly_temps if 0 <= temp <= threshold)

    return float(chill_hours)


def calculate_evapotranspiration(
    forecast: DailyForecast, method: str = "penman_monteith"
) -> float:
    """
    Calculate reference evapotranspiration (ET0)
    حساب التبخر والنتح المرجعي

    Uses simplified Penman-Monteith or Hargreaves method.
    يستخدم طريقة Penman-Monteith أو Hargreaves المبسطة.

    Args:
        forecast: Daily forecast data
        method: Calculation method ("penman_monteith" or "hargreaves")

    Returns:
        ET0 in mm/day
    """
    if method == "hargreaves":
        # Simplified Hargreaves method
        # طريقة Hargreaves المبسطة
        tavg = (forecast.temp_max_c + forecast.temp_min_c) / 2.0
        trange = abs(forecast.temp_max_c - forecast.temp_min_c)

        # Simplified calculation (requires solar radiation, using approximation)
        # حساب مبسط (يتطلب الإشعاع الشمسي، باستخدام التقريب)
        et0 = 0.0023 * (tavg + 17.8) * (trange**0.5) * 2.45  # Simplified
        return max(0, et0)

    else:
        # Simplified FAO Penman-Monteith
        # طريقة FAO Penman-Monteith المبسطة
        tavg = (forecast.temp_max_c + forecast.temp_min_c) / 2.0

        # Very simplified version (full calculation requires more data)
        # نسخة مبسطة جداً (الحساب الكامل يتطلب المزيد من البيانات)
        wind_factor = 1 + (forecast.wind_speed_max_kmh / 100.0)
        temp_factor = 0.408 * (tavg + 17.0) / 30.0

        et0 = temp_factor * wind_factor * 3.5  # Approximation

        return max(0, et0)


def calculate_agricultural_indices(
    daily_forecast: DailyForecast,
    hourly_forecast: list[HourlyForecast] | None = None,
) -> AgriculturalIndices:
    """
    Calculate agricultural weather indices for a day
    حساب المؤشرات الزراعية ليوم

    Args:
        daily_forecast: Daily forecast data
        hourly_forecast: Hourly forecast data (optional, for better accuracy)

    Returns:
        AgriculturalIndices object
    """
    indices = AgriculturalIndices(date=daily_forecast.date)

    # Growing Degree Days
    # أيام درجة النمو
    indices.gdd = calculate_gdd(
        daily_forecast.temp_min_c, daily_forecast.temp_max_c
    )

    # Chill hours (if hourly data available)
    # ساعات البرودة (إذا توفرت البيانات الساعية)
    if hourly_forecast:
        temps = [h.temperature_c for h in hourly_forecast]
        indices.chill_hours = calculate_chill_hours(temps)
    else:
        # Estimate from daily min/max
        # تقدير من الحد الأدنى/الأقصى اليومي
        if daily_forecast.temp_min_c <= 7.2:
            # Rough estimate: assume 1/3 of day is in chill range
            indices.chill_hours = 8.0

    # Evapotranspiration
    # التبخر والنتح
    indices.eto = calculate_evapotranspiration(daily_forecast)

    # Heat stress hours (temperature > 35°C)
    # ساعات الإجهاد الحراري
    if daily_forecast.temp_max_c >= 35:
        if hourly_forecast:
            indices.heat_stress_hours = sum(
                1 for h in hourly_forecast if h.temperature_c >= 35
            )
        else:
            # Rough estimate based on max temp
            # تقدير تقريبي بناءً على الحرارة القصوى
            if daily_forecast.temp_max_c >= 40:
                indices.heat_stress_hours = 6.0
            elif daily_forecast.temp_max_c >= 35:
                indices.heat_stress_hours = 3.0

    # Moisture deficit (ET0 - Precipitation)
    # عجز الرطوبة
    indices.moisture_deficit_mm = max(
        0, indices.eto - daily_forecast.precipitation_mm
    )

    return indices


# ═══════════════════════════════════════════════════════════════════════════════
# Export public API - تصدير الواجهة العامة
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Service classes
    "WeatherForecastService",
    "YemenMetAdapter",
    # Data models
    "AgriculturalAlert",
    "AgriculturalIndices",
    "ForecastSummary",
    "AlertSeverity",
    "AlertCategory",
    # Alert detection
    "detect_frost_risk",
    "detect_heat_wave",
    "detect_heavy_rain",
    "detect_drought_conditions",
    # Agricultural indices
    "calculate_gdd",
    "calculate_chill_hours",
    "calculate_evapotranspiration",
    "calculate_agricultural_indices",
]
