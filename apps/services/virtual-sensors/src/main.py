"""
Virtual Sensors Engine - Sahool Smart Irrigation v16.0
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

import logging
import math
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta, timezone
from enum import Enum, StrEnum
from typing import Any

import structlog
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, Field, field_validator

from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

logger = structlog.get_logger(__name__)

# NATS publisher (optional)
_nats_available = False
try:
    sys.path.insert(0, "/home/user/sahool-unified-v15-idp")
    from shared.libs.events.nats_publisher import publish_analysis_completed_sync

    _nats_available = True
except ImportError:
    logger.info("NATS publisher not available")
    publish_analysis_completed_sync = None

# Async NATS client for event publishing
_nats_client = None

try:
    import json as _json

    import nats as _nats_module
except ImportError:
    _nats_module = None


async def _init_nats():
    """Initialize async NATS connection for event publishing."""
    global _nats_client
    nats_url = os.getenv("NATS_URL", "nats://nats:4222")
    if _nats_module is None:
        logger.warning("nats-py not installed, async NATS publishing disabled")
        return
    try:
        _nats_client = await _nats_module.connect(nats_url)
        logger.info("nats_async_connected", url=nats_url)
    except Exception as e:
        logger.warning("nats_async_connection_failed", error=str(e))


async def _close_nats():
    """Close async NATS connection."""
    global _nats_client
    if _nats_client and not _nats_client.is_closed:
        await _nats_client.close()
        _nats_client = None


async def publish_event(subject: str, data: dict):
    """Publish event to NATS. Falls back to logging if NATS is unavailable."""
    if _nats_client and not _nats_client.is_closed:
        try:
            payload = _json.dumps(data, default=str).encode()
            await _nats_client.publish(subject, payload)
            logger.info("nats_event_published", subject=subject)
        except Exception as e:
            logger.warning("nats_publish_failed", subject=subject, error=str(e))
    else:
        logger.info("nats_event_local", subject=subject, data_keys=list(data.keys()))


# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "virtual-sensors"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = int(os.getenv("PORT", "8119"))

# ═══════════════════════════════════════════════════════════════════════════════
# Prometheus Metrics
# ═══════════════════════════════════════════════════════════════════════════════

PROM_REGISTRY = CollectorRegistry()

REQUEST_COUNT = Counter(
    "virtual_sensors_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=PROM_REGISTRY,
)

REQUEST_LATENCY = Histogram(
    "virtual_sensors_request_duration_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    registry=PROM_REGISTRY,
)

ET0_CALCULATIONS = Counter(
    "virtual_sensors_et0_calculations_total",
    "Total ET0 calculations performed",
    registry=PROM_REGISTRY,
)

IRRIGATION_RECOMMENDATIONS = Counter(
    "virtual_sensors_irrigation_recommendations_total",
    "Total irrigation recommendations generated",
    registry=PROM_REGISTRY,
)

SOIL_MOISTURE_ESTIMATES = Counter(
    "virtual_sensors_soil_moisture_estimates_total",
    "Total soil moisture estimations performed",
    registry=PROM_REGISTRY,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enums and Constants
# ═══════════════════════════════════════════════════════════════════════════════


class GrowthStage(StrEnum):
    """Crop growth stages for Kc determination"""

    INITIAL = "initial"  # المرحلة الأولية
    DEVELOPMENT = "development"  # مرحلة النمو
    MID_SEASON = "mid_season"  # منتصف الموسم
    LATE_SEASON = "late_season"  # نهاية الموسم


class SoilType(StrEnum):
    """Soil types common in Yemen"""

    SANDY = "sandy"  # رملي
    SANDY_LOAM = "sandy_loam"  # رملي طميي
    LOAM = "loam"  # طميي
    CLAY_LOAM = "clay_loam"  # طيني طميي
    CLAY = "clay"  # طيني
    SILTY_CLAY = "silty_clay"  # طيني غريني


class IrrigationMethod(StrEnum):
    """Irrigation methods"""

    DRIP = "drip"  # تنقيط
    SPRINKLER = "sprinkler"  # رش
    SURFACE = "surface"  # سطحي
    FLOOD = "flood"  # غمر
    FURROW = "furrow"  # أخاديد


class UrgencyLevel(StrEnum):
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
# Sensor Value Bounds - حدود قيم المستشعرات
# Physical bounds for validating virtual sensor computed outputs
# ═══════════════════════════════════════════════════════════════════════════════

SENSOR_VALUE_BOUNDS: dict[str, dict[str, float]] = {
    "temperature": {"min": -60.0, "max": 60.0, "unit_ar": "°س"},
    "humidity": {"min": 0.0, "max": 100.0, "unit_ar": "%"},
    "soil_moisture": {"min": 0.0, "max": 1.0, "unit_ar": "م³/م³"},
    "soil_moisture_percent": {"min": 0.0, "max": 100.0, "unit_ar": "%"},
    "et0": {"min": 0.0, "max": 25.0, "unit_ar": "مم/يوم"},
    "etc": {"min": 0.0, "max": 30.0, "unit_ar": "مم/يوم"},
    "kc": {"min": 0.0, "max": 2.0, "unit_ar": "معامل"},
    "wind_speed": {"min": 0.0, "max": 111.12, "unit_ar": "م/ث"},
    "solar_radiation": {"min": 0.0, "max": 130.0, "unit_ar": "MJ/م²/يوم"},
    "water_amount_mm": {"min": 0.0, "max": 500.0, "unit_ar": "مم"},
    "ph": {"min": 0.0, "max": 14.0, "unit_ar": "pH"},
    "ec": {"min": 0.0, "max": 20.0, "unit_ar": "dS/م"},
    "latitude": {"min": -90.0, "max": 90.0, "unit_ar": "درجة"},
    "longitude": {"min": -180.0, "max": 180.0, "unit_ar": "درجة"},
}


def validate_sensor_value(sensor_type: str, value: float) -> tuple[bool, str | None]:
    """
    Validate a computed sensor value against physical bounds.
    Returns (is_valid, error_message).
    """
    bounds = SENSOR_VALUE_BOUNDS.get(sensor_type)
    if bounds is None:
        return True, None
    if not (bounds["min"] <= value <= bounds["max"]):
        return False, (
            f"{sensor_type} value {value} out of bounds [{bounds['min']}, {bounds['max']}] | "
            f"قيمة {sensor_type} خارج الحدود المسموحة"
        )
    return True, None


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Models
# ═══════════════════════════════════════════════════════════════════════════════


class WeatherInput(BaseModel):
    """Weather data input for ET0 calculation"""

    temperature_max: float = Field(..., ge=-60, le=60, description="Maximum temperature (°C)")
    temperature_min: float = Field(..., ge=-60, le=60, description="Minimum temperature (°C)")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    wind_speed: float = Field(
        ...,
        ge=0,
        le=111.12,
        description="Wind speed at 2m height (m/s). Max 400 km/h = 111.12 m/s",
    )
    solar_radiation: float | None = Field(
        None,
        ge=0,
        le=130.0,
        description="Solar radiation (MJ/m²/day). Max 1500 W/m² peak ≈ 130 MJ/m²/day",
    )
    sunshine_hours: float | None = Field(None, ge=0, le=24, description="Sunshine hours")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (degrees)")
    longitude: float | None = Field(None, ge=-180, le=180, description="Longitude (degrees)")
    altitude: float = Field(0, ge=-500, le=5000, description="Altitude above sea level (m)")
    calculation_date: date = Field(default_factory=lambda: date.today(), description="Date for calculation")

    def model_post_init(self, __context: Any) -> None:
        if self.temperature_max < self.temperature_min:
            raise ValueError("temperature_max must be >= temperature_min")


class ET0Response(BaseModel):
    """Reference evapotranspiration response"""

    et0: float = Field(..., description="Reference ET (mm/day)")
    et0_ar: str
    method: str
    weather_summary: dict
    calculation_date: date


class CropWaterRequirement(BaseModel):
    """Crop water requirement calculation input"""

    crop_type: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z_]+$")
    growth_stage: GrowthStage
    planting_date: date | None = None
    days_after_planting: int | None = None
    field_area_hectares: float = Field(1.0, gt=0)

    @field_validator("crop_type")
    @classmethod
    def validate_crop_type(cls, v: str) -> str:
        if v not in CROP_COEFFICIENTS:
            raise ValueError(f"Unsupported crop type '{v}'. Supported: {', '.join(sorted(CROP_COEFFICIENTS.keys()))}")
        return v


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
    last_irrigation_amount: float = Field(..., ge=0, le=500, description="Irrigation amount (mm)")
    rainfall_since: float = Field(0, ge=0, le=500, description="Rainfall since last irrigation (mm)")
    daily_etc: float = Field(..., ge=0, le=25, description="Daily crop ET (mm/day)")


class VirtualSoilMoistureResponse(BaseModel):
    """Virtual soil moisture estimation response"""

    calculation_id: str
    estimated_moisture: float = Field(..., description="Estimated soil moisture (m³/m³)")
    moisture_percentage: float = Field(..., description="Available water depletion (%)")
    days_since_irrigation: int
    total_et_loss: float = Field(..., description="Total ET loss since irrigation (mm)")
    available_water: float = Field(..., description="Remaining available water (mm)")
    total_available_water: float = Field(..., description="Total available water capacity (mm)")
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
    last_irrigation_date: date | None = None
    last_irrigation_amount: float | None = Field(None, ge=0, le=500)
    current_soil_moisture: float | None = Field(None, ge=0, le=1, description="Current moisture if known (m³/m³)")
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

    field_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="Field identifier (alphanumeric, hyphens, underscores)",
    )
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
    delta = (4098 * (0.6108 * math.exp((17.27 * T_mean) / (T_mean + 237.3)))) / ((T_mean + 237.3) ** 2)

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
        * (ws * math.sin(lat_rad) * math.sin(solar_dec) + math.cos(lat_rad) * math.cos(solar_dec) * math.sin(ws))
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


def get_crop_kc(crop_type: str, growth_stage: GrowthStage, days_in_stage: int = None) -> float:
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


def calculate_available_water(soil_type: SoilType, root_depth: float) -> tuple[float, float, float]:
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
        recommended_liters = recommended_mm * field_area_hectares * 10000  # 1 mm = 10 m³/ha
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
        advice = (
            f"No irrigation needed. Soil moisture is adequate. Next irrigation expected in {days_until_needed} days."
        )
        advice_ar = f"لا حاجة للري حالياً. رطوبة التربة كافية. الري القادم متوقع خلال {days_until_needed} أيام."
    else:
        advice = f"Irrigation recommended. Apply {gross_mm:.1f} mm ({recommended_m3:.1f} m³) using {irrigation_method.value} method."
        advice_ar = f"يُنصح بالري. أضف {gross_mm:.1f} مم ({recommended_m3:.1f} متر مكعب) باستخدام طريقة {irrigation_method.value}."

    # Add warnings
    if growth_stage in [GrowthStage.MID_SEASON] and depletion > 60:
        warnings.append("Critical growth stage - avoid water stress")
        warnings_ar.append("مرحلة نمو حرجة - تجنب إجهاد الماء")

    if soil_type in [SoilType.SANDY, SoilType.SANDY_LOAM] and gross_mm > 30:
        warnings.append("Sandy soil - consider splitting irrigation into smaller applications")
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
    logger.info("service_starting", service=SERVICE_NAME, version=SERVICE_VERSION, port=SERVICE_PORT)
    logger.info("crop_coefficients_loaded", count=len(CROP_COEFFICIENTS))
    logger.info("soil_types_loaded", count=len(SOIL_PROPERTIES))

    # Initialize NATS connection state for health checks
    # Note: This service uses sync NATS publisher, not async client
    app.state.nats_client = True if _nats_available else None
    if _nats_available:
        logger.info("nats_publisher_available")
    else:
        logger.warning("nats_publisher_unavailable", mode="degraded")

    # Initialize async NATS client for event publishing
    await _init_nats()

    yield

    # Cleanup
    await _close_nats()
    app.state.nats_client = None
    logger.info("service_shutting_down", service=SERVICE_NAME)


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

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

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

# Add tenant context middleware
try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    app.add_middleware(TenantContextMiddleware)
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


def _enforce_tenant(user: User, requested_tenant_id: str) -> None:
    """Validate JWT tenant matches the requested tenant."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "missing_tenant",
                "message_en": "Token missing tenant ID",
                "message_ar": "الرمز لا يحتوي على معرف المستأجر",
            },
        )
    if user.tenant_id != requested_tenant_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "tenant_mismatch",
                "message_ar": "لا يمكنك الوصول إلى بيانات مستأجر آخر",
                "message_en": "Cannot access another tenant's data",
            },
        )


