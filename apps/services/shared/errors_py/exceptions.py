"""
Custom Exception Classes
فئات الاستثناءات المخصصة

@module shared/errors_py
@description Custom exception classes with bilingual support
"""

from datetime import datetime
from typing import Any, Dict, Optional
from .error_codes import ErrorCode, ERROR_REGISTRY, BilingualMessage


class AppException(Exception):
    """
    Base Application Exception
    الاستثناء الأساسي للتطبيق
    """

    def __init__(
        self,
        error_code: ErrorCode,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        metadata = ERROR_REGISTRY[error_code]

        if custom_message:
            self.message_en = custom_message.en
            self.message_ar = custom_message.ar
        else:
            self.message_en = metadata.message.en
            self.message_ar = metadata.message.ar

        self.error_code = error_code
        self.http_status = metadata.http_status
        self.retryable = metadata.retryable
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.path: Optional[str] = None

        super().__init__(self.message_en)

    def to_dict(self) -> Dict[str, Any]:
        """
        Get error response object
        الحصول على كائن استجابة الخطأ
        """
        return {
            "success": False,
            "error": {
                "code": self.error_code.value,
                "message": self.message_en,
                "messageAr": self.message_ar,
                "retryable": self.retryable,
                "details": self.details if self.details else None,
                "timestamp": self.timestamp,
                "path": self.path,
            },
        }


class ValidationException(AppException):
    """
    Validation Exception
    استثناء التحقق من صحة البيانات
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)

    @classmethod
    def from_field_errors(
        cls,
        field_errors: list[Dict[str, str]],
    ) -> "ValidationException":
        """
        Create validation exception from field errors
        إنشاء استثناء التحقق من أخطاء الحقول
        """
        return cls(
            ErrorCode.VALIDATION_ERROR,
            details={"fields": field_errors},
        )


class AuthenticationException(AppException):
    """
    Authentication Exception
    استثناء المصادقة
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.AUTHENTICATION_FAILED,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)


