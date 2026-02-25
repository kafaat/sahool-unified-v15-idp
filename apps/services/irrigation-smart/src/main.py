"""
💧 SAHOOL Smart Irrigation Service v15.3
خدمة الري الذكي - AI-Powered Scheduling & Water Conservation

Field-First Architecture:
- كل توصية تُنتج ActionTemplate قابل للتنفيذ بدون اتصال
- التحليل يخدم الميدان، لا العكس
"""

import json
import math
import os

# Field-First: Action Template Support
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, time, timedelta, timezone
from enum import Enum, StrEnum
from typing import Any

import jwt
import structlog
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# NATS messaging
try:
    import nats

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    nats = None

logger = structlog.get_logger()

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel, Field

sys.path.insert(0, "/app")
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

    def setup_security_headers(app):
        pass


from shared.middleware.tenant_context import TenantContextMiddleware

try:
    from shared.contracts.actions import (
        ActionTemplate,
        ActionTemplateFactory,
    )
    from shared.contracts.actions import (
        UrgencyLevel as ActionUrgency,
    )

    ACTION_TEMPLATE_AVAILABLE = True
except ImportError:
    ACTION_TEMPLATE_AVAILABLE = False


# =============================================================================
# Lifespan & NATS Connection
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown"""
    logger.info("Starting irrigation-smart service...")

    # Initialize NATS connection
    app.state.nc = None
    if NATS_AVAILABLE:
        nats_url = os.getenv("NATS_URL")
        if nats_url:
            try:
                app.state.nc = await nats.connect(nats_url)
                logger.info("Connected to NATS", nats_url=nats_url)
            except Exception as e:
                logger.warning("Failed to connect to NATS", error=str(e))
                app.state.nc = None
        else:
            logger.info("NATS_URL not configured, event publishing disabled")
    else:
        logger.warning("nats-py not installed, event publishing disabled")

    yield

    # Shutdown: Close NATS connection
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("Closed NATS connection")

    logger.info("Shutdown irrigation-smart service complete")


app = FastAPI(
    title="SAHOOL Smart Irrigation Service | خدمة الري الذكي",
    version="16.0.0",
    description="AI-powered irrigation scheduling, water conservation, and smart recommendations",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Security headers - رؤوس الأمان
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

# Tenant context middleware - عزل المستأجرين
app.add_middleware(TenantContextMiddleware)


# =============================================================================
# JWT Authentication - مصادقة JWT
# =============================================================================

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT token and return user info.
    التحقق من رمز JWT وإرجاع معلومات المستخدم.
    """
    token = credentials.credentials
    jwt_secret = os.getenv("JWT_SECRET_KEY")

    if not jwt_secret:
        logger.error("JWT_SECRET_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT not configured",
        )

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256", "HS384", "HS512"],
        )
        logger.debug("JWT validated successfully", user_id=payload.get("sub"))
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid JWT token", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# =============================================================================
# Enums & Models
# =============================================================================


class CropType(StrEnum):
    TOMATO = "tomato"
    WHEAT = "wheat"
    COFFEE = "coffee"
    QAT = "qat"
    BANANA = "banana"
    CUCUMBER = "cucumber"
    PEPPER = "pepper"
    POTATO = "potato"
    CORN = "corn"
    GRAPES = "grapes"
    DATE_PALM = "date_palm"
    MANGO = "mango"
    ONION = "onion"
    GARLIC = "garlic"
    ALFALFA = "alfalfa"


class GrowthStage(StrEnum):
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"


class SoilType(StrEnum):
    SANDY = "sandy"
    CLAY = "clay"
    LOAMY = "loamy"
    SILT = "silt"
    ROCKY = "rocky"


class IrrigationMethod(StrEnum):
    FLOOD = "flood"
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    FURROW = "furrow"
    TRADITIONAL = "traditional"


class UrgencyLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IrrigationRequest(BaseModel):
    field_id: str
    crop: CropType
    growth_stage: GrowthStage
    area_hectares: float = Field(..., gt=0)
    soil_type: SoilType = SoilType.LOAMY
    irrigation_method: IrrigationMethod = IrrigationMethod.DRIP
    current_soil_moisture: float | None = Field(default=None, ge=0, le=100)
    last_irrigation_date: date | None = None
    weather_forecast: dict[str, Any] | None = None


class IrrigationSchedule(BaseModel):
    schedule_id: str
    field_id: str
    crop: CropType
    crop_name_ar: str
    irrigation_date: date
    start_time: str
    duration_minutes: int
    water_amount_liters: float
    water_amount_m3: float
    urgency: UrgencyLevel
    urgency_ar: str
    method: IrrigationMethod
    method_ar: str
    reasoning_ar: str
    reasoning_en: str
    weather_adjusted: bool
    savings_percent: float


