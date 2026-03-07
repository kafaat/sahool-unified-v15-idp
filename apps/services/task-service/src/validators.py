"""
Validators for Task Service - أدوات التحقق لخدمة المهام

This module provides validation utilities for task data including
time formats, metadata size limits, and field ID validation.
"""

import json
import re
from datetime import datetime
from typing import Any

try:
    from pydantic import field_validator, model_validator
    from pydantic_core.core_schema import ValidationInfo

    PYDANTIC_AVAILABLE = True
except ImportError:
    # Pydantic not available - validators will raise if used
    field_validator = None
    model_validator = None
    ValidationInfo = None
    PYDANTIC_AVAILABLE = False

from .exceptions import (
    InvalidDateFormatError,
    InvalidFieldIdError,
    InvalidTimeFormatError,
    MetadataTooLargeError,
)

# ═══════════════════════════════════════════════════════════════════════════
# Constants - الثوابت
# ═══════════════════════════════════════════════════════════════════════════

# Maximum metadata size in bytes (64KB)
MAX_METADATA_SIZE_BYTES = 65536

# Field ID pattern: alphanumeric, underscores, and hyphens
FIELD_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

# Time format pattern: HH:MM or HH:MM:SS
TIME_FORMAT_PATTERN = re.compile(r"^([01]?[0-9]|2[0-3]):([0-5][0-9])(?::([0-5][0-9]))?$")

# Date format pattern: YYYY-MM-DD
DATE_FORMAT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Control characters pattern for sanitization
CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x1f\x7f]")


# ═══════════════════════════════════════════════════════════════════════════
# Validation Functions - دوال التحقق
# ═══════════════════════════════════════════════════════════════════════════


def validate_field_id(field_id: str | None, raise_exception: bool = True) -> bool:
    """
    Validate field ID format
    التحقق من تنسيق معرف الحقل

    Args:
        field_id: The field ID to validate
        raise_exception: Whether to raise an exception on invalid input

    Returns:
        bool: True if valid, False if invalid (when raise_exception=False)

    Raises:
        InvalidFieldIdError: If field_id is invalid and raise_exception=True
    """
    if field_id is None:
        return True  # None is allowed (optional field)

    if not field_id or len(field_id) > 100:
        if raise_exception:
            raise InvalidFieldIdError(field_id or "")
        return False

    if not FIELD_ID_PATTERN.match(field_id):
        if raise_exception:
            raise InvalidFieldIdError(field_id)
        return False

    return True


def validate_scheduled_time(time_str: str | None, raise_exception: bool = True) -> bool:
    """
    Validate scheduled time format (HH:MM or HH:MM:SS)
    التحقق من تنسيق الوقت المجدول

    Args:
        time_str: Time string to validate
        raise_exception: Whether to raise an exception on invalid input

    Returns:
        bool: True if valid, False if invalid (when raise_exception=False)

    Raises:
        InvalidTimeFormatError: If time format is invalid and raise_exception=True
    """
    if time_str is None:
        return True  # None is allowed (optional field)

    if not TIME_FORMAT_PATTERN.match(time_str):
        if raise_exception:
            raise InvalidTimeFormatError(time_str)
        return False

    return True


def validate_date_string(date_str: str | None, raise_exception: bool = True) -> bool:
    """
    Validate date string format (YYYY-MM-DD)
    التحقق من تنسيق سلسلة التاريخ

    Args:
        date_str: Date string to validate
        raise_exception: Whether to raise an exception on invalid input

    Returns:
        bool: True if valid, False if invalid (when raise_exception=False)

    Raises:
        InvalidDateFormatError: If date format is invalid and raise_exception=True
    """
    if date_str is None:
        return True  # None is allowed (optional field)

    if not DATE_FORMAT_PATTERN.match(date_str):
        if raise_exception:
            raise InvalidDateFormatError(date_str)
        return False

    # Also validate that it's a real date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        if raise_exception:
            raise InvalidDateFormatError(date_str)
        return False

    return True


def validate_metadata_size(metadata: dict | None, raise_exception: bool = True) -> bool:
    """
    Validate metadata size is within limits
    التحقق من أن حجم البيانات الوصفية ضمن الحدود

    Args:
        metadata: Metadata dictionary to validate
        raise_exception: Whether to raise an exception on invalid input

    Returns:
        bool: True if valid, False if invalid (when raise_exception=False)

    Raises:
        MetadataTooLargeError: If metadata exceeds size limit and raise_exception=True
    """
    if metadata is None:
        return True  # None is allowed

    try:
        # Calculate size of JSON serialization
        json_str = json.dumps(metadata, ensure_ascii=False)
        size = len(json_str.encode("utf-8"))

        if size > MAX_METADATA_SIZE_BYTES:
            if raise_exception:
                raise MetadataTooLargeError(size, MAX_METADATA_SIZE_BYTES)
            return False

        return True

    except (TypeError, ValueError):
        # Metadata is not JSON serializable
        if raise_exception:
            raise MetadataTooLargeError(0, MAX_METADATA_SIZE_BYTES)
        return False


