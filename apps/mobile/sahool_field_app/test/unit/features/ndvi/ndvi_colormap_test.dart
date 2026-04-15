import 'dart:ui';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/ndvi/domain/ndvi_colormap.dart';

void main() {
  group('NdviColormap.getColor', () {
    test('returns blue for water (NDVI = -1.0)', () {
      final color = NdviColormap.getColor(-1.0);
      expect(color.blue, greaterThan(200));
    });

    test('returns green-ish for healthy vegetation (NDVI = 0.7)', () {
      final color = NdviColormap.getColor(0.7);
      expect(color.green, greaterThan(color.red));
    });

    test('returns dark green for peak health (NDVI = 1.0)', () {
      final color = NdviColormap.getColor(1.0);
      expect(color.green, greaterThan(0));
      expect(color.red, lessThan(50));
    });

    test('clamps values to -1 to 1 range', () {
      final below = NdviColormap.getColor(-2.0);
      final atMin = NdviColormap.getColor(-1.0);
      expect(below, atMin);

      final above = NdviColormap.getColor(2.0);
      final atMax = NdviColormap.getColor(1.0);
      expect(above, atMax);
    });

    test('uses Yemen stops when provided', () {
      final defaultColor = NdviColormap.getColor(0.5);
      final yemenColor = NdviColormap.getColor(0.5, stops: NdviColormap.yemenStops);
      // Different colormaps should produce different colors at same value
      expect(defaultColor, isNot(equals(yemenColor)));
    });
  });

  group('NdviColormap.generateGradient', () {
    test('returns correct number of steps', () {
      final gradient = NdviColormap.generateGradient(steps: 10);
      expect(gradient, hasLength(10));
    });

    test('returns 5 colors for 5 steps', () {
      final gradient = NdviColormap.generateGradient(steps: 5);
      expect(gradient, hasLength(5));
    });

    test('custom range works', () {
      final gradient = NdviColormap.generateGradient(
        steps: 3,
        minNdvi: 0.0,
        maxNdvi: 1.0,
      );
      expect(gradient, hasLength(3));
    });
  });

  group('NdviColormap.ndviToRgba', () {
    test('produces RGBA pixels for valid values', () {
      final pixels = NdviColormap.ndviToRgba([0.5, 0.7, 0.9]);
      // Each pixel is 4 bytes (R, G, B, A)
      expect(pixels.length, 12);
    });

    test('produces transparent pixels for noData', () {
      final pixels = NdviColormap.ndviToRgba([-999.0]);
      expect(pixels[0], 0); // R
      expect(pixels[1], 0); // G
      expect(pixels[2], 0); // B
      expect(pixels[3], 0); // A (transparent)
    });

    test('produces transparent for NaN values', () {
      final pixels = NdviColormap.ndviToRgba([double.nan]);
      expect(pixels[3], 0);
    });
  });

  group('NdviLegend', () {
    test('has 6 legend items', () {
      expect(NdviLegend.items, hasLength(6));
    });

    test('all items have bilingual labels', () {
      for (final item in NdviLegend.items) {
        expect(item.label, isNotEmpty);
        expect(item.labelEn, isNotEmpty);
        expect(item.range, isNotEmpty);
      }
    });

    test('first item is water, last is very dense vegetation', () {
      expect(NdviLegend.items.first.labelEn, contains('Water'));
      expect(NdviLegend.items.last.labelEn, contains('Very Dense'));
    });
  });

  group('ColorStop', () {
    test('stores value and color', () {
      const stop = ColorStop(0.5, Color(0xFF00FF00));
      expect(stop.value, 0.5);
      expect(stop.color, const Color(0xFF00FF00));
    });
  });

  group('Default stops', () {
    test('has 13 color stops', () {
      expect(NdviColormap.defaultStops, hasLength(13));
    });

    test('starts at -1.0 and ends at 1.0', () {
      expect(NdviColormap.defaultStops.first.value, -1.0);
      expect(NdviColormap.defaultStops.last.value, 1.0);
    });

    test('values are monotonically increasing', () {
      for (int i = 1; i < NdviColormap.defaultStops.length; i++) {
        expect(NdviColormap.defaultStops[i].value,
            greaterThan(NdviColormap.defaultStops[i - 1].value));
      }
    });
  });

  group('Yemen stops', () {
    test('has 12 color stops', () {
      expect(NdviColormap.yemenStops, hasLength(12));
    });

    test('starts at -1.0 and ends at 1.0', () {
      expect(NdviColormap.yemenStops.first.value, -1.0);
      expect(NdviColormap.yemenStops.last.value, 1.0);
    });
  });
}
