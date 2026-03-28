"""
SAHOOL Notification Service - Controller Tests
Comprehensive tests for notification API endpoints
Coverage: REST endpoints, validation, error handling, authentication
"""

import asyncio
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

try:
    from fastapi.testclient import TestClient
except BaseException:
    pytest.skip("fastapi not installed", allow_module_level=True)


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
        "data": {"temperature": -2, "type_ar": "تنبيه طقس", "priority_ar": "عالية"},
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

    def test_health_check_success(self, client):
        """Test health check returns healthy status"""
        response = client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "healthy", "degraded"]
        assert "service" in data
        assert data["service"] == "notification-service"

    def test_readiness_check_with_db_error(self, client):
        """Test readiness check when database is unavailable"""
        with (
            patch(
                "src.main.check_db_health",
                new=AsyncMock(return_value={"connected": False, "error": "Connection refused"}),
            ),
            patch(
                "src.repository.FarmerProfileRepository.get_count",
                new=AsyncMock(return_value=0),
            ),
        ):
            response = client.get("/readyz")

            assert response.status_code in (200, 503)
            data = response.json()
            assert data["status"] in ("degraded", "ready")


class TestNotificationCreation:
    """Test notification creation endpoints"""

    def test_create_custom_notification(self, client, mock_notification_data):
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

        mock_notif = MagicMock(**mock_notification_data)

        with patch(
            "src.main.create_notification",
            new=AsyncMock(return_value=mock_notif),
        ):
            response = client.post("/", json=notification_request)

            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["type"] == "weather_alert"
            assert data["title"] == "Weather Alert"

    def test_create_notification_validation_error(self, client):
        """Test notification creation with invalid data"""
        invalid_request = {
            "type": "invalid_type",
            "title": "Test",
            "body": "Test body",
        }

        response = client.post("/", json=invalid_request)

        assert response.status_code == 422

    def test_create_weather_alert(self, client, mock_notification_data):
        """Test creating a weather alert"""
        weather_alert_request = {
            "governorates": ["sanaa", "ibb"],
            "alert_type": "frost",
            "severity": "high",
            "expected_date": (date.today() + timedelta(days=1)).isoformat(),
            "details": {"min_temperature": -2, "duration_hours": 6},
        }

        mock_notif = MagicMock(**mock_notification_data)

        with patch(
            "src.main.create_notification",
            new=AsyncMock(return_value=mock_notif),
        ):
            response = client.post("/weather", json=weather_alert_request)

            assert response.status_code == 200
            data = response.json()
            assert "id" in data

    def test_create_pest_alert(self, client, mock_notification_data):
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

        mock_notif = MagicMock(**mock_notification_data)

        with patch(
            "src.main.create_notification",
            new=AsyncMock(return_value=mock_notif),
        ):
            response = client.post("/pest", json=pest_alert_request)

            assert response.status_code == 200
            data = response.json()
            assert "id" in data

    def test_create_irrigation_reminder(self, client, mock_notification_data):
        """Test creating an irrigation reminder"""
        irrigation_request = {
            "farmer_id": "farmer-123",
            "field_id": "field-456",
            "field_name": "North Field",
            "crop": "tomato",
            "water_needed_mm": 25.5,
            "urgency": "high",
        }

        mock_notif = MagicMock(**mock_notification_data)

        with patch(
            "src.main.create_notification",
            new=AsyncMock(return_value=mock_notif),
        ):
            response = client.post("/irrigation", json=irrigation_request)

            assert response.status_code == 200
            data = response.json()
            assert "id" in data


