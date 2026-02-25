import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/release/release_checklist.dart';

void main() {
  group('ReleaseCriteria', () {
    test('should have correct threshold values', () {
      expect(ReleaseCriteria.minTestCoverage, 80.0);
      expect(ReleaseCriteria.minCrashFreeRate, 99.5);
      expect(ReleaseCriteria.maxColdStartSeconds, 2.0);
      expect(ReleaseCriteria.minFrameRate, 55.0);
      expect(ReleaseCriteria.maxMemoryMB, 150.0);
      expect(ReleaseCriteria.maxApkSizeMB, 50.0);
      expect(ReleaseCriteria.maxBatteryDrainPerHour, 5.0);
      expect(ReleaseCriteria.minAppRating, 4.5);
    });
  });

  group('ChecklistCategory', () {
    test('should have 7 categories', () {
      expect(ChecklistCategory.values.length, 7);
    });

    test('should have Arabic names', () {
      expect(ChecklistCategory.codeQuality.nameAr, 'جودة الكود');
      expect(ChecklistCategory.testing.nameAr, 'الاختبارات');
      expect(ChecklistCategory.performance.nameAr, 'الأداء');
      expect(ChecklistCategory.security.nameAr, 'الأمان');
      expect(ChecklistCategory.localization.nameAr, 'التوطين');
      expect(ChecklistCategory.accessibility.nameAr, 'إمكانية الوصول');
      expect(ChecklistCategory.release.nameAr, 'الإصدار');
    });

    test('should have English names', () {
      expect(ChecklistCategory.codeQuality.nameEn, 'Code Quality');
      expect(ChecklistCategory.testing.nameEn, 'Testing');
      expect(ChecklistCategory.performance.nameEn, 'Performance');
      expect(ChecklistCategory.security.nameEn, 'Security');
      expect(ChecklistCategory.localization.nameEn, 'Localization');
      expect(ChecklistCategory.accessibility.nameEn, 'Accessibility');
      expect(ChecklistCategory.release.nameEn, 'Release');
    });
  });

  group('ChecklistStatus', () {
    test('should have 4 statuses', () {
      expect(ChecklistStatus.values.length, 4);
      expect(ChecklistStatus.values, contains(ChecklistStatus.passed));
      expect(ChecklistStatus.values, contains(ChecklistStatus.failed));
      expect(ChecklistStatus.values, contains(ChecklistStatus.warning));
      expect(ChecklistStatus.values, contains(ChecklistStatus.notChecked));
    });
  });

  group('ChecklistItem', () {
    test('should create with required fields', () {
      const item = ChecklistItem(
        id: 'test_item',
        titleAr: 'عنصر اختبار',
        titleEn: 'Test Item',
        category: ChecklistCategory.testing,
      );

      expect(item.id, 'test_item');
      expect(item.titleAr, 'عنصر اختبار');
      expect(item.titleEn, 'Test Item');
      expect(item.category, ChecklistCategory.testing);
      expect(item.status, ChecklistStatus.notChecked);
      expect(item.details, isNull);
      expect(item.measuredValue, isNull);
      expect(item.targetValue, isNull);
    });

    test('isPassing should return true only for passed status', () {
      const passed = ChecklistItem(
        id: 'p',
        titleAr: 'أ',
        titleEn: 'A',
        category: ChecklistCategory.testing,
        status: ChecklistStatus.passed,
      );
      const failed = ChecklistItem(
        id: 'f',
        titleAr: 'ب',
        titleEn: 'B',
        category: ChecklistCategory.testing,
        status: ChecklistStatus.failed,
      );

      expect(passed.isPassing, true);
      expect(failed.isPassing, false);
    });

    test('meetsTarget should compare measured vs target values', () {
      const meetsItem = ChecklistItem(
        id: 'meets',
        titleAr: 'أ',
        titleEn: 'A',
        category: ChecklistCategory.performance,
        measuredValue: 85.0,
        targetValue: 80.0,
      );
      const failsItem = ChecklistItem(
        id: 'fails',
        titleAr: 'ب',
        titleEn: 'B',
        category: ChecklistCategory.performance,
        measuredValue: 75.0,
        targetValue: 80.0,
      );

      expect(meetsItem.meetsTarget, true);
      expect(failsItem.meetsTarget, false);
    });

    test('meetsTarget should fallback to isPassing when no values', () {
      const passedItem = ChecklistItem(
        id: 'p',
        titleAr: 'أ',
        titleEn: 'A',
        category: ChecklistCategory.testing,
        status: ChecklistStatus.passed,
      );

      expect(passedItem.meetsTarget, true);
    });

    test('copyWith should update specified fields', () {
      const original = ChecklistItem(
        id: 'item1',
        titleAr: 'عنصر',
        titleEn: 'Item',
        category: ChecklistCategory.security,
      );
      final updated = original.copyWith(
        status: ChecklistStatus.passed,
        details: 'All good',
        measuredValue: 100.0,
      );

      expect(updated.id, 'item1');
      expect(updated.status, ChecklistStatus.passed);
      expect(updated.details, 'All good');
      expect(updated.measuredValue, 100.0);
      expect(updated.category, ChecklistCategory.security);
    });
  });

  group('ReleaseReport', () {
    test('should compute correct counts', () {
      final report = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.passed,
          ),
          ChecklistItem(
            id: '2',
            titleAr: 'ب',
            titleEn: 'B',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.passed,
          ),
          ChecklistItem(
            id: '3',
            titleAr: 'ج',
            titleEn: 'C',
            category: ChecklistCategory.security,
            status: ChecklistStatus.failed,
          ),
          ChecklistItem(
            id: '4',
            titleAr: 'د',
            titleEn: 'D',
            category: ChecklistCategory.performance,
            status: ChecklistStatus.warning,
          ),
          ChecklistItem(
            id: '5',
            titleAr: 'هـ',
            titleEn: 'E',
            category: ChecklistCategory.release,
            status: ChecklistStatus.notChecked,
          ),
        ],
      );

      expect(report.totalItems, 5);
      expect(report.passedItems, 2);
      expect(report.failedItems, 1);
      expect(report.warningItems, 1);
      expect(report.uncheckedItems, 1);
    });

    test('should compute pass rate', () {
      final report = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.passed,
          ),
          ChecklistItem(
            id: '2',
            titleAr: 'ب',
            titleEn: 'B',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.failed,
          ),
        ],
      );

      expect(report.passRate, 50.0);
    });

    test('should handle empty items', () {
      final report = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [],
      );

      expect(report.passRate, 0);
      expect(report.isReleaseReady, true); // no failures
    });

    test('isReleaseReady should be true only when no failures and no unchecked',
        () {
      final ready = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.passed,
          ),
        ],
      );
      final notReady = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.failed,
          ),
        ],
      );

      expect(ready.isReleaseReady, true);
      expect(notReady.isReleaseReady, false);
    });

    test('hasCriticalFailures should detect failures', () {
      final withFailure = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.security,
            status: ChecklistStatus.failed,
          ),
        ],
      );
      final noFailure = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.security,
            status: ChecklistStatus.passed,
          ),
        ],
      );

      expect(withFailure.hasCriticalFailures, true);
      expect(noFailure.hasCriticalFailures, false);
    });

    test('itemsByCategory should group correctly', () {
      final report = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.passed,
          ),
          ChecklistItem(
            id: '2',
            titleAr: 'ب',
            titleEn: 'B',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.failed,
          ),
          ChecklistItem(
            id: '3',
            titleAr: 'ج',
            titleEn: 'C',
            category: ChecklistCategory.security,
            status: ChecklistStatus.passed,
          ),
        ],
      );

      final byCategory = report.itemsByCategory;
      expect(byCategory[ChecklistCategory.testing]?.length, 2);
      expect(byCategory[ChecklistCategory.security]?.length, 1);
      expect(byCategory[ChecklistCategory.performance], isNull);
    });

    test('categoryPassRates should compute per-category', () {
      final report = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.passed,
          ),
          ChecklistItem(
            id: '2',
            titleAr: 'ب',
            titleEn: 'B',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.failed,
          ),
          ChecklistItem(
            id: '3',
            titleAr: 'ج',
            titleEn: 'C',
            category: ChecklistCategory.security,
            status: ChecklistStatus.passed,
          ),
        ],
      );

      final rates = report.categoryPassRates;
      expect(rates[ChecklistCategory.testing], 50.0);
      expect(rates[ChecklistCategory.security], 100.0);
    });

    test('summaryAr/summaryEn should reflect status', () {
      // Release ready
      final ready = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.passed,
          ),
        ],
      );
      expect(ready.summaryAr, contains('جاهز'));
      expect(ready.summaryEn, contains('Ready'));

      // Has failures
      final failed = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.failed,
          ),
        ],
      );
      expect(failed.summaryAr, contains('فشل'));
      expect(failed.summaryEn, contains('failed'));

      // Has unchecked
      final unchecked = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.notChecked,
          ),
        ],
      );
      expect(unchecked.summaryAr, contains('يُفحص'));
      expect(unchecked.summaryEn, contains('unchecked'));
    });

    test('toString should include version and pass rate', () {
      final report = ReleaseReport(
        version: '16.0.0',
        generatedAt: DateTime.now(),
        items: const [
          ChecklistItem(
            id: '1',
            titleAr: 'أ',
            titleEn: 'A',
            category: ChecklistCategory.testing,
            status: ChecklistStatus.passed,
          ),
        ],
      );

      final str = report.toString();
      expect(str, contains('16.0.0'));
      expect(str, contains('1/1'));
    });
  });

  group('ReleaseChecklistBuilder', () {
    test('should build a non-empty checklist', () {
      final items = ReleaseChecklistBuilder.buildChecklist();
      expect(items.isNotEmpty, true);
    });

    test('should have 25 checklist items', () {
      final items = ReleaseChecklistBuilder.buildChecklist();
      expect(items.length, 25);
    });

    test('should have unique IDs', () {
      final items = ReleaseChecklistBuilder.buildChecklist();
      final ids = items.map((i) => i.id).toSet();
      expect(ids.length, items.length);
    });

    test('should cover all categories', () {
      final items = ReleaseChecklistBuilder.buildChecklist();
      final categories = items.map((i) => i.category).toSet();
      expect(categories, contains(ChecklistCategory.codeQuality));
      expect(categories, contains(ChecklistCategory.testing));
      expect(categories, contains(ChecklistCategory.performance));
      expect(categories, contains(ChecklistCategory.security));
      expect(categories, contains(ChecklistCategory.localization));
      expect(categories, contains(ChecklistCategory.accessibility));
      expect(categories, contains(ChecklistCategory.release));
    });

    test('all items should start as notChecked', () {
      final items = ReleaseChecklistBuilder.buildChecklist();
      expect(
        items.every((i) => i.status == ChecklistStatus.notChecked),
        true,
      );
    });

    test('performance items should have target values', () {
      final items = ReleaseChecklistBuilder.buildChecklist();
      final perfItems = items
          .where((i) => i.category == ChecklistCategory.performance)
          .toList();
      expect(perfItems.every((i) => i.targetValue != null), true);
    });

    test('test coverage item should have correct target', () {
      final items = ReleaseChecklistBuilder.buildChecklist();
      final coverageItem = items.firstWhere((i) => i.id == 'test_coverage');
      expect(coverageItem.targetValue, ReleaseCriteria.minTestCoverage);
    });
  });

  group('Golden Release Version', () {
    test('should be 16.0.0', () {
      expect(kGoldenReleaseVersion, '16.0.0');
    });
  });
}
