library;

/// SAHOOL Unified Error Handling
/// نظام معالجة الأخطاء الموحد لتطبيق سهول
///
/// Provides a comprehensive exception hierarchy with:
/// - Bilingual error messages (Arabic/English)
/// - Error categorization for analytics
/// - Retry-ability indicators
/// - Recovery suggestions
/// - Proper logging integration

import 'package:dio/dio.dart';
import '../utils/app_logger.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Error Type Enumeration
// ═══════════════════════════════════════════════════════════════════════════

/// Categories of errors for analytics and handling
enum ErrorType {
  /// Network connectivity issues
  network,

  /// Server-side errors (5xx)
  server,

  /// Client-side errors (4xx)
  client,

  /// Authentication/Authorization errors
  auth,

  /// Validation errors
  validation,

  /// Local storage/database errors
  storage,

  /// Timeout errors
  timeout,

  /// Resource not found
  notFound,

  /// Rate limiting
  rateLimit,

  /// Security-related errors (certificate pinning, etc.)
  security,

  /// Sync/Offline errors
  sync,

  /// Unknown/Unexpected errors
  unknown,
}

/// Severity levels for error reporting
enum ErrorSeverity {
  /// Informational - user should be notified
  info,

  /// Warning - operation may have partial failure
  warning,

  /// Error - operation failed but can retry
  error,

  /// Critical - operation failed, may need intervention
  critical,
}

// ═══════════════════════════════════════════════════════════════════════════
// Base App Exception
// ═══════════════════════════════════════════════════════════════════════════

/// Base exception class for all SAHOOL app exceptions
///
/// Provides bilingual messages, error categorization, and recovery hints.
///
/// Usage:
/// ```dart
/// throw AppException(
///   message: 'Failed to load fields',
///   messageAr: 'فشل في تحميل الحقول',
///   type: ErrorType.network,
/// );
/// ```
class AppException implements Exception {
  /// English error message (for logging and debugging)
  final String message;

  /// Arabic error message (for user display)
  final String messageAr;

  /// Error type for categorization
  final ErrorType type;

  /// Error severity level
  final ErrorSeverity severity;

  /// Error code for identification
  final String? code;

  /// HTTP status code (if applicable)
  final int? statusCode;

  /// Whether this error can be retried
  final bool isRetryable;

  /// Original error that caused this exception
  final Object? originalError;

  /// Stack trace from original error
  final StackTrace? originalStackTrace;

  /// Additional context data
  final Map<String, dynamic>? context;

  /// Recovery suggestion for the user
  final String? recoverySuggestion;

  /// Arabic recovery suggestion
  final String? recoverySuggestionAr;

  const AppException({
    required this.message,
    required this.messageAr,
    this.type = ErrorType.unknown,
    this.severity = ErrorSeverity.error,
    this.code,
    this.statusCode,
    this.isRetryable = false,
    this.originalError,
    this.originalStackTrace,
    this.context,
    this.recoverySuggestion,
    this.recoverySuggestionAr,
  });

  /// Get the user-facing message based on locale
  String getUserMessage({bool isArabic = true}) {
    return isArabic ? messageAr : message;
  }

  /// Get recovery suggestion based on locale
  String? getRecoverySuggestion({bool isArabic = true}) {
    return isArabic ? recoverySuggestionAr : recoverySuggestion;
  }

  /// Log this exception with proper context
  void log({String? tag}) {
    final logTag = tag ?? 'AppException';
    final logData = {
      'code': code,
      'type': type.name,
      'severity': severity.name,
      'statusCode': statusCode,
      'isRetryable': isRetryable,
      if (context != null) ...context!,
    };

    switch (severity) {
      case ErrorSeverity.critical:
        AppLogger.critical(message,
            tag: logTag, error: originalError, data: logData);
        break;
      case ErrorSeverity.error:
        AppLogger.e(message, tag: logTag, error: originalError, data: logData);
        break;
      case ErrorSeverity.warning:
        AppLogger.w(message, tag: logTag, data: logData);
        break;
      case ErrorSeverity.info:
        AppLogger.i(message, tag: logTag, data: logData);
        break;
    }
  }

  @override
  String toString() => 'AppException[$code]: $message';

