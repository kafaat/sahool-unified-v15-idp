"""
Task Automation Hook - SAHOOL Agro Advisor
Automatically creates FieldOps tasks from recommendations and plans
"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from nats.aio.client import Client as NATS

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
FIELDOPS_URL = os.getenv("FIELDOPS_URL", "http://fieldops:8080")

# Action to task type mapping
ACTION_TASK_MAPPING = {
    # Spraying
    "spray_copper": {
        "task_type": "spray",
        "title_ar": "رش بالنحاس",
        "title_en": "Copper Spray Application",
        "priority": "high",
    },
    "spray_mancozeb": {
        "task_type": "spray",
        "title_ar": "رش مانكوزيب",
        "title_en": "Mancozeb Spray Application",
        "priority": "high",
    },
    "spray_sulfur": {
        "task_type": "spray",
        "title_ar": "رش بالكبريت",
        "title_en": "Sulfur Spray Application",
        "priority": "medium",
    },
    "spray_neem_oil": {
        "task_type": "spray",
        "title_ar": "رش بزيت النيم",
        "title_en": "Neem Oil Spray",
        "priority": "medium",
    },
    # Manual tasks
    "remove_infected_parts": {
        "task_type": "manual",
        "title_ar": "إزالة الأجزاء المصابة",
        "title_en": "Remove Infected Parts",
        "priority": "high",
    },
    "improve_air_circulation": {
        "task_type": "manual",
        "title_ar": "تحسين التهوية",
        "title_en": "Improve Air Circulation",
        "priority": "low",
    },
    # Irrigation
    "avoid_overhead_irrigation": {
        "task_type": "irrigation",
        "title_ar": "تعديل نظام الري",
        "title_en": "Adjust Irrigation System",
        "priority": "medium",
    },
    # Monitoring
    "use_yellow_sticky_traps": {
        "task_type": "monitoring",
        "title_ar": "تركيب مصائد صفراء",
        "title_en": "Install Yellow Sticky Traps",
        "priority": "medium",
    },
}


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
        source: str = "agro_advisor",
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


class TaskAutomationHook:
    """
    Subscribes to advisor events and creates corresponding tasks
    """

    def __init__(self):
        self.nc: Optional[NATS] = None
        self.fieldops = FieldOpsClient()
        self._running = False

    async def start(self):
        """Start listening for events"""
        self.nc = NATS()
        await self.nc.connect(NATS_URL)
        self._running = True

        print("🔗 Task Automation Hook started")

        # Subscribe to recommendation events
        await self.nc.subscribe(
            "advisor.recommendation_issued",
            cb=self._handle_recommendation,
        )

        # Subscribe to fertilizer plan events
        await self.nc.subscribe(
            "advisor.fertilizer_plan_issued",
            cb=self._handle_fertilizer_plan,
        )

        # Subscribe to nutrient assessment events
        await self.nc.subscribe(
            "advisor.nutrient_assessment_issued",
            cb=self._handle_nutrient_assessment,
        )

        print("📡 Subscribed to advisor events")

    async def stop(self):
        """Stop the hook"""
        self._running = False
        if self.nc:
            await self.nc.close()
        await self.fieldops.close()
        print("🛑 Task Automation Hook stopped")

    async def _handle_recommendation(self, msg):
        """Handle recommendation_issued events"""
        try:
            envelope = json.loads(msg.data.decode())
            payload = envelope.get("payload", {})
            tenant_id = envelope.get("tenant_id")
            field_id = payload.get("field_id")

            print(f"📥 Received recommendation for field {field_id}")

            # Create tasks for each action
            actions = payload.get("actions", [])
            severity = payload.get("severity", "medium")
            urgency_hours = payload.get("details", {}).get("urgency_hours", 48)

            for action in actions[:3]:  # Max 3 tasks per recommendation
                task_info = ACTION_TASK_MAPPING.get(action)
                if not task_info:
                    continue

                # Calculate due date based on urgency
                due_date = datetime.now(timezone.utc) + timedelta(hours=urgency_hours)

                # Adjust priority based on severity
                priority = task_info["priority"]
                if severity == "high" or severity == "critical":
                    priority = "high"

                await self.fieldops.create_task(
                    tenant_id=tenant_id,
                    field_id=field_id,
                    title=task_info["title_ar"],
                    description=f"{payload.get('title_ar', '')} - {task_info['title_en']}",
                    task_type=task_info["task_type"],
                    priority=priority,
                    due_date=due_date,
                    source="agro_advisor",
                    metadata={
                        "action_id": action,
                        "confidence": payload.get("confidence"),
                        "category": payload.get("category"),
                        "correlation_id": envelope.get("correlation_id"),
                    },
                )

                print(f"✅ Created task: {task_info['title_en']} for field {field_id}")

        except Exception as e:
            print(f"❌ Error handling recommendation: {e}")

    async def _handle_fertilizer_plan(self, msg):
        """Handle fertilizer_plan_issued events"""
        try:
            envelope = json.loads(msg.data.decode())
            payload = envelope.get("payload", {})
            tenant_id = envelope.get("tenant_id")
            field_id = payload.get("field_id")

            print(f"📥 Received fertilizer plan for field {field_id}")

            plan = payload.get("plan", [])
            crop = payload.get("crop", "")
            stage = payload.get("stage", "")

            # Create task for each application
            for app in plan:
                timing_days = app.get("timing_days", 0)
                due_date = datetime.now(timezone.utc) + timedelta(days=timing_days)

                product = app.get("product", "")
                product_ar = app.get("product_ar", product)
                dose = app.get("dose_kg_per_ha", 0)
                total = app.get("total_kg", dose)
                method = app.get("method", "")

                await self.fieldops.create_task(
                    tenant_id=tenant_id,
                    field_id=field_id,
                    title=f"تسميد: {product_ar}",
                    description=f"تطبيق {product} بمعدل {dose} كجم/هكتار (إجمالي {total} كجم) - طريقة: {method}",
                    task_type="fertilization",
                    priority="medium",
                    due_date=due_date,
                    source="agro_advisor",
                    metadata={
                        "product": product,
                        "dose_kg_per_ha": dose,
                        "total_kg": total,
                        "method": method,
                        "crop": crop,
                        "stage": stage,
                        "correlation_id": envelope.get("correlation_id"),
                    },
                )

                print(f"✅ Created fertilization task: {product} for field {field_id}")

        except Exception as e:
            print(f"❌ Error handling fertilizer plan: {e}")

    async def _handle_nutrient_assessment(self, msg):
        """Handle nutrient_assessment_issued events"""
        try:
            envelope = json.loads(msg.data.decode())
            payload = envelope.get("payload", {})
            tenant_id = envelope.get("tenant_id")
            field_id = payload.get("field_id")

            print(f"📥 Received nutrient assessment for field {field_id}")

            nutrient = payload.get("nutrient", "")
            severity = payload.get("severity", "medium")
            title_ar = payload.get("title_ar", "")
            corrections = payload.get("corrections", [])

            # Create inspection task
            due_date = datetime.now(timezone.utc) + timedelta(
                hours=24 if severity == "high" else 48
            )

            await self.fieldops.create_task(
                tenant_id=tenant_id,
                field_id=field_id,
                title=f"فحص: {title_ar}",
                description=f"فحص وتأكيد {title_ar} - يرجى التقاط صور للأعراض",
                task_type="inspection",
                priority="high" if severity == "high" else "medium",
                due_date=due_date,
                source="agro_advisor",
                metadata={
                    "nutrient": nutrient,
                    "deficiency_id": payload.get("deficiency_id"),
                    "confidence": payload.get("confidence"),
                    "correlation_id": envelope.get("correlation_id"),
                },
            )

            print(f"✅ Created inspection task for {nutrient} deficiency")

            # Create correction tasks if high confidence
            if payload.get("confidence", 0) >= 0.7:
                for correction in corrections[:2]:  # Max 2 correction tasks
                    if correction.get("type") == "fertilizer":
                        product = correction.get("product", "")
                        dose = correction.get("dose_kg_ha", 0)

                        await self.fieldops.create_task(
                            tenant_id=tenant_id,
                            field_id=field_id,
                            title=f"تصحيح {nutrient}: {product}",
                            description=f"تطبيق {product} بمعدل {dose} كجم/هكتار لتصحيح {title_ar}",
                            task_type="fertilization",
                            priority="high" if severity == "high" else "medium",
                            due_date=due_date + timedelta(days=1),
                            source="agro_advisor",
                            metadata={
                                "correction_type": "fertilizer",
                                "product": product,
                                "dose_kg_ha": dose,
                                "nutrient": nutrient,
                            },
                        )

        except Exception as e:
            print(f"❌ Error handling nutrient assessment: {e}")


# Standalone runner
async def run_hook():
    """Run the task automation hook as standalone service"""
    hook = TaskAutomationHook()
    await hook.start()

    try:
        # Keep running
        import asyncio

        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await hook.stop()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_hook())
