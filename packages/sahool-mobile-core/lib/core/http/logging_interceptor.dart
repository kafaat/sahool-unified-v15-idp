import 'package:dio/dio.dart';
import '../utils/app_logger.dart';
import '../utils/pii_filter.dart';

/// SAHOOL Logging Interceptor - Secure HTTP Logging with PII Protection
/// معترض تسجيل الطلبات مع حماية البيانات الشخصية
///
/// Features:
/// - Automatic PII filtering for all requests/responses
/// - Sanitized header logging
/// - Request/Response body sanitization
/// - Error message sanitization
/// - Configurable detail levels
/// - Performance timing
///
/// Usage:
/// ```dart
/// final dio = Dio();
/// dio.interceptors.add(LoggingInterceptor(
///   logRequestBody: true,
///   logResponseBody: true,
/// ));
/// ```

class LoggingInterceptor extends Interceptor {
  final bool logRequestHeaders;
  final bool logRequestBody;
  final bool logResponseHeaders;
  final bool logResponseBody;
  final bool logErrorBody;
  final int maxBodyLength;

  LoggingInterceptor({
    this.logRequestHeaders = true,
    this.logRequestBody = true,
    this.logResponseHeaders = false,
    this.logResponseBody = false,
    this.logErrorBody = true,
    this.maxBodyLength = 2000,
  });

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final startTime = DateTime.now();
    options.extra['request_start_time'] = startTime;

    AppLogger.d(
      '┌─── Request ────────────────────────────────────────────',
      tag: 'HTTP',
    );
    AppLogger.d('│ ${options.method} ${options.uri}', tag: 'HTTP');

    // Log sanitized headers
    if (logRequestHeaders && options.headers.isNotEmpty) {
      final sanitizedHeaders = PiiFilter.sanitizeHeaders(
        options.headers.map((k, v) => MapEntry(k, v)),
      );
      AppLogger.d('│ Headers:', tag: 'HTTP');
      sanitizedHeaders.forEach((key, value) {
        AppLogger.d('│   $key: $value', tag: 'HTTP');
      });
    }

    // Log sanitized body
    if (logRequestBody && options.data != null) {
      final sanitizedBody = PiiFilter.sanitizeRequestBody(options.data);
      final bodyStr = _formatBody(sanitizedBody);
      AppLogger.d('│ Body: $bodyStr', tag: 'HTTP');
    }

    AppLogger.d(
      '└────────────────────────────────────────────────────────',
      tag: 'HTTP',
    );

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    final startTime = response.requestOptions.extra['request_start_time'] as DateTime?;
    final duration = startTime != null
        ? DateTime.now().difference(startTime)
        : null;

    AppLogger.d(
      '┌─── Response ───────────────────────────────────────────',
      tag: 'HTTP',
    );
    AppLogger.d(
      '│ ${response.requestOptions.method} ${response.requestOptions.uri}',
      tag: 'HTTP',
    );
    AppLogger.d(
      '│ Status: ${response.statusCode} ${response.statusMessage ?? ""}',
      tag: 'HTTP',
    );

    if (duration != null) {
      AppLogger.d('│ Duration: ${duration.inMilliseconds}ms', tag: 'HTTP');
    }

    // Log sanitized headers
    if (logResponseHeaders && response.headers.map.isNotEmpty) {
      final sanitizedHeaders = PiiFilter.sanitizeHeaders(
        response.headers.map.map((k, v) => MapEntry(k, v.join(', '))),
      );
      AppLogger.d('│ Headers:', tag: 'HTTP');
      sanitizedHeaders.forEach((key, value) {
        AppLogger.d('│   $key: $value', tag: 'HTTP');
      });
    }

    // Log sanitized response body
    if (logResponseBody && response.data != null) {
      final sanitizedBody = PiiFilter.sanitizeResponseBody(response.data);
      final bodyStr = _formatBody(sanitizedBody);
      AppLogger.d('│ Body: $bodyStr', tag: 'HTTP');
    }

    AppLogger.d(
      '└────────────────────────────────────────────────────────',
      tag: 'HTTP',
    );

    // Log to network logger with sanitized data
    AppLogger.network(
      response.requestOptions.method,
      response.requestOptions.uri.toString(),
      statusCode: response.statusCode,
      duration: duration,
      data: {
        if (duration != null) 'duration_ms': duration.inMilliseconds,
      },
    );

    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final startTime = err.requestOptions.extra['request_start_time'] as DateTime?;
    final duration = startTime != null
        ? DateTime.now().difference(startTime)
        : null;

    AppLogger.d(
      '┌─── Error ──────────────────────────────────────────────',
      tag: 'HTTP',
    );
    AppLogger.d(
      '│ ${err.requestOptions.method} ${err.requestOptions.uri}',
      tag: 'HTTP',
    );
    AppLogger.d('│ Error: ${err.type}', tag: 'HTTP');

    if (err.response != null) {
      AppLogger.d(
        '│ Status: ${err.response!.statusCode} ${err.response!.statusMessage ?? ""}',
        tag: 'HTTP',
      );
    }

    if (duration != null) {
      AppLogger.d('│ Duration: ${duration.inMilliseconds}ms', tag: 'HTTP');
    }

    // Log sanitized error message
    final sanitizedMessage = PiiFilter.sanitizeError(err.message ?? 'Unknown error');
    AppLogger.d('│ Message: $sanitizedMessage', tag: 'HTTP');

    // Log sanitized error response body
    if (logErrorBody && err.response?.data != null) {
      final sanitizedBody = PiiFilter.sanitizeResponseBody(err.response!.data);
      final bodyStr = _formatBody(sanitizedBody);
      AppLogger.d('│ Response: $bodyStr', tag: 'HTTP');
    }

    AppLogger.d(
      '└────────────────────────────────────────────────────────',
      tag: 'HTTP',
    );

    // Log to network logger with sanitized data
    AppLogger.network(
      err.requestOptions.method,
      err.requestOptions.uri.toString(),
      statusCode: err.response?.statusCode ?? 0,
      duration: duration,
      data: {
        'error_type': err.type.toString(),
        'error_message': PiiFilter.sanitize(err.message ?? 'Unknown'),
        if (duration != null) 'duration_ms': duration.inMilliseconds,
      },
    );

    handler.next(err);
  }

  /// Format body for logging with length limit
  String _formatBody(dynamic body) {
    if (body == null) return 'null';

    String bodyStr;
    if (body is String) {
      bodyStr = body;
    } else if (body is Map || body is List) {
      bodyStr = body.toString();
    } else {
      bodyStr = body.toString();
    }

    // Truncate if too long
    if (bodyStr.length > maxBodyLength) {
      return '${bodyStr.substring(0, maxBodyLength)}... (truncated)';
    }

    return bodyStr;
  }
}

/// Extension for easy Dio configuration with secure logging
extension DioSecureLogging on Dio {
  /// Add secure logging interceptor with PII protection
  void addSecureLogging({
    bool logRequestHeaders = true,
    bool logRequestBody = true,
    bool logResponseHeaders = false,
    bool logResponseBody = false,
    bool logErrorBody = true,
  }) {
    interceptors.add(LoggingInterceptor(
      logRequestHeaders: logRequestHeaders,
      logRequestBody: logRequestBody,
      logResponseHeaders: logResponseHeaders,
      logResponseBody: logResponseBody,
      logErrorBody: logErrorBody,
    ));
  }
}
