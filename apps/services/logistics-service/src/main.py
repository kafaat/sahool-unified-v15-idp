"""
SAHOOL Logistics Service - خدمة اللوجستيات الزراعية
Port: 8167

Provides agricultural logistics management:
- Harvest collection scheduling and routing (جدولة جمع المحاصيل والتوجيه)
- Transportation tracking (تتبع النقل)
- Storage facility management (إدارة مرافق التخزين)
- Delivery optimization (تحسين التسليم)
- Fleet management (إدارة الأسطول)
"""

import json
import logging
import os
import re
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from starlette.middleware.base import BaseHTTPMiddleware

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Import authentication dependencies and error handling
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    setup_exception_handlers = None
    add_request_id_middleware = None

    class User:  # type: ignore[no-redef]
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise HTTPException(status_code=503, detail="Authentication backend unavailable")


# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

    def setup_security_headers(app):
        pass


from shared.middleware.tenant_context import TenantContextMiddleware

# NATS import
_nats_client = None
_nats_available = False
try:
    import nats

    _nats_available = True
except ImportError:
    pass


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("sahool-logistics")

# ==============================================================================
# Configuration
# ==============================================================================

SERVICE_NAME = "sahool-logistics-service"
SERVICE_VERSION = "16.0.0"
SERVICE_PORT = int(os.getenv("PORT", "8167"))
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
DATABASE_URL = os.getenv("DATABASE_URL", "")
# Enforce sslmode for non-development database connections
if DATABASE_URL and os.getenv("ENVIRONMENT", "development") != "development":
    if "sslmode" not in DATABASE_URL:
        # Use sslmode=disable for PgBouncer (port 6432) which does not support SSL
        ssl_mode = "disable" if ":6432" in DATABASE_URL else "require"
        DATABASE_URL += f"?sslmode={ssl_mode}" if "?" not in DATABASE_URL else f"&sslmode={ssl_mode}"


# ==============================================================================
# Enums
# ==============================================================================


class VehicleType(StrEnum):
    TRUCK = "truck"
    PICKUP = "pickup"
    VAN = "van"
    REFRIGERATED = "refrigerated"
    TANKER = "tanker"
    TRACTOR_TRAILER = "tractor_trailer"


class VehicleStatus(StrEnum):
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    LOADING = "loading"
    UNLOADING = "unloading"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class ShipmentStatus(StrEnum):
    """
    Canonical shipment status enum.

    Includes both backend-native values (scheduled, collecting, at_storage,
    delivering) and soft/UX values used by the frontend (pending, delayed).

    Soft states semantics:
      - `pending`: Maps internally to `scheduled` (not yet dispatched) - a "soft" state
        used by the frontend to represent shipments that have been created but have
        no vehicle assigned. Persisted canonically as `scheduled`.
      - `delayed`: Maps internally to `in_transit` with a `delayed=True` flag - a
        "soft" state representing a shipment in transit past its ETA. Persisted
        canonically as `in_transit` with metadata.delayed=True.
    """

    # Soft / UX-layer statuses (aligned with frontend)
    PENDING = "pending"
    DELAYED = "delayed"

    # Canonical backend statuses
    SCHEDULED = "scheduled"
    COLLECTING = "collecting"
    IN_TRANSIT = "in_transit"
    AT_STORAGE = "at_storage"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# Canonical unified status set (emitted on output)
CANONICAL_STATUSES = [
    "pending",
    "scheduled",
    "collecting",
    "in_transit",
    "at_storage",
    "delivering",
    "delivered",
    "delayed",
    "cancelled",
]

# Map of legacy / frontend-soft status values to canonical internal values
# for persistence. "pending" is persisted as "scheduled"; "delayed" stays as
# "in_transit" but is re-emitted as "delayed" when a delayed flag is present.
LEGACY_STATUS_MAP = {
    "in-transit": "in_transit",  # legacy dash form
    "pending": "scheduled",  # soft -> canonical persist
    # "delayed" is not mapped for persistence; handled separately via flag
}


def normalize_status(value: str | ShipmentStatus | None) -> str | None:
    """Normalize a status value, accepting both old and new values.

    Returns the canonical (persistable) status value.
    """
    if value is None:
        return None
    if isinstance(value, ShipmentStatus):
        value = value.value
    v = str(value).strip().lower()
    # apply legacy mapping
    v = LEGACY_STATUS_MAP.get(v, v)
    # validate against allowed set
    if v not in {
        "scheduled",
        "collecting",
        "in_transit",
        "at_storage",
        "delivering",
        "delivered",
        "cancelled",
        "delayed",
        "pending",
    }:
        raise ValueError(f"Invalid shipment status: {value}")
    return v


class StorageType(StrEnum):
    COLD = "cold"
    DRY = "dry"
    CONTROLLED_ATMOSPHERE = "controlled_atmosphere"
    GRAIN_SILO = "grain_silo"
    GENERAL = "general"


class CollectionPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Arabic translations
VEHICLE_TYPE_AR = {
    VehicleType.TRUCK: "شاحنة",
    VehicleType.PICKUP: "بيك أب",
    VehicleType.VAN: "فان",
    VehicleType.REFRIGERATED: "مبردة",
    VehicleType.TANKER: "صهريج",
    VehicleType.TRACTOR_TRAILER: "مقطورة جرار",
}

VEHICLE_STATUS_AR = {
    VehicleStatus.AVAILABLE: "متاح",
    VehicleStatus.IN_TRANSIT: "في الطريق",
    VehicleStatus.LOADING: "قيد التحميل",
    VehicleStatus.UNLOADING: "قيد التفريغ",
    VehicleStatus.MAINTENANCE: "صيانة",
    VehicleStatus.OUT_OF_SERVICE: "خارج الخدمة",
}

SHIPMENT_STATUS_AR = {
    ShipmentStatus.PENDING: "قيد الانتظار",
    ShipmentStatus.SCHEDULED: "مجدول",
    ShipmentStatus.COLLECTING: "قيد الجمع",
    ShipmentStatus.IN_TRANSIT: "في الطريق",
    ShipmentStatus.AT_STORAGE: "في المخزن",
    ShipmentStatus.DELIVERING: "قيد التسليم",
    ShipmentStatus.DELIVERED: "تم التسليم",
    ShipmentStatus.DELAYED: "متأخر",
    ShipmentStatus.CANCELLED: "ملغى",
}

# String-keyed variant (for output emission since canonical values are strings)
SHIPMENT_STATUS_AR_STR = {k.value: v for k, v in SHIPMENT_STATUS_AR.items()}

STORAGE_TYPE_AR = {
    StorageType.COLD: "تبريد",
    StorageType.DRY: "جاف",
    StorageType.CONTROLLED_ATMOSPHERE: "جو متحكم",
    StorageType.GRAIN_SILO: "صومعة حبوب",
    StorageType.GENERAL: "عام",
}

