/// Spectral Index Tests - اختبارات مؤشرات الأقمار الصناعية الطيفية
///
/// Tests for:
/// - SpectralIndex enum (all 6 indices)
/// - SpectralColormap color interpolation
/// - Health labels (bilingual)
/// - Legend items
/// - IndexLayerControl widget
/// - SpectralHealthIndicator widget
/// - SpectralBadge widget
/// - SpectralLegendCard widget
/// - IndexPolygonLayer data model
library;

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/ndvi/domain/spectral_index.dart';
import 'package:sahool_field_app/features/ndvi/domain/ndvi_colormap.dart';
import 'package:sahool_field_app/features/ndvi/ui/ndvi_health_indicator.dart';
import 'package:sahool_field_app/features/ndvi/ui/ndvi_tile_layer.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // SpectralIndex Enum Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SpectralIndex', () {
    test('should have 6 indices', () {
      expect(SpectralIndex.values.length, equals(6));
    });

    test('each index should have code, name, nameAr, icon', () {
      for (final index in SpectralIndex.values) {
        expect(index.code, isNotEmpty);
        expect(index.name, isNotEmpty);
        expect(index.nameAr, isNotEmpty);
        expect(index.description, isNotEmpty);
        expect(index.descriptionAr, isNotEmpty);
        expect(index.icon, isNotNull);
      }
    });

    test('fromCode should parse valid codes', () {
      expect(SpectralIndex.fromCode('NDVI'), equals(SpectralIndex.ndvi));
      expect(SpectralIndex.fromCode('ndwi'), equals(SpectralIndex.ndwi));
      expect(SpectralIndex.fromCode('EVI'), equals(SpectralIndex.evi));
      expect(SpectralIndex.fromCode('savi'), equals(SpectralIndex.savi));
      expect(SpectralIndex.fromCode('NDRE'), equals(SpectralIndex.ndre));
      expect(SpectralIndex.fromCode('LAI'), equals(SpectralIndex.lai));
    });

    test('fromCode should return null for invalid codes', () {
      expect(SpectralIndex.fromCode('INVALID'), isNull);
      expect(SpectralIndex.fromCode(''), isNull);
    });

    test('getLabel should return correct locale label', () {
      expect(SpectralIndex.ndvi.getLabel(true), contains('للنبات'));
      expect(SpectralIndex.ndvi.getLabel(false), contains('Vegetation'));
      expect(SpectralIndex.ndwi.getLabel(true), contains('للمياه'));
    });

    test('LAI should have different range (0 to 8)', () {
      expect(SpectralIndex.lai.minValue, equals(0.0));
      expect(SpectralIndex.lai.maxValue, equals(8.0));
    });

    test('most indices should have -1 to 1 range', () {
      final standardIndices = [
        SpectralIndex.ndvi,
        SpectralIndex.ndwi,
        SpectralIndex.evi,
        SpectralIndex.savi,
        SpectralIndex.ndre,
      ];
      for (final idx in standardIndices) {
        expect(idx.minValue, equals(-1.0));
        expect(idx.maxValue, equals(1.0));
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SpectralColormap Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SpectralColormap', () {
    test('getStops should return non-empty list for all indices', () {
      for (final index in SpectralIndex.values) {
        final stops = SpectralColormap.getStops(index);
        expect(stops, isNotEmpty,
            reason: '${index.code} should have color stops');
        expect(stops.length, greaterThanOrEqualTo(5),
            reason: '${index.code} should have at least 5 stops');
      }
    });

    test('getColor should return valid colors for all indices', () {
      for (final index in SpectralIndex.values) {
        final color = SpectralColormap.getColor(index, 0.5);
        expect(color, isNotNull);
        expect(color.alpha, greaterThan(0));
      }
    });

    test('getColor should clamp to valid range', () {
      // Beyond max should use last stop color
      final maxColor = SpectralColormap.getColor(SpectralIndex.ndvi, 2.0);
      expect(maxColor, isNotNull);

      // Below min should use first stop color
      final minColor = SpectralColormap.getColor(SpectralIndex.ndvi, -2.0);
      expect(minColor, isNotNull);
    });

    test('NDVI colormap should use yemen stops', () {
      final stops = SpectralColormap.getStops(SpectralIndex.ndvi);
      expect(stops, equals(NdviColormap.yemenStops));
    });

    test('NDWI colors should trend from brown to blue', () {
      final dryColor = SpectralColormap.getColor(SpectralIndex.ndwi, -0.5);
      final wetColor = SpectralColormap.getColor(SpectralIndex.ndwi, 0.8);

      // Blue channel should be higher in wet color
      expect(wetColor.blue, greaterThan(dryColor.blue));
    });

    test('generateGradient should return correct number of steps', () {
      final gradient =
          SpectralColormap.generateGradient(SpectralIndex.ndvi, steps: 10);
      expect(gradient.length, equals(10));

      final gradient20 =
          SpectralColormap.generateGradient(SpectralIndex.evi, steps: 20);
      expect(gradient20.length, equals(20));
    });

    test('getLegend should return items for all indices', () {
      for (final index in SpectralIndex.values) {
        final legend = SpectralColormap.getLegend(index);
        expect(legend, isNotEmpty,
            reason: '${index.code} should have legend items');
        expect(legend.length, equals(6),
            reason: '${index.code} should have 6 legend items');
      }
    });

    test('legend items should have bilingual labels', () {
      for (final index in SpectralIndex.values) {
        final legend = SpectralColormap.getLegend(index);
        for (final item in legend) {
          expect(item.label, isNotEmpty);
          expect(item.labelEn, isNotEmpty);
          expect(item.range, isNotEmpty);
          expect(item.color, isNotNull);
        }
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Label Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SpectralColormap Health Labels', () {
    test('NDVI health labels should be correct (Arabic)', () {
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndvi, 0.85, true),
          equals('ممتاز'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndvi, 0.65, true),
          equals('جيد'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndvi, 0.45, true),
          equals('مقبول'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndvi, 0.25, true),
          equals('ضعيف'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndvi, 0.1, true),
          equals('حرج'));
    });

    test('NDVI health labels should be correct (English)', () {
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndvi, 0.85, false),
          equals('Excellent'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndvi, 0.65, false),
          equals('Good'));
    });

    test('NDWI water labels should differ from vegetation labels', () {
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndwi, 0.7, true),
          contains('مشبع'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndwi, -0.2, true),
          contains('جاف'));
    });

    test('NDRE nitrogen labels should be nitrogen-specific', () {
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndre, 0.6, true),
          contains('نيتروجين'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.ndre, 0.05, true),
          contains('نقص'));
    });

    test('LAI labels should reflect canopy density', () {
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.lai, 6.0, true),
          contains('كثيف'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.lai, 0.3, true),
          contains('ضعيف'));
    });

    test('EVI and SAVI should use vegetation health labels', () {
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.evi, 0.85, false),
          equals('Excellent'));
      expect(
          SpectralColormap.getHealthLabel(SpectralIndex.savi, 0.65, false),
          equals('Good'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IndexFieldData Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IndexFieldData', () {
    test('should create with multiple index values', () {
      const data = IndexFieldData(
        id: 'field_001',
        name: 'حقل القمح',
        boundary: [],
        values: {
          SpectralIndex.ndvi: 0.72,
          SpectralIndex.ndwi: -0.05,
          SpectralIndex.evi: 0.58,
          SpectralIndex.savi: 0.45,
        },
      );

      expect(data.getValue(SpectralIndex.ndvi), equals(0.72));
      expect(data.getValue(SpectralIndex.ndwi), equals(-0.05));
      expect(data.getValue(SpectralIndex.evi), equals(0.58));
      expect(data.getValue(SpectralIndex.savi), equals(0.45));
    });

    test('getValue should return 0.0 for missing indices', () {
      const data = IndexFieldData(
        id: 'field_002',
        name: 'حقل الشعير',
        boundary: [],
        values: {SpectralIndex.ndvi: 0.5},
      );

      expect(data.getValue(SpectralIndex.ndwi), equals(0.0));
      expect(data.getValue(SpectralIndex.lai), equals(0.0));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IndexLayerControl Widget Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IndexLayerControl', () {
    testWidgets('should show switch and selected index label', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: IndexLayerControl(
              selectedIndex: SpectralIndex.ndvi,
              onIndexChanged: (_) {},
              isVisible: false,
              onVisibilityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(Switch), findsOneWidget);
      expect(find.textContaining('NDVI'), findsOneWidget);
    });

    testWidgets('should show index selector chips when visible',
        (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: IndexLayerControl(
              selectedIndex: SpectralIndex.ndvi,
              onIndexChanged: (_) {},
              isVisible: true,
              onVisibilityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Should show ChoiceChip for each index
      expect(find.byType(ChoiceChip), findsNWidgets(6));
      // Should show all 6 index codes
      expect(find.text('NDVI'), findsWidgets);
      expect(find.text('NDWI'), findsOneWidget);
      expect(find.text('EVI'), findsOneWidget);
      expect(find.text('SAVI'), findsOneWidget);
      expect(find.text('NDRE'), findsOneWidget);
      expect(find.text('LAI'), findsOneWidget);
    });

    testWidgets('should NOT show chips when invisible', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: IndexLayerControl(
              selectedIndex: SpectralIndex.evi,
              onIndexChanged: (_) {},
              isVisible: false,
              onVisibilityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(ChoiceChip), findsNothing);
    });

    testWidgets('should show opacity slider when visible and callback provided',
        (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: IndexLayerControl(
              selectedIndex: SpectralIndex.ndvi,
              onIndexChanged: (_) {},
              isVisible: true,
              onVisibilityChanged: (_) {},
              opacity: 0.7,
              onOpacityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(Slider), findsOneWidget);
    });

    testWidgets('should show gradient legend when visible', (tester) async {
      await tester.pumpWidget(MaterialApp(
        locale: const Locale('ar'),
        supportedLocales: const [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: IndexLayerControl(
              selectedIndex: SpectralIndex.ndwi,
              onIndexChanged: (_) {},
              isVisible: true,
              onVisibilityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Should show the index name in Arabic
      expect(find.textContaining('للمياه'), findsOneWidget);
      // Should show min/max range
      expect(find.text('-1.0'), findsOneWidget);
      expect(find.text('1.0'), findsOneWidget);
    });

    testWidgets('should call onIndexChanged when chip tapped', (tester) async {
      SpectralIndex? changedIndex;

      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: IndexLayerControl(
              selectedIndex: SpectralIndex.ndvi,
              onIndexChanged: (idx) => changedIndex = idx,
              isVisible: true,
              onVisibilityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Tap on EVI chip
      await tester.tap(find.text('EVI'));
      await tester.pumpAndSettle();

      expect(changedIndex, equals(SpectralIndex.evi));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SpectralHealthIndicator Widget Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SpectralHealthIndicator', () {
    testWidgets('should render for NDVI', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        locale: Locale('ar'),
        supportedLocales: [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Scaffold(
          body: SpectralHealthIndicator(
            index: SpectralIndex.ndvi,
            value: 0.72,
          ),
        ),
      ));
      await tester.pump();

      expect(find.text('0.72'), findsOneWidget);
      expect(find.text('NDVI'), findsOneWidget);
    });

    testWidgets('should render for NDWI', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        locale: Locale('ar'),
        supportedLocales: [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Scaffold(
          body: SpectralHealthIndicator(
            index: SpectralIndex.ndwi,
            value: 0.4,
          ),
        ),
      ));
      await tester.pump();

      expect(find.text('0.40'), findsOneWidget);
      expect(find.text('NDWI'), findsOneWidget);
    });

    testWidgets('should show health label', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        locale: Locale('ar'),
        supportedLocales: [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Scaffold(
          body: SpectralHealthIndicator(
            index: SpectralIndex.ndvi,
            value: 0.85,
            showLabel: true,
          ),
        ),
      ));
      await tester.pump();

      expect(find.textContaining('ممتاز'), findsOneWidget);
    });

    testWidgets('should contain CircularProgressIndicator', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        locale: Locale('ar'),
        supportedLocales: [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Scaffold(
          body: SpectralHealthIndicator(
            index: SpectralIndex.evi,
            value: 0.5,
          ),
        ),
      ));
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsWidgets);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SpectralBadge Widget Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SpectralBadge', () {
    testWidgets('should show index code and value', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: SpectralBadge(
            index: SpectralIndex.savi,
            value: 0.45,
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('SAVI: 0.45'), findsOneWidget);
    });

    testWidgets('should show correct icon for each index', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: SpectralBadge(
            index: SpectralIndex.ndwi,
            value: 0.3,
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.water_drop), findsOneWidget);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SpectralLegendCard Widget Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SpectralLegendCard', () {
    testWidgets('should display NDVI legend in Arabic', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        locale: Locale('ar'),
        supportedLocales: [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: SingleChildScrollView(
              child: SpectralLegendCard(index: SpectralIndex.ndvi),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.textContaining('للنبات'), findsOneWidget);
    });

    testWidgets('should display NDWI legend items', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        locale: Locale('ar'),
        supportedLocales: [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: SingleChildScrollView(
              child: SpectralLegendCard(index: SpectralIndex.ndwi),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.textContaining('للمياه'), findsOneWidget);
      // NDWI legend should have 6 items
      expect(find.textContaining('رطوبة'), findsWidgets);
    });
  });
}
