"""
Unit tests for shared/crop_rotation module.

Tests rotation planner, soil health tracker, helper functions,
compatibility matrix, crop database, and bilingual label support.
"""

import pytest
from datetime import date, timedelta

from shared.crop_rotation.models import (
    CropCharacteristics,
    CropFamily,
    CropHistoryRecord,
    CropType,
    FieldRotationHistory,
    MultiYearPlan,
    NutrientBalance,
    PestBreakRecommendation,
    PestDiseaseRisk,
    PlanStatus,
    RecommendationPriority,
    RotationBenefit,
    RotationRecommendation,
    RotationSequence,
    RotationSlot,
    Season,
    SoilHealthIndicator,
    SoilHealthMeasurement,
    SoilHealthReport,
    SoilHealthTrend,
)
from shared.crop_rotation.planner import (
    CROP_DATABASE,
    PEST_DISEASE_DATABASE,
    ROTATION_COMPATIBILITY,
    CropRotationPlanner,
    RotationPlannerConfig,
    calculate_rotation_score,
    get_crop_arabic_name,
    get_crop_characteristics,
    get_recommended_break_crops,
    get_rotation_compatibility,
)
from shared.crop_rotation.soil_health import (
    CROP_SOIL_IMPACT,
    OPTIMAL_RANGES,
    SoilHealthRating,
    SoilHealthTracker,
    SoilHealthTrackerConfig,
    TrendDirection,
    assess_soil_health_from_measurement,
    calculate_nitrogen_credit,
    get_organic_matter_trend_summary,
)


# =============================================================================
# Crop Database Tests
# =============================================================================


@pytest.mark.unit
class TestCropDatabase:
    """Tests for the CROP_DATABASE constant and crop characteristics lookup."""

    def test_crop_database_has_major_crops(self):
        """All major Middle East crops should be in the database."""
        expected_crops = [
            CropType.WHEAT,
            CropType.BARLEY,
            CropType.MAIZE,
            CropType.ALFALFA,
            CropType.TOMATO,
            CropType.POTATO,
            CropType.DATE_PALM,
            CropType.COTTON,
        ]
        for crop in expected_crops:
            assert crop in CROP_DATABASE, f"{crop.value} missing from CROP_DATABASE"

    def test_crop_database_entries_have_bilingual_names(self):
        """Every crop in the database must have both English and Arabic names."""
        for crop_type, info in CROP_DATABASE.items():
            assert info.name_en, f"{crop_type.value} missing name_en"
            assert info.name_ar, f"{crop_type.value} missing name_ar"

    def test_wheat_is_not_nitrogen_fixer(self):
        wheat = CROP_DATABASE[CropType.WHEAT]
        assert wheat.is_nitrogen_fixer is False
        assert wheat.crop_family == CropFamily.POACEAE

    def test_alfalfa_is_nitrogen_fixer(self):
        alfalfa = CROP_DATABASE[CropType.ALFALFA]
        assert alfalfa.is_nitrogen_fixer is True
        assert alfalfa.residue_nitrogen_kg_ha == 150
        assert alfalfa.crop_family == CropFamily.FABACEAE

    def test_fallow_has_no_water_requirement(self):
        fallow = CROP_DATABASE[CropType.FALLOW]
        assert fallow.water_requirement_mm == 0
        assert fallow.drought_tolerance == 1.0

    def test_date_palm_high_temperature_tolerance(self):
        palm = CROP_DATABASE[CropType.DATE_PALM]
        assert palm.optimal_temp_max_c >= 40.0
        assert palm.growing_season == Season.PERENNIAL


# =============================================================================
# Rotation Compatibility Tests
# =============================================================================


