import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// SAHOOL Performance Metrics Collector
/// جامع مقاييس الأداء
///
/// Features:
/// - Local storage of performance metrics
/// - Batch aggregation for efficiency
/// - Automatic sync when online
/// - Configurable retention period
/// - Metric categorization by type
///
/// Stores metrics locally and syncs to backend when online.
/// Only active in debug/profile mode.

/// Types of metrics collected
enum MetricType {
  appStartup,
  frameRate,
  apiResponse,
  database,
  screenTransition,
  imageLoad,
  memory,
  operation,
}

/// Single metric entry
class MetricEntry {
  final MetricType type;
  final String name;
  final double value;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  MetricEntry({
    required this.type,
    required this.name,
    required this.value,
    DateTime? timestamp,
    this.metadata,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() => {
        'type': type.name,
        'name': name,
        'value': value,
        'timestamp': timestamp.toIso8601String(),
        if (metadata != null) 'metadata': metadata,
      };

  factory MetricEntry.fromJson(Map<String, dynamic> json) => MetricEntry(
        type: MetricType.values.firstWhere(
          (t) => t.name == json['type'],
          orElse: () => MetricType.operation,
        ),
        name: json['name'] as String,
        value: (json['value'] as num).toDouble(),
        timestamp: DateTime.parse(json['timestamp'] as String),
        metadata: json['metadata'] as Map<String, dynamic>?,
      );
}

/// Aggregated metric statistics
class MetricStats {
  final MetricType type;
  final String name;
  final int count;
  final double min;
  final double max;
  final double sum;
  final double average;
  final double p50;
  final double p95;
  final double p99;

  MetricStats({
    required this.type,
    required this.name,
    required this.count,
    required this.min,
    required this.max,
    required this.sum,
    required this.average,
    required this.p50,
    required this.p95,
    required this.p99,
  });

  Map<String, dynamic> toJson() => {
        'type': type.name,
        'name': name,
        'count': count,
        'min': min,
        'max': max,
        'sum': sum,
        'average': average,
        'p50': p50,
        'p95': p95,
        'p99': p99,
      };

  @override
  String toString() =>
      'MetricStats($name: count=$count, avg=${average.toStringAsFixed(2)}, '
      'p95=${p95.toStringAsFixed(2)}, p99=${p99.toStringAsFixed(2)})';
}

/// Metrics Collector for local storage and aggregation
class MetricsCollector {
  static const String _storageKey = 'sahool_perf_metrics';
  static const String _lastSyncKey = 'sahool_perf_last_sync';
  static const int _maxStoredEntries = 5000;
  static const int _batchSize = 100;
  static const Duration _retentionPeriod = Duration(days: 7);
  static const Duration _minSyncInterval = Duration(minutes: 15);

  late SharedPreferences _prefs;
  bool _initialized = false;

  /// In-memory buffer for pending metrics
  final List<MetricEntry> _buffer = [];

  /// Aggregated stats by metric name
  final Map<String, List<double>> _aggregationBuffer = {};

  /// Timer for periodic flush
  Timer? _flushTimer;

  /// Callback for when metrics are ready to sync
  Future<bool> Function(List<MetricEntry> metrics)? onSyncReady;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the metrics collector
  Future<void> initialize() async {
    if (_initialized) return;

    _prefs = await SharedPreferences.getInstance();
    _initialized = true;

    // Start periodic flush timer (every 30 seconds in debug, 5 minutes in profile)
    const flushInterval = kDebugMode
        ? Duration(seconds: 30)
        : Duration(minutes: 5);

    _flushTimer = Timer.periodic(flushInterval, (_) => flush());

    // Load any pending metrics from storage
    await _loadFromStorage();

    // Cleanup old entries
    await _cleanupOldEntries();

    AppLogger.d(
      'MetricsCollector initialized',
      tag: 'PERF',
      data: {'pending_entries': _buffer.length},
    );
  }

  /// Load pending metrics from storage
  Future<void> _loadFromStorage() async {
    try {
      final jsonStr = _prefs.getString(_storageKey);
      if (jsonStr == null || jsonStr.isEmpty) return;

      final List<dynamic> jsonList = json.decode(jsonStr) as List<dynamic>;
      for (final item in jsonList) {
        try {
          _buffer.add(MetricEntry.fromJson(item as Map<String, dynamic>));
        } catch (e) {
          // Skip invalid entries
        }
      }
    } catch (e) {
      AppLogger.e('Failed to load metrics from storage', tag: 'PERF', error: e);
    }
  }

  /// Save pending metrics to storage
  Future<void> _saveToStorage() async {
    if (!_initialized) return;

    try {
      // Limit stored entries
      final entriesToStore = _buffer.length > _maxStoredEntries
          ? _buffer.sublist(_buffer.length - _maxStoredEntries)
          : _buffer;

      final jsonStr = json.encode(entriesToStore.map((e) => e.toJson()).toList());
      await _prefs.setString(_storageKey, jsonStr);
    } catch (e) {
      AppLogger.e('Failed to save metrics to storage', tag: 'PERF', error: e);
    }
  }

  /// Cleanup entries older than retention period
  Future<void> _cleanupOldEntries() async {
    final cutoff = DateTime.now().subtract(_retentionPeriod);
    final initialCount = _buffer.length;

    _buffer.removeWhere((e) => e.timestamp.isBefore(cutoff));

    if (_buffer.length < initialCount) {
      AppLogger.d(
        'Cleaned up old metrics',
        tag: 'PERF',
        data: {'removed': initialCount - _buffer.length},
      );
      await _saveToStorage();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Recording Metrics
  // ═══════════════════════════════════════════════════════════════════════════

  /// Record a single metric
  void recordMetric(
    MetricType type,
    String name,
    double value, {
    Map<String, dynamic>? metadata,
  }) {
    if (!_initialized) return;

    final entry = MetricEntry(
      type: type,
      name: name,
      value: value,
      metadata: metadata,
    );

    _buffer.add(entry);

    // Add to aggregation buffer
    final key = '${type.name}:$name';
    _aggregationBuffer.putIfAbsent(key, () => []);
    _aggregationBuffer[key]!.add(value);

    // Keep aggregation buffer limited
    if (_aggregationBuffer[key]!.length > 1000) {
      _aggregationBuffer[key]!.removeRange(0, 500);
    }
  }

  /// Record API response time
  void recordApiResponse({
    required String endpoint,
    required String method,
    required int statusCode,
    required Duration duration,
    int? responseSize,
  }) {
    recordMetric(
      MetricType.apiResponse,
      '$method $endpoint',
      duration.inMilliseconds.toDouble(),
      metadata: {
        'status_code': statusCode,
        'method': method,
        'endpoint': endpoint,
        if (responseSize != null) 'response_size': responseSize,
      },
    );
  }

  /// Record database query time
  void recordDatabaseQuery({
    required String queryName,
    required Duration duration,
    int? rowCount,
  }) {
    recordMetric(
      MetricType.database,
      queryName,
      duration.inMilliseconds.toDouble(),
      metadata: {
        if (rowCount != null) 'row_count': rowCount,
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Statistics & Aggregation
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get statistics for a specific metric
  MetricStats? getStats(MetricType type, String name) {
    final key = '${type.name}:$name';
    final values = _aggregationBuffer[key];

    if (values == null || values.isEmpty) return null;

    return _calculateStats(type, name, values);
  }

  /// Get all statistics for a metric type
  Map<String, MetricStats> getStatsByType(MetricType type) {
    final stats = <String, MetricStats>{};

    for (final entry in _aggregationBuffer.entries) {
      if (entry.key.startsWith('${type.name}:')) {
        final name = entry.key.substring(type.name.length + 1);
        final stat = _calculateStats(type, name, entry.value);
        if (stat != null) {
          stats[name] = stat;
        }
      }
    }

    return stats;
  }

  /// Get all API response statistics
  Map<String, MetricStats> getApiStats() => getStatsByType(MetricType.apiResponse);

  /// Get all database query statistics
  Map<String, MetricStats> getDatabaseStats() => getStatsByType(MetricType.database);

  /// Calculate statistics from values
  MetricStats? _calculateStats(MetricType type, String name, List<double> values) {
    if (values.isEmpty) return null;

    final sorted = List<double>.from(values)..sort();
    final count = sorted.length;
    final sum = sorted.fold<double>(0, (a, b) => a + b);

    return MetricStats(
      type: type,
      name: name,
      count: count,
      min: sorted.first,
      max: sorted.last,
      sum: sum,
      average: sum / count,
      p50: _percentile(sorted, 50),
      p95: _percentile(sorted, 95),
      p99: _percentile(sorted, 99),
    );
  }

  double _percentile(List<double> sorted, int percentile) {
    if (sorted.isEmpty) return 0;
    if (sorted.length == 1) return sorted.first;

    final index = (percentile / 100 * (sorted.length - 1)).round();
    return sorted[index.clamp(0, sorted.length - 1)];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync & Persistence
  // ═══════════════════════════════════════════════════════════════════════════

  /// Flush pending metrics to storage
  Future<void> flush() async {
    if (!_initialized || _buffer.isEmpty) return;

    await _saveToStorage();

    AppLogger.d(
      'Metrics flushed to storage',
      tag: 'PERF',
      data: {'count': _buffer.length},
    );
  }

  /// Attempt to sync metrics to backend
  Future<bool> syncToBackend() async {
    if (!_initialized || _buffer.isEmpty) return true;

    // Check if enough time has passed since last sync
    final lastSyncStr = _prefs.getString(_lastSyncKey);
    if (lastSyncStr != null) {
      final lastSync = DateTime.parse(lastSyncStr);
      if (DateTime.now().difference(lastSync) < _minSyncInterval) {
        return true; // Too soon to sync
      }
    }

    // Check if sync callback is configured
    if (onSyncReady == null) {
      AppLogger.d('No sync callback configured', tag: 'PERF');
      return false;
    }

    // Sync in batches
    var synced = 0;
    while (synced < _buffer.length) {
      final batch = _buffer.skip(synced).take(_batchSize).toList();
      if (batch.isEmpty) break;

      try {
        final success = await onSyncReady!(batch);
        if (!success) break;

        synced += batch.length;
      } catch (e) {
        AppLogger.e('Failed to sync metrics batch', tag: 'PERF', error: e);
        break;
      }
    }

    if (synced > 0) {
      // Remove synced entries
      _buffer.removeRange(0, synced);
      await _saveToStorage();

      // Update last sync time
      await _prefs.setString(_lastSyncKey, DateTime.now().toIso8601String());

      AppLogger.i('Metrics synced', tag: 'PERF', data: {'count': synced});
    }

    return synced == _buffer.length;
  }

  /// Get pending metrics count
  int get pendingCount => _buffer.length;

  /// Get last sync time
  DateTime? getLastSyncTime() {
    final str = _prefs.getString(_lastSyncKey);
    return str != null ? DateTime.parse(str) : null;
  }

  /// Export all metrics as JSON (for debugging)
  String exportAsJson() {
    return json.encode({
      'timestamp': DateTime.now().toIso8601String(),
      'metrics': _buffer.map((e) => e.toJson()).toList(),
      'stats': _aggregationBuffer.map((key, values) {
        final parts = key.split(':');
        final type = MetricType.values.firstWhere((t) => t.name == parts[0]);
        final name = parts.sublist(1).join(':');
        final stats = _calculateStats(type, name, values);
        return MapEntry(key, stats?.toJson());
      }),
    });
  }

  /// Clear all metrics (for testing)
  Future<void> clear() async {
    _buffer.clear();
    _aggregationBuffer.clear();
    await _prefs.remove(_storageKey);
    await _prefs.remove(_lastSyncKey);
  }

  /// Dispose resources
  void dispose() {
    _flushTimer?.cancel();
    _flushTimer = null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Convenience Extensions
// ═══════════════════════════════════════════════════════════════════════════

extension MetricTypeExtension on MetricType {
  String get displayName {
    switch (this) {
      case MetricType.appStartup:
        return 'App Startup';
      case MetricType.frameRate:
        return 'Frame Rate';
      case MetricType.apiResponse:
        return 'API Response';
      case MetricType.database:
        return 'Database';
      case MetricType.screenTransition:
        return 'Screen Transition';
      case MetricType.imageLoad:
        return 'Image Load';
      case MetricType.memory:
        return 'Memory';
      case MetricType.operation:
        return 'Operation';
    }
  }

  String get displayNameAr {
    switch (this) {
      case MetricType.appStartup:
        return 'بدء التشغيل';
      case MetricType.frameRate:
        return 'معدل الإطارات';
      case MetricType.apiResponse:
        return 'استجابة API';
      case MetricType.database:
        return 'قاعدة البيانات';
      case MetricType.screenTransition:
        return 'انتقال الشاشة';
      case MetricType.imageLoad:
        return 'تحميل الصور';
      case MetricType.memory:
        return 'الذاكرة';
      case MetricType.operation:
        return 'العملية';
    }
  }
}
