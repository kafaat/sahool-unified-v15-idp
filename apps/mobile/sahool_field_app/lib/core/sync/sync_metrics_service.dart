import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Sync Metrics Service - Tracks and persists sync performance metrics
/// خدمة قياس أداء المزامنة
class SyncMetricsService {
  static const String _prefsKeyPrefix = 'sync_metrics_';
  static const String _currentMetricsKey = '${_prefsKeyPrefix}current';
  static const String _dailyMetricsKey = '${_prefsKeyPrefix}daily';
  static const String _weeklyMetricsKey = '${_prefsKeyPrefix}weekly';

  final SharedPreferences _prefs;
  final _metricsController = StreamController<SyncMetrics>.broadcast();

  SyncMetrics _currentMetrics = SyncMetrics.initial();
  final Map<String, DailyMetrics> _dailyMetrics = {};
  final Map<String, WeeklyMetrics> _weeklyMetrics = {};

  SyncMetricsService(this._prefs) {
    _loadMetrics();
  }

  /// Stream of real-time metrics updates
  Stream<SyncMetrics> get metricsStream => _metricsController.stream;

  /// Get current metrics
  SyncMetrics get currentMetrics => _currentMetrics;

  /// Get daily metrics for a specific date
  DailyMetrics? getDailyMetrics(DateTime date) {
    final key = _formatDateKey(date);
    return _dailyMetrics[key];
  }

  /// Get weekly metrics for a specific week
  WeeklyMetrics? getWeeklyMetrics(DateTime weekStart) {
    final key = _formatWeekKey(weekStart);
    return _weeklyMetrics[key];
  }

  /// Get metrics for the last N days
  List<DailyMetrics> getLastNDays(int days) {
    final metrics = <DailyMetrics>[];
    final now = DateTime.now();

    for (int i = 0; i < days; i++) {
      final date = now.subtract(Duration(days: i));
      final dayMetrics = getDailyMetrics(date);
      if (dayMetrics != null) {
        metrics.add(dayMetrics);
      }
    }

    return metrics.reversed.toList();
  }

  /// Record a sync operation start
  String startSyncOperation({
    required SyncOperationType type,
    required String entityType,
    int? estimatedPayloadSize,
  }) {
    final operation = SyncOperation(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: type,
      entityType: entityType,
      startTime: DateTime.now(),
      estimatedPayloadSize: estimatedPayloadSize,
    );

    _currentMetrics = _currentMetrics.copyWith(
      activeOperations: {..._currentMetrics.activeOperations, operation.id: operation},
    );

    _metricsController.add(_currentMetrics);
    return operation.id;
  }

