import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// Draft Manager - Persists form drafts for offline-first experience
/// مدير المسودات - يحفظ مسودات النماذج لتجربة العمل دون اتصال
///
/// Features:
/// - Auto-save form drafts as user types
/// - Restore drafts on app resume
/// - Support for multiple form types
/// - Expiration and cleanup of old drafts
/// - Uses shared_preferences for simplicity and speed
///
/// Usage:
/// 1. Call saveDraft() periodically or on field changes
/// 2. Call getDraft() when opening a form to restore data
/// 3. Call deleteDraft() after successful form submission

// ============================================================
// Constants
// ============================================================

const String _keyDraftPrefix = 'draft_';
const String _keyDraftMetaPrefix = 'draft_meta_';
const Duration _defaultDraftExpiration = Duration(days: 7);

// ============================================================
// Draft Types
// ============================================================

/// Supported form/draft types
/// أنواع النماذج/المسودات المدعومة
enum DraftType {
  task, // مهمة
  field, // حقل
  irrigation, // ري
  fertilizer, // تسميد
  spray, // رش
  harvest, // حصاد
  note, // ملاحظة
  observation, // مراقبة
  equipment, // معدات
  marketplace, // سوق
  report, // تقرير
  custom, // مخصص
}

// ============================================================
// Draft Models
// ============================================================

/// Metadata for a saved draft
/// بيانات وصفية للمسودة المحفوظة
class DraftMetadata {
  final String id;
  final DraftType type;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? title;
  final String? entityId;
  final bool isAutoSave;

  const DraftMetadata({
    required this.id,
    required this.type,
    required this.createdAt,
    required this.updatedAt,
    this.title,
    this.entityId,
    this.isAutoSave = true,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type.name,
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt.toIso8601String(),
        'title': title,
        'entityId': entityId,
        'isAutoSave': isAutoSave,
      };

  factory DraftMetadata.fromJson(Map<String, dynamic> json) {
    return DraftMetadata(
      id: json['id'] as String,
      type: DraftType.values.byName(json['type'] as String),
      createdAt: DateTime.tryParse(json['createdAt'] as String) ?? DateTime.now(),
      updatedAt: DateTime.tryParse(json['updatedAt'] as String) ?? DateTime.now(),
      title: json['title'] as String?,
      entityId: json['entityId'] as String?,
      isAutoSave: json['isAutoSave'] as bool? ?? true,
    );
  }

  DraftMetadata copyWith({
    String? id,
    DraftType? type,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? title,
    String? entityId,
    bool? isAutoSave,
  }) {
    return DraftMetadata(
      id: id ?? this.id,
      type: type ?? this.type,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      title: title ?? this.title,
      entityId: entityId ?? this.entityId,
      isAutoSave: isAutoSave ?? this.isAutoSave,
    );
  }

  bool get isExpired {
    return DateTime.now().difference(updatedAt) > _defaultDraftExpiration;
  }

  @override
  String toString() =>
      'DraftMetadata(id: $id, type: ${type.name}, title: $title)';
}

/// Complete draft with data
/// مسودة كاملة مع البيانات
class Draft {
  final DraftMetadata metadata;
  final Map<String, dynamic> data;

  const Draft({
    required this.metadata,
    required this.data,
  });

  Map<String, dynamic> toJson() => {
        'metadata': metadata.toJson(),
        'data': data,
      };

  factory Draft.fromJson(Map<String, dynamic> json) {
    return Draft(
      metadata:
          DraftMetadata.fromJson(json['metadata'] as Map<String, dynamic>),
      data: json['data'] as Map<String, dynamic>,
    );
  }

  /// Create a new draft
  factory Draft.create({
    required DraftType type,
    required Map<String, dynamic> data,
    String? title,
    String? entityId,
    bool isAutoSave = true,
  }) {
    final now = DateTime.now();
    final id = '${type.name}_${now.millisecondsSinceEpoch}';
    return Draft(
      metadata: DraftMetadata(
        id: id,
        type: type,
        createdAt: now,
        updatedAt: now,
        title: title,
        entityId: entityId,
        isAutoSave: isAutoSave,
      ),
      data: data,
    );
  }