class IrrigationPlan(BaseModel):
    plan_id: str
    field_id: str
    crop: CropType
    crop_name_ar: str
    growth_stage: GrowthStage
    growth_stage_ar: str
    area_hectares: float
    soil_type: SoilType
    current_water_need_mm: float
    daily_et_mm: float
    schedules: list[IrrigationSchedule]
    total_water_m3: float
    estimated_cost_yer: float
    water_savings_m3: float
    recommendations_ar: list[str]
    recommendations_en: list[str]
    alerts_ar: list[str]
    created_at: datetime


class SoilMoistureReading(BaseModel):
    field_id: str
    sensor_id: str
    reading_time: datetime
    depth_cm: int
    moisture_percent: float
    temperature_c: float
    ec_ds_m: float


class WaterBalance(BaseModel):
    field_id: str
    date: date
    et_mm: float
    rainfall_mm: float
    irrigation_mm: float
    soil_moisture_change_mm: float
    water_deficit_mm: float
    cumulative_deficit_mm: float


class IrrigationExecution(BaseModel):
    """تنفيذ الري - Record actual irrigation event"""

    field_id: str
    schedule_id: str | None = None
    plan_id: str | None = None
    amount_mm: float = Field(..., gt=0, description="Water amount in mm")
    duration_minutes: int = Field(..., gt=0, description="Actual duration in minutes")
    method: IrrigationMethod = IrrigationMethod.DRIP
    executed_at: datetime | None = None
    notes: str | None = None


# =============================================================================
# Crop & Irrigation Data
# =============================================================================

CROP_TRANSLATIONS = {
    CropType.TOMATO: "طماطم",
    CropType.WHEAT: "قمح",
    CropType.COFFEE: "بن",
    CropType.QAT: "قات",
    CropType.BANANA: "موز",
    CropType.CUCUMBER: "خيار",
    CropType.PEPPER: "فلفل",
    CropType.POTATO: "بطاطس",
    CropType.CORN: "ذرة",
    CropType.GRAPES: "عنب",
    CropType.DATE_PALM: "نخيل",
    CropType.MANGO: "مانجو",
    CropType.ONION: "بصل",
    CropType.GARLIC: "ثوم",
    CropType.ALFALFA: "برسيم",
}

STAGE_TRANSLATIONS = {
    GrowthStage.SEEDLING: "شتلة",
    GrowthStage.VEGETATIVE: "نمو خضري",
    GrowthStage.FLOWERING: "إزهار",
    GrowthStage.FRUITING: "إثمار",
    GrowthStage.MATURITY: "نضج",
}

METHOD_TRANSLATIONS = {
    IrrigationMethod.FLOOD: "ري غمر",
    IrrigationMethod.DRIP: "ري بالتنقيط",
    IrrigationMethod.SPRINKLER: "ري رشاش",
    IrrigationMethod.FURROW: "ري أخدود",
    IrrigationMethod.TRADITIONAL: "ري تقليدي",
}

URGENCY_TRANSLATIONS = {
    UrgencyLevel.LOW: "منخفض",
    UrgencyLevel.MEDIUM: "متوسط",
    UrgencyLevel.HIGH: "عالي",
    UrgencyLevel.CRITICAL: "حرج",
}

# Crop water requirements (mm/day) by growth stage
CROP_WATER_REQUIREMENTS = {
    CropType.TOMATO: {
        GrowthStage.SEEDLING: 2.5,
        GrowthStage.VEGETATIVE: 4.5,
        GrowthStage.FLOWERING: 6.0,
        GrowthStage.FRUITING: 7.5,
        GrowthStage.MATURITY: 4.0,
    },
    CropType.WHEAT: {
        GrowthStage.SEEDLING: 2.0,
        GrowthStage.VEGETATIVE: 4.0,
        GrowthStage.FLOWERING: 5.5,
        GrowthStage.FRUITING: 4.5,
        GrowthStage.MATURITY: 2.5,
    },
    CropType.COFFEE: {
        GrowthStage.SEEDLING: 3.0,
        GrowthStage.VEGETATIVE: 4.0,
        GrowthStage.FLOWERING: 5.0,
        GrowthStage.FRUITING: 5.5,
        GrowthStage.MATURITY: 3.5,
    },
    CropType.BANANA: {
        GrowthStage.SEEDLING: 4.0,
        GrowthStage.VEGETATIVE: 6.0,
        GrowthStage.FLOWERING: 7.0,
        GrowthStage.FRUITING: 8.0,
        GrowthStage.MATURITY: 5.0,
    },
    CropType.QAT: {
        GrowthStage.SEEDLING: 3.5,
        GrowthStage.VEGETATIVE: 5.0,
        GrowthStage.FLOWERING: 5.5,
        GrowthStage.FRUITING: 6.0,
        GrowthStage.MATURITY: 4.0,
    },
    CropType.DATE_PALM: {
        GrowthStage.SEEDLING: 5.0,
        GrowthStage.VEGETATIVE: 8.0,
        GrowthStage.FLOWERING: 10.0,
        GrowthStage.FRUITING: 12.0,
        GrowthStage.MATURITY: 7.0,
    },
}

