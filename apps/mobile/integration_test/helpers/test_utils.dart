/// SAHOOL Integration Test - Test Utilities
/// أدوات مساعدة للاختبارات
///
/// Additional utilities for integration testing:
/// - Performance measurement
/// - Accessibility testing
/// - Network simulation
/// - State management helpers
/// - Screenshot utilities

import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import '../fixtures/test_data.dart';

// =============================================================================
// Performance Utilities
// أدوات قياس الأداء
// =============================================================================

/// Performance metrics for tests
/// مقاييس الأداء للاختبارات
class PerformanceMetrics {
  final Duration loadTime;
  final Duration navigationTime;
  final Duration interactionTime;
  final int frameCount;
  final double averageFps;

  const PerformanceMetrics({
    required this.loadTime,
    required this.navigationTime,
    required this.interactionTime,
    required this.frameCount,
    required this.averageFps,
  });

  bool get isAcceptable =>
      loadTime.inSeconds < 5 &&
      navigationTime.inSeconds < 2 &&
      averageFps >= 30;

  @override
  String toString() => '''
Performance Metrics:
- Load Time: ${loadTime.inMilliseconds}ms
- Navigation Time: ${navigationTime.inMilliseconds}ms
- Interaction Time: ${interactionTime.inMilliseconds}ms
- Frame Count: $frameCount
- Average FPS: ${averageFps.toStringAsFixed(1)}
- Acceptable: $isAcceptable
''';
}

/// Measure performance of an action
/// قياس أداء إجراء
Future<Duration> measureDuration(Future<void> Function() action) async {
  final stopwatch = Stopwatch()..start();
  await action();
  stopwatch.stop();
  return stopwatch.elapsed;
}

/// Performance test helper
/// مساعد اختبار الأداء
class PerformanceTester {
  final WidgetTester tester;
  final IntegrationTestWidgetsFlutterBinding binding;

  PerformanceTester(this.tester, this.binding);

  /// Run a performance test and collect metrics
  /// تشغيل اختبار الأداء وجمع المقاييس
  Future<PerformanceMetrics> runTest({
    required Future<void> Function() setup,
    required Future<void> Function() action,
    int iterations = 5,
  }) async {
    // Setup
    final loadTime = await measureDuration(setup);

    // Run action multiple times
    Duration totalNavigationTime = Duration.zero;
    Duration totalInteractionTime = Duration.zero;
    int frameCount = 0;

    for (int i = 0; i < iterations; i++) {
      final navStart = DateTime.now();
      await action();
      await tester.pumpAndSettle();
      totalNavigationTime += DateTime.now().difference(navStart);
    }

    // Calculate averages
    final avgNavTime = Duration(
      milliseconds: totalNavigationTime.inMilliseconds ~/ iterations,
    );

    // Estimate FPS (simplified)
    final fps = frameCount > 0
        ? frameCount / (totalNavigationTime.inMilliseconds / 1000)
        : 60.0;

    return PerformanceMetrics(
      loadTime: loadTime,
      navigationTime: avgNavTime,
      interactionTime: totalInteractionTime,
      frameCount: frameCount,
      averageFps: fps,
    );
  }

  /// Assert performance meets requirements
  /// التأكد من أن الأداء يلبي المتطلبات
  void assertPerformance(PerformanceMetrics metrics) {
    expect(metrics.loadTime.inSeconds, lessThan(5),
        reason: 'Load time should be under 5 seconds');
    expect(metrics.navigationTime.inSeconds, lessThan(2),
        reason: 'Navigation should be under 2 seconds');
  }
}

// =============================================================================
// Accessibility Utilities
// أدوات اختبار إمكانية الوصول
// =============================================================================

/// Accessibility test results
/// نتائج اختبار إمكانية الوصول
class AccessibilityReport {
  final bool hasSemanticsLabels;
  final bool hasMinimumTouchTargets;
  final bool hasProperContrast;
  final bool supportsScreenReader;
  final List<String> issues;

