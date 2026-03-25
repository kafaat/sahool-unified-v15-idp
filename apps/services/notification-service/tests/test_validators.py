"""
Tests for src/validators.py - Input Validation
Covers phone validation, email validation, text content, XSS prevention,
time format, farmer ID, expiration, alert types, expected dates,
and all Pydantic validated models.
"""

from datetime import date, timedelta

import pytest
from fastapi import HTTPException
from src.validators import (
    MAX_BODY_LENGTH,
    MAX_FARMER_ID_LENGTH,
    MAX_TITLE_LENGTH,
    VALID_ALERT_TYPES,
    ValidatedFarmerProfile,
    ValidatedNotificationRequest,
    ValidatedPreferences,
    ValidatedWeatherAlertRequest,
    raise_not_found,
    raise_validation_error,
    validate_alert_type,
    validate_email_format,
    validate_expected_date,
    validate_expires_in_hours,
    validate_farmer_id,
    validate_phone_yemen,
    validate_text_content,
    validate_time_format,
)

# ─────────────────────────────────────────────────────────────────────────────
# Phone Number Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestValidatePhoneYemen:
    def test_valid_phone_with_plus_country_code(self):
        result = validate_phone_yemen("+967712345678")
        assert result == "+967712345678"

    def test_valid_phone_without_plus(self):
        result = validate_phone_yemen("967712345678")
        assert result == "+967712345678"

    def test_valid_phone_local_format(self):
        result = validate_phone_yemen("712345678")
        assert result == "+967712345678"

    def test_valid_phone_with_spaces(self):
        result = validate_phone_yemen("7 1234 5678")
        assert result == "+967712345678"

    def test_valid_phone_with_dashes(self):
        result = validate_phone_yemen("71-234-5678")
        assert result == "+967712345678"

    def test_valid_phone_with_dots(self):
        result = validate_phone_yemen("71.234.5678")
        assert result == "+967712345678"

    def test_none_returns_none(self):
        assert validate_phone_yemen(None) is None

    def test_empty_string_returns_none(self):
        assert validate_phone_yemen("") is None

    def test_invalid_not_starting_with_7(self):
        with pytest.raises(ValueError, match="Invalid Yemen phone number"):
            validate_phone_yemen("612345678")

    def test_invalid_too_short(self):
        with pytest.raises(ValueError, match="Invalid Yemen phone number"):
            validate_phone_yemen("71234567")

    def test_invalid_too_long(self):
        with pytest.raises(ValueError, match="Invalid Yemen phone number"):
            validate_phone_yemen("7123456789")

    def test_invalid_non_digits(self):
        with pytest.raises(ValueError, match="Invalid Yemen phone number"):
            validate_phone_yemen("71234abcd")


