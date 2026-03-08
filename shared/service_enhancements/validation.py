"""
SAHOOL Input Validation Module
==============================
Provides comprehensive input validation for Arabic/English agricultural platform.

Features:
- Pydantic-based model validation
- Arabic text validation with normalization
- Coordinate validation for Yemen region
- Phone number validation (Yemen format)
- UUID and field ID validation
- Date range validation

Usage:
    from shared.service_enhancements.validation import (
        validate_input,
        validate_phone,
        validate_coordinates,
        ValidatedModel,
    )

    @validate_input
    async def create_field(request: FieldRequest):
        ...
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import date
from functools import wraps
from typing import TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ValidatedModel(BaseModel):
    """
    Base model with enhanced validation for SAHOOL services.
    Includes Arabic text normalization and common field validators.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    @classmethod
    def normalize_arabic(cls, text: str | None) -> str | None:
        """Normalize Arabic text by removing diacritics and normalizing characters."""
        if not text:
            return text

        # Remove Arabic diacritics (tashkeel)
        diacritics = re.compile(r"[\u064B-\u065F\u0670]")
        text = diacritics.sub("", text)

        # Normalize alef variants to plain alef
        text = re.sub(r"[إأآا]", "ا", text)

        # Normalize teh marbuta to heh
        text = text.replace("ة", "ه")

        # Normalize yeh variants
        text = re.sub(r"[يى]", "ي", text)

        return text.strip()


def validate_uuid(value: str, field_name: str = "id") -> str:
    """Validate UUID format."""
    try:
        uuid.UUID(value)
        return value
    except ValueError as e:
        raise ValueError(f"Invalid {field_name} format: must be a valid UUID") from e


def validate_field_id(value: str) -> str:
    """
    Validate SAHOOL field ID format.
    Format: FIELD-XXXXXXXX or SAHOOL-FIELD-XXXXXXXX
    """
    if not value:
        raise ValueError("Field ID is required")

    patterns = [
        r"^FIELD-[A-Za-z0-9]{8,}$",
        r"^SAHOOL-FIELD-[A-Za-z0-9]{8,}$",
        r"^[A-Za-z0-9\-]{8,36}$",  # Allow UUID format
    ]

    if not any(re.match(pattern, value) for pattern in patterns):
        raise ValueError(f"Invalid field ID format: {value}. Expected format: FIELD-XXXXXXXX or valid UUID")

    return value


def validate_phone(value: str, country_code: str = "967") -> str:
    """
    Validate phone number (Yemen format by default).
    Accepts: +967XXXXXXXXX, 00967XXXXXXXXX, 7XXXXXXXX
    """
    if not value:
        return value

    # Remove all non-digit characters
    digits = re.sub(r"\D", "", value)

    # Handle different formats
    if digits.startswith(country_code):
        digits = digits[len(country_code) :]
    elif digits.startswith(f"00{country_code}"):
        digits = digits[len(f"00{country_code}") :]

    # Yemen mobile: 7XXXXXXXX (9 digits)
    # Yemen landline: 1XXXXXXXX or 2XXXXXXXX (8-9 digits)
    if not (8 <= len(digits) <= 9):
        raise ValueError(f"Invalid phone number length: {len(digits)} digits. Expected 8-9 digits for Yemen numbers.")

    # Mobile numbers start with 7
    if len(digits) == 9 and not digits.startswith("7"):
        raise ValueError("Invalid Yemen mobile number. Must start with 7.")

    return f"+{country_code}{digits}"


def validate_coordinates(lat: float, lon: float) -> tuple[float, float]:
    """
    Validate geographic coordinates for Yemen region.
    Yemen bounds: lat 12.1-19.0, lon 42.5-54.5
    """
    yemen_bounds = {
        "lat_min": 12.1,
        "lat_max": 19.0,
        "lon_min": 42.5,
        "lon_max": 54.5,
    }

    if not (yemen_bounds["lat_min"] <= lat <= yemen_bounds["lat_max"]):
        raise ValueError(
            f"Latitude {lat} is outside Yemen bounds ({yemen_bounds['lat_min']} to {yemen_bounds['lat_max']})"
        )

    if not (yemen_bounds["lon_min"] <= lon <= yemen_bounds["lon_max"]):
        raise ValueError(
            f"Longitude {lon} is outside Yemen bounds ({yemen_bounds['lon_min']} to {yemen_bounds['lon_max']})"
        )

    return lat, lon


