"""
NDVI Integration Routes - مسارات تكامل NDVI

This module provides NDVI-based task automation endpoints:
- Create tasks from NDVI alerts
- Get task suggestions based on field health
- Auto-create batch tasks from recommendations
- Get field health analysis
"""

import logging
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Import authentication
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


# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ..database import get_db
from ..exceptions import NdviServiceError, TaskCreationError
from ..repository import TaskRepository
from ..task_utils import (
    TaskCreateData,
    TaskPriority,
    TaskStatus,
    TaskType,
    calculate_ndvi_priority,
    create_task_model,
    db_task_to_dict,
    fetch_field_manager,
    generate_ndvi_task_content,
    generate_task_id,
    get_due_date_for_priority,
    send_task_notification,
)
from ..validators import sanitize_for_log, validate_field_id

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Router Setup - إعداد الموجه
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v1", tags=["NDVI Integration"])


async def get_tenant_id(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> str:
    """Extract and validate tenant ID from request header.
    استخراج والتحقق من معرّف المستأجر من ترويسة الطلب.
    """
    if not x_tenant_id or x_tenant_id == "default":
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-Id header is required | ترويسة معرّف المستأجر مطلوبة",
        )

    # Validate UUID format to prevent injection of arbitrary strings
    import uuid as _uuid_mod

    try:
        _uuid_mod.UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-Id must be a valid UUID",
        )

    return x_tenant_id


# ═══════════════════════════════════════════════════════════════════════════
# Request/Response Models - نماذج الطلب/الاستجابة
# ═══════════════════════════════════════════════════════════════════════════


class NdviAlertTaskRequest(BaseModel):
    """Create task from NDVI alert - إنشاء مهمة من تنبيه NDVI"""

    field_id: str = Field(..., description="Field ID that triggered the alert")
    zone_id: str | None = Field(None, description="Specific zone within field")
    ndvi_value: float = Field(..., ge=-1, le=1, description="Current NDVI value")
    previous_ndvi: float | None = Field(None, ge=-1, le=1, description="Previous NDVI value for comparison")
    alert_type: str = Field(..., description="Alert type: 'drop', 'critical', 'anomaly'")
    auto_assign: bool = Field(default=False, description="Auto-assign to field manager")
    assigned_to: str | None = Field(None, description="Specific user to assign to")
    alert_metadata: dict | None = Field(None, description="Additional alert context (z_score, deviation_pct, etc.)")


class TaskSuggestion(BaseModel):
    """Task suggestion based on field health"""

    task_type: TaskType
    priority: TaskPriority
    title: str
    title_ar: str
    description: str
    description_ar: str
    reason: str
    reason_ar: str
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    suggested_due_days: int = Field(..., ge=1, description="Suggested days until due date")
    metadata: dict | None = None


class TaskAutoCreateRequest(BaseModel):
    """Batch create tasks from recommendations"""

    field_id: str = Field(..., description="Field ID for task creation")
    suggestions: list[TaskSuggestion] = Field(..., description="List of task suggestions")
    auto_assign: bool = Field(default=False, description="Auto-assign tasks to field manager")
    assigned_to: str | None = Field(None, description="Specific user to assign to")


# ═══════════════════════════════════════════════════════════════════════════
# NDVI Alert Endpoints - نقاط نهاية تنبيهات NDVI
# ═══════════════════════════════════════════════════════════════════════════