  @override
  String toString() =>
      'Draft(${metadata.type.name}, ${metadata.title ?? metadata.id})';
}

// ============================================================
// Draft Manager Service
// ============================================================

/// Service for managing form drafts
/// خدمة إدارة مسودات النماذج
class DraftManager {
  late SharedPreferences _prefs;
  bool _isInitialized = false;

  // Auto-save debouncing
  final Map<String, Timer> _autoSaveTimers = {};
  static const Duration _autoSaveDelay = Duration(seconds: 2);

  /// Initialize the draft manager
  /// تهيئة مدير المسودات
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      _prefs = await SharedPreferences.getInstance();
      _isInitialized = true;
      AppLogger.i('DraftManager initialized', tag: 'Drafts');

      // Clean up expired drafts on init
      await _cleanupExpiredDrafts();
    } catch (e) {
      AppLogger.e('Failed to initialize DraftManager', tag: 'Drafts', error: e);
      rethrow;
    }
  }

  void _ensureInitialized() {
    if (!_isInitialized) {
      throw StateError(
          'DraftManager not initialized. Call initialize() first.');
    }
  }

  // ============================================================
  // Core Draft Operations
  // ============================================================

  /// Save a draft
  /// حفظ مسودة
  Future<Draft> saveDraft({
    required DraftType type,
    required Map<String, dynamic> data,
    String? draftId,
    String? title,
    String? entityId,
    bool isAutoSave = false,
  }) async {
    _ensureInitialized();

    try {
      // If updating existing draft
      if (draftId != null) {
        final existingMeta = await _getDraftMetadata(draftId);
        if (existingMeta != null) {
          final updatedMeta = existingMeta.copyWith(
            updatedAt: DateTime.now(),
            title: title ?? existingMeta.title,
            isAutoSave: isAutoSave,
          );
          final draft = Draft(metadata: updatedMeta, data: data);
          await _saveDraftInternal(draft);
          return draft;
        }
      }

      // Create new draft
      final draft = Draft.create(
        type: type,
        data: data,
        title: title,
        entityId: entityId,
        isAutoSave: isAutoSave,
      );
      await _saveDraftInternal(draft);

      AppLogger.d(
        'Draft saved',
        tag: 'Drafts',
        data: {'id': draft.metadata.id, 'type': type.name},
      );

      return draft;
    } catch (e) {
      AppLogger.e('Failed to save draft', tag: 'Drafts', error: e);
      rethrow;
    }
  }

  Future<void> _saveDraftInternal(Draft draft) async {
    final dataKey = '$_keyDraftPrefix${draft.metadata.id}';
    final metaKey = '$_keyDraftMetaPrefix${draft.metadata.id}';

    await Future.wait([
      _prefs.setString(dataKey, jsonEncode(draft.data)),
      _prefs.setString(metaKey, jsonEncode(draft.metadata.toJson())),
    ]);
  }

  /// Get a draft by ID
  /// الحصول على مسودة بالمعرف
  Future<Draft?> getDraft(String draftId) async {
    _ensureInitialized();

    try {
      final meta = await _getDraftMetadata(draftId);
      if (meta == null) return null;

      final dataKey = '$_keyDraftPrefix$draftId';
      final dataJson = _prefs.getString(dataKey);
      if (dataJson == null) return null;

      final data = jsonDecode(dataJson) as Map<String, dynamic>;
      return Draft(metadata: meta, data: data);
    } catch (e) {
      AppLogger.e('Failed to get draft', tag: 'Drafts', error: e);
      return null;
    }
  }

  Future<DraftMetadata?> _getDraftMetadata(String draftId) async {
    final metaKey = '$_keyDraftMetaPrefix$draftId';
    final metaJson = _prefs.getString(metaKey);
    if (metaJson == null) return null;

    try {
      return DraftMetadata.fromJson(
          jsonDecode(metaJson) as Map<String, dynamic>);
    } catch (e) {
      return null;
    }
  }

  /// Get draft by type and entity ID
  /// الحصول على مسودة بالنوع ومعرف الكيان
  Future<Draft?> getDraftByEntity(DraftType type, String entityId) async {
    _ensureInitialized();

    final drafts = await getDraftsByType(type);
    for (final draft in drafts) {
      if (draft.metadata.entityId == entityId) {
        return draft;
      }
    }
    return null;
  }

  /// Delete a draft
  /// حذف مسودة
  Future<void> deleteDraft(String draftId) async {
    _ensureInitialized();

    try {
      final dataKey = '$_keyDraftPrefix$draftId';
      final metaKey = '$_keyDraftMetaPrefix$draftId';

      await Future.wait([
        _prefs.remove(dataKey),
        _prefs.remove(metaKey),
      ]);

      // Cancel any pending auto-save
      _autoSaveTimers[draftId]?.cancel();
      _autoSaveTimers.remove(draftId);

      AppLogger.d('Draft deleted: $draftId', tag: 'Drafts');
    } catch (e) {
      AppLogger.e('Failed to delete draft', tag: 'Drafts', error: e);
    }
  }

  /// Delete draft by entity
  /// حذف مسودة بالكيان
  Future<void> deleteDraftByEntity(DraftType type, String entityId) async {
    _ensureInitialized();

    final draft = await getDraftByEntity(type, entityId);
    if (draft != null) {
      await deleteDraft(draft.metadata.id);
    }
  }

  // ============================================================
  // Batch Operations
  // ============================================================

  /// Get all drafts of a specific type
  /// الحصول على جميع المسودات من نوع معين
  Future<List<Draft>> getDraftsByType(DraftType type) async {
    _ensureInitialized();

    final allMetadata = await _getAllDraftMetadata();
    final typedMetadata = allMetadata.where((m) => m.type == type).toList();

    final drafts = <Draft>[];
    for (final meta in typedMetadata) {
      final draft = await getDraft(meta.id);
      if (draft != null) {
        drafts.add(draft);
      }
    }

    // Sort by updated date, most recent first
    drafts.sort((a, b) => b.metadata.updatedAt.compareTo(a.metadata.updatedAt));

    return drafts;
  }

  /// Get all drafts
  /// الحصول على جميع المسودات
  Future<List<Draft>> getAllDrafts() async {
    _ensureInitialized();

    final allMetadata = await _getAllDraftMetadata();
    final drafts = <Draft>[];

    for (final meta in allMetadata) {
      final draft = await getDraft(meta.id);
      if (draft != null) {
        drafts.add(draft);
      }
    }

    // Sort by updated date, most recent first
    drafts.sort((a, b) => b.metadata.updatedAt.compareTo(a.metadata.updatedAt));

    return drafts;
  }

  Future<List<DraftMetadata>> _getAllDraftMetadata() async {
    final keys =
        _prefs.getKeys().where((k) => k.startsWith(_keyDraftMetaPrefix));
    final metadata = <DraftMetadata>[];

    for (final key in keys) {
      final json = _prefs.getString(key);
      if (json != null) {
        try {
          metadata.add(
              DraftMetadata.fromJson(jsonDecode(json) as Map<String, dynamic>));
        } catch (_) {
          // Skip invalid metadata
        }
      }
    }

    return metadata;
  }

  /// Get draft count by type
  /// الحصول على عدد المسودات حسب النوع
  Future<int> getDraftCount(DraftType? type) async {
    _ensureInitialized();

    final allMetadata = await _getAllDraftMetadata();
    if (type == null) {
      return allMetadata.length;
    }
    return allMetadata.where((m) => m.type == type).length;
  }

  /// Delete all drafts of a type
  /// حذف جميع مسودات نوع معين
  Future<void> deleteAllDraftsByType(DraftType type) async {
    _ensureInitialized();

    final drafts = await getDraftsByType(type);
    await Future.wait(drafts.map((d) => deleteDraft(d.metadata.id)));

    AppLogger.d('Deleted all ${type.name} drafts: ${drafts.length}',
        tag: 'Drafts');
  }

  /// Delete all drafts
  /// حذف جميع المسودات
  Future<void> deleteAllDrafts() async {
    _ensureInitialized();

    final keys = _prefs.getKeys().where(
          (k) =>
              k.startsWith(_keyDraftPrefix) ||
              k.startsWith(_keyDraftMetaPrefix),
        );

    await Future.wait(keys.map((k) => _prefs.remove(k)));

    // Cancel all auto-save timers
    for (final timer in _autoSaveTimers.values) {
      timer.cancel();
    }
    _autoSaveTimers.clear();

    AppLogger.i('All drafts deleted', tag: 'Drafts');
  }

  // ============================================================
  // Auto-Save Functionality
  // ============================================================

  /// Schedule auto-save for a draft (debounced)
  /// جدولة الحفظ التلقائي للمسودة (مع إزالة الارتداد)
  void scheduleAutoSave({
    required DraftType type,
    required Map<String, dynamic> data,
    required String formKey,
    String? title,
    String? entityId,
  }) {
    _ensureInitialized();

    // Cancel previous timer for this form
    _autoSaveTimers[formKey]?.cancel();

    // Schedule new save
    _autoSaveTimers[formKey] = Timer(_autoSaveDelay, () async {
      try {
        await saveDraft(
          type: type,
          data: data,
          draftId: formKey,
          title: title,
          entityId: entityId,
          isAutoSave: true,
        );
        AppLogger.d('Auto-saved draft: $formKey', tag: 'Drafts');
      } catch (e) {
        AppLogger.e('Auto-save failed', tag: 'Drafts', error: e);
      }
    });
  }

  /// Cancel scheduled auto-save
  /// إلغاء الحفظ التلقائي المجدول
  void cancelAutoSave(String formKey) {
    _autoSaveTimers[formKey]?.cancel();
    _autoSaveTimers.remove(formKey);
  }

  /// Immediately save current form state
  /// حفظ حالة النموذج الحالي فوراً
  Future<Draft> saveImmediately({
    required DraftType type,
    required Map<String, dynamic> data,
    required String formKey,
    String? title,
    String? entityId,
  }) async {
    // Cancel any pending auto-save
    cancelAutoSave(formKey);

    return saveDraft(
      type: type,
      data: data,
      draftId: formKey,
      title: title,
      entityId: entityId,
      isAutoSave: false,
    );
  }

  // ============================================================
  // Cleanup Operations
  // ============================================================

  /// Clean up expired drafts
  /// تنظيف المسودات منتهية الصلاحية
  Future<int> _cleanupExpiredDrafts() async {
    final allMetadata = await _getAllDraftMetadata();
    final expiredDrafts = allMetadata.where((m) => m.isExpired).toList();

    for (final meta in expiredDrafts) {
      await deleteDraft(meta.id);
    }

    if (expiredDrafts.isNotEmpty) {
      AppLogger.i('Cleaned up ${expiredDrafts.length} expired drafts',
          tag: 'Drafts');
    }

    return expiredDrafts.length;
  }

  /// Clean up old auto-save drafts (keep only most recent per type/entity)
  /// تنظيف مسودات الحفظ التلقائي القديمة
  Future<int> cleanupOldAutoSaves({int keepPerType = 5}) async {
    _ensureInitialized();

    int deletedCount = 0;
    final allMetadata = await _getAllDraftMetadata();

    // Group by type
    final byType = <DraftType, List<DraftMetadata>>{};
    for (final meta in allMetadata) {
      if (meta.isAutoSave) {
        byType.putIfAbsent(meta.type, () => []).add(meta);
      }
    }

    // Keep only most recent per type
    for (final entry in byType.entries) {
      final drafts = entry.value;
      drafts.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));

      if (drafts.length > keepPerType) {
        final toDelete = drafts.skip(keepPerType);
        for (final meta in toDelete) {
          await deleteDraft(meta.id);
          deletedCount++;
        }
      }
    }

    if (deletedCount > 0) {
      AppLogger.i('Cleaned up $deletedCount old auto-save drafts',
          tag: 'Drafts');
    }

    return deletedCount;
  }

  /// Dispose resources
  /// التخلص من الموارد
  void dispose() {
    for (final timer in _autoSaveTimers.values) {
      timer.cancel();
    }
    _autoSaveTimers.clear();
  }
}

