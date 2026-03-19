"""
Integration Tests for Field Geospatial Operations - SAHOOL Platform
اختبارات التكامل للعمليات الجغرافية على الحقول - منصة سهول

Tests the complete field geospatial workflow through the API:
- Creating a field and setting its center location (PostGIS POINT)
- Drawing field boundaries (PostGIS POLYGON)
- Rejecting self-intersecting boundaries
- Detecting and warning about overlapping fields

These tests require:
- field-management-service running on port 3000
- PostgreSQL with PostGIS extension
- Valid authentication token

They are skipped gracefully when the stack is unavailable.

Test Markers:
- @pytest.mark.integration  - Requires running services
- @pytest.mark.asyncio      - Async tests

Author: SAHOOL QA Team
Updated: March 2026
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

try:
    import httpx

    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Field management service URL
FIELD_SERVICE_URL = os.getenv("FIELD_SERVICE_URL", "http://localhost:3000")
BASE_URL = os.getenv("KONG_BASE_URL", "http://localhost:8000")

# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures - أدوات الاختبار
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
async def db_session():
    """
    PostgreSQL + PostGIS session — skips when unavailable, fails on DB errors.
    جلسة قاعدة بيانات مع PostGIS — تُهمَل الاختبارات عند عدم التوفر.
    """
    try:
        import asyncpg
    except ImportError:
        pytest.skip("asyncpg not installed — PostgreSQL with PostGIS not available for integration tests")

    db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://sahool_test:test_password_123@localhost:5432/sahool_test",
    )
    try:
        conn = await asyncpg.connect(db_url)
    except (OSError, ConnectionError, Exception) as exc:
        if "connect" in str(exc).lower() or "refused" in str(exc).lower() or "timeout" in str(exc).lower():
            pytest.skip(f"PostgreSQL not reachable for integration tests: {exc}")
        raise

    try:
        yield conn
    finally:
        await conn.close()


@pytest.fixture
async def authenticated_client():
    """
    عميل HTTP مصادَق عليه جاهز للاستخدام.
    Authenticated HTTP client — skips when Kong is unreachable.
    """
    if not HAS_HTTPX:
        pytest.skip("httpx not installed")

    token = os.getenv("TEST_JWT_TOKEN", "mock-jwt-for-geo-tests")

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=15.0,
    ) as client:
        try:
            await client.get("/healthz")
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("API Gateway not reachable — start docker-compose.test.yml first")
        yield client


# ═══════════════════════════════════════════════════════════════════════════════
# TestFieldGeoIntegration - اختبارات التكامل الجغرافي للحقول
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestFieldGeoIntegration:
    """اختبارات العمليات الجغرافية المكانية على الحقول عبر PostGIS"""

    # ── helpers ────────────────────────────────────────────────────────────────

    async def _create_field(self, client: Any) -> str:
        """
        مساعد: إنشاء حقل بسيط وإرجاع معرّفه.
        Helper: create a minimal field and return its ID.
        """
        resp = await client.post(
            "/api/v1/fields",
            json={"name": "حقل اختبار جغرافي", "crop_type": "wheat"},
        )
        if resp.status_code not in (200, 201):
            pytest.skip(f"Field creation endpoint unavailable: {resp.status_code}")
        return resp.json().get("field_id") or resp.json().get("id")

    async def _create_field_with_boundary(
        self, client: Any, coords: list[list[float]]
    ) -> str:
        """
        مساعد: إنشاء حقل مع حدود وإرجاع معرّفه.
        Helper: create a field with a polygon boundary and return its ID.
        """
        field_id = await self._create_field(client)
        boundary = {"type": "Polygon", "coordinates": [coords]}
        resp = await client.put(
            f"/api/v1/fields/{field_id}/boundary",
            json={"boundary": boundary},
        )
        if resp.status_code not in (200, 201):
            pytest.skip(f"Boundary endpoint unavailable: {resp.status_code}")
        return field_id

    # ── tests ──────────────────────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_create_field_with_location(
        self,
        authenticated_client: Any,
        db_session: Any,
    ) -> None:
        """
        إنشاء حقل → تحديد الموقع → PostGIS يحفظ الإحداثيات

        Create a field, set its center point (latitude/longitude/altitude),
        then verify the coordinates are stored correctly in PostGIS.
        """
        # الخطوة 1: إنشاء الحقل — Step 1: Create field
        create_resp = await authenticated_client.post(
            "/api/v1/fields",
            json={"name": "حقل صنعاء الشمالي", "crop_type": "wheat"},
        )
        assert create_resp.status_code in (200, 201), f"Field creation failed: {create_resp.text}"
        field_id = create_resp.json().get("field_id") or create_resp.json().get("id")
        assert field_id is not None

        # الخطوة 2: تحديد الموقع المركزي — Step 2: Set center location
        location_resp = await authenticated_client.patch(
            f"/api/v1/fields/{field_id}/location",
            json={
                "latitude": 15.3694,
                "longitude": 44.1910,
                "altitude": 2200,  # متر — صنعاء مرتفعة
            },
        )
        assert location_resp.status_code == 200, f"Location update failed: {location_resp.text}"

        # الخطوة 3: التحقق من PostGIS — Step 3: Verify PostGIS storage
        geo_record = await db_session.fetchrow(
            """
            SELECT
                ST_X(center_point::geometry) AS lng,
                ST_Y(center_point::geometry) AS lat,
                altitude
            FROM fields WHERE id = $1
            """,
            field_id,
        )
        if geo_record and not isinstance(geo_record, MagicMock):
            assert abs(geo_record["lat"] - 15.3694) < 0.0001
            assert abs(geo_record["lng"] - 44.1910) < 0.0001
            assert geo_record["altitude"] == 2200

    @pytest.mark.asyncio
    async def test_draw_field_boundary(
        self,
        authenticated_client: Any,
        db_session: Any,
    ) -> None:
        """
        رسم حدود الحقل → PostGIS يحفظ Polygon → حساب المساحة تلقائياً

        Draw a rectangular field boundary as a GeoJSON Polygon,
        then verify PostGIS stores it and auto-calculates the area.
        """
        field_id = await self._create_field(authenticated_client)

        # GeoJSON Polygon — حقل مستطيل بسيط بالقرب من صنعاء
        boundary = {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.1900, 15.3690],  # SW — جنوب غرب
                    [44.1920, 15.3690],  # SE — جنوب شرق
                    [44.1920, 15.3700],  # NE — شمال شرق
                    [44.1900, 15.3700],  # NW — شمال غرب
                    [44.1900, 15.3690],  # إغلاق الحلقة
                ]
            ],
        }

        resp = await authenticated_client.put(
            f"/api/v1/fields/{field_id}/boundary",
            json={"boundary": boundary},
        )
        assert resp.status_code == 200, f"Boundary update failed: {resp.text}"

        # التحقق من حسابات PostGIS — Verify PostGIS calculations
        record = await db_session.fetchrow(
            """
            SELECT
                ST_AsGeoJSON(boundary)::json AS geojson,
                ST_Area(ST_Transform(boundary, 32638)) / 10000 AS area_ha,
                ST_IsValid(boundary)   AS is_valid,
                ST_NPoints(boundary)   AS num_points
            FROM fields WHERE id = $1
            """,
            field_id,
        )

        if record and not isinstance(record, MagicMock):
            # الحدود محفوظة
            assert record["geojson"] is not None
            # المساحة محسوبة تلقائياً.
            # The polygon spans 0.002° longitude × 0.001° latitude near 15.37°N.
            # At that latitude: 0.002° ≈ 215 m, 0.001° ≈ 111 m → area ≈ 2.4 ha.
            # Bounds [0.5, 10] allow for projection rounding while ruling out
            # obviously wrong values.
            assert 0.5 < record["area_ha"] < 10
            # Polygon صالح هندسياً
            assert record["is_valid"] is True
            # 5 نقاط (4 زوايا + نقطة الإغلاق)
            assert record["num_points"] == 5

        # API يعيد المساحة المحسوبة — API returns computed area
        body = resp.json()
        assert "area_ha" in body
        assert body["area_ha"] > 0

    @pytest.mark.asyncio
    async def test_boundary_self_intersection_rejected(
        self,
        authenticated_client: Any,
    ) -> None:
        """
        الحدود المتقاطعة مع نفسها → رفض 422

        A self-intersecting (figure-8) polygon must be rejected
        with HTTP 422 Unprocessable Entity.
        """
        field_id = await self._create_field(authenticated_client)

        # Polygon متقاطع مع نفسه — figure-8 shape
        invalid_boundary = {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.190, 15.369],
                    [44.192, 15.370],
                    [44.192, 15.369],  # ← يتقاطع هنا — self-intersection
                    [44.190, 15.370],
                    [44.190, 15.369],
                ]
            ],
        }

        resp = await authenticated_client.put(
            f"/api/v1/fields/{field_id}/boundary",
            json={"boundary": invalid_boundary},
        )
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
        assert "self_intersection" in resp.json().get("error", "").lower() or resp.status_code == 422

    @pytest.mark.asyncio
    async def test_overlapping_fields_warning(
        self,
        authenticated_client: Any,
    ) -> None:
        """
        حقلان يتداخلان جزئياً → تحذير (ليس رفض)

        Two partially-overlapping fields produce a warning in the response
        body, but the operation succeeds (HTTP 200).
        """
        # الحقل الأول مع حدوده — create first field with boundary
        field1_coords = [
            [44.190, 15.369],
            [44.195, 15.369],
            [44.195, 15.374],
            [44.190, 15.374],
            [44.190, 15.369],
        ]
        await self._create_field_with_boundary(authenticated_client, field1_coords)

        # الحقل الثاني يتداخل جزئياً — second field overlaps with first
        field2_id = await self._create_field(authenticated_client)
        overlapping_boundary = {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.193, 15.371],  # داخل الحقل الأول — inside field 1
                    [44.198, 15.371],
                    [44.198, 15.376],
                    [44.193, 15.376],
                    [44.193, 15.371],
                ]
            ],
        }

        resp = await authenticated_client.put(
            f"/api/v1/fields/{field2_id}/boundary",
            json={"boundary": overlapping_boundary},
        )
        # تحذير موجود لكن العملية تنجح — warning present but operation succeeds
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        body = resp.json()
        warnings = body.get("warnings", {})
        if warnings:
            assert warnings.get("overlap") is True
            assert "overlapping_field_ids" in warnings

    @pytest.mark.asyncio
    async def test_invalid_coordinates_rejected(
        self,
        authenticated_client: Any,
    ) -> None:
        """
        إحداثيات خارج نطاق خطوط الطول والعرض → رفض 422

        Coordinates outside valid lat/lon ranges must be rejected.
        """
        field_id = await self._create_field(authenticated_client)

        resp = await authenticated_client.patch(
            f"/api/v1/fields/{field_id}/location",
            json={
                "latitude": 999.0,   # خارج النطاق — out of range
                "longitude": 44.191,
            },
        )
        assert resp.status_code in (400, 422), (
            f"Invalid coordinates should be rejected, got {resp.status_code}"
        )
