"""
NDVI Service - خدمة تحليل صور الأقمار الصناعية
Layer 2: Signal Producer

NDVI = Normalized Difference Vegetation Index
مؤشر الغطاء النباتي الطبيعي

Responsibilities:
1. Fetch satellite imagery (Sentinel-2 simulation)
2. Calculate NDVI values for fields
3. Detect vegetation anomalies (stress, disease signs)
4. Publish NDVI events to NATS

Events Produced:
- ndvi.processed
- ndvi.anomaly.detected

NO PUBLIC API - Internal only (Layer 2 Rule)
"""

import os
import sys
import json
import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum

from fastapi import FastAPI
import uvicorn
import nats
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

sys.path.insert(0, '/app')
from shared.events.base_event import create_event, EventTypes  # noqa: E402
from shared.utils.logging import configure_logging, get_logger, EventLogger  # noqa: E402
from shared.metrics import EVENTS_PUBLISHED, init_service_info  # noqa: E402

configure_logging(service_name="ndvi-service")
logger = get_logger(__name__)
event_logger = EventLogger("ndvi-service")

SERVICE_NAME = "ndvi-service"
SERVICE_LAYER = "signal-producer"
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")


# ============================================
# Domain Models
# ============================================

class VegetationHealth(str, Enum):
    EXCELLENT = "excellent"    # NDVI > 0.7
    GOOD = "good"              # NDVI 0.5-0.7
    MODERATE = "moderate"      # NDVI 0.3-0.5
    POOR = "poor"              # NDVI 0.2-0.3
    BARE_SOIL = "bare_soil"    # NDVI < 0.2
    WATER = "water"            # NDVI < 0


class NDVIAnomalyType(str, Enum):
    SUDDEN_DECLINE = "sudden_decline"       # انخفاض مفاجئ
    WATER_STRESS = "water_stress"           # إجهاد مائي
    NUTRIENT_DEFICIENCY = "nutrient_def"    # نقص غذائي
    DISEASE_SUSPECTED = "disease_suspected" # اشتباه مرض
    PEST_DAMAGE = "pest_damage"             # ضرر آفات
    UNEVEN_GROWTH = "uneven_growth"         # نمو غير متساوي


@dataclass
class NDVIPixel:
    """Single NDVI pixel data"""
    x: int
    y: int
    ndvi: float
    health: VegetationHealth


@dataclass
class NDVIAnalysis:
    """Complete NDVI analysis for a field"""
    field_id: str
    analysis_date: str
    acquisition_date: str
    satellite: str
    cloud_cover_percent: float
    
    # Statistics
    ndvi_mean: float
    ndvi_min: float
    ndvi_max: float
    ndvi_std: float
    
    # Health distribution
    health_distribution: Dict[str, float]
    
    # Zones (grid of 10x10)
    zones: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "field_id": self.field_id,
            "analysis_date": self.analysis_date,
            "acquisition_date": self.acquisition_date,
            "satellite": self.satellite,
            "cloud_cover_percent": self.cloud_cover_percent,
            "statistics": {
                "mean": round(self.ndvi_mean, 3),
                "min": round(self.ndvi_min, 3),
                "max": round(self.ndvi_max, 3),
                "std": round(self.ndvi_std, 3)
            },
            "health_distribution": self.health_distribution,
            "zones": self.zones
        }


@dataclass
class NDVIAnomaly:
    """Detected NDVI anomaly"""
    anomaly_type: NDVIAnomalyType
    severity: str
    zone_id: str
    current_ndvi: float
    expected_ndvi: float
    change_percent: float
    description_ar: str
    description_en: str
    recommended_action: str
    
    def to_dict(self) -> dict:
        return {
            "type": self.anomaly_type.value,
            "severity": self.severity,
            "zone_id": self.zone_id,
            "current_ndvi": round(self.current_ndvi, 3),
            "expected_ndvi": round(self.expected_ndvi, 3),
            "change_percent": round(self.change_percent, 1),
            "description": {"ar": self.description_ar, "en": self.description_en},
            "recommended_action": self.recommended_action
        }


# ============================================
# NDVI Calculation Engine
# ============================================

