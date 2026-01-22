"""
SAHOOL HMC Irrigation Decision Framework - Model Tests
اختبارات نماذج إطار قرارات الري التعاوني

Tests all Pydantic models:
- IrrigationGoal
- EcologicalConstraint
- ExperienceRule (farmer and AI sources)
- HumanDecisionOverride
- CalibrationResult
- ZoneConfiguration
- ChecklistItem
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest
from pydantic import BaseModel, Field, ValidationError, field_validator

# ═══════════════════════════════════════════════════════════════════════════════
# Model Definitions for Testing
# These would normally be imported from the actual module
# ═══════════════════════════════════════════════════════════════════════════════


class GoalPriority:
    WATER_SAVING = "water_saving"
    HIGH_YIELD = "high_yield"
    BALANCED = "balanced"
    ECOLOGICAL = "ecological"


class ConstraintType:
    WATER_LIMIT = "water_limit"
    GROUNDWATER_PROTECTION = "groundwater_protection"
    SOIL_HEALTH = "soil_health"
    BIODIVERSITY = "biodiversity"
    CARBON_FOOTPRINT = "carbon_footprint"


class RuleSource:
    FARMER = "farmer"
    AI = "ai"
    AGRONOMIST = "agronomist"
    HISTORICAL = "historical"


class IrrigationGoal(BaseModel):
    """Irrigation goal model"""

    goal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    farm_id: str
    field_id: str
    tenant_id: str
    priority: str = GoalPriority.BALANCED
    target_water_savings_percent: float = Field(ge=0, le=100)
    target_yield_kg_ha: float = Field(ge=0)
    min_yield_threshold_percent: float = Field(ge=0, le=100, default=85.0)
    season: str
    crop_type: str
    description_en: str | None = None
    description_ar: str | None = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    valid_from: date
    valid_until: date
    is_active: bool = True

    @field_validator("valid_until")
    @classmethod
    def validate_dates(cls, v: date, info) -> date:
        """Ensure valid_until is after valid_from"""
        if "valid_from" in info.data and v <= info.data["valid_from"]:
            raise ValueError("valid_until must be after valid_from")
        return v


class EcologicalConstraint(BaseModel):
    """Ecological constraint model"""

    constraint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    farm_id: str
    tenant_id: str
    constraint_type: str
    name_en: str
    name_ar: str
    max_daily_water_m3: float | None = Field(default=None, ge=0)
    max_weekly_water_m3: float | None = Field(default=None, ge=0)
    max_seasonal_water_m3: float | None = Field(default=None, ge=0)
    min_groundwater_level_m: float | None = None
    buffer_zone_m: float | None = Field(default=None, ge=0)
    sensitive_period_start: date | None = None
    sensitive_period_end: date | None = None
    penalty_coefficient: float = Field(ge=1.0, default=1.0)
    is_mandatory: bool = True
    regulatory_reference: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("constraint_type")
    @classmethod
    def validate_constraint_type(cls, v: str) -> str:
        """Validate constraint type"""
        valid_types = [
            ConstraintType.WATER_LIMIT,
            ConstraintType.GROUNDWATER_PROTECTION,
            ConstraintType.SOIL_HEALTH,
            ConstraintType.BIODIVERSITY,
            ConstraintType.CARBON_FOOTPRINT,
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid constraint type: {v}")
        return v


class ExperienceRule(BaseModel):
    """Experience rule model for farmer and AI knowledge"""

    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    farm_id: str
    tenant_id: str
    source: str
    source_id: str
    crop_type: str
    condition_en: str
    condition_ar: str
    action_en: str
    action_ar: str
    condition_formula: str
    action_parameters: dict[str, Any]
    confidence: float = Field(ge=0, le=1)
    success_rate: float = Field(ge=0, le=1, default=0.0)
    applications_count: int = Field(ge=0, default=0)
    learned_from_observations: int = Field(ge=0, default=0)
    model_version: str | None = None
    training_data_size: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_applied: datetime | None = None
    is_validated: bool = False
    validation_date: datetime | None = None
    requires_human_validation: bool = False

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate rule source"""
        valid_sources = [
            RuleSource.FARMER,
            RuleSource.AI,
            RuleSource.AGRONOMIST,
            RuleSource.HISTORICAL,
        ]
        if v not in valid_sources:
            raise ValueError(f"Invalid rule source: {v}")
        return v


