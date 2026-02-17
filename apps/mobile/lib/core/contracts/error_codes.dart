/// SAHOOL Unified Error Codes (Dart)
/// أكواد الأخطاء الموحدة
///
/// Auto-generated from: packages/shared-types/src/contracts/error-codes.ts
/// Used by: Mobile app (Flutter/Dart)
///
/// @version 16.0.0
library;

/// Unified error codes used across all SAHOOL clients and services.
abstract final class ErrorCodes {
  // ── Network & Transport ──────────────────────────────────────────────
  static const String networkError = 'NETWORK_ERROR';
  static const String timeout = 'TIMEOUT';
  static const String circuitOpen = 'CIRCUIT_OPEN';
  static const String invalidResponse = 'INVALID_RESPONSE';

  // ── Authentication (401) ─────────────────────────────────────────────
  static const String unauthorized = 'UNAUTHORIZED';
  static const String tokenExpired = 'TOKEN_EXPIRED';
  static const String tokenInvalid = 'TOKEN_INVALID';
  static const String sessionExpired = 'SESSION_EXPIRED';

  // ── Authorization (403) ──────────────────────────────────────────────
  static const String forbidden = 'FORBIDDEN';
  static const String insufficientPermissions = 'INSUFFICIENT_PERMISSIONS';

  // ── Client Errors (4xx) ──────────────────────────────────────────────
  static const String badRequest = 'BAD_REQUEST';
  static const String validationError = 'VALIDATION_ERROR';
  static const String notFound = 'NOT_FOUND';
  static const String conflict = 'CONFLICT';
  static const String rateLimited = 'RATE_LIMITED';

  // ── Server Errors (5xx) ──────────────────────────────────────────────
  static const String serverError = 'SERVER_ERROR';
  static const String serviceUnavailable = 'SERVICE_UNAVAILABLE';
  static const String gatewayTimeout = 'GATEWAY_TIMEOUT';

  // ── Mobile-Specific ──────────────────────────────────────────────────
  static const String offline = 'OFFLINE';
  static const String syncFailed = 'SYNC_FAILED';
  static const String syncConflict = 'SYNC_CONFLICT';
  static const String certificateError = 'CERTIFICATE_ERROR';

  // ── Generic ──────────────────────────────────────────────────────────
  static const String unknown = 'UNKNOWN';
}

/// Bilingual error message definition.
class ErrorMessage {
  final String code;
  final int httpStatus;
  final String en;
  final String ar;
  final bool retryable;

  const ErrorMessage({
    required this.code,
    required this.httpStatus,
    required this.en,
    required this.ar,
    required this.retryable,
  });

  /// Get localized error text.
  String localized(String locale) => locale == 'ar' ? ar : en;
}

