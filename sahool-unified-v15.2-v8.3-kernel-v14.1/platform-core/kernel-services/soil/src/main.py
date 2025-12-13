"""
SAHOOL Soil Service - Soil Analysis & Monitoring
=================================================
Layer: Signal Producer (Layer 2)
Purpose: Soil data collection, analysis, and recommendations
"""

import os
import asyncio
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from contextlib import asynccontextmanager
import uuid
import json
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Integer, Float, Date, select, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import structlog
import enum

# Shared imports
import sys
sys.path.insert(0, '/app/shared')
from database import Database, BaseModel as DBBaseModel
from events.base_event import BaseEvent, EventBus
from utils.logging import setup_logging
from metrics import MetricsManager

# ============================================================================
# Configuration
# ============================================================================

class Settings:
    """Soil service configuration"""
    SERVICE_NAME = "soil-service"
    SERVICE_PORT = int(os.getenv("SOIL_SERVICE_PORT", "8087"))
    SERVICE_LAYER = "signal-producer"
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_soil")
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
    
    # Soil Analysis Thresholds (Yemen-specific)
    OPTIMAL_PH_RANGE = (6.0, 7.5)
    OPTIMAL_ORGANIC_MATTER = 3.0  # percentage
    OPTIMAL_NITROGEN = 20  # ppm
    OPTIMAL_PHOSPHORUS = 15  # ppm
    OPTIMAL_POTASSIUM = 150  # ppm

settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

soil_events = Counter('soil_events_total', 'Soil events', ['event_type', 'status'])
analysis_latency = Histogram('soil_analysis_latency_seconds', 'Soil analysis latency')

# ============================================================================
# Database Models
# ============================================================================

class SoilType(str, enum.Enum):
    CLAY = "clay"
    SANDY = "sandy"
    LOAMY = "loamy"
    SILT = "silt"
    PEAT = "peat"
    CHALKY = "chalky"
    CLAY_LOAM = "clay_loam"
    SANDY_LOAM = "sandy_loam"
    SILTY_CLAY = "silty_clay"

