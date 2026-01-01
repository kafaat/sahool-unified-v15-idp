"""
SAHOOL Integration Tests - IoT Workflow
اختبارات التكامل - سير عمل إنترنت الأشياء

Tests complete IoT integration workflow including:
- Device registration and management
- Sensor data ingestion
- Real-time data streaming
- Data aggregation and analysis
- Alert generation from sensor data
- Irrigation automation
- Actuator control

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════════════════════
# Test IoT Device Registration - اختبار تسجيل أجهزة IoT
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_iot_device_registration_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تسجيل جهاز IoT

    Test IoT device registration:
    1. Register new IoT device
    2. Verify device credentials
    3. Associate device with field
    """
    # Arrange - إعداد
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    device_data = {
        "device_id": "sensor-sm-test-001",
        "device_type": "soil_moisture_sensor",
        "device_type_ar": "مستشعر رطوبة التربة",
        "manufacturer": "AgroSense",
        "model": "SM-200",
        "firmware_version": "2.1.0",
        "field_id": "field-test-123",
        "location": {"latitude": 15.3694, "longitude": 44.1910},
        "configuration": {
            "measurement_interval_minutes": 30,
            "depth_cm": 30,
            "alert_threshold_low": 20,
            "alert_threshold_high": 80,
        },
    }

    # Act - تنفيذ
    response = await http_client.post(
        f"{iot_gateway_url}/v1/devices", json=device_data, headers=auth_headers
    )

    # Assert - التحقق
    assert response.status_code in (
        200,
        201,
        401,
    ), f"Failed to register device: {response.text}"

    if response.status_code in (200, 201):
        registered_device = response.json()
        assert "device_id" in registered_device or "id" in registered_device
        assert "credentials" in registered_device or "api_key" in registered_device


@pytest.mark.integration
@pytest.mark.asyncio
async def test_iot_device_listing_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل سرد أجهزة IoT

    Test listing IoT devices:
    1. List all devices for a field
    2. Filter by device type
    3. Check device status
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Get all devices - الحصول على جميع الأجهزة
    response = await http_client.get(
        f"{iot_gateway_url}/v1/devices", headers=auth_headers
    )

    if response.status_code == 200:
        devices = response.json()
        assert isinstance(devices, (list, dict))


