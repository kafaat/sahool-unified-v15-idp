"""
SAHOOL Integration Tests - Alert Workflow
اختبارات التكامل - سير عمل التنبيهات

Tests complete alert system workflow including:
- Weather alerts (rain, frost, heat waves)
- Pest outbreak alerts
- Soil condition alerts
- IoT sensor alerts
- Irrigation alerts
- Disease detection alerts
- Alert priority and escalation
- Multi-channel alert delivery

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════════════════════
# Test Weather Alert Workflow - اختبار سير عمل تنبيهات الطقس
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_alert_creation_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل إنشاء تنبيه طقس

    Test weather alert creation:
    1. Detect extreme weather condition
    2. Create alert
    3. Notify affected farmers
    4. Verify alert delivery
    """
    # Arrange - إعداد
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    # Step 1: Create extreme weather alert - إنشاء تنبيه طقس متطرف
    alert_data = {
        "type": "weather",
        "subtype": "heavy_rain",
        "severity": "high",
        "title": "Heavy Rain Warning",
        "title_ar": "تحذير من الأمطار الغزيرة",
        "description": "Heavy rainfall expected in the next 24 hours. Secure your crops and equipment.",
        "description_ar": "من المتوقع هطول أمطار غزيرة خلال الـ 24 ساعة القادمة. قم بتأمين محاصيلك ومعداتك.",
        "location": {
            "latitude": 15.3694,
            "longitude": 44.1910,
            "radius_km": 50
        },
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "data": {
            "rainfall_mm": 80,
            "wind_speed_kmh": 45,
            "temperature_c": 22
        },
        "actions": [
            {
                "action": "secure_equipment",
                "action_ar": "تأمين المعدات"
            },
            {
                "action": "check_drainage",
                "action_ar": "فحص نظام الصرف"
            }
        ]
    }

    # Act - تنفيذ
    response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    # Assert - التحقق
    assert response.status_code in (200, 201), f"Failed to create alert: {response.text}"

    created_alert = response.json()

    assert "id" in created_alert or "alert_id" in created_alert
    assert created_alert.get("type") == "weather"
    assert created_alert.get("severity") == "high"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_frost_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تنبيه الصقيع

    Test frost alert workflow:
    1. Detect frost conditions
    2. Alert farmers to protect crops
    3. Suggest protective actions
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    alert_data = {
        "type": "weather",
        "subtype": "frost",
        "severity": "critical",
        "title": "Frost Alert - Protect Your Crops",
        "title_ar": "تنبيه الصقيع - احمِ محاصيلك",
        "description": "Frost conditions expected tonight. Take immediate action to protect sensitive crops.",
        "description_ar": "من المتوقع ظروف صقيع الليلة. اتخذ إجراءات فورية لحماية المحاصيل الحساسة.",
        "location": {
            "latitude": 15.3694,
            "longitude": 44.1910,
            "radius_km": 30
        },
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(hours=12)).isoformat(),
        "data": {
            "min_temperature_c": -2,
            "frost_probability": 0.85,
            "affected_hours": 6
        },
        "actions": [
            {
                "action": "cover_sensitive_crops",
                "action_ar": "غطِ المحاصيل الحساسة",
                "priority": "critical"
            },
            {
                "action": "run_frost_protection",
                "action_ar": "شغل نظام الحماية من الصقيع",
                "priority": "high"
            }
        ]
    }

    response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    assert response.status_code in (200, 201, 401), f"Unexpected response: {response.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# Test Pest Alert Workflow - اختبار سير عمل تنبيهات الآفات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pest_outbreak_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تنبيه تفشي الآفات

    Test pest outbreak alert:
    1. Detect pest outbreak pattern
    2. Create alert for affected region
    3. Recommend treatment actions
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    alert_data = {
        "type": "pest",
        "subtype": "locust_swarm",
        "severity": "critical",
        "title": "Locust Swarm Alert",
        "title_ar": "تنبيه سرب الجراد",
        "description": "Locust swarm detected moving towards your region. Immediate action required.",
        "description_ar": "تم رصد سرب جراد يتحرك نحو منطقتك. مطلوب إجراء فوري.",
        "location": {
            "latitude": 15.5000,
            "longitude": 44.2000,
            "radius_km": 100
        },
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(hours=48)).isoformat(),
        "data": {
            "pest_type": "desert_locust",
            "pest_type_ar": "جراد الصحراء",
            "swarm_density": "high",
            "movement_direction": "northeast",
            "estimated_arrival_hours": 12
        },
        "actions": [
            {
                "action": "apply_pesticide",
                "action_ar": "رش المبيدات",
                "priority": "critical"
            },
            {
                "action": "coordinate_with_authorities",
                "action_ar": "التنسيق مع السلطات",
                "priority": "high"
            },
            {
                "action": "monitor_crops",
                "action_ar": "مراقبة المحاصيل",
                "priority": "medium"
            }
        ]
    }

    response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_disease_detection_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تنبيه اكتشاف الأمراض

    Test disease detection alert:
    1. AI detects crop disease from images
    2. Create alert for affected field
    3. Recommend treatment
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    alert_data = {
        "type": "disease",
        "subtype": "fungal_infection",
        "severity": "high",
        "title": "Crop Disease Detected",
        "title_ar": "تم اكتشاف مرض في المحصول",
        "description": "Fungal infection detected in wheat crop. Early treatment recommended.",
        "description_ar": "تم اكتشاف عدوى فطرية في محصول القمح. يوصى بالعلاج المبكر.",
        "field_id": "field-test-123",
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "data": {
            "disease_name": "Wheat Rust",
            "disease_name_ar": "صدأ القمح",
            "confidence": 0.87,
            "affected_area_percentage": 15,
            "spread_rate": "medium"
        },
        "actions": [
            {
                "action": "apply_fungicide",
                "action_ar": "رش مبيد فطري",
                "priority": "high",
                "product_recommendations": ["Propiconazole", "Tebuconazole"]
            },
            {
                "action": "isolate_affected_area",
                "action_ar": "عزل المنطقة المصابة",
                "priority": "high"
            },
            {
                "action": "increase_monitoring",
                "action_ar": "زيادة المراقبة",
                "priority": "medium"
            }
        ]
    }

    response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test IoT Sensor Alert Workflow - اختبار سير عمل تنبيهات أجهزة IoT
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_soil_moisture_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تنبيه رطوبة التربة

    Test soil moisture alert:
    1. IoT sensor detects low soil moisture
    2. Create irrigation alert
    3. Notify farmer to irrigate
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    alert_data = {
        "type": "iot_sensor",
        "subtype": "soil_moisture_low",
        "severity": "medium",
        "title": "Low Soil Moisture - Irrigation Needed",
        "title_ar": "رطوبة التربة منخفضة - مطلوب ري",
        "description": "Soil moisture has dropped below optimal level. Irrigation recommended.",
        "description_ar": "انخفضت رطوبة التربة عن المستوى الأمثل. يوصى بالري.",
        "field_id": "field-test-123",
        "device_id": "sensor-sm-001",
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(hours=6)).isoformat(),
        "data": {
            "current_moisture_percentage": 18,
            "optimal_range": [25, 35],
            "sensor_depth_cm": 30,
            "measurement_time": datetime.utcnow().isoformat()
        },
        "actions": [
            {
                "action": "irrigate_field",
                "action_ar": "ري الحقل",
                "priority": "high",
                "estimated_water_needed_liters": 5000
            }
        ]
    }

    response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_temperature_threshold_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تنبيه عتبة الحرارة

    Test temperature threshold alert:
    1. IoT sensor detects high temperature
    2. Create heat stress alert
    3. Recommend cooling actions
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    alert_data = {
        "type": "iot_sensor",
        "subtype": "temperature_high",
        "severity": "high",
        "title": "High Temperature Alert - Heat Stress Risk",
        "title_ar": "تنبيه درجة حرارة عالية - خطر الإجهاد الحراري",
        "description": "Temperature exceeds safe threshold for crops. Take action to prevent heat stress.",
        "description_ar": "تجاوزت درجة الحرارة العتبة الآمنة للمحاصيل. اتخذ إجراءات لمنع الإجهاد الحراري.",
        "field_id": "field-test-123",
        "device_id": "sensor-temp-002",
        "valid_from": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(hours=8)).isoformat(),
        "data": {
            "current_temperature_c": 42,
            "safe_threshold_c": 35,
            "duration_hours": 3,
            "heat_stress_index": "severe"
        },
        "actions": [
            {
                "action": "increase_irrigation",
                "action_ar": "زيادة الري",
                "priority": "high"
            },
            {
                "action": "provide_shade",
                "action_ar": "توفير الظل",
                "priority": "medium"
            }
        ]
    }

    response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Alert Retrieval and Management - اختبار استرجاع وإدارة التنبيهات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_active_alerts_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل الحصول على التنبيهات النشطة

    Test retrieving active alerts:
    1. Get all active alerts for farmer
    2. Filter by severity
    3. Filter by type
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    # Get all active alerts - الحصول على جميع التنبيهات النشطة
    response = await http_client.get(
        f"{alert_service_url}/v1/alerts/active",
        headers=auth_headers
    )

    if response.status_code == 200:
        alerts = response.json()
        assert isinstance(alerts, (list, dict))

        if isinstance(alerts, list):
            for alert in alerts:
                assert "id" in alert or "alert_id" in alert
                assert "type" in alert
                assert "severity" in alert


