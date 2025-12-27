"""
Integration Tests for WS Gateway API
اختبارات التكامل لواجهة برمجة بوابة WebSocket
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch


@pytest.fixture
def client(mock_env_vars):
    """Create test client"""
    # Mock NATS bridge to prevent connection attempts
    with patch('src.main.NATSBridge') as mock_nats:
        mock_nats_instance = AsyncMock()
        mock_nats_instance.is_connected = False
        mock_nats_instance.connect = AsyncMock()
        mock_nats_instance.disconnect = AsyncMock()
        mock_nats_instance.get_stats = Mock(return_value={"connected": False})
        mock_nats.return_value = mock_nats_instance
       
        from src.main import app
       
        with TestClient(app) as test_client:
            yield test_client


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_healthz(self, client):
        """Test basic health check"""
        response = client.get("/healthz")
       
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ws-gateway"
        assert "version" in data
        assert "timestamp" in data

    def test_readyz(self, client):
        """Test readiness check"""
        response = client.get("/readyz")
       
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "nats" in data
        assert "connections" in data

    def test_stats(self, client):
        """Test statistics endpoint"""
        response = client.get("/stats")
       
        assert response.status_code == 200
        data = response.json()
        assert "connections" in data
        assert "nats" in data
        assert "timestamp" in data


class TestBroadcastEndpoint:
    """Test broadcast API endpoint"""

    def test_broadcast_to_tenant(self, client, valid_jwt_token, sample_broadcast_request):
        """Test broadcasting to tenant"""
        response = client.post(
            "/broadcast",
            json=sample_broadcast_request,
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )
       
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"
        assert "recipients" in data
        assert "timestamp" in data

    def test_broadcast_to_user(self, client, valid_jwt_token):
        """Test broadcasting to specific user"""
        request_data = {
            "user_id": "user-123",
            "tenant_id": "tenant-456",
            "message": {
                "type": "notification",
                "body": "Direct message"
            }
        }
       
        response = client.post(
            "/broadcast",
            json=request_data,
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )
       
        assert response.status_code == 200

    def test_broadcast_to_field(self, client, valid_jwt_token):
        """Test broadcasting to field watchers"""
        request_data = {
            "field_id": "field-789",
            "tenant_id": "tenant-456",
            "message": {
                "type": "field_update",
                "body": "Irrigation completed"
            }
        }
       
        response = client.post(
            "/broadcast",
            json=request_data,
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )
       
        assert response.status_code == 200

    def test_broadcast_to_room(self, client, valid_jwt_token):
        """Test broadcasting to specific room"""
        request_data = {
            "room": "chat:general",
            "tenant_id": "tenant-456",
            "message": {
                "type": "chat_message",
                "body": "Hello everyone"
            }
        }
       
        response = client.post(
            "/broadcast",
            json=request_data,
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )
       
        assert response.status_code == 200

    def test_broadcast_without_token(self, client, sample_broadcast_request):
        """Test broadcast without authentication token"""
        response = client.post("/broadcast", json=sample_broadcast_request)
       
        assert response.status_code == 401

    def test_broadcast_with_invalid_token(self, client, invalid_jwt_token, sample_broadcast_request):
        """Test broadcast with invalid token"""
        response = client.post(
            "/broadcast",
            json=sample_broadcast_request,
            headers={"Authorization": f"Bearer {invalid_jwt_token}"}
        )
       
        assert response.status_code == 401

    def test_broadcast_tenant_mismatch(self, client, valid_jwt_token):
        """Test broadcast to different tenant (should fail for non-admin)"""
        request_data = {
            "tenant_id": "different-tenant",
            "message": {
                "type": "notification",
                "body": "Unauthorized"
            }
        }
       
        response = client.post(
            "/broadcast",
            json=request_data,
            headers={"Authorization": f"Bearer {valid_jwt_token}"}
        )
       
        assert response.status_code == 403

    def test_broadcast_admin_cross_tenant(self, client, admin_jwt_token):
        """Test admin can broadcast to any tenant"""
        request_data = {
            "tenant_id": "any-tenant",
            "message": {
                "type": "system_announcement",
                "body": "System maintenance"
            }
        }
       
        response = client.post(
            "/broadcast",
            json=request_data,
            headers={"Authorization": f"Bearer {admin_jwt_token}"}
        )
       
        assert response.status_code == 200


class TestJWTValidation:
    """Test JWT validation logic"""

    @pytest.mark.asyncio
    async def test_validate_valid_token(self, mock_env_vars, valid_jwt_token):
        """Test validating a valid JWT token"""
        from src.main import validate_jwt_token
       
        payload = await validate_jwt_token(valid_jwt_token)
       
        assert payload is not None
        assert "sub" in payload
        assert payload["tenant_id"] == "tenant-456"

    @pytest.mark.asyncio
    async def test_validate_expired_token(self, mock_env_vars, expired_jwt_token):
        """Test validating an expired token"""
        from src.main import validate_jwt_token
       
        with pytest.raises(ValueError, match="Invalid token"):
            await validate_jwt_token(expired_jwt_token)

    @pytest.mark.asyncio
    async def test_validate_invalid_token(self, mock_env_vars, invalid_jwt_token):
        """Test validating an invalid token"""
        from src.main import validate_jwt_token
       
        with pytest.raises(ValueError, match="Invalid token"):
            await validate_jwt_token(invalid_jwt_token)

    @pytest.mark.asyncio
    async def test_validate_empty_token(self, mock_env_vars):
        """Test validating empty token"""
        from src.main import validate_jwt_token
       
        with pytest.raises(ValueError, match="Token is required"):
            await validate_jwt_token("")


class TestDataModels:
    """Test data models"""

    def test_broadcast_request_model(self):
        """Test BroadcastRequest model"""
        from src.main import BroadcastRequest
       
        request = BroadcastRequest(
            tenant_id="tenant-123",
            message={"type": "test", "body": "hello"}
        )
       
        assert request.tenant_id == "tenant-123"
        assert request.message["type"] == "test"
        assert request.user_id is None
        assert request.field_id is None
        assert request.room is None

    def test_broadcast_request_with_all_fields(self):
        """Test BroadcastRequest with all fields"""
        from src.main import BroadcastRequest
       
        request = BroadcastRequest(
            tenant_id="tenant-123",
            user_id="user-456",
            field_id="field-789",
            room="chat:general",
            message={"type": "test"}
        )
       
        assert request.tenant_id == "tenant-123"
        assert request.user_id == "user-456"
        assert request.field_id == "field-789"
        assert request.room == "chat:general"
