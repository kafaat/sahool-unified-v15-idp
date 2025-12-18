"""
Agricultural Weather Calculations - SAHOOL Weather Core
GDD, ET0, Spray Windows, and Crop Calendars
Merged from weather-advanced v15.3
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import math


class CropType(str, Enum):
    TOMATO = "tomato"
    WHEAT = "wheat"
    COFFEE = "coffee"
    BANANA = "banana"
    POTATO = "potato"
    CORN = "corn"
    COTTON = "cotton"
    SORGHUM = "sorghum"
    MANGO = "mango"
    GRAPE = "grape"
    DATE_PALM = "date_palm"
    QAT = "qat"
    ONION = "onion"


# Base temperatures for GDD calculation (Celsius)
CROP_BASE_TEMPS = {
    CropType.TOMATO: 10.0,
    CropType.WHEAT: 4.4,
    CropType.COFFEE: 12.0,
    CropType.BANANA: 14.0,
    CropType.POTATO: 7.0,
    CropType.CORN: 10.0,
    CropType.COTTON: 15.5,
    CropType.SORGHUM: 10.0,
    CropType.MANGO: 15.0,
    CropType.GRAPE: 10.0,
    CropType.DATE_PALM: 18.0,
    CropType.QAT: 12.0,
    CropType.ONION: 6.0,
}

# Crop calendar data (Yemen-specific)
CROP_CALENDARS = {
    CropType.TOMATO: {
        "name_ar": "طماطم",
        "planting_months": [9, 10, 2, 3],
        "harvest_months": [12, 1, 5, 6],
        "optimal_temp": (20, 30),
        "water_need": "high",
        "gdd_to_maturity": 1200,
    },
    CropType.WHEAT: {
        "name_ar": "قمح",
        "planting_months": [10, 11],
        "harvest_months": [4, 5],
        "optimal_temp": (15, 25),
        "water_need": "medium",
        "gdd_to_maturity": 1500,
    },
    CropType.COFFEE: {
        "name_ar": "بن",
        "planting_months": [3, 4],
        "harvest_months": [10, 11, 12],
        "optimal_temp": (18, 24),
        "water_need": "medium",
        "gdd_to_maturity": 2500,
    },
    CropType.BANANA: {
        "name_ar": "موز",
        "planting_months": [2, 3, 4],
        "harvest_months": list(range(1, 13)),
        "optimal_temp": (25, 35),
        "water_need": "very_high",
        "gdd_to_maturity": 2200,
    },
    CropType.POTATO: {
        "name_ar": "بطاطس",
        "planting_months": [9, 10, 2, 3],
        "harvest_months": [12, 1, 5, 6],
        "optimal_temp": (15, 20),
        "water_need": "high",
        "gdd_to_maturity": 1100,
    },
    CropType.CORN: {
        "name_ar": "ذرة",
        "planting_months": [3, 4, 7, 8],
        "harvest_months": [6, 7, 10, 11],
        "optimal_temp": (21, 30),
        "water_need": "high",
        "gdd_to_maturity": 1400,
    },
    CropType.SORGHUM: {
        "name_ar": "ذرة رفيعة",
        "planting_months": [4, 5, 7],
        "harvest_months": [8, 9, 11],
        "optimal_temp": (25, 35),
        "water_need": "low",
        "gdd_to_maturity": 1300,
    },
    CropType.DATE_PALM: {
        "name_ar": "نخيل",
        "planting_months": [2, 3, 4],
        "harvest_months": [8, 9, 10],
        "optimal_temp": (30, 40),
        "water_need": "medium",
        "gdd_to_maturity": 3000,
    },
    CropType.QAT: {
        "name_ar": "قات",
        "planting_months": [3, 4],
        "harvest_months": list(range(1, 13)),
        "optimal_temp": (18, 28),
        "water_need": "medium",
        "gdd_to_maturity": None,
    },
    CropType.ONION: {
        "name_ar": "بصل",
        "planting_months": [9, 10],
        "harvest_months": [2, 3, 4],
        "optimal_temp": (13, 24),
        "water_need": "medium",
        "gdd_to_maturity": 1000,
    },
}


@dataclass
class GDDResult:
    """Growing Degree Days calculation result"""
    crop: str
    crop_name_ar: str
    base_temp_c: float
    gdd_today: float
    gdd_accumulated: float
    gdd_to_maturity: Optional[float]
    progress_pct: Optional[float]
    days_to_maturity: Optional[int]


@dataclass
class ET0Result:
    """Evapotranspiration calculation result"""
    et0_mm: float
    irrigation_need_ar: str
    irrigation_need_en: str
    factors: dict


@dataclass
class SprayWindow:
    """Optimal spray window"""
    start_time: datetime
    end_time: datetime
    suitability_score: float
    conditions: dict


def calculate_gdd(
    temp_max_c: float,
    temp_min_c: float,
    crop: CropType = CropType.TOMATO,
    accumulated_gdd: float = 0,
) -> GDDResult:
    """
    Calculate Growing Degree Days (GDD)

    GDD = max(0, (Tmax + Tmin) / 2 - Tbase)

    Args:
        temp_max_c: Maximum daily temperature
        temp_min_c: Minimum daily temperature
        crop: Crop type for base temperature
        accumulated_gdd: Previously accumulated GDD

    Returns:
        GDDResult with calculations
    """
    base_temp = CROP_BASE_TEMPS.get(crop, 10.0)
    crop_info = CROP_CALENDARS.get(crop, CROP_CALENDARS[CropType.TOMATO])

    # Calculate average temperature
    avg_temp = (temp_max_c + temp_min_c) / 2

    # Calculate GDD (can't be negative)
    gdd_today = max(0, avg_temp - base_temp)

    # Accumulate
    total_gdd = accumulated_gdd + gdd_today

    # Calculate progress if maturity GDD is known
    gdd_to_maturity = crop_info.get("gdd_to_maturity")
    progress_pct = None
    days_to_maturity = None

    if gdd_to_maturity:
        progress_pct = min(100, (total_gdd / gdd_to_maturity) * 100)
        remaining_gdd = max(0, gdd_to_maturity - total_gdd)
        # Estimate days (assuming average 15 GDD/day in Yemen)
        if gdd_today > 0:
            days_to_maturity = int(remaining_gdd / gdd_today)
        else:
            days_to_maturity = int(remaining_gdd / 15)

    return GDDResult(
        crop=crop.value,
        crop_name_ar=crop_info["name_ar"],
        base_temp_c=base_temp,
        gdd_today=round(gdd_today, 1),
        gdd_accumulated=round(total_gdd, 1),
        gdd_to_maturity=gdd_to_maturity,
        progress_pct=round(progress_pct, 1) if progress_pct else None,
        days_to_maturity=days_to_maturity,
    )


def calculate_et0(
    temp_c: float,
    humidity_pct: float,
    wind_speed_kmh: float,
    solar_radiation_mj: float = 20.0,
    elevation_m: float = 1000,
) -> ET0Result:
    """
    Calculate Reference Evapotranspiration (ET0)

    Uses simplified Penman-Monteith equation

    Args:
        temp_c: Temperature in Celsius
        humidity_pct: Relative humidity percentage
        wind_speed_kmh: Wind speed in km/h
        solar_radiation_mj: Solar radiation in MJ/m²/day
        elevation_m: Elevation in meters

    Returns:
        ET0Result with evapotranspiration in mm/day
    """
    # Convert wind speed to m/s
    wind_speed_ms = wind_speed_kmh / 3.6

    # Atmospheric pressure (kPa) based on elevation
    pressure_kpa = 101.3 * ((293 - 0.0065 * elevation_m) / 293) ** 5.26

    # Psychrometric constant
    gamma = 0.000665 * pressure_kpa

    # Saturation vapor pressure (kPa)
    es = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))

    # Actual vapor pressure
    ea = es * humidity_pct / 100

    # Slope of saturation vapor pressure curve
    delta = (4098 * es) / ((temp_c + 237.3) ** 2)

    # Simplified Penman-Monteith (FAO-56)
    # ET0 = (0.408 * delta * Rn + gamma * (900/(T+273)) * u2 * (es-ea)) / (delta + gamma * (1 + 0.34 * u2))

    # Net radiation (simplified)
    rn = 0.77 * solar_radiation_mj  # Net shortwave

    numerator = 0.408 * delta * rn + gamma * (900 / (temp_c + 273)) * wind_speed_ms * (es - ea)
    denominator = delta + gamma * (1 + 0.34 * wind_speed_ms)

    et0 = max(0, numerator / denominator)

    # Irrigation recommendation
    if et0 > 6:
        irrig_ar = "احتياج ري عالي جداً - ري مرتين يومياً"
        irrig_en = "Very high irrigation need - irrigate twice daily"
    elif et0 > 4:
        irrig_ar = "احتياج ري عالي - ري يومي مطلوب"
        irrig_en = "High irrigation need - daily irrigation required"
    elif et0 > 2.5:
        irrig_ar = "احتياج ري متوسط - ري كل يومين"
        irrig_en = "Medium irrigation need - irrigate every 2 days"
    else:
        irrig_ar = "احتياج ري منخفض - تقليل الري ممكن"
        irrig_en = "Low irrigation need - reduced irrigation possible"

    return ET0Result(
        et0_mm=round(et0, 2),
        irrigation_need_ar=irrig_ar,
        irrigation_need_en=irrig_en,
        factors={
            "temperature_c": temp_c,
            "humidity_pct": humidity_pct,
            "wind_speed_kmh": wind_speed_kmh,
            "solar_radiation_mj": solar_radiation_mj,
            "vapor_pressure_deficit_kpa": round(es - ea, 3),
        },
    )


def find_spray_windows(
    hourly_forecasts: list[dict],
    min_hours: int = 2,
) -> list[SprayWindow]:
    """
    Find optimal spray windows in forecast data

    Criteria for spraying:
    - Wind speed < 15 km/h
    - No rain (precipitation probability < 20%)
    - Temperature 15-35°C
    - Humidity 40-80%

    Args:
        hourly_forecasts: List of hourly forecast dicts with keys:
            - datetime: datetime object
            - temp_c: temperature
            - humidity_pct: humidity
            - wind_speed_kmh: wind speed
            - precipitation_prob_pct: rain probability
        min_hours: Minimum consecutive hours for a window

    Returns:
        List of SprayWindow objects
    """
    windows = []
    current_window_start = None
    current_conditions = []

    for i, hour in enumerate(hourly_forecasts):
        is_suitable = (
            hour.get("wind_speed_kmh", 100) < 15 and
            hour.get("precipitation_prob_pct", 100) < 20 and
            15 <= hour.get("temp_c", 0) <= 35 and
            40 <= hour.get("humidity_pct", 0) <= 80
        )

        if is_suitable:
            if current_window_start is None:
                current_window_start = hour.get("datetime")
                current_conditions = [hour]
            else:
                current_conditions.append(hour)
        else:
            # Window ended
            if current_window_start and len(current_conditions) >= min_hours:
                # Calculate average suitability score
                avg_wind = sum(h.get("wind_speed_kmh", 0) for h in current_conditions) / len(current_conditions)
                avg_precip = sum(h.get("precipitation_prob_pct", 0) for h in current_conditions) / len(current_conditions)
                score = 1.0 - (avg_wind / 30) - (avg_precip / 100)

                windows.append(SprayWindow(
                    start_time=current_window_start,
                    end_time=current_conditions[-1].get("datetime"),
                    suitability_score=round(max(0, min(1, score)), 2),
                    conditions={
                        "avg_wind_kmh": round(avg_wind, 1),
                        "avg_precip_prob": round(avg_precip, 1),
                        "duration_hours": len(current_conditions),
                    },
                ))

            current_window_start = None
            current_conditions = []

    # Handle window at end of forecast
    if current_window_start and len(current_conditions) >= min_hours:
        avg_wind = sum(h.get("wind_speed_kmh", 0) for h in current_conditions) / len(current_conditions)
        avg_precip = sum(h.get("precipitation_prob_pct", 0) for h in current_conditions) / len(current_conditions)
        score = 1.0 - (avg_wind / 30) - (avg_precip / 100)

        windows.append(SprayWindow(
            start_time=current_window_start,
            end_time=current_conditions[-1].get("datetime"),
            suitability_score=round(max(0, min(1, score)), 2),
            conditions={
                "avg_wind_kmh": round(avg_wind, 1),
                "avg_precip_prob": round(avg_precip, 1),
                "duration_hours": len(current_conditions),
            },
        ))

    # Sort by suitability score
    windows.sort(key=lambda w: w.suitability_score, reverse=True)

    return windows[:10]  # Return top 10 windows


def get_crop_calendar(crop: CropType, current_month: int) -> dict:
    """
    Get crop calendar information

    Args:
        crop: Crop type
        current_month: Current month (1-12)

    Returns:
        Dictionary with calendar information
    """
    info = CROP_CALENDARS.get(crop, CROP_CALENDARS[CropType.TOMATO])

    # Determine current activity
    if current_month in info["planting_months"]:
        activity_ar = "موسم الزراعة - وقت مثالي للزراعة"
        activity_en = "Planting season - optimal time for planting"
        activity_phase = "planting"
    elif current_month in info["harvest_months"]:
        activity_ar = "موسم الحصاد - المحصول جاهز للجمع"
        activity_en = "Harvest season - crop ready for collection"
        activity_phase = "harvest"
    else:
        activity_ar = "موسم النمو - العناية والمتابعة"
        activity_en = "Growing season - care and monitoring"
        activity_phase = "growing"

    return {
        "crop": crop.value,
        "crop_name_ar": info["name_ar"],
        "current_month": current_month,
        "activity_phase": activity_phase,
        "activity_ar": activity_ar,
        "activity_en": activity_en,
        "optimal_temp_range": info["optimal_temp"],
        "water_requirement": info["water_need"],
        "planting_months": info["planting_months"],
        "harvest_months": info["harvest_months"],
        "gdd_to_maturity": info.get("gdd_to_maturity"),
    }
