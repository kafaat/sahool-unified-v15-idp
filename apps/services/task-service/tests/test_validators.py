"""
Comprehensive unit tests for Task Service validators module.
اختبارات شاملة لوحدة التحقق لخدمة المهام
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


class TestValidateFieldId:
    """Tests for validate_field_id function"""

    def test_valid_field_ids(self):
        assert validate_field_id("field_001") is True
        assert validate_field_id("field-north") is True
        assert validate_field_id("ABC123") is True
        assert validate_field_id("a") is True

    def test_none_allowed(self):
        assert validate_field_id(None) is True

    def test_empty_string_raises(self):
        with pytest.raises(InvalidFieldIdError):
            validate_field_id("")

    def test_special_chars_raises(self):
        with pytest.raises(InvalidFieldIdError):
            validate_field_id("field@bad!")

    def test_too_long_raises(self):
        with pytest.raises(InvalidFieldIdError):
            validate_field_id("x" * 101)

    def test_no_raise_mode(self):
        assert validate_field_id("bad@id", raise_exception=False) is False
        assert validate_field_id("", raise_exception=False) is False
        assert validate_field_id("x" * 101, raise_exception=False) is False

    def test_path_traversal_rejected(self):
        with pytest.raises(InvalidFieldIdError):
            validate_field_id("../etc/passwd")


class TestValidateScheduledTime:
    """Tests for validate_scheduled_time function"""

    def test_valid_times(self):
        assert validate_scheduled_time("08:00") is True
        assert validate_scheduled_time("23:59") is True
        assert validate_scheduled_time("00:00") is True
        assert validate_scheduled_time("08:30:45") is True

    def test_none_allowed(self):
        assert validate_scheduled_time(None) is True

    def test_invalid_times_raise(self):
        with pytest.raises(InvalidTimeFormatError):
            validate_scheduled_time("25:00")
        with pytest.raises(InvalidTimeFormatError):
            validate_scheduled_time("abc")
        with pytest.raises(InvalidTimeFormatError):
            validate_scheduled_time("8:0")  # single digit without leading zero still matches

    def test_no_raise_mode(self):
        assert validate_scheduled_time("25:00", raise_exception=False) is False
        assert validate_scheduled_time("not-time", raise_exception=False) is False


class TestValidateDateString:
    """Tests for validate_date_string function"""

    def test_valid_dates(self):
        assert validate_date_string("2025-01-15") is True
        assert validate_date_string("2024-12-31") is True

    def test_none_allowed(self):
        assert validate_date_string(None) is True

    def test_invalid_format_raises(self):
        with pytest.raises(InvalidDateFormatError):
            validate_date_string("15-01-2025")
        with pytest.raises(InvalidDateFormatError):
            validate_date_string("not-a-date")

    def test_invalid_date_value_raises(self):
        with pytest.raises(InvalidDateFormatError):
            validate_date_string("2025-02-30")  # Feb 30 doesn't exist

    def test_no_raise_mode(self):
        assert validate_date_string("bad", raise_exception=False) is False
        assert validate_date_string("2025-02-30", raise_exception=False) is False


class TestValidateMetadataSize:
    """Tests for validate_metadata_size function"""

    def test_valid_metadata(self):
        assert validate_metadata_size({"key": "value"}) is True
        assert validate_metadata_size({}) is True

    def test_none_allowed(self):
        assert validate_metadata_size(None) is True

    def test_too_large_raises(self):
        large_metadata = {"data": "x" * 70000}
        with pytest.raises(MetadataTooLargeError):
            validate_metadata_size(large_metadata)

    def test_no_raise_mode(self):
        large_metadata = {"data": "x" * 70000}
        assert validate_metadata_size(large_metadata, raise_exception=False) is False


class TestSanitizeForLog:
    """Tests for sanitize_for_log function"""

    def test_normal_string(self):
        assert sanitize_for_log("hello") == "hello"

    def test_none_value(self):
        assert sanitize_for_log(None) == "<none>"

    def test_newline_removal(self):
        result = sanitize_for_log("line1\nline2\rline3")
        assert "\n" not in result
        assert "\r" not in result

    def test_control_characters_removed(self):
        result = sanitize_for_log("test\x00\x01\x7f")
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x7f" not in result

    def test_truncation(self):
        long_str = "a" * 200
        result = sanitize_for_log(long_str, max_length=50)
        assert len(result) == 50

    def test_empty_after_sanitize(self):
        result = sanitize_for_log("\x00\x01\x02")
        assert result == "<empty>"

    def test_integer_input(self):
        assert sanitize_for_log(42) == "42"

    def test_float_input(self):
        assert sanitize_for_log(3.14) == "3.14"

    def test_whitespace_only(self):
        result = sanitize_for_log("   ")
        assert result == "<empty>"


class TestSanitizeFieldIdForUrl:
    """Tests for sanitize_field_id_for_url function"""

    def test_valid_id(self):
        assert sanitize_field_id_for_url("field_001") == "field_001"
        assert sanitize_field_id_for_url("field-north") == "field-north"

    def test_empty_string(self):
        assert sanitize_field_id_for_url("") == ""

    def test_special_chars_removed(self):
        result = sanitize_field_id_for_url("field../etc/passwd")
        assert "/" not in result
        assert ".." not in result

    def test_length_limited(self):
        result = sanitize_field_id_for_url("x" * 200)
        assert len(result) <= 100


class TestScheduledTimeValidator:
    """Tests for Pydantic scheduled_time_validator"""

    def test_valid_time(self):
        result = scheduled_time_validator(None, "08:30")
        assert result == "08:30"

    def test_none_returns_none(self):
        result = scheduled_time_validator(None, None)
        assert result is None

    def test_invalid_time_raises(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            scheduled_time_validator(None, "25:00")


class TestFieldIdValidator:
    """Tests for Pydantic field_id_validator"""

    def test_valid_id(self):
        result = field_id_validator(None, "field_abc")
        assert result == "field_abc"

    def test_none_returns_none(self):
        result = field_id_validator(None, None)
        assert result is None

    def test_too_long_raises(self):
        with pytest.raises(ValueError, match="too long"):
            field_id_validator(None, "x" * 101)

    def test_invalid_chars_raises(self):
        with pytest.raises(ValueError, match="Invalid field ID"):
            field_id_validator(None, "field@bad!")


class TestMetadataValidator:
    """Tests for Pydantic metadata_validator"""

    def test_valid_metadata(self):
        result = metadata_validator(None, {"key": "val"})
        assert result == {"key": "val"}

    def test_none_returns_none(self):
        result = metadata_validator(None, None)
        assert result is None

    def test_too_large_raises(self):
        with pytest.raises(ValueError, match="too large"):
            metadata_validator(None, {"data": "x" * 70000})


class TestDateStringValidator:
    """Tests for Pydantic date_string_validator"""

    def test_valid_date(self):
        result = date_string_validator(None, "2025-06-15")
        assert result == "2025-06-15"

    def test_none_returns_none(self):
        result = date_string_validator(None, None)
        assert result is None

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Invalid date format"):
            date_string_validator(None, "15/06/2025")

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError, match="Invalid date"):
            date_string_validator(None, "2025-02-30")


class TestValidateTaskCreateData:
    """Tests for validate_task_create_data composite validator"""

    def test_valid_data(self):
        result = validate_task_create_data(
            title="Test Task",
            field_id="field_001",
            scheduled_time="08:00",
            metadata={"key": "val"},
        )
        assert result["title"] == "Test Task"
        assert result["field_id"] == "field_001"

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="")

    def test_whitespace_title_raises(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="   ")

    def test_long_title_raises(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="x" * 201)

    def test_invalid_field_id_raises(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="Test", field_id="bad@id!")

    def test_invalid_time_raises(self):
        with pytest.raises(ValidationError):
            validate_task_create_data(title="Test", scheduled_time="99:99")

    def test_title_stripped(self):
        result = validate_task_create_data(title="  Test Task  ")
        assert result["title"] == "Test Task"


class TestPatternConstants:
    """Test regex pattern constants"""

    def test_field_id_pattern(self):
        assert FIELD_ID_PATTERN.match("abc_123-def")
        assert not FIELD_ID_PATTERN.match("abc@def")
        assert not FIELD_ID_PATTERN.match("")

    def test_time_format_pattern(self):
        assert TIME_FORMAT_PATTERN.match("08:30")
        assert TIME_FORMAT_PATTERN.match("23:59:59")
        assert not TIME_FORMAT_PATTERN.match("25:00")

    def test_date_format_pattern(self):
        assert DATE_FORMAT_PATTERN.match("2025-01-15")
        assert not DATE_FORMAT_PATTERN.match("15-01-2025")

    def test_max_metadata_size(self):
        assert MAX_METADATA_SIZE_BYTES == 65536