@app.get("/healthz")
@app.get("/health")
async def health_check():
    """Health check endpoint with dependency status"""
    nats_connected = hasattr(app.state, "nats_client") and app.state.nats_client is not None

    return {
        "status": "healthy" if nats_connected else "degraded",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "nats_connected": nats_connected,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz")
async def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    nats_ok = _nats_client is not None and not _nats_client.is_closed

    redis_ok = False
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis.asyncio as aioredis

            r = aioredis.from_url(redis_url, socket_connect_timeout=2)
            await r.ping()
            redis_ok = True
            await r.aclose()
        except Exception:
            redis_ok = False
    else:
        redis_ok = True  # Not configured, not required

    all_ok = nats_ok or not _nats_available  # NATS optional when unavailable
    status = "ready" if all_ok and redis_ok else "not_ready"

    response = {
        "status": status,
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "checks": {
            "service": "ready",
            "nats": "connected" if nats_ok else "disconnected",
            "redis": "connected" if redis_ok else "disconnected",
        },
    }

    if status != "ready":
        raise HTTPException(status_code=503, detail=response)

    return response


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(
        content=generate_latest(PROM_REGISTRY),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


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
async def calculate_et0(weather: WeatherInput, user: User = Depends(get_current_user)):
    """
    Calculate reference evapotranspiration (ET0) using Penman-Monteith.
    حساب التبخر-نتح المرجعي باستخدام بنمان-مونتيث
    """
    tenant_id = getattr(user, "tenant_id", None) or ""
    logger.info("et0_calculate", tenant_id=tenant_id, user_id=getattr(user, "id", None))

    et0 = calculate_et0_penman_monteith(weather)

    # Publish sensor.calculated event
    await publish_event(
        "sahool.sensor.calculated",
        {
            "sensor_type": "et0",
            "method": "FAO-56 Penman-Monteith",
            "value": round(et0, 2),
            "unit": "mm/day",
            "latitude": weather.latitude,
            "altitude": weather.altitude,
            "calculation_date": str(weather.calculation_date),
            "user_id": user.id if hasattr(user, "id") else None,
            "tenant_id": tenant_id,
        },
    )

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
    growth_stage: GrowthStage | None = None,
    days_in_stage: int | None = None,
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
    user: User = Depends(get_current_user),
    field_area_hectares: float = Query(1.0, gt=0, description="Field area in hectares"),
    days_in_stage: int | None = Query(None, description="Days in current stage"),
):
    """
    Calculate crop evapotranspiration (ETc = ET0 × Kc).
    حساب التبخر-نتح للمحصول
    """
    tenant_id = getattr(user, "tenant_id", None) or ""
    logger.info("etc_calculate", tenant_id=tenant_id, user_id=getattr(user, "id", None))

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
                "available_water_capacity": props["field_capacity"] - props["wilting_point"],
                "infiltration_rate_mm_hr": props["infiltration_rate"],
            }
        )
    return {"soils": soils, "total": len(soils)}


