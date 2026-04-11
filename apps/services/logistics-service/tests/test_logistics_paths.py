"""Tests for Wave 2 logistics path migration, drivers endpoint, and status enum.

Covers:
- New `/api/v1/logistics/*` path prefixes.
- Legacy aliases `/api/v1/shipments` and `/api/v1/stats` still respond and
  now carry RFC 8594 deprecation headers.
- New `/api/v1/logistics/drivers` endpoint with pagination envelope.
- Status enum unification: accepts both legacy (`pending`, `in-transit`,
  `delayed`) and canonical values; emits canonical on output.
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.main import (
    DRIVERS,
    HARVEST_COLLECTIONS,
    SHIPMENTS,
    STORAGE_FACILITIES,
    VEHICLES,
    app,
    seed_demo_data,
)

TENANT = "tenant_demo"
HEADERS = {"X-Tenant-Id": "00000000-0000-0000-0000-000000000001"}


async def _override_tenant_id():
    return TENANT


class _MockUser:
    id = "test-user-logistics"
    tenant_id = TENANT
    email = "test@sahool.app"
    role = "admin"


@pytest.fixture(autouse=True)
def reset_stores():
    """Reset in-memory stores before each test and reseed demo data."""
    VEHICLES.clear()
    STORAGE_FACILITIES.clear()
    HARVEST_COLLECTIONS.clear()
    SHIPMENTS.clear()
    DRIVERS.clear()
    seed_demo_data()
    yield
    VEHICLES.clear()
    STORAGE_FACILITIES.clear()
    HARVEST_COLLECTIONS.clear()
    SHIPMENTS.clear()
    DRIVERS.clear()


@pytest.fixture
def client():
    from src.main import get_current_user as real_get_current_user
    from src.main import get_tenant_id as real_get_tenant_id

    app.dependency_overrides[real_get_tenant_id] = _override_tenant_id
    app.dependency_overrides[real_get_current_user] = lambda: _MockUser()
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


def _create_shipment(client):
    return client.post(
        "/api/v1/logistics/shipments",
        json={
            "vehicle_id": "veh_001",
            "cargo_description": "Test cargo",
            "weight_kg": 1000,
            "scheduled_departure": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
        },
        headers=HEADERS,
    )


class TestNewLogisticsPaths:
    """Paths under /api/v1/logistics/* should be the canonical surface."""

    def test_new_shipments_list_path(self, client):
        _create_shipment(client)
        resp = client.get("/api/v1/logistics/shipments", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "shipments" in data
        assert "pagination" in data
        assert data["pagination"]["total"] == data["total"]
        assert data["pagination"]["limit"] == data["limit"]
        assert data["pagination"]["offset"] == data["offset"]
        # New path should NOT carry deprecation headers
        assert "Deprecation" not in resp.headers
        assert "Sunset" not in resp.headers

    def test_new_shipments_create_path(self, client):
        resp = _create_shipment(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "scheduled"
        assert data["weight_kg"] == 1000

    def test_new_stats_path(self, client):
        resp = client.get("/api/v1/logistics/stats", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "fleet" in data
        assert "collections" in data
        # New path should NOT carry deprecation headers
        assert "Deprecation" not in resp.headers


class TestDeprecatedAliases:
    """Legacy paths continue to work but emit RFC 8594 headers."""

    def test_legacy_shipments_path_still_works(self, client):
        resp = client.get("/api/v1/shipments", headers=HEADERS)
        assert resp.status_code == 200

    def test_legacy_shipments_emits_deprecation_headers(self, client):
        resp = client.get("/api/v1/shipments", headers=HEADERS)
        assert resp.headers.get("X-API-Deprecated") == "true"
        assert resp.headers.get("Deprecation") == "true"
        assert "Sunset" in resp.headers
        assert "Link" in resp.headers
        assert "/api/v1/logistics/shipments" in resp.headers["Link"]

    def test_legacy_stats_path_emits_deprecation_headers(self, client):
        resp = client.get("/api/v1/stats", headers=HEADERS)
        assert resp.status_code == 200
        assert resp.headers.get("X-API-Deprecated") == "true"
        assert "Link" in resp.headers
        assert "/api/v1/logistics/stats" in resp.headers["Link"]


class TestDriversEndpoint:
    """New drivers endpoint at /api/v1/logistics/drivers."""

    def test_list_drivers_envelope(self, client):
        resp = client.get("/api/v1/logistics/drivers", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "drivers" in data
        assert "pagination" in data
        assert data["pagination"]["total"] == data["total"]
        # Seed data provides 2 demo drivers for tenant_demo
        assert data["total"] == 2

    def test_get_driver_by_id(self, client):
        resp = client.get("/api/v1/logistics/drivers/driver_001", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "driver_001"
        assert data["name"] == "Ahmed Mohammed"
        assert data["status"] == "active"

    def test_get_driver_not_found(self, client):
        resp = client.get("/api/v1/logistics/drivers/nonexistent", headers=HEADERS)
        assert resp.status_code == 404

    def test_create_driver(self, client):
        resp = client.post(
            "/api/v1/logistics/drivers",
            json={
                "name": "Omar Saleh",
                "name_ar": "عمر صالح",
                "phone": "+967-771-000-000",
                "license_number": "DL-YE-999",
                "vehicle_type": "truck",
                "status": "active",
            },
            headers=HEADERS,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Omar Saleh"
        assert data["vehicle_type"] == "truck"
        assert data["id"].startswith("driver_")

    def test_drivers_filtered_by_tenant(self, client):
        """Drivers from other tenants should not leak."""
        DRIVERS["driver_other"] = {
            **DRIVERS["driver_001"],
            "id": "driver_other",
            "tenant_id": "other_tenant",
        }
        resp = client.get("/api/v1/logistics/drivers", headers=HEADERS)
        data = resp.json()
        assert data["total"] == 2  # still 2, not 3
        ids = [d["id"] for d in data["drivers"]]
        assert "driver_other" not in ids


class TestStatusEnumUnification:
    """Status enum accepts legacy + canonical values, emits canonical output."""

    def test_list_shipments_accepts_legacy_dash_form(self, client):
        _create_shipment(client)
        # `in-transit` is a legacy dash form; should be accepted and normalized
        resp = client.get("/api/v1/logistics/shipments?status=in-transit", headers=HEADERS)
        assert resp.status_code == 200

    def test_list_shipments_accepts_soft_pending(self, client):
        _create_shipment(client)
        # `pending` is a frontend soft state; maps to `scheduled`
        resp = client.get("/api/v1/logistics/shipments?status=pending", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        # Should return shipments with canonical `scheduled` status
        assert all(s["status"] == "scheduled" for s in data["shipments"])

    def test_list_shipments_rejects_invalid_status(self, client):
        resp = client.get("/api/v1/logistics/shipments?status=bogus", headers=HEADERS)
        assert resp.status_code == 400

    def test_update_status_accepts_legacy_in_transit(self, client):
        create_resp = _create_shipment(client)
        sid = create_resp.json()["shipment_id"]
        resp = client.post(
            f"/api/v1/logistics/shipments/{sid}/status?status=in-transit",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        assert SHIPMENTS[sid]["status"] == "in_transit"

    def test_update_status_delayed_is_soft_state(self, client):
        """`delayed` is a soft UX state; persisted as in_transit + metadata flag."""
        create_resp = _create_shipment(client)
        sid = create_resp.json()["shipment_id"]
        # First move to in_transit
        client.post(
            f"/api/v1/logistics/shipments/{sid}/status?status=in_transit",
            headers=HEADERS,
        )
        # Then mark delayed
        resp = client.post(
            f"/api/v1/logistics/shipments/{sid}/status?status=delayed",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        # Canonical persisted status is still in_transit
        assert SHIPMENTS[sid]["status"] == "in_transit"
        # With a delayed flag in metadata
        assert SHIPMENTS[sid].get("metadata", {}).get("delayed") is True

    def test_update_status_pending_maps_to_scheduled(self, client):
        create_resp = _create_shipment(client)
        sid = create_resp.json()["shipment_id"]
        resp = client.post(
            f"/api/v1/logistics/shipments/{sid}/status?status=pending",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        # "pending" is a soft state that persists as "scheduled"
        assert SHIPMENTS[sid]["status"] == "scheduled"
