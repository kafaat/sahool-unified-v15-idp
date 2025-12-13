"""
Alerts Service - خدمة التنبيهات
Layer 4: Execution Service

Sends notifications to farmers via multiple channels.

Responsibilities:
1. Subscribe to task and anomaly events
2. Generate appropriate alerts
3. Send via SMS, Push, Email (simulated)
4. Track alert delivery and acknowledgment

Events Consumed:
- task.created
- task.overdue
- weather.anomaly.detected
- ndvi.anomaly.detected

Events Produced:
- alert.sent
- alert.acknowledged
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import nats

sys.path.insert(0, '/app')
from shared.events.base_event import create_event, EventTypes, generate_id
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.metrics import EVENTS_PUBLISHED, EVENTS_CONSUMED, init_service_info

configure_logging(service_name="alerts-service")
logger = get_logger(__name__)
event_logger = EventLogger("alerts-service")

SERVICE_NAME = "alerts-service"
SERVICE_LAYER = "execution"
NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")


# ============================================
# Domain Models
# ============================================

class AlertChannel(str, Enum):
    SMS = "sms"
    PUSH = "push"
    EMAIL = "email"
    IN_APP = "in_app"


class AlertPriority(str, Enum):
    INFO = "info"
    WARNING = "warning"
    URGENT = "urgent"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"


@dataclass
class Alert:
    """An alert notification"""
    id: str
    tenant_id: str
    user_id: str
    title_ar: str
    title_en: str
    body_ar: str
    body_en: str
    priority: AlertPriority
    channel: AlertChannel
    status: AlertStatus
    source_event_type: str
    source_event_id: str
    created_at: str
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    read_at: Optional[str] = None
    acknowledged_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "title": {"ar": self.title_ar, "en": self.title_en},
            "body": {"ar": self.body_ar, "en": self.body_en},
            "priority": self.priority.value,
            "channel": self.channel.value,
            "status": self.status.value,
            "source_event_type": self.source_event_type,
            "source_event_id": self.source_event_id,
            "created_at": self.created_at,
            "sent_at": self.sent_at,
            "delivered_at": self.delivered_at,
            "read_at": self.read_at,
            "acknowledged_at": self.acknowledged_at,
            "metadata": self.metadata
        }


# ============================================
# Alert Templates
# ============================================

ALERT_TEMPLATES = {
    "task.created": {
        "title_ar": "مهمة جديدة",
        "title_en": "New Task",
        "priority": AlertPriority.WARNING,
        "channels": [AlertChannel.PUSH, AlertChannel.IN_APP]
    },
    "task.overdue": {
        "title_ar": "⚠️ مهمة متأخرة",
        "title_en": "⚠️ Overdue Task",
        "priority": AlertPriority.URGENT,
        "channels": [AlertChannel.SMS, AlertChannel.PUSH, AlertChannel.IN_APP]
    },
    "weather.anomaly.detected": {
        "title_ar": "🌡️ تنبيه طقس",
        "title_en": "🌡️ Weather Alert",
        "priority": AlertPriority.URGENT,
        "channels": [AlertChannel.SMS, AlertChannel.PUSH, AlertChannel.IN_APP]
    },
    "ndvi.anomaly.detected": {
        "title_ar": "🛰️ تنبيه صحة المحصول",
        "title_en": "🛰️ Crop Health Alert",
        "priority": AlertPriority.WARNING,
        "channels": [AlertChannel.PUSH, AlertChannel.IN_APP]
    }
}


# ============================================
# Alert Manager
# ============================================

class AlertManager:
    """Manages alert creation and delivery"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        # Demo users (would be from DB)
        self.users = {
            "default": [
                {"id": "user_001", "name": "أحمد", "phone": "+967700000001", "email": "ahmed@example.com"},
                {"id": "user_002", "name": "محمد", "phone": "+967700000002", "email": "mohammed@example.com"},
            ]
        }
    
    def create_alert_from_event(self, event: Dict) -> List[Alert]:
        """Create alerts from incoming event"""
        event_type = event.get("event_type", "")
        template = ALERT_TEMPLATES.get(event_type)
        
        if not template:
            logger.debug("no_template", event_type=event_type)
            return []
        
        tenant_id = event.get("tenant_id", "default")
        users = self.users.get(tenant_id, [])
        
        if not users:
            logger.warning("no_users_for_tenant", tenant_id=tenant_id)
            return []
        
        alerts = []
        payload = event.get("payload", {})
        
        # Build alert body from event payload
        body_ar, body_en = self._build_alert_body(event_type, payload)
        
        for user in users:
            for channel in template["channels"]:
                alert = Alert(
                    id=f"alert_{generate_id()}",
                    tenant_id=tenant_id,
                    user_id=user["id"],
                    title_ar=template["title_ar"],
                    title_en=template["title_en"],
                    body_ar=body_ar,
                    body_en=body_en,
                    priority=template["priority"],
                    channel=channel,
                    status=AlertStatus.PENDING,
                    source_event_type=event_type,
                    source_event_id=event.get("event_id", ""),
                    created_at=datetime.utcnow().isoformat(),
                    metadata={
                        "user_name": user["name"],
                        "user_phone": user["phone"],
                        "user_email": user["email"]
                    }
                )
                self.alerts[alert.id] = alert
                alerts.append(alert)
        
        return alerts
    
    def _build_alert_body(self, event_type: str, payload: Dict) -> tuple:
        """Build alert body text from payload"""
        if event_type == "task.created":
            task = payload.get("task", {})
            title = task.get("title", {})
            return (
                f"لديك مهمة جديدة: {title.get('ar', '')}",
                f"You have a new task: {title.get('en', '')}"
            )
        
        elif event_type == "task.overdue":
            task = payload.get("task", {})
            title = task.get("title", {})
            return (
                f"مهمة متأخرة تحتاج اهتمام: {title.get('ar', '')}",
                f"Overdue task needs attention: {title.get('en', '')}"
            )
        
        elif event_type == "weather.anomaly.detected":
            anomaly = payload.get("anomaly", {})
            desc = anomaly.get("description", {})
            location = payload.get("location", {})
            return (
                f"{desc.get('ar', '')} في {location.get('name', '')}",
                f"{desc.get('en', '')} in {location.get('name', '')}"
            )
        
        elif event_type == "ndvi.anomaly.detected":
            anomaly = payload.get("anomaly", {})
            desc = anomaly.get("description", {})
            field_info = payload.get("field", {})
            return (
                f"{desc.get('ar', '')} - {field_info.get('name', '')}",
                f"{desc.get('en', '')} - {field_info.get('name', '')}"
            )
        
        return ("تنبيه جديد", "New alert")
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert via appropriate channel (simulated)"""
        try:
            # Simulate sending based on channel
            if alert.channel == AlertChannel.SMS:
                logger.info("sms_sent", phone=alert.metadata.get("user_phone"), alert_id=alert.id)
            elif alert.channel == AlertChannel.PUSH:
                logger.info("push_sent", user=alert.user_id, alert_id=alert.id)
            elif alert.channel == AlertChannel.EMAIL:
                logger.info("email_sent", email=alert.metadata.get("user_email"), alert_id=alert.id)
            elif alert.channel == AlertChannel.IN_APP:
                logger.info("in_app_created", user=alert.user_id, alert_id=alert.id)
            
            # Update status
            alert.status = AlertStatus.SENT
            alert.sent_at = datetime.utcnow().isoformat()
            
            # Simulate delivery
            await asyncio.sleep(0.1)
            alert.status = AlertStatus.DELIVERED
            alert.delivered_at = datetime.utcnow().isoformat()
            
            return True
            
        except Exception as e:
            logger.error("alert_send_failed", alert_id=alert.id, error=str(e))
            alert.status = AlertStatus.FAILED
            return False
    
    def acknowledge_alert(self, alert_id: str) -> Optional[Alert]:
        """Mark alert as acknowledged"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow().isoformat()
        return alert
    
    def get_user_alerts(self, user_id: str, unread_only: bool = False) -> List[Alert]:
        """Get alerts for a user"""
        alerts = [a for a in self.alerts.values() if a.user_id == user_id]
        if unread_only:
            alerts = [a for a in alerts if a.status not in [AlertStatus.READ, AlertStatus.ACKNOWLEDGED]]
        return sorted(alerts, key=lambda a: a.created_at, reverse=True)


