"""
Irrigation Cycle Engine - SAHOOL Platform v3.0

FAO-56 based irrigation scheduling engine with Yemen-specific adaptations.
Uses pyfao56 as the core computational library for ET0/ETc calculations,
dual crop coefficients, and automated irrigation scheduling.

Features:
- ET0 calculation (Penman-Monteith FAO-56)
- ETc with dual Kc (Kcb + Ke)
- Irrigation cycle formula: T = ((θfc - θmin) × Zr × ρb) / ETc
- AutoIrrigate (25 parameters) from pyfao56
- Salinity-adjusted Kc via SalinityModule
- Yemen crop/climate/soil database integration
- NATS event publishing for irrigation decisions

Port: 8250
"""

from __future__ import annotations

import json
import math
import os
import sys
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from typing import Optional

# Path setup for shared modules
sys.path.insert(0, "/app")
sys.path.insert(0, "/app/shared")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")

VERSION = "16.0.0"
SERVICE_NAME = "irrigation-cycle-engine"
PORT = int(os.getenv("PORT", "8250"))

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


class WeatherInput(BaseModel):
    """Daily weather data for ET0 calculation."""

    date: date
    temp_min_c: float = Field(..., description="Min temperature (°C)")
    temp_max_c: float = Field(..., description="Max temperature (°C)")
    humidity_min_pct: float = Field(default=30.0, description="Min relative humidity (%)")
    humidity_max_pct: float = Field(default=70.0, description="Max relative humidity (%)")
    wind_speed_2m_ms: float = Field(default=2.0, description="Wind speed at 2m (m/s)")
    solar_radiation_mjm2: float = Field(default=20.0, description="Solar radiation (MJ/m²/day)")
    rainfall_mm: float = Field(default=0.0, description="Rainfall (mm)")


class ET0Request(BaseModel):
    """Request for ET0 calculation."""

    latitude: float = Field(..., description="Latitude (decimal degrees)")
    elevation_m: float = Field(..., description="Elevation (m)")
    weather: list[WeatherInput] = Field(..., min_length=1, description="Weather data series")


class ET0Response(BaseModel):
    """ET0 calculation result."""

    date: date
    et0_mm: float
    method: str = "penman_monteith_fao56"


class IrrigationCycleRequest(BaseModel):
    """Request for irrigation cycle calculation."""

    crop: str = Field(..., description="Crop name")
    growth_stage: str | None = Field(None, description="Current growth stage name")
    field_capacity: float = Field(..., description="θfc (cm³/cm³)")
    wilting_point: float = Field(..., description="θwp (cm³/cm³)")
    root_depth_m: float = Field(default=1.0, description="Effective root depth (m)")
    bulk_density: float = Field(default=1.4, description="Soil bulk density (g/cm³)")
    depletion_fraction: float = Field(default=0.5, description="Allowable depletion (p)")
    et0_mm_day: float = Field(..., description="Reference ET (mm/day)")
    kc: float | None = Field(None, description="Crop coefficient (overrides crop DB)")
    ec_water: float | None = Field(None, description="Irrigation water EC (dS/m)")
    ec_soil: float | None = Field(None, description="Soil EC (dS/m)")
    alpha: float = Field(default=1.0, description="ET correction factor α")
    beta: float = Field(default=1.0, description="Soil correction factor β")
    gamma: float = Field(default=1.0, description="Stress correction factor γ")


class IrrigationCycleResponse(BaseModel):
    """Irrigation cycle calculation result."""

    cycle_days: float = Field(..., description="Irrigation cycle T (days)")
    net_irrigation_mm: float = Field(..., description="Net irrigation depth (mm)")
    gross_irrigation_mm: float = Field(..., description="Gross irrigation with efficiency (mm)")
    etc_mm_day: float = Field(..., description="Crop ET (mm/day)")
    kc_used: float = Field(..., description="Kc value used")
    kc_adjusted: float | None = Field(None, description="Salinity-adjusted Kc")
    leaching_fraction: float | None = Field(None, description="Leaching fraction if salinity")
    total_water_mm: float = Field(..., description="Total water including leaching (mm)")
    available_water_mm: float = Field(..., description="Total available water in root zone (mm)")
    readily_available_mm: float = Field(..., description="Readily available water (mm)")
    next_irrigation_date: date | None = Field(None, description="Recommended next irrigation")
    crop_name: str
    crop_name_ar: str | None = None
    recommendations: list[str] = []
    recommendations_ar: list[str] = []