class AuthorizationException(AppException):
    """
    Authorization Exception
    استثناء التفويض
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.FORBIDDEN,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)


class NotFoundException(AppException):
    """
    Not Found Exception
    استثناء عدم العثور على المورد
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)

    @classmethod
    def user(cls, user_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for user not found"""
        return cls(ErrorCode.USER_NOT_FOUND, details={"userId": user_id})

    @classmethod
    def farm(cls, farm_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for farm not found"""
        return cls(ErrorCode.FARM_NOT_FOUND, details={"farmId": farm_id})

    @classmethod
    def field(cls, field_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for field not found"""
        return cls(ErrorCode.FIELD_NOT_FOUND, details={"fieldId": field_id})

    @classmethod
    def crop(cls, crop_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for crop not found"""
        return cls(ErrorCode.CROP_NOT_FOUND, details={"cropId": crop_id})

    @classmethod
    def sensor(cls, sensor_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for sensor not found"""
        return cls(ErrorCode.SENSOR_NOT_FOUND, details={"sensorId": sensor_id})

    @classmethod
    def conversation(cls, conversation_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for conversation not found"""
        return cls(ErrorCode.CONVERSATION_NOT_FOUND, details={"conversationId": conversation_id})

    @classmethod
    def message(cls, message_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for message not found"""
        return cls(ErrorCode.MESSAGE_NOT_FOUND, details={"messageId": message_id})

    @classmethod
    def wallet(cls, wallet_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for wallet not found"""
        return cls(ErrorCode.WALLET_NOT_FOUND, details={"walletId": wallet_id})

    @classmethod
    def order(cls, order_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for order not found"""
        return cls(ErrorCode.ORDER_NOT_FOUND, details={"orderId": order_id})

    @classmethod
    def product(cls, product_id: Optional[str] = None) -> "NotFoundException":
        """Create exception for product not found"""
        return cls(ErrorCode.PRODUCT_NOT_FOUND, details={"productId": product_id})


class ConflictException(AppException):
    """
    Conflict Exception
    استثناء التعارض
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.RESOURCE_ALREADY_EXISTS,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)


class BusinessLogicException(AppException):
    """
    Business Logic Exception
    استثناء منطق الأعمال
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.BUSINESS_RULE_VIOLATION,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)

    @classmethod
    def insufficient_balance(
        cls,
        available: float,
        required: float,
    ) -> "BusinessLogicException":
        """Create exception for insufficient balance"""
        return cls(
            ErrorCode.INSUFFICIENT_BALANCE,
            details={"available": available, "required": required},
        )

    @classmethod
    def amount_must_be_positive(cls, amount: float) -> "BusinessLogicException":
        """Create exception for invalid amount"""
        return cls(
            ErrorCode.AMOUNT_MUST_BE_POSITIVE,
            details={"amount": amount},
        )

    @classmethod
    def invalid_state_transition(
        cls,
        current_state: str,
        target_state: str,
    ) -> "BusinessLogicException":
        """Create exception for invalid state transition"""
        return cls(
            ErrorCode.INVALID_STATE_TRANSITION,
            details={"currentState": current_state, "targetState": target_state},
        )

    @classmethod
    def operation_not_allowed(
        cls,
        operation: str,
        reason: Optional[str] = None,
    ) -> "BusinessLogicException":
        """Create exception for operation not allowed"""
        return cls(
            ErrorCode.OPERATION_NOT_ALLOWED,
            details={"operation": operation, "reason": reason},
        )


class ExternalServiceException(AppException):
    """
    External Service Exception
    استثناء الخدمة الخارجية
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)

    @classmethod
    def weather_service(cls, error: Optional[Any] = None) -> "ExternalServiceException":
        """Create exception for weather service error"""
        return cls(
            ErrorCode.WEATHER_SERVICE_UNAVAILABLE,
            details={"originalError": str(error)} if error else None,
        )

    @classmethod
    def satellite_service(cls, error: Optional[Any] = None) -> "ExternalServiceException":
        """Create exception for satellite service error"""
        return cls(
            ErrorCode.SATELLITE_SERVICE_UNAVAILABLE,
            details={"originalError": str(error)} if error else None,
        )

    @classmethod
    def payment_gateway(cls, error: Optional[Any] = None) -> "ExternalServiceException":
        """Create exception for payment gateway error"""
        return cls(
            ErrorCode.PAYMENT_GATEWAY_ERROR,
            details={"originalError": str(error)} if error else None,
        )

    @classmethod
    def sms_service(cls, error: Optional[Any] = None) -> "ExternalServiceException":
        """Create exception for SMS service error"""
        return cls(
            ErrorCode.SMS_SERVICE_ERROR,
            details={"originalError": str(error)} if error else None,
        )

    @classmethod
    def email_service(cls, error: Optional[Any] = None) -> "ExternalServiceException":
        """Create exception for email service error"""
        return cls(
            ErrorCode.EMAIL_SERVICE_ERROR,
            details={"originalError": str(error)} if error else None,
        )


class DatabaseException(AppException):
    """
    Database Exception
    استثناء قاعدة البيانات
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.DATABASE_ERROR,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)

    @classmethod
    def from_database_error(cls, error: Any) -> "DatabaseException":
        """
        Create exception from database error
        إنشاء استثناء من خطأ قاعدة البيانات
        """
        error_str = str(error).lower()

        # Check for specific database errors
        if "unique constraint" in error_str or "duplicate key" in error_str:
            return cls(ErrorCode.UNIQUE_CONSTRAINT_VIOLATION)
        elif "foreign key" in error_str:
            return cls(ErrorCode.FOREIGN_KEY_VIOLATION)
        elif "timeout" in error_str:
            return cls(ErrorCode.QUERY_TIMEOUT)
        elif "connection" in error_str:
            return cls(ErrorCode.DATABASE_CONNECTION_FAILED)
        else:
            return cls(
                ErrorCode.DATABASE_ERROR,
                details={"originalError": str(error)},
            )


class InternalServerException(AppException):
    """
    Internal Server Exception
    استثناء الخادم الداخلي
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)


class RateLimitException(AppException):
    """
    Rate Limit Exception
    استثناء تجاوز الحد المسموح
    """

    def __init__(
        self,
        error_code: ErrorCode = ErrorCode.RATE_LIMIT_EXCEEDED,
        custom_message: Optional[BilingualMessage] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(error_code, custom_message, details)

    @classmethod
    def with_retry_after(cls, retry_after_seconds: int) -> "RateLimitException":
        """
        Create exception with retry information
        إنشاء استثناء مع معلومات إعادة المحاولة
        """
        retry_after_date = datetime.utcnow()
        retry_after_date = retry_after_date.replace(
            second=retry_after_date.second + retry_after_seconds
        )

        return cls(
            ErrorCode.RATE_LIMIT_EXCEEDED,
            details={
                "retryAfter": retry_after_seconds,
                "retryAfterDate": retry_after_date.isoformat(),
            },
        )
