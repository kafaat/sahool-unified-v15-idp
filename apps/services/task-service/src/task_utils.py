"""
Task Utilities for Task Service - أدوات المهام لخدمة المهام

This module provides shared utilities for task creation, NDVI priority
calculation, content generation, and astronomical data enrichment.
Consolidates common logic to avoid code duplication across endpoints.
"""

import logging
import os
import re
import uuid
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum, StrEnum
from typing import Any

import httpx

from .exceptions import (
    AstronomicalServiceError,
    AstronomicalServiceTimeoutError,
    FieldServiceError,
    TaskCreationError,
)
from .validators import sanitize_for_log, validate_field_id

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Configuration - التكوين
# ═══════════════════════════════════════════════════════════════════════════

ASTRONOMICAL_SERVICE_URL = os.getenv("ASTRONOMICAL_SERVICE_URL", "http://astronomical-calendar:8111")
FIELD_SERVICE_URL = os.getenv("FIELD_SERVICE_URL", "http://field-service:8115")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8110")

# HTTP client timeout
HTTP_TIMEOUT = 10.0


# ═══════════════════════════════════════════════════════════════════════════
# Enums - التعدادات
# ═══════════════════════════════════════════════════════════════════════════


class TaskType(StrEnum):
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    SPRAYING = "spraying"
    SCOUTING = "scouting"
    MAINTENANCE = "maintenance"
    SAMPLING = "sampling"
    HARVEST = "harvest"
    PLANTING = "planting"
    OTHER = "other"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


# ═══════════════════════════════════════════════════════════════════════════
# Task Creation Data Classes - فئات بيانات إنشاء المهام
# ═══════════════════════════════════════════════════════════════════════════


class TaskCreateData:
    """
    Data transfer object for task creation
    كائن نقل البيانات لإنشاء المهمة
    """

    def __init__(
        self,
        tenant_id: str,
        title: str,
        task_type: TaskType,
        priority: TaskPriority = TaskPriority.MEDIUM,
        title_ar: str | None = None,
        description: str | None = None,
        description_ar: str | None = None,
        field_id: str | None = None,
        zone_id: str | None = None,
        assigned_to: str | None = None,
        created_by: str = "system",
        due_date: datetime | None = None,
        scheduled_time: str | None = None,
        estimated_duration_minutes: int | None = None,
        metadata: dict | None = None,
        # Astronomical fields
        astronomical_score: int | None = None,
        moon_phase_at_due_date: str | None = None,
        lunar_mansion_at_due_date: str | None = None,
        optimal_time_of_day: str | None = None,
        suggested_by_calendar: bool = False,
        astronomical_recommendation: dict | None = None,
        astronomical_warnings: list[str] | None = None,
    ):
        self.tenant_id = tenant_id
        self.title = title
        self.title_ar = title_ar
        self.description = description
        self.description_ar = description_ar
        self.task_type = task_type
        self.priority = priority
        self.field_id = field_id
        self.zone_id = zone_id
        self.assigned_to = assigned_to
        self.created_by = created_by
        self.due_date = due_date
        self.scheduled_time = scheduled_time
        self.estimated_duration_minutes = estimated_duration_minutes
        self.metadata = metadata or {}
        # Astronomical fields
        self.astronomical_score = astronomical_score
        self.moon_phase_at_due_date = moon_phase_at_due_date
        self.lunar_mansion_at_due_date = lunar_mansion_at_due_date
        self.optimal_time_of_day = optimal_time_of_day
        self.suggested_by_calendar = suggested_by_calendar
        self.astronomical_recommendation = astronomical_recommendation
        self.astronomical_warnings = astronomical_warnings or []


# ═══════════════════════════════════════════════════════════════════════════
# Task Creation Utilities - أدوات إنشاء المهام
# ═══════════════════════════════════════════════════════════════════════════


def generate_task_id() -> str:
    """
    Generate unique task ID
    إنشاء معرف مهمة فريد
    """
    return f"task_{uuid.uuid4().hex[:12]}"


