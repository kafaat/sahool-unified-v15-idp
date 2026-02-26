import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';

/// SAHOOL Offline Completeness Checker
/// مدقق اكتمال وضع عدم الاتصال
///
/// Validates that all features work offline:
/// - Data availability (fields, crops, tasks, weather cache)
/// - Map tile cache coverage
/// - Sync queue health
/// - Local database integrity

// ═══════════════════════════════════════════════════════════════════════════
// Offline Feature Readiness
// ═══════════════════════════════════════════════════════════════════════════

/// Features that must work offline
enum OfflineFeature {
  /// Local field data (boundaries, crops, area)
  fieldData,

  /// Cached weather data (at least 3 days)
  weatherCache,

  /// Map tiles for field regions
  mapTiles,

  /// Task list and task creation
  taskManagement,

  /// Irrigation recording
  irrigationRecording,

  /// Pest/disease photo capture
  photoCaptureAndStorage,

  /// Sensor data cache (latest readings)
  sensorDataCache,

  /// Advisory cache (recent recommendations)
  advisoryCache,

  /// Sync outbox (pending mutations)
  syncOutbox,

  /// Local database integrity
  databaseIntegrity,
}

/// Extension for OfflineFeature
extension OfflineFeatureExtension on OfflineFeature {
  String get nameAr {
    switch (this) {
      case OfflineFeature.fieldData:
        return 'بيانات الحقول';
      case OfflineFeature.weatherCache:
        return 'ذاكرة الطقس';
      case OfflineFeature.mapTiles:
        return 'خرائط محفوظة';
      case OfflineFeature.taskManagement:
        return 'إدارة المهام';
      case OfflineFeature.irrigationRecording:
        return 'تسجيل الري';
      case OfflineFeature.photoCaptureAndStorage:
        return 'التقاط الصور';
      case OfflineFeature.sensorDataCache:
        return 'بيانات المستشعرات';
      case OfflineFeature.advisoryCache:
        return 'ذاكرة التوصيات';
      case OfflineFeature.syncOutbox:
        return 'صندوق المزامنة';
      case OfflineFeature.databaseIntegrity:
        return 'سلامة قاعدة البيانات';
    }
  }

  String get nameEn {
    switch (this) {
      case OfflineFeature.fieldData:
        return 'Field Data';
      case OfflineFeature.weatherCache:
        return 'Weather Cache';
      case OfflineFeature.mapTiles:
        return 'Map Tiles';
      case OfflineFeature.taskManagement:
        return 'Task Management';
      case OfflineFeature.irrigationRecording:
        return 'Irrigation Recording';
      case OfflineFeature.photoCaptureAndStorage:
        return 'Photo Capture';
      case OfflineFeature.sensorDataCache:
        return 'Sensor Data Cache';
      case OfflineFeature.advisoryCache:
        return 'Advisory Cache';
      case OfflineFeature.syncOutbox:
        return 'Sync Outbox';
      case OfflineFeature.databaseIntegrity:
        return 'Database Integrity';
    }
  }

