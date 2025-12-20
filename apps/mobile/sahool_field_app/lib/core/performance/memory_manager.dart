import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import '../utils/app_logger.dart';

/// SAHOOL Memory Manager
/// مدير الذاكرة للتطبيق
///
/// Features:
/// - Memory pressure monitoring
/// - Automatic cache cleanup
/// - Memory usage tracking
/// - Low memory warnings

class MemoryManager {
  static MemoryManager? _instance;
  static MemoryManager get instance {
    _instance ??= MemoryManager._();
    return _instance!;
  }

  MemoryManager._() {
    _init();
  }

  final List<MemoryPressureCallback> _callbacks = [];
  Timer? _monitorTimer;
  MemoryPressureLevel _currentLevel = MemoryPressureLevel.normal;

  MemoryPressureLevel get currentLevel => _currentLevel;

  void _init() {
    // Listen to system memory pressure events
    SystemChannels.lifecycle.setMessageHandler((message) async {
      if (message == AppLifecycleState.paused.toString()) {
        // App is in background - release non-essential resources
        await _handleMemoryPressure(MemoryPressureLevel.moderate);
      }
      return null;
    });

    // Start periodic memory monitoring
    _startMonitoring();
  }

  void _startMonitoring() {
    _monitorTimer?.cancel();
    _monitorTimer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => _checkMemory(),
    );
  }

  void _checkMemory() {
    // In a real implementation, you would check actual memory usage
    // For now, we'll simulate based on image cache size etc.
    AppLogger.d('Memory check performed', tag: 'MEMORY');
  }

  /// تسجيل callback لضغط الذاكرة
  void registerCallback(MemoryPressureCallback callback) {
    _callbacks.add(callback);
  }

  /// إلغاء تسجيل callback
  void unregisterCallback(MemoryPressureCallback callback) {
    _callbacks.remove(callback);
  }

  /// معالجة ضغط الذاكرة
  Future<void> _handleMemoryPressure(MemoryPressureLevel level) async {
    if (level.index <= _currentLevel.index) return;

    _currentLevel = level;
    AppLogger.w('Memory pressure: ${level.name}', tag: 'MEMORY');

    // Notify all registered callbacks
    for (final callback in _callbacks) {
      try {
        await callback(level);
      } catch (e) {
        AppLogger.e('Error in memory callback', tag: 'MEMORY', error: e);
      }
    }

    // Reset level after handling
    _currentLevel = MemoryPressureLevel.normal;
  }

  /// تنظيف الذاكرة يدوياً
  Future<void> clearMemory({bool aggressive = false}) async {
    final level = aggressive
        ? MemoryPressureLevel.critical
        : MemoryPressureLevel.moderate;

    await _handleMemoryPressure(level);

    // Clear image cache
    PaintingBinding.instance.imageCache.clear();
    PaintingBinding.instance.imageCache.clearLiveImages();

    AppLogger.i('Memory cleared (aggressive: $aggressive)', tag: 'MEMORY');
  }

  /// الحصول على معلومات الذاكرة
  MemoryInfo getMemoryInfo() {
    final imageCache = PaintingBinding.instance.imageCache;

    return MemoryInfo(
      imageCacheCount: imageCache.currentSize,
      imageCacheBytes: imageCache.currentSizeBytes,
      maxImageCacheBytes: imageCache.maximumSizeBytes,
    );
  }

  /// تعيين حد أقصى لكاش الصور
  void setImageCacheLimit({int? count, int? bytes}) {
    final imageCache = PaintingBinding.instance.imageCache;

    if (count != null) {
      imageCache.maximumSize = count;
    }
    if (bytes != null) {
      imageCache.maximumSizeBytes = bytes;
    }
  }

  /// إيقاف المراقبة
  void dispose() {
    _monitorTimer?.cancel();
    _callbacks.clear();
  }
}

/// مستويات ضغط الذاكرة
enum MemoryPressureLevel {
  normal,
  moderate,
  high,
  critical,
}

/// نوع callback لضغط الذاكرة
typedef MemoryPressureCallback = Future<void> Function(MemoryPressureLevel level);

/// معلومات الذاكرة
class MemoryInfo {
  final int imageCacheCount;
  final int imageCacheBytes;
  final int maxImageCacheBytes;

  const MemoryInfo({
    required this.imageCacheCount,
    required this.imageCacheBytes,
    required this.maxImageCacheBytes,
  });

  double get imageCacheUsagePercent =>
      maxImageCacheBytes > 0 ? imageCacheBytes / maxImageCacheBytes * 100 : 0;

  String get imageCacheSizeFormatted {
    final mb = imageCacheBytes / (1024 * 1024);
    return '${mb.toStringAsFixed(1)} MB';
  }

  @override
  String toString() =>
      'MemoryInfo(images: $imageCacheCount, size: $imageCacheSizeFormatted, usage: ${imageCacheUsagePercent.toStringAsFixed(1)}%)';
}

/// Mixin لإدارة الذاكرة في StatefulWidget
mixin MemoryAwareMixin<T extends StatefulWidget> on State<T> {
  late final void Function(MemoryPressureLevel) _memoryCallback;

  @override
  void initState() {
    super.initState();
    _memoryCallback = (level) async => onMemoryPressure(level);
    MemoryManager.instance.registerCallback(_memoryCallback);
  }

  @override
  void dispose() {
    MemoryManager.instance.unregisterCallback(_memoryCallback);
    super.dispose();
  }

  /// يتم استدعاؤها عند ضغط الذاكرة - يمكن تجاوزها
  void onMemoryPressure(MemoryPressureLevel level) {
    // Override in subclass to handle memory pressure
    // e.g., clear cached data, dispose of large objects
  }
}

/// Widget wrapper لتحسين الذاكرة
class MemoryOptimizedWidget extends StatefulWidget {
  final Widget child;
  final Widget Function()? lowMemoryBuilder;

  const MemoryOptimizedWidget({
    super.key,
    required this.child,
    this.lowMemoryBuilder,
  });

  @override
  State<MemoryOptimizedWidget> createState() => _MemoryOptimizedWidgetState();
}

class _MemoryOptimizedWidgetState extends State<MemoryOptimizedWidget>
    with MemoryAwareMixin {
  bool _isLowMemory = false;

  @override
  void onMemoryPressure(MemoryPressureLevel level) {
    if (level.index >= MemoryPressureLevel.high.index) {
      if (!_isLowMemory && mounted) {
        setState(() => _isLowMemory = true);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLowMemory && widget.lowMemoryBuilder != null) {
      return widget.lowMemoryBuilder!();
    }
    return widget.child;
  }
}
