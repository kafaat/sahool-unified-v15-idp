#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - Comprehensive Services Simulator
محاكي شامل لجميع خدمات منصة سهول
═══════════════════════════════════════════════════════════════════════════════════════

This simulator covers ALL platform services:
- Authentication & Authorization
- Field Management
- Weather Services
- IoT & Sensors
- Billing & Payments
- Inventory Management
- Marketplace
- Chat & Messaging
- NDVI & Vegetation Analysis
- Yield Prediction
- Crop Intelligence
- Equipment Management
- Task Management
- Notifications & Alerts
- Research & Analytics
- Advisory Services

Usage:
    python comprehensive_simulator.py --duration 300 --users 50 --gateway http://localhost:8081

═══════════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import aiohttp
import argparse
import random
import time
import json
import uuid
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
import logging
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sahool-simulator")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

SAUDI_LOCATIONS = [
    {"name": "Al-Kharj", "lat": 24.1500, "lng": 47.3000, "region": "Riyadh"},
    {"name": "Al-Ahsa", "lat": 25.3800, "lng": 49.5900, "region": "Eastern"},
    {"name": "Tabuk", "lat": 28.3838, "lng": 36.5550, "region": "Tabuk"},
    {"name": "Wadi Al-Dawasir", "lat": 20.4910, "lng": 44.7800, "region": "Riyadh"},
    {"name": "Jizan", "lat": 16.8892, "lng": 42.5511, "region": "Jizan"},
    {"name": "Al-Jouf", "lat": 29.7850, "lng": 40.1000, "region": "Al-Jouf"},
    {"name": "Qassim", "lat": 26.3260, "lng": 43.9750, "region": "Qassim"},
    {"name": "Hail", "lat": 27.5114, "lng": 41.7208, "region": "Hail"},
]

CROP_TYPES = ["wheat", "barley", "dates", "tomatoes", "cucumbers", "alfalfa", "corn", "grapes"]
EQUIPMENT_TYPES = ["tractor", "harvester", "irrigation_pump", "sprayer", "seeder", "cultivator"]
TASK_TYPES = ["irrigation", "fertilization", "harvesting", "planting", "pest_control", "maintenance"]
ALERT_TYPES = ["weather", "pest", "disease", "equipment", "irrigation", "harvest"]

# ═══════════════════════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ServiceStats:
    requests: int = 0
    success: int = 0
    failed: int = 0
    total_latency_ms: float = 0.0

    @property
    def success_rate(self) -> float:
        return (self.success / self.requests * 100) if self.requests > 0 else 0.0

    @property
    def avg_latency(self) -> float:
        return (self.total_latency_ms / self.success) if self.success > 0 else 0.0

@dataclass
class SimulatorStats:
    start_time: float = field(default_factory=time.time)
    services: Dict[str, ServiceStats] = field(default_factory=dict)

    def get_service(self, name: str) -> ServiceStats:
        if name not in self.services:
            self.services[name] = ServiceStats()
        return self.services[name]

    def record(self, service: str, success: bool, latency_ms: float):
        stats = self.get_service(service)
        stats.requests += 1
        if success:
            stats.success += 1
            stats.total_latency_ms += latency_ms
        else:
            stats.failed += 1