@pytest.mark.unit
class TestRotationCompatibility:
    """Tests for the compatibility matrix and get_rotation_compatibility()."""

    def test_same_crop_low_compatibility(self):
        """Planting the same crop consecutively should score poorly."""
        score = get_rotation_compatibility(CropType.WHEAT, CropType.WHEAT)
        assert score <= 0.3

    def test_legume_before_cereal_high_compatibility(self):
        """Legume followed by cereal should score highly."""
        score = get_rotation_compatibility(CropType.ALFALFA, CropType.WHEAT)
        assert score >= 0.85

    def test_wheat_after_alfalfa_excellent(self):
        score = get_rotation_compatibility(CropType.ALFALFA, CropType.WHEAT)
        assert score >= 0.9

    def test_tomato_after_tomato_very_low(self):
        score = get_rotation_compatibility(CropType.TOMATO, CropType.TOMATO)
        assert score <= 0.2

    def test_same_family_moderate_score(self):
        """Same family (both Solanaceae) should have lower score."""
        score = get_rotation_compatibility(CropType.TOMATO, CropType.POTATO)
        assert score <= 0.4

    def test_unknown_crop_returns_default(self):
        """Crops not in the compatibility matrix should use family-based defaults."""
        # RICE is in CropType but likely not in ROTATION_COMPATIBILITY keys
        score = get_rotation_compatibility(CropType.RICE, CropType.WHEAT)
        assert 0.0 <= score <= 1.0

    def test_legume_to_non_legume_fallback_high(self):
        """When not in matrix, legume->non-legume should score ~0.85."""
        score = get_rotation_compatibility(CropType.CHICKPEA, CropType.ONION)
        assert score >= 0.8


# =============================================================================
# Helper Functions Tests
# =============================================================================


@pytest.mark.unit
class TestHelperFunctions:
    """Tests for standalone helper functions in planner.py."""

    def test_get_crop_characteristics_existing(self):
        result = get_crop_characteristics(CropType.WHEAT)
        assert result is not None
        assert result.crop_type == CropType.WHEAT

    def test_get_crop_characteristics_missing(self):
        """CropTypes not in CROP_DATABASE return None."""
        result = get_crop_characteristics(CropType.LETTUCE)
        assert result is None

    def test_get_crop_arabic_name_known(self):
        name = get_crop_arabic_name(CropType.WHEAT)
        assert name == "قمح"

    def test_get_crop_arabic_name_unknown(self):
        """Unknown crop should return the enum value string."""
        name = get_crop_arabic_name(CropType.LETTUCE)
        assert name == "lettuce"

    def test_get_recommended_break_crops_for_wheat(self):
        breaks = get_recommended_break_crops(CropType.WHEAT, min_score=0.7)
        assert len(breaks) > 0
        # Legumes should be good break crops for wheat
        assert CropType.ALFALFA in breaks

    def test_get_recommended_break_crops_high_threshold(self):
        breaks = get_recommended_break_crops(CropType.WHEAT, min_score=0.95)
        # Very high threshold should return fewer crops
        assert len(breaks) < len(get_recommended_break_crops(CropType.WHEAT, min_score=0.5))

    def test_calculate_rotation_score_single_crop(self):
        """Single crop sequence should return 0.5 (neutral)."""
        score = calculate_rotation_score([CropType.WHEAT])
        assert score == 0.5

    def test_calculate_rotation_score_good_sequence(self):
        """Legume-cereal rotation should score well."""
        score = calculate_rotation_score([CropType.ALFALFA, CropType.WHEAT])
        assert score >= 0.8

    def test_calculate_rotation_score_bad_sequence(self):
        """Same crop repeated should score poorly."""
        score = calculate_rotation_score([CropType.WHEAT, CropType.WHEAT])
        assert score <= 0.3

    def test_calculate_rotation_score_multi_year(self):
        """Multi-year diverse rotation should score reasonably well."""
        sequence = [CropType.WHEAT, CropType.ALFALFA, CropType.TOMATO, CropType.BARLEY]
        score = calculate_rotation_score(sequence)
        assert 0.5 < score <= 1.0


# =============================================================================
# Pest/Disease Database Tests
# =============================================================================


