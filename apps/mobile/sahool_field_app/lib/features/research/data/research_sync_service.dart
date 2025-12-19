import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:isar/isar.dart';
import 'local_log.dart';

/// Research Sync Service
/// خدمة مزامنة البحث
///
/// Handles offline-first sync of research logs with the backend.
/// يتعامل مع مزامنة سجلات البحث مع الخادم (offline-first)
class ResearchSyncService {
  final Isar _isar;
  final ResearchApiClient _apiClient;
  final LocalResearchLogRepository _repository;

  StreamSubscription<ConnectivityResult>? _connectivitySubscription;
  bool _isSyncing = false;

  ResearchSyncService(this._isar, this._apiClient)
      : _repository = LocalResearchLogRepository(_isar);

  /// Initialize sync service and listen for connectivity
  /// تهيئة خدمة المزامنة والاستماع للاتصال
  void initialize() {
    _connectivitySubscription = Connectivity()
        .onConnectivityChanged
        .listen(_onConnectivityChanged);
  }

  /// Dispose resources
  /// التخلص من الموارد
  void dispose() {
    _connectivitySubscription?.cancel();
  }

  /// Handle connectivity changes
  /// التعامل مع تغييرات الاتصال
  void _onConnectivityChanged(ConnectivityResult result) {
    if (result != ConnectivityResult.none) {
      // Connection restored - trigger sync
      syncPendingLogs();
    }
  }

  /// Sync all pending logs
  /// مزامنة جميع السجلات المعلقة
  Future<SyncResult> syncPendingLogs() async {
    if (_isSyncing) {
      return SyncResult(
        success: false,
        message: 'Sync already in progress',
        syncedCount: 0,
        failedCount: 0,
      );
    }

    _isSyncing = true;

    try {
      final pendingLogs = await _repository.getPendingSync();

      if (pendingLogs.isEmpty) {
        return SyncResult(
          success: true,
          message: 'No logs to sync',
          syncedCount: 0,
          failedCount: 0,
        );
      }

      int syncedCount = 0;
      int failedCount = 0;
      final errors = <String>[];

      for (final log in pendingLogs) {
        try {
          // Update status to syncing
          log.syncStatus = SyncStatus.syncing;
          await _repository.update(log);

          // Upload photos first if any
          if (log.localPhotoPaths.isNotEmpty) {
            final uploadedUrls = await _uploadPhotos(log.localPhotoPaths);
            log.uploadedPhotoUrls = uploadedUrls;
          }

          // Sync log to server
          final response = await _apiClient.syncLog(log.toSyncPayload());

          if (response.success && response.serverId != null) {
            log.markAsSynced(response.serverId!);
            syncedCount++;
          } else {
            log.markSyncFailed(response.error ?? 'Unknown error');
            failedCount++;
            errors.add('${log.offlineId}: ${response.error}');
          }

          await _repository.update(log);
        } catch (e) {
          log.markSyncFailed(e.toString());
          await _repository.update(log);
          failedCount++;
          errors.add('${log.offlineId}: $e');
        }
      }

      return SyncResult(
        success: failedCount == 0,
        message: 'Synced $syncedCount logs, $failedCount failed',
        syncedCount: syncedCount,
        failedCount: failedCount,
        errors: errors,
      );
    } finally {
      _isSyncing = false;
    }
  }

  /// Upload photos and return URLs
  /// رفع الصور وإرجاع الروابط
  Future<List<String>> _uploadPhotos(List<String> localPaths) async {
    final uploadedUrls = <String>[];

    for (final path in localPaths) {
      try {
        final url = await _apiClient.uploadPhoto(path);
        if (url != null) {
          uploadedUrls.add(url);
        }
      } catch (e) {
        // Log error but continue with other photos
        print('Failed to upload photo $path: $e');
      }
    }

    return uploadedUrls;
  }

  /// Get sync status summary
  /// الحصول على ملخص حالة المزامنة
  Future<SyncStatusSummary> getSyncStatusSummary() async {
    final pending = await _repository.getCountBySyncStatus(SyncStatus.pending);
    final syncing = await _repository.getCountBySyncStatus(SyncStatus.syncing);
    final synced = await _repository.getCountBySyncStatus(SyncStatus.synced);
    final failed = await _repository.getCountBySyncStatus(SyncStatus.failed);

    return SyncStatusSummary(
      pendingCount: pending,
      syncingCount: syncing,
      syncedCount: synced,
      failedCount: failed,
    );
  }

  /// Force retry all failed syncs
  /// إعادة محاولة جميع المزامنات الفاشلة
  Future<void> retryFailedSyncs() async {
    final failedLogs = await _isar.localResearchLogs
        .filter()
        .syncStatusEqualTo(SyncStatus.failed)
        .findAll();

    await _isar.writeTxn(() async {
      for (final log in failedLogs) {
        log.syncStatus = SyncStatus.pending;
        log.syncAttempts = 0;
        log.syncError = null;
        await _isar.localResearchLogs.put(log);
      }
    });

    // Trigger sync
    syncPendingLogs();
  }
}

/// Sync result
/// نتيجة المزامنة
class SyncResult {
  final bool success;
  final String message;
  final int syncedCount;
  final int failedCount;
  final List<String> errors;

  SyncResult({
    required this.success,
    required this.message,
    required this.syncedCount,
    required this.failedCount,
    this.errors = const [],
  });
}

/// Sync status summary
/// ملخص حالة المزامنة
class SyncStatusSummary {
  final int pendingCount;
  final int syncingCount;
  final int syncedCount;
  final int failedCount;

  SyncStatusSummary({
    required this.pendingCount,
    required this.syncingCount,
    required this.syncedCount,
    required this.failedCount,
  });

  int get totalCount => pendingCount + syncingCount + syncedCount + failedCount;
  bool get hasUnsyncedLogs => pendingCount > 0 || failedCount > 0;
}

/// API client interface for research sync
/// واجهة عميل API لمزامنة البحث
class ResearchApiClient {
  final String baseUrl;
  final String Function() getToken;

  ResearchApiClient({
    required this.baseUrl,
    required this.getToken,
  });

  /// Sync log to server
  /// مزامنة السجل مع الخادم
  Future<ApiResponse> syncLog(Map<String, dynamic> payload) async {
    // Implementation with Dio or http
    // In production, use proper HTTP client
    try {
      // POST to /api/v1/experiments/{experimentId}/logs/sync
      // with Authorization: Bearer {token}

      // Placeholder response
      return ApiResponse(
        success: true,
        serverId: 'server-generated-uuid',
      );
    } catch (e) {
      return ApiResponse(
        success: false,
        error: e.toString(),
      );
    }
  }

  /// Upload photo
  /// رفع صورة
  Future<String?> uploadPhoto(String localPath) async {
    // Implementation for file upload
    // POST to /api/v1/uploads/photos
    // with multipart/form-data

    // Placeholder
    return 'https://cdn.sahool.io/photos/uploaded-photo.jpg';
  }
}

/// API response
/// استجابة API
class ApiResponse {
  final bool success;
  final String? serverId;
  final String? error;

  ApiResponse({
    required this.success,
    this.serverId,
    this.error,
  });
}
