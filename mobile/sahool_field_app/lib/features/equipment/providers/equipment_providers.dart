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
}

/// مزود Controller
final equipmentControllerProvider =
    StateNotifierProvider<EquipmentController, AsyncValue<void>>((ref) {
  final repo = ref.watch(equipmentRepositoryProvider);
  return EquipmentController(repo, ref);
});