# ═══════════════════════════════════════════════════════════════════════════════
# BASE SERVICE SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class ServiceSimulator(ABC):
    """Base class for service simulators."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str, stats: SimulatorStats):
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.stats = stats
        self.token: Optional[str] = None

    @property
    @abstractmethod
    def service_name(self) -> str:
        pass

    @property
    def headers(self) -> Dict[str, str]:
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Request-ID": str(uuid.uuid4()),
            "X-Tenant-ID": "tenant-001",
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    async def request(self, method: str, path: str, **kwargs) -> tuple[bool, Any]:
        url = f"{self.base_url}{path}"
        start = time.time()

        try:
            async with self.session.request(
                method, url,
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30),
                **kwargs
            ) as response:
                latency = (time.time() - start) * 1000
                success = response.status in [200, 201, 202, 204, 404]

                self.stats.record(self.service_name, success, latency)

                try:
                    data = await response.json()
                except:
                    data = await response.text()

                if not success:
                    logger.warning(f"{self.service_name}: {method} {path} -> {response.status}")

                return success, data

        except asyncio.TimeoutError:
            self.stats.record(self.service_name, False, 30000)
            logger.warning(f"{self.service_name}: {method} {path} -> Timeout")
            return False, None
        except Exception as e:
            self.stats.record(self.service_name, False, 0)
            logger.warning(f"{self.service_name}: {method} {path} -> {e}")
            return False, None

    @abstractmethod
    async def simulate(self):
        pass

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class AuthSimulator(ServiceSimulator):
    service_name = "auth"

    async def login(self, username: str, password: str) -> Optional[str]:
        success, data = await self.request("POST", "/api/auth/login", json={
            "username": username,
            "password": password,
        })
        if success and isinstance(data, dict):
            self.token = data.get("access_token") or data.get("token")
            return self.token
        return None

    async def simulate(self):
        users = [
            ("farmer@sahool.app", "farmer123"),
            ("admin@sahool.app", "admin123"),
            ("worker@sahool.app", "worker123"),
        ]
        user = random.choice(users)
        await self.login(user[0], user[1])

# ═══════════════════════════════════════════════════════════════════════════════
# FIELD SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class FieldSimulator(ServiceSimulator):
    service_name = "fields"

    async def list_fields(self):
        return await self.request("GET", "/api/fields?page=1&limit=20")

    async def get_field(self, field_id: int):
        return await self.request("GET", f"/api/fields/{field_id}")

    async def create_field(self):
        location = random.choice(SAUDI_LOCATIONS)
        return await self.request("POST", "/api/fields", json={
            "name": f"Field-{uuid.uuid4().hex[:8]}",
            "crop_type": random.choice(CROP_TYPES),
            "area_hectares": random.uniform(1, 100),
            "location": {
                "latitude": location["lat"] + random.uniform(-0.1, 0.1),
                "longitude": location["lng"] + random.uniform(-0.1, 0.1),
                "region": location["region"],
            },
            "soil_type": random.choice(["sandy", "clay", "loam", "silt"]),
            "irrigation_type": random.choice(["drip", "sprinkler", "flood", "center_pivot"]),
        })

    async def add_reading(self, field_id: int):
        return await self.request("POST", f"/api/fields/{field_id}/readings", json={
            "soil_moisture": random.uniform(15, 60),
            "soil_temperature": random.uniform(15, 40),
            "ph_level": random.uniform(5.5, 8.0),
            "nitrogen": random.uniform(10, 100),
            "phosphorus": random.uniform(5, 50),
            "potassium": random.uniform(50, 200),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    async def simulate(self):
        action = random.choice(["list", "get", "create", "reading"])
        if action == "list":
            await self.list_fields()
        elif action == "get":
            await self.get_field(random.randint(1, 50))
        elif action == "create":
            await self.create_field()
        else:
            await self.add_reading(random.randint(1, 50))

# ═══════════════════════════════════════════════════════════════════════════════
# WEATHER SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class WeatherSimulator(ServiceSimulator):
    service_name = "weather"

    async def get_current(self, lat: float, lng: float):
        return await self.request("GET", f"/api/weather/current?lat={lat}&lng={lng}")

    async def get_forecast(self, lat: float, lng: float, days: int = 7):
        return await self.request("GET", f"/api/weather/forecast?lat={lat}&lng={lng}&days={days}")

    async def get_historical(self, lat: float, lng: float, start: str, end: str):
        return await self.request("GET", f"/api/weather/historical?lat={lat}&lng={lng}&start={start}&end={end}")

    async def simulate(self):
        location = random.choice(SAUDI_LOCATIONS)
        action = random.choice(["current", "forecast", "historical"])

        if action == "current":
            await self.get_current(location["lat"], location["lng"])
        elif action == "forecast":
            await self.get_forecast(location["lat"], location["lng"], random.randint(3, 14))
        else:
            end = datetime.now()
            start = end - timedelta(days=30)
            await self.get_historical(
                location["lat"], location["lng"],
                start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
            )

# ═══════════════════════════════════════════════════════════════════════════════
# BILLING SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class BillingSimulator(ServiceSimulator):
    service_name = "billing"

    async def get_invoices(self):
        return await self.request("GET", "/api/billing/invoices?page=1&limit=20")

    async def get_subscription(self):
        return await self.request("GET", "/api/billing/subscription")

    async def get_usage(self, period: str = "monthly"):
        return await self.request("GET", f"/api/billing/usage?period={period}")

    async def create_payment(self):
        return await self.request("POST", "/api/billing/payments", json={
            "amount": random.uniform(100, 5000),
            "currency": "SAR",
            "payment_method": random.choice(["credit_card", "bank_transfer", "mada"]),
            "description": f"Payment for services - {datetime.now().strftime('%Y-%m')}",
        })

    async def simulate(self):
        action = random.choice(["invoices", "subscription", "usage", "payment"])
        if action == "invoices":
            await self.get_invoices()
        elif action == "subscription":
            await self.get_subscription()
        elif action == "usage":
            await self.get_usage(random.choice(["daily", "weekly", "monthly"]))
        else:
            await self.create_payment()

# ═══════════════════════════════════════════════════════════════════════════════
# INVENTORY SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class InventorySimulator(ServiceSimulator):
    service_name = "inventory"

    async def list_items(self, category: Optional[str] = None):
        path = "/api/inventory/items?page=1&limit=20"
        if category:
            path += f"&category={category}"
        return await self.request("GET", path)

    async def get_item(self, item_id: str):
        return await self.request("GET", f"/api/inventory/items/{item_id}")

    async def add_stock(self, item_id: str):
        return await self.request("POST", f"/api/inventory/items/{item_id}/stock", json={
            "quantity": random.randint(10, 500),
            "unit": random.choice(["kg", "liters", "units", "bags"]),
            "batch_number": f"BATCH-{uuid.uuid4().hex[:8]}",
            "expiry_date": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "supplier": f"Supplier-{random.randint(1, 10)}",
            "unit_cost": random.uniform(10, 500),
        })

    async def get_forecast(self, item_id: str):
        return await self.request("GET", f"/api/inventory/analytics/forecast/{item_id}?forecast_days=90")

    async def simulate(self):
        categories = ["seeds", "fertilizers", "pesticides", "tools", "equipment_parts"]
        action = random.choice(["list", "get", "stock", "forecast"])

        if action == "list":
            await self.list_items(random.choice([None] + categories))
        elif action == "get":
            await self.get_item(f"item-{random.randint(1, 100)}")
        elif action == "stock":
            await self.add_stock(f"item-{random.randint(1, 100)}")
        else:
            await self.get_forecast(f"item-{random.randint(1, 100)}")

# ═══════════════════════════════════════════════════════════════════════════════
# MARKETPLACE SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class MarketplaceSimulator(ServiceSimulator):
    service_name = "marketplace"

    async def list_products(self, category: Optional[str] = None):
        path = "/api/marketplace/products?page=1&limit=20"
        if category:
            path += f"&category={category}"
        return await self.request("GET", path)

    async def get_product(self, product_id: str):
        return await self.request("GET", f"/api/marketplace/products/{product_id}")

    async def create_order(self):
        return await self.request("POST", "/api/marketplace/orders", json={
            "items": [
                {
                    "product_id": f"prod-{random.randint(1, 100)}",
                    "quantity": random.randint(1, 10),
                }
                for _ in range(random.randint(1, 5))
            ],
            "shipping_address": {
                "city": random.choice(SAUDI_LOCATIONS)["name"],
                "street": f"Street {random.randint(1, 100)}",
                "postal_code": f"{random.randint(10000, 99999)}",
            },
            "payment_method": random.choice(["cod", "credit_card", "bank_transfer"]),
        })

    async def get_orders(self):
        return await self.request("GET", "/api/marketplace/orders?page=1&limit=20")

    async def simulate(self):
        categories = ["seeds", "fertilizers", "equipment", "irrigation", "organic"]
        action = random.choice(["list", "get", "order", "orders"])

        if action == "list":
            await self.list_products(random.choice([None] + categories))
        elif action == "get":
            await self.get_product(f"prod-{random.randint(1, 100)}")
        elif action == "order":
            await self.create_order()
        else:
            await self.get_orders()

# ═══════════════════════════════════════════════════════════════════════════════
# CHAT SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class ChatSimulator(ServiceSimulator):
    service_name = "chat"

    async def list_conversations(self):
        return await self.request("GET", "/api/chat/conversations")

    async def get_messages(self, conversation_id: str):
        return await self.request("GET", f"/api/chat/conversations/{conversation_id}/messages?limit=50")

    async def send_message(self, conversation_id: str):
        messages = [
            "ما هو أفضل وقت للري؟",
            "كيف يمكنني تحسين جودة التربة؟",
            "هل الطقس مناسب للحصاد؟",
            "أحتاج مساعدة في مكافحة الآفات",
            "What is the recommended fertilizer for wheat?",
            "How to detect early signs of disease?",
        ]
        return await self.request("POST", f"/api/chat/conversations/{conversation_id}/messages", json={
            "content": random.choice(messages),
            "type": "text",
        })

    async def start_ai_chat(self):
        return await self.request("POST", "/api/chat/ai/start", json={
            "topic": random.choice(["irrigation", "pest_control", "fertilization", "harvesting"]),
            "language": random.choice(["ar", "en"]),
        })

    async def simulate(self):
        action = random.choice(["list", "messages", "send", "ai"])
        conv_id = f"conv-{random.randint(1, 50)}"

        if action == "list":
            await self.list_conversations()
        elif action == "messages":
            await self.get_messages(conv_id)
        elif action == "send":
            await self.send_message(conv_id)
        else:
            await self.start_ai_chat()

# ═══════════════════════════════════════════════════════════════════════════════
# NDVI PROCESSOR SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class NDVISimulator(ServiceSimulator):
    service_name = "ndvi"

    async def get_ndvi(self, field_id: str):
        return await self.request("GET", f"/api/ndvi/fields/{field_id}/latest")

    async def get_timeseries(self, field_id: str):
        end = datetime.now()
        start = end - timedelta(days=90)
        return await self.request("GET",
            f"/api/ndvi/fields/{field_id}/timeseries?start={start.strftime('%Y-%m-%d')}&end={end.strftime('%Y-%m-%d')}"
        )

    async def request_processing(self, field_id: str):
        return await self.request("POST", "/api/ndvi/process", json={
            "field_id": field_id,
            "source": random.choice(["sentinel-2", "landsat-8", "modis"]),
            "date_range": {
                "start": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "end": datetime.now().strftime("%Y-%m-%d"),
            },
            "options": {
                "cloud_mask": True,
                "atmospheric_correction": True,
            }
        })

    async def get_change_analysis(self, field_id: str):
        return await self.request("GET",
            f"/api/ndvi/fields/{field_id}/change?date1=2024-01-01&date2=2024-06-01"
        )

    async def simulate(self):
        field_id = f"field-{random.randint(1, 50)}"
        action = random.choice(["latest", "timeseries", "process", "change"])

        if action == "latest":
            await self.get_ndvi(field_id)
        elif action == "timeseries":
            await self.get_timeseries(field_id)
        elif action == "process":
            await self.request_processing(field_id)
        else:
            await self.get_change_analysis(field_id)

# ═══════════════════════════════════════════════════════════════════════════════
# VEGETATION ANALYSIS SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class VegetationSimulator(ServiceSimulator):
    service_name = "vegetation"

    async def analyze_health(self, field_id: str):
        return await self.request("GET", f"/api/vegetation/fields/{field_id}/health")

    async def get_stress_map(self, field_id: str):
        return await self.request("GET", f"/api/vegetation/fields/{field_id}/stress-map")

    async def detect_anomalies(self, field_id: str):
        return await self.request("GET", f"/api/vegetation/fields/{field_id}/anomalies")

    async def get_growth_stage(self, field_id: str):
        return await self.request("GET", f"/api/vegetation/fields/{field_id}/growth-stage")

    async def simulate(self):
        field_id = f"field-{random.randint(1, 50)}"
        action = random.choice(["health", "stress", "anomalies", "growth"])

        if action == "health":
            await self.analyze_health(field_id)
        elif action == "stress":
            await self.get_stress_map(field_id)
        elif action == "anomalies":
            await self.detect_anomalies(field_id)
        else:
            await self.get_growth_stage(field_id)

# ═══════════════════════════════════════════════════════════════════════════════
# YIELD PREDICTION SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class YieldSimulator(ServiceSimulator):
    service_name = "yield"

    async def predict_yield(self, field_id: str):
        return await self.request("POST", f"/api/yield/predict", json={
            "field_id": field_id,
            "crop_type": random.choice(CROP_TYPES),
            "planting_date": (datetime.now() - timedelta(days=random.randint(30, 120))).strftime("%Y-%m-%d"),
            "area_hectares": random.uniform(1, 100),
        })

    async def get_historical(self, field_id: str):
        return await self.request("GET", f"/api/yield/fields/{field_id}/historical")

    async def compare_predictions(self, field_id: str):
        return await self.request("GET", f"/api/yield/fields/{field_id}/compare")

    async def get_factors(self, field_id: str):
        return await self.request("GET", f"/api/yield/fields/{field_id}/factors")

    async def simulate(self):
        field_id = f"field-{random.randint(1, 50)}"
        action = random.choice(["predict", "historical", "compare", "factors"])

        if action == "predict":
            await self.predict_yield(field_id)
        elif action == "historical":
            await self.get_historical(field_id)
        elif action == "compare":
            await self.compare_predictions(field_id)
        else:
            await self.get_factors(field_id)

# ═══════════════════════════════════════════════════════════════════════════════
# CROP INTELLIGENCE SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class CropIntelligenceSimulator(ServiceSimulator):
    service_name = "crop-intelligence"

    async def get_recommendations(self, field_id: str):
        return await self.request("GET", f"/api/crops/fields/{field_id}/recommendations")

    async def diagnose_disease(self):
        return await self.request("POST", "/api/crops/diagnose", json={
            "crop_type": random.choice(CROP_TYPES),
            "symptoms": random.sample([
                "yellow_leaves", "wilting", "spots", "stunted_growth",
                "brown_tips", "curling", "holes", "discoloration"
            ], random.randint(1, 4)),
            "location": random.choice(SAUDI_LOCATIONS)["region"],
            "growth_stage": random.choice(["seedling", "vegetative", "flowering", "fruiting", "mature"]),
        })

    async def get_pest_alerts(self, region: str):
        return await self.request("GET", f"/api/crops/pests/alerts?region={region}")

    async def get_planting_calendar(self, crop: str, region: str):
        return await self.request("GET", f"/api/crops/calendar?crop={crop}&region={region}")

    async def simulate(self):
        location = random.choice(SAUDI_LOCATIONS)
        action = random.choice(["recommendations", "diagnose", "pests", "calendar"])

        if action == "recommendations":
            await self.get_recommendations(f"field-{random.randint(1, 50)}")
        elif action == "diagnose":
            await self.diagnose_disease()
        elif action == "pests":
            await self.get_pest_alerts(location["region"])
        else:
            await self.get_planting_calendar(random.choice(CROP_TYPES), location["region"])

# ═══════════════════════════════════════════════════════════════════════════════
# EQUIPMENT SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class EquipmentSimulator(ServiceSimulator):
    service_name = "equipment"

    async def list_equipment(self):
        return await self.request("GET", "/api/equipment?page=1&limit=20")

    async def get_equipment(self, equipment_id: str):
        return await self.request("GET", f"/api/equipment/{equipment_id}")

    async def log_usage(self, equipment_id: str):
        return await self.request("POST", f"/api/equipment/{equipment_id}/usage", json={
            "hours": random.uniform(0.5, 8),
            "fuel_consumption": random.uniform(5, 50),
            "operator_id": f"operator-{random.randint(1, 20)}",
            "field_id": f"field-{random.randint(1, 50)}",
            "task_type": random.choice(TASK_TYPES),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    async def schedule_maintenance(self, equipment_id: str):
        return await self.request("POST", f"/api/equipment/{equipment_id}/maintenance", json={
            "type": random.choice(["routine", "repair", "inspection"]),
            "scheduled_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "description": "Scheduled maintenance",
            "priority": random.choice(["low", "medium", "high"]),
        })

    async def simulate(self):
        equipment_id = f"equip-{random.randint(1, 30)}"
        action = random.choice(["list", "get", "usage", "maintenance"])

        if action == "list":
            await self.list_equipment()
        elif action == "get":
            await self.get_equipment(equipment_id)
        elif action == "usage":
            await self.log_usage(equipment_id)
        else:
            await self.schedule_maintenance(equipment_id)

# ═══════════════════════════════════════════════════════════════════════════════
# TASK SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class TaskSimulator(ServiceSimulator):
    service_name = "tasks"

    async def list_tasks(self, status: Optional[str] = None):
        path = "/api/tasks?page=1&limit=20"
        if status:
            path += f"&status={status}"
        return await self.request("GET", path)

    async def create_task(self):
        return await self.request("POST", "/api/tasks", json={
            "title": f"Task-{uuid.uuid4().hex[:8]}",
            "type": random.choice(TASK_TYPES),
            "field_id": f"field-{random.randint(1, 50)}",
            "assignee_id": f"worker-{random.randint(1, 20)}",
            "priority": random.choice(["low", "medium", "high", "urgent"]),
            "due_date": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
            "description": "Auto-generated task for simulation",
            "estimated_hours": random.uniform(1, 8),
        })

    async def update_task(self, task_id: str):
        return await self.request("PATCH", f"/api/tasks/{task_id}", json={
            "status": random.choice(["pending", "in_progress", "completed", "cancelled"]),
            "progress": random.randint(0, 100),
        })

    async def get_worker_tasks(self, worker_id: str):
        return await self.request("GET", f"/api/tasks/workers/{worker_id}?status=pending")

    async def simulate(self):
        action = random.choice(["list", "create", "update", "worker"])

        if action == "list":
            await self.list_tasks(random.choice([None, "pending", "in_progress", "completed"]))
        elif action == "create":
            await self.create_task()
        elif action == "update":
            await self.update_task(f"task-{random.randint(1, 100)}")
        else:
            await self.get_worker_tasks(f"worker-{random.randint(1, 20)}")

# ═══════════════════════════════════════════════════════════════════════════════
# NOTIFICATION SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class NotificationSimulator(ServiceSimulator):
    service_name = "notifications"

    async def list_notifications(self, unread_only: bool = False):
        path = "/api/notifications?page=1&limit=20"
        if unread_only:
            path += "&unread=true"
        return await self.request("GET", path)

    async def mark_read(self, notification_id: str):
        return await self.request("PATCH", f"/api/notifications/{notification_id}/read")

    async def get_preferences(self):
        return await self.request("GET", "/api/notifications/preferences")

    async def update_preferences(self):
        return await self.request("PUT", "/api/notifications/preferences", json={
            "email": random.choice([True, False]),
            "push": random.choice([True, False]),
            "sms": random.choice([True, False]),
            "categories": {
                "weather": True,
                "tasks": True,
                "alerts": True,
                "marketing": random.choice([True, False]),
            }
        })

    async def simulate(self):
        action = random.choice(["list", "read", "preferences", "update"])

        if action == "list":
            await self.list_notifications(random.choice([True, False]))
        elif action == "read":
            await self.mark_read(f"notif-{random.randint(1, 100)}")
        elif action == "preferences":
            await self.get_preferences()
        else:
            await self.update_preferences()

# ═══════════════════════════════════════════════════════════════════════════════
# ALERT SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class AlertSimulator(ServiceSimulator):
    service_name = "alerts"

    async def list_alerts(self, alert_type: Optional[str] = None):
        path = "/api/alerts?page=1&limit=20"
        if alert_type:
            path += f"&type={alert_type}"
        return await self.request("GET", path)

    async def get_alert(self, alert_id: str):
        return await self.request("GET", f"/api/alerts/{alert_id}")

    async def acknowledge_alert(self, alert_id: str):
        return await self.request("POST", f"/api/alerts/{alert_id}/acknowledge", json={
            "action_taken": random.choice(["reviewed", "addressed", "scheduled", "dismissed"]),
            "notes": "Acknowledged via simulation",
        })

    async def get_active_alerts(self):
        return await self.request("GET", "/api/alerts/active")

    async def simulate(self):
        action = random.choice(["list", "get", "acknowledge", "active"])

        if action == "list":
            await self.list_alerts(random.choice([None] + ALERT_TYPES))
        elif action == "get":
            await self.get_alert(f"alert-{random.randint(1, 50)}")
        elif action == "acknowledge":
            await self.acknowledge_alert(f"alert-{random.randint(1, 50)}")
        else:
            await self.get_active_alerts()

# ═══════════════════════════════════════════════════════════════════════════════
# RESEARCH/ANALYTICS SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class ResearchSimulator(ServiceSimulator):
    service_name = "research"

    async def get_overview(self, period: str = "30d"):
        return await self.request("GET", f"/api/analytics/overview?period={period}")

    async def get_field_analytics(self, field_id: str):
        return await self.request("GET", f"/api/analytics/fields/{field_id}")

    async def generate_report(self):
        return await self.request("POST", "/api/reports/generate", json={
            "type": random.choice(["yield", "costs", "efficiency", "sustainability"]),
            "period": random.choice(["weekly", "monthly", "quarterly", "yearly"]),
            "fields": [f"field-{i}" for i in random.sample(range(1, 51), random.randint(1, 10))],
            "format": random.choice(["pdf", "excel", "csv"]),
        })

    async def get_benchmarks(self):
        return await self.request("GET", f"/api/analytics/benchmarks?crop={random.choice(CROP_TYPES)}")

    async def simulate(self):
        action = random.choice(["overview", "field", "report", "benchmarks"])

        if action == "overview":
            await self.get_overview(random.choice(["7d", "30d", "90d", "365d"]))
        elif action == "field":
            await self.get_field_analytics(f"field-{random.randint(1, 50)}")
        elif action == "report":
            await self.generate_report()
        else:
            await self.get_benchmarks()

# ═══════════════════════════════════════════════════════════════════════════════
# ADVISORY SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class AdvisorySimulator(ServiceSimulator):
    service_name = "advisory"

    async def get_recommendations(self, field_id: str):
        return await self.request("GET", f"/api/advisory/fields/{field_id}/recommendations")

    async def ask_expert(self):
        questions = [
            "ما أفضل موعد لزراعة القمح في منطقة الرياض؟",
            "كيف أتعامل مع نقص الري في الصيف؟",
            "What are the signs of nitrogen deficiency?",
            "How to improve soil drainage?",
        ]
        return await self.request("POST", "/api/advisory/ask", json={
            "question": random.choice(questions),
            "crop_type": random.choice(CROP_TYPES),
            "field_id": f"field-{random.randint(1, 50)}",
            "language": random.choice(["ar", "en"]),
        })

    async def get_seasonal_advice(self, region: str):
        return await self.request("GET", f"/api/advisory/seasonal?region={region}")

    async def get_best_practices(self, crop: str):
        return await self.request("GET", f"/api/advisory/best-practices?crop={crop}")

    async def simulate(self):
        location = random.choice(SAUDI_LOCATIONS)
        action = random.choice(["recommendations", "ask", "seasonal", "practices"])

        if action == "recommendations":
            await self.get_recommendations(f"field-{random.randint(1, 50)}")
        elif action == "ask":
            await self.ask_expert()
        elif action == "seasonal":
            await self.get_seasonal_advice(location["region"])
        else:
            await self.get_best_practices(random.choice(CROP_TYPES))

# ═══════════════════════════════════════════════════════════════════════════════
# IOT SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class IoTSimulator(ServiceSimulator):
    service_name = "iot"

    async def list_devices(self):
        return await self.request("GET", "/api/iot/devices?page=1&limit=20")

    async def get_device(self, device_id: str):
        return await self.request("GET", f"/api/iot/devices/{device_id}")

    async def send_telemetry(self, device_id: str):
        device_types = ["soil_sensor", "weather_station", "irrigation_controller", "gps_tracker"]
        device_type = random.choice(device_types)
        location = random.choice(SAUDI_LOCATIONS)

        payload = {
            "device_id": device_id,
            "device_type": device_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location": {
                "latitude": location["lat"] + random.uniform(-0.1, 0.1),
                "longitude": location["lng"] + random.uniform(-0.1, 0.1),
            },
            "battery_level": random.randint(10, 100),
            "signal_strength": -30 - random.randint(0, 70),
        }

        if device_type == "soil_sensor":
            payload["readings"] = {
                "moisture": random.uniform(15, 60),
                "temperature": random.uniform(15, 40),
                "ec": random.uniform(0.5, 3),
            }
        elif device_type == "weather_station":
            payload["readings"] = {
                "temperature": random.uniform(20, 50),
                "humidity": random.uniform(10, 60),
                "wind_speed": random.uniform(0, 30),
                "pressure": random.uniform(1000, 1030),
            }

        return await self.request("POST", "/api/iot/telemetry", json={
            "topic": f"sahool/iot/{device_type}/{device_id}",
            "payload": payload,
            "qos": 1,
        })

    async def get_device_history(self, device_id: str):
        return await self.request("GET", f"/api/iot/devices/{device_id}/history?limit=100")

    async def simulate(self):
        device_id = f"device-{random.randint(1, 100)}"
        action = random.choice(["list", "get", "telemetry", "history"])

        if action == "list":
            await self.list_devices()
        elif action == "get":
            await self.get_device(device_id)
        elif action == "telemetry":
            await self.send_telemetry(device_id)
        else:
            await self.get_device_history(device_id)

# ═══════════════════════════════════════════════════════════════════════════════
# INDICATORS SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class IndicatorsSimulator(ServiceSimulator):
    service_name = "indicators"

    async def get_kpis(self):
        return await self.request("GET", "/api/indicators/kpis")

    async def get_field_indicators(self, field_id: str):
        return await self.request("GET", f"/api/indicators/fields/{field_id}")

    async def get_sustainability_score(self):
        return await self.request("GET", "/api/indicators/sustainability")

    async def get_efficiency_metrics(self):
        return await self.request("GET", "/api/indicators/efficiency")

    async def simulate(self):
        action = random.choice(["kpis", "field", "sustainability", "efficiency"])

        if action == "kpis":
            await self.get_kpis()
        elif action == "field":
            await self.get_field_indicators(f"field-{random.randint(1, 50)}")
        elif action == "sustainability":
            await self.get_sustainability_score()
        else:
            await self.get_efficiency_metrics()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class ComprehensiveSimulator:
    """Main simulator orchestrating all service simulators."""

    SIMULATOR_CLASSES = [
        AuthSimulator,
        FieldSimulator,
        WeatherSimulator,
        BillingSimulator,
        InventorySimulator,
        MarketplaceSimulator,
        ChatSimulator,
        NDVISimulator,
        VegetationSimulator,
        YieldSimulator,
        CropIntelligenceSimulator,
        EquipmentSimulator,
        TaskSimulator,
        NotificationSimulator,
        AlertSimulator,
        ResearchSimulator,
        AdvisorySimulator,
        IoTSimulator,
        IndicatorsSimulator,
    ]

    def __init__(self, gateway_url: str, num_users: int, duration_seconds: int):
        self.gateway_url = gateway_url
        self.num_users = num_users
        self.duration_seconds = duration_seconds
        self.stats = SimulatorStats()
        self.running = False

    async def user_session(self, session: aiohttp.ClientSession, user_id: int):
        """Simulate a single user session."""
        simulators = [
            cls(session, self.gateway_url, self.stats)
            for cls in self.SIMULATOR_CLASSES
        ]

        # Authenticate first
        auth = simulators[0]
        await auth.simulate()
        token = auth.token

        # Share token with other simulators
        for sim in simulators[1:]:
            sim.token = token

        while self.running:
            # Random service simulation
            simulator = random.choice(simulators)
            await simulator.simulate()

            # Random delay between requests
            await asyncio.sleep(random.uniform(0.5, 3))

    async def run(self):
        """Run the comprehensive simulation."""
        self.running = True

        logger.info("=" * 80)
        logger.info("  SAHOOL IDP - Comprehensive Services Simulator")
        logger.info("  محاكي شامل لجميع خدمات منصة سهول")
        logger.info("=" * 80)
        logger.info(f"  Gateway URL:     {self.gateway_url}")
        logger.info(f"  Virtual Users:   {self.num_users}")
        logger.info(f"  Duration:        {self.duration_seconds}s")
        logger.info(f"  Services:        {len(self.SIMULATOR_CLASSES)}")
        logger.info("=" * 80)
        logger.info("")
        logger.info("  Services being simulated:")
        for cls in self.SIMULATOR_CLASSES:
            logger.info(f"    - {cls.service_name}")
        logger.info("")
        logger.info("=" * 80)

        async with aiohttp.ClientSession() as session:
            # Create user tasks
            tasks = [
                asyncio.create_task(self.user_session(session, i))
                for i in range(self.num_users)
            ]

            # Run for specified duration
            await asyncio.sleep(self.duration_seconds)
            self.running = False

            # Cancel all tasks
            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

        self.print_results()
        self.save_results()

    def print_results(self):
        """Print simulation results."""
        duration = time.time() - self.stats.start_time

        logger.info("")
        logger.info("=" * 80)
        logger.info("  SIMULATION RESULTS - نتائج المحاكاة")
        logger.info("=" * 80)
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info("")
        logger.info("  Service Results:")
        logger.info("  " + "-" * 76)
        logger.info(f"  {'Service':<25} {'Requests':>10} {'Success':>10} {'Failed':>10} {'Rate':>10} {'Avg Latency':>12}")
        logger.info("  " + "-" * 76)

        total_requests = 0
        total_success = 0
        total_failed = 0

        for name, stats in sorted(self.stats.services.items()):
            total_requests += stats.requests
            total_success += stats.success
            total_failed += stats.failed

            logger.info(
                f"  {name:<25} {stats.requests:>10} {stats.success:>10} {stats.failed:>10} "
                f"{stats.success_rate:>9.1f}% {stats.avg_latency:>10.1f}ms"
            )

        logger.info("  " + "-" * 76)
        overall_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
        logger.info(f"  {'TOTAL':<25} {total_requests:>10} {total_success:>10} {total_failed:>10} {overall_rate:>9.1f}%")
        logger.info("=" * 80)

    def save_results(self):
        """Save results to JSON file."""
        duration = time.time() - self.stats.start_time

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "configuration": {
                "gateway_url": self.gateway_url,
                "num_users": self.num_users,
                "duration_seconds": self.duration_seconds,
                "services_count": len(self.SIMULATOR_CLASSES),
            },
            "duration_actual": duration,
            "services": {
                name: {
                    "requests": stats.requests,
                    "success": stats.success,
                    "failed": stats.failed,
                    "success_rate": stats.success_rate,
                    "avg_latency_ms": stats.avg_latency,
                }
                for name, stats in self.stats.services.items()
            },
            "totals": {
                "requests": sum(s.requests for s in self.stats.services.values()),
                "success": sum(s.success for s in self.stats.services.values()),
                "failed": sum(s.failed for s in self.stats.services.values()),
            }
        }

        filename = f"comprehensive_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"  Results saved to: {filename}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL IDP - Comprehensive Services Simulator"
    )
    parser.add_argument(
        "--gateway", "-g",
        default="http://localhost:8081",
        help="Kong Gateway URL (default: http://localhost:8081)"
    )
    parser.add_argument(
        "--users", "-u",
        type=int,
        default=10,
        help="Number of virtual users (default: 10)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=60,
        help="Duration in seconds (default: 60)"
    )

    args = parser.parse_args()

    simulator = ComprehensiveSimulator(
        gateway_url=args.gateway,
        num_users=args.users,
        duration_seconds=args.duration
    )

    try:
        asyncio.run(simulator.run())
    except KeyboardInterrupt:
        logger.info("\nSimulation stopped by user")

if __name__ == "__main__":
    main()
