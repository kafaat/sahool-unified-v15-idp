/// Equipment State Providers - مزودات حالة المعدات
/// Comprehensive Riverpod state management for Equipment feature
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/equipment_api.dart';
import '../data/equipment_local_db.dart';
import '../domain/models/equipment.dart';
import '../domain/models/equipment_status.dart';
import '../domain/models/maintenance_record.dart';
import '../domain/models/fuel_log.dart';
import '../domain/models/usage_log.dart';

// Re-export models for convenience
export '../domain/models/equipment.dart';
export '../domain/models/equipment_status.dart';
export '../domain/models/maintenance_record.dart';
export '../domain/models/fuel_log.dart';
export '../domain/models/usage_log.dart';
export '../data/equipment_api.dart' show ApiResult;

// ═══════════════════════════════════════════════════════════════════════════════
// Core Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Equipment Repository Provider (API + Local DB)
final equipmentRepositoryProvider = Provider<EquipmentApi>((ref) {
  return EquipmentApi();
});

/// Equipment Local Database Provider
final equipmentLocalDbProvider = Provider<EquipmentLocalDb>((ref) {
  return EquipmentLocalDb();
});

// ═══════════════════════════════════════════════════════════════════════════════
// Equipment List Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Equipment list with optional filtering
final equipmentListProvider = FutureProvider.autoDispose
    .family<List<Equipment>, EquipmentFilter?>((ref, filter) async {
  final api = ref.watch(equipmentRepositoryProvider);
  final localDb = ref.watch(equipmentLocalDbProvider);

  try {
    final result = await api.getEquipment(
      type: filter?.type,
      status: filter?.status,
      fieldId: filter?.fieldId,
      search: filter?.search,
    );

    if (result.isSuccess && result.data != null) {
      // Cache to local DB
      await localDb.saveEquipmentList(result.data!);
      return result.data!;
    }

    // Fallback to local cache
    return localDb.getEquipmentList(
      type: filter?.type,
      status: filter?.status,
      fieldId: filter?.fieldId,
      search: filter?.search,
    );
  } catch (e) {
    // Fallback to local cache on error
    return localDb.getEquipmentList(
      type: filter?.type,
      status: filter?.status,
      fieldId: filter?.fieldId,
      search: filter?.search,
    );
  }
});

/// Equipment details by ID
final equipmentDetailsProvider = FutureProvider.autoDispose
    .family<Equipment, String>((ref, equipmentId) async {
  final api = ref.watch(equipmentRepositoryProvider);
  final localDb = ref.watch(equipmentLocalDbProvider);

  try {
    final result = await api.getEquipmentById(equipmentId);

    if (result.isSuccess && result.data != null) {
      // Cache to local DB
      await localDb.saveEquipment(result.data!);
      return result.data!;
    }

    // Fallback to local cache
    final local = await localDb.getEquipmentById(equipmentId);
    if (local != null) return local;

    throw Exception(result.errorAr ?? result.error ?? 'المعدة غير موجودة');
  } catch (e) {
    // Fallback to local cache on error
    final local = await localDb.getEquipmentById(equipmentId);
    if (local != null) return local;
    rethrow;
  }
});

/// Equipment by QR Code
final equipmentByQrProvider = FutureProvider.autoDispose
    .family<Equipment, String>((ref, qrCode) async {
  final api = ref.watch(equipmentRepositoryProvider);
  final localDb = ref.watch(equipmentLocalDbProvider);

  final result = await api.getEquipmentByQrCode(qrCode);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }

  // Try local cache
  final local = await localDb.getEquipmentByQrCode(qrCode);
  if (local != null) return local;

  throw Exception(result.errorAr ?? result.error ?? 'المعدة غير موجودة');
});

// ═══════════════════════════════════════════════════════════════════════════════
// Statistics & Alerts Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Equipment statistics
final equipmentStatsProvider = FutureProvider.autoDispose<EquipmentStats>((ref) async {
  final api = ref.watch(equipmentRepositoryProvider);
  final localDb = ref.watch(equipmentLocalDbProvider);

  try {
    final result = await api.getStats();

    if (result.isSuccess && result.data != null) {
      await localDb.saveStats(result.data!);
      return result.data!;
    }

    // Fallback to local stats
    final local = await localDb.getStats();
    if (local != null) return local;

    // Calculate from local data
    return localDb.calculateLocalStats();
  } catch (e) {
    // Fallback to local stats
    final local = await localDb.getStats();
    if (local != null) return local;
    return localDb.calculateLocalStats();
  }
});

