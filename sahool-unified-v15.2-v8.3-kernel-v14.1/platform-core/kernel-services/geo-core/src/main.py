"""
SAHOOL Geo-Core Service - Geographic Field Management
======================================================
Layer: Platform Core (Layer 1)
Purpose: Field management, geographic boundaries, PostGIS integration, spatial queries
"""

import os
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Float, Date, select, func
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry import shape, mapping, Point, Polygon
from shapely.ops import transform
import pyproj
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
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
    """Geo-Core service configuration"""
    SERVICE_NAME = "geo-core-service"
    SERVICE_PORT = int(os.getenv("GEO_SERVICE_PORT", "8085"))
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_geo")
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
    
    # Default SRID for Yemen
    DEFAULT_SRID = 4326  # WGS84
    YEMEN_BBOX = {
        "min_lat": 12.0,
        "max_lat": 19.0,
        "min_lon": 42.0,
        "max_lon": 55.0
    }

settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

geo_operations = Counter('geo_operations_total', 'Geo operations', ['operation', 'status'])
area_calculations = Histogram('area_calculation_seconds', 'Area calculation latency')

# ============================================================================
# Database Models
# ============================================================================

class FieldStatus(str, enum.Enum):
    ACTIVE = "active"
    FALLOW = "fallow"
    PREPARING = "preparing"
    HARVESTED = "harvested"
    INACTIVE = "inactive"

class SoilType(str, enum.Enum):
    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    SILT = "silt"
    PEAT = "peat"
    CHALKY = "chalky"
    MIXED = "mixed"

class IrrigationType(str, enum.Enum):
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    FLOOD = "flood"
    FURROW = "furrow"
    SUBSURFACE = "subsurface"
    RAINFED = "rainfed"
    MANUAL = "manual"

class Field(DBBaseModel):
    """Field model with geographic data"""
    __tablename__ = "fields"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    code = Column(String(50), nullable=True)  # Internal reference code
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    
    # Geographic Data (PostGIS)
    boundary = Column(Geometry('POLYGON', srid=4326), nullable=False)
    centroid = Column(Geometry('POINT', srid=4326), nullable=True)
    
    # Calculated Area
    area_hectares = Column(Float, nullable=False)
    area_sqm = Column(Float, nullable=False)
    perimeter_meters = Column(Float, nullable=True)
    
    # Location Reference
    region = Column(String(100), nullable=True)
    governorate = Column(String(100), nullable=True)  # المحافظة
    district = Column(String(100), nullable=True)     # المديرية
    village = Column(String(100), nullable=True)      # القرية
    
    # Elevation & Terrain
    elevation_min = Column(Float, nullable=True)  # meters
    elevation_max = Column(Float, nullable=True)
    elevation_avg = Column(Float, nullable=True)
    slope_percent = Column(Float, nullable=True)
    aspect = Column(String(20), nullable=True)  # N, NE, E, SE, S, SW, W, NW
    
    # Soil Characteristics
    soil_type = Column(String(50), default=SoilType.MIXED.value)
    soil_ph = Column(Float, nullable=True)
    soil_organic_matter = Column(Float, nullable=True)  # percentage
    soil_texture = Column(String(100), nullable=True)
    
    # Water & Irrigation
    irrigation_type = Column(String(50), default=IrrigationType.MANUAL.value)
    water_source = Column(String(100), nullable=True)  # well, canal, rain, etc.
    water_availability = Column(String(20), nullable=True)  # abundant, moderate, scarce
    
    # Current Status
    status = Column(String(20), default=FieldStatus.ACTIVE.value)
    current_crop_id = Column(UUID(as_uuid=True), nullable=True)
    current_crop_name = Column(String(100), nullable=True)
    planting_date = Column(Date, nullable=True)
    expected_harvest_date = Column(Date, nullable=True)
    
    # Historical Data
    crop_history = Column(JSON, default=[])  # [{crop, year, yield, notes}]
    
    # Settings & Metadata
    settings = Column(JSON, default={})
    tags = Column(ARRAY(String), default=[])
    
    # Ownership
    owner_user_id = Column(UUID(as_uuid=True), nullable=True)
    manager_user_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    zones = relationship("FieldZone", back_populates="field", cascade="all, delete-orphan")
    sensors = relationship("FieldSensor", back_populates="field", cascade="all, delete-orphan")

