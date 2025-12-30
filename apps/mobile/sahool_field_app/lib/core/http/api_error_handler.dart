import 'package:dio/dio.dart';
import '../utils/app_logger.dart';

/// Standardized API error types
enum ApiErrorType {
  /// Network connectivity issues
  network,

  /// Server errors (5xx)
  server,

  /// Authentication/authorization errors (401, 403)
  auth,

  /// Validation errors (400, 422)
  validation,

  /// Resource not found (404)
  notFound,

  /// Request timeout
  timeout,

  /// Rate limiting (429)
  rateLimited,

  /// Client errors (other 4xx)
  client,

  /// SSL/Certificate errors
  certificate,

  /// Request cancelled
  cancelled,

  /// Unknown/unexpected errors
  unknown,
}

/// Standardized API error with user-friendly messages
class ApiError {
  final ApiErrorType type;
  final String message;
  final String? technicalMessage;
  final String? code;
  final int? statusCode;
  final dynamic data;
  final Exception exception;
  final StackTrace? stackTrace;

  const ApiError({
    required this.type,
    required this.message,
    this.technicalMessage,
    this.code,
    this.statusCode,
    this.data,
    required this.exception,
    this.stackTrace,
  });

  /// Check if error is retryable
  bool get isRetryable => switch (type) {
        ApiErrorType.network => true,
        ApiErrorType.server => true,
        ApiErrorType.timeout => true,
        ApiErrorType.rateLimited => true,
        ApiErrorType.unknown => true,
        _ => false,
      };

  /// Check if error is a network issue
  bool get isNetworkError => type == ApiErrorType.network;

  /// Check if error requires authentication
  bool get isAuthError => type == ApiErrorType.auth;

  /// Check if error is a server issue
  bool get isServerError => type == ApiErrorType.server;

  /// Check if error is a validation issue
  bool get isValidationError => type == ApiErrorType.validation;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ApiError &&
          runtimeType == other.runtimeType &&
          type == other.type &&
          message == other.message &&
          code == other.code &&
          statusCode == other.statusCode;

  @override
  int get hashCode =>
      type.hashCode ^
      message.hashCode ^
      code.hashCode ^
      statusCode.hashCode;

  @override
  String toString() =>
      'ApiError(type: $type, message: $message, code: $code, statusCode: $statusCode)';

  /// Convert to JSON for logging
  Map<String, dynamic> toJson() => {
        'type': type.name,
        'message': message,
        'technicalMessage': technicalMessage,
        'code': code,
        'statusCode': statusCode,
        'data': data,
      };
}

/// API Error Handler - Converts exceptions to standardized errors
class ApiErrorHandler {
  /// Handle DioException and convert to ApiError
  static ApiError handleError(
    DioException error, {
    StackTrace? stackTrace,
  }) {
    AppLogger.e(
      'API Error occurred',
      tag: 'API_ERROR',
      error: error,
      stackTrace: stackTrace,
      data: {
        'type': error.type.name,
        'statusCode': error.response?.statusCode,
        'path': error.requestOptions.path,
      },
    );

    return switch (error.type) {
      // Timeout errors
      DioExceptionType.connectionTimeout ||
      DioExceptionType.sendTimeout ||
      DioExceptionType.receiveTimeout =>
        _handleTimeoutError(error, stackTrace),

      // Connection errors (no internet, DNS failure, etc.)
      DioExceptionType.connectionError => _handleConnectionError(error, stackTrace),

      // Bad response (4xx, 5xx)
      DioExceptionType.badResponse => _handleBadResponse(error, stackTrace),

      // Certificate/SSL errors
      DioExceptionType.badCertificate =>
        _handleCertificateError(error, stackTrace),

      // Request cancelled
      DioExceptionType.cancel => _handleCancelError(error, stackTrace),

      // Unknown errors
      DioExceptionType.unknown => _handleUnknownError(error, stackTrace),
    };
  }

  /// Handle timeout errors
  static ApiError _handleTimeoutError(
    DioException error,
    StackTrace? stackTrace,
  ) {
    return ApiError(
      type: ApiErrorType.timeout,
      message: 'انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى',
      technicalMessage: 'Request timeout: ${error.type.name}',
      code: 'TIMEOUT',
      exception: error,
      stackTrace: stackTrace,
    );
  }

  /// Handle connection errors
  static ApiError _handleConnectionError(
    DioException error,
    StackTrace? stackTrace,
  ) {
    return ApiError(
      type: ApiErrorType.network,
      message: 'لا يوجد اتصال بالإنترنت. يرجى التحقق من الاتصال والمحاولة مرة أخرى',
      technicalMessage: 'Connection error: ${error.message}',
      code: 'NO_CONNECTION',
      exception: error,
      stackTrace: stackTrace,
    );
  }

