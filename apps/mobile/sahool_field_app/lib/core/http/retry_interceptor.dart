import 'dart:io';
import 'dart:math';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

/// SAHOOL Retry Interceptor
/// معترض إعادة المحاولة
///
/// Features:
/// - Automatic retry on network errors
/// - Exponential backoff strategy
/// - Configurable retry attempts
/// - Skip retry on client errors (4xx)
/// - Detailed retry logging

class RetryInterceptor extends Interceptor {
  final int maxRetries;
  final Duration initialDelay;

  RetryInterceptor({
    this.maxRetries = 3,
    this.initialDelay = const Duration(seconds: 1),
  });

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    // Get current retry count from request extra data
    final retryCount = err.requestOptions.extra['retry_count'] as int? ?? 0;

    // Check if we should retry
    if (_shouldRetry(err) && retryCount < maxRetries) {
      final nextRetryCount = retryCount + 1;

      // Calculate delay with exponential backoff
      final delay = initialDelay * pow(2, retryCount);

      if (kDebugMode) {
        debugPrint('🔄 Retrying request (attempt $nextRetryCount/$maxRetries)');
        debugPrint('   Path: ${err.requestOptions.path}');
        debugPrint('   Method: ${err.requestOptions.method}');
        debugPrint('   Error: ${err.type}');
        debugPrint('   Delay: ${delay.inSeconds}s');
      }

      // Wait before retrying
      await Future.delayed(delay);

      // Clone request options and increment retry count
      final requestOptions = err.requestOptions;
      requestOptions.extra['retry_count'] = nextRetryCount;

      try {
        // Retry the request
        final response = await Dio(
          BaseOptions(
            baseUrl: requestOptions.baseUrl,
            connectTimeout: requestOptions.connectTimeout,
            receiveTimeout: requestOptions.receiveTimeout,
            sendTimeout: requestOptions.sendTimeout,
            headers: requestOptions.headers,
          ),
        ).request(
          requestOptions.path,
          data: requestOptions.data,
          queryParameters: requestOptions.queryParameters,
          options: Options(
            method: requestOptions.method,
            headers: requestOptions.headers,
            responseType: requestOptions.responseType,
            contentType: requestOptions.contentType,
            validateStatus: requestOptions.validateStatus,
            receiveDataWhenStatusError: requestOptions.receiveDataWhenStatusError,
            followRedirects: requestOptions.followRedirects,
            maxRedirects: requestOptions.maxRedirects,
            extra: requestOptions.extra,
          ),
        );

        if (kDebugMode) {
          debugPrint('✅ Retry successful');
          debugPrint('   Path: ${requestOptions.path}');
          debugPrint('   Attempt: $nextRetryCount');
          debugPrint('   Status: ${response.statusCode}');
        }

        return handler.resolve(response);
      } on DioException catch (e) {
        // If retry also fails, pass it back to this interceptor
        // This allows for multiple retry attempts
        return super.onError(e, handler);
      }
    } else {
      // Max retries exceeded or shouldn't retry
      if (retryCount >= maxRetries && kDebugMode) {
        debugPrint('❌ Max retries exceeded');
        debugPrint('   Path: ${err.requestOptions.path}');
        debugPrint('   Attempts: $retryCount');
        debugPrint('   Error: ${err.type}');
      }

      return super.onError(err, handler);
    }
  }

  /// Determine if the request should be retried
  bool _shouldRetry(DioException error) {
    // Don't retry on client errors (4xx)
    if (error.response != null) {
      final statusCode = error.response!.statusCode ?? 0;
      if (statusCode >= 400 && statusCode < 500) {
        if (kDebugMode) {
          debugPrint('⏭️  Skipping retry for client error (${statusCode})');
        }
        return false;
      }
    }

    // Retry on specific error types
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        if (kDebugMode) {
          debugPrint('⏱️  Timeout error - will retry');
        }
        return true;

      case DioExceptionType.connectionError:
        // Check if it's a network error (SocketException)
        if (error.error is SocketException) {
          if (kDebugMode) {
            debugPrint('🔌 Socket error - will retry');
          }
          return true;
        }
        // Check for timeout exceptions
        if (error.error is TimeoutException) {
          if (kDebugMode) {
            debugPrint('⏱️  Timeout exception - will retry');
          }
          return true;
        }
        return false;

      case DioExceptionType.badResponse:
        // Retry on server errors (5xx)
        final statusCode = error.response?.statusCode ?? 0;
        final shouldRetry = statusCode >= 500;
        if (kDebugMode) {
          if (shouldRetry) {
            debugPrint('🔧 Server error (${statusCode}) - will retry');
          } else {
            debugPrint('⏭️  Bad response (${statusCode}) - will not retry');
          }
        }
        return shouldRetry;

      case DioExceptionType.cancel:
        // Don't retry cancelled requests
        if (kDebugMode) {
          debugPrint('🚫 Request cancelled - will not retry');
        }
        return false;

      default:
        if (kDebugMode) {
          debugPrint('❓ Unknown error type - will not retry');
        }
        return false;
    }
  }
}

/// Retry Configuration
/// Allows customization of retry behavior per endpoint or globally
class RetryConfig {
  final int maxRetries;
  final Duration initialDelay;
  final bool retryOnTimeout;
  final bool retryOnConnectionError;
  final bool retryOnServerError;

  const RetryConfig({
    this.maxRetries = 3,
    this.initialDelay = const Duration(seconds: 1),
    this.retryOnTimeout = true,
    this.retryOnConnectionError = true,
    this.retryOnServerError = true,
  });

  /// Default configuration for most endpoints
  static const RetryConfig standard = RetryConfig(
    maxRetries: 3,
    initialDelay: Duration(seconds: 1),
  );

  /// Aggressive retry for critical operations
  static const RetryConfig aggressive = RetryConfig(
    maxRetries: 5,
    initialDelay: Duration(milliseconds: 500),
  );

  /// Conservative retry for non-critical operations
  static const RetryConfig conservative = RetryConfig(
    maxRetries: 2,
    initialDelay: Duration(seconds: 2),
  );

  /// No retry
  static const RetryConfig none = RetryConfig(
    maxRetries: 0,
  );
}