// ============================================================
// Form-Specific Draft Helpers
// ============================================================

/// Extension methods for common form draft operations
/// طرق توسيع لعمليات مسودات النماذج الشائعة
extension DraftManagerFormHelpers on DraftManager {
  /// Save task form draft
  /// حفظ مسودة نموذج المهمة
  Future<Draft> saveTaskDraft({
    required String? taskId,
    required String? title,
    required String? description,
    required String? fieldId,
    required String? priority,
    required DateTime? dueDate,
    required String? assignedTo,
  }) async {
    return saveDraft(
      type: DraftType.task,
      data: {
        'taskId': taskId,
        'title': title,
        'description': description,
        'fieldId': fieldId,
        'priority': priority,
        'dueDate': dueDate?.toIso8601String(),
        'assignedTo': assignedTo,
      },
      entityId: taskId,
      title: title ?? 'مهمة جديدة',
    );
  }

  /// Save irrigation record draft
  /// حفظ مسودة سجل الري
  Future<Draft> saveIrrigationDraft({
    required String? fieldId,
    required String? method,
    required double? amount,
    required String? unit,
    required DateTime? date,
    required String? notes,
  }) async {
    return saveDraft(
      type: DraftType.irrigation,
      data: {
        'fieldId': fieldId,
        'method': method,
        'amount': amount,
        'unit': unit,
        'date': date?.toIso8601String(),
        'notes': notes,
      },
      entityId: fieldId,
      title: 'سجل ري - ${date?.toString().split(' ')[0] ?? 'جديد'}',
    );
  }

