/// Advisor Feature Providers - Riverpod State Management
/// موفرو ميزة المستشار - إدارة الحالة بـ Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/fertilizer_models.dart';
import '../../data/models/irrigation_models.dart';
import '../../data/repositories/advisor_repository.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Repository Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for AdvisorRepository instance
/// موفر لنسخة مستودع المستشار
final advisorRepositoryProvider = Provider<AdvisorRepository>((ref) {
  final repository = AdvisorRepository();
  ref.onDispose(() => repository.dispose());
  return repository;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Fertilizer Providers
// موفرو التسميد
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for available crop types
/// موفر أنواع المحاصيل المتاحة
final fertilizerCropsProvider = FutureProvider<List<CropTypeOption>>((ref) async {
  final repository = ref.watch(advisorRepositoryProvider);
  return repository.getFertilizerCrops();
});

/// Provider for fertilizer recommendation
/// موفر توصية التسميد
final fertilizerRecommendationProvider = FutureProvider.family<
    FertilizerRecommendation, FertilizerRequest>((ref, request) async {
  final repository = ref.watch(advisorRepositoryProvider);
  return repository.getFertilizerRecommendation(request);
});

/// Provider for soil interpretation
/// موفر تفسير التربة
final soilInterpretationProvider =
    FutureProvider.family<SoilInterpretation, SoilAnalysis>((ref, soilData) async {
  final repository = ref.watch(advisorRepositoryProvider);
  return repository.interpretSoil(soilData);
});

/// Provider for deficiency symptoms
/// موفر أعراض النقص
final deficiencySymptomsProvider = FutureProvider.family<
    List<DeficiencySymptom>, ({String? nutrient, String? cropType})>(
  (ref, params) async {
    final repository = ref.watch(advisorRepositoryProvider);
    return repository.getDeficiencySymptoms(
      nutrient: params.nutrient,
      cropType: params.cropType,
    );
  },
);

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Providers
// موفرو الري
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for crop water requirements
/// موفر متطلبات المحاصيل المائية
final irrigationCropsProvider =
    FutureProvider<List<CropWaterRequirement>>((ref) async {
  final repository = ref.watch(advisorRepositoryProvider);
  return repository.getIrrigationCrops();
});

/// Provider for irrigation methods
/// موفر طرق الري
final irrigationMethodsProvider =
    FutureProvider<List<IrrigationMethodOption>>((ref) async {
  final repository = ref.watch(advisorRepositoryProvider);
  return repository.getIrrigationMethods();
});

/// Provider for irrigation calculation
/// موفر حساب الري
final irrigationCalculationProvider = FutureProvider.family<
    IrrigationCalculation, IrrigationRequest>((ref, request) async {
  final repository = ref.watch(advisorRepositoryProvider);
  return repository.calculateIrrigation(request);
});

/// Provider for water balance
/// موفر التوازن المائي
final waterBalanceProvider = FutureProvider.family<
    WaterBalance,
    ({
      String fieldId,
      double soilMoisture,
      String soilType,
      String cropType
    })>((ref, params) async {
  final repository = ref.watch(advisorRepositoryProvider);
  return repository.getWaterBalance(
    fieldId: params.fieldId,
    soilMoisture: params.soilMoisture,
    soilType: params.soilType,
    cropType: params.cropType,
  );
});

/// Provider for irrigation efficiency report
/// موفر تقرير كفاءة الري
final irrigationEfficiencyProvider = FutureProvider.family<
    IrrigationEfficiencyReport, ({String fieldId, String period})>(
  (ref, params) async {
    final repository = ref.watch(advisorRepositoryProvider);
    return repository.getEfficiencyReport(
      fieldId: params.fieldId,
      period: params.period,
    );
  },
);

/// Provider for irrigation schedule
/// موفر جدول الري
final irrigationScheduleProvider =
    FutureProvider.family<IrrigationSchedule, String>((ref, fieldId) async {
  final repository = ref.watch(advisorRepositoryProvider);
  return repository.getIrrigationSchedule(fieldId);
});

// ═══════════════════════════════════════════════════════════════════════════════
// State Notifiers for User Interactions
// إشعارات الحالة لتفاعلات المستخدم
// ═══════════════════════════════════════════════════════════════════════════════

/// State for fertilizer recommendation form
/// حالة نموذج توصية التسميد
class FertilizerFormState {
  final String? selectedCropType;
  final String? selectedGrowthStage;
  final double? fieldArea;
  final SoilAnalysis? soilAnalysis;
  final String? irrigationType;
  final bool isLoading;
  final String? error;

  const FertilizerFormState({
    this.selectedCropType,
    this.selectedGrowthStage,
    this.fieldArea,
    this.soilAnalysis,
    this.irrigationType,
    this.isLoading = false,
    this.error,
  });

  FertilizerFormState copyWith({
    String? selectedCropType,
    String? selectedGrowthStage,
    double? fieldArea,
    SoilAnalysis? soilAnalysis,
    String? irrigationType,
    bool? isLoading,
    String? error,
  }) {
    return FertilizerFormState(
      selectedCropType: selectedCropType ?? this.selectedCropType,
      selectedGrowthStage: selectedGrowthStage ?? this.selectedGrowthStage,
      fieldArea: fieldArea ?? this.fieldArea,
      soilAnalysis: soilAnalysis ?? this.soilAnalysis,
      irrigationType: irrigationType ?? this.irrigationType,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  bool get isValid =>
      selectedCropType != null &&
      selectedGrowthStage != null &&
      fieldArea != null &&
      fieldArea! > 0 &&
      soilAnalysis != null;
}

/// Notifier for fertilizer form state
/// مُعلم حالة نموذج التسميد
class FertilizerFormNotifier extends StateNotifier<FertilizerFormState> {
  FertilizerFormNotifier() : super(const FertilizerFormState());

  void setCropType(String cropType) {
    state = state.copyWith(selectedCropType: cropType);
  }

  void setGrowthStage(String stage) {
    state = state.copyWith(selectedGrowthStage: stage);
  }

  void setFieldArea(double area) {
    state = state.copyWith(fieldArea: area);
  }

  void setSoilAnalysis(SoilAnalysis analysis) {
    state = state.copyWith(soilAnalysis: analysis);
  }

  void setIrrigationType(String type) {
    state = state.copyWith(irrigationType: type);
  }

  void setLoading(bool loading) {
    state = state.copyWith(isLoading: loading);
  }

  void setError(String? error) {
    state = state.copyWith(error: error);
  }

  void reset() {
    state = const FertilizerFormState();
  }

  FertilizerRequest? buildRequest() {
    if (!state.isValid) return null;

    return FertilizerRequest(
      cropType: state.selectedCropType!,
      fieldArea: state.fieldArea!,
      soilAnalysis: state.soilAnalysis!,
      growthStage: state.selectedGrowthStage!,
      irrigationType: state.irrigationType ?? '',
    );
  }
}

/// Provider for fertilizer form state
/// موفر حالة نموذج التسميد
final fertilizerFormProvider =
    StateNotifierProvider<FertilizerFormNotifier, FertilizerFormState>((ref) {
  return FertilizerFormNotifier();
});

/// State for irrigation form
/// حالة نموذج الري
class IrrigationFormState {
  final String? selectedCropType;
  final String? selectedGrowthStage;
  final String? selectedMethod;
  final String? selectedSoilType;
  final double? fieldArea;
  final double? soilMoisture;
  final double? temperature;
  final double? humidity;
  final bool isLoading;
  final String? error;

  const IrrigationFormState({
    this.selectedCropType,
    this.selectedGrowthStage,
    this.selectedMethod,
    this.selectedSoilType,
    this.fieldArea,
    this.soilMoisture,
    this.temperature,
    this.humidity,
    this.isLoading = false,
    this.error,
  });

  IrrigationFormState copyWith({
    String? selectedCropType,
    String? selectedGrowthStage,
    String? selectedMethod,
    String? selectedSoilType,
    double? fieldArea,
    double? soilMoisture,
    double? temperature,
    double? humidity,
    bool? isLoading,
    String? error,
  }) {
    return IrrigationFormState(
      selectedCropType: selectedCropType ?? this.selectedCropType,
      selectedGrowthStage: selectedGrowthStage ?? this.selectedGrowthStage,
      selectedMethod: selectedMethod ?? this.selectedMethod,
      selectedSoilType: selectedSoilType ?? this.selectedSoilType,
      fieldArea: fieldArea ?? this.fieldArea,
      soilMoisture: soilMoisture ?? this.soilMoisture,
      temperature: temperature ?? this.temperature,
      humidity: humidity ?? this.humidity,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  bool get isValid =>
      selectedCropType != null &&
      selectedGrowthStage != null &&
      selectedMethod != null &&
      selectedSoilType != null &&
      fieldArea != null &&
      fieldArea! > 0;
}

/// Notifier for irrigation form state
/// مُعلم حالة نموذج الري
class IrrigationFormNotifier extends StateNotifier<IrrigationFormState> {
  IrrigationFormNotifier() : super(const IrrigationFormState());

  void setCropType(String cropType) {
    state = state.copyWith(selectedCropType: cropType);
  }

  void setGrowthStage(String stage) {
    state = state.copyWith(selectedGrowthStage: stage);
  }

  void setMethod(String method) {
    state = state.copyWith(selectedMethod: method);
  }

  void setSoilType(String soilType) {
    state = state.copyWith(selectedSoilType: soilType);
  }

  void setFieldArea(double area) {
    state = state.copyWith(fieldArea: area);
  }

  void setSoilMoisture(double moisture) {
    state = state.copyWith(soilMoisture: moisture);
  }

  void setTemperature(double temp) {
    state = state.copyWith(temperature: temp);
  }

  void setHumidity(double humidity) {
    state = state.copyWith(humidity: humidity);
  }

  void setLoading(bool loading) {
    state = state.copyWith(isLoading: loading);
  }

  void setError(String? error) {
    state = state.copyWith(error: error);
  }

  void reset() {
    state = const IrrigationFormState();
  }

  IrrigationRequest? buildRequest() {
    if (!state.isValid) return null;

    return IrrigationRequest(
      cropType: state.selectedCropType!,
      growthStage: state.selectedGrowthStage!,
      fieldArea: state.fieldArea!,
      soilType: state.selectedSoilType!,
      irrigationMethod: state.selectedMethod!,
      currentSoilMoisture: state.soilMoisture ?? 0,
      temperature: state.temperature ?? 0,
      humidity: state.humidity ?? 0,
    );
  }
}

/// Provider for irrigation form state
/// موفر حالة نموذج الري
final irrigationFormProvider =
    StateNotifierProvider<IrrigationFormNotifier, IrrigationFormState>((ref) {
  return IrrigationFormNotifier();
});