# Add defaults for other crops
for crop in CropType:
    if crop not in CROP_WATER_REQUIREMENTS:
        CROP_WATER_REQUIREMENTS[crop] = CROP_WATER_REQUIREMENTS[CropType.TOMATO]

# Soil water holding capacity (mm/m depth)
SOIL_WATER_CAPACITY = {
    SoilType.SANDY: 80,
    SoilType.LOAMY: 150,
    SoilType.CLAY: 200,
    SoilType.SILT: 170,
    SoilType.ROCKY: 50,
}

# Irrigation efficiency by method
IRRIGATION_EFFICIENCY = {
    IrrigationMethod.DRIP: 0.90,
    IrrigationMethod.SPRINKLER: 0.75,
    IrrigationMethod.FURROW: 0.60,
    IrrigationMethod.FLOOD: 0.50,
    IrrigationMethod.TRADITIONAL: 0.45,
}

# Water cost (YER per m³)
WATER_COST_PER_M3 = 150


# =============================================================================
# NATS Event Publishing
# =============================================================================


async def publish_event(subject: str, data: dict) -> bool:
    """
    Publish event to NATS message bus.

    Args:
        subject: NATS subject (e.g., "sahool.irrigation.plan_created")
        data: Event data to publish

    Returns:
        True if published successfully, False otherwise
    """
    try:
        nc = app.state.nc
        if nc and nc.is_connected:
            payload = json.dumps(data, default=str).encode()
            await nc.publish(subject, payload)
            logger.info(
                "Published event",
                subject=subject,
                field_id=data.get("field_id"),
            )
            return True
        else:
            logger.debug("NATS not connected, skipping event publish", subject=subject)
            return False
    except Exception as e:
        logger.error("Failed to publish event", subject=subject, error=str(e))
        return False


# =============================================================================
# Calculation Functions
# =============================================================================


def calculate_et0(temperature: float, humidity: float, wind_speed: float, solar_radiation: float = 20) -> float:
    """Calculate reference evapotranspiration (Hargreaves method)"""
    # Simplified ET0 = 0.0023 * Ra * (T + 17.8) * TD^0.5
    # Where TD = daily temperature range (assumed 10°C)
    td = 10  # Temperature range
    et0 = 0.0023 * solar_radiation * (temperature + 17.8) * math.sqrt(td)
    # Adjust for humidity and wind
    humidity_factor = 1 + (50 - humidity) / 100
    wind_factor = 1 + wind_speed / 100
    return round(et0 * humidity_factor * wind_factor, 2)


def calculate_crop_et(et0: float, crop: CropType, stage: GrowthStage) -> float:
    """Calculate crop evapotranspiration (ETc = ET0 * Kc)"""
    # Crop coefficients by stage
    kc_values = {
        GrowthStage.SEEDLING: 0.5,
        GrowthStage.VEGETATIVE: 0.8,
        GrowthStage.FLOWERING: 1.0,
        GrowthStage.FRUITING: 1.15,
        GrowthStage.MATURITY: 0.8,
    }
    kc = kc_values[stage]

    # Crop-specific adjustments
    if crop == CropType.BANANA:
        kc *= 1.1
    elif crop == CropType.DATE_PALM:
        kc *= 1.2
    elif crop == CropType.WHEAT:
        kc *= 0.9

    return round(et0 * kc, 2)


