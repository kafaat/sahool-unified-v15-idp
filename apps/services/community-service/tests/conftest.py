"""Test configuration for community-service."""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
os.environ["JWT_ALGORITHM"] = "HS256"


@pytest.fixture
def mock_auth_user():
    """Create a mock authenticated user."""
    user = MagicMock()
    user.id = "test-user-001"
    user.username = "test_farmer"
    user.email = "farmer@sahool.app"
    user.tenant_id = "00000000-0000-0000-0000-000000000001"
    user.roles = ["user"]
    return user


@pytest.fixture
def client(mock_auth_user):
    """Create test client with mocked auth and tenant header."""
    with patch("src.main.get_current_user", return_value=mock_auth_user):
        from src.main import app

        c = TestClient(app)
        c.headers["X-Tenant-Id"] = "00000000-0000-0000-0000-000000000001"
        yield c


@pytest.fixture
def mock_rc_client():
    """Create a mock Rocket.Chat client."""
    rc = AsyncMock()
    rc.create_channel = AsyncMock(return_value={"_id": "ch001", "name": "test-channel"})
    rc.get_channels = AsyncMock(return_value=[])
    rc.post_message = AsyncMock(return_value={"_id": "msg001", "ts": "2026-01-01T00:00:00Z"})
    rc.add_user_to_channel = AsyncMock(return_value={})
    rc.remove_user_from_channel = AsyncMock(return_value={})
    rc.get_channel_history = AsyncMock(return_value=[])
    rc.get_channel_members = AsyncMock(return_value=[])
    rc.search_messages = AsyncMock(return_value=[])
    rc.create_user = AsyncMock(return_value={"_id": "rc_user_001", "username": "test"})
    rc.set_user_avatar = AsyncMock(return_value={})
    rc.pin_message = AsyncMock(return_value={})
    return rc


@pytest.fixture
def mock_db_pool():
    """Create a mock database pool for testing."""
    pool = AsyncMock()
    pool.fetchrow = AsyncMock()
    pool.fetch = AsyncMock(return_value=[])
    pool.fetchval = AsyncMock(return_value=0)
    pool.execute = AsyncMock()
    return pool


@pytest.fixture
def mock_nats():
    """Create a mock NATS client."""
    nc = AsyncMock()
    nc.publish = AsyncMock()
    return nc


@pytest.fixture
def app_with_rc(mock_rc_client, mock_db_pool, mock_nats, mock_auth_user):
    """Create FastAPI app with mocked Rocket.Chat, DB, and NATS."""
    with patch("src.main.get_current_user", return_value=mock_auth_user):
        from src.main import app

        app.state.rc = mock_rc_client
        app.state.rc_connected = True
        app.state.db_pool = mock_db_pool
        app.state.db_connected = True
        app.state.nc = mock_nats
        app.state.nats_connected = True
        app.state.redis = None
        app.state.redis_connected = False
        yield app


@pytest.fixture
def rc_client(app_with_rc):
    """Create test client with Rocket.Chat mock and tenant header."""
    c = TestClient(app_with_rc)
    c.headers["X-Tenant-Id"] = "00000000-0000-0000-0000-000000000001"
    return c
