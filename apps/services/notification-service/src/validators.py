"""
SAHOOL Notification Service - Input Validation
===============================================
Provides comprehensive input validation for notification service.

Features:
- Phone number validation (Yemen format)
- Email validation with proper error messages
- Notification content validation (length, XSS prevention)
- Farmer ID validation
- Time format validation for quiet hours
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, time, timedelta
from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

# Yemen phone number pattern
YEMEN_PHONE_PATTERN = re.compile(r"^(\+?967)?7[0-9]{8}$")

# Allowed weather alert types
VALID_ALERT_TYPES = {"frost", "heat_wave", "storm", "flood", "drought", "dust_storm", "hail"}

# Max lengths for text fields
MAX_TITLE_LENGTH = 200
MAX_BODY_LENGTH = 2000
MAX_FARMER_ID_LENGTH = 100

# XSS prevention - disallowed patterns
XSS_PATTERNS = [
    re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),
    re.compile(r"<iframe.*?>", re.IGNORECASE),
    re.compile(r"<object.*?>", re.IGNORECASE),
]


# ─────────────────────────────────────────────────────────────────────────────
# Validation Functions
# ─────────────────────────────────────────────────────────────────────────────


def validate_phone_yemen(phone: str | None) -> str | None:
    """
    Validate Yemen phone number format.

    Valid formats:
    - +967712345678
    - 967712345678
    - 712345678
    - 7XXXXXXXX (starts with 7, 9 digits)
    """
    if not phone:
        return None

    # Remove spaces, dashes, and dots
    cleaned = re.sub(r"[\s\-\.]", "", phone)

    # Remove leading + if present
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]

    # If starts with 967, remove it
    if cleaned.startswith("967"):
        cleaned = cleaned[3:]

    # Now we should have 9 digits starting with 7
    if not (len(cleaned) == 9 and cleaned.startswith("7") and cleaned.isdigit()):
        raise ValueError(f"Invalid Yemen phone number: {phone}. Expected format: 7XXXXXXXX (9 digits starting with 7)")

    return f"+967{cleaned}"


def validate_email_format(email: str | None) -> str | None:
    """Validate email format."""
    if not email:
        return None

    # Basic email pattern
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    if not email_pattern.match(email):
        raise ValueError(f"Invalid email format: {email}")

    return email.lower()


def validate_text_content(
    text: str,
    field_name: str,
    max_length: int = 500,
    allow_empty: bool = False,
) -> str:
    """
    Validate text content for notifications.

    - Removes potential XSS
    - Validates length
    - Strips whitespace
    """
    if not text:
        if not allow_empty:
            raise ValueError(f"{field_name} is required and cannot be empty")
        return ""

    # Strip whitespace
    text = text.strip()

    # Check length
    if len(text) > max_length:
        raise ValueError(
            f"{field_name} is too long. Maximum {max_length} characters allowed, got {len(text)} characters"
        )

    # Check for XSS patterns
    for pattern in XSS_PATTERNS:
        if pattern.search(text):
            logger.warning(
                f"XSS pattern detected in {field_name}",
                extra={"field": field_name, "pattern": pattern.pattern},
            )
            raise ValueError(f"{field_name} contains invalid content (potential XSS detected)")

    return text


def validate_time_format(time_str: str | None, field_name: str) -> str | None:
    """Validate time format (HH:MM)."""
    if not time_str:
        return None

    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError as e:
        raise ValueError(f"Invalid {field_name} format: {time_str}. Expected HH:MM format (e.g., 22:00)") from e

    return time_str


def validate_farmer_id(farmer_id: str) -> str:
    """Validate farmer ID format."""
    if not farmer_id:
        raise ValueError("Farmer ID is required")

    farmer_id = farmer_id.strip()

    if len(farmer_id) > MAX_FARMER_ID_LENGTH:
        raise ValueError(f"Farmer ID is too long. Maximum {MAX_FARMER_ID_LENGTH} characters")

    # Allow alphanumeric, underscores, and hyphens
    if not re.match(r"^[a-zA-Z0-9_\-]+$", farmer_id):
        raise ValueError(
            "Farmer ID contains invalid characters. Only alphanumeric, underscores, and hyphens are allowed"
        )

    return farmer_id


def validate_expires_in_hours(hours: int | None) -> int | None:
    """Validate expiration hours."""
    if hours is None:
        return None

    if hours < 1:
        raise ValueError("Expiration must be at least 1 hour")

    if hours > 720:  # 30 days
        raise ValueError("Expiration cannot exceed 720 hours (30 days)")

    return hours


def validate_alert_type(alert_type: str) -> str:
    """Validate weather alert type."""
    alert_type = alert_type.lower().strip()

    if alert_type not in VALID_ALERT_TYPES:
        raise ValueError(f"Invalid alert type: {alert_type}. Valid types: {', '.join(VALID_ALERT_TYPES)}")

    return alert_type


def validate_expected_date(expected_date: date) -> date:
    """Validate expected date for alerts."""
    today = date.today()

    # Cannot be in the past
    if expected_date < today:
        raise ValueError(f"Expected date cannot be in the past: {expected_date}")

    # Cannot be more than 14 days in the future
    max_date = today + timedelta(days=14)
    if expected_date > max_date:
        raise ValueError(f"Expected date cannot be more than 14 days in the future: {expected_date}")

    return expected_date


# ─────────────────────────────────────────────────────────────────────────────
# Enhanced Pydantic Models with Validation
# ─────────────────────────────────────────────────────────────────────────────


class ValidatedFarmerProfile(BaseModel):
    """Enhanced farmer profile with validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    farmer_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    governorate: str
    district: str | None = Field(None, max_length=100)
    crops: list[str] = Field(default_factory=list)
    field_ids: list[str] = Field(default_factory=list)
    phone: str | None = None
    email: str | None = None
    fcm_token: str | None = Field(None, max_length=500)
    notification_channels: list[str] = Field(default_factory=lambda: ["in_app"])
    language: str = Field(default="ar", pattern="^(ar|en)$")

    @field_validator("farmer_id")
    @classmethod
    def validate_farmer_id_field(cls, v: str) -> str:
        return validate_farmer_id(v)

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: str | None) -> str | None:
        return validate_phone_yemen(v)

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str | None) -> str | None:
        return validate_email_format(v)

    @field_validator("name", "name_ar")
    @classmethod
    def validate_name_fields(cls, v: str) -> str:
        return validate_text_content(v, "name", max_length=200)


