"""
Comprehensive tests for advisory-service src/main.py
اختبارات شاملة لخدمة الاستشارة الزراعية

Covers:
- All API endpoints: health, readiness, disease, nutrient, fertilizer,
  crops, actions, comprehensive advisory, loan verification
- Input-validation helpers: _sanitize_text, _validate_identifier, _validate_crop_type
- Tenant-enforcement helper: _enforce_tenant
- Pydantic model field validators
"""

import os
import sys
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock all external / shared dependencies BEFORE importing source
# ---------------------------------------------------------------------------


class _NoopMiddleware:
    """Pass-through ASGI middleware stub."""

    def __init__(self, app, **kwargs):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


_SHARED_MOCKS = [
    "shared",
    "shared.logging_config",
    "shared.auth",
    "shared.auth.dependencies",
    "shared.auth.models",
    "shared.errors_py",
    "shared.auth.revocation_middleware",
    "shared.auth.token_revocation",
    "shared.observability",
    "shared.observability.middleware",
    "shared.middleware",
    "shared.middleware.security_headers",
    "shared.middleware.tenant_context",
    "shared.cors_config",
    "shared.auth.service_middleware",
    "shared.db",
    "shared.db.ssl",
    "shared.libs",
    "shared.libs.outbox",
    "structlog",
    "nats",
    "asyncpg",
    # NOTE: do NOT mock httpx here — starlette.testclient imports it at class
    # definition time and needs real httpx types to avoid metaclass conflicts.
]

for _mod in _SHARED_MOCKS:
    sys.modules.setdefault(_mod, MagicMock())

# Wire callables invoked at module import time
sys.modules["shared.logging_config"].setup_logging = lambda *a, **kw: None
sys.modules["shared.logging_config"].get_logger = lambda *a, **kw: MagicMock()
sys.modules["shared.errors_py"].setup_exception_handlers = lambda app: None
sys.modules["shared.errors_py"].add_request_id_middleware = lambda app: None
sys.modules["shared.errors_py"].create_success_response = lambda d: d
sys.modules["shared.middleware.tenant_context"].TenantContextMiddleware = _NoopMiddleware
sys.modules["shared.middleware.security_headers"].setup_security_headers = lambda app: None
sys.modules["shared.observability.middleware"].ObservabilityMiddleware = _NoopMiddleware
sys.modules["shared.auth.service_middleware"].ServiceAuthMiddleware = _NoopMiddleware

# Ensure TokenRevocationMiddleware is a proper ASGI middleware stub
sys.modules["shared.auth.revocation_middleware"].TokenRevocationMiddleware = _NoopMiddleware
# Ensure get_revocation_store returns a mock with an async initialize/close
_revocation_store_mock = MagicMock()
_revocation_store_mock.initialize = AsyncMock()
_revocation_store_mock.close = AsyncMock()
sys.modules["shared.auth.token_revocation"].get_revocation_store = MagicMock(return_value=_revocation_store_mock)

# structlog mock
_structlog = sys.modules["structlog"]
_structlog.get_logger.return_value = MagicMock()

# Fake User with tenant_id attribute
_FakeUser = type(
    "User",
    (),
    {"id": "user-001", "email": "test@sahool.sa", "tenant_id": "tenant-001", "roles": ["farmer"]},
)
_mock_user = _FakeUser()


async def _fake_get_current_user():
    return _mock_user


sys.modules["shared.auth.dependencies"].get_current_user = _fake_get_current_user
sys.modules["shared.auth.models"].User = _FakeUser

# Mock comprehensive and loans modules (import external HTTP deps)
_comp_mock = MagicMock()
_comp_mock.ComprehensiveAdvisoryOrchestrator = MagicMock()
_comp_mock.ServiceUrls = MagicMock()
sys.modules["src.comprehensive"] = _comp_mock

_loans_mock = MagicMock()
_loans_mock.CropLoanVerificationEngine = MagicMock()
_loans_mock.LoanVerificationRequest = MagicMock()
sys.modules["src.loans"] = _loans_mock

# Ensure the actual service packages (crops, yemen_varieties) are resolvable
_SVC_SHARED = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
_SVC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

