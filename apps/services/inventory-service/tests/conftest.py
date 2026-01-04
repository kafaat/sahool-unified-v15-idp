"""
Pytest Configuration and Fixtures for Inventory Service
تكوين pytest والتجهيزات لخدمة المخزون
"""

import os

# Import models
import sys
from collections.abc import AsyncGenerator
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared"))
from database.base import Base


@pytest.fixture(scope="function")
async def async_engine():
    """Create an async in-memory SQLite engine for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create an async database session for testing"""
    async_session_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_env_vars():
    """Mock environment variables"""
    env_vars = {
        "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test_db",
        "ALLOW_DEV_DEFAULTS": "true",
        "CORS_ALLOWED_ORIGINS": "http://localhost:3000",
        "SERVICE_PORT": "8115",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def sample_tenant_id() -> str:
    """Sample tenant ID for testing"""
    return "test-tenant-123"


@pytest.fixture
def sample_item_category():
    """Sample item category data"""
    return {
        "name_en": "Fertilizers",
        "name_ar": "الأسمدة",
        "code": "FERT",
        "description": "Agricultural fertilizers",
    }


@pytest.fixture
def sample_warehouse():
    """Sample warehouse data"""
    return {
        "name": "Main Warehouse",
        "code": "WH001",
        "location": "Sana'a",
        "tenant_id": "test-tenant-123",
    }


@pytest.fixture
def sample_supplier():
    """Sample supplier data"""
    return {
        "name": "AgriSupply Co.",
        "contact_person": "Ahmed Ali",
        "phone": "+967-777-123456",
        "email": "contact@agrisupply.ye",
        "lead_time_days": 7,
        "tenant_id": "test-tenant-123",
    }


@pytest.fixture
def sample_inventory_item():
    """Sample inventory item data"""
    return {
        "sku": "FERT-NPK-001",
        "name_en": "NPK Fertilizer 20-20-20",
        "name_ar": "سماد NPK 20-20-20",
        "unit": "kg",
        "current_stock": Decimal("500.0"),
        "available_stock": Decimal("500.0"),
        "reserved_stock": Decimal("0.0"),
        "reorder_level": Decimal("100.0"),
        "reorder_quantity": Decimal("500.0"),
        "minimum_stock": Decimal("50.0"),
        "maximum_stock": Decimal("2000.0"),
        "average_cost": Decimal("15.0"),
        "has_expiry": False,
        "tenant_id": "test-tenant-123",
    }


@pytest.fixture
def sample_inventory_movement():
    """Sample inventory movement data"""
    return {
        "movement_type": "RECEIPT",
        "quantity": Decimal("100.0"),
        "unit_cost": Decimal("15.0"),
        "total_cost": Decimal("1500.0"),
        "reference_no": "PO-2024-001",
        "movement_date": datetime.now(),
        "tenant_id": "test-tenant-123",
    }


@pytest.fixture
def sample_consumption_forecast():
    """Sample consumption forecast data"""
    from src.inventory_analytics import ConsumptionForecast

    return ConsumptionForecast(
        item_id="item-123",
        item_name="NPK Fertilizer",
        current_stock=500.0,
        avg_daily_consumption=5.0,
        avg_weekly_consumption=35.0,
        avg_monthly_consumption=150.0,
        days_until_stockout=100,
        reorder_date=date.today() + timedelta(days=80),
        recommended_order_qty=500.0,
        confidence=0.85,
    )


@pytest.fixture
async def mock_analytics_session():
    """Mock analytics session with sample data"""
    session = AsyncMock(spec=AsyncSession)
    return session
