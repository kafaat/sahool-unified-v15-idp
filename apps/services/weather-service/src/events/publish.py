"""
Event Publisher - SAHOOL Weather Core
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import UTC, datetime, timezone

try:
    from nats.aio.client import Client as NATS
except ImportError:
    NATS = None  # Optional: not available in test environments

logger = logging.getLogger(__name__)

from .types import IRRIGATION_ADJUSTMENT, WEATHER_ALERT, WEATHER_FORECAST_ISSUED, get_subject, get_version

try:
    from shared.events.subjects import get_tenant_subject
except ImportError:

    def get_tenant_subject(tenant_id: str, domain: str, action: str) -> str:
        return f"sahool.tenant.{tenant_id}.{domain}.{action}"


def _weather_scoped(event_type: str, tenant_id: str | None) -> str:
    """Return tenant-scoped weather subject or fall back to global with warning."""
    global_subject = get_subject(event_type)
    if tenant_id:
        # Preserve the "alert" / "forecast.issued" / "irrigation.adjustment" action suffix.
        # The domain prefix is kept as a 2-segment literal (valid NATS subject —
        # `"sahool.<domain>"`) so string-level drift detectors don't trip on a
        # trailing-dot prefix that was never a real subject.
        _WEATHER_DOMAIN = "sahool.weather"
        action = (
            global_subject[len(_WEATHER_DOMAIN) + 1 :]
            if global_subject.startswith(_WEATHER_DOMAIN + ".")
            else event_type
        )
        return get_tenant_subject(tenant_id, "weather", action)
    logger.warning(
        "nats_publish_missing_tenant_id subject=%s (falling back to global; TODO plumb tenant_id)",
        global_subject,
    )
    return global_subject


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
        self.nc = None
        self._connected = False

    async def connect(self):
        """Connect to NATS with reconnection support"""
        if self._connected:
            return
        if NATS is None:
            logger.warning("nats-py not installed, event publishing disabled")
            return
        self.nc = NATS()
        await self.nc.connect(
            self.nats_url,
            reconnect_time_wait=2,
            max_reconnect_attempts=60,
            error_cb=self._on_error,
            disconnected_cb=self._on_disconnect,
            reconnected_cb=self._on_reconnect,
        )
        self._connected = True
        logger.info("Weather Publisher connected to NATS: %s", self.nats_url)

    async def _on_error(self, e):
        logger.error("NATS error: %s", e)

    async def _on_disconnect(self):
        self._connected = False
        logger.warning("NATS disconnected — will auto-reconnect")

    async def _on_reconnect(self):
        self._connected = True
        logger.info("NATS reconnected")

    @property
    def _is_available(self) -> bool:
        """Check if NATS publishing is available"""
        return NATS is not None and self.nc is not None and self._connected

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

        if not self._is_available:
            logger.debug("NATS unavailable, skipping weather_alert publish for field=%s", field_id)
            return str(uuid.uuid4())

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

        subject = _weather_scoped(WEATHER_ALERT, tenant_id)
        try:
            await self.nc.publish(subject, json.dumps(env.to_dict(), default=str).encode())
        except Exception as e:
            logger.error(
                "Failed to publish weather_alert event: subject=%s, field=%s, error=%s",
                subject,
                field_id,
                str(e),
            )
            raise

        logger.info("Published weather_alert: field=%s, type=%s, severity=%s", field_id, alert_type, severity)
        return env.event_id

    async def publish_forecast_issued(
        self,
        tenant_id: str,
        field_id: str,
        provider: str,
        days: int,
        correlation_id: str = None,
    ) -> str:
        """Publish forecast issued event"""
        if not self._connected:
            await self.connect()

        if not self._is_available:
            logger.debug("NATS unavailable, skipping forecast_issued publish for field=%s", field_id)
            return str(uuid.uuid4())

        payload = {
            "field_id": field_id,
            "provider": provider,
            "forecast_days": days,
        }

        env = EventEnvelope.create(
            event_type=WEATHER_FORECAST_ISSUED,
            version=get_version(WEATHER_FORECAST_ISSUED),
            aggregate_id=field_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            payload=payload,
        )

        subject = _weather_scoped(WEATHER_FORECAST_ISSUED, tenant_id)
        try:
            await self.nc.publish(subject, json.dumps(env.to_dict(), default=str).encode())
        except Exception as e:
            logger.error(
                "Failed to publish forecast_issued event: subject=%s, field=%s, error=%s",
                subject,
                field_id,
                str(e),
            )
            raise

        logger.info("Published forecast_issued: field=%s, provider=%s, days=%d", field_id, provider, days)
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

        if not self._is_available:
            logger.debug("NATS unavailable, skipping irrigation_adjustment publish for field=%s", field_id)
            return str(uuid.uuid4())

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

        subject = _weather_scoped(IRRIGATION_ADJUSTMENT, tenant_id)
        try:
            await self.nc.publish(subject, json.dumps(env.to_dict(), default=str).encode())
        except Exception as e:
            logger.error(
                "Failed to publish irrigation_adjustment event: subject=%s, field=%s, error=%s",
                subject,
                field_id,
                str(e),
            )
            raise

        logger.info("Published irrigation_adjustment: field=%s, factor=%s", field_id, adjustment_factor)
        return env.event_id


# Singleton
_publisher: WeatherPublisher | None = None
# Lock is created lazily on first use inside the running event loop.
# Creating asyncio.Lock() at module level (before the loop starts) is deprecated
# since Python 3.10 and raises RuntimeError in Python 3.12+.
_publisher_lock: asyncio.Lock | None = None


async def get_publisher() -> WeatherPublisher:
    global _publisher, _publisher_lock
    if _publisher_lock is None:
        _publisher_lock = asyncio.Lock()
    async with _publisher_lock:
        if _publisher is None:
            _publisher = WeatherPublisher()
            try:
                await _publisher.connect()
            except Exception as e:
                logger.warning("Failed to connect to NATS: %s", e)
        return _publisher
