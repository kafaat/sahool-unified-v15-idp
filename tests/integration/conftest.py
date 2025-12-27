"""
SAHOOL Integration Test Configuration
تكوين اختبارات التكامل لمنصة سهول

Integration test fixtures for all 41+ SAHOOL services
Provides service clients, configuration, and helper functions

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import os
from typing import AsyncGenerator, Dict, Any
from dataclasses import dataclass

import pytest
import httpx


# ═══════════════════════════════════════════════════════════════════════════════
# Service Configuration - تكوين الخدمات
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ServiceConfig:
    """Service configuration - تكوين الخدمة"""
    name: str
    url: str
    health_endpoint: str
    timeout: int = 30


# Infrastructure Services - الخدمات الأساسية
INFRASTRUCTURE_SERVICES = {
    "postgres": ServiceConfig(
        name="PostgreSQL",
        url="postgresql://localhost:5432",
        health_endpoint="",  # No HTTP endpoint
        timeout=10
    ),
    "kong": ServiceConfig(
        name="Kong API Gateway",
        url="http://localhost:8000",
        health_endpoint="/",
        timeout=10
    ),
    "nats": ServiceConfig(
        name="NATS Messaging",
        url="http://localhost:8222",
        health_endpoint="/healthz",
        timeout=10
    ),
    "redis": ServiceConfig(
        name="Redis Cache",
        url="redis://localhost:6379",
        health_endpoint="",  # No HTTP endpoint
        timeout=10
    ),
    "qdrant": ServiceConfig(
        name="Qdrant Vector DB",
        url="http://localhost:6333",
        health_endpoint="/healthz",
        timeout=10
    ),
    "mqtt": ServiceConfig(
        name="MQTT Broker",
        url="mqtt://localhost:1883",
        health_endpoint="",  # No HTTP endpoint
        timeout=10
    ),
    "prometheus": ServiceConfig(
        name="Prometheus",
        url="http://localhost:9090",
        health_endpoint="/-/healthy",
        timeout=10
    ),
    "grafana": ServiceConfig(
        name="Grafana",
        url="http://localhost:3002",
        health_endpoint="/api/health",
        timeout=10
    ),
}

# Application Services - خدمات التطبيق
APPLICATION_SERVICES = {
    "field_core": ServiceConfig(
        name="Field Core Service",
        url="http://localhost:3000",
        health_endpoint="/healthz",
        timeout=30
    ),
    "field_ops": ServiceConfig(
        name="Field Operations Service",
        url="http://localhost:8080",
        health_endpoint="/healthz",
        timeout=30
    ),
    "ndvi_engine": ServiceConfig(
        name="NDVI Engine",
        url="http://localhost:8107",
        health_endpoint="/healthz",
        timeout=30
    ),
    "weather_core": ServiceConfig(
        name="Weather Core Service",
        url="http://localhost:8108",
        health_endpoint="/healthz",
        timeout=30
    ),
    "field_chat": ServiceConfig(
        name="Field Chat Service",
        url="http://localhost:8099",
        health_endpoint="/healthz",
        timeout=30
    ),
    "iot_gateway": ServiceConfig(
        name="IoT Gateway",
        url="http://localhost:8106",
        health_endpoint="/healthz",
        timeout=30
    ),
    "agro_advisor": ServiceConfig(
        name="Agro Advisor Service",
        url="http://localhost:8105",
        health_endpoint="/healthz",
        timeout=30
    ),
    "ws_gateway": ServiceConfig(
        name="WebSocket Gateway",
        url="http://localhost:8081",
        health_endpoint="/healthz",
        timeout=30
    ),
    "crop_health": ServiceConfig(
        name="Crop Health Service",
        url="http://localhost:8100",
        health_endpoint="/healthz",
        timeout=30
    ),
    "task_service": ServiceConfig(
        name="Task Service",
        url="http://localhost:8103",
        health_endpoint="/health",
        timeout=30
    ),
    "equipment_service": ServiceConfig(
        name="Equipment Service",
        url="http://localhost:8101",
        health_endpoint="/health",
        timeout=30
    ),
    "provider_config": ServiceConfig(
        name="Provider Configuration Service",
        url="http://localhost:8104",
        health_endpoint="/health",
        timeout=30
    ),
    "crop_health_ai": ServiceConfig(
        name="Crop Health AI",
        url="http://localhost:8095",
        health_endpoint="/healthz",
        timeout=30
    ),
    "virtual_sensors": ServiceConfig(
        name="Virtual Sensors Engine",
        url="http://localhost:8096",
        health_endpoint="/healthz",
        timeout=30
    ),
    "community_chat": ServiceConfig(
        name="Community Chat Service",
        url="http://localhost:8097",
        health_endpoint="/healthz",
        timeout=30
    ),
    "yield_engine": ServiceConfig(
        name="Yield Prediction Engine",
        url="http://localhost:8098",
        health_endpoint="/healthz",
        timeout=30
    ),
    "irrigation_smart": ServiceConfig(
        name="Smart Irrigation Service",
        url="http://localhost:8094",
        health_endpoint="/healthz",
        timeout=30
    ),
    "fertilizer_advisor": ServiceConfig(
        name="Fertilizer Advisor Service",
        url="http://localhost:8093",
        health_endpoint="/healthz",
        timeout=30
    ),
    "indicators_service": ServiceConfig(
        name="Agricultural Indicators Service",
        url="http://localhost:8091",
        health_endpoint="/healthz",
        timeout=30
    ),
    "satellite_service": ServiceConfig(
        name="Satellite Service",
        url="http://localhost:8090",
        health_endpoint="/healthz",
        timeout=30
    ),
    "weather_advanced": ServiceConfig(
        name="Weather Advanced Service",
        url="http://localhost:8092",
        health_endpoint="/healthz",
        timeout=30
    ),
    "notification_service": ServiceConfig(
        name="Notification Service",
        url="http://localhost:8110",
        health_endpoint="/healthz",
        timeout=30
    ),
    "research_core": ServiceConfig(
        name="Research Core Service",
        url="http://localhost:3015",
        health_endpoint="/api/v1/healthz",
        timeout=30
    ),
    "disaster_assessment": ServiceConfig(
        name="Disaster Assessment Service",
        url="http://localhost:3020",
        health_endpoint="/api/v1/disasters/health",
        timeout=30
    ),
    "yield_prediction": ServiceConfig(
        name="Yield Prediction Service",
        url="http://localhost:3021",
        health_endpoint="/api/v1/yield/health",
        timeout=30
    ),
    "lai_estimation": ServiceConfig(
        name="LAI Estimation Service",
        url="http://localhost:3022",
        health_endpoint="/api/v1/lai/health",
        timeout=30
    ),
    "crop_growth_model": ServiceConfig(
        name="Crop Growth Model Service",
        url="http://localhost:3023",
        health_endpoint="/api/v1/simulation/health",
        timeout=30
    ),
    "marketplace_service": ServiceConfig(
        name="Marketplace Service",
        url="http://localhost:3010",
        health_endpoint="/api/v1/healthz",
        timeout=30
    ),
    "admin_dashboard": ServiceConfig(
        name="Admin Dashboard",
        url="http://localhost:3001",
        health_endpoint="/",
        timeout=30
    ),
    "billing_core": ServiceConfig(
        name="Billing Core Service",
        url="http://localhost:8089",
        health_endpoint="/healthz",
        timeout=30
    ),
    "ai_advisor": ServiceConfig(
        name="AI Advisor Multi-Agent System",
        url="http://localhost:8112",
        health_endpoint="/healthz",
        timeout=30
    ),
    "astronomical_calendar": ServiceConfig(
        name="Astronomical Calendar Service",
        url="http://localhost:8111",
        health_endpoint="/healthz",
        timeout=30
    ),
}

# All services combined - جميع الخدمات
ALL_SERVICES = {**INFRASTRUCTURE_SERVICES, **APPLICATION_SERVICES}


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP Client Fixtures - عملاء HTTP
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Shared async HTTP client for all tests
    عميل HTTP غير متزامن مشترك لجميع الاختبارات
    """
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        yield client


