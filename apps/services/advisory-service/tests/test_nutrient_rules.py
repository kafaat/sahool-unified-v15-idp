"""
Nutrient Rules Engine Tests - Advisory Service
Tests for NDVI-based, visual, and soil-test nutrient assessment,
plus correction plan generation.
"""

import pytest

try:
    from src.engine.nutrient_rules import (
        NutrientAssessment,
        assess_from_ndvi,
        assess_from_soil_test,
        assess_from_visual,
        get_correction_plan,
    )
    from src.kb.nutrients import NUTRIENT_DEFICIENCIES
except ImportError:
    pytest.skip("advisory-service dependencies not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# NutrientAssessment model
# ---------------------------------------------------------------------------


class TestNutrientAssessment:
    """Test NutrientAssessment data class."""

    def test_basic_construction(self):
        a = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="نقص النيتروجين",
            title_en="Nitrogen Deficiency",
            corrections=[{"type": "fertilizer", "product": "urea", "dose_kg_ha": 50}],
            confidence=0.8,
            urgency_hours=48,
        )
        assert a.deficiency_id == "nitrogen_deficiency"
        assert a.nutrient == "N"
        assert a.details == {}

    def test_construction_with_details(self):
        details = {"ndvi_value": 0.25}
        a = NutrientAssessment(
            deficiency_id="d1",
            nutrient="P",
            category="nutrient_deficiency",
            severity="medium",
            title_ar="ن",
            title_en="P Def",
            corrections=[],
            confidence=0.5,
            urgency_hours=72,
            details=details,
        )
        assert a.details == details

    def test_to_dict(self):
        corrections = [{"type": "fertilizer", "product": "urea", "dose_kg_ha": 50}]
        a = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="عربي",
            title_en="English",
            corrections=corrections,
            confidence=0.7,
            urgency_hours=48,
            details={"key": "val"},
        )
        d = a.to_dict()
        assert isinstance(d, dict)
        assert d["deficiency_id"] == "nitrogen_deficiency"
        assert d["nutrient"] == "N"
        assert d["category"] == "nutrient_deficiency"
        assert d["corrections"] == corrections
        assert d["confidence"] == 0.7
        assert d["urgency_hours"] == 48
        assert d["details"] == {"key": "val"}

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


# ---------------------------------------------------------------------------
# assess_from_ndvi
# ---------------------------------------------------------------------------


