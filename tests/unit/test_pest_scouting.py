"""
Unit Tests for Pest Scouting Module - اختبارات وحدة مسح الآفات
==============================================================

Comprehensive unit tests for the SAHOOL pest scouting and monitoring module.
Tests cover:
- Pest identification models and database
- Threshold calculations and economic analysis
- IPM treatment recommendations
- Scout report management
- Bilingual support (English/Arabic)

Test markers:
@pytest.mark.unit - Fast unit tests, no I/O

Author: Test Suite
Version: 1.0.0
Updated: January 2026
"""

from datetime import date, datetime, timedelta
from typing import Any

import pytest

from shared.pest_scouting.identification import (
    PEST_DATABASE,
    assess_infestation_level,
    get_high_priority_pests,
    get_pest_by_id,
    get_pest_by_scientific_name,
    get_pest_risk_factors,
    get_pests_by_category,
    get_pests_by_crop,
    get_quarantine_pests,
    get_seasonal_pests,
    get_similar_pests,
    identify_by_description,
    identify_by_symptoms,
    search_pests_by_name,
)

# Import all models and functions
from shared.pest_scouting.models import (
    AlertPriority,
    CropType,
    EconomicThreshold,
    InfestationLevel,
    OutbreakRecord,
    PestAlert,
    PestCategory,
    PestIdentification,
    PestLifeStage,
    ScoutingMethod,
    ScoutObservation,
    ScoutReport,
    TreatmentRecommendation,
    TreatmentType,
    TreatmentUrgency,
)
from shared.pest_scouting.recommendations import (
    TREATMENT_PROTOCOLS,
    BiologicalOption,
    ChemicalOption,
    CulturalPractice,
    generate_recommendation_from_alert,
    generate_recommendations_from_report,
    generate_treatment_recommendation,
    get_ipm_calendar,
    get_rotation_recommendation,
    get_treatment_protocol,
)
from shared.pest_scouting.thresholds import (
    THRESHOLD_DATABASE,
    ThresholdAssessment,
    assess_scout_report,
    assess_threshold,
    calculate_economic_injury_level,
    calculate_gain_threshold,
    calculate_treatment_roi,
    estimate_yield_loss,
    generate_threshold_alert,
    get_threshold,
    get_thresholds_for_crop,
    get_thresholds_for_pest,
)

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_pest_observation():
    """Create a sample pest observation."""
    return ScoutObservation(
        pest_id="APHID001",
        pest_name="Cotton Aphid",
        pest_name_ar="من القطن",
        life_stage=PestLifeStage.ADULT,
        count_per_unit=15.0,
        unit_type="per_plant",
        damage_observed=True,
        damage_rating=5,
        temperature_c=28.0,
        humidity_pct=65.0,
    )


@pytest.fixture
def sample_scout_report():
    """Create a sample scout report."""
    return ScoutReport(
        tenant_id="tenant001",
        farm_id="farm001",
        field_id="field001",
        crop_type=CropType.TOMATO,
        crop_variety="Roma VF",
        growth_stage="vegetative",
        growth_stage_ar="خضري",
        planting_date=date.today() - timedelta(days=30),
        scout_date=date.today(),
        scout_time="09:00",
        scout_id="scout001",
        scout_name="Ahmed",
        scouting_method=ScoutingMethod.VISUAL_INSPECTION,
        field_area_ha=5.0,
        sample_points=10,
        plants_examined=50,
        temperature_c=28.0,
        humidity_pct=65.0,
        overall_infestation=InfestationLevel.MODERATE,
    )


@pytest.fixture
def sample_threshold_assessment():
    """Create a sample threshold assessment."""
    return ThresholdAssessment(
        pest_id="APHID001",
        pest_name="Cotton Aphid",
        pest_name_ar="من القطن",
        crop_type=CropType.TOMATO,
        observed_value=15.0,
        unit="percentage_plants",
        action_threshold=10.0,
        economic_threshold=20.0,
        adjusted_action_threshold=10.0,
        adjusted_economic_threshold=20.0,
        exceeds_action_threshold=True,
        exceeds_economic_threshold=False,
        percentage_of_action_threshold=150.0,
        percentage_of_economic_threshold=75.0,
        infestation_level=InfestationLevel.HIGH,
        alert_priority=AlertPriority.MEDIUM,
        estimated_loss_if_no_action=6000.0,
        treatment_cost=400.0,
        benefit_cost_ratio=15.0,
    )


