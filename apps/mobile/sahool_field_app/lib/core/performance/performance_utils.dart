import 'dart:async';
import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';
import 'package:flutter/scheduler.dart';
import '../utils/app_logger.dart';

/// SAHOOL Performance Utilities
/// أدوات مراقبة الأداء
///
/// Features:
/// - Frame rate monitoring
/// - Performance metrics tracking
/// - Performance logging
/// - Frame drops detection

/// PerformanceMonitor - مراقب الأداء
///
/// Monitors app performance including FPS, frame drops, and frame build times
class PerformanceMonitor {
  static PerformanceMonitor? _instance;
  static PerformanceMonitor get instance {
    _instance ??= PerformanceMonitor._();
    return _instance!;
  }

  PerformanceMonitor._();

  // Performance metrics
  final List<double> _frameTimes = [];
  final List<FrameMetrics> _recentFrames = [];
  int _totalFrames = 0;
  int _droppedFrames = 0;
  DateTime? _monitoringStartTime;
  bool _isMonitoring = false;

  // Configuration
  static const int maxFrameHistory = 120; // Keep last 2 seconds at 60fps
  static const Duration targetFrameDuration = Duration(milliseconds: 16); // ~60fps
  static const double jankThreshold = 16.0; // ms - frame is janky if > 16ms

  /// Start monitoring performance
  void startMonitoring() {
    if (_isMonitoring) return;

    _isMonitoring = true;
    _monitoringStartTime = DateTime.now();
    _totalFrames = 0;
    _droppedFrames = 0;
    _frameTimes.clear();
    _recentFrames.clear();

    // Register frame callback
    SchedulerBinding.instance.addTimingsCallback(_onFrameTiming);

    AppLogger.i('Performance monitoring started', tag: 'PERFORMANCE');
  }

  /// Stop monitoring performance
  void stopMonitoring() {
    if (!_isMonitoring) return;

    _isMonitoring = false;
    SchedulerBinding.instance.removeTimingsCallback(_onFrameTiming);

    AppLogger.i('Performance monitoring stopped', tag: 'PERFORMANCE');
  }

  /// Frame timing callback
  void _onFrameTiming(List<ui.FrameTiming> timings) {
    if (!_isMonitoring) return;

    for (final timing in timings) {
      _totalFrames++;

      // Calculate frame duration
      final buildDuration = timing.buildDuration.inMicroseconds / 1000.0; // ms
      final rasterDuration = timing.rasterDuration.inMicroseconds / 1000.0; // ms
      final totalDuration = timing.totalSpan.inMicroseconds / 1000.0; // ms

      // Add to frame times
      _frameTimes.add(totalDuration);
      if (_frameTimes.length > maxFrameHistory) {
        _frameTimes.removeAt(0);
      }

      // Track frame metrics
      final metrics = FrameMetrics(
        buildDuration: buildDuration,
        rasterDuration: rasterDuration,
        totalDuration: totalDuration,
        timestamp: DateTime.now(),
      );

      _recentFrames.add(metrics);
      if (_recentFrames.length > maxFrameHistory) {
        _recentFrames.removeAt(0);
      }

      // Detect dropped frames (janky frames)
      if (totalDuration > jankThreshold) {
        _droppedFrames++;

        if (kDebugMode) {
          AppLogger.w(
            'Janky frame detected: ${totalDuration.toStringAsFixed(2)}ms '
            '(build: ${buildDuration.toStringAsFixed(2)}ms, '
            'raster: ${rasterDuration.toStringAsFixed(2)}ms)',
            tag: 'PERFORMANCE',
          );
        }
      }
    }
  }

  /// Get current FPS (frames per second)
  double getCurrentFps() {
    if (_frameTimes.isEmpty) return 0.0;

    final avgFrameTime = _frameTimes.reduce((a, b) => a + b) / _frameTimes.length;
    if (avgFrameTime == 0) return 0.0;

    return 1000.0 / avgFrameTime; // Convert ms to fps
  }

  /// Get average FPS over monitoring period
  double getAverageFps() {
    if (_monitoringStartTime == null || _totalFrames == 0) return 0.0;

    final duration = DateTime.now().difference(_monitoringStartTime!);
    if (duration.inMilliseconds == 0) return 0.0;

    return _totalFrames / (duration.inMilliseconds / 1000.0);
  }

