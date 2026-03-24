"""
Tests for src/notification_types.py - Notification Types, Templates, and Helper Functions

Covers:
- NotificationType and NotificationPriority enums
- NotificationPayload model
- NotificationTemplate.format_template (all types + weather subtypes)
- create_weather_notification helper
- create_harvest_notification helper
- create_satellite_notification helper
"""

from datetime import datetime

import pytest
from src.notification_types import (
    NotificationPayload,
    NotificationPriority,
    NotificationTemplate,
    NotificationType,
    create_harvest_notification,
    create_satellite_notification,
    create_weather_notification,
)

# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class TestNotificationTypeEnum:
    def test_all_types_defined(self):
        assert NotificationType.WEATHER_ALERT == "weather_alert"
        assert NotificationType.LOW_STOCK == "low_stock"
        assert NotificationType.DISEASE_DETECTED == "disease_detected"
        assert NotificationType.SPRAY_WINDOW == "spray_window"
        assert NotificationType.HARVEST_REMINDER == "harvest_reminder"
        assert NotificationType.PAYMENT_DUE == "payment_due"
        assert NotificationType.FIELD_UPDATE == "field_update"
        assert NotificationType.SATELLITE_READY == "satellite_ready"
        assert NotificationType.PEST_OUTBREAK == "pest_outbreak"
        assert NotificationType.IRRIGATION_REMINDER == "irrigation_reminder"
        assert NotificationType.MARKET_PRICE == "market_price"
        assert NotificationType.CROP_HEALTH == "crop_health"
        assert NotificationType.TASK_REMINDER == "task_reminder"
        assert NotificationType.SYSTEM == "system"


class TestNotificationPriorityEnum:
    def test_all_priorities(self):
        assert NotificationPriority.LOW == "low"
        assert NotificationPriority.MEDIUM == "medium"
        assert NotificationPriority.HIGH == "high"
        assert NotificationPriority.CRITICAL == "critical"


# ─────────────────────────────────────────────────────────────────────────────
# NotificationPayload
# ─────────────────────────────────────────────────────────────────────────────


class TestNotificationPayload:
    def test_basic_payload(self):
        payload = NotificationPayload(
            notification_type=NotificationType.WEATHER_ALERT,
            priority=NotificationPriority.HIGH,
            title="Frost Warning",
            title_ar="تحذير صقيع",
            body="Frost expected",
            body_ar="صقيع متوقع",
        )
        assert payload.notification_type == NotificationType.WEATHER_ALERT
        assert payload.priority == NotificationPriority.HIGH
        assert payload.created_at is not None
        assert payload.image_url is None
        assert payload.action_url is None
        assert payload.field_id is None

    def test_full_payload(self):
        payload = NotificationPayload(
            notification_type=NotificationType.DISEASE_DETECTED,
            priority=NotificationPriority.CRITICAL,
            title="Disease",
            title_ar="مرض",
            body="Disease found",
            body_ar="تم اكتشاف مرض",
            image_url="https://img.example.com/disease.jpg",
            action_url="https://sahool.app/field/123",
            field_id="field-123",
            crop_type="wheat",
            farmer_id="farmer-456",
            data={"confidence": 95},
        )
        assert payload.image_url is not None
        assert payload.field_id == "field-123"
        assert payload.data["confidence"] == 95

    def test_default_priority(self):
        payload = NotificationPayload(
            notification_type=NotificationType.SYSTEM,
            title="System",
            title_ar="نظام",
            body="Message",
            body_ar="رسالة",
        )
        assert payload.priority == NotificationPriority.MEDIUM


# ─────────────────────────────────────────────────────────────────────────────
# NotificationTemplate.format_template
# ─────────────────────────────────────────────────────────────────────────────


