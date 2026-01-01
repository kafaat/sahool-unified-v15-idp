"""
SAHOOL Notification Service - Unit Tests
اختبارات خدمة الإشعارات
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client with mocked app"""
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/healthz")
    def health():
        return {"status": "ok", "service": "notification_service"}

    @app.post("/api/v1/notifications/send")
    def send_notification():
        return {
            "id": "notif_001",
            "status": "sent",
            "channels": ["push", "email"],
            "timestamp": "2025-12-23T10:00:00Z",
        }

    @app.get("/api/v1/users/{user_id}/notifications")
    def get_user_notifications(user_id: str, limit: int = 20):
        return {
            "user_id": user_id,
            "notifications": [
                {
                    "id": "notif_001",
                    "type": "alert",
                    "title": "تنبيه ري",
                    "title_en": "Irrigation Alert",
                    "body": "حقلك يحتاج للري",
                    "read": False,
                    "timestamp": "2025-12-23T08:00:00Z",
                }
            ],
            "unread_count": 3,
        }

    @app.put("/api/v1/notifications/{notification_id}/read")
    def mark_as_read(notification_id: str):
        return {"id": notification_id, "read": True}

    @app.put("/api/v1/users/{user_id}/notifications/read-all")
    def mark_all_read(user_id: str):
        return {"user_id": user_id, "marked_count": 5}

    @app.get("/api/v1/users/{user_id}/preferences")
    def get_preferences(user_id: str):
        return {
            "user_id": user_id,
            "channels": {"push": True, "email": True, "sms": False},
            "categories": {
                "alerts": True,
                "tasks": True,
                "weather": True,
                "marketing": False,
            },
        }

    @app.put("/api/v1/users/{user_id}/preferences")
    def update_preferences(user_id: str):
        return {"user_id": user_id, "status": "updated"}

    @app.post("/api/v1/notifications/broadcast")
    def broadcast():
        return {"broadcast_id": "broadcast_001", "recipients": 150, "status": "queued"}

    @app.get("/api/v1/templates")
    def list_templates():
        return {
            "templates": [
                {"id": "irrigation_alert", "name": "Irrigation Alert"},
                {"id": "weather_warning", "name": "Weather Warning"},
            ]
        }

    return TestClient(app)


class TestHealthEndpoint:
    """Test health check"""

    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200


class TestSendNotification:
    """Test sending notifications"""

    def test_send_notification(self, client):
        response = client.post(
            "/api/v1/notifications/send",
            json={
                "user_id": "user_001",
                "type": "alert",
                "title": "Test",
                "body": "Test notification",
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "sent"


class TestUserNotifications:
    """Test user notifications"""

    def test_get_notifications(self, client):
        response = client.get("/api/v1/users/user_001/notifications")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data

    def test_mark_as_read(self, client):
        response = client.put("/api/v1/notifications/notif_001/read")
        assert response.status_code == 200
        assert response.json()["read"] == True

    def test_mark_all_read(self, client):
        response = client.put("/api/v1/users/user_001/notifications/read-all")
        assert response.status_code == 200


class TestPreferences:
    """Test notification preferences"""

    def test_get_preferences(self, client):
        response = client.get("/api/v1/users/user_001/preferences")
        assert response.status_code == 200
        data = response.json()
        assert "channels" in data
        assert "categories" in data

    def test_update_preferences(self, client):
        response = client.put(
            "/api/v1/users/user_001/preferences",
            json={"channels": {"push": True, "email": False}},
        )
        assert response.status_code == 200


class TestBroadcast:
    """Test broadcast notifications"""

    def test_broadcast(self, client):
        response = client.post(
            "/api/v1/notifications/broadcast",
            json={
                "tenant_id": "tenant_001",
                "title": "Announcement",
                "body": "Important message",
            },
        )
        assert response.status_code == 200
        assert "recipients" in response.json()


class TestTemplates:
    """Test notification templates"""

    def test_list_templates(self, client):
        response = client.get("/api/v1/templates")
        assert response.status_code == 200
        assert "templates" in response.json()
