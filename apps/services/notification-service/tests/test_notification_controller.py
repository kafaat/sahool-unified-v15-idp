"""
SAHOOL Notification Service - Controller Tests
Comprehensive tests for notification API endpoints
Coverage: REST endpoints, validation, error handling, authentication
"""

from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


@pytest.fixture
def mock_notification_data():
    """Mock notification data for testing"""
    return {
        "id": str(uuid4()),
        "type": "weather_alert",
        "type_ar": "تنبيه طقس",
        "priority": "high",
        "priority_ar": "عالية",
        "title": "Weather Alert",
        "title_ar": "تنبيه طقس",
        "body": "Frost expected tonight",
        "body_ar": "صقيع متوقع الليلة",
        "data": {"temperature": -2},
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "status": "sent",
    }


@pytest.fixture
def mock_farmer_profile():
    """Mock farmer profile"""
    return {
        "farmer_id": "farmer-123",
        "name": "Ahmed Ali",
        "name_ar": "أحمد علي",
        "governorate": "sanaa",
        "crops": ["tomato", "coffee"],
        "phone": "+967771234567",
        "email": "ahmed@example.com",
        "fcm_token": "mock-fcm-token",
    }


class TestHealthEndpoint:
    """Test health check endpoint"""

    @pytest.mark.asyncio
    async def test_health_check_success(self, async_client):
        """Test health check returns healthy status"""
        with (
            patch(
                "src.main.check_db_health",
                new=AsyncMock(return_value={"status": "healthy", "connected": True}),
            ),
            patch(
                "src.main.get_db_stats",
                new=AsyncMock(
                    return_value={"total_notifications": 100, "pending_notifications": 5}
                ),
            ),
        ):
            response = await async_client.get("/healthz")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded"]
            assert "service" in data
            assert data["service"] == "notification-service"

    @pytest.mark.asyncio
    async def test_health_check_with_db_error(self, async_client):
        """Test health check when database is unavailable"""
        with patch(
            "src.main.check_db_health",
            new=AsyncMock(return_value={"connected": False, "error": "Connection refused"}),
        ):
            response = await async_client.get("/healthz")

            assert response.status_code == 200
            data = response.json()
            assert data["mode"] == "degraded"


class TestNotificationCreation:
    """Test notification creation endpoints"""

    @pytest.mark.asyncio
    async def test_create_custom_notification(self, async_client, mock_notification_data):
        """Test creating a custom notification"""
        notification_request = {
            "type": "weather_alert",
            "priority": "high",
            "title": "Weather Alert",
            "title_ar": "تنبيه طقس",
            "body": "Frost expected tonight",
            "body_ar": "صقيع متوقع الليلة",
            "data": {"temperature": -2},
            "target_farmers": ["farmer-123"],
            "channels": ["push", "in_app"],
            "expires_in_hours": 24,
        }

        with patch(
            "src.main.create_notification",
            new=AsyncMock(return_value=MagicMock(**mock_notification_data)),
        ):
            response = await async_client.post("/v1/notifications", json=notification_request)

            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["type"] == "weather_alert"
            assert data["title"] == "Weather Alert"

    @pytest.mark.asyncio
    async def test_create_notification_validation_error(self, async_client):
        """Test notification creation with invalid data"""
        invalid_request = {
            "type": "invalid_type",  # Invalid type
            "title": "Test",
            "body": "Test body",
        }

        response = await async_client.post("/v1/notifications", json=invalid_request)

        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_weather_alert(self, async_client, mock_notification_data):
        """Test creating a weather alert"""
        weather_alert_request = {
            "governorates": ["sanaa", "ibb"],
            "alert_type": "frost",
            "severity": "high",
            "expected_date": (date.today() + timedelta(days=1)).isoformat(),
            "details": {"min_temperature": -2, "duration_hours": 6},
        }

        with patch(
            "src.main.create_notification",
            new=AsyncMock(return_value=MagicMock(**mock_notification_data)),
        ):
            response = await async_client.post("/v1/alerts/weather", json=weather_alert_request)

            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["type"] == "weather_alert"

    @pytest.mark.asyncio
    async def test_create_pest_alert(self, async_client, mock_notification_data):
        """Test creating a pest outbreak alert"""
        pest_alert_request = {
            "governorate": "taiz",
            "pest_name": "Aphids",
            "pest_name_ar": "المن",
            "affected_crops": ["tomato", "potato"],
            "severity": "medium",
            "recommendations": ["Use organic pesticides", "Remove infected plants"],
            "recommendations_ar": ["استخدم المبيدات العضوية", "أزل النباتات المصابة"],
        }

        with patch(
            "src.main.create_notification",
            new=AsyncMock(return_value=MagicMock(**mock_notification_data)),
        ):
            response = await async_client.post("/v1/alerts/pest", json=pest_alert_request)

            assert response.status_code == 200
            data = response.json()
            assert "id" in data

    @pytest.mark.asyncio
    async def test_create_irrigation_reminder(self, async_client, mock_notification_data):
        """Test creating an irrigation reminder"""
        irrigation_request = {
            "farmer_id": "farmer-123",
            "field_id": "field-456",
            "field_name": "North Field",
            "crop": "tomato",
            "water_needed_mm": 25.5,
            "urgency": "high",
        }

        with patch(
            "src.main.create_notification",
            new=AsyncMock(return_value=MagicMock(**mock_notification_data)),
        ):
            response = await async_client.post("/v1/reminders/irrigation", json=irrigation_request)

            assert response.status_code == 200
            data = response.json()
            assert "id" in data


