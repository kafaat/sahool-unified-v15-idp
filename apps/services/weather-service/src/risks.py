"""
Weather Risk Assessment - SAHOOL Weather Core
Agricultural weather risk evaluation for Yemen
"""

from dataclasses import dataclass
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


# =============================================================================
# Advanced Agricultural Calculations
# الحسابات الزراعية المتقدمة
# =============================================================================


def calculate_evapotranspiration(
    temp_c: float,
    humidity_pct: float,
    wind_speed_kmh: float,
    solar_radiation_mj: float = 15.0,  # Default for Yemen (high solar)
) -> dict:
    """
    Calculate Reference Evapotranspiration (ET0) using simplified Penman-Monteith
    حساب التبخر-نتح المرجعي باستخدام معادلة بنمان-مونتيث المبسطة

    Based on FAO-56 Penman-Monteith equation (simplified)

    Args:
        temp_c: Average temperature (°C)
        humidity_pct: Relative humidity (%)
        wind_speed_kmh: Wind speed at 2m height (km/h)
        solar_radiation_mj: Solar radiation (MJ/m²/day), default 15 for Yemen

    Returns:
        Dictionary with ET0 and irrigation recommendations
    """
    import math

    # Convert wind speed from km/h to m/s
    wind_speed_ms = wind_speed_kmh / 3.6

    # Saturation vapor pressure (kPa)
    es = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))

    # Actual vapor pressure (kPa)
    ea = es * (humidity_pct / 100)

    # Vapor pressure deficit (kPa)
    vpd = es - ea

    # Slope of saturation vapor pressure curve (kPa/°C)
    delta = (4098 * es) / ((temp_c + 237.3) ** 2)

    # Psychrometric constant (kPa/°C) - approximately 0.066 at sea level
    gamma = 0.066

    # Net radiation (MJ/m²/day) - simplified as 77% of solar radiation
    rn = solar_radiation_mj * 0.77

    # Soil heat flux (MJ/m²/day) - assume 0 for daily calculations
    g = 0

    # Reference ET0 (mm/day) - FAO-56 Penman-Monteith (simplified)
    numerator = 0.408 * delta * (rn - g) + gamma * (900 / (temp_c + 273)) * wind_speed_ms * vpd
    denominator = delta + gamma * (1 + 0.34 * wind_speed_ms)
    et0 = numerator / denominator

    # Clamp to reasonable range (0-15 mm/day)
    et0 = max(0, min(15, et0))

    # Calculate water needs
    daily_water_liters_per_sqm = et0  # 1 mm = 1 L/m²

    return {
        "et0_mm_day": round(et0, 2),
        "daily_water_liters_per_sqm": round(daily_water_liters_per_sqm, 2),
        "weekly_water_liters_per_sqm": round(et0 * 7, 2),
        "vapor_pressure_deficit_kpa": round(vpd, 3),
        "classification": _classify_et0(et0),
        "recommendation_ar": _get_et0_recommendation_ar(et0),
        "recommendation_en": _get_et0_recommendation_en(et0),
    }


def _classify_et0(et0: float) -> str:
    """Classify ET0 level"""
    if et0 < 2:
        return "very_low"
    elif et0 < 4:
        return "low"
    elif et0 < 6:
        return "moderate"
    elif et0 < 8:
        return "high"
    else:
        return "very_high"


def _get_et0_recommendation_ar(et0: float) -> str:
    if et0 < 2:
        return "تبخر-نتح منخفض جداً - الري كل 5-7 أيام"
    elif et0 < 4:
        return "تبخر-نتح منخفض - الري كل 3-4 أيام"
    elif et0 < 6:
        return "تبخر-نتح معتدل - الري كل 2-3 أيام"
    elif et0 < 8:
        return "تبخر-نتح مرتفع - الري يومياً أو كل يومين"
    else:
        return "تبخر-نتح مرتفع جداً - الري يومياً مع زيادة الكمية"


def _get_et0_recommendation_en(et0: float) -> str:
    if et0 < 2:
        return "Very low ET - Irrigate every 5-7 days"
    elif et0 < 4:
        return "Low ET - Irrigate every 3-4 days"
    elif et0 < 6:
        return "Moderate ET - Irrigate every 2-3 days"
    elif et0 < 8:
        return "High ET - Irrigate daily or every 2 days"
    else:
        return "Very high ET - Daily irrigation with increased volume"


def calculate_growing_degree_days(
    temp_max_c: float,
    temp_min_c: float,
    base_temp_c: float = 10.0,
    upper_temp_c: float = 30.0,
) -> dict:
    """
    Calculate Growing Degree Days (GDD)
    حساب أيام النمو الحراري

    GDD is used to predict crop development stages

    Args:
        temp_max_c: Maximum daily temperature (°C)
        temp_min_c: Minimum daily temperature (°C)
        base_temp_c: Base temperature for crop (default 10°C for many crops)
        upper_temp_c: Upper threshold temperature (default 30°C)

    Returns:
        Dictionary with GDD and crop development info
    """
    # Apply upper cutoff
    temp_max_adj = min(temp_max_c, upper_temp_c)
    temp_min_adj = max(temp_min_c, base_temp_c)

    # Ensure min doesn't exceed max after adjustments
    temp_min_adj = min(temp_min_adj, temp_max_adj)

    # Calculate average temperature
    temp_avg = (temp_max_adj + temp_min_adj) / 2

    # Calculate GDD (only positive values)
    gdd = max(0, temp_avg - base_temp_c)

    return {
        "gdd_daily": round(gdd, 2),
        "temp_avg_c": round(temp_avg, 2),
        "base_temp_c": base_temp_c,
        "upper_temp_c": upper_temp_c,
        "growth_rate": _classify_growth_rate(gdd, base_temp_c),
        "recommendation_ar": _get_gdd_recommendation_ar(gdd),
        "recommendation_en": _get_gdd_recommendation_en(gdd),
    }


