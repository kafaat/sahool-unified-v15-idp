"""Test configuration for cooperative-service."""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"


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
    """Create test client with tenant header."""
    from src.main import app

    from src.api.v1.cooperatives import get_current_user

    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    c = TestClient(app)
    c.headers["X-Tenant-Id"] = "00000000-0000-0000-0000-000000000001"
    yield c
    app.dependency_overrides.pop(get_current_user, None)


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
def app_with_db(mock_db_pool, mock_nats, mock_auth_user):
    """Create FastAPI app with mocked DB and NATS."""
    from src.main import app

    from src.api.v1.cooperatives import get_current_user

    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    app.state.db_pool = mock_db_pool
    app.state.db_connected = True
    app.state.nc = mock_nats
    app.state.nats_connected = True
    yield app
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def db_client(app_with_db):
    """Create test client with DB mock and tenant header."""
    c = TestClient(app_with_db)
    c.headers["X-Tenant-Id"] = "00000000-0000-0000-0000-000000000001"
    return c
