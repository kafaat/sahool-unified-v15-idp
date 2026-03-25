"""
Astronomical Task Routes - مسارات المهام الفلكية

This module provides astronomical calendar integration endpoints:
- Get best days for agricultural activities
- Create tasks with astronomical recommendations
- Validate date suitability for activities
"""

import logging
import os
import sys
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
from ..exceptions import (
    AstronomicalServiceError,
    AstronomicalServiceTimeoutError,
    InvalidDateFormatError,
)
from ..repository import TaskRepository
from ..task_utils import (
    TaskCreateData,
    TaskPriority,
    TaskType,
    create_task_model,
    db_task_to_dict,
    fetch_astronomical_best_days,
    fetch_astronomical_daily_data,
    generate_task_id,
    get_activity_translation,
)
from ..validators import sanitize_for_log, validate_date_string

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# Router Setup - إعداد الموجه
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v1/tasks", tags=["Astronomical Tasks"])


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
    return x_tenant_id


# ═══════════════════════════════════════════════════════════════════════════
# Request/Response Models - نماذج الطلب/الاستجابة
# ═══════════════════════════════════════════════════════════════════════════


class BestDayResponse(BaseModel):
    """Best day recommendation for agricultural activity - أفضل يوم للنشاط الزراعي"""

    date: str = Field(..., description="التاريخ الميلادي (YYYY-MM-DD)")
    date_ar: str = Field(..., description="التاريخ بالعربية")
    activity: str = Field(..., description="النشاط الزراعي")
    activity_ar: str = Field(..., description="النشاط بالعربية")
    score: int = Field(..., ge=1, le=10, description="درجة الملاءمة (1-10)")
    moon_phase: str = Field(..., description="مرحلة القمر")
    moon_phase_ar: str = Field(..., description="مرحلة القمر بالعربية")
    lunar_mansion: str = Field(..., description="المنزلة القمرية")
    lunar_mansion_ar: str = Field(..., description="المنزلة القمرية بالعربية")
    reason: str = Field(..., description="السبب باللغة الإنجليزية")
    reason_ar: str = Field(..., description="السبب بالعربية")
    best_time: str | None = Field(None, description="أفضل وقت في اليوم")
    hijri_date: str | None = Field(None, description="التاريخ الهجري")


class AstronomicalTaskCreateRequest(BaseModel):
    """Create task with astronomical recommendation - إنشاء مهمة مع توصية فلكية"""

    field_id: str = Field(..., description="معرف الحقل")
    task_type: TaskType = Field(..., description="نوع المهمة")
    title: str = Field(..., min_length=1, max_length=200, description="عنوان المهمة")
    title_ar: str | None = Field(None, description="عنوان المهمة بالعربية")
    description: str | None = Field(None, description="وصف المهمة")
    description_ar: str | None = Field(None, description="وصف المهمة بالعربية")
    activity: str = Field(
        ...,
        description="النشاط الفلكي: زراعة، ري، حصاد، تسميد، تقليم، غرس",
    )
    use_best_date: bool = Field(default=True, description="استخدام أفضل تاريخ من التقويم الفلكي")
    assigned_to: str | None = Field(None, description="المستخدم المعين للمهمة")
    zone_id: str | None = Field(None, description="معرف المنطقة")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="أولوية المهمة")
    estimated_duration_minutes: int | None = Field(None, ge=1, le=1440, description="المدة المقدرة بالدقائق")
    search_days: int = Field(default=30, ge=7, le=90, description="عدد الأيام للبحث عن أفضل تاريخ")


class DateValidationRequest(BaseModel):
    """Validate date suitability for activity - التحقق من ملاءمة التاريخ للنشاط"""

    date: str = Field(..., description="التاريخ للتحقق منه (YYYY-MM-DD)")
    activity: str = Field(..., description="النشاط: زراعة، ري، حصاد، تسميد، تقليم، غرس")


class DateValidationResponse(BaseModel):
    """Date validation result - نتيجة التحقق من التاريخ"""

    date: str = Field(..., description="التاريخ")
    activity: str = Field(..., description="النشاط")
    activity_ar: str = Field(..., description="النشاط بالعربية")
    is_suitable: bool = Field(..., description="هل التاريخ مناسب؟")
    score: int = Field(..., ge=1, le=10, description="درجة الملاءمة")
    moon_phase: str = Field(..., description="مرحلة القمر")
    moon_phase_ar: str = Field(..., description="مرحلة القمر بالعربية")
    lunar_mansion: str = Field(..., description="المنزلة القمرية")
    lunar_mansion_ar: str = Field(..., description="المنزلة القمرية بالعربية")
    recommendation: str = Field(..., description="التوصية بالإنجليزية")
    recommendation_ar: str = Field(..., description="التوصية بالعربية")
    best_time: str | None = Field(None, description="أفضل وقت")
    alternative_dates: list[str] = Field(default=[], description="تواريخ بديلة أفضل")


# ═══════════════════════════════════════════════════════════════════════════
# Endpoints - نقاط النهاية
# ═══════════════════════════════════════════════════════════════════════════


