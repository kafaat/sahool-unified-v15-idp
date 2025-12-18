import 'dart:async';
import '../storage/database.dart';

/// Sync Metrics - Analytics and monitoring for sync operations
/// مقاييس المزامنة - تحليلات ومراقبة عمليات المزامنة
class SyncMetrics {
  final AppDatabase database;

  static const String _metricsKey = 'sync_metrics';

  SyncMetrics({required this.database});

  /// Record sync operation
  Future<void> recordSync(SyncOperation operation) async {
    final metrics = await loadMetrics();
    final updated = metrics.addOperation(operation);
    await _saveMetrics(updated);
  }

  /// Load current metrics
  Future<SyncMetricsData> loadMetrics() async {
    try {
      final json = await database.getMetadata(_metricsKey);
      if (json != null) {
        return SyncMetricsData.fromJson(json);
      }
    } catch (e) {
      // Return empty on error
    }
    return SyncMetricsData.empty();
  }

  /// Save metrics
  Future<void> _saveMetrics(SyncMetricsData metrics) async {
    await database.setMetadata(_metricsKey, metrics.toJson());
  }

  /// Get sync health score (0-100)
  Future<int> getHealthScore() async {
    final metrics = await loadMetrics();
    return metrics.calculateHealthScore();
  }

  /// Get sync statistics for display
  Future<SyncStats> getStats() async {
    final metrics = await loadMetrics();
    return SyncStats(
      totalSyncs: metrics.totalSyncs,
      successfulSyncs: metrics.successfulSyncs,
      failedSyncs: metrics.failedSyncs,
      totalConflicts: metrics.totalConflicts,
      totalUploaded: metrics.totalUploaded,
      totalDownloaded: metrics.totalDownloaded,
      averageSyncDuration: metrics.averageSyncDuration,
      lastSyncTime: metrics.lastSyncTime,
      healthScore: metrics.calculateHealthScore(),
    );
  }

  /// Clear metrics (for testing or reset)
  Future<void> clearMetrics() async {
    await _saveMetrics(SyncMetricsData.empty());
  }

  /// Get daily sync summary
  Future<DailySyncSummary> getDailySummary() async {
    final logs = await database.getRecentSyncLogs(limit: 200);
    final today = DateTime.now();
    final todayStart = DateTime(today.year, today.month, today.day);

    int syncsToday = 0;
    int successToday = 0;
    int conflictsToday = 0;
    int itemsUploaded = 0;
    int itemsDownloaded = 0;

    for (final log in logs) {
      if (log.timestamp.isAfter(todayStart)) {
        if (log.type.contains('sync')) {
          syncsToday++;
          if (log.status == 'success') {
            successToday++;
            // Parse message for counts
            final uploadMatch = RegExp(r'Uploaded: (\d+)').firstMatch(log.message);
            final downloadMatch = RegExp(r'Pulled: (\d+)').firstMatch(log.message);
            if (uploadMatch != null) {
              itemsUploaded += int.tryParse(uploadMatch.group(1) ?? '0') ?? 0;
            }
            if (downloadMatch != null) {
              itemsDownloaded += int.tryParse(downloadMatch.group(1) ?? '0') ?? 0;
            }
          }
        }
        if (log.type == 'conflict') {
          conflictsToday++;
        }
      }
    }

    return DailySyncSummary(
      date: todayStart,
      totalSyncs: syncsToday,
      successfulSyncs: successToday,
      conflicts: conflictsToday,
      itemsUploaded: itemsUploaded,
      itemsDownloaded: itemsDownloaded,
    );
  }
}

/// Sync operation record
class SyncOperation {
  final DateTime timestamp;
  final bool success;
  final int uploaded;
  final int downloaded;
  final int conflicts;
  final Duration duration;
  final String? error;

  SyncOperation({
    required this.timestamp,
    required this.success,
    this.uploaded = 0,
    this.downloaded = 0,
    this.conflicts = 0,
    required this.duration,
    this.error,
  });
}

/// Sync metrics data
class SyncMetricsData {
  final int totalSyncs;
  final int successfulSyncs;
  final int failedSyncs;
  final int totalConflicts;
  final int totalUploaded;
  final int totalDownloaded;
  final int totalDurationMs;
  final DateTime? lastSyncTime;

  const SyncMetricsData({
    required this.totalSyncs,
    required this.successfulSyncs,
    required this.failedSyncs,
    required this.totalConflicts,
    required this.totalUploaded,
    required this.totalDownloaded,
    required this.totalDurationMs,
    this.lastSyncTime,
  });

  factory SyncMetricsData.empty() => const SyncMetricsData(
        totalSyncs: 0,
        successfulSyncs: 0,
        failedSyncs: 0,
        totalConflicts: 0,
        totalUploaded: 0,
        totalDownloaded: 0,
        totalDurationMs: 0,
      );

  /// Add operation and return new metrics
  SyncMetricsData addOperation(SyncOperation op) {
    return SyncMetricsData(
      totalSyncs: totalSyncs + 1,
      successfulSyncs: successfulSyncs + (op.success ? 1 : 0),
      failedSyncs: failedSyncs + (op.success ? 0 : 1),
      totalConflicts: totalConflicts + op.conflicts,
      totalUploaded: totalUploaded + op.uploaded,
      totalDownloaded: totalDownloaded + op.downloaded,
      totalDurationMs: totalDurationMs + op.duration.inMilliseconds,
      lastSyncTime: op.timestamp,
    );
  }