  /// Record a sync operation completion
  Future<void> completeSyncOperation({
    required String operationId,
    required bool success,
    int? actualPayloadSize,
    String? errorMessage,
    bool wasConflict = false,
    ConflictResolution? conflictResolution,
  }) async {
    final operation = _currentMetrics.activeOperations[operationId];
    if (operation == null) return;

    final endTime = DateTime.now();
    final duration = endTime.difference(operation.startTime);

    // Update current metrics
    _currentMetrics = _currentMetrics.copyWith(
      totalOperations: _currentMetrics.totalOperations + 1,
      successfulOperations: _currentMetrics.successfulOperations + (success ? 1 : 0),
      failedOperations: _currentMetrics.failedOperations + (success ? 0 : 1),
      totalDuration: _currentMetrics.totalDuration + duration.inMilliseconds,
      totalBandwidthBytes: _currentMetrics.totalBandwidthBytes + (actualPayloadSize ?? 0),
      conflictCount: _currentMetrics.conflictCount + (wasConflict ? 1 : 0),
      activeOperations: Map.from(_currentMetrics.activeOperations)..remove(operationId),
      lastSyncTime: endTime,
    );

    // Add to retry statistics if failed
    if (!success) {
      _currentMetrics = _currentMetrics.copyWith(
        retryStatistics: _currentMetrics.retryStatistics.copyWith(
          totalRetries: _currentMetrics.retryStatistics.totalRetries + 1,
        ),
      );
    }

    // Add to conflict resolutions if conflict occurred
    if (wasConflict && conflictResolution != null) {
      final resolutions = Map<ConflictResolution, int>.from(
        _currentMetrics.conflictResolutions,
      );
      resolutions[conflictResolution] = (resolutions[conflictResolution] ?? 0) + 1;
      _currentMetrics = _currentMetrics.copyWith(conflictResolutions: resolutions);
    }

    // Update operation history (keep last 100)
    final history = List<CompletedOperation>.from(_currentMetrics.operationHistory);
    history.add(CompletedOperation(
      type: operation.type,
      entityType: operation.entityType,
      startTime: operation.startTime,
      endTime: endTime,
      duration: duration,
      success: success,
      payloadSize: actualPayloadSize,
      errorMessage: errorMessage,
      wasConflict: wasConflict,
      conflictResolution: conflictResolution,
    ));

    if (history.length > 100) {
      history.removeAt(0);
    }

    _currentMetrics = _currentMetrics.copyWith(operationHistory: history);

    // Update queue depth history (keep last 1000 samples)
    final queueDepth = _currentMetrics.activeOperations.length;
    final queueHistory = List<QueueDepthSample>.from(_currentMetrics.queueDepthHistory);
    queueHistory.add(QueueDepthSample(
      timestamp: endTime,
      depth: queueDepth,
    ));

    if (queueHistory.length > 1000) {
      queueHistory.removeAt(0);
    }

    _currentMetrics = _currentMetrics.copyWith(queueDepthHistory: queueHistory);

    // Aggregate into daily metrics
    await _aggregateDailyMetrics(endTime, success, duration, actualPayloadSize);

    // Save and notify
    await _saveMetrics();
    _metricsController.add(_currentMetrics);
  }

  /// Record a retry attempt
  Future<void> recordRetry({
    required String operationId,
    required int attemptNumber,
    required Duration backoffDelay,
  }) async {
    _currentMetrics = _currentMetrics.copyWith(
      retryStatistics: _currentMetrics.retryStatistics.copyWith(
        totalRetries: _currentMetrics.retryStatistics.totalRetries + 1,
        retryAttemptsByCount: {
          ..._currentMetrics.retryStatistics.retryAttemptsByCount,
          attemptNumber: (_currentMetrics.retryStatistics.retryAttemptsByCount[attemptNumber] ?? 0) + 1,
        },
      ),
    );

    await _saveMetrics();
    _metricsController.add(_currentMetrics);
  }

  /// Update queue depth (call this periodically)
  Future<void> updateQueueDepth(int depth) async {
    final queueHistory = List<QueueDepthSample>.from(_currentMetrics.queueDepthHistory);
    queueHistory.add(QueueDepthSample(
      timestamp: DateTime.now(),
      depth: depth,
    ));

    if (queueHistory.length > 1000) {
      queueHistory.removeAt(0);
    }

    _currentMetrics = _currentMetrics.copyWith(queueDepthHistory: queueHistory);
    _metricsController.add(_currentMetrics);
  }

  /// Aggregate metrics into daily summary
  Future<void> _aggregateDailyMetrics(
    DateTime timestamp,
    bool success,
    Duration duration,
    int? payloadSize,
  ) async {
    final dateKey = _formatDateKey(timestamp);
    final existing = _dailyMetrics[dateKey] ?? DailyMetrics(date: timestamp);

    _dailyMetrics[dateKey] = existing.copyWith(
      totalOperations: existing.totalOperations + 1,
      successfulOperations: existing.successfulOperations + (success ? 1 : 0),
      failedOperations: existing.failedOperations + (success ? 0 : 1),
      totalDurationMs: existing.totalDurationMs + duration.inMilliseconds,
      totalBandwidthBytes: existing.totalBandwidthBytes + (payloadSize ?? 0),
    );

    // Aggregate into weekly metrics
    await _aggregateWeeklyMetrics(timestamp, success, duration, payloadSize);
  }