@pytest.mark.unit
class TestPestDiseaseDatabase:
    """Tests for the PEST_DISEASE_DATABASE constant."""

    def test_database_is_not_empty(self):
        assert len(PEST_DISEASE_DATABASE) > 0

    def test_all_entries_have_bilingual_names(self):
        for risk in PEST_DISEASE_DATABASE:
            assert risk.name_en, f"Missing name_en for risk {risk.risk_id}"
            assert risk.name_ar, f"Missing name_ar for risk {risk.risk_id}"

    def test_fusarium_wilt_has_high_persistence(self):
        fusarium = next((r for r in PEST_DISEASE_DATABASE if r.name_en == "Fusarium Wilt"), None)
        assert fusarium is not None
        assert fusarium.soil_persistence_years >= 4
        assert fusarium.yield_loss_potential_percent >= 50.0

    def test_red_palm_weevil_is_pest(self):
        rpw = next((r for r in PEST_DISEASE_DATABASE if "Red Palm Weevil" in r.name_en), None)
        assert rpw is not None
        assert rpw.is_pest is True
        assert rpw.yield_loss_potential_percent == 100.0
        assert CropType.DATE_PALM in rpw.host_crops

    def test_cultural_controls_bilingual(self):
        """Cultural controls should have matching EN/AR lists."""
        for risk in PEST_DISEASE_DATABASE:
            if risk.cultural_controls:
                assert len(risk.cultural_controls_ar) == len(risk.cultural_controls), (
                    f"{risk.name_en}: cultural_controls and cultural_controls_ar length mismatch"
                )


# =============================================================================
# CropRotationPlanner Tests
# =============================================================================


