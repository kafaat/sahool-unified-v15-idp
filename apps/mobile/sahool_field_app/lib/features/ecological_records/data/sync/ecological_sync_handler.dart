import 'dart:convert';
import 'package:dio/dio.dart';

import '../../../../core/storage/database.dart';
import '../../../../core/http/api_client.dart';

/// معالج مزامنة السجلات البيئية - Ecological Records Sync Handler
///
/// Handles offline-first synchronization for all ecological agriculture records:
/// يدير المزامنة بنمط Offline-First لجميع السجلات الزراعية البيئية:
/// - Biodiversity Records (سجلات التنوع البيولوجي)
/// - Soil Health Records (سجلات صحة التربة)
/// - Water Conservation Records (سجلات الحفاظ على المياه)
/// - Farm Practice Records (سجلات الممارسات الزراعية)
///
/// Features:
/// - Outbox pattern for reliable sync
/// - Automatic retry on failure
/// - Conflict resolution (server-wins strategy)
/// - ETag support for optimistic locking
/// - Batch processing for efficiency
class EcologicalSyncHandler {
  final AppDatabase _db;
  final ApiClient _apiClient;

  EcologicalSyncHandler({
    required AppDatabase db,
    required ApiClient apiClient,
  })  : _db = db,
        _apiClient = apiClient;