  /// Aggregate metrics into weekly summary
  Future<void> _aggregateWeeklyMetrics(
    DateTime timestamp,
    bool success,
    Duration duration,
    int? payloadSize,
  ) async {
    final weekStart = _getWeekStart(timestamp);
    final weekKey = _formatWeekKey(weekStart);
    final existing = _weeklyMetrics[weekKey] ?? WeeklyMetrics(weekStart: weekStart);

    _weeklyMetrics[weekKey] = existing.copyWith(
      totalOperations: existing.totalOperations + 1,
      successfulOperations: existing.successfulOperations + (success ? 1 : 0),
      failedOperations: existing.failedOperations + (success ? 0 : 1),
      totalDurationMs: existing.totalDurationMs + duration.inMilliseconds,
      totalBandwidthBytes: existing.totalBandwidthBytes + (payloadSize ?? 0),
    );
  }

  /// Reset all metrics (for testing or maintenance)
  Future<void> resetMetrics() async {
    _currentMetrics = SyncMetrics.initial();
    _dailyMetrics.clear();
    _weeklyMetrics.clear();
    await _saveMetrics();
    _metricsController.add(_currentMetrics);
  }

  /// Export metrics as JSON for debugging
  Map<String, dynamic> exportMetrics() {
    return {
      'current': _currentMetrics.toJson(),
      'daily': _dailyMetrics.map((key, value) => MapEntry(key, value.toJson())),
      'weekly': _weeklyMetrics.map((key, value) => MapEntry(key, value.toJson())),
      'exportedAt': DateTime.now().toIso8601String(),
    };
  }

  /// Export metrics as human-readable string
  String exportMetricsAsString() {
    final json = exportMetrics();
    return const JsonEncoder.withIndent('  ').convert(json);
  }

  /// Load metrics from SharedPreferences
  Future<void> _loadMetrics() async {
    try {
      // Load current metrics
      final currentJson = _prefs.getString(_currentMetricsKey);
      if (currentJson != null) {
        _currentMetrics = SyncMetrics.fromJson(jsonDecode(currentJson));
      }

      // Load daily metrics
      final dailyJson = _prefs.getString(_dailyMetricsKey);
      if (dailyJson != null) {
        final Map<String, dynamic> dailyData = jsonDecode(dailyJson);
        _dailyMetrics.clear();
        dailyData.forEach((key, value) {
          _dailyMetrics[key] = DailyMetrics.fromJson(value);
        });
      }

      // Load weekly metrics
      final weeklyJson = _prefs.getString(_weeklyMetricsKey);
      if (weeklyJson != null) {
        final Map<String, dynamic> weeklyData = jsonDecode(weeklyJson);
        _weeklyMetrics.clear();
        weeklyData.forEach((key, value) {
          _weeklyMetrics[key] = WeeklyMetrics.fromJson(value);
        });
      }

      _metricsController.add(_currentMetrics);
    } catch (e) {
      debugPrint('Failed to load sync metrics: $e');
    }
  }

  /// Save metrics to SharedPreferences
  Future<void> _saveMetrics() async {
    try {
      await _prefs.setString(_currentMetricsKey, jsonEncode(_currentMetrics.toJson()));

      final dailyData = _dailyMetrics.map((key, value) => MapEntry(key, value.toJson()));
      await _prefs.setString(_dailyMetricsKey, jsonEncode(dailyData));

      final weeklyData = _weeklyMetrics.map((key, value) => MapEntry(key, value.toJson()));
      await _prefs.setString(_weeklyMetricsKey, jsonEncode(weeklyData));
    } catch (e) {
      debugPrint('Failed to save sync metrics: $e');
    }
  }

  /// Helper: Format date as key
  String _formatDateKey(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }

  /// Helper: Format week as key
  String _formatWeekKey(DateTime weekStart) {
    return '${weekStart.year}-W${_getWeekNumber(weekStart).toString().padLeft(2, '0')}';
  }

