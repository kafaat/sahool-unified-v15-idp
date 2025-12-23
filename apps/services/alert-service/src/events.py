"""
SAHOOL Alert Service - NATS Events
أحداث NATS لخدمة التنبيهات
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Callable, Awaitable
from uuid import uuid4

import nats
from nats.aio.client import Client as NatsClient

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Topics
# ═══════════════════════════════════════════════════════════════════════════════


class AlertTopics:
    """موضوعات NATS للتنبيهات"""
    # نشر التنبيهات
    ALERT_CREATED = "sahool.alerts.created"
    ALERT_UPDATED = "sahool.alerts.updated"
    ALERT_ACKNOWLEDGED = "sahool.alerts.acknowledged"
    ALERT_RESOLVED = "sahool.alerts.resolved"
    ALERT_EXPIRED = "sahool.alerts.expired"

    # استقبال من خدمات أخرى
    NDVI_ANOMALY = "sahool.ndvi.anomaly"
    WEATHER_ALERT = "sahool.weather.alert"
    IOT_THRESHOLD = "sahool.iot.threshold"
    CROP_HEALTH_ALERT = "sahool.crop_health.alert"
    IRRIGATION_ALERT = "sahool.irrigation.alert"


# ═══════════════════════════════════════════════════════════════════════════════
# Event Publisher
# ═══════════════════════════════════════════════════════════════════════════════


class AlertEventPublisher:
    """ناشر أحداث التنبيهات"""

    def __init__(self):
        self._nc: Optional[NatsClient] = None
        self._connected = False

    async def connect(self) -> bool:
        """الاتصال بـ NATS"""
        nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
        try:
            self._nc = await nats.connect(nats_url)
            self._connected = True
            logger.info(f"Connected to NATS at {nats_url}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to NATS: {e}")
            self._connected = False
            return False

    async def close(self):
        """إغلاق الاتصال"""
        if self._nc and self._connected:
            await self._nc.close()
            self._connected = False
            logger.info("NATS connection closed")

    @property
    def is_connected(self) -> bool:
        return self._connected and self._nc is not None

    async def _publish(self, topic: str, data: dict) -> Optional[str]:
        """نشر حدث"""
        if not self.is_connected:
            logger.warning(f"Cannot publish to {topic}: not connected to NATS")
            return None

        event_id = str(uuid4())
        payload = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "topic": topic,
            **data
        }

        try:
            await self._nc.publish(topic, json.dumps(payload).encode())
            logger.debug(f"Published event {event_id} to {topic}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return None

    async def publish_alert_created(
        self,
        alert_id: str,
        field_id: str,
        tenant_id: Optional[str],
        alert_type: str,
        severity: str,
        title: str,
        correlation_id: Optional[str] = None
    ) -> Optional[str]:
        """نشر حدث إنشاء تنبيه"""
        return await self._publish(AlertTopics.ALERT_CREATED, {
            "alert_id": alert_id,
            "field_id": field_id,
            "tenant_id": tenant_id,
            "type": alert_type,
            "severity": severity,
            "title": title,
            "correlation_id": correlation_id
        })

    async def publish_alert_updated(
        self,
        alert_id: str,
        field_id: str,
        old_status: str,
        new_status: str,
        updated_by: Optional[str] = None
    ) -> Optional[str]:
        """نشر حدث تحديث تنبيه"""
        return await self._publish(AlertTopics.ALERT_UPDATED, {
            "alert_id": alert_id,
            "field_id": field_id,
            "old_status": old_status,
            "new_status": new_status,
            "updated_by": updated_by
        })

    async def publish_alert_acknowledged(
        self,
        alert_id: str,
        field_id: str,
        acknowledged_by: str
    ) -> Optional[str]:
        """نشر حدث إقرار بتنبيه"""
        return await self._publish(AlertTopics.ALERT_ACKNOWLEDGED, {
            "alert_id": alert_id,
            "field_id": field_id,
            "acknowledged_by": acknowledged_by
        })

    async def publish_alert_resolved(
        self,
        alert_id: str,
        field_id: str,
        resolved_by: str,
        resolution_note: Optional[str] = None
    ) -> Optional[str]:
        """نشر حدث حل تنبيه"""
        return await self._publish(AlertTopics.ALERT_RESOLVED, {
            "alert_id": alert_id,
            "field_id": field_id,
            "resolved_by": resolved_by,
            "resolution_note": resolution_note
        })


# ═══════════════════════════════════════════════════════════════════════════════
# Event Subscriber
# ═══════════════════════════════════════════════════════════════════════════════


class AlertEventSubscriber:
    """مستقبل أحداث التنبيهات"""

    def __init__(self):
        self._nc: Optional[NatsClient] = None
        self._subscriptions = []
        self._handlers: dict[str, Callable[[dict], Awaitable[None]]] = {}

    async def connect(self) -> bool:
        """الاتصال بـ NATS"""
        nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
        try:
            self._nc = await nats.connect(nats_url)
            logger.info(f"Subscriber connected to NATS at {nats_url}")
            return True
        except Exception as e:
            logger.warning(f"Subscriber failed to connect to NATS: {e}")
            return False

    async def close(self):
        """إغلاق الاتصال"""
        for sub in self._subscriptions:
            await sub.unsubscribe()
        if self._nc:
            await self._nc.close()
        logger.info("Subscriber disconnected from NATS")

    def register_handler(self, topic: str, handler: Callable[[dict], Awaitable[None]]):
        """تسجيل معالج لموضوع معين"""
        self._handlers[topic] = handler

    async def subscribe_to_external_alerts(self):
        """الاشتراك في التنبيهات من الخدمات الأخرى"""
        if not self._nc:
            logger.warning("Cannot subscribe: not connected to NATS")
            return

        topics = [
            AlertTopics.NDVI_ANOMALY,
            AlertTopics.WEATHER_ALERT,
            AlertTopics.IOT_THRESHOLD,
            AlertTopics.CROP_HEALTH_ALERT,
            AlertTopics.IRRIGATION_ALERT,
        ]

        for topic in topics:
            sub = await self._nc.subscribe(topic, cb=self._message_handler)
            self._subscriptions.append(sub)
            logger.info(f"Subscribed to {topic}")

    async def _message_handler(self, msg):
        """معالج الرسائل الواردة"""
        try:
            data = json.loads(msg.data.decode())
            topic = msg.subject

            logger.debug(f"Received message on {topic}: {data.get('event_id', 'unknown')}")

            if topic in self._handlers:
                await self._handlers[topic](data)
            else:
                logger.debug(f"No handler registered for {topic}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton Instances
# ═══════════════════════════════════════════════════════════════════════════════


_publisher: Optional[AlertEventPublisher] = None
_subscriber: Optional[AlertEventSubscriber] = None


async def get_publisher() -> AlertEventPublisher:
    """الحصول على ناشر الأحداث"""
    global _publisher
    if _publisher is None:
        _publisher = AlertEventPublisher()
        await _publisher.connect()
    return _publisher


async def get_subscriber() -> AlertEventSubscriber:
    """الحصول على مستقبل الأحداث"""
    global _subscriber
    if _subscriber is None:
        _subscriber = AlertEventSubscriber()
        await _subscriber.connect()
    return _subscriber