# =============================================================================
# TESTS: Pest Identification Models
# =============================================================================


@pytest.mark.unit
def test_pest_identification_creation():
    """Test PestIdentification model creation."""
    pest = PestIdentification(
        id="TEST001",
        scientific_name="Test species",
        common_name="Test Pest",
        common_name_ar="آفة الاختبار",
        category=PestCategory.INSECT,
        family="Testidae",
    )

    assert pest.id == "TEST001"
    assert pest.common_name == "Test Pest"
    assert pest.common_name_ar == "آفة الاختبار"
    assert pest.category == PestCategory.INSECT


@pytest.mark.unit
def test_pest_identification_to_dict():
    """Test PestIdentification conversion to dictionary."""
    pest = PestIdentification(
        id="TEST001",
        scientific_name="Test species",
        common_name="Test Pest",
        common_name_ar="آفة الاختبار",
        category=PestCategory.INSECT,
        primary_hosts=[CropType.TOMATO],
    )

    pest_dict = pest.to_dict()
    assert pest_dict["id"] == "TEST001"
    assert pest_dict["common_name"] == "Test Pest"
    assert pest_dict["category"] == "insect"
    assert pest_dict["primary_hosts"] == ["tomato"]


@pytest.mark.unit
def test_scout_observation_creation(sample_pest_observation):
    """Test ScoutObservation creation."""
    assert sample_pest_observation.pest_id == "APHID001"
    assert sample_pest_observation.life_stage == PestLifeStage.ADULT
    assert sample_pest_observation.count_per_unit == 15.0
    assert sample_pest_observation.damage_rating == 5


@pytest.mark.unit
def test_scout_observation_to_dict(sample_pest_observation):
    """Test ScoutObservation conversion to dictionary."""
    obs_dict = sample_pest_observation.to_dict()

    assert obs_dict["pest_id"] == "APHID001"
    assert obs_dict["life_stage"] == "adult"
    assert obs_dict["count_per_unit"] == 15.0
    assert obs_dict["damage_rating"] == 5


@pytest.mark.unit
def test_scout_report_creation(sample_scout_report):
    """Test ScoutReport creation."""
    assert sample_scout_report.field_id == "field001"
    assert sample_scout_report.crop_type == CropType.TOMATO
    assert sample_scout_report.overall_infestation == InfestationLevel.MODERATE


@pytest.mark.unit
def test_scout_report_pest_summary(sample_scout_report, sample_pest_observation):
    """Test scout report pest summary."""
    sample_scout_report.observations = [sample_pest_observation]

    summary = sample_scout_report.get_pest_summary()
    assert summary["total_observations"] == 1
    assert summary["unique_pests"] == 1
    assert "APHID001" in summary["pest_counts"]


@pytest.mark.unit
def test_pest_alert_creation():
    """Test PestAlert model creation."""
    alert = PestAlert(
        alert_type="threshold_exceeded",
        priority=AlertPriority.HIGH,
        tenant_id="tenant001",
        farm_id="farm001",
        field_id="field001",
        pest_id="APHID001",
        pest_name="Cotton Aphid",
        pest_name_ar="من القطن",
        title="Aphid Detection",
        title_ar="اكتشاف المن",
    )

    assert alert.priority == AlertPriority.HIGH
    assert alert.pest_name == "Cotton Aphid"
    assert alert.is_active is True


@pytest.mark.unit
def test_pest_alert_priority_icon():
    """Test pest alert priority icon display."""
    alert_critical = PestAlert(priority=AlertPriority.CRITICAL)
    alert_high = PestAlert(priority=AlertPriority.HIGH)
    alert_medium = PestAlert(priority=AlertPriority.MEDIUM)

    assert alert_critical.get_priority_icon() == "[!!!]"
    assert alert_high.get_priority_icon() == "[!!]"
    assert alert_medium.get_priority_icon() == "[!]"


