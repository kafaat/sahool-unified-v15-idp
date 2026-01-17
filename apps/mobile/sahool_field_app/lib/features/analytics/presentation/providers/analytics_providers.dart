/// Analytics Providers - Riverpod State Management for Analytics
/// موفرو التحليلات - إدارة الحالة بـ Riverpod للتحليلات
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/analytics_models.dart';
import '../../data/repositories/analytics_repository.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Repository Provider
// موفر المستودع
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for AnalyticsRepository instance
/// موفر لنسخة مستودع التحليلات
final analyticsRepositoryProvider = Provider<AnalyticsRepository>((ref) {
  final repository = AnalyticsRepository();
  ref.onDispose(() => repository.dispose());
  return repository;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Field Health Score
// درجة صحة الحقل
// ═══════════════════════════════════════════════════════════════════════════════

/// Parameters for field health calculation
/// معلمات حساب صحة الحقل
class FieldHealthParams {
  final String fieldId;
  final String fieldName;
  final double? ndvi;
  final double? soilMoisture;
  final double? temperature;
  final double? humidity;
  final String? cropType;

  const FieldHealthParams({
    required this.fieldId,
    required this.fieldName,
    this.ndvi,
    this.soilMoisture,
    this.temperature,
    this.humidity,
    this.cropType,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FieldHealthParams &&
          fieldId == other.fieldId &&
          ndvi == other.ndvi &&
          soilMoisture == other.soilMoisture;

  @override
  int get hashCode => Object.hash(fieldId, ndvi, soilMoisture);
}

/// Provider for field health score
/// موفر درجة صحة الحقل
final fieldHealthScoreProvider =
    FutureProvider.family<FieldHealthScore, FieldHealthParams>((ref, params) async {
  final repository = ref.watch(analyticsRepositoryProvider);
  return repository.calculateFieldHealth(
    fieldId: params.fieldId,
    fieldName: params.fieldName,
    ndvi: params.ndvi,
    soilMoisture: params.soilMoisture,
    temperature: params.temperature,
    humidity: params.humidity,
    cropType: params.cropType,
  );
});

// ═══════════════════════════════════════════════════════════════════════════════
// Yield Prediction
// توقع الإنتاجية
// ═══════════════════════════════════════════════════════════════════════════════

/// Parameters for yield prediction
/// معلمات توقع الإنتاجية
class YieldPredictionParams {
  final String fieldId;
  final String cropType;
  final double fieldAreaHectares;
  final double? ndvi;
  final double? soilMoisture;
  final int? daysToHarvest;

  const YieldPredictionParams({
    required this.fieldId,
    required this.cropType,
    required this.fieldAreaHectares,
    this.ndvi,
    this.soilMoisture,
    this.daysToHarvest,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is YieldPredictionParams &&
          fieldId == other.fieldId &&
          cropType == other.cropType &&
          fieldAreaHectares == other.fieldAreaHectares;

  @override
  int get hashCode => Object.hash(fieldId, cropType, fieldAreaHectares);
}

/// Provider for yield prediction
/// موفر توقع الإنتاجية
final yieldPredictionProvider =
    FutureProvider.family<YieldPrediction, YieldPredictionParams>((ref, params) async {
  final repository = ref.watch(analyticsRepositoryProvider);
  return repository.predictYield(
    fieldId: params.fieldId,
    cropType: params.cropType,
    fieldAreaHectares: params.fieldAreaHectares,
    ndvi: params.ndvi,
    soilMoisture: params.soilMoisture,
    daysToHarvest: params.daysToHarvest,
  );
});

// ═══════════════════════════════════════════════════════════════════════════════
// Risk Assessment
// تقييم المخاطر
// ═══════════════════════════════════════════════════════════════════════════════

/// Parameters for risk assessment
/// معلمات تقييم المخاطر
class RiskAssessmentParams {
  final String fieldId;
  final double? temperature;
  final double? humidity;
  final double? rainfall;
  final double? ndvi;
  final String? cropType;

  const RiskAssessmentParams({
    required this.fieldId,
    this.temperature,
    this.humidity,
    this.rainfall,
    this.ndvi,
    this.cropType,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RiskAssessmentParams &&
          fieldId == other.fieldId &&
          temperature == other.temperature &&
          humidity == other.humidity;

  @override
  int get hashCode => Object.hash(fieldId, temperature, humidity);
}

/// Provider for risk assessment
/// موفر تقييم المخاطر
final riskAssessmentProvider =
    FutureProvider.family<RiskAssessment, RiskAssessmentParams>((ref, params) async {
  final repository = ref.watch(analyticsRepositoryProvider);
  return repository.assessRisks(
    fieldId: params.fieldId,
    temperature: params.temperature,
    humidity: params.humidity,
    rainfall: params.rainfall,
    ndvi: params.ndvi,
    cropType: params.cropType,
  );
});

// ═══════════════════════════════════════════════════════════════════════════════
// Analytics Summary
// ملخص التحليلات
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for analytics summary
/// موفر ملخص التحليلات
final analyticsSummaryProvider =
    FutureProvider.family<AnalyticsSummary, List<String>>((ref, fieldIds) async {
  final repository = ref.watch(analyticsRepositoryProvider);
  return repository.getAnalyticsSummary(fieldIds);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Historical Trends
// الاتجاهات التاريخية
// ═══════════════════════════════════════════════════════════════════════════════

/// Parameters for historical trend
/// معلمات الاتجاه التاريخي
class HistoricalTrendParams {
  final String fieldId;
  final String metricName;
  final int days;

  const HistoricalTrendParams({
    required this.fieldId,
    required this.metricName,
    this.days = 30,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is HistoricalTrendParams &&
          fieldId == other.fieldId &&
          metricName == other.metricName &&
          days == other.days;

  @override
  int get hashCode => Object.hash(fieldId, metricName, days);
}

/// Provider for historical trend
/// موفر الاتجاه التاريخي
final historicalTrendProvider =
    FutureProvider.family<HistoricalTrend, HistoricalTrendParams>((ref, params) async {
  final repository = ref.watch(analyticsRepositoryProvider);
  return repository.getHistoricalTrend(
    fieldId: params.fieldId,
    metricName: params.metricName,
    days: params.days,
  );
});

// ═══════════════════════════════════════════════════════════════════════════════
// Dashboard State
// حالة لوحة التحكم
// ═══════════════════════════════════════════════════════════════════════════════

/// State for analytics dashboard
/// حالة لوحة تحكم التحليلات
class AnalyticsDashboardState {
  final bool isLoading;
  final String? selectedFieldId;
  final FieldHealthScore? selectedFieldHealth;
  final YieldPrediction? selectedYieldPrediction;
  final RiskAssessment? selectedRiskAssessment;
  final AnalyticsSummary? summary;
  final String? error;
  final DateRange selectedDateRange;

  const AnalyticsDashboardState({
    this.isLoading = false,
    this.selectedFieldId,
    this.selectedFieldHealth,
    this.selectedYieldPrediction,
    this.selectedRiskAssessment,
    this.summary,
    this.error,
    this.selectedDateRange = DateRange.week,
  });

  AnalyticsDashboardState copyWith({
    bool? isLoading,
    String? selectedFieldId,
    FieldHealthScore? selectedFieldHealth,
    YieldPrediction? selectedYieldPrediction,
    RiskAssessment? selectedRiskAssessment,
    AnalyticsSummary? summary,
    String? error,
    DateRange? selectedDateRange,
  }) {
    return AnalyticsDashboardState(
      isLoading: isLoading ?? this.isLoading,
      selectedFieldId: selectedFieldId ?? this.selectedFieldId,
      selectedFieldHealth: selectedFieldHealth ?? this.selectedFieldHealth,
      selectedYieldPrediction: selectedYieldPrediction ?? this.selectedYieldPrediction,
      selectedRiskAssessment: selectedRiskAssessment ?? this.selectedRiskAssessment,
      summary: summary ?? this.summary,
      error: error,
      selectedDateRange: selectedDateRange ?? this.selectedDateRange,
    );
  }
}

enum DateRange { week, month, quarter, year }

/// Notifier for analytics dashboard
/// مُعلم لوحة تحكم التحليلات
class AnalyticsDashboardNotifier extends StateNotifier<AnalyticsDashboardState> {
  final AnalyticsRepository _repository;

  AnalyticsDashboardNotifier(this._repository) : super(const AnalyticsDashboardState());

  /// Load analytics for a specific field
  /// تحميل التحليلات لحقل محدد
  Future<void> loadFieldAnalytics({
    required String fieldId,
    required String fieldName,
    double? ndvi,
    double? soilMoisture,
    double? temperature,
    double? humidity,
    String? cropType,
    double? fieldArea,
    double? rainfall,
  }) async {
    state = state.copyWith(isLoading: true, error: null, selectedFieldId: fieldId);

    try {
      // Load all analytics in parallel
      final results = await Future.wait([
        _repository.calculateFieldHealth(
          fieldId: fieldId,
          fieldName: fieldName,
          ndvi: ndvi,
          soilMoisture: soilMoisture,
          temperature: temperature,
          humidity: humidity,
          cropType: cropType,
        ),
        if (cropType != null && fieldArea != null)
          _repository.predictYield(
            fieldId: fieldId,
            cropType: cropType,
            fieldAreaHectares: fieldArea,
            ndvi: ndvi,
            soilMoisture: soilMoisture,
          ),
        _repository.assessRisks(
          fieldId: fieldId,
          temperature: temperature,
          humidity: humidity,
          rainfall: rainfall,
          ndvi: ndvi,
          cropType: cropType,
        ),
      ]);

      state = state.copyWith(
        isLoading: false,
        selectedFieldHealth: results[0] as FieldHealthScore,
        selectedYieldPrediction: results.length > 2 ? results[1] as YieldPrediction? : null,
        selectedRiskAssessment: results.last as RiskAssessment,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Load summary for all fields
  /// تحميل الملخص لجميع الحقول
  Future<void> loadSummary(List<String> fieldIds) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final summary = await _repository.getAnalyticsSummary(fieldIds);
      state = state.copyWith(
        isLoading: false,
        summary: summary,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Set date range for historical data
  /// تعيين نطاق التاريخ للبيانات التاريخية
  void setDateRange(DateRange range) {
    state = state.copyWith(selectedDateRange: range);
  }

  /// Clear selection
  /// مسح الاختيار
  void clearSelection() {
    state = const AnalyticsDashboardState();
  }

  /// Refresh current data
  /// تحديث البيانات الحالية
  Future<void> refresh() async {
    if (state.selectedFieldId != null && state.selectedFieldHealth != null) {
      await loadFieldAnalytics(
        fieldId: state.selectedFieldId!,
        fieldName: state.selectedFieldHealth!.fieldName,
      );
    }
  }
}

/// Provider for analytics dashboard
/// موفر لوحة تحكم التحليلات
final analyticsDashboardProvider =
    StateNotifierProvider<AnalyticsDashboardNotifier, AnalyticsDashboardState>((ref) {
  final repository = ref.watch(analyticsRepositoryProvider);
  return AnalyticsDashboardNotifier(repository);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Comparison State
// حالة المقارنة
// ═══════════════════════════════════════════════════════════════════════════════

/// State for comparing fields
/// حالة مقارنة الحقول
class FieldComparisonState {
  final List<String> selectedFieldIds;
  final Map<String, FieldHealthScore> healthScores;
  final bool isLoading;
  final String? error;

  const FieldComparisonState({
    this.selectedFieldIds = const [],
    this.healthScores = const {},
    this.isLoading = false,
    this.error,
  });

  FieldComparisonState copyWith({
    List<String>? selectedFieldIds,
    Map<String, FieldHealthScore>? healthScores,
    bool? isLoading,
    String? error,
  }) {
    return FieldComparisonState(
      selectedFieldIds: selectedFieldIds ?? this.selectedFieldIds,
      healthScores: healthScores ?? this.healthScores,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Notifier for field comparison
/// مُعلم مقارنة الحقول
class FieldComparisonNotifier extends StateNotifier<FieldComparisonState> {
  final AnalyticsRepository _repository;

  FieldComparisonNotifier(this._repository) : super(const FieldComparisonState());

  /// Add field to comparison
  /// إضافة حقل للمقارنة
  void addField(String fieldId) {
    if (state.selectedFieldIds.length >= 5) return;
    if (state.selectedFieldIds.contains(fieldId)) return;

    state = state.copyWith(
      selectedFieldIds: [...state.selectedFieldIds, fieldId],
    );
  }

  /// Remove field from comparison
  /// إزالة حقل من المقارنة
  void removeField(String fieldId) {
    final updated = state.selectedFieldIds.where((id) => id != fieldId).toList();
    final scores = Map<String, FieldHealthScore>.from(state.healthScores)..remove(fieldId);

    state = state.copyWith(
      selectedFieldIds: updated,
      healthScores: scores,
    );
  }

  /// Load comparison data
  /// تحميل بيانات المقارنة
  Future<void> loadComparison(Map<String, String> fieldNames) async {
    if (state.selectedFieldIds.isEmpty) return;

    state = state.copyWith(isLoading: true, error: null);

    try {
      final scores = <String, FieldHealthScore>{};

      for (final fieldId in state.selectedFieldIds) {
        final score = await _repository.calculateFieldHealth(
          fieldId: fieldId,
          fieldName: fieldNames[fieldId] ?? fieldId,
        );
        scores[fieldId] = score;
      }

      state = state.copyWith(
        isLoading: false,
        healthScores: scores,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Clear all selections
  /// مسح جميع الاختيارات
  void clear() {
    state = const FieldComparisonState();
  }
}

/// Provider for field comparison
/// موفر مقارنة الحقول
final fieldComparisonProvider =
    StateNotifierProvider<FieldComparisonNotifier, FieldComparisonState>((ref) {
  final repository = ref.watch(analyticsRepositoryProvider);
  return FieldComparisonNotifier(repository);
});
