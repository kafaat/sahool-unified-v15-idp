"""
Contract-path tests for leveling-optimizer-service.

اختبارات مسار العقد لخدمة تحسين التسوية

Verifies that the endpoints used by the unified API contract
(``TERRAIN_ENDPOINTS``) are reachable and enforce JWT-only tenant isolation:

- ``POST /api/v1/leveling/analyze`` (cut/fill data included in response body)
- ``GET  /api/v1/leveling/cost/{field_id}`` (only ``cut_volume_m3`` required)

These tests override ``get_current_user`` with a fake JWT-derived ``User`` —
no ``X-Tenant-Id`` header is sent, yet the service must still honour tenant
isolation via the authenticated user.
"""

from __future__ import annotations

import pytest


class _FakeUser:
    """Minimal stand-in for shared.auth.models.User."""

    id = "user-leveling-contract"
    tenant_id = "00000000-0000-0000-0000-000000000099"


@pytest.fixture
def contract_client():
    """TestClient with JWT auth overridden (no X-Tenant-Id header needed)."""
    try:
        from fastapi.testclient import TestClient
        from src.api.endpoints.leveling import get_current_user
        from src.main import app
    except ImportError as exc:  # pragma: no cover
        pytest.skip(f"leveling-optimizer-service not importable: {exc}")

    async def _user_override():
        return _FakeUser()

    app.dependency_overrides[get_current_user] = _user_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_elevation_points():
    return [
        {"x": 0.0, "y": 0.0, "elevation": 100.00, "point_id": "P1"},
        {"x": 100.0, "y": 0.0, "elevation": 100.20, "point_id": "P2"},
        {"x": 0.0, "y": 100.0, "elevation": 100.10, "point_id": "P3"},
        {"x": 100.0, "y": 100.0, "elevation": 100.40, "point_id": "P4"},
        {"x": 50.0, "y": 50.0, "elevation": 100.15, "point_id": "P5"},
    ]


def test_analyze_returns_cut_fill_in_same_response(contract_client, sample_elevation_points):
    """POST /api/v1/leveling/analyze must include cut/fill volumes in the response body."""
    request_body = {
        "field_id": "FIELD-LVL-001",
        "elevation_points": sample_elevation_points,
        "soil_type": "loamy",
        "method": "single_plane",
        "priority": "minimize_cost",
        "include_cost_estimate": True,
    }

    response = contract_client.post("/api/v1/leveling/analyze", json=request_body)
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["success"] is True
    assert data["field_id"] == "FIELD-LVL-001"

    plan = data["plan"]
    # Cut/fill is part of the analyze response — NO separate /cut-fill endpoint
    assert "cut_fill" in plan, "cut/fill must be included in analyze response"
    cut_fill = plan["cut_fill"]
    assert "cut_volume_m3" in cut_fill
    assert "fill_volume_m3" in cut_fill
    assert "net_volume_m3" in cut_fill
    assert cut_fill["cut_volume_m3"] >= 0
    assert cut_fill["fill_volume_m3"] >= 0


def test_cost_endpoint_only_requires_cut_volume(contract_client):
    """
    GET /api/v1/leveling/cost/{field_id}?cut_volume_m3=... must succeed with
    only the single required parameter per contract.
    """
    response = contract_client.get(
        "/api/v1/leveling/cost/FIELD-LVL-002",
        params={"cut_volume_m3": 1500.0},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    # Core cost fields must be present
    assert "total_cost_sar" in data
    assert "earthwork_cost_sar" in data
    assert "equipment_cost_sar" in data
    assert "labor_cost_sar" in data
    assert "cost_per_m3_sar" in data
    assert "cost_per_hectare_sar" in data
    assert data["total_cost_sar"] > 0


def test_cost_endpoint_accepts_all_optional_params(contract_client):
    """Caller may still pass fill volume, area, and haul distance."""
    response = contract_client.get(
        "/api/v1/leveling/cost/FIELD-LVL-003",
        params={
            "cut_volume_m3": 2500,
            "fill_volume_m3": 2300,
            "field_area_hectares": 2.5,
            "haul_distance_m": 120.0,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_cost_sar"] > 0
    assert "summary_en" in data
    assert "summary_ar" in data


def test_cost_endpoint_rejects_invalid_field_id(contract_client):
    """Field IDs with control characters or path traversal must be rejected."""
    response = contract_client.get(
        "/api/v1/leveling/cost/../evil",
        params={"cut_volume_m3": 100},
    )
    # Starlette will normalize, so the most common outcome is 400 or 404;
    # we accept any 4xx as proof the route doesn't happily log attacker input.
    assert 400 <= response.status_code < 500


def test_analyze_tenant_isolation_via_jwt(contract_client, sample_elevation_points):
    """
    The endpoint must accept calls with NO X-Tenant-Id header, so long as
    the authenticated User carries a tenant_id from the JWT.
    """
    response = contract_client.post(
        "/api/v1/leveling/analyze",
        json={
            "field_id": "FIELD-JWT-TENANT",
            "elevation_points": sample_elevation_points,
            "method": "single_plane",
            "priority": "minimize_cost",
            "include_cost_estimate": False,
        },
        # Deliberately no X-Tenant-Id — the service must not require it
    )
    assert response.status_code == 200, response.text
    assert response.json()["field_id"] == "FIELD-JWT-TENANT"