@pytest.mark.unit
class TestCropRotationPlanner:
    """Tests for the CropRotationPlanner class."""

    def _make_planner(self, **kwargs):
        config = RotationPlannerConfig(**kwargs)
        return CropRotationPlanner(config)

    def test_default_initialization(self):
        planner = CropRotationPlanner()
        assert planner.config is not None
        assert planner.crop_db is CROP_DATABASE

    def test_get_crop_info(self):
        planner = CropRotationPlanner()
        info = planner.get_crop_info(CropType.WHEAT)
        assert info is not None
        assert info.name_en == "Wheat"

    def test_get_suitable_crops_winter(self):
        planner = CropRotationPlanner()
        suitable = planner.get_suitable_crops(
            previous_crops=[CropType.TOMATO],
            season=Season.WINTER,
        )
        # Should return crops that grow in winter
        crop_types = [c for c, s in suitable]
        assert CropType.WHEAT in crop_types or CropType.BARLEY in crop_types

    def test_get_suitable_crops_excludes_constrained(self):
        planner = CropRotationPlanner()
        suitable = planner.get_suitable_crops(
            previous_crops=[CropType.TOMATO],
            season=Season.WINTER,
            constraints=["wheat"],
        )
        crop_types = [c for c, s in suitable]
        assert CropType.WHEAT not in crop_types

    def test_get_suitable_crops_sorted_by_score_descending(self):
        planner = CropRotationPlanner()
        suitable = planner.get_suitable_crops(
            previous_crops=[CropType.WHEAT],
            season=Season.WINTER,
        )
        scores = [s for _, s in suitable]
        assert scores == sorted(scores, reverse=True)

    def test_generate_recommendation_returns_recommendation(self):
        planner = CropRotationPlanner()
        rec = planner.generate_recommendation(
            field_id="field-001",
            tenant_id="tenant-001",
            previous_crops=[CropType.WHEAT, CropType.WHEAT],
            season=Season.WINTER,
        )
        assert isinstance(rec, RotationRecommendation)
        assert rec.field_id == "field-001"
        assert rec.recommended_crop is not None
        assert rec.overall_suitability_score > 0

    def test_generate_recommendation_bilingual_reasoning(self):
        planner = CropRotationPlanner()
        rec = planner.generate_recommendation(
            field_id="f1",
            tenant_id="t1",
            previous_crops=[CropType.WHEAT],
            season=Season.SUMMER,
        )
        assert rec.reasoning_en != ""
        assert rec.reasoning_ar != ""

    def test_generate_recommendation_with_soil_ph(self):
        planner = CropRotationPlanner()
        rec = planner.generate_recommendation(
            field_id="f1",
            tenant_id="t1",
            previous_crops=[CropType.WHEAT],
            season=Season.SUMMER,
            field_conditions={"soil_ph": 7.0, "water_available_mm": 500},
        )
        assert rec.recommended_crop is not None

    def test_generate_recommendation_no_previous_crops_fallback(self):
        planner = CropRotationPlanner()
        rec = planner.generate_recommendation(
            field_id="f1",
            tenant_id="t1",
            previous_crops=[],
            season=Season.WINTER,
        )
        assert rec.recommended_crop is not None

    def test_analyze_field_history(self):
        planner = CropRotationPlanner()
        history = FieldRotationHistory(
            field_id="field-001",
            years_of_data=3,
            records=[
                CropHistoryRecord(
                    crop_type=CropType.WHEAT,
                    season=Season.WINTER,
                    year=2023,
                    pest_issues=["aphids"],
                    disease_issues=["rust"],
                ),
                CropHistoryRecord(
                    crop_type=CropType.WHEAT,
                    season=Season.WINTER,
                    year=2024,
                    pest_issues=["aphids"],
                ),
                CropHistoryRecord(
                    crop_type=CropType.ALFALFA,
                    season=Season.SUMMER,
                    year=2024,
                ),
                CropHistoryRecord(
                    crop_type=CropType.WHEAT,
                    season=Season.WINTER,
                    year=2025,
                ),
            ],
        )
        analysis = planner.analyze_field_history(history)
        assert analysis["total_years"] == 3
        assert len(analysis["crops_grown"]) == 4
        # Should detect consecutive same-family crops
        assert analysis["same_family_consecutive_max"] >= 2

    def test_analyze_field_history_empty(self):
        planner = CropRotationPlanner()
        history = FieldRotationHistory(field_id="f1", years_of_data=0, records=[])
        analysis = planner.analyze_field_history(history)
        assert analysis["total_years"] == 0
        assert len(analysis["crops_grown"]) == 0

    def test_analyze_field_history_low_legume_recommendation(self):
        """When legume frequency is low, should recommend increasing legumes."""
        planner = CropRotationPlanner()
        history = FieldRotationHistory(
            field_id="f1",
            years_of_data=3,
            records=[
                CropHistoryRecord(crop_type=CropType.WHEAT, season=Season.WINTER, year=2023),
                CropHistoryRecord(crop_type=CropType.BARLEY, season=Season.WINTER, year=2024),
                CropHistoryRecord(crop_type=CropType.MAIZE, season=Season.SUMMER, year=2024),
                CropHistoryRecord(crop_type=CropType.WHEAT, season=Season.WINTER, year=2025),
                CropHistoryRecord(crop_type=CropType.SORGHUM, season=Season.SUMMER, year=2025),
            ],
        )
        analysis = planner.analyze_field_history(history)
        assert analysis["legume_frequency"] < 20
        # Should have a recommendation about legumes
        combined_recs = " ".join(analysis["recommendations"])
        assert "legume" in combined_recs.lower()


# =============================================================================
# Planner Config Tests
# =============================================================================


@pytest.mark.unit
class TestRotationPlannerConfig:
    """Tests for RotationPlannerConfig defaults and customization."""

    def test_default_weights_approximately_sum_to_one(self):
        config = RotationPlannerConfig()
        total = (
            config.weight_soil_health
            + config.weight_pest_break
            + config.weight_economic
            + config.weight_water
        )
        assert total == pytest.approx(1.0)

    def test_default_prices_include_wheat(self):
        config = RotationPlannerConfig()
        assert "wheat" in config.default_prices
        assert config.default_prices["wheat"] > 0

    def test_custom_config(self):
        config = RotationPlannerConfig(
            planning_horizon_years=3,
            min_legume_frequency_percent=30.0,
            climate_zone="semi-arid",
        )
        assert config.planning_horizon_years == 3
        assert config.min_legume_frequency_percent == 30.0
        assert config.climate_zone == "semi-arid"


# =============================================================================
# Soil Health Tracker Tests
# =============================================================================


