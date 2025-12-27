"""
SAHOOL Integration Tests - Notification Workflow
اختبارات التكامل - سير عمل الإشعارات

Tests complete notification workflow including:
- Sending notifications
- Recording notifications
- Retrieving farmer notifications
- Weather alerts
- Pest outbreak alerts
- Irrigation reminders

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime, date, timedelta


# ═══════════════════════════════════════════════════════════════════════════════
# Test Notification Creation - اختبار إنشاء الإشعارات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_notification_workflow(
    http_client,
    service_urls: Dict[str, str],
    notification_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل إنشاء إشعار

    Test notification creation:
    1. Create a custom notification
    2. Verify notification is created
    3. Check notification structure
    """
    # Arrange - إعداد بيانات الاختبار
    notification_url = service_urls.get("notification_service", "http://localhost:8110")

    notification_data = notification_factory.create(
        user_id="test-farmer-123",
        notification_type="weather_alert"
    )

    # Convert to API format
    api_data = {
        "type": "weather_alert",
        "priority": "high",
        "title": notification_data["title"],
        "title_ar": notification_data["title_ar"],
        "body": notification_data["message"],
        "body_ar": notification_data["message_ar"],
        "data": {},
        "target_farmers": ["test-farmer-123"],
        "channels": ["push", "in_app"],
        "expires_in_hours": 24
    }

    # Act - إنشاء الإشعار
    response = await http_client.post(
        f"{notification_url}/v1/notifications",
        json=api_data,
        headers=auth_headers
    )

    # Assert - التحقق من النتائج
    assert response.status_code == 200, f"Failed to create notification: {response.text}"

    created_notification = response.json()

    # Verify notification structure
    assert "id" in created_notification
    assert created_notification["type"] == "weather_alert"
    assert created_notification["priority"] == "high"
    assert created_notification["title"] == api_data["title"]
    assert created_notification["title_ar"] == api_data["title_ar"]
    assert created_notification["type_ar"] is not None  # Should have Arabic translation
    assert created_notification["priority_ar"] is not None
    assert "created_at" in created_notification
    assert "expires_at" in created_notification


