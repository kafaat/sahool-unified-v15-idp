"""
Unit tests for Task Service Exceptions
اختبارات الوحدة لاستثناءات خدمة المهام

Tests:
- Exception creation with proper attributes
- Bilingual message support (Arabic/English)
- Error code assignment
- HTTP status code mapping
- to_dict() method for API responses
"""

import pytest

# Import from the src package (conftest.py sets up the path)
try:
    from src.exceptions import (
        AstronomicalServiceError,
        AstronomicalServiceTimeoutError,
        CacheConnectionError,
        CacheError,
        DatabaseConnectionError,
        DatabaseError,
        ErrorCode,
        FieldServiceError,
        ForbiddenError,
        InvalidFieldIdError,
        InvalidTenantError,
        MetadataTooLargeError,
        NdviServiceError,
        TaskInvalidStatusError,
        TaskNotFoundError,
        TaskServiceError,
        UnauthorizedError,
        ValidationError,
    )
except ModuleNotFoundError:
    pytest.skip("Task service src module not found - run tests from service directory", allow_module_level=True)


class TestErrorCode:
    """Test ErrorCode enum"""

    def test_task_error_codes_exist(self):
        """Test that all task error codes are defined"""
        assert ErrorCode.TASK_NOT_FOUND.value == "TASK_NOT_FOUND"
        assert ErrorCode.TASK_ALREADY_EXISTS.value == "TASK_ALREADY_EXISTS"
        assert ErrorCode.TASK_INVALID_STATUS.value == "TASK_INVALID_STATUS"
        assert ErrorCode.TASK_INVALID_TRANSITION.value == "TASK_INVALID_TRANSITION"
        assert ErrorCode.TASK_CREATION_FAILED.value == "TASK_CREATION_FAILED"

    def test_validation_error_codes_exist(self):
        """Test that all validation error codes are defined"""
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.INVALID_FIELD_ID.value == "INVALID_FIELD_ID"
        assert ErrorCode.INVALID_DATE_FORMAT.value == "INVALID_DATE_FORMAT"
        assert ErrorCode.INVALID_TIME_FORMAT.value == "INVALID_TIME_FORMAT"
        assert ErrorCode.METADATA_TOO_LARGE.value == "METADATA_TOO_LARGE"

    def test_external_service_error_codes_exist(self):
        """Test that external service error codes are defined"""
        assert ErrorCode.ASTRONOMICAL_SERVICE_ERROR.value == "ASTRONOMICAL_SERVICE_ERROR"
        assert ErrorCode.ASTRONOMICAL_SERVICE_TIMEOUT.value == "ASTRONOMICAL_SERVICE_TIMEOUT"
        assert ErrorCode.FIELD_SERVICE_ERROR.value == "FIELD_SERVICE_ERROR"
        assert ErrorCode.NDVI_SERVICE_ERROR.value == "NDVI_SERVICE_ERROR"


class TestTaskServiceError:
    """Test base TaskServiceError exception"""

    def test_creation_with_defaults(self):
        """Test creating exception with default values"""
        exc = TaskServiceError(message="Test error")

        assert exc.message == "Test error"
        assert exc.message_ar == "Test error"  # Default to English if no Arabic
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.status_code == 400
        assert exc.details == {}

    def test_creation_with_all_params(self):
        """Test creating exception with all parameters"""
        exc = TaskServiceError(
            message="Test error",
            message_ar="خطأ اختبار",
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details={"key": "value"},
        )

        assert exc.message == "Test error"
        assert exc.message_ar == "خطأ اختبار"
        assert exc.error_code == ErrorCode.DATABASE_ERROR
        assert exc.status_code == 500
        assert exc.details == {"key": "value"}

    def test_to_dict_method(self):
        """Test to_dict() method for API responses"""
        exc = TaskServiceError(
            message="Test error",
            message_ar="خطأ اختبار",
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details={"field": "title"},
        )

        result = exc.to_dict()

        assert "error" in result
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert result["error"]["message"] == "Test error"
        assert result["error"]["message_ar"] == "خطأ اختبار"
        assert result["error"]["details"] == {"field": "title"}

    def test_str_representation(self):
        """Test string representation of exception"""
        exc = TaskServiceError(message="Test error")
        assert str(exc) == "Test error"


class TestTaskNotFoundError:
    """Test TaskNotFoundError exception"""

    def test_creation_with_task_id(self):
        """Test creating TaskNotFoundError with task ID"""
        exc = TaskNotFoundError(task_id="task_123")

        assert "task_123" in exc.message
        assert "task_123" in exc.message_ar
        assert exc.error_code == ErrorCode.TASK_NOT_FOUND
        assert exc.status_code == 404
        assert exc.details["task_id"] == "task_123"

    def test_creation_with_tenant_id(self):
        """Test creating TaskNotFoundError with tenant ID"""
        exc = TaskNotFoundError(task_id="task_123", tenant_id="tenant_abc")

        assert exc.details["task_id"] == "task_123"
        assert exc.details["tenant_id"] == "tenant_abc"


class TestTaskInvalidStatusError:
    """Test TaskInvalidStatusError exception"""

    def test_creation(self):
        """Test creating TaskInvalidStatusError"""
        exc = TaskInvalidStatusError(
            task_id="task_123",
            current_status="completed",
            expected_statuses=["pending", "in_progress"],
            operation="start",
        )

        assert "task_123" in exc.message
        assert "completed" in exc.message
        assert exc.error_code == ErrorCode.TASK_INVALID_STATUS
        assert exc.status_code == 400
        assert exc.details["task_id"] == "task_123"
        assert exc.details["current_status"] == "completed"
        assert exc.details["expected_statuses"] == ["pending", "in_progress"]
        assert exc.details["operation"] == "start"