@app.post("/v1/soil-moisture/estimate", response_model=VirtualSoilMoistureResponse)
async def estimate_virtual_soil_moisture(input_data: SoilMoistureInput, user: User = Depends(get_current_user)):
    """
    Estimate soil moisture using water balance method.
    تقدير رطوبة التربة باستخدام ميزان الماء
    """
    tenant_id = getattr(user, "tenant_id", None) or ""

    result = estimate_soil_moisture(
        soil_type=input_data.soil_type,
        root_depth=input_data.root_depth,
        last_irrigation_date=input_data.last_irrigation_date,
        last_irrigation_amount=input_data.last_irrigation_amount,
        rainfall_since=input_data.rainfall_since,
        daily_etc=input_data.daily_etc,
    )

    calculation_id = str(uuid.uuid4())

    # Publish sensor.calculated event for soil moisture estimation
    await publish_event(
        "sahool.sensor.calculated",
        {
            "calculation_id": calculation_id,
            "sensor_type": "soil_moisture",
            "method": "water_balance",
            "value": round(result["moisture_content"], 3),
            "unit": "volumetric",
            "depletion_percent": round(result["depletion_percent"], 1),
            "soil_type": input_data.soil_type.value,
            "status": result["status"],
            "urgency": result["urgency"].value if hasattr(result["urgency"], "value") else str(result["urgency"]),
            "user_id": user.id if hasattr(user, "id") else None,
            "tenant_id": tenant_id,
        },
    )

    # Publish sensor.anomaly event when critical depletion is detected
    if result["depletion_percent"] >= 80:
        await publish_event(
            "sahool.sensor.anomaly",
            {
                "calculation_id": calculation_id,
                "anomaly_type": "critical_moisture_depletion",
                "sensor_type": "soil_moisture",
                "depletion_percent": round(result["depletion_percent"], 1),
                "soil_type": input_data.soil_type.value,
                "status": result["status"],
                "urgency": result["urgency"].value if hasattr(result["urgency"], "value") else str(result["urgency"]),
                "message": "Soil moisture critically depleted - immediate irrigation recommended",
                "message_ar": "رطوبة التربة منخفضة بشكل حرج - يوصى بالري فوراً",
                "tenant_id": tenant_id,
            },
        )

    return VirtualSoilMoistureResponse(
        calculation_id=calculation_id,
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
async def get_irrigation_recommendation(
    input_data: IrrigationRecommendationInput, user: User = Depends(get_current_user)
):
    """
    Get complete irrigation recommendation.
    الحصول على توصية ري شاملة
    """
    if input_data.crop_type not in CROP_COEFFICIENTS:
        raise HTTPException(status_code=404, detail=f"Crop '{input_data.crop_type}' not found")

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
    last_irr_date = input_data.last_irrigation_date or (date.today() - timedelta(days=7))
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
        timestamp=datetime.now(UTC),
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
    days_since_irrigation: int = Query(..., ge=0, description="Days since last irrigation"),
    temperature: float = Query(..., ge=-60, le=60, description="Average temperature (°C)"),
    humidity: float = Query(50, ge=0, le=100, description="Relative humidity (%)"),
    user: User = Depends(get_current_user),
):
    """
    Quick irrigation check without full weather data.
    فحص سريع للري بدون بيانات الطقس الكاملة
    """
    tenant_id = getattr(user, "tenant_id", None) or ""
    logger.info("quick_irrigation_check", tenant_id=tenant_id, user_id=getattr(user, "id", None))

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

    field_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="معرف الحقل - Field identifier (alphanumeric, hyphens, underscores)",
    )
    farmer_id: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="معرف المزارع",
    )
    tenant_id: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="معرف المستأجر",
    )
    crop_type: str = Field(..., min_length=1, max_length=50, description="نوع المحصول")

    @field_validator("crop_type")
    @classmethod
    def validate_crop_type(cls, v: str) -> str:
        if v not in CROP_COEFFICIENTS:
            raise ValueError(f"Unsupported crop type '{v}'. Supported: {', '.join(sorted(CROP_COEFFICIENTS.keys()))}")
        return v

    growth_stage: GrowthStage = Field(..., description="مرحلة النمو")
    soil_type: SoilType = Field(SoilType.LOAM, description="نوع التربة")
    irrigation_method: IrrigationMethod = Field(IrrigationMethod.DRIP, description="طريقة الري")
    field_area_hectares: float = Field(1.0, gt=0, description="مساحة الحقل بالهكتار")
    last_irrigation_date: date | None = Field(None, description="تاريخ آخر ري")
    last_irrigation_amount: float | None = Field(None, description="كمية آخر ري بالمم")
    weather: WeatherInput = Field(..., description="بيانات الطقس")
    publish_event: bool = Field(default=True, description="نشر الحدث عبر NATS")


