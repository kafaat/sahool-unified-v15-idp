/**
 * Error Codes and HTTP Status Mapping
 * أكواد الأخطاء وربطها بحالات HTTP
 *
 * @module shared/errors
 * @description Centralized error code definitions with bilingual messages
 */

import { HttpStatus } from "@nestjs/common";

/**
 * Error Code Categories
 * فئات أكواد الأخطاء
 */
export enum ErrorCategory {
  VALIDATION = "VALIDATION", // أخطاء التحقق من صحة البيانات
  AUTHENTICATION = "AUTHENTICATION", // أخطاء المصادقة
  AUTHORIZATION = "AUTHORIZATION", // أخطاء التفويض
  NOT_FOUND = "NOT_FOUND", // الموارد غير الموجودة
  CONFLICT = "CONFLICT", // تعارض في البيانات
  BUSINESS_LOGIC = "BUSINESS_LOGIC", // أخطاء منطق الأعمال
  EXTERNAL_SERVICE = "EXTERNAL_SERVICE", // أخطاء الخدمات الخارجية
  DATABASE = "DATABASE", // أخطاء قاعدة البيانات
  INTERNAL = "INTERNAL", // أخطاء داخلية
  RATE_LIMIT = "RATE_LIMIT", // تجاوز الحد المسموح
}

/**
 * Application Error Codes
 * أكواد أخطاء التطبيق
 */
export enum ErrorCode {
  // Validation Errors (1000-1999) - أخطاء التحقق
  VALIDATION_ERROR = "ERR_1000",
  INVALID_INPUT = "ERR_1001",
  MISSING_REQUIRED_FIELD = "ERR_1002",
  INVALID_FORMAT = "ERR_1003",
  INVALID_EMAIL = "ERR_1004",
  INVALID_PHONE = "ERR_1005",
  INVALID_DATE = "ERR_1006",
  INVALID_RANGE = "ERR_1007",
  INVALID_ENUM_VALUE = "ERR_1008",

  // Authentication Errors (2000-2999) - أخطاء المصادقة
  AUTHENTICATION_FAILED = "ERR_2000",
  INVALID_CREDENTIALS = "ERR_2001",
  TOKEN_EXPIRED = "ERR_2002",
  TOKEN_INVALID = "ERR_2003",
  TOKEN_MISSING = "ERR_2004",
  SESSION_EXPIRED = "ERR_2005",
  ACCOUNT_LOCKED = "ERR_2006",
  ACCOUNT_DISABLED = "ERR_2007",
  EMAIL_NOT_VERIFIED = "ERR_2008",

  // Authorization Errors (3000-3999) - أخطاء التفويض
  FORBIDDEN = "ERR_3000",
  INSUFFICIENT_PERMISSIONS = "ERR_3001",
  ACCESS_DENIED = "ERR_3002",
  TENANT_MISMATCH = "ERR_3003",
  ROLE_REQUIRED = "ERR_3004",
  SUBSCRIPTION_REQUIRED = "ERR_3005",
  QUOTA_EXCEEDED = "ERR_3006",

  // Not Found Errors (4000-4999) - أخطاء العناصر غير الموجودة
  RESOURCE_NOT_FOUND = "ERR_4000",
  USER_NOT_FOUND = "ERR_4001",
  FARM_NOT_FOUND = "ERR_4002",
  FIELD_NOT_FOUND = "ERR_4003",
  CROP_NOT_FOUND = "ERR_4004",
  SENSOR_NOT_FOUND = "ERR_4005",
  CONVERSATION_NOT_FOUND = "ERR_4006",
  MESSAGE_NOT_FOUND = "ERR_4007",
  WALLET_NOT_FOUND = "ERR_4008",
  ORDER_NOT_FOUND = "ERR_4009",
  PRODUCT_NOT_FOUND = "ERR_4010",

