"""
IoT Rules Worker - SAHOOL Agro Rules
Subscribes to sensor events and creates tasks
"""

import asyncio
import json
import os
from datetime import UTC, datetime, timedelta

from nats.aio.client import Client as NATS

from .fieldops_client import FieldOpsClient
from .iot_rules import TaskRecommendation, evaluate_combined_rules, rule_from_sensor

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")


class IoTRulesWorker:
    """
    Worker that subscribes to sensor events and applies rules
    """

    def __init__(self):
        self.nc: NATS | None = None
        self.fieldops = FieldOpsClient()
        self._running = False
        self._recent_readings: dict[str, list[dict]] = {}  # field_id -> recent readings
        self._recent_tasks: dict[str, datetime] = {}  # task_key -> last_created
        self._cooldown_minutes = 30  # Don't create duplicate tasks within cooldown

    async def start(self):
        """Start the worker"""
        self.nc = NATS()
        await self.nc.connect(NATS_URL)
        self._running = True

        print("🔧 IoT Rules Worker started")

        # Subscribe to sensor readings (unified sahool.* namespace)
        await self.nc.subscribe(
            "sahool.iot.sensor.reading",
            cb=self._handle_sensor_reading,
        )

        # Subscribe to specific sensor types for high-priority rules
        for sensor_type in ["soil_moisture", "air_temperature", "soil_ec"]:
            await self.nc.subscribe(
                f"sahool.iot.sensor.{sensor_type}",
                cb=self._handle_sensor_reading,
            )

        print("📡 Subscribed to sahool.iot.* sensor events")

        # Start periodic combined rule evaluation
        asyncio.create_task(self._periodic_evaluation())

    async def stop(self):
        """Stop the worker"""
        self._running = False
        if self.nc:
            await self.nc.close()
        await self.fieldops.close()
        print("🛑 IoT Rules Worker stopped")

    async def _handle_sensor_reading(self, msg):
        """Handle incoming sensor reading"""
        try:
            # Parse message
            data = json.loads(msg.data.decode())

            # Extract payload (may be wrapped in envelope or direct)
            if "payload" in data:
                payload = data["payload"]
                tenant_id = data.get("tenant_id") or payload.get("tenant_id")
            else:
                payload = data
                tenant_id = data.get("tenant_id")

            if not tenant_id:
                print("⚠️ Missing tenant_id in sensor reading, skipping")
                return

            field_id = payload.get("field_id")
            sensor_type = payload.get("sensor_type")
            value = payload.get("value")
            device_id = payload.get("device_id")

            if not all([field_id, sensor_type, value is not None]):
                return

            print(f"📥 Sensor: {sensor_type}={value} from {device_id} (field: {field_id})")

            # Store recent reading
            self._store_reading(field_id, sensor_type, value, device_id, tenant_id)

            # Evaluate single-sensor rules
            recommendation = rule_from_sensor(sensor_type, value)

            # Extract correlation_id for traceability
            correlation_id = data.get("correlation_id")

            if recommendation:
                await self._create_task_from_recommendation(
                    tenant_id=tenant_id,
                    field_id=field_id,
                    recommendation=recommendation,
                    device_id=device_id,
                    correlation_id=correlation_id,
                )

        except Exception as e:
            print(f"❌ Error handling sensor reading: {e}")

    def _store_reading(self, field_id: str, sensor_type: str, value: float, device_id: str, tenant_id: str = None):
        """Store recent reading for combined rule evaluation"""
        if field_id not in self._recent_readings:
            self._recent_readings[field_id] = []

        # Add reading
        self._recent_readings[field_id].append(
            {
                "tenant_id": tenant_id,
                "sensor_type": sensor_type,
                "value": value,
                "device_id": device_id,
                "timestamp": datetime.now(UTC),
            }
        )

        # Keep only last 10 readings per field
        self._recent_readings[field_id] = self._recent_readings[field_id][-10:]

    async def _periodic_evaluation(self):
        """Periodically evaluate combined rules"""
        while self._running:
            await asyncio.sleep(300)  # Every 5 minutes

            for field_id, readings in self._recent_readings.items():
                if not readings:
                    continue

                # Get latest reading per sensor type
                latest = {}
                for r in readings:
                    latest[r["sensor_type"]] = r["value"]

                # Extract tenant_id from the most recent reading
                tenant_id = next(
                    (r["tenant_id"] for r in reversed(readings) if r.get("tenant_id")),
                    None,
                )
                if not tenant_id:
                    continue  # Skip fields without tenant context

                # Evaluate combined rules
                recommendations = evaluate_combined_rules(
                    [{"sensor_type": k, "value": v} for k, v in latest.items()]
                )

                for rec in recommendations:
                    await self._create_task_from_recommendation(
                        tenant_id=tenant_id,
                        field_id=field_id,
                        recommendation=rec,
                    )

    async def _create_task_from_recommendation(
        self,
        tenant_id: str,
        field_id: str,
        recommendation: TaskRecommendation,
        device_id: str = None,
        correlation_id: str = None,
    ):
        """Create task from recommendation with cooldown check"""
        # Create task key for deduplication
        task_key = f"{field_id}:{recommendation.task_type}:{recommendation.priority}"

        # Check cooldown
        if task_key in self._recent_tasks:
            last_created = self._recent_tasks[task_key]
            if datetime.now(UTC) - last_created < timedelta(minutes=self._cooldown_minutes):
                print(f"⏳ Skipping task (cooldown): {recommendation.title_en}")
                return

        # Add device info and English content to metadata
        metadata = recommendation.metadata or {}
        if device_id:
            metadata["device_id"] = device_id
        metadata["title_en"] = recommendation.title_en
        metadata["description_en"] = recommendation.description_en

        try:
            await self.fieldops.create_task(
                tenant_id=tenant_id,
                field_id=field_id,
                title=recommendation.title_ar,
                description=recommendation.description_ar,
                task_type=recommendation.task_type,
                priority=recommendation.priority,
                due_hours=recommendation.urgency_hours,
                correlation_id=correlation_id,
                source="iot_rules",
                metadata=metadata,
            )

            self._recent_tasks[task_key] = datetime.now(UTC)
            print(f"✅ Created task: {recommendation.title_en} (field: {field_id})")

        except Exception as e:
            print(f"❌ Failed to create task: {e}")


# Standalone runner
async def run_worker():
    """Run the IoT rules worker"""
    worker = IoTRulesWorker()
    await worker.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(run_worker())