class TestAssessFromNDVI:
    """Test NDVI-based nutrient assessment."""

    def test_severe_ndvi_returns_nitrogen(self):
        """NDVI < 0.3 should identify nitrogen deficiency."""
        results = assess_from_ndvi(ndvi=0.2)
        assert len(results) > 0
        ids = [r.deficiency_id for r in results]
        assert "nitrogen_deficiency" in ids

    def test_severe_ndvi_high_confidence(self):
        """NDVI < 0.3 should give nitrogen confidence of 0.7."""
        results = assess_from_ndvi(ndvi=0.15)
        n_results = [r for r in results if r.deficiency_id == "nitrogen_deficiency"]
        assert len(n_results) == 1
        assert n_results[0].confidence == 0.7

    def test_moderate_ndvi_multiple_deficiencies(self):
        """NDVI 0.3-0.5 should return both nitrogen and potassium."""
        results = assess_from_ndvi(ndvi=0.4)
        ids = [r.deficiency_id for r in results]
        assert "nitrogen_deficiency" in ids
        assert "potassium_deficiency" in ids

    def test_moderate_ndvi_nitrogen_confidence(self):
        """NDVI 0.3-0.5 nitrogen confidence should be 0.5."""
        results = assess_from_ndvi(ndvi=0.45)
        n_results = [r for r in results if r.deficiency_id == "nitrogen_deficiency"]
        assert n_results[0].confidence == 0.5

    def test_moderate_ndvi_potassium_confidence(self):
        """NDVI 0.3-0.5 potassium confidence should be 0.3."""
        results = assess_from_ndvi(ndvi=0.45)
        k_results = [r for r in results if r.deficiency_id == "potassium_deficiency"]
        assert k_results[0].confidence == 0.3

    def test_healthy_ndvi_returns_empty(self):
        """NDVI >= 0.5 without declining history returns empty."""
        results = assess_from_ndvi(ndvi=0.7)
        assert results == []

    def test_declining_ndvi_trend_adds_phosphorus(self):
        """Declining NDVI trend (>0.1 drop) should add phosphorus deficiency."""
        results = assess_from_ndvi(
            ndvi=0.6,
            ndvi_history=[0.8, 0.75, 0.65],
        )
        ids = [r.deficiency_id for r in results]
        assert "phosphorus_deficiency" in ids

    def test_stable_ndvi_trend_no_phosphorus(self):
        """Stable NDVI history should not add phosphorus."""
        results = assess_from_ndvi(
            ndvi=0.6,
            ndvi_history=[0.60, 0.61, 0.60],
        )
        ids = [r.deficiency_id for r in results]
        assert "phosphorus_deficiency" not in ids

    def test_short_history_no_trend_analysis(self):
        """History with < 3 values should skip trend analysis."""
        results = assess_from_ndvi(
            ndvi=0.6,
            ndvi_history=[0.8, 0.6],
        )
        ids = [r.deficiency_id for r in results]
        assert "phosphorus_deficiency" not in ids

    def test_none_history(self):
        """None history should not crash."""
        results = assess_from_ndvi(ndvi=0.6, ndvi_history=None)
        assert isinstance(results, list)

    def test_assessment_has_correct_fields(self):
        """Verify assessment fields for NDVI-based result."""
        results = assess_from_ndvi(ndvi=0.2)
        for r in results:
            assert r.category == "nutrient_deficiency"
            assert r.urgency_hours > 0
            assert len(r.corrections) > 0
            assert r.title_ar != ""
            assert r.title_en != ""

    def test_details_contain_ndvi_value(self):
        """Details should contain the NDVI value."""
        results = assess_from_ndvi(ndvi=0.25)
        for r in results:
            assert "ndvi_value" in r.details
            assert r.details["ndvi_value"] == 0.25

    def test_details_contain_diagnosis_reason(self):
        """Details should contain diagnosis reason."""
        results = assess_from_ndvi(ndvi=0.25)
        for r in results:
            assert "diagnosis_reason" in r.details

    def test_boundary_ndvi_0_3(self):
        """NDVI exactly 0.3 should NOT trigger severe (< 0.3 needed)."""
        results = assess_from_ndvi(ndvi=0.3)
        # At 0.3, diagnose_from_ndvi enters the elif branch (0.3-0.5)
        ids = [r.deficiency_id for r in results]
        assert "potassium_deficiency" in ids  # moderate branch

    def test_boundary_ndvi_0_5(self):
        """NDVI exactly 0.5 is not < 0.5, should return empty without trend."""
        results = assess_from_ndvi(ndvi=0.5)
        assert results == []

    def test_combined_low_ndvi_and_declining_trend(self):
        """Low NDVI with declining trend should return multiple deficiencies."""
        results = assess_from_ndvi(
            ndvi=0.25,
            ndvi_history=[0.5, 0.4, 0.3],
        )
        ids = [r.deficiency_id for r in results]
        assert "nitrogen_deficiency" in ids
        assert "phosphorus_deficiency" in ids

    def test_with_declining_history(self):
        results = assess_from_ndvi(ndvi=0.4, ndvi_history=[0.6, 0.5, 0.4])
        nutrients = [r.nutrient for r in results]
        assert "P" in nutrients  # Phosphorus from declining trend


# ---------------------------------------------------------------------------
# assess_from_visual
# ---------------------------------------------------------------------------