  // Conflict Errors (5000-5999) - أخطاء التعارض
  RESOURCE_ALREADY_EXISTS = "ERR_5000",
  DUPLICATE_EMAIL = "ERR_5001",
  DUPLICATE_PHONE = "ERR_5002",
  CONCURRENT_MODIFICATION = "ERR_5003",
  VERSION_MISMATCH = "ERR_5004",

  // Business Logic Errors (6000-6999) - أخطاء منطق الأعمال
  BUSINESS_RULE_VIOLATION = "ERR_6000",
  INSUFFICIENT_BALANCE = "ERR_6001",
  INVALID_STATE_TRANSITION = "ERR_6002",
  OPERATION_NOT_ALLOWED = "ERR_6003",
  AMOUNT_MUST_BE_POSITIVE = "ERR_6004",
  PLANTING_DATE_INVALID = "ERR_6005",
  HARVEST_DATE_BEFORE_PLANTING = "ERR_6006",
  FIELD_ALREADY_HAS_CROP = "ERR_6007",
  ESCROW_ALREADY_EXISTS = "ERR_6008",
  LOAN_NOT_ACTIVE = "ERR_6009",
  PAYMENT_NOT_PENDING = "ERR_6010",

  // External Service Errors (7000-7999) - أخطاء الخدمات الخارجية
  EXTERNAL_SERVICE_ERROR = "ERR_7000",
  WEATHER_SERVICE_UNAVAILABLE = "ERR_7001",
  SATELLITE_SERVICE_UNAVAILABLE = "ERR_7002",
  PAYMENT_GATEWAY_ERROR = "ERR_7003",
  SMS_SERVICE_ERROR = "ERR_7004",
  EMAIL_SERVICE_ERROR = "ERR_7005",
  MAPS_SERVICE_ERROR = "ERR_7006",

  // Database Errors (8000-8999) - أخطاء قاعدة البيانات
  DATABASE_ERROR = "ERR_8000",
  DATABASE_CONNECTION_FAILED = "ERR_8001",
  QUERY_TIMEOUT = "ERR_8002",
  TRANSACTION_FAILED = "ERR_8003",
  CONSTRAINT_VIOLATION = "ERR_8004",
  FOREIGN_KEY_VIOLATION = "ERR_8005",
  UNIQUE_CONSTRAINT_VIOLATION = "ERR_8006",

  // Internal Errors (9000-9999) - الأخطاء الداخلية
  INTERNAL_SERVER_ERROR = "ERR_9000",
  SERVICE_UNAVAILABLE = "ERR_9001",
  CONFIGURATION_ERROR = "ERR_9002",
  NOT_IMPLEMENTED = "ERR_9003",
  DEPENDENCY_FAILED = "ERR_9004",

  // Rate Limiting (10000-10999) - تجاوز الحد المسموح
  RATE_LIMIT_EXCEEDED = "ERR_10000",
  TOO_MANY_REQUESTS = "ERR_10001",
  API_QUOTA_EXCEEDED = "ERR_10002",
}

/**
 * Bilingual Error Message
 * رسالة خطأ ثنائية اللغة
 */
export interface BilingualMessage {
  en: string; // English message
  ar: string; // Arabic message - الرسالة العربية
}

/**
 * Error Code Metadata
 * بيانات كود الخطأ الوصفية
 */
export interface ErrorCodeMetadata {
  code: ErrorCode;
  category: ErrorCategory;
  httpStatus: HttpStatus;
  message: BilingualMessage;
  retryable: boolean;
}

/**
 * Error Code Registry
 * سجل أكواد الأخطاء
 */
