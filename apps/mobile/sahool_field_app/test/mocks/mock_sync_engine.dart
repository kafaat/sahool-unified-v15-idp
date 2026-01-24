import 'dart:async';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/sync/sync_engine.dart';
import 'package:sahool_field_app/core/storage/database.dart';
import 'package:sahool_field_app/core/sync/network_status.dart';
import 'package:sahool_field_app/core/http/rate_limiter.dart';
import 'package:sahool_field_app/core/utils/retry_policy.dart';

/// Mock SyncEngine for testing
/// محرك المزامنة الوهمي للاختبارات
class MockSyncEngine extends Mock implements SyncEngine {
  bool _isSyncing = false;
  SyncStatus _currentStatus = SyncStatus.idle;
  final _syncStatusController = StreamController<SyncStatus>.broadcast();
  final _backoffStatusController = StreamController<BackoffStatus>.broadcast();

  int _uploadedCount = 0;
  int _downloadedCount = 0;
  bool _shouldFail = false;
  String? _failureMessage;
  int _consecutiveFailures = 0;
  DateTime? _lastSuccessfulSync;

  MockSyncEngine({
    AppDatabase? database,
    NetworkStatus? networkStatus,
  });

  /// Configure sync to fail
  void setShouldFail(bool shouldFail, {String? message}) {
    _shouldFail = shouldFail;
    _failureMessage = message;
  }

  /// Set sync counts for testing
  void setSyncCounts({int uploaded = 0, int downloaded = 0}) {
    _uploadedCount = uploaded;
    _downloadedCount = downloaded;
  }

  /// Simulate sync in progress
  void setIsSyncing(bool syncing) {
    _isSyncing = syncing;
    _currentStatus = syncing ? SyncStatus.syncing : SyncStatus.idle;
    _syncStatusController.add(_currentStatus);
  }

  /// Simulate sync error
  void simulateError() {
    _currentStatus = SyncStatus.error;
    _syncStatusController.add(_currentStatus);
  }

  @override
  Stream<SyncStatus> get syncStatus => _syncStatusController.stream;

  @override
  Future<SyncResult> runOnce() async {
    if (_isSyncing) {
      return SyncResult(
        success: false,
        message: 'Sync already in progress',
      );
    }

    if (_shouldFail) {
      _currentStatus = SyncStatus.error;
      _syncStatusController.add(_currentStatus);
      return SyncResult(
        success: false,
        message: _failureMessage ?? 'Sync failed',
      );
    }

    _isSyncing = true;
    _currentStatus = SyncStatus.syncing;
    _syncStatusController.add(_currentStatus);

    // Simulate sync delay
    await Future.delayed(const Duration(milliseconds: 100));

    _isSyncing = false;
    _currentStatus = SyncStatus.idle;
    _syncStatusController.add(_currentStatus);

    return SyncResult(
      success: true,
      uploaded: _uploadedCount,
      downloaded: _downloadedCount,
    );
  }

  @override
  void startPeriodic() {
    // Mock implementation - do nothing
  }

  @override
  void stop() {
    _isSyncing = false;
    _currentStatus = SyncStatus.idle;
  }

  @override
  Future<void> forceRefresh() async {
    _currentStatus = SyncStatus.syncing;
    _syncStatusController.add(_currentStatus);

    await Future.delayed(const Duration(milliseconds: 100));

    if (_shouldFail) {
      _currentStatus = SyncStatus.error;
      _syncStatusController.add(_currentStatus);
      throw Exception(_failureMessage ?? 'Refresh failed');
    }

    _currentStatus = SyncStatus.idle;
    _syncStatusController.add(_currentStatus);
  }

  @override
  void dispose() {
    _syncStatusController.close();
    _backoffStatusController.close();
  }

  @override
  AppDatabase get database => throw UnimplementedError();

  // ═══════════════════════════════════════════════════════════════════════════
  // Backoff and Retry Tracking
  // ═══════════════════════════════════════════════════════════════════════════

  @override
  Stream<BackoffStatus> get backoffStatus => _backoffStatusController.stream;

  /// Get backoff statuses for all tracked endpoints
  @override
  Map<String, EndpointStatus> getBackoffStatuses() {
    // Return empty map for mock - can be customized in tests
    return {};
  }

  /// Reset backoff for a specific endpoint
  @override
  void resetEndpointBackoff(String endpoint) {
    _backoffStatusController.add(BackoffStatus.idle());
  }

  /// Reset all backoff trackers
  @override
  void resetAllBackoff() {
    _consecutiveFailures = 0;
    _backoffStatusController.add(BackoffStatus.idle());
  }

  /// Get sync statistics
  @override
  SyncStatistics getStatistics() {
    return SyncStatistics(
      consecutiveFailures: _consecutiveFailures,
      lastSuccessfulSync: _lastSuccessfulSync,
      isSyncing: _isSyncing,
      unhealthyEndpoints: 0,
    );
  }

  /// Get rate limit status
  @override
  RateLimitStatus getSyncRateLimitStatus() {
    return RateLimitStatus(
      endpointType: 'sync',
      availableTokens: 30,
      maxTokens: 30,
      refillRate: 0.5,
      queuedRequests: 0,
    );
  }

  /// Set consecutive failures for testing
  void setConsecutiveFailures(int count) {
    _consecutiveFailures = count;
  }

  /// Simulate successful sync completion
  void simulateSuccessfulSync() {
    _lastSuccessfulSync = DateTime.now();
    _consecutiveFailures = 0;
    _currentStatus = SyncStatus.idle;
    _syncStatusController.add(_currentStatus);
    _backoffStatusController.add(BackoffStatus.idle());
  }

  /// Simulate backoff status
  void simulateBackoffActive({
    required int endpointsInBackoff,
    Duration? nextRetryIn,
  }) {
    _backoffStatusController.add(BackoffStatus(
      isBackoffActive: true,
      affectedEndpoints: [],
      totalEndpointsInBackoff: endpointsInBackoff,
    ));
  }
}
