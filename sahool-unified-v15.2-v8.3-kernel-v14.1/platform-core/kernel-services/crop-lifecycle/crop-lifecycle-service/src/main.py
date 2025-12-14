"""
Crop Lifecycle Service (خدمة دورة حياة المحصول)
Layer 3: Decision Service

مسؤول عن:
1. تتبع مراحل نمو المحصول
2. تحليل الإشارات من Layer 2 (astro, weather, ndvi)
3. توليد توصيات زراعية ذكية
4. ربط التقويم الفلكي بالمحصول

Events Consumed:
- astro.star.rising
- weather.daily.summary
- weather.anomaly.detected
- ndvi.processed
- ndvi.anomaly.detected

Events Published:
- crop.stage.changed
- crop.action.recommended
- crop.harvest.ready
"""

import os
import sys
import json
import asyncio
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import uvicorn
import nats

sys.path.insert(0, '/app')
from shared.events.base_event import create_event, EventTypes  # noqa: E402
from shared.utils.logging import configure_logging, get_logger, EventLogger  # noqa: E402
from shared.metrics import (  # noqa: E402
    EVENTS_PUBLISHED, EVENTS_CONSUMED,
    init_service_info, get_metrics, get_metrics_content_type
)
)

configure_logging(service_name="crop-lifecycle-service")
logger = get_logger(__name__)
event_logger = EventLogger("crop-lifecycle-service")

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "crop-lifecycle-service"
SERVICE_LAYER = "decision"


# ============================================
# Data Models
# ============================================

class CropStage(str, Enum):
    PREPARATION = "تجهيز"
    SOWING = "بذر"
    GERMINATION = "إنبات"
    VEGETATIVE = "نمو خضري"
    FLOWERING = "إزهار"
    FRUITING = "إثمار"
    MATURATION = "نضج"
    HARVEST = "حصاد"
    DORMANT = "سكون"


class ActionType(str, Enum):
    PLOW = "حرث"
    SOW = "بذر"
    IRRIGATE = "ري"
    FERTILIZE = "تسميد"
    PRUNE = "تقليم"
    SPRAY = "رش"
    WEED = "تعشيب"
    HARVEST = "حصاد"
    MONITOR = "مراقبة"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class CropPlanting:
    """Crop planting record"""
    id: str
    field_id: str
    tenant_id: str
    crop_type: str
    variety: Optional[str]
    planting_date: str
    expected_harvest_date: Optional[str]
    current_stage: str
    stage_started_at: str
    health_score: float = 0.7
    notes: Optional[str] = None
    
    def days_in_stage(self) -> int:
        started = datetime.fromisoformat(self.stage_started_at)
        return (datetime.utcnow() - started).days
    
    def days_since_planting(self) -> int:
        planted = datetime.fromisoformat(self.planting_date)
        return (datetime.utcnow() - planted).days
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ActionRecommendation:
    """Agricultural action recommendation"""
    crop_planting_id: str
    field_id: str
    action_type: str
    priority: str
    reason: str
    reason_ar: str
    deadline: Optional[str]
    source_event: str
    source_signal: str  # astro, weather, ndvi
    proverb_reference: Optional[str] = None
    estimated_duration_hours: Optional[float] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


# ============================================
# Crop Knowledge Base
# ============================================