@pytest.fixture(scope="session")
def service_configs() -> Dict[str, ServiceConfig]:
    """
    All service configurations
    تكوينات جميع الخدمات
    """
    return ALL_SERVICES


@pytest.fixture(scope="session")
def infrastructure_configs() -> Dict[str, ServiceConfig]:
    """
    Infrastructure service configurations
    تكوينات الخدمات الأساسية
    """
    return INFRASTRUCTURE_SERVICES


@pytest.fixture(scope="session")
def application_configs() -> Dict[str, ServiceConfig]:
    """
    Application service configurations
    تكوينات خدمات التطبيق
    """
    return APPLICATION_SERVICES


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication Fixtures - الاعتماد
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def test_token() -> str:
    """
    Test JWT token for authenticated requests
    رمز JWT للطلبات المصادق عليها
    """
    return os.getenv("TEST_JWT_TOKEN", "test-token-123")


@pytest.fixture
def auth_headers(test_token: str) -> Dict[str, str]:
    """
    Authentication headers for API requests
    رؤوس المصادقة لطلبات API
    """
    return {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Database Fixtures - قاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def postgres_url() -> str:
    """PostgreSQL connection URL"""
    user = os.getenv("POSTGRES_USER", "sahool")
    password = os.getenv("POSTGRES_PASSWORD", "sahool")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "sahool")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# ═══════════════════════════════════════════════════════════════════════════════
