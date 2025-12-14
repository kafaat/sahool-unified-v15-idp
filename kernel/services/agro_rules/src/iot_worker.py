"""
IoT Rules Worker - SAHOOL Agro Rules
Subscribes to sensor events and creates tasks
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from nats.aio.client import Client as NATS

from .iot_rules import rule_from_sensor, evaluate_combined_rules, TaskRecommendation


NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
FIELDOPS_URL = os.getenv("FIELDOPS_URL", "http://fieldops:8080")


class FieldOpsClient:
    """Client for FieldOps task service"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or FIELDOPS_URL
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self._client

    async def create_task(
        self,
        tenant_id: str,
        field_id: str,
        title: str,
        description: str,
        task_type: str,
        priority: str,
        due_date: datetime,
        source: str = "iot_rules",
        metadata: dict = None,
    ) -> dict:
        """Create a new task in FieldOps"""
        client = await self._get_client()

        payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "title": title,
            "description": description,
            "task_type": task_type,
            "priority": priority,
            "due_date": due_date.isoformat(),
            "source": source,
            "metadata": metadata or {},
        }

        try:
            response = await client.post("/tasks", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to create task: {e}")
            raise

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class IoTRulesWorker:
    """
    Worker that subscribes to sensor events and applies rules
    """

    def __init__(self):
        self.nc: Optional[NATS] = None
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

        # Subscribe to sensor readings
        await self.nc.subscribe(
            "iot.sensor_reading",
            cb=self._handle_sensor_reading,
        )

        # Subscribe to specific sensor types for high-priority rules
        for sensor_type in ["soil_moisture", "air_temperature", "soil_ec"]:
            await self.nc.subscribe(
                f"iot.sensor.{sensor_type}",
                cb=self._handle_sensor_reading,
            )

        print("📡 Subscribed to IoT sensor events")

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
                tenant_id = data.get("tenant_id", "default")
            else:
                payload = data
                tenant_id = "default"

            field_id = payload.get("field_id")
            sensor_type = payload.get("sensor_type")
            value = payload.get("value")
            device_id = payload.get("device_id")

            if not all([field_id, sensor_type, value is not None]):
                return

            print(f"📥 Sensor: {sensor_type}={value} from {device_id} (field: {field_id})")

            # Store recent reading
            self._store_reading(field_id, sensor_type, value, device_id)

            # Evaluate single-sensor rules
            recommendation = rule_from_sensor(sensor_type, value)

            if recommendation:
                await self._create_task_from_recommendation(
                    tenant_id=tenant_id,
                    field_id=field_id,
                    recommendation=recommendation,
                    device_id=device_id,
                )

        except Exception as e:
            print(f"❌ Error handling sensor reading: {e}")

    def _store_reading(self, field_id: str, sensor_type: str, value: float, device_id: str):
        """Store recent reading for combined rule evaluation"""
        if field_id not in self._recent_readings:
            self._recent_readings[field_id] = []

        # Add reading
        self._recent_readings[field_id].append({
            "sensor_type": sensor_type,
            "value": value,
            "device_id": device_id,
            "timestamp": datetime.now(timezone.utc),
        })

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

                # Evaluate combined rules
                recommendations = evaluate_combined_rules(
                    [{"sensor_type": k, "value": v} for k, v in latest.items()]
                )

                for rec in recommendations:
                    await self._create_task_from_recommendation(
                        tenant_id="default",
                        field_id=field_id,
                        recommendation=rec,
                    )

    async def _create_task_from_recommendation(
        self,
        tenant_id: str,
        field_id: str,
        recommendation: TaskRecommendation,
        device_id: str = None,
    ):
        """Create task from recommendation with cooldown check"""
        # Create task key for deduplication
        task_key = f"{field_id}:{recommendation.task_type}:{recommendation.priority}"

        # Check cooldown
        if task_key in self._recent_tasks:
            last_created = self._recent_tasks[task_key]
            if datetime.now(timezone.utc) - last_created < timedelta(minutes=self._cooldown_minutes):
                print(f"⏳ Skipping task (cooldown): {recommendation.title_en}")
                return

        # Calculate due date
        due_date = datetime.now(timezone.utc) + timedelta(hours=recommendation.urgency_hours)

        # Add device info to metadata
        metadata = recommendation.metadata or {}
        if device_id:
            metadata["device_id"] = device_id

        try:
            await self.fieldops.create_task(
                tenant_id=tenant_id,
                field_id=field_id,
                title=recommendation.title_ar,
                description=recommendation.description_ar,
                task_type=recommendation.task_type,
                priority=recommendation.priority,
                due_date=due_date,
                source="iot_rules",
                metadata=metadata,
            )

            self._recent_tasks[task_key] = datetime.now(timezone.utc)
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
