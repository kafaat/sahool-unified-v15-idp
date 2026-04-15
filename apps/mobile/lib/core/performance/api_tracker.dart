import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../utils/app_logger.dart';
import 'metrics_collector.dart';
import 'performance_monitor.dart';

/// SAHOOL API Performance Tracker
/// متتبع أداء طلبات API
///
/// Features:
/// - Request/response timing measurement
/// - Response size tracking
/// - Error rate monitoring
/// - Slow request detection
/// - Retry tracking
/// - Per-endpoint statistics
///
/// Add to Dio interceptors to automatically track API performance.
///
/// Usage:
/// ```dart
/// final dio = Dio();
/// dio.interceptors.add(ApiPerformanceInterceptor(
///   metricsCollector: metricsCollector,
///   slowThresholdMs: 2000,
/// ));
/// ```

class ApiPerformanceInterceptor extends Interceptor {
  final MetricsCollector? metricsCollector;
  final int slowThresholdMs;
  final bool logSlowRequests;
  final bool trackRetries;

  /// Enable/disable tracking (useful for testing)
  bool enabled;

  /// Request start times (keyed by request hashcode)
  final Map<int, DateTime> _requestStartTimes = {};

  /// Retry counts per request
  final Map<int, int> _retryCounts = {};

  ApiPerformanceInterceptor({
    this.metricsCollector,
    this.slowThresholdMs = 2000,
    this.logSlowRequests = true,
    this.trackRetries = true,
    this.enabled = true,
  });

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (!enabled || kReleaseMode) {
      handler.next(options);
      return;
    }

    // Record start time
    final requestId = options.hashCode;
    _requestStartTimes[requestId] = DateTime.now();

    // Store start time in extras for access in response/error
    options.extra['perf_start_time'] = DateTime.now().millisecondsSinceEpoch;
    options.extra['perf_request_id'] = requestId;

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (!enabled || kReleaseMode) {
      handler.next(response);
      return;
    }

    _trackResponse(response.requestOptions, response.statusCode, response.data);
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (!enabled || kReleaseMode) {
      handler.next(err);
      return;
    }

    // Track retry if this is a retry attempt
    if (trackRetries) {
      final requestId = err.requestOptions.extra['perf_request_id'] as int?;
      if (requestId != null) {
        _retryCounts[requestId] = (_retryCounts[requestId] ?? 0) + 1;
      }
    }

    _trackResponse(
      err.requestOptions,
      err.response?.statusCode ?? 0,
      null,
      error: err,
    );

    handler.next(err);
  }

  void _trackResponse(
    RequestOptions options,
    int? statusCode,
    dynamic responseData, {
    DioException? error,
  }) {
    final startTimeMs = options.extra['perf_start_time'] as int?;
    if (startTimeMs == null) return;

    final duration = Duration(
      milliseconds: DateTime.now().millisecondsSinceEpoch - startTimeMs,
    );

    // Calculate response size
    int? responseSize;
    if (responseData != null) {
      try {
        if (responseData is String) {
          responseSize = responseData.length;
        } else if (responseData is List<int>) {
          responseSize = responseData.length;
        }
      } catch (e) {
        // Ignore size calculation errors
      }
    }

    // Get endpoint name (strip query params and IDs for grouping)
    final endpoint = _normalizeEndpoint(options.path);
    final method = options.method;

    // Record metric
    final collector = metricsCollector ?? PerformanceMonitor.instance.metricsCollector;
    collector.recordApiResponse(
      endpoint: endpoint,
      method: method,
      statusCode: statusCode ?? 0,
      duration: duration,
      responseSize: responseSize,
    );

    // Log slow requests
    if (logSlowRequests && duration.inMilliseconds > slowThresholdMs) {
      AppLogger.w(
        'Slow API request: $method $endpoint',
        tag: 'PERF',
        data: {
          'duration_ms': duration.inMilliseconds,
          'status_code': statusCode,
          'threshold_ms': slowThresholdMs,
          if (responseSize != null) 'response_size': responseSize,
          if (error != null) 'error': error.type.toString(),
        },
      );
    }

    // Cleanup
    final requestId = options.extra['perf_request_id'] as int?;
    if (requestId != null) {
      _requestStartTimes.remove(requestId);
      _retryCounts.remove(requestId);
    }
  }

  /// Normalize endpoint path for consistent grouping
  /// Replaces UUIDs and numeric IDs with placeholders
  String _normalizeEndpoint(String path) {
    // Remove query string
    final pathOnly = path.split('?').first;

    // Replace UUIDs with {id}
    var normalized = pathOnly.replaceAllMapped(
      RegExp(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'),
      (m) => '{id}',
    );

    // Replace numeric IDs in path segments with {id}
    normalized = normalized.replaceAllMapped(
      RegExp(r'/\d+(/|$)'),
      (m) => '/{id}${m.group(1)}',
    );

    return normalized;
  }

  /// Get current statistics
  ApiPerformanceStats getStats() {
    return ApiPerformanceStats(
      pendingRequests: _requestStartTimes.length,
      retryStats: Map.from(_retryCounts),
    );
  }

  /// Clear tracking state
  void clear() {
    _requestStartTimes.clear();
    _retryCounts.clear();
  }
}