@pytest.mark.unit
class TestSoilHealthTracker:
    """Tests for the SoilHealthTracker class."""

    def _make_tracker(self):
        return SoilHealthTracker()

    def _make_measurement(self, field_id="f1", days_ago=0, **kwargs):
        return SoilHealthMeasurement(
            field_id=field_id,
            measurement_date=date.today() - timedelta(days=days_ago),
            **kwargs,
        )

    def test_add_and_get_measurement(self):
        tracker = self._make_tracker()
        m = self._make_measurement(field_id="f1", organic_matter_percent=2.5)
        tracker.add_measurement(m)
        results = tracker.get_measurements("f1")
        assert len(results) == 1
        assert results[0].organic_matter_percent == 2.5

    def test_get_measurements_date_filter(self):
        tracker = self._make_tracker()
        tracker.add_measurement(self._make_measurement("f1", days_ago=400, organic_matter_percent=2.0))
        tracker.add_measurement(self._make_measurement("f1", days_ago=100, organic_matter_percent=2.5))
        tracker.add_measurement(self._make_measurement("f1", days_ago=10, organic_matter_percent=3.0))

        start = date.today() - timedelta(days=200)
        results = tracker.get_measurements("f1", start_date=start)
        assert len(results) == 2

    def test_calculate_soil_health_score_optimal(self):
        tracker = self._make_tracker()
        m = SoilHealthMeasurement(
            organic_matter_percent=3.0,
            nitrogen_available_kg_ha=60.0,
            phosphorus_ppm=35.0,
            potassium_ppm=300.0,
            ph=7.0,
            ec_ds_m=1.0,
            microbial_biomass_mg_kg=350.0,
        )
        score, components = tracker.calculate_soil_health_score(m)
        assert score > 70.0
        assert "organic_matter" in components
        assert "nutrients" in components

    def test_calculate_soil_health_score_poor(self):
        tracker = self._make_tracker()
        m = SoilHealthMeasurement(
            organic_matter_percent=0.3,
            nitrogen_available_kg_ha=5.0,
            phosphorus_ppm=3.0,
            potassium_ppm=50.0,
            ph=4.5,
            ec_ds_m=5.0,
            microbial_biomass_mg_kg=20.0,
        )
        score, components = tracker.calculate_soil_health_score(m)
        assert score < 40.0

    def test_calculate_indicator_trend_improving(self):
        tracker = self._make_tracker()
        # Add measurements showing improvement over time
        tracker.add_measurement(self._make_measurement("f1", days_ago=700, organic_matter_percent=1.5))
        tracker.add_measurement(self._make_measurement("f1", days_ago=350, organic_matter_percent=2.0))
        tracker.add_measurement(self._make_measurement("f1", days_ago=10, organic_matter_percent=2.5))

        trend = tracker.calculate_indicator_trend("f1", SoilHealthIndicator.ORGANIC_MATTER, years=3)
        assert trend.measurement_count == 3
        assert trend.change_percent > 0
        assert trend.trend_direction == TrendDirection.IMPROVING.value

    def test_calculate_indicator_trend_insufficient_data(self):
        tracker = self._make_tracker()
        tracker.add_measurement(self._make_measurement("f1", days_ago=10, organic_matter_percent=2.0))
        trend = tracker.calculate_indicator_trend("f1", SoilHealthIndicator.ORGANIC_MATTER)
        assert trend.measurement_count == 1
        assert trend.trend_direction == "stable"
        assert trend.status == "unknown"

    def test_analyze_rotation_impact_positive(self):
        tracker = self._make_tracker()
        today = date.today()
        crop_history = [
            (CropType.ALFALFA, today - timedelta(days=730), today - timedelta(days=365)),
            (CropType.WHEAT, today - timedelta(days=365), today),
        ]
        analysis = tracker.analyze_rotation_impact("f1", crop_history)
        assert analysis["nitrogen_balance"] > 0  # Alfalfa fixes N
        assert analysis["organic_matter_impact"] > 0

    def test_analyze_rotation_impact_empty(self):
        tracker = self._make_tracker()
        analysis = tracker.analyze_rotation_impact("f1", [])
        assert analysis["rotation_length"] == 0
        assert analysis["overall_impact_rating"] == "neutral"

    def test_estimate_rotation_impact_improving(self):
        tracker = self._make_tracker()
        estimate = tracker.estimate_rotation_impact(
            "f1",
            planned_crops=[CropType.ALFALFA, CropType.GREEN_MANURE, CropType.WHEAT],
        )
        assert estimate["projected_organic_matter_change"] > 0
        assert estimate["projected_soil_health_trend"] == "improving"

    def test_estimate_rotation_impact_no_legumes_warning(self):
        tracker = self._make_tracker()
        estimate = tracker.estimate_rotation_impact(
            "f1",
            planned_crops=[CropType.WHEAT, CropType.MAIZE, CropType.BARLEY],
        )
        risks = " ".join(estimate["risks_identified"])
        assert "legume" in risks.lower() or "nitrogen" in risks.lower()