@router.get("/best-days/{activity}")
async def get_best_days_for_activity(
    activity: str,
    days: int = Query(30, ge=7, le=90, description="عدد الأيام للبحث"),
    min_score: int = Query(7, ge=1, le=10, description="الحد الأدنى لدرجة الملاءمة"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Get best days for agricultural activity from astronomical calendar
    الحصول على أفضل الأيام للنشاط الزراعي من التقويم الفلكي

    Supported activities:
    - زراعة (planting)
    - ري (irrigation)
    - حصاد (harvest)
    - تسميد (fertilization)
    - تقليم (pruning)
    - غرس (transplanting)
    """
    logger.info(
        "Fetching best days for activity: %s, days: %s, min_score: %s",
        sanitize_for_log(activity),
        sanitize_for_log(days),
        sanitize_for_log(min_score),
    )

    try:
        # Fetch from astronomical calendar service
        astro_data = await fetch_astronomical_best_days(activity, days)

        # Get activity translations
        activity_en, activity_ar = get_activity_translation(activity)

        # Transform the response
        best_days = []
        for day_data in astro_data.get("best_days", []):
            score = day_data.get("score", 0)
            if score >= min_score:
                best_day = BestDayResponse(
                    date=day_data["date"],
                    date_ar=day_data.get("hijri_date", day_data["date"]),
                    activity=activity_en,
                    activity_ar=activity_ar,
                    score=score,
                    moon_phase=day_data.get("moon_phase", "Unknown"),
                    moon_phase_ar=day_data.get("moon_phase", "غير معروف"),
                    lunar_mansion=day_data.get("lunar_mansion", "Unknown"),
                    lunar_mansion_ar=day_data.get("lunar_mansion", "غير معروف"),
                    reason=day_data.get("reason", f"Good day for {activity_en}"),
                    reason_ar=day_data.get("reason", f"يوم جيد لـ{activity_ar}"),
                    best_time=None,
                    hijri_date=day_data.get("hijri_date"),
                )
                best_days.append(best_day)

        return {
            "activity": activity_en,
            "activity_ar": activity_ar,
            "search_period_days": days,
            "min_score": min_score,
            "best_days": [day.model_dump() for day in best_days],
            "total_found": len(best_days),
            "message": f"وجدنا {len(best_days)} يوماً مناسباً لـ{activity_ar}",
            "message_en": f"Found {len(best_days)} suitable days for {activity_en}",
        }

    except AstronomicalServiceTimeoutError:
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Astronomical service timeout",
                "error_ar": "انتهت مهلة خدمة التقويم الفلكي",
            },
        )
    except AstronomicalServiceError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": str(e),
                "error_ar": "خدمة التقويم الفلكي غير متاحة",
            },
        )


@router.post("/create-with-astronomical", response_model=dict, status_code=201)
async def create_task_with_astronomical_recommendation(
    data: AstronomicalTaskCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create task with astronomical recommendation
    إنشاء مهمة مع توصية فلكية

    If use_best_date is True, the task will be scheduled on the best astronomical date.
    إذا كان use_best_date صحيحاً، سيتم جدولة المهمة في أفضل تاريخ فلكي.
    """
    logger.info(
        "Creating astronomical task for activity: %s, field: %s",
        sanitize_for_log(data.activity),
        sanitize_for_log(data.field_id),
    )

    now = datetime.now(UTC)
    task_id = generate_task_id()

    # Get activity translations
    activity_en, activity_ar = get_activity_translation(data.activity)

    # Determine due date
    due_date = None
    astronomical_metadata = {}

    if data.use_best_date:
        try:
            # Fetch best days from astronomical calendar
            astro_data = await fetch_astronomical_best_days(data.activity, data.search_days)

            best_days = astro_data.get("best_days", [])
            if best_days:
                # Use the first (best) day
                best_day = best_days[0]
                due_date_str = best_day["date"]
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").replace(tzinfo=UTC)

                # Store astronomical metadata
                astronomical_metadata = {
                    "astronomical_recommendation": True,
                    "selected_date": due_date_str,
                    "moon_phase": best_day.get("moon_phase"),
                    "lunar_mansion": best_day.get("lunar_mansion"),
                    "suitability_score": best_day.get("score"),
                    "reason": best_day.get("reason"),
                    "hijri_date": best_day.get("hijri_date"),
                }

                logger.info(
                    "Selected astronomical date: %s with score %s",
                    sanitize_for_log(due_date_str),
                    sanitize_for_log(best_day.get("score")),
                )
            else:
                logger.warning(
                    f"No suitable astronomical days found for {sanitize_for_log(data.activity)}, using default scheduling"
                )
                due_date = now + timedelta(days=7)
                astronomical_metadata = {
                    "astronomical_recommendation": False,
                    "reason": "No suitable astronomical days found in search period",
                    "reason_ar": "لم يتم العثور على أيام فلكية مناسبة في فترة البحث",
                }

        except (AstronomicalServiceError, AstronomicalServiceTimeoutError) as e:
            logger.warning("Astronomical service error: %s, using default scheduling", type(e).__name__)
            due_date = now + timedelta(days=7)
            astronomical_metadata = {
                "astronomical_recommendation": False,
                "reason": f"Astronomical service unavailable: {type(e).__name__}",
                "reason_ar": "خدمة التقويم الفلكي غير متاحة",
            }

    # Create task data
    task_data = TaskCreateData(
        tenant_id=tenant_id,
        title=data.title,
        title_ar=data.title_ar or f"{activity_ar} - {data.field_id}",
        description=data.description,
        description_ar=data.description_ar,
        task_type=data.task_type,
        priority=data.priority,
        field_id=data.field_id,
        zone_id=data.zone_id,
        assigned_to=data.assigned_to,
        created_by="user_system",
        due_date=due_date,
        scheduled_time=astronomical_metadata.get("best_time"),
        estimated_duration_minutes=data.estimated_duration_minutes,
        metadata=astronomical_metadata,
        astronomical_score=astronomical_metadata.get("suitability_score"),
        moon_phase_at_due_date=astronomical_metadata.get("moon_phase"),
        lunar_mansion_at_due_date=astronomical_metadata.get("lunar_mansion"),
        suggested_by_calendar=astronomical_metadata.get("astronomical_recommendation", False),
        astronomical_recommendation=astronomical_metadata,
    )

    # Create and save task
    db_task = create_task_model(task_data, task_id)
    repo = TaskRepository(db)
    created_task = repo.create_task(db_task)

    logger.info(
        "Created astronomical task %s with due date %s",
        sanitize_for_log(task_id),
        sanitize_for_log(due_date.isoformat() if due_date else "None"),
    )

    return db_task_to_dict(created_task)


@router.post("/validate-date", response_model=DateValidationResponse)
async def validate_date_for_activity(
    data: DateValidationRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """
    Validate date suitability for agricultural activity
    التحقق من ملاءمة التاريخ للنشاط الزراعي

    Returns suitability score and recommendations based on astronomical calendar.
    يُرجع درجة الملاءمة والتوصيات بناءً على التقويم الفلكي.
    """
    logger.info(
        "Validating date %s for activity %s",
        sanitize_for_log(data.date),
        sanitize_for_log(data.activity),
    )

    # Validate date format
    try:
        validate_date_string(data.date)
        datetime.strptime(data.date, "%Y-%m-%d")
    except (InvalidDateFormatError, ValueError):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid date format. Use YYYY-MM-DD",
                "error_ar": "تنسيق تاريخ غير صحيح. استخدم YYYY-MM-DD",
            },
        )

    # Get activity translations
    activity_en, activity_ar = get_activity_translation(data.activity)

    try:
        # Fetch astronomical data for the specific date
        daily_data = await fetch_astronomical_daily_data(data.date)

        # Extract relevant information
        moon_phase = daily_data.get("moon_phase", {})
        lunar_mansion = daily_data.get("lunar_mansion", {})
        recommendations = daily_data.get("recommendations", [])

        # Find recommendation for this activity
        activity_rec = None
        for rec in recommendations:
            if rec.get("activity") == data.activity or rec.get("activity") == activity_ar:
                activity_rec = rec
                break

        # Determine suitability
        if activity_rec:
            score = activity_rec.get("suitability_score", 5)
            is_suitable = score >= 7
            recommendation = activity_rec.get("reason", "")
            recommendation_ar = activity_rec.get("reason", "")
            best_time = activity_rec.get("best_time")
        else:
            # Default moderate score if no specific recommendation
            score = 5
            is_suitable = False
            recommendation = f"No specific recommendation for {activity_en} on this date"
            recommendation_ar = f"لا توجد توصية محددة لـ{activity_ar} في هذا التاريخ"
            best_time = None

        # Find alternative better dates if this date is not suitable
        alternative_dates = []
        if not is_suitable:
            try:
                astro_data = await fetch_astronomical_best_days(data.activity, 30)
                best_days = astro_data.get("best_days", [])[:3]
                alternative_dates = [day["date"] for day in best_days]
            except Exception as exc:
                logger.debug("Failed to fetch alternative dates: %s", exc)

        return DateValidationResponse(
            date=data.date,
            activity=activity_en,
            activity_ar=activity_ar,
            is_suitable=is_suitable,
            score=score,
            moon_phase=moon_phase.get("name", "Unknown"),
            moon_phase_ar=moon_phase.get("name_ar", "غير معروف"),
            lunar_mansion=lunar_mansion.get("name", "Unknown"),
            lunar_mansion_ar=lunar_mansion.get("name_ar", "غير معروف"),
            recommendation=recommendation,
            recommendation_ar=recommendation_ar,
            best_time=best_time,
            alternative_dates=alternative_dates,
        )

    except AstronomicalServiceTimeoutError:
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Astronomical service timeout",
                "error_ar": "انتهت مهلة خدمة التقويم الفلكي",
            },
        )
    except AstronomicalServiceError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "error": str(e),
                "error_ar": "خدمة التقويم الفلكي غير متاحة",
            },
        )