class TestNotificationRetrieval:
    """Test notification retrieval endpoints"""

    @pytest.mark.asyncio
    async def test_get_farmer_notifications(self, async_client, mock_notification_data):
        """Test getting notifications for a specific farmer"""
        mock_notification = MagicMock(**mock_notification_data)

        with (
            patch(
                "src.repository.NotificationRepository.get_by_user",
                new=AsyncMock(return_value=[mock_notification]),
            ),
            patch(
                "src.repository.NotificationRepository.get_unread_count",
                new=AsyncMock(return_value=1),
            ),
        ):
            response = await async_client.get("/v1/notifications/farmer/farmer-123")

            assert response.status_code == 200
            data = response.json()
            assert "notifications" in data
            assert data["farmer_id"] == "farmer-123"
            assert data["total"] >= 0
            assert "unread_count" in data

    @pytest.mark.asyncio
    async def test_get_farmer_notifications_with_filters(
        self, async_client, mock_notification_data
    ):
        """Test getting notifications with filters"""
        mock_notification = MagicMock(**mock_notification_data)

        with (
            patch(
                "src.repository.NotificationRepository.get_by_user",
                new=AsyncMock(return_value=[mock_notification]),
            ),
            patch(
                "src.repository.NotificationRepository.get_unread_count",
                new=AsyncMock(return_value=1),
            ),
        ):
            response = await async_client.get(
                "/v1/notifications/farmer/farmer-123",
                params={"unread_only": True, "type": "weather_alert", "limit": 10, "offset": 0},
            )

            assert response.status_code == 200
            data = response.json()
            assert "notifications" in data

    @pytest.mark.asyncio
    async def test_get_broadcast_notifications(self, async_client, mock_notification_data):
        """Test getting broadcast notifications"""
        mock_notification = MagicMock(**mock_notification_data)

        with patch(
            "src.repository.NotificationRepository.get_broadcast_notifications",
            new=AsyncMock(return_value=[mock_notification]),
        ):
            response = await async_client.get("/v1/notifications/broadcast")

            assert response.status_code == 200
            data = response.json()
            assert "notifications" in data
            assert "total" in data

    @pytest.mark.asyncio
    async def test_get_broadcast_notifications_with_filters(self, async_client):
        """Test getting broadcast notifications with governorate and crop filters"""
        with patch(
            "src.repository.NotificationRepository.get_broadcast_notifications",
            new=AsyncMock(return_value=[]),
        ):
            response = await async_client.get(
                "/v1/notifications/broadcast",
                params={"governorate": "sanaa", "crop": "tomato", "limit": 20},
            )

            assert response.status_code == 200


