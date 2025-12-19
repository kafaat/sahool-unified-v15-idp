import 'package:isar/isar.dart';

part 'local_log.g.dart';

/// Research Daily Log - Isar Collection
/// السجل اليومي للبحث - مجموعة Isar
///
/// Stores research logs locally for offline-first operation.
/// يخزن سجلات البحث محليًا للعمل بدون اتصال.
@collection
class LocalResearchLog {
  Id id = Isar.autoIncrement;

  /// Local offline ID for sync tracking
  /// معرف محلي لتتبع المزامنة
  @Index(unique: true)
  late String offlineId;

  /// Server ID (populated after sync)
  /// معرف الخادم (يتم ملؤه بعد المزامنة)
  String? serverId;

  /// Experiment ID
  /// معرف التجربة
  @Index()
  late String experimentId;

  /// Plot ID (optional)
  /// معرف القطعة (اختياري)
  String? plotId;

  /// Treatment ID (optional)
  /// معرف المعاملة (اختياري)
  String? treatmentId;

  /// Log date
  /// تاريخ السجل
  @Index()
  late DateTime logDate;

  /// Log time (HH:MM:SS format)
  /// وقت السجل
  String? logTime;

  /// Category: observation, measurement, treatment, harvest, weather, pest, other
  /// التصنيف
  @Index()
  late String category;

  /// Title (required)
  /// العنوان
  late String title;

  /// Arabic title
  /// العنوان بالعربية
  String? titleAr;

  /// Notes
  /// الملاحظات
  String? notes;

  /// Arabic notes
  /// الملاحظات بالعربية
  String? notesAr;

  /// Measurements as JSON string
  /// القياسات كنص JSON
  String? measurementsJson;

  /// Weather conditions as JSON string
  /// الظروف الجوية كنص JSON
  String? weatherConditionsJson;

  /// Photo paths (local paths)
  /// مسارات الصور المحلية
  List<String> localPhotoPaths = [];

  /// Uploaded photo URLs (after sync)
  /// روابط الصور المرفوعة
  List<String> uploadedPhotoUrls = [];

  /// Attachment paths (local)
  /// مسارات المرفقات المحلية
  List<String> localAttachmentPaths = [];

  /// Uploaded attachment URLs
  /// روابط المرفقات المرفوعة
  List<String> uploadedAttachmentUrls = [];

  /// Recorded by user ID
  /// سُجل بواسطة
  late String recordedBy;

  /// Device ID
  /// معرف الجهاز
  String? deviceId;

  /// Data hash for integrity verification
  /// تجزئة البيانات للتحقق من السلامة
  String? hash;

  /// Latitude of recording location
  /// خط العرض
  double? latitude;

  /// Longitude of recording location
  /// خط الطول
  double? longitude;

  /// Sync status: pending, syncing, synced, failed
  /// حالة المزامنة
  @Index()
  @Enumerated(EnumType.name)
  late SyncStatus syncStatus;

  /// Last sync attempt timestamp
  /// آخر محاولة مزامنة
  DateTime? lastSyncAttempt;

  /// Sync error message (if any)
  /// رسالة خطأ المزامنة
  String? syncError;

  /// Number of sync attempts
  /// عدد محاولات المزامنة
  int syncAttempts = 0;

  /// Created at timestamp
  /// تاريخ الإنشاء
  late DateTime createdAt;

  /// Updated at timestamp
  /// تاريخ التحديث
  late DateTime updatedAt;

  /// Constructor with defaults
  LocalResearchLog() {
    createdAt = DateTime.now();
    updatedAt = DateTime.now();
    syncStatus = SyncStatus.pending;
  }

  /// Factory constructor for creating new log
  factory LocalResearchLog.create({
    required String experimentId,
    required DateTime logDate,
    required String category,
    required String title,
    required String recordedBy,
    String? plotId,
    String? treatmentId,
    String? logTime,
    String? titleAr,
    String? notes,
    String? notesAr,
    Map<String, dynamic>? measurements,
    Map<String, dynamic>? weatherConditions,
    List<String>? localPhotoPaths,
    String? deviceId,
    double? latitude,
    double? longitude,
  }) {
    final log = LocalResearchLog()
      ..offlineId = _generateOfflineId(deviceId ?? 'unknown')
      ..experimentId = experimentId
      ..plotId = plotId
      ..treatmentId = treatmentId
      ..logDate = logDate
      ..logTime = logTime
      ..category = category
      ..title = title
      ..titleAr = titleAr
      ..notes = notes
      ..notesAr = notesAr
      ..measurementsJson = measurements != null ? _encodeJson(measurements) : null
      ..weatherConditionsJson = weatherConditions != null ? _encodeJson(weatherConditions) : null
      ..localPhotoPaths = localPhotoPaths ?? []
      ..recordedBy = recordedBy
      ..deviceId = deviceId
      ..latitude = latitude
      ..longitude = longitude;

    // Generate data hash
    log.hash = _generateHash(log);

    return log;
  }

