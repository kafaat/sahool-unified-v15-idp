#!/usr/bin/env python3
"""
SAHOOL Demo Data Service
خدمة البيانات التجريبية لمنصة سهول

This service simulates real-world data by sending HTTP requests
to various API endpoints, creating a realistic demo environment.
"""

import asyncio
import logging
import os
import random
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("demo-data")

# Configuration
KONG_URL = os.getenv("KONG_URL", "http://kong:8000")
API_KEY = os.getenv("API_KEY", "demo-api-key")
TENANT_ID = os.getenv("TENANT_ID", "a0000000-0000-0000-0000-000000000001")
USER_ID = os.getenv("USER_ID", "b0000000-0000-0000-0000-000000000001")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "30"))
DEMO_MODE = os.getenv("DEMO_MODE", "continuous")  # continuous, once, batch

# Demo field IDs
FIELD_IDS = [
    "d0000000-0000-0000-0000-000000000001",
    "d0000000-0000-0000-0000-000000000002",
    "d0000000-0000-0000-0000-000000000003",
]

# Demo device IDs
DEVICE_IDS = [
    "SOIL-001",
    "SOIL-002",
    "WEATHER-001",
    "WATER-001",
    "CAM-001",
]

# Saudi Arabia governorates
GOVERNORATES = ["Riyadh", "Makkah", "Madinah", "Eastern Province", "Qassim", "Asir"]

# Crop types
CROPS = ["wheat", "barley", "dates", "tomatoes", "alfalfa", "cucumbers", "grapes"]


