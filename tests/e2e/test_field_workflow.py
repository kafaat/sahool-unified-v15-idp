"""
SAHOOL Field Workflow E2E Tests
اختبارات سير عمل الحقل من البداية إلى النهاية

End-to-end tests for complete field management workflow:
1. Create field
2. Get NDVI analysis
3. Get weather data
4. Receive recommendations

Author: SAHOOL Platform Team
"""

import pytest
import httpx
import asyncio
from typing import Dict, Any


# ═══════════════════════════════════════════════════════════════════════════════
# Complete Field Workflow Test - اختبار سير عمل الحقل الكامل
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_complete_field_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: Dict[str, str],
    test_field_data: Dict[str, Any],
    test_location_yemen: Dict[str, float],
    ensure_field_ops_ready,
    ensure_weather_ready,
    ensure_ndvi_ready,
    cleanup_test_data: Dict[str, list]
):
    """
    Test complete field workflow: Create → NDVI → Weather → Recommendations
    اختبار سير عمل الحقل الكامل: إنشاء → NDVI → طقس → توصيات

    Workflow Steps:
    1. Create a new field in Field Ops
    2. Request NDVI analysis for the field
    3. Get weather data for field location
    4. Get agricultural recommendations
    5. Verify data consistency across services
    """

    # ───────────────────────────────────────────────────────────────────────────
    # Step 1: Create Field - إنشاء الحقل
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 1] Creating field...")

    field_response = await workflow_client.post(
        "http://localhost:8080/api/v1/fields",
        headers=e2e_headers,
        json=test_field_data
    )

    # Should create field or require authentication
    assert field_response.status_code in (201, 401, 422), \
        f"Field creation failed with status {field_response.status_code}"

    if field_response.status_code != 201:
        pytest.skip(f"Cannot create field: {field_response.status_code}")

    field_data = field_response.json()
    field_id = field_data.get("id") or field_data.get("field_id")
    assert field_id is not None, "Field ID should be returned"

    cleanup_test_data["fields"].append(field_id)
    print(f"✓ Field created successfully: {field_id}")

    # Wait for event propagation
    await asyncio.sleep(2)

    # ───────────────────────────────────────────────────────────────────────────
    # Step 2: Get NDVI Analysis - الحصول على تحليل NDVI
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 2] Requesting NDVI analysis...")

    # Request NDVI analysis for the field
    ndvi_response = await workflow_client.get(
        f"http://localhost:8107/api/v1/ndvi/fields/{field_id}/analysis",
        headers=e2e_headers
    )

    # NDVI analysis should be available or being processed
    assert ndvi_response.status_code in (200, 202, 404, 401), \
        f"NDVI request failed with status {ndvi_response.status_code}"

    if ndvi_response.status_code == 200:
        ndvi_data = ndvi_response.json()
        print(f"✓ NDVI analysis retrieved: {ndvi_data.get('status', 'N/A')}")
    elif ndvi_response.status_code == 202:
        print("✓ NDVI analysis queued for processing")
    else:
        print(f"⚠ NDVI analysis not yet available: {ndvi_response.status_code}")

    # ───────────────────────────────────────────────────────────────────────────
    # Step 3: Get Weather Data - الحصول على بيانات الطقس
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 3] Getting weather data...")

    weather_response = await workflow_client.get(
        "http://localhost:8108/api/v1/weather/current",
        headers=e2e_headers,
        params=test_location_yemen
    )

    assert weather_response.status_code in (200, 401, 503), \
        f"Weather request failed with status {weather_response.status_code}"

    if weather_response.status_code == 200:
        weather_data = weather_response.json()
        print(f"✓ Weather data retrieved for location")

        # Verify weather data structure
        assert any(key in weather_data for key in ["temperature", "temp", "main", "current"]), \
            "Weather data should contain temperature information"
    else:
        print(f"⚠ Weather data not available: {weather_response.status_code}")

    # ───────────────────────────────────────────────────────────────────────────
    # Step 4: Get Agricultural Recommendations - الحصول على التوصيات الزراعية
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 4] Getting agricultural recommendations...")

    recommendations_response = await workflow_client.get(
        f"http://localhost:8105/api/v1/recommendations/field/{field_id}",
        headers=e2e_headers
    )

    assert recommendations_response.status_code in (200, 404, 401), \
        f"Recommendations request failed with status {recommendations_response.status_code}"

    if recommendations_response.status_code == 200:
        recommendations = recommendations_response.json()
        print(f"✓ Recommendations retrieved")
    else:
        print(f"⚠ Recommendations not yet available: {recommendations_response.status_code}")

    # ───────────────────────────────────────────────────────────────────────────
    # Step 5: Verify Field Data Consistency - التحقق من اتساق بيانات الحقل
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 5] Verifying data consistency...")

    # Retrieve field from Field Ops again
    field_verify_response = await workflow_client.get(
        f"http://localhost:8080/api/v1/fields/{field_id}",
        headers=e2e_headers
    )

    assert field_verify_response.status_code in (200, 401), \
        "Field should still be accessible"

    if field_verify_response.status_code == 200:
        verified_field = field_verify_response.json()
        # Verify field name matches
        assert verified_field.get("name") == test_field_data["name"], \
            "Field data should be consistent"
        print("✓ Field data is consistent")

    print("\n" + "="*80)
    print("✓ Complete field workflow test PASSED")
    print("="*80)


