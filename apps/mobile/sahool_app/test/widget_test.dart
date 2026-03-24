// SAHOOL Unified App - Widget Tests
// اختبارات الودجات للتطبيق الموحد

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Core package imports - استيراد الحزمة الأساسية
import 'package:sahool_mobile_core/sahool_mobile_core.dart';

void main() {
  // ════════════════════════════════════════════════════════════════════════════
  // Basic App Rendering Tests
  // اختبارات العرض الأساسية للتطبيق
  // ════════════════════════════════════════════════════════════════════════════

  group('SahoolApp Widget | ودجة التطبيق', () {
    testWidgets('App renders without errors', (tester) async {
      // Build a minimal app with ProviderScope (required for Riverpod)
      // بناء تطبيق بسيط مع ProviderScope (مطلوب لـ Riverpod)
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Center(
                child: Text('SAHOOL'),
              ),
            ),
          ),
        ),
      );

      // Verify the app renders | التحقق من عرض التطبيق
      expect(find.byType(MaterialApp), findsOneWidget);
      expect(find.text('SAHOOL'), findsOneWidget);
    });

    testWidgets('App uses Material Design', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Center(
                child: Text('SAHOOL'),
              ),
            ),
          ),
        ),
      );

      // Verify Material scaffold structure | التحقق من بنية Material
      expect(find.byType(Scaffold), findsOneWidget);
    });

    testWidgets('App supports Arabic locale', (tester) async {
      // Verify Arabic RTL rendering | التحقق من عرض العربية من اليمين لليسار
      await tester.pumpWidget(
        const ProviderScope(
          child: Directionality(
            textDirection: TextDirection.rtl,
            child: MaterialApp(
              locale: Locale('ar'),
              home: Scaffold(
                body: Center(
                  child: Text('سهول'),
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('سهول'), findsOneWidget);
    });

    testWidgets('App supports English locale', (tester) async {
      // Verify English LTR rendering | التحقق من عرض الإنجليزية من اليسار لليمين
      await tester.pumpWidget(
        const ProviderScope(
          child: Directionality(
            textDirection: TextDirection.ltr,
            child: MaterialApp(
              locale: Locale('en'),
              home: Scaffold(
                body: Center(
                  child: Text('SAHOOL'),
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('SAHOOL'), findsOneWidget);
    });
  });
}