class TestNotificationUpdates:
    """Test notification update endpoints"""

    @pytest.mark.asyncio
    async def test_mark_notification_as_read(self, async_client, mock_notification_data):
        """Test marking a notification as read"""
        notification_id = str(uuid4())
        mock_notification = MagicMock(**mock_notification_data)
        mock_notification.user_id = "farmer-123"

        with (
            patch(
                "src.repository.NotificationRepository.get_by_id",
                new=AsyncMock(return_value=mock_notification),
            ),
            patch(
                "src.repository.NotificationRepository.mark_as_read",
                new=AsyncMock(return_value=True),
            ),
        ):
            response = await async_client.patch(
                f"/v1/notifications/{notification_id}/read", params={"farmer_id": "farmer-123"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["is_read"] is True

    @pytest.mark.asyncio
    async def test_mark_notification_unauthorized(self, async_client):
        """Test marking notification as read with wrong farmer_id"""
        notification_id = str(uuid4())
        mock_notification = MagicMock()
        mock_notification.user_id = "farmer-123"

        with patch(
            "src.repository.NotificationRepository.get_by_id",
            new=AsyncMock(return_value=mock_notification),
        ):
            response = await async_client.patch(
                f"/v1/notifications/{notification_id}/read", params={"farmer_id": "wrong-farmer"}
            )

            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_mark_notification_not_found(self, async_client):
        """Test marking non-existent notification as read"""
        notification_id = str(uuid4())

        with patch(
            "src.repository.NotificationRepository.get_by_id", new=AsyncMock(return_value=None)
        ):
            response = await async_client.patch(
                f"/v1/notifications/{notification_id}/read", params={"farmer_id": "farmer-123"}
            )

            assert response.status_code == 404


class TestFarmerRegistration:
    """Test farmer registration endpoints"""

    @pytest.mark.asyncio
    async def test_register_farmer(self, async_client, mock_farmer_profile):
        """Test registering a new farmer"""
        response = await async_client.post("/v1/farmers/register", json=mock_farmer_profile)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["farmer_id"] == mock_farmer_profile["farmer_id"]

    @pytest.mark.asyncio
    async def test_update_notification_preferences(self, async_client):
        """Test updating notification preferences"""
        preferences = {
            "farmer_id": "farmer-123",
            "weather_alerts": True,
            "pest_alerts": True,
            "irrigation_reminders": True,
            "crop_health_alerts": False,
            "market_prices": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "06:00",
            "min_priority": "medium",
        }

        with patch(
            "src.repository.NotificationPreferenceRepository.create_or_update",
            new=AsyncMock(return_value=MagicMock()),
        ):
            response = await async_client.put(
                "/v1/farmers/farmer-123/preferences", json=preferences
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestNotificationStats:
    """Test notification statistics endpoints"""

    @pytest.mark.asyncio
    async def test_get_notification_stats(self, async_client):
        """Test getting notification statistics"""
        mock_stats = {
            "total_notifications": 500,
            "pending_notifications": 10,
            "total_templates": 15,
            "total_preferences": 200,
        }

        with patch("src.main.get_db_stats", new=AsyncMock(return_value=mock_stats)):
            with patch("src.models.Notification.filter") as mock_filter:
                mock_filter.return_value.count = AsyncMock(return_value=50)

                response = await async_client.get("/v1/stats")

                assert response.status_code == 200
                data = response.json()
                assert "total_notifications" in data
                assert "registered_farmers" in data


# Pytest fixtures for test client


@pytest.fixture
async def async_client():
    """Create async test client"""
    from src.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def client():
    """Create sync test client"""
    from src.main import app

    return TestClient(app)
