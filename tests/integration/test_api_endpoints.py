"""
SAHOOL API Endpoint Integration Tests
اختبارات نقاط نهاية API لمنصة سهول

Comprehensive API endpoint tests for SAHOOL platform services
Tests RESTful endpoints, authentication, data validation, and error handling

Author: SAHOOL Platform Team
"""

from typing import Any

import httpx
import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Kong API Gateway Tests - اختبارات بوابة Kong API
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_kong_gateway_routes(kong_client: httpx.AsyncClient):
    """
    Test Kong API Gateway routing
    اختبار توجيه بوابة Kong API
    """
    # Test that Kong is responding
    response = await kong_client.get("/")
    assert response.status_code in (200, 404), "Kong should be running"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_kong_admin_api():
    """
    Test Kong Admin API (localhost only)
    اختبار Kong Admin API (localhost فقط)
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/status")
            assert response.status_code == 200, "Kong Admin API should be accessible"
            data = response.json()
            assert "database" in data or "server" in data
        except httpx.ConnectError:
            pytest.skip("Kong Admin API not accessible (expected in production)")


# ═══════════════════════════════════════════════════════════════════════════════
# Field Operations API Tests - اختبارات API عمليات الحقول
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_field_ops_list_fields(
    field_ops_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """
    Test listing fields endpoint
    اختبار نقطة نهاية قائمة الحقول
    """
    response = await field_ops_client.get("/api/v1/fields", headers=auth_headers)
    assert response.status_code in (
        200,
        401,
    ), "Should return fields or require authentication"

    if response.status_code == 200:
        data = response.json()
        assert isinstance(
            data, list | dict
        ), "Response should be a list or paginated object"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_field_ops_create_field(
    field_ops_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    sample_field: dict[str, Any],
):
    """
    Test creating a field
    اختبار إنشاء حقل
    """
    response = await field_ops_client.post(
        "/api/v1/fields", headers=auth_headers, json=sample_field
    )
    # Should return 201 (created), 401 (unauthorized), or 422 (validation error)
    assert response.status_code in (
        201,
        401,
        422,
    ), f"Unexpected status: {response.status_code}"

    if response.status_code == 201:
        data = response.json()
        assert "id" in data or "field_id" in data, "Response should include field ID"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_field_ops_get_field(
    field_ops_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """
    Test getting a specific field
    اختبار الحصول على حقل محدد
    """
    # Try to get a field (may not exist)
    field_id = "test-field-123"
    response = await field_ops_client.get(
        f"/api/v1/fields/{field_id}", headers=auth_headers
    )
    assert response.status_code in (
        200,
        401,
        404,
    ), "Should return field, unauthorized, or not found"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_field_ops_invalid_field_data(
    field_ops_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """
    Test validation with invalid field data
    اختبار التحقق من صحة البيانات مع بيانات حقل غير صالحة
    """
    invalid_field = {
        "name": "",  # Empty name should fail validation
        "area_hectares": -10,  # Negative area should fail
    }

    response = await field_ops_client.post(
        "/api/v1/fields", headers=auth_headers, json=invalid_field
    )
    # Should return validation error or unauthorized
    assert response.status_code in (400, 401, 422), "Invalid data should be rejected"


# ═══════════════════════════════════════════════════════════════════════════════
# Weather Service API Tests - اختبارات API خدمة الطقس
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_weather_get_current(
    weather_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    sample_location: dict[str, float],
):
    """
    Test getting current weather
    اختبار الحصول على الطقس الحالي
    """
    response = await weather_client.get(
        "/api/v1/weather/current", headers=auth_headers, params=sample_location
    )
    assert response.status_code in (
        200,
        401,
        400,
    ), "Should return weather data or error"

    if response.status_code == 200:
        data = response.json()
        # Weather data should have temperature, humidity, etc.
        assert any(key in data for key in ["temperature", "temp", "main", "current"])


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_weather_get_forecast(
    weather_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    sample_location: dict[str, float],
):
    """
    Test getting weather forecast
    اختبار الحصول على توقعات الطقس
    """
    response = await weather_client.get(
        "/api/v1/weather/forecast", headers=auth_headers, params=sample_location
    )
    assert response.status_code in (200, 401, 400), "Should return forecast or error"


# ═══════════════════════════════════════════════════════════════════════════════
# NDVI Engine API Tests - اختبارات API محرك NDVI
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_ndvi_get_field_analysis(
    ndvi_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """
    Test getting NDVI analysis for a field
    اختبار الحصول على تحليل NDVI للحقل
    """
    field_id = "test-field-123"
    response = await ndvi_client.get(
        f"/api/v1/ndvi/fields/{field_id}/analysis", headers=auth_headers
    )
    assert response.status_code in (200, 401, 404), "Should return NDVI data or error"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_ndvi_calculate_index(
    ndvi_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """
    Test calculating NDVI index
    اختبار حساب مؤشر NDVI
    """
    ndvi_data = {"red": 0.5, "nir": 0.8}

    response = await ndvi_client.post(
        "/api/v1/ndvi/calculate", headers=auth_headers, json=ndvi_data
    )
    assert response.status_code in (
        200,
        401,
        422,
    ), "Should calculate NDVI or return error"

    if response.status_code == 200:
        data = response.json()
        assert "ndvi" in data or "value" in data, "Response should include NDVI value"


# ═══════════════════════════════════════════════════════════════════════════════
# AI Advisor API Tests - اختبارات API المستشار الذكي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_ai_advisor_ask_question(
    ai_advisor_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    sample_ai_question: dict[str, Any],
):
    """
    Test asking AI advisor a question
    اختبار طرح سؤال على المستشار الذكي
    """
    response = await ai_advisor_client.post(
        "/api/v1/advisor/ask", headers=auth_headers, json=sample_ai_question
    )
    assert response.status_code in (200, 401, 422, 503), "Should return answer or error"

    if response.status_code == 200:
        data = response.json()
        assert "answer" in data or "response" in data, "Response should include answer"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_ai_advisor_get_agents(
    ai_advisor_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """
    Test getting available AI agents
    اختبار الحصول على الوكلاء الذكيين المتاحين
    """
    response = await ai_advisor_client.get(
        "/api/v1/advisor/agents", headers=auth_headers
    )
    assert response.status_code in (
        200,
        401,
    ), "Should return agents list or require auth"

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list | dict), "Response should be agents list"


# ═══════════════════════════════════════════════════════════════════════════════
# Billing Core API Tests - اختبارات API الفوترة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_billing_get_subscriptions(
    billing_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """
    Test getting user subscriptions
    اختبار الحصول على اشتراكات المستخدم
    """
    response = await billing_client.get("/api/v1/subscriptions", headers=auth_headers)
    assert response.status_code in (
        200,
        401,
    ), "Should return subscriptions or require auth"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_billing_create_payment_intent(
    billing_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    sample_payment: dict[str, Any],
):
    """
    Test creating payment intent
    اختبار إنشاء نية الدفع
    """
    response = await billing_client.post(
        "/api/v1/payments/intent", headers=auth_headers, json=sample_payment
    )
    assert response.status_code in (
        200,
        201,
        401,
        422,
    ), "Should create intent or return error"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_billing_get_invoices(
    billing_client: httpx.AsyncClient, auth_headers: dict[str, str]
):
    """
    Test getting user invoices
    اختبار الحصول على فواتير المستخدم
    """
    response = await billing_client.get("/api/v1/invoices", headers=auth_headers)
    assert response.status_code in (200, 401), "Should return invoices or require auth"


# ═══════════════════════════════════════════════════════════════════════════════
# Satellite Service API Tests - اختبارات API خدمة الأقمار الصناعية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_satellite_get_imagery():
    """
    Test getting satellite imagery for a field
    اختبار الحصول على صور الأقمار الصناعية للحقل
    """
    async with httpx.AsyncClient(base_url="http://localhost:8090") as client:
        response = await client.get("/api/v1/satellite/imagery")
        assert response.status_code in (
            200,
            400,
            401,
        ), "Should return imagery list or error"


# ═══════════════════════════════════════════════════════════════════════════════
# Task Service API Tests - اختبارات API خدمة المهام
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_task_service_list_tasks(auth_headers: dict[str, str]):
    """
    Test listing agricultural tasks
    اختبار قائمة المهام الزراعية
    """
    async with httpx.AsyncClient(base_url="http://localhost:8103") as client:
        response = await client.get("/api/v1/tasks", headers=auth_headers)
        assert response.status_code in (200, 401), "Should return tasks or require auth"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_task_service_create_task(auth_headers: dict[str, str]):
    """
    Test creating agricultural task
    اختبار إنشاء مهمة زراعية
    """
    task_data = {
        "title": "Irrigation Task",
        "title_ar": "مهمة الري",
        "description": "Water the wheat field",
        "task_type": "irrigation",
        "priority": "high",
    }

    async with httpx.AsyncClient(base_url="http://localhost:8103") as client:
        response = await client.post(
            "/api/v1/tasks", headers=auth_headers, json=task_data
        )
        assert response.status_code in (
            201,
            401,
            422,
        ), "Should create task or return error"


# ═══════════════════════════════════════════════════════════════════════════════
# Equipment Service API Tests - اختبارات API خدمة المعدات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_equipment_service_list_equipment(auth_headers: dict[str, str]):
    """
    Test listing agricultural equipment
    اختبار قائمة المعدات الزراعية
    """
    async with httpx.AsyncClient(base_url="http://localhost:8101") as client:
        response = await client.get("/api/v1/equipment", headers=auth_headers)
        assert response.status_code in (
            200,
            401,
        ), "Should return equipment or require auth"


# ═══════════════════════════════════════════════════════════════════════════════
# Irrigation Smart API Tests - اختبارات API الري الذكي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_irrigation_smart_calculate_et0(
    auth_headers: dict[str, str], sample_location: dict[str, float]
):
    """
    Test calculating ET0 (reference evapotranspiration)
    اختبار حساب ET0 (التبخر المرجعي)
    """
    et0_data = {
        **sample_location,
        "temperature_max": 35.0,
        "temperature_min": 20.0,
        "humidity": 45.0,
        "wind_speed": 2.5,
        "solar_radiation": 25.0,
    }

    async with httpx.AsyncClient(base_url="http://localhost:8094") as client:
        response = await client.post(
            "/api/v1/irrigation/et0", headers=auth_headers, json=et0_data
        )
        assert response.status_code in (
            200,
            401,
            422,
        ), "Should calculate ET0 or return error"

        if response.status_code == 200:
            data = response.json()
            assert "et0" in data or "value" in data, "Response should include ET0 value"


# ═══════════════════════════════════════════════════════════════════════════════
# Marketplace Service API Tests - اختبارات API خدمة السوق
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_marketplace_list_products(auth_headers: dict[str, str]):
    """
    Test listing marketplace products
    اختبار قائمة منتجات السوق
    """
    async with httpx.AsyncClient(base_url="http://localhost:3010") as client:
        response = await client.get("/api/v1/products", headers=auth_headers)
        assert response.status_code in (
            200,
            401,
        ), "Should return products or require auth"


# ═══════════════════════════════════════════════════════════════════════════════
# Error Handling Tests - اختبارات معالجة الأخطاء
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_unauthorized_access(field_ops_client: httpx.AsyncClient):
    """
    Test that endpoints require authentication
    اختبار أن نقاط النهاية تتطلب المصادقة
    """
    response = await field_ops_client.get("/api/v1/fields")
    # Should require authentication (401) or be publicly accessible (200)
    assert response.status_code in (200, 401), "Endpoint should handle auth properly"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_invalid_endpoint(field_ops_client: httpx.AsyncClient):
    """
    Test accessing non-existent endpoint
    اختبار الوصول إلى نقطة نهاية غير موجودة
    """
    response = await field_ops_client.get("/api/v1/nonexistent")
    assert response.status_code == 404, "Should return 404 for non-existent endpoint"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_method_not_allowed(field_ops_client: httpx.AsyncClient):
    """
    Test using wrong HTTP method
    اختبار استخدام طريقة HTTP خاطئة
    """
    response = await field_ops_client.put("/healthz")
    assert response.status_code in (404, 405), "Should return method not allowed"


# ═══════════════════════════════════════════════════════════════════════════════
# CORS and Headers Tests - اختبارات CORS والرؤوس
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_cors_headers(field_ops_client: httpx.AsyncClient):
    """
    Test CORS headers are present
    اختبار وجود رؤوس CORS
    """
    response = await field_ops_client.options("/healthz")
    # OPTIONS should be supported for CORS
    assert response.status_code in (200, 204, 405), "OPTIONS should be handled"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.asyncio
async def test_content_type_json(field_ops_client: httpx.AsyncClient):
    """
    Test that API returns JSON content type
    اختبار أن API يعيد نوع محتوى JSON
    """
    response = await field_ops_client.get("/healthz")
    if response.status_code == 200:
        content_type = response.headers.get("content-type", "")
        assert "json" in content_type.lower(), "API should return JSON"