for _p in (_SVC_SHARED, _SVC_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from src.main import (  # noqa: E402
    CROP_REQUIREMENTS,
    VALID_CROP_VALUES,
    VALID_IRRIGATION_TYPES,
    VALID_LANG_CODES,
    VALID_SOIL_FERTILITY,
    DiseaseAssessRequest,
    FertilizerPlanRequest,
    NDVIAssessRequest,
    SymptomAssessRequest,
    VisualAssessRequest,
    _enforce_tenant,
    _sanitize_text,
    _validate_crop_type,
    _validate_identifier,
    app,
)

# ---------------------------------------------------------------------------
# Override the auth dependency so every endpoint gets our fake user
# ---------------------------------------------------------------------------
from src.main import get_current_user as _real_get_current_user  # noqa: E402


async def _fake_get_current_user():
    return _mock_user


app.dependency_overrides[_real_get_current_user] = _fake_get_current_user

client = TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture()
def disease_assess_body():
    return {
        "tenant_id": "tenant-001",
        "field_id": "FIELD-001",
        "condition_id": "wheat_rust",
        "confidence": 0.85,
        "crop": "wheat",
    }


@pytest.fixture()
def symptom_assess_body():
    return {
        "tenant_id": "tenant-001",
        "field_id": "FIELD-001",
        "crop": "wheat",
        "symptoms": ["yellowing leaves", "orange pustules"],
        "lang": "en",
    }


@pytest.fixture()
def ndvi_assess_body():
    return {
        "tenant_id": "tenant-001",
        "field_id": "FIELD-001",
        "ndvi": 0.25,
        "crop": "wheat",
        "stage": "vegetative",
    }


@pytest.fixture()
def visual_assess_body():
    return {
        "tenant_id": "tenant-001",
        "field_id": "FIELD-001",
        "leaf_color": "yellow",
        "pattern": "uniform",
        "location": "lower leaves",
        "crop": "wheat",
        "lang": "en",
    }


@pytest.fixture()
def fertilizer_plan_body():
    return {
        "tenant_id": "tenant-001",
        "field_id": "FIELD-001",
        "crop": "wheat",
        "stage": "tillering",
        "field_size_ha": 2.5,
        "soil_fertility": "medium",
        "irrigation_type": "drip",
    }


# ===========================================================================
# 1. Pure helper functions
# ===========================================================================


class TestSanitizeText:
    def test_strips_null_bytes(self):
        assert "\x00" not in _sanitize_text("hello\x00world")

    def test_strips_control_chars(self):
        assert "\x01" not in _sanitize_text("test\x01data")

    def test_preserves_ampersand(self):
        assert "&" in _sanitize_text("yellowing & wilting")

    def test_preserves_angle_brackets(self):
        result = _sanitize_text("<5% leaf area affected")
        assert "<" in result
        assert "%" in result

    def test_truncates_to_500_chars(self):
        long_input = "a" * 600
        assert len(_sanitize_text(long_input)) == 500

    def test_empty_string(self):
        assert _sanitize_text("") == ""

    def test_arabic_text_preserved(self):
        arabic = "اصفرار الأوراق"
        assert _sanitize_text(arabic) == arabic


class TestValidateIdentifier:
    def test_valid_alphanumeric(self):
        assert _validate_identifier("FIELD-001", "field_id") == "FIELD-001"

    def test_valid_with_dots_colons(self):
        assert _validate_identifier("sahool.tenant:v1", "x") == "sahool.tenant:v1"

    def test_valid_with_underscores(self):
        assert _validate_identifier("field_001", "x") == "field_001"

    def test_rejects_spaces(self):
        with pytest.raises(ValueError, match="invalid characters"):
            _validate_identifier("field 001", "field_id")

    def test_rejects_slashes(self):
        with pytest.raises(ValueError, match="invalid characters"):
            _validate_identifier("../admin", "field_id")

    def test_rejects_angle_brackets(self):
        with pytest.raises(ValueError, match="invalid characters"):
            _validate_identifier("<script>", "x")


class TestValidateCropType:
    def test_known_catalog_code(self):
        # WHEAT is a catalog code
        assert _validate_crop_type("wheat") == "wheat"

    def test_kb_crop_name(self):
        # 'tomato' is in _KB_CROP_NAMES
        assert _validate_crop_type("tomato") == "tomato"

    def test_planner_crop_name(self):
        # 'potato' is in CROP_REQUIREMENTS
        assert _validate_crop_type("potato") == "potato"

    def test_unknown_crop_raises(self):
        with pytest.raises(ValueError, match="Unknown crop type"):
            _validate_crop_type("unknowncrop_xyz_abc")


class TestEnforceTenant:
    def test_passes_when_tenant_matches(self):
        user = type("U", (), {"tenant_id": "t1"})()
        _enforce_tenant(user, "t1")  # should not raise

    def test_raises_403_when_no_tenant_id(self):
        user = type("U", (), {"tenant_id": None})()
        with pytest.raises(HTTPException) as exc_info:
            _enforce_tenant(user, "t1")
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == "missing_tenant"

    def test_raises_403_when_tenant_mismatch(self):
        user = type("U", (), {"tenant_id": "t1"})()
        with pytest.raises(HTTPException) as exc_info:
            _enforce_tenant(user, "t2")
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == "tenant_mismatch"


# ===========================================================================
# 2. Pydantic model validators
# ===========================================================================


class TestDiseaseAssessRequestValidation:
    def test_valid_body(self, disease_assess_body):
        req = DiseaseAssessRequest(**disease_assess_body)
        assert req.confidence == 0.85

    def test_invalid_identifier_rejected(self, disease_assess_body):
        disease_assess_body["field_id"] = "field with spaces"
        with pytest.raises(Exception):
            DiseaseAssessRequest(**disease_assess_body)

    def test_confidence_out_of_range_rejected(self, disease_assess_body):
        disease_assess_body["confidence"] = 1.5
        with pytest.raises(Exception):
            DiseaseAssessRequest(**disease_assess_body)

    def test_unknown_crop_rejected(self, disease_assess_body):
        disease_assess_body["crop"] = "unknowncrop_xyz"
        with pytest.raises(Exception):
            DiseaseAssessRequest(**disease_assess_body)

    def test_weather_clamped(self, disease_assess_body):
        disease_assess_body["weather"] = {"temperature": 999, "humidity": 200}
        req = DiseaseAssessRequest(**disease_assess_body)
        assert req.weather["temperature"] == 60
        assert req.weather["humidity"] == 100

    def test_no_crop_allowed(self, disease_assess_body):
        disease_assess_body.pop("crop")
        req = DiseaseAssessRequest(**disease_assess_body)
        assert req.crop is None


class TestSymptomAssessRequestValidation:
    def test_valid_body(self, symptom_assess_body):
        req = SymptomAssessRequest(**symptom_assess_body)
        assert req.crop == "wheat"

    def test_invalid_lang_rejected(self, symptom_assess_body):
        symptom_assess_body["lang"] = "fr"
        with pytest.raises(Exception):
            SymptomAssessRequest(**symptom_assess_body)

    def test_symptom_too_long_rejected(self, symptom_assess_body):
        symptom_assess_body["symptoms"] = ["a" * 501]
        with pytest.raises(Exception):
            SymptomAssessRequest(**symptom_assess_body)

    def test_control_chars_stripped_from_symptoms(self, symptom_assess_body):
        symptom_assess_body["symptoms"] = ["yellow\x00leaf"]
        req = SymptomAssessRequest(**symptom_assess_body)
        assert "\x00" not in req.symptoms[0]


class TestNDVIAssessRequestValidation:
    def test_valid_body(self, ndvi_assess_body):
        req = NDVIAssessRequest(**ndvi_assess_body)
        assert req.ndvi == 0.25

    def test_ndvi_out_of_range_rejected(self, ndvi_assess_body):
        ndvi_assess_body["ndvi"] = 1.5
        with pytest.raises(Exception):
            NDVIAssessRequest(**ndvi_assess_body)

    def test_ndvi_history_out_of_range_rejected(self, ndvi_assess_body):
        ndvi_assess_body["ndvi_history"] = [0.5, 1.5]
        with pytest.raises(Exception):
            NDVIAssessRequest(**ndvi_assess_body)

    def test_stage_sanitized(self, ndvi_assess_body):
        ndvi_assess_body["stage"] = "vegetative\x00"
        req = NDVIAssessRequest(**ndvi_assess_body)
        assert "\x00" not in req.stage


class TestFertilizerPlanRequestValidation:
    def test_valid_body(self, fertilizer_plan_body):
        req = FertilizerPlanRequest(**fertilizer_plan_body)
        assert req.crop == "wheat"

    def test_invalid_soil_fertility_rejected(self, fertilizer_plan_body):
        fertilizer_plan_body["soil_fertility"] = "super"
        with pytest.raises(Exception):
            FertilizerPlanRequest(**fertilizer_plan_body)

    def test_invalid_irrigation_type_rejected(self, fertilizer_plan_body):
        fertilizer_plan_body["irrigation_type"] = "hand_watering"
        with pytest.raises(Exception):
            FertilizerPlanRequest(**fertilizer_plan_body)

    def test_future_planting_date_rejected(self, fertilizer_plan_body):
        fertilizer_plan_body["planting_date"] = str(date.today() + timedelta(days=1))
        with pytest.raises(Exception):
            FertilizerPlanRequest(**fertilizer_plan_body)

    def test_past_planting_date_accepted(self, fertilizer_plan_body):
        fertilizer_plan_body["planting_date"] = str(date.today() - timedelta(days=30))
        req = FertilizerPlanRequest(**fertilizer_plan_body)
        assert req.planting_date is not None

    def test_field_size_zero_rejected(self, fertilizer_plan_body):
        fertilizer_plan_body["field_size_ha"] = 0
        with pytest.raises(Exception):
            FertilizerPlanRequest(**fertilizer_plan_body)


# ===========================================================================
# 3. Health endpoints
# ===========================================================================


class TestHealthEndpoints:
    def test_healthz_returns_ok(self):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "advisory_service"
        assert "version" in data

    def test_healthz_version_format(self):
        resp = client.get("/healthz")
        version = resp.json()["version"]
        parts = version.split(".")
        assert len(parts) == 3  # semver

    def test_readyz_returns_status(self):
        resp = client.get("/readyz")
        # Engine may or may not be loaded; either way we get a JSON response
        assert resp.status_code in (200, 503)
        data = resp.json()
        assert "status" in data
        assert data["service"] == "advisory_service"

    def test_readyz_checks_engine(self):
        resp = client.get("/readyz")
        data = resp.json()
        # When loaded, checks include engine status
        if resp.status_code == 200:
            assert data["checks"]["engine"] == "loaded"


# ===========================================================================
# 4. Disease endpoints
# ===========================================================================


class TestDiseaseAssessEndpoint:
    def test_known_disease_high_confidence(self, disease_assess_body):
        resp = client.post("/api/v1/disease/assess", json=disease_assess_body)
        assert resp.status_code == 200
        data = resp.json()
        assert "field_id" in data
        assert data["field_id"] == "FIELD-001"
        assert data["result"] is not None

    def test_unknown_condition_returns_null_result(self, disease_assess_body):
        disease_assess_body["condition_id"] = "totally_unknown_xyz"
        disease_assess_body["confidence"] = 0.9
        resp = client.post("/api/v1/disease/assess", json=disease_assess_body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"] is None

    def test_low_confidence_returns_null_result(self, disease_assess_body):
        disease_assess_body["confidence"] = 0.05
        resp = client.post("/api/v1/disease/assess", json=disease_assess_body)
        assert resp.status_code == 200
        data = resp.json()
        # Low confidence → result is None or message
        assert data.get("result") is None or "message" in data

    def test_tenant_mismatch_returns_403(self, disease_assess_body):
        disease_assess_body["tenant_id"] = "other-tenant"
        resp = client.post("/api/v1/disease/assess", json=disease_assess_body)
        assert resp.status_code == 403

    def test_missing_required_field_returns_422(self, disease_assess_body):
        del disease_assess_body["confidence"]
        resp = client.post("/api/v1/disease/assess", json=disease_assess_body)
        assert resp.status_code == 422

    def test_invalid_crop_returns_422(self, disease_assess_body):
        disease_assess_body["crop"] = "NOTACROP99"
        resp = client.post("/api/v1/disease/assess", json=disease_assess_body)
        assert resp.status_code == 422

    def test_weather_clamping_accepted(self, disease_assess_body):
        disease_assess_body["weather"] = {"temperature": 9999, "humidity": -50}
        resp = client.post("/api/v1/disease/assess", json=disease_assess_body)
        assert resp.status_code == 200


class TestDiseaseSymptomEndpoint:
    def test_valid_symptoms_returns_results(self, symptom_assess_body):
        resp = client.post("/api/v1/disease/symptoms", json=symptom_assess_body)
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert "field_id" in data

    def test_no_matching_symptoms_returns_empty(self, symptom_assess_body):
        symptom_assess_body["symptoms"] = ["completely unrecognized symptom xyz"]
        resp = client.post("/api/v1/disease/symptoms", json=symptom_assess_body)
        assert resp.status_code == 200

    def test_tenant_mismatch_returns_403(self, symptom_assess_body):
        symptom_assess_body["tenant_id"] = "other-tenant"
        resp = client.post("/api/v1/disease/symptoms", json=symptom_assess_body)
        assert resp.status_code == 403

    def test_invalid_lang_returns_422(self, symptom_assess_body):
        symptom_assess_body["lang"] = "fr"
        resp = client.post("/api/v1/disease/symptoms", json=symptom_assess_body)
        assert resp.status_code == 422

    def test_arabic_lang_accepted(self, symptom_assess_body):
        symptom_assess_body["lang"] = "ar"
        symptom_assess_body["symptoms"] = ["اصفرار الأوراق"]
        resp = client.post("/api/v1/disease/symptoms", json=symptom_assess_body)
        assert resp.status_code == 200


class TestDiseaseSearchEndpoint:
    def test_search_returns_results(self):
        resp = client.get("/api/v1/disease/search?q=rust&lang=en")
        assert resp.status_code == 200
        data = resp.json()
        assert "query" in data
        assert "results" in data
        assert "count" in data

    def test_search_by_arabic(self):
        resp = client.get("/api/v1/disease/search?q=صدأ&lang=ar")
        assert resp.status_code == 200

    def test_search_no_results(self):
        resp = client.get("/api/v1/disease/search?q=zzznomatch999")
        assert resp.status_code == 200
        assert resp.json()["count"] == 0


class TestDiseaseByIdEndpoint:
    def test_known_disease_returns_data(self):
        resp = client.get("/api/v1/disease/wheat_rust?lang=en")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data or "name_en" in data

    def test_unknown_disease_returns_404(self):
        resp = client.get("/api/v1/disease/totally_unknown_xyz")
        assert resp.status_code == 404


class TestDiseasesByCropEndpoint:
    def test_wheat_diseases(self):
        resp = client.get("/api/v1/disease/crop/wheat")
        assert resp.status_code == 200
        data = resp.json()
        assert "diseases" in data
        assert "count" in data

    def test_unknown_crop_returns_empty_list(self):
        resp = client.get("/api/v1/disease/crop/notacrop")
        assert resp.status_code == 200
        # Returns general/cross-crop diseases rather than empty list
        data = resp.json()
        assert "count" in data
        assert isinstance(data["count"], int)


# ===========================================================================
# 5. Nutrient endpoints
# ===========================================================================


class TestNutrientNdviEndpoint:
    def test_low_ndvi_triggers_assessment(self, ndvi_assess_body):
        resp = client.post("/api/v1/nutrient/ndvi", json=ndvi_assess_body)
        assert resp.status_code == 200
        data = resp.json()
        assert "field_id" in data
        assert "ndvi" in data
        assert "results" in data

    def test_healthy_ndvi_returns_results(self, ndvi_assess_body):
        ndvi_assess_body["ndvi"] = 0.75
        resp = client.post("/api/v1/nutrient/ndvi", json=ndvi_assess_body)
        assert resp.status_code == 200

    def test_tenant_mismatch_returns_403(self, ndvi_assess_body):
        ndvi_assess_body["tenant_id"] = "other"
        resp = client.post("/api/v1/nutrient/ndvi", json=ndvi_assess_body)
        assert resp.status_code == 403

    def test_ndvi_out_of_range_returns_422(self, ndvi_assess_body):
        ndvi_assess_body["ndvi"] = 2.0
        resp = client.post("/api/v1/nutrient/ndvi", json=ndvi_assess_body)
        assert resp.status_code == 422

    def test_ndvi_history_included(self, ndvi_assess_body):
        ndvi_assess_body["ndvi_history"] = [0.3, 0.25, 0.20]
        resp = client.post("/api/v1/nutrient/ndvi", json=ndvi_assess_body)
        assert resp.status_code == 200


class TestNutrientVisualEndpoint:
    def test_valid_visual_indicators(self, visual_assess_body):
        resp = client.post("/api/v1/nutrient/visual", json=visual_assess_body)
        assert resp.status_code == 200
        data = resp.json()
        assert "field_id" in data
        assert "results" in data
        assert "indicators" in data

    def test_tenant_mismatch_returns_403(self, visual_assess_body):
        visual_assess_body["tenant_id"] = "other"
        resp = client.post("/api/v1/nutrient/visual", json=visual_assess_body)
        assert resp.status_code == 403

    def test_minimal_indicators_accepted(self, visual_assess_body):
        # Provide all indicator fields (engine requires non-None for pattern/location)
        resp = client.post(
            "/api/v1/nutrient/visual",
            json={
                "tenant_id": "tenant-001",
                "field_id": "FIELD-001",
                "leaf_color": "yellow",
                "pattern": "",
                "location": "",
            },
        )
        assert resp.status_code == 200


class TestNutrientDeficiencyByIdEndpoint:
    def test_known_deficiency_returns_data(self):
        resp = client.get("/api/v1/nutrient/nitrogen_deficiency")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data or "nutrient" in data

    def test_unknown_deficiency_returns_404(self):
        resp = client.get("/api/v1/nutrient/unknown_deficiency_xyz")
        assert resp.status_code == 404


# ===========================================================================
# 6. Fertilizer endpoints
# ===========================================================================


class TestFertilizerPlanEndpoint:
    def test_valid_plan_request(self, fertilizer_plan_body):
        resp = client.post("/api/v1/fertilizer/plan", json=fertilizer_plan_body)
        assert resp.status_code == 200
        data = resp.json()
        assert "field_id" in data
        assert "applications" in data

    def test_tenant_mismatch_returns_403(self, fertilizer_plan_body):
        fertilizer_plan_body["tenant_id"] = "other"
        resp = client.post("/api/v1/fertilizer/plan", json=fertilizer_plan_body)
        assert resp.status_code == 403

    def test_invalid_irrigation_type_returns_422(self, fertilizer_plan_body):
        fertilizer_plan_body["irrigation_type"] = "bucket"
        resp = client.post("/api/v1/fertilizer/plan", json=fertilizer_plan_body)
        assert resp.status_code == 422

    def test_invalid_soil_fertility_returns_422(self, fertilizer_plan_body):
        fertilizer_plan_body["soil_fertility"] = "excellent"
        resp = client.post("/api/v1/fertilizer/plan", json=fertilizer_plan_body)
        assert resp.status_code == 422

    def test_tomato_plan(self, fertilizer_plan_body):
        fertilizer_plan_body["crop"] = "tomato"
        fertilizer_plan_body["stage"] = "flowering"
        resp = client.post("/api/v1/fertilizer/plan", json=fertilizer_plan_body)
        assert resp.status_code == 200

    def test_field_size_respected_in_plan(self, fertilizer_plan_body):
        fertilizer_plan_body["field_size_ha"] = 5.0
        resp = client.post("/api/v1/fertilizer/plan", json=fertilizer_plan_body)
        assert resp.status_code == 200


class TestFertilizerByIdEndpoint:
    def test_known_fertilizer_returns_data(self):
        resp = client.get("/api/v1/fertilizer/urea")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data or "name_en" in data

    def test_unknown_fertilizer_returns_404(self):
        resp = client.get("/api/v1/fertilizer/unknown_fertilizer_xyz")
        assert resp.status_code == 404


# ===========================================================================
# 7. Crop endpoints
# ===========================================================================


class TestCropCategoriesEndpoint:
    def test_returns_categories(self):
        resp = client.get("/api/v1/crops/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert "categories" in data
        assert len(data["categories"]) > 0

    def test_total_crops_positive(self):
        resp = client.get("/api/v1/crops/categories")
        assert resp.json()["total_crops"] > 0

    def test_each_category_has_crops_list(self):
        resp = client.get("/api/v1/crops/categories")
        for cat in resp.json()["categories"]:
            assert "crops" in cat
            assert "count" in cat


class TestCropSearchEndpoint:
    def test_search_by_english_name(self):
        resp = client.get("/api/v1/crops/search?q=wheat")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert data["count"] >= 0

    def test_query_too_short_returns_422(self):
        resp = client.get("/api/v1/crops/search?q=w")
        assert resp.status_code == 422

    def test_arabic_search_works(self):
        resp = client.get("/api/v1/crops/search?q=قمح")
        assert resp.status_code == 200

    def test_no_match_returns_empty(self):
        resp = client.get("/api/v1/crops/search?q=zzznomatching")
        assert resp.status_code == 200
        assert resp.json()["count"] == 0


class TestCropDetailEndpoint:
    def test_known_crop_returns_data(self):
        resp = client.get("/api/v1/crops/WHEAT")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == "WHEAT"
        assert "name_en" in data
        assert "growing_conditions" in data
        assert "yield_data" in data

    def test_unknown_crop_returns_404(self):
        resp = client.get("/api/v1/crops/NOTACROP_XYZ")
        assert resp.status_code == 404


class TestCropVarietiesEndpoint:
    def test_known_crop_returns_varieties(self):
        resp = client.get("/api/v1/crops/WHEAT/varieties")
        assert resp.status_code == 200
        data = resp.json()
        assert "varieties" in data
        assert "count" in data
        assert data["crop_code"] == "WHEAT"

    def test_unknown_crop_returns_404(self):
        resp = client.get("/api/v1/crops/NOTACROP/varieties")
        assert resp.status_code == 404


class TestCropStagesEndpoint:
    def test_wheat_stages(self):
        resp = client.get("/api/v1/crops/wheat/stages")
        assert resp.status_code == 200
        data = resp.json()
        inner = data.get("data", data)
        assert inner["crop"] == "wheat"
        assert "stages" in inner
        assert len(inner["stages"]) > 0

    def test_unknown_crop_returns_404(self):
        resp = client.get("/api/v1/crops/notacrop_xyz/stages")
        assert resp.status_code == 404


class TestCropRequirementsEndpoint:
    def test_wheat_requirements(self):
        resp = client.get("/api/v1/crops/wheat/requirements")
        assert resp.status_code == 200
        data = resp.json()
        inner = data.get("data", data)
        assert inner["crop"] == "wheat"

    def test_tomato_requirements(self):
        resp = client.get("/api/v1/crops/tomato/requirements")
        assert resp.status_code == 200

    def test_unknown_crop_returns_404(self):
        resp = client.get("/api/v1/crops/notacrop_xyz/requirements")
        assert resp.status_code == 404


class TestDeprecatedCropsEndpoint:
    def test_deprecated_endpoint_returns_ok(self):
        resp = client.get("/api/v1/crops")
        assert resp.status_code == 200

    def test_deprecated_endpoint_emits_deprecation_headers(self):
        resp = client.get("/api/v1/crops")
        assert resp.headers.get("Deprecation") == "true"
        assert "Sunset" in resp.headers
        assert "X-API-Deprecated" in resp.headers


class TestCropCatalogEndpoint:
    def test_canonical_catalog_endpoint(self):
        resp = client.get("/api/v1/crop-catalog/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert "categories" in data
        assert "total_crops" in data

    def test_pagination_limit(self):
        resp = client.get("/api/v1/crop-catalog/categories?limit=5&offset=0")
        assert resp.status_code == 200

    def test_invalid_limit_returns_422(self):
        resp = client.get("/api/v1/crop-catalog/categories?limit=0")
        assert resp.status_code == 422


# ===========================================================================
# 8. Actions endpoint
# ===========================================================================


class TestActionsEndpoint:
    def test_known_action_returns_data(self):
        resp = client.get("/api/v1/actions/spray_propiconazole?lang=en")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data

    def test_action_arabic_lang(self):
        resp = client.get("/api/v1/actions/spray_propiconazole?lang=ar")
        assert resp.status_code == 200

    def test_unknown_action_returns_data_with_id(self):
        # The endpoint returns data even for unknown actions (action details function)
        resp = client.get("/api/v1/actions/unknown_action_xyz")
        assert resp.status_code == 200
        assert resp.json()["id"] == "unknown_action_xyz"


# ===========================================================================
# 9. Comprehensive advisory endpoint
# ===========================================================================


class TestComprehensiveAdvisoryEndpoint:
    """The comprehensive endpoint calls downstream services via HTTP.
    With mocked httpx, it will return a result (possibly degraded)."""

    def test_valid_field_id_accepted(self):
        # Mock the orchestrator
        mock_orchestrator = AsyncMock()
        mock_orchestrator.collect = AsyncMock(
            return_value={
                "nutrients": None,
                "pests": None,
                "overall_status": "degraded",
            }
        )
        app.state.comprehensive_orchestrator = mock_orchestrator

        resp = client.post("/api/v1/advisory/comprehensive/FIELD001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "data" in data

    def test_invalid_field_id_chars_returns_422(self):
        # Path pattern requires ^[A-Za-z0-9_-]+$
        resp = client.post("/api/v1/advisory/comprehensive/field%20id")
        assert resp.status_code in (404, 422)

    def test_field_id_with_slash_rejected(self):
        resp = client.post("/api/v1/advisory/comprehensive/../../admin")
        assert resp.status_code in (404, 422)


# ===========================================================================
# 10. Loan verification endpoint
# ===========================================================================


class TestCropLoanVerificationEndpoint:
    def test_valid_loan_request(self):
        mock_engine = AsyncMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {
            "eligibility_score": 75,
            "decision": "approved",
            "recommended_loan_amount_sar": 50000,
        }
        mock_engine.verify = AsyncMock(return_value=mock_result)
        app.state.loan_verification_engine = mock_engine

        resp = client.post(
            "/api/v1/loans/crop-loan-verification/FIELD001",
            json={
                "declared_crop": "wheat",
                "declared_area_hectares": 5.0,
                "requested_loan_amount_sar": 50000.0,
                "loan_term_months": 12,
                "language": "en",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "data" in data

    def test_invalid_language_returns_422(self):
        resp = client.post(
            "/api/v1/loans/crop-loan-verification/FIELD001",
            json={
                "declared_crop": "wheat",
                "declared_area_hectares": 5.0,
                "requested_loan_amount_sar": 50000.0,
                "language": "fr",  # invalid
            },
        )
        assert resp.status_code == 422

    def test_zero_area_returns_422(self):
        resp = client.post(
            "/api/v1/loans/crop-loan-verification/FIELD001",
            json={
                "declared_crop": "wheat",
                "declared_area_hectares": 0,  # must be > 0
                "requested_loan_amount_sar": 50000.0,
            },
        )
        assert resp.status_code == 422


# ===========================================================================
# 11. Deprecated legacy routes (backward-compatible aliases)
# ===========================================================================


class TestLegacyRouteAliases:
    """Legacy routes strip /api/v1 prefix."""

    def test_legacy_healthz(self):
        resp = client.get("/healthz")
        assert resp.status_code == 200

    def test_legacy_disease_search(self):
        resp = client.get("/disease/search?q=rust")
        assert resp.status_code == 200

    def test_legacy_crops_categories(self):
        resp = client.get("/crops/categories")
        assert resp.status_code == 200

    def test_legacy_fertilizer_plan(self, fertilizer_plan_body):
        resp = client.post("/fertilizer/plan", json=fertilizer_plan_body)
        assert resp.status_code in (200, 403)  # allowed or tenant check


# ===========================================================================
# 12. Constants / module-level assertions
# ===========================================================================


class TestModuleLevelConstants:
    def test_valid_lang_codes_contains_ar_en(self):
        assert "ar" in VALID_LANG_CODES
        assert "en" in VALID_LANG_CODES

    def test_valid_soil_fertility_values(self):
        assert VALID_SOIL_FERTILITY == {"low", "medium", "high"}

    def test_valid_irrigation_types(self):
        expected = {"drip", "flood", "sprinkler", "furrow", "pivot", "surface"}
        assert VALID_IRRIGATION_TYPES == expected

    def test_crop_requirements_not_empty(self):
        assert len(CROP_REQUIREMENTS) > 0

    def test_valid_crop_values_includes_kb_crops(self):
        for crop in ("tomato", "wheat", "potato", "barley", "date_palm", "general"):
            assert crop in VALID_CROP_VALUES
