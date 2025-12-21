import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../utils/app_logger.dart';
import '../sync/network_status.dart';
import 'outbox_repository.dart';
import 'sync_conflict_resolver.dart';

/// SAHOOL Offline Sync Engine
/// محرك المزامنة بدون اتصال
///
/// Features:
/// - Outbox pattern for reliable offline mutations
/// - Delta sync for efficient data transfer
/// - Automatic conflict resolution
/// - Retry with exponential backoff
/// - Queue prioritization

class OfflineSyncEngine {
  static OfflineSyncEngine? _instance;
  static OfflineSyncEngine get instance {
    _instance ??= OfflineSyncEngine._();
    return _instance!;
  }

  OfflineSyncEngine._();

  final OutboxRepository _outbox = OutboxRepository();
  final SyncConflictResolver _conflictResolver = SyncConflictResolver();
  final _uuid = const Uuid();

  Timer? _syncTimer;
  bool _isSyncing = false;
  int _retryCount = 0;
  static const int _maxRetries = 5;

  final _syncStatusController = StreamController<SyncStatus>.broadcast();
  Stream<SyncStatus> get syncStatus => _syncStatusController.stream;

  SyncStatus _currentStatus = SyncStatus.idle;
  SyncStatus get currentStatus => _currentStatus;

  // ═══════════════════════════════════════════════════════════════════════════
  // التهيئة
  // ═══════════════════════════════════════════════════════════════════════════

  /// تهيئة المحرك
  Future<void> initialize() async {
    await _outbox.initialize();

    // Start periodic sync check
    _syncTimer = Timer.periodic(
      const Duration(minutes: 2),
      (_) => _checkAndSync(),
    );

    AppLogger.i('Offline sync engine initialized', tag: 'SYNC');
  }

