"""Pytest configuration and fixtures for Supply Chain Service tests."""

import os
from uuid import uuid4

import pytest

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["REDIS_URL"] = ""
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"

try:
    from src.main import app
except ImportError:
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
