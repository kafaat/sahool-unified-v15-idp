/// Irrigation Providers - مزودات بيانات الري
/// Riverpod state management for Irrigation feature
/// إدارة حالة الري باستخدام Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/remote/irrigation_api.dart';
import '../../data/repository/irrigation_repository.dart';

// Re-export models for convenience
export '../../data/remote/irrigation_api.dart';
export '../../data/repository/irrigation_repository.dart'
    show ApiResult, WaterBalanceData, IrrigationEfficiencyData;

// ═══════════════════════════════════════════════════════════════════════════════
// Core Providers - المزودات الأساسية
// ═══════════════════════════════════════════════════════════════════════════════

/// Selected field ID state
/// حقل محدد حالياً
final selectedFieldIdProvider = StateProvider<String?>((ref) => null);

/// Selected crop ID state
/// محصول محدد حالياً
final selectedCropIdProvider = StateProvider<String?>((ref) => null);

/// Selected irrigation method state
/// طريقة ري محددة حالياً
final selectedMethodIdProvider = StateProvider<String?>((ref) => null);

// ═══════════════════════════════════════════════════════════════════════════════
// Reference Data Providers - مزودات البيانات المرجعية
// ═══════════════════════════════════════════════════════════════════════════════

/// Available crops for irrigation
/// المحاصيل المتاحة للري
final irrigationCropsProvider =
    FutureProvider.autoDispose<List<IrrigationCrop>>((ref) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  final result = await repo.getCrops();

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب المحاصيل');
});

/// Available irrigation methods
/// طرق الري المتاحة
final irrigationMethodsProvider =
    FutureProvider.autoDispose<List<IrrigationMethod>>((ref) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  final result = await repo.getMethods();

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب طرق الري');
});

// ═══════════════════════════════════════════════════════════════════════════════
// Schedule Providers - مزودات الجدولة
// ═══════════════════════════════════════════════════════════════════════════════

/// Irrigation schedule for a specific field
/// جدول الري لحقل محدد
final irrigationScheduleProvider = FutureProvider.autoDispose
    .family<IrrigationSchedule, String>((ref, fieldId) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  final result = await repo.getSchedule(fieldId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب جدول الري');
});

