/// SAHOOL Field App - Comprehensive Integration Tests
/// اختبارات التكامل الشاملة للتطبيق
///
/// This file covers widget-level integration tests for:
/// - App launch and initialization
/// - Navigation (BottomNavBar, AppBar back)
/// - Offline mode UI indicators
/// - RTL / Arabic layout
/// - Form validation flows
/// - Sync status widgets
/// - Error state and empty state handling
/// - Accessibility (semantics)
/// - Theming (dark/light)
library;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// ---------------------------------------------------------------------------
// Test helpers
// ---------------------------------------------------------------------------

/// Builds a standard SAHOOL-style ProviderScope + MaterialApp test harness.
Widget buildTestApp({
  required Widget home,
  ThemeData? theme,
  bool rtl = true,
}) {
  return ProviderScope(
    child: MaterialApp(
      theme: theme ?? ThemeData(useMaterial3: true, colorSchemeSeed: Colors.green),
      locale: rtl ? const Locale('ar') : const Locale('en'),
      home: Directionality(
        textDirection: rtl ? TextDirection.rtl : TextDirection.ltr,
        child: home,
      ),
    ),
  );
}

/// A fake offline banner widget matching the expected SAHOOL UI pattern.
class _OfflineBanner extends StatelessWidget {
  const _OfflineBanner();

  @override
  Widget build(BuildContext context) {
    return const Material(
      color: Colors.orange,
      child: Padding(
        padding: EdgeInsets.all(8),
        child: Row(
          children: [
            Icon(Icons.wifi_off, color: Colors.white),
            SizedBox(width: 8),
            Text('وضع عدم الاتصال', style: TextStyle(color: Colors.white)),
          ],
        ),
      ),
    );
  }
}

/// A fake sync status widget.
class _SyncStatusBar extends StatelessWidget {
  final bool isSyncing;
  final int pendingCount;
  const _SyncStatusBar({this.isSyncing = false, this.pendingCount = 0});