  /// Save fertilizer application draft
  /// حفظ مسودة تطبيق السماد
  Future<Draft> saveFertilizerDraft({
    required String? fieldId,
    required String? productName,
    required double? rate,
    required String? unit,
    required String? method,
    required DateTime? date,
    required String? notes,
  }) async {
    return saveDraft(
      type: DraftType.fertilizer,
      data: {
        'fieldId': fieldId,
        'productName': productName,
        'rate': rate,
        'unit': unit,
        'method': method,
        'date': date?.toIso8601String(),
        'notes': notes,
      },
      entityId: fieldId,
      title: productName ?? 'تسميد جديد',
    );
  }

  /// Save spray application draft
  /// حفظ مسودة تطبيق الرش
  Future<Draft> saveSprayDraft({
    required String? fieldId,
    required String? productName,
    required String? targetPest,
    required double? rate,
    required String? unit,
    required DateTime? date,
    required int? phi,
    required String? notes,
  }) async {
    return saveDraft(
      type: DraftType.spray,
      data: {
        'fieldId': fieldId,
        'productName': productName,
        'targetPest': targetPest,
        'rate': rate,
        'unit': unit,
        'date': date?.toIso8601String(),
        'phi': phi,
        'notes': notes,
      },
      entityId: fieldId,
      title: productName ?? 'رش جديد',
    );
  }

