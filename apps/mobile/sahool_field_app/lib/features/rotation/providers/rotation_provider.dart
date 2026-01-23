import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/rotation_models.dart';
import '../services/rotation_service.dart';

/// Rotation service provider
final rotationServiceProvider = Provider<RotationService>((ref) {
  return RotationService();
});

/// Rotation plan provider for a specific field
final rotationPlanProvider =
    FutureProvider.family<RotationPlan, String>((ref, fieldId) async {
  final service = ref.watch(rotationServiceProvider);
  return service.getRotationPlan(fieldId);
});

/// Soil health trend provider for a specific field
final soilHealthTrendProvider =
    FutureProvider.family<List<SoilHealth>, String>((ref, fieldId) async {
  final service = ref.watch(rotationServiceProvider);
  return service.getSoilHealthTrend(fieldId);
});

/// Crop compatibility provider for two crops
final cropCompatibilityProvider = FutureProvider.family<CompatibilityScore,
    CropCompatibilityParams>((ref, params) async {
  final service = ref.watch(rotationServiceProvider);
  return service.getCropCompatibility(params.crop1, params.crop2);
});

/// Parameters for crop compatibility
class CropCompatibilityParams {
  final Crop crop1;
  final Crop crop2;

  const CropCompatibilityParams({
    required this.crop1,
    required this.crop2,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CropCompatibilityParams &&
          runtimeType == other.runtimeType &&
          crop1.id == other.crop1.id &&
          crop2.id == other.crop2.id;

  @override
  int get hashCode => crop1.id.hashCode ^ crop2.id.hashCode;
}

/// Recommended crops provider for a field and year
final recommendedCropsProvider = FutureProvider.family<List<CropRecommendation>,
    RecommendedCropsParams>((ref, params) async {
  final service = ref.watch(rotationServiceProvider);
  return service.getRecommendedCrops(params.fieldId, params.year);
});

/// Parameters for recommended crops
class RecommendedCropsParams {
  final String fieldId;
  final int year;

  const RecommendedCropsParams({
    required this.fieldId,
    required this.year,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is RecommendedCropsParams &&
          runtimeType == other.runtimeType &&
          fieldId == other.fieldId &&
          year == other.year;

  @override
  int get hashCode => fieldId.hashCode ^ year.hashCode;
}

/// All crop families provider
final cropFamiliesProvider = Provider<List<CropFamilyInfo>>((ref) {
  final service = ref.watch(rotationServiceProvider);
  return service.getAllCropFamilies();
});

/// Compatibility matrix provider
final compatibilityMatrixProvider =
    FutureProvider<Map<String, Map<String, CompatibilityScore>>>((ref) async {
  final service = ref.watch(rotationServiceProvider);
  return service.getCompatibilityMatrix();
});

/// State notifier for managing rotation plan generation
class RotationPlanNotifier extends StateNotifier<AsyncValue<RotationPlan>> {
  final RotationService _service;

  RotationPlanNotifier(this._service) : super(const AsyncValue.loading());

  Future<void> generatePlan(
    String fieldId,
    int years,
    Map<String, dynamic> preferences,
  ) async {
    state = const AsyncValue.loading();
    try {
      final plan = await _service.generateRotationPlan(
        fieldId,
        years,
        preferences,
      );
      state = AsyncValue.data(plan);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> loadPlan(String fieldId) async {
    state = const AsyncValue.loading();
    try {
      final plan = await _service.getRotationPlan(fieldId);
      state = AsyncValue.data(plan);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }
}

/// Provider for rotation plan notifier
final rotationPlanNotifierProvider =
    StateNotifierProvider<RotationPlanNotifier, AsyncValue<RotationPlan>>((ref) {
  final service = ref.watch(rotationServiceProvider);
  return RotationPlanNotifier(service);
});

/// Selected field ID provider (for UI state)
final selectedFieldIdProvider = StateProvider<String?>((ref) => null);

/// Selected year provider (for recommendations)
final selectedYearProvider = StateProvider<int>((ref) => DateTime.now().year);

/// Rotation preferences provider
final rotationPreferencesProvider =
    StateProvider<Map<String, dynamic>>((ref) => {
          'prioritizeSoilHealth': true,
          'includeNitrogenFixers': true,
          'avoidSameFamily': true,
          'rotationCycleYears': 5,
        });

/// Current soil health provider
final currentSoilHealthProvider =
    Provider.family<SoilHealth?, String>((ref, fieldId) {
  final planAsync = ref.watch(rotationPlanProvider(fieldId));
  return planAsync.maybeWhen(
    data: (plan) => plan.currentRotation?.soilHealthBefore,
    orElse: () => null,
  );
});

/// Soil health score provider
final soilHealthScoreProvider = Provider.family<double, String>((ref, fieldId) {
  final soilHealth = ref.watch(currentSoilHealthProvider(fieldId));
  return soilHealth?.overallScore ?? 0.0;
});
