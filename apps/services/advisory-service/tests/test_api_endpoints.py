"""
API Endpoint Tests - Advisory Service
Tests for authenticated disease, nutrient, and fertilizer API endpoints.
Uses dependency override to bypass JWT authentication.
"""

import pytest

try:
    from fastapi.testclient import TestClient
    from src.main import _enforce_tenant, app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    pytest.skip("advisory-service dependencies not installed", allow_module_level=True)


def _fake_user():
    """Create a fake user for testing."""
    try:
        return User(
            id="test-user-001",
            email="test@sahool.sa",
            roles=["farmer"],
            tenant_id="test_tenant",
        )
    except TypeError:
        return User(
            id="test-user-001",
            email="test@sahool.sa",
            hashed_password="fake-hash",
            roles=[],
            tenant_id="test_tenant",
        )


@pytest.fixture
def client():
    """Create test client with auth dependency overridden."""
    app.dependency_overrides[get_current_user] = _fake_user
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tenant enforcement
# ---------------------------------------------------------------------------


class TestTenantEnforcement:
    """Test tenant isolation enforcement."""

    def test_enforce_tenant_matching(self):
        """Matching tenant should not raise."""
        user = _fake_user()
        _enforce_tenant(user, "test_tenant")  # should not raise

    def test_enforce_tenant_mismatch(self):
        """Mismatched tenant should raise 403."""
        from fastapi import HTTPException

        user = _fake_user()
        with pytest.raises(HTTPException) as exc_info:
            _enforce_tenant(user, "different_tenant")
        assert exc_info.value.status_code == 403

    def test_enforce_tenant_no_tenant_on_user(self):
        """User without tenant_id should pass (no restriction)."""
        try:
            user = User(id="u1", email="t@t.com", roles=[], tenant_id=None)
        except TypeError:
            user = User(id="u1", email="t@t.com", hashed_password="x", roles=[], tenant_id=None)
        _enforce_tenant(user, "any_tenant")  # should not raise


# ---------------------------------------------------------------------------
# Disease Assessment API
# ---------------------------------------------------------------------------


