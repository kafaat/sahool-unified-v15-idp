"""
Tests for Nutrient Rules Engine - advisory-service
"""

import pytest
from src.engine.nutrient_rules import (
    NutrientAssessment,
    assess_from_ndvi,
    assess_from_soil_test,
    assess_from_visual,
    get_correction_plan,
)


class TestNutrientAssessment:
    """Tests for NutrientAssessment model"""

    def test_to_dict(self):
        a = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="نقص النيتروجين",
            title_en="Nitrogen Deficiency",
            corrections=[{"type": "fertilizer", "product": "urea", "dose_kg_ha": 50}],
            confidence=0.7,
            urgency_hours=48,
            details={"ndvi_value": 0.2},
        )
        d = a.to_dict()
        assert d["deficiency_id"] == "nitrogen_deficiency"
        assert d["nutrient"] == "N"
        assert d["confidence"] == 0.7
        assert len(d["corrections"]) == 1

    def test_default_details(self):
        a = NutrientAssessment(
            deficiency_id="test",
            nutrient="N",
            category="test",
            severity="low",
            title_ar="t",
            title_en="t",
            corrections=[],
            confidence=0.5,
            urgency_hours=72,
        )
        assert a.details == {}
class TestAssessFromNdvi:
    """Tests for assess_from_ndvi function"""

    def test_severe_ndvi(self):
        results = assess_from_ndvi(ndvi=0.2)
        assert len(results) > 0
        assert results[0].nutrient == "N"

    def test_moderate_ndvi(self):
        results = assess_from_ndvi(ndvi=0.4)
        assert len(results) >= 1

    def test_healthy_ndvi(self):
        results = assess_from_ndvi(ndvi=0.7)
        assert len(results) == 0

    def test_with_declining_history(self):
        results = assess_from_ndvi(ndvi=0.4, ndvi_history=[0.6, 0.5, 0.4])
        nutrients = [r.nutrient for r in results]
        assert "P" in nutrients  # Phosphorus from declining trend

    def test_assessment_has_details(self):
        results = assess_from_ndvi(ndvi=0.2)
        assert len(results) > 0
        assert "diagnosis_reason" in results[0].details
        assert "ndvi_value" in results[0].details
class TestAssessFromVisual:
    """Tests for assess_from_visual function"""

    def test_nitrogen_visual_match(self):
        indicators = {
            "leaf_color": "pale_yellow",
            "pattern": "uniform",
            "location": "older_leaves",
        }
        results = assess_from_visual(indicators)
        assert len(results) > 0

    def test_potassium_visual_match(self):
        indicators = {
            "leaf_color": "brown_edges",
            "pattern": "marginal",
            "location": "older_leaves",
        }
        results = assess_from_visual(indicators)
        assert len(results) > 0

    def test_no_match_below_threshold(self):
        indicators = {
            "leaf_color": "completely_unknown",
            "pattern": "unknown_pattern",
            "location": "unknown_location",
        }
        results = assess_from_visual(indicators)
        assert len(results) == 0

    def test_max_3_results(self):
        indicators = {
            "leaf_color": "yellow",
            "pattern": "chlorosis",
            "location": "leaves",
        }
        results = assess_from_visual(indicators)
        assert len(results) <= 3

    def test_sorted_by_confidence(self):
        indicators = {
            "leaf_color": "yellow",
            "pattern": "interveinal",
            "location": "older_leaves",
        }
        results = assess_from_visual(indicators)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].confidence >= results[i + 1].confidence

    def test_lang_ar(self):
        indicators = {
            "leaf_color": "pale_yellow",
            "pattern": "uniform_chlorosis",
            "location": "older_leaves_first",
        }
        results = assess_from_visual(indicators, lang="ar")
        for r in results:
            assert "symptoms" in r.details

    def test_lang_en(self):
        indicators = {
            "leaf_color": "pale_yellow",
            "pattern": "uniform_chlorosis",
            "location": "older_leaves_first",
        }
        results = assess_from_visual(indicators, lang="en")
        for r in results:
            assert "symptoms" in r.details
class TestAssessFromSoilTest:
    """Tests for assess_from_soil_test function"""

    def test_low_nitrogen(self):
        soil = {"N_ppm": 10, "P_ppm": 30, "K_ppm": 200}
        results = assess_from_soil_test(soil, crop="wheat")
        assert len(results) > 0
        nutrients = [r.nutrient for r in results]
        assert "N" in nutrients

    def test_very_low_nitrogen_high_severity(self):
        soil = {"N_ppm": 5}  # Well below low threshold / 2
        results = assess_from_soil_test(soil, crop="wheat")
        n_result = next((r for r in results if r.nutrient == "N"), None)
        assert n_result is not None
        assert n_result.severity == "high"
        assert n_result.confidence == 0.9

    def test_moderate_low_nitrogen(self):
        soil = {"N_ppm": 15}  # Below 20 but above 10 (20/2)
        results = assess_from_soil_test(soil, crop="wheat")
        n_result = next((r for r in results if r.nutrient == "N"), None)
        assert n_result is not None
        assert n_result.severity == "medium"
        assert n_result.confidence == 0.7

    def test_optimal_levels_no_deficiency(self):
        soil = {"N_ppm": 50, "P_ppm": 30, "K_ppm": 250}
        results = assess_from_soil_test(soil, crop="wheat")
        assert len(results) == 0

    def test_multiple_deficiencies(self):
        soil = {"N_ppm": 10, "P_ppm": 5, "K_ppm": 50}
        results = assess_from_soil_test(soil, crop="wheat")
        nutrients = [r.nutrient for r in results]
        assert "N" in nutrients
        assert "P" in nutrients
        assert "K" in nutrients

    def test_missing_nutrient_values(self):
        soil = {}  # No values at all
        results = assess_from_soil_test(soil, crop="wheat")
        assert len(results) == 0

    def test_details_include_soil_value(self):
        soil = {"N_ppm": 10}
        results = assess_from_soil_test(soil, crop="wheat")
        assert len(results) > 0
        assert "soil_value" in results[0].details
        assert "optimal_range" in results[0].details
        assert "deficit_pct" in results[0].details
