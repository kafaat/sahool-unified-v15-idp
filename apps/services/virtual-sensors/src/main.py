"""
Virtual Sensors Engine - Sahool Smart Irrigation v15.5
محرك المستشعرات الافتراضية - الري الذكي سهول

Software-based sensor calculations for irrigation management without physical hardware.
Calculates evapotranspiration, soil moisture estimation, and irrigation recommendations
using weather data, crop coefficients, and soil characteristics.

Based on FAO-56 Penman-Monteith methodology.

Field-First Architecture:
- بديل تشغيلي لـ IoT في البيئات الريفية
- ينتج ActionTemplates للتطبيق المحمول
- يتكامل مع NATS للإشعارات الفورية
- Badge "تقدير افتراضي" لتمييز البيانات عن IoT
"""

import os
import math
import uuid
import logging
from datetime import datetime, date, time, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# NATS publisher (optional)
_nats_available = False
try:
    import sys

    sys.path.insert(0, "/home/user/sahool-unified-v15-idp")
    from shared.libs.events.nats_publisher import publish_analysis_completed_sync

    _nats_available = True
except ImportError:
    logger.info("NATS publisher not available")
    publish_analysis_completed_sync = None

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "virtual-sensors"
SERVICE_VERSION = "15.5.0"
SERVICE_PORT = 8096


# ═══════════════════════════════════════════════════════════════════════════════
# Enums and Constants
# ═══════════════════════════════════════════════════════════════════════════════


class GrowthStage(str, Enum):
    """Crop growth stages for Kc determination"""

    INITIAL = "initial"  # المرحلة الأولية
    DEVELOPMENT = "development"  # مرحلة النمو
    MID_SEASON = "mid_season"  # منتصف الموسم
    LATE_SEASON = "late_season"  # نهاية الموسم


class SoilType(str, Enum):
    """Soil types common in Yemen"""

    SANDY = "sandy"  # رملي
    SANDY_LOAM = "sandy_loam"  # رملي طميي
    LOAM = "loam"  # طميي
    CLAY_LOAM = "clay_loam"  # طيني طميي
    CLAY = "clay"  # طيني
    SILTY_CLAY = "silty_clay"  # طيني غريني


class IrrigationMethod(str, Enum):
    """Irrigation methods"""

    DRIP = "drip"  # تنقيط
    SPRINKLER = "sprinkler"  # رش
    SURFACE = "surface"  # سطحي
    FLOOD = "flood"  # غمر
    FURROW = "furrow"  # أخاديد


class UrgencyLevel(str, Enum):
    """Irrigation urgency levels"""

    NONE = "none"  # لا حاجة
    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # عالي
    CRITICAL = "critical"  # حرج


# ═══════════════════════════════════════════════════════════════════════════════
# Crop Coefficients Database (FAO-56 values adapted for Yemen)
# معاملات المحاصيل - قيم FAO-56 معدلة لليمن
# ═══════════════════════════════════════════════════════════════════════════════