@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تنبيه الطقس

    Test weather alert workflow:
    1. Create weather alert for governorates
    2. Verify alert is created
    3. Check targeting by governorate
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")

    # Create weather alert - إنشاء تنبيه طقس
    weather_alert = {
        "governorates": ["sanaa", "ibb"],
        "alert_type": "frost",  # frost, heat_wave, storm, flood, drought
        "severity": "high",
        "expected_date": (date.today() + timedelta(days=1)).isoformat(),
        "details": {
            "temperature_min": -2,
            "temperature_max": 10,
            "description": "Frost expected tonight"
        }
    }

    # Act - إرسال تنبيه الطقس
    response = await http_client.post(
        f"{notification_url}/v1/alerts/weather",
        json=weather_alert,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 200, f"Failed to create weather alert: {response.text}"

    alert = response.json()

    # Verify weather alert structure
    assert alert["type"] == "weather_alert"
    assert alert["priority"] == "high"
    assert "sanaa" in [g for g in alert["target_governorates"]]
    assert "ibb" in [g for g in alert["target_governorates"]]
    assert alert["data"]["alert_type"] == "frost"
    assert "expected_date" in alert["data"]

    # Verify Arabic translations are present
    assert alert["title_ar"] is not None
    assert "صقيع" in alert["title_ar"] or "تحذير" in alert["title_ar"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pest_outbreak_alert_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تنبيه انتشار الآفات

    Test pest outbreak alert:
    1. Create pest alert
    2. Verify targeting by crop type
    3. Check recommendations
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")

    # Create pest alert - إنشاء تنبيه آفات
    pest_alert = {
        "governorate": "taiz",
        "pest_name": "Tomato Blight",
        "pest_name_ar": "آفة الطماطم",
        "affected_crops": ["tomato"],
        "severity": "critical",
        "recommendations": [
            "Remove infected plants immediately",
            "Apply appropriate fungicide",
            "Improve air circulation"
        ],
        "recommendations_ar": [
            "قم بإزالة النباتات المصابة فوراً",
            "استخدم مبيد فطري مناسب",
            "حسّن دوران الهواء"
        ]
    }

    # Act - إرسال تنبيه الآفات
    response = await http_client.post(
        f"{notification_url}/v1/alerts/pest",
        json=pest_alert,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 200, f"Failed to create pest alert: {response.text}"

    alert = response.json()

    # Verify pest alert structure
    assert alert["type"] == "pest_outbreak"
    assert alert["priority"] == "critical"
    assert alert["target_governorates"] == ["taiz"]
    assert "tomato" in alert["target_crops"]
    assert alert["data"]["pest_name"] == "Tomato Blight"
    assert alert["data"]["pest_name_ar"] == "آفة الطماطم"
    assert len(alert["data"]["recommendations"]) == 3
    assert len(alert["data"]["recommendations_ar"]) == 3


@pytest.mark.integration
@pytest.mark.asyncio
async def test_irrigation_reminder_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تذكير الري

    Test irrigation reminder:
    1. Create irrigation reminder for specific farmer
    2. Verify farmer targeting
    3. Check field details
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")

    # Create irrigation reminder - إنشاء تذكير ري
    irrigation_reminder = {
        "farmer_id": "test-farmer-456",
        "field_id": "field-789",
        "field_name": "North Field",
        "crop": "wheat",
        "water_needed_mm": 25.5,
        "urgency": "medium"
    }

    # Act - إرسال تذكير الري
    response = await http_client.post(
        f"{notification_url}/v1/reminders/irrigation",
        json=irrigation_reminder,
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 200, f"Failed to create irrigation reminder: {response.text}"

    reminder = response.json()

    # Verify irrigation reminder structure
    assert reminder["type"] == "irrigation_reminder"
    assert reminder["priority"] == "medium"
    assert reminder["target_farmers"] == ["test-farmer-456"]
    assert reminder["data"]["field_id"] == "field-789"
    assert reminder["data"]["field_name"] == "North Field"
    assert reminder["data"]["crop"] == "wheat"
    assert reminder["data"]["water_needed_mm"] == 25.5

    # Verify message contains water amount
    assert "25.5" in reminder["body_ar"]


# ═══════════════════════════════════════════════════════════════════════════════
# Test Farmer Notification Retrieval - اختبار استرجاع إشعارات المزارع
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_farmer_notification_retrieval_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل استرجاع إشعارات المزارع

    Test farmer notification retrieval:
    1. Register farmer
    2. Create notifications for farmer
    3. Retrieve farmer's notifications
    4. Verify filtering and sorting
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")
    farmer_id = f"test-farmer-{datetime.utcnow().timestamp()}"

    # Step 1: Register farmer - تسجيل المزارع
    farmer_profile = {
        "farmer_id": farmer_id,
        "name": "Ahmed Integration Test",
        "name_ar": "أحمد اختبار التكامل",
        "governorate": "sanaa",
        "district": "Bani Hushaysh",
        "crops": ["wheat", "tomato"],
        "field_ids": ["field-1", "field-2"],
        "phone": "+967771234567",
        "notification_channels": ["push", "in_app"],
        "language": "ar"
    }

    register_response = await http_client.post(
        f"{notification_url}/v1/farmers/register",
        json=farmer_profile,
        headers=auth_headers
    )

    assert register_response.status_code == 200
    registration = register_response.json()
    assert registration["success"] is True

    # Step 2: Create multiple notifications - إنشاء إشعارات متعددة
    notifications_created = []

    # Create weather alert
    weather_data = {
        "type": "weather_alert",
        "priority": "high",
        "title": "Rain Expected",
        "title_ar": "أمطار متوقعة",
        "body": "Heavy rain expected tomorrow",
        "body_ar": "أمطار غزيرة متوقعة غداً",
        "target_governorates": ["sanaa"],
        "channels": ["push", "in_app"]
    }

    weather_response = await http_client.post(
        f"{notification_url}/v1/notifications",
        json=weather_data,
        headers=auth_headers
    )
    if weather_response.status_code == 200:
        notifications_created.append(weather_response.json())

    # Create crop health notification
    crop_data = {
        "type": "crop_health",
        "priority": "medium",
        "title": "Crop Health Check",
        "title_ar": "فحص صحة المحصول",
        "body": "Check your wheat field for signs of disease",
        "body_ar": "تحقق من حقل القمح للكشف عن علامات المرض",
        "target_crops": ["wheat"],
        "channels": ["in_app"]
    }

    crop_response = await http_client.post(
        f"{notification_url}/v1/notifications",
        json=crop_data,
        headers=auth_headers
    )
    if crop_response.status_code == 200:
        notifications_created.append(crop_response.json())

    # Step 3: Retrieve farmer notifications - استرجاع إشعارات المزارع
    # Wait a moment for notifications to be processed
    await asyncio.sleep(0.5)

    get_response = await http_client.get(
        f"{notification_url}/v1/notifications/farmer/{farmer_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 200
    farmer_notifications = get_response.json()

    # Verify response structure
    assert "farmer_id" in farmer_notifications
    assert farmer_notifications["farmer_id"] == farmer_id
    assert "total" in farmer_notifications
    assert "unread_count" in farmer_notifications
    assert "notifications" in farmer_notifications
    assert isinstance(farmer_notifications["notifications"], list)

    # Verify notifications are sorted by created_at (newest first)
    if len(farmer_notifications["notifications"]) > 1:
        for i in range(len(farmer_notifications["notifications"]) - 1):
            current = datetime.fromisoformat(
                farmer_notifications["notifications"][i]["created_at"].replace("Z", "+00:00")
            )
            next_notif = datetime.fromisoformat(
                farmer_notifications["notifications"][i + 1]["created_at"].replace("Z", "+00:00")
            )
            assert current >= next_notif, "Notifications should be sorted by created_at descending"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_notification_filtering_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تصفية الإشعارات

    Test notification filtering:
    1. Create notifications of different types
    2. Filter by type
    3. Filter by unread status
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")
    farmer_id = f"filter-test-{datetime.utcnow().timestamp()}"

    # Register farmer
    farmer_profile = {
        "farmer_id": farmer_id,
        "name": "Filter Test Farmer",
        "name_ar": "مزارع اختبار التصفية",
        "governorate": "ibb",
        "crops": ["coffee", "banana"],
        "notification_channels": ["in_app"],
        "language": "ar"
    }

    await http_client.post(
        f"{notification_url}/v1/farmers/register",
        json=farmer_profile,
        headers=auth_headers
    )

    # Create notifications of different types
    notification_types = ["weather_alert", "pest_outbreak", "market_price"]

    for ntype in notification_types:
        notif_data = {
            "type": ntype,
            "priority": "medium",
            "title": f"Test {ntype}",
            "title_ar": f"اختبار {ntype}",
            "body": f"Test notification of type {ntype}",
            "body_ar": f"إشعار اختبار من نوع {ntype}",
            "target_farmers": [farmer_id],
            "channels": ["in_app"]
        }

        await http_client.post(
            f"{notification_url}/v1/notifications",
            json=notif_data,
            headers=auth_headers
        )

    # Wait for processing
    await asyncio.sleep(0.5)

    # Test filtering by type - اختبار التصفية حسب النوع
    for ntype in notification_types:
        filter_response = await http_client.get(
            f"{notification_url}/v1/notifications/farmer/{farmer_id}?type={ntype}",
            headers=auth_headers
        )

        if filter_response.status_code == 200:
            filtered = filter_response.json()

            # All returned notifications should be of the requested type
            for notif in filtered["notifications"]:
                assert notif["type"] == ntype

    # Test filtering by unread - اختبار التصفية حسب غير المقروء
    unread_response = await http_client.get(
        f"{notification_url}/v1/notifications/farmer/{farmer_id}?unread_only=true",
        headers=auth_headers
    )

    if unread_response.status_code == 200:
        unread_data = unread_response.json()
        # All notifications should be unread initially
        for notif in unread_data["notifications"]:
            assert notif["is_read"] is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mark_notification_read_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تحديد الإشعار كمقروء

    Test marking notification as read:
    1. Create notification
    2. Mark as read
    3. Verify read status
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")
    farmer_id = f"read-test-{datetime.utcnow().timestamp()}"

    # Create notification
    notif_data = {
        "type": "system",
        "priority": "low",
        "title": "Read Test",
        "title_ar": "اختبار القراءة",
        "body": "Test notification",
        "body_ar": "إشعار اختبار",
        "target_farmers": [farmer_id],
        "channels": ["in_app"]
    }

    create_response = await http_client.post(
        f"{notification_url}/v1/notifications",
        json=notif_data,
        headers=auth_headers
    )

    assert create_response.status_code == 200
    notification = create_response.json()
    notification_id = notification["id"]

    # Mark as read - تحديد كمقروء
    read_response = await http_client.patch(
        f"{notification_url}/v1/notifications/{notification_id}/read?farmer_id={farmer_id}",
        headers=auth_headers
    )

    assert read_response.status_code == 200
    read_result = read_response.json()

    assert read_result["success"] is True
    assert read_result["notification_id"] == notification_id


# ═══════════════════════════════════════════════════════════════════════════════
# Test Broadcast Notifications - اختبار الإشعارات العامة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_broadcast_notifications_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل الإشعارات العامة (البث)

    Test broadcast notifications:
    1. Create broadcast notification (no specific farmers)
    2. Retrieve broadcast notifications
    3. Filter by governorate and crop
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")

    # Create broadcast notification - إنشاء إشعار عام
    broadcast_data = {
        "type": "market_price",
        "priority": "medium",
        "title": "Wheat Price Update",
        "title_ar": "تحديث سعر القمح",
        "body": "Wheat prices increased by 10% this week",
        "body_ar": "ارتفعت أسعار القمح بنسبة 10٪ هذا الأسبوع",
        "target_governorates": ["sanaa", "dhamar"],
        "target_crops": ["wheat"],
        "channels": ["in_app"],
        "data": {
            "crop": "wheat",
            "old_price": 100,
            "new_price": 110,
            "currency": "YER"
        }
    }

    create_response = await http_client.post(
        f"{notification_url}/v1/notifications",
        json=broadcast_data,
        headers=auth_headers
    )

    assert create_response.status_code == 200

    # Wait for processing
    await asyncio.sleep(0.5)

    # Retrieve broadcast notifications - استرجاع الإشعارات العامة
    broadcast_response = await http_client.get(
        f"{notification_url}/v1/notifications/broadcast",
        headers=auth_headers
    )

    assert broadcast_response.status_code == 200
    broadcasts = broadcast_response.json()

    assert "notifications" in broadcasts
    assert "total" in broadcasts

    # Test filtering by governorate - اختبار التصفية حسب المحافظة
    gov_response = await http_client.get(
        f"{notification_url}/v1/notifications/broadcast?governorate=sanaa",
        headers=auth_headers
    )

    if gov_response.status_code == 200:
        gov_broadcasts = gov_response.json()
        # Verify filtering worked
        for notif in gov_broadcasts["notifications"]:
            if notif["target_governorates"]:
                assert "sanaa" in notif["target_governorates"]

    # Test filtering by crop - اختبار التصفية حسب المحصول
    crop_response = await http_client.get(
        f"{notification_url}/v1/notifications/broadcast?crop=wheat",
        headers=auth_headers
    )

    if crop_response.status_code == 200:
        crop_broadcasts = crop_response.json()
        # Verify filtering worked
        for notif in crop_broadcasts["notifications"]:
            if notif["target_crops"]:
                assert "wheat" in notif["target_crops"]


# ═══════════════════════════════════════════════════════════════════════════════
# Test Notification Preferences - اختبار تفضيلات الإشعارات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_notification_preferences_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تفضيلات الإشعارات

    Test notification preferences:
    1. Register farmer
    2. Update notification preferences
    3. Verify preferences are saved
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")
    farmer_id = f"pref-test-{datetime.utcnow().timestamp()}"

    # Register farmer
    farmer_profile = {
        "farmer_id": farmer_id,
        "name": "Preferences Test",
        "name_ar": "اختبار التفضيلات",
        "governorate": "taiz",
        "crops": ["coffee"],
        "notification_channels": ["push", "in_app"],
        "language": "ar"
    }

    register_response = await http_client.post(
        f"{notification_url}/v1/farmers/register",
        json=farmer_profile,
        headers=auth_headers
    )

    assert register_response.status_code == 200

    # Update preferences - تحديث التفضيلات
    preferences = {
        "farmer_id": farmer_id,
        "weather_alerts": True,
        "pest_alerts": True,
        "irrigation_reminders": False,  # Disable irrigation reminders
        "crop_health_alerts": True,
        "market_prices": False,  # Disable market prices
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "06:00",
        "min_priority": "medium"  # Only medium and above
    }

    pref_response = await http_client.put(
        f"{notification_url}/v1/farmers/{farmer_id}/preferences",
        json=preferences,
        headers=auth_headers
    )

    assert pref_response.status_code == 200
    pref_result = pref_response.json()

    assert pref_result["success"] is True
    assert pref_result["farmer_id"] == farmer_id
    assert "preferences" in pref_result

    # Verify preferences
    saved_prefs = pref_result["preferences"]
    assert saved_prefs["weather_alerts"] is True
    assert saved_prefs["irrigation_reminders"] is False
    assert saved_prefs["market_prices"] is False
    assert saved_prefs["min_priority"] == "medium"


# ═══════════════════════════════════════════════════════════════════════════════
# Test Notification Statistics - اختبار إحصائيات الإشعارات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_notification_statistics_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل إحصائيات الإشعارات

    Test notification statistics:
    1. Get notification statistics
    2. Verify statistics structure
    3. Check counts by type
    """
    # Arrange
    notification_url = service_urls.get("notification_service", "http://localhost:8110")

    # Get statistics - الحصول على الإحصائيات
    stats_response = await http_client.get(
        f"{notification_url}/v1/stats",
        headers=auth_headers
    )

    assert stats_response.status_code == 200
    stats = stats_response.json()

    # Verify statistics structure
    assert "total_notifications" in stats
    assert "registered_farmers" in stats
    assert "by_type" in stats
    assert "active_weather_alerts" in stats
    assert "active_pest_alerts" in stats

    # Verify types
    assert isinstance(stats["total_notifications"], int)
    assert isinstance(stats["registered_farmers"], int)
    assert isinstance(stats["by_type"], dict)
    assert isinstance(stats["active_weather_alerts"], int)
    assert isinstance(stats["active_pest_alerts"], int)