# =============================================================================
# Soil Health Helper Functions
# =============================================================================


@pytest.mark.unit
class TestSoilHealthHelpers:
    """Tests for standalone helper functions in soil_health.py."""

    def test_assess_soil_health_excellent(self):
        m = SoilHealthMeasurement(
            organic_matter_percent=3.5,
            nitrogen_available_kg_ha=60.0,
            phosphorus_ppm=40.0,
            potassium_ppm=300.0,
            ph=7.0,
            ec_ds_m=1.0,
            microbial_biomass_mg_kg=400.0,
        )
        rating, rating_ar, score = assess_soil_health_from_measurement(m)
        assert score > 60
        assert rating in ("excellent", "good", "fair")
        assert rating_ar in ("ممتاز", "جيد", "مقبول")

    def test_assess_soil_health_returns_arabic(self):
        m = SoilHealthMeasurement(organic_matter_percent=0.3)
        _, rating_ar, _ = assess_soil_health_from_measurement(m)
        assert rating_ar != ""

    def test_calculate_nitrogen_credit_legume(self):
        credit = calculate_nitrogen_credit(CropType.ALFALFA)
        assert credit > 0
        # Alfalfa has 150 residue N, 50% available = 75
        assert credit == pytest.approx(75.0)

    def test_calculate_nitrogen_credit_non_legume(self):
        credit = calculate_nitrogen_credit(CropType.WHEAT)
        assert credit == 0.0

    def test_calculate_nitrogen_credit_with_yield(self):
        credit = calculate_nitrogen_credit(CropType.ALFALFA, yield_tons_ha=15.0)
        # Should be higher than base credit because yield_factor > 1.0
        base_credit = calculate_nitrogen_credit(CropType.ALFALFA)
        assert credit >= base_credit

    def test_calculate_nitrogen_credit_unknown_crop(self):
        credit = calculate_nitrogen_credit(CropType.LETTUCE)
        assert credit == 0.0

    def test_get_organic_matter_trend_insufficient_data(self):
        result = get_organic_matter_trend_summary([])
        assert result["status"] == "insufficient_data"
        assert result["status_ar"] == "بيانات غير كافية"

    def test_get_organic_matter_trend_improving(self):
        measurements = [
            SoilHealthMeasurement(
                measurement_date=date(2024, 1, 1),
                organic_matter_percent=1.5,
            ),
            SoilHealthMeasurement(
                measurement_date=date(2025, 1, 1),
                organic_matter_percent=2.0,
            ),
        ]
        result = get_organic_matter_trend_summary(measurements)
        assert result["status"] == "analyzed"
        assert result["trend"] == "improving"
        assert result["trend_ar"] == "متحسن"
        assert result["change_percent"] > 5

    def test_get_organic_matter_trend_declining(self):
        measurements = [
            SoilHealthMeasurement(
                measurement_date=date(2024, 1, 1),
                organic_matter_percent=3.0,
            ),
            SoilHealthMeasurement(
                measurement_date=date(2025, 1, 1),
                organic_matter_percent=2.0,
            ),
        ]
        result = get_organic_matter_trend_summary(measurements)
        assert result["trend"] == "declining"
        assert result["trend_ar"] == "متراجع"

    def test_get_organic_matter_trend_stable(self):
        measurements = [
            SoilHealthMeasurement(
                measurement_date=date(2024, 1, 1),
                organic_matter_percent=2.5,
            ),
            SoilHealthMeasurement(
                measurement_date=date(2025, 1, 1),
                organic_matter_percent=2.55,
            ),
        ]
        result = get_organic_matter_trend_summary(measurements)
        assert result["trend"] == "stable"