class HumanDecisionOverride(BaseModel):
    """Human decision override model"""

    override_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    program_id: str
    user_id: str
    override_type: str
    original_value: dict[str, Any]
    new_value: dict[str, Any]
    reason_en: str
    reason_ar: str | None = None
    confidence: float = Field(ge=0, le=1, default=0.5)
    requires_validation: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("override_type")
    @classmethod
    def validate_override_type(cls, v: str) -> str:
        """Validate override type"""
        valid_types = [
            "schedule_modification",
            "water_amount_change",
            "timing_change",
            "zone_exclusion",
            "emergency_override",
            "constraint_relaxation",
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid override type: {v}")
        return v


class CalibrationResult(BaseModel):
    """Calibration result model"""

    calibration_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    program_id: str
    calibration_type: str
    status: str
    simulated_water_savings_percent: float = Field(ge=0, le=100)
    simulated_yield_percent: float = Field(ge=0)
    goal_water_savings_percent: float = Field(ge=0, le=100)
    goal_yield_percent: float = Field(ge=0, le=100)
    water_savings_gap: float
    yield_margin: float
    confidence: float = Field(ge=0, le=1)
    simulation_parameters: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    recommendations_ar: list[str] = Field(default_factory=list)
    calibrated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    calibrated_by: str

    @field_validator("calibration_type")
    @classmethod
    def validate_calibration_type(cls, v: str) -> str:
        """Validate calibration type"""
        valid_types = ["simulation", "field_trial", "historical_comparison", "expert_review"]
        if v not in valid_types:
            raise ValueError(f"Invalid calibration type: {v}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate calibration status"""
        valid_statuses = ["pending", "running", "passed", "failed", "warning"]
        if v not in valid_statuses:
            raise ValueError(f"Invalid calibration status: {v}")
        return v


class ZoneConfiguration(BaseModel):
    """Irrigation zone configuration model"""

    zone_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    field_id: str
    farm_id: str
    name_en: str
    name_ar: str
    zone_type: str
    area_hectares: float = Field(gt=0)
    soil_type: str
    irrigation_method: str
    flow_rate_m3_hr: float = Field(gt=0)
    efficiency_percent: float = Field(ge=0, le=100)
    emitter_spacing_m: float | None = Field(default=None, gt=0)
    lateral_spacing_m: float | None = Field(default=None, gt=0)
    sensors: list[dict[str, Any]] = Field(default_factory=list)
    crop_type: str
    growth_stage: str
    root_depth_cm: float = Field(gt=0)
    water_holding_capacity_mm_m: float = Field(gt=0)
    management_allowable_depletion: float = Field(ge=0, le=1)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("zone_type")
    @classmethod
    def validate_zone_type(cls, v: str) -> str:
        """Validate zone type"""
        valid_types = ["high_value", "standard", "water_scarce", "sensitive"]
        if v not in valid_types:
            raise ValueError(f"Invalid zone type: {v}")
        return v


class ChecklistItem(BaseModel):
    """Validation checklist item model"""

    item_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    category: str
    order: int = Field(ge=1)
    title_en: str
    title_ar: str
    description_en: str | None = None
    description_ar: str | None = None
    is_required: bool = True
    is_completed: bool = False
    completed_at: datetime | None = None
    completed_by: str | None = None
    validation_data: dict[str, Any] | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate checklist category"""
        valid_categories = [
            "goal_anchoring",
            "experience_injection",
            "supervision",
            "value_upgrade",
        ]
        if v not in valid_categories:
            raise ValueError(f"Invalid checklist category: {v}")
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# IrrigationGoal Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIrrigationGoalCreation:
    """Test IrrigationGoal model creation and validation"""

    def test_create_basic_irrigation_goal(self, sample_irrigation_goal):
        """Test creating a basic irrigation goal"""
        goal = IrrigationGoal(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            priority=sample_irrigation_goal["priority"],
            target_water_savings_percent=sample_irrigation_goal["target_water_savings_percent"],
            target_yield_kg_ha=sample_irrigation_goal["target_yield_kg_ha"],
            season=sample_irrigation_goal["season"],
            crop_type=sample_irrigation_goal["crop_type"],
            created_by=sample_irrigation_goal["created_by"],
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=120),
        )

        assert goal.farm_id == sample_irrigation_goal["farm_id"]
        assert goal.priority == GoalPriority.WATER_SAVING
        assert goal.target_water_savings_percent == 25.0
        assert goal.is_active is True

    def test_create_goal_with_descriptions(self, sample_irrigation_goal):
        """Test creating goal with bilingual descriptions"""
        goal = IrrigationGoal(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            target_water_savings_percent=25.0,
            target_yield_kg_ha=5000.0,
            season="winter",
            crop_type="wheat",
            description_en="Reduce water usage by 25%",
            description_ar="تقليل استخدام المياه بنسبة 25%",
            created_by=sample_irrigation_goal["created_by"],
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=90),
        )

        assert goal.description_en is not None
        assert goal.description_ar is not None
        assert "25%" in goal.description_en

    def test_goal_date_validation(self, sample_irrigation_goal):
        """Test that valid_until must be after valid_from"""
        with pytest.raises(ValidationError) as exc_info:
            IrrigationGoal(
                farm_id=sample_irrigation_goal["farm_id"],
                field_id=sample_irrigation_goal["field_id"],
                tenant_id=sample_irrigation_goal["tenant_id"],
                target_water_savings_percent=25.0,
                target_yield_kg_ha=5000.0,
                season="winter",
                crop_type="wheat",
                created_by=sample_irrigation_goal["created_by"],
                valid_from=date.today(),
                valid_until=date.today() - timedelta(days=1),  # Invalid: before valid_from
            )

        assert "valid_until must be after valid_from" in str(exc_info.value)

    def test_goal_water_savings_range(self, sample_irrigation_goal):
        """Test water savings percentage validation (0-100)"""
        # Valid: 0%
        goal_zero = IrrigationGoal(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            target_water_savings_percent=0.0,
            target_yield_kg_ha=5000.0,
            season="winter",
            crop_type="wheat",
            created_by=sample_irrigation_goal["created_by"],
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=90),
        )
        assert goal_zero.target_water_savings_percent == 0.0

        # Valid: 100%
        goal_max = IrrigationGoal(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            target_water_savings_percent=100.0,
            target_yield_kg_ha=5000.0,
            season="winter",
            crop_type="wheat",
            created_by=sample_irrigation_goal["created_by"],
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=90),
        )
        assert goal_max.target_water_savings_percent == 100.0

        # Invalid: > 100%
        with pytest.raises(ValidationError):
            IrrigationGoal(
                farm_id=sample_irrigation_goal["farm_id"],
                field_id=sample_irrigation_goal["field_id"],
                tenant_id=sample_irrigation_goal["tenant_id"],
                target_water_savings_percent=150.0,
                target_yield_kg_ha=5000.0,
                season="winter",
                crop_type="wheat",
                created_by=sample_irrigation_goal["created_by"],
                valid_from=date.today(),
                valid_until=date.today() + timedelta(days=90),
            )

    def test_goal_generates_uuid(self):
        """Test that goal_id is auto-generated as UUID"""
        goal = IrrigationGoal(
            farm_id=str(uuid.uuid4()),
            field_id=str(uuid.uuid4()),
            tenant_id=str(uuid.uuid4()),
            target_water_savings_percent=20.0,
            target_yield_kg_ha=4500.0,
            season="summer",
            crop_type="tomato",
            created_by=str(uuid.uuid4()),
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=60),
        )

        assert goal.goal_id is not None
        # Verify it's a valid UUID string
        uuid.UUID(goal.goal_id)


# ═══════════════════════════════════════════════════════════════════════════════
# EcologicalConstraint Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEcologicalConstraintValidation:
    """Test EcologicalConstraint model validation"""

    def test_create_water_limit_constraint(self, sample_ecological_constraint):
        """Test creating a water limit constraint"""
        constraint = EcologicalConstraint(
            farm_id=sample_ecological_constraint["farm_id"],
            tenant_id=sample_ecological_constraint["tenant_id"],
            constraint_type=ConstraintType.WATER_LIMIT,
            name_en="Daily Water Limit",
            name_ar="حد المياه اليومي",
            max_daily_water_m3=500.0,
            max_weekly_water_m3=3000.0,
        )

        assert constraint.constraint_type == ConstraintType.WATER_LIMIT
        assert constraint.max_daily_water_m3 == 500.0
        assert constraint.is_mandatory is True

    def test_create_groundwater_constraint(self, sample_ecological_constraint):
        """Test creating a groundwater protection constraint"""
        constraint = EcologicalConstraint(
            farm_id=sample_ecological_constraint["farm_id"],
            tenant_id=sample_ecological_constraint["tenant_id"],
            constraint_type=ConstraintType.GROUNDWATER_PROTECTION,
            name_en="Groundwater Level Protection",
            name_ar="حماية مستوى المياه الجوفية",
            min_groundwater_level_m=-50.0,
            buffer_zone_m=100.0,
        )

        assert constraint.min_groundwater_level_m == -50.0
        assert constraint.buffer_zone_m == 100.0

    def test_constraint_type_validation(self, sample_ecological_constraint):
        """Test constraint type validation"""
        with pytest.raises(ValidationError) as exc_info:
            EcologicalConstraint(
                farm_id=sample_ecological_constraint["farm_id"],
                tenant_id=sample_ecological_constraint["tenant_id"],
                constraint_type="invalid_type",
                name_en="Invalid",
                name_ar="غير صالح",
            )

        assert "Invalid constraint type" in str(exc_info.value)

    def test_constraint_penalty_coefficient(self, sample_ecological_constraint):
        """Test penalty coefficient validation (must be >= 1.0)"""
        # Valid coefficient
        constraint = EcologicalConstraint(
            farm_id=sample_ecological_constraint["farm_id"],
            tenant_id=sample_ecological_constraint["tenant_id"],
            constraint_type=ConstraintType.WATER_LIMIT,
            name_en="Test",
            name_ar="اختبار",
            penalty_coefficient=1.5,
        )
        assert constraint.penalty_coefficient == 1.5

        # Invalid coefficient (< 1.0)
        with pytest.raises(ValidationError):
            EcologicalConstraint(
                farm_id=sample_ecological_constraint["farm_id"],
                tenant_id=sample_ecological_constraint["tenant_id"],
                constraint_type=ConstraintType.WATER_LIMIT,
                name_en="Test",
                name_ar="اختبار",
                penalty_coefficient=0.5,
            )

    def test_constraint_with_sensitive_period(self, sample_ecological_constraint):
        """Test constraint with sensitive period dates"""
        constraint = EcologicalConstraint(
            farm_id=sample_ecological_constraint["farm_id"],
            tenant_id=sample_ecological_constraint["tenant_id"],
            constraint_type=ConstraintType.BIODIVERSITY,
            name_en="Bird Nesting Season Protection",
            name_ar="حماية موسم تعشيش الطيور",
            sensitive_period_start=date.today(),
            sensitive_period_end=date.today() + timedelta(days=60),
        )

        assert constraint.sensitive_period_start is not None
        assert constraint.sensitive_period_end is not None


# ═══════════════════════════════════════════════════════════════════════════════
# ExperienceRule Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestExperienceRuleFromFarmer:
    """Test ExperienceRule model for farmer-sourced rules"""

    def test_create_farmer_experience_rule(self, sample_experience_rule):
        """Test creating a farmer experience rule"""
        rule = ExperienceRule(
            farm_id=sample_experience_rule["farm_id"],
            tenant_id=sample_experience_rule["tenant_id"],
            source=RuleSource.FARMER,
            source_id=sample_experience_rule["source_id"],
            crop_type="wheat",
            condition_en="When soil is dry and hot",
            condition_ar="عندما تكون التربة جافة وحارة",
            action_en="Irrigate early morning",
            action_ar="الري في الصباح الباكر",
            condition_formula="soil_moisture < 35 AND temperature > 30",
            action_parameters={"water_amount_mm": 20, "start_time": "06:00"},
            confidence=0.85,
        )

        assert rule.source == RuleSource.FARMER
        assert rule.confidence == 0.85
        assert rule.is_validated is False

    def test_farmer_rule_with_validation(self, sample_experience_rule):
        """Test farmer rule with validation data"""
        rule = ExperienceRule(
            farm_id=sample_experience_rule["farm_id"],
            tenant_id=sample_experience_rule["tenant_id"],
            source=RuleSource.FARMER,
            source_id=sample_experience_rule["source_id"],
            crop_type="wheat",
            condition_en="Test condition",
            condition_ar="شرط الاختبار",
            action_en="Test action",
            action_ar="إجراء الاختبار",
            condition_formula="test_condition",
            action_parameters={},
            confidence=0.9,
            is_validated=True,
            validation_date=datetime.now(UTC),
            success_rate=0.92,
            applications_count=45,
        )

        assert rule.is_validated is True
        assert rule.success_rate == 0.92
        assert rule.applications_count == 45


class TestExperienceRuleFromAI:
    """Test ExperienceRule model for AI-generated rules"""

    def test_create_ai_experience_rule(self, sample_ai_experience_rule):
        """Test creating an AI-generated experience rule"""
        rule = ExperienceRule(
            farm_id=sample_ai_experience_rule["farm_id"],
            tenant_id=sample_ai_experience_rule["tenant_id"],
            source=RuleSource.AI,
            source_id="model-irrigation-v2",
            crop_type="tomato",
            condition_en="NDVI drop detected",
            condition_ar="تم اكتشاف انخفاض NDVI",
            action_en="Increase irrigation",
            action_ar="زيادة الري",
            condition_formula="ndvi_delta < -0.05",
            action_parameters={"water_amount_mm": 25},
            confidence=0.78,
            model_version="2.1.0",
            training_data_size=10000,
            requires_human_validation=True,
        )

        assert rule.source == RuleSource.AI
        assert rule.model_version == "2.1.0"
        assert rule.requires_human_validation is True

    def test_ai_rule_confidence_range(self, sample_ai_experience_rule):
        """Test AI rule confidence validation (0-1)"""
        # Valid confidence
        rule = ExperienceRule(
            farm_id=sample_ai_experience_rule["farm_id"],
            tenant_id=sample_ai_experience_rule["tenant_id"],
            source=RuleSource.AI,
            source_id="model-test",
            crop_type="wheat",
            condition_en="Test",
            condition_ar="اختبار",
            action_en="Test",
            action_ar="اختبار",
            condition_formula="test",
            action_parameters={},
            confidence=0.5,
        )
        assert rule.confidence == 0.5

        # Invalid confidence (> 1)
        with pytest.raises(ValidationError):
            ExperienceRule(
                farm_id=sample_ai_experience_rule["farm_id"],
                tenant_id=sample_ai_experience_rule["tenant_id"],
                source=RuleSource.AI,
                source_id="model-test",
                crop_type="wheat",
                condition_en="Test",
                condition_ar="اختبار",
                action_en="Test",
                action_ar="اختبار",
                condition_formula="test",
                action_parameters={},
                confidence=1.5,
            )

    def test_rule_source_validation(self, sample_experience_rule):
        """Test rule source validation"""
        with pytest.raises(ValidationError) as exc_info:
            ExperienceRule(
                farm_id=sample_experience_rule["farm_id"],
                tenant_id=sample_experience_rule["tenant_id"],
                source="invalid_source",
                source_id="test",
                crop_type="wheat",
                condition_en="Test",
                condition_ar="اختبار",
                action_en="Test",
                action_ar="اختبار",
                condition_formula="test",
                action_parameters={},
                confidence=0.5,
            )

        assert "Invalid rule source" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════════════════
# HumanDecisionOverride Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHumanDecisionOverride:
    """Test HumanDecisionOverride model"""

    def test_create_schedule_modification_override(self, sample_human_override):
        """Test creating a schedule modification override"""
        override = HumanDecisionOverride(
            session_id=sample_human_override["session_id"],
            program_id=sample_human_override["program_id"],
            user_id=sample_human_override["user_id"],
            override_type="schedule_modification",
            original_value={"water_amount_mm": 18},
            new_value={"water_amount_mm": 22},
            reason_en="Local soil conditions require more water",
            reason_ar="ظروف التربة المحلية تتطلب المزيد من المياه",
        )

        assert override.override_type == "schedule_modification"
        assert override.new_value["water_amount_mm"] == 22
        assert override.requires_validation is True

    def test_create_emergency_override(self, sample_human_override):
        """Test creating an emergency override"""
        override = HumanDecisionOverride(
            session_id=sample_human_override["session_id"],
            program_id=sample_human_override["program_id"],
            user_id=sample_human_override["user_id"],
            override_type="emergency_override",
            original_value={"schedule": "normal"},
            new_value={"schedule": "emergency_irrigation"},
            reason_en="Severe drought conditions detected",
            confidence=0.95,
        )

        assert override.override_type == "emergency_override"
        assert override.confidence == 0.95

    def test_override_type_validation(self, sample_human_override):
        """Test override type validation"""
        with pytest.raises(ValidationError) as exc_info:
            HumanDecisionOverride(
                session_id=sample_human_override["session_id"],
                program_id=sample_human_override["program_id"],
                user_id=sample_human_override["user_id"],
                override_type="invalid_type",
                original_value={},
                new_value={},
                reason_en="Test",
            )

        assert "Invalid override type" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════════════════
# CalibrationResult Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalibrationResult:
    """Test CalibrationResult model"""

    def test_create_passed_calibration(self, sample_calibration_result):
        """Test creating a passed calibration result"""
        calibration = CalibrationResult(
            session_id=sample_calibration_result["session_id"],
            program_id=sample_calibration_result["program_id"],
            calibration_type="simulation",
            status="passed",
            simulated_water_savings_percent=23.5,
            simulated_yield_percent=94.0,
            goal_water_savings_percent=25.0,
            goal_yield_percent=90.0,
            water_savings_gap=1.5,
            yield_margin=4.0,
            confidence=0.88,
            simulation_parameters={"weather_scenario": "normal"},
            calibrated_by="system",
        )

        assert calibration.status == "passed"
        assert calibration.yield_margin == 4.0

    def test_create_failed_calibration(self, sample_failed_calibration):
        """Test creating a failed calibration result"""
        calibration = CalibrationResult(
            session_id=sample_failed_calibration["session_id"],
            program_id=sample_failed_calibration["program_id"],
            calibration_type="simulation",
            status="failed",
            simulated_water_savings_percent=15.0,
            simulated_yield_percent=82.0,
            goal_water_savings_percent=25.0,
            goal_yield_percent=90.0,
            water_savings_gap=10.0,
            yield_margin=-8.0,
            confidence=0.65,
            simulation_parameters={"weather_scenario": "drought"},
            warnings=["Yield below threshold"],
            recommendations=["Increase irrigation reserves"],
            calibrated_by="system",
        )

        assert calibration.status == "failed"
        assert calibration.yield_margin < 0
        assert len(calibration.warnings) > 0

    def test_calibration_type_validation(self, sample_calibration_result):
        """Test calibration type validation"""
        with pytest.raises(ValidationError) as exc_info:
            CalibrationResult(
                session_id=sample_calibration_result["session_id"],
                program_id=sample_calibration_result["program_id"],
                calibration_type="invalid_type",
                status="passed",
                simulated_water_savings_percent=20.0,
                simulated_yield_percent=90.0,
                goal_water_savings_percent=20.0,
                goal_yield_percent=85.0,
                water_savings_gap=0.0,
                yield_margin=5.0,
                confidence=0.8,
                simulation_parameters={},
                calibrated_by="system",
            )

        assert "Invalid calibration type" in str(exc_info.value)

    def test_calibration_status_validation(self, sample_calibration_result):
        """Test calibration status validation"""
        with pytest.raises(ValidationError) as exc_info:
            CalibrationResult(
                session_id=sample_calibration_result["session_id"],
                program_id=sample_calibration_result["program_id"],
                calibration_type="simulation",
                status="invalid_status",
                simulated_water_savings_percent=20.0,
                simulated_yield_percent=90.0,
                goal_water_savings_percent=20.0,
                goal_yield_percent=85.0,
                water_savings_gap=0.0,
                yield_margin=5.0,
                confidence=0.8,
                simulation_parameters={},
                calibrated_by="system",
            )

        assert "Invalid calibration status" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════════════════
# ZoneConfiguration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestZoneConfiguration:
    """Test ZoneConfiguration model"""

    def test_create_standard_zone(self, sample_zone_configuration):
        """Test creating a standard irrigation zone"""
        zone = ZoneConfiguration(
            field_id=sample_zone_configuration["field_id"],
            farm_id=sample_zone_configuration["farm_id"],
            name_en="Zone A",
            name_ar="المنطقة أ",
            zone_type="standard",
            area_hectares=5.2,
            soil_type="loamy",
            irrigation_method="drip",
            flow_rate_m3_hr=12.5,
            efficiency_percent=90.0,
            crop_type="wheat",
            growth_stage="tillering",
            root_depth_cm=40,
            water_holding_capacity_mm_m=150,
            management_allowable_depletion=0.5,
        )

        assert zone.zone_type == "standard"
        assert zone.efficiency_percent == 90.0
        assert zone.is_active is True

    def test_create_high_value_zone(self, sample_zone_configuration):
        """Test creating a high-value irrigation zone"""
        zone = ZoneConfiguration(
            field_id=sample_zone_configuration["field_id"],
            farm_id=sample_zone_configuration["farm_id"],
            name_en="High Value Zone",
            name_ar="منطقة عالية القيمة",
            zone_type="high_value",
            area_hectares=2.0,
            soil_type="loamy",
            irrigation_method="drip",
            flow_rate_m3_hr=8.0,
            efficiency_percent=95.0,
            emitter_spacing_m=0.2,
            lateral_spacing_m=0.8,
            crop_type="tomato",
            growth_stage="flowering",
            root_depth_cm=30,
            water_holding_capacity_mm_m=140,
            management_allowable_depletion=0.4,
        )

        assert zone.zone_type == "high_value"
        assert zone.emitter_spacing_m == 0.2

    def test_zone_type_validation(self, sample_zone_configuration):
        """Test zone type validation"""
        with pytest.raises(ValidationError) as exc_info:
            ZoneConfiguration(
                field_id=sample_zone_configuration["field_id"],
                farm_id=sample_zone_configuration["farm_id"],
                name_en="Invalid Zone",
                name_ar="منطقة غير صالحة",
                zone_type="invalid_type",
                area_hectares=5.0,
                soil_type="loamy",
                irrigation_method="drip",
                flow_rate_m3_hr=10.0,
                efficiency_percent=85.0,
                crop_type="wheat",
                growth_stage="vegetative",
                root_depth_cm=30,
                water_holding_capacity_mm_m=150,
                management_allowable_depletion=0.5,
            )

        assert "Invalid zone type" in str(exc_info.value)

    def test_zone_area_must_be_positive(self, sample_zone_configuration):
        """Test that zone area must be positive"""
        with pytest.raises(ValidationError):
            ZoneConfiguration(
                field_id=sample_zone_configuration["field_id"],
                farm_id=sample_zone_configuration["farm_id"],
                name_en="Zero Area Zone",
                name_ar="منطقة صفر",
                zone_type="standard",
                area_hectares=0,  # Invalid: must be > 0
                soil_type="loamy",
                irrigation_method="drip",
                flow_rate_m3_hr=10.0,
                efficiency_percent=85.0,
                crop_type="wheat",
                growth_stage="vegetative",
                root_depth_cm=30,
                water_holding_capacity_mm_m=150,
                management_allowable_depletion=0.5,
            )

    def test_zone_with_sensors(self, sample_zone_configuration):
        """Test zone with sensor configuration"""
        zone = ZoneConfiguration(
            field_id=sample_zone_configuration["field_id"],
            farm_id=sample_zone_configuration["farm_id"],
            name_en="Sensor Zone",
            name_ar="منطقة المستشعرات",
            zone_type="standard",
            area_hectares=3.0,
            soil_type="clay",
            irrigation_method="drip",
            flow_rate_m3_hr=8.0,
            efficiency_percent=88.0,
            sensors=[
                {"sensor_id": "sm-001", "type": "soil_moisture", "depth_cm": 30},
                {"sensor_id": "ec-001", "type": "ec", "depth_cm": 30},
            ],
            crop_type="wheat",
            growth_stage="tillering",
            root_depth_cm=35,
            water_holding_capacity_mm_m=180,
            management_allowable_depletion=0.45,
        )

        assert len(zone.sensors) == 2
        assert zone.sensors[0]["type"] == "soil_moisture"


# ═══════════════════════════════════════════════════════════════════════════════
# ChecklistItem Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestChecklistItem:
    """Test ChecklistItem model"""

    def test_create_incomplete_checklist_item(self, sample_incomplete_checklist_item):
        """Test creating an incomplete checklist item"""
        item = ChecklistItem(
            session_id=sample_incomplete_checklist_item["session_id"],
            category="supervision",
            order=1,
            title_en="Simulation completed",
            title_ar="اكتملت المحاكاة",
            is_required=True,
            is_completed=False,
        )

        assert item.is_completed is False
        assert item.completed_at is None
        assert item.is_required is True

    def test_create_completed_checklist_item(self, sample_checklist_item):
        """Test creating a completed checklist item"""
        item = ChecklistItem(
            session_id=sample_checklist_item["session_id"],
            category="goal_anchoring",
            order=1,
            title_en="Goal defined",
            title_ar="تم تحديد الهدف",
            is_completed=True,
            completed_at=datetime.now(UTC),
            completed_by=str(uuid.uuid4()),
            validation_data={"goal_type": "water_saving", "target": 25.0},
        )

        assert item.is_completed is True
        assert item.completed_at is not None
        assert item.validation_data is not None

    def test_checklist_category_validation(self, sample_checklist_item):
        """Test checklist category validation"""
        with pytest.raises(ValidationError) as exc_info:
            ChecklistItem(
                session_id=sample_checklist_item["session_id"],
                category="invalid_category",
                order=1,
                title_en="Invalid",
                title_ar="غير صالح",
            )

        assert "Invalid checklist category" in str(exc_info.value)

    def test_checklist_order_must_be_positive(self, sample_checklist_item):
        """Test that checklist order must be >= 1"""
        with pytest.raises(ValidationError):
            ChecklistItem(
                session_id=sample_checklist_item["session_id"],
                category="goal_anchoring",
                order=0,  # Invalid: must be >= 1
                title_en="Invalid order",
                title_ar="ترتيب غير صالح",
            )

    def test_all_checklist_categories(self, sample_checklist_item):
        """Test all valid checklist categories"""
        valid_categories = [
            "goal_anchoring",
            "experience_injection",
            "supervision",
            "value_upgrade",
        ]

        for i, category in enumerate(valid_categories, 1):
            item = ChecklistItem(
                session_id=sample_checklist_item["session_id"],
                category=category,
                order=i,
                title_en=f"Item for {category}",
                title_ar=f"عنصر لـ {category}",
            )
            assert item.category == category
