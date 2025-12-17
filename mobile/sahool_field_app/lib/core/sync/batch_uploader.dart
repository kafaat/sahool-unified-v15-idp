import 'dart:async';
import 'dart:convert';
import '../storage/database.dart';
import '../http/api_client.dart';

/// Batch Uploader - Optimized batch upload for offline changes
/// رافع الدفعات - رفع مُحسَّن للتغييرات غير المتصلة
class BatchUploader {
  final AppDatabase database;
  final ApiClient apiClient;

  /// Maximum items per batch
  static const int maxBatchSize = 25;

  /// Maximum concurrent batches
  static const int maxConcurrentBatches = 3;

  BatchUploader({
    required this.database,
    required this.apiClient,
  });

  /// Process outbox in batches by entity type
  Future<BatchUploadResult> uploadBatched() async {
    final pending = await database.getPendingOutbox(limit: 100);

    if (pending.isEmpty) {
      return BatchUploadResult.empty();
    }

    // Group by entity type for batching
    final grouped = _groupByEntityType(pending);
    final results = <String, EntityBatchResult>{};

    // Process each entity type
    for (final entry in grouped.entries) {
      final entityType = entry.key;
      final items = entry.value;

      final result = await _processBatch(entityType, items);
      results[entityType] = result;
    }

    return BatchUploadResult(
      totalProcessed: results.values.fold(0, (sum, r) => sum + r.processed),
      totalFailed: results.values.fold(0, (sum, r) => sum + r.failed),
      totalConflicts: results.values.fold(0, (sum, r) => sum + r.conflicts),
      entityResults: results,
    );
  }

  /// Group outbox items by entity type
  Map<String, List<OutboxData>> _groupByEntityType(List<OutboxData> items) {
    final grouped = <String, List<OutboxData>>{};

    for (final item in items) {
      final type = item.entityType;
      grouped.putIfAbsent(type, () => []);
      grouped[type]!.add(item);
    }

    return grouped;
  }

  /// Process a batch of items for single entity type
  Future<EntityBatchResult> _processBatch(
    String entityType,
    List<OutboxData> items,
  ) async {
    int processed = 0;
    int failed = 0;
    int conflicts = 0;

    // Split into chunks
    final chunks = _splitIntoChunks(items, maxBatchSize);

    for (final chunk in chunks) {
      // Check if entity type supports batch API
      if (_supportsBatchApi(entityType)) {
        final result = await _uploadBatch(entityType, chunk);
        processed += result.processed;
        failed += result.failed;
        conflicts += result.conflicts;
      } else {
        // Fall back to individual upload
        for (final item in chunk) {
          final result = await _uploadSingle(item);
          if (result == _UploadResult.success) {
            processed++;
          } else if (result == _UploadResult.conflict) {
            conflicts++;
            processed++; // Count as processed (server wins)
          } else {
            failed++;
          }
        }
      }
    }

    return EntityBatchResult(
      entityType: entityType,
      processed: processed,
      failed: failed,
      conflicts: conflicts,
    );
  }

  /// Check if entity type supports batch API
  bool _supportsBatchApi(String entityType) {
    return ['task', 'log', 'sample'].contains(entityType);
  }

  /// Upload batch to batch API endpoint
  Future<_BatchResult> _uploadBatch(
    String entityType,
    List<OutboxData> items,
  ) async {
    try {
      final batchPayload = items.map((item) {
        final payload = jsonDecode(item.payload) as Map<String, dynamic>;
        return {
          'id': item.entityId,
          'method': item.method,
          'data': payload,
          'ifMatch': item.ifMatch,
        };
      }).toList();

      final response = await apiClient.post(
        '/batch/$entityType',
        {'items': batchPayload},
      );

      // Parse batch response
      if (response is Map<String, dynamic>) {
        final results = response['results'] as List? ?? [];
        int processed = 0;
        int conflicts = 0;
        int failed = 0;

        for (int i = 0; i < results.length && i < items.length; i++) {
          final result = results[i] as Map<String, dynamic>;
          final status = result['status'] as String?;

          if (status == 'success') {
            await database.markOutboxDone(items[i].id);
            processed++;
          } else if (status == 'conflict') {
            await database.markOutboxDone(items[i].id);
            await _logConflict(items[i]);
            conflicts++;
          } else {
            await database.bumpOutboxRetry(items[i].id);
            failed++;
          }
        }

        return _BatchResult(
          processed: processed,
          conflicts: conflicts,
          failed: failed,
        );
      }

      return _BatchResult(processed: 0, conflicts: 0, failed: items.length);
    } catch (e) {
      // Mark all as retry on batch failure
      for (final item in items) {
        await database.bumpOutboxRetry(item.id);
      }
      return _BatchResult(processed: 0, conflicts: 0, failed: items.length);
    }
  }