@pytest.mark.unit
def test_treatment_recommendation_creation():
    """Test TreatmentRecommendation model creation."""
    rec = TreatmentRecommendation(
        pest_id="APHID001",
        pest_name="Cotton Aphid",
        pest_name_ar="من القطن",
        field_id="field001",
        crop_type=CropType.TOMATO,
        treatment_type=TreatmentType.CHEMICAL,
        urgency=TreatmentUrgency.URGENT,
    )

    assert rec.pest_id == "APHID001"
    assert rec.treatment_type == TreatmentType.CHEMICAL
    assert rec.urgency == TreatmentUrgency.URGENT


# =============================================================================
# TESTS: Pest Database and Lookup Functions
# =============================================================================


@pytest.mark.unit
def test_pest_database_exists():
    """Test pest database is populated."""
    assert len(PEST_DATABASE) > 0
    assert "RPW001" in PEST_DATABASE
    assert "DUBAS001" in PEST_DATABASE
    assert "APHID001" in PEST_DATABASE


@pytest.mark.unit
def test_get_pest_by_id():
    """Test getting pest by ID."""
    pest = get_pest_by_id("RPW001")

    assert pest is not None
    assert pest.id == "RPW001"
    assert pest.common_name == "Red Palm Weevil"
    assert pest.common_name_ar == "سوسة النخيل الحمراء"


@pytest.mark.unit
def test_get_pest_by_id_not_found():
    """Test getting non-existent pest."""
    pest = get_pest_by_id("NONEXISTENT")
    assert pest is None


@pytest.mark.unit
def test_get_pest_by_scientific_name():
    """Test getting pest by scientific name."""
    pest = get_pest_by_scientific_name("Rhynchophorus ferrugineus")

    assert pest is not None
    assert pest.id == "RPW001"


@pytest.mark.unit
def test_get_pest_by_scientific_name_case_insensitive():
    """Test scientific name lookup is case-insensitive."""
    pest = get_pest_by_scientific_name("rhynchophorus ferrugineus")

    assert pest is not None
    assert pest.id == "RPW001"


@pytest.mark.unit
def test_search_pests_by_name():
    """Test searching pests by common name."""
    results = search_pests_by_name("Aphid")

    assert len(results) > 0
    assert any(p.id == "APHID001" for p in results)


@pytest.mark.unit
def test_search_pests_by_arabic_name():
    """Test searching pests by Arabic name."""
    results = search_pests_by_name("المن")

    assert len(results) > 0


@pytest.mark.unit
def test_get_pests_by_crop():
    """Test getting pests that affect a specific crop."""
    pests = get_pests_by_crop(CropType.TOMATO)

    assert len(pests) > 0
    # Check for known tomato pests
    pest_ids = [p.id for p in pests]
    assert "APHID001" in pest_ids
    assert "WHITEFLY001" in pest_ids


@pytest.mark.unit
def test_get_pests_by_category():
    """Test getting pests by category."""
    insects = get_pests_by_category(PestCategory.INSECT)
    mites = get_pests_by_category(PestCategory.MITE)

    assert len(insects) > len(mites)
    assert all(p.category == PestCategory.INSECT for p in insects)
    assert all(p.category == PestCategory.MITE for p in mites)


@pytest.mark.unit
def test_get_quarantine_pests():
    """Test getting quarantine pests."""
    quarantine = get_quarantine_pests()

    assert len(quarantine) > 0
    assert all(p.is_quarantine_pest for p in quarantine)
    # Check for known quarantine pests
    pest_ids = [p.id for p in quarantine]
    assert "RPW001" in pest_ids
    assert "TUTA001" in pest_ids


@pytest.mark.unit
def test_get_high_priority_pests():
    """Test getting high priority pests."""
    priority = get_high_priority_pests()

    assert len(priority) > 0
    for p in priority:
        assert p.economic_importance in ("very_high", "high")


@pytest.mark.unit
def test_identify_by_symptoms():
    """Test pest identification by symptoms."""
    symptoms = [
        "Leaf curling",
        "Stunted growth",
        "Honeydew",
    ]

    results = identify_by_symptoms(symptoms)
    assert len(results) > 0
    # Results should be sorted by match score
    assert results[0][1] >= results[-1][1]


@pytest.mark.unit
def test_identify_by_symptoms_with_crop_filter():
    """Test symptom identification with crop filter."""
    symptoms = ["Crown collapse", "Brown oozing"]

    # Without filter - should find RPW
    results = identify_by_symptoms(symptoms)
    assert len(results) > 0

    # With wrong crop filter - should find nothing
    results = identify_by_symptoms(symptoms, crop_type=CropType.TOMATO, min_match_score=0.5)
    # RPW doesn't affect tomato, so should be few/no results
    assert len(results) == 0


