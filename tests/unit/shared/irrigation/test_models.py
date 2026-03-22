"""
Unit tests for shared/irrigation/models.py
Tests irrigation HMC framework Pydantic models including enums,
BilingualLabel, IrrigationGoal, EcologicalConstraint, and ExperienceRule.
"""

import pytest
from uuid import UUID

from pydantic import ValidationError

from shared.irrigation.models import (
    # Enums
    IrrigationGoalType,
    ExperienceSource,
    DecisionType,
    SoilType,
    ProductivityLevel,
    ChecklistDimension,
    CalibrationMethod,
    SessionStatus,
    # Pydantic models
    BilingualLabel,
    IrrigationGoal,
    EcologicalConstraint,
    ExperienceRule,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_irrigation_goal_type(self):
        assert IrrigationGoalType.WATER_SAVING == "water_saving"
        assert IrrigationGoalType.HIGH_YIELD == "high_yield"
        assert IrrigationGoalType.BALANCED == "balanced"
        assert IrrigationGoalType.ENERGY_EFFICIENT == "energy_efficient"

    def test_experience_source(self):
        assert ExperienceSource.FARMER == "farmer"
        assert ExperienceSource.RESEARCH == "research"
        assert ExperienceSource.AI_LEARNED == "ai_learned"
        assert ExperienceSource.TRADITIONAL == "traditional"

    def test_decision_type(self):
        assert DecisionType.APPROVE == "approve"
        assert DecisionType.REJECT == "reject"
        assert DecisionType.MODIFY == "modify"
        assert DecisionType.OVERRIDE == "override"

    def test_soil_type(self):
        assert SoilType.SANDY == "sandy"
        assert SoilType.CLAY == "clay"
        assert SoilType.LOAMY == "loamy"

    def test_productivity_level(self):
        assert ProductivityLevel.LOW == "low"
        assert ProductivityLevel.MEDIUM == "medium"
        assert ProductivityLevel.HIGH == "high"

    def test_checklist_dimension(self):
        assert ChecklistDimension.GOAL_ANCHORING == "goal_anchoring"
        assert ChecklistDimension.EXPERIENCE_INJECTION == "experience_injection"

    def test_calibration_method(self):
        assert CalibrationMethod.SIMULATION == "simulation"
        assert CalibrationMethod.FIELD_TRIAL == "field_trial"
        assert CalibrationMethod.A_B_TEST == "a_b_test"

    def test_session_status(self):
        assert SessionStatus.INITIALIZED == "initialized"
        assert SessionStatus.APPROVED == "approved"
        assert SessionStatus.COMPLETED == "completed"
        assert SessionStatus.CANCELLED == "cancelled"


# =============================================================================
# BilingualLabel Tests
# =============================================================================


class TestBilingualLabel:
    def test_creation(self):
        label = BilingualLabel(en="Water Saving", ar="توفير المياه")
        assert label.en == "Water Saving"
        assert label.ar == "توفير المياه"

    def test_str(self):
        label = BilingualLabel(en="Irrigation", ar="ري")
        assert str(label) == "Irrigation | ري"

    def test_requires_both_fields(self):
        with pytest.raises(ValidationError):
            BilingualLabel(en="Only English")


# =============================================================================
# IrrigationGoal Tests
# =============================================================================


class TestIrrigationGoal:
    def test_creation_minimal(self):
        goal = IrrigationGoal(goal_type=IrrigationGoalType.WATER_SAVING)
        assert goal.goal_type == IrrigationGoalType.WATER_SAVING
        assert isinstance(goal.id, UUID)
        assert goal.priority == 1
        assert goal.is_primary is False
        assert goal.name == ""

    def test_creation_full(self):
        goal = IrrigationGoal(
            goal_type=IrrigationGoalType.HIGH_YIELD,
            name="Maximize Yield",
            name_ar="تعظيم الإنتاج",
            description="Maximize crop yield per hectare",
            target_value=5.0,
            target_reduction=0.1,
            priority=1,
            is_primary=True,
        )
        assert goal.name == "Maximize Yield"
        assert goal.target_value == 5.0
        assert goal.target_reduction == 0.1
        assert goal.is_primary is True

    def test_target_reduction_validation_max(self):
        with pytest.raises(ValidationError):
            IrrigationGoal(
                goal_type=IrrigationGoalType.WATER_SAVING,
                target_reduction=1.5,  # > 1.0
            )

    def test_target_reduction_validation_min(self):
        with pytest.raises(ValidationError):
            IrrigationGoal(
                goal_type=IrrigationGoalType.WATER_SAVING,
                target_reduction=-0.1,  # < 0.0
            )

    def test_priority_validation(self):
        with pytest.raises(ValidationError):
            IrrigationGoal(
                goal_type=IrrigationGoalType.BALANCED,
                priority=0,  # < 1
            )
        with pytest.raises(ValidationError):
            IrrigationGoal(
                goal_type=IrrigationGoalType.BALANCED,
                priority=11,  # > 10
            )

    def test_priority_valid_range(self):
        goal = IrrigationGoal(
            goal_type=IrrigationGoalType.BALANCED,
            priority=10,
        )
        assert goal.priority == 10

    def test_serialization(self):
        goal = IrrigationGoal(
            goal_type=IrrigationGoalType.WATER_SAVING,
            target_reduction=0.3,
        )
        d = goal.model_dump()
        assert d["goal_type"] == "water_saving"
        assert d["target_reduction"] == 0.3
        assert "id" in d

    def test_metadata_dict(self):
        goal = IrrigationGoal(
            goal_type=IrrigationGoalType.WATER_SAVING,
            metadata={"source": "research", "study_id": "S-001"},
        )
        assert goal.metadata["source"] == "research"


# =============================================================================
# EcologicalConstraint Tests
# =============================================================================


class TestEcologicalConstraint:
    def test_creation_minimal(self):
        constraint = EcologicalConstraint()
        assert isinstance(constraint.id, UUID)
        assert constraint.is_mandatory is True
        assert constraint.enforcement_level == "strict"

    def test_water_constraints(self):
        constraint = EcologicalConstraint(
            water_quota_m3=5000.0,
            water_quota_reduction=0.3,
            min_irrigation_interval_hours=12,
        )
        assert constraint.water_quota_m3 == 5000.0
        assert constraint.water_quota_reduction == 0.3
        assert constraint.min_irrigation_interval_hours == 12

    def test_soil_constraints(self):
        constraint = EcologicalConstraint(
            soil_salinity_limit=4.0,
            soil_moisture_min=20.0,
            soil_moisture_max=80.0,
        )
        assert constraint.soil_salinity_limit == 4.0
        assert constraint.soil_moisture_min == 20.0
        assert constraint.soil_moisture_max == 80.0

    def test_soil_moisture_validation(self):
        """soil_moisture_max must be >= soil_moisture_min."""
        with pytest.raises(ValidationError):
            EcologicalConstraint(
                soil_moisture_min=80.0,
                soil_moisture_max=20.0,  # Less than min
            )

    def test_water_quota_reduction_range(self):
        with pytest.raises(ValidationError):
            EcologicalConstraint(water_quota_reduction=1.5)  # > 1.0

    def test_negative_water_quota(self):
        with pytest.raises(ValidationError):
            EcologicalConstraint(water_quota_m3=-100)

    def test_environmental_constraints(self):
        constraint = EcologicalConstraint(
            carbon_emission_target=100.0,
            nitrogen_runoff_limit=50.0,
        )
        assert constraint.carbon_emission_target == 100.0
        assert constraint.nitrogen_runoff_limit == 50.0

    def test_time_constraints(self):
        constraint = EcologicalConstraint(
            no_irrigation_hours=[12, 13, 14],
            seasonal_restrictions={"summer": {"max_daily_hours": 4}},
        )
        assert 12 in constraint.no_irrigation_hours
        assert "summer" in constraint.seasonal_restrictions

    def test_serialization(self):
        constraint = EcologicalConstraint(
            name="Water Quota",
            name_ar="حصة المياه",
            water_quota_m3=5000.0,
        )
        d = constraint.model_dump()
        assert d["name"] == "Water Quota"
        assert d["water_quota_m3"] == 5000.0


# =============================================================================
# ExperienceRule Tests
# =============================================================================


class TestExperienceRule:
    def test_creation(self):
        rule = ExperienceRule(
            condition="wheat_cold_wave",
            action="reduce_irrigation_20%",
            source=ExperienceSource.FARMER,
        )
        assert rule.condition == "wheat_cold_wave"
        assert rule.action == "reduce_irrigation_20%"
        assert rule.source == ExperienceSource.FARMER
        assert isinstance(rule.id, UUID)

    def test_creation_full(self):
        rule = ExperienceRule(
            name="Cold wave irrigation rule",
            name_ar="قاعدة ري موجة البرد",
            condition="temperature_below_5c_for_3_days",
            condition_ar="درجة الحرارة أقل من 5 درجات لمدة 3 أيام",
            action="reduce_irrigation_by_20_percent",
            action_ar="تقليل الري بنسبة 20 بالمائة",
            source=ExperienceSource.RESEARCH,
            source_detail="Study: XYZ University 2024",
            rationale="Cold reduces evapotranspiration",
            rationale_ar="البرد يقلل من التبخر والنتح",
        )
        assert rule.name == "Cold wave irrigation rule"
        assert rule.source == ExperienceSource.RESEARCH
        assert rule.rationale == "Cold reduces evapotranspiration"

    def test_condition_required(self):
        with pytest.raises(ValidationError):
            ExperienceRule(
                condition="",  # min_length=1
                action="reduce_irrigation",
                source=ExperienceSource.FARMER,
            )

    def test_action_required(self):
        with pytest.raises(ValidationError):
            ExperienceRule(
                condition="some_condition",
                action="",  # min_length=1
                source=ExperienceSource.FARMER,
            )

    def test_serialization(self):
        rule = ExperienceRule(
            condition="high_salinity",
            action="leaching_irrigation",
            source=ExperienceSource.EXTENSION,
        )
        d = rule.model_dump()
        assert d["condition"] == "high_salinity"
        assert d["action"] == "leaching_irrigation"
        assert d["source"] == "extension"