@router.post("/tasks/from-ndvi-alert", response_model=dict, status_code=201)
async def create_task_from_ndvi_alert(
    data: NdviAlertTaskRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create task from NDVI alert
    إنشاء مهمة من تنبيه NDVI

    Automatically creates a task when NDVI anomaly is detected:
    - Calculates priority based on severity
    - Generates Arabic and English descriptions
    - Auto-assigns if requested
    - Sends notifications
    """
    safe_field_id = sanitize_for_log(data.field_id)
    safe_alert_type = sanitize_for_log(str(data.alert_type))
    logger.info(
        f"Creating task from NDVI alert: field={safe_field_id}, type={safe_alert_type}, ndvi={data.ndvi_value:.3f}"
    )

    try:
        # Calculate priority based on NDVI severity
        priority = calculate_ndvi_priority(
            ndvi_value=data.ndvi_value,
            previous_ndvi=data.previous_ndvi,
            alert_type=data.alert_type,
            alert_metadata=data.alert_metadata,
        )

        # Generate task content in English and Arabic
        title, title_ar, description, description_ar = generate_ndvi_task_content(
            alert_type=data.alert_type,
            ndvi_value=data.ndvi_value,
            previous_ndvi=data.previous_ndvi,
            field_id=data.field_id,
            zone_id=data.zone_id,
        )

        # Determine task type based on NDVI value
        if data.ndvi_value < 0.3:
            task_type = TaskType.SCOUTING  # Critical - needs investigation
        elif data.alert_type == "drop":
            task_type = TaskType.IRRIGATION  # Likely water stress
        else:
            task_type = TaskType.SCOUTING  # General investigation

        # Calculate due date based on priority
        due_date = get_due_date_for_priority(priority)

        # Determine assignee
        assigned_to = data.assigned_to
        if data.auto_assign and not assigned_to:
            field_manager = await fetch_field_manager(data.field_id, tenant_id)
            if field_manager:
                assigned_to = field_manager
                logger.info("Auto-assigned NDVI task to field manager: %s", sanitize_for_log(assigned_to))
            else:
                logger.warning(
                    "Could not fetch field manager for field %s, task will be created without assignment",
                    safe_field_id,
                )

        # Build metadata
        metadata = {
            "source": "ndvi_alert",
            "alert_type": data.alert_type,
            "ndvi_value": data.ndvi_value,
            "previous_ndvi": data.previous_ndvi,
            **(data.alert_metadata or {}),
        }

        # Create task
        task_id = generate_task_id()
        task_data = TaskCreateData(
            tenant_id=tenant_id,
            title=title,
            title_ar=title_ar,
            description=description,
            description_ar=description_ar,
            task_type=task_type,
            priority=priority,
            field_id=data.field_id,
            zone_id=data.zone_id,
            assigned_to=assigned_to,
            created_by="system_ndvi",
            due_date=due_date,
            metadata=metadata,
        )

        db_task = create_task_model(task_data, task_id)
        repo = TaskRepository(db)
        created_task = repo.create_task(db_task)

        # Send notification if task is assigned
        if assigned_to:
            await send_task_notification(
                tenant_id=tenant_id,
                task_id=task_id,
                title=title,
                title_ar=title_ar,
                description=description,
                description_ar=description_ar,
                assigned_to=assigned_to,
                priority=priority,
                task_type=task_type,
                field_id=data.field_id,
                zone_id=data.zone_id,
                due_date=due_date,
                notification_type="ndvi_alert_task",
            )

        safe_assigned_to = sanitize_for_log(assigned_to) if assigned_to is not None else None
        logger.info(
            f"Task created from NDVI alert: {task_id} (priority={priority.value}, assigned_to={safe_assigned_to})"
        )

        return db_task_to_dict(created_task)

    except Exception as e:
        logger.error("Error creating task from NDVI alert: %s", type(e).__name__, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create task from NDVI alert",
                "error_ar": "فشل إنشاء المهمة من تنبيه NDVI",
            },
        )


# ═══════════════════════════════════════════════════════════════════════════
# Task Suggestions Endpoints - نقاط نهاية اقتراحات المهام
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/tasks/suggest-for-field/{field_id}", response_model=dict)
async def get_task_suggestions_for_field(
    field_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Get task suggestions based on field health
    الحصول على اقتراحات المهام بناءً على صحة الحقل

    Analyzes field's NDVI history and current status to suggest tasks:
    - Reviews recent NDVI trends
    - Identifies areas of concern
    - Suggests preventive and corrective actions
    - Returns prioritized list with confidence scores
    """
    safe_field_id = sanitize_for_log(field_id)
    logger.info("Generating task suggestions for field: %s", safe_field_id)

    try:
        # Import NDVI client
        from ..ndvi_client import get_ndvi_client, get_task_suggestions_from_health

        ndvi_client = get_ndvi_client()
        health_data = await ndvi_client.get_field_health(field_id)

        logger.info(
            "Field %s health: score=%s, status=%s",
            safe_field_id,
            health_data.health_score,
            health_data.health_status.value,
        )

        # Generate task suggestions
        raw_suggestions = get_task_suggestions_from_health(health_data)

        # Convert to TaskSuggestion objects
        suggestions = []
        task_type_map = {
            "scouting": TaskType.SCOUTING,
            "irrigation": TaskType.IRRIGATION,
            "sampling": TaskType.SAMPLING,
            "spraying": TaskType.SPRAYING,
            "fertilization": TaskType.FERTILIZATION,
            "harvest": TaskType.HARVEST,
            "other": TaskType.OTHER,
        }
        priority_map = {
            "urgent": TaskPriority.URGENT,
            "high": TaskPriority.HIGH,
            "medium": TaskPriority.MEDIUM,
            "low": TaskPriority.LOW,
        }

        for raw in raw_suggestions:
            task_type = task_type_map.get(raw.get("task_type", "other"), TaskType.OTHER)
            priority = priority_map.get(raw.get("priority", "medium"), TaskPriority.MEDIUM)

            suggestions.append(
                TaskSuggestion(
                    task_type=task_type,
                    priority=priority,
                    title=raw.get("title", ""),
                    title_ar=raw.get("title_ar", ""),
                    description=raw.get("description", ""),
                    description_ar=raw.get("description_ar", ""),
                    reason=raw.get("reason", ""),
                    reason_ar=raw.get("reason_ar", ""),
                    confidence=raw.get("confidence", 0.5),
                    suggested_due_days=raw.get("suggested_due_days", 3),
                    metadata={
                        "source": "ndvi_analysis",
                        "health_score": health_data.health_score,
                        "health_status": health_data.health_status.value,
                        "ndvi_mean": health_data.ndvi_mean,
                    },
                )
            )

        logger.info("Generated %d task suggestions for field %s", len(suggestions), safe_field_id)

        return {
            "field_id": field_id,
            "suggestions": [s.model_dump() for s in suggestions],
            "total": len(suggestions),
            "generated_at": datetime.now(UTC).isoformat(),
            "health_summary": {
                "score": health_data.health_score,
                "status": health_data.health_status.value,
                "needs_attention": health_data.needs_attention,
                "vegetation_coverage": health_data.vegetation_coverage,
            },
        }

    except Exception as e:
        logger.error("Error generating task suggestions: %s", type(e).__name__, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate task suggestions",
                "error_ar": "فشل إنشاء اقتراحات المهام",
            },
        )


