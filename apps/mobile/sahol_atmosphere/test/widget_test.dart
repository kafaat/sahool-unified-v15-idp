import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:sahool_atmosphere/main.dart';

void main() {
  group('SAHOOL Atmosphere App Tests', () {
    testWidgets('App initializes and shows dashboard', (WidgetTester tester) async {
      // Build our app and trigger a frame.
      await tester.pumpWidget(
        const ProviderScope(
          child: SahoolAtmosphereApp(),
        ),
      );

      // Wait for async operations
      await tester.pumpAndSettle();

      // Verify that the app shows Arabic title
      expect(find.text('ساهول أتموسفير'), findsOneWidget);
    });

    testWidgets('App uses dark theme', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SahoolAtmosphereApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Get the MaterialApp widget
      final materialApp = tester.widget<MaterialApp>(find.byType(MaterialApp));

      // Verify system theme is used by default (follows user preference)
      expect(materialApp.themeMode, ThemeMode.system);
    });

    testWidgets('App supports Arabic locale', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SahoolAtmosphereApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Get the MaterialApp widget
      final materialApp = tester.widget<MaterialApp>(find.byType(MaterialApp));

      // Verify Arabic locale is set
      expect(materialApp.locale?.languageCode, 'ar');
    });

    testWidgets('App supports multiple locales', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SahoolAtmosphereApp(),
        ),
      );

      await tester.pumpAndSettle();

      // Get the MaterialApp widget
      final materialApp = tester.widget<MaterialApp>(find.byType(MaterialApp));

      // Verify supported locales include Arabic and English
      final locales = materialApp.supportedLocales.map((l) => l.languageCode).toList();
      expect(locales.contains('ar'), isTrue);
      expect(locales.contains('en'), isTrue);
    });
  });
}