class TestFormatTemplate:
    def test_weather_frost_en(self):
        result = NotificationTemplate.format_template(
            NotificationType.WEATHER_ALERT,
            language="en",
            weather_type="frost",
            governorate="Sana'a",
        )
        assert "Frost" in result["title"]
        assert "Sana'a" in result["body"]

    def test_weather_frost_ar(self):
        result = NotificationTemplate.format_template(
            NotificationType.WEATHER_ALERT,
            language="ar",
            weather_type="frost",
            governorate="صنعاء",
        )
        assert "صقيع" in result["title"]
        assert "صنعاء" in result["body"]

    def test_weather_heat_wave(self):
        result = NotificationTemplate.format_template(
            NotificationType.WEATHER_ALERT,
            language="en",
            weather_type="heat_wave",
            governorate="Aden",
        )
        assert "Heat" in result["title"]

    def test_weather_storm(self):
        result = NotificationTemplate.format_template(
            NotificationType.WEATHER_ALERT,
            language="en",
            weather_type="storm",
            governorate="Taiz",
        )
        assert "Storm" in result["title"]

    def test_weather_flood(self):
        result = NotificationTemplate.format_template(
            NotificationType.WEATHER_ALERT,
            language="en",
            weather_type="flood",
            governorate="Hodeidah",
        )
        assert "Flood" in result["title"]

    def test_weather_drought(self):
        result = NotificationTemplate.format_template(
            NotificationType.WEATHER_ALERT,
            language="en",
            weather_type="drought",
            governorate="Ibb",
        )
        assert "Drought" in result["title"]

    def test_weather_unknown_type_defaults_to_storm(self):
        result = NotificationTemplate.format_template(
            NotificationType.WEATHER_ALERT,
            language="en",
            weather_type="unknown_weather",
            governorate="Test",
        )
        assert "Storm" in result["title"]

    def test_weather_without_subtype(self):
        result = NotificationTemplate.format_template(
            NotificationType.WEATHER_ALERT,
            language="en",
            governorate="Test",
        )
        # Should use default WEATHER_STORM
        assert "Storm" in result["title"]

    def test_low_stock(self):
        result = NotificationTemplate.format_template(
            NotificationType.LOW_STOCK,
            language="en",
            item_name="Urea",
            quantity=5,
            unit="bags",
        )
        assert "Low Stock" in result["title"]
        assert "Urea" in result["body"]

    def test_disease_detected(self):
        result = NotificationTemplate.format_template(
            NotificationType.DISEASE_DETECTED,
            language="en",
            disease_name="Wheat Rust",
            field_name="North Field",
            confidence=92,
        )
        assert "Disease" in result["title"]
        assert "Wheat Rust" in result["body"]
        assert "92" in result["body"]

    def test_spray_window(self):
        result = NotificationTemplate.format_template(
            NotificationType.SPRAY_WINDOW,
            language="en",
            field_name="West Field",
            wind_speed=8,
            temp=25,
            hours=4,
        )
        assert "Spray" in result["title"]
        assert "8" in result["body"]

    def test_harvest_reminder(self):
        result = NotificationTemplate.format_template(
            NotificationType.HARVEST_REMINDER,
            language="en",
            crop_name="Wheat",
            field_name="East Field",
            yield_kg=5000,
            days=3,
        )
        assert "Harvest" in result["title"]
        assert "5000" in result["body"]

    def test_payment_due(self):
        result = NotificationTemplate.format_template(
            NotificationType.PAYMENT_DUE,
            language="en",
            amount=1500,
            item="fertilizer",
            due_date="2026-04-01",
        )
        assert "Payment" in result["title"]
        assert "1500" in result["body"]

    def test_field_update(self):
        result = NotificationTemplate.format_template(
            NotificationType.FIELD_UPDATE,
            language="en",
            field_name="South Field",
            update_message="Irrigation completed",
        )
        assert "Field Update" in result["title"]

    def test_satellite_ready(self):
        result = NotificationTemplate.format_template(
            NotificationType.SATELLITE_READY,
            language="en",
            field_name="Farm-3",
            ndvi_value="0.72",
        )
        assert "Satellite" in result["title"]
        assert "0.72" in result["body"]

    def test_pest_outbreak(self):
        result = NotificationTemplate.format_template(
            NotificationType.PEST_OUTBREAK,
            language="en",
            pest_name="Aphids",
            governorate="Taiz",
            crops="Tomato, Potato",
        )
        assert "Pest" in result["title"]
        assert "Aphids" in result["body"]

    def test_irrigation_reminder(self):
        result = NotificationTemplate.format_template(
            NotificationType.IRRIGATION_REMINDER,
            language="en",
            field_name="North Field",
            water_mm=25,
        )
        assert "Irrigation" in result["title"]
        assert "25" in result["body"]

    def test_market_price(self):
        result = NotificationTemplate.format_template(
            NotificationType.MARKET_PRICE,
            language="en",
            crop_name="Coffee",
            price=850,
            change=5,
            market_name="Sana'a Market",
        )
        assert "Market" in result["title"]
        assert "850" in result["body"]

    def test_crop_health(self):
        result = NotificationTemplate.format_template(
            NotificationType.CROP_HEALTH,
            language="en",
            field_name="Main Field",
            status="declining",
            drop=15,
        )
        assert "Crop Health" in result["title"]

    def test_task_reminder(self):
        result = NotificationTemplate.format_template(
            NotificationType.TASK_REMINDER,
            language="en",
            task_name="Fertilize wheat",
            due_time="tomorrow",
            priority="high",
        )
        assert "Task" in result["title"]
        assert "Fertilize wheat" in result["body"]

    def test_system_notification(self):
        result = NotificationTemplate.format_template(
            NotificationType.SYSTEM,
            language="en",
            message="System maintenance scheduled",
        )
        assert "System" in result["title"]
        assert "maintenance" in result["body"]

    def test_missing_kwargs_returns_raw_template(self):
        result = NotificationTemplate.format_template(
            NotificationType.IRRIGATION_REMINDER,
            language="en",
        )
        # Should not raise, returns raw template
        assert "Irrigation" in result["title"]
        assert "{field_name}" in result["body"]

    def test_arabic_templates(self):
        result = NotificationTemplate.format_template(
            NotificationType.IRRIGATION_REMINDER,
            language="ar",
            field_name="الحقل",
            water_mm=30,
        )
        assert "ري" in result["title"]
        assert "الحقل" in result["body"]


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────


