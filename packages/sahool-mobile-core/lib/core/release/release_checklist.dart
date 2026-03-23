import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// SAHOOL Golden Release Checklist
/// قائمة التحقق للإصدار الذهبي v16.0.0
///
/// Validates all golden release criteria programmatically.
/// Used for CI/CD gating and pre-release verification.

// ═══════════════════════════════════════════════════════════════════════════
// Release Criteria
// ═══════════════════════════════════════════════════════════════════════════

/// Target version for golden release
const String kGoldenReleaseVersion = '16.0.0';

/// Golden release criteria thresholds
class ReleaseCriteria {
  ReleaseCriteria._();

  /// Minimum test coverage percentage
  static const double minTestCoverage = 80.0;

  /// Minimum crash-free rate percentage
  static const double minCrashFreeRate = 99.5;

  /// Maximum cold start time in seconds
  static const double maxColdStartSeconds = 2.0;

  /// Minimum average frame rate (FPS)
  static const double minFrameRate = 55.0;

  /// Maximum memory usage in MB
  static const double maxMemoryMB = 150.0;

  /// Maximum APK size in MB
  static const double maxApkSizeMB = 50.0;

  /// Maximum battery drain per hour (active use) percentage
  static const double maxBatteryDrainPerHour = 5.0;

  /// Minimum app store rating
  static const double minAppRating = 4.5;
}

// ═══════════════════════════════════════════════════════════════════════════
// Checklist Item Model
// ═══════════════════════════════════════════════════════════════════════════

/// Category for checklist items
enum ChecklistCategory {
  codeQuality,
  testing,
  performance,
  security,
  localization,
  accessibility,
  release,
}

/// Extension for ChecklistCategory
extension ChecklistCategoryExtension on ChecklistCategory {
  String get nameAr {
    switch (this) {
      case ChecklistCategory.codeQuality:
        return 'جودة الكود';
      case ChecklistCategory.testing:
        return 'الاختبارات';
      case ChecklistCategory.performance:
        return 'الأداء';
      case ChecklistCategory.security:
        return 'الأمان';
      case ChecklistCategory.localization:
        return 'التوطين';
      case ChecklistCategory.accessibility:
        return 'إمكانية الوصول';
      case ChecklistCategory.release:
        return 'الإصدار';
    }
  }

  String get nameEn {
    switch (this) {
      case ChecklistCategory.codeQuality:
        return 'Code Quality';
      case ChecklistCategory.testing:
        return 'Testing';
      case ChecklistCategory.performance:
        return 'Performance';
      case ChecklistCategory.security:
        return 'Security';
      case ChecklistCategory.localization:
        return 'Localization';
      case ChecklistCategory.accessibility:
        return 'Accessibility';
      case ChecklistCategory.release:
        return 'Release';
    }
  }
}

/// Status of a checklist item
enum ChecklistStatus {
  passed,
  failed,
  warning,
  notChecked,
}

/// A single checklist item
@immutable
class ChecklistItem {
  final String id;
  final String titleAr;
  final String titleEn;
  final ChecklistCategory category;
  final ChecklistStatus status;
  final String? details;
  final double? measuredValue;
  final double? targetValue;

  const ChecklistItem({
    required this.id,
    required this.titleAr,
    required this.titleEn,
    required this.category,
    this.status = ChecklistStatus.notChecked,
    this.details,
    this.measuredValue,
    this.targetValue,
  });

  ChecklistItem copyWith({
    ChecklistStatus? status,
    String? details,
    double? measuredValue,
  }) {
    return ChecklistItem(
      id: id,
      titleAr: titleAr,
      titleEn: titleEn,
      category: category,
      status: status ?? this.status,
      details: details ?? this.details,
      measuredValue: measuredValue ?? this.measuredValue,
      targetValue: targetValue,
    );
  }

  /// Whether this item is passing
  bool get isPassing => status == ChecklistStatus.passed;

