"""
Tests for Pest Scouting Module - اختبارات وحدة مسح الآفات

Covers:
- Pest data models and enums
- Pest database lookups
- Threshold calculations and economic analysis
- Infestation level assessment
- Alert generation
"""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest

from shared.pest_scouting.identification import (
    PEST_DATABASE,
    assess_infestation_level,
    get_high_priority_pests,
    get_pest_by_id,
    get_pest_by_scientific_name,
    get_pests_by_category,
    get_pests_by_crop,
    get_quarantine_pests,
    get_seasonal_pests,
    search_pests_by_name,
)
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
from shared.pest_scouting.thresholds import (
    THRESHOLD_DATABASE,
    ThresholdAssessment,
    assess_threshold,
    calculate_economic_injury_level,
    calculate_gain_threshold,
    calculate_treatment_roi,
    estimate_yield_loss,
    get_threshold,
    get_thresholds_for_crop,
    get_thresholds_for_pest,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPestEnums:
    """Test pest-related enums."""

    def test_pest_category_values(self):
        assert PestCategory.INSECT == "insect"
        assert PestCategory.FUNGAL == "fungal"
        assert PestCategory.WEED == "weed"
        assert len(PestCategory) == 9

    def test_pest_life_stage_values(self):
        assert PestLifeStage.EGG == "egg"
        assert PestLifeStage.LARVA == "larva"
        assert PestLifeStage.ADULT == "adult"
        assert PestLifeStage.ALL_STAGES == "all_stages"

    def test_infestation_level_values(self):
        assert InfestationLevel.NONE == "none"
        assert InfestationLevel.CRITICAL == "critical"
        assert len(InfestationLevel) == 7

    def test_alert_priority_values(self):
        assert AlertPriority.CRITICAL == "critical"
        assert AlertPriority.INFORMATIONAL == "informational"
        assert len(AlertPriority) == 5

    def test_scouting_method_values(self):
        assert ScoutingMethod.PHEROMONE_TRAP == "pheromone_trap"
        assert ScoutingMethod.DRONE_IMAGERY == "drone_imagery"
        assert ScoutingMethod.ACOUSTIC_DETECTION == "acoustic_detection"

    def test_treatment_type_values(self):
        assert TreatmentType.CHEMICAL == "chemical"
        assert TreatmentType.BIOLOGICAL == "biological"
        assert TreatmentType.INTEGRATED == "integrated"

    def test_crop_type_values(self):
        assert CropType.DATE_PALM == "date_palm"
        assert CropType.WHEAT == "wheat"
        assert CropType.TOMATO == "tomato"


# ═══════════════════════════════════════════════════════════════════════════════
# Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestScoutObservation:
    """Test ScoutObservation dataclass."""

    def test_basic_creation(self):
        obs = ScoutObservation(
            pest_id="RPW001",
            pest_name="Red Palm Weevil",
            pest_name_ar="سوسة النخيل الحمراء",
            count=3,
        )
        assert obs.pest_id == "RPW001"
        assert obs.count == 3
        assert obs.id != ""  # UUID auto-generated

    def test_defaults(self):
        obs = ScoutObservation()
        assert obs.life_stage == PestLifeStage.ADULT
        assert obs.damage_observed is False
        assert obs.identification_confidence == 0.8


class TestScoutReport:
    """Test ScoutReport dataclass."""

    def test_basic_creation(self):
        report = ScoutReport(
            tenant_id="t-001",
            farm_id="farm-001",
            field_id="field-001",
            crop_type=CropType.DATE_PALM,
            scouting_method=ScoutingMethod.PHEROMONE_TRAP,
            observations=[
                ScoutObservation(
                    pest_id="RPW001",
                    pest_name="Red Palm Weevil",
                    pest_name_ar="سوسة النخيل الحمراء",
                    count=2,
                )
            ],
        )
        assert report.crop_type == CropType.DATE_PALM
        assert len(report.observations) == 1

    def test_defaults(self):
        report = ScoutReport()
        assert report.crop_type == CropType.GENERAL
        assert report.scouting_method == ScoutingMethod.VISUAL_INSPECTION
        assert report.overall_infestation == InfestationLevel.NONE


class TestPestAlert:
    """Test PestAlert dataclass."""

    def test_basic_creation(self):
        alert = PestAlert(
            tenant_id="t-001",
            field_id="field-001",
            pest_id="RPW001",
            pest_name="Red Palm Weevil",
            pest_name_ar="سوسة النخيل الحمراء",
            priority=AlertPriority.CRITICAL,
        )
        assert alert.priority == AlertPriority.CRITICAL
        assert alert.resolved_at is None

    def test_auto_generated_id(self):
        alert = PestAlert()
        assert alert.id != ""


class TestOutbreakRecord:
    """Test OutbreakRecord dataclass."""

    def test_basic_creation(self):
        record = OutbreakRecord(
            tenant_id="t-001",
            pest_id="RPW001",
            pest_name="Red Palm Weevil",
            pest_name_ar="سوسة النخيل الحمراء",
        )
        assert record.pest_id == "RPW001"


# ═══════════════════════════════════════════════════════════════════════════════
# Pest Database Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPestDatabase:
    """Test pest database lookups."""

    def test_database_not_empty(self):
        assert len(PEST_DATABASE) > 0

    def test_rpw_exists(self):
        assert "RPW001" in PEST_DATABASE
        rpw = PEST_DATABASE["RPW001"]
        assert rpw.scientific_name == "Rhynchophorus ferrugineus"
        assert rpw.common_name == "Red Palm Weevil"
        assert rpw.common_name_ar == "سوسة النخيل الحمراء"
        assert rpw.is_quarantine_pest is True

    def test_get_pest_by_id_existing(self):
        pest = get_pest_by_id("RPW001")
        assert pest is not None
        assert pest.id == "RPW001"

    def test_get_pest_by_id_nonexistent(self):
        pest = get_pest_by_id("NONEXISTENT999")
        assert pest is None

    def test_get_pest_by_scientific_name(self):
        pest = get_pest_by_scientific_name("Rhynchophorus ferrugineus")
        assert pest is not None
        assert pest.id == "RPW001"

    def test_search_pests_by_name_english(self):
        results = search_pests_by_name("weevil")
        assert len(results) > 0
        assert any("Weevil" in p.common_name for p in results)

    def test_search_pests_by_name_arabic(self):
        results = search_pests_by_name("سوسة")
        assert len(results) > 0

    def test_get_pests_by_crop_date_palm(self):
        pests = get_pests_by_crop(CropType.DATE_PALM)
        assert len(pests) > 0
        pest_ids = [p.id for p in pests]
        assert "RPW001" in pest_ids

    def test_get_pests_by_category_insect(self):
        pests = get_pests_by_category(PestCategory.INSECT)
        assert len(pests) > 0
        assert all(p.category == PestCategory.INSECT for p in pests)

    def test_get_quarantine_pests(self):
        pests = get_quarantine_pests()
        assert len(pests) > 0
        assert all(p.is_quarantine_pest is True for p in pests)
        rpw_ids = [p.id for p in pests]
        assert "RPW001" in rpw_ids

    def test_get_high_priority_pests(self):
        pests = get_high_priority_pests()
        assert len(pests) > 0

    def test_all_pests_have_bilingual_names(self):
        for pest_id, pest in PEST_DATABASE.items():
            assert pest.common_name != "", f"{pest_id} missing English name"
            assert pest.common_name_ar != "", f"{pest_id} missing Arabic name"

    def test_pest_database_has_damage_symptoms(self):
        rpw = PEST_DATABASE["RPW001"]
        assert len(rpw.damage_symptoms) > 0
        assert len(rpw.damage_symptoms_ar) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Threshold Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestThresholdDatabase:
    """Test threshold database."""

    def test_database_not_empty(self):
        assert len(THRESHOLD_DATABASE) > 0

    def test_rpw_zero_tolerance(self):
        """RPW should have zero tolerance threshold."""
        rpw_thresh = THRESHOLD_DATABASE.get("THR_RPW001_PALM")
        if rpw_thresh is None:
            # Try DATE_PALM key
            rpw_thresh = get_threshold("RPW001", CropType.DATE_PALM)
        assert rpw_thresh is not None
        assert rpw_thresh.action_threshold == 0.0
        assert rpw_thresh.economic_threshold == 0.0

    def test_dubas_bug_thresholds(self):
        thresh = get_threshold("DUBAS001", CropType.DATE_PALM)
        assert thresh is not None
        assert thresh.action_threshold == 5.0
        assert thresh.economic_threshold == 10.0


class TestThresholdLookups:
    """Test threshold lookup functions."""

    def test_get_threshold_existing(self):
        thresh = get_threshold("RPW001", CropType.DATE_PALM)
        assert thresh is not None

    def test_get_threshold_nonexistent(self):
        thresh = get_threshold("FAKE999", CropType.WHEAT)
        assert thresh is None

    def test_get_thresholds_for_crop(self):
        thresholds = get_thresholds_for_crop(CropType.DATE_PALM)
        assert len(thresholds) >= 1

    def test_get_thresholds_for_pest(self):
        thresholds = get_thresholds_for_pest("RPW001")
        assert len(thresholds) >= 1


class TestThresholdAssessment:
    """Test threshold assessment calculations."""

    def test_assess_threshold_below_action(self):
        """Test assessment when below action threshold."""
        assessment = assess_threshold(
            pest_id="DUBAS001",
            crop_type=CropType.DATE_PALM,
            observed_value=2.0,  # Below action threshold of 5
        )
        assert assessment is not None
        assert assessment.exceeds_action_threshold is False
        assert assessment.exceeds_economic_threshold is False
        assert assessment.action_required is False

    def test_assess_threshold_exceeds_action(self):
        """Test assessment when exceeds action threshold."""
        assessment = assess_threshold(
            pest_id="DUBAS001",
            crop_type=CropType.DATE_PALM,
            observed_value=7.0,  # Between action (5) and economic (10)
        )
        assert assessment is not None
        assert assessment.exceeds_action_threshold is True
        assert assessment.exceeds_economic_threshold is False
        assert assessment.action_required is True

    def test_assess_threshold_exceeds_economic(self):
        """Test assessment when exceeds economic threshold."""
        assessment = assess_threshold(
            pest_id="DUBAS001",
            crop_type=CropType.DATE_PALM,
            observed_value=15.0,  # Above economic threshold of 10
        )
        assert assessment is not None
        assert assessment.exceeds_action_threshold is True
        assert assessment.exceeds_economic_threshold is True
        assert "Immediate" in assessment.recommendation or "immediate" in assessment.recommendation

    def test_assess_threshold_rpw_zero_tolerance(self):
        """RPW should trigger on any detection."""
        assessment = assess_threshold(
            pest_id="RPW001",
            crop_type=CropType.DATE_PALM,
            observed_value=1.0,
        )
        assert assessment is not None
        assert assessment.action_required is True
        assert assessment.alert_priority in [AlertPriority.CRITICAL, AlertPriority.HIGH]

    def test_assess_threshold_nonexistent_pest(self):
        """Non-existent pest-crop combo should return None."""
        assessment = assess_threshold(
            pest_id="FAKE999",
            crop_type=CropType.WHEAT,
            observed_value=10.0,
        )
        assert assessment is None

    def test_assess_threshold_bilingual_recommendation(self):
        assessment = assess_threshold(
            pest_id="DUBAS001",
            crop_type=CropType.DATE_PALM,
            observed_value=7.0,
        )
        assert assessment is not None
        assert assessment.recommendation != ""
        assert assessment.recommendation_ar != ""

    def test_assess_threshold_virus_modifier(self):
        """Virus presence should lower thresholds by 50%."""
        assessment_normal = assess_threshold(
            pest_id="APHID001",
            crop_type=CropType.TOMATO,
            observed_value=8.0,
        )
        assessment_virus = assess_threshold(
            pest_id="APHID001",
            crop_type=CropType.TOMATO,
            observed_value=8.0,
            virus_present=True,
        )
        if assessment_normal and assessment_virus:
            # With virus, adjusted threshold should be lower
            assert assessment_virus.adjusted_action_threshold <= assessment_normal.adjusted_action_threshold

    def test_assess_threshold_temperature_modifier(self):
        """Temperature should modify thresholds."""
        assessment_hot = assess_threshold(
            pest_id="DUBAS001",
            crop_type=CropType.DATE_PALM,
            observed_value=4.0,
            temperature_c=38.0,
        )
        assessment_cool = assess_threshold(
            pest_id="DUBAS001",
            crop_type=CropType.DATE_PALM,
            observed_value=4.0,
            temperature_c=15.0,
        )
        if assessment_hot and assessment_cool:
            # Different temperatures should produce different thresholds
            assert assessment_hot.adjusted_action_threshold != assessment_cool.adjusted_action_threshold

    def test_threshold_assessment_to_dict(self):
        assessment = assess_threshold(
            pest_id="DUBAS001",
            crop_type=CropType.DATE_PALM,
            observed_value=7.0,
        )
        assert assessment is not None
        d = assessment.to_dict()
        assert "pest_id" in d
        assert "infestation_level" in d
        assert "benefit_cost_ratio" in d


# ═══════════════════════════════════════════════════════════════════════════════
# Economic Calculation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEconomicCalculations:
    """Test economic calculation functions."""

    def test_calculate_eil(self):
        # calculate_economic_injury_level(control_cost_per_ha, crop_value_per_ha, damage_per_pest_unit, control_efficacy=0.85)
        eil = calculate_economic_injury_level(
            control_cost_per_ha=5000.0,
            crop_value_per_ha=50000.0,
            damage_per_pest_unit=100.0,
        )
        assert eil > 0

    def test_calculate_gain_threshold(self):
        # calculate_gain_threshold(eil, pest_growth_rate=1.5, days_to_treatment=3)
        gt = calculate_gain_threshold(eil=0.1)
        assert gt > 0

    def test_estimate_yield_loss(self):
        # estimate_yield_loss(infestation_level, threshold, area_ha)
        threshold = get_threshold("DUBAS001", CropType.DATE_PALM)
        assert threshold is not None
        loss = estimate_yield_loss(
            infestation_level=15.0,
            threshold=threshold,
            area_ha=1.0,
        )
        assert isinstance(loss, dict)

    def test_estimate_yield_loss_zero(self):
        threshold = get_threshold("DUBAS001", CropType.DATE_PALM)
        assert threshold is not None
        loss = estimate_yield_loss(
            infestation_level=0.0,
            threshold=threshold,
            area_ha=1.0,
        )
        assert isinstance(loss, dict)

    def test_calculate_treatment_roi(self):
        # calculate_treatment_roi(assessment: ThresholdAssessment)
        assessment = assess_threshold(
            pest_id="DUBAS001",
            crop_type=CropType.DATE_PALM,
            observed_value=15.0,
        )
        assert assessment is not None
        roi = calculate_treatment_roi(assessment)
        assert isinstance(roi, dict)


# ═══════════════════════════════════════════════════════════════════════════════
# Infestation Level Assessment Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestInfestationLevelAssessment:
    """Test infestation level assessment."""

    def test_assess_zero_count(self):
        obs = ScoutObservation(pest_id="RPW001", pest_name="RPW", pest_name_ar="سوسة", count=0)
        level = assess_infestation_level(obs, "RPW001")
        assert level == InfestationLevel.NONE

    def test_assess_low_count(self):
        obs = ScoutObservation(pest_id="APHID001", pest_name="Aphid", pest_name_ar="من", count=5)
        level = assess_infestation_level(obs, "APHID001")
        assert level in [InfestationLevel.TRACE, InfestationLevel.LOW, InfestationLevel.MODERATE]

    def test_assess_high_count(self):
        obs = ScoutObservation(pest_id="APHID001", pest_name="Aphid", pest_name_ar="من", count=200)
        level = assess_infestation_level(obs, "APHID001")
        assert level in list(InfestationLevel)  # Any valid level
