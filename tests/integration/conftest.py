"""
SAHOOL Integration Test Configuration
تكوين اختبارات التكامل لمنصة سهول

Comprehensive pytest fixtures for integration testing:
- Docker Compose setup/teardown
- Database connections (PostgreSQL with PostGIS)
- NATS messaging connections
- HTTP client with retries
- Test data factories

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import os
import time
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import httpx
import pytest
from httpx import AsyncClient, Timeout

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

try:
    from faker import Faker

    faker_ar = Faker("ar_SA")
    faker_en = Faker("en_US")
    HAS_FAKER = True
except ImportError:
    import uuid as _uuid

    HAS_FAKER = False

    class _FallbackFaker:
        """Minimal fallback when faker is not installed."""

        def uuid4(self) -> str:
            return str(_uuid.uuid4())

        def sentence(self) -> str:
            return "Test sentence."

        def text(self) -> str:
            return "Test text content."

        def city(self) -> str:
            return "Test City"

        def email(self) -> str:
            return f"test-{self.uuid4()[:8]}@example.com"

        def phone_number(self) -> str:
            return "+1-555-0100"

        def iso8601(self) -> str:
            from datetime import datetime, timezone

            return datetime.now(tz=timezone.utc).isoformat()

        def date_this_year(self) -> Any:
            from datetime import date

            return date.today()

        def pyfloat(self, min_value: float = 0, max_value: float = 100, right_digits: int = 2) -> float:
            return round((min_value + max_value) / 2, right_digits)

        def random_int(self, *args: int, **kwargs: int) -> int:
            min_val = args[0] if args else kwargs.get("min", 0)
            max_val = args[1] if len(args) > 1 else kwargs.get("max", 100)
            return (min_val + max_val) // 2

        def random_element(self, elements: list) -> Any:
            return elements[0] if elements else None

    faker_ar = _FallbackFaker()  # type: ignore[assignment]
    faker_en = _FallbackFaker()  # type: ignore[assignment]

# ═══════════════════════════════════════════════════════════════════════════════
# Test Configuration - تكوين الاختبارات
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TestConfig:
    """Test environment configuration"""

    # Database
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_user: str = os.getenv("POSTGRES_USER", "sahool_test")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "test_password_123")
    postgres_db: str = os.getenv("POSTGRES_DB", "sahool_test")

    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "test_redis_pass")

    # NATS
    nats_host: str = os.getenv("NATS_HOST", "localhost")
    nats_port: int = int(os.getenv("NATS_PORT", "4222"))

    # Qdrant
    qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))

    # JWT
    jwt_secret: str = os.getenv(
        "JWT_SECRET_KEY",
        "test-secret-key-for-tests-only-do-not-use-in-production-32chars",
    )

    # Test timeouts
    service_startup_timeout: int = 60
    http_timeout: int = 30

    @property
    def postgres_url(self) -> str:
        """PostgreSQL connection URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self) -> str:
        """Redis connection URL"""
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"

    @property
    def nats_url(self) -> str:
        """NATS connection URL"""
        return f"nats://{self.nats_host}:{self.nats_port}"


@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Test configuration - تكوين الاختبارات"""
    return TestConfig()


# ═══════════════════════════════════════════════════════════════════════════════
# Docker Compose Fixtures - إعدادات Docker Compose
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session", autouse=True)
def docker_compose_setup():
    """
    Setup and teardown Docker Compose environment
    إعداد وتنظيف بيئة Docker Compose

    Note: This assumes docker-compose.test.yml is already running
    ملاحظة: يفترض هذا أن docker-compose.test.yml يعمل بالفعل
    """
    # In CI/CD, Docker Compose should be started before tests
    # We just verify services are ready
    yield
    # Cleanup happens in CI/CD after tests complete


def wait_for_service(url: str, max_retries: int = 30, delay: float = 2.0) -> bool:
    """
    Wait for a service to become available
    انتظار حتى تصبح الخدمة متاحة
    """
    import requests
    from requests.exceptions import RequestException

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 500:  # Any non-server error is considered "available"
                return True
        except RequestException:
            pass

        if attempt < max_retries - 1:
            time.sleep(delay)

    return False


# ═══════════════════════════════════════════════════════════════════════════════
# Database Fixtures - إعدادات قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def db_connection(
    test_config: TestConfig,
) -> Generator[Any, None, None]:
    """
    PostgreSQL database connection
    اتصال قاعدة بيانات PostgreSQL
    """
    if not HAS_PSYCOPG2:
        pytest.skip("psycopg2 not installed - skipping database-dependent tests")

    # Wait for PostgreSQL to be ready
    max_retries = 30
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(  # type: ignore[union-attr]
                host=test_config.postgres_host,
                port=test_config.postgres_port,
                user=test_config.postgres_user,
                password=test_config.postgres_password,
                dbname=test_config.postgres_db,
                cursor_factory=RealDictCursor,
            )
            conn.autocommit = True
            yield conn
            conn.close()
            return
        except psycopg2.OperationalError:  # type: ignore[union-attr]
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise

    pytest.fail("Failed to connect to PostgreSQL")


@pytest.fixture
def db_cursor(db_connection):
    """
    Database cursor for executing queries
    مؤشر قاعدة البيانات لتنفيذ الاستعلامات
    """
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()


def pytest_addoption(parser):
    """
    Add custom command-line options for pytest
    إضافة خيارات سطر أوامر مخصصة لـ pytest
    """
    parser.addoption(
        "--postgis",
        action="store_true",
        default=False,
        help="Enable PostGIS integration tests (requires PostGIS to be installed)",
    )


def pytest_configure(config):
    """
    Configure pytest and check PostGIS availability
    تكوين pytest والتحقق من توفر PostGIS
    """
    config.postgis_available = False
    config.postgis_skip_reason = "PostGIS not available (--postgis flag not set)"

    if config.getoption("--postgis") and HAS_PSYCOPG2:
        try:
            # Try to connect and check for PostGIS
            from tests.integration.conftest import TestConfig as TC

            test_config = TC()
            conn = psycopg2.connect(  # type: ignore[union-attr]
                host=test_config.postgres_host,
                port=test_config.postgres_port,
                user=test_config.postgres_user,
                password=test_config.postgres_password,
                dbname=test_config.postgres_db,
                cursor_factory=RealDictCursor,
                connect_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'postgis';")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                config.postgis_available = True
                config.postgis_skip_reason = None
            else:
                config.postgis_skip_reason = "PostGIS extension not installed. Run: CREATE EXTENSION postgis;"
        except Exception as e:
            config.postgis_skip_reason = f"Could not verify PostGIS availability: {str(e)}"
    elif config.getoption("--postgis") and not HAS_PSYCOPG2:
        config.postgis_skip_reason = "psycopg2 not installed - cannot verify PostGIS availability"


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to skip PostGIS tests based on availability
    تعديل مجموعة الاختبارات لتخطي اختبارات PostGIS بناءً على التوفر
    """
    skip_postgis = pytest.mark.skip(reason=config.postgis_skip_reason)

    for item in items:
        # Check if test is in TestPostGISIntegration class
        if "TestPostGISIntegration" in item.nodeid:
            if not config.postgis_available:
                item.add_marker(skip_postgis)


