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
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
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


async def get_tenant_id(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> str:
    """
    Extract and validate tenant ID.
    استخراج والتحقق من معرف المستأجر

    SECURITY: Tenant ID must be a valid UUID and is required for all
    tenant-scoped operations. Previously this accepted any string with a
    default of "default", which broke tenant isolation entirely -- any
    caller could omit the header and share the same "default" namespace,
    or supply an arbitrary string to access another tenant's data.

    The JWT-validated tenant should ideally be used (via TenantContextMiddleware),
    but when auth is unavailable we still require a valid UUID from the header
    to maintain isolation guarantees.
    """
    # SECURITY: If auth is available and user has a tenant_id from JWT, prefer that
    if AUTH_AVAILABLE:
        try:
            # In production, the TenantContextMiddleware sets tenant from JWT.
            # This is a defense-in-depth check at the route level.
            user = await get_current_user()
            if user and getattr(user, "tenant_id", None):
                jwt_tenant = user.tenant_id
                if x_tenant_id and x_tenant_id != jwt_tenant:
                    logger.warning(
                        "Tenant ID mismatch: header=%s jwt=%s — using JWT tenant",
                        sanitize_for_log(x_tenant_id),
                        sanitize_for_log(jwt_tenant),
                    )
                return jwt_tenant
        except Exception as exc:
            logger.warning(
                "Defense-in-depth tenant check failed, falling back to header: %s",
                exc,
            )

    if not x_tenant_id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "missing_tenant",
                "message": "X-Tenant-Id header is required",
                "message_ar": "رأس X-Tenant-Id مطلوب",
            },
        )

    # Validate UUID format to prevent injection of arbitrary strings
    try:
        import uuid as _uuid_mod

        _uuid_mod.UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_tenant",
                "message": "X-Tenant-Id must be a valid UUID",
                "message_ar": "يجب أن يكون معرف المستأجر UUID صالح",
            },
        )

    return x_tenant_id


# ═══════════════════════════════════════════════════════════════════════════
# Request/Response Models - نماذج الطلب/الاستجابة
# ═══════════════════════════════════════════════════════════════════════════


# Strict UUID v4 format regex used for assigned_to validation.
_UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"


class TaskCreateRequest(BaseModel):
    """Create a new task - إنشاء مهمة جديدة"""

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
    due_date: datetime | None = None
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


class TaskUpdateRequest(BaseModel):
    """Update task properties - تحديث خصائص المهمة"""

    title: str | None = Field(None, min_length=1, max_length=200)
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType | None = None
    priority: TaskPriority | None = None
    field_id: str | None = Field(None, max_length=100)
    zone_id: str | None = None
    assigned_to: str | None = Field(None, max_length=100, pattern=_UUID_PATTERN)
    due_date: datetime | None = None
    scheduled_time: str | None = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):([0-5][0-9])(?::([0-5][0-9]))?$")
    estimated_duration_minutes: int | None = Field(None, ge=1, le=1440)
    status: TaskStatus | None = None
    metadata: dict | None = Field(None, description="Must be < 64KB when serialized")


class TaskCompleteRequest(BaseModel):
    """Complete a task with evidence - إكمال مهمة مع الأدلة"""

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

    tasks, total = repo.list_tasks(
        tenant_id=tenant_id,
        field_id=field_id,
        status=status.value if status else None,
        task_type=task_type.value if task_type else None,
        priority=priority.value if priority else None,
        assigned_to=assigned_to,
        due_before=due_before,
        due_after=due_after,
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
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail="Invalid metadata | بيانات وصفية غير صالحة")

    # Validate field_id format
    if data.field_id:
        try:
            validate_field_id(data.field_id)
        except (ValueError, TypeError) as e:
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
        except (ValueError, TypeError):
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