  /// Average sync duration
  Duration get averageSyncDuration {
    if (totalSyncs == 0) return Duration.zero;
    return Duration(milliseconds: totalDurationMs ~/ totalSyncs);
  }

  /// Success rate (0-100)
  int get successRate {
    if (totalSyncs == 0) return 100;
    return ((successfulSyncs / totalSyncs) * 100).round();
  }

  /// Calculate health score (0-100)
  int calculateHealthScore() {
    if (totalSyncs == 0) return 100;

    // Base score from success rate
    int score = successRate;

    // Penalize for conflicts (max -20)
    final conflictPenalty = (totalConflicts / totalSyncs * 20).clamp(0, 20);
    score -= conflictPenalty.round();

    // Penalize for slow syncs (max -10)
    if (averageSyncDuration.inSeconds > 30) {
      score -= 10;
    } else if (averageSyncDuration.inSeconds > 15) {
      score -= 5;
    }

    return score.clamp(0, 100);
  }

  /// To JSON string
  String toJson() {
    return '{"totalSyncs":$totalSyncs,"successfulSyncs":$successfulSyncs,'
        '"failedSyncs":$failedSyncs,"totalConflicts":$totalConflicts,'
        '"totalUploaded":$totalUploaded,"totalDownloaded":$totalDownloaded,'
        '"totalDurationMs":$totalDurationMs,'
        '"lastSyncTime":${lastSyncTime?.millisecondsSinceEpoch ?? 0}}';
  }

  /// From JSON string
  factory SyncMetricsData.fromJson(String json) {
    try {
      int getInt(String key) {
        final pattern = RegExp('"$key":(\\d+)');
        final match = pattern.firstMatch(json);
        return int.tryParse(match?.group(1) ?? '0') ?? 0;
      }

      final lastSyncMs = getInt('lastSyncTime');

      return SyncMetricsData(
        totalSyncs: getInt('totalSyncs'),
        successfulSyncs: getInt('successfulSyncs'),
        failedSyncs: getInt('failedSyncs'),
        totalConflicts: getInt('totalConflicts'),
        totalUploaded: getInt('totalUploaded'),
        totalDownloaded: getInt('totalDownloaded'),
        totalDurationMs: getInt('totalDurationMs'),
        lastSyncTime: lastSyncMs > 0
            ? DateTime.fromMillisecondsSinceEpoch(lastSyncMs)
            : null,
      );
    } catch (e) {
      return SyncMetricsData.empty();
    }
  }
}

/// Sync statistics for display
class SyncStats {
  final int totalSyncs;
  final int successfulSyncs;
  final int failedSyncs;
  final int totalConflicts;
  final int totalUploaded;
  final int totalDownloaded;
  final Duration averageSyncDuration;
  final DateTime? lastSyncTime;
  final int healthScore;

  const SyncStats({
    required this.totalSyncs,
    required this.successfulSyncs,
    required this.failedSyncs,
    required this.totalConflicts,
    required this.totalUploaded,
    required this.totalDownloaded,
    required this.averageSyncDuration,
    required this.lastSyncTime,
    required this.healthScore,
  });

  /// Get health status
  SyncHealthStatus get healthStatus {
    if (healthScore >= 90) return SyncHealthStatus.excellent;
    if (healthScore >= 70) return SyncHealthStatus.good;
    if (healthScore >= 50) return SyncHealthStatus.fair;
    return SyncHealthStatus.poor;
  }
}

/// Daily sync summary
class DailySyncSummary {
  final DateTime date;
  final int totalSyncs;
  final int successfulSyncs;
  final int conflicts;
  final int itemsUploaded;
  final int itemsDownloaded;

  const DailySyncSummary({
    required this.date,
    required this.totalSyncs,
    required this.successfulSyncs,
    required this.conflicts,
    required this.itemsUploaded,
    required this.itemsDownloaded,
  });

  int get successRate {
    if (totalSyncs == 0) return 100;
    return ((successfulSyncs / totalSyncs) * 100).round();
  }
}

/// Sync health status
enum SyncHealthStatus {
  excellent,
  good,
  fair,
  poor,
}

/// Extension for Arabic messages
extension SyncHealthStatusExtension on SyncHealthStatus {
  String get messageAr {
    switch (this) {
      case SyncHealthStatus.excellent:
        return 'ممتاز';
      case SyncHealthStatus.good:
        return 'جيد';
      case SyncHealthStatus.fair:
        return 'مقبول';
      case SyncHealthStatus.poor:
        return 'يحتاج انتباه';
    }
  }

  String get messageEn {
    switch (this) {
      case SyncHealthStatus.excellent:
        return 'Excellent';
      case SyncHealthStatus.good:
        return 'Good';
      case SyncHealthStatus.fair:
        return 'Fair';
      case SyncHealthStatus.poor:
        return 'Needs attention';
    }
  }
}
