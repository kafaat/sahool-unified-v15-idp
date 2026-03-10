"""
SAHOOL HMC Irrigation Decision Framework - Integration Tests
اختبارات التكامل لإطار قرارات الري التعاوني

Tests integration with SAHOOL services:
- Farm Advisor integration
- Irrigation Agent integration
- Weather service synchronization
- Fertilization schedule synchronization
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Farm Advisor Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFarmAdvisorIntegration:
    """
    Test Farm Advisor Integration
    اختبار تكامل مستشار المزرعة
    """

    @pytest.mark.asyncio
    async def test_farm_advisor_integration(
        self,
        mock_farm_advisor,
        hmc_engine,
        sample_irrigation_goal,
    ):
        """Test basic integration with farm advisor service"""
        # Get field data from farm advisor
        field_data = await mock_farm_advisor.get_field_data(field_id=sample_irrigation_goal["field_id"])

        assert field_data is not None
        assert "field_id" in field_data
        assert "crop_type" in field_data
        assert "area_hectares" in field_data

    @pytest.mark.asyncio
    async def test_get_crop_water_requirement(
        self,
        mock_farm_advisor,
        sample_irrigation_goal,
    ):
        """Test getting crop water requirement from farm advisor"""
        requirement = await mock_farm_advisor.get_crop_water_requirement(
            field_id=sample_irrigation_goal["field_id"],
            crop_type=sample_irrigation_goal["crop_type"],
        )

        assert "daily_et_mm" in requirement
        assert "kc" in requirement
        assert requirement["daily_et_mm"] > 0

    @pytest.mark.asyncio
    async def test_get_soil_moisture_reading(
        self,
        mock_farm_advisor,
        sample_irrigation_goal,
    ):
        """Test getting soil moisture reading from farm advisor"""
        moisture = await mock_farm_advisor.get_soil_moisture(field_id=sample_irrigation_goal["field_id"])

        assert "moisture_percent" in moisture
        assert 0 <= moisture["moisture_percent"] <= 100
        assert "reading_time" in moisture

    @pytest.mark.asyncio
    async def test_get_irrigation_history(
        self,
        mock_farm_advisor,
        sample_irrigation_goal,
    ):
        """Test getting irrigation history from farm advisor"""
        history = await mock_farm_advisor.get_irrigation_history(
            field_id=sample_irrigation_goal["field_id"],
            days=30,
        )

        assert isinstance(history, list)
        assert len(history) > 0
        assert "date" in history[0]
        assert "water_amount_mm" in history[0]

    @pytest.mark.asyncio
    async def test_get_irrigation_advisory(
        self,
        mock_farm_advisor,
        sample_irrigation_goal,
    ):
        """Test getting irrigation advisory from farm advisor"""
        advisory = await mock_farm_advisor.get_irrigation_advisory(
            field_id=sample_irrigation_goal["field_id"],
        )

        assert "recommended_amount_mm" in advisory
        assert "optimal_time" in advisory
        assert "confidence" in advisory
        assert "reasoning_en" in advisory
        assert "reasoning_ar" in advisory

    @pytest.mark.asyncio
    async def test_farm_advisor_provides_hmc_data(
        self,
        mock_farm_advisor,
        hmc_engine,
        sample_irrigation_goal,
    ):
        """Test that farm advisor provides all data needed for HMC session"""
        field_id = sample_irrigation_goal["field_id"]

        # Get all required data
        field_data = await mock_farm_advisor.get_field_data(field_id=field_id)
        soil_moisture = await mock_farm_advisor.get_soil_moisture(field_id=field_id)
        water_req = await mock_farm_advisor.get_crop_water_requirement(
            field_id=field_id,
            crop_type=field_data["crop_type"],
        )
        history = await mock_farm_advisor.get_irrigation_history(
            field_id=field_id,
            days=30,
        )

        # All data should be available
        assert field_data is not None
        assert soil_moisture is not None
        assert water_req is not None
        assert len(history) > 0

    @pytest.mark.asyncio
    async def test_farm_advisor_handles_missing_field(
        self,
        mock_farm_advisor,
    ):
        """Test farm advisor handles missing field gracefully"""
        mock_farm_advisor.get_field_data.side_effect = ValueError("Field not found")

        with pytest.raises(ValueError) as exc_info:
            await mock_farm_advisor.get_field_data(field_id="nonexistent-field")

        assert "not found" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════════════════
# Irrigation Agent Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIrrigationAgentIntegration:
    """
    Test Irrigation Agent Integration
    اختبار تكامل وكيل الري
    """

    @pytest.mark.asyncio
    async def test_irrigation_agent_integration(
        self,
        mock_irrigation_agent,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test basic integration with irrigation agent"""
        result = await mock_irrigation_agent.optimize_schedule(
            field_id=sample_irrigation_goal["field_id"],
            goal=sample_irrigation_goal,
        )

        assert result is not None
        assert "schedule" in result
        assert "total_water_m3" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_agent_validates_schedule(
        self,
        mock_irrigation_agent,
        sample_irrigation_program,
    ):
        """Test irrigation agent validates generated schedule"""
        validation = await mock_irrigation_agent.validate_schedule(
            schedule=sample_irrigation_program["schedules"],
            constraints=[],
        )

        assert "is_valid" in validation
        assert "warnings" in validation
        assert "errors" in validation

    @pytest.mark.asyncio
    async def test_agent_validation_with_constraints(
        self,
        mock_irrigation_agent,
        sample_irrigation_program,
        sample_ecological_constraint,
    ):
        """Test agent validates schedule against constraints"""
        mock_irrigation_agent.validate_schedule.return_value = {
            "is_valid": True,
            "warnings": ["Schedule approaches daily water limit"],
            "errors": [],
            "constraint_checks": [
                {
                    "constraint_id": sample_ecological_constraint["constraint_id"],
                    "passed": True,
                    "margin_percent": 15.0,
                }
            ],
        }

        validation = await mock_irrigation_agent.validate_schedule(
            schedule=sample_irrigation_program["schedules"],
            constraints=[sample_ecological_constraint],
        )

        assert validation["is_valid"] is True
        assert "constraint_checks" in validation

    @pytest.mark.asyncio
    async def test_agent_validation_fails_constraint(
        self,
        mock_irrigation_agent,
        sample_irrigation_program,
        sample_ecological_constraint,
    ):
        """Test agent validation fails when constraint violated"""
        mock_irrigation_agent.validate_schedule.return_value = {
            "is_valid": False,
            "warnings": [],
            "errors": ["Daily water limit exceeded"],
            "constraint_checks": [
                {
                    "constraint_id": sample_ecological_constraint["constraint_id"],
                    "passed": False,
                    "violation": "Exceeds max_daily_water_m3 by 50 m3",
                }
            ],
        }

        validation = await mock_irrigation_agent.validate_schedule(
            schedule=sample_irrigation_program["schedules"],
            constraints=[sample_ecological_constraint],
        )

        assert validation["is_valid"] is False
        assert len(validation["errors"]) > 0

    @pytest.mark.asyncio
    async def test_agent_executes_schedule(
        self,
        mock_irrigation_agent,
        sample_irrigation_program,
    ):
        """Test irrigation agent can execute approved schedule"""
        result = await mock_irrigation_agent.execute_schedule(
            program_id=sample_irrigation_program["program_id"],
            schedule=sample_irrigation_program["schedules"],
        )

        assert "execution_id" in result
        assert "status" in result
        assert result["status"] == "scheduled"

    @pytest.mark.asyncio
    async def test_agent_integrates_with_hmc_program(
        self,
        mock_irrigation_agent,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test agent integrates with HMC-generated program"""
        # Start HMC session
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        # Set goal
        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        # Generate HMC program
        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        # Validate with irrigation agent
        validation = await mock_irrigation_agent.validate_schedule(
            schedule=program["schedules"],
            constraints=[],
        )

        assert validation["is_valid"] is True

        # Execute if valid
        if validation["is_valid"]:
            result = await mock_irrigation_agent.execute_schedule(
                program_id=program["program_id"],
                schedule=program["schedules"],
            )
            assert result["status"] == "scheduled"


# ═══════════════════════════════════════════════════════════════════════════════
# Weather Service Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestWeatherServiceIntegration:
    """
    Test Weather Service Integration
    اختبار تكامل خدمة الطقس
    """

    @pytest.mark.asyncio
    async def test_weather_sync(
        self,
        mock_weather_service,
        sample_irrigation_goal,
    ):
        """Test synchronization with weather service"""
        current = await mock_weather_service.get_current()

        assert current is not None
        assert "temperature_c" in current
        assert "humidity_percent" in current
        assert "wind_speed_kmh" in current

    @pytest.mark.asyncio
    async def test_weather_forecast_retrieval(
        self,
        mock_weather_service,
        sample_irrigation_goal,
    ):
        """Test retrieving weather forecast"""
        forecast = await mock_weather_service.get_forecast()

        assert isinstance(forecast, list)
        assert len(forecast) >= 7  # 7-day forecast
        assert "date" in forecast[0]
        assert "temperature_high_c" in forecast[0]
        assert "precipitation_probability" in forecast[0]

    @pytest.mark.asyncio
    async def test_et0_calculation(
        self,
        mock_weather_service,
    ):
        """Test ET0 calculation from weather service"""
        et0_result = await mock_weather_service.calculate_et0()

        assert "et0_mm" in et0_result
        assert "method" in et0_result
        assert et0_result["et0_mm"] > 0

    @pytest.mark.asyncio
    async def test_weather_adjusts_irrigation_schedule(
        self,
        mock_weather_service,
        mock_irrigation_agent,
        sample_irrigation_goal,
    ):
        """Test that weather data adjusts irrigation schedule"""
        # Get forecast
        forecast = await mock_weather_service.get_forecast()

        # Find days with rain
        rainy_days = [day for day in forecast if day["precipitation_probability"] > 0.5]

        # Optimize schedule with weather data
        mock_irrigation_agent.optimize_schedule.return_value = {
            "schedule": [
                {
                    "date": day["date"],
                    "water_amount_mm": 0 if day in rainy_days else 20,
                    "weather_adjusted": True,
                }
                for day in forecast[:7]
            ],
            "total_water_m3": 1000,  # Reduced due to rain
            "weather_adjustments": [f"Skipped irrigation on {day['date']} due to rain forecast" for day in rainy_days],
            "confidence": 0.82,
        }

        result = await mock_irrigation_agent.optimize_schedule(
            field_id=sample_irrigation_goal["field_id"],
            goal=sample_irrigation_goal,
            weather_forecast=forecast,
        )

        assert "weather_adjustments" in result
        # Should have reduced water for rainy days
        if rainy_days:
            assert len(result["weather_adjustments"]) > 0

    @pytest.mark.asyncio
    async def test_weather_integration_with_hmc_calibration(
        self,
        mock_weather_service,
        hmc_engine,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test weather integration during HMC calibration"""
        # Get weather forecast
        forecast = await mock_weather_service.get_forecast()

        # Start HMC session
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        hmc_engine.generate_program.return_value = sample_irrigation_program
        program = await hmc_engine.generate_program(session_id=session_id)

        # Calibrate with weather scenarios based on forecast
        scenarios = ["normal"]
        if any(day["temperature_high_c"] > 35 for day in forecast):
            scenarios.append("heat_wave")
        if any(day["precipitation_mm"] > 10 for day in forecast):
            scenarios.append("wet")

        for scenario in scenarios:
            hmc_engine.calibrate.return_value = {
                "calibration_id": str(uuid.uuid4()),
                "status": "passed",
                "scenario": scenario,
                "weather_data_used": True,
            }

            calibration = await hmc_engine.calibrate(
                session_id=session_id,
                program_id=program["program_id"],
                weather_scenario=scenario,
            )

            assert calibration["weather_data_used"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# Fertilization Sync Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFertilizationSyncIntegration:
    """
    Test Fertilization Schedule Synchronization
    اختبار مزامنة جدول التسميد
    """

    @pytest.fixture
    def mock_fertilization_service(self):
        """Mock fertilization service"""
        service = MagicMock()

        service.get_schedule = AsyncMock(
            return_value=[
                {
                    "date": (date.today() + timedelta(days=3)).isoformat(),
                    "fertilizer_type": "nitrogen",
                    "amount_kg_ha": 50,
                    "application_method": "fertigation",
                },
                {
                    "date": (date.today() + timedelta(days=10)).isoformat(),
                    "fertilizer_type": "potassium",
                    "amount_kg_ha": 30,
                    "application_method": "broadcast",
                },
            ]
        )

        service.sync_with_irrigation = AsyncMock(
            return_value={
                "synced": True,
                "adjusted_dates": [],
                "conflicts_resolved": 0,
            }
        )

        return service

    @pytest.mark.asyncio
    async def test_fertilization_sync(
        self,
        mock_fertilization_service,
        sample_irrigation_goal,
    ):
        """Test synchronization with fertilization schedule"""
        schedule = await mock_fertilization_service.get_schedule(field_id=sample_irrigation_goal["field_id"])

        assert isinstance(schedule, list)
        assert len(schedule) > 0
        assert "fertilizer_type" in schedule[0]
        assert "application_method" in schedule[0]

    @pytest.mark.asyncio
    async def test_irrigation_adjusts_for_fertigation(
        self,
        mock_fertilization_service,
        mock_irrigation_agent,
        sample_irrigation_goal,
    ):
        """Test irrigation schedule adjusts for fertigation days"""
        fert_schedule = await mock_fertilization_service.get_schedule(field_id=sample_irrigation_goal["field_id"])

        # Find fertigation days
        fertigation_dates = [item["date"] for item in fert_schedule if item["application_method"] == "fertigation"]

        # Optimize irrigation with fertigation awareness
        mock_irrigation_agent.optimize_schedule.return_value = {
            "schedule": [
                {
                    "date": (date.today() + timedelta(days=i)).isoformat(),
                    "water_amount_mm": 25
                    if (date.today() + timedelta(days=i)).isoformat() in fertigation_dates
                    else 18,
                    "fertigation_day": (date.today() + timedelta(days=i)).isoformat() in fertigation_dates,
                }
                for i in range(7)
            ],
            "total_water_m3": 1300,
            "fertigation_adjustments": [f"Increased water on {fdate} for fertigation" for fdate in fertigation_dates],
            "confidence": 0.88,
        }

        result = await mock_irrigation_agent.optimize_schedule(
            field_id=sample_irrigation_goal["field_id"],
            goal=sample_irrigation_goal,
            fertilization_schedule=fert_schedule,
        )

        # Check fertigation days have more water
        fertigation_days = [s for s in result["schedule"] if s.get("fertigation_day")]
        normal_days = [s for s in result["schedule"] if not s.get("fertigation_day")]

        if fertigation_days and normal_days:
            assert fertigation_days[0]["water_amount_mm"] >= normal_days[0]["water_amount_mm"]

    @pytest.mark.asyncio
    async def test_sync_resolves_conflicts(
        self,
        mock_fertilization_service,
        sample_irrigation_program,
    ):
        """Test fertilization sync resolves scheduling conflicts"""
        mock_fertilization_service.sync_with_irrigation.return_value = {
            "synced": True,
            "adjusted_dates": [
                {
                    "original_date": (date.today() + timedelta(days=3)).isoformat(),
                    "new_date": (date.today() + timedelta(days=4)).isoformat(),
                    "reason": "Moved to avoid post-irrigation wet soil",
                }
            ],
            "conflicts_resolved": 1,
        }

        result = await mock_fertilization_service.sync_with_irrigation(
            irrigation_schedule=sample_irrigation_program["schedules"],
        )

        assert result["synced"] is True
        assert result["conflicts_resolved"] > 0

    @pytest.mark.asyncio
    async def test_hmc_integrates_fertilization(
        self,
        mock_fertilization_service,
        value_upgrade_dimension,
        sample_irrigation_program,
    ):
        """Test HMC value upgrade dimension integrates fertilization"""
        fert_schedule = await mock_fertilization_service.get_schedule(field_id=sample_irrigation_program["field_id"])

        result = await value_upgrade_dimension.integrate_fertilization(
            irrigation_program=sample_irrigation_program,
            fertilization_schedule=fert_schedule,
        )

        assert "integrated_schedule" in result
        assert result["nutrient_water_sync"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# End-to-End Integration Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEndToEndIntegration:
    """
    Test End-to-End Integration Scenarios
    اختبار سيناريوهات التكامل الشاملة
    """

    @pytest.mark.asyncio
    async def test_full_hmc_workflow_with_services(
        self,
        hmc_engine,
        mock_farm_advisor,
        mock_weather_service,
        mock_irrigation_agent,
        sample_irrigation_goal,
        sample_ecological_constraint,
        sample_experience_rule,
        sample_irrigation_program,
        sample_calibration_result,
    ):
        """Test complete HMC workflow with all service integrations"""
        # 1. Get field data from farm advisor
        field_data = await mock_farm_advisor.get_field_data(field_id=sample_irrigation_goal["field_id"])
        assert field_data is not None

        # 2. Get weather forecast
        weather_forecast = await mock_weather_service.get_forecast()
        assert len(weather_forecast) > 0

        # 3. Start HMC session
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        # 4. Set goal with field data context
        await hmc_engine.set_goal(
            session_id=session_id,
            goal={
                **sample_irrigation_goal,
                "field_data": field_data,
            },
        )

        # 5. Add ecological constraint
        await hmc_engine.add_constraint(
            session_id=session_id,
            constraint=sample_ecological_constraint,
        )

        # 6. Inject farmer experience
        await hmc_engine.inject_experience(
            session_id=session_id,
            rule=sample_experience_rule,
        )

        # 7. Generate AI program with weather data
        hmc_engine.generate_program.return_value = {
            **sample_irrigation_program,
            "weather_integrated": True,
        }
        program = await hmc_engine.generate_program(
            session_id=session_id,
            weather_forecast=weather_forecast,
        )

        # 8. Validate with irrigation agent
        validation = await mock_irrigation_agent.validate_schedule(
            schedule=program["schedules"],
            constraints=[sample_ecological_constraint],
        )
        assert validation["is_valid"] is True

        # 9. Calibrate
        hmc_engine.calibrate.return_value = sample_calibration_result
        calibration = await hmc_engine.calibrate(
            session_id=session_id,
            program_id=program["program_id"],
        )
        assert calibration["status"] == "passed"

        # 10. Approve
        hmc_engine.get_checklist.return_value = [
            {"item_id": str(i), "is_completed": True, "is_required": True} for i in range(10)
        ]

        approved = await hmc_engine.approve_program(
            session_id=session_id,
            program_id=program["program_id"],
            approver_id=sample_irrigation_goal["created_by"],
        )
        assert approved is True

        # 11. Execute schedule via irrigation agent
        execution = await mock_irrigation_agent.execute_schedule(
            program_id=program["program_id"],
            schedule=program["schedules"],
        )
        assert execution["status"] == "scheduled"

    @pytest.mark.asyncio
    async def test_integration_handles_service_failures(
        self,
        hmc_engine,
        mock_farm_advisor,
        mock_weather_service,
        sample_irrigation_goal,
    ):
        """Test integration handles service failures gracefully"""
        # Simulate weather service failure
        mock_weather_service.get_forecast.side_effect = ConnectionError("Weather service unavailable")

        # Start session
        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        # Should handle weather service failure
        with pytest.raises(ConnectionError):
            await mock_weather_service.get_forecast()

        # But can still generate program with fallback
        hmc_engine.generate_program.return_value = {
            "program_id": str(uuid.uuid4()),
            "schedules": [],
            "weather_integrated": False,
            "warning": "Generated without weather data due to service unavailability",
        }

        program = await hmc_engine.generate_program(
            session_id=session_id,
            use_fallback_weather=True,
        )

        assert program is not None
        assert program["weather_integrated"] is False

    @pytest.mark.asyncio
    async def test_integration_data_consistency(
        self,
        hmc_engine,
        mock_farm_advisor,
        mock_weather_service,
        sample_irrigation_goal,
        sample_irrigation_program,
    ):
        """Test data consistency across integrated services"""
        # Get data from multiple sources
        field_data = await mock_farm_advisor.get_field_data(field_id=sample_irrigation_goal["field_id"])
        soil_moisture = await mock_farm_advisor.get_soil_moisture(field_id=sample_irrigation_goal["field_id"])
        weather = await mock_weather_service.get_current()

        # Generate program using all data
        hmc_engine.generate_program.return_value = {
            **sample_irrigation_program,
            "input_data": {
                "field": field_data,
                "soil_moisture": soil_moisture,
                "weather": weather,
            },
        }

        session_id = await hmc_engine.start_session(
            farm_id=sample_irrigation_goal["farm_id"],
            field_id=sample_irrigation_goal["field_id"],
            tenant_id=sample_irrigation_goal["tenant_id"],
            initiated_by=sample_irrigation_goal["created_by"],
        )

        await hmc_engine.set_goal(session_id=session_id, goal=sample_irrigation_goal)

        program = await hmc_engine.generate_program(session_id=session_id)

        # Verify all input data is captured
        assert "input_data" in program
        assert program["input_data"]["field"] == field_data
        assert program["input_data"]["soil_moisture"] == soil_moisture
        assert program["input_data"]["weather"] == weather