class SoilHealthStatus(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class SoilSample(DBBaseModel):
    """Soil sample record"""
    __tablename__ = "soil_samples"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    field_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    zone_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Sample Info
    sample_code = Column(String(50), nullable=False)
    sample_date = Column(Date, nullable=False)
    sample_depth_cm = Column(Integer, default=30)  # Sampling depth
    
    # Location (within field)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Physical Properties
    soil_type = Column(String(50), nullable=True)
    texture = Column(String(100), nullable=True)
    structure = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    moisture_percent = Column(Float, nullable=True)
    bulk_density = Column(Float, nullable=True)  # g/cm³
    porosity_percent = Column(Float, nullable=True)
    water_holding_capacity = Column(Float, nullable=True)  # percentage
    
    # Chemical Properties
    ph = Column(Float, nullable=True)
    electrical_conductivity = Column(Float, nullable=True)  # dS/m
    organic_matter_percent = Column(Float, nullable=True)
    organic_carbon_percent = Column(Float, nullable=True)
    cation_exchange_capacity = Column(Float, nullable=True)  # cmol/kg
    
    # Macronutrients (ppm)
    nitrogen_total = Column(Float, nullable=True)
    nitrogen_available = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    calcium = Column(Float, nullable=True)
    magnesium = Column(Float, nullable=True)
    sulfur = Column(Float, nullable=True)
    
    # Micronutrients (ppm)
    iron = Column(Float, nullable=True)
    manganese = Column(Float, nullable=True)
    zinc = Column(Float, nullable=True)
    copper = Column(Float, nullable=True)
    boron = Column(Float, nullable=True)
    molybdenum = Column(Float, nullable=True)
    
    # Contaminants
    sodium = Column(Float, nullable=True)
    chloride = Column(Float, nullable=True)
    heavy_metals = Column(JSON, nullable=True)  # {lead, cadmium, etc.}
    
    # Analysis Results
    health_status = Column(String(20), nullable=True)
    health_score = Column(Float, nullable=True)  # 0-100
    
    # Metadata
    lab_name = Column(String(255), nullable=True)
    lab_report_id = Column(String(100), nullable=True)
    analyzed_by = Column(UUID(as_uuid=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recommendations = relationship("SoilRecommendation", back_populates="sample", cascade="all, delete-orphan")

class SoilRecommendation(DBBaseModel):
    """Soil improvement recommendations"""
    __tablename__ = "soil_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id = Column(UUID(as_uuid=True), ForeignKey('soil_samples.id', ondelete='CASCADE'), nullable=False)
    
    category = Column(String(50), nullable=False)  # fertilizer, amendment, irrigation, crop_selection
    priority = Column(String(20), nullable=False)  # high, medium, low
    
    title = Column(String(255), nullable=False)
    title_ar = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=True)
    
    # Application details
    product_name = Column(String(255), nullable=True)
    application_rate = Column(String(100), nullable=True)  # e.g., "50 kg/hectare"
    application_method = Column(String(100), nullable=True)
    application_timing = Column(String(255), nullable=True)
    
    # Expected outcome
    expected_improvement = Column(Text, nullable=True)
    expected_improvement_ar = Column(Text, nullable=True)
    
    # Cost estimate (YER)
    estimated_cost_per_hectare = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sample = relationship("SoilSample", back_populates="recommendations")

class SoilSensorReading(DBBaseModel):
    """Real-time soil sensor readings"""
    __tablename__ = "soil_sensor_readings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    field_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    
    reading_time = Column(DateTime, nullable=False, index=True)
    
    # Sensor readings
    moisture_percent = Column(Float, nullable=True)
    temperature_celsius = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    electrical_conductivity = Column(Float, nullable=True)
    
    # Calculated values
    moisture_status = Column(String(20), nullable=True)  # dry, optimal, wet, saturated
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SoilFertilityTrend(DBBaseModel):
    """Soil fertility trends over time"""
    __tablename__ = "soil_fertility_trends"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    field_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Averages for period
    avg_ph = Column(Float, nullable=True)
    avg_organic_matter = Column(Float, nullable=True)
    avg_nitrogen = Column(Float, nullable=True)
    avg_phosphorus = Column(Float, nullable=True)
    avg_potassium = Column(Float, nullable=True)
    
    # Trends (positive = improving, negative = declining)
    ph_trend = Column(Float, nullable=True)
    organic_matter_trend = Column(Float, nullable=True)
    nitrogen_trend = Column(Float, nullable=True)
    phosphorus_trend = Column(Float, nullable=True)
    potassium_trend = Column(Float, nullable=True)
    
    # Overall health
    overall_health_score = Column(Float, nullable=True)
    overall_health_trend = Column(Float, nullable=True)
    
    sample_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# Pydantic Schemas
# ============================================================================

class SoilSampleCreate(BaseModel):
    """Create soil sample"""
    field_id: uuid.UUID
    zone_id: Optional[uuid.UUID] = None
    sample_code: str
    sample_date: date
    sample_depth_cm: int = 30
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Physical
    soil_type: Optional[str] = None
    texture: Optional[str] = None
    moisture_percent: Optional[float] = None
    bulk_density: Optional[float] = None
    
    # Chemical
    ph: Optional[float] = None
    electrical_conductivity: Optional[float] = None
    organic_matter_percent: Optional[float] = None
    
    # Nutrients
    nitrogen_total: Optional[float] = None
    nitrogen_available: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    calcium: Optional[float] = None
    magnesium: Optional[float] = None
    
    # Micronutrients
    iron: Optional[float] = None
    zinc: Optional[float] = None
    copper: Optional[float] = None
    boron: Optional[float] = None
    
    lab_name: Optional[str] = None
    lab_report_id: Optional[str] = None
    notes: Optional[str] = None

class SoilSampleResponse(BaseModel):
    """Soil sample response"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    field_id: uuid.UUID
    zone_id: Optional[uuid.UUID]
    sample_code: str
    sample_date: date
    sample_depth_cm: int
    
    soil_type: Optional[str]
    texture: Optional[str]
    moisture_percent: Optional[float]
    
    ph: Optional[float]
    electrical_conductivity: Optional[float]
    organic_matter_percent: Optional[float]
    
    nitrogen_available: Optional[float]
    phosphorus: Optional[float]
    potassium: Optional[float]
    
    health_status: Optional[str]
    health_score: Optional[float]
    
    created_at: datetime
    
    class Config:
        from_attributes = True

class SoilAnalysisResult(BaseModel):
    """Soil analysis result"""
    sample_id: uuid.UUID
    health_status: str
    health_score: float
    
    ph_status: str
    organic_matter_status: str
    nitrogen_status: str
    phosphorus_status: str
    potassium_status: str
    
    issues: List[Dict[str, str]]
    recommendations: List[Dict[str, Any]]

class SensorReadingCreate(BaseModel):
    """Create sensor reading"""
    field_id: uuid.UUID
    sensor_id: str
    reading_time: datetime
    
    moisture_percent: Optional[float] = None
    temperature_celsius: Optional[float] = None
    ph: Optional[float] = None
    electrical_conductivity: Optional[float] = None

class SensorReadingResponse(BaseModel):
    """Sensor reading response"""
    id: uuid.UUID
    field_id: uuid.UUID
    sensor_id: str
    reading_time: datetime
    moisture_percent: Optional[float]
    temperature_celsius: Optional[float]
    ph: Optional[float]
    moisture_status: Optional[str]
    
    class Config:
        from_attributes = True

class FertilityTrendResponse(BaseModel):
    """Fertility trend response"""
    field_id: uuid.UUID
    period_start: date
    period_end: date
    avg_ph: Optional[float]
    avg_organic_matter: Optional[float]
    avg_nitrogen: Optional[float]
    avg_phosphorus: Optional[float]
    avg_potassium: Optional[float]
    overall_health_score: Optional[float]
    overall_health_trend: Optional[float]
    
    class Config:
        from_attributes = True

# ============================================================================
# Soil Analysis Engine
# ============================================================================

@dataclass
class NutrientStatus:
    status: str  # deficient, low, optimal, high, excessive
    value: float
    optimal_range: Tuple[float, float]
    recommendation: str
    recommendation_ar: str

class SoilAnalysisEngine:
    """Soil analysis and recommendation engine"""
    
    # Yemen-specific thresholds
    THRESHOLDS = {
        "ph": {
            "very_acidic": (0, 5.5),
            "acidic": (5.5, 6.0),
            "optimal": (6.0, 7.5),
            "alkaline": (7.5, 8.5),
            "very_alkaline": (8.5, 14)
        },
        "organic_matter": {
            "very_low": (0, 1),
            "low": (1, 2),
            "moderate": (2, 3),
            "optimal": (3, 5),
            "high": (5, 100)
        },
        "nitrogen": {  # Available N in ppm
            "deficient": (0, 10),
            "low": (10, 20),
            "optimal": (20, 40),
            "high": (40, 60),
            "excessive": (60, 1000)
        },
        "phosphorus": {  # Olsen P in ppm
            "deficient": (0, 5),
            "low": (5, 10),
            "optimal": (10, 25),
            "high": (25, 50),
            "excessive": (50, 1000)
        },
        "potassium": {  # Exchangeable K in ppm
            "deficient": (0, 50),
            "low": (50, 100),
            "optimal": (100, 200),
            "high": (200, 400),
            "excessive": (400, 10000)
        }
    }
    
    RECOMMENDATIONS_DB = {
        "ph_acidic": {
            "title": "Apply lime to raise pH",
            "title_ar": "إضافة الجير لرفع حموضة التربة",
            "product": "Agricultural lime",
            "rate": "2-4 tons/hectare",
            "timing": "Before planting season"
        },
        "ph_alkaline": {
            "title": "Apply sulfur to lower pH",
            "title_ar": "إضافة الكبريت لخفض قلوية التربة",
            "product": "Elemental sulfur",
            "rate": "0.5-1 ton/hectare",
            "timing": "Before planting season"
        },
        "organic_matter_low": {
            "title": "Add organic matter",
            "title_ar": "إضافة المادة العضوية",
            "product": "Compost or well-rotted manure",
            "rate": "10-20 tons/hectare",
            "timing": "During soil preparation"
        },
        "nitrogen_deficient": {
            "title": "Apply nitrogen fertilizer",
            "title_ar": "إضافة سماد النيتروجين",
            "product": "Urea (46-0-0) or Ammonium sulfate",
            "rate": "100-150 kg/hectare",
            "timing": "Split application during growth"
        },
        "phosphorus_deficient": {
            "title": "Apply phosphate fertilizer",
            "title_ar": "إضافة سماد الفوسفور",
            "product": "Triple superphosphate (0-46-0)",
            "rate": "100-200 kg/hectare",
            "timing": "At planting"
        },
        "potassium_deficient": {
            "title": "Apply potassium fertilizer",
            "title_ar": "إضافة سماد البوتاسيوم",
            "product": "Potassium chloride (0-0-60)",
            "rate": "100-150 kg/hectare",
            "timing": "Before or at planting"
        }
    }
    
    def analyze(self, sample: SoilSample) -> SoilAnalysisResult:
        """Analyze soil sample and generate recommendations"""
        issues = []
        recommendations = []
        scores = []
        
        # Analyze pH
        if sample.ph:
            ph_status = self._get_nutrient_status("ph", sample.ph)
            scores.append(self._status_to_score(ph_status.status))
            
            if ph_status.status in ["very_acidic", "acidic"]:
                issues.append({"nutrient": "pH", "status": ph_status.status, "value": sample.ph})
                rec = self.RECOMMENDATIONS_DB["ph_acidic"]
                recommendations.append({
                    "category": "amendment",
                    "priority": "high" if ph_status.status == "very_acidic" else "medium",
                    **rec
                })
            elif ph_status.status in ["alkaline", "very_alkaline"]:
                issues.append({"nutrient": "pH", "status": ph_status.status, "value": sample.ph})
                rec = self.RECOMMENDATIONS_DB["ph_alkaline"]
                recommendations.append({
                    "category": "amendment",
                    "priority": "high" if ph_status.status == "very_alkaline" else "medium",
                    **rec
                })
        
        # Analyze organic matter
        if sample.organic_matter_percent:
            om_status = self._get_nutrient_status("organic_matter", sample.organic_matter_percent)
            scores.append(self._status_to_score(om_status.status))
            
            if om_status.status in ["very_low", "low"]:
                issues.append({"nutrient": "organic_matter", "status": om_status.status, "value": sample.organic_matter_percent})
                rec = self.RECOMMENDATIONS_DB["organic_matter_low"]
                recommendations.append({
                    "category": "amendment",
                    "priority": "high" if om_status.status == "very_low" else "medium",
                    **rec
                })
        
        # Analyze Nitrogen
        if sample.nitrogen_available:
            n_status = self._get_nutrient_status("nitrogen", sample.nitrogen_available)
            scores.append(self._status_to_score(n_status.status))
            
            if n_status.status in ["deficient", "low"]:
                issues.append({"nutrient": "nitrogen", "status": n_status.status, "value": sample.nitrogen_available})
                rec = self.RECOMMENDATIONS_DB["nitrogen_deficient"]
                recommendations.append({
                    "category": "fertilizer",
                    "priority": "high" if n_status.status == "deficient" else "medium",
                    **rec
                })
        
        # Analyze Phosphorus
        if sample.phosphorus:
            p_status = self._get_nutrient_status("phosphorus", sample.phosphorus)
            scores.append(self._status_to_score(p_status.status))
            
            if p_status.status in ["deficient", "low"]:
                issues.append({"nutrient": "phosphorus", "status": p_status.status, "value": sample.phosphorus})
                rec = self.RECOMMENDATIONS_DB["phosphorus_deficient"]
                recommendations.append({
                    "category": "fertilizer",
                    "priority": "high" if p_status.status == "deficient" else "medium",
                    **rec
                })
        
        # Analyze Potassium
        if sample.potassium:
            k_status = self._get_nutrient_status("potassium", sample.potassium)
            scores.append(self._status_to_score(k_status.status))
            
            if k_status.status in ["deficient", "low"]:
                issues.append({"nutrient": "potassium", "status": k_status.status, "value": sample.potassium})
                rec = self.RECOMMENDATIONS_DB["potassium_deficient"]
                recommendations.append({
                    "category": "fertilizer",
                    "priority": "high" if k_status.status == "deficient" else "medium",
                    **rec
                })
        
        # Calculate overall health score
        health_score = sum(scores) / len(scores) if scores else 50
        health_status = self._score_to_health_status(health_score)
        
        return SoilAnalysisResult(
            sample_id=sample.id,
            health_status=health_status,
            health_score=round(health_score, 1),
            ph_status=self._get_nutrient_status("ph", sample.ph).status if sample.ph else "unknown",
            organic_matter_status=self._get_nutrient_status("organic_matter", sample.organic_matter_percent).status if sample.organic_matter_percent else "unknown",
            nitrogen_status=self._get_nutrient_status("nitrogen", sample.nitrogen_available).status if sample.nitrogen_available else "unknown",
            phosphorus_status=self._get_nutrient_status("phosphorus", sample.phosphorus).status if sample.phosphorus else "unknown",
            potassium_status=self._get_nutrient_status("potassium", sample.potassium).status if sample.potassium else "unknown",
            issues=issues,
            recommendations=recommendations
        )
    
    def _get_nutrient_status(self, nutrient: str, value: float) -> NutrientStatus:
        """Get status for a nutrient value"""
        thresholds = self.THRESHOLDS.get(nutrient, {})
        
        for status, (low, high) in thresholds.items():
            if low <= value < high:
                return NutrientStatus(
                    status=status,
                    value=value,
                    optimal_range=thresholds.get("optimal", (0, 0)),
                    recommendation="",
                    recommendation_ar=""
                )
        
        return NutrientStatus(
            status="unknown",
            value=value,
            optimal_range=(0, 0),
            recommendation="",
            recommendation_ar=""
        )
    
    def _status_to_score(self, status: str) -> float:
        """Convert status to numeric score"""
        scores = {
            "optimal": 100,
            "high": 85,
            "moderate": 75,
            "low": 50,
            "deficient": 25,
            "very_low": 15,
            "acidic": 60,
            "alkaline": 60,
            "very_acidic": 30,
            "very_alkaline": 30,
            "excessive": 40
        }
        return scores.get(status, 50)
    
    def _score_to_health_status(self, score: float) -> str:
        """Convert score to health status"""
        if score >= 90:
            return SoilHealthStatus.EXCELLENT.value
        elif score >= 75:
            return SoilHealthStatus.GOOD.value
        elif score >= 60:
            return SoilHealthStatus.FAIR.value
        elif score >= 40:
            return SoilHealthStatus.POOR.value
        else:
            return SoilHealthStatus.CRITICAL.value

# ============================================================================
# Soil Service
# ============================================================================

class SoilService:
    """Core soil analysis service"""
    
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.analysis_engine = SoilAnalysisEngine()
    
    async def create_sample(self, tenant_id: uuid.UUID, data: SoilSampleCreate) -> SoilSample:
        """Create soil sample and analyze"""
        async with self.db.session() as session:
            sample = SoilSample(
                tenant_id=tenant_id,
                **data.dict()
            )
            
            session.add(sample)
            await session.flush()
            
            # Analyze sample
            analysis = self.analysis_engine.analyze(sample)
            
            sample.health_status = analysis.health_status
            sample.health_score = analysis.health_score
            
            # Create recommendations
            for rec in analysis.recommendations:
                recommendation = SoilRecommendation(
                    sample_id=sample.id,
                    category=rec["category"],
                    priority=rec["priority"],
                    title=rec["title"],
                    title_ar=rec.get("title_ar"),
                    description=f"Apply {rec.get('product', '')} at {rec.get('rate', '')}",
                    description_ar=rec.get("title_ar"),
                    product_name=rec.get("product"),
                    application_rate=rec.get("rate"),
                    application_timing=rec.get("timing")
                )
                session.add(recommendation)
            
            await session.commit()
            await session.refresh(sample)
            
            # Emit event
            await self.event_bus.publish(
                "soil.sample.analyzed",
                {
                    "sample_id": str(sample.id),
                    "tenant_id": str(tenant_id),
                    "field_id": str(sample.field_id),
                    "health_status": sample.health_status,
                    "health_score": sample.health_score,
                    "issues_count": len(analysis.issues),
                    "recommendations_count": len(analysis.recommendations)
                }
            )
            
            soil_events.labels(event_type="sample_created", status="success").inc()
            logger.info("Soil sample created", sample_id=str(sample.id), health=sample.health_status)
            
            return sample
    
    async def get_sample(self, sample_id: uuid.UUID, tenant_id: uuid.UUID) -> Optional[SoilSample]:
        """Get soil sample by ID"""
        async with self.db.session() as session:
            result = await session.execute(
                select(SoilSample).where(
                    SoilSample.id == sample_id,
                    SoilSample.tenant_id == tenant_id
                )
            )
            return result.scalar_one_or_none()
    
    async def get_field_samples(
        self,
        field_id: uuid.UUID,
        tenant_id: uuid.UUID,
        limit: int = 10
    ) -> List[SoilSample]:
        """Get soil samples for a field"""
        async with self.db.session() as session:
            result = await session.execute(
                select(SoilSample)
                .where(
                    SoilSample.field_id == field_id,
                    SoilSample.tenant_id == tenant_id
                )
                .order_by(SoilSample.sample_date.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def record_sensor_reading(
        self,
        tenant_id: uuid.UUID,
        data: SensorReadingCreate
    ) -> SoilSensorReading:
        """Record sensor reading"""
        async with self.db.session() as session:
            # Determine moisture status
            moisture_status = None
            if data.moisture_percent is not None:
                if data.moisture_percent < 20:
                    moisture_status = "dry"
                elif data.moisture_percent < 40:
                    moisture_status = "optimal"
                elif data.moisture_percent < 60:
                    moisture_status = "wet"
                else:
                    moisture_status = "saturated"
            
            reading = SoilSensorReading(
                tenant_id=tenant_id,
                field_id=data.field_id,
                sensor_id=data.sensor_id,
                reading_time=data.reading_time,
                moisture_percent=data.moisture_percent,
                temperature_celsius=data.temperature_celsius,
                ph=data.ph,
                electrical_conductivity=data.electrical_conductivity,
                moisture_status=moisture_status
            )
            
            session.add(reading)
            await session.commit()
            await session.refresh(reading)
            
            # Emit event if moisture is critical
            if moisture_status in ["dry", "saturated"]:
                await self.event_bus.publish(
                    "soil.moisture.critical",
                    {
                        "field_id": str(data.field_id),
                        "tenant_id": str(tenant_id),
                        "sensor_id": data.sensor_id,
                        "moisture_percent": data.moisture_percent,
                        "status": moisture_status
                    }
                )
            
            return reading
    
    async def get_sensor_readings(
        self,
        field_id: uuid.UUID,
        tenant_id: uuid.UUID,
        sensor_id: Optional[str] = None,
        hours: int = 24
    ) -> List[SoilSensorReading]:
        """Get sensor readings for field"""
        async with self.db.session() as session:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            query = select(SoilSensorReading).where(
                SoilSensorReading.field_id == field_id,
                SoilSensorReading.tenant_id == tenant_id,
                SoilSensorReading.reading_time >= cutoff
            )
            
            if sensor_id:
                query = query.where(SoilSensorReading.sensor_id == sensor_id)
            
            query = query.order_by(SoilSensorReading.reading_time.desc())
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def calculate_fertility_trend(
        self,
        field_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> Optional[SoilFertilityTrend]:
        """Calculate fertility trend for field"""
        async with self.db.session() as session:
            # Get samples from last year
            cutoff = date.today() - timedelta(days=365)
            
            result = await session.execute(
                select(SoilSample).where(
                    SoilSample.field_id == field_id,
                    SoilSample.tenant_id == tenant_id,
                    SoilSample.sample_date >= cutoff
                ).order_by(SoilSample.sample_date)
            )
            samples = result.scalars().all()
            
            if len(samples) < 2:
                return None
            
            # Calculate averages
            ph_values = [s.ph for s in samples if s.ph]
            om_values = [s.organic_matter_percent for s in samples if s.organic_matter_percent]
            n_values = [s.nitrogen_available for s in samples if s.nitrogen_available]
            p_values = [s.phosphorus for s in samples if s.phosphorus]
            k_values = [s.potassium for s in samples if s.potassium]
            health_values = [s.health_score for s in samples if s.health_score]
            
            # Simple trend calculation (last value - first value)
            def calc_trend(values: List[float]) -> Optional[float]:
                if len(values) >= 2:
                    return values[-1] - values[0]
                return None
            
            trend = SoilFertilityTrend(
                tenant_id=tenant_id,
                field_id=field_id,
                period_start=samples[0].sample_date,
                period_end=samples[-1].sample_date,
                avg_ph=sum(ph_values) / len(ph_values) if ph_values else None,
                avg_organic_matter=sum(om_values) / len(om_values) if om_values else None,
                avg_nitrogen=sum(n_values) / len(n_values) if n_values else None,
                avg_phosphorus=sum(p_values) / len(p_values) if p_values else None,
                avg_potassium=sum(k_values) / len(k_values) if k_values else None,
                ph_trend=calc_trend(ph_values),
                organic_matter_trend=calc_trend(om_values),
                nitrogen_trend=calc_trend(n_values),
                phosphorus_trend=calc_trend(p_values),
                potassium_trend=calc_trend(k_values),
                overall_health_score=sum(health_values) / len(health_values) if health_values else None,
                overall_health_trend=calc_trend(health_values),
                sample_count=len(samples)
            )
            
            session.add(trend)
            await session.commit()
            await session.refresh(trend)
            
            return trend

# ============================================================================
# Dependencies
# ============================================================================

db: Database = None
event_bus: EventBus = None
soil_service: SoilService = None

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, event_bus, soil_service
    
    logger.info("Starting Soil Service...")
    
    db = Database(settings.DATABASE_URL)
    await db.connect()
    
    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()
    
    soil_service = SoilService(db, event_bus)
    
    logger.info("Soil Service started successfully")
    
    yield
    
    logger.info("Shutting down Soil Service...")
    await event_bus.close()
    await db.disconnect()

app = FastAPI(
    title="SAHOOL Soil Service",
    description="Soil Analysis & Monitoring (Layer 2 - Signal Producer)",
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
# API Endpoints (Internal Only - Layer 2)
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME, "layer": settings.SERVICE_LAYER}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Internal endpoints
@app.post("/internal/samples", response_model=SoilSampleResponse, status_code=status.HTTP_201_CREATED)
async def create_sample(tenant_id: uuid.UUID, data: SoilSampleCreate):
    """Create and analyze soil sample (internal)"""
    sample = await soil_service.create_sample(tenant_id, data)
    return sample

@app.get("/internal/samples/{sample_id}", response_model=SoilSampleResponse)
async def get_sample(sample_id: uuid.UUID, tenant_id: uuid.UUID):
    """Get soil sample (internal)"""
    sample = await soil_service.get_sample(sample_id, tenant_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample

@app.get("/internal/fields/{field_id}/samples", response_model=List[SoilSampleResponse])
async def get_field_samples(field_id: uuid.UUID, tenant_id: uuid.UUID, limit: int = 10):
    """Get field samples (internal)"""
    samples = await soil_service.get_field_samples(field_id, tenant_id, limit)
    return samples

@app.post("/internal/sensor-readings", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
async def record_sensor_reading(tenant_id: uuid.UUID, data: SensorReadingCreate):
    """Record sensor reading (internal)"""
    reading = await soil_service.record_sensor_reading(tenant_id, data)
    return reading

@app.get("/internal/fields/{field_id}/sensor-readings", response_model=List[SensorReadingResponse])
async def get_sensor_readings(
    field_id: uuid.UUID,
    tenant_id: uuid.UUID,
    sensor_id: Optional[str] = None,
    hours: int = 24
):
    """Get sensor readings (internal)"""
    readings = await soil_service.get_sensor_readings(field_id, tenant_id, sensor_id, hours)
    return readings

@app.get("/internal/fields/{field_id}/fertility-trend", response_model=FertilityTrendResponse)
async def get_fertility_trend(field_id: uuid.UUID, tenant_id: uuid.UUID):
    """Get fertility trend (internal)"""
    trend = await soil_service.calculate_fertility_trend(field_id, tenant_id)
    if not trend:
        raise HTTPException(status_code=404, detail="Not enough data for trend analysis")
    return trend

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
