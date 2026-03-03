/// Map Screen Tests - اختبارات شاشة الخريطة
///
/// Tests for the improved MapScreen:
/// - ConsumerStatefulWidget with Riverpod
/// - MapController integration
/// - Layer switching (Satellite/Map/NDVI/Moisture)
/// - Search functionality
/// - Quick filters
/// - Zoom controls
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/map_home/ui/map_screen.dart';

void main() {
  Widget createTestWidget() {
    return ProviderScope(
      child: MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: const MapScreen(),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Basic Rendering Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MapScreen Rendering', () {
    testWidgets('should render without errors', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pump();

      // The screen should be displayed
      expect(find.byType(MapScreen), findsOneWidget);
    });

    testWidgets('should show layer selector icons', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pump();

      // Layer icons should be present
      expect(find.byIcon(Icons.satellite_alt), findsWidgets);
      expect(find.byIcon(Icons.map), findsWidgets);
      expect(find.byIcon(Icons.grass), findsWidgets);
      expect(find.byIcon(Icons.water_drop), findsWidgets);
    });

    testWidgets('should show quick filter chips', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pump();

      // Tap filter button to expand search panel and reveal filter chips
      await tester.tap(find.byIcon(Icons.filter_list));
      await tester.pumpAndSettle();

      // Quick filter labels
      expect(find.text('الكل'), findsWidgets);
      expect(find.text('نشط'), findsWidgets);
      expect(find.text('تنبيه'), findsWidgets);
      expect(find.text('حصاد'), findsWidgets);
    });

    testWidgets('should show zoom control buttons', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pump();

      expect(find.byIcon(Icons.add), findsWidgets);
      expect(find.byIcon(Icons.remove), findsWidgets);
      expect(find.byIcon(Icons.my_location), findsWidgets);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Search Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MapScreen Search', () {
    testWidgets('should have search icon', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pump();

      expect(find.byIcon(Icons.search), findsWidgets);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync and Status Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MapScreen Status', () {
    testWidgets('should show sync indicator', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pump();

      // Sync indicator should be present (cloud_upload when pendingSync > 0)
      expect(find.byIcon(Icons.cloud_upload), findsWidgets);
    });
  });
}
