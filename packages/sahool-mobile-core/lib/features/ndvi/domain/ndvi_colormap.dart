import 'dart:ui';

/// NDVI Colormap - Professional vegetation index color scale
/// Maps NDVI values (-1 to 1) to colors
///
/// Based on standard NDVI colormaps used in agricultural remote sensing
class NdviColormap {
  /// Default NDVI colormap (QGIS/ArcGIS style)
  static const List<ColorStop> defaultStops = [
    ColorStop(-1.0, Color(0xFF0000FF)), // Water - Blue
    ColorStop(-0.2, Color(0xFF87CEEB)), // Light water - Sky Blue
    ColorStop(0.0, Color(0xFFD2B48C)),  // Bare soil - Tan
    ColorStop(0.1, Color(0xFFC19A6B)),  // Dry soil - Camel
    ColorStop(0.2, Color(0xFFFFE4B5)),  // Sparse - Moccasin
    ColorStop(0.3, Color(0xFFEEE8AA)),  // Low veg - Pale Goldenrod
    ColorStop(0.4, Color(0xFFBDB76B)),  // Medium-low - Dark Khaki
    ColorStop(0.5, Color(0xFF9ACD32)),  // Medium - Yellow Green
    ColorStop(0.6, Color(0xFF7CFC00)),  // Medium-high - Lawn Green
    ColorStop(0.7, Color(0xFF32CD32)),  // High - Lime Green
    ColorStop(0.8, Color(0xFF228B22)),  // Very high - Forest Green
    ColorStop(0.9, Color(0xFF006400)),  // Dense - Dark Green
    ColorStop(1.0, Color(0xFF004400)),  // Maximum - Very Dark Green
  ];

  /// Yemen/Arabia agriculture colormap (optimized for arid regions)
  static const List<ColorStop> yemenStops = [
    ColorStop(-1.0, Color(0xFF0066CC)), // Water - Deep Blue
    ColorStop(-0.1, Color(0xFF66B2FF)), // Shallow water - Light Blue
    ColorStop(0.0, Color(0xFFE6D5AC)),  // Desert - Sand
    ColorStop(0.15, Color(0xFFD4A76A)), // Dry land - Buff
    ColorStop(0.25, Color(0xFFCD853F)), // Bare soil - Peru
    ColorStop(0.35, Color(0xFFDAA520)), // Stressed - Goldenrod
    ColorStop(0.45, Color(0xFFADFF2F)), // Moderate - Green Yellow
    ColorStop(0.55, Color(0xFF7FFF00)), // Growing - Chartreuse
    ColorStop(0.65, Color(0xFF32CD32)), // Healthy - Lime Green
    ColorStop(0.75, Color(0xFF228B22)), // Dense - Forest Green
    ColorStop(0.85, Color(0xFF006400)), // Very Dense - Dark Green
    ColorStop(1.0, Color(0xFF003300)),  // Peak - Very Dark Green
  ];

  /// Get color for NDVI value using linear interpolation
  static Color getColor(double ndvi, {List<ColorStop>? stops}) {
    final colorStops = stops ?? defaultStops;

    // Clamp to valid range
    final value = ndvi.clamp(-1.0, 1.0);

    // Find surrounding stops
    ColorStop? lower;
    ColorStop? upper;

    for (int i = 0; i < colorStops.length - 1; i++) {
      if (value >= colorStops[i].value && value <= colorStops[i + 1].value) {
        lower = colorStops[i];
        upper = colorStops[i + 1];
        break;
      }
    }

    if (lower == null || upper == null) {
      // Edge cases
      if (value <= colorStops.first.value) return colorStops.first.color;
      return colorStops.last.color;
    }

    // Linear interpolation
    final t = (value - lower.value) / (upper.value - lower.value);
    return Color.lerp(lower.color, upper.color, t)!;
  }

  /// Generate a gradient for UI display
  static List<Color> generateGradient({
    int steps = 10,
    double minNdvi = -0.2,
    double maxNdvi = 0.9,
    List<ColorStop>? stops,
  }) {
    final colors = <Color>[];
    for (int i = 0; i < steps; i++) {
      final ndvi = minNdvi + (maxNdvi - minNdvi) * (i / (steps - 1));
      colors.add(getColor(ndvi, stops: stops));
    }
    return colors;
  }

  /// Convert NDVI raster data to RGBA image pixels
  static List<int> ndviToRgba(
    List<double> ndviValues, {
    int width = 256,
    int height = 256,
    double noDataValue = -999,
    int noDataAlpha = 0,
    List<ColorStop>? stops,
  }) {
    final pixels = <int>[];

    for (final ndvi in ndviValues) {
      if (ndvi == noDataValue || ndvi.isNaN) {
        // Transparent for no data
        pixels.addAll([0, 0, 0, noDataAlpha]);
      } else {
        final color = getColor(ndvi, stops: stops);
        pixels.addAll([
          color.red,
          color.green,
          color.blue,
          (color.opacity * 255).round(),
        ]);
      }
    }

    return pixels;
  }
}

/// Color stop for gradient interpolation
class ColorStop {
  final double value;
  final Color color;

  const ColorStop(this.value, this.color);
}

/// NDVI Legend for UI display
class NdviLegend {
  static const List<LegendItem> items = [
    LegendItem(
      range: '-1.0 - 0.0',
      label: 'مياه / غير نباتي',
      labelEn: 'Water / Non-Vegetation',
      color: Color(0xFF0066CC),
    ),
    LegendItem(
      range: '0.0 - 0.2',
      label: 'تربة جرداء',
      labelEn: 'Bare Soil',
      color: Color(0xFFD4A76A),
    ),
    LegendItem(
      range: '0.2 - 0.4',
      label: 'نباتات متناثرة / إجهاد',
      labelEn: 'Sparse / Stressed',
      color: Color(0xFFDAA520),
    ),
    LegendItem(
      range: '0.4 - 0.6',
      label: 'نمو متوسط',
      labelEn: 'Moderate Growth',
      color: Color(0xFF7FFF00),
    ),
    LegendItem(
      range: '0.6 - 0.8',
      label: 'نباتات صحية',
      labelEn: 'Healthy Vegetation',
      color: Color(0xFF32CD32),
    ),
    LegendItem(
      range: '0.8 - 1.0',
      label: 'نباتات كثيفة جداً',
      labelEn: 'Very Dense Vegetation',
      color: Color(0xFF006400),
    ),
  ];
}

/// Legend item for UI
class LegendItem {
  final String range;
  final String label;
  final String labelEn;
  final Color color;

  const LegendItem({
    required this.range,
    required this.label,
    required this.labelEn,
    required this.color,
  });
}