PRIORITY_AR = {
    CollectionPriority.LOW: "منخفضة",
    CollectionPriority.MEDIUM: "متوسطة",
    CollectionPriority.HIGH: "عالية",
    CollectionPriority.URGENT: "عاجلة",
}


# ==============================================================================
# Request/Response Models
# ==============================================================================


class Vehicle(BaseModel):
    """Fleet vehicle model - نموذج مركبة الأسطول"""

    vehicle_id: str
    tenant_id: str
    name: str
    name_ar: str | None = None
    vehicle_type: VehicleType
    vehicle_type_ar: str | None = None
    status: VehicleStatus
    status_ar: str | None = None
    license_plate: str
    capacity_kg: float
    capacity_volume_m3: float | None = None
    driver_id: str | None = None
    driver_name: str | None = None
    current_lat: float | None = None
    current_lon: float | None = None
    fuel_level_percent: float | None = None
    last_maintenance_at: datetime | None = None
    next_maintenance_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] | None = None


class VehicleCreate(BaseModel):
    """Create vehicle request"""

    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str | None = None
    vehicle_type: VehicleType
    license_plate: str = Field(..., min_length=1, max_length=20)
    capacity_kg: float = Field(..., gt=0)
    capacity_volume_m3: float | None = None
    driver_id: str | None = None
    metadata: dict[str, Any] | None = None


class VehicleUpdate(BaseModel):
    """Update vehicle request"""

    name: str | None = None
    name_ar: str | None = None
    status: VehicleStatus | None = None
    driver_id: str | None = None
    current_lat: float | None = None
    current_lon: float | None = None
    fuel_level_percent: float | None = None
    metadata: dict[str, Any] | None = None


class DriverStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Driver(BaseModel):
    """Driver model - نموذج السائق"""

    id: str
    tenant_id: str
    name: str
    name_ar: str | None = None
    phone: str | None = None
    license_number: str | None = None
    vehicle_type: VehicleType | None = None
    status: DriverStatus = DriverStatus.ACTIVE
    created_at: datetime
    version: int = 1


class DriverCreate(BaseModel):
    """Create driver request"""

    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str | None = None
    phone: str | None = None
    license_number: str | None = None
    vehicle_type: VehicleType | None = None
    status: DriverStatus = DriverStatus.ACTIVE


class StorageFacility(BaseModel):
    """Storage facility model - نموذج مرفق التخزين"""

    facility_id: str
    tenant_id: str
    name: str
    name_ar: str | None = None
    storage_type: StorageType
    storage_type_ar: str | None = None
    address: str
    address_ar: str | None = None
    lat: float
    lon: float
    total_capacity_kg: float
    available_capacity_kg: float
    temperature_min_c: float | None = None
    temperature_max_c: float | None = None
    humidity_min_percent: float | None = None
    humidity_max_percent: float | None = None
    current_temperature_c: float | None = None
    current_humidity_percent: float | None = None
    is_active: bool = True
    contact_phone: str | None = None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] | None = None


class StorageFacilityCreate(BaseModel):
    """Create storage facility request"""

    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str | None = None
    storage_type: StorageType
    address: str
    address_ar: str | None = None
    lat: float
    lon: float
    total_capacity_kg: float = Field(..., gt=0)
    temperature_min_c: float | None = None
    temperature_max_c: float | None = None
    humidity_min_percent: float | None = None
    humidity_max_percent: float | None = None
    contact_phone: str | None = None
    metadata: dict[str, Any] | None = None


class HarvestCollection(BaseModel):
    """Harvest collection schedule - جدول جمع المحاصيل"""

    collection_id: str
    tenant_id: str
    field_id: str
    field_name: str
    field_name_ar: str | None = None
    crop_type: str
    crop_type_ar: str | None = None
    estimated_quantity_kg: float
    actual_quantity_kg: float | None = None
    priority: CollectionPriority
    priority_ar: str | None = None
    scheduled_date: datetime
    actual_collection_date: datetime | None = None
    pickup_lat: float
    pickup_lon: float
    assigned_vehicle_id: str | None = None
    destination_facility_id: str | None = None
    status: ShipmentStatus
    status_ar: str | None = None
    notes: str | None = None
    notes_ar: str | None = None
    created_at: datetime
    updated_at: datetime


class HarvestCollectionCreate(BaseModel):
    """Create harvest collection request"""

    field_id: str
    field_name: str
    field_name_ar: str | None = None
    crop_type: str
    crop_type_ar: str | None = None
    estimated_quantity_kg: float = Field(..., gt=0)
    priority: CollectionPriority = CollectionPriority.MEDIUM
    scheduled_date: datetime
    pickup_lat: float
    pickup_lon: float
    destination_facility_id: str | None = None
    notes: str | None = None
    notes_ar: str | None = None


class Shipment(BaseModel):
    """Shipment/delivery model - نموذج الشحنة

    Status field accepts both legacy and canonical values. See module-level
    `normalize_status()` and `CANONICAL_STATUSES`.

    Soft/UX states (see ShipmentStatus docstring):
      - `pending`: Frontend-only; persisted as `scheduled`.
      - `delayed`: Frontend-only; persisted as `in_transit` with
        metadata.delayed=True.
    """

    shipment_id: str
    tenant_id: str
    vehicle_id: str
    driver_id: str | None = None
    origin_facility_id: str | None = None
    destination_facility_id: str | None = None
    destination_address: str | None = None
    destination_lat: float | None = None
    destination_lon: float | None = None
    cargo_description: str
    cargo_description_ar: str | None = None
    weight_kg: float
    status: str
    status_ar: str | None = None
    scheduled_departure: datetime
    actual_departure: datetime | None = None
    estimated_arrival: datetime | None = None
    actual_arrival: datetime | None = None
    route_waypoints: list[dict[str, float]] | None = None
    current_lat: float | None = None
    current_lon: float | None = None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] | None = None

    # StatusConverter: accept both old and new values on input,
    # emit canonical persistable value on output.
    @field_validator("status", mode="before")
    @classmethod
    def _normalize_status(cls, v):
        return normalize_status(v) if v is not None else v


class ShipmentCreate(BaseModel):
    """Create shipment request"""

    vehicle_id: str
    driver_id: str | None = None
    origin_facility_id: str | None = None
    destination_facility_id: str | None = None
    destination_address: str | None = None
    destination_lat: float | None = None
    destination_lon: float | None = None
    cargo_description: str
    cargo_description_ar: str | None = None
    weight_kg: float = Field(..., gt=0)
    scheduled_departure: datetime
    estimated_arrival: datetime | None = None


class RouteOptimizationRequest(BaseModel):
    """Request for route optimization - طلب تحسين المسار"""

    vehicle_id: str
    start_lat: float
    start_lon: float
    collection_ids: list[str]
    return_to_start: bool = True
    max_weight_kg: float | None = None


class RouteOptimizationResult(BaseModel):
    """Route optimization result - نتيجة تحسين المسار"""

    vehicle_id: str
    optimized_order: list[str]
    total_distance_km: float
    estimated_duration_hours: float
    waypoints: list[dict[str, Any]]
    message: str
    message_ar: str


