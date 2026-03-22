"""
Unit tests for Task Service Validators
اختبارات الوحدة لأدوات التحقق من خدمة المهام

Tests:
- Field ID validation
- Scheduled time validation
- Date string validation
- Metadata size validation
- Log sanitization
"""

import pytest

# Import from the src package (conftest.py sets up the path)
try:
    from src.exceptions import (
        InvalidDateFormatError,
        InvalidFieldIdError,
        InvalidTimeFormatError,
        MetadataTooLargeError,
        ValidationError,
    )
    from src.validators import (
        MAX_METADATA_SIZE_BYTES,
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
except ModuleNotFoundError:
    pytest.skip("Task service src module not found - run tests from service directory", allow_module_level=True)


class TestFieldIdValidation:
    """Test field_id validation"""

    def test_valid_field_ids(self):
        """Test that valid field IDs pass validation"""
        valid_ids = [
            "field_001",
            "field-123",
            "FIELD_ABC",
            "my_field_2024",
            "a",
            "field123",
        ]

        for field_id in valid_ids:
            assert validate_field_id(field_id) is True

    def test_none_is_valid(self):
        """Test that None is valid (optional field)"""
        assert validate_field_id(None) is True

    def test_invalid_field_ids_with_exception(self):
        """Test that invalid field IDs raise exception by default"""
        invalid_ids = [
            "field/001",
            "field@123",
            "../etc/passwd",
            "field id",
            "field\nid",
            "a" * 101,  # Too long
        ]

        for field_id in invalid_ids:
            with pytest.raises(InvalidFieldIdError):
                validate_field_id(field_id)

    def test_invalid_field_ids_without_exception(self):
        """Test that invalid field IDs return False when not raising"""
        invalid_ids = [
            "field/001",
            "field@123",
            "",
            "a" * 101,
        ]

        for field_id in invalid_ids:
            assert validate_field_id(field_id, raise_exception=False) is False


class TestScheduledTimeValidation:
    """Test scheduled_time validation"""

    def test_valid_times(self):
        """Test that valid times pass validation"""
        valid_times = [
            "00:00",
            "06:30",
            "12:00",
            "23:59",
            "9:45",  # Single digit hour
            "06:30:00",  # With seconds
            "12:00:45",
        ]

        for time_str in valid_times:
            assert validate_scheduled_time(time_str) is True

    def test_none_is_valid(self):
        """Test that None is valid (optional field)"""
        assert validate_scheduled_time(None) is True

    def test_invalid_times_with_exception(self):
        """Test that invalid times raise exception by default"""
        invalid_times = [
            "25:00",  # Invalid hour
            "12:60",  # Invalid minute
            "12:00:60",  # Invalid second
            "12",  # Missing minute
            "twelve:00",
            "12-00",
            "",
        ]

        for time_str in invalid_times:
            with pytest.raises(InvalidTimeFormatError):
                validate_scheduled_time(time_str)

    def test_invalid_times_without_exception(self):
        """Test that invalid times return False when not raising"""
        invalid_times = [
            "25:00",
            "12:60",
            "invalid",
        ]

        for time_str in invalid_times:
            assert validate_scheduled_time(time_str, raise_exception=False) is False


class TestDateStringValidation:
    """Test date string validation"""

    def test_valid_dates(self):
        """Test that valid dates pass validation"""
        valid_dates = [
            "2024-01-15",
            "2025-12-31",
            "2000-06-01",
        ]

        for date_str in valid_dates:
            assert validate_date_string(date_str) is True

    def test_none_is_valid(self):
        """Test that None is valid (optional field)"""
        assert validate_date_string(None) is True

    def test_invalid_date_format(self):
        """Test that invalid date formats raise exception"""
        invalid_dates = [
            "01-15-2024",  # Wrong order
            "2024/01/15",  # Wrong separator
            "2024-1-15",  # Single digit month
            "2024-01-1",  # Single digit day
            "not-a-date",
        ]

        for date_str in invalid_dates:
            with pytest.raises(InvalidDateFormatError):
                validate_date_string(date_str)

    def test_invalid_date_values(self):
        """Test that invalid date values raise exception"""
        invalid_dates = [
            "2024-13-01",  # Invalid month
            "2024-02-30",  # Invalid day for February
            "2024-00-15",  # Zero month
        ]

        for date_str in invalid_dates:
            with pytest.raises(InvalidDateFormatError):
                validate_date_string(date_str)


class TestMetadataSizeValidation:
    """Test metadata size validation"""

    def test_valid_metadata(self):
        """Test that small metadata passes validation"""
        valid_metadata = [
            {"key": "value"},
            {"a": 1, "b": 2, "c": [1, 2, 3]},
            {},
        ]

        for metadata in valid_metadata:
            assert validate_metadata_size(metadata) is True

    def test_none_is_valid(self):
        """Test that None is valid (optional field)"""
        assert validate_metadata_size(None) is True

    def test_large_metadata_raises_exception(self):
        """Test that large metadata raises exception"""
        # Create metadata larger than limit
        large_metadata = {"data": "x" * MAX_METADATA_SIZE_BYTES}

        with pytest.raises(MetadataTooLargeError):
            validate_metadata_size(large_metadata)

    def test_large_metadata_returns_false(self):
        """Test that large metadata returns False when not raising"""
        large_metadata = {"data": "x" * MAX_METADATA_SIZE_BYTES}

        assert validate_metadata_size(large_metadata, raise_exception=False) is False


class TestSanitizeForLog:
    """Test log sanitization function"""

    def test_normal_strings(self):
        """Test that normal strings pass through"""
        assert sanitize_for_log("normal_string") == "normal_string"
        assert sanitize_for_log("field_123") == "field_123"

    def test_none_handling(self):
        """Test that None returns placeholder"""
        assert sanitize_for_log(None) == "<none>"

    def test_newline_removal(self):
        """Test that newlines are removed"""
        input_str = "line1\nline2\rline3"
        result = sanitize_for_log(input_str)

        assert "\n" not in result
        assert "\r" not in result

    def test_control_char_removal(self):
        """Test that control characters are removed"""
        input_str = "hello\x00world\x1ftest"
        result = sanitize_for_log(input_str)

        assert "\x00" not in result
        assert "\x1f" not in result

    def test_truncation(self):
        """Test that long strings are truncated"""
        long_string = "a" * 200
        result = sanitize_for_log(long_string, max_length=100)

        assert len(result) == 100

    def test_custom_max_length(self):
        """Test custom max length"""
        long_string = "a" * 100
        result = sanitize_for_log(long_string, max_length=50)

        assert len(result) == 50


class TestSanitizeFieldIdForUrl:
    """Test URL sanitization for field IDs"""

    def test_valid_field_ids(self):
        """Test that valid IDs pass through"""
        assert sanitize_field_id_for_url("field_123") == "field_123"
        assert sanitize_field_id_for_url("field-abc") == "field-abc"

    def test_special_chars_removed(self):
        """Test that special characters are removed"""
        assert sanitize_field_id_for_url("field/../../etc") == "fieldetc"
        assert sanitize_field_id_for_url("field@#$%123") == "field123"

    def test_empty_string(self):
        """Test handling empty string"""
        assert sanitize_field_id_for_url("") == ""

    def test_truncation(self):
        """Test that long IDs are truncated"""
        long_id = "a" * 200
        result = sanitize_field_id_for_url(long_id)

        assert len(result) == 100


class TestPydanticValidators:
    """Test Pydantic validator decorators"""

    def test_scheduled_time_validator_valid(self):
        """Test scheduled_time_validator with valid input"""
        assert scheduled_time_validator(None, "12:30") == "12:30"
        assert scheduled_time_validator(None, "06:00:00") == "06:00:00"

    def test_scheduled_time_validator_none(self):
        """Test scheduled_time_validator with None"""
        assert scheduled_time_validator(None, None) is None

    def test_scheduled_time_validator_invalid(self):
        """Test scheduled_time_validator with invalid input"""
        with pytest.raises(ValueError):
            scheduled_time_validator(None, "25:00")

    def test_field_id_validator_valid(self):
        """Test field_id_validator with valid input"""
        assert field_id_validator(None, "field_123") == "field_123"

    def test_field_id_validator_none(self):
        """Test field_id_validator with None"""
        assert field_id_validator(None, None) is None

    def test_field_id_validator_invalid(self):
        """Test field_id_validator with invalid input"""
        with pytest.raises(ValueError):
            field_id_validator(None, "field/invalid")

    def test_metadata_validator_valid(self):
        """Test metadata_validator with valid input"""
        metadata = {"key": "value"}
        assert metadata_validator(None, metadata) == metadata

    def test_metadata_validator_none(self):
        """Test metadata_validator with None"""
        assert metadata_validator(None, None) is None

    def test_metadata_validator_too_large(self):
        """Test metadata_validator with too large input"""
        large_metadata = {"data": "x" * MAX_METADATA_SIZE_BYTES}

        with pytest.raises(ValueError, match="too large"):
            metadata_validator(None, large_metadata)


class TestCompositeValidation:
    """Test composite validation function"""

    def test_valid_task_data(self):
        """Test validate_task_create_data with valid data"""
        result = validate_task_create_data(
            title="Test Task",
            field_id="field_123",
            scheduled_time="12:30",
            metadata={"key": "value"},
        )

        assert result["title"] == "Test Task"
        assert result["field_id"] == "field_123"

    def test_title_whitespace_trimmed(self):
        """Test that title whitespace is trimmed"""
        result = validate_task_create_data(title="  Test Task  ")
        assert result["title"] == "Test Task"

    def test_empty_title_raises_error(self):
        """Test that empty title raises error"""
        with pytest.raises(ValidationError):
            validate_task_create_data(title="")

        with pytest.raises(ValidationError):
            validate_task_create_data(title="   ")

    def test_title_too_long_raises_error(self):
        """Test that long title raises error"""
        with pytest.raises(ValidationError):
            validate_task_create_data(title="x" * 201)
