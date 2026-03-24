/// SAHOOL Performance Utilities
/// أدوات تحسين الأداء
///
/// Features:
/// - Image caching and optimization
/// - Lazy loading widgets
/// - Deferred initialization
/// - Memory management utilities
/// - Widget caching
library;

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

// =============================================================================
// Lazy Loading Widget - مكون التحميل الكسول
// =============================================================================

/// Widget that only builds its child when visible on screen
/// مكون يبني محتواه فقط عندما يكون مرئياً على الشاشة
class LazyLoadWidget extends StatefulWidget {
  final Widget child;
  final Widget? placeholder;
  final Duration delay;
  final bool preloadWhenNearby;
  final double preloadDistance;

  const LazyLoadWidget({
    super.key,
    required this.child,
    this.placeholder,
    this.delay = Duration.zero,
    this.preloadWhenNearby = true,
    this.preloadDistance = 200,
  });

  @override
  State<LazyLoadWidget> createState() => _LazyLoadWidgetState();
}

class _LazyLoadWidgetState extends State<LazyLoadWidget> {
  bool _isLoaded = false;
  bool _isVisible = false;

  @override
  void initState() {
    super.initState();
    if (widget.delay == Duration.zero) {
      _scheduleLoad();
    } else {
      Future.delayed(widget.delay, _scheduleLoad);
    }
  }

  void _scheduleLoad() {
    SchedulerBinding.instance.addPostFrameCallback((_) {
      if (mounted && _isVisible) {
        setState(() => _isLoaded = true);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return VisibilityDetector(
      onVisibilityChanged: (visible) {
        _isVisible = visible;
        if (visible && !_isLoaded) {
          setState(() => _isLoaded = true);
        }
      },
      child: _isLoaded
          ? widget.child
          : widget.placeholder ?? const _DefaultPlaceholder(),
    );
  }
}

class _DefaultPlaceholder extends StatelessWidget {
  const _DefaultPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 100,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(8),
      ),
    );
  }
}

// =============================================================================
// Visibility Detector - كاشف الرؤية
// =============================================================================

/// Detects when widget becomes visible in viewport
/// يكتشف عندما يصبح المكون مرئياً في نطاق العرض
class VisibilityDetector extends StatefulWidget {
  final Widget child;
  final void Function(bool isVisible) onVisibilityChanged;

  const VisibilityDetector({
    super.key,
    required this.child,
    required this.onVisibilityChanged,
  });

  @override
  State<VisibilityDetector> createState() => _VisibilityDetectorState();
}

class _VisibilityDetectorState extends State<VisibilityDetector> {
  final GlobalKey _key = GlobalKey();
  bool _wasVisible = false;

  @override
  void initState() {
    super.initState();
    SchedulerBinding.instance.addPostFrameCallback((_) => _checkVisibility());
  }

  void _checkVisibility() {
    if (!mounted) return;

    final RenderBox? renderBox =
        _key.currentContext?.findRenderObject() as RenderBox?;
    if (renderBox == null) return;

    final size = renderBox.size;
    final offset = renderBox.localToGlobal(Offset.zero);

    final screenSize = MediaQuery.of(context).size;

    final isVisible = offset.dy < screenSize.height &&
        offset.dy + size.height > 0 &&
        offset.dx < screenSize.width &&
        offset.dx + size.width > 0;

    if (isVisible != _wasVisible) {
      _wasVisible = isVisible;
      widget.onVisibilityChanged(isVisible);
    }

    // Schedule next check
    SchedulerBinding.instance.addPostFrameCallback((_) => _checkVisibility());
  }

  @override
  Widget build(BuildContext context) {
    return KeyedSubtree(
      key: _key,
      child: widget.child,
    );
  }
}

// =============================================================================
// Deferred Builder - بناء مؤجل
// =============================================================================

/// Defers building of widget until next frame
/// يؤجل بناء المكون حتى الإطار التالي
class DeferredBuilder extends StatefulWidget {
  final WidgetBuilder builder;
  final Widget? placeholder;
  final int deferFrames;

  const DeferredBuilder({
    super.key,
    required this.builder,
    this.placeholder,
    this.deferFrames = 1,
  });

  @override
  State<DeferredBuilder> createState() => _DeferredBuilderState();
}

class _DeferredBuilderState extends State<DeferredBuilder> {
  int _frameCount = 0;
  bool _isBuilt = false;

  @override
  void initState() {
    super.initState();
    _deferBuild();
  }

  void _deferBuild() {
    if (_frameCount >= widget.deferFrames) {
      if (mounted) {
        setState(() => _isBuilt = true);
      }
      return;
    }

    _frameCount++;
    SchedulerBinding.instance.addPostFrameCallback((_) => _deferBuild());
  }

  @override
  Widget build(BuildContext context) {
    if (!_isBuilt) {
      return widget.placeholder ?? const SizedBox.shrink();
    }
    return widget.builder(context);
  }
}

// =============================================================================
// Cached Widget - مكون مخزن مؤقتاً
// =============================================================================

