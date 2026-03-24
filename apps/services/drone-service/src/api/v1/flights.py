"""
Flight planning endpoints - نقاط نهاية تخطيط الرحلات
Integrates with shared.drone_integration for flight planning.
Supports database persistence with in-memory fallback.
"""

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

# Unified error handling
try:
    from shared.errors_py import NotFoundException
except ImportError:

    class NotFoundException(HTTPException):  # type: ignore[no-redef]
        """Fallback when shared.errors_py is unavailable."""

        def __init__(self, message: str = "", message_ar: str | None = None, resource_type: str | None = None, **_kw):
            detail = {"error": message}
            if message_ar:
                detail["error_ar"] = message_ar
            if resource_type:
                detail["resource_type"] = resource_type
            super().__init__(status_code=404, detail=detail)


# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    class User:  # type: ignore[no-redef]
        def __init__(self, **kw):
            self.id = kw.get("id", "anonymous")
            self.tenant_id = kw.get("tenant_id", "default")

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return User(id="anonymous", tenant_id="default")


logger = structlog.get_logger()


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


def _get_repo(req: Request):
    pool = getattr(req.app.state, "db_pool", None)
    if pool:
        from src.db import DroneRepository

        return DroneRepository(pool)
    return None


def _get_tenant_id(user) -> str:
    return getattr(user, "tenant_id", "default")


def _raise_plan_not_found():
    """Raise NotFoundException for missing flight plans."""
    raise NotFoundException("Plan not found", "الخطة غير موجودة", "flight_plan")


@router.post("/plan/spray", status_code=201)
async def create_spray_flight_plan(
    request: SprayFlightRequest,
    req: Request,
    user=Depends(get_current_user),
):
    """Create spray flight plan - إنشاء خطة رحلة رش"""
    try:
        from shared.drone_integration import Coordinate as DCoord
        from shared.drone_integration import create_spray_flight_plan
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail={"error": "Flight planning module not available", "error_ar": "وحدة تخطيط الرحلات غير متوفرة"},
        )

    tenant_id = _get_tenant_id(user)
    boundary = [DCoord(lat=c.lat, lng=c.lng) for c in request.boundary]
    result = create_spray_flight_plan(
        boundary=boundary,
        spray_rate_l_ha=request.spray_rate_l_ha,
        swath_width_m=request.swath_width_m,
        altitude_m=request.altitude_m,
        name=request.name,
        name_ar=request.name_ar,
    )

    waypoints_data = []
    if result.flight_path:
        waypoints_data = [
            {"lat": wp.coordinate.lat, "lng": wp.coordinate.lng, "alt": wp.coordinate.alt_agl_m}
            for wp in result.flight_path.waypoints
        ]

    plan_data = {
        "field_id": request.field_id,
        "name": request.name,
        "name_ar": request.name_ar,
        "plan_type": "spray",
        "success": result.success,
        "total_distance_m": result.total_distance_m,
        "estimated_duration_min": result.estimated_duration_min,
        "waypoints_count": len(waypoints_data),
        "total_spray_volume_l": getattr(result, "total_spray_volume_l", None),
        "area_ha": getattr(result, "coverage_area_ha", None),
        "waypoints": waypoints_data,
        "boundary": [{"lat": c.lat, "lng": c.lng} for c in request.boundary],
    }

    # Save to database or in-memory
    repo = _get_repo(req)
    if repo:
        row = await repo.create_flight_plan(tenant_id, plan_data)
        plan_id = str(row["id"])
    else:
        plan_id = f"FP-{uuid.uuid4().hex[:8].upper()}"
        plan_data["id"] = plan_id
        plan_data["tenant_id"] = tenant_id
        plan_data["created_at"] = datetime.now(UTC).isoformat()
        _flight_plans[plan_id] = plan_data

    # Publish NATS event
    try:
        from src.events import FLIGHT_PLANNED, publish_drone_event

        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(
            nc,
            FLIGHT_PLANNED,
            tenant_id,
            plan_id=plan_id,
            plan_type="spray",
            field_id=request.field_id,
            distance_m=result.total_distance_m,
        )
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("spray_flight_planned", plan_id=plan_id, distance=result.total_distance_m, tenant_id=tenant_id)

    return {
        "id": plan_id,
        "field_id": request.field_id,
        "type": "spray",
        "name": request.name,
        "success": result.success,
        "total_distance_m": result.total_distance_m,
        "estimated_duration_min": result.estimated_duration_min,
        "waypoints_count": len(waypoints_data),
        "total_spray_volume_l": getattr(result, "total_spray_volume_l", None),
        "warnings": result.warnings_en,
        "warnings_ar": result.warnings_ar,
    }