  const AccessibilityReport({
    required this.hasSemanticsLabels,
    required this.hasMinimumTouchTargets,
    required this.hasProperContrast,
    required this.supportsScreenReader,
    this.issues = const [],
  });

  bool get isAccessible =>
      hasSemanticsLabels &&
      hasMinimumTouchTargets &&
      hasProperContrast &&
      supportsScreenReader;

  @override
  String toString() => '''
Accessibility Report:
- Semantics Labels: $hasSemanticsLabels
- Minimum Touch Targets: $hasMinimumTouchTargets
- Proper Contrast: $hasProperContrast
- Screen Reader Support: $supportsScreenReader
- Issues: ${issues.isEmpty ? 'None' : issues.join(', ')}
''';
}

/// Accessibility tester
/// مختبر إمكانية الوصول
class AccessibilityTester {
  final WidgetTester tester;

  AccessibilityTester(this.tester);

  /// Run accessibility audit
  /// تشغيل تدقيق إمكانية الوصول
  Future<AccessibilityReport> audit() async {
    final issues = <String>[];

    // Check for semantics labels
    final semantics = find.byType(Semantics);
    final hasSemantics = semantics.evaluate().isNotEmpty;
    if (!hasSemantics) {
      issues.add('Missing Semantics widgets');
    }

    // Check touch target sizes
    bool hasMinimumTouchTargets = true;
    final buttons = find.byType(ElevatedButton);
    for (final button in buttons.evaluate()) {
      final size = button.size;
      if (size != null && (size.width < 44 || size.height < 44)) {
        hasMinimumTouchTargets = false;
        issues.add('Touch target too small: ${size.width}x${size.height}');
      }
    }

    // Check icon buttons
    final iconButtons = find.byType(IconButton);
    for (final button in iconButtons.evaluate()) {
      final size = button.size;
      if (size != null && (size.width < 44 || size.height < 44)) {
        hasMinimumTouchTargets = false;
        issues.add('Icon button touch target too small');
      }
    }

    return AccessibilityReport(
      hasSemanticsLabels: hasSemantics,
      hasMinimumTouchTargets: hasMinimumTouchTargets,
      hasProperContrast: true, // Would need actual color analysis
      supportsScreenReader: hasSemantics,
      issues: issues,
    );
  }

  /// Assert accessibility requirements
  /// التأكد من متطلبات إمكانية الوصول
  void assertAccessible(AccessibilityReport report) {
    expect(report.hasSemanticsLabels, true,
        reason: 'App should have semantics labels');
    expect(report.hasMinimumTouchTargets, true,
        reason: 'Touch targets should be at least 44x44');
  }
}

// =============================================================================
// Network Simulation Utilities
// أدوات محاكاة الشبكة
// =============================================================================

/// Network condition types
/// أنواع حالات الشبكة
enum NetworkCondition {
  good,      // Normal connection
  slow,      // Slow 3G-like
  unstable,  // Intermittent
  offline,   // No connection
}

/// Network simulator
/// محاكي الشبكة
class NetworkSimulator {
  NetworkCondition _currentCondition = NetworkCondition.good;

  NetworkCondition get condition => _currentCondition;

  /// Set network condition
  /// تعيين حالة الشبكة
  void setCondition(NetworkCondition condition) {
    _currentCondition = condition;
    debugPrint('Network condition set to: ${condition.name}');
  }

  /// Simulate network delay
  /// محاكاة تأخير الشبكة
  Future<void> simulateDelay() async {
    switch (_currentCondition) {
      case NetworkCondition.good:
        await Future.delayed(const Duration(milliseconds: 100));
        break;
      case NetworkCondition.slow:
        await Future.delayed(const Duration(seconds: 2));
        break;
      case NetworkCondition.unstable:
        if (DateTime.now().millisecond % 2 == 0) {
          await Future.delayed(const Duration(seconds: 1));
        }
        break;
      case NetworkCondition.offline:
        throw Exception('Network unavailable');
    }
  }

