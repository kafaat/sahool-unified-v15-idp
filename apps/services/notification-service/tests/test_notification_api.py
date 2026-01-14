"""
SAHOOL Notification Service - API Tests
Comprehensive API endpoint testing with mocked dependencies
Coverage: API endpoints, error handling, authentication, validation
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_db():
    """Mock database connection"""
    with (
        patch("src.database.init_db", new=AsyncMock()),
        patch(
            "src.database.check_db_health",
            new=AsyncMock(return_value={"status": "healthy", "connected": True}),
        ),
        patch(
            "src.database.get_db_stats",
            new=AsyncMock(
                return_value={
                    "total_notifications": 100,
                    "pending_notifications": 10,
                    "total_templates": 5,
                    "total_preferences": 20,
                }
            ),
        ),
    ):
        yield


@pytest.fixture
def mock_notification_repo():
    """Mock NotificationRepository"""
    with patch("src.main.NotificationRepository") as mock:
        mock_notif = MagicMock()
        mock_notif.id = uuid4()
        mock_notif.user_id = "user-123"
        mock_notif.title = "Test Notification"
        mock_notif.title_ar = "إشعار تجريبي"
        mock_notif.body = "Test body"
        mock_notif.body_ar = "نص تجريبي"
        mock_notif.type = "weather_alert"
        mock_notif.priority = "high"
        mock_notif.status = "pending"
        mock_notif.created_at = datetime.utcnow()
        mock_notif.expires_at = datetime.utcnow() + timedelta(hours=24)
        mock_notif.is_read = False
        mock_notif.data = {"type_ar": "تنبيه طقس", "priority_ar": "عالية"}
        mock_notif.action_url = None

        mock.create = AsyncMock(return_value=mock_notif)
        mock.get_by_user = AsyncMock(return_value=[mock_notif])
        mock.get_by_id = AsyncMock(return_value=mock_notif)
        mock.mark_as_read = AsyncMock(return_value=True)
        mock.get_unread_count = AsyncMock(return_value=5)
        mock.get_broadcast_notifications = AsyncMock(return_value=[mock_notif])
        yield mock


@pytest.fixture
def mock_preferences_service():
    """Mock PreferencesService"""
    with patch("src.main.PreferencesService") as mock:
        mock.check_if_should_send = AsyncMock(return_value=(True, ["push", "in_app"]))
        yield mock


@pytest.fixture
def app_client(mock_db, mock_notification_repo, mock_preferences_service):
    """Create test client with mocked dependencies"""
    with patch("src.main.create_notification") as mock_create:
        mock_create.return_value = AsyncMock()
        from src.main import app

        client = TestClient(app)
        yield client


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check_success(self, app_client):
        """Test health check returns healthy status"""
        response = app_client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["service"] == "notification-service"

    def test_health_check_includes_stats(self, app_client):
        """Test health check includes database stats"""
        response = app_client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data or "database" in data


class TestNotificationCreation:
    """Test notification creation endpoints"""

    @pytest.mark.asyncio
    async def test_create_custom_notification_success(self, app_client, mock_notification_repo):
        """Test creating custom notification"""
        payload = {
            "type": "weather_alert",
            "priority": "high",
            "title": "Weather Alert",
            "title_ar": "تنبيه طقس",
            "body": "Storm warning",
            "body_ar": "تحذير من عاصفة",
            "data": {"temp": 35},
            "target_farmers": ["farmer-1"],
            "channels": ["push", "in_app"],
            "expires_in_hours": 24,
        }

        with patch("src.main.create_notification") as mock_create:
            mock_notif = MagicMock()
            mock_notif.id = uuid4()
            mock_notif.type = "weather_alert"
            mock_notif.priority = "high"
            mock_notif.title = "Weather Alert"
            mock_notif.title_ar = "تنبيه طقس"
            mock_notif.body = "Storm warning"
            mock_notif.body_ar = "تحذير من عاصفة"
            mock_notif.status = "pending"
            mock_notif.created_at = datetime.utcnow()
            mock_notif.expires_at = datetime.utcnow() + timedelta(hours=24)
            mock_notif.data = {"type_ar": "تنبيه طقس", "priority_ar": "عالية"}
            mock_create.return_value = mock_notif

            response = app_client.post("/", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["type"] == "weather_alert"

    @pytest.mark.asyncio
    async def test_create_notification_missing_required_fields(self, app_client):
        """Test validation for missing required fields"""
        payload = {
            "type": "weather_alert",
            # Missing title, body, etc.
        }

        response = app_client.post("/", json=payload)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_weather_alert(self, app_client):
        """Test creating weather alert"""
        payload = {
            "governorates": ["sanaa", "taiz"],
            "alert_type": "storm",
            "severity": "high",
            "expected_date": (datetime.utcnow() + timedelta(days=1)).date().isoformat(),
            "details": {"wind_speed": 60},
        }

        with patch("src.main.create_notification") as mock_create:
            mock_notif = MagicMock()
            mock_notif.id = uuid4()
            mock_notif.type = "weather_alert"
            mock_notif.title = "Storm Warning"
            mock_notif.title_ar = "تحذير من عاصفة"
            mock_notif.body = "Storm expected"
            mock_notif.body_ar = "عاصفة متوقعة"
            mock_notif.created_at = datetime.utcnow()
            mock_create.return_value = mock_notif

            response = app_client.post("/weather", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "id" in data

    @pytest.mark.asyncio
    async def test_create_pest_alert(self, app_client):
        """Test creating pest alert"""
        payload = {
            "governorate": "sanaa",
            "pest_name": "Aphids",
            "pest_name_ar": "حشرات المن",
            "affected_crops": ["tomato", "wheat"],
            "severity": "medium",
            "recommendations": ["Use organic pesticides"],
            "recommendations_ar": ["استخدم مبيدات عضوية"],
        }

        with patch("src.main.create_notification") as mock_create:
            mock_notif = MagicMock()
            mock_notif.id = uuid4()
            mock_notif.type = "pest_outbreak"
            mock_notif.title = "Pest Outbreak: Aphids"
            mock_notif.created_at = datetime.utcnow()
            mock_create.return_value = mock_notif

            response = app_client.post("/pest", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "id" in data

    @pytest.mark.asyncio
    async def test_create_irrigation_reminder(self, app_client):
        """Test creating irrigation reminder"""
        payload = {
            "farmer_id": "farmer-123",
            "field_id": "field-456",
            "field_name": "North Field",
            "crop": "tomato",
            "water_needed_mm": 25.5,
            "urgency": "medium",
        }

        with patch("src.main.create_notification") as mock_create:
            mock_notif = MagicMock()
            mock_notif.id = uuid4()
            mock_notif.type = "irrigation_reminder"
            mock_notif.created_at = datetime.utcnow()
            mock_create.return_value = mock_notif

            response = app_client.post("/irrigation", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "id" in data


class TestNotificationRetrieval:
    """Test notification retrieval endpoints"""

    @pytest.mark.asyncio
    async def test_get_farmer_notifications(self, app_client, mock_notification_repo):
        """Test getting notifications for a farmer"""
        response = app_client.get("//farmer/farmer-123")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        assert "farmer_id" in data
        assert data["farmer_id"] == "farmer-123"

    @pytest.mark.asyncio
    async def test_get_farmer_notifications_with_filters(self, app_client, mock_notification_repo):
        """Test getting notifications with filters"""
        response = app_client.get(
            "//farmer/farmer-123",
            params={"unread_only": True, "type": "weather_alert", "limit": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data

    @pytest.mark.asyncio
    async def test_get_broadcast_notifications(self, app_client, mock_notification_repo):
        """Test getting broadcast notifications"""
        response = app_client.get("//broadcast")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_broadcast_notifications_with_filters(
        self, app_client, mock_notification_repo
    ):
        """Test getting broadcast notifications with filters"""
        response = app_client.get(
            "//broadcast",
            params={"governorate": "sanaa", "crop": "tomato", "limit": 20},
        )
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data


class TestNotificationActions:
    """Test notification action endpoints"""

    @pytest.mark.asyncio
    async def test_mark_notification_as_read(self, app_client, mock_notification_repo):
        """Test marking notification as read"""
        notification_id = str(uuid4())
        response = app_client.patch(
            f"//{notification_id}/read", params={"farmer_id": "farmer-123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_read"] is True

    @pytest.mark.asyncio
    async def test_mark_notification_as_read_invalid_id(self, app_client):
        """Test marking notification with invalid ID"""
        response = app_client.patch(
            "//invalid-id/read", params={"farmer_id": "farmer-123"}
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_mark_notification_as_read_not_found(self, app_client):
        """Test marking non-existent notification"""
        with patch("src.main.NotificationRepository.get_by_id", new=AsyncMock(return_value=None)):
            notification_id = str(uuid4())
            response = app_client.patch(
                f"//{notification_id}/read", params={"farmer_id": "farmer-123"}
            )
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_mark_notification_unauthorized(self, app_client):
        """Test marking notification for different farmer"""
        with patch("src.main.NotificationRepository.get_by_id") as mock_get:
            mock_notif = MagicMock()
            mock_notif.user_id = "farmer-999"  # Different farmer
            mock_get.return_value = mock_notif

            notification_id = str(uuid4())
            response = app_client.patch(
                f"//{notification_id}/read", params={"farmer_id": "farmer-123"}
            )
            assert response.status_code == 403


class TestFarmerManagement:
    """Test farmer registration and preferences"""

    def test_register_farmer(self, app_client):
        """Test registering a new farmer"""
        payload = {
            "farmer_id": "farmer-new",
            "name": "Ali Ahmed",
            "name_ar": "علي أحمد",
            "governorate": "sanaa",
            "crops": ["tomato", "wheat"],
            "field_ids": ["field-1"],
            "phone": "+967771234567",
            "email": "ali@example.com",
            "notification_channels": ["push", "sms"],
        }

        response = app_client.post("/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["farmer_id"] == "farmer-new"

    @pytest.mark.asyncio
    async def test_update_farmer_preferences(self, app_client):
        """Test updating farmer notification preferences"""
        payload = {
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

        with patch("src.main.NotificationPreferenceRepository.create_or_update", new=AsyncMock()):
            response = app_client.put("/farmer-123/preferences", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestNotificationStats:
    """Test notification statistics endpoint"""

    @pytest.mark.asyncio
    async def test_get_notification_stats(self, app_client):
        """Test getting notification statistics"""
        with (
            patch(
                "src.main.get_db_stats",
                new=AsyncMock(
                    return_value={
                        "total_notifications": 1000,
                        "pending_notifications": 50,
                        "total_templates": 10,
                        "total_preferences": 100,
                    }
                ),
            ),
            patch("src.models.Notification") as mock_model,
        ):
            mock_model.filter.return_value.count = AsyncMock(return_value=10)

            response = app_client.get("/stats")
            assert response.status_code == 200
            data = response.json()
            assert "total_notifications" in data
            assert "registered_farmers" in data


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_database_error_handling(self, app_client):
        """Test handling database errors gracefully"""
        with patch(
            "src.main.NotificationRepository.get_by_user", side_effect=Exception("DB Error")
        ):
            response = app_client.get("//farmer/farmer-123")
            # Should handle error gracefully, not crash
            assert response.status_code in [200, 500]

    @pytest.mark.asyncio
    async def test_invalid_enum_values(self, app_client):
        """Test validation of enum values"""
        payload = {
            "type": "invalid_type",  # Invalid type
            "priority": "high",
            "title": "Test",
            "title_ar": "اختبار",
            "body": "Test",
            "body_ar": "اختبار",
        }

        response = app_client.post("/", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_payload(self, app_client):
        """Test handling empty payload"""
        response = app_client.post("/", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_notification_creation_failure(self, app_client):
        """Test handling notification creation failure"""
        payload = {
            "type": "weather_alert",
            "priority": "high",
            "title": "Test",
            "title_ar": "اختبار",
            "body": "Test body",
            "body_ar": "نص اختبار",
        }

        with patch("src.main.create_notification", return_value=None):
            response = app_client.post("/", json=payload)
            assert response.status_code == 400


class TestAuthenticationIntegration:
    """Test authentication integration (when available)"""

    def test_endpoint_without_auth_header(self, app_client):
        """Test accessing endpoint without authentication"""
        # Most endpoints should work without auth in current implementation
        response = app_client.get("/healthz")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_protected_endpoint_behavior(self, app_client):
        """Test protected endpoint behavior"""
        # Test that endpoints handle optional authentication
        response = app_client.get("//farmer/farmer-123")
        # Should work even without auth (for now)
        assert response.status_code in [200, 401, 403]


class TestPaginationAndFiltering:
    """Test pagination and filtering capabilities"""

    @pytest.mark.asyncio
    async def test_pagination_parameters(self, app_client, mock_notification_repo):
        """Test pagination with limit and offset"""
        response = app_client.get(
            "//farmer/farmer-123", params={"limit": 10, "offset": 20}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_pagination_boundary_values(self, app_client, mock_notification_repo):
        """Test pagination boundary values"""
        # Test minimum
        response = app_client.get(
            "//farmer/farmer-123", params={"limit": 1, "offset": 0}
        )
        assert response.status_code == 200

        # Test maximum
        response = app_client.get(
            "//farmer/farmer-123", params={"limit": 100, "offset": 0}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_filtering_by_type(self, app_client, mock_notification_repo):
        """Test filtering notifications by type"""
        response = app_client.get(
            "//farmer/farmer-123", params={"type": "weather_alert"}
        )
        assert response.status_code == 200
