"""
Event Publisher - SAHOOL NDVI Engine
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from nats.aio.client import Client as NATS

from .types import get_subject, get_version, NDVI_COMPUTED, NDVI_ANOMALY_DETECTED

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
    def create(cls, event_type: str, version: int, aggregate_id: str,
               tenant_id: str, correlation_id: str, payload: dict):
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


class NdviPublisher:
    """Publisher for NDVI events"""

    def __init__(self, nats_url: str = None):
        self.nats_url = nats_url or NATS_URL
        self.nc: Optional[NATS] = None
        self._connected = False

    async def connect(self):
        """Connect to NATS"""
        if self._connected:
            return
        self.nc = NATS()
        await self.nc.connect(self.nats_url)
        self._connected = True
        print(f"📡 NDVI Publisher connected to NATS")

    async def close(self):
        """Close connection"""
        if self.nc and self._connected:
            await self.nc.close()
            self._connected = False

    async def publish_ndvi_computed(
        self,
        tenant_id: str,
        field_id: str,
        ndvi_mean: float,
        ndvi_trend_7d: float,
        scene_date: str,
        correlation_id: str = None,
        ndvi_min: float = None,
        ndvi_max: float = None,
        data_source: str = "satellite",
    ) -> str:
        """Publish NDVI computed event"""
        if not self._connected:
            await self.connect()

        payload = {
            "field_id": field_id,
            "ndvi_mean": ndvi_mean,
            "ndvi_trend_7d": ndvi_trend_7d,
            "scene_date": scene_date,
            "data_source": data_source,
        }

        if ndvi_min is not None:
            payload["ndvi_min"] = ndvi_min
        if ndvi_max is not None:
            payload["ndvi_max"] = ndvi_max

        env = EventEnvelope.create(
            event_type=NDVI_COMPUTED,
            version=get_version(NDVI_COMPUTED),
            aggregate_id=field_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        subject = get_subject(NDVI_COMPUTED)
        await self.nc.publish(subject, json.dumps(env.to_dict(), default=str).encode())

        print(f"📤 Published ndvi_computed: field={field_id}, ndvi={ndvi_mean}")
        return env.event_id

    async def publish_ndvi_anomaly(
        self,
        tenant_id: str,
        field_id: str,
        anomaly_type: str,
        severity: str,
        z_score: float,
        current_ndvi: float,
        historical_mean: float,
        correlation_id: str = None,
    ) -> str:
        """Publish NDVI anomaly event"""
        if not self._connected:
            await self.connect()

        payload = {
            "field_id": field_id,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "z_score": z_score,
            "current_ndvi": current_ndvi,
            "historical_mean": historical_mean,
        }

        env = EventEnvelope.create(
            event_type=NDVI_ANOMALY_DETECTED,
            version=get_version(NDVI_ANOMALY_DETECTED),
            aggregate_id=field_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        subject = get_subject(NDVI_ANOMALY_DETECTED)
        await self.nc.publish(subject, json.dumps(env.to_dict(), default=str).encode())

        print(f"🚨 Published ndvi_anomaly: field={field_id}, type={anomaly_type}")
        return env.event_id


# Singleton
_publisher: Optional[NdviPublisher] = None


async def get_publisher() -> NdviPublisher:
    global _publisher
    if _publisher is None:
        _publisher = NdviPublisher()
        await _publisher.connect()
    return _publisher
