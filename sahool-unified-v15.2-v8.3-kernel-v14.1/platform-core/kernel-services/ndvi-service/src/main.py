"""
NDVI Service - Signal Producer
Layer 2: Signal Producer (NO PUBLIC API)

خدمة تحليل مؤشر الغطاء النباتي NDVI
تحلل صور الأقمار الصناعية وترصد صحة المحاصيل

Responsibilities:
1. Fetch satellite imagery (Sentinel-2 via STAC API)
2. Calculate NDVI (Normalized Difference Vegetation Index)
3. Detect vegetation health anomalies
4. Publish NDVI events to NATS
5. NO public API (Layer 2 rule)
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import math

from fastapi import FastAPI
import uvicorn
import httpx
import nats
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Add shared to path
sys.path.insert(0, '/app')
from shared.events.base_event import EventTypes, create_event  # noqa: E402
from shared.utils.logging import configure_logging, get_logger, EventLogger  # noqa: E402
from shared.metrics import EVENTS_PUBLISHED, init_service_info, get_metrics, get_metrics_content_type  # noqa: E402

# Configure
configure_logging(service_name="ndvi-service")
logger = get_logger(__name__)
event_logger = EventLogger("ndvi-service")

# Configuration
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "ndvi-service"
SERVICE_LAYER = "signal-producer"


# ============================================
# NDVI Data Models
# ============================================

class VegetationHealth(str, Enum):
    """صحة الغطاء النباتي"""
    DEAD = "dead"           # ميت
    STRESSED = "stressed"   # مجهد
    MODERATE = "moderate"   # متوسط
    HEALTHY = "healthy"     # صحي
    VERY_HEALTHY = "very_healthy"  # صحي جداً


class NDVIAnomalyType(str, Enum):
    """أنواع شذوذ NDVI"""
    SUDDEN_DROP = "sudden_drop"         # انخفاض مفاجئ
    GRADUAL_DECLINE = "gradual_decline" # تراجع تدريجي
    STRESS_PATTERN = "stress_pattern"   # نمط إجهاد
    DISEASE_SUSPECTED = "disease_suspected"  # اشتباه مرض
    WATER_STRESS = "water_stress"       # إجهاد مائي
    PEST_DAMAGE = "pest_damage"         # أضرار آفات


@dataclass
class NDVIReading:
    """قراءة NDVI لحقل"""
    field_id: str
    timestamp: datetime
    ndvi_mean: float      # -1 to 1
    ndvi_min: float
    ndvi_max: float
    ndvi_std: float       # Standard deviation
    cloud_cover: float    # Percentage
    vegetation_health: VegetationHealth
    area_healthy_pct: float    # % of area that's healthy
    area_stressed_pct: float   # % of area that's stressed
    
    def to_dict(self) -> dict:
        return {
            "field_id": self.field_id,
            "timestamp": self.timestamp.isoformat(),
            "ndvi_mean": round(self.ndvi_mean, 3),
            "ndvi_min": round(self.ndvi_min, 3),
            "ndvi_max": round(self.ndvi_max, 3),
            "ndvi_std": round(self.ndvi_std, 3),
            "cloud_cover": round(self.cloud_cover, 1),
            "vegetation_health": self.vegetation_health.value,
            "area_healthy_pct": round(self.area_healthy_pct, 1),
            "area_stressed_pct": round(self.area_stressed_pct, 1)
        }


@dataclass
class NDVIAnomaly:
    """شذوذ NDVI مكتشف"""
    anomaly_type: NDVIAnomalyType
    severity: str  # low, medium, high, critical
    current_ndvi: float
    baseline_ndvi: float
    change_pct: float
    affected_area_pct: float
    description_ar: str
    
    def to_dict(self) -> dict:
        return {
            "type": self.anomaly_type.value,
            "severity": self.severity,
            "current_ndvi": round(self.current_ndvi, 3),
            "baseline_ndvi": round(self.baseline_ndvi, 3),
            "change_pct": round(self.change_pct, 1),
            "affected_area_pct": round(self.affected_area_pct, 1),
            "description_ar": self.description_ar
        }


# ============================================
# NDVI Calculation & Classification
# ============================================

def classify_ndvi(ndvi: float) -> VegetationHealth:
    """
    تصنيف NDVI إلى فئات صحة النبات
    
    NDVI ranges:
    < 0.1: Dead/Bare soil
    0.1 - 0.2: Stressed vegetation
    0.2 - 0.4: Moderate vegetation
    0.4 - 0.6: Healthy vegetation
    > 0.6: Very healthy/Dense vegetation
    """
    if ndvi < 0.1:
        return VegetationHealth.DEAD
    elif ndvi < 0.2:
        return VegetationHealth.STRESSED
    elif ndvi < 0.4:
        return VegetationHealth.MODERATE
    elif ndvi < 0.6:
        return VegetationHealth.HEALTHY
    else:
        return VegetationHealth.VERY_HEALTHY


def calculate_ndvi(nir: float, red: float) -> float:
    """
    حساب NDVI
    NDVI = (NIR - Red) / (NIR + Red)
    """
    if nir + red == 0:
        return 0
    return (nir - red) / (nir + red)


# ============================================
# Sentinel Hub Simulator (for development)
# In production, use actual Sentinel Hub or STAC API
# ============================================

class SatelliteImageryProvider:
    """
    مزود صور الأقمار الصناعية
    Simulates satellite imagery data for development
    In production: Use Sentinel Hub, Planet, or STAC APIs
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        # In production, set these from environment
        self.stac_api_url = os.getenv("STAC_API_URL", "https://earth-search.aws.element84.com/v1")
    
    async def get_ndvi_for_field(
        self,
        field_id: str,
        bbox: Tuple[float, float, float, float],  # (min_lon, min_lat, max_lon, max_lat)
        date_range: Tuple[str, str] = None
    ) -> Optional[NDVIReading]:
        """
        الحصول على NDVI للحقل
        
        For development: Returns simulated data
        For production: Query Sentinel-2 imagery and calculate NDVI
        """
        try:
            # Simulate NDVI calculation
            # In production, this would:
            # 1. Query STAC API for Sentinel-2 imagery
            # 2. Download NIR (B8) and Red (B4) bands
            # 3. Calculate NDVI pixel by pixel
            # 4. Aggregate statistics
            
            # Simulated values based on typical Yemen agriculture
            import random
            base_ndvi = 0.35 + random.uniform(-0.15, 0.2)
            
            # Add some randomness for realistic variation
            ndvi_values = [base_ndvi + random.uniform(-0.1, 0.1) for _ in range(100)]
            
            ndvi_mean = sum(ndvi_values) / len(ndvi_values)
            ndvi_min = min(ndvi_values)
            ndvi_max = max(ndvi_values)
            ndvi_std = math.sqrt(sum((x - ndvi_mean) ** 2 for x in ndvi_values) / len(ndvi_values))
            
            # Calculate area percentages
            healthy_count = sum(1 for v in ndvi_values if v >= 0.4)
            stressed_count = sum(1 for v in ndvi_values if v < 0.2)
            
            reading = NDVIReading(
                field_id=field_id,
                timestamp=datetime.utcnow(),
                ndvi_mean=ndvi_mean,
                ndvi_min=ndvi_min,
                ndvi_max=ndvi_max,
                ndvi_std=ndvi_std,
                cloud_cover=random.uniform(0, 30),  # Simulated
                vegetation_health=classify_ndvi(ndvi_mean),
                area_healthy_pct=(healthy_count / len(ndvi_values)) * 100,
                area_stressed_pct=(stressed_count / len(ndvi_values)) * 100
            )
            
            return reading
            
        except Exception as e:
            logger.error("ndvi_fetch_failed", field_id=field_id, error=str(e))
            return None
    
    async def get_ndvi_timeseries(
        self,
        field_id: str,
        bbox: Tuple[float, float, float, float],
        days: int = 30
    ) -> List[dict]:
        """
        الحصول على سلسلة NDVI الزمنية للكشف عن التغيرات
        """
        timeseries = []
        
        # Simulate historical data
        import random
        base = 0.4
        for i in range(days // 5):  # Every 5 days (Sentinel-2 revisit)
            date = datetime.utcnow() - timedelta(days=days - i * 5)
            # Add trend and noise
            ndvi = base + (i * 0.01) + random.uniform(-0.05, 0.05)
            timeseries.append({
                "date": date.isoformat(),
                "ndvi": round(ndvi, 3)
            })
        
        return timeseries
    
    async def close(self):
        await self.client.aclose()


# ============================================
# Anomaly Detector
# ============================================

class NDVIAnomalyDetector:
    """كاشف شذوذ NDVI"""
    
    def __init__(self):
        self.baseline_cache: Dict[str, float] = {}
        self.history_cache: Dict[str, List[float]] = {}
    
    def detect(
        self,
        current: NDVIReading,
        history: List[dict] = None,
        baseline: float = None
    ) -> List[NDVIAnomaly]:
        """
        الكشف عن الشذوذات في NDVI
        """
        anomalies = []
        field_id = current.field_id
        
        # Use cached baseline or calculate from history
        if baseline is None:
            if history and len(history) > 5:
                baseline = sum(h.get("ndvi", 0) for h in history) / len(history)
            else:
                baseline = self.baseline_cache.get(field_id, 0.4)  # Default
        
        self.baseline_cache[field_id] = baseline
        
        # Calculate change percentage
        if baseline > 0:
            change_pct = ((current.ndvi_mean - baseline) / baseline) * 100
        else:
            change_pct = 0
        
        # Check for sudden drop (> 20% decrease)
        if change_pct < -20:
            severity = "critical" if change_pct < -40 else "high"
            anomalies.append(NDVIAnomaly(
                anomaly_type=NDVIAnomalyType.SUDDEN_DROP,
                severity=severity,
                current_ndvi=current.ndvi_mean,
                baseline_ndvi=baseline,
                change_pct=change_pct,
                affected_area_pct=current.area_stressed_pct,
                description_ar=f"انخفاض مفاجئ في صحة النباتات بنسبة {abs(change_pct):.1f}%"
            ))
        
        # Check for water stress pattern
        if current.ndvi_mean < 0.25 and current.ndvi_std > 0.1:
            anomalies.append(NDVIAnomaly(
                anomaly_type=NDVIAnomalyType.WATER_STRESS,
                severity="high" if current.ndvi_mean < 0.2 else "medium",
                current_ndvi=current.ndvi_mean,
                baseline_ndvi=baseline,
                change_pct=change_pct,
                affected_area_pct=current.area_stressed_pct,
                description_ar="نمط إجهاد مائي مكتشف - النباتات بحاجة للري"
            ))
        
        # Check for high stressed area
        if current.area_stressed_pct > 30:
            severity = "critical" if current.area_stressed_pct > 50 else "high"
            anomalies.append(NDVIAnomaly(
                anomaly_type=NDVIAnomalyType.STRESS_PATTERN,
                severity=severity,
                current_ndvi=current.ndvi_mean,
                baseline_ndvi=baseline,
                change_pct=change_pct,
                affected_area_pct=current.area_stressed_pct,
                description_ar=f"{current.area_stressed_pct:.1f}% من الحقل يعاني من إجهاد"
            ))
        
        # Check for potential disease (high variability + decline)
        if current.ndvi_std > 0.15 and change_pct < -10:
            anomalies.append(NDVIAnomaly(
                anomaly_type=NDVIAnomalyType.DISEASE_SUSPECTED,
                severity="high",
                current_ndvi=current.ndvi_mean,
                baseline_ndvi=baseline,
                change_pct=change_pct,
                affected_area_pct=current.area_stressed_pct,
                description_ar="اشتباه إصابة مرضية - يرجى الفحص الميداني"
            ))
        
        # Check for gradual decline using history
        if history and len(history) >= 4:
            recent = [h.get("ndvi", 0) for h in history[-4:]]
            if all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
                # Consistent decline
                total_decline = ((recent[-1] - recent[0]) / recent[0]) * 100 if recent[0] > 0 else 0
                if total_decline < -10:
                    anomalies.append(NDVIAnomaly(
                        anomaly_type=NDVIAnomalyType.GRADUAL_DECLINE,
                        severity="medium",
                        current_ndvi=current.ndvi_mean,
                        baseline_ndvi=baseline,
                        change_pct=total_decline,
                        affected_area_pct=current.area_stressed_pct,
                        description_ar=f"تراجع تدريجي مستمر في صحة النباتات ({total_decline:.1f}%)"
                    ))
        
        return anomalies


# ============================================
# NDVI Service Core
# ============================================

class NDVIService:
    """Core NDVI analysis service"""
    
    def __init__(self):
        self.nc = None
        self.js = None
        self.provider = SatelliteImageryProvider()
        self.detector = NDVIAnomalyDetector()
        self.scheduler = AsyncIOScheduler()
        self.monitored_fields: Dict[str, dict] = {}
    
    async def connect(self):
        """Connect to NATS"""
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("nats_connected")
    
    async def start(self):
        """Start NDVI monitoring"""
        # Add sample fields for development
        self._add_sample_fields()
        
        # Schedule NDVI analysis (every 5 days to match Sentinel-2)
        self.scheduler.add_job(
            self._analyze_all_fields,
            CronTrigger(day="*/5", hour=10, minute=0),
            id="ndvi_analysis"
        )
        
        # Daily check for new imagery
        self.scheduler.add_job(
            self._check_new_imagery,
            CronTrigger(hour=8, minute=0),
            id="imagery_check"
        )
        
        self.scheduler.start()
        logger.info("ndvi_scheduler_started")
        
        # Initial analysis
        await self._analyze_all_fields()
    
    def _add_sample_fields(self):
        """Add sample fields for monitoring"""
        self.monitored_fields = {
            "field_001": {
                "name_ar": "حقل القمح - ذمار",
                "crop_type": "wheat",
                "bbox": (44.35, 14.50, 44.40, 14.55),
                "tenant_id": "default",
                "region": "highlands"
            },
            "field_002": {
                "name_ar": "حقل البن - صنعاء",
                "crop_type": "coffee",
                "bbox": (44.18, 15.35, 44.22, 15.40),
                "tenant_id": "default",
                "region": "highlands"
            },
            "field_003": {
                "name_ar": "حقل الذرة - إب",
                "crop_type": "sorghum",
                "bbox": (44.15, 13.95, 44.20, 14.00),
                "tenant_id": "default",
                "region": "highlands"
            },
            "field_004": {
                "name_ar": "حقل المانجو - تهامة",
                "crop_type": "mango",
                "bbox": (43.20, 14.75, 43.25, 14.80),
                "tenant_id": "default",
                "region": "tihama"
            }
        }
    
    async def _analyze_all_fields(self):
        """Analyze NDVI for all monitored fields"""
        logger.info("analyzing_all_fields", count=len(self.monitored_fields))
        
        for field_id, field in self.monitored_fields.items():
            await self._analyze_field(field_id, field)
            await asyncio.sleep(2)  # Rate limiting
    
    async def _analyze_field(self, field_id: str, field: dict):
        """Analyze NDVI for a single field"""
        try:
            # Get current NDVI
            reading = await self.provider.get_ndvi_for_field(
                field_id=field_id,
                bbox=field["bbox"]
            )
            
            if not reading:
                return
            
            # Get historical data for comparison
            history = await self.provider.get_ndvi_timeseries(
                field_id=field_id,
                bbox=field["bbox"],
                days=30
            )
            
            # Detect anomalies
            anomalies = self.detector.detect(reading, history)
            
            # Publish NDVI processed event
            await self._publish_ndvi_processed(field_id, field, reading, history)
            
            # Publish anomaly events
            for anomaly in anomalies:
                await self._publish_anomaly(field_id, field, anomaly, reading)
            
            logger.info(
                "field_analyzed",
                field_id=field_id,
                ndvi=reading.ndvi_mean,
                health=reading.vegetation_health.value,
                anomalies=len(anomalies)
            )
            
        except Exception as e:
            logger.error("field_analysis_failed", field_id=field_id, error=str(e))
    
    async def _publish_ndvi_processed(
        self,
        field_id: str,
        field: dict,
        reading: NDVIReading,
        history: List[dict]
    ):
        """Publish NDVI processed event"""
        event = create_event(
            event_type=EventTypes.NDVI_PROCESSED,
            payload={
                "field": {
                    "id": field_id,
                    "name_ar": field["name_ar"],
                    "crop_type": field["crop_type"],
                    "region": field["region"]
                },
                "reading": reading.to_dict(),
                "history_30d": history[-6:] if history else [],  # Last 6 readings
                "recommendations": self._get_recommendations(reading)
            },
            tenant_id=field["tenant_id"]
        )
        
        await self.js.publish(
            subject=EventTypes.NDVI_PROCESSED,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        EVENTS_PUBLISHED.labels(
            service=SERVICE_NAME,
            event_type=EventTypes.NDVI_PROCESSED,
            tenant_id=field["tenant_id"]
        ).inc()
        
        event_logger.published(EventTypes.NDVI_PROCESSED, event_id=event["event_id"])
    
    async def _publish_anomaly(
        self,
        field_id: str,
        field: dict,
        anomaly: NDVIAnomaly,
        reading: NDVIReading
    ):
        """Publish NDVI anomaly event"""
        event = create_event(
            event_type=EventTypes.NDVI_ANOMALY_DETECTED,
            payload={
                "field": {
                    "id": field_id,
                    "name_ar": field["name_ar"],
                    "crop_type": field["crop_type"]
                },
                "anomaly": anomaly.to_dict(),
                "current_reading": reading.to_dict(),
                "actions": self._get_anomaly_actions(anomaly)
            },
            tenant_id=field["tenant_id"]
        )
        
        await self.js.publish(
            subject=EventTypes.NDVI_ANOMALY_DETECTED,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        EVENTS_PUBLISHED.labels(
            service=SERVICE_NAME,
            event_type=EventTypes.NDVI_ANOMALY_DETECTED,
            tenant_id=field["tenant_id"]
        ).inc()
        
        event_logger.published(
            EventTypes.NDVI_ANOMALY_DETECTED,
            event_id=event["event_id"],
            anomaly_type=anomaly.anomaly_type.value
        )
        
        logger.warning(
            "ndvi_anomaly_detected",
            field_id=field_id,
            type=anomaly.anomaly_type.value,
            severity=anomaly.severity
        )
    
    async def _check_new_imagery(self):
        """Check for new satellite imagery availability"""
        logger.info("checking_new_imagery")
        # In production, query STAC API for new Sentinel-2 scenes
    
    def _get_recommendations(self, reading: NDVIReading) -> List[dict]:
        """Get recommendations based on NDVI reading"""
        recommendations = []
        
        if reading.vegetation_health == VegetationHealth.STRESSED:
            recommendations.append({
                "action_ar": "فحص الري والتسميد",
                "priority": "high"
            })
        elif reading.vegetation_health == VegetationHealth.DEAD:
            recommendations.append({
                "action_ar": "فحص ميداني عاجل",
                "priority": "urgent"
            })
        
        if reading.area_stressed_pct > 20:
            recommendations.append({
                "action_ar": f"معالجة المنطقة المتضررة ({reading.area_stressed_pct:.0f}%)",
                "priority": "high"
            })
        
        if reading.ndvi_std > 0.12:
            recommendations.append({
                "action_ar": "توحيد المعاملات الزراعية",
                "priority": "medium"
            })
        
        return recommendations
    
    def _get_anomaly_actions(self, anomaly: NDVIAnomaly) -> List[dict]:
        """Get actions for anomaly"""
        actions = {
            NDVIAnomalyType.SUDDEN_DROP: [
                {"action_ar": "فحص ميداني فوري", "priority": "urgent"},
                {"action_ar": "فحص الري والصرف", "priority": "high"},
                {"action_ar": "أخذ عينات للتحليل", "priority": "high"}
            ],
            NDVIAnomalyType.WATER_STRESS: [
                {"action_ar": "زيادة معدلات الري", "priority": "urgent"},
                {"action_ar": "فحص نظام الري", "priority": "high"},
                {"action_ar": "تطبيق مواد حافظة للرطوبة", "priority": "medium"}
            ],
            NDVIAnomalyType.DISEASE_SUSPECTED: [
                {"action_ar": "فحص بصري للنباتات", "priority": "urgent"},
                {"action_ar": "أخذ عينات للمختبر", "priority": "high"},
                {"action_ar": "عزل المنطقة المتضررة", "priority": "high"}
            ],
            NDVIAnomalyType.GRADUAL_DECLINE: [
                {"action_ar": "مراجعة برنامج التسميد", "priority": "high"},
                {"action_ar": "فحص التربة", "priority": "medium"},
                {"action_ar": "تقييم الصرف", "priority": "medium"}
            ],
            NDVIAnomalyType.STRESS_PATTERN: [
                {"action_ar": "تحديد نمط الإجهاد", "priority": "high"},
                {"action_ar": "معالجة حسب السبب", "priority": "medium"}
            ],
            NDVIAnomalyType.PEST_DAMAGE: [
                {"action_ar": "تحديد نوع الآفة", "priority": "urgent"},
                {"action_ar": "تطبيق المكافحة المناسبة", "priority": "high"}
            ]
        }
        
        return actions.get(anomaly.anomaly_type, [])
    
    async def stop(self):
        """Stop service"""
        self.scheduler.shutdown()
        await self.provider.close()
        if self.nc:
            await self.nc.close()
        logger.info("ndvi_service_stopped")


# ============================================
# Global Instance
# ============================================

ndvi_service = NDVIService()


# ============================================
# FastAPI Application (Internal Only)
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("service_starting", layer=SERVICE_LAYER)
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    
    await ndvi_service.connect()
    await ndvi_service.start()
    
    logger.info("service_started")
    yield
    
    await ndvi_service.stop()
    logger.info("service_stopped")


app = FastAPI(
    title="NDVI Service",
    description="SAHOOL Platform - NDVI Signal Producer (Internal)",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================
# Internal Endpoints Only (Layer 2 Rule)
# ============================================

@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    connected = ndvi_service.nc is not None and ndvi_service.nc.is_connected
    return {"status": "ready" if connected else "not_ready"}


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response
    return Response(content=get_metrics(), media_type=get_metrics_content_type())


@app.get("/internal/fields")
async def get_fields():
    """Internal: List monitored fields"""
    return {"fields": ndvi_service.monitored_fields}


@app.post("/internal/analyze/{field_id}")
async def trigger_analysis(field_id: str):
    """Internal: Trigger manual NDVI analysis"""
    field = ndvi_service.monitored_fields.get(field_id)
    if not field:
        return {"error": "Field not found"}, 404
    
    await ndvi_service._analyze_field(field_id, field)
    return {"message": f"Analysis triggered for {field_id}"}


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("NDVI_PORT", "8085")),
        reload=os.getenv("ENV") == "development"
    )
