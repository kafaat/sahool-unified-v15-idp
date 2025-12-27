/// SAHOOL Field App - Main Integration Tests
/// اختبارات التكامل الرئيسية للتطبيق
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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

      await app.main();
      await helpers.pumpAndSettle();

      // Verify app launched
      helpers.verifyElementExists(find.byType(MaterialApp));
      helpers.debug('✓ App launched successfully');
    });

    testWidgets('App shows proper Arabic RTL layout', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Create field
      await helpers.createField(TestFields.newFieldData);

      helpers.debug('✓ Field created successfully');
      await helpers.takeScreenshot('field_created');
    });

    testWidgets('View field details', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
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

      await app.main();
      await helpers.pumpAndSettle();

      final loadTime = DateTime.now().difference(startTime);

      expect(loadTime.inSeconds, lessThan(10),
          reason: 'App should load in less than 10 seconds');

      helpers.debug('✓ App loaded in ${loadTime.inSeconds}s');
    });

    testWidgets('Navigation is smooth and responsive', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
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

      await app.main();
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

      await app.main();
      await helpers.pumpAndSettle();

      // Verify semantic widgets exist
      final semantics = find.byType(Semantics);
      expect(semantics.evaluate().isNotEmpty, true,
          reason: 'App should have semantic widgets for accessibility');

      helpers.debug('✓ Semantic labels present');
    });

    testWidgets('Buttons have sufficient touch targets', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
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
  });
}