@pytest.mark.unit
def test_identify_by_description():
    """Test pest identification by physical description."""
    results = identify_by_description(
        description="Large reddish-brown weevil with curved snout",
        size_mm=(35, 40),
        color="reddish-brown",
    )

    assert len(results) > 0
    # RPW should be high ranked
    top_result_ids = [p.id for p, _ in results[:3]]
    assert "RPW001" in top_result_ids


@pytest.mark.unit
def test_assess_infestation_level():
    """Test infestation level assessment."""
    obs = ScoutObservation(
        count_per_unit=5.0,
        damage_rating=4,
    )

    level = assess_infestation_level(obs, "APHID001")
    assert level in [
        InfestationLevel.NONE,
        InfestationLevel.TRACE,
        InfestationLevel.LOW,
        InfestationLevel.MODERATE,
        InfestationLevel.HIGH,
        InfestationLevel.SEVERE,
        InfestationLevel.CRITICAL,
    ]


@pytest.mark.unit
def test_get_similar_pests():
    """Test getting similar pests for confusion avoidance."""
    similar = get_similar_pests("APHID001")

    # Should find similar insects that attack same crops
    for pest in similar:
        # All should be in same category
        assert pest.category == PestCategory.INSECT


@pytest.mark.unit
def test_get_seasonal_pests():
    """Test getting seasonal pests."""
    # January is typically winter in Middle East
    pests_jan = get_seasonal_pests(1)
    pests_july = get_seasonal_pests(7)

    assert len(pests_jan) > 0
    assert len(pests_july) > 0
    # Different months should have different pest profiles
    jan_ids = {p.id for p in pests_jan}
    july_ids = {p.id for p in pests_july}
    assert jan_ids != july_ids


@pytest.mark.unit
def test_get_pest_risk_factors():
    """Test pest risk factor assessment."""
    result = get_pest_risk_factors(
        "MITE001",
        temperature_c=32.0,
        humidity_pct=40.0,
    )

    assert result["pest_id"] == "MITE001"
    assert "temperature_risk" in result
    assert "humidity_risk" in result
    assert "overall_risk" in result


@pytest.mark.unit
def test_get_pest_risk_factors_optimal():
    """Test pest risk when conditions are optimal."""
    result = get_pest_risk_factors(
        "MITE001",
        temperature_c=30.0,  # Optimal for MITE001
        humidity_pct=40.0,  # Optimal for MITE001
    )

    assert result["temperature_risk"] == "high"
    assert result["humidity_risk"] == "high"
    assert result["overall_risk"] == "high"


# =============================================================================
# TESTS: Threshold Calculations
# =============================================================================


@pytest.mark.unit
def test_threshold_database_exists():
    """Test threshold database is populated."""
    assert len(THRESHOLD_DATABASE) > 0
    assert "THR_RPW001_PALM" in THRESHOLD_DATABASE
    assert "THR_APHID001_TOMATO" in THRESHOLD_DATABASE


@pytest.mark.unit
def test_get_threshold():
    """Test getting threshold for pest-crop combination."""
    threshold = get_threshold("APHID001", CropType.TOMATO)

    assert threshold is not None
    assert threshold.pest_id == "APHID001"
    assert threshold.crop_type == CropType.TOMATO
    assert threshold.action_threshold == 10.0


@pytest.mark.unit
def test_get_threshold_not_found():
    """Test getting non-existent threshold."""
    threshold = get_threshold("NONEXISTENT", CropType.TOMATO)
    assert threshold is None


@pytest.mark.unit
def test_get_thresholds_for_crop():
    """Test getting all thresholds for a crop."""
    thresholds = get_thresholds_for_crop(CropType.TOMATO)

    assert len(thresholds) > 0
    assert all(t.crop_type == CropType.TOMATO for t in thresholds)


@pytest.mark.unit
def test_get_thresholds_for_pest():
    """Test getting all thresholds for a pest."""
    thresholds = get_thresholds_for_pest("APHID001")

    assert len(thresholds) > 0
    assert all(t.pest_id == "APHID001" for t in thresholds)