  /// إيقاف المحرك
  void dispose() {
    _syncTimer?.cancel();
    _syncStatusController.close();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // إضافة عمليات للـ Outbox
  // ═══════════════════════════════════════════════════════════════════════════

  /// إضافة عملية إنشاء
  Future<String> enqueueCreate<T>({
    required String entityType,
    required Map<String, dynamic> data,
    SyncPriority priority = SyncPriority.normal,
  }) async {
    final id = _uuid.v4();
    final entry = OutboxEntry(
      id: id,
      entityType: entityType,
      operation: SyncOperation.create,
      data: data,
      priority: priority,
      createdAt: DateTime.now(),
      status: OutboxStatus.pending,
    );

    await _outbox.add(entry);
    AppLogger.sync('Enqueued CREATE: $entityType', details: id);

    _triggerSync();
    return id;
  }

  /// إضافة عملية تحديث
  Future<void> enqueueUpdate({
    required String entityType,
    required String entityId,
    required Map<String, dynamic> data,
    Map<String, dynamic>? previousData,
    SyncPriority priority = SyncPriority.normal,
  }) async {
    final entry = OutboxEntry(
      id: _uuid.v4(),
      entityType: entityType,
      entityId: entityId,
      operation: SyncOperation.update,
      data: data,
      previousData: previousData,
      priority: priority,
      createdAt: DateTime.now(),
      status: OutboxStatus.pending,
    );

    await _outbox.add(entry);
    AppLogger.sync('Enqueued UPDATE: $entityType/$entityId');

    _triggerSync();
  }

  /// إضافة عملية حذف
  Future<void> enqueueDelete({
    required String entityType,
    required String entityId,
    SyncPriority priority = SyncPriority.high,
  }) async {
    final entry = OutboxEntry(
      id: _uuid.v4(),
      entityType: entityType,
      entityId: entityId,
      operation: SyncOperation.delete,
      data: {},
      priority: priority,
      createdAt: DateTime.now(),
      status: OutboxStatus.pending,
    );

    await _outbox.add(entry);
    AppLogger.sync('Enqueued DELETE: $entityType/$entityId');

    _triggerSync();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // المزامنة
  // ═══════════════════════════════════════════════════════════════════════════

  /// تشغيل المزامنة
  void _triggerSync() {
    if (!_isSyncing) {
      _checkAndSync();
    }
  }

  /// فحص وتشغيل المزامنة
  Future<void> _checkAndSync() async {
    if (_isSyncing) return;

    // Check network status
    final isOnline = await NetworkStatus.instance.isConnected;
    if (!isOnline) {
      _updateStatus(SyncStatus.offline);
      return;
    }

    // Check if there are pending items
    final pendingCount = await _outbox.getPendingCount();
    if (pendingCount == 0) {
      _updateStatus(SyncStatus.idle);
      return;
    }

    await sync();
  }

  /// تنفيذ المزامنة
  Future<SyncResult> sync() async {
    if (_isSyncing) {
      return SyncResult(
        success: false,
        message: 'Sync already in progress',
      );
    }

    _isSyncing = true;
    _updateStatus(SyncStatus.syncing);

    try {
      final pending = await _outbox.getPending();
      AppLogger.sync('Starting sync', details: '${pending.length} items');

      int successCount = 0;
      int failCount = 0;
      final errors = <String>[];

      for (final entry in pending) {
        try {
          await _processEntry(entry);
          await _outbox.markCompleted(entry.id);
          successCount++;
        } catch (e) {
          failCount++;
          errors.add('${entry.entityType}/${entry.entityId}: $e');

          // Mark as failed with retry info
          await _outbox.markFailed(entry.id, e.toString());

          // Check if should stop syncing
          if (failCount >= 3) {
            AppLogger.w('Too many failures, pausing sync', tag: 'SYNC');
            break;
          }
        }
      }

      _retryCount = 0;
      _updateStatus(failCount > 0 ? SyncStatus.partialSuccess : SyncStatus.success);

      final result = SyncResult(
        success: failCount == 0,
        syncedCount: successCount,
        failedCount: failCount,
        errors: errors,
        message: 'Synced $successCount items, $failCount failed',
      );

      AppLogger.sync('Sync completed', success: result.success, details: result.message);

      return result;
    } catch (e) {
      AppLogger.e('Sync failed', tag: 'SYNC', error: e);
      _updateStatus(SyncStatus.error);

      // Schedule retry with exponential backoff
      _scheduleRetry();

      return SyncResult(
        success: false,
        message: 'Sync failed: $e',
      );
    } finally {
      _isSyncing = false;
    }
  }

  /// معالجة عنصر واحد
  Future<void> _processEntry(OutboxEntry entry) async {
    switch (entry.operation) {
      case SyncOperation.create:
        await _processCreate(entry);
        break;
      case SyncOperation.update:
        await _processUpdate(entry);
        break;
      case SyncOperation.delete:
        await _processDelete(entry);
        break;
    }
  }

  /// معالجة عملية إنشاء
  Future<void> _processCreate(OutboxEntry entry) async {
    // In real implementation, call API
    // final response = await _apiClient.post(
    //   '/${entry.entityType}',
    //   data: entry.data,
    // );

    // Simulate API call
    await Future.delayed(const Duration(milliseconds: 100));
    AppLogger.d('Processed CREATE: ${entry.entityType}', tag: 'SYNC');
  }

  /// معالجة عملية تحديث
  Future<void> _processUpdate(OutboxEntry entry) async {
    // Check for conflicts
    if (entry.previousData != null) {
      final serverData = await _fetchServerData(entry.entityType, entry.entityId!);
      if (serverData != null) {
        final hasConflict = _conflictResolver.detectConflict(
          local: entry.data,
          server: serverData,
          base: entry.previousData!,
        );

        if (hasConflict) {
          final resolved = await _conflictResolver.resolve(
            local: entry.data,
            server: serverData,
            base: entry.previousData!,
            strategy: ConflictStrategy.serverWins, // or custom logic
          );

          // Use resolved data
          entry = entry.copyWith(data: resolved);
        }
      }
    }

    // Simulate API call
    await Future.delayed(const Duration(milliseconds: 100));
    AppLogger.d('Processed UPDATE: ${entry.entityType}/${entry.entityId}', tag: 'SYNC');
  }

  /// معالجة عملية حذف
  Future<void> _processDelete(OutboxEntry entry) async {
    // Simulate API call
    await Future.delayed(const Duration(milliseconds: 100));
    AppLogger.d('Processed DELETE: ${entry.entityType}/${entry.entityId}', tag: 'SYNC');
  }

  /// جلب بيانات الخادم (للمقارنة)
  Future<Map<String, dynamic>?> _fetchServerData(String entityType, String entityId) async {
    // In real implementation, fetch from API
    return null;
  }

  /// جدولة إعادة المحاولة
  void _scheduleRetry() {
    if (_retryCount >= _maxRetries) {
      AppLogger.e('Max retries reached', tag: 'SYNC');
      return;
    }

    _retryCount++;
    final delay = Duration(seconds: (2 << _retryCount)); // Exponential backoff

    Timer(delay, _checkAndSync);
    AppLogger.d('Retry scheduled in ${delay.inSeconds}s (attempt $_retryCount)', tag: 'SYNC');
  }

  /// تحديث الحالة
  void _updateStatus(SyncStatus status) {
    _currentStatus = status;
    _syncStatusController.add(status);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الإحصائيات
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحصول على إحصائيات الـ Outbox
  Future<OutboxStats> getStats() async {
    final pending = await _outbox.getPendingCount();
    final failed = await _outbox.getFailedCount();
    final completed = await _outbox.getCompletedCount();

    return OutboxStats(
      pendingCount: pending,
      failedCount: failed,
      completedCount: completed,
      isSyncing: _isSyncing,
      lastSyncStatus: _currentStatus,
    );
  }

  /// إعادة محاولة العناصر الفاشلة
  Future<void> retryFailed() async {
    await _outbox.resetFailed();
    _triggerSync();
  }

  /// تنظيف العناصر المكتملة
  Future<void> clearCompleted() async {
    await _outbox.clearCompleted();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// النماذج
// ═══════════════════════════════════════════════════════════════════════════

/// حالة المزامنة
enum SyncStatus {
  idle,
  syncing,
  success,
  partialSuccess,
  error,
  offline,
}

/// عملية المزامنة
enum SyncOperation {
  create,
  update,
  delete,
}

/// أولوية المزامنة
enum SyncPriority {
  low,
  normal,
  high,
  critical,
}

/// حالة عنصر الـ Outbox
enum OutboxStatus {
  pending,
  processing,
  completed,
  failed,
}

/// عنصر الـ Outbox
class OutboxEntry {
  final String id;
  final String entityType;
  final String? entityId;
  final SyncOperation operation;
  final Map<String, dynamic> data;
  final Map<String, dynamic>? previousData;
  final SyncPriority priority;
  final DateTime createdAt;
  final OutboxStatus status;
  final int retryCount;
  final String? lastError;

  const OutboxEntry({
    required this.id,
    required this.entityType,
    this.entityId,
    required this.operation,
    required this.data,
    this.previousData,
    required this.priority,
    required this.createdAt,
    required this.status,
    this.retryCount = 0,
    this.lastError,
  });

  OutboxEntry copyWith({
    String? id,
    String? entityType,
    String? entityId,
    SyncOperation? operation,
    Map<String, dynamic>? data,
    Map<String, dynamic>? previousData,
    SyncPriority? priority,
    DateTime? createdAt,
    OutboxStatus? status,
    int? retryCount,
    String? lastError,
  }) {
    return OutboxEntry(
      id: id ?? this.id,
      entityType: entityType ?? this.entityType,
      entityId: entityId ?? this.entityId,
      operation: operation ?? this.operation,
      data: data ?? this.data,
      previousData: previousData ?? this.previousData,
      priority: priority ?? this.priority,
      createdAt: createdAt ?? this.createdAt,
      status: status ?? this.status,
      retryCount: retryCount ?? this.retryCount,
      lastError: lastError ?? this.lastError,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'entityType': entityType,
    'entityId': entityId,
    'operation': operation.name,
    'data': data,
    'previousData': previousData,
    'priority': priority.index,
    'createdAt': createdAt.toIso8601String(),
    'status': status.name,
    'retryCount': retryCount,
    'lastError': lastError,
  };

  factory OutboxEntry.fromJson(Map<String, dynamic> json) => OutboxEntry(
    id: json['id'] as String,
    entityType: json['entityType'] as String,
    entityId: json['entityId'] as String?,
    operation: SyncOperation.values.byName(json['operation'] as String),
    data: Map<String, dynamic>.from(json['data'] as Map),
    previousData: json['previousData'] != null
        ? Map<String, dynamic>.from(json['previousData'] as Map)
        : null,
    priority: SyncPriority.values[json['priority'] as int],
    createdAt: DateTime.parse(json['createdAt'] as String),
    status: OutboxStatus.values.byName(json['status'] as String),
    retryCount: json['retryCount'] as int? ?? 0,
    lastError: json['lastError'] as String?,
  );
}

/// نتيجة المزامنة
class SyncResult {
  final bool success;
  final int syncedCount;
  final int failedCount;
  final List<String> errors;
  final String message;

  const SyncResult({
    required this.success,
    this.syncedCount = 0,
    this.failedCount = 0,
    this.errors = const [],
    required this.message,
  });
}

/// إحصائيات الـ Outbox
class OutboxStats {
  final int pendingCount;
  final int failedCount;
  final int completedCount;
  final bool isSyncing;
  final SyncStatus lastSyncStatus;

  const OutboxStats({
    required this.pendingCount,
    required this.failedCount,
    required this.completedCount,
    required this.isSyncing,
    required this.lastSyncStatus,
  });

  int get totalCount => pendingCount + failedCount + completedCount;

  bool get hasPending => pendingCount > 0;
  bool get hasFailed => failedCount > 0;
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

final offlineSyncEngineProvider = Provider<OfflineSyncEngine>((ref) {
  return OfflineSyncEngine.instance;
});

final syncStatusProvider = StreamProvider<SyncStatus>((ref) {
  return OfflineSyncEngine.instance.syncStatus;
});

final outboxStatsProvider = FutureProvider<OutboxStats>((ref) {
  return OfflineSyncEngine.instance.getStats();
});
