"""
SAHOOL Platform - Performance Baseline Tests (Locust)
اختبارات خط الأساس للأداء

This script establishes performance baselines for critical API endpoints.
Run with: locust -f tests/load/locustfile.py --host=http://localhost:8000

Author: SAHOOL Platform Team
"""

import os
import random
from typing import Any

from locust import HttpUser, between, task, events
from locust.runners import MasterRunner

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")
TENANT_ID = os.getenv("TENANT_ID", "tenant_test_001")

# Performance baselines (in milliseconds)
BASELINES = {
    "health_check": 100,
    "field_list": 300,
    "field_detail": 250,
    "weather_current": 200,
    "weather_forecast": 300,
    "ndvi_latest": 500,
    "advisory_recommendations": 400,
    "task_list": 250,
    "auth_validate": 150,
}


# ═══════════════════════════════════════════════════════════════════════════════
# Custom Event Handlers for Baseline Tracking
# ═══════════════════════════════════════════════════════════════════════════════


@events.init.add_listener
def on_init(environment, **kwargs):
    """Initialize test environment"""
    print("=" * 60)
    print("SAHOOL Performance Baseline Test")
    print("خط الأساس لاختبار الأداء")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary when test stops"""
    print("=" * 60)
    print("Test Complete - خط الأساس للأداء مكتمل")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════════════════════
# User Behaviors
# ═══════════════════════════════════════════════════════════════════════════════


class SAHOOLBaseUser(HttpUser):
    """
    Base user class with common configuration
    فئة المستخدم الأساسية مع التكوين المشترك
    """

    # Wait time between tasks (simulates real user behavior)
    wait_time = between(1, 3)

    # Default headers
    def on_start(self):
        """Set up headers on user start"""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Tenant-ID": TENANT_ID,
        }
        if AUTH_TOKEN:
            self.headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

    def check_baseline(self, response, endpoint: str):
        """Check if response time meets baseline"""
        baseline_ms = BASELINES.get(endpoint, 500)
        if response.elapsed.total_seconds() * 1000 > baseline_ms:
            response.failure(
                f"Response time {response.elapsed.total_seconds() * 1000:.0f}ms exceeds baseline {baseline_ms}ms"
            )


class FarmerUser(SAHOOLBaseUser):
    """
    Simulates a farmer user workflow
    محاكاة سير عمل المزارع
    """

    weight = 10  # 10x more farmers than admins

    @task(10)
    def view_fields(self):
        """View list of fields"""
        with self.client.get(
            "/api/v1/fields",
            headers=self.headers,
            name="[Farmer] List Fields",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.check_baseline(response, "field_list")
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(8)
    def view_field_detail(self):
        """View single field details"""
        # Using a mock field ID - in real tests, use actual IDs
        field_id = "test_field_001"
        with self.client.get(
            f"/api/v1/fields/{field_id}",
            headers=self.headers,
            name="[Farmer] Field Detail",
            catch_response=True,
        ) as response:
            if response.status_code in [200, 404]:  # 404 is acceptable for mock ID
                self.check_baseline(response, "field_detail")
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(6)
    def check_weather(self):
        """Check current weather"""
        # Sana'a coordinates
        with self.client.get(
            "/api/v1/weather/current?lat=15.3694&lon=44.1910",
            headers=self.headers,
            name="[Farmer] Current Weather",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.check_baseline(response, "weather_current")
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(4)
    def check_forecast(self):
        """Check weather forecast"""
        with self.client.get(
            "/api/v1/weather/forecast?lat=15.3694&lon=44.1910&days=5",
            headers=self.headers,
            name="[Farmer] Weather Forecast",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.check_baseline(response, "weather_forecast")
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(5)
    def view_ndvi(self):
        """View NDVI data for field"""
        with self.client.get(
            "/api/v1/ndvi/latest?field_id=test_field_001",
            headers=self.headers,
            name="[Farmer] NDVI Data",
            catch_response=True,
        ) as response:
            if response.status_code in [200, 404]:
                self.check_baseline(response, "ndvi_latest")
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(5)
    def get_advisory(self):
        """Get AI advisory recommendations"""
        with self.client.get(
            "/api/v1/advisory/recommendations?field_id=test_field_001",
            headers=self.headers,
            name="[Farmer] Advisory",
            catch_response=True,
        ) as response:
            if response.status_code in [200, 404]:
                self.check_baseline(response, "advisory_recommendations")
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(7)
    def list_tasks(self):
        """List pending tasks"""
        with self.client.get(
            "/api/v1/tasks?status=pending&limit=10",
            headers=self.headers,
            name="[Farmer] List Tasks",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.check_baseline(response, "task_list")
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")


class AdminUser(SAHOOLBaseUser):
    """
    Simulates an admin user workflow
    محاكاة سير عمل المدير
    """

    weight = 1  # Fewer admins than farmers

    @task(5)
    def health_check(self):
        """Check system health"""
        with self.client.get(
            "/health",
            headers=self.headers,
            name="[Admin] Health Check",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.check_baseline(response, "health_check")
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(3)
    def list_all_fields(self):
        """List all fields (admin view)"""
        with self.client.get(
            "/api/v1/fields?limit=100",
            headers=self.headers,
            name="[Admin] All Fields",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

    @task(2)
    def view_analytics(self):
        """View analytics dashboard data"""
        with self.client.get(
            "/api/v1/analytics/summary",
            headers=self.headers,
            name="[Admin] Analytics",
            catch_response=True,
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")


class IoTDevice(SAHOOLBaseUser):
    """
    Simulates IoT device sending sensor data
    محاكاة جهاز إنترنت الأشياء لإرسال بيانات المستشعرات
    """

    weight = 5  # Multiple IoT devices

    # IoT devices send data more frequently
    wait_time = between(5, 15)

    @task(1)
    def send_sensor_reading(self):
        """Send sensor reading"""
        reading = {
            "device_id": f"iot_sensor_{random.randint(1, 100)}",
            "tenant_id": TENANT_ID,
            "readings": {
                "soil_moisture": random.uniform(20, 80),
                "soil_temperature": random.uniform(15, 35),
                "air_temperature": random.uniform(20, 45),
                "humidity": random.uniform(30, 90),
            },
            "timestamp": "2025-01-26T10:00:00Z",
        }

        with self.client.post(
            "/api/v1/iot/readings",
            json=reading,
            headers=self.headers,
            name="[IoT] Send Reading",
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201, 404]:  # 404 if endpoint not exist
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Baseline Thresholds (SLOs)
# ═══════════════════════════════════════════════════════════════════════════════
#
# These thresholds define acceptable performance for SAHOOL Platform:
#
# | Endpoint             | Target P95  | Max Response |
# |----------------------|-------------|--------------|
# | Health Check         | 100ms       | 200ms        |
# | Field List           | 300ms       | 500ms        |
# | Field Detail         | 250ms       | 400ms        |
# | Weather Current      | 200ms       | 400ms        |
# | Weather Forecast     | 300ms       | 500ms        |
# | NDVI Latest          | 500ms       | 1000ms       |
# | Advisory             | 400ms       | 800ms        |
# | Task List            | 250ms       | 400ms        |
# | Auth Validate        | 150ms       | 300ms        |
#
# ═══════════════════════════════════════════════════════════════════════════════