def create_task_model(data: TaskCreateData, task_id: str | None = None):
    """
    Create a database task model from task data
    إنشاء نموذج مهمة قاعدة البيانات من بيانات المهمة

    Args:
        data: Task creation data
        task_id: Optional task ID (generated if not provided)

    Returns:
        TaskModel: Database model instance
    """
    from .models import Task as TaskModel

    if task_id is None:
        task_id = generate_task_id()

    task_type_value = data.task_type.value if isinstance(data.task_type, TaskType) else data.task_type
    priority_value = data.priority.value if isinstance(data.priority, TaskPriority) else data.priority

    return TaskModel(
        task_id=task_id,
        tenant_id=data.tenant_id,
        title=data.title,
        title_ar=data.title_ar,
        description=data.description,
        description_ar=data.description_ar,
        task_type=task_type_value,
        priority=priority_value,
        status="pending",
        field_id=data.field_id,
        zone_id=data.zone_id,
        assigned_to=data.assigned_to,
        created_by=data.created_by,
        due_date=data.due_date,
        scheduled_time=data.scheduled_time,
        estimated_duration_minutes=data.estimated_duration_minutes,
        task_metadata=data.metadata,
        # Astronomical fields
        astronomical_score=data.astronomical_score,
        moon_phase_at_due_date=data.moon_phase_at_due_date,
        lunar_mansion_at_due_date=data.lunar_mansion_at_due_date,
        optimal_time_of_day=data.optimal_time_of_day,
        suggested_by_calendar=data.suggested_by_calendar,
        astronomical_recommendation=data.astronomical_recommendation,
        astronomical_warnings=data.astronomical_warnings,
    )


def db_task_to_dict(db_task) -> dict[str, Any]:
    """
    Convert database task model to dictionary
    تحويل نموذج المهمة من قاعدة البيانات إلى قاموس

    Args:
        db_task: SQLAlchemy Task model instance

    Returns:
        dict: Task data as dictionary
    """
    return {
        "task_id": db_task.task_id,
        "tenant_id": db_task.tenant_id,
        "title": db_task.title,
        "title_ar": db_task.title_ar,
        "description": db_task.description,
        "description_ar": db_task.description_ar,
        "task_type": db_task.task_type,
        "priority": db_task.priority,
        "status": db_task.status,
        "field_id": db_task.field_id,
        "zone_id": db_task.zone_id,
        "assigned_to": db_task.assigned_to,
        "created_by": db_task.created_by,
        "due_date": db_task.due_date.isoformat() if db_task.due_date else None,
        "scheduled_time": db_task.scheduled_time,
        "estimated_duration_minutes": db_task.estimated_duration_minutes,
        "actual_duration_minutes": db_task.actual_duration_minutes,
        "created_at": db_task.created_at.isoformat() if db_task.created_at else None,
        "updated_at": db_task.updated_at.isoformat() if db_task.updated_at else None,
        "completed_at": db_task.completed_at.isoformat() if db_task.completed_at else None,
        "completion_notes": db_task.completion_notes,
        "metadata": db_task.task_metadata,
        "evidence": [
            {
                "evidence_id": e.evidence_id,
                "task_id": e.task_id,
                "type": e.type,
                "content": e.content,
                "captured_at": e.captured_at.isoformat() if e.captured_at else None,
                "location": e.location,
            }
            for e in (db_task.evidence or [])
        ],
        # Astronomical fields
        "astronomical_score": db_task.astronomical_score,
        "moon_phase_at_due_date": db_task.moon_phase_at_due_date,
        "lunar_mansion_at_due_date": db_task.lunar_mansion_at_due_date,
        "optimal_time_of_day": db_task.optimal_time_of_day,
        "suggested_by_calendar": db_task.suggested_by_calendar,
        "astronomical_recommendation": db_task.astronomical_recommendation,
        "astronomical_warnings": db_task.astronomical_warnings or [],
    }


# ═══════════════════════════════════════════════════════════════════════════
# NDVI Priority Calculation - حساب أولوية NDVI
# ═══════════════════════════════════════════════════════════════════════════


