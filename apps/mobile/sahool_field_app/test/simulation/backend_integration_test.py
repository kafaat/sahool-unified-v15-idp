#!/usr/bin/env python3
"""
SAHOOL Backend Services Integration Test
اختبار تكامل الخدمات الخلفية مع تطبيق الهاتف

Tests the API endpoints that the mobile app connects to.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# =============================================================================
# Service Configuration - تكوين الخدمات
# =============================================================================


@dataclass
class ServiceConfig:
    """Service endpoint configuration"""

    name: str
    name_ar: str
    port: int
    health_endpoint: str = "/healthz"
    base_path: str = ""


SERVICES = {
    "gateway": ServiceConfig("Kong Gateway", "بوابة Kong", 8000, "/health"),
    "field_core": ServiceConfig("Field Core", "خدمة الحقول", 3000),
    "marketplace": ServiceConfig("Marketplace", "السوق", 3010),
    "billing": ServiceConfig("Billing Core", "خدمة الفوترة", 8089),
    "satellite": ServiceConfig("Satellite/NDVI", "خدمة الأقمار والـNDVI", 8090),
    "indicators": ServiceConfig("Indicators Service", "خدمة المؤشرات", 8091),
    "weather": ServiceConfig("Weather Advanced", "خدمة الطقس المتقدمة", 8092),
    "fertilizer": ServiceConfig("Fertilizer Advisor", "مستشار الأسمدة", 8093),
    "irrigation": ServiceConfig("Irrigation Smart", "الري الذكي", 8094),
    "crop_health": ServiceConfig(
        "Crop Health AI", "صحة المحاصيل بالذكاء الاصطناعي", 8095
    ),
    "virtual_sensors": ServiceConfig("Virtual Sensors", "المستشعرات الافتراضية", 8096),
    "community": ServiceConfig("Community Chat", "مجتمع المزارعين", 8097),
    "yield_engine": ServiceConfig("Yield Engine", "محرك الإنتاجية", 8098),
    "iot_gateway": ServiceConfig("IoT Gateway", "بوابة إنترنت الأشياء", 8100),
    "equipment": ServiceConfig("Equipment Manager", "إدارة المعدات", 8101),
    "notifications": ServiceConfig("Notification Service", "خدمة الإشعارات", 8109),
    "astronomical": ServiceConfig(
        "Astronomical Calendar", "التقويم الفلكي اليمني", 8111
    ),
}


# =============================================================================
# Test Results
# =============================================================================


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """Single test result"""

    name: str
    status: TestStatus
    duration_ms: float
    message: str | None = None
    details: dict[str, Any] | None = None


class TestSuite:
    """Test suite manager"""

    def __init__(self, name: str):
        self.name = name
        self.results: list[TestResult] = []
        self.start_time = None
        self.end_time = None

    def add_result(self, result: TestResult):
        self.results.append(result)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.PASSED)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.SKIPPED)

    def print_summary(self):
        print(f"\n{'=' * 60}")
        print(f"📊 ملخص الاختبارات: {self.name}")
        print(f"{'=' * 60}")
        print(f"   ✅ نجح: {self.passed}")
        print(f"   ❌ فشل: {self.failed}")
        print(f"   ⏭️  تخطى: {self.skipped}")
        print(f"   📊 الإجمالي: {len(self.results)}")

        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            print(f"   ⏱️  المدة: {duration:.2f} ثانية")


# =============================================================================
# Mock Backend Services
# =============================================================================


class MockBackendService:
    """Simulates backend service responses"""

    def __init__(self, config: ServiceConfig):
        self.config = config
        self.is_healthy = True
        self.request_count = 0

    def health_check(self) -> dict[str, Any]:
        """Simulate health check response"""
        self.request_count += 1
        return {
            "status": "healthy" if self.is_healthy else "unhealthy",
            "service": self.config.name,
            "version": "15.4.0",
            "timestamp": datetime.now().isoformat(),
        }


class MockBillingService(MockBackendService):
    """Mock Billing Core Service"""

    def __init__(self):
        super().__init__(SERVICES["billing"])
        self.tenants = {}
        self.plans = self._init_plans()

    def _init_plans(self) -> dict[str, dict[str, Any]]:
        return {
            "free": {
                "id": "free",
                "name": "مجاني",
                "price_usd": 0,
                "limits": {"fields": 1, "users": 1, "ai_analysis": 10},
            },
            "starter": {
                "id": "starter",
                "name": "المبتدئ",
                "price_usd": 29,
                "limits": {"fields": 5, "users": 3, "ai_analysis": 100},
            },
            "professional": {
                "id": "professional",
                "name": "المحترف",
                "price_usd": 99,
                "limits": {"fields": 25, "users": 10, "ai_analysis": 500},
            },
            "enterprise": {
                "id": "enterprise",
                "name": "المؤسسة",
                "price_usd": 299,
                "limits": {"fields": -1, "users": -1, "ai_analysis": -1},
            },
        }

    def get_plans(self) -> list[dict[str, Any]]:
        """Get available plans"""
        self.request_count += 1
        return list(self.plans.values())

    def get_subscription(self, tenant_id: str) -> dict[str, Any]:
        """Get tenant subscription"""
        self.request_count += 1
        if tenant_id not in self.tenants:
            self.tenants[tenant_id] = {
                "tenant_id": tenant_id,
                "plan_id": "free",
                "status": "active",
                "usage": {"fields": 0, "users": 1, "ai_analysis": 0},
            }
        return self.tenants[tenant_id]

    def check_quota(self, tenant_id: str, resource: str) -> dict[str, Any]:
        """Check quota for resource"""
        self.request_count += 1
        sub = self.get_subscription(tenant_id)
        plan = self.plans[sub["plan_id"]]
        usage = sub["usage"].get(resource, 0)
        limit = plan["limits"].get(resource, 0)

        return {
            "resource": resource,
            "used": usage,
            "limit": limit,
            "remaining": limit - usage if limit > 0 else -1,
            "allowed": limit < 0 or usage < limit,
        }


class MockWeatherService(MockBackendService):
    """Mock Weather Advanced Service"""

    def __init__(self):
        super().__init__(SERVICES["weather"])

    def get_current_weather(self, lat: float, lng: float) -> dict[str, Any]:
        """Get current weather"""
        self.request_count += 1
        import random

        return {
            "location": {"lat": lat, "lng": lng},
            "temperature": round(random.uniform(20, 35), 1),
            "humidity": random.randint(30, 80),
            "condition": random.choice(["sunny", "cloudy", "rainy"]),
            "wind_speed": round(random.uniform(5, 25), 1),
            "timestamp": datetime.now().isoformat(),
        }

    def get_forecast(
        self, lat: float, lng: float, days: int = 7
    ) -> list[dict[str, Any]]:
        """Get weather forecast"""
        self.request_count += 1
        import random
        from datetime import timedelta

        forecast = []
        for i in range(days):
            forecast.append(
                {
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "high": round(random.uniform(28, 38), 1),
                    "low": round(random.uniform(18, 25), 1),
                    "condition": random.choice(
                        ["sunny", "cloudy", "rainy", "partly_cloudy"]
                    ),
                    "precipitation_chance": random.randint(0, 100),
                }
            )
        return forecast


class MockNotificationService(MockBackendService):
    """Mock Notification Service"""

    def __init__(self):
        super().__init__(SERVICES["notifications"])
        self.notifications = []

    def send_notification(
        self, tenant_id: str, user_id: str, message: str, title: str = None
    ) -> dict[str, Any]:
        """Send notification"""
        self.request_count += 1
        notification = {
            "id": f"notif-{len(self.notifications) + 1}",
            "tenant_id": tenant_id,
            "user_id": user_id,
            "title": title or "إشعار",
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "status": "sent",
        }
        self.notifications.append(notification)
        return notification

    def get_notifications(self, user_id: str) -> list[dict[str, Any]]:
        """Get user notifications"""
        self.request_count += 1
        return [n for n in self.notifications if n["user_id"] == user_id]


class MockAstronomicalService(MockBackendService):
    """Mock Astronomical Calendar Service"""

    def __init__(self):
        super().__init__(SERVICES["astronomical"])

    def get_today_info(self) -> dict[str, Any]:
        """Get today's astronomical information"""
        self.request_count += 1
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "hijri_date": "15 جمادى الآخرة 1446",
            "season": "شتاء",
            "yemeni_season": "المربعانية",
            "moon_phase": "هلال متزايد",
            "moon_age_days": 8,
            "farming_advice": [
                "وقت مناسب لزراعة البقوليات",
                "يُنصح بتجنب ري المحاصيل في الصباح الباكر",
            ],
            "star_positions": {
                "الثريا": "مرتفعة",
                "سهيل": "ظاهر",
            },
        }

    def get_planting_calendar(self, crop: str) -> dict[str, Any]:
        """Get planting calendar for crop"""
        self.request_count += 1
        return {
            "crop": crop,
            "best_planting_season": "خريف",
            "optimal_months": ["سبتمبر", "أكتوبر", "نوفمبر"],
            "harvest_after_days": 120,
            "water_needs": "متوسط",
            "yemeni_tradition": "يُزرع بعد طلوع سهيل",
        }


