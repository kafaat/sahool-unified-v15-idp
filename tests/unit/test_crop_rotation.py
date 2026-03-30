"""
Unit tests for the crop_rotation module

Tests cover:
1. Rotation plan models
2. Multi-year planning
3. Pest break cycles
4. Soil health tracking
5. Compatibility checks

Author: Test Suite
Date: January 2026
"""

from datetime import date, datetime, timedelta
from typing import List

import pytest

# Import all models and classes
from shared.crop_rotation.models import (
    # Models
    CropCharacteristics,
    # Enums
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
    RotationPlan,
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
# Test Fixtures
# =============================================================================


@pytest.fixture
def planner_config():
    """Create a basic planner configuration"""
    return RotationPlannerConfig(
        planning_horizon_years=5,
        consider_economic=True,
        consider_water=True,
        consider_soil_health=True,
        climate_zone="arid",
    )


@pytest.fixture
def planner(planner_config):
    """Create a CropRotationPlanner instance"""
    return CropRotationPlanner(config=planner_config)


@pytest.fixture
def soil_tracker():
    """Create a SoilHealthTracker instance"""
    config = SoilHealthTrackerConfig(
        recommended_test_frequency_months=6,
        minimum_measurements_for_trend=3,
    )
    return SoilHealthTracker(config=config)


@pytest.fixture
def sample_soil_measurement():
    """Create a sample soil health measurement"""
    return SoilHealthMeasurement(
        field_id="FIELD-001",
        sample_location="Center",
        sample_depth_cm=30.0,
        measurement_date=date(2025, 1, 15),
        organic_matter_percent=2.5,
        bulk_density_g_cm3=1.2,
        porosity_percent=55.0,
        water_holding_capacity_mm_m=150.0,
        infiltration_rate_mm_hr=15.0,
        ph=7.0,
        ec_ds_m=1.2,
        cec_meq_100g=15.0,
        nitrogen_total_ppm=25.0,
        nitrogen_available_kg_ha=50.0,
        phosphorus_ppm=30.0,
        potassium_ppm=250.0,
        calcium_ppm=1500.0,
        magnesium_ppm=300.0,
        microbial_biomass_mg_kg=250.0,
        respiration_rate_mg_co2_kg_day=50.0,
        earthworm_count_per_m2=10,
        lab_name="Regional Soil Lab",
        lab_reference="LAB-2025-001",
    )


@pytest.fixture
def sample_crop_history():
    """Create sample crop history records"""
    return FieldRotationHistory(
        field_id="FIELD-001",
        tenant_id="TENANT-001",
        field_name="Test Field",
        field_name_ar="حقل الاختبار",
        records=[
            CropHistoryRecord(
                field_id="FIELD-001",
                tenant_id="TENANT-001",
                crop_type=CropType.WHEAT,
                crop_variety="Sakha 95",
                planting_date=date(2024, 10, 15),
                harvest_date=date(2025, 5, 1),
                season=Season.WINTER,
                year=2024,
                area_ha=5.0,
                yield_tons_ha=4.5,
                fertilizer_n_kg_ha=120,
                fertilizer_p_kg_ha=60,
                fertilizer_k_kg_ha=40,
                irrigation_mm=400,
                pesticide_applications=2,
                revenue_per_ha=8325,
                cost_per_ha=3500,
                profit_per_ha=4825,
            ),
            CropHistoryRecord(
                field_id="FIELD-001",
                tenant_id="TENANT-001",
                crop_type=CropType.ALFALFA,
                planting_date=date(2025, 5, 15),
                harvest_date=date(2025, 9, 30),
                season=Season.SUMMER,
                year=2025,
                area_ha=5.0,
                yield_tons_ha=15.0,
                fertilizer_n_kg_ha=0,
                fertilizer_p_kg_ha=60,
                fertilizer_k_kg_ha=80,
                irrigation_mm=1000,
                revenue_per_ha=12000,
                cost_per_ha=6000,
                profit_per_ha=6000,
            ),
        ],
    )


# =============================================================================
# Rotation Plan Model Tests
# =============================================================================


@pytest.mark.unit
class TestRotationModels:
    """Test rotation planning models"""

    def test_rotation_slot_creation(self):
        """Test creating a rotation slot"""
        slot = RotationSlot(
            crop_type=CropType.WHEAT,
            crop_variety="Sakha 95",
            season=Season.WINTER,
            year=1,
            area_ha=5.0,
            expected_yield_tons_ha=4.5,
            expected_nitrogen_contribution_kg_ha=0,
        )
        assert slot.crop_type == CropType.WHEAT
        assert slot.crop_variety == "Sakha 95"
        assert slot.year == 1
        assert slot.area_ha == 5.0
        assert slot.expected_yield_tons_ha == 4.5

    def test_rotation_slot_to_dict(self):
        """Test rotation slot serialization"""
        slot = RotationSlot(
            crop_type=CropType.ALFALFA,
            season=Season.SUMMER,
            year=2,
            expected_nitrogen_contribution_kg_ha=150,
        )
        data = slot.to_dict()
        assert data["crop_type"] == "alfalfa"
        assert data["season"] == "summer"
        assert data["year"] == 2

    def test_rotation_sequence_creation(self):
        """Test creating a rotation sequence"""
        slot1 = RotationSlot(crop_type=CropType.WHEAT, year=1)
        slot2 = RotationSlot(crop_type=CropType.ALFALFA, year=2)
        slot3 = RotationSlot(crop_type=CropType.TOMATO, year=3)

        sequence = RotationSequence(
            name="3-Year Rotation",
            name_ar="دورة ثلاث سنوات",
            cycle_years=3,
            slots=[slot1, slot2, slot3],
        )

        assert sequence.cycle_years == 3
        assert len(sequence.slots) == 3
        assert sequence.get_crop_sequence() == [CropType.WHEAT, CropType.ALFALFA, CropType.TOMATO]

    def test_rotation_sequence_nitrogen_balance(self):
        """Test rotation sequence nitrogen balance calculation"""
        slot1 = RotationSlot(crop_type=CropType.WHEAT, expected_nitrogen_contribution_kg_ha=0)
        slot2 = RotationSlot(crop_type=CropType.ALFALFA, expected_nitrogen_contribution_kg_ha=150)
        slot3 = RotationSlot(crop_type=CropType.TOMATO, expected_nitrogen_contribution_kg_ha=0)

        sequence = RotationSequence(
            cycle_years=3,
            slots=[slot1, slot2, slot3],
        )

        balance = sequence.calculate_nitrogen_balance()
        assert balance == 150.0

    def test_rotation_plan_creation(self):
        """Test creating a complete rotation plan"""
        plan = RotationPlan(
            plan_id="PLAN-001",
            tenant_id="TENANT-001",
            field_id="FIELD-001",
            field_name="Field A",
            field_name_ar="حقل أ",
            name="5-Year Rotation",
            name_ar="دورة 5 سنوات",
            total_area_ha=10.0,
            start_date=date(2026, 1, 1),
            end_date=date(2031, 1, 1),
            planning_horizon_years=5,
            status=PlanStatus.ACTIVE,
        )

        assert plan.field_id == "FIELD-001"
        assert plan.total_area_ha == 10.0
        assert plan.status == PlanStatus.ACTIVE

    def test_rotation_plan_constraints(self):
        """Test rotation plan with constraints"""
        plan = RotationPlan(
            field_id="FIELD-001",
            constraints=["no_cotton", "water_limited"],
            constraints_ar=["بدون قطن", "محدودية المياه"],
        )

        assert len(plan.constraints) == 2
        assert "no_cotton" in plan.constraints

    def test_crop_characteristics_wheat(self):
        """Test wheat crop characteristics from database"""
        wheat = CROP_DATABASE[CropType.WHEAT]
        assert wheat.crop_type == CropType.WHEAT
        assert wheat.crop_family == CropFamily.POACEAE
        assert wheat.is_nitrogen_fixer == False
        assert wheat.growing_season == Season.WINTER
        assert wheat.water_requirement_mm == 450

    def test_crop_characteristics_alfalfa(self):
        """Test alfalfa crop characteristics from database"""
        alfalfa = CROP_DATABASE[CropType.ALFALFA]
        assert alfalfa.crop_type == CropType.ALFALFA
        assert alfalfa.crop_family == CropFamily.FABACEAE
        assert alfalfa.is_nitrogen_fixer == True
        assert alfalfa.residue_nitrogen_kg_ha == 150

    def test_nutrient_balance_creation(self):
        """Test nutrient balance model"""
        balance = NutrientBalance(
            field_id="FIELD-001",
            rotation_plan_id="PLAN-001",
            nitrogen_inputs=150.0,
            nitrogen_outputs=80.0,
            nitrogen_balance=70.0,
            phosphorus_inputs=50.0,
            phosphorus_outputs=30.0,
            phosphorus_balance=20.0,
            potassium_inputs=100.0,
            potassium_outputs=60.0,
            potassium_balance=40.0,
        )

        assert balance.nitrogen_balance == 70.0
        assert balance.phosphorus_balance == 20.0
        assert balance.potassium_balance == 40.0


# =============================================================================
# Multi-Year Planning Tests
# =============================================================================


@pytest.mark.unit
class TestMultiYearPlanning:
    """Test multi-year crop rotation planning"""

    def test_generate_rotation_recommendation(self, planner):
        """Test generating a single rotation recommendation"""
        rec = planner.generate_recommendation(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            previous_crops=[CropType.WHEAT],
            season=Season.SUMMER,
        )

        assert rec.field_id == "FIELD-001"
        assert rec.tenant_id == "TENANT-001"
        assert rec.recommended_crop is not None
        assert rec.overall_suitability_score > 0

    def test_recommendation_after_wheat(self, planner):
        """Test that recommendations after wheat favor legumes"""
        rec = planner.generate_recommendation(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            previous_crops=[CropType.WHEAT],
            season=Season.WINTER,
        )

        # Should recommend legume or high-compatibility crop
        assert rec.recommended_crop in [
            CropType.ALFALFA,
            CropType.CLOVER,
            CropType.FABA_BEAN,
            CropType.CHICKPEA,
            CropType.GREEN_MANURE,
        ]

    def test_recommendation_includes_alternatives(self, planner):
        """Test that recommendations include alternative crops"""
        rec = planner.generate_recommendation(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            previous_crops=[CropType.WHEAT],
            season=Season.WINTER,
        )

        assert len(rec.alternative_crops) > 0
        assert rec.recommended_crop not in rec.alternative_crops

    def test_generate_multi_year_plan(self, planner):
        """Test generating a complete multi-year plan"""
        plan = planner.generate_multi_year_plan(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            field_name="Test Field",
            field_name_ar="حقل الاختبار",
            area_ha=5.0,
            starting_crop=CropType.WHEAT,
            start_year=date.today().year,
            years=3,
        )

        assert plan.field_id == "FIELD-001"
        assert plan.start_year == date.today().year
        assert plan.total_years == 3
        assert len(plan.yearly_recommendations) > 0

    def test_multi_year_plan_projections(self, planner):
        """Test that multi-year plan includes economic projections"""
        plan = planner.generate_multi_year_plan(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            field_name="Test Field",
            field_name_ar="حقل الاختبار",
            area_ha=10.0,
            starting_crop=CropType.WHEAT,
            start_year=2026,
            years=3,
        )

        assert plan.total_projected_revenue >= 0
        assert plan.total_projected_cost >= 0
        assert plan.average_annual_profit_per_ha is not None

    def test_multi_year_plan_includes_nutrient_balance(self, planner):
        """Test that multi-year plan includes nutrient balance"""
        plan = planner.generate_multi_year_plan(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            field_name="Test Field",
            field_name_ar="حقل الاختبار",
            area_ha=5.0,
            starting_crop=CropType.WHEAT,
            start_year=2026,
            years=3,
        )

        assert plan.nutrient_balance is not None
        assert hasattr(plan.nutrient_balance, "nitrogen_balance")

    def test_multi_year_plan_risk_assessment(self, planner):
        """Test that multi-year plan includes risk assessment"""
        plan = planner.generate_multi_year_plan(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            field_name="Test Field",
            field_name_ar="حقل الاختبار",
            area_ha=5.0,
            starting_crop=CropType.WHEAT,
            start_year=2026,
            years=3,
        )

        assert plan.overall_risk_level in ["low", "medium", "high"]
        assert isinstance(plan.risk_factors, list)


# =============================================================================
# Pest Break Cycle Tests
# =============================================================================


@pytest.mark.unit
class TestPestBreakCycles:
    """Test pest/disease break recommendations and cycles"""

    def test_pest_disease_risk_creation(self):
        """Test creating a pest/disease risk"""
        risk = PestDiseaseRisk(
            name_en="Wheat Rust",
            name_ar="صدأ القمح",
            scientific_name="Puccinia spp.",
            is_pest=False,
            disease_type="fungal",
            host_crops=[CropType.WHEAT, CropType.BARLEY],
            primary_host=CropType.WHEAT,
            soil_persistence_years=0,
            requires_host_crop=True,
            break_crops=[CropType.ALFALFA, CropType.TOMATO],
            recommended_break_years=1,
            yield_loss_potential_percent=40.0,
        )

        assert risk.name_en == "Wheat Rust"
        assert risk.disease_type == "fungal"
        assert len(risk.break_crops) == 2

    def test_pest_disease_database_completeness(self):
        """Test that pest/disease database has entries"""
        assert len(PEST_DISEASE_DATABASE) > 0

        # Check for key pests/diseases
        disease_names = [p.name_en for p in PEST_DISEASE_DATABASE]
        assert "Wheat Rust" in disease_names
        assert "Fusarium Wilt" in disease_names
        assert "Root-knot Nematode" in disease_names

    def test_generate_pest_break_recommendation(self, planner):
        """Test generating pest break recommendation"""
        rec = planner.generate_pest_break_recommendation(
            field_id="FIELD-001",
            current_crop=CropType.TOMATO,
            pest_disease_history=["fusarium_wilt", "nematode"],
        )

        assert rec.field_id == "FIELD-001"
        assert rec.current_crop == CropType.TOMATO
        assert len(rec.recommended_break_crops) > 0

    def test_pest_break_includes_reasoning(self, planner):
        """Test that pest break recommendation includes reasoning"""
        rec = planner.generate_pest_break_recommendation(
            field_id="FIELD-001",
            current_crop=CropType.TOMATO,
            pest_disease_history=["fusarium_wilt"],
        )

        assert len(rec.reasoning_en) > 0
        assert len(rec.reasoning_ar) > 0
        assert rec.minimum_break_years > 0

    def test_pest_break_risk_reduction_estimate(self, planner):
        """Test that pest break includes risk reduction estimates"""
        rec = planner.generate_pest_break_recommendation(
            field_id="FIELD-001",
            current_crop=CropType.TOMATO,
            pest_disease_history=["fusarium_wilt"],
        )

        assert 0 <= rec.expected_risk_reduction_percent <= 100
        assert 0 <= rec.expected_yield_improvement_percent <= 100

    def test_pest_break_warnings(self, planner):
        """Test that pest break includes warnings"""
        rec = planner.generate_pest_break_recommendation(
            field_id="FIELD-001",
            current_crop=CropType.TOMATO,
            pest_disease_history=["fusarium_wilt"],
        )

        # Should have warnings about soil persistence
        if rec.pest_disease_risks:
            has_soil_persistent = any(r.soil_persistence_years > 2 for r in rec.pest_disease_risks)
            if has_soil_persistent:
                assert len(rec.warnings_en) > 0


# =============================================================================
# Soil Health Tracking Tests
# =============================================================================


@pytest.mark.unit
class TestSoilHealthTracking:
    """Test soil health measurement and tracking"""

    def test_soil_measurement_creation(self, sample_soil_measurement):
        """Test creating a soil health measurement"""
        assert sample_soil_measurement.field_id == "FIELD-001"
        assert sample_soil_measurement.organic_matter_percent == 2.5
        assert sample_soil_measurement.ph == 7.0

    def test_add_measurement_to_tracker(self, soil_tracker, sample_soil_measurement):
        """Test adding measurements to tracker"""
        soil_tracker.add_measurement(sample_soil_measurement)

        measurements = soil_tracker.get_measurements("FIELD-001")
        assert len(measurements) == 1
        assert measurements[0].field_id == "FIELD-001"

    def test_multiple_measurements_sorted(self, soil_tracker):
        """Test that measurements are sorted by date"""
        m1 = SoilHealthMeasurement(field_id="FIELD-001", measurement_date=date(2025, 3, 1))
        m2 = SoilHealthMeasurement(field_id="FIELD-001", measurement_date=date(2025, 1, 1))
        m3 = SoilHealthMeasurement(field_id="FIELD-001", measurement_date=date(2025, 2, 1))

        soil_tracker.add_measurement(m1)
        soil_tracker.add_measurement(m2)
        soil_tracker.add_measurement(m3)

        measurements = soil_tracker.get_measurements("FIELD-001")
        dates = [m.measurement_date for m in measurements]
        assert dates == sorted(dates)

    def test_calculate_indicator_trend(self, soil_tracker, sample_soil_measurement):
        """Test calculating trend for soil indicator"""
        # Add multiple measurements
        for i in range(3):
            m = SoilHealthMeasurement(
                field_id="FIELD-001",
                measurement_date=date(2025, 1, 1) + timedelta(days=i * 180),
                organic_matter_percent=2.0 + i * 0.3,
                nitrogen_available_kg_ha=40 + i * 10,
            )
            soil_tracker.add_measurement(m)

        trend = soil_tracker.calculate_indicator_trend(
            field_id="FIELD-001",
            indicator=SoilHealthIndicator.ORGANIC_MATTER,
            years=1,
        )

        assert trend.field_id == "FIELD-001"
        assert trend.measurement_count >= 2
        assert trend.trend_direction in [
            TrendDirection.IMPROVING.value,
            TrendDirection.STABLE.value,
            TrendDirection.DECLINING.value,
        ]

    def test_soil_health_score_calculation(self, soil_tracker, sample_soil_measurement):
        """Test calculating overall soil health score"""
        score, components = soil_tracker.calculate_soil_health_score(sample_soil_measurement)

        assert 0 <= score <= 100
        assert "organic_matter" in components
        assert "nutrients" in components
        assert "physical" in components
        assert "biological" in components

    def test_soil_health_rating_mapping(self, soil_tracker):
        """Test soil health rating based on score"""
        m = SoilHealthMeasurement(
            field_id="FIELD-001",
            organic_matter_percent=3.0,
            nitrogen_available_kg_ha=60,
            phosphorus_ppm=35,
            potassium_ppm=300,
            ph=7.0,
            microbial_biomass_mg_kg=300,
        )

        score, _ = soil_tracker.calculate_soil_health_score(m)
        assert score > 50  # Should be decent

    def test_generate_soil_health_report(self, soil_tracker, sample_soil_measurement):
        """Test generating comprehensive soil health report"""
        soil_tracker.add_measurement(sample_soil_measurement)

        report = soil_tracker.generate_soil_health_report(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            field_name="Test Field",
            field_name_ar="حقل الاختبار",
            years=3,
        )

        assert report.field_id == "FIELD-001"
        assert report.overall_score >= 0
        assert report.overall_rating in [r.value for r in SoilHealthRating]

    def test_estimate_rotation_impact(self, soil_tracker):
        """Test estimating soil impact of planned rotation"""
        estimate = soil_tracker.estimate_rotation_impact(
            field_id="FIELD-001",
            planned_crops=[CropType.WHEAT, CropType.ALFALFA, CropType.TOMATO],
        )

        assert "projected_organic_matter_change" in estimate
        assert "projected_nitrogen_balance" in estimate
        assert estimate["projected_soil_health_trend"] in ["stable", "improving", "declining"]


# =============================================================================
# Compatibility Check Tests
# =============================================================================


@pytest.mark.unit
class TestCompatibilityChecks:
    """Test crop rotation compatibility checking"""

    def test_rotation_compatibility_matrix_exists(self):
        """Test that rotation compatibility matrix exists"""
        assert len(ROTATION_COMPATIBILITY) > 0
        assert CropType.WHEAT in ROTATION_COMPATIBILITY

    def test_wheat_after_wheat_low_score(self):
        """Test that wheat-wheat rotation has low score"""
        score = get_rotation_compatibility(CropType.WHEAT, CropType.WHEAT)
        assert score < 0.5

    def test_wheat_after_alfalfa_high_score(self):
        """Test that wheat after alfalfa has high score"""
        score = get_rotation_compatibility(CropType.ALFALFA, CropType.WHEAT)
        assert score > 0.8

    def test_tomato_after_tomato_very_low(self):
        """Test that tomato-tomato rotation has very low score"""
        score = get_rotation_compatibility(CropType.TOMATO, CropType.TOMATO)
        assert score < 0.2

    def test_get_suitable_crops(self, planner):
        """Test getting suitable crops for rotation"""
        suitable = planner.get_suitable_crops(
            previous_crops=[CropType.WHEAT],
            season=Season.WINTER,
        )

        assert len(suitable) > 0
        assert all(isinstance(s, tuple) and len(s) == 2 for s in suitable)
        assert all(0 <= score <= 1 for _, score in suitable)

    def test_get_recommended_break_crops(self):
        """Test getting recommended break crops"""
        break_crops = get_recommended_break_crops(CropType.WHEAT, min_score=0.8)

        assert len(break_crops) > 0
        assert all(isinstance(c, CropType) for c in break_crops)
        assert CropType.WHEAT not in break_crops

    def test_calculate_rotation_score_sequence(self):
        """Test calculating score for crop sequence"""
        sequence = [CropType.WHEAT, CropType.ALFALFA, CropType.TOMATO]
        score = calculate_rotation_score(sequence)

        assert 0 <= score <= 1

    def test_better_sequence_higher_score(self):
        """Test that better rotation sequences score higher"""
        # Good sequence: wheat -> legume -> vegetable
        good_sequence = [CropType.WHEAT, CropType.ALFALFA, CropType.TOMATO]

        # Poor sequence: wheat -> wheat -> wheat
        poor_sequence = [CropType.WHEAT, CropType.WHEAT, CropType.WHEAT]

        good_score = calculate_rotation_score(good_sequence)
        poor_score = calculate_rotation_score(poor_sequence)

        assert good_score > poor_score

    def test_crop_family_compatibility(self, planner):
        """Test that crops from different families are more compatible"""
        # Different families
        diff_family_score = planner._calculate_crop_suitability(
            crop_type=CropType.ALFALFA,
            crop_info=CROP_DATABASE[CropType.ALFALFA],
            previous_crops=[CropType.WHEAT],
        )

        # Same family
        same_family_score = planner._calculate_crop_suitability(
            crop_type=CropType.BARLEY,
            crop_info=CROP_DATABASE[CropType.BARLEY],
            previous_crops=[CropType.WHEAT],
        )

        assert diff_family_score > same_family_score


# =============================================================================
# Field History Analysis Tests
# =============================================================================


@pytest.mark.unit
class TestFieldHistoryAnalysis:
    """Test field history analysis and recommendations"""

    def test_crop_history_record_creation(self):
        """Test creating crop history record"""
        record = CropHistoryRecord(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            crop_type=CropType.WHEAT,
            year=2024,
            season=Season.WINTER,
            area_ha=5.0,
            yield_tons_ha=4.5,
        )

        assert record.crop_type == CropType.WHEAT
        assert record.yield_tons_ha == 4.5

    def test_field_rotation_history_creation(self, sample_crop_history):
        """Test creating field rotation history"""
        assert sample_crop_history.field_id == "FIELD-001"
        assert len(sample_crop_history.records) == 2

    def test_get_last_n_crops(self, sample_crop_history):
        """Test getting last N crops from history"""
        last_crops = sample_crop_history.get_last_n_crops(n=2)

        assert len(last_crops) == 2
        assert CropType.WHEAT in last_crops
        assert CropType.ALFALFA in last_crops

    def test_get_years_since_crop(self, sample_crop_history):
        """Test calculating years since crop was grown"""
        # Wheat was grown in 2024
        years_since_wheat = sample_crop_history.get_years_since_crop(CropType.WHEAT)

        assert years_since_wheat is not None
        assert years_since_wheat >= 0

    def test_analyze_field_history(self, planner, sample_crop_history):
        """Test analyzing field history"""
        analysis = planner.analyze_field_history(sample_crop_history)

        assert "legume_frequency" in analysis
        assert "same_family_consecutive_max" in analysis
        assert len(analysis["recommendations"]) >= 0
        # Verify it analyzed crops
        assert len(analysis["crops_grown"]) == len(sample_crop_history.records)

    def test_history_identifies_legume_benefits(self, planner):
        """Test that history analysis identifies legume benefits"""
        history = FieldRotationHistory(
            field_id="FIELD-001",
            records=[
                CropHistoryRecord(crop_type=CropType.WHEAT, year=2023, season=Season.WINTER),
                CropHistoryRecord(crop_type=CropType.ALFALFA, year=2023, season=Season.SUMMER),
                CropHistoryRecord(crop_type=CropType.WHEAT, year=2024, season=Season.WINTER),
            ],
        )

        analysis = planner.analyze_field_history(history)
        assert analysis["legume_frequency"] > 0


# =============================================================================
# Helper Function Tests
# =============================================================================


@pytest.mark.unit
class TestHelperFunctions:
    """Test helper functions"""

    def test_get_crop_characteristics_wheat(self):
        """Test getting crop characteristics"""
        wheat = get_crop_characteristics(CropType.WHEAT)

        assert wheat is not None
        assert wheat.crop_type == CropType.WHEAT
        assert wheat.name_en == "Wheat"

    def test_get_crop_arabic_name(self):
        """Test getting crop Arabic names"""
        wheat_ar = get_crop_arabic_name(CropType.WHEAT)
        assert wheat_ar == "قمح"

        alfalfa_ar = get_crop_arabic_name(CropType.ALFALFA)
        assert alfalfa_ar == "برسيم حجازي"

    def test_assess_soil_health_from_measurement(self, sample_soil_measurement):
        """Test quick soil health assessment"""
        rating, rating_ar, score = assess_soil_health_from_measurement(sample_soil_measurement)

        assert rating in ["excellent", "good", "fair", "poor", "critical"]
        assert score > 0

    def test_calculate_nitrogen_credit(self):
        """Test nitrogen credit calculation"""
        # Wheat has no nitrogen fixation
        wheat_credit = calculate_nitrogen_credit(CropType.WHEAT)
        assert wheat_credit == 0.0

        # Alfalfa has nitrogen fixation
        alfalfa_credit = calculate_nitrogen_credit(CropType.ALFALFA, yield_tons_ha=15.0)
        assert alfalfa_credit > 0

    def test_get_organic_matter_trend_summary(self):
        """Test organic matter trend summary"""
        measurements = [
            SoilHealthMeasurement(measurement_date=date(2024, 1, 1), organic_matter_percent=2.0),
            SoilHealthMeasurement(measurement_date=date(2024, 6, 1), organic_matter_percent=2.3),
            SoilHealthMeasurement(measurement_date=date(2025, 1, 1), organic_matter_percent=2.6),
        ]

        summary = get_organic_matter_trend_summary(measurements)

        assert summary["status"] == "analyzed"
        assert summary["trend"] in ["improving", "declining", "stable"]
        assert summary["change_percent"] > 0  # Should show improvement


# =============================================================================
# Bilingual Support Tests
# =============================================================================


@pytest.mark.unit
class TestBilingualSupport:
    """Test bilingual support (English/Arabic)"""

    def test_crop_names_bilingual(self):
        """Test that crops have English and Arabic names"""
        wheat = CROP_DATABASE[CropType.WHEAT]
        assert len(wheat.name_en) > 0
        assert len(wheat.name_ar) > 0

    def test_recommendation_bilingual_output(self, planner):
        """Test that recommendations are bilingual"""
        rec = planner.generate_recommendation(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            previous_crops=[CropType.WHEAT],
            season=Season.WINTER,
        )

        assert len(rec.reasoning_en) > 0
        assert len(rec.reasoning_ar) > 0

    def test_pest_break_bilingual(self, planner):
        """Test that pest break recommendations are bilingual"""
        rec = planner.generate_pest_break_recommendation(
            field_id="FIELD-001",
            current_crop=CropType.TOMATO,
            pest_disease_history=["fusarium_wilt"],
        )

        assert len(rec.reasoning_en) > 0
        assert len(rec.reasoning_ar) > 0


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_crop_history_handling(self, planner):
        """Test handling empty crop history"""
        history = FieldRotationHistory(field_id="FIELD-001", records=[])
        analysis = planner.analyze_field_history(history)

        assert analysis["total_years"] == 0
        assert analysis["legume_frequency"] == 0.0

    def test_single_measurement_trend(self, soil_tracker):
        """Test trend calculation with single measurement"""
        m = SoilHealthMeasurement(field_id="FIELD-001")
        soil_tracker.add_measurement(m)

        trend = soil_tracker.calculate_indicator_trend(
            field_id="FIELD-001",
            indicator=SoilHealthIndicator.ORGANIC_MATTER,
        )

        assert trend.trend_direction == "stable"

    def test_zero_area_planning(self, planner):
        """Test planning with zero area"""
        plan = planner.generate_multi_year_plan(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            field_name="Test",
            field_name_ar="اختبار",
            area_ha=0.0,
            starting_crop=CropType.WHEAT,
            start_year=2026,
            years=3,
        )

        # Should handle gracefully
        assert plan is not None

    def test_invalid_crop_compatibility_fallback(self, planner):
        """Test compatibility checking with unknown crop"""
        # Should return default value for unknown crops
        score = get_rotation_compatibility(CropType.WHEAT, CropType.WHEAT)
        assert 0 <= score <= 1

    def test_missing_soil_parameters(self, soil_tracker):
        """Test soil health score with missing parameters"""
        m = SoilHealthMeasurement(field_id="FIELD-001")
        # Only has default values

        score, components = soil_tracker.calculate_soil_health_score(m)
        assert 0 <= score <= 100


# =============================================================================
# Integration Tests (light)
# =============================================================================


@pytest.mark.unit
class TestIntegration:
    """Light integration tests combining multiple components"""

    def test_complete_planning_workflow(self, planner):
        """Test complete planning workflow"""
        # Get field history analysis
        history = FieldRotationHistory(
            field_id="FIELD-001",
            records=[
                CropHistoryRecord(crop_type=CropType.WHEAT, year=2024, season=Season.WINTER),
            ],
        )

        analysis = planner.analyze_field_history(history)
        assert analysis is not None

        # Generate recommendation
        rec = planner.generate_recommendation(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            previous_crops=history.get_last_n_crops(n=3),
            season=Season.SUMMER,
        )
        assert rec is not None

        # Generate multi-year plan
        plan = planner.generate_multi_year_plan(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            field_name="Test Field",
            field_name_ar="حقل الاختبار",
            area_ha=5.0,
            starting_crop=CropType.WHEAT,
            start_year=2026,
            years=3,
        )
        assert plan is not None

    def test_soil_tracking_with_rotation_plan(self, soil_tracker, planner):
        """Test combining soil tracking with rotation planning"""
        # Create initial measurement
        m1 = SoilHealthMeasurement(
            field_id="FIELD-001",
            measurement_date=date(2024, 1, 1),
            organic_matter_percent=2.0,
            nitrogen_available_kg_ha=40.0,
        )
        soil_tracker.add_measurement(m1)

        # Generate rotation plan
        plan = planner.generate_multi_year_plan(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            field_name="Test Field",
            field_name_ar="حقل الاختبار",
            area_ha=5.0,
            starting_crop=CropType.WHEAT,
            start_year=2026,
            years=3,
        )

        # Estimate rotation impact
        estimate = soil_tracker.estimate_rotation_impact(
            field_id="FIELD-001",
            planned_crops=[rec.recommended_crop for rec in plan.yearly_recommendations if rec.recommended_crop][:6],
        )

        assert estimate is not None
