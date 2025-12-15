import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';

import '../storage/database.dart';
import '../sync/network_status.dart';
import '../auth/user_context.dart';

/// Sync Worker - عامل المزامنة مع دعم ETag و Conflict Resolution
///
/// يدعم:
/// - If-Match header لتجنب التعارضات
/// - 409 Conflict handling مع تطبيق نسخة السيرفر
/// - SyncEvents للإشعارات
class SyncWorker {
  final AppDatabase _db;
  final NetworkStatus _net;
  final UserContext _auth;
  final Dio _dio;
  final String _baseUrl;

  SyncWorker({
    required AppDatabase db,
    required NetworkStatus net,
    required UserContext auth,
    required String baseUrl,
    Dio? dio,
  })  : _db = db,
        _net = net,
        _auth = auth,
        _baseUrl = baseUrl,
        _dio = dio ?? Dio();

  /// تشغيل المزامنة
  Future<SyncResult> run() async {
    if (!_net.isOnline) {
      await _log('INFO', 'Sync skipped: offline');
      return SyncResult(synced: 0, failed: 0, conflicts: 0);
    }

    final tenantId = _auth.currentUserId;
    final items = await _db.getPendingOutbox();

    int synced = 0;
    int failed = 0;
    int conflicts = 0;

    for (final item in items) {
      final result = await _processItem(item, tenantId);
      switch (result) {
        case _SyncItemResult.success:
          synced++;
          break;
        case _SyncItemResult.conflict:
          conflicts++;
          break;
        case _SyncItemResult.failed:
          failed++;
          break;
      }
    }

    await _log('INFO',
        'Sync completed: $synced synced, $conflicts conflicts, $failed failed');
    return SyncResult(synced: synced, failed: failed, conflicts: conflicts);
  }

  Future<_SyncItemResult> _processItem(OutboxData item, String tenantId) async {
    try {
      // Build request headers
      final headers = <String, dynamic>{
        'Content-Type': 'application/json',
        'X-Tenant-Id': tenantId,
        'X-Client-Updated-At': item.createdAt.toIso8601String(),
      };

      // Add If-Match for field updates if we have an ETag
      if (item.type.startsWith('field_') && item.type.contains('update')) {
        final payload = jsonDecode(item.payload) as Map<String, dynamic>;
        final fieldId = payload['id']?.toString();
        if (fieldId != null) {
          final field = await _db.getFieldById(fieldId);
          if (field?.etag != null && field!.etag!.isNotEmpty) {
            headers['If-Match'] = field.etag!;
          }
        }
      }

      // Determine endpoint and method
      final endpoint = _getEndpoint(item.type);
      final method = _getMethod(item.type);

      final resp = await _dio.request(
        '$_baseUrl$endpoint',
        data: jsonDecode(item.payload),
        options: Options(method: method, headers: headers),
      );

      // Handle ETag from response
      final newEtag = resp.headers.value('etag') ?? resp.headers.value('ETag');
      if (newEtag != null && item.type.startsWith('field_')) {
        final payload = jsonDecode(item.payload) as Map<String, dynamic>;
        final fieldId = payload['id']?.toString();
        if (fieldId != null) {
          await _db.updateFieldWithEtag(
            fieldId: fieldId,
            etag: newEtag,
            serverUpdatedAt: DateTime.now(),
          );
        }
      }

      await _db.markOutboxDone(item.id);
      return _SyncItemResult.success;
    } on DioException catch (e) {
      if (e.response?.statusCode == 409) {
        await _handleConflict(item, e.response?.data, tenantId);
        await _db.markOutboxDone(item.id);
        return _SyncItemResult.conflict;
      }

      if (e.response?.statusCode != null && e.response!.statusCode! >= 500) {
        await _log('ERROR', 'Server error. Will retry later. ${e.message}');
        await _db.bumpOutboxRetry(item.id);
        return _SyncItemResult.failed;
      }

      await _log('ERROR', 'Request error: ${e.message}');
      await _db.markOutboxDone(item.id); // prevent queue lock
      return _SyncItemResult.failed;
    } catch (e) {
      await _log('ERROR', 'Unknown sync error: $e');
      return _SyncItemResult.failed;
    }
  }

  Future<void> _handleConflict(
      OutboxData item, dynamic serverBody, String tenantId) async {
    // Parse server response: { "serverData": {...}, "message": "Conflict" }
    Map<String, dynamic>? serverData;
    if (serverBody is Map<String, dynamic>) {
      final sd = serverBody['serverData'];
      if (sd is Map<String, dynamic>) serverData = sd;
    }

    if (item.type.startsWith('field_') && serverData != null) {
      // Apply server version (Last-Write-Wins from server)
      final fieldId = serverData['id']?.toString();
      if (fieldId != null) {
        await _db.markFieldSynced(fieldId, serverData['remote_id']?.toString());

        // Update with server data
        await (await _db.getFieldById(fieldId))?.let((field) async {
          await _db.upsertFieldsFromServer([serverData!]);
        });
      }
    }

    // Add conflict event for UI notification
    await _db.addSyncEvent(
      tenantId: tenantId,
      type: 'CONFLICT',
      message:
          'تم تطبيق نسخة السيرفر بسبب تعارض في ${_getEntityTypeAr(item.type)}',
      entityType: _getEntityType(item.type),
      entityId: _extractEntityId(item.payload),
    );

    await _log('INFO',
        'Conflict resolved by applying server version for: ${item.type}');
  }

  String _getEndpoint(String type) {
    if (type.startsWith('field_')) return '/api/v1/fields';
    if (type.startsWith('task_')) return '/api/v1/tasks';
    return '/api/v1/sync';
  }

  String _getMethod(String type) {
    if (type.contains('create')) return 'POST';
    if (type.contains('update')) return 'PUT';
    if (type.contains('delete')) return 'DELETE';
    return 'POST';
  }

  String _getEntityType(String type) {
    if (type.startsWith('field_')) return 'field';
    if (type.startsWith('task_')) return 'task';
    return 'unknown';
  }

  String _getEntityTypeAr(String type) {
    if (type.startsWith('field_')) return 'الحقل';
    if (type.startsWith('task_')) return 'المهمة';
    return 'البيانات';
  }

  String? _extractEntityId(String payloadStr) {
    try {
      final payload = jsonDecode(payloadStr) as Map<String, dynamic>;
      return payload['id']?.toString();
    } catch (_) {
      return null;
    }
  }

  Future<void> _log(String level, String message) async {
    await _db.logSync(
        type: 'sync_worker', status: level.toLowerCase(), message: message);
  }
}

enum _SyncItemResult { success, conflict, failed }

/// نتيجة المزامنة
class SyncResult {
  final int synced;
  final int failed;
  final int conflicts;

  SyncResult({
    required this.synced,
    required this.failed,
    required this.conflicts,
  });

  bool get hasConflicts => conflicts > 0;
  bool get isSuccess => failed == 0;

  @override
  String toString() =>
      'SyncResult(synced: $synced, failed: $failed, conflicts: $conflicts)';
}

/// Extension helper
extension _ObjectExtension<T> on T? {
  R? let<R>(R Function(T) block) {
    if (this != null) {
      return block(this as T);
    }
    return null;
  }
}