export const ERROR_REGISTRY: Record<ErrorCode, ErrorCodeMetadata> = {
  // Validation Errors
  [ErrorCode.VALIDATION_ERROR]: {
    code: ErrorCode.VALIDATION_ERROR,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Validation error occurred",
      ar: "حدث خطأ في التحقق من صحة البيانات",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_INPUT]: {
    code: ErrorCode.INVALID_INPUT,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Invalid input provided",
      ar: "تم تقديم بيانات غير صالحة",
    },
    retryable: false,
  },
  [ErrorCode.MISSING_REQUIRED_FIELD]: {
    code: ErrorCode.MISSING_REQUIRED_FIELD,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Required field is missing",
      ar: "حقل مطلوب غير موجود",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_FORMAT]: {
    code: ErrorCode.INVALID_FORMAT,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Invalid format",
      ar: "تنسيق غير صالح",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_EMAIL]: {
    code: ErrorCode.INVALID_EMAIL,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Invalid email format",
      ar: "تنسيق البريد الإلكتروني غير صالح",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_PHONE]: {
    code: ErrorCode.INVALID_PHONE,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Invalid phone number format",
      ar: "تنسيق رقم الهاتف غير صالح",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_DATE]: {
    code: ErrorCode.INVALID_DATE,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Invalid date format",
      ar: "تنسيق التاريخ غير صالح",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_RANGE]: {
    code: ErrorCode.INVALID_RANGE,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Value is outside the valid range",
      ar: "القيمة خارج النطاق الصحيح",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_ENUM_VALUE]: {
    code: ErrorCode.INVALID_ENUM_VALUE,
    category: ErrorCategory.VALIDATION,
    httpStatus: HttpStatus.BAD_REQUEST,
    message: {
      en: "Invalid enum value",
      ar: "قيمة التعداد غير صالحة",
    },
    retryable: false,
  },

  // Authentication Errors
  [ErrorCode.AUTHENTICATION_FAILED]: {
    code: ErrorCode.AUTHENTICATION_FAILED,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Authentication failed",
      ar: "فشلت المصادقة",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_CREDENTIALS]: {
    code: ErrorCode.INVALID_CREDENTIALS,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Invalid credentials provided",
      ar: "بيانات اعتماد غير صالحة",
    },
    retryable: false,
  },
  [ErrorCode.TOKEN_EXPIRED]: {
    code: ErrorCode.TOKEN_EXPIRED,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Authentication token has expired",
      ar: "انتهت صلاحية رمز المصادقة",
    },
    retryable: false,
  },
  [ErrorCode.TOKEN_INVALID]: {
    code: ErrorCode.TOKEN_INVALID,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Invalid authentication token",
      ar: "رمز مصادقة غير صالح",
    },
    retryable: false,
  },
  [ErrorCode.TOKEN_MISSING]: {
    code: ErrorCode.TOKEN_MISSING,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Authentication token is missing",
      ar: "رمز المصادقة مفقود",
    },
    retryable: false,
  },
  [ErrorCode.SESSION_EXPIRED]: {
    code: ErrorCode.SESSION_EXPIRED,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Session has expired",
      ar: "انتهت صلاحية الجلسة",
    },
    retryable: false,
  },
  [ErrorCode.ACCOUNT_LOCKED]: {
    code: ErrorCode.ACCOUNT_LOCKED,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Account is locked",
      ar: "الحساب مقفل",
    },
    retryable: false,
  },
  [ErrorCode.ACCOUNT_DISABLED]: {
    code: ErrorCode.ACCOUNT_DISABLED,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Account is disabled",
      ar: "الحساب معطل",
    },
    retryable: false,
  },
  [ErrorCode.EMAIL_NOT_VERIFIED]: {
    code: ErrorCode.EMAIL_NOT_VERIFIED,
    category: ErrorCategory.AUTHENTICATION,
    httpStatus: HttpStatus.UNAUTHORIZED,
    message: {
      en: "Email address not verified",
      ar: "البريد الإلكتروني غير مُفعّل",
    },
    retryable: false,
  },

  // Authorization Errors
  [ErrorCode.FORBIDDEN]: {
    code: ErrorCode.FORBIDDEN,
    category: ErrorCategory.AUTHORIZATION,
    httpStatus: HttpStatus.FORBIDDEN,
    message: {
      en: "Access forbidden",
      ar: "الوصول محظور",
    },
    retryable: false,
  },
  [ErrorCode.INSUFFICIENT_PERMISSIONS]: {
    code: ErrorCode.INSUFFICIENT_PERMISSIONS,
    category: ErrorCategory.AUTHORIZATION,
    httpStatus: HttpStatus.FORBIDDEN,
    message: {
      en: "Insufficient permissions to perform this action",
      ar: "صلاحيات غير كافية لتنفيذ هذا الإجراء",
    },
    retryable: false,
  },
  [ErrorCode.ACCESS_DENIED]: {
    code: ErrorCode.ACCESS_DENIED,
    category: ErrorCategory.AUTHORIZATION,
    httpStatus: HttpStatus.FORBIDDEN,
    message: {
      en: "Access denied",
      ar: "تم رفض الوصول",
    },
    retryable: false,
  },
  [ErrorCode.TENANT_MISMATCH]: {
    code: ErrorCode.TENANT_MISMATCH,
    category: ErrorCategory.AUTHORIZATION,
    httpStatus: HttpStatus.FORBIDDEN,
    message: {
      en: "Resource does not belong to your organization",
      ar: "المورد لا ينتمي إلى مؤسستك",
    },
    retryable: false,
  },
  [ErrorCode.ROLE_REQUIRED]: {
    code: ErrorCode.ROLE_REQUIRED,
    category: ErrorCategory.AUTHORIZATION,
    httpStatus: HttpStatus.FORBIDDEN,
    message: {
      en: "Required role not assigned",
      ar: "الدور المطلوب غير معين",
    },
    retryable: false,
  },
  [ErrorCode.SUBSCRIPTION_REQUIRED]: {
    code: ErrorCode.SUBSCRIPTION_REQUIRED,
    category: ErrorCategory.AUTHORIZATION,
    httpStatus: HttpStatus.FORBIDDEN,
    message: {
      en: "Active subscription required",
      ar: "يتطلب اشتراك نشط",
    },
    retryable: false,
  },
  [ErrorCode.QUOTA_EXCEEDED]: {
    code: ErrorCode.QUOTA_EXCEEDED,
    category: ErrorCategory.AUTHORIZATION,
    httpStatus: HttpStatus.FORBIDDEN,
    message: {
      en: "Usage quota exceeded",
      ar: "تم تجاوز حصة الاستخدام",
    },
    retryable: false,
  },

  // Not Found Errors
  [ErrorCode.RESOURCE_NOT_FOUND]: {
    code: ErrorCode.RESOURCE_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Resource not found",
      ar: "المورد غير موجود",
    },
    retryable: false,
  },
  [ErrorCode.USER_NOT_FOUND]: {
    code: ErrorCode.USER_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "User not found",
      ar: "المستخدم غير موجود",
    },
    retryable: false,
  },
  [ErrorCode.FARM_NOT_FOUND]: {
    code: ErrorCode.FARM_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Farm not found",
      ar: "المزرعة غير موجودة",
    },
    retryable: false,
  },
  [ErrorCode.FIELD_NOT_FOUND]: {
    code: ErrorCode.FIELD_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Field not found",
      ar: "الحقل غير موجود",
    },
    retryable: false,
  },
  [ErrorCode.CROP_NOT_FOUND]: {
    code: ErrorCode.CROP_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Crop not found",
      ar: "المحصول غير موجود",
    },
    retryable: false,
  },
  [ErrorCode.SENSOR_NOT_FOUND]: {
    code: ErrorCode.SENSOR_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Sensor not found",
      ar: "المستشعر غير موجود",
    },
    retryable: false,
  },
  [ErrorCode.CONVERSATION_NOT_FOUND]: {
    code: ErrorCode.CONVERSATION_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Conversation not found",
      ar: "المحادثة غير موجودة",
    },
    retryable: false,
  },
  [ErrorCode.MESSAGE_NOT_FOUND]: {
    code: ErrorCode.MESSAGE_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Message not found",
      ar: "الرسالة غير موجودة",
    },
    retryable: false,
  },
  [ErrorCode.WALLET_NOT_FOUND]: {
    code: ErrorCode.WALLET_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Wallet not found",
      ar: "المحفظة غير موجودة",
    },
    retryable: false,
  },
  [ErrorCode.ORDER_NOT_FOUND]: {
    code: ErrorCode.ORDER_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Order not found",
      ar: "الطلب غير موجود",
    },
    retryable: false,
  },
  [ErrorCode.PRODUCT_NOT_FOUND]: {
    code: ErrorCode.PRODUCT_NOT_FOUND,
    category: ErrorCategory.NOT_FOUND,
    httpStatus: HttpStatus.NOT_FOUND,
    message: {
      en: "Product not found",
      ar: "المنتج غير موجود",
    },
    retryable: false,
  },

  // Conflict Errors
  [ErrorCode.RESOURCE_ALREADY_EXISTS]: {
    code: ErrorCode.RESOURCE_ALREADY_EXISTS,
    category: ErrorCategory.CONFLICT,
    httpStatus: HttpStatus.CONFLICT,
    message: {
      en: "Resource already exists",
      ar: "المورد موجود بالفعل",
    },
    retryable: false,
  },
  [ErrorCode.DUPLICATE_EMAIL]: {
    code: ErrorCode.DUPLICATE_EMAIL,
    category: ErrorCategory.CONFLICT,
    httpStatus: HttpStatus.CONFLICT,
    message: {
      en: "Email address already registered",
      ar: "البريد الإلكتروني مسجل بالفعل",
    },
    retryable: false,
  },
  [ErrorCode.DUPLICATE_PHONE]: {
    code: ErrorCode.DUPLICATE_PHONE,
    category: ErrorCategory.CONFLICT,
    httpStatus: HttpStatus.CONFLICT,
    message: {
      en: "Phone number already registered",
      ar: "رقم الهاتف مسجل بالفعل",
    },
    retryable: false,
  },
  [ErrorCode.CONCURRENT_MODIFICATION]: {
    code: ErrorCode.CONCURRENT_MODIFICATION,
    category: ErrorCategory.CONFLICT,
    httpStatus: HttpStatus.CONFLICT,
    message: {
      en: "Resource was modified by another user",
      ar: "تم تعديل المورد بواسطة مستخدم آخر",
    },
    retryable: true,
  },
  [ErrorCode.VERSION_MISMATCH]: {
    code: ErrorCode.VERSION_MISMATCH,
    category: ErrorCategory.CONFLICT,
    httpStatus: HttpStatus.CONFLICT,
    message: {
      en: "Version mismatch detected",
      ar: "تم اكتشاف عدم تطابق في الإصدار",
    },
    retryable: true,
  },

  // Business Logic Errors
  [ErrorCode.BUSINESS_RULE_VIOLATION]: {
    code: ErrorCode.BUSINESS_RULE_VIOLATION,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Business rule violation",
      ar: "انتهاك قاعدة عمل",
    },
    retryable: false,
  },
  [ErrorCode.INSUFFICIENT_BALANCE]: {
    code: ErrorCode.INSUFFICIENT_BALANCE,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Insufficient balance",
      ar: "الرصيد غير كافي",
    },
    retryable: false,
  },
  [ErrorCode.INVALID_STATE_TRANSITION]: {
    code: ErrorCode.INVALID_STATE_TRANSITION,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Invalid state transition",
      ar: "انتقال حالة غير صالح",
    },
    retryable: false,
  },
  [ErrorCode.OPERATION_NOT_ALLOWED]: {
    code: ErrorCode.OPERATION_NOT_ALLOWED,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Operation not allowed in current state",
      ar: "العملية غير مسموحة في الحالة الحالية",
    },
    retryable: false,
  },
  [ErrorCode.AMOUNT_MUST_BE_POSITIVE]: {
    code: ErrorCode.AMOUNT_MUST_BE_POSITIVE,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Amount must be greater than zero",
      ar: "المبلغ يجب أن يكون أكبر من صفر",
    },
    retryable: false,
  },
  [ErrorCode.PLANTING_DATE_INVALID]: {
    code: ErrorCode.PLANTING_DATE_INVALID,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Invalid planting date",
      ar: "تاريخ الزراعة غير صالح",
    },
    retryable: false,
  },
  [ErrorCode.HARVEST_DATE_BEFORE_PLANTING]: {
    code: ErrorCode.HARVEST_DATE_BEFORE_PLANTING,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Harvest date cannot be before planting date",
      ar: "تاريخ الحصاد لا يمكن أن يكون قبل تاريخ الزراعة",
    },
    retryable: false,
  },
  [ErrorCode.FIELD_ALREADY_HAS_CROP]: {
    code: ErrorCode.FIELD_ALREADY_HAS_CROP,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Field already has an active crop",
      ar: "الحقل يحتوي بالفعل على محصول نشط",
    },
    retryable: false,
  },
  [ErrorCode.ESCROW_ALREADY_EXISTS]: {
    code: ErrorCode.ESCROW_ALREADY_EXISTS,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Escrow already exists for this order",
      ar: "يوجد إسكرو لهذا الطلب بالفعل",
    },
    retryable: false,
  },
  [ErrorCode.LOAN_NOT_ACTIVE]: {
    code: ErrorCode.LOAN_NOT_ACTIVE,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Loan is not active",
      ar: "القرض غير نشط",
    },
    retryable: false,
  },
  [ErrorCode.PAYMENT_NOT_PENDING]: {
    code: ErrorCode.PAYMENT_NOT_PENDING,
    category: ErrorCategory.BUSINESS_LOGIC,
    httpStatus: HttpStatus.UNPROCESSABLE_ENTITY,
    message: {
      en: "Payment is not in pending state",
      ar: "الدفعة ليست في حالة الانتظار",
    },
    retryable: false,
  },

  // External Service Errors
  [ErrorCode.EXTERNAL_SERVICE_ERROR]: {
    code: ErrorCode.EXTERNAL_SERVICE_ERROR,
    category: ErrorCategory.EXTERNAL_SERVICE,
    httpStatus: HttpStatus.BAD_GATEWAY,
    message: {
      en: "External service error",
      ar: "خطأ في الخدمة الخارجية",
    },
    retryable: true,
  },
  [ErrorCode.WEATHER_SERVICE_UNAVAILABLE]: {
    code: ErrorCode.WEATHER_SERVICE_UNAVAILABLE,
    category: ErrorCategory.EXTERNAL_SERVICE,
    httpStatus: HttpStatus.SERVICE_UNAVAILABLE,
    message: {
      en: "Weather service is currently unavailable",
      ar: "خدمة الطقس غير متاحة حالياً",
    },
    retryable: true,
  },
  [ErrorCode.SATELLITE_SERVICE_UNAVAILABLE]: {
    code: ErrorCode.SATELLITE_SERVICE_UNAVAILABLE,
    category: ErrorCategory.EXTERNAL_SERVICE,
    httpStatus: HttpStatus.SERVICE_UNAVAILABLE,
    message: {
      en: "Satellite service is currently unavailable",
      ar: "خدمة الأقمار الصناعية غير متاحة حالياً",
    },
    retryable: true,
  },
  [ErrorCode.PAYMENT_GATEWAY_ERROR]: {
    code: ErrorCode.PAYMENT_GATEWAY_ERROR,
    category: ErrorCategory.EXTERNAL_SERVICE,
    httpStatus: HttpStatus.BAD_GATEWAY,
    message: {
      en: "Payment gateway error",
      ar: "خطأ في بوابة الدفع",
    },
    retryable: true,
  },
  [ErrorCode.SMS_SERVICE_ERROR]: {
    code: ErrorCode.SMS_SERVICE_ERROR,
    category: ErrorCategory.EXTERNAL_SERVICE,
    httpStatus: HttpStatus.BAD_GATEWAY,
    message: {
      en: "SMS service error",
      ar: "خطأ في خدمة الرسائل النصية",
    },
    retryable: true,
  },
  [ErrorCode.EMAIL_SERVICE_ERROR]: {
    code: ErrorCode.EMAIL_SERVICE_ERROR,
    category: ErrorCategory.EXTERNAL_SERVICE,
    httpStatus: HttpStatus.BAD_GATEWAY,
    message: {
      en: "Email service error",
      ar: "خطأ في خدمة البريد الإلكتروني",
    },
    retryable: true,
  },
  [ErrorCode.MAPS_SERVICE_ERROR]: {
    code: ErrorCode.MAPS_SERVICE_ERROR,
    category: ErrorCategory.EXTERNAL_SERVICE,
    httpStatus: HttpStatus.BAD_GATEWAY,
    message: {
      en: "Maps service error",
      ar: "خطأ في خدمة الخرائط",
    },
    retryable: true,
  },

  // Database Errors
  [ErrorCode.DATABASE_ERROR]: {
    code: ErrorCode.DATABASE_ERROR,
    category: ErrorCategory.DATABASE,
    httpStatus: HttpStatus.INTERNAL_SERVER_ERROR,
    message: {
      en: "Database error occurred",
      ar: "حدث خطأ في قاعدة البيانات",
    },
    retryable: true,
  },
  [ErrorCode.DATABASE_CONNECTION_FAILED]: {
    code: ErrorCode.DATABASE_CONNECTION_FAILED,
    category: ErrorCategory.DATABASE,
    httpStatus: HttpStatus.SERVICE_UNAVAILABLE,
    message: {
      en: "Failed to connect to database",
      ar: "فشل الاتصال بقاعدة البيانات",
    },
    retryable: true,
  },
  [ErrorCode.QUERY_TIMEOUT]: {
    code: ErrorCode.QUERY_TIMEOUT,
    category: ErrorCategory.DATABASE,
    httpStatus: HttpStatus.REQUEST_TIMEOUT,
    message: {
      en: "Database query timeout",
      ar: "انتهت مهلة استعلام قاعدة البيانات",
    },
    retryable: true,
  },
  [ErrorCode.TRANSACTION_FAILED]: {
    code: ErrorCode.TRANSACTION_FAILED,
    category: ErrorCategory.DATABASE,
    httpStatus: HttpStatus.INTERNAL_SERVER_ERROR,
    message: {
      en: "Database transaction failed",
      ar: "فشلت معاملة قاعدة البيانات",
    },
    retryable: true,
  },
  [ErrorCode.CONSTRAINT_VIOLATION]: {
    code: ErrorCode.CONSTRAINT_VIOLATION,
    category: ErrorCategory.DATABASE,
    httpStatus: HttpStatus.CONFLICT,
    message: {
      en: "Database constraint violation",
      ar: "انتهاك قيد قاعدة البيانات",
    },
    retryable: false,
  },
  [ErrorCode.FOREIGN_KEY_VIOLATION]: {
    code: ErrorCode.FOREIGN_KEY_VIOLATION,
    category: ErrorCategory.DATABASE,
    httpStatus: HttpStatus.CONFLICT,
    message: {
      en: "Foreign key constraint violation",
      ar: "انتهاك قيد المفتاح الخارجي",
    },
    retryable: false,
  },
  [ErrorCode.UNIQUE_CONSTRAINT_VIOLATION]: {
    code: ErrorCode.UNIQUE_CONSTRAINT_VIOLATION,
    category: ErrorCategory.DATABASE,
    httpStatus: HttpStatus.CONFLICT,
    message: {
      en: "Unique constraint violation",
      ar: "انتهاك قيد الفريدية",
    },
    retryable: false,
  },

  // Internal Errors
  [ErrorCode.INTERNAL_SERVER_ERROR]: {
    code: ErrorCode.INTERNAL_SERVER_ERROR,
    category: ErrorCategory.INTERNAL,
    httpStatus: HttpStatus.INTERNAL_SERVER_ERROR,
    message: {
      en: "Internal server error",
      ar: "خطأ داخلي في الخادم",
    },
    retryable: true,
  },
  [ErrorCode.SERVICE_UNAVAILABLE]: {
    code: ErrorCode.SERVICE_UNAVAILABLE,
    category: ErrorCategory.INTERNAL,
    httpStatus: HttpStatus.SERVICE_UNAVAILABLE,
    message: {
      en: "Service temporarily unavailable",
      ar: "الخدمة غير متاحة مؤقتاً",
    },
    retryable: true,
  },
  [ErrorCode.CONFIGURATION_ERROR]: {
    code: ErrorCode.CONFIGURATION_ERROR,
    category: ErrorCategory.INTERNAL,
    httpStatus: HttpStatus.INTERNAL_SERVER_ERROR,
    message: {
      en: "Configuration error",
      ar: "خطأ في التكوين",
    },
    retryable: false,
  },
  [ErrorCode.NOT_IMPLEMENTED]: {
    code: ErrorCode.NOT_IMPLEMENTED,
    category: ErrorCategory.INTERNAL,
    httpStatus: HttpStatus.NOT_IMPLEMENTED,
    message: {
      en: "Feature not implemented",
      ar: "الميزة غير مطبقة",
    },
    retryable: false,
  },
  [ErrorCode.DEPENDENCY_FAILED]: {
    code: ErrorCode.DEPENDENCY_FAILED,
    category: ErrorCategory.INTERNAL,
    httpStatus: HttpStatus.FAILED_DEPENDENCY,
    message: {
      en: "Dependency service failed",
      ar: "فشلت خدمة الاعتماد",
    },
    retryable: true,
  },

  // Rate Limiting
  [ErrorCode.RATE_LIMIT_EXCEEDED]: {
    code: ErrorCode.RATE_LIMIT_EXCEEDED,
    category: ErrorCategory.RATE_LIMIT,
    httpStatus: HttpStatus.TOO_MANY_REQUESTS,
    message: {
      en: "Rate limit exceeded",
      ar: "تم تجاوز حد المعدل",
    },
    retryable: true,
  },
  [ErrorCode.TOO_MANY_REQUESTS]: {
    code: ErrorCode.TOO_MANY_REQUESTS,
    category: ErrorCategory.RATE_LIMIT,
    httpStatus: HttpStatus.TOO_MANY_REQUESTS,
    message: {
      en: "Too many requests",
      ar: "طلبات كثيرة جداً",
    },
    retryable: true,
  },
  [ErrorCode.API_QUOTA_EXCEEDED]: {
    code: ErrorCode.API_QUOTA_EXCEEDED,
    category: ErrorCategory.RATE_LIMIT,
    httpStatus: HttpStatus.TOO_MANY_REQUESTS,
    message: {
      en: "API quota exceeded",
      ar: "تم تجاوز حصة API",
    },
    retryable: false,
  },
};

/**
 * Get error metadata by code
 * الحصول على بيانات الخطأ الوصفية حسب الكود
 */
export function getErrorMetadata(code: ErrorCode): ErrorCodeMetadata {
  return ERROR_REGISTRY[code];
}

/**
 * Get all error codes by category
 * الحصول على جميع أكواد الأخطاء حسب الفئة
 */
export function getErrorCodesByCategory(category: ErrorCategory): ErrorCode[] {
  return Object.values(ErrorCode).filter(
    (code) => ERROR_REGISTRY[code]?.category === category,
  );
}
