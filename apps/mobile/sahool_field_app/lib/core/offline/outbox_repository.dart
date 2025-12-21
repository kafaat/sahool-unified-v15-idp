import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';
import 'offline_sync_engine.dart';

/// SAHOOL Outbox Repository
/// مستودع صندوق الصادر للمزامنة
///
/// Features:
/// - Persistent storage of pending operations
/// - Priority-based ordering
/// - Retry tracking
/// - Cleanup of completed items

class OutboxRepository {
  static const String _storageKey = 'sahool_outbox';
  static const String _statsKey = 'sahool_outbox_stats';
  static const int _maxCompletedItems = 100;

  SharedPreferences? _prefs;
  List<OutboxEntry> _entries = [];
  bool _isInitialized = false;

  /// تهيئة المستودع
  Future<void> initialize() async {
    if (_isInitialized) return;

    _prefs = await SharedPreferences.getInstance();
    await _load();
    _isInitialized = true;

    AppLogger.d('Outbox repository initialized with ${_entries.length} items', tag: 'OUTBOX');
  }

  /// تحميل من التخزين
  Future<void> _load() async {
    final data = _prefs?.getString(_storageKey);
    if (data == null) {
      _entries = [];
      return;
    }

    try {
      final list = jsonDecode(data) as List;
      _entries = list
          .map((e) => OutboxEntry.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      AppLogger.e('Failed to load outbox', tag: 'OUTBOX', error: e);
      _entries = [];
    }
  }

  /// حفظ للتخزين
  Future<void> _save() async {
    final data = jsonEncode(_entries.map((e) => e.toJson()).toList());
    await _prefs?.setString(_storageKey, data);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // العمليات الأساسية
  // ═══════════════════════════════════════════════════════════════════════════

  /// إضافة عنصر جديد
  Future<void> add(OutboxEntry entry) async {
    _entries.add(entry);
    _sortByPriority();
    await _save();

    AppLogger.d('Added to outbox: ${entry.entityType}/${entry.operation.name}', tag: 'OUTBOX');
  }

  /// الحصول على العناصر المعلقة
  Future<List<OutboxEntry>> getPending() async {
    return _entries
        .where((e) => e.status == OutboxStatus.pending)
        .toList();
  }

  /// الحصول على كل العناصر
  Future<List<OutboxEntry>> getAll() async {
    return List.from(_entries);
  }

  /// الحصول على عنصر بالـ ID
  Future<OutboxEntry?> getById(String id) async {
    try {
      return _entries.firstWhere((e) => e.id == id);
    } catch (e) {
      return null;
    }
  }

  /// تحديث عنصر
  Future<void> update(OutboxEntry entry) async {
    final index = _entries.indexWhere((e) => e.id == entry.id);
    if (index >= 0) {
      _entries[index] = entry;
      await _save();
    }
  }

  /// حذف عنصر
  Future<void> delete(String id) async {
    _entries.removeWhere((e) => e.id == id);
    await _save();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // تحديث الحالة
  // ═══════════════════════════════════════════════════════════════════════════

  /// تحديد كمكتمل
  Future<void> markCompleted(String id) async {
    final index = _entries.indexWhere((e) => e.id == id);
    if (index >= 0) {
      _entries[index] = _entries[index].copyWith(
        status: OutboxStatus.completed,
      );
      await _save();
      await _cleanupCompleted();
    }
  }

  /// تحديد كفاشل
  Future<void> markFailed(String id, String error) async {
    final index = _entries.indexWhere((e) => e.id == id);
    if (index >= 0) {
      final entry = _entries[index];
      _entries[index] = entry.copyWith(
        status: OutboxStatus.failed,
        retryCount: entry.retryCount + 1,
        lastError: error,
      );
      await _save();
    }
  }

  /// تحديد كقيد المعالجة
  Future<void> markProcessing(String id) async {
    final index = _entries.indexWhere((e) => e.id == id);
    if (index >= 0) {
      _entries[index] = _entries[index].copyWith(
        status: OutboxStatus.processing,
      );
      await _save();
    }
  }

  /// إعادة تعيين العناصر الفاشلة للمعلقة
  Future<void> resetFailed() async {
    for (int i = 0; i < _entries.length; i++) {
      if (_entries[i].status == OutboxStatus.failed) {
        _entries[i] = _entries[i].copyWith(
          status: OutboxStatus.pending,
        );
      }
    }
    await _save();
    AppLogger.i('Reset failed items to pending', tag: 'OUTBOX');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الإحصائيات
  // ═══════════════════════════════════════════════════════════════════════════

  /// عدد العناصر المعلقة
  Future<int> getPendingCount() async {
    return _entries.where((e) => e.status == OutboxStatus.pending).length;
  }

  /// عدد العناصر الفاشلة
  Future<int> getFailedCount() async {
    return _entries.where((e) => e.status == OutboxStatus.failed).length;
  }

  /// عدد العناصر المكتملة
  Future<int> getCompletedCount() async {
    return _entries.where((e) => e.status == OutboxStatus.completed).length;
  }

  /// إجمالي العناصر
  Future<int> getTotalCount() async {
    return _entries.length;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التنظيف والصيانة
  // ═══════════════════════════════════════════════════════════════════════════

  /// تنظيف العناصر المكتملة
  Future<void> clearCompleted() async {
    _entries.removeWhere((e) => e.status == OutboxStatus.completed);
    await _save();
    AppLogger.d('Cleared completed items', tag: 'OUTBOX');
  }

  /// تنظيف العناصر المكتملة الزائدة
  Future<void> _cleanupCompleted() async {
    final completed = _entries
        .where((e) => e.status == OutboxStatus.completed)
        .toList();

    if (completed.length > _maxCompletedItems) {
      // Sort by creation date and remove oldest
      completed.sort((a, b) => a.createdAt.compareTo(b.createdAt));
      final toRemove = completed.take(completed.length - _maxCompletedItems);

      for (final entry in toRemove) {
        _entries.removeWhere((e) => e.id == entry.id);
      }

      await _save();
      AppLogger.d('Cleaned up ${toRemove.length} old completed items', tag: 'OUTBOX');
    }
  }

  /// تنظيف كل البيانات
  Future<void> clearAll() async {
    _entries.clear();
    await _save();
    AppLogger.i('Cleared all outbox items', tag: 'OUTBOX');
  }

  /// ترتيب حسب الأولوية
  void _sortByPriority() {
    _entries.sort((a, b) {
      // Sort by priority (higher first), then by creation date (older first)
      final priorityCompare = b.priority.index.compareTo(a.priority.index);
      if (priorityCompare != 0) return priorityCompare;
      return a.createdAt.compareTo(b.createdAt);
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // استعلامات متقدمة
  // ═══════════════════════════════════════════════════════════════════════════

  /// الحصول على عناصر بنوع الكيان
  Future<List<OutboxEntry>> getByEntityType(String entityType) async {
    return _entries.where((e) => e.entityType == entityType).toList();
  }

  /// الحصول على عناصر بالعملية
  Future<List<OutboxEntry>> getByOperation(SyncOperation operation) async {
    return _entries.where((e) => e.operation == operation).toList();
  }

  /// الحصول على العناصر التي تجاوزت الحد الأقصى للمحاولات
  Future<List<OutboxEntry>> getExceededRetries(int maxRetries) async {
    return _entries
        .where((e) => e.status == OutboxStatus.failed && e.retryCount >= maxRetries)
        .toList();
  }

  /// التحقق من وجود تغييرات معلقة لكيان معين
  Future<bool> hasPendingChanges(String entityType, String entityId) async {
    return _entries.any((e) =>
        e.entityType == entityType &&
        e.entityId == entityId &&
        (e.status == OutboxStatus.pending || e.status == OutboxStatus.processing));
  }

  /// دمج التغييرات المعلقة لنفس الكيان
  Future<void> mergeUpdates(String entityType, String entityId) async {
    final pending = _entries.where((e) =>
        e.entityType == entityType &&
        e.entityId == entityId &&
        e.operation == SyncOperation.update &&
        e.status == OutboxStatus.pending).toList();

    if (pending.length <= 1) return;

    // Merge all updates into one
    Map<String, dynamic> mergedData = {};
    for (final entry in pending) {
      mergedData.addAll(entry.data);
    }

    // Keep only the last one with merged data
    final last = pending.last;
    final merged = last.copyWith(data: mergedData);

    // Remove all but update last
    for (final entry in pending) {
      if (entry.id != last.id) {
        _entries.removeWhere((e) => e.id == entry.id);
      }
    }

    final index = _entries.indexWhere((e) => e.id == last.id);
    if (index >= 0) {
      _entries[index] = merged;
    }

    await _save();
    AppLogger.d('Merged ${pending.length} updates for $entityType/$entityId', tag: 'OUTBOX');
  }
}