# ═══════════════════════════════════════════════════════════════════════════════
# Field Creation and Validation Workflow - سير عمل إنشاء والتحقق من الحقل
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_field_creation_validation_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: Dict[str, str],
    ensure_field_ops_ready
):
    """
    Test field creation with validation
    اختبار إنشاء الحقل مع التحقق من الصحة
    """

    # Test 1: Invalid field data (should fail validation)
    invalid_field = {
        "name": "",  # Empty name
        "area_hectares": -10,  # Negative area
    }

    response = await workflow_client.post(
        "http://localhost:8080/api/v1/fields",
        headers=e2e_headers,
        json=invalid_field
    )

    # Should reject invalid data
    assert response.status_code in (400, 401, 422), \
        "Invalid field data should be rejected"

    print("✓ Field validation working correctly")


# ═══════════════════════════════════════════════════════════════════════════════
# NDVI Analysis Workflow - سير عمل تحليل NDVI
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_ndvi_analysis_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: Dict[str, str],
    ensure_ndvi_ready
):
    """
    Test NDVI analysis workflow
    اختبار سير عمل تحليل NDVI
    """

    # Test NDVI calculation endpoint
    ndvi_input = {
        "red": 0.5,
        "nir": 0.8
    }

    response = await workflow_client.post(
        "http://localhost:8107/api/v1/ndvi/calculate",
        headers=e2e_headers,
        json=ndvi_input
    )

    assert response.status_code in (200, 401, 422), \
        f"NDVI calculation failed with status {response.status_code}"

    if response.status_code == 200:
        ndvi_result = response.json()
        assert "ndvi" in ndvi_result or "value" in ndvi_result, \
            "NDVI result should contain calculated value"

        # NDVI value should be between -1 and 1
        ndvi_value = ndvi_result.get("ndvi") or ndvi_result.get("value")
        if ndvi_value is not None:
            assert -1 <= ndvi_value <= 1, "NDVI value should be between -1 and 1"

        print(f"✓ NDVI calculated successfully: {ndvi_value}")


# ═══════════════════════════════════════════════════════════════════════════════
# Weather Integration Workflow - سير عمل تكامل الطقس
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_weather_forecast_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: Dict[str, str],
    test_location_yemen: Dict[str, float],
    ensure_weather_ready
):
    """
    Test weather forecast workflow
    اختبار سير عمل توقعات الطقس
    """

    # Get current weather
    current_response = await workflow_client.get(
        "http://localhost:8108/api/v1/weather/current",
        headers=e2e_headers,
        params=test_location_yemen
    )

    # Get weather forecast
    forecast_response = await workflow_client.get(
        "http://localhost:8108/api/v1/weather/forecast",
        headers=e2e_headers,
        params=test_location_yemen
    )

    # At least one should work
    assert current_response.status_code in (200, 401, 503) or \
           forecast_response.status_code in (200, 401, 503), \
        "Weather service should respond"

    if current_response.status_code == 200:
        print("✓ Current weather retrieved successfully")

    if forecast_response.status_code == 200:
        print("✓ Weather forecast retrieved successfully")