class TestDiseaseAssessAPI:
    """Test disease assessment endpoints."""

    def test_assess_disease_success(self, client):
        """Valid disease assessment request."""
        response = client.post(
            "/api/v1/disease/assess",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "condition_id": "tomato_late_blight",
                "confidence": 0.85,
                "crop": "tomato",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"
        assert data["result"] is not None
        assert data["result"]["disease_id"] == "tomato_late_blight"
        assert data["result"]["severity"] == "high"

    def test_assess_disease_low_confidence(self, client):
        """Low confidence should return null result."""
        response = client.post(
            "/api/v1/disease/assess",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "condition_id": "tomato_late_blight",
                "confidence": 0.3,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is None

    def test_assess_disease_unknown_condition(self, client):
        """Unknown condition should return null result."""
        response = client.post(
            "/api/v1/disease/assess",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "condition_id": "nonexistent_disease",
                "confidence": 0.9,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is None

    def test_assess_disease_with_weather(self, client):
        """Weather context should adjust assessment."""
        response = client.post(
            "/api/v1/disease/assess",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "condition_id": "tomato_early_blight",
                "confidence": 0.8,
                "crop": "tomato",
                "weather": {"humidity": 80, "temperature": 26},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] is not None
        # Weather conditions escalate severity
        assert data["result"]["severity"] == "high"

    def test_assess_disease_published_false_no_nats(self, client):
        """Without NATS, published should be false."""
        response = client.post(
            "/api/v1/disease/assess",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "condition_id": "tomato_late_blight",
                "confidence": 0.85,
            },
        )
        data = response.json()
        assert data["published"] is False
        assert data["event_id"] is None


# ---------------------------------------------------------------------------
# Symptom Assessment API
# ---------------------------------------------------------------------------


class TestSymptomAssessAPI:
    """Test symptom-based assessment endpoint."""

    def test_assess_symptoms_success(self, client):
        response = client.post(
            "/api/v1/disease/symptoms",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "crop": "tomato",
                "symptoms": ["بقع مائية على الأوراق", "تعفن الثمار"],
                "lang": "ar",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"
        assert len(data["results"]) > 0
        # tomato_late_blight should be in results
        ids = [r["disease_id"] for r in data["results"]]
        assert "tomato_late_blight" in ids

    def test_assess_symptoms_english(self, client):
        response = client.post(
            "/api/v1/disease/symptoms",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "crop": "wheat",
                "symptoms": ["Orange or brown pustules on leaves"],
                "lang": "en",
            },
        )
        assert response.status_code == 200
        data = response.json()
        ids = [r["disease_id"] for r in data["results"]]
        assert "wheat_rust" in ids

    def test_assess_symptoms_no_match(self, client):
        response = client.post(
            "/api/v1/disease/symptoms",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "crop": "tomato",
                "symptoms": ["completely unrelated text"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert "message" in data


# ---------------------------------------------------------------------------
# NDVI Assessment API
# ---------------------------------------------------------------------------


class TestNDVIAssessAPI:
    """Test NDVI-based nutrient assessment endpoint."""

    def test_ndvi_low_value(self, client):
        response = client.post(
            "/api/v1/nutrient/ndvi",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "ndvi": 0.2,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"
        assert data["ndvi"] == 0.2
        assert len(data["results"]) > 0

    def test_ndvi_healthy_value(self, client):
        response = client.post(
            "/api/v1/nutrient/ndvi",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "ndvi": 0.8,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []

    def test_ndvi_with_history(self, client):
        response = client.post(
            "/api/v1/nutrient/ndvi",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "ndvi": 0.6,
                "ndvi_history": [0.8, 0.75, 0.65],
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Declining trend should add phosphorus
        ids = [r["deficiency_id"] for r in data["results"]]
        assert "phosphorus_deficiency" in ids


# ---------------------------------------------------------------------------
# Visual Assessment API
# ---------------------------------------------------------------------------


class TestVisualAssessAPI:
    """Test visual nutrient assessment endpoint."""

    def test_visual_assessment(self, client):
        response = client.post(
            "/api/v1/nutrient/visual",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "leaf_color": "pale_yellow",
                "pattern": "uniform_chlorosis",
                "location": "older_leaves_first",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"
        assert len(data["results"]) > 0
        ids = [r["deficiency_id"] for r in data["results"]]
        assert "nitrogen_deficiency" in ids

    def test_visual_assessment_no_match(self, client):
        response = client.post(
            "/api/v1/nutrient/visual",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_001",
                "leaf_color": "random_color",
                "pattern": "random_pattern",
                "location": "random_location",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []


# ---------------------------------------------------------------------------
# Nutrient / Deficiency info API
# ---------------------------------------------------------------------------


class TestDeficiencyInfoAPI:
    """Test deficiency info endpoint."""

    def test_get_deficiency_found(self, client):
        response = client.get("/api/v1/nutrient/nitrogen_deficiency")
        assert response.status_code == 200
        data = response.json()
        inner = data.get("data", data)
        assert inner["id"] == "nitrogen_deficiency"

    def test_get_deficiency_not_found(self, client):
        response = client.get("/api/v1/nutrient/nonexistent_deficiency")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Readiness endpoint
# ---------------------------------------------------------------------------


class TestReadiness:
    """Test readiness probe."""

    def test_readyz_when_ready(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["checks"]["engine"] == "loaded"


# ---------------------------------------------------------------------------
# Crop endpoints
# ---------------------------------------------------------------------------


class TestCropEndpoints:
    """Test crop-related endpoints."""

    def test_crop_categories(self, client):
        response = client.get("/api/v1/crops/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert data["total_crops"] > 0

    def test_search_crops(self, client):
        response = client.get("/api/v1/crops/search?q=tomato")
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "tomato"

    def test_search_crops_too_short(self, client):
        response = client.get("/api/v1/crops/search?q=t")
        assert response.status_code == 422

    def test_get_crop_details(self, client):
        response = client.get("/api/v1/crops/tomato")
        assert response.status_code == 200
        data = response.json()
        assert data["code"].lower() == "tomato"
        assert "growing_conditions" in data
        assert "yield_data" in data
        assert "coefficients" in data

    def test_get_crop_details_not_found(self, client):
        response = client.get("/api/v1/crops/nonexistent_crop_xyz")
        assert response.status_code == 404

    def test_get_crop_varieties(self, client):
        response = client.get("/api/v1/crops/tomato/varieties")
        assert response.status_code == 200
        data = response.json()
        assert data["crop_code"] == "tomato"

    def test_get_crop_varieties_not_found(self, client):
        response = client.get("/api/v1/crops/nonexistent_crop_xyz/varieties")
        assert response.status_code == 404

    def test_get_crop_stages_not_found(self, client):
        response = client.get("/api/v1/crops/nonexistent_crop_xyz/stages")
        assert response.status_code == 404

    def test_get_crop_requirements_not_found(self, client):
        response = client.get("/api/v1/crops/nonexistent_crop_xyz/requirements")
        assert response.status_code == 404

    def test_list_all_crops_with_pagination(self, client):
        response = client.get("/api/v1/crops?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 0


# ---------------------------------------------------------------------------
# KB module tests (fertilizers.py coverage)
# ---------------------------------------------------------------------------


class TestFertilizerKB:
    """Test fertilizer knowledge base functions."""

    def test_get_fertilizer_exists(self):
        from src.kb.fertilizers import get_fertilizer

        fert = get_fertilizer("urea")
        assert fert is not None
        assert fert["analysis"]["N"] == 46

    def test_get_fertilizer_not_found(self):
        from src.kb.fertilizers import get_fertilizer

        assert get_fertilizer("nonexistent") is None

    def test_get_fertilizers_by_type(self):
        from src.kb.fertilizers import get_fertilizers_by_type

        nitrogen = get_fertilizers_by_type("nitrogen")
        assert len(nitrogen) > 0
        for f in nitrogen:
            assert f["type"] == "nitrogen"

    def test_get_fertilizers_by_type_empty(self):
        from src.kb.fertilizers import get_fertilizers_by_type

        result = get_fertilizers_by_type("nonexistent_type")
        assert result == []

    def test_calculate_dose(self):
        from src.kb.fertilizers import calculate_dose

        # Urea has 46% N
        # To get 46 kg N/ha: need 100 kg urea/ha
        dose = calculate_dose("urea", "N", 46)
        assert dose == 100.0

    def test_calculate_dose_unknown_fertilizer(self):
        from src.kb.fertilizers import calculate_dose

        assert calculate_dose("nonexistent", "N", 50) is None

    def test_calculate_dose_unknown_nutrient(self):
        from src.kb.fertilizers import calculate_dose

        assert calculate_dose("urea", "Zn", 10) is None

    def test_calculate_dose_zero_nutrient(self):
        from src.kb.fertilizers import calculate_dose

        # Urea has K=0
        assert calculate_dose("urea", "K", 10) is None


# ---------------------------------------------------------------------------
# Disease KB tests
# ---------------------------------------------------------------------------


class TestDiseaseKB:
    """Test disease knowledge base functions."""

    def test_search_diseases_english(self):
        from src.kb.diseases import search_diseases

        results = search_diseases("Blight", lang="en")
        assert len(results) > 0
        assert all("match" in r for r in results)

    def test_search_diseases_no_results(self):
        from src.kb.diseases import search_diseases

        results = search_diseases("zzzznonexistentzzzz", lang="en")
        assert results == []

    def test_search_diseases_by_symptom(self):
        from src.kb.diseases import search_diseases

        results = search_diseases("leaf yellowing", lang="en")
        assert len(results) > 0


# ---------------------------------------------------------------------------
# Nutrient KB tests
# ---------------------------------------------------------------------------


class TestNutrientKB:
    """Test nutrient knowledge base functions."""

    def test_get_deficiency_by_nutrient(self):
        from src.kb.nutrients import get_deficiency_by_nutrient

        result = get_deficiency_by_nutrient("N")
        assert result is not None
        assert result["nutrient"] == "N"
        assert "id" in result

    def test_get_deficiency_by_nutrient_not_found(self):
        from src.kb.nutrients import get_deficiency_by_nutrient

        result = get_deficiency_by_nutrient("Xx")
        assert result is None
