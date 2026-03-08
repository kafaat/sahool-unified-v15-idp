"""
Mission management endpoints - نقاط نهاية إدارة المهام
Supports database persistence with in-memory fallback.
"""

import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

# Unified error handling
try:
    from shared.errors_py import NotFoundException, ValidationException
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

    class ValidationException(HTTPException):  # type: ignore[no-redef]
        """Fallback when shared.errors_py is unavailable."""

        def __init__(self, message: str = "", message_ar: str | None = None, **_kw):
            detail = {"error": message}
            if message_ar:
                detail["error_ar"] = message_ar
            super().__init__(status_code=422, detail=detail)

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
    drone_id: str | None = None
    mission_type: str
    name: str
    status: str
    tenant_id: str | None = None


def _get_repo(req: Request):
    pool = getattr(req.app.state, "db_pool", None)
    if pool:
        from src.db import DroneRepository
        return DroneRepository(pool)
    return None


def _get_tenant_id(user) -> str:
    return getattr(user, "tenant_id", "default")


def _mission_to_response(m: dict) -> dict:
    return {
        k: (str(m[k]) if k in ("id", "drone_id") and m.get(k) else m.get(k))
        for k in MissionResponse.model_fields
        if k in m
    }


def _raise_not_found():
    """Raise NotFoundException for missing missions."""
    raise NotFoundException("Mission not found", "المهمة غير موجودة", "mission")


def _validate_transition(current: str, target: str) -> None:
    """Validate mission status transition."""
    if target not in VALID_TRANSITIONS.get(current, []):
        raise ValidationException(
            f"Cannot transition from {current} to {target}",
            f"لا يمكن الانتقال من {current} إلى {target}",
        )


@router.get("/", response_model=list[MissionResponse])
async def list_missions(
    req: Request,
    status: str | None = None,
    drone_id: str | None = None,
    user=Depends(get_current_user),
):
    """List all missions - قائمة بجميع المهام"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        rows = await repo.list_missions(tenant_id, status=status, drone_id=drone_id)
        return [MissionResponse(**_mission_to_response(r)) for r in rows]

    missions = [m for m in _missions.values() if m.get("tenant_id") == tenant_id]
    if status:
        missions = [m for m in missions if m.get("status") == status]
    if drone_id:
        missions = [m for m in missions if m.get("drone_id") == drone_id]
    return [MissionResponse(**_mission_to_response(m)) for m in missions]


@router.post("/", response_model=MissionResponse, status_code=201)
async def create_mission(mission: MissionCreate, req: Request, user=Depends(get_current_user)):
    """Create a new mission - إنشاء مهمة جديدة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        row = await repo.create_mission(tenant_id, mission.model_dump())
        result = MissionResponse(**_mission_to_response(row))
    else:
        mission_id = f"MSN-{uuid.uuid4().hex[:8].upper()}"
        mission_data = {
            "id": mission_id, "tenant_id": tenant_id,
            **mission.model_dump(),
            "status": "planned", "progress_percent": 0,
            "created_at": datetime.now(UTC).isoformat(),
            "started_at": None, "completed_at": None,
        }
        _missions[mission_id] = mission_data
        result = MissionResponse(**_mission_to_response(mission_data))

    try:
        from src.events import MISSION_CREATED, publish_drone_event
        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(
            nc, MISSION_CREATED, tenant_id,
            mission_id=result.id, drone_id=mission.drone_id,
            mission_type=mission.mission_type, field_id=mission.field_id,
        )
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("mission_created", mission_id=result.id, type=mission.mission_type, tenant_id=tenant_id)
    return result


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: str, req: Request, user=Depends(get_current_user)):
    """Get mission details - الحصول على تفاصيل المهمة"""
    tenant_id = _get_tenant_id(user)
    repo = _get_repo(req)

    if repo:
        row = await repo.get_mission(mission_id, tenant_id)
        if not row:
            _raise_not_found()
        return MissionResponse(**_mission_to_response(row))

    if mission_id not in _missions or _missions[mission_id].get("tenant_id") != tenant_id:
        _raise_not_found()
    return MissionResponse(**_mission_to_response(_missions[mission_id]))


