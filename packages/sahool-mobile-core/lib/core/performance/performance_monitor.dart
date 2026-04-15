import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter/widgets.dart';
import '../utils/app_logger.dart';
import 'memory_manager.dart';
import 'metrics_collector.dart';

/// SAHOOL Performance Monitor
/// مراقب الأداء للتطبيق
///
/// Features:
/// - App startup time tracking
/// - Frame rate monitoring (FPS)
/// - Widget build time tracking
/// - Memory usage monitoring
/// - Screen transition timing
/// - Database query timing
/// - Image loading time
///
/// Only detailed monitoring in debug/profile mode, minimal in release.
///
/// Usage:
/// ```dart
/// // Initialize at app start
/// await PerformanceMonitor.instance.initialize();
///
/// // Track startup
/// PerformanceMonitor.instance.markStartupComplete();
///
/// // Track custom operations
/// final stopwatch = PerformanceMonitor.instance.startOperation('load_fields');
/// // ... do work
/// PerformanceMonitor.instance.endOperation('load_fields', stopwatch);
/// ```

class PerformanceMonitor {
  static PerformanceMonitor? _instance;
  static PerformanceMonitor get instance {
    _instance ??= PerformanceMonitor._();
    return _instance!;
  }

  PerformanceMonitor._();

  /// Whether monitoring is enabled (disabled in release by default)
  bool _enabled = !kReleaseMode;
  bool get isEnabled => _enabled;

  /// Whether detailed frame monitoring is active
  bool _frameMonitoringActive = false;

  /// Metrics collector for persistence
  late final MetricsCollector _metricsCollector;

  /// App startup tracking
  DateTime? _appStartTime;
  DateTime? _firstFrameTime;
  DateTime? _startupCompleteTime;
  bool _startupTracked = false;

  /// Frame rate monitoring
  final List<Duration> _frameDurations = [];
  static const int _maxFrameSamples = 120; // 2 seconds at 60fps
  Timer? _fpsReportTimer;

  /// Current FPS (updated periodically)
  double _currentFps = 0;
  double get currentFps => _currentFps;

  /// Frame statistics
  int _droppedFrames = 0;
  int _totalFrames = 0;

  /// Active operations being tracked
  final Map<String, Stopwatch> _activeOperations = {};

  /// Screen transition tracking
  String? _currentScreen;
  DateTime? _screenTransitionStart;
  final Map<String, Duration> _screenTransitionTimes = {};

  /// Widget build tracking (only in debug/profile)
  final Map<String, List<Duration>> _widgetBuildTimes = {};
  static const int _maxBuildSamples = 50;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize performance monitoring
  Future<void> initialize({bool enabled = true}) async {
    // In release mode, only enable if explicitly requested
    _enabled = kReleaseMode ? false : enabled;

    if (!_enabled) {
      AppLogger.d('Performance monitoring disabled (release mode)', tag: 'PERF');
      return;
    }

    _appStartTime = DateTime.now();

    // Initialize metrics collector
    _metricsCollector = MetricsCollector();
    await _metricsCollector.initialize();

    // Start frame monitoring in debug/profile mode
    if (kDebugMode || kProfileMode) {
      _startFrameMonitoring();
    }

    AppLogger.i('Performance monitoring initialized', tag: 'PERF');
  }

  /// Mark when first frame is rendered
  void markFirstFrame() {
    if (!_enabled || _firstFrameTime != null) return;

    _firstFrameTime = DateTime.now();

    if (_appStartTime != null) {
      final timeToFirstFrame = _firstFrameTime!.difference(_appStartTime!);
      _metricsCollector.recordMetric(
        MetricType.appStartup,
        'time_to_first_frame',
        timeToFirstFrame.inMilliseconds.toDouble(),
      );

      AppLogger.i(
        'Time to first frame: ${timeToFirstFrame.inMilliseconds}ms',
        tag: 'PERF',
      );
    }
  }

  /// Mark when app startup is complete (home screen loaded)
  void markStartupComplete() {
    if (!_enabled || _startupTracked) return;

    _startupCompleteTime = DateTime.now();
    _startupTracked = true;

    if (_appStartTime != null) {
      final startupTime = _startupCompleteTime!.difference(_appStartTime!);
      _metricsCollector.recordMetric(
        MetricType.appStartup,
        'startup_complete',
        startupTime.inMilliseconds.toDouble(),
      );

      AppLogger.i(
        'App startup complete: ${startupTime.inMilliseconds}ms',
        tag: 'PERF',
      );

      // Log startup breakdown
      if (_firstFrameTime != null) {
        final postFirstFrame = _startupCompleteTime!.difference(_firstFrameTime!);
        AppLogger.d(
          'Post first-frame initialization: ${postFirstFrame.inMilliseconds}ms',
          tag: 'PERF',
        );
      }
    }
  }