  /// Whether this item meets or exceeds target (for numeric criteria)
  bool get meetsTarget {
    if (measuredValue == null || targetValue == null) return isPassing;
    return measuredValue! >= targetValue!;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Release Report
// ═══════════════════════════════════════════════════════════════════════════

/// Complete release validation report
@immutable
class ReleaseReport {
  final String version;
  final DateTime generatedAt;
  final List<ChecklistItem> items;

  const ReleaseReport({
    required this.version,
    required this.generatedAt,
    required this.items,
  });

  /// Total number of items
  int get totalItems => items.length;

  /// Number of passing items
  int get passedItems =>
      items.where((i) => i.status == ChecklistStatus.passed).length;

  /// Number of failing items
  int get failedItems =>
      items.where((i) => i.status == ChecklistStatus.failed).length;

  /// Number of warning items
  int get warningItems =>
      items.where((i) => i.status == ChecklistStatus.warning).length;

  /// Number of unchecked items
  int get uncheckedItems =>
      items.where((i) => i.status == ChecklistStatus.notChecked).length;

  /// Overall pass rate
  double get passRate => totalItems > 0 ? (passedItems / totalItems) * 100 : 0;

  /// Whether all items pass (release-ready)
  bool get isReleaseReady => failedItems == 0 && uncheckedItems == 0;

  /// Whether the release has critical failures
  bool get hasCriticalFailures => failedItems > 0;

  /// Items grouped by category
  Map<ChecklistCategory, List<ChecklistItem>> get itemsByCategory {
    final map = <ChecklistCategory, List<ChecklistItem>>{};
    for (final item in items) {
      map.putIfAbsent(item.category, () => []).add(item);
    }
    return map;
  }

  /// Category pass rates
  Map<ChecklistCategory, double> get categoryPassRates {
    final rates = <ChecklistCategory, double>{};
    for (final entry in itemsByCategory.entries) {
      final passed = entry.value.where((i) => i.isPassing).length;
      rates[entry.key] =
          entry.value.isNotEmpty ? (passed / entry.value.length) * 100 : 0;
    }
    return rates;
  }

  /// Summary for display
  String get summaryAr {
    if (isReleaseReady) return 'جاهز للإصدار ✓';
    if (hasCriticalFailures) return '$failedItems عنصر فشل - غير جاهز';
    return '$uncheckedItems عنصر لم يُفحص بعد';
  }

  String get summaryEn {
    if (isReleaseReady) return 'Release Ready ✓';
    if (hasCriticalFailures) return '$failedItems items failed - Not Ready';
    return '$uncheckedItems items unchecked';
  }

  @override
  String toString() {
    return 'ReleaseReport(v$version: $passedItems/$totalItems passed, '
        '${passRate.toStringAsFixed(1)}%)';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Release Checklist Builder
// ═══════════════════════════════════════════════════════════════════════════

/// Builds the complete golden release checklist
class ReleaseChecklistBuilder {
  /// Build the full checklist with all items
  static List<ChecklistItem> buildChecklist() {
    return [
      // Code Quality
      const ChecklistItem(
        id: 'cq_lint',
        titleAr: 'جميع قواعد Lint تمر',
        titleEn: 'All lint rules passing',
        category: ChecklistCategory.codeQuality,
      ),
      const ChecklistItem(
        id: 'cq_no_todo',
        titleAr: 'لا يوجد TODO/FIXME في كود الإنتاج',
        titleEn: 'No TODO/FIXME in production code',
        category: ChecklistCategory.codeQuality,
      ),
      const ChecklistItem(
        id: 'cq_dead_code',
        titleAr: 'تم إزالة الكود الميت',
        titleEn: 'All dead code removed',
        category: ChecklistCategory.codeQuality,
      ),
      const ChecklistItem(
        id: 'cq_docs',
        titleAr: 'التوثيق مكتمل',
        titleEn: 'Documentation complete',
        category: ChecklistCategory.codeQuality,
      ),

      // Testing
      ChecklistItem(
        id: 'test_coverage',
        titleAr: 'تغطية الاختبارات >= 80%',
        titleEn: 'Test coverage >= 80%',
        category: ChecklistCategory.testing,
        targetValue: ReleaseCriteria.minTestCoverage,
      ),
      const ChecklistItem(
        id: 'test_widget',
        titleAr: 'اختبارات Widget للمسارات الحرجة',
        titleEn: 'Widget tests for critical flows',
        category: ChecklistCategory.testing,
      ),
      const ChecklistItem(
        id: 'test_integration',
        titleAr: 'اختبارات التكامل للمسارات الرئيسية',
        titleEn: 'Integration tests for main journeys',
        category: ChecklistCategory.testing,
      ),
      const ChecklistItem(
        id: 'test_manual',
        titleAr: 'اختبار يدوي لجميع الميزات',
        titleEn: 'Manual QA for all features',
        category: ChecklistCategory.testing,
      ),

      // Performance
      ChecklistItem(
        id: 'perf_cold_start',
        titleAr: 'زمن البدء البارد <= 2 ثانية',
        titleEn: 'Cold start time <= 2 seconds',
        category: ChecklistCategory.performance,
        targetValue: ReleaseCriteria.maxColdStartSeconds,
      ),
      ChecklistItem(
        id: 'perf_frame_rate',
        titleAr: 'معدل الإطارات >= 55 FPS',
        titleEn: 'Frame rate >= 55 FPS average',
        category: ChecklistCategory.performance,
        targetValue: ReleaseCriteria.minFrameRate,
      ),
      ChecklistItem(
        id: 'perf_memory',
        titleAr: 'استخدام الذاكرة <= 150 MB',
        titleEn: 'Memory usage <= 150 MB',
        category: ChecklistCategory.performance,
        targetValue: ReleaseCriteria.maxMemoryMB,
      ),
      ChecklistItem(
        id: 'perf_apk_size',
        titleAr: 'حجم APK <= 50 MB',
        titleEn: 'APK size <= 50 MB',
        category: ChecklistCategory.performance,
        targetValue: ReleaseCriteria.maxApkSizeMB,
      ),

      // Security
      const ChecklistItem(
        id: 'sec_audit',
        titleAr: 'تدقيق الأمان تم',
        titleEn: 'Security audit passed',
        category: ChecklistCategory.security,
      ),
      const ChecklistItem(
        id: 'sec_no_secrets',
        titleAr: 'لا أسرار مكتوبة في الكود',
        titleEn: 'No hardcoded secrets',
        category: ChecklistCategory.security,
      ),
      const ChecklistItem(
        id: 'sec_ssl',
        titleAr: 'تثبيت الشهادات مفعل',
        titleEn: 'SSL/Certificate pinning enabled',
        category: ChecklistCategory.security,
      ),
      const ChecklistItem(
        id: 'sec_encryption',
        titleAr: 'البيانات الحساسة مشفرة',
        titleEn: 'Sensitive data encrypted',
        category: ChecklistCategory.security,
      ),

      // Localization
      const ChecklistItem(
        id: 'l10n_arabic',
        titleAr: 'الترجمة العربية مكتملة',
        titleEn: 'Arabic translations complete',
        category: ChecklistCategory.localization,
      ),
      const ChecklistItem(
        id: 'l10n_rtl',
        titleAr: 'تخطيط RTL مختبر',
        titleEn: 'RTL layout tested',
        category: ChecklistCategory.localization,
      ),
      const ChecklistItem(
        id: 'l10n_formats',
        titleAr: 'تنسيقات التاريخ والأرقام صحيحة',
        titleEn: 'Date/number formats correct',
        category: ChecklistCategory.localization,
      ),

      // Accessibility
      const ChecklistItem(
        id: 'a11y_screen_reader',
        titleAr: 'دعم قارئ الشاشة',
        titleEn: 'Screen reader support',
        category: ChecklistCategory.accessibility,
      ),
      const ChecklistItem(
        id: 'a11y_contrast',
        titleAr: 'نسب التباين كافية',
        titleEn: 'Sufficient contrast ratios',
        category: ChecklistCategory.accessibility,
      ),
      const ChecklistItem(
        id: 'a11y_touch',
        titleAr: 'أهداف اللمس >= 48 dp',
        titleEn: 'Touch targets >= 48 dp',
        category: ChecklistCategory.accessibility,
      ),

      // Release
      const ChecklistItem(
        id: 'rel_version',
        titleAr: 'الإصدار محدث إلى 16.0.0',
        titleEn: 'Version bumped to 16.0.0',
        category: ChecklistCategory.release,
      ),
      const ChecklistItem(
        id: 'rel_changelog',
        titleAr: 'سجل التغييرات محدث',
        titleEn: 'Changelog updated',
        category: ChecklistCategory.release,
      ),
      const ChecklistItem(
        id: 'rel_store',
        titleAr: 'قوائم المتجر جاهزة',
        titleEn: 'Store listings ready',
        category: ChecklistCategory.release,
      ),
    ];
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for the release checklist items
final releaseChecklistProvider = Provider<List<ChecklistItem>>((ref) {
  return ReleaseChecklistBuilder.buildChecklist();
});

/// Provider for the release report
final releaseReportProvider = Provider<ReleaseReport>((ref) {
  final items = ref.watch(releaseChecklistProvider);
  return ReleaseReport(
    version: kGoldenReleaseVersion,
    generatedAt: DateTime.now(),
    items: items,
  );
});
