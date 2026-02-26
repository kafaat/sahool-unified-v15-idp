import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/dashboard/smart_recommendations.dart';

void main() {
  group('RecommendationPriority', () {
    test('should have 4 levels', () {
      expect(RecommendationPriority.values.length, 4);
    });

    test('should have Arabic labels', () {
      expect(RecommendationPriority.critical.labelAr, 'حرج');
      expect(RecommendationPriority.high.labelAr, 'مرتفع');
      expect(RecommendationPriority.medium.labelAr, 'متوسط');
      expect(RecommendationPriority.low.labelAr, 'منخفض');
    });

    test('should have English labels', () {
      expect(RecommendationPriority.critical.labelEn, 'Critical');
      expect(RecommendationPriority.high.labelEn, 'High');
      expect(RecommendationPriority.medium.labelEn, 'Medium');
      expect(RecommendationPriority.low.labelEn, 'Low');
    });

    test('sortWeight should be ordered critical > high > medium > low', () {
      expect(RecommendationPriority.critical.sortWeight,
          greaterThan(RecommendationPriority.high.sortWeight));
      expect(RecommendationPriority.high.sortWeight,
          greaterThan(RecommendationPriority.medium.sortWeight));
      expect(RecommendationPriority.medium.sortWeight,
          greaterThan(RecommendationPriority.low.sortWeight));
    });
  });

  group('RecommendationCategory', () {
    test('should have 9 categories', () {
      expect(RecommendationCategory.values.length, 9);
    });

    test('should have Arabic labels', () {
      expect(RecommendationCategory.irrigation.labelAr, 'الري');
      expect(RecommendationCategory.pest.labelAr, 'الآفات');
      expect(RecommendationCategory.disease.labelAr, 'الأمراض');
      expect(RecommendationCategory.weather.labelAr, 'الطقس');
      expect(RecommendationCategory.harvest.labelAr, 'الحصاد');
      expect(RecommendationCategory.fertilizer.labelAr, 'التسميد');
      expect(RecommendationCategory.equipment.labelAr, 'المعدات');
      expect(RecommendationCategory.task.labelAr, 'المهام');
      expect(RecommendationCategory.general.labelAr, 'عام');
    });

    test('should have English labels', () {
      expect(RecommendationCategory.irrigation.labelEn, 'Irrigation');
      expect(RecommendationCategory.pest.labelEn, 'Pest');
      expect(RecommendationCategory.disease.labelEn, 'Disease');
      expect(RecommendationCategory.weather.labelEn, 'Weather');
      expect(RecommendationCategory.harvest.labelEn, 'Harvest');
      expect(RecommendationCategory.fertilizer.labelEn, 'Fertilizer');
      expect(RecommendationCategory.equipment.labelEn, 'Equipment');
      expect(RecommendationCategory.task.labelEn, 'Task');
      expect(RecommendationCategory.general.labelEn, 'General');
    });

    test('should have icon names', () {
      expect(RecommendationCategory.irrigation.iconName, 'water_drop');
      expect(RecommendationCategory.pest.iconName, 'bug_report');
      expect(RecommendationCategory.weather.iconName, 'cloud');
    });
  });

  group('SmartRecommendation', () {
    SmartRecommendation createRecommendation({
      String id = 'rec-1',
      RecommendationPriority priority = RecommendationPriority.medium,
      RecommendationCategory category = RecommendationCategory.irrigation,
      DateTime? expiresAt,
      String? fieldId,
      String? actionRoute,
      bool isDismissed = false,
    }) {
      return SmartRecommendation(
        id: id,
        titleAr: 'توصية اختبار',
        titleEn: 'Test Recommendation',
        descriptionAr: 'وصف التوصية',
        descriptionEn: 'Recommendation description',
        priority: priority,
        category: category,
        createdAt: DateTime.now(),
        expiresAt: expiresAt,
        fieldId: fieldId,
        actionRoute: actionRoute,
        isDismissed: isDismissed,
      );
    }

    test('should create with required fields', () {
      final rec = createRecommendation();
      expect(rec.id, 'rec-1');
      expect(rec.titleAr, 'توصية اختبار');
      expect(rec.priority, RecommendationPriority.medium);
      expect(rec.category, RecommendationCategory.irrigation);
      expect(rec.isDismissed, false);
      expect(rec.metadata, isEmpty);
    });

    test('isExpired should return false when no expiresAt', () {
      final rec = createRecommendation();
      expect(rec.isExpired, false);
    });

    test('isExpired should return false for future expiry', () {
      final rec = createRecommendation(
        expiresAt: DateTime.now().add(const Duration(hours: 1)),
      );
      expect(rec.isExpired, false);
    });

    test('isExpired should return true for past expiry', () {
      final rec = createRecommendation(
        expiresAt: DateTime.now().subtract(const Duration(hours: 1)),
      );
      expect(rec.isExpired, true);
    });

    test('isFieldSpecific should check for fieldId', () {
      final withField = createRecommendation(fieldId: 'field-1');
      final withoutField = createRecommendation();

      expect(withField.isFieldSpecific, true);
      expect(withoutField.isFieldSpecific, false);
    });

    test('hasAction should check for actionRoute', () {
      final withAction = createRecommendation(actionRoute: '/fields/1');
      final withoutAction = createRecommendation();

      expect(withAction.hasAction, true);
      expect(withoutAction.hasAction, false);
    });

    test('copyWith should update isDismissed', () {
      final rec = createRecommendation();
      final dismissed = rec.copyWith(isDismissed: true);

      expect(dismissed.isDismissed, true);
      expect(dismissed.id, rec.id);
      expect(dismissed.priority, rec.priority);
    });

    test('toString should include id, priority, and category', () {
      final rec = createRecommendation();
      final str = rec.toString();
      expect(str, contains('rec-1'));
      expect(str, contains('Medium'));
      expect(str, contains('Irrigation'));
    });
  });

  group('DashboardStats', () {
    test('should have sensible defaults', () {
      const stats = DashboardStats();
      expect(stats.totalFields, 0);
      expect(stats.fieldsNeedingAttention, 0);
      expect(stats.averageNdvi, isNull);
      expect(stats.pendingTasks, 0);
      expect(stats.overdueTasks, 0);
      expect(stats.totalAreaHectares, 0);
      expect(stats.activeSensors, 0);
      expect(stats.offlineSensors, 0);
      expect(stats.lastSyncAt, isNull);
    });

    test('fieldHealthPercent should compute correctly', () {
      const stats = DashboardStats(
        totalFields: 10,
        fieldsNeedingAttention: 3,
      );
      expect(stats.fieldHealthPercent, 70.0);
    });

    test('fieldHealthPercent should be 100 when no fields', () {
      const stats = DashboardStats();
      expect(stats.fieldHealthPercent, 100);
    });

    test('sensorHealthPercent should compute correctly', () {
      const stats = DashboardStats(
        activeSensors: 8,
        offlineSensors: 2,
      );
      expect(stats.sensorHealthPercent, 80.0);
    });

    test('sensorHealthPercent should be 100 when no sensors', () {
      const stats = DashboardStats();
      expect(stats.sensorHealthPercent, 100);
    });

    test('taskSummaryAr should prioritize overdue', () {
      const stats = DashboardStats(overdueTasks: 3, pendingTasks: 5);
      expect(stats.taskSummaryAr, contains('متأخرة'));
      expect(stats.taskSummaryEn, contains('overdue'));
    });

    test('taskSummaryAr should show pending when no overdue', () {
      const stats = DashboardStats(pendingTasks: 5);
      expect(stats.taskSummaryAr, contains('معلقة'));
      expect(stats.taskSummaryEn, contains('pending'));
    });

    test('taskSummaryAr should show no tasks when empty', () {
      const stats = DashboardStats();
      expect(stats.taskSummaryAr, contains('لا'));
      expect(stats.taskSummaryEn, contains('No'));
    });

    test('isSyncFresh should be true for recent sync', () {
      final stats = DashboardStats(
        lastSyncAt: DateTime.now().subtract(const Duration(minutes: 5)),
      );
      expect(stats.isSyncFresh, true);
    });

    test('isSyncFresh should be false for old sync', () {
      final stats = DashboardStats(
        lastSyncAt: DateTime.now().subtract(const Duration(hours: 1)),
      );
      expect(stats.isSyncFresh, false);
    });

    test('isSyncFresh should be false when never synced', () {
      const stats = DashboardStats();
      expect(stats.isSyncFresh, false);
    });

    test('copyWith should update fields', () {
      const stats = DashboardStats();
      final updated = stats.copyWith(
        totalFields: 5,
        pendingTasks: 3,
        activeSensors: 10,
      );

      expect(updated.totalFields, 5);
      expect(updated.pendingTasks, 3);
      expect(updated.activeSensors, 10);
      expect(updated.fieldsNeedingAttention, 0); // preserved
    });
  });

  group('SmartRecommendationEngine', () {
    late SmartRecommendationEngine engine;

    SmartRecommendation makeRec({
      required String id,
      RecommendationPriority priority = RecommendationPriority.medium,
      RecommendationCategory category = RecommendationCategory.general,
      String? fieldId,
      DateTime? expiresAt,
    }) {
      return SmartRecommendation(
        id: id,
        titleAr: 'توصية $id',
        titleEn: 'Rec $id',
        descriptionAr: 'وصف',
        descriptionEn: 'desc',
        priority: priority,
        category: category,
        createdAt: DateTime.now(),
        fieldId: fieldId,
        expiresAt: expiresAt,
      );
    }

    setUp(() {
      engine = SmartRecommendationEngine();
    });

    test('should start empty', () {
      expect(engine.activeRecommendations, isEmpty);
      expect(engine.criticalRecommendations, isEmpty);
    });

    test('should add recommendations', () {
      engine.addRecommendation(makeRec(id: 'r1'));
      engine.addRecommendation(makeRec(id: 'r2'));

      expect(engine.activeRecommendations.length, 2);
    });

    test('should replace recommendation with same ID', () {
      engine.addRecommendation(makeRec(
        id: 'r1',
        priority: RecommendationPriority.low,
      ));
      engine.addRecommendation(makeRec(
        id: 'r1',
        priority: RecommendationPriority.critical,
      ));

      expect(engine.activeRecommendations.length, 1);
      expect(
        engine.activeRecommendations.first.priority,
        RecommendationPriority.critical,
      );
    });

    test('should sort by priority (highest first)', () {
      engine.addRecommendation(
          makeRec(id: 'low', priority: RecommendationPriority.low));
      engine.addRecommendation(
          makeRec(id: 'critical', priority: RecommendationPriority.critical));
      engine.addRecommendation(
          makeRec(id: 'high', priority: RecommendationPriority.high));

      final active = engine.activeRecommendations;
      expect(active[0].id, 'critical');
      expect(active[1].id, 'high');
      expect(active[2].id, 'low');
    });

    test('should filter critical recommendations', () {
      engine.addRecommendation(
          makeRec(id: 'c1', priority: RecommendationPriority.critical));
      engine.addRecommendation(
          makeRec(id: 'h1', priority: RecommendationPriority.high));
      engine.addRecommendation(
          makeRec(id: 'c2', priority: RecommendationPriority.critical));

      expect(engine.criticalRecommendations.length, 2);
    });

    test('should filter by field', () {
      engine.addRecommendation(makeRec(id: 'r1', fieldId: 'field-A'));
      engine.addRecommendation(makeRec(id: 'r2', fieldId: 'field-B'));
      engine.addRecommendation(makeRec(id: 'r3', fieldId: 'field-A'));

      expect(engine.forField('field-A').length, 2);
      expect(engine.forField('field-B').length, 1);
      expect(engine.forField('field-C').length, 0);
    });

    test('should filter by category', () {
      engine.addRecommendation(makeRec(
        id: 'r1',
        category: RecommendationCategory.irrigation,
      ));
      engine.addRecommendation(makeRec(
        id: 'r2',
        category: RecommendationCategory.pest,
      ));
      engine.addRecommendation(makeRec(
        id: 'r3',
        category: RecommendationCategory.irrigation,
      ));

      expect(engine.byCategory(RecommendationCategory.irrigation).length, 2);
      expect(engine.byCategory(RecommendationCategory.pest).length, 1);
    });

    test('should count by priority', () {
      engine.addRecommendation(
          makeRec(id: 'c1', priority: RecommendationPriority.critical));
      engine.addRecommendation(
          makeRec(id: 'h1', priority: RecommendationPriority.high));
      engine.addRecommendation(
          makeRec(id: 'c2', priority: RecommendationPriority.critical));

      final counts = engine.countByPriority;
      expect(counts[RecommendationPriority.critical], 2);
      expect(counts[RecommendationPriority.high], 1);
    });

    test('should dismiss recommendation', () {
      engine.addRecommendation(makeRec(id: 'r1'));
      engine.addRecommendation(makeRec(id: 'r2'));
      engine.dismiss('r1');

      expect(engine.activeRecommendations.length, 1);
      expect(engine.activeRecommendations.first.id, 'r2');
    });

    test('should not re-add dismissed recommendations', () {
      engine.addRecommendation(makeRec(id: 'r1'));
      engine.dismiss('r1');
      engine.addRecommendation(makeRec(id: 'r1'));

      expect(engine.activeRecommendations, isEmpty);
    });

    test('should exclude expired recommendations', () {
      engine.addRecommendation(makeRec(
        id: 'expired',
        expiresAt: DateTime.now().subtract(const Duration(hours: 1)),
      ));
      engine.addRecommendation(makeRec(
        id: 'active',
        expiresAt: DateTime.now().add(const Duration(hours: 1)),
      ));

      expect(engine.activeRecommendations.length, 1);
      expect(engine.activeRecommendations.first.id, 'active');
    });

    test('should clear expired recommendations', () {
      engine.addRecommendation(makeRec(
        id: 'expired',
        expiresAt: DateTime.now().subtract(const Duration(hours: 1)),
      ));
      engine.addRecommendation(makeRec(id: 'active'));

      final removed = engine.clearExpired();
      expect(removed, 1);
    });

    test('should reset all', () {
      engine.addRecommendation(makeRec(id: 'r1'));
      engine.addRecommendation(makeRec(id: 'r2'));
      engine.dismiss('r1');
      engine.reset();

      expect(engine.activeRecommendations, isEmpty);

      // After reset, dismissed IDs should be cleared
      engine.addRecommendation(makeRec(id: 'r1'));
      expect(engine.activeRecommendations.length, 1);
    });
  });

  group('DashboardState', () {
    test('should have sensible defaults', () {
      const state = DashboardState();
      expect(state.stats, isNotNull);
      expect(state.recommendations, isEmpty);
      expect(state.isLoading, false);
      expect(state.error, isNull);
      expect(state.lastRefreshAt, isNull);
    });

    test('hasData should be false initially', () {
      const state = DashboardState();
      expect(state.hasData, false);
    });

    test('hasData should be true with fields', () {
      const state = DashboardState(
        stats: DashboardStats(totalFields: 1),
      );
      expect(state.hasData, true);
    });

    test('hasCriticalAlerts should detect critical recommendations', () {
      final state = DashboardState(
        recommendations: [
          SmartRecommendation(
            id: 'c1',
            titleAr: 'تنبيه',
            titleEn: 'Alert',
            descriptionAr: 'وصف',
            descriptionEn: 'desc',
            priority: RecommendationPriority.critical,
            category: RecommendationCategory.pest,
            createdAt: DateTime.now(),
          ),
        ],
      );
      expect(state.hasCriticalAlerts, true);
    });

    test('activeRecommendationCount should exclude dismissed and expired', () {
      final now = DateTime.now();
      final state = DashboardState(
        recommendations: [
          SmartRecommendation(
            id: 'active',
            titleAr: 'أ',
            titleEn: 'A',
            descriptionAr: 'أ',
            descriptionEn: 'A',
            priority: RecommendationPriority.medium,
            category: RecommendationCategory.general,
            createdAt: now,
          ),
          SmartRecommendation(
            id: 'dismissed',
            titleAr: 'ب',
            titleEn: 'B',
            descriptionAr: 'ب',
            descriptionEn: 'B',
            priority: RecommendationPriority.low,
            category: RecommendationCategory.general,
            createdAt: now,
            isDismissed: true,
          ),
          SmartRecommendation(
            id: 'expired',
            titleAr: 'ج',
            titleEn: 'C',
            descriptionAr: 'ج',
            descriptionEn: 'C',
            priority: RecommendationPriority.low,
            category: RecommendationCategory.general,
            createdAt: now,
            expiresAt: now.subtract(const Duration(hours: 1)),
          ),
        ],
      );
      expect(state.activeRecommendationCount, 1);
    });

    test('copyWith should update fields', () {
      const state = DashboardState();
      final updated = state.copyWith(
        isLoading: true,
        error: 'Something went wrong',
      );

      expect(updated.isLoading, true);
      expect(updated.error, 'Something went wrong');
    });

    test('copyWith clearError should set error to null', () {
      const state = DashboardState(error: 'Error');
      final cleared = state.copyWith(clearError: true);
      expect(cleared.error, isNull);
    });
  });
}