class CropKnowledgeBase:
    """Agricultural knowledge base for Yemen crops"""
    
    # Crop lifecycle definitions (days per stage)
    CROP_STAGES = {
        "ذرة": {
            CropStage.SOWING: 0,
            CropStage.GERMINATION: 7,
            CropStage.VEGETATIVE: 21,
            CropStage.FLOWERING: 60,
            CropStage.FRUITING: 75,
            CropStage.MATURATION: 100,
            CropStage.HARVEST: 120,
        },
        "قمح": {
            CropStage.SOWING: 0,
            CropStage.GERMINATION: 10,
            CropStage.VEGETATIVE: 25,
            CropStage.FLOWERING: 70,
            CropStage.FRUITING: 90,
            CropStage.MATURATION: 110,
            CropStage.HARVEST: 130,
        },
        "بن": {
            CropStage.VEGETATIVE: 0,
            CropStage.FLOWERING: 90,
            CropStage.FRUITING: 180,
            CropStage.MATURATION: 270,
            CropStage.HARVEST: 300,
            CropStage.DORMANT: 330,
        },
        "قات": {
            CropStage.VEGETATIVE: 0,
            CropStage.HARVEST: 90,  # Continuous harvest
        },
        "طماطم": {
            CropStage.SOWING: 0,
            CropStage.GERMINATION: 10,
            CropStage.VEGETATIVE: 30,
            CropStage.FLOWERING: 50,
            CropStage.FRUITING: 70,
            CropStage.HARVEST: 90,
        },
    }
    
    # Star to crop action mappings (from traditional knowledge)
    STAR_ACTIONS = {
        "star_alab": {  # العلب
            "ذرة": [
                ActionRecommendation(
                    crop_planting_id="",
                    field_id="",
                    action_type=ActionType.IRRIGATE.value,
                    priority=Priority.HIGH.value,
                    reason="Al-Alab star indicates critical irrigation period",
                    reason_ar="نجم العلب يدل على فترة ري حرجة - الذرة تحتاج ماء في هذه الفترة",
                    deadline=None,
                    source_event="astro.star.rising",
                    source_signal="astro",
                    proverb_reference="ما قيظ إلا قيظ العلب"
                ),
            ],
            "قمح": [
                ActionRecommendation(
                    crop_planting_id="",
                    field_id="",
                    action_type=ActionType.PLOW.value,
                    priority=Priority.HIGH.value,
                    reason="Prepare land during Al-Alab for wheat sowing",
                    reason_ar="تجهيز الأرض للقمح في فترة العلب",
                    deadline=None,
                    source_event="astro.star.rising",
                    source_signal="astro",
                    proverb_reference="ثورك والعلب"
                ),
            ],
        },
        "star_thuraiya": {  # الثريا
            "بن": [
                ActionRecommendation(
                    crop_planting_id="",
                    field_id="",
                    action_type=ActionType.PRUNE.value,
                    priority=Priority.MEDIUM.value,
                    reason="Thuraiya rising marks coffee pruning season",
                    reason_ar="طلوع الثريا موسم تقليم البن",
                    deadline=None,
                    source_event="astro.star.rising",
                    source_signal="astro",
                    proverb_reference=None
                ),
            ],
        },
    }
    
    # Weather-based actions
    WEATHER_ACTIONS = {
        "heavy_precipitation": {
            ActionType.MONITOR: {
                "reason_ar": "مراقبة الحقول بعد الأمطار الغزيرة للتحقق من التصريف",
                "priority": Priority.HIGH
            },
        },
        "high_temperature": {
            ActionType.IRRIGATE: {
                "reason_ar": "ري عاجل بسبب ارتفاع درجة الحرارة",
                "priority": Priority.URGENT
            },
        },
        "strong_wind": {
            ActionType.MONITOR: {
                "reason_ar": "فحص المحاصيل بعد الرياح القوية",
                "priority": Priority.HIGH
            },
        },
    }
    
    @classmethod
    def get_expected_stage(cls, crop_type: str, days_since_planting: int) -> CropStage:
        """Determine expected crop stage based on days since planting"""
        stages = cls.CROP_STAGES.get(crop_type, cls.CROP_STAGES["ذرة"])
        
        current_stage = CropStage.SOWING
        for stage, start_day in sorted(stages.items(), key=lambda x: x[1]):
            if days_since_planting >= start_day:
                current_stage = stage
        
        return current_stage
    
    @classmethod
    def get_star_actions(cls, star_id: str, crop_type: str) -> List[ActionRecommendation]:
        """Get recommended actions for a star/crop combination"""
        star_actions = cls.STAR_ACTIONS.get(star_id, {})
        return star_actions.get(crop_type, [])
    
    @classmethod
    def get_weather_actions(cls, anomaly_type: str) -> Dict:
        """Get recommended actions for weather anomaly"""
        return cls.WEATHER_ACTIONS.get(anomaly_type, {})