  /// Get startup metrics
  StartupMetrics? getStartupMetrics() {
    if (_appStartTime == null) return null;

    return StartupMetrics(
      appStartTime: _appStartTime!,
      timeToFirstFrame: _firstFrameTime?.difference(_appStartTime!),
      timeToStartupComplete: _startupCompleteTime?.difference(_appStartTime!),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Frame Rate Monitoring
  // ═══════════════════════════════════════════════════════════════════════════

  void _startFrameMonitoring() {
    if (_frameMonitoringActive) return;
    _frameMonitoringActive = true;

    // Use SchedulerBinding to track frame timings
    SchedulerBinding.instance.addTimingsCallback(_onFrameTimings);

    // Report FPS every 2 seconds
    _fpsReportTimer = Timer.periodic(const Duration(seconds: 2), (_) {
      _calculateAndReportFps();
    });

    AppLogger.d('Frame monitoring started', tag: 'PERF');
  }

  void _stopFrameMonitoring() {
    if (!_frameMonitoringActive) return;
    _frameMonitoringActive = false;

    SchedulerBinding.instance.removeTimingsCallback(_onFrameTimings);
    _fpsReportTimer?.cancel();
    _fpsReportTimer = null;

    AppLogger.d('Frame monitoring stopped', tag: 'PERF');
  }

  void _onFrameTimings(List<FrameTiming> timings) {
    for (final timing in timings) {
      final duration = Duration(
        microseconds: timing.totalSpan.inMicroseconds,
      );

      _frameDurations.add(duration);
      _totalFrames++;

      // Check for dropped frames (>16.67ms for 60fps)
      if (duration.inMilliseconds > 16) {
        _droppedFrames++;
      }

      // Keep buffer size limited
      if (_frameDurations.length > _maxFrameSamples) {
        _frameDurations.removeAt(0);
      }
    }
  }

  void _calculateAndReportFps() {
    if (_frameDurations.isEmpty) return;

    // Calculate average frame duration
    final totalMicros = _frameDurations.fold<int>(
      0,
      (sum, d) => sum + d.inMicroseconds,
    );
    final avgMicros = totalMicros / _frameDurations.length;
    _currentFps = 1000000 / avgMicros; // Convert to FPS

    // Record metric
    _metricsCollector.recordMetric(
      MetricType.frameRate,
      'fps',
      _currentFps,
    );

    // Log if FPS drops below threshold
    if (_currentFps < 55 && kDebugMode) {
      AppLogger.w(
        'Low FPS detected: ${_currentFps.toStringAsFixed(1)}',
        tag: 'PERF',
        data: {
          'dropped_frames': _droppedFrames,
          'total_frames': _totalFrames,
        },
      );
    }
  }

  /// Get current frame rate statistics
  FrameRateStats getFrameRateStats() {
    if (_frameDurations.isEmpty) {
      return const FrameRateStats(
        currentFps: 60,
        averageFrameTime: Duration(milliseconds: 16),
        droppedFrames: 0,
        totalFrames: 0,
      );
    }

    final totalMicros = _frameDurations.fold<int>(
      0,
      (sum, d) => sum + d.inMicroseconds,
    );

    return FrameRateStats(
      currentFps: _currentFps,
      averageFrameTime: Duration(microseconds: totalMicros ~/ _frameDurations.length),
      droppedFrames: _droppedFrames,
      totalFrames: _totalFrames,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Operation Tracking
  // ═══════════════════════════════════════════════════════════════════════════

  /// Start tracking an operation
  Stopwatch startOperation(String operationName) {
    final stopwatch = Stopwatch()..start();
    _activeOperations[operationName] = stopwatch;
    return stopwatch;
  }

  /// End tracking an operation
  Duration endOperation(String operationName, [Stopwatch? stopwatch]) {
    final sw = stopwatch ?? _activeOperations.remove(operationName);
    if (sw == null) {
      AppLogger.w('No active operation found: $operationName', tag: 'PERF');
      return Duration.zero;
    }

    sw.stop();
    final duration = sw.elapsed;

    if (_enabled) {
      _metricsCollector.recordMetric(
        MetricType.operation,
        operationName,
        duration.inMilliseconds.toDouble(),
      );

      // Log slow operations
      if (duration.inMilliseconds > 100) {
        AppLogger.performance(operationName, duration);
      }
    }

    _activeOperations.remove(operationName);
    return duration;
  }

  /// Track a database query
  Future<T> trackDatabaseQuery<T>(
    String queryName,
    Future<T> Function() query,
  ) async {
    if (!_enabled) return query();

    final stopwatch = startOperation('db_$queryName');
    try {
      final result = await query();
      final duration = endOperation('db_$queryName', stopwatch);

      _metricsCollector.recordMetric(
        MetricType.database,
        queryName,
        duration.inMilliseconds.toDouble(),
      );

      return result;
    } catch (e) {
      endOperation('db_$queryName', stopwatch);
      rethrow;
    }
  }

  /// Track an image load operation
  void trackImageLoad(String imageName, Duration duration) {
    if (!_enabled) return;

    _metricsCollector.recordMetric(
      MetricType.imageLoad,
      imageName,
      duration.inMilliseconds.toDouble(),
    );

    if (duration.inMilliseconds > 500) {
      AppLogger.w(
        'Slow image load: $imageName (${duration.inMilliseconds}ms)',
        tag: 'PERF',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Screen Transition Tracking
  // ═══════════════════════════════════════════════════════════════════════════

  /// Mark the start of a screen transition
  void startScreenTransition(String toScreen) {
    if (!_enabled) return;

    _screenTransitionStart = DateTime.now();
    _currentScreen = toScreen;
  }

  /// Mark the end of a screen transition
  void endScreenTransition(String screenName) {
    if (!_enabled || _screenTransitionStart == null) return;

    final duration = DateTime.now().difference(_screenTransitionStart!);
    _screenTransitionTimes[screenName] = duration;

    _metricsCollector.recordMetric(
      MetricType.screenTransition,
      screenName,
      duration.inMilliseconds.toDouble(),
    );

    if (duration.inMilliseconds > 300) {
      AppLogger.w(
        'Slow screen transition to $screenName: ${duration.inMilliseconds}ms',
        tag: 'PERF',
      );
    }

    _screenTransitionStart = null;
  }

  /// Get screen transition times
  Map<String, Duration> getScreenTransitionTimes() => Map.from(_screenTransitionTimes);

  // ═══════════════════════════════════════════════════════════════════════════
  // Widget Build Tracking (Debug/Profile only)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Track widget build time
  void trackWidgetBuild(String widgetName, Duration duration) {
    if (!_enabled || kReleaseMode) return;

    _widgetBuildTimes.putIfAbsent(widgetName, () => []);
    final times = _widgetBuildTimes[widgetName]!;

    times.add(duration);
    if (times.length > _maxBuildSamples) {
      times.removeAt(0);
    }

    // Warn about slow builds
    if (duration.inMilliseconds > 16) {
      AppLogger.w(
        'Slow widget build: $widgetName (${duration.inMilliseconds}ms)',
        tag: 'PERF',
      );
    }
  }

  /// Get widget build statistics
  Map<String, WidgetBuildStats> getWidgetBuildStats() {
    final stats = <String, WidgetBuildStats>{};

    for (final entry in _widgetBuildTimes.entries) {
      final times = entry.value;
      if (times.isEmpty) continue;

      final totalMicros = times.fold<int>(0, (s, d) => s + d.inMicroseconds);
      final avgMicros = totalMicros ~/ times.length;
      final maxMicros = times.map((d) => d.inMicroseconds).reduce((a, b) => a > b ? a : b);

      stats[entry.key] = WidgetBuildStats(
        buildCount: times.length,
        averageBuildTime: Duration(microseconds: avgMicros),
        maxBuildTime: Duration(microseconds: maxMicros),
      );
    }

    return stats;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Memory Monitoring
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get current memory info (integrates with MemoryManager)
  MemoryInfo getMemoryInfo() {
    return MemoryManager.instance.getMemoryInfo();
  }

  /// Record memory snapshot
  void recordMemorySnapshot() {
    if (!_enabled) return;

    final memInfo = getMemoryInfo();
    _metricsCollector.recordMetric(
      MetricType.memory,
      'image_cache_bytes',
      memInfo.imageCacheBytes.toDouble(),
    );
    _metricsCollector.recordMetric(
      MetricType.memory,
      'image_cache_count',
      memInfo.imageCacheCount.toDouble(),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Summary & Reporting
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get overall performance summary
  PerformanceSummary getSummary() {
    return PerformanceSummary(
      startupMetrics: getStartupMetrics(),
      frameRateStats: getFrameRateStats(),
      memoryInfo: getMemoryInfo(),
      screenTransitions: Map.from(_screenTransitionTimes),
      widgetBuildStats: getWidgetBuildStats(),
    );
  }

  /// Get metrics collector for persistence operations
  MetricsCollector get metricsCollector => _metricsCollector;

  /// Flush all pending metrics to storage
  Future<void> flush() async {
    if (!_enabled) return;
    await _metricsCollector.flush();
  }

  /// Enable or disable monitoring
  void setEnabled(bool enabled) {
    // Never enable in release mode
    if (kReleaseMode) return;

    _enabled = enabled;

    if (enabled && !_frameMonitoringActive) {
      _startFrameMonitoring();
    } else if (!enabled && _frameMonitoringActive) {
      _stopFrameMonitoring();
    }
  }

  /// Cleanup resources
  void dispose() {
    _stopFrameMonitoring();
    _activeOperations.clear();
    _frameDurations.clear();
    _widgetBuildTimes.clear();
    _screenTransitionTimes.clear();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Data Classes
// ═══════════════════════════════════════════════════════════════════════════

/// Startup timing metrics
class StartupMetrics {
  final DateTime appStartTime;
  final Duration? timeToFirstFrame;
  final Duration? timeToStartupComplete;

  const StartupMetrics({
    required this.appStartTime,
    this.timeToFirstFrame,
    this.timeToStartupComplete,
  });

  @override
  String toString() =>
      'StartupMetrics(firstFrame: ${timeToFirstFrame?.inMilliseconds}ms, '
      'complete: ${timeToStartupComplete?.inMilliseconds}ms)';
}

/// Frame rate statistics
class FrameRateStats {
  final double currentFps;
  final Duration averageFrameTime;
  final int droppedFrames;
  final int totalFrames;

  const FrameRateStats({
    required this.currentFps,
    required this.averageFrameTime,
    required this.droppedFrames,
    required this.totalFrames,
  });

  double get droppedFrameRatio =>
      totalFrames > 0 ? droppedFrames / totalFrames : 0;

  @override
  String toString() =>
      'FrameRateStats(fps: ${currentFps.toStringAsFixed(1)}, '
      'dropped: $droppedFrames/$totalFrames)';
}

/// Widget build time statistics
class WidgetBuildStats {
  final int buildCount;
  final Duration averageBuildTime;
  final Duration maxBuildTime;

  const WidgetBuildStats({
    required this.buildCount,
    required this.averageBuildTime,
    required this.maxBuildTime,
  });

  @override
  String toString() =>
      'WidgetBuildStats(count: $buildCount, '
      'avg: ${averageBuildTime.inMicroseconds}us, '
      'max: ${maxBuildTime.inMicroseconds}us)';
}

/// Overall performance summary
class PerformanceSummary {
  final StartupMetrics? startupMetrics;
  final FrameRateStats frameRateStats;
  final MemoryInfo memoryInfo;
  final Map<String, Duration> screenTransitions;
  final Map<String, WidgetBuildStats> widgetBuildStats;

  const PerformanceSummary({
    this.startupMetrics,
    required this.frameRateStats,
    required this.memoryInfo,
    required this.screenTransitions,
    required this.widgetBuildStats,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Mixins
// ═══════════════════════════════════════════════════════════════════════════

/// Mixin for tracking widget build times
mixin PerformanceTrackedWidget<T extends StatefulWidget> on State<T> {
  Stopwatch? _buildStopwatch;

  @override
  Widget build(BuildContext context) {
    // Only track in debug/profile mode
    if (kReleaseMode) {
      return buildTracked(context);
    }

    _buildStopwatch = Stopwatch()..start();
    final widget = buildTracked(context);
    _buildStopwatch!.stop();

    PerformanceMonitor.instance.trackWidgetBuild(
      runtimeType.toString(),
      _buildStopwatch!.elapsed,
    );

    return widget;
  }

  /// Override this instead of build() when using the mixin
  Widget buildTracked(BuildContext context);
}

/// Navigation observer for screen transition tracking
class PerformanceNavigatorObserver extends NavigatorObserver {
  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    final name = route.settings.name;
    if (name != null) {
      PerformanceMonitor.instance.startScreenTransition(name);
    }
  }

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    // Could track pop transitions if needed
  }
}

/// Route-aware widget for screen transition completion
mixin PerformanceRouteAware<T extends StatefulWidget> on State<T>
    implements RouteAware {
  @override
  void didPopNext() {}

  @override
  void didPush() {
    // Mark screen transition complete when screen is pushed
    final routeName = ModalRoute.of(context)?.settings.name;
    if (routeName != null) {
      PerformanceMonitor.instance.endScreenTransition(routeName);
    }
  }

  @override
  void didPushNext() {}

  @override
  void didPop() {}
}