# ─────────────────────────────────────────────────────────────────────────────
# Email Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateEmailFormat:
    def test_valid_email(self):
        result = validate_email_format("user@example.com")
        assert result == "user@example.com"

    def test_valid_email_uppercase(self):
        result = validate_email_format("User@Example.COM")
        assert result == "user@example.com"

    def test_valid_email_with_dots(self):
        result = validate_email_format("first.last@example.com")
        assert result == "first.last@example.com"

    def test_valid_email_with_plus(self):
        result = validate_email_format("user+tag@example.com")
        assert result == "user+tag@example.com"

    def test_none_returns_none(self):
        assert validate_email_format(None) is None

    def test_empty_returns_none(self):
        assert validate_email_format("") is None

    def test_invalid_no_at(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email_format("userexample.com")

    def test_invalid_no_domain(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email_format("user@")

    def test_invalid_no_tld(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email_format("user@example")


# ─────────────────────────────────────────────────────────────────────────────
# Text Content Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateTextContent:
    def test_valid_text(self):
        result = validate_text_content("Hello world", "title")
        assert result == "Hello world"

    def test_strips_whitespace(self):
        result = validate_text_content("  Hello  ", "title")
        assert result == "Hello"

    def test_empty_not_allowed(self):
        with pytest.raises(ValueError, match="is required"):
            validate_text_content("", "title")

    def test_empty_allowed_when_flag_set(self):
        result = validate_text_content("", "title", allow_empty=True)
        assert result == ""

    def test_too_long(self):
        long_text = "a" * 501
        with pytest.raises(ValueError, match="too long"):
            validate_text_content(long_text, "body", max_length=500)

    def test_xss_script_tag(self):
        with pytest.raises(ValueError, match="XSS detected"):
            validate_text_content("<script>alert('xss')</script>", "title")

    def test_xss_javascript_protocol(self):
        with pytest.raises(ValueError, match="XSS detected"):
            validate_text_content("javascript:alert(1)", "title")

    def test_xss_event_handler(self):
        with pytest.raises(ValueError, match="XSS detected"):
            validate_text_content("onclick=doEvil()", "title")

    def test_xss_iframe(self):
        with pytest.raises(ValueError, match="XSS detected"):
            validate_text_content("<iframe src='evil.com'>", "title")

    def test_xss_object(self):
        with pytest.raises(ValueError, match="XSS detected"):
            validate_text_content("<object data='evil.swf'>", "title")

    def test_arabic_text_allowed(self):
        result = validate_text_content("مرحبا بالعالم", "title")
        assert result == "مرحبا بالعالم"

    def test_custom_max_length(self):
        result = validate_text_content("abc", "title", max_length=5)
        assert result == "abc"

    def test_none_not_allowed(self):
        with pytest.raises(ValueError, match="is required"):
            validate_text_content(None, "title")


# ─────────────────────────────────────────────────────────────────────────────
# Time Format Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateTimeFormat:
    def test_valid_time(self):
        assert validate_time_format("22:00", "quiet_start") == "22:00"

    def test_valid_midnight(self):
        assert validate_time_format("00:00", "quiet_start") == "00:00"

    def test_none_returns_none(self):
        assert validate_time_format(None, "quiet_start") is None

    def test_empty_returns_none(self):
        assert validate_time_format("", "quiet_start") is None

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid.*format"):
            validate_time_format("25:00", "quiet_start")

    def test_invalid_not_time(self):
        with pytest.raises(ValueError, match="Invalid.*format"):
            validate_time_format("abc", "quiet_start")


# ─────────────────────────────────────────────────────────────────────────────
# Farmer ID Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateFarmerId:
    def test_valid_farmer_id(self):
        assert validate_farmer_id("farmer-123") == "farmer-123"

    def test_valid_with_underscore(self):
        assert validate_farmer_id("farmer_123") == "farmer_123"

    def test_strips_whitespace(self):
        assert validate_farmer_id("  farmer-123  ") == "farmer-123"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="required"):
            validate_farmer_id("")

    def test_too_long(self):
        with pytest.raises(ValueError, match="too long"):
            validate_farmer_id("a" * (MAX_FARMER_ID_LENGTH + 1))

    def test_invalid_characters(self):
        with pytest.raises(ValueError, match="invalid characters"):
            validate_farmer_id("farmer@123")

    def test_spaces_not_allowed(self):
        with pytest.raises(ValueError, match="invalid characters"):
            validate_farmer_id("farmer 123")


# ─────────────────────────────────────────────────────────────────────────────
# Expires In Hours Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateExpiresInHours:
    def test_valid_hours(self):
        assert validate_expires_in_hours(24) == 24

    def test_none_returns_none(self):
        assert validate_expires_in_hours(None) is None

    def test_minimum_1_hour(self):
        assert validate_expires_in_hours(1) == 1

    def test_maximum_720_hours(self):
        assert validate_expires_in_hours(720) == 720

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="at least 1 hour"):
            validate_expires_in_hours(0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="at least 1 hour"):
            validate_expires_in_hours(-1)

    def test_over_720_raises(self):
        with pytest.raises(ValueError, match="cannot exceed 720"):
            validate_expires_in_hours(721)


# ─────────────────────────────────────────────────────────────────────────────
# Alert Type Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateAlertType:
    def test_valid_types(self):
        for alert_type in VALID_ALERT_TYPES:
            assert validate_alert_type(alert_type) == alert_type

    def test_case_insensitive(self):
        assert validate_alert_type("FROST") == "frost"

    def test_strips_whitespace(self):
        assert validate_alert_type("  frost  ") == "frost"

    def test_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid alert type"):
            validate_alert_type("tornado")


# ─────────────────────────────────────────────────────────────────────────────
# Expected Date Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestValidateExpectedDate:
    def test_today_is_valid(self):
        today = date.today()
        assert validate_expected_date(today) == today

    def test_tomorrow_is_valid(self):
        tomorrow = date.today() + timedelta(days=1)
        assert validate_expected_date(tomorrow) == tomorrow

    def test_14_days_is_valid(self):
        future = date.today() + timedelta(days=14)
        assert validate_expected_date(future) == future

    def test_past_date_raises(self):
        yesterday = date.today() - timedelta(days=1)
        with pytest.raises(ValueError, match="cannot be in the past"):
            validate_expected_date(yesterday)

    def test_over_14_days_raises(self):
        too_far = date.today() + timedelta(days=15)
        with pytest.raises(ValueError, match="cannot be more than 14 days"):
            validate_expected_date(too_far)


# ─────────────────────────────────────────────────────────────────────────────
# HTTP Exception Helpers
# ─────────────────────────────────────────────────────────────────────────────


class TestRaiseValidationError:
    def test_raises_400(self):
        with pytest.raises(HTTPException) as exc_info:
            raise_validation_error("bad input", "إدخال سيء", "field_name")
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail["error"] == "VALIDATION_ERROR"
        assert exc_info.value.detail["message"] == "bad input"
        assert exc_info.value.detail["message_ar"] == "إدخال سيء"
        assert exc_info.value.detail["field"] == "field_name"

    def test_default_arabic_message(self):
        with pytest.raises(HTTPException) as exc_info:
            raise_validation_error("bad input")
        assert exc_info.value.detail["message_ar"] == "خطأ في التحقق من البيانات"


class TestRaiseNotFound:
    def test_raises_404(self):
        with pytest.raises(HTTPException) as exc_info:
            raise_not_found("Farmer", "farmer-123", "المزارع غير موجود")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail["error"] == "NOT_FOUND"
        assert exc_info.value.detail["resource"] == "Farmer"
        assert exc_info.value.detail["resource_id"] == "farmer-123"

    def test_default_arabic_message(self):
        with pytest.raises(HTTPException) as exc_info:
            raise_not_found("Farmer", "farmer-123")
        assert "غير موجود" in exc_info.value.detail["message_ar"]


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Validated Models
# ─────────────────────────────────────────────────────────────────────────────


class TestValidatedFarmerProfile:
    def test_valid_profile(self):
        profile = ValidatedFarmerProfile(
            farmer_id="farmer-123",
            name="Ahmed Ali",
            name_ar="أحمد علي",
            governorate="sanaa",
            crops=["tomato"],
            phone="712345678",
            email="ahmed@example.com",
        )
        assert profile.farmer_id == "farmer-123"
        assert profile.phone == "+967712345678"
        assert profile.email == "ahmed@example.com"

    def test_invalid_farmer_id(self):
        with pytest.raises(Exception):
            ValidatedFarmerProfile(
                farmer_id="farmer@bad",
                name="Ahmed",
                name_ar="أحمد",
                governorate="sanaa",
            )

    def test_invalid_phone(self):
        with pytest.raises(Exception):
            ValidatedFarmerProfile(
                farmer_id="farmer-123",
                name="Ahmed",
                name_ar="أحمد",
                governorate="sanaa",
                phone="123",
            )

    def test_invalid_email(self):
        with pytest.raises(Exception):
            ValidatedFarmerProfile(
                farmer_id="farmer-123",
                name="Ahmed",
                name_ar="أحمد",
                governorate="sanaa",
                email="not-an-email",
            )

    def test_default_language(self):
        profile = ValidatedFarmerProfile(
            farmer_id="farmer-123",
            name="Ahmed",
            name_ar="أحمد",
            governorate="sanaa",
        )
        assert profile.language == "ar"

    def test_invalid_language(self):
        with pytest.raises(Exception):
            ValidatedFarmerProfile(
                farmer_id="farmer-123",
                name="Ahmed",
                name_ar="أحمد",
                governorate="sanaa",
                language="fr",
            )


class TestValidatedNotificationRequest:
    def test_valid_request(self):
        req = ValidatedNotificationRequest(
            type="weather_alert",
            title="Frost Warning",
            title_ar="تحذير صقيع",
            body="Frost expected tonight",
            body_ar="صقيع متوقع الليلة",
        )
        assert req.type == "weather_alert"
        assert req.priority == "medium"
        assert req.expires_in_hours == 24

    def test_xss_in_title_rejected(self):
        with pytest.raises(Exception):
            ValidatedNotificationRequest(
                type="system",
                title="<script>alert(1)</script>",
                title_ar="test",
                body="body",
                body_ar="نص",
            )

    def test_xss_in_body_rejected(self):
        with pytest.raises(Exception):
            ValidatedNotificationRequest(
                type="system",
                title="title",
                title_ar="عنوان",
                body="<script>evil()</script>",
                body_ar="نص",
            )

    def test_target_farmers_validated(self):
        req = ValidatedNotificationRequest(
            type="system",
            title="Title",
            title_ar="عنوان",
            body="Body",
            body_ar="نص",
            target_farmers=["farmer-1", "farmer-2"],
        )
        assert req.target_farmers == ["farmer-1", "farmer-2"]

    def test_invalid_target_farmer_id(self):
        with pytest.raises(Exception):
            ValidatedNotificationRequest(
                type="system",
                title="Title",
                title_ar="عنوان",
                body="Body",
                body_ar="نص",
                target_farmers=["farmer@bad"],
            )


class TestValidatedWeatherAlertRequest:
    def test_valid_request(self):
        req = ValidatedWeatherAlertRequest(
            governorates=["sanaa"],
            alert_type="frost",
            severity="high",
            expected_date=date.today() + timedelta(days=1),
        )
        assert req.alert_type == "frost"

    def test_invalid_alert_type(self):
        with pytest.raises(Exception):
            ValidatedWeatherAlertRequest(
                governorates=["sanaa"],
                alert_type="tornado",
                severity="high",
                expected_date=date.today() + timedelta(days=1),
            )

    def test_past_date_rejected(self):
        with pytest.raises(Exception):
            ValidatedWeatherAlertRequest(
                governorates=["sanaa"],
                alert_type="frost",
                severity="high",
                expected_date=date.today() - timedelta(days=1),
            )


class TestValidatedPreferences:
    def test_valid_preferences(self):
        pref = ValidatedPreferences(
            farmer_id="farmer-123",
            quiet_hours_start="22:00",
            quiet_hours_end="06:00",
        )
        assert pref.farmer_id == "farmer-123"
        assert pref.weather_alerts is True

    def test_invalid_farmer_id(self):
        with pytest.raises(Exception):
            ValidatedPreferences(farmer_id="farmer@bad")

    def test_invalid_quiet_hours_format(self):
        with pytest.raises(Exception):
            ValidatedPreferences(
                farmer_id="farmer-123",
                quiet_hours_start="25:00",
            )

    def test_quiet_hours_spanning_midnight(self):
        pref = ValidatedPreferences(
            farmer_id="farmer-123",
            quiet_hours_start="22:00",
            quiet_hours_end="06:00",
        )
        assert pref.quiet_hours_start == "22:00"
        assert pref.quiet_hours_end == "06:00"

    def test_all_preferences_disabled(self):
        pref = ValidatedPreferences(
            farmer_id="farmer-123",
            weather_alerts=False,
            pest_alerts=False,
            irrigation_reminders=False,
            crop_health_alerts=False,
            market_prices=False,
        )
        assert pref.weather_alerts is False
        assert pref.market_prices is False