class NDVICalculator:
    """NDVI calculation and analysis"""
    
    @staticmethod
    def classify_health(ndvi: float) -> VegetationHealth:
        if ndvi < 0:
            return VegetationHealth.WATER
        elif ndvi < 0.2:
            return VegetationHealth.BARE_SOIL
        elif ndvi < 0.3:
            return VegetationHealth.POOR
        elif ndvi < 0.5:
            return VegetationHealth.MODERATE
        elif ndvi < 0.7:
            return VegetationHealth.GOOD
        else:
            return VegetationHealth.EXCELLENT
    
    @staticmethod
    def calculate_ndvi(nir: float, red: float) -> float:
        """Calculate NDVI from NIR and Red bands"""
        if (nir + red) == 0:
            return 0
        return (nir - red) / (nir + red)
    
    def simulate_field_ndvi(
        self,
        field_id: str,
        base_ndvi: float = 0.6,
        variation: float = 0.15,
        problem_zones: int = 0
    ) -> NDVIAnalysis:
        """
        Simulate NDVI data for a field (10x10 grid)
        In production, this would fetch from Sentinel Hub API
        """
        zones = []
        all_ndvi = []
        
        # Create 10x10 grid
        for row in range(10):
            for col in range(10):
                zone_id = f"Z{row}{col}"
                
                # Base NDVI with random variation
                ndvi = base_ndvi + random.uniform(-variation, variation)
                
                # Add problem zones
                if problem_zones > 0 and random.random() < 0.1:
                    ndvi = ndvi * random.uniform(0.3, 0.6)
                    problem_zones -= 1
                
                ndvi = max(-0.1, min(1.0, ndvi))  # Clamp
                all_ndvi.append(ndvi)
                
                zones.append({
                    "zone_id": zone_id,
                    "row": row,
                    "col": col,
                    "ndvi": round(ndvi, 3),
                    "health": self.classify_health(ndvi).value
                })
        
        # Calculate statistics
        import statistics
        ndvi_mean = statistics.mean(all_ndvi)
        ndvi_std = statistics.stdev(all_ndvi) if len(all_ndvi) > 1 else 0
        
        # Health distribution
        health_counts = {}
        for zone in zones:
            h = zone["health"]
            health_counts[h] = health_counts.get(h, 0) + 1
        health_dist = {k: round(v/100, 2) for k, v in health_counts.items()}
        
        return NDVIAnalysis(
            field_id=field_id,
            analysis_date=datetime.utcnow().isoformat(),
            acquisition_date=(datetime.utcnow() - timedelta(days=random.randint(1, 5))).strftime("%Y-%m-%d"),
            satellite="Sentinel-2",
            cloud_cover_percent=random.uniform(0, 20),
            ndvi_mean=ndvi_mean,
            ndvi_min=min(all_ndvi),
            ndvi_max=max(all_ndvi),
            ndvi_std=ndvi_std,
            health_distribution=health_dist,
            zones=zones
        )