# ==============================================================================
# In-Memory Storage (Replace with database in production)
# ==============================================================================

VEHICLES: dict[str, dict] = {}
STORAGE_FACILITIES: dict[str, dict] = {}
HARVEST_COLLECTIONS: dict[str, dict] = {}
SHIPMENTS: dict[str, dict] = {}
DRIVERS: dict[str, dict] = {}


def seed_demo_data(_db: Any = None) -> None:
    """Seed demo data for testing - بيانات تجريبية للاختبار.

    The `_db` parameter is unused here (logistics-service keeps its demo
    stores in-memory) but is accepted for signature parity with sibling
    services (`equipment-service`, `task-service`) so cross-file static
    analyzers do not mis-resolve the symbol.
    """
    now = datetime.now(UTC)

    # Demo vehicles
    demo_vehicles = [
        {
            "vehicle_id": "veh_001",
            "tenant_id": "tenant_demo",
            "name": "Refrigerated Truck 01",
            "name_ar": "شاحنة مبردة 01",
            "vehicle_type": VehicleType.REFRIGERATED.value,
            "status": VehicleStatus.AVAILABLE.value,
            "license_plate": "ABC-1234",
            "capacity_kg": 5000,
            "capacity_volume_m3": 25,
            "driver_id": "driver_001",
            "driver_name": "Ahmed Mohammed",
            "current_lat": 15.3694,
            "current_lon": 44.1910,
            "fuel_level_percent": 85,
            "created_at": now - timedelta(days=180),
            "updated_at": now - timedelta(hours=2),
        },
        {
            "vehicle_id": "veh_002",
            "tenant_id": "tenant_demo",
            "name": "Pickup Truck 01",
            "name_ar": "بيك أب 01",
            "vehicle_type": VehicleType.PICKUP.value,
            "status": VehicleStatus.IN_TRANSIT.value,
            "license_plate": "XYZ-5678",
            "capacity_kg": 1500,
            "capacity_volume_m3": 8,
            "driver_id": "driver_002",
            "driver_name": "Ali Hassan",
            "current_lat": 15.4021,
            "current_lon": 44.2105,
            "fuel_level_percent": 60,
            "created_at": now - timedelta(days=120),
            "updated_at": now - timedelta(minutes=30),
        },
    ]

    for v in demo_vehicles:
        VEHICLES[v["vehicle_id"]] = v

    # Demo storage facilities
    demo_facilities = [
        {
            "facility_id": "fac_001",
            "tenant_id": "tenant_demo",
            "name": "Central Cold Storage",
            "name_ar": "التخزين البارد المركزي",
            "storage_type": StorageType.COLD.value,
            "address": "Industrial Area, Sanaa",
            "address_ar": "المنطقة الصناعية، صنعاء",
            "lat": 15.3547,
            "lon": 44.2066,
            "total_capacity_kg": 50000,
            "available_capacity_kg": 35000,
            "temperature_min_c": 2,
            "temperature_max_c": 8,
            "humidity_min_percent": 85,
            "humidity_max_percent": 95,
            "current_temperature_c": 4.5,
            "current_humidity_percent": 90,
            "is_active": True,
            "contact_phone": "+967-1-234567",
            "created_at": now - timedelta(days=365),
            "updated_at": now - timedelta(days=1),
        },
        {
            "facility_id": "fac_002",
            "tenant_id": "tenant_demo",
            "name": "Grain Silo North",
            "name_ar": "صومعة الحبوب الشمالية",
            "storage_type": StorageType.GRAIN_SILO.value,
            "address": "Agricultural Zone, Dhamar",
            "address_ar": "المنطقة الزراعية، ذمار",
            "lat": 14.5426,
            "lon": 44.4050,
            "total_capacity_kg": 100000,
            "available_capacity_kg": 45000,
            "humidity_min_percent": 12,
            "humidity_max_percent": 14,
            "is_active": True,
            "contact_phone": "+967-6-789012",
            "created_at": now - timedelta(days=500),
            "updated_at": now - timedelta(days=3),
        },
    ]

    for f in demo_facilities:
        STORAGE_FACILITIES[f["facility_id"]] = f

    # Demo harvest collections
    demo_collections = [
        {
            "collection_id": "col_001",
            "tenant_id": "tenant_demo",
            "field_id": "field_north",
            "field_name": "North Field - Wheat",
            "field_name_ar": "الحقل الشمالي - قمح",
            "crop_type": "wheat",
            "crop_type_ar": "قمح",
            "estimated_quantity_kg": 2500,
            "actual_quantity_kg": None,
            "priority": CollectionPriority.HIGH.value,
            "scheduled_date": now + timedelta(days=2),
            "pickup_lat": 15.3800,
            "pickup_lon": 44.2000,
            "assigned_vehicle_id": "veh_001",
            "destination_facility_id": "fac_002",
            "status": ShipmentStatus.SCHEDULED.value,
            "notes": "Ready for harvest",
            "notes_ar": "جاهز للحصاد",
            "created_at": now - timedelta(days=5),
            "updated_at": now - timedelta(hours=6),
        },
        {
            "collection_id": "col_002",
            "tenant_id": "tenant_demo",
            "field_id": "field_south",
            "field_name": "South Field - Tomatoes",
            "field_name_ar": "الحقل الجنوبي - طماطم",
            "crop_type": "tomato",
            "crop_type_ar": "طماطم",
            "estimated_quantity_kg": 1200,
            "actual_quantity_kg": None,
            "priority": CollectionPriority.URGENT.value,
            "scheduled_date": now + timedelta(hours=12),
            "pickup_lat": 15.3500,
            "pickup_lon": 44.1800,
            "assigned_vehicle_id": "veh_002",
            "destination_facility_id": "fac_001",
            "status": ShipmentStatus.COLLECTING.value,
            "notes": "Perishable - needs cold storage",
            "notes_ar": "قابل للتلف - يحتاج تخزين بارد",
            "created_at": now - timedelta(days=1),
            "updated_at": now - timedelta(hours=1),
        },
    ]

    for c in demo_collections:
        HARVEST_COLLECTIONS[c["collection_id"]] = c

    # Demo drivers
    demo_drivers = [
        {
            "id": "driver_001",
            "tenant_id": "tenant_demo",
            "name": "Ahmed Mohammed",
            "name_ar": "أحمد محمد",
            "phone": "+967-771-123-456",
            "license_number": "DL-YE-001",
            "vehicle_type": VehicleType.REFRIGERATED.value,
            "status": DriverStatus.ACTIVE.value,
            "created_at": now - timedelta(days=365),
            "version": 1,
        },
        {
            "id": "driver_002",
            "tenant_id": "tenant_demo",
            "name": "Ali Hassan",
            "name_ar": "علي حسن",
            "phone": "+967-771-456-789",
            "license_number": "DL-YE-002",
            "vehicle_type": VehicleType.PICKUP.value,
            "status": DriverStatus.ACTIVE.value,
            "created_at": now - timedelta(days=200),
            "version": 1,
        },
    ]
    for d in demo_drivers:
        DRIVERS[d["id"]] = d

    logger.info("Demo data seeded successfully")


