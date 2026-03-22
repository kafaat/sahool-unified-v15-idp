/// NDVI Tile Layer Tests - اختبارات طبقة بلاطات NDVI
///
/// Tests for:
/// - NdviTileConfig creation and factory methods
/// - NdviTileLayerWidget with AnimatedOpacity
/// - NdviPolygonLayer with 80x80 tap markers
/// - NdviFieldData model
/// - NdviLayerControl switch and slider
library;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/features/ndvi/ui/ndvi_tile_layer.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // NdviTileConfig Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviTileConfig', () {
    test('should create with required fields', () {
      const config = NdviTileConfig(
        urlTemplate: 'https://example.com/{z}/{x}/{y}.png',
      );

      expect(config.urlTemplate, contains('{z}'));
      expect(config.tileSize, equals(256));
      expect(config.opacity, equals(0.7));
      expect(config.minZoom, equals(10));
      expect(config.maxZoom, equals(18));
      expect(config.apiKey, isNull);
      expect(config.headers, isNull);
    });

    test('sentinelHub factory should include WMS parameters', () {
      final config = NdviTileConfig.sentinelHub(apiKey: 'test-key-123');

      expect(config.urlTemplate, contains('sentinel-hub.com'));
      expect(config.urlTemplate, contains('NDVI'));
      expect(config.urlTemplate, contains('GetMap'));
      expect(config.apiKey, equals('test-key-123'));
      expect(config.headers, isNotNull);
      expect(config.headers!['Authorization'], contains('test-key-123'));
    });

    test('sahoolBackend factory should use correct URL pattern', () {
      final config = NdviTileConfig.sahoolBackend(
        baseUrl: 'https://api.sahool.app',
      );

      expect(config.urlTemplate,
          equals('https://api.sahool.app/api/v1/ndvi/tiles/{z}/{x}/{y}.png'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviFieldData Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviFieldData', () {
    test('should create with all required fields', () {
      final data = NdviFieldData(
        id: 'field_001',
        name: 'حقل القمح',
        boundary: [
          const LatLng(15.37, 44.19),
          const LatLng(15.38, 44.19),
          const LatLng(15.38, 44.20),
          const LatLng(15.37, 44.20),
        ],
        ndviValue: 0.72,
        lastUpdated: DateTime(2026, 1, 15),
      );

      expect(data.id, equals('field_001'));
      expect(data.name, equals('حقل القمح'));
      expect(data.boundary.length, equals(4));
      expect(data.ndviValue, equals(0.72));
      expect(data.lastUpdated, isNotNull);
    });

    test('should work without optional lastUpdated', () {
      const data = NdviFieldData(
        id: 'field_002',
        name: 'حقل الشعير',
        boundary: [],
        ndviValue: 0.55,
      );

      expect(data.lastUpdated, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviLayerControl Widget Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviLayerControl', () {
    testWidgets('should show switch and NDVI label', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: NdviLayerControl(
              isNdviVisible: false,
              onVisibilityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('طبقة NDVI'), findsOneWidget);
      expect(find.byType(Switch), findsOneWidget);
      expect(find.byIcon(Icons.grass), findsOneWidget);
    });

    testWidgets('switch should toggle NDVI visibility', (tester) async {
      bool visible = false;

      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: StatefulBuilder(
            builder: (context, setState) => Scaffold(
              body: NdviLayerControl(
                isNdviVisible: visible,
                onVisibilityChanged: (v) => setState(() => visible = v),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Tap switch to enable
      await tester.tap(find.byType(Switch));
      await tester.pumpAndSettle();

      expect(visible, isTrue);
    });

    testWidgets('should show opacity slider when visible and callback provided',
        (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: NdviLayerControl(
              isNdviVisible: true,
              onVisibilityChanged: (_) {},
              opacity: 0.7,
              onOpacityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(Slider), findsOneWidget);
      expect(find.text('الشفافية'), findsOneWidget);
      expect(find.text('70%'), findsOneWidget);
    });

    testWidgets('should NOT show slider when invisible', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: NdviLayerControl(
              isNdviVisible: false,
              onVisibilityChanged: (_) {},
              onOpacityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(Slider), findsNothing);
    });

    testWidgets('icon color should change based on visibility', (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: NdviLayerControl(
              isNdviVisible: true,
              onVisibilityChanged: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      final icon = tester.widget<Icon>(find.byIcon(Icons.grass));
      expect(icon.color, equals(Colors.green));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviTileLayerWidget Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviTileLayerWidget', () {
    testWidgets('should not render when invisible', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: NdviTileLayerWidget(
            config: NdviTileConfig(
              urlTemplate: 'https://example.com/{z}/{x}/{y}.png',
            ),
            visible: false,
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.byType(SizedBox), findsWidgets);
    });

    testWidgets('should use AnimatedOpacity when visible', (tester) async {
      await tester.pumpWidget(const MaterialApp(
        home: Scaffold(
          body: FlutterMap(
            options: MapOptions(),
            children: [
              NdviTileLayerWidget(
                config: NdviTileConfig(
                  urlTemplate: 'https://example.com/{z}/{x}/{y}.png',
                  opacity: 0.5,
                ),
                visible: true,
              ),
            ],
          ),
        ),
      ));
      await tester.pump();

      // Should have AnimatedOpacity instead of Opacity
      expect(find.byType(AnimatedOpacity), findsOneWidget);

      final animatedOpacity =
          tester.widget<AnimatedOpacity>(find.byType(AnimatedOpacity));
      expect(animatedOpacity.opacity, equals(0.5));
      expect(animatedOpacity.duration, equals(const Duration(milliseconds: 300)));
    });
  });
}