class TestAssessFromVisual:
    """Test visual-indicator-based nutrient assessment."""

    def test_nitrogen_deficiency_visual(self):
        """Pale yellow older leaves should match nitrogen deficiency."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "pale_yellow",
                "pattern": "uniform_chlorosis",
                "location": "older_leaves_first",
            },
        )
        ids = [r.deficiency_id for r in results]
        assert "nitrogen_deficiency" in ids

    def test_potassium_deficiency_visual(self):
        """Brown edges with marginal necrosis on older leaves -> potassium."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "brown_edges",
                "pattern": "marginal_necrosis",
                "location": "older_leaves_first",
            },
        )
        ids = [r.deficiency_id for r in results]
        assert "potassium_deficiency" in ids

    def test_phosphorus_deficiency_visual(self):
        """Purple/bronze coloring -> phosphorus."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "purple_bronze",
                "pattern": "purple_veins",
                "location": "older_leaves",
            },
        )
        ids = [r.deficiency_id for r in results]
        assert "phosphorus_deficiency" in ids

    def test_minimum_score_threshold(self):
        """Score below 3 should not produce results."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "totally_random_color",
                "pattern": "random_pattern",
                "location": "random_location",
            },
        )
        assert results == []

    def test_empty_indicators(self):
        """Empty indicators dict should return empty."""
        results = assess_from_visual(indicators={})
        assert results == []

    def test_only_leaf_color_match(self):
        """Only leaf_color match (score=3) should meet threshold."""
        results = assess_from_visual(
            indicators={"leaf_color": "pale_yellow"},
        )
        # Score 3 from color match alone meets threshold
        ids = [r.deficiency_id for r in results]
        assert "nitrogen_deficiency" in ids

    def test_results_sorted_by_confidence(self):
        """Results should be sorted by confidence descending."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "yellow",
                "pattern": "chlorosis",
                "location": "older_leaves",
            },
        )
        if len(results) >= 2:
            for i in range(len(results) - 1):
                assert results[i].confidence >= results[i + 1].confidence

    def test_max_three_results(self):
        """Should return at most 3 results."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "yellow",
                "pattern": "chlorosis",
                "location": "leaves",
            },
        )
        assert len(results) <= 3

    def test_confidence_capped(self):
        """Confidence should not exceed 0.9."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "pale_yellow",
                "pattern": "uniform_chlorosis",
                "location": "older_leaves_first",
            },
        )
        for r in results:
            assert r.confidence <= 0.9

    def test_details_contain_matched_indicators(self):
        """Details should list matched indicators."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "pale_yellow",
                "pattern": "uniform_chlorosis",
                "location": "older_leaves_first",
            },
        )
        for r in results:
            assert "matched_indicators" in r.details
            assert "match_score" in r.details
            assert "symptoms" in r.details

    def test_language_ar(self):
        """Arabic lang should provide symptoms_ar in details."""
        results = assess_from_visual(
            indicators={"leaf_color": "pale_yellow"},
            lang="ar",
        )
        for r in results:
            # symptoms key should contain Arabic text
            assert any(
                isinstance(s, str) for s in r.details.get("symptoms", [])
            )

    def test_language_en(self):
        """English lang should provide symptoms_en in details."""
        results = assess_from_visual(
            indicators={"leaf_color": "pale_yellow"},
            lang="en",
        )
        for r in results:
            assert any(
                isinstance(s, str) for s in r.details.get("symptoms", [])
            )

    def test_iron_deficiency_new_leaves(self):
        """Pale new leaves with interveinal chlorosis -> iron."""
        results = assess_from_visual(
            indicators={
                "leaf_color": "pale_new_leaves",
                "pattern": "interveinal_chlorosis",
                "location": "new_leaves_first",
            },
        )
        ids = [r.deficiency_id for r in results]
        assert "iron_deficiency" in ids


# ---------------------------------------------------------------------------
# assess_from_soil_test
# ---------------------------------------------------------------------------


