"""
Extended tests for src/exceptions.py
Tests all exception classes, error codes, bilingual messages, and to_dict serialization.
"""

import pytest
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

# ── ErrorCode enum ──────────────────────────────────────────────────────


class TestErrorCode:
    def test_all_error_codes_exist(self):
        codes = [
            "TASK_NOT_FOUND",
            "TASK_ALREADY_EXISTS",
            "TASK_INVALID_STATUS",
            "TASK_INVALID_TRANSITION",
            "TASK_CREATION_FAILED",
            "TASK_UPDATE_FAILED",
            "VALIDATION_ERROR",
            "INVALID_FIELD_ID",
            "INVALID_DATE_FORMAT",
            "INVALID_TIME_FORMAT",
            "INVALID_PRIORITY",
            "METADATA_TOO_LARGE",
            "ASTRONOMICAL_SERVICE_ERROR",
            "ASTRONOMICAL_SERVICE_TIMEOUT",
            "FIELD_SERVICE_ERROR",
            "NOTIFICATION_SERVICE_ERROR",
            "NDVI_SERVICE_ERROR",
            "DATABASE_ERROR",
            "DATABASE_CONNECTION_ERROR",
            "CACHE_ERROR",
            "CACHE_CONNECTION_ERROR",
            "UNAUTHORIZED",
            "FORBIDDEN",
            "INVALID_TENANT",
        ]
        for code in codes:
            assert hasattr(ErrorCode, code)

    def test_error_code_is_string(self):
        assert ErrorCode.TASK_NOT_FOUND == "TASK_NOT_FOUND"
        assert isinstance(ErrorCode.TASK_NOT_FOUND, str)


# ── TaskServiceError (base) ────────────────────────────────────────────


class TestTaskServiceError:
    def test_default_values(self):
        exc = TaskServiceError(message="test error")
        assert exc.message == "test error"
        assert exc.message_ar == "test error"  # defaults to message
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.status_code == 400
        assert exc.details == {}

    def test_custom_values(self):
        exc = TaskServiceError(
            message="something failed",
            message_ar="حدث خطأ",
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details={"key": "val"},
        )
        assert exc.message == "something failed"
        assert exc.message_ar == "حدث خطأ"
        assert exc.status_code == 500
        assert exc.details == {"key": "val"}

    def test_to_dict(self):
        exc = TaskServiceError(message="err", message_ar="خطأ")
        d = exc.to_dict()
        assert "error" in d
        assert d["error"]["code"] == ErrorCode.VALIDATION_ERROR.value
        assert d["error"]["message"] == "err"
        assert d["error"]["message_ar"] == "خطأ"
        assert d["error"]["details"] == {}

    def test_is_exception(self):
        exc = TaskServiceError(message="x")
        assert isinstance(exc, Exception)
        assert str(exc) == "x"


# ── Task-specific exceptions ───────────────────────────────────────────


class TestTaskNotFoundError:
    def test_basic(self):
        exc = TaskNotFoundError("task-123")
        assert exc.status_code == 404
        assert exc.error_code == ErrorCode.TASK_NOT_FOUND
        assert "task-123" in exc.message
        assert "task-123" in exc.message_ar
        assert exc.details["task_id"] == "task-123"

    def test_with_tenant(self):
        exc = TaskNotFoundError("task-123", tenant_id="tenant-1")
        assert exc.details["tenant_id"] == "tenant-1"

    def test_without_tenant(self):
        exc = TaskNotFoundError("t1")
        assert "tenant_id" not in exc.details


class TestTaskAlreadyExistsError:
    def test_basic(self):
        exc = TaskAlreadyExistsError("task-456")
        assert exc.status_code == 409
        assert exc.error_code == ErrorCode.TASK_ALREADY_EXISTS
        assert "task-456" in exc.message


class TestTaskInvalidStatusError:
    def test_basic(self):
        exc = TaskInvalidStatusError("t1", "pending", ["in_progress"], "start")
        assert exc.status_code == 400
        assert exc.error_code == ErrorCode.TASK_INVALID_STATUS
        assert exc.details["current_status"] == "pending"
        assert exc.details["expected_statuses"] == ["in_progress"]
        assert exc.details["operation"] == "start"


class TestTaskInvalidTransitionError:
    def test_basic(self):
        exc = TaskInvalidTransitionError("t1", "completed", "pending")
        assert exc.status_code == 400
        assert exc.error_code == ErrorCode.TASK_INVALID_TRANSITION
        assert exc.details["from_status"] == "completed"
        assert exc.details["to_status"] == "pending"


class TestTaskCreationError:
    def test_basic(self):
        exc = TaskCreationError("db failure")
        assert exc.status_code == 500
        assert exc.error_code == ErrorCode.TASK_CREATION_FAILED
        assert "db failure" in exc.message

    def test_with_arabic(self):
        exc = TaskCreationError("db failure", reason_ar="فشل قاعدة البيانات")
        assert "فشل قاعدة البيانات" in exc.message_ar


# ── Validation exceptions ──────────────────────────────────────────────


class TestValidationError:
    def test_basic(self):
        exc = ValidationError(field="title", message="required")
        assert exc.status_code == 400
        assert exc.error_code == ErrorCode.VALIDATION_ERROR
        assert exc.details["field"] == "title"

    def test_with_value(self):
        exc = ValidationError(field="x", message="bad", value=42)
        assert exc.details["value_type"] == "int"

    def test_without_value(self):
        exc = ValidationError(field="x", message="bad")
        assert "value_type" not in exc.details