@pytest.mark.unit
def test_assess_threshold():
    """Test threshold assessment."""
    assessment = assess_threshold(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        observed_value=15.0,  # Above action threshold of 10
        growth_stage="vegetative",
        temperature_c=28.0,
        area_ha=5.0,
    )

    assert assessment is not None
    assert assessment.pest_id == "APHID001"
    assert assessment.exceeds_action_threshold is True
    assert assessment.action_required is True


@pytest.mark.unit
def test_assess_threshold_below_threshold():
    """Test threshold assessment when below threshold."""
    assessment = assess_threshold(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        observed_value=5.0,  # Below action threshold of 10
        area_ha=5.0,
    )

    assert assessment is not None
    assert assessment.exceeds_action_threshold is False
    assert assessment.action_required is False


@pytest.mark.unit
def test_assess_threshold_with_temperature_modifier():
    """Test threshold assessment with temperature modifier."""
    # Hot weather should reduce threshold for spider mites
    assessment_hot = assess_threshold(
        pest_id="MITE001",
        crop_type=CropType.CUCUMBER,
        observed_value=2.0,
        temperature_c=38.0,  # Very hot
        area_ha=1.0,
    )

    assessment_cool = assess_threshold(
        pest_id="MITE001",
        crop_type=CropType.CUCUMBER,
        observed_value=2.0,
        temperature_c=18.0,  # Cool
        area_ha=1.0,
    )

    # Same observed value but different temperatures
    # Hot weather should trigger alert more easily
    if assessment_hot and assessment_cool:
        assert assessment_hot.adjusted_action_threshold <= assessment_cool.adjusted_action_threshold


@pytest.mark.unit
def test_assess_scout_report(sample_scout_report, sample_pest_observation):
    """Test assessing a complete scout report."""
    sample_scout_report.observations = [sample_pest_observation]

    assessments = assess_scout_report(sample_scout_report)

    assert len(assessments) > 0
    assert assessments[0].pest_id == "APHID001"


@pytest.mark.unit
def test_generate_threshold_alert(sample_threshold_assessment):
    """Test generating alert from threshold assessment."""
    alert = generate_threshold_alert(
        sample_threshold_assessment,
        field_id="field001",
        farm_id="farm001",
        tenant_id="tenant001",
    )

    assert alert is not None
    assert alert.pest_id == "APHID001"
    assert alert.field_id == "field001"
    assert alert.priority == AlertPriority.MEDIUM


@pytest.mark.unit
def test_calculate_economic_injury_level():
    """Test EIL calculation."""
    eil = calculate_economic_injury_level(
        control_cost_per_ha=500.0,
        crop_value_per_ha=50000.0,
        damage_per_pest_unit=100.0,
        control_efficacy=0.85,
    )

    assert eil > 0
    assert isinstance(eil, float)


@pytest.mark.unit
def test_calculate_gain_threshold():
    """Test action threshold calculation."""
    eil = 50.0
    threshold = calculate_gain_threshold(eil, pest_growth_rate=1.5, days_to_treatment=3)

    assert threshold < eil  # Should be lower than EIL
    assert threshold > 0


@pytest.mark.unit
def test_estimate_yield_loss():
    """Test yield loss estimation."""
    threshold = EconomicThreshold(
        crop_type=CropType.TOMATO,
        expected_loss_per_pest_unit=100.0,
        currency="SAR",
    )

    loss = estimate_yield_loss(10.0, threshold, 5.0)

    assert loss["expected"] == 5000.0  # 10 * 100 * 5
    assert loss["low"] < loss["expected"]
    assert loss["high"] > loss["expected"]
    assert loss["currency"] == "SAR"


@pytest.mark.unit
def test_calculate_treatment_roi(sample_threshold_assessment):
    """Test ROI calculation for treatment."""
    roi_result = calculate_treatment_roi(sample_threshold_assessment)

    assert "roi_percentage" in roi_result
    assert "benefit_cost_ratio" in roi_result
    assert roi_result["gross_benefit"] > 0
    assert roi_result["treatment_cost"] > 0


# =============================================================================
# TESTS: IPM Recommendations
# =============================================================================


@pytest.mark.unit
def test_treatment_protocols_exist():
    """Test treatment protocols are populated."""
    assert len(TREATMENT_PROTOCOLS) > 0
    assert "RPW001" in TREATMENT_PROTOCOLS
    assert "APHID001" in TREATMENT_PROTOCOLS


