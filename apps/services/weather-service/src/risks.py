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


# =============================================================================
# Frost and Heat Stress Calculations
# حسابات الصقيع والإجهاد الحراري
# =============================================================================


def calculate_frost_risk(
    temp_c: float,
    humidity_pct: float,
    wind_speed_kmh: float,
    cloud_cover_pct: float = 0,
    dew_point_c: float | None = None,
) -> dict:
    """
    Calculate frost risk and protection recommendations
    حساب خطر الصقيع وتوصيات الحماية

    Args:
        temp_c: Current or forecast minimum temperature (°C)
        humidity_pct: Relative humidity (%)
        wind_speed_kmh: Wind speed (km/h)
        cloud_cover_pct: Cloud cover percentage (0-100)
        dew_point_c: Dew point temperature (°C), calculated if not provided

    Returns:
        Dictionary with frost risk assessment and recommendations
    """
    import math

    # Calculate dew point if not provided (Magnus formula)
    if dew_point_c is None:
        a = 17.27
        b = 237.7
        alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity_pct / 100)
        dew_point_c = (b * alpha) / (a - alpha)

    # Frost risk factors
    risk_score = 0

    # Temperature factor (most important)
    if temp_c <= -5:
        risk_score += 50
        temp_risk = "severe"
    elif temp_c <= 0:
        risk_score += 40
        temp_risk = "high"
    elif temp_c <= 2:
        risk_score += 30
        temp_risk = "moderate"
    elif temp_c <= 4:
        risk_score += 15
        temp_risk = "low"
    else:
        temp_risk = "none"

    # Clear sky factor (radiation frost more likely)
    if cloud_cover_pct < 20:
        risk_score += 20
    elif cloud_cover_pct < 50:
        risk_score += 10

    # Low wind factor (cold air pooling)
    if wind_speed_kmh < 5:
        risk_score += 15
    elif wind_speed_kmh < 10:
        risk_score += 10

    # Dew point factor
    if dew_point_c <= 0:
        risk_score += 10

    # High humidity can cause frost damage at slightly higher temps
    if humidity_pct > 80 and temp_c <= 3:
        risk_score += 5

    # Classify risk level
    if risk_score >= 70:
        risk_level = "critical"
        color = "red"
    elif risk_score >= 50:
        risk_level = "high"
        color = "orange"
    elif risk_score >= 30:
        risk_level = "moderate"
        color = "yellow"
    elif risk_score >= 15:
        risk_level = "low"
        color = "blue"
    else:
        risk_level = "none"
        color = "green"

    # Protection recommendations
    protection_measures = _get_frost_protection_measures(risk_level, temp_c)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "color": color,
        "temp_risk": temp_risk,
        "dew_point_c": round(dew_point_c, 1),
        "frost_likely": risk_score >= 50,
        "protection_measures": protection_measures,
        "recommendation_ar": _get_frost_recommendation_ar(risk_level, temp_c),
        "recommendation_en": _get_frost_recommendation_en(risk_level, temp_c),
    }


def _get_frost_protection_measures(risk_level: str, temp_c: float) -> list[dict]:
    """Get frost protection measures based on risk level"""
    measures = []

    if risk_level in ["critical", "high"]:
        measures.append(
            {
                "method_en": "Sprinkler irrigation",
                "method_ar": "الري بالرشاشات",
                "description_en": "Run sprinklers overnight - ice formation releases heat",
                "description_ar": "تشغيل الرشاشات طوال الليل - تكوين الجليد يطلق حرارة",
                "effectiveness": "high",
            }
        )
        measures.append(
            {
                "method_en": "Frost cloth/blankets",
                "method_ar": "أقمشة/بطانيات الصقيع",
                "description_en": "Cover sensitive crops with frost protection fabric",
                "description_ar": "تغطية المحاصيل الحساسة بأقمشة حماية الصقيع",
                "effectiveness": "high",
            }
        )

    if risk_level in ["critical", "high", "moderate"]:
        measures.append(
            {
                "method_en": "Mulching",
                "method_ar": "التغطية العضوية",
                "description_en": "Apply thick mulch around plant bases",
                "description_ar": "وضع طبقة سميكة من التغطية حول قواعد النباتات",
                "effectiveness": "medium",
            }
        )
        measures.append(
            {
                "method_en": "Wind machines",
                "method_ar": "مراوح الرياح",
                "description_en": "Use wind machines to mix air layers",
                "description_ar": "استخدام مراوح لخلط طبقات الهواء",
                "effectiveness": "medium",
            }
        )

    if risk_level == "critical" and temp_c <= -3:
        measures.append(
            {
                "method_en": "Heaters/smudge pots",
                "method_ar": "سخانات/مواقد التدفئة",
                "description_en": "Deploy orchard heaters for severe frost",
                "description_ar": "نشر سخانات البستان للصقيع الشديد",
                "effectiveness": "high",
            }
        )

    return measures


