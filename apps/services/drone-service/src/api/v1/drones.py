"""
Drone management endpoints - نقاط نهاية إدارة الطائرات
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
            self.roles = kw.get("roles", [])

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return User(id="anonymous", tenant_id="default")


logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/drones", tags=["drones"])

# In-memory fallback when database is unavailable
_drones: dict[str, dict] = {}


class DroneCreate(BaseModel):
    name: str
    name_ar: str | None = None
    model: str
    serial_number: str
    drone_type: str = "custom"
    max_payload_kg: float | None = None
    tank_capacity_l: float | None = None
    max_flight_time_min: float | None = None


class DroneResponse(BaseModel):
    id: str
    name: str
    name_ar: str | None = None
    model: str
    serial_number: str
    drone_type: str
    status: str = "active"
    tenant_id: str | None = None


def _get_repo(req: Request):
    """Get DroneRepository if DB is available."""
    pool = getattr(req.app.state, "db_pool", None)
    if pool:
        from src.db import DroneRepository

        return DroneRepository(pool)
    return None


def _get_tenant_id(user) -> str:
    """Extract tenant_id from user object."""
    return getattr(user, "tenant_id", "default")


def _raise_not_found(resource: str = "Drone", resource_ar: str = "الطائرة"):
    """Raise NotFoundException (platform or fallback)."""
    raise NotFoundException(
        f"{resource} not found",
        f"{resource_ar} غير موجودة",
        "drone",
    )


def _drone_to_response(d: dict) -> dict:
    """Map DB row or in-memory dict to DroneResponse fields."""
    return {k: str(d[k]) if k == "id" else d[k] for k in DroneResponse.model_fields if k in d}


@router.get("/", response_model=list[DroneResponse])
async def list_drones(
    req: Request,
    status: str | None = None,
    user=Depends(get_current_user),
):
    """List all registered drones - قائمة بجميع الطائرات المسجلة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)
    if repo:
        rows = await repo.list_drones(tenant_id, status=status)
        return [DroneResponse(**_drone_to_response(r)) for r in rows]

    # In-memory fallback
    drones = [d for d in _drones.values() if d.get("tenant_id") == tenant_id]
    if status:
        drones = [d for d in drones if d.get("status") == status]
    return [DroneResponse(**_drone_to_response(d)) for d in drones]


@router.post("/", response_model=DroneResponse, status_code=201)
async def register_drone(drone: DroneCreate, req: Request, user=Depends(get_current_user)):
    """Register a new drone - تسجيل طائرة جديدة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        row = await repo.create_drone(tenant_id, drone.model_dump())
        result = DroneResponse(**_drone_to_response(row))
    else:
        drone_id = f"DRN-{uuid.uuid4().hex[:8].upper()}"
        drone_data = {
            "id": drone_id,
            "tenant_id": tenant_id,
            **drone.model_dump(),
            "status": "active",
            "battery_percent": 100,
            "total_flight_hours": 0.0,
            "registered_at": datetime.now(UTC).isoformat(),
        }
        _drones[drone_id] = drone_data
        result = DroneResponse(**_drone_to_response(drone_data))

    # Publish NATS event
    try:
        from src.events import DRONE_REGISTERED, publish_drone_event

        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(
            nc,
            DRONE_REGISTERED,
            tenant_id,
            drone_id=result.id,
            model=drone.model,
            serial_number=drone.serial_number,
        )
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("drone_registered", drone_id=result.id, model=drone.model, tenant_id=tenant_id)
    return result


@router.get("/{drone_id}", response_model=DroneResponse)
async def get_drone(drone_id: str, req: Request, user=Depends(get_current_user)):
    """Get drone details - الحصول على تفاصيل الطائرة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        row = await repo.get_drone(drone_id, tenant_id)
        if not row:
            _raise_not_found()
        return DroneResponse(**_drone_to_response(row))

    if drone_id not in _drones or _drones[drone_id].get("tenant_id") != tenant_id:
        _raise_not_found()
    return DroneResponse(**_drone_to_response(_drones[drone_id]))


@router.put("/{drone_id}", response_model=DroneResponse)
async def update_drone(drone_id: str, drone: DroneCreate, req: Request, user=Depends(get_current_user)):
    """Update drone information - تحديث معلومات الطائرة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        row = await repo.update_drone(drone_id, tenant_id, drone.model_dump())
        if not row:
            _raise_not_found()
        result = DroneResponse(**_drone_to_response(row))
    else:
        if drone_id not in _drones or _drones[drone_id].get("tenant_id") != tenant_id:
            _raise_not_found()
        _drones[drone_id].update(drone.model_dump(exclude_none=True))
        result = DroneResponse(**_drone_to_response(_drones[drone_id]))

    try:
        from src.events import DRONE_UPDATED, publish_drone_event

        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(nc, DRONE_UPDATED, tenant_id, drone_id=result.id)
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("drone_updated", drone_id=drone_id, tenant_id=tenant_id)
    return result


@router.delete("/{drone_id}", status_code=204)
async def delete_drone(drone_id: str, req: Request, user=Depends(get_current_user)):
    """Deregister a drone - إلغاء تسجيل الطائرة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        success = await repo.delete_drone(drone_id, tenant_id)
        if not success:
            _raise_not_found()
    else:
        if drone_id not in _drones or _drones[drone_id].get("tenant_id") != tenant_id:
            _raise_not_found()
        del _drones[drone_id]

    try:
        from src.events import DRONE_DEREGISTERED, publish_drone_event

        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(nc, DRONE_DEREGISTERED, tenant_id, drone_id=drone_id)
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("drone_deregistered", drone_id=drone_id, tenant_id=tenant_id)


@router.get("/{drone_id}/status")
async def get_drone_status(drone_id: str, req: Request, user=Depends(get_current_user)):
    """Get real-time drone status - الحصول على حالة الطائرة في الوقت الفعلي"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        row = await repo.get_drone(drone_id, tenant_id)
        if not row:
            _raise_not_found()
        return {
            "drone_id": str(row["id"]),
            "status": row["status"],
            "battery_percent": float(row.get("battery_percent", 100)),
            "total_flight_hours": float(row.get("total_flight_hours", 0)),
            "last_updated": row.get("updated_at", datetime.now(UTC)).isoformat(),
        }

    if drone_id not in _drones or _drones[drone_id].get("tenant_id") != tenant_id:
        _raise_not_found()
    d = _drones[drone_id]
    return {
        "drone_id": drone_id,
        "status": d["status"],
        "battery_percent": d.get("battery_percent", 100),
        "total_flight_hours": d.get("total_flight_hours", 0),
        "last_updated": datetime.now(UTC).isoformat(),
    }


@router.get("/{drone_id}/telemetry")
async def get_drone_telemetry(drone_id: str, req: Request, user=Depends(get_current_user)):
    """Get drone telemetry history - الحصول على سجل القياس عن بعد للطائرة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        row = await repo.get_drone(drone_id, tenant_id)
        if not row:
            _raise_not_found()
    elif drone_id not in _drones or _drones[drone_id].get("tenant_id") != tenant_id:
        _raise_not_found()

    return {
        "drone_id": drone_id,
        "telemetry": [],
        "message": "Telemetry data collected during active flights",
        "message_ar": "يتم جمع بيانات القياس عن بعد أثناء الرحلات النشطة",
    }
