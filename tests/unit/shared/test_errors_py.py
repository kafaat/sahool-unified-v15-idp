"""
Tests for SAHOOL Unified Error Handling Module
اختبارات وحدة معالجة الأخطاء الموحدة

Tests exception classes, error codes, and response formatting.
"""

import pytest

from shared.errors_py import (
    ErrorCode,
    ExternalServiceException,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
    SahoolException,
    UnauthorizedException,
    ValidationException,
    create_error_response,
    create_success_response,
)


# ═══════════════════════════════════════════════════════════════════════════════
# ErrorCode Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestErrorCode:
    """Test error code enum values."""

    def test_general_errors_1xxx(self):
        """General error codes start with E1."""
        assert ErrorCode.INTERNAL_ERROR == "E1001"
        assert ErrorCode.VALIDATION_ERROR == "E1002"
        assert ErrorCode.NOT_FOUND == "E1003"
        assert ErrorCode.CONFLICT == "E1004"

    def test_auth_errors_2xxx(self):
        """Auth error codes start with E2."""
        assert ErrorCode.UNAUTHORIZED == "E2001"
        assert ErrorCode.FORBIDDEN == "E2002"
        assert ErrorCode.TOKEN_EXPIRED == "E2003"

    def test_business_errors_3xxx(self):
        """Business error codes start with E3."""
        assert ErrorCode.BUSINESS_RULE_VIOLATION == "E3001"
        assert ErrorCode.QUOTA_EXCEEDED == "E3002"

    def test_external_errors_4xxx(self):
        """External service error codes start with E4."""
        assert ErrorCode.EXTERNAL_SERVICE_ERROR == "E4001"
        assert ErrorCode.DATABASE_ERROR == "E4002"

    def test_ai_errors_5xxx(self):
        """AI/ML error codes start with E5."""
        assert ErrorCode.AI_MODEL_ERROR == "E5001"
        assert ErrorCode.INFERENCE_TIMEOUT == "E5002"


# ═══════════════════════════════════════════════════════════════════════════════
# SahoolException Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSahoolException:
    """Test base exception class."""

    def test_basic_creation(self):
        """Exception can be created with message."""
        exc = SahoolException(message="Something went wrong")
        assert exc.message == "Something went wrong"
        assert exc.status_code == 500
        assert exc.code == ErrorCode.INTERNAL_ERROR

    def test_bilingual_message(self):
        """Exception supports Arabic message."""
        exc = SahoolException(
            message="Field not found",
            message_ar="الحقل غير موجود",
        )
        assert exc.message == "Field not found"
        assert exc.message_ar == "الحقل غير موجود"

    def test_arabic_defaults_to_english(self):
        """Arabic message defaults to English if not provided."""
        exc = SahoolException(message="Error occurred")
        assert exc.message_ar == "Error occurred"

    def test_custom_details(self):
        """Exception can carry additional details."""
        exc = SahoolException(
            message="Error",
            details={"field_id": "F-001", "reason": "invalid geometry"},
        )
        assert exc.details["field_id"] == "F-001"

    def test_inherits_from_exception(self):
        """SahoolException is a proper Exception subclass."""
        exc = SahoolException(message="test")
        assert isinstance(exc, Exception)
        assert str(exc) == "test"


# ═══════════════════════════════════════════════════════════════════════════════
# Specialized Exception Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidationException:
    """Test validation exception."""

    def test_defaults(self):
        """Validation exception has correct defaults."""
        exc = ValidationException(message="Invalid input")
        assert exc.status_code == 422
        assert exc.code == ErrorCode.VALIDATION_ERROR

    def test_with_details(self):
        """Validation exception with field details."""
        exc = ValidationException(
            message="Invalid area",
            details={"field": "area_hectares", "min": 0.1},
        )
        assert exc.details["field"] == "area_hectares"


