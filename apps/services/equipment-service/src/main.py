"""
SAHOOL Equipment Service - خدمة إدارة المعدات والأصول
Port: 8101

Provides equipment/asset management:
- Equipment CRUD (tractors, pumps, drones, harvesters)
- Maintenance tracking and alerts
- Real-time status (fuel, hours, location)
- QR code registration
"""

import json
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum, StrEnum

import structlog
from fastapi import Body, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

logger = structlog.get_logger()

from . import repository
from .api_models import (
    STATUS_IN_MAP,
    STATUS_OUT_MAP,
    map_status_in,
    map_status_out,
    serialize_equipment,
)
from .database import check_db_connection, get_db, init_db
from .db_models import (
    Equipment as DBEquipment,
)
from .db_models import (
    MaintenanceAlert as DBMaintenanceAlert,
)
from .db_models import (
    MaintenanceRecord as DBMaintenanceRecord,
)

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
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    AUTH_AVAILABLE = True
except ImportError:
    # Fallback if auth module not available
    AUTH_AVAILABLE = False
    setup_exception_handlers = None
    add_request_id_middleware = None

    class User:  # type: ignore[no-redef]
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise HTTPException(status_code=503, detail="Authentication backend unavailable")

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "sahool-equipment-service"
SERVICE_PORT = int(os.getenv("PORT", "8101"))

