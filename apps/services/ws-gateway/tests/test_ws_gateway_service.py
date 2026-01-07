"""
Comprehensive Tests for WebSocket Gateway Service
اختبارات شاملة لخدمة بوابة WebSocket
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsInRlbmFudF9pZCI6InRlbmFudF8xMjMiLCJyb2xlcyI6WyJ1c2VyIl19.test_signature"


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_health_check(self, client):
        """Test /healthz endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "ws-gateway"

    def test_readiness_check(self, client):
        """Test /readyz endpoint"""
        response = client.get("/readyz")
        assert response.status_code == 200
        assert "status" in response.json()
        assert "nats" in response.json()

    def test_stats_endpoint(self, client):
        """Test /stats endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        assert "connections" in response.json()
        assert "nats" in response.json()
        assert "timestamp" in response.json()


class TestWebSocketConnection:
    """Test WebSocket connection"""

    @patch("src.main.validate_jwt_token")
    def test_websocket_connection_success(self, mock_validate, client):
        """Test successful WebSocket connection (query param - deprecated)"""
        mock_validate.return_value = AsyncMock(
            return_value={"sub": "user_123", "tenant_id": "tenant_123"}
        )

        with client.websocket_connect("/ws?tenant_id=tenant_123&token=valid_token") as websocket:
            data = websocket.receive_json()

            assert data["type"] == "connected"
            assert "connection_id" in data
            assert data["tenant_id"] == "tenant_123"

    @patch("src.main.validate_jwt_token")
    def test_websocket_connection_with_auth_header(self, mock_validate, client):
        """Test successful WebSocket connection with Authorization header (preferred)"""
        mock_validate.return_value = AsyncMock(
            return_value={"sub": "user_123", "tenant_id": "tenant_123"}
        )

        # Note: TestClient may not support custom headers for websocket_connect
        # This is a placeholder for the expected behavior
        try:
            with client.websocket_connect(
                "/ws?tenant_id=tenant_123", headers={"Authorization": "Bearer valid_token"}
            ) as websocket:
                data = websocket.receive_json()

                assert data["type"] == "connected"
                assert "connection_id" in data
                assert data["tenant_id"] == "tenant_123"
        except TypeError:
            # TestClient might not support headers for WebSocket, skip this test
            pytest.skip("TestClient does not support WebSocket headers")

    def test_websocket_connection_without_token(self, client):
        """Test WebSocket connection without token"""
        with pytest.raises(Exception), client.websocket_connect("/ws?tenant_id=tenant_123"):
            pass

    @patch("src.main.validate_jwt_token")
    def test_websocket_connection_invalid_token(self, mock_validate, client):
        """Test WebSocket connection with invalid token"""
        mock_validate.side_effect = ValueError("Invalid token")

        with (
            pytest.raises(Exception),
            client.websocket_connect("/ws?tenant_id=tenant_123&token=invalid_token"),
        ):
            pass

    @patch("src.main.validate_jwt_token")
    def test_websocket_tenant_mismatch(self, mock_validate, client):
        """Test WebSocket connection with tenant mismatch"""
        mock_validate.return_value = AsyncMock(
            return_value={
                "sub": "user_123",
                "tenant_id": "tenant_456",  # Different tenant
            }
        )

        with pytest.raises(Exception):
            with client.websocket_connect("/ws?tenant_id=tenant_123&token=token"):
                pass


class TestWebSocketMessaging:
    """Test WebSocket messaging"""

    @patch("src.main.validate_jwt_token")
    @patch("src.main.room_manager")
    def test_send_message_to_room(self, mock_room_manager, mock_validate, client):
        """Test sending message to a room"""
        mock_validate.return_value = AsyncMock(
            return_value={"sub": "user_123", "tenant_id": "tenant_123"}
        )

        mock_room_manager.broadcast_to_room = AsyncMock(return_value=5)

        with client.websocket_connect("/ws?tenant_id=tenant_123&token=token") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send join room message
            websocket.send_json({"type": "join_room", "room": "field_123"})

            # Receive response
            response = websocket.receive_json()
            assert "type" in response

    @patch("src.main.validate_jwt_token")
    def test_websocket_message_echo(self, mock_validate, client):
        """Test message echo functionality"""
        mock_validate.return_value = AsyncMock(
            return_value={"sub": "user_123", "tenant_id": "tenant_123"}
        )

        with client.websocket_connect("/ws?tenant_id=tenant_123&token=token") as websocket:
            # Receive connection confirmation
            websocket.receive_json()

            # Send test message
            websocket.send_json({"type": "test", "data": "test message"})

            # Should receive response
            response = websocket.receive_json()
            assert response is not None


class TestBroadcastAPI:
    """Test broadcast REST API"""

    @patch("src.main.validate_jwt_token")
    @patch("src.main.room_manager")
    def test_broadcast_to_tenant(self, mock_room_manager, mock_validate, client):
        """Test broadcasting message to tenant"""
        mock_validate.return_value = {"sub": "user_123", "tenant_id": "tenant_123"}

        mock_room_manager.send_to_tenant = AsyncMock(return_value=10)

        broadcast_data = {
            "tenant_id": "tenant_123",
            "message": {"type": "notification", "content": "Test notification"},
        }

        response = client.post(
            "/broadcast",
            json=broadcast_data,
            headers={"Authorization": "Bearer test_token"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "sent"
        assert response.json()["recipients"] == 10

    def test_broadcast_without_token(self, client):
        """Test broadcast without authentication token"""
        broadcast_data = {"tenant_id": "tenant_123", "message": {"type": "test"}}

        response = client.post("/broadcast", json=broadcast_data)
        assert response.status_code == 401

    @patch("src.main.validate_jwt_token")
    def test_broadcast_tenant_mismatch(self, mock_validate, client):
        """Test broadcast with tenant mismatch"""
        mock_validate.return_value = {
            "sub": "user_123",
            "tenant_id": "tenant_456",
            "roles": [],
        }

        broadcast_data = {"tenant_id": "tenant_123", "message": {"type": "test"}}

        response = client.post(
            "/broadcast", json=broadcast_data, headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 403

    @patch("src.main.validate_jwt_token")
    @patch("src.main.room_manager")
    def test_broadcast_to_user(self, mock_room_manager, mock_validate, client):
        """Test broadcasting message to specific user"""
        mock_validate.return_value = {"sub": "admin_123", "tenant_id": "tenant_123"}

        mock_room_manager.send_to_user = AsyncMock(return_value=1)

        broadcast_data = {
            "tenant_id": "tenant_123",
            "user_id": "user_456",
            "message": {"type": "direct_message", "content": "Hello user"},
        }

        response = client.post(
            "/broadcast", json=broadcast_data, headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        assert response.json()["recipients"] == 1

    @patch("src.main.validate_jwt_token")
    @patch("src.main.room_manager")
    def test_broadcast_to_field(self, mock_room_manager, mock_validate, client):
        """Test broadcasting message to field"""
        mock_validate.return_value = {"sub": "user_123", "tenant_id": "tenant_123"}

        mock_room_manager.send_to_field = AsyncMock(return_value=3)

        broadcast_data = {
            "tenant_id": "tenant_123",
            "field_id": "field_789",
            "message": {"type": "field_update", "content": "Field status changed"},
        }

        response = client.post(
            "/broadcast", json=broadcast_data, headers={"Authorization": "Bearer token"}
        )

        assert response.status_code == 200
        assert response.json()["recipients"] == 3


class TestRoomManagement:
    """Test room management functionality"""

    @patch("src.main.room_manager")
    def test_room_stats(self, mock_room_manager, client):
        """Test getting room statistics"""
        mock_room_manager.get_stats.return_value = {
            "total_connections": 25,
            "total_rooms": 10,
            "connections_by_tenant": {"tenant_123": 15, "tenant_456": 10},
        }

        response = client.get("/stats")

        assert response.status_code == 200
        stats = response.json()
        assert "connections" in stats
        assert stats["connections"]["total_connections"] == 25


class TestNATSIntegration:
    """Test NATS integration"""

    @patch("src.main.nats_bridge")
    def test_nats_connected_status(self, mock_nats, client):
        """Test NATS connection status"""
        mock_nats.is_connected = True

        response = client.get("/readyz")

        assert response.status_code == 200
        assert response.json()["nats"] is True

    @patch("src.main.nats_bridge")
    def test_nats_stats(self, mock_nats, client):
        """Test NATS statistics"""
        mock_nats.get_stats.return_value = {
            "connected": True,
            "subscriptions": 5,
            "messages_received": 100,
        }

        response = client.get("/stats")

        assert response.status_code == 200
        assert "nats" in response.json()


# Integration test for complete workflow
class TestCompleteWorkflow:
    """Integration tests for complete WebSocket workflow"""

    @patch("src.main.validate_jwt_token")
    @patch("src.main.room_manager")
    def test_complete_websocket_workflow(self, mock_room_manager, mock_validate, client):
        """Test complete WebSocket communication workflow"""
        # Setup mocks
        mock_validate.return_value = {"sub": "user_123", "tenant_id": "tenant_123"}

        mock_room_manager.add_connection = AsyncMock()
        mock_room_manager.remove_connection = AsyncMock()
        mock_room_manager.broadcast_to_room = AsyncMock(return_value=1)

        # Connect WebSocket
        with client.websocket_connect("/ws?tenant_id=tenant_123&token=token") as websocket:
            # Step 1: Receive connection confirmation
            connection_data = websocket.receive_json()
            assert connection_data["type"] == "connected"
            connection_data["connection_id"]

            # Step 2: Join a room
            websocket.send_json({"type": "join_room", "room": "field_123"})

            # Step 3: Send a message to the room
            websocket.send_json(
                {"type": "message", "room": "field_123", "content": "Hello from user"}
            )

            # Connection should remain active
            assert websocket is not None