def _get_frost_recommendation_ar(risk_level: str, temp_c: float) -> str:
    if risk_level == "critical":
        return f"خطر صقيع حرج ({temp_c}°م) - اتخذ إجراءات حماية فورية"
    elif risk_level == "high":
        return f"خطر صقيع مرتفع ({temp_c}°م) - جهز وسائل الحماية الليلة"
    elif risk_level == "moderate":
        return f"خطر صقيع معتدل ({temp_c}°م) - راقب الحرارة وكن مستعداً"
    elif risk_level == "low":
        return "خطر صقيع منخفض - لا حاجة لإجراءات خاصة"
    else:
        return "لا خطر صقيع متوقع"


def _get_frost_recommendation_en(risk_level: str, temp_c: float) -> str:
    if risk_level == "critical":
        return f"Critical frost risk ({temp_c}°C) - Take immediate protective action"
    elif risk_level == "high":
        return f"High frost risk ({temp_c}°C) - Prepare protection measures tonight"
    elif risk_level == "moderate":
        return f"Moderate frost risk ({temp_c}°C) - Monitor temperatures and be ready"
    elif risk_level == "low":
        return "Low frost risk - No special measures needed"
    else:
        return "No frost risk expected"


def calculate_heat_stress_index(
    temp_c: float,
    humidity_pct: float,
    solar_radiation_mj: float = 15.0,
    wind_speed_kmh: float = 10.0,
) -> dict:
    """
    Calculate heat stress index for crops
    حساب مؤشر الإجهاد الحراري للمحاصيل

    Based on Temperature-Humidity Index (THI) adapted for crops

    Args:
        temp_c: Current temperature (°C)
        humidity_pct: Relative humidity (%)
        solar_radiation_mj: Solar radiation (MJ/m²/day)
        wind_speed_kmh: Wind speed (km/h)

    Returns:
        Dictionary with heat stress assessment and recommendations
    """
    # Calculate Temperature-Humidity Index (simplified)
    # THI = 0.8 * T + (RH / 100) * (T - 14.4) + 46.4
    thi = 0.8 * temp_c + (humidity_pct / 100) * (temp_c - 14.4) + 46.4

    # Crop Heat Unit (CHU) style calculation
    # Adjusted for high solar radiation conditions
    solar_factor = min(1.5, solar_radiation_mj / 15.0)
    wind_cooling = min(5, wind_speed_kmh / 5) * 0.5

    effective_stress = (temp_c - 25) * solar_factor - wind_cooling
    effective_stress = max(0, effective_stress)

    # Classify heat stress level
    if temp_c >= 45:
        stress_level = "extreme"
        color = "darkred"
        crop_impact = "severe_damage"
    elif temp_c >= 40 or (temp_c >= 35 and humidity_pct >= 60):
        stress_level = "severe"
        color = "red"
        crop_impact = "significant_damage"
    elif temp_c >= 35 or (temp_c >= 30 and humidity_pct >= 70):
        stress_level = "high"
        color = "orange"
        crop_impact = "reduced_growth"
    elif temp_c >= 30:
        stress_level = "moderate"
        color = "yellow"
        crop_impact = "minor_stress"
    elif temp_c >= 25:
        stress_level = "low"
        color = "lightgreen"
        crop_impact = "optimal"
    else:
        stress_level = "none"
        color = "green"
        crop_impact = "optimal"

    # Mitigation recommendations
    mitigation = _get_heat_mitigation_measures(stress_level, temp_c, humidity_pct)

    return {
        "temperature_humidity_index": round(thi, 1),
        "effective_stress_score": round(effective_stress, 2),
        "stress_level": stress_level,
        "color": color,
        "crop_impact": crop_impact,
        "is_critical": stress_level in ["extreme", "severe"],
        "mitigation_measures": mitigation,
        "recommendation_ar": _get_heat_recommendation_ar(stress_level, temp_c),
        "recommendation_en": _get_heat_recommendation_en(stress_level, temp_c),
    }


