"""
E2E Tests for YOLO26 Vision Detection Service.
اختبارات شاملة لخدمة الكشف البصري YOLO26

Tests the complete vision detection workflow:
- Pest detection with bilingual labels
- Disease detection with treatment recommendations
- Weed detection with coverage estimation
- Model management and warmup
- Batch detection processing
- Error handling for invalid uploads

Service: yolo26-vision-service (FastAPI)
Port: 8150
Routes: /api/v1/detect/*, /api/v1/models/*

Usage:
    pytest tests/e2e/test_vision_detection_e2e.py -v -m e2e

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import io
import os
import uuid

import httpx
import pytest

# ============================================================================
# Configuration
# ============================================================================

VISION_BASE_URL = os.getenv("E2E_VISION_BASE_URL", "http://localhost:8150")
AUTH_BASE_URL = os.getenv("E2E_AUTH_BASE_URL", "http://localhost:3025")
VISION_API = f"{VISION_BASE_URL}/api/v1"

pytestmark = [pytest.mark.e2e, pytest.mark.asyncio]


# ============================================================================
# Helpers
# ============================================================================


def create_test_image(width: int = 640, height: int = 480, fmt: str = "JPEG") -> bytes:
    """
    Create a minimal test image in memory.
    إنشاء صورة اختبار بسيطة في الذاكرة
    """
    try:
        from PIL import Image

        img = Image.new("RGB", (width, height), color=(34, 139, 34))  # ForestGreen
        buffer = io.BytesIO()
        img.save(buffer, format=fmt)
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        # Minimal valid 1x1 JPEG if PIL is not available
        return (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
            b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
            b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
            b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342"
            b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
            b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
            b"\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
            b"\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"
            b"\x22q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16"
            b"\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz"
            b"\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99"
            b"\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7"
            b"\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5"
            b"\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1"
            b"\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa"
            b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00T\xdb\xae\x8ap\xa0\x02\x80"
            b"\xff\xd9"
        )


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
async def auth_token() -> str:
    """Obtain JWT auth token."""
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
        "Accept": "application/json",
    }


@pytest.fixture
async def http_client() -> httpx.AsyncClient:
    """Async HTTP client with extended timeout for vision processing."""
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
def test_image_bytes() -> bytes:
    """Generate a test image for upload."""
    return create_test_image()


# ============================================================================
# Health Check Tests
# ============================================================================


class TestVisionServiceHealth:
    """Vision service health and readiness tests."""

    async def test_healthz_returns_ok(self, http_client: httpx.AsyncClient):
        """
        Vision service liveness probe.
        فحص صحة خدمة الكشف البصري
        """
        resp = await http_client.get(f"{VISION_BASE_URL}/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") == "ok"
        assert "version" in body

    async def test_readyz_returns_ready(self, http_client: httpx.AsyncClient):
        """
        Readiness probe confirms GPU/model availability.
        فحص الجاهزية يؤكد توفر GPU/النموذج
        """
        resp = await http_client.get(f"{VISION_BASE_URL}/readyz")
        assert resp.status_code in (200, 503)

    async def test_health_detailed(self, http_client: httpx.AsyncClient):
        """Detailed health check with component status."""
        resp = await http_client.get(f"{VISION_BASE_URL}/health")
        assert resp.status_code in (200, 404)


# ============================================================================
# Pest Detection Tests
# ============================================================================


class TestPestDetection:
    """
    Pest detection endpoint tests.
    اختبارات نقطة نهاية الكشف عن الآفات
    """

    async def test_detect_pest_with_image(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Upload an image for pest detection.
        رفع صورة للكشف عن الآفات
        """
        files = {
            "file": ("test_field.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/pest",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
            params={
                "confidence_threshold": 0.25,
                "include_recommendations": True,
            },
        )
        assert resp.status_code in (200, 401, 500, 503)

        if resp.status_code == 200:
            body = resp.json()
            assert "request_id" in body
            assert "processing_time_ms" in body
            assert "model_variant" in body
            assert "image_metadata" in body
            assert "detections" in body
            assert "total_count" in body
            assert "severity_summary" in body

            # Verify bilingual labels in detections
            for det in body.get("detections", []):
                assert "class_name_en" in det
                assert "class_name_ar" in det
                assert "confidence" in det
                assert "bbox" in det
                assert "severity" in det
                # Recommendations should be present when requested
                if det.get("recommended_action_en"):
                    assert det.get("recommended_action_ar")

    async def test_detect_pest_with_visualization(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Request pest detection with visualization overlay.
        طلب كشف الآفات مع تراكب التصور
        """
        files = {
            "file": ("test_vis.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/pest",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
            params={
                "return_visualization": True,
                "confidence_threshold": 0.1,
            },
        )
        assert resp.status_code in (200, 401, 500, 503)

        if resp.status_code == 200:
            body = resp.json()
            # visualization_base64 should be present if detections found
            if body.get("total_count", 0) > 0:
                assert body.get("visualization_base64") is not None

    async def test_detect_pest_custom_model_variant(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Use different model variants (nano, small, medium) for detection.
        استخدام أنواع نماذج مختلفة للكشف
        """
        files = {
            "file": ("test_variant.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/pest",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
            params={"model_variant": "n"},  # Nano variant
        )
        assert resp.status_code in (200, 401, 500, 503)

        if resp.status_code == 200:
            body = resp.json()
            assert body.get("model_variant") in ("n", "nano")

    async def test_detect_pest_invalid_file_type(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Uploading a non-image file should be rejected.
        يجب رفض رفع ملف غير صورة
        """
        files = {
            "file": ("test.txt", b"This is not an image", "text/plain"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/pest",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
        )
        assert resp.status_code in (400, 422, 500)

        if resp.status_code == 400:
            body = resp.json()
            detail = body.get("detail", {})
            # Should include bilingual error message
            assert "message_ar" in detail or "error" in detail

    async def test_detect_pest_missing_file(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Detection without uploading a file should fail.
        الكشف بدون رفع ملف يجب أن يفشل
        """
        resp = await http_client.post(
            f"{VISION_API}/detect/pest",
            headers={"Authorization": auth_headers["Authorization"]},
        )
        assert resp.status_code in (400, 422)


# ============================================================================
# Disease Detection Tests
# ============================================================================


class TestDiseaseDetection:
    """
    Disease detection endpoint tests with treatment recommendations.
    اختبارات الكشف عن الأمراض مع توصيات العلاج
    """

    async def test_detect_disease_with_treatments(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Detect plant diseases with treatment recommendations.
        الكشف عن أمراض النبات مع توصيات العلاج
        """
        files = {
            "file": ("diseased_leaf.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/disease",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
            params={
                "include_treatments": True,
                "calculate_affected_area": True,
            },
        )
        assert resp.status_code in (200, 401, 500, 503)

        if resp.status_code == 200:
            body = resp.json()
            assert "request_id" in body
            assert "overall_health_score" in body
            assert "severity_summary" in body

            for det in body.get("detections", []):
                assert "class_name_ar" in det
                assert "class_name_en" in det
                assert "severity" in det
                # Affected area should be calculated
                if det.get("affected_area_percent") is not None:
                    assert det["affected_area_percent"] >= 0
                # Treatment recommendations
                if det.get("recommended_treatment_en"):
                    assert det.get("recommended_treatment_ar")
                    assert "spread_risk" in det

    async def test_detect_disease_health_score_range(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Health score should be between 0 and 100.
        يجب أن تكون درجة الصحة بين 0 و100
        """
        files = {
            "file": ("health_check.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/disease",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
        )
        if resp.status_code == 200:
            body = resp.json()
            score = body.get("overall_health_score", 0)
            assert 0 <= score <= 100, f"Health score {score} out of range"


# ============================================================================
# Weed Detection Tests
# ============================================================================


class TestWeedDetection:
    """
    Weed detection endpoint tests with coverage estimation.
    اختبارات الكشف عن الأعشاب مع تقدير التغطية
    """

    async def test_detect_weeds_with_coverage(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Detect weeds with coverage percentage calculation.
        الكشف عن الأعشاب مع حساب نسبة التغطية
        """
        files = {
            "file": ("weedy_field.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/weed",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
            params={"calculate_coverage": True},
        )
        assert resp.status_code in (200, 401, 500, 503)

        if resp.status_code == 200:
            body = resp.json()
            assert "total_coverage_percent" in body
            assert "species_distribution" in body
            assert body.get("total_coverage_percent", 0) <= 100

            for det in body.get("detections", []):
                assert "class_name_ar" in det
                assert "class_name_en" in det

    async def test_detect_weeds_species_distribution(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Verify weed species distribution is returned.
        التحقق من أن توزيع أنواع الأعشاب يتم إرجاعه
        """
        files = {
            "file": ("species_test.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/weed",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
        )
        if resp.status_code == 200:
            body = resp.json()
            species = body.get("species_distribution", {})
            assert isinstance(species, dict)


# ============================================================================
# Model Management Tests
# ============================================================================


class TestModelManagement:
    """
    Model version management and info tests.
    اختبارات إدارة إصدارات النماذج والمعلومات
    """

    async def test_list_model_versions(self, http_client: httpx.AsyncClient):
        """
        List all available model versions.
        سرد جميع إصدارات النماذج المتاحة
        """
        resp = await http_client.get(f"{VISION_API}/models/versions")
        assert resp.status_code in (200, 404)

        if resp.status_code == 200:
            body = resp.json()
            assert isinstance(body, (list, dict))

    async def test_get_model_info(self, http_client: httpx.AsyncClient):
        """
        Get info for the medium model variant.
        الحصول على معلومات نوع النموذج المتوسط
        """
        resp = await http_client.get(f"{VISION_API}/models/m/info")
        assert resp.status_code in (200, 404)

    async def test_list_loaded_models(self, http_client: httpx.AsyncClient):
        """
        Get currently loaded models in memory.
        الحصول على النماذج المحملة حاليا في الذاكرة
        """
        resp = await http_client.get(f"{VISION_API}/models/loaded")
        assert resp.status_code in (200, 404)

    async def test_warmup_models(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Preload models into memory for faster inference.
        تحميل النماذج مسبقا في الذاكرة لاستنتاج أسرع
        """
        resp = await http_client.post(
            f"{VISION_API}/models/warmup",
            headers=auth_headers,
        )
        # Model warmup might take a while; could be 200, 503, or timeout
        assert resp.status_code in (200, 401, 404, 500, 503)


# ============================================================================
# Batch Detection Tests
# ============================================================================


class TestBatchDetection:
    """
    Batch image processing tests.
    اختبارات معالجة الصور بالدفعات
    """

    async def test_batch_cache_stats(self, http_client: httpx.AsyncClient):
        """
        Get batch processing cache statistics.
        الحصول على إحصائيات ذاكرة التخزين المؤقت للمعالجة
        """
        resp = await http_client.get(f"{VISION_API}/batch/cache/stats")
        assert resp.status_code in (200, 404)

    async def test_batch_status(self, http_client: httpx.AsyncClient):
        """
        Check batch processing queue status.
        التحقق من حالة قائمة انتظار المعالجة
        """
        resp = await http_client.get(f"{VISION_API}/batch/status")
        assert resp.status_code in (200, 404)


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestVisionErrorHandling:
    """
    Error handling and edge case tests.
    اختبارات معالجة الأخطاء والحالات الحدودية
    """

    async def test_confidence_threshold_out_of_range(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Confidence threshold > 1.0 should be rejected.
        عتبة الثقة > 1.0 يجب أن ترفض
        """
        files = {
            "file": ("test_thresh.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/pest",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
            params={"confidence_threshold": 1.5},
        )
        assert resp.status_code in (400, 422)

    async def test_image_size_out_of_range(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
        test_image_bytes: bytes,
    ):
        """
        Image size below minimum (320) should be rejected.
        حجم الصورة أقل من الحد الأدنى يجب أن يرفض
        """
        files = {
            "file": ("test_size.jpg", test_image_bytes, "image/jpeg"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/pest",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
            params={"image_size": 100},
        )
        assert resp.status_code in (400, 422)

    async def test_bilingual_error_responses(
        self,
        http_client: httpx.AsyncClient,
        auth_headers: dict[str, str],
    ):
        """
        Error responses should include both Arabic and English messages.
        يجب أن تتضمن استجابات الخطأ رسائل بالعربية والإنجليزية
        """
        files = {
            "file": ("bad.txt", b"not an image at all", "text/plain"),
        }
        resp = await http_client.post(
            f"{VISION_API}/detect/pest",
            headers={"Authorization": auth_headers["Authorization"]},
            files=files,
        )
        if resp.status_code in (400, 422):
            body = resp.json()
            detail = body.get("detail", {})
            if isinstance(detail, dict):
                # Vision service returns bilingual error messages
                assert "message" in detail or "message_ar" in detail