/// API performance statistics
class ApiPerformanceStats {
  final int pendingRequests;
  final Map<int, int> retryStats;

  const ApiPerformanceStats({
    required this.pendingRequests,
    required this.retryStats,
  });

  int get totalRetries => retryStats.values.fold(0, (a, b) => a + b);
}

// ═══════════════════════════════════════════════════════════════════════════
// API Response Time Tracking Widget
// ═══════════════════════════════════════════════════════════════════════════

/// Callback type for API timing events
typedef ApiTimingCallback = void Function(ApiTimingEvent event);

/// API timing event data
class ApiTimingEvent {
  final String method;
  final String endpoint;
  final int statusCode;
  final Duration duration;
  final int? responseSize;
  final bool isError;
  final DateTime timestamp;

  ApiTimingEvent({
    required this.method,
    required this.endpoint,
    required this.statusCode,
    required this.duration,
    this.responseSize,
    required this.isError,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  bool get isSlow => duration.inMilliseconds > 1000;

  @override
  String toString() =>
      '$method $endpoint: ${duration.inMilliseconds}ms ($statusCode)';
}

/// Real-time API timing tracker with callback support
class ApiTimingTracker extends ApiPerformanceInterceptor {
  final List<ApiTimingCallback> _listeners = [];
  final List<ApiTimingEvent> _recentEvents = [];
  static const int _maxRecentEvents = 100;

  ApiTimingTracker({
    super.metricsCollector,
    super.slowThresholdMs = 2000,
  });

  /// Add listener for timing events
  void addListener(ApiTimingCallback callback) {
    _listeners.add(callback);
  }

  /// Remove listener
  void removeListener(ApiTimingCallback callback) {
    _listeners.remove(callback);
  }

  /// Get recent events
  List<ApiTimingEvent> get recentEvents => List.unmodifiable(_recentEvents);

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (enabled && !kReleaseMode) {
      _emitEvent(response.requestOptions, response.statusCode, response.data);
    }
    super.onResponse(response, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (enabled && !kReleaseMode) {
      _emitEvent(err.requestOptions, err.response?.statusCode ?? 0, null, isError: true);
    }
    super.onError(err, handler);
  }

  void _emitEvent(
    RequestOptions options,
    int? statusCode,
    dynamic responseData, {
    bool isError = false,
  }) {
    final startTimeMs = options.extra['perf_start_time'] as int?;
    if (startTimeMs == null) return;

    final duration = Duration(
      milliseconds: DateTime.now().millisecondsSinceEpoch - startTimeMs,
    );

    int? responseSize;
    if (responseData is String) {
      responseSize = responseData.length;
    } else if (responseData is List<int>) {
      responseSize = responseData.length;
    }

    final event = ApiTimingEvent(
      method: options.method,
      endpoint: options.path,
      statusCode: statusCode ?? 0,
      duration: duration,
      responseSize: responseSize,
      isError: isError,
    );

    // Add to recent events
    _recentEvents.add(event);
    if (_recentEvents.length > _maxRecentEvents) {
      _recentEvents.removeAt(0);
    }

    // Notify listeners
    for (final listener in _listeners) {
      try {
        listener(event);
      } catch (e) {
        AppLogger.e('Error in API timing listener', tag: 'PERF', error: e);
      }
    }
  }

  /// Get statistics for recent events
  ApiRecentStats getRecentStats() {
    if (_recentEvents.isEmpty) {
      return const ApiRecentStats(
        totalRequests: 0,
        errorCount: 0,
        slowCount: 0,
        averageDurationMs: 0,
        p95DurationMs: 0,
      );
    }

    final durations = _recentEvents.map((e) => e.duration.inMilliseconds).toList()..sort();
    final errorCount = _recentEvents.where((e) => e.isError).length;
    final slowCount = _recentEvents.where((e) => e.isSlow).length;
    final avgDuration = durations.fold<int>(0, (a, b) => a + b) / durations.length;

    final p95Index = (0.95 * durations.length).round().clamp(0, durations.length - 1);
    final p95Duration = durations[p95Index];

    return ApiRecentStats(
      totalRequests: _recentEvents.length,
      errorCount: errorCount,
      slowCount: slowCount,
      averageDurationMs: avgDuration.round(),
      p95DurationMs: p95Duration,
    );
  }

  @override
  void clear() {
    super.clear();
    _recentEvents.clear();
  }

  /// Dispose and clear listeners
  void dispose() {
    _listeners.clear();
    _recentEvents.clear();
    clear();
  }
}

/// Recent API statistics
class ApiRecentStats {
  final int totalRequests;
  final int errorCount;
  final int slowCount;
  final int averageDurationMs;
  final int p95DurationMs;

  const ApiRecentStats({
    required this.totalRequests,
    required this.errorCount,
    required this.slowCount,
    required this.averageDurationMs,
    required this.p95DurationMs,
  });

  double get errorRate => totalRequests > 0 ? errorCount / totalRequests : 0;
  double get slowRate => totalRequests > 0 ? slowCount / totalRequests : 0;

  @override
  String toString() =>
      'ApiRecentStats(requests: $totalRequests, errors: $errorCount, '
      'slow: $slowCount, avg: ${averageDurationMs}ms, p95: ${p95DurationMs}ms)';
}

// ═══════════════════════════════════════════════════════════════════════════
// Dio Extension for Easy Integration
// ═══════════════════════════════════════════════════════════════════════════

extension DioPerformanceTracking on Dio {
  /// Add performance tracking interceptor
  ApiPerformanceInterceptor addPerformanceTracking({
    MetricsCollector? metricsCollector,
    int slowThresholdMs = 2000,
    bool logSlowRequests = true,
  }) {
    final interceptor = ApiPerformanceInterceptor(
      metricsCollector: metricsCollector,
      slowThresholdMs: slowThresholdMs,
      logSlowRequests: logSlowRequests,
    );

    // Insert at beginning to capture accurate timing
    interceptors.insert(0, interceptor);

    return interceptor;
  }

  /// Add real-time timing tracker with event callbacks
  ApiTimingTracker addTimingTracker({
    MetricsCollector? metricsCollector,
    int slowThresholdMs = 2000,
    ApiTimingCallback? onTiming,
  }) {
    final tracker = ApiTimingTracker(
      metricsCollector: metricsCollector,
      slowThresholdMs: slowThresholdMs,
    );

    if (onTiming != null) {
      tracker.addListener(onTiming);
    }

    // Insert at beginning to capture accurate timing
    interceptors.insert(0, tracker);

    return tracker;
  }
}
