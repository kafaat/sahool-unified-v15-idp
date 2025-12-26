/// VRA Providers - مزودات بيانات التطبيق المتغير
/// Riverpod providers للتواصل مع VRA Service
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/vra_models.dart';
import '../services/vra_service.dart';

/// مزود قائمة الوصفات
final prescriptionListProvider = FutureProvider.autoDispose
    .family<List<VRAPrescription>, PrescriptionFilter?>((ref, filter) async {
  final service = ref.watch(vraServiceProvider);
  final result = await service.getPrescriptions(
    fieldId: filter?.fieldId,
    vraType: filter?.vraType,
    status: filter?.status,
    startDate: filter?.startDate,
    endDate: filter?.endDate,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الوصفات');
});

/// مزود تفاصيل وصفة محددة
final prescriptionDetailsProvider = FutureProvider.autoDispose
    .family<VRAPrescription, String>((ref, prescriptionId) async {
  final service = ref.watch(vraServiceProvider);
  final result = await service.getPrescriptionById(prescriptionId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'الوصفة غير موجودة');
});

/// مزود إحصائيات VRA
final vraStatsProvider = FutureProvider.autoDispose<VRAStats>((ref) async {
  final service = ref.watch(vraServiceProvider);
  final result = await service.getStats();

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الإحصائيات');
});

/// مزود مناطق الإدارة لحقل
final fieldZonesProvider = FutureProvider.autoDispose
    .family<List<ManagementZone>, FieldZonesParams>((ref, params) async {
  final service = ref.watch(vraServiceProvider);
  final result = await service.getFieldZones(
    params.fieldId,
    zoningMethod: params.zoningMethod,
    zonesCount: params.zonesCount,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المناطق');
});

/// حالة الفلتر المحددة
final selectedPrescriptionFilterProvider = StateProvider<PrescriptionFilter?>((ref) => null);

/// الوصفة الحالية (للتعديل)
final currentPrescriptionProvider = StateProvider<VRAPrescription?>((ref) => null);

/// الوصفة المعاينة (عند الإنشاء)
final prescriptionPreviewProvider = StateProvider<VRAPrescription?>((ref) => null);

/// المنطقة المختارة
final selectedZoneProvider = StateProvider<ManagementZone?>((ref) => null);

/// فلتر الوصفات
class PrescriptionFilter {
  final String? fieldId;
  final VRAType? vraType;
  final PrescriptionStatus? status;
  final DateTime? startDate;
  final DateTime? endDate;

  const PrescriptionFilter({
    this.fieldId,
    this.vraType,
    this.status,
    this.startDate,
    this.endDate,
  });

  PrescriptionFilter copyWith({
    String? fieldId,
    VRAType? vraType,
    PrescriptionStatus? status,
    DateTime? startDate,
    DateTime? endDate,
    bool clearFieldId = false,
    bool clearVraType = false,
    bool clearStatus = false,
    bool clearStartDate = false,
    bool clearEndDate = false,
  }) {
    return PrescriptionFilter(
      fieldId: clearFieldId ? null : (fieldId ?? this.fieldId),
      vraType: clearVraType ? null : (vraType ?? this.vraType),
      status: clearStatus ? null : (status ?? this.status),
      startDate: clearStartDate ? null : (startDate ?? this.startDate),
      endDate: clearEndDate ? null : (endDate ?? this.endDate),
    );
  }

  bool get hasFilters =>
      fieldId != null || vraType != null || status != null || startDate != null || endDate != null;
}

/// معاملات جلب مناطق الحقل
class FieldZonesParams {
  final String fieldId;
  final ZoningMethod? zoningMethod;
  final int? zonesCount;

  const FieldZonesParams({
    required this.fieldId,
    this.zoningMethod,
    this.zonesCount,
  });

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is FieldZonesParams &&
        other.fieldId == fieldId &&
        other.zoningMethod == zoningMethod &&
        other.zonesCount == zonesCount;
  }

  @override
  int get hashCode => Object.hash(fieldId, zoningMethod, zonesCount);
}

/// Controller للعمليات (CRUD)
class VRAController extends StateNotifier<AsyncValue<void>> {
  final VRAService _service;
  final Ref _ref;

  VRAController(this._service, this._ref) : super(const AsyncValue.data(null));

  /// توليد وصفة جديدة
  Future<VRAPrescription?> generatePrescription({
    required String fieldId,
    required VRAType vraType,
    required ZoningMethod zoningMethod,
    required int zonesCount,
    String? name,
    String? nameAr,
    DateTime? scheduledDate,
    String? notes,
    String? notesAr,
    Map<String, dynamic>? parameters,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.generatePrescription(
      fieldId: fieldId,
      vraType: vraType,
      zoningMethod: zoningMethod,
      zonesCount: zonesCount,
      name: name,
      nameAr: nameAr,
      scheduledDate: scheduledDate,
      notes: notes,
      notesAr: notesAr,
      parameters: parameters,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _ref.invalidate(prescriptionListProvider);
      _ref.invalidate(vraStatsProvider);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في توليد الوصفة',
      StackTrace.current,
    );
    return null;
  }

  /// إنشاء وصفة يدوية
  Future<VRAPrescription?> createPrescription({
    required String fieldId,
    required String name,
    String? nameAr,
    required VRAType vraType,
    required ZoningMethod zoningMethod,
    required List<ManagementZone> zones,
    required List<ApplicationRate> rates,
    DateTime? scheduledDate,
    String? notes,
    String? notesAr,
    Map<String, dynamic>? parameters,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.createPrescription(
      fieldId: fieldId,
      name: name,
      nameAr: nameAr,
      vraType: vraType,
      zoningMethod: zoningMethod,
      zones: zones,
      rates: rates,
      scheduledDate: scheduledDate,
      notes: notes,
      notesAr: notesAr,
      parameters: parameters,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _ref.invalidate(prescriptionListProvider);
      _ref.invalidate(vraStatsProvider);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء الوصفة',
      StackTrace.current,
    );
    return null;
  }

  /// تحديث وصفة
  Future<bool> updatePrescription(
    String prescriptionId,
    Map<String, dynamic> updates,
  ) async {
    state = const AsyncValue.loading();

    final result = await _service.updatePrescription(prescriptionId, updates);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(prescriptionListProvider);
      _ref.invalidate(prescriptionDetailsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الوصفة',
      StackTrace.current,
    );
    return false;
  }

  /// حذف وصفة
  Future<bool> deletePrescription(String prescriptionId) async {
    state = const AsyncValue.loading();

    final result = await _service.deletePrescription(prescriptionId);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(prescriptionListProvider);
      _ref.invalidate(vraStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف الوصفة',
      StackTrace.current,
    );
    return false;
  }

  /// اعتماد وصفة
  Future<bool> approvePrescription(
    String prescriptionId, {
    String? notes,
    String? notesAr,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.approvePrescription(
      prescriptionId,
      notes: notes,
      notesAr: notesAr,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(prescriptionListProvider);
      _ref.invalidate(prescriptionDetailsProvider);
      _ref.invalidate(vraStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في اعتماد الوصفة',
      StackTrace.current,
    );
    return false;
  }

  /// تطبيق وصفة
  Future<bool> applyPrescription(
    String prescriptionId, {
    DateTime? appliedDate,
    String? notes,
    String? notesAr,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.applyPrescription(
      prescriptionId,
      appliedDate: appliedDate,
      notes: notes,
      notesAr: notesAr,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(prescriptionListProvider);
      _ref.invalidate(prescriptionDetailsProvider);
      _ref.invalidate(vraStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تطبيق الوصفة',
      StackTrace.current,
    );
    return false;
  }

  /// إلغاء وصفة
  Future<bool> cancelPrescription(
    String prescriptionId, {
    String? reason,
    String? reasonAr,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.cancelPrescription(
      prescriptionId,
      reason: reason,
      reasonAr: reasonAr,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(prescriptionListProvider);
      _ref.invalidate(prescriptionDetailsProvider);
      _ref.invalidate(vraStatsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إلغاء الوصفة',
      StackTrace.current,
    );
    return false;
  }

  /// توليد مناطق
  Future<List<ManagementZone>?> generateZones({
    required String fieldId,
    required ZoningMethod zoningMethod,
    required int zonesCount,
    Map<String, dynamic>? parameters,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.generateZones(
      fieldId: fieldId,
      zoningMethod: zoningMethod,
      zonesCount: zonesCount,
      parameters: parameters,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _ref.invalidate(fieldZonesProvider);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في توليد المناطق',
      StackTrace.current,
    );
    return null;
  }

  /// تصدير وصفة
  Future<Map<String, dynamic>?> exportPrescription(
    String prescriptionId, {
    required String format,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.exportPrescription(
      prescriptionId,
      format: format,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تصدير الوصفة',
      StackTrace.current,
    );
    return null;
  }

  /// تنزيل وصفة
  Future<String?> downloadPrescription(
    String prescriptionId, {
    required String format,
    required String savePath,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.downloadPrescription(
      prescriptionId,
      format: format,
      savePath: savePath,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تنزيل الوصفة',
      StackTrace.current,
    );
    return null;
  }
}

/// مزود Controller
final vraControllerProvider =
    StateNotifierProvider<VRAController, AsyncValue<void>>((ref) {
  final service = ref.watch(vraServiceProvider);
  return VRAController(service, ref);
});