class FieldZone(DBBaseModel):
    """Sub-zones within a field for detailed management"""
    __tablename__ = "field_zones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey('fields.id', ondelete='CASCADE'), nullable=False)
    
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=True)
    zone_type = Column(String(50), nullable=True)  # planting, buffer, road, building
    
    boundary = Column(Geometry('POLYGON', srid=4326), nullable=False)
    area_hectares = Column(Float, nullable=False)
    
    # Zone-specific attributes
    soil_type = Column(String(50), nullable=True)
    irrigation_type = Column(String(50), nullable=True)
    current_crop = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    field = relationship("Field", back_populates="zones")

class FieldSensor(DBBaseModel):
    """IoT sensors deployed in fields"""
    __tablename__ = "field_sensors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey('fields.id', ondelete='CASCADE'), nullable=False)
    
    sensor_id = Column(String(100), unique=True, nullable=False)
    sensor_type = Column(String(50), nullable=False)  # soil_moisture, temperature, weather_station
    
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    
    is_active = Column(Boolean, default=True)
    last_reading_at = Column(DateTime, nullable=True)
    battery_level = Column(Float, nullable=True)
    
    metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    field = relationship("Field", back_populates="sensors")

class FieldHistory(DBBaseModel):
    """Field change history for auditing"""
    __tablename__ = "field_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    change_type = Column(String(50), nullable=False)  # created, updated, boundary_changed, crop_changed
    changed_by = Column(UUID(as_uuid=True), nullable=True)
    
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# Pydantic Schemas
# ============================================================================

class GeoJSONPolygon(BaseModel):
    """GeoJSON Polygon schema"""
    type: str = "Polygon"
    coordinates: List[List[List[float]]]
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['Polygon', 'MultiPolygon']:
            raise ValueError('type must be Polygon or MultiPolygon')
        return v
    
    @validator('coordinates')
    def validate_coordinates(cls, v, values):
        if values.get('type') == 'Polygon':
            if len(v) < 1:
                raise ValueError('Polygon must have at least one ring')
            for ring in v:
                if len(ring) < 4:
                    raise ValueError('Ring must have at least 4 coordinates')
                if ring[0] != ring[-1]:
                    raise ValueError('Ring must be closed')
        return v

class GeoJSONPoint(BaseModel):
    """GeoJSON Point schema"""
    type: str = "Point"
    coordinates: List[float]
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if len(v) < 2:
            raise ValueError('Point must have at least 2 coordinates')
        return v

class FieldCreate(BaseModel):
    """Create field request"""
    name: str = Field(..., min_length=2, max_length=255)
    name_ar: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    
    boundary: GeoJSONPolygon
    
    region: Optional[str] = None
    governorate: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    
    elevation_avg: Optional[float] = None
    slope_percent: Optional[float] = None
    
    soil_type: str = SoilType.MIXED.value
    soil_ph: Optional[float] = None
    
    irrigation_type: str = IrrigationType.MANUAL.value
    water_source: Optional[str] = None
    
    owner_user_id: Optional[uuid.UUID] = None
    manager_user_id: Optional[uuid.UUID] = None
    tags: List[str] = []

class FieldUpdate(BaseModel):
    """Update field request"""
    name: Optional[str] = None
    name_ar: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    
    boundary: Optional[GeoJSONPolygon] = None
    
    region: Optional[str] = None
    governorate: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    
    elevation_avg: Optional[float] = None
    slope_percent: Optional[float] = None
    
    soil_type: Optional[str] = None
    soil_ph: Optional[float] = None
    soil_organic_matter: Optional[float] = None
    
    irrigation_type: Optional[str] = None
    water_source: Optional[str] = None
    water_availability: Optional[str] = None
    
    status: Optional[str] = None
    current_crop_id: Optional[uuid.UUID] = None
    current_crop_name: Optional[str] = None
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None

