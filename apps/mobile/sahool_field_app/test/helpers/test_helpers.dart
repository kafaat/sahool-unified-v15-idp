import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

/// Test Helpers for SAHOOL Field App
/// مساعدات الاختبار لتطبيق SAHOOL

/// Creates a testable widget with all required providers and configurations
Widget createTestableWidget({
  required Widget child,
  List<Override> overrides = const [],
  Locale locale = const Locale('ar'),
}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(
      debugShowCheckedModeBanner: false,
      locale: locale,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('ar'),
        Locale('en'),
      ],
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1B5E20),
        ),
      ),
      home: Directionality(
        textDirection: TextDirection.rtl,
        child: child,
      ),
    ),
  );
}

/// Creates a simple testable widget without providers
Widget createSimpleTestableWidget(Widget child) {
  return MaterialApp(
    home: Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(body: child),
    ),
  );
}

/// Pump widget and settle all animations
Future<void> pumpAndSettle(WidgetTester tester, Widget widget) async {
  await tester.pumpWidget(widget);
  await tester.pumpAndSettle();
}

/// Wait for async operations
Future<void> waitForAsync(WidgetTester tester) async {
  await tester.pump(const Duration(milliseconds: 100));
  await tester.pumpAndSettle();
}

/// Extension for common test operations
extension WidgetTesterExtensions on WidgetTester {
  /// Tap and wait for animations
  Future<void> tapAndSettle(Finder finder) async {
    await tap(finder);
    await this.pumpAndSettle();
  }

  /// Enter text and wait
  Future<void> enterTextAndSettle(Finder finder, String text) async {
    await enterText(finder, text);
    await this.pumpAndSettle();
  }

  /// Scroll until visible
  Future<void> scrollUntilVisible(
    Finder finder,
    Finder scrollable, {
    double delta = 100,
  }) async {
    while (finder.evaluate().isEmpty) {
      await drag(scrollable, Offset(0, -delta));
      await pump();
    }
  }
}

/// Golden test configuration
class GoldenTestConfig {
  static const double defaultWidth = 390.0;
  static const double defaultHeight = 844.0;

  static Future<void> setupGoldenTest(WidgetTester tester) async {
    tester.view.physicalSize = const Size(defaultWidth, defaultHeight);
    tester.view.devicePixelRatio = 1.0;
  }
}

/// Test data generators
class TestDataGenerator {
  static String generateUuid() {
    return 'test-uuid-${DateTime.now().millisecondsSinceEpoch}';
  }

  static DateTime generateDate({int daysFromNow = 0}) {
    return DateTime.now().add(Duration(days: daysFromNow));
  }

  static Map<String, dynamic> generateFieldJson({
    String? id,
    String? name,
    double? area,
  }) {
    return {
      'id': id ?? generateUuid(),
      'name': name ?? 'حقل اختباري',
      'area': area ?? 100.0,
      'tenant_id': 'tenant_1',
      'created_at': DateTime.now().toIso8601String(),
    };
  }

  static Map<String, dynamic> generateTaskJson({
    String? id,
    String? title,
    String? status,
  }) {
    return {
      'id': id ?? generateUuid(),
      'title': title ?? 'مهمة اختبارية',
      'status': status ?? 'pending',
      'tenant_id': 'tenant_1',
      'created_at': DateTime.now().toIso8601String(),
    };
  }
}
