import 'dart:async';
import 'dart:convert';
import '../storage/database.dart';
import '../http/api_client.dart';

/// Delta Sync - Incremental sync with version tracking
/// مزامنة تفاضلية - مزامنة تزايدية مع تتبع الإصدارات
class DeltaSync {
  final AppDatabase database;
  final ApiClient apiClient;

  /// Version key for each entity type
  static const String _versionKey = 'sync_version';

  DeltaSync({
    required this.database,
    required this.apiClient,
  });

  /// Get last sync version for entity type
  Future<int> getLastSyncVersion(String entityType) async {
    try {
      final key = '${_versionKey}_$entityType';
      final result = await database.getMetadata(key);
      return result != null ? int.tryParse(result) ?? 0 : 0;
    } catch (e) {
      return 0;
    }
  }

  /// Save sync version for entity type
  Future<void> saveSyncVersion(String entityType, int version) async {
    final key = '${_versionKey}_$entityType';
    await database.setMetadata(key, version.toString());
  }

  /// Fetch delta changes since last sync
  Future<DeltaResult> fetchDelta({
    required String entityType,
    required String endpoint,
    int? sinceVersion,
  }) async {
    final lastVersion = sinceVersion ?? await getLastSyncVersion(entityType);

    try {
      final response = await apiClient.get(
        endpoint,
        queryParameters: {
          'since_version': lastVersion.toString(),
          'include_deleted': 'true',
        },
      );

      if (response is Map<String, dynamic>) {
        final items = (response['data'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final deletedIds = (response['deleted'] as List?)?.cast<String>() ?? [];
        final newVersion = response['version'] as int? ?? lastVersion;

        return DeltaResult(
          items: items,
          deletedIds: deletedIds,
          newVersion: newVersion,
          hasChanges: items.isNotEmpty || deletedIds.isNotEmpty,
        );
      }

      return DeltaResult.empty(lastVersion);
    } catch (e) {
      return DeltaResult.error(lastVersion, e.toString());
    }
  }

  /// Apply delta changes to local database
  Future<ApplyResult> applyDelta({
    required String entityType,
    required DeltaResult delta,
    required Future<void> Function(List<Map<String, dynamic>>) upsertFn,
    required Future<void> Function(List<String>) deleteFn,
  }) async {
    if (!delta.hasChanges) {
      return ApplyResult(
        applied: 0,
        deleted: 0,
        success: true,
      );
    }

    try {
      // Apply upserts
      if (delta.items.isNotEmpty) {
        await upsertFn(delta.items);
      }

      // Apply deletions
      if (delta.deletedIds.isNotEmpty) {
        await deleteFn(delta.deletedIds);
      }

      // Save new version
      await saveSyncVersion(entityType, delta.newVersion);

      return ApplyResult(
        applied: delta.items.length,
        deleted: delta.deletedIds.length,
        success: true,
      );
    } catch (e) {
      return ApplyResult(
        applied: 0,
        deleted: 0,
        success: false,
        error: e.toString(),
      );
    }
  }

  /// Full delta sync for an entity type
  Future<SyncEntityResult> syncEntity({
    required String entityType,
    required String endpoint,
    required Future<void> Function(List<Map<String, dynamic>>) upsertFn,
    required Future<void> Function(List<String>) deleteFn,
  }) async {
    final delta = await fetchDelta(
      entityType: entityType,
      endpoint: endpoint,
    );

    if (delta.error != null) {
      return SyncEntityResult(
        entityType: entityType,
        success: false,
        error: delta.error,
      );
    }

    final result = await applyDelta(
      entityType: entityType,
      delta: delta,
      upsertFn: upsertFn,
      deleteFn: deleteFn,
    );

    return SyncEntityResult(
      entityType: entityType,
      success: result.success,
      applied: result.applied,
      deleted: result.deleted,
      newVersion: delta.newVersion,
      error: result.error,
    );
  }

  /// Reset sync version (force full sync)
  Future<void> resetSyncVersion(String entityType) async {
    await saveSyncVersion(entityType, 0);
  }

  /// Reset all sync versions
  Future<void> resetAllSyncVersions() async {
    for (final entityType in ['field', 'task', 'experiment', 'log', 'sample']) {
      await resetSyncVersion(entityType);
    }
  }
}

/// Delta fetch result
class DeltaResult {
  final List<Map<String, dynamic>> items;
  final List<String> deletedIds;
  final int newVersion;
  final bool hasChanges;
  final String? error;

  DeltaResult({
    required this.items,
    required this.deletedIds,
    required this.newVersion,
    required this.hasChanges,
    this.error,
  });

  factory DeltaResult.empty(int version) => DeltaResult(
        items: [],
        deletedIds: [],
        newVersion: version,
        hasChanges: false,
      );

  factory DeltaResult.error(int version, String error) => DeltaResult(
        items: [],
        deletedIds: [],
        newVersion: version,
        hasChanges: false,
        error: error,
      );
}

/// Apply delta result
class ApplyResult {
  final int applied;
  final int deleted;
  final bool success;
  final String? error;

  ApplyResult({
    required this.applied,
    required this.deleted,
    required this.success,
    this.error,
  });
}

/// Sync entity result
class SyncEntityResult {
  final String entityType;
  final bool success;
  final int applied;
  final int deleted;
  final int? newVersion;
  final String? error;

  SyncEntityResult({
    required this.entityType,
    required this.success,
    this.applied = 0,
    this.deleted = 0,
    this.newVersion,
    this.error,
  });

  Map<String, dynamic> toJson() => {
        'entityType': entityType,
        'success': success,
        'applied': applied,
        'deleted': deleted,
        'newVersion': newVersion,
        'error': error,
      };
}
