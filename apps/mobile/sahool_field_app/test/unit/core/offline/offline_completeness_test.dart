import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/offline/offline_completeness.dart';

void main() {
  group('OfflineFeature', () {
    test('should have 10 features', () {
      expect(OfflineFeature.values.length, 10);
    });

    test('should have Arabic names', () {
      expect(OfflineFeature.fieldData.nameAr, 'بيانات الحقول');
      expect(OfflineFeature.weatherCache.nameAr, 'ذاكرة الطقس');
      expect(OfflineFeature.mapTiles.nameAr, 'خرائط محفوظة');
      expect(OfflineFeature.taskManagement.nameAr, 'إدارة المهام');
      expect(OfflineFeature.irrigationRecording.nameAr, 'تسجيل الري');
      expect(OfflineFeature.photoCaptureAndStorage.nameAr, 'التقاط الصور');
      expect(OfflineFeature.sensorDataCache.nameAr, 'بيانات المستشعرات');
      expect(OfflineFeature.advisoryCache.nameAr, 'ذاكرة التوصيات');
      expect(OfflineFeature.syncOutbox.nameAr, 'صندوق المزامنة');
      expect(OfflineFeature.databaseIntegrity.nameAr, 'سلامة قاعدة البيانات');
    });

    test('should have English names', () {
      expect(OfflineFeature.fieldData.nameEn, 'Field Data');
      expect(OfflineFeature.weatherCache.nameEn, 'Weather Cache');
      expect(OfflineFeature.mapTiles.nameEn, 'Map Tiles');
      expect(OfflineFeature.taskManagement.nameEn, 'Task Management');
      expect(OfflineFeature.irrigationRecording.nameEn, 'Irrigation Recording');
      expect(OfflineFeature.photoCaptureAndStorage.nameEn, 'Photo Capture');
      expect(OfflineFeature.sensorDataCache.nameEn, 'Sensor Data Cache');
      expect(OfflineFeature.advisoryCache.nameEn, 'Advisory Cache');
      expect(OfflineFeature.syncOutbox.nameEn, 'Sync Outbox');
      expect(OfflineFeature.databaseIntegrity.nameEn, 'Database Integrity');
    });

    test(
        'critical features should be fieldData, taskManagement, syncOutbox, databaseIntegrity',
        () {
      expect(OfflineFeature.fieldData.isCritical, true);
      expect(OfflineFeature.taskManagement.isCritical, true);
      expect(OfflineFeature.syncOutbox.isCritical, true);
      expect(OfflineFeature.databaseIntegrity.isCritical, true);
    });

    test('non-critical features should be weatherCache, mapTiles, etc.', () {
      expect(OfflineFeature.weatherCache.isCritical, false);
      expect(OfflineFeature.mapTiles.isCritical, false);
      expect(OfflineFeature.irrigationRecording.isCritical, false);
      expect(OfflineFeature.photoCaptureAndStorage.isCritical, false);
      expect(OfflineFeature.sensorDataCache.isCritical, false);
      expect(OfflineFeature.advisoryCache.isCritical, false);
    });
  });

  group('OfflineReadinessStatus', () {
    test('should have 4 statuses', () {
      expect(OfflineReadinessStatus.values.length, 4);
      expect(OfflineReadinessStatus.values,
          contains(OfflineReadinessStatus.ready));
      expect(OfflineReadinessStatus.values,
          contains(OfflineReadinessStatus.partial));
      expect(OfflineReadinessStatus.values,
          contains(OfflineReadinessStatus.notReady));
      expect(OfflineReadinessStatus.values,
          contains(OfflineReadinessStatus.unchecked));
    });
  });

  group('FeatureReadinessResult', () {
    test('isReady should check for ready status', () {
      const ready = FeatureReadinessResult(
        feature: OfflineFeature.fieldData,
        status: OfflineReadinessStatus.ready,
      );
      const notReady = FeatureReadinessResult(
        feature: OfflineFeature.fieldData,
        status: OfflineReadinessStatus.notReady,
      );

      expect(ready.isReady, true);
      expect(notReady.isReady, false);
    });

    test('isCacheStale should return true when no lastCacheUpdate', () {
      const result = FeatureReadinessResult(
        feature: OfflineFeature.weatherCache,
        status: OfflineReadinessStatus.ready,
      );
      expect(result.isCacheStale, true);
    });

    test('isCacheStale should return false for recent updates', () {
      final result = FeatureReadinessResult(
        feature: OfflineFeature.weatherCache,
        status: OfflineReadinessStatus.ready,
        lastCacheUpdate: DateTime.now().subtract(const Duration(hours: 1)),
      );
      expect(result.isCacheStale, false);
    });

    test('isCacheStale should return true for old updates', () {
      final result = FeatureReadinessResult(
        feature: OfflineFeature.weatherCache,
        status: OfflineReadinessStatus.ready,
        lastCacheUpdate: DateTime.now().subtract(const Duration(hours: 25)),
      );
      expect(result.isCacheStale, true);
    });

    test('cacheCompleteness should calculate percentage', () {
      const result = FeatureReadinessResult(
        feature: OfflineFeature.mapTiles,
        status: OfflineReadinessStatus.partial,
        cachedItemCount: 50,
        requiredItemCount: 100,
      );
      expect(result.cacheCompleteness, 50.0);
    });

    test('cacheCompleteness should be 100 for ready without counts', () {
      const result = FeatureReadinessResult(
        feature: OfflineFeature.fieldData,
        status: OfflineReadinessStatus.ready,
      );
      expect(result.cacheCompleteness, 100);
    });

    test('cacheCompleteness should be 0 for notReady without counts', () {
      const result = FeatureReadinessResult(
        feature: OfflineFeature.fieldData,
        status: OfflineReadinessStatus.notReady,
      );
      expect(result.cacheCompleteness, 0);
    });

    test('cacheCompleteness should handle zero required items', () {
      const result = FeatureReadinessResult(
        feature: OfflineFeature.fieldData,
        status: OfflineReadinessStatus.ready,
        cachedItemCount: 0,
        requiredItemCount: 0,
      );
      expect(result.cacheCompleteness, 100);
    });
  });

  group('OfflineReadinessReport', () {
    test('should compute counts correctly', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.weatherCache,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.mapTiles,
            status: OfflineReadinessStatus.partial,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.taskManagement,
            status: OfflineReadinessStatus.notReady,
          ),
        ],
      );

      expect(report.totalFeatures, 4);
      expect(report.readyCount, 2);
      expect(report.partialCount, 1);
      expect(report.notReadyCount, 1);
    });

    test('readinessPercent should account for partial as 0.5', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.weatherCache,
            status: OfflineReadinessStatus.partial,
          ),
        ],
      );

      // (1.0 + 0.5) / 2 * 100 = 75%
      expect(report.readinessPercent, 75.0);
    });

    test('readinessPercent should be 0 for empty report', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [],
      );
      expect(report.readinessPercent, 0);
    });

    test('readinessPercent should be 100 when all ready', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.syncOutbox,
            status: OfflineReadinessStatus.ready,
          ),
        ],
      );
      expect(report.readinessPercent, 100.0);
    });

    test('criticalFeaturesReady should check only critical features', () {
      final ready = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.taskManagement,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.syncOutbox,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.databaseIntegrity,
            status: OfflineReadinessStatus.ready,
          ),
          // Non-critical not ready - should still pass
          FeatureReadinessResult(
            feature: OfflineFeature.weatherCache,
            status: OfflineReadinessStatus.notReady,
          ),
        ],
      );
      expect(ready.criticalFeaturesReady, true);

      final notReady = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.notReady, // critical!
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.taskManagement,
            status: OfflineReadinessStatus.ready,
          ),
        ],
      );
      expect(notReady.criticalFeaturesReady, false);
    });

    test('isFullyOfflineReady should require all features ready', () {
      final fully = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.weatherCache,
            status: OfflineReadinessStatus.ready,
          ),
        ],
      );
      expect(fully.isFullyOfflineReady, true);

      final partial = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.weatherCache,
            status: OfflineReadinessStatus.notReady,
          ),
        ],
      );
      expect(partial.isFullyOfflineReady, false);
    });

    test('summaryAr/En should reflect fully ready state', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
        ],
      );
      expect(report.summaryAr, contains('جاهز'));
      expect(report.summaryEn, contains('Ready'));
    });

    test('summaryAr/En should reflect partially ready state', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.taskManagement,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.syncOutbox,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.databaseIntegrity,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.weatherCache,
            status: OfflineReadinessStatus.notReady,
          ),
        ],
      );
      expect(report.summaryAr, contains('جزئياً'));
      expect(report.summaryEn, contains('Partially'));
    });

    test('summaryAr/En should reflect not-ready state', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.notReady,
          ),
        ],
      );
      expect(report.summaryAr, contains('غير جاهز'));
      expect(report.summaryEn, contains('Not'));
    });

    test('needsAttention should list notReady and partial features', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.weatherCache,
            status: OfflineReadinessStatus.partial,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.mapTiles,
            status: OfflineReadinessStatus.notReady,
          ),
        ],
      );

      expect(report.needsAttention.length, 2);
    });

    test('toString should include counts and percentage', () {
      final report = OfflineReadinessReport(
        generatedAt: DateTime.now(),
        results: const [
          FeatureReadinessResult(
            feature: OfflineFeature.fieldData,
            status: OfflineReadinessStatus.ready,
          ),
          FeatureReadinessResult(
            feature: OfflineFeature.weatherCache,
            status: OfflineReadinessStatus.notReady,
          ),
        ],
      );

      final str = report.toString();
      expect(str, contains('1/2'));
      expect(str, contains('50%'));
    });
  });

  group('OfflineCompletenessChecker', () {
    test('checkAll should return report with all features', () async {
      final checker = OfflineCompletenessChecker();
      final report = await checker.checkAll();

      expect(report.totalFeatures, OfflineFeature.values.length);
      expect(report.totalFeatures, 10);
    });

    test('checkFeature should return result for each feature', () async {
      final checker = OfflineCompletenessChecker();

      for (final feature in OfflineFeature.values) {
        final result = await checker.checkFeature(feature);
        expect(result.feature, feature);
      }
    });
  });
}