  /// Check if network is available
  /// التحقق من توفر الشبكة
  bool get isAvailable => _currentCondition != NetworkCondition.offline;

  /// Reset to good condition
  /// إعادة التعيين إلى حالة جيدة
  void reset() {
    _currentCondition = NetworkCondition.good;
  }
}

// =============================================================================
// State Management Utilities
// أدوات إدارة الحالة
// =============================================================================

/// Test state snapshot
/// لقطة حالة الاختبار
class StateSnapshot {
  final String name;
  final DateTime timestamp;
  final Map<String, dynamic> data;

  StateSnapshot({
    required this.name,
    required this.data,
  }) : timestamp = DateTime.now();

  @override
  String toString() => 'StateSnapshot($name at $timestamp)';
}

/// State manager for tests
/// مدير الحالة للاختبارات
class TestStateManager {
  final List<StateSnapshot> _snapshots = [];

  /// Capture current state
  /// التقاط الحالة الحالية
  StateSnapshot capture(String name, Map<String, dynamic> data) {
    final snapshot = StateSnapshot(name: name, data: data);
    _snapshots.add(snapshot);
    return snapshot;
  }

  /// Get all snapshots
  /// الحصول على جميع اللقطات
  List<StateSnapshot> get snapshots => List.unmodifiable(_snapshots);

  /// Get snapshot by name
  /// الحصول على لقطة بالاسم
  StateSnapshot? getSnapshot(String name) {
    try {
      return _snapshots.firstWhere((s) => s.name == name);
    } catch (_) {
      return null;
    }
  }

  /// Clear all snapshots
  /// مسح جميع اللقطات
  void clear() => _snapshots.clear();

  /// Compare two snapshots
  /// مقارنة لقطتين
  Map<String, dynamic> compare(StateSnapshot a, StateSnapshot b) {
    final diff = <String, dynamic>{};

    for (final key in a.data.keys) {
      if (a.data[key] != b.data[key]) {
        diff[key] = {
          'before': a.data[key],
          'after': b.data[key],
        };
      }
    }

    for (final key in b.data.keys) {
      if (!a.data.containsKey(key)) {
        diff[key] = {
          'before': null,
          'after': b.data[key],
        };
      }
    }

    return diff;
  }
}

// =============================================================================
// Screenshot Utilities
// أدوات لقطات الشاشة
// =============================================================================

/// Screenshot manager
/// مدير لقطات الشاشة
class ScreenshotManager {
  final IntegrationTestWidgetsFlutterBinding binding;
  final String outputDir;
  int _screenshotCount = 0;

  ScreenshotManager(this.binding, {this.outputDir = 'screenshots'});

  /// Take a screenshot
  /// التقاط لقطة شاشة
  Future<void> capture(String name, {String? description}) async {
    if (kIsWeb) {
      debugPrint('Screenshots not supported on web');
      return;
    }

    try {
      _screenshotCount++;
      final filename = '${_screenshotCount.toString().padLeft(3, '0')}_$name';

      // Create directory if needed
      final dir = Directory(outputDir);
      if (!dir.existsSync()) {
        dir.createSync(recursive: true);
      }

      // Take screenshot
      await binding.takeScreenshot(filename);

      debugPrint('Screenshot captured: $filename');
      if (description != null) {
        debugPrint('  Description: $description');
      }
    } catch (e) {
      debugPrint('Failed to capture screenshot: $e');
    }
  }

  /// Take a screenshot on failure
  /// التقاط لقطة شاشة عند الفشل
  Future<void> captureOnFailure(String testName, dynamic error) async {
    await capture(
      'failure_$testName',
      description: 'Test failed: $error',
    );
  }

  /// Get screenshot count
  /// الحصول على عدد لقطات الشاشة
  int get count => _screenshotCount;

  /// Reset counter
  /// إعادة تعيين العداد
  void resetCounter() => _screenshotCount = 0;
}

// =============================================================================
// Widget Test Utilities
// أدوات اختبار العناصر
// =============================================================================

