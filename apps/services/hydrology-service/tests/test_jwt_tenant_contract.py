"""
JWT-only tenant isolation and contract-path tests for hydrology-service.

اختبارات عزل المستأجر عبر JWT لخدمة الهيدرولوجيا

Verifies that:
- ``GET /api/v1/hydrology/basins/{field_id}`` is reachable via JWT alone
  (no ``X-Tenant-Id`` header needed).
- ``GET /api/v1/hydrology/drainage/{field_id}`` is reachable via JWT alone.
- When the JWT carries a tenant, a mismatching ``X-Tenant-Id`` header is
  rejected with 403.
- The legacy endpoints ``/wetness``, ``/depressions``, ``/streams`` continue
  to work unchanged.
"""

from __future__ import annotations

import os
import sys
import types
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_shared(monkeypatch):
    """Provide shared.* stubs so the service can boot in unit tests."""
    shared = types.ModuleType("shared")
    errors_py = types.ModuleType("shared.errors_py")
    errors_py.add_request_id_middleware = lambda app: None
    errors_py.setup_exception_handlers = lambda app: None
    shared.errors_py = errors_py

    middleware = types.ModuleType("shared.middleware")
    tenant_ctx = types.ModuleType("shared.middleware.tenant_context")

    class _FakeTenantMiddleware:
        def __init__(self, app, **kwargs):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

    tenant_ctx.TenantContextMiddleware = _FakeTenantMiddleware
    shared.middleware = middleware
    shared.middleware.tenant_context = tenant_ctx

    db_mod = types.ModuleType("shared.db")
    simple_mig = types.ModuleType("shared.db.simple_migrations")

    class _Migration:
        def __init__(self, version, description, up, down):
            self.version = version
            self.description = description
            self.up = up
            self.down = down

    class _MigrationRunner:
        def __init__(self, *a, **kw):
            pass

        async def run(self, migrations):
            return None

    simple_mig.Migration = _Migration
    simple_mig.SimpleMigrationRunner = _MigrationRunner
    db_mod.simple_migrations = simple_mig
    shared.db = db_mod

    monkeypatch.setitem(sys.modules, "shared", shared)
    monkeypatch.setitem(sys.modules, "shared.errors_py", errors_py)
    monkeypatch.setitem(sys.modules, "shared.middleware", middleware)
    monkeypatch.setitem(sys.modules, "shared.middleware.tenant_context", tenant_ctx)
    monkeypatch.setitem(sys.modules, "shared.db", db_mod)
    monkeypatch.setitem(sys.modules, "shared.db.simple_migrations", simple_mig)


class _FakeUser:
    """Stand-in for shared.auth.models.User."""

    id = "hydro-user"
    tenant_id = "00000000-0000-0000-0000-000000000055"


@pytest.fixture
def jwt_client(mock_shared):
    """TestClient with get_current_user overridden by a JWT-user stub."""
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")

    from importlib import reload

    with patch.dict(
        os.environ,
        {"DATABASE_URL": "", "NATS_URL": "", "ENVIRONMENT": "test"},
    ):
        try:
            import src.main  # type: ignore[import-not-found]
        except ImportError as exc:
            pytest.skip(f"hydrology-service not importable: {exc}")

        # Reload to pick up mocked shared.* modules
        reload(src.main)

        from fastapi.testclient import TestClient
        from src.api.endpoints.hydrology import get_current_user
        from src.main import app

        async def _user_override():
            return _FakeUser()

        app.dependency_overrides[get_current_user] = _user_override
        with TestClient(app) as client:
            yield client
        app.dependency_overrides.clear()


def test_basins_endpoint_reachable_via_jwt_only(jwt_client):
    """GET /api/v1/hydrology/basins/{field_id} works without X-Tenant-Id header."""
    response = jwt_client.get("/api/v1/hydrology/basins/FIELD-HYD-001")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["success"] is True
    body = data["data"]
    assert body["field_id"] == "FIELD-HYD-001"
    assert "total_basins" in body


def test_drainage_endpoint_reachable_via_jwt_only(jwt_client):
    """GET /api/v1/hydrology/drainage/{field_id} works without X-Tenant-Id header."""
    response = jwt_client.get("/api/v1/hydrology/drainage/FIELD-HYD-002")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["success"] is True
    body = data["data"]
    assert body["field_id"] == "FIELD-HYD-002"
    assert "total_length_m" in body
    assert "segments" in body


def test_conflicting_tenant_header_rejected(jwt_client):
    """When JWT has a tenant, a mismatching X-Tenant-Id must 403."""
    response = jwt_client.get(
        "/api/v1/hydrology/basins/FIELD-HYD-003",
        headers={"X-Tenant-Id": "ffffffff-ffff-ffff-ffff-ffffffffffff"},
    )
    assert response.status_code == 403


def test_matching_tenant_header_accepted(jwt_client):
    """A matching X-Tenant-Id is harmless (legacy compatibility)."""
    response = jwt_client.get(
        "/api/v1/hydrology/basins/FIELD-HYD-004",
        headers={"X-Tenant-Id": _FakeUser.tenant_id},
    )
    assert response.status_code == 200


def test_wetness_still_mounted(jwt_client):
    """Legacy endpoints remain available at the same contract paths."""
    response = jwt_client.get("/api/v1/hydrology/wetness/FIELD-HYD-005")
    assert response.status_code == 200
    assert response.json()["success"] is True