def _classify_growth_rate(gdd: float, base_temp: float) -> str:
    """Classify growth rate based on GDD"""
    if gdd <= 0:
        return "dormant"
    elif gdd < 5:
        return "slow"
    elif gdd < 10:
        return "moderate"
    elif gdd < 15:
        return "fast"
    else:
        return "very_fast"


def _get_gdd_recommendation_ar(gdd: float) -> str:
    if gdd <= 0:
        return "الحرارة أقل من عتبة النمو - النبات في حالة سكون"
    elif gdd < 5:
        return "نمو بطيء - مراقبة الري والتسميد"
    elif gdd < 10:
        return "نمو معتدل - ظروف مثالية لمعظم المحاصيل"
    elif gdd < 15:
        return "نمو سريع - زيادة التغذية والري"
    else:
        return "نمو سريع جداً - احتمال إجهاد حراري"


def _get_gdd_recommendation_en(gdd: float) -> str:
    if gdd <= 0:
        return "Temperature below growth threshold - plant dormant"
    elif gdd < 5:
        return "Slow growth - monitor irrigation and fertilization"
    elif gdd < 10:
        return "Moderate growth - optimal conditions for most crops"
    elif gdd < 15:
        return "Fast growth - increase nutrients and irrigation"
    else:
        return "Very fast growth - potential heat stress"


def calculate_spray_window(
    temp_c: float,
    humidity_pct: float,
    wind_speed_kmh: float,
    precipitation_probability: float = 0,
) -> dict:
    """
    Determine if conditions are suitable for spraying
    تحديد مدى ملاءمة الظروف للرش

    Args:
        temp_c: Current temperature (°C)
        humidity_pct: Relative humidity (%)
        wind_speed_kmh: Wind speed (km/h)
        precipitation_probability: Rain probability (0-100)

    Returns:
        Dictionary with spray window suitability
    """
    # Ideal spray conditions:
    # - Temperature: 15-28°C
    # - Humidity: 40-80%
    # - Wind: < 15 km/h
    # - No rain expected

    issues = []
    score = 100

    # Temperature check
    if temp_c < 10:
        issues.append("temperature_too_low")
        score -= 30
    elif temp_c < 15:
        issues.append("temperature_low")
        score -= 15
    elif temp_c > 35:
        issues.append("temperature_too_high")
        score -= 40
    elif temp_c > 28:
        issues.append("temperature_high")
        score -= 20

    # Humidity check
    if humidity_pct < 30:
        issues.append("humidity_too_low")
        score -= 25
    elif humidity_pct < 40:
        issues.append("humidity_low")
        score -= 10
    elif humidity_pct > 90:
        issues.append("humidity_too_high")
        score -= 30
    elif humidity_pct > 80:
        issues.append("humidity_high")
        score -= 15

    # Wind check
    if wind_speed_kmh > 25:
        issues.append("wind_too_strong")
        score -= 50
    elif wind_speed_kmh > 15:
        issues.append("wind_strong")
        score -= 25

    # Rain check
    if precipitation_probability > 70:
        issues.append("rain_likely")
        score -= 40
    elif precipitation_probability > 40:
        issues.append("rain_possible")
        score -= 20

    score = max(0, score)

    if score >= 80:
        suitability = "excellent"
        color = "green"
    elif score >= 60:
        suitability = "good"
        color = "yellow"
    elif score >= 40:
        suitability = "fair"
        color = "orange"
    else:
        suitability = "poor"
        color = "red"

    return {
        "score": score,
        "suitability": suitability,
        "color": color,
        "is_suitable": score >= 60,
        "issues": issues,
        "recommendation_ar": _get_spray_recommendation_ar(suitability, issues),
        "recommendation_en": _get_spray_recommendation_en(suitability, issues),
    }


def _get_spray_recommendation_ar(suitability: str, issues: list) -> str:
    if suitability == "excellent":
        return "ظروف مثالية للرش - يُنصح بالرش الآن"
    elif suitability == "good":
        return "ظروف جيدة للرش - يمكن الرش مع مراقبة الظروف"
    elif suitability == "fair":
        return "ظروف مقبولة - الرش ممكن مع الحذر"
    else:
        if "wind_too_strong" in issues:
            return "رياح قوية - تأجيل الرش حتى تهدأ"
        elif "rain_likely" in issues:
            return "أمطار متوقعة - تأجيل الرش"
        elif "temperature_too_high" in issues:
            return "حرارة مرتفعة - الرش في الصباح الباكر"
        return "ظروف غير ملائمة - تأجيل الرش"


def _get_spray_recommendation_en(suitability: str, issues: list) -> str:
    if suitability == "excellent":
        return "Excellent spray conditions - spray now recommended"
    elif suitability == "good":
        return "Good spray conditions - spraying possible with monitoring"
    elif suitability == "fair":
        return "Fair conditions - spraying possible with caution"
    else:
        if "wind_too_strong" in issues:
            return "Strong wind - delay spraying until calmer"
        elif "rain_likely" in issues:
            return "Rain expected - delay spraying"
        elif "temperature_too_high" in issues:
            return "High temperature - spray in early morning"
        return "Unfavorable conditions - delay spraying"