def calculate_ndvi_priority(
    ndvi_value: float,
    previous_ndvi: float | None = None,
    alert_type: str = "anomaly",
    alert_metadata: dict | None = None,
) -> TaskPriority:
    """
    Calculate task priority based on NDVI alert severity
    حساب أولوية المهمة بناءً على شدة تنبيه NDVI

    Priority is determined by:
    1. NDVI absolute value (< 0.3 is critical)
    2. Drop percentage from previous reading
    3. Z-score deviation (if available)

    Args:
        ndvi_value: Current NDVI value (-1 to 1)
        previous_ndvi: Previous NDVI value for comparison
        alert_type: Type of alert ("critical", "drop", "anomaly")
        alert_metadata: Additional metadata with z_score, deviation_pct

    Returns:
        TaskPriority: Calculated priority level
    """
    metadata = alert_metadata or {}

    # Critical NDVI values always get urgent priority
    if ndvi_value < 0.2:
        return TaskPriority.URGENT
    if ndvi_value < 0.3:
        return TaskPriority.HIGH

    # Check for significant drop
    if previous_ndvi is not None and previous_ndvi > 0:
        drop_pct = ((previous_ndvi - ndvi_value) / previous_ndvi) * 100

        if drop_pct >= 30:
            return TaskPriority.URGENT
        if drop_pct >= 20:
            return TaskPriority.HIGH
        if drop_pct >= 10:
            return TaskPriority.MEDIUM

    # Check z-score deviation
    z_score = metadata.get("z_score")
    if z_score is not None:
        if abs(z_score) >= 3:
            return TaskPriority.URGENT
        if abs(z_score) >= 2:
            return TaskPriority.HIGH
        if abs(z_score) >= 1.5:
            return TaskPriority.MEDIUM

    # Alert type-based fallback
    if alert_type == "critical":
        return TaskPriority.HIGH
    if alert_type == "drop":
        return TaskPriority.MEDIUM

    return TaskPriority.LOW


def generate_ndvi_task_content(
    alert_type: str,
    ndvi_value: float,
    previous_ndvi: float | None,
    field_id: str,
    zone_id: str | None = None,
) -> tuple[str, str, str, str]:
    """
    Generate task title and description for NDVI alerts
    إنشاء عنوان ووصف المهمة لتنبيهات NDVI

    Args:
        alert_type: Type of alert ("critical", "drop", "anomaly")
        ndvi_value: Current NDVI value
        previous_ndvi: Previous NDVI value
        field_id: Field identifier
        zone_id: Optional zone identifier

    Returns:
        tuple: (title, title_ar, description, description_ar)
    """
    # Sanitize field_id for display
    safe_field_id = sanitize_for_log(field_id, max_length=50)
    zone_text = f" (Zone: {zone_id})" if zone_id else ""
    zone_text_ar = f" (المنطقة: {zone_id})" if zone_id else ""

    if alert_type == "critical":
        title = f"Critical Vegetation Alert - Field {safe_field_id}{zone_text}"
        title_ar = f"تنبيه نباتي حرج - الحقل {safe_field_id}{zone_text_ar}"
        description = (
            f"Critical vegetation health detected (NDVI: {ndvi_value:.3f}). "
            f"Immediate field inspection required to assess:\n"
            f"• Crop damage extent\n"
            f"• Irrigation system functionality\n"
            f"• Signs of disease or pest infestation\n"
            f"• Environmental stress factors"
        )
        description_ar = (
            f"تم اكتشاف صحة نباتية حرجة (NDVI: {ndvi_value:.3f}). "
            f"مطلوب فحص فوري للحقل لتقييم:\n"
            f"• مدى ضرر المحصول\n"
            f"• وظائف نظام الري\n"
            f"• علامات المرض أو الإصابة بالآفات\n"
            f"• عوامل الإجهاد البيئي"
        )
    elif alert_type == "drop":
        drop_pct = 0.0
        if previous_ndvi and previous_ndvi > 0:
            drop_pct = ((previous_ndvi - ndvi_value) / previous_ndvi) * 100

        title = f"Vegetation Decline Detected - Field {safe_field_id}{zone_text}"
        title_ar = f"تم اكتشاف تراجع نباتي - الحقل {safe_field_id}{zone_text_ar}"
        description = (
            f"Vegetation index dropped {drop_pct:.1f}% "
            f"(from {previous_ndvi:.3f} to {ndvi_value:.3f}). "
            f"Scout the field to identify:\n"
            f"• Early signs of stress\n"
            f"• Irrigation effectiveness\n"
            f"• Pest pressure\n"
            f"• Growth stage issues"
        )
        description_ar = (
            f"انخفض مؤشر الغطاء النباتي بنسبة {drop_pct:.1f}% "
            f"(من {previous_ndvi:.3f} إلى {ndvi_value:.3f}). "
            f"افحص الحقل لتحديد:\n"
            f"• علامات الإجهاد المبكرة\n"
            f"• فعالية الري\n"
            f"• ضغط الآفات\n"
            f"• مشاكل مرحلة النمو"
        )
    else:  # anomaly
        title = f"Unusual Vegetation Pattern - Field {safe_field_id}{zone_text}"
        title_ar = f"نمط نباتي غير معتاد - الحقل {safe_field_id}{zone_text_ar}"
        description = (
            f"Abnormal vegetation reading detected (NDVI: {ndvi_value:.3f}). "
            f"Investigate potential causes:\n"
            f"• Localized stress areas\n"
            f"• Uneven irrigation\n"
            f"• Soil variability\n"
            f"• Equipment issues"
        )
        description_ar = (
            f"تم اكتشاف قراءة نباتية غير طبيعية (NDVI: {ndvi_value:.3f}). "
            f"ابحث عن الأسباب المحتملة:\n"
            f"• مناطق إجهاد موضعية\n"
            f"• ري غير متساوٍ\n"
            f"• تباين التربة\n"
            f"• مشاكل في المعدات"
        )

    return title, title_ar, description, description_ar