  /// Whether this feature is critical for basic offline operation
  bool get isCritical {
    switch (this) {
      case OfflineFeature.fieldData:
      case OfflineFeature.taskManagement:
      case OfflineFeature.syncOutbox:
      case OfflineFeature.databaseIntegrity:
        return true;
      case OfflineFeature.weatherCache:
      case OfflineFeature.mapTiles:
      case OfflineFeature.irrigationRecording:
      case OfflineFeature.photoCaptureAndStorage:
      case OfflineFeature.sensorDataCache:
      case OfflineFeature.advisoryCache:
        return false;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Readiness Status
// ═══════════════════════════════════════════════════════════════════════════

/// Status for a single offline feature check
enum OfflineReadinessStatus {
  /// Feature is fully ready for offline use
  ready,

  /// Feature is partially ready (limited functionality)
  partial,

  /// Feature is not ready for offline use
  notReady,

  /// Check has not been performed yet
  unchecked,
}

/// Result of checking a single offline feature
@immutable
class FeatureReadinessResult {
  final OfflineFeature feature;
  final OfflineReadinessStatus status;
  final String? detailsAr;
  final String? detailsEn;
  final int? cachedItemCount;
  final int? requiredItemCount;
  final DateTime? lastCacheUpdate;

  const FeatureReadinessResult({
    required this.feature,
    required this.status,
    this.detailsAr,
    this.detailsEn,
    this.cachedItemCount,
    this.requiredItemCount,
    this.lastCacheUpdate,
  });

  /// Whether this feature is ready
  bool get isReady => status == OfflineReadinessStatus.ready;

  /// Whether the cache is stale (older than 24 hours)
  bool get isCacheStale {
    if (lastCacheUpdate == null) return true;
    return DateTime.now().difference(lastCacheUpdate!).inHours > 24;
  }

  /// Cache completeness percentage
  double get cacheCompleteness {
    if (cachedItemCount == null || requiredItemCount == null) {
      return isReady ? 100 : 0;
    }
    if (requiredItemCount == 0) return 100;
    return (cachedItemCount! / requiredItemCount!) * 100;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Offline Readiness Report
// ═══════════════════════════════════════════════════════════════════════════

/// Complete offline readiness report
@immutable
class OfflineReadinessReport {
  final List<FeatureReadinessResult> results;
  final DateTime generatedAt;

  const OfflineReadinessReport({
    required this.results,
    required this.generatedAt,
  });

  /// Total features checked
  int get totalFeatures => results.length;

  /// Number of ready features
  int get readyCount =>
      results.where((r) => r.status == OfflineReadinessStatus.ready).length;

  /// Number of partially ready features
  int get partialCount =>
      results.where((r) => r.status == OfflineReadinessStatus.partial).length;

  /// Number of not-ready features
  int get notReadyCount =>
      results.where((r) => r.status == OfflineReadinessStatus.notReady).length;

  /// Overall readiness percentage
  double get readinessPercent {
    if (results.isEmpty) return 0;
    final score = results.fold<double>(0, (sum, r) {
      switch (r.status) {
        case OfflineReadinessStatus.ready:
          return sum + 1.0;
        case OfflineReadinessStatus.partial:
          return sum + 0.5;
        case OfflineReadinessStatus.notReady:
        case OfflineReadinessStatus.unchecked:
          return sum;
      }
    });
    return (score / results.length) * 100;
  }

  /// Whether all critical features are ready
  bool get criticalFeaturesReady {
    return results.where((r) => r.feature.isCritical).every((r) => r.isReady);
  }

  /// Whether the app is ready for full offline operation
  bool get isFullyOfflineReady => notReadyCount == 0;

  /// Summary text
  String get summaryAr {
    if (isFullyOfflineReady) return 'جاهز للعمل بدون اتصال ✓';
    if (criticalFeaturesReady) {
      return 'جاهز جزئياً - $notReadyCount ميزة غير متوفرة';
    }
    return 'غير جاهز للعمل بدون اتصال';
  }

  String get summaryEn {
    if (isFullyOfflineReady) return 'Fully Offline Ready ✓';
    if (criticalFeaturesReady) {
      return 'Partially Ready - $notReadyCount features unavailable';
    }
    return 'Not Offline Ready';
  }

  /// Features that need attention
  List<FeatureReadinessResult> get needsAttention {
    return results
        .where((r) =>
            r.status == OfflineReadinessStatus.notReady ||
            r.status == OfflineReadinessStatus.partial)
        .toList();
  }

  /// Features with stale caches
  List<FeatureReadinessResult> get staleCaches {
    return results.where((r) => r.isCacheStale && r.isReady).toList();
  }

  @override
  String toString() {
    return 'OfflineReadinessReport($readyCount/$totalFeatures ready, '
        '${readinessPercent.toStringAsFixed(0)}%)';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Completeness Checker
// ═══════════════════════════════════════════════════════════════════════════

/// Checks offline feature completeness
class OfflineCompletenessChecker {
  /// Run a full offline readiness check
  ///
  /// In a real implementation, each check would query local databases,
  /// file caches, and sync status to determine readiness.
  Future<OfflineReadinessReport> checkAll() async {
    final results = <FeatureReadinessResult>[];

    for (final feature in OfflineFeature.values) {
      results.add(await checkFeature(feature));
    }

    final report = OfflineReadinessReport(
      results: results,
      generatedAt: DateTime.now(),
    );

    AppLogger.i(
      'Offline readiness: ${report.readinessPercent.toStringAsFixed(0)}%',
      tag: 'OFFLINE',
    );

    return report;
  }

  /// Check a specific feature's offline readiness
  Future<FeatureReadinessResult> checkFeature(OfflineFeature feature) async {
    // In production, each case would perform real checks.
    // Here we provide the framework structure.
    switch (feature) {
      case OfflineFeature.fieldData:
        return _checkFieldData();
      case OfflineFeature.weatherCache:
        return _checkWeatherCache();
      case OfflineFeature.mapTiles:
        return _checkMapTiles();
      case OfflineFeature.taskManagement:
        return _checkTaskManagement();
      case OfflineFeature.irrigationRecording:
        return _checkIrrigationRecording();
      case OfflineFeature.photoCaptureAndStorage:
        return _checkPhotoStorage();
      case OfflineFeature.sensorDataCache:
        return _checkSensorCache();
      case OfflineFeature.advisoryCache:
        return _checkAdvisoryCache();
      case OfflineFeature.syncOutbox:
        return _checkSyncOutbox();
      case OfflineFeature.databaseIntegrity:
        return _checkDatabaseIntegrity();
    }
  }

  Future<FeatureReadinessResult> _checkFieldData() async {
    // Framework: Check if local DB has field records
    return const FeatureReadinessResult(
      feature: OfflineFeature.fieldData,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires local database query',
      detailsAr: 'يتطلب استعلام قاعدة البيانات المحلية',
    );
  }

  Future<FeatureReadinessResult> _checkWeatherCache() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.weatherCache,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires weather cache inspection',
      detailsAr: 'يتطلب فحص ذاكرة الطقس',
    );
  }

  Future<FeatureReadinessResult> _checkMapTiles() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.mapTiles,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires map tile cache inspection',
      detailsAr: 'يتطلب فحص ذاكرة الخرائط',
    );
  }

  Future<FeatureReadinessResult> _checkTaskManagement() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.taskManagement,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires task database check',
      detailsAr: 'يتطلب فحص قاعدة بيانات المهام',
    );
  }

  Future<FeatureReadinessResult> _checkIrrigationRecording() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.irrigationRecording,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires irrigation module check',
      detailsAr: 'يتطلب فحص وحدة الري',
    );
  }

  Future<FeatureReadinessResult> _checkPhotoStorage() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.photoCaptureAndStorage,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires storage permissions check',
      detailsAr: 'يتطلب فحص صلاحيات التخزين',
    );
  }

  Future<FeatureReadinessResult> _checkSensorCache() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.sensorDataCache,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires sensor cache inspection',
      detailsAr: 'يتطلب فحص ذاكرة المستشعرات',
    );
  }

  Future<FeatureReadinessResult> _checkAdvisoryCache() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.advisoryCache,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires advisory cache check',
      detailsAr: 'يتطلب فحص ذاكرة التوصيات',
    );
  }

  Future<FeatureReadinessResult> _checkSyncOutbox() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.syncOutbox,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires outbox queue check',
      detailsAr: 'يتطلب فحص صف المزامنة',
    );
  }

  Future<FeatureReadinessResult> _checkDatabaseIntegrity() async {
    return const FeatureReadinessResult(
      feature: OfflineFeature.databaseIntegrity,
      status: OfflineReadinessStatus.unchecked,
      detailsEn: 'Requires database integrity check',
      detailsAr: 'يتطلب فحص سلامة قاعدة البيانات',
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for the offline completeness checker
final offlineCompletenessCheckerProvider =
    Provider<OfflineCompletenessChecker>((ref) {
  return OfflineCompletenessChecker();
});

/// Provider for the offline readiness report
final offlineReadinessProvider =
    FutureProvider<OfflineReadinessReport>((ref) async {
  final checker = ref.watch(offlineCompletenessCheckerProvider);
  return checker.checkAll();
});
