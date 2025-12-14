"""
SAHOOL Equipment Service - Farm Equipment Management
=====================================================
Layer: Execution Services (Layer 4)
Purpose: Equipment tracking, maintenance scheduling, IoT device integration
"""

import os
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Tuple
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Integer, Float, Date, select, update, func, and_, or_
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog
import enum

# Shared imports
import sys
sys.path.insert(0, '/app/shared')
from database import Database, BaseModel as DBBaseModel  # noqa: E402
from events.base_event import EventBus  # noqa: E402
from utils.logging import setup_logging  # noqa: E402


# ============================================================================
# Configuration
# ============================================================================

class Settings:
    """Equipment service configuration"""
    SERVICE_NAME = "equipment-service"
    SERVICE_PORT = int(os.getenv("EQUIPMENT_SERVICE_PORT", "8089"))
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_equipment")
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
    
    # Maintenance check interval (hours)
    MAINTENANCE_CHECK_INTERVAL = int(os.getenv("MAINTENANCE_CHECK_INTERVAL", "6"))

settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

equipment_operations = Counter('equipment_operations_total', 'Equipment operations', ['operation', 'status'])
maintenance_alerts = Counter('maintenance_alerts_total', 'Maintenance alerts generated')

# ============================================================================
# Database Models
# ============================================================================

class EquipmentType(str, enum.Enum):
    TRACTOR = "tractor"
    HARVESTER = "harvester"
    SPRAYER = "sprayer"
    IRRIGATOR = "irrigator"
    SEEDER = "seeder"
    PLOW = "plow"
    PUMP = "pump"
    SENSOR_STATION = "sensor_station"
    DRONE = "drone"
    VEHICLE = "vehicle"
    TOOL = "tool"
    OTHER = "other"

class EquipmentStatus(str, enum.Enum):
    OPERATIONAL = "operational"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    OUT_OF_SERVICE = "out_of_service"
    RETIRED = "retired"

class MaintenanceType(str, enum.Enum):
    SCHEDULED = "scheduled"
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"

class MaintenanceStatus(str, enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Equipment(DBBaseModel):
    """Equipment model"""
    __tablename__ = "equipment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    code = Column(String(50), nullable=True)  # Internal asset code
    equipment_type = Column(String(50), nullable=False)
    
    # Details
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    year_manufactured = Column(Integer, nullable=True)
    
    # Purchase Info
    purchase_date = Column(Date, nullable=True)
    purchase_price = Column(Float, nullable=True)
    purchase_currency = Column(String(10), default="YER")
    supplier = Column(String(255), nullable=True)
    warranty_expiry = Column(Date, nullable=True)
    
    # Technical Specs
    specifications = Column(JSON, default={})  # {engine_power, fuel_type, capacity, etc.}
    
    # Status
    status = Column(String(50), default=EquipmentStatus.OPERATIONAL.value)
    current_field_id = Column(UUID(as_uuid=True), nullable=True)
    current_operator_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Location (for GPS-enabled equipment)
    last_known_latitude = Column(Float, nullable=True)
    last_known_longitude = Column(Float, nullable=True)
    last_location_update = Column(DateTime, nullable=True)
    
    # Usage Tracking
    total_operating_hours = Column(Float, default=0.0)
    total_fuel_consumed = Column(Float, default=0.0)  # Liters
    total_distance_km = Column(Float, default=0.0)
    
    # Maintenance Schedule
    maintenance_interval_hours = Column(Float, nullable=True)  # Hours between maintenance
    maintenance_interval_days = Column(Integer, nullable=True)  # Days between maintenance
    last_maintenance_date = Column(Date, nullable=True)
    last_maintenance_hours = Column(Float, nullable=True)
    next_maintenance_due = Column(Date, nullable=True)
    
    # IoT Integration
    iot_device_id = Column(String(100), nullable=True)
    iot_enabled = Column(Boolean, default=False)
    
    # Documents & Images
    documents = Column(JSON, default=[])  # [{name, url, type, date}]
    images = Column(JSON, default=[])
    
    # Additional
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[])
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    maintenance_records = relationship("MaintenanceRecord", back_populates="equipment", cascade="all, delete-orphan")
    usage_logs = relationship("EquipmentUsageLog", back_populates="equipment", cascade="all, delete-orphan")

