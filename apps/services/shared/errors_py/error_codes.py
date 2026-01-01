"""
Error Codes and HTTP Status Mapping
أكواد الأخطاء وربطها بحالات HTTP

@module shared/errors_py
@description Centralized error code definitions with bilingual messages
"""

from enum import Enum
from typing import Dict, List, NamedTuple
from http import HTTPStatus


class ErrorCategory(str, Enum):
    """Error Code Categories - فئات أكواد الأخطاء"""
    VALIDATION = "VALIDATION"           # أخطاء التحقق من صحة البيانات
    AUTHENTICATION = "AUTHENTICATION"   # أخطاء المصادقة
    AUTHORIZATION = "AUTHORIZATION"     # أخطاء التفويض
    NOT_FOUND = "NOT_FOUND"             # الموارد غير الموجودة
    CONFLICT = "CONFLICT"               # تعارض في البيانات
    BUSINESS_LOGIC = "BUSINESS_LOGIC"   # أخطاء منطق الأعمال
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"  # أخطاء الخدمات الخارجية
    DATABASE = "DATABASE"               # أخطاء قاعدة البيانات
    INTERNAL = "INTERNAL"               # أخطاء داخلية
    RATE_LIMIT = "RATE_LIMIT"           # تجاوز الحد المسموح


