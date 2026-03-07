"""
Mission management endpoints - نقاط نهاية إدارة المهام
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


router = APIRouter(prefix="/api/v1/missions", tags=["missions"])

_missions: dict[str, dict] = {}

VALID_TRANSITIONS = {
    "planned": ["active"],
    "active": ["paused", "completed", "aborted"],
    "paused": ["active", "aborted"],
    "completed": [],
    "aborted": [],
}


class MissionCreate(BaseModel):
    drone_id: str
    flight_plan_id: str | None = None
    mission_type: str = "spray"
    name: str
    name_ar: str | None = None
    field_id: str | None = None


class MissionResponse(BaseModel):
    id: str
    drone_id: str
    mission_type: str
    name: str
    status: str


@router.get("/", response_model=list[MissionResponse])
async def list_missions(_user=Depends(get_current_user)):
    """List all missions - قائمة بجميع المهام"""
    return [MissionResponse(**{k: m[k] for k in MissionResponse.model_fields}) for m in _missions.values()]


@router.post("/", response_model=MissionResponse, status_code=201)
async def create_mission(mission: MissionCreate, req: Request):
    """Create a new mission - إنشاء مهمة جديدة"""
    mission_id = f"MSN-{uuid.uuid4().hex[:8].upper()}"
    mission_data = {
        "id": mission_id,
        "drone_id": mission.drone_id,
        "flight_plan_id": mission.flight_plan_id,
        "mission_type": mission.mission_type,
        "name": mission.name,
        "name_ar": mission.name_ar,
        "field_id": mission.field_id,
        "status": "planned",
        "progress_percent": 0,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": None,
        "completed_at": None,
    }
    _missions[mission_id] = mission_data

    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish(
            "sahool.drone.mission_created",
            json.dumps({"mission_id": mission_id, "drone_id": mission.drone_id}).encode(),
        )

    logger.info("mission_created", mission_id=mission_id, type=mission.mission_type)
    return MissionResponse(**{k: mission_data[k] for k in MissionResponse.model_fields})


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: str):
    """Get mission details - الحصول على تفاصيل المهمة"""
    if mission_id not in _missions:
        raise HTTPException(status_code=404, detail={"error": "Mission not found", "error_ar": "المهمة غير موجودة"})
    m = _missions[mission_id]
    return MissionResponse(**{k: m[k] for k in MissionResponse.model_fields})


def _transition_mission(mission_id: str, target_status: str) -> dict:
    if mission_id not in _missions:
        raise HTTPException(status_code=404, detail={"error": "Mission not found", "error_ar": "المهمة غير موجودة"})
    mission = _missions[mission_id]
    current = mission["status"]
    if target_status not in VALID_TRANSITIONS.get(current, []):
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Cannot transition from {current} to {target_status}",
                "error_ar": f"لا يمكن الانتقال من {current} إلى {target_status}",
            },
        )
    mission["status"] = target_status
    if target_status == "active" and not mission.get("started_at"):
        mission["started_at"] = datetime.utcnow().isoformat()
    if target_status in ("completed", "aborted"):
        mission["completed_at"] = datetime.utcnow().isoformat()
    logger.info("mission_transition", mission_id=mission_id, from_status=current, to_status=target_status)
    return mission


@router.post("/{mission_id}/start")
async def start_mission(mission_id: str, req: Request):
    """Start mission execution - بدء تنفيذ المهمة"""
    _transition_mission(mission_id, "active")
    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish("sahool.drone.mission_started", json.dumps({"mission_id": mission_id}).encode())
    return {"mission_id": mission_id, "status": "active", "message": "Mission started", "message_ar": "بدأت المهمة"}


@router.post("/{mission_id}/pause")
async def pause_mission(mission_id: str):
    """Pause mission - إيقاف المهمة مؤقتاً"""
    _transition_mission(mission_id, "paused")
    return {
        "mission_id": mission_id,
        "status": "paused",
        "message": "Mission paused",
        "message_ar": "المهمة متوقفة مؤقتاً",
    }


@router.post("/{mission_id}/resume")
async def resume_mission(mission_id: str):
    """Resume mission - استئناف المهمة"""
    _transition_mission(mission_id, "active")
    return {"mission_id": mission_id, "status": "active", "message": "Mission resumed", "message_ar": "استُؤنفت المهمة"}


@router.post("/{mission_id}/abort")
async def abort_mission(mission_id: str, req: Request):
    """Abort mission - إلغاء المهمة"""
    _transition_mission(mission_id, "aborted")
    nc = getattr(req.app.state, "nc", None)
    if nc:
        await nc.publish("sahool.drone.mission_aborted", json.dumps({"mission_id": mission_id}).encode())
    return {
        "mission_id": mission_id,
        "status": "aborted",
        "message": "Mission aborted",
        "message_ar": "تم إلغاء المهمة",
    }