def calculate_water_need(
    crop: CropType,
    stage: GrowthStage,
    area_ha: float,
    soil_type: SoilType,
    method: IrrigationMethod,
    current_moisture: float | None,
    days_since_irrigation: int,
    temperature: float = 30,
    humidity: float = 50,
    rainfall_forecast: float = 0,
) -> dict[str, Any]:
    """Calculate irrigation water requirements"""

    # Base water requirement from crop data
    base_et = CROP_WATER_REQUIREMENTS[crop][stage]

    # Adjust for weather (simplified)
    temp_factor = 1 + (temperature - 25) / 50  # Higher temp = more water
    humidity_factor = 1 + (50 - humidity) / 100  # Lower humidity = more water

    adjusted_et = base_et * temp_factor * humidity_factor

    # Calculate ET0 for reference
    et0 = calculate_et0(temperature, humidity, 10)
    crop_et = calculate_crop_et(et0, crop, stage)

    # Use the higher of the two estimates
    daily_need_mm = max(adjusted_et, crop_et)

    # Accumulated deficit since last irrigation
    accumulated_need_mm = daily_need_mm * max(1, days_since_irrigation)

    # Subtract expected rainfall
    accumulated_need_mm = max(0, accumulated_need_mm - rainfall_forecast)

    # Adjust for soil moisture if available
    if current_moisture is not None:
        soil_capacity = SOIL_WATER_CAPACITY[soil_type]
        moisture_deficit = (70 - current_moisture) / 100 * soil_capacity * 0.3  # Top 30cm
        accumulated_need_mm = max(accumulated_need_mm, moisture_deficit)

    # Apply irrigation efficiency
    efficiency = IRRIGATION_EFFICIENCY[method]
    gross_water_mm = accumulated_need_mm / efficiency

    # Convert to volume
    water_m3 = gross_water_mm * area_ha * 10  # mm * ha * 10 = m³
    water_liters = water_m3 * 1000

    # Determine urgency
    if accumulated_need_mm > daily_need_mm * 3:
        urgency = UrgencyLevel.CRITICAL
    elif accumulated_need_mm > daily_need_mm * 2:
        urgency = UrgencyLevel.HIGH
    elif accumulated_need_mm > daily_need_mm * 1:
        urgency = UrgencyLevel.MEDIUM
    else:
        urgency = UrgencyLevel.LOW

    # Calculate potential savings with drip vs current method
    if method != IrrigationMethod.DRIP:
        drip_water = accumulated_need_mm / IRRIGATION_EFFICIENCY[IrrigationMethod.DRIP]
        savings_percent = (gross_water_mm - drip_water) / gross_water_mm * 100
    else:
        savings_percent = 0

    return {
        "daily_et_mm": round(daily_need_mm, 2),
        "accumulated_need_mm": round(accumulated_need_mm, 2),
        "gross_water_mm": round(gross_water_mm, 2),
        "water_m3": round(water_m3, 2),
        "water_liters": round(water_liters, 0),
        "urgency": urgency,
        "efficiency": efficiency,
        "savings_percent": round(savings_percent, 1),
    }


def determine_irrigation_time(crop: CropType, temperature: float) -> str:
    """Determine optimal irrigation time"""
    if temperature > 35:
        return "05:00"  # Very early for hot weather
    elif temperature > 30:
        return "06:00"
    else:
        return "07:00"


def calculate_duration(water_liters: float, flow_rate_lph: float = 2000) -> int:
    """Calculate irrigation duration in minutes"""
    hours = water_liters / flow_rate_lph
    return round(hours * 60)


def generate_reasoning(
    crop: CropType,
    stage: GrowthStage,
    urgency: UrgencyLevel,
    water_need: dict[str, Any],
    days_since_irrigation: int,
) -> tuple[str, str]:
    """Generate bilingual reasoning for irrigation recommendation"""

    crop_ar = CROP_TRANSLATIONS[crop]
    stage_ar = STAGE_TRANSLATIONS[stage]

    if urgency == UrgencyLevel.CRITICAL:
        reason_ar = f"⚠️ {crop_ar} في مرحلة {stage_ar} يعاني من نقص مائي حاد. آخر ري منذ {days_since_irrigation} أيام. الري فوري ضروري لتجنب خسائر المحصول."
        reason_en = f"⚠️ {crop.value} in {stage.value} stage is experiencing severe water stress. Last irrigation {days_since_irrigation} days ago. Immediate irrigation required to avoid crop loss."
    elif urgency == UrgencyLevel.HIGH:
        reason_ar = f"🔴 {crop_ar} يحتاج ري عاجل. الاحتياج المتراكم {water_need['accumulated_need_mm']} ملم."
        reason_en = f"🔴 {crop.value} needs urgent irrigation. Accumulated need {water_need['accumulated_need_mm']} mm."
    elif urgency == UrgencyLevel.MEDIUM:
        reason_ar = f"🟡 {crop_ar} يحتاج ري خلال 24 ساعة. مرحلة {stage_ar} تتطلب {water_need['daily_et_mm']} ملم/يوم."
        reason_en = f"🟡 {crop.value} needs irrigation within 24 hours. {stage.value} stage requires {water_need['daily_et_mm']} mm/day."
    else:
        reason_ar = f"🟢 {crop_ar} في حالة جيدة. الري الوقائي مُوصى به للحفاظ على رطوبة مثالية."
        reason_en = (
            f"🟢 {crop.value} is in good condition. Preventive irrigation recommended to maintain optimal moisture."
        )

    return reason_ar, reason_en


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/healthz")
def health():
    """Health check endpoint (liveness probe)"""
    return {
        "status": "ok",
        "service": "irrigation-smart",
        "version": "16.0.0",
    }


@app.get("/readyz")
def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    nats_connected = hasattr(app.state, "nc") and app.state.nc is not None and app.state.nc.is_connected
    return {
        "status": "ready",
        "service": "irrigation-smart",
        "version": "16.0.0",
        "checks": {
            "crop_requirements": "loaded" if CROP_WATER_REQUIREMENTS else "not_loaded",
            "nats": "connected" if nats_connected else "disconnected",
        },
        "crops_supported": len(CROP_WATER_REQUIREMENTS),
    }