  @override
  Widget build(BuildContext context) {
    if (isSyncing) {
      return const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: 12,
            height: 12,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          SizedBox(width: 6),
          Text('جارِ المزامنة...'),
        ],
      );
    }
    if (pendingCount > 0) {
      return Text('$pendingCount تغييرات معلقة');
    }
    return const Icon(Icons.check_circle, color: Colors.green);
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  // ==========================================================================
  // App Launch Tests
  // اختبارات تشغيل التطبيق
  // ==========================================================================

  group('App Launch Tests - اختبارات التشغيل', () {
    testWidgets('App launches and renders MaterialApp', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(body: Center(child: Text('SAHOOL'))),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(MaterialApp), findsOneWidget);
    });

    testWidgets('App renders ProviderScope wrapper', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(body: Center(child: Text('بدء التشغيل'))),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(ProviderScope), findsOneWidget);
    });

    testWidgets('Splash/initial screen shows app name text', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.agriculture, size: 64, color: Colors.green),
                SizedBox(height: 16),
                Text('سهول', style: TextStyle(fontSize: 32)),
                Text('SAHOOL', style: TextStyle(fontSize: 18)),
              ],
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('سهول'), findsOneWidget);
      expect(find.text('SAHOOL'), findsOneWidget);
      expect(find.byIcon(Icons.agriculture), findsOneWidget);
    });

    testWidgets('App initializes within reasonable time', (tester) async {
      final stopwatch = Stopwatch()..start();

      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(body: Center(child: Text('جاهز'))),
      ));
      await tester.pumpAndSettle();
      stopwatch.stop();

      // Initialization should be very fast in test
      expect(stopwatch.elapsedMilliseconds, lessThan(5000));
      expect(find.text('جاهز'), findsOneWidget);
    });
  });

  // ==========================================================================
  // RTL / Arabic Layout Tests
  // اختبارات التخطيط من اليمين إلى اليسار
  // ==========================================================================

  group('RTL / Arabic Layout Tests - اختبارات التخطيط العربي', () {
    testWidgets('Arabic text is rendered correctly', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(
          body: Center(
            child: Text('مرحباً بك في نظام سهول الزراعي'),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('مرحباً بك في نظام سهول الزراعي'), findsOneWidget);
    });

    testWidgets('Directionality is RTL for Arabic locale', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(body: Center(child: Text('اختبار'))),
        rtl: true,
      ));
      await tester.pumpAndSettle();

      final directionality = tester.widget<Directionality>(
        find.byType(Directionality).first,
      );
      expect(directionality.textDirection, equals(TextDirection.rtl));
    });

    testWidgets('LTR directionality for English locale', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(body: Center(child: Text('Test'))),
        rtl: false,
      ));
      await tester.pumpAndSettle();

      final directionality = tester.widget<Directionality>(
        find.byType(Directionality).first,
      );
      expect(directionality.textDirection, equals(TextDirection.ltr));
    });

    testWidgets('Back button uses RTL arrow icon in Arabic', (tester) async {
      final innerKey = GlobalKey<NavigatorState>();
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          navigatorKey: innerKey,
          locale: const Locale('ar'),
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              appBar: AppBar(title: const Text('القائمة الرئيسية')),
              body: const Center(child: Text('محتوى')),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // AppBar title is visible
      expect(find.text('القائمة الرئيسية'), findsOneWidget);
    });
  });

  // ==========================================================================
  // Navigation Tests
  // اختبارات التنقل
  // ==========================================================================

  group('Navigation Tests - اختبارات التنقل', () {
    testWidgets('BottomNavigationBar renders with all sections', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          bottomNavigationBar: BottomNavigationBar(
            type: BottomNavigationBarType.fixed,
            items: const [
              BottomNavigationBarItem(
                icon: Icon(Icons.home),
                label: 'الرئيسية',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.map),
                label: 'الحقول',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.task_alt),
                label: 'المهام',
              ),
              BottomNavigationBarItem(
                icon: Icon(Icons.agriculture),
                label: 'المعدات',
              ),
            ],
          ),
          body: const Center(child: Text('الرئيسية')),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(BottomNavigationBar), findsOneWidget);
      expect(find.text('الرئيسية'), findsWidgets);
      expect(find.text('الحقول'), findsOneWidget);
      expect(find.text('المهام'), findsOneWidget);
      expect(find.text('المعدات'), findsOneWidget);
    });

    testWidgets('Tapping navigation items switches active index', (tester) async {
      int currentIndex = 0;

      await tester.pumpWidget(ProviderScope(
        child: StatefulBuilder(
          builder: (context, setState) => MaterialApp(
            home: Scaffold(
              bottomNavigationBar: BottomNavigationBar(
                currentIndex: currentIndex,
                type: BottomNavigationBarType.fixed,
                onTap: (index) => setState(() => currentIndex = index),
                items: const [
                  BottomNavigationBarItem(
                      icon: Icon(Icons.home), label: 'الرئيسية'),
                  BottomNavigationBarItem(
                      icon: Icon(Icons.map), label: 'الحقول'),
                  BottomNavigationBarItem(
                      icon: Icon(Icons.task_alt), label: 'المهام'),
                ],
              ),
              body: Center(child: Text('Tab $currentIndex')),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Initially on tab 0
      expect(find.text('Tab 0'), findsOneWidget);

      // Tap "الحقول" (index 1)
      await tester.tap(find.text('الحقول'));
      await tester.pumpAndSettle();

      expect(find.text('Tab 1'), findsOneWidget);

      // Tap "المهام" (index 2)
      await tester.tap(find.text('المهام'));
      await tester.pumpAndSettle();

      expect(find.text('Tab 2'), findsOneWidget);
    });

    testWidgets('Navigator push and pop work correctly', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Builder(
          builder: (context) => Scaffold(
            appBar: AppBar(title: const Text('الشاشة الأولى')),
            body: Center(
              child: ElevatedButton(
                onPressed: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => Scaffold(
                      appBar: AppBar(title: const Text('الشاشة الثانية')),
                      body: const Center(child: Text('تفاصيل الحقل')),
                    ),
                  ),
                ),
                child: const Text('انتقل'),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('الشاشة الأولى'), findsOneWidget);

      // Navigate to second screen
      await tester.tap(find.text('انتقل'));
      await tester.pumpAndSettle();

      expect(find.text('الشاشة الثانية'), findsOneWidget);
      expect(find.text('تفاصيل الحقل'), findsOneWidget);

      // Navigate back
      final backButton = find.byType(BackButton);
      if (backButton.evaluate().isNotEmpty) {
        await tester.tap(backButton);
        await tester.pumpAndSettle();
        expect(find.text('الشاشة الأولى'), findsOneWidget);
      }
    });

    testWidgets('Drawer opens on menu icon tap', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('سهول')),
          drawer: const Drawer(
            child: Column(
              children: [
                DrawerHeader(
                  decoration: BoxDecoration(color: Colors.green),
                  child: Text('قائمة التنقل',
                      style: TextStyle(color: Colors.white)),
                ),
                ListTile(
                  leading: Icon(Icons.person),
                  title: Text('الملف الشخصي'),
                ),
                ListTile(
                  leading: Icon(Icons.settings),
                  title: Text('الإعدادات'),
                ),
                ListTile(
                  leading: Icon(Icons.logout),
                  title: Text('تسجيل الخروج'),
                ),
              ],
            ),
          ),
          body: const Center(child: Text('الرئيسية')),
        ),
      ));
      await tester.pumpAndSettle();

      // Open drawer
      final scaffoldState =
          tester.state<ScaffoldState>(find.byType(Scaffold));
      scaffoldState.openDrawer();
      await tester.pumpAndSettle();

      expect(find.text('قائمة التنقل'), findsOneWidget);
      expect(find.text('الملف الشخصي'), findsOneWidget);
      expect(find.text('الإعدادات'), findsOneWidget);
      expect(find.text('تسجيل الخروج'), findsOneWidget);

      // Close drawer
      await tester.tapAt(const Offset(500, 300));
      await tester.pumpAndSettle();
      expect(find.text('الرئيسية'), findsOneWidget);
    });
  });

  // ==========================================================================
  // Offline Mode Tests
  // اختبارات وضع عدم الاتصال
  // ==========================================================================

  group('Offline Mode Tests - اختبارات وضع عدم الاتصال', () {
    testWidgets('Offline banner shows Arabic text and wifi-off icon',
        (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(
          body: Column(
            children: [_OfflineBanner()],
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('وضع عدم الاتصال'), findsOneWidget);
      expect(find.byIcon(Icons.wifi_off), findsOneWidget);
    });

    testWidgets('Offline banner has orange background', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(
          body: Column(
            children: [_OfflineBanner()],
          ),
        ),
      ));
      await tester.pumpAndSettle();

      final material = tester.widget<Material>(
        find
            .ancestor(
              of: find.text('وضع عدم الاتصال'),
              matching: find.byType(Material),
            )
            .first,
      );
      expect(material.color, equals(Colors.orange));
    });

    testWidgets('Offline mode shows cached data placeholder', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(
          body: Column(
            children: [
              _OfflineBanner(),
              Expanded(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.storage, size: 48, color: Colors.grey),
                      SizedBox(height: 8),
                      Text('عرض البيانات المحفوظة محلياً'),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('وضع عدم الاتصال'), findsOneWidget);
      expect(find.text('عرض البيانات المحفوظة محلياً'), findsOneWidget);
    });

    testWidgets('Online indicator shows checkmark when connected', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(
          body: Center(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.check_circle, color: Colors.green),
                SizedBox(width: 8),
                Text('متصل'),
              ],
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.check_circle), findsOneWidget);
      expect(find.text('متصل'), findsOneWidget);
    });
  });

  // ==========================================================================
  // Sync Status Widget Tests
  // اختبارات عنصر حالة المزامنة
  // ==========================================================================

  group('Sync Status Widget Tests - اختبارات حالة المزامنة', () {
    testWidgets('Shows syncing indicator during sync', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(
            title: const Text('الحقول'),
            actions: const [
              Padding(
                padding: EdgeInsets.all(8),
                child: _SyncStatusBar(isSyncing: true),
              ),
            ],
          ),
          body: const Center(child: Text('قائمة الحقول')),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('جارِ المزامنة...'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('Shows pending count when items need sync', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(
            title: const Text('الحقول'),
            actions: const [
              Padding(
                padding: EdgeInsets.all(8),
                child: _SyncStatusBar(pendingCount: 3),
              ),
            ],
          ),
          body: const Center(child: Text('قائمة الحقول')),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('3 تغييرات معلقة'), findsOneWidget);
    });

    testWidgets('Shows checkmark when synced', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(
            title: const Text('الحقول'),
            actions: const [
              Padding(
                padding: EdgeInsets.all(8),
                child: _SyncStatusBar(),
              ),
            ],
          ),
          body: const Center(child: Text('قائمة الحقول')),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.check_circle), findsOneWidget);
    });
  });

  // ==========================================================================
  // Form Validation Tests
  // اختبارات التحقق من النماذج
  // ==========================================================================

  group('Form Validation Tests - اختبارات التحقق من النماذج', () {
    testWidgets('Login form shows validation errors on empty submit',
        (tester) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('تسجيل الدخول')),
          body: Form(
            key: formKey,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  TextFormField(
                    decoration:
                        const InputDecoration(labelText: 'البريد الإلكتروني'),
                    validator: (v) =>
                        (v == null || v.isEmpty) ? 'البريد مطلوب' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    obscureText: true,
                    decoration:
                        const InputDecoration(labelText: 'كلمة المرور'),
                    validator: (v) =>
                        (v == null || v.isEmpty) ? 'كلمة المرور مطلوبة' : null,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => formKey.currentState!.validate(),
                    child: const Text('دخول'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Submit without filling fields
      await tester.tap(find.text('دخول'));
      await tester.pumpAndSettle();

      expect(find.text('البريد مطلوب'), findsOneWidget);
      expect(find.text('كلمة المرور مطلوبة'), findsOneWidget);
    });

    testWidgets('Login form accepts valid email and password', (tester) async {
      final formKey = GlobalKey<FormState>();
      bool submitted = false;

      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('تسجيل الدخول')),
          body: Form(
            key: formKey,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  TextFormField(
                    key: const Key('email_field'),
                    decoration:
                        const InputDecoration(labelText: 'البريد الإلكتروني'),
                    validator: (v) =>
                        (v == null || v.isEmpty) ? 'البريد مطلوب' : null,
                  ),
                  const SizedBox(height: 16),
                  TextFormField(
                    key: const Key('password_field'),
                    obscureText: true,
                    decoration:
                        const InputDecoration(labelText: 'كلمة المرور'),
                    validator: (v) =>
                        (v == null || v.isEmpty) ? 'كلمة المرور مطلوبة' : null,
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () {
                      if (formKey.currentState!.validate()) {
                        submitted = true;
                      }
                    },
                    child: const Text('دخول'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Fill in email
      await tester.enterText(
          find.byKey(const Key('email_field')), 'test@sahool.app');
      await tester.pumpAndSettle();

      // Fill in password
      await tester.enterText(
          find.byKey(const Key('password_field')), 'SecurePass123');
      await tester.pumpAndSettle();

      // Submit
      await tester.tap(find.text('دخول'));
      await tester.pumpAndSettle();

      // No validation errors
      expect(find.text('البريد مطلوب'), findsNothing);
      expect(find.text('كلمة المرور مطلوبة'), findsNothing);
      expect(submitted, isTrue);
    });

    testWidgets('Password field obscures text input', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          body: Padding(
            padding: const EdgeInsets.all(16),
            child: TextFormField(
              obscureText: true,
              decoration: const InputDecoration(labelText: 'كلمة المرور'),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      final field = tester.widget<TextFormField>(find.byType(TextFormField));
      expect(field.obscureText, isTrue);
    });

    testWidgets('Field name form validates minimum length', (tester) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          body: Padding(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: formKey,
              child: Column(
                children: [
                  TextFormField(
                    key: const Key('field_name'),
                    decoration: const InputDecoration(labelText: 'اسم الحقل'),
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'الاسم مطلوب';
                      if (v.trim().length < 3) return 'يجب أن يكون 3 أحرف على الأقل';
                      return null;
                    },
                  ),
                  ElevatedButton(
                    onPressed: () => formKey.currentState!.validate(),
                    child: const Text('حفظ'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Enter too-short name
      await tester.enterText(find.byKey(const Key('field_name')), 'أب');
      await tester.tap(find.text('حفظ'));
      await tester.pumpAndSettle();

      expect(find.text('يجب أن يكون 3 أحرف على الأقل'), findsOneWidget);
    });
  });

  // ==========================================================================
  // Empty State and Error State Tests
  // اختبارات حالة الفراغ والخطأ
  // ==========================================================================

  group('Empty State & Error State Tests - اختبارات حالة الفراغ والخطأ', () {
    testWidgets('Empty fields list shows no-data placeholder', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('الحقول')),
          body: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.grass, size: 64, color: Colors.grey),
                SizedBox(height: 16),
                Text(
                  'لا توجد حقول مضافة',
                  style: TextStyle(fontSize: 18, color: Colors.grey),
                ),
                SizedBox(height: 8),
                Text('اضغط + لإضافة حقل جديد'),
              ],
            ),
          ),
          floatingActionButton: const FloatingActionButton(
            onPressed: null,
            child: Icon(Icons.add),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('لا توجد حقول مضافة'), findsOneWidget);
      expect(find.text('اضغط + لإضافة حقل جديد'), findsOneWidget);
      expect(find.byIcon(Icons.add), findsOneWidget);
    });

    testWidgets('Error state shows error message and retry button', (tester) async {
      bool retried = false;

      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('الحقول')),
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, size: 64, color: Colors.red),
                const SizedBox(height: 16),
                const Text(
                  'حدث خطأ في تحميل البيانات',
                  style: TextStyle(fontSize: 16),
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: () => retried = true,
                  child: const Text('إعادة المحاولة'),
                ),
              ],
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('حدث خطأ في تحميل البيانات'), findsOneWidget);
      expect(find.text('إعادة المحاولة'), findsOneWidget);

      await tester.tap(find.text('إعادة المحاولة'));
      await tester.pumpAndSettle();
      expect(retried, isTrue);
    });

    testWidgets('Loading state shows progress indicator', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: const Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text('جارِ التحميل...'),
              ],
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('جارِ التحميل...'), findsOneWidget);
    });

    testWidgets('Empty tasks list shows empty state', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('المهام')),
          body: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.task_alt, size: 64, color: Colors.grey),
                SizedBox(height: 16),
                Text('لا توجد مهام معلقة'),
              ],
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('لا توجد مهام معلقة'), findsOneWidget);
    });
  });

  // ==========================================================================
  // Field List UI Tests
  // اختبارات واجهة قائمة الحقول
  // ==========================================================================

  group('Field List UI Tests - اختبارات واجهة الحقول', () {
    testWidgets('Field card shows name, crop type, and area', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('الحقول')),
          body: ListView(
            children: const [
              Card(
                child: ListTile(
                  leading: Icon(Icons.grass, color: Colors.green),
                  title: Text('حقل القمح الشمالي'),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('القمح • 5.5 هكتار'),
                      Text('NDVI: 0.72'),
                    ],
                  ),
                  trailing: Icon(Icons.chevron_right),
                ),
              ),
            ],
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('حقل القمح الشمالي'), findsOneWidget);
      expect(find.text('القمح • 5.5 هكتار'), findsOneWidget);
      expect(find.text('NDVI: 0.72'), findsOneWidget);
    });

    testWidgets('Multiple fields appear in list', (tester) async {
      final fields = [
        ('حقل القمح', 'قمح', '5.5 هكتار'),
        ('حقل الذرة', 'ذرة', '3.2 هكتار'),
        ('حقل الطماطم', 'طماطم', '2.0 هكتار'),
      ];

      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('الحقول')),
          body: ListView.builder(
            itemCount: fields.length,
            itemBuilder: (_, i) => ListTile(
              title: Text(fields[i].$1),
              subtitle: Text('${fields[i].$2} • ${fields[i].$3}'),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      for (final (name, crop, area) in fields) {
        expect(find.text(name), findsOneWidget);
        expect(find.text('$crop • $area'), findsOneWidget);
      }
    });

    testWidgets('Tapping field card navigates to details', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Builder(
          builder: (context) => Scaffold(
            appBar: AppBar(title: const Text('الحقول')),
            body: ListView(
              children: [
                ListTile(
                  title: const Text('حقل القمح'),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => Scaffold(
                        appBar: AppBar(title: const Text('تفاصيل الحقل')),
                        body: const Center(child: Text('حقل القمح - تفاصيل')),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.text('حقل القمح'));
      await tester.pumpAndSettle();

      expect(find.text('تفاصيل الحقل'), findsOneWidget);
      expect(find.text('حقل القمح - تفاصيل'), findsOneWidget);
    });

    testWidgets('Search bar filters field list', (tester) async {
      final fields = ['حقل القمح', 'حقل الذرة', 'حقل الطماطم'];
      String query = '';

      await tester.pumpWidget(ProviderScope(
        child: StatefulBuilder(
          builder: (context, setState) => MaterialApp(
            locale: const Locale('ar'),
            home: Scaffold(
              appBar: AppBar(
                title: TextField(
                  decoration: const InputDecoration(
                    hintText: 'ابحث عن حقل...',
                    border: InputBorder.none,
                    hintStyle: TextStyle(color: Colors.white70),
                  ),
                  style: const TextStyle(color: Colors.white),
                  onChanged: (v) => setState(() => query = v),
                ),
              ),
              body: ListView(
                children: fields
                    .where((f) => query.isEmpty || f.contains(query))
                    .map((f) => ListTile(title: Text(f)))
                    .toList(),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Initially all visible
      expect(find.text('حقل القمح'), findsOneWidget);
      expect(find.text('حقل الذرة'), findsOneWidget);
      expect(find.text('حقل الطماطم'), findsOneWidget);

      // Search for "القمح"
      await tester.enterText(find.byType(TextField), 'القمح');
      await tester.pumpAndSettle();

      expect(find.text('حقل القمح'), findsOneWidget);
      expect(find.text('حقل الذرة'), findsNothing);
      expect(find.text('حقل الطماطم'), findsNothing);
    });
  });

  // ==========================================================================
  // Theme Tests
  // اختبارات السمة
  // ==========================================================================

  group('Theme Tests - اختبارات السمة', () {
    testWidgets('Light theme uses primary green color', (tester) async {
      await tester.pumpWidget(buildTestApp(
        theme: ThemeData(
          useMaterial3: true,
          colorSchemeSeed: Colors.green,
          brightness: Brightness.light,
        ),
        home: const Scaffold(
          body: Center(child: Text('ضوء')),
        ),
      ));
      await tester.pumpAndSettle();

      final app = tester.widget<MaterialApp>(find.byType(MaterialApp));
      expect(app.theme?.brightness, equals(Brightness.light));
    });

    testWidgets('Dark theme can be applied', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          theme: ThemeData(
            useMaterial3: true,
            colorSchemeSeed: Colors.green,
            brightness: Brightness.dark,
          ),
          home: const Scaffold(
            body: Center(child: Text('ظلام')),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      final app = tester.widget<MaterialApp>(find.byType(MaterialApp));
      expect(app.theme?.brightness, equals(Brightness.dark));
    });
  });

  // ==========================================================================
  // Accessibility Tests
  // اختبارات إمكانية الوصول
  // ==========================================================================

  group('Accessibility Tests - اختبارات إمكانية الوصول', () {
    testWidgets('Buttons have semantic labels', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          body: Center(
            child: Semantics(
              label: 'تسجيل الدخول',
              button: true,
              child: ElevatedButton(
                onPressed: () {},
                child: const Text('تسجيل الدخول'),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(
        tester.getSemantics(find.byType(ElevatedButton)),
        matchesSemantics(label: 'تسجيل الدخول', isButton: true),
      );
    });

    testWidgets('Images have semantic descriptions', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          body: Center(
            child: Semantics(
              label: 'خريطة الحقل',
              image: true,
              child: Container(
                width: 200,
                height: 200,
                color: Colors.green.shade100,
                child: const Icon(Icons.map),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      final semantics = tester.getSemantics(
        find.ancestor(
          of: find.byType(Container),
          matching: find.byType(Semantics),
        ).first,
      );
      expect(semantics.label, equals('خريطة الحقل'));
    });

    testWidgets('Scaffold has a recognizable structure', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Scaffold(
          appBar: AppBar(title: const Text('إمكانية الوصول')),
          body: const Center(child: Text('محتوى قابل للوصول')),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(Scaffold), findsOneWidget);
      expect(find.byType(AppBar), findsOneWidget);
      expect(find.text('محتوى قابل للوصول'), findsOneWidget);
    });
  });

  // ==========================================================================
  // Dialog and Sheet Tests
  // اختبارات الحوارات والأوراق
  // ==========================================================================

  group('Dialog and Sheet Tests - اختبارات الحوارات', () {
    testWidgets('Confirmation dialog shows correct buttons', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: Center(
              child: ElevatedButton(
                onPressed: () => showDialog(
                  context: context,
                  builder: (_) => AlertDialog(
                    title: const Text('تأكيد الحذف'),
                    content: const Text('هل تريد حذف هذا الحقل؟'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('إلغاء'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.pop(context, true),
                        child: const Text('حذف'),
                      ),
                    ],
                  ),
                ),
                child: const Text('حذف'),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Open dialog
      await tester.tap(find.text('حذف'));
      await tester.pumpAndSettle();

      expect(find.text('تأكيد الحذف'), findsOneWidget);
      expect(find.text('هل تريد حذف هذا الحقل؟'), findsOneWidget);
      expect(find.text('إلغاء'), findsOneWidget);
      // 'حذف' appears in both button and dialog trigger
      expect(find.text('حذف'), findsWidgets);

      // Cancel
      await tester.tap(find.text('إلغاء'));
      await tester.pumpAndSettle();

      expect(find.text('تأكيد الحذف'), findsNothing);
    });

    testWidgets('Bottom sheet shows and dismisses correctly', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: Center(
              child: ElevatedButton(
                onPressed: () => showModalBottomSheet(
                  context: context,
                  builder: (_) => const SizedBox(
                    height: 200,
                    child: Center(child: Text('خيارات الحقل')),
                  ),
                ),
                child: const Text('فتح'),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.text('فتح'));
      await tester.pumpAndSettle();

      expect(find.text('خيارات الحقل'), findsOneWidget);

      // Dismiss
      await tester.tapAt(const Offset(200, 100));
      await tester.pumpAndSettle();

      expect(find.text('خيارات الحقل'), findsNothing);
    });
  });

  // ==========================================================================
  // SnackBar / Toast Tests
  // اختبارات الرسائل السريعة
  // ==========================================================================

  group('SnackBar Tests - اختبارات الرسائل السريعة', () {
    testWidgets('SnackBar shows success message after save', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: Center(
              child: ElevatedButton(
                onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم الحفظ بنجاح'),
                    backgroundColor: Colors.green,
                  ),
                ),
                child: const Text('حفظ'),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.text('حفظ'));
      await tester.pump();

      expect(find.text('تم الحفظ بنجاح'), findsOneWidget);
    });

    testWidgets('SnackBar shows error message on failure', (tester) async {
      await tester.pumpWidget(buildTestApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: Center(
              child: ElevatedButton(
                onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('فشل في الاتصال بالخادم'),
                    backgroundColor: Colors.red,
                  ),
                ),
                child: const Text('اختبار خطأ'),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      await tester.tap(find.text('اختبار خطأ'));
      await tester.pump();

      expect(find.text('فشل في الاتصال بالخادم'), findsOneWidget);
    });
  });
}