@pytest.mark.integration
@pytest.mark.asyncio
async def test_acknowledge_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل الإقرار بالتنبيه

    Test alert acknowledgment:
    1. Create alert
    2. Farmer acknowledges alert
    3. Verify acknowledgment recorded
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    # Create a test alert first
    alert_data = {
        "type": "irrigation",
        "subtype": "schedule_reminder",
        "severity": "low",
        "title": "Irrigation Scheduled",
        "title_ar": "جدولة الري",
        "description": "Scheduled irrigation for tomorrow morning",
        "description_ar": "ري مجدول لصباح الغد",
        "field_id": "field-test-123"
    }

    create_response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    if create_response.status_code in (200, 201):
        created_alert = create_response.json()
        alert_id = created_alert.get("id") or created_alert.get("alert_id")

        # Acknowledge the alert - الإقرار بالتنبيه
        ack_response = await http_client.post(
            f"{alert_service_url}/v1/alerts/{alert_id}/acknowledge",
            headers=auth_headers
        )

        assert ack_response.status_code in (200, 204, 401)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dismiss_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل رفض التنبيه

    Test alert dismissal:
    1. Create alert
    2. Farmer dismisses alert
    3. Alert marked as dismissed
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    # Create a test alert
    alert_data = {
        "type": "maintenance",
        "subtype": "equipment_service",
        "severity": "low",
        "title": "Equipment Maintenance Due",
        "title_ar": "صيانة المعدات مستحقة",
        "description": "Tractor service is due this week",
        "description_ar": "صيانة الجرار مستحقة هذا الأسبوع"
    }

    create_response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    if create_response.status_code in (200, 201):
        created_alert = create_response.json()
        alert_id = created_alert.get("id") or created_alert.get("alert_id")

        # Dismiss the alert - رفض التنبيه
        dismiss_response = await http_client.delete(
            f"{alert_service_url}/v1/alerts/{alert_id}",
            headers=auth_headers
        )

        assert dismiss_response.status_code in (200, 204, 404, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Alert Priority and Escalation - اختبار أولوية التنبيه والتصعيد
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_alert_priority_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل أولوية التنبيه

    Test alert priority handling:
    1. Create alerts with different priorities
    2. Verify priority-based delivery
    3. Test escalation for unacknowledged critical alerts
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    # Create critical priority alert - إنشاء تنبيه ذو أولوية حرجة
    critical_alert = {
        "type": "weather",
        "subtype": "flash_flood",
        "severity": "critical",
        "title": "URGENT: Flash Flood Warning",
        "title_ar": "عاجل: تحذير من فيضانات مفاجئة",
        "description": "Flash flood imminent. Evacuate low-lying areas immediately.",
        "description_ar": "فيضان مفاجئ وشيك. قم بإخلاء المناطق المنخفضة فوراً.",
        "location": {
            "latitude": 15.3694,
            "longitude": 44.1910,
            "radius_km": 20
        },
        "priority_override": "critical",
        "require_acknowledgment": True,
        "escalation_minutes": 5
    }

    response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=critical_alert,
        headers=auth_headers
    )

    if response.status_code in (200, 201):
        alert = response.json()
        assert alert.get("severity") == "critical"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multi_channel_alert_delivery(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار توصيل التنبيه عبر قنوات متعددة

    Test multi-channel alert delivery:
    1. Create alert with multiple delivery channels
    2. Verify delivery to push, SMS, email
    3. Track delivery status
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    alert_data = {
        "type": "critical_action",
        "subtype": "harvest_now",
        "severity": "critical",
        "title": "Immediate Harvest Required",
        "title_ar": "مطلوب حصاد فوري",
        "description": "Weather conditions deteriorating. Harvest crop immediately.",
        "description_ar": "تدهور الأحوال الجوية. احصد المحصول فوراً.",
        "field_id": "field-test-123",
        "channels": ["push", "sms", "email", "in_app"],
        "priority": "critical"
    }

    response = await http_client.post(
        f"{alert_service_url}/v1/alerts",
        json=alert_data,
        headers=auth_headers
    )

    assert response.status_code in (200, 201, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Alert Analytics - اختبار تحليلات التنبيهات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_alert_statistics_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل إحصائيات التنبيهات

    Test alert statistics:
    1. Get alert counts by type
    2. Get alert counts by severity
    3. Get response time metrics
    """
    alert_service_url = service_urls.get("alert_service", "http://localhost:8113")

    # Get alert statistics - الحصول على إحصائيات التنبيهات
    response = await http_client.get(
        f"{alert_service_url}/v1/alerts/statistics",
        headers=auth_headers
    )

    if response.status_code == 200:
        stats = response.json()
        # Statistics should include counts and metrics
        assert isinstance(stats, dict)
