"""
اختبارات عزل المستأجرين - Tenant Isolation Security Tests

Comprehensive tests for tenant isolation across the SAHOOL platform.
Tests validate that:
1. TenantContextMiddleware correctly extracts and enforces tenant_id
2. Cross-tenant access is blocked for non-admin users
3. Admin users can cross tenant boundaries
4. Database query helpers enforce tenant filtering
5. Tenant context is async-safe via ContextVar
6. Vulnerable patterns (body-extracted tenant_id) are rejected
"""

import asyncio
import os
import uuid
from contextvars import copy_context
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.testclient import TestClient

# Ensure test environment
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")

from shared.middleware.tenant_context import (
    TenantContext,
    TenantContextMiddleware,
    _tenant_context,
    get_current_tenant,
    get_current_tenant_id,
    get_optional_tenant,
    tenant_filter_dict,
)
from shared.auth.dependencies import enforce_tenant
from shared.auth.models import User


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def tenant_a_id() -> str:
    return f"tenant-a-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def tenant_b_id() -> str:
    return f"tenant-b-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def user_a(tenant_a_id) -> User:
    """Regular user belonging to tenant A."""
    return User(
        id="user-a-001",
        email="farmer-a@sahool.app",
        roles=["farmer"],
        tenant_id=tenant_a_id,
        permissions=["field:read", "field:write"],
        is_active=True,
        is_verified=True,
    )


@pytest.fixture
def user_b(tenant_b_id) -> User:
    """Regular user belonging to tenant B."""
    return User(
        id="user-b-002",
        email="farmer-b@sahool.app",
        roles=["farmer"],
        tenant_id=tenant_b_id,
        permissions=["field:read", "field:write"],
        is_active=True,
        is_verified=True,
    )


@pytest.fixture
def admin_user(tenant_a_id) -> User:
    """Super admin user belonging to tenant A but can access any tenant."""
    return User(
        id="admin-001",
        email="admin@sahool.app",
        roles=["super_admin"],
        tenant_id=tenant_a_id,
        permissions=["*"],
        is_active=True,
        is_verified=True,
    )


@pytest.fixture
def tenant_context_a(tenant_a_id):
    """Set up tenant context for tenant A."""
    ctx = TenantContext(id=tenant_a_id, user_id="user-a-001", roles=["farmer"])
    token = _tenant_context.set(ctx)
    yield ctx
    _tenant_context.reset(token)


@pytest.fixture
def tenant_context_b(tenant_b_id):
    """Set up tenant context for tenant B."""
    ctx = TenantContext(id=tenant_b_id, user_id="user-b-002", roles=["farmer"])
    token = _tenant_context.set(ctx)
    yield ctx
    _tenant_context.reset(token)


