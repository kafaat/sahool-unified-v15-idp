import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Widget Testing Helpers for SAHOOL Field App
/// مساعدات اختبار الواجهات

/// Pump widget with multiple frames
Future<void> pumpWidgetWithFrames(
  WidgetTester tester,
  Widget widget, {
  int frames = 3,
  Duration duration = const Duration(milliseconds: 16),
}) async {
  await tester.pumpWidget(widget);
  for (int i = 0; i < frames; i++) {
    await tester.pump(duration);
  }
}

/// Tap button by key and wait
Future<void> tapButtonByKey(
  WidgetTester tester,
  Key key, {
  bool settle = true,
}) async {
  final finder = find.byKey(key);
  expect(finder, findsOneWidget);
  await tester.tap(finder);
  if (settle) {
    await tester.pumpAndSettle();
  } else {
    await tester.pump();
  }
}

/// Tap button by text and wait
Future<void> tapButtonByText(
  WidgetTester tester,
  String text, {
  bool settle = true,
}) async {
  final finder = find.text(text);
  expect(finder, findsOneWidget);
  await tester.tap(finder);
  if (settle) {
    await tester.pumpAndSettle();
  } else {
    await tester.pump();
  }
}

/// Enter text in field by key
Future<void> enterTextByKey(
  WidgetTester tester,
  Key key,
  String text, {
  bool settle = true,
}) async {
  final finder = find.byKey(key);
  expect(finder, findsOneWidget);
  await tester.enterText(finder, text);
  if (settle) {
    await tester.pumpAndSettle();
  } else {
    await tester.pump();
  }
}

/// Scroll widget into view
Future<void> scrollIntoView(
  WidgetTester tester,
  Finder target, {
  Finder? scrollable,
  double delta = 100.0,
  int maxScrolls = 10,
}) async {
  scrollable ??= find.byType(Scrollable).first;

  for (int i = 0; i < maxScrolls && target.evaluate().isEmpty; i++) {
    await tester.drag(scrollable, Offset(0, -delta));
    await tester.pump();
  }

  expect(target, findsOneWidget, reason: 'Widget not found after scrolling');
}

/// Verify widget exists
void expectWidgetExists(Finder finder, {String? reason}) {
  expect(finder, findsOneWidget, reason: reason);
}

/// Verify widget does not exist
void expectWidgetDoesNotExist(Finder finder, {String? reason}) {
  expect(finder, findsNothing, reason: reason);
}

/// Verify multiple widgets exist
void expectWidgetsExist(Finder finder, int count, {String? reason}) {
  expect(finder, findsNWidgets(count), reason: reason);
}

/// Wait for widget to appear
Future<void> waitForWidget(
  WidgetTester tester,
  Finder finder, {
  Duration timeout = const Duration(seconds: 5),
  Duration checkInterval = const Duration(milliseconds: 100),
}) async {
  final endTime = DateTime.now().add(timeout);

  while (DateTime.now().isBefore(endTime)) {
    await tester.pump(checkInterval);
    if (finder.evaluate().isNotEmpty) {
      return;
    }
  }

  throw TimeoutException(
    'Widget not found within ${timeout.inSeconds} seconds',
  );
}

/// Wait for widget to disappear
Future<void> waitForWidgetToDisappear(
  WidgetTester tester,
  Finder finder, {
  Duration timeout = const Duration(seconds: 5),
  Duration checkInterval = const Duration(milliseconds: 100),
}) async {
  final endTime = DateTime.now().add(timeout);

  while (DateTime.now().isBefore(endTime)) {
    await tester.pump(checkInterval);
    if (finder.evaluate().isEmpty) {
      return;
    }
  }

  throw TimeoutException(
    'Widget still visible after ${timeout.inSeconds} seconds',
  );
}

/// Verify loading indicator
void expectLoadingIndicator({bool shouldExist = true}) {
  final finder = find.byType(CircularProgressIndicator);
  if (shouldExist) {
    expect(finder, findsAtLeastNWidgets(1));
  } else {
    expect(finder, findsNothing);
  }
}

/// Verify error message
void expectErrorMessage(String message) {
  expect(find.text(message), findsOneWidget);
}