class AnomalyDetector:
    """Detect NDVI anomalies by comparing with history"""
    
    def __init__(self):
        # Historical baselines (simulated - would be from DB)
        self.baselines: Dict[str, Dict[str, float]] = {}
    
    def set_baseline(self, field_id: str, month: int, expected_ndvi: float):
        key = f"{field_id}_{month}"
        self.baselines[key] = {"expected": expected_ndvi, "threshold": 0.15}
    
    def detect_anomalies(
        self,
        analysis: NDVIAnalysis,
        previous_ndvi: Optional[float] = None
    ) -> List[NDVIAnomaly]:
        """Detect anomalies in NDVI analysis"""
        anomalies = []
        current_month = datetime.now().month
        
        # Get baseline
        baseline_key = f"{analysis.field_id}_{current_month}"
        baseline = self.baselines.get(baseline_key, {"expected": 0.55, "threshold": 0.15})
        expected = baseline["expected"]
        threshold = baseline["threshold"]
        
        # Check overall decline
        if previous_ndvi and previous_ndvi > 0:
            change = ((analysis.ndvi_mean - previous_ndvi) / previous_ndvi) * 100
            if change < -20:
                anomalies.append(NDVIAnomaly(
                    anomaly_type=NDVIAnomalyType.SUDDEN_DECLINE,
                    severity="high" if change < -30 else "medium",
                    zone_id="field_wide",
                    current_ndvi=analysis.ndvi_mean,
                    expected_ndvi=previous_ndvi,
                    change_percent=change,
                    description_ar=f"انخفاض مفاجئ في الغطاء النباتي بنسبة {abs(change):.1f}%",
                    description_en=f"Sudden vegetation decline of {abs(change):.1f}%",
                    recommended_action="immediate_field_inspection"
                ))
        
        # Check if below baseline
        deviation = analysis.ndvi_mean - expected
        if deviation < -threshold:
            # Determine likely cause
            if analysis.health_distribution.get("poor", 0) > 0.3:
                anomaly_type = NDVIAnomalyType.WATER_STRESS
                desc_ar = "اشتباه إجهاد مائي - المحصول يحتاج ري عاجل"
                desc_en = "Water stress suspected - crop needs urgent irrigation"
                action = "increase_irrigation"
            else:
                anomaly_type = NDVIAnomalyType.NUTRIENT_DEFICIENCY
                desc_ar = "اشتباه نقص غذائي - يُنصح بفحص التربة"
                desc_en = "Nutrient deficiency suspected - soil test recommended"
                action = "soil_test"
            
            anomalies.append(NDVIAnomaly(
                anomaly_type=anomaly_type,
                severity="medium",
                zone_id="field_wide",
                current_ndvi=analysis.ndvi_mean,
                expected_ndvi=expected,
                change_percent=(deviation / expected) * 100,
                description_ar=desc_ar,
                description_en=desc_en,
                recommended_action=action
            ))
        
        # Check for uneven growth (high std)
        if analysis.ndvi_std > 0.2:
            # Find problem zones
            problem_zones = [z for z in analysis.zones if z["health"] in ["poor", "bare_soil"]]
            if problem_zones:
                anomalies.append(NDVIAnomaly(
                    anomaly_type=NDVIAnomalyType.UNEVEN_GROWTH,
                    severity="medium",
                    zone_id=problem_zones[0]["zone_id"],
                    current_ndvi=problem_zones[0]["ndvi"],
                    expected_ndvi=analysis.ndvi_mean,
                    change_percent=((problem_zones[0]["ndvi"] - analysis.ndvi_mean) / analysis.ndvi_mean) * 100,
                    description_ar=f"نمو غير متساوي - {len(problem_zones)} منطقة ضعيفة",
                    description_en=f"Uneven growth - {len(problem_zones)} problem zones",
                    recommended_action="zone_specific_treatment"
                ))
        
        return anomalies


# ============================================
# NDVI Service Core
# ============================================

