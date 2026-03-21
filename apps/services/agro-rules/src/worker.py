"""
Agro Rules Worker - SAHOOL
Event-driven worker that generates tasks from NDVI/Weather events
"""

from __future__ import annotations

import asyncio
import json
import os

_nats_available = False
try:
    from nats.aio.client import Client as NATS

    _nats_available = True
except ImportError:
    NATS = None  # type: ignore[assignment,misc]

from .fieldops_client import FieldOpsClient
from .rules import (
    TaskRule,
    rule_from_irrigation_adjustment,
    rule_from_ndvi,
    rule_from_ndvi_weather,
    rule_from_weather,
)

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
FIELDOPS_URL = os.getenv("FIELDOPS_URL", "http://field-management-service:3000")


class AgroRulesWorker:
    """
    Event-driven worker that subscribes to NDVI and Weather events
    and creates tasks in FieldOps based on rules
    """

    def __init__(self):
        self.nc: NATS | None = None
        self.fieldops = FieldOpsClient(FIELDOPS_URL)
        self._running = False
        self._recent_ndvi: dict[str, dict] = {}  # field_id -> last NDVI data
        self._recent_weather: dict[str, dict] = {}  # field_id -> last weather data
        self._processed_events: set[str] = set()  # Deduplication

    async def start(self):
        """Start the worker"""
        if not _nats_available:
            raise RuntimeError("NATS client library is not installed. Install with: pip install nats-py")
        self.nc = NATS()
        await self.nc.connect(NATS_URL)
        self._running = True

        print("🚀 Agro Rules Worker started")
        print(f"   NATS: {NATS_URL}")
        print(f"   FieldOps: {FIELDOPS_URL}")

        # Subscribe to NDVI events (under satellite domain)
        await self.nc.subscribe(
            "sahool.satellite.ndvi.computed",
            cb=self._handle_ndvi_computed,
        )
        print("📡 Subscribed to sahool.satellite.ndvi.computed")

        # Subscribe to NDVI anomaly events
        await self.nc.subscribe(
            "sahool.satellite.ndvi.anomaly",
            cb=self._handle_ndvi_anomaly,
        )
        print("📡 Subscribed to sahool.satellite.ndvi.anomaly")

        # Subscribe to Weather alerts
        await self.nc.subscribe(
            "sahool.weather.alert",
            cb=self._handle_weather_alert,
        )
        print("📡 Subscribed to sahool.weather.alert")

        # Subscribe to irrigation adjustments
        await self.nc.subscribe(
            "sahool.weather.irrigation_adjustment",
            cb=self._handle_irrigation_adjustment,
        )
        print("📡 Subscribed to sahool.weather.irrigation_adjustment")

        print("✅ Agro Rules Worker ready")

    async def stop(self):
        """Stop the worker"""
        self._running = False
        if self.nc:
            await self.nc.close()
        await self.fieldops.close()
        print("🛑 Agro Rules Worker stopped")

    async def _handle_ndvi_computed(self, msg):
        """Handle NDVI computed events"""
        try:
            env = json.loads(msg.data.decode())

            # Deduplication
            event_id = env.get("event_id")
            if event_id in self._processed_events:
                return
            self._processed_events.add(event_id)

            tenant_id = env.get("tenant_id")
            field_id = env.get("aggregate_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", {})

            print(f"📥 NDVI computed: field={field_id}, ndvi={payload.get('ndvi_mean')}")

            # Store for combined rules
            self._recent_ndvi[field_id] = payload

            # Apply rules
            ndvi_mean = payload.get("ndvi_mean", 0)
            ndvi_trend = payload.get("ndvi_trend_7d", 0)

            task_rule = rule_from_ndvi(ndvi_mean, ndvi_trend)

            if task_rule:
                await self._create_task(tenant_id, field_id, task_rule, correlation_id)

            # Check combined rules if we have weather data
            if field_id in self._recent_weather:
                weather = self._recent_weather[field_id]
                combined_rule = rule_from_ndvi_weather(
                    ndvi_mean=ndvi_mean,
                    ndvi_trend=ndvi_trend,
                    temp_c=weather.get("temp_c", 25),
                    humidity_pct=weather.get("humidity_pct", 50),
                )
                if combined_rule:
                    await self._create_task(tenant_id, field_id, combined_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling NDVI event: {e}")

    async def _handle_ndvi_anomaly(self, msg):
        """Handle NDVI anomaly events"""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if event_id in self._processed_events:
                return
            self._processed_events.add(event_id)

            tenant_id = env.get("tenant_id")
            field_id = env.get("aggregate_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", {})

            anomaly_type = payload.get("anomaly_type")
            severity = payload.get("severity")
            z_score = payload.get("z_score", 0)

            print(f"🚨 NDVI anomaly: field={field_id}, type={anomaly_type}, severity={severity}")

            # Create inspection task for anomalies
            if severity in ("medium", "high"):
                task_rule = TaskRule(
                    title_ar=f"فحص شذوذ NDVI ({anomaly_type})",
                    title_en=f"NDVI Anomaly Inspection ({anomaly_type})",
                    description_ar=f"اكتشاف شذوذ في NDVI (z-score: {z_score}). فحص الحقل للمشاكل المحتملة.",
                    description_en=f"NDVI anomaly detected (z-score: {z_score}). Inspect field for potential issues.",
                    task_type="inspection",
                    priority="high" if severity == "high" else "medium",
                    urgency_hours=12 if severity == "high" else 24,
                )
                await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling NDVI anomaly: {e}")

    async def _handle_weather_alert(self, msg):
        """Handle weather alert events"""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if event_id in self._processed_events:
                return
            self._processed_events.add(event_id)

            tenant_id = env.get("tenant_id")
            field_id = env.get("aggregate_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", {})

            alert_type = payload.get("alert_type")
            severity = payload.get("severity")

            print(f"🌤️ Weather alert: field={field_id}, type={alert_type}, severity={severity}")

            # Store for combined rules
            self._recent_weather[field_id] = {
                "alert_type": alert_type,
                "severity": severity,
                "temp_c": payload.get("temp_c", 25),
                "humidity_pct": payload.get("humidity_pct", 50),
            }

            # Apply rules
            task_rule = rule_from_weather(alert_type, severity)

            if task_rule:
                await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling weather alert: {e}")

    async def _handle_irrigation_adjustment(self, msg):
        """Handle irrigation adjustment events"""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if event_id in self._processed_events:
                return
            self._processed_events.add(event_id)

            tenant_id = env.get("tenant_id")
            field_id = env.get("aggregate_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", {})

            adjustment_factor = payload.get("adjustment_factor", 1.0)

            print(f"💧 Irrigation adjustment: field={field_id}, factor={adjustment_factor}")

            # Apply rules
            task_rule = rule_from_irrigation_adjustment(adjustment_factor, field_id)

            if task_rule:
                await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling irrigation adjustment: {e}")

    async def _create_task(
        self,
        tenant_id: str,
        field_id: str,
        rule: TaskRule,
        correlation_id: str,
    ):
        """Create task from rule"""
        try:
            await self.fieldops.create_task(
                tenant_id=tenant_id,
                field_id=field_id,
                title=rule.title_ar,
                description=rule.description_ar,
                priority=rule.priority,
                correlation_id=correlation_id,
                task_type=rule.task_type,
                due_hours=rule.urgency_hours,
                source="agro_rules",
                metadata={
                    "title_en": rule.title_en,
                    "description_en": rule.description_en,
                },
            )
        except Exception as e:
            print(f"❌ Failed to create task: {e}")

    def _cleanup_processed_events(self):
        """Cleanup old processed events to prevent memory growth"""
        if len(self._processed_events) > 10000:
            # Keep last 5000
            self._processed_events = set(list(self._processed_events)[-5000:])


async def main():
    """Main entry point"""
    worker = AgroRulesWorker()
    await worker.start()

    try:
        while True:
            await asyncio.sleep(60)
            worker._cleanup_processed_events()
    except KeyboardInterrupt:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