CROP_COEFFICIENTS = {
    "wheat": {
        "name_ar": "القمح",
        "kc_initial": 0.3,
        "kc_mid": 1.15,
        "kc_end": 0.25,
        "root_depth_max": 1.5,  # meters
        "depletion_fraction": 0.55,
        "stages_days": {
            "initial": 20,
            "development": 30,
            "mid_season": 60,
            "late_season": 30,
        },
        "critical_periods": ["flowering", "grain_filling"],
    },
    "barley": {
        "name_ar": "الشعير",
        "kc_initial": 0.3,
        "kc_mid": 1.15,
        "kc_end": 0.25,
        "root_depth_max": 1.2,
        "depletion_fraction": 0.55,
        "stages_days": {
            "initial": 15,
            "development": 25,
            "mid_season": 50,
            "late_season": 30,
        },
        "critical_periods": ["flowering"],
    },
    "sorghum": {
        "name_ar": "الذرة الرفيعة",
        "kc_initial": 0.3,
        "kc_mid": 1.10,
        "kc_end": 0.55,
        "root_depth_max": 1.5,
        "depletion_fraction": 0.55,
        "stages_days": {
            "initial": 20,
            "development": 35,
            "mid_season": 40,
            "late_season": 30,
        },
        "critical_periods": ["flowering", "grain_filling"],
    },
    "maize": {
        "name_ar": "الذرة",
        "kc_initial": 0.3,
        "kc_mid": 1.20,
        "kc_end": 0.35,
        "root_depth_max": 1.5,
        "depletion_fraction": 0.55,
        "stages_days": {
            "initial": 20,
            "development": 35,
            "mid_season": 40,
            "late_season": 30,
        },
        "critical_periods": ["tasseling", "silking"],
    },
    "tomato": {
        "name_ar": "الطماطم",
        "kc_initial": 0.6,
        "kc_mid": 1.15,
        "kc_end": 0.80,
        "root_depth_max": 1.0,
        "depletion_fraction": 0.40,
        "stages_days": {
            "initial": 30,
            "development": 40,
            "mid_season": 45,
            "late_season": 30,
        },
        "critical_periods": ["flowering", "fruit_set"],
    },
    "potato": {
        "name_ar": "البطاطس",
        "kc_initial": 0.5,
        "kc_mid": 1.15,
        "kc_end": 0.75,
        "root_depth_max": 0.6,
        "depletion_fraction": 0.35,
        "stages_days": {
            "initial": 25,
            "development": 30,
            "mid_season": 45,
            "late_season": 30,
        },
        "critical_periods": ["tuber_initiation", "tuber_bulking"],
    },
    "onion": {
        "name_ar": "البصل",
        "kc_initial": 0.7,
        "kc_mid": 1.05,
        "kc_end": 0.75,
        "root_depth_max": 0.4,
        "depletion_fraction": 0.30,
        "stages_days": {
            "initial": 15,
            "development": 25,
            "mid_season": 70,
            "late_season": 40,
        },
        "critical_periods": ["bulb_formation"],
    },
    "coffee": {
        "name_ar": "البن اليمني",
        "kc_initial": 0.90,
        "kc_mid": 0.95,
        "kc_end": 0.90,
        "root_depth_max": 1.5,
        "depletion_fraction": 0.40,
        "stages_days": {
            "initial": 60,
            "development": 90,
            "mid_season": 120,
            "late_season": 95,
        },
        "critical_periods": ["flowering", "cherry_development"],
    },
    "date_palm": {
        "name_ar": "النخيل",
        "kc_initial": 0.90,
        "kc_mid": 1.00,
        "kc_end": 0.90,
        "root_depth_max": 2.5,
        "depletion_fraction": 0.50,
        "stages_days": {
            "initial": 90,
            "development": 60,
            "mid_season": 120,
            "late_season": 95,
        },
        "critical_periods": ["pollination", "fruit_development"],
    },
    "mango": {
        "name_ar": "المانجو",
        "kc_initial": 0.75,
        "kc_mid": 0.90,
        "kc_end": 0.80,
        "root_depth_max": 2.0,
        "depletion_fraction": 0.50,
        "stages_days": {
            "initial": 60,
            "development": 90,
            "mid_season": 120,
            "late_season": 95,
        },
        "critical_periods": ["flowering", "fruit_set"],
    },
    "grape": {
        "name_ar": "العنب",
        "kc_initial": 0.30,
        "kc_mid": 0.85,
        "kc_end": 0.45,
        "root_depth_max": 1.5,
        "depletion_fraction": 0.45,
        "stages_days": {
            "initial": 20,
            "development": 40,
            "mid_season": 120,
            "late_season": 60,
        },
        "critical_periods": ["flowering", "veraison"],
    },
    "alfalfa": {
        "name_ar": "البرسيم",
        "kc_initial": 0.40,
        "kc_mid": 1.20,
        "kc_end": 1.15,
        "root_depth_max": 1.5,
        "depletion_fraction": 0.55,
        "stages_days": {
            "initial": 10,
            "development": 20,
            "mid_season": 20,
            "late_season": 10,
        },
        "critical_periods": ["regrowth"],
    },
    "qat": {
        "name_ar": "القات",
        "kc_initial": 0.85,
        "kc_mid": 1.00,
        "kc_end": 0.90,
        "root_depth_max": 1.5,
        "depletion_fraction": 0.50,
        "stages_days": {
            "initial": 60,
            "development": 90,
            "mid_season": 150,
            "late_season": 65,
        },
        "critical_periods": ["harvest_regrowth"],
    },
    "banana": {
        "name_ar": "الموز",
        "kc_initial": 0.50,
        "kc_mid": 1.10,
        "kc_end": 1.00,
        "root_depth_max": 0.6,
        "depletion_fraction": 0.35,
        "stages_days": {
            "initial": 120,
            "development": 60,
            "mid_season": 180,
            "late_season": 60,
        },
        "critical_periods": ["flowering", "bunch_development"],
    },
    "sesame": {
        "name_ar": "السمسم",
        "kc_initial": 0.35,
        "kc_mid": 1.10,
        "kc_end": 0.25,
        "root_depth_max": 1.0,
        "depletion_fraction": 0.60,
        "stages_days": {
            "initial": 20,
            "development": 30,
            "mid_season": 35,
            "late_season": 25,
        },
        "critical_periods": ["flowering"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Soil Properties Database
# خصائص التربة
# ═══════════════════════════════════════════════════════════════════════════════

SOIL_PROPERTIES = {
    SoilType.SANDY: {
        "name_ar": "رملي",
        "field_capacity": 0.12,  # m³/m³
        "wilting_point": 0.04,  # m³/m³
        "saturation": 0.38,  # m³/m³
        "infiltration_rate": 50,  # mm/hour
        "hydraulic_conductivity": 200,  # mm/day
    },
    SoilType.SANDY_LOAM: {
        "name_ar": "رملي طميي",
        "field_capacity": 0.20,
        "wilting_point": 0.08,
        "saturation": 0.42,
        "infiltration_rate": 25,
        "hydraulic_conductivity": 100,
    },
    SoilType.LOAM: {
        "name_ar": "طميي",
        "field_capacity": 0.27,
        "wilting_point": 0.12,
        "saturation": 0.45,
        "infiltration_rate": 13,
        "hydraulic_conductivity": 50,
    },
    SoilType.CLAY_LOAM: {
        "name_ar": "طيني طميي",
        "field_capacity": 0.32,
        "wilting_point": 0.18,
        "saturation": 0.47,
        "infiltration_rate": 8,
        "hydraulic_conductivity": 20,
    },
    SoilType.CLAY: {
        "name_ar": "طيني",
        "field_capacity": 0.38,
        "wilting_point": 0.25,
        "saturation": 0.50,
        "infiltration_rate": 3,
        "hydraulic_conductivity": 5,
    },
    SoilType.SILTY_CLAY: {
        "name_ar": "طيني غريني",
        "field_capacity": 0.35,
        "wilting_point": 0.22,
        "saturation": 0.48,
        "infiltration_rate": 5,
        "hydraulic_conductivity": 10,
    },
}


# Irrigation method efficiencies
IRRIGATION_EFFICIENCY = {
    IrrigationMethod.DRIP: 0.90,
    IrrigationMethod.SPRINKLER: 0.75,
    IrrigationMethod.SURFACE: 0.60,
    IrrigationMethod.FLOOD: 0.50,
    IrrigationMethod.FURROW: 0.55,
}


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════════


class WeatherInput(BaseModel):
    """Weather data input for ET0 calculation"""

    temperature_max: float = Field(..., description="Maximum temperature (°C)")
    temperature_min: float = Field(..., description="Minimum temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    wind_speed: float = Field(..., ge=0, description="Wind speed at 2m height (m/s)")
    solar_radiation: Optional[float] = Field(
        None, description="Solar radiation (MJ/m²/day)"
    )
    sunshine_hours: Optional[float] = Field(
        None, ge=0, le=24, description="Sunshine hours"
    )
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (degrees)")
    altitude: float = Field(0, description="Altitude above sea level (m)")
    calculation_date: date = Field(
        default_factory=lambda: date.today(), description="Date for calculation"
    )


class ET0Response(BaseModel):
    """Reference evapotranspiration response"""

    et0: float = Field(..., description="Reference ET (mm/day)")
    et0_ar: str
    method: str
    weather_summary: dict
    calculation_date: date


class CropWaterRequirement(BaseModel):
    """Crop water requirement calculation input"""

    crop_type: str
    growth_stage: GrowthStage
    planting_date: Optional[date] = None
    days_after_planting: Optional[int] = None
    field_area_hectares: float = Field(1.0, gt=0)


class CropETcResponse(BaseModel):
    """Crop evapotranspiration response"""

    crop_type: str
    crop_name_ar: str
    growth_stage: str
    kc: float = Field(..., description="Crop coefficient")
    et0: float = Field(..., description="Reference ET (mm/day)")
    etc: float = Field(..., description="Crop ET (mm/day)")
    daily_water_need_liters: float
    daily_water_need_m3: float
    weekly_water_need_m3: float
    critical_period: bool
    notes: str
    notes_ar: str


class SoilMoistureInput(BaseModel):
    """Input for virtual soil moisture calculation"""

    soil_type: SoilType
    root_depth: float = Field(0.6, gt=0, le=3.0, description="Root depth (m)")
    last_irrigation_date: date
    last_irrigation_amount: float = Field(..., description="Irrigation amount (mm)")
    rainfall_since: float = Field(
        0, ge=0, description="Rainfall since last irrigation (mm)"
    )
    daily_etc: float = Field(..., description="Daily crop ET (mm/day)")


class VirtualSoilMoistureResponse(BaseModel):
    """Virtual soil moisture estimation response"""

    calculation_id: str
    estimated_moisture: float = Field(
        ..., description="Estimated soil moisture (m³/m³)"
    )
    moisture_percentage: float = Field(..., description="Available water depletion (%)")
    days_since_irrigation: int
    total_et_loss: float = Field(..., description="Total ET loss since irrigation (mm)")
    available_water: float = Field(..., description="Remaining available water (mm)")
    total_available_water: float = Field(
        ..., description="Total available water capacity (mm)"
    )
    status: str
    status_ar: str
    urgency: UrgencyLevel


class IrrigationRecommendationInput(BaseModel):
    """Input for irrigation recommendation"""

    crop_type: str
    growth_stage: GrowthStage
    soil_type: SoilType
    irrigation_method: IrrigationMethod
    field_area_hectares: float = Field(1.0, gt=0)
    last_irrigation_date: Optional[date] = None
    last_irrigation_amount: Optional[float] = None
    current_soil_moisture: Optional[float] = Field(
        None, description="Current moisture if known (m³/m³)"
    )
    weather: WeatherInput


class IrrigationRecommendation(BaseModel):
    """Complete irrigation recommendation response"""

    recommendation_id: str
    timestamp: datetime

    # Field info
    crop_type: str
    crop_name_ar: str
    growth_stage: str
    field_area_hectares: float

    # Calculations
    et0: float
    kc: float
    etc: float

    # Soil status
    soil_type: str
    soil_type_ar: str
    estimated_moisture: float
    moisture_depletion_percent: float

    # Recommendation
    irrigation_needed: bool
    urgency: UrgencyLevel
    urgency_ar: str
    recommended_amount_mm: float
    recommended_amount_liters: float
    recommended_amount_m3: float
    gross_irrigation_mm: float  # Accounting for efficiency

    # Timing
    optimal_time: str
    optimal_time_ar: str
    next_irrigation_days: int

    # Detailed advice
    advice: str
    advice_ar: str
    warnings: list[str]
    warnings_ar: list[str]


class WaterBalanceInput(BaseModel):
    """Input for water balance tracking"""

    field_id: str
    crop_type: str
    soil_type: SoilType
    start_date: date
    end_date: date
    irrigations: list[dict]  # [{"date": "2024-01-01", "amount_mm": 25}, ...]
    rainfall_data: list[dict]  # [{"date": "2024-01-01", "amount_mm": 10}, ...]
    weather_data: list[dict]  # Daily weather for ET calculation


class WaterBalanceResponse(BaseModel):
    """Water balance tracking response"""

    field_id: str
    period_start: date
    period_end: date

    # Summary
    total_et: float
    total_irrigation: float
    total_rainfall: float
    effective_rainfall: float
    net_balance: float

    # Daily breakdown
    daily_balance: list[dict]

    # Efficiency metrics
    irrigation_efficiency: float
    water_productivity: float

    # Recommendations
    cumulative_deficit: float
    recommended_adjustment: str
    recommended_adjustment_ar: str


# ═══════════════════════════════════════════════════════════════════════════════
# Calculation Functions
# دوال الحساب
# ═══════════════════════════════════════════════════════════════════════════════


def calculate_et0_penman_monteith(weather: WeatherInput) -> float:
    """
    Calculate reference evapotranspiration using FAO-56 Penman-Monteith equation.
    حساب التبخر-نتح المرجعي باستخدام معادلة بنمان-مونتيث FAO-56

    ET0 = [0.408 Δ(Rn-G) + γ(900/(T+273))u2(es-ea)] / [Δ + γ(1+0.34u2)]
    """
    # Temperature calculations
    T_max = weather.temperature_max
    T_min = weather.temperature_min
    T_mean = (T_max + T_min) / 2

    # Saturation vapor pressure (kPa)
    e_T_max = 0.6108 * math.exp((17.27 * T_max) / (T_max + 237.3))
    e_T_min = 0.6108 * math.exp((17.27 * T_min) / (T_min + 237.3))
    es = (e_T_max + e_T_min) / 2  # Mean saturation vapor pressure

    # Actual vapor pressure from humidity
    ea = (weather.humidity / 100) * es

    # Vapor pressure deficit
    vpd = es - ea

    # Slope of saturation vapor pressure curve (kPa/°C)
    delta = (4098 * (0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3)))) / (
        (T_mean + 237.3) ** 2
    )

    # Atmospheric pressure (kPa)
    P = 101.3 * ((293 - 0.0065 * weather.altitude) / 293) ** 5.26

    # Psychrometric constant (kPa/°C)
    gamma = 0.000665 * P

    # Day of year
    day_of_year = weather.calculation_date.timetuple().tm_yday

    # Solar calculations
    lat_rad = math.radians(weather.latitude)

    # Solar declination
    solar_dec = 0.409 * math.sin(2 * math.pi * day_of_year / 365 - 1.39)

    # Sunset hour angle
    cos_ws = -math.tan(lat_rad) * math.tan(solar_dec)
    cos_ws = max(-1, min(1, cos_ws))  # Clamp to valid range
    ws = math.acos(cos_ws)

    # Extraterrestrial radiation (MJ/m²/day)
    dr = 1 + 0.033 * math.cos(2 * math.pi * day_of_year / 365)
    Gsc = 0.0820  # Solar constant
    Ra = (
        (24 * 60 / math.pi)
        * Gsc
        * dr
        * (
            ws * math.sin(lat_rad) * math.sin(solar_dec)
            + math.cos(lat_rad) * math.cos(solar_dec) * math.sin(ws)
        )
    )

    # Solar radiation
    if weather.solar_radiation is not None:
        Rs = weather.solar_radiation
    elif weather.sunshine_hours is not None:
        # Angstrom formula
        N = 24 * ws / math.pi  # Daylight hours
        n = weather.sunshine_hours
        Rs = (0.25 + 0.50 * n / N) * Ra
    else:
        # Estimate from temperature range (Hargreaves)
        kRs = 0.16  # Interior location
        Rs = kRs * math.sqrt(T_max - T_min) * Ra

    # Clear-sky radiation
    Rso = (0.75 + 2e-5 * weather.altitude) * Ra

    # Net shortwave radiation
    albedo = 0.23
    Rns = (1 - albedo) * Rs

    # Net longwave radiation
    sigma = 4.903e-9  # Stefan-Boltzmann constant
    Rs_Rso = min(Rs / Rso, 1.0) if Rso > 0 else 0.5
    Rnl = (
        sigma
        * ((T_max + 273.16) ** 4 + (T_min + 273.16) ** 4)
        / 2
        * (0.34 - 0.14 * math.sqrt(ea))
        * (1.35 * Rs_Rso - 0.35)
    )

    # Net radiation
    Rn = Rns - Rnl

    # Soil heat flux (assumed 0 for daily calculation)
    G = 0

    # Wind speed (convert if needed, assume at 2m)
    u2 = weather.wind_speed

    # FAO-56 Penman-Monteith equation
    numerator = 0.408 * delta * (Rn - G) + gamma * (900 / (T_mean + 273)) * u2 * vpd
    denominator = delta + gamma * (1 + 0.34 * u2)

    ET0 = numerator / denominator

    return max(0, ET0)  # ET0 cannot be negative


def get_crop_kc(
    crop_type: str, growth_stage: GrowthStage, days_in_stage: int = None
) -> float:
    """Get crop coefficient (Kc) for given crop and growth stage"""
    crop = CROP_COEFFICIENTS.get(crop_type)
    if not crop:
        return 1.0  # Default Kc

    if growth_stage == GrowthStage.INITIAL:
        return crop["kc_initial"]
    elif growth_stage == GrowthStage.DEVELOPMENT:
        # Linear interpolation during development
        kc_init = crop["kc_initial"]
        kc_mid = crop["kc_mid"]
        stage_length = crop["stages_days"]["development"]
        if days_in_stage and stage_length > 0:
            progress = min(days_in_stage / stage_length, 1.0)
            return kc_init + (kc_mid - kc_init) * progress
        return (kc_init + kc_mid) / 2
    elif growth_stage == GrowthStage.MID_SEASON:
        return crop["kc_mid"]
    elif growth_stage == GrowthStage.LATE_SEASON:
        # Linear decline
        kc_mid = crop["kc_mid"]
        kc_end = crop["kc_end"]
        stage_length = crop["stages_days"]["late_season"]
        if days_in_stage and stage_length > 0:
            progress = min(days_in_stage / stage_length, 1.0)
            return kc_mid - (kc_mid - kc_end) * progress
        return (kc_mid + kc_end) / 2

    return 1.0


def calculate_available_water(
    soil_type: SoilType, root_depth: float
) -> tuple[float, float, float]:
    """
    Calculate available water capacity.
    Returns: (total_available_water_mm, field_capacity_mm, wilting_point_mm)
    """
    soil = SOIL_PROPERTIES[soil_type]
    fc = soil["field_capacity"]
    wp = soil["wilting_point"]

    # Available water in root zone (mm)
    taw = (fc - wp) * root_depth * 1000  # Convert m to mm
    fc_mm = fc * root_depth * 1000
    wp_mm = wp * root_depth * 1000

    return taw, fc_mm, wp_mm


def estimate_soil_moisture(
    soil_type: SoilType,
    root_depth: float,
    last_irrigation_date: date,
    last_irrigation_amount: float,
    rainfall_since: float,
    daily_etc: float,
) -> dict:
    """
    Estimate current soil moisture using water balance method.
    تقدير رطوبة التربة الحالية باستخدام ميزان الماء
    """
    taw, fc_mm, wp_mm = calculate_available_water(soil_type, root_depth)
    soil = SOIL_PROPERTIES[soil_type]

    # Days since irrigation
    today = date.today()
    days_elapsed = (today - last_irrigation_date).days

    # Effective rainfall (assume 80% efficiency)
    effective_rainfall = rainfall_since * 0.80

    # Total water input
    water_input = min(last_irrigation_amount + effective_rainfall, taw)

    # Total ET loss
    total_et_loss = daily_etc * days_elapsed

    # Remaining available water
    remaining_aw = max(0, water_input - total_et_loss)

    # Depletion percentage
    depletion_percent = ((taw - remaining_aw) / taw * 100) if taw > 0 else 100

    # Estimate moisture content (m³/m³)
    moisture_content = soil["wilting_point"] + (remaining_aw / (root_depth * 1000))

    # Status determination
    if depletion_percent < 30:
        status = "optimal"
        status_ar = "مثالي"
        urgency = UrgencyLevel.NONE
    elif depletion_percent < 50:
        status = "adequate"
        status_ar = "كافي"
        urgency = UrgencyLevel.LOW
    elif depletion_percent < 70:
        status = "moderate_stress"
        status_ar = "إجهاد متوسط"
        urgency = UrgencyLevel.MEDIUM
    elif depletion_percent < 85:
        status = "high_stress"
        status_ar = "إجهاد عالي"
        urgency = UrgencyLevel.HIGH
    else:
        status = "critical"
        status_ar = "حرج"
        urgency = UrgencyLevel.CRITICAL

    return {
        "moisture_content": moisture_content,
        "depletion_percent": depletion_percent,
        "remaining_aw": remaining_aw,
        "total_aw": taw,
        "total_et_loss": total_et_loss,
        "days_elapsed": days_elapsed,
        "status": status,
        "status_ar": status_ar,
        "urgency": urgency,
    }


def calculate_irrigation_recommendation(
    crop_type: str,
    growth_stage: GrowthStage,
    soil_type: SoilType,
    irrigation_method: IrrigationMethod,
    field_area_hectares: float,
    et0: float,
    moisture_status: dict,
) -> dict:
    """
    Generate irrigation recommendation.
    إنشاء توصية الري
    """
    crop = CROP_COEFFICIENTS.get(crop_type, CROP_COEFFICIENTS["wheat"])
    soil = SOIL_PROPERTIES[soil_type]
    efficiency = IRRIGATION_EFFICIENCY[irrigation_method]

    kc = get_crop_kc(crop_type, growth_stage)
    etc = et0 * kc

    # Management Allowed Depletion (MAD) - typically 50% of TAW
    p = crop.get("depletion_fraction", 0.5)
    mad_percent = p * 100

    depletion = moisture_status["depletion_percent"]
    taw = moisture_status["total_aw"]
    remaining_aw = moisture_status["remaining_aw"]

    # Check if irrigation is needed
    irrigation_needed = depletion > (mad_percent - 10)  # Start 10% before MAD

    warnings = []
    warnings_ar = []

    # Calculate required irrigation
    if irrigation_needed:
        # Refill to field capacity
        deficit = taw - remaining_aw
        recommended_mm = deficit * 1.1  # 10% extra for distribution uniformity

        # Gross irrigation (accounting for efficiency)
        gross_mm = recommended_mm / efficiency

        # Convert to volume
        recommended_liters = (
            recommended_mm * field_area_hectares * 10000
        )  # 1 mm = 10 m³/ha
        recommended_m3 = recommended_liters / 1000
    else:
        recommended_mm = 0
        gross_mm = 0
        recommended_liters = 0
        recommended_m3 = 0

    # Calculate days until next irrigation needed
    if etc > 0:
        allowable_depletion_mm = taw * p
        current_depletion_mm = taw - remaining_aw
        remaining_allowable = allowable_depletion_mm - current_depletion_mm
        days_until_needed = max(0, int(remaining_allowable / etc))
    else:
        days_until_needed = 7  # Default

    # Optimal timing advice
    if moisture_status["urgency"] == UrgencyLevel.CRITICAL:
        optimal_time = "Immediately - early morning preferred"
        optimal_time_ar = "فوراً - يفضل الصباح الباكر"
    elif moisture_status["urgency"] == UrgencyLevel.HIGH:
        optimal_time = "Today, early morning or late evening"
        optimal_time_ar = "اليوم، الصباح الباكر أو المساء"
    else:
        optimal_time = "Early morning (6-8 AM) or late evening (6-8 PM)"
        optimal_time_ar = "الصباح الباكر (6-8 صباحاً) أو المساء (6-8 مساءً)"

    # Generate advice
    if not irrigation_needed:
        advice = f"No irrigation needed. Soil moisture is adequate. Next irrigation expected in {days_until_needed} days."
        advice_ar = f"لا حاجة للري حالياً. رطوبة التربة كافية. الري القادم متوقع خلال {days_until_needed} أيام."
    else:
        advice = f"Irrigation recommended. Apply {gross_mm:.1f} mm ({recommended_m3:.1f} m³) using {irrigation_method.value} method."
        advice_ar = f"يُنصح بالري. أضف {gross_mm:.1f} مم ({recommended_m3:.1f} متر مكعب) باستخدام طريقة {irrigation_method.value}."

    # Add warnings
    if growth_stage in [GrowthStage.MID_SEASON] and depletion > 60:
        warnings.append("Critical growth stage - avoid water stress")
        warnings_ar.append("مرحلة نمو حرجة - تجنب إجهاد الماء")

    if soil_type in [SoilType.SANDY, SoilType.SANDY_LOAM] and gross_mm > 30:
        warnings.append(
            "Sandy soil - consider splitting irrigation into smaller applications"
        )
        warnings_ar.append("تربة رملية - يُنصح بتقسيم الري إلى دفعات أصغر")

    # Urgency in Arabic
    urgency_ar_map = {
        UrgencyLevel.NONE: "لا حاجة",
        UrgencyLevel.LOW: "منخفض",
        UrgencyLevel.MEDIUM: "متوسط",
        UrgencyLevel.HIGH: "عالي",
        UrgencyLevel.CRITICAL: "حرج",
    }

    return {
        "irrigation_needed": irrigation_needed,
        "urgency": moisture_status["urgency"],
        "urgency_ar": urgency_ar_map[moisture_status["urgency"]],
        "recommended_amount_mm": recommended_mm,
        "recommended_amount_liters": recommended_liters,
        "recommended_amount_m3": recommended_m3,
        "gross_irrigation_mm": gross_mm,
        "optimal_time": optimal_time,
        "optimal_time_ar": optimal_time_ar,
        "next_irrigation_days": days_until_needed,
        "advice": advice,
        "advice_ar": advice_ar,
        "warnings": warnings,
        "warnings_ar": warnings_ar,
        "kc": kc,
        "etc": etc,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print(f"🌱 {SERVICE_NAME} v{SERVICE_VERSION} starting on port {SERVICE_PORT}")
    print(f"📊 Loaded {len(CROP_COEFFICIENTS)} crop types with Kc values")
    print(f"🌍 Loaded {len(SOIL_PROPERTIES)} soil types")
    yield
    print(f"👋 {SERVICE_NAME} shutting down")


app = FastAPI(
    title="Sahool Virtual Sensors Engine",
    description="""
    محرك المستشعرات الافتراضية - سهول

    Software-based sensor calculations for smart irrigation management.
    Provides evapotranspiration calculations, soil moisture estimation,
    and irrigation recommendations without physical sensors.

    Based on FAO-56 Penman-Monteith methodology.
    """,
    version=SERVICE_VERSION,
    lifespan=lifespan,
)

# CORS middleware - secure origins from environment
CORS_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:8080",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/v1/info")
async def service_info():
    """Get service information"""
    return {
        "service": SERVICE_NAME,
        "service_ar": "محرك المستشعرات الافتراضية",
        "version": SERVICE_VERSION,
        "description": "Software-based irrigation sensors using weather and crop data",
        "description_ar": "مستشعرات ري برمجية باستخدام بيانات الطقس والمحاصيل",
        "capabilities": [
            "ET0 calculation (Penman-Monteith)",
            "Crop water requirements (ETc)",
            "Virtual soil moisture estimation",
            "Irrigation scheduling",
            "Water balance tracking",
        ],
        "supported_crops": len(CROP_COEFFICIENTS),
        "supported_soils": len(SOIL_PROPERTIES),
    }


# ─────────────────────────────────────────────────────────────────────────────
# ET0 Calculation Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@app.post("/v1/et0/calculate", response_model=ET0Response)
async def calculate_et0(weather: WeatherInput):
    """
    Calculate reference evapotranspiration (ET0) using Penman-Monteith.
    حساب التبخر-نتح المرجعي باستخدام بنمان-مونتيث
    """
    et0 = calculate_et0_penman_monteith(weather)

    return ET0Response(
        et0=round(et0, 2),
        et0_ar=f"{et0:.2f} مم/يوم",
        method="FAO-56 Penman-Monteith",
        weather_summary={
            "temp_max": weather.temperature_max,
            "temp_min": weather.temperature_min,
            "temp_mean": (weather.temperature_max + weather.temperature_min) / 2,
            "humidity": weather.humidity,
            "wind_speed": weather.wind_speed,
            "latitude": weather.latitude,
            "altitude": weather.altitude,
        },
        calculation_date=weather.calculation_date,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Crop Water Requirements
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/v1/crops")
async def get_supported_crops():
    """Get list of supported crops with Kc values"""
    crops = []
    for crop_id, crop_data in CROP_COEFFICIENTS.items():
        crops.append(
            {
                "crop_id": crop_id,
                "name": crop_id.replace("_", " ").title(),
                "name_ar": crop_data["name_ar"],
                "kc_initial": crop_data["kc_initial"],
                "kc_mid": crop_data["kc_mid"],
                "kc_end": crop_data["kc_end"],
                "root_depth_max": crop_data["root_depth_max"],
                "critical_periods": crop_data.get("critical_periods", []),
            }
        )
    return {"crops": crops, "total": len(crops)}


@app.get("/v1/crops/{crop_type}/kc")
async def get_crop_kc_values(
    crop_type: str,
    growth_stage: Optional[GrowthStage] = None,
    days_in_stage: Optional[int] = None,
):
    """Get Kc values for a specific crop"""
    if crop_type not in CROP_COEFFICIENTS:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_type}' not found")

    crop = CROP_COEFFICIENTS[crop_type]

    if growth_stage:
        kc = get_crop_kc(crop_type, growth_stage, days_in_stage)
        return {
            "crop_type": crop_type,
            "crop_name_ar": crop["name_ar"],
            "growth_stage": growth_stage.value,
            "kc": round(kc, 2),
            "days_in_stage": days_in_stage,
        }

    return {
        "crop_type": crop_type,
        "crop_name_ar": crop["name_ar"],
        "kc_initial": crop["kc_initial"],
        "kc_mid": crop["kc_mid"],
        "kc_end": crop["kc_end"],
        "stages_days": crop["stages_days"],
        "root_depth_max": crop["root_depth_max"],
        "depletion_fraction": crop["depletion_fraction"],
    }


@app.post("/v1/etc/calculate", response_model=CropETcResponse)
async def calculate_crop_etc(
    weather: WeatherInput,
    crop_type: str = Query(..., description="Crop type"),
    growth_stage: GrowthStage = Query(..., description="Current growth stage"),
    field_area_hectares: float = Query(1.0, gt=0, description="Field area in hectares"),
    days_in_stage: Optional[int] = Query(None, description="Days in current stage"),
):
    """
    Calculate crop evapotranspiration (ETc = ET0 × Kc).
    حساب التبخر-نتح للمحصول
    """
    if crop_type not in CROP_COEFFICIENTS:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_type}' not found")

    crop = CROP_COEFFICIENTS[crop_type]
    et0 = calculate_et0_penman_monteith(weather)
    kc = get_crop_kc(crop_type, growth_stage, days_in_stage)
    etc = et0 * kc

    # Water needs
    daily_liters = etc * field_area_hectares * 10000  # 1 mm = 10 m³/ha = 10000 L/ha
    daily_m3 = daily_liters / 1000
    weekly_m3 = daily_m3 * 7

    # Check critical period
    critical = growth_stage == GrowthStage.MID_SEASON and "critical_periods" in crop

    notes = f"Crop is in {growth_stage.value} stage with Kc={kc:.2f}"
    notes_ar = f"المحصول في مرحلة {growth_stage.value} مع معامل Kc={kc:.2f}"

    if critical:
        notes += ". Critical growth period - maintain optimal irrigation."
        notes_ar += ". فترة نمو حرجة - حافظ على الري المثالي."

    return CropETcResponse(
        crop_type=crop_type,
        crop_name_ar=crop["name_ar"],
        growth_stage=growth_stage.value,
        kc=round(kc, 2),
        et0=round(et0, 2),
        etc=round(etc, 2),
        daily_water_need_liters=round(daily_liters, 0),
        daily_water_need_m3=round(daily_m3, 2),
        weekly_water_need_m3=round(weekly_m3, 2),
        critical_period=critical,
        notes=notes,
        notes_ar=notes_ar,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Soil Moisture Estimation
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/v1/soils")
async def get_soil_types():
    """Get list of supported soil types with properties"""
    soils = []
    for soil_type, props in SOIL_PROPERTIES.items():
        soils.append(
            {
                "soil_type": soil_type.value,
                "name_ar": props["name_ar"],
                "field_capacity": props["field_capacity"],
                "wilting_point": props["wilting_point"],
                "available_water_capacity": props["field_capacity"]
                - props["wilting_point"],
                "infiltration_rate_mm_hr": props["infiltration_rate"],
            }
        )
    return {"soils": soils, "total": len(soils)}


@app.post("/v1/soil-moisture/estimate", response_model=VirtualSoilMoistureResponse)
async def estimate_virtual_soil_moisture(input_data: SoilMoistureInput):
    """
    Estimate soil moisture using water balance method.
    تقدير رطوبة التربة باستخدام ميزان الماء
    """
    result = estimate_soil_moisture(
        soil_type=input_data.soil_type,
        root_depth=input_data.root_depth,
        last_irrigation_date=input_data.last_irrigation_date,
        last_irrigation_amount=input_data.last_irrigation_amount,
        rainfall_since=input_data.rainfall_since,
        daily_etc=input_data.daily_etc,
    )

    return VirtualSoilMoistureResponse(
        calculation_id=str(uuid.uuid4()),
        estimated_moisture=round(result["moisture_content"], 3),
        moisture_percentage=round(100 - result["depletion_percent"], 1),
        days_since_irrigation=result["days_elapsed"],
        total_et_loss=round(result["total_et_loss"], 2),
        available_water=round(result["remaining_aw"], 2),
        total_available_water=round(result["total_aw"], 2),
        status=result["status"],
        status_ar=result["status_ar"],
        urgency=result["urgency"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Irrigation Recommendation
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/v1/irrigation-methods")
async def get_irrigation_methods():
    """Get irrigation methods with efficiencies"""
    methods = []
    for method, efficiency in IRRIGATION_EFFICIENCY.items():
        methods.append(
            {
                "method": method.value,
                "efficiency": efficiency,
                "efficiency_percent": f"{efficiency * 100:.0f}%",
            }
        )
    return {"methods": methods}


@app.post("/v1/irrigation/recommend", response_model=IrrigationRecommendation)
async def get_irrigation_recommendation(input_data: IrrigationRecommendationInput):
    """
    Get complete irrigation recommendation.
    الحصول على توصية ري شاملة
    """
    if input_data.crop_type not in CROP_COEFFICIENTS:
        raise HTTPException(
            status_code=404, detail=f"Crop '{input_data.crop_type}' not found"
        )

    crop = CROP_COEFFICIENTS[input_data.crop_type]
    soil = SOIL_PROPERTIES[input_data.soil_type]

    # Calculate ET0
    et0 = calculate_et0_penman_monteith(input_data.weather)
    kc = get_crop_kc(input_data.crop_type, input_data.growth_stage)
    etc = et0 * kc

    # Get root depth based on growth stage
    max_root = crop["root_depth_max"]
    if input_data.growth_stage == GrowthStage.INITIAL:
        root_depth = max_root * 0.3
    elif input_data.growth_stage == GrowthStage.DEVELOPMENT:
        root_depth = max_root * 0.6
    else:
        root_depth = max_root

    # Estimate soil moisture
    last_irr_date = input_data.last_irrigation_date or (
        date.today() - timedelta(days=7)
    )
    last_irr_amount = input_data.last_irrigation_amount or 30.0

    moisture_status = estimate_soil_moisture(
        soil_type=input_data.soil_type,
        root_depth=root_depth,
        last_irrigation_date=last_irr_date,
        last_irrigation_amount=last_irr_amount,
        rainfall_since=0,  # Could be integrated with weather service
        daily_etc=etc,
    )

    # Get recommendation
    recommendation = calculate_irrigation_recommendation(
        crop_type=input_data.crop_type,
        growth_stage=input_data.growth_stage,
        soil_type=input_data.soil_type,
        irrigation_method=input_data.irrigation_method,
        field_area_hectares=input_data.field_area_hectares,
        et0=et0,
        moisture_status=moisture_status,
    )

    return IrrigationRecommendation(
        recommendation_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        crop_type=input_data.crop_type,
        crop_name_ar=crop["name_ar"],
        growth_stage=input_data.growth_stage.value,
        field_area_hectares=input_data.field_area_hectares,
        et0=round(et0, 2),
        kc=round(kc, 2),
        etc=round(etc, 2),
        soil_type=input_data.soil_type.value,
        soil_type_ar=soil["name_ar"],
        estimated_moisture=round(moisture_status["moisture_content"], 3),
        moisture_depletion_percent=round(moisture_status["depletion_percent"], 1),
        irrigation_needed=recommendation["irrigation_needed"],
        urgency=recommendation["urgency"],
        urgency_ar=recommendation["urgency_ar"],
        recommended_amount_mm=round(recommendation["recommended_amount_mm"], 1),
        recommended_amount_liters=round(recommendation["recommended_amount_liters"], 0),
        recommended_amount_m3=round(recommendation["recommended_amount_m3"], 2),
        gross_irrigation_mm=round(recommendation["gross_irrigation_mm"], 1),
        optimal_time=recommendation["optimal_time"],
        optimal_time_ar=recommendation["optimal_time_ar"],
        next_irrigation_days=recommendation["next_irrigation_days"],
        advice=recommendation["advice"],
        advice_ar=recommendation["advice_ar"],
        warnings=recommendation["warnings"],
        warnings_ar=recommendation["warnings_ar"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Quick Irrigation Check (Simplified)
# ─────────────────────────────────────────────────────────────────────────────


@app.get("/v1/irrigation/quick-check")
async def quick_irrigation_check(
    crop_type: str = Query(..., description="Crop type"),
    growth_stage: GrowthStage = Query(..., description="Growth stage"),
    soil_type: SoilType = Query(SoilType.LOAM, description="Soil type"),
    days_since_irrigation: int = Query(
        ..., ge=0, description="Days since last irrigation"
    ),
    temperature: float = Query(..., description="Average temperature (°C)"),
    humidity: float = Query(50, ge=0, le=100, description="Relative humidity (%)"),
):
    """
    Quick irrigation check without full weather data.
    فحص سريع للري بدون بيانات الطقس الكاملة
    """
    if crop_type not in CROP_COEFFICIENTS:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_type}' not found")

    crop = CROP_COEFFICIENTS[crop_type]

    # Simplified ET0 estimation (Hargreaves-like)
    # More accurate would require full weather data
    base_et0 = 0.0023 * (temperature + 17.8) * 15 * 0.5  # Simplified
    et0 = max(2.0, min(base_et0, 10.0))  # Clamp to reasonable range

    kc = get_crop_kc(crop_type, growth_stage)
    etc = et0 * kc

    # Quick moisture estimate
    total_et_loss = etc * days_since_irrigation

    # Typical irrigation amount assumption
    typical_irrigation = 30  # mm
    remaining = typical_irrigation - total_et_loss
    depletion = (total_et_loss / typical_irrigation) * 100

    # Quick assessment
    if depletion < 40:
        status = "good"
        status_ar = "جيد"
        needs_irrigation = False
    elif depletion < 60:
        status = "monitor"
        status_ar = "راقب"
        needs_irrigation = False
    elif depletion < 80:
        status = "irrigate_soon"
        status_ar = "ري قريباً"
        needs_irrigation = True
    else:
        status = "irrigate_now"
        status_ar = "ري الآن"
        needs_irrigation = True

    return {
        "crop_type": crop_type,
        "crop_name_ar": crop["name_ar"],
        "growth_stage": growth_stage.value,
        "days_since_irrigation": days_since_irrigation,
        "estimated_et0": round(et0, 2),
        "kc": round(kc, 2),
        "estimated_etc": round(etc, 2),
        "estimated_water_loss_mm": round(total_et_loss, 1),
        "estimated_depletion_percent": round(min(depletion, 100), 0),
        "status": status,
        "status_ar": status_ar,
        "needs_irrigation": needs_irrigation,
        "recommendation": f"{'Irrigate now' if needs_irrigation else 'No irrigation needed'}",
        "recommendation_ar": f"{'قم بالري الآن' if needs_irrigation else 'لا حاجة للري'}",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Field-First: ActionTemplate Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


class VirtualSensorActionRequest(BaseModel):
    """Request for virtual sensor analysis with ActionTemplate output"""

    field_id: str = Field(..., description="معرف الحقل")
    farmer_id: Optional[str] = Field(None, description="معرف المزارع")
    tenant_id: Optional[str] = Field(None, description="معرف المستأجر")
    crop_type: str = Field(..., description="نوع المحصول")
    growth_stage: GrowthStage = Field(..., description="مرحلة النمو")
    soil_type: SoilType = Field(SoilType.LOAM, description="نوع التربة")
    irrigation_method: IrrigationMethod = Field(
        IrrigationMethod.DRIP, description="طريقة الري"
    )
    field_area_hectares: float = Field(1.0, gt=0, description="مساحة الحقل بالهكتار")
    last_irrigation_date: Optional[date] = Field(None, description="تاريخ آخر ري")
    last_irrigation_amount: Optional[float] = Field(
        None, description="كمية آخر ري بالمم"
    )
    weather: WeatherInput = Field(..., description="بيانات الطقس")
    publish_event: bool = Field(default=True, description="نشر الحدث عبر NATS")


def _create_virtual_sensor_action(
    recommendation: IrrigationRecommendation,
    field_id: str,
    farmer_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an ActionTemplate from virtual sensor analysis"""

    # Map urgency
    urgency_map = {
        UrgencyLevel.NONE: "low",
        UrgencyLevel.LOW: "low",
        UrgencyLevel.MEDIUM: "medium",
        UrgencyLevel.HIGH: "high",
        UrgencyLevel.CRITICAL: "critical",
    }
    urgency = urgency_map.get(recommendation.urgency, "medium")

    if recommendation.irrigation_needed:
        action_type = "irrigation"
        title_ar = f"ري تقديري - {recommendation.urgency_ar}"
        title_en = f"Virtual Irrigation - {recommendation.urgency.value}"
    else:
        action_type = "monitoring"
        title_ar = "مراقبة - لا حاجة للري"
        title_en = "Monitoring - No Irrigation Needed"

    return {
        "action_id": str(uuid.uuid4()),
        "action_type": action_type,
        "title_ar": title_ar,
        "title_en": title_en,
        "description_ar": recommendation.advice_ar,
        "description_en": recommendation.advice,
        "summary_ar": f"رطوبة التربة: {100 - recommendation.moisture_depletion_percent:.0f}% | ET: {recommendation.etc:.1f} مم/يوم",
        "source_service": "virtual-sensors",
        "source_analysis_type": "virtual_soil_moisture",
        "confidence": 0.75,  # Virtual sensor confidence lower than IoT
        "urgency": urgency,
        "field_id": field_id,
        "farmer_id": farmer_id,
        "tenant_id": tenant_id,
        "offline_executable": True,
        "fallback_instructions_ar": "في حال عدم توفر البيانات، قم بفحص رطوبة التربة يدوياً بعمق 15 سم",
        "fallback_instructions_en": "If data unavailable, manually check soil moisture at 15cm depth",
        "estimated_duration_minutes": (
            int(recommendation.gross_irrigation_mm * 2)
            if recommendation.irrigation_needed
            else 30
        ),
        "data": {
            "et0": recommendation.et0,
            "kc": recommendation.kc,
            "etc": recommendation.etc,
            "soil_type": recommendation.soil_type,
            "moisture_depletion_percent": recommendation.moisture_depletion_percent,
            "recommended_amount_mm": recommendation.recommended_amount_mm,
            "recommended_amount_m3": recommendation.recommended_amount_m3,
            "next_irrigation_days": recommendation.next_irrigation_days,
            "is_virtual": True,  # Badge: تقدير افتراضي
        },
        "badge": {
            "type": "virtual_estimate",
            "label_ar": "تقدير افتراضي",
            "label_en": "Virtual Estimate",
            "color": "#6366F1",  # Indigo for virtual
        },
        "created_at": datetime.utcnow().isoformat(),
    }


@app.post("/v1/irrigation/recommend-with-action")
async def get_irrigation_recommendation_with_action(
    request: VirtualSensorActionRequest,
    background_tasks: BackgroundTasks,
):
    """
    الحصول على توصية ري مع ActionTemplate

    Field-First: ينتج قالب إجراء للتطبيق المحمول
    Badge: تقدير افتراضي (بدون حساس)
    """

    # Build weather input
    weather = request.weather

    # Build recommendation input
    rec_input = IrrigationRecommendationInput(
        crop_type=request.crop_type,
        growth_stage=request.growth_stage,
        soil_type=request.soil_type,
        irrigation_method=request.irrigation_method,
        field_area_hectares=request.field_area_hectares,
        last_irrigation_date=request.last_irrigation_date,
        last_irrigation_amount=request.last_irrigation_amount,
        weather=weather,
    )

    # Get recommendation
    recommendation = await get_irrigation_recommendation(rec_input)

    # Create ActionTemplate
    action_template = _create_virtual_sensor_action(
        recommendation=recommendation,
        field_id=request.field_id,
        farmer_id=request.farmer_id,
        tenant_id=request.tenant_id,
    )

    # Publish to NATS if irrigation is needed
    if (
        request.publish_event
        and _nats_available
        and publish_analysis_completed_sync
        and recommendation.irrigation_needed
    ):
        try:
            publish_analysis_completed_sync(
                event_type="virtual_sensor.irrigation_needed",
                source_service="virtual-sensors",
                field_id=request.field_id,
                data=action_template.get("data", {}),
                action_template=action_template,
                priority=action_template.get("urgency", "medium"),
                farmer_id=request.farmer_id,
                tenant_id=request.tenant_id,
            )
            logger.info(
                f"NATS: Published virtual sensor event for field {request.field_id}"
            )
        except Exception as e:
            logger.error(f"Failed to publish NATS event: {e}")

    # Task card for mobile
    task_card = {
        "id": action_template["action_id"],
        "type": action_template["action_type"],
        "title_ar": action_template["title_ar"],
        "title_en": action_template["title_en"],
        "urgency": {
            "level": action_template["urgency"],
            "label_ar": recommendation.urgency_ar,
            "color": {
                "low": "#22C55E",
                "medium": "#EAB308",
                "high": "#F97316",
                "critical": "#EF4444",
            }.get(action_template["urgency"], "#6B7280"),
        },
        "field_id": request.field_id,
        "confidence_percent": 75,
        "offline_ready": True,
        "badge": action_template["badge"],
        "irrigation_needed": recommendation.irrigation_needed,
        "water_m3": recommendation.recommended_amount_m3,
    }

    return {
        "recommendation": {
            "recommendation_id": recommendation.recommendation_id,
            "crop_type": recommendation.crop_type,
            "crop_name_ar": recommendation.crop_name_ar,
            "et0": recommendation.et0,
            "kc": recommendation.kc,
            "etc": recommendation.etc,
            "moisture_depletion_percent": recommendation.moisture_depletion_percent,
            "irrigation_needed": recommendation.irrigation_needed,
            "urgency": recommendation.urgency.value,
            "urgency_ar": recommendation.urgency_ar,
            "recommended_amount_mm": recommendation.recommended_amount_mm,
            "recommended_amount_m3": recommendation.recommended_amount_m3,
            "optimal_time_ar": recommendation.optimal_time_ar,
            "next_irrigation_days": recommendation.next_irrigation_days,
            "advice_ar": recommendation.advice_ar,
            "warnings_ar": recommendation.warnings_ar,
        },
        "action_template": action_template,
        "task_card": task_card,
        "is_virtual": True,
        "nats_published": request.publish_event
        and _nats_available
        and recommendation.irrigation_needed,
    }


@app.get("/v1/quick-check-with-action")
async def quick_check_with_action(
    field_id: str = Query(..., description="معرف الحقل"),
    farmer_id: Optional[str] = Query(None, description="معرف المزارع"),
    crop_type: str = Query(..., description="نوع المحصول"),
    growth_stage: GrowthStage = Query(..., description="مرحلة النمو"),
    soil_type: SoilType = Query(SoilType.LOAM, description="نوع التربة"),
    days_since_irrigation: int = Query(..., ge=0, description="أيام منذ آخر ري"),
    temperature: float = Query(..., description="درجة الحرارة"),
    humidity: float = Query(50, ge=0, le=100, description="الرطوبة النسبية"),
):
    """
    فحص سريع مع ActionTemplate

    للبيئات الريفية بدون IoT
    """
    # Get quick check result
    result = await quick_irrigation_check(
        crop_type=crop_type,
        growth_stage=growth_stage,
        soil_type=soil_type,
        days_since_irrigation=days_since_irrigation,
        temperature=temperature,
        humidity=humidity,
    )

    # Determine urgency
    status_urgency_map = {
        "good": "low",
        "monitor": "low",
        "irrigate_soon": "medium",
        "irrigate_now": "high",
    }
    urgency = status_urgency_map.get(result["status"], "medium")

    # Create simple action template
    action_template = {
        "action_id": str(uuid.uuid4()),
        "action_type": "irrigation" if result["needs_irrigation"] else "monitoring",
        "title_ar": result["recommendation_ar"],
        "title_en": result["recommendation"],
        "description_ar": f"رطوبة التربة المتبقية: {100 - result['estimated_depletion_percent']:.0f}%",
        "description_en": f"Remaining soil moisture: {100 - result['estimated_depletion_percent']:.0f}%",
        "source_service": "virtual-sensors",
        "confidence": 0.70,  # Quick check has lower confidence
        "urgency": urgency,
        "field_id": field_id,
        "offline_executable": True,
        "fallback_instructions_ar": "افحص رطوبة التربة يدوياً",
        "fallback_instructions_en": "Check soil moisture manually",
        "estimated_duration_minutes": 60 if result["needs_irrigation"] else 15,
        "badge": {
            "type": "virtual_quick",
            "label_ar": "فحص سريع",
            "label_en": "Quick Check",
            "color": "#8B5CF6",
        },
        "data": result,
    }

    return {
        "quick_check": result,
        "action_template": action_template,
        "is_virtual": True,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