# ==============================================================================
# Helper Functions
# ==============================================================================


def get_tenant_id(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
    user: User | None = Depends(get_current_user),
) -> str:
    """Extract tenant ID strictly from the authenticated JWT `tid` claim.

    Security: In production we do NOT trust the X-Tenant-Id header. The tenant
    is pulled exclusively from the JWT propagated via the auth dependency,
    which exposes `user.tenant_id` populated from the `tid` claim.

    The header fallback is retained ONLY for development/testing environments
    where authentication is not wired up (AUTH_AVAILABLE=False).
    """
    # Primary: trust only the JWT-derived user context.
    if AUTH_AVAILABLE and user and getattr(user, "tenant_id", None):
        return user.tenant_id

    # Dev/test fallback path: authentication backend unavailable.
    if not AUTH_AVAILABLE:
        if x_tenant_id:
            return x_tenant_id
        return "tenant_demo"

    # Auth is available but user has no tenant_id — reject.
    raise HTTPException(
        status_code=401,
        detail="Authenticated user has no tenant context (missing `tid` claim)",
    )


# Strip newlines and control characters from values before logging them to
# prevent log-injection / log-forging (CodeQL py/log-injection). Any value
# that flows from a request (tenant_id, user_id, ids in NATS subjects, etc.)
# MUST be sanitized before being interpolated into a log message.
_LOG_INJECTION_RE = re.compile(r"[\r\n\t\x00-\x1f\x7f]")


def sanitize_log(value: Any) -> str:
    """Make a value safe for inclusion in a log line.

    Replaces CR/LF/TAB/NULL/control characters with `?` and caps the result
    at 500 characters to protect against log-line flooding.
    """
    if value is None:
        return ""
    text = str(value)
    cleaned = _LOG_INJECTION_RE.sub("?", text)
    return cleaned[:500]


async def publish_event(subject: str, data: dict):
    """Publish event to NATS"""
    global _nats_client
    if _nats_client and _nats_available:
        try:
            await _nats_client.publish(subject, json.dumps(data).encode())
            logger.info("Published event to %s", sanitize_log(subject))
        except Exception as e:
            logger.warning("Failed to publish event: %s", sanitize_log(str(e)))


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate approximate distance between two points in km (Haversine formula simplified)"""
    import math

    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ==============================================================================
# Lifespan Context Manager
# ==============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - manage NATS and database connections"""
    global _nats_client

    # Startup
    logger.info("Starting Logistics Service...")

    # Seed demo data
    seed_demo_data()
    logger.info("Demo data initialized")

    # Initialize NATS connection (optional)
    if _nats_available and NATS_URL:
        try:
            _nats_client = await nats.connect(NATS_URL)
            from shared.logging_config import sanitize_url

            logger.info(f"NATS connected: {sanitize_url(NATS_URL)}")
        except Exception as e:
            logger.warning(f"Failed to connect to NATS: {e}")

    logger.info(f"Logistics Service ready on port {SERVICE_PORT}")

    yield

    # Shutdown
    logger.info("Shutting down Logistics Service...")

    # Close NATS connection
    if _nats_client:
        try:
            await _nats_client.close()
            logger.info("NATS connection closed")
        except Exception as e:
            logger.error(f"Error closing NATS: {e}")

    logger.info("Logistics Service stopped")


# ==============================================================================
# FastAPI App
# ==============================================================================

app = FastAPI(
    title="SAHOOL Logistics Service | خدمة اللوجستيات",
    description="Agricultural logistics management - fleet, storage, collection, and delivery optimization",
    version=SERVICE_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
if setup_exception_handlers:
    setup_exception_handlers(app)
if add_request_id_middleware:
    add_request_id_middleware(app)

# CORS Configuration
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
)

# Security headers
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

# Tenant context middleware - عزل المستأجرين
app.add_middleware(TenantContextMiddleware)


# ==============================================================================
# Deprecation headers middleware (RFC 8594)
# ==============================================================================
# Legacy paths (without the /logistics/ segment) are still mounted as aliases
# but receive RFC 8594 deprecation headers so API clients can migrate.

_DEPRECATED_PATHS = {
    "/api/v1/shipments",
    "/api/v1/stats",
}
_DEPRECATION_SUNSET = "Wed, 01 Jul 2026 00:00:00 GMT"


def _is_deprecated_path(path: str) -> bool:
    """Return True if the request path matches a deprecated (legacy) alias."""
    # Match exact path or path + suffix (e.g. /api/v1/shipments/{id}/status)
    for deprecated in _DEPRECATED_PATHS:
        if path == deprecated or path.startswith(deprecated + "/") or path.startswith(deprecated + "?"):
            return True
    return False


class DeprecationHeadersMiddleware(BaseHTTPMiddleware):
    """Add RFC 8594 deprecation headers for legacy path aliases."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if _is_deprecated_path(request.url.path):
            response.headers["X-API-Deprecated"] = "true"
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = _DEPRECATION_SUNSET
            # Migration hint: new canonical path
            new_path = request.url.path.replace("/api/v1/", "/api/v1/logistics/", 1)
            response.headers["Link"] = f'<{new_path}>; rel="successor-version"'
        return response


app.add_middleware(DeprecationHeadersMiddleware)


# ==============================================================================
# Health Endpoints
# ==============================================================================


@app.get("/healthz")
async def health_check():
    """
    Liveness probe endpoint
    نقطة نهاية فحص الحيوية
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }


@app.get("/readyz")
async def readiness_check():
    """
    Readiness probe endpoint
    نقطة نهاية فحص الجاهزية
    """
    nats_ready = _nats_client is not None if _nats_available else True

    return {
        "status": "ready" if nats_ready else "not_ready",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "nats_connected": _nats_client is not None if _nats_available else False,
        "vehicles_count": len(VEHICLES),
        "facilities_count": len(STORAGE_FACILITIES),
        "collections_count": len(HARVEST_COLLECTIONS),
    }