/// Caches widget to prevent unnecessary rebuilds
/// يخزن المكون مؤقتاً لمنع إعادة البناء غير الضرورية
class CachedWidget extends StatefulWidget {
  final Widget child;
  final Object cacheKey;

  const CachedWidget({
    super.key,
    required this.child,
    required this.cacheKey,
  });

  @override
  State<CachedWidget> createState() => _CachedWidgetState();
}

class _CachedWidgetState extends State<CachedWidget> {
  Widget? _cachedChild;
  Object? _lastCacheKey;

  @override
  Widget build(BuildContext context) {
    if (_lastCacheKey != widget.cacheKey) {
      _cachedChild = widget.child;
      _lastCacheKey = widget.cacheKey;
    }
    return _cachedChild ?? widget.child;
  }
}

// =============================================================================
// Frame Rate Monitor - مراقب معدل الإطارات
// =============================================================================

/// Monitor and report frame rate
/// مراقبة والإبلاغ عن معدل الإطارات
class FrameRateMonitor {
  static FrameRateMonitor? _instance;
  static FrameRateMonitor get instance {
    _instance ??= FrameRateMonitor._();
    return _instance!;
  }

  FrameRateMonitor._();

  final List<Duration> _frameTimes = [];
  final _frameRateController = StreamController<double>.broadcast();
  Stream<double> get frameRate => _frameRateController.stream;

  DateTime? _lastFrameTime;
  bool _isMonitoring = false;

  /// Start monitoring frame rate
  void start() {
    if (_isMonitoring) return;
    _isMonitoring = true;
    SchedulerBinding.instance.addPersistentFrameCallback(_onFrame);
  }

  /// Stop monitoring
  void stop() {
    _isMonitoring = false;
    _frameTimes.clear();
  }

  void _onFrame(Duration timestamp) {
    if (!_isMonitoring) return;

    final now = DateTime.now();
    if (_lastFrameTime != null) {
      final frameDuration = now.difference(_lastFrameTime!);
      _frameTimes.add(frameDuration);

      // Keep only last 60 frames
      if (_frameTimes.length > 60) {
        _frameTimes.removeAt(0);
      }

      // Calculate FPS
      if (_frameTimes.length >= 10) {
        final avgDuration = _frameTimes.fold<Duration>(
              Duration.zero,
              (sum, d) => sum + d,
            ).inMicroseconds /
            _frameTimes.length;
        final fps = 1000000 / avgDuration;
        _frameRateController.add(fps);
      }
    }
    _lastFrameTime = now;
  }

  /// Get current average FPS
  double get currentFps {
    if (_frameTimes.isEmpty) return 60;
    final avgDuration = _frameTimes.fold<Duration>(
          Duration.zero,
          (sum, d) => sum + d,
        ).inMicroseconds /
        _frameTimes.length;
    return 1000000 / avgDuration;
  }

  /// Check if FPS is below threshold (indicating jank)
  bool isJanky({double threshold = 55}) {
    return currentFps < threshold;
  }

  void dispose() {
    stop();
    _frameRateController.close();
  }
}

// =============================================================================
// Memory Usage Tracker - متتبع استخدام الذاكرة
// =============================================================================

/// Track and report memory usage
/// تتبع والإبلاغ عن استخدام الذاكرة
class MemoryUsageTracker {
  static MemoryUsageTracker? _instance;
  static MemoryUsageTracker get instance {
    _instance ??= MemoryUsageTracker._();
    return _instance!;
  }

  MemoryUsageTracker._();

  /// Check current memory usage (debug mode only)
  Future<MemoryInfo> checkMemory() async {
    if (!kDebugMode) {
      return const MemoryInfo(
        usedHeapSize: 0,
        externalUsage: 0,
        heapCapacity: 0,
      );
    }

    // In a real app, you'd use dart:developer or platform channels
    // This is a placeholder implementation
    return const MemoryInfo(
      usedHeapSize: 0,
      externalUsage: 0,
      heapCapacity: 0,
    );
  }

  /// Suggest garbage collection (debug mode only)
  void suggestGC() {
    if (kDebugMode) {
      debugPrint('Memory: Suggesting garbage collection');
    }
  }
}

class MemoryInfo {
  final int usedHeapSize;
  final int externalUsage;
  final int heapCapacity;

  const MemoryInfo({
    required this.usedHeapSize,
    required this.externalUsage,
    required this.heapCapacity,
  });

  double get usagePercentage {
    if (heapCapacity == 0) return 0;
    return usedHeapSize / heapCapacity * 100;
  }
}

// =============================================================================
// Throttle & Debounce - التأخير والتقييد
// =============================================================================

/// Throttle function calls
/// تقييد استدعاءات الدوال
class Throttle {
  final Duration duration;
  Timer? _timer;
  bool _isThrottled = false;

  Throttle(this.duration);

  void call(VoidCallback callback) {
    if (_isThrottled) return;

    callback();
    _isThrottled = true;

    _timer?.cancel();
    _timer = Timer(duration, () {
      _isThrottled = false;
    });
  }