class MaintenanceRecord(DBBaseModel):
    """Maintenance records"""
    __tablename__ = "maintenance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Maintenance Info
    maintenance_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    title_ar = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_date = Column(Date, nullable=True)
    due_at_hours = Column(Float, nullable=True)  # At what operating hours
    
    # Execution
    status = Column(String(50), default=MaintenanceStatus.PENDING.value)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Work Details
    work_performed = Column(Text, nullable=True)
    parts_replaced = Column(JSON, default=[])  # [{part_name, part_number, quantity, cost}]
    
    # Costs
    labor_cost = Column(Float, default=0.0)
    parts_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    currency = Column(String(10), default="YER")
    
    # Personnel
    technician_name = Column(String(255), nullable=True)
    technician_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Equipment State
    hours_at_maintenance = Column(Float, nullable=True)
    
    # Documents
    attachments = Column(JSON, default=[])
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_records")

class EquipmentUsageLog(DBBaseModel):
    """Equipment usage tracking"""
    __tablename__ = "equipment_usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment.id', ondelete='CASCADE'), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Usage Session
    session_start = Column(DateTime, nullable=False)
    session_end = Column(DateTime, nullable=True)
    
    # Operation Details
    operator_id = Column(UUID(as_uuid=True), nullable=True)
    operator_name = Column(String(255), nullable=True)
    field_id = Column(UUID(as_uuid=True), nullable=True)
    field_name = Column(String(255), nullable=True)
    task_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Activity
    activity_type = Column(String(100), nullable=True)  # plowing, spraying, harvesting, etc.
    description = Column(Text, nullable=True)
    
    # Metrics
    operating_hours = Column(Float, default=0.0)
    fuel_consumed = Column(Float, default=0.0)
    distance_km = Column(Float, default=0.0)
    area_covered_hectares = Column(Float, default=0.0)
    
    # Location Track
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)
    end_latitude = Column(Float, nullable=True)
    end_longitude = Column(Float, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="usage_logs")

class EquipmentAssignment(DBBaseModel):
    """Equipment-Field assignments"""
    __tablename__ = "equipment_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    field_id = Column(UUID(as_uuid=True), nullable=False)
    field_name = Column(String(255), nullable=True)
    
    # Assignment Period
    assigned_from = Column(DateTime, default=datetime.utcnow)
    assigned_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Assignment Details
    purpose = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    assigned_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# Pydantic Schemas
# ============================================================================

class EquipmentCreate(BaseModel):
    """Create equipment request"""
    tenant_id: uuid.UUID
    name: str = Field(..., min_length=2, max_length=255)
    name_ar: Optional[str] = None
    code: Optional[str] = None
    equipment_type: str
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year_manufactured: Optional[int] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    supplier: Optional[str] = None
    warranty_expiry: Optional[date] = None
    specifications: Optional[Dict[str, Any]] = {}
    maintenance_interval_hours: Optional[float] = None
    maintenance_interval_days: Optional[int] = None
    iot_device_id: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = []

class EquipmentUpdate(BaseModel):
    """Update equipment request"""
    name: Optional[str] = None
    name_ar: Optional[str] = None
    code: Optional[str] = None
    equipment_type: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    year_manufactured: Optional[int] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    supplier: Optional[str] = None
    warranty_expiry: Optional[date] = None
    specifications: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    maintenance_interval_hours: Optional[float] = None
    maintenance_interval_days: Optional[int] = None
    iot_device_id: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class EquipmentResponse(BaseModel):
    """Equipment response"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    name_ar: Optional[str]
    code: Optional[str]
    equipment_type: str
    brand: Optional[str]
    model: Optional[str]
    serial_number: Optional[str]
    year_manufactured: Optional[int]
    purchase_date: Optional[date]
    purchase_price: Optional[float]
    supplier: Optional[str]
    warranty_expiry: Optional[date]
    specifications: Dict[str, Any]
    status: str
    current_field_id: Optional[uuid.UUID]
    current_operator_id: Optional[uuid.UUID]
    last_known_latitude: Optional[float]
    last_known_longitude: Optional[float]
    last_location_update: Optional[datetime]
    total_operating_hours: float
    total_fuel_consumed: float
    total_distance_km: float
    maintenance_interval_hours: Optional[float]
    maintenance_interval_days: Optional[int]
    last_maintenance_date: Optional[date]
    next_maintenance_due: Optional[date]
    iot_enabled: bool
    iot_device_id: Optional[str]
    documents: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MaintenanceCreate(BaseModel):
    """Create maintenance record"""
    maintenance_type: str
    title: str
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    scheduled_date: Optional[date] = None
    due_at_hours: Optional[float] = None

class MaintenanceUpdate(BaseModel):
    """Update maintenance record"""
    title: Optional[str] = None
    title_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    scheduled_date: Optional[date] = None
    status: Optional[str] = None
    work_performed: Optional[str] = None
    parts_replaced: Optional[List[Dict[str, Any]]] = None
    labor_cost: Optional[float] = None
    parts_cost: Optional[float] = None
    technician_name: Optional[str] = None

class MaintenanceResponse(BaseModel):
    """Maintenance record response"""
    id: uuid.UUID
    equipment_id: uuid.UUID
    maintenance_type: str
    title: str
    title_ar: Optional[str]
    description: Optional[str]
    description_ar: Optional[str]
    scheduled_date: Optional[date]
    due_at_hours: Optional[float]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    work_performed: Optional[str]
    parts_replaced: List[Dict[str, Any]]
    labor_cost: float
    parts_cost: float
    total_cost: float
    technician_name: Optional[str]
    hours_at_maintenance: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UsageLogCreate(BaseModel):
    """Create usage log"""
    operator_id: Optional[uuid.UUID] = None
    operator_name: Optional[str] = None
    field_id: Optional[uuid.UUID] = None
    field_name: Optional[str] = None
    task_id: Optional[uuid.UUID] = None
    activity_type: Optional[str] = None
    description: Optional[str] = None
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None

class UsageLogEnd(BaseModel):
    """End usage session"""
    operating_hours: float
    fuel_consumed: Optional[float] = 0.0
    distance_km: Optional[float] = 0.0
    area_covered_hectares: Optional[float] = 0.0
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None
    notes: Optional[str] = None

class UsageLogResponse(BaseModel):
    """Usage log response"""
    id: uuid.UUID
    equipment_id: uuid.UUID
    session_start: datetime
    session_end: Optional[datetime]
    operator_name: Optional[str]
    field_name: Optional[str]
    activity_type: Optional[str]
    operating_hours: float
    fuel_consumed: float
    distance_km: float
    area_covered_hectares: float
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LocationUpdate(BaseModel):
    """Update equipment location"""
    latitude: float
    longitude: float

# ============================================================================
# Equipment Service
# ============================================================================

class EquipmentService:
    """Core equipment management service"""
    
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.scheduler = AsyncIOScheduler()
    
    async def start_scheduler(self):
        """Start maintenance check scheduler"""
        self.scheduler.add_job(
            self._check_maintenance_due,
            CronTrigger(hour=f"*/{settings.MAINTENANCE_CHECK_INTERVAL}"),
            id="maintenance_check"
        )
        self.scheduler.start()
        logger.info("Maintenance scheduler started")
    
    async def stop_scheduler(self):
        """Stop scheduler"""
        self.scheduler.shutdown()
    
    async def _check_maintenance_due(self):
        """Check for equipment needing maintenance"""
        logger.info("Running maintenance due check...")
        async with self.db.session() as session:
            # Find equipment with overdue or upcoming maintenance
            today = date.today()
            upcoming_date = today + timedelta(days=7)
            
            result = await session.execute(
                select(Equipment).where(
                    and_(
                        Equipment.status != EquipmentStatus.RETIRED.value,
                        or_(
                            Equipment.next_maintenance_due <= upcoming_date,
                            and_(
                                Equipment.maintenance_interval_hours.isnot(None),
                                Equipment.total_operating_hours >= Equipment.last_maintenance_hours + Equipment.maintenance_interval_hours - 10
                            )
                        )
                    )
                )
            )
            
            equipment_list = result.scalars().all()
            
            for equip in equipment_list:
                # Emit maintenance alert event
                await self.event_bus.publish(
                    "equipment.maintenance.due",
                    {
                        "equipment_id": str(equip.id),
                        "tenant_id": str(equip.tenant_id),
                        "equipment_name": equip.name,
                        "next_maintenance_due": equip.next_maintenance_due.isoformat() if equip.next_maintenance_due else None,
                        "current_hours": equip.total_operating_hours,
                        "maintenance_interval_hours": equip.maintenance_interval_hours
                    }
                )
                maintenance_alerts.inc()
            
            logger.info(f"Maintenance check complete. {len(equipment_list)} equipment items need attention.")
    
    async def create_equipment(self, data: EquipmentCreate) -> Equipment:
        """Create new equipment"""
        async with self.db.session() as session:
            equipment = Equipment(
                tenant_id=data.tenant_id,
                name=data.name,
                name_ar=data.name_ar,
                code=data.code,
                equipment_type=data.equipment_type,
                brand=data.brand,
                model=data.model,
                serial_number=data.serial_number,
                year_manufactured=data.year_manufactured,
                purchase_date=data.purchase_date,
                purchase_price=data.purchase_price,
                supplier=data.supplier,
                warranty_expiry=data.warranty_expiry,
                specifications=data.specifications or {},
                maintenance_interval_hours=data.maintenance_interval_hours,
                maintenance_interval_days=data.maintenance_interval_days,
                iot_device_id=data.iot_device_id,
                iot_enabled=bool(data.iot_device_id),
                notes=data.notes,
                tags=data.tags or []
            )
            
            # Calculate next maintenance due
            if data.maintenance_interval_days:
                equipment.next_maintenance_due = date.today() + timedelta(days=data.maintenance_interval_days)
            
            session.add(equipment)
            await session.commit()
            await session.refresh(equipment)
            
            # Emit event
            await self.event_bus.publish(
                "equipment.created",
                {
                    "equipment_id": str(equipment.id),
                    "tenant_id": str(equipment.tenant_id),
                    "name": equipment.name,
                    "type": equipment.equipment_type
                }
            )
            
            logger.info("Equipment created", equipment_id=str(equipment.id), name=equipment.name)
            return equipment
    
    async def get_equipment(self, equipment_id: uuid.UUID, tenant_id: Optional[uuid.UUID] = None) -> Optional[Equipment]:
        """Get equipment by ID"""
        async with self.db.session() as session:
            query = select(Equipment).where(Equipment.id == equipment_id)
            if tenant_id:
                query = query.where(Equipment.tenant_id == tenant_id)
            
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def update_equipment(self, equipment_id: uuid.UUID, tenant_id: uuid.UUID, data: EquipmentUpdate) -> Equipment:
        """Update equipment"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Equipment).where(
                    Equipment.id == equipment_id,
                    Equipment.tenant_id == tenant_id
                )
            )
            equipment = result.scalar_one_or_none()
            
            if not equipment:
                raise HTTPException(status_code=404, detail="Equipment not found")
            
            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(equipment, key, value)
            
            # Update IoT status
            if 'iot_device_id' in update_data:
                equipment.iot_enabled = bool(update_data['iot_device_id'])
            
            equipment.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(equipment)
            
            # Emit event
            await self.event_bus.publish(
                "equipment.updated",
                {
                    "equipment_id": str(equipment.id),
                    "tenant_id": str(tenant_id),
                    "updated_fields": list(update_data.keys())
                }
            )
            
            return equipment
    
    async def delete_equipment(self, equipment_id: uuid.UUID, tenant_id: uuid.UUID):
        """Delete equipment"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Equipment).where(
                    Equipment.id == equipment_id,
                    Equipment.tenant_id == tenant_id
                )
            )
            equipment = result.scalar_one_or_none()
            
            if not equipment:
                raise HTTPException(status_code=404, detail="Equipment not found")
            
            await session.delete(equipment)
            await session.commit()
            
            # Emit event
            await self.event_bus.publish(
                "equipment.deleted",
                {
                    "equipment_id": str(equipment_id),
                    "tenant_id": str(tenant_id)
                }
            )
    
    async def list_equipment(
        self,
        tenant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        equipment_type: Optional[str] = None,
        status_filter: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Equipment], int]:
        """List equipment with pagination and filters"""
        async with self.db.session() as session:
            query = select(Equipment).where(Equipment.tenant_id == tenant_id)
            count_query = select(func.count(Equipment.id)).where(Equipment.tenant_id == tenant_id)
            
            if equipment_type:
                query = query.where(Equipment.equipment_type == equipment_type)
                count_query = count_query.where(Equipment.equipment_type == equipment_type)
            
            if status_filter:
                query = query.where(Equipment.status == status_filter)
                count_query = count_query.where(Equipment.status == status_filter)
            
            if search:
                search_filter = f"%{search}%"
                query = query.where(
                    or_(
                        Equipment.name.ilike(search_filter),
                        Equipment.name_ar.ilike(search_filter),
                        Equipment.code.ilike(search_filter),
                        Equipment.serial_number.ilike(search_filter)
                    )
                )
                count_query = count_query.where(
                    or_(
                        Equipment.name.ilike(search_filter),
                        Equipment.name_ar.ilike(search_filter),
                        Equipment.code.ilike(search_filter),
                        Equipment.serial_number.ilike(search_filter)
                    )
                )
            
            # Get total count
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(Equipment.created_at.desc())
            
            result = await session.execute(query)
            equipment_list = result.scalars().all()
            
            return equipment_list, total
    
    async def update_location(self, equipment_id: uuid.UUID, tenant_id: uuid.UUID, latitude: float, longitude: float):
        """Update equipment location (from GPS/IoT)"""
        async with self.db.session() as session:
            await session.execute(
                update(Equipment)
                .where(Equipment.id == equipment_id, Equipment.tenant_id == tenant_id)
                .values(
                    last_known_latitude=latitude,
                    last_known_longitude=longitude,
                    last_location_update=datetime.utcnow()
                )
            )
            await session.commit()
            
            # Emit event for real-time tracking
            await self.event_bus.publish(
                "equipment.location.updated",
                {
                    "equipment_id": str(equipment_id),
                    "tenant_id": str(tenant_id),
                    "latitude": latitude,
                    "longitude": longitude,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    async def start_usage_session(
        self,
        equipment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        data: UsageLogCreate
    ) -> EquipmentUsageLog:
        """Start equipment usage session"""
        async with self.db.session() as session:
            # Verify equipment exists and is available
            result = await session.execute(
                select(Equipment).where(
                    Equipment.id == equipment_id,
                    Equipment.tenant_id == tenant_id
                )
            )
            equipment = result.scalar_one_or_none()
            
            if not equipment:
                raise HTTPException(status_code=404, detail="Equipment not found")
            
            if equipment.status not in [EquipmentStatus.OPERATIONAL.value]:
                raise HTTPException(status_code=400, detail=f"Equipment is {equipment.status}, cannot start usage")
            
            # Create usage log
            usage_log = EquipmentUsageLog(
                equipment_id=equipment_id,
                tenant_id=tenant_id,
                session_start=datetime.utcnow(),
                operator_id=data.operator_id,
                operator_name=data.operator_name,
                field_id=data.field_id,
                field_name=data.field_name,
                task_id=data.task_id,
                activity_type=data.activity_type,
                description=data.description,
                start_latitude=data.start_latitude,
                start_longitude=data.start_longitude
            )
            
            session.add(usage_log)
            
            # Update equipment status
            equipment.status = EquipmentStatus.IN_USE.value
            equipment.current_field_id = data.field_id
            equipment.current_operator_id = data.operator_id
            
            await session.commit()
            await session.refresh(usage_log)
            
            # Emit event
            await self.event_bus.publish(
                "equipment.usage.started",
                {
                    "equipment_id": str(equipment_id),
                    "tenant_id": str(tenant_id),
                    "usage_log_id": str(usage_log.id),
                    "field_id": str(data.field_id) if data.field_id else None,
                    "operator_id": str(data.operator_id) if data.operator_id else None
                }
            )
            
            return usage_log
    
    async def end_usage_session(
        self,
        usage_log_id: uuid.UUID,
        tenant_id: uuid.UUID,
        data: UsageLogEnd
    ) -> EquipmentUsageLog:
        """End equipment usage session"""
        async with self.db.session() as session:
            result = await session.execute(
                select(EquipmentUsageLog).where(
                    EquipmentUsageLog.id == usage_log_id,
                    EquipmentUsageLog.tenant_id == tenant_id
                )
            )
            usage_log = result.scalar_one_or_none()
            
            if not usage_log:
                raise HTTPException(status_code=404, detail="Usage log not found")
            
            if usage_log.session_end:
                raise HTTPException(status_code=400, detail="Session already ended")
            
            # Update usage log
            usage_log.session_end = datetime.utcnow()
            usage_log.operating_hours = data.operating_hours
            usage_log.fuel_consumed = data.fuel_consumed or 0.0
            usage_log.distance_km = data.distance_km or 0.0
            usage_log.area_covered_hectares = data.area_covered_hectares or 0.0
            usage_log.end_latitude = data.end_latitude
            usage_log.end_longitude = data.end_longitude
            usage_log.notes = data.notes
            
            # Update equipment totals
            result = await session.execute(
                select(Equipment).where(Equipment.id == usage_log.equipment_id)
            )
            equipment = result.scalar_one_or_none()
            
            if equipment:
                equipment.total_operating_hours += data.operating_hours
                equipment.total_fuel_consumed += data.fuel_consumed or 0.0
                equipment.total_distance_km += data.distance_km or 0.0
                equipment.status = EquipmentStatus.OPERATIONAL.value
                equipment.current_field_id = None
                equipment.current_operator_id = None
                
                if data.end_latitude and data.end_longitude:
                    equipment.last_known_latitude = data.end_latitude
                    equipment.last_known_longitude = data.end_longitude
                    equipment.last_location_update = datetime.utcnow()
            
            await session.commit()
            await session.refresh(usage_log)
            
            # Emit event
            await self.event_bus.publish(
                "equipment.usage.ended",
                {
                    "equipment_id": str(usage_log.equipment_id),
                    "tenant_id": str(tenant_id),
                    "usage_log_id": str(usage_log_id),
                    "operating_hours": data.operating_hours,
                    "fuel_consumed": data.fuel_consumed,
                    "area_covered": data.area_covered_hectares
                }
            )
            
            return usage_log
    
    async def create_maintenance(
        self,
        equipment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        data: MaintenanceCreate,
        created_by: Optional[uuid.UUID] = None
    ) -> MaintenanceRecord:
        """Create maintenance record"""
        async with self.db.session() as session:
            # Verify equipment exists
            result = await session.execute(
                select(Equipment).where(
                    Equipment.id == equipment_id,
                    Equipment.tenant_id == tenant_id
                )
            )
            equipment = result.scalar_one_or_none()
            
            if not equipment:
                raise HTTPException(status_code=404, detail="Equipment not found")
            
            maintenance = MaintenanceRecord(
                equipment_id=equipment_id,
                tenant_id=tenant_id,
                maintenance_type=data.maintenance_type,
                title=data.title,
                title_ar=data.title_ar,
                description=data.description,
                description_ar=data.description_ar,
                scheduled_date=data.scheduled_date,
                due_at_hours=data.due_at_hours,
                hours_at_maintenance=equipment.total_operating_hours,
                created_by=created_by
            )
            
            session.add(maintenance)
            await session.commit()
            await session.refresh(maintenance)
            
            # Emit event
            await self.event_bus.publish(
                "equipment.maintenance.created",
                {
                    "equipment_id": str(equipment_id),
                    "tenant_id": str(tenant_id),
                    "maintenance_id": str(maintenance.id),
                    "maintenance_type": data.maintenance_type,
                    "scheduled_date": data.scheduled_date.isoformat() if data.scheduled_date else None
                }
            )
            
            return maintenance
    
    async def complete_maintenance(
        self,
        maintenance_id: uuid.UUID,
        tenant_id: uuid.UUID,
        data: MaintenanceUpdate
    ) -> MaintenanceRecord:
        """Complete maintenance record"""
        async with self.db.session() as session:
            result = await session.execute(
                select(MaintenanceRecord).where(
                    MaintenanceRecord.id == maintenance_id,
                    MaintenanceRecord.tenant_id == tenant_id
                )
            )
            maintenance = result.scalar_one_or_none()
            
            if not maintenance:
                raise HTTPException(status_code=404, detail="Maintenance record not found")
            
            # Update maintenance record
            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(maintenance, key):
                    setattr(maintenance, key, value)
            
            # Calculate total cost
            maintenance.total_cost = (maintenance.labor_cost or 0) + (maintenance.parts_cost or 0)
            
            if data.status == MaintenanceStatus.COMPLETED.value:
                maintenance.completed_at = datetime.utcnow()
                
                # Update equipment maintenance tracking
                result = await session.execute(
                    select(Equipment).where(Equipment.id == maintenance.equipment_id)
                )
                equipment = result.scalar_one_or_none()
                
                if equipment:
                    equipment.last_maintenance_date = date.today()
                    equipment.last_maintenance_hours = equipment.total_operating_hours
                    
                    # Calculate next maintenance due
                    if equipment.maintenance_interval_days:
                        equipment.next_maintenance_due = date.today() + timedelta(days=equipment.maintenance_interval_days)
                    
                    # Reset status if was in maintenance
                    if equipment.status == EquipmentStatus.MAINTENANCE.value:
                        equipment.status = EquipmentStatus.OPERATIONAL.value
            
            maintenance.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(maintenance)
            
            # Emit event
            await self.event_bus.publish(
                "equipment.maintenance.completed",
                {
                    "equipment_id": str(maintenance.equipment_id),
                    "tenant_id": str(tenant_id),
                    "maintenance_id": str(maintenance_id),
                    "total_cost": maintenance.total_cost
                }
            )
            
            return maintenance
    
    async def get_maintenance_history(
        self,
        equipment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        limit: int = 50
    ) -> List[MaintenanceRecord]:
        """Get equipment maintenance history"""
        async with self.db.session() as session:
            result = await session.execute(
                select(MaintenanceRecord)
                .where(
                    MaintenanceRecord.equipment_id == equipment_id,
                    MaintenanceRecord.tenant_id == tenant_id
                )
                .order_by(MaintenanceRecord.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_usage_history(
        self,
        equipment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        limit: int = 50
    ) -> List[EquipmentUsageLog]:
        """Get equipment usage history"""
        async with self.db.session() as session:
            result = await session.execute(
                select(EquipmentUsageLog)
                .where(
                    EquipmentUsageLog.equipment_id == equipment_id,
                    EquipmentUsageLog.tenant_id == tenant_id
                )
                .order_by(EquipmentUsageLog.session_start.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_tenant_stats(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Get tenant equipment statistics"""
        async with self.db.session() as session:
            result = await session.execute(
                select(
                    func.count(Equipment.id).label('total_equipment'),
                    func.count(Equipment.id).filter(Equipment.status == 'operational').label('operational'),
                    func.count(Equipment.id).filter(Equipment.status == 'in_use').label('in_use'),
                    func.count(Equipment.id).filter(Equipment.status == 'maintenance').label('in_maintenance'),
                    func.sum(Equipment.total_operating_hours).label('total_hours'),
                    func.sum(Equipment.total_fuel_consumed).label('total_fuel')
                ).where(Equipment.tenant_id == tenant_id)
            )
            row = result.fetchone()
            
            # Get equipment by type
            type_result = await session.execute(
                select(
                    Equipment.equipment_type,
                    func.count(Equipment.id)
                ).where(Equipment.tenant_id == tenant_id)
                .group_by(Equipment.equipment_type)
            )
            type_counts = {r[0]: r[1] for r in type_result.fetchall()}
            
            # Get equipment needing maintenance
            upcoming_maintenance = await session.execute(
                select(func.count(Equipment.id)).where(
                    Equipment.tenant_id == tenant_id,
                    Equipment.next_maintenance_due <= date.today() + timedelta(days=7)
                )
            )
            maintenance_due = upcoming_maintenance.scalar()
            
            return {
                "total_equipment": row.total_equipment or 0,
                "operational": row.operational or 0,
                "in_use": row.in_use or 0,
                "in_maintenance": row.in_maintenance or 0,
                "total_operating_hours": row.total_hours or 0,
                "total_fuel_consumed": row.total_fuel or 0,
                "equipment_by_type": type_counts,
                "maintenance_due_count": maintenance_due or 0
            }