# =============================================================================
# Constants and Ranges Tests
# =============================================================================


@pytest.mark.unit
class TestOptimalRangesAndImpacts:
    """Tests for OPTIMAL_RANGES and CROP_SOIL_IMPACT constants."""

    def test_optimal_ranges_has_key_indicators(self):
        expected = [
            SoilHealthIndicator.ORGANIC_MATTER,
            SoilHealthIndicator.NITROGEN,
            SoilHealthIndicator.PH,
            SoilHealthIndicator.EC,
        ]
        for indicator in expected:
            assert indicator in OPTIMAL_RANGES

    def test_optimal_ranges_have_correct_keys(self):
        for indicator, ranges in OPTIMAL_RANGES.items():
            assert "optimal_min" in ranges, f"{indicator.value} missing optimal_min"
            assert "optimal_max" in ranges, f"{indicator.value} missing optimal_max"
            assert ranges["optimal_min"] <= ranges["optimal_max"]

    def test_crop_soil_impact_alfalfa_positive_nitrogen(self):
        impact = CROP_SOIL_IMPACT.get(CropType.ALFALFA, {})
        assert impact["nitrogen_change"] > 0
        assert impact["organic_matter_change"] > 0

    def test_crop_soil_impact_fallow_negative_om(self):
        impact = CROP_SOIL_IMPACT.get(CropType.FALLOW, {})
        assert impact["organic_matter_change"] < 0

    def test_crop_soil_impact_wheat_negative_nitrogen(self):
        impact = CROP_SOIL_IMPACT.get(CropType.WHEAT, {})
        assert impact["nitrogen_change"] < 0


# =============================================================================
# Additional Model Tests (beyond test_models.py)
# =============================================================================


@pytest.mark.unit
class TestNutrientBalance:
    """Tests for NutrientBalance model."""

    def test_creation_defaults(self):
        nb = NutrientBalance()
        assert nb.balance_id  # UUID
        assert nb.nitrogen_balance == 0.0
        assert nb.is_sustainable is True

    def test_to_dict(self):
        nb = NutrientBalance(
            field_id="f1",
            nitrogen_inputs=100.0,
            nitrogen_outputs=80.0,
            nitrogen_balance=20.0,
            nitrogen_fixation_contribution=50.0,
            is_sustainable=True,
            sustainability_score=75.0,
        )
        d = nb.to_dict()
        assert d["nitrogen"]["inputs"] == 100.0
        assert d["nitrogen"]["balance"] == 20.0
        assert d["is_sustainable"] is True


@pytest.mark.unit
class TestPestBreakRecommendation:
    """Tests for PestBreakRecommendation model."""

    def test_creation_defaults(self):
        rec = PestBreakRecommendation()
        assert rec.priority == RecommendationPriority.MEDIUM
        assert rec.minimum_break_years == 2

    def test_to_dict_bilingual(self):
        rec = PestBreakRecommendation(
            field_id="f1",
            current_crop=CropType.TOMATO,
            recommended_break_crops=[CropType.WHEAT, CropType.ONION],
            reasoning_en="Break disease cycle",
            reasoning_ar="كسر دورة المرض",
            warnings_en=["Monitor for nematodes"],
            warnings_ar=["راقب النيماتودا"],
        )
        d = rec.to_dict()
        assert d["current_crop"] == "tomato"
        assert d["reasoning_en"] == "Break disease cycle"
        assert d["reasoning_ar"] == "كسر دورة المرض"
        assert len(d["warnings_en"]) == 1
        assert len(d["warnings_ar"]) == 1


