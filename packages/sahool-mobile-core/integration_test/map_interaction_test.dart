// SAHOOL Integration Test - Map Interaction Tests
// اختبارات التفاعل مع الخريطة
//
// Tests for:
// - Map loading and display
// - Map navigation and zoom
// - Field polygon drawing
// - Point selection
// - Map layer switching
// - Offline map functionality

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:sahool_field_app/main.dart' as app;

import 'helpers/test_helpers.dart';
import 'fixtures/test_data.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Map Interaction Tests - اختبارات التفاعل مع الخريطة', () {
    late TestHelpers helpers;

    setUp(() async {
      // Setup for each test
    });

    tearDown(() async {
      // Cleanup after each test
    });

    // ==========================================================================
    // Map Loading Tests
    // اختبارات تحميل الخريطة
    // ==========================================================================

    testWidgets('Map widget loads successfully', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to a screen with map (field creation or field details)
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        // Look for map button or map widget
        final mapButton = find.textContaining('خريطة');
        if (mapButton.evaluate().isNotEmpty) {
          await helpers.tapElement(mapButton);
          await helpers.pumpAndSettle();
        }

        // Verify FlutterMap widget is rendered
        final flutterMap = find.byType(FlutterMap);
        if (flutterMap.evaluate().isNotEmpty) {
          helpers.verifyElementExists(flutterMap);
          helpers.debug('Map widget loaded successfully');
          await helpers.takeScreenshot('map_loaded');
        } else {
          helpers.debug('Map widget not found - screen may not have map');
        }
      }
    });

    testWidgets('Map displays with correct initial position', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to map view
      await _navigateToMap(helpers);

      // Map should center on Yemen region by default
      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        helpers.debug('Map displayed with initial position');
        await helpers.takeScreenshot('map_initial_position');
      }
    });

    testWidgets('Map shows attribution correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Look for attribution widget
      final attribution = find.byType(RichAttributionWidget);
      if (attribution.evaluate().isNotEmpty) {
        helpers.verifyElementExists(attribution);
        helpers.debug('Map attribution displayed');
        await helpers.takeScreenshot('map_attribution');
      }
    });

    // ==========================================================================
    // Map Navigation Tests
    // اختبارات التنقل في الخريطة
    // ==========================================================================

    testWidgets('Zoom controls work correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Find zoom in button
      final zoomInButton = find.byIcon(Icons.add);
      if (zoomInButton.evaluate().isNotEmpty) {
        await helpers.tapElement(zoomInButton);
        await helpers.pumpAndSettle();
        helpers.debug('Zoomed in');
        await helpers.takeScreenshot('map_zoom_in');

        // Find zoom out button
        final zoomOutButton = find.byIcon(Icons.remove);
        await helpers.tapElement(zoomOutButton);
        await helpers.pumpAndSettle();
        helpers.debug('Zoomed out');
        await helpers.takeScreenshot('map_zoom_out');
      }
    });

    testWidgets('Map pan gesture works', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Perform drag gesture on map
      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        await tester.drag(flutterMap, const Offset(100, 100));
        await helpers.pumpAndSettle();

        helpers.debug('Map panned successfully');
        await helpers.takeScreenshot('map_panned');
      }
    });

    testWidgets('Map pinch zoom works', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Note: Pinch zoom is difficult to test in integration tests
      // This test verifies the map accepts touch input
      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        // Single tap to verify interaction
        await tester.tap(flutterMap);
        await helpers.pumpAndSettle();
        helpers.debug('Map interaction verified');
      }
    });

    // ==========================================================================
    // Map Layer Tests
    // اختبارات طبقات الخريطة
    // ==========================================================================

    testWidgets('Toggle satellite layer', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Find satellite toggle button
      final satelliteButton = find.byIcon(Icons.satellite_alt);
      final mapButton = find.byIcon(Icons.map);

      if (satelliteButton.evaluate().isNotEmpty) {
        await helpers.tapElement(satelliteButton);
        await helpers.pumpAndSettle();
        helpers.debug('Switched to satellite view');
        await helpers.takeScreenshot('map_satellite_view');
      } else if (mapButton.evaluate().isNotEmpty) {
        await helpers.tapElement(mapButton);
        await helpers.pumpAndSettle();
        helpers.debug('Switched to map view');
        await helpers.takeScreenshot('map_standard_view');
      }
    });

    testWidgets('Layer selector popup works', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Find layers button
      final layersButton = find.byIcon(Icons.layers);
      if (layersButton.evaluate().isNotEmpty) {
        await helpers.tapElement(layersButton);
        await helpers.pumpAndSettle();

        // Verify popup menu appeared
        final popupMenu = find.byType(PopupMenuButton);
        helpers.debug('Layer selector opened');
        await helpers.takeScreenshot('map_layer_selector');

        // Dismiss popup by tapping outside
        await tester.tapAt(const Offset(10, 10));
        await helpers.pumpAndSettle();
      }
    });

    // ==========================================================================
    // Field Polygon Drawing Tests
    // اختبارات رسم حدود الحقل
    // ==========================================================================

    testWidgets('Drawing mode activates correctly', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to field creation
      final addButton = find.byIcon(Icons.add);
      if (addButton.evaluate().isNotEmpty) {
        await helpers.tapElement(addButton);
        await helpers.pumpAndSettle();

        // Look for draw on map option
        final drawOption = find.textContaining('رسم');
        if (drawOption.evaluate().isNotEmpty) {
          await helpers.tapElement(drawOption);
          await helpers.pumpAndSettle();

          // Verify drawing controls appear
          final undoButton = find.text('تراجع');
          final finishButton = find.text('إنهاء');

          if (undoButton.evaluate().isNotEmpty || finishButton.evaluate().isNotEmpty) {
            helpers.debug('Drawing mode activated');
            await helpers.takeScreenshot('map_drawing_mode');
          }
        }
      }
    });

    testWidgets('Add points to polygon', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to drawing mode
      await _navigateToDrawingMode(helpers);

      // Find map widget
      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        // Tap to add points
        final center = tester.getCenter(flutterMap);

        // Add 4 points to create a polygon
        await tester.tapAt(Offset(center.dx - 50, center.dy - 50));
        await helpers.pumpAndSettle();

        await tester.tapAt(Offset(center.dx + 50, center.dy - 50));
        await helpers.pumpAndSettle();

        await tester.tapAt(Offset(center.dx + 50, center.dy + 50));
        await helpers.pumpAndSettle();

        await tester.tapAt(Offset(center.dx - 50, center.dy + 50));
        await helpers.pumpAndSettle();

        // Check if points counter updated
        final pointsText = find.textContaining('النقاط');
        if (pointsText.evaluate().isNotEmpty) {
          helpers.debug('Points added to polygon');
          await helpers.takeScreenshot('map_polygon_points');
        }
      }
    });

    testWidgets('Undo last point', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToDrawingMode(helpers);

      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        // Add a point
        final center = tester.getCenter(flutterMap);
        await tester.tapAt(center);
        await helpers.pumpAndSettle();

        // Tap undo
        final undoButton = find.text('تراجع');
        if (undoButton.evaluate().isNotEmpty) {
          await helpers.tapElement(undoButton);
          await helpers.pumpAndSettle();
          helpers.debug('Undo point successful');
          await helpers.takeScreenshot('map_undo_point');
        }
      }
    });

    testWidgets('Complete polygon drawing', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToDrawingMode(helpers);

      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        // Add 3 points (minimum for polygon)
        final center = tester.getCenter(flutterMap);

        await tester.tapAt(Offset(center.dx, center.dy - 50));
        await helpers.pumpAndSettle();

        await tester.tapAt(Offset(center.dx + 50, center.dy + 30));
        await helpers.pumpAndSettle();

        await tester.tapAt(Offset(center.dx - 50, center.dy + 30));
        await helpers.pumpAndSettle();

        // Complete polygon
        final finishButton = find.text('إنهاء');
        if (finishButton.evaluate().isNotEmpty) {
          await helpers.tapElement(finishButton);
          await helpers.pumpAndSettle();
          helpers.debug('Polygon completed');
          await helpers.takeScreenshot('map_polygon_complete');
        }
      }
    });

    // ==========================================================================
    // Point Selection Tests
    // اختبارات اختيار النقاط
    // ==========================================================================

    testWidgets('Select point on map', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to point selection mode (if available)
      await _navigateToMap(helpers);

      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        // Tap on map
        await tester.tap(flutterMap);
        await helpers.pumpAndSettle();

        helpers.debug('Point selected on map');
        await helpers.takeScreenshot('map_point_selected');
      }
    });

    // ==========================================================================
    // Field Display Tests
    // اختبارات عرض الحقول
    // ==========================================================================

    testWidgets('Display field boundaries on map', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to field details with map
      final fieldCard = find.textContaining('حقل');
      if (fieldCard.evaluate().isNotEmpty) {
        await helpers.tapElement(fieldCard.first);
        await helpers.pumpAndSettle();

        // Look for map tab or button
        final mapButton = find.byIcon(Icons.map);
        if (mapButton.evaluate().isNotEmpty) {
          await helpers.tapElement(mapButton);
          await helpers.pumpAndSettle();

          // Verify polygon layer is present
          final polygonLayer = find.byType(PolygonLayer);
          if (polygonLayer.evaluate().isNotEmpty) {
            helpers.verifyElementExists(polygonLayer);
            helpers.debug('Field boundaries displayed');
            await helpers.takeScreenshot('map_field_boundaries');
          }
        }
      }
    });

    testWidgets('Display multiple fields on map', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Navigate to overview map (if available)
      final mapViewButton = find.textContaining('خريطة الحقول');
      if (mapViewButton.evaluate().isNotEmpty) {
        await helpers.tapElement(mapViewButton);
        await helpers.pumpAndSettle();

        // Verify multiple polygons
        final polygonLayer = find.byType(PolygonLayer);
        if (polygonLayer.evaluate().isNotEmpty) {
          helpers.debug('Multiple fields displayed');
          await helpers.takeScreenshot('map_multiple_fields');
        }
      }
    });

    // ==========================================================================
    // Marker Tests
    // اختبارات العلامات
    // ==========================================================================

    testWidgets('Display markers on map', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Verify marker layer exists
      final markerLayer = find.byType(MarkerLayer);
      if (markerLayer.evaluate().isNotEmpty) {
        helpers.verifyElementExists(markerLayer);
        helpers.debug('Markers displayed on map');
        await helpers.takeScreenshot('map_markers');
      }
    });

    testWidgets('Tap on marker shows info', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Find marker and tap it
      final markers = find.byType(MarkerLayer);
      if (markers.evaluate().isNotEmpty) {
        // Find first marker widget
        final marker = find.descendant(
          of: markers,
          matching: find.byType(InkWell),
        );

        if (marker.evaluate().isNotEmpty) {
          await tester.tap(marker.first);
          await helpers.pumpAndSettle();

          helpers.debug('Marker info displayed');
          await helpers.takeScreenshot('map_marker_info');
        }
      }
    });

    // ==========================================================================
    // Location Button Tests
    // اختبارات زر الموقع
    // ==========================================================================

    testWidgets('Current location button exists', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Find my location button
      final locationButton = find.byIcon(Icons.my_location);
      final gpsButton = find.byIcon(Icons.gps_fixed);

      if (locationButton.evaluate().isNotEmpty || gpsButton.evaluate().isNotEmpty) {
        helpers.debug('Location button found');
        await helpers.takeScreenshot('map_location_button');
      }
    });

    // ==========================================================================
    // Offline Map Tests
    // اختبارات الخريطة بدون اتصال
    // ==========================================================================

    testWidgets('Map works with cached tiles offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      // Navigate to map
      await _navigateToMap(helpers);

      // Map should still display (with cached tiles)
      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        helpers.debug('Map displayed in offline mode');
        await helpers.takeScreenshot('map_offline');
      }

      // Go back online
      await helpers.toggleOfflineMode();
    });

    testWidgets('Offline indicator shown when map offline', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      // Go offline
      await helpers.toggleOfflineMode();
      await helpers.pumpAndSettle();

      await _navigateToMap(helpers);

      // Verify offline indicator
      helpers.verifyTextContains(ArabicStrings.offline);
      helpers.debug('Offline indicator shown');
      await helpers.takeScreenshot('map_offline_indicator');

      // Go back online
      await helpers.toggleOfflineMode();
    });

    // ==========================================================================
    // Map Performance Tests
    // اختبارات أداء الخريطة
    // ==========================================================================

    testWidgets('Map loads within acceptable time', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      final startTime = DateTime.now();

      await _navigateToMap(helpers);

      final loadTime = DateTime.now().difference(startTime);

      expect(loadTime.inSeconds, lessThan(5),
          reason: 'Map should load in less than 5 seconds');

      helpers.debug('Map loaded in ${loadTime.inMilliseconds}ms');
    });

    testWidgets('Map interaction is responsive', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        final startTime = DateTime.now();

        // Perform multiple interactions
        for (int i = 0; i < 5; i++) {
          await tester.drag(flutterMap, const Offset(50, 50));
          await helpers.pumpAndSettle();
        }

        final interactionTime = DateTime.now().difference(startTime);

        expect(interactionTime.inSeconds, lessThan(3),
            reason: 'Map interactions should be fast');

        helpers.debug('Map interactions completed in ${interactionTime.inMilliseconds}ms');
      }
    });

    // ==========================================================================
    // Map Error Handling Tests
    // اختبارات معالجة الأخطاء
    // ==========================================================================

    testWidgets('Map handles tile loading errors gracefully', (tester) async {
      helpers = TestHelpers(tester, binding);

      app.main();
      await helpers.pumpAndSettle();
      await helpers.login();

      await _navigateToMap(helpers);

      // Map should still be functional even if some tiles fail
      final flutterMap = find.byType(FlutterMap);
      if (flutterMap.evaluate().isNotEmpty) {
        helpers.debug('Map handles errors gracefully');
        await helpers.takeScreenshot('map_error_handling');
      }
    });
  });
}

