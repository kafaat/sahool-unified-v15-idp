"""
Pytest Configuration and Fixtures for WS Gateway
تكوين pytest والتجهيزات لبوابة WebSocket
"""

import os
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from jose import jwt


@pytest.fixture
def mock_env_vars():
    """Mock environment variables"""
    env_vars = {
        "JWT_SECRET_KEY": "test-secret-key-for-testing-only",
        "JWT_ALGORITHM": "HS256",
        "NATS_URL": "nats://localhost:4222",
        "PORT": "8081",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def sample_jwt_secret() -> str:
    """Sample JWT secret for testing"""
    return "test-secret-key-for-testing-only"


@pytest.fixture
def sample_user_payload() -> dict[str, Any]:
    """Sample user payload for JWT"""
    return {
        "sub": "user-123",
        "user_id": "user-123",
        "tenant_id": "tenant-456",
        "roles": ["farmer"],
        "exp": datetime.utcnow() + timedelta(hours=1),
    }


@pytest.fixture
def sample_admin_payload() -> dict[str, Any]:
    """Sample admin payload for JWT"""
    return {
        "sub": "admin-789",
        "user_id": "admin-789",
        "tenant_id": "tenant-admin",
        "roles": ["super_admin"],
        "exp": datetime.utcnow() + timedelta(hours=1),
    }


@pytest.fixture
def valid_jwt_token(sample_jwt_secret, sample_user_payload) -> str:
    """Generate valid JWT token"""
    return jwt.encode(sample_user_payload, sample_jwt_secret, algorithm="HS256")


@pytest.fixture
def admin_jwt_token(sample_jwt_secret, sample_admin_payload) -> str:
    """Generate admin JWT token"""
    return jwt.encode(sample_admin_payload, sample_jwt_secret, algorithm="HS256")


@pytest.fixture
def expired_jwt_token(sample_jwt_secret) -> str:
    """Generate expired JWT token"""
    expired_payload = {
        "sub": "user-999",
        "tenant_id": "tenant-999",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
    }
    return jwt.encode(expired_payload, sample_jwt_secret, algorithm="HS256")


@pytest.fixture
def invalid_jwt_token() -> str:
    """Invalid JWT token"""
    return "invalid.token.here"


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    websocket = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.receive_json = AsyncMock()
    websocket.close = AsyncMock()
    return websocket


@pytest.fixture
def sample_broadcast_request() -> dict[str, Any]:
    """Sample broadcast request"""
    return {
        "tenant_id": "tenant-456",
        "message": {
            "type": "notification",
            "title": "Test Alert",
            "body": "This is a test notification",
        },
    }


@pytest.fixture
def sample_room_message() -> dict[str, Any]:
    """Sample room message"""
    return {"action": "join", "room": "field:field-123"}