class ErrorCode(str, Enum):
    """Application Error Codes - أكواد أخطاء التطبيق"""

    # Validation Errors (1000-1999) - أخطاء التحقق
    VALIDATION_ERROR = "ERR_1000"
    INVALID_INPUT = "ERR_1001"
    MISSING_REQUIRED_FIELD = "ERR_1002"
    INVALID_FORMAT = "ERR_1003"
    INVALID_EMAIL = "ERR_1004"
    INVALID_PHONE = "ERR_1005"
    INVALID_DATE = "ERR_1006"
    INVALID_RANGE = "ERR_1007"
    INVALID_ENUM_VALUE = "ERR_1008"

    # Authentication Errors (2000-2999) - أخطاء المصادقة
    AUTHENTICATION_FAILED = "ERR_2000"
    INVALID_CREDENTIALS = "ERR_2001"
    TOKEN_EXPIRED = "ERR_2002"
    TOKEN_INVALID = "ERR_2003"
    TOKEN_MISSING = "ERR_2004"
    SESSION_EXPIRED = "ERR_2005"
    ACCOUNT_LOCKED = "ERR_2006"
    ACCOUNT_DISABLED = "ERR_2007"
    EMAIL_NOT_VERIFIED = "ERR_2008"

    # Authorization Errors (3000-3999) - أخطاء التفويض
    FORBIDDEN = "ERR_3000"
    INSUFFICIENT_PERMISSIONS = "ERR_3001"
    ACCESS_DENIED = "ERR_3002"
    TENANT_MISMATCH = "ERR_3003"
    ROLE_REQUIRED = "ERR_3004"
    SUBSCRIPTION_REQUIRED = "ERR_3005"
    QUOTA_EXCEEDED = "ERR_3006"

    # Not Found Errors (4000-4999) - أخطاء العناصر غير الموجودة
    RESOURCE_NOT_FOUND = "ERR_4000"
    USER_NOT_FOUND = "ERR_4001"
    FARM_NOT_FOUND = "ERR_4002"
    FIELD_NOT_FOUND = "ERR_4003"
    CROP_NOT_FOUND = "ERR_4004"
    SENSOR_NOT_FOUND = "ERR_4005"
    CONVERSATION_NOT_FOUND = "ERR_4006"
    MESSAGE_NOT_FOUND = "ERR_4007"
    WALLET_NOT_FOUND = "ERR_4008"
    ORDER_NOT_FOUND = "ERR_4009"
    PRODUCT_NOT_FOUND = "ERR_4010"

    # Conflict Errors (5000-5999) - أخطاء التعارض
    RESOURCE_ALREADY_EXISTS = "ERR_5000"
    DUPLICATE_EMAIL = "ERR_5001"
    DUPLICATE_PHONE = "ERR_5002"
    CONCURRENT_MODIFICATION = "ERR_5003"
    VERSION_MISMATCH = "ERR_5004"

    # Business Logic Errors (6000-6999) - أخطاء منطق الأعمال
    BUSINESS_RULE_VIOLATION = "ERR_6000"
    INSUFFICIENT_BALANCE = "ERR_6001"
    INVALID_STATE_TRANSITION = "ERR_6002"
    OPERATION_NOT_ALLOWED = "ERR_6003"
    AMOUNT_MUST_BE_POSITIVE = "ERR_6004"
    PLANTING_DATE_INVALID = "ERR_6005"
    HARVEST_DATE_BEFORE_PLANTING = "ERR_6006"
    FIELD_ALREADY_HAS_CROP = "ERR_6007"
    ESCROW_ALREADY_EXISTS = "ERR_6008"
    LOAN_NOT_ACTIVE = "ERR_6009"
    PAYMENT_NOT_PENDING = "ERR_6010"

    # External Service Errors (7000-7999) - أخطاء الخدمات الخارجية
    EXTERNAL_SERVICE_ERROR = "ERR_7000"
    WEATHER_SERVICE_UNAVAILABLE = "ERR_7001"
    SATELLITE_SERVICE_UNAVAILABLE = "ERR_7002"
    PAYMENT_GATEWAY_ERROR = "ERR_7003"
    SMS_SERVICE_ERROR = "ERR_7004"
    EMAIL_SERVICE_ERROR = "ERR_7005"
    MAPS_SERVICE_ERROR = "ERR_7006"

    # Database Errors (8000-8999) - أخطاء قاعدة البيانات
    DATABASE_ERROR = "ERR_8000"
    DATABASE_CONNECTION_FAILED = "ERR_8001"
    QUERY_TIMEOUT = "ERR_8002"
    TRANSACTION_FAILED = "ERR_8003"
    CONSTRAINT_VIOLATION = "ERR_8004"
    FOREIGN_KEY_VIOLATION = "ERR_8005"
    UNIQUE_CONSTRAINT_VIOLATION = "ERR_8006"

    # Internal Errors (9000-9999) - الأخطاء الداخلية
    INTERNAL_SERVER_ERROR = "ERR_9000"
    SERVICE_UNAVAILABLE = "ERR_9001"
    CONFIGURATION_ERROR = "ERR_9002"
    NOT_IMPLEMENTED = "ERR_9003"
    DEPENDENCY_FAILED = "ERR_9004"

    # Rate Limiting (10000-10999) - تجاوز الحد المسموح
    RATE_LIMIT_EXCEEDED = "ERR_10000"
    TOO_MANY_REQUESTS = "ERR_10001"
    API_QUOTA_EXCEEDED = "ERR_10002"


class BilingualMessage(NamedTuple):
    """Bilingual Error Message - رسالة خطأ ثنائية اللغة"""
    en: str  # English message
    ar: str  # Arabic message - الرسالة العربية


class ErrorCodeMetadata(NamedTuple):
    """Error Code Metadata - بيانات كود الخطأ الوصفية"""
    code: ErrorCode
    category: ErrorCategory
    http_status: int
    message: BilingualMessage
    retryable: bool