  /// Get performance summary
  PerformanceSummary getSummary() {
    final currentFps = getCurrentFps();
    final avgFps = getAverageFps();
    final dropRate = _totalFrames > 0 ? (_droppedFrames / _totalFrames) * 100 : 0.0;

    double avgBuildTime = 0.0;
    double avgRasterTime = 0.0;
    double avgTotalTime = 0.0;

    if (_recentFrames.isNotEmpty) {
      avgBuildTime = _recentFrames
              .map((f) => f.buildDuration)
              .reduce((a, b) => a + b) /
          _recentFrames.length;

      avgRasterTime = _recentFrames
              .map((f) => f.rasterDuration)
              .reduce((a, b) => a + b) /
          _recentFrames.length;

      avgTotalTime = _recentFrames
              .map((f) => f.totalDuration)
              .reduce((a, b) => a + b) /
          _recentFrames.length;
    }

    return PerformanceSummary(
      currentFps: currentFps,
      averageFps: avgFps,
      totalFrames: _totalFrames,
      droppedFrames: _droppedFrames,
      dropRate: dropRate,
      avgBuildTime: avgBuildTime,
      avgRasterTime: avgRasterTime,
      avgTotalTime: avgTotalTime,
      monitoringDuration: _monitoringStartTime != null
          ? DateTime.now().difference(_monitoringStartTime!)
          : Duration.zero,
    );
  }

  /// Log current performance metrics
  void logMetrics() {
    final summary = getSummary();
    AppLogger.i(summary.toString(), tag: 'PERFORMANCE');
  }

  /// Reset metrics
  void reset() {
    _frameTimes.clear();
    _recentFrames.clear();
    _totalFrames = 0;
    _droppedFrames = 0;
    _monitoringStartTime = _isMonitoring ? DateTime.now() : null;
  }

  /// Check if monitoring is active
  bool get isMonitoring => _isMonitoring;
}

/// Frame metrics data class
class FrameMetrics {
  final double buildDuration;
  final double rasterDuration;
  final double totalDuration;
  final DateTime timestamp;

  const FrameMetrics({
    required this.buildDuration,
    required this.rasterDuration,
    required this.totalDuration,
    required this.timestamp,
  });

  bool get isJanky => totalDuration > PerformanceMonitor.jankThreshold;

  @override
  String toString() =>
      'FrameMetrics(build: ${buildDuration.toStringAsFixed(2)}ms, '
      'raster: ${rasterDuration.toStringAsFixed(2)}ms, '
      'total: ${totalDuration.toStringAsFixed(2)}ms)';
}

/// Performance summary
class PerformanceSummary {
  final double currentFps;
  final double averageFps;
  final int totalFrames;
  final int droppedFrames;
  final double dropRate;
  final double avgBuildTime;
  final double avgRasterTime;
  final double avgTotalTime;
  final Duration monitoringDuration;

  const PerformanceSummary({
    required this.currentFps,
    required this.averageFps,
    required this.totalFrames,
    required this.droppedFrames,
    required this.dropRate,
    required this.avgBuildTime,
    required this.avgRasterTime,
    required this.avgTotalTime,
    required this.monitoringDuration,
  });

  bool get isHealthy => dropRate < 5.0 && currentFps > 50.0;

  PerformanceLevel get performanceLevel {
    if (currentFps >= 55.0 && dropRate < 2.0) {
      return PerformanceLevel.excellent;
    } else if (currentFps >= 45.0 && dropRate < 5.0) {
      return PerformanceLevel.good;
    } else if (currentFps >= 30.0 && dropRate < 10.0) {
      return PerformanceLevel.fair;
    } else {
      return PerformanceLevel.poor;
    }
  }

  @override
  String toString() => '''
Performance Summary:
  Current FPS: ${currentFps.toStringAsFixed(1)}
  Average FPS: ${averageFps.toStringAsFixed(1)}
  Total Frames: $totalFrames
  Dropped Frames: $droppedFrames (${dropRate.toStringAsFixed(2)}%)
  Avg Build Time: ${avgBuildTime.toStringAsFixed(2)}ms
  Avg Raster Time: ${avgRasterTime.toStringAsFixed(2)}ms
  Avg Total Time: ${avgTotalTime.toStringAsFixed(2)}ms
  Monitoring Duration: ${monitoringDuration.inSeconds}s
  Performance Level: ${performanceLevel.name}''';
}

