/// Profitability Providers - مزودات تحليل الربحية
/// State management for profitability analysis
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/profitability_models.dart';
import '../services/profitability_service.dart';

// ═════════════════════════════════════════════════════════════════════════════
// State Classes
// ═════════════════════════════════════════════════════════════════════════════

/// حالة تحليل الربحية
class ProfitabilityState {
  final CropProfitability? data;
  final bool isLoading;
  final String? error;
  final String? errorAr;

  const ProfitabilityState({
    this.data,
    this.isLoading = false,
    this.error,
    this.errorAr,
  });

  ProfitabilityState copyWith({
    CropProfitability? data,
    bool? isLoading,
    String? error,
    String? errorAr,
  }) {
    return ProfitabilityState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      errorAr: errorAr,
    );
  }
}

/// حالة ملخص الموسم
class SeasonSummaryState {
  final SeasonSummary? data;
  final bool isLoading;
  final String? error;
  final String? errorAr;

  const SeasonSummaryState({
    this.data,
    this.isLoading = false,
    this.error,
    this.errorAr,
  });

  SeasonSummaryState copyWith({
    SeasonSummary? data,
    bool? isLoading,
    String? error,
    String? errorAr,
  }) {
    return SeasonSummaryState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      errorAr: errorAr,
    );
  }
}

/// حالة تفصيل التكاليف
class CostBreakdownState {
  final Map<String, double>? data;
  final bool isLoading;
  final String? error;
  final String? errorAr;

  const CostBreakdownState({
    this.data,
    this.isLoading = false,
    this.error,
    this.errorAr,
  });

  CostBreakdownState copyWith({
    Map<String, double>? data,
    bool? isLoading,
    String? error,
    String? errorAr,
  }) {
    return CostBreakdownState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      errorAr: errorAr,
    );
  }
}

/// حالة مقارنة المحاصيل
class CropComparisonState {
  final ProfitabilityComparison? data;
  final bool isLoading;
  final String? error;
  final String? errorAr;

  const CropComparisonState({
    this.data,
    this.isLoading = false,
    this.error,
    this.errorAr,
  });

