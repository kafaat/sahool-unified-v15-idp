"""
Weather Risk Assessment - SAHOOL Weather Core
Agricultural weather risk evaluation for Yemen
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class RiskSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    HEAT_STRESS = "heat_stress"
    FROST = "frost"
    DROUGHT = "drought"
    HEAVY_RAIN = "heavy_rain"
    STRONG_WIND = "strong_wind"
    HIGH_UV = "high_uv"
    DISEASE_RISK = "disease_risk"


@dataclass
class WeatherAlert:
    """Weather alert"""
    alert_type: str
    severity: str
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    window_hours: int
    recommendations_ar: list[str]
    recommendations_en: list[str]

    def to_dict(self) -> dict:
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "description_ar": self.description_ar,
            "description_en": self.description_en,
            "window_hours": self.window_hours,
            "recommendations_ar": self.recommendations_ar,
            "recommendations_en": self.recommendations_en,
        }


def heat_stress_risk(temp_c: float) -> tuple[str, str]:
    """
    Evaluate heat stress risk

    Returns:
        Tuple of (alert_type, severity)
    """
    if temp_c >= 45:
        return (AlertType.HEAT_STRESS.value, RiskSeverity.CRITICAL.value)
    elif temp_c >= 42:
        return (AlertType.HEAT_STRESS.value, RiskSeverity.HIGH.value)
    elif temp_c >= 38:
        return (AlertType.HEAT_STRESS.value, RiskSeverity.MEDIUM.value)
    elif temp_c >= 35:
        return (AlertType.HEAT_STRESS.value, RiskSeverity.LOW.value)
    return (AlertType.HEAT_STRESS.value, "none")


def frost_risk(temp_c: float) -> tuple[str, str]:
    """Evaluate frost risk"""
    if temp_c <= 0:
        return (AlertType.FROST.value, RiskSeverity.CRITICAL.value)
    elif temp_c <= 2:
        return (AlertType.FROST.value, RiskSeverity.HIGH.value)
    elif temp_c <= 5:
        return (AlertType.FROST.value, RiskSeverity.MEDIUM.value)
    return (AlertType.FROST.value, "none")


def heavy_rain_risk(precipitation_mm: float, hours: int = 24) -> tuple[str, str]:
    """Evaluate heavy rain/flood risk"""
    intensity = precipitation_mm / hours if hours > 0 else precipitation_mm

    if precipitation_mm >= 50 or intensity >= 10:
        return (AlertType.HEAVY_RAIN.value, RiskSeverity.CRITICAL.value)
    elif precipitation_mm >= 30 or intensity >= 5:
        return (AlertType.HEAVY_RAIN.value, RiskSeverity.HIGH.value)
    elif precipitation_mm >= 15:
        return (AlertType.HEAVY_RAIN.value, RiskSeverity.MEDIUM.value)
    return (AlertType.HEAVY_RAIN.value, "none")


def wind_risk(wind_speed_kmh: float) -> tuple[str, str]:
    """Evaluate strong wind risk"""
    if wind_speed_kmh >= 60:
        return (AlertType.STRONG_WIND.value, RiskSeverity.CRITICAL.value)
    elif wind_speed_kmh >= 45:
        return (AlertType.STRONG_WIND.value, RiskSeverity.HIGH.value)
    elif wind_speed_kmh >= 30:
        return (AlertType.STRONG_WIND.value, RiskSeverity.MEDIUM.value)
    return (AlertType.STRONG_WIND.value, "none")


def disease_risk(temp_c: float, humidity_pct: float) -> tuple[str, str]:
    """
    Evaluate disease risk based on temperature and humidity

    Fungal diseases thrive in warm, humid conditions
    """
    if temp_c >= 20 and temp_c <= 30 and humidity_pct >= 85:
        return (AlertType.DISEASE_RISK.value, RiskSeverity.HIGH.value)
    elif temp_c >= 18 and temp_c <= 32 and humidity_pct >= 75:
        return (AlertType.DISEASE_RISK.value, RiskSeverity.MEDIUM.value)
    elif humidity_pct >= 80:
        return (AlertType.DISEASE_RISK.value, RiskSeverity.LOW.value)
    return (AlertType.DISEASE_RISK.value, "none")


def assess_weather(
    temp_c: float,
    humidity_pct: float = None,
    wind_speed_kmh: float = None,
    precipitation_mm: float = None,
    uv_index: float = None,
) -> list[WeatherAlert]:
    """
    Comprehensive weather assessment

    Args:
        temp_c: Temperature in Celsius
        humidity_pct: Relative humidity percentage
        wind_speed_kmh: Wind speed in km/h
        precipitation_mm: Precipitation in mm
        uv_index: UV index

    Returns:
        List of weather alerts
    """
    alerts = []

    # Heat stress
    alert_type, severity = heat_stress_risk(temp_c)
    if severity != "none":
        alerts.append(
            WeatherAlert(
                alert_type=alert_type,
                severity=severity,
                title_ar="تحذير موجة حر",
                title_en="Heat Stress Warning",
                description_ar=f"درجة الحرارة {temp_c}°C - خطر إجهاد حراري على المحاصيل",
                description_en=f"Temperature {temp_c}°C - Risk of heat stress on crops",
                window_hours=24,
                recommendations_ar=[
                    "زيادة الري في الصباح الباكر أو المساء",
                    "استخدام شبكات التظليل إن أمكن",
                    "تجنب العمل الميداني وقت الذروة",
                ],
                recommendations_en=[
                    "Increase irrigation in early morning or evening",
                    "Use shade nets if possible",
                    "Avoid field work during peak hours",
                ],
            )
        )

    # Frost
    alert_type, severity = frost_risk(temp_c)
    if severity != "none":
        alerts.append(
            WeatherAlert(
                alert_type=alert_type,
                severity=severity,
                title_ar="تحذير صقيع",
                title_en="Frost Warning",
                description_ar=f"درجة الحرارة {temp_c}°C - خطر صقيع على المحاصيل",
                description_en=f"Temperature {temp_c}°C - Risk of frost damage",
                window_hours=12,
                recommendations_ar=[
                    "تغطية المحاصيل الحساسة",
                    "الري قبل الصقيع لحماية الجذور",
                    "تجنب الحصاد حتى ذوبان الصقيع",
                ],
                recommendations_en=[
                    "Cover sensitive crops",
                    "Irrigate before frost to protect roots",
                    "Avoid harvesting until frost melts",
                ],
            )
        )

    # Heavy rain
    if precipitation_mm:
        alert_type, severity = heavy_rain_risk(precipitation_mm)
        if severity != "none":
            alerts.append(
                WeatherAlert(
                    alert_type=alert_type,
                    severity=severity,
                    title_ar="تحذير أمطار غزيرة",
                    title_en="Heavy Rain Warning",
                    description_ar=f"أمطار متوقعة {precipitation_mm} مم - خطر فيضانات",
                    description_en=f"Expected rainfall {precipitation_mm}mm - Flood risk",
                    window_hours=24,
                    recommendations_ar=[
                        "تحسين الصرف في الحقول",
                        "تأجيل الرش والتسميد",
                        "حصاد المحاصيل الجاهزة إن أمكن",
                    ],
                    recommendations_en=[
                        "Improve field drainage",
                        "Postpone spraying and fertilization",
                        "Harvest ready crops if possible",
                    ],
                )
            )

    # Strong wind
    if wind_speed_kmh:
        alert_type, severity = wind_risk(wind_speed_kmh)
        if severity != "none":
            alerts.append(
                WeatherAlert(
                    alert_type=alert_type,
                    severity=severity,
                    title_ar="تحذير رياح قوية",
                    title_en="Strong Wind Warning",
                    description_ar=f"سرعة الرياح {wind_speed_kmh} كم/س",
                    description_en=f"Wind speed {wind_speed_kmh} km/h",
                    window_hours=12,
                    recommendations_ar=[
                        "تأمين الأغطية والمعدات",
                        "تأجيل الرش",
                        "دعم النباتات الطويلة",
                    ],
                    recommendations_en=[
                        "Secure covers and equipment",
                        "Postpone spraying",
                        "Support tall plants",
                    ],
                )
            )

    # Disease risk
    if humidity_pct:
        alert_type, severity = disease_risk(temp_c, humidity_pct)
        if severity != "none":
            alerts.append(
                WeatherAlert(
                    alert_type=alert_type,
                    severity=severity,
                    title_ar="تحذير خطر أمراض",
                    title_en="Disease Risk Warning",
                    description_ar=f"رطوبة {humidity_pct}% + حرارة {temp_c}°C - ظروف مناسبة للأمراض الفطرية",
                    description_en=f"Humidity {humidity_pct}% + Temp {temp_c}°C - Favorable conditions for fungal diseases",
                    window_hours=48,
                    recommendations_ar=[
                        "فحص النباتات للأعراض المبكرة",
                        "تحسين التهوية في البيوت المحمية",
                        "تطبيق رش وقائي إن لزم",
                    ],
                    recommendations_en=[
                        "Inspect plants for early symptoms",
                        "Improve ventilation in greenhouses",
                        "Apply preventive spray if needed",
                    ],
                )
            )

    return alerts


def get_irrigation_adjustment(
    temp_c: float,
    humidity_pct: float,
    wind_speed_kmh: float,
    precipitation_mm: float = 0,
) -> dict:
    """
    Calculate irrigation adjustment based on weather

    Returns:
        Dictionary with adjustment factor and recommendations
    """
    base_factor = 1.0

    # Temperature adjustment
    if temp_c >= 40:
        base_factor += 0.3
    elif temp_c >= 35:
        base_factor += 0.2
    elif temp_c >= 30:
        base_factor += 0.1
    elif temp_c <= 15:
        base_factor -= 0.2

    # Humidity adjustment
    if humidity_pct <= 30:
        base_factor += 0.2
    elif humidity_pct >= 80:
        base_factor -= 0.2

    # Wind adjustment
    if wind_speed_kmh >= 30:
        base_factor += 0.15
    elif wind_speed_kmh >= 20:
        base_factor += 0.1

    # Precipitation adjustment
    if precipitation_mm >= 20:
        base_factor -= 0.5
    elif precipitation_mm >= 10:
        base_factor -= 0.3
    elif precipitation_mm >= 5:
        base_factor -= 0.15

    # Clamp to reasonable range
    base_factor = max(0.3, min(1.5, base_factor))

    return {
        "adjustment_factor": round(base_factor, 2),
        "recommendation_ar": _get_irrigation_recommendation_ar(base_factor),
        "recommendation_en": _get_irrigation_recommendation_en(base_factor),
    }


def _get_irrigation_recommendation_ar(factor: float) -> str:
    if factor >= 1.3:
        return "زيادة الري بنسبة 30% أو أكثر"
    elif factor >= 1.15:
        return "زيادة الري بنسبة 15-30%"
    elif factor >= 0.85:
        return "الري بالمعدل الطبيعي"
    elif factor >= 0.6:
        return "تقليل الري بنسبة 15-40%"
    else:
        return "تأجيل الري - رطوبة كافية"


def _get_irrigation_recommendation_en(factor: float) -> str:
    if factor >= 1.3:
        return "Increase irrigation by 30% or more"
    elif factor >= 1.15:
        return "Increase irrigation by 15-30%"
    elif factor >= 0.85:
        return "Normal irrigation rate"
    elif factor >= 0.6:
        return "Reduce irrigation by 15-40%"
    else:
        return "Delay irrigation - sufficient moisture"
