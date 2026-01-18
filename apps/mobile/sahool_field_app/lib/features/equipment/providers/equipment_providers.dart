/// Equipment Providers - مزودات بيانات المعدات
/// Riverpod providers للتواصل مع Equipment Service
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/equipment_models.dart';
import '../data/equipment_repository.dart';

/// مزود قائمة المعدات
final equipmentListProvider = FutureProvider.autoDispose
    .family<List<Equipment>, EquipmentFilter?>((ref, filter) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getEquipment(
    type: filter?.type,
    status: filter?.status,
    fieldId: filter?.fieldId,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المعدات');
});

/// مزود إحصائيات المعدات
final equipmentStatsProvider = FutureProvider.autoDispose<EquipmentStats>((ref) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getStats();

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الإحصائيات');
});

/// مزود تنبيهات الصيانة
final maintenanceAlertsProvider = FutureProvider.autoDispose
    .family<List<MaintenanceAlert>, bool>((ref, overdueOnly) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getMaintenanceAlerts(overdueOnly: overdueOnly);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب التنبيهات');
});

/// مزود تفاصيل معدة محددة
final equipmentDetailsProvider = FutureProvider.autoDispose
    .family<Equipment, String>((ref, equipmentId) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getEquipmentById(equipmentId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'المعدة غير موجودة');
});

/// مزود البحث عبر QR Code
final equipmentByQrProvider = FutureProvider.autoDispose
    .family<Equipment, String>((ref, qrCode) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getEquipmentByQrCode(qrCode);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'المعدة غير موجودة');
});

/// مزود سجل الصيانة لمعدة محددة
final maintenanceHistoryProvider = FutureProvider.autoDispose
    .family<List<MaintenanceRecord>, String>((ref, equipmentId) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getMaintenanceHistory(equipmentId);

  if (result.isSuccess && result.data != null) {
    return result.data!.map((json) => MaintenanceRecord.fromJson(json)).toList();
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب سجل الصيانة');
});

/// سجل الصيانة
class MaintenanceRecord {
  final String recordId;
  final String equipmentId;
  final MaintenanceType maintenanceType;
  final String description;
  final String? descriptionAr;
  final String? performedBy;
  final double? cost;
  final String? notes;
  final List<String>? partsReplaced;
  final DateTime performedAt;
  final DateTime createdAt;

  const MaintenanceRecord({
    required this.recordId,
    required this.equipmentId,
    required this.maintenanceType,
    required this.description,
    this.descriptionAr,
    this.performedBy,
    this.cost,
    this.notes,
    this.partsReplaced,
    required this.performedAt,
    required this.createdAt,
  });

  String getDescription(String locale) {
    return locale == 'ar' && descriptionAr != null ? descriptionAr! : description;
  }

  factory MaintenanceRecord.fromJson(Map<String, dynamic> json) {
    return MaintenanceRecord(
      recordId: json['record_id'] as String? ?? json['id'] as String? ?? '',
      equipmentId: json['equipment_id'] as String? ?? '',
      maintenanceType: MaintenanceType.fromString(
        json['maintenance_type'] as String? ?? 'other',
      ),
      description: json['description'] as String? ?? '',
      descriptionAr: json['description_ar'] as String?,
      performedBy: json['performed_by'] as String?,
      cost: (json['cost'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      partsReplaced: json['parts_replaced'] != null
          ? List<String>.from(json['parts_replaced'] as List)
          : null,
      performedAt: json['performed_at'] != null
          ? DateTime.parse(json['performed_at'] as String)
          : DateTime.now(),
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }
}

/// حالة الفلتر المحددة
final selectedEquipmentFilterProvider = StateProvider<EquipmentFilter?>((ref) => null);

/// فلتر المعدات
class EquipmentFilter {
  final EquipmentType? type;
  final EquipmentStatus? status;
  final String? fieldId;

  const EquipmentFilter({this.type, this.status, this.fieldId});

  EquipmentFilter copyWith({
    EquipmentType? type,
    EquipmentStatus? status,
    String? fieldId,
    bool clearType = false,
    bool clearStatus = false,
    bool clearFieldId = false,
  }) {
    return EquipmentFilter(
      type: clearType ? null : (type ?? this.type),
      status: clearStatus ? null : (status ?? this.status),
      fieldId: clearFieldId ? null : (fieldId ?? this.fieldId),
    );
  }

  bool get hasFilters => type != null || status != null || fieldId != null;
}

/// Controller للعمليات (CRUD)
class EquipmentController extends StateNotifier<AsyncValue<void>> {
  final EquipmentRepository _repo;
  final Ref _ref;

  EquipmentController(this._repo, this._ref) : super(const AsyncValue.data(null));

  /// تحديث حالة المعدة
  Future<bool> updateStatus(String equipmentId, EquipmentStatus status) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateEquipmentStatus(equipmentId, status);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      // Invalidate related providers
      _ref.invalidate(equipmentListProvider);
      _ref.invalidate(equipmentStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الحالة',
      StackTrace.current,
    );
    return false;
  }

  /// تحديث موقع المعدة
  Future<bool> updateLocation(String equipmentId, double lat, double lon, [String? locationName]) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateEquipmentLocation(
      equipmentId,
      lat: lat,
      lon: lon,
      locationName: locationName,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(equipmentListProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الموقع',
      StackTrace.current,
    );
    return false;
  }

  /// إضافة سجل صيانة
  Future<bool> addMaintenanceRecord(
    String equipmentId, {
    required MaintenanceType maintenanceType,
    required String description,
    String? descriptionAr,
    String? performedBy,
    double? cost,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.addMaintenanceRecord(
      equipmentId,
      maintenanceType: maintenanceType,
      description: description,
      descriptionAr: descriptionAr,
      performedBy: performedBy,
      cost: cost,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(maintenanceAlertsProvider);
      _ref.invalidate(equipmentDetailsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إضافة سجل الصيانة',
      StackTrace.current,
    );
    return false;
  }

  /// حذف معدة
  Future<bool> deleteEquipment(String equipmentId) async {
    state = const AsyncValue.loading();

    final result = await _repo.deleteEquipment(equipmentId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(equipmentListProvider);
      _ref.invalidate(equipmentStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف المعدة',
      StackTrace.current,
    );
    return false;
  }

  /// إنشاء معدة جديدة
  Future<bool> createEquipment({
    required String name,
    String? nameAr,
    required EquipmentType type,
    String? serialNumber,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.createEquipment(
      name: name,
      nameAr: nameAr,
      type: type,
      serialNumber: serialNumber,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(equipmentListProvider);
      _ref.invalidate(equipmentStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء المعدة',
      StackTrace.current,
    );
    return false;
  }
}

/// مزود Controller
final equipmentControllerProvider =
    StateNotifierProvider<EquipmentController, AsyncValue<void>>((ref) {
  final repo = ref.watch(equipmentRepositoryProvider);
  return EquipmentController(repo, ref);
});