/// Schedule for currently selected field
/// جدول الري للحقل المحدد حالياً
final currentFieldScheduleProvider =
    FutureProvider.autoDispose<IrrigationSchedule?>((ref) async {
  final fieldId = ref.watch(selectedFieldIdProvider);
  if (fieldId == null) return null;

  final repo = ref.watch(irrigationRepositoryProvider);
  final result = await repo.getSchedule(fieldId);

  if (result.isSuccess && result.data != null) {
    return result.data;
  }
  return null;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Water Balance Providers - مزودات توازن المياه
// ═══════════════════════════════════════════════════════════════════════════════

/// Water balance parameters
class WaterBalanceParams {
  final String fieldId;
  final DateTime from;
  final DateTime to;

  const WaterBalanceParams({
    required this.fieldId,
    required this.from,
    required this.to,
  });

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is WaterBalanceParams &&
        other.fieldId == fieldId &&
        other.from == from &&
        other.to == to;
  }

  @override
  int get hashCode => Object.hash(fieldId, from, to);
}

/// Water balance for a specific field and date range
/// توازن المياه لحقل ونطاق تاريخ محدد
final waterBalanceProvider = FutureProvider.autoDispose
    .family<WaterBalanceData, WaterBalanceParams>((ref, params) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  final result = await repo.calculateWaterBalance(
    fieldId: params.fieldId,
    from: params.from,
    to: params.to,
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(
    result.errorAr ?? result.error ?? 'فشل في حساب توازن المياه',
  );
});

/// Water balance for the currently selected field (last 7 days)
/// توازن المياه للحقل المحدد (آخر 7 أيام)
final currentFieldWaterBalanceProvider =
    FutureProvider.autoDispose<WaterBalanceData?>((ref) async {
  final fieldId = ref.watch(selectedFieldIdProvider);
  if (fieldId == null) return null;

  final repo = ref.watch(irrigationRepositoryProvider);
  final now = DateTime.now();
  final result = await repo.calculateWaterBalance(
    fieldId: fieldId,
    from: now.subtract(const Duration(days: 7)),
    to: now,
  );

  if (result.isSuccess && result.data != null) {
    return result.data;
  }
  return null;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Calculation Providers - مزودات الحسابات
// ═══════════════════════════════════════════════════════════════════════════════

/// Irrigation calculation parameters
class IrrigationCalcParams {
  final String cropId;
  final String methodId;
  final double areaHectares;
  final double et0;
  final double? soilMoistureCurrent;
  final double? soilMoistureFieldCapacity;
  final String? growthStage;

  const IrrigationCalcParams({
    required this.cropId,
    required this.methodId,
    required this.areaHectares,
    required this.et0,
    this.soilMoistureCurrent,
    this.soilMoistureFieldCapacity,
    this.growthStage,
  });

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is IrrigationCalcParams &&
        other.cropId == cropId &&
        other.methodId == methodId &&
        other.areaHectares == areaHectares &&
        other.et0 == et0 &&
        other.soilMoistureCurrent == soilMoistureCurrent &&
        other.growthStage == growthStage;
  }

  @override
  int get hashCode => Object.hash(
        cropId,
        methodId,
        areaHectares,
        et0,
        soilMoistureCurrent,
        growthStage,
      );
}

/// Irrigation calculation result
/// نتيجة حساب الري
final irrigationCalculationProvider = FutureProvider.autoDispose
    .family<IrrigationCalculation, IrrigationCalcParams>((ref, params) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  final result = await repo.calculate(
    IrrigationCalculationRequest(
      cropId: params.cropId,
      methodId: params.methodId,
      areaHectares: params.areaHectares,
      et0: params.et0,
      soilMoistureCurrent: params.soilMoistureCurrent,
      soilMoistureFieldCapacity: params.soilMoistureFieldCapacity,
      growthStage: params.growthStage,
    ),
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(
    result.errorAr ?? result.error ?? 'فشل في حساب احتياجات الري',
  );
});

// ═══════════════════════════════════════════════════════════════════════════════
// Dashboard Summary Provider - مزود ملخص لوحة التحكم
// ═══════════════════════════════════════════════════════════════════════════════

/// Summary data for the irrigation dashboard
/// بيانات ملخصة للوحة الري
class IrrigationDashboardSummary {
  final WaterBalanceData? waterBalance;
  final IrrigationSchedule? schedule;
  final List<IrrigationCrop> crops;
  final List<IrrigationMethod> methods;
  final IrrigationEvent? nextEvent;
  final bool isFromCache;

  IrrigationDashboardSummary({
    this.waterBalance,
    this.schedule,
    this.crops = const [],
    this.methods = const [],
    this.nextEvent,
    this.isFromCache = false,
  });

  /// Next irrigation countdown in hours
  int? get hoursUntilNextIrrigation {
    if (nextEvent == null) return null;
    final diff = nextEvent!.scheduledAt.difference(DateTime.now());
    if (diff.isNegative) return 0;
    return diff.inHours;
  }
}

/// Dashboard summary for the currently selected field
/// ملخص لوحة التحكم للحقل المحدد
final irrigationDashboardProvider =
    FutureProvider.autoDispose<IrrigationDashboardSummary>((ref) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  final fieldId = ref.watch(selectedFieldIdProvider);

  // Fetch crops and methods in parallel
  final cropsResult = await repo.getCrops();
  final methodsResult = await repo.getMethods();

  final crops = cropsResult.data ?? [];
  final methods = methodsResult.data ?? [];

  WaterBalanceData? waterBalance;
  IrrigationSchedule? schedule;
  IrrigationEvent? nextEvent;
  var fromCache = false;

  if (fieldId != null) {
    final now = DateTime.now();
    final wbResult = await repo.calculateWaterBalance(
      fieldId: fieldId,
      from: now.subtract(const Duration(days: 7)),
      to: now,
    );
    waterBalance = wbResult.data;
    fromCache = fromCache || wbResult.isFromCache;

    final scheduleResult = await repo.getSchedule(fieldId);
    schedule = scheduleResult.data;
    fromCache = fromCache || scheduleResult.isFromCache;

    // Find next upcoming event
    if (schedule != null && schedule.events.isNotEmpty) {
      final upcoming = schedule.events
          .where((e) =>
              e.scheduledAt.isAfter(now) &&
              (e.status == 'scheduled' || e.status == 'pending'))
          .toList();
      if (upcoming.isNotEmpty) {
        upcoming.sort((a, b) => a.scheduledAt.compareTo(b.scheduledAt));
        nextEvent = upcoming.first;
      }
    }
  }

  return IrrigationDashboardSummary(
    waterBalance: waterBalance,
    schedule: schedule,
    crops: crops,
    methods: methods,
    nextEvent: nextEvent,
    isFromCache: fromCache,
  );
});

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Controller - متحكم الري
// ═══════════════════════════════════════════════════════════════════════════════

/// Controller for irrigation CRUD operations
/// متحكم لعمليات الري
class IrrigationController extends StateNotifier<AsyncValue<void>> {
  final IrrigationRepository _repo;
  final Ref _ref;

  IrrigationController(this._repo, this._ref)
      : super(const AsyncValue.data(null));

  /// Generate a new irrigation schedule
  /// إنشاء جدول ري جديد
  Future<IrrigationSchedule?> generateSchedule({
    required String fieldId,
    required String cropId,
    required String methodId,
    int days = 14,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.generateSchedule(
      fieldId: fieldId,
      cropId: cropId,
      methodId: methodId,
      days: days,
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      _ref.invalidate(irrigationScheduleProvider);
      _ref.invalidate(currentFieldScheduleProvider);
      _ref.invalidate(irrigationDashboardProvider);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء جدول الري',
      StackTrace.current,
    );
    return null;
  }

  /// Calculate irrigation needs
  /// حساب احتياجات الري
  Future<IrrigationCalculation?> calculateNeeds({
    required String cropId,
    required String methodId,
    required double areaHectares,
    required double et0,
    double? soilMoistureCurrent,
    double? soilMoistureFieldCapacity,
    String? growthStage,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.calculate(
      IrrigationCalculationRequest(
        cropId: cropId,
        methodId: methodId,
        areaHectares: areaHectares,
        et0: et0,
        soilMoistureCurrent: soilMoistureCurrent,
        soilMoistureFieldCapacity: soilMoistureFieldCapacity,
        growthStage: growthStage,
      ),
    );

    if (result.isSuccess && result.data != null) {
      state = const AsyncValue.data(null);
      return result.data;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حساب احتياجات الري',
      StackTrace.current,
    );
    return null;
  }

  /// Record a sensor reading
  /// تسجيل قراءة مستشعر
  Future<bool> recordSensorReading({
    required String fieldId,
    required String sensorType,
    required double value,
    required String unit,
  }) async {
    state = const AsyncValue.loading();

    final result = await _repo.recordSensorReading(
      fieldId: fieldId,
      sensorType: sensorType,
      value: value,
      unit: unit,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(currentFieldWaterBalanceProvider);
      _ref.invalidate(irrigationDashboardProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تسجيل القراءة',
      StackTrace.current,
    );
    return false;
  }

  /// Sync all pending operations
  /// مزامنة العمليات المعلقة
  Future<int> syncPending() async {
    return _repo.syncPendingOperations();
  }

  /// Refresh all irrigation data
  /// تحديث جميع بيانات الري
  void refreshAll() {
    _ref.invalidate(irrigationCropsProvider);
    _ref.invalidate(irrigationMethodsProvider);
    _ref.invalidate(irrigationScheduleProvider);
    _ref.invalidate(currentFieldScheduleProvider);
    _ref.invalidate(currentFieldWaterBalanceProvider);
    _ref.invalidate(irrigationDashboardProvider);
  }
}

/// Irrigation Controller Provider
/// مزود متحكم الري
final irrigationControllerProvider =
    StateNotifierProvider<IrrigationController, AsyncValue<void>>((ref) {
  final repo = ref.watch(irrigationRepositoryProvider);
  return IrrigationController(repo, ref);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Sync Status Providers - مزودات حالة المزامنة
// ═══════════════════════════════════════════════════════════════════════════════

/// Pending operations count
/// عدد العمليات المعلقة
final irrigationPendingOpsCountProvider =
    FutureProvider.autoDispose<int>((ref) async {
  final repo = ref.watch(irrigationRepositoryProvider);
  return repo.getPendingOperationsCount();
});
