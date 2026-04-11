"""
Task CRUD Routes - مسارات عمليات المهام الأساسية

This module provides core task management endpoints:
- List, create, read, update, delete tasks
- Task status transitions (start, complete, cancel)
- Evidence attachment
- Task statistics
"""

import logging
import os
import sys
import uuid
from datetime import UTC, datetime, time, timedelta
from datetime import date as date_type
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ..database import get_db
from ..exceptions import (
    TaskCreationError,
    TaskInvalidStatusError,
    TaskNotFoundError,
    ValidationError,
)
from ..models import Task as TaskModel
from ..models import TaskEvidence
from ..repository import TaskRepository
from ..task_utils import (
    TaskCreateData,
    TaskPriority,
    TaskStatus,
    TaskType,
    create_task_model,
    db_task_to_dict,
    enrich_task_with_astronomy,
    generate_task_id,
    send_task_notification,
)
from ..validators import (
    sanitize_for_log,
    validate_field_id,
    validate_metadata_size,
    validate_scheduled_time,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Router Setup - إعداد الموجه
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])

# ═══════════════════════════════════════════════════════════════════════════
# Auth Dependencies - تبعيات المصادقة
# ═══════════════════════════════════════════════════════════════════════════

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

    class User(BaseModel):  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str = ""

    async def get_current_user():
        raise HTTPException(
            status_code=503,
            detail="Authentication backend unavailable",
        )


def _extract_tenant_from_user(user: Any) -> str | None:
    """
    Read a tenant id from a User-like object.

    The shared JWT decoder populates `tenant_id` from the JWT `tid` claim.
    Some integrations expose it directly as `tid` — check both for safety.
    """
    if user is None:
        return None
    for attr in ("tenant_id", "tid"):
        value = getattr(user, attr, None)
        if value:
            return str(value)
    # dataclass / dict fallback
    if isinstance(user, dict):
        return user.get("tenant_id") or user.get("tid")
    return None


def _extract_tenant_from_request_state(request: Request) -> str | None:
    """
    Read tenant id from request.state populated by JWT/tenant middleware.

    The shared ``TenantContextMiddleware`` sets ``request.state.tenant_id``
    (and ``request.state.principal`` with the full JWT claim set) BEFORE the
    route runs. We prefer these sources because they are authenticated.
    """
    # 1. user object attached by shared auth middleware
    user = getattr(request.state, "user", None)
    tid = _extract_tenant_from_user(user)
    if tid:
        return tid

    # 2. principal dict from TenantContextMiddleware (JWT claims)
    principal = getattr(request.state, "principal", None)
    if isinstance(principal, dict):
        value = principal.get("tid") or principal.get("tenant_id")
        if value:
            return str(value)

    # 3. tenant_id already resolved by TenantContextMiddleware
    value = getattr(request.state, "tenant_id", None)
    if value:
        return str(value)

    return None


async def get_tenant_id(
    request: Request,
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> str:
    """
    Resolve the current tenant ID from the authenticated JWT.

    SECURITY (Wave 2)
    -----------------
    The previous implementation trusted the ``X-Tenant-Id`` header, which
    allowed a client with any valid JWT to request data from *any* tenant
    simply by setting a different header value. We now:

    1. Pull the tenant exclusively from authenticated sources:
         * ``request.state.user`` / ``request.state.principal`` set by
           JWT / TenantContext middleware, **or**
         * the ``get_current_user()`` dependency if no middleware ran.
    2. Use the raw ``X-Tenant-Id`` header *only* as a cross-check — a
       mismatch with the JWT tenant is rejected with **403 Forbidden**.
    3. Reject the request with **401** if no JWT tenant can be resolved.
    """
    # 1. Prefer tenant already attached to request.state by middleware
    jwt_tenant: str | None = _extract_tenant_from_request_state(request)

    # 2. Fall back to resolving the user via the dependency
    if not jwt_tenant and AUTH_AVAILABLE:
        try:
            user = await get_current_user()
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning(
                "get_current_user failed while resolving tenant: %s",
                type(exc).__name__,
            )
            user = None
        jwt_tenant = _extract_tenant_from_user(user)

    if not jwt_tenant:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthenticated",
                "message": "Authenticated tenant (JWT 'tid') is required",
                "message_ar": "يجب توفر المستأجر الموثّق (JWT 'tid')",
            },
        )

    # 3. If the client supplied an X-Tenant-Id header, it MUST match the JWT.
    #    Silent mismatch is now a 403 Forbidden — we never trust the header.
    if x_tenant_id and x_tenant_id != jwt_tenant:
        logger.warning(
            "Tenant header/JWT mismatch blocked: header=%s jwt=%s",
            sanitize_for_log(x_tenant_id),
            sanitize_for_log(jwt_tenant),
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "tenant_mismatch",
                "message": "X-Tenant-Id does not match authenticated tenant",
                "message_ar": "رأس X-Tenant-Id لا يطابق المستأجر الموثّق",
            },
        )

    return jwt_tenant