  /// Save field observation draft
  /// حفظ مسودة مراقبة الحقل
  Future<Draft> saveObservationDraft({
    required String? fieldId,
    required String? type,
    required String? description,
    required List<String>? photoUrls,
    required Map<String, double>? location,
    required DateTime? date,
  }) async {
    return saveDraft(
      type: DraftType.observation,
      data: {
        'fieldId': fieldId,
        'observationType': type,
        'description': description,
        'photoUrls': photoUrls,
        'location': location,
        'date': date?.toIso8601String(),
      },
      entityId: fieldId,
      title: type ?? 'مراقبة جديدة',
    );
  }

  /// Save harvest record draft
  /// حفظ مسودة سجل الحصاد
  Future<Draft> saveHarvestDraft({
    required String? fieldId,
    required String? cropType,
    required double? yieldAmount,
    required String? yieldUnit,
    required String? quality,
    required DateTime? date,
    required String? notes,
  }) async {
    return saveDraft(
      type: DraftType.harvest,
      data: {
        'fieldId': fieldId,
        'cropType': cropType,
        'yieldAmount': yieldAmount,
        'yieldUnit': yieldUnit,
        'quality': quality,
        'date': date?.toIso8601String(),
        'notes': notes,
      },
      entityId: fieldId,
      title: cropType != null ? 'حصاد $cropType' : 'حصاد جديد',
    );
  }

