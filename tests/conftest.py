"""
SAHOOL Test Configuration
Shared fixtures for all tests - Single Source of Truth
"""

from __future__ import annotations

import os
from collections.abc import Generator
from datetime import timezone, datetime, timedelta, UTC
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


@pytest.fixture
def test_token(test_user_id, test_tenant_id, test_roles, test_scopes) -> str:
    """
    Generate a valid JWT token for E2E and integration tests.
    توليد رمز JWT صالح لاختبارات E2E والتكامل.
    """
    try:
        import jwt

        secret_key = os.environ.get("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
        algorithm = os.environ.get("JWT_ALGORITHM", "HS256")

        payload = {
            "sub": test_user_id,
            "tid": test_tenant_id,
            "roles": test_roles,
            "scopes": test_scopes,
            "iss": os.environ.get("JWT_ISSUER", "sahool-idp"),
            "aud": os.environ.get("JWT_AUDIENCE", "sahool-platform"),
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC),
        }

        return jwt.encode(payload, secret_key, algorithm=algorithm)
    except ImportError:
        # PyJWT not installed, return a placeholder token
        return "test-token-placeholder"


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


# ═══════════════════════════════════════════════════════════════════════════════
# Factory Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def field_factory():
    """Field factory fixture."""
    from tests.factories.field_factory import FieldFactory

    return FieldFactory


@pytest.fixture
def user_factory():
    """User factory fixture."""
    from tests.factories.user_factory import UserFactory

    return UserFactory


@pytest.fixture
def farm_factory():
    """Farm factory fixture."""
    from tests.factories.farm_factory import FarmFactory

    return FarmFactory


@pytest.fixture
def crop_factory():
    """Crop factory fixture."""
    from tests.factories.crop_factory import CropFactory

    return CropFactory


# ═══════════════════════════════════════════════════════════════════════════════
# Enhanced Mock Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_event_publisher():
    """Mock event publisher for testing."""
    from tests.utils.mocks import MockEventPublisher

    return MockEventPublisher()


@pytest.fixture
def mock_database():
    """Mock database for testing."""
    from tests.utils.mocks import MockDatabase

    return MockDatabase()


@pytest.fixture
def mock_redis_client():
    """Mock Redis client with full functionality."""
    from tests.utils.mocks import MockRedisClient

    return MockRedisClient()


@pytest.fixture
def mock_nats_client():
    """Mock NATS client with full functionality."""
    from tests.utils.mocks import MockNATSClient

    return MockNATSClient()


# ═══════════════════════════════════════════════════════════════════════════════
# API Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def auth_headers(test_token) -> dict:
    """Headers with authentication token."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {test_token}",
    }


@pytest.fixture
def arabic_content() -> dict:
    """Sample Arabic content for testing."""
    return {
        "name": "Test",
        "name_ar": "اختبار",
        "description": "Test description",
        "description_ar": "وصف الاختبار",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Geospatial Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_polygon() -> dict:
    """Sample GeoJSON polygon (Saudi Arabia location)."""
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [46.6753, 24.7136],
                [46.6853, 24.7136],
                [46.6853, 24.7236],
                [46.6753, 24.7236],
                [46.6753, 24.7136],
            ]
        ],
    }


@pytest.fixture
def sample_multipolygon() -> dict:
    """Sample GeoJSON MultiPolygon."""
    return {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [46.6753, 24.7136],
                    [46.6853, 24.7136],
                    [46.6853, 24.7236],
                    [46.6753, 24.7236],
                    [46.6753, 24.7136],
                ]
            ],
            [
                [
                    [46.7753, 24.8136],
                    [46.7853, 24.8136],
                    [46.7853, 24.8236],
                    [46.7753, 24.8236],
                    [46.7753, 24.8136],
                ]
            ],
        ],
    }


@pytest.fixture
def sample_point() -> dict:
    """Sample GeoJSON point (Riyadh)."""
    return {
        "type": "Point",
        "coordinates": [46.6753, 24.7136],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Agricultural Data Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_ndvi_data() -> dict:
    """Sample NDVI analysis data."""
    return {
        "field_id": "field-123",
        "mean_ndvi": 0.65,
        "min_ndvi": 0.35,
        "max_ndvi": 0.85,
        "std_ndvi": 0.12,
        "health_status": "healthy",
        "health_status_ar": "صحي",
        "cloud_cover_percent": 5.2,
        "acquisition_date": datetime.now(UTC).isoformat(),
    }


@pytest.fixture
def sample_weather_data() -> dict:
    """Sample weather data."""
    return {
        "temperature": 28.5,
        "humidity": 45.0,
        "wind_speed": 12.0,
        "precipitation": 0.0,
        "conditions": "sunny",
        "conditions_ar": "مشمس",
        "forecast_date": datetime.now(UTC).isoformat(),
    }


@pytest.fixture
def sample_soil_data() -> dict:
    """Sample soil analysis data."""
    return {
        "ph": 7.2,
        "nitrogen_ppm": 25.0,
        "phosphorus_ppm": 18.0,
        "potassium_ppm": 150.0,
        "organic_matter_percent": 2.5,
        "soil_type": "loam",
        "soil_type_ar": "طفلة",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Async Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def anyio_backend():
    """Backend for anyio tests."""
    return "asyncio"