class FieldResponse(BaseModel):
    """Field response"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    name_ar: Optional[str]
    code: Optional[str]
    description: Optional[str]
    description_ar: Optional[str]
    
    boundary: Dict[str, Any]  # GeoJSON
    centroid: Optional[Dict[str, Any]]
    
    area_hectares: float
    area_sqm: float
    perimeter_meters: Optional[float]
    
    region: Optional[str]
    governorate: Optional[str]
    district: Optional[str]
    village: Optional[str]
    
    elevation_avg: Optional[float]
    slope_percent: Optional[float]
    
    soil_type: str
    soil_ph: Optional[float]
    soil_organic_matter: Optional[float]
    
    irrigation_type: str
    water_source: Optional[str]
    water_availability: Optional[str]
    
    status: str
    current_crop_id: Optional[uuid.UUID]
    current_crop_name: Optional[str]
    planting_date: Optional[date]
    expected_harvest_date: Optional[date]
    
    tags: List[str]
    
    owner_user_id: Optional[uuid.UUID]
    manager_user_id: Optional[uuid.UUID]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FieldListResponse(BaseModel):
    """Paginated field list"""
    items: List[FieldResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    total_area_hectares: float

class ZoneCreate(BaseModel):
    """Create zone request"""
    name: str
    name_ar: Optional[str] = None
    zone_type: Optional[str] = None
    boundary: GeoJSONPolygon
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    current_crop: Optional[str] = None

class ZoneResponse(BaseModel):
    """Zone response"""
    id: uuid.UUID
    field_id: uuid.UUID
    name: str
    name_ar: Optional[str]
    zone_type: Optional[str]
    boundary: Dict[str, Any]
    area_hectares: float
    soil_type: Optional[str]
    irrigation_type: Optional[str]
    current_crop: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SensorCreate(BaseModel):
    """Create sensor request"""
    sensor_id: str
    sensor_type: str
    location: GeoJSONPoint
    metadata: Dict[str, Any] = {}

class SensorResponse(BaseModel):
    """Sensor response"""
    id: uuid.UUID
    field_id: uuid.UUID
    sensor_id: str
    sensor_type: str
    location: Dict[str, Any]
    is_active: bool
    last_reading_at: Optional[datetime]
    battery_level: Optional[float]
    metadata: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class SpatialQueryRequest(BaseModel):
    """Spatial query request"""
    point: Optional[GeoJSONPoint] = None
    polygon: Optional[GeoJSONPolygon] = None
    buffer_meters: float = 0
    limit: int = 100

class FieldStatistics(BaseModel):
    """Field statistics"""
    total_fields: int
    total_area_hectares: float
    active_fields: int
    fallow_fields: int
    by_crop: Dict[str, int]
    by_soil_type: Dict[str, int]
    by_irrigation: Dict[str, int]
    by_governorate: Dict[str, int]

# ============================================================================
# Geo Service
# ============================================================================

class GeoService:
    """Core geographic service"""
    
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        
        # Setup coordinate transformer for area calculations
        self.wgs84 = pyproj.CRS('EPSG:4326')
        # UTM zone for Yemen (Zone 38N covers most of Yemen)
        self.utm_yemen = pyproj.CRS('EPSG:32638')
        self.transformer = pyproj.Transformer.from_crs(
            self.wgs84, self.utm_yemen, always_xy=True
        )
    
    def _geojson_to_shapely(self, geojson: Dict) -> Polygon:
        """Convert GeoJSON to Shapely geometry"""
        return shape(geojson)
    
    def _shapely_to_geojson(self, geom) -> Dict:
        """Convert Shapely geometry to GeoJSON"""
        return mapping(geom)
    
    def _calculate_area(self, geom: Polygon) -> Tuple[float, float]:
        """Calculate area in hectares and square meters"""
        # Transform to UTM for accurate area calculation
        utm_geom = transform(self.transformer.transform, geom)
        area_sqm = utm_geom.area
        area_hectares = area_sqm / 10000
        return area_hectares, area_sqm
    
    def _calculate_perimeter(self, geom: Polygon) -> float:
        """Calculate perimeter in meters"""
        utm_geom = transform(self.transformer.transform, geom)
        return utm_geom.length
    
    def _calculate_centroid(self, geom: Polygon) -> Point:
        """Calculate centroid"""
        return geom.centroid
    
    async def create_field(self, tenant_id: uuid.UUID, data: FieldCreate) -> Field:
        """Create a new field"""
        async with self.db.session() as session:
            # Convert GeoJSON to Shapely
            boundary_geom = self._geojson_to_shapely(data.boundary.dict())
            
            # Validate geometry
            if not boundary_geom.is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid polygon geometry"
                )
            
            # Calculate metrics
            area_hectares, area_sqm = self._calculate_area(boundary_geom)
            perimeter = self._calculate_perimeter(boundary_geom)
            centroid = self._calculate_centroid(boundary_geom)
            
            # Create field
            field = Field(
                tenant_id=tenant_id,
                name=data.name,
                name_ar=data.name_ar,
                code=data.code,
                description=data.description,
                description_ar=data.description_ar,
                boundary=f"SRID=4326;{boundary_geom.wkt}",
                centroid=f"SRID=4326;{centroid.wkt}",
                area_hectares=round(area_hectares, 4),
                area_sqm=round(area_sqm, 2),
                perimeter_meters=round(perimeter, 2),
                region=data.region,
                governorate=data.governorate,
                district=data.district,
                village=data.village,
                elevation_avg=data.elevation_avg,
                slope_percent=data.slope_percent,
                soil_type=data.soil_type,
                soil_ph=data.soil_ph,
                irrigation_type=data.irrigation_type,
                water_source=data.water_source,
                owner_user_id=data.owner_user_id,
                manager_user_id=data.manager_user_id,
                tags=data.tags
            )
            
            session.add(field)
            await session.commit()
            await session.refresh(field)
            
            # Log history
            await self._log_history(
                session, field.id, tenant_id, "created", None,
                {"name": field.name, "area_hectares": field.area_hectares}
            )
            
            # Emit event
            await self.event_bus.publish(
                "geo.field.created",
                {
                    "field_id": str(field.id),
                    "tenant_id": str(tenant_id),
                    "name": field.name,
                    "area_hectares": field.area_hectares,
                    "centroid": self._shapely_to_geojson(centroid)
                }
            )
            
            logger.info("Field created", field_id=str(field.id), area=field.area_hectares)
            return field
    
    async def get_field(self, field_id: uuid.UUID, tenant_id: uuid.UUID) -> Optional[Field]:
        """Get field by ID"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Field)
                .options(selectinload(Field.zones), selectinload(Field.sensors))
                .where(Field.id == field_id, Field.tenant_id == tenant_id)
            )
            return result.scalar_one_or_none()
    
    async def update_field(
        self,
        field_id: uuid.UUID,
        tenant_id: uuid.UUID,
        data: FieldUpdate,
        updated_by: Optional[uuid.UUID] = None
    ) -> Field:
        """Update field"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Field).where(Field.id == field_id, Field.tenant_id == tenant_id)
            )
            field = result.scalar_one_or_none()
            
            if not field:
                raise HTTPException(status_code=404, detail="Field not found")
            
            old_values = {}
            new_values = {}
            
            update_data = data.dict(exclude_unset=True)
            
            # Handle boundary update separately
            if 'boundary' in update_data and update_data['boundary']:
                old_values['boundary'] = "changed"
                boundary_geom = self._geojson_to_shapely(update_data['boundary'])
                
                if not boundary_geom.is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid polygon geometry"
                    )
                
                area_hectares, area_sqm = self._calculate_area(boundary_geom)
                perimeter = self._calculate_perimeter(boundary_geom)
                centroid = self._calculate_centroid(boundary_geom)
                
                field.boundary = f"SRID=4326;{boundary_geom.wkt}"
                field.centroid = f"SRID=4326;{centroid.wkt}"
                field.area_hectares = round(area_hectares, 4)
                field.area_sqm = round(area_sqm, 2)
                field.perimeter_meters = round(perimeter, 2)
                
                new_values['area_hectares'] = field.area_hectares
                del update_data['boundary']
            
            # Update other fields
            for key, value in update_data.items():
                if hasattr(field, key):
                    old_val = getattr(field, key)
                    if old_val != value:
                        old_values[key] = old_val
                        new_values[key] = value
                    setattr(field, key, value)
            
            field.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(field)
            
            # Log history
            if old_values:
                await self._log_history(
                    session, field.id, tenant_id, "updated",
                    old_values, new_values, updated_by
                )
            
            # Emit event
            await self.event_bus.publish(
                "geo.field.updated",
                {
                    "field_id": str(field.id),
                    "tenant_id": str(tenant_id),
                    "updated_fields": list(new_values.keys())
                }
            )
            
            return field
    
    async def delete_field(self, field_id: uuid.UUID, tenant_id: uuid.UUID):
        """Delete field"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Field).where(Field.id == field_id, Field.tenant_id == tenant_id)
            )
            field = result.scalar_one_or_none()
            
            if not field:
                raise HTTPException(status_code=404, detail="Field not found")
            
            await session.delete(field)
            await session.commit()
            
            # Emit event
            await self.event_bus.publish(
                "geo.field.deleted",
                {
                    "field_id": str(field_id),
                    "tenant_id": str(tenant_id)
                }
            )
    
    async def list_fields(
        self,
        tenant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        crop_filter: Optional[str] = None,
        governorate: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Field], int, float]:
        """List fields with pagination and filters"""
        async with self.db.session() as session:
            query = select(Field).where(Field.tenant_id == tenant_id)
            count_query = select(func.count(Field.id)).where(Field.tenant_id == tenant_id)
            area_query = select(func.sum(Field.area_hectares)).where(Field.tenant_id == tenant_id)
            
            if status_filter:
                query = query.where(Field.status == status_filter)
                count_query = count_query.where(Field.status == status_filter)
                area_query = area_query.where(Field.status == status_filter)
            
            if crop_filter:
                query = query.where(Field.current_crop_name == crop_filter)
                count_query = count_query.where(Field.current_crop_name == crop_filter)
                area_query = area_query.where(Field.current_crop_name == crop_filter)
            
            if governorate:
                query = query.where(Field.governorate == governorate)
                count_query = count_query.where(Field.governorate == governorate)
                area_query = area_query.where(Field.governorate == governorate)
            
            if search:
                search_filter = f"%{search}%"
                query = query.where(
                    (Field.name.ilike(search_filter)) |
                    (Field.name_ar.ilike(search_filter)) |
                    (Field.code.ilike(search_filter))
                )
                count_query = count_query.where(
                    (Field.name.ilike(search_filter)) |
                    (Field.name_ar.ilike(search_filter)) |
                    (Field.code.ilike(search_filter))
                )
                area_query = area_query.where(
                    (Field.name.ilike(search_filter)) |
                    (Field.name_ar.ilike(search_filter)) |
                    (Field.code.ilike(search_filter))
                )
            
            # Get counts
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0
            
            area_result = await session.execute(area_query)
            total_area = area_result.scalar() or 0.0
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(Field.created_at.desc())
            
            result = await session.execute(query)
            fields = result.scalars().all()
            
            return fields, total, total_area
    
    async def find_fields_by_point(
        self,
        tenant_id: uuid.UUID,
        point: GeoJSONPoint,
        buffer_meters: float = 0
    ) -> List[Field]:
        """Find fields containing or near a point"""
        async with self.db.session() as session:
            point_wkt = f"POINT({point.coordinates[0]} {point.coordinates[1]})"
            
            if buffer_meters > 0:
                # Use buffer for nearby search
                query = select(Field).where(
                    Field.tenant_id == tenant_id,
                    func.ST_DWithin(
                        Field.boundary,
                        func.ST_GeomFromText(point_wkt, 4326),
                        buffer_meters / 111000  # Approximate degrees
                    )
                )
            else:
                # Exact containment
                query = select(Field).where(
                    Field.tenant_id == tenant_id,
                    func.ST_Contains(
                        Field.boundary,
                        func.ST_GeomFromText(point_wkt, 4326)
                    )
                )
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def find_fields_intersecting(
        self,
        tenant_id: uuid.UUID,
        polygon: GeoJSONPolygon
    ) -> List[Field]:
        """Find fields intersecting a polygon"""
        async with self.db.session() as session:
            polygon_geom = self._geojson_to_shapely(polygon.dict())
            
            query = select(Field).where(
                Field.tenant_id == tenant_id,
                func.ST_Intersects(
                    Field.boundary,
                    func.ST_GeomFromText(polygon_geom.wkt, 4326)
                )
            )
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_statistics(self, tenant_id: uuid.UUID) -> FieldStatistics:
        """Get field statistics for tenant"""
        async with self.db.session() as session:
            # Total fields and area
            result = await session.execute(
                select(
                    func.count(Field.id),
                    func.sum(Field.area_hectares)
                ).where(Field.tenant_id == tenant_id)
            )
            total_fields, total_area = result.first()
            
            # Active fields
            active_result = await session.execute(
                select(func.count(Field.id)).where(
                    Field.tenant_id == tenant_id,
                    Field.status == FieldStatus.ACTIVE.value
                )
            )
            active_fields = active_result.scalar()
            
            # Fallow fields
            fallow_result = await session.execute(
                select(func.count(Field.id)).where(
                    Field.tenant_id == tenant_id,
                    Field.status == FieldStatus.FALLOW.value
                )
            )
            fallow_fields = fallow_result.scalar()
            
            # By crop
            crop_result = await session.execute(
                select(
                    Field.current_crop_name,
                    func.count(Field.id)
                ).where(
                    Field.tenant_id == tenant_id,
                    Field.current_crop_name.isnot(None)
                ).group_by(Field.current_crop_name)
            )
            by_crop = {row[0]: row[1] for row in crop_result}
            
            # By soil type
            soil_result = await session.execute(
                select(
                    Field.soil_type,
                    func.count(Field.id)
                ).where(Field.tenant_id == tenant_id).group_by(Field.soil_type)
            )
            by_soil = {row[0]: row[1] for row in soil_result}
            
            # By irrigation
            irrigation_result = await session.execute(
                select(
                    Field.irrigation_type,
                    func.count(Field.id)
                ).where(Field.tenant_id == tenant_id).group_by(Field.irrigation_type)
            )
            by_irrigation = {row[0]: row[1] for row in irrigation_result}
            
            # By governorate
            gov_result = await session.execute(
                select(
                    Field.governorate,
                    func.count(Field.id)
                ).where(
                    Field.tenant_id == tenant_id,
                    Field.governorate.isnot(None)
                ).group_by(Field.governorate)
            )
            by_governorate = {row[0]: row[1] for row in gov_result}
            
            return FieldStatistics(
                total_fields=total_fields or 0,
                total_area_hectares=total_area or 0.0,
                active_fields=active_fields or 0,
                fallow_fields=fallow_fields or 0,
                by_crop=by_crop,
                by_soil_type=by_soil,
                by_irrigation=by_irrigation,
                by_governorate=by_governorate
            )
    
    async def create_zone(
        self,
        field_id: uuid.UUID,
        tenant_id: uuid.UUID,
        data: ZoneCreate
    ) -> FieldZone:
        """Create zone within field"""
        async with self.db.session() as session:
            # Verify field exists
            field = await session.execute(
                select(Field).where(Field.id == field_id, Field.tenant_id == tenant_id)
            )
            if not field.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Field not found")
            
            boundary_geom = self._geojson_to_shapely(data.boundary.dict())
            area_hectares, _ = self._calculate_area(boundary_geom)
            
            zone = FieldZone(
                field_id=field_id,
                name=data.name,
                name_ar=data.name_ar,
                zone_type=data.zone_type,
                boundary=f"SRID=4326;{boundary_geom.wkt}",
                area_hectares=round(area_hectares, 4),
                soil_type=data.soil_type,
                irrigation_type=data.irrigation_type,
                current_crop=data.current_crop
            )
            
            session.add(zone)
            await session.commit()
            await session.refresh(zone)
            
            return zone
    
    async def create_sensor(
        self,
        field_id: uuid.UUID,
        tenant_id: uuid.UUID,
        data: SensorCreate
    ) -> FieldSensor:
        """Create sensor in field"""
        async with self.db.session() as session:
            # Verify field exists
            field = await session.execute(
                select(Field).where(Field.id == field_id, Field.tenant_id == tenant_id)
            )
            if not field.scalar_one_or_none():
                raise HTTPException(status_code=404, detail="Field not found")
            
            point = Point(data.location.coordinates[0], data.location.coordinates[1])
            
            sensor = FieldSensor(
                field_id=field_id,
                sensor_id=data.sensor_id,
                sensor_type=data.sensor_type,
                location=f"SRID=4326;{point.wkt}",
                metadata=data.metadata
            )
            
            session.add(sensor)
            await session.commit()
            await session.refresh(sensor)
            
            return sensor
    
    async def _log_history(
        self,
        session,
        field_id: uuid.UUID,
        tenant_id: uuid.UUID,
        change_type: str,
        old_values: Optional[Dict],
        new_values: Optional[Dict],
        changed_by: Optional[uuid.UUID] = None
    ):
        """Log field change history"""
        history = FieldHistory(
            field_id=field_id,
            tenant_id=tenant_id,
            change_type=change_type,
            changed_by=changed_by,
            old_values=old_values,
            new_values=new_values
        )
        session.add(history)
        await session.commit()
    
    def _field_to_response(self, field: Field) -> FieldResponse:
        """Convert field model to response"""
        boundary_shape = to_shape(field.boundary)
        centroid_shape = to_shape(field.centroid) if field.centroid else None
        
        return FieldResponse(
            id=field.id,
            tenant_id=field.tenant_id,
            name=field.name,
            name_ar=field.name_ar,
            code=field.code,
            description=field.description,
            description_ar=field.description_ar,
            boundary=self._shapely_to_geojson(boundary_shape),
            centroid=self._shapely_to_geojson(centroid_shape) if centroid_shape else None,
            area_hectares=field.area_hectares,
            area_sqm=field.area_sqm,
            perimeter_meters=field.perimeter_meters,
            region=field.region,
            governorate=field.governorate,
            district=field.district,
            village=field.village,
            elevation_avg=field.elevation_avg,
            slope_percent=field.slope_percent,
            soil_type=field.soil_type,
            soil_ph=field.soil_ph,
            soil_organic_matter=field.soil_organic_matter,
            irrigation_type=field.irrigation_type,
            water_source=field.water_source,
            water_availability=field.water_availability,
            status=field.status,
            current_crop_id=field.current_crop_id,
            current_crop_name=field.current_crop_name,
            planting_date=field.planting_date,
            expected_harvest_date=field.expected_harvest_date,
            tags=field.tags or [],
            owner_user_id=field.owner_user_id,
            manager_user_id=field.manager_user_id,
            created_at=field.created_at,
            updated_at=field.updated_at
        )