@app.get("/health")
async def combined_health():
    """
    Combined health check
    فحص صحة شامل
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "nats": "connected" if (_nats_client is not None) else "disconnected",
        "stats": {
            "vehicles": len(VEHICLES),
            "facilities": len(STORAGE_FACILITIES),
            "active_collections": len(
                [c for c in HARVEST_COLLECTIONS.values() if c["status"] != ShipmentStatus.DELIVERED.value]
            ),
            "active_shipments": len(
                [
                    s
                    for s in SHIPMENTS.values()
                    if s["status"] not in [ShipmentStatus.DELIVERED.value, ShipmentStatus.CANCELLED.value]
                ]
            ),
        },
    }


# ==============================================================================
# Fleet Management Endpoints
# ==============================================================================


@app.get("/api/v1/vehicles", response_model=dict)
async def list_vehicles(
    vehicle_type: VehicleType | None = Query(None, description="Filter by vehicle type"),
    status: VehicleStatus | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    List all fleet vehicles
    قائمة جميع مركبات الأسطول
    """
    vehicles = [v for v in VEHICLES.values() if v["tenant_id"] == tenant_id]

    if vehicle_type:
        vehicles = [v for v in vehicles if v["vehicle_type"] == vehicle_type.value]
    if status:
        vehicles = [v for v in vehicles if v["status"] == status.value]

    total = len(vehicles)
    vehicles = vehicles[offset : offset + limit]

    # Add Arabic translations
    for v in vehicles:
        v["vehicle_type_ar"] = VEHICLE_TYPE_AR.get(VehicleType(v["vehicle_type"]), v["vehicle_type"])
        v["status_ar"] = VEHICLE_STATUS_AR.get(VehicleStatus(v["status"]), v["status"])

    return {
        "vehicles": vehicles,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(
    vehicle_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Get vehicle by ID
    الحصول على مركبة بواسطة المعرف
    """
    vehicle = VEHICLES.get(vehicle_id)
    if not vehicle or vehicle["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Vehicle not found | المركبة غير موجودة")

    vehicle["vehicle_type_ar"] = VEHICLE_TYPE_AR.get(VehicleType(vehicle["vehicle_type"]))
    vehicle["status_ar"] = VEHICLE_STATUS_AR.get(VehicleStatus(vehicle["status"]))
    return Vehicle(**vehicle)


@app.post("/api/v1/vehicles", response_model=Vehicle, status_code=201)
async def create_vehicle(
    data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Create a new vehicle
    إنشاء مركبة جديدة
    """
    now = datetime.now(UTC)
    vehicle_id = f"veh_{uuid.uuid4().hex[:8]}"

    vehicle = {
        "vehicle_id": vehicle_id,
        "tenant_id": tenant_id,
        "name": data.name,
        "name_ar": data.name_ar,
        "vehicle_type": data.vehicle_type.value,
        "status": VehicleStatus.AVAILABLE.value,
        "license_plate": data.license_plate,
        "capacity_kg": data.capacity_kg,
        "capacity_volume_m3": data.capacity_volume_m3,
        "driver_id": data.driver_id,
        "driver_name": None,
        "current_lat": None,
        "current_lon": None,
        "fuel_level_percent": None,
        "last_maintenance_at": None,
        "next_maintenance_at": None,
        "created_at": now,
        "updated_at": now,
        "metadata": data.metadata,
    }

    VEHICLES[vehicle_id] = vehicle

    # Publish event
    await publish_event(
        f"sahool.{tenant_id}.logistics.vehicle.created",
        {"vehicle_id": vehicle_id, "tenant_id": tenant_id, "vehicle_type": data.vehicle_type.value},
    )

    vehicle["vehicle_type_ar"] = VEHICLE_TYPE_AR.get(data.vehicle_type)
    vehicle["status_ar"] = VEHICLE_STATUS_AR.get(VehicleStatus.AVAILABLE)
    return Vehicle(**vehicle)


@app.put("/api/v1/vehicles/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: str,
    data: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Update vehicle
    تحديث المركبة
    """
    vehicle = VEHICLES.get(vehicle_id)
    if not vehicle or vehicle["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Vehicle not found | المركبة غير موجودة")

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"]:
        update_data["status"] = update_data["status"].value

    vehicle.update(update_data)
    vehicle["updated_at"] = datetime.now(UTC)
    VEHICLES[vehicle_id] = vehicle

    vehicle["vehicle_type_ar"] = VEHICLE_TYPE_AR.get(VehicleType(vehicle["vehicle_type"]))
    vehicle["status_ar"] = VEHICLE_STATUS_AR.get(VehicleStatus(vehicle["status"]))
    return Vehicle(**vehicle)


@app.post("/api/v1/vehicles/{vehicle_id}/location")
async def update_vehicle_location(
    vehicle_id: str,
    lat: float = Query(...),
    lon: float = Query(...),
    fuel_level: float | None = Query(None),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Update vehicle GPS location
    تحديث موقع GPS للمركبة
    """
    vehicle = VEHICLES.get(vehicle_id)
    if not vehicle or vehicle["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Vehicle not found | المركبة غير موجودة")

    vehicle["current_lat"] = lat
    vehicle["current_lon"] = lon
    if fuel_level is not None:
        vehicle["fuel_level_percent"] = fuel_level
    vehicle["updated_at"] = datetime.now(UTC)

    # Publish location event
    await publish_event(
        f"sahool.{tenant_id}.logistics.vehicle.location",
        {"vehicle_id": vehicle_id, "lat": lat, "lon": lon, "fuel_level": fuel_level},
    )

    return {"status": "ok", "message": "Location updated | تم تحديث الموقع"}


# ==============================================================================
# Storage Facility Endpoints
# ==============================================================================


@app.get("/api/v1/storage-facilities", response_model=dict)
async def list_storage_facilities(
    storage_type: StorageType | None = Query(None),
    active_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    List storage facilities
    قائمة مرافق التخزين
    """
    facilities = [f for f in STORAGE_FACILITIES.values() if f["tenant_id"] == tenant_id]

    if storage_type:
        facilities = [f for f in facilities if f["storage_type"] == storage_type.value]
    if active_only:
        facilities = [f for f in facilities if f.get("is_active", True)]

    total = len(facilities)
    facilities = facilities[offset : offset + limit]

    for f in facilities:
        f["storage_type_ar"] = STORAGE_TYPE_AR.get(StorageType(f["storage_type"]))

    return {
        "facilities": facilities,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/storage-facilities/{facility_id}", response_model=StorageFacility)
async def get_storage_facility(
    facility_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Get storage facility by ID
    الحصول على مرفق التخزين بواسطة المعرف
    """
    facility = STORAGE_FACILITIES.get(facility_id)
    if not facility or facility["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Facility not found | المرفق غير موجود")

    facility["storage_type_ar"] = STORAGE_TYPE_AR.get(StorageType(facility["storage_type"]))
    return StorageFacility(**facility)


@app.post("/api/v1/storage-facilities", response_model=StorageFacility, status_code=201)
async def create_storage_facility(
    data: StorageFacilityCreate,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Create a new storage facility
    إنشاء مرفق تخزين جديد
    """
    now = datetime.now(UTC)
    facility_id = f"fac_{uuid.uuid4().hex[:8]}"

    facility = {
        "facility_id": facility_id,
        "tenant_id": tenant_id,
        "name": data.name,
        "name_ar": data.name_ar,
        "storage_type": data.storage_type.value,
        "address": data.address,
        "address_ar": data.address_ar,
        "lat": data.lat,
        "lon": data.lon,
        "total_capacity_kg": data.total_capacity_kg,
        "available_capacity_kg": data.total_capacity_kg,
        "temperature_min_c": data.temperature_min_c,
        "temperature_max_c": data.temperature_max_c,
        "humidity_min_percent": data.humidity_min_percent,
        "humidity_max_percent": data.humidity_max_percent,
        "current_temperature_c": None,
        "current_humidity_percent": None,
        "is_active": True,
        "contact_phone": data.contact_phone,
        "created_at": now,
        "updated_at": now,
        "metadata": data.metadata,
    }

    STORAGE_FACILITIES[facility_id] = facility

    await publish_event(
        f"sahool.{tenant_id}.logistics.facility.created",
        {
            "facility_id": facility_id,
            "tenant_id": tenant_id,
            "storage_type": data.storage_type.value,
        },
    )

    facility["storage_type_ar"] = STORAGE_TYPE_AR.get(data.storage_type)
    return StorageFacility(**facility)


@app.post("/api/v1/storage-facilities/{facility_id}/conditions")
async def update_facility_conditions(
    facility_id: str,
    temperature_c: float | None = Query(None),
    humidity_percent: float | None = Query(None),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Update storage facility conditions (temperature, humidity)
    تحديث ظروف مرفق التخزين (درجة الحرارة، الرطوبة)
    """
    facility = STORAGE_FACILITIES.get(facility_id)
    if not facility or facility["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Facility not found | المرفق غير موجود")

    if temperature_c is not None:
        facility["current_temperature_c"] = temperature_c
    if humidity_percent is not None:
        facility["current_humidity_percent"] = humidity_percent
    facility["updated_at"] = datetime.now(UTC)

    # Check for alerts
    alerts = []
    if temperature_c is not None:
        if facility.get("temperature_min_c") and temperature_c < facility["temperature_min_c"]:
            alerts.append(f"Temperature below minimum: {temperature_c}C < {facility['temperature_min_c']}C")
        if facility.get("temperature_max_c") and temperature_c > facility["temperature_max_c"]:
            alerts.append(f"Temperature above maximum: {temperature_c}C > {facility['temperature_max_c']}C")

    return {
        "status": "ok",
        "message": "Conditions updated | تم تحديث الظروف",
        "alerts": alerts,
    }


# ==============================================================================
# Harvest Collection Endpoints
# ==============================================================================


@app.get("/api/v1/collections", response_model=dict)
async def list_harvest_collections(
    status: ShipmentStatus | None = Query(None),
    priority: CollectionPriority | None = Query(None),
    scheduled_from: datetime | None = Query(None),
    scheduled_to: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    List harvest collections
    قائمة جمع المحاصيل
    """
    collections = [c for c in HARVEST_COLLECTIONS.values() if c["tenant_id"] == tenant_id]

    if status:
        collections = [c for c in collections if c["status"] == status.value]
    if priority:
        collections = [c for c in collections if c["priority"] == priority.value]
    if scheduled_from:
        collections = [c for c in collections if c["scheduled_date"] >= scheduled_from]
    if scheduled_to:
        collections = [c for c in collections if c["scheduled_date"] <= scheduled_to]

    total = len(collections)
    collections = collections[offset : offset + limit]

    for c in collections:
        c["priority_ar"] = PRIORITY_AR.get(CollectionPriority(c["priority"]))
        c["status_ar"] = SHIPMENT_STATUS_AR.get(ShipmentStatus(c["status"]))

    return {
        "collections": collections,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.post("/api/v1/collections", response_model=HarvestCollection, status_code=201)
async def create_harvest_collection(
    data: HarvestCollectionCreate,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Schedule a new harvest collection
    جدولة جمع محاصيل جديد
    """
    now = datetime.now(UTC)
    collection_id = f"col_{uuid.uuid4().hex[:8]}"

    collection = {
        "collection_id": collection_id,
        "tenant_id": tenant_id,
        "field_id": data.field_id,
        "field_name": data.field_name,
        "field_name_ar": data.field_name_ar,
        "crop_type": data.crop_type,
        "crop_type_ar": data.crop_type_ar,
        "estimated_quantity_kg": data.estimated_quantity_kg,
        "actual_quantity_kg": None,
        "priority": data.priority.value,
        "scheduled_date": data.scheduled_date,
        "actual_collection_date": None,
        "pickup_lat": data.pickup_lat,
        "pickup_lon": data.pickup_lon,
        "assigned_vehicle_id": None,
        "destination_facility_id": data.destination_facility_id,
        "status": ShipmentStatus.SCHEDULED.value,
        "notes": data.notes,
        "notes_ar": data.notes_ar,
        "created_at": now,
        "updated_at": now,
    }

    HARVEST_COLLECTIONS[collection_id] = collection

    await publish_event(
        f"sahool.{tenant_id}.logistics.collection.scheduled",
        {
            "collection_id": collection_id,
            "field_id": data.field_id,
            "crop_type": data.crop_type,
            "scheduled_date": data.scheduled_date.isoformat(),
            "priority": data.priority.value,
        },
    )

    collection["priority_ar"] = PRIORITY_AR.get(data.priority)
    collection["status_ar"] = SHIPMENT_STATUS_AR.get(ShipmentStatus.SCHEDULED)
    return HarvestCollection(**collection)


@app.post("/api/v1/collections/{collection_id}/assign")
async def assign_vehicle_to_collection(
    collection_id: str,
    vehicle_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Assign a vehicle to a harvest collection
    تعيين مركبة لجمع المحاصيل
    """
    collection = HARVEST_COLLECTIONS.get(collection_id)
    if not collection or collection["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Collection not found | الجمع غير موجود")

    vehicle = VEHICLES.get(vehicle_id)
    if not vehicle or vehicle["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Vehicle not found | المركبة غير موجودة")

    collection["assigned_vehicle_id"] = vehicle_id
    collection["updated_at"] = datetime.now(UTC)

    return {
        "status": "ok",
        "message": "Vehicle assigned | تم تعيين المركبة",
        "collection_id": collection_id,
        "vehicle_id": vehicle_id,
    }


@app.post("/api/v1/collections/{collection_id}/status")
async def update_collection_status(
    collection_id: str,
    status: ShipmentStatus = Query(...),
    actual_quantity_kg: float | None = Query(None),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Update harvest collection status
    تحديث حالة جمع المحاصيل
    """
    collection = HARVEST_COLLECTIONS.get(collection_id)
    if not collection or collection["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Collection not found | الجمع غير موجود")

    collection["status"] = status.value
    if actual_quantity_kg is not None:
        collection["actual_quantity_kg"] = actual_quantity_kg
    if status == ShipmentStatus.COLLECTING:
        collection["actual_collection_date"] = datetime.now(UTC)
    collection["updated_at"] = datetime.now(UTC)

    await publish_event(
        f"sahool.{tenant_id}.logistics.collection.status_changed",
        {"collection_id": collection_id, "status": status.value},
    )

    return {
        "status": "ok",
        "message": f"Status updated to {status.value} | تم تحديث الحالة إلى {SHIPMENT_STATUS_AR.get(status)}",
    }


# ==============================================================================
# Route Optimization Endpoints
# ==============================================================================


@app.post("/api/v1/routes/optimize", response_model=RouteOptimizationResult)
async def optimize_route(
    data: RouteOptimizationRequest,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Optimize collection route for a vehicle
    تحسين مسار الجمع للمركبة

    Uses a simple nearest-neighbor algorithm for demonstration.
    In production, integrate with a proper routing service.
    """
    vehicle = VEHICLES.get(data.vehicle_id)
    if not vehicle or vehicle["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Vehicle not found | المركبة غير موجودة")

    # Get collections
    collections = []
    for col_id in data.collection_ids:
        col = HARVEST_COLLECTIONS.get(col_id)
        if col and col["tenant_id"] == tenant_id:
            collections.append(col)

    if not collections:
        raise HTTPException(status_code=400, detail="No valid collections found | لم يتم العثور على جمع صالح")

    # Simple nearest-neighbor optimization
    optimized_order = []
    waypoints = []
    total_distance = 0
    current_lat, current_lon = data.start_lat, data.start_lon
    remaining = collections.copy()

    while remaining:
        # Find nearest collection
        nearest = min(
            remaining,
            key=lambda c: calculate_distance(current_lat, current_lon, c["pickup_lat"], c["pickup_lon"]),
        )
        distance = calculate_distance(current_lat, current_lon, nearest["pickup_lat"], nearest["pickup_lon"])
        total_distance += distance

        optimized_order.append(nearest["collection_id"])
        waypoints.append(
            {
                "collection_id": nearest["collection_id"],
                "field_name": nearest["field_name"],
                "field_name_ar": nearest.get("field_name_ar"),
                "lat": nearest["pickup_lat"],
                "lon": nearest["pickup_lon"],
                "estimated_quantity_kg": nearest["estimated_quantity_kg"],
                "distance_from_previous_km": round(distance, 2),
            }
        )

        current_lat, current_lon = nearest["pickup_lat"], nearest["pickup_lon"]
        remaining.remove(nearest)

    # Return to start if requested
    if data.return_to_start:
        return_distance = calculate_distance(current_lat, current_lon, data.start_lat, data.start_lon)
        total_distance += return_distance
        waypoints.append(
            {
                "type": "return",
                "lat": data.start_lat,
                "lon": data.start_lon,
                "distance_from_previous_km": round(return_distance, 2),
            }
        )

    # Estimate duration (assuming average 40 km/h + 30 min per stop)
    estimated_hours = (total_distance / 40) + (len(collections) * 0.5)

    return RouteOptimizationResult(
        vehicle_id=data.vehicle_id,
        optimized_order=optimized_order,
        total_distance_km=round(total_distance, 2),
        estimated_duration_hours=round(estimated_hours, 2),
        waypoints=waypoints,
        message=f"Optimized route with {len(collections)} stops, {round(total_distance, 1)} km total",
        message_ar=f"مسار محسن بـ {len(collections)} محطات، {round(total_distance, 1)} كم إجمالي",
    )


# ==============================================================================
# Shipment/Delivery Endpoints
# ==============================================================================


@app.get("/api/v1/logistics/shipments", response_model=dict)
@app.get("/api/v1/shipments", response_model=dict, include_in_schema=False)
async def list_shipments(
    status: str | None = Query(None, description="Filter by shipment status (canonical or legacy)"),
    vehicle_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    List shipments/deliveries
    قائمة الشحنات/التسليمات

    Returns an envelope:
    `{shipments: [...], total, limit, offset, pagination: {...}}`
    """
    shipments = [s for s in SHIPMENTS.values() if s["tenant_id"] == tenant_id]

    if status:
        try:
            normalized = normalize_status(status)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        shipments = [s for s in shipments if s["status"] == normalized]
    if vehicle_id:
        shipments = [s for s in shipments if s["vehicle_id"] == vehicle_id]

    total = len(shipments)
    shipments = shipments[offset : offset + limit]

    for s in shipments:
        s["status_ar"] = SHIPMENT_STATUS_AR_STR.get(s["status"], s["status"])

    return {
        "shipments": shipments,
        "total": total,
        "limit": limit,
        "offset": offset,
        "pagination": {"total": total, "limit": limit, "offset": offset},
    }


@app.post("/api/v1/logistics/shipments", response_model=Shipment, status_code=201)
@app.post("/api/v1/shipments", response_model=Shipment, status_code=201, include_in_schema=False)
async def create_shipment(
    data: ShipmentCreate,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Create a new shipment/delivery
    إنشاء شحنة/تسليم جديد
    """
    vehicle = VEHICLES.get(data.vehicle_id)
    if not vehicle or vehicle["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Vehicle not found | المركبة غير موجودة")

    now = datetime.now(UTC)
    shipment_id = f"ship_{uuid.uuid4().hex[:8]}"

    shipment = {
        "shipment_id": shipment_id,
        "tenant_id": tenant_id,
        "vehicle_id": data.vehicle_id,
        "driver_id": data.driver_id,
        "origin_facility_id": data.origin_facility_id,
        "destination_facility_id": data.destination_facility_id,
        "destination_address": data.destination_address,
        "destination_lat": data.destination_lat,
        "destination_lon": data.destination_lon,
        "cargo_description": data.cargo_description,
        "cargo_description_ar": data.cargo_description_ar,
        "weight_kg": data.weight_kg,
        "status": ShipmentStatus.SCHEDULED.value,
        "scheduled_departure": data.scheduled_departure,
        "actual_departure": None,
        "estimated_arrival": data.estimated_arrival,
        "actual_arrival": None,
        "route_waypoints": None,
        "current_lat": None,
        "current_lon": None,
        "created_at": now,
        "updated_at": now,
        "metadata": None,
    }

    SHIPMENTS[shipment_id] = shipment

    await publish_event(
        f"sahool.{tenant_id}.logistics.shipment.created",
        {"shipment_id": shipment_id, "vehicle_id": data.vehicle_id, "weight_kg": data.weight_kg},
    )

    shipment["status_ar"] = SHIPMENT_STATUS_AR.get(ShipmentStatus.SCHEDULED)
    return Shipment(**shipment)


@app.post("/api/v1/logistics/shipments/{shipment_id}/status")
@app.post("/api/v1/shipments/{shipment_id}/status", include_in_schema=False)
async def update_shipment_status(
    shipment_id: str,
    status: str = Query(..., description="Shipment status (canonical or legacy value)"),
    lat: float | None = Query(None),
    lon: float | None = Query(None),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Update shipment status
    تحديث حالة الشحنة

    Accepts both canonical backend statuses (scheduled, collecting, in_transit,
    at_storage, delivering, delivered, cancelled) and soft/UX frontend statuses
    (pending, delayed). The "pending" value is mapped to `scheduled`;
    "delayed" is mapped to `in_transit` with a metadata.delayed=True flag.
    """
    shipment = SHIPMENTS.get(shipment_id)
    if not shipment or shipment["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Shipment not found | الشحنة غير موجودة")

    # Accept both legacy and canonical values. Special-case "delayed" as a
    # soft state: persist as in_transit + delayed flag.
    raw_status = status
    delayed_flag = False
    try:
        normalized = normalize_status(raw_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if normalized == "delayed":
        delayed_flag = True
        normalized = "in_transit"

    now = datetime.now(UTC)
    shipment["status"] = normalized
    shipment["updated_at"] = now

    # Track delayed flag in metadata for re-emission as the "delayed" UX state.
    metadata = shipment.get("metadata") or {}
    if delayed_flag:
        metadata["delayed"] = True
        shipment["metadata"] = metadata
    elif "delayed" in metadata:
        metadata.pop("delayed", None)
        shipment["metadata"] = metadata or None

    if lat is not None:
        shipment["current_lat"] = lat
    if lon is not None:
        shipment["current_lon"] = lon

    if normalized == "in_transit" and shipment["actual_departure"] is None:
        shipment["actual_departure"] = now
    elif normalized == "delivered":
        shipment["actual_arrival"] = now

    await publish_event(
        f"sahool.{tenant_id}.logistics.shipment.status_changed",
        {"shipment_id": shipment_id, "status": normalized, "delayed": delayed_flag},
    )

    status_ar = SHIPMENT_STATUS_AR_STR.get(normalized, normalized)
    return {
        "status": "ok",
        "message": f"Status updated to {normalized} | تم تحديث الحالة إلى {status_ar}",
    }


# ==============================================================================
# Statistics Endpoint
# ==============================================================================


@app.get("/api/v1/logistics/stats")
@app.get("/api/v1/stats", include_in_schema=False)
async def get_logistics_stats(
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Get logistics statistics
    الحصول على إحصائيات اللوجستيات
    """
    vehicles = [v for v in VEHICLES.values() if v["tenant_id"] == tenant_id]
    facilities = [f for f in STORAGE_FACILITIES.values() if f["tenant_id"] == tenant_id]
    collections = [c for c in HARVEST_COLLECTIONS.values() if c["tenant_id"] == tenant_id]
    shipments = [s for s in SHIPMENTS.values() if s["tenant_id"] == tenant_id]

    available_vehicles = len([v for v in vehicles if v["status"] == VehicleStatus.AVAILABLE.value])
    in_transit_vehicles = len([v for v in vehicles if v["status"] == VehicleStatus.IN_TRANSIT.value])

    total_storage_capacity = sum(f["total_capacity_kg"] for f in facilities)
    available_storage = sum(f["available_capacity_kg"] for f in facilities)

    pending_collections = len([c for c in collections if c["status"] == ShipmentStatus.SCHEDULED.value])
    active_collections = len(
        [c for c in collections if c["status"] in [ShipmentStatus.COLLECTING.value, ShipmentStatus.IN_TRANSIT.value]]
    )

    active_shipments = len(
        [s for s in shipments if s["status"] not in [ShipmentStatus.DELIVERED.value, ShipmentStatus.CANCELLED.value]]
    )

    return {
        "tenant_id": tenant_id,
        "fleet": {
            "total_vehicles": len(vehicles),
            "available": available_vehicles,
            "in_transit": in_transit_vehicles,
            "message": f"{available_vehicles} مركبات متاحة من أصل {len(vehicles)}",
        },
        "storage": {
            "total_facilities": len(facilities),
            "total_capacity_kg": total_storage_capacity,
            "available_capacity_kg": available_storage,
            "utilization_percent": round((1 - available_storage / total_storage_capacity) * 100, 1)
            if total_storage_capacity > 0
            else 0,
            "message_ar": f"استخدام {round((1 - available_storage / total_storage_capacity) * 100, 1) if total_storage_capacity > 0 else 0}% من السعة",
        },
        "collections": {
            "total": len(collections),
            "pending": pending_collections,
            "active": active_collections,
            "message_ar": f"{pending_collections} جمع مجدول، {active_collections} نشط",
        },
        "shipments": {
            "total": len(shipments),
            "active": active_shipments,
            "message_ar": f"{active_shipments} شحنة نشطة",
        },
    }


# ==============================================================================
# Driver Endpoints - نقاط نهاية السائقين
# ==============================================================================


@app.get("/api/v1/logistics/drivers", response_model=dict)
async def list_drivers(
    status: DriverStatus | None = Query(None, description="Filter by driver status"),
    vehicle_type: VehicleType | None = Query(None, description="Filter by certified vehicle type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    List drivers in the fleet.
    قائمة سائقي الأسطول.

    Returns an envelope:
    `{drivers: [...], total, limit, offset, pagination: {...}}`
    """
    drivers = [d for d in DRIVERS.values() if d["tenant_id"] == tenant_id]

    if status:
        drivers = [d for d in drivers if d.get("status") == status.value]
    if vehicle_type:
        drivers = [d for d in drivers if d.get("vehicle_type") == vehicle_type.value]

    total = len(drivers)
    drivers = drivers[offset : offset + limit]

    return {
        "drivers": drivers,
        "total": total,
        "limit": limit,
        "offset": offset,
        "pagination": {"total": total, "limit": limit, "offset": offset},
    }


@app.get("/api/v1/logistics/drivers/{driver_id}", response_model=Driver)
async def get_driver(
    driver_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Get driver by ID.
    الحصول على سائق بواسطة المعرف.
    """
    driver = DRIVERS.get(driver_id)
    if not driver or driver["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Driver not found | السائق غير موجود")
    return Driver(**driver)


@app.post("/api/v1/logistics/drivers", response_model=Driver, status_code=201)
async def create_driver(
    data: DriverCreate,
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Create a new driver.
    إنشاء سائق جديد.
    """
    now = datetime.now(UTC)
    driver_id = f"driver_{uuid.uuid4().hex[:8]}"
    driver = {
        "id": driver_id,
        "tenant_id": tenant_id,
        "name": data.name,
        "name_ar": data.name_ar,
        "phone": data.phone,
        "license_number": data.license_number,
        "vehicle_type": data.vehicle_type.value if data.vehicle_type else None,
        "status": data.status.value,
        "created_at": now,
        "version": 1,
    }
    DRIVERS[driver_id] = driver

    await publish_event(
        f"sahool.{tenant_id}.logistics.driver.created",
        {"driver_id": driver_id, "tenant_id": tenant_id},
    )

    return Driver(**driver)


# ==============================================================================
# Include Report Routes from api/v1/
# تضمين مسارات التقارير من api/v1/
# ==============================================================================
try:
    from api.v1 import router as reports_router

    app.include_router(reports_router)
    logger.info("Logistics report routes included successfully")
except ImportError:
    logger.warning("Could not import report routes from api.v1")


# ==============================================================================
# Main Entry Point
# ==============================================================================

if __name__ == "__main__":
    import uvicorn

    # Host binding configurable via environment variable for security
    host = os.getenv("HOST", "0.0.0.0")  # nosec B104 - binding to all interfaces required for Docker container
    uvicorn.run(app, host=host, port=SERVICE_PORT)
