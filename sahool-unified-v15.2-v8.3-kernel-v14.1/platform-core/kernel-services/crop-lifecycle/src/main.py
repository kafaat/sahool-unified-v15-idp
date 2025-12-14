"""
Crop Lifecycle Service - Decision Service
Layer 3: Decision Service

خدمة دورة حياة المحصول - صانع القرار
تستقبل إشارات من Layer 2 وتحلل مراحل المحصول وتصدر توصيات

Responsibilities:
1. Subscribe to astro, weather, and NDVI events
2. Track crop growth stages per field
3. Analyze signals and determine actions
4. Publish crop recommendations and stage changes
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import nats

sys.path.insert(0, "/app")
from shared.events.base_event import EventTypes, create_event
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.metrics import (
    EVENTS_PUBLISHED,
    EVENTS_CONSUMED,
    init_service_info,
    get_metrics,
    get_metrics_content_type,
)

configure_logging(service_name="crop-lifecycle")
logger = get_logger(__name__)
event_logger = EventLogger("crop-lifecycle")

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "crop-lifecycle"
SERVICE_LAYER = "decision"


class CropStage(str, Enum):
    SEED = "بذر"
    GERMINATION = "إنبات"
    VEGETATIVE = "نمو_خضري"
    FLOWERING = "إزهار"
    FRUITING = "إثمار"
    MATURATION = "نضج"
    HARVEST = "حصاد"
    DORMANT = "سكون"


class ActionType(str, Enum):
    PLANTING = "زراعة"
    IRRIGATION = "ري"
    FERTILIZATION = "تسميد"
    PEST_CONTROL = "مكافحة_آفات"
    PRUNING = "تقليم"
    HARVESTING = "حصاد"
    MONITORING = "مراقبة"
    SOIL_PREP = "تحضير_تربة"


class ActionPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class CropPlanting:
    field_id: str
    crop_type: str
    variety: str
    planted_at: datetime
    current_stage: CropStage
    days_in_stage: int
    expected_harvest: datetime
    health_score: float
    last_updated: datetime
    tenant_id: str

    def to_dict(self) -> dict:
        return {
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "variety": self.variety,
            "planted_at": self.planted_at.isoformat(),
            "current_stage": self.current_stage.value,
            "days_in_stage": self.days_in_stage,
            "expected_harvest": self.expected_harvest.isoformat(),
            "health_score": round(self.health_score, 2),
            "last_updated": self.last_updated.isoformat(),
            "tenant_id": self.tenant_id,
        }


@dataclass
class CropRecommendation:
    field_id: str
    crop_type: str
    action: ActionType
    priority: ActionPriority
    description_ar: str
    reason_ar: str
    deadline: Optional[datetime]
    source_signal: str
    proverb_reference: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "action": self.action.value,
            "priority": self.priority.value,
            "description_ar": self.description_ar,
            "reason_ar": self.reason_ar,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "source_signal": self.source_signal,
            "proverb_reference": self.proverb_reference,
        }


STAR_CROP_ACTIONS = {
    "star_alab": {
        "sorghum": {
            "action": ActionType.SOIL_PREP,
            "description_ar": "حرث الجنيد استعداداً للزراعة",
            "proverb": "ثورك والعلب",
        },
        "wheat": {
            "action": ActionType.MONITORING,
            "description_ar": "مراقبة نمو القمح",
            "proverb": None,
        },
    },
    "star_saal": {
        "wheat": {
            "action": ActionType.PLANTING,
            "description_ar": "بدء زراعة القمح",
            "proverb": "سعل الضان والخضار",
        }
    },
    "star_batn_hoot": {
        "coffee": {
            "action": ActionType.HARVESTING,
            "description_ar": "بدء موسم حصاد البن",
            "proverb": None,
        }
    },
    "star_sharatain": {
        "vegetables": {
            "action": ActionType.PLANTING,
            "description_ar": "زراعة الخضروات الشتوية",
            "proverb": "الشرط زراعة",
        }
    },
}


class CropStateManager:
    def __init__(self):
        self.plantings: Dict[str, CropPlanting] = {}
        self.history: Dict[str, List[dict]] = {}

    def add_planting(self, planting: CropPlanting):
        self.plantings[planting.field_id] = planting
        self.history.setdefault(planting.field_id, []).append(
            {
                "stage": planting.current_stage.value,
                "timestamp": datetime.utcnow().isoformat(),
                "health_score": planting.health_score,
            }
        )

    def get_planting(self, field_id: str) -> Optional[CropPlanting]:
        return self.plantings.get(field_id)

    def update_health(self, field_id: str, health_score: float):
        planting = self.plantings.get(field_id)
        if planting:
            planting.health_score = health_score
            planting.last_updated = datetime.utcnow()

    def get_fields_by_crop(self, crop_type: str) -> List[CropPlanting]:
        return [p for p in self.plantings.values() if p.crop_type == crop_type]


class CropDecisionEngine:
    def __init__(self, state_manager: CropStateManager):
        self.state = state_manager

    def process_star_rising(self, event_data: dict) -> List[CropRecommendation]:
        recommendations = []
        payload = event_data.get("payload", {})
        star = payload.get("star", {})
        star_id = star.get("id", "")

        star_actions = STAR_CROP_ACTIONS.get(star_id, {})

        for crop_type, action_info in star_actions.items():
            fields = self.state.get_fields_by_crop(crop_type)
            for planting in fields:
                recommendation = CropRecommendation(
                    field_id=planting.field_id,
                    crop_type=crop_type,
                    action=action_info["action"],
                    priority=ActionPriority.HIGH,
                    description_ar=action_info["description_ar"],
                    reason_ar=f"بناءً على طلوع نجم {star.get('name_ar', '')}",
                    deadline=datetime.utcnow() + timedelta(days=7),
                    source_signal=EventTypes.ASTRO_STAR_RISING,
                    proverb_reference=action_info.get("proverb"),
                )
                recommendations.append(recommendation)

        return recommendations

    def process_weather_anomaly(self, event_data: dict) -> List[CropRecommendation]:
        recommendations = []
        payload = event_data.get("payload", {})
        anomaly = payload.get("anomaly", {})
        anomaly_type = anomaly.get("type", "")
        severity = anomaly.get("severity", "medium")

        affected_fields = list(self.state.plantings.values())

        for planting in affected_fields:
            if anomaly_type == "drought":
                recommendations.append(
                    CropRecommendation(
                        field_id=planting.field_id,
                        crop_type=planting.crop_type,
                        action=ActionType.IRRIGATION,
                        priority=(
                            ActionPriority.URGENT
                            if severity in ["high", "critical"]
                            else ActionPriority.HIGH
                        ),
                        description_ar="زيادة الري بسبب الجفاف",
                        reason_ar=anomaly.get("description_ar", "تحذير جفاف"),
                        deadline=datetime.utcnow() + timedelta(days=1),
                        source_signal=EventTypes.WEATHER_ANOMALY_DETECTED,
                    )
                )
            elif anomaly_type == "frost":
                recommendations.append(
                    CropRecommendation(
                        field_id=planting.field_id,
                        crop_type=planting.crop_type,
                        action=ActionType.MONITORING,
                        priority=ActionPriority.URGENT,
                        description_ar="تغطية المحاصيل من الصقيع",
                        reason_ar=anomaly.get("description_ar", "تحذير صقيع"),
                        deadline=datetime.utcnow() + timedelta(hours=6),
                        source_signal=EventTypes.WEATHER_ANOMALY_DETECTED,
                    )
                )
            elif anomaly_type == "humidity_high":
                recommendations.append(
                    CropRecommendation(
                        field_id=planting.field_id,
                        crop_type=planting.crop_type,
                        action=ActionType.PEST_CONTROL,
                        priority=ActionPriority.HIGH,
                        description_ar="مراقبة الأمراض الفطرية",
                        reason_ar="رطوبة عالية تزيد خطر الأمراض",
                        deadline=datetime.utcnow() + timedelta(days=2),
                        source_signal=EventTypes.WEATHER_ANOMALY_DETECTED,
                    )
                )

        return recommendations

    def process_ndvi_anomaly(self, event_data: dict) -> List[CropRecommendation]:
        recommendations = []
        payload = event_data.get("payload", {})
        field = payload.get("field", {})
        field_id = field.get("id", "")
        anomaly = payload.get("anomaly", {})
        anomaly_type = anomaly.get("type", "")
        severity = anomaly.get("severity", "medium")

        planting = self.state.get_planting(field_id)
        if not planting:
            return recommendations

        if anomaly_type == "water_stress":
            recommendations.append(
                CropRecommendation(
                    field_id=field_id,
                    crop_type=planting.crop_type,
                    action=ActionType.IRRIGATION,
                    priority=(
                        ActionPriority.URGENT
                        if severity == "critical"
                        else ActionPriority.HIGH
                    ),
                    description_ar="إجهاد مائي - زيادة الري فوراً",
                    reason_ar=anomaly.get("description_ar", ""),
                    deadline=datetime.utcnow() + timedelta(days=1),
                    source_signal=EventTypes.NDVI_ANOMALY_DETECTED,
                )
            )
        elif anomaly_type == "disease_suspected":
            recommendations.append(
                CropRecommendation(
                    field_id=field_id,
                    crop_type=planting.crop_type,
                    action=ActionType.MONITORING,
                    priority=ActionPriority.URGENT,
                    description_ar="اشتباه مرض - فحص ميداني عاجل",
                    reason_ar=anomaly.get("description_ar", ""),
                    deadline=datetime.utcnow() + timedelta(hours=24),
                    source_signal=EventTypes.NDVI_ANOMALY_DETECTED,
                )
            )

        return recommendations


class CropLifecycleService:
    def __init__(self):
        self.nc = None
        self.js = None
        self.state_manager = CropStateManager()
        self.decision_engine = CropDecisionEngine(self.state_manager)
        self.running = False

    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("nats_connected")

    async def start(self):
        self.running = True
        self._add_sample_plantings()

        subscriptions = [
            (EventTypes.ASTRO_STAR_RISING, "crop-astro"),
            (EventTypes.WEATHER_ANOMALY_DETECTED, "crop-weather"),
            (EventTypes.NDVI_ANOMALY_DETECTED, "crop-ndvi"),
        ]

        for subject, durable in subscriptions:
            try:
                sub = await self.js.pull_subscribe(
                    subject=subject, durable=durable, stream="SAHOOL"
                )
                asyncio.create_task(self._process_events(sub, subject))
            except Exception as e:
                logger.warning("subscription_failed", subject=subject, error=str(e))

        logger.info("crop_lifecycle_started")

    def _add_sample_plantings(self):
        samples = [
            CropPlanting(
                "field_001",
                "wheat",
                "محلي",
                datetime.utcnow() - timedelta(days=45),
                CropStage.VEGETATIVE,
                15,
                datetime.utcnow() + timedelta(days=90),
                0.75,
                datetime.utcnow(),
                "default",
            ),
            CropPlanting(
                "field_002",
                "coffee",
                "بني يمني",
                datetime.utcnow() - timedelta(days=365),
                CropStage.FRUITING,
                60,
                datetime.utcnow() + timedelta(days=60),
                0.85,
                datetime.utcnow(),
                "default",
            ),
            CropPlanting(
                "field_003",
                "sorghum",
                "ذرة بيضاء",
                datetime.utcnow() - timedelta(days=30),
                CropStage.GERMINATION,
                10,
                datetime.utcnow() + timedelta(days=120),
                0.80,
                datetime.utcnow(),
                "default",
            ),
        ]
        for p in samples:
            self.state_manager.add_planting(p)
        logger.info("sample_plantings_added", count=len(samples))

    async def _process_events(self, sub, subject: str):
        while self.running:
            try:
                messages = await sub.fetch(batch=10, timeout=1)
                for msg in messages:
                    await self._handle_event(msg, subject)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("event_processing_error", error=str(e))
                await asyncio.sleep(1)

    async def _handle_event(self, msg, subject: str):
        try:
            event_data = json.loads(msg.data.decode())
            event_type = event_data.get("event_type", subject)

            EVENTS_CONSUMED.labels(
                service=SERVICE_NAME, event_type=event_type, tenant_id="default"
            ).inc()
            event_logger.received(event_type, event_id=event_data.get("event_id"))

            recommendations = []
            if event_type == EventTypes.ASTRO_STAR_RISING:
                recommendations = self.decision_engine.process_star_rising(event_data)
            elif event_type == EventTypes.WEATHER_ANOMALY_DETECTED:
                recommendations = self.decision_engine.process_weather_anomaly(
                    event_data
                )
            elif event_type == EventTypes.NDVI_ANOMALY_DETECTED:
                recommendations = self.decision_engine.process_ndvi_anomaly(event_data)

            for rec in recommendations:
                await self._publish_recommendation(
                    rec, event_data.get("correlation_id")
                )

            await msg.ack()
        except Exception as e:
            logger.error("event_handling_failed", error=str(e))
            await msg.nak()

    async def _publish_recommendation(
        self, rec: CropRecommendation, correlation_id: str = None
    ):
        event = create_event(
            event_type=EventTypes.CROP_ACTION_RECOMMENDED,
            payload=rec.to_dict(),
            tenant_id="default",
            correlation_id=correlation_id,
        )
        await self.js.publish(
            subject=EventTypes.CROP_ACTION_RECOMMENDED,
            payload=json.dumps(event, ensure_ascii=False).encode(),
        )
        EVENTS_PUBLISHED.labels(
            service=SERVICE_NAME,
            event_type=EventTypes.CROP_ACTION_RECOMMENDED,
            tenant_id="default",
        ).inc()
        event_logger.published(
            EventTypes.CROP_ACTION_RECOMMENDED, event_id=event["event_id"]
        )
        logger.info(
            "recommendation_published", field_id=rec.field_id, action=rec.action.value
        )

    async def stop(self):
        self.running = False
        if self.nc:
            await self.nc.close()


crop_service = CropLifecycleService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", layer=SERVICE_LAYER)
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await crop_service.connect()
    await crop_service.start()
    logger.info("service_started")
    yield
    await crop_service.stop()


app = FastAPI(title="Crop Lifecycle Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    return {
        "status": (
            "ready" if crop_service.nc and crop_service.nc.is_connected else "not_ready"
        )
    }


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response

    return Response(content=get_metrics(), media_type=get_metrics_content_type())


@app.get("/api/plantings")
async def list_plantings():
    return {
        "plantings": [
            p.to_dict() for p in crop_service.state_manager.plantings.values()
        ]
    }


@app.get("/api/plantings/{field_id}")
async def get_planting(field_id: str):
    p = crop_service.state_manager.get_planting(field_id)
    if not p:
        raise HTTPException(404, "Planting not found")
    return p.to_dict()


class AddPlantingRequest(BaseModel):
    field_id: str
    crop_type: str
    variety: str
    tenant_id: str = "default"


@app.post("/api/plantings")
async def add_planting(request: AddPlantingRequest):
    planting = CropPlanting(
        request.field_id,
        request.crop_type,
        request.variety,
        datetime.utcnow(),
        CropStage.SEED,
        0,
        datetime.utcnow() + timedelta(days=120),
        1.0,
        datetime.utcnow(),
        request.tenant_id,
    )
    crop_service.state_manager.add_planting(planting)
    return {"message": "Planting added", "planting": planting.to_dict()}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("CROP_LIFECYCLE_PORT", "8086")),
        reload=os.getenv("ENV") == "development",
    )