class TestValidationError:
    """Test ValidationError exception"""

    def test_creation(self):
        """Test creating ValidationError"""
        exc = ValidationError(
            field="title",
            message="Title is required",
            message_ar="العنوان مطلوب",
        )

        assert "title" in exc.message
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.status_code == 400
        assert exc.details["field"] == "title"

    def test_value_type_included(self):
        """Test that value type is included but not value itself"""
        exc = ValidationError(
            field="title",
            message="Invalid value",
            value="sensitive_data",
        )

        assert "value_type" in exc.details
        assert exc.details["value_type"] == "str"
        assert "sensitive_data" not in str(exc.details)


class TestInvalidFieldIdError:
    """Test InvalidFieldIdError exception"""

    def test_creation(self):
        """Test creating InvalidFieldIdError"""
        exc = InvalidFieldIdError(field_id="invalid!@#field")

        assert "invalid" in exc.message.lower()
        assert exc.error_code == ErrorCode.INVALID_FIELD_ID
        assert exc.status_code == 400

    def test_truncation_for_long_ids(self):
        """Test that long field IDs are truncated"""
        long_id = "a" * 100
        exc = InvalidFieldIdError(field_id=long_id)

        assert len(exc.message) < 150  # Message should be reasonable length

    def test_empty_field_id(self):
        """Test handling empty field ID"""
        exc = InvalidFieldIdError(field_id="")

        assert "<empty>" in exc.message or "empty" in exc.message.lower()


class TestMetadataTooLargeError:
    """Test MetadataTooLargeError exception"""

    def test_creation(self):
        """Test creating MetadataTooLargeError"""
        exc = MetadataTooLargeError(size=100000, max_size=65536)

        assert "100000" in exc.message
        assert "65536" in exc.message
        assert exc.error_code == ErrorCode.METADATA_TOO_LARGE
        assert exc.details["size"] == 100000
        assert exc.details["max_size"] == 65536


class TestExternalServiceErrors:
    """Test external service error exceptions"""

    def test_astronomical_service_error(self):
        """Test AstronomicalServiceError"""
        exc = AstronomicalServiceError(message="Connection refused")

        assert exc.error_code == ErrorCode.ASTRONOMICAL_SERVICE_ERROR
        assert exc.status_code == 502
        assert "Astronomical" in exc.message

    def test_astronomical_service_timeout(self):
        """Test AstronomicalServiceTimeoutError"""
        exc = AstronomicalServiceTimeoutError()

        assert exc.error_code == ErrorCode.ASTRONOMICAL_SERVICE_TIMEOUT
        assert exc.status_code == 504
        assert "timeout" in exc.message.lower() or "مهلة" in exc.message_ar

    def test_field_service_error(self):
        """Test FieldServiceError"""
        exc = FieldServiceError(message="Not found", field_id="field_123")

        assert exc.error_code == ErrorCode.FIELD_SERVICE_ERROR
        assert exc.status_code == 502
        assert exc.details["field_id"] == "field_123"

    def test_ndvi_service_error(self):
        """Test NdviServiceError"""
        exc = NdviServiceError(message="Service unavailable")

        assert exc.error_code == ErrorCode.NDVI_SERVICE_ERROR
        assert exc.status_code == 502


class TestDatabaseErrors:
    """Test database error exceptions"""

    def test_database_error(self):
        """Test DatabaseError"""
        exc = DatabaseError(message="Connection lost", operation="insert")

        assert exc.error_code == ErrorCode.DATABASE_ERROR
        assert exc.status_code == 500
        assert exc.details["operation"] == "insert"

    def test_database_connection_error(self):
        """Test DatabaseConnectionError"""
        exc = DatabaseConnectionError()

        assert exc.error_code == ErrorCode.DATABASE_CONNECTION_ERROR
        assert exc.status_code == 500


class TestCacheErrors:
    """Test cache error exceptions"""

    def test_cache_error(self):
        """Test CacheError"""
        exc = CacheError(message="Timeout", operation="get")

        assert exc.error_code == ErrorCode.CACHE_ERROR
        assert exc.status_code == 500
        assert exc.details["operation"] == "get"

    def test_cache_connection_error(self):
        """Test CacheConnectionError"""
        exc = CacheConnectionError()

        assert exc.error_code == ErrorCode.CACHE_CONNECTION_ERROR


class TestAuthorizationErrors:
    """Test authorization error exceptions"""

    def test_unauthorized_error(self):
        """Test UnauthorizedError"""
        exc = UnauthorizedError()

        assert exc.error_code == ErrorCode.UNAUTHORIZED
        assert exc.status_code == 401

    def test_forbidden_error(self):
        """Test ForbiddenError"""
        exc = ForbiddenError(resource="task_123")

        assert exc.error_code == ErrorCode.FORBIDDEN
        assert exc.status_code == 403
        assert exc.details["resource"] == "task_123"

    def test_invalid_tenant_error(self):
        """Test InvalidTenantError"""
        exc = InvalidTenantError()

        assert exc.error_code == ErrorCode.INVALID_TENANT
        assert exc.status_code == 400