class TestNotFoundException:
    """Test not found exception."""

    def test_defaults(self):
        """Not found exception has correct defaults."""
        exc = NotFoundException(message="Field not found")
        assert exc.status_code == 404
        assert exc.code == ErrorCode.NOT_FOUND

    def test_resource_info(self):
        """Resource type and ID are included in details."""
        exc = NotFoundException(
            message="Field not found",
            resource_type="field",
            resource_id="FIELD-001",
        )
        assert exc.details["resource_type"] == "field"
        assert exc.details["resource_id"] == "FIELD-001"


class TestUnauthorizedException:
    """Test unauthorized exception."""

    def test_defaults(self):
        """Unauthorized has correct defaults and bilingual messages."""
        exc = UnauthorizedException()
        assert exc.status_code == 401
        assert exc.code == ErrorCode.UNAUTHORIZED
        assert exc.message == "Authentication required"
        assert exc.message_ar == "المصادقة مطلوبة"


class TestForbiddenException:
    """Test forbidden exception."""

    def test_defaults(self):
        """Forbidden has correct defaults and bilingual messages."""
        exc = ForbiddenException()
        assert exc.status_code == 403
        assert exc.code == ErrorCode.FORBIDDEN
        assert exc.message == "Access denied"
        assert exc.message_ar == "الوصول مرفوض"


class TestExternalServiceException:
    """Test external service exception."""

    def test_defaults(self):
        """External service error has correct defaults."""
        exc = ExternalServiceException()
        assert exc.status_code == 502
        assert exc.code == ErrorCode.EXTERNAL_SERVICE_ERROR

    def test_weather_service_factory(self):
        """Weather service factory creates correct exception."""
        exc = ExternalServiceException.weather_service(
            error=ConnectionError("timeout"),
        )
        assert "Weather service" in exc.message
        assert "timeout" in exc.message
        assert exc.message_ar == "خطأ في خدمة الطقس"

    def test_weather_service_no_error(self):
        """Weather service factory without error arg."""
        exc = ExternalServiceException.weather_service()
        assert "unavailable" in exc.message


class TestInternalServerException:
    """Test internal server exception."""

    def test_defaults(self):
        """Internal server error has correct defaults."""
        exc = InternalServerException()
        assert exc.status_code == 500
        assert exc.message_ar == "خطأ داخلي في الخادم"


# ═══════════════════════════════════════════════════════════════════════════════
# Response Creation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCreateErrorResponse:
    """Test error response formatting."""

    def test_error_response_structure(self):
        """Error response has correct structure."""
        exc = NotFoundException(message="Not found", message_ar="غير موجود")
        response = create_error_response(exc, request_id="req-123")

        assert response.status_code == 404
        body = response.body
        assert b"success" in body
        assert b"false" in body
        assert b"req-123" in body

    def test_error_response_without_request_id(self):
        """Error response works without request ID."""
        exc = ValidationException(message="Bad input")
        response = create_error_response(exc)
        assert response.status_code == 422


class TestCreateSuccessResponse:
    """Test success response formatting."""

    def test_minimal_response(self):
        """Minimal success response."""
        result = create_success_response()
        assert result["success"] is True
        assert result["data"] is None

    def test_with_data(self):
        """Success response with data."""
        data = {"field_id": "F-001", "name": "حقل القمح"}
        result = create_success_response(data=data)
        assert result["success"] is True
        assert result["data"]["field_id"] == "F-001"

    def test_with_bilingual_message(self):
        """Success response with bilingual messages."""
        result = create_success_response(
            data=None,
            message="Field created",
            message_ar="تم إنشاء الحقل",
        )
        assert result["message"] == "Field created"
        assert result["message_ar"] == "تم إنشاء الحقل"

    def test_with_meta(self):
        """Success response with pagination meta."""
        result = create_success_response(
            data=[],
            meta={"page": 1, "total": 100, "per_page": 20},
        )
        assert result["meta"]["total"] == 100

    def test_no_optional_fields_when_none(self):
        """Optional fields are not included when None."""
        result = create_success_response(data="test")
        assert "message" not in result
        assert "message_ar" not in result
        assert "meta" not in result
