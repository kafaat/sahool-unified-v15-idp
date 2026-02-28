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
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum, StrEnum
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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

    class User(BaseModel):  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str = ""

    async def get_current_user():
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
        DATABASE_URL += "?sslmode=require" if "?" not in DATABASE_URL else "&sslmode=require"


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
    SCHEDULED = "scheduled"
    COLLECTING = "collecting"
    IN_TRANSIT = "in_transit"
    AT_STORAGE = "at_storage"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


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
    ShipmentStatus.SCHEDULED: "مجدول",
    ShipmentStatus.COLLECTING: "قيد الجمع",
    ShipmentStatus.IN_TRANSIT: "في الطريق",
    ShipmentStatus.AT_STORAGE: "في المخزن",
    ShipmentStatus.DELIVERING: "قيد التسليم",
    ShipmentStatus.DELIVERED: "تم التسليم",
    ShipmentStatus.CANCELLED: "ملغى",
}

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
    """Shipment/delivery model - نموذج الشحنة"""

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
    status: ShipmentStatus
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


def seed_demo_data():
    """Seed demo data for testing - بيانات تجريبية للاختبار"""
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

    logger.info("Demo data seeded successfully")


# ==============================================================================
# Helper Functions
# ==============================================================================


def get_tenant_id(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
    user: User | None = Depends(get_current_user),
) -> str:
    """Extract tenant ID from authenticated user or header"""
    if AUTH_AVAILABLE and user:
        return user.tenant_id
    if x_tenant_id:
        return x_tenant_id
    return "tenant_demo"


async def publish_event(subject: str, data: dict):
    """Publish event to NATS"""
    global _nats_client
    if _nats_client and _nats_available:
        try:
            await _nats_client.publish(subject, json.dumps(data).encode())
            logger.info(f"Published event to {subject}")
        except Exception as e:
            logger.warning(f"Failed to publish event: {e}")


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
            logger.info(f"NATS connected: {NATS_URL}")
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


@app.get("/api/v1/shipments", response_model=dict)
async def list_shipments(
    status: ShipmentStatus | None = Query(None),
    vehicle_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    List shipments/deliveries
    قائمة الشحنات/التسليمات
    """
    shipments = [s for s in SHIPMENTS.values() if s["tenant_id"] == tenant_id]

    if status:
        shipments = [s for s in shipments if s["status"] == status.value]
    if vehicle_id:
        shipments = [s for s in shipments if s["vehicle_id"] == vehicle_id]

    total = len(shipments)
    shipments = shipments[offset : offset + limit]

    for s in shipments:
        s["status_ar"] = SHIPMENT_STATUS_AR.get(ShipmentStatus(s["status"]))

    return {
        "shipments": shipments,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.post("/api/v1/shipments", response_model=Shipment, status_code=201)
async def create_shipment(
    data: ShipmentCreate,
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


@app.post("/api/v1/shipments/{shipment_id}/status")
async def update_shipment_status(
    shipment_id: str,
    status: ShipmentStatus = Query(...),
    lat: float | None = Query(None),
    lon: float | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Update shipment status
    تحديث حالة الشحنة
    """
    shipment = SHIPMENTS.get(shipment_id)
    if not shipment or shipment["tenant_id"] != tenant_id:
        raise HTTPException(status_code=404, detail="Shipment not found | الشحنة غير موجودة")

    now = datetime.now(UTC)
    shipment["status"] = status.value
    shipment["updated_at"] = now

    if lat is not None:
        shipment["current_lat"] = lat
    if lon is not None:
        shipment["current_lon"] = lon

    if status == ShipmentStatus.IN_TRANSIT and shipment["actual_departure"] is None:
        shipment["actual_departure"] = now
    elif status == ShipmentStatus.DELIVERED:
        shipment["actual_arrival"] = now

    await publish_event(
        f"sahool.{tenant_id}.logistics.shipment.status_changed",
        {"shipment_id": shipment_id, "status": status.value},
    )

    return {
        "status": "ok",
        "message": f"Status updated to {status.value} | تم تحديث الحالة إلى {SHIPMENT_STATUS_AR.get(status)}",
    }


# ==============================================================================
# Statistics Endpoint
# ==============================================================================


@app.get("/api/v1/stats")
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
# Main Entry Point
# ==============================================================================

if __name__ == "__main__":
    import uvicorn

    # Host binding configurable via environment variable for security
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=SERVICE_PORT)