/// Maintenance alerts
final maintenanceAlertsProvider = FutureProvider.autoDispose
    .family<List<MaintenanceAlert>, bool>((ref, overdueOnly) async {
  final api = ref.watch(equipmentRepositoryProvider);

  final result = await api.getMaintenanceAlerts(overdueOnly: overdueOnly);

  if (result.isSuccess) {
    return result.data ?? [];
  }

  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب التنبيهات');
});

// ═══════════════════════════════════════════════════════════════════════════════
// Maintenance Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Maintenance history for equipment
final equipmentMaintenanceHistoryProvider = FutureProvider.autoDispose
    .family<List<MaintenanceRecord>, String>((ref, equipmentId) async {
  final api = ref.watch(equipmentRepositoryProvider);
  final localDb = ref.watch(equipmentLocalDbProvider);

  try {
    final result = await api.getMaintenanceHistory(equipmentId);

    if (result.isSuccess && result.data != null) {
      await localDb.saveMaintenanceRecords(equipmentId, result.data!);
      return result.data!;
    }

    // Fallback to local cache
    return localDb.getMaintenanceRecords(equipmentId);
  } catch (e) {
    return localDb.getMaintenanceRecords(equipmentId);
  }
});

/// Scheduled maintenances (all equipment or specific)
final scheduledMaintenancesProvider = FutureProvider.autoDispose
    .family<List<ScheduledMaintenance>, String?>((ref, equipmentId) async {
  final api = ref.watch(equipmentRepositoryProvider);

  final result = await api.getScheduledMaintenances(
    equipmentId: equipmentId,
    upcomingOnly: true,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }

  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الصيانات المجدولة');
});

// ═══════════════════════════════════════════════════════════════════════════════
// Fuel Log Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Fuel log parameters
class FuelLogParams {
  final String equipmentId;
  final DateTime? from;
  final DateTime? to;
  final int limit;

  const FuelLogParams({
    required this.equipmentId,
    this.from,
    this.to,
    this.limit = 50,
  });

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is FuelLogParams &&
        other.equipmentId == equipmentId &&
        other.from == from &&
        other.to == to &&
        other.limit == limit;
  }

  @override
  int get hashCode => Object.hash(equipmentId, from, to, limit);
}

/// Fuel logs for equipment
final equipmentFuelLogsProvider = FutureProvider.autoDispose
    .family<List<FuelLog>, FuelLogParams>((ref, params) async {
  final api = ref.watch(equipmentRepositoryProvider);
  final localDb = ref.watch(equipmentLocalDbProvider);

  try {
    final result = await api.getFuelLogs(
      params.equipmentId,
      from: params.from,
      to: params.to,
      limit: params.limit,
    );

    if (result.isSuccess && result.data != null) {
      await localDb.saveFuelLogs(params.equipmentId, result.data!);
      return result.data!;
    }

    return localDb.getFuelLogs(
      params.equipmentId,
      from: params.from,
      to: params.to,
    );
  } catch (e) {
    return localDb.getFuelLogs(
      params.equipmentId,
      from: params.from,
      to: params.to,
    );
  }
});

/// Simple fuel logs provider by equipment ID only
final equipmentFuelLogsSimpleProvider = FutureProvider.autoDispose
    .family<List<FuelLog>, String>((ref, equipmentId) async {
  return ref.watch(equipmentFuelLogsProvider(FuelLogParams(
    equipmentId: equipmentId,
  )).future);
});

/// Fuel consumption summary
final fuelConsumptionSummaryProvider = FutureProvider.autoDispose
    .family<FuelConsumptionSummary, String>((ref, equipmentId) async {
  final api = ref.watch(equipmentRepositoryProvider);

  final result = await api.getFuelConsumptionSummary(
    equipmentId,
    from: DateTime.now().subtract(const Duration(days: 30)),
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }

  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب ملخص الوقود');
});

// ═══════════════════════════════════════════════════════════════════════════════
// Usage Log Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Usage log parameters
class UsageLogParams {
  final String equipmentId;
  final DateTime? from;
  final DateTime? to;
  final UsageType? usageType;
  final int limit;

  const UsageLogParams({
    required this.equipmentId,
    this.from,
    this.to,
    this.usageType,
    this.limit = 50,
  });

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UsageLogParams &&
        other.equipmentId == equipmentId &&
        other.from == from &&
        other.to == to &&
        other.usageType == usageType &&
        other.limit == limit;
  }

  @override
  int get hashCode => Object.hash(equipmentId, from, to, usageType, limit);
}