  CropComparisonState copyWith({
    ProfitabilityComparison? data,
    bool? isLoading,
    String? error,
    String? errorAr,
  }) {
    return CropComparisonState(
      data: data ?? this.data,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      errorAr: errorAr,
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Notifiers
// ═════════════════════════════════════════════════════════════════════════════

/// Profitability Notifier
class ProfitabilityNotifier extends StateNotifier<ProfitabilityState> {
  final ProfitabilityService _service;

  ProfitabilityNotifier(this._service) : super(const ProfitabilityState());

  /// تحليل ربحية حقل
  Future<void> analyzeProfitability({
    required String fieldId,
    required String season,
  }) async {
    state = state.copyWith(isLoading: true, error: null, errorAr: null);

    final result = await _service.analyzeProfitability(
      fieldId: fieldId,
      season: season,
    );

    if (result.isSuccess && result.data != null) {
      state = state.copyWith(
        data: result.data,
        isLoading: false,
      );
    } else {
      state = state.copyWith(
        isLoading: false,
        error: result.error,
        errorAr: result.errorAr,
      );
    }
  }

  /// الحصول على تحليل محدد
  Future<void> getProfitabilityById(String profitabilityId) async {
    state = state.copyWith(isLoading: true, error: null, errorAr: null);

    final result = await _service.getProfitabilityById(profitabilityId);

    if (result.isSuccess && result.data != null) {
      state = state.copyWith(
        data: result.data,
        isLoading: false,
      );
    } else {
      state = state.copyWith(
        isLoading: false,
        error: result.error,
        errorAr: result.errorAr,
      );
    }
  }

  /// مسح البيانات
  void clear() {
    state = const ProfitabilityState();
  }
}

/// Season Summary Notifier
class SeasonSummaryNotifier extends StateNotifier<SeasonSummaryState> {
  final ProfitabilityService _service;

  SeasonSummaryNotifier(this._service) : super(const SeasonSummaryState());

  /// الحصول على ملخص الموسم
  Future<void> getSeasonSummary({
    required String farmId,
    required String season,
  }) async {
    state = state.copyWith(isLoading: true, error: null, errorAr: null);

    final result = await _service.getSeasonSummary(
      farmId: farmId,
      season: season,
    );

    if (result.isSuccess && result.data != null) {
      state = state.copyWith(
        data: result.data,
        isLoading: false,
      );
    } else {
      state = state.copyWith(
        isLoading: false,
        error: result.error,
        errorAr: result.errorAr,
      );
    }
  }

  /// مسح البيانات
  void clear() {
    state = const SeasonSummaryState();
  }
}

/// Cost Breakdown Notifier
class CostBreakdownNotifier extends StateNotifier<CostBreakdownState> {
  final ProfitabilityService _service;

  CostBreakdownNotifier(this._service) : super(const CostBreakdownState());

  /// الحصول على تفصيل التكاليف
  Future<void> getCostBreakdown({
    required String fieldId,
    String? season,
  }) async {
    state = state.copyWith(isLoading: true, error: null, errorAr: null);

    final result = await _service.getCostBreakdown(
      fieldId: fieldId,
      season: season,
    );

    if (result.isSuccess && result.data != null) {
      state = state.copyWith(
        data: result.data,
        isLoading: false,
      );
    } else {
      state = state.copyWith(
        isLoading: false,
        error: result.error,
        errorAr: result.errorAr,
      );
    }
  }

  /// مسح البيانات
  void clear() {
    state = const CostBreakdownState();
  }
}

/// Crop Comparison Notifier
class CropComparisonNotifier extends StateNotifier<CropComparisonState> {
  final ProfitabilityService _service;

  CropComparisonNotifier(this._service) : super(const CropComparisonState());

  /// مقارنة المحاصيل
  Future<void> compareCrops({
    required List<String> cropIds,
  }) async {
    state = state.copyWith(isLoading: true, error: null, errorAr: null);

    final result = await _service.compareCrops(cropIds: cropIds);

    if (result.isSuccess && result.data != null) {
      state = state.copyWith(
        data: result.data,
        isLoading: false,
      );
    } else {
      state = state.copyWith(
        isLoading: false,
        error: result.error,
        errorAr: result.errorAr,
      );
    }
  }

  /// مسح البيانات
  void clear() {
    state = const CropComparisonState();
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// Providers
// ═════════════════════════════════════════════════════════════════════════════

/// Profitability Provider
final profitabilityProvider =
    StateNotifierProvider<ProfitabilityNotifier, ProfitabilityState>((ref) {
  final service = ref.watch(profitabilityServiceProvider);
  return ProfitabilityNotifier(service);
});

/// Season Summary Provider
final seasonSummaryProvider =
    StateNotifierProvider<SeasonSummaryNotifier, SeasonSummaryState>((ref) {
  final service = ref.watch(profitabilityServiceProvider);
  return SeasonSummaryNotifier(service);
});

/// Cost Breakdown Provider
final costBreakdownProvider =
    StateNotifierProvider<CostBreakdownNotifier, CostBreakdownState>((ref) {
  final service = ref.watch(profitabilityServiceProvider);
  return CostBreakdownNotifier(service);
});

/// Crop Comparison Provider
final cropComparisonProvider =
    StateNotifierProvider<CropComparisonNotifier, CropComparisonState>((ref) {
  final service = ref.watch(profitabilityServiceProvider);
  return CropComparisonNotifier(service);
});

// ═════════════════════════════════════════════════════════════════════════════
// Future Providers (for one-time fetches)
// ═════════════════════════════════════════════════════════════════════════════

/// Field Profitability List Provider
final fieldProfitabilityListProvider = FutureProvider.family<
    List<CropProfitability>,
    ({String fieldId, String? season})>((ref, params) async {
  final service = ref.watch(profitabilityServiceProvider);
  final result = await service.getFieldProfitability(
    fieldId: params.fieldId,
    season: params.season,
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.error ?? 'Failed to fetch profitability');
});

/// Break-Even Analysis Provider
final breakEvenAnalysisProvider = FutureProvider.family<
    BreakEvenAnalysis,
    ({String fieldId, String? season})>((ref, params) async {
  final service = ref.watch(profitabilityServiceProvider);
  final result = await service.getBreakEvenPoint(
    fieldId: params.fieldId,
    season: params.season,
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.error ?? 'Failed to calculate break-even');
});

/// Historical Trend Provider
final historicalTrendProvider = FutureProvider.family<
    List<CropProfitability>,
    ({String fieldId, int years})>((ref, params) async {
  final service = ref.watch(profitabilityServiceProvider);
  final result = await service.getHistoricalTrend(
    fieldId: params.fieldId,
    years: params.years,
  );

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.error ?? 'Failed to fetch historical trend');
});

/// Farm Seasons Provider
final farmSeasonsProvider =
    FutureProvider.family<List<SeasonSummary>, String>((ref, farmId) async {
  final service = ref.watch(profitabilityServiceProvider);
  final result = await service.getFarmSeasons(farmId: farmId);

  if (result.isSuccess && result.data != null) {
    return result.data!;
  }
  throw Exception(result.error ?? 'Failed to fetch farm seasons');
});