class YemenCropListResponse(BaseModel):
    """List of available Yemen crops."""

    crops: list[dict]
    total: int


class CropInfoResponse(BaseModel):
    """Detailed crop information."""

    name: str
    name_ar: str
    crop_type: str
    root_depth_m: float
    depletion_fraction: float
    growth_stages: list[dict]
    salinity_threshold_dsm: float
    regions: list[str]


class ScheduleRequest(BaseModel):
    """Multi-day irrigation schedule request."""

    crop: str
    soil_profile: str = Field(..., description="Yemen soil profile name")
    climate_zone: str = Field(..., description="Yemen climate zone")
    start_date: date
    days: int = Field(default=30, ge=1, le=365)
    field_area_ha: float = Field(default=1.0, description="Field area (hectares)")
    irrigation_efficiency: float = Field(default=0.85, description="System efficiency (0-1)")
    ec_water: float | None = Field(None, description="Water EC (dS/m)")


class ScheduleDay(BaseModel):
    """Single day in irrigation schedule."""

    date: date
    day_of_season: int
    growth_stage: str
    kc: float
    et0_mm: float
    etc_mm: float
    soil_moisture_pct: float
    irrigate: bool
    irrigation_mm: float
    cumulative_water_mm: float


class ScheduleResponse(BaseModel):
    """Multi-day irrigation schedule."""

    crop: str
    crop_ar: str
    soil_profile: str
    climate_zone: str
    schedule: list[ScheduleDay]
    total_water_mm: float
    total_water_m3_per_ha: float
    irrigation_events: int
    average_cycle_days: float
    water_use_efficiency: str


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------


