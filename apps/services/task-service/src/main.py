"""
SAHOOL Task Service - خدمة إدارة المهام الزراعية
Port: 8103

Provides task management for agricultural operations:
- Task CRUD (create, read, update, delete)
- Task assignment and completion
- Evidence attachment (photos, notes)
- Task filtering and search
- NDVI-based task automation
- Astronomical calendar integration for optimal task scheduling
- Best day recommendations based on lunar cycles and mansions
"""

import logging
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Database imports
from .database import close_database, get_db, init_database, init_demo_data_if_needed
from .models import Task as TaskModel
from .repository import TaskRepository

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
try:
    from shared.middleware import (
        RequestLoggingMiddleware,
        TenantContextMiddleware,
        setup_cors,
    )
    from shared.observability.middleware import ObservabilityMiddleware
except ImportError:
    RequestLoggingMiddleware = None
    TenantContextMiddleware = None
    setup_cors = None
    ObservabilityMiddleware = None

# Import authentication dependencies and error handling
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    # Fallback if auth module not available
    AUTH_AVAILABLE = False
    User = None
    setup_exception_handlers = None
    add_request_id_middleware = None

    def get_current_user():
        """Placeholder when auth not available"""
        return None

# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers
    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False
    def setup_security_headers(app):
        pass


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Regex pattern for all ASCII control characters (0x00-0x1F and 0x7F)
_CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x1f\x7f]')


def _sanitize_for_log(value: str | None, max_length: int = 100) -> str:
    """
    Sanitize user input for safe logging to prevent log injection attacks.
    تعقيم المدخلات لمنع هجمات حقن السجلات

    This function removes ALL ASCII control characters (0x00-0x1F, 0x7F)
    to prevent log injection attacks including newline injection.

    Args:
        value: The input value to sanitize
        max_length: Maximum length of the output string

    Returns:
        A sanitized string safe for logging
    """
    if value is None:
        return "<none>"
    # Convert to string
    raw = str(value)
    # Remove ALL ASCII control characters using regex
    sanitized = _CONTROL_CHAR_PATTERN.sub('', raw)
    # Additional safety: keep only printable characters
    sanitized = ''.join(c for c in sanitized if c.isprintable())
    # Truncate to max length
    return sanitized[:max_length] if len(sanitized) > max_length else sanitized


# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "sahool-task-service"
SERVICE_PORT = int(os.getenv("PORT", "8103"))
ASTRONOMICAL_SERVICE_URL = os.getenv(
    "ASTRONOMICAL_SERVICE_URL", "http://astronomical-calendar:8111"
)
FIELD_SERVICE_URL = os.getenv(
    "FIELD_SERVICE_URL", "http://field-service:8115"
)

app = FastAPI(
    title="SAHOOL Task Service",
    description="Agricultural task management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
if setup_exception_handlers:
    setup_exception_handlers(app)
if add_request_id_middleware:
    add_request_id_middleware(app)

# CORS - Secure configuration
# In production, use explicit origins from environment or CORS_SETTINGS
try:
    from shared.cors_config import CORS_SETTINGS

    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
    # Fallback for standalone deployment
    ALLOWED_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
    )

# Security headers - رؤوس الأمان
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

# ═══════════════════════════════════════════════════════════════════════════
# Enums & Models
# ═══════════════════════════════════════════════════════════════════════════


class TaskType(str, Enum):
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    SPRAYING = "spraying"
    SCOUTING = "scouting"
    MAINTENANCE = "maintenance"
    SAMPLING = "sampling"
    HARVEST = "harvest"
    PLANTING = "planting"
    OTHER = "other"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class TaskCreate(BaseModel):
    """Create a new task"""

    title: str = Field(..., min_length=1, max_length=200)
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType = TaskType.OTHER
    priority: TaskPriority = TaskPriority.MEDIUM
    field_id: str | None = None
    zone_id: str | None = None
    assigned_to: str | None = None
    due_date: datetime | None = None
    scheduled_time: str | None = None  # HH:MM format
    estimated_duration_minutes: int | None = None
    metadata: dict | None = None

    # Astronomical fields (auto-populated if due_date is provided) - حقول فلكية
    astronomical_score: int | None = Field(
        None, ge=1, le=10, description="Astronomical score (1-10) - التصنيف الفلكي"
    )
    moon_phase_at_due_date: str | None = Field(None, description="Moon phase - مرحلة القمر")
    lunar_mansion_at_due_date: str | None = Field(
        None, description="Lunar mansion - المنزلة القمرية"
    )
    optimal_time_of_day: str | None = Field(
        None, description="Optimal time of day - أفضل وقت في اليوم"
    )
    suggested_by_calendar: bool = Field(
        False, description="Suggested by astronomical calendar - مقترح من التقويم الفلكي"
    )
    astronomical_recommendation: dict | None = Field(
        None, description="Full astronomical data - البيانات الفلكية الكاملة"
    )


class TaskUpdate(BaseModel):
    """Update task properties"""

    title: str | None = None
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType | None = None
    priority: TaskPriority | None = None
    field_id: str | None = None
    zone_id: str | None = None
    assigned_to: str | None = None
    due_date: datetime | None = None
    scheduled_time: str | None = None
    estimated_duration_minutes: int | None = None
    status: TaskStatus | None = None
    metadata: dict | None = None

    # Astronomical fields (auto-populated if due_date is changed) - حقول فلكية
    astronomical_score: int | None = Field(
        None, ge=1, le=10, description="Astronomical score (1-10) - التصنيف الفلكي"
    )
    moon_phase_at_due_date: str | None = Field(None, description="Moon phase - مرحلة القمر")
    lunar_mansion_at_due_date: str | None = Field(
        None, description="Lunar mansion - المنزلة القمرية"
    )
    optimal_time_of_day: str | None = Field(
        None, description="Optimal time of day - أفضل وقت في اليوم"
    )
    suggested_by_calendar: bool | None = Field(
        None, description="Suggested by astronomical calendar - مقترح من التقويم الفلكي"
    )
    astronomical_recommendation: dict | None = Field(
        None, description="Full astronomical data - البيانات الفلكية الكاملة"
    )


class TaskComplete(BaseModel):
    """Complete a task with evidence"""

    notes: str | None = None
    notes_ar: str | None = None
    photo_urls: list[str] | None = None
    actual_duration_minutes: int | None = None
    completion_metadata: dict | None = None