class TestInvalidFieldIdError:
    def test_basic(self):
        exc = InvalidFieldIdError("bad@id")
        assert exc.error_code == ErrorCode.INVALID_FIELD_ID
        assert "bad@id" in exc.message

    def test_empty(self):
        exc = InvalidFieldIdError("")
        assert "<empty>" in exc.message

    def test_long_field_id_truncated(self):
        long_id = "a" * 100
        exc = InvalidFieldIdError(long_id)
        assert len(exc.message) < 200  # truncated at 50 chars


class TestInvalidDateFormatError:
    def test_basic(self):
        exc = InvalidDateFormatError("not-a-date")
        assert exc.error_code == ErrorCode.INVALID_DATE_FORMAT
        assert exc.status_code == 400

    def test_custom_format(self):
        exc = InvalidDateFormatError("bad", expected_format="DD/MM/YYYY")
        assert "DD/MM/YYYY" in exc.message


class TestInvalidTimeFormatError:
    def test_basic(self):
        exc = InvalidTimeFormatError("25:00")
        assert exc.error_code == ErrorCode.INVALID_TIME_FORMAT
        assert exc.details["field"] == "scheduled_time"


class TestMetadataTooLargeError:
    def test_basic(self):
        exc = MetadataTooLargeError(100000, 65536)
        assert exc.error_code == ErrorCode.METADATA_TOO_LARGE
        assert exc.details["size"] == 100000
        assert exc.details["max_size"] == 65536


# ── External service exceptions ────────────────────────────────────────


class TestExternalServiceError:
    def test_basic(self):
        exc = ExternalServiceError(service_name="TestSvc", message="down")
        assert exc.status_code == 502
        assert exc.details["service"] == "TestSvc"
        assert "TestSvc" in exc.message

    def test_with_details(self):
        exc = ExternalServiceError(
            service_name="S",
            message="err",
            details={"extra": 1},
        )
        assert exc.details["extra"] == 1
        assert exc.details["service"] == "S"


class TestAstronomicalServiceError:
    def test_basic(self):
        exc = AstronomicalServiceError("service down")
        assert exc.status_code == 502
        assert exc.error_code == ErrorCode.ASTRONOMICAL_SERVICE_ERROR


class TestAstronomicalServiceTimeoutError:
    def test_basic(self):
        exc = AstronomicalServiceTimeoutError()
        assert exc.status_code == 504
        assert exc.error_code == ErrorCode.ASTRONOMICAL_SERVICE_TIMEOUT


class TestFieldServiceError:
    def test_basic(self):
        exc = FieldServiceError("not found")
        assert exc.status_code == 502
        assert exc.error_code == ErrorCode.FIELD_SERVICE_ERROR

    def test_with_field_id(self):
        exc = FieldServiceError("err", field_id="f1")
        assert exc.details["field_id"] == "f1"

    def test_long_field_id_truncated(self):
        exc = FieldServiceError("err", field_id="a" * 100)
        assert len(exc.details["field_id"]) == 50


class TestNdviServiceError:
    def test_basic(self):
        exc = NdviServiceError("err")
        assert exc.error_code == ErrorCode.NDVI_SERVICE_ERROR

    def test_with_field_id(self):
        exc = NdviServiceError("err", field_id="f1")
        assert exc.details["field_id"] == "f1"


class TestNotificationServiceError:
    def test_basic(self):
        exc = NotificationServiceError("failed")
        assert exc.error_code == ErrorCode.NOTIFICATION_SERVICE_ERROR
        assert exc.status_code == 502


# ── Database exceptions ────────────────────────────────────────────────


class TestDatabaseError:
    def test_basic(self):
        exc = DatabaseError("timeout")
        assert exc.status_code == 500
        assert exc.error_code == ErrorCode.DATABASE_ERROR

    def test_with_operation(self):
        exc = DatabaseError("err", operation="insert")
        assert exc.details["operation"] == "insert"


class TestDatabaseConnectionError:
    def test_basic(self):
        exc = DatabaseConnectionError()
        assert exc.error_code == ErrorCode.DATABASE_CONNECTION_ERROR
        assert exc.details["operation"] == "connect"


# ── Cache exceptions ───────────────────────────────────────────────────


class TestCacheError:
    def test_basic(self):
        exc = CacheError("timeout")
        assert exc.status_code == 500
        assert exc.error_code == ErrorCode.CACHE_ERROR

    def test_with_operation(self):
        exc = CacheError("err", operation="get")
        assert exc.details["operation"] == "get"


class TestCacheConnectionError:
    def test_basic(self):
        exc = CacheConnectionError()
        assert exc.error_code == ErrorCode.CACHE_CONNECTION_ERROR
        assert exc.details["operation"] == "connect"


# ── Auth exceptions ────────────────────────────────────────────────────


class TestUnauthorizedError:
    def test_default(self):
        exc = UnauthorizedError()
        assert exc.status_code == 401
        assert exc.error_code == ErrorCode.UNAUTHORIZED

    def test_custom_message(self):
        exc = UnauthorizedError("Token expired")
        assert exc.message == "Token expired"


class TestForbiddenError:
    def test_default(self):
        exc = ForbiddenError()
        assert exc.status_code == 403
        assert exc.error_code == ErrorCode.FORBIDDEN

    def test_custom_resource(self):
        exc = ForbiddenError("tasks")
        assert "tasks" in exc.message
        assert exc.details["resource"] == "tasks"


class TestInvalidTenantError:
    def test_basic(self):
        exc = InvalidTenantError()
        assert exc.status_code == 400
        assert exc.error_code == ErrorCode.INVALID_TENANT

    def test_with_tenant_id(self):
        exc = InvalidTenantError(tenant_id="bad-id")
        assert exc.status_code == 400