/// All error messages keyed by error code.
const Map<String, ErrorMessage> errorMessages = {
  // ── Network & Transport ──────────────────────────────────────────────
  'NETWORK_ERROR': ErrorMessage(
    code: 'NETWORK_ERROR',
    httpStatus: 0,
    en: 'Network error - please check your connection',
    ar: 'خطأ في الشبكة - يرجى التحقق من اتصالك',
    retryable: true,
  ),
  'TIMEOUT': ErrorMessage(
    code: 'TIMEOUT',
    httpStatus: 504,
    en: 'Request timed out - please try again',
    ar: 'انتهت مهلة الطلب - يرجى المحاولة مرة أخرى',
    retryable: true,
  ),
  'CIRCUIT_OPEN': ErrorMessage(
    code: 'CIRCUIT_OPEN',
    httpStatus: 503,
    en: 'Service temporarily unavailable',
    ar: 'الخدمة غير متاحة مؤقتاً',
    retryable: true,
  ),
  'INVALID_RESPONSE': ErrorMessage(
    code: 'INVALID_RESPONSE',
    httpStatus: 502,
    en: 'Invalid response from server',
    ar: 'استجابة غير صالحة من الخادم',
    retryable: false,
  ),

  // ── Authentication (401) ─────────────────────────────────────────────
  'UNAUTHORIZED': ErrorMessage(
    code: 'UNAUTHORIZED',
    httpStatus: 401,
    en: 'Authentication required',
    ar: 'المصادقة مطلوبة',
    retryable: false,
  ),
  'TOKEN_EXPIRED': ErrorMessage(
    code: 'TOKEN_EXPIRED',
    httpStatus: 401,
    en: 'Session expired. Please login again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  ),
  'TOKEN_INVALID': ErrorMessage(
    code: 'TOKEN_INVALID',
    httpStatus: 401,
    en: 'Invalid authentication token',
    ar: 'رمز مصادقة غير صالح',
    retryable: false,
  ),
  'SESSION_EXPIRED': ErrorMessage(
    code: 'SESSION_EXPIRED',
    httpStatus: 401,
    en: 'Session expired. Please login again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
    retryable: false,
  ),

  // ── Authorization (403) ──────────────────────────────────────────────
  'FORBIDDEN': ErrorMessage(
    code: 'FORBIDDEN',
    httpStatus: 403,
    en: 'Access denied - insufficient permissions',
    ar: 'الوصول مرفوض - صلاحيات غير كافية',
    retryable: false,
  ),
  'INSUFFICIENT_PERMISSIONS': ErrorMessage(
    code: 'INSUFFICIENT_PERMISSIONS',
    httpStatus: 403,
    en: 'You do not have permission to perform this action',
    ar: 'ليس لديك صلاحية لتنفيذ هذا الإجراء',
    retryable: false,
  ),

  // ── Client Errors (4xx) ──────────────────────────────────────────────
  'BAD_REQUEST': ErrorMessage(
    code: 'BAD_REQUEST',
    httpStatus: 400,
    en: 'Invalid request',
    ar: 'طلب غير صالح',
    retryable: false,
  ),
  'VALIDATION_ERROR': ErrorMessage(
    code: 'VALIDATION_ERROR',
    httpStatus: 400,
    en: 'Validation error - please check your input',
    ar: 'خطأ في التحقق - يرجى مراجعة المدخلات',
    retryable: false,
  ),
  'NOT_FOUND': ErrorMessage(
    code: 'NOT_FOUND',
    httpStatus: 404,
    en: 'Resource not found',
    ar: 'المورد غير موجود',
    retryable: false,
  ),
  'CONFLICT': ErrorMessage(
    code: 'CONFLICT',
    httpStatus: 409,
    en: 'Conflict - resource was modified by another request',
    ar: 'تعارض - تم تعديل المورد بواسطة طلب آخر',
    retryable: false,
  ),
  'RATE_LIMITED': ErrorMessage(
    code: 'RATE_LIMITED',
    httpStatus: 429,
    en: 'Too many requests. Please wait.',
    ar: 'طلبات كثيرة جداً. يرجى الانتظار.',
    retryable: true,
  ),

  // ── Server Errors (5xx) ──────────────────────────────────────────────
  'SERVER_ERROR': ErrorMessage(
    code: 'SERVER_ERROR',
    httpStatus: 500,
    en: 'Server error - please try again later',
    ar: 'خطأ في الخادم - يرجى المحاولة لاحقاً',
    retryable: true,
  ),
  'SERVICE_UNAVAILABLE': ErrorMessage(
    code: 'SERVICE_UNAVAILABLE',
    httpStatus: 503,
    en: 'Service temporarily unavailable',
    ar: 'الخدمة غير متاحة مؤقتاً',
    retryable: true,
  ),
  'GATEWAY_TIMEOUT': ErrorMessage(
    code: 'GATEWAY_TIMEOUT',
    httpStatus: 504,
    en: 'Gateway timeout - please try again',
    ar: 'انتهت مهلة البوابة - يرجى المحاولة مرة أخرى',
    retryable: true,
  ),

  // ── Mobile-Specific ──────────────────────────────────────────────────
  'OFFLINE': ErrorMessage(
    code: 'OFFLINE',
    httpStatus: 0,
    en: 'You are offline. Changes will sync when connected.',
    ar: 'أنت غير متصل. سيتم مزامنة التغييرات عند الاتصال.',
    retryable: true,
  ),
  'SYNC_FAILED': ErrorMessage(
    code: 'SYNC_FAILED',
    httpStatus: 0,
    en: 'Sync failed. Please try again.',
    ar: 'فشلت المزامنة. يرجى المحاولة مرة أخرى.',
    retryable: true,
  ),
  'SYNC_CONFLICT': ErrorMessage(
    code: 'SYNC_CONFLICT',
    httpStatus: 409,
    en: 'Sync conflict detected. Please resolve manually.',
    ar: 'تم اكتشاف تعارض في المزامنة. يرجى الحل يدوياً.',
    retryable: false,
  ),
  'CERTIFICATE_ERROR': ErrorMessage(
    code: 'CERTIFICATE_ERROR',
    httpStatus: 0,
    en: 'Security certificate error',
    ar: 'خطأ في شهادة الأمان',
    retryable: false,
  ),

  // ── Generic ──────────────────────────────────────────────────────────
  'UNKNOWN': ErrorMessage(
    code: 'UNKNOWN',
    httpStatus: 0,
    en: 'An unexpected error occurred',
    ar: 'حدث خطأ غير متوقع',
    retryable: false,
  ),
};

/// Get the ErrorMessage for a given code.
ErrorMessage getErrorMessage(String code) {
  return errorMessages[code] ?? errorMessages[ErrorCodes.unknown]!;
}

/// Get localized error text.
String getLocalizedError(String code, {String locale = 'ar'}) {
  return getErrorMessage(code).localized(locale);
}

/// Map an HTTP status code to the best matching error code.
String httpStatusToErrorCode(int status) {
  return switch (status) {
    401 => ErrorCodes.unauthorized,
    403 => ErrorCodes.forbidden,
    404 => ErrorCodes.notFound,
    409 => ErrorCodes.conflict,
    429 => ErrorCodes.rateLimited,
    400 => ErrorCodes.badRequest,
    502 => ErrorCodes.invalidResponse,
    503 => ErrorCodes.serviceUnavailable,
    504 => ErrorCodes.gatewayTimeout,
    >= 500 => ErrorCodes.serverError,
    _ => ErrorCodes.unknown,
  };
}

/// Check if an error code is retryable.
bool isRetryable(String code) => getErrorMessage(code).retryable;