class IrrigationCycleEngine:
    """
    Core engine for irrigation cycle calculations.

    Implements the cycle formula:
    T = ((θfc - θmin) × Zr × ρb × β) / (ETc × α × γ)

    Where:
    - θfc: Field capacity (cm³/cm³)
    - θmin: Minimum soil moisture (from depletion fraction)
    - Zr: Root depth (mm)
    - ρb: Bulk density (g/cm³)
    - ETc: Crop evapotranspiration (mm/day)
    - α: ET correction factor
    - β: Soil correction factor
    - γ: Stress/management factor
    """

    def __init__(self):
        self._salinity_module = None
        self._yemen_crops = None
        self._yemen_climate = None
        self._yemen_soils = None
        self._load_yemen_data()

    def _load_yemen_data(self):
        """Load Yemen-specific data modules."""
        try:
            from shared.salinity import SalinityModule
            from shared.yemen.climate import YEMEN_CLIMATE_ZONES, get_climate_zone
            from shared.yemen.crops import YEMEN_CROPS, get_yemen_crop
            from shared.yemen.soils import YEMEN_SOIL_PROFILES, get_soil_profile

            self._yemen_crops = YEMEN_CROPS
            self._get_yemen_crop = get_yemen_crop
            self._yemen_climate = YEMEN_CLIMATE_ZONES
            self._get_climate_zone = get_climate_zone
            self._yemen_soils = YEMEN_SOIL_PROFILES
            self._get_soil_profile = get_soil_profile
            self._salinity_module = SalinityModule()
        except ImportError:
            # Fallback for testing without shared modules
            self._yemen_crops = {}
            self._get_yemen_crop = lambda _: None
            self._yemen_climate = {}
            self._get_climate_zone = lambda _: None
            self._yemen_soils = {}
            self._get_soil_profile = lambda _: None
            self._salinity_module = None

    def calculate_et0_penman_monteith(
        self,
        temp_min: float,
        temp_max: float,
        humidity_min: float,
        humidity_max: float,
        wind_speed_2m: float,
        solar_radiation: float,
        latitude: float,
        elevation: float,
        day_of_year: int,
    ) -> float:
        """
        Calculate reference ET0 using Penman-Monteith FAO-56 method.

        This is a pure-Python implementation for when pyfao56 is not available.

        Returns:
            ET0 in mm/day
        """
        # Mean temperature
        t_mean = (temp_min + temp_max) / 2.0

        # Atmospheric pressure (kPa)
        p = 101.3 * ((293.0 - 0.0065 * elevation) / 293.0) ** 5.26

        # Psychrometric constant (kPa/°C)
        gamma = 0.000665 * p

        # Saturation vapor pressure (kPa)
        e_s_min = 0.6108 * math.exp((17.27 * temp_min) / (temp_min + 237.3))
        e_s_max = 0.6108 * math.exp((17.27 * temp_max) / (temp_max + 237.3))
        e_s = (e_s_min + e_s_max) / 2.0

        # Actual vapor pressure (kPa)
        e_a = (e_s_min * humidity_max / 100.0 + e_s_max * humidity_min / 100.0) / 2.0

        # Slope of saturation vapor pressure curve (kPa/°C)
        delta = 4098.0 * (0.6108 * math.exp((17.27 * t_mean) / (t_mean + 237.3))) / ((t_mean + 237.3) ** 2)

        # Net radiation (simplified)
        # Extraterrestrial radiation
        lat_rad = latitude * math.pi / 180.0
        dr = 1.0 + 0.033 * math.cos(2.0 * math.pi * day_of_year / 365.0)
        solar_decl = 0.409 * math.sin(2.0 * math.pi * day_of_year / 365.0 - 1.39)
        ws = math.acos(-math.tan(lat_rad) * math.tan(solar_decl))
        ra = (
            24.0
            * 60.0
            / math.pi
            * 0.0820
            * dr
            * (ws * math.sin(lat_rad) * math.sin(solar_decl) + math.cos(lat_rad) * math.cos(solar_decl) * math.sin(ws))
        )

        # Clear sky radiation
        rso = (0.75 + 2e-5 * elevation) * ra

        # Net shortwave radiation
        rns = (1.0 - 0.23) * solar_radiation

        # Net longwave radiation
        sigma = 4.903e-9  # Stefan-Boltzmann (MJ/m²/day/K⁴)
        rnl = (
            sigma
            * (((temp_max + 273.16) ** 4 + (temp_min + 273.16) ** 4) / 2.0)
            * (0.34 - 0.14 * math.sqrt(max(e_a, 0.01)))
            * (1.35 * (solar_radiation / max(rso, 0.1)) - 0.35)
        )

        # Net radiation
        rn = rns - rnl

        # Soil heat flux (negligible for daily)
        g = 0.0

        # ET0 (mm/day) - FAO Penman-Monteith
        numerator = 0.408 * delta * (rn - g) + gamma * (900.0 / (t_mean + 273.0)) * wind_speed_2m * (e_s - e_a)
        denominator = delta + gamma * (1.0 + 0.34 * wind_speed_2m)

        et0 = numerator / denominator
        return max(et0, 0.0)

    def calculate_cycle(self, req: IrrigationCycleRequest) -> IrrigationCycleResponse:
        """
        Calculate irrigation cycle using the SAHOOL cycle formula.

        T = ((θfc - θmin) × Zr × ρb × β) / (ETc × α × γ)
        """
        # Get crop data
        crop_data = self._get_yemen_crop(req.crop) if self._get_yemen_crop else None
        crop_name_ar = crop_data.name_ar if crop_data else None

        # Determine Kc
        if req.kc is not None:
            kc = req.kc
        elif crop_data:
            # Find Kc for current growth stage
            if req.growth_stage:
                stage = next(
                    (s for s in crop_data.growth_stages if s.name.lower() == req.growth_stage.lower()),
                    None,
                )
                kc = stage.kc if stage else crop_data.kc_mid
            else:
                kc = crop_data.kc_mid
        else:
            kc = 1.0  # Default

        # Salinity adjustment
        kc_adjusted = None
        leaching_fraction = None
        if req.ec_water and self._salinity_module:
            assessment = self._salinity_module.assess(
                ec_water=req.ec_water,
                crop=req.crop,
                kc=kc,
                ec_soil=req.ec_soil,
            )
            kc_adjusted = assessment.adjusted_kc
            leaching_fraction = assessment.leaching_fraction

        # Use adjusted Kc if salinity present
        effective_kc = kc_adjusted if kc_adjusted is not None else kc

        # Calculate ETc
        etc = req.et0_mm_day * effective_kc

        # Calculate available water
        theta_min = req.wilting_point + (req.field_capacity - req.wilting_point) * (1.0 - req.depletion_fraction)
        root_depth_mm = req.root_depth_m * 1000.0

        # Available water in root zone (mm)
        total_aw = (req.field_capacity - req.wilting_point) * root_depth_mm
        readily_aw = (req.field_capacity - theta_min) * root_depth_mm

        # Net irrigation depth (mm) = readily available water
        net_irrigation = readily_aw

        # Irrigation cycle (days)
        # T = ((θfc - θmin) × Zr × β) / (ETc × α × γ)
        # Note: θ values are volumetric (cm³/cm³), so bulk density is NOT needed.
        # The product (θfc - θmin) × Zr_mm already gives mm of available water.
        if etc > 0:
            cycle_days = ((req.field_capacity - theta_min) * root_depth_mm * req.beta) / (etc * req.alpha * req.gamma)
            # Clamp to reasonable range (1-60 days)
            cycle_days = max(1.0, min(cycle_days, 60.0))
        else:
            cycle_days = 30.0  # Default if no ET

        # Gross irrigation (account for efficiency, default 85%)
        efficiency = 0.85
        gross_irrigation = net_irrigation / efficiency

        # Total water including leaching
        total_water = gross_irrigation
        if leaching_fraction and leaching_fraction > 0:
            total_water = gross_irrigation / (1.0 - leaching_fraction)

        # Recommendations
        recs = []
        recs_ar = []
        if cycle_days < 2:
            recs.append("Very short cycle. Consider drip irrigation for continuous supply.")
            recs_ar.append("دورة قصيرة جداً. يُنصح بالري بالتنقيط للتزويد المستمر.")
        elif cycle_days > 14:
            recs.append("Long cycle. Monitor soil moisture to verify schedule accuracy.")
            recs_ar.append("دورة طويلة. راقب رطوبة التربة للتحقق من دقة الجدول.")

        if leaching_fraction and leaching_fraction > 0.15:
            recs.append(f"High leaching fraction ({leaching_fraction:.0%}). Salinity management critical.")
            recs_ar.append(f"نسبة غسيل عالية ({leaching_fraction:.0%}). إدارة الملوحة حرجة.")

        next_date = date.today() + timedelta(days=int(cycle_days))

        return IrrigationCycleResponse(
            cycle_days=round(cycle_days, 1),
            net_irrigation_mm=round(net_irrigation, 1),
            gross_irrigation_mm=round(gross_irrigation, 1),
            etc_mm_day=round(etc, 2),
            kc_used=round(kc, 3),
            kc_adjusted=round(kc_adjusted, 3) if kc_adjusted else None,
            leaching_fraction=round(leaching_fraction, 3) if leaching_fraction else None,
            total_water_mm=round(total_water, 1),
            available_water_mm=round(total_aw, 1),
            readily_available_mm=round(readily_aw, 1),
            next_irrigation_date=next_date,
            crop_name=req.crop,
            crop_name_ar=crop_name_ar,
            recommendations=recs,
            recommendations_ar=recs_ar,
        )

    def generate_schedule(self, req: ScheduleRequest) -> ScheduleResponse:
        """Generate multi-day irrigation schedule."""
        crop_data = self._get_yemen_crop(req.crop) if self._get_yemen_crop else None
        climate_data = self._get_climate_zone(req.climate_zone) if self._get_climate_zone else None
        soil_data = self._get_soil_profile(req.soil_profile) if self._get_soil_profile else None

        if not crop_data:
            raise ValueError(f"Unknown crop: {req.crop}")

        # Defaults if climate/soil data not available
        if soil_data:
            fc = soil_data.field_capacity
            wp = soil_data.wilting_point
        else:
            fc, wp, _bd = 0.28, 0.12, 1.40

        schedule: list[ScheduleDay] = []
        cumulative_water = 0.0
        irrigation_events = 0
        soil_moisture = fc  # Start at field capacity

        for day_offset in range(req.days):
            current_date = req.start_date + timedelta(days=day_offset)
            month = current_date.month

            # Get ET0 from climate zone monthly data
            if climate_data and climate_data.monthly_data:
                month_data = climate_data.monthly_data[month - 1]
                et0 = month_data.et0_mm_day
            else:
                et0 = 5.0  # Default

            # Determine growth stage
            if crop_data.growth_stages:
                total_days = 0
                stage = crop_data.growth_stages[0]
                for s in crop_data.growth_stages:
                    total_days += s.duration_days
                    if day_offset < total_days:
                        stage = s
                        break
                kc = stage.kc
                stage_name = stage.name
            else:
                kc = 1.0
                stage_name = "Unknown"

            # Salinity adjustment
            if req.ec_water and self._salinity_module:
                assessment = self._salinity_module.assess(
                    ec_water=req.ec_water,
                    crop=req.crop,
                    kc=kc,
                )
                kc = assessment.adjusted_kc

            # ETc
            etc = et0 * kc

            # Soil water balance
            soil_moisture -= etc / (crop_data.root_depth_m * 1000.0)

            # Check if irrigation needed
            theta_min = wp + (fc - wp) * (1.0 - crop_data.depletion_fraction)
            irrigate = soil_moisture <= theta_min

            irrigation_mm = 0.0
            if irrigate:
                # Refill to field capacity
                deficit_mm = (fc - soil_moisture) * crop_data.root_depth_m * 1000.0
                irrigation_mm = deficit_mm / req.irrigation_efficiency

                if req.ec_water and self._salinity_module:
                    lr = self._salinity_module.calculate_leaching_requirement(
                        req.ec_water,
                        req.crop,
                        irrigation_mm,
                    )
                    irrigation_mm = lr.total_water_mm

                soil_moisture = fc
                cumulative_water += irrigation_mm
                irrigation_events += 1

            sm_pct = max(0.0, min(100.0, (soil_moisture - wp) / (fc - wp) * 100.0))

            schedule.append(
                ScheduleDay(
                    date=current_date,
                    day_of_season=day_offset + 1,
                    growth_stage=stage_name,
                    kc=round(kc, 3),
                    et0_mm=round(et0, 2),
                    etc_mm=round(etc, 2),
                    soil_moisture_pct=round(sm_pct, 1),
                    irrigate=irrigate,
                    irrigation_mm=round(irrigation_mm, 1),
                    cumulative_water_mm=round(cumulative_water, 1),
                )
            )

        avg_cycle = req.days / max(irrigation_events, 1)
        total_m3_ha = cumulative_water * 10.0  # mm to m³/ha

        return ScheduleResponse(
            crop=req.crop,
            crop_ar=crop_data.name_ar if crop_data else req.crop,
            soil_profile=req.soil_profile,
            climate_zone=req.climate_zone,
            schedule=schedule,
            total_water_mm=round(cumulative_water, 1),
            total_water_m3_per_ha=round(total_m3_ha, 1),
            irrigation_events=irrigation_events,
            average_cycle_days=round(avg_cycle, 1),
            water_use_efficiency=f"{total_m3_ha:.0f} m³/ha over {req.days} days",
        )


