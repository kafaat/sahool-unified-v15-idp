library;

/// Equipment Providers - مزودات بيانات المعدات
/// Riverpod providers للتواصل مع Equipment Service
/// Enhanced with offline-first support and comprehensive state management

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/equipment_models.dart';
import '../data/equipment_repository.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Equipment List Providers
// ═══════════════════════════════════════════════════════════════════════════

/// مزود قائمة المعدات
final equipmentListProvider = FutureProvider.autoDispose
    .family<List<Equipment>, EquipmentFilter?>((ref, filter) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getEquipment(
    type: filter?.type,
    status: filter?.status,
    fieldId: filter?.fieldId,
    search: filter?.search,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المعدات');
});

/// مزود قائمة المعدات المفلترة مع دعم البحث
final filteredEquipmentProvider =
    FutureProvider.autoDispose<List<Equipment>>((ref) async {
  final filter = ref.watch(selectedEquipmentFilterProvider);
  final equipmentAsync = ref.watch(equipmentListProvider(filter));

  return equipmentAsync.when(
    data: (data) => data,
    loading: () => [],
    error: (_, __) => [],
  );
});

/// مزود إحصائيات المعدات
final equipmentStatsProvider =
    FutureProvider.autoDispose<EquipmentStats>((ref) async {
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

/// مزود المعدات التي تحتاج صيانة
final equipmentNeedingMaintenanceProvider =
    FutureProvider.autoDispose<List<Equipment>>((ref) async {
  final equipmentAsync = ref.watch(equipmentListProvider(null));

  return equipmentAsync.when(
    data: (data) => data
        .where((e) => e.needsMaintenanceSoon || e.isMaintenanceOverdue)
        .toList(),
    loading: () => [],
    error: (_, __) => [],
  );
});

/// مزود المعدات ذات الوقود المنخفض
final lowFuelEquipmentProvider =
    FutureProvider.autoDispose<List<Equipment>>((ref) async {
  final equipmentAsync = ref.watch(equipmentListProvider(null));

  return equipmentAsync.when(
    data: (data) => data.where((e) => e.isLowFuel).toList(),
    loading: () => [],
    error: (_, __) => [],
  );
});

// ═══════════════════════════════════════════════════════════════════════════
// Equipment Details Providers
// ═══════════════════════════════════════════════════════════════════════════

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
final equipmentByQrProvider =
    FutureProvider.autoDispose.family<Equipment, String>((ref, qrCode) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getEquipmentByQrCode(qrCode);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'المعدة غير موجودة');
});

/// مزود المعدة المحددة حاليا
final selectedEquipmentIdProvider = StateProvider<String?>((ref) => null);

/// مزود تفاصيل المعدة المحددة
final selectedEquipmentProvider =
    FutureProvider.autoDispose<Equipment?>((ref) async {
  final equipmentId = ref.watch(selectedEquipmentIdProvider);
  if (equipmentId == null) return null;

  final details = ref.watch(equipmentDetailsProvider(equipmentId));
  return details.when(
    data: (data) => data,
    loading: () => null,
    error: (_, __) => null,
  );
});

// ═══════════════════════════════════════════════════════════════════════════
// Maintenance Providers
// ═══════════════════════════════════════════════════════════════════════════

/// مزود سجل صيانة المعدة
final equipmentMaintenanceHistoryProvider = FutureProvider.autoDispose
    .family<List<MaintenanceRecord>, String>((ref, equipmentId) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getMaintenanceHistory(equipmentId);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب سجل الصيانة');
});

/// Alias for backwards compatibility
final equipmentHistoryProvider = equipmentMaintenanceHistoryProvider;

// ═══════════════════════════════════════════════════════════════════════════
// Fuel Log Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Parameters for fuel log query
class FuelLogParams {
  final String equipmentId;
  final DateTime? from;
  final DateTime? to;

  const FuelLogParams({required this.equipmentId, this.from, this.to});

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FuelLogParams &&
          equipmentId == other.equipmentId &&
          from == other.from &&
          to == other.to;

  @override
  int get hashCode => Object.hash(equipmentId, from, to);
}