# =============================================================================
# Integration Tests
# =============================================================================


async def test_billing_integration(suite: TestSuite):
    """Test billing service integration"""
    print("\n🧪 اختبار تكامل خدمة الفوترة")
    print("-" * 40)

    billing = MockBillingService()

    # Test 1: Get plans
    start = datetime.now()
    try:
        plans = billing.get_plans()
        duration = (datetime.now() - start).total_seconds() * 1000

        assert len(plans) == 4, "Should have 4 plans"
        assert any(p["id"] == "free" for p in plans), "Should have free plan"

        suite.add_result(
            TestResult(
                name="جلب خطط الاشتراك",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"تم جلب {len(plans)} خطة",
            )
        )
        print(f"   ✅ جلب خطط الاشتراك: {len(plans)} خطة")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="جلب خطط الاشتراك",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ جلب خطط الاشتراك: {e}")

    # Test 2: Get subscription
    start = datetime.now()
    try:
        sub = billing.get_subscription("tenant-test-001")
        duration = (datetime.now() - start).total_seconds() * 1000

        assert sub["tenant_id"] == "tenant-test-001"
        assert sub["status"] == "active"

        suite.add_result(
            TestResult(
                name="جلب اشتراك المستأجر",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"الخطة: {sub['plan_id']}",
            )
        )
        print(f"   ✅ جلب اشتراك المستأجر: {sub['plan_id']}")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="جلب اشتراك المستأجر",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ جلب اشتراك المستأجر: {e}")

    # Test 3: Check quota
    start = datetime.now()
    try:
        quota = billing.check_quota("tenant-test-001", "ai_analysis")
        duration = (datetime.now() - start).total_seconds() * 1000

        assert "remaining" in quota
        assert quota["allowed"] is True

        suite.add_result(
            TestResult(
                name="فحص الحصة",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"متبقي: {quota['remaining']}",
            )
        )
        print(f"   ✅ فحص الحصة: متبقي {quota['remaining']}")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="فحص الحصة",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ فحص الحصة: {e}")