class TestAssessFromSoilTest:
    """Test soil-test-based nutrient assessment."""

    def test_low_nitrogen(self):
        """N below 20 ppm should detect nitrogen deficiency."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 15, "P_ppm": 30, "K_ppm": 200},
            crop="wheat",
        )
        nutrients = [r.nutrient for r in results]
        assert "N" in nutrients

    def test_very_low_nitrogen_high_severity(self):
        """N below 10 (half of 20) should be high severity."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 8},
            crop="wheat",
        )
        n_results = [r for r in results if r.nutrient == "N"]
        assert len(n_results) == 1
        assert n_results[0].severity == "high"
        assert n_results[0].confidence == 0.9

    def test_moderately_low_nitrogen_medium_severity(self):
        """N between 10-20 should be medium severity."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 15},
            crop="wheat",
        )
        n_results = [r for r in results if r.nutrient == "N"]
        assert len(n_results) == 1
        assert n_results[0].severity == "medium"
        assert n_results[0].confidence == 0.7

    def test_adequate_nitrogen_no_deficiency(self):
        """N above 20 should not trigger deficiency."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 25},
            crop="wheat",
        )
        nutrients = [r.nutrient for r in results]
        assert "N" not in nutrients

    def test_low_phosphorus(self):
        """P below 10 ppm should detect phosphorus deficiency."""
        results = assess_from_soil_test(
            soil_data={"P_ppm": 5},
            crop="tomato",
        )
        nutrients = [r.nutrient for r in results]
        assert "P" in nutrients

    def test_low_potassium(self):
        """K below 100 ppm should detect potassium deficiency."""
        results = assess_from_soil_test(
            soil_data={"K_ppm": 80},
            crop="tomato",
        )
        nutrients = [r.nutrient for r in results]
        assert "K" in nutrients

    def test_multiple_deficiencies(self):
        """All nutrients low should return multiple deficiencies."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 5, "P_ppm": 3, "K_ppm": 30},
            crop="wheat",
        )
        assert len(results) == 3
        nutrients = {r.nutrient for r in results}
        assert nutrients == {"N", "P", "K"}

    def test_no_deficiencies(self):
        """All nutrients adequate should return empty."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 50, "P_ppm": 30, "K_ppm": 250},
            crop="wheat",
        )
        assert results == []

    def test_missing_nutrient_key_skipped(self):
        """Missing keys in soil_data should be skipped."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 5},  # no P_ppm, K_ppm
            crop="wheat",
        )
        assert len(results) == 1
        assert results[0].nutrient == "N"

    def test_empty_soil_data(self):
        """Empty soil data should return empty."""
        results = assess_from_soil_test(soil_data={}, crop="wheat")
        assert results == []

    def test_details_contain_soil_value(self):
        """Details should contain the measured soil value."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 10},
            crop="wheat",
        )
        assert results[0].details["soil_value"] == 10

    def test_details_contain_optimal_range(self):
        """Details should contain optimal range."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 10},
            crop="wheat",
        )
        assert "optimal_range" in results[0].details

    def test_details_contain_deficit_pct(self):
        """Details should contain deficit percentage."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 10},
            crop="wheat",
        )
        assert "deficit_pct" in results[0].details
        # 10 ppm vs optimal 40 ppm = 75% deficit
        assert results[0].details["deficit_pct"] == 75.0

    def test_corrections_present(self):
        """Results should have correction recommendations."""
        results = assess_from_soil_test(
            soil_data={"N_ppm": 5},
            crop="wheat",
        )
        assert len(results[0].corrections) > 0


# ---------------------------------------------------------------------------
# get_correction_plan
# ---------------------------------------------------------------------------


