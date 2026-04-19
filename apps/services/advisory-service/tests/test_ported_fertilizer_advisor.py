"""
Tests for the two endpoints ported from the archived fertilizer-advisor service:

  GET  /api/v1/fertilizers            — flat fertilizer catalog
  POST /api/v1/soil-analysis/interpret — rule-based soil test interpretation

Both endpoints are stateless and pure (no DB / NATS / downstream calls) so
tests drive them directly via TestClient without any fixture scaffolding.
"""

import pytest

try:
    from fastapi.testclient import TestClient
    from src.main import app
except ImportError:
    pytest.skip("advisory-service dependencies not installed", allow_module_level=True)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /api/v1/fertilizers
# ---------------------------------------------------------------------------


class TestListFertilizers:
    def test_returns_flat_list_with_count(self, client):
        r = client.get("/api/v1/fertilizers")
        assert r.status_code == 200
        body = r.json()
        assert "fertilizers" in body
        assert "count" in body
        assert body["count"] == len(body["fertilizers"])
        assert body["count"] > 0

    def test_entries_carry_id_names_and_analysis(self, client):
        body = client.get("/api/v1/fertilizers").json()
        sample = body["fertilizers"][0]
        # Minimum contract — any future KB edit must keep these keys
        for key in ("id", "name_ar", "name_en", "analysis", "type", "form"):
            assert key in sample, f"expected '{key}' on every fertilizer entry"

    def test_includes_well_known_fertilizers(self, client):
        ids = {f["id"] for f in client.get("/api/v1/fertilizers").json()["fertilizers"]}
        # Core NPK products that existed in the archived fertilizer-advisor
        # catalog — archive had urea + DAP + potassium_sulfate explicitly.
        for expected in ("urea", "dap", "potassium_sulfate"):
            assert expected in ids, f"missing well-known fertilizer '{expected}'"

    def test_npk_percent_shape(self, client):
        fertilizers = client.get("/api/v1/fertilizers").json()["fertilizers"]
        urea = next(f for f in fertilizers if f["id"] == "urea")
        # Urea is 46-0-0 in both the archive and the advisory KB
        assert urea["analysis"]["N"] == 46
        assert urea["analysis"].get("P", 0) == 0
        assert urea["analysis"].get("K", 0) == 0


# ---------------------------------------------------------------------------
# POST /api/v1/soil-analysis/interpret
# ---------------------------------------------------------------------------


def _base_payload(**overrides) -> dict:
    payload = {
        "field_id": "FIELD-001",
        "ph": 7.0,
        "nitrogen_ppm": 30.0,
        "phosphorus_ppm": 20.0,
        "potassium_ppm": 150.0,
        "organic_matter_percent": 2.5,
        "ec_ds_m": 1.0,
        "analysis_date": "2026-04-19",
    }
    payload.update(overrides)
    return payload


class TestInterpretSoilAnalysis:
    def test_balanced_soil_marked_green_everywhere(self, client):
        r = client.post("/api/v1/soil-analysis/interpret", json=_base_payload())
        assert r.status_code == 200
        body = r.json()
        assert body["field_id"] == "FIELD-001"
        # Four greens (pH, N, P, K) — balanced soil stays above the fertility threshold
        greens = sum(1 for i in body["interpretations_ar"] if "🟢" in i)
        assert greens >= 4
        assert body["overall_fertility_en"] == "good"

    def test_acidic_soil_flags_lime_recommendation(self, client):
        r = client.post("/api/v1/soil-analysis/interpret", json=_base_payload(ph=5.0))
        body = r.json()
        assert any("acidic" in msg.lower() for msg in body["interpretations_en"])
        assert any("lime" in rec.lower() for rec in body["recommendations_en"])

    def test_alkaline_soil_flags_sulfur_recommendation(self, client):
        r = client.post("/api/v1/soil-analysis/interpret", json=_base_payload(ph=8.5))
        body = r.json()
        assert any("alkaline" in msg.lower() for msg in body["interpretations_en"])
        assert any("sulfur" in rec.lower() or "acidic" in rec.lower() for rec in body["recommendations_en"])

    def test_nitrogen_deficiency_recommends_urea(self, client):
        r = client.post("/api/v1/soil-analysis/interpret", json=_base_payload(nitrogen_ppm=10.0))
        body = r.json()
        assert any("Nitrogen deficiency" in msg for msg in body["interpretations_en"])
        assert any("urea" in rec.lower() for rec in body["recommendations_en"])

    def test_high_salinity_triggers_leach_recommendation(self, client):
        r = client.post("/api/v1/soil-analysis/interpret", json=_base_payload(ec_ds_m=5.0))
        body = r.json()
        assert any("salinity" in msg.lower() for msg in body["interpretations_en"])
        assert any("leach" in rec.lower() for rec in body["recommendations_en"])

    def test_bilingual_output_parity(self, client):
        """Every interpretation must have an EN and AR counterpart at the same index."""
        r = client.post("/api/v1/soil-analysis/interpret", json=_base_payload(ph=5.0, nitrogen_ppm=10.0))
        body = r.json()
        assert len(body["interpretations_ar"]) == len(body["interpretations_en"])
        assert len(body["recommendations_ar"]) == len(body["recommendations_en"])

    def test_overall_fertility_poor_when_many_deficiencies(self, client):
        r = client.post(
            "/api/v1/soil-analysis/interpret",
            json=_base_payload(
                ph=5.0,
                nitrogen_ppm=5.0,
                phosphorus_ppm=2.0,
                potassium_ppm=20.0,
                organic_matter_percent=0.5,
                ec_ds_m=6.0,
            ),
        )
        body = r.json()
        assert body["overall_fertility_en"] == "poor"

    def test_ph_out_of_range_rejected(self, client):
        # pH clamp is 0..14 per pydantic Field(ge=0, le=14)
        r = client.post("/api/v1/soil-analysis/interpret", json=_base_payload(ph=15.0))
        assert r.status_code == 422

    def test_negative_nutrient_ppm_rejected(self, client):
        r = client.post("/api/v1/soil-analysis/interpret", json=_base_payload(nitrogen_ppm=-1.0))
        assert r.status_code == 422

    def test_field_id_injection_rejected(self, client):
        r = client.post(
            "/api/v1/soil-analysis/interpret",
            json=_base_payload(field_id="FIELD'; DROP TABLE farms;--"),
        )
        # Reuses advisory-service's _validate_identifier (alphanumerics, -, _, ., :)
        assert r.status_code == 422