# ═══════════════════════════════════════════════════════════════════════════
# Request/Response Models - نماذج الطلب/الاستجابة
# ═══════════════════════════════════════════════════════════════════════════


# Strict UUID v4 format regex used for assigned_to validation.
_UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"


def _normalize_due_date(value: Any) -> datetime | None:
    """
    Coerce a due-date input into a timezone-aware UTC datetime.

    Accepts:
      * ``None``                                          → ``None``
      * ``datetime`` instances                            → made UTC-aware
      * ISO-8601 strings with an explicit offset          → parsed as-is
      * ``YYYY-MM-DD`` (date only, no time)               → **end of day UTC**
        (``23:59:59.999999+00:00``) so "due today" filters behave predictably
        regardless of the client's local timezone.

    This mirrors how the web/admin UI submits due dates (`<input type="date">`
    returns ``YYYY-MM-DD``) and fixes the previous off-by-timezone bug where
    naïve parsing treated them as midnight UTC.
    """
    if value is None or isinstance(value, datetime):
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
    if isinstance(value, date_type):
        return datetime.combine(value, time(23, 59, 59, 999999), tzinfo=UTC)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        # Bare YYYY-MM-DD → end of day UTC
        try:
            parsed_date = date_type.fromisoformat(text)
            return datetime.combine(parsed_date, time(23, 59, 59, 999999), tzinfo=UTC)
        except ValueError:
            pass
        # ISO-8601 datetime (with or without 'Z')
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("due_date must be ISO-8601 (YYYY-MM-DD or full datetime with timezone)") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed
    raise ValueError("due_date must be a string or datetime")


class TaskCreateRequest(BaseModel):
    """Create a new task - إنشاء مهمة جديدة"""

    # SECURITY (Wave 2): strict mode — unknown fields return 422 instead of
    # being silently dropped (e.g. camelCase vs snake_case typos such as
    # ``assignee_id``/``taskType`` which used to corrupt records).
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType = TaskType.OTHER
    priority: TaskPriority = TaskPriority.MEDIUM
    field_id: str | None = Field(None, max_length=100)
    zone_id: str | None = None
    # Validate assigned_to as a UUID to prevent cross-tenant assignment with
    # arbitrary strings. Full tenant-scoped user existence verification should
    # be added when a user-lookup service is available.
    assigned_to: str | None = Field(None, max_length=100, pattern=_UUID_PATTERN)
    due_date: datetime | None = Field(
        None,
        description=(
            "ISO-8601 datetime with timezone OR bare YYYY-MM-DD. "
            "Bare dates are interpreted as end-of-day UTC (23:59:59+00:00)."
        ),
    )
    scheduled_time: str | None = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):([0-5][0-9])(?::([0-5][0-9]))?$")
    estimated_duration_minutes: int | None = Field(None, ge=1, le=1440)
    metadata: dict | None = Field(None, description="Must be < 64KB when serialized")

    # Astronomical fields (auto-populated if due_date is provided)
    astronomical_score: int | None = Field(None, ge=1, le=10)
    moon_phase_at_due_date: str | None = None
    lunar_mansion_at_due_date: str | None = None
    optimal_time_of_day: str | None = None
    suggested_by_calendar: bool = False
    astronomical_recommendation: dict | None = None

    @field_validator("due_date", mode="before")
    @classmethod
    def _parse_due_date(cls, v):
        return _normalize_due_date(v)