/// Create testable widget with Riverpod providers
Widget createTestWidget({
  required Widget child,
  List<Override> overrides = const [],
  ThemeData? theme,
  Locale locale = const Locale('ar'),
}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(
      theme: theme ??
          ThemeData(
            useMaterial3: true,
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFF1B5E20),
            ),
          ),
      locale: locale,
      home: Directionality(
        textDirection: locale.languageCode == 'ar'
            ? TextDirection.rtl
            : TextDirection.ltr,
        child: Scaffold(
          body: child,
        ),
      ),
    ),
  );
}

/// Pump widget and wait for animations
Future<void> pumpAndWait(
  WidgetTester tester,
  Widget widget, {
  Duration duration = const Duration(milliseconds: 500),
}) async {
  await tester.pumpWidget(widget);
  await tester.pump(duration);
  await tester.pumpAndSettle();
}

/// Extension for WidgetTester with common operations
extension WidgetTesterHelpers on WidgetTester {
  /// Find widget by type and key
  Finder findByTypeAndKey<T extends Widget>(Key key) {
    return find.byWidgetPredicate(
      (widget) => widget is T && widget.key == key,
    );
  }

  /// Verify text exists anywhere in the widget tree
  void expectText(String text, {int count = 1}) {
    expect(find.text(text), findsNWidgets(count));
  }

  /// Verify text contains pattern
  void expectTextContains(String pattern) {
    expect(
      find.byWidgetPredicate(
        (widget) =>
            widget is Text &&
            widget.data != null &&
            widget.data!.contains(pattern),
      ),
      findsOneWidget,
    );
  }

  /// Verify widget is enabled
  void expectEnabled(Finder finder) {
    final widget = this.widget(finder);
    if (widget is ElevatedButton) {
      expect(widget.onPressed, isNotNull);
    } else if (widget is TextButton) {
      expect(widget.onPressed, isNotNull);
    } else if (widget is IconButton) {
      expect(widget.onPressed, isNotNull);
    }
  }

  /// Verify widget is disabled
  void expectDisabled(Finder finder) {
    final widget = this.widget(finder);
    if (widget is ElevatedButton) {
      expect(widget.onPressed, isNull);
    } else if (widget is TextButton) {
      expect(widget.onPressed, isNull);
    } else if (widget is IconButton) {
      expect(widget.onPressed, isNull);
    }
  }

  /// Tap and wait for async operations
  Future<void> tapAndWaitAsync(Finder finder) async {
    await tap(finder);
    await pump();
    await pump(const Duration(milliseconds: 100));
    await pumpAndSettle();
  }

  /// Scroll to bottom of scrollable
  Future<void> scrollToBottom(Finder scrollable) async {
    final scrollableWidget = widget<Scrollable>(scrollable);
    final position = scrollableWidget.controller?.position;
    if (position != null) {
      scrollableWidget.controller?.jumpTo(position.maxScrollExtent);
      await pumpAndSettle();
    }
  }

  /// Scroll to top of scrollable
  Future<void> scrollToTop(Finder scrollable) async {
    final scrollableWidget = widget<Scrollable>(scrollable);
    final position = scrollableWidget.controller?.position;
    if (position != null) {
      scrollableWidget.controller?.jumpTo(position.minScrollExtent);
      await pumpAndSettle();
    }
  }
}

/// Timeout exception for widget testing
class TimeoutException implements Exception {
  final String message;

  TimeoutException(this.message);

  @override
  String toString() => 'TimeoutException: $message';
}

/// Golden test helpers
class GoldenTestHelpers {
  /// Standard phone size (iPhone 13)
  static const Size phoneSize = Size(390, 844);

  /// Standard tablet size (iPad)
  static const Size tabletSize = Size(768, 1024);

  /// Setup for golden tests
  static Future<void> setup(WidgetTester tester, {Size? size}) async {
    final testSize = size ?? phoneSize;
    tester.view.physicalSize = testSize;
    tester.view.devicePixelRatio = 1.0;
  }

  /// Compare with golden file
  static Future<void> expectGolden(
    WidgetTester tester,
    String fileName, {
    Finder? finder,
  }) async {
    await tester.pumpAndSettle();
    await expectLater(
      finder ?? find.byType(MaterialApp),
      matchesGoldenFile('goldens/$fileName.png'),
    );
  }
}