  /// Handle bad response (HTTP errors)
  static ApiError _handleBadResponse(
    DioException error,
    StackTrace? stackTrace,
  ) {
    final statusCode = error.response?.statusCode ?? 0;
    final data = error.response?.data;

    // Extract error message from response
    String? serverMessage;
    String? errorCode;

    if (data is Map) {
      serverMessage = data['message'] ??
          data['error'] ??
          data['detail'] ??
          data['msg'];
      errorCode = data['code'] ?? data['error_code'];
    } else if (data is String) {
      serverMessage = data;
    }

    // Determine error type based on status code
    return switch (statusCode) {
      // Authentication errors
      401 => ApiError(
          type: ApiErrorType.auth,
          message: 'انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى',
          technicalMessage: serverMessage ?? 'Unauthorized',
          code: errorCode ?? 'UNAUTHORIZED',
          statusCode: statusCode,
          data: data,
          exception: error,
          stackTrace: stackTrace,
        ),

      // Forbidden
      403 => ApiError(
          type: ApiErrorType.auth,
          message: 'ليس لديك صلاحية للوصول إلى هذا المورد',
          technicalMessage: serverMessage ?? 'Forbidden',
          code: errorCode ?? 'FORBIDDEN',
          statusCode: statusCode,
          data: data,
          exception: error,
          stackTrace: stackTrace,
        ),

      // Not found
      404 => ApiError(
          type: ApiErrorType.notFound,
          message: 'المورد المطلوب غير موجود',
          technicalMessage: serverMessage ?? 'Not found',
          code: errorCode ?? 'NOT_FOUND',
          statusCode: statusCode,
          data: data,
          exception: error,
          stackTrace: stackTrace,
        ),

      // Validation errors
      400 || 422 => ApiError(
          type: ApiErrorType.validation,
          message: serverMessage ?? 'البيانات المدخلة غير صحيحة. يرجى التحقق والمحاولة مرة أخرى',
          technicalMessage: serverMessage ?? 'Validation error',
          code: errorCode ?? 'VALIDATION_ERROR',
          statusCode: statusCode,
          data: data,
          exception: error,
          stackTrace: stackTrace,
        ),

      // Rate limiting
      429 => ApiError(
          type: ApiErrorType.rateLimited,
          message: 'تم تجاوز عدد الطلبات المسموح به. يرجى المحاولة لاحقاً',
          technicalMessage: serverMessage ?? 'Too many requests',
          code: errorCode ?? 'RATE_LIMITED',
          statusCode: statusCode,
          data: data,
          exception: error,
          stackTrace: stackTrace,
        ),

      // Server errors (5xx)
      >= 500 && < 600 => ApiError(
          type: ApiErrorType.server,
          message: 'حدث خطأ في الخادم. يرجى المحاولة لاحقاً',
          technicalMessage: serverMessage ?? 'Server error',
          code: errorCode ?? 'SERVER_ERROR',
          statusCode: statusCode,
          data: data,
          exception: error,
          stackTrace: stackTrace,
        ),

      // Other client errors (4xx)
      >= 400 && < 500 => ApiError(
          type: ApiErrorType.client,
          message: serverMessage ?? 'حدث خطأ في الطلب. يرجى المحاولة مرة أخرى',
          technicalMessage: serverMessage ?? 'Client error',
          code: errorCode ?? 'CLIENT_ERROR',
          statusCode: statusCode,
          data: data,
          exception: error,
          stackTrace: stackTrace,
        ),

      // Unknown status code
      _ => ApiError(
          type: ApiErrorType.unknown,
          message: 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى',
          technicalMessage: serverMessage ?? 'Unknown error',
          code: errorCode ?? 'UNKNOWN',
          statusCode: statusCode,
          data: data,
          exception: error,
          stackTrace: stackTrace,
        ),
    };
  }

  /// Handle certificate errors
  static ApiError _handleCertificateError(
    DioException error,
    StackTrace? stackTrace,
  ) {
    return ApiError(
      type: ApiErrorType.certificate,
      message: 'حدث خطأ في التحقق من شهادة الأمان. يرجى التحقق من الاتصال',
      technicalMessage: 'Certificate validation failed: ${error.message}',
      code: 'CERTIFICATE_ERROR',
      exception: error,
      stackTrace: stackTrace,
    );
  }

  /// Handle cancel errors
  static ApiError _handleCancelError(
    DioException error,
    StackTrace? stackTrace,
  ) {
    return ApiError(
      type: ApiErrorType.cancelled,
      message: 'تم إلغاء الطلب',
      technicalMessage: 'Request cancelled',
      code: 'CANCELLED',
      exception: error,
      stackTrace: stackTrace,
    );
  }

  /// Handle unknown errors
  static ApiError _handleUnknownError(
    DioException error,
    StackTrace? stackTrace,
  ) {
    return ApiError(
      type: ApiErrorType.unknown,
      message: 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى',
      technicalMessage: error.message ?? 'Unknown error occurred',
      code: 'UNKNOWN',
      exception: error,
      stackTrace: stackTrace,
    );
  }

  /// Handle generic exceptions
  static ApiError handleGenericError(
    Exception error, {
    StackTrace? stackTrace,
  }) {
    AppLogger.e(
      'Generic error occurred',
      tag: 'API_ERROR',
      error: error,
      stackTrace: stackTrace,
    );

    return ApiError(
      type: ApiErrorType.unknown,
      message: 'حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى',
      technicalMessage: error.toString(),
      code: 'UNKNOWN',
      exception: error,
      stackTrace: stackTrace,
    );
  }

  /// Get user-friendly error message for common error codes
  static String getUserMessage(String? code, {String? defaultMessage}) {
    return switch (code?.toUpperCase()) {
      'TIMEOUT' => 'انتهت مهلة الاتصال. يرجى المحاولة مرة أخرى',
      'NO_CONNECTION' => 'لا يوجد اتصال بالإنترنت',
      'UNAUTHORIZED' => 'انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى',
      'FORBIDDEN' => 'ليس لديك صلاحية للوصول',
      'NOT_FOUND' => 'المورد المطلوب غير موجود',
      'VALIDATION_ERROR' => 'البيانات المدخلة غير صحيحة',
      'RATE_LIMITED' => 'تم تجاوز عدد الطلبات المسموح به',
      'SERVER_ERROR' => 'حدث خطأ في الخادم',
      'CERTIFICATE_ERROR' => 'خطأ في شهادة الأمان',
      'CANCELLED' => 'تم إلغاء الطلب',
      _ => defaultMessage ?? 'حدث خطأ غير متوقع',
    };
  }
}