/// Performance level
enum PerformanceLevel {
  excellent,
  good,
  fair,
  poor,
}

/// Helper Functions

/// Measure execution time of a function
Future<T> measurePerformance<T>(
  String operation,
  Future<T> Function() function, {
  bool logResult = true,
}) async {
  final stopwatch = Stopwatch()..start();

  try {
    final result = await function();
    stopwatch.stop();

    if (logResult) {
      AppLogger.d(
        '$operation completed in ${stopwatch.elapsedMilliseconds}ms',
        tag: 'PERFORMANCE',
      );
    }

    return result;
  } catch (e) {
    stopwatch.stop();
    AppLogger.e(
      '$operation failed after ${stopwatch.elapsedMilliseconds}ms',
      tag: 'PERFORMANCE',
      error: e,
    );
    rethrow;
  }
}

/// Measure synchronous execution time
T measurePerformanceSync<T>(
  String operation,
  T Function() function, {
  bool logResult = true,
}) {
  final stopwatch = Stopwatch()..start();

  try {
    final result = function();
    stopwatch.stop();

    if (logResult) {
      AppLogger.d(
        '$operation completed in ${stopwatch.elapsedMilliseconds}ms',
        tag: 'PERFORMANCE',
      );
    }

    return result;
  } catch (e) {
    stopwatch.stop();
    AppLogger.e(
      '$operation failed after ${stopwatch.elapsedMilliseconds}ms',
      tag: 'PERFORMANCE',
      error: e,
    );
    rethrow;
  }
}

/// Debounce function calls
class Debouncer {
  final Duration duration;
  Timer? _timer;

  Debouncer({this.duration = const Duration(milliseconds: 300)});

  void run(VoidCallback action) {
    _timer?.cancel();
    _timer = Timer(duration, action);
  }

  void cancel() {
    _timer?.cancel();
  }

  void dispose() {
    _timer?.cancel();
    _timer = null;
  }
}

/// Throttle function calls
class Throttler {
  final Duration duration;
  DateTime? _lastCallTime;

  Throttler({this.duration = const Duration(milliseconds: 300)});

  void run(VoidCallback action) {
    final now = DateTime.now();

    if (_lastCallTime == null ||
        now.difference(_lastCallTime!) >= duration) {
      _lastCallTime = now;
      action();
    }
  }

  void reset() {
    _lastCallTime = null;
  }
}

/// Performance logging helper
void logPerformanceMetric(String metric, dynamic value) {
  if (kDebugMode) {
    AppLogger.d('$metric: $value', tag: 'PERFORMANCE');
  }
}

/// Widget build time tracker
class BuildTimeTracker {
  static final Map<String, List<int>> _buildTimes = {};

  static void recordBuildTime(String widgetName, int milliseconds) {
    _buildTimes.putIfAbsent(widgetName, () => []);
    _buildTimes[widgetName]!.add(milliseconds);

    // Keep only last 100 builds
    if (_buildTimes[widgetName]!.length > 100) {
      _buildTimes[widgetName]!.removeAt(0);
    }
  }

  static double getAverageBuildTime(String widgetName) {
    final times = _buildTimes[widgetName];
    if (times == null || times.isEmpty) return 0.0;

    return times.reduce((a, b) => a + b) / times.length;
  }

  static void logBuildTimes() {
    if (_buildTimes.isEmpty) {
      AppLogger.i('No build times recorded', tag: 'PERFORMANCE');
      return;
    }

    final buffer = StringBuffer('Widget Build Times:\n');
    _buildTimes.forEach((widget, times) {
      final avg = times.reduce((a, b) => a + b) / times.length;
      buffer.writeln('  $widget: ${avg.toStringAsFixed(2)}ms avg');
    });

    AppLogger.i(buffer.toString(), tag: 'PERFORMANCE');
  }

  static void clear() {
    _buildTimes.clear();
  }
}
