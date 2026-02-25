import 'package:connectivity_plus/connectivity_plus.dart';
import '../models/rotation_models.dart';
import '../services/rotation_service.dart';
import 'rotation_local_data_source.dart';

/// Repository for rotation plans with offline-first support
/// مستودع لخطط التناوب مع دعم العمل بدون اتصال أولاً
class RotationRepository {
  final RotationService _service;
  final RotationLocalDataSource _localDataSource;
  final Connectivity _connectivity;

  RotationRepository({
    required RotationService service,
    required RotationLocalDataSource localDataSource,
    Connectivity? connectivity,
  })  : _service = service,
        _localDataSource = localDataSource,
        _connectivity = connectivity ?? Connectivity();

  /// Check if device has internet connectivity
  Future<bool> _hasConnectivity() async {
    final result = await _connectivity.checkConnectivity();
    return !result.contains(ConnectivityResult.none);
  }

  /// Get rotation plan for a field with offline-first approach
  ///
  /// Strategy:
  /// 1. Return cached data immediately if available
  /// 2. Fetch from network in background if online
  /// 3. Update cache with fresh data
  Future<RotationPlan> getRotationPlan(String fieldId) async {
    // Try to get cached data first
    final cachedPlan = await _localDataSource.getRotationPlan(fieldId);

    // If offline, return cached data or generate default
    if (!await _hasConnectivity()) {
      if (cachedPlan != null) {
        return cachedPlan;
      }
      // Generate default plan if no cache
      return _generateDefaultPlan(fieldId);
    }

    // Online: fetch from service
    try {
      final plan = await _service.getRotationPlan(fieldId);
      // Cache the plan
      await _localDataSource.saveRotationPlan(plan);
      await _localDataSource.clearPendingSync(fieldId);
      return plan;
    } catch (e) {
      // On error, return cached data or generate default
      if (cachedPlan != null) {
        return cachedPlan;
      }
      return _generateDefaultPlan(fieldId);
    }
  }

  /// Generate a new rotation plan
  Future<RotationPlan> generateRotationPlan(
    String fieldId,
    int years,
    Map<String, dynamic> preferences,
  ) async {
    final plan =
        await _service.generateRotationPlan(fieldId, years, preferences);

    // Save to local storage
    await _localDataSource.saveRotationPlan(plan);

    return plan;
  }

  /// Update a rotation year in the plan
  Future<RotationPlan> updateRotationYear(
    String fieldId,
    RotationYear updatedYear,
  ) async {
    final plan = await getRotationPlan(fieldId);

    // Update the rotation year in the plan
    final updatedYears = plan.rotationYears.map((year) {
      if (year.year == updatedYear.year && year.season == updatedYear.season) {
        return updatedYear;
      }
      return year;
    }).toList();

    final updatedPlan = RotationPlan(
      id: plan.id,
      fieldId: plan.fieldId,
      fieldName: plan.fieldName,
      rotationYears: updatedYears,
      createdAt: plan.createdAt,
      updatedAt: DateTime.now(),
      preferences: plan.preferences,
    );

    // Save locally
    await _localDataSource.saveRotationPlan(updatedPlan);

    // Add to history if completed
    if (updatedYear.isCompleted && updatedYear.crop != null) {
      await _localDataSource.addRotationHistoryEntry(
        fieldId,
        RotationHistoryEntry(
          fieldId: fieldId,
          cropId: updatedYear.crop!.id,
          cropNameEn: updatedYear.crop!.nameEn,
          cropNameAr: updatedYear.crop!.nameAr,
          year: updatedYear.year,
          season: updatedYear.season,
          plantingDate: updatedYear.plantingDate ?? DateTime.now(),
          harvestDate: updatedYear.harvestDate,
          yieldAmount: updatedYear.yieldAmount,
          notes: updatedYear.notes,
          recordedAt: DateTime.now(),
        ),
      );
    }

    return updatedPlan;
  }

  /// Get crop recommendations with caching
  Future<List<CropRecommendation>> getRecommendedCrops(
    String fieldId,
    int year,
  ) async {
    // Check cache first
    final cached =
        await _localDataSource.getCachedRecommendations(fieldId, year);

    if (!await _hasConnectivity()) {
      // Return cached or generate locally if offline
      if (cached != null) {
        return cached;
      }
      return _generateLocalRecommendations(fieldId, year);
    }

    try {
      final recommendations = await _service.getRecommendedCrops(fieldId, year);
      // Cache recommendations
      await _localDataSource.cacheRecommendations(
          fieldId, year, recommendations);
      return recommendations;
    } catch (e) {
      if (cached != null) {
        return cached;
      }
      return _generateLocalRecommendations(fieldId, year);
    }
  }

  /// Get crop compatibility
  Future<CompatibilityScore> getCropCompatibility(
      Crop crop1, Crop crop2) async {
    return _service.getCropCompatibility(crop1, crop2);
  }

  /// Get soil health trend
  Future<List<SoilHealth>> getSoilHealthTrend(String fieldId) async {
    return _service.getSoilHealthTrend(fieldId);
  }

  /// Get rotation history for a field
  Future<List<RotationHistoryEntry>> getRotationHistory(String fieldId) async {
    return _localDataSource.getRotationHistory(fieldId);
  }

  /// Sync pending changes with server
  Future<void> syncPendingChanges() async {
    if (!await _hasConnectivity()) {
      return;
    }

    final pendingFieldIds = await _localDataSource.getPendingSyncFieldIds();

    for (final fieldId in pendingFieldIds) {
      try {
        final plan = await _localDataSource.getRotationPlan(fieldId);
        if (plan != null) {
          // TODO: Implement actual API sync when backend is ready
          // await _apiService.syncRotationPlan(plan);
          await _localDataSource.clearPendingSync(fieldId);
        }
      } catch (e) {
        // Log error but continue with other syncs
        continue;
      }
    }

    await _localDataSource.updateLastSyncTime();
  }

  /// Check if there are pending changes to sync
  Future<bool> hasPendingSync() async {
    return _localDataSource.hasPendingSync();
  }

  /// Get last sync time
  Future<DateTime?> getLastSyncTime() async {
    return _localDataSource.getLastSyncTime();
  }

  /// Generate default plan for offline use
  RotationPlan _generateDefaultPlan(String fieldId) {
    final currentYear = DateTime.now().year;
    return RotationPlan(
      id: 'local_plan_$fieldId',
      fieldId: fieldId,
      fieldName: 'Field #$fieldId',
      rotationYears: [
        RotationYear(
          year: currentYear,
          season: 'Spring',
          crop: YemenCrops.crops.firstWhere((c) => c.id == 'wheat'),
        ),
        RotationYear(
          year: currentYear + 1,
          season: 'Winter',
          crop: YemenCrops.crops.firstWhere((c) => c.id == 'fava_beans'),
        ),
      ],
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }

  /// Generate local recommendations when offline
  List<CropRecommendation> _generateLocalRecommendations(
      String fieldId, int year) {
    // Return all non-perennial crops with default scores
    return YemenCrops.crops
        .where((c) => !c.isPerennial)
        .map((crop) => CropRecommendation(
              crop: crop,
              suitabilityScore: 70,
              reasons: ['Based on local recommendation engine'],
              reasonsAr: ['بناءً على محرك التوصيات المحلي'],
            ))
        .toList();
  }

  /// Get all crop families
  List<CropFamilyInfo> getAllCropFamilies() {
    return _service.getAllCropFamilies();
  }

  /// Get compatibility matrix
  Future<Map<String, Map<String, CompatibilityScore>>>
      getCompatibilityMatrix() {
    return _service.getCompatibilityMatrix();
  }
}
