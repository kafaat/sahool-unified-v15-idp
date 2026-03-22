"""Tests for YOLO26 Vision Service error handling."""

import pytest
from src.core.errors import (
    CircuitBreaker,
    ErrorCategory,
    ErrorCode,
    ModelError,
    RateLimitError,
    ResourceError,
    ValidationError,
    VisionError,
    VisionTimeoutError,
)


class TestErrorCodes:
    """Test error code definitions."""

    def test_validation_error_codes(self):
        """Validation error codes should start with E1."""
        assert ErrorCode.INVALID_IMAGE_FORMAT.value == "E1001"
        assert ErrorCode.IMAGE_TOO_LARGE.value == "E1002"

    def test_model_error_codes(self):
        """Model error codes should start with E2."""
        assert ErrorCode.MODEL_NOT_FOUND.value == "E2001"
        assert ErrorCode.INFERENCE_FAILED.value == "E2003"

    def test_timeout_error_codes(self):
        """Timeout error codes should start with E7."""
        assert ErrorCode.INFERENCE_TIMEOUT.value == "E7001"
        assert ErrorCode.REQUEST_TIMEOUT.value == "E7002"


class TestVisionError:
    """Test VisionError exception."""

    def test_bilingual_messages(self):
        """Error should have both English and Arabic messages."""
        error = VisionError(
            code=ErrorCode.INVALID_IMAGE_FORMAT,
            category=ErrorCategory.VALIDATION,
        )
        assert "Invalid image format" in error.message_en
        assert "تنسيق الصورة غير صالح" in error.message_ar

    def test_to_dict(self):
        """Error should serialize to dict correctly."""
        error = VisionError(
            code=ErrorCode.INVALID_IMAGE_FORMAT,
            category=ErrorCategory.VALIDATION,
        )
        result = error.to_dict()
        assert "error" in result
        assert result["error"]["code"] == "E1001"
        assert result["error"]["category"] == "validation"

    def test_message_params_substitution(self):
        """Error messages should support parameter substitution."""
        error = VisionError(
            code=ErrorCode.IMAGE_TOO_LARGE,
            category=ErrorCategory.VALIDATION,
            message_params={"max_size": 50},
        )
        assert "50" in error.message_en
        assert "50" in error.message_ar


class TestConvenienceErrors:
    """Test convenience error constructors."""

    def test_validation_error(self):
        """ValidationError should set correct category and status."""
        error = ValidationError(code=ErrorCode.INVALID_IMAGE_FORMAT)
        assert error.category == ErrorCategory.VALIDATION
        assert error.http_status == 400

    def test_model_error(self):
        """ModelError should set correct category and status."""
        error = ModelError(code=ErrorCode.MODEL_NOT_FOUND)
        assert error.category == ErrorCategory.MODEL
        assert error.http_status == 503

    def test_resource_error(self):
        """ResourceError should set correct category and retry_after."""
        error = ResourceError(code=ErrorCode.GPU_OUT_OF_MEMORY, retry_after=60)
        assert error.category == ErrorCategory.RESOURCE
        assert error.retry_after == 60

    def test_rate_limit_error(self):
        """RateLimitError should set correct status and retry_after."""
        error = RateLimitError(retry_after=120)
        assert error.http_status == 429
        assert error.retry_after == 120

    def test_vision_timeout_error(self):
        """VisionTimeoutError should not shadow built-in TimeoutError."""
        error = VisionTimeoutError(timeout=30.0)
        assert error.http_status == 504
        assert error.code == ErrorCode.INFERENCE_TIMEOUT
        # Verify it doesn't shadow the built-in
        assert VisionTimeoutError is not TimeoutError


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_initial_state_closed(self):
        """Circuit should start in closed state."""
        cb = CircuitBreaker(failure_threshold=3)
        assert not cb.is_open("test")

    def test_opens_after_threshold(self):
        """Circuit should open after reaching failure threshold."""
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure("test")
        assert cb.is_open("test")

    def test_success_resets_failures(self):
        """Success should reset failure count in closed state."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure("test")
        cb.record_failure("test")
        cb.record_success("test")
        assert not cb.is_open("test")

    def test_get_status(self):
        """Status should report all circuit states."""
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure("service_a")
        status = cb.get_status()
        assert "service_a" in status
        assert status["service_a"]["failures"] == 1