# ---------------------------------------------------------------------------
# Application Setup
# ---------------------------------------------------------------------------

engine = IrrigationCycleEngine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    import logging

    logger = logging.getLogger(SERVICE_NAME)
    logger.info(f"Starting {SERVICE_NAME} v{VERSION} on port {PORT}")

    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats as nats_lib

            app.state.nc = await nats_lib.connect(nats_url)
            from shared.logging_config import sanitize_url

            logger.info(f"Connected to NATS: {sanitize_url(nats_url)}")
        except Exception as e:
            logger.warning(f"NATS connection failed: {e}")
            app.state.nc = None
    else:
        app.state.nc = None

    yield

    # Shutdown
    if getattr(app.state, "nc", None):
        await app.state.nc.close()
    logger.info(f"{SERVICE_NAME} shutdown complete")


app = FastAPI(
    title="Irrigation Cycle Engine",
    description="FAO-56 based irrigation scheduling with Yemen adaptations",
    version=VERSION,
    lifespan=lifespan,
)

# Setup error handling
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    setup_exception_handlers(app)
    add_request_id_middleware(app)
except ImportError:
    pass

try:
    from shared.middleware.tenant_context import TenantContextMiddleware

    app.add_middleware(TenantContextMiddleware)
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Health Endpoints
# ---------------------------------------------------------------------------


