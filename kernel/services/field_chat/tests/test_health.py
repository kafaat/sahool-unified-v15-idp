"""
Tests for Field Chat Health Endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app

        return TestClient(app)

    def test_health_check(self, client):
        """Test /healthz endpoint"""
        response = client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "field_chat"
        assert "version" in data

    def test_root_endpoint(self, client):
        """Test root endpoint returns service info"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SAHOOL Field Chat"
        assert "description_ar" in data
        assert "description_en" in data
        assert "endpoints" in data


class TestThreadEndpoints:
    """Test chat thread endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app

        return TestClient(app)

    def test_create_thread_validation(self, client):
        """Test thread creation validates scope_type"""
        response = client.post(
            "/chat/threads",
            json={
                "tenant_id": "tenant-1",
                "scope_type": "invalid_type",
                "scope_id": "123",
                "created_by": "user-1",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "invalid_scope_type" in str(data)

    def test_get_thread_not_found(self, client):
        """Test getting non-existent thread"""
        response = client.get(
            "/chat/threads/00000000-0000-0000-0000-000000000000",
            params={"tenant_id": "tenant-1"},
        )

        assert response.status_code == 404


class TestMessageEndpoints:
    """Test chat message endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app

        return TestClient(app)

    def test_send_message_thread_not_found(self, client):
        """Test sending message to non-existent thread"""
        response = client.post(
            "/chat/threads/00000000-0000-0000-0000-000000000000/messages",
            json={
                "tenant_id": "tenant-1",
                "sender_id": "user-1",
                "text": "Test message",
            },
        )

        assert response.status_code == 404

    def test_search_messages_requires_query(self, client):
        """Test search requires query parameter"""
        response = client.get(
            "/chat/messages/search",
            params={"tenant_id": "tenant-1"},
        )

        assert response.status_code == 422  # Validation error


class TestUnreadCounts:
    """Test unread count endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app

        return TestClient(app)

    def test_get_unread_counts(self, client):
        """Test getting unread counts"""
        response = client.get(
            "/chat/unread-counts",
            params={"tenant_id": "tenant-1", "user_id": "user-1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_unread" in data
        assert "threads" in data