@router.post("/plan/mapping", status_code=201)
async def create_mapping_flight_plan(
    request: MappingFlightRequest,
    req: Request,
    user=Depends(get_current_user),
):
    """Create mapping flight plan - إنشاء خطة رحلة تصوير"""
    try:
        from shared.drone_integration import Coordinate as DCoord
        from shared.drone_integration import create_mapping_flight_plan
    except ImportError:
        raise HTTPException(
            status_code=503,
            detail={"error": "Flight planning module not available", "error_ar": "وحدة تخطيط الرحلات غير متوفرة"},
        )

    tenant_id = _get_tenant_id(user)
    boundary = [DCoord(lat=c.lat, lng=c.lng) for c in request.boundary]
    result = create_mapping_flight_plan(
        boundary=boundary,
        gsd_cm_px=request.gsd_cm_px,
        frontal_overlap=request.frontal_overlap,
        side_overlap=request.side_overlap,
        name=request.name,
        name_ar=request.name_ar,
    )

    waypoints_data = []
    if result.flight_path:
        waypoints_data = [
            {"lat": wp.coordinate.lat, "lng": wp.coordinate.lng, "alt": wp.coordinate.alt_agl_m}
            for wp in result.flight_path.waypoints
        ]

    plan_data = {
        "field_id": request.field_id,
        "name": request.name,
        "name_ar": request.name_ar,
        "plan_type": "mapping",
        "success": result.success,
        "total_distance_m": result.total_distance_m,
        "estimated_duration_min": result.estimated_duration_min,
        "waypoints_count": len(waypoints_data),
        "area_ha": getattr(result, "coverage_area_ha", None),
        "waypoints": waypoints_data,
        "boundary": [{"lat": c.lat, "lng": c.lng} for c in request.boundary],
    }

    repo = _get_repo(req)
    if repo:
        row = await repo.create_flight_plan(tenant_id, plan_data)
        plan_id = str(row["id"])
    else:
        plan_id = f"FP-{uuid.uuid4().hex[:8].upper()}"
        plan_data["id"] = plan_id
        plan_data["tenant_id"] = tenant_id
        plan_data["created_at"] = datetime.now(UTC).isoformat()
        _flight_plans[plan_id] = plan_data

    try:
        from src.events import FLIGHT_PLANNED, publish_drone_event

        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(
            nc,
            FLIGHT_PLANNED,
            tenant_id,
            plan_id=plan_id,
            plan_type="mapping",
            field_id=request.field_id,
        )
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("mapping_flight_planned", plan_id=plan_id, tenant_id=tenant_id)

    return {
        "id": plan_id,
        "field_id": request.field_id,
        "type": "mapping",
        "name": request.name,
        "success": result.success,
        "total_distance_m": result.total_distance_m,
        "estimated_duration_min": result.estimated_duration_min,
        "waypoints_count": len(waypoints_data),
        "estimated_photos": getattr(result, "estimated_photos", 0),
        "gsd_cm_px": getattr(result, "gsd_cm_px", 0),
        "warnings": result.warnings_en,
        "warnings_ar": result.warnings_ar,
    }


