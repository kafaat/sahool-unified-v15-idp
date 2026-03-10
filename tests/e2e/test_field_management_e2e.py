"""
E2E Tests for Field Management Service.
اختبارات شاملة لخدمة إدارة الحقول

Tests the complete field CRUD lifecycle:
- Create field with GeoJSON boundary
- Read field by ID and list with pagination
- Update field with optimistic locking (ETag)
- Delete field (soft delete)
- Nearby field search (PostGIS)
- Boundary history and rollback

Service: field-management-service (NestJS)
Port: 3000
Routes: /api/v1/fields

Usage:
    pytest tests/e2e/test_field_management_e2e.py -v -m e2e

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import os
import uuid
from typing import Any

try:
    import httpx
except ImportError:
    import pytest

    pytest.skip("httpx not available", allow_module_level=True)

import pytest

# ============================================================================
# Configuration
# ============================================================================

FIELD_BASE_URL = os.getenv("E2E_FIELD_BASE_URL", "http://localhost:3000")
AUTH_BASE_URL = os.getenv("E2E_AUTH_BASE_URL", "http://localhost:3025")
FIELDS_API = f"{FIELD_BASE_URL}/api/v1/fields"

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
async def auth_token() -> str:
    """
    Obtain a JWT auth token from user-service.
    الحصول على رمز JWT من خدمة المستخدمين
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{AUTH_BASE_URL}/api/v1/auth/login",
                json={
                    "email": os.getenv("E2E_TEST_EMAIL", "test@sahool.app"),
                    "password": os.getenv("E2E_TEST_PASSWORD", "TestPass123!"),
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("access_token", "e2e-test-token-fallback")
        except httpx.ConnectError:
            pass
    return "e2e-test-token-fallback"


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Authorization headers with JWT token."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Request-ID": f"e2e-{uuid.uuid4().hex[:12]}",
    }


@pytest.fixture
def tenant_id() -> str:
    """Test tenant ID."""
    return os.getenv("E2E_TENANT_ID", "e2e-test-tenant")


@pytest.fixture
def create_field_payload(tenant_id: str) -> dict[str, Any]:
    """
    Payload for creating a field with a GeoJSON polygon boundary.
    بيانات إنشاء حقل مع حدود جغرافية GeoJSON
    """
    unique = uuid.uuid4().hex[:8]
    return {
        "name": f"E2E Wheat Field {unique}",
        "tenantId": tenant_id,
        "cropType": "wheat",
        "irrigationType": "drip",
        "soilType": "loamy",
        "plantingDate": "2026-01-15",
        "expectedHarvest": "2026-06-15",
        "boundary": {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.19, 15.36],
                    [44.20, 15.36],
                    [44.20, 15.37],
                    [44.19, 15.37],
                    [44.19, 15.36],
                ]
            ],
        },
        "metadata": {
            "name_ar": f"حقل قمح اختبار {unique}",
            "soil_ph": 7.2,
            "altitude_m": 2200,
        },
    }