def _get_heat_mitigation_measures(
    stress_level: str, temp_c: float, humidity_pct: float
) -> list[dict]:
    """Get heat stress mitigation measures"""
    measures = []

    if stress_level in ["extreme", "severe", "high"]:
        measures.append(
            {
                "method_en": "Increase irrigation frequency",
                "method_ar": "زيادة تكرار الري",
                "description_en": "Water in early morning and late evening",
                "description_ar": "الري في الصباح الباكر والمساء المتأخر",
                "priority": "high",
            }
        )
        measures.append(
            {
                "method_en": "Shade netting",
                "method_ar": "شبكات التظليل",
                "description_en": "Install 30-50% shade cloth for sensitive crops",
                "description_ar": "تركيب قماش تظليل 30-50% للمحاصيل الحساسة",
                "priority": "high",
            }
        )

    if stress_level in ["extreme", "severe"]:
        measures.append(
            {
                "method_en": "Foliar cooling sprays",
                "method_ar": "رش ورقي للتبريد",
                "description_en": "Apply light water mist to reduce leaf temperature",
                "description_ar": "رش رذاذ ماء خفيف لتخفيض حرارة الأوراق",
                "priority": "high",
            }
        )
        measures.append(
            {
                "method_en": "Avoid field work",
                "method_ar": "تجنب العمل الحقلي",
                "description_en": "No harvesting or cultivation during peak heat",
                "description_ar": "لا حصاد أو زراعة خلال ذروة الحرارة",
                "priority": "high",
            }
        )

    if stress_level in ["extreme", "severe", "high", "moderate"]:
        measures.append(
            {
                "method_en": "Mulching",
                "method_ar": "التغطية العضوية",
                "description_en": "Apply organic mulch to reduce soil temperature",
                "description_ar": "وضع تغطية عضوية لتخفيض حرارة التربة",
                "priority": "medium",
            }
        )

    if humidity_pct < 40 and stress_level != "none":
        measures.append(
            {
                "method_en": "Anti-transpirant sprays",
                "method_ar": "مضادات النتح",
                "description_en": "Apply kaolin clay or other anti-transpirants",
                "description_ar": "رش طين الكاولين أو مضادات نتح أخرى",
                "priority": "medium",
            }
        )

    return measures


def _get_heat_recommendation_ar(stress_level: str, temp_c: float) -> str:
    if stress_level == "extreme":
        return f"إجهاد حراري شديد ({temp_c}°م) - اتخذ إجراءات حماية طارئة"
    elif stress_level == "severe":
        return f"إجهاد حراري مرتفع ({temp_c}°م) - زد الري وقلل العمل الحقلي"
    elif stress_level == "high":
        return f"إجهاد حراري ملحوظ ({temp_c}°م) - راقب المحاصيل وزد الري"
    elif stress_level == "moderate":
        return "إجهاد حراري معتدل - اروِ في الصباح الباكر أو المساء"
    elif stress_level == "low":
        return "إجهاد حراري منخفض - ظروف طبيعية"
    else:
        return "لا إجهاد حراري - ظروف مثالية للنمو"


def _get_heat_recommendation_en(stress_level: str, temp_c: float) -> str:
    if stress_level == "extreme":
        return f"Extreme heat stress ({temp_c}°C) - Take emergency protective measures"
    elif stress_level == "severe":
        return f"Severe heat stress ({temp_c}°C) - Increase irrigation and reduce field work"
    elif stress_level == "high":
        return f"High heat stress ({temp_c}°C) - Monitor crops and increase irrigation"
    elif stress_level == "moderate":
        return "Moderate heat stress - Irrigate in early morning or evening"
    elif stress_level == "low":
        return "Low heat stress - Normal conditions"
    else:
        return "No heat stress - Optimal growing conditions"


