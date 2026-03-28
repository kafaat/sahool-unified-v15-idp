"""Test configuration for traceability-service."""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"


@pytest.fixture
def client():
    """Create test client with tenant header."""
    from src.main import app

    c = TestClient(app)
    c.headers["X-Tenant-Id"] = "00000000-0000-0000-0000-000000000001"
    return c


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
def app_with_db(mock_db_pool, mock_nats):
    """Create FastAPI app with mocked DB and NATS."""
    from src.main import app

    app.state.db_pool = mock_db_pool
    app.state.db_connected = True
    app.state.nc = mock_nats
    app.state.nats_connected = True
    return app


@pytest.fixture
def db_client(app_with_db):
    """Create test client with DB mock, tenant header, and auth override."""
    from src.api.v1.batches import get_current_user

    app_with_db.dependency_overrides[get_current_user] = lambda: {"id": "test-user", "role": "admin"}
    c = TestClient(app_with_db)
    c.headers["X-Tenant-Id"] = "00000000-0000-0000-0000-000000000001"
    yield c
    app_with_db.dependency_overrides.pop(get_current_user, None)