  /// تسجيل معالجات المزامنة لكل نوع سجل
  /// Register sync handlers for each ecological record type
  ///
  /// Returns a map of entity types to their sync handler functions
  /// يعيد خريطة من أنواع الكيانات إلى دوال المعالجة الخاصة بها
  Map<String, Future<bool> Function(OutboxData)> get handlers => {
        'biodiversity_record': _syncBiodiversityRecord,
        'soil_health_record': _syncSoilHealthRecord,
        'water_conservation_record': _syncWaterRecord,
        'farm_practice_record': _syncPracticeRecord,
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Biodiversity Records Sync - مزامنة سجلات التنوع البيولوجي
  // ═══════════════════════════════════════════════════════════════════════════

  /// مزامنة سجل التنوع البيولوجي مع الخادم
  /// Sync biodiversity record to server
  Future<bool> _syncBiodiversityRecord(OutboxData item) async {
    try {
      // فك تشفير البيانات | Decode payload
      final payload = jsonDecode(item.payload) as Map<String, dynamic>;
      final recordId = payload['id']?.toString();

      if (recordId == null) {
        await _logError('Biodiversity record missing ID', item);
        return false;
      }

      // إرسال الطلب إلى الخادم | Send request to server
      final response = await _apiClient.post(
        item.apiEndpoint,
        data: payload,
        options: Options(
          headers: _buildHeaders(item),
        ),
      );

      // التحقق من نجاح الطلب | Verify successful response
      if (_isSuccessResponse(response)) {
        // تحديث حالة المزامنة في قاعدة البيانات المحلية
        // Update sync status in local database
        await _db.markBiodiversitySynced(recordId);

        await _logSuccess('Biodiversity record synced', recordId);
        return true;
      }

      return false;
    } on DioException catch (e) {
      return await _handleDioError(e, item, 'biodiversity_record');
    } catch (e) {
      await _logError('Unknown error syncing biodiversity record: $e', item);
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Soil Health Records Sync - مزامنة سجلات صحة التربة
  // ═══════════════════════════════════════════════════════════════════════════

  /// مزامنة سجل صحة التربة مع الخادم
  /// Sync soil health record to server
  Future<bool> _syncSoilHealthRecord(OutboxData item) async {
    try {
      // فك تشفير البيانات | Decode payload
      final payload = jsonDecode(item.payload) as Map<String, dynamic>;
      final recordId = payload['id']?.toString();

      if (recordId == null) {
        await _logError('Soil health record missing ID', item);
        return false;
      }

      // إرسال الطلب إلى الخادم | Send request to server
      final response = await _apiClient.post(
        item.apiEndpoint,
        data: payload,
        options: Options(
          headers: _buildHeaders(item),
        ),
      );

      // التحقق من نجاح الطلب | Verify successful response
      if (_isSuccessResponse(response)) {
        // تحديث حالة المزامنة في قاعدة البيانات المحلية
        // Update sync status in local database
        await _db.markSoilHealthSynced(recordId);

        await _logSuccess('Soil health record synced', recordId);
        return true;
      }

      return false;
    } on DioException catch (e) {
      return await _handleDioError(e, item, 'soil_health_record');
    } catch (e) {
      await _logError('Unknown error syncing soil health record: $e', item);
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Conservation Records Sync - مزامنة سجلات الحفاظ على المياه
  // ═══════════════════════════════════════════════════════════════════════════

  /// مزامنة سجل الحفاظ على المياه مع الخادم
  /// Sync water conservation record to server
  Future<bool> _syncWaterRecord(OutboxData item) async {
    try {
      // فك تشفير البيانات | Decode payload
      final payload = jsonDecode(item.payload) as Map<String, dynamic>;
      final recordId = payload['id']?.toString();

      if (recordId == null) {
        await _logError('Water conservation record missing ID', item);
        return false;
      }

      // إرسال الطلب إلى الخادم | Send request to server
      final response = await _apiClient.post(
        item.apiEndpoint,
        data: payload,
        options: Options(
          headers: _buildHeaders(item),
        ),
      );

      // التحقق من نجاح الطلب | Verify successful response
      if (_isSuccessResponse(response)) {
        // تحديث حالة المزامنة في قاعدة البيانات المحلية
        // Update sync status in local database
        await _db.markWaterConservationSynced(recordId);

        await _logSuccess('Water conservation record synced', recordId);
        return true;
      }

      return false;
    } on DioException catch (e) {
      return await _handleDioError(e, item, 'water_conservation_record');
    } catch (e) {
      await _logError('Unknown error syncing water conservation record: $e', item);
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Farm Practice Records Sync - مزامنة سجلات الممارسات الزراعية
  // ═══════════════════════════════════════════════════════════════════════════

  /// مزامنة سجل الممارسات الزراعية مع الخادم
  /// Sync farm practice record to server
  Future<bool> _syncPracticeRecord(OutboxData item) async {
    try {
      // فك تشفير البيانات | Decode payload
      final payload = jsonDecode(item.payload) as Map<String, dynamic>;
      final recordId = payload['id']?.toString();

      if (recordId == null) {
        await _logError('Farm practice record missing ID', item);
        return false;
      }

      // إرسال الطلب إلى الخادم | Send request to server
      final response = await _apiClient.post(
        item.apiEndpoint,
        data: payload,
        options: Options(
          headers: _buildHeaders(item),
        ),
      );

      // التحقق من نجاح الطلب | Verify successful response
      if (_isSuccessResponse(response)) {
        // تحديث حالة المزامنة في قاعدة البيانات المحلية
        // Update sync status in local database
        await _db.markPracticeRecordSynced(recordId);

        await _logSuccess('Farm practice record synced', recordId);
        return true;
      }

      return false;
    } on DioException catch (e) {
      return await _handleDioError(e, item, 'farm_practice_record');
    } catch (e) {
      await _logError('Unknown error syncing farm practice record: $e', item);
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods - الطرق المساعدة
  // ═══════════════════════════════════════════════════════════════════════════

  /// بناء رؤوس الطلب مع دعم ETag
  /// Build request headers with ETag support
  Map<String, dynamic> _buildHeaders(OutboxData item) {
    final headers = <String, dynamic>{
      'Content-Type': 'application/json',
      'X-Tenant-Id': item.tenantId,
      'X-Client-Updated-At': item.createdAt.toIso8601String(),
    };

    // إضافة If-Match للتحديثات (قفل متفائل)
    // Add If-Match for updates (optimistic locking)
    if (item.ifMatch != null && item.ifMatch!.isNotEmpty) {
      headers['If-Match'] = item.ifMatch!;
    }

    return headers;
  }

  /// التحقق من نجاح الاستجابة
  /// Check if response indicates success
  bool _isSuccessResponse(dynamic response) {
    if (response is Response) {
      return response.statusCode == 200 || response.statusCode == 201;
    }
    return false;
  }

  /// معالجة أخطاء Dio
  /// Handle Dio exceptions (HTTP errors)
  Future<bool> _handleDioError(
    DioException e,
    OutboxData item,
    String recordType,
  ) async {
    final statusCode = e.response?.statusCode;

    // معالجة التعارض 409 - تطبيق نسخة الخادم
    // Handle 409 Conflict - apply server version
    if (statusCode == 409) {
      await _handleConflict(item, e.response?.data, recordType);
      return true; // عتبر نجاح لأننا حللنا التعارض | Consider success as we resolved conflict
    }

    // خطأ من جانب الخادم - إعادة المحاولة لاحقاً
    // Server error - retry later
    if (statusCode != null && statusCode >= 500) {
      await _logError(
        'Server error (HTTP $statusCode). Will retry later.',
        item,
      );
      return false; // سيتم إعادة المحاولة | Will be retried
    }

    // خطأ من جانب العميل - لا داعي لإعادة المحاولة
    // Client error - no need to retry
    if (statusCode != null && statusCode >= 400 && statusCode < 500) {
      await _logError(
        'Client error (HTTP $statusCode): ${e.message}',
        item,
      );
      return false;
    }

    // أخطاء الشبكة - إعادة المحاولة
    // Network errors - retry
    await _logError('Network error: ${e.message}', item);
    return false;
  }

  /// معالجة التعارض - تطبيق استراتيجية "الخادم يفوز"
  /// Handle conflict - apply "server wins" strategy
  Future<void> _handleConflict(
    OutboxData item,
    dynamic serverResponse,
    String recordType,
  ) async {
    // تحليل استجابة الخادم
    // Parse server response
    Map<String, dynamic>? serverData;
    if (serverResponse is Map<String, dynamic>) {
      serverData = serverResponse['serverData'] as Map<String, dynamic>?;
    }

    if (serverData != null) {
      // تطبيق بيانات الخادم على قاعدة البيانات المحلية
      // Apply server data to local database
      await _applyServerVersion(recordType, serverData);
    }

    // إضافة حدث مزامنة للإشعار
    // Add sync event for UI notification
    await _db.addSyncEvent(
      tenantId: item.tenantId,
      type: 'CONFLICT',
      message: 'تم تطبيق نسخة السيرفر بسبب تعارض في ${_getEntityTypeAr(recordType)}',
      entityType: recordType,
      entityId: item.entityId,
    );

    await _db.logSync(
      type: 'conflict',
      status: 'resolved',
      message: 'Conflict resolved by applying server version for: $recordType/${item.entityId}',
    );
  }

  /// تطبيق النسخة من الخادم على قاعدة البيانات المحلية
  /// Apply server version to local database
  Future<void> _applyServerVersion(
    String recordType,
    Map<String, dynamic> serverData,
  ) async {
    switch (recordType) {
      case 'biodiversity_record':
        await _db.upsertBiodiversityRecordsFromServer([serverData]);
        break;
      case 'soil_health_record':
        await _db.upsertSoilHealthRecordsFromServer([serverData]);
        break;
      case 'water_conservation_record':
        await _db.upsertWaterConservationRecordsFromServer([serverData]);
        break;
      case 'farm_practice_record':
        await _db.upsertPracticeRecordsFromServer([serverData]);
        break;
      default:
        await _db.logSync(
          type: 'conflict',
          status: 'error',
          message: 'Unknown record type: $recordType',
        );
    }
  }

  /// الحصول على اسم الكيان بالعربية
  /// Get entity type name in Arabic
  String _getEntityTypeAr(String type) {
    switch (type) {
      case 'biodiversity_record':
        return 'سجل التنوع البيولوجي';
      case 'soil_health_record':
        return 'سجل صحة التربة';
      case 'water_conservation_record':
        return 'سجل الحفاظ على المياه';
      case 'farm_practice_record':
        return 'سجل الممارسات الزراعية';
      default:
        return 'السجل البيئي';
    }
  }

  /// تسجيل نجاح العملية
  /// Log successful operation
  Future<void> _logSuccess(String message, String recordId) async {
    await _db.logSync(
      type: 'ecological_sync',
      status: 'success',
      message: '$message: $recordId',
    );
    print('✅ $message: $recordId');
  }

  /// تسجيل خطأ في العملية
  /// Log error
  Future<void> _logError(String message, OutboxData item) async {
    await _db.logSync(
      type: 'ecological_sync',
      status: 'error',
      message: '$message - Item: ${item.entityType}/${item.entityId}',
    );
    print('❌ $message');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Batch Sync Operations - عمليات المزامنة الجماعية
  // ═══════════════════════════════════════════════════════════════════════════

  /// مزامنة جميع السجلات البيئية المعلقة
  /// Sync all pending ecological records
  ///
  /// Returns statistics about the sync operation
  /// يعيد إحصائيات حول عملية المزامنة
  Future<EcologicalSyncResult> syncAllPending({
    int batchSize = 50,
  }) async {
    int synced = 0;
    int failed = 0;
    int conflicts = 0;

    // الحصول على جميع العناصر المعلقة من صندوق الإرسال
    // Get all pending items from outbox
    final pendingItems = await _db.getPendingOutbox(limit: batchSize);

    // تصفية السجلات البيئية فقط
    // Filter ecological records only
    final ecologicalItems = pendingItems.where((item) {
      return handlers.containsKey(item.entityType);
    }).toList();

    print('🔄 Found ${ecologicalItems.length} pending ecological records to sync');

    // معالجة كل عنصر
    // Process each item
    for (final item in ecologicalItems) {
      final handler = handlers[item.entityType];
      if (handler == null) continue;

      try {
        final success = await handler(item);
        if (success) {
          // وضع علامة كمنتهي في صندوق الإرسال
          // Mark as done in outbox
          await _db.markOutboxDone(item.id);
          synced++;
        } else {
          // زيادة عداد إعادة المحاولة
          // Increment retry counter
          await _db.bumpOutboxRetry(item.id);
          failed++;
        }
      } catch (e) {
        await _logError('Unexpected error: $e', item);
        await _db.bumpOutboxRetry(item.id);
        failed++;
      }
    }

    // تسجيل النتائج
    // Log results
    await _db.logSync(
      type: 'ecological_batch_sync',
      status: synced > 0 ? 'success' : 'partial',
      message: 'Synced: $synced, Failed: $failed, Conflicts: $conflicts',
    );

    return EcologicalSyncResult(
      synced: synced,
      failed: failed,
      conflicts: conflicts,
      totalProcessed: synced + failed + conflicts,
    );
  }

  /// سحب السجلات البيئية من الخادم
  /// Pull ecological records from server
  Future<void> pullFromServer(String tenantId) async {
    try {
      // سحب سجلات التنوع البيولوجي
      // Pull biodiversity records
      final biodiversityData = await _apiClient.get(
        '/api/v1/ecological/biodiversity',
        queryParameters: {'tenant_id': tenantId},
      );
      if (biodiversityData is List) {
        await _db.upsertBiodiversityRecordsFromServer(
          biodiversityData.cast<Map<String, dynamic>>(),
        );
      }

      // سحب سجلات صحة التربة
      // Pull soil health records
      final soilHealthData = await _apiClient.get(
        '/api/v1/ecological/soil-health',
        queryParameters: {'tenant_id': tenantId},
      );
      if (soilHealthData is List) {
        await _db.upsertSoilHealthRecordsFromServer(
          soilHealthData.cast<Map<String, dynamic>>(),
        );
      }

      // سحب سجلات المياه
      // Pull water conservation records
      final waterData = await _apiClient.get(
        '/api/v1/ecological/water-conservation',
        queryParameters: {'tenant_id': tenantId},
      );
      if (waterData is List) {
        await _db.upsertWaterConservationRecordsFromServer(
          waterData.cast<Map<String, dynamic>>(),
        );
      }

      // سحب سجلات الممارسات
      // Pull practice records
      final practiceData = await _apiClient.get(
        '/api/v1/ecological/practices',
        queryParameters: {'tenant_id': tenantId},
      );
      if (practiceData is List) {
        await _db.upsertPracticeRecordsFromServer(
          practiceData.cast<Map<String, dynamic>>(),
        );
      }

      await _db.logSync(
        type: 'ecological_pull',
        status: 'success',
        message: 'Successfully pulled ecological records from server',
      );
    } catch (e) {
      await _db.logSync(
        type: 'ecological_pull',
        status: 'error',
        message: 'Failed to pull ecological records: $e',
      );
      rethrow;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Sync Result Model - نموذج نتيجة المزامنة
// ═══════════════════════════════════════════════════════════════════════════

/// نتيجة عملية مزامنة السجلات البيئية
/// Result of ecological records sync operation
class EcologicalSyncResult {
  /// عدد السجلات المتزامنة بنجاح
  /// Number of records successfully synced
  final int synced;

  /// عدد السجلات التي فشلت
  /// Number of records that failed
  final int failed;

  /// عدد التعارضات التي تم حلها
  /// Number of conflicts resolved
  final int conflicts;

  /// إجمالي السجلات المعالجة
  /// Total records processed
  final int totalProcessed;

  EcologicalSyncResult({
    required this.synced,
    required this.failed,
    required this.conflicts,
    required this.totalProcessed,
  });

  /// هل العملية ناجحة تماماً؟
  /// Is the operation completely successful?
  bool get isSuccess => failed == 0 && totalProcessed > 0;

  /// هل هناك تعارضات؟
  /// Are there any conflicts?
  bool get hasConflicts => conflicts > 0;

  /// رسالة الحالة بالعربية
  /// Status message in Arabic
  String get statusMessageAr {
    if (isSuccess) {
      return 'تمت مزامنة $synced سجل بنجاح';
    } else if (totalProcessed == 0) {
      return 'لا توجد سجلات للمزامنة';
    } else {
      return 'تمت مزامنة $synced، فشل $failed، تعارضات $conflicts';
    }
  }

  /// رسالة الحالة بالإنجليزية
  /// Status message in English
  String get statusMessageEn {
    if (isSuccess) {
      return 'Successfully synced $synced records';
    } else if (totalProcessed == 0) {
      return 'No records to sync';
    } else {
      return 'Synced $synced, Failed $failed, Conflicts $conflicts';
    }
  }

  @override
  String toString() =>
      'EcologicalSyncResult(synced: $synced, failed: $failed, conflicts: $conflicts, total: $totalProcessed)';
}