# Error Code Registry - سجل أكواد الأخطاء
ERROR_REGISTRY: Dict[ErrorCode, ErrorCodeMetadata] = {
    # Validation Errors
    ErrorCode.VALIDATION_ERROR: ErrorCodeMetadata(
        code=ErrorCode.VALIDATION_ERROR,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Validation error occurred",
            ar="حدث خطأ في التحقق من صحة البيانات"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_INPUT: ErrorCodeMetadata(
        code=ErrorCode.INVALID_INPUT,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Invalid input provided",
            ar="تم تقديم بيانات غير صالحة"
        ),
        retryable=False,
    ),
    ErrorCode.MISSING_REQUIRED_FIELD: ErrorCodeMetadata(
        code=ErrorCode.MISSING_REQUIRED_FIELD,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Required field is missing",
            ar="حقل مطلوب غير موجود"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_FORMAT: ErrorCodeMetadata(
        code=ErrorCode.INVALID_FORMAT,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Invalid format",
            ar="تنسيق غير صالح"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_EMAIL: ErrorCodeMetadata(
        code=ErrorCode.INVALID_EMAIL,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Invalid email format",
            ar="تنسيق البريد الإلكتروني غير صالح"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_PHONE: ErrorCodeMetadata(
        code=ErrorCode.INVALID_PHONE,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Invalid phone number format",
            ar="تنسيق رقم الهاتف غير صالح"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_DATE: ErrorCodeMetadata(
        code=ErrorCode.INVALID_DATE,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Invalid date format",
            ar="تنسيق التاريخ غير صالح"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_RANGE: ErrorCodeMetadata(
        code=ErrorCode.INVALID_RANGE,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Value is outside the valid range",
            ar="القيمة خارج النطاق الصحيح"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_ENUM_VALUE: ErrorCodeMetadata(
        code=ErrorCode.INVALID_ENUM_VALUE,
        category=ErrorCategory.VALIDATION,
        http_status=HTTPStatus.BAD_REQUEST,
        message=BilingualMessage(
            en="Invalid enum value",
            ar="قيمة التعداد غير صالحة"
        ),
        retryable=False,
    ),

    # Authentication Errors
    ErrorCode.AUTHENTICATION_FAILED: ErrorCodeMetadata(
        code=ErrorCode.AUTHENTICATION_FAILED,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Authentication failed",
            ar="فشلت المصادقة"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_CREDENTIALS: ErrorCodeMetadata(
        code=ErrorCode.INVALID_CREDENTIALS,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Invalid credentials provided",
            ar="بيانات اعتماد غير صالحة"
        ),
        retryable=False,
    ),
    ErrorCode.TOKEN_EXPIRED: ErrorCodeMetadata(
        code=ErrorCode.TOKEN_EXPIRED,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Authentication token has expired",
            ar="انتهت صلاحية رمز المصادقة"
        ),
        retryable=False,
    ),
    ErrorCode.TOKEN_INVALID: ErrorCodeMetadata(
        code=ErrorCode.TOKEN_INVALID,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Invalid authentication token",
            ar="رمز مصادقة غير صالح"
        ),
        retryable=False,
    ),
    ErrorCode.TOKEN_MISSING: ErrorCodeMetadata(
        code=ErrorCode.TOKEN_MISSING,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Authentication token is missing",
            ar="رمز المصادقة مفقود"
        ),
        retryable=False,
    ),
    ErrorCode.SESSION_EXPIRED: ErrorCodeMetadata(
        code=ErrorCode.SESSION_EXPIRED,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Session has expired",
            ar="انتهت صلاحية الجلسة"
        ),
        retryable=False,
    ),
    ErrorCode.ACCOUNT_LOCKED: ErrorCodeMetadata(
        code=ErrorCode.ACCOUNT_LOCKED,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Account is locked",
            ar="الحساب مقفل"
        ),
        retryable=False,
    ),
    ErrorCode.ACCOUNT_DISABLED: ErrorCodeMetadata(
        code=ErrorCode.ACCOUNT_DISABLED,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Account is disabled",
            ar="الحساب معطل"
        ),
        retryable=False,
    ),
    ErrorCode.EMAIL_NOT_VERIFIED: ErrorCodeMetadata(
        code=ErrorCode.EMAIL_NOT_VERIFIED,
        category=ErrorCategory.AUTHENTICATION,
        http_status=HTTPStatus.UNAUTHORIZED,
        message=BilingualMessage(
            en="Email address not verified",
            ar="البريد الإلكتروني غير مُفعّل"
        ),
        retryable=False,
    ),

    # Authorization Errors
    ErrorCode.FORBIDDEN: ErrorCodeMetadata(
        code=ErrorCode.FORBIDDEN,
        category=ErrorCategory.AUTHORIZATION,
        http_status=HTTPStatus.FORBIDDEN,
        message=BilingualMessage(
            en="Access forbidden",
            ar="الوصول محظور"
        ),
        retryable=False,
    ),
    ErrorCode.INSUFFICIENT_PERMISSIONS: ErrorCodeMetadata(
        code=ErrorCode.INSUFFICIENT_PERMISSIONS,
        category=ErrorCategory.AUTHORIZATION,
        http_status=HTTPStatus.FORBIDDEN,
        message=BilingualMessage(
            en="Insufficient permissions to perform this action",
            ar="صلاحيات غير كافية لتنفيذ هذا الإجراء"
        ),
        retryable=False,
    ),
    ErrorCode.ACCESS_DENIED: ErrorCodeMetadata(
        code=ErrorCode.ACCESS_DENIED,
        category=ErrorCategory.AUTHORIZATION,
        http_status=HTTPStatus.FORBIDDEN,
        message=BilingualMessage(
            en="Access denied",
            ar="تم رفض الوصول"
        ),
        retryable=False,
    ),
    ErrorCode.TENANT_MISMATCH: ErrorCodeMetadata(
        code=ErrorCode.TENANT_MISMATCH,
        category=ErrorCategory.AUTHORIZATION,
        http_status=HTTPStatus.FORBIDDEN,
        message=BilingualMessage(
            en="Resource does not belong to your organization",
            ar="المورد لا ينتمي إلى مؤسستك"
        ),
        retryable=False,
    ),
    ErrorCode.ROLE_REQUIRED: ErrorCodeMetadata(
        code=ErrorCode.ROLE_REQUIRED,
        category=ErrorCategory.AUTHORIZATION,
        http_status=HTTPStatus.FORBIDDEN,
        message=BilingualMessage(
            en="Required role not assigned",
            ar="الدور المطلوب غير معين"
        ),
        retryable=False,
    ),
    ErrorCode.SUBSCRIPTION_REQUIRED: ErrorCodeMetadata(
        code=ErrorCode.SUBSCRIPTION_REQUIRED,
        category=ErrorCategory.AUTHORIZATION,
        http_status=HTTPStatus.FORBIDDEN,
        message=BilingualMessage(
            en="Active subscription required",
            ar="يتطلب اشتراك نشط"
        ),
        retryable=False,
    ),
    ErrorCode.QUOTA_EXCEEDED: ErrorCodeMetadata(
        code=ErrorCode.QUOTA_EXCEEDED,
        category=ErrorCategory.AUTHORIZATION,
        http_status=HTTPStatus.FORBIDDEN,
        message=BilingualMessage(
            en="Usage quota exceeded",
            ar="تم تجاوز حصة الاستخدام"
        ),
        retryable=False,
    ),

    # Not Found Errors
    ErrorCode.RESOURCE_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.RESOURCE_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Resource not found",
            ar="المورد غير موجود"
        ),
        retryable=False,
    ),
    ErrorCode.USER_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.USER_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="User not found",
            ar="المستخدم غير موجود"
        ),
        retryable=False,
    ),
    ErrorCode.FARM_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.FARM_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Farm not found",
            ar="المزرعة غير موجودة"
        ),
        retryable=False,
    ),
    ErrorCode.FIELD_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.FIELD_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Field not found",
            ar="الحقل غير موجود"
        ),
        retryable=False,
    ),
    ErrorCode.CROP_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.CROP_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Crop not found",
            ar="المحصول غير موجود"
        ),
        retryable=False,
    ),
    ErrorCode.SENSOR_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.SENSOR_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Sensor not found",
            ar="المستشعر غير موجود"
        ),
        retryable=False,
    ),
    ErrorCode.CONVERSATION_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.CONVERSATION_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Conversation not found",
            ar="المحادثة غير موجودة"
        ),
        retryable=False,
    ),
    ErrorCode.MESSAGE_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.MESSAGE_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Message not found",
            ar="الرسالة غير موجودة"
        ),
        retryable=False,
    ),
    ErrorCode.WALLET_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.WALLET_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Wallet not found",
            ar="المحفظة غير موجودة"
        ),
        retryable=False,
    ),
    ErrorCode.ORDER_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.ORDER_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Order not found",
            ar="الطلب غير موجود"
        ),
        retryable=False,
    ),
    ErrorCode.PRODUCT_NOT_FOUND: ErrorCodeMetadata(
        code=ErrorCode.PRODUCT_NOT_FOUND,
        category=ErrorCategory.NOT_FOUND,
        http_status=HTTPStatus.NOT_FOUND,
        message=BilingualMessage(
            en="Product not found",
            ar="المنتج غير موجود"
        ),
        retryable=False,
    ),

    # Conflict Errors
    ErrorCode.RESOURCE_ALREADY_EXISTS: ErrorCodeMetadata(
        code=ErrorCode.RESOURCE_ALREADY_EXISTS,
        category=ErrorCategory.CONFLICT,
        http_status=HTTPStatus.CONFLICT,
        message=BilingualMessage(
            en="Resource already exists",
            ar="المورد موجود بالفعل"
        ),
        retryable=False,
    ),
    ErrorCode.DUPLICATE_EMAIL: ErrorCodeMetadata(
        code=ErrorCode.DUPLICATE_EMAIL,
        category=ErrorCategory.CONFLICT,
        http_status=HTTPStatus.CONFLICT,
        message=BilingualMessage(
            en="Email address already registered",
            ar="البريد الإلكتروني مسجل بالفعل"
        ),
        retryable=False,
    ),
    ErrorCode.DUPLICATE_PHONE: ErrorCodeMetadata(
        code=ErrorCode.DUPLICATE_PHONE,
        category=ErrorCategory.CONFLICT,
        http_status=HTTPStatus.CONFLICT,
        message=BilingualMessage(
            en="Phone number already registered",
            ar="رقم الهاتف مسجل بالفعل"
        ),
        retryable=False,
    ),
    ErrorCode.CONCURRENT_MODIFICATION: ErrorCodeMetadata(
        code=ErrorCode.CONCURRENT_MODIFICATION,
        category=ErrorCategory.CONFLICT,
        http_status=HTTPStatus.CONFLICT,
        message=BilingualMessage(
            en="Resource was modified by another user",
            ar="تم تعديل المورد بواسطة مستخدم آخر"
        ),
        retryable=True,
    ),
    ErrorCode.VERSION_MISMATCH: ErrorCodeMetadata(
        code=ErrorCode.VERSION_MISMATCH,
        category=ErrorCategory.CONFLICT,
        http_status=HTTPStatus.CONFLICT,
        message=BilingualMessage(
            en="Version mismatch detected",
            ar="تم اكتشاف عدم تطابق في الإصدار"
        ),
        retryable=True,
    ),

    # Business Logic Errors
    ErrorCode.BUSINESS_RULE_VIOLATION: ErrorCodeMetadata(
        code=ErrorCode.BUSINESS_RULE_VIOLATION,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Business rule violation",
            ar="انتهاك قاعدة عمل"
        ),
        retryable=False,
    ),
    ErrorCode.INSUFFICIENT_BALANCE: ErrorCodeMetadata(
        code=ErrorCode.INSUFFICIENT_BALANCE,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Insufficient balance",
            ar="الرصيد غير كافي"
        ),
        retryable=False,
    ),
    ErrorCode.INVALID_STATE_TRANSITION: ErrorCodeMetadata(
        code=ErrorCode.INVALID_STATE_TRANSITION,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Invalid state transition",
            ar="انتقال حالة غير صالح"
        ),
        retryable=False,
    ),
    ErrorCode.OPERATION_NOT_ALLOWED: ErrorCodeMetadata(
        code=ErrorCode.OPERATION_NOT_ALLOWED,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Operation not allowed in current state",
            ar="العملية غير مسموحة في الحالة الحالية"
        ),
        retryable=False,
    ),
    ErrorCode.AMOUNT_MUST_BE_POSITIVE: ErrorCodeMetadata(
        code=ErrorCode.AMOUNT_MUST_BE_POSITIVE,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Amount must be greater than zero",
            ar="المبلغ يجب أن يكون أكبر من صفر"
        ),
        retryable=False,
    ),
    ErrorCode.PLANTING_DATE_INVALID: ErrorCodeMetadata(
        code=ErrorCode.PLANTING_DATE_INVALID,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Invalid planting date",
            ar="تاريخ الزراعة غير صالح"
        ),
        retryable=False,
    ),
    ErrorCode.HARVEST_DATE_BEFORE_PLANTING: ErrorCodeMetadata(
        code=ErrorCode.HARVEST_DATE_BEFORE_PLANTING,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Harvest date cannot be before planting date",
            ar="تاريخ الحصاد لا يمكن أن يكون قبل تاريخ الزراعة"
        ),
        retryable=False,
    ),
    ErrorCode.FIELD_ALREADY_HAS_CROP: ErrorCodeMetadata(
        code=ErrorCode.FIELD_ALREADY_HAS_CROP,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Field already has an active crop",
            ar="الحقل يحتوي بالفعل على محصول نشط"
        ),
        retryable=False,
    ),
    ErrorCode.ESCROW_ALREADY_EXISTS: ErrorCodeMetadata(
        code=ErrorCode.ESCROW_ALREADY_EXISTS,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Escrow already exists for this order",
            ar="يوجد إسكرو لهذا الطلب بالفعل"
        ),
        retryable=False,
    ),
    ErrorCode.LOAN_NOT_ACTIVE: ErrorCodeMetadata(
        code=ErrorCode.LOAN_NOT_ACTIVE,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Loan is not active",
            ar="القرض غير نشط"
        ),
        retryable=False,
    ),
    ErrorCode.PAYMENT_NOT_PENDING: ErrorCodeMetadata(
        code=ErrorCode.PAYMENT_NOT_PENDING,
        category=ErrorCategory.BUSINESS_LOGIC,
        http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
        message=BilingualMessage(
            en="Payment is not in pending state",
            ar="الدفعة ليست في حالة الانتظار"
        ),
        retryable=False,
    ),

    # External Service Errors
    ErrorCode.EXTERNAL_SERVICE_ERROR: ErrorCodeMetadata(
        code=ErrorCode.EXTERNAL_SERVICE_ERROR,
        category=ErrorCategory.EXTERNAL_SERVICE,
        http_status=HTTPStatus.BAD_GATEWAY,
        message=BilingualMessage(
            en="External service error",
            ar="خطأ في الخدمة الخارجية"
        ),
        retryable=True,
    ),
    ErrorCode.WEATHER_SERVICE_UNAVAILABLE: ErrorCodeMetadata(
        code=ErrorCode.WEATHER_SERVICE_UNAVAILABLE,
        category=ErrorCategory.EXTERNAL_SERVICE,
        http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        message=BilingualMessage(
            en="Weather service is currently unavailable",
            ar="خدمة الطقس غير متاحة حالياً"
        ),
        retryable=True,
    ),
    ErrorCode.SATELLITE_SERVICE_UNAVAILABLE: ErrorCodeMetadata(
        code=ErrorCode.SATELLITE_SERVICE_UNAVAILABLE,
        category=ErrorCategory.EXTERNAL_SERVICE,
        http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        message=BilingualMessage(
            en="Satellite service is currently unavailable",
            ar="خدمة الأقمار الصناعية غير متاحة حالياً"
        ),
        retryable=True,
    ),
    ErrorCode.PAYMENT_GATEWAY_ERROR: ErrorCodeMetadata(
        code=ErrorCode.PAYMENT_GATEWAY_ERROR,
        category=ErrorCategory.EXTERNAL_SERVICE,
        http_status=HTTPStatus.BAD_GATEWAY,
        message=BilingualMessage(
            en="Payment gateway error",
            ar="خطأ في بوابة الدفع"
        ),
        retryable=True,
    ),
    ErrorCode.SMS_SERVICE_ERROR: ErrorCodeMetadata(
        code=ErrorCode.SMS_SERVICE_ERROR,
        category=ErrorCategory.EXTERNAL_SERVICE,
        http_status=HTTPStatus.BAD_GATEWAY,
        message=BilingualMessage(
            en="SMS service error",
            ar="خطأ في خدمة الرسائل النصية"
        ),
        retryable=True,
    ),
    ErrorCode.EMAIL_SERVICE_ERROR: ErrorCodeMetadata(
        code=ErrorCode.EMAIL_SERVICE_ERROR,
        category=ErrorCategory.EXTERNAL_SERVICE,
        http_status=HTTPStatus.BAD_GATEWAY,
        message=BilingualMessage(
            en="Email service error",
            ar="خطأ في خدمة البريد الإلكتروني"
        ),
        retryable=True,
    ),
    ErrorCode.MAPS_SERVICE_ERROR: ErrorCodeMetadata(
        code=ErrorCode.MAPS_SERVICE_ERROR,
        category=ErrorCategory.EXTERNAL_SERVICE,
        http_status=HTTPStatus.BAD_GATEWAY,
        message=BilingualMessage(
            en="Maps service error",
            ar="خطأ في خدمة الخرائط"
        ),
        retryable=True,
    ),

    # Database Errors
    ErrorCode.DATABASE_ERROR: ErrorCodeMetadata(
        code=ErrorCode.DATABASE_ERROR,
        category=ErrorCategory.DATABASE,
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
        message=BilingualMessage(
            en="Database error occurred",
            ar="حدث خطأ في قاعدة البيانات"
        ),
        retryable=True,
    ),
    ErrorCode.DATABASE_CONNECTION_FAILED: ErrorCodeMetadata(
        code=ErrorCode.DATABASE_CONNECTION_FAILED,
        category=ErrorCategory.DATABASE,
        http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        message=BilingualMessage(
            en="Failed to connect to database",
            ar="فشل الاتصال بقاعدة البيانات"
        ),
        retryable=True,
    ),
    ErrorCode.QUERY_TIMEOUT: ErrorCodeMetadata(
        code=ErrorCode.QUERY_TIMEOUT,
        category=ErrorCategory.DATABASE,
        http_status=HTTPStatus.REQUEST_TIMEOUT,
        message=BilingualMessage(
            en="Database query timeout",
            ar="انتهت مهلة استعلام قاعدة البيانات"
        ),
        retryable=True,
    ),
    ErrorCode.TRANSACTION_FAILED: ErrorCodeMetadata(
        code=ErrorCode.TRANSACTION_FAILED,
        category=ErrorCategory.DATABASE,
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
        message=BilingualMessage(
            en="Database transaction failed",
            ar="فشلت معاملة قاعدة البيانات"
        ),
        retryable=True,
    ),
    ErrorCode.CONSTRAINT_VIOLATION: ErrorCodeMetadata(
        code=ErrorCode.CONSTRAINT_VIOLATION,
        category=ErrorCategory.DATABASE,
        http_status=HTTPStatus.CONFLICT,
        message=BilingualMessage(
            en="Database constraint violation",
            ar="انتهاك قيد قاعدة البيانات"
        ),
        retryable=False,
    ),
    ErrorCode.FOREIGN_KEY_VIOLATION: ErrorCodeMetadata(
        code=ErrorCode.FOREIGN_KEY_VIOLATION,
        category=ErrorCategory.DATABASE,
        http_status=HTTPStatus.CONFLICT,
        message=BilingualMessage(
            en="Foreign key constraint violation",
            ar="انتهاك قيد المفتاح الخارجي"
        ),
        retryable=False,
    ),
    ErrorCode.UNIQUE_CONSTRAINT_VIOLATION: ErrorCodeMetadata(
        code=ErrorCode.UNIQUE_CONSTRAINT_VIOLATION,
        category=ErrorCategory.DATABASE,
        http_status=HTTPStatus.CONFLICT,
        message=BilingualMessage(
            en="Unique constraint violation",
            ar="انتهاك قيد الفريدية"
        ),
        retryable=False,
    ),

    # Internal Errors
    ErrorCode.INTERNAL_SERVER_ERROR: ErrorCodeMetadata(
        code=ErrorCode.INTERNAL_SERVER_ERROR,
        category=ErrorCategory.INTERNAL,
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
        message=BilingualMessage(
            en="Internal server error",
            ar="خطأ داخلي في الخادم"
        ),
        retryable=True,
    ),
    ErrorCode.SERVICE_UNAVAILABLE: ErrorCodeMetadata(
        code=ErrorCode.SERVICE_UNAVAILABLE,
        category=ErrorCategory.INTERNAL,
        http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        message=BilingualMessage(
            en="Service temporarily unavailable",
            ar="الخدمة غير متاحة مؤقتاً"
        ),
        retryable=True,
    ),
    ErrorCode.CONFIGURATION_ERROR: ErrorCodeMetadata(
        code=ErrorCode.CONFIGURATION_ERROR,
        category=ErrorCategory.INTERNAL,
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
        message=BilingualMessage(
            en="Configuration error",
            ar="خطأ في التكوين"
        ),
        retryable=False,
    ),
    ErrorCode.NOT_IMPLEMENTED: ErrorCodeMetadata(
        code=ErrorCode.NOT_IMPLEMENTED,
        category=ErrorCategory.INTERNAL,
        http_status=HTTPStatus.NOT_IMPLEMENTED,
        message=BilingualMessage(
            en="Feature not implemented",
            ar="الميزة غير مطبقة"
        ),
        retryable=False,
    ),
    ErrorCode.DEPENDENCY_FAILED: ErrorCodeMetadata(
        code=ErrorCode.DEPENDENCY_FAILED,
        category=ErrorCategory.INTERNAL,
        http_status=HTTPStatus.FAILED_DEPENDENCY,
        message=BilingualMessage(
            en="Dependency service failed",
            ar="فشلت خدمة الاعتماد"
        ),
        retryable=True,
    ),

    # Rate Limiting
    ErrorCode.RATE_LIMIT_EXCEEDED: ErrorCodeMetadata(
        code=ErrorCode.RATE_LIMIT_EXCEEDED,
        category=ErrorCategory.RATE_LIMIT,
        http_status=HTTPStatus.TOO_MANY_REQUESTS,
        message=BilingualMessage(
            en="Rate limit exceeded",
            ar="تم تجاوز حد المعدل"
        ),
        retryable=True,
    ),
    ErrorCode.TOO_MANY_REQUESTS: ErrorCodeMetadata(
        code=ErrorCode.TOO_MANY_REQUESTS,
        category=ErrorCategory.RATE_LIMIT,
        http_status=HTTPStatus.TOO_MANY_REQUESTS,
        message=BilingualMessage(
            en="Too many requests",
            ar="طلبات كثيرة جداً"
        ),
        retryable=True,
    ),
    ErrorCode.API_QUOTA_EXCEEDED: ErrorCodeMetadata(
        code=ErrorCode.API_QUOTA_EXCEEDED,
        category=ErrorCategory.RATE_LIMIT,
        http_status=HTTPStatus.TOO_MANY_REQUESTS,
        message=BilingualMessage(
            en="API quota exceeded",
            ar="تم تجاوز حصة API"
        ),
        retryable=False,
    ),
}


def get_error_metadata(code: ErrorCode) -> ErrorCodeMetadata:
    """
    Get error metadata by code
    الحصول على بيانات الخطأ الوصفية حسب الكود
    """
    return ERROR_REGISTRY[code]


def get_error_codes_by_category(category: ErrorCategory) -> List[ErrorCode]:
    """
    Get all error codes by category
    الحصول على جميع أكواد الأخطاء حسب الفئة
    """
    return [
        code for code, metadata in ERROR_REGISTRY.items()
        if metadata.category == category
    ]