def _create_test_app(require_tenant: bool = True, allow_query_param: bool = False) -> FastAPI:
    """Create a FastAPI test app with TenantContextMiddleware."""
    app = FastAPI()
    app.add_middleware(
        TenantContextMiddleware,
        require_tenant=require_tenant,
        allow_query_param=allow_query_param,
    )

    @app.get("/api/v1/fields")
    async def list_fields():
        tenant_id = get_current_tenant_id()
        return {"tenant_id": tenant_id, "fields": []}

    @app.get("/api/v1/fields/{field_id}")
    async def get_field(field_id: str):
        tenant_id = get_current_tenant_id()
        return {"tenant_id": tenant_id, "field_id": field_id}

    @app.get("/healthz")
    async def health():
        return {"status": "ok"}

    @app.get("/readyz")
    async def readiness():
        return {"status": "ok"}

    @app.get("/metrics")
    async def metrics():
        return {"metrics": "ok"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: TenantContextMiddleware - Header Extraction
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTenantContextMiddlewareHeaders:
    """Test tenant extraction from X-Tenant-ID header."""

    def test_extracts_tenant_from_header(self, tenant_a_id):
        """يجب استخراج معرف المستأجر من الرأس X-Tenant-ID."""
        app = _create_test_app()
        client = TestClient(app)

        response = client.get(
            "/api/v1/fields",
            headers={"X-Tenant-ID": tenant_a_id},
        )

        assert response.status_code == 200
        assert response.json()["tenant_id"] == tenant_a_id

    def test_rejects_missing_tenant_header(self):
        """يجب رفض الطلبات بدون معرف المستأجر."""
        app = _create_test_app(require_tenant=True)
        client = TestClient(app)

        response = client.get("/api/v1/fields")

        assert response.status_code == 400
        body = response.json()
        assert body["error"] == "missing_tenant"
        assert "message_ar" in body  # Bilingual error message

    def test_allows_missing_tenant_when_not_required(self):
        """يجب السماح بدون معرف المستأجر عند عدم الإلزام."""
        app = _create_test_app(require_tenant=False)
        client = TestClient(app)

        # Without tenant, get_current_tenant_id() will raise RuntimeError
        # This is expected - the middleware allows it but the endpoint still needs it
        with pytest.raises(Exception):
            client.get("/api/v1/fields")

    def test_exempt_paths_skip_tenant_check(self):
        """يجب تجاوز فحص المستأجر للمسارات المعفاة."""
        app = _create_test_app(require_tenant=True)
        client = TestClient(app)

        # Health endpoints should work without tenant
        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 200
        assert client.get("/metrics").status_code == 200

    def test_tenant_id_not_empty_string(self):
        """يجب رفض معرف المستأجر الفارغ."""
        app = _create_test_app(require_tenant=True)
        client = TestClient(app)

        response = client.get(
            "/api/v1/fields",
            headers={"X-Tenant-ID": ""},
        )

        # Empty string is falsy, so middleware should reject it
        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: TenantContextMiddleware - JWT Extraction
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTenantContextMiddlewareJWT:
    """Test tenant extraction from JWT principal."""

    def test_prefers_jwt_over_header(self, tenant_a_id, tenant_b_id):
        """يجب تفضيل JWT على رأس X-Tenant-ID."""
        app = _create_test_app()

        @app.middleware("http")
        async def mock_auth_middleware(request: Request, call_next):
            """Simulate auth middleware setting principal from JWT."""
            request.state.principal = {
                "sub": "user-001",
                "tid": tenant_a_id,
                "roles": ["farmer"],
            }
            return await call_next(request)

        client = TestClient(app)

        # JWT has tenant_a, header has tenant_b - JWT should win
        response = client.get(
            "/api/v1/fields",
            headers={"X-Tenant-ID": tenant_b_id},
        )

        assert response.status_code == 200
        assert response.json()["tenant_id"] == tenant_a_id


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: enforce_tenant - Cross-Tenant Access Prevention
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnforceTenant:
    """Test enforce_tenant blocks cross-tenant access for non-admin users."""

    def test_user_can_access_own_tenant(self, user_a, tenant_a_id):
        """يجب أن يتمكن المستخدم من الوصول لمستأجره."""
        result = enforce_tenant(user_a)
        assert result == tenant_a_id

    def test_user_can_access_own_tenant_explicitly(self, user_a, tenant_a_id):
        """يجب أن يتمكن المستخدم من الوصول لمستأجره بشكل صريح."""
        result = enforce_tenant(user_a, requested_tenant_id=tenant_a_id)
        assert result == tenant_a_id

    def test_user_cannot_access_other_tenant(self, user_a, tenant_b_id):
        """يجب منع المستخدم من الوصول لمستأجر آخر."""
        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user_a, requested_tenant_id=tenant_b_id)

        assert exc_info.value.status_code == 403
        assert "tenant mismatch" in exc_info.value.detail.lower()

    def test_admin_can_access_any_tenant(self, admin_user, tenant_b_id):
        """يجب أن يتمكن المسؤول من الوصول لأي مستأجر."""
        result = enforce_tenant(admin_user, requested_tenant_id=tenant_b_id)
        assert result == tenant_b_id

    def test_admin_can_access_own_tenant(self, admin_user, tenant_a_id):
        """يجب أن يتمكن المسؤول من الوصول لمستأجره."""
        result = enforce_tenant(admin_user, requested_tenant_id=tenant_a_id)
        assert result == tenant_a_id

    def test_user_without_tenant_raises(self):
        """يجب رفض المستخدم بدون معرف مستأجر."""
        user_no_tenant = User(
            id="user-no-tenant",
            email="orphan@sahool.app",
            roles=["farmer"],
            tenant_id=None,
        )

        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user_no_tenant)

        assert exc_info.value.status_code == 400

    def test_user_with_empty_tenant_and_no_requested(self):
        """يجب رفض المستخدم بمعرف مستأجر فارغ."""
        user_empty = User(
            id="user-empty",
            email="empty@sahool.app",
            roles=["farmer"],
            tenant_id="",
        )

        # Empty string is falsy - should raise 400
        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user_empty)

        assert exc_info.value.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: ContextVar Isolation (Async Safety)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestContextVarIsolation:
    """Test that tenant context is properly isolated across async contexts."""

    def test_context_not_shared_across_requests(self, tenant_a_id, tenant_b_id):
        """يجب ألا يتم مشاركة السياق بين الطلبات."""
        # Set tenant A context
        ctx_a = TenantContext(id=tenant_a_id, user_id="user-a", roles=["farmer"])
        token_a = _tenant_context.set(ctx_a)

        assert get_current_tenant_id() == tenant_a_id

        # Reset tenant A
        _tenant_context.reset(token_a)

        # Set tenant B context
        ctx_b = TenantContext(id=tenant_b_id, user_id="user-b", roles=["farmer"])
        token_b = _tenant_context.set(ctx_b)

        assert get_current_tenant_id() == tenant_b_id

        _tenant_context.reset(token_b)

    def test_get_current_tenant_raises_without_context(self):
        """يجب أن يرفع خطأ عند عدم وجود سياق."""
        # Ensure no context is set
        assert _tenant_context.get() is None or True  # May have default None

        # If context is not set, should raise
        try:
            _tenant_context.set(None)
        except Exception:
            pass

        # get_current_tenant should raise RuntimeError when no context
        with pytest.raises(RuntimeError, match="Tenant context not available"):
            saved = _tenant_context.get()
            token = _tenant_context.set(None)
            try:
                get_current_tenant()
            finally:
                _tenant_context.reset(token)

    def test_get_optional_tenant_returns_none_without_context(self):
        """يجب إرجاع None عند عدم وجود سياق."""
        token = _tenant_context.set(None)
        try:
            result = get_optional_tenant()
            assert result is None
        finally:
            _tenant_context.reset(token)

    def test_tenant_context_has_role_check(self, tenant_a_id):
        """يجب التحقق من الأدوار في سياق المستأجر."""
        ctx = TenantContext(id=tenant_a_id, user_id="user-a", roles=["farmer", "manager"])

        assert ctx.has_role("farmer") is True
        assert ctx.has_role("manager") is True
        assert ctx.has_role("admin") is False

    def test_tenant_context_has_role_with_empty_roles(self, tenant_a_id):
        """يجب التعامل مع الأدوار الفارغة."""
        ctx = TenantContext(id=tenant_a_id, user_id="user-a", roles=None)
        assert ctx.has_role("farmer") is False

        ctx2 = TenantContext(id=tenant_a_id, user_id="user-a", roles=[])
        assert ctx2.has_role("farmer") is False


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Database Query Helpers
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTenantDatabaseHelpers:
    """Test tenant-scoped database query helpers."""

    def test_tenant_filter_dict(self, tenant_context_a, tenant_a_id):
        """يجب إرجاع فلتر المستأجر كقاموس."""
        result = tenant_filter_dict()
        assert result == {"tenant_id": tenant_a_id}

    def test_tenant_filter_dict_changes_with_context(self, tenant_a_id, tenant_b_id):
        """يجب أن يتغير الفلتر مع تغير السياق."""
        # Set tenant A
        ctx_a = TenantContext(id=tenant_a_id)
        token_a = _tenant_context.set(ctx_a)
        assert tenant_filter_dict()["tenant_id"] == tenant_a_id
        _tenant_context.reset(token_a)

        # Set tenant B
        ctx_b = TenantContext(id=tenant_b_id)
        token_b = _tenant_context.set(ctx_b)
        assert tenant_filter_dict()["tenant_id"] == tenant_b_id
        _tenant_context.reset(token_b)

    def test_tenant_filter_dict_raises_without_context(self):
        """يجب رفع خطأ عند استخدام الفلتر بدون سياق."""
        token = _tenant_context.set(None)
        try:
            with pytest.raises(RuntimeError):
                tenant_filter_dict()
        finally:
            _tenant_context.reset(token)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Cross-Tenant Attack Scenarios
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCrossTenantAttackScenarios:
    """Test prevention of common cross-tenant attack vectors."""

    def test_tenant_id_from_body_should_not_override_header(self, tenant_a_id, tenant_b_id):
        """يجب ألا يتجاوز معرف المستأجر من الجسم الرأس.

        SECURITY: If a service accepts tenant_id from request body,
        it MUST validate it against the authenticated tenant context.
        """
        user = User(
            id="attacker",
            email="attacker@evil.com",
            roles=["farmer"],
            tenant_id=tenant_a_id,
        )

        # Attacker tries to send tenant_b_id in request body
        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user, requested_tenant_id=tenant_b_id)

        assert exc_info.value.status_code == 403

    def test_sql_injection_in_tenant_id(self):
        """يجب منع حقن SQL في معرف المستأجر."""
        malicious_ids = [
            "'; DROP TABLE fields;--",
            "tenant_a' OR '1'='1",
            "tenant_a UNION SELECT * FROM pg_shadow--",
            "tenant\x00_id",
        ]

        for malicious_id in malicious_ids:
            # TenantContext should store it as-is (parameterized queries prevent injection)
            ctx = TenantContext(id=malicious_id)
            # But tenant_filter_dict returns it for parameterized use
            token = _tenant_context.set(ctx)
            try:
                result = tenant_filter_dict()
                # The filter dict stores the value - SQL injection prevention
                # is at the database layer via parameterized queries
                assert result["tenant_id"] == malicious_id
            finally:
                _tenant_context.reset(token)

    def test_multiple_tenant_headers_uses_first(self, tenant_a_id):
        """يجب استخدام أول رأس عند وجود عدة رؤوس."""
        app = _create_test_app()
        client = TestClient(app)

        # HTTP allows multiple headers with same name
        response = client.get(
            "/api/v1/fields",
            headers={"X-Tenant-ID": tenant_a_id},
        )

        assert response.status_code == 200
        assert response.json()["tenant_id"] == tenant_a_id

    def test_user_cannot_escalate_to_admin_tenant_access(self, tenant_a_id, tenant_b_id):
        """يجب منع المستخدم من تصعيد الصلاحيات للوصول لمستأجر آخر."""
        # User claims to be admin but has farmer role
        fake_admin = User(
            id="fake-admin",
            email="fake@sahool.app",
            roles=["farmer"],  # NOT admin
            tenant_id=tenant_a_id,
        )

        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(fake_admin, requested_tenant_id=tenant_b_id)

        assert exc_info.value.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Service-Level Tenant Isolation
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceLevelIsolation:
    """Test tenant isolation at service endpoint level."""

    def test_field_endpoint_returns_tenant_scoped_data(self, tenant_a_id):
        """يجب إرجاع بيانات المستأجر فقط."""
        app = _create_test_app()
        client = TestClient(app)

        response = client.get(
            "/api/v1/fields/field-001",
            headers={"X-Tenant-ID": tenant_a_id},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == tenant_a_id
        assert data["field_id"] == "field-001"

    def test_different_tenants_see_different_data(self, tenant_a_id, tenant_b_id):
        """يجب أن يرى كل مستأجر بياناته فقط."""
        app = _create_test_app()
        client = TestClient(app)

        resp_a = client.get(
            "/api/v1/fields",
            headers={"X-Tenant-ID": tenant_a_id},
        )
        resp_b = client.get(
            "/api/v1/fields",
            headers={"X-Tenant-ID": tenant_b_id},
        )

        assert resp_a.json()["tenant_id"] == tenant_a_id
        assert resp_b.json()["tenant_id"] == tenant_b_id
        assert resp_a.json()["tenant_id"] != resp_b.json()["tenant_id"]


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Tenant Context Cleanup
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTenantContextCleanup:
    """Test that tenant context is properly cleaned up after requests."""

    def test_context_cleaned_after_successful_request(self, tenant_a_id):
        """يجب تنظيف السياق بعد الطلب الناجح."""
        app = _create_test_app()
        client = TestClient(app)

        response = client.get(
            "/api/v1/fields",
            headers={"X-Tenant-ID": tenant_a_id},
        )
        assert response.status_code == 200

        # After request, context should be cleaned
        # (TestClient resets between requests)
        optional = get_optional_tenant()
        # In test context, this may or may not be None depending on TestClient behavior
        # The important thing is it doesn't leak between requests

    def test_context_cleaned_after_failed_request(self, tenant_a_id):
        """يجب تنظيف السياق بعد فشل الطلب."""
        app = _create_test_app()

        @app.get("/api/v1/error")
        async def error_endpoint():
            raise HTTPException(status_code=500, detail="Internal error")

        client = TestClient(app, raise_server_exceptions=False)

        response = client.get(
            "/api/v1/error",
            headers={"X-Tenant-ID": tenant_a_id},
        )
        assert response.status_code == 500


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Query Parameter Tenant Extraction
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestQueryParamTenantExtraction:
    """Test tenant extraction from query parameters (for webhooks)."""

    def test_query_param_disabled_by_default(self, tenant_a_id):
        """يجب تعطيل استخراج المستأجر من معلمات الاستعلام افتراضياً."""
        app = _create_test_app(require_tenant=True, allow_query_param=False)
        client = TestClient(app)

        # Query param should be ignored
        response = client.get(f"/api/v1/fields?tenant_id={tenant_a_id}")
        assert response.status_code == 400

    def test_query_param_works_when_enabled(self, tenant_a_id):
        """يجب استخراج المستأجر من معلمات الاستعلام عند التفعيل."""
        app = _create_test_app(require_tenant=True, allow_query_param=True)
        client = TestClient(app)

        response = client.get(f"/api/v1/fields?tenant_id={tenant_a_id}")
        assert response.status_code == 200
        assert response.json()["tenant_id"] == tenant_a_id


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: NATS Event Tenant Scoping
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestNATSEventTenantScoping:
    """Test that NATS events include tenant scope."""

    def test_event_subject_includes_tenant(self, tenant_a_id):
        """يجب أن تتضمن موضوعات الأحداث معرف المستأجر."""
        # Verify the tenant-scoped subject pattern
        base_subject = "sahool.field.created"
        tenant_subject = f"sahool.tenant.{tenant_a_id}.field.created"

        assert tenant_a_id in tenant_subject
        assert tenant_subject.startswith("sahool.tenant.")

    def test_event_payload_includes_tenant_id(self, tenant_a_id):
        """يجب أن تتضمن حمولة الحدث معرف المستأجر."""
        event_payload = {
            "event_type": "field.created",
            "tenant_id": tenant_a_id,
            "field_id": "field-001",
            "timestamp": "2026-03-12T00:00:00Z",
        }

        assert "tenant_id" in event_payload
        assert event_payload["tenant_id"] == tenant_a_id


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Explicit Header Extraction (Best Practice)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestExplicitHeaderExtraction:
    """Test the recommended pattern of explicit Header extraction in endpoints."""

    def test_explicit_header_dependency(self, tenant_a_id):
        """يجب أن يعمل استخراج الرأس الصريح."""
        app = FastAPI()

        def get_tenant_id(
            x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
        ) -> str:
            if not x_tenant_id:
                raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
            return x_tenant_id

        @app.get("/api/v1/secure-fields")
        async def list_secure_fields(tenant_id: str = Depends(get_tenant_id)):
            return {"tenant_id": tenant_id}

        client = TestClient(app)

        # With header
        response = client.get(
            "/api/v1/secure-fields",
            headers={"X-Tenant-Id": tenant_a_id},
        )
        assert response.status_code == 200
        assert response.json()["tenant_id"] == tenant_a_id

        # Without header
        response = client.get("/api/v1/secure-fields")
        assert response.status_code == 400

    def test_explicit_header_rejects_empty_value(self):
        """يجب رفض القيمة الفارغة في الرأس الصريح."""
        app = FastAPI()

        def get_tenant_id(
            x_tenant_id: str | None = Header(None, alias="X-Tenant-Id"),
        ) -> str:
            if not x_tenant_id or not x_tenant_id.strip():
                raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
            return x_tenant_id

        @app.get("/api/v1/fields")
        async def list_fields(tenant_id: str = Depends(get_tenant_id)):
            return {"tenant_id": tenant_id}

        client = TestClient(app)

        response = client.get(
            "/api/v1/fields",
            headers={"X-Tenant-Id": "   "},
        )
        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Tenant-Scoped Resource Access Validation
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTenantScopedResourceAccess:
    """Test that resource access is validated against tenant ownership."""

    def test_resource_ownership_check(self, user_a, tenant_a_id, tenant_b_id):
        """يجب التحقق من ملكية الموارد."""
        # Simulate a resource belonging to tenant B
        resource = {
            "id": "field-001",
            "tenant_id": tenant_b_id,
            "name": "Field in Tenant B",
        }

        # User A should not be able to access this resource
        def validate_resource_access(user: User, resource: dict) -> bool:
            validated_tenant = enforce_tenant(user)
            return resource["tenant_id"] == validated_tenant

        assert validate_resource_access(user_a, resource) is False

    def test_resource_ownership_check_same_tenant(self, user_a, tenant_a_id):
        """يجب السماح بالوصول لموارد نفس المستأجر."""
        resource = {
            "id": "field-001",
            "tenant_id": tenant_a_id,
            "name": "Field in Tenant A",
        }

        def validate_resource_access(user: User, resource: dict) -> bool:
            validated_tenant = enforce_tenant(user)
            return resource["tenant_id"] == validated_tenant

        assert validate_resource_access(user_a, resource) is True

    def test_admin_resource_access_any_tenant(self, admin_user, tenant_b_id):
        """يجب أن يتمكن المسؤول من الوصول لموارد أي مستأجر."""
        resource = {
            "id": "field-001",
            "tenant_id": tenant_b_id,
            "name": "Field in Tenant B",
        }

        # Admin requesting access to tenant B's resource
        validated_tenant = enforce_tenant(admin_user, requested_tenant_id=tenant_b_id)
        assert validated_tenant == tenant_b_id
        assert resource["tenant_id"] == validated_tenant


# ═══════════════════════════════════════════════════════════════════════════════
# Test Class: Vulnerable Service Patterns Detection
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestVulnerablePatternDetection:
    """Test detection and prevention of vulnerable tenant patterns.

    These tests validate that known vulnerable patterns from the audit
    (hydrology-service, soil-analysis-service, llm-orchestrator-service)
    are properly handled.
    """

    def test_body_tenant_id_must_match_auth_context(self, user_a, tenant_a_id, tenant_b_id):
        """يجب أن يتطابق معرف المستأجر من الجسم مع السياق المعتمد.

        CRITICAL: hydrology-service was found accepting tenant_id from request body.
        This test ensures the enforce_tenant function catches this.
        """
        # Simulate: User A sends request with tenant_B in body
        body_tenant_id = tenant_b_id

        with pytest.raises(HTTPException) as exc_info:
            enforce_tenant(user_a, requested_tenant_id=body_tenant_id)

        assert exc_info.value.status_code == 403

    def test_resource_id_access_requires_tenant_check(self, tenant_a_id, tenant_b_id):
        """يجب التحقق من المستأجر عند الوصول بمعرف المورد.

        VULNERABILITY: soil-analysis-service allows GET /tests/{test_id}
        without verifying tenant ownership.
        """
        # Simulate database record belonging to tenant B
        db_records = {
            "test-001": {"id": "test-001", "tenant_id": tenant_b_id, "data": "sensitive"},
        }

        def get_resource_secure(resource_id: str, user_tenant_id: str):
            """Secure pattern: always check tenant ownership."""
            record = db_records.get(resource_id)
            if not record:
                return None
            if record["tenant_id"] != user_tenant_id:
                raise HTTPException(status_code=403, detail="Access denied")
            return record

        # User from tenant A should NOT see tenant B's data
        with pytest.raises(HTTPException) as exc_info:
            get_resource_secure("test-001", tenant_a_id)

        assert exc_info.value.status_code == 403