@router.post("/tasks/auto-create", response_model=dict, status_code=201)
async def auto_create_tasks(
    data: TaskAutoCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Batch create tasks from recommendations
    إنشاء دفعة من المهام من التوصيات

    Creates multiple tasks at once from AI/ML recommendations:
    - Validates all suggestions
    - Creates tasks with appropriate priorities
    - Auto-assigns if requested
    - Sends batch notifications
    - Returns summary of created tasks
    """
    safe_field_id = sanitize_for_log(data.field_id)
    logger.info("Auto-creating %d tasks for field %s", len(data.suggestions), safe_field_id)

    created_tasks = []
    failed_tasks = []
    now = datetime.now(UTC)

    try:
        # Determine assignee
        assigned_to = data.assigned_to
        if data.auto_assign and not assigned_to:
            field_manager = await fetch_field_manager(data.field_id, tenant_id)
            if field_manager:
                assigned_to = field_manager
                logger.info("Auto-assigned batch tasks to field manager: %s", sanitize_for_log(assigned_to))
            else:
                logger.warning(
                    "Could not fetch field manager for field %s, tasks will be created without assignment",
                    safe_field_id,
                )

        repo = TaskRepository(db)

        # Create tasks from suggestions
        for idx, suggestion in enumerate(data.suggestions):
            try:
                due_date = now + timedelta(days=suggestion.suggested_due_days)
                task_id = generate_task_id()

                task_data = TaskCreateData(
                    tenant_id=tenant_id,
                    title=suggestion.title,
                    title_ar=suggestion.title_ar,
                    description=suggestion.description,
                    description_ar=suggestion.description_ar,
                    task_type=suggestion.task_type,
                    priority=suggestion.priority,
                    field_id=data.field_id,
                    assigned_to=assigned_to,
                    created_by="system_auto",
                    due_date=due_date,
                    metadata={
                        "source": "auto_create",
                        "confidence": suggestion.confidence,
                        "reason": suggestion.reason,
                        "reason_ar": suggestion.reason_ar,
                        **(suggestion.metadata or {}),
                    },
                )

                db_task = create_task_model(task_data, task_id)
                created_task = repo.create_task(db_task)
                created_tasks.append(db_task_to_dict(created_task))

                logger.info(
                    "Auto-created task %d/%d: %s (%s)",
                    idx + 1,
                    len(data.suggestions),
                    sanitize_for_log(task_id),
                    suggestion.task_type.value,
                )

            except Exception as task_error:
                logger.error("Failed to create task from suggestion %d: %s", idx, type(task_error).__name__)
                failed_tasks.append(
                    {
                        "index": idx,
                        "suggestion": suggestion.title,
                        "error": str(task_error),
                    }
                )

        # Send batch notification if tasks were created and assigned
        if created_tasks and assigned_to:
            try:
                await send_task_notification(
                    tenant_id=tenant_id,
                    task_id="batch_summary",
                    title=f"{len(created_tasks)} New Tasks Created",
                    title_ar=f"تم إنشاء {len(created_tasks)} مهمة جديدة",
                    description=f"Field {data.field_id} has {len(created_tasks)} new recommended tasks",
                    description_ar=f"الحقل {data.field_id} لديه {len(created_tasks)} مهمة موصى بها جديدة",
                    assigned_to=assigned_to,
                    priority=TaskPriority.MEDIUM,
                    task_type=TaskType.OTHER,
                    field_id=data.field_id,
                    zone_id=None,
                    due_date=None,
                    notification_type="tasks_batch_created",
                )
            except Exception as notif_error:
                logger.warning("Failed to send batch notification: %s", type(notif_error).__name__)

        logger.info("Auto-create completed: %d created, %d failed", len(created_tasks), len(failed_tasks))

        return {
            "field_id": data.field_id,
            "created": created_tasks,
            "failed": failed_tasks,
            "summary": {
                "total_requested": len(data.suggestions),
                "created_count": len(created_tasks),
                "failed_count": len(failed_tasks),
                "assigned_to": assigned_to,
            },
        }

    except Exception as e:
        logger.error("Error in auto-create tasks: %s", type(e).__name__, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to auto-create tasks",
                "error_ar": "فشل إنشاء المهام تلقائياً",
            },
        )


# ═══════════════════════════════════════════════════════════════════════════
# Field Health Endpoints - نقاط نهاية صحة الحقل
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/fields/{field_id}/health", response_model=dict)
async def get_field_health(
    field_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Get field health analysis from NDVI data
    الحصول على تحليل صحة الحقل من بيانات NDVI

    Returns comprehensive field health analysis including:
    - Health score (0-10)
    - Zone classification (healthy, stressed, critical)
    - NDVI statistics
    - Alerts and suggested actions
    """
    safe_field_id = sanitize_for_log(field_id)
    logger.info("Fetching health data for field: %s", safe_field_id)

    try:
        from ..ndvi_client import get_ndvi_client

        ndvi_client = get_ndvi_client()
        health_data = await ndvi_client.get_field_health(field_id)

        return {
            "field_id": field_id,
            "tenant_id": tenant_id,
            "health": health_data.to_dict(),
            "fetched_at": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error("Error fetching field health: %s", type(e).__name__, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch field health",
                "error_ar": "فشل جلب صحة الحقل",
            },
        )
