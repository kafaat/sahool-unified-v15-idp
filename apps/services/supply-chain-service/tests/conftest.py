"""Pytest configuration and fixtures for Supply Chain Service tests."""

import os
import sys
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["REDIS_URL"] = ""
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"

# Add service root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Mock shared.auth module tree to avoid cryptography import issues
# Provide a real async function for get_current_user
async def _fake_get_current_user():
    return {"id": "12345678-1234-1234-1234-123456789abc", "tenant_id": "test-tenant", "token": "fake-token"}


_mock_auth = MagicMock()
_mock_auth.dependencies.get_current_user = _fake_get_current_user
sys.modules["shared.auth"] = _mock_auth
sys.modules["shared.auth.dependencies"] = _mock_auth.dependencies
sys.modules["shared.auth.models"] = _mock_auth.models

# Mock shared.errors_py to avoid import issues
sys.modules["shared.errors_py"] = MagicMock()


# Mock shared.middleware.tenant_context with a proper ASGI middleware
class _FakeTenantMiddleware:
    """No-op middleware that just passes through."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


_mock_tenant_module = MagicMock()
_mock_tenant_module.TenantContextMiddleware = _FakeTenantMiddleware
sys.modules["shared.middleware"] = MagicMock()
sys.modules["shared.middleware.tenant_context"] = _mock_tenant_module

try:
    from src.main import app
except (ImportError, OSError, RuntimeError) as exc:
    app = None


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio backend for pytest-asyncio."""
    return "asyncio"


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for synchronous tests."""
    if app is None:
        pytest.skip("supply-chain-service src not available")
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("fastapi not installed")
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client():
    """Create an async test client for async tests."""
    if app is None:
        pytest.skip("supply-chain-service src not available")
    try:
        from httpx import ASGITransport, AsyncClient
    except ImportError:
        pytest.skip("httpx not installed")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_farmer_id() -> str:
    """Generate a sample farmer ID."""
    return str(uuid4())


@pytest.fixture
def sample_supplier_id() -> str:
    """Generate a sample supplier ID."""
    return str(uuid4())


@pytest.fixture
def sample_product_id() -> str:
    """Generate a sample product ID."""
    return str(uuid4())


@pytest.fixture
def sample_order_data(sample_supplier_id: str, sample_product_id: str) -> dict:
    """Create sample order data for testing."""
    return {
        "supplier_id": sample_supplier_id,
        "items": [
            {
                "product_id": sample_product_id,
                "quantity": 50.0,
            }
        ],
        "delivery_address": "Farm Address, Al-Kharj, Saudi Arabia",
        "delivery_address_ar": "عنوان المزرعة، الخرج، المملكة العربية السعودية",
        "payment_method": "cash_on_delivery",
        "notes": "Please deliver in the morning",
        "notes_ar": "يرجى التوصيل صباحاً",
    }


@pytest.fixture
def sample_quote_request(sample_product_id: str) -> dict:
    """Create sample quote request data."""
    return {
        "product_id": sample_product_id,
        "quantity": 100.0,
        "delivery_address": "Farm Address, Riyadh",
    }


@pytest.fixture
def sample_bulk_purchase_data(sample_product_id: str) -> dict:
    """Create sample bulk purchase data."""
    return {
        "items": [
            {"product_id": sample_product_id, "quantity": 100.0},
            {"product_id": str(uuid4()), "quantity": 50.0},
        ],
        "delivery_address": "Farm Warehouse, Al-Kharj",
        "payment_method": "cash_on_delivery",
        "optimize_for": "price",
    }