# ============================================
# Alerts Service
# ============================================

class AlertsService:
    """Main alerts service"""
    
    def __init__(self):
        self.nc = None
        self.js = None
        self.manager = AlertManager()
        self.running = False
    
    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("nats_connected")
    
    async def start(self):
        """Start event processing"""
        self.running = True
        
        # Subscribe to events that need alerts
        subjects = [
            "task.created",
            "task.overdue",
            "weather.anomaly.detected",
            "ndvi.anomaly.detected"
        ]
        
        for subject in subjects:
            try:
                sub = await self.js.pull_subscribe(
                    subject=subject,
                    durable=f"alerts-{subject.replace('.', '-')}",
                    stream="SAHOOL"
                )
                asyncio.create_task(self._process_subscription(sub, subject))
                logger.info("subscribed", subject=subject)
            except Exception as e:
                logger.warning("subscription_failed", subject=subject, error=str(e))
    
    async def _process_subscription(self, sub, subject: str):
        while self.running:
            try:
                messages = await sub.fetch(batch=10, timeout=1)
                for msg in messages:
                    await self._handle_message(msg, subject)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("subscription_error", subject=subject, error=str(e))
                await asyncio.sleep(1)
    
    async def _handle_message(self, msg, subject: str):
        try:
            event = json.loads(msg.data.decode())
            event_type = event.get("event_type", subject)
            
            EVENTS_CONSUMED.labels(service=SERVICE_NAME, event_type=event_type, tenant_id=event.get("tenant_id", "default")).inc()
            event_logger.consumed(event_type)
            
            # Create alerts
            alerts = self.manager.create_alert_from_event(event)
            
            # Send and publish
            for alert in alerts:
                success = await self.manager.send_alert(alert)
                if success:
                    await self._publish_alert_sent(alert, event)
            
            await msg.ack()
            
        except Exception as e:
            logger.error("message_handling_failed", error=str(e))
            await msg.nak()
    
    async def _publish_alert_sent(self, alert: Alert, source_event: Dict):
        event = create_event(
            event_type=EventTypes.ALERT_SENT,
            payload={"alert": alert.to_dict()},
            tenant_id=alert.tenant_id,
            correlation_id=source_event.get("correlation_id"),
            causation_id=source_event.get("event_id")
        )
        await self.js.publish(subject=EventTypes.ALERT_SENT, payload=json.dumps(event).encode())
        event_logger.published(EventTypes.ALERT_SENT, alert_id=alert.id, channel=alert.channel.value)
        EVENTS_PUBLISHED.labels(service=SERVICE_NAME, event_type=EventTypes.ALERT_SENT, tenant_id=alert.tenant_id).inc()
    
    async def _publish_alert_acknowledged(self, alert: Alert):
        event = create_event(
            event_type=EventTypes.ALERT_ACKNOWLEDGED,
            payload={"alert": alert.to_dict()},
            tenant_id=alert.tenant_id
        )
        await self.js.publish(subject=EventTypes.ALERT_ACKNOWLEDGED, payload=json.dumps(event).encode())
        event_logger.published(EventTypes.ALERT_ACKNOWLEDGED, alert_id=alert.id)
    
    async def stop(self):
        self.running = False
        if self.nc: await self.nc.close()
        logger.info("service_stopped")


alerts_service = AlertsService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", layer=SERVICE_LAYER)
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await alerts_service.connect()
    await alerts_service.start()
    logger.info("service_started")
    yield
    await alerts_service.stop()


app = FastAPI(title="Alerts Service", description="SAHOOL - Alert Notification Service (Layer 4)", version="1.0.0", lifespan=lifespan)


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}

@app.get("/readyz")
async def ready():
    return {"status": "ready" if alerts_service.nc and alerts_service.nc.is_connected else "not_ready"}

@app.get("/api/alerts")
async def get_all_alerts():
    """Get all alerts"""
    return {"alerts": [a.to_dict() for a in alerts_service.manager.alerts.values()]}

@app.get("/api/users/{user_id}/alerts")
async def get_user_alerts(user_id: str, unread_only: bool = False):
    """Get alerts for a specific user"""
    alerts = alerts_service.manager.get_user_alerts(user_id, unread_only)
    return {"alerts": [a.to_dict() for a in alerts]}

@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    alert = alerts_service.manager.acknowledge_alert(alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    await alerts_service._publish_alert_acknowledged(alert)
    return alert.to_dict()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("ALERTS_PORT", "8090")), reload=os.getenv("ENV") == "development")