class TaskUpdateRequest(BaseModel):
    """Update task properties - تحديث خصائص المهمة"""

    # Strict mode — reject unknown fields (see TaskCreateRequest).
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(None, min_length=1, max_length=200)
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType | None = None
    priority: TaskPriority | None = None
    field_id: str | None = Field(None, max_length=100)
    zone_id: str | None = None
    assigned_to: str | None = Field(None, max_length=100, pattern=_UUID_PATTERN)
    due_date: datetime | None = Field(
        None,
        description=("ISO-8601 datetime with timezone OR bare YYYY-MM-DD (interpreted as end-of-day UTC)."),
    )
    scheduled_time: str | None = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):([0-5][0-9])(?::([0-5][0-9]))?$")
    estimated_duration_minutes: int | None = Field(None, ge=1, le=1440)
    status: TaskStatus | None = None
    metadata: dict | None = Field(None, description="Must be < 64KB when serialized")

    # Optimistic concurrency control. When provided, the server rejects
    # the update with 409 if the stored task's ``version`` no longer
    # matches, preventing kanban drag-drop / concurrent-edit overwrites.
    if_match_version: int | None = Field(
        None,
        ge=1,
        description=(
            "Expected current version of the task. If set and the stored "
            "version does not match, the update is rejected with HTTP 409."
        ),
    )

    @field_validator("due_date", mode="before")
    @classmethod
    def _parse_due_date(cls, v):
        return _normalize_due_date(v)


class TaskCompleteRequest(BaseModel):
    """Complete a task with evidence - إكمال مهمة مع الأدلة"""

    # Strict mode — reject unknown fields (see TaskCreateRequest).
    model_config = ConfigDict(extra="forbid")

    notes: str | None = None
    notes_ar: str | None = None
    photo_urls: list[str] | None = None
    actual_duration_minutes: int | None = Field(None, ge=1)
    completion_metadata: dict | None = None


class EvidenceResponse(BaseModel):
    """Evidence attached to a task - دليل مرفق بمهمة"""

    evidence_id: str
    task_id: str
    type: str
    content: str
    captured_at: datetime
    location: dict | None = None


# ═══════════════════════════════════════════════════════════════════════════
# List & Stats Endpoints - نقاط نهاية القائمة والإحصائيات
# ═══════════════════════════════════════════════════════════════════════════


