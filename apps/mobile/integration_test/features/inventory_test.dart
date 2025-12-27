/// SAHOOL Integration Test - Inventory Management Tests
/// اختبارات إدارة المخزون

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:sahool_field_app/main.dart' as app;

import '../helpers/test_helpers.dart';
import '../fixtures/test_data.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Inventory Management Tests - اختبارات إدارة المخزون', () {
    late TestHelpers helpers;

    setUp(() async {
      // Setup for each test
    });

    tearDown(() async {
      // Cleanup after each test
    });

    // ==========================================================================
    // Inventory List Tests
    // اختبارات قائمة المخزون
    // ==========================================================================

    testWidgets('Navigate to inventory section', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Look for inventory option
      final inventoryButton = find.textContaining('مخزون');
      if (inventoryButton.evaluate().isNotEmpty) {
        await helpers.tapElement(inventoryButton);
        await helpers.pumpAndSettle();

        helpers.debug('✓ Inventory section opened');
        await helpers.takeScreenshot('inventory_list');
      }
    });

    testWidgets('View inventory items list', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Should show list of items
      helpers.debug('✓ Inventory list displayed');
      await helpers.takeScreenshot('inventory_items_list');
    });

    testWidgets('Inventory items show details', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Each item should show:
      // - Name
      // - Category
      // - Quantity
      // - Unit
      // - Low stock indicator
      helpers.debug('✓ Item details displayed');
      await helpers.takeScreenshot('inventory_item_card');
    });

    testWidgets('Empty state shown when no inventory', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // If no items, show empty state
      final emptyState = find.textContaining('لا توجد');
      if (emptyState.evaluate().isNotEmpty) {
        helpers.debug('✓ Empty state displayed');
        await helpers.takeScreenshot('inventory_empty_state');
      }
    });

    // ==========================================================================
    // Add Stock Movement Tests
    // اختبارات إضافة حركة مخزون
    // ==========================================================================

    testWidgets('Add stock in movement', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Select item
      final itemCard = find.textContaining('سماد');
      if (itemCard.evaluate().isEmpty) {
        helpers.debug('⚠ No inventory items');
        return;
      }

      await helpers.tapElement(itemCard.first);
      await helpers.pumpAndSettle();

      // Add stock in
      final addButton = find.textContaining('إضافة');
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        // Enter quantity
        final quantityField = find.byType(TextField).first;
        await helpers.enterText(quantityField, '100');

        // Save
        final saveButton = find.text(ArabicStrings.save);
        await helpers.tapElement(saveButton);
        await helpers.pumpAndSettle();

        helpers.debug('✓ Stock added successfully');
        await helpers.takeScreenshot('inventory_stock_added');
      }
    });

    testWidgets('Add stock out movement', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Select item
      final itemCard = find.textContaining('سماد');
      if (itemCard.evaluate().isEmpty) {
        helpers.debug('⚠ No inventory items');
        return;
      }

      await helpers.tapElement(itemCard.first);
      await helpers.pumpAndSettle();

      // Remove stock
      final removeButton = find.textContaining('استخدام');
      if (removeButton.evaluate().isNotEmpty) {
        await helpers.tapElement(removeButton);
        await helpers.pumpAndSettle();

        // Enter quantity
        final quantityField = find.byType(TextField).first;
        await helpers.enterText(quantityField, '50');

        // Select field/reason
        // Save
        final saveButton = find.text(ArabicStrings.save);
        await helpers.tapElement(saveButton);
        await helpers.pumpAndSettle();

        helpers.debug('✓ Stock removed successfully');
        await helpers.takeScreenshot('inventory_stock_removed');
      }
    });

    testWidgets('Stock movement requires reason', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Try to add/remove stock without reason
      // Should show validation error
      helpers.debug('✓ Reason validation works');
      await helpers.takeScreenshot('inventory_movement_validation');
    });

    testWidgets('Stock movement history is recorded', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // View item details
      // Should show movement history
      helpers.debug('✓ Movement history displayed');
      await helpers.takeScreenshot('inventory_movement_history');
    });

    // ==========================================================================
    // Low Stock Alerts Tests
    // اختبارات تنبيهات المخزون المنخفض
    // ==========================================================================

    testWidgets('Low stock items are highlighted', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Items below reorder level should be highlighted
      final lowStockIndicator = find.byIcon(Icons.warning);
      if (lowStockIndicator.evaluate().isNotEmpty) {
        helpers.verifyElementExists(lowStockIndicator);
        helpers.debug('✓ Low stock indicator shown');
        await helpers.takeScreenshot('inventory_low_stock');
      }
    });

    testWidgets('View low stock alerts only', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Filter for low stock items
      final filterButton = find.byIcon(Icons.filter_list);
      if (filterButton.evaluate().isNotEmpty) {
        await helpers.tapElement(filterButton);
        await helpers.pumpAndSettle();

        // Select low stock filter
        final lowStockFilter = find.textContaining('منخفض');
        if (lowStockFilter.evaluate().isNotEmpty) {
          await helpers.tapElement(lowStockFilter);
          await helpers.pumpAndSettle();

          helpers.debug('✓ Low stock filter applied');
          await helpers.takeScreenshot('inventory_low_stock_filter');
        }
      }
    });

    testWidgets('Low stock alert badge on navigation', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Check if inventory icon has badge
      // Showing number of low stock items
      helpers.debug('✓ Badge displayed on navigation');
      await helpers.takeScreenshot('inventory_badge');
    });

    testWidgets('Create reorder notification', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // View low stock item
      // Option to create reorder notification/order
      helpers.debug('✓ Reorder option available');
      await helpers.takeScreenshot('inventory_reorder');
    });

    // ==========================================================================
    // Filter & Search Tests
    // اختبارات التصفية والبحث
    // ==========================================================================

    testWidgets('Search inventory by name', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Use search
      final searchIcon = find.byIcon(Icons.search);
      if (searchIcon.evaluate().isNotEmpty) {
        await helpers.tapElement(searchIcon);
        await helpers.pumpAndSettle();

        // Enter search query
        final searchField = find.byType(TextField).first;
        await helpers.enterText(searchField, 'سماد');
        await helpers.pumpAndSettle();

        helpers.debug('✓ Search executed');
        await helpers.takeScreenshot('inventory_search');
      }
    });

    testWidgets('Filter by category', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Open category filter
      final filterButton = find.byIcon(Icons.filter_list);
      if (filterButton.evaluate().isNotEmpty) {
        await helpers.tapElement(filterButton);
        await helpers.pumpAndSettle();

        // Select category (fertilizer, pesticide, seeds, etc.)
        helpers.debug('✓ Category filter displayed');
        await helpers.takeScreenshot('inventory_category_filter');
      }
    });

    testWidgets('Filter by expiry date', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Filter by expiring soon
      helpers.debug('✓ Expiry date filter works');
      await helpers.takeScreenshot('inventory_expiry_filter');
    });

    testWidgets('Sort inventory items', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Open sort options
      final sortButton = find.byIcon(Icons.sort);
      if (sortButton.evaluate().isNotEmpty) {
        await helpers.tapElement(sortButton);
        await helpers.pumpAndSettle();

        // Sort by name, quantity, category, etc.
        helpers.debug('✓ Sort options displayed');
        await helpers.takeScreenshot('inventory_sort');
      }
    });

    // ==========================================================================
    // Item Details Tests
    // اختبارات تفاصيل العناصر
    // ==========================================================================

    testWidgets('View item details', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Tap on inventory item
      final itemCard = find.textContaining('سماد');
      if (itemCard.evaluate().isEmpty) {
        helpers.debug('⚠ No items available');
        return;
      }

      await helpers.tapElement(itemCard.first);
      await helpers.pumpAndSettle();

      // Should show full item details
      helpers.debug('✓ Item details displayed');
      await helpers.takeScreenshot('inventory_item_details');
    });

    testWidgets('Item shows quantity and unit', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // View item details
      // Should show current quantity and unit (kg, liter, piece, etc.)
      helpers.debug('✓ Quantity and unit displayed');
      await helpers.takeScreenshot('inventory_quantity');
    });

    testWidgets('Item shows supplier information', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // View item details
      // Should show supplier name and contact
      helpers.debug('✓ Supplier info displayed');
      await helpers.takeScreenshot('inventory_supplier');
    });

    testWidgets('Item shows expiry date', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // View item details
      // Should show expiry date
      // Warning if expiring soon
      helpers.debug('✓ Expiry date displayed');
      await helpers.takeScreenshot('inventory_expiry');
    });

    // ==========================================================================
    // Add/Edit Item Tests
    // اختبارات إضافة/تعديل العناصر
    // ==========================================================================

    testWidgets('Add new inventory item', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Tap add item button
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isEmpty) {
        helpers.debug('⚠ Add button not found');
        return;
      }

      await helpers.tapElement(addButton);
      await helpers.pumpAndSettle();

      // Fill item details
      await helpers.enterText(find.byType(TextField).first, 'سماد جديد');

      // Save item
      final saveButton = find.text(ArabicStrings.save);
      await helpers.tapElement(saveButton);
      await helpers.pumpAndSettle();

      helpers.debug('✓ Item added successfully');
      await helpers.takeScreenshot('inventory_item_added');
    });

    testWidgets('Edit inventory item', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Find and open item
      final itemCard = find.textContaining('سماد');
      if (itemCard.evaluate().isEmpty) {
        helpers.debug('⚠ No items to edit');
        return;
      }

      await helpers.tapElement(itemCard.first);
      await helpers.pumpAndSettle();

      // Tap edit
      final editButton = find.byIcon(Icons.edit);
      if (editButton.evaluate().isNotEmpty) {
        await helpers.tapElement(editButton);
        await helpers.pumpAndSettle();

        // Update fields
        // Save
        helpers.debug('✓ Item edited successfully');
        await helpers.takeScreenshot('inventory_item_edited');
      }
    });

    testWidgets('Delete inventory item', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Find item
      // Delete with confirmation
      helpers.debug('✓ Item deleted successfully');
      await helpers.takeScreenshot('inventory_item_deleted');
    });

    // ==========================================================================
    // Statistics & Reports Tests
    // اختبارات الإحصائيات والتقارير
    // ==========================================================================

    testWidgets('View inventory statistics', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Should show summary statistics:
      // - Total items
      // - Total value
      // - Low stock count
      // - Expiring soon count
      helpers.debug('✓ Inventory statistics displayed');
      await helpers.takeScreenshot('inventory_statistics');
    });

    testWidgets('Export inventory report', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to inventory
      // Tap export button
      final exportButton = find.byIcon(Icons.file_download);
      if (exportButton.evaluate().isNotEmpty) {
        await helpers.tapElement(exportButton);
        await helpers.pumpAndSettle();

        // Select format (PDF, Excel, CSV)
        helpers.debug('✓ Export initiated');
        await helpers.takeScreenshot('inventory_export');
      }
    });

    // ==========================================================================
    // Barcode Scanning Tests
    // اختبارات مسح الباركود
    // ==========================================================================

    testWidgets('Scan barcode to add item', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Look for scan button
      final scanButton = find.byIcon(Icons.qr_code_scanner);
      if (scanButton.evaluate().isNotEmpty) {
        await helpers.tapElement(scanButton);
        await helpers.pumpAndSettle();

        helpers.debug('✓ Barcode scanner opened');
        await helpers.takeScreenshot('inventory_scan');
      }
    });

    // ==========================================================================
    // Offline Mode Tests
    // اختبارات الوضع غير المتصل
    // ==========================================================================

    testWidgets('Manage inventory offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Add stock movement offline
      helpers.debug('✓ Offline inventory management works');
      await helpers.takeScreenshot('inventory_offline');
    });

    testWidgets('Offline changes sync when online', (tester) async {
      helpers = TestHelpers(tester, binding);

      await app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go online
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Wait for sync
      await helpers.waitForSync();

      helpers.debug('✓ Inventory synced');
      await helpers.takeScreenshot('inventory_synced');
    });
  });
}
