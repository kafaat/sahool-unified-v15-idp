"""
Tests for Wave 2 inventory CRUD endpoints (/api/v1/inventory).
اختبارات نقاط نهاية CRUD الخاصة بالمخزون - الموجة الثانية.

Covers:
- Happy path: create -> list -> get -> update -> adjust -> delete
- Optimistic locking conflict on update & adjust
- Tenant isolation (items from tenant A are invisible to tenant B)
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import Mock

import pytest

try:
    # Importing the module is what registers the v2 tables on Base.metadata.
    from fastapi.testclient import TestClient
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from src.main import app, get_current_user, get_db
    from src.models import inventory_v2 as _inventory_v2  # noqa: F401
    from src.models.inventory import Base

    assert _inventory_v2 is not None  # keep the side-effect import alive
except ImportError:  # pragma: no cover - skip if deps missing locally
    pytest.skip("inventory-service dependencies not installed", allow_module_level=True)


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
async def session_maker(engine) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    yield maker


def _make_client(session_maker, tenant_id: str = "tenant-a") -> TestClient:
    """Build a TestClient that always uses a fresh session per-request."""

    async def override_get_db():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def override_get_current_user():
        user = Mock()
        user.id = "user-1"
        user.tenant_id = tenant_id
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app)


@pytest.fixture
def client_a(session_maker):
    client = _make_client(session_maker, tenant_id="tenant-a")
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client_b(session_maker):
    client = _make_client(session_maker, tenant_id="tenant-b")
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


def _sample_payload(**overrides):
    base = {
        "name": "Urea 46%",
        "name_ar": "يوريا 46%",
        "sku": "URE-46",
        "category": "fertilizer",
        "quantity": "100.0",
        "unit": "kg",
        "unit_price": "12.50",
        "currency": "SAR",
        "low_stock_threshold": "20.0",
    }
    base.update(overrides)
    return base


class TestInventoryCrudHappyPath:
    def test_full_crud_cycle(self, client_a):
        # Create
        resp = client_a.post("/api/v1/inventory", json=_sample_payload())
        assert resp.status_code == 201, resp.text
        item = resp.json()
        item_id = item["id"]
        assert item["tenant_id"] == "tenant-a"
        assert item["version"] == 1
        assert item["name"] == "Urea 46%"

        # List
        resp = client_a.get("/api/v1/inventory")
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["pagination"]["total"] == 1
        assert len(payload["items"]) == 1

        # Filter by category
        resp = client_a.get("/api/v1/inventory", params={"category": "fertilizer"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 1

        resp = client_a.get("/api/v1/inventory", params={"category": "pesticide"})
        assert resp.status_code == 200
        assert resp.json()["pagination"]["total"] == 0

        # Get single
        resp = client_a.get(f"/api/v1/inventory/{item_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == item_id

        # Update with correct version
        resp = client_a.put(
            f"/api/v1/inventory/{item_id}",
            json={"name": "Urea 46% Premium", "if_match_version": 1},
        )
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["name"] == "Urea 46% Premium"
        assert updated["version"] == 2

        # Adjust stock (+50)
        resp = client_a.post(
            f"/api/v1/inventory/{item_id}/adjust",
            json={
                "delta": "50.0",
                "reason": "purchase received",
                "transaction_type": "purchase",
                "if_match_version": 2,
            },
        )
        assert resp.status_code == 200, resp.text
        adjusted = resp.json()
        assert float(adjusted["quantity"]) == 150.0
        assert adjusted["version"] == 3

        # Transactions log
        resp = client_a.get("/api/v1/inventory/transactions")
        assert resp.status_code == 200
        txns = resp.json()["transactions"]
        assert len(txns) == 1
        assert txns[0]["transaction_type"] == "purchase"
        assert float(txns[0]["quantity_delta"]) == 50.0
        assert float(txns[0]["quantity_after"]) == 150.0

        # Stats
        resp = client_a.get("/api/v1/inventory/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_items"] == 1
        assert float(stats["total_quantity"]) == 150.0
        assert stats["out_of_stock_count"] == 0

        # Adjust would go negative -> 400
        resp = client_a.post(
            f"/api/v1/inventory/{item_id}/adjust",
            json={
                "delta": "-500.0",
                "reason": "big sale",
                "transaction_type": "sale",
            },
        )
        assert resp.status_code == 400

        # Delete (soft)
        resp = client_a.delete(f"/api/v1/inventory/{item_id}")
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True

        # After soft delete the item is hidden from listings & get
        resp = client_a.get("/api/v1/inventory")
        assert resp.json()["pagination"]["total"] == 0

        resp = client_a.get(f"/api/v1/inventory/{item_id}")
        assert resp.status_code == 404


class TestOptimisticLocking:
    def test_update_version_conflict_returns_409(self, client_a):
        resp = client_a.post("/api/v1/inventory", json=_sample_payload(sku="LOCK-1"))
        item_id = resp.json()["id"]

        # Stale version
        resp = client_a.put(
            f"/api/v1/inventory/{item_id}",
            json={"name": "X", "if_match_version": 99},
        )
        assert resp.status_code == 409
        detail = resp.json()["detail"]
        # Bilingual payload
        assert "message" in detail
        assert "message_ar" in detail

    def test_adjust_version_conflict_returns_409(self, client_a):
        resp = client_a.post("/api/v1/inventory", json=_sample_payload(sku="LOCK-2"))
        item_id = resp.json()["id"]

        resp = client_a.post(
            f"/api/v1/inventory/{item_id}/adjust",
            json={
                "delta": "1.0",
                "reason": "test",
                "transaction_type": "adjustment",
                "if_match_version": 7,
            },
        )
        assert resp.status_code == 409


class TestTenantIsolation:
    def test_tenant_b_cannot_see_tenant_a_items(self, session_maker):
        # Seed item as tenant-a
        client_a = _make_client(session_maker, tenant_id="tenant-a")
        try:
            resp = client_a.post("/api/v1/inventory", json=_sample_payload(sku="ISO-1"))
            assert resp.status_code == 201
            item_id = resp.json()["id"]
        finally:
            app.dependency_overrides.clear()

        # Now switch to tenant-b
        client_b = _make_client(session_maker, tenant_id="tenant-b")
        try:
            # List should be empty
            resp = client_b.get("/api/v1/inventory")
            assert resp.status_code == 200
            assert resp.json()["pagination"]["total"] == 0

            # Direct fetch must 404
            resp = client_b.get(f"/api/v1/inventory/{item_id}")
            assert resp.status_code == 404

            # Update attempt must 404
            resp = client_b.put(
                f"/api/v1/inventory/{item_id}",
                json={"name": "hacked"},
            )
            assert resp.status_code == 404

            # Adjust attempt must 404
            resp = client_b.post(
                f"/api/v1/inventory/{item_id}/adjust",
                json={
                    "delta": "1",
                    "reason": "hack",
                    "transaction_type": "adjustment",
                },
            )
            assert resp.status_code == 404

            # Stats are empty for tenant-b
            resp = client_b.get("/api/v1/inventory/stats")
            assert resp.status_code == 200
            assert resp.json()["total_items"] == 0
        finally:
            app.dependency_overrides.clear()