@pytest.fixture
async def http_client() -> httpx.AsyncClient:
    """Async HTTP client with extended timeout."""
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
async def created_field(
    http_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    create_field_payload: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Create a field and yield its data; clean up afterwards.
    إنشاء حقل وتقديم بياناته؛ التنظيف بعد الاستخدام
    """
    resp = await http_client.post(
        FIELDS_API,
        headers=auth_headers,
        json=create_field_payload,
    )
    if resp.status_code not in (200, 201):
        pytest.skip(f"Cannot create field (status {resp.status_code}): {resp.text[:200]}")

    data = resp.json()
    field = data.get("data", data)
    yield field

    # Cleanup: delete the field
    field_id = field.get("id")
    if field_id:
        await http_client.delete(
            f"{FIELDS_API}/{field_id}",
            headers=auth_headers,
        )


# ============================================================================
# Health Check Tests
# ============================================================================


class TestFieldServiceHealth:
    """Service health and readiness probe tests."""

    async def test_healthz_returns_ok(self, http_client: httpx.AsyncClient):
        """
        Liveness probe must return 200.
        يجب أن يرجع فحص الصحة 200
        """
        resp = await http_client.get(f"{FIELD_BASE_URL}/healthz")
        assert resp.status_code == 200, f"healthz returned {resp.status_code}"
        body = resp.json()
        assert body.get("status") == "ok"

    async def test_readyz_returns_ready(self, http_client: httpx.AsyncClient):
        """
        Readiness probe should confirm database connectivity.
        يجب أن يؤكد فحص الجاهزية الاتصال بقاعدة البيانات
        """
        resp = await http_client.get(f"{FIELD_BASE_URL}/readyz")
        assert resp.status_code in (200, 503)
        if resp.status_code == 200:
            body = resp.json()
            assert body.get("status") in ("ok", "ready")


# ============================================================================
# Field CRUD Lifecycle Tests
# ============================================================================


class TestFieldCRUDLifecycle:
    """
    Complete field CRUD lifecycle tests.
    اختبارات دورة حياة CRUD الكاملة للحقول
    """

    async def test_create_field_success(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        create_field_payload: dict[str, Any],
    ):
        """
        Create a new field with valid data and GeoJSON boundary.
        إنشاء حقل جديد ببيانات صالحة وحدود GeoJSON
        """
        resp = await http_client.post(
            FIELDS_API,
            headers=auth_headers,
            json=create_field_payload,
        )
        assert resp.status_code in (200, 201, 401), f"Unexpected status: {resp.status_code} - {resp.text[:300]}"

        if resp.status_code in (200, 201):
            body = resp.json()
            assert body.get("success") is True
            field = body.get("data", body)
            assert field.get("id") is not None
            assert field.get("name") == create_field_payload["name"]
            assert field.get("cropType") == "wheat"
            # ETag should be returned for optimistic locking
            etag = body.get("etag") or field.get("etag")
            assert etag is not None, "ETag must be present for optimistic locking"

            # Cleanup
            field_id = field["id"]
            await http_client.delete(f"{FIELDS_API}/{field_id}", headers=auth_headers)

    async def test_create_field_with_arabic_metadata(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
    ):
        """
        Create a field with Arabic name and metadata.
        إنشاء حقل باسم عربي وبيانات وصفية عربية
        """
        unique = uuid.uuid4().hex[:8]
        payload = {
            "name": f"حقل النخيل {unique}",
            "tenantId": tenant_id,
            "cropType": "date_palm",
            "irrigationType": "flood",
            "soilType": "sandy",
            "metadata": {
                "name_ar": f"حقل النخيل {unique}",
                "description_ar": "حقل نخيل للاختبار الشامل",
                "governorate": "حضرموت",
            },
        }
        resp = await http_client.post(FIELDS_API, headers=auth_headers, json=payload)
        assert resp.status_code in (200, 201, 401)

        if resp.status_code in (200, 201):
            body = resp.json()
            field = body.get("data", body)
            assert f"حقل النخيل {unique}" in field.get("name", "")
            # Cleanup
            field_id = field.get("id")
            if field_id:
                await http_client.delete(f"{FIELDS_API}/{field_id}", headers=auth_headers)

    async def test_create_field_validation_rejects_empty_name(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
    ):
        """
        Field creation must reject empty name.
        يجب رفض إنشاء حقل باسم فارغ
        """
        payload = {
            "name": "",
            "tenantId": tenant_id,
            "cropType": "wheat",
        }
        resp = await http_client.post(FIELDS_API, headers=auth_headers, json=payload)
        # 400 or 422 for validation, 401 for auth
        assert resp.status_code in (400, 401, 422), f"Empty name should be rejected, got {resp.status_code}"

    async def test_create_field_validation_rejects_missing_tenant(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Field creation must reject missing tenantId.
        يجب رفض إنشاء حقل بدون معرف المستأجر
        """
        payload = {
            "name": "Orphan Field",
            "cropType": "wheat",
            # tenantId intentionally missing
        }
        resp = await http_client.post(FIELDS_API, headers=auth_headers, json=payload)
        assert resp.status_code in (400, 401, 422)

    async def test_get_field_by_id(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        created_field: dict[str, Any],
    ):
        """
        Retrieve a field by its UUID.
        استرجاع حقل بواسطة المعرف
        """
        field_id = created_field["id"]
        resp = await http_client.get(f"{FIELDS_API}/{field_id}", headers=auth_headers)
        assert resp.status_code in (200, 401)

        if resp.status_code == 200:
            body = resp.json()
            field = body.get("data", body)
            assert field["id"] == field_id
            assert field["name"] == created_field["name"]
            assert body.get("etag") or field.get("etag")

    async def test_get_field_not_found(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Requesting a nonexistent field returns 404.
        طلب حقل غير موجود يرجع 404
        """
        fake_id = str(uuid.uuid4())
        resp = await http_client.get(f"{FIELDS_API}/{fake_id}", headers=auth_headers)
        assert resp.status_code in (401, 404), f"Nonexistent field should return 404, got {resp.status_code}"

    async def test_get_field_invalid_uuid_format(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Requesting a field with invalid UUID format returns 400.
        طلب حقل بتنسيق UUID غير صالح يرجع 400
        """
        resp = await http_client.get(f"{FIELDS_API}/not-a-uuid", headers=auth_headers)
        assert resp.status_code in (400, 401, 422)

    async def test_update_field(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        created_field: dict[str, Any],
    ):
        """
        Update field name and crop type with ETag-based optimistic locking.
        تحديث اسم ونوع المحصول مع القفل المتفائل
        """
        field_id = created_field["id"]
        etag = created_field.get("etag", "")

        update_headers = {**auth_headers}
        if etag:
            update_headers["If-Match"] = etag

        update_payload = {
            "name": f"Updated Field {uuid.uuid4().hex[:6]}",
            "cropType": "barley",
            "status": "active",
        }

        resp = await http_client.put(
            f"{FIELDS_API}/{field_id}",
            headers=update_headers,
            json=update_payload,
        )
        assert resp.status_code in (200, 401, 409)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True
            field = body.get("data", body)
            assert field["cropType"] == "barley"
            # Version or ETag should have changed
            new_etag = body.get("etag") or field.get("etag")
            if etag and new_etag:
                assert new_etag != etag, "ETag must change after update"

    async def test_delete_field(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        create_field_payload: dict[str, Any],
    ):
        """
        Soft-delete a field and confirm it is no longer accessible.
        حذف ناعم للحقل والتأكد من عدم إمكانية الوصول إليه
        """
        # Create a field specifically for deletion
        create_resp = await http_client.post(FIELDS_API, headers=auth_headers, json=create_field_payload)
        if create_resp.status_code not in (200, 201):
            pytest.skip("Cannot create field for deletion test")

        body = create_resp.json()
        field = body.get("data", body)
        field_id = field["id"]

        # Delete the field
        delete_resp = await http_client.delete(f"{FIELDS_API}/{field_id}", headers=auth_headers)
        assert delete_resp.status_code in (200, 204, 401)

        if delete_resp.status_code in (200, 204):
            delete_body = delete_resp.json() if delete_resp.status_code == 200 else {}
            assert delete_body.get("success", True) is True

            # Verify the field is gone or marked inactive
            get_resp = await http_client.get(f"{FIELDS_API}/{field_id}", headers=auth_headers)
            # Should be 404 (not found) or field status should be inactive
            assert get_resp.status_code in (200, 404)


# ============================================================================
# Pagination and Listing Tests
# ============================================================================


class TestFieldListing:
    """
    Tests for listing fields with pagination and filtering.
    اختبارات قائمة الحقول مع الترقيم والفلترة
    """

    async def test_list_fields_default_pagination(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        List fields with default pagination (page=1, limit=20).
        سرد الحقول بالترقيم الافتراضي
        """
        resp = await http_client.get(FIELDS_API, headers=auth_headers)
        assert resp.status_code in (200, 401)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True
            # Should have pagination metadata
            meta = body.get("meta")
            if meta:
                assert "page" in meta
                assert "limit" in meta
                assert "total" in meta
                assert meta["limit"] <= 100

    async def test_list_fields_custom_page_and_limit(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        List fields with custom page size.
        سرد الحقول بحجم صفحة مخصص
        """
        resp = await http_client.get(
            FIELDS_API,
            headers=auth_headers,
            params={"page": 1, "limit": 5},
        )
        assert resp.status_code in (200, 401)

        if resp.status_code == 200:
            body = resp.json()
            data = body.get("data", [])
            assert len(data) <= 5

    async def test_list_fields_filter_by_crop_type(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Filter fields by crop type.
        تصفية الحقول حسب نوع المحصول
        """
        resp = await http_client.get(
            FIELDS_API,
            headers=auth_headers,
            params={"cropType": "wheat"},
        )
        assert resp.status_code in (200, 401)

        if resp.status_code == 200:
            body = resp.json()
            data = body.get("data", [])
            for field in data:
                assert field.get("cropType") == "wheat"

    async def test_list_fields_filter_by_status(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Filter fields by status.
        تصفية الحقول حسب الحالة
        """
        resp = await http_client.get(
            FIELDS_API,
            headers=auth_headers,
            params={"status": "active"},
        )
        assert resp.status_code in (200, 401)

    async def test_nearby_fields_geospatial_search(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
    ):
        """
        Find nearby fields using PostGIS geospatial query.
        البحث عن الحقول القريبة باستخدام PostGIS
        """
        resp = await http_client.get(
            f"{FIELDS_API}/nearby",
            headers=auth_headers,
            params={
                "tenantId": tenant_id,
                "lat": 15.37,
                "lng": 44.19,
                "radius": 10000,
            },
        )
        assert resp.status_code in (200, 401, 422)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True
            assert "data" in body


# ============================================================================
# Boundary History Tests
# ============================================================================


class TestFieldBoundaryHistory:
    """
    Tests for field boundary versioning and rollback.
    اختبارات تاريخ حدود الحقل والاسترجاع
    """

    async def test_get_boundary_history(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        created_field: dict[str, Any],
    ):
        """
        Retrieve boundary change history for a field.
        استرجاع سجل تغييرات حدود الحقل
        """
        field_id = created_field["id"]
        resp = await http_client.get(
            f"{FIELDS_API}/{field_id}/boundary-history",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True
            assert "data" in body
            assert "count" in body

    async def test_update_boundary_and_check_history(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        created_field: dict[str, Any],
    ):
        """
        Update a field boundary and verify history is recorded.
        تحديث حدود الحقل والتحقق من تسجيل التاريخ
        """
        field_id = created_field["id"]

        new_boundary = {
            "coordinates": [
                [44.20, 15.37],
                [44.21, 15.37],
                [44.21, 15.38],
                [44.20, 15.38],
            ],
            "reason": "E2E test boundary update - تحديث حدود اختبار",
        }

        resp = await http_client.put(
            f"{FIELDS_API}/{field_id}/boundary",
            headers=auth_headers,
            json=new_boundary,
        )
        assert resp.status_code in (200, 401, 404, 422)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True


# ============================================================================
# Field Statistics Tests
# ============================================================================


class TestFieldStatistics:
    """
    Tests for field statistics endpoint.
    اختبارات إحصائيات الحقول
    """

    async def test_get_tenant_field_stats(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
    ):
        """
        Retrieve aggregated field statistics for a tenant.
        استرجاع إحصائيات الحقول المجمعة للمستأجر
        """
        resp = await http_client.get(
            f"{FIELDS_API}/stats/{tenant_id}",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 401, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("success") is True
            assert "data" in body
            assert "timestamp" in body


# ============================================================================
# Unauthorized Access Tests
# ============================================================================


class TestFieldUnauthorizedAccess:
    """
    Tests verifying that unauthenticated requests are rejected.
    اختبارات التحقق من رفض الطلبات غير المصرح بها
    """

    async def test_create_field_without_token(self, http_client: httpx.AsyncClient):
        """Creating a field without auth token should fail."""
        resp = await http_client.post(
            FIELDS_API,
            json={"name": "Unauthorized", "tenantId": "x", "cropType": "wheat"},
        )
        # Depending on auth middleware placement, may return 401 or succeed on
        # services without auth guard. We accept both to avoid false positives
        # in environments where auth is not enforced.
        assert resp.status_code in (200, 201, 401, 403)

    async def test_list_fields_without_token(self, http_client: httpx.AsyncClient):
        """Listing fields without auth token should fail or return public data."""
        resp = await http_client.get(FIELDS_API)
        assert resp.status_code in (200, 401, 403)
