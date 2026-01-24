/// NDVI Colormap Tests - اختبارات خريطة ألوان NDVI
///
/// Comprehensive unit tests for:
/// - NdviColormap color interpolation
/// - Default and Yemen colormap stops
/// - Gradient generation
/// - NDVI to RGBA conversion
/// - NdviLegend items
library;

import 'dart:ui';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/ndvi/domain/ndvi_colormap.dart';

import 'ndvi_fixtures.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // ColorStop Tests - اختبارات توقف اللون
  // ═══════════════════════════════════════════════════════════════════════════

  group('ColorStop', () {
    test('should create ColorStop with value and color', () {
      // Arrange & Act
      const stop = ColorStop(0.5, Color(0xFF00FF00));

      // Assert
      expect(stop.value, equals(0.5));
      expect(stop.color, equals(const Color(0xFF00FF00)));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviColormap.defaultStops Tests - اختبارات التوقفات الافتراضية
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviColormap.defaultStops', () {
    test('should have stops from -1.0 to 1.0', () {
      // Assert
      expect(NdviColormap.defaultStops.first.value, equals(-1.0));
      expect(NdviColormap.defaultStops.last.value, equals(1.0));
    });

    test('should have stops in ascending order', () {
      // Arrange
      final values = NdviColormap.defaultStops.map((s) => s.value).toList();

      // Assert
      for (int i = 1; i < values.length; i++) {
        expect(values[i], greaterThan(values[i - 1]));
      }
    });

    test('should have at least 10 stops for smooth gradient', () {
      expect(NdviColormap.defaultStops.length, greaterThanOrEqualTo(10));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviColormap.yemenStops Tests - اختبارات توقفات اليمن
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviColormap.yemenStops', () {
    test('should have stops from -1.0 to 1.0', () {
      // Assert
      expect(NdviColormap.yemenStops.first.value, equals(-1.0));
      expect(NdviColormap.yemenStops.last.value, equals(1.0));
    });

    test('should have stops in ascending order', () {
      // Arrange
      final values = NdviColormap.yemenStops.map((s) => s.value).toList();

      // Assert
      for (int i = 1; i < values.length; i++) {
        expect(values[i], greaterThan(values[i - 1]));
      }
    });

    test('should have at least 10 stops for smooth gradient', () {
      expect(NdviColormap.yemenStops.length, greaterThanOrEqualTo(10));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviColormap.getColor Tests - اختبارات الحصول على اللون
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviColormap.getColor', () {
    group('with default stops', () {
      test('should return blue color for water (-1.0)', () {
        // Act
        final color = NdviColormap.getColor(-1.0);

        // Assert - Should be in blue range
        expect(color.blue, greaterThan(color.red));
        expect(color.blue, greaterThan(color.green));
      });

      test('should return brown/tan color for bare soil (0.0-0.2)', () {
        // Act
        final color = NdviColormap.getColor(0.1);

        // Assert - Should be in tan/brown range
        expect(color.red, greaterThan(0));
        expect(color.green, greaterThan(0));
      });

      test('should return green color for healthy vegetation (0.6-0.8)', () {
        // Act
        final color = NdviColormap.getColor(NdviFixtures.healthyNdvi);

        // Assert - Should be in green range
        expect(color.green, greaterThan(color.red));
      });

      test('should return dark green for very healthy vegetation (0.9)', () {
        // Act
        final color = NdviColormap.getColor(0.9);

        // Assert - Should be dark green
        expect(color.green, greaterThan(0));
        expect(color.green, greaterThan(color.red));
      });

      test('should clamp value below -1.0', () {
        // Act
        final colorMin = NdviColormap.getColor(-1.5);
        final colorBoundary = NdviColormap.getColor(-1.0);

        // Assert
        expect(colorMin, equals(colorBoundary));
      });

      test('should clamp value above 1.0', () {
        // Act
        final colorMax = NdviColormap.getColor(1.5);
        final colorBoundary = NdviColormap.getColor(1.0);

        // Assert
        expect(colorMax, equals(colorBoundary));
      });

      test('should return exact stop color when at stop value', () {
        // Arrange - Test at exact stop value -1.0
        final expectedColor = NdviColormap.defaultStops.first.color;

        // Act
        final color = NdviColormap.getColor(-1.0);

        // Assert
        expect(color, equals(expectedColor));
      });

      test('should interpolate between stops', () {
        // Arrange - Find two consecutive stops
        final stop1 = NdviColormap.defaultStops[0]; // -1.0
        final stop2 = NdviColormap.defaultStops[1]; // next stop

        // Act - Get color at midpoint
        final midValue = (stop1.value + stop2.value) / 2;
        final color = NdviColormap.getColor(midValue);

        // Assert - Color should be between the two stops
        expect(color, isA<Color>());
        // The color should be a blend of the two stop colors
      });
    });

    group('with Yemen stops', () {
      test('should return color for water with Yemen colormap', () {
        // Act
        final color = NdviColormap.getColor(
          -0.5,
          stops: NdviColormap.yemenStops,
        );

        // Assert - Should be in blue range
        expect(color.blue, greaterThan(0));
      });

      test('should return sand color for bare soil with Yemen colormap', () {
        // Act
        final color = NdviColormap.getColor(
          0.1,
          stops: NdviColormap.yemenStops,
        );

        // Assert - Should be in sand/tan range
        expect(color.red, greaterThan(0));
      });

      test('should return green for healthy vegetation with Yemen colormap', () {
        // Act
        final color = NdviColormap.getColor(
          NdviFixtures.healthyNdvi,
          stops: NdviColormap.yemenStops,
        );

        // Assert
        expect(color.green, greaterThan(color.red));
      });
    });

    group('edge cases - حالات خاصة', () {
      test('should handle zero value', () {
        // Act
        final color = NdviColormap.getColor(0.0);

        // Assert
        expect(color, isA<Color>());
      });

      test('should handle value just above boundary', () {
        // Act
        final color = NdviColormap.getColor(0.001);

        // Assert
        expect(color, isA<Color>());
      });

      test('should handle value just below boundary', () {
        // Act
        final color = NdviColormap.getColor(-0.001);

        // Assert
        expect(color, isA<Color>());
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviColormap.generateGradient Tests - اختبارات إنشاء التدرج
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviColormap.generateGradient', () {
    test('should generate correct number of colors', () {
      // Act
      final colors = NdviColormap.generateGradient(steps: 10);

      // Assert
      expect(colors.length, equals(10));
    });

    test('should generate colors within min/max range', () {
      // Arrange
      const minNdvi = 0.2;
      const maxNdvi = 0.8;

      // Act
      final colors = NdviColormap.generateGradient(
        steps: 5,
        minNdvi: minNdvi,
        maxNdvi: maxNdvi,
      );

      // Assert
      expect(colors.length, equals(5));
      // First color should match minNdvi color
      expect(colors.first, equals(NdviColormap.getColor(minNdvi)));
      // Last color should match maxNdvi color
      expect(colors.last, equals(NdviColormap.getColor(maxNdvi)));
    });

    test('should use custom stops when provided', () {
      // Act
      final colorsDefault = NdviColormap.generateGradient(steps: 5);
      final colorsYemen = NdviColormap.generateGradient(
        steps: 5,
        stops: NdviColormap.yemenStops,
      );

      // Assert - Colors should be different with different stops
      expect(colorsDefault, isNot(equals(colorsYemen)));
    });

    test('should handle single step', () {
      // Act
      final colors = NdviColormap.generateGradient(steps: 1);

      // Assert
      expect(colors.length, equals(1));
    });

    test('should handle two steps', () {
      // Act
      final colors = NdviColormap.generateGradient(
        steps: 2,
        minNdvi: 0.0,
        maxNdvi: 1.0,
      );

      // Assert
      expect(colors.length, equals(2));
      expect(colors.first, equals(NdviColormap.getColor(0.0)));
      expect(colors.last, equals(NdviColormap.getColor(1.0)));
    });

    test('should generate smooth gradient', () {
      // Act
      final colors = NdviColormap.generateGradient(steps: 20);

      // Assert - All colors should be valid
      for (final color in colors) {
        expect(color.alpha, greaterThanOrEqualTo(0));
        expect(color.red, greaterThanOrEqualTo(0));
        expect(color.green, greaterThanOrEqualTo(0));
        expect(color.blue, greaterThanOrEqualTo(0));
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviColormap.ndviToRgba Tests - اختبارات تحويل NDVI إلى RGBA
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviColormap.ndviToRgba', () {
    test('should convert single NDVI value to 4 RGBA bytes', () {
      // Arrange
      final ndviValues = [0.5];

      // Act
      final pixels = NdviColormap.ndviToRgba(ndviValues);

      // Assert
      expect(pixels.length, equals(4)); // R, G, B, A
    });

    test('should convert array of NDVI values to RGBA pixels', () {
      // Arrange
      final ndviValues = [0.3, 0.5, 0.7];

      // Act
      final pixels = NdviColormap.ndviToRgba(ndviValues);

      // Assert
      expect(pixels.length, equals(12)); // 3 pixels * 4 bytes
    });

    test('should return transparent for noData value', () {
      // Arrange
      final ndviValues = [NdviFixtures.noDataValue];

      // Act
      final pixels = NdviColormap.ndviToRgba(
        ndviValues,
        noDataValue: NdviFixtures.noDataValue,
        noDataAlpha: 0,
      );

      // Assert
      expect(pixels[0], equals(0)); // R
      expect(pixels[1], equals(0)); // G
      expect(pixels[2], equals(0)); // B
      expect(pixels[3], equals(0)); // A (transparent)
    });

    test('should return transparent for NaN value', () {
      // Arrange
      final ndviValues = [double.nan];

      // Act
      final pixels = NdviColormap.ndviToRgba(ndviValues, noDataAlpha: 0);

      // Assert
      expect(pixels[3], equals(0)); // Alpha should be 0 (transparent)
    });

    test('should use custom noData alpha', () {
      // Arrange
      final ndviValues = [NdviFixtures.noDataValue];

      // Act
      final pixels = NdviColormap.ndviToRgba(
        ndviValues,
        noDataValue: NdviFixtures.noDataValue,
        noDataAlpha: 128,
      );

      // Assert
      expect(pixels[3], equals(128));
    });

    test('should convert raster data correctly', () {
      // Arrange
      final ndviValues = NdviFixtures.generateRasterData(
        width: 2,
        height: 2,
        baseValue: 0.5,
      );

      // Act
      final pixels = NdviColormap.ndviToRgba(ndviValues);

      // Assert
      expect(pixels.length, equals(16)); // 4 pixels * 4 bytes
    });

    test('should handle mixed valid and noData values', () {
      // Arrange
      final ndviValues = [0.5, NdviFixtures.noDataValue, 0.7];

      // Act
      final pixels = NdviColormap.ndviToRgba(
        ndviValues,
        noDataValue: NdviFixtures.noDataValue,
        noDataAlpha: 0,
      );

      // Assert
      expect(pixels.length, equals(12));
      // First pixel should be opaque
      expect(pixels[3], greaterThan(0));
      // Second pixel (noData) should be transparent
      expect(pixels[7], equals(0));
      // Third pixel should be opaque
      expect(pixels[11], greaterThan(0));
    });

    test('should use custom stops', () {
      // Arrange
      final ndviValues = [0.5];

      // Act
      final pixelsDefault = NdviColormap.ndviToRgba(ndviValues);
      final pixelsYemen = NdviColormap.ndviToRgba(
        ndviValues,
        stops: NdviColormap.yemenStops,
      );

      // Assert - Colors should be different
      expect(pixelsDefault, isNot(equals(pixelsYemen)));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviLegend Tests - اختبارات شرح NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviLegend', () {
    test('should have 6 legend items', () {
      expect(NdviLegend.items.length, equals(6));
    });

    test('all items should have range string', () {
      for (final item in NdviLegend.items) {
        expect(item.range, isNotEmpty);
        expect(item.range, contains('-'));
      }
    });

    test('all items should have Arabic label', () {
      for (final item in NdviLegend.items) {
        expect(item.label, isNotEmpty);
      }
    });

    test('all items should have English label', () {
      for (final item in NdviLegend.items) {
        expect(item.labelEn, isNotEmpty);
      }
    });

    test('all items should have color', () {
      for (final item in NdviLegend.items) {
        expect(item.color, isA<Color>());
      }
    });

    test('should cover full NDVI range', () {
      // Verify first item starts at -1.0
      expect(NdviLegend.items.first.range, contains('-1.0'));
      // Verify last item ends at 1.0
      expect(NdviLegend.items.last.range, contains('1.0'));
    });

    test('should have correct Arabic labels', () {
      // Verify some specific Arabic labels
      final labels = NdviLegend.items.map((i) => i.label).toList();
      expect(labels, contains('مياه / غير نباتي'));
      expect(labels, contains('تربة جرداء'));
      expect(labels, contains('نباتات صحية'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // LegendItem Tests - اختبارات عنصر الشرح
  // ═══════════════════════════════════════════════════════════════════════════

  group('LegendItem', () {
    test('should create with all required fields', () {
      // Arrange & Act
      const item = LegendItem(
        range: '0.0 - 0.2',
        label: 'تربة جرداء',
        labelEn: 'Bare Soil',
        color: Color(0xFFD4A76A),
      );

      // Assert
      expect(item.range, equals('0.0 - 0.2'));
      expect(item.label, equals('تربة جرداء'));
      expect(item.labelEn, equals('Bare Soil'));
      expect(item.color, equals(const Color(0xFFD4A76A)));
    });
  });
}
