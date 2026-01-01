"""
Integration Tests for SAHOOL Starter Package
اختبارات التكامل لحزمة سهول المبتدئة

Tests for starter package services:
- Field Core: CRUD operations for fields - عمليات الحقول
- Weather Core: Weather forecast retrieval - توقعات الطقس
- Astronomical Calendar: Agricultural calendar - التقويم الزراعي
- Agro Advisor: Recommendations - توصيات زراعية
- Notifications: Alerts and messages - الإشعارات

Author: SAHOOL Platform Team
"""

import pytest
import httpx
from typing import Dict, Any


# ═══════════════════════════════════════════════════════════════════════════════
# Field Core CRUD Operations - عمليات الحقول
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestFieldOperations:
    """Test field CRUD operations - اختبار عمليات الحقول"""

    async def test_create_field(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        field_factory,
        auth_headers: Dict[str, str],
    ):
        """
        Test creating a new field
        اختبار إنشاء حقل جديد
        """
        # Arrange - التحضير
        field_data = field_factory.create(name="Test Wheat Field", crop_type="wheat")
        url = f"{service_urls['field_core']}/api/v1/fields"

        # Act - التنفيذ
        response = await http_client.post(url, json=field_data, headers=auth_headers)

        # Assert - التحقق
        assert response.status_code in (
            200,
            201,
        ), f"Failed to create field: {response.text}"
        data = response.json()
        assert data.get("name") == field_data["name"]
        assert data.get("crop_type") == field_data["crop_type"]
        assert "id" in data or "field_id" in data

    async def test_get_field_by_id(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        field_factory,
        auth_headers: Dict[str, str],
    ):
        """
        Test retrieving a field by ID
        اختبار استرجاع حقل بالمعرف
        """
        # Arrange - Create a field first
        field_data = field_factory.create()
        create_url = f"{service_urls['field_core']}/api/v1/fields"
        create_response = await http_client.post(
            create_url, json=field_data, headers=auth_headers
        )

        if create_response.status_code not in (200, 201):
            pytest.skip("Field creation failed, skipping get test")

        created_field = create_response.json()
        field_id = created_field.get("id") or created_field.get("field_id")

        # Act - Retrieve the field
        get_url = f"{service_urls['field_core']}/api/v1/fields/{field_id}"
        response = await http_client.get(get_url, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to get field: {response.text}"
        data = response.json()
        assert (data.get("id") or data.get("field_id")) == field_id

    async def test_update_field(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        field_factory,
        auth_headers: Dict[str, str],
    ):
        """
        Test updating a field
        اختبار تحديث حقل
        """
        # Arrange - Create a field first
        field_data = field_factory.create()
        create_url = f"{service_urls['field_core']}/api/v1/fields"
        create_response = await http_client.post(
            create_url, json=field_data, headers=auth_headers
        )

        if create_response.status_code not in (200, 201):
            pytest.skip("Field creation failed, skipping update test")

        created_field = create_response.json()
        field_id = created_field.get("id") or created_field.get("field_id")

        # Act - Update the field
        update_data = {"crop_type": "corn", "area_hectares": 50.0}
        update_url = f"{service_urls['field_core']}/api/v1/fields/{field_id}"
        response = await http_client.put(
            update_url, json=update_data, headers=auth_headers
        )

        # Assert
        assert response.status_code in (
            200,
            204,
        ), f"Failed to update field: {response.text}"

    async def test_list_fields(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        auth_headers: Dict[str, str],
    ):
        """
        Test listing all fields
        اختبار عرض جميع الحقول
        """
        # Act
        url = f"{service_urls['field_core']}/api/v1/fields"
        response = await http_client.get(url, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to list fields: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))  # Could be list or paginated response


# ═══════════════════════════════════════════════════════════════════════════════
# Weather Forecast Tests - اختبارات توقعات الطقس
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestWeatherForecast:
    """Test weather forecast retrieval - اختبار استرجاع توقعات الطقس"""

    async def test_get_current_weather(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        weather_factory,
        auth_headers: Dict[str, str],
    ):
        """
        Test getting current weather for location
        اختبار الحصول على الطقس الحالي للموقع
        """
        # Arrange
        location = weather_factory.create(latitude=15.3694, longitude=44.1910)
        url = f"{service_urls['weather_core']}/api/v1/weather/current"

        # Act
        response = await http_client.get(url, params=location, headers=auth_headers)

        # Assert
        assert (
            response.status_code == 200
        ), f"Failed to get current weather: {response.text}"
        data = response.json()
        assert "temperature" in data or "temp" in data
        assert "humidity" in data

    async def test_get_weather_forecast(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        weather_factory,
        auth_headers: Dict[str, str],
    ):
        """
        Test getting weather forecast for multiple days
        اختبار الحصول على توقعات الطقس لعدة أيام
        """
        # Arrange
        location = weather_factory.create(latitude=15.3694, longitude=44.1910)
        url = f"{service_urls['weather_core']}/api/v1/weather/forecast"

        # Act
        response = await http_client.get(url, params=location, headers=auth_headers)

        # Assert
        assert response.status_code == 200, f"Failed to get forecast: {response.text}"
        data = response.json()
        assert "forecast" in data or isinstance(data, list)


