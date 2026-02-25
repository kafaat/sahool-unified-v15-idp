import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import '../utils/app_logger.dart';

/// Performance Monitor for tracking app performance metrics
/// Tracks screen load times, API call durations, and memory usage
///
/// مراقب الأداء لتتبع مقاييس أداء التطبيق
class PerformanceMonitor {
  static final PerformanceMonitor _instance = PerformanceMonitor._internal();
  factory PerformanceMonitor() => _instance;
  PerformanceMonitor._internal();

  final Map<String, DateTime> _startTimes = {};
  final Map<String, List<Duration>> _metrics = {};
  final int _maxMetricsPerKey = 100;

  /// Start tracking a performance metric
  void start(String key) {
    _startTimes[key] = DateTime.now();
  }

  /// End tracking and log the duration
  void end(String key, {Map<String, dynamic>? metadata}) {
    final startTime = _startTimes[key];
    if (startTime == null) {
      if (kDebugMode) {
        AppLogger.w('Performance tracking end called without start for: $key');
      }
      return;
    }

    final duration = DateTime.now().difference(startTime);
    _recordMetric(key, duration);

    if (kDebugMode) {
      final metaInfo = metadata != null ? ' | Meta: $metadata' : '';
      AppLogger.i(
        'Performance: $key took ${duration.inMilliseconds}ms$metaInfo',
        tag: 'Performance',
      );
    }

    // Warn if operation took too long
    if (duration.inMilliseconds > 3000) {
      AppLogger.w(
        'Slow operation detected: $key took ${duration.inMilliseconds}ms',
        tag: 'Performance',
      );
    }

    _startTimes.remove(key);
  }

  /// Record a metric duration
  void _recordMetric(String key, Duration duration) {
    _metrics.putIfAbsent(key, () => []);
    _metrics[key]!.add(duration);

    // Keep only last N metrics to prevent memory bloat
    if (_metrics[key]!.length > _maxMetricsPerKey) {
      _metrics[key]!.removeAt(0);
    }
  }

  /// Track screen load time
  void trackScreenLoad(String screenName, VoidCallback onComplete) {
    start('screen_load_$screenName');
    WidgetsBinding.instance.addPostFrameCallback((_) {
      end('screen_load_$screenName', metadata: {'screen': screenName});
      onComplete();
    });
  }

  /// Track API call duration
  Future<T> trackApiCall<T>(
    String endpoint,
    Future<T> Function() apiCall,
  ) async {
    final key = 'api_$endpoint';
    start(key);

    try {
      final result = await apiCall();
      end(key, metadata: {'endpoint': endpoint, 'status': 'success'});
      return result;
    } catch (e) {
      end(key, metadata: {
        'endpoint': endpoint,
        'status': 'error',
        'error': e.toString()
      });
      rethrow;
    }
  }

  /// Get average duration for a metric
  Duration? getAverageDuration(String key) {
    final metrics = _metrics[key];
    if (metrics == null || metrics.isEmpty) return null;

    final totalMs = metrics.fold<int>(
      0,
      (sum, duration) => sum + duration.inMilliseconds,
    );

    return Duration(milliseconds: totalMs ~/ metrics.length);
  }

  /// Get performance summary
  Map<String, dynamic> getSummary() {
    final summary = <String, dynamic>{};

    for (final entry in _metrics.entries) {
      final key = entry.key;
      final metrics = entry.value;

      if (metrics.isEmpty) continue;

      final durations = metrics.map((d) => d.inMilliseconds).toList();
      durations.sort();

      summary[key] = {
        'count': metrics.length,
        'avg_ms': durations.reduce((a, b) => a + b) ~/ durations.length,
        'min_ms': durations.first,
        'max_ms': durations.last,
        'p50_ms': durations[durations.length ~/ 2],
        'p95_ms': durations[(durations.length * 0.95).toInt()],
      };
    }

    return summary;
  }

  /// Log performance summary
  void logSummary() {
    if (!kDebugMode) return;

    final summary = getSummary();
    if (summary.isEmpty) {
      AppLogger.i('No performance metrics recorded', tag: 'Performance');
      return;
    }

    AppLogger.i('=== Performance Summary ===', tag: 'Performance');
    for (final entry in summary.entries) {
      final stats = entry.value as Map<String, dynamic>;
      AppLogger.i(
        '${entry.key}: avg=${stats['avg_ms']}ms, '
        'min=${stats['min_ms']}ms, max=${stats['max_ms']}ms, '
        'p95=${stats['p95_ms']}ms (n=${stats['count']})',
        tag: 'Performance',
      );
    }
  }

  /// Clear all metrics
  void clear() {
    _startTimes.clear();
    _metrics.clear();
  }

  /// Clear metrics for a specific key
  void clearKey(String key) {
    _startTimes.remove(key);
    _metrics.remove(key);
  }
}

/// Mixin for widgets to easily track performance
mixin PerformanceTrackingMixin {
  final _performanceMonitor = PerformanceMonitor();

  void startPerformanceTracking(String key) {
    _performanceMonitor.start(key);
  }

  void endPerformanceTracking(String key, {Map<String, dynamic>? metadata}) {
    _performanceMonitor.end(key, metadata: metadata);
  }

  Future<T> trackApiCall<T>(String endpoint, Future<T> Function() apiCall) {
    return _performanceMonitor.trackApiCall(endpoint, apiCall);
  }
}

/// Extension on BuildContext for easy screen tracking
extension PerformanceTrackingContext on BuildContext {
  void trackScreenLoad(String screenName) {
    PerformanceMonitor().trackScreenLoad(screenName, () {});
  }
}
