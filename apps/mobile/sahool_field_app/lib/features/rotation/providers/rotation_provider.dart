import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/rotation_models.dart';
import '../services/rotation_service.dart';
import '../data/rotation_local_data_source.dart';
import '../data/rotation_repository.dart';
export '../data/rotation_local_data_source.dart' show RotationHistoryEntry;

/// SharedPreferences provider (should be overridden at app startup)
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError(
    'sharedPreferencesProvider must be overridden with the actual SharedPreferences instance',
  );
});

/// Rotation service provider
final rotationServiceProvider = Provider<RotationService>((ref) {
  return RotationService();
});

/// Rotation local data source provider
final rotationLocalDataSourceProvider =
    Provider<RotationLocalDataSource>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return RotationLocalDataSource(prefs);
});

/// Rotation repository provider with offline support
final rotationRepositoryProvider = Provider<RotationRepository>((ref) {
  final service = ref.watch(rotationServiceProvider);
  final localDataSource = ref.watch(rotationLocalDataSourceProvider);
  return RotationRepository(
    service: service,
    localDataSource: localDataSource,
  );
});

/// Rotation plan provider for a specific field (with offline support)
final rotationPlanProvider =
    FutureProvider.family<RotationPlan, String>((ref, fieldId) async {
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.getRotationPlan(fieldId);
});

/// Soil health trend provider for a specific field
final soilHealthTrendProvider =
    FutureProvider.family<List<SoilHealth>, String>((ref, fieldId) async {
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.getSoilHealthTrend(fieldId);
});

/// Crop compatibility provider for two crops
final cropCompatibilityProvider =
    FutureProvider.family<CompatibilityScore, CropCompatibilityParams>(
        (ref, params) async {
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.getCropCompatibility(params.crop1, params.crop2);
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

/// Recommended crops provider for a field and year (with offline caching)
final recommendedCropsProvider =
    FutureProvider.family<List<CropRecommendation>, RecommendedCropsParams>(
        (ref, params) async {
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.getRecommendedCrops(params.fieldId, params.year);
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
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.getAllCropFamilies();
});

/// Compatibility matrix provider
final compatibilityMatrixProvider =
    FutureProvider<Map<String, Map<String, CompatibilityScore>>>((ref) async {
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.getCompatibilityMatrix();
});

/// Rotation history provider for a field
final rotationHistoryProvider =
    FutureProvider.family<List<RotationHistoryEntry>, String>(
        (ref, fieldId) async {
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.getRotationHistory(fieldId);
});

/// Pending sync status provider
final rotationPendingSyncProvider = FutureProvider<bool>((ref) async {
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.hasPendingSync();
});

/// Last sync time provider
final rotationLastSyncProvider = FutureProvider<DateTime?>((ref) async {
  final repository = ref.watch(rotationRepositoryProvider);
  return repository.getLastSyncTime();
});

/// State notifier for managing rotation plan generation (with offline support)
class RotationPlanNotifier extends StateNotifier<AsyncValue<RotationPlan>> {
  final RotationRepository _repository;

  RotationPlanNotifier(this._repository) : super(const AsyncValue.loading());

  Future<void> generatePlan(
    String fieldId,
    int years,
    Map<String, dynamic> preferences,
  ) async {
    state = const AsyncValue.loading();
    try {
      final plan = await _repository.generateRotationPlan(
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
      final plan = await _repository.getRotationPlan(fieldId);
      state = AsyncValue.data(plan);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> updateRotationYear(
      String fieldId, RotationYear updatedYear) async {
    final currentState = state;
    if (currentState is AsyncData<RotationPlan>) {
      state = const AsyncValue.loading();
      try {
        final updatedPlan =
            await _repository.updateRotationYear(fieldId, updatedYear);
        state = AsyncValue.data(updatedPlan);
      } catch (error) {
        state = currentState; // Revert on error
        rethrow;
      }
    }
  }

  Future<void> syncPendingChanges() async {
    try {
      await _repository.syncPendingChanges();
    } catch (e) {
      // Silent fail for sync - will retry later
    }
  }
}

/// Provider for rotation plan notifier - autoDispose for proper cleanup
final rotationPlanNotifierProvider = StateNotifierProvider.autoDispose<
    RotationPlanNotifier, AsyncValue<RotationPlan>>((ref) {
  final repository = ref.watch(rotationRepositoryProvider);
  return RotationPlanNotifier(repository);
});

/// Selected field ID provider for rotation feature (for UI state)
/// Note: This is scoped to rotation feature. Use core/providers/selected_field_provider.dart
/// for app-wide field selection.
final rotationSelectedFieldIdProvider =
    StateProvider.autoDispose<String?>((ref) => null);

/// Selected year provider (for recommendations) - autoDispose to match
final selectedYearProvider =
    StateProvider.autoDispose<int>((ref) => DateTime.now().year);

/// Rotation preferences provider - autoDispose to match
final rotationPreferencesProvider =
    StateProvider.autoDispose<Map<String, dynamic>>((ref) => {
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