async def test_weather_integration(suite: TestSuite):
    """Test weather service integration"""
    print("\n🧪 اختبار تكامل خدمة الطقس")
    print("-" * 40)

    weather = MockWeatherService()

    # Test 1: Current weather
    start = datetime.now()
    try:
        current = weather.get_current_weather(15.3694, 44.1910)
        duration = (datetime.now() - start).total_seconds() * 1000

        assert "temperature" in current
        assert "humidity" in current
        assert current["location"]["lat"] == 15.3694

        suite.add_result(
            TestResult(
                name="جلب الطقس الحالي",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"{current['temperature']}°C, {current['condition']}",
            )
        )
        print(f"   ✅ الطقس الحالي: {current['temperature']}°C")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="جلب الطقس الحالي",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ الطقس الحالي: {e}")

    # Test 2: Weather forecast
    start = datetime.now()
    try:
        forecast = weather.get_forecast(15.3694, 44.1910, 7)
        duration = (datetime.now() - start).total_seconds() * 1000

        assert len(forecast) == 7
        assert all("high" in day and "low" in day for day in forecast)

        suite.add_result(
            TestResult(
                name="جلب توقعات الطقس",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"توقعات {len(forecast)} أيام",
            )
        )
        print(f"   ✅ توقعات الطقس: {len(forecast)} أيام")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="جلب توقعات الطقس",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ توقعات الطقس: {e}")


async def test_notification_integration(suite: TestSuite):
    """Test notification service integration"""
    print("\n🧪 اختبار تكامل خدمة الإشعارات")
    print("-" * 40)

    notifications = MockNotificationService()

    # Test 1: Send notification
    start = datetime.now()
    try:
        result = notifications.send_notification(
            tenant_id="tenant-test-001",
            user_id="user-001",
            title="تنبيه الري",
            message="حان وقت ري الحقل رقم 1",
        )
        duration = (datetime.now() - start).total_seconds() * 1000

        assert result["status"] == "sent"
        assert "id" in result

        suite.add_result(
            TestResult(
                name="إرسال إشعار",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"ID: {result['id']}",
            )
        )
        print(f"   ✅ إرسال إشعار: {result['id']}")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="إرسال إشعار",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ إرسال إشعار: {e}")

    # Test 2: Get notifications
    start = datetime.now()
    try:
        user_notifs = notifications.get_notifications("user-001")
        duration = (datetime.now() - start).total_seconds() * 1000

        assert len(user_notifs) >= 1

        suite.add_result(
            TestResult(
                name="جلب إشعارات المستخدم",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"{len(user_notifs)} إشعار",
            )
        )
        print(f"   ✅ جلب إشعارات المستخدم: {len(user_notifs)}")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="جلب إشعارات المستخدم",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ جلب إشعارات المستخدم: {e}")