class NdviAlertTaskRequest(BaseModel):
    """Create task from NDVI alert - إنشاء مهمة من تنبيه NDVI"""

    field_id: str = Field(..., description="Field ID that triggered the alert")
    zone_id: str | None = Field(None, description="Specific zone within field")
    ndvi_value: float = Field(..., ge=-1, le=1, description="Current NDVI value")
    previous_ndvi: float | None = Field(
        None, ge=-1, le=1, description="Previous NDVI value for comparison"
    )
    alert_type: str = Field(..., description="Alert type: 'drop', 'critical', 'anomaly'")
    auto_assign: bool = Field(default=False, description="Auto-assign to field manager")
    assigned_to: str | None = Field(None, description="Specific user to assign to")
    alert_metadata: dict | None = Field(
        None, description="Additional alert context (z_score, deviation_pct, etc.)"
    )


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
    suggested_due_days: int = Field(..., description="Suggested days until due date")
    metadata: dict | None = None


class TaskAutoCreateRequest(BaseModel):
    """Batch create tasks from recommendations"""

    field_id: str = Field(..., description="Field ID for task creation")
    suggestions: list[TaskSuggestion] = Field(..., description="List of task suggestions to create")
    auto_assign: bool = Field(default=False, description="Auto-assign tasks to field manager")
    assigned_to: str | None = Field(None, description="Specific user to assign to")


class Evidence(BaseModel):
    """Evidence attached to a task"""

    evidence_id: str
    task_id: str
    type: str  # photo, note, voice, measurement
    content: str  # URL or text content
    captured_at: datetime
    location: dict | None = None  # {lat, lon}


class Task(BaseModel):
    """Full task model"""

    task_id: str
    tenant_id: str
    title: str
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    field_id: str | None = None
    zone_id: str | None = None
    assigned_to: str | None = None
    created_by: str
    due_date: datetime | None = None
    scheduled_time: str | None = None
    estimated_duration_minutes: int | None = None
    actual_duration_minutes: int | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    completion_notes: str | None = None
    evidence: list[Evidence] = []
    metadata: dict | None = None

    # Astronomical fields - البيانات الفلكية
    astronomical_score: int | None = Field(
        None, ge=1, le=10, description="Astronomical score (1-10) - التصنيف الفلكي"
    )
    moon_phase_at_due_date: str | None = Field(None, description="Moon phase - مرحلة القمر")
    lunar_mansion_at_due_date: str | None = Field(
        None, description="Lunar mansion - المنزلة القمرية"
    )
    optimal_time_of_day: str | None = Field(
        None, description="Optimal time of day - أفضل وقت في اليوم"
    )
    suggested_by_calendar: bool = Field(
        False, description="Suggested by astronomical calendar - مقترح من التقويم الفلكي"
    )
    astronomical_recommendation: dict | None = Field(
        None, description="Full astronomical data - البيانات الفلكية الكاملة"
    )
    astronomical_warnings: list[str] = Field(
        default_factory=list,
        description="Warnings about non-optimal dates - تحذيرات حول التواريخ غير المثالية",
    )


# ═══════════════════════════════════════════════════════════════════════════
# Astronomical-Based Task Models - نماذج المهام الفلكية
# ═══════════════════════════════════════════════════════════════════════════


class BestDayResponse(BaseModel):
    """Best day recommendation for agricultural activity - أفضل يوم موصى به للنشاط الزراعي"""

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


class AstronomicalTaskCreate(BaseModel):
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
    estimated_duration_minutes: int | None = Field(None, description="المدة المقدرة بالدقائق")
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
# PostgreSQL Database Storage - تخزين قاعدة بيانات PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════

# NOTE: All endpoints now use TaskRepository for PostgreSQL storage.
# In-memory storage has been fully migrated to persistent database storage.
# Data survives service restarts and supports multi-instance deployments.

# Astronomical data cache - التخزين المؤقت للبيانات الفلكية
# Cache format: {(activity, days): (data, timestamp)}
astronomical_cache: dict[tuple[str, int], tuple[dict, datetime]] = {}
CACHE_TTL_MINUTES = 60  # Cache for 1 hour


# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and create tables"""
    logger.info("Initializing task-service database...")
    try:
        init_database(create_tables=True)
        init_demo_data_if_needed()
        logger.info("Task-service database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        # Don't raise - allow service to start even if DB fails

    # Initialize NATS connection
    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
    logger.info(f"Connecting to NATS at {nats_url}...")
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from events import NatsPublisher
        from events.nats_publisher import set_publisher

        publisher = NatsPublisher()
        connected = await publisher.connect(nats_url)
        if connected:
            set_publisher(publisher)
            app.state.nats_publisher = publisher
            logger.info(f"✅ NATS connected: {nats_url}")
        else:
            app.state.nats_publisher = None
            logger.warning(f"⚠️ NATS connection failed: {nats_url}")
    except Exception as e:
        logger.warning(f"⚠️ NATS connection error: {e}")
        app.state.nats_publisher = None


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections and cleanup resources"""
    logger.info("Closing task-service database connections...")
    close_database()

    # Disconnect from NATS
    if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
        try:
            await app.state.nats_publisher.disconnect()
            logger.info("✅ NATS disconnected")
        except Exception as e:
            logger.error(f"❌ Error disconnecting from NATS: {e}")

    # Close NDVI client
    try:
        from .ndvi_client import close_ndvi_client

        await close_ndvi_client()
        logger.info("✅ NDVI client closed")
    except Exception as e:
        logger.warning(f"Could not close NDVI client: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


def get_tenant_id(
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
) -> str:
    """Extract tenant ID from authenticated user or X-Tenant-Id header (fallback)"""
    if AUTH_AVAILABLE and user:
        return user.tenant_id
    if not x_tenant_id:
        raise HTTPException(
            status_code=400, detail="X-Tenant-Id header is required or authentication required"
        )
    return x_tenant_id


def db_task_to_dict(task: TaskModel) -> dict:
    """Convert SQLAlchemy Task model to dictionary"""
    return {
        "task_id": task.task_id,
        "tenant_id": task.tenant_id,
        "title": task.title,
        "title_ar": task.title_ar,
        "description": task.description,
        "description_ar": task.description_ar,
        "task_type": task.task_type,
        "priority": task.priority,
        "status": task.status,
        "field_id": task.field_id,
        "zone_id": task.zone_id,
        "assigned_to": task.assigned_to,
        "created_by": task.created_by,
        "due_date": task.due_date,
        "scheduled_time": task.scheduled_time,
        "estimated_duration_minutes": task.estimated_duration_minutes,
        "actual_duration_minutes": task.actual_duration_minutes,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "completed_at": task.completed_at,
        "completion_notes": task.completion_notes,
        "metadata": task.task_metadata,
        "astronomical_score": task.astronomical_score,
        "moon_phase_at_due_date": task.moon_phase_at_due_date,
        "lunar_mansion_at_due_date": task.lunar_mansion_at_due_date,
        "optimal_time_of_day": task.optimal_time_of_day,
        "suggested_by_calendar": task.suggested_by_calendar,
        "astronomical_recommendation": task.astronomical_recommendation,
        "astronomical_warnings": task.astronomical_warnings or [],
        "evidence": [
            {
                "evidence_id": e.evidence_id,
                "task_id": e.task_id,
                "type": e.type,
                "content": e.content,
                "captured_at": e.captured_at,
                "location": e.location,
            }
            for e in task.evidence
        ],
    }


def calculate_ndvi_priority(
    ndvi_value: float,
    previous_ndvi: float | None,
    alert_type: str,
    alert_metadata: dict | None = None,
) -> TaskPriority:
    """
    Calculate task priority based on NDVI severity
    حساب أولوية المهمة بناءً على خطورة NDVI

    Args:
        ndvi_value: Current NDVI value
        previous_ndvi: Previous NDVI value for comparison
        alert_type: Type of alert (drop, critical, anomaly)
        alert_metadata: Additional metadata (z_score, deviation_pct)

    Returns:
        TaskPriority: Calculated priority level
    """
    # Critical NDVI levels (below 0.2 indicates severe stress)
    if ndvi_value < 0.2:
        logger.info(f"Critical NDVI detected: {ndvi_value:.3f} - Setting URGENT priority")
        return TaskPriority.URGENT

    # Significant drop detection
    if previous_ndvi is not None:
        drop_pct = ((previous_ndvi - ndvi_value) / previous_ndvi) * 100
        if drop_pct > 30:  # >30% drop
            logger.info(f"Severe NDVI drop: {drop_pct:.1f}% - Setting URGENT priority")
            return TaskPriority.URGENT
        elif drop_pct > 20:  # 20-30% drop
            logger.info(f"Significant NDVI drop: {drop_pct:.1f}% - Setting HIGH priority")
            return TaskPriority.HIGH

    # Alert type based priority
    if alert_type == "critical":
        return TaskPriority.URGENT
    elif alert_type == "drop":
        # Check severity from metadata
        if alert_metadata:
            deviation_pct = alert_metadata.get("deviation_pct", 0)
            if abs(deviation_pct) > 25:
                return TaskPriority.HIGH
        return TaskPriority.MEDIUM

    # Anomaly detection
    if alert_type == "anomaly" and alert_metadata:
        z_score = abs(alert_metadata.get("z_score", 0))
        if z_score > 3:  # 3 sigma outlier
            return TaskPriority.HIGH
        elif z_score > 2:  # 2 sigma outlier
            return TaskPriority.MEDIUM

    # Default for moderate concerns
    return TaskPriority.MEDIUM


def generate_ndvi_task_content(
    alert_type: str,
    ndvi_value: float,
    previous_ndvi: float | None,
    field_id: str,
    zone_id: str | None,
) -> tuple[str, str, str, str]:
    """
    Generate task title and description in English and Arabic
    إنشاء عنوان ووصف المهمة بالإنجليزية والعربية

    Returns:
        Tuple of (title, title_ar, description, description_ar)
    """
    # Calculate drop percentage if available
    drop_pct = 0.0
    if previous_ndvi is not None:
        drop_pct = ((previous_ndvi - ndvi_value) / previous_ndvi) * 100

    zone_text = f" - Zone {zone_id}" if zone_id else ""
    zone_text_ar = f" - المنطقة {zone_id}" if zone_id else ""

    # Generate content based on alert type
    if alert_type == "critical":
        title = f"URGENT: Critical Plant Health{zone_text}"
        title_ar = f"عاجل: صحة نباتية حرجة{zone_text_ar}"
        description = (
            f"Field vegetation health is critically low (NDVI: {ndvi_value:.3f}). "
            f"Immediate investigation required. Check for:\n"
            f"• Water stress or irrigation issues\n"
            f"• Pest or disease outbreak\n"
            f"• Nutrient deficiency\n"
            f"• Environmental stress"
        )
        description_ar = (
            f"صحة النباتات في حالة حرجة (NDVI: {ndvi_value:.3f}). "
            f"يتطلب فحص فوري. تحقق من:\n"
            f"• إجهاد مائي أو مشاكل الري\n"
            f"• انتشار آفات أو أمراض\n"
            f"• نقص العناصر الغذائية\n"
            f"• إجهاد بيئي"
        )
    elif alert_type == "drop":
        title = f"Vegetation Health Decline{zone_text}"
        title_ar = f"تراجع في الصحة النباتية{zone_text_ar}"
        if previous_ndvi:
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
        else:
            description = (
                f"Vegetation health below expected (NDVI: {ndvi_value:.3f}). "
                f"Field inspection recommended."
            )
            description_ar = (
                f"الصحة النباتية أقل من المتوقع (NDVI: {ndvi_value:.3f}). يُنصح بفحص الحقل."
            )
    else:  # anomaly
        title = f"Unusual Vegetation Pattern{zone_text}"
        title_ar = f"نمط نباتي غير معتاد{zone_text_ar}"
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


async def send_task_notification(
    tenant_id: str,
    task: Task,
    notification_type: str = "task_created",
) -> bool:
    """
    Send notification about task creation
    إرسال إشعار حول إنشاء المهمة

    Args:
        tenant_id: Tenant ID
        task: Created task
        notification_type: Type of notification

    Returns:
        bool: Success status
    """
    try:
        # Import ServiceClient here to avoid circular imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
        from integration.client import ServiceName, get_service_client

        notification_client = get_service_client(ServiceName.NOTIFICATION)

        # Determine priority-based notification urgency
        priority_map = {
            TaskPriority.URGENT: "critical",
            TaskPriority.HIGH: "high",
            TaskPriority.MEDIUM: "medium",
            TaskPriority.LOW: "low",
        }

        # Build notification payload
        notification_data = {
            "tenant_id": tenant_id,
            "user_id": task.assigned_to or "all",
            "title": task.title,
            "title_ar": task.title_ar,
            "body": task.description or "New task assigned",
            "body_ar": task.description_ar or "تم تعيين مهمة جديدة",
            "type": notification_type,
            "priority": priority_map.get(task.priority, "medium"),
            "channel": "in_app",
            "data": {
                "task_id": task.task_id,
                "field_id": task.field_id,
                "zone_id": task.zone_id,
                "task_type": task.task_type.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
            },
            "action_url": f"/tasks/{task.task_id}",
        }

        response = await notification_client.post("/api/v1/notifications", json=notification_data)

        if response.success:
            logger.info(f"Notification sent for task {task.task_id} to user {task.assigned_to}")
            return True
        else:
            logger.warning(f"Failed to send notification for task {task.task_id}: {response.error}")
            return False

    except Exception as e:
        logger.error(f"Error sending task notification: {e}", exc_info=True)
        return False


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
    # Validate and sanitize field_id to prevent SSRF
    if not field_id or not re.match(r'^[a-zA-Z0-9_-]+$', field_id):
        logger.warning("Invalid field_id format detected")
        return None

    # Create validated copy for URL (SSRF prevention)
    validated_field_id = field_id[:100]
    # Create sanitized version for logging (log injection prevention)
    log_field_id = _sanitize_for_log(field_id)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{FIELD_SERVICE_URL}/fields/{validated_field_id}",
                headers={
                    "X-Tenant-Id": tenant_id,
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                field_data = response.json()
                # The field service returns user_id as the field owner/manager
                manager_id = field_data.get("user_id")
                if manager_id:
                    log_manager_id = _sanitize_for_log(manager_id)
                    logger.info(
                        "Fetched field manager for field %s: %s", log_field_id, log_manager_id
                    )
                    return manager_id
                else:
                    logger.warning(
                        "Field %s has no user_id/manager assigned", log_field_id
                    )
                    return None
            elif response.status_code == 404:
                logger.warning("Field %s not found in field service", log_field_id)
                return None
            else:
                logger.error(
                    "Field service returned status %d for field %s",
                    response.status_code, log_field_id
                )
                return None

    except httpx.TimeoutException:
        logger.error("Timeout fetching field manager for field %s", log_field_id)
        return None
    except httpx.RequestError as e:
        logger.error("Error connecting to field service: %s", type(e).__name__)
        return None
    except Exception as e:
        logger.error("Unexpected error fetching field manager", exc_info=True)
        return None


# ═══════════════════════════════════════════════════════════════════════════
# Astronomical Service Integration - تكامل خدمة التقويم الفلكي
# ═══════════════════════════════════════════════════════════════════════════


def get_activity_translation(activity: str) -> tuple[str, str]:
    """
    Get Arabic and English translations for activity
    الحصول على الترجمة العربية والإنجليزية للنشاط

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
        # English to Arabic
        "planting": ("planting", "زراعة"),
        "irrigation": ("irrigation", "ري"),
        "harvest": ("harvest", "حصاد"),
        "fertilization": ("fertilization", "تسميد"),
        "pruning": ("pruning", "تقليم"),
        "transplanting": ("transplanting", "غرس"),
    }

    result = activity_map.get(activity.lower())
    if result:
        return result
    # Default if not found
    return (activity, activity)


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
        HTTPException: If service is unavailable or returns error
    """
    # Check cache first
    cache_key = (activity, days)
    if cache_key in astronomical_cache:
        cached_data, cached_time = astronomical_cache[cache_key]
        if datetime.now(timezone.utc) - cached_time < timedelta(minutes=CACHE_TTL_MINUTES):
            logger.info(f"Using cached astronomical data for {activity}")
            return cached_data

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{ASTRONOMICAL_SERVICE_URL}/v1/best-days",
                params={"activity": activity, "days": days},
            )

            if response.status_code == 200:
                data = response.json()
                # Cache the result
                astronomical_cache[cache_key] = (data, datetime.now(timezone.utc))
                logger.info(f"Fetched and cached astronomical data for {activity}")
                return data
            else:
                logger.error(
                    f"Astronomical service returned {response.status_code}: {response.text}"
                )
                raise HTTPException(
                    status_code=502,
                    detail=f"Astronomical service error: {response.status_code}",
                )

    except httpx.TimeoutException:
        logger.error("Timeout connecting to astronomical calendar service")
        raise HTTPException(
            status_code=504,
            detail="خدمة التقويم الفلكي غير متاحة حالياً - Astronomical service timeout",
        )
    except httpx.RequestError as e:
        logger.error(f"Error connecting to astronomical service: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"خدمة التقويم الفلكي غير متاحة - Astronomical service unavailable: {str(e)}",
        )


async def fetch_astronomical_daily_data(date_str: str) -> dict:
    """
    Fetch astronomical data for a specific date
    جلب البيانات الفلكية لتاريخ محدد

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        dict: Daily astronomical data

    Raises:
        HTTPException: If service is unavailable
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{ASTRONOMICAL_SERVICE_URL}/v1/daily",
                params={"date": date_str},
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Astronomical service returned {response.status_code}: {response.text}"
                )
                raise HTTPException(
                    status_code=502,
                    detail=f"Astronomical service error: {response.status_code}",
                )

    except httpx.TimeoutException:
        logger.error("Timeout connecting to astronomical calendar service")
        raise HTTPException(
            status_code=504,
            detail="خدمة التقويم الفلكي غير متاحة حالياً - Astronomical service timeout",
        )
    except httpx.RequestError as e:
        logger.error(f"Error connecting to astronomical service: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"خدمة التقويم الفلكي غير متاحة - Astronomical service unavailable: {str(e)}",
        )


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
        # Map task type to agricultural activity in Arabic
        activity_map = {
            TaskType.PLANTING: "زراعة",
            TaskType.IRRIGATION: "ري",
            TaskType.HARVEST: "حصاد",
            TaskType.FERTILIZATION: "تسميد",
            TaskType.SPRAYING: "رش",
            TaskType.MAINTENANCE: "تقليم",
            TaskType.SCOUTING: "فحص",
            TaskType.SAMPLING: "جمع عينات",
            TaskType.OTHER: "زراعة",  # Default to planting
        }

        activity = activity_map.get(task_type, "زراعة")
        date_str = due_date.strftime("%Y-%m-%d")

        # Fetch astronomical data for the specific date
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ASTRONOMICAL_SERVICE_URL}/v1/date/{date_str}")
            response.raise_for_status()
            astro_data = response.json()

            # Extract relevant fields
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

            # Determine optimal time based on season and activity
            astro_data.get("season", {})
            if activity in ["ري", "رش"]:
                result["optimal_time"] = "06:00-08:00"  # Early morning for irrigation/spraying
            elif activity == "حصاد":
                result["optimal_time"] = "07:00-11:00"  # Morning for harvesting
            else:
                result["optimal_time"] = "07:00-10:00"  # General morning work

            # Add warnings for non-optimal conditions
            warnings = []
            if result["score"] < 5:
                warnings.append(
                    f"التاريخ المحدد غير مثالي للنشاط ({activity}). الدرجة: {result['score']}/10"
                )
                warnings.append(
                    f"Selected date is not optimal for {task_type.value}. Score: {result['score']}/10"
                )

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
        logger.warning(f"Failed to fetch astronomical data: {e}")
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
    except Exception as e:
        logger.error(f"Error fetching astronomical data: {e}", exc_info=True)
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