# ═══════════════════════════════════════════════════════════════════════════════
# Astronomical Calendar Tests - اختبارات التقويم الفلكي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestAstronomicalCalendar:
    """Test astronomical calendar - اختبار التقويم الفلكي"""

    async def test_get_lunar_phase(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        auth_headers: Dict[str, str],
    ):
        """
        Test getting lunar phase information
        اختبار الحصول على معلومات القمر
        """
        # Arrange
        url = f"{service_urls['astronomical_calendar']}/api/v1/lunar/phase"

        # Act
        response = await http_client.get(url, headers=auth_headers)

        # Assert
        assert (
            response.status_code == 200
        ), f"Failed to get lunar phase: {response.text}"
        data = response.json()
        assert "phase" in data or "moon_phase" in data

    async def test_get_planting_calendar(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        auth_headers: Dict[str, str],
    ):
        """
        Test getting agricultural planting calendar
        اختبار الحصول على تقويم الزراعة
        """
        # Arrange
        url = f"{service_urls['astronomical_calendar']}/api/v1/calendar/planting"
        params = {"latitude": 15.3694, "longitude": 44.1910}

        # Act
        response = await http_client.get(url, params=params, headers=auth_headers)

        # Assert
        assert (
            response.status_code == 200
        ), f"Failed to get planting calendar: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))


# ═══════════════════════════════════════════════════════════════════════════════
# Agro Advisor Tests - اختبارات المستشار الزراعي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestAgroAdvisor:
    """Test agro advisor recommendations - اختبار توصيات المستشار الزراعي"""

    async def test_get_crop_recommendation(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        auth_headers: Dict[str, str],
    ):
        """
        Test getting crop recommendations
        اختبار الحصول على توصيات المحاصيل
        """
        # Arrange
        url = f"{service_urls['agro_advisor']}/api/v1/recommendations/crop"
        query = {"soil_type": "loamy", "climate": "arid", "season": "spring"}

        # Act
        response = await http_client.post(url, json=query, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to get crop recommendations: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))

    async def test_get_fertilizer_recommendation(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        auth_headers: Dict[str, str],
    ):
        """
        Test getting fertilizer recommendations
        اختبار الحصول على توصيات التسميد
        """
        # Arrange
        url = f"{service_urls['agro_advisor']}/api/v1/recommendations/fertilizer"
        query = {
            "crop_type": "wheat",
            "soil_nutrients": {
                "nitrogen": "low",
                "phosphorus": "medium",
                "potassium": "high",
            },
        }

        # Act
        response = await http_client.post(url, json=query, headers=auth_headers)

        # Assert
        assert response.status_code in (
            200,
            201,
        ), f"Failed to get fertilizer recommendations: {response.text}"


# ═══════════════════════════════════════════════════════════════════════════════
# Notification Tests - اختبارات الإشعارات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestNotifications:
    """Test notification service - اختبار خدمة الإشعارات"""

    async def test_send_notification(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        notification_factory,
        auth_headers: Dict[str, str],
    ):
        """
        Test sending a notification
        اختبار إرسال إشعار
        """
        # Arrange
        notification_data = notification_factory.create(
            user_id="test-user-123", notification_type="weather_alert"
        )
        url = f"{service_urls['notification_service']}/api/v1/notifications"

        # Act
        response = await http_client.post(
            url, json=notification_data, headers=auth_headers
        )

        # Assert
        assert response.status_code in (
            200,
            201,
            202,
        ), f"Failed to send notification: {response.text}"
        data = response.json()
        assert "id" in data or "notification_id" in data or "status" in data

    async def test_get_user_notifications(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        auth_headers: Dict[str, str],
    ):
        """
        Test retrieving user notifications
        اختبار استرجاع إشعارات المستخدم
        """
        # Arrange
        user_id = "test-user-123"
        url = f"{service_urls['notification_service']}/api/v1/notifications/user/{user_id}"

        # Act
        response = await http_client.get(url, headers=auth_headers)

        # Assert
        assert (
            response.status_code == 200
        ), f"Failed to get notifications: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))


# ═══════════════════════════════════════════════════════════════════════════════
# Service Health Tests - اختبارات صحة الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestStarterPackageHealth:
    """Test health endpoints of starter package services - اختبار نقاط صحة خدمات الحزمة المبتدئة"""

    @pytest.mark.parametrize(
        "service_name",
        [
            "field_core",
            "weather_core",
            "astronomical_calendar",
            "agro_advisor",
            "notification_service",
        ],
    )
    async def test_service_health(
        self,
        http_client: httpx.AsyncClient,
        service_urls: Dict[str, str],
        service_name: str,
    ):
        """
        Test service health endpoint
        اختبار نقطة صحة الخدمة
        """
        # Arrange
        base_url = service_urls.get(service_name)
        if not base_url:
            pytest.skip(f"Service {service_name} not configured")

        url = f"{base_url}/healthz"

        # Act
        response = await http_client.get(url, timeout=10)

        # Assert
        assert response.status_code in (
            200,
            204,
        ), f"Service {service_name} is not healthy: {response.text}"
