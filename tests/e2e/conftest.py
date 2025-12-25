"""
SAHOOL E2E Test Configuration
تكوين اختبارات من البداية إلى النهاية

E2E test fixtures for workflow testing
Provides complete workflow setup and teardown

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import pytest
import httpx
import asyncio
from typing import Dict, Any, Optional
import uuid


# ═══════════════════════════════════════════════════════════════════════════════
# E2E Test Configuration - تكوين اختبارات E2E
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def e2e_timeout() -> int:
    """Timeout for E2E tests in seconds"""
    return 120


@pytest.fixture(scope="session")
def e2e_retry_count() -> int:
    """Number of retries for E2E operations"""
    return 3


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Generators - مولدات بيانات الاختبار
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def unique_field_name() -> str:
    """Generate unique field name for testing"""
    return f"E2E Test Field {uuid.uuid4().hex[:8]}"


@pytest.fixture
def unique_user_id() -> str:
    """Generate unique user ID for testing"""
    return f"e2e-user-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_field_data(unique_field_name: str) -> Dict[str, Any]:
    """
    Complete field data for E2E testing
    بيانات حقل كاملة لاختبار E2E
    """
    return {
        "name": unique_field_name,
        "name_ar": f"حقل اختبار {unique_field_name}",
        "description": "E2E test field for comprehensive workflow testing",
        "area_hectares": 15.5,
        "crop_type": "wheat",
        "soil_type": "clay_loam",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.0, 15.0],
                    [44.01, 15.0],
                    [44.01, 15.01],
                    [44.0, 15.01],
                    [44.0, 15.0]
                ]
            ]
        },
        "location": {
            "latitude": 15.005,
            "longitude": 44.005
        }
    }


@pytest.fixture
def test_location_yemen() -> Dict[str, float]:
    """
    Test location in Yemen (Sana'a)
    موقع اختبار في اليمن (صنعاء)
    """
    return {
        "latitude": 15.3694,
        "longitude": 44.1910,
        "altitude": 2250
    }


@pytest.fixture
def test_subscription_data() -> Dict[str, Any]:
    """
    Test subscription data
    بيانات اشتراك الاختبار
    """
    return {
        "plan": "premium",
        "billing_cycle": "monthly",
        "currency": "YER",
        "auto_renew": True
    }


@pytest.fixture
def test_payment_data() -> Dict[str, Any]:
    """
    Test payment data for Tharwatt
    بيانات الدفع الاختبارية لثروات
    """
    return {
        "amount": 5000.00,
        "currency": "YER",
        "payment_method": "tharwatt",
        "description": "SAHOOL Premium Subscription - Monthly",
        "customer_name": "E2E Test User",
        "customer_email": "e2e-test@sahool.io",
        "customer_phone": "+967777123456"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Workflow Helper Functions - دوال مساعدة لسير العمل
# ═══════════════════════════════════════════════════════════════════════════════

async def wait_for_async_operation(
    client: httpx.AsyncClient,
    check_url: str,
    headers: Dict[str, str],
    expected_status: str = "completed",
    max_attempts: int = 30,
    delay: float = 2.0
) -> Optional[Dict[str, Any]]:
    """
    Wait for an async operation to complete
    انتظار اكتمال عملية غير متزامنة

    Args:
        client: HTTP client
        check_url: URL to check operation status
        headers: Request headers
        expected_status: Expected final status
        max_attempts: Maximum number of check attempts
        delay: Delay between checks in seconds

    Returns:
        Operation result or None if timeout
    """
    for attempt in range(max_attempts):
        try:
            response = await client.get(check_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status") or data.get("state")

                if status == expected_status:
                    return data
                elif status in ("failed", "error"):
                    return None

        except Exception:
            pass

        await asyncio.sleep(delay)

    return None


@pytest.fixture
async def workflow_client() -> httpx.AsyncClient:
    """
    HTTP client for workflow tests with extended timeout
    عميل HTTP لاختبارات سير العمل مع وقت انتظار ممتد
    """
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
def e2e_headers(test_token: str) -> Dict[str, str]:
    """
    Headers for E2E workflow tests
    رؤوس لاختبارات سير العمل E2E
    """
    return {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Test-Run": "e2e",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Service Availability Checks - فحوصات توفر الخدمات
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
async def ensure_field_ops_ready():
    """Ensure Field Ops service is ready"""
    async with httpx.AsyncClient() as client:
        for _ in range(10):
            try:
                response = await client.get("http://localhost:8080/healthz")
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            await asyncio.sleep(2)
        pytest.skip("Field Ops service not ready")


@pytest.fixture(scope="session")
async def ensure_weather_ready():
    """Ensure Weather service is ready"""
    async with httpx.AsyncClient() as client:
        for _ in range(10):
            try:
                response = await client.get("http://localhost:8108/healthz")
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            await asyncio.sleep(2)
        pytest.skip("Weather service not ready")


@pytest.fixture(scope="session")
async def ensure_ndvi_ready():
    """Ensure NDVI Engine is ready"""
    async with httpx.AsyncClient() as client:
        for _ in range(10):
            try:
                response = await client.get("http://localhost:8107/healthz")
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            await asyncio.sleep(2)
        pytest.skip("NDVI Engine not ready")


@pytest.fixture(scope="session")
async def ensure_billing_ready():
    """Ensure Billing service is ready"""
    async with httpx.AsyncClient() as client:
        for _ in range(10):
            try:
                response = await client.get("http://localhost:8089/healthz")
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            await asyncio.sleep(2)
        pytest.skip("Billing service not ready")


@pytest.fixture(scope="session")
async def ensure_ai_advisor_ready():
    """Ensure AI Advisor is ready"""
    async with httpx.AsyncClient() as client:
        for _ in range(10):
            try:
                response = await client.get("http://localhost:8112/healthz")
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            await asyncio.sleep(2)
        pytest.skip("AI Advisor not ready")


# ═══════════════════════════════════════════════════════════════════════════════
# Cleanup Fixtures - تنظيف بعد الاختبار
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
async def cleanup_test_data():
    """
    Cleanup test data after E2E tests
    تنظيف بيانات الاختبار بعد اختبارات E2E
    """
    created_resources = {
        "fields": [],
        "subscriptions": [],
        "tasks": []
    }

    yield created_resources

    # Cleanup logic would go here
    # In a real scenario, we'd delete all created resources
    # For now, we just track them
    pass