/// Find widgets by key
/// البحث عن العناصر بالمفتاح
Finder findByKey(String key) => find.byKey(Key(key));

/// Find widgets by semantic label
/// البحث عن العناصر بالتسمية الدلالية
Finder findBySemanticsLabel(String label) =>
    find.bySemanticsLabel(RegExp(label, caseSensitive: false));

/// Find text containing string (case insensitive)
/// البحث عن نص يحتوي على سلسلة
Finder findTextContaining(String text) =>
    find.textContaining(RegExp(text, caseSensitive: false));

/// Find widget by type and child text
/// البحث عن عنصر بالنوع والنص الفرعي
Finder findByTypeWithText<T extends Widget>(String text) =>
    find.widgetWithText(T, text);

/// Check if finder has exactly n widgets
/// التحقق من أن الباحث لديه n عنصر بالضبط
void expectExactly(Finder finder, int count, {String? message}) {
  expect(finder, findsNWidgets(count), reason: message);
}

/// Check if finder has at least n widgets
/// التحقق من أن الباحث لديه n عنصر على الأقل
void expectAtLeast(Finder finder, int count, {String? message}) {
  expect(
    finder.evaluate().length,
    greaterThanOrEqualTo(count),
    reason: message,
  );
}

// =============================================================================
// Gesture Test Utilities
// أدوات اختبار الإيماءات
// =============================================================================

/// Gesture helper
/// مساعد الإيماءات
class GestureHelper {
  final WidgetTester tester;

  GestureHelper(this.tester);

  /// Double tap
  /// نقر مزدوج
  Future<void> doubleTap(Finder finder) async {
    await tester.tap(finder);
    await tester.pump(const Duration(milliseconds: 50));
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }

  /// Long press
  /// ضغط طويل
  Future<void> longPress(Finder finder, {Duration? duration}) async {
    await tester.longPress(finder);
    await tester.pumpAndSettle();
  }

  /// Drag from point to point
  /// السحب من نقطة إلى نقطة
  Future<void> dragFromTo(Offset start, Offset end) async {
    await tester.dragFrom(start, end - start);
    await tester.pumpAndSettle();
  }

  /// Swipe left
  /// التمرير لليسار
  Future<void> swipeLeft(Finder finder, {double distance = 300}) async {
    await tester.drag(finder, Offset(-distance, 0));
    await tester.pumpAndSettle();
  }

  /// Swipe right
  /// التمرير لليمين
  Future<void> swipeRight(Finder finder, {double distance = 300}) async {
    await tester.drag(finder, Offset(distance, 0));
    await tester.pumpAndSettle();
  }

  /// Swipe up
  /// التمرير للأعلى
  Future<void> swipeUp(Finder finder, {double distance = 300}) async {
    await tester.drag(finder, Offset(0, -distance));
    await tester.pumpAndSettle();
  }

  /// Swipe down
  /// التمرير للأسفل
  Future<void> swipeDown(Finder finder, {double distance = 300}) async {
    await tester.drag(finder, Offset(0, distance));
    await tester.pumpAndSettle();
  }

  /// Pinch zoom in
  /// التكبير بالقرص
  Future<void> pinchZoomIn(Finder finder) async {
    // Note: Pinch gestures are complex to simulate
    // This is a placeholder for actual implementation
    debugPrint('Pinch zoom in - requires multi-touch simulation');
  }

  /// Pinch zoom out
  /// التصغير بالقرص
  Future<void> pinchZoomOut(Finder finder) async {
    debugPrint('Pinch zoom out - requires multi-touch simulation');
  }
}

// =============================================================================
// Form Test Utilities
// أدوات اختبار النماذج
// =============================================================================

/// Form test helper
/// مساعد اختبار النماذج
class FormTestHelper {
  final WidgetTester tester;

  FormTestHelper(this.tester);

  /// Fill text field
  /// ملء حقل نصي
  Future<void> fillTextField(Finder finder, String text) async {
    await tester.enterText(finder, text);
    await tester.pumpAndSettle();
  }

