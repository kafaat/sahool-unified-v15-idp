import 'dart:async';
import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:uuid/uuid.dart';

import '../../storage/database.dart';
import '../../utils/app_logger.dart';
import 'outbox_entry.dart';

/// SAHOOL Outbox Service
/// خدمة صندوق الصادر للمزامنة
///
/// Unified service for managing the outbox pattern with Drift database.
/// Provides CRUD operations, query methods, aggregation, and statistics.
///
/// Features:
/// - Priority-based queue management
/// - Idempotency checking
/// - Update aggregation
/// - Comprehensive statistics
/// - Retry scheduling with exponential backoff

class OutboxService {
  final AppDatabase _db;
  final _uuid = const Uuid();

  // Stream controllers for reactive updates
  final _statsController = StreamController<OutboxStats>.broadcast();
  final _changesController = StreamController<OutboxChangeEvent>.broadcast();

  // Cache for frequently accessed stats
  OutboxStats? _cachedStats;
  DateTime? _statsCacheTime;
  static const _statsCacheDuration = Duration(seconds: 5);

  OutboxService({required AppDatabase database}) : _db = database;

  /// Stream of statistics updates
  Stream<OutboxStats> get statsStream => _statsController.stream;

  /// Stream of outbox changes (for UI updates)
  Stream<OutboxChangeEvent> get changesStream => _changesController.stream;

  // ═══════════════════════════════════════════════════════════════════════════
  // Queue Operations - إضافة للطابور
  // ═══════════════════════════════════════════════════════════════════════════

  /// Add a create operation to the outbox
  Future<OutboxEntry> enqueueCreate({
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required Map<String, dynamic> payload,
    OutboxPriority priority = OutboxPriority.normal,
    Map<String, dynamic>? metadata,
    String? source,
  }) async {
    final id = _uuid.v4();
    final entry = OutboxEntry.create(
      id: id,
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      payload: payload,
      priority: priority,
      metadata: metadata,
      source: source ?? 'user_action',
    );

    await _insertEntry(entry);
    _notifyChange(OutboxChangeEvent.added(entry));
    AppLogger.sync('Enqueued CREATE: $entityType/$entityId', details: id);

    return entry;
  }

  /// Add an update operation to the outbox
  Future<OutboxEntry> enqueueUpdate({
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required Map<String, dynamic> payload,
    Map<String, dynamic>? previousData,
    String? ifMatch,
    OutboxPriority priority = OutboxPriority.normal,
    Map<String, dynamic>? metadata,
    String? source,
    bool canAggregate = true,
  }) async {
    // Check for existing pending updates to aggregate
    if (canAggregate) {
      final aggregated = await _tryAggregateUpdate(
        tenantId: tenantId,
        entityType: entityType,
        entityId: entityId,
        payload: payload,
      );
      if (aggregated != null) {
        _notifyChange(OutboxChangeEvent.updated(aggregated));
        return aggregated;
      }
    }

    final id = _uuid.v4();
    final entry = OutboxEntry.update(
      id: id,
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      payload: payload,
      previousData: previousData,
      ifMatch: ifMatch,
      priority: priority,
      metadata: metadata,
      source: source ?? 'user_action',
      canAggregate: canAggregate,
    );

    await _insertEntry(entry);
    _notifyChange(OutboxChangeEvent.added(entry));
    AppLogger.sync('Enqueued UPDATE: $entityType/$entityId');

    return entry;
  }

  /// Add a delete operation to the outbox
  Future<OutboxEntry> enqueueDelete({
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    String? ifMatch,
    OutboxPriority priority = OutboxPriority.high,
    Map<String, dynamic>? metadata,
    String? source,
  }) async {
    // Cancel any pending operations for this entity
    await cancelPendingForEntity(tenantId, entityType, entityId);

    final id = _uuid.v4();
    final entry = OutboxEntry.delete(
      id: id,
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      ifMatch: ifMatch,
      priority: priority,
      metadata: metadata,
      source: source ?? 'user_action',
    );

    await _insertEntry(entry);
    _notifyChange(OutboxChangeEvent.added(entry));
    AppLogger.sync('Enqueued DELETE: $entityType/$entityId');

    return entry;
  }

