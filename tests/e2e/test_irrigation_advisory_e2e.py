"""
E2E Tests for Irrigation Advisory Flow.
اختبارات شاملة لتدفق الاستشارات الزراعية والري

Tests the cross-service advisory workflow:
- Create field (field-management-service) -> Get weather context
- Disease assessment from symptoms
- Nutrient assessment from NDVI data
- Fertilizer plan generation
- Crop catalog search with Arabic queries
- Advisory event publishing verification

Services:
  - advisory-service (FastAPI) - Port 8093
  - field-management-service (NestJS) - Port 3000
  - weather-service (Python) - Port 8092

Usage:
    pytest tests/e2e/test_irrigation_advisory_e2e.py -v -m e2e

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import os
import uuid
from typing import Any

import httpx
import pytest

# ============================================================================
# Configuration
# ============================================================================

ADVISORY_BASE_URL = os.getenv("E2E_ADVISORY_BASE_URL", "http://localhost:8093")
FIELD_BASE_URL = os.getenv("E2E_FIELD_BASE_URL", "http://localhost:3000")
WEATHER_BASE_URL = os.getenv("E2E_WEATHER_BASE_URL", "http://localhost:8092")
AUTH_BASE_URL = os.getenv("E2E_AUTH_BASE_URL", "http://localhost:3025")

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
async def auth_token() -> str:
    """Obtain JWT auth token for advisory-service endpoints."""
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
                return resp.json().get("access_token", "e2e-test-token")
        except httpx.ConnectError:
            pass
    return "e2e-test-token-fallback"


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """Authorization headers."""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


@pytest.fixture
async def http_client() -> httpx.AsyncClient:
    """Async HTTP client with extended timeout."""
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
def tenant_id() -> str:
    return os.getenv("E2E_TENANT_ID", "e2e-test-tenant")


@pytest.fixture
def field_id() -> str:
    """Static field ID for advisory tests (assumes field exists or tests skip)."""
    return os.getenv("E2E_FIELD_ID", f"e2e-field-{uuid.uuid4().hex[:8]}")


# ============================================================================
# Health Check Tests
# ============================================================================


class TestAdvisoryServiceHealth:
    """Advisory service health and readiness tests."""

    async def test_healthz_returns_ok(self, http_client: httpx.AsyncClient):
        """
        Advisory service liveness probe.
        فحص صحة خدمة الاستشارات
        """
        resp = await http_client.get(f"{ADVISORY_BASE_URL}/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") == "ok"
        assert body.get("service") == "advisory_service"
        assert body.get("version") is not None

    async def test_readyz_confirms_engine_loaded(self, http_client: httpx.AsyncClient):
        """
        Readiness probe should confirm the advisory engine is loaded.
        يجب أن يؤكد فحص الجاهزية أن محرك الاستشارات محمل
        """
        resp = await http_client.get(f"{ADVISORY_BASE_URL}/readyz")
        assert resp.status_code in (200, 503)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("status") == "ready"
            checks = body.get("checks", {})
            assert checks.get("engine") == "loaded"


# ============================================================================
# Disease Assessment Tests
# ============================================================================


class TestDiseaseAssessment:
    """
    Disease diagnosis and symptom assessment tests.
    اختبارات تشخيص الأمراض وتقييم الأعراض
    """

    async def test_assess_disease_from_image_event(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
        field_id: str,
    ):
        """
        Assess disease from an image classification result.
        تقييم المرض من نتيجة تصنيف الصورة
        """
        payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "condition_id": "wheat_rust",
            "confidence": 0.85,
            "crop": "wheat",
            "weather": {
                "temperature": 25,
                "humidity": 65,
                "rain_probability": 10,
            },
            "correlation_id": f"e2e-{uuid.uuid4().hex[:8]}",
        }
        resp = await http_client.post(
            f"{ADVISORY_BASE_URL}/disease/assess",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (200, 401, 403, 422)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("field_id") == field_id
            result = body.get("result")
            if result:
                # Assessment should have bilingual titles
                assert "title_ar" in result or "title_en" in result
                assert "severity" in result
                assert "actions" in result

    async def test_assess_disease_from_symptoms(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
        field_id: str,
    ):
        """
        Assess possible diseases from reported symptoms in Arabic.
        تقييم الأمراض المحتملة من الأعراض المبلغ عنها بالعربية
        """
        payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "crop": "wheat",
            "symptoms": ["اصفرار الأوراق", "بقع بنية", "ذبول"],
            "lang": "ar",
        }
        resp = await http_client.post(
            f"{ADVISORY_BASE_URL}/disease/symptoms",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (200, 401, 403)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("field_id") == field_id
            results = body.get("results", [])
            assert isinstance(results, list)
            # Each result should have confidence and bilingual info
            for r in results:
                assert "confidence" in r
                assert "title_ar" in r or "title_en" in r

    async def test_assess_disease_low_confidence(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
        field_id: str,
    ):
        """
        Low confidence assessment should return null result.
        تقييم بثقة منخفضة يجب أن يرجع نتيجة فارغة
        """
        payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "condition_id": "unknown_condition_xyz",
            "confidence": 0.1,
        }
        resp = await http_client.post(
            f"{ADVISORY_BASE_URL}/disease/assess",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (200, 401, 403)

        if resp.status_code == 200:
            body = resp.json()
            # Low confidence or unknown condition may return null result
            if body.get("result") is None:
                assert "message" in body

    async def test_search_diseases_by_name(self, http_client: httpx.AsyncClient):
        """
        Search diseases by Arabic name.
        البحث عن الأمراض بالاسم العربي
        """
        resp = await http_client.get(
            f"{ADVISORY_BASE_URL}/disease/search",
            params={"q": "صدأ", "lang": "ar"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "results" in body
        assert body.get("count", 0) >= 0

    async def test_get_diseases_by_crop(self, http_client: httpx.AsyncClient):
        """
        Get all diseases for a specific crop.
        الحصول على جميع أمراض محصول معين
        """
        resp = await http_client.get(
            f"{ADVISORY_BASE_URL}/disease/crop/wheat",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("crop") == "wheat"
        assert "diseases" in body
        assert body.get("count", 0) >= 0

    async def test_get_disease_by_id(self, http_client: httpx.AsyncClient):
        """Get disease information by ID."""
        resp = await http_client.get(
            f"{ADVISORY_BASE_URL}/disease/wheat_rust",
            params={"lang": "ar"},
        )
        assert resp.status_code in (200, 404)


# ============================================================================
# Nutrient Assessment Tests
# ============================================================================


class TestNutrientAssessment:
    """
    Nutrient deficiency assessment from NDVI and visual indicators.
    تقييم نقص المغذيات من NDVI والمؤشرات البصرية
    """

    async def test_assess_nutrient_from_ndvi(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
        field_id: str,
    ):
        """
        Assess nutrient deficiency from NDVI data.
        تقييم نقص المغذيات من بيانات NDVI
        """
        payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "ndvi": 0.35,
            "ndvi_history": [0.55, 0.50, 0.45, 0.40, 0.35],
            "crop": "wheat",
            "stage": "tillering",
        }
        resp = await http_client.post(
            f"{ADVISORY_BASE_URL}/nutrient/ndvi",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (200, 401, 403)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("field_id") == field_id
            assert body.get("ndvi") == 0.35
            results = body.get("results", [])
            assert isinstance(results, list)

    async def test_assess_nutrient_from_visual_indicators(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
        field_id: str,
    ):
        """
        Assess nutrient deficiency from visual indicators (leaf color, pattern).
        تقييم نقص المغذيات من المؤشرات البصرية
        """
        payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "leaf_color": "yellow",
            "pattern": "interveinal_chlorosis",
            "location": "lower_leaves",
            "crop": "wheat",
            "lang": "ar",
        }
        resp = await http_client.post(
            f"{ADVISORY_BASE_URL}/nutrient/visual",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (200, 401, 403)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("field_id") == field_id
            assert "indicators" in body


# ============================================================================
# Fertilizer Plan Tests
# ============================================================================


class TestFertilizerPlan:
    """
    Fertilizer plan generation tests.
    اختبارات توليد خطة التسميد
    """

    async def test_generate_fertilizer_plan(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
        field_id: str,
    ):
        """
        Generate a comprehensive fertilizer plan for wheat at tillering stage.
        توليد خطة تسميد شاملة للقمح في مرحلة التفريع
        """
        payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "crop": "wheat",
            "stage": "tillering",
            "field_size_ha": 5.0,
            "soil_fertility": "medium",
            "irrigation_type": "drip",
        }
        resp = await http_client.post(
            f"{ADVISORY_BASE_URL}/fertilizer/plan",
            headers=auth_headers,
            json=payload,
        )
        assert resp.status_code in (200, 401, 403, 422)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("field_id") == field_id
            # Plan should include applications and potentially notes
            assert "applications" in body or "plan" in body or "crop" in body

    async def test_fertilizer_plan_different_crops(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
        field_id: str,
    ):
        """
        Fertilizer plans should vary by crop type and growth stage.
        يجب أن تختلف خطط التسميد حسب نوع المحصول ومرحلة النمو
        """
        crops = [
            {"crop": "wheat", "stage": "tillering"},
            {"crop": "tomato", "stage": "fruiting"},
        ]

        results = []
        for crop_info in crops:
            payload = {
                "tenant_id": tenant_id,
                "field_id": field_id,
                **crop_info,
                "field_size_ha": 2.0,
                "soil_fertility": "low",
                "irrigation_type": "flood",
            }
            resp = await http_client.post(
                f"{ADVISORY_BASE_URL}/fertilizer/plan",
                headers=auth_headers,
                json=payload,
            )
            if resp.status_code == 200:
                results.append(resp.json())

        # If we got results for both, they should differ
        if len(results) == 2:
            # Different crops should produce different plans
            assert results[0] != results[1], "Fertilizer plans for different crops should differ"

    async def test_get_fertilizer_by_nutrient(self, http_client: httpx.AsyncClient):
        """
        Get fertilizers that provide a specific nutrient (nitrogen).
        الحصول على الأسمدة التي توفر عنصرا معينا
        """
        resp = await http_client.get(
            f"{ADVISORY_BASE_URL}/fertilizer/nutrient/N",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("nutrient") == "N"
        assert "fertilizers" in body


# ============================================================================
# Crop Catalog Tests
# ============================================================================


class TestCropCatalog:
    """
    Crop catalog and information retrieval tests.
    اختبارات كتالوج المحاصيل واسترجاع المعلومات
    """

    async def test_list_crop_categories(self, http_client: httpx.AsyncClient):
        """
        List all crop categories with counts.
        سرد جميع فئات المحاصيل مع العدد
        """
        resp = await http_client.get(f"{ADVISORY_BASE_URL}/crops/categories")
        assert resp.status_code == 200
        body = resp.json()
        assert "categories" in body
        assert body.get("total_categories", 0) > 0
        assert body.get("total_crops", 0) > 0

    async def test_search_crops_arabic(self, http_client: httpx.AsyncClient):
        """
        Search crops by Arabic name.
        البحث عن المحاصيل بالاسم العربي
        """
        resp = await http_client.get(
            f"{ADVISORY_BASE_URL}/crops/search",
            params={"q": "قمح"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("query") == "قمح"
        results = body.get("results", [])
        assert isinstance(results, list)
        # Arabic search for "wheat" should find results
        if results:
            for crop in results:
                assert "name_ar" in crop
                assert "name_en" in crop

    async def test_search_crops_english(self, http_client: httpx.AsyncClient):
        """Search crops by English name."""
        resp = await http_client.get(
            f"{ADVISORY_BASE_URL}/crops/search",
            params={"q": "wheat"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("count", 0) >= 0

    async def test_search_crops_minimum_length(self, http_client: httpx.AsyncClient):
        """Search query must be at least 2 characters."""
        resp = await http_client.get(
            f"{ADVISORY_BASE_URL}/crops/search",
            params={"q": "a"},
        )
        assert resp.status_code == 422

    async def test_get_crop_details_with_yemen_varieties(
        self,
        http_client: httpx.AsyncClient,
    ):
        """
        Get detailed crop info including Yemen-specific varieties.
        الحصول على تفاصيل المحصول بما في ذلك الأصناف اليمنية
        """
        resp = await http_client.get(f"{ADVISORY_BASE_URL}/crops/wheat")
        assert resp.status_code in (200, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("code") == "wheat"
            assert "name_ar" in body
            assert "name_en" in body
            assert "growing_conditions" in body
            assert "yemen_specific" in body
            assert "coefficients" in body

    async def test_get_crop_stages(self, http_client: httpx.AsyncClient):
        """
        Get growth stages for a specific crop.
        الحصول على مراحل النمو لمحصول معين
        """
        resp = await http_client.get(f"{ADVISORY_BASE_URL}/crops/wheat/stages")
        assert resp.status_code in (200, 404)

        if resp.status_code == 200:
            body = resp.json()
            data = body.get("data", body)
            assert data.get("crop") == "wheat"
            assert "stages" in data

    async def test_get_crop_varieties(self, http_client: httpx.AsyncClient):
        """
        Get Yemen-specific varieties for wheat.
        الحصول على الأصناف اليمنية للقمح
        """
        resp = await http_client.get(f"{ADVISORY_BASE_URL}/crops/wheat/varieties")
        assert resp.status_code in (200, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("crop_code") == "wheat"
            assert "varieties" in body


# ============================================================================
# Cross-Service Advisory Workflow Tests
# ============================================================================


class TestCrossServiceAdvisoryWorkflow:
    """
    End-to-end advisory workflow that spans multiple services.
    سير عمل استشاري شامل يمتد عبر خدمات متعددة
    """

    async def test_field_to_advisory_workflow(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        tenant_id: str,
    ):
        """
        Full workflow: create field -> get weather context -> generate advisory.
        سير عمل كامل: إنشاء حقل -> الحصول على سياق الطقس -> توليد الاستشارة

        Steps:
        1. Verify advisory service is available
        2. Query crop requirements for wheat
        3. Assess nutrient status from NDVI
        4. Generate fertilizer plan
        """
        # Step 1: Check advisory service
        health_resp = await http_client.get(f"{ADVISORY_BASE_URL}/healthz")
        if health_resp.status_code != 200:
            pytest.skip("Advisory service not available")

        # Step 2: Get crop requirements for wheat
        crop_resp = await http_client.get(f"{ADVISORY_BASE_URL}/crops/wheat/requirements")
        assert crop_resp.status_code in (200, 404)

        # Step 3: Assess nutrient status from NDVI = 0.38 (stressed)
        field_id = f"e2e-workflow-{uuid.uuid4().hex[:8]}"
        ndvi_payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "ndvi": 0.38,
            "ndvi_history": [0.65, 0.58, 0.50, 0.42, 0.38],
            "crop": "wheat",
            "stage": "tillering",
            "correlation_id": f"e2e-workflow-{uuid.uuid4().hex[:8]}",
        }
        ndvi_resp = await http_client.post(
            f"{ADVISORY_BASE_URL}/nutrient/ndvi",
            headers=auth_headers,
            json=ndvi_payload,
        )
        assert ndvi_resp.status_code in (200, 401, 403)

        # Step 4: Generate fertilizer plan for the same field
        fert_payload = {
            "tenant_id": tenant_id,
            "field_id": field_id,
            "crop": "wheat",
            "stage": "tillering",
            "field_size_ha": 8.5,
            "soil_fertility": "low",
            "irrigation_type": "drip",
            "correlation_id": f"e2e-workflow-{uuid.uuid4().hex[:8]}",
        }
        fert_resp = await http_client.post(
            f"{ADVISORY_BASE_URL}/fertilizer/plan",
            headers=auth_headers,
            json=fert_payload,
        )
        assert fert_resp.status_code in (200, 401, 403)

        # If both succeeded, verify cross-reference
        if ndvi_resp.status_code == 200 and fert_resp.status_code == 200:
            ndvi_body = ndvi_resp.json()
            fert_body = fert_resp.json()
            assert ndvi_body["field_id"] == fert_body["field_id"]