  /// Create a copy with updated fields
  AppException copyWith({
    String? message,
    String? messageAr,
    ErrorType? type,
    ErrorSeverity? severity,
    String? code,
    int? statusCode,
    bool? isRetryable,
    Object? originalError,
    StackTrace? originalStackTrace,
    Map<String, dynamic>? context,
    String? recoverySuggestion,
    String? recoverySuggestionAr,
  }) {
    return AppException(
      message: message ?? this.message,
      messageAr: messageAr ?? this.messageAr,
      type: type ?? this.type,
      severity: severity ?? this.severity,
      code: code ?? this.code,
      statusCode: statusCode ?? this.statusCode,
      isRetryable: isRetryable ?? this.isRetryable,
      originalError: originalError ?? this.originalError,
      originalStackTrace: originalStackTrace ?? this.originalStackTrace,
      context: context ?? this.context,
      recoverySuggestion: recoverySuggestion ?? this.recoverySuggestion,
      recoverySuggestionAr: recoverySuggestionAr ?? this.recoverySuggestionAr,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Specific Exception Types
// ═══════════════════════════════════════════════════════════════════════════

/// Network-related exceptions
class NetworkException extends AppException {
  const NetworkException({
    super.message = 'Network error occurred',
    super.messageAr = 'حدث خطأ في الشبكة',
    super.code = 'NETWORK_ERROR',
    super.isRetryable = true,
    super.originalError,
    super.originalStackTrace,
    super.context,
    super.recoverySuggestion = 'Check your internet connection and try again',
    super.recoverySuggestionAr = 'تحقق من اتصالك بالإنترنت وحاول مرة أخرى',
  }) : super(
          type: ErrorType.network,
          severity: ErrorSeverity.error,
        );

  /// No internet connection
  factory NetworkException.noConnection({Object? originalError}) {
    return NetworkException(
      message: 'No internet connection',
      messageAr: 'لا يوجد اتصال بالإنترنت',
      code: 'NO_CONNECTION',
      isRetryable: true,
      originalError: originalError,
      recoverySuggestion: 'Please check your Wi-Fi or mobile data connection',
      recoverySuggestionAr: 'يرجى التحقق من اتصال Wi-Fi أو بيانات الجوال',
    );
  }

  /// Connection timeout
  factory NetworkException.timeout({Object? originalError}) {
    return NetworkException(
      message: 'Connection timed out',
      messageAr: 'انتهت مهلة الاتصال',
      code: 'TIMEOUT',
      isRetryable: true,
      originalError: originalError,
      recoverySuggestion:
          'The server is taking too long to respond. Try again later',
      recoverySuggestionAr: 'الخادم يستغرق وقتًا طويلاً للرد. حاول لاحقًا',
    );
  }

  /// DNS resolution failed
  factory NetworkException.dnsFailure({Object? originalError}) {
    return NetworkException(
      message: 'Could not resolve server address',
      messageAr: 'تعذر الوصول إلى عنوان الخادم',
      code: 'DNS_FAILURE',
      isRetryable: true,
      originalError: originalError,
    );
  }
}

/// Server-side exceptions (5xx errors)
class ServerException extends AppException {
  const ServerException({
    super.message = 'Server error occurred',
    super.messageAr = 'حدث خطأ في الخادم',
    super.code = 'SERVER_ERROR',
    super.statusCode,
    super.isRetryable = true,
    super.originalError,
    super.originalStackTrace,
    super.context,
    super.recoverySuggestion =
        'Our servers are experiencing issues. Please try again later',
    super.recoverySuggestionAr = 'خوادمنا تواجه مشاكل. يرجى المحاولة لاحقًا',
  }) : super(
          type: ErrorType.server,
          severity: ErrorSeverity.error,
        );

  /// Internal server error (500)
  factory ServerException.internalError(
      {int? statusCode, Object? originalError}) {
    return ServerException(
      message: 'Internal server error',
      messageAr: 'خطأ داخلي في الخادم',
      code: 'INTERNAL_ERROR',
      statusCode: statusCode ?? 500,
      originalError: originalError,
    );
  }

  /// Service unavailable (503)
  factory ServerException.unavailable({Object? originalError}) {
    return ServerException(
      message: 'Service temporarily unavailable',
      messageAr: 'الخدمة غير متاحة مؤقتًا',
      code: 'SERVICE_UNAVAILABLE',
      statusCode: 503,
      isRetryable: true,
      originalError: originalError,
      recoverySuggestion:
          'The service is under maintenance. Please try again in a few minutes',
      recoverySuggestionAr: 'الخدمة قيد الصيانة. يرجى المحاولة بعد بضع دقائق',
    );
  }

  /// Gateway timeout (504)
  factory ServerException.gatewayTimeout({Object? originalError}) {
    return ServerException(
      message: 'Gateway timeout',
      messageAr: 'انتهت مهلة البوابة',
      code: 'GATEWAY_TIMEOUT',
      statusCode: 504,
      isRetryable: true,
      originalError: originalError,
    );
  }
}

/// Authentication and authorization exceptions
class AuthException extends AppException {
  const AuthException({
    super.message = 'Authentication error',
    super.messageAr = 'خطأ في المصادقة',
    super.code = 'AUTH_ERROR',
    super.statusCode,
    super.isRetryable = false,
    super.originalError,
    super.originalStackTrace,
    super.context,
    super.recoverySuggestion,
    super.recoverySuggestionAr,
  }) : super(
          type: ErrorType.auth,
          severity: ErrorSeverity.error,
        );

  /// Invalid credentials
  factory AuthException.invalidCredentials({Object? originalError}) {
    return AuthException(
      message: 'Invalid email or password',
      messageAr: 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
      code: 'INVALID_CREDENTIALS',
      statusCode: 401,
      originalError: originalError,
      recoverySuggestion: 'Please check your email and password and try again',
      recoverySuggestionAr:
          'يرجى التحقق من البريد الإلكتروني وكلمة المرور والمحاولة مرة أخرى',
    );
  }

  /// Session expired
  factory AuthException.sessionExpired({Object? originalError}) {
    return AuthException(
      message: 'Your session has expired',
      messageAr: 'انتهت صلاحية جلستك',
      code: 'SESSION_EXPIRED',
      statusCode: 401,
      originalError: originalError,
      recoverySuggestion: 'Please log in again to continue',
      recoverySuggestionAr: 'يرجى تسجيل الدخول مرة أخرى للمتابعة',
    );
  }

  /// Unauthorized access
  factory AuthException.unauthorized({Object? originalError}) {
    return AuthException(
      message: 'You are not authorized to perform this action',
      messageAr: 'غير مصرح لك بتنفيذ هذا الإجراء',
      code: 'UNAUTHORIZED',
      statusCode: 403,
      originalError: originalError,
    );
  }

  /// Token refresh failed
  factory AuthException.tokenRefreshFailed({Object? originalError}) {
    return AuthException(
      message: 'Failed to refresh authentication',
      messageAr: 'فشل تجديد المصادقة',
      code: 'TOKEN_REFRESH_FAILED',
      originalError: originalError,
      recoverySuggestion: 'Please log in again',
      recoverySuggestionAr: 'يرجى تسجيل الدخول مرة أخرى',
    );
  }

  /// Biometric authentication failed
  factory AuthException.biometricFailed(
      {String? reason, Object? originalError}) {
    return AuthException(
      message: reason ?? 'Biometric authentication failed',
      messageAr: 'فشل التحقق بالبصمة',
      code: 'BIOMETRIC_FAILED',
      originalError: originalError,
      recoverySuggestion: 'Try using your password instead',
      recoverySuggestionAr: 'حاول استخدام كلمة المرور بدلاً من ذلك',
    );
  }
}

/// Validation exceptions
class ValidationException extends AppException {
  /// Field-specific validation errors
  final Map<String, String>? fieldErrors;

  /// Arabic field-specific validation errors
  final Map<String, String>? fieldErrorsAr;

  const ValidationException({
    super.message = 'Validation error',
    super.messageAr = 'خطأ في البيانات',
    super.code = 'VALIDATION_ERROR',
    super.statusCode = 400,
    super.originalError,
    super.originalStackTrace,
    super.context,
    this.fieldErrors,
    this.fieldErrorsAr,
  }) : super(
          type: ErrorType.validation,
          severity: ErrorSeverity.warning,
          isRetryable: false,
        );

  /// Required field missing
  factory ValidationException.requiredField(
      String fieldName, String fieldNameAr) {
    return ValidationException(
      message: '$fieldName is required',
      messageAr: '$fieldNameAr مطلوب',
      code: 'REQUIRED_FIELD',
      fieldErrors: {fieldName: 'This field is required'},
      fieldErrorsAr: {fieldNameAr: 'هذا الحقل مطلوب'},
    );
  }

  /// Invalid format
  factory ValidationException.invalidFormat(
      String fieldName, String fieldNameAr) {
    return ValidationException(
      message: '$fieldName has an invalid format',
      messageAr: 'صيغة $fieldNameAr غير صالحة',
      code: 'INVALID_FORMAT',
      fieldErrors: {fieldName: 'Invalid format'},
      fieldErrorsAr: {fieldNameAr: 'صيغة غير صالحة'},
    );
  }

  /// Value out of range
  factory ValidationException.outOfRange(String fieldName, String fieldNameAr,
      {num? min, num? max}) {
    final rangeMsg = min != null && max != null
        ? 'must be between $min and $max'
        : min != null
            ? 'must be at least $min'
            : 'must be at most $max';
    final rangeMsgAr = min != null && max != null
        ? 'يجب أن يكون بين $min و $max'
        : min != null
            ? 'يجب أن يكون على الأقل $min'
            : 'يجب أن يكون على الأكثر $max';

    return ValidationException(
      message: '$fieldName $rangeMsg',
      messageAr: '$fieldNameAr $rangeMsgAr',
      code: 'OUT_OF_RANGE',
    );
  }
}

/// Not found exceptions
class NotFoundException extends AppException {
  const NotFoundException({
    super.message = 'Resource not found',
    super.messageAr = 'المورد غير موجود',
    super.code = 'NOT_FOUND',
    super.statusCode = 404,
    super.originalError,
    super.originalStackTrace,
    super.context,
  }) : super(
          type: ErrorType.notFound,
          severity: ErrorSeverity.warning,
          isRetryable: false,
        );

  /// Field not found
  factory NotFoundException.field(String fieldId) {
    return NotFoundException(
      message: 'Field not found',
      messageAr: 'الحقل غير موجود',
      code: 'FIELD_NOT_FOUND',
      context: {'fieldId': fieldId},
    );
  }

  /// Task not found
  factory NotFoundException.task(String taskId) {
    return NotFoundException(
      message: 'Task not found',
      messageAr: 'المهمة غير موجودة',
      code: 'TASK_NOT_FOUND',
      context: {'taskId': taskId},
    );
  }

  /// User not found
  factory NotFoundException.user(String userId) {
    return NotFoundException(
      message: 'User not found',
      messageAr: 'المستخدم غير موجود',
      code: 'USER_NOT_FOUND',
      context: {'userId': userId},
    );
  }
}

/// Rate limit exceptions
class RateLimitException extends AppException {
  /// When the rate limit resets
  final DateTime? retryAfter;

  const RateLimitException({
    super.message = 'Too many requests',
    super.messageAr = 'طلبات كثيرة جدًا',
    super.code = 'RATE_LIMITED',
    super.statusCode = 429,
    super.originalError,
    super.originalStackTrace,
    super.context,
    this.retryAfter,
    super.recoverySuggestion = 'Please wait a moment before trying again',
    super.recoverySuggestionAr = 'يرجى الانتظار لحظة قبل المحاولة مرة أخرى',
  }) : super(
          type: ErrorType.rateLimit,
          severity: ErrorSeverity.warning,
          isRetryable: true,
        );
}

/// Security exceptions
class SecurityException extends AppException {
  const SecurityException({
    super.message = 'Security error',
    super.messageAr = 'خطأ أمني',
    super.code = 'SECURITY_ERROR',
    super.originalError,
    super.originalStackTrace,
    super.context,
    super.recoverySuggestion,
    super.recoverySuggestionAr,
  }) : super(
          type: ErrorType.security,
          severity: ErrorSeverity.critical,
          isRetryable: false,
        );

  /// Certificate pinning failure
  factory SecurityException.certificatePinningFailed({Object? originalError}) {
    return SecurityException(
      message: 'SSL certificate verification failed',
      messageAr: 'فشل التحقق من شهادة SSL',
      code: 'CERT_PINNING_FAILED',
      originalError: originalError,
      recoverySuggestion: 'Please update the app or contact support',
      recoverySuggestionAr: 'يرجى تحديث التطبيق أو الاتصال بالدعم',
    );
  }

  /// Tampered request
  factory SecurityException.requestTampered({Object? originalError}) {
    return SecurityException(
      message: 'Request integrity check failed',
      messageAr: 'فشل التحقق من سلامة الطلب',
      code: 'REQUEST_TAMPERED',
      originalError: originalError,
    );
  }
}

/// Storage/Database exceptions
class StorageException extends AppException {
  const StorageException({
    super.message = 'Storage error',
    super.messageAr = 'خطأ في التخزين',
    super.code = 'STORAGE_ERROR',
    super.originalError,
    super.originalStackTrace,
    super.context,
    super.recoverySuggestion,
    super.recoverySuggestionAr,
  }) : super(
          type: ErrorType.storage,
          severity: ErrorSeverity.error,
          isRetryable: false,
        );

  /// Database error
  factory StorageException.database({String? details, Object? originalError}) {
    return StorageException(
      message: details ?? 'Database operation failed',
      messageAr: 'فشلت عملية قاعدة البيانات',
      code: 'DATABASE_ERROR',
      originalError: originalError,
    );
  }

  /// Encryption error
  factory StorageException.encryption({Object? originalError}) {
    return StorageException(
      message: 'Data encryption/decryption failed',
      messageAr: 'فشل تشفير/فك تشفير البيانات',
      code: 'ENCRYPTION_ERROR',
      originalError: originalError,
    );
  }

  /// Storage full
  factory StorageException.full({Object? originalError}) {
    return StorageException(
      message: 'Device storage is full',
      messageAr: 'مساحة التخزين ممتلئة',
      code: 'STORAGE_FULL',
      originalError: originalError,
      recoverySuggestion: 'Free up some space on your device',
      recoverySuggestionAr: 'قم بتحرير بعض المساحة على جهازك',
    );
  }
}

/// Sync/Offline exceptions
class SyncException extends AppException {
  const SyncException({
    super.message = 'Sync error',
    super.messageAr = 'خطأ في المزامنة',
    super.code = 'SYNC_ERROR',
    super.originalError,
    super.originalStackTrace,
    super.context,
    super.recoverySuggestion =
        'Your changes will sync when you\'re back online',
    super.recoverySuggestionAr = 'سيتم مزامنة تغييراتك عندما تعود للاتصال',
  }) : super(
          type: ErrorType.sync,
          severity: ErrorSeverity.warning,
          isRetryable: true,
        );

  /// Conflict during sync
  factory SyncException.conflict(
      {String? entityType, String? entityId, Object? originalError}) {
    return SyncException(
      message: 'Sync conflict detected',
      messageAr: 'تم اكتشاف تعارض في المزامنة',
      code: 'SYNC_CONFLICT',
      originalError: originalError,
      context: {
        if (entityType != null) 'entityType': entityType,
        if (entityId != null) 'entityId': entityId,
      },
      recoverySuggestion: 'Please review the conflicting changes',
      recoverySuggestionAr: 'يرجى مراجعة التغييرات المتعارضة',
    );
  }

  /// Offline mode
  factory SyncException.offline({Object? originalError}) {
    return SyncException(
      message: 'You are currently offline',
      messageAr: 'أنت حاليًا غير متصل',
      code: 'OFFLINE',
      originalError: originalError,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Exception Factory from Dio Errors
// ═══════════════════════════════════════════════════════════════════════════

/// Convert DioException to AppException
AppException fromDioException(DioException e) {
  switch (e.type) {
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.sendTimeout:
    case DioExceptionType.receiveTimeout:
      return NetworkException.timeout(originalError: e);

    case DioExceptionType.connectionError:
      return NetworkException.noConnection(originalError: e);

    case DioExceptionType.badCertificate:
      return SecurityException.certificatePinningFailed(originalError: e);

    case DioExceptionType.cancel:
      return AppException(
        message: 'Request was cancelled',
        messageAr: 'تم إلغاء الطلب',
        code: 'REQUEST_CANCELLED',
        type: ErrorType.client,
        isRetryable: false,
        originalError: e,
      );

    case DioExceptionType.badResponse:
      return _fromHttpStatus(e.response?.statusCode, e.response?.data, e);

    case DioExceptionType.unknown:
      if (e.message?.contains('SocketException') ?? false) {
        return NetworkException.noConnection(originalError: e);
      }
      return AppException(
        message: 'An unexpected error occurred',
        messageAr: 'حدث خطأ غير متوقع',
        code: 'UNKNOWN_ERROR',
        type: ErrorType.unknown,
        originalError: e,
      );
  }
}

/// Convert HTTP status code to AppException
AppException _fromHttpStatus(
    int? statusCode, dynamic responseData, Object? originalError) {
  // Extract message from response
  String? serverMessage;
  String? serverMessageAr;
  if (responseData is Map) {
    serverMessage = responseData['message'] ?? responseData['error'];
    serverMessageAr = responseData['message_ar'] ?? responseData['messageAr'];
  }

  switch (statusCode) {
    case 400:
      return ValidationException(
        message: serverMessage ?? 'Invalid request',
        messageAr: serverMessageAr ?? 'طلب غير صالح',
        statusCode: 400,
        originalError: originalError,
      );

    case 401:
      // Check if it's a session expiry or invalid credentials
      final isSessionExpired =
          serverMessage?.toLowerCase().contains('expired') ?? false;
      if (isSessionExpired) {
        return AuthException.sessionExpired(originalError: originalError);
      }
      return AuthException.invalidCredentials(originalError: originalError);

    case 403:
      return AuthException.unauthorized(originalError: originalError);

    case 404:
      return NotFoundException(
        message: serverMessage ?? 'Resource not found',
        messageAr: serverMessageAr ?? 'المورد غير موجود',
        originalError: originalError,
      );

    case 408:
      return NetworkException.timeout(originalError: originalError);

    case 409:
      return SyncException.conflict(originalError: originalError);

    case 413:
      return ValidationException(
        message: 'File is too large',
        messageAr: 'حجم الملف كبير جدًا',
        code: 'PAYLOAD_TOO_LARGE',
        statusCode: 413,
        originalError: originalError,
      );

    case 422:
      return ValidationException(
        message: serverMessage ?? 'Validation failed',
        messageAr: serverMessageAr ?? 'فشل التحقق من البيانات',
        statusCode: 422,
        originalError: originalError,
      );

    case 429:
      return RateLimitException(originalError: originalError);

    case 500:
      return ServerException.internalError(
          statusCode: 500, originalError: originalError);

    case 502:
      return ServerException(
        message: 'Bad gateway',
        messageAr: 'بوابة غير صالحة',
        code: 'BAD_GATEWAY',
        statusCode: 502,
        originalError: originalError,
      );

    case 503:
      return ServerException.unavailable(originalError: originalError);

    case 504:
      return ServerException.gatewayTimeout(originalError: originalError);

    default:
      if (statusCode != null && statusCode >= 500) {
        return ServerException.internalError(
            statusCode: statusCode, originalError: originalError);
      }
      return AppException(
        message: serverMessage ?? 'Request failed',
        messageAr: serverMessageAr ?? 'فشل الطلب',
        code: 'HTTP_$statusCode',
        statusCode: statusCode,
        type: statusCode != null && statusCode >= 400 && statusCode < 500
            ? ErrorType.client
            : ErrorType.unknown,
        originalError: originalError,
      );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Extension Methods
// ═══════════════════════════════════════════════════════════════════════════

/// Extension to convert any exception to AppException
extension ExceptionExtension on Object {
  /// Convert any error to AppException
  AppException toAppException({String? tag}) {
    if (this is AppException) {
      return this as AppException;
    }

    if (this is DioException) {
      return fromDioException(this as DioException);
    }

    // Generic fallback
    return AppException(
      message: toString(),
      messageAr: 'حدث خطأ غير متوقع',
      code: 'UNEXPECTED_ERROR',
      type: ErrorType.unknown,
      originalError: this,
    );
  }
}

/// Extension for error handling in async operations
extension FutureErrorHandling<T> on Future<T> {
  /// Handle errors and convert to AppException
  Future<T> handleErrors({String? tag, bool log = true}) async {
    try {
      return await this;
    } catch (e, stackTrace) {
      final appException = e.toAppException().copyWith(
            originalStackTrace: stackTrace,
          );
      if (log) {
        appException.log(tag: tag);
      }
      throw appException;
    }
  }
}
