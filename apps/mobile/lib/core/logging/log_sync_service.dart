import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import 'log_models.dart';
import 'file_logger.dart';

/// SAHOOL Log Sync Service
/// خدمة مزامنة السجلات لتطبيق سهول
///
/// Features:
/// - Automatic sync when online
/// - Batch sync with configurable size
/// - Retry logic for failed syncs
/// - Network status monitoring
/// - Background sync support
class LogSyncService {
  /// File logger for reading logs
  final FileLogger fileLogger;

  /// Configuration
  final LoggerConfig config;

  /// HTTP client for syncing (will be injected)
  final Future<bool> Function(List<Map<String, dynamic>> logs)? _syncCallback;

  /// Network connectivity
  final Connectivity _connectivity = Connectivity();

  /// Network status subscription
  StreamSubscription<List<ConnectivityResult>>? _connectivitySubscription;

  /// Sync timer
  Timer? _syncTimer;

  /// Current sync status
  LogSyncStatus _status = const LogSyncStatus();

  /// Status stream controller
  final _statusController = StreamController<LogSyncStatus>.broadcast();

  /// Whether service is started
  bool _isStarted = false;

  /// Whether currently online
  bool _isOnline = false;

  /// Maximum retry attempts
  static const int _maxRetries = 3;

  /// Retry delay in seconds
  static const int _retryDelaySeconds = 30;

  LogSyncService({
    required this.fileLogger,
    LoggerConfig? config,
    Future<bool> Function(List<Map<String, dynamic>>)? syncCallback,
  })  : config = config ?? const LoggerConfig(),
        _syncCallback = syncCallback;

  /// Get sync status stream
  /// الحصول على تدفق حالة المزامنة
  Stream<LogSyncStatus> get statusStream => _statusController.stream;

  /// Get current sync status
  /// الحصول على حالة المزامنة الحالية
  LogSyncStatus get status => _status;

  /// Check if online
  /// التحقق من الاتصال بالإنترنت
  bool get isOnline => _isOnline;

  /// Start the sync service
  /// بدء خدمة المزامنة
  Future<void> start() async {
    if (_isStarted) return;

    _isStarted = true;

    // Check initial connectivity
    final results = await _connectivity.checkConnectivity();
    _updateConnectivity(results);

    // Listen for connectivity changes
    _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
      _updateConnectivity,
    );

    // Start periodic sync if enabled
    if (config.enableAutoSync) {
      _startPeriodicSync();
    }

    debugPrint('LogSyncService started');
  }

  /// Stop the sync service
  /// إيقاف خدمة المزامنة
  Future<void> stop() async {
    _isStarted = false;
    _syncTimer?.cancel();
    _syncTimer = null;
    await _connectivitySubscription?.cancel();
    _connectivitySubscription = null;
    debugPrint('LogSyncService stopped');
  }

  /// Manually trigger sync
  /// تشغيل المزامنة يدوياً
  Future<LogSyncStatus> syncNow() async {
    if (!_isOnline) {
      _updateStatus(_status.copyWith(
        lastError: 'No network connection | لا يوجد اتصال بالشبكة',
      ));
      return _status;
    }

    if (_status.isSyncing) {
      return _status;
    }

    _updateStatus(_status.copyWith(isSyncing: true));

    try {
      // Get unsynced logs
      final unsyncedLogs = await fileLogger.getUnsyncedLogs(
        limit: config.syncBatchSize,
      );

      if (unsyncedLogs.isEmpty) {
        _updateStatus(_status.copyWith(
          isSyncing: false,
          lastSyncAt: DateTime.now(),
          pendingCount: 0,
        ));
        return _status;
      }

      _updateStatus(_status.copyWith(
        pendingCount: unsyncedLogs.length,
      ));

      // Try to sync
      final success = await _performSync(unsyncedLogs);

      if (success) {
        // Mark logs as synced
        await fileLogger.markAsSynced(unsyncedLogs.map((e) => e.id).toList());

        _updateStatus(_status.copyWith(
          isSyncing: false,
          lastSyncAt: DateTime.now(),
          syncedCount: _status.syncedCount + unsyncedLogs.length,
          pendingCount: 0,
          lastError: null,
        ));
      } else {
        _updateStatus(_status.copyWith(
          isSyncing: false,
          failedCount: _status.failedCount + unsyncedLogs.length,
          lastError: 'Sync failed | فشلت المزامنة',
        ));
      }
    } catch (e) {
      _updateStatus(_status.copyWith(
        isSyncing: false,
        lastError: e.toString(),
      ));
    }

    return _status;
  }

  /// Sync with retries
  /// المزامنة مع إعادة المحاولة
  Future<LogSyncStatus> syncWithRetry() async {
    for (int attempt = 0; attempt < _maxRetries; attempt++) {
      final result = await syncNow();

      if (result.lastError == null) {
        return result;
      }

      if (attempt < _maxRetries - 1) {
        await Future.delayed(const Duration(seconds: _retryDelaySeconds));
      }
    }

    return _status;
  }

  /// Get pending log count
  /// الحصول على عدد السجلات المعلقة
  Future<int> getPendingCount() async {
    final logs = await fileLogger.getUnsyncedLogs(limit: 10000);
    return logs.length;
  }

  /// Clear sync history
  /// مسح سجل المزامنة
  void clearSyncHistory() {
    _updateStatus(const LogSyncStatus());
  }

  /// Dispose resources
  /// التخلص من الموارد
  Future<void> dispose() async {
    await stop();
    await _statusController.close();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Perform the actual sync
  Future<bool> _performSync(List<StructuredLogEntry> logs) async {
    if (_syncCallback == null) {
      // No callback provided, simulate success
      // In production, this would call the API
      debugPrint('LogSyncService: Would sync ${logs.length} logs');
      return true;
    }

    try {
      return await _syncCallback(logs.map((e) => e.toJson()).toList());
    } catch (e) {
      debugPrint('LogSyncService sync error: $e');
      return false;
    }
  }

  /// Update connectivity status
  void _updateConnectivity(List<ConnectivityResult> results) {
    final wasOnline = _isOnline;
    _isOnline = results.isNotEmpty &&
        !results.every((r) => r == ConnectivityResult.none);

    // Trigger sync when coming online
    if (!wasOnline && _isOnline && config.enableAutoSync) {
      debugPrint('LogSyncService: Network restored, triggering sync');
      syncNow();
    }
  }

  /// Start periodic sync
  void _startPeriodicSync() {
    _syncTimer?.cancel();
    _syncTimer = Timer.periodic(
      Duration(seconds: config.syncIntervalSeconds),
      (_) {
        if (_isOnline && !_status.isSyncing) {
          syncNow();
        }
      },
    );
  }

  /// Update sync status
  void _updateStatus(LogSyncStatus newStatus) {
    _status = newStatus;
    _statusController.add(_status);
  }
}