# ============================================================================
# Dependencies
# ============================================================================

db: Database = None
event_bus: EventBus = None
geo_service: GeoService = None

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, event_bus, geo_service
    
    logger.info("Starting Geo-Core Service...")
    
    db = Database(settings.DATABASE_URL)
    await db.connect()
    
    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()
    
    geo_service = GeoService(db, event_bus)
    
    logger.info("Geo-Core Service started successfully")
    
    yield
    
    logger.info("Shutting down Geo-Core Service...")
    await event_bus.close()
    await db.disconnect()

app = FastAPI(
    title="SAHOOL Geo-Core Service",
    description="Geographic Field Management with PostGIS",
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

# Field CRUD
@app.post("/api/v1/fields", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
async def create_field(tenant_id: uuid.UUID, data: FieldCreate):
    """Create a new field"""
    field = await geo_service.create_field(tenant_id, data)
    geo_operations.labels(operation="create", status="success").inc()
    return geo_service._field_to_response(field)

@app.get("/api/v1/fields/{field_id}", response_model=FieldResponse)
async def get_field(field_id: uuid.UUID, tenant_id: uuid.UUID):
    """Get field by ID"""
    field = await geo_service.get_field(field_id, tenant_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return geo_service._field_to_response(field)

@app.patch("/api/v1/fields/{field_id}", response_model=FieldResponse)
async def update_field(
    field_id: uuid.UUID,
    tenant_id: uuid.UUID,
    data: FieldUpdate,
    updated_by: Optional[uuid.UUID] = None
):
    """Update field"""
    field = await geo_service.update_field(field_id, tenant_id, data, updated_by)
    geo_operations.labels(operation="update", status="success").inc()
    return geo_service._field_to_response(field)

@app.delete("/api/v1/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field(field_id: uuid.UUID, tenant_id: uuid.UUID):
    """Delete field"""
    await geo_service.delete_field(field_id, tenant_id)
    geo_operations.labels(operation="delete", status="success").inc()

@app.get("/api/v1/fields", response_model=FieldListResponse)
async def list_fields(
    tenant_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    crop: Optional[str] = None,
    governorate: Optional[str] = None,
    search: Optional[str] = None
):
    """List fields with pagination and filters"""
    fields, total, total_area = await geo_service.list_fields(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        status_filter=status_filter,
        crop_filter=crop,
        governorate=governorate,
        search=search
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return FieldListResponse(
        items=[geo_service._field_to_response(f) for f in fields],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        total_area_hectares=total_area
    )

# Statistics
@app.get("/api/v1/fields/statistics", response_model=FieldStatistics)
async def get_statistics(tenant_id: uuid.UUID):
    """Get field statistics"""
    return await geo_service.get_statistics(tenant_id)

# Spatial Queries
@app.post("/api/v1/fields/find-by-point")
async def find_by_point(
    tenant_id: uuid.UUID,
    point: GeoJSONPoint,
    buffer_meters: float = 0
):
    """Find fields containing or near a point"""
    fields = await geo_service.find_fields_by_point(tenant_id, point, buffer_meters)
    return [geo_service._field_to_response(f) for f in fields]

@app.post("/api/v1/fields/find-intersecting")
async def find_intersecting(tenant_id: uuid.UUID, polygon: GeoJSONPolygon):
    """Find fields intersecting a polygon"""
    fields = await geo_service.find_fields_intersecting(tenant_id, polygon)
    return [geo_service._field_to_response(f) for f in fields]

# Zones
@app.post("/api/v1/fields/{field_id}/zones", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(field_id: uuid.UUID, tenant_id: uuid.UUID, data: ZoneCreate):
    """Create zone within field"""
    zone = await geo_service.create_zone(field_id, tenant_id, data)
    return zone

@app.get("/api/v1/fields/{field_id}/zones", response_model=List[ZoneResponse])
async def get_zones(field_id: uuid.UUID, tenant_id: uuid.UUID):
    """Get field zones"""
    field = await geo_service.get_field(field_id, tenant_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field.zones

# Sensors
@app.post("/api/v1/fields/{field_id}/sensors", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def create_sensor(field_id: uuid.UUID, tenant_id: uuid.UUID, data: SensorCreate):
    """Create sensor in field"""
    sensor = await geo_service.create_sensor(field_id, tenant_id, data)
    return sensor

@app.get("/api/v1/fields/{field_id}/sensors", response_model=List[SensorResponse])
async def get_sensors(field_id: uuid.UUID, tenant_id: uuid.UUID):
    """Get field sensors"""
    field = await geo_service.get_field(field_id, tenant_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field.sensors

# GeoJSON Export
@app.get("/api/v1/fields/export/geojson")
async def export_geojson(
    tenant_id: uuid.UUID,
    status_filter: Optional[str] = None,
    crop: Optional[str] = None
):
    """Export fields as GeoJSON FeatureCollection"""
    fields, _, _ = await geo_service.list_fields(
        tenant_id=tenant_id,
        page=1,
        page_size=1000,
        status_filter=status_filter,
        crop_filter=crop
    )
    
    features = []
    for field in fields:
        boundary_shape = to_shape(field.boundary)
        feature = {
            "type": "Feature",
            "geometry": mapping(boundary_shape),
            "properties": {
                "id": str(field.id),
                "name": field.name,
                "name_ar": field.name_ar,
                "area_hectares": field.area_hectares,
                "status": field.status,
                "crop": field.current_crop_name,
                "soil_type": field.soil_type,
                "irrigation": field.irrigation_type
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "tenant_id": str(tenant_id),
            "exported_at": datetime.utcnow().isoformat(),
            "total_fields": len(features)
        }
    }

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