class DemoDataGenerator:
    """Generates realistic demo data for SAHOOL platform"""

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=KONG_URL,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": API_KEY,
                "X-Tenant-ID": TENANT_ID,
                "X-User-ID": USER_ID,
            },
        )
        self.stats = {
            "requests_sent": 0,
            "requests_success": 0,
            "requests_failed": 0,
        }

    async def close(self):
        await self.client.aclose()

    # ─────────────────────────────────────────────────────────────────────────
    # Weather Data
    # ─────────────────────────────────────────────────────────────────────────

    def generate_weather_data(self) -> dict[str, Any]:
        """Generate realistic weather data for Saudi Arabia"""
        return {
            "location_id": random.choice(["riyadh", "jeddah", "dammam", "al-kharj"]),
            "temperature_celsius": round(random.uniform(25, 45), 1),
            "humidity_percent": round(random.uniform(10, 60), 1),
            "wind_speed_ms": round(random.uniform(0, 15), 1),
            "wind_direction_degrees": random.randint(0, 360),
            "pressure_hpa": round(random.uniform(1005, 1025), 1),
            "uv_index": round(random.uniform(5, 11), 1),
            "conditions": random.choice(["Clear", "Partly Cloudy", "Sunny", "Hazy"]),
            "recorded_at": datetime.now(UTC).isoformat(),
        }

    async def send_weather_data(self):
        """Send weather data to weather service"""
        data = self.generate_weather_data()
        try:
            response = await self.client.post("/api/v1/weather/readings", json=data)
            self._log_response("Weather", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"Weather connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"Weather request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Weather HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # IoT Sensor Data
    # ─────────────────────────────────────────────────────────────────────────

    def generate_sensor_data(self) -> dict[str, Any]:
        """Generate realistic IoT sensor readings"""
        device_id = random.choice(DEVICE_IDS)
        device_type = device_id.split("-")[0].lower()

        readings = {
            "device_id": device_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "battery_level": round(random.uniform(20, 100), 1),
        }

        if device_type == "soil":
            readings.update(
                {
                    "soil_moisture": round(random.uniform(20, 80), 2),
                    "soil_temperature": round(random.uniform(15, 35), 2),
                    "soil_ph": round(random.uniform(6.0, 8.0), 2),
                    "ec_value": round(random.uniform(0.5, 3.0), 3),
                }
            )
        elif device_type == "weather":
            readings.update(
                {
                    "air_temperature": round(random.uniform(25, 45), 2),
                    "humidity": round(random.uniform(10, 60), 2),
                    "wind_speed": round(random.uniform(0, 20), 2),
                    "solar_radiation": round(random.uniform(200, 1000), 1),
                }
            )
        elif device_type == "water":
            readings.update(
                {
                    "flow_rate": round(random.uniform(0, 100), 2),
                    "total_volume": round(random.uniform(1000, 50000), 1),
                    "pressure": round(random.uniform(1, 5), 2),
                }
            )

        return readings

    async def send_sensor_data(self):
        """Send IoT sensor data to IoT gateway"""
        data = self.generate_sensor_data()
        try:
            response = await self.client.post("/api/v1/iot/readings", json=data)
            self._log_response("IoT Sensor", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"IoT connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"IoT request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"IoT HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # NDVI Data
    # ─────────────────────────────────────────────────────────────────────────

    def generate_ndvi_data(self) -> dict[str, Any]:
        """Generate NDVI vegetation index data"""
        field_id = random.choice(FIELD_IDS)
        ndvi_mean = round(random.uniform(0.3, 0.9), 4)

        return {
            "field_id": field_id,
            "capture_date": datetime.now(UTC).date().isoformat(),
            "satellite": random.choice(["Sentinel-2", "Landsat-8", "Planet"]),
            "cloud_coverage_percent": round(random.uniform(0, 30), 1),
            "ndvi_mean": ndvi_mean,
            "ndvi_min": round(ndvi_mean - random.uniform(0.1, 0.2), 4),
            "ndvi_max": round(ndvi_mean + random.uniform(0.1, 0.2), 4),
            "ndvi_std_dev": round(random.uniform(0.02, 0.1), 4),
            "classification": self._classify_ndvi(ndvi_mean),
            "health_score": round(ndvi_mean * 100, 1),
        }

    def _classify_ndvi(self, ndvi: float) -> str:
        if ndvi >= 0.8:
            return "excellent"
        elif ndvi >= 0.6:
            return "good"
        elif ndvi >= 0.4:
            return "moderate"
        elif ndvi >= 0.2:
            return "poor"
        else:
            return "critical"

    async def send_ndvi_data(self):
        """Send NDVI data to NDVI engine"""
        data = self.generate_ndvi_data()
        try:
            response = await self.client.post("/api/v1/ndvi/records", json=data)
            self._log_response("NDVI", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"NDVI connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"NDVI request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"NDVI HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Alert Data
    # ─────────────────────────────────────────────────────────────────────────

    def generate_alert_data(self) -> dict[str, Any]:
        """Generate agricultural alerts"""
        alert_types = [
            {
                "category": "weather",
                "title": "High Temperature Alert",
                "title_ar": "تنبيه درجة حرارة مرتفعة",
                "message": "Temperature exceeds 40°C in field area",
                "severity": "warning",
            },
            {
                "category": "irrigation",
                "title": "Low Soil Moisture",
                "title_ar": "انخفاض رطوبة التربة",
                "message": "Soil moisture below optimal threshold",
                "severity": "warning",
            },
            {
                "category": "pest",
                "title": "Pest Activity Detected",
                "title_ar": "نشاط آفات مكتشف",
                "message": "Unusual pest activity detected in sector",
                "severity": "critical",
            },
            {
                "category": "harvest",
                "title": "Harvest Ready",
                "title_ar": "جاهز للحصاد",
                "message": "Crop maturity indicators suggest harvest time",
                "severity": "info",
            },
        ]

        alert = random.choice(alert_types)
        return {
            "tenant_id": TENANT_ID,
            "field_id": random.choice(FIELD_IDS),
            "title": alert["title"],
            "title_ar": alert["title_ar"],
            "message": alert["message"],
            "category": alert["category"],
            "severity": alert["severity"],
            "source_service": "demo-data",
        }

    async def send_alert(self):
        """Send alert to notification service"""
        data = self.generate_alert_data()
        try:
            response = await self.client.post("/api/v1/alerts", json=data)
            self._log_response("Alert", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"Alert connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"Alert request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Alert HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Task Data
    # ─────────────────────────────────────────────────────────────────────────

    def generate_task_data(self) -> dict[str, Any]:
        """Generate agricultural task"""
        task_types = [
            ("irrigation", "Check irrigation system", "فحص نظام الري"),
            ("fertilization", "Apply fertilizer", "تطبيق السماد"),
            ("inspection", "Field inspection", "فحص الحقل"),
            ("harvest", "Prepare for harvest", "التحضير للحصاد"),
            ("pesticide", "Apply pest control", "تطبيق مكافحة الآفات"),
        ]

        task = random.choice(task_types)
        scheduled_date = datetime.now(UTC) + timedelta(days=random.randint(1, 7))

        return {
            "tenant_id": TENANT_ID,
            "field_id": random.choice(FIELD_IDS),
            "title": task[1],
            "title_ar": task[2],
            "type": task[0],
            "status": "pending",
            "priority": random.choice(["low", "medium", "high"]),
            "scheduled_date": scheduled_date.date().isoformat(),
            "assigned_to": USER_ID,
        }

    async def send_task(self):
        """Send task to task service"""
        data = self.generate_task_data()
        try:
            response = await self.client.post("/api/v1/tasks", json=data)
            self._log_response("Task", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"Task connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"Task request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Task HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Yield Prediction Request
    # ─────────────────────────────────────────────────────────────────────────

    def generate_yield_prediction_request(self) -> dict[str, Any]:
        """Generate yield prediction request"""
        return {
            "field_id": random.choice(FIELD_IDS),
            "crop_type": random.choice(CROPS),
            "planting_date": (datetime.now(UTC) - timedelta(days=random.randint(30, 120)))
            .date()
            .isoformat(),
            "area_hectares": round(random.uniform(5, 150), 2),
            "irrigation_type": random.choice(["drip", "sprinkler", "flood", "center_pivot"]),
            "soil_type": random.choice(["clay", "sandy", "loam", "silt"]),
        }

    async def request_yield_prediction(self):
        """Request yield prediction from ML service"""
        data = self.generate_yield_prediction_request()
        try:
            response = await self.client.post("/api/v1/yield-prediction/predict", json=data)
            self._log_response("Yield Prediction", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"Yield prediction connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"Yield prediction request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Yield prediction HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Field Health Check
    # ─────────────────────────────────────────────────────────────────────────

    async def check_field_health(self):
        """Query field health status"""
        field_id = random.choice(FIELD_IDS)
        try:
            response = await self.client.get(f"/api/v1/fields/{field_id}/health")
            self._log_response("Field Health", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"Field health connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"Field health request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Field health HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Inventory Update
    # ─────────────────────────────────────────────────────────────────────────

    def generate_inventory_update(self) -> dict[str, Any]:
        """Generate inventory transaction"""
        items = [
            ("seeds", "Wheat Seeds", "kg"),
            ("fertilizer", "NPK Fertilizer", "kg"),
            ("pesticide", "Organic Pesticide", "L"),
            ("fuel", "Diesel", "L"),
        ]

        item = random.choice(items)
        return {
            "tenant_id": TENANT_ID,
            "category": item[0],
            "item_name": item[1],
            "quantity": round(random.uniform(10, 500), 2),
            "unit": item[2],
            "transaction_type": random.choice(["in", "out"]),
            "notes": "Demo transaction",
        }

    async def update_inventory(self):
        """Send inventory update"""
        data = self.generate_inventory_update()
        try:
            response = await self.client.post("/api/v1/inventory/transactions", json=data)
            self._log_response("Inventory", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"Inventory connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"Inventory request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Inventory HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Marketplace Listing
    # ─────────────────────────────────────────────────────────────────────────

    def generate_marketplace_listing(self) -> dict[str, Any]:
        """Generate marketplace product listing"""
        products = [
            ("Fresh Tomatoes", "طماطم طازجة", "crops", 8.5, "kg"),
            ("Wheat Seeds", "بذور قمح", "seeds", 250, "kg"),
            ("Organic Fertilizer", "سماد عضوي", "fertilizers", 180, "kg"),
            ("Premium Dates", "تمور فاخرة", "crops", 45, "kg"),
        ]

        product = random.choice(products)
        return {
            "tenant_id": TENANT_ID,
            "seller_id": USER_ID,
            "name": product[0],
            "name_ar": product[1],
            "category": product[2],
            "price": product[3] * random.uniform(0.9, 1.1),
            "stock": random.randint(50, 1000),
            "unit": product[4],
            "governorate": random.choice(GOVERNORATES),
            "quality_grade": random.choice(["A+", "A", "B"]),
            "status": "active",
        }

    async def create_marketplace_listing(self):
        """Create marketplace listing"""
        data = self.generate_marketplace_listing()
        try:
            response = await self.client.post("/api/v1/marketplace/products", json=data)
            self._log_response("Marketplace", response)
            return response.status_code < 400
        except httpx.ConnectError as e:
            logger.error(f"Marketplace connection error: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.TimeoutException as e:
            logger.warning(f"Marketplace request timeout: {e}")
            self.stats["requests_failed"] += 1
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Marketplace HTTP error: {e}")
            self.stats["requests_failed"] += 1
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # Health Check Endpoints
    # ─────────────────────────────────────────────────────────────────────────

    async def check_service_health(self, endpoint: str, service_name: str):
        """Check if a service is healthy"""
        try:
            response = await self.client.get(endpoint, timeout=5.0)
            status = "OK" if response.status_code < 400 else "FAIL"
            logger.info(f"Health check {service_name}: {status} ({response.status_code})")
            return response.status_code < 400
        except httpx.ConnectError:
            logger.warning(f"Health check {service_name}: FAIL (connection error)")
            return False
        except httpx.TimeoutException:
            logger.warning(f"Health check {service_name}: FAIL (timeout)")
            return False
        except httpx.HTTPStatusError as e:
            logger.warning(f"Health check {service_name}: FAIL (HTTP {e.response.status_code})")
            return False

    async def run_health_checks(self):
        """Run health checks on all services"""
        services = [
            ("/api/v1/weather/health", "Weather"),
            ("/api/v1/iot/health", "IoT Gateway"),
            ("/api/v1/ndvi/health", "NDVI Engine"),
            ("/api/v1/fields/health", "Field Service"),
            ("/api/v1/tasks/health", "Task Service"),
            ("/api/v1/alerts/health", "Alert Service"),
            ("/api/v1/marketplace/health", "Marketplace"),
        ]

        results = {}
        for endpoint, name in services:
            results[name] = await self.check_service_health(endpoint, name)

        healthy = sum(1 for v in results.values() if v)
        logger.info(f"Health check summary: {healthy}/{len(services)} services healthy")
        return results

    # ─────────────────────────────────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────────────────────────────────

    def _log_response(self, operation: str, response: httpx.Response):
        """Log API response"""
        self.stats["requests_sent"] += 1
        if response.status_code < 400:
            self.stats["requests_success"] += 1
            logger.info(f"{operation}: {response.status_code} OK")
        else:
            self.stats["requests_failed"] += 1
            logger.warning(f"{operation}: {response.status_code} - {response.text[:200]}")

    def print_stats(self):
        """Print statistics"""
        logger.info("=" * 50)
        logger.info("Demo Data Statistics:")
        logger.info(f"  Total requests: {self.stats['requests_sent']}")
        logger.info(f"  Successful: {self.stats['requests_success']}")
        logger.info(f"  Failed: {self.stats['requests_failed']}")
        success_rate = (
            self.stats["requests_success"] / self.stats["requests_sent"] * 100
            if self.stats["requests_sent"] > 0
            else 0
        )
        logger.info(f"  Success rate: {success_rate:.1f}%")
        logger.info("=" * 50)

    # ─────────────────────────────────────────────────────────────────────────
    # Main Run Methods
    # ─────────────────────────────────────────────────────────────────────────

    async def run_once(self):
        """Run all demo data generators once"""
        logger.info("Running demo data generation (once)...")

        # Run health checks first
        await self.run_health_checks()

        # Send demo data to various services
        tasks = [
            self.send_weather_data(),
            self.send_sensor_data(),
            self.send_sensor_data(),
            self.send_ndvi_data(),
            self.send_alert(),
            self.send_task(),
            self.request_yield_prediction(),
            self.check_field_health(),
            self.update_inventory(),
            self.create_marketplace_listing(),
        ]

        await asyncio.gather(*tasks, return_exceptions=True)
        self.print_stats()

    async def run_continuous(self):
        """Run demo data generators continuously"""
        logger.info(f"Running demo data generation (continuous, interval: {INTERVAL_SECONDS}s)...")

        # Initial health check
        await self.run_health_checks()

        iteration = 0
        while True:
            iteration += 1
            logger.info(f"--- Iteration {iteration} ---")

            # Select random operations
            operations = [
                self.send_weather_data,
                self.send_sensor_data,
                self.send_ndvi_data,
                self.send_alert,
                self.send_task,
                self.request_yield_prediction,
                self.check_field_health,
                self.update_inventory,
                self.create_marketplace_listing,
            ]

            # Run 3-5 random operations per iteration
            selected = random.sample(operations, k=random.randint(3, 5))
            tasks = [op() for op in selected]
            await asyncio.gather(*tasks, return_exceptions=True)

            if iteration % 10 == 0:
                self.print_stats()

            await asyncio.sleep(INTERVAL_SECONDS)

    async def run_batch(self, count: int = 100):
        """Run batch demo data generation"""
        logger.info(f"Running demo data generation (batch, count: {count})...")

        for i in range(count):
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{count}")

            operations = [
                self.send_weather_data,
                self.send_sensor_data,
                self.send_ndvi_data,
            ]

            tasks = [op() for op in operations]
            await asyncio.gather(*tasks, return_exceptions=True)

            # Small delay to avoid overwhelming services
            await asyncio.sleep(0.1)

        self.print_stats()


async def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("  SAHOOL Demo Data Service")
    logger.info("  خدمة البيانات التجريبية")
    logger.info("=" * 60)
    logger.info(f"Kong URL: {KONG_URL}")
    logger.info(f"Tenant ID: {TENANT_ID}")
    logger.info(f"Mode: {DEMO_MODE}")
    logger.info("=" * 60)

    generator = DemoDataGenerator()

    try:
        if DEMO_MODE == "once":
            await generator.run_once()
        elif DEMO_MODE == "batch":
            batch_count = int(os.getenv("BATCH_COUNT", "100"))
            await generator.run_batch(batch_count)
        else:  # continuous
            await generator.run_continuous()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        generator.print_stats()
        await generator.close()


if __name__ == "__main__":
    asyncio.run(main())
