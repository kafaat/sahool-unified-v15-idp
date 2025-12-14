"""
Process Manager Service (Saga Engine)
Layer 1: Platform Core

المسؤول عن تنسيق العمليات متعددة الخطوات (Sagas)
Orchestrates multi-step workflows across services

Key Responsibilities:
1. Subscribe to domain events
2. Maintain saga state
3. Publish coordination events
4. Handle compensation on failure
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from enum import Enum
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import nats
from nats.js.api import StreamConfig, ConsumerConfig, DeliverPolicy, AckPolicy

# Add shared to path
sys.path.insert(0, "/app")
from shared.events.base_event import Event, create_event
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.metrics import EVENTS_PROCESSED, SAGAS_ACTIVE, SAGAS_COMPLETED, SAGAS_FAILED

# Configure logging
configure_logging(service_name="process-manager")
logger = get_logger(__name__)
event_logger = EventLogger("process-manager")

# Configuration
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "process-manager"
SERVICE_LAYER = "platform-core"


# ============================================
# Saga Definitions
# ============================================


class SagaStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"


@dataclass
class SagaStep:
    """Single step in a saga"""

    name: str
    trigger_event: str
    success_event: str
    failure_event: Optional[str] = None
    compensation_event: Optional[str] = None
    timeout_seconds: int = 300


@dataclass
class SagaDefinition:
    """Complete saga workflow definition"""

    saga_type: str
    description: str
    steps: List[SagaStep]

    def to_dict(self) -> dict:
        return {
            "saga_type": self.saga_type,
            "description": self.description,
            "steps": [asdict(s) for s in self.steps],
        }


# Pre-defined Sagas
SAGA_DEFINITIONS: Dict[str, SagaDefinition] = {
    "star_rising_to_task": SagaDefinition(
        saga_type="star_rising_to_task",
        description="عند طلوع نجم → تحليل المحصول → إنشاء مهام",
        steps=[
            SagaStep(
                name="process_star_rising",
                trigger_event="astro.star.rising",
                success_event="crop.action.recommended",
                failure_event="saga.step.failed",
            ),
            SagaStep(
                name="create_task",
                trigger_event="crop.action.recommended",
                success_event="task.created",
                failure_event="saga.step.failed",
                compensation_event="task.cancelled",
            ),
            SagaStep(
                name="send_alert",
                trigger_event="task.created",
                success_event="alert.sent",
                failure_event="saga.step.failed",
            ),
        ],
    ),
    "weather_anomaly_response": SagaDefinition(
        saga_type="weather_anomaly_response",
        description="عند رصد شذوذ مناخي → تقييم المخاطر → تنبيه عاجل",
        steps=[
            SagaStep(
                name="assess_risk",
                trigger_event="weather.anomaly.detected",
                success_event="disease.risk.calculated",
                failure_event="saga.step.failed",
            ),
            SagaStep(
                name="urgent_alert",
                trigger_event="disease.risk.calculated",
                success_event="alert.sent",
                failure_event="saga.step.failed",
            ),
        ],
    ),
}


# ============================================
# Saga State Management (JetStream KV)
# ============================================


class SagaStateStore:
    """Manages saga state in NATS JetStream KV"""

    BUCKET_NAME = "saga_states"

    def __init__(self, js):
        self.js = js
        self.kv = None

    async def initialize(self):
        """Create or get KV bucket"""
        try:
            self.kv = await self.js.key_value(self.BUCKET_NAME)
            logger.info("kv_bucket_connected", bucket=self.BUCKET_NAME)
        except Exception:
            self.kv = await self.js.create_key_value(
                bucket=self.BUCKET_NAME, history=5, ttl=86400 * 7  # 7 days
            )
            logger.info("kv_bucket_created", bucket=self.BUCKET_NAME)

    async def save(self, saga_id: str, state: dict):
        """Save saga state"""
        await self.kv.put(saga_id, json.dumps(state).encode())
        logger.debug("saga_state_saved", saga_id=saga_id)

    async def get(self, saga_id: str) -> Optional[dict]:
        """Get saga state"""
        try:
            entry = await self.kv.get(saga_id)
            return json.loads(entry.value.decode())
        except Exception:
            return None

    async def delete(self, saga_id: str):
        """Delete saga state"""
        await self.kv.delete(saga_id)


# ============================================
# Process Manager Core
# ============================================


class ProcessManager:
    """Core saga orchestration engine"""

    def __init__(self):
        self.nc = None
        self.js = None
        self.state_store = None
        self.running = False

    async def connect(self):
        """Connect to NATS and initialize"""
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()

        # Initialize state store
        self.state_store = SagaStateStore(self.js)
        await self.state_store.initialize()

        # Ensure streams exist
        await self._ensure_streams()

        logger.info("process_manager_connected")

    async def _ensure_streams(self):
        """Ensure required streams exist"""
        # Main stream
        try:
            await self.js.add_stream(
                name="SAHOOL",
                subjects=[
                    "astro.*.*",
                    "weather.*.*",
                    "ndvi.*.*",
                    "crop.*.*",
                    "disease.*.*",
                    "irrigation.*.*",
                    "task.*",
                    "alert.*",
                    "saga.*.*",
                ],
                retention="limits",
                max_msgs=1000000,
                max_age=86400 * 7 * 1e9,  # 7 days in nanoseconds
            )
            logger.info("stream_created", stream="SAHOOL")
        except Exception as e:
            if "already" not in str(e).lower():
                logger.warning("stream_exists", stream="SAHOOL")

        # DLQ Stream
        try:
            await self.js.add_stream(
                name="SAHOOL_DLQ",
                subjects=["dlq.*"],
                retention="limits",
                max_msgs=100000,
                max_age=86400 * 30 * 1e9,  # 30 days
            )
            logger.info("stream_created", stream="SAHOOL_DLQ")
        except Exception:
            logger.warning("stream_exists", stream="SAHOOL_DLQ")

    async def start(self):
        """Start processing events"""
        self.running = True

        # Subscribe to saga trigger events
        trigger_subjects = set()
        for saga_def in SAGA_DEFINITIONS.values():
            for step in saga_def.steps:
                trigger_subjects.add(step.trigger_event)

        for subject in trigger_subjects:
            sub = await self.js.pull_subscribe(
                subject=subject,
                durable=f"pm-{subject.replace('.', '-')}",
                stream="SAHOOL",
            )
            asyncio.create_task(self._process_loop(sub, subject))

        logger.info("process_manager_started", subjects=list(trigger_subjects))

    async def _process_loop(self, sub, subject: str):
        """Process events from subscription"""
        while self.running:
            try:
                messages = await sub.fetch(batch=10, timeout=1)
                for msg in messages:
                    await self._handle_event(msg)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("process_loop_error", error=str(e), subject=subject)
                await asyncio.sleep(1)

    async def _handle_event(self, msg):
        """Handle incoming event"""
        try:
            event_data = json.loads(msg.data.decode())
            event_type = event_data.get("event_type", msg.subject)

            logger.info("event_received", event_type=event_type)
            EVENTS_PROCESSED.labels(service=SERVICE_NAME, event_type=event_type).inc()

            # Find matching saga
            for saga_type, saga_def in SAGA_DEFINITIONS.items():
                for i, step in enumerate(saga_def.steps):
                    if step.trigger_event == event_type:
                        await self._execute_saga_step(saga_def, i, event_data)

            await msg.ack()

        except Exception as e:
            logger.error("event_handling_failed", error=str(e))
            await msg.nak()

    async def _execute_saga_step(
        self, saga_def: SagaDefinition, step_index: int, event_data: dict
    ):
        """Execute a saga step"""
        step = saga_def.steps[step_index]
        saga_id = event_data.get("correlation_id") or event_data.get("event_id")

        # Load or create saga state
        state = await self.state_store.get(saga_id)
        if not state:
            state = {
                "saga_id": saga_id,
                "saga_type": saga_def.saga_type,
                "status": SagaStatus.RUNNING.value,
                "current_step": step_index,
                "started_at": datetime.utcnow().isoformat(),
                "events": [event_data],
                "tenant_id": event_data.get("tenant_id", "default"),
            }
            SAGAS_ACTIVE.labels(saga_type=saga_def.saga_type).inc()
        else:
            state["current_step"] = step_index
            state["events"].append(event_data)

        # Check if saga completed
        if step_index == len(saga_def.steps) - 1:
            state["status"] = SagaStatus.COMPLETED.value
            state["completed_at"] = datetime.utcnow().isoformat()
            SAGAS_ACTIVE.labels(saga_type=saga_def.saga_type).dec()
            SAGAS_COMPLETED.labels(saga_type=saga_def.saga_type).inc()
            logger.info("saga_completed", saga_id=saga_id, saga_type=saga_def.saga_type)

        await self.state_store.save(saga_id, state)

        # Publish success event to trigger next step
        if step.success_event and state["status"] != SagaStatus.COMPLETED.value:
            next_event = create_event(
                event_type=step.success_event,
                payload=event_data.get("payload", {}),
                tenant_id=state["tenant_id"],
                correlation_id=saga_id,
            )
            await self.js.publish(
                subject=step.success_event, payload=json.dumps(next_event).encode()
            )
            event_logger.published(step.success_event, event_id=next_event["event_id"])

    async def stop(self):
        """Stop processing"""
        self.running = False
        if self.nc:
            await self.nc.close()
        logger.info("process_manager_stopped")


# ============================================
# Global Instance
# ============================================

pm = ProcessManager()


# ============================================
# FastAPI Application
# ============================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info("service_starting", layer=SERVICE_LAYER)

    await pm.connect()
    await pm.start()

    logger.info("service_started")
    yield

    await pm.stop()
    logger.info("service_stopped")


app = FastAPI(
    title="Process Manager",
    description="SAHOOL Platform - Saga Orchestration Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# API Endpoints
# ============================================


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    connected = pm.nc is not None and pm.nc.is_connected
    return {"status": "ready" if connected else "not_ready"}


@app.get("/api/sagas")
async def list_saga_definitions():
    """List all saga definitions"""
    return {"sagas": [s.to_dict() for s in SAGA_DEFINITIONS.values()]}


@app.get("/api/sagas/{saga_id}")
async def get_saga_state(saga_id: str):
    """Get saga state by ID"""
    state = await pm.state_store.get(saga_id)
    if not state:
        raise HTTPException(404, "Saga not found")
    return state


class TriggerSagaRequest(BaseModel):
    saga_type: str
    payload: dict
    tenant_id: str = "default"


@app.post("/api/sagas/trigger")
async def trigger_saga(request: TriggerSagaRequest):
    """Manually trigger a saga (for testing)"""
    if request.saga_type not in SAGA_DEFINITIONS:
        raise HTTPException(400, f"Unknown saga type: {request.saga_type}")

    saga_def = SAGA_DEFINITIONS[request.saga_type]
    first_step = saga_def.steps[0]

    event = create_event(
        event_type=first_step.trigger_event,
        payload=request.payload,
        tenant_id=request.tenant_id,
    )

    await pm.js.publish(
        subject=first_step.trigger_event, payload=json.dumps(event).encode()
    )

    return {
        "message": "Saga triggered",
        "event_id": event["event_id"],
        "saga_type": request.saga_type,
    }


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PROCESS_MANAGER_PORT", "8081")),
        reload=os.getenv("ENV") == "development",
    )