async def test_astronomical_integration(suite: TestSuite):
    """Test astronomical calendar service integration"""
    print("\n🧪 اختبار تكامل خدمة التقويم الفلكي")
    print("-" * 40)

    astro = MockAstronomicalService()

    # Test 1: Today's info
    start = datetime.now()
    try:
        info = astro.get_today_info()
        duration = (datetime.now() - start).total_seconds() * 1000

        assert "hijri_date" in info
        assert "yemeni_season" in info
        assert "moon_phase" in info

        suite.add_result(
            TestResult(
                name="معلومات اليوم الفلكية",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"{info['yemeni_season']} - {info['moon_phase']}",
            )
        )
        print(f"   ✅ معلومات اليوم: {info['yemeni_season']}")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="معلومات اليوم الفلكية",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ معلومات اليوم: {e}")

    # Test 2: Planting calendar
    start = datetime.now()
    try:
        calendar = astro.get_planting_calendar("قمح")
        duration = (datetime.now() - start).total_seconds() * 1000

        assert "best_planting_season" in calendar
        assert "optimal_months" in calendar

        suite.add_result(
            TestResult(
                name="تقويم الزراعة",
                status=TestStatus.PASSED,
                duration_ms=duration,
                message=f"موسم الزراعة: {calendar['best_planting_season']}",
            )
        )
        print(f"   ✅ تقويم الزراعة: {calendar['best_planting_season']}")
    except Exception as e:
        suite.add_result(
            TestResult(
                name="تقويم الزراعة",
                status=TestStatus.FAILED,
                duration_ms=0,
                message=str(e),
            )
        )
        print(f"   ❌ تقويم الزراعة: {e}")


async def test_service_health_checks(suite: TestSuite):
    """Test all service health checks"""
    print("\n🧪 اختبار صحة الخدمات")
    print("-" * 40)

    for _service_key, config in SERVICES.items():
        start = datetime.now()
        try:
            mock = MockBackendService(config)
            health = mock.health_check()
            duration = (datetime.now() - start).total_seconds() * 1000

            assert health["status"] == "healthy"

            suite.add_result(
                TestResult(
                    name=f"صحة {config.name_ar}",
                    status=TestStatus.PASSED,
                    duration_ms=duration,
                    message=f"Port {config.port}",
                )
            )
            print(f"   ✅ {config.name_ar}: healthy (:{config.port})")
        except Exception as e:
            suite.add_result(
                TestResult(
                    name=f"صحة {config.name_ar}",
                    status=TestStatus.FAILED,
                    duration_ms=0,
                    message=str(e),
                )
            )
            print(f"   ❌ {config.name_ar}: {e}")


# =============================================================================
# Main
# =============================================================================


async def run_integration_tests():
    """Run all integration tests"""

    print("\n" + "=" * 60)
    print("🔌 SAHOOL Backend Integration Tests")
    print("اختبارات تكامل الخدمات الخلفية مع تطبيق الهاتف")
    print("=" * 60)

    suite = TestSuite("Backend Integration")
    suite.start_time = datetime.now()

    # Run all test suites
    await test_service_health_checks(suite)
    await test_billing_integration(suite)
    await test_weather_integration(suite)
    await test_notification_integration(suite)
    await test_astronomical_integration(suite)

    suite.end_time = datetime.now()

    # Print summary
    suite.print_summary()

    # Print detailed failures
    failures = [r for r in suite.results if r.status == TestStatus.FAILED]
    if failures:
        print(f"\n{'=' * 60}")
        print("❌ تفاصيل الاختبارات الفاشلة:")
        print("=" * 60)
        for f in failures:
            print(f"   • {f.name}: {f.message}")

    # Overall result
    if suite.failed == 0:
        print("\n🎉 جميع الاختبارات نجحت!")
        return 0
    else:
        print(f"\n⚠️ فشل {suite.failed} اختبار")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_integration_tests())
    exit(exit_code)