class ValidatedNotificationRequest(BaseModel):
    """Enhanced notification request with validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    type: str
    priority: str = "medium"
    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    title_ar: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH)
    body: str = Field(..., min_length=1, max_length=MAX_BODY_LENGTH)
    body_ar: str = Field(..., min_length=1, max_length=MAX_BODY_LENGTH)
    data: dict[str, Any] = Field(default_factory=dict)
    target_farmers: list[str] = Field(default_factory=list)
    target_governorates: list[str] = Field(default_factory=list)
    target_crops: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=lambda: ["in_app"])
    expires_in_hours: int | None = Field(default=24, ge=1, le=720)

    @field_validator("title", "title_ar")
    @classmethod
    def validate_title_fields(cls, v: str) -> str:
        return validate_text_content(v, "title", max_length=MAX_TITLE_LENGTH)

    @field_validator("body", "body_ar")
    @classmethod
    def validate_body_fields(cls, v: str) -> str:
        return validate_text_content(v, "body", max_length=MAX_BODY_LENGTH)

    @field_validator("target_farmers")
    @classmethod
    def validate_target_farmers(cls, v: list[str]) -> list[str]:
        validated = []
        for farmer_id in v:
            validated.append(validate_farmer_id(farmer_id))
        return validated


class ValidatedWeatherAlertRequest(BaseModel):
    """Enhanced weather alert request with validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    governorates: list[str] = Field(..., min_length=1)
    alert_type: str
    severity: str
    expected_date: date
    details: dict[str, Any] = Field(default_factory=dict)

    @field_validator("alert_type")
    @classmethod
    def validate_alert_type_field(cls, v: str) -> str:
        return validate_alert_type(v)

    @field_validator("expected_date")
    @classmethod
    def validate_expected_date_field(cls, v: date) -> date:
        return validate_expected_date(v)


class ValidatedPreferences(BaseModel):
    """Enhanced notification preferences with validation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    farmer_id: str = Field(..., min_length=1, max_length=100)
    weather_alerts: bool = True
    pest_alerts: bool = True
    irrigation_reminders: bool = True
    crop_health_alerts: bool = True
    market_prices: bool = True
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    min_priority: str = "low"

    @field_validator("farmer_id")
    @classmethod
    def validate_farmer_id_field(cls, v: str) -> str:
        return validate_farmer_id(v)

    @field_validator("quiet_hours_start")
    @classmethod
    def validate_quiet_start(cls, v: str | None) -> str | None:
        return validate_time_format(v, "quiet_hours_start")

    @field_validator("quiet_hours_end")
    @classmethod
    def validate_quiet_end(cls, v: str | None) -> str | None:
        return validate_time_format(v, "quiet_hours_end")

    @model_validator(mode="after")
    def validate_quiet_hours(self) -> ValidatedPreferences:
        """Validate quiet hours range."""
        if self.quiet_hours_start and self.quiet_hours_end:
            datetime.strptime(self.quiet_hours_start, "%H:%M").time()
            datetime.strptime(self.quiet_hours_end, "%H:%M").time()

            # Quiet hours can span midnight (e.g., 22:00 to 06:00)
            # This is valid, so no additional validation needed
            pass

        return self


# ─────────────────────────────────────────────────────────────────────────────
# HTTP Exception Helpers
# ─────────────────────────────────────────────────────────────────────────────


def raise_validation_error(
    message: str,
    message_ar: str | None = None,
    field: str | None = None,
) -> None:
    """Raise a validation error with proper formatting."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error": "VALIDATION_ERROR",
            "message": message,
            "message_ar": message_ar or "خطأ في التحقق من البيانات",
            "field": field,
        },
    )


def raise_not_found(
    resource: str,
    resource_id: str,
    message_ar: str | None = None,
) -> None:
    """Raise a not found error."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "NOT_FOUND",
            "message": f"{resource} with ID {resource_id} not found",
            "message_ar": message_ar or f"{resource} غير موجود",
            "resource": resource,
            "resource_id": resource_id,
        },
    )