  /// Upload single item
  Future<_UploadResult> _uploadSingle(OutboxData item) async {
    try {
      final payload = jsonDecode(item.payload) as Map<String, dynamic>;
      final headers = item.ifMatch != null ? {'If-Match': item.ifMatch!} : null;

      switch (item.method.toUpperCase()) {
        case 'POST':
          await apiClient.post(item.apiEndpoint, payload, headers: headers);
          break;
        case 'PUT':
          await apiClient.put(item.apiEndpoint, payload, headers: headers);
          break;
        case 'DELETE':
          await apiClient.delete(item.apiEndpoint, headers: headers);
          break;
        default:
          await apiClient.post(item.apiEndpoint, payload, headers: headers);
      }

      await database.markOutboxDone(item.id);
      return _UploadResult.success;
    } catch (e) {
      if (e.toString().contains('409') || e.toString().contains('Conflict')) {
        await database.markOutboxDone(item.id);
        await _logConflict(item);
        return _UploadResult.conflict;
      }

      await database.bumpOutboxRetry(item.id);
      return _UploadResult.failed;
    }
  }

  /// Log conflict for UI notification
  Future<void> _logConflict(OutboxData item) async {
    await database.addSyncEvent(
      tenantId: item.tenantId,
      type: 'CONFLICT',
      message: 'تعارض في ${_getEntityTypeAr(item.entityType)} - تم تطبيق نسخة السيرفر',
      entityType: item.entityType,
      entityId: item.entityId,
    );
  }

  /// Get Arabic entity type name
  String _getEntityTypeAr(String type) {
    const names = {
      'field': 'الحقل',
      'task': 'المهمة',
      'experiment': 'التجربة',
      'log': 'السجل',
      'sample': 'العينة',
    };
    return names[type] ?? 'البيانات';
  }

  /// Split list into chunks
  List<List<T>> _splitIntoChunks<T>(List<T> list, int chunkSize) {
    final chunks = <List<T>>[];
    for (int i = 0; i < list.length; i += chunkSize) {
      final end = (i + chunkSize < list.length) ? i + chunkSize : list.length;
      chunks.add(list.sublist(i, end));
    }
    return chunks;
  }
}

/// Batch upload result
class BatchUploadResult {
  final int totalProcessed;
  final int totalFailed;
  final int totalConflicts;
  final Map<String, EntityBatchResult> entityResults;

  BatchUploadResult({
    required this.totalProcessed,
    required this.totalFailed,
    required this.totalConflicts,
    required this.entityResults,
  });

  factory BatchUploadResult.empty() => BatchUploadResult(
        totalProcessed: 0,
        totalFailed: 0,
        totalConflicts: 0,
        entityResults: {},
      );

  bool get hasFailures => totalFailed > 0;
  bool get hasConflicts => totalConflicts > 0;
  bool get isEmpty => totalProcessed == 0 && totalFailed == 0;
}

/// Entity batch result
class EntityBatchResult {
  final String entityType;
  final int processed;
  final int failed;
  final int conflicts;

  EntityBatchResult({
    required this.entityType,
    required this.processed,
    required this.failed,
    required this.conflicts,
  });
}

/// Internal batch result
class _BatchResult {
  final int processed;
  final int conflicts;
  final int failed;

  _BatchResult({
    required this.processed,
    required this.conflicts,
    required this.failed,
  });
}

/// Internal upload result
enum _UploadResult { success, conflict, failed }