def validate_date_range(
    start_date: date | None,
    end_date: date | None,
    max_days: int = 365,
    allow_future: bool = True,
) -> tuple[date | None, date | None]:
    """
    Validate date range with constraints.

    Args:
        start_date: Start of range
        end_date: End of range
        max_days: Maximum allowed days between dates
        allow_future: Whether to allow future dates

    Returns:
        Validated (start_date, end_date) tuple
    """
    today = date.today()

    if start_date and end_date:
        if start_date > end_date:
            raise ValueError("Start date must be before or equal to end date")

        days_diff = (end_date - start_date).days
        if days_diff > max_days:
            raise ValueError(f"Date range exceeds maximum of {max_days} days (requested: {days_diff} days)")

    if not allow_future:
        if start_date and start_date > today:
            raise ValueError("Start date cannot be in the future")
        if end_date and end_date > today:
            raise ValueError("End date cannot be in the future")

    return start_date, end_date


def validate_arabic_text(
    text: str,
    min_length: int = 1,
    max_length: int = 500,
    require_arabic: bool = False,
) -> str:
    """
    Validate Arabic text with length and content constraints.

    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        require_arabic: Whether to require Arabic characters

    Returns:
        Validated and normalized text
    """
    if not text:
        if min_length > 0:
            raise ValueError(f"Text is required (minimum {min_length} characters)")
        return text

    # Strip and check length
    text = text.strip()

    if len(text) < min_length:
        raise ValueError(f"Text too short (minimum {min_length} characters)")

    if len(text) > max_length:
        raise ValueError(f"Text too long (maximum {max_length} characters)")

    # Check for Arabic characters if required
    if require_arabic:
        arabic_pattern = re.compile(r"[\u0600-\u06FF]")
        if not arabic_pattern.search(text):
            raise ValueError("Text must contain Arabic characters")

    # Normalize Arabic text
    text = ValidatedModel.normalize_arabic(text)

    return text


def validate_input(func):
    """
    Decorator for validating function inputs and providing consistent error responses.

    Catches validation errors and converts them to proper HTTP exceptions
    with bilingual error messages.

    Usage:
        @app.post("/fields")
        @validate_input
        async def create_field(request: FieldRequest):
            ...
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            error_msg = str(e)
            logger.warning(f"Validation error in {func.__name__}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "VALIDATION_ERROR",
                    "message": error_msg,
                    "message_ar": "خطأ في التحقق من البيانات",
                    "field": _extract_field_from_error(error_msg),
                },
            ) from e
        except TypeError as e:
            error_msg = str(e)
            logger.warning(f"Type error in {func.__name__}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "TYPE_ERROR",
                    "message": error_msg,
                    "message_ar": "نوع البيانات غير صحيح",
                },
            ) from e

    return wrapper


def _extract_field_from_error(error_msg: str) -> str | None:
    """Extract field name from error message if present."""
    patterns = [
        r"field '(\w+)'",
        r"for (\w+)",
        r"Invalid (\w+)",
        r"(\w+) is required",
    ]

    for pattern in patterns:
        match = re.search(pattern, error_msg, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Validators for Common Fields
# ─────────────────────────────────────────────────────────────────────────────


class CoordinatesModel(ValidatedModel):
    """Model with coordinate validation for Yemen region."""

    latitude: float
    longitude: float

    @model_validator(mode="after")
    def validate_coords(self) -> CoordinatesModel:
        self.latitude, self.longitude = validate_coordinates(self.latitude, self.longitude)
        return self


class PhoneModel(ValidatedModel):
    """Model with phone validation for Yemen numbers."""

    phone: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone_field(cls, v: str | None) -> str | None:
        if v:
            return validate_phone(v)
        return v


class DateRangeModel(ValidatedModel):
    """Model with date range validation."""

    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> DateRangeModel:
        self.start_date, self.end_date = validate_date_range(self.start_date, self.end_date)
        return self


class FieldIdModel(ValidatedModel):
    """Model with field ID validation."""

    field_id: str

    @field_validator("field_id")
    @classmethod
    def validate_field_id_field(cls, v: str) -> str:
        return validate_field_id(v)