/// مزود سجل الوقود للمعدة
final fuelLogsProvider = FutureProvider.autoDispose
    .family<List<FuelLog>, FuelLogParams>((ref, params) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getFuelLogs(
    params.equipmentId,
    from: params.from,
    to: params.to,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب سجل الوقود');
});

/// مزود ملخص استهلاك الوقود
final fuelConsumptionSummaryProvider = FutureProvider.autoDispose
    .family<FuelConsumptionSummary, FuelLogParams>((ref, params) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getFuelConsumptionSummary(
    params.equipmentId,
    from: params.from,
    to: params.to,
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب ملخص الوقود');
});

// ═══════════════════════════════════════════════════════════════════════════
// Usage Log Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Parameters for usage log query
class UsageLogParams {
  final String equipmentId;
  final DateTime? from;
  final DateTime? to;
  final UsageType? usageType;

  const UsageLogParams({
    required this.equipmentId,
    this.from,
    this.to,
    this.usageType,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UsageLogParams &&
          equipmentId == other.equipmentId &&
          from == other.from &&
          to == other.to &&
          usageType == other.usageType;

  @override
  int get hashCode => Object.hash(equipmentId, from, to, usageType);
}

/// مزود سجل الاستخدام للمعدة
final usageLogsProvider = FutureProvider.autoDispose
    .family<List<UsageLog>, UsageLogParams>((ref, params) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getUsageLogs(
    params.equipmentId,
    from: params.from,
    to: params.to,
    usageType: params.usageType,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب سجل الاستخدام');
});

/// مزود ملخص الاستخدام
final usageSummaryProvider = FutureProvider.autoDispose
    .family<UsageSummary, UsageLogParams>((ref, params) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getUsageSummary(
    params.equipmentId,
    from: params.from,
    to: params.to,
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(
      result.errorAr ?? result.error ?? 'فشل في جلب ملخص الاستخدام');
});

/// مزود جلسة الاستخدام النشطة
final activeUsageSessionProvider = FutureProvider.autoDispose
    .family<UsageLog?, String>((ref, equipmentId) async {
  final repo = ref.watch(equipmentRepositoryProvider);
  final result = await repo.getActiveUsageSession(equipmentId);

  if (result.isSuccess) {
    return result.data;
  }
  return null;
});

// ═══════════════════════════════════════════════════════════════════════════
// Filter State Providers
// ═══════════════════════════════════════════════════════════════════════════

/// حالة الفلتر المحددة
final selectedEquipmentFilterProvider =
    StateProvider<EquipmentFilter?>((ref) => null);

/// حالة البحث النصي
final equipmentSearchQueryProvider = StateProvider<String>((ref) => '');

/// حالة النوع المحدد
final selectedEquipmentTypeProvider =
    StateProvider<EquipmentType?>((ref) => null);

/// حالة الحالة المحددة
final selectedEquipmentStatusProvider =
    StateProvider<EquipmentStatus?>((ref) => null);

/// فلتر المعدات
class EquipmentFilter {
  final EquipmentType? type;
  final EquipmentStatus? status;
  final String? fieldId;
  final String? search;

  const EquipmentFilter({this.type, this.status, this.fieldId, this.search});

  EquipmentFilter copyWith({
    EquipmentType? type,
    EquipmentStatus? status,
    String? fieldId,
    String? search,
    bool clearType = false,
    bool clearStatus = false,
    bool clearFieldId = false,
    bool clearSearch = false,
  }) {
    return EquipmentFilter(
      type: clearType ? null : (type ?? this.type),
      status: clearStatus ? null : (status ?? this.status),
      fieldId: clearFieldId ? null : (fieldId ?? this.fieldId),
      search: clearSearch ? null : (search ?? this.search),
    );
  }

  bool get hasFilters =>
      type != null ||
      status != null ||
      fieldId != null ||
      (search != null && search!.isNotEmpty);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is EquipmentFilter &&
          type == other.type &&
          status == other.status &&
          fieldId == other.fieldId &&
          search == other.search;

  @override
  int get hashCode => Object.hash(type, status, fieldId, search);
}

// ═══════════════════════════════════════════════════════════════════════════
// Offline Status Providers
// ═══════════════════════════════════════════════════════════════════════════

/// مزود عدد العمليات المعلقة
final pendingOperationsCountProvider =
    FutureProvider.autoDispose<int>((ref) async {
  final localDb = ref.watch(equipmentLocalDbProvider);
  return localDb.getPendingOperationsCount();
});

/// مزود وقت آخر مزامنة
final lastSyncTimeProvider = FutureProvider.autoDispose<DateTime?>((ref) async {
  final localDb = ref.watch(equipmentLocalDbProvider);
  return localDb.getLastSyncTime();
});

/// مزود حالة التخزين المؤقت
final isCacheStaleProvider = FutureProvider.autoDispose<bool>((ref) async {
  final localDb = ref.watch(equipmentLocalDbProvider);
  return localDb.isCacheStale();
});

// ═══════════════════════════════════════════════════════════════════════════
// Equipment Controller
// ═══════════════════════════════════════════════════════════════════════════

/// Controller للعمليات (CRUD)
class EquipmentController extends StateNotifier<AsyncValue<void>> {
  final EquipmentRepository _repo;
  final Ref _ref;

  EquipmentController(this._repo, this._ref)
      : super(const AsyncValue.data(null));

  /// إنشاء معدة جديدة
  Future<bool> createEquipment({
    required String name,
    String? nameAr,
    required EquipmentType type,
    String? serialNumber,
    String? brand,
    String? model,
    int? year,
    DateTime? purchaseDate,
    double? purchasePrice,
    String? fieldId,
    String? locationName,
    int? horsepower,
    FuelType? fuelType,
    double? fuelCapacityLiters,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.createEquipment(
      name: name,
      nameAr: nameAr,
      type: type,
      serialNumber: serialNumber,
      brand: brand,
      model: model,
      year: year,
      purchaseDate: purchaseDate,
      purchasePrice: purchasePrice,
      fieldId: fieldId,
      locationName: locationName,
      horsepower: horsepower,
      fuelType: fuelType,
      fuelCapacityLiters: fuelCapacityLiters,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateAllProviders();
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء المعدة',
      StackTrace.current,
    );
    return false;
  }

  /// تحديث معدة
  Future<bool> updateEquipment(
      String equipmentId, Map<String, dynamic> updates) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateEquipment(equipmentId, updates);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateEquipmentProviders(equipmentId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث المعدة',
      StackTrace.current,
    );
    return false;
  }

  /// تحديث حالة المعدة
  Future<bool> updateStatus(String equipmentId, EquipmentStatus status) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateEquipmentStatus(equipmentId, status);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateEquipmentProviders(equipmentId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الحالة',
      StackTrace.current,
    );
    return false;
  }

  /// تحديث موقع المعدة
  Future<bool> updateLocation(
    String equipmentId,
    double lat,
    double lon, [
    String? locationName,
  ]) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateEquipmentLocation(
      equipmentId,
      lat: lat,
      lon: lon,
      locationName: locationName,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateEquipmentProviders(equipmentId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الموقع',
      StackTrace.current,
    );
    return false;
  }

  /// تحديث القياسات (Telemetry)
  Future<bool> updateTelemetry(
    String equipmentId, {
    double? fuelPercent,
    double? hours,
    double? lat,
    double? lon,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.updateTelemetry(
      equipmentId,
      fuelPercent: fuelPercent,
      hours: hours,
      lat: lat,
      lon: lon,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _invalidateEquipmentProviders(equipmentId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث القياسات',
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
      _invalidateAllProviders();
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف المعدة',
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
    String? notes,
    List<String>? partsReplaced,
    double? hoursAtMaintenance,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.addMaintenanceRecord(
      equipmentId,
      maintenanceType: maintenanceType,
      description: description,
      descriptionAr: descriptionAr,
      performedBy: performedBy,
      cost: cost,
      notes: notes,
      partsReplaced: partsReplaced,
      hoursAtMaintenance: hoursAtMaintenance,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(equipmentMaintenanceHistoryProvider);
      _ref.invalidate(maintenanceAlertsProvider);
      _invalidateEquipmentProviders(equipmentId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إضافة سجل الصيانة',
      StackTrace.current,
    );
    return false;
  }

  /// جدولة صيانة
  Future<bool> scheduleMaintenance(
    String equipmentId, {
    required MaintenanceType maintenanceType,
    required MaintenancePriority priority,
    required String description,
    String? descriptionAr,
    required DateTime scheduledDate,
    double? scheduledAtHours,
    bool isRecurring = false,
    int? recurringIntervalDays,
    int? recurringIntervalHours,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.scheduleMaintenance(
      equipmentId,
      maintenanceType: maintenanceType,
      priority: priority,
      description: description,
      descriptionAr: descriptionAr,
      scheduledDate: scheduledDate,
      scheduledAtHours: scheduledAtHours,
      isRecurring: isRecurring,
      recurringIntervalDays: recurringIntervalDays,
      recurringIntervalHours: recurringIntervalHours,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(maintenanceAlertsProvider);
      _invalidateEquipmentProviders(equipmentId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في جدولة الصيانة',
      StackTrace.current,
    );
    return false;
  }

  /// إضافة سجل وقود
  Future<bool> addFuelLog(
    String equipmentId, {
    required FuelOperationType operationType,
    FuelType? fuelType,
    required double quantity,
    double? pricePerLiter,
    double? totalCost,
    double? fuelLevelBefore,
    double? fuelLevelAfter,
    String? stationName,
    String? receiptNumber,
    String? notes,
    double? lat,
    double? lon,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.addFuelLog(
      equipmentId,
      operationType: operationType,
      fuelType: fuelType,
      quantity: quantity,
      pricePerLiter: pricePerLiter,
      totalCost: totalCost,
      fuelLevelBefore: fuelLevelBefore,
      fuelLevelAfter: fuelLevelAfter,
      stationName: stationName,
      receiptNumber: receiptNumber,
      notes: notes,
      lat: lat,
      lon: lon,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(fuelLogsProvider);
      _ref.invalidate(fuelConsumptionSummaryProvider);
      _invalidateEquipmentProviders(equipmentId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إضافة سجل الوقود',
      StackTrace.current,
    );
    return false;
  }

  /// بدء جلسة استخدام
  Future<UsageLog?> startUsageSession(
    String equipmentId, {
    required UsageType usageType,
    FieldActivityType? activityType,
    String? fieldId,
    String? operatorName,
    double? startHourReading,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.startUsageSession(
      equipmentId,
      usageType: usageType,
      activityType: activityType,
      fieldId: fieldId,
      operatorName: operatorName,
      startHourReading: startHourReading,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _ref.invalidate(usageLogsProvider);
      _ref.invalidate(activeUsageSessionProvider);
      _invalidateEquipmentProviders(equipmentId);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في بدء جلسة الاستخدام',
      StackTrace.current,
    );
    return null;
  }

  /// إنهاء جلسة استخدام
  Future<bool> endUsageSession(
    String equipmentId,
    String logId, {
    double? endHourReading,
    double? fuelUsed,
    double? areaWorked,
    double? distanceTraveled,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.endUsageSession(
      equipmentId,
      logId,
      endHourReading: endHourReading,
      fuelUsed: fuelUsed,
      areaWorked: areaWorked,
      distanceTraveled: distanceTraveled,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(usageLogsProvider);
      _ref.invalidate(usageSummaryProvider);
      _ref.invalidate(activeUsageSessionProvider);
      _invalidateEquipmentProviders(equipmentId);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنهاء جلسة الاستخدام',
      StackTrace.current,
    );
    return false;
  }

  /// Invalidate providers for specific equipment
  void _invalidateEquipmentProviders(String equipmentId) {
    _ref.invalidate(equipmentDetailsProvider(equipmentId));
    _ref.invalidate(equipmentListProvider);
    _ref.invalidate(equipmentStatsProvider);
  }

  /// Invalidate all equipment providers
  void _invalidateAllProviders() {
    _ref.invalidate(equipmentListProvider);
    _ref.invalidate(equipmentStatsProvider);
    _ref.invalidate(maintenanceAlertsProvider);
    _ref.invalidate(equipmentNeedingMaintenanceProvider);
    _ref.invalidate(lowFuelEquipmentProvider);
  }
}

/// مزود Controller
final equipmentControllerProvider =
    StateNotifierProvider<EquipmentController, AsyncValue<void>>((ref) {
  final repo = ref.watch(equipmentRepositoryProvider);
  return EquipmentController(repo, ref);
});