/// Usage logs for equipment
final equipmentUsageLogsProvider = FutureProvider.autoDispose
    .family<List<UsageLog>, UsageLogParams>((ref, params) async {
  final api = ref.watch(equipmentRepositoryProvider);
  final localDb = ref.watch(equipmentLocalDbProvider);

  try {
    final result = await api.getUsageLogs(
      params.equipmentId,
      from: params.from,
      to: params.to,
      usageType: params.usageType,
      limit: params.limit,
    );

    if (result.isSuccess && result.data != null) {
      await localDb.saveUsageLogs(params.equipmentId, result.data!);
      return result.data!;
    }

    return localDb.getUsageLogs(
      params.equipmentId,
      from: params.from,
      to: params.to,
      usageType: params.usageType,
    );
  } catch (e) {
    return localDb.getUsageLogs(
      params.equipmentId,
      from: params.from,
      to: params.to,
      usageType: params.usageType,
    );
  }
});

/// Simple usage logs provider by equipment ID only
final equipmentUsageLogsSimpleProvider = FutureProvider.autoDispose
    .family<List<UsageLog>, String>((ref, equipmentId) async {
  return ref.watch(equipmentUsageLogsProvider(UsageLogParams(
    equipmentId: equipmentId,
  )).future);
});

/// Usage summary for equipment
final equipmentUsageSummaryProvider = FutureProvider.autoDispose
    .family<UsageSummary, String>((ref, equipmentId) async {
  final api = ref.watch(equipmentRepositoryProvider);

  final result = await api.getUsageSummary(
    equipmentId,
    from: DateTime.now().subtract(const Duration(days: 30)),
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }

  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب ملخص الاستخدام');
});

