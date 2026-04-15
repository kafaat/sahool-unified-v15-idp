"""
SAHOOL Smart Agriculture - Test Fixtures
تجهيزات اختبار الزراعة الذكية

Provides fixtures for:
- PID controller configurations
- IFTTT automation rules
- Blockchain traceability records
- Deployment configurations
- Performance metrics

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum, StrEnum
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# ==============================================================================
# Enums for Smart Agriculture
# ==============================================================================


class ControllerType(StrEnum):
    """Types of controllers"""

    PID = "pid"
    ON_OFF = "on_off"
    FUZZY = "fuzzy"
    ADAPTIVE = "adaptive"


class TriggerType(StrEnum):
    """Types of IFTTT triggers"""

    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    SOIL_MOISTURE = "soil_moisture"
    LIGHT = "light"
    TIME = "time"
    WEATHER = "weather"
    CUSTOM = "custom"


class ActionType(StrEnum):
    """Types of IFTTT actions"""

    IRRIGATION = "irrigation"
    VENTILATION = "ventilation"
    LIGHTING = "lighting"
    HEATING = "heating"
    COOLING = "cooling"
    ALERT = "alert"
    LOG = "log"


class OperationType(StrEnum):
    """Types of farm operations for traceability"""

    PLANTING = "planting"
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    PESTICIDE = "pesticide"
    HARVEST = "harvest"
    STORAGE = "storage"
    TRANSPORT = "transport"
    SALE = "sale"


class DeploymentMode(StrEnum):
    """Deployment modes"""

    SAAS = "saas"
    CUSTOM = "custom"
    HYBRID = "hybrid"


# ==============================================================================
# PID Controller Fixtures
# ==============================================================================


@pytest.fixture
def pid_config() -> dict[str, Any]:
    """
    PID controller configuration
    تكوين وحدة التحكم PID
    """
    return {
        "controller_id": str(uuid.uuid4()),
        "controller_type": ControllerType.PID.value,
        "name_en": "NPK Fertilizer Controller",
        "name_ar": "وحدة التحكم في السماد NPK",
        "control_variable": "nitrogen_ppm",
        "setpoint": 25.0,
        "coefficients": {
            "kp": 2.0,  # Proportional gain
            "ki": 0.5,  # Integral gain
            "kd": 0.1,  # Derivative gain
        },
        "limits": {
            "output_min": 0.0,
            "output_max": 100.0,
            "integral_min": -50.0,
            "integral_max": 50.0,
        },
        "sampling_time_seconds": 60,
        "deadband": 1.0,
        "enabled": True,
        "auto_tune_enabled": True,
        "created_at": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
    }


@pytest.fixture
def pid_state() -> dict[str, Any]:
    """
    PID controller internal state
    الحالة الداخلية لوحدة التحكم PID
    """
    return {
        "previous_error": 0.0,
        "integral": 0.0,
        "last_output": 0.0,
        "last_input": 24.5,
        "last_update": datetime.now(UTC).isoformat(),
    }


@pytest.fixture
def sample_npk_readings() -> list[dict[str, Any]]:
    """
    Sample NPK sensor readings
    قراءات مستشعر NPK النموذجية
    """
    base_time = datetime.now(UTC)
    return [
        {
            "timestamp": (base_time - timedelta(minutes=i * 5)).isoformat(),
            "nitrogen_ppm": 22.0 + (i * 0.3),
            "phosphorus_ppm": 18.0 + (i * 0.2),
            "potassium_ppm": 150.0 + (i * 1.0),
            "ph": 7.0 + (i * 0.01),
            "ec_ds_m": 1.2 + (i * 0.05),
        }
        for i in range(10)
    ]


@pytest.fixture
def auto_tune_result() -> dict[str, Any]:
    """
    Auto-tune result for PID controller
    نتيجة الضبط التلقائي لوحدة التحكم PID
    """
    return {
        "tune_id": str(uuid.uuid4()),
        "original_coefficients": {"kp": 2.0, "ki": 0.5, "kd": 0.1},
        "tuned_coefficients": {"kp": 2.5, "ki": 0.6, "kd": 0.15},
        "method": "ziegler_nichols",
        "performance_improvement": {
            "settling_time_reduction": 15.0,  # percent
            "overshoot_reduction": 8.0,  # percent
            "steady_state_error": 0.5,  # ppm
        },
        "test_duration_minutes": 30,
        "completed_at": datetime.now(UTC).isoformat(),
    }


# ==============================================================================
# IFTTT Controller Fixtures
# ==============================================================================


@pytest.fixture
def sample_ifttt_rule() -> dict[str, Any]:
    """
    Sample IFTTT automation rule
    قاعدة أتمتة IFTTT نموذجية
    """
    return {
        "rule_id": str(uuid.uuid4()),
        "name_en": "High Temperature Alert",
        "name_ar": "تنبيه درجة الحرارة المرتفعة",
        "enabled": True,
        "priority": 1,
        "trigger": {
            "type": TriggerType.TEMPERATURE.value,
            "condition": "greater_than",
            "threshold": 35.0,
            "unit": "C",
            "duration_seconds": 300,  # Must persist for 5 minutes
        },
        "action": {
            "type": ActionType.VENTILATION.value,
            "parameters": {
                "fan_speed": 100,
                "duration_minutes": 30,
            },
        },
        "cooldown_minutes": 15,
        "last_triggered": None,
        "trigger_count": 0,
        "created_at": (datetime.now(UTC) - timedelta(days=7)).isoformat(),
    }


@pytest.fixture
def sample_light_rule() -> dict[str, Any]:
    """
    Sample light control rule
    قاعدة التحكم في الإضاءة النموذجية
    """
    return {
        "rule_id": str(uuid.uuid4()),
        "name_en": "Supplemental Lighting",
        "name_ar": "الإضاءة التكميلية",
        "enabled": True,
        "priority": 2,
        "trigger": {
            "type": TriggerType.LIGHT.value,
            "condition": "less_than",
            "threshold": 10000,
            "unit": "lux",
            "time_window": {
                "start": "06:00",
                "end": "18:00",
            },
        },
        "action": {
            "type": ActionType.LIGHTING.value,
            "parameters": {
                "brightness": 80,
                "spectrum": "full",
                "target_ppfd": 400,
            },
        },
        "cooldown_minutes": 5,
        "last_triggered": None,
        "trigger_count": 0,
    }


@pytest.fixture
def sample_compound_rule() -> dict[str, Any]:
    """
    Sample compound rule with multiple conditions
    قاعدة مركبة نموذجية مع شروط متعددة
    """
    return {
        "rule_id": str(uuid.uuid4()),
        "name_en": "Smart Irrigation",
        "name_ar": "الري الذكي",
        "enabled": True,
        "priority": 1,
        "compound_trigger": {
            "operator": "AND",
            "conditions": [
                {
                    "type": TriggerType.SOIL_MOISTURE.value,
                    "condition": "less_than",
                    "threshold": 35.0,
                },
                {
                    "type": TriggerType.TEMPERATURE.value,
                    "condition": "less_than",
                    "threshold": 35.0,  # Not too hot
                },
                {
                    "type": TriggerType.TIME.value,
                    "condition": "between",
                    "start": "05:00",
                    "end": "08:00",
                },
            ],
        },
        "action": {
            "type": ActionType.IRRIGATION.value,
            "parameters": {
                "zone_id": "zone-001",
                "duration_minutes": 30,
                "water_amount_mm": 15,
            },
        },
        "cooldown_minutes": 120,
    }


@pytest.fixture
def ifttt_controller_config() -> dict[str, Any]:
    """
    IFTTT controller configuration
    تكوين وحدة التحكم IFTTT
    """
    return {
        "controller_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "max_rules": 100,
        "evaluation_interval_seconds": 10,
        "energy_optimization": {
            "enabled": True,
            "peak_hours_start": "12:00",
            "peak_hours_end": "17:00",
            "defer_non_critical": True,
        },
        "safety_limits": {
            "max_actions_per_hour": 20,
            "require_confirmation_above": 50,  # % of resource usage
        },
    }


# ==============================================================================
# Blockchain Traceability Fixtures
# ==============================================================================


@pytest.fixture
def sample_batch() -> dict[str, Any]:
    """
    Sample product batch for traceability
    دفعة منتج نموذجية للتتبع
    """
    batch_id = str(uuid.uuid4())
    return {
        "batch_id": batch_id,
        "farm_id": str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "product_type": "wheat",
        "variety": "Sakha-95",
        "quantity_kg": 5000,
        "quality_grade": "A",
        "created_at": (datetime.now(UTC) - timedelta(days=120)).isoformat(),
        "harvest_date": (datetime.now(UTC) - timedelta(days=7)).isoformat(),
        "certifications": ["GlobalGAP", "Organic"],
        "status": "active",
    }


@pytest.fixture
def sample_operation_records() -> list[dict[str, Any]]:
    """
    Sample operation records for a batch
    سجلات العمليات النموذجية لدفعة
    """
    batch_id = str(uuid.uuid4())
    base_time = datetime.now(UTC) - timedelta(days=120)

    return [
        {
            "record_id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "operation_type": OperationType.PLANTING.value,
            "timestamp": base_time.isoformat(),
            "data": {
                "seed_variety": "Sakha-95",
                "seed_rate_kg_ha": 120,
                "depth_cm": 5,
            },
            "operator_id": "farmer-001",
            "verified": True,
        },
        {
            "record_id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "operation_type": OperationType.IRRIGATION.value,
            "timestamp": (base_time + timedelta(days=14)).isoformat(),
            "data": {
                "water_amount_mm": 25,
                "method": "drip",
                "duration_minutes": 60,
            },
            "operator_id": "system",
            "verified": True,
        },
        {
            "record_id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "operation_type": OperationType.FERTILIZATION.value,
            "timestamp": (base_time + timedelta(days=30)).isoformat(),
            "data": {
                "fertilizer_type": "Urea 46%",
                "rate_kg_ha": 46,
                "method": "broadcast",
            },
            "operator_id": "farmer-001",
            "verified": True,
        },
        {
            "record_id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "operation_type": OperationType.HARVEST.value,
            "timestamp": (base_time + timedelta(days=113)).isoformat(),
            "data": {
                "yield_kg_ha": 5200,
                "moisture_percent": 12.5,
                "quality_grade": "A",
            },
            "operator_id": "farmer-001",
            "verified": True,
        },
    ]


@pytest.fixture
def blockchain_config() -> dict[str, Any]:
    """
    Blockchain traceability configuration
    تكوين تتبع البلوكتشين
    """
    return {
        "chain_id": "sahool-trace-1",
        "consensus": "proof_of_authority",
        "validators": [
            "validator-001.sahool.local",
            "validator-002.sahool.local",
            "validator-003.sahool.local",
        ],
        "block_time_seconds": 5,
        "hash_algorithm": "sha256",
        "encryption": {
            "enabled": True,
            "algorithm": "AES-256-GCM",
        },
        "retention_days": 3650,  # 10 years
    }


# ==============================================================================
# Deployment Fixtures
# ==============================================================================


@pytest.fixture
def saas_deployment_config() -> dict[str, Any]:
    """
    SaaS deployment configuration
    تكوين نشر SaaS
    """
    return {
        "deployment_id": str(uuid.uuid4()),
        "mode": DeploymentMode.SAAS.value,
        "tenant_id": str(uuid.uuid4()),
        "subscription_tier": "professional",
        "features": {
            "max_fields": 50,
            "max_devices": 200,
            "ai_features": True,
            "blockchain_traceability": True,
            "advanced_analytics": True,
        },
        "resource_limits": {
            "api_calls_per_day": 10000,
            "storage_gb": 50,
            "data_retention_days": 365,
        },
        "region": "me-central-1",
        "compliance": ["GDPR", "MEWA-SA"],
        "sla": {
            "uptime_percent": 99.9,
            "support_response_hours": 4,
        },
        "created_at": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
    }


@pytest.fixture
def custom_deployment_config() -> dict[str, Any]:
    """
    Custom on-premise deployment configuration
    تكوين نشر مخصص محلي
    """
    return {
        "deployment_id": str(uuid.uuid4()),
        "mode": DeploymentMode.CUSTOM.value,
        "organization_id": str(uuid.uuid4()),
        "infrastructure": {
            "type": "on_premise",
            "servers": 5,
            "cpu_cores_total": 64,
            "ram_gb_total": 256,
            "storage_tb": 10,
        },
        "customizations": {
            "branding": True,
            "custom_workflows": True,
            "integration_api": True,
            "white_label": True,
        },
        "features": {
            "max_fields": -1,  # Unlimited
            "max_devices": -1,
            "ai_features": True,
            "blockchain_traceability": True,
            "advanced_analytics": True,
            "custom_models": True,
        },
        "support": {
            "type": "dedicated",
            "sla_hours": 2,
            "on_site": True,
        },
        "created_at": (datetime.now(UTC) - timedelta(days=90)).isoformat(),
    }


@pytest.fixture
def lowcode_setup_config() -> dict[str, Any]:
    """
    Low-code setup configuration
    تكوين الإعداد منخفض الكود
    """
    return {
        "setup_id": str(uuid.uuid4()),
        "template": "smart_irrigation",
        "components": [
            {
                "id": "sensor_input",
                "type": "data_source",
                "config": {"protocol": "mqtt", "sensors": ["soil_moisture", "temperature"]},
            },
            {
                "id": "pid_controller",
                "type": "controller",
                "config": {"type": "pid", "setpoint": 40},
            },
            {
                "id": "irrigation_output",
                "type": "actuator",
                "config": {"type": "valve", "zone": "zone-001"},
            },
        ],
        "connections": [
            {"from": "sensor_input", "to": "pid_controller"},
            {"from": "pid_controller", "to": "irrigation_output"},
        ],
        "validation_status": "valid",
        "estimated_setup_time_minutes": 15,
    }


# ==============================================================================
# Metrics Fixtures
# ==============================================================================


@pytest.fixture
def sample_performance_metrics() -> dict[str, Any]:
    """
    Sample performance metrics
    مقاييس الأداء النموذجية
    """
    return {
        "farm_id": str(uuid.uuid4()),
        "period": "monthly",
        "start_date": (datetime.now(UTC) - timedelta(days=30)).date().isoformat(),
        "end_date": datetime.now(UTC).date().isoformat(),
        "operational": {
            "management_radius_km": 50.0,
            "fields_managed": 25,
            "devices_active": 150,
            "automation_rate_percent": 85.0,
        },
        "efficiency": {
            "water_savings_percent": 28.0,
            "fertilizer_savings_percent": 15.0,
            "labor_cost_reduction_percent": 40.0,
            "energy_savings_percent": 22.0,
        },
        "reliability": {
            "system_uptime_percent": 99.8,
            "failure_response_time_minutes": 5.0,
            "false_positive_rate_percent": 2.0,
            "detection_accuracy_percent": 94.0,
        },
        "financial": {
            "roi_percent": 285.0,
            "payback_months": 8,
            "cost_per_hectare_yer": 450,
        },
    }


@pytest.fixture
def roi_calculation_data() -> dict[str, Any]:
    """
    ROI calculation input data
    بيانات حساب العائد على الاستثمار
    """
    return {
        "farm_id": str(uuid.uuid4()),
        "area_hectares": 100,
        "investment": {
            "hardware_cost": 150000,  # SAR
            "software_cost": 50000,
            "installation_cost": 30000,
            "training_cost": 10000,
            "total": 240000,
        },
        "annual_savings": {
            "water": 45000,
            "fertilizer": 25000,
            "labor": 80000,
            "energy": 15000,
            "yield_improvement_value": 120000,
            "total": 285000,
        },
        "annual_costs": {
            "maintenance": 20000,
            "subscription": 30000,
            "total": 50000,
        },
    }


# ==============================================================================
# Mock Services
# ==============================================================================


@pytest.fixture
def mock_sensor_service() -> MagicMock:
    """Mock sensor service"""
    service = MagicMock()
    service.get_reading = AsyncMock(
        return_value={
            "temperature": 28.5,
            "humidity": 65.0,
            "soil_moisture": 42.0,
            "light": 45000,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )
    service.get_history = AsyncMock(return_value=[])
    return service


@pytest.fixture
def mock_actuator_service() -> MagicMock:
    """Mock actuator service"""
    service = MagicMock()
    service.execute_action = AsyncMock(
        return_value={
            "success": True,
            "action_id": str(uuid.uuid4()),
            "executed_at": datetime.now(UTC).isoformat(),
        }
    )
    service.get_status = AsyncMock(return_value={"status": "ready"})
    return service


@pytest.fixture
def mock_notification_service() -> MagicMock:
    """Mock notification service"""
    service = MagicMock()
    service.send_alert = AsyncMock(return_value={"sent": True})
    service.send_report = AsyncMock(return_value={"sent": True})
    return service
