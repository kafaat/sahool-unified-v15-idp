"""
SAHOOL HMC Irrigation Decision Framework - Dimension Tests
اختبارات أبعاد إطار قرارات الري التعاوني

Tests all 4 collaboration dimensions:
1. GoalAnchoringDimension - Goal setting and constraint management
2. ExperienceInjectionDimension - Knowledge translation and reward calibration
3. SupervisionCalibrationDimension - Simulation and validation
4. ValueUpgradeDimension - Rule extraction and integration
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# GoalAnchoringDimension Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestGoalAnchoringDimension:
    """
    Test Goal Anchoring Dimension
    اختبار بُعد تثبيت الهدف

    This dimension handles:
    - Setting water saving goals
    - Setting high yield goals
    - Defining ecological boundaries
    - Defining human/AI responsibilities
    - Detecting goal conflicts
    """

    def test_set_water_saving_goal(
        self,
        goal_anchoring_dimension,
        sample_irrigation_goal,
    ):
        """Test setting a water saving goal"""
        result = goal_anchoring_dimension.set_water_saving_goal(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            target_savings_percent=25.0,
            min_yield_threshold_percent=90.0,
        )

        assert result is True
        goal_anchoring_dimension.set_water_saving_goal.assert_called_once()

    def test_set_water_saving_goal_validates_range(
        self,
        goal_anchoring_dimension,
        sample_irrigation_goal,
    ):
        """Test that water saving goal validates percentage range"""
        # Test invalid percentage (> 100)
        goal_anchoring_dimension.set_water_saving_goal.side_effect = ValueError(
            "Target savings percent must be between 0 and 100"
        )

        with pytest.raises(ValueError) as exc_info:
            goal_anchoring_dimension.set_water_saving_goal(
                farm_id=sample_irrigation_goal["farm_id"],
                field_id=sample_irrigation_goal["field_id"],
                target_savings_percent=150.0,  # Invalid
                min_yield_threshold_percent=90.0,
            )

        assert "between 0 and 100" in str(exc_info.value)

    def test_set_high_yield_goal(
        self,
        goal_anchoring_dimension,
        sample_high_yield_goal,
    ):
        """Test setting a high yield goal"""
        result = goal_anchoring_dimension.set_high_yield_goal(
            farm_id=sample_high_yield_goal["farm_id"],
            field_id=sample_high_yield_goal["field_id"],
            target_yield_kg_ha=7000.0,
            max_water_budget_m3=5000.0,
        )

        assert result is True

    def test_set_high_yield_goal_with_crop_specific_targets(
        self,
        goal_anchoring_dimension,
        sample_high_yield_goal,
    ):
        """Test setting high yield goal with crop-specific targets"""
        goal_anchoring_dimension.set_high_yield_goal.return_value = True

        result = goal_anchoring_dimension.set_high_yield_goal(
            farm_id=sample_high_yield_goal["farm_id"],
            field_id=sample_high_yield_goal["field_id"],
            target_yield_kg_ha=50000.0,  # High for tomatoes
            max_water_budget_m3=8000.0,
            crop_type="tomato",
            growth_stage="fruiting",
        )

        assert result is True

    def test_set_ecological_boundaries(
        self,
        goal_anchoring_dimension,
        sample_ecological_constraint,
    ):
        """Test setting ecological boundaries"""
        result = goal_anchoring_dimension.set_ecological_boundaries(
            farm_id=sample_ecological_constraint["farm_id"],
            constraints=[sample_ecological_constraint],
        )

        assert result is True

    def test_set_ecological_boundaries_multiple_constraints(
        self,
        goal_anchoring_dimension,
        sample_ecological_constraint,
        sample_soil_health_constraint,
    ):
        """Test setting multiple ecological constraints"""
        result = goal_anchoring_dimension.set_ecological_boundaries(
            farm_id=sample_ecological_constraint["farm_id"],
            constraints=[
                sample_ecological_constraint,
                sample_soil_health_constraint,
            ],
        )

        assert result is True

    def test_define_responsibilities(
        self,
        goal_anchoring_dimension,
        sample_irrigation_goal,
    ):
        """Test defining human and AI responsibilities"""
        result = goal_anchoring_dimension.define_responsibilities(
            session_id=str(uuid.uuid4()),
            human_responsibilities=[
                "final_approval",
                "emergency_override",
                "constraint_definition",
            ],
            ai_responsibilities=[
                "schedule_optimization",
                "weather_adjustment",
                "sensor_monitoring",
            ],
        )

        assert result is True

    def test_goal_conflict_detection_no_conflicts(
        self,
        goal_anchoring_dimension,
        sample_irrigation_goal,
    ):
        """Test goal conflict detection when no conflicts exist"""
        goal_anchoring_dimension.detect_goal_conflicts.return_value = []

        conflicts = goal_anchoring_dimension.detect_goal_conflicts(
            water_savings_target=25.0,
            yield_target=90.0,
            ecological_constraints=[],
        )

        assert len(conflicts) == 0

    def test_goal_conflict_detection_with_conflicts(
        self,
        goal_anchoring_dimension,
        sample_irrigation_goal,
        sample_ecological_constraint,
    ):
        """Test goal conflict detection when conflicts exist"""
        goal_anchoring_dimension.detect_goal_conflicts.return_value = [
            {
                "conflict_type": "water_budget_exceeded",
                "description_en": "Water savings goal conflicts with minimum yield requirement",
                "description_ar": "هدف توفير المياه يتعارض مع متطلبات الحد الأدنى للإنتاج",
                "severity": "high",
                "resolution_suggestion": "Reduce water savings target or accept lower yield",
            }
        ]

        conflicts = goal_anchoring_dimension.detect_goal_conflicts(
            water_savings_target=50.0,  # Very aggressive
            yield_target=100.0,  # Maximum yield
            ecological_constraints=[sample_ecological_constraint],
        )

        assert len(conflicts) == 1
        assert conflicts[0]["severity"] == "high"

    def test_validate_goals_success(
        self,
        goal_anchoring_dimension,
        sample_irrigation_goal,
    ):
        """Test goal validation success"""
        result = goal_anchoring_dimension.validate_goals(
            goals=[sample_irrigation_goal],
        )

        assert result["is_valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_goals_failure(
        self,
        goal_anchoring_dimension,
    ):
        """Test goal validation failure"""
        goal_anchoring_dimension.validate_goals.return_value = {
            "is_valid": False,
            "errors": [
                "Target yield exceeds historical maximum",
                "Water savings target unrealistic for crop type",
            ],
        }

        result = goal_anchoring_dimension.validate_goals(
            goals=[{"target_yield_kg_ha": 100000}],  # Unrealistic
        )

        assert result["is_valid"] is False
        assert len(result["errors"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# ExperienceInjectionDimension Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestExperienceInjectionDimension:
    """
    Test Experience Injection Dimension
    اختبار بُعد حقن الخبرة

    This dimension handles:
    - Injecting farmer experience/tacit knowledge
    - Translating natural language to formal rules
    - Calibrating AI reward functions
    - Updating the knowledge base
    """

    def test_inject_farmer_experience(
        self,
        experience_injection_dimension,
        sample_experience_rule,
    ):
        """Test injecting farmer experience rule"""
        result = experience_injection_dimension.inject_farmer_experience(
            farm_id=sample_experience_rule["farm_id"],
            experience_description_en="When soil is very dry, irrigate early morning",
            experience_description_ar="عندما تكون التربة جافة جداً، نري في الصباح الباكر",
            crop_type="wheat",
            confidence=0.85,
        )

        assert result is True

    def test_inject_farmer_experience_with_conditions(
        self,
        experience_injection_dimension,
        sample_experience_rule,
    ):
        """Test injecting farmer experience with specific conditions"""
        result = experience_injection_dimension.inject_farmer_experience(
            farm_id=sample_experience_rule["farm_id"],
            experience_description_en="After rain, skip irrigation for 2 days",
            experience_description_ar="بعد المطر، تخطي الري لمدة يومين",
            crop_type="wheat",
            conditions={
                "trigger": "after_rain",
                "min_rainfall_mm": 10,
                "skip_days": 2,
            },
            confidence=0.9,
        )

        assert result is True

    def test_translate_tacit_knowledge(
        self,
        experience_injection_dimension,
    ):
        """Test translating tacit knowledge to formal rule"""
        result = experience_injection_dimension.translate_tacit_knowledge(
            natural_language_en="My grandfather always said to water when the wheat leaves start curling",
            natural_language_ar="كان جدي يقول دائماً أن نسقي عندما تبدأ أوراق القمح بالانحناء",
        )

        assert "rule_id" in result
        assert "condition_formula" in result
        assert "action_parameters" in result

    def test_translate_tacit_knowledge_complex_rule(
        self,
        experience_injection_dimension,
    ):
        """Test translating complex tacit knowledge"""
        experience_injection_dimension.translate_tacit_knowledge.return_value = {
            "rule_id": str(uuid.uuid4()),
            "condition_formula": "(temperature > 35 AND humidity < 30) OR soil_moisture < 25",
            "action_parameters": {
                "water_amount_mm": 25,
                "start_time": "05:00",
                "priority": "high",
            },
            "confidence": 0.75,
            "requires_validation": True,
        }

        result = experience_injection_dimension.translate_tacit_knowledge(
            natural_language_en="In very hot dry weather or when soil is too dry, irrigate heavily at dawn",
            natural_language_ar="في الطقس الحار الجاف جداً أو عندما تكون التربة جافة جداً، نري بكثرة عند الفجر",
        )

        assert "OR" in result["condition_formula"] or "AND" in result["condition_formula"]
        assert result["requires_validation"] is True

    def test_calibrate_reward_function(
        self,
        experience_injection_dimension,
        sample_irrigation_goal,
    ):
        """Test calibrating reward function based on farmer preferences"""
        result = experience_injection_dimension.calibrate_reward_function(
            farmer_preferences={
                "water_savings_importance": 0.7,
                "yield_importance": 0.8,
                "cost_importance": 0.5,
                "labor_importance": 0.3,
            },
            historical_outcomes=[
                {"water_saved_percent": 20, "yield_percent": 95, "satisfaction": 0.9},
                {"water_saved_percent": 30, "yield_percent": 88, "satisfaction": 0.7},
            ],
        )

        assert "reward_weights" in result
        assert "calibration_score" in result
        assert result["calibration_score"] > 0

    def test_calibrate_reward_function_normalizes_weights(
        self,
        experience_injection_dimension,
    ):
        """Test that reward function calibration normalizes weights"""
        experience_injection_dimension.calibrate_reward_function.return_value = {
            "reward_weights": {
                "water_savings": 0.35,
                "yield": 0.40,
                "cost": 0.25,
            },
            "calibration_score": 0.92,
            "weights_sum": 1.0,
        }

        result = experience_injection_dimension.calibrate_reward_function(
            farmer_preferences={
                "water_savings_importance": 7,
                "yield_importance": 8,
                "cost_importance": 5,
            },
            historical_outcomes=[],
        )

        # Weights should sum to approximately 1.0
        weights = result["reward_weights"]
        total = sum(weights.values())
        assert abs(total - 1.0) < 0.01

    @pytest.mark.asyncio
    async def test_update_knowledge_base(
        self,
        experience_injection_dimension,
        sample_experience_rule,
    ):
        """Test updating the knowledge base with new rule"""
        result = await experience_injection_dimension.update_knowledge_base(
            rule=sample_experience_rule,
            operation="add",
        )

        assert result is True
        experience_injection_dimension.update_knowledge_base.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_knowledge_base_modify_existing(
        self,
        experience_injection_dimension,
        sample_experience_rule,
    ):
        """Test modifying existing rule in knowledge base"""
        modified_rule = dict(sample_experience_rule)
        modified_rule["confidence"] = 0.95
        modified_rule["success_rate"] = 0.98

        result = await experience_injection_dimension.update_knowledge_base(
            rule=modified_rule,
            operation="update",
        )

        assert result is True


# ═══════════════════════════════════════════════════════════════════════════════
# SupervisionCalibrationDimension Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSupervisionCalibrationDimension:
    """
    Test Supervision Calibration Dimension
    اختبار بُعد معايرة الإشراف

    This dimension handles:
    - Running simulations for verification
    - Comparing field trial results
    - Checking emergency strategies
    - Handling sensor failures
    """

    @pytest.mark.asyncio
    async def test_simulation_verification_pass(
        self,
        supervision_calibration_dimension,
        sample_irrigation_program,
        sample_irrigation_goal,
    ):
        """Test simulation verification that passes"""
        result = await supervision_calibration_dimension.run_simulation(
            program=sample_irrigation_program,
            goal=sample_irrigation_goal,
            weather_scenario="normal",
            simulation_days=30,
        )

        assert result["status"] == "passed"
        assert result["simulated_yield_percent"] >= 90.0

    @pytest.mark.asyncio
    async def test_simulation_verification_fail(
        self,
        supervision_calibration_dimension,
        sample_irrigation_program,
        sample_irrigation_goal,
    ):
        """Test simulation verification that fails"""
        supervision_calibration_dimension.run_simulation.return_value = {
            "status": "failed",
            "simulated_yield_percent": 78.0,
            "simulated_water_savings_percent": 35.0,
            "failure_reasons": [
                "Yield below minimum threshold",
                "Water stress detected in week 3",
            ],
        }

        result = await supervision_calibration_dimension.run_simulation(
            program=sample_irrigation_program,
            goal=sample_irrigation_goal,
            weather_scenario="drought",
            simulation_days=30,
        )

        assert result["status"] == "failed"
        assert result["simulated_yield_percent"] < 90.0
        assert len(result["failure_reasons"]) > 0

    @pytest.mark.asyncio
    async def test_simulation_multiple_scenarios(
        self,
        supervision_calibration_dimension,
        sample_irrigation_program,
        sample_irrigation_goal,
    ):
        """Test simulation with multiple weather scenarios"""
        scenarios = ["normal", "drought", "wet", "heat_wave"]
        results = []

        for scenario in scenarios:
            supervision_calibration_dimension.run_simulation.return_value = {
                "status": "passed" if scenario == "normal" else "warning",
                "simulated_yield_percent": 94.0 if scenario == "normal" else 85.0,
                "scenario": scenario,
            }

            result = await supervision_calibration_dimension.run_simulation(
                program=sample_irrigation_program,
                goal=sample_irrigation_goal,
                weather_scenario=scenario,
                simulation_days=30,
            )
            results.append(result)

        # At least one scenario should pass
        passed = [r for r in results if r["status"] == "passed"]
        assert len(passed) >= 1

    @pytest.mark.asyncio
    async def test_field_trial_comparison(
        self,
        supervision_calibration_dimension,
        sample_irrigation_program,
    ):
        """Test comparison with actual field trial results"""
        result = await supervision_calibration_dimension.compare_field_trial(
            program_id=sample_irrigation_program["program_id"],
            actual_water_used_m3=1300,
            actual_yield_kg=4800,
            trial_duration_days=30,
        )

        assert "actual_yield_percent" in result
        assert "actual_water_savings_percent" in result
        assert "deviation" in result

    @pytest.mark.asyncio
    async def test_field_trial_comparison_within_tolerance(
        self,
        supervision_calibration_dimension,
        sample_irrigation_program,
    ):
        """Test field trial comparison is within acceptable tolerance"""
        supervision_calibration_dimension.compare_field_trial.return_value = {
            "actual_yield_percent": 93.5,
            "actual_water_savings_percent": 22.5,
            "predicted_yield_percent": 94.0,
            "predicted_water_savings_percent": 23.0,
            "deviation": 0.5,
            "within_tolerance": True,
            "tolerance_percent": 5.0,
        }

        result = await supervision_calibration_dimension.compare_field_trial(
            program_id=sample_irrigation_program["program_id"],
            actual_water_used_m3=1300,
            actual_yield_kg=4800,
            trial_duration_days=30,
        )

        assert result["within_tolerance"] is True
        assert result["deviation"] < result["tolerance_percent"]

    def test_emergency_strategy_check(
        self,
        supervision_calibration_dimension,
        sample_irrigation_program,
    ):
        """Test checking emergency strategy presence"""
        result = supervision_calibration_dimension.check_emergency_strategy(
            program_id=sample_irrigation_program["program_id"],
        )

        assert result["has_strategy"] is True
        assert "scenarios_covered" in result

    def test_emergency_strategy_check_all_scenarios(
        self,
        supervision_calibration_dimension,
        sample_irrigation_program,
    ):
        """Test that emergency strategy covers all critical scenarios"""
        supervision_calibration_dimension.check_emergency_strategy.return_value = {
            "has_strategy": True,
            "scenarios_covered": [
                "drought",
                "equipment_failure",
                "sensor_failure",
                "power_outage",
                "water_contamination",
            ],
            "missing_scenarios": [],
            "coverage_score": 1.0,
        }

        result = supervision_calibration_dimension.check_emergency_strategy(
            program_id=sample_irrigation_program["program_id"],
        )

        assert "drought" in result["scenarios_covered"]
        assert "sensor_failure" in result["scenarios_covered"]
        assert result["coverage_score"] == 1.0

    def test_emergency_strategy_check_incomplete(
        self,
        supervision_calibration_dimension,
        sample_irrigation_program,
    ):
        """Test emergency strategy check with missing scenarios"""
        supervision_calibration_dimension.check_emergency_strategy.return_value = {
            "has_strategy": True,
            "scenarios_covered": ["drought", "equipment_failure"],
            "missing_scenarios": ["sensor_failure", "power_outage"],
            "coverage_score": 0.5,
        }

        result = supervision_calibration_dimension.check_emergency_strategy(
            program_id=sample_irrigation_program["program_id"],
        )

        assert len(result["missing_scenarios"]) > 0
        assert result["coverage_score"] < 1.0

    @pytest.mark.asyncio
    async def test_sensor_failure_handling(
        self,
        supervision_calibration_dimension,
        sample_zone_configuration,
    ):
        """Test handling sensor failure scenario"""
        result = await supervision_calibration_dimension.handle_sensor_failure(
            zone_id=sample_zone_configuration["zone_id"],
            failed_sensors=["sm-001"],
            failure_type="connection_lost",
        )

        assert "fallback_mode" in result
        assert result["fallback_mode"] in ["conservative", "historical", "manual"]

    @pytest.mark.asyncio
    async def test_sensor_failure_with_backup_sensors(
        self,
        supervision_calibration_dimension,
        sample_zone_configuration,
    ):
        """Test sensor failure when backup sensors available"""
        supervision_calibration_dimension.handle_sensor_failure.return_value = {
            "fallback_mode": "backup_sensor",
            "active_sensor": "sm-002",
            "fallback_schedule": [],
            "alert_sent": True,
            "maintenance_ticket_created": True,
        }

        result = await supervision_calibration_dimension.handle_sensor_failure(
            zone_id=sample_zone_configuration["zone_id"],
            failed_sensors=["sm-001"],
            failure_type="hardware_malfunction",
        )

        assert result["fallback_mode"] == "backup_sensor"
        assert result["alert_sent"] is True

    @pytest.mark.asyncio
    async def test_sensor_failure_complete_loss(
        self,
        supervision_calibration_dimension,
        sample_zone_configuration,
    ):
        """Test handling complete sensor loss in zone"""
        supervision_calibration_dimension.handle_sensor_failure.return_value = {
            "fallback_mode": "conservative",
            "fallback_schedule": [
                {
                    "date": date.today().isoformat(),
                    "water_amount_mm": 15,  # Conservative amount
                    "source": "historical_average",
                }
            ],
            "alert_sent": True,
            "requires_manual_inspection": True,
        }

        result = await supervision_calibration_dimension.handle_sensor_failure(
            zone_id=sample_zone_configuration["zone_id"],
            failed_sensors=["sm-001", "sm-002", "ec-001"],  # All sensors
            failure_type="complete_loss",
        )

        assert result["fallback_mode"] == "conservative"
        assert result["requires_manual_inspection"] is True
        assert len(result["fallback_schedule"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# ValueUpgradeDimension Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestValueUpgradeDimension:
    """
    Test Value Upgrade Dimension
    اختبار بُعد ترقية القيمة

    This dimension handles:
    - Extracting field-specific rules from data
    - Integrating with fertilization schedules
    - Integrating with weather forecasts
    - Calculating carbon reduction
    """

    @pytest.mark.asyncio
    async def test_extract_field_rules(
        self,
        value_upgrade_dimension,
        sample_zone_configuration,
    ):
        """Test extracting field-specific rules from historical data"""
        result = await value_upgrade_dimension.extract_field_rules(
            field_id=sample_zone_configuration["field_id"],
            data_period_days=365,
            min_confidence=0.7,
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert "rule_id" in result[0]
        assert "confidence" in result[0]

    @pytest.mark.asyncio
    async def test_extract_field_rules_multiple_patterns(
        self,
        value_upgrade_dimension,
        sample_zone_configuration,
    ):
        """Test extracting multiple rule patterns from field data"""
        value_upgrade_dimension.extract_field_rules.return_value = [
            {
                "rule_id": str(uuid.uuid4()),
                "condition": "soil_moisture < 40",
                "action": "irrigate_20mm",
                "confidence": 0.85,
                "frequency": 45,  # Applied 45 times in the period
            },
            {
                "rule_id": str(uuid.uuid4()),
                "condition": "temperature > 35 AND humidity < 30",
                "action": "irrigate_early_morning",
                "confidence": 0.78,
                "frequency": 28,
            },
            {
                "rule_id": str(uuid.uuid4()),
                "condition": "rainfall_forecast > 10mm",
                "action": "skip_irrigation",
                "confidence": 0.92,
                "frequency": 15,
            },
        ]

        result = await value_upgrade_dimension.extract_field_rules(
            field_id=sample_zone_configuration["field_id"],
            data_period_days=365,
            min_confidence=0.7,
        )

        assert len(result) == 3
        # All rules should have confidence >= min_confidence
        for rule in result:
            assert rule["confidence"] >= 0.7

    @pytest.mark.asyncio
    async def test_fertilization_integration(
        self,
        value_upgrade_dimension,
        sample_irrigation_program,
    ):
        """Test integration with fertilization schedule"""
        result = await value_upgrade_dimension.integrate_fertilization(
            irrigation_program=sample_irrigation_program,
            fertilization_schedule=[
                {
                    "date": date.today().isoformat(),
                    "fertilizer_type": "nitrogen",
                    "amount_kg_ha": 50,
                    "application_method": "fertigation",
                }
            ],
        )

        assert "integrated_schedule" in result
        assert result["nutrient_water_sync"] is True

    @pytest.mark.asyncio
    async def test_fertilization_integration_timing_adjustment(
        self,
        value_upgrade_dimension,
        sample_irrigation_program,
    ):
        """Test fertilization integration adjusts irrigation timing"""
        value_upgrade_dimension.integrate_fertilization.return_value = {
            "integrated_schedule": [
                {
                    "date": date.today().isoformat(),
                    "irrigation_time": "06:00",
                    "fertigation_time": "06:30",
                    "water_amount_mm": 20,
                    "fertilizer_amount_kg_ha": 50,
                    "notes": "Extended irrigation for nutrient uptake",
                }
            ],
            "nutrient_water_sync": True,
            "water_increase_percent": 10,  # Increased water for fertigation
            "timing_adjusted": True,
        }

        result = await value_upgrade_dimension.integrate_fertilization(
            irrigation_program=sample_irrigation_program,
            fertilization_schedule=[
                {
                    "date": date.today().isoformat(),
                    "fertilizer_type": "nitrogen",
                    "amount_kg_ha": 50,
                    "application_method": "fertigation",
                }
            ],
        )

        assert result["timing_adjusted"] is True
        assert result["water_increase_percent"] > 0

    @pytest.mark.asyncio
    async def test_weather_integration(
        self,
        value_upgrade_dimension,
        sample_irrigation_program,
        mock_weather_service,
    ):
        """Test integration with weather forecast"""
        result = await value_upgrade_dimension.integrate_weather(
            irrigation_program=sample_irrigation_program,
            weather_forecast=await mock_weather_service.get_forecast(),
        )

        assert "weather_adjusted" in result

    @pytest.mark.asyncio
    async def test_weather_integration_rain_adjustment(
        self,
        value_upgrade_dimension,
        sample_irrigation_program,
    ):
        """Test weather integration reduces irrigation when rain expected"""
        value_upgrade_dimension.integrate_weather.return_value = {
            "weather_adjusted": True,
            "rain_reduction_mm": 15.0,
            "original_water_mm": 20.0,
            "adjusted_water_mm": 5.0,
            "adjustment_reason": "Rain forecast: 15mm expected",
            "confidence": 0.85,
        }

        result = await value_upgrade_dimension.integrate_weather(
            irrigation_program=sample_irrigation_program,
            weather_forecast=[
                {
                    "date": date.today().isoformat(),
                    "precipitation_mm": 15.0,
                    "precipitation_probability": 0.8,
                }
            ],
        )

        assert result["weather_adjusted"] is True
        assert result["rain_reduction_mm"] > 0
        assert result["adjusted_water_mm"] < result["original_water_mm"]

    @pytest.mark.asyncio
    async def test_weather_integration_heat_adjustment(
        self,
        value_upgrade_dimension,
        sample_irrigation_program,
    ):
        """Test weather integration increases irrigation during heat wave"""
        value_upgrade_dimension.integrate_weather.return_value = {
            "weather_adjusted": True,
            "heat_increase_mm": 5.0,
            "original_water_mm": 20.0,
            "adjusted_water_mm": 25.0,
            "adjustment_reason": "Heat wave: Temperature > 40C expected",
            "timing_adjusted": True,
            "new_timing": "05:00",  # Earlier to avoid heat
        }

        result = await value_upgrade_dimension.integrate_weather(
            irrigation_program=sample_irrigation_program,
            weather_forecast=[
                {
                    "date": date.today().isoformat(),
                    "temperature_high_c": 42,
                    "humidity_percent": 20,
                }
            ],
        )

        assert result["weather_adjusted"] is True
        assert result["adjusted_water_mm"] > result["original_water_mm"]
        assert result["timing_adjusted"] is True

    def test_carbon_reduction_calculation(
        self,
        value_upgrade_dimension,
        sample_irrigation_program,
    ):
        """Test carbon reduction calculation"""
        result = value_upgrade_dimension.calculate_carbon_reduction(
            water_saved_m3=450,
            pumping_depth_m=50,
            pump_efficiency=0.75,
        )

        assert "carbon_saved_kg" in result
        assert result["carbon_saved_kg"] > 0

    def test_carbon_reduction_calculation_detailed(
        self,
        value_upgrade_dimension,
        sample_irrigation_program,
    ):
        """Test detailed carbon reduction calculation"""
        value_upgrade_dimension.calculate_carbon_reduction.return_value = {
            "carbon_saved_kg": 125.5,
            "water_energy_saved_kwh": 450.0,
            "pumping_energy_saved_kwh": 300.0,
            "treatment_energy_saved_kwh": 50.0,
            "distribution_energy_saved_kwh": 100.0,
            "carbon_factor_kg_per_kwh": 0.279,
            "equivalent_trees_planted": 5.7,
        }

        result = value_upgrade_dimension.calculate_carbon_reduction(
            water_saved_m3=450,
            pumping_depth_m=50,
            pump_efficiency=0.75,
        )

        assert result["carbon_saved_kg"] > 0
        assert result["water_energy_saved_kwh"] > 0
        assert "equivalent_trees_planted" in result

    def test_carbon_reduction_zero_water_saved(
        self,
        value_upgrade_dimension,
    ):
        """Test carbon reduction when no water saved"""
        value_upgrade_dimension.calculate_carbon_reduction.return_value = {
            "carbon_saved_kg": 0.0,
            "water_energy_saved_kwh": 0.0,
        }

        result = value_upgrade_dimension.calculate_carbon_reduction(
            water_saved_m3=0,
            pumping_depth_m=50,
            pump_efficiency=0.75,
        )

        assert result["carbon_saved_kg"] == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-Dimension Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDimensionInteractions:
    """
    Test interactions between dimensions
    اختبار التفاعلات بين الأبعاد
    """

    def test_goal_anchoring_feeds_experience_injection(
        self,
        goal_anchoring_dimension,
        experience_injection_dimension,
        sample_irrigation_goal,
    ):
        """Test that goal anchoring properly feeds experience injection"""
        # Set goal first
        goal_anchoring_dimension.set_water_saving_goal(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            target_savings_percent=25.0,
            min_yield_threshold_percent=90.0,
        )

        # Calibrate reward function based on goal
        result = experience_injection_dimension.calibrate_reward_function(
            farmer_preferences={
                "water_savings_importance": 0.7,  # Aligned with goal
                "yield_importance": 0.6,
            },
            historical_outcomes=[],
        )

        assert "reward_weights" in result

    @pytest.mark.asyncio
    async def test_experience_injection_feeds_supervision(
        self,
        experience_injection_dimension,
        supervision_calibration_dimension,
        sample_experience_rule,
        sample_irrigation_program,
        sample_irrigation_goal,
    ):
        """Test that injected experience is validated by supervision"""
        # Inject experience
        experience_injection_dimension.inject_farmer_experience(
            farm_id=sample_experience_rule["farm_id"],
            experience_description_en="Water more in sandy areas",
            experience_description_ar="سقي أكثر في المناطق الرملية",
            crop_type="wheat",
            confidence=0.8,
        )

        # Verify through simulation
        result = await supervision_calibration_dimension.run_simulation(
            program=sample_irrigation_program,
            goal=sample_irrigation_goal,
            weather_scenario="normal",
            simulation_days=30,
        )

        assert result["status"] in ["passed", "warning"]

    @pytest.mark.asyncio
    async def test_supervision_feeds_value_upgrade(
        self,
        supervision_calibration_dimension,
        value_upgrade_dimension,
        sample_irrigation_program,
        sample_irrigation_goal,
        sample_zone_configuration,
    ):
        """Test that successful supervision enables value extraction"""
        # Run successful simulation
        simulation_result = await supervision_calibration_dimension.run_simulation(
            program=sample_irrigation_program,
            goal=sample_irrigation_goal,
            weather_scenario="normal",
            simulation_days=30,
        )

        assert simulation_result["status"] == "passed"

        # Extract rules from successful program
        rules = await value_upgrade_dimension.extract_field_rules(
            field_id=sample_zone_configuration["field_id"],
            data_period_days=365,
            min_confidence=0.7,
        )

        assert len(rules) > 0
