"""
Tests for the three endpoints ported from archived crop-health-ai:

  GET /api/v1/crops                    — supported crops + Arabic labels
  GET /api/v1/diseases/catalog         — named disease catalog (paginated)
  GET /api/v1/treatment/{disease_id}   — per-disease treatment lookup

Also covers the ``disease_catalog`` module directly to keep catalog
integrity tests independent of FastAPI wiring.
"""

from __future__ import annotations

import pytest

try:
    from src.disease_catalog import (
        CROPS_INFO,
        DISEASE_CATALOG,
        get_treatment_details,
        list_named_diseases,
        list_supported_crops,
    )
    from src.disease_detection import CropType, DiseaseSeverity
except Exception:
    pytest.skip(
        "crop-intelligence-service src not importable in this env",
        allow_module_level=True,
    )


# ---------------------------------------------------------------------------
# Catalog integrity (no HTTP needed)
# ---------------------------------------------------------------------------


class TestCatalogIntegrity:
    def test_catalog_has_five_real_diseases_plus_healthy(self):
        # 5 real: wheat_leaf_rust, tomato_late_blight, coffee_leaf_rust,
        # date_palm_bayoud, mango_anthracnose. Plus the healthy sentinel.
        assert "wheat_leaf_rust" in DISEASE_CATALOG
        assert "tomato_late_blight" in DISEASE_CATALOG
        assert "coffee_leaf_rust" in DISEASE_CATALOG
        assert "date_palm_bayoud" in DISEASE_CATALOG
        assert "mango_anthracnose" in DISEASE_CATALOG
        assert "healthy" in DISEASE_CATALOG

    def test_every_entry_has_bilingual_labels_and_severity(self):
        for disease_id, info in DISEASE_CATALOG.items():
            assert isinstance(info.get("name"), str) and info["name"]
            assert isinstance(info.get("name_ar"), str) and info["name_ar"]
            assert isinstance(info.get("severity_default"), DiseaseSeverity)
            assert isinstance(info.get("crop"), CropType), disease_id

    def test_bayoud_marked_critical(self):
        # Yemeni date-palm agriculture — bayoud is lethal, the archive's
        # classification that farmer mobile apps already rely on.
        assert DISEASE_CATALOG["date_palm_bayoud"]["severity_default"] == DiseaseSeverity.CRITICAL

    def test_healthy_has_empty_treatments(self):
        assert DISEASE_CATALOG["healthy"]["treatments"] == []


# ---------------------------------------------------------------------------
# disease_catalog helpers
# ---------------------------------------------------------------------------


class TestListNamedDiseases:
    def test_excludes_healthy(self):
        diseases = list_named_diseases()
        assert all(d["disease_id"] != "healthy" for d in diseases)

    def test_crop_filter_wheat(self):
        diseases = list_named_diseases(CropType.WHEAT)
        assert len(diseases) == 1
        assert diseases[0]["disease_id"] == "wheat_leaf_rust"
        assert diseases[0]["crop"] == "wheat"

    def test_crop_filter_without_matches_returns_empty(self):
        # QAT has no curated disease in the archive catalog
        diseases = list_named_diseases(CropType.QAT)
        assert diseases == []


class TestGetTreatmentDetails:
    def test_known_disease_returns_full_record(self):
        record = get_treatment_details("wheat_leaf_rust")
        assert record is not None
        assert record["disease_id"] == "wheat_leaf_rust"
        assert record["disease_name_ar"] == "صدأ أوراق القمح"
        assert record["severity"] == "medium"
        assert record["treatments"][0]["product_name"] == "Propiconazole 25% EC"
        assert record["prevention"]  # non-empty
        assert record["prevention_ar"]

    def test_unknown_disease_returns_none(self):
        assert get_treatment_details("not_a_real_disease") is None


class TestListSupportedCrops:
    def test_returns_one_entry_per_crop_info_entry(self):
        crops = list_supported_crops()
        assert len(crops) == len(CROPS_INFO)

    def test_includes_yemen_signature_crops(self):
        ids = {c["crop_id"] for c in list_supported_crops()}
        for key in ("coffee", "date_palm", "sorghum"):
            assert key in ids, f"missing '{key}' in supported crops"

    def test_wheat_has_at_least_one_curated_disease(self):
        wheat = next(c for c in list_supported_crops() if c["crop_id"] == "wheat")
        assert wheat["diseases_count"] >= 1


# ---------------------------------------------------------------------------
# HTTP-level smoke tests — run only when the full FastAPI app can be loaded
# ---------------------------------------------------------------------------


class TestHttpEndpoints:
    def test_get_crops_returns_count_plus_crops(self, client):
        r = client.get("/api/v1/crops")
        assert r.status_code == 200
        body = r.json()
        assert "crops" in body
        assert body["count"] == len(body["crops"])
        # Every entry carries bilingual fields
        for entry in body["crops"]:
            assert "crop_id" in entry
            assert "name_ar" in entry
            assert "icon" in entry
            assert "diseases_count" in entry

    def test_get_diseases_catalog_paginates(self, client):
        r = client.get("/api/v1/diseases/catalog?limit=2")
        assert r.status_code == 200
        body = r.json()
        assert body["limit"] == 2
        assert len(body["diseases"]) <= 2
        assert body["total"] >= len(body["diseases"])

    def test_get_diseases_catalog_filter_by_crop(self, client):
        r = client.get("/api/v1/diseases/catalog?crop_type=wheat")
        assert r.status_code == 200
        body = r.json()
        assert all(d["crop"] == "wheat" for d in body["diseases"])

    def test_get_treatment_known_disease(self, client):
        r = client.get("/api/v1/treatment/tomato_late_blight")
        assert r.status_code == 200
        body = r.json()
        assert body["disease_id"] == "tomato_late_blight"
        assert body["severity"] == "high"

    def test_get_treatment_unknown_disease_returns_404(self, client):
        r = client.get("/api/v1/treatment/does_not_exist")
        assert r.status_code == 404