  void dispose() {
    _timer?.cancel();
  }
}

/// Debounce function calls
/// تأخير استدعاءات الدوال
class Debounce {
  final Duration duration;
  Timer? _timer;

  Debounce(this.duration);

  void call(VoidCallback callback) {
    _timer?.cancel();
    _timer = Timer(duration, callback);
  }

  void cancel() {
    _timer?.cancel();
  }

  void dispose() {
    _timer?.cancel();
  }
}

// =============================================================================
// Optimized Scrollable - قائمة تمرير محسّنة
// =============================================================================

/// Optimized list with item recycling
/// قائمة محسّنة مع إعادة تدوير العناصر
class OptimizedListView<T> extends StatelessWidget {
  final List<T> items;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final ScrollController? controller;
  final EdgeInsets? padding;
  final double? itemExtent;
  final Widget? separator;
  final bool shrinkWrap;

  const OptimizedListView({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.controller,
    this.padding,
    this.itemExtent,
    this.separator,
    this.shrinkWrap = false,
  });

  @override
  Widget build(BuildContext context) {
    if (itemExtent != null) {
      // Use ListView.builder with itemExtent for better performance
      return ListView.builder(
        controller: controller,
        padding: padding,
        itemExtent: itemExtent,
        shrinkWrap: shrinkWrap,
        itemCount: items.length,
        itemBuilder: (context, index) => itemBuilder(context, items[index], index),
      );
    }

    if (separator != null) {
      return ListView.separated(
        controller: controller,
        padding: padding,
        shrinkWrap: shrinkWrap,
        itemCount: items.length,
        separatorBuilder: (_, __) => separator!,
        itemBuilder: (context, index) => itemBuilder(context, items[index], index),
      );
    }

    return ListView.builder(
      controller: controller,
      padding: padding,
      shrinkWrap: shrinkWrap,
      itemCount: items.length,
      itemBuilder: (context, index) => itemBuilder(context, items[index], index),
    );
  }
}

// =============================================================================
// Repaint Boundary Wrapper - غلاف حدود إعادة الرسم
// =============================================================================

/// Wraps child in RepaintBoundary for performance optimization
/// يغلف المكون في حدود إعادة الرسم لتحسين الأداء
class IsolatedRepaint extends StatelessWidget {
  final Widget child;

  const IsolatedRepaint({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return RepaintBoundary(child: child);
  }
}

// =============================================================================
// Keep Alive Wrapper - غلاف البقاء حياً
// =============================================================================

/// Keeps widget alive when scrolled out of view
/// يبقي المكون حياً عند التمرير خارج العرض
class KeepAliveWrapper extends StatefulWidget {
  final Widget child;

  const KeepAliveWrapper({
    super.key,
    required this.child,
  });

  @override
  State<KeepAliveWrapper> createState() => _KeepAliveWrapperState();
}

class _KeepAliveWrapperState extends State<KeepAliveWrapper>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return widget.child;
  }
}

// =============================================================================
// Performance Observer - مراقب الأداء
// =============================================================================

/// Observes and logs performance metrics
/// يراقب ويسجل مقاييس الأداء
class PerformanceObserver {
  static final Map<String, Stopwatch> _timers = {};
  static final Map<String, List<int>> _measurements = {};

  /// Start measuring an operation
  static void startMeasurement(String operationName) {
    _timers[operationName] = Stopwatch()..start();
  }

  /// End measurement and record result
  static Duration endMeasurement(String operationName) {
    final timer = _timers.remove(operationName);
    if (timer == null) return Duration.zero;

    timer.stop();
    final duration = timer.elapsed;

    // Store measurement
    _measurements.putIfAbsent(operationName, () => []);
    _measurements[operationName]!.add(duration.inMilliseconds);

    // Keep only last 100 measurements
    if (_measurements[operationName]!.length > 100) {
      _measurements[operationName]!.removeAt(0);
    }

    if (kDebugMode) {
      debugPrint('Performance: $operationName took ${duration.inMilliseconds}ms');
    }

    return duration;
  }

  /// Get average duration for an operation
  static Duration getAverageDuration(String operationName) {
    final measurements = _measurements[operationName];
    if (measurements == null || measurements.isEmpty) return Duration.zero;

    final avgMs = measurements.reduce((a, b) => a + b) / measurements.length;
    return Duration(milliseconds: avgMs.round());
  }

  /// Measure a synchronous function
  static T measure<T>(String operationName, T Function() fn) {
    startMeasurement(operationName);
    try {
      return fn();
    } finally {
      endMeasurement(operationName);
    }
  }

  /// Measure an async function
  static Future<T> measureAsync<T>(
    String operationName,
    Future<T> Function() fn,
  ) async {
    startMeasurement(operationName);
    try {
      return await fn();
    } finally {
      endMeasurement(operationName);
    }
  }

  /// Clear all measurements
  static void clearMeasurements() {
    _timers.clear();
    _measurements.clear();
  }
}