/// Active usage session for equipment
final activeUsageSessionProvider = FutureProvider.autoDispose
    .family<UsageLog?, String>((ref, equipmentId) async {
  final localDb = ref.watch(equipmentLocalDbProvider);
  return localDb.getActiveUsageSession(equipmentId);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Filter State
// ═══════════════════════════════════════════════════════════════════════════════

/// Equipment filter class
class EquipmentFilter {
  final EquipmentType? type;
  final EquipmentStatus? status;
  final String? fieldId;
  final String? search;

  const EquipmentFilter({
    this.type,
    this.status,
    this.fieldId,
    this.search,
  });

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
      type != null || status != null || fieldId != null || (search != null && search!.isNotEmpty);

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is EquipmentFilter &&
        other.type == type &&
        other.status == status &&
        other.fieldId == fieldId &&
        other.search == search;
  }

  @override
  int get hashCode => Object.hash(type, status, fieldId, search);
}

/// Selected filter state
final selectedEquipmentFilterProvider = StateProvider<EquipmentFilter?>((ref) => null);

// ═══════════════════════════════════════════════════════════════════════════════
// Equipment Controller
// ═══════════════════════════════════════════════════════════════════════════════

/// Equipment Controller for CRUD operations
class EquipmentController extends StateNotifier<AsyncValue<void>> {
  final EquipmentApi _api;
  final EquipmentLocalDb _localDb;
  final Ref _ref;

  EquipmentController(this._api, this._localDb, this._ref)
      : super(const AsyncValue.data(null));

  // ─────────────────────────────────────────────────────────────────────────────
  // Equipment CRUD
  // ─────────────────────────────────────────────────────────────────────────────

  /// Create new equipment
  Future<bool> createEquipment({
    required String name,
    String? nameAr,
    required EquipmentType type,
    String? serialNumber,
    String? brand,
    String? model,
    int? year,
    String? fieldId,
    String? locationName,
    int? horsepower,
    FuelType? fuelType,
    double? fuelCapacityLiters,
  }) async {
    state = const AsyncValue.loading();

    final result = await _api.createEquipment(
      name: name,
      nameAr: nameAr,
      type: type,
      serialNumber: serialNumber,
      brand: brand,
      model: model,
      year: year,
      fieldId: fieldId,
      locationName: locationName,
      horsepower: horsepower,
      fuelType: fuelType,
      fuelCapacityLiters: fuelCapacityLiters,
    );

    if (result.isSuccess && result.data != null) {
      await _localDb.saveEquipment(result.data!);
      state = const AsyncValue.data(null);
      _invalidateProviders();
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء المعدة',
      StackTrace.current,
    );
    return false;
  }

  /// Update equipment status
  Future<bool> updateStatus(String equipmentId, EquipmentStatus status) async {
    state = const AsyncValue.loading();

    final result = await _api.updateEquipmentStatus(equipmentId, status);

    if (result.isSuccess) {
      if (result.data != null) {
        await _localDb.saveEquipment(result.data!);
      }
      state = const AsyncValue.data(null);
      _invalidateProviders();
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الحالة',
      StackTrace.current,
    );
    return false;
  }

  /// Update equipment location
  Future<bool> updateLocation(
    String equipmentId,
    double lat,
    double lon, [
    String? locationName,
  ]) async {
    state = const AsyncValue.loading();

    final result = await _api.updateEquipmentLocation(
      equipmentId,
      lat: lat,
      lon: lon,
      locationName: locationName,
    );

    if (result.isSuccess) {
      if (result.data != null) {
        await _localDb.saveEquipment(result.data!);
      }
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

  /// Delete equipment
  Future<bool> deleteEquipment(String equipmentId) async {
    state = const AsyncValue.loading();

    final result = await _api.deleteEquipment(equipmentId);

    if (result.isSuccess) {
      await _localDb.deleteEquipment(equipmentId);
      await _localDb.clearEquipmentCache(equipmentId);
      state = const AsyncValue.data(null);
      _invalidateProviders();
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حذف المعدة',
      StackTrace.current,
    );
    return false;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Maintenance Operations
  // ─────────────────────────────────────────────────────────────────────────────

  /// Add maintenance record
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

    final result = await _api.addMaintenanceRecord(
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

    if (result.isSuccess && result.data != null) {
      await _localDb.addMaintenanceRecord(result.data!);
      state = const AsyncValue.data(null);
      _ref.invalidate(maintenanceAlertsProvider);
      _ref.invalidate(equipmentMaintenanceHistoryProvider);
      _ref.invalidate(equipmentDetailsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إضافة سجل الصيانة',
      StackTrace.current,
    );
    return false;
  }

  /// Schedule maintenance
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

    final result = await _api.scheduleMaintenance(
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
      _ref.invalidate(scheduledMaintenancesProvider);
      _ref.invalidate(equipmentDetailsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في جدولة الصيانة',
      StackTrace.current,
    );
    return false;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Fuel Operations
  // ─────────────────────────────────────────────────────────────────────────────

  /// Add fuel log entry
  Future<bool> addFuelLog(
    String equipmentId, {
    required FuelOperationType operationType,
    required double quantity,
    FuelType? fuelType,
    double? pricePerLiter,
    double? totalCost,
    double? odometerReading,
    String? odometerUnit,
    double? fuelLevelBefore,
    double? fuelLevelAfter,
    String? stationName,
    String? receiptNumber,
    String? notes,
    String? notesAr,
    double? lat,
    double? lon,
  }) async {
    state = const AsyncValue.loading();

    final result = await _api.addFuelLog(
      equipmentId,
      operationType: operationType,
      quantity: quantity,
      fuelType: fuelType,
      pricePerLiter: pricePerLiter,
      totalCost: totalCost,
      odometerReading: odometerReading,
      odometerUnit: odometerUnit,
      fuelLevelBefore: fuelLevelBefore,
      fuelLevelAfter: fuelLevelAfter,
      stationName: stationName,
      receiptNumber: receiptNumber,
      notes: notes,
      notesAr: notesAr,
      lat: lat,
      lon: lon,
    );

    if (result.isSuccess && result.data != null) {
      await _localDb.addFuelLog(result.data!);
      state = const AsyncValue.data(null);
      _ref.invalidate(equipmentFuelLogsProvider);
      _ref.invalidate(equipmentFuelLogsSimpleProvider);
      _ref.invalidate(fuelConsumptionSummaryProvider);
      _ref.invalidate(equipmentDetailsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إضافة سجل الوقود',
      StackTrace.current,
    );
    return false;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Usage Operations
  // ─────────────────────────────────────────────────────────────────────────────

  /// Start usage session
  Future<UsageLog?> startUsageSession(
    String equipmentId, {
    required UsageType usageType,
    FieldActivityType? activityType,
    String? fieldId,
    String? operatorId,
    String? operatorName,
    double? startHourReading,
    String? notes,
  }) async {
    state = const AsyncValue.loading();

    final result = await _api.startUsageSession(
      equipmentId,
      usageType: usageType,
      activityType: activityType,
      fieldId: fieldId,
      operatorId: operatorId,
      operatorName: operatorName,
      startHourReading: startHourReading,
      notes: notes,
    );

    if (result.isSuccess && result.data != null) {
      await _localDb.saveUsageLog(result.data!);
      state = const AsyncValue.data(null);
      _ref.invalidate(equipmentUsageLogsProvider);
      _ref.invalidate(activeUsageSessionProvider);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في بدء جلسة الاستخدام',
      StackTrace.current,
    );
    return null;
  }

  /// End usage session
  Future<bool> endUsageSession(
    String equipmentId,
    String logId, {
    double? endHourReading,
    double? fuelUsed,
    double? areaWorked,
    double? distanceTraveled,
    String? notes,
  }) async {
    state = const AsyncValue.loading();

    final result = await _api.endUsageSession(
      equipmentId,
      logId,
      endHourReading: endHourReading,
      fuelUsed: fuelUsed,
      areaWorked: areaWorked,
      distanceTraveled: distanceTraveled,
      notes: notes,
    );

    if (result.isSuccess && result.data != null) {
      await _localDb.saveUsageLog(result.data!);
      state = const AsyncValue.data(null);
      _ref.invalidate(equipmentUsageLogsProvider);
      _ref.invalidate(equipmentUsageLogsSimpleProvider);
      _ref.invalidate(equipmentUsageSummaryProvider);
      _ref.invalidate(activeUsageSessionProvider);
      _ref.invalidate(equipmentDetailsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنهاء جلسة الاستخدام',
      StackTrace.current,
    );
    return false;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Telemetry
  // ─────────────────────────────────────────────────────────────────────────────

  /// Update telemetry data
  Future<bool> updateTelemetry(
    String equipmentId, {
    double? fuelPercent,
    double? hours,
    double? lat,
    double? lon,
  }) async {
    state = const AsyncValue.loading();

    final result = await _api.updateTelemetry(
      equipmentId,
      fuelPercent: fuelPercent,
      hours: hours,
      lat: lat,
      lon: lon,
    );

    if (result.isSuccess) {
      if (result.data != null) {
        await _localDb.saveEquipment(result.data!);
      }
      state = const AsyncValue.data(null);
      _ref.invalidate(equipmentDetailsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث القياسات',
      StackTrace.current,
    );
    return false;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Sync
  // ─────────────────────────────────────────────────────────────────────────────

  /// Sync pending operations
  Future<int> syncPendingOperations() async {
    final operations = await _localDb.getPendingOperations();
    var synced = 0;

    for (final op in operations) {
      try {
        bool success = false;

        switch (op.entity) {
          case 'fuel':
            if (op.type == 'create') {
              final result = await _api.addFuelLog(
                op.data['equipment_id'] as String,
                operationType: FuelOperationType.values.firstWhere(
                  (e) => e.value == op.data['operation_type'],
                ),
                quantity: op.data['quantity'] as double,
                pricePerLiter: op.data['price_per_liter'] as double?,
                totalCost: op.data['total_cost'] as double?,
              );
              success = result.isSuccess;
            }
            break;
          case 'usage':
            // Handle usage sync
            break;
          case 'maintenance':
            // Handle maintenance sync
            break;
        }

        if (success) {
          await _localDb.removePendingOperation(op.id);
          synced++;
        } else if (op.retryCount >= 3) {
          await _localDb.removePendingOperation(op.id);
        } else {
          await _localDb.updatePendingOperation(
            op.copyWith(retryCount: op.retryCount + 1),
          );
        }
      } catch (e) {
        if (op.retryCount >= 3) {
          await _localDb.removePendingOperation(op.id);
        }
      }
    }

    return synced;
  }

  /// Check if there are pending operations
  Future<bool> hasPendingOperations() async {
    return _localDb.hasPendingOperations();
  }

  /// Get pending operations count
  Future<int> getPendingOperationsCount() async {
    return _localDb.getPendingOperationsCount();
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────────────────────────────────────

  void _invalidateProviders() {
    _ref.invalidate(equipmentListProvider);
    _ref.invalidate(equipmentStatsProvider);
    _ref.invalidate(maintenanceAlertsProvider);
  }
}

/// Equipment Controller Provider
final equipmentControllerProvider =
    StateNotifierProvider<EquipmentController, AsyncValue<void>>((ref) {
  final api = ref.watch(equipmentRepositoryProvider);
  final localDb = ref.watch(equipmentLocalDbProvider);
  return EquipmentController(api, localDb, ref);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Sync Status Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Last sync time
final lastSyncTimeProvider = FutureProvider.autoDispose<DateTime?>((ref) async {
  final localDb = ref.watch(equipmentLocalDbProvider);
  return localDb.getLastSyncTime();
});

/// Pending operations count
final pendingOperationsCountProvider = FutureProvider.autoDispose<int>((ref) async {
  final localDb = ref.watch(equipmentLocalDbProvider);
  return localDb.getPendingOperationsCount();
});

/// Cache staleness
final isCacheStaleProvider = FutureProvider.autoDispose<bool>((ref) async {
  final localDb = ref.watch(equipmentLocalDbProvider);
  return localDb.isCacheStale();
});