class TestCreateWeatherNotification:
    def test_frost_notification(self):
        payload = create_weather_notification("frost", "Sana'a")
        assert payload.notification_type == NotificationType.WEATHER_ALERT
        assert payload.priority == NotificationPriority.HIGH
        assert "frost" in payload.data["weather_type"]

    def test_heat_wave_notification(self):
        payload = create_weather_notification("heat_wave", "Aden")
        assert payload.priority == NotificationPriority.MEDIUM

    def test_storm_notification(self):
        payload = create_weather_notification("storm", "Taiz")
        assert payload.priority == NotificationPriority.HIGH

    def test_flood_notification(self):
        payload = create_weather_notification("flood", "Hodeidah")
        assert payload.priority == NotificationPriority.HIGH

    def test_drought_notification(self):
        payload = create_weather_notification("drought", "Ibb")
        assert payload.priority == NotificationPriority.MEDIUM

    def test_extra_data_included(self):
        payload = create_weather_notification("frost", "Sana'a", min_temp=-3)
        assert payload.data["min_temp"] == -3


class TestCreateHarvestNotification:
    def test_basic_harvest(self):
        payload = create_harvest_notification(
            crop_name="Wheat",
            crop_name_ar="قمح",
            field_name="North Field",
            field_id="f-1",
            yield_kg=5000,
            days_until=5,
        )
        assert payload.notification_type == NotificationType.HARVEST_REMINDER
        assert payload.priority == NotificationPriority.MEDIUM
        assert payload.field_id == "f-1"
        assert payload.crop_type == "Wheat"
        assert "Wheat" in payload.data["crop_name"]

    def test_urgent_harvest(self):
        payload = create_harvest_notification(
            crop_name="Tomato",
            crop_name_ar="طماطم",
            field_name="South",
            field_id="f-2",
            yield_kg=1000,
            days_until=1,
        )
        assert payload.priority == NotificationPriority.HIGH

    def test_exact_2_days_is_high(self):
        payload = create_harvest_notification(
            crop_name="Coffee",
            crop_name_ar="بن",
            field_name="Hill",
            field_id="f-3",
            yield_kg=2000,
            days_until=2,
        )
        assert payload.priority == NotificationPriority.HIGH


class TestCreateSatelliteNotification:
    def test_normal_change(self):
        payload = create_satellite_notification(
            field_name="Farm A",
            field_id="f-1",
            ndvi_value=0.72,
            change_percentage=-5,
        )
        assert payload.notification_type == NotificationType.SATELLITE_READY
        assert payload.priority == NotificationPriority.MEDIUM
        assert payload.action_url == "/fields/f-1/satellite"
        assert payload.data["ndvi_value"] == 0.72

    def test_significant_drop_is_high_priority(self):
        payload = create_satellite_notification(
            field_name="Farm B",
            field_id="f-2",
            ndvi_value=0.35,
            change_percentage=-15,
        )
        assert payload.priority == NotificationPriority.HIGH

    def test_exact_minus_10_is_medium(self):
        payload = create_satellite_notification(
            field_name="Farm C",
            field_id="f-3",
            ndvi_value=0.50,
            change_percentage=-10,
        )
        assert payload.priority == NotificationPriority.MEDIUM

    def test_positive_change_is_medium(self):
        payload = create_satellite_notification(
            field_name="Farm D",
            field_id="f-4",
            ndvi_value=0.80,
            change_percentage=5,
        )
        assert payload.priority == NotificationPriority.MEDIUM
