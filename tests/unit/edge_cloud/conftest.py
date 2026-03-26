"""
SAHOOL Edge-Cloud Cooperative Computing - Test Fixtures
تجهيزات اختبار الحوسبة التعاونية بين الحافة والسحابة

Provides fixtures for:
- Sensor configurations (MQTT, Modbus, LoRa)
- Edge gateway mocks
- Cloud service mocks
- Device registration data
- Sensor reading samples

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from enum import Enum, StrEnum
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# ==============================================================================
# Enums for Edge-Cloud System
# ==============================================================================


class DeviceProtocol(StrEnum):
    """Supported device communication protocols"""

    MQTT = "mqtt"
    MODBUS = "modbus"
    LORA = "lora"
    COAP = "coap"
    HTTP = "http"


class SensorType(StrEnum):
    """Types of sensors in the system"""

    SOIL_MOISTURE = "soil_moisture"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"
    PH = "ph"
    EC = "ec"
    RAIN_GAUGE = "rain_gauge"
    WIND_SPEED = "wind_speed"
    NDVI = "ndvi"
    WATER_FLOW = "water_flow"


class DeviceStatus(StrEnum):
    """Device operational status"""

    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    CALIBRATING = "calibrating"


class DataQuality(StrEnum):
    """Quality assessment of sensor data"""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INVALID = "invalid"


class InferenceMode(StrEnum):
    """Inference execution mode"""

    EDGE = "edge"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class SyncStatus(StrEnum):
    """Edge-cloud synchronization status"""

    SYNCED = "synced"
    PENDING = "pending"
    FAILED = "failed"
    OFFLINE = "offline"


# ==============================================================================
# Sensor Configuration Fixtures
# ==============================================================================


@pytest.fixture
def sample_mqtt_device() -> dict[str, Any]:
    """
    Sample MQTT device configuration
    تكوين جهاز MQTT نموذجي
    """
    device_id = str(uuid.uuid4())
    return {
        "device_id": device_id,
        "farm_id": str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "protocol": DeviceProtocol.MQTT.value,
        "name_en": "Soil Moisture Sensor Node 1",
        "name_ar": "عقدة مستشعر رطوبة التربة 1",
        "model": "SM-100-PRO",
        "manufacturer": "AgriSense",
        "firmware_version": "2.3.1",
        "connection": {
            "broker_url": "mqtt://iot.sahool.local:1883",
            "topic_data": f"sahool/sensors/{device_id}/data",
            "topic_status": f"sahool/sensors/{device_id}/status",
            "topic_command": f"sahool/sensors/{device_id}/command",
            "qos": 1,
            "retain": False,
            "client_id": f"sensor_{device_id[:8]}",
            "username": "sensor_user",
            "use_tls": True,
        },
        "sensors": [
            {
                "sensor_id": f"{device_id}_sm",
                "type": SensorType.SOIL_MOISTURE.value,
                "unit": "%",
                "depth_cm": 30,
                "min_value": 0,
                "max_value": 100,
                "accuracy": 2.0,
                "calibration_date": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
            },
            {
                "sensor_id": f"{device_id}_temp",
                "type": SensorType.TEMPERATURE.value,
                "unit": "C",
                "depth_cm": 30,
                "min_value": -10,
                "max_value": 60,
                "accuracy": 0.5,
                "calibration_date": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
            },
        ],
        "sampling_frequency_seconds": 300,  # 5 minutes
        "battery_level_percent": 85,
        "signal_strength_dbm": -65,
        "location": {
            "latitude": 24.7136,
            "longitude": 46.6753,
            "elevation_m": 612,
        },
        "status": DeviceStatus.ONLINE.value,
        "last_seen": datetime.now(UTC).isoformat(),
        "registered_at": (datetime.now(UTC) - timedelta(days=60)).isoformat(),
        "metadata": {
            "installation_date": "2024-11-15",
            "warranty_expires": "2026-11-15",
        },
    }


@pytest.fixture
def sample_modbus_device() -> dict[str, Any]:
    """
    Sample Modbus device configuration
    تكوين جهاز Modbus نموذجي
    """
    device_id = str(uuid.uuid4())
    return {
        "device_id": device_id,
        "farm_id": str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "protocol": DeviceProtocol.MODBUS.value,
        "name_en": "Weather Station WS-2000",
        "name_ar": "محطة الطقس WS-2000",
        "model": "WS-2000",
        "manufacturer": "WeatherTech",
        "firmware_version": "1.8.4",
        "connection": {
            "mode": "rtu",
            "port": "/dev/ttyUSB0",
            "baudrate": 9600,
            "parity": "N",
            "stopbits": 1,
            "bytesize": 8,
            "slave_address": 1,
            "timeout_ms": 1000,
        },
        "registers": [
            {
                "name": "temperature",
                "address": 0,
                "type": "holding",
                "data_type": "int16",
                "scale_factor": 0.1,
                "unit": "C",
            },
            {
                "name": "humidity",
                "address": 1,
                "type": "holding",
                "data_type": "int16",
                "scale_factor": 0.1,
                "unit": "%",
            },
            {
                "name": "wind_speed",
                "address": 2,
                "type": "holding",
                "data_type": "uint16",
                "scale_factor": 0.1,
                "unit": "m/s",
            },
            {
                "name": "rain_gauge",
                "address": 3,
                "type": "holding",
                "data_type": "uint16",
                "scale_factor": 0.2,
                "unit": "mm",
            },
        ],
        "sensors": [
            {
                "sensor_id": f"{device_id}_temp",
                "type": SensorType.TEMPERATURE.value,
                "unit": "C",
                "min_value": -40,
                "max_value": 60,
                "accuracy": 0.3,
            },
            {
                "sensor_id": f"{device_id}_hum",
                "type": SensorType.HUMIDITY.value,
                "unit": "%",
                "min_value": 0,
                "max_value": 100,
                "accuracy": 2.0,
            },
            {
                "sensor_id": f"{device_id}_wind",
                "type": SensorType.WIND_SPEED.value,
                "unit": "m/s",
                "min_value": 0,
                "max_value": 60,
                "accuracy": 0.5,
            },
            {
                "sensor_id": f"{device_id}_rain",
                "type": SensorType.RAIN_GAUGE.value,
                "unit": "mm",
                "min_value": 0,
                "max_value": 500,
                "accuracy": 0.2,
            },
        ],
        "sampling_frequency_seconds": 60,  # 1 minute
        "power_source": "solar",
        "status": DeviceStatus.ONLINE.value,
        "last_seen": datetime.now(UTC).isoformat(),
        "registered_at": (datetime.now(UTC) - timedelta(days=90)).isoformat(),
    }


@pytest.fixture
def sample_lora_device() -> dict[str, Any]:
    """
    Sample LoRa device configuration
    تكوين جهاز LoRa نموذجي
    """
    device_id = str(uuid.uuid4())
    return {
        "device_id": device_id,
        "farm_id": str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "protocol": DeviceProtocol.LORA.value,
        "name_en": "Remote Field Sensor LoRa-500",
        "name_ar": "مستشعر الحقل البعيد LoRa-500",
        "model": "LoRa-500",
        "manufacturer": "AgriIoT",
        "firmware_version": "3.0.2",
        "connection": {
            "dev_eui": "0011223344556677",
            "app_eui": "70B3D57ED0000001",
            "app_key": "2B7E151628AED2A6ABF7158809CF4F3C",
            "network_server": "lorawan.sahool.local",
            "spreading_factor": 7,
            "bandwidth_khz": 125,
            "frequency_mhz": 868.1,
        },
        "sensors": [
            {
                "sensor_id": f"{device_id}_sm",
                "type": SensorType.SOIL_MOISTURE.value,
                "unit": "%",
                "depth_cm": 60,
                "min_value": 0,
                "max_value": 100,
                "accuracy": 3.0,
            },
        ],
        "sampling_frequency_seconds": 900,  # 15 minutes (battery saving)
        "battery_level_percent": 72,
        "signal_strength_rssi": -95,
        "snr": 8.5,
        "status": DeviceStatus.ONLINE.value,
        "last_seen": datetime.now(UTC).isoformat(),
    }


# ==============================================================================
# Sensor Reading Fixtures
# ==============================================================================


@pytest.fixture
def sample_sensor_readings() -> list[dict[str, Any]]:
    """
    Sample batch of sensor readings
    مجموعة قراءات المستشعرات النموذجية
    """
    device_id = str(uuid.uuid4())
    base_time = datetime.now(UTC)

    readings = []
    for i in range(10):
        timestamp = base_time - timedelta(minutes=5 * i)
        readings.append(
            {
                "reading_id": str(uuid.uuid4()),
                "device_id": device_id,
                "sensor_id": f"{device_id}_sm",
                "sensor_type": SensorType.SOIL_MOISTURE.value,
                "value": 42.5 + (i * 0.5),  # Slightly varying values
                "unit": "%",
                "timestamp": timestamp.isoformat(),
                "quality": DataQuality.GOOD.value,
                "quality_score": 0.95,
                "metadata": {
                    "battery_level": 85 - (i * 0.1),
                    "signal_strength": -65 - (i * 0.5),
                },
            }
        )

    return readings


@pytest.fixture
def sample_raw_sensor_data() -> dict[str, Any]:
    """
    Sample raw sensor data before cleaning
    بيانات المستشعر الخام قبل التنظيف
    """
    return {
        "device_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "raw_values": [
            {"sensor": "soil_moisture", "value": 45.2, "raw_adc": 2048},
            {"sensor": "temperature", "value": 28.7, "raw_adc": 1536},
            {"sensor": "humidity", "value": 65.3, "raw_adc": 2867},
        ],
        "checksum": "a3b2c1d4",
        "sequence_number": 12345,
    }


@pytest.fixture
def sample_anomalous_readings() -> list[dict[str, Any]]:
    """
    Sample sensor readings with anomalies for testing data cleaning
    قراءات مستشعر نموذجية مع شذوذ لاختبار تنظيف البيانات
    """
    device_id = str(uuid.uuid4())
    base_time = datetime.now(UTC)

    return [
        # Normal reading
        {
            "reading_id": str(uuid.uuid4()),
            "device_id": device_id,
            "sensor_type": SensorType.SOIL_MOISTURE.value,
            "value": 45.0,
            "timestamp": base_time.isoformat(),
        },
        # Out of range (too high)
        {
            "reading_id": str(uuid.uuid4()),
            "device_id": device_id,
            "sensor_type": SensorType.SOIL_MOISTURE.value,
            "value": 150.0,  # Invalid: > 100%
            "timestamp": (base_time - timedelta(minutes=5)).isoformat(),
        },
        # Out of range (negative)
        {
            "reading_id": str(uuid.uuid4()),
            "device_id": device_id,
            "sensor_type": SensorType.SOIL_MOISTURE.value,
            "value": -10.0,  # Invalid: < 0%
            "timestamp": (base_time - timedelta(minutes=10)).isoformat(),
        },
        # Spike (sudden change)
        {
            "reading_id": str(uuid.uuid4()),
            "device_id": device_id,
            "sensor_type": SensorType.SOIL_MOISTURE.value,
            "value": 95.0,  # Suspicious spike
            "timestamp": (base_time - timedelta(minutes=15)).isoformat(),
        },
        # Null value
        {
            "reading_id": str(uuid.uuid4()),
            "device_id": device_id,
            "sensor_type": SensorType.SOIL_MOISTURE.value,
            "value": None,  # Missing
            "timestamp": (base_time - timedelta(minutes=20)).isoformat(),
        },
        # Normal reading
        {
            "reading_id": str(uuid.uuid4()),
            "device_id": device_id,
            "sensor_type": SensorType.SOIL_MOISTURE.value,
            "value": 44.5,
            "timestamp": (base_time - timedelta(minutes=25)).isoformat(),
        },
    ]


# ==============================================================================
# Edge Gateway Fixtures
# ==============================================================================


@pytest.fixture
def mock_edge_gateway() -> MagicMock:
    """
    Mock Edge Gateway service
    خدمة بوابة الحافة الوهمية
    """
    gateway = MagicMock()
    gateway.gateway_id = str(uuid.uuid4())
    gateway.status = "online"
    gateway.connected_devices = 15
    gateway.sync_status = SyncStatus.SYNCED.value
    gateway.last_cloud_sync = datetime.now(UTC).isoformat()

    # Configure async methods
    gateway.register_device = AsyncMock(return_value={"success": True, "device_id": str(uuid.uuid4())})
    gateway.unregister_device = AsyncMock(return_value={"success": True})
    gateway.collect_data = AsyncMock(
        return_value={
            "readings_count": 100,
            "devices_polled": 15,
            "errors": [],
        }
    )
    gateway.run_local_inference = AsyncMock(
        return_value={
            "inference_id": str(uuid.uuid4()),
            "predictions": [{"field_id": str(uuid.uuid4()), "irrigation_needed": True, "confidence": 0.87}],
            "latency_ms": 150,
            "model_version": "edge-1.2.0",
        }
    )
    gateway.sync_to_cloud = AsyncMock(
        return_value={
            "records_synced": 500,
            "sync_duration_ms": 2500,
            "status": "completed",
        }
    )
    gateway.get_offline_queue_size = MagicMock(return_value=0)
    gateway.trigger_auto_irrigation = AsyncMock(
        return_value={
            "action_id": str(uuid.uuid4()),
            "zone_id": str(uuid.uuid4()),
            "water_amount_mm": 15,
            "triggered_at": datetime.now(UTC).isoformat(),
        }
    )

    return gateway


@pytest.fixture
def mock_edge_model() -> MagicMock:
    """
    Mock edge inference model
    نموذج الاستدلال الحافة الوهمي
    """
    model = MagicMock()
    model.model_id = "irrigation-edge-v1.2"
    model.model_type = "decision_tree"
    model.version = "1.2.0"
    model.input_features = ["soil_moisture", "temperature", "humidity", "et0"]
    model.output_classes = ["irrigate", "wait", "reduce"]
    model.size_kb = 256
    model.inference_time_ms = 50

    model.predict = MagicMock(
        return_value={
            "prediction": "irrigate",
            "confidence": 0.92,
            "probabilities": {"irrigate": 0.92, "wait": 0.06, "reduce": 0.02},
        }
    )
    model.predict_batch = MagicMock(
        return_value=[
            {"prediction": "irrigate", "confidence": 0.92},
            {"prediction": "wait", "confidence": 0.85},
        ]
    )
    model.validate_input = MagicMock(return_value=True)

    return model


@pytest.fixture
def edge_gateway_config() -> dict[str, Any]:
    """
    Edge gateway configuration
    تكوين بوابة الحافة
    """
    return {
        "gateway_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "name_en": "Field Gateway 1",
        "name_ar": "بوابة الحقل 1",
        "hardware": {
            "model": "EdgeGate-Pro-500",
            "cpu": "ARM Cortex-A72",
            "ram_mb": 4096,
            "storage_gb": 64,
            "has_gpu": False,
        },
        "network": {
            "primary_interface": "eth0",
            "backup_interface": "wlan0",
            "cellular_enabled": True,
            "cellular_apn": "m2m.sahool.sa",
        },
        "protocols": [
            DeviceProtocol.MQTT.value,
            DeviceProtocol.MODBUS.value,
            DeviceProtocol.LORA.value,
        ],
        "edge_inference": {
            "enabled": True,
            "models": ["irrigation-edge-v1.2", "pest-detection-lite-v1.0"],
            "max_batch_size": 32,
            "inference_threads": 4,
        },
        "data_buffer": {
            "max_records": 100000,
            "sync_interval_seconds": 300,
            "offline_retention_days": 7,
        },
        "latency_requirements": {
            "max_inference_ms": 300,
            "max_data_collection_ms": 1000,
            "auto_action_threshold_ms": 500,
        },
        "auto_actions": {
            "irrigation_enabled": True,
            "alert_enabled": True,
            "frost_protection_enabled": True,
        },
        "location": {
            "latitude": 24.7136,
            "longitude": 46.6753,
        },
        "created_at": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }


# ==============================================================================
# Cloud Service Fixtures
# ==============================================================================


@pytest.fixture
def mock_cloud_ai_service() -> MagicMock:
    """
    Mock Cloud AI service
    خدمة الذكاء الاصطناعي السحابية الوهمية
    """
    service = MagicMock()

    # Pest detection
    service.detect_pest = AsyncMock(
        return_value={
            "detection_id": str(uuid.uuid4()),
            "pest_detected": True,
            "pest_type": "aphid",
            "confidence": 0.94,
            "severity": "moderate",
            "affected_area_percent": 15.0,
            "recommendations": [
                "Apply neem oil spray",
                "Introduce beneficial insects (ladybugs)",
            ],
            "recommendations_ar": [
                "رش زيت النيم",
                "إدخال الحشرات المفيدة (الدعسوقة)",
            ],
            "processing_time_ms": 850,
        }
    )

    # Moisture prediction
    service.predict_moisture = AsyncMock(
        return_value={
            "prediction_id": str(uuid.uuid4()),
            "field_id": str(uuid.uuid4()),
            "predictions": [
                {"hours_ahead": 6, "moisture_percent": 38.5, "confidence": 0.92},
                {"hours_ahead": 12, "moisture_percent": 35.2, "confidence": 0.88},
                {"hours_ahead": 24, "moisture_percent": 31.0, "confidence": 0.82},
                {"hours_ahead": 48, "moisture_percent": 28.5, "confidence": 0.75},
            ],
            "irrigation_needed_within_hours": 24,
            "model_version": "moisture-lstm-v2.1",
        }
    )

    # Yield estimation
    service.estimate_yield = AsyncMock(
        return_value={
            "estimation_id": str(uuid.uuid4()),
            "field_id": str(uuid.uuid4()),
            "crop_type": "wheat",
            "estimated_yield_kg_ha": 5250,
            "yield_range": {"min": 4800, "max": 5700},
            "confidence": 0.85,
            "factors": {
                "soil_health": 0.88,
                "weather_favorability": 0.82,
                "irrigation_efficiency": 0.91,
                "pest_pressure": 0.95,
            },
            "comparison_to_historical": {
                "vs_last_season": "+8.5%",
                "vs_5_year_avg": "+12.2%",
            },
            "model_version": "yield-xgboost-v3.0",
        }
    )

    # Model training
    service.train_model = AsyncMock(
        return_value={
            "training_job_id": str(uuid.uuid4()),
            "model_type": "pest_detection",
            "status": "completed",
            "metrics": {
                "accuracy": 0.94,
                "precision": 0.92,
                "recall": 0.95,
                "f1_score": 0.935,
            },
            "training_duration_minutes": 45,
            "data_samples": 15000,
            "model_version": "pest-detection-v2.1",
        }
    )

    return service


@pytest.fixture
def mock_cloud_storage() -> MagicMock:
    """
    Mock cloud storage service
    خدمة التخزين السحابي الوهمية
    """
    storage = MagicMock()

    storage.upload_sensor_data = AsyncMock(
        return_value={
            "upload_id": str(uuid.uuid4()),
            "records_uploaded": 1000,
            "bytes_transferred": 256000,
            "duration_ms": 1500,
        }
    )
    storage.download_model = AsyncMock(
        return_value={
            "model_id": "pest-detection-v2.1",
            "size_bytes": 52428800,
            "checksum": "sha256:abc123...",
        }
    )
    storage.sync_historical_data = AsyncMock(
        return_value={
            "sync_id": str(uuid.uuid4()),
            "records_synced": 50000,
            "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
        }
    )

    return storage


# ==============================================================================
# Cooperative System Fixtures
# ==============================================================================


@pytest.fixture
def cooperative_system_config() -> dict[str, Any]:
    """
    Edge-cloud cooperative system configuration
    تكوين النظام التعاوني بين الحافة والسحابة
    """
    return {
        "system_id": str(uuid.uuid4()),
        "farm_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "mode": InferenceMode.HYBRID.value,
        "edge_config": {
            "enabled": True,
            "primary_tasks": ["irrigation_decision", "alert_detection"],
            "max_latency_ms": 300,
            "offline_capable": True,
        },
        "cloud_config": {
            "enabled": True,
            "primary_tasks": ["pest_detection", "yield_estimation", "model_training"],
            "sync_interval_seconds": 300,
        },
        "fallback_rules": {
            "on_cloud_unavailable": "use_edge",
            "on_edge_failure": "queue_for_cloud",
            "max_offline_hours": 72,
        },
        "data_flow": {
            "sensor_to_edge_batch_size": 100,
            "edge_to_cloud_batch_size": 1000,
            "cloud_model_update_interval_hours": 24,
        },
        "quality_thresholds": {
            "min_data_quality_score": 0.7,
            "min_inference_confidence": 0.75,
        },
    }


@pytest.fixture
def mock_cooperative_orchestrator() -> MagicMock:
    """
    Mock cooperative system orchestrator
    منسق النظام التعاوني الوهمي
    """
    orchestrator = MagicMock()
    orchestrator.system_id = str(uuid.uuid4())
    orchestrator.mode = InferenceMode.HYBRID.value
    orchestrator.edge_status = "online"
    orchestrator.cloud_status = "connected"

    orchestrator.route_inference = AsyncMock(
        return_value={
            "execution_layer": "edge",
            "reason": "latency_requirement",
            "fallback_available": True,
        }
    )
    orchestrator.sync_data = AsyncMock(
        return_value={
            "sync_id": str(uuid.uuid4()),
            "records_synced": 5000,
            "direction": "edge_to_cloud",
            "status": "completed",
        }
    )
    orchestrator.update_edge_model = AsyncMock(
        return_value={
            "model_id": "irrigation-edge-v1.3",
            "update_status": "success",
            "previous_version": "1.2.0",
            "new_version": "1.3.0",
        }
    )
    orchestrator.get_system_metrics = MagicMock(
        return_value={
            "edge_inference_count_24h": 5000,
            "cloud_inference_count_24h": 500,
            "avg_edge_latency_ms": 85,
            "avg_cloud_latency_ms": 450,
            "sync_success_rate": 0.998,
            "data_freshness_seconds": 120,
        }
    )

    return orchestrator


@pytest.fixture
def full_pipeline_data() -> dict[str, Any]:
    """
    Sample data for full pipeline testing
    بيانات نموذجية لاختبار خط الأنابيب الكامل
    """
    field_id = str(uuid.uuid4())
    return {
        "field_id": field_id,
        "farm_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "sensor_data": {
            "soil_moisture": 35.5,
            "temperature": 32.0,
            "humidity": 45.0,
            "et0": 6.2,
        },
        "weather_forecast": {
            "next_rain_hours": 72,
            "max_temp_c": 35,
            "min_temp_c": 22,
        },
        "crop_info": {
            "type": "wheat",
            "stage": "tillering",
            "days_since_planting": 45,
        },
        "expected_output": {
            "irrigation_decision": "irrigate",
            "recommended_amount_mm": 20,
            "urgency": "high",
        },
    }


# ==============================================================================
# Performance Testing Fixtures
# ==============================================================================


@pytest.fixture
def latency_test_config() -> dict[str, Any]:
    """
    Configuration for latency testing
    تكوين اختبار زمن الاستجابة
    """
    return {
        "target_inference_latency_ms": 300,
        "target_data_collection_latency_ms": 1000,
        "target_sync_latency_ms": 5000,
        "test_iterations": 100,
        "warm_up_iterations": 10,
    }


@pytest.fixture
def stress_test_config() -> dict[str, Any]:
    """
    Configuration for stress testing
    تكوين اختبار الإجهاد
    """
    return {
        "concurrent_devices": 100,
        "readings_per_second": 1000,
        "test_duration_seconds": 60,
        "expected_success_rate": 0.99,
    }
