"""
Unit tests for shared/crop_rotation/models.py
Tests crop rotation data models including enums, CropCharacteristics,
RotationSlot, RotationSequence, RotationPlan, and PestDiseaseRisk.
"""

import pytest
from datetime import date, datetime, UTC

from shared.crop_rotation.models import (
    # Enums
    CropFamily,
    CropType,
    Season,
    RotationBenefit,
    SoilHealthIndicator,
    RecommendationPriority,
    PlanStatus,
    # Dataclasses
    CropCharacteristics,
    RotationSlot,
    RotationSequence,
    RotationPlan,
    PestDiseaseRisk,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_crop_family_values(self):
        assert CropFamily.POACEAE == "poaceae"
        assert CropFamily.FABACEAE == "fabaceae"
        assert CropFamily.SOLANACEAE == "solanaceae"
        assert CropFamily.ARECACEAE == "arecaceae"

    def test_crop_type_cereals(self):
        assert CropType.WHEAT == "wheat"
        assert CropType.BARLEY == "barley"
        assert CropType.RICE == "rice"

    def test_crop_type_legumes(self):
        assert CropType.ALFALFA == "alfalfa"
        assert CropType.CHICKPEA == "chickpea"
        assert CropType.FABA_BEAN == "faba_bean"

    def test_crop_type_special(self):
        assert CropType.FALLOW == "fallow"
        assert CropType.GREEN_MANURE == "green_manure"
        assert CropType.DATE_PALM == "date_palm"

    def test_season_values(self):
        assert Season.WINTER == "winter"
        assert Season.SUMMER == "summer"
        assert Season.YEAR_ROUND == "year_round"
        assert Season.PERENNIAL == "perennial"

    def test_rotation_benefit_values(self):
        assert RotationBenefit.NITROGEN_FIXATION == "nitrogen_fixation"
        assert RotationBenefit.PEST_BREAK == "pest_break"
        assert RotationBenefit.WATER_EFFICIENCY == "water_efficiency"

    def test_soil_health_indicator_values(self):
        assert SoilHealthIndicator.ORGANIC_MATTER == "organic_matter"
        assert SoilHealthIndicator.PH == "ph"
        assert SoilHealthIndicator.COMPACTION == "compaction"

    def test_plan_status_values(self):
        assert PlanStatus.DRAFT == "draft"
        assert PlanStatus.ACTIVE == "active"
        assert PlanStatus.ARCHIVED == "archived"


# =============================================================================
# CropCharacteristics Tests
# =============================================================================


class TestCropCharacteristics:
    def test_creation(self):
        cc = CropCharacteristics(
            crop_type=CropType.WHEAT,
            crop_family=CropFamily.POACEAE,
            name_en="Wheat",
            name_ar="قمح",
            growing_season=Season.WINTER,
        )
        assert cc.crop_type == CropType.WHEAT
        assert cc.crop_family == CropFamily.POACEAE
        assert cc.is_nitrogen_fixer is False
        assert cc.root_type == "fibrous"

    def test_defaults(self):
        cc = CropCharacteristics(
            crop_type=CropType.ALFALFA,
            crop_family=CropFamily.FABACEAE,
            name_en="Alfalfa",
            name_ar="برسيم",
            growing_season=Season.PERENNIAL,
        )
        assert cc.growing_days_min == 90
        assert cc.growing_days_max == 150
        assert cc.water_requirement_mm == 400.0
        assert cc.drought_tolerance == 0.5
        assert cc.min_rotation_years == 1

    def test_nitrogen_fixer(self):
        cc = CropCharacteristics(
            crop_type=CropType.ALFALFA,
            crop_family=CropFamily.FABACEAE,
            name_en="Alfalfa",
            name_ar="برسيم",
            growing_season=Season.PERENNIAL,
            is_nitrogen_fixer=True,
            residue_nitrogen_kg_ha=150.0,
        )
        assert cc.is_nitrogen_fixer is True
        assert cc.residue_nitrogen_kg_ha == 150.0

    def test_to_dict(self):
        cc = CropCharacteristics(
            crop_type=CropType.TOMATO,
            crop_family=CropFamily.SOLANACEAE,
            name_en="Tomato",
            name_ar="طماطم",
            growing_season=Season.SUMMER,
            water_requirement_mm=600.0,
        )
        d = cc.to_dict()
        assert d["crop_type"] == "tomato"
        assert d["crop_family"] == "solanaceae"
        assert d["growing_season"] == "summer"
        assert d["water_requirement_mm"] == 600.0
        assert "growing_days" in d
        assert d["growing_days"]["min"] == 90

    def test_with_pest_disease_lists(self):
        cc = CropCharacteristics(
            crop_type=CropType.WHEAT,
            crop_family=CropFamily.POACEAE,
            name_en="Wheat",
            name_ar="قمح",
            growing_season=Season.WINTER,
            major_pests=["aphid", "sunn_pest"],
            major_diseases=["leaf_rust", "yellow_rust"],
        )
        assert len(cc.major_pests) == 2
        assert len(cc.major_diseases) == 2


# =============================================================================
# RotationSlot Tests
# =============================================================================


class TestRotationSlot:
    def test_creation_defaults(self):
        slot = RotationSlot()
        assert slot.slot_id  # UUID
        assert slot.crop_type is None
        assert slot.season == Season.WINTER
        assert slot.year == 1
        assert slot.is_completed is False
        assert slot.expected_nitrogen_contribution_kg_ha == 0.0

    def test_creation_with_values(self):
        slot = RotationSlot(
            crop_type=CropType.WHEAT,
            season=Season.WINTER,
            year=1,
            area_ha=10.0,
            expected_yield_tons_ha=4.5,
            rotation_benefits=[RotationBenefit.PEST_BREAK],
        )
        assert slot.crop_type == CropType.WHEAT
        assert slot.area_ha == 10.0
        assert RotationBenefit.PEST_BREAK in slot.rotation_benefits

    def test_to_dict(self):
        slot = RotationSlot(
            crop_type=CropType.ALFALFA,
            season=Season.PERENNIAL,
            year=2,
            expected_nitrogen_contribution_kg_ha=150.0,
            rotation_benefits=[RotationBenefit.NITROGEN_FIXATION, RotationBenefit.SOIL_STRUCTURE],
        )
        d = slot.to_dict()
        assert d["crop_type"] == "alfalfa"
        assert d["season"] == "perennial"
        assert d["year"] == 2
        assert "nitrogen_fixation" in d["rotation_benefits"]

    def test_completed_slot(self):
        slot = RotationSlot(
            crop_type=CropType.WHEAT,
            is_completed=True,
            actual_planting_date=date(2025, 11, 1),
            actual_harvest_date=date(2026, 4, 15),
            actual_yield_tons_ha=4.2,
        )
        assert slot.is_completed is True
        assert slot.actual_yield_tons_ha == 4.2


# =============================================================================
# RotationSequence Tests
# =============================================================================


class TestRotationSequence:
    def _make_sequence(self):
        slots = [
            RotationSlot(crop_type=CropType.WHEAT, season=Season.WINTER, year=1, expected_nitrogen_contribution_kg_ha=-50),
            RotationSlot(crop_type=CropType.ALFALFA, season=Season.SUMMER, year=1, expected_nitrogen_contribution_kg_ha=150),
            RotationSlot(crop_type=CropType.TOMATO, season=Season.WINTER, year=2, expected_nitrogen_contribution_kg_ha=-30),
        ]
        return RotationSequence(
            name="Wheat-Alfalfa-Tomato",
            name_ar="قمح-برسيم-طماطم",
            cycle_years=2,
            slots=slots,
        )

    def test_creation(self):
        seq = self._make_sequence()
        assert seq.name == "Wheat-Alfalfa-Tomato"
        assert seq.cycle_years == 2
        assert len(seq.slots) == 3

    def test_get_slots_for_year(self):
        seq = self._make_sequence()
        year1 = seq.get_slots_for_year(1)
        assert len(year1) == 2
        year2 = seq.get_slots_for_year(2)
        assert len(year2) == 1

    def test_get_crop_sequence(self):
        seq = self._make_sequence()
        crops = seq.get_crop_sequence()
        assert len(crops) == 3
        assert CropType.WHEAT in crops

    def test_calculate_nitrogen_balance(self):
        seq = self._make_sequence()
        balance = seq.calculate_nitrogen_balance()
        assert balance == pytest.approx(70.0)  # -50 + 150 + (-30)

    def test_to_dict(self):
        seq = self._make_sequence()
        d = seq.to_dict()
        assert d["name"] == "Wheat-Alfalfa-Tomato"
        assert d["cycle_years"] == 2
        assert len(d["slots"]) == 3
        assert d["nitrogen_balance_kg_ha"] == pytest.approx(70.0)


# =============================================================================
# RotationPlan Tests
# =============================================================================


class TestRotationPlan:
    def test_creation_defaults(self):
        plan = RotationPlan()
        assert plan.plan_id  # UUID
        assert plan.status == PlanStatus.DRAFT
        assert plan.planning_horizon_years == 5
        assert plan.total_area_ha == 0.0

    def test_creation_with_values(self):
        plan = RotationPlan(
            tenant_id="tenant-001",
            field_id="field-001",
            name="Main Field Plan",
            name_ar="خطة الحقل الرئيسي",
            total_area_ha=25.0,
            status=PlanStatus.ACTIVE,
        )
        assert plan.tenant_id == "tenant-001"
        assert plan.status == PlanStatus.ACTIVE
        assert plan.total_area_ha == 25.0

    def test_to_dict(self):
        plan = RotationPlan(
            name="Test Plan",
            name_ar="خطة اختبار",
            total_area_ha=10.0,
            start_date=date(2026, 1, 1),
            projected_profit_per_ha=5000.0,
        )
        d = plan.to_dict()
        assert d["name"] == "Test Plan"
        assert d["start_date"] == "2026-01-01"
        assert d["projected_profit_per_ha"] == 5000.0
        assert d["status"] == "draft"

    def test_to_dict_with_sequence(self):
        seq = RotationSequence(name="seq1", name_ar="تسلسل1")
        plan = RotationPlan(sequence=seq)
        d = plan.to_dict()
        assert d["sequence"] is not None
        assert d["sequence"]["name"] == "seq1"

    def test_to_dict_without_sequence(self):
        plan = RotationPlan()
        d = plan.to_dict()
        assert d["sequence"] is None


# =============================================================================
# PestDiseaseRisk Tests
# =============================================================================


class TestPestDiseaseRisk:
    def test_creation_defaults(self):
        risk = PestDiseaseRisk()
        assert risk.risk_id  # UUID
        assert risk.is_pest is True
        assert risk.soil_persistence_years == 1
        assert risk.recommended_break_years == 2

    def test_pest_creation(self):
        risk = PestDiseaseRisk(
            name_en="Sunn Pest",
            name_ar="حشرة السونة",
            is_pest=True,
            pest_type="insect",
            host_crops=[CropType.WHEAT, CropType.BARLEY],
            primary_host=CropType.WHEAT,
            break_crops=[CropType.ALFALFA, CropType.TOMATO],
            yield_loss_potential_percent=30.0,
        )
        assert risk.name_en == "Sunn Pest"
        assert risk.is_pest is True
        assert CropType.WHEAT in risk.host_crops
        assert risk.yield_loss_potential_percent == 30.0

    def test_disease_creation(self):
        risk = PestDiseaseRisk(
            name_en="Leaf Rust",
            name_ar="صدأ الأوراق",
            is_pest=False,
            disease_type="fungal",
            host_crops=[CropType.WHEAT],
            soil_persistence_years=2,
            overwinters_in_residue=True,
        )
        assert risk.is_pest is False
        assert risk.disease_type == "fungal"
        assert risk.soil_persistence_years == 2
        assert risk.overwinters_in_residue is True
