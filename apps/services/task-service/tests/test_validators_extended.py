"""
Extended tests for src/validators.py
Tests all validation functions with valid/invalid inputs, edge cases, and
Pydantic validator decorators.
"""

import json

import pytest
from src.exceptions import (
    InvalidDateFormatError,
    InvalidFieldIdError,
    InvalidTimeFormatError,
    MetadataTooLargeError,
    ValidationError,
)
from src.validators import (
    CONTROL_CHAR_PATTERN,
    DATE_FORMAT_PATTERN,
    FIELD_ID_PATTERN,
    MAX_METADATA_SIZE_BYTES,
    TIME_FORMAT_PATTERN,
    date_string_validator,
    field_id_validator,
    metadata_validator,
    sanitize_field_id_for_url,
    sanitize_for_log,
    scheduled_time_validator,
    validate_date_string,
    validate_field_id,
    validate_metadata_size,
    validate_scheduled_time,
    validate_task_create_data,
)

# ── validate_field_id ──────────────────────────────────────────────────


class TestValidateFieldId:
    def test_none_is_valid(self):
        assert validate_field_id(None) is True

    def test_valid_alphanumeric(self):
        assert validate_field_id("field_123") is True
        assert validate_field_id("FIELD-abc") is True
        assert validate_field_id("a") is True

    def test_empty_string_raises(self):
        with pytest.raises(InvalidFieldIdError):
            validate_field_id("")

    def test_empty_string_no_raise(self):
        assert validate_field_id("", raise_exception=False) is False

    def test_too_long_raises(self):
        with pytest.raises(InvalidFieldIdError):
            validate_field_id("a" * 101)

    def test_too_long_no_raise(self):
        assert validate_field_id("a" * 101, raise_exception=False) is False

    def test_special_characters_raises(self):
        with pytest.raises(InvalidFieldIdError):
            validate_field_id("field@id")

    def test_special_characters_no_raise(self):
        assert validate_field_id("field@id", raise_exception=False) is False

    def test_100_chars_is_valid(self):
        assert validate_field_id("a" * 100) is True

    def test_spaces_invalid(self):
        assert validate_field_id("field id", raise_exception=False) is False

    def test_unicode_invalid(self):
        assert validate_field_id("حقل", raise_exception=False) is False


# ── validate_scheduled_time ────────────────────────────────────────────


class TestValidateScheduledTime:
    def test_none_is_valid(self):
        assert validate_scheduled_time(None) is True

    def test_valid_hhmm(self):
        assert validate_scheduled_time("08:30") is True
        assert validate_scheduled_time("23:59") is True
        assert validate_scheduled_time("0:00") is True

    def test_valid_hhmmss(self):
        assert validate_scheduled_time("08:30:00") is True
        assert validate_scheduled_time("23:59:59") is True

    def test_invalid_raises(self):
        with pytest.raises(InvalidTimeFormatError):
            validate_scheduled_time("25:00")

    def test_invalid_no_raise(self):
        assert validate_scheduled_time("25:00", raise_exception=False) is False

    def test_invalid_formats(self):
        assert validate_scheduled_time("abc", raise_exception=False) is False
        assert validate_scheduled_time("8:60", raise_exception=False) is False
        assert validate_scheduled_time("", raise_exception=False) is False


# ── validate_date_string ───────────────────────────────────────────────


class TestValidateDateString:
    def test_none_is_valid(self):
        assert validate_date_string(None) is True

    def test_valid_date(self):
        assert validate_date_string("2024-01-15") is True
        assert validate_date_string("2024-12-31") is True

    def test_invalid_format_raises(self):
        with pytest.raises(InvalidDateFormatError):
            validate_date_string("15-01-2024")

    def test_invalid_format_no_raise(self):
        assert validate_date_string("15-01-2024", raise_exception=False) is False

    def test_invalid_date_value(self):
        # Feb 30 doesn't exist
        with pytest.raises(InvalidDateFormatError):
            validate_date_string("2024-02-30")

    def test_invalid_date_no_raise(self):
        assert validate_date_string("2024-02-30", raise_exception=False) is False

    def test_empty_string(self):
        assert validate_date_string("", raise_exception=False) is False

    def test_leap_year(self):
        assert validate_date_string("2024-02-29") is True
        assert validate_date_string("2023-02-29", raise_exception=False) is False


# ── validate_metadata_size ─────────────────────────────────────────────


class TestValidateMetadataSize:
    def test_none_is_valid(self):
        assert validate_metadata_size(None) is True

    def test_small_metadata(self):
        assert validate_metadata_size({"key": "value"}) is True

    def test_empty_dict(self):
        assert validate_metadata_size({}) is True

    def test_oversized_raises(self):
        large = {"data": "x" * MAX_METADATA_SIZE_BYTES}
        with pytest.raises(MetadataTooLargeError):
            validate_metadata_size(large)

    def test_oversized_no_raise(self):
        large = {"data": "x" * MAX_METADATA_SIZE_BYTES}
        assert validate_metadata_size(large, raise_exception=False) is False

    def test_unicode_metadata(self):
        # Arabic characters take more bytes in UTF-8
        meta = {"name": "مرحبا" * 100}
        assert validate_metadata_size(meta) is True

    def test_non_serializable_raises(self):
        class Unserializable:
            pass

        with pytest.raises(MetadataTooLargeError):
            validate_metadata_size({"obj": Unserializable()})

    def test_non_serializable_no_raise(self):
        class Unserializable:
            pass

        assert validate_metadata_size({"obj": Unserializable()}, raise_exception=False) is False


# ── sanitize_for_log ───────────────────────────────────────────────────