@pytest.fixture(scope="session")
def postgis_available(request) -> bool:
    """
    Check if PostGIS extension is available in the database
    فحص ما إذا كان امتداد PostGIS متاحاً في قاعدة البيانات

    Returns True if PostGIS is installed and enabled, False otherwise.
    This fixture allows tests to conditionally check PostGIS availability.
    """
    return request.config.postgis_available


@pytest.fixture(autouse=True)
def cleanup_test_data(db_cursor):
    """
    Clean up test data before each test
    تنظيف بيانات الاختبار قبل كل اختبار
    """
    yield
    # Cleanup after test — only runs when psycopg2 is available (db_cursor is
    # provided by db_connection which calls pytest.skip() otherwise).
    if not HAS_PSYCOPG2:
        return
    try:
        # Clean up test tables in reverse order of dependencies
        tables = [
            "notifications",
            "alerts",
            "inventory_items",
            "experiments",
            "marketplace_listings",
            "subscriptions",
            "payments",
            "iot_readings",
            "satellite_analyses",
            "ndvi_analyses",
            "weather_forecasts",
            "tasks",
            "fields",
        ]

        for table in tables:
            try:
                db_cursor.execute(f"DELETE FROM {table} WHERE name LIKE '%test%' OR name LIKE '%Test%'")
            except psycopg2.errors.UndefinedTable:  # type: ignore[union-attr]
                # Table might not exist, skip
                pass
    except Exception:
        # Ignore cleanup errors
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Connection Fixtures - إعدادات اتصال NATS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
async def nats_client(test_config: TestConfig):
    """
    NATS messaging client
    عميل رسائل NATS
    """
    try:
        from nats.aio.client import Client as NATS

        nc = NATS()

        # Wait for NATS to be ready
        max_retries = 30
        for attempt in range(max_retries):
            try:
                await nc.connect(test_config.nats_url)
                yield nc
                await nc.close()
                return
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise
    except ImportError:
        # NATS client not installed, yield mock
        from unittest.mock import AsyncMock

        yield AsyncMock()


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP Client Fixtures - إعدادات عميل HTTP
# ═══════════════════════════════════════════════════════════════════════════════