def sanitize_for_log(value: str | int | float | None, max_length: int = 100) -> str:
    """
    Sanitize user input for safe logging to prevent log injection attacks
    تعقيم المدخلات لمنع هجمات حقن السجلات

    This function explicitly removes newline (\\n) and carriage return (\\r) characters,
    as well as ALL ASCII control characters (0x00-0x1F, 0x7F) to prevent log injection
    attacks including log forging and newline injection.

    Args:
        value: The input value to sanitize (supports str, int, float, None)
        max_length: Maximum length of the output string

    Returns:
        A sanitized string safe for logging
    """
    if value is None:
        return "<none>"

    # Convert to string (supports int/float for numeric parameters)
    raw = str(value)

    # Explicitly remove newline and carriage return characters first
    # This addresses CodeQL log injection warnings directly
    sanitized = raw.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")

    # Remove ALL ASCII control characters using regex (0x00-0x1F, 0x7F)
    sanitized = CONTROL_CHAR_PATTERN.sub("", sanitized)

    # Additional safety: keep only printable characters
    sanitized = "".join(c for c in sanitized if c.isprintable())

    # Strip whitespace and check for empty result
    sanitized = sanitized.strip()
    if not sanitized:
        return "<empty>"

    # Truncate to max length
    return sanitized[:max_length] if len(sanitized) > max_length else sanitized


def sanitize_field_id_for_url(field_id: str) -> str:
    """
    Sanitize field ID for use in URLs (SSRF prevention)
    تعقيم معرف الحقل للاستخدام في عناوين URL

    Args:
        field_id: Field ID to sanitize

    Returns:
        Sanitized field ID safe for URL construction
    """
    if not field_id:
        return ""

    # Remove any characters that could be used for path traversal or SSRF
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "", field_id)

    # Limit length
    return sanitized[:100]


# ═══════════════════════════════════════════════════════════════════════════
# Pydantic Validator Decorators - زخارف التحقق من Pydantic
# ═══════════════════════════════════════════════════════════════════════════


def scheduled_time_validator(cls: Any, v: str | None) -> str | None:
    """
    Pydantic validator for scheduled_time field
    أداة التحقق من Pydantic لحقل scheduled_time

    Usage in Pydantic model:
        @field_validator("scheduled_time")
        @classmethod
        def validate_time(cls, v):
            return scheduled_time_validator(cls, v)
    """
    if v is None:
        return v

    if not TIME_FORMAT_PATTERN.match(v):
        raise ValueError(f"Invalid time format: {v}. Expected HH:MM or HH:MM:SS")

    return v


def field_id_validator(cls: Any, v: str | None) -> str | None:
    """
    Pydantic validator for field_id field
    أداة التحقق من Pydantic لحقل field_id

    Usage in Pydantic model:
        @field_validator("field_id")
        @classmethod
        def validate_field_id(cls, v):
            return field_id_validator(cls, v)
    """
    if v is None:
        return v

    if len(v) > 100:
        raise ValueError("Field ID too long: max 100 characters")

    if not FIELD_ID_PATTERN.match(v):
        raise ValueError(f"Invalid field ID format: {v}. Only alphanumeric, underscore, and hyphen allowed")

    return v


def metadata_validator(cls: Any, v: dict | None) -> dict | None:
    """
    Pydantic validator for metadata field
    أداة التحقق من Pydantic لحقل metadata

    Usage in Pydantic model:
        @field_validator("metadata")
        @classmethod
        def validate_metadata(cls, v):
            return metadata_validator(cls, v)
    """
    if v is None:
        return v

    try:
        json_str = json.dumps(v, ensure_ascii=False)
        size = len(json_str.encode("utf-8"))

        if size > MAX_METADATA_SIZE_BYTES:
            raise ValueError(f"Metadata too large: {size} bytes (max {MAX_METADATA_SIZE_BYTES})")

    except (TypeError, ValueError) as e:
        if "too large" in str(e):
            raise
        raise ValueError(f"Metadata must be JSON serializable: {e}")

    return v


def date_string_validator(cls: Any, v: str | None) -> str | None:
    """
    Pydantic validator for date string fields
    أداة التحقق من Pydantic لحقول سلسلة التاريخ

    Usage in Pydantic model:
        @field_validator("date")
        @classmethod
        def validate_date(cls, v):
            return date_string_validator(cls, v)
    """
    if v is None:
        return v

    if not DATE_FORMAT_PATTERN.match(v):
        raise ValueError(f"Invalid date format: {v}. Expected YYYY-MM-DD")

    try:
        datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date: {v}")

    return v


# ═══════════════════════════════════════════════════════════════════════════
# Composite Validators - أدوات التحقق المركبة
# ═══════════════════════════════════════════════════════════════════════════


def validate_task_create_data(
    title: str,
    field_id: str | None = None,
    scheduled_time: str | None = None,
    metadata: dict | None = None,
) -> dict[str, Any]:
    """
    Validate all fields for task creation
    التحقق من جميع الحقول لإنشاء المهمة

    Args:
        title: Task title
        field_id: Optional field ID
        scheduled_time: Optional scheduled time
        metadata: Optional metadata

    Returns:
        dict: Validated data

    Raises:
        Various validation exceptions if data is invalid
    """
    errors = []

    # Validate title
    if not title or len(title.strip()) == 0:
        errors.append("Title is required")
    elif len(title) > 200:
        errors.append("Title must be 200 characters or less")

    # Validate field_id
    if field_id is not None:
        try:
            validate_field_id(field_id)
        except InvalidFieldIdError as e:
            errors.append(str(e))

    # Validate scheduled_time
    if scheduled_time is not None:
        try:
            validate_scheduled_time(scheduled_time)
        except InvalidTimeFormatError as e:
            errors.append(str(e))

    # Validate metadata
    if metadata is not None:
        try:
            validate_metadata_size(metadata)
        except MetadataTooLargeError as e:
            errors.append(str(e))

    if errors:
        from .exceptions import ValidationError

        raise ValidationError(
            field="task_data",
            message="; ".join(errors),
            message_ar="أخطاء في بيانات المهمة",
        )

    return {
        "title": title.strip(),
        "field_id": field_id,
        "scheduled_time": scheduled_time,
        "metadata": metadata,
    }