# ============================================================================
# Event Handlers
# ============================================================================

async def handle_task_assigned(event: Dict[str, Any], service: EquipmentService):
    """Handle task assignment - may need equipment"""
    # This could auto-assign equipment if specified in task

# ============================================================================
# Dependencies
# ============================================================================

db: Database = None
event_bus: EventBus = None
equipment_service: EquipmentService = None

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, event_bus, equipment_service
    
    logger.info("Starting Equipment Service...")
    
    db = Database(settings.DATABASE_URL)
    await db.connect()
    
    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()
    
    equipment_service = EquipmentService(db, event_bus)
    await equipment_service.start_scheduler()
    
    logger.info("Equipment Service started successfully")
    
    yield
    
    logger.info("Shutting down Equipment Service...")
    await equipment_service.stop_scheduler()
    await event_bus.close()
    await db.disconnect()

app = FastAPI(
    title="SAHOOL Equipment Service",
    description="Farm Equipment Management Service",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Equipment CRUD
@app.post("/api/v1/equipment", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(data: EquipmentCreate):
    """Create new equipment"""
    equipment = await equipment_service.create_equipment(data)
    equipment_operations.labels(operation="create", status="success").inc()
    return equipment

@app.get("/api/v1/equipment/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment(equipment_id: uuid.UUID, tenant_id: uuid.UUID = Query(...)):
    """Get equipment by ID"""
    equipment = await equipment_service.get_equipment(equipment_id, tenant_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment

@app.patch("/api/v1/equipment/{equipment_id}", response_model=EquipmentResponse)
async def update_equipment(equipment_id: uuid.UUID, tenant_id: uuid.UUID, data: EquipmentUpdate):
    """Update equipment"""
    equipment = await equipment_service.update_equipment(equipment_id, tenant_id, data)
    equipment_operations.labels(operation="update", status="success").inc()
    return equipment

@app.delete("/api/v1/equipment/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(equipment_id: uuid.UUID, tenant_id: uuid.UUID):
    """Delete equipment"""
    await equipment_service.delete_equipment(equipment_id, tenant_id)
    equipment_operations.labels(operation="delete", status="success").inc()

@app.get("/api/v1/equipment")
async def list_equipment(
    tenant_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    equipment_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None
):
    """List equipment with pagination and filters"""
    equipment_list, total = await equipment_service.list_equipment(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        equipment_type=equipment_type,
        status_filter=status_filter,
        search=search
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": equipment_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

# Location
@app.post("/api/v1/equipment/{equipment_id}/location", status_code=status.HTTP_204_NO_CONTENT)
async def update_location(equipment_id: uuid.UUID, tenant_id: uuid.UUID, data: LocationUpdate):
    """Update equipment location (from GPS/IoT)"""
    await equipment_service.update_location(equipment_id, tenant_id, data.latitude, data.longitude)

# Usage Sessions
@app.post("/api/v1/equipment/{equipment_id}/usage/start", response_model=UsageLogResponse)
async def start_usage(equipment_id: uuid.UUID, tenant_id: uuid.UUID, data: UsageLogCreate):
    """Start equipment usage session"""
    return await equipment_service.start_usage_session(equipment_id, tenant_id, data)

@app.post("/api/v1/equipment/usage/{usage_log_id}/end", response_model=UsageLogResponse)
async def end_usage(usage_log_id: uuid.UUID, tenant_id: uuid.UUID, data: UsageLogEnd):
    """End equipment usage session"""
    return await equipment_service.end_usage_session(usage_log_id, tenant_id, data)

@app.get("/api/v1/equipment/{equipment_id}/usage", response_model=List[UsageLogResponse])
async def get_usage_history(
    equipment_id: uuid.UUID,
    tenant_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200)
):
    """Get equipment usage history"""
    return await equipment_service.get_usage_history(equipment_id, tenant_id, limit)

# Maintenance
@app.post("/api/v1/equipment/{equipment_id}/maintenance", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance(
    equipment_id: uuid.UUID,
    tenant_id: uuid.UUID,
    data: MaintenanceCreate,
    created_by: Optional[uuid.UUID] = None
):
    """Create maintenance record"""
    return await equipment_service.create_maintenance(equipment_id, tenant_id, data, created_by)

@app.patch("/api/v1/equipment/maintenance/{maintenance_id}", response_model=MaintenanceResponse)
async def update_maintenance(maintenance_id: uuid.UUID, tenant_id: uuid.UUID, data: MaintenanceUpdate):
    """Update/complete maintenance record"""
    return await equipment_service.complete_maintenance(maintenance_id, tenant_id, data)

@app.get("/api/v1/equipment/{equipment_id}/maintenance", response_model=List[MaintenanceResponse])
async def get_maintenance_history(
    equipment_id: uuid.UUID,
    tenant_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200)
):
    """Get equipment maintenance history"""
    return await equipment_service.get_maintenance_history(equipment_id, tenant_id, limit)

# Statistics
@app.get("/api/v1/tenants/{tenant_id}/equipment-stats")
async def get_equipment_stats(tenant_id: uuid.UUID):
    """Get tenant equipment statistics"""
    return await equipment_service.get_tenant_stats(tenant_id)

# Equipment Types (static)
@app.get("/api/v1/equipment-types")
async def get_equipment_types():
    """Get available equipment types"""
    return {
        "types": [
            {"code": "tractor", "name_en": "Tractor", "name_ar": "جرار"},
            {"code": "harvester", "name_en": "Harvester", "name_ar": "حصادة"},
            {"code": "sprayer", "name_en": "Sprayer", "name_ar": "رشاش"},
            {"code": "irrigator", "name_en": "Irrigator", "name_ar": "نظام ري"},
            {"code": "seeder", "name_en": "Seeder", "name_ar": "بذارة"},
            {"code": "plow", "name_en": "Plow", "name_ar": "محراث"},
            {"code": "pump", "name_en": "Pump", "name_ar": "مضخة"},
            {"code": "sensor_station", "name_en": "Sensor Station", "name_ar": "محطة استشعار"},
            {"code": "drone", "name_en": "Drone", "name_ar": "طائرة بدون طيار"},
            {"code": "vehicle", "name_en": "Vehicle", "name_ar": "مركبة"},
            {"code": "tool", "name_en": "Tool", "name_ar": "أداة"},
            {"code": "other", "name_en": "Other", "name_ar": "أخرى"}
        ]
    }

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