# Redis Fixtures - ذاكرة التخزين المؤقت
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def redis_url() -> str:
    """Redis connection URL"""
    password = os.getenv("REDIS_PASSWORD", "changeme")
    host = os.getenv("REDIS_HOST", "localhost")
    port = os.getenv("REDIS_PORT", "6379")
    return f"redis://:{password}@{host}:{port}/0"


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Fixtures - نظام الرسائل
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def nats_url() -> str:
    """NATS connection URL"""
    host = os.getenv("NATS_HOST", "localhost")
    port = os.getenv("NATS_PORT", "4222")
    return f"nats://{host}:{port}"


# ═══════════════════════════════════════════════════════════════════════════════
# Qdrant Fixtures - قاعدة البيانات المتجهة
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def qdrant_config() -> Dict[str, Any]:
    """Qdrant configuration"""
    return {
        "host": os.getenv("QDRANT_HOST", "localhost"),
        "port": int(os.getenv("QDRANT_PORT", "6333")),
        "grpc_port": int(os.getenv("QDRANT_GRPC_PORT", "6334")),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Service Client Fixtures - عملاء الخدمات
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
async def field_ops_client(http_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Field Operations service client"""
    http_client.base_url = "http://localhost:8080"
    return http_client


@pytest.fixture
async def weather_client(http_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Weather service client"""
    http_client.base_url = "http://localhost:8108"
    return http_client


@pytest.fixture
async def ndvi_client(http_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """NDVI Engine client"""
    http_client.base_url = "http://localhost:8107"
    return http_client


@pytest.fixture
async def ai_advisor_client(http_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """AI Advisor service client"""
    http_client.base_url = "http://localhost:8112"
    return http_client


@pytest.fixture
async def billing_client(http_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Billing Core service client"""
    http_client.base_url = "http://localhost:8089"
    return http_client


@pytest.fixture
async def kong_client(http_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Kong API Gateway client"""
    http_client.base_url = "http://localhost:8000"
    return http_client


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Fixtures - بيانات الاختبار
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_field() -> Dict[str, Any]:
    """
    Sample field data for testing
    بيانات حقل عينة للاختبار
    """
    return {
        "name": "Test Field",
        "name_ar": "حقل الاختبار",
        "area_hectares": 10.5,
        "crop_type": "wheat",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.0, 15.0],
                    [44.1, 15.0],
                    [44.1, 15.1],
                    [44.0, 15.1],
                    [44.0, 15.0]
                ]
            ]
        }
    }


@pytest.fixture
def sample_location() -> Dict[str, float]:
    """
    Sample location (Sana'a, Yemen)
    موقع عينة (صنعاء، اليمن)
    """
    return {
        "latitude": 15.3694,
        "longitude": 44.1910
    }


@pytest.fixture
def sample_ai_question() -> Dict[str, Any]:
    """
    Sample AI advisor question
    سؤال عينة للمستشار الذكي
    """
    return {
        "question": "ما هو أفضل وقت لزراعة القمح في اليمن؟",
        "question_en": "What is the best time to plant wheat in Yemen?",
        "field_id": "test-field-123",
        "language": "ar"
    }


@pytest.fixture
def sample_payment() -> Dict[str, Any]:
    """
    Sample payment data
    بيانات دفع عينة
    """
    return {
        "amount": 100.00,
        "currency": "YER",
        "payment_method": "tharwatt",
        "description": "SAHOOL Subscription - Monthly"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions - دوال مساعدة
# ═══════════════════════════════════════════════════════════════════════════════

async def wait_for_service(
    client: httpx.AsyncClient,
    config: ServiceConfig,
    max_retries: int = 10,
    delay: float = 2.0
) -> bool:
    """
    Wait for a service to become healthy
    انتظار حتى تصبح الخدمة جاهزة

    Args:
        client: HTTP client
        config: Service configuration
        max_retries: Maximum retry attempts
        delay: Delay between retries in seconds

    Returns:
        True if service is healthy, False otherwise
    """
    import asyncio

    if not config.health_endpoint:
        return True  # Services without health endpoints are assumed ready

    url = f"{config.url}{config.health_endpoint}"

    for attempt in range(max_retries):
        try:
            response = await client.get(url, timeout=config.timeout)
            if response.status_code in (200, 204):
                return True
        except (httpx.ConnectError, httpx.TimeoutException):
            pass

        if attempt < max_retries - 1:
            await asyncio.sleep(delay)

    return False


@pytest.fixture
async def ensure_services_ready(
    http_client: httpx.AsyncClient,
    service_configs: Dict[str, ServiceConfig]
) -> None:
    """
    Ensure all critical services are ready before running tests
    التأكد من أن جميع الخدمات الحرجة جاهزة قبل تشغيل الاختبارات
    """
    critical_services = ["kong", "nats", "field_ops", "weather_core"]

    for service_name in critical_services:
        if service_name in service_configs:
            config = service_configs[service_name]
            is_ready = await wait_for_service(http_client, config)
            if not is_ready:
                pytest.skip(f"Service {config.name} is not ready")