def get_due_date_for_priority(priority: TaskPriority) -> datetime:
    """
    Calculate due date based on task priority
    حساب تاريخ الاستحقاق بناءً على أولوية المهمة

    Args:
        priority: Task priority level

    Returns:
        datetime: Calculated due date
    """
    now = datetime.now(UTC)
    due_date_map = {
        TaskPriority.URGENT: timedelta(hours=4),
        TaskPriority.HIGH: timedelta(hours=12),
        TaskPriority.MEDIUM: timedelta(days=1),
        TaskPriority.LOW: timedelta(days=2),
    }
    return now + due_date_map.get(priority, timedelta(days=1))


# ═══════════════════════════════════════════════════════════════════════════
# Field Service Integration - تكامل خدمة الحقول
# ═══════════════════════════════════════════════════════════════════════════


async def fetch_field_manager(field_id: str, tenant_id: str) -> str | None:
    """
    Fetch field manager/owner from field service
    جلب مدير/مالك الحقل من خدمة الحقول

    Args:
        field_id: Field ID to look up
        tenant_id: Tenant ID for authentication

    Returns:
        str | None: User ID of the field manager, or None if not found
    """
    # Validate field_id format
    if not validate_field_id(field_id, raise_exception=False):
        logger.warning("Invalid field_id format detected")
        return None

    # Sanitize for URL and logging
    validated_field_id = re.sub(r"[^a-zA-Z0-9_-]", "", field_id)[:100]
    log_field_id = sanitize_for_log(field_id)

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(
                f"{FIELD_SERVICE_URL}/fields/{validated_field_id}",
                headers={
                    "X-Tenant-Id": tenant_id,
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                field_data = response.json()
                manager_id = field_data.get("user_id")
                if manager_id:
                    log_manager_id = sanitize_for_log(manager_id)
                    logger.info("Fetched field manager for field %s: %s", log_field_id, log_manager_id)
                    return manager_id
                else:
                    logger.warning("Field %s has no user_id/manager assigned", log_field_id)
                    return None

            elif response.status_code == 404:
                logger.warning("Field %s not found in field service", log_field_id)
                return None
            else:
                logger.error(
                    "Field service returned status %d for field %s",
                    response.status_code,
                    log_field_id,
                )
                return None

    except httpx.TimeoutException:
        logger.error("Timeout fetching field manager for field %s", log_field_id)
        return None
    except httpx.RequestError as e:
        logger.error("Error connecting to field service: %s", type(e).__name__)
        return None
    except Exception:
        logger.error("Unexpected error fetching field manager", exc_info=True)
        return None


# ═══════════════════════════════════════════════════════════════════════════
# Astronomical Service Integration - تكامل خدمة التقويم الفلكي
# ═══════════════════════════════════════════════════════════════════════════


def get_activity_translation(activity: str) -> tuple[str, str]:
    """
    Get Arabic and English translations for agricultural activity
    الحصول على الترجمة العربية والإنجليزية للنشاط الزراعي

    Args:
        activity: Activity name in Arabic or English

    Returns:
        Tuple of (english, arabic)
    """
    activity_map = {
        # Arabic to English
        "زراعة": ("planting", "زراعة"),
        "ري": ("irrigation", "ري"),
        "حصاد": ("harvest", "حصاد"),
        "تسميد": ("fertilization", "تسميد"),
        "تقليم": ("pruning", "تقليم"),
        "غرس": ("transplanting", "غرس"),
        "رش": ("spraying", "رش"),
        "فحص": ("scouting", "فحص"),
        "جمع عينات": ("sampling", "جمع عينات"),
        # English to Arabic
        "planting": ("planting", "زراعة"),
        "irrigation": ("irrigation", "ري"),
        "harvest": ("harvest", "حصاد"),
        "fertilization": ("fertilization", "تسميد"),
        "pruning": ("pruning", "تقليم"),
        "transplanting": ("transplanting", "غرس"),
        "spraying": ("spraying", "رش"),
        "scouting": ("scouting", "فحص"),
        "sampling": ("sampling", "جمع عينات"),
    }

    result = activity_map.get(activity.lower())
    if result:
        return result
    return (activity, activity)


def get_task_type_activity(task_type: TaskType) -> str:
    """
    Map task type to Arabic agricultural activity name
    تعيين نوع المهمة إلى اسم النشاط الزراعي بالعربية

    Args:
        task_type: Task type enum

    Returns:
        str: Arabic activity name
    """
    activity_map = {
        TaskType.PLANTING: "زراعة",
        TaskType.IRRIGATION: "ري",
        TaskType.HARVEST: "حصاد",
        TaskType.FERTILIZATION: "تسميد",
        TaskType.SPRAYING: "رش",
        TaskType.MAINTENANCE: "تقليم",
        TaskType.SCOUTING: "فحص",
        TaskType.SAMPLING: "جمع عينات",
        TaskType.OTHER: "زراعة",  # Default
    }
    return activity_map.get(task_type, "زراعة")


async def fetch_astronomical_best_days(activity: str, days: int = 30) -> dict:
    """
    Fetch best days for activity from astronomical calendar service
    جلب أفضل الأيام للنشاط من خدمة التقويم الفلكي

    Args:
        activity: Agricultural activity (زراعة، ري، حصاد، etc.)
        days: Number of days to search

    Returns:
        dict: Response from astronomical calendar service

    Raises:
        AstronomicalServiceError: If service returns error
        AstronomicalServiceTimeoutError: If service times out
    """
    # Check cache first
    from .cache import astronomical_cache

    cached = await astronomical_cache.get_best_days(activity, days)
    if cached:
        logger.info("Using cached astronomical data for %s", sanitize_for_log(activity))
        return cached

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(
                f"{ASTRONOMICAL_SERVICE_URL}/v1/best-days",
                params={"activity": activity, "days": days},
            )

            if response.status_code == 200:
                data = response.json()
                # Cache the result
                await astronomical_cache.set_best_days(activity, days, data)
                logger.info("Fetched and cached astronomical data for %s", sanitize_for_log(activity))
                return data
            else:
                logger.error(
                    "Astronomical service returned %d: %s",
                    response.status_code,
                    sanitize_for_log(str(response.text)[:200]),
                )
                raise AstronomicalServiceError(f"Service returned {response.status_code}")

    except httpx.TimeoutException:
        logger.error("Timeout connecting to astronomical calendar service")
        raise AstronomicalServiceTimeoutError()
    except httpx.RequestError as e:
        logger.error("Error connecting to astronomical service: %s", type(e).__name__)
        raise AstronomicalServiceError(str(e))


async def fetch_astronomical_daily_data(date_str: str) -> dict:
    """
    Fetch astronomical data for a specific date
    جلب البيانات الفلكية لتاريخ محدد

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        dict: Daily astronomical data

    Raises:
        AstronomicalServiceError: If service returns error
        AstronomicalServiceTimeoutError: If service times out
    """
    # Check cache first
    from .cache import astronomical_cache

    cached = await astronomical_cache.get_daily_data(date_str)
    if cached:
        logger.info("Using cached daily astronomical data for %s", sanitize_for_log(date_str))
        return cached

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(
                f"{ASTRONOMICAL_SERVICE_URL}/v1/daily",
                params={"date": date_str},
            )

            if response.status_code == 200:
                data = response.json()
                # Cache the result
                await astronomical_cache.set_daily_data(date_str, data)
                return data
            else:
                logger.error(f"Astronomical service returned {response.status_code}: {response.text}")
                raise AstronomicalServiceError(f"Service returned {response.status_code}")

    except httpx.TimeoutException:
        logger.error("Timeout connecting to astronomical calendar service")
        raise AstronomicalServiceTimeoutError()
    except httpx.RequestError as e:
        logger.error("Error connecting to astronomical service: %s", type(e).__name__)
        raise AstronomicalServiceError(str(e))


async def fetch_astronomical_data(due_date: datetime, task_type: TaskType) -> dict:
    """
    Fetch astronomical data from astronomical calendar service
    جلب البيانات الفلكية من خدمة التقويم الفلكي

    Args:
        due_date: Task due date
        task_type: Type of agricultural task

    Returns:
        dict: Astronomical data including score, moon phase, lunar mansion, etc.
    """
    try:
        activity = get_task_type_activity(task_type)
        date_str = due_date.strftime("%Y-%m-%d")

        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.get(f"{ASTRONOMICAL_SERVICE_URL}/v1/date/{date_str}")
            response.raise_for_status()
            astro_data = response.json()

            result = {
                "score": astro_data.get("overall_farming_score", 5),
                "moon_phase": astro_data.get("moon_phase", {}).get("name", ""),
                "moon_phase_ar": astro_data.get("moon_phase", {}).get("name", ""),
                "lunar_mansion": astro_data.get("lunar_mansion", {}).get("name", ""),
                "lunar_mansion_ar": astro_data.get("lunar_mansion", {}).get("name", ""),
                "farming_good": astro_data.get("moon_phase", {}).get("farming_good", True),
                "recommendations": astro_data.get("recommendations", []),
                "full_data": astro_data,
            }

            # Determine optimal time based on activity
            if activity in ["ري", "رش"]:
                result["optimal_time"] = "06:00-08:00"
            elif activity == "حصاد":
                result["optimal_time"] = "07:00-11:00"
            else:
                result["optimal_time"] = "07:00-10:00"

            # Add warnings for non-optimal conditions
            warnings = []
            if result["score"] < 5:
                warnings.append(f"التاريخ المحدد غير مثالي للنشاط ({activity}). الدرجة: {result['score']}/10")
                warnings.append(f"Selected date is not optimal for {task_type.value}. Score: {result['score']}/10")

            if not result["farming_good"]:
                warnings.append(f"مرحلة القمر ({result['moon_phase_ar']}) غير مناسبة للزراعة")
                warnings.append(f"Moon phase ({result['moon_phase']}) is not suitable for planting")

            result["warnings"] = warnings

            logger.info(
                f"Fetched astronomical data for {date_str}: score={result['score']}, "
                f"moon={result['moon_phase']}, mansion={result['lunar_mansion']}"
            )

            return result

    except httpx.HTTPError as e:
        logger.warning("Failed to fetch astronomical data: %s", type(e).__name__)
        return _empty_astronomical_data()
    except Exception as e:
        logger.error("Error fetching astronomical data: %s", type(e).__name__, exc_info=True)
        return _empty_astronomical_data()


def _empty_astronomical_data() -> dict:
    """Return empty astronomical data structure"""
    return {
        "score": None,
        "moon_phase": None,
        "moon_phase_ar": None,
        "lunar_mansion": None,
        "lunar_mansion_ar": None,
        "optimal_time": None,
        "warnings": [],
        "full_data": None,
    }


async def enrich_task_with_astronomy(task_data: TaskCreateData, task_type: TaskType) -> TaskCreateData:
    """
    Enrich task data with astronomical information
    إثراء بيانات المهمة بالمعلومات الفلكية

    Args:
        task_data: Task creation data to enrich
        task_type: Type of task for activity mapping

    Returns:
        TaskCreateData: Enriched task data
    """
    if not task_data.due_date:
        return task_data

    astro_data = await fetch_astronomical_data(task_data.due_date, task_type)

    task_data.astronomical_score = astro_data.get("score")
    task_data.moon_phase_at_due_date = astro_data.get("moon_phase_ar")
    task_data.lunar_mansion_at_due_date = astro_data.get("lunar_mansion_ar")
    task_data.optimal_time_of_day = astro_data.get("optimal_time")
    task_data.astronomical_recommendation = astro_data.get("full_data")
    task_data.astronomical_warnings = astro_data.get("warnings", [])

    if astro_data.get("score") and astro_data["score"] < 5:
        logger.warning(
            f"Task scheduled on non-optimal date: "
            f"score={astro_data['score']}/10, warnings={task_data.astronomical_warnings}"
        )

    return task_data


# ═══════════════════════════════════════════════════════════════════════════
# Notification Service Integration - تكامل خدمة الإشعارات
# ═══════════════════════════════════════════════════════════════════════════


async def send_task_notification(
    tenant_id: str,
    task_id: str,
    title: str,
    title_ar: str | None,
    description: str | None,
    description_ar: str | None,
    assigned_to: str | None,
    priority: TaskPriority,
    task_type: TaskType,
    field_id: str | None,
    zone_id: str | None,
    due_date: datetime | None,
    notification_type: str = "task_created",
) -> bool:
    """
    Send notification about task creation
    إرسال إشعار حول إنشاء المهمة

    Args:
        Various task fields for notification payload

    Returns:
        bool: Success status
    """
    try:
        # Import ServiceClient here to avoid circular imports
        import sys

        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

        try:
            from integration.client import ServiceName, get_service_client

            notification_client = get_service_client(ServiceName.NOTIFICATION)
        except ImportError:
            # Direct HTTP call fallback
            notification_client = None

        # Determine priority-based notification urgency
        priority_map = {
            TaskPriority.URGENT: "critical",
            TaskPriority.HIGH: "high",
            TaskPriority.MEDIUM: "medium",
            TaskPriority.LOW: "low",
        }

        notification_data = {
            "tenant_id": tenant_id,
            "user_id": assigned_to or "all",
            "title": title,
            "title_ar": title_ar,
            "body": description or "New task assigned",
            "body_ar": description_ar or "تم تعيين مهمة جديدة",
            "type": notification_type,
            "priority": priority_map.get(priority, "medium"),
            "channel": "in_app",
            "data": {
                "task_id": task_id,
                "field_id": field_id,
                "zone_id": zone_id,
                "task_type": task_type.value if isinstance(task_type, TaskType) else task_type,
                "due_date": due_date.isoformat() if due_date else None,
            },
            "action_url": f"/tasks/{task_id}",
        }

        log_task_id = sanitize_for_log(task_id)
        log_user_id = sanitize_for_log(assigned_to)

        if notification_client:
            response = await notification_client.post("/api/v1/notifications", json=notification_data)
            if response.success:
                logger.info("Notification sent for task %s to user %s", log_task_id, log_user_id)
                return True
            else:
                logger.warning("Failed to send notification for task %s", log_task_id)
                return False
        else:
            # Direct HTTP call
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.post(
                    f"{NOTIFICATION_SERVICE_URL}/api/v1/notifications",
                    json=notification_data,
                )
                if response.status_code in (200, 201):
                    logger.info("Notification sent for task %s", log_task_id)
                    return True
                else:
                    logger.warning("Notification failed: %d", response.status_code)
                    return False

    except Exception as e:
        logger.error("Error sending task notification: %s", type(e).__name__, exc_info=True)
        return False
