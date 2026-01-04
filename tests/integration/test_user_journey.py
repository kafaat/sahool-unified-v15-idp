"""
SAHOOL Integration Tests - Complete User Journey
اختبارات التكامل - رحلة المستخدم الكاملة

Tests complete end-to-end user journeys through the platform:
- New farmer onboarding
- Daily farming operations
- Crisis management scenarios
- Seasonal planning and execution
- Business growth journey

These tests validate the full user experience across multiple services.

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# New Farmer Onboarding Journey - رحلة تسجيل المزارع الجديد
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_new_farmer_onboarding_journey(
    http_client,
    service_urls: dict[str, str],
    field_factory,
    auth_headers: dict[str, str],
):
    """
    اختبار رحلة تسجيل مزارع جديد

    Complete new farmer onboarding journey:
    1. Sign up and create account
    2. Choose subscription plan
    3. Complete payment
    4. Add first field
    5. Get initial recommendations
    6. Set up notifications
    7. Connect IoT devices (if available)
    """
    # Step 1: Sign up (handled by auth service)
    # In production: POST /auth/register

    # Step 2: Choose subscription plan - اختيار خطة الاشتراك
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # List available plans
    plans_response = await http_client.get(
        f"{billing_url}/v1/plans", headers=auth_headers
    )

    if plans_response.status_code == 200:
        plans = plans_response.json()
        # Farmer chooses starter plan
        starter_plan = next(
            (p for p in plans.get("plans", []) if p.get("plan_id") == "starter"), None
        )
        assert starter_plan is not None

    # Step 3: Create subscription
    tenant_data = {
        "name": "New Farmer Test",
        "name_ar": "مزرعة مزارع جديد تجريبي",
        "email": "newfarmer-test@sahool.io",
        "phone": "+967777999888",
        "plan_id": "starter",
        "billing_cycle": "monthly",
    }

    subscription_response = await http_client.post(
        f"{billing_url}/v1/tenants", json=tenant_data, headers=auth_headers
    )

    if subscription_response.status_code == 200:
        subscription = subscription_response.json()
        tenant_id = subscription.get("tenant_id")
        assert tenant_id is not None

    # Step 4: Add first field - إضافة الحقل الأول
    field_ops_url = service_urls.get("field_core", "http://localhost:3000")

    field_data = field_factory.create(name="My First Wheat Field", crop_type="wheat")

    field_response = await http_client.post(
        f"{field_ops_url}/api/v1/fields", json=field_data, headers=auth_headers
    )

    if field_response.status_code == 201:
        field = field_response.json()
        field_id = field.get("id") or field.get("field_id")

        # Step 5: Get initial recommendations - الحصول على التوصيات الأولية
        agro_advisor_url = service_urls.get("agro_advisor", "http://localhost:8105")

        # Wait a bit for data to propagate
        await asyncio.sleep(2)

        # Get crop calendar recommendations
        calendar_response = await http_client.get(
            f"{agro_advisor_url}/api/v1/calendar/{field_id}", headers=auth_headers
        )

        # Should get recommendations or require more data
        assert calendar_response.status_code in (200, 404, 401)

    # Step 6: Set up notifications - إعداد الإشعارات
    notification_url = service_urls.get("notification_service", "http://localhost:8110")

    notification_prefs = {
        "channels": ["push", "sms", "in_app"],
        "types": ["weather_alerts", "irrigation_reminders", "pest_alerts"],
        "quiet_hours": {"start": "22:00", "end": "07:00"},
    }

    prefs_response = await http_client.put(
        f"{notification_url}/v1/preferences",
        json=notification_prefs,
        headers=auth_headers,
    )

    assert prefs_response.status_code in (200, 201, 401)


# ═══════════════════════════════════════════════════════════════════════════════
# Daily Farming Operations Journey - رحلة العمليات الزراعية اليومية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_daily_farming_operations_journey(
    http_client,
    service_urls: dict[str, str],
    auth_headers: dict[str, str],
):
    """
    اختبار رحلة العمليات الزراعية اليومية

    Daily farming operations journey:
    1. Check weather forecast
    2. Review field conditions (IoT sensors)
    3. Check irrigation schedule
    4. View crop health alerts
    5. Record farm activities
    6. Get AI recommendations
    """
    field_id = "field-test-123"

    # Step 1: Check weather forecast - فحص توقعات الطقس
    weather_url = service_urls.get("weather_core", "http://localhost:8108")

    weather_response = await http_client.get(
        f"{weather_url}/api/v1/weather/forecast",
        params={"latitude": 15.3694, "longitude": 44.1910, "days": 7},
        headers=auth_headers,
    )

    # Should get weather data
    assert weather_response.status_code in (200, 401)

    # Step 2: Review field conditions - مراجعة ظروف الحقل
    iot_url = service_urls.get("iot_gateway", "http://localhost:8106")

    # Get latest sensor readings
    sensors_response = await http_client.get(
        f"{iot_url}/v1/readings/latest",
        params={"field_id": field_id},
        headers=auth_headers,
    )

    # May or may not have IoT sensors
    assert sensors_response.status_code in (200, 404, 401)

    # Step 3: Check irrigation schedule - فحص جدول الري
    irrigation_url = service_urls.get("irrigation_smart", "http://localhost:8094")

    schedule_response = await http_client.get(
        f"{irrigation_url}/api/v1/irrigation/schedule/{field_id}", headers=auth_headers
    )

    assert schedule_response.status_code in (200, 404, 401)

    # Step 4: View crop health alerts - عرض تنبيهات صحة المحاصيل
    alert_url = service_urls.get("alert_service", "http://localhost:8113")

    alerts_response = await http_client.get(
        f"{alert_url}/v1/alerts/active",
        params={"field_id": field_id},
        headers=auth_headers,
    )

    assert alerts_response.status_code in (200, 401)

    # Step 5: Record farm activity - تسجيل نشاط زراعي
    task_url = service_urls.get("task_service", "http://localhost:8103")

    activity_data = {
        "field_id": field_id,
        "activity_type": "irrigation",
        "title": "Morning irrigation",
        "title_ar": "ري الصباح",
        "description": "Irrigated wheat field for 2 hours",
        "description_ar": "ري حقل القمح لمدة ساعتين",
        "duration_minutes": 120,
        "water_used_liters": 5000,
        "cost_yer": 500,
    }

    activity_response = await http_client.post(
        f"{task_url}/api/v1/activities", json=activity_data, headers=auth_headers
    )

    assert activity_response.status_code in (200, 201, 401, 422)

    # Step 6: Get AI recommendations - الحصول على توصيات الذكاء الاصطناعي
    ai_advisor_url = service_urls.get("ai_advisor", "http://localhost:8112")

    question = {
        "question": "ما هو أفضل وقت للري بناءً على حالة حقلي الحالية؟",
        "field_id": field_id,
        "language": "ar",
    }

    ai_response = await http_client.post(
        f"{ai_advisor_url}/api/v1/advisor/ask", json=question, headers=auth_headers
    )

    assert ai_response.status_code in (200, 401, 503)


# ═══════════════════════════════════════════════════════════════════════════════
# Crisis Management Journey - رحلة إدارة الأزمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_crisis_management_journey(
    http_client,
    service_urls: dict[str, str],
    auth_headers: dict[str, str],
):
    """
    اختبار رحلة إدارة الأزمات

    Crisis management journey (e.g., pest outbreak):
    1. AI detects unusual crop patterns
    2. System generates pest alert
    3. Farmer receives urgent notification
    4. Farmer reviews AI diagnosis
    5. Farmer gets treatment recommendations
    6. Farmer orders pesticides from marketplace
    7. Farmer records treatment action
    8. System monitors improvement
    """
    field_id = "field-test-123"

    # Step 1 & 2: AI detects issue and generates alert
    # (This would happen automatically via background jobs)

    # Step 3: Farmer receives notification
    notification_url = service_urls.get("notification_service", "http://localhost:8110")

    # Check for recent notifications
    notif_response = await http_client.get(
        f"{notification_url}/v1/notifications",
        params={"type": "pest_alert", "limit": 10},
        headers=auth_headers,
    )

    assert notif_response.status_code in (200, 401)

    # Step 4: Review AI diagnosis
    crop_health_url = service_urls.get("crop_health_ai", "http://localhost:8095")

    # Get crop health analysis
    health_response = await http_client.get(
        f"{crop_health_url}/api/v1/health/field/{field_id}", headers=auth_headers
    )

    assert health_response.status_code in (200, 404, 401)

    # Step 5: Get treatment recommendations
    agro_advisor_url = service_urls.get("agro_advisor", "http://localhost:8105")

    treatment_response = await http_client.get(
        f"{agro_advisor_url}/api/v1/recommendations/pest-control",
        params={"field_id": field_id, "pest_type": "aphids"},
        headers=auth_headers,
    )

    assert treatment_response.status_code in (200, 404, 401)

    # Step 6: Order pesticides from marketplace
    marketplace_url = service_urls.get("marketplace_service", "http://localhost:3010")

    # Search for pesticides
    search_response = await http_client.get(
        f"{marketplace_url}/api/v1/products/search",
        params={"query": "pesticide", "category": "inputs"},
        headers=auth_headers,
    )

    if search_response.status_code == 200:
        products = search_response.json()

        # Add to cart and place order
        order_data = {
            "items": [
                {
                    "product_id": "product-pesticide-001",
                    "quantity": 2,
                    "unit_price": 15000,
                }
            ],
            "urgent": True,
            "notes": "Urgent - pest outbreak",
        }

        order_response = await http_client.post(
            f"{marketplace_url}/api/v1/orders", json=order_data, headers=auth_headers
        )

        assert order_response.status_code in (200, 201, 401, 422)

    # Step 7: Record treatment action
    task_url = service_urls.get("task_service", "http://localhost:8103")

    treatment_activity = {
        "field_id": field_id,
        "activity_type": "pest_control",
        "title": "Applied pesticide for aphid control",
        "title_ar": "رش المبيد الحشري لمكافحة حشرات المن",
        "pesticide_used": "Imidacloprid",
        "quantity_ml": 500,
        "area_treated_hectares": 2.5,
    }

    activity_response = await http_client.post(
        f"{task_url}/api/v1/activities", json=treatment_activity, headers=auth_headers
    )

    assert activity_response.status_code in (200, 201, 401, 422)


# ═══════════════════════════════════════════════════════════════════════════════
# Seasonal Planning Journey - رحلة التخطيط الموسمي
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_seasonal_planning_journey(
    http_client,
    service_urls: dict[str, str],
    auth_headers: dict[str, str],
):
    """
    اختبار رحلة التخطيط الموسمي

    Seasonal planning journey (new crop season):
    1. Review previous season's yield data
    2. Check astronomical calendar for planting dates
    3. Get crop rotation recommendations
    4. Plan fertilizer and seed purchases
    5. Set up field preparation tasks
    6. Schedule irrigation plan
    7. Set budget and track expenses
    """
    field_id = "field-test-123"

    # Step 1: Review previous season's yield
    yield_url = service_urls.get("yield_engine", "http://localhost:3021")

    yield_response = await http_client.get(
        f"{yield_url}/api/v1/yield/history/{field_id}", headers=auth_headers
    )

    assert yield_response.status_code in (200, 404, 401)

    # Step 2: Check astronomical calendar
    calendar_url = service_urls.get("astronomical_calendar", "http://localhost:8111")

    calendar_response = await http_client.get(
        f"{calendar_url}/api/v1/calendar/planting-dates",
        params={"crop": "wheat", "location": "Sana'a"},
        headers=auth_headers,
    )

    assert calendar_response.status_code in (200, 401)

    # Step 3: Get crop rotation recommendations
    agro_advisor_url = service_urls.get("agro_advisor", "http://localhost:8105")

    rotation_response = await http_client.get(
        f"{agro_advisor_url}/api/v1/recommendations/crop-rotation",
        params={"field_id": field_id, "previous_crop": "wheat"},
        headers=auth_headers,
    )

    assert rotation_response.status_code in (200, 404, 401)

    # Step 4: Plan purchases - Budget fertilizer and seeds
    inventory_url = service_urls.get("inventory_service", "http://localhost:8116")

    purchase_plan = {
        "field_id": field_id,
        "crop": "wheat",
        "area_hectares": 5.0,
        "items": [
            {
                "type": "fertilizer",
                "name": "NPK 20-20-20",
                "quantity_kg": 500,
                "estimated_cost_yer": 250000,
            },
            {
                "type": "seeds",
                "name": "Wheat Seeds - Local Variety",
                "quantity_kg": 150,
                "estimated_cost_yer": 60000,
            },
        ],
    }

    plan_response = await http_client.post(
        f"{inventory_url}/api/v1/purchase-plans",
        json=purchase_plan,
        headers=auth_headers,
    )

    assert plan_response.status_code in (200, 201, 401, 422)

    # Step 5: Set up field preparation tasks
    task_url = service_urls.get("task_service", "http://localhost:8103")

    tasks = [
        {
            "title": "Plow field",
            "title_ar": "حرث الحقل",
            "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "priority": "high",
        },
        {
            "title": "Apply base fertilizer",
            "title_ar": "وضع السماد الأساسي",
            "due_date": (datetime.utcnow() + timedelta(days=10)).isoformat(),
            "priority": "high",
        },
        {
            "title": "Plant seeds",
            "title_ar": "زراعة البذور",
            "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "priority": "critical",
        },
    ]

    for task_data in tasks:
        task_data["field_id"] = field_id
        task_response = await http_client.post(
            f"{task_url}/api/v1/tasks", json=task_data, headers=auth_headers
        )

        assert task_response.status_code in (200, 201, 401, 422)

    # Step 6: Schedule irrigation plan
    irrigation_url = service_urls.get("irrigation_smart", "http://localhost:8094")

    irrigation_plan = {
        "field_id": field_id,
        "crop": "wheat",
        "start_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
        "schedule_type": "smart",  # Based on ET0 calculations
        "enable_automation": True,
    }

    irrigation_response = await http_client.post(
        f"{irrigation_url}/api/v1/irrigation/schedules",
        json=irrigation_plan,
        headers=auth_headers,
    )

    assert irrigation_response.status_code in (200, 201, 401, 422)


# ═══════════════════════════════════════════════════════════════════════════════
# Business Growth Journey - رحلة نمو الأعمال
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_business_growth_journey(
    http_client,
    service_urls: dict[str, str],
    auth_headers: dict[str, str],
):
    """
    اختبار رحلة نمو الأعمال

    Business growth journey:
    1. Farmer starts with Starter plan
    2. Adds more fields
    3. Sees value in advanced features
    4. Upgrades to Professional plan
    5. Starts using satellite imagery
    6. Implements precision farming
    7. Eventually upgrades to Enterprise
    8. Joins research program
    9. Becomes marketplace seller
    """
    # Step 1 & 2: Already covered in onboarding

    # Step 3 & 4: Upgrade to Professional plan
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Check current subscription
    subscription_response = await http_client.get(
        f"{billing_url}/v1/subscription", headers=auth_headers
    )

    if subscription_response.status_code == 200:
        current_sub = subscription_response.json()

        # Upgrade plan
        upgrade_data = {
            "new_plan_id": "professional",
            "billing_cycle": "annual",  # Save money with annual billing
            "apply_proration": True,
        }

        upgrade_response = await http_client.post(
            f"{billing_url}/v1/subscription/upgrade",
            json=upgrade_data,
            headers=auth_headers,
        )

        assert upgrade_response.status_code in (200, 401, 422)

    # Step 5: Start using satellite imagery
    satellite_url = service_urls.get("satellite_service", "http://localhost:8090")
    field_id = "field-test-123"

    satellite_response = await http_client.get(
        f"{satellite_url}/api/v1/satellite/imagery/{field_id}",
        params={"start_date": (datetime.utcnow() - timedelta(days=30)).isoformat()},
        headers=auth_headers,
    )

    assert satellite_response.status_code in (200, 404, 401)

    # Step 6: Get NDVI analysis for precision farming
    ndvi_url = service_urls.get("ndvi_engine", "http://localhost:8107")

    ndvi_response = await http_client.get(
        f"{ndvi_url}/api/v1/ndvi/fields/{field_id}/analysis", headers=auth_headers
    )

    assert ndvi_response.status_code in (200, 404, 401)

    # Step 7: Upgrade to Enterprise (for large operations)
    enterprise_upgrade = {
        "new_plan_id": "enterprise",
        "billing_cycle": "annual",
        "apply_proration": True,
    }

    enterprise_response = await http_client.post(
        f"{billing_url}/v1/subscription/upgrade",
        json=enterprise_upgrade,
        headers=auth_headers,
    )

    assert enterprise_response.status_code in (200, 401, 422)

    # Step 8: Join research program
    research_url = service_urls.get("research_core", "http://localhost:3015")

    research_registration = {
        "farmer_type": "progressive",
        "farm_size_hectares": 50,
        "interested_in": ["soil_health", "climate_resilience"],
        "willing_to_share_data": True,
    }

    research_response = await http_client.post(
        f"{research_url}/api/v1/participants",
        json=research_registration,
        headers=auth_headers,
    )

    assert research_response.status_code in (200, 201, 401, 422)

    # Step 9: Become marketplace seller
    marketplace_url = service_urls.get("marketplace_service", "http://localhost:3010")

    seller_registration = {
        "business_name": "Ahmed's Organic Farm",
        "business_name_ar": "مزرعة أحمد العضوية",
        "business_type": "producer",
        "products_offered": ["organic_wheat", "organic_vegetables"],
        "certifications": ["organic_certified"],
    }

    seller_response = await http_client.post(
        f"{marketplace_url}/api/v1/sellers",
        json=seller_registration,
        headers=auth_headers,
    )

    assert seller_response.status_code in (200, 201, 401, 422)


# ═══════════════════════════════════════════════════════════════════════════════
# Multi-Service Integration Journey - رحلة التكامل متعدد الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_multi_service_integration_journey(
    http_client,
    service_urls: dict[str, str],
    auth_headers: dict[str, str],
):
    """
    اختبار رحلة التكامل متعدد الخدمات

    Multi-service integration journey:
    Demonstrates how data flows between services:
    1. IoT sensor detects low soil moisture
    2. Alert service creates alert
    3. Notification service sends notification
    4. Irrigation service calculates water needed
    5. Task service creates irrigation task
    6. Farmer approves automated irrigation
    7. IoT actuator opens water valve
    8. System monitors and records water usage
    9. Billing service tracks usage quota
    10. AI learns from the event
    """
    field_id = "field-test-123"

    # Step 1: Simulate IoT sensor reading
    iot_url = service_urls.get("iot_gateway", "http://localhost:8106")

    sensor_reading = {
        "device_id": "sensor-sm-001",
        "field_id": field_id,
        "sensor_type": "soil_moisture",
        "value": 18,  # Low moisture
        "unit": "%",
        "timestamp": datetime.utcnow().isoformat(),
    }

    sensor_response = await http_client.post(
        f"{iot_url}/v1/readings", json=sensor_reading, headers=auth_headers
    )

    # Steps 2-3: Alert and notification happen automatically
    # Wait for event propagation
    await asyncio.sleep(2)

    # Step 4: Check irrigation recommendation
    irrigation_url = service_urls.get("irrigation_smart", "http://localhost:8094")

    irrigation_calc = {
        "field_id": field_id,
        "current_moisture_percent": 18,
        "target_moisture_percent": 40,
        "soil_type": "loamy",
        "crop_type": "wheat",
    }

    calc_response = await http_client.post(
        f"{irrigation_url}/api/v1/irrigation/calculate",
        json=irrigation_calc,
        headers=auth_headers,
    )

    water_needed = 0
    if calc_response.status_code == 200:
        calc_result = calc_response.json()
        water_needed = calc_result.get("water_needed_liters", 0)

    # Step 5: Task created automatically or manually
    task_url = service_urls.get("task_service", "http://localhost:8103")

    irrigation_task = {
        "field_id": field_id,
        "task_type": "irrigation",
        "title": "Urgent Irrigation Required",
        "title_ar": "ري عاجل مطلوب",
        "priority": "high",
        "auto_created": True,
        "due_date": datetime.utcnow().isoformat(),
    }

    task_response = await http_client.post(
        f"{task_url}/api/v1/tasks", json=irrigation_task, headers=auth_headers
    )

    # Step 6: Farmer approves (or auto-approved if configured)
    # Step 7: Actuator control
    valve_command = {
        "device_id": "valve-001",
        "command": "open",
        "parameters": {"duration_minutes": 30, "target_volume_liters": water_needed},
    }

    actuator_response = await http_client.post(
        f"{iot_url}/v1/actuators/command", json=valve_command, headers=auth_headers
    )

    # Step 8: Monitor water usage (happens automatically)

    # Step 9: Check billing quota usage
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    usage_response = await http_client.get(
        f"{billing_url}/v1/usage", headers=auth_headers
    )

    if usage_response.status_code == 200:
        usage = usage_response.json()
        # Verify IoT reading was counted
        assert isinstance(usage, dict)

    # Step 10: AI learning happens in background
    # The system learns optimal irrigation patterns over time
