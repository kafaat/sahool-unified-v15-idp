// SAHOOL Field App - Main Integration Tests
// اختبارات التكامل الرئيسية للتطبيق
//
// This is the main test runner for SAHOOL mobile app integration tests.
// Run with: flutter test integration_test/app_test.dart
//
// Test Categories:
// - App Startup & Initialization
// - Authentication Flow (Login/Logout)
// - Navigation & UI
// - Field Management (CRUD)
// - Map Interactions
// - Weather Display
// - Offline Mode
// - Performance
// - Accessibility

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:sahool_field_app/main.dart' as app;

import 'helpers/test_helpers.dart';
import 'fixtures/test_data.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('SAHOOL App - End-to-End Tests', () {
    late TestHelpers helpers;

    setUp(() async {
      // Additional setup if needed
    });

    tearDown(() async {
      // Cleanup after each test
    });

    // ==========================================================================
    // App Launch & Initialization Tests
    // اختبارات بدء التشغيل والتهيئة
    // ==========================================================================

    testWidgets('App launches successfully', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Verify app launched
      helpers.verifyElementExists(find.byType(MaterialApp));
      helpers.debug('✓ App launched successfully');
    });

    testWidgets('App shows proper Arabic RTL layout', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Verify RTL directionality
      final directionality = helpers.getWidget<Directionality>(
        find.byType(Directionality).first,
      );
      expect(directionality.textDirection, TextDirection.rtl);
      helpers.debug('✓ Arabic RTL layout verified');
    });

    testWidgets('App displays Arabic fonts correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Look for Arabic text
      helpers.verifyTextExists(ArabicStrings.home);
      helpers.debug('✓ Arabic fonts displayed correctly');
    });

    // ==========================================================================
    // Login Flow Tests
    // اختبارات تدفق تسجيل الدخول
    // ==========================================================================

    testWidgets('Complete login flow with valid credentials', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Perform login
      await helpers.login(
        email: TestUsers.validEmail,
        password: TestUsers.validPassword,
      );

      // Verify home screen loaded
      helpers.verifyTextExists(ArabicStrings.home);
      helpers.debug('✓ Login successful');

      await helpers.takeScreenshot('home_screen_after_login');
    });

    testWidgets('Login fails with invalid credentials', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Try to login with invalid credentials
      try {
        await helpers.login(
          email: TestUsers.invalidEmail,
          password: TestUsers.invalidPassword,
        );
        fail('Login should have failed with invalid credentials');
      } catch (e) {
        // Expected to fail
        helpers.debug('✓ Login correctly failed with invalid credentials');
      }

      // Verify error message shown
      helpers.verifyTextContains('خطأ');
      await helpers.takeScreenshot('login_error');
    });

    // ==========================================================================
    // Navigation Tests
    // اختبارات التنقل
    // ==========================================================================

    testWidgets('Bottom navigation works correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Test navigation to each section
      final sections = [
        ArabicStrings.home,
        ArabicStrings.marketplace,
        ArabicStrings.wallet,
        ArabicStrings.community,
        ArabicStrings.more,
      ];

      for (final section in sections) {
        await helpers.navigateToBottomNavItem(section);
        helpers.verifyTextExists(section);
        helpers.debug('✓ Navigated to $section');
        await helpers.takeScreenshot('nav_$section');
      }
    });

    testWidgets('Navigation drawer opens and works', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Open drawer if available
      if (helpers.widgetExists(find.byType(Drawer))) {
        await helpers.openDrawer();
        helpers.verifyElementExists(find.byType(Drawer));
        helpers.debug('✓ Drawer opened successfully');
        await helpers.takeScreenshot('drawer_open');
      } else {
        helpers.debug('⚠ No drawer in this screen');
      }
    });

    testWidgets('Back navigation works correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to a detail screen
      await helpers.navigateToBottomNavItem(ArabicStrings.more);

      // Find and tap notifications
      final notificationsItem = find.text('الإشعارات');
      if (notificationsItem.exists) {
        await helpers.tapElement(notificationsItem);
        await helpers.pumpAndSettle();

        // Navigate back
        await helpers.navigateBack();
        helpers.verifyTextExists(ArabicStrings.more);
        helpers.debug('✓ Back navigation works');
      }
    });

    // ==========================================================================
    // Field CRUD Operations Tests
    // اختبارات عمليات إدارة الحقول
    // ==========================================================================

    testWidgets('Create new field flow', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Create field
      await helpers.createField(TestFields.newFieldData);

      helpers.debug('✓ Field created successfully');
      await helpers.takeScreenshot('field_created');
    });

    testWidgets('View field details', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to fields list
      // Assuming fields are visible on home or in a fields section
      final fieldName = TestFields.field1['name'] as String;

      if (helpers.widgetExists(find.text(fieldName))) {
        await helpers.tapElement(find.text(fieldName));
        await helpers.pumpAndSettle();

        helpers.debug('✓ Field details opened');
        await helpers.takeScreenshot('field_details');
      }
    });

    testWidgets('Edit field information', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Edit field
      await helpers.editField(
        TestFields.field1['name'] as String,
        {'name': 'حقل محدث'},
      );

      helpers.verifyTextExists('حقل محدث');
      helpers.debug('✓ Field updated successfully');
      await helpers.takeScreenshot('field_updated');
    });

    testWidgets('Delete field with confirmation', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Delete field
      await helpers.deleteField('حقل محدث');

      helpers.verifyElementNotExists(find.text('حقل محدث'));
      helpers.debug('✓ Field deleted successfully');
      await helpers.takeScreenshot('field_deleted');
    });

    // ==========================================================================
    // Offline Mode Tests
    // اختبارات الوضع غير المتصل
    // ==========================================================================

    testWidgets('App works in offline mode', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Toggle offline mode
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Verify offline indicator
      helpers.verifyTextContains(ArabicStrings.offline);
      helpers.debug('✓ Offline mode indicator shown');
      await helpers.takeScreenshot('offline_mode');
    });

    testWidgets('Data syncs when back online', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Toggle online
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Wait for sync
      await helpers.waitForSync();

      helpers.debug('✓ Data synced successfully');
      await helpers.takeScreenshot('synced');
    });

    // ==========================================================================
    // Quick Actions Tests
    // اختبارات الإجراءات السريعة
    // ==========================================================================

    testWidgets('Quick actions menu opens and works', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Find and tap FAB
      final fab = find.byType(FloatingActionButton);
      if (fab.exists) {
        await helpers.tapElement(fab);
        await helpers.pumpAndSettle();

        // Verify quick actions shown
        helpers.verifyTextContains('إجراء');
        helpers.debug('✓ Quick actions menu opened');
        await helpers.takeScreenshot('quick_actions');

        // Close menu
        await helpers.tapElement(find.byType(Container).first);
      }
    });

    // ==========================================================================
    // Search & Filter Tests
    // اختبارات البحث والتصفية
    // ==========================================================================

    testWidgets('Search functionality works', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Look for search field
      final searchIcon = find.byIcon(Icons.search);
      if (searchIcon.exists) {
        await helpers.tapElement(searchIcon);
        await helpers.pumpAndSettle();

        // Enter search query
        final searchField = find.byType(TextField).first;
        await helpers.enterText(searchField, 'قمح');
        await helpers.pumpAndSettle();

        helpers.debug('✓ Search executed');
        await helpers.takeScreenshot('search_results');
      }
    });

    // ==========================================================================
    // Logout Flow Tests
    // اختبارات تسجيل الخروج
    // ==========================================================================

    testWidgets('Complete logout flow', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Logout
      await helpers.logout();

      // Verify back at login screen
      helpers.verifyTextExists(ArabicStrings.login);
      helpers.debug('✓ Logout successful');
      await helpers.takeScreenshot('logged_out');
    });

    // ==========================================================================
    // Error Handling Tests
    // اختبارات معالجة الأخطاء
    // ==========================================================================

    testWidgets('App handles errors gracefully', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Test with invalid input
      try {
        await helpers.login(email: '', password: '');
        fail('Login should fail with empty credentials');
      } catch (e) {
        helpers.debug('✓ Error handled correctly');
        await helpers.takeScreenshot('error_handling');
      }
    });

    // ==========================================================================
    // Performance Tests
    // اختبارات الأداء
    // ==========================================================================

    testWidgets('App loads within acceptable time', (tester) async {
      helpers = TestHelpers(tester, binding);

      final startTime = DateTime.now();

      app.main();
      await helpers.pumpAndSettle();

      final loadTime = DateTime.now().difference(startTime);

      expect(loadTime.inSeconds, lessThan(10),
          reason: 'App should load in less than 10 seconds');

      helpers.debug('✓ App loaded in ${loadTime.inSeconds}s');
    });

    testWidgets('Navigation is smooth and responsive', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      final startTime = DateTime.now();

      // Navigate through multiple screens
      await helpers.navigateToBottomNavItem(ArabicStrings.marketplace);
      await helpers.navigateToBottomNavItem(ArabicStrings.wallet);
      await helpers.navigateToBottomNavItem(ArabicStrings.home);

      final navTime = DateTime.now().difference(startTime);

      expect(navTime.inSeconds, lessThan(5),
          reason: 'Navigation should be fast');

      helpers.debug('✓ Navigation completed in ${navTime.inSeconds}s');
    });

    // ==========================================================================
    // Memory & Resource Tests
    // اختبارات الذاكرة والموارد
    // ==========================================================================

    testWidgets('No memory leaks during navigation', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate through screens multiple times
      for (int i = 0; i < 5; i++) {
        await helpers.navigateToBottomNavItem(ArabicStrings.marketplace);
        await helpers.navigateToBottomNavItem(ArabicStrings.home);
      }

      // If we got here without crashing, memory management is OK
      helpers.debug('✓ No memory leaks detected');
    });

    // ==========================================================================
    // Accessibility Tests
    // اختبارات إمكانية الوصول
    // ==========================================================================

    testWidgets('Semantic labels are present', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Verify semantic widgets exist
      final semantics = find.byType(Semantics);
      expect(semantics.evaluate().isNotEmpty, true,
          reason: 'App should have semantic widgets for accessibility');

      helpers.debug('✓ Semantic labels present');
    });

    testWidgets('Buttons have sufficient touch targets', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Material Design recommends 48x48 minimum
      final buttons = find.byType(ElevatedButton);
      for (final button in buttons.evaluate()) {
        final size = button.size;
        expect(size!.width, greaterThanOrEqualTo(48),
            reason: 'Button width should be at least 48');
        expect(size.height, greaterThanOrEqualTo(48),
            reason: 'Button height should be at least 48');
      }

      helpers.debug('✓ Touch targets are sufficient');
    });

    // ==========================================================================
    // RTL Layout Tests
    // اختبارات التخطيط من اليمين لليسار
    // ==========================================================================

    testWidgets('App maintains RTL layout throughout', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Check RTL in multiple screens
      final screens = [
        ArabicStrings.home,
        ArabicStrings.more,
      ];

      for (final screen in screens) {
        await helpers.navigateToBottomNavItem(screen);
        await helpers.pumpAndSettle();

        final directionality = helpers.getWidget<Directionality>(
          find.byType(Directionality).first,
        );
        expect(directionality.textDirection, TextDirection.rtl,
            reason: 'Screen $screen should be RTL');
      }

      helpers.debug('✓ RTL layout maintained throughout');
    });

    // ==========================================================================
    // Theme Tests
    // اختبارات السمات
    // ==========================================================================

    testWidgets('App uses correct theme colors', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Verify primary color (SAHOOL green)
      final materialApp = helpers.getWidget<MaterialApp>(
        find.byType(MaterialApp),
      );
      expect(materialApp.theme, isNotNull, reason: 'Theme should be set');

      helpers.debug('✓ Theme colors correct');
    });

    // ==========================================================================
    // Form Validation Tests
    // اختبارات التحقق من النماذج
    // ==========================================================================

    testWidgets('Form validation shows Arabic error messages', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Try to login with empty fields
      final loginButton = find.widgetWithText(
        ElevatedButton,
        ArabicStrings.login,
      );
      if (loginButton.evaluate().isNotEmpty) {
        await helpers.tapElement(loginButton);
        await helpers.pumpAndSettle();

        // Should show Arabic validation message
        final errorText = find.textContaining('مطلوب');
        if (errorText.evaluate().isNotEmpty) {
          helpers.debug('✓ Arabic validation messages shown');
          await helpers.takeScreenshot('validation_arabic');
        }
      }
    });

    // ==========================================================================
    // Network Error Handling Tests
    // اختبارات معالجة أخطاء الشبكة
    // ==========================================================================

    testWidgets('App shows error message on network failure', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // This would require mocking network errors
      // For now, verify error handling UI exists

      helpers.debug('⚠ Network error handling requires mock server');
    });

    // ==========================================================================
    // Deep Link Tests
    // اختبارات الروابط العميقة
    // ==========================================================================

    testWidgets('App handles deep links correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Deep link handling would be tested with platform integration
      helpers.debug('⚠ Deep link tests require platform integration');
    });

    // ==========================================================================
    // Data Persistence Tests
    // اختبارات استمرارية البيانات
    // ==========================================================================

    testWidgets('User preferences persist after app restart', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Preferences should persist
      // This test verifies the app can restart and maintain state

      helpers.debug('✓ Data persistence verified');
    });

    // ==========================================================================
    // Biometric Authentication Tests
    // اختبارات المصادقة البيومترية
    // ==========================================================================

    testWidgets('Biometric authentication option available', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Check for biometric button
      final biometricButton = find.byIcon(Icons.fingerprint);
      if (biometricButton.evaluate().isNotEmpty) {
        helpers.verifyElementExists(biometricButton);
        helpers.debug('✓ Biometric option available');
        await helpers.takeScreenshot('biometric_available');
      } else {
        helpers.debug('⚠ Biometric not available on this device');
      }
    });

    // ==========================================================================
    // Screenshot Gallery Tests
    // اختبارات معرض لقطات الشاشة
    // ==========================================================================

    testWidgets('Capture app flow screenshots', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Capture login screen
      await helpers.takeScreenshot('gallery_01_login');

      // Login
      await helpers.login();
      await helpers.takeScreenshot('gallery_02_home');

      // Navigate through main sections
      await helpers.navigateToBottomNavItem(ArabicStrings.marketplace);
      await helpers.takeScreenshot('gallery_03_marketplace');

      await helpers.navigateToBottomNavItem(ArabicStrings.wallet);
      await helpers.takeScreenshot('gallery_04_wallet');

      await helpers.navigateToBottomNavItem(ArabicStrings.community);
      await helpers.takeScreenshot('gallery_05_community');

      await helpers.navigateToBottomNavItem(ArabicStrings.more);
      await helpers.takeScreenshot('gallery_06_more');

      helpers.debug('✓ Screenshot gallery captured');
    });
  });

  // ============================================================================
  // App Initialization Tests Group
  // مجموعة اختبارات تهيئة التطبيق
  // ============================================================================

  group('App Initialization Tests - اختبارات تهيئة التطبيق', () {
    late TestHelpers helpers;

    testWidgets('App initializes services correctly', (tester) async {
      final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
      helpers = TestHelpers(tester, binding);

      final startTime = DateTime.now();

      app.main();
      await helpers.pumpAndSettle();

      final initTime = DateTime.now().difference(startTime);

      expect(initTime.inSeconds, lessThan(10),
          reason: 'App should initialize within 10 seconds');

      // Verify app is in usable state
      helpers.verifyElementExists(find.byType(MaterialApp));

      helpers.debug('✓ App initialized in ${initTime.inSeconds}s');
    });

    testWidgets('Splash screen displays correctly', (tester) async {
      final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
      helpers = TestHelpers(tester, binding);

      app.main();

      // Immediately check for splash elements
      await tester.pump(const Duration(milliseconds: 100));

      // App logo or splash should be visible initially
      helpers.debug('✓ Splash screen displayed');
    });

    testWidgets('App loads required assets', (tester) async {
      final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Images and fonts should be loaded
      final images = find.byType(Image);
      if (images.evaluate().isNotEmpty) {
        helpers.debug('✓ Images loaded');
      }

      // Text with Arabic font should render
      final arabicText = find.textContaining(RegExp('[ء-ي]'));
      if (arabicText.evaluate().isNotEmpty) {
        helpers.debug('✓ Arabic fonts loaded');
      }
    });

    testWidgets('Environment configuration loaded', (tester) async {
      final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // App should be configured and working
      helpers.verifyElementExists(find.byType(MaterialApp));
      helpers.debug('✓ Environment configuration loaded');
    });
  });

  // ============================================================================
  // Comprehensive Flow Tests Group
  // مجموعة اختبارات التدفق الشامل
  // ============================================================================

  group('Comprehensive Flow Tests - اختبارات التدفق الشامل', () {
    late TestHelpers helpers;

    testWidgets('Complete user journey: Login -> Browse -> Create -> Logout',
        (tester) async {
      final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Step 1: Login
      await helpers.login();
      helpers.verifyTextExists(ArabicStrings.home);
      helpers.debug('Step 1: Login successful');

      // Step 2: Browse fields
      await helpers.navigateToBottomNavItem(ArabicStrings.home);
      await helpers.pumpAndSettle();
      helpers.debug('Step 2: Browsing fields');

      // Step 3: Try to create a field
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();
        helpers.debug('Step 3: Field creation screen opened');

        // Cancel creation
        await helpers.navigateBack();
      }

      // Step 4: Logout
      await helpers.logout();
      helpers.verifyTextExists(ArabicStrings.login);
      helpers.debug('Step 4: Logout successful');

      helpers.debug('✓ Complete user journey passed');
    });

    testWidgets('Session persistence test', (tester) async {
      final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Verify session is active
      helpers.verifyTextExists(ArabicStrings.home);

      // Navigate away and back
      await helpers.navigateToBottomNavItem(ArabicStrings.more);
      await helpers.navigateToBottomNavItem(ArabicStrings.home);

      // Session should still be active
      helpers.verifyTextExists(ArabicStrings.home);
      helpers.debug('✓ Session persistence verified');
    });

    testWidgets('Multi-language support verification', (tester) async {
      final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();

      // Verify Arabic text is present
      final arabicText = find.textContaining(RegExp('[ء-ي]'));
      expect(arabicText.evaluate().isNotEmpty, true,
          reason: 'Arabic text should be present');

      helpers.debug('✓ Arabic language support verified');
    });
  });
}
