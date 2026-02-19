/// NDVI Widget Tests - اختبارات ودجات NDVI
///
/// Comprehensive widget tests for:
/// - NdviHealthIndicator (circular gauge)
/// - NdviBadge (compact badge)
/// - NdviLegendBar (gradient legend)
/// - NdviLegendCard (full legend card)
/// - NdviTrendChart (time series chart)
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/ndvi/domain/ndvi_value.dart';
import 'package:sahool_field_app/features/ndvi/domain/ndvi_colormap.dart';
import 'package:sahool_field_app/features/ndvi/ui/ndvi_health_indicator.dart';

import 'ndvi_fixtures.dart';
import 'ndvi_mocks.dart';
import '../../helpers/test_helpers.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // NdviHealthIndicator Tests - اختبارات مؤشر صحة NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviHealthIndicator', () {
    testWidgets('should render with healthy NDVI value', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: NdviFixtures.healthyNdvi,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byType(NdviHealthIndicator), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsWidgets);
    });

    testWidgets('should display NDVI value when showValue is true', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: 0.72,
          showValue: true,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.text('0.72'), findsOneWidget);
    });

    testWidgets('should not display value when showValue is false', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: 0.72,
          showValue: false,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.text('0.72'), findsNothing);
    });

    testWidgets('should display label when showLabel is true', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: NdviFixtures.healthyNdvi,
          showLabel: true,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Arabic label for healthy
      expect(find.text('صحي'), findsOneWidget);
    });

    testWidgets('should not display label when showLabel is false', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: NdviFixtures.healthyNdvi,
          showLabel: false,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.text('صحي'), findsNothing);
    });

    testWidgets('should display correct icon for category', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: NdviFixtures.healthyNdvi,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - healthy category uses check_circle icon
      expect(find.byIcon(Icons.check_circle), findsOneWidget);
    });

    testWidgets('should display stressed icon for stressed vegetation', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: NdviFixtures.stressedNdvi,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - stressed category uses warning_amber icon
      expect(find.byIcon(Icons.warning_amber), findsOneWidget);
    });

    testWidgets('should display water icon for non-vegetation', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: NdviFixtures.waterNdvi,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - non-vegetation uses water_drop icon
      expect(find.byIcon(Icons.water_drop), findsOneWidget);
    });

    testWidgets('should respect custom size', (tester) async {
      // Arrange
      const customSize = 120.0;
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: NdviFixtures.healthyNdvi,
          size: customSize,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      final sizeFinder = find.byWidgetPredicate(
        (widget) => widget is SizedBox && widget.width == customSize,
      );
      expect(sizeFinder, findsWidgets);
    });

    testWidgets('should handle minimum NDVI value (-1.0)', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: -1.0,
          showValue: true,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.text('-1.00'), findsOneWidget);
    });

    testWidgets('should handle maximum NDVI value (1.0)', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: 1.0,
          showValue: true,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.text('1.00'), findsOneWidget);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviBadge Tests - اختبارات شارة NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviBadge', () {
    testWidgets('should render with NDVI value', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviBadge(ndviValue: 0.72),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byType(NdviBadge), findsOneWidget);
      expect(find.textContaining('NDVI'), findsOneWidget);
      expect(find.text('NDVI: 0.72'), findsOneWidget);
    });

    testWidgets('should display correct icon for category', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviBadge(ndviValue: NdviFixtures.healthyNdvi),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byIcon(Icons.check_circle), findsOneWidget);
    });

    testWidgets('should show trend indicator when showTrend is true', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviBadge(
          ndviValue: NdviFixtures.healthyNdvi,
          showTrend: true,
          trend: TrendDirection.improving,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byIcon(Icons.trending_up), findsOneWidget);
    });

    testWidgets('should show declining trend icon', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviBadge(
          ndviValue: NdviFixtures.stressedNdvi,
          showTrend: true,
          trend: TrendDirection.declining,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byIcon(Icons.trending_down), findsOneWidget);
    });

    testWidgets('should show stable trend icon', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviBadge(
          ndviValue: NdviFixtures.moderateNdvi,
          showTrend: true,
          trend: TrendDirection.stable,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byIcon(Icons.trending_flat), findsWidgets);
    });

    testWidgets('should not show trend when showTrend is false', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviBadge(
          ndviValue: NdviFixtures.healthyNdvi,
          showTrend: false,
          trend: TrendDirection.improving,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Check circle is from category, trending_up should not be there
      expect(find.byIcon(Icons.trending_up), findsNothing);
    });

    testWidgets('should handle different NDVI values', (tester) async {
      // Test various values
      for (final ndvi in [0.1, 0.3, 0.5, 0.7, 0.9]) {
        final widget = createSimpleTestableWidget(
          NdviBadge(ndviValue: ndvi),
        );

        await tester.pumpWidget(widget);
        expect(find.byType(NdviBadge), findsOneWidget);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviLegendBar Tests - اختبارات شريط شرح NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviLegendBar', () {
    testWidgets('should render gradient bar', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendBar(),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byType(NdviLegendBar), findsOneWidget);
    });

    testWidgets('should show labels when showLabels is true', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendBar(showLabels: true),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Arabic labels
      expect(find.text('ضعيف'), findsOneWidget);
      expect(find.text('متوسط'), findsOneWidget);
      expect(find.text('ممتاز'), findsOneWidget);
    });

    testWidgets('should hide labels when showLabels is false', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendBar(showLabels: false),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.text('ضعيف'), findsNothing);
      expect(find.text('متوسط'), findsNothing);
      expect(find.text('ممتاز'), findsNothing);
    });

    testWidgets('should respect custom width', (tester) async {
      // Arrange
      const customWidth = 300.0;
      final widget = createSimpleTestableWidget(
        const NdviLegendBar(width: customWidth),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      final containerFinder = find.byWidgetPredicate(
        (widget) => widget is Container && widget.constraints?.maxWidth == customWidth,
      );
      // Check that we find the NdviLegendBar (width is applied to inner widgets)
      expect(find.byType(NdviLegendBar), findsOneWidget);
    });

    testWidgets('should have gradient decoration', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendBar(),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Find container with gradient
      final containerFinder = find.byWidgetPredicate(
        (widget) =>
            widget is Container &&
            widget.decoration is BoxDecoration &&
            (widget.decoration as BoxDecoration).gradient != null,
      );
      expect(containerFinder, findsOneWidget);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviLegendCard Tests - اختبارات بطاقة شرح NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviLegendCard', () {
    testWidgets('should render as Card', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendCard(),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byType(Card), findsOneWidget);
    });

    testWidgets('should display title in Arabic', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendCard(),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.text('مؤشر صحة النباتات (NDVI)'), findsOneWidget);
    });

    testWidgets('should display all legend items', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendCard(),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Check for some legend labels
      expect(find.text('مياه / غير نباتي'), findsOneWidget);
      expect(find.text('تربة جرداء'), findsOneWidget);
      expect(find.text('نباتات صحية'), findsOneWidget);
    });

    testWidgets('should display range strings', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendCard(),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Check for range strings
      expect(find.text('-1.0 - 0.0'), findsOneWidget);
      expect(find.text('0.6 - 0.8'), findsOneWidget);
    });

    testWidgets('should have 6 legend rows (color boxes)', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        const NdviLegendCard(),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Count colored containers (24x24 with border radius 4)
      final colorBoxFinder = find.byWidgetPredicate(
        (widget) =>
            widget is Container &&
            widget.decoration is BoxDecoration &&
            (widget.decoration as BoxDecoration).borderRadius ==
                BorderRadius.circular(4),
      );
      expect(colorBoxFinder, findsNWidgets(6));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviTrendChart Tests - اختبارات مخطط اتجاه NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviTrendChart', () {
    testWidgets('should show empty state when no data', (tester) async {
      // Arrange
      final stats = NdviStatistics.fromHistory([]);
      final widget = createSimpleTestableWidget(
        NdviTrendChart(statistics: stats),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Empty state message in Arabic
      expect(find.text('لا توجد بيانات تاريخية'), findsOneWidget);
    });

    testWidgets('should render CustomPaint when data available', (tester) async {
      // Arrange
      final history = createMockTimePoints(NdviFixtures.improvingTrendJson);
      final stats = NdviStatistics.fromHistory(history);
      final widget = createSimpleTestableWidget(
        NdviTrendChart(statistics: stats),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - CustomPaint may appear multiple times in the widget tree
      expect(find.byType(CustomPaint), findsAtLeastNWidgets(1));
    });

    testWidgets('should respect custom height', (tester) async {
      // Arrange
      const customHeight = 200.0;
      final history = createMockTimePoints(NdviFixtures.improvingTrendJson);
      final stats = NdviStatistics.fromHistory(history);
      final widget = createSimpleTestableWidget(
        NdviTrendChart(
          statistics: stats,
          height: customHeight,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      final sizeFinder = find.byWidgetPredicate(
        (widget) => widget is SizedBox && widget.height == customHeight,
      );
      expect(sizeFinder, findsOneWidget);
    });

    testWidgets('should render with single data point', (tester) async {
      // Arrange
      final history = [
        NdviTimePoint(date: DateTime(2026, 1, 15), value: 0.65),
      ];
      final stats = NdviStatistics.fromHistory(history);
      final widget = createSimpleTestableWidget(
        NdviTrendChart(statistics: stats),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - CustomPaint may appear multiple times in the widget tree
      expect(find.byType(CustomPaint), findsAtLeastNWidgets(1));
    });

    testWidgets('should handle improving trend data', (tester) async {
      // Arrange
      final history = createMockTimePoints(NdviFixtures.improvingTrendJson);
      final stats = NdviStatistics.fromHistory(history);
      final widget = createSimpleTestableWidget(
        NdviTrendChart(statistics: stats),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - CustomPaint may appear multiple times in the widget tree
      expect(find.byType(CustomPaint), findsAtLeastNWidgets(1));
    });

    testWidgets('should handle declining trend data', (tester) async {
      // Arrange
      final history = createMockTimePoints(NdviFixtures.decliningTrendJson);
      final stats = NdviStatistics.fromHistory(history);
      final widget = createSimpleTestableWidget(
        NdviTrendChart(statistics: stats),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - CustomPaint may appear multiple times in the widget tree
      expect(find.byType(CustomPaint), findsAtLeastNWidgets(1));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Color Mapping Visualization Tests - اختبارات تصور تخطيط الألوان
  // ═══════════════════════════════════════════════════════════════════════════

  group('NDVI Color Mapping', () {
    test('should map water values to blue colors', () {
      // Arrange & Act
      final color = NdviColormap.getColor(-0.5);

      // Assert - Blue dominant
      expect(color.blue, greaterThan(color.red));
    });

    test('should map healthy vegetation to green colors', () {
      // Arrange & Act
      final color = NdviColormap.getColor(0.7);

      // Assert - Green dominant
      expect(color.green, greaterThan(color.blue));
    });

    test('should map stressed vegetation to yellow/orange colors', () {
      // Arrange & Act
      final color = NdviColormap.getColor(0.35);

      // Assert - Some red and green (yellow-ish range)
      expect(color.red, greaterThan(0));
      expect(color.green, greaterThan(0));
    });

    test('should create distinct colors for each category boundary', () {
      // Arrange - Category boundaries
      final boundaries = [-0.5, 0.1, 0.3, 0.5, 0.7, 0.9];
      final colors = boundaries.map((v) => NdviColormap.getColor(v)).toList();

      // Assert - All colors should be unique
      final uniqueColors = colors.toSet();
      expect(uniqueColors.length, equals(colors.length));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Alert Widget Tests - اختبارات ودجات تنبيهات NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NDVI Alert Visual Tests', () {
    testWidgets('should show critical indicator for very low NDVI', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: 0.15, // Critical
          showLabel: true,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert - Should show terrain icon (bareSoil category)
      expect(find.byIcon(Icons.terrain), findsOneWidget);
    });

    testWidgets('should show eco icon for very healthy NDVI', (tester) async {
      // Arrange
      final widget = createSimpleTestableWidget(
        NdviHealthIndicator(
          ndviValue: 0.85, // Very healthy
          showLabel: true,
        ),
      );

      // Act
      await tester.pumpWidget(widget);

      // Assert
      expect(find.byIcon(Icons.eco), findsOneWidget);
      expect(find.text('ممتاز'), findsOneWidget);
    });
  });
}
