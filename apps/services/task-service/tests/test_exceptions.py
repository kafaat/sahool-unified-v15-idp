"""
Comprehensive unit tests for Task Service exceptions module.
اختبارات شاملة لوحدة استثناءات خدمة المهام
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.exceptions import (
    AstronomicalServiceError,
    AstronomicalServiceTimeoutError,
    CacheConnectionError,
    CacheError,
    DatabaseConnectionError,
    DatabaseError,
    ErrorCode,
    ExternalServiceError,
    FieldServiceError,
    ForbiddenError,
    InvalidDateFormatError,
    InvalidFieldIdError,
    InvalidTenantError,
    InvalidTimeFormatError,
    MetadataTooLargeError,
    NdviServiceError,
    NotificationServiceError,
    TaskAlreadyExistsError,
    TaskCreationError,
    TaskInvalidStatusError,
    TaskInvalidTransitionError,
    TaskNotFoundError,
    TaskServiceError,
    UnauthorizedError,
    ValidationError,
)


class TestErrorCode:
    """Tests for ErrorCode enum"""

    def test_task_error_codes(self):
        assert ErrorCode.TASK_NOT_FOUND == "TASK_NOT_FOUND"
        assert ErrorCode.TASK_ALREADY_EXISTS == "TASK_ALREADY_EXISTS"
        assert ErrorCode.TASK_INVALID_STATUS == "TASK_INVALID_STATUS"
        assert ErrorCode.TASK_INVALID_TRANSITION == "TASK_INVALID_TRANSITION"
        assert ErrorCode.TASK_CREATION_FAILED == "TASK_CREATION_FAILED"
        assert ErrorCode.TASK_UPDATE_FAILED == "TASK_UPDATE_FAILED"

    def test_validation_error_codes(self):
        assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"
        assert ErrorCode.INVALID_FIELD_ID == "INVALID_FIELD_ID"
        assert ErrorCode.INVALID_DATE_FORMAT == "INVALID_DATE_FORMAT"
        assert ErrorCode.INVALID_TIME_FORMAT == "INVALID_TIME_FORMAT"
        assert ErrorCode.INVALID_PRIORITY == "INVALID_PRIORITY"
        assert ErrorCode.METADATA_TOO_LARGE == "METADATA_TOO_LARGE"

    def test_external_service_error_codes(self):
        assert ErrorCode.ASTRONOMICAL_SERVICE_ERROR == "ASTRONOMICAL_SERVICE_ERROR"
        assert ErrorCode.NDVI_SERVICE_ERROR == "NDVI_SERVICE_ERROR"
        assert ErrorCode.DATABASE_ERROR == "DATABASE_ERROR"


class TestTaskServiceError:
    """Tests for base TaskServiceError"""

    def test_basic_error(self):
        err = TaskServiceError("Something failed")
        assert err.message == "Something failed"
        assert err.message_ar == "Something failed"  # defaults to message
        assert err.status_code == 400
        assert err.error_code == ErrorCode.VALIDATION_ERROR
        assert err.details == {}

    def test_error_with_arabic(self):
        err = TaskServiceError(
            "Failed",
            message_ar="فشل",
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details={"key": "value"},
        )
        assert err.message == "Failed"
        assert err.message_ar == "فشل"
        assert err.status_code == 500
        assert err.details == {"key": "value"}

    def test_to_dict(self):
        err = TaskServiceError("test", error_code=ErrorCode.TASK_NOT_FOUND, status_code=404)
        d = err.to_dict()
        assert "error" in d
        assert d["error"]["code"] == "TASK_NOT_FOUND"
        assert d["error"]["message"] == "test"
        assert d["error"]["message_ar"] == "test"
        assert d["error"]["details"] == {}

    def test_str_representation(self):
        err = TaskServiceError("Something went wrong")
        assert str(err) == "Something went wrong"


class TestTaskNotFoundError:
    def test_basic(self):
        err = TaskNotFoundError("task_123")
        assert err.status_code == 404
        assert "task_123" in err.message
        assert err.error_code == ErrorCode.TASK_NOT_FOUND
        assert err.details["task_id"] == "task_123"

    def test_with_tenant(self):
        err = TaskNotFoundError("task_123", tenant_id="tenant_abc")
        assert err.details["tenant_id"] == "tenant_abc"


class TestTaskAlreadyExistsError:
    def test_basic(self):
        err = TaskAlreadyExistsError("task_123")
        assert err.status_code == 409
        assert "task_123" in err.message
        assert err.error_code == ErrorCode.TASK_ALREADY_EXISTS


class TestTaskInvalidStatusError:
    def test_basic(self):
        err = TaskInvalidStatusError("task_1", "completed", ["pending"], "start")
        assert err.status_code == 400
        assert "completed" in err.message
        assert "pending" in err.message
        assert err.details["current_status"] == "completed"
        assert err.details["expected_statuses"] == ["pending"]
        assert err.details["operation"] == "start"


class TestTaskInvalidTransitionError:
    def test_basic(self):
        err = TaskInvalidTransitionError("task_1", "completed", "pending")
        assert err.status_code == 400
        assert "completed" in err.message
        assert "pending" in err.message
        assert err.details["from_status"] == "completed"
        assert err.details["to_status"] == "pending"


class TestTaskCreationError:
    def test_basic(self):
        err = TaskCreationError("db error")
        assert err.status_code == 500
        assert "db error" in err.message
        assert err.error_code == ErrorCode.TASK_CREATION_FAILED

    def test_with_arabic(self):
        err = TaskCreationError("db error", reason_ar="خطأ قاعدة بيانات")
        assert "خطأ قاعدة بيانات" in err.message_ar


class TestValidationError:
    def test_basic(self):
        err = ValidationError(field="title", message="required")
        assert err.status_code == 400
        assert err.details["field"] == "title"

    def test_with_value(self):
        err = ValidationError(field="age", message="invalid", value=123)
        assert err.details["value_type"] == "int"

    def test_without_value(self):
        err = ValidationError(field="name", message="empty")
        assert "value_type" not in err.details


class TestInvalidFieldIdError:
    def test_basic(self):
        err = InvalidFieldIdError("bad@id!")
        assert err.error_code == ErrorCode.INVALID_FIELD_ID

    def test_long_id_truncated(self):
        long_id = "x" * 100
        err = InvalidFieldIdError(long_id)
        assert len(err.message) < 200  # truncated in safe_id


class TestInvalidDateFormatError:
    def test_basic(self):
        err = InvalidDateFormatError("not-a-date")
        assert err.error_code == ErrorCode.INVALID_DATE_FORMAT
        assert "YYYY-MM-DD" in err.message


class TestInvalidTimeFormatError:
    def test_basic(self):
        err = InvalidTimeFormatError("99:99")
        assert err.error_code == ErrorCode.INVALID_TIME_FORMAT
        assert "HH:MM" in err.message


class TestMetadataTooLargeError:
    def test_basic(self):
        err = MetadataTooLargeError(100000, 65536)
        assert err.error_code == ErrorCode.METADATA_TOO_LARGE
        assert err.details["size"] == 100000
        assert err.details["max_size"] == 65536


class TestExternalServiceError:
    def test_basic(self):
        err = ExternalServiceError("TestService", "connection refused")
        assert err.status_code == 502
        assert "TestService" in err.message
        assert err.details["service"] == "TestService"


class TestAstronomicalServiceError:
    def test_basic(self):
        err = AstronomicalServiceError("unavailable")
        assert err.status_code == 502
        assert err.error_code == ErrorCode.ASTRONOMICAL_SERVICE_ERROR


class TestAstronomicalServiceTimeoutError:
    def test_basic(self):
        err = AstronomicalServiceTimeoutError()
        assert err.status_code == 504
        assert err.error_code == ErrorCode.ASTRONOMICAL_SERVICE_TIMEOUT


class TestFieldServiceError:
    def test_basic(self):
        err = FieldServiceError("not found", field_id="field_123")
        assert err.status_code == 502
        assert err.details["field_id"] == "field_123"

    def test_without_field_id(self):
        err = FieldServiceError("error")
        assert "field_id" not in err.details


class TestNdviServiceError:
    def test_basic(self):
        err = NdviServiceError("timeout", field_id="f1")
        assert err.error_code == ErrorCode.NDVI_SERVICE_ERROR
        assert err.details["field_id"] == "f1"


class TestNotificationServiceError:
    def test_basic(self):
        err = NotificationServiceError("send failed")
        assert err.error_code == ErrorCode.NOTIFICATION_SERVICE_ERROR


class TestDatabaseError:
    def test_basic(self):
        err = DatabaseError("connection lost")
        assert err.status_code == 500
        assert err.error_code == ErrorCode.DATABASE_ERROR

    def test_with_operation(self):
        err = DatabaseError("timeout", operation="insert")
        assert err.details["operation"] == "insert"


class TestDatabaseConnectionError:
    def test_basic(self):
        err = DatabaseConnectionError()
        assert err.error_code == ErrorCode.DATABASE_CONNECTION_ERROR
        assert err.details["operation"] == "connect"


class TestCacheError:
    def test_basic(self):
        err = CacheError("connection refused")
        assert err.status_code == 500
        assert err.error_code == ErrorCode.CACHE_ERROR

    def test_with_operation(self):
        err = CacheError("timeout", operation="get")
        assert err.details["operation"] == "get"


class TestCacheConnectionError:
    def test_basic(self):
        err = CacheConnectionError()
        assert err.error_code == ErrorCode.CACHE_CONNECTION_ERROR


class TestUnauthorizedError:
    def test_basic(self):
        err = UnauthorizedError()
        assert err.status_code == 401
        assert err.error_code == ErrorCode.UNAUTHORIZED

    def test_custom_message(self):
        err = UnauthorizedError("Token expired")
        assert "Token expired" in err.message


class TestForbiddenError:
    def test_basic(self):
        err = ForbiddenError("tasks")
        assert err.status_code == 403
        assert err.error_code == ErrorCode.FORBIDDEN
        assert err.details["resource"] == "tasks"


class TestInvalidTenantError:
    def test_basic(self):
        err = InvalidTenantError()
        assert err.status_code == 400
        assert err.error_code == ErrorCode.INVALID_TENANT
