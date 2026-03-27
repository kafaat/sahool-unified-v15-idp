/// Satellite Map Overlay Tests - اختبارات تراكب خريطة الأقمار الصناعية
///
/// Tests for interactive SatelliteMapOverlay widget:
/// - StatefulWidget with animation
/// - Opacity control slider
/// - Gradient legend
/// - Index badge with pulse animation (NDVI, NDWI, EVI, SAVI, NDRE, LAI)
/// - Multi-index selector
/// - Capture date display
/// - Health label (bilingual)
library;

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/features/ndvi/domain/spectral_index.dart';
import 'package:sahool_mobile_core/features/satellite/widgets/satellite_map_overlay.dart';

void main() {
  Widget createTestWidget({
    String? imageUrl,
    double ndviValue = 0.65,
    VoidCallback? onRefresh,
    DateTime? captureDate,
    ValueChanged<double>? onOpacityChanged,
    VoidCallback? onTap,
    Locale locale = const Locale('ar'),
  }) {
    return MaterialApp(
      locale: locale,
      supportedLocales: const [Locale('ar'), Locale('en')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      home: Directionality(
        textDirection: TextDirection.rtl,
        child: Scaffold(
          body: SingleChildScrollView(
            child: SatelliteMapOverlay(
              imageUrl: imageUrl,
              ndviValue: ndviValue,
              onRefresh: onRefresh,
              captureDate: captureDate,
              onOpacityChanged: onOpacityChanged,
              onTap: onTap,
            ),
          ),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Basic Rendering Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SatelliteMapOverlay Rendering', () {
    testWidgets('should render with required parameters', (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Should show NDVI value
      expect(find.text('0.65'), findsOneWidget);
      // Should show NDVI label
      expect(find.text('NDVI'), findsOneWidget);
    });

    testWidgets('should display different NDVI values correctly',
        (tester) async {
      await tester.pumpWidget(createTestWidget(ndviValue: 0.85));
      await tester.pumpAndSettle();

      expect(find.text('0.85'), findsOneWidget);
    });

    testWidgets('should show placeholder when no image URL', (tester) async {
      await tester.pumpWidget(createTestWidget(imageUrl: null));
      await tester.pumpAndSettle();

      // Should find the satellite icon placeholder
      expect(find.byIcon(Icons.satellite_alt), findsWidgets);
    });

    testWidgets('should show refresh button when callback provided',
        (tester) async {
      bool refreshed = false;
      await tester.pumpWidget(createTestWidget(
        onRefresh: () => refreshed = true,
      ));
      await tester.pumpAndSettle();

      final refreshButton = find.byIcon(Icons.refresh);
      expect(refreshButton, findsOneWidget);

      await tester.tap(refreshButton);
      expect(refreshed, isTrue);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Interactive Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SatelliteMapOverlay Interactivity', () {
    testWidgets('should toggle controls on tap', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(createTestWidget(
        onTap: () => tapped = true,
        onOpacityChanged: (_) {},
      ));
      await tester.pumpAndSettle();

      // Initially, slider should not be visible
      expect(find.byType(Slider), findsNothing);

      // Tap on the overlay to show controls
      await tester.tap(find.byType(GestureDetector).first);
      await tester.pumpAndSettle();

      expect(tapped, isTrue);

      // After tap, slider should appear
      expect(find.byType(Slider), findsOneWidget);
    });

    testWidgets('should show opacity slider with correct range',
        (tester) async {
      double? changedOpacity;
      await tester.pumpWidget(createTestWidget(
        onOpacityChanged: (v) => changedOpacity = v,
      ));
      await tester.pumpAndSettle();

      // Tap to show controls
      await tester.tap(find.byType(GestureDetector).first);
      await tester.pumpAndSettle();

      // Slider should be present
      final sliderFinder = find.byType(Slider);
      expect(sliderFinder, findsOneWidget);

      // Slider has correct range (0.1 to 1.0)
      final slider = tester.widget<Slider>(sliderFinder);
      expect(slider.min, equals(0.1));
      expect(slider.max, equals(1.0));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Capture Date Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SatelliteMapOverlay Capture Date', () {
    testWidgets('should display capture date when provided', (tester) async {
      final captureDate = DateTime(2026, 1, 15);
      await tester.pumpWidget(createTestWidget(captureDate: captureDate));
      await tester.pumpAndSettle();

      // Should show calendar icon
      expect(find.byIcon(Icons.calendar_today), findsOneWidget);
      // Should show formatted date
      expect(find.textContaining('2026'), findsWidgets);
    });

    testWidgets('should NOT show date badge when no capture date',
        (tester) async {
      await tester.pumpWidget(createTestWidget(captureDate: null));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.calendar_today), findsNothing);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Label Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SatelliteMapOverlay Health Labels', () {
    testWidgets('should show Excellent for high NDVI (>= 0.8)',
        (tester) async {
      await tester.pumpWidget(createTestWidget(ndviValue: 0.85));
      await tester.pumpAndSettle();

      // Should contain the health label
      expect(find.textContaining('ممتاز'), findsOneWidget);
    });

    testWidgets('should show Good for NDVI >= 0.6', (tester) async {
      await tester.pumpWidget(createTestWidget(ndviValue: 0.65));
      await tester.pumpAndSettle();

      expect(find.textContaining('جيد'), findsOneWidget);
    });

    testWidgets('should show Fair/Moderate for NDVI >= 0.4', (tester) async {
      await tester.pumpWidget(createTestWidget(ndviValue: 0.45));
      await tester.pumpAndSettle();

      // SpectralColormap uses 'مقبول' for Fair
      expect(find.textContaining('مقبول'), findsOneWidget);
    });

    testWidgets('should show Poor for NDVI >= 0.2', (tester) async {
      await tester.pumpWidget(createTestWidget(ndviValue: 0.25));
      await tester.pumpAndSettle();

      expect(find.textContaining('ضعيف'), findsOneWidget);
    });

    testWidgets('should show Critical for NDVI < 0.2', (tester) async {
      await tester.pumpWidget(createTestWidget(ndviValue: 0.10));
      await tester.pumpAndSettle();

      expect(find.textContaining('حرج'), findsOneWidget);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Gradient Legend Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SatelliteMapOverlay Legend', () {
    testWidgets('should display gradient legend with range labels',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pumpAndSettle();

      // Legend should show NDVI range labels
      expect(find.textContaining('-1.0'), findsWidgets);
      expect(find.textContaining('1.0'), findsWidgets);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Multi-Index Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SatelliteMapOverlay Multi-Index', () {
    testWidgets('should show index selector chips when multiple indices provided',
        (tester) async {
      await tester.pumpWidget(MaterialApp(
        locale: const Locale('ar'),
        supportedLocales: const [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: SingleChildScrollView(
              child: SatelliteMapOverlay(
                ndviValue: 0.72,
                onOpacityChanged: (_) {},
                onTap: () {},
                indexValues: const {
                  SpectralIndex.ndvi: 0.72,
                  SpectralIndex.ndwi: -0.05,
                  SpectralIndex.evi: 0.58,
                },
                onIndexChanged: (_) {},
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Tap to show controls
      await tester.tap(find.byType(GestureDetector).first);
      await tester.pumpAndSettle();

      // Should show index chips
      expect(find.text('NDVI'), findsWidgets);
      expect(find.text('NDWI'), findsOneWidget);
      expect(find.text('EVI'), findsOneWidget);
    });

    testWidgets('should NOT show index chips with single index',
        (tester) async {
      await tester.pumpWidget(MaterialApp(
        locale: const Locale('ar'),
        supportedLocales: const [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: SingleChildScrollView(
              child: SatelliteMapOverlay(
                ndviValue: 0.72,
                onOpacityChanged: (_) {},
                onTap: () {},
                indexValues: const {SpectralIndex.ndvi: 0.72},
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Tap to show controls
      await tester.tap(find.byType(GestureDetector).first);
      await tester.pumpAndSettle();

      // Should NOT show NDWI, EVI chips (only single index)
      expect(find.text('NDWI'), findsNothing);
      expect(find.text('EVI'), findsNothing);
    });

    testWidgets('should display NDVI by default', (tester) async {
      await tester.pumpWidget(MaterialApp(
        locale: const Locale('ar'),
        supportedLocales: const [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            body: SingleChildScrollView(
              child: SatelliteMapOverlay(
                ndviValue: 0.72,
                indexValues: const {
                  SpectralIndex.ndvi: 0.72,
                  SpectralIndex.ndwi: -0.05,
                },
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      // Badge should show NDVI by default
      expect(find.text('NDVI'), findsWidgets);
      expect(find.text('0.72'), findsOneWidget);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Animation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SatelliteMapOverlay Animation', () {
    testWidgets('should contain AnimatedContainer for height transition',
        (tester) async {
      await tester.pumpWidget(createTestWidget(onOpacityChanged: (_) {}));
      await tester.pump();

      expect(find.byType(AnimatedContainer), findsWidgets);
    });

    testWidgets('should contain AnimatedOpacity for image opacity',
        (tester) async {
      await tester.pumpWidget(createTestWidget(
        imageUrl: 'https://example.com/satellite.png',
      ));
      await tester.pump();

      expect(find.byType(AnimatedOpacity), findsWidgets);
    });

    testWidgets('should contain ScaleTransition for NDVI badge',
        (tester) async {
      await tester.pumpWidget(createTestWidget());
      await tester.pump();

      expect(find.byType(ScaleTransition), findsWidgets);
    });
  });
}