def _create_virtual_sensor_action(
    recommendation: IrrigationRecommendation,
    field_id: str,
    farmer_id: str | None = None,
    tenant_id: str | None = None,
) -> dict[str, Any]:
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
            int(recommendation.gross_irrigation_mm * 2) if recommendation.irrigation_needed else 30
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
        "created_at": datetime.now(UTC).isoformat(),
    }


@app.post("/v1/irrigation/recommend-with-action")
async def get_irrigation_recommendation_with_action(
    request: VirtualSensorActionRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """
    الحصول على توصية ري مع ActionTemplate

    Field-First: ينتج قالب إجراء للتطبيق المحمول
    Badge: تقدير افتراضي (بدون حساس)
    """

    # Enforce tenant isolation
    if request.tenant_id:
        _enforce_tenant(user, request.tenant_id)

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
            logger.info(f"NATS: Published virtual sensor event for field {request.field_id}")
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
        "nats_published": request.publish_event and _nats_available and recommendation.irrigation_needed,
    }


@app.get("/v1/quick-check-with-action")
async def quick_check_with_action(
    field_id: str = Query(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="معرف الحقل - Field identifier",
    ),
    farmer_id: str | None = Query(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_\-]+$",
        description="معرف المزارع",
    ),
    crop_type: str = Query(..., description="نوع المحصول"),
    growth_stage: GrowthStage = Query(..., description="مرحلة النمو"),
    soil_type: SoilType = Query(SoilType.LOAM, description="نوع التربة"),
    days_since_irrigation: int = Query(..., ge=0, description="أيام منذ آخر ري"),
    temperature: float = Query(..., ge=-60, le=60, description="درجة الحرارة"),
    humidity: float = Query(50, ge=0, le=100, description="الرطوبة النسبية"),
    tenant_id: str | None = Query(None, description="معرف المستأجر - Tenant identifier"),
    user: User = Depends(get_current_user),
):
    """
    فحص سريع مع ActionTemplate

    للبيئات الريفية بدون IoT
    """
    # Enforce tenant isolation
    if tenant_id:
        _enforce_tenant(user, tenant_id)

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

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)  # nosec B104 - binding to all interfaces required for Docker container