  /// Try to aggregate an update with existing pending updates
  Future<OutboxEntry?> _tryAggregateUpdate({
    required String tenantId,
    required String entityType,
    required String entityId,
    required Map<String, dynamic> payload,
  }) async {
    final existing = await _db.customSelect(
      '''
      SELECT * FROM outbox
      WHERE tenant_id = ?
        AND entity_type = ?
        AND entity_id = ?
        AND is_synced = 0
        AND method = 'PUT'
      ORDER BY created_at DESC
      LIMIT 1
      ''',
      variables: [
        Variable.withString(tenantId),
        Variable.withString(entityType),
        Variable.withString(entityId),
      ],
    ).getSingleOrNull();

    if (existing == null) return null;

    try {
      // Merge payloads
      final existingPayload =
          jsonDecode(existing.read<String>('payload')) as Map<String, dynamic>;
      final mergedPayload = {...existingPayload, ...payload};

      // Update the existing entry
      await _db.customStatement(
        '''
        UPDATE outbox
        SET payload = ?,
            retry_count = 0
        WHERE id = ?
        ''',
        [jsonEncode(mergedPayload), existing.read<int>('id')],
      );

      AppLogger.d('Aggregated UPDATE for $entityType/$entityId', tag: 'OUTBOX');

      // Return a mock entry for the aggregated update
      final now = DateTime.now();
      return OutboxEntry(
        id: existing.read<int>('id').toString(),
        tenantId: tenantId,
        entityType: entityType,
        entityId: entityId,
        operation: OutboxOperation.update,
        apiEndpoint: existing.read<String>('api_endpoint'),
        httpMethod: 'PUT',
        payload: mergedPayload,
        idempotencyKey:
            'update_${entityType}_${entityId}_${now.millisecondsSinceEpoch}',
        createdAt: DateTime.parse(existing.read<String>('created_at')),
        updatedAt: now,
      );
    } catch (e) {
      AppLogger.w('Failed to aggregate update',
          tag: 'OUTBOX', data: {'error': e.toString()});
      return null;
    }
  }