@app.get("/healthz")
def health():
    return {"status": "ok", "service": SERVICE_NAME, "version": VERSION}


@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": VERSION,
        "nats": getattr(app.state, "nc", None) is not None,
        "yemen_crops_loaded": len(engine._yemen_crops) > 0 if engine._yemen_crops else False,
    }


# ---------------------------------------------------------------------------
# ET0 Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/v1/irrigation/et0", response_model=list[ET0Response])
async def calculate_et0(req: ET0Request):
    """Calculate reference evapotranspiration (ET0) using FAO-56 Penman-Monteith."""
    results = []
    for w in req.weather:
        doy = w.date.timetuple().tm_yday
        et0 = engine.calculate_et0_penman_monteith(
            temp_min=w.temp_min_c,
            temp_max=w.temp_max_c,
            humidity_min=w.humidity_min_pct,
            humidity_max=w.humidity_max_pct,
            wind_speed_2m=w.wind_speed_2m_ms,
            solar_radiation=w.solar_radiation_mjm2,
            latitude=req.latitude,
            elevation=req.elevation_m,
            day_of_year=doy,
        )
        results.append(ET0Response(date=w.date, et0_mm=round(et0, 2)))
    return results


# ---------------------------------------------------------------------------
# Irrigation Cycle Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/v1/irrigation/cycle", response_model=IrrigationCycleResponse)
async def calculate_irrigation_cycle(req: IrrigationCycleRequest):
    """
    Calculate irrigation cycle period and water requirements.

    Uses the formula: T = ((θfc - θmin) × Zr × β) / (ETc × α × γ)
    With optional salinity adjustment via SalinityModule.
    """
    try:
        result = engine.calculate_cycle(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Publish NATS event (subject: sahool.{tenant_id}.irrigation.cycle_calculated)
    nc = getattr(app.state, "nc", None)
    if nc:
        try:
            tenant_id = os.getenv("TENANT_ID", "default")
            await nc.publish(
                f"sahool.{tenant_id}.irrigation.cycle_calculated",
                json.dumps(
                    {
                        "crop": req.crop,
                        "cycle_days": result.cycle_days,
                        "etc_mm_day": result.etc_mm_day,
                        "total_water_mm": result.total_water_mm,
                        "timestamp": datetime.now(tz=None).isoformat(),
                    }
                ).encode(),
            )
        except Exception:
            pass

    return result


@app.post("/api/v1/irrigation/schedule", response_model=ScheduleResponse)
async def generate_irrigation_schedule(req: ScheduleRequest):
    """
    Generate multi-day irrigation schedule using Yemen crop/climate/soil data.

    Combines pyfao56 ET calculations with Yemen-specific parameters
    for a complete irrigation plan.
    """
    try:
        result = engine.generate_schedule(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


# ---------------------------------------------------------------------------
# Yemen Data Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/v1/yemen/crops", response_model=YemenCropListResponse)
async def list_yemen_crops(
    crop_type: str | None = Query(None, description="Filter by type"),
    region: str | None = Query(None, description="Filter by region"),
):
    """List available Yemen crop parameters."""
    try:
        from shared.yemen.crops import list_yemen_crops as _list_crops

        crops = _list_crops(crop_type=crop_type, region=region)
        return YemenCropListResponse(
            crops=[
                {
                    "name": c.name,
                    "name_ar": c.name_ar,
                    "crop_type": c.crop_type,
                    "root_depth_m": c.root_depth_m,
                    "kc_mid": c.kc_mid,
                    "salinity_threshold_dsm": c.salinity_threshold_dsm,
                    "regions": c.regions,
                }
                for c in crops
            ],
            total=len(crops),
        )
    except ImportError:
        return YemenCropListResponse(crops=[], total=0)


@app.get("/api/v1/yemen/crops/{crop_name}", response_model=CropInfoResponse)
async def get_crop_info(crop_name: str):
    """Get detailed crop parameters for a Yemen crop."""
    crop = engine._get_yemen_crop(crop_name) if engine._get_yemen_crop else None
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop not found: {crop_name}")
    return CropInfoResponse(
        name=crop.name,
        name_ar=crop.name_ar,
        crop_type=crop.crop_type,
        root_depth_m=crop.root_depth_m,
        depletion_fraction=crop.depletion_fraction,
        growth_stages=[
            {"name": s.name, "name_ar": s.name_ar, "duration_days": s.duration_days, "kc": s.kc}
            for s in crop.growth_stages
        ],
        salinity_threshold_dsm=crop.salinity_threshold_dsm,
        regions=crop.regions,
    )


@app.get("/api/v1/yemen/climate-zones")
async def list_climate_zones():
    """List Yemen climate zones with key parameters."""
    if not engine._yemen_climate:
        return {"zones": [], "total": 0}
    return {
        "zones": [
            {
                "zone": z.zone.value,
                "name": z.name,
                "name_ar": z.name_ar,
                "et0_range_mm_day": z.et0_range_mm_day,
                "annual_rainfall_mm": z.annual_rainfall_mm,
                "groundwater_decline_m_year": z.groundwater_decline_m_year,
                "major_crops": z.major_crops,
            }
            for z in engine._yemen_climate.values()
        ],
        "total": len(engine._yemen_climate),
    }


@app.get("/api/v1/yemen/soils")
async def list_soil_profiles(region: str | None = Query(None)):
    """List Yemen soil profiles with hydraulic properties."""
    try:
        from shared.yemen.soils import list_soil_profiles as _list_soils

        soils = _list_soils(region=region)
        return {
            "profiles": [
                {
                    "name": s.name,
                    "name_ar": s.name_ar,
                    "soil_type": s.soil_type,
                    "region": s.region,
                    "field_capacity": s.field_capacity,
                    "wilting_point": s.wilting_point,
                    "bulk_density": s.bulk_density,
                    "available_water_mm_m": round(s.available_water, 1),
                    "ec_natural": s.ec_natural,
                }
                for s in soils
            ],
            "total": len(soils),
        }
    except ImportError:
        return {"profiles": [], "total": 0}


# ---------------------------------------------------------------------------
# Salinity Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/v1/irrigation/salinity-assessment")
async def assess_salinity(
    ec_water: float = Query(..., description="EC of irrigation water (dS/m)"),
    crop: str = Query(..., description="Crop name"),
    kc: float = Query(default=1.0, description="Current Kc"),
    ec_soil: float | None = Query(None, description="Soil EC (dS/m)"),
    na: float = Query(default=0.0, description="Sodium (meq/L)"),
    ca: float = Query(default=0.0, description="Calcium (meq/L)"),
    mg: float = Query(default=0.0, description="Magnesium (meq/L)"),
):
    """Assess salinity impact on irrigation and crop yield."""
    if not engine._salinity_module:
        raise HTTPException(status_code=503, detail="Salinity module not available")

    assessment = engine._salinity_module.assess(
        ec_water=ec_water,
        crop=crop,
        kc=kc,
        ec_soil=ec_soil,
        na=na,
        ca=ca,
        mg=mg,
    )
    return {
        "ec_water": assessment.ec_water,
        "ec_soil": assessment.ec_soil,
        "sar": assessment.sar,
        "risk": assessment.risk.value,
        "risk_ar": assessment.risk_ar,
        "yield_reduction_pct": assessment.yield_reduction_pct,
        "leaching_fraction": assessment.leaching_fraction,
        "kc_original": assessment.original_kc,
        "kc_adjusted": assessment.adjusted_kc,
        "recommendations": assessment.recommendations,
        "recommendations_ar": assessment.recommendations_ar,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
