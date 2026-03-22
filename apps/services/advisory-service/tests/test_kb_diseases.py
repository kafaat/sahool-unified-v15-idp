"""
Tests for Disease Knowledge Base - advisory-service
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.kb.diseases import (
    DISEASES,
    get_disease,
    get_diseases_by_crop,
    search_diseases,
)


class TestGetDisease:
    """Tests for get_disease function"""

    def test_get_existing_disease(self):
        disease = get_disease("tomato_late_blight")
        assert disease is not None
        assert disease["name_en"] == "Late Blight"
        assert disease["crop"] == "tomato"

    def test_get_nonexistent_disease(self):
        assert get_disease("nonexistent") is None

    def test_disease_has_required_fields(self):
        for disease_id, disease in DISEASES.items():
            assert "name_ar" in disease, f"{disease_id} missing name_ar"
            assert "name_en" in disease, f"{disease_id} missing name_en"
            assert "crop" in disease, f"{disease_id} missing crop"
            assert "symptoms_ar" in disease, f"{disease_id} missing symptoms_ar"
            assert "symptoms_en" in disease, f"{disease_id} missing symptoms_en"
            assert "actions" in disease, f"{disease_id} missing actions"
            assert "severity_default" in disease, f"{disease_id} missing severity_default"
            assert "urgency_hours" in disease, f"{disease_id} missing urgency_hours"


class TestGetDiseasesByCrop:
    """Tests for get_diseases_by_crop function"""

    def test_tomato_diseases(self):
        diseases = get_diseases_by_crop("tomato")
        assert len(diseases) > 0
        # All returned diseases should be tomato or general
        for d in diseases:
            assert d["crop"] in ("tomato", "general")

    def test_general_diseases_included(self):
        # General diseases (like aphid) should appear for any crop
        diseases = get_diseases_by_crop("tomato")
        general_ids = [d["id"] for d in diseases if d["crop"] == "general"]
        assert len(general_ids) > 0

    def test_unknown_crop_gets_only_general(self):
        diseases = get_diseases_by_crop("unknown_crop")
        for d in diseases:
            assert d["crop"] == "general"

    def test_result_includes_id(self):
        diseases = get_diseases_by_crop("wheat")
        for d in diseases:
            assert "id" in d


class TestSearchDiseases:
    """Tests for search_diseases function"""

    def test_search_by_arabic_name(self):
        results = search_diseases("لفحة", lang="ar")
        assert len(results) > 0

    def test_search_by_english_name(self):
        results = search_diseases("blight", lang="en")
        assert len(results) > 0
        for r in results:
            assert r["match"] in ("name", "symptom")

    def test_search_by_symptom_ar(self):
        results = search_diseases("اصفرار", lang="ar")
        assert len(results) > 0

    def test_search_by_symptom_en(self):
        results = search_diseases("yellowing", lang="en")
        assert len(results) > 0

    def test_search_no_results(self):
        results = search_diseases("zzzznonexistent", lang="en")
        assert len(results) == 0

    def test_search_case_insensitive(self):
        results_lower = search_diseases("blight", lang="en")
        results_upper = search_diseases("Blight", lang="en")
        assert len(results_lower) == len(results_upper)