  /// Save marketplace listing draft
  /// حفظ مسودة قائمة السوق
  Future<Draft> saveMarketplaceDraft({
    required String? productType,
    required String? title,
    required String? description,
    required double? quantity,
    required String? unit,
    required double? pricePerUnit,
    required String? currency,
    required List<String>? photoUrls,
    required String? location,
  }) async {
    return saveDraft(
      type: DraftType.marketplace,
      data: {
        'productType': productType,
        'title': title,
        'description': description,
        'quantity': quantity,
        'unit': unit,
        'pricePerUnit': pricePerUnit,
        'currency': currency,
        'photoUrls': photoUrls,
        'location': location,
      },
      title: title ?? productType ?? 'منتج جديد',
    );
  }
}

// ============================================================
// Riverpod Providers
// ============================================================

/// Provider for DraftManager
final draftManagerProvider = Provider<DraftManager>((ref) {
  final manager = DraftManager();
  ref.onDispose(() => manager.dispose());
  return manager;
});

/// Provider for draft count (all types)
final draftCountProvider = FutureProvider<int>((ref) async {
  final manager = ref.watch(draftManagerProvider);
  await manager.initialize();
  return manager.getDraftCount(null);
});

/// Provider for drafts by type
final draftsByTypeProvider =
    FutureProvider.family<List<Draft>, DraftType>((ref, type) async {
  final manager = ref.watch(draftManagerProvider);
  await manager.initialize();
  return manager.getDraftsByType(type);
});

/// Provider for all drafts
final allDraftsProvider = FutureProvider<List<Draft>>((ref) async {
  final manager = ref.watch(draftManagerProvider);
  await manager.initialize();
  return manager.getAllDrafts();
});

/// Provider for specific draft
final draftProvider =
    FutureProvider.family<Draft?, String>((ref, draftId) async {
  final manager = ref.watch(draftManagerProvider);
  await manager.initialize();
  return manager.getDraft(draftId);
});

// ============================================================
// Draft State Notifier for Form Integration
// ============================================================

/// State notifier for managing draft state in forms
class DraftFormNotifier extends StateNotifier<Draft?> {
  final DraftManager _manager;
  final DraftType _type;
  final String? _entityId;

  DraftFormNotifier(this._manager, this._type, this._entityId) : super(null);

  /// Load existing draft for entity
  Future<void> loadDraft() async {
    if (_entityId != null) {
      state = await _manager.getDraftByEntity(_type, _entityId);
    }
  }

  /// Update draft data (triggers auto-save)
  void updateData(Map<String, dynamic> data, {String? title}) {
    final formKey = _entityId ?? '${_type.name}_new';
    _manager.scheduleAutoSave(
      type: _type,
      data: data,
      formKey: formKey,
      title: title,
      entityId: _entityId,
    );
  }

  /// Save draft immediately
  Future<void> save(Map<String, dynamic> data, {String? title}) async {
    final formKey = _entityId ?? '${_type.name}_new';
    state = await _manager.saveImmediately(
      type: _type,
      data: data,
      formKey: formKey,
      title: title,
      entityId: _entityId,
    );
  }

  /// Clear draft (after successful submission)
  Future<void> clear() async {
    if (state != null) {
      await _manager.deleteDraft(state!.metadata.id);
      state = null;
    } else if (_entityId != null) {
      await _manager.deleteDraftByEntity(_type, _entityId);
    }
  }
}

/// Provider factory for draft form notifier
final draftFormNotifierProvider = StateNotifierProvider.family<
    DraftFormNotifier, Draft?, (DraftType, String?)>(
  (ref, params) {
    final (type, entityId) = params;
    final manager = ref.watch(draftManagerProvider);
    return DraftFormNotifier(manager, type, entityId);
  },
);