class NDVIService:
    """Main NDVI service"""
    
    def __init__(self):
        self.nc = None
        self.js = None
        self.calculator = NDVICalculator()
        self.detector = AnomalyDetector()
        self.scheduler = AsyncIOScheduler()
        
        # Monitored fields (would be from DB)
        self.fields = [
            {"id": "field_001", "name": "حقل القمح - صنعاء", "crop": "wheat", "area_ha": 5.2, "lat": 15.37, "lon": 44.19},
            {"id": "field_002", "name": "حقل البن - تعز", "crop": "coffee", "area_ha": 3.8, "lat": 13.58, "lon": 44.02},
            {"id": "field_003", "name": "حقل الذرة - الحديدة", "crop": "corn", "area_ha": 8.0, "lat": 14.80, "lon": 42.95},
            {"id": "field_004", "name": "حقل الخضروات - عدن", "crop": "vegetables", "area_ha": 2.5, "lat": 12.78, "lon": 45.01},
        ]
        
        # Previous NDVI values for change detection
        self.previous_ndvi: Dict[str, float] = {}
    
    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("nats_connected")
    
    async def start_scheduler(self):
        # Process NDVI every 5 days (Sentinel-2 revisit time)
        self.scheduler.add_job(self.process_all_fields, CronTrigger(day="*/5", hour=10), id="ndvi_processing")
        self.scheduler.start()
        logger.info("scheduler_started")
    
    async def process_field(self, field: Dict) -> Tuple[NDVIAnalysis, List[NDVIAnomaly]]:
        """Process NDVI for single field"""
        # Simulate NDVI (in production, fetch from Sentinel Hub)
        # Different crops have different baseline NDVI
        crop_baselines = {"wheat": 0.55, "coffee": 0.65, "corn": 0.60, "vegetables": 0.50}
        base_ndvi = crop_baselines.get(field["crop"], 0.55)
        
        # Random problem zones for demo
        problem_zones = random.randint(0, 3) if random.random() < 0.3 else 0
        
        analysis = self.calculator.simulate_field_ndvi(
            field_id=field["id"],
            base_ndvi=base_ndvi,
            variation=0.1,
            problem_zones=problem_zones
        )
        
        # Detect anomalies
        previous = self.previous_ndvi.get(field["id"])
        anomalies = self.detector.detect_anomalies(analysis, previous)
        
        # Store for next comparison
        self.previous_ndvi[field["id"]] = analysis.ndvi_mean
        
        return analysis, anomalies
    
    async def process_all_fields(self):
        """Process NDVI for all monitored fields"""
        logger.info("processing_ndvi_all_fields", field_count=len(self.fields))
        
        for field in self.fields:
            try:
                analysis, anomalies = await self.process_field(field)
                
                # Publish NDVI processed event
                event = create_event(
                    event_type=EventTypes.NDVI_PROCESSED,
                    payload={
                        "field": {
                            "id": field["id"],
                            "name": field["name"],
                            "crop": field["crop"],
                            "area_ha": field["area_ha"]
                        },
                        "analysis": analysis.to_dict()
                    },
                    tenant_id="default"
                )
                
                await self.js.publish(
                    subject=EventTypes.NDVI_PROCESSED,
                    payload=json.dumps(event).encode()
                )
                event_logger.published(EventTypes.NDVI_PROCESSED, field_id=field["id"])
                EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.NDVI_PROCESSED, tenant_id="default").inc()
                
                # Publish anomalies
                for anomaly in anomalies:
                    anomaly_event = create_event(
                        event_type=EventTypes.NDVI_ANOMALY_DETECTED,
                        payload={
                            "field": {"id": field["id"], "name": field["name"], "crop": field["crop"]},
                            "anomaly": anomaly.to_dict(),
                            "analysis_summary": {
                                "ndvi_mean": analysis.ndvi_mean,
                                "health_distribution": analysis.health_distribution
                            }
                        },
                        tenant_id="default"
                    )
                    await self.js.publish(subject=EventTypes.NDVI_ANOMALY_DETECTED, payload=json.dumps(anomaly_event).encode())
                    event_logger.published(EventTypes.NDVI_ANOMALY_DETECTED, field_id=field["id"], anomaly_type=anomaly.anomaly_type.value)
                    logger.warning("ndvi_anomaly_detected", field=field["id"], type=anomaly.anomaly_type.value, severity=anomaly.severity)
                
                logger.info("field_processed", field_id=field["id"], ndvi_mean=round(analysis.ndvi_mean, 3), anomalies=len(anomalies))
                
            except Exception as e:
                logger.error("field_processing_failed", field_id=field["id"], error=str(e))
    
    async def stop(self):
        self.scheduler.shutdown()
        if self.nc: await self.nc.close()
        logger.info("ndvi_service_stopped")


ndvi_service = NDVIService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", layer=SERVICE_LAYER)
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await ndvi_service.connect()
    await ndvi_service.start_scheduler()
    asyncio.create_task(ndvi_service.process_all_fields())
    logger.info("service_started")
    yield
    await ndvi_service.stop()


app = FastAPI(title="NDVI Service", description="SAHOOL - Satellite NDVI Signal Producer (Layer 2)", version="1.0.0", lifespan=lifespan)


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}

@app.get("/readyz")
async def ready():
    return {"status": "ready" if ndvi_service.nc and ndvi_service.nc.is_connected else "not_ready"}

@app.get("/internal/fields")
async def get_fields():
    return {"fields": ndvi_service.fields}

@app.post("/internal/trigger-processing")
async def trigger_processing():
    asyncio.create_task(ndvi_service.process_all_fields())
    return {"message": "NDVI processing triggered"}

@app.post("/internal/process-field/{field_id}")
async def process_single_field(field_id: str):
    field = next((f for f in ndvi_service.fields if f["id"] == field_id), None)
    if not field:
        return {"error": "Field not found"}
    analysis, anomalies = await ndvi_service.process_field(field)
    return {"analysis": analysis.to_dict(), "anomalies": [a.to_dict() for a in anomalies]}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("NDVI_PORT", "8085")), reload=os.getenv("ENV") == "development")
