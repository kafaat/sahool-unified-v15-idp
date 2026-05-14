"""
Comprehensive unit tests for crop-intelligence-service main.py
اختبارات شاملة لخدمة ذكاء المحاصيل

Covers:
- Feature schema endpoint
- Health & readiness probes
- Root endpoint
- Zone management (create, list, geojson)
- Observation ingest & retrieval
- Field diagnosis (decision engine)
- Zone timeline
- VRT export
- Quick diagnose
- Disease detection & types
- Nutrient detection, fertilizer plan & types
- Yield prediction & crop parameters
- Pest assessment & types
- Comprehensive analysis
- Zone-level disease / nutrient / yield / pest analyses
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# 1. Noop ASGI middleware – replaces TenantContextMiddleware
# ---------------------------------------------------------------------------
class _NoopMiddleware:
    """Transparent ASGI middleware pass-through."""

    def __init__(self, app, **kwargs):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


# ---------------------------------------------------------------------------
# 2. Mock every shared.* dependency BEFORE importing src.main
# ---------------------------------------------------------------------------
_SHARED_MOCKS = [
    "shared",
    "shared.auth",
    "shared.auth.dependencies",
    "shared.auth.models",
    "shared.errors_py",
    "shared.logging_config",
    "shared.middleware",
    "shared.middleware.tenant_context",
    "shared.middleware.security_headers",
    "shared.observability",
    "shared.observability.tracing",
    "shared.cors_config",
    "shared.db",
    "shared.db.simple_migrations",
    "shared.db.ssl",
    "shared.events",
    "shared.events.streams",
    "shared.events.subjects",
    "shared.calibration",
    "shared.calibration.worker",
    "asyncpg",
    "nats",
    "structlog",
    "prometheus_client",
]

for _mod in _SHARED_MOCKS:
    sys.modules.setdefault(_mod, MagicMock())

# Wire up callables invoked at import time
sys.modules["shared.errors_py"].setup_exception_handlers = lambda app: None
sys.modules["shared.errors_py"].add_request_id_middleware = lambda app: None
sys.modules["shared.logging_config"].setup_logging = lambda *a, **kw: None

_mock_tracer = MagicMock()
_mock_tracer.instrument_fastapi = lambda app: None
sys.modules["shared.observability.tracing"].setup_tracing = lambda *a, **kw: _mock_tracer

sys.modules["shared.middleware.tenant_context"].TenantContextMiddleware = _NoopMiddleware
sys.modules["shared.middleware.security_headers"].setup_security_headers = lambda app: None

# Migration helpers – db won't connect during tests; these are just to avoid ImportError
_migration_runner_mock = MagicMock()
_migration_runner_mock.run = AsyncMock()
sys.modules["shared.db.simple_migrations"].Migration = MagicMock(side_effect=lambda **kw: kw)
sys.modules["shared.db.simple_migrations"].SimpleMigrationRunner = MagicMock(return_value=_migration_runner_mock)

# CORS settings must be unpackable as **kwargs for CORSMiddleware
sys.modules["shared.cors_config"].CORS_SETTINGS = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Fake User ­– carries tenant_id so auth checks pass
_FakeUser = type(
    "User",
    (),
    {"id": "user_001", "tenant_id": "tenant_001", "roles": ["admin"], "email": "test@sahool.sa"},
)
_mock_user = _FakeUser()


async def _fake_get_current_user():
    return _mock_user


sys.modules["shared.auth.dependencies"].get_current_user = _fake_get_current_user
sys.modules["shared.auth.models"].User = _FakeUser

# structlog
sys.modules["structlog"].get_logger = MagicMock(return_value=MagicMock())

# asyncpg – create_pool is an async coroutine; DB won't connect (no DATABASE_URL)
sys.modules["asyncpg"].create_pool = AsyncMock(return_value=None)
sys.modules["asyncpg"].Pool = MagicMock

# ---------------------------------------------------------------------------
# 3. Remove DATABASE_URL / NATS_URL so lifespan falls back to in-memory store
# ---------------------------------------------------------------------------
os.environ.pop("DATABASE_URL", None)
os.environ.pop("NATS_URL", None)
os.environ.setdefault("ENVIRONMENT", "test")

# ---------------------------------------------------------------------------
# 4. Add service root to sys.path and import source under test
# ---------------------------------------------------------------------------
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from src.main import (  # noqa: E402
    OBSERVATIONS,
    ZONES,
    _init_sample_data,
    app,
)
from src.main import get_current_user as _real_get_current_user  # noqa: E402

# ---------------------------------------------------------------------------
# 5. Override auth dependency and populate sample data
# ---------------------------------------------------------------------------
app.dependency_overrides[_real_get_current_user] = _fake_get_current_user

# Ensure sample data is present (field_demo with 3 zones)
ZONES.clear()
OBSERVATIONS.clear()
_init_sample_data()

# ---------------------------------------------------------------------------
# 6. Module-level test client
# ---------------------------------------------------------------------------
client = TestClient(app, raise_server_exceptions=True)

# ---------------------------------------------------------------------------
# 7. Shared test payloads
# ---------------------------------------------------------------------------
_GOOD_INDICES: dict = {
    "ndvi": 0.65,
    "evi": 0.50,
    "ndre": 0.20,
    "lci": 0.30,
    "ndwi": -0.05,
    "savi": 0.55,
}

_STRESSED_INDICES: dict = {
    "ndvi": 0.10,
    "evi": 0.08,
    "ndre": 0.05,
    "lci": 0.04,
    "ndwi": -0.40,
    "savi": 0.06,
}

_VALID_OBS = {
    "captured_at": "2025-12-14T10:00:00Z",
    "source": "sentinel-2",
    "growth_stage": "mid",
    "indices": _GOOD_INDICES,
    "cloud_pct": 5.0,
}

# Comprehensive-analysis query params
_CA_PARAMS = (
    "ndvi=0.65&evi=0.50&ndre=0.20&ndwi=-0.05&lci=0.30&savi=0.55"
    "&crop_type=wheat&temp_c=25&humidity_pct=50&field_area_hectares=5.0"
)


# ---------------------------------------------------------------------------
# 8. Autouse fixture to keep sample data fresh between tests
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _refresh_sample_data():
    """Reset in-memory store to a clean baseline before every test."""
    ZONES.clear()
    OBSERVATIONS.clear()
    _init_sample_data()
    yield


# =============================================================================
# Test: Feature Schema
# =============================================================================


class TestFeatureSchema:
    def test_returns_200(self):
        r = client.get("/v1/feature-schema")
        assert r.status_code == 200

    def test_has_version(self):
        data = client.get("/v1/feature-schema").json()
        assert data["version"] == "1.0.0"

    def test_has_service_name(self):
        data = client.get("/v1/feature-schema").json()
        assert data["service"] == "crop-intelligence-service"

    def test_has_features_dict(self):
        data = client.get("/v1/feature-schema").json()
        assert "features" in data
        assert "ndvi" in data["features"]

    def test_quality_requirements_present(self):
        data = client.get("/v1/feature-schema").json()
        assert "quality_requirements" in data


# =============================================================================
# Test: Health Endpoint (/healthz)
# =============================================================================


class TestHealthEndpoint:
    def test_returns_200(self):
        assert client.get("/healthz").status_code == 200

    def test_status_ok(self):
        assert client.get("/healthz").json()["status"] == "ok"

    def test_service_name(self):
        assert client.get("/healthz").json()["service"] == "crop-intelligence-service"

    def test_version_field(self):
        assert client.get("/healthz").json()["version"] == "16.0.0"

    def test_no_extra_errors(self):
        r = client.get("/healthz")
        assert "error" not in r.json()


# =============================================================================
# Test: Readiness Endpoint (/readyz)
# =============================================================================


class TestReadinessEndpoint:
    def test_returns_200_in_test_env(self):
        assert client.get("/readyz").status_code == 200

    def test_status_is_ready(self):
        assert client.get("/readyz").json()["status"] == "ready"

    def test_has_service_name(self):
        assert client.get("/readyz").json()["service"] == "crop-intelligence-service"

    def test_has_checks_dict(self):
        data = client.get("/readyz").json()
        assert "checks" in data

    def test_nats_not_configured(self):
        data = client.get("/readyz").json()
        assert data["checks"]["nats"] == "not_configured"

    def test_db_not_configured(self):
        data = client.get("/readyz").json()
        assert data["checks"]["database"] == "not_configured"


# =============================================================================
# Test: Root Endpoint (/)
# =============================================================================


class TestRootEndpoint:
    def test_returns_200(self):
        assert client.get("/").status_code == 200

    def test_has_service_key(self):
        data = client.get("/").json()
        assert "service" in data

    def test_has_endpoints_key(self):
        data = client.get("/").json()
        assert "endpoints" in data

    def test_has_version(self):
        data = client.get("/").json()
        assert data["version"] == "16.0.0"


# =============================================================================
# Test: Zone Management
# =============================================================================


class TestZoneManagement:
    def test_create_zone_returns_200(self):
        payload = {"name": "New Zone", "name_ar": "منطقة جديدة", "area_hectares": 3.0}
        r = client.post("/api/v1/fields/field_test/zones", json=payload)
        assert r.status_code == 200

    def test_create_zone_returns_zone_id(self):
        payload = {"name": "Zone X", "area_hectares": 2.5}
        r = client.post("/api/v1/fields/field_test/zones", json=payload)
        assert "zone_id" in r.json()

    def test_create_zone_status_created(self):
        payload = {"name": "Zone Y"}
        r = client.post("/api/v1/fields/field_test/zones", json=payload)
        assert r.json()["status"] == "created"

    def test_create_zone_with_geometry(self):
        payload = {
            "name": "Geo Zone",
            "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
            "area_hectares": 1.0,
        }
        r = client.post("/api/v1/fields/field_geo/zones", json=payload)
        assert r.status_code == 200

    def test_list_zones_for_field_demo(self):
        r = client.get("/api/v1/fields/field_demo/zones")
        assert r.status_code == 200
        data = r.json()
        assert "zones" in data
        assert data["count"] >= 3

    def test_list_zones_unknown_field_returns_empty(self):
        r = client.get("/api/v1/fields/no_such_field/zones")
        assert r.status_code == 200
        assert r.json()["count"] == 0

    def test_zones_geojson_field_demo(self):
        r = client.get("/api/v1/fields/field_demo/zones.geojson")
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) >= 3

    def test_zones_geojson_unknown_field_returns_404(self):
        r = client.get("/api/v1/fields/unknown_xyz/zones.geojson")
        assert r.status_code == 404

    def test_list_zones_has_source_field(self):
        r = client.get("/api/v1/fields/field_demo/zones")
        assert "source" in r.json()


# =============================================================================
# Test: Observations
# =============================================================================


class TestObservations:
    def test_ingest_observation_returns_200(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/observations", json=_VALID_OBS)
        assert r.status_code == 200

    def test_ingest_observation_status_stored(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/observations", json=_VALID_OBS)
        assert r.json()["status"] == "stored"

    def test_ingest_observation_returns_ids(self):
        r = client.post("/api/v1/fields/new_field/zones/zone_1/observations", json=_VALID_OBS)
        data = r.json()
        assert data["field_id"] == "new_field"
        assert data["zone_id"] == "zone_1"
        assert "observation_id" in data

    def test_list_observations_existing_zone(self):
        r = client.get("/api/v1/fields/field_demo/zones/zone_a/observations")
        assert r.status_code == 200
        data = r.json()
        assert "observations" in data
        assert data["count"] >= 1

    def test_list_observations_unknown_zone_returns_empty(self):
        r = client.get("/api/v1/fields/field_demo/zones/no_zone/observations")
        assert r.status_code == 200
        assert r.json()["count"] == 0

    def test_list_observations_has_source_field(self):
        r = client.get("/api/v1/fields/field_demo/zones/zone_b/observations")
        assert "source" in r.json()

    def test_ingest_observation_drone_source(self):
        obs = {**_VALID_OBS, "source": "drone", "growth_stage": "rapid"}
        r = client.post("/api/v1/fields/field_drone/zones/zone_d/observations", json=obs)
        assert r.status_code == 200

    def test_list_observations_limit_respected(self):
        for _ in range(5):
            client.post("/api/v1/fields/field_demo/zones/zone_a/observations", json=_VALID_OBS)
        r = client.get("/api/v1/fields/field_demo/zones/zone_a/observations?limit=3")
        assert r.status_code == 200


# =============================================================================
# Test: Field Diagnosis
# =============================================================================


class TestFieldDiagnosis:
    def test_diagnosis_returns_200_for_field_demo(self):
        r = client.get("/api/v1/fields/field_demo/diagnosis?date=2025-12-14")
        assert r.status_code == 200

    def test_diagnosis_has_summary(self):
        r = client.get("/api/v1/fields/field_demo/diagnosis?date=2025-12-14")
        data = r.json()
        assert "summary" in data
        assert "zones_total" in data["summary"]

    def test_diagnosis_has_actions(self):
        r = client.get("/api/v1/fields/field_demo/diagnosis?date=2025-12-14")
        assert "actions" in r.json()

    def test_diagnosis_has_map_layers(self):
        r = client.get("/api/v1/fields/field_demo/diagnosis?date=2025-12-14")
        data = r.json()
        assert "map_layers" in data
        assert "zones_geojson_url" in data["map_layers"]

    def test_diagnosis_invalid_date_returns_400(self):
        r = client.get("/api/v1/fields/field_demo/diagnosis?date=not-a-date")
        assert r.status_code == 400

    def test_diagnosis_unknown_field_returns_404(self):
        r = client.get("/api/v1/fields/no_field_ever/diagnosis?date=2025-01-01")
        assert r.status_code == 404

    def test_diagnosis_zones_total_matches_sample(self):
        r = client.get("/api/v1/fields/field_demo/diagnosis?date=2025-12-14")
        summary = r.json()["summary"]
        assert summary["zones_total"] == 3


# =============================================================================
# Test: Zone Timeline
# =============================================================================


class TestZoneTimeline:
    def test_timeline_returns_200(self):
        r = client.get("/api/v1/fields/field_demo/zones/zone_a/timeline?from=2025-12-01&to=2025-12-31")
        assert r.status_code == 200

    def test_timeline_has_series(self):
        r = client.get("/api/v1/fields/field_demo/zones/zone_a/timeline?from=2025-12-01&to=2025-12-31")
        assert "series" in r.json()

    def test_timeline_has_zone_id(self):
        r = client.get("/api/v1/fields/field_demo/zones/zone_a/timeline?from=2025-12-01&to=2025-12-31")
        assert r.json()["zone_id"] == "zone_a"

    def test_timeline_invalid_from_returns_400(self):
        r = client.get("/api/v1/fields/field_demo/zones/zone_a/timeline?from=bad&to=2025-12-31")
        assert r.status_code == 400

    def test_timeline_unknown_zone_returns_empty_series(self):
        r = client.get("/api/v1/fields/field_demo/zones/ghost_zone/timeline?from=2025-01-01&to=2025-12-31")
        assert r.status_code == 200
        assert r.json()["series"] == []

    def test_timeline_narrow_date_range_may_return_empty(self):
        r = client.get("/api/v1/fields/field_demo/zones/zone_a/timeline?from=2024-01-01&to=2024-01-02")
        assert r.status_code == 200
        assert isinstance(r.json()["series"], list)


# =============================================================================
# Test: VRT Export
# =============================================================================


class TestVRTExport:
    def test_vrt_returns_200_for_field_demo(self):
        r = client.get("/api/v1/fields/field_demo/vrt?date=2025-12-14")
        assert r.status_code == 200

    def test_vrt_feature_collection_type(self):
        r = client.get("/api/v1/fields/field_demo/vrt?date=2025-12-14")
        assert r.json()["type"] == "FeatureCollection"

    def test_vrt_has_features(self):
        r = client.get("/api/v1/fields/field_demo/vrt?date=2025-12-14")
        assert len(r.json()["features"]) >= 3

    def test_vrt_has_metadata(self):
        r = client.get("/api/v1/fields/field_demo/vrt?date=2025-12-14")
        assert "metadata" in r.json()

    def test_vrt_unknown_field_returns_404(self):
        r = client.get("/api/v1/fields/never_existed/vrt?date=2025-12-14")
        assert r.status_code == 404

    def test_vrt_invalid_date_returns_400(self):
        r = client.get("/api/v1/fields/field_demo/vrt?date=notadate")
        assert r.status_code == 400

    def test_vrt_with_action_type_filter(self):
        r = client.get("/api/v1/fields/field_demo/vrt?date=2025-12-14&action_type=irrigation")
        assert r.status_code == 200


# =============================================================================
# Test: Quick Diagnose (/api/v1/diagnose)
# =============================================================================


class TestQuickDiagnose:
    def test_quick_diagnose_healthy_returns_200(self):
        r = client.post("/api/v1/diagnose", json=_VALID_OBS)
        assert r.status_code == 200

    def test_quick_diagnose_has_actions(self):
        r = client.post("/api/v1/diagnose", json=_VALID_OBS)
        data = r.json()
        assert "actions" in data

    def test_quick_diagnose_has_status(self):
        r = client.post("/api/v1/diagnose", json=_VALID_OBS)
        assert "status" in r.json()

    def test_quick_diagnose_has_indices(self):
        r = client.post("/api/v1/diagnose", json=_VALID_OBS)
        assert "indices_received" in r.json()

    def test_quick_diagnose_custom_zone_id(self):
        r = client.post("/api/v1/diagnose?zone_id=custom_zone", json=_VALID_OBS)
        assert r.status_code == 200
        assert r.json()["zone_id"] == "custom_zone"

    def test_quick_diagnose_stressed_still_returns_200(self):
        obs = {**_VALID_OBS, "indices": _STRESSED_INDICES}
        r = client.post("/api/v1/diagnose", json=obs)
        assert r.status_code == 200


# =============================================================================
# Test: Disease Detection
# =============================================================================


class TestDiseaseDetect:
    _PAYLOAD = {**_GOOD_INDICES, "crop_type": "wheat", "humidity_pct": 60.0, "temp_c": 25.0}
    _STRESSED_PAYLOAD = {**_STRESSED_INDICES, "crop_type": "wheat", "humidity_pct": 85.0, "temp_c": 30.0}

    def test_detect_returns_200(self):
        r = client.post("/api/v1/disease/detect", json=self._PAYLOAD)
        assert r.status_code == 200

    def test_detect_has_overall_health(self):
        r = client.post("/api/v1/disease/detect", json=self._PAYLOAD)
        assert "overall_health" in r.json()

    def test_detect_has_detection_count(self):
        r = client.post("/api/v1/disease/detect", json=self._PAYLOAD)
        assert "detection_count" in r.json()

    def test_detect_has_detections_list(self):
        r = client.post("/api/v1/disease/detect", json=self._PAYLOAD)
        assert isinstance(r.json()["detections"], list)

    def test_detect_has_input_indices(self):
        r = client.post("/api/v1/disease/detect", json=self._PAYLOAD)
        assert "input_indices" in r.json()

    def test_detect_has_environmental_context(self):
        r = client.post("/api/v1/disease/detect", json=self._PAYLOAD)
        assert "environmental_context" in r.json()

    def test_detect_stressed_crop_may_detect_disease(self):
        r = client.post("/api/v1/disease/detect", json=self._STRESSED_PAYLOAD)
        assert r.status_code == 200

    def test_detect_with_field_id_publishes_ok(self):
        r = client.post("/api/v1/disease/detect?field_id=field_demo", json=self._PAYLOAD)
        assert r.status_code == 200

    def test_detect_unknown_crop_type_uses_default(self):
        payload = {**self._PAYLOAD, "crop_type": "unknown"}
        r = client.post("/api/v1/disease/detect", json=payload)
        assert r.status_code == 200


# =============================================================================
# Test: Disease Types
# =============================================================================


class TestDiseaseTypes:
    def test_list_disease_types_returns_200(self):
        assert client.get("/api/v1/disease/types").status_code == 200

    def test_list_disease_types_has_disease_types(self):
        data = client.get("/api/v1/disease/types").json()
        assert "disease_types" in data
        assert len(data["disease_types"]) > 0

    def test_list_disease_types_has_crop_types(self):
        data = client.get("/api/v1/disease/types").json()
        assert "crop_types" in data

    def test_list_disease_types_has_severity_levels(self):
        data = client.get("/api/v1/disease/types").json()
        assert "severity_levels" in data

    def test_list_disease_types_has_treatment_types(self):
        data = client.get("/api/v1/disease/types").json()
        assert "treatment_types" in data


# =============================================================================
# Test: Nutrient Detect
# =============================================================================


class TestNutrientDetect:
    _PAYLOAD = {**_GOOD_INDICES, "growth_stage": "vegetative"}
    _DEFICIENT = {**_STRESSED_INDICES, "growth_stage": "mid"}

    def test_detect_nutrients_returns_200(self):
        r = client.post("/api/v1/nutrients/detect", json=self._PAYLOAD)
        assert r.status_code == 200

    def test_detect_nutrients_has_nutrient_status(self):
        r = client.post("/api/v1/nutrients/detect", json=self._PAYLOAD)
        assert "nutrient_status" in r.json()

    def test_detect_nutrients_has_deficiency_count(self):
        r = client.post("/api/v1/nutrients/detect", json=self._PAYLOAD)
        assert "deficiency_count" in r.json()

    def test_detect_nutrients_deficiencies_is_list(self):
        r = client.post("/api/v1/nutrients/detect", json=self._PAYLOAD)
        assert isinstance(r.json()["deficiencies"], list)

    def test_detect_nutrients_has_input_indices(self):
        r = client.post("/api/v1/nutrients/detect", json=self._PAYLOAD)
        assert "input_indices" in r.json()

    def test_detect_nutrients_stressed_returns_200(self):
        r = client.post("/api/v1/nutrients/detect", json=self._DEFICIENT)
        assert r.status_code == 200


# =============================================================================
# Test: Fertilizer Plan
# =============================================================================


class TestFertilizerPlan:
    _PAYLOAD = {**_GOOD_INDICES, "field_area_hectares": 5.0}
    _PAYLOAD_WITH_BUDGET = {**_GOOD_INDICES, "field_area_hectares": 10.0, "budget_usd": 500.0}

    def test_fertilizer_plan_returns_200(self):
        r = client.post("/api/v1/nutrients/fertilizer-plan", json=self._PAYLOAD)
        assert r.status_code == 200

    def test_fertilizer_plan_has_plan(self):
        r = client.post("/api/v1/nutrients/fertilizer-plan", json=self._PAYLOAD)
        assert "fertilizer_plan" in r.json()

    def test_fertilizer_plan_has_nutrient_status(self):
        r = client.post("/api/v1/nutrients/fertilizer-plan", json=self._PAYLOAD)
        assert "nutrient_status" in r.json()

    def test_fertilizer_plan_with_budget(self):
        r = client.post("/api/v1/nutrients/fertilizer-plan", json=self._PAYLOAD_WITH_BUDGET)
        assert r.status_code == 200
        assert r.json()["budget_usd"] == 500.0

    def test_fertilizer_plan_field_area_reflected(self):
        r = client.post("/api/v1/nutrients/fertilizer-plan", json=self._PAYLOAD)
        assert r.json()["field_area_hectares"] == 5.0


# =============================================================================
# Test: Nutrient Types
# =============================================================================


class TestNutrientTypes:
    def test_list_nutrient_types_returns_200(self):
        assert client.get("/api/v1/nutrients/types").status_code == 200

    def test_list_nutrient_types_has_nutrient_types(self):
        data = client.get("/api/v1/nutrients/types").json()
        assert "nutrient_types" in data
        assert len(data["nutrient_types"]) > 0

    def test_list_nutrient_types_has_macronutrients(self):
        data = client.get("/api/v1/nutrients/types").json()
        assert "macronutrients" in data

    def test_list_nutrient_types_has_micronutrients(self):
        data = client.get("/api/v1/nutrients/types").json()
        assert "micronutrients" in data

    def test_list_nutrient_types_has_severity_levels(self):
        data = client.get("/api/v1/nutrients/types").json()
        assert "severity_levels" in data


# =============================================================================
# Test: Yield Prediction
# =============================================================================


class TestYieldPredict:
    _PAYLOAD = {
        **_GOOD_INDICES,
        "crop_type": "wheat",
        "field_area_hectares": 5.0,
        "growth_stage_percent": 60.0,
    }

    def test_yield_predict_returns_200(self):
        r = client.post("/api/v1/yield/predict", json=self._PAYLOAD)
        assert r.status_code == 200

    def test_yield_predict_has_prediction(self):
        r = client.post("/api/v1/yield/predict", json=self._PAYLOAD)
        assert "prediction" in r.json()

    def test_yield_predict_has_total_yield(self):
        r = client.post("/api/v1/yield/predict", json=self._PAYLOAD)
        assert "total_predicted_yield_kg" in r.json()

    def test_yield_predict_total_yield_is_positive(self):
        r = client.post("/api/v1/yield/predict", json=self._PAYLOAD)
        assert r.json()["total_predicted_yield_kg"] > 0

    def test_yield_predict_has_input_indices(self):
        r = client.post("/api/v1/yield/predict", json=self._PAYLOAD)
        assert "input_indices" in r.json()

    def test_yield_predict_unknown_crop_defaults_to_wheat(self):
        payload = {**self._PAYLOAD, "crop_type": "not_a_crop"}
        r = client.post("/api/v1/yield/predict", json=payload)
        assert r.status_code == 200

    def test_yield_predict_with_historical_yield(self):
        payload = {**self._PAYLOAD, "historical_yield_kg_ha": 3500.0}
        r = client.post("/api/v1/yield/predict", json=payload)
        assert r.status_code == 200


# =============================================================================
# Test: Yield Crop Parameters
# =============================================================================


class TestYieldCropParameters:
    def test_all_crop_params_returns_200(self):
        assert client.get("/api/v1/yield/crop-parameters").status_code == 200

    def test_wheat_params_returns_200(self):
        assert client.get("/api/v1/yield/crop-parameters?crop_type=wheat").status_code == 200

    def test_tomato_params_returns_200(self):
        assert client.get("/api/v1/yield/crop-parameters?crop_type=tomato").status_code == 200

    def test_unknown_crop_returns_400(self):
        r = client.get("/api/v1/yield/crop-parameters?crop_type=banana_moon")
        assert r.status_code == 400

    def test_date_palm_params_returns_200(self):
        assert client.get("/api/v1/yield/crop-parameters?crop_type=date_palm").status_code == 200


# =============================================================================
# Test: Pest Assessment
# =============================================================================


class TestPestAssess:
    _PAYLOAD = {
        "temp_c": 28.0,
        "humidity_pct": 65.0,
        "ndvi": 0.65,
        "crop_type": "wheat",
        "season": "summer",
    }
    _HIGH_RISK = {
        "temp_c": 35.0,
        "humidity_pct": 85.0,
        "ndvi": 0.20,
        "crop_type": "wheat",
        "season": "summer",
    }

    def test_pest_assess_returns_200(self):
        r = client.post("/api/v1/pests/assess", json=self._PAYLOAD)
        assert r.status_code == 200

    def test_pest_assess_has_assessment(self):
        r = client.post("/api/v1/pests/assess", json=self._PAYLOAD)
        assert "pest_assessment" in r.json()

    def test_pest_assess_has_risks_count(self):
        r = client.post("/api/v1/pests/assess", json=self._PAYLOAD)
        assert "risks_count" in r.json()

    def test_pest_assess_risks_is_list(self):
        r = client.post("/api/v1/pests/assess", json=self._PAYLOAD)
        assert isinstance(r.json()["risks"], list)

    def test_pest_assess_has_environmental_conditions(self):
        r = client.post("/api/v1/pests/assess", json=self._PAYLOAD)
        assert "environmental_conditions" in r.json()

    def test_pest_assess_high_risk_conditions(self):
        r = client.post("/api/v1/pests/assess", json=self._HIGH_RISK)
        assert r.status_code == 200


# =============================================================================
# Test: Pest Types
# =============================================================================


class TestPestTypes:
    def test_list_pest_types_returns_200(self):
        assert client.get("/api/v1/pests/types").status_code == 200

    def test_list_pest_types_has_pest_types(self):
        data = client.get("/api/v1/pests/types").json()
        assert "pest_types" in data
        assert len(data["pest_types"]) > 0

    def test_list_pest_types_has_risk_levels(self):
        data = client.get("/api/v1/pests/types").json()
        assert "risk_levels" in data


# =============================================================================
# Test: Comprehensive Analysis
# =============================================================================


class TestComprehensiveAnalysis:
    def test_returns_200(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert r.status_code == 200

    def test_has_overall_status(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert "overall_status" in r.json()

    def test_overall_status_valid_value(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert r.json()["overall_status"] in ("critical", "warning", "good")

    def test_has_health_assessment(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert "health_assessment" in r.json()

    def test_has_nutrient_assessment(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert "nutrient_assessment" in r.json()

    def test_has_yield_prediction(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert "yield_prediction" in r.json()

    def test_has_pest_assessment(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert "pest_assessment" in r.json()

    def test_has_input_indices(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert "input_indices" in r.json()

    def test_has_environmental_context(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}")
        assert "environmental_context" in r.json()

    def test_with_field_id_param(self):
        r = client.post(f"/api/v1/comprehensive-analysis?{_CA_PARAMS}&field_id=test_field")
        assert r.status_code == 200

    def test_stressed_indices_may_produce_critical(self):
        stressed_params = (
            "ndvi=0.05&evi=0.03&ndre=0.02&ndwi=-0.5&lci=0.02&savi=0.03"
            "&crop_type=wheat&temp_c=40&humidity_pct=90&field_area_hectares=1.0"
        )
        r = client.post(f"/api/v1/comprehensive-analysis?{stressed_params}")
        assert r.status_code == 200
        assert r.json()["overall_status"] in ("critical", "warning", "good")


# =============================================================================
# Test: Zone-level Disease Analysis
# =============================================================================


class TestZoneDiseaseAnalysis:
    def test_zone_disease_analysis_returns_200(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/disease-analysis")
        assert r.status_code == 200

    def test_zone_disease_analysis_has_overall_health(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/disease-analysis")
        assert "overall_health" in r.json()

    def test_zone_disease_analysis_has_field_id(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/disease-analysis")
        assert r.json()["field_id"] == "field_demo"

    def test_zone_disease_analysis_unknown_zone_returns_404(self):
        r = client.post("/api/v1/fields/field_demo/zones/nonexistent/disease-analysis")
        assert r.status_code == 404

    def test_zone_disease_analysis_has_detections(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_b/disease-analysis")
        assert "detections" in r.json()


# =============================================================================
# Test: Zone-level Nutrient Analysis
# =============================================================================


class TestZoneNutrientAnalysis:
    def test_zone_nutrient_analysis_returns_200(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/nutrient-analysis")
        assert r.status_code == 200

    def test_zone_nutrient_analysis_has_nutrient_status(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/nutrient-analysis")
        assert "nutrient_status" in r.json()

    def test_zone_nutrient_analysis_has_fertilizer_plan(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/nutrient-analysis")
        assert "fertilizer_plan" in r.json()

    def test_zone_nutrient_analysis_unknown_zone_returns_404(self):
        r = client.post("/api/v1/fields/field_demo/zones/ghostzone/nutrient-analysis")
        assert r.status_code == 404

    def test_zone_nutrient_analysis_with_area_param(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_c/nutrient-analysis?field_area_hectares=10.0")
        assert r.status_code == 200


# =============================================================================
# Test: Zone-level Yield Prediction
# =============================================================================


class TestZoneYieldPrediction:
    def test_zone_yield_prediction_returns_200(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/yield-prediction")
        assert r.status_code == 200

    def test_zone_yield_prediction_has_prediction(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/yield-prediction")
        assert "prediction" in r.json()

    def test_zone_yield_prediction_has_field_id(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_a/yield-prediction")
        assert r.json()["field_id"] == "field_demo"

    def test_zone_yield_prediction_unknown_zone_returns_404(self):
        r = client.post("/api/v1/fields/field_demo/zones/phantom/yield-prediction")
        assert r.status_code == 404

    def test_zone_yield_prediction_with_crop_param(self):
        r = client.post("/api/v1/fields/field_demo/zones/zone_b/yield-prediction?crop_type=tomato")
        assert r.status_code == 200


# =============================================================================
# Test: Zone-level Pest Assessment
# =============================================================================


class TestZonePestAssessment:
    _QPARAMS = "temp_c=28&humidity_pct=60"

    def test_zone_pest_assessment_returns_200(self):
        r = client.post(f"/api/v1/fields/field_demo/zones/zone_a/pest-assessment?{self._QPARAMS}")
        assert r.status_code == 200

    def test_zone_pest_assessment_has_pest_assessment(self):
        r = client.post(f"/api/v1/fields/field_demo/zones/zone_a/pest-assessment?{self._QPARAMS}")
        assert "pest_assessment" in r.json()

    def test_zone_pest_assessment_has_field_id(self):
        r = client.post(f"/api/v1/fields/field_demo/zones/zone_a/pest-assessment?{self._QPARAMS}")
        assert r.json()["field_id"] == "field_demo"

    def test_zone_pest_assessment_unknown_zone_returns_404(self):
        r = client.post(f"/api/v1/fields/field_demo/zones/nozone/pest-assessment?{self._QPARAMS}")
        assert r.status_code == 404

    def test_zone_pest_assessment_with_crop_season_params(self):
        r = client.post(
            "/api/v1/fields/field_demo/zones/zone_c/pest-assessment"
            "?temp_c=32&humidity_pct=75&crop_type=wheat&season=summer"
        )
        assert r.status_code == 200