async def validate_and_enrich_task_with_astronomy(task: Task, task_type: TaskType) -> Task:
    """
    Validate task due date against astronomical calendar and enrich with astronomical data
    التحقق من تاريخ المهمة مقابل التقويم الفلكي وإثرائها بالبيانات الفلكية

    Args:
        task: Task to validate and enrich
        task_type: Type of task for activity mapping

    Returns:
        Task: Enriched task with astronomical data
    """
    if not task.due_date:
        return task

    astro_data = await fetch_astronomical_data(task.due_date, task_type)

    # Update task with astronomical data
    task.astronomical_score = astro_data.get("score")
    task.moon_phase_at_due_date = astro_data.get("moon_phase_ar")
    task.lunar_mansion_at_due_date = astro_data.get("lunar_mansion_ar")
    task.optimal_time_of_day = astro_data.get("optimal_time")
    task.astronomical_recommendation = astro_data.get("full_data")
    task.astronomical_warnings = astro_data.get("warnings", [])

    # Log if date is not optimal
    if astro_data.get("score") and astro_data["score"] < 5:
        logger.warning(
            f"Task {task.task_id} scheduled on non-optimal date: "
            f"score={astro_data['score']}/10, warnings={task.astronomical_warnings}"
        )

    return task


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/healthz")
async def health_check():
    """Health check endpoint (liveness probe)"""
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": "16.0.0",
    }