class RetryTransport(httpx.AsyncHTTPTransport):
    """
    HTTP transport with automatic retries
    نقل HTTP مع إعادة المحاولات التلقائية
    """

    def __init__(self, *args, max_retries: int = 3, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_retries = max_retries

    async def handle_async_request(self, request):
        for attempt in range(self.max_retries):
            try:
                response = await super().handle_async_request(request)
                if response.status_code < 500 or attempt == self.max_retries - 1:
                    return response
            except (httpx.ConnectError, httpx.TimeoutException):
                if attempt == self.max_retries - 1:
                    raise

            await asyncio.sleep(2**attempt)  # Exponential backoff
        return None


@pytest.fixture(scope="session")
async def http_client(test_config: TestConfig) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP client with retries and timeout configuration
    عميل HTTP مع إعادة المحاولات وتكوين المهلة
    """
    transport = RetryTransport(max_retries=3)
    timeout = Timeout(timeout=test_config.http_timeout)

    async with AsyncClient(transport=transport, timeout=timeout, follow_redirects=True) as client:
        yield client


@pytest.fixture
def auth_headers(test_config: TestConfig) -> dict[str, str]:
    """
    Authentication headers for API requests
    رؤوس المصادقة لطلبات API
    """
    # In a real scenario, generate a proper JWT token
    # For testing, use a simple token
    return {
        "Authorization": f"Bearer {test_config.jwt_secret}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Factories - مصانع بيانات الاختبار
# ═══════════════════════════════════════════════════════════════════════════════


class FieldFactory:
    """Factory for creating test field data - مصنع لإنشاء بيانات حقول الاختبار"""

    @staticmethod
    def create(name: str = None, crop_type: str = "wheat") -> dict[str, Any]:
        """Create a test field - إنشاء حقل اختبار"""
        return {
            "name": name or f"Test Field {faker_en.uuid4()[:8]}",
            "name_ar": f"حقل اختبار {faker_ar.uuid4()[:8]}",
            "area_hectares": faker_en.pyfloat(min_value=1.0, max_value=100.0, right_digits=2),
            "crop_type": crop_type,
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [44.0, 15.0],
                        [44.1, 15.0],
                        [44.1, 15.1],
                        [44.0, 15.1],
                        [44.0, 15.0],
                    ]
                ],
            },
        }


class WeatherQueryFactory:
    """Factory for creating weather query data - مصنع لإنشاء بيانات استعلام الطقس"""

    @staticmethod
    def create(latitude: float = 15.3694, longitude: float = 44.1910) -> dict[str, Any]:
        """Create a weather query - إنشاء استعلام طقس"""
        return {"latitude": latitude, "longitude": longitude, "days": 7}


class NotificationFactory:
    """Factory for creating notification data - مصنع لإنشاء بيانات الإشعارات"""

    @staticmethod
    def create(user_id: str = "test-user-123", notification_type: str = "weather_alert") -> dict[str, Any]:
        """Create a notification - إنشاء إشعار"""
        return {
            "user_id": user_id,
            "type": notification_type,
            "title": faker_en.sentence(),
            "title_ar": faker_ar.sentence(),
            "message": faker_en.text(),
            "message_ar": faker_ar.text(),
            "priority": "high",
            "channels": ["push", "email"],
        }


class InventoryItemFactory:
    """Factory for creating inventory item data - مصنع لإنشاء بيانات المخزون"""

    @staticmethod
    def create(item_type: str = "fertilizer") -> dict[str, Any]:
        """Create an inventory item - إنشاء عنصر مخزون"""
        return {
            "name": f"Test {item_type.title()} {faker_en.uuid4()[:8]}",
            "name_ar": f"{item_type} اختبار {faker_ar.uuid4()[:8]}",
            "type": item_type,
            "quantity": faker_en.random_int(min=10, max=1000),
            "unit": "kg",
            "low_stock_threshold": 50,
            "location": faker_en.city(),
        }


class AIQueryFactory:
    """Factory for creating AI advisor queries - مصنع لإنشاء استعلامات المستشار الذكي"""

    @staticmethod
    def create(language: str = "ar") -> dict[str, Any]:
        """Create an AI query - إنشاء استعلام ذكي"""
        if language == "ar":
            return {
                "question": "ما هو أفضل وقت لزراعة القمح في اليمن؟",
                "field_id": "test-field-123",
                "language": "ar",
                "context": {"crop_type": "wheat", "location": "Sana'a, Yemen"},
            }
        else:
            return {
                "question": "What is the best time to plant wheat in Yemen?",
                "field_id": "test-field-123",
                "language": "en",
                "context": {"crop_type": "wheat", "location": "Sana'a, Yemen"},
            }


class PaymentFactory:
    """Factory for creating payment data - مصنع لإنشاء بيانات الدفع"""

    @staticmethod
    def create(amount: float = 100.0, currency: str = "YER") -> dict[str, Any]:
        """Create a payment - إنشاء دفعة"""
        return {
            "amount": amount,
            "currency": currency,
            "payment_method": "tharwatt",
            "description": "SAHOOL Subscription - Test",
            "customer_email": faker_en.email(),
            "customer_phone": faker_en.phone_number(),
        }


class IoTReadingFactory:
    """Factory for creating IoT sensor readings - مصنع لإنشاء قراءات أجهزة IoT"""

    @staticmethod
    def create(sensor_type: str = "soil_moisture") -> dict[str, Any]:
        """Create an IoT reading - إنشاء قراءة IoT"""
        return {
            "device_id": f"device-{faker_en.uuid4()[:8]}",
            "sensor_type": sensor_type,
            "value": faker_en.pyfloat(min_value=0, max_value=100, right_digits=2),
            "unit": "%" if sensor_type == "soil_moisture" else "°C",
            "latitude": 15.3694,
            "longitude": 44.1910,
            "timestamp": faker_en.iso8601(),
        }


class ExperimentFactory:
    """Factory for creating research experiments - مصنع لإنشاء التجارب البحثية"""

    @staticmethod
    def create() -> dict[str, Any]:
        """Create a research experiment - إنشاء تجربة بحثية"""
        return {
            "title": f"Test Experiment {faker_en.uuid4()[:8]}",
            "title_ar": f"تجربة اختبار {faker_ar.uuid4()[:8]}",
            "description": faker_en.text(),
            "description_ar": faker_ar.text(),
            "status": "active",
            "start_date": faker_en.date_this_year().isoformat(),
            "variables": {"fertilizer_type": "NPK", "irrigation_frequency": "daily"},
        }


@pytest.fixture
def field_factory() -> FieldFactory:
    """Field data factory - مصنع بيانات الحقول"""
    return FieldFactory()


@pytest.fixture
def weather_factory() -> WeatherQueryFactory:
    """Weather query factory - مصنع استعلامات الطقس"""
    return WeatherQueryFactory()


@pytest.fixture
def notification_factory() -> NotificationFactory:
    """Notification factory - مصنع الإشعارات"""
    return NotificationFactory()


@pytest.fixture
def inventory_factory() -> InventoryItemFactory:
    """Inventory item factory - مصنع عناصر المخزون"""
    return InventoryItemFactory()


@pytest.fixture
def ai_query_factory() -> AIQueryFactory:
    """AI query factory - مصنع استعلامات الذكاء الاصطناعي"""
    return AIQueryFactory()


@pytest.fixture
def payment_factory() -> PaymentFactory:
    """Payment factory - مصنع الدفعات"""
    return PaymentFactory()


@pytest.fixture
def iot_factory() -> IoTReadingFactory:
    """IoT reading factory - مصنع قراءات IoT"""
    return IoTReadingFactory()


@pytest.fixture
def experiment_factory() -> ExperimentFactory:
    """Experiment factory - مصنع التجارب"""
    return ExperimentFactory()


# ═══════════════════════════════════════════════════════════════════════════════
# Service URL Fixtures - إعدادات عناوين الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def service_urls() -> dict[str, str]:
    """
    Service URLs for integration testing
    عناوين الخدمات لاختبارات التكامل
    """
    return {
        # Starter Package
        # field-core and field-ops are deprecated; replaced by field-management-service (port 3000)
        "field_management": "http://localhost:3000",
        # weather-core is deprecated; replaced by weather-service (port 8092)
        "weather_service": "http://localhost:8092",
        "astronomical_calendar": "http://localhost:8111",
        # agro-advisor is deprecated; replaced by advisory-service (port 8093)
        "advisory_service": "http://localhost:8093",
        "notification_service": "http://localhost:8110",
        # Professional Package
        # satellite-service is deprecated; replaced by vegetation-analysis-service (port 8090)
        "vegetation_analysis_service": "http://localhost:8090",
        # ndvi-engine is deprecated; replaced by vegetation-analysis-service (port 8090)
        "vegetation_analysis_ndvi": "http://localhost:8090",
        # crop-health-ai is deprecated; replaced by crop-intelligence-service (port 8095)
        "crop_intelligence_service": "http://localhost:8095",
        "irrigation_smart": "http://localhost:8094",
        "inventory_service": "http://localhost:8116",
        # Enterprise Package
        "ai_advisor": "http://localhost:8112",
        "iot_gateway": "http://localhost:8106",
        "marketplace_service": "http://localhost:3010",
        "billing_core": "http://localhost:8089",
        "research_core": "http://localhost:3015",
        # Additional Services
        "alert_service": "http://localhost:8113",
        "task_service": "http://localhost:8103",
        "ws_gateway": "http://localhost:8081",
        "equipment_service": "http://localhost:8101",
        # yield-engine is deprecated; replaced by yield-prediction-service (port 8152)
        "yield_prediction_service": "http://localhost:8152",
        "provider_config": "http://localhost:8104",
        # Platform Integration Services
        "ai_agents_service": "http://localhost:8130",
        "crm_service": "http://localhost:8131",
        "lowcode_engine": "http://localhost:8132",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions - دوال مساعدة
# ═══════════════════════════════════════════════════════════════════════════════


async def wait_for_service_health(
    client: AsyncClient,
    url: str,
    health_endpoint: str = "/healthz",
    max_retries: int = 30,
    delay: float = 2.0,
) -> bool:
    """
    Wait for a service to become healthy
    انتظار حتى تصبح الخدمة صحية
    """
    full_url = f"{url}{health_endpoint}"

    for attempt in range(max_retries):
        try:
            response = await client.get(full_url)
            if response.status_code in (200, 204):
                return True
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        if attempt < max_retries - 1:
            await asyncio.sleep(delay)

    return False


@pytest.fixture
async def wait_for_services(http_client: AsyncClient, service_urls: dict[str, str]):
    """
    Wait for all services to be ready
    انتظار حتى تصبح جميع الخدمات جاهزة
    """

    async def wait(service_name: str, timeout: int = 60) -> bool:
        url = service_urls.get(service_name)
        if not url:
            return False

        return await wait_for_service_health(http_client, url, max_retries=timeout // 2)

    return wait


# ═══════════════════════════════════════════════════════════════════════════════
# Additional Test Data Factories - مصانع بيانات اختبار إضافية
# ═══════════════════════════════════════════════════════════════════════════════


class AlertFactory:
    """Factory for creating alert data - مصنع لإنشاء بيانات التنبيهات"""

    @staticmethod
    def create(alert_type: str = "weather", severity: str = "medium") -> dict[str, Any]:
        """Create an alert - إنشاء تنبيه"""
        return {
            "type": alert_type,
            "subtype": "general",
            "severity": severity,
            "title": faker_en.sentence(),
            "title_ar": faker_ar.sentence(),
            "description": faker_en.text(),
            "description_ar": faker_ar.text(),
            "valid_from": datetime.utcnow().isoformat(),
            "valid_until": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        }


class MarketplaceProductFactory:
    """Factory for creating marketplace product data - مصنع لإنشاء بيانات منتجات السوق"""

    @staticmethod
    def create(product_type: str = "fertilizer") -> dict[str, Any]:
        """Create a marketplace product - إنشاء منتج للسوق"""
        return {
            "name": f"Test {product_type.title()} {faker_en.uuid4()[:8]}",
            "name_ar": f"{product_type} اختبار {faker_ar.uuid4()[:8]}",
            "description": faker_en.text(),
            "description_ar": faker_ar.text(),
            "category": "inputs",
            "price": faker_en.random_int(min=1000, max=50000),
            "currency": "YER",
            "unit": "kg",
            "quantity_available": faker_en.random_int(min=50, max=1000),
        }


class TaskFactory:
    """Factory for creating task data - مصنع لإنشاء بيانات المهام"""

    @staticmethod
    def create(task_type: str = "irrigation") -> dict[str, Any]:
        """Create a task - إنشاء مهمة"""
        return {
            "title": f"Test Task - {task_type.title()}",
            "title_ar": f"مهمة اختبار - {task_type}",
            "description": faker_en.text(),
            "task_type": task_type,
            "priority": faker_en.random_element(["low", "medium", "high"]),
            "due_date": (datetime.utcnow() + timedelta(days=faker_en.random_int(1, 7))).isoformat(),
            "status": "pending",
        }


class SubscriptionFactory:
    """Factory for creating subscription data - مصنع لإنشاء بيانات الاشتراكات"""

    @staticmethod
    def create(plan_id: str = "starter") -> dict[str, Any]:
        """Create a subscription - إنشاء اشتراك"""
        return {
            "name": f"Test Tenant {faker_en.uuid4()[:8]}",
            "name_ar": f"مستأجر اختبار {faker_ar.uuid4()[:8]}",
            "email": faker_en.email(),
            "phone": faker_en.phone_number(),
            "plan_id": plan_id,
            "billing_cycle": "monthly",
        }


class OrderFactory:
    """Factory for creating order data - مصنع لإنشاء بيانات الطلبات"""

    @staticmethod
    def create(item_count: int = 2) -> dict[str, Any]:
        """Create an order - إنشاء طلب"""
        items = []
        for _ in range(item_count):
            items.append(
                {
                    "product_id": f"product-{faker_en.uuid4()[:8]}",
                    "quantity": faker_en.random_int(min=1, max=20),
                    "unit_price": faker_en.random_int(min=5000, max=50000),
                }
            )

        return {
            "items": items,
            "delivery_address": {
                "name": faker_en.name(),
                "phone": faker_en.phone_number(),
                "street": faker_en.street_address(),
                "city": "Sana'a",
                "city_ar": "صنعاء",
            },
            "payment_method": "tharwatt",
        }


class DeviceFactory:
    """Factory for creating IoT device data - مصنع لإنشاء بيانات أجهزة IoT"""

    @staticmethod
    def create(device_type: str = "soil_moisture_sensor") -> dict[str, Any]:
        """Create an IoT device - إنشاء جهاز IoT"""
        return {
            "device_id": f"device-{faker_en.uuid4()[:12]}",
            "device_type": device_type,
            "device_type_ar": f"مستشعر {device_type}",
            "manufacturer": faker_en.company(),
            "model": f"MODEL-{faker_en.random_int(100, 999)}",
            "firmware_version": f"{faker_en.random_int(1, 3)}.{faker_en.random_int(0, 9)}.0",
            "location": {"latitude": 15.3694, "longitude": 44.1910},
        }


class ReviewFactory:
    """Factory for creating product review data - مصنع لإنشاء بيانات مراجعات المنتجات"""

    @staticmethod
    def create(rating: int = 5) -> dict[str, Any]:
        """Create a product review - إنشاء مراجعة منتج"""
        return {
            "product_id": f"product-{faker_en.uuid4()[:8]}",
            "rating": rating,
            "title": faker_en.sentence(),
            "title_ar": faker_ar.sentence(),
            "review": faker_en.text(),
            "review_ar": faker_ar.text(),
            "verified_purchase": True,
        }


# Pytest fixtures for the new factories


@pytest.fixture
def alert_factory() -> AlertFactory:
    """Alert factory - مصنع التنبيهات"""
    return AlertFactory()


@pytest.fixture
def marketplace_factory() -> MarketplaceProductFactory:
    """Marketplace product factory - مصنع منتجات السوق"""
    return MarketplaceProductFactory()


@pytest.fixture
def task_factory() -> TaskFactory:
    """Task factory - مصنع المهام"""
    return TaskFactory()


@pytest.fixture
def subscription_factory() -> SubscriptionFactory:
    """Subscription factory - مصنع الاشتراكات"""
    return SubscriptionFactory()


@pytest.fixture
def order_factory() -> OrderFactory:
    """Order factory - مصنع الطلبات"""
    return OrderFactory()


@pytest.fixture
def device_factory() -> DeviceFactory:
    """IoT device factory - مصنع أجهزة IoT"""
    return DeviceFactory()


@pytest.fixture
def review_factory() -> ReviewFactory:
    """Review factory - مصنع المراجعات"""
    return ReviewFactory()


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience Fixtures for Common Test Data - إعدادات ملائمة لبيانات الاختبار الشائعة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_field(field_factory: FieldFactory) -> dict[str, Any]:
    """Sample field data - بيانات حقل نموذجي"""
    return field_factory.create()


@pytest.fixture
def sample_location() -> dict[str, float]:
    """Sample location (Sana'a, Yemen) - موقع نموذجي (صنعاء، اليمن)"""
    return {"latitude": 15.3694, "longitude": 44.1910}


@pytest.fixture
def sample_ai_question(ai_query_factory: AIQueryFactory) -> dict[str, Any]:
    """Sample AI question - سؤال ذكاء اصطناعي نموذجي"""
    return ai_query_factory.create()


@pytest.fixture
def sample_payment(payment_factory: PaymentFactory) -> dict[str, Any]:
    """Sample payment data - بيانات دفع نموذجية"""
    return payment_factory.create()


# ═══════════════════════════════════════════════════════════════════════════════
# Service-Specific HTTP Clients - عملاء HTTP خاصة بالخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
async def field_ops_client(http_client: AsyncClient, service_urls: dict[str, str]) -> AsyncClient:
    """HTTP client for field management service - عميل HTTP لخدمة إدارة الحقول"""
    # field-core/field-ops deprecated; now uses field-management-service (port 3000)
    base_url = service_urls.get("field_management", "http://localhost:3000")
    http_client.base_url = base_url
    return http_client


@pytest.fixture
async def weather_client(http_client: AsyncClient, service_urls: dict[str, str]) -> AsyncClient:
    """HTTP client for weather service - عميل HTTP لخدمة الطقس"""
    # weather-core deprecated; now uses weather-service (port 8092)
    base_url = service_urls.get("weather_service", "http://localhost:8092")
    http_client.base_url = base_url
    return http_client


@pytest.fixture
async def ndvi_client(http_client: AsyncClient, service_urls: dict[str, str]) -> AsyncClient:
    """HTTP client for vegetation analysis service - عميل HTTP لخدمة تحليل الغطاء النباتي"""
    # ndvi-engine deprecated; now uses vegetation-analysis-service (port 8090)
    base_url = service_urls.get("vegetation_analysis_service", "http://localhost:8090")
    http_client.base_url = base_url
    return http_client


@pytest.fixture
async def ai_advisor_client(http_client: AsyncClient, service_urls: dict[str, str]) -> AsyncClient:
    """HTTP client for AI advisor - عميل HTTP للمستشار الذكي"""
    base_url = service_urls.get("ai_advisor", "http://localhost:8112")
    http_client.base_url = base_url
    return http_client


@pytest.fixture
async def billing_client(http_client: AsyncClient, service_urls: dict[str, str]) -> AsyncClient:
    """HTTP client for billing service - عميل HTTP لخدمة الفوترة"""
    base_url = service_urls.get("billing_core", "http://localhost:8089")
    http_client.base_url = base_url
    return http_client


@pytest.fixture
async def kong_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client for Kong API Gateway - عميل HTTP لبوابة Kong API"""
    async with AsyncClient(base_url="http://localhost:8000", timeout=Timeout(30.0)) as client:
        yield client


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Data and Utilities - بيانات وهمية وأدوات مساعدة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_jwt_token(test_config: TestConfig) -> str:
    """Generate a mock JWT token for testing - إنشاء رمز JWT وهمي للاختبار"""
    try:
        from datetime import datetime, timedelta

        import jwt

        payload = {
            "sub": "test-user-123",
            "tenant_id": "test-tenant-123",
            "role": "farmer",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, test_config.jwt_secret, algorithm="HS256")
        return token
    except ImportError:
        # If PyJWT not available, return a placeholder
        return "mock-jwt-token-for-testing"


@pytest.fixture
def mock_nats_message() -> dict[str, Any]:
    """Mock NATS message for testing - رسالة NATS وهمية للاختبار"""
    return {
        "subject": "test.subject",
        "data": {
            "event_type": "test_event",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {"test": "data"},
        },
    }


@pytest.fixture
def mock_redis_connection():
    """Mock Redis connection for testing - اتصال Redis وهمي للاختبار"""
    try:
        from unittest.mock import MagicMock

        mock = MagicMock()
        mock.get.return_value = None
        mock.set.return_value = True
        mock.delete.return_value = True
        return mock
    except ImportError:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Platform Integration Service Fixtures - إعدادات خدمات التكامل
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
async def ai_agents_client(
    http_client: AsyncClient, service_urls: dict[str, str], auth_headers: dict[str, str]
) -> AsyncClient:
    """
    HTTP client for AI Agents Service
    عميل HTTP لخدمة الوكلاء الذكية
    """
    base_url = service_urls.get("ai_agents_service", "http://localhost:8130")
    http_client.base_url = base_url
    http_client.headers.update(auth_headers)
    return http_client


@pytest.fixture
async def crm_client(
    http_client: AsyncClient, service_urls: dict[str, str], auth_headers: dict[str, str]
) -> AsyncClient:
    """
    HTTP client for CRM Service
    عميل HTTP لخدمة إدارة علاقات المزارعين
    """
    base_url = service_urls.get("crm_service", "http://localhost:8131")
    http_client.base_url = base_url
    http_client.headers.update(auth_headers)
    return http_client


@pytest.fixture
async def lowcode_client(
    http_client: AsyncClient, service_urls: dict[str, str], auth_headers: dict[str, str]
) -> AsyncClient:
    """
    HTTP client for Low-Code Engine Service
    عميل HTTP لمحرك التطوير منخفض الكود
    """
    base_url = service_urls.get("lowcode_engine", "http://localhost:8132")
    http_client.base_url = base_url
    http_client.headers.update(auth_headers)
    return http_client


# ═══════════════════════════════════════════════════════════════════════════════
# Platform Integration Test Data Factories - مصانع بيانات اختبارات التكامل
# ═══════════════════════════════════════════════════════════════════════════════


class AgentExecutionFactory:
    """Factory for creating AI agent execution test data - مصنع لإنشاء بيانات تنفيذ الوكلاء الذكية"""

    @staticmethod
    def create(
        agent_type: str = "farm_advisor",
        mode: str = "hybrid",
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """Create an agent execution request - إنشاء طلب تنفيذ وكيل"""
        return {
            "task": "Analyze field conditions and recommend next actions",
            "task_ar": "تحليل ظروف الحقل واقتراح الإجراءات التالية",
            "agent_type": agent_type,
            "mode": mode,
            "context": {
                "crop_type": "wheat",
                "growth_stage": "tillering",
                "soil_moisture": 45.0,
            },
            "tenant_id": tenant_id or f"test-tenant-{faker_en.uuid4()[:8]}",
            "field_id": f"field-{faker_en.uuid4()[:8]}",
        }


class FarmerCRMFactory:
    """Factory for creating farmer CRM test data - مصنع لإنشاء بيانات CRM للمزارعين"""

    @staticmethod
    def create(tenant_id: str | None = None) -> dict[str, Any]:
        """Create a farmer CRM record - إنشاء سجل CRM للمزارع"""
        unique_id = faker_en.uuid4()[:8]
        return {
            "name": f"Test Farmer {unique_id}",
            "name_ar": f"مزارع اختبار {unique_id}",
            "phone": f"+9677{faker_en.random_int(1000000, 9999999)}",
            "email": f"farmer_{unique_id}@test.sahool.com",
            "national_id": f"ID{unique_id}",
            "farm_location": "Sana'a, Yemen",
            "farm_location_ar": "صنعاء، اليمن",
            "farm_size_hectares": faker_en.pyfloat(min_value=1.0, max_value=50.0, right_digits=1),
            "primary_crops": ["wheat", "barley"],
            "tenant_id": tenant_id or f"test-tenant-{faker_en.uuid4()[:8]}",
        }


class HarvestDealFactory:
    """Factory for creating harvest deal test data - مصنع لإنشاء بيانات صفقات الحصاد"""

    @staticmethod
    def create(farmer_id: str, crop_type: str = "wheat") -> dict[str, Any]:
        """Create a harvest deal - إنشاء صفقة حصاد"""
        return {
            "farmer_id": farmer_id,
            "crop_type": crop_type,
            "crop_type_ar": "قمح" if crop_type == "wheat" else crop_type,
            "expected_quantity_tons": faker_en.pyfloat(min_value=10.0, max_value=100.0, right_digits=1),
            "expected_harvest_date": (datetime.utcnow() + timedelta(days=90)).strftime("%Y-%m-%d"),
            "price_per_ton": faker_en.pyfloat(min_value=400.0, max_value=600.0, right_digits=2),
            "notes": "Test harvest deal",
            "notes_ar": "صفقة حصاد اختبار",
        }


class LowCodePageFactory:
    """Factory for creating low-code page test data - مصنع لإنشاء بيانات صفحات التطوير منخفض الكود"""

    @staticmethod
    def create(tenant_id: str | None = None) -> dict[str, Any]:
        """Create a low-code page - إنشاء صفحة تطوير منخفض الكود"""
        unique_id = faker_en.uuid4()[:8]
        return {
            "name": f"TestPage{unique_id}",
            "name_ar": f"صفحة اختبار {unique_id}",
            "description": "Test page for integration testing",
            "route": f"/test/{unique_id}",
            "blocks": [
                {
                    "id": str(faker_en.uuid4()),
                    "component_name": "field_map",
                    "props": {"zoom": 12},
                    "children": [],
                },
            ],
            "tenant_id": tenant_id or f"test-tenant-{faker_en.uuid4()[:8]}",
        }


class LowCodeDataModelFactory:
    """Factory for creating low-code data model test data - مصنع لإنشاء بيانات نماذج التطوير منخفض الكود"""

    @staticmethod
    def create(tenant_id: str | None = None) -> dict[str, Any]:
        """Create a data model - إنشاء نموذج بيانات"""
        unique_id = faker_en.uuid4()[:8]
        return {
            "name": f"TestModel{unique_id}",
            "name_ar": f"نموذج اختبار {unique_id}",
            "description": "Test data model",
            "fields": [
                {"name": "field_name", "type": "string", "required": True},
                {"name": "area_hectares", "type": "number", "required": True},
            ],
            "tenant_id": tenant_id or f"test-tenant-{faker_en.uuid4()[:8]}",
        }


@pytest.fixture
def agent_execution_factory() -> AgentExecutionFactory:
    """Agent execution factory - مصنع تنفيذ الوكلاء"""
    return AgentExecutionFactory()


@pytest.fixture
def farmer_crm_factory() -> FarmerCRMFactory:
    """Farmer CRM factory - مصنع CRM المزارعين"""
    return FarmerCRMFactory()


@pytest.fixture
def harvest_deal_factory() -> HarvestDealFactory:
    """Harvest deal factory - مصنع صفقات الحصاد"""
    return HarvestDealFactory()


@pytest.fixture
def lowcode_page_factory() -> LowCodePageFactory:
    """Low-code page factory - مصنع صفحات التطوير منخفض الكود"""
    return LowCodePageFactory()


@pytest.fixture
def lowcode_data_model_factory() -> LowCodeDataModelFactory:
    """Low-code data model factory - مصنع نماذج التطوير منخفض الكود"""
    return LowCodeDataModelFactory()


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Event Helpers - مساعدات أحداث NATS
# ═══════════════════════════════════════════════════════════════════════════════


class NATSEventCollector:
    """
    Helper class for collecting NATS events during tests.
    فئة مساعدة لتجميع أحداث NATS أثناء الاختبارات
    """

    def __init__(self):
        self.events: list[dict[str, Any]] = []
        self.subscriptions: list[Any] = []

    async def subscribe(self, nats_client, subject: str) -> None:
        """Subscribe to a NATS subject and collect events."""
        import json

        async def handler(msg):
            try:
                data = json.loads(msg.data.decode())
                self.events.append(
                    {
                        "subject": msg.subject,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            except Exception:
                pass

        sub = await nats_client.subscribe(subject, cb=handler)
        self.subscriptions.append(sub)

    async def unsubscribe_all(self) -> None:
        """Unsubscribe from all subjects."""
        for sub in self.subscriptions:
            try:
                await sub.unsubscribe()
            except Exception:
                pass
        self.subscriptions = []

    def get_events(self, event_type: str | None = None) -> list[dict[str, Any]]:
        """Get collected events, optionally filtered by type."""
        if event_type:
            return [e for e in self.events if e.get("data", {}).get("event_type") == event_type]
        return self.events

    def clear(self) -> None:
        """Clear collected events."""
        self.events = []


@pytest.fixture
def nats_event_collector() -> NATSEventCollector:
    """NATS event collector - مجمع أحداث NATS"""
    return NATSEventCollector()


# ═══════════════════════════════════════════════════════════════════════════════
# Redis Connection Fixture - إعداد اتصال Redis
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
async def redis_client(test_config: TestConfig):
    """
    Redis client for integration tests.
    عميل Redis لاختبارات التكامل
    """
    try:
        import redis.asyncio as redis

        client = redis.from_url(test_config.redis_url)

        # Wait for Redis to be ready
        max_retries = 30
        for attempt in range(max_retries):
            try:
                await client.ping()
                yield client
                await client.close()
                return
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise

    except ImportError:
        # Redis client not installed, yield mock
        from unittest.mock import AsyncMock

        yield AsyncMock()


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced JWT Token Generation - توليد رموز JWT محسّنة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def generate_jwt_token(test_config: TestConfig):
    """
    Factory to generate JWT tokens with custom claims.
    مصنع لتوليد رموز JWT مع مطالبات مخصصة
    """

    def _generate(
        user_id: str = "test-user-123",
        tenant_id: str = "test-tenant-123",
        role: str = "farmer",
        expires_in_hours: int = 1,
    ) -> str:
        try:
            import jwt

            payload = {
                "sub": user_id,
                "tenant_id": tenant_id,
                "role": role,
                "exp": datetime.utcnow() + timedelta(hours=expires_in_hours),
                "iat": datetime.utcnow(),
            }

            return jwt.encode(payload, test_config.jwt_secret, algorithm="HS256")
        except ImportError:
            return f"mock-jwt-{user_id}-{tenant_id}-{role}"

    return _generate


@pytest.fixture
def auth_headers_for_tenant(generate_jwt_token):
    """
    Factory to generate auth headers for a specific tenant.
    مصنع لتوليد رؤوس المصادقة لمستأجر محدد
    """

    def _headers(tenant_id: str, user_id: str | None = None, role: str = "farmer") -> dict[str, str]:
        token = generate_jwt_token(
            user_id=user_id or f"user-{tenant_id}",
            tenant_id=tenant_id,
            role=role,
        )
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Tenant-ID": tenant_id,
        }

    return _headers


# ═══════════════════════════════════════════════════════════════════════════════
# Database Cleanup Helpers - مساعدات تنظيف قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
async def cleanup_test_tenant(db_cursor):
    """
    Cleanup function to remove test data for a specific tenant.
    دالة تنظيف لإزالة بيانات الاختبار لمستأجر محدد
    """
    tenants_to_cleanup = []

    def register_tenant(tenant_id: str):
        tenants_to_cleanup.append(tenant_id)
        return tenant_id

    yield register_tenant

    # Cleanup after test
    for tenant_id in tenants_to_cleanup:
        try:
            # Clean platform integration tables
            tables = [
                "agent_executions",
                "interactions",
                "harvest_deals",
                "farmers",
                "lowcode_pages",
                "lowcode_data_models",
            ]
            for table in tables:
                try:
                    db_cursor.execute(f"DELETE FROM {table} WHERE tenant_id = %s", (tenant_id,))
                except Exception:
                    pass
        except Exception:
            pass