@router.post("/weather-check")
async def check_flight_weather(request: WeatherCheckRequest, user=Depends(get_current_user)):
    """Check weather conditions for flight - فحص حالة الطقس للرحلة"""
    try:
        from shared.drone_integration import assess_flight_weather

        assessment = assess_flight_weather(
            wind_speed_ms=request.wind_speed_ms,
            temperature_c=request.temperature_c,
            humidity_percent=request.humidity_percent,
            precipitation_mm=request.precipitation_mm,
            wind_direction_deg=0.0,
        )
        return {
            "safe_to_fly": assessment.can_fly,
            "condition": assessment.condition.value,
            "message": assessment.message_en,
            "message_ar": assessment.message_ar,
            "warnings": assessment.warnings_en,
            "warnings_ar": assessment.warnings_ar,
        }
    except ImportError:
        safe = request.wind_speed_ms < 8 and request.precipitation_mm == 0 and 5 < request.temperature_c < 45
        warnings_en = []
        warnings_ar = []
        if request.wind_speed_ms >= 8:
            warnings_en.append("Wind speed too high for safe flight")
            warnings_ar.append("سرعة الرياح عالية جداً للطيران الآمن")
        if request.precipitation_mm > 0:
            warnings_en.append("Active precipitation detected")
            warnings_ar.append("تم اكتشاف هطول نشط")
        if request.temperature_c <= 5 or request.temperature_c >= 45:
            warnings_en.append("Temperature outside safe operating range")
            warnings_ar.append("درجة الحرارة خارج النطاق الآمن للتشغيل")
        condition = "optimal" if safe and not warnings_en else ("prohibited" if not safe else "marginal")
        return {
            "safe_to_fly": safe,
            "condition": condition,
            "message": "Safe to fly" if safe else "Flight not recommended",
            "message_ar": "آمن للطيران" if safe else "الطيران غير مستحسن",
            "warnings": warnings_en,
            "warnings_ar": warnings_ar,
        }


@router.post("/estimate")
async def estimate_resources(request: ResourceEstimateRequest, user=Depends(get_current_user)):
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
        # Basic calculation fallback
        total_vol = request.area_ha * request.spray_rate_l_ha
        fills = max(1, int(total_vol / request.tank_capacity_l) + 1)
        flight_min = fills * request.flight_time_per_tank_min
        return {
            "area_ha": request.area_ha,
            "total_volume_l": round(total_vol, 1),
            "tank_fills": fills,
            "total_flight_time_min": round(flight_min, 1),
            "batteries_needed": max(1, fills),
            "estimated_cost_factor": round(request.area_ha * 1.5, 2),
        }


@router.get("/plans")
async def list_flight_plans(
    req: Request,
    field_id: str | None = None,
    plan_type: str | None = None,
    limit: int = 500,
    offset: int = 0,
    user=Depends(get_current_user),
):
    """List flight plans - قائمة خطط الرحلات"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        rows = await repo.list_flight_plans(
            tenant_id, field_id=field_id, plan_type=plan_type, limit=min(limit, 1000), offset=offset
        )
        plans = [{k: str(v) if k == "id" else v for k, v in r.items() if k != "waypoints"} for r in rows]
    else:
        plans = [p for p in _flight_plans.values() if p.get("tenant_id") == tenant_id]
        if field_id:
            plans = [p for p in plans if p.get("field_id") == field_id]
        if plan_type:
            plans = [p for p in plans if p.get("plan_type") == plan_type]

    return {"plans": plans, "count": len(plans)}


@router.get("/plans/{plan_id}")
async def get_flight_plan(plan_id: str, req: Request, user=Depends(get_current_user)):
    """Get flight plan details - تفاصيل خطة الرحلة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        row = await repo.get_flight_plan(plan_id, tenant_id)
        if not row:
            _raise_plan_not_found()
        return {k: str(v) if k == "id" else v for k, v in row.items()}

    if plan_id not in _flight_plans or _flight_plans[plan_id].get("tenant_id") != tenant_id:
        _raise_plan_not_found()
    return _flight_plans[plan_id]
