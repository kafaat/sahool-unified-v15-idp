"""
Comprehensive Error Handling Tests for SAHOOL Platform
اختبارات شاملة لمعالجة الأخطاء لمنصة سهول

Tests cover:
- ErrorCode enum values
- Exception classes (SahoolException, ValidationException, etc.)
- Bilingual error messages (Arabic/English)
- Error response creation
- Success response creation
- Exception handlers with FastAPI
- Request ID middleware
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.errors_py import (
    ErrorCode,
    ErrorResponse,
    ExternalServiceException,
    ForbiddenException,
    InternalServerException,
    NotFoundException,
    SahoolException,
    UnauthorizedException,
    ValidationException,
    add_request_id_middleware,
    create_error_response,
    create_success_response,
    setup_exception_handlers,
)


@pytest.mark.unit
class TestErrorCode:
    """Tests for ErrorCode enum"""

    def test_general_error_codes(self):
        """Test general error code values"""
        assert ErrorCode.INTERNAL_ERROR == "E1001"
        assert ErrorCode.VALIDATION_ERROR == "E1002"
        assert ErrorCode.NOT_FOUND == "E1003"
        assert ErrorCode.CONFLICT == "E1004"
        assert ErrorCode.METHOD_NOT_ALLOWED == "E1005"

    def test_auth_error_codes(self):
        """Test authentication error code values"""
        assert ErrorCode.UNAUTHORIZED == "E2001"
        assert ErrorCode.FORBIDDEN == "E2002"
        assert ErrorCode.TOKEN_EXPIRED == "E2003"
        assert ErrorCode.TOKEN_INVALID == "E2004"

    def test_business_error_codes(self):
        """Test business logic error code values"""
        assert ErrorCode.BUSINESS_RULE_VIOLATION == "E3001"
        assert ErrorCode.QUOTA_EXCEEDED == "E3002"
        assert ErrorCode.RESOURCE_EXHAUSTED == "E3003"

    def test_external_service_error_codes(self):
        """Test external service error codes"""
        assert ErrorCode.EXTERNAL_SERVICE_ERROR == "E4001"
        assert ErrorCode.DATABASE_ERROR == "E4002"
        assert ErrorCode.CACHE_ERROR == "E4003"
        assert ErrorCode.MESSAGING_ERROR == "E4004"

    def test_ai_error_codes(self):
        """Test AI/ML error codes"""
        assert ErrorCode.AI_MODEL_ERROR == "E5001"
        assert ErrorCode.INFERENCE_TIMEOUT == "E5002"
        assert ErrorCode.MODEL_NOT_AVAILABLE == "E5003"

    def test_error_code_is_string(self):
        """Test that error codes are string values"""
        for code in ErrorCode:
            assert isinstance(code.value, str)
            assert code.value.startswith("E")


@pytest.mark.unit
class TestSahoolException:
    """Tests for base SahoolException"""

    def test_basic_exception(self):
        """Test creating a basic SahoolException"""
        exc = SahoolException(message="Something went wrong")
        assert exc.message == "Something went wrong"
        assert exc.message_ar == "Something went wrong"  # Default fallback
        assert exc.code == ErrorCode.INTERNAL_ERROR
        assert exc.status_code == 500
        assert exc.details == {}

    def test_bilingual_exception(self):
        """Test exception with Arabic message"""
        exc = SahoolException(
            message="Field not found",
            message_ar="الحقل غير موجود",
        )
        assert exc.message == "Field not found"
        assert exc.message_ar == "الحقل غير موجود"

    def test_exception_with_custom_code(self):
        """Test exception with custom error code"""
        exc = SahoolException(
            message="Validation failed",
            code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
        )
        assert exc.code == ErrorCode.VALIDATION_ERROR
        assert exc.status_code == 422

    def test_exception_with_details(self):
        """Test exception with details dict"""
        exc = SahoolException(
            message="Error",
            details={"field": "name", "reason": "too_short"},
        )
        assert exc.details == {"field": "name", "reason": "too_short"}

    def test_exception_str(self):
        """Test exception string representation"""
        exc = SahoolException(message="Test error")
        assert str(exc) == "Test error"


@pytest.mark.unit
class TestValidationException:
    """Tests for ValidationException"""

    def test_default_status_code(self):
        """Test that validation exception has 422 status code"""
        exc = ValidationException(message="Invalid input")
        assert exc.status_code == 422
        assert exc.code == ErrorCode.VALIDATION_ERROR

    def test_with_arabic_message(self):
        """Test validation exception with Arabic"""
        exc = ValidationException(
            message="Invalid email format",
            message_ar="تنسيق البريد الإلكتروني غير صالح",
        )
        assert exc.message_ar == "تنسيق البريد الإلكتروني غير صالح"

    def test_with_details(self):
        """Test validation exception with field details"""
        exc = ValidationException(
            message="Validation failed",
            details={"fields": ["email", "phone"]},
        )
        assert exc.details == {"fields": ["email", "phone"]}


@pytest.mark.unit
class TestNotFoundException:
    """Tests for NotFoundException"""

    def test_default_status_code(self):
        """Test that not found exception has 404 status code"""
        exc = NotFoundException(message="Resource not found")
        assert exc.status_code == 404
        assert exc.code == ErrorCode.NOT_FOUND

    def test_with_resource_info(self):
        """Test not found exception with resource type and ID"""
        exc = NotFoundException(
            message="Field not found",
            message_ar="الحقل غير موجود",
            resource_type="field",
            resource_id="field-123",
        )
        assert exc.details["resource_type"] == "field"
        assert exc.details["resource_id"] == "field-123"

    def test_without_resource_info(self):
        """Test not found exception without resource info"""
        exc = NotFoundException(message="Not found")
        assert "resource_type" not in exc.details
        assert "resource_id" not in exc.details


@pytest.mark.unit
class TestUnauthorizedException:
    """Tests for UnauthorizedException"""

    def test_default_message(self):
        """Test default unauthorized message"""
        exc = UnauthorizedException()
        assert exc.message == "Authentication required"
        assert exc.message_ar == "المصادقة مطلوبة"
        assert exc.status_code == 401

    def test_custom_message(self):
        """Test custom unauthorized message"""
        exc = UnauthorizedException(
            message="Token expired",
            message_ar="انتهت صلاحية الرمز",
        )
        assert exc.message == "Token expired"


@pytest.mark.unit
class TestForbiddenException:
    """Tests for ForbiddenException"""

    def test_default_message(self):
        """Test default forbidden message"""
        exc = ForbiddenException()
        assert exc.message == "Access denied"
        assert exc.message_ar == "الوصول مرفوض"
        assert exc.status_code == 403


@pytest.mark.unit
class TestExternalServiceException:
    """Tests for ExternalServiceException"""

    def test_default_message(self):
        """Test default external service error"""
        exc = ExternalServiceException()
        assert exc.status_code == 502
        assert exc.code == ErrorCode.EXTERNAL_SERVICE_ERROR

    def test_weather_service_factory(self):
        """Test weather service error factory method"""
        exc = ExternalServiceException.weather_service(
            error=ConnectionError("timeout"),
        )
        assert "Weather service error" in exc.message
        assert exc.message_ar == "خطأ في خدمة الطقس"

    def test_weather_service_factory_no_error(self):
        """Test weather service factory without error"""
        exc = ExternalServiceException.weather_service()
        assert exc.message == "Weather service unavailable"


@pytest.mark.unit
class TestInternalServerException:
    """Tests for InternalServerException"""

    def test_default_message(self):
        """Test default internal server error"""
        exc = InternalServerException()
        assert exc.message == "Internal server error"
        assert exc.message_ar == "خطأ داخلي في الخادم"
        assert exc.status_code == 500


@pytest.mark.unit
class TestCreateErrorResponse:
    """Tests for error response creation"""

    def test_error_response_format(self):
        """Test that error response has correct format"""
        exc = SahoolException(
            message="Test error",
            message_ar="خطأ اختبار",
            code=ErrorCode.INTERNAL_ERROR,
        )
        response = create_error_response(exc, request_id="req-123")

        assert response.status_code == 500
        import json

        body = json.loads(response.body.decode())
        assert body["success"] is False
        assert body["error"]["code"] == "E1001"
        assert body["error"]["message"] == "Test error"
        assert body["error"]["message_ar"] == "خطأ اختبار"
        assert body["request_id"] == "req-123"

    def test_error_response_without_request_id(self):
        """Test error response without request ID"""
        exc = NotFoundException(message="Not found")
        response = create_error_response(exc)

        import json

        body = json.loads(response.body.decode())
        assert body["request_id"] is None


@pytest.mark.unit
class TestCreateSuccessResponse:
    """Tests for success response creation"""

    def test_basic_success_response(self):
        """Test basic success response"""
        response = create_success_response(data={"id": "123"})
        assert response["success"] is True
        assert response["data"] == {"id": "123"}

    def test_success_response_with_messages(self):
        """Test success response with bilingual messages"""
        response = create_success_response(
            data=None,
            message="Operation completed",
            message_ar="اكتملت العملية",
        )
        assert response["message"] == "Operation completed"
        assert response["message_ar"] == "اكتملت العملية"

    def test_success_response_with_meta(self):
        """Test success response with metadata"""
        response = create_success_response(
            data=[1, 2, 3],
            meta={"page": 1, "total": 100},
        )
        assert response["meta"] == {"page": 1, "total": 100}

    def test_success_response_without_optional_fields(self):
        """Test success response without optional fields"""
        response = create_success_response()
        assert response["success"] is True
        assert response["data"] is None
        assert "message" not in response
        assert "meta" not in response


@pytest.mark.unit
class TestExceptionHandlersIntegration:
    """Integration tests for FastAPI exception handlers"""

    def setup_method(self):
        """Set up a test FastAPI app with exception handlers"""
        self.app = FastAPI()
        setup_exception_handlers(self.app)
        add_request_id_middleware(self.app)

        @self.app.get("/validation-error")
        async def validation_error():
            raise ValidationException(
                message="Invalid input",
                message_ar="إدخال غير صالح",
                details={"field": "email"},
            )

        @self.app.get("/not-found")
        async def not_found():
            raise NotFoundException(
                message="Field not found",
                resource_type="field",
                resource_id="123",
            )

        @self.app.get("/unauthorized")
        async def unauthorized():
            raise UnauthorizedException()

        @self.app.get("/forbidden")
        async def forbidden():
            raise ForbiddenException()

        @self.app.get("/internal-error")
        async def internal_error():
            raise InternalServerException()

        @self.app.get("/generic-error")
        async def generic_error():
            raise RuntimeError("Unexpected error")

        @self.app.get("/ok")
        async def ok():
            return {"status": "ok"}

        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_validation_error_handler(self):
        """Test validation exception handler returns 422"""
        response = self.client.get("/validation-error")
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E1002"

    def test_not_found_handler(self):
        """Test not found exception handler returns 404"""
        response = self.client.get("/not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["details"]["resource_type"] == "field"

    def test_unauthorized_handler(self):
        """Test unauthorized exception handler returns 401"""
        response = self.client.get("/unauthorized")
        assert response.status_code == 401

    def test_forbidden_handler(self):
        """Test forbidden exception handler returns 403"""
        response = self.client.get("/forbidden")
        assert response.status_code == 403

    def test_internal_error_handler(self):
        """Test internal error handler returns 500"""
        response = self.client.get("/internal-error")
        assert response.status_code == 500

    def test_generic_error_handler(self):
        """Test generic exception handler catches unhandled errors"""
        response = self.client.get("/generic-error")
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "E1001"
        assert data["error"]["message"] == "An unexpected error occurred"

    def test_request_id_middleware_generates_id(self):
        """Test that request ID middleware generates an ID"""
        response = self.client.get("/ok")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_request_id_middleware_preserves_existing_id(self):
        """Test that existing request ID is preserved"""
        response = self.client.get("/ok", headers={"X-Request-ID": "custom-req-id"})
        assert response.headers["X-Request-ID"] == "custom-req-id"

    def test_request_id_in_error_response(self):
        """Test that request ID appears in error responses"""
        response = self.client.get(
            "/validation-error",
            headers={"X-Request-ID": "trace-123"},
        )
        data = response.json()
        assert data["request_id"] == "trace-123"
