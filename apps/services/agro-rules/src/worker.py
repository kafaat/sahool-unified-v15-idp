"""
Agro Rules Worker - SAHOOL
Event-driven worker that generates tasks from NDVI/Weather events
"""

import asyncio
import json
import logging
import os

from nats.aio.client import Client as NATS

from .fieldops_client import FieldOpsClient
from .rules import (
    TaskRule,
    rule_from_irrigation_adjustment,
    rule_from_ndvi,
    rule_from_ndvi_trend,
    rule_from_ndvi_weather,
    rule_from_phenology,
    rule_from_weather,
)

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
FIELDOPS_URL = os.getenv("FIELDOPS_URL", "http://field-management-service:3000")

_log = logging.getLogger(__name__)


def _safe_int(value, default: int = 0) -> int:
    """Coerce *value* to int, falling back to *default* on any failure.

    Event payloads can legitimately ship None, empty strings, or typed
    JSON numbers that aren't integers yet. A bare ``int(payload.get(
    ...))`` crashes the entire handler on any of those, so the whole
    event gets dropped for what's often a single-field issue. Coerce
    one field at a time and carry on.
    """
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value, default: float = 0.0) -> float:
    """Coerce *value* to float with the same guarantees as :func:`_safe_int`."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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

    def _is_duplicate_event(self, event_id: str | None) -> bool:
        """
        Idempotency check for an incoming event.

        Returns True iff `event_id` is a non-empty string we've already
        seen (so the caller should drop the message). Returns False
        otherwise — INCLUDING the case where `event_id` is None / empty.

        Rationale: the previous inline pattern
            if event_id in self._processed_events: return
            self._processed_events.add(event_id)
        poisoned the set on the first event with `event_id is None`,
        after which `None in self._processed_events` evaluated True and
        every subsequent event without an id was silently dropped —
        a hard-to-diagnose event blackhole. Gating both branches on
        `event_id` truthiness closes that trap: events without an id
        are simply processed every time (best-effort), and the set
        only ever contains real ids.
        """
        if not event_id:
            return False
        if event_id in self._processed_events:
            return True
        self._processed_events.add(event_id)
        return False

    @staticmethod
    def _extract_routing(env: dict) -> tuple[str | None, str | None, str | None, dict]:
        """
        Pull the four fields every handler needs out of an event envelope,
        whether they live at the envelope root or nested in `payload`.
        Returns (tenant_id, field_id, correlation_id, payload_dict).
        """
        payload = env.get("payload", env)
        tenant_id = env.get("tenant_id") or payload.get("tenant_id")
        field_id = env.get("aggregate_id") or payload.get("field_id")
        correlation_id = env.get("correlation_id")
        return tenant_id, field_id, correlation_id, payload

    async def start(self):
        """Start the worker"""
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

        # Subscribe to NDVI trend events (multi-week declining/volatile series)
        await self.nc.subscribe(
            "sahool.satellite.ndvi.trend",
            cb=self._handle_ndvi_trend,
        )
        await self.nc.subscribe(
            "sahool.tenant.*.satellite.ndvi.trend",
            cb=self._handle_ndvi_trend,
        )
        print("📡 Subscribed to sahool.satellite.ndvi.trend (+tenant-scoped)")

        # Subscribe to phenology-stage detection events
        await self.nc.subscribe(
            "sahool.phenology.stage_detected",
            cb=self._handle_phenology_stage_detected,
        )
        await self.nc.subscribe(
            "sahool.tenant.*.phenology.stage_detected",
            cb=self._handle_phenology_stage_detected,
        )
        print("📡 Subscribed to sahool.phenology.stage_detected (+tenant-scoped)")

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

        # Subscribe to terrain advisory events
        await self.nc.subscribe(
            "sahool.terrain.leveling_recommended",
            cb=self._handle_terrain_leveling,
        )
        print("📡 Subscribed to sahool.terrain.leveling_recommended")

        await self.nc.subscribe(
            "sahool.terrain.drainage_recommended",
            cb=self._handle_terrain_drainage,
        )
        print("📡 Subscribed to sahool.terrain.drainage_recommended")

        await self.nc.subscribe(
            "sahool.terrain.high_erosion_risk",
            cb=self._handle_terrain_erosion,
        )
        print("📡 Subscribed to sahool.terrain.high_erosion_risk")

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

            event_id = env.get("event_id")
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id")
            field_id = env.get("aggregate_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", {})

            if not tenant_id or not field_id:
                print(
                    f"⚠️ ndvi_computed: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

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
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id")
            field_id = env.get("aggregate_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", {})

            if not tenant_id or not field_id:
                print(
                    f"⚠️ ndvi_anomaly: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

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

    async def _handle_ndvi_trend(self, msg):
        """Handle multi-week NDVI trend events (satellite.ndvi.trend)."""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id")
            # AnalysisEvent uses `field_id`; ndvi-processor legacy events use `aggregate_id`.
            field_id = env.get("field_id") or env.get("aggregate_id")
            correlation_id = env.get("correlation_id") or event_id
            payload = env.get("data") or env.get("payload") or {}

            if not tenant_id or not field_id:
                print(
                    f"⚠️ ndvi_trend: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

            trend_direction = payload.get("trend_direction", "")
            # Safe casts — Copilot review #1704 (round 2): a null or
            # empty-string `anomaly_count`/`period_days` previously
            # blew up the whole handler with a TypeError.
            anomaly_count = _safe_int(payload.get("anomaly_count"), default=0)
            period_days = _safe_int(payload.get("period_days"), default=30)
            current_ndvi = payload.get("current_ndvi")

            _log.info(
                "ndvi_trend_received",
                extra={
                    "field_id": field_id,
                    "direction": trend_direction,
                    "anomalies": anomaly_count,
                    "period_days": period_days,
                },
            )

            if not tenant_id or not field_id:
                return

            task_rule = rule_from_ndvi_trend(
                trend_direction=trend_direction,
                anomaly_count=anomaly_count,
                period_days=period_days,
                current_ndvi=current_ndvi,
            )
            if task_rule:
                await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling NDVI trend: {e}")

    async def _handle_phenology_stage_detected(self, msg):
        """Handle phenology-stage detection events (phenology.stage_detected)."""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id")
            field_id = env.get("field_id") or env.get("aggregate_id")
            correlation_id = env.get("correlation_id") or event_id
            payload = env.get("data") or env.get("payload") or {}
            action_template = env.get("action_template")

            if not tenant_id or not field_id:
                print(
                    f"⚠️ phenology_stage: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

            current_stage = payload.get("current_stage", "")
            # Safe cast — per the trend handler above, a stray null
            # confidence must not drop the whole event on the floor.
            confidence = _safe_float(payload.get("confidence"), default=0.0)
            stage_ar = payload.get("stage_ar")
            stage_en = payload.get("stage_en")

            _log.info(
                "phenology_stage_received",
                extra={
                    "field_id": field_id,
                    "stage": current_stage,
                    "confidence": round(confidence, 3),
                },
            )

            if not tenant_id or not field_id:
                return

            task_rule = rule_from_phenology(
                current_stage=current_stage,
                confidence=confidence,
                stage_ar=stage_ar,
                stage_en=stage_en,
                action_template=action_template,
            )
            if task_rule:
                await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling phenology stage: {e}")

    async def _handle_weather_alert(self, msg):
        """Handle weather alert events"""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id")
            field_id = env.get("aggregate_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", {})

            if not tenant_id or not field_id:
                print(
                    f"⚠️ weather_alert: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

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
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id")
            field_id = env.get("aggregate_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", {})

            if not tenant_id or not field_id:
                print(
                    f"⚠️ irrigation_adjustment: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

            adjustment_factor = payload.get("adjustment_factor", 1.0)

            print(f"💧 Irrigation adjustment: field={field_id}, factor={adjustment_factor}")

            # Apply rules
            task_rule = rule_from_irrigation_adjustment(adjustment_factor, field_id)

            if task_rule:
                await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling irrigation adjustment: {e}")

    async def _handle_terrain_leveling(self, msg):
        """Handle terrain leveling recommended events — create a planning task"""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id") or env.get("payload", {}).get("tenant_id")
            field_id = env.get("aggregate_id") or env.get("payload", {}).get("field_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", env)

            if not tenant_id or not field_id:
                print(
                    f"⚠️ terrain_leveling: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

            slope = payload.get("slope_percent", 0)
            volume = payload.get("cut_fill_volume_m3", 0)
            cost = payload.get("estimated_cost")

            print(f"🏔️ Terrain leveling recommended: field={field_id}, slope={slope}%")

            desc_ar = f"تسوية الأرض مطلوبة (ميل: {slope}%. حجم الحفر/الردم: {volume} م³)"
            desc_en = f"Field leveling required (slope: {slope}%, cut/fill volume: {volume} m³)"
            if cost:
                desc_ar += f". التكلفة التقديرية: {cost}"
                desc_en += f". Estimated cost: {cost}"

            task_rule = TaskRule(
                title_ar="تخطيط تسوية الأرض",
                title_en="Field Leveling Planning",
                description_ar=desc_ar,
                description_en=desc_en,
                task_type="planning",
                priority="medium",
                urgency_hours=72,
            )
            await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling terrain leveling event: {e}")

    async def _handle_terrain_drainage(self, msg):
        """Handle terrain drainage recommended events — create a drainage task"""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id") or env.get("payload", {}).get("tenant_id")
            field_id = env.get("aggregate_id") or env.get("payload", {}).get("field_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", env)

            if not tenant_id or not field_id:
                print(
                    f"⚠️ terrain_drainage: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

            drainage_type = payload.get("drainage_type", "surface")
            priority = payload.get("priority", "medium")

            print(f"🌊 Drainage recommended: field={field_id}, type={drainage_type}")

            task_rule = TaskRule(
                title_ar=f"تحسين الصرف ({drainage_type})",
                title_en=f"Drainage Improvement ({drainage_type})",
                description_ar=f"يوصى بتحسين نظام الصرف من نوع '{drainage_type}' بناءً على تحليل التضاريس.",
                description_en=f"Drainage improvement of type '{drainage_type}' recommended based on terrain analysis.",
                task_type="planning",
                priority=priority if priority in ("urgent", "high", "medium", "low") else "medium",
                urgency_hours=48,
            )
            await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling terrain drainage event: {e}")

    async def _handle_terrain_erosion(self, msg):
        """Handle high erosion risk events — create an urgent inspection task"""
        try:
            env = json.loads(msg.data.decode())

            event_id = env.get("event_id")
            if self._is_duplicate_event(event_id):
                return

            tenant_id = env.get("tenant_id") or env.get("payload", {}).get("tenant_id")
            field_id = env.get("aggregate_id") or env.get("payload", {}).get("field_id")
            correlation_id = env.get("correlation_id")
            payload = env.get("payload", env)

            if not tenant_id or not field_id:
                print(
                    f"⚠️ terrain_erosion: missing routing "
                    f"(tenant_id={tenant_id}, field_id={field_id}) — dropping event"
                )
                return

            risk_level = payload.get("risk_level", "high")

            print(f"⚠️ High erosion risk: field={field_id}, level={risk_level}")

            task_rule = TaskRule(
                title_ar="فحص خطر التآكل",
                title_en="Erosion Risk Inspection",
                description_ar=f"خطر تآكل مرتفع ({risk_level}) تم اكتشافه. فحص الحقل وتقييم الحماية اللازمة.",
                description_en=f"High erosion risk ({risk_level}) detected. Inspect field and assess protection measures.",
                task_type="inspection",
                priority="high" if risk_level in ("high", "critical") else "medium",
                urgency_hours=24,
            )
            await self._create_task(tenant_id, field_id, task_rule, correlation_id)

        except Exception as e:
            print(f"❌ Error handling terrain erosion event: {e}")

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
