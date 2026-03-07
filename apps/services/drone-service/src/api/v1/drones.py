"""
Drone management endpoints - نقاط نهاية إدارة الطائرات
"""

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

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

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/drones", tags=["drones"])

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


@router.get("/", response_model=list[DroneResponse])
async def list_drones(_user=Depends(get_current_user)):
    """List all registered drones - قائمة بجميع الطائرات المسجلة"""
    return [DroneResponse(**{k: d[k] for k in DroneResponse.model_fields if k in d}) for d in _drones.values()]


@router.post("/", response_model=DroneResponse, status_code=201)
async def register_drone(drone: DroneCreate, _user=Depends(get_current_user)):
    """Register a new drone - تسجيل طائرة جديدة"""
    drone_id = f"DRN-{uuid.uuid4().hex[:8].upper()}"
    drone_data = {
        "id": drone_id,
        "name": drone.name,
        "name_ar": drone.name_ar,
        "model": drone.model,
        "serial_number": drone.serial_number,
        "drone_type": drone.drone_type,
        "max_payload_kg": drone.max_payload_kg,
        "tank_capacity_l": drone.tank_capacity_l,
        "max_flight_time_min": drone.max_flight_time_min,
        "status": "active",
        "battery_percent": 100,
        "total_flight_hours": 0.0,
        "registered_at": datetime.now(UTC).isoformat(),
    }
    _drones[drone_id] = drone_data
    logger.info("drone_registered", drone_id=drone_id, model=drone.model)
    return DroneResponse(**{k: drone_data[k] for k in DroneResponse.model_fields})


@router.get("/{drone_id}", response_model=DroneResponse)
async def get_drone(drone_id: str):
    """Get drone details - الحصول على تفاصيل الطائرة"""
    if drone_id not in _drones:
        raise HTTPException(status_code=404, detail={"error": "Drone not found", "error_ar": "الطائرة غير موجودة"})
    d = _drones[drone_id]
    return DroneResponse(**{k: d[k] for k in DroneResponse.model_fields})


@router.put("/{drone_id}", response_model=DroneResponse)
async def update_drone(drone_id: str, drone: DroneCreate, _user=Depends(get_current_user)):
    """Update drone information - تحديث معلومات الطائرة"""
    if drone_id not in _drones:
        raise HTTPException(status_code=404, detail={"error": "Drone not found", "error_ar": "الطائرة غير موجودة"})
    _drones[drone_id].update({
        "name": drone.name, "name_ar": drone.name_ar,
        "model": drone.model, "serial_number": drone.serial_number,
        "drone_type": drone.drone_type,
    })
    logger.info("drone_updated", drone_id=drone_id)
    d = _drones[drone_id]
    return DroneResponse(**{k: d[k] for k in DroneResponse.model_fields})


@router.delete("/{drone_id}", status_code=204)
async def delete_drone(drone_id: str, _user=Depends(get_current_user)):
    """Deregister a drone - إلغاء تسجيل الطائرة"""
    if drone_id not in _drones:
        raise HTTPException(status_code=404, detail={"error": "Drone not found", "error_ar": "الطائرة غير موجودة"})
    del _drones[drone_id]
    logger.info("drone_deregistered", drone_id=drone_id)


@router.get("/{drone_id}/status")
async def get_drone_status(drone_id: str):
    """Get real-time drone status - الحصول على حالة الطائرة في الوقت الفعلي"""
    if drone_id not in _drones:
        raise HTTPException(status_code=404, detail={"error": "Drone not found", "error_ar": "الطائرة غير موجودة"})
    d = _drones[drone_id]
    return {
        "drone_id": drone_id, "status": d["status"],
        "battery_percent": d.get("battery_percent", 100),
        "total_flight_hours": d.get("total_flight_hours", 0),
        "last_updated": datetime.now(UTC).isoformat(),
    }


@router.get("/{drone_id}/telemetry")
async def get_drone_telemetry(drone_id: str):
    """Get drone telemetry history - الحصول على سجل القياس عن بعد للطائرة"""
    if drone_id not in _drones:
        raise HTTPException(status_code=404, detail={"error": "Drone not found", "error_ar": "الطائرة غير موجودة"})
    return {
        "drone_id": drone_id, "telemetry": [],
        "message": "Telemetry data collected during active flights",
        "message_ar": "يتم جمع بيانات القياس عن بعد أثناء الرحلات النشطة",
    }