class TestNotificationRetrieval:
    """Test notification retrieval endpoints"""

    def test_get_farmer_notifications(self, client, mock_notification_data):
        """Test getting notifications for a specific farmer"""
        mock_notification = MagicMock(**mock_notification_data)
        mock_notification.is_read = False
        mock_notification.action_url = None

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
            response = client.get("/farmer/farmer-123")

            assert response.status_code == 200
            data = response.json()
            assert "notifications" in data
            assert data["farmer_id"] == "farmer-123"
            assert data["total"] >= 0
            assert "unread_count" in data

    def test_get_farmer_notifications_with_filters(self, client, mock_notification_data):
        """Test getting notifications with filters"""
        mock_notification = MagicMock(**mock_notification_data)
        mock_notification.is_read = False
        mock_notification.action_url = None

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
            response = client.get(
                "/farmer/farmer-123",
                params={"unread_only": True, "type": "weather_alert", "limit": 10, "offset": 0},
            )

            assert response.status_code == 200
            data = response.json()
            assert "notifications" in data

    def test_get_broadcast_notifications(self, client, mock_notification_data):
        """Test getting broadcast notifications"""
        mock_notification = MagicMock(**mock_notification_data)
        mock_notification.target_governorates = ["sanaa"]
        mock_notification.target_crops = ["tomato"]

        with patch(
            "src.repository.NotificationRepository.get_broadcast_notifications",
            new=AsyncMock(return_value=[mock_notification]),
        ):
            response = client.get("/broadcast")

            assert response.status_code == 200
            data = response.json()
            assert "notifications" in data
            assert "total" in data

    def test_get_broadcast_notifications_with_filters(self, client):
        """Test getting broadcast notifications with governorate and crop filters"""
        with patch(
            "src.repository.NotificationRepository.get_broadcast_notifications",
            new=AsyncMock(return_value=[]),
        ):
            response = client.get(
                "/broadcast",
                params={"governorate": "sanaa", "crop": "tomato", "limit": 20},
            )

            assert response.status_code == 200


class TestNotificationUpdates:
    """Test notification update endpoints"""

    def test_mark_notification_as_read(self, client):
        """Test marking a notification as read"""
        notification_id = str(uuid4())
        mock_notification = MagicMock()
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
            response = client.patch(f"/{notification_id}/read", params={"farmer_id": "farmer-123"})

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["is_read"] is True

    def test_mark_notification_unauthorized(self, client):
        """Test marking notification as read with wrong farmer_id"""
        notification_id = str(uuid4())
        mock_notification = MagicMock()
        mock_notification.user_id = "farmer-123"

        with patch(
            "src.repository.NotificationRepository.get_by_id",
            new=AsyncMock(return_value=mock_notification),
        ):
            response = client.patch(f"/{notification_id}/read", params={"farmer_id": "wrong-farmer"})

            assert response.status_code == 403

    def test_mark_notification_not_found(self, client):
        """Test marking non-existent notification as read"""
        notification_id = str(uuid4())

        with patch("src.repository.NotificationRepository.get_by_id", new=AsyncMock(return_value=None)):
            response = client.patch(f"/{notification_id}/read", params={"farmer_id": "farmer-123"})

            assert response.status_code == 404


class TestFarmerRegistration:
    """Test farmer registration endpoints"""

    def test_register_farmer(self, client, mock_farmer_profile):
        """Test registering a new farmer"""
        with patch(
            "src.repository.FarmerProfileRepository.create",
            new=AsyncMock(return_value=MagicMock()),
        ):
            response = client.post("/register", json=mock_farmer_profile)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["farmer_id"] == mock_farmer_profile["farmer_id"]

    def test_update_notification_preferences(self, client):
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
            response = client.put("/farmer-123/preferences", json=preferences)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestNotificationStats:
    """Test notification statistics endpoints"""

    def test_get_notification_stats(self, client):
        """Test getting notification statistics"""
        mock_stats = {
            "total_notifications": 500,
            "pending_notifications": 10,
            "total_templates": 15,
            "total_preferences": 200,
        }

        with (
            patch("src.main.get_db_stats", new=AsyncMock(return_value=mock_stats)),
            patch("src.models.Notification.filter") as mock_filter,
            patch(
                "src.repository.FarmerProfileRepository.get_count",
                new=AsyncMock(return_value=50),
            ),
        ):
            mock_filter.return_value.count = AsyncMock(return_value=50)

            response = client.get("/stats")

            assert response.status_code == 200
            data = response.json()
            assert "total_notifications" in data
            assert "registered_farmers" in data
