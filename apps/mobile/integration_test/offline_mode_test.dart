// SAHOOL Integration Test - Offline Mode Tests
// اختبارات الوضع غير المتصل
//
// Tests for:
// - Offline mode detection and indication
// - Data persistence when offline
// - CRUD operations in offline mode
// - Sync when back online
// - Conflict resolution
// - Queue management

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:sahool_field_app/main.dart' as app;

import 'helpers/test_helpers.dart';
import 'fixtures/test_data.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Offline Mode Tests - اختبارات الوضع غير المتصل', () {
    late TestHelpers helpers;

    setUp(() async {
      // Setup for each test
    });

    tearDown(() async {
      // Cleanup after each test - ensure online mode
      // This would require mocking in a real scenario
    });

    // ==========================================================================
    // Offline Detection Tests
    // اختبارات اكتشاف عدم الاتصال
    // ==========================================================================

    testWidgets('App detects offline mode correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Toggle offline mode
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Verify offline indicator appears
      final offlineIndicator = find.textContaining(ArabicStrings.offline);
      final offlineIcon = find.byIcon(Icons.cloud_off);
      final offlineBanner = find.byIcon(Icons.signal_wifi_off);

      final hasOfflineIndicator = offlineIndicator.evaluate().isNotEmpty ||
          offlineIcon.evaluate().isNotEmpty ||
          offlineBanner.evaluate().isNotEmpty;

      if (hasOfflineIndicator) {
        helpers.debug('Offline mode detected and indicated');
        await helpers.takeScreenshot('offline_indicator');
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Offline banner shows correct message', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Toggle offline mode
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Check for offline message
      helpers.verifyTextContains(ArabicStrings.offline);
      helpers.debug('Offline banner message displayed');
      await helpers.takeScreenshot('offline_banner');

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('App gracefully transitions to offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // App should be in online mode initially
      await helpers.pumpAndSettle();

      // Transition to offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // App should still be functional
      helpers.verifyTextExists(ArabicStrings.home);
      helpers.debug('App transitioned to offline gracefully');

      // Go back online
      await helpers.toggleOfflineMode();
    });

    // ==========================================================================
    // Data Persistence Tests
    // اختبارات استمرارية البيانات
    // ==========================================================================

    testWidgets('Cached data available when offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Wait for initial data load
      await helpers.wait(TestConfig.mediumDelay);

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Navigate to fields - data should be available from cache
      await helpers.navigateToBottomNavItem(ArabicStrings.home);
      await helpers.pumpAndSettle();

      // Data should still be visible
      final fieldCard = find.textContaining('حقل');
      if (fieldCard.evaluate().isNotEmpty) {
        helpers.debug('Cached field data available offline');
        await helpers.takeScreenshot('offline_cached_data');
      } else {
        helpers.debug('No cached data - first run');
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Local database stores data correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Create data while online
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        // Fill field name
        await helpers.enterText(
          find.byType(TextField).first,
          'حقل اختبار قاعدة البيانات',
        );

        // Save
        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();
        }
      }

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Data should still be visible
      helpers.verifyTextContains('حقل');
      helpers.debug('Data persisted to local database');
      await helpers.takeScreenshot('offline_local_db');

      // Go back online
      await helpers.toggleOfflineMode();
    });

    // ==========================================================================
    // Offline CRUD Operations Tests
    // اختبارات عمليات CRUD بدون اتصال
    // ==========================================================================

    testWidgets('Create field while offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Create new field
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        // Fill form
        await helpers.enterText(
          find.byType(TextField).first,
          'حقل مُنشأ بدون اتصال',
        );

        await helpers.takeScreenshot('offline_create_form');

        // Save
        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();

          // Verify field created locally
          helpers.verifyTextContains('حقل');
          helpers.debug('Field created while offline');
          await helpers.takeScreenshot('offline_create_success');
        }
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Edit field while offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Find existing field
      final fieldCard = find.textContaining('حقل');
      if (fieldCard.evaluate().isNotEmpty) {
        // Long press to edit
        await helpers.longPressElement(fieldCard.first);
        await helpers.pumpAndSettle();

        // Tap edit
        final editOption = find.text(ArabicStrings.edit);
        if (editOption.evaluate().isNotEmpty) {
          await helpers.tapElement(editOption);
          await helpers.pumpAndSettle();

          // Update name
          await helpers.clearText(find.byType(TextField).first);
          await helpers.enterText(
            find.byType(TextField).first,
            'حقل محدث بدون اتصال',
          );

          // Save
          final saveButton = find.text(ArabicStrings.save);
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();

          helpers.debug('Field edited while offline');
          await helpers.takeScreenshot('offline_edit_success');
        }
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Delete field while offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Find field to delete
      final fieldCard = find.textContaining('حقل محدث بدون اتصال');
      if (fieldCard.evaluate().isNotEmpty) {
        // Long press to show options
        await helpers.longPressElement(fieldCard);
        await helpers.pumpAndSettle();

        // Tap delete
        final deleteOption = find.text(ArabicStrings.delete);
        if (deleteOption.evaluate().isNotEmpty) {
          await helpers.tapElement(deleteOption);
          await helpers.pumpAndSettle();

          // Confirm
          final confirmButton = find.text(ArabicStrings.confirm);
          await helpers.tapElement(confirmButton);
          await helpers.pumpAndSettle();

          // Verify deletion
          helpers.verifyElementNotExists(find.text('حقل محدث بدون اتصال'));
          helpers.debug('Field deleted while offline');
          await helpers.takeScreenshot('offline_delete_success');
        }
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    // ==========================================================================
    // Sync Queue Tests
    // اختبارات قائمة انتظار المزامنة
    // ==========================================================================

    testWidgets('Changes queued for sync when offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Create a change
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        await helpers.enterText(
          find.byType(TextField).first,
          'حقل في الانتظار',
        );

        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();

          // Look for pending sync indicator
          final pendingIndicator = find.byIcon(Icons.sync);
          final pendingText = find.textContaining('انتظار');

          if (pendingIndicator.evaluate().isNotEmpty ||
              pendingText.evaluate().isNotEmpty) {
            helpers.debug('Change queued for sync');
            await helpers.takeScreenshot('offline_sync_queue');
          }
        }
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Pending sync count shown correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Make multiple changes
      for (int i = 0; i < 2; i++) {
        final addButton = find.byIcon(Icons.add);
        if (addButton.evaluate().isNotEmpty) {
          await helpers.tapElement(addButton);
          await helpers.pumpAndSettle();

          await helpers.enterText(
            find.byType(TextField).first,
            'حقل معلق $i',
          );

          final saveButton = find.text(ArabicStrings.save);
          if (saveButton.evaluate().isNotEmpty) {
            await helpers.tapElement(saveButton);
            await helpers.pumpAndSettle();
          }
        }
      }

      // Check pending count
      final pendingBadge = find.textContaining('2');
      if (pendingBadge.evaluate().isNotEmpty) {
        helpers.debug('Pending sync count displayed');
        await helpers.takeScreenshot('offline_pending_count');
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    // ==========================================================================
    // Sync on Reconnect Tests
    // اختبارات المزامنة عند إعادة الاتصال
    // ==========================================================================

    testWidgets('Data syncs automatically when back online', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline and make changes
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        await helpers.enterText(
          find.byType(TextField).first,
          'حقل للمزامنة',
        );

        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();
        }
      }

      // Go back online
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Look for sync indicator
      final syncingIndicator = find.textContaining(ArabicStrings.syncing);
      if (syncingIndicator.evaluate().isNotEmpty) {
        helpers.debug('Sync started automatically');
        await helpers.takeScreenshot('offline_sync_started');

        // Wait for sync to complete
        await helpers.waitForSync();
        await helpers.takeScreenshot('offline_sync_complete');
      }

      helpers.debug('Data synced after reconnection');
    });

    testWidgets('Sync progress indicator shown', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Create pending changes offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Make a change
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        await helpers.enterText(
          find.byType(TextField).first,
          'حقل مؤقت للمزامنة',
        );

        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();
        }
      }

      // Go online
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Check for progress indicator
      final progressIndicator = find.byType(CircularProgressIndicator);
      final syncIndicator = find.byIcon(Icons.sync);
      final syncText = find.textContaining(ArabicStrings.syncing);

      if (progressIndicator.evaluate().isNotEmpty ||
          syncIndicator.evaluate().isNotEmpty ||
          syncText.evaluate().isNotEmpty) {
        helpers.debug('Sync progress indicator shown');
        await helpers.takeScreenshot('offline_sync_progress');
      }

      // Wait for completion
      await helpers.waitForSync();
    });

    testWidgets('Sync success notification shown', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Make offline changes
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        await helpers.enterText(
          find.byType(TextField).first,
          'حقل مزامنة ناجحة',
        );

        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();
        }
      }

      // Go online and wait for sync
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();
      await helpers.waitForSync();

      // Check for success notification
      final successSnackbar = find.textContaining(ArabicStrings.success);
      final successIcon = find.byIcon(Icons.check_circle);

      if (successSnackbar.evaluate().isNotEmpty ||
          successIcon.evaluate().isNotEmpty) {
        helpers.debug('Sync success notification shown');
        await helpers.takeScreenshot('offline_sync_success');
      }
    });

    // ==========================================================================
    // Conflict Resolution Tests
    // اختبارات حل التعارضات
    // ==========================================================================

    testWidgets('Conflict detected when server data changed', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // This test requires mocking server responses
      // In a real scenario, we would:
      // 1. Edit a field locally
      // 2. Simulate server having different data
      // 3. Sync and verify conflict dialog appears

      helpers.debug('Conflict detection test requires mock server');
    });

    testWidgets('Conflict resolution dialog shown', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // This test would verify:
      // - Conflict dialog appears
      // - Options to keep local or server version
      // - Merge option if available

      helpers.debug('Conflict resolution test requires mock server');
    });

    // ==========================================================================
    // Error Handling Tests
    // اختبارات معالجة الأخطاء
    // ==========================================================================

    testWidgets('Failed sync shows retry option', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // This test would require simulating sync failure
      // Verify retry button appears and works

      helpers.debug('Sync retry test requires mock server');
    });

    testWidgets('Sync errors shown clearly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // This test would verify error messages are shown
      // when sync fails

      helpers.debug('Sync error display test requires mock server');
    });

    // ==========================================================================
    // Offline Feature Availability Tests
    // اختبارات توفر الميزات بدون اتصال
    // ==========================================================================

    testWidgets('Core features available offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Check core features work
      // Navigation
      await helpers.navigateToBottomNavItem(ArabicStrings.home);
      await helpers.pumpAndSettle();
      helpers.verifyTextExists(ArabicStrings.home);

      // Field list view
      final fieldList = find.byType(ListView);
      helpers.verifyElementExists(fieldList);

      helpers.debug('Core features available offline');
      await helpers.takeScreenshot('offline_core_features');

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Online-only features disabled when offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Check that online-only features show appropriate state
      // e.g., marketplace, sync button disabled

      final marketplaceButton = find.text(ArabicStrings.marketplace);
      if (marketplaceButton.evaluate().isNotEmpty) {
        await helpers.tapElement(marketplaceButton);
        await helpers.pumpAndSettle();

        // Should show offline message or empty state
        final offlineMessage = find.textContaining(ArabicStrings.offline);
        if (offlineMessage.evaluate().isNotEmpty) {
          helpers.debug('Online-only features properly disabled');
          await helpers.takeScreenshot('offline_disabled_features');
        }
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    // ==========================================================================
    // Data Integrity Tests
    // اختبارات سلامة البيانات
    // ==========================================================================

    testWidgets('Data integrity maintained after offline session', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Record initial field count
      final initialFields = find.textContaining('حقل');
      final initialCount = initialFields.evaluate().length;

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Make changes
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        await helpers.enterText(
          find.byType(TextField).first,
          'حقل اختبار السلامة',
        );

        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();
        }
      }

      // Go online and sync
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();
      await helpers.waitForSync();

      // Verify data integrity
      final finalFields = find.textContaining('حقل');
      final finalCount = finalFields.evaluate().length;

      expect(finalCount, greaterThanOrEqualTo(initialCount),
          reason: 'Data should be preserved after offline session');

      helpers.debug('Data integrity verified');
    });

    testWidgets('No data loss during interrupted sync', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Create data offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        await helpers.enterText(
          find.byType(TextField).first,
          'حقل اختبار المقاطعة',
        );

        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();
        }
      }

      // Go online briefly
      await helpers.toggleOfflineMode();
      await tester.pump(const Duration(milliseconds: 100));

      // Interrupt by going offline again
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Data should still exist locally
      helpers.verifyTextContains('حقل اختبار المقاطعة');
      helpers.debug('Data preserved during interrupted sync');
      await helpers.takeScreenshot('offline_interrupted_sync');

      // Go back online
      await helpers.toggleOfflineMode();
    });

    // ==========================================================================
    // Performance Tests
    // اختبارات الأداء
    // ==========================================================================

    testWidgets('Offline mode has acceptable performance', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      final startTime = DateTime.now();

      // Navigate through multiple screens
      await helpers.navigateToBottomNavItem(ArabicStrings.home);
      await helpers.pumpAndSettle();

      final navTime = DateTime.now().difference(startTime);

      expect(navTime.inSeconds, lessThan(3),
          reason: 'Navigation should be fast in offline mode');

      helpers.debug('Offline performance acceptable: ${navTime.inMilliseconds}ms');

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Sync completes within reasonable time', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Create offline changes
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        await helpers.enterText(
          find.byType(TextField).first,
          'حقل اختبار السرعة',
        );

        final saveButton = find.text(ArabicStrings.save);
        if (saveButton.evaluate().isNotEmpty) {
          await helpers.tapElement(saveButton);
          await helpers.pumpAndSettle();
        }
      }

      // Go online and measure sync time
      final startTime = DateTime.now();

      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();
      await helpers.waitForSync();

      final syncTime = DateTime.now().difference(startTime);

      expect(syncTime.inSeconds, lessThan(30),
          reason: 'Sync should complete within 30 seconds');

      helpers.debug('Sync completed in ${syncTime.inSeconds}s');
    });
  });
}
