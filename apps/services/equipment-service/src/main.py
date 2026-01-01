"""
SAHOOL Equipment Service - خدمة إدارة المعدات والأصول
Port: 8101

Provides equipment/asset management:
- Equipment CRUD (tractors, pumps, drones, harvesters)
- Maintenance tracking and alerts
- Real-time status (fuel, hours, location)
- QR code registration
"""

import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "sahool-equipment-service"
SERVICE_PORT = int(os.getenv("PORT", "8101"))

app = FastAPI(
    title="SAHOOL Equipment Service",
    description="Agricultural equipment and asset management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - Secure configuration
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
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

# ═══════════════════════════════════════════════════════════════════════════
# Enums & Models
# ═══════════════════════════════════════════════════════════════════════════


class EquipmentType(str, Enum):
    TRACTOR = "tractor"
    PUMP = "pump"
    DRONE = "drone"
    HARVESTER = "harvester"
    SPRAYER = "sprayer"
    PIVOT = "pivot"
    SENSOR = "sensor"
    VEHICLE = "vehicle"
    OTHER = "other"


class EquipmentStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    REPAIR = "repair"


class MaintenancePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaintenanceType(str, Enum):
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
    name_ar: Optional[str] = None
    equipment_type: EquipmentType
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year: Optional[int] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    field_id: Optional[str] = None
    location_name: Optional[str] = None
    horsepower: Optional[int] = None
    fuel_capacity_liters: Optional[float] = None
    metadata: Optional[dict] = None


class EquipmentUpdate(BaseModel):
    """Update equipment properties"""

    name: Optional[str] = None
    name_ar: Optional[str] = None
    equipment_type: Optional[EquipmentType] = None
    status: Optional[EquipmentStatus] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year: Optional[int] = None
    field_id: Optional[str] = None
    location_name: Optional[str] = None
    current_fuel_percent: Optional[float] = None
    current_hours: Optional[float] = None
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None
    metadata: Optional[dict] = None


class MaintenanceRecord(BaseModel):
    """Maintenance record"""

    record_id: str
    equipment_id: str
    maintenance_type: MaintenanceType
    description: str
    description_ar: Optional[str] = None
    performed_at: datetime
    performed_by: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None
    parts_replaced: Optional[list[str]] = None


class MaintenanceAlert(BaseModel):
    """Maintenance alert"""

    alert_id: str
    equipment_id: str
    equipment_name: str
    maintenance_type: MaintenanceType
    description: str
    description_ar: Optional[str] = None
    priority: MaintenancePriority
    due_at: Optional[datetime] = None
    due_hours: Optional[float] = None
    is_overdue: bool = False
    created_at: datetime


class Equipment(BaseModel):
    """Full equipment model"""

    equipment_id: str
    tenant_id: str
    name: str
    name_ar: Optional[str] = None
    equipment_type: EquipmentType
    status: EquipmentStatus
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year: Optional[int] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[float] = None
    field_id: Optional[str] = None
    location_name: Optional[str] = None
    horsepower: Optional[int] = None
    fuel_capacity_liters: Optional[float] = None
    current_fuel_percent: Optional[float] = None
    current_hours: Optional[float] = None
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None
    last_maintenance_at: Optional[datetime] = None
    next_maintenance_at: Optional[datetime] = None
    next_maintenance_hours: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None
    qr_code: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════
# In-Memory Storage (Replace with PostgreSQL in production)
# ═══════════════════════════════════════════════════════════════════════════

# TODO: MIGRATE TO POSTGRESQL
# Current: equipment_db, maintenance_db, alerts_db stored in-memory
# Issues:
#   - Equipment inventory lost on restart
#   - Maintenance history lost (no audit trail for compliance)
#   - Cannot track equipment lifecycle across deployments
#   - No geospatial queries for equipment location
# Required:
#   1. Create PostgreSQL tables:
#      a) 'equipment' table:
#         - equipment_id (UUID, PK)
#         - tenant_id (VARCHAR, indexed)
#         - name, name_ar (VARCHAR)
#         - equipment_type (VARCHAR, indexed)
#         - status (VARCHAR, indexed)
#         - brand, model, serial_number
#         - year, purchase_date
#         - horsepower, fuel_capacity_liters, current_fuel_percent
#         - current_hours (DECIMAL)
#         - field_id (VARCHAR, indexed)
#         - location_name (VARCHAR)
#         - current_location (GEOGRAPHY POINT)
#         - last_maintenance_at, next_maintenance_at (TIMESTAMP)
#         - created_at, updated_at (TIMESTAMP)
#         - metadata (JSONB)
#         - qr_code (VARCHAR, unique)
#      b) 'equipment_maintenance' table:
#         - record_id (UUID, PK)
#         - equipment_id (UUID, FK, indexed)
#         - maintenance_type (VARCHAR)
#         - description (TEXT)
#         - performed_by (VARCHAR)
#         - performed_at (TIMESTAMP, indexed)
#         - cost (DECIMAL)
#         - parts_replaced (JSONB)
#         - next_due_at (TIMESTAMP)
#         - photos (VARCHAR[])
#      c) 'equipment_alerts' table:
#         - alert_id (UUID, PK)
#         - equipment_id (UUID, FK, indexed)
#         - maintenance_type (VARCHAR)
#         - priority (VARCHAR)
#         - due_at (TIMESTAMP, indexed)
#         - is_overdue (BOOLEAN, indexed)
#         - acknowledged_at (TIMESTAMP)
#   2. Create Tortoise ORM models: Equipment, MaintenanceRecord, MaintenanceAlert
#   3. Create repository: EquipmentRepository
#   4. Add indexes: (tenant_id, status), (equipment_type), (field_id)
#   5. Add geospatial index for equipment location tracking
# Migration Priority: HIGH - Equipment tracking is critical for asset management
equipment_db: dict[str, Equipment] = {}
maintenance_db: dict[str, MaintenanceRecord] = {}
alerts_db: dict[str, MaintenanceAlert] = {}


def seed_demo_data():
    """Seed demo equipment for testing"""
    now = datetime.utcnow()

    demo_equipment = [
        Equipment(
            equipment_id="eq_001",
            tenant_id="tenant_demo",
            name="John Deere 8R 410",
            name_ar="جون ديري 8R 410",
            equipment_type=EquipmentType.TRACTOR,
            status=EquipmentStatus.OPERATIONAL,
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
        Equipment(
            equipment_id="eq_002",
            tenant_id="tenant_demo",
            name="DJI Agras T40",
            name_ar="درون دي جي آي أجراس T40",
            equipment_type=EquipmentType.DRONE,
            status=EquipmentStatus.MAINTENANCE,
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
        Equipment(
            equipment_id="eq_003",
            tenant_id="tenant_demo",
            name="Grundfos Submersible Pump",
            name_ar="مضخة غاطسة جروندفوس",
            equipment_type=EquipmentType.PUMP,
            status=EquipmentStatus.OPERATIONAL,
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
        Equipment(
            equipment_id="eq_004",
            tenant_id="tenant_demo",
            name="New Holland CR9.90",
            name_ar="حاصدة نيو هولاند",
            equipment_type=EquipmentType.HARVESTER,
            status=EquipmentStatus.INACTIVE,
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
        Equipment(
            equipment_id="eq_005",
            tenant_id="tenant_demo",
            name="Valley Center Pivot",
            name_ar="رشاش محوري فالي",
            equipment_type=EquipmentType.PIVOT,
            status=EquipmentStatus.OPERATIONAL,
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
        equipment_db[eq.equipment_id] = eq

    # Demo maintenance alerts
    demo_alerts = [
        MaintenanceAlert(
            alert_id="alert_001",
            equipment_id="eq_001",
            equipment_name="John Deere 8R",
            maintenance_type=MaintenanceType.OIL_CHANGE,
            description="Engine oil change required",
            description_ar="تغيير زيت المحرك مطلوب",
            priority=MaintenancePriority.MEDIUM,
            due_hours=1300,
            is_overdue=False,
            created_at=now - timedelta(days=5),
        ),
        MaintenanceAlert(
            alert_id="alert_002",
            equipment_id="eq_002",
            equipment_name="DJI Agras T40",
            maintenance_type=MaintenanceType.BATTERY_CHECK,
            description="Battery inspection overdue",
            description_ar="فحص البطارية متأخر",
            priority=MaintenancePriority.HIGH,
            due_at=now - timedelta(days=2),
            is_overdue=True,
            created_at=now - timedelta(days=10),
        ),
    ]

    for alert in demo_alerts:
        alerts_db[alert.alert_id] = alert


# Seed on startup
seed_demo_data()


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


def get_tenant_id(x_tenant_id: str = "tenant_demo") -> str:
    """Extract tenant ID from header (simplified)"""
    return x_tenant_id


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/api/v1/equipment", response_model=dict)
async def list_equipment(
    equipment_type: Optional[EquipmentType] = Query(None, description="Filter by type"),
    status: Optional[EquipmentStatus] = Query(None, description="Filter by status"),
    field_id: Optional[str] = Query(None, description="Filter by field"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """List all equipment with optional filters"""
    filtered = [e for e in equipment_db.values() if e.tenant_id == tenant_id]

    if equipment_type:
        filtered = [e for e in filtered if e.equipment_type == equipment_type]
    if status:
        filtered = [e for e in filtered if e.status == status]
    if field_id:
        filtered = [e for e in filtered if e.field_id == field_id]

    # Sort by name
    filtered.sort(key=lambda e: e.name)

    total = len(filtered)
    paginated = filtered[offset : offset + limit]

    return {
        "equipment": [e.model_dump() for e in paginated],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/equipment/stats", response_model=dict)
async def get_equipment_stats(
    tenant_id: str = Depends(get_tenant_id),
):
    """Get equipment statistics"""
    tenant_equipment = [e for e in equipment_db.values() if e.tenant_id == tenant_id]

    by_type = {}
    for eq in tenant_equipment:
        by_type[eq.equipment_type.value] = by_type.get(eq.equipment_type.value, 0) + 1

    by_status = {}
    for eq in tenant_equipment:
        by_status[eq.status.value] = by_status.get(eq.status.value, 0) + 1

    return {
        "total": len(tenant_equipment),
        "by_type": by_type,
        "by_status": by_status,
        "operational": by_status.get("operational", 0),
        "maintenance": by_status.get("maintenance", 0) + by_status.get("repair", 0),
        "inactive": by_status.get("inactive", 0),
    }


@app.get("/api/v1/equipment/alerts", response_model=dict)
async def get_maintenance_alerts(
    priority: Optional[MaintenancePriority] = Query(None),
    overdue_only: bool = Query(False),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get maintenance alerts"""
    # Get equipment IDs for this tenant
    tenant_eq_ids = {
        e.equipment_id for e in equipment_db.values() if e.tenant_id == tenant_id
    }

    alerts = [a for a in alerts_db.values() if a.equipment_id in tenant_eq_ids]

    if priority:
        alerts = [a for a in alerts if a.priority == priority]
    if overdue_only:
        alerts = [a for a in alerts if a.is_overdue]

    # Sort by priority (critical first), then overdue
    priority_order = {
        MaintenancePriority.CRITICAL: 0,
        MaintenancePriority.HIGH: 1,
        MaintenancePriority.MEDIUM: 2,
        MaintenancePriority.LOW: 3,
    }
    alerts.sort(key=lambda a: (not a.is_overdue, priority_order.get(a.priority, 99)))

    return {
        "alerts": [a.model_dump() for a in alerts],
        "count": len(alerts),
        "overdue_count": len([a for a in alerts if a.is_overdue]),
    }


@app.get("/api/v1/equipment/{equipment_id}", response_model=Equipment)
async def get_equipment(
    equipment_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get equipment by ID"""
    eq = equipment_db.get(equipment_id)
    if not eq or eq.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return eq


@app.get("/api/v1/equipment/qr/{qr_code}", response_model=Equipment)
async def get_equipment_by_qr(
    qr_code: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get equipment by QR code"""
    for eq in equipment_db.values():
        if eq.qr_code == qr_code and eq.tenant_id == tenant_id:
            return eq
    raise HTTPException(status_code=404, detail="Equipment not found")


@app.post("/api/v1/equipment", response_model=Equipment, status_code=201)
async def create_equipment(
    data: EquipmentCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Create new equipment"""
    now = datetime.utcnow()
    equipment_id = f"eq_{uuid.uuid4().hex[:8]}"
    qr_code = f"QR_{equipment_id.upper()}_{data.name[:10].replace(' ', '')}"

    eq = Equipment(
        equipment_id=equipment_id,
        tenant_id=tenant_id,
        name=data.name,
        name_ar=data.name_ar,
        equipment_type=data.equipment_type,
        status=EquipmentStatus.OPERATIONAL,
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
        metadata=data.metadata,
        qr_code=qr_code,
    )

    equipment_db[equipment_id] = eq
    return eq


@app.put("/api/v1/equipment/{equipment_id}", response_model=Equipment)
async def update_equipment(
    equipment_id: str,
    data: EquipmentUpdate,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update equipment"""
    eq = equipment_db.get(equipment_id)
    if not eq or eq.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(eq, field, value)

    eq.updated_at = datetime.utcnow()
    equipment_db[equipment_id] = eq
    return eq


@app.post("/api/v1/equipment/{equipment_id}/status", response_model=Equipment)
async def update_equipment_status(
    equipment_id: str,
    status: EquipmentStatus,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update equipment status"""
    eq = equipment_db.get(equipment_id)
    if not eq or eq.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")

    eq.status = status
    eq.updated_at = datetime.utcnow()
    equipment_db[equipment_id] = eq
    return eq


@app.post("/api/v1/equipment/{equipment_id}/location", response_model=Equipment)
async def update_equipment_location(
    equipment_id: str,
    lat: float = Query(...),
    lon: float = Query(...),
    location_name: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update equipment GPS location"""
    eq = equipment_db.get(equipment_id)
    if not eq or eq.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")

    eq.current_lat = lat
    eq.current_lon = lon
    if location_name:
        eq.location_name = location_name
    eq.updated_at = datetime.utcnow()
    equipment_db[equipment_id] = eq
    return eq


@app.post("/api/v1/equipment/{equipment_id}/telemetry", response_model=Equipment)
async def update_equipment_telemetry(
    equipment_id: str,
    fuel_percent: Optional[float] = None,
    hours: Optional[float] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update equipment telemetry data (fuel, hours, location)"""
    eq = equipment_db.get(equipment_id)
    if not eq or eq.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")

    if fuel_percent is not None:
        eq.current_fuel_percent = fuel_percent
    if hours is not None:
        eq.current_hours = hours
    if lat is not None:
        eq.current_lat = lat
    if lon is not None:
        eq.current_lon = lon

    eq.updated_at = datetime.utcnow()
    equipment_db[equipment_id] = eq
    return eq


@app.get("/api/v1/equipment/{equipment_id}/maintenance", response_model=dict)
async def get_maintenance_history(
    equipment_id: str,
    limit: int = Query(20, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get maintenance history for equipment"""
    eq = equipment_db.get(equipment_id)
    if not eq or eq.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")

    records = [r for r in maintenance_db.values() if r.equipment_id == equipment_id]
    records.sort(key=lambda r: r.performed_at, reverse=True)

    return {
        "equipment_id": equipment_id,
        "records": [r.model_dump() for r in records[:limit]],
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
    description_ar: Optional[str] = None,
    performed_by: Optional[str] = None,
    cost: Optional[float] = None,
    notes: Optional[str] = None,
    parts_replaced: Optional[list[str]] = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Add a maintenance record"""
    eq = equipment_db.get(equipment_id)
    if not eq or eq.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")

    now = datetime.utcnow()
    record = MaintenanceRecord(
        record_id=f"maint_{uuid.uuid4().hex[:8]}",
        equipment_id=equipment_id,
        maintenance_type=maintenance_type,
        description=description,
        description_ar=description_ar,
        performed_at=now,
        performed_by=performed_by,
        cost=cost,
        notes=notes,
        parts_replaced=parts_replaced,
    )

    maintenance_db[record.record_id] = record

    # Update equipment
    eq.last_maintenance_at = now
    eq.updated_at = now
    equipment_db[equipment_id] = eq

    return record


@app.delete("/api/v1/equipment/{equipment_id}", status_code=204)
async def delete_equipment(
    equipment_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Delete equipment"""
    eq = equipment_db.get(equipment_id)
    if not eq or eq.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Equipment not found")

    del equipment_db[equipment_id]


# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
