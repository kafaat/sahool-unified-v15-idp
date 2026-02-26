/// Sector Drawing Tool Tests - اختبارات أداة رسم القطاعات
///
/// Tests for undo/redo stacks, sector creation, equal division,
/// and widget rendering.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/pivot_models.dart';
import 'package:sahool_field_app/features/pivot_irrigation/presentation/widgets/sector_drawing_tool.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // Widget Rendering Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SectorDrawingTool Widget', () {
    late List<PivotSector> capturedSectors;

    setUp(() {
      capturedSectors = [];
    });

    Widget createTestWidget({
      List<PivotSector>? initialSectors,
      bool drawingEnabled = true,
    }) {
      return MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: SectorDrawingTool(
              initialSectors: initialSectors,
              onSectorsChanged: (sectors) => capturedSectors = sectors,
              drawingEnabled: drawingEnabled,
              size: 300,
            ),
          ),
        ),
      );
    }

    testWidgets('should render control buttons when drawing enabled',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Should show all 5 control buttons
      expect(find.text('إضافة قطاع'), findsOneWidget);
      expect(find.text('تقسيم متساوي'), findsOneWidget);
      expect(find.text('مسح الكل'), findsOneWidget);
      expect(find.text('تراجع'), findsOneWidget);
      expect(find.text('إعادة'), findsOneWidget);
    });

    testWidgets('should NOT render controls when drawing disabled',
        (tester) async {
      await tester.pumpWidget(createTestWidget(drawingEnabled: false));
      await tester.pumpAndSettle();

      expect(find.text('إضافة قطاع'), findsNothing);
    });

    testWidgets('should render sector list when initial sectors provided',
        (tester) async {
      final sectors = [
        const PivotSector(
          id: 'sector_1',
          sectorNumber: 1,
          nameAr: 'قطاع 1',
          startAngle: 0,
          endAngle: 90,
          color: '#4CAF50',
        ),
        const PivotSector(
          id: 'sector_2',
          sectorNumber: 2,
          nameAr: 'قطاع 2',
          startAngle: 90,
          endAngle: 180,
          color: '#8BC34A',
        ),
      ];

      await tester.pumpWidget(createTestWidget(initialSectors: sectors));
      await tester.pumpAndSettle();

      expect(find.text('قطاع 1'), findsOneWidget);
      expect(find.text('قطاع 2'), findsOneWidget);
      // Angle display
      expect(find.textContaining('0°'), findsWidgets);
      expect(find.textContaining('90°'), findsWidgets);
    });

    testWidgets('should toggle add sector mode on tap', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Tap the add sector button
      await tester.tap(find.text('إضافة قطاع'));
      await tester.pumpAndSettle();

      // The button should become active (visual change handled by painter)
      // Verify button is still there
      expect(find.text('إضافة قطاع'), findsOneWidget);
    });

    testWidgets('should open equal division dialog', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      await tester.tap(find.text('تقسيم متساوي'));
      await tester.pumpAndSettle();

      // Dialog should appear
      expect(find.text('اختر عدد القطاعات:'), findsOneWidget);
      expect(find.text('تطبيق'), findsOneWidget);
      expect(find.text('إلغاء'), findsOneWidget);
    });

    testWidgets('should create equal sectors from dialog', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Open equal division dialog
      await tester.tap(find.text('تقسيم متساوي'));
      await tester.pumpAndSettle();

      // Apply default 8 sectors
      await tester.tap(find.text('تطبيق'));
      await tester.pumpAndSettle();

      // Should have created 8 equal sectors
      expect(capturedSectors.length, equals(8));

      // Each sector should be 45 degrees
      for (int i = 0; i < 8; i++) {
        expect(capturedSectors[i].sectorNumber, equals(i + 1));
        expect(capturedSectors[i].startAngle, closeTo(i * 45.0, 0.01));
        expect(capturedSectors[i].endAngle, closeTo((i + 1) * 45.0, 0.01));
      }
    });

    testWidgets('should show delete confirmation dialog', (tester) async {
      final sectors = [
        const PivotSector(
          id: 'sector_1',
          sectorNumber: 1,
          nameAr: 'قطاع 1',
          startAngle: 0,
          endAngle: 90,
          color: '#4CAF50',
        ),
      ];

      await tester.pumpWidget(createTestWidget(initialSectors: sectors));
      await tester.pumpAndSettle();

      // Find and tap delete button
      await tester.tap(find.byIcon(Icons.delete).first);
      await tester.pumpAndSettle();

      // Confirmation dialog
      expect(find.text('حذف القطاع؟'), findsOneWidget);
    });

    testWidgets('clear all should show confirmation and empty sectors',
        (tester) async {
      final sectors = [
        const PivotSector(
          id: 'sector_1',
          sectorNumber: 1,
          nameAr: 'قطاع 1',
          startAngle: 0,
          endAngle: 180,
          color: '#4CAF50',
        ),
      ];

      await tester.pumpWidget(createTestWidget(initialSectors: sectors));
      await tester.pumpAndSettle();

      // Tap clear all
      await tester.tap(find.text('مسح الكل'));
      await tester.pumpAndSettle();

      // Confirm dialog
      expect(find.text('مسح جميع القطاعات؟'), findsOneWidget);

      // Confirm
      await tester.tap(find.widgetWithText(ElevatedButton, 'مسح الكل'));
      await tester.pumpAndSettle();

      expect(capturedSectors, isEmpty);
    });

    testWidgets('undo should restore previous sector state after equal division',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Create equal sectors
      await tester.tap(find.text('تقسيم متساوي'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('تطبيق'));
      await tester.pumpAndSettle();

      expect(capturedSectors.length, equals(8));

      // Undo should restore to empty (since we started with no sectors)
      await tester.tap(find.text('تراجع'));
      await tester.pumpAndSettle();

      expect(capturedSectors, isEmpty);
    });

    testWidgets('redo should restore sectors after undo', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Create equal sectors
      await tester.tap(find.text('تقسيم متساوي'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('تطبيق'));
      await tester.pumpAndSettle();
      expect(capturedSectors.length, equals(8));

      // Undo
      await tester.tap(find.text('تراجع'));
      await tester.pumpAndSettle();
      expect(capturedSectors, isEmpty);

      // Redo
      await tester.tap(find.text('إعادة'));
      await tester.pumpAndSettle();
      expect(capturedSectors.length, equals(8));
    });

    testWidgets('sector list item should be tappable for selection',
        (tester) async {
      final sectors = [
        const PivotSector(
          id: 'sector_1',
          sectorNumber: 1,
          nameAr: 'قطاع 1',
          startAngle: 0,
          endAngle: 120,
          color: '#4CAF50',
        ),
        const PivotSector(
          id: 'sector_2',
          sectorNumber: 2,
          nameAr: 'قطاع 2',
          startAngle: 120,
          endAngle: 240,
          color: '#8BC34A',
        ),
      ];

      await tester.pumpWidget(createTestWidget(initialSectors: sectors));
      await tester.pumpAndSettle();

      // Tap on first sector item
      await tester.tap(find.text('قطاع 1'));
      await tester.pumpAndSettle();

      // Sector should be selectable (visual change in card color)
      expect(find.text('قطاع 1'), findsOneWidget);
    });

    testWidgets('edit button should open edit sheet', (tester) async {
      final sectors = [
        const PivotSector(
          id: 'sector_1',
          sectorNumber: 1,
          nameAr: 'قطاع 1',
          startAngle: 0,
          endAngle: 90,
          color: '#4CAF50',
        ),
      ];

      await tester.pumpWidget(createTestWidget(initialSectors: sectors));
      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.edit).first);
      await tester.pumpAndSettle();

      // Edit sheet should show
      expect(find.text('تعديل قطاع 1'), findsOneWidget);
      expect(find.text('اسم القطاع'), findsOneWidget);
      expect(find.text('زاوية البداية'), findsOneWidget);
      expect(find.text('زاوية النهاية'), findsOneWidget);
      expect(find.text('لون القطاع'), findsOneWidget);
      expect(find.text('حفظ التغييرات'), findsOneWidget);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PivotSector Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('PivotSector Model', () {
    test('should create with required fields', () {
      const sector = PivotSector(
        id: 'test_1',
        sectorNumber: 1,
        startAngle: 0,
        endAngle: 90,
      );

      expect(sector.id, equals('test_1'));
      expect(sector.sectorNumber, equals(1));
      expect(sector.startAngle, equals(0));
      expect(sector.endAngle, equals(90));
      expect(sector.color, equals('#4CAF50')); // default
      expect(sector.isEnabled, isTrue); // default
      expect(sector.irrigationDepthMm, equals(25)); // default
    });

    test('copyWith should preserve unchanged fields', () {
      const original = PivotSector(
        id: 'test_1',
        sectorNumber: 1,
        nameAr: 'قطاع 1',
        startAngle: 0,
        endAngle: 90,
        color: '#4CAF50',
      );

      final modified = original.copyWith(endAngle: 120);
      expect(modified.id, equals('test_1'));
      expect(modified.sectorNumber, equals(1));
      expect(modified.nameAr, equals('قطاع 1'));
      expect(modified.startAngle, equals(0));
      expect(modified.endAngle, equals(120));
      expect(modified.color, equals('#4CAF50'));
    });

    test('angleSpan should calculate correct span', () {
      const sector = PivotSector(
        id: 'test_1',
        sectorNumber: 1,
        startAngle: 45,
        endAngle: 135,
      );

      expect(sector.angleSpan, equals(90));
    });
  });
}