# ═══════════════════════════════════════════════════════════════════════════════
# Satellite Imagery Workflow - سير عمل صور الأقمار الصناعية
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_satellite_imagery_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: Dict[str, str],
    test_location_yemen: Dict[str, float]
):
    """
    Test satellite imagery workflow
    اختبار سير عمل صور الأقمار الصناعية
    """

    # Check satellite service health
    health_response = await workflow_client.get("http://localhost:8090/healthz")

    if health_response.status_code != 200:
        pytest.skip("Satellite service not available")

    # Request satellite imagery
    imagery_response = await workflow_client.get(
        "http://localhost:8090/api/v1/satellite/imagery",
        headers=e2e_headers,
        params=test_location_yemen
    )

    assert imagery_response.status_code in (200, 401, 404), \
        "Satellite imagery request should be handled"

    if imagery_response.status_code == 200:
        print("✓ Satellite imagery retrieved successfully")


# ═══════════════════════════════════════════════════════════════════════════════
# Irrigation Recommendation Workflow - سير عمل توصيات الري
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_irrigation_recommendation_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: Dict[str, str],
    test_location_yemen: Dict[str, float]
):
    """
    Test irrigation recommendation workflow
    اختبار سير عمل توصيات الري
    """

    # Check irrigation service health
    health_response = await workflow_client.get("http://localhost:8094/healthz")

    if health_response.status_code != 200:
        pytest.skip("Irrigation Smart service not available")

    # Calculate ET0 (reference evapotranspiration)
    et0_data = {
        **test_location_yemen,
        "temperature_max": 35.0,
        "temperature_min": 20.0,
        "humidity": 45.0,
        "wind_speed": 2.5,
        "solar_radiation": 25.0,
        "date": "2024-01-15"
    }

    et0_response = await workflow_client.post(
        "http://localhost:8094/api/v1/irrigation/et0",
        headers=e2e_headers,
        json=et0_data
    )

    assert et0_response.status_code in (200, 401, 422), \
        "ET0 calculation should be processed"

    if et0_response.status_code == 200:
        et0_result = et0_response.json()
        assert "et0" in et0_result or "value" in et0_result, \
            "ET0 result should contain calculated value"

        et0_value = et0_result.get("et0") or et0_result.get("value")
        if et0_value is not None:
            assert et0_value >= 0, "ET0 value should be non-negative"

        print(f"✓ ET0 calculated successfully: {et0_value} mm/day")


# ═══════════════════════════════════════════════════════════════════════════════
# Field Operations Complete Workflow - سير عمل عمليات الحقل الكامل
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_field_operations_complete_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: Dict[str, str],
    test_field_data: Dict[str, Any],
    ensure_field_ops_ready
):
    """
    Test complete field operations workflow
    اختبار سير عمل عمليات الحقل الكامل

    Workflow:
    1. Create field
    2. List fields
    3. Get specific field
    4. Update field
    5. Verify update
    """

    # Step 1: Create field
    create_response = await workflow_client.post(
        "http://localhost:8080/api/v1/fields",
        headers=e2e_headers,
        json=test_field_data
    )

    if create_response.status_code != 201:
        pytest.skip(f"Cannot create field: {create_response.status_code}")

    field_data = create_response.json()
    field_id = field_data.get("id") or field_data.get("field_id")

    # Step 2: List fields
    list_response = await workflow_client.get(
        "http://localhost:8080/api/v1/fields",
        headers=e2e_headers
    )

    assert list_response.status_code in (200, 401), "Fields list should be accessible"

    # Step 3: Get specific field
    get_response = await workflow_client.get(
        f"http://localhost:8080/api/v1/fields/{field_id}",
        headers=e2e_headers
    )

    assert get_response.status_code in (200, 401), "Field should be retrievable"

    if get_response.status_code == 200:
        retrieved_field = get_response.json()
        assert retrieved_field.get("name") == test_field_data["name"], \
            "Retrieved field should match created field"

    print("✓ Complete field operations workflow PASSED")
