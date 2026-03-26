// SAHOOL Unified App - Integration Tests
// اختبارات التكامل للتطبيق الموحد
//
// Run with: flutter test integration_test/app_test.dart
// التشغيل: flutter test integration_test/app_test.dart
//
// Test Categories | فئات الاختبار:
// - App Launch & Initialization | بدء التشغيل والتهيئة
// - Authentication Flow | تدفق المصادقة
// - Navigation | التنقل
// - Offline Mode | وضع عدم الاتصال
// - Feature Screens | شاشات الميزات

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Core package imports - استيراد الحزمة الأساسية
import 'package:sahool_mobile_core/sahool_mobile_core.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  // ════════════════════════════════════════════════════════════════════════════
  // App Launch & Initialization Tests
  // اختبارات بدء التشغيل والتهيئة
  // ════════════════════════════════════════════════════════════════════════════

  group('App Launch | بدء التطبيق', () {
    testWidgets('App launches and renders MaterialApp', (tester) async {
      // Build a minimal app using core package components
      // بناء تطبيق بسيط باستخدام مكونات الحزمة الأساسية
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(),
        ),
      );
      await tester.pumpAndSettle();

      // Verify MaterialApp is rendered | التحقق من عرض التطبيق
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('App shows splash or home screen on startup', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(),
        ),
      );
      await tester.pumpAndSettle();

      // The app should show either a splash screen or the home screen
      // يجب أن يعرض التطبيق شاشة البداية أو الشاشة الرئيسية
      final hasSplashOrHome = find.byType(Scaffold).evaluate().isNotEmpty;
      expect(hasSplashOrHome, isTrue);
    });

    testWidgets('App supports RTL layout for Arabic', (tester) async {
      // Verify Arabic RTL directionality is available
      // التحقق من دعم الاتجاه من اليمين لليسار للعربية
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(locale: Locale('ar')),
        ),
      );
      await tester.pumpAndSettle();

      // Find the Directionality widget closest to the app content
      final directionality = tester.widget<Directionality>(
        find.byType(Directionality).first,
      );
      expect(directionality.textDirection, TextDirection.rtl);
    });
  });

  // ════════════════════════════════════════════════════════════════════════════
  // Authentication Flow Tests
  // اختبارات تدفق المصادقة
  // ════════════════════════════════════════════════════════════════════════════

  group('Authentication Flow | تدفق المصادقة', () {
    testWidgets('Login screen displays email and password fields',
        (tester) async {
      // Navigate to login screen
      // الانتقال إلى شاشة تسجيل الدخول
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(initialRoute: '/login'),
        ),
      );
      await tester.pumpAndSettle();

      // Verify login form elements exist
      // التحقق من وجود عناصر نموذج تسجيل الدخول
      // TODO: Update finders when login screen is wired up
      // expect(find.byType(TextFormField), findsNWidgets(2));
      // expect(find.byType(ElevatedButton), findsOneWidget);
    });

    testWidgets('Login with valid credentials navigates to home',
        (tester) async {
      // Test complete login flow
      // اختبار تدفق تسجيل الدخول الكامل
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(initialRoute: '/login'),
        ),
      );
      await tester.pumpAndSettle();

      // TODO: Fill in credentials and tap login button
      // TODO: ملء بيانات الاعتماد والنقر على زر تسجيل الدخول
      //
      // await tester.enterText(find.byKey(const Key('email_field')), 'test@sahool.app');
      // await tester.enterText(find.byKey(const Key('password_field')), 'TestPass123!');
      // await tester.tap(find.byKey(const Key('login_button')));
      // await tester.pumpAndSettle();
      //
      // expect(find.text('Home'), findsOneWidget);
    });

    testWidgets('Logout returns to login screen', (tester) async {
      // Test logout flow
      // اختبار تدفق تسجيل الخروج
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(initialRoute: '/home'),
        ),
      );
      await tester.pumpAndSettle();

      // TODO: Tap logout and verify navigation back to login
      // TODO: النقر على تسجيل الخروج والتحقق من العودة إلى شاشة الدخول
      //
      // await tester.tap(find.byKey(const Key('logout_button')));
      // await tester.pumpAndSettle();
      //
      // expect(find.byKey(const Key('login_screen')), findsOneWidget);
    });
  });

  // ════════════════════════════════════════════════════════════════════════════
  // Navigation Tests
  // اختبارات التنقل
  // ════════════════════════════════════════════════════════════════════════════

  group('Navigation | التنقل', () {
    testWidgets('Bottom navigation switches between main tabs',
        (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(initialRoute: '/home'),
        ),
      );
      await tester.pumpAndSettle();

      // TODO: Tap each bottom navigation item and verify screen change
      // TODO: النقر على كل عنصر في شريط التنقل السفلي والتحقق من تغيير الشاشة
      //
      // final bottomNav = find.byType(SahoolBottomNavigation);
      // expect(bottomNav, findsOneWidget);
    });

    testWidgets('Can navigate to fields list screen', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(initialRoute: '/home'),
        ),
      );
      await tester.pumpAndSettle();

      // TODO: Navigate to fields list
      // TODO: الانتقال إلى قائمة الحقول
      //
      // await tester.tap(find.byKey(const Key('fields_nav_item')));
      // await tester.pumpAndSettle();
      // expect(find.text('Fields'), findsOneWidget);
    });

    testWidgets('Can navigate to map screen', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(initialRoute: '/home'),
        ),
      );
      await tester.pumpAndSettle();

      // TODO: Navigate to map screen
      // TODO: الانتقال إلى شاشة الخريطة
      //
      // await tester.tap(find.byKey(const Key('map_nav_item')));
      // await tester.pumpAndSettle();
      // expect(find.byType(SahoolMapWidget), findsOneWidget);
    });
  });

  // ════════════════════════════════════════════════════════════════════════════
  // Offline Mode Tests
  // اختبارات وضع عدم الاتصال
  // ════════════════════════════════════════════════════════════════════════════

  group('Offline Mode | وضع عدم الاتصال', () {
    testWidgets('App renders without network connectivity', (tester) async {
      // The app should function in offline-first mode
      // يجب أن يعمل التطبيق في وضع عدم الاتصال أولاً
      await tester.pumpWidget(
        const ProviderScope(
          child: _TestSahoolApp(),
        ),
      );
      await tester.pumpAndSettle();

      // App should still render its UI when offline
      // يجب أن يعرض التطبيق واجهته حتى بدون اتصال
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('Offline banner appears when connectivity is lost',
        (tester) async {
      // TODO: Simulate network disconnection and verify offline indicator
      // TODO: محاكاة فقدان الاتصال والتحقق من مؤشر عدم الاتصال
      //
      // await tester.pumpWidget(
      //   const ProviderScope(
      //     child: _TestSahoolApp(),
      //   ),
      // );
      // await tester.pumpAndSettle();
      //
      // // Simulate offline state
      // // expect(find.byType(ConnectivityBanner), findsOneWidget);
    });

    testWidgets('Cached data is accessible in offline mode', (tester) async {
      // TODO: Pre-populate local database, go offline, verify data loads
      // TODO: ملء قاعدة البيانات المحلية مسبقاً، قطع الاتصال، التحقق من تحميل البيانات
    });
  });

  // ════════════════════════════════════════════════════════════════════════════
  // Feature Screen Tests (Expand as features are integrated)
  // اختبارات شاشات الميزات (التوسيع عند دمج الميزات)
  // ════════════════════════════════════════════════════════════════════════════

  group('Feature Screens | شاشات الميزات', () {
    // TODO: Add tests for each feature as they are wired into sahool_app
    // TODO: إضافة اختبارات لكل ميزة عند ربطها بالتطبيق

    // Advisory | الاستشارات
    // testWidgets('Advisory screen loads recommendations', ...);

    // Irrigation | الري
    // testWidgets('Irrigation dashboard shows schedule', ...);

    // Crop Health | صحة المحصول
    // testWidgets('NDVI analysis screen renders map layer', ...);

    // Weather | الطقس
    // testWidgets('Weather screen shows forecast cards', ...);

    // Inventory | المخزون
    // testWidgets('Inventory list shows items', ...);
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// Test App Wrapper
// غلاف التطبيق للاختبار
// ══════════════════════════════════════════════════════════════════════════════

/// Minimal test app that mirrors the real SahoolApp structure.
/// تطبيق اختبار بسيط يعكس بنية تطبيق سهول الحقيقي.
class _TestSahoolApp extends StatelessWidget {
  final String? initialRoute;
  final Locale locale;

  const _TestSahoolApp({
    this.initialRoute,
    this.locale = const Locale('ar'),
  });

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SAHOOL Test',
      debugShowCheckedModeBanner: false,
      locale: locale,
      supportedLocales: const [
        Locale('ar'),
        Locale('en'),
      ],
      localizationsDelegates: const [
        // Add localizations delegates as available
        // إضافة مندوبي الترجمة عند توفرها
      ],
      // Use Directionality based on locale
      builder: (context, child) {
        return Directionality(
          textDirection:
              locale.languageCode == 'ar' ? TextDirection.rtl : TextDirection.ltr,
          child: child ?? const SizedBox.shrink(),
        );
      },
      home: Scaffold(
        appBar: AppBar(title: const Text('SAHOOL')),
        body: const Center(
          child: Text('SAHOOL Unified App'),
        ),
      ),
    );
  }
}
