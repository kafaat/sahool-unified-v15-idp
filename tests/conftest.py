"""
SAHOOL Test Configuration
Shared fixtures for all tests - Single Source of Truth
"""

from __future__ import annotations

import os
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Environment Setup
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Configure test environment variables before all tests"""
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")
    os.environ.setdefault("JWT_ISSUER", "sahool-idp")
    os.environ.setdefault("JWT_AUDIENCE", "sahool-platform")
    os.environ.setdefault("DATABASE_URL", "")
    os.environ.setdefault("NATS_URL", "")
    yield


# ═══════════════════════════════════════════════════════════════════════════════
# Database Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Test database URL - in-memory SQLite for speed"""
    return os.getenv(
        "TEST_DATABASE_URL",
        "sqlite+pysqlite:///:memory:",
    )


@pytest.fixture(scope="function")
def db_session(test_db_url):
    """
    Database session fixture.
    Creates a fresh session per test function.
    When Testcontainers is added, modify this fixture only.
    """
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(test_db_url, future=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            yield session
        finally:
            session.close()
    except ImportError:
        # SQLAlchemy not installed, yield mock
        yield MagicMock()


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def test_user_id() -> str:
    """Standard test user ID"""
    return "test-user-123"


@pytest.fixture
def test_tenant_id() -> str:
    """Standard test tenant ID"""
    return "test-tenant-456"


@pytest.fixture
def test_roles() -> list[str]:
    """Default test roles"""
    return ["worker"]


@pytest.fixture
def test_scopes() -> list[str]:
    """Default test scopes"""
    return ["fieldops:task.read", "fieldops:field.read"]


@pytest.fixture
def admin_roles() -> list[str]:
    """Admin test roles"""
    return ["admin"]


@pytest.fixture
def super_admin_roles() -> list[str]:
    """Super admin test roles"""
    return ["super_admin"]


@pytest.fixture
def test_principal(test_user_id, test_tenant_id, test_roles, test_scopes) -> dict:
    """Standard test principal (decoded JWT payload)"""
    return {
        "sub": test_user_id,
        "tid": test_tenant_id,
        "roles": test_roles,
        "scopes": test_scopes,
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
    }


@pytest.fixture
def admin_principal(test_user_id, test_tenant_id, admin_roles) -> dict:
    """Admin test principal"""
    return {
        "sub": test_user_id,
        "tid": test_tenant_id,
        "roles": admin_roles,
        "scopes": [],
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# API Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def api_headers(test_user_id, test_tenant_id) -> dict:
    """Standard API headers for testing"""
    return {
        "Content-Type": "application/json",
        "X-Tenant-ID": test_tenant_id,
        "X-User-ID": test_user_id,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Field Operations Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_field_data(test_tenant_id) -> dict:
    """Sample field creation data"""
    return {
        "tenant_id": test_tenant_id,
        "name": "Test Field Alpha",
        "name_ar": "حقل اختبار ألفا",
        "area_hectares": 25.5,
        "crop_type": "wheat",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[45.0, 15.0], [45.1, 15.0], [45.1, 15.1], [45.0, 15.1], [45.0, 15.0]]],
        },
    }


@pytest.fixture
def sample_operation_data(test_tenant_id) -> dict:
    """Sample operation creation data"""
    return {
        "tenant_id": test_tenant_id,
        "field_id": "field-123",
        "operation_type": "irrigation",
        "scheduled_date": datetime.now(UTC).isoformat(),
        "notes": "Scheduled irrigation",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_nats() -> Generator[MagicMock, None, None]:
    """Mock NATS client"""
    mock = MagicMock()
    mock.publish = MagicMock(return_value=None)
    mock.subscribe = MagicMock(return_value=None)
    yield mock


@pytest.fixture
def mock_redis() -> Generator[MagicMock, None, None]:
    """Mock Redis client"""
    mock = MagicMock()
    mock.get = MagicMock(return_value=None)
    mock.set = MagicMock(return_value=True)
    mock.delete = MagicMock(return_value=1)
    yield mock
