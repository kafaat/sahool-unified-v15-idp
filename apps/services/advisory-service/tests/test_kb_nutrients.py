"""
Tests for Nutrient Knowledge Base - advisory-service
"""

import pytest
from src.kb.nutrients import (
    NUTRIENT_DEFICIENCIES,
    diagnose_from_ndvi,
    get_deficiency,
    get_deficiency_by_nutrient,
)


class TestGetDeficiency:
    """Tests for get_deficiency function"""

    def test_get_existing_deficiency(self):
        d = get_deficiency("nitrogen_deficiency")
        assert d is not None
        assert d["nutrient"] == "N"

    def test_get_nonexistent_deficiency(self):
        assert get_deficiency("nonexistent") is None

    def test_all_deficiencies_have_required_fields(self):
        for def_id, deficiency in NUTRIENT_DEFICIENCIES.items():
            assert "nutrient" in deficiency, f"{def_id} missing nutrient"
            assert "name_ar" in deficiency, f"{def_id} missing name_ar"
            assert "name_en" in deficiency, f"{def_id} missing name_en"
            assert "corrections" in deficiency, f"{def_id} missing corrections"
            assert "severity_default" in deficiency, f"{def_id} missing severity_default"
            assert "urgency_hours" in deficiency, f"{def_id} missing urgency_hours"
            assert "visual_indicators" in deficiency, f"{def_id} missing visual_indicators"


class TestGetDeficiencyByNutrient:
    """Tests for get_deficiency_by_nutrient function"""

    def test_get_nitrogen(self):
        d = get_deficiency_by_nutrient("N")
        assert d is not None
        assert d["nutrient"] == "N"
        assert "id" in d

    def test_get_phosphorus(self):
        d = get_deficiency_by_nutrient("P")
        assert d is not None
        assert d["nutrient"] == "P"

    def test_get_potassium(self):
        d = get_deficiency_by_nutrient("K")
        assert d is not None
        assert d["nutrient"] == "K"

    def test_unknown_nutrient(self):
        assert get_deficiency_by_nutrient("Xx") is None


class TestDiagnoseFromNdvi:
    """Tests for diagnose_from_ndvi function"""

    def test_severe_ndvi_below_poor_cutoff(self):
        """NDVI below the poor cutoff (0.2) = vegetation "poor" status
        = severe nitrogen deficiency hypothesis. Cutoff aligned with
        vegetation-analysis-service status_for_ndvi in PR #1704."""
        diagnoses = diagnose_from_ndvi(0.15)
        assert len(diagnoses) > 0
        ids = [d["id"] for d in diagnoses]
        assert "nitrogen_deficiency" in ids
        # Confidence should be relatively high for severe
        n_diag = next(d for d in diagnoses if d["id"] == "nitrogen_deficiency")
        assert n_diag["confidence"] == 0.7

    def test_moderate_ndvi_between_poor_and_moderate_cutoffs(self):
        """NDVI between 0.2 and 0.4 = vegetation "moderate" status
        = possible N or K deficiency."""
        diagnoses = diagnose_from_ndvi(0.3)
        assert len(diagnoses) >= 2
        ids = [d["id"] for d in diagnoses]
        assert "nitrogen_deficiency" in ids
        assert "potassium_deficiency" in ids

    def test_healthy_ndvi_above_moderate_cutoff(self):
        """NDVI 0.4+ = vegetation "good"/"excellent" — advisory must
        NOT hypothesise a nutrient deficiency on a field the health
        badge shows as good."""
        assert diagnose_from_ndvi(0.5) == []
        assert diagnose_from_ndvi(0.7) == []

    def test_declining_trend_adds_phosphorus(self):
        # Declining trend: 0.6 -> 0.5 -> 0.45 (trend = -0.15)
        history = [0.6, 0.5, 0.45]
        diagnoses = diagnose_from_ndvi(0.45, ndvi_history=history)
        ids = [d["id"] for d in diagnoses]
        assert "phosphorus_deficiency" in ids

    def test_stable_trend_no_phosphorus(self):
        history = [0.6, 0.6, 0.6]
        diagnoses = diagnose_from_ndvi(0.6, ndvi_history=history)
        ids = [d["id"] for d in diagnoses]
        assert "phosphorus_deficiency" not in ids

    def test_short_history_no_trend(self):
        # Less than 3 entries - no trend analysis
        history = [0.6, 0.5]
        diagnoses = diagnose_from_ndvi(0.6, ndvi_history=history)
        ids = [d["id"] for d in diagnoses]
        assert "phosphorus_deficiency" not in ids
