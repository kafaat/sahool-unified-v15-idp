"""
Flight planning endpoints - نقاط نهاية تخطيط الرحلات
Integrates with shared.drone_integration for flight planning.
"""

import json
import uuid
from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

logger = structlog.get_logger()

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    _bearer_scheme = HTTPBearer(auto_error=False)
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}

router = APIRouter(prefix="/api/v1/flights", tags=["flight-planning"])

_flight_plans: dict[str, dict] = {}


class Coordinate(BaseModel):
    lat: float
    lng: float


class SprayFlightRequest(BaseModel):
    field_id: str
    boundary: list[Coordinate]
    spray_rate_l_ha: float = 10.0
    swath_width_m: float = 5.0
    altitude_m: float = 3.0
    name: str
    name_ar: str | None = None


class MappingFlightRequest(BaseModel):
    field_id: str
    boundary: list[Coordinate]
    gsd_cm_px: float = 2.0
    frontal_overlap: float = 80.0
    side_overlap: float = 70.0
    name: str
    name_ar: str | None = None


class WeatherCheckRequest(BaseModel):
    lat: float
    lng: float
    wind_speed_ms: float = 0.0
    temperature_c: float = 25.0
    humidity_percent: float = 50.0
    precipitation_mm: float = 0.0


class ResourceEstimateRequest(BaseModel):
    area_ha: float
    spray_rate_l_ha: float = 10.0
    tank_capacity_l: float = 20.0
    flight_time_per_tank_min: float = 15.0


@router.post("/plan/spray", status_code=201)
async def create_spray_flight_plan(request: SprayFlightRequest, req: Request, _user=Depends(get_current_user)):
    """Create spray flight plan - إنشاء خطة رحلة رش"""
    try:
        from shared.drone_integration import Coordinate as DCoord, create_spray_flight_plan

        boundary = [DCoord(lat=c.lat, lng=c.lng) for c in request.boundary]
        result = create_spray_flight_plan(
            boundary=boundary,
            spray_rate_l_ha=request.spray_rate_l_ha,
            swath_width_m=request.swath_width_m,
            altitude_m=request.altitude_m,
            name=request.name,
            name_ar=request.name_ar,
        )

        plan_id = f"FP-{uuid.uuid4().hex[:8].upper()}"
        plan_data = {
            "id": plan_id,
            "field_id": request.field_id,
            "type": "spray",
            "name": request.name,
            "name_ar": request.name_ar,
            "success": result.success,
            "total_distance_m": result.total_distance_m,
            "estimated_duration_min": result.estimated_duration_min,
            "waypoints_count": len(result.flight_path.waypoints) if result.flight_path else 0,
            "total_spray_volume_l": getattr(result, "total_spray_volume_l", None),
            "area_ha": getattr(result, "area_ha", None),
            "created_at": datetime.utcnow().isoformat(),
        }
        _flight_plans[plan_id] = plan_data

        nc = getattr(req.app.state, "nc", None)
        if nc:
            await nc.publish("sahool.drone.flight_planned", json.dumps({"plan_id": plan_id, "type": "spray"}).encode())

        logger.info("spray_flight_planned", plan_id=plan_id, distance=result.total_distance_m)
        return plan_data
    except ImportError:
        raise HTTPException(status_code=503, detail={"error": "Flight planning module not available", "error_ar": "وحدة تخطيط الرحلات غير متوفرة"})


@router.post("/plan/mapping", status_code=201)
async def create_mapping_flight_plan(request: MappingFlightRequest, req: Request):
    """Create mapping flight plan - إنشاء خطة رحلة تصوير"""
    try:
        from shared.drone_integration import Coordinate as DCoord, create_mapping_flight_plan

        boundary = [DCoord(lat=c.lat, lng=c.lng) for c in request.boundary]
        result = create_mapping_flight_plan(
            boundary=boundary,
            gsd_cm_px=request.gsd_cm_px,
            frontal_overlap=request.frontal_overlap,
            side_overlap=request.side_overlap,
            name=request.name,
            name_ar=request.name_ar,
        )

        plan_id = f"FP-{uuid.uuid4().hex[:8].upper()}"
        plan_data = {
            "id": plan_id,
            "field_id": request.field_id,
            "type": "mapping",
            "name": request.name,
            "success": result.success,
            "total_distance_m": result.total_distance_m,
            "estimated_duration_min": result.estimated_duration_min,
            "waypoints_count": len(result.flight_path.waypoints) if result.flight_path else 0,
            "created_at": datetime.utcnow().isoformat(),
        }
        _flight_plans[plan_id] = plan_data
        logger.info("mapping_flight_planned", plan_id=plan_id)
        return plan_data
    except ImportError:
        raise HTTPException(status_code=503, detail={"error": "Flight planning module not available", "error_ar": "وحدة تخطيط الرحلات غير متوفرة"})


@router.post("/weather-check")
async def check_flight_weather(request: WeatherCheckRequest):
    """Check weather conditions for flight - فحص حالة الطقس للرحلة"""
    try:
        from shared.drone_integration import assess_flight_weather

        assessment = assess_flight_weather(
            wind_speed_ms=request.wind_speed_ms,
            temperature_c=request.temperature_c,
            humidity_percent=request.humidity_percent,
            precipitation_mm=request.precipitation_mm,
        )
        return {
            "safe_to_fly": assessment.safe_to_fly,
            "risk_level": assessment.risk_level,
            "warnings": assessment.warnings,
            "warnings_ar": getattr(assessment, "warnings_ar", []),
        }
    except ImportError:
        safe = request.wind_speed_ms < 8 and request.precipitation_mm == 0 and 5 < request.temperature_c < 45
        warnings = []
        if request.wind_speed_ms >= 8:
            warnings.append("Wind speed too high for safe flight")
        if request.precipitation_mm > 0:
            warnings.append("Active precipitation detected")
        return {"safe_to_fly": safe, "risk_level": "low" if safe else "high", "warnings": warnings}


@router.post("/estimate")
async def estimate_flight_resources(request: ResourceEstimateRequest):
    """Estimate flight resources - تقدير موارد الرحلة"""
    try:
        from shared.drone_integration import estimate_flight_resources

        estimate = estimate_flight_resources(
            area_ha=request.area_ha,
            spray_rate_l_ha=request.spray_rate_l_ha,
            tank_capacity_l=request.tank_capacity_l,
            flight_time_per_tank_min=request.flight_time_per_tank_min,
        )
        return {
            "area_ha": request.area_ha,
            "total_volume_l": estimate["total_volume_l"],
            "tank_fills": estimate["tank_fills"],
            "total_flight_time_min": estimate["total_flight_time_min"],
            "batteries_needed": estimate["batteries_needed"],
            "estimated_cost_factor": estimate["estimated_cost_factor"],
        }
    except ImportError:
        raise HTTPException(status_code=503, detail={"error": "Flight planning module not available", "error_ar": "وحدة تخطيط الرحلات غير متوفرة"})


@router.get("/plans")
async def list_flight_plans(field_id: str | None = None):
    """List flight plans - قائمة خطط الرحلات"""
    plans = list(_flight_plans.values())
    if field_id:
        plans = [p for p in plans if p.get("field_id") == field_id]
    return {"plans": plans, "count": len(plans)}


@router.get("/plans/{plan_id}")
async def get_flight_plan(plan_id: str):
    """Get flight plan details - تفاصيل خطة الرحلة"""
    if plan_id not in _flight_plans:
        raise HTTPException(status_code=404, detail={"error": "Plan not found", "error_ar": "الخطة غير موجودة"})
    return _flight_plans[plan_id]