/// Log sync API client interface
/// واجهة عميل API لمزامنة السجلات
abstract class LogSyncApiClient {
  /// Send logs to server
  /// إرسال السجلات إلى الخادم
  Future<bool> sendLogs(List<Map<String, dynamic>> logs);

  /// Get server acknowledgement for synced logs
  /// الحصول على تأكيد الخادم للسجلات المتزامنة
  Future<List<String>> getAcknowledgedLogIds();
}

/// Default implementation of log sync API client
/// التنفيذ الافتراضي لعميل API لمزامنة السجلات
class DefaultLogSyncApiClient implements LogSyncApiClient {
  final String baseUrl;
  final String? authToken;
  final Future<dynamic> Function(
    String method,
    String url,
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  )? httpClient;

  DefaultLogSyncApiClient({
    required this.baseUrl,
    this.authToken,
    this.httpClient,
  });

  @override
  Future<bool> sendLogs(List<Map<String, dynamic>> logs) async {
    if (httpClient == null) {
      debugPrint('DefaultLogSyncApiClient: No HTTP client provided');
      return false;
    }

    try {
      final response = await httpClient!(
        'POST',
        '$baseUrl/api/v1/logs/batch',
        {'logs': logs},
        {
          'Content-Type': 'application/json',
          if (authToken != null) 'Authorization': 'Bearer $authToken',
        },
      );

      return response != null;
    } catch (e) {
      debugPrint('DefaultLogSyncApiClient error: $e');
      return false;
    }
  }

  @override
  Future<List<String>> getAcknowledgedLogIds() async {
    // Implementation would depend on server API
    return [];
  }
}

/// Batch log sync result
/// نتيجة مزامنة السجلات الدفعية
class LogSyncResult {
  /// Number of logs synced successfully
  final int successCount;

  /// Number of logs that failed to sync
  final int failedCount;

  /// Error messages if any
  final List<String> errors;

  /// Timestamp of sync attempt
  final DateTime timestamp;

  const LogSyncResult({
    required this.successCount,
    required this.failedCount,
    required this.errors,
    required this.timestamp,
  });

  /// Whether sync was fully successful
  bool get isSuccess => failedCount == 0;

  /// Whether sync was partially successful
  bool get isPartialSuccess => successCount > 0 && failedCount > 0;

  Map<String, dynamic> toJson() => {
        'success_count': successCount,
        'failed_count': failedCount,
        'errors': errors,
        'timestamp': timestamp.toIso8601String(),
      };
}