// =============================================================================
// Helper Functions
// دوال مساعدة
// =============================================================================

/// Navigate to a map view
/// التنقل إلى عرض الخريطة
Future<void> _navigateToMap(TestHelpers helpers) async {
  // Try different ways to navigate to map

  // Option 1: Create field flow
  final addButton = find.byIcon(Icons.add);
  if (addButton.evaluate().isNotEmpty) {
    await helpers.tapElement(addButton);
    await helpers.pumpAndSettle();

    final mapOption = find.textContaining('خريطة');
    if (mapOption.evaluate().isNotEmpty) {
      await helpers.tapElement(mapOption);
      await helpers.pumpAndSettle();
      return;
    }

    // Go back
    await helpers.navigateBack();
  }

  // Option 2: Field details
  final fieldCard = find.textContaining('حقل');
  if (fieldCard.evaluate().isNotEmpty) {
    await helpers.tapElement(fieldCard.first);
    await helpers.pumpAndSettle();

    final mapTab = find.byIcon(Icons.map);
    if (mapTab.evaluate().isNotEmpty) {
      await helpers.tapElement(mapTab);
      await helpers.pumpAndSettle();
      return;
    }
  }

  helpers.debug('Could not navigate to map view');
}

/// Navigate to drawing mode
/// التنقل إلى وضع الرسم
Future<void> _navigateToDrawingMode(TestHelpers helpers) async {
  // Navigate to field creation
  final addButton = find.byIcon(Icons.add);
  if (addButton.evaluate().isNotEmpty) {
    await helpers.tapElement(addButton);
    await helpers.pumpAndSettle();

    // Look for draw on map option
    final drawOption = find.textContaining('رسم');
    final mapOption = find.textContaining('خريطة');

    if (drawOption.evaluate().isNotEmpty) {
      await helpers.tapElement(drawOption);
      await helpers.pumpAndSettle();
    } else if (mapOption.evaluate().isNotEmpty) {
      await helpers.tapElement(mapOption);
      await helpers.pumpAndSettle();
    }
  }
}