@pytest.mark.unit
class TestFieldRotationHistory:
    """Tests for FieldRotationHistory model methods."""

    def _make_history(self):
        return FieldRotationHistory(
            field_id="f1",
            years_of_data=3,
            records=[
                CropHistoryRecord(crop_type=CropType.WHEAT, season=Season.WINTER, year=2023),
                CropHistoryRecord(crop_type=CropType.ALFALFA, season=Season.SUMMER, year=2023),
                CropHistoryRecord(crop_type=CropType.TOMATO, season=Season.SUMMER, year=2024),
                CropHistoryRecord(crop_type=CropType.BARLEY, season=Season.WINTER, year=2025),
            ],
        )

    def test_get_last_n_crops(self):
        history = self._make_history()
        last_2 = history.get_last_n_crops(2)
        assert len(last_2) == 2
        # Most recent year first
        assert last_2[0] == CropType.BARLEY

    def test_get_years_since_crop_found(self):
        history = self._make_history()
        years = history.get_years_since_crop(CropType.BARLEY)
        current_year = date.today().year
        assert years == current_year - 2025

    def test_get_years_since_crop_not_found(self):
        history = self._make_history()
        years = history.get_years_since_crop(CropType.COTTON)
        assert years is None

    def test_to_dict(self):
        history = self._make_history()
        d = history.to_dict()
        assert d["field_id"] == "f1"
        assert len(d["records"]) == 4


@pytest.mark.unit
class TestRotationRecommendationModel:
    """Tests for RotationRecommendation model."""

    def test_to_dict_structure(self):
        rec = RotationRecommendation(
            tenant_id="t1",
            field_id="f1",
            previous_crops=[CropType.WHEAT],
            recommended_crop=CropType.ALFALFA,
            recommended_crop_name_ar="برسيم حجازي",
            alternative_crops=[CropType.CLOVER, CropType.FABA_BEAN],
            expected_benefits=[RotationBenefit.NITROGEN_FIXATION],
            overall_suitability_score=85.0,
            reasoning_en="Good rotation choice",
            reasoning_ar="خيار دورة جيد",
            confidence=0.9,
        )
        d = rec.to_dict()
        assert d["recommended_crop"] == "alfalfa"
        assert d["recommended_crop_name_ar"] == "برسيم حجازي"
        assert d["scores"]["overall_suitability"] == 85.0
        assert d["confidence"] == 0.9
        assert "nitrogen_fixation" in d["expected_benefits"]


@pytest.mark.unit
class TestMultiYearPlan:
    """Tests for MultiYearPlan model."""

    def test_creation_defaults(self):
        plan = MultiYearPlan()
        assert plan.start_year == date.today().year
        assert plan.total_years == 5
        assert plan.overall_risk_level == "medium"

    def test_to_dict_has_projections(self):
        plan = MultiYearPlan(
            field_id="f1",
            field_name="Main Field",
            field_name_ar="الحقل الرئيسي",
            total_area_ha=10.0,
            total_projected_profit=50000.0,
            summary_en="Diverse rotation plan",
            summary_ar="خطة دورة متنوعة",
        )
        d = plan.to_dict()
        assert d["field_name_ar"] == "الحقل الرئيسي"
        assert d["projections"]["total_profit"] == 50000.0
        assert d["summary_ar"] == "خطة دورة متنوعة"


# =============================================================================
# Enums Tests (soil_health module enums)
# =============================================================================


@pytest.mark.unit
class TestSoilHealthEnums:
    """Tests for SoilHealthRating and TrendDirection enums."""

    def test_soil_health_rating_values(self):
        assert SoilHealthRating.EXCELLENT == "excellent"
        assert SoilHealthRating.CRITICAL == "critical"

    def test_trend_direction_values(self):
        assert TrendDirection.IMPROVING == "improving"
        assert TrendDirection.STABLE == "stable"
        assert TrendDirection.DECLINING == "declining"