@pytest.mark.unit
def test_get_treatment_protocol():
    """Test getting treatment protocol."""
    protocol = get_treatment_protocol("RPW001")

    assert protocol is not None
    assert protocol["pest_name"] == "Red Palm Weevil"
    assert protocol["pest_name_ar"] == "سوسة النخيل الحمراء"
    assert "chemical_options" in protocol
    assert "biological_options" in protocol
    assert "cultural_practices" in protocol


@pytest.mark.unit
def test_get_treatment_protocol_not_found():
    """Test getting non-existent protocol."""
    protocol = get_treatment_protocol("NONEXISTENT")
    assert protocol is None


@pytest.mark.unit
def test_chemical_option_structure():
    """Test ChemicalOption data structure."""
    chemical = ChemicalOption(
        product_name="Test Product",
        product_name_ar="منتج اختبار",
        active_ingredient="test ingredient",
        active_ingredient_ar="مادة فعالة",
        formulation="SC",
        rate_per_ha="1 L",
        rate_unit="L/ha",
        phi_days=7,
        rei_hours=24,
        target_stages=[PestLifeStage.ADULT, PestLifeStage.LARVA],
        mode_of_action="test mode",
        mode_of_action_ar="آلية عمل",
        efficacy="good",
        resistance_risk="low",
    )

    assert chemical.product_name == "Test Product"
    assert chemical.phi_days == 7
    assert PestLifeStage.ADULT in chemical.target_stages


@pytest.mark.unit
def test_generate_treatment_recommendation():
    """Test generating treatment recommendation."""
    rec = generate_treatment_recommendation(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        growth_stage="vegetative",
        infestation_level=InfestationLevel.HIGH,
        area_ha=5.0,
        field_id="field001",
    )

    assert rec is not None
    assert rec.pest_id == "APHID001"
    assert rec.field_id == "field001"
    assert rec.treatment_type == TreatmentType.INTEGRATED


@pytest.mark.unit
def test_generate_treatment_recommendation_biological_only():
    """Test generating biological-only recommendation."""
    rec = generate_treatment_recommendation(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        growth_stage="vegetative",
        infestation_level=InfestationLevel.MODERATE,
        organic_only=True,
        area_ha=5.0,
    )

    assert rec is not None
    assert rec.treatment_type == TreatmentType.BIOLOGICAL
    assert len(rec.chemical_options) == 0


@pytest.mark.unit
def test_generate_treatment_recommendation_urgency():
    """Test recommendation urgency levels."""
    rec_critical = generate_treatment_recommendation(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        growth_stage="vegetative",
        infestation_level=InfestationLevel.CRITICAL,
    )

    rec_low = generate_treatment_recommendation(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        growth_stage="vegetative",
        infestation_level=InfestationLevel.LOW,
    )

    assert rec_critical.urgency == TreatmentUrgency.IMMEDIATE
    assert rec_low.urgency in [TreatmentUrgency.MONITOR, TreatmentUrgency.PREVENTIVE]


@pytest.mark.unit
def test_generate_recommendation_from_alert(sample_threshold_assessment):
    """Test generating recommendation from alert."""
    alert = generate_threshold_alert(
        sample_threshold_assessment,
        field_id="field001",
        farm_id="farm001",
    )

    rec = generate_recommendation_from_alert(alert)

    assert rec is not None
    assert rec.pest_id == alert.pest_id
    assert rec.alert_id == alert.id


@pytest.mark.unit
def test_generate_recommendations_from_report():
    """Test generating recommendations from scout report."""
    report = ScoutReport(
        field_id="field001",
        crop_type=CropType.TOMATO,
        growth_stage="vegetative",
        field_area_ha=5.0,
    )

    assessment = ThresholdAssessment(
        pest_id="APHID001",
        pest_name="Cotton Aphid",
        pest_name_ar="من القطن",
        crop_type=CropType.TOMATO,
        observed_value=15.0,
        unit="percentage_plants",
        action_threshold=10.0,
        economic_threshold=20.0,
        adjusted_action_threshold=10.0,
        adjusted_economic_threshold=20.0,
        exceeds_action_threshold=True,
        exceeds_economic_threshold=False,
        percentage_of_action_threshold=150.0,
        percentage_of_economic_threshold=75.0,
        infestation_level=InfestationLevel.HIGH,
        alert_priority=AlertPriority.MEDIUM,
        estimated_loss_if_no_action=6000.0,
        treatment_cost=400.0,
        benefit_cost_ratio=15.0,
        action_required=True,
    )

    recommendations = generate_recommendations_from_report(report, [assessment])

    assert len(recommendations) > 0
    assert recommendations[0].scout_report_id == report.id


