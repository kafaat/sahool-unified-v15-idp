"""
SAHOOL HMC Irrigation Decision Framework - Test Fixtures
تجهيزات اختبار إطار قرارات الري التعاوني

Provides fixtures for:
- sample_irrigation_goal
- sample_ecological_constraint
- sample_experience_rule
- sample_irrigation_program
- hmc_engine instance
- mock_farm_advisor
- mock_weather_service
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator, Generator
from datetime import UTC, date, datetime, timedelta
from enum import Enum, StrEnum
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Enums for Testing
# ═══════════════════════════════════════════════════════════════════════════════


class GoalPriority(StrEnum):
    """Irrigation goal priority levels"""

    WATER_SAVING = "water_saving"
    HIGH_YIELD = "high_yield"
    BALANCED = "balanced"
    ECOLOGICAL = "ecological"


class ConstraintType(StrEnum):
    """Types of ecological constraints"""

    WATER_LIMIT = "water_limit"
    GROUNDWATER_PROTECTION = "groundwater_protection"
    SOIL_HEALTH = "soil_health"
    BIODIVERSITY = "biodiversity"
    CARBON_FOOTPRINT = "carbon_footprint"


class RuleSource(StrEnum):
    """Source of experience rules"""

    FARMER = "farmer"
    AI = "ai"
    AGRONOMIST = "agronomist"
    HISTORICAL = "historical"


class SessionStatus(StrEnum):
    """HMC session status"""

    PENDING = "pending"
    GOAL_SETTING = "goal_setting"
    AI_GENERATION = "ai_generation"
    HUMAN_REVIEW = "human_review"
    CALIBRATION = "calibration"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class ChecklistCategory(StrEnum):
    """Checklist item categories"""

    GOAL_ANCHORING = "goal_anchoring"
    EXPERIENCE_INJECTION = "experience_injection"
    SUPERVISION = "supervision"
    VALUE_UPGRADE = "value_upgrade"


class ZoneType(StrEnum):
    """Irrigation zone types"""

    HIGH_VALUE = "high_value"
    STANDARD = "standard"
    WATER_SCARCE = "water_scarce"
    SENSITIVE = "sensitive"


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Irrigation Goal Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_irrigation_goal() -> dict[str, Any]:
    """
    Sample irrigation goal for testing
    هدف ري نموذجي للاختبار
    """
    return {
        "goal_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "priority": GoalPriority.WATER_SAVING.value,
        "target_water_savings_percent": 25.0,
        "target_yield_kg_ha": 5000.0,
        "min_yield_threshold_percent": 90.0,
        "season": "winter",
        "crop_type": "wheat",
        "description_en": "Reduce water usage by 25% while maintaining 90% yield",
        "description_ar": "تقليل استخدام المياه بنسبة 25% مع الحفاظ على 90% من الإنتاج",
        "created_by": str(uuid.uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "valid_from": date.today().isoformat(),
        "valid_until": (date.today() + timedelta(days=120)).isoformat(),
        "is_active": True,
    }


@pytest.fixture
def sample_high_yield_goal() -> dict[str, Any]:
    """
    Sample high yield goal for testing
    هدف إنتاج عالي نموذجي للاختبار
    """
    return {
        "goal_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "priority": GoalPriority.HIGH_YIELD.value,
        "target_water_savings_percent": 10.0,
        "target_yield_kg_ha": 7000.0,
        "min_yield_threshold_percent": 100.0,
        "season": "summer",
        "crop_type": "tomato",
        "description_en": "Maximize yield with optimal irrigation",
        "description_ar": "تعظيم الإنتاج مع الري الأمثل",
        "created_by": str(uuid.uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "valid_from": date.today().isoformat(),
        "valid_until": (date.today() + timedelta(days=90)).isoformat(),
        "is_active": True,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Ecological Constraint Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_ecological_constraint() -> dict[str, Any]:
    """
    Sample ecological constraint for testing
    قيد بيئي نموذجي للاختبار
    """
    return {
        "constraint_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "constraint_type": ConstraintType.WATER_LIMIT.value,
        "name_en": "Groundwater Conservation Limit",
        "name_ar": "حد الحفاظ على المياه الجوفية",
        "max_daily_water_m3": 500.0,
        "max_weekly_water_m3": 3000.0,
        "max_seasonal_water_m3": 45000.0,
        "min_groundwater_level_m": -50.0,
        "buffer_zone_m": 100.0,
        "sensitive_period_start": date.today().isoformat(),
        "sensitive_period_end": (date.today() + timedelta(days=60)).isoformat(),
        "penalty_coefficient": 1.5,
        "is_mandatory": True,
        "regulatory_reference": "MEWA-2024-WR-001",
        "created_at": datetime.now(UTC).isoformat(),
    }


@pytest.fixture
def sample_soil_health_constraint() -> dict[str, Any]:
    """
    Sample soil health constraint for testing
    قيد صحة التربة نموذجي للاختبار
    """
    return {
        "constraint_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "constraint_type": ConstraintType.SOIL_HEALTH.value,
        "name_en": "Soil Salinity Prevention",
        "name_ar": "منع ملوحة التربة",
        "max_ec_ds_m": 4.0,
        "max_sar": 13.0,
        "min_infiltration_rate_mm_hr": 5.0,
        "avoid_waterlogging": True,
        "max_irrigation_interval_hours": 8,
        "is_mandatory": True,
        "created_at": datetime.now(UTC).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Experience Rule Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_experience_rule() -> dict[str, Any]:
    """
    Sample farmer experience rule for testing
    قاعدة خبرة المزارع نموذجية للاختبار
    """
    return {
        "rule_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "source": RuleSource.FARMER.value,
        "source_id": str(uuid.uuid4()),
        "crop_type": "wheat",
        "condition_en": "When soil moisture drops below 35% and temperature exceeds 30C",
        "condition_ar": "عندما تنخفض رطوبة التربة تحت 35% ودرجة الحرارة تتجاوز 30 درجة",
        "action_en": "Irrigate in early morning (5-7 AM) with 20mm application",
        "action_ar": "الري في الصباح الباكر (5-7 صباحاً) بكمية 20 ملم",
        "condition_formula": "soil_moisture < 35 AND temperature > 30",
        "action_parameters": {
            "start_time": "05:00",
            "end_time": "07:00",
            "water_amount_mm": 20,
            "urgency": "high",
        },
        "confidence": 0.85,
        "success_rate": 0.92,
        "applications_count": 45,
        "learned_from_observations": 150,
        "created_at": datetime.now(UTC).isoformat(),
        "last_applied": (datetime.now(UTC) - timedelta(days=3)).isoformat(),
        "is_validated": True,
        "validation_date": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
    }


@pytest.fixture
def sample_ai_experience_rule() -> dict[str, Any]:
    """
    Sample AI-generated experience rule for testing
    قاعدة خبرة مُنشأة بالذكاء الاصطناعي نموذجية للاختبار
    """
    return {
        "rule_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "source": RuleSource.AI.value,
        "source_id": "model-crop-irrigation-v2.1",
        "crop_type": "tomato",
        "condition_en": "When NDVI drops by 0.05 in 3 days and ET0 > 6mm",
        "condition_ar": "عندما ينخفض مؤشر NDVI بمقدار 0.05 خلال 3 أيام و ET0 أكبر من 6 ملم",
        "action_en": "Increase irrigation frequency to daily with stress recovery protocol",
        "action_ar": "زيادة تواتر الري إلى يومي مع بروتوكول استعادة الإجهاد",
        "condition_formula": "ndvi_delta_3d < -0.05 AND et0 > 6",
        "action_parameters": {
            "frequency": "daily",
            "protocol": "stress_recovery",
            "water_amount_mm": 25,
            "urgency": "high",
        },
        "confidence": 0.78,
        "success_rate": 0.85,
        "applications_count": 23,
        "learned_from_observations": 500,
        "model_version": "2.1.0",
        "training_data_size": 10000,
        "created_at": datetime.now(UTC).isoformat(),
        "is_validated": False,
        "requires_human_validation": True,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Irrigation Program Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_irrigation_program() -> dict[str, Any]:
    """
    Sample AI-generated irrigation program for testing
    برنامج ري مُنشأ بالذكاء الاصطناعي نموذجي للاختبار
    """
    field_id = str(uuid.uuid4())
    return {
        "program_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "field_id": field_id,
        "tenant_id": str(uuid.uuid4()),
        "goal_id": str(uuid.uuid4()),
        "name_en": "Winter Wheat Water Conservation Program",
        "name_ar": "برنامج توفير المياه للقمح الشتوي",
        "version": "1.0.0",
        "status": "pending_review",
        "schedules": [
            {
                "schedule_id": str(uuid.uuid4()),
                "field_id": field_id,
                "date": (date.today() + timedelta(days=i)).isoformat(),
                "start_time": "06:00",
                "duration_minutes": 45,
                "water_amount_mm": 18,
                "water_amount_m3": 180,
                "zone_ids": ["zone-1", "zone-2"],
                "method": "drip",
                "priority": "normal",
                "weather_adjusted": True,
            }
            for i in range(7)
        ],
        "total_water_m3": 1260,
        "estimated_water_savings_percent": 22.5,
        "estimated_yield_percent": 95.0,
        "confidence_score": 0.87,
        "applied_rules": [str(uuid.uuid4()), str(uuid.uuid4())],
        "applied_constraints": [str(uuid.uuid4())],
        "generation_metadata": {
            "model": "irrigation-optimizer-v3",
            "model_version": "3.2.1",
            "generation_time_ms": 1250,
            "weather_data_source": "weather-service",
            "soil_data_source": "sensor-network",
        },
        "created_at": datetime.now(UTC).isoformat(),
        "valid_from": date.today().isoformat(),
        "valid_until": (date.today() + timedelta(days=7)).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Human Decision Override Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_human_override() -> dict[str, Any]:
    """
    Sample human decision override for testing
    تجاوز قرار بشري نموذجي للاختبار
    """
    return {
        "override_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "program_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "override_type": "schedule_modification",
        "original_value": {
            "water_amount_mm": 18,
            "start_time": "06:00",
        },
        "new_value": {
            "water_amount_mm": 22,
            "start_time": "05:30",
        },
        "reason_en": "Local knowledge suggests higher water need due to sandy soil patch",
        "reason_ar": "المعرفة المحلية تشير إلى حاجة مائية أعلى بسبب وجود بقعة تربة رملية",
        "confidence": 0.9,
        "requires_validation": True,
        "created_at": datetime.now(UTC).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Calibration Result Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_calibration_result() -> dict[str, Any]:
    """
    Sample calibration result for testing
    نتيجة معايرة نموذجية للاختبار
    """
    return {
        "calibration_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "program_id": str(uuid.uuid4()),
        "calibration_type": "simulation",
        "status": "passed",
        "simulated_water_savings_percent": 23.5,
        "simulated_yield_percent": 94.2,
        "goal_water_savings_percent": 25.0,
        "goal_yield_percent": 90.0,
        "water_savings_gap": 1.5,
        "yield_margin": 4.2,
        "confidence": 0.88,
        "simulation_parameters": {
            "weather_scenario": "normal",
            "soil_conditions": "average",
            "crop_response_model": "wheat-v2",
            "simulation_days": 30,
        },
        "warnings": [],
        "recommendations": [
            "Consider slight increase in irrigation during flowering stage",
        ],
        "recommendations_ar": [
            "يُنصح بزيادة طفيفة في الري خلال مرحلة الإزهار",
        ],
        "calibrated_at": datetime.now(UTC).isoformat(),
        "calibrated_by": "system",
    }


@pytest.fixture
def sample_failed_calibration() -> dict[str, Any]:
    """
    Sample failed calibration result for testing
    نتيجة معايرة فاشلة نموذجية للاختبار
    """
    return {
        "calibration_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "program_id": str(uuid.uuid4()),
        "calibration_type": "simulation",
        "status": "failed",
        "simulated_water_savings_percent": 15.0,
        "simulated_yield_percent": 82.0,
        "goal_water_savings_percent": 25.0,
        "goal_yield_percent": 90.0,
        "water_savings_gap": 10.0,
        "yield_margin": -8.0,
        "confidence": 0.65,
        "simulation_parameters": {
            "weather_scenario": "drought",
            "soil_conditions": "poor",
            "crop_response_model": "wheat-v2",
            "simulation_days": 30,
        },
        "warnings": [
            "Yield below threshold under drought conditions",
            "Water savings insufficient for goal",
        ],
        "recommendations": [
            "Increase irrigation reserves for drought buffer",
            "Consider yield-focused strategy for this field",
        ],
        "calibrated_at": datetime.now(UTC).isoformat(),
        "calibrated_by": "system",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Zone Configuration Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_zone_configuration() -> dict[str, Any]:
    """
    Sample irrigation zone configuration for testing
    تكوين منطقة ري نموذجي للاختبار
    """
    return {
        "zone_id": str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "name_en": "North Wheat Zone A",
        "name_ar": "منطقة القمح الشمالية أ",
        "zone_type": ZoneType.STANDARD.value,
        "area_hectares": 5.2,
        "soil_type": "loamy",
        "irrigation_method": "drip",
        "flow_rate_m3_hr": 12.5,
        "efficiency_percent": 90.0,
        "emitter_spacing_m": 0.3,
        "lateral_spacing_m": 1.0,
        "sensors": [
            {"sensor_id": "sm-001", "type": "soil_moisture", "depth_cm": 30},
            {"sensor_id": "sm-002", "type": "soil_moisture", "depth_cm": 60},
            {"sensor_id": "ec-001", "type": "ec", "depth_cm": 30},
        ],
        "crop_type": "wheat",
        "growth_stage": "tillering",
        "root_depth_cm": 40,
        "water_holding_capacity_mm_m": 150,
        "management_allowable_depletion": 0.5,
        "is_active": True,
        "created_at": datetime.now(UTC).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Checklist Item Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_checklist_item() -> dict[str, Any]:
    """
    Sample checklist item for testing
    عنصر قائمة تحقق نموذجي للاختبار
    """
    return {
        "item_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "category": ChecklistCategory.GOAL_ANCHORING.value,
        "order": 1,
        "title_en": "Water savings goal defined",
        "title_ar": "تم تحديد هدف توفير المياه",
        "description_en": "User has specified target water savings percentage",
        "description_ar": "حدد المستخدم النسبة المستهدفة لتوفير المياه",
        "is_required": True,
        "is_completed": True,
        "completed_at": datetime.now(UTC).isoformat(),
        "completed_by": str(uuid.uuid4()),
        "validation_data": {
            "target_percent": 25.0,
            "validated": True,
        },
    }


@pytest.fixture
def sample_incomplete_checklist_item() -> dict[str, Any]:
    """
    Sample incomplete checklist item for testing
    عنصر قائمة تحقق غير مكتمل نموذجي للاختبار
    """
    return {
        "item_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "category": ChecklistCategory.SUPERVISION.value,
        "order": 5,
        "title_en": "Simulation verification completed",
        "title_ar": "اكتمل التحقق بالمحاكاة",
        "description_en": "AI program has been verified through simulation",
        "description_ar": "تم التحقق من برنامج الذكاء الاصطناعي من خلال المحاكاة",
        "is_required": True,
        "is_completed": False,
        "completed_at": None,
        "completed_by": None,
        "validation_data": None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HMC Engine Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def hmc_engine() -> MagicMock:
    """
    Mock HMC Collaborative Engine instance
    نسخة وهمية من محرك التعاون HMC
    """
    engine = MagicMock()
    engine.session_id = str(uuid.uuid4())
    engine.status = SessionStatus.PENDING.value
    engine.farm_id = str(uuid.uuid4())
    engine.field_id = str(uuid.uuid4())
    engine.tenant_id = str(uuid.uuid4())

    # Configure async methods
    engine.start_session = AsyncMock(return_value=engine.session_id)
    engine.set_goal = AsyncMock(return_value=True)
    engine.add_constraint = AsyncMock(return_value=True)
    engine.inject_experience = AsyncMock(return_value=True)
    engine.generate_program = AsyncMock()
    engine.review_program = AsyncMock(return_value=True)
    engine.approve_program = AsyncMock(return_value=True)
    engine.reject_program = AsyncMock(return_value=True)
    engine.calibrate = AsyncMock()
    engine.record_outcome = AsyncMock(return_value=True)
    engine.get_iteration_report = AsyncMock()
    engine.get_checklist = AsyncMock(return_value=[])
    engine.get_status = MagicMock(return_value=SessionStatus.PENDING.value)

    return engine


@pytest.fixture
def hmc_engine_async() -> AsyncMock:
    """
    Async HMC Collaborative Engine for async tests
    محرك التعاون HMC غير متزامن للاختبارات غير المتزامنة
    """
    engine = AsyncMock()
    engine.session_id = str(uuid.uuid4())
    engine.status = SessionStatus.PENDING.value
    engine.farm_id = str(uuid.uuid4())
    engine.field_id = str(uuid.uuid4())
    engine.tenant_id = str(uuid.uuid4())

    return engine


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Service Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_farm_advisor() -> MagicMock:
    """
    Mock Farm Advisor service
    خدمة مستشار المزرعة الوهمية
    """
    advisor = MagicMock()

    # Field data
    advisor.get_field_data = AsyncMock(
        return_value={
            "field_id": str(uuid.uuid4()),
            "area_hectares": 10.5,
            "crop_type": "wheat",
            "growth_stage": "tillering",
            "soil_type": "loamy",
            "irrigation_method": "drip",
        }
    )

    # Soil moisture
    advisor.get_soil_moisture = AsyncMock(
        return_value={
            "moisture_percent": 42.0,
            "ec_ds_m": 1.8,
            "temperature_c": 18.5,
            "reading_time": datetime.now(UTC).isoformat(),
        }
    )

    # Crop water requirement
    advisor.get_crop_water_requirement = AsyncMock(
        return_value={
            "daily_et_mm": 5.5,
            "kc": 1.05,
            "root_depth_cm": 45,
        }
    )

    # Historical data
    advisor.get_irrigation_history = AsyncMock(
        return_value=[
            {
                "date": (date.today() - timedelta(days=i)).isoformat(),
                "water_amount_mm": 20 + (i % 5),
                "duration_minutes": 45,
                "yield_impact": 0.95 + (0.01 * (i % 3)),
            }
            for i in range(30)
        ]
    )

    # Advisory
    advisor.get_irrigation_advisory = AsyncMock(
        return_value={
            "recommended_amount_mm": 22,
            "optimal_time": "06:00",
            "urgency": "normal",
            "confidence": 0.85,
            "reasoning_en": "Based on soil moisture and weather forecast",
            "reasoning_ar": "بناءً على رطوبة التربة وتوقعات الطقس",
        }
    )

    return advisor


@pytest.fixture
def mock_weather_service() -> MagicMock:
    """
    Mock Weather Service
    خدمة الطقس الوهمية
    """
    weather = MagicMock()

    # Current weather
    weather.get_current = AsyncMock(
        return_value={
            "temperature_c": 28.5,
            "humidity_percent": 45.0,
            "wind_speed_kmh": 12.0,
            "solar_radiation_wm2": 650,
            "precipitation_mm": 0.0,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )

    # Forecast
    weather.get_forecast = AsyncMock(
        return_value=[
            {
                "date": (date.today() + timedelta(days=i)).isoformat(),
                "temperature_high_c": 30 + (i % 5),
                "temperature_low_c": 18 + (i % 3),
                "humidity_percent": 40 + (i * 2),
                "precipitation_mm": 0.0 if i < 5 else 5.0,
                "precipitation_probability": 0.1 if i < 5 else 0.6,
                "wind_speed_kmh": 10 + (i * 2),
                "et0_mm": 5.5 + (0.2 * i),
            }
            for i in range(7)
        ]
    )

    # ET0 calculation
    weather.calculate_et0 = AsyncMock(
        return_value={
            "et0_mm": 5.8,
            "method": "penman_monteith",
            "date": date.today().isoformat(),
        }
    )

    return weather


@pytest.fixture
def mock_irrigation_agent() -> MagicMock:
    """
    Mock Irrigation Agent for integration tests
    وكيل الري الوهمي لاختبارات التكامل
    """
    agent = MagicMock()

    agent.optimize_schedule = AsyncMock(
        return_value={
            "schedule": [
                {
                    "date": (date.today() + timedelta(days=i)).isoformat(),
                    "water_amount_mm": 20,
                    "start_time": "06:00",
                    "duration_minutes": 45,
                }
                for i in range(7)
            ],
            "total_water_m3": 1400,
            "estimated_savings_percent": 22.0,
            "confidence": 0.85,
        }
    )

    agent.validate_schedule = AsyncMock(
        return_value={
            "is_valid": True,
            "warnings": [],
            "errors": [],
        }
    )

    agent.execute_schedule = AsyncMock(
        return_value={
            "execution_id": str(uuid.uuid4()),
            "status": "scheduled",
            "message": "Schedule activated successfully",
        }
    )

    return agent


@pytest.fixture
def mock_nats_client() -> MagicMock:
    """
    Mock NATS client for event publishing
    عميل NATS الوهمي لنشر الأحداث
    """
    nats = MagicMock()
    nats.publish = AsyncMock(return_value=None)
    nats.subscribe = AsyncMock(return_value=MagicMock())
    nats.is_connected = True
    return nats


# ═══════════════════════════════════════════════════════════════════════════════
# Dimension Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def goal_anchoring_dimension() -> MagicMock:
    """
    Mock Goal Anchoring Dimension
    بُعد تثبيت الهدف الوهمي
    """
    dimension = MagicMock()
    dimension.set_water_saving_goal = MagicMock(return_value=True)
    dimension.set_high_yield_goal = MagicMock(return_value=True)
    dimension.set_ecological_boundaries = MagicMock(return_value=True)
    dimension.define_responsibilities = MagicMock(return_value=True)
    dimension.detect_goal_conflicts = MagicMock(return_value=[])
    dimension.validate_goals = MagicMock(return_value={"is_valid": True, "errors": []})
    return dimension


@pytest.fixture
def experience_injection_dimension() -> MagicMock:
    """
    Mock Experience Injection Dimension
    بُعد حقن الخبرة الوهمي
    """
    dimension = MagicMock()
    dimension.inject_farmer_experience = MagicMock(return_value=True)
    dimension.translate_tacit_knowledge = MagicMock(
        return_value={
            "rule_id": str(uuid.uuid4()),
            "condition_formula": "soil_moisture < 35",
            "action_parameters": {"water_amount_mm": 20},
        }
    )
    dimension.calibrate_reward_function = MagicMock(
        return_value={
            "reward_weights": {
                "water_savings": 0.4,
                "yield": 0.4,
                "cost": 0.2,
            },
            "calibration_score": 0.88,
        }
    )
    dimension.update_knowledge_base = AsyncMock(return_value=True)
    return dimension


@pytest.fixture
def supervision_calibration_dimension() -> MagicMock:
    """
    Mock Supervision Calibration Dimension
    بُعد معايرة الإشراف الوهمي
    """
    dimension = MagicMock()
    dimension.run_simulation = AsyncMock(
        return_value={
            "status": "passed",
            "simulated_yield_percent": 94.0,
            "simulated_water_savings_percent": 23.0,
        }
    )
    dimension.compare_field_trial = AsyncMock(
        return_value={
            "actual_yield_percent": 93.5,
            "actual_water_savings_percent": 22.5,
            "deviation": 0.5,
        }
    )
    dimension.check_emergency_strategy = MagicMock(
        return_value={
            "has_strategy": True,
            "scenarios_covered": ["drought", "equipment_failure", "sensor_failure"],
        }
    )
    dimension.handle_sensor_failure = AsyncMock(
        return_value={
            "fallback_mode": "conservative",
            "fallback_schedule": [],
        }
    )
    return dimension


@pytest.fixture
def value_upgrade_dimension() -> MagicMock:
    """
    Mock Value Upgrade Dimension
    بُعد ترقية القيمة الوهمي
    """
    dimension = MagicMock()
    dimension.extract_field_rules = AsyncMock(
        return_value=[
            {
                "rule_id": str(uuid.uuid4()),
                "condition": "soil_moisture < 40",
                "action": "irrigate_20mm",
                "confidence": 0.85,
            }
        ]
    )
    dimension.integrate_fertilization = AsyncMock(
        return_value={
            "integrated_schedule": [],
            "nutrient_water_sync": True,
        }
    )
    dimension.integrate_weather = AsyncMock(
        return_value={
            "weather_adjusted": True,
            "rain_reduction_mm": 5.0,
        }
    )
    dimension.calculate_carbon_reduction = MagicMock(
        return_value={
            "carbon_saved_kg": 125.5,
            "water_energy_saved_kwh": 450.0,
        }
    )
    return dimension


# ═══════════════════════════════════════════════════════════════════════════════
# Session and Workflow Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def completed_session_data(
    sample_irrigation_goal,
    sample_ecological_constraint,
    sample_experience_rule,
    sample_irrigation_program,
    sample_calibration_result,
) -> dict[str, Any]:
    """
    Complete session data for testing full workflow
    بيانات جلسة كاملة لاختبار سير العمل الكامل
    """
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "status": SessionStatus.COMPLETED.value,
        "farm_id": sample_irrigation_goal["farm_id"],
        "field_id": sample_irrigation_goal["field_id"],
        "tenant_id": sample_irrigation_goal["tenant_id"],
        "goal": sample_irrigation_goal,
        "constraints": [sample_ecological_constraint],
        "experience_rules": [sample_experience_rule],
        "program": sample_irrigation_program,
        "calibration": sample_calibration_result,
        "checklist_complete": True,
        "approved_at": datetime.now(UTC).isoformat(),
        "approved_by": str(uuid.uuid4()),
        "outcome_recorded": False,
        "created_at": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }


@pytest.fixture
def iteration_report_data() -> dict[str, Any]:
    """
    Sample iteration report data
    بيانات تقرير التكرار نموذجي
    """
    return {
        "report_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "iteration_number": 3,
        "goal_achievement": {
            "water_savings_target": 25.0,
            "water_savings_actual": 23.5,
            "yield_target": 90.0,
            "yield_actual": 94.0,
            "goal_met": True,
        },
        "experience_contribution": {
            "farmer_rules_applied": 3,
            "ai_rules_applied": 5,
            "new_rules_learned": 2,
        },
        "calibration_summary": {
            "simulations_run": 5,
            "simulations_passed": 4,
            "field_trials": 1,
        },
        "value_creation": {
            "water_saved_m3": 450,
            "cost_saved_yer": 67500,
            "carbon_reduced_kg": 125,
        },
        "recommendations": [
            "Consider adjusting irrigation timing based on new weather patterns",
        ],
        "recommendations_ar": [
            "يُنصح بتعديل توقيت الري بناءً على أنماط الطقس الجديدة",
        ],
        "created_at": datetime.now(UTC).isoformat(),
    }