@app.get("/readyz")
async def readiness_check():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    nats_status = "disconnected"
    if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
        nats_status = "connected" if app.state.nats_publisher.connected else "disconnected"

    # Check database connection
    db_ok = True
    try:
        from .database import engine
        if engine:
            db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ready" if db_ok else "not_ready",
        "service": SERVICE_NAME,
        "version": "16.0.0",
        "checks": {
            "database": "connected" if db_ok else "disconnected",
            "nats": nats_status,
        },
    }


@app.get("/api/v1/tasks", response_model=dict)
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
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """List tasks with optional filters"""
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


@app.get("/api/v1/tasks/today", response_model=dict)
async def get_today_tasks(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get tasks due today"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    repo = TaskRepository(db)
    tasks, _ = repo.list_tasks(
        tenant_id=tenant_id,
        due_after=today_start,
        due_before=today_end,
        limit=100,
    )

    return {
        "tasks": [db_task_to_dict(t) for t in tasks],
        "count": len(tasks),
    }


@app.get("/api/v1/tasks/upcoming", response_model=dict)
async def get_upcoming_tasks(
    days: int = Query(7, ge=1, le=30),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get upcoming tasks for the next N days"""
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=days)
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    repo = TaskRepository(db)
    # Get pending and in_progress tasks for the upcoming period
    tasks, _ = repo.list_tasks(
        tenant_id=tenant_id,
        due_after=tomorrow,
        due_before=future,
        limit=100,
    )

    # Filter out completed and cancelled tasks
    upcoming = [
        t for t in tasks
        if t.status not in ["completed", "cancelled"]
    ]

    return {
        "tasks": [db_task_to_dict(t) for t in upcoming],
        "count": len(upcoming),
        "days": days,
    }


@app.get("/api/v1/tasks/stats", response_model=dict)
async def get_task_stats(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get task statistics"""
    repo = TaskRepository(db)
    return repo.get_task_stats(tenant_id)


@app.get("/api/v1/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get a specific task by ID"""
    repo = TaskRepository(db)
    task = repo.get_task_by_id(task_id, tenant_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task_to_dict(task)


@app.post("/api/v1/tasks", response_model=Task, status_code=201)
async def create_task(
    data: TaskCreate,
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a new task"""
    now = datetime.now(timezone.utc)
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    created_by = user.id if user else "user_system"

    # Create SQLAlchemy Task model for database
    db_task = TaskModel(
        task_id=task_id,
        tenant_id=tenant_id,
        title=data.title,
        title_ar=data.title_ar,
        description=data.description,
        description_ar=data.description_ar,
        task_type=data.task_type.value if isinstance(data.task_type, TaskType) else data.task_type,
        priority=data.priority.value if isinstance(data.priority, TaskPriority) else data.priority,
        status="pending",
        field_id=data.field_id,
        zone_id=data.zone_id,
        assigned_to=data.assigned_to,
        created_by=created_by,
        due_date=data.due_date,
        scheduled_time=data.scheduled_time,
        estimated_duration_minutes=data.estimated_duration_minutes,
        task_metadata=data.metadata,
        # Astronomical fields
        astronomical_score=data.astronomical_score,
        moon_phase_at_due_date=data.moon_phase_at_due_date,
        lunar_mansion_at_due_date=data.lunar_mansion_at_due_date,
        optimal_time_of_day=data.optimal_time_of_day,
        suggested_by_calendar=data.suggested_by_calendar or False,
        astronomical_recommendation=data.astronomical_recommendation,
    )

    # Fetch and populate astronomical data if due_date is provided
    if data.due_date:
        # Create a temporary Pydantic task to use the astronomical function
        temp_task = Task(
            task_id=task_id,
            tenant_id=tenant_id,
            title=data.title,
            task_type=data.task_type,
            priority=data.priority,
            status=TaskStatus.PENDING,
            due_date=data.due_date,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )
        enriched_task = await validate_and_enrich_task_with_astronomy(temp_task, data.task_type)
        # Copy astronomical fields back to db_task
        db_task.astronomical_score = enriched_task.astronomical_score
        db_task.moon_phase_at_due_date = enriched_task.moon_phase_at_due_date
        db_task.lunar_mansion_at_due_date = enriched_task.lunar_mansion_at_due_date
        db_task.optimal_time_of_day = enriched_task.optimal_time_of_day
        db_task.suggested_by_calendar = enriched_task.suggested_by_calendar
        db_task.astronomical_recommendation = enriched_task.astronomical_recommendation
        db_task.astronomical_warnings = enriched_task.astronomical_warnings

    # Save to database using repository
    repo = TaskRepository(db)
    created_task = repo.create_task(db_task)

    # Publish task created event
    if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
        try:
            from events import publish_task_created

            await publish_task_created(
                task_id=task_id,
                tenant_id=tenant_id,
                task_type=created_task.task_type,
                priority=created_task.priority,
                field_id=created_task.field_id,
                assigned_to=created_task.assigned_to,
                due_date=created_task.due_date.isoformat() if created_task.due_date else None,
            )
        except Exception as e:
            logger.warning(f"Failed to publish task_created event: {e}")

    return db_task_to_dict(created_task)


@app.put("/api/v1/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    db: Session = Depends(get_db),
):
    """Update a task"""
    repo = TaskRepository(db)
    performed_by = user.id if user else "system"

    # Prepare update data, converting enums to strings
    update_data = data.model_dump(exclude_unset=True)
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
        raise HTTPException(status_code=404, detail="Task not found")

    # Publish task updated event
    if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
        try:
            from events import publish_task_updated

            await publish_task_updated(
                task_id=task_id,
                tenant_id=tenant_id,
                changes=update_data,
            )
        except Exception as e:
            logger.warning(f"Failed to publish task_updated event: {e}")

    return db_task_to_dict(task)


@app.post("/api/v1/tasks/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: str,
    data: TaskComplete,
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    db: Session = Depends(get_db),
):
    """Mark a task as completed with evidence"""
    repo = TaskRepository(db)
    performed_by = user.id if user else "system"
    now = datetime.now(timezone.utc)

    # Complete the task
    task = repo.complete_task(
        task_id=task_id,
        tenant_id=tenant_id,
        performed_by=performed_by,
        notes=data.notes or data.notes_ar,
        actual_duration_minutes=data.actual_duration_minutes,
        completion_metadata=data.completion_metadata,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Add photo evidence if provided
    if data.photo_urls:
        from .models import TaskEvidence
        for url in data.photo_urls:
            evidence = TaskEvidence(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                task_id=task_id,
                type="photo",
                content=url,
                captured_at=now,
            )
            repo.add_evidence(evidence)

    # Publish task completed event
    if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
        try:
            from events import publish_task_completed

            await publish_task_completed(
                task_id=task_id,
                tenant_id=tenant_id,
                completed_by=task.assigned_to or "system",
                actual_duration_minutes=data.actual_duration_minutes,
            )
        except Exception as e:
            logger.warning(f"Failed to publish task_completed event: {e}")

    return db_task_to_dict(task)


@app.post("/api/v1/tasks/{task_id}/start", response_model=Task)
async def start_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    db: Session = Depends(get_db),
):
    """Mark a task as in progress"""
    repo = TaskRepository(db)
    performed_by = user.id if user else "system"

    try:
        task = repo.start_task(task_id, tenant_id, performed_by)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Publish task started event
        if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
            try:
                from events import publish_task_started

                await publish_task_started(
                    task_id=task_id,
                    tenant_id=tenant_id,
                    started_by=task.assigned_to or "system",
                )
            except Exception as e:
                logger.warning(f"Failed to publish task_started event: {e}")

        return db_task_to_dict(task)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/tasks/{task_id}/cancel", response_model=Task)
async def cancel_task(
    task_id: str,
    reason: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
    db: Session = Depends(get_db),
):
    """Cancel a task"""
    repo = TaskRepository(db)
    performed_by = user.id if user else "system"

    task = repo.cancel_task(task_id, tenant_id, performed_by, reason)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Publish task cancelled event
    if hasattr(app.state, "nats_publisher") and app.state.nats_publisher:
        try:
            from events import publish_task_cancelled

            await publish_task_cancelled(
                task_id=task_id,
                tenant_id=tenant_id,
                cancelled_by=task.assigned_to or "system",
                reason=reason,
            )
        except Exception as e:
            logger.warning(f"Failed to publish task_cancelled event: {e}")

    return db_task_to_dict(task)


@app.delete("/api/v1/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Delete a task"""
    repo = TaskRepository(db)
    success = repo.delete_task(task_id, tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")


@app.post("/api/v1/tasks/{task_id}/evidence", response_model=Evidence, status_code=201)
async def add_evidence(
    task_id: str,
    evidence_type: str = Query(..., description="Type: photo, note, voice, measurement"),
    content: str = Query(..., description="URL or text content"),
    lat: float | None = None,
    lon: float | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Add evidence to a task"""
    repo = TaskRepository(db)

    # Check if task exists
    task = repo.get_task_by_id(task_id, tenant_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Create and save evidence
    from .models import TaskEvidence
    db_evidence = TaskEvidence(
        evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        type=evidence_type,
        content=content,
        captured_at=datetime.now(timezone.utc),
        location={"lat": lat, "lon": lon} if lat and lon else None,
    )

    saved_evidence = repo.add_evidence(db_evidence)

    # Convert to Pydantic response model
    return Evidence(
        evidence_id=saved_evidence.evidence_id,
        task_id=saved_evidence.task_id,
        type=saved_evidence.type,
        content=saved_evidence.content,
        captured_at=saved_evidence.captured_at,
        location=saved_evidence.location,
    )


# ═══════════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════════════════
# NDVI Integration Endpoints - نقاط تكامل NDVI
# ═══════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/tasks/from-ndvi-alert", response_model=Task, status_code=201)
async def create_task_from_ndvi_alert(
    data: NdviAlertTaskRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
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
    logger.info(
        f"Creating task from NDVI alert: field={data.field_id}, "
        f"type={data.alert_type}, ndvi={data.ndvi_value:.3f}"
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
        now = datetime.now(timezone.utc)
        due_date_map = {
            TaskPriority.URGENT: timedelta(hours=4),  # 4 hours for urgent
            TaskPriority.HIGH: timedelta(hours=12),  # 12 hours for high
            TaskPriority.MEDIUM: timedelta(days=1),  # 1 day for medium
            TaskPriority.LOW: timedelta(days=2),  # 2 days for low
        }
        due_date = now + due_date_map.get(priority, timedelta(days=1))

        # Determine assignee
        assigned_to = data.assigned_to
        if data.auto_assign and not assigned_to:
            # Fetch field manager from field service
            safe_field_id = str(data.field_id).replace('\n', '').replace('\r', '')[:100]
            field_manager = await fetch_field_manager(data.field_id, tenant_id)
            if field_manager:
                assigned_to = field_manager
                logger.info("Auto-assigned NDVI task to field manager: %s", assigned_to)
            else:
                logger.warning(
                    "Could not fetch field manager for field %s, task will be created without assignment",
                    safe_field_id
                )

        # Build metadata
        metadata = {
            "source": "ndvi_alert",
            "alert_type": data.alert_type,
            "ndvi_value": data.ndvi_value,
            "previous_ndvi": data.previous_ndvi,
            **(data.alert_metadata or {}),
        }

        # Create task using repository
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        db_task = TaskModel(
            task_id=task_id,
            tenant_id=tenant_id,
            title=title,
            title_ar=title_ar,
            description=description,
            description_ar=description_ar,
            task_type=task_type.value if isinstance(task_type, TaskType) else task_type,
            priority=priority.value if isinstance(priority, TaskPriority) else priority,
            status="pending",
            field_id=data.field_id,
            zone_id=data.zone_id,
            assigned_to=assigned_to,
            created_by="system_ndvi",
            due_date=due_date,
            task_metadata=metadata,
        )

        repo = TaskRepository(db)
        created_task = repo.create_task(db_task)

        # Send notification if task is assigned
        if assigned_to:
            # Convert db task to pydantic for notification
            pydantic_task = Task(
                task_id=created_task.task_id,
                tenant_id=created_task.tenant_id,
                title=created_task.title,
                title_ar=created_task.title_ar,
                task_type=TaskType(created_task.task_type),
                priority=TaskPriority(created_task.priority),
                status=TaskStatus(created_task.status),
                field_id=created_task.field_id,
                assigned_to=created_task.assigned_to,
                created_by=created_task.created_by,
                due_date=created_task.due_date,
                created_at=created_task.created_at,
                updated_at=created_task.updated_at,
            )
            await send_task_notification(
                tenant_id=tenant_id,
                task=pydantic_task,
                notification_type="ndvi_alert_task",
            )

        logger.info(
            f"Task created from NDVI alert: {task_id} "
            f"(priority={priority.value}, assigned_to={assigned_to})"
        )

        return db_task_to_dict(created_task)

    except Exception as e:
        logger.error(f"Error creating task from NDVI alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to create task from NDVI alert: {str(e)}"
        )


@app.get("/api/v1/tasks/suggest-for-field/{field_id}", response_model=dict)
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
    # Sanitize field_id for logging to prevent log injection
    safe_field_id = str(field_id).replace('\n', '').replace('\r', '')[:100]
    logger.info("Generating task suggestions for field: %s", safe_field_id)

    try:
        # Import NDVI client for field health analysis
        from .ndvi_client import (
            get_ndvi_client,
            get_task_suggestions_from_health,
        )

        # Get NDVI client and fetch field health data
        ndvi_client = get_ndvi_client()
        health_data = await ndvi_client.get_field_health(field_id)

        logger.info(
            "Field %s health: score=%s, status=%s",
            safe_field_id, health_data.health_score, health_data.health_status.value
        )

        # Generate task suggestions based on actual field health data
        raw_suggestions = get_task_suggestions_from_health(health_data)

        # Convert to TaskSuggestion objects
        suggestions = []
        for raw in raw_suggestions:
            # Map task type string to TaskType enum
            task_type_map = {
                "scouting": TaskType.SCOUTING,
                "irrigation": TaskType.IRRIGATION,
                "sampling": TaskType.SAMPLING,
                "spraying": TaskType.SPRAYING,
                "fertilization": TaskType.FERTILIZATION,
                "harvest": TaskType.HARVEST,
                "other": TaskType.OTHER,
            }
            task_type = task_type_map.get(raw.get("task_type", "other"), TaskType.OTHER)

            # Map priority string to TaskPriority enum
            priority_map = {
                "urgent": TaskPriority.URGENT,
                "high": TaskPriority.HIGH,
                "medium": TaskPriority.MEDIUM,
                "low": TaskPriority.LOW,
            }
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
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "health_summary": {
                "score": health_data.health_score,
                "status": health_data.health_status.value,
                "needs_attention": health_data.needs_attention,
                "vegetation_coverage": health_data.vegetation_coverage,
            },
        }

    except Exception as e:
        logger.error("Error generating task suggestions", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to generate task suggestions"
        )


@app.get("/api/v1/fields/{field_id}/health", response_model=dict)
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
    logger.info(f"Fetching health data for field: {field_id}")

    try:
        from .ndvi_client import get_ndvi_client

        ndvi_client = get_ndvi_client()
        health_data = await ndvi_client.get_field_health(field_id)

        return {
            "field_id": field_id,
            "tenant_id": tenant_id,
            "health": health_data.to_dict(),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching field health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch field health: {str(e)}")


@app.post("/api/v1/tasks/auto-create", response_model=dict, status_code=201)
async def auto_create_tasks(
    data: TaskAutoCreateRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
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
    logger.info(f"Auto-creating {len(data.suggestions)} tasks for field {data.field_id}")

    created_tasks = []
    failed_tasks = []
    now = datetime.now(timezone.utc)

    try:
        # Determine assignee
        assigned_to = data.assigned_to
        if data.auto_assign and not assigned_to:
            # Fetch field manager from field service
            safe_field_id = str(data.field_id).replace('\n', '').replace('\r', '')[:100]
            field_manager = await fetch_field_manager(data.field_id, tenant_id)
            if field_manager:
                assigned_to = field_manager
                logger.info("Auto-assigned batch tasks to field manager: %s", assigned_to)
            else:
                logger.warning(
                    "Could not fetch field manager for field %s, tasks will be created without assignment",
                    safe_field_id
                )

        # Create repository instance
        repo = TaskRepository(db)

        # Create tasks from suggestions
        for idx, suggestion in enumerate(data.suggestions):
            try:
                # Calculate due date
                due_date = now + timedelta(days=suggestion.suggested_due_days)

                # Create task using repository
                task_id = f"task_{uuid.uuid4().hex[:12]}"
                db_task = TaskModel(
                    task_id=task_id,
                    tenant_id=tenant_id,
                    title=suggestion.title,
                    title_ar=suggestion.title_ar,
                    description=suggestion.description,
                    description_ar=suggestion.description_ar,
                    task_type=suggestion.task_type.value if isinstance(suggestion.task_type, TaskType) else suggestion.task_type,
                    priority=suggestion.priority.value if isinstance(suggestion.priority, TaskPriority) else suggestion.priority,
                    status="pending",
                    field_id=data.field_id,
                    assigned_to=assigned_to,
                    created_by="system_auto",
                    due_date=due_date,
                    task_metadata={
                        "source": "auto_create",
                        "confidence": suggestion.confidence,
                        "reason": suggestion.reason,
                        "reason_ar": suggestion.reason_ar,
                        **(suggestion.metadata or {}),
                    },
                )

                created_task = repo.create_task(db_task)
                created_tasks.append(db_task_to_dict(created_task))

                logger.info(
                    f"Auto-created task {idx + 1}/{len(data.suggestions)}: "
                    f"{task_id} ({suggestion.task_type.value})"
                )

            except Exception as task_error:
                logger.error(f"Failed to create task from suggestion {idx}: {task_error}")
                failed_tasks.append(
                    {
                        "index": idx,
                        "suggestion": suggestion.title,
                        "error": str(task_error),
                    }
                )

        # Send batch notification if tasks were created
        if created_tasks and assigned_to:
            try:
                # Send a summary notification
                summary_task = Task(
                    task_id="batch_summary",
                    tenant_id=tenant_id,
                    title=f"{len(created_tasks)} New Tasks Created",
                    title_ar=f"تم إنشاء {len(created_tasks)} مهمة جديدة",
                    description=f"Field {data.field_id} has {len(created_tasks)} new recommended tasks",
                    description_ar=f"الحقل {data.field_id} لديه {len(created_tasks)} مهمة موصى بها جديدة",
                    task_type=TaskType.OTHER,
                    priority=TaskPriority.MEDIUM,
                    status=TaskStatus.PENDING,
                    field_id=data.field_id,
                    assigned_to=assigned_to,
                    created_by="system_auto",
                    created_at=now,
                    updated_at=now,
                )

                await send_task_notification(
                    tenant_id=tenant_id,
                    task=summary_task,
                    notification_type="tasks_batch_created",
                )
            except Exception as notif_error:
                logger.warning(f"Failed to send batch notification: {notif_error}")

        logger.info(
            f"Auto-create completed: {len(created_tasks)} created, {len(failed_tasks)} failed"
        )

        return {
            "field_id": data.field_id,
            "created": created_tasks,  # Already dicts from db_task_to_dict()
            "failed": failed_tasks,
            "summary": {
                "total_requested": len(data.suggestions),
                "created_count": len(created_tasks),
                "failed_count": len(failed_tasks),
                "assigned_to": assigned_to,
            },
        }

    except Exception as e:
        logger.error(f"Error in auto-create tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to auto-create tasks: {str(e)}")


# Astronomical-Based Task Endpoints - نقاط نهاية المهام الفلكية
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/tasks/best-days/{activity}", tags=["Astronomical Tasks"])
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
        f"Fetching best days for activity: {activity}, days: {days}, min_score: {min_score}"
    )

    # Fetch from astronomical calendar service
    astro_data = await fetch_astronomical_best_days(activity, days)

    # Get activity translations
    activity_en, activity_ar = get_activity_translation(activity)

    # Transform the response to match our model
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
                best_time=None,  # Can be added if available from service
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


@app.post(
    "/api/v1/tasks/create-with-astronomical",
    response_model=Task,
    status_code=201,
    tags=["Astronomical Tasks"],
)
async def create_task_with_astronomical_recommendation(
    data: AstronomicalTaskCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Create task with astronomical recommendation
    إنشاء مهمة مع توصية فلكية

    If use_best_date is True, the task will be scheduled on the best astronomical date.
    إذا كان use_best_date صحيحاً، سيتم جدولة المهمة في أفضل تاريخ فلكي.
    """
    logger.info(f"Creating astronomical task for activity: {data.activity}, field: {data.field_id}")

    now = datetime.now(timezone.utc)
    task_id = f"task_{uuid.uuid4().hex[:12]}"

    # Get activity translations
    activity_en, activity_ar = get_activity_translation(data.activity)

    # Determine due date
    due_date = None
    astronomical_metadata = {}

    if data.use_best_date:
        # Fetch best days from astronomical calendar
        astro_data = await fetch_astronomical_best_days(data.activity, data.search_days)

        best_days = astro_data.get("best_days", [])
        if best_days:
            # Use the first (best) day
            best_day = best_days[0]
            due_date_str = best_day["date"]
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")

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
                f"Selected astronomical date: {due_date_str} with score {best_day.get('score')}"
            )
        else:
            logger.warning(
                f"No suitable astronomical days found for {data.activity}, using default scheduling"
            )
            # Default to 7 days from now if no good days found
            due_date = now + timedelta(days=7)
            astronomical_metadata = {
                "astronomical_recommendation": False,
                "reason": "No suitable astronomical days found in search period",
                "reason_ar": "لم يتم العثور على أيام فلكية مناسبة في فترة البحث",
            }

    # Merge metadata
    metadata = {**(data.metadata if hasattr(data, "metadata") else {}), **astronomical_metadata}

    # Create the task using repository
    db_task = TaskModel(
        task_id=task_id,
        tenant_id=tenant_id,
        title=data.title,
        title_ar=data.title_ar or f"{activity_ar} - {data.field_id}",
        description=data.description,
        description_ar=data.description_ar,
        task_type=data.task_type.value if isinstance(data.task_type, TaskType) else data.task_type,
        priority=data.priority.value if isinstance(data.priority, TaskPriority) else data.priority,
        status="pending",
        field_id=data.field_id,
        zone_id=data.zone_id,
        assigned_to=data.assigned_to,
        created_by="user_system",  # Would come from auth in production
        due_date=due_date,
        scheduled_time=astronomical_metadata.get("best_time"),
        estimated_duration_minutes=data.estimated_duration_minutes,
        task_metadata=metadata,
        # Astronomical fields
        astronomical_score=astronomical_metadata.get("suitability_score"),
        moon_phase_at_due_date=astronomical_metadata.get("moon_phase"),
        lunar_mansion_at_due_date=astronomical_metadata.get("lunar_mansion"),
        suggested_by_calendar=astronomical_metadata.get("astronomical_recommendation", False),
        astronomical_recommendation=astronomical_metadata,
    )

    repo = TaskRepository(db)
    created_task = repo.create_task(db_task)

    logger.info(
        f"Created astronomical task {task_id} with due date {due_date.isoformat() if due_date else 'None'}"
    )

    return db_task_to_dict(created_task)


@app.post(
    "/api/v1/tasks/validate-date",
    response_model=DateValidationResponse,
    tags=["Astronomical Tasks"],
)
async def validate_date_for_activity(
    data: DateValidationRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Validate date suitability for agricultural activity
    التحقق من ملاءمة التاريخ للنشاط الزراعي

    Returns suitability score and recommendations based on astronomical calendar.
    يُرجع درجة الملاءمة والتوصيات بناءً على التقويم الفلكي.
    """
    logger.info(f"Validating date {data.date} for activity {data.activity}")

    # Validate date format
    try:
        datetime.strptime(data.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="تنسيق تاريخ غير صحيح. استخدم YYYY-MM-DD - Invalid date format. Use YYYY-MM-DD",
        )

    # Get activity translations
    activity_en, activity_ar = get_activity_translation(data.activity)

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
        # Fetch best days for the next 30 days
        astro_data = await fetch_astronomical_best_days(data.activity, 30)
        best_days = astro_data.get("best_days", [])[:3]  # Top 3 alternatives
        alternative_dates = [day["date"] for day in best_days]

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


# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
