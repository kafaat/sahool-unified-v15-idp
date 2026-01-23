/// GDD Providers - مزودات بيانات درجات النمو الحراري
/// Riverpod providers للتواصل مع GDD Service
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/gdd_models.dart';
import '../services/gdd_service.dart';

// ═════════════════════════════════════════════════════════════════════════════
// Field GDD Data Providers
// ═════════════════════════════════════════════════════════════════════════════

/// مزود تراكم GDD للحقل
final fieldGDDProvider = FutureProvider.autoDispose
    .family<GDDAccumulation, String>((ref, fieldId) async {
  final service = ref.watch(gddServiceProvider);
  final result = await service.getGDDAccumulation(fieldId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب بيانات GDD');
});

/// مزود سجلات GDD اليومية
final gddRecordsProvider = FutureProvider.autoDispose
    .family<List<GDDRecord>, GDDRecordsParams>((ref, params) async {
  final service = ref.watch(gddServiceProvider);
  final result = await service.getGDDRecords(
    params.fieldId,
    startDate: params.startDate,
    endDate: params.endDate,
    limit: params.limit,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب سجلات GDD');
});

/// مزود المرحلة الحالية للنمو
final currentGrowthStageProvider = FutureProvider.autoDispose
    .family<GrowthStage?, String>((ref, fieldId) async {
  final service = ref.watch(gddServiceProvider);
  final result = await service.getCurrentGrowthStage(fieldId);

  if (result.isSuccess) {
    return result.data;
  }
  // إذا لم يتم العثور على مرحلة، نعيد null بدلاً من رمي خطأ
  if (result.error?.contains('not found') ?? false) {
    return null;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب مرحلة النمو');
});

/// مزود جميع مراحل النمو
final growthStagesProvider = FutureProvider.autoDispose
    .family<List<GrowthStage>, String>((ref, fieldId) async {
  final service = ref.watch(gddServiceProvider);
  final result = await service.getGrowthStages(fieldId);

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب مراحل النمو');
});

// ═════════════════════════════════════════════════════════════════════════════
// Crop Requirements Providers
// ═════════════════════════════════════════════════════════════════════════════

/// مزود متطلبات GDD للمحصول
final cropGDDRequirementsProvider = FutureProvider.autoDispose
    .family<CropGDDRequirements, CropType>((ref, cropType) async {
  final service = ref.watch(gddServiceProvider);
  final result = await service.getCropGDDRequirements(cropType);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(
    result.errorAr ?? result.error ?? 'فشل في جلب متطلبات المحصول',
  );
});

/// مزود قائمة المحاصيل المدعومة
final supportedCropsProvider = FutureProvider.autoDispose<List<CropGDDRequirements>>((ref) async {
  final service = ref.watch(gddServiceProvider);
  final result = await service.getSupportedCrops();

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(
    result.errorAr ?? result.error ?? 'فشل في جلب المحاصيل المدعومة',
  );
});

// ═════════════════════════════════════════════════════════════════════════════
// Forecast Providers
// ═════════════════════════════════════════════════════════════════════════════

/// مزود توقعات GDD
final gddForecastProvider = FutureProvider.autoDispose
    .family<List<GDDForecast>, GDDForecastParams>((ref, params) async {
  final service = ref.watch(gddServiceProvider);
  final result = await service.getGDDForecast(
    params.fieldId,
    days: params.days,
  );

  if (result.isSuccess) {
    return result.data ?? [];
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب توقعات GDD');
});

// ═════════════════════════════════════════════════════════════════════════════
// Settings Providers
// ═════════════════════════════════════════════════════════════════════════════

/// مزود إعدادات GDD للحقل
final gddSettingsProvider = FutureProvider.autoDispose
    .family<GDDSettings?, String>((ref, fieldId) async {
  final service = ref.watch(gddServiceProvider);
  final result = await service.getGDDSettings(fieldId);

  if (result.isSuccess) {
    return result.data;
  }
  // إذا لم يتم العثور على إعدادات، نعيد null
  if (result.error?.contains('not found') ?? false) {
    return null;
  }
  throw Exception(result.errorAr ?? result.error ?? 'فشل في جلب الإعدادات');
});

// ═════════════════════════════════════════════════════════════════════════════
// Chart Data Provider
// ═════════════════════════════════════════════════════════════════════════════

/// مزود بيانات الرسم البياني (يجمع السجلات والتوقعات)
final gddChartDataProvider = FutureProvider.autoDispose
    .family<GDDChartData, GDDChartParams>((ref, params) async {
  // جلب السجلات
  final recordsResult = await ref.watch(gddServiceProvider).getGDDRecords(
        params.fieldId,
        startDate: params.startDate,
        endDate: params.endDate,
        limit: params.limit,
      );

  // جلب التوقعات
  final forecastResult = params.includeForecast
      ? await ref.watch(gddServiceProvider).getGDDForecast(
            params.fieldId,
            days: params.forecastDays,
          )
      : null;

  // جلب مراحل النمو
  final stagesResult = params.includeStages
      ? await ref.watch(gddServiceProvider).getGrowthStages(params.fieldId)
      : null;

  final records = recordsResult.isSuccess ? (recordsResult.data ?? []) : <GDDRecord>[];
  final forecasts =
      forecastResult?.isSuccess ?? false ? (forecastResult!.data ?? []) : <GDDForecast>[];
  final stages = stagesResult?.isSuccess ?? false ? (stagesResult!.data ?? []) : <GrowthStage>[];

  return GDDChartData(
    records: records,
    forecasts: forecasts,
    stages: stages,
  );
});

// ═════════════════════════════════════════════════════════════════════════════
// State Providers
// ═════════════════════════════════════════════════════════════════════════════

/// مزود الحقل المحدد حالياً
final selectedFieldIdProvider = StateProvider<String?>((ref) => null);

/// مزود نطاق التاريخ المحدد
final selectedDateRangeProvider = StateProvider<DateRange?>((ref) => null);

/// مزود عرض التوقعات
final showForecastProvider = StateProvider<bool>((ref) => true);

/// مزود عرض مراحل النمو
final showGrowthStagesProvider = StateProvider<bool>((ref) => true);

// ═════════════════════════════════════════════════════════════════════════════
// Controller for Settings
// ═════════════════════════════════════════════════════════════════════════════

/// Controller لإدارة إعدادات GDD
class GDDSettingsController extends StateNotifier<AsyncValue<void>> {
  final GDDService _service;
  final Ref _ref;

  GDDSettingsController(this._service, this._ref) : super(const AsyncValue.data(null));

  /// تحديث إعدادات GDD
  Future<bool> updateSettings(String fieldId, GDDSettings settings) async {
    state = const AsyncValue.loading();

    final result = await _service.updateGDDSettings(fieldId, settings);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      // إلغاء البيانات المخزنة مؤقتاً
      _ref.invalidate(gddSettingsProvider);
      _ref.invalidate(fieldGDDProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في تحديث الإعدادات',
      StackTrace.current,
    );
    return false;
  }

  /// إنشاء إعدادات GDD جديدة
  Future<bool> createSettings(GDDSettings settings) async {
    state = const AsyncValue.loading();

    final result = await _service.createGDDSettings(settings);

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(gddSettingsProvider);
      _ref.invalidate(fieldGDDProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في إنشاء الإعدادات',
      StackTrace.current,
    );
    return false;
  }

  /// حساب GDD يدوياً
  Future<bool> calculateManualGDD({
    required String fieldId,
    required DateTime date,
    required double tMin,
    required double tMax,
    double? baseTemperature,
    double? upperThreshold,
    GDDCalculationMethod? method,
  }) async {
    state = const AsyncValue.loading();

    final result = await _service.calculateGDD(
      fieldId,
      date: date,
      tMin: tMin,
      tMax: tMax,
      baseTemperature: baseTemperature,
      upperThreshold: upperThreshold,
      method: method,
    );

    if (result.isSuccess) {
      state = const AsyncValue.data(null);
      _ref.invalidate(fieldGDDProvider);
      _ref.invalidate(gddRecordsProvider);
      return true;
    }

    state = AsyncValue.error(
      result.errorAr ?? result.error ?? 'فشل في حساب GDD',
      StackTrace.current,
    );
    return false;
  }
}

/// مزود Controller
final gddSettingsControllerProvider =
    StateNotifierProvider<GDDSettingsController, AsyncValue<void>>((ref) {
  final service = ref.watch(gddServiceProvider);
  return GDDSettingsController(service, ref);
});

// ═════════════════════════════════════════════════════════════════════════════
// Helper Classes
// ═════════════════════════════════════════════════════════════════════════════

/// معاملات سجلات GDD
class GDDRecordsParams {
  final String fieldId;
  final DateTime? startDate;
  final DateTime? endDate;
  final int limit;

  const GDDRecordsParams({
    required this.fieldId,
    this.startDate,
    this.endDate,
    this.limit = 100,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is GDDRecordsParams &&
          runtimeType == other.runtimeType &&
          fieldId == other.fieldId &&
          startDate == other.startDate &&
          endDate == other.endDate &&
          limit == other.limit;

  @override
  int get hashCode =>
      fieldId.hashCode ^ startDate.hashCode ^ endDate.hashCode ^ limit.hashCode;
}

/// معاملات توقعات GDD
class GDDForecastParams {
  final String fieldId;
  final int days;

  const GDDForecastParams({
    required this.fieldId,
    this.days = 7,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is GDDForecastParams &&
          runtimeType == other.runtimeType &&
          fieldId == other.fieldId &&
          days == other.days;

  @override
  int get hashCode => fieldId.hashCode ^ days.hashCode;
}

/// معاملات بيانات الرسم البياني
class GDDChartParams {
  final String fieldId;
  final DateTime? startDate;
  final DateTime? endDate;
  final int limit;
  final bool includeForecast;
  final int forecastDays;
  final bool includeStages;

  const GDDChartParams({
    required this.fieldId,
    this.startDate,
    this.endDate,
    this.limit = 100,
    this.includeForecast = true,
    this.forecastDays = 7,
    this.includeStages = true,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is GDDChartParams &&
          runtimeType == other.runtimeType &&
          fieldId == other.fieldId &&
          startDate == other.startDate &&
          endDate == other.endDate &&
          limit == other.limit &&
          includeForecast == other.includeForecast &&
          forecastDays == other.forecastDays &&
          includeStages == other.includeStages;

  @override
  int get hashCode =>
      fieldId.hashCode ^
      startDate.hashCode ^
      endDate.hashCode ^
      limit.hashCode ^
      includeForecast.hashCode ^
      forecastDays.hashCode ^
      includeStages.hashCode;
}

/// بيانات الرسم البياني
class GDDChartData {
  final List<GDDRecord> records;
  final List<GDDForecast> forecasts;
  final List<GrowthStage> stages;

  const GDDChartData({
    required this.records,
    required this.forecasts,
    required this.stages,
  });
}

/// نطاق التاريخ
class DateRange {
  final DateTime start;
  final DateTime end;

  const DateRange({
    required this.start,
    required this.end,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DateRange &&
          runtimeType == other.runtimeType &&
          start == other.start &&
          end == other.end;

  @override
  int get hashCode => start.hashCode ^ end.hashCode;
}