def calculate_chill_hours(
    hourly_temps: list[float],
    model: str = "utah",
    base_temp_c: float = 7.2,
) -> dict:
    """
    Calculate chill hours/units for fruit trees and perennials
    حساب ساعات البرودة للأشجار المثمرة والمعمرات

    Supports multiple chill models:
    - "simple": Hours below threshold (traditional)
    - "utah": Utah Chill Unit model (more accurate)
    - "dynamic": Dynamic model (for mild winters)

    Args:
        hourly_temps: List of hourly temperatures (°C)
        model: Chill calculation model ("simple", "utah", "dynamic")
        base_temp_c: Base temperature for simple model (default 7.2°C/45°F)

    Returns:
        Dictionary with chill hours/units and crop requirements
    """
    if not hourly_temps:
        return {
            "chill_units": 0,
            "model": model,
            "hours_analyzed": 0,
            "error": "No temperature data provided",
        }

    chill_units = 0.0

    if model == "simple":
        # Simple model: count hours below threshold
        chill_units = sum(1 for t in hourly_temps if t <= base_temp_c)

    elif model == "utah":
        # Utah Chill Unit model
        for temp in hourly_temps:
            if temp <= 1.4:
                chill_units += 0.0
            elif temp <= 2.4:
                chill_units += 0.5
            elif temp <= 9.1:
                chill_units += 1.0
            elif temp <= 12.4:
                chill_units += 0.5
            elif temp <= 15.9:
                chill_units += 0.0
            elif temp <= 18.0:
                chill_units -= 0.5
            else:
                chill_units -= 1.0

        # Chill units can't go negative for the season
        chill_units = max(0, chill_units)

    elif model == "dynamic":
        # Simplified Dynamic Model
        # More complex in reality, this is an approximation
        for temp in hourly_temps:
            if 0 <= temp <= 6:
                chill_units += 1.0
            elif 6 < temp <= 8:
                chill_units += 0.8
            elif 8 < temp <= 13:
                chill_units += 0.4
            elif temp > 16:
                chill_units -= 0.2

        chill_units = max(0, chill_units)

    # Crop chill requirements (approximate values in chill units)
    crop_requirements = {
        "apple": {"min": 800, "max": 1500, "name_ar": "تفاح"},
        "peach": {"min": 400, "max": 1000, "name_ar": "خوخ"},
        "cherry": {"min": 700, "max": 1200, "name_ar": "كرز"},
        "apricot": {"min": 300, "max": 900, "name_ar": "مشمش"},
        "plum": {"min": 500, "max": 1000, "name_ar": "برقوق"},
        "grape": {"min": 100, "max": 400, "name_ar": "عنب"},
        "almond": {"min": 200, "max": 700, "name_ar": "لوز"},
        "fig": {"min": 100, "max": 300, "name_ar": "تين"},
        "pomegranate": {"min": 100, "max": 200, "name_ar": "رمان"},
        "olive": {"min": 200, "max": 600, "name_ar": "زيتون"},
    }

    # Determine which crops can be satisfied
    satisfied_crops = []
    insufficient_crops = []

    for crop, req in crop_requirements.items():
        if chill_units >= req["min"]:
            satisfied_crops.append(
                {
                    "crop": crop,
                    "crop_ar": req["name_ar"],
                    "requirement_met_pct": min(100, round(chill_units / req["min"] * 100)),
                }
            )
        else:
            insufficient_crops.append(
                {
                    "crop": crop,
                    "crop_ar": req["name_ar"],
                    "required": req["min"],
                    "current": round(chill_units),
                    "deficit": round(req["min"] - chill_units),
                }
            )

    return {
        "chill_units": round(chill_units, 1),
        "model": model,
        "base_temp_c": base_temp_c if model == "simple" else None,
        "hours_analyzed": len(hourly_temps),
        "satisfied_crops": satisfied_crops,
        "insufficient_crops": insufficient_crops,
        "crop_requirements": crop_requirements,
        "recommendation_ar": _get_chill_recommendation_ar(chill_units),
        "recommendation_en": _get_chill_recommendation_en(chill_units),
    }