async def _transition_mission(
    mission_id: str, target: str, req: Request, tenant_id: str,
) -> dict:
    """Transition mission status with validation."""
    repo = _get_repo(req)

    if repo:
        current_row = await repo.get_mission(mission_id, tenant_id)
        if not current_row:
            _raise_not_found()
        _validate_transition(current_row["status"], target)
        updated = await repo.update_mission_status(mission_id, tenant_id, target)
        return updated or current_row

    if mission_id not in _missions or _missions[mission_id].get("tenant_id") != tenant_id:
        _raise_not_found()
    mission = _missions[mission_id]
    _validate_transition(mission["status"], target)
    mission["status"] = target
    if target == "active" and not mission.get("started_at"):
        mission["started_at"] = datetime.now(UTC).isoformat()
    if target in ("completed", "aborted"):
        mission["completed_at"] = datetime.now(UTC).isoformat()
    return mission


@router.post("/{mission_id}/start")
async def start_mission(mission_id: str, req: Request, user=Depends(get_current_user)):
    """Start mission execution - بدء تنفيذ المهمة"""
    tenant_id = _get_tenant_id(user)
    await _transition_mission(mission_id, "active", req, tenant_id)

    try:
        from src.events import MISSION_STARTED, publish_drone_event
        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(nc, MISSION_STARTED, tenant_id, mission_id=mission_id)
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("mission_started", mission_id=mission_id, tenant_id=tenant_id)
    return {"mission_id": mission_id, "status": "active", "message": "Mission started", "message_ar": "بدأت المهمة"}


@router.post("/{mission_id}/pause")
async def pause_mission(mission_id: str, req: Request, user=Depends(get_current_user)):
    """Pause mission - إيقاف المهمة مؤقتاً"""
    tenant_id = _get_tenant_id(user)
    await _transition_mission(mission_id, "paused", req, tenant_id)

    try:
        from src.events import MISSION_PAUSED, publish_drone_event
        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(nc, MISSION_PAUSED, tenant_id, mission_id=mission_id)
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    return {"mission_id": mission_id, "status": "paused", "message": "Mission paused", "message_ar": "المهمة متوقفة مؤقتاً"}


@router.post("/{mission_id}/resume")
async def resume_mission(mission_id: str, req: Request, user=Depends(get_current_user)):
    """Resume mission - استئناف المهمة"""
    tenant_id = _get_tenant_id(user)
    await _transition_mission(mission_id, "active", req, tenant_id)

    try:
        from src.events import MISSION_RESUMED, publish_drone_event
        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(nc, MISSION_RESUMED, tenant_id, mission_id=mission_id)
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    return {"mission_id": mission_id, "status": "active", "message": "Mission resumed", "message_ar": "استُؤنفت المهمة"}


@router.post("/{mission_id}/abort")
async def abort_mission(mission_id: str, req: Request, user=Depends(get_current_user)):
    """Abort mission - إلغاء المهمة"""
    tenant_id = _get_tenant_id(user)
    await _transition_mission(mission_id, "aborted", req, tenant_id)

    try:
        from src.events import MISSION_ABORTED, publish_drone_event
        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(nc, MISSION_ABORTED, tenant_id, mission_id=mission_id)
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("mission_aborted", mission_id=mission_id, tenant_id=tenant_id)
    return {"mission_id": mission_id, "status": "aborted", "message": "Mission aborted", "message_ar": "تم إلغاء المهمة"}


@router.post("/{mission_id}/complete")
async def complete_mission(mission_id: str, req: Request, user=Depends(get_current_user)):
    """Complete mission - إكمال المهمة"""
    tenant_id = _get_tenant_id(user)
    await _transition_mission(mission_id, "completed", req, tenant_id)

    try:
        from src.events import MISSION_COMPLETED, publish_drone_event
        nc = getattr(req.app.state, "nc", None)
        await publish_drone_event(nc, MISSION_COMPLETED, tenant_id, mission_id=mission_id)
    except Exception:
        pass  # NATS event publishing is best-effort; do not block the request

    logger.info("mission_completed", mission_id=mission_id, tenant_id=tenant_id)
    return {"mission_id": mission_id, "status": "completed", "message": "Mission completed", "message_ar": "اكتملت المهمة"}