@pytest.mark.unit
def test_get_rotation_recommendation():
    """Test getting rotation recommendation for resistance management."""
    recent_treatments = ["flonicamid"]

    rotation = get_rotation_recommendation("APHID001", recent_treatments)

    assert "recommended_mode_of_action" in rotation or "warning" in rotation


@pytest.mark.unit
def test_get_ipm_calendar():
    """Test getting IPM activity calendar."""
    calendar = get_ipm_calendar("APHID001", CropType.TOMATO)

    assert len(calendar) > 0
    for activity in calendar:
        assert "activity" in activity
        assert "activity_ar" in activity
        assert "timing" in activity


# =============================================================================
# TESTS: Data Model Validation
# =============================================================================


@pytest.mark.unit
def test_enum_values():
    """Test enum value definitions."""
    assert PestCategory.INSECT.value == "insect"
    assert PestLifeStage.ADULT.value == "adult"
    assert InfestationLevel.MODERATE.value == "moderate"
    assert AlertPriority.CRITICAL.value == "critical"


@pytest.mark.unit
def test_crop_types():
    """Test all crop types are defined."""
    expected_crops = [
        CropType.TOMATO,
        CropType.CUCUMBER,
        CropType.DATE_PALM,
        CropType.WHEAT,
        CropType.BARLEY,
    ]

    for crop in expected_crops:
        assert isinstance(crop, CropType)


@pytest.mark.unit
def test_treatment_urgency_ordering():
    """Test treatment urgency levels."""
    urgencies = [
        TreatmentUrgency.IMMEDIATE,
        TreatmentUrgency.URGENT,
        TreatmentUrgency.SOON,
        TreatmentUrgency.SCHEDULED,
        TreatmentUrgency.PREVENTIVE,
        TreatmentUrgency.MONITOR,
    ]

    assert len(urgencies) == 6
    assert all(isinstance(u, TreatmentUrgency) for u in urgencies)


# =============================================================================
# TESTS: Bilingual Support
# =============================================================================


@pytest.mark.unit
def test_pest_arabic_names():
    """Test Arabic name support in pest database."""
    pest = get_pest_by_id("RPW001")

    assert pest.common_name_ar == "سوسة النخيل الحمراء"
    assert len(pest.damage_symptoms_ar) > 0
    assert len(pest.adult_description_ar) > 0


@pytest.mark.unit
def test_search_arabic_pest_names():
    """Test searching for pests by Arabic names."""
    # Search by Arabic name
    results = search_pests_by_name("سوسة")

    assert len(results) > 0
    assert any(p.id == "RPW001" for p in results)


@pytest.mark.unit
def test_alert_bilingual_output():
    """Test alert bilingual support."""
    alert = generate_threshold_alert(
        ThresholdAssessment(
            pest_id="APHID001",
            pest_name="Cotton Aphid",
            pest_name_ar="من القطن",
            crop_type=CropType.TOMATO,
            observed_value=15.0,
            unit="percentage_plants",
            action_threshold=10.0,
            economic_threshold=20.0,
            adjusted_action_threshold=10.0,
            adjusted_economic_threshold=20.0,
            exceeds_action_threshold=True,
            exceeds_economic_threshold=False,
            percentage_of_action_threshold=150.0,
            percentage_of_economic_threshold=75.0,
            infestation_level=InfestationLevel.HIGH,
            alert_priority=AlertPriority.MEDIUM,
            estimated_loss_if_no_action=6000.0,
            treatment_cost=400.0,
            benefit_cost_ratio=15.0,
        ),
        field_id="field001",
    )

    assert alert.title != ""
    assert alert.title_ar != ""
    assert alert.description != ""
    assert alert.description_ar != ""


# =============================================================================
# TESTS: Edge Cases and Boundary Conditions
# =============================================================================


