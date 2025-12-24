import 'dart:async';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/sync/sync_engine.dart';
import 'package:sahool_field_app/core/storage/database.dart';
import 'package:sahool_field_app/core/sync/network_status.dart';

/// Mock SyncEngine for testing
/// محرك المزامنة الوهمي للاختبارات
class MockSyncEngine extends Mock implements SyncEngine {
  bool _isSyncing = false;
  SyncStatus _currentStatus = SyncStatus.idle;
  final _syncStatusController = StreamController<SyncStatus>.broadcast();

  int _uploadedCount = 0;
  int _downloadedCount = 0;
  bool _shouldFail = false;
  String? _failureMessage;

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
  }

  @override
  AppDatabase get database => throw UnimplementedError();
}