# ============================================
# Crop Lifecycle Engine
# ============================================

class CropLifecycleEngine:
    """Core decision engine for crop lifecycle management"""
    
    def __init__(self):
        # In-memory storage (use database in production)
        self.plantings: Dict[str, CropPlanting] = {}
        
        # Add sample data
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize sample crop plantings"""
        samples = [
            CropPlanting(
                id="planting_001",
                field_id="field_001",
                tenant_id="default",
                crop_type="ذرة",
                variety="محلي",
                planting_date=(date.today() - timedelta(days=45)).isoformat(),
                expected_harvest_date=(date.today() + timedelta(days=75)).isoformat(),
                current_stage=CropStage.VEGETATIVE.value,
                stage_started_at=(date.today() - timedelta(days=24)).isoformat(),
                health_score=0.75
            ),
            CropPlanting(
                id="planting_002",
                field_id="field_002",
                tenant_id="default",
                crop_type="بن",
                variety="يافعي",
                planting_date=(date.today() - timedelta(days=400)).isoformat(),
                expected_harvest_date=(date.today() + timedelta(days=60)).isoformat(),
                current_stage=CropStage.FRUITING.value,
                stage_started_at=(date.today() - timedelta(days=30)).isoformat(),
                health_score=0.8
            ),
            CropPlanting(
                id="planting_003",
                field_id="field_003",
                tenant_id="default",
                crop_type="قمح",
                variety="محسن",
                planting_date=(date.today() - timedelta(days=30)).isoformat(),
                expected_harvest_date=(date.today() + timedelta(days=100)).isoformat(),
                current_stage=CropStage.GERMINATION.value,
                stage_started_at=(date.today() - timedelta(days=5)).isoformat(),
                health_score=0.7
            ),
        ]
        
        for p in samples:
            self.plantings[p.id] = p
    
    def update_stage(self, planting_id: str) -> Optional[CropStage]:
        """Check and update crop stage if needed"""
        planting = self.plantings.get(planting_id)
        if not planting:
            return None
        
        days = planting.days_since_planting()
        expected_stage = CropKnowledgeBase.get_expected_stage(
            planting.crop_type, days
        )
        
        if expected_stage.value != planting.current_stage:
            old_stage = planting.current_stage
            planting.current_stage = expected_stage.value
            planting.stage_started_at = datetime.utcnow().isoformat()
            
            logger.info("crop_stage_changed",
                       planting_id=planting_id,
                       old_stage=old_stage,
                       new_stage=expected_stage.value)
            
            return expected_stage
        
        return None
    
    def process_star_event(self, star_data: dict) -> List[ActionRecommendation]:
        """Process astronomical calendar event"""
        star_id = star_data.get("star", {}).get("id", "")
        recommendations = []
        
        for planting_id, planting in self.plantings.items():
            actions = CropKnowledgeBase.get_star_actions(
                star_id, planting.crop_type
            )
            
            for action in actions:
                # Customize recommendation for this planting
                rec = ActionRecommendation(
                    crop_planting_id=planting_id,
                    field_id=planting.field_id,
                    action_type=action.action_type,
                    priority=action.priority,
                    reason=action.reason,
                    reason_ar=action.reason_ar,
                    deadline=(datetime.utcnow() + timedelta(days=3)).isoformat(),
                    source_event=action.source_event,
                    source_signal=action.source_signal,
                    proverb_reference=action.proverb_reference
                )
                recommendations.append(rec)
        
        return recommendations
    
    def process_weather_event(self, weather_data: dict) -> List[ActionRecommendation]:
        """Process weather event"""
        recommendations = []
        
        # Check for anomalies
        anomaly = weather_data.get("anomaly", {})
        if anomaly:
            anomaly_type = anomaly.get("anomaly_type", "")
            weather_data.get("region", "")
            
            actions = CropKnowledgeBase.get_weather_actions(anomaly_type)
            
            for planting_id, planting in self.plantings.items():
                # Match by region (simplified - in production use field location)
                for action_type, action_info in actions.items():
                    rec = ActionRecommendation(
                        crop_planting_id=planting_id,
                        field_id=planting.field_id,
                        action_type=action_type.value,
                        priority=action_info["priority"].value,
                        reason=f"Weather anomaly: {anomaly_type}",
                        reason_ar=action_info["reason_ar"],
                        deadline=(datetime.utcnow() + timedelta(hours=24)).isoformat(),
                        source_event="weather.anomaly.detected",
                        source_signal="weather"
                    )
                    recommendations.append(rec)
        
        return recommendations
    
    def process_ndvi_event(self, ndvi_data: dict) -> List[ActionRecommendation]:
        """Process NDVI analysis event"""
        recommendations = []
        
        field_id = ndvi_data.get("field", {}).get("id", "")
        ndvi = ndvi_data.get("ndvi", {})
        
        # Find planting for this field
        planting = next(
            (p for p in self.plantings.values() if p.field_id == field_id),
            None
        )
        
        if not planting:
            return recommendations
        
        # Update health score
        health_status = ndvi.get("health_status", "moderate")
        health_scores = {
            "dead": 0.1, "poor": 0.3, "moderate": 0.5,
            "healthy": 0.7, "excellent": 0.9
        }
        planting.health_score = health_scores.get(health_status, 0.5)
        
        # Generate recommendations based on NDVI
        ndvi_mean = ndvi.get("ndvi_mean", 0.5)
        
        if ndvi_mean < 0.35:
            recommendations.append(ActionRecommendation(
                crop_planting_id=planting.id,
                field_id=field_id,
                action_type=ActionType.IRRIGATE.value,
                priority=Priority.HIGH.value,
                reason="Low NDVI indicates possible water stress",
                reason_ar="مؤشر NDVI منخفض يدل على احتمال إجهاد مائي",
                deadline=(datetime.utcnow() + timedelta(hours=48)).isoformat(),
                source_event="ndvi.processed",
                source_signal="ndvi"
            ))
        
        if ndvi_mean < 0.25:
            recommendations.append(ActionRecommendation(
                crop_planting_id=planting.id,
                field_id=field_id,
                action_type=ActionType.FERTILIZE.value,
                priority=Priority.HIGH.value,
                reason="Very low NDVI may indicate nutrient deficiency",
                reason_ar="مؤشر NDVI منخفض جداً قد يدل على نقص العناصر الغذائية",
                deadline=(datetime.utcnow() + timedelta(days=3)).isoformat(),
                source_event="ndvi.processed",
                source_signal="ndvi"
            ))
        
        return recommendations
    
    def check_harvest_readiness(self, planting_id: str) -> bool:
        """Check if crop is ready for harvest"""
        planting = self.plantings.get(planting_id)
        if not planting:
            return False
        
        if planting.current_stage == CropStage.HARVEST.value:
            return True
        
        if planting.current_stage == CropStage.MATURATION.value:
            days_in_stage = planting.days_in_stage()
            if days_in_stage >= 14:  # 2 weeks in maturation
                return True
        
        return False
    
    def get_planting(self, planting_id: str) -> Optional[CropPlanting]:
        return self.plantings.get(planting_id)
    
    def get_plantings_by_tenant(self, tenant_id: str) -> List[CropPlanting]:
        return [p for p in self.plantings.values() if p.tenant_id == tenant_id]


# ============================================
# Crop Lifecycle Service
# ============================================

class CropLifecycleService:
    """Crop lifecycle decision service"""
    
    def __init__(self):
        self.nc = None
        self.js = None
        self.engine = CropLifecycleEngine()
        self.running = False
    
    async def connect(self):
        """Connect to NATS"""
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("crop_lifecycle_service_connected")
    
    async def start(self):
        """Start event processing"""
        self.running = True
        
        # Subscribe to signal producer events
        subscriptions = [
            ("astro.star.rising", self._handle_star_rising),
            ("weather.anomaly.detected", self._handle_weather_anomaly),
            ("ndvi.processed", self._handle_ndvi_processed),
            ("ndvi.anomaly.detected", self._handle_ndvi_anomaly),
        ]
        
        for subject, handler in subscriptions:
            try:
                sub = await self.js.pull_subscribe(
                    subject=subject,
                    durable=f"crop-lifecycle-{subject.replace('.', '-')}",
                    stream="SAHOOL"
                )
                asyncio.create_task(self._process_loop(sub, handler))
                logger.info("subscribed_to_event", subject=subject)
            except Exception as e:
                logger.warning("subscription_failed", subject=subject, error=str(e))
        
        # Start periodic stage updates
        asyncio.create_task(self._stage_update_loop())
        
        logger.info("crop_lifecycle_service_started")
    
    async def _process_loop(self, sub, handler):
        """Process events from subscription"""
        while self.running:
            try:
                messages = await sub.fetch(batch=10, timeout=1)
                for msg in messages:
                    try:
                        event_data = json.loads(msg.data.decode())
                        await handler(event_data)
                        await msg.ack()
                    except Exception as e:
                        logger.error("event_processing_failed", error=str(e))
                        await msg.nak()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("process_loop_error", error=str(e))
                await asyncio.sleep(1)
    
    async def _stage_update_loop(self):
        """Periodically check for stage transitions"""
        while self.running:
            for planting_id in list(self.engine.plantings.keys()):
                new_stage = self.engine.update_stage(planting_id)
                
                if new_stage:
                    planting = self.engine.get_planting(planting_id)
                    await self._publish_stage_change(planting, new_stage)
                    
                    # Check harvest readiness
                    if self.engine.check_harvest_readiness(planting_id):
                        await self._publish_harvest_ready(planting)
            
            await asyncio.sleep(3600)  # Check every hour
    
    async def _handle_star_rising(self, event_data: dict):
        """Handle astro.star.rising event"""
        event_logger.received("astro.star.rising")
        EVENTS_CONSUMED.labels(
            service=SERVICE_NAME,
            event_type="astro.star.rising",
            tenant_id=event_data.get("tenant_id", "default")
        ).inc()
        
        payload = event_data.get("payload", {})
        recommendations = self.engine.process_star_event(payload)
        
        for rec in recommendations:
            await self._publish_recommendation(rec, event_data.get("tenant_id", "default"))
    
    async def _handle_weather_anomaly(self, event_data: dict):
        """Handle weather.anomaly.detected event"""
        event_logger.received("weather.anomaly.detected")
        EVENTS_CONSUMED.labels(
            service=SERVICE_NAME,
            event_type="weather.anomaly.detected",
            tenant_id=event_data.get("tenant_id", "default")
        ).inc()
        
        payload = event_data.get("payload", {})
        recommendations = self.engine.process_weather_event(payload)
        
        for rec in recommendations:
            await self._publish_recommendation(rec, event_data.get("tenant_id", "default"))
    
    async def _handle_ndvi_processed(self, event_data: dict):
        """Handle ndvi.processed event"""
        event_logger.received("ndvi.processed")
        EVENTS_CONSUMED.labels(
            service=SERVICE_NAME,
            event_type="ndvi.processed",
            tenant_id=event_data.get("tenant_id", "default")
        ).inc()
        
        payload = event_data.get("payload", {})
        recommendations = self.engine.process_ndvi_event(payload)
        
        for rec in recommendations:
            await self._publish_recommendation(rec, event_data.get("tenant_id", "default"))
    
    async def _handle_ndvi_anomaly(self, event_data: dict):
        """Handle ndvi.anomaly.detected event"""
        event_logger.received("ndvi.anomaly.detected")
        EVENTS_CONSUMED.labels(
            service=SERVICE_NAME,
            event_type="ndvi.anomaly.detected",
            tenant_id=event_data.get("tenant_id", "default")
        ).inc()
        
        # NDVI anomalies are urgent
        payload = event_data.get("payload", {})
        field_id = payload.get("field", {}).get("id", "")
        anomaly = payload.get("anomaly", {})
        
        planting = next(
            (p for p in self.engine.plantings.values() if p.field_id == field_id),
            None
        )
        
        if planting:
            rec = ActionRecommendation(
                crop_planting_id=planting.id,
                field_id=field_id,
                action_type=ActionType.MONITOR.value,
                priority=Priority.URGENT.value,
                reason=f"NDVI anomaly detected: {anomaly.get('anomaly_type', 'unknown')}",
                reason_ar=anomaly.get("description_ar", "شذوذ مكتشف في صور الأقمار الصناعية"),
                deadline=(datetime.utcnow() + timedelta(hours=12)).isoformat(),
                source_event="ndvi.anomaly.detected",
                source_signal="ndvi"
            )
            await self._publish_recommendation(rec, event_data.get("tenant_id", "default"))
    
    async def _publish_recommendation(self, rec: ActionRecommendation, tenant_id: str):
        """Publish crop.action.recommended event"""
        event = create_event(
            event_type=EventTypes.CROP_ACTION_RECOMMENDED,
            payload=rec.to_dict(),
            tenant_id=tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.CROP_ACTION_RECOMMENDED,
            payload=json.dumps(event).encode()
        )
        
        EVENTS_PUBLISHED.labels(
            service=SERVICE_NAME,
            event_type=EventTypes.CROP_ACTION_RECOMMENDED,
            tenant_id=tenant_id
        ).inc()
        
        event_logger.published(
            EventTypes.CROP_ACTION_RECOMMENDED,
            action=rec.action_type,
            priority=rec.priority
        )
    
    async def _publish_stage_change(self, planting: CropPlanting, new_stage: CropStage):
        """Publish crop.stage.changed event"""
        event = create_event(
            event_type=EventTypes.CROP_STAGE_CHANGED,
            payload={
                "planting": planting.to_dict(),
                "new_stage": new_stage.value,
                "days_since_planting": planting.days_since_planting()
            },
            tenant_id=planting.tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.CROP_STAGE_CHANGED,
            payload=json.dumps(event).encode()
        )
        
        event_logger.published(EventTypes.CROP_STAGE_CHANGED, stage=new_stage.value)
    
    async def _publish_harvest_ready(self, planting: CropPlanting):
        """Publish crop.harvest.ready event"""
        event = create_event(
            event_type=EventTypes.CROP_HARVEST_READY,
            payload={
                "planting": planting.to_dict(),
                "days_since_planting": planting.days_since_planting(),
                "health_score": planting.health_score
            },
            tenant_id=planting.tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.CROP_HARVEST_READY,
            payload=json.dumps(event).encode()
        )
        
        event_logger.published(EventTypes.CROP_HARVEST_READY, crop=planting.crop_type)
    
    async def stop(self):
        """Stop service"""
        self.running = False
        if self.nc:
            await self.nc.close()
        logger.info("crop_lifecycle_service_stopped")


# ============================================
# Global Instance
# ============================================

service = CropLifecycleService()


# ============================================
# FastAPI Application
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", layer=SERVICE_LAYER)
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    
    await service.connect()
    await service.start()
    
    logger.info("service_started")
    yield
    
    await service.stop()
    logger.info("service_stopped")


app = FastAPI(
    title="Crop Lifecycle Service",
    description="SAHOOL Platform - Crop Decision Engine",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    connected = service.nc is not None
    return {"status": "ready" if connected else "not_ready"}


@app.get("/metrics")
async def metrics():
    return Response(content=get_metrics(), media_type=get_metrics_content_type())


# Layer 3 can have API endpoints for queries
@app.get("/api/plantings")
async def list_plantings(tenant_id: str = "default"):
    """List crop plantings for a tenant"""
    plantings = service.engine.get_plantings_by_tenant(tenant_id)
    return {"plantings": [p.to_dict() for p in plantings]}


@app.get("/api/plantings/{planting_id}")
async def get_planting(planting_id: str):
    """Get specific planting details"""
    planting = service.engine.get_planting(planting_id)
    if not planting:
        raise HTTPException(404, "Planting not found")
    return planting.to_dict()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8086")),
        reload=os.getenv("ENV") == "development"
    )
