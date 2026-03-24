import 'dart:convert';
import 'package:dio/dio.dart';

import '../storage/database.dart';
import '../sync/network_status.dart';
import '../auth/user_context.dart';
import '../config/api_config.dart';

/// Sync Worker - عامل المزامنة مع دعم ETag و Conflict Resolution
///
/// يدعم:
/// - If-Match header لتجنب التعارضات
/// - 409 Conflict handling مع تطبيق نسخة السيرفر
/// - SyncEvents للإشعارات
/// - Timeout مناسب للمناطق النائية
/// - Retry مع exponential backoff
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
    String? baseUrl,
    Dio? dio,
  })  : _db = db,
        _net = net,
        _auth = auth,
        _baseUrl = baseUrl ?? ApiConfig.effectiveBaseUrl,
        _dio = dio ?? _createDio();

  /// Create Dio instance with proper configuration
  static Dio _createDio() {
    return Dio(BaseOptions(
      connectTimeout: ApiConfig.connectTimeout,
      sendTimeout: ApiConfig.sendTimeout,
      receiveTimeout: ApiConfig.receiveTimeout,
      headers: ApiConfig.defaultHeaders,
    ));
  }

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
      if (item.entityType == 'field' && item.method == 'PUT') {
        final payload = jsonDecode(item.payload) as Map<String, dynamic>;
        final fieldId = payload['id']?.toString();
        if (fieldId != null) {
          final field = await _db.getFieldById(fieldId);
          if (field?.etag != null && field!.etag!.isNotEmpty) {
            headers['If-Match'] = field.etag;
          }
        }
      }

      // Determine endpoint and method
      final endpoint = item.apiEndpoint;
      final method = item.method;

      final resp = await _dio.request<Map<String, dynamic>>(
        '$_baseUrl$endpoint',
        data: jsonDecode(item.payload),
        options: Options(method: method, headers: headers),
      );

      // Handle ETag from response
      final newEtag = resp.headers.value('etag') ?? resp.headers.value('ETag');
      if (newEtag != null && item.entityType == 'field') {
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

    if (item.entityType == 'field' && serverData != null) {
      // Apply server version (Last-Write-Wins from server)
      final fieldId = serverData['id']?.toString();
      if (fieldId != null) {
        await _db.markFieldSynced(fieldId, serverData['remote_id']?.toString());

        // Apply server data (upsert handles both existing and new fields)
        await _db.upsertFieldsFromServer([serverData]);
      }
    }

    // Add conflict event for UI notification
    await _db.addSyncEvent(
      tenantId: tenantId,
      type: 'CONFLICT',
      message:
          'تم تطبيق نسخة السيرفر بسبب تعارض في ${_getEntityTypeAr(item.entityType)}',
      entityType: item.entityType,
      entityId: _extractEntityId(item.payload),
    );

    await _log('INFO',
        'Conflict resolved by applying server version for: ${item.entityType}');
  }

  String _getEntityTypeAr(String entityType) {
    switch (entityType) {
      case 'field':
        return 'الحقل';
      case 'task':
        return 'المهمة';
      default:
        return 'البيانات';
    }
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

