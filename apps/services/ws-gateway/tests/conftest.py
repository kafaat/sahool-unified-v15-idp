"""
Pytest Configuration and Fixtures for WS Gateway
تكوين pytest والتجهيزات لبوابة WebSocket
"""

import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src modules from other services to avoid cross-contamination in CI
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _mod in list(sys.modules):
    if not (_mod == "src" or _mod.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_service_root):
        del sys.modules[_mod]
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, patch

import jwt
import pytest


@pytest.fixture
def mock_env_vars():
    """Mock environment variables"""
    env_vars = {
        "JWT_SECRET_KEY": "test-secret-key-for-unit-tests-only-32chars",
        "JWT_ALGORITHM": "HS256",
        "NATS_URL": "nats://localhost:4222",
        "PORT": "8081",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def sample_jwt_secret() -> str:
    """Sample JWT secret for testing"""
    return "test-secret-key-for-unit-tests-only-32chars"


@pytest.fixture
def sample_user_payload() -> dict[str, Any]:
    """Sample user payload for JWT"""
    now = datetime.utcnow()
    return {
        "sub": "user-123",
        "user_id": "user-123",
        "tenant_id": "tenant-456",
        "roles": ["farmer"],
        "iss": "sahool-platform",
        "aud": "sahool-api",
        "iat": now,
        "exp": now + timedelta(hours=1),
    }


@pytest.fixture
def sample_admin_payload() -> dict[str, Any]:
    """Sample admin payload for JWT"""
    now = datetime.utcnow()
    return {
        "sub": "admin-789",
        "user_id": "admin-789",
        "tenant_id": "tenant-admin",
        "roles": ["super_admin"],
        "iss": "sahool-platform",
        "aud": "sahool-api",
        "iat": now,
        "exp": now + timedelta(hours=1),
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