app = FastAPI(
    title="SAHOOL Equipment Service",
    description="Agricultural equipment and asset management API",
    version="16.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
if setup_exception_handlers:
    setup_exception_handlers(app)
if add_request_id_middleware:
    add_request_id_middleware(app)

# CORS - Secure configuration
try:
    from shared.cors_config import CORS_SETTINGS

    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
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

# Tenant context middleware - عزل المستأجرين
if TenantContextMiddleware:
    app.add_middleware(TenantContextMiddleware)

# ═══════════════════════════════════════════════════════════════════════════
# Enums & Models
# ═══════════════════════════════════════════════════════════════════════════


class EquipmentType(StrEnum):
    TRACTOR = "tractor"
    PUMP = "pump"
    DRONE = "drone"
    HARVESTER = "harvester"
    SPRAYER = "sprayer"
    PIVOT = "pivot"
    SENSOR = "sensor"
    VEHICLE = "vehicle"
    OTHER = "other"


class EquipmentStatus(StrEnum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    REPAIR = "repair"


class MaintenancePriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaintenanceType(StrEnum):
    OIL_CHANGE = "oil_change"
    FILTER_CHANGE = "filter_change"
    TIRE_CHECK = "tire_check"
    BATTERY_CHECK = "battery_check"
    CALIBRATION = "calibration"
    GENERAL_SERVICE = "general_service"
    REPAIR = "repair"
    OTHER = "other"


class EquipmentCreate(BaseModel):
    """Create a new equipment"""

    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str | None = None
    equipment_type: EquipmentType
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    year: int | None = None
    purchase_date: datetime | None = None
    purchase_price: float | None = None
    field_id: str | None = None
    location_name: str | None = None
    horsepower: int | None = None
    fuel_capacity_liters: float | None = None
    metadata: dict | None = None


class EquipmentUpdate(BaseModel):
    """Update equipment properties.

    Accepts both backend-canonical status values (``operational``, ``inactive``)
    and frontend-canonical aliases (``active``, ``idle``, ``retired``). Incoming
    aliases are normalized to the backend canonical form before persistence.
    """

    name: str | None = None
    name_ar: str | None = None
    equipment_type: EquipmentType | None = None
    status: str | None = None
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    year: int | None = None
    field_id: str | None = None
    location_name: str | None = None
    current_fuel_percent: float | None = None
    current_hours: float | None = None
    current_lat: float | None = None
    current_lon: float | None = None
    metadata: dict | None = None

    @field_validator("status")
    @classmethod
    def _normalize_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = map_status_in(value)
        # After normalization, ensure it is a recognised backend value.
        valid_backend = {s.value for s in EquipmentStatus}
        if normalized not in valid_backend:
            raise ValueError(
                f"Invalid status '{value}'. Allowed: "
                f"{sorted(valid_backend | set(STATUS_IN_MAP.keys()))}"
            )
        return normalized


class MaintenanceRecord(BaseModel):
    """Maintenance record"""

    record_id: str
    equipment_id: str
    maintenance_type: MaintenanceType
    description: str
    description_ar: str | None = None
    performed_at: datetime
    performed_by: str | None = None
    cost: float | None = None
    notes: str | None = None
    parts_replaced: list[str] | None = None


class MaintenanceAlert(BaseModel):
    """Maintenance alert"""

    alert_id: str
    equipment_id: str
    equipment_name: str
    maintenance_type: MaintenanceType
    description: str
    description_ar: str | None = None
    priority: MaintenancePriority
    due_at: datetime | None = None
    due_hours: float | None = None
    is_overdue: bool = False
    created_at: datetime


class IssueSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class EquipmentIssueCreate(BaseModel):
    """Schema for reporting an incident/issue against a piece of equipment.

    This is intentionally minimal: the service does not yet own a dedicated
    ``equipment_issues`` table, so we persist via the NATS event bus instead
    (subject ``sahool.tenant.{tid}.equipment.issue_reported``) and return a
    synthetic ``issue_id`` so the client can correlate.
    """

    title: str = Field(..., min_length=1, max_length=200)
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    severity: IssueSeverity = IssueSeverity.MEDIUM
    reported_by: str | None = None
    metadata: dict | None = None


class EquipmentIssueResponse(BaseModel):
    """Response payload for a reported issue."""

    id: str
    issue_id: str
    equipment_id: str
    tenant_id: str
    title: str
    title_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    severity: IssueSeverity
    status: IssueStatus = IssueStatus.OPEN
    reported_at: datetime
    reported_by: str | None = None
    metadata: dict | None = None


class Equipment(BaseModel):
    """Full equipment model"""

    equipment_id: str
    tenant_id: str
    name: str
    name_ar: str | None = None
    equipment_type: EquipmentType
    status: EquipmentStatus
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    year: int | None = None
    purchase_date: datetime | None = None
    purchase_price: float | None = None
    field_id: str | None = None
    location_name: str | None = None
    horsepower: int | None = None
    fuel_capacity_liters: float | None = None
    current_fuel_percent: float | None = None
    current_hours: float | None = None
    current_lat: float | None = None
    current_lon: float | None = None
    last_maintenance_at: datetime | None = None
    next_maintenance_at: datetime | None = None
    next_maintenance_hours: float | None = None
    created_at: datetime
    updated_at: datetime
    metadata: dict | None = None
    qr_code: str | None = None


# ═══════════════════════════════════════════════════════════════════════════
# Database Initialization
# ═══════════════════════════════════════════════════════════════════════════

# Initialize database tables on startup
# In production, use Alembic migrations instead
try:
    init_db()
except Exception as e:
    logger.warning("database_init_failed", error=str(e))


def seed_demo_data(db: Session):
    """Seed demo equipment for testing"""
    # Check if data already exists
    existing_count = db.query(DBEquipment).count()
    if existing_count > 0:
        return  # Data already seeded

    now = datetime.now(UTC)

    demo_equipment = [
        DBEquipment(
            equipment_id="eq_001",
            tenant_id="tenant_demo",
            name="John Deere 8R 410",
            name_ar="جون ديري 8R 410",
            equipment_type=EquipmentType.TRACTOR.value,
            status=EquipmentStatus.OPERATIONAL.value,
            brand="John Deere",
            model="8R 410",
            serial_number="JD8R410-2023-001",
            year=2023,
            purchase_date=datetime(2023, 3, 15),
            horsepower=410,
            fuel_capacity_liters=800,
            current_fuel_percent=75,
            current_hours=1250,
            field_id="field_north",
            location_name="الحقل الشمالي - القطاع C",
            current_lat=15.3694,
            current_lon=44.1910,
            last_maintenance_at=now - timedelta(days=30),
            next_maintenance_at=now + timedelta(days=60),
            next_maintenance_hours=1500,
            created_at=now - timedelta(days=365),
            updated_at=now - timedelta(hours=2),
            qr_code="QR_EQ001_JD8R410",
        ),
        DBEquipment(
            equipment_id="eq_002",
            tenant_id="tenant_demo",
            name="DJI Agras T40",
            name_ar="درون دي جي آي أجراس T40",
            equipment_type=EquipmentType.DRONE.value,
            status=EquipmentStatus.MAINTENANCE.value,
            brand="DJI",
            model="Agras T40",
            serial_number="DJI-T40-2024-012",
            year=2024,
            purchase_date=datetime(2024, 1, 10),
            current_fuel_percent=100,  # Battery
            current_hours=320,
            location_name="الورشة",
            last_maintenance_at=now - timedelta(days=5),
            created_at=now - timedelta(days=180),
            updated_at=now - timedelta(days=2),
            qr_code="QR_EQ002_DJIT40",
            metadata={"battery_cycles": 120, "max_payload_kg": 40},
        ),
        DBEquipment(
            equipment_id="eq_003",
            tenant_id="tenant_demo",
            name="Grundfos Submersible Pump",
            name_ar="مضخة غاطسة جروندفوس",
            equipment_type=EquipmentType.PUMP.value,
            status=EquipmentStatus.OPERATIONAL.value,
            brand="Grundfos",
            model="SP 46-7",
            serial_number="GF-SP467-2022-045",
            year=2022,
            horsepower=15,
            field_id="field_north",
            location_name="البئر رقم 1",
            current_hours=8500,
            last_maintenance_at=now - timedelta(days=90),
            next_maintenance_at=now + timedelta(days=30),
            created_at=now - timedelta(days=500),
            updated_at=now - timedelta(days=1),
            qr_code="QR_EQ003_GFPUMP",
            metadata={"flow_rate_m3h": 46, "head_m": 150},
        ),
        DBEquipment(
            equipment_id="eq_004",
            tenant_id="tenant_demo",
            name="New Holland CR9.90",
            name_ar="حاصدة نيو هولاند",
            equipment_type=EquipmentType.HARVESTER.value,
            status=EquipmentStatus.INACTIVE.value,
            brand="New Holland",
            model="CR9.90",
            serial_number="NH-CR990-2021-008",
            year=2021,
            horsepower=653,
            fuel_capacity_liters=1100,
            current_fuel_percent=40,
            current_hours=890,
            location_name="المخزن",
            last_maintenance_at=now - timedelta(days=120),
            created_at=now - timedelta(days=800),
            updated_at=now - timedelta(days=30),
            qr_code="QR_EQ004_NHCR9",
        ),
        DBEquipment(
            equipment_id="eq_005",
            tenant_id="tenant_demo",
            name="Valley Center Pivot",
            name_ar="رشاش محوري فالي",
            equipment_type=EquipmentType.PIVOT.value,
            status=EquipmentStatus.OPERATIONAL.value,
            brand="Valley",
            model="8000 Series",
            serial_number="VL-8K-2020-023",
            year=2020,
            field_id="field_south",
            location_name="الحقل الجنوبي",
            current_hours=15000,
            last_maintenance_at=now - timedelta(days=45),
            next_maintenance_at=now + timedelta(days=45),
            created_at=now - timedelta(days=1200),
            updated_at=now - timedelta(hours=12),
            qr_code="QR_EQ005_VPIVOT",
            metadata={"coverage_ha": 50, "spans": 7},
        ),
    ]

    for eq in demo_equipment:
        db.add(eq)

    # Demo maintenance alerts
    demo_alerts = [
        DBMaintenanceAlert(
            alert_id="alert_001",
            equipment_id="eq_001",
            equipment_name="John Deere 8R",
            maintenance_type=MaintenanceType.OIL_CHANGE.value,
            description="Engine oil change required",
            description_ar="تغيير زيت المحرك مطلوب",
            priority=MaintenancePriority.MEDIUM.value,
            due_hours=1300,
            is_overdue=False,
            created_at=now - timedelta(days=5),
        ),
        DBMaintenanceAlert(
            alert_id="alert_002",
            equipment_id="eq_002",
            equipment_name="DJI Agras T40",
            maintenance_type=MaintenanceType.BATTERY_CHECK.value,
            description="Battery inspection overdue",
            description_ar="فحص البطارية متأخر",
            priority=MaintenancePriority.HIGH.value,
            due_at=now - timedelta(days=2),
            is_overdue=True,
            created_at=now - timedelta(days=10),
        ),
    ]

    for alert in demo_alerts:
        db.add(alert)

    db.commit()


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


def get_tenant_id(user: User | None = Depends(get_current_user)) -> str:
    """Extract tenant ID from authenticated user.
    SECURITY: Never fall back to a shared tenant - this would bypass tenant isolation."""
    if AUTH_AVAILABLE and user:
        return user.tenant_id
    # SECURITY FIX: Reject requests without valid tenant context instead of falling back
    # to a shared "tenant_demo" namespace which bypasses tenant isolation.
    raise HTTPException(
        status_code=401,
        detail="Authentication required - cannot determine tenant context",
    )


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/healthz")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint (liveness probe)"""
    # Seed demo data if needed
    try:
        seed_demo_data(db)
    except Exception as exc:
        logger.debug("Demo data seeding skipped during health check: %s", exc)

    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": "16.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint alias for compatibility"""
    return {"status": "healthy", "service": SERVICE_NAME, "version": "16.0.0"}


@app.get("/readyz")
async def readiness_check():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    db_healthy = check_db_connection()

    return {
        "status": "ready" if db_healthy else "not_ready",
        "service": SERVICE_NAME,
        "version": "16.0.0",
        "checks": {
            "database": "connected" if db_healthy else "disconnected",
        },
    }


@app.get("/api/v1/equipment", response_model=dict)
async def list_equipment(
    equipment_type: str | None = Query(
        None,
        description="Filter by equipment type (preferred)",
    ),
    type: str | None = Query(
        None,
        alias="type",
        description="Alias for equipment_type (frontend compatibility)",
    ),
    status: str | None = Query(
        None,
        description="Filter by status. Accepts both backend (operational) and "
        "frontend (active) canonical values.",
    ),
    field_id: str | None = Query(None, description="Filter by field"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User | None = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """List all equipment with optional filters.

    Accepts both ``equipment_type`` and ``type`` query parameters for
    frontend compatibility. ``equipment_type`` takes precedence if both are
    supplied. ``status`` accepts both the backend canonical dialect
    (``operational``, ``inactive``) and the frontend canonical dialect
    (``active``, ``idle``, ``retired``).

    The response envelope is::

        {
            "data": [...],           # new, preferred
            "pagination": {...},     # new, preferred
            "equipment": [...],      # legacy alias (will be removed in v17)
            "total": N,              # legacy alias
            "limit": X,              # legacy alias
            "offset": Y,             # legacy alias
        }
    """
    # Prefer the explicit ``equipment_type`` param; fall back to ``type``.
    effective_type = equipment_type or type
    if effective_type is not None:
        valid_types = {t.value for t in EquipmentType}
        if effective_type not in valid_types:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid equipment_type '{effective_type}'. Allowed: {sorted(valid_types)}",
            )

    # Normalize status to the backend canonical dialect before querying.
    backend_status: str | None = None
    if status is not None:
        backend_status = map_status_in(status)
        valid_statuses = {s.value for s in EquipmentStatus}
        if backend_status not in valid_statuses:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Invalid status '{status}'. Allowed: "
                    f"{sorted(valid_statuses | set(STATUS_IN_MAP.keys()))}"
                ),
            )

    equipment_list, total = repository.list_equipment(
        db,
        tenant_id=tenant_id,
        equipment_type=effective_type,
        status=backend_status,
        field_id=field_id,
        skip=offset,
        limit=limit,
    )

    equipment_dicts = [serialize_equipment(eq) for eq in equipment_list]

    return {
        # New unified envelope
        "data": equipment_dicts,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
        },
        # Legacy envelope (deprecated, kept for 1 minor version)
        "equipment": equipment_dicts,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/equipment/stats", response_model=dict)
async def get_equipment_stats(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get equipment statistics"""
    return repository.get_equipment_stats(db, tenant_id=tenant_id)


@app.get("/api/v1/equipment/alerts", response_model=dict)
async def get_maintenance_alerts(
    priority: MaintenancePriority | None = Query(None),
    overdue_only: bool = Query(False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get maintenance alerts"""
    alerts = repository.get_maintenance_alerts(
        db,
        tenant_id=tenant_id,
        priority=priority.value if priority else None,
        overdue_only=overdue_only,
    )

    # Convert to dictionaries
    alert_dicts = []
    for alert in alerts:
        alert_dicts.append(
            {
                "alert_id": alert.alert_id,
                "equipment_id": alert.equipment_id,
                "equipment_name": alert.equipment_name,
                "maintenance_type": alert.maintenance_type,
                "description": alert.description,
                "description_ar": alert.description_ar,
                "priority": alert.priority,
                "due_at": alert.due_at,
                "due_hours": float(alert.due_hours) if alert.due_hours else None,
                "is_overdue": alert.is_overdue,
                "created_at": alert.created_at,
            }
        )

    return {
        "alerts": alert_dicts,
        "count": len(alerts),
        "overdue_count": len([a for a in alerts if a.is_overdue]),
    }


@app.get("/api/v1/equipment/maintenance-schedule", response_model=dict)
async def get_maintenance_schedule(
    days_ahead: int = Query(
        90,
        ge=1,
        le=365,
        description="Look-ahead window in days for upcoming maintenance",
    ),
    priority: MaintenancePriority | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Return the upcoming maintenance schedule.

    Combines two sources:

    1. ``MaintenanceAlert`` rows scoped to the tenant (via the equipment join),
       which represent service tickets the system has already raised.
    2. Equipment whose ``next_maintenance_at`` falls inside the look-ahead
       window -- these are upcoming scheduled services that may not yet have
       an explicit alert row.

    The endpoint is the authoritative source for the frontend
    ``/api/v1/equipment/maintenance-schedule`` call, which used to 404.
    """
    now = datetime.now(UTC)
    cutoff = now + timedelta(days=days_ahead)

    # --- 1) Pull alerts (tenant-isolated via JOIN in the repository) ------
    alerts = repository.get_maintenance_alerts(
        db,
        tenant_id=tenant_id,
        priority=priority.value if priority else None,
        overdue_only=False,
    )

    schedule_items: list[dict] = []
    for alert in alerts:
        schedule_items.append(
            {
                "source": "alert",
                "alert_id": alert.alert_id,
                "equipment_id": alert.equipment_id,
                "equipment_name": alert.equipment_name,
                "maintenance_type": alert.maintenance_type,
                "description": alert.description,
                "description_ar": alert.description_ar,
                "priority": alert.priority,
                "scheduled_date": alert.due_at,
                "scheduledDate": alert.due_at,
                "due_hours": float(alert.due_hours) if alert.due_hours else None,
                "is_overdue": alert.is_overdue,
                "created_at": alert.created_at,
            }
        )

    # --- 2) Pull equipment with an upcoming next_maintenance_at ----------
    try:
        upcoming_query = (
            db.query(DBEquipment)
            .filter(DBEquipment.tenant_id == tenant_id)
            .filter(DBEquipment.next_maintenance_at.is_not(None))
            .filter(DBEquipment.next_maintenance_at <= cutoff)
            .order_by(DBEquipment.next_maintenance_at.asc())
        )
        upcoming = list(upcoming_query)
    except Exception as exc:  # pragma: no cover - defensive, fall back to alerts
        logger.warning("maintenance_schedule_upcoming_query_failed", error=str(exc))
        upcoming = []

    for eq in upcoming:
        schedule_items.append(
            {
                "source": "equipment",
                "equipment_id": eq.equipment_id,
                "equipment_name": eq.name,
                "maintenance_type": "scheduled_service",
                "description": "Scheduled maintenance window",
                "description_ar": "موعد الصيانة المجدولة",
                "priority": MaintenancePriority.MEDIUM.value,
                "scheduled_date": eq.next_maintenance_at,
                "scheduledDate": eq.next_maintenance_at,
                "due_hours": float(eq.next_maintenance_hours) if eq.next_maintenance_hours else None,
                "is_overdue": bool(eq.next_maintenance_at and eq.next_maintenance_at < now),
                "created_at": eq.updated_at,
            }
        )

    # Sort by scheduled_date ascending, overdue first
    schedule_items.sort(
        key=lambda item: (
            not item.get("is_overdue"),
            item.get("scheduled_date") or datetime.max.replace(tzinfo=UTC),
        )
    )

    return {
        "data": schedule_items,
        "schedule": schedule_items,  # legacy alias
        "count": len(schedule_items),
        "pagination": {
            "total": len(schedule_items),
            "limit": len(schedule_items),
            "offset": 0,
        },
        "window": {
            "from": now,
            "to": cutoff,
            "days_ahead": days_ahead,
        },
    }


@app.get("/api/v1/equipment/{equipment_id}", response_model=dict)
async def get_equipment(
    equipment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get equipment by ID.

    Returns the unified response shape emitted by :func:`serialize_equipment`
    (legacy snake_case fields + new camelCase frontend aliases).
    """
    eq = repository.get_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return serialize_equipment(eq)


@app.get("/api/v1/equipment/qr/{qr_code}", response_model=dict)
async def get_equipment_by_qr(
    qr_code: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get equipment by QR code."""
    eq = repository.get_equipment_by_qr(db, qr_code=qr_code, tenant_id=tenant_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return serialize_equipment(eq)


@app.post("/api/v1/equipment", response_model=dict, status_code=201)
async def create_equipment(
    data: EquipmentCreate,
    user: User | None = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create new equipment"""
    now = datetime.now(UTC)
    equipment_id = f"eq_{uuid.uuid4().hex[:8]}"
    qr_code = f"QR_{equipment_id.upper()}_{data.name[:10].replace(' ', '')}"

    db_eq = DBEquipment(
        equipment_id=equipment_id,
        tenant_id=tenant_id,
        name=data.name,
        name_ar=data.name_ar,
        equipment_type=data.equipment_type.value,
        status=EquipmentStatus.OPERATIONAL.value,
        brand=data.brand,
        model=data.model,
        serial_number=data.serial_number,
        year=data.year,
        purchase_date=data.purchase_date,
        purchase_price=data.purchase_price,
        field_id=data.field_id,
        location_name=data.location_name,
        horsepower=data.horsepower,
        fuel_capacity_liters=data.fuel_capacity_liters,
        created_at=now,
        updated_at=now,
        extra_metadata=data.metadata,
        qr_code=qr_code,
    )

    repository.create_equipment(db, db_eq)

    return serialize_equipment(db_eq)


@app.put("/api/v1/equipment/{equipment_id}", response_model=dict)
async def update_equipment(
    equipment_id: str,
    data: EquipmentUpdate,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update equipment"""
    update_data = data.model_dump(exclude_unset=True)

    # Convert enum values to strings. Status is already normalized to a
    # plain backend-canonical string by ``EquipmentUpdate._normalize_status``.
    if "equipment_type" in update_data and update_data["equipment_type"]:
        eq_type = update_data["equipment_type"]
        update_data["equipment_type"] = eq_type.value if hasattr(eq_type, "value") else eq_type

    eq = repository.update_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id, **update_data)

    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return serialize_equipment(eq)


@app.post("/api/v1/equipment/{equipment_id}/status", response_model=dict)
async def update_equipment_status(
    equipment_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update equipment status.

    Accepts both backend canonical (``operational``, ``inactive``) and
    frontend canonical (``active``, ``idle``, ``retired``) values.
    """
    normalized = map_status_in(status)
    valid_backend = {s.value for s in EquipmentStatus}
    if normalized not in valid_backend:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid status '{status}'. Allowed: "
                f"{sorted(valid_backend | set(STATUS_IN_MAP.keys()))}"
            ),
        )

    eq = repository.update_equipment(
        db, equipment_id=equipment_id, tenant_id=tenant_id, status=normalized
    )

    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return serialize_equipment(eq)


@app.post("/api/v1/equipment/{equipment_id}/location", response_model=dict)
async def update_equipment_location(
    equipment_id: str,
    lat: float = Query(...),
    lon: float = Query(...),
    location_name: str | None = None,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update equipment GPS location"""
    update_data: dict = {"current_lat": lat, "current_lon": lon}
    if location_name:
        update_data["location_name"] = location_name

    eq = repository.update_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id, **update_data)

    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return serialize_equipment(eq)


@app.post("/api/v1/equipment/{equipment_id}/telemetry", response_model=dict)
async def update_equipment_telemetry(
    equipment_id: str,
    fuel_percent: float | None = None,
    hours: float | None = None,
    lat: float | None = None,
    lon: float | None = None,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Update equipment telemetry data (fuel, hours, location)"""
    update_data: dict = {}
    if fuel_percent is not None:
        update_data["current_fuel_percent"] = fuel_percent
    if hours is not None:
        update_data["current_hours"] = hours
    if lat is not None:
        update_data["current_lat"] = lat
    if lon is not None:
        update_data["current_lon"] = lon

    eq = repository.update_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id, **update_data)

    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    return serialize_equipment(eq)


@app.post(
    "/api/v1/equipment/{equipment_id}/issues",
    response_model=EquipmentIssueResponse,
    status_code=202,
)
async def report_equipment_issue(
    equipment_id: str,
    issue: EquipmentIssueCreate = Body(...),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Report an issue/incident against a piece of equipment.

    This endpoint is an **event-first** replacement for the missing DB-backed
    issues table. Behaviour:

    1. Verifies the equipment exists and belongs to the authenticated tenant.
    2. Builds an ``EquipmentIssueResponse`` payload with a synthetic issue_id.
    3. Best-effort publishes the payload to NATS on the subject
       ``sahool.tenant.{tenant_id}.equipment.issue_reported`` so downstream
       services (notification, audit, ticketing) can react. Publishing is
       best-effort: the HTTP call returns ``202 Accepted`` even if the NATS
       connection is unavailable (the payload is still logged for later
       reconciliation).

    Returns ``202 Accepted`` to signal the issue has been queued.
    """
    # Verify equipment exists and belongs to tenant
    eq = repository.get_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    now = datetime.now(UTC)
    issue_id = f"issue_{uuid.uuid4().hex[:12]}"

    reported_by = issue.reported_by
    if not reported_by and current_user is not None:
        reported_by = getattr(current_user, "id", None)

    response = EquipmentIssueResponse(
        id=issue_id,
        issue_id=issue_id,
        equipment_id=equipment_id,
        tenant_id=tenant_id,
        title=issue.title,
        title_ar=issue.title_ar,
        description=issue.description,
        description_ar=issue.description_ar,
        severity=issue.severity,
        status=IssueStatus.OPEN,
        reported_at=now,
        reported_by=reported_by,
        metadata=issue.metadata,
    )

    # Best-effort NATS publish. We deliberately swallow all errors here so a
    # NATS outage does not break the user-facing flow; the payload is logged.
    subject = f"sahool.tenant.{tenant_id}.equipment.issue_reported"
    try:
        nc = getattr(app.state, "nc", None)
        if nc is not None and hasattr(nc, "publish"):
            payload = response.model_dump(mode="json")
            payload_bytes = json.dumps(payload, default=str).encode("utf-8")
            maybe_coro = nc.publish(subject, payload_bytes)
            # nats-py publish is a coroutine; await if so
            if hasattr(maybe_coro, "__await__"):
                await maybe_coro
        logger.info(
            "equipment_issue_reported",
            issue_id=issue_id,
            equipment_id=equipment_id,
            tenant_id=tenant_id,
            severity=issue.severity.value,
            subject=subject,
        )
    except Exception as exc:  # pragma: no cover - best-effort publish
        logger.warning(
            "equipment_issue_nats_publish_failed",
            error=str(exc),
            issue_id=issue_id,
            subject=subject,
        )

    return response


@app.get("/api/v1/equipment/{equipment_id}/maintenance", response_model=dict)
async def get_maintenance_history(
    equipment_id: str,
    limit: int = Query(20, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Get maintenance history for equipment"""
    # Verify equipment exists and belongs to tenant
    eq = repository.get_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    records = repository.get_maintenance_history(db, equipment_id=equipment_id, limit=limit)

    # Convert to dictionaries
    record_dicts = []
    for record in records:
        record_dicts.append(
            {
                "record_id": record.record_id,
                "equipment_id": record.equipment_id,
                "maintenance_type": record.maintenance_type,
                "description": record.description,
                "description_ar": record.description_ar,
                "performed_at": record.performed_at,
                "performed_by": record.performed_by,
                "cost": float(record.cost) if record.cost else None,
                "notes": record.notes,
                "parts_replaced": record.parts_replaced,
            }
        )

    return {
        "equipment_id": equipment_id,
        "records": record_dicts,
        "count": len(records),
    }


@app.post(
    "/api/v1/equipment/{equipment_id}/maintenance",
    response_model=MaintenanceRecord,
    status_code=201,
)
async def add_maintenance_record(
    equipment_id: str,
    maintenance_type: MaintenanceType,
    description: str,
    description_ar: str | None = None,
    performed_by: str | None = None,
    cost: float | None = None,
    notes: str | None = None,
    parts_replaced: list[str] | None = None,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Add a maintenance record"""
    # Verify equipment exists and belongs to tenant
    eq = repository.get_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id)
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    now = datetime.now(UTC)
    db_record = DBMaintenanceRecord(
        record_id=f"maint_{uuid.uuid4().hex[:8]}",
        equipment_id=equipment_id,
        maintenance_type=maintenance_type.value,
        description=description,
        description_ar=description_ar,
        performed_at=now,
        performed_by=performed_by,
        cost=cost,
        notes=notes,
        parts_replaced=parts_replaced,
    )

    repository.create_maintenance_record(db, db_record)

    # Update equipment last maintenance time
    repository.update_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id, last_maintenance_at=now)

    # Convert to Pydantic model
    return MaintenanceRecord(
        record_id=db_record.record_id,
        equipment_id=db_record.equipment_id,
        maintenance_type=MaintenanceType(db_record.maintenance_type),
        description=db_record.description,
        description_ar=db_record.description_ar,
        performed_at=db_record.performed_at,
        performed_by=db_record.performed_by,
        cost=float(db_record.cost) if db_record.cost else None,
        notes=db_record.notes,
        parts_replaced=db_record.parts_replaced,
    )


@app.delete("/api/v1/equipment/{equipment_id}", status_code=204)
async def delete_equipment(
    equipment_id: str,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Delete equipment"""
    deleted = repository.delete_equipment(db, equipment_id=equipment_id, tenant_id=tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Equipment not found")


# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")  # nosec B104 - binding to all interfaces required for Docker
    uvicorn.run(app, host=host, port=SERVICE_PORT)