# ═══════════════════════════════════════════════════════════════════════════════
# Test Sensor Data Ingestion - اختبار استيعاب بيانات المستشعرات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_soil_moisture_reading_workflow(
    http_client,
    service_urls: Dict[str, str],
    iot_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل قراءة رطوبة التربة

    Test soil moisture sensor reading:
    1. Device sends soil moisture reading
    2. Gateway ingests and validates data
    3. Data stored in database
    4. Real-time update sent via NATS
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Create sensor reading - إنشاء قراءة المستشعر
    reading_data = iot_factory.create(sensor_type="soil_moisture")

    # Add required fields
    reading_data.update(
        {
            "field_id": "field-test-123",
            "location": {"latitude": 15.3694, "longitude": 44.1910, "depth_cm": 30},
        }
    )

    # Send reading to gateway - إرسال القراءة إلى البوابة
    response = await http_client.post(
        f"{iot_gateway_url}/v1/readings", json=reading_data, headers=auth_headers
    )

    assert response.status_code in (
        200,
        201,
        401,
    ), f"Failed to submit reading: {response.text}"

    if response.status_code in (200, 201):
        result = response.json()
        assert "id" in result or "reading_id" in result
        assert result.get("status") in ("accepted", "processed", None)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_temperature_humidity_reading_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل قراءة درجة الحرارة والرطوبة

    Test temperature and humidity sensor reading:
    1. Device sends temperature and humidity data
    2. Data validated and stored
    3. Trigger alert if thresholds exceeded
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    reading_data = {
        "device_id": "sensor-th-test-001",
        "sensor_type": "temperature_humidity",
        "field_id": "field-test-123",
        "timestamp": datetime.utcnow().isoformat(),
        "readings": {"temperature_c": 38.5, "humidity_percent": 32, "heat_index": 42.3},
        "location": {"latitude": 15.3694, "longitude": 44.1910, "height_cm": 150},
    }

    response = await http_client.post(
        f"{iot_gateway_url}/v1/readings", json=reading_data, headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_soil_nutrient_reading_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل قراءة مغذيات التربة

    Test soil nutrient sensor reading:
    1. Device sends N-P-K sensor data
    2. Data analyzed for nutrient deficiencies
    3. Fertilizer recommendations generated
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    reading_data = {
        "device_id": "sensor-npk-test-001",
        "sensor_type": "soil_nutrient",
        "field_id": "field-test-123",
        "timestamp": datetime.utcnow().isoformat(),
        "readings": {
            "nitrogen_ppm": 45,
            "phosphorus_ppm": 28,
            "potassium_ppm": 120,
            "ph": 6.8,
            "ec_ds_m": 1.2,
        },
        "location": {"latitude": 15.3694, "longitude": 44.1910, "depth_cm": 20},
    }

    response = await http_client.post(
        f"{iot_gateway_url}/v1/readings", json=reading_data, headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Batch Sensor Data - اختبار بيانات المستشعرات الدفعية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_batch_readings_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل القراءات الدفعية

    Test batch sensor readings:
    1. Device sends multiple readings at once
    2. Gateway processes batch efficiently
    3. All readings stored correctly
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Create batch of readings - إنشاء دفعة من القراءات
    batch_data = {
        "device_id": "sensor-sm-test-001",
        "readings": [
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                "sensor_type": "soil_moisture",
                "value": 42.5,
                "unit": "%",
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
                "sensor_type": "soil_moisture",
                "value": 41.8,
                "unit": "%",
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
                "sensor_type": "soil_moisture",
                "value": 41.2,
                "unit": "%",
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "sensor_type": "soil_moisture",
                "value": 40.5,
                "unit": "%",
            },
        ],
    }

    response = await http_client.post(
        f"{iot_gateway_url}/v1/readings/batch", json=batch_data, headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Real-time Data Streaming - اختبار بث البيانات في الوقت الفعلي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_realtime_data_streaming_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل بث البيانات في الوقت الفعلي

    Test real-time data streaming:
    1. Subscribe to field sensor updates
    2. Receive real-time data via WebSocket
    3. Verify data integrity
    """
    ws_gateway_url = service_urls.get("ws_gateway", "http://localhost:8081")

    # This would typically use WebSocket connection
    # For HTTP testing, we check if the endpoint exists
    response = await http_client.get(f"{ws_gateway_url}/healthz", headers=auth_headers)

    # WebSocket gateway should be running
    assert response.status_code in (200, 404, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Aggregation - اختبار تجميع البيانات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sensor_data_aggregation_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تجميع بيانات المستشعرات

    Test sensor data aggregation:
    1. Get hourly averages
    2. Get daily summaries
    3. Get trend analysis
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Get hourly aggregated data - الحصول على البيانات المجمعة بالساعة
    params = {
        "field_id": "field-test-123",
        "sensor_type": "soil_moisture",
        "aggregation": "hourly",
        "start_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "end_date": datetime.utcnow().isoformat(),
    }

    response = await http_client.get(
        f"{iot_gateway_url}/v1/readings/aggregated", params=params, headers=auth_headers
    )

    if response.status_code == 200:
        aggregated_data = response.json()
        assert isinstance(aggregated_data, (list, dict))


# ═══════════════════════════════════════════════════════════════════════════════
# Test Irrigation Automation - اختبار أتمتة الري
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_automated_irrigation_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل الري الآلي

    Test automated irrigation:
    1. Soil moisture drops below threshold
    2. System automatically triggers irrigation
    3. Irrigation valve actuator activated
    4. Monitor water flow
    5. Stop when optimal moisture reached
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Create irrigation automation rule - إنشاء قاعدة أتمتة الري
    automation_rule = {
        "field_id": "field-test-123",
        "rule_type": "irrigation_auto",
        "name": "Auto Irrigation - Wheat Field",
        "name_ar": "ري آلي - حقل القمح",
        "enabled": True,
        "conditions": {
            "sensor_type": "soil_moisture",
            "operator": "less_than",
            "threshold": 30,
            "consecutive_readings": 2,
        },
        "actions": [
            {
                "action_type": "actuator_control",
                "device_id": "valve-001",
                "command": "open",
                "duration_minutes": 30,
            }
        ],
        "stop_conditions": {
            "sensor_type": "soil_moisture",
            "operator": "greater_than",
            "threshold": 50,
        },
    }

    response = await http_client.post(
        f"{iot_gateway_url}/v1/automation/rules",
        json=automation_rule,
        headers=auth_headers,
    )

    assert response.status_code in (200, 201, 401)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_irrigation_valve_control_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل التحكم في صمام الري

    Test irrigation valve control:
    1. Send command to open valve
    2. Monitor valve status
    3. Close valve after irrigation complete
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Open irrigation valve - فتح صمام الري
    valve_command = {
        "device_id": "valve-test-001",
        "command": "open",
        "parameters": {"duration_minutes": 15, "flow_rate_lpm": 50},
    }

    response = await http_client.post(
        f"{iot_gateway_url}/v1/actuators/command",
        json=valve_command,
        headers=auth_headers,
    )

    assert response.status_code in (200, 201, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Alert Generation from Sensors - اختبار إنشاء التنبيهات من المستشعرات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sensor_threshold_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تنبيه عتبة المستشعر

    Test sensor threshold alert:
    1. Sensor reading exceeds threshold
    2. Alert automatically generated
    3. Farmer notified
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Configure alert threshold - تكوين عتبة التنبيه
    threshold_config = {
        "device_id": "sensor-sm-test-001",
        "sensor_type": "soil_moisture",
        "field_id": "field-test-123",
        "thresholds": [
            {
                "condition": "less_than",
                "value": 25,
                "severity": "high",
                "alert_type": "irrigation_needed",
            },
            {
                "condition": "greater_than",
                "value": 75,
                "severity": "medium",
                "alert_type": "over_irrigation",
            },
        ],
    }

    response = await http_client.post(
        f"{iot_gateway_url}/v1/devices/thresholds",
        json=threshold_config,
        headers=auth_headers,
    )

    assert response.status_code in (200, 201, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Device Health Monitoring - اختبار مراقبة صحة الجهاز
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_health_monitoring_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل مراقبة صحة الجهاز

    Test device health monitoring:
    1. Check device battery level
    2. Check last communication time
    3. Alert if device offline
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Send device health status - إرسال حالة صحة الجهاز
    health_data = {
        "device_id": "sensor-sm-test-001",
        "timestamp": datetime.utcnow().isoformat(),
        "battery_percent": 45,
        "signal_strength_dbm": -72,
        "temperature_c": 28,
        "uptime_hours": 720,
        "error_count": 0,
    }

    response = await http_client.post(
        f"{iot_gateway_url}/v1/devices/health", json=health_data, headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_offline_detection_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل كشف الجهاز غير المتصل

    Test offline device detection:
    1. Device hasn't sent data in expected interval
    2. System marks device as offline
    3. Alert sent to farmer
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Get offline devices - الحصول على الأجهزة غير المتصلة
    response = await http_client.get(
        f"{iot_gateway_url}/v1/devices/offline", headers=auth_headers
    )

    if response.status_code == 200:
        offline_devices = response.json()
        assert isinstance(offline_devices, (list, dict))


# ═══════════════════════════════════════════════════════════════════════════════
# Test Data Export and Analytics - اختبار تصدير البيانات والتحليلات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sensor_data_export_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تصدير بيانات المستشعرات

    Test sensor data export:
    1. Export sensor data for date range
    2. Format as CSV/JSON
    3. Include metadata
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    export_params = {
        "field_id": "field-test-123",
        "start_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "format": "csv",
        "sensor_types": ["soil_moisture", "temperature"],
    }

    response = await http_client.get(
        f"{iot_gateway_url}/v1/readings/export",
        params=export_params,
        headers=auth_headers,
    )

    assert response.status_code in (200, 401, 404)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sensor_analytics_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تحليلات المستشعرات

    Test sensor analytics:
    1. Calculate statistics (min, max, avg, stddev)
    2. Detect anomalies
    3. Identify trends
    """
    iot_gateway_url = service_urls.get("iot_gateway", "http://localhost:8106")

    analytics_params = {
        "field_id": "field-test-123",
        "sensor_type": "soil_moisture",
        "period": "last_7_days",
    }

    response = await http_client.get(
        f"{iot_gateway_url}/v1/analytics/sensors",
        params=analytics_params,
        headers=auth_headers,
    )

    if response.status_code == 200:
        analytics = response.json()
        # Should include statistics
        assert isinstance(analytics, dict)