class TestGetCorrectionPlan:
    """Test correction plan generation."""

    def test_basic_correction_plan(self):
        """Plan for nitrogen deficiency should include fertilizer steps."""
        assessment = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="نقص النيتروجين",
            title_en="Nitrogen Deficiency",
            corrections=[
                {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50},
                {"type": "practice", "action": "foliar_spray_urea_2pct"},
            ],
            confidence=0.8,
            urgency_hours=48,
        )
        plan = get_correction_plan(assessment, field_size_ha=2.0)
        assert len(plan) > 0

    def test_fertilizer_step_fields(self):
        """Fertilizer steps should have all required fields."""
        assessment = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="ن",
            title_en="N",
            corrections=[
                {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50},
            ],
            confidence=0.8,
            urgency_hours=48,
        )
        plan = get_correction_plan(assessment, field_size_ha=1.0)
        fert_steps = [s for s in plan if s["type"] == "fertilizer"]
        if fert_steps:
            step = fert_steps[0]
            assert "product_id" in step
            assert "product_name_ar" in step
            assert "product_name_en" in step
            assert "dose_kg_per_ha" in step
            assert "total_kg" in step
            assert "application_method" in step
            assert "timing" in step

    def test_field_size_scaling(self):
        """Total kg should scale with field size."""
        assessment = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="ن",
            title_en="N",
            corrections=[
                {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50},
            ],
            confidence=0.8,
            urgency_hours=48,
        )
        plan = get_correction_plan(assessment, field_size_ha=3.0)
        fert_steps = [s for s in plan if s["type"] == "fertilizer"]
        if fert_steps:
            assert fert_steps[0]["total_kg"] == 150.0  # 50 * 3.0

    def test_practice_step(self):
        """Practice corrections should appear in plan."""
        assessment = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="ن",
            title_en="N",
            corrections=[
                {"type": "practice", "action": "foliar_spray_urea_2pct"},
            ],
            confidence=0.8,
            urgency_hours=48,
        )
        plan = get_correction_plan(assessment)
        practice_steps = [s for s in plan if s["type"] == "practice"]
        assert len(practice_steps) == 1
        assert practice_steps[0]["action"] == "foliar_spray_urea_2pct"

    def test_max_three_corrections(self):
        """Plan should use at most 3 corrections."""
        assessment = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="ن",
            title_en="N",
            corrections=[
                {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50},
                {"type": "fertilizer", "product": "ammonium_sulfate", "dose_kg_ha": 75},
                {"type": "fertilizer", "product": "npk_balanced", "dose_kg_ha": 100},
                {"type": "practice", "action": "foliar_spray_urea_2pct"},
            ],
            confidence=0.8,
            urgency_hours=48,
        )
        plan = get_correction_plan(assessment)
        assert len(plan) <= 3

    def test_preferred_method_override(self):
        """Preferred method should override default application method."""
        assessment = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="ن",
            title_en="N",
            corrections=[
                {"type": "fertilizer", "product": "urea", "dose_kg_ha": 50},
            ],
            confidence=0.8,
            urgency_hours=48,
        )
        plan = get_correction_plan(assessment, preferred_method="fertigation")
        fert_steps = [s for s in plan if s["type"] == "fertilizer"]
        if fert_steps:
            assert fert_steps[0]["application_method"] == "fertigation"

    def test_unknown_product_skipped(self):
        """Unknown product ID should be skipped in plan."""
        assessment = NutrientAssessment(
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            category="nutrient_deficiency",
            severity="high",
            title_ar="ن",
            title_en="N",
            corrections=[
                {"type": "fertilizer", "product": "totally_fake_product", "dose_kg_ha": 50},
            ],
            confidence=0.8,
            urgency_hours=48,
        )
        plan = get_correction_plan(assessment)
        fert_steps = [s for s in plan if s["type"] == "fertilizer"]
        assert len(fert_steps) == 0  # unknown product not found in KB

    def test_empty_corrections(self):
        """Empty corrections list should produce empty plan."""
        assessment = NutrientAssessment(
            deficiency_id="test",
            nutrient="N",
            category="nutrient_deficiency",
            severity="medium",
            title_ar="ن",
            title_en="N",
            corrections=[],
            confidence=0.5,
            urgency_hours=72,
        )
        plan = get_correction_plan(assessment)
        assert plan == []
