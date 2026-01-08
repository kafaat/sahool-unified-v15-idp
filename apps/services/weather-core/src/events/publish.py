"""
Event Publisher - SAHOOL Weather Core
"""

import json
import os
import uuid
from datetime import UTC, datetime

from nats.aio.client import Client as NATS

from .types import IRRIGATION_ADJUSTMENT, WEATHER_ALERT, get_subject, get_version

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")


class EventEnvelope:
    """Standard event envelope"""

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
    ):
        return cls(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            version=version,
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            timestamp=datetime.now(UTC).isoformat(),
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


class WeatherPublisher:
    """Publisher for Weather events"""

    def __init__(self, nats_url: str = None):
        self.nats_url = nats_url or NATS_URL
        self.nc: NATS | None = None
        self._connected = False

    async def connect(self):
        """Connect to NATS"""
        if self._connected:
            return
        self.nc = NATS()
        await self.nc.connect(self.nats_url)
        self._connected = True
        print("📡 Weather Publisher connected to NATS")

    async def close(self):
        """Close connection"""
        if self.nc and self._connected:
            await self.nc.close()
            self._connected = False

    async def publish_weather_alert(
        self,
        tenant_id: str,
        field_id: str,
        alert_type: str,
        severity: str,
        window_hours: int,
        title_ar: str = None,
        title_en: str = None,
        correlation_id: str = None,
    ) -> str:
        """Publish weather alert event"""
        if not self._connected:
            await self.connect()

        payload = {
            "field_id": field_id,
            "alert_type": alert_type,
            "severity": severity,
            "window_hours": window_hours,
        }

        if title_ar:
            payload["title_ar"] = title_ar
        if title_en:
            payload["title_en"] = title_en

        env = EventEnvelope.create(
            event_type=WEATHER_ALERT,
            version=get_version(WEATHER_ALERT),
            aggregate_id=field_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        subject = get_subject(WEATHER_ALERT)
        await self.nc.publish(subject, json.dumps(env.to_dict(), default=str).encode())

        print(
            f"🌤️ Published weather_alert: field={field_id}, type={alert_type}, severity={severity}"
        )
        return env.event_id

    async def publish_irrigation_adjustment(
        self,
        tenant_id: str,
        field_id: str,
        adjustment_factor: float,
        recommendation_ar: str,
        recommendation_en: str,
        correlation_id: str = None,
    ) -> str:
        """Publish irrigation adjustment event"""
        if not self._connected:
            await self.connect()

        payload = {
            "field_id": field_id,
            "adjustment_factor": adjustment_factor,
            "recommendation_ar": recommendation_ar,
            "recommendation_en": recommendation_en,
        }

        env = EventEnvelope.create(
            event_type=IRRIGATION_ADJUSTMENT,
            version=get_version(IRRIGATION_ADJUSTMENT),
            aggregate_id=field_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        subject = get_subject(IRRIGATION_ADJUSTMENT)
        await self.nc.publish(subject, json.dumps(env.to_dict(), default=str).encode())

        print(f"💧 Published irrigation_adjustment: field={field_id}, factor={adjustment_factor}")
        return env.event_id


# Singleton
_publisher: WeatherPublisher | None = None


async def get_publisher() -> WeatherPublisher:
    global _publisher
    if _publisher is None:
        _publisher = WeatherPublisher()
        await _publisher.connect()
    return _publisher