  /// Helper: Get week start (Monday)
  DateTime _getWeekStart(DateTime date) {
    final weekday = date.weekday;
    return date.subtract(Duration(days: weekday - 1));
  }

  /// Helper: Get week number
  int _getWeekNumber(DateTime date) {
    final firstDayOfYear = DateTime(date.year, 1, 1);
    final daysSinceFirstDay = date.difference(firstDayOfYear).inDays;
    return (daysSinceFirstDay / 7).ceil() + 1;
  }

  void dispose() {
    _metricsController.close();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Models
// ═══════════════════════════════════════════════════════════════════════════

/// Sync operation types
enum SyncOperationType {
  upload,
  download,
  conflict,
}

/// Conflict resolution strategies
enum ConflictResolution {
  serverWins,
  localWins,
  merged,
  manual,
}

/// Active sync operation
class SyncOperation {
  final String id;
  final SyncOperationType type;
  final String entityType;
  final DateTime startTime;
  final int? estimatedPayloadSize;

  const SyncOperation({
    required this.id,
    required this.type,
    required this.entityType,
    required this.startTime,
    this.estimatedPayloadSize,
  });
}

/// Completed sync operation
class CompletedOperation {
  final SyncOperationType type;
  final String entityType;
  final DateTime startTime;
  final DateTime endTime;
  final Duration duration;
  final bool success;
  final int? payloadSize;
  final String? errorMessage;
  final bool wasConflict;
  final ConflictResolution? conflictResolution;

  const CompletedOperation({
    required this.type,
    required this.entityType,
    required this.startTime,
    required this.endTime,
    required this.duration,
    required this.success,
    this.payloadSize,
    this.errorMessage,
    this.wasConflict = false,
    this.conflictResolution,
  });

  Map<String, dynamic> toJson() => {
    'type': type.name,
    'entityType': entityType,
    'startTime': startTime.toIso8601String(),
    'endTime': endTime.toIso8601String(),
    'durationMs': duration.inMilliseconds,
    'success': success,
    'payloadSize': payloadSize,
    'errorMessage': errorMessage,
    'wasConflict': wasConflict,
    'conflictResolution': conflictResolution?.name,
  };

  factory CompletedOperation.fromJson(Map<String, dynamic> json) => CompletedOperation(
    type: SyncOperationType.values.byName(json['type'] as String),
    entityType: json['entityType'] as String,
    startTime: DateTime.parse(json['startTime'] as String),
    endTime: DateTime.parse(json['endTime'] as String),
    duration: Duration(milliseconds: json['durationMs'] as int),
    success: json['success'] as bool,
    payloadSize: json['payloadSize'] as int?,
    errorMessage: json['errorMessage'] as String?,
    wasConflict: json['wasConflict'] as bool? ?? false,
    conflictResolution: json['conflictResolution'] != null
        ? ConflictResolution.values.byName(json['conflictResolution'] as String)
        : null,
  );
}

/// Queue depth sample
class QueueDepthSample {
  final DateTime timestamp;
  final int depth;

  const QueueDepthSample({
    required this.timestamp,
    required this.depth,
  });

  Map<String, dynamic> toJson() => {
    'timestamp': timestamp.toIso8601String(),
    'depth': depth,
  };

  factory QueueDepthSample.fromJson(Map<String, dynamic> json) => QueueDepthSample(
    timestamp: DateTime.parse(json['timestamp'] as String),
    depth: json['depth'] as int,
  );
}

/// Retry statistics
class RetryStatistics {
  final int totalRetries;
  final Map<int, int> retryAttemptsByCount; // attemptNumber -> count

  const RetryStatistics({
    this.totalRetries = 0,
    this.retryAttemptsByCount = const {},
  });

  RetryStatistics copyWith({
    int? totalRetries,
    Map<int, int>? retryAttemptsByCount,
  }) {
    return RetryStatistics(
      totalRetries: totalRetries ?? this.totalRetries,
      retryAttemptsByCount: retryAttemptsByCount ?? this.retryAttemptsByCount,
    );
  }

  Map<String, dynamic> toJson() => {
    'totalRetries': totalRetries,
    'retryAttemptsByCount': retryAttemptsByCount.map((k, v) => MapEntry(k.toString(), v)),
  };

  factory RetryStatistics.fromJson(Map<String, dynamic> json) => RetryStatistics(
    totalRetries: json['totalRetries'] as int? ?? 0,
    retryAttemptsByCount: (json['retryAttemptsByCount'] as Map<String, dynamic>?)
        ?.map((k, v) => MapEntry(int.parse(k), v as int)) ?? {},
  );
}

/// Main sync metrics
class SyncMetrics {
  final int totalOperations;
  final int successfulOperations;
  final int failedOperations;
  final int totalDuration; // in milliseconds
  final int totalBandwidthBytes;
  final int conflictCount;
  final Map<ConflictResolution, int> conflictResolutions;
  final RetryStatistics retryStatistics;
  final Map<String, SyncOperation> activeOperations;
  final List<CompletedOperation> operationHistory;
  final List<QueueDepthSample> queueDepthHistory;
  final DateTime? lastSyncTime;

  const SyncMetrics({
    required this.totalOperations,
    required this.successfulOperations,
    required this.failedOperations,
    required this.totalDuration,
    required this.totalBandwidthBytes,
    required this.conflictCount,
    required this.conflictResolutions,
    required this.retryStatistics,
    required this.activeOperations,
    required this.operationHistory,
    required this.queueDepthHistory,
    this.lastSyncTime,
  });

  factory SyncMetrics.initial() => const SyncMetrics(
    totalOperations: 0,
    successfulOperations: 0,
    failedOperations: 0,
    totalDuration: 0,
    totalBandwidthBytes: 0,
    conflictCount: 0,
    conflictResolutions: {},
    retryStatistics: RetryStatistics(),
    activeOperations: {},
    operationHistory: [],
    queueDepthHistory: [],
  );

  /// Success rate (0.0 to 1.0)
  double get successRate {
    if (totalOperations == 0) return 1.0;
    return successfulOperations / totalOperations;
  }

  /// Average sync duration in milliseconds
  double get averageDuration {
    if (totalOperations == 0) return 0.0;
    return totalDuration / totalOperations;
  }

  /// Average payload size in bytes
  double get averagePayloadSize {
    if (totalOperations == 0) return 0.0;
    return totalBandwidthBytes / totalOperations;
  }

  /// Current queue depth
  int get currentQueueDepth => activeOperations.length;

  /// Average queue depth over last 100 samples
  double get averageQueueDepth {
    if (queueDepthHistory.isEmpty) return 0.0;
    final samples = queueDepthHistory.length > 100
        ? queueDepthHistory.sublist(queueDepthHistory.length - 100)
        : queueDepthHistory;
    return samples.map((s) => s.depth).reduce((a, b) => a + b) / samples.length;
  }

  /// Peak queue depth
  int get peakQueueDepth {
    if (queueDepthHistory.isEmpty) return 0;
    return queueDepthHistory.map((s) => s.depth).reduce((a, b) => a > b ? a : b);
  }

  SyncMetrics copyWith({
    int? totalOperations,
    int? successfulOperations,
    int? failedOperations,
    int? totalDuration,
    int? totalBandwidthBytes,
    int? conflictCount,
    Map<ConflictResolution, int>? conflictResolutions,
    RetryStatistics? retryStatistics,
    Map<String, SyncOperation>? activeOperations,
    List<CompletedOperation>? operationHistory,
    List<QueueDepthSample>? queueDepthHistory,
    DateTime? lastSyncTime,
  }) {
    return SyncMetrics(
      totalOperations: totalOperations ?? this.totalOperations,
      successfulOperations: successfulOperations ?? this.successfulOperations,
      failedOperations: failedOperations ?? this.failedOperations,
      totalDuration: totalDuration ?? this.totalDuration,
      totalBandwidthBytes: totalBandwidthBytes ?? this.totalBandwidthBytes,
      conflictCount: conflictCount ?? this.conflictCount,
      conflictResolutions: conflictResolutions ?? this.conflictResolutions,
      retryStatistics: retryStatistics ?? this.retryStatistics,
      activeOperations: activeOperations ?? this.activeOperations,
      operationHistory: operationHistory ?? this.operationHistory,
      queueDepthHistory: queueDepthHistory ?? this.queueDepthHistory,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
    );
  }

  Map<String, dynamic> toJson() => {
    'totalOperations': totalOperations,
    'successfulOperations': successfulOperations,
    'failedOperations': failedOperations,
    'totalDuration': totalDuration,
    'totalBandwidthBytes': totalBandwidthBytes,
    'conflictCount': conflictCount,
    'conflictResolutions': conflictResolutions.map((k, v) => MapEntry(k.name, v)),
    'retryStatistics': retryStatistics.toJson(),
    'operationHistory': operationHistory.map((o) => o.toJson()).toList(),
    'queueDepthHistory': queueDepthHistory.map((s) => s.toJson()).toList(),
    'lastSyncTime': lastSyncTime?.toIso8601String(),
  };

  factory SyncMetrics.fromJson(Map<String, dynamic> json) => SyncMetrics(
    totalOperations: json['totalOperations'] as int? ?? 0,
    successfulOperations: json['successfulOperations'] as int? ?? 0,
    failedOperations: json['failedOperations'] as int? ?? 0,
    totalDuration: json['totalDuration'] as int? ?? 0,
    totalBandwidthBytes: json['totalBandwidthBytes'] as int? ?? 0,
    conflictCount: json['conflictCount'] as int? ?? 0,
    conflictResolutions: (json['conflictResolutions'] as Map<String, dynamic>?)
        ?.map((k, v) => MapEntry(ConflictResolution.values.byName(k), v as int)) ?? {},
    retryStatistics: json['retryStatistics'] != null
        ? RetryStatistics.fromJson(json['retryStatistics'] as Map<String, dynamic>)
        : const RetryStatistics(),
    activeOperations: {}, // Don't restore active operations
    operationHistory: (json['operationHistory'] as List?)
        ?.map((o) => CompletedOperation.fromJson(o as Map<String, dynamic>))
        .toList() ?? [],
    queueDepthHistory: (json['queueDepthHistory'] as List?)
        ?.map((s) => QueueDepthSample.fromJson(s as Map<String, dynamic>))
        .toList() ?? [],
    lastSyncTime: json['lastSyncTime'] != null
        ? DateTime.parse(json['lastSyncTime'] as String)
        : null,
  );
}

/// Daily metrics aggregation
class DailyMetrics {
  final DateTime date;
  final int totalOperations;
  final int successfulOperations;
  final int failedOperations;
  final int totalDurationMs;
  final int totalBandwidthBytes;

  const DailyMetrics({
    required this.date,
    this.totalOperations = 0,
    this.successfulOperations = 0,
    this.failedOperations = 0,
    this.totalDurationMs = 0,
    this.totalBandwidthBytes = 0,
  });

  double get successRate {
    if (totalOperations == 0) return 1.0;
    return successfulOperations / totalOperations;
  }

  double get averageDuration {
    if (totalOperations == 0) return 0.0;
    return totalDurationMs / totalOperations;
  }

  DailyMetrics copyWith({
    DateTime? date,
    int? totalOperations,
    int? successfulOperations,
    int? failedOperations,
    int? totalDurationMs,
    int? totalBandwidthBytes,
  }) {
    return DailyMetrics(
      date: date ?? this.date,
      totalOperations: totalOperations ?? this.totalOperations,
      successfulOperations: successfulOperations ?? this.successfulOperations,
      failedOperations: failedOperations ?? this.failedOperations,
      totalDurationMs: totalDurationMs ?? this.totalDurationMs,
      totalBandwidthBytes: totalBandwidthBytes ?? this.totalBandwidthBytes,
    );
  }

  Map<String, dynamic> toJson() => {
    'date': date.toIso8601String(),
    'totalOperations': totalOperations,
    'successfulOperations': successfulOperations,
    'failedOperations': failedOperations,
    'totalDurationMs': totalDurationMs,
    'totalBandwidthBytes': totalBandwidthBytes,
  };

  factory DailyMetrics.fromJson(Map<String, dynamic> json) => DailyMetrics(
    date: DateTime.parse(json['date'] as String),
    totalOperations: json['totalOperations'] as int? ?? 0,
    successfulOperations: json['successfulOperations'] as int? ?? 0,
    failedOperations: json['failedOperations'] as int? ?? 0,
    totalDurationMs: json['totalDurationMs'] as int? ?? 0,
    totalBandwidthBytes: json['totalBandwidthBytes'] as int? ?? 0,
  );
}

/// Weekly metrics aggregation
class WeeklyMetrics {
  final DateTime weekStart;
  final int totalOperations;
  final int successfulOperations;
  final int failedOperations;
  final int totalDurationMs;
  final int totalBandwidthBytes;

  const WeeklyMetrics({
    required this.weekStart,
    this.totalOperations = 0,
    this.successfulOperations = 0,
    this.failedOperations = 0,
    this.totalDurationMs = 0,
    this.totalBandwidthBytes = 0,
  });

  double get successRate {
    if (totalOperations == 0) return 1.0;
    return successfulOperations / totalOperations;
  }

  double get averageDuration {
    if (totalOperations == 0) return 0.0;
    return totalDurationMs / totalOperations;
  }

  WeeklyMetrics copyWith({
    DateTime? weekStart,
    int? totalOperations,
    int? successfulOperations,
    int? failedOperations,
    int? totalDurationMs,
    int? totalBandwidthBytes,
  }) {
    return WeeklyMetrics(
      weekStart: weekStart ?? this.weekStart,
      totalOperations: totalOperations ?? this.totalOperations,
      successfulOperations: successfulOperations ?? this.successfulOperations,
      failedOperations: failedOperations ?? this.failedOperations,
      totalDurationMs: totalDurationMs ?? this.totalDurationMs,
      totalBandwidthBytes: totalBandwidthBytes ?? this.totalBandwidthBytes,
    );
  }

  Map<String, dynamic> toJson() => {
    'weekStart': weekStart.toIso8601String(),
    'totalOperations': totalOperations,
    'successfulOperations': successfulOperations,
    'failedOperations': failedOperations,
    'totalDurationMs': totalDurationMs,
    'totalBandwidthBytes': totalBandwidthBytes,
  };

  factory WeeklyMetrics.fromJson(Map<String, dynamic> json) => WeeklyMetrics(
    weekStart: DateTime.parse(json['weekStart'] as String),
    totalOperations: json['totalOperations'] as int? ?? 0,
    successfulOperations: json['successfulOperations'] as int? ?? 0,
    failedOperations: json['failedOperations'] as int? ?? 0,
    totalDurationMs: json['totalDurationMs'] as int? ?? 0,
    totalBandwidthBytes: json['totalBandwidthBytes'] as int? ?? 0,
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for SyncMetricsService
final syncMetricsServiceProvider = Provider<SyncMetricsService>((ref) {
  throw UnimplementedError('syncMetricsServiceProvider must be overridden');
});

/// Provider for real-time sync metrics stream
final syncMetricsProvider = StreamProvider<SyncMetrics>((ref) {
  final service = ref.watch(syncMetricsServiceProvider);
  return service.metricsStream;
});

/// Provider for current sync metrics
final currentSyncMetricsProvider = Provider<SyncMetrics>((ref) {
  final service = ref.watch(syncMetricsServiceProvider);
  return service.currentMetrics;
});

/// Provider for daily metrics (last 7 days)
final dailyMetricsProvider = Provider<List<DailyMetrics>>((ref) {
  final service = ref.watch(syncMetricsServiceProvider);
  return service.getLastNDays(7);
});