class TestSanitizeForLog:
    def test_none_returns_none_tag(self):
        assert sanitize_for_log(None) == "<none>"

    def test_normal_string(self):
        assert sanitize_for_log("hello") == "hello"

    def test_newline_injection(self):
        result = sanitize_for_log("line1\nline2")
        assert "\n" not in result

    def test_carriage_return(self):
        result = sanitize_for_log("a\r\nb")
        assert "\r" not in result
        assert "\n" not in result

    def test_control_characters(self):
        result = sanitize_for_log("test\x00\x01\x7f")
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x7f" not in result

    def test_truncation(self):
        result = sanitize_for_log("a" * 200, max_length=50)
        assert len(result) == 50

    def test_no_truncation_when_short(self):
        assert sanitize_for_log("abc", max_length=100) == "abc"

    def test_empty_after_sanitize(self):
        result = sanitize_for_log("\x00\x01")
        assert result == "<empty>"

    def test_integer_input(self):
        assert sanitize_for_log(42) == "42"

    def test_float_input(self):
        assert sanitize_for_log(3.14) == "3.14"

    def test_whitespace_stripped(self):
        assert sanitize_for_log("  hello  ") == "hello"


# ── sanitize_field_id_for_url ──────────────────────────────────────────


class TestSanitizeFieldIdForUrl:
    def test_normal(self):
        assert sanitize_field_id_for_url("field_123") == "field_123"

    def test_empty(self):
        assert sanitize_field_id_for_url("") == ""

    def test_path_traversal(self):
        result = sanitize_field_id_for_url("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_special_chars_removed(self):
        result = sanitize_field_id_for_url("field@#$%^&*id")
        assert result == "fieldid"

    def test_length_limit(self):
        result = sanitize_field_id_for_url("a" * 200)
        assert len(result) == 100

    def test_hyphens_and_underscores_kept(self):
        result = sanitize_field_id_for_url("field-test_id")
        assert result == "field-test_id"


# ── Pydantic validator functions ───────────────────────────────────────


class TestScheduledTimeValidator:
    def test_none(self):
        assert scheduled_time_validator(None, None) is None

    def test_valid(self):
        assert scheduled_time_validator(None, "08:30") == "08:30"

    def test_invalid(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            scheduled_time_validator(None, "25:00")


class TestFieldIdValidator:
    def test_none(self):
        assert field_id_validator(None, None) is None

    def test_valid(self):
        assert field_id_validator(None, "field_1") == "field_1"

    def test_too_long(self):
        with pytest.raises(ValueError, match="too long"):
            field_id_validator(None, "a" * 101)

    def test_invalid_chars(self):
        with pytest.raises(ValueError, match="Invalid field ID"):
            field_id_validator(None, "bad@id")


class TestMetadataValidator:
    def test_none(self):
        assert metadata_validator(None, None) is None

    def test_valid(self):
        assert metadata_validator(None, {"key": "val"}) == {"key": "val"}

    def test_too_large(self):
        large = {"data": "x" * MAX_METADATA_SIZE_BYTES}
        with pytest.raises(ValueError, match="too large"):
            metadata_validator(None, large)

    def test_non_serializable(self):
        class Bad:
            pass

        with pytest.raises(ValueError, match="JSON serializable"):
            metadata_validator(None, {"obj": Bad()})


class TestDateStringValidator:
    def test_none(self):
        assert date_string_validator(None, None) is None

    def test_valid(self):
        assert date_string_validator(None, "2024-01-15") == "2024-01-15"

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            date_string_validator(None, "15/01/2024")

    def test_invalid_date(self):
        with pytest.raises(ValueError, match="Invalid date"):
            date_string_validator(None, "2024-02-30")


# ── validate_task_create_data ──────────────────────────────────────────


class TestValidateTaskCreateData:
    def test_valid_data(self):
        result = validate_task_create_data(title="Test Task")
        assert result["title"] == "Test Task"
        assert result["field_id"] is None

    def test_with_all_fields(self):
        result = validate_task_create_data(
            title="Test",
            field_id="field_1",
            scheduled_time="08:30",
            metadata={"key": "val"},
        )
        assert result["field_id"] == "field_1"
        assert result["scheduled_time"] == "08:30"

    def test_empty_title(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="")

    def test_whitespace_title(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="   ")

    def test_title_too_long(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="a" * 201)

    def test_invalid_field_id(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="task", field_id="bad@id")

    def test_invalid_time(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="task", scheduled_time="99:99")

    def test_oversized_metadata(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(
                title="task",
                metadata={"data": "x" * MAX_METADATA_SIZE_BYTES},
            )

    def test_title_stripped(self):
        result = validate_task_create_data(title="  Test Task  ")
        assert result["title"] == "Test Task"


# ── Pattern constants ──────────────────────────────────────────────────


class TestPatternConstants:
    def test_field_id_pattern(self):
        assert FIELD_ID_PATTERN.match("abc_123-DEF")
        assert not FIELD_ID_PATTERN.match("abc def")
        assert not FIELD_ID_PATTERN.match("a@b")

    def test_time_format_pattern(self):
        assert TIME_FORMAT_PATTERN.match("08:30")
        assert TIME_FORMAT_PATTERN.match("23:59:59")
        assert not TIME_FORMAT_PATTERN.match("25:00")

    def test_date_format_pattern(self):
        assert DATE_FORMAT_PATTERN.match("2024-01-15")
        assert not DATE_FORMAT_PATTERN.match("15-01-2024")

    def test_control_char_pattern(self):
        assert CONTROL_CHAR_PATTERN.search("\x00")
        assert CONTROL_CHAR_PATTERN.search("\x1f")
        assert CONTROL_CHAR_PATTERN.search("\x7f")
        assert not CONTROL_CHAR_PATTERN.search("a")

    def test_max_metadata_size(self):
        assert MAX_METADATA_SIZE_BYTES == 65536