  /// Convert to API payload for sync
  /// تحويل إلى حمولة API للمزامنة
  Map<String, dynamic> toSyncPayload() {
    return {
      'offlineId': offlineId,
      'experimentId': experimentId,
      'plotId': plotId,
      'treatmentId': treatmentId,
      'logDate': logDate.toIso8601String().split('T')[0],
      'logTime': logTime,
      'category': category,
      'title': title,
      'titleAr': titleAr,
      'notes': notes,
      'notesAr': notesAr,
      'measurements': measurementsJson != null ? _decodeJson(measurementsJson!) : {},
      'weatherConditions': weatherConditionsJson != null ? _decodeJson(weatherConditionsJson!) : {},
      'photos': uploadedPhotoUrls,
      'attachments': uploadedAttachmentUrls,
      'deviceId': deviceId,
      if (latitude != null && longitude != null) 'location': {'lat': latitude, 'lng': longitude},
    };
  }

  /// Mark as synced with server ID
  /// تحديد كمتزامن مع معرف الخادم
  void markAsSynced(String serverIdValue) {
    serverId = serverIdValue;
    syncStatus = SyncStatus.synced;
    syncError = null;
    updatedAt = DateTime.now();
  }

  /// Mark sync as failed
  /// تحديد المزامنة كفاشلة
  void markSyncFailed(String error) {
    syncStatus = SyncStatus.failed;
    syncError = error;
    syncAttempts++;
    lastSyncAttempt = DateTime.now();
    updatedAt = DateTime.now();
  }

  /// Check if should retry sync
  /// التحقق من إمكانية إعادة المحاولة
  bool get shouldRetrySync => syncAttempts < 5 && syncStatus == SyncStatus.failed;

  static String _generateOfflineId(String deviceId) {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final random = DateTime.now().microsecond.toString().padLeft(6, '0');
    return '${deviceId}_${timestamp}_$random';
  }

  static String _generateHash(LocalResearchLog log) {
    final data = [
      log.experimentId,
      log.plotId ?? '',
      log.logDate.toIso8601String(),
      log.category,
      log.notes ?? '',
      log.measurementsJson ?? '{}',
      log.recordedBy,
    ].join('|');

    // Simple hash for now - in production use crypto
    var hash = 0;
    for (var i = 0; i < data.length; i++) {
      hash = ((hash << 5) - hash + data.codeUnitAt(i)) & 0xFFFFFFFF;
    }
    return hash.toRadixString(16).padLeft(16, '0');
  }

  static String _encodeJson(Map<String, dynamic> data) {
    // Simple JSON encoding - import 'dart:convert' in actual implementation
    return data.toString();
  }

  static Map<String, dynamic> _decodeJson(String json) {
    // Placeholder - use jsonDecode in actual implementation
    return {};
  }
}

/// Sync status enumeration
/// حالات المزامنة
enum SyncStatus {
  pending,
  syncing,
  synced,
  failed,
}

/// Research Log Repository for Isar
/// مستودع سجلات البحث لـ Isar
class LocalResearchLogRepository {
  final Isar _isar;

  LocalResearchLogRepository(this._isar);

  /// Save a new log
  /// حفظ سجل جديد
  Future<int> save(LocalResearchLog log) async {
    return _isar.writeTxn(() => _isar.localResearchLogs.put(log));
  }

  /// Get all pending sync logs
  /// الحصول على السجلات المعلقة للمزامنة
  Future<List<LocalResearchLog>> getPendingSync() {
    return _isar.localResearchLogs
        .filter()
        .syncStatusEqualTo(SyncStatus.pending)
        .or()
        .group((q) => q
            .syncStatusEqualTo(SyncStatus.failed)
            .syncAttemptsLessThan(5))
        .findAll();
  }

  /// Get logs by experiment
  /// الحصول على السجلات حسب التجربة
  Future<List<LocalResearchLog>> getByExperiment(String experimentId) {
    return _isar.localResearchLogs
        .filter()
        .experimentIdEqualTo(experimentId)
        .sortByLogDateDesc()
        .findAll();
  }

  /// Get log by offline ID
  /// الحصول على سجل بواسطة المعرف المحلي
  Future<LocalResearchLog?> getByOfflineId(String offlineId) {
    return _isar.localResearchLogs
        .filter()
        .offlineIdEqualTo(offlineId)
        .findFirst();
  }

  /// Update log
  /// تحديث سجل
  Future<void> update(LocalResearchLog log) async {
    log.updatedAt = DateTime.now();
    await _isar.writeTxn(() => _isar.localResearchLogs.put(log));
  }

  /// Delete log by ID
  /// حذف سجل بواسطة المعرف
  Future<bool> delete(int id) {
    return _isar.writeTxn(() => _isar.localResearchLogs.delete(id));
  }

  /// Get logs count by sync status
  /// الحصول على عدد السجلات حسب حالة المزامنة
  Future<int> getCountBySyncStatus(SyncStatus status) {
    return _isar.localResearchLogs
        .filter()
        .syncStatusEqualTo(status)
        .count();
  }

  /// Clear all synced logs older than days
  /// حذف السجلات المتزامنة الأقدم من عدد أيام
  Future<int> clearOldSyncedLogs(int daysOld) async {
    final cutoffDate = DateTime.now().subtract(Duration(days: daysOld));

    final logsToDelete = await _isar.localResearchLogs
        .filter()
        .syncStatusEqualTo(SyncStatus.synced)
        .updatedAtLessThan(cutoffDate)
        .findAll();

    if (logsToDelete.isEmpty) return 0;

    final ids = logsToDelete.map((l) => l.id).toList();

    return _isar.writeTxn(() => _isar.localResearchLogs.deleteAll(ids));
  }
}