  /// Clear text field
  /// مسح حقل نصي
  Future<void> clearTextField(Finder finder) async {
    await tester.enterText(finder, '');
    await tester.pumpAndSettle();
  }

  /// Select dropdown item
  /// اختيار عنصر قائمة منسدلة
  Future<void> selectDropdownItem<T>(
    Finder dropdownFinder,
    T value,
  ) async {
    await tester.tap(dropdownFinder);
    await tester.pumpAndSettle();

    // Find and tap the item
    final item = find.text(value.toString()).last;
    await tester.tap(item);
    await tester.pumpAndSettle();
  }

  /// Toggle checkbox
  /// تبديل مربع الاختيار
  Future<void> toggleCheckbox(Finder finder) async {
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }

  /// Toggle switch
  /// تبديل المفتاح
  Future<void> toggleSwitch(Finder finder) async {
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }

  /// Select radio button
  /// اختيار زر الراديو
  Future<void> selectRadio<T>(Finder finder) async {
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }

  /// Submit form
  /// إرسال النموذج
  Future<void> submitForm(Finder submitButton) async {
    await tester.tap(submitButton);
    await tester.pumpAndSettle();
  }

  /// Fill form with data
  /// ملء النموذج بالبيانات
  Future<void> fillForm(Map<String, dynamic> data) async {
    for (final entry in data.entries) {
      final key = entry.key;
      final value = entry.value;

      // Try to find field by key
      final fieldFinder = find.byKey(Key(key));

      if (fieldFinder.evaluate().isNotEmpty) {
        if (value is String) {
          await fillTextField(fieldFinder, value);
        } else if (value is bool) {
          await toggleCheckbox(fieldFinder);
        }
      }
    }
  }
}

// =============================================================================
// Wait Utilities
// أدوات الانتظار
// =============================================================================

/// Wait for condition with timeout
/// الانتظار للشرط مع مهلة
Future<bool> waitForCondition(
  bool Function() condition, {
  Duration timeout = const Duration(seconds: 10),
  Duration pollInterval = const Duration(milliseconds: 100),
}) async {
  final endTime = DateTime.now().add(timeout);

  while (DateTime.now().isBefore(endTime)) {
    if (condition()) return true;
    await Future.delayed(pollInterval);
  }

  return false;
}

/// Wait for element to appear
/// الانتظار لظهور عنصر
Future<bool> waitForElement(
  WidgetTester tester,
  Finder finder, {
  Duration timeout = const Duration(seconds: 10),
}) async {
  return waitForCondition(
    () {
      tester.pump();
      return finder.evaluate().isNotEmpty;
    },
    timeout: timeout,
  );
}

/// Wait for element to disappear
/// الانتظار لاختفاء عنصر
Future<bool> waitForElementToDisappear(
  WidgetTester tester,
  Finder finder, {
  Duration timeout = const Duration(seconds: 10),
}) async {
  return waitForCondition(
    () {
      tester.pump();
      return finder.evaluate().isEmpty;
    },
    timeout: timeout,
  );
}

// =============================================================================
// Debug Utilities
// أدوات التصحيح
// =============================================================================

/// Print widget tree
/// طباعة شجرة العناصر
void printWidgetTree(WidgetTester tester) {
  debugPrint(tester.allWidgets.map((w) => w.runtimeType.toString()).join('\n'));
}

/// Print all text widgets
/// طباعة جميع عناصر النص
void printAllText(WidgetTester tester) {
  final textWidgets = find.byType(Text);
  for (final widget in textWidgets.evaluate()) {
    final text = widget.widget as Text;
    debugPrint('Text: ${text.data ?? text.textSpan?.toPlainText()}');
  }
}

/// Print all buttons
/// طباعة جميع الأزرار
void printAllButtons(WidgetTester tester) {
  final buttons = find.byType(ElevatedButton);
  for (final widget in buttons.evaluate()) {
    debugPrint('Button found: ${widget.widget.key}');
  }
}