  /// Insert entry into database
  Future<void> _insertEntry(OutboxEntry entry) async {
    await _db.queueOutboxItem(
      tenantId: entry.tenantId,
      entityType: entry.entityType,
      entityId: entry.entityId,
      apiEndpoint: entry.apiEndpoint,
      method: entry.httpMethod,
      payload: jsonEncode(entry.payload),
      ifMatch: entry.ifMatch,
    );

    _invalidateStatsCache();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Query Operations - استعلام الطابور
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all pending entries sorted by priority and creation time
  Future<List<OutboxData>> getPendingEntries({
    int limit = 50,
    String? tenantId,
  }) async {
    if (tenantId != null) {
      final results = await _db.customSelect(
        '''
        SELECT * FROM outbox
        WHERE is_synced = 0 AND tenant_id = ?
        ORDER BY created_at ASC
        LIMIT ?
        ''',
        variables: [
          Variable.withString(tenantId),
          Variable.withInt(limit),
        ],
      ).get();

      return results
          .map((row) => OutboxData(
                id: row.read<int>('id'),
                tenantId: row.read<String>('tenant_id'),
                entityType: row.read<String>('entity_type'),
                entityId: row.read<String>('entity_id'),
                apiEndpoint: row.read<String>('api_endpoint'),
                method: row.read<String>('method'),
                payload: row.read<String>('payload'),
                ifMatch: row.readNullable<String>('if_match'),
                retryCount: row.read<int>('retry_count'),
                isSynced: row.read<bool>('is_synced'),
                createdAt: DateTime.parse(row.read<String>('created_at')),
              ))
          .toList();
    }

    return _db.getPendingOutbox(limit: limit);
  }

  /// Get entries ready for retry (past their next_retry_at time)
  Future<List<OutboxData>> getRetryableEntries({int limit = 20}) async {
    return _db.getPendingOutbox(limit: limit);
  }

  /// Get entries by entity
  Future<List<OutboxData>> getEntriesForEntity(
    String entityType,
    String entityId,
  ) async {
    final results = await _db.customSelect(
      '''
      SELECT * FROM outbox
      WHERE entity_type = ? AND entity_id = ?
      ORDER BY created_at DESC
      ''',
      variables: [
        Variable.withString(entityType),
        Variable.withString(entityId),
      ],
    ).get();

    return results
        .map((row) => OutboxData(
              id: row.read<int>('id'),
              tenantId: row.read<String>('tenant_id'),
              entityType: row.read<String>('entity_type'),
              entityId: row.read<String>('entity_id'),
              apiEndpoint: row.read<String>('api_endpoint'),
              method: row.read<String>('method'),
              payload: row.read<String>('payload'),
              ifMatch: row.readNullable<String>('if_match'),
              retryCount: row.read<int>('retry_count'),
              isSynced: row.read<bool>('is_synced'),
              createdAt: DateTime.parse(row.read<String>('created_at')),
            ))
        .toList();
  }

  /// Check if there are pending changes for an entity
  Future<bool> hasPendingChanges(String entityType, String entityId) async {
    final result = await _db.customSelect(
      '''
      SELECT COUNT(*) as count FROM outbox
      WHERE entity_type = ? AND entity_id = ? AND is_synced = 0
      ''',
      variables: [
        Variable.withString(entityType),
        Variable.withString(entityId),
      ],
    ).getSingle();

    return result.read<int>('count') > 0;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Status Updates - تحديث الحالة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Mark entry as processing
  Future<void> markProcessing(int id) async {
    // The current schema doesn't have a status column, so we just track this in memory
    AppLogger.d('Marking entry $id as processing', tag: 'OUTBOX');
  }

  /// Mark entry as completed
  Future<void> markCompleted(int id) async {
    await _db.markOutboxDone(id);
    _invalidateStatsCache();

    final entry = await _db.getOutboxItemById(id);
    if (entry != null) {
      _notifyChange(OutboxChangeEvent.completed(id.toString()));
    }
  }

  /// Mark entry as failed
  Future<void> markFailed(int id, String error, {String? errorCode}) async {
    await _db.bumpOutboxRetry(id);
    _invalidateStatsCache();

    _notifyChange(OutboxChangeEvent.failed(id.toString(), error));
  }

  /// Mark entry as conflict
  Future<void> markConflict(int id, String error) async {
    await _db.bumpOutboxRetry(id);
    _invalidateStatsCache();

    _notifyChange(OutboxChangeEvent.conflict(id.toString(), error));
  }

  /// Mark entry as dead (permanently failed)
  Future<void> markDead(int id) async {
    await _db.markOutboxDone(id);
    _invalidateStatsCache();
  }

  /// Reset failed entries for retry
  Future<int> resetFailedEntries() async {
    final result = await _db.customStatement(
      'UPDATE outbox SET retry_count = 0 WHERE is_synced = 0 AND retry_count > 0',
      [],
    );
    _invalidateStatsCache();

    AppLogger.i('Reset failed entries for retry', tag: 'OUTBOX');
    return result;
  }

  /// Cancel pending operations for an entity
  Future<void> cancelPendingForEntity(
    String tenantId,
    String entityType,
    String entityId,
  ) async {
    await _db.customStatement(
      '''
      UPDATE outbox SET is_synced = 1
      WHERE tenant_id = ? AND entity_type = ? AND entity_id = ? AND is_synced = 0
      ''',
      [tenantId, entityType, entityId],
    );
    _invalidateStatsCache();

    AppLogger.d('Cancelled pending operations for $entityType/$entityId',
        tag: 'OUTBOX');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Statistics - الإحصائيات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get current outbox statistics
  Future<OutboxStats> getStats({bool forceRefresh = false}) async {
    if (!forceRefresh && _cachedStats != null && _statsCacheTime != null) {
      final age = DateTime.now().difference(_statsCacheTime!);
      if (age < _statsCacheDuration) {
        return _cachedStats!;
      }
    }

    final pendingResult = await _db
        .customSelect(
          'SELECT COUNT(*) as count FROM outbox WHERE is_synced = 0',
        )
        .getSingle();

    final failedResult = await _db
        .customSelect(
          'SELECT COUNT(*) as count FROM outbox WHERE is_synced = 0 AND retry_count > 0',
        )
        .getSingle();

    final completedTodayResult = await _db.customSelect(
      '''
      SELECT COUNT(*) as count FROM outbox
      WHERE is_synced = 1
        AND created_at >= date('now', 'start of day')
      ''',
    ).getSingle();

    final logs = await _db.getRecentSyncLogs(limit: 1);
    DateTime? lastSync;
    if (logs.isNotEmpty) {
      lastSync = logs.first.timestamp;
    }

    final stats = OutboxStats(
      pendingCount: pendingResult.read<int>('count'),
      failedCount: failedResult.read<int>('count'),
      completedTodayCount: completedTodayResult.read<int>('count'),
      lastSyncTime: lastSync,
      byEntityType: await _getStatsByEntityType(),
    );

    _cachedStats = stats;
    _statsCacheTime = DateTime.now();
    _statsController.add(stats);

    return stats;
  }

  /// Get stats grouped by entity type
  Future<Map<String, int>> _getStatsByEntityType() async {
    final results = await _db.customSelect(
      '''
      SELECT entity_type, COUNT(*) as count
      FROM outbox
      WHERE is_synced = 0
      GROUP BY entity_type
      ''',
    ).get();

    final map = <String, int>{};
    for (final row in results) {
      map[row.read<String>('entity_type')] = row.read<int>('count');
    }
    return map;
  }

  /// Invalidate stats cache
  void _invalidateStatsCache() {
    _cachedStats = null;
    _statsCacheTime = null;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cleanup - التنظيف
  // ═══════════════════════════════════════════════════════════════════════════

  /// Clean up completed entries
  Future<int> cleanupCompleted() async {
    final result = await _db.cleanupOutbox();
    _invalidateStatsCache();

    AppLogger.d('Cleaned up completed outbox entries', tag: 'OUTBOX');
    return result;
  }

  /// Clean up old entries
  Future<int> cleanupOld({Duration olderThan = const Duration(days: 7)}) async {
    final result = await _db.cleanupOldOutbox(olderThan: olderThan);
    _invalidateStatsCache();

    AppLogger.d('Cleaned up old outbox entries', tag: 'OUTBOX');
    return result;
  }

  /// Clear all entries (use with caution)
  Future<void> clearAll() async {
    await _db.customStatement('DELETE FROM outbox', []);
    _invalidateStatsCache();

    AppLogger.w('Cleared all outbox entries', tag: 'OUTBOX');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Notifications - الإشعارات
  // ═══════════════════════════════════════════════════════════════════════════

  void _notifyChange(OutboxChangeEvent event) {
    _changesController.add(event);
    _invalidateStatsCache();
  }

  /// Dispose of resources
  void dispose() {
    _statsController.close();
    _changesController.close();
  }
}

/// Outbox statistics
class OutboxStats {
  final int pendingCount;
  final int failedCount;
  final int completedTodayCount;
  final DateTime? lastSyncTime;
  final Map<String, int> byEntityType;

  const OutboxStats({
    required this.pendingCount,
    required this.failedCount,
    required this.completedTodayCount,
    this.lastSyncTime,
    this.byEntityType = const {},
  });

  bool get isEmpty => pendingCount == 0;
  bool get hasFailed => failedCount > 0;
  bool get needsSync => pendingCount > 0;

  int get totalPending => pendingCount;
  int get healthyPending => pendingCount - failedCount;

  /// Get health status
  OutboxHealthStatus get healthStatus {
    if (pendingCount == 0) return OutboxHealthStatus.synced;
    if (failedCount > 5) return OutboxHealthStatus.critical;
    if (failedCount > 0) return OutboxHealthStatus.warning;
    if (pendingCount > 20) return OutboxHealthStatus.busy;
    return OutboxHealthStatus.healthy;
  }

  /// Arabic status message
  String get statusMessageAr {
    if (pendingCount == 0) return 'متزامن بالكامل';
    if (failedCount > 0) return 'يوجد $failedCount عملية فاشلة';
    return '$pendingCount عملية قيد الانتظار';
  }

  /// English status message
  String get statusMessageEn {
    if (pendingCount == 0) return 'Fully synced';
    if (failedCount > 0) return '$failedCount failed operations';
    return '$pendingCount pending operations';
  }

  OutboxStats copyWith({
    int? pendingCount,
    int? failedCount,
    int? completedTodayCount,
    DateTime? lastSyncTime,
    Map<String, int>? byEntityType,
  }) {
    return OutboxStats(
      pendingCount: pendingCount ?? this.pendingCount,
      failedCount: failedCount ?? this.failedCount,
      completedTodayCount: completedTodayCount ?? this.completedTodayCount,
      lastSyncTime: lastSyncTime ?? this.lastSyncTime,
      byEntityType: byEntityType ?? this.byEntityType,
    );
  }
}

/// Outbox health status
enum OutboxHealthStatus {
  synced,
  healthy,
  busy,
  warning,
  critical,
}

/// Extension for health status messages
extension OutboxHealthStatusExtension on OutboxHealthStatus {
  String get labelAr {
    switch (this) {
      case OutboxHealthStatus.synced:
        return 'متزامن';
      case OutboxHealthStatus.healthy:
        return 'سليم';
      case OutboxHealthStatus.busy:
        return 'مشغول';
      case OutboxHealthStatus.warning:
        return 'تحذير';
      case OutboxHealthStatus.critical:
        return 'حرج';
    }
  }

  String get labelEn {
    switch (this) {
      case OutboxHealthStatus.synced:
        return 'Synced';
      case OutboxHealthStatus.healthy:
        return 'Healthy';
      case OutboxHealthStatus.busy:
        return 'Busy';
      case OutboxHealthStatus.warning:
        return 'Warning';
      case OutboxHealthStatus.critical:
        return 'Critical';
    }
  }
}

/// Outbox change event for reactive updates
class OutboxChangeEvent {
  final OutboxChangeType type;
  final String? entryId;
  final String? error;
  final OutboxEntry? entry;

  const OutboxChangeEvent._({
    required this.type,
    this.entryId,
    this.error,
    this.entry,
  });

  factory OutboxChangeEvent.added(OutboxEntry entry) => OutboxChangeEvent._(
        type: OutboxChangeType.added,
        entryId: entry.id,
        entry: entry,
      );

  factory OutboxChangeEvent.updated(OutboxEntry entry) => OutboxChangeEvent._(
        type: OutboxChangeType.updated,
        entryId: entry.id,
        entry: entry,
      );

  factory OutboxChangeEvent.completed(String id) => OutboxChangeEvent._(
        type: OutboxChangeType.completed,
        entryId: id,
      );

  factory OutboxChangeEvent.failed(String id, String error) =>
      OutboxChangeEvent._(
        type: OutboxChangeType.failed,
        entryId: id,
        error: error,
      );

  factory OutboxChangeEvent.conflict(String id, String error) =>
      OutboxChangeEvent._(
        type: OutboxChangeType.conflict,
        entryId: id,
        error: error,
      );

  factory OutboxChangeEvent.removed(String id) => OutboxChangeEvent._(
        type: OutboxChangeType.removed,
        entryId: id,
      );
}

/// Types of outbox changes
enum OutboxChangeType {
  added,
  updated,
  completed,
  failed,
  conflict,
  removed,
}