@router.get("", response_model=dict)
async def list_tasks(
    field_id: str | None = Query(None, description="Filter by field"),
    status: TaskStatus | None = Query(None, description="Filter by status"),
    task_type: TaskType | None = Query(None, description="Filter by type"),
    priority: TaskPriority | None = Query(None, description="Filter by priority"),
    assigned_to: str | None = Query(None, description="Filter by assignee"),
    due_before: datetime | None = Query(None, description="Due before date"),
    due_after: datetime | None = Query(None, description="Due after date"),
    search: str | None = Query(
        None,
        max_length=200,
        description=(
            "Case-insensitive ILIKE match on title / title_ar / description. "
            "Empty or whitespace-only values are ignored."
        ),
    ),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    List tasks with optional filters
    عرض المهام مع فلاتر اختيارية
    """
    repo = TaskRepository(db)

    # Normalize search: ignore empty/whitespace-only values
    search_term = search.strip() if search else None
    if search_term == "":
        search_term = None

    tasks, total = repo.list_tasks(
        tenant_id=tenant_id,
        field_id=field_id,
        status=status.value if status else None,
        task_type=task_type.value if task_type else None,
        priority=priority.value if priority else None,
        assigned_to=assigned_to,
        due_before=due_before,
        due_after=due_after,
        search=search_term,
        limit=limit,
        offset=offset,
    )

    return {
        "tasks": [db_task_to_dict(t) for t in tasks],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/today", response_model=dict)
async def get_today_tasks(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Get tasks due today
    الحصول على مهام اليوم
    """
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    repo = TaskRepository(db)
    tasks, total = repo.list_tasks(
        tenant_id=tenant_id,
        due_after=today_start,
        due_before=today_end,
        limit=limit,
        offset=offset,
    )

    return {
        "tasks": [db_task_to_dict(t) for t in tasks],
        "count": len(tasks),
        "total": total,
        "date": today_start.date().isoformat(),
    }


@router.get("/upcoming", response_model=dict)
async def get_upcoming_tasks(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Get upcoming tasks for the next N days
    الحصول على المهام القادمة للأيام القادمة
    """
    now = datetime.now(UTC)
    future = now + timedelta(days=days)
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    repo = TaskRepository(db)
    tasks, _ = repo.list_tasks(
        tenant_id=tenant_id,
        due_after=tomorrow,
        due_before=future,
        limit=limit,
        offset=offset,
    )

    # Filter out completed and cancelled tasks
    upcoming = [t for t in tasks if t.status not in ["completed", "cancelled"]]

    return {
        "tasks": [db_task_to_dict(t) for t in upcoming],
        "count": len(upcoming),
        "days": days,
    }


@router.get("/stats", response_model=dict)
async def get_task_stats(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Get task statistics
    الحصول على إحصائيات المهام
    """
    repo = TaskRepository(db)
    return repo.get_task_stats(tenant_id)


# ═══════════════════════════════════════════════════════════════════════════
# CRUD Endpoints - نقاط نهاية CRUD
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Get a specific task by ID
    الحصول على مهمة محددة بواسطة المعرف
    """
    repo = TaskRepository(db)
    task = repo.get_task_by_id(task_id, tenant_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found",
                "error_ar": "المهمة غير موجودة",
                "task_id": task_id,
            },
        )

    return db_task_to_dict(task)


@router.post("", response_model=dict, status_code=201)
async def create_task(
    data: TaskCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new task
    إنشاء مهمة جديدة
    """
    # Validate metadata size
    if data.metadata:
        try:
            validate_metadata_size(data.metadata)
        except (ValidationError, ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid metadata | بيانات وصفية غير صالحة")

    # Validate field_id format
    if data.field_id:
        try:
            validate_field_id(data.field_id)
        except (ValidationError, ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid field ID format | صيغة معرف الحقل غير صالحة")

    task_id = generate_task_id()
    created_by = getattr(current_user, "id", "system")

    # Create task data object
    task_data = TaskCreateData(
        tenant_id=tenant_id,
        title=data.title,
        title_ar=data.title_ar,
        description=data.description,
        description_ar=data.description_ar,
        task_type=data.task_type,
        priority=data.priority,
        field_id=data.field_id,
        zone_id=data.zone_id,
        assigned_to=data.assigned_to,
        created_by=created_by,
        due_date=data.due_date,
        scheduled_time=data.scheduled_time,
        estimated_duration_minutes=data.estimated_duration_minutes,
        metadata=data.metadata,
        astronomical_score=data.astronomical_score,
        moon_phase_at_due_date=data.moon_phase_at_due_date,
        lunar_mansion_at_due_date=data.lunar_mansion_at_due_date,
        optimal_time_of_day=data.optimal_time_of_day,
        suggested_by_calendar=data.suggested_by_calendar,
        astronomical_recommendation=data.astronomical_recommendation,
    )

    # Enrich with astronomical data if due_date is provided
    if data.due_date:
        task_data = await enrich_task_with_astronomy(task_data, data.task_type)

    # Create database model
    db_task = create_task_model(task_data, task_id)

    # Save to database
    repo = TaskRepository(db)
    created_task = repo.create_task(db_task)

    logger.info("Task created: %s", sanitize_for_log(task_id))

    return db_task_to_dict(created_task)


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: str,
    data: TaskUpdateRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a task
    تحديث مهمة
    """
    # Validate metadata size
    if data.metadata:
        try:
            validate_metadata_size(data.metadata)
        except (ValidationError, ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid metadata | بيانات وصفية غير صالحة")

    repo = TaskRepository(db)
    performed_by = current_user.id if current_user and current_user.id else "system"

    # Prepare update data
    update_data = data.model_dump(exclude_unset=True)

    # Convert enums to strings
    if "task_type" in update_data and isinstance(update_data["task_type"], TaskType):
        update_data["task_type"] = update_data["task_type"].value
    if "priority" in update_data and isinstance(update_data["priority"], TaskPriority):
        update_data["priority"] = update_data["priority"].value
    if "status" in update_data and isinstance(update_data["status"], TaskStatus):
        update_data["status"] = update_data["status"].value

    # Map 'metadata' to 'task_metadata' for database
    if "metadata" in update_data:
        update_data["task_metadata"] = update_data.pop("metadata")

    task = repo.update_task(task_id, tenant_id, update_data, performed_by)

    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found",
                "error_ar": "المهمة غير موجودة",
                "task_id": task_id,
            },
        )

    logger.info("Task updated: %s by %s", sanitize_for_log(task_id), sanitize_for_log(performed_by))

    return db_task_to_dict(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a task
    حذف مهمة
    """
    repo = TaskRepository(db)
    success = repo.delete_task(task_id, tenant_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found",
                "error_ar": "المهمة غير موجودة",
                "task_id": task_id,
            },
        )

    performed_by = current_user.id if current_user and current_user.id else "system"
    logger.info("Task deleted: %s by %s", sanitize_for_log(task_id), sanitize_for_log(performed_by))


# ═══════════════════════════════════════════════════════════════════════════
# Status Transition Endpoints - نقاط نهاية انتقال الحالة
# ═══════════════════════════════════════════════════════════════════════════


@router.post("/{task_id}/start", response_model=dict)
async def start_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a task as in progress
    وضع علامة على المهمة كقيد التنفيذ
    """
    repo = TaskRepository(db)
    performed_by = current_user.id if current_user and current_user.id else "system"

    try:
        task = repo.start_task(task_id, tenant_id, performed_by)

        if not task:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Task not found",
                    "error_ar": "المهمة غير موجودة",
                    "task_id": task_id,
                },
            )

        logger.info("Task started: %s by %s", sanitize_for_log(task_id), sanitize_for_log(performed_by))

        return db_task_to_dict(task)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": str(e),
                "error_ar": "لا يمكن بدء هذه المهمة",
            },
        )


@router.post("/{task_id}/complete", response_model=dict)
async def complete_task(
    task_id: str,
    data: TaskCompleteRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a task as completed with evidence
    وضع علامة على المهمة كمكتملة مع الأدلة
    """
    repo = TaskRepository(db)
    performed_by = current_user.id if current_user and current_user.id else "system"
    now = datetime.now(UTC)

    task = repo.complete_task(
        task_id=task_id,
        tenant_id=tenant_id,
        performed_by=performed_by,
        notes=data.notes or data.notes_ar,
        actual_duration_minutes=data.actual_duration_minutes,
        completion_metadata=data.completion_metadata,
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found",
                "error_ar": "المهمة غير موجودة",
                "task_id": task_id,
            },
        )

    # Add photo evidence if provided
    if data.photo_urls:
        for url in data.photo_urls:
            evidence = TaskEvidence(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                type="photo",
                content=url,
                captured_at=now,
            )
            repo.add_evidence(evidence)

    logger.info("Task completed: %s", sanitize_for_log(task_id))

    return db_task_to_dict(task)


@router.post("/{task_id}/cancel", response_model=dict)
async def cancel_task(
    task_id: str,
    reason: str | None = Query(None, description="Cancellation reason"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel a task
    إلغاء مهمة
    """
    repo = TaskRepository(db)
    performed_by = current_user.id if current_user and current_user.id else "system"

    task = repo.cancel_task(task_id, tenant_id, performed_by, reason)

    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found",
                "error_ar": "المهمة غير موجودة",
                "task_id": task_id,
            },
        )

    logger.info("Task cancelled: %s (reason: %s)", sanitize_for_log(task_id), sanitize_for_log(reason))

    return db_task_to_dict(task)


# ═══════════════════════════════════════════════════════════════════════════
# Evidence Endpoints - نقاط نهاية الأدلة
# ═══════════════════════════════════════════════════════════════════════════


@router.post("/{task_id}/evidence", response_model=EvidenceResponse, status_code=201)
async def add_evidence(
    task_id: str,
    evidence_type: str = Query(..., description="Type: photo, note, voice, measurement"),
    content: str = Query(..., description="URL or text content"),
    lat: float | None = Query(None, description="Latitude"),
    lon: float | None = Query(None, description="Longitude"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add evidence to a task
    إضافة دليل إلى مهمة
    """
    repo = TaskRepository(db)

    # Check if task exists
    task = repo.get_task_by_id(task_id, tenant_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found",
                "error_ar": "المهمة غير موجودة",
                "task_id": task_id,
            },
        )

    # Create and save evidence
    db_evidence = TaskEvidence(
        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        type=evidence_type,
        content=content,
        captured_at=datetime.now(UTC),
        location={"lat": lat, "lon": lon} if lat and lon else None,
    )

    saved_evidence = repo.add_evidence(db_evidence)

    added_by = current_user.id if current_user and current_user.id else "system"
    logger.info(
        "Evidence added to task %s: %s by %s",
        sanitize_for_log(task_id),
        sanitize_for_log(saved_evidence.evidence_id),
        sanitize_for_log(added_by),
    )

    return EvidenceResponse(
        evidence_id=saved_evidence.evidence_id,
        task_id=saved_evidence.task_id,
        type=saved_evidence.type,
        content=saved_evidence.content,
        captured_at=saved_evidence.captured_at,
        location=saved_evidence.location,
    )