def _get_chill_recommendation_ar(chill_units: float) -> str:
    if chill_units >= 1000:
        return "ساعات برودة ممتازة - مناسب لجميع الفواكه المعتدلة"
    elif chill_units >= 700:
        return "ساعات برودة جيدة - مناسب لمعظم الفواكه"
    elif chill_units >= 400:
        return "ساعات برودة معتدلة - اختر أصناف منخفضة البرودة"
    elif chill_units >= 200:
        return "ساعات برودة منخفضة - فقط للفواكه الاستوائية وشبه الاستوائية"
    else:
        return "ساعات برودة غير كافية - منطقة استوائية"


def _get_chill_recommendation_en(chill_units: float) -> str:
    if chill_units >= 1000:
        return "Excellent chill accumulation - suitable for all temperate fruits"
    elif chill_units >= 700:
        return "Good chill accumulation - suitable for most fruits"
    elif chill_units >= 400:
        return "Moderate chill accumulation - select low-chill varieties"
    elif chill_units >= 200:
        return "Low chill accumulation - only tropical/subtropical fruits"
    else:
        return "Insufficient chill hours - tropical climate"


def calculate_drought_index(
    precipitation_mm: float,
    et0_mm: float,
    days: int = 30,
    soil_water_capacity_mm: float = 100,
) -> dict:
    """
    Calculate drought stress index
    حساب مؤشر الإجهاد الجفافي

    Based on water balance approach

    Args:
        precipitation_mm: Total precipitation over period (mm)
        et0_mm: Total evapotranspiration over period (mm)
        days: Number of days in period
        soil_water_capacity_mm: Available soil water capacity (mm)

    Returns:
        Dictionary with drought assessment
    """
    # Water balance
    water_balance = precipitation_mm - et0_mm

    # Aridity index (P/ET0)
    aridity_index = precipitation_mm / et0_mm if et0_mm > 0 else float("inf")

    # Drought severity
    if aridity_index >= 1.0:
        drought_level = "none"
        color = "green"
    elif aridity_index >= 0.75:
        drought_level = "mild"
        color = "yellow"
    elif aridity_index >= 0.50:
        drought_level = "moderate"
        color = "orange"
    elif aridity_index >= 0.25:
        drought_level = "severe"
        color = "red"
    else:
        drought_level = "extreme"
        color = "darkred"

    # Irrigation need
    irrigation_need_mm = max(0, et0_mm - precipitation_mm)

    return {
        "water_balance_mm": round(water_balance, 1),
        "aridity_index": round(aridity_index, 2),
        "drought_level": drought_level,
        "color": color,
        "irrigation_need_mm": round(irrigation_need_mm, 1),
        "irrigation_need_liters_per_sqm": round(irrigation_need_mm, 1),  # 1mm = 1 L/m²
        "period_days": days,
        "precipitation_mm": precipitation_mm,
        "evapotranspiration_mm": et0_mm,
        "recommendation_ar": _get_drought_recommendation_ar(drought_level, irrigation_need_mm),
        "recommendation_en": _get_drought_recommendation_en(drought_level, irrigation_need_mm),
    }


def _get_drought_recommendation_ar(drought_level: str, irrigation_mm: float) -> str:
    if drought_level == "extreme":
        return f"جفاف شديد - ري عاجل بمعدل {irrigation_mm:.0f} مم/م²"
    elif drought_level == "severe":
        return f"جفاف حاد - زد الري إلى {irrigation_mm:.0f} مم/م²"
    elif drought_level == "moderate":
        return f"جفاف معتدل - ري إضافي {irrigation_mm:.0f} مم/م² مطلوب"
    elif drought_level == "mild":
        return "جفاف خفيف - راقب رطوبة التربة"
    else:
        return "لا جفاف - توازن مائي جيد"


def _get_drought_recommendation_en(drought_level: str, irrigation_mm: float) -> str:
    if drought_level == "extreme":
        return f"Extreme drought - Urgent irrigation at {irrigation_mm:.0f} mm/m²"
    elif drought_level == "severe":
        return f"Severe drought - Increase irrigation to {irrigation_mm:.0f} mm/m²"
    elif drought_level == "moderate":
        return f"Moderate drought - Additional {irrigation_mm:.0f} mm/m² irrigation needed"
    elif drought_level == "mild":
        return "Mild drought - Monitor soil moisture"
    else:
        return "No drought - Good water balance"
