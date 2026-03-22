"""
Tests for shared/middleware/tenant_context.py — Tenant context middleware
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.middleware.tenant_context import (
    TenantContext,
    TenantContextMiddleware,
    get_current_tenant,
    get_current_tenant_id,
    get_optional_tenant,
    is_current_user_admin,
    tenant_filter_dict,
)


VALID_UUID = str(uuid.uuid4())


def _make_app(**middleware_kwargs) -> FastAPI:
    """Create a test FastAPI app with TenantContextMiddleware."""
    app = FastAPI()
    app.add_middleware(TenantContextMiddleware, **middleware_kwargs)

    @app.get("/tenant-info")
    def tenant_info():
        ctx = get_current_tenant()
        return {"tenant_id": ctx.id, "user_id": ctx.user_id}

    @app.get("/optional")
    def optional_info():
        ctx = get_optional_tenant()
        return {"has_tenant": ctx is not None}

    @app.get("/healthz")
    def health():
        return {"status": "ok"}

    return app


class TestTenantContext:
    """Tests for the TenantContext dataclass."""

    def test_has_role_true(self):
        ctx = TenantContext(id="t1", roles=["admin", "user"])
        assert ctx.has_role("admin") is True

    def test_has_role_false(self):
        ctx = TenantContext(id="t1", roles=["user"])
        assert ctx.has_role("admin") is False

    def test_has_role_no_roles(self):
        ctx = TenantContext(id="t1")
        assert ctx.has_role("admin") is False


class TestTenantContextMiddleware:
    """Tests for middleware request flow."""

    def test_exempt_path_skips_tenant_check(self):
        app = _make_app(require_tenant=True)
        client = TestClient(app)
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_missing_tenant_returns_400(self):
        app = _make_app(require_tenant=True)
        client = TestClient(app)
        resp = client.get("/tenant-info")
        assert resp.status_code == 400
        assert resp.json()["error"] == "missing_tenant"

    def test_invalid_uuid_returns_400(self):
        app = _make_app(require_tenant=True)
        client = TestClient(app)
        resp = client.get("/tenant-info", headers={"X-Tenant-ID": "not-a-uuid"})
        assert resp.status_code == 400
        assert resp.json()["error"] == "invalid_tenant_id"

    def test_valid_tenant_from_header(self):
        app = _make_app(require_tenant=True)
        client = TestClient(app)
        resp = client.get("/tenant-info", headers={"X-Tenant-ID": VALID_UUID})
        assert resp.status_code == 200
        assert resp.json()["tenant_id"] == VALID_UUID

    def test_tenant_from_query_param_when_allowed(self):
        app = _make_app(require_tenant=True, allow_query_param=True)
        client = TestClient(app)
        resp = client.get(f"/tenant-info?tenant_id={VALID_UUID}")
        assert resp.status_code == 200
        assert resp.json()["tenant_id"] == VALID_UUID

    def test_tenant_from_query_param_not_allowed_by_default(self):
        app = _make_app(require_tenant=True, allow_query_param=False)
        client = TestClient(app)
        resp = client.get(f"/tenant-info?tenant_id={VALID_UUID}")
        assert resp.status_code == 400  # Query param ignored, no tenant found

    def test_not_required_tenant_passes_through(self):
        app = _make_app(require_tenant=False)
        client = TestClient(app)
        resp = client.get("/optional")
        assert resp.status_code == 200
        assert resp.json()["has_tenant"] is False

    def test_custom_exempt_paths(self):
        app = _make_app(require_tenant=True, exempt_paths=["/custom-health"])

        @app.get("/custom-health")
        def custom():
            return {"ok": True}

        client = TestClient(app)
        # Custom exempt path passes
        resp = client.get("/custom-health")
        assert resp.status_code == 200

        # Default /healthz is NOT exempt with custom list
        resp = client.get("/healthz")
        assert resp.status_code == 400


class TestContextHelpers:
    """Tests for context access helper functions."""

    def test_get_current_tenant_raises_outside_request(self):
        with pytest.raises(RuntimeError, match="Tenant context not available"):
            get_current_tenant()

    def test_get_optional_tenant_returns_none(self):
        result = get_optional_tenant()
        assert result is None

    def test_is_current_user_admin_false_outside_context(self):
        assert is_current_user_admin() is False

    def test_tenant_filter_dict_in_request(self):
        app = _make_app(require_tenant=False)

        @app.get("/filter-test")
        def filter_test():
            ctx = get_optional_tenant()
            if ctx:
                d = tenant_filter_dict()
                return d
            return {}

        client = TestClient(app)
        resp = client.get("/filter-test", headers={"X-Tenant-ID": VALID_UUID})
        assert resp.status_code == 200
        assert resp.json()["tenant_id"] == VALID_UUID


class TestIsCurrentUserAdmin:
    """Test admin role check within request context."""

    def test_admin_role_detected(self):
        app = FastAPI()
        app.add_middleware(TenantContextMiddleware, require_tenant=False)

        @app.get("/admin-check")
        def check():
            return {"is_admin": is_current_user_admin()}

        # Simulate JWT principal via middleware by setting state
        @app.middleware("http")
        async def set_principal(request, call_next):
            request.state.principal = {
                "tid": VALID_UUID,
                "sub": "user-1",
                "roles": ["admin"],
            }
            return await call_next(request)

        client = TestClient(app)
        resp = client.get("/admin-check")
        assert resp.status_code == 200
        assert resp.json()["is_admin"] is True

    def test_super_admin_role_detected(self):
        app = FastAPI()
        app.add_middleware(TenantContextMiddleware, require_tenant=False)

        @app.get("/admin-check")
        def check():
            return {"is_admin": is_current_user_admin()}

        @app.middleware("http")
        async def set_principal(request, call_next):
            request.state.principal = {
                "tid": VALID_UUID,
                "sub": "user-2",
                "roles": ["super_admin"],
            }
            return await call_next(request)

        client = TestClient(app)
        resp = client.get("/admin-check")
        assert resp.status_code == 200
        assert resp.json()["is_admin"] is True

    def test_non_admin_role(self):
        app = FastAPI()
        app.add_middleware(TenantContextMiddleware, require_tenant=False)

        @app.get("/admin-check")
        def check():
            return {"is_admin": is_current_user_admin()}

        @app.middleware("http")
        async def set_principal(request, call_next):
            request.state.principal = {
                "tid": VALID_UUID,
                "sub": "user-3",
                "roles": ["viewer"],
            }
            return await call_next(request)

        client = TestClient(app)
        resp = client.get("/admin-check")
        assert resp.status_code == 200
        assert resp.json()["is_admin"] is False


class TestGetCurrentTenantId:
    """Test get_current_tenant_id helper."""

    def test_returns_tenant_id_in_request(self):
        app = _make_app(require_tenant=True)

        @app.get("/tid")
        def tid():
            return {"tid": get_current_tenant_id()}

        client = TestClient(app)
        resp = client.get("/tid", headers={"X-Tenant-ID": VALID_UUID})
        assert resp.status_code == 200
        assert resp.json()["tid"] == VALID_UUID

    def test_raises_outside_request(self):
        with pytest.raises(RuntimeError):
            get_current_tenant_id()


class TestTenantContextFromJWT:
    """Test tenant extraction from JWT principal."""

    def test_tenant_extracted_from_principal(self):
        app = FastAPI()
        app.add_middleware(TenantContextMiddleware, require_tenant=True)

        @app.get("/info")
        def info():
            ctx = get_current_tenant()
            return {"tid": ctx.id, "uid": ctx.user_id, "roles": ctx.roles}

        @app.middleware("http")
        async def set_principal(request, call_next):
            request.state.principal = {
                "tid": VALID_UUID,
                "sub": "user-42",
                "roles": ["admin", "editor"],
            }
            return await call_next(request)

        client = TestClient(app)
        resp = client.get("/info")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tid"] == VALID_UUID
        assert data["uid"] == "user-42"
        assert data["roles"] == ["admin", "editor"]
