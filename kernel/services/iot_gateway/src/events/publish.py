"""
Event Publisher - SAHOOL IoT Gateway
Publish IoT events to NATS JetStream
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from nats.aio.client import Client as NATS

from .types import (
    DEVICE_ALERT,
    DEVICE_REGISTERED,
    DEVICE_STATUS,
    SENSOR_READING,
    get_sensor_subject,
    get_subject,
    get_version,
)

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")


class EventEnvelope:
    """Standard event envelope wrapper"""

    def __init__(
        self,
        event_id: str,
        event_type: str,
        version: int,
        aggregate_id: str,
        tenant_id: str,
        correlation_id: str,
        timestamp: str,
        payload: dict,
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.version = version
        self.aggregate_id = aggregate_id
        self.tenant_id = tenant_id
        self.correlation_id = correlation_id
        self.timestamp = timestamp
        self.payload = payload

    @classmethod
    def create(
        cls,
        event_type: str,
        version: int,
        aggregate_id: str,
        tenant_id: str,
        correlation_id: str,
        payload: dict,
    ) -> "EventEnvelope":
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            version=version,
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload=payload,
        )

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "version": self.version,
            "aggregate_id": self.aggregate_id,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


class IoTPublisher:
    """Publisher for IoT Gateway events"""

    def __init__(self, nats_url: str = None):
        self.nats_url = nats_url or NATS_URL
        self.nc: Optional[NATS] = None
        self._connected = False
        self._stats = {
            "readings_published": 0,
            "status_published": 0,
            "alerts_published": 0,
        }

    async def connect(self):
        """Connect to NATS server"""
        if self._connected:
            return

        self.nc = NATS()
        try:
            await self.nc.connect(self.nats_url)
            self._connected = True
            print(f"📡 IoT Publisher connected to NATS: {self.nats_url}")
        except Exception as e:
            print(f"❌ Failed to connect to NATS: {e}")
            raise

    async def close(self):
        """Close NATS connection"""
        if self.nc and self._connected:
            await self.nc.close()
            self._connected = False
            print("📴 IoT Publisher disconnected from NATS")

    async def _publish(
        self,
        subject: str,
        event_type: str,
        tenant_id: str,
        aggregate_id: str,
        payload: dict,
        correlation_id: str = None,
    ) -> str:
        """Internal publish method"""
        if not self._connected:
            await self.connect()

        version = get_version(event_type)
        envelope = EventEnvelope.create(
            event_type=event_type,
            version=version,
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        message = json.dumps(envelope.to_dict(), default=str).encode()
        await self.nc.publish(subject, message)

        return envelope.event_id

    async def publish_sensor_reading(
        self,
        tenant_id: str,
        field_id: str,
        device_id: str,
        sensor_type: str,
        value: float,
        unit: str,
        timestamp: str,
        correlation_id: str = None,
        metadata: dict = None,
    ) -> str:
        """
        Publish a sensor reading event

        Publishes to both general and sensor-specific subjects
        """
        payload = {
            "device_id": device_id,
            "field_id": field_id,
            "sensor_type": sensor_type,
            "value": value,
            "unit": unit,
            "timestamp": timestamp,
            "metadata": metadata or {},
        }

        # Publish to general subject
        event_id = await self._publish(
            subject=get_subject(SENSOR_READING),
            event_type=SENSOR_READING,
            tenant_id=tenant_id,
            aggregate_id=field_id,
            payload=payload,
            correlation_id=correlation_id,
        )

        # Also publish to sensor-specific subject
        sensor_subject = get_sensor_subject(sensor_type)
        await self.nc.publish(
            sensor_subject,
            json.dumps(payload, default=str).encode(),
        )

        self._stats["readings_published"] += 1
        print(f"📤 Sensor reading: {sensor_type}={value}{unit} from {device_id}")

        return event_id

    async def publish_device_status(
        self,
        tenant_id: str,
        device_id: str,
        field_id: str,
        status: str,
        last_seen: str,
        battery_level: float = None,
        signal_strength: int = None,
        correlation_id: str = None,
    ) -> str:
        """Publish device status change event"""
        payload = {
            "device_id": device_id,
            "field_id": field_id,
            "status": status,
            "last_seen": last_seen,
        }

        if battery_level is not None:
            payload["battery_level"] = battery_level
        if signal_strength is not None:
            payload["signal_strength"] = signal_strength

        event_id = await self._publish(
            subject=get_subject(DEVICE_STATUS),
            event_type=DEVICE_STATUS,
            tenant_id=tenant_id,
            aggregate_id=device_id,
            payload=payload,
            correlation_id=correlation_id,
        )

        self._stats["status_published"] += 1
        print(f"📤 Device status: {device_id} -> {status}")

        return event_id

    async def publish_device_registered(
        self,
        tenant_id: str,
        device_id: str,
        field_id: str,
        device_type: str,
        name_ar: str,
        name_en: str,
        correlation_id: str = None,
    ) -> str:
        """Publish device registration event"""
        payload = {
            "device_id": device_id,
            "field_id": field_id,
            "device_type": device_type,
            "name_ar": name_ar,
            "name_en": name_en,
        }

        event_id = await self._publish(
            subject=get_subject(DEVICE_REGISTERED),
            event_type=DEVICE_REGISTERED,
            tenant_id=tenant_id,
            aggregate_id=device_id,
            payload=payload,
            correlation_id=correlation_id,
        )

        print(f"📤 Device registered: {device_id} ({device_type})")
        return event_id

    async def publish_device_alert(
        self,
        tenant_id: str,
        device_id: str,
        field_id: str,
        alert_type: str,
        message_ar: str,
        message_en: str,
        severity: str = "warning",
        correlation_id: str = None,
    ) -> str:
        """Publish device alert event"""
        payload = {
            "device_id": device_id,
            "field_id": field_id,
            "alert_type": alert_type,
            "message_ar": message_ar,
            "message_en": message_en,
            "severity": severity,
        }

        event_id = await self._publish(
            subject=get_subject(DEVICE_ALERT),
            event_type=DEVICE_ALERT,
            tenant_id=tenant_id,
            aggregate_id=device_id,
            payload=payload,
            correlation_id=correlation_id,
        )

        self._stats["alerts_published"] += 1
        print(f"🚨 Device alert: {device_id} - {alert_type}")

        return event_id

    def get_stats(self) -> dict:
        """Get publisher statistics"""
        return {
            **self._stats,
            "connected": self._connected,
        }


# Singleton instance
_publisher: Optional[IoTPublisher] = None


async def get_publisher() -> IoTPublisher:
    """Get or create publisher singleton"""
    global _publisher
    if _publisher is None:
        _publisher = IoTPublisher()
        await _publisher.connect()
    return _publisher
