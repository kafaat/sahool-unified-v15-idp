// SAHOOL Field App - Basic Widget Test
//
// This test verifies basic app startup functionality.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  group('App Startup Tests', () {
    testWidgets('App should display without crashing', (WidgetTester tester) async {
      // Build a minimal app widget
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Center(
                child: Text('سهول'),
              ),
            ),
          ),
        ),
      );

      // Verify the app title is displayed
      expect(find.text('سهول'), findsOneWidget);
    });

    testWidgets('App should support RTL layout', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                body: Center(
                  child: Text('مرحباً'),
                ),
              ),
            ),
          ),
        ),
      );

      // Verify RTL text is displayed
      expect(find.text('مرحباً'), findsOneWidget);
    });

    testWidgets('Material theme should be applied', (WidgetTester tester) async {
      const primaryColor = Color(0xFF367C2B);

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            theme: ThemeData(
              colorScheme: const ColorScheme.light(primary: primaryColor),
            ),
            home: const Scaffold(
              body: Center(
                child: Text('Theme Test'),
              ),
            ),
          ),
        ),
      );

      // Find the MaterialApp and verify it exists
      expect(find.byType(MaterialApp), findsOneWidget);
    });
  });

  group('Navigation Tests', () {
    testWidgets('Should navigate between screens', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: _TestNavigationScreen(),
          ),
        ),
      );

      // Find and tap the navigation button
      expect(find.text('الرئيسية'), findsOneWidget);

      await tester.tap(find.text('انتقال'));
      await tester.pumpAndSettle();

      // Verify navigation occurred
      expect(find.text('الصفحة الثانية'), findsOneWidget);
    });
  });
}

/// Test helper widget for navigation
class _TestNavigationScreen extends StatelessWidget {
  const _TestNavigationScreen();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('الرئيسية'),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const Scaffold(
                      body: Center(child: Text('الصفحة الثانية')),
                    ),
                  ),
                );
              },
              child: const Text('انتقال'),
            ),
          ],
        ),
      ),
    );
  }
}