@pytest.mark.unit
def test_zero_threshold_rph():
    """Test RPW zero-tolerance threshold."""
    threshold = get_threshold("RPW001", CropType.DATE_PALM)

    assert threshold is not None
    assert threshold.action_threshold == 0.0  # Zero tolerance


@pytest.mark.unit
def test_assess_no_observations():
    """Test assessment with empty observations."""
    report = ScoutReport(
        field_id="field001",
        crop_type=CropType.TOMATO,
        observations=[],
    )

    assessments = assess_scout_report(report)
    assert assessments == []


@pytest.mark.unit
def test_negative_infestation_level():
    """Test negative observed values are handled."""
    assessment = assess_threshold(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        observed_value=-5.0,  # Invalid, but should be handled
        area_ha=1.0,
    )

    # Should return something (not crash)
    assert assessment is not None


@pytest.mark.unit
def test_very_high_infestation():
    """Test very high infestation levels."""
    assessment = assess_threshold(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        observed_value=100.0,  # Well above threshold
        area_ha=5.0,
    )

    assert assessment.infestation_level == InfestationLevel.CRITICAL
    assert assessment.alert_priority == AlertPriority.CRITICAL


@pytest.mark.unit
def test_large_field_area():
    """Test economic calculations for large areas."""
    assessment = assess_threshold(
        pest_id="APHID001",
        crop_type=CropType.TOMATO,
        observed_value=15.0,
        area_ha=1000.0,  # Large field
    )

    assert assessment is not None
    assert assessment.estimated_loss_if_no_action > 0


# =============================================================================
# TESTS: Performance and Data Integrity
# =============================================================================


@pytest.mark.unit
def test_pest_database_unique_ids():
    """Test all pests have unique IDs."""
    ids = [p.id for p in PEST_DATABASE.values()]
    assert len(ids) == len(set(ids))  # All unique


@pytest.mark.unit
def test_threshold_database_unique_ids():
    """Test all thresholds have unique IDs."""
    ids = [t.id for t in THRESHOLD_DATABASE.values()]
    assert len(ids) == len(set(ids))  # All unique


@pytest.mark.unit
def test_protocol_completeness():
    """Test treatment protocols have required fields."""
    for pest_id, protocol in TREATMENT_PROTOCOLS.items():
        assert "pest_name" in protocol
        assert "pest_name_ar" in protocol
        assert "urgency" in protocol
        assert "primary_strategy" in protocol
        assert "chemical_options" in protocol or "biological_options" in protocol


@pytest.mark.unit
def test_pest_database_completeness():
    """Test pests have required fields."""
    for pest_id, pest in PEST_DATABASE.items():
        assert pest.id == pest_id
        assert pest.scientific_name != ""
        assert pest.common_name != ""
        assert pest.common_name_ar != ""


# =============================================================================
# TESTS: Integration Scenarios
# =============================================================================


@pytest.mark.unit
def test_complete_scouting_workflow():
    """Test complete workflow: scout -> assess -> recommend."""
    # 1. Scout report
    report = ScoutReport(
        field_id="field001",
        crop_type=CropType.TOMATO,
        growth_stage="vegetative",
        field_area_ha=5.0,
    )

    obs = ScoutObservation(
        pest_id="APHID001",
        pest_name="Cotton Aphid",
        count_per_unit=15.0,
        unit_type="percentage_plants",
    )
    report.observations = [obs]

    # 2. Assess
    assessments = assess_scout_report(report)
    assert len(assessments) > 0

    # 3. Generate alert
    alert = generate_threshold_alert(
        assessments[0],
        field_id="field001",
    )
    assert alert is not None

    # 4. Generate recommendation
    rec = generate_recommendation_from_alert(alert)
    assert rec is not None
    assert rec.pest_id == "APHID001"


@pytest.mark.unit
def test_multi_pest_report():
    """Test scout report with multiple pests."""
    report = ScoutReport(
        field_id="field001",
        crop_type=CropType.TOMATO,
        growth_stage="vegetative",
        field_area_ha=5.0,
    )

    # Add multiple pest observations
    obs1 = ScoutObservation(pest_id="APHID001", count_per_unit=10.0)
    obs2 = ScoutObservation(pest_id="WHITEFLY001", count_per_unit=5.0)
    report.observations = [obs1, obs2]

    summary = report.get_pest_summary()
    assert summary["unique_pests"] == 2
    assert summary["total_observations"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
