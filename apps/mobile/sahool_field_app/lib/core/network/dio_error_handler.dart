/// Sahool Dio Error Handler
/// معالج أخطاء Dio لتحويلها لرسائل عربية مفهومة
library;

import 'package:dio/dio.dart';
import '../error_handling/app_exceptions.dart';
import 'api_result.dart';

/// معالج أخطاء Dio الموحد
///
/// Converts [DioException] to user-friendly error messages with:
/// - Bilingual messages (Arabic/English)
/// - Error categorization
/// - Retry-ability detection
/// - Timeout-specific handling
class DioErrorHandler {
  /// تحويل DioException لـ Failure مع رسالة عربية
  static Failure<T> handle<T>(DioException e) {
    final appException = fromDioException(e);
    return Failure<T>(
      appException.messageAr,
      statusCode: appException.statusCode,
      originalError: e,
    );
  }

  /// Convert DioException to AppException for detailed error handling
  static AppException toAppException(DioException e) {
    return fromDioException(e);
  }

  /// الحصول على رسالة الخطأ بالعربية
  static String getErrorMessage(DioException e) {
    return fromDioException(e).messageAr;
  }

  /// الحصول على رسالة الخطأ بالإنجليزية
  static String getErrorMessageEn(DioException e) {
    return fromDioException(e).message;
  }

  /// التحقق من كون الخطأ قابل لإعادة المحاولة
  static bool isRetryable(DioException e) {
    return fromDioException(e).isRetryable;
  }

  /// Check if this is a timeout error
  static bool isTimeoutError(DioException e) {
    return e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.receiveTimeout;
  }

  /// Check if this is a connection error
  static bool isConnectionError(DioException e) {
    return e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.connectionTimeout;
  }

  /// Check if this is a server error (5xx)
  static bool isServerError(DioException e) {
    final statusCode = e.response?.statusCode;
    return statusCode != null && statusCode >= 500 && statusCode < 600;
  }

  /// Check if this is a client error (4xx)
  static bool isClientError(DioException e) {
    final statusCode = e.response?.statusCode;
    return statusCode != null && statusCode >= 400 && statusCode < 500;
  }

  /// Get appropriate retry delay based on error type
  static Duration getRecommendedRetryDelay(DioException e, int retryAttempt) {
    // For rate limiting (429), check Retry-After header
    if (e.response?.statusCode == 429) {
      final retryAfter = e.response?.headers.value('Retry-After');
      if (retryAfter != null) {
        final seconds = int.tryParse(retryAfter);
        if (seconds != null) {
          return Duration(seconds: seconds);
        }
      }
      // Default rate limit delay
      return Duration(seconds: 30 + (retryAttempt * 10));
    }

    // For server errors, use exponential backoff
    if (isServerError(e)) {
      return Duration(seconds: 2 * (retryAttempt + 1));
    }

    // For timeout errors, shorter delay
    if (isTimeoutError(e)) {
      return Duration(seconds: 1 * (retryAttempt + 1));
    }

    // Default exponential backoff
    return Duration(seconds: 1 * (1 << retryAttempt));
  }
}

/// Extension على Dio للاستخدام السهل
extension DioExtension on Dio {
  /// طلب GET آمن يرجع ApiResult
  Future<ApiResult<T>> safeGet<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    required T Function(dynamic data) fromJson,
  }) async {
    try {
      final response =
          await get(path, queryParameters: queryParameters, options: options);
      return Success(fromJson(response.data));
    } on DioException catch (e) {
      return DioErrorHandler.handle(e);
    } catch (e) {
      final appException = e.toAppException();
      return Failure(appException.messageAr, originalError: e);
    }
  }

  /// طلب POST آمن يرجع ApiResult
  Future<ApiResult<T>> safePost<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    required T Function(dynamic data) fromJson,
  }) async {
    try {
      final response = await post(path,
          data: data, queryParameters: queryParameters, options: options);
      return Success(fromJson(response.data));
    } on DioException catch (e) {
      return DioErrorHandler.handle(e);
    } catch (e) {
      final appException = e.toAppException();
      return Failure(appException.messageAr, originalError: e);
    }
  }

  /// طلب PUT آمن يرجع ApiResult
  Future<ApiResult<T>> safePut<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    required T Function(dynamic data) fromJson,
  }) async {
    try {
      final response = await put(path,
          data: data, queryParameters: queryParameters, options: options);
      return Success(fromJson(response.data));
    } on DioException catch (e) {
      return DioErrorHandler.handle(e);
    } catch (e) {
      final appException = e.toAppException();
      return Failure(appException.messageAr, originalError: e);
    }
  }

  /// طلب DELETE آمن يرجع ApiResult
  Future<ApiResult<T>> safeDelete<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    required T Function(dynamic data) fromJson,
  }) async {
    try {
      final response = await delete(path,
          queryParameters: queryParameters, options: options);
      return Success(fromJson(response.data));
    } on DioException catch (e) {
      return DioErrorHandler.handle(e);
    } catch (e) {
      final appException = e.toAppException();
      return Failure(appException.messageAr, originalError: e);
    }
  }
}
