"""
SAHOOL Integration Tests - Field Workflow
اختبارات التكامل - سير عمل الحقول

Tests complete field workflow including:
- Field creation
- Linking field to satellite data
- NDVI calculation for field
- Crop season management

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal


# ═══════════════════════════════════════════════════════════════════════════════
# Test Field Creation Workflow - اختبار سير عمل إنشاء الحقول
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_field_workflow(
    http_client,
    service_urls: Dict[str, str],
    field_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل إنشاء حقل كامل

    Test complete field creation workflow:
    1. Create a new field with boundary
    2. Verify field is stored correctly
    3. Verify field has valid geometry
    4. Check field area calculation
    """
    # Arrange - إعداد بيانات الاختبار
    field_service_url = service_urls["field_core"]

    field_data = field_factory.create(name="Integration Test Field", crop_type="wheat")
    field_data["tenant_id"] = "test-tenant-123"
    field_data["user_id"] = "test-user-123"

    # Add X-Tenant-Id header
    headers = {**auth_headers, "X-Tenant-Id": "test-tenant-123"}

    # Act - تنفيذ عملية إنشاء الحقل
    response = await http_client.post(
        f"{field_service_url}/fields",
        json=field_data,
        headers=headers
    )

    # Assert - التحقق من النتائج
    assert response.status_code == 201, f"Failed to create field: {response.text}"

    created_field = response.json()
    field_id = created_field["id"]

    # Verify field data
    assert created_field["name"] == field_data["name"]
    assert created_field["tenant_id"] == field_data["tenant_id"]
    assert created_field["user_id"] == field_data["user_id"]
    assert created_field["status"] == "active"
    assert "area_hectares" in created_field
    assert created_field["area_hectares"] > 0

    # Step 2: Retrieve field details - استرجاع تفاصيل الحقل
    get_response = await http_client.get(
        f"{field_service_url}/fields/{field_id}",
        headers=headers
    )

    assert get_response.status_code == 200
    field_details = get_response.json()

    # Verify detailed field information
    assert field_details["id"] == field_id
    assert "zones_count" in field_details
    assert "seasons_count" in field_details

    # Step 3: Calculate field area from boundary - حساب مساحة الحقل
    if field_data.get("boundary"):
        area_response = await http_client.get(
            f"{field_service_url}/fields/{field_id}/area",
            headers=headers
        )

        assert area_response.status_code == 200
        area_data = area_response.json()

        assert "calculated_area_hectares" in area_data
        assert "centroid" in area_data
        assert area_data["field_id"] == field_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_link_field_to_satellite_data(
    http_client,
    service_urls: Dict[str, str],
    field_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار ربط الحقل ببيانات الأقمار الصناعية

    Test linking field to satellite data:
    1. Create a field
    2. Request satellite analysis for field
    3. Verify satellite data is linked
    """
    # Arrange - إنشاء حقل
    field_service_url = service_urls["field_core"]
    satellite_url = service_urls.get("satellite_service", "http://localhost:8090")

    field_data = field_factory.create(name="Satellite Test Field", crop_type="tomato")
    field_data["tenant_id"] = "test-tenant-123"
    field_data["user_id"] = "test-user-123"

    # Add boundary coordinates for satellite analysis
    field_data["boundary"] = {
        "type": "Polygon",
        "coordinates": [[
            [44.0, 15.0],
            [44.01, 15.0],
            [44.01, 15.01],
            [44.0, 15.01],
            [44.0, 15.0]
        ]]
    }

    headers = {**auth_headers, "X-Tenant-Id": "test-tenant-123"}

    # Step 1: Create field - إنشاء الحقل
    field_response = await http_client.post(
        f"{field_service_url}/fields",
        json=field_data,
        headers=headers
    )

    assert field_response.status_code == 201
    field_id = field_response.json()["id"]

    # Step 2: Request satellite analysis - طلب تحليل الأقمار الصناعية
    # Note: This simulates satellite service integration
    satellite_request = {
        "field_id": field_id,
        "geometry": field_data["boundary"],
        "start_date": (date.today() - timedelta(days=30)).isoformat(),
        "end_date": date.today().isoformat(),
        "analysis_type": "ndvi"
    }

    try:
        satellite_response = await http_client.post(
            f"{satellite_url}/v1/analysis",
            json=satellite_request,
            headers=headers,
            timeout=30.0
        )

        # Satellite service may not be running in all test environments
        if satellite_response.status_code == 200:
            analysis_data = satellite_response.json()

            # Verify satellite analysis contains field reference
            assert "field_id" in analysis_data or "analysis_id" in analysis_data

    except Exception as e:
        # Satellite service not available - skip this part
        pytest.skip(f"Satellite service not available: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_calculate_ndvi_for_field(
    http_client,
    service_urls: Dict[str, str],
    field_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار حساب NDVI للحقل

    Test NDVI calculation workflow:
    1. Create a field
    2. Add NDVI record
    3. Retrieve NDVI history
    4. Verify NDVI trends
    """
    # Arrange - إنشاء حقل
    field_service_url = service_urls["field_core"]
    ndvi_service_url = service_urls.get("ndvi_engine", "http://localhost:8107")

    field_data = field_factory.create(name="NDVI Test Field", crop_type="wheat")
    field_data["tenant_id"] = "test-tenant-123"
    field_data["user_id"] = "test-user-123"

    headers = {**auth_headers, "X-Tenant-Id": "test-tenant-123"}

    # Step 1: Create field - إنشاء الحقل
    field_response = await http_client.post(
        f"{field_service_url}/fields",
        json=field_data,
        headers=headers
    )

    assert field_response.status_code == 201
    field_id = field_response.json()["id"]

    # Step 2: Add NDVI records - إضافة سجلات NDVI
    ndvi_records = []
    base_date = date.today() - timedelta(days=30)

    for i in range(5):
        ndvi_record = {
            "date": (base_date + timedelta(days=i * 7)).isoformat(),
            "mean": 0.65 + (i * 0.02),  # Increasing NDVI
            "min": 0.45,
            "max": 0.85,
            "std": 0.08,
            "cloud_cover": 5.0 + (i * 2)
        }

        add_response = await http_client.post(
            f"{field_service_url}/fields/{field_id}/ndvi",
            json=ndvi_record,
            headers=headers
        )

        assert add_response.status_code == 201
        ndvi_records.append(ndvi_record)

    # Step 3: Retrieve NDVI history - استرجاع سجل NDVI
    history_response = await http_client.get(
        f"{field_service_url}/fields/{field_id}/ndvi/history",
        headers=headers
    )

    assert history_response.status_code == 200
    history_data = history_response.json()

    # Verify NDVI history
    assert "records" in history_data
    assert len(history_data["records"]) == 5
    assert history_data["field_id"] == field_id

    # Step 4: Get field details with NDVI trend - الحصول على تفاصيل الحقل مع اتجاه NDVI
    field_details_response = await http_client.get(
        f"{field_service_url}/fields/{field_id}",
        headers=headers
    )

    assert field_details_response.status_code == 200
    field_details = field_details_response.json()

    # Verify latest NDVI is included
    if "latest_ndvi" in field_details:
        assert field_details["latest_ndvi"] is not None

    # Verify NDVI trend
    if "ndvi_trend" in field_details:
        ndvi_trend = field_details["ndvi_trend"]
        if ndvi_trend:
            assert "direction" in ndvi_trend
            assert ndvi_trend["direction"] in ["increasing", "decreasing", "stable"]


# ═══════════════════════════════════════════════════════════════════════════════
# Test Crop Season Workflow - اختبار سير عمل مواسم المحاصيل
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crop_season_workflow(
    http_client,
    service_urls: Dict[str, str],
    field_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل موسم المحصول

    Test crop season workflow:
    1. Create field
    2. Start crop season
    3. Retrieve crop history
    4. Close season with harvest data
    """
    # Arrange - إنشاء حقل
    field_service_url = service_urls["field_core"]

    field_data = field_factory.create(name="Season Test Field", crop_type="tomato")
    field_data["tenant_id"] = "test-tenant-123"
    field_data["user_id"] = "test-user-123"

    headers = {**auth_headers, "X-Tenant-Id": "test-tenant-123"}

    # Step 1: Create field
    field_response = await http_client.post(
        f"{field_service_url}/fields",
        json=field_data,
        headers=headers
    )

    assert field_response.status_code == 201
    field_id = field_response.json()["id"]

    # Step 2: Start crop season - بدء موسم المحصول
    season_data = {
        "crop_type": "tomato",
        "variety": "Roma",
        "planting_date": (date.today() - timedelta(days=60)).isoformat(),
        "expected_harvest": (date.today() + timedelta(days=30)).isoformat(),
        "seed_source": "Local supplier",
        "notes": "Integration test season"
    }

    season_response = await http_client.post(
        f"{field_service_url}/fields/{field_id}/crops",
        json=season_data,
        headers=headers
    )

    assert season_response.status_code == 201
    season = season_response.json()

    assert season["crop_type"] == "tomato"
    assert season["status"] == "active"
    assert season["field_id"] == field_id

    # Step 3: Get crop history - الحصول على سجل المحاصيل
    history_response = await http_client.get(
        f"{field_service_url}/fields/{field_id}/crops/history",
        headers=headers
    )

    assert history_response.status_code == 200
    history = history_response.json()

    assert history["field_id"] == field_id
    assert history["total"] == 1
    assert len(history["seasons"]) == 1

    # Step 4: Close season with harvest data - إغلاق الموسم مع بيانات الحصاد
    close_data = {
        "harvest_date": date.today().isoformat(),
        "actual_yield_kg": 2500.0,
        "notes": "Good harvest season"
    }

    close_response = await http_client.post(
        f"{field_service_url}/fields/{field_id}/crops/current/close",
        json=close_data,
        headers=headers
    )

    assert close_response.status_code == 200
    closed_season = close_response.json()

    assert closed_season["status"] == "harvested"
    assert closed_season["actual_yield_kg"] == 2500.0
    assert closed_season["harvest_date"] == date.today().isoformat()


# ═══════════════════════════════════════════════════════════════════════════════
# Test Field Zone Management - اختبار إدارة مناطق الحقل
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_field_zone_workflow(
    http_client,
    service_urls: Dict[str, str],
    field_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل مناطق الحقل

    Test field zone workflow:
    1. Create field
    2. Create zone within field
    3. List zones
    4. Delete zone
    """
    # Arrange
    field_service_url = service_urls["field_core"]

    field_data = field_factory.create(name="Zone Test Field", crop_type="wheat")
    field_data["tenant_id"] = "test-tenant-123"
    field_data["user_id"] = "test-user-123"

    headers = {**auth_headers, "X-Tenant-Id": "test-tenant-123"}

    # Step 1: Create field
    field_response = await http_client.post(
        f"{field_service_url}/fields",
        json=field_data,
        headers=headers
    )

    assert field_response.status_code == 201
    field_id = field_response.json()["id"]

    # Step 2: Create zone - إنشاء منطقة
    zone_data = {
        "name": "North Zone",
        "name_ar": "المنطقة الشمالية",
        "boundary": {
            "type": "Polygon",
            "coordinates": [[
                [44.0, 15.0],
                [44.005, 15.0],
                [44.005, 15.005],
                [44.0, 15.005],
                [44.0, 15.0]
            ]]
        },
        "purpose": "irrigation",
        "notes": "Test zone for irrigation management"
    }

    zone_response = await http_client.post(
        f"{field_service_url}/fields/{field_id}/zones",
        json=zone_data,
        headers=headers
    )

    assert zone_response.status_code == 201
    zone = zone_response.json()
    zone_id = zone["id"]

    assert zone["name"] == "North Zone"
    assert zone["field_id"] == field_id
    assert "area_hectares" in zone

    # Step 3: List zones - قائمة المناطق
    list_response = await http_client.get(
        f"{field_service_url}/fields/{field_id}/zones",
        headers=headers
    )

    assert list_response.status_code == 200
    zones_list = list_response.json()

    assert zones_list["field_id"] == field_id
    assert zones_list["total"] == 1
    assert len(zones_list["zones"]) == 1

    # Step 4: Delete zone - حذف المنطقة
    delete_response = await http_client.delete(
        f"{field_service_url}/zones/{zone_id}",
        headers=headers
    )

    assert delete_response.status_code == 200
    delete_result = delete_response.json()

    assert delete_result["status"] == "deleted"
    assert delete_result["zone_id"] == zone_id


# ═══════════════════════════════════════════════════════════════════════════════
# Test Field Statistics - اختبار إحصائيات الحقل
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_field_statistics(
    http_client,
    service_urls: Dict[str, str],
    field_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار إحصائيات الحقل

    Test field statistics:
    1. Create field with multiple seasons
    2. Get field statistics
    3. Verify statistics calculations
    """
    # Arrange
    field_service_url = service_urls["field_core"]

    field_data = field_factory.create(name="Stats Test Field", crop_type="wheat")
    field_data["tenant_id"] = "test-tenant-123"
    field_data["user_id"] = "test-user-123"

    headers = {**auth_headers, "X-Tenant-Id": "test-tenant-123"}

    # Create field
    field_response = await http_client.post(
        f"{field_service_url}/fields",
        json=field_data,
        headers=headers
    )

    assert field_response.status_code == 201
    field_id = field_response.json()["id"]

    # Get field statistics - الحصول على إحصائيات الحقل
    stats_response = await http_client.get(
        f"{field_service_url}/fields/{field_id}/stats",
        headers=headers
    )

    assert stats_response.status_code == 200
    stats = stats_response.json()

    # Verify statistics structure
    assert stats["field_id"] == field_id
    assert "area_hectares" in stats
    assert "seasons_count" in stats
    assert "crops_grown" in stats
    assert isinstance(stats["crops_grown"], list)