@app.get("/v1/crops")
def list_crops(user: dict = Depends(get_current_user)):
    """قائمة المحاصيل المدعومة - Protected endpoint"""
    return {
        "crops": [
            {
                "id": crop.value,
                "name_ar": CROP_TRANSLATIONS[crop],
                "water_requirements_mm_day": CROP_WATER_REQUIREMENTS[crop],
            }
            for crop in CropType
        ]
    }


@app.get("/v1/methods")
def list_irrigation_methods(user: dict = Depends(get_current_user)):
    """طرق الري المتاحة - Protected endpoint"""
    return {
        "methods": [
            {
                "id": method.value,
                "name_ar": METHOD_TRANSLATIONS[method],
                "efficiency_percent": int(IRRIGATION_EFFICIENCY[method] * 100),
            }
            for method in IrrigationMethod
        ]
    }


@app.post("/v1/calculate", response_model=IrrigationPlan)
async def calculate_irrigation(
    request: IrrigationRequest,
    user: dict = Depends(get_current_user),
):
    """حساب احتياجات الري - Protected endpoint"""
    import random

    # Calculate days since last irrigation
    if request.last_irrigation_date:
        days_since = (date.today() - request.last_irrigation_date).days
    else:
        days_since = 3  # Assume 3 days if unknown

    # Get weather data (use provided or simulate)
    if request.weather_forecast:
        temperature = request.weather_forecast.get("temperature", 30)
        humidity = request.weather_forecast.get("humidity", 50)
        rainfall = request.weather_forecast.get("rainfall_mm", 0)
    else:
        temperature = random.uniform(25, 38)
        humidity = random.uniform(30, 70)
        rainfall = random.uniform(0, 5) if random.random() < 0.2 else 0

    # Calculate water needs
    water_need = calculate_water_need(
        crop=request.crop,
        stage=request.growth_stage,
        area_ha=request.area_hectares,
        soil_type=request.soil_type,
        method=request.irrigation_method,
        current_moisture=request.current_soil_moisture,
        days_since_irrigation=days_since,
        temperature=temperature,
        humidity=humidity,
        rainfall_forecast=rainfall,
    )

    # Generate schedules (split if large amount)
    schedules = []
    total_water = water_need["water_liters"]
    remaining_water = total_water

    schedule_date = date.today()
    while remaining_water > 0:
        # Maximum per session based on soil type
        max_per_session = {
            SoilType.SANDY: total_water * 0.3,
            SoilType.LOAMY: total_water * 0.5,
            SoilType.CLAY: total_water * 0.4,
            SoilType.SILT: total_water * 0.45,
            SoilType.ROCKY: total_water * 0.25,
        }[request.soil_type]

        session_water = min(remaining_water, max_per_session)
        remaining_water -= session_water

        start_time = determine_irrigation_time(request.crop, temperature)
        duration = calculate_duration(session_water)

        reason_ar, reason_en = generate_reasoning(
            request.crop,
            request.growth_stage,
            water_need["urgency"],
            water_need,
            days_since,
        )

        schedules.append(
            IrrigationSchedule(
                schedule_id=str(uuid.uuid4()),
                field_id=request.field_id,
                crop=request.crop,
                crop_name_ar=CROP_TRANSLATIONS[request.crop],
                irrigation_date=schedule_date,
                start_time=start_time,
                duration_minutes=duration,
                water_amount_liters=round(session_water, 0),
                water_amount_m3=round(session_water / 1000, 2),
                urgency=water_need["urgency"],
                urgency_ar=URGENCY_TRANSLATIONS[water_need["urgency"]],
                method=request.irrigation_method,
                method_ar=METHOD_TRANSLATIONS[request.irrigation_method],
                reasoning_ar=reason_ar,
                reasoning_en=reason_en,
                weather_adjusted=rainfall > 0,
                savings_percent=water_need["savings_percent"],
            )
        )

        schedule_date += timedelta(days=1)

        if len(schedules) >= 7:  # Max 7 days planning
            break

    # Calculate totals
    total_water_m3 = water_need["water_m3"]
    estimated_cost = total_water_m3 * WATER_COST_PER_M3

    # Calculate potential savings with drip
    if request.irrigation_method != IrrigationMethod.DRIP:
        drip_efficiency = IRRIGATION_EFFICIENCY[IrrigationMethod.DRIP]
        current_efficiency = IRRIGATION_EFFICIENCY[request.irrigation_method]
        savings_m3 = total_water_m3 * (1 - current_efficiency / drip_efficiency)
    else:
        savings_m3 = 0

    # Generate recommendations
    recommendations_ar = []
    recommendations_en = []

    if water_need["urgency"] == UrgencyLevel.CRITICAL:
        recommendations_ar.append("⚠️ ري فوري مطلوب - تجنب تأخير أكثر من 6 ساعات")
        recommendations_en.append("⚠️ Immediate irrigation required - avoid delay beyond 6 hours")

    if request.irrigation_method == IrrigationMethod.FLOOD:
        recommendations_ar.append("💡 التحويل للري بالتنقيط يوفر حتى 45% من المياه")
        recommendations_en.append("💡 Switching to drip irrigation can save up to 45% water")

    if temperature > 35:
        recommendations_ar.append("🌡️ ري في الصباح الباكر فقط لتقليل التبخر")
        recommendations_en.append("🌡️ Irrigate early morning only to reduce evaporation")

    if request.current_soil_moisture and request.current_soil_moisture < 30:
        recommendations_ar.append("🔴 رطوبة التربة منخفضة جداً - زيادة تواتر الري")
        recommendations_en.append("🔴 Soil moisture very low - increase irrigation frequency")

    recommendations_ar.append(f"💧 كفاءة الري الحالية: {int(water_need['efficiency'] * 100)}%")
    recommendations_en.append(f"💧 Current irrigation efficiency: {int(water_need['efficiency'] * 100)}%")

    # Alerts
    alerts_ar = []
    if water_need["urgency"] in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]:
        alerts_ar.append(f"🚨 {CROP_TRANSLATIONS[request.crop]} يحتاج ري عاجل!")

    if rainfall > 10:
        alerts_ar.append(f"🌧️ أمطار متوقعة ({rainfall} ملم) - تم تعديل الجدول")

    plan_id = str(uuid.uuid4())
    plan = IrrigationPlan(
        plan_id=plan_id,
        field_id=request.field_id,
        crop=request.crop,
        crop_name_ar=CROP_TRANSLATIONS[request.crop],
        growth_stage=request.growth_stage,
        growth_stage_ar=STAGE_TRANSLATIONS[request.growth_stage],
        area_hectares=request.area_hectares,
        soil_type=request.soil_type,
        current_water_need_mm=water_need["accumulated_need_mm"],
        daily_et_mm=water_need["daily_et_mm"],
        schedules=schedules,
        total_water_m3=round(total_water_m3, 2),
        estimated_cost_yer=round(estimated_cost, 0),
        water_savings_m3=round(savings_m3, 2),
        recommendations_ar=recommendations_ar,
        recommendations_en=recommendations_en,
        alerts_ar=alerts_ar,
        created_at=datetime.now(UTC),
    )

    # Publish irrigation plan created event
    await publish_event(
        subject="sahool.irrigation.plan_created",
        data={
            "field_id": request.field_id,
            "plan_id": plan_id,
            "schedule": [
                {
                    "schedule_id": s.schedule_id,
                    "date": s.irrigation_date,
                    "start_time": s.start_time,
                    "duration_minutes": s.duration_minutes,
                    "water_amount_m3": s.water_amount_m3,
                }
                for s in schedules
            ],
            "total_water_m3": plan.total_water_m3,
            "urgency": water_need["urgency"].value,
            "crop": request.crop.value,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )

    return plan


@app.get("/v1/water-balance/{field_id}")
def get_water_balance(
    field_id: str,
    crop: CropType = Query(default=CropType.TOMATO),
    days: int = Query(default=14, ge=7, le=60),
    user: dict = Depends(get_current_user),
):
    """الميزان المائي للحقل - Protected endpoint"""
    import random

    balance_data = []
    cumulative_deficit = 0

    for i in range(days):
        balance_date = date.today() - timedelta(days=days - i - 1)

        # Simulate daily values
        et = random.uniform(4, 8)
        rainfall = random.uniform(0, 15) if random.random() < 0.15 else 0
        irrigation = random.uniform(0, 30) if random.random() < 0.3 else 0

        net_change = rainfall + irrigation - et
        daily_deficit = max(0, et - rainfall - irrigation)
        cumulative_deficit += daily_deficit

        balance_data.append(
            WaterBalance(
                field_id=field_id,
                date=balance_date,
                et_mm=round(et, 2),
                rainfall_mm=round(rainfall, 2),
                irrigation_mm=round(irrigation, 2),
                soil_moisture_change_mm=round(net_change, 2),
                water_deficit_mm=round(daily_deficit, 2),
                cumulative_deficit_mm=round(cumulative_deficit, 2),
            )
        )

    # Summary statistics
    total_et = sum(b.et_mm for b in balance_data)
    total_rainfall = sum(b.rainfall_mm for b in balance_data)
    total_irrigation = sum(b.irrigation_mm for b in balance_data)

    return {
        "field_id": field_id,
        "crop": crop.value,
        "period_days": days,
        "summary": {
            "total_et_mm": round(total_et, 2),
            "total_rainfall_mm": round(total_rainfall, 2),
            "total_irrigation_mm": round(total_irrigation, 2),
            "net_water_balance_mm": round(total_rainfall + total_irrigation - total_et, 2),
            "cumulative_deficit_mm": round(cumulative_deficit, 2),
        },
        "daily_data": [b.dict() for b in balance_data],
        "recommendation_ar": ("💧 يُنصح بري تعويضي" if cumulative_deficit > 30 else "✅ الميزان المائي متوازن"),
    }


@app.post("/v1/sensor-reading")
def record_sensor_reading(
    reading: SoilMoistureReading,
    user: dict = Depends(get_current_user),
):
    """تسجيل قراءة مستشعر الرطوبة - Protected endpoint"""

    # Analyze reading
    if reading.moisture_percent < 25:
        status = "critical"
        action_ar = "🚨 ري فوري مطلوب!"
        action_en = "🚨 Immediate irrigation required!"
    elif reading.moisture_percent < 40:
        status = "low"
        action_ar = "⚠️ جدولة ري خلال 24 ساعة"
        action_en = "⚠️ Schedule irrigation within 24 hours"
    elif reading.moisture_percent < 70:
        status = "optimal"
        action_ar = "✅ مستوى الرطوبة مثالي"
        action_en = "✅ Moisture level is optimal"
    else:
        status = "high"
        action_ar = "💧 رطوبة عالية - تقليل الري"
        action_en = "💧 High moisture - reduce irrigation"

    return {
        "reading_id": str(uuid.uuid4()),
        "field_id": reading.field_id,
        "sensor_id": reading.sensor_id,
        "moisture_percent": reading.moisture_percent,
        "status": status,
        "action_ar": action_ar,
        "action_en": action_en,
        "recorded_at": datetime.now(UTC).isoformat(),
    }


@app.post("/v1/irrigation-executed")
async def record_irrigation_executed(
    execution: IrrigationExecution,
    user: dict = Depends(get_current_user),
):
    """
    تسجيل تنفيذ الري - Record completed irrigation event (Protected endpoint)

    This endpoint records when irrigation has actually been executed
    and publishes an event for downstream services.
    """
    execution_id = str(uuid.uuid4())
    executed_at = execution.executed_at or datetime.now(UTC)

    # Publish irrigation executed event
    await publish_event(
        subject="sahool.irrigation.executed",
        data={
            "execution_id": execution_id,
            "field_id": execution.field_id,
            "plan_id": execution.plan_id,
            "schedule_id": execution.schedule_id,
            "amount_mm": execution.amount_mm,
            "duration_minutes": execution.duration_minutes,
            "method": execution.method.value,
            "timestamp": executed_at.isoformat(),
        },
    )

    return {
        "execution_id": execution_id,
        "field_id": execution.field_id,
        "plan_id": execution.plan_id,
        "schedule_id": execution.schedule_id,
        "amount_mm": execution.amount_mm,
        "duration_minutes": execution.duration_minutes,
        "method": execution.method.value,
        "method_ar": METHOD_TRANSLATIONS[execution.method],
        "executed_at": executed_at.isoformat(),
        "status": "recorded",
        "message_ar": "✅ تم تسجيل عملية الري بنجاح",
        "message_en": "✅ Irrigation execution recorded successfully",
    }


@app.get("/v1/efficiency-report/{field_id}")
def get_efficiency_report(
    field_id: str,
    current_method: IrrigationMethod = IrrigationMethod.TRADITIONAL,
    area_hectares: float = Query(default=1.0, gt=0),
    user: dict = Depends(get_current_user),
):
    """تقرير كفاءة الري ومقارنة الطرق - Protected endpoint"""

    # Annual water usage estimates (m³/ha/year)
    annual_water_by_method = {
        IrrigationMethod.DRIP: 4500,
        IrrigationMethod.SPRINKLER: 6000,
        IrrigationMethod.FURROW: 7500,
        IrrigationMethod.FLOOD: 9000,
        IrrigationMethod.TRADITIONAL: 10000,
    }

    current_water = annual_water_by_method[current_method] * area_hectares
    current_cost = current_water * WATER_COST_PER_M3

    comparisons = []
    for method, water in annual_water_by_method.items():
        method_water = water * area_hectares
        method_cost = method_water * WATER_COST_PER_M3

        if method != current_method:
            water_saved = current_water - method_water
            cost_saved = current_cost - method_cost
            savings_percent = (water_saved / current_water) * 100 if current_water > 0 else 0

            comparisons.append(
                {
                    "method": method.value,
                    "method_ar": METHOD_TRANSLATIONS[method],
                    "efficiency_percent": int(IRRIGATION_EFFICIENCY[method] * 100),
                    "annual_water_m3": round(method_water, 0),
                    "annual_cost_yer": round(method_cost, 0),
                    "water_saved_m3": round(water_saved, 0),
                    "cost_saved_yer": round(cost_saved, 0),
                    "savings_percent": round(savings_percent, 1),
                }
            )

    # Sort by water saved
    comparisons.sort(key=lambda x: x["water_saved_m3"], reverse=True)

    return {
        "field_id": field_id,
        "area_hectares": area_hectares,
        "current_method": {
            "method": current_method.value,
            "method_ar": METHOD_TRANSLATIONS[current_method],
            "efficiency_percent": int(IRRIGATION_EFFICIENCY[current_method] * 100),
            "annual_water_m3": round(current_water, 0),
            "annual_cost_yer": round(current_cost, 0),
        },
        "alternatives": comparisons,
        "recommendation_ar": (
            f"💡 التحويل إلى الري بالتنقيط يوفر {comparisons[0]['water_saved_m3']} م³ سنوياً ({comparisons[0]['savings_percent']}%)"
            if comparisons
            else "✅ أنت تستخدم أكفأ طريقة"
        ),
        "roi_months": (
            round(50000 / (comparisons[0]["cost_saved_yer"] / 12), 0)
            if comparisons and comparisons[0]["cost_saved_yer"] > 0
            else None
        ),
    }


# =============================================================================
# Field-First: Action Template Endpoints
# =============================================================================


def _convert_urgency(urgency: UrgencyLevel) -> "ActionUrgency":
    """Convert local UrgencyLevel to ActionTemplate UrgencyLevel"""
    if not ACTION_TEMPLATE_AVAILABLE:
        return None
    mapping = {
        UrgencyLevel.LOW: ActionUrgency.LOW,
        UrgencyLevel.MEDIUM: ActionUrgency.MEDIUM,
        UrgencyLevel.HIGH: ActionUrgency.HIGH,
        UrgencyLevel.CRITICAL: ActionUrgency.CRITICAL,
    }
    return mapping.get(urgency, ActionUrgency.MEDIUM)


@app.post("/v1/calculate-with-action")
async def calculate_irrigation_with_action(
    request: IrrigationRequest,
    user: dict = Depends(get_current_user),
):
    """
    حساب احتياجات الري مع ActionTemplate - Protected endpoint

    Field-First: هذا الـ endpoint يُنتج قالب إجراء قابل للتنفيذ
    بدون اتصال، مع خطوات واضحة وموارد محددة.
    """
    # Get the regular irrigation plan
    plan = await calculate_irrigation(request, user)

    # If ActionTemplate not available, return plan only
    if not ACTION_TEMPLATE_AVAILABLE:
        return {
            "plan": plan,
            "action_template": None,
            "action_template_available": False,
        }

    # Get the first (most urgent) schedule
    if plan.schedules:
        schedule = plan.schedules[0]

        # Create ActionTemplate using factory
        action = ActionTemplateFactory.create_irrigation_action(
            field_id=request.field_id,
            water_amount_liters=schedule.water_amount_liters,
            duration_minutes=schedule.duration_minutes,
            urgency=_convert_urgency(schedule.urgency),
            confidence=0.85 + (0.1 if request.current_soil_moisture else 0),
            soil_moisture_percent=request.current_soil_moisture,
            source_analysis_id=plan.plan_id,
            method=request.irrigation_method.value,
            deadline=datetime.combine(schedule.irrigation_date, time(18, 0)),
        )

        # Calculate priority
        action.calculate_priority_score()

        return {
            "plan": plan,
            "action_template": action.model_dump(),
            "action_template_available": True,
            "task_card": action.to_task_card(),
            "notification_payload": action.to_notification_payload(),
        }

    return {
        "plan": plan,
        "action_template": None,
        "action_template_available": True,
        "message": "No irrigation needed at this time",
    }


@app.post("/v1/sensor-reading-with-action")
def record_sensor_reading_with_action(
    reading: SoilMoistureReading,
    user: dict = Depends(get_current_user),
):
    """
    تسجيل قراءة مستشعر الرطوبة مع ActionTemplate - Protected endpoint

    Field-First: إذا كانت الرطوبة منخفضة، يُنتج إجراء ري
    """
    # Get the regular sensor reading response
    result = record_sensor_reading(reading, user)

    # If ActionTemplate not available or moisture is OK, return as-is
    if not ACTION_TEMPLATE_AVAILABLE or result["status"] not in ["critical", "low"]:
        return {
            **result,
            "action_template": None,
        }

    # Create irrigation action for low moisture
    if result["status"] == "critical":
        urgency = ActionUrgency.CRITICAL
        water_liters = 5000  # Emergency irrigation
        duration = 60
    else:
        urgency = ActionUrgency.HIGH
        water_liters = 3000
        duration = 45

    action = ActionTemplateFactory.create_irrigation_action(
        field_id=reading.field_id,
        water_amount_liters=water_liters,
        duration_minutes=duration,
        urgency=urgency,
        confidence=0.92,  # High confidence from sensor
        soil_moisture_percent=reading.moisture_percent,
        source_analysis_id=result["reading_id"],
        method="drip",
    )

    action.calculate_priority_score()

    return {
        **result,
        "action_template": action.model_dump(),
        "task_card": action.to_task_card(),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8094))
    uvicorn.run(app, host="0.0.0.0", port=port)
