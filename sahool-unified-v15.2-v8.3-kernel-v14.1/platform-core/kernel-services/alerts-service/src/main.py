"""
Alerts Service - Execution Service
Layer 4: Execution Service

خدمة التنبيهات - إرسال الإشعارات للمزارعين
Sends notifications via SMS, Push, WhatsApp, etc.

Responsibilities:
1. Subscribe to events requiring user notification
2. Create and send alerts via multiple channels
3. Track alert delivery and acknowledgment
4. Manage alert preferences
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import nats

sys.path.insert(0, '/app')
from shared.events.base_event import EventTypes, create_event
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.metrics import EVENTS_PUBLISHED, EVENTS_CONSUMED, init_service_info, get_metrics, get_metrics_content_type

configure_logging(service_name="alerts-service")
logger = get_logger(__name__)
event_logger = EventLogger("alerts-service")

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "alerts-service"
SERVICE_LAYER = "execution"


class AlertChannel(str, Enum):
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    IN_APP = "in_app"


class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AlertStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


@dataclass
class Alert:
    alert_id: str
    title: str
    message_ar: str
    message_en: Optional[str]
    priority: AlertPriority
    channels: List[AlertChannel]
    status: AlertStatus
    recipient_id: str
    recipient_phone: Optional[str]
    field_id: Optional[str]
    source_event_type: str
    source_event_id: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    tenant_id: str
    
    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "title": self.title,
            "message_ar": self.message_ar,
            "message_en": self.message_en,
            "priority": self.priority.value,
            "channels": [c.value for c in self.channels],
            "status": self.status.value,
            "recipient_id": self.recipient_id,
            "recipient_phone": self.recipient_phone,
            "field_id": self.field_id,
            "source_event_type": self.source_event_type,
            "source_event_id": self.source_event_id,
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "tenant_id": self.tenant_id
        }


class AlertStore:
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
    
    def create(self, alert: Alert) -> Alert:
        self.alerts[alert.alert_id] = alert
        return alert
    
    def get(self, alert_id: str) -> Optional[Alert]:
        return self.alerts.get(alert_id)
    
    def update(self, alert: Alert) -> Alert:
        self.alerts[alert.alert_id] = alert
        return alert
    
    def list_by_recipient(self, recipient_id: str, limit: int = 50) -> List[Alert]:
        alerts = [a for a in self.alerts.values() if a.recipient_id == recipient_id]
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)[:limit]
    
    def list_unacknowledged(self, recipient_id: str) -> List[Alert]:
        return [a for a in self.alerts.values() 
                if a.recipient_id == recipient_id and a.status != AlertStatus.ACKNOWLEDGED]


# Channel Providers (simulated for development)
class SMSProvider:
    async def send(self, phone: str, message: str) -> bool:
        logger.info("sms_sent", phone=phone[-4:], message_length=len(message))
        return True


class PushProvider:
    async def send(self, user_id: str, title: str, message: str) -> bool:
        logger.info("push_sent", user_id=user_id, title=title)
        return True


class WhatsAppProvider:
    async def send(self, phone: str, message: str) -> bool:
        logger.info("whatsapp_sent", phone=phone[-4:])
        return True


class AlertService:
    def __init__(self):
        self.nc = None
        self.js = None
        self.store = AlertStore()
        self.sms = SMSProvider()
        self.push = PushProvider()
        self.whatsapp = WhatsAppProvider()
        self.running = False
        
        # Default user for demo (would come from user service)
        self.demo_user = {
            "id": "user_001",
            "name_ar": "أحمد المزارع",
            "phone": "+967771234567"
        }
    
    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("nats_connected")
    
    async def start(self):
        self.running = True
        
        subscriptions = [
            (EventTypes.TASK_CREATED, "alerts-task"),
            (EventTypes.TASK_OVERDUE, "alerts-overdue"),
            (EventTypes.WEATHER_ANOMALY_DETECTED, "alerts-weather"),
            (EventTypes.NDVI_ANOMALY_DETECTED, "alerts-ndvi"),
            (EventTypes.CROP_ACTION_RECOMMENDED, "alerts-crop"),
        ]
        
        for subject, durable in subscriptions:
            try:
                sub = await self.js.pull_subscribe(subject=subject, durable=durable, stream="SAHOOL")
                asyncio.create_task(self._process_events(sub, subject))
            except Exception as e:
                logger.warning("subscription_failed", subject=subject, error=str(e))
        
        logger.info("alerts_service_started")
    
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
            
            EVENTS_CONSUMED.labels(service=SERVICE_NAME, event_type=event_type, tenant_id="default").inc()
            
            # Create alert based on event type
            alert = await self._create_alert_from_event(event_type, event_data)
            if alert:
                await self._send_alert(alert)
            
            await msg.ack()
        except Exception as e:
            logger.error("event_handling_failed", error=str(e))
            await msg.nak()
    
    async def _create_alert_from_event(self, event_type: str, event_data: dict) -> Optional[Alert]:
        payload = event_data.get("payload", {})
        
        # Determine priority and channels based on event type
        priority = AlertPriority.MEDIUM
        channels = [AlertChannel.PUSH, AlertChannel.IN_APP]
        title = ""
        message_ar = ""
        field_id = None
        
        if event_type == EventTypes.TASK_CREATED:
            task = payload.get("task", {})
            priority_str = task.get("priority", "medium")
            priority = AlertPriority(priority_str) if priority_str in [p.value for p in AlertPriority] else AlertPriority.MEDIUM
            
            if task.get("requires_immediate_attention"):
                channels = [AlertChannel.SMS, AlertChannel.PUSH, AlertChannel.WHATSAPP]
            
            title = "مهمة جديدة"
            message_ar = f"📋 {task.get('title', '')}\n🌾 الحقل: {task.get('field_id', '')}\n⏰ الموعد النهائي: {task.get('due_date', '')[:10]}"
            field_id = task.get("field_id")
        
        elif event_type == EventTypes.TASK_OVERDUE:
            priority = AlertPriority.URGENT
            channels = [AlertChannel.SMS, AlertChannel.PUSH, AlertChannel.WHATSAPP]
            title = "⚠️ مهمة متأخرة"
            message_ar = f"المهمة '{payload.get('title', '')}' تجاوزت موعدها!\nالحقل: {payload.get('field_id', '')}"
            field_id = payload.get("field_id")
        
        elif event_type == EventTypes.WEATHER_ANOMALY_DETECTED:
            anomaly = payload.get("anomaly", {})
            severity = anomaly.get("severity", "medium")
            
            if severity in ["high", "critical"]:
                priority = AlertPriority.URGENT
                channels = [AlertChannel.SMS, AlertChannel.PUSH, AlertChannel.WHATSAPP]
            
            title = "🌤️ تنبيه طقس"
            message_ar = anomaly.get("description_ar", "تغير في أحوال الطقس")
            location = payload.get("location", {})
            if location:
                message_ar += f"\n📍 المنطقة: {location.get('name_ar', '')}"
        
        elif event_type == EventTypes.NDVI_ANOMALY_DETECTED:
            anomaly = payload.get("anomaly", {})
            field = payload.get("field", {})
            severity = anomaly.get("severity", "medium")
            
            if severity in ["high", "critical"]:
                priority = AlertPriority.HIGH
                channels = [AlertChannel.SMS, AlertChannel.PUSH]
            
            title = "🛰️ تنبيه صحة المحصول"
            message_ar = f"{anomaly.get('description_ar', 'تغير في صحة النباتات')}\nالحقل: {field.get('name_ar', '')}"
            field_id = field.get("id")
        
        elif event_type == EventTypes.CROP_ACTION_RECOMMENDED:
            priority_str = payload.get("priority", "medium")
            priority = AlertPriority(priority_str) if priority_str in [p.value for p in AlertPriority] else AlertPriority.MEDIUM
            
            title = "💡 توصية زراعية"
            message_ar = payload.get("description_ar", "")
            if payload.get("proverb_reference"):
                message_ar += f"\n📜 المثل: {payload.get('proverb_reference')}"
            field_id = payload.get("field_id")
        
        if not message_ar:
            return None
        
        alert = Alert(
            alert_id=f"alert_{uuid4().hex[:12]}",
            title=title,
            message_ar=message_ar,
            message_en=None,
            priority=priority,
            channels=channels,
            status=AlertStatus.PENDING,
            recipient_id=self.demo_user["id"],
            recipient_phone=self.demo_user["phone"],
            field_id=field_id,
            source_event_type=event_type,
            source_event_id=event_data.get("event_id"),
            created_at=datetime.utcnow(),
            sent_at=None,
            acknowledged_at=None,
            tenant_id=event_data.get("tenant_id", "default")
        )
        
        self.store.create(alert)
        return alert
    
    async def _send_alert(self, alert: Alert):
        """Send alert via configured channels"""
        sent = False
        
        for channel in alert.channels:
            try:
                if channel == AlertChannel.SMS and alert.recipient_phone:
                    sent = await self.sms.send(alert.recipient_phone, f"{alert.title}\n{alert.message_ar}")
                elif channel == AlertChannel.PUSH:
                    sent = await self.push.send(alert.recipient_id, alert.title, alert.message_ar)
                elif channel == AlertChannel.WHATSAPP and alert.recipient_phone:
                    sent = await self.whatsapp.send(alert.recipient_phone, f"*{alert.title}*\n{alert.message_ar}")
                elif channel == AlertChannel.IN_APP:
                    sent = True  # In-app is always successful
            except Exception as e:
                logger.error("channel_send_failed", channel=channel.value, error=str(e))
        
        if sent:
            alert.status = AlertStatus.SENT
            alert.sent_at = datetime.utcnow()
            self.store.update(alert)
            
            # Publish alert sent event
            await self._publish_alert_sent(alert)
            
            logger.info("alert_sent", alert_id=alert.alert_id, channels=[c.value for c in alert.channels])
        else:
            alert.status = AlertStatus.FAILED
            self.store.update(alert)
            logger.error("alert_failed", alert_id=alert.alert_id)
    
    async def _publish_alert_sent(self, alert: Alert):
        event = create_event(
            event_type=EventTypes.ALERT_SENT,
            payload={
                "alert_id": alert.alert_id,
                "title": alert.title,
                "recipient_id": alert.recipient_id,
                "channels": [c.value for c in alert.channels],
                "priority": alert.priority.value,
                "field_id": alert.field_id
            },
            tenant_id=alert.tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.ALERT_SENT,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.ALERT_SENT, tenant_id=alert.tenant_id).inc()
    
    async def acknowledge_alert(self, alert_id: str) -> Alert:
        alert = self.store.get(alert_id)
        if not alert:
            raise ValueError("Alert not found")
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        self.store.update(alert)
        
        # Publish acknowledged event
        event = create_event(
            event_type=EventTypes.ALERT_ACKNOWLEDGED,
            payload={"alert_id": alert_id, "acknowledged_at": alert.acknowledged_at.isoformat()},
            tenant_id=alert.tenant_id
        )
        await self.js.publish(
            subject=EventTypes.ALERT_ACKNOWLEDGED,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        return alert
    
    async def stop(self):
        self.running = False
        if self.nc:
            await self.nc.close()


alert_service = AlertService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", layer=SERVICE_LAYER)
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await alert_service.connect()
    await alert_service.start()
    logger.info("service_started")
    yield
    await alert_service.stop()


app = FastAPI(title="Alerts Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    return {"status": "ready" if alert_service.nc and alert_service.nc.is_connected else "not_ready"}


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response
    return Response(content=get_metrics(), media_type=get_metrics_content_type())


@app.get("/api/alerts")
async def list_alerts(recipient_id: str = "user_001", limit: int = 50):
    alerts = alert_service.store.list_by_recipient(recipient_id, limit)
    return {"alerts": [a.to_dict() for a in alerts]}


@app.get("/api/alerts/unread")
async def list_unread(recipient_id: str = "user_001"):
    alerts = alert_service.store.list_unacknowledged(recipient_id)
    return {"alerts": [a.to_dict() for a in alerts], "count": len(alerts)}


@app.get("/api/alerts/{alert_id}")
async def get_alert(alert_id: str):
    alert = alert_service.store.get(alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    return alert.to_dict()


@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    try:
        alert = await alert_service.acknowledge_alert(alert_id)
        return {"message": "Alert acknowledged", "alert": alert.to_dict()}
    except ValueError as e:
        raise HTTPException(404, str(e))


class SendAlertRequest(BaseModel):
    title: str
    message_ar: str
    recipient_id: str = "user_001"
    priority: str = "medium"
    channels: List[str] = ["push", "in_app"]


@app.post("/api/alerts/send")
async def send_manual_alert(request: SendAlertRequest):
    """Manually send an alert"""
    alert = Alert(
        alert_id=f"alert_{uuid4().hex[:12]}",
        title=request.title,
        message_ar=request.message_ar,
        message_en=None,
        priority=AlertPriority(request.priority),
        channels=[AlertChannel(c) for c in request.channels],
        status=AlertStatus.PENDING,
        recipient_id=request.recipient_id,
        recipient_phone=alert_service.demo_user["phone"],
        field_id=None,
        source_event_type="manual",
        source_event_id=None,
        created_at=datetime.utcnow(),
        sent_at=None,
        acknowledged_at=None,
        tenant_id="default"
    )
    
    alert_service.store.create(alert)
    await alert_service._send_alert(alert)
    
    return {"message": "Alert sent", "alert": alert.to_dict()}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("ALERTS_PORT", "8090")), reload=os.getenv("ENV") == "development")
