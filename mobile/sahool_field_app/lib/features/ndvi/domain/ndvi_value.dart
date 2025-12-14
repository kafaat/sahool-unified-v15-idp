import 'package:flutter/material.dart';

/// NDVI Value Object - Normalized Difference Vegetation Index
/// القيمة الطبيعية للنبات تتراوح بين -1 و 1
///
/// Interpretation:
/// -1.0 to 0.0  : Water, snow, clouds, bare soil
///  0.0 to 0.2  : Bare soil, rocks, sand
///  0.2 to 0.4  : Sparse vegetation, stressed crops
///  0.4 to 0.6  : Moderate vegetation, developing crops
///  0.6 to 0.8  : Dense vegetation, healthy crops
///  0.8 to 1.0  : Very dense vegetation, peak health
class NdviValue {
  final double value;
  final DateTime capturedAt;
  final String? source; // satellite source (Sentinel-2, Landsat, etc.)

  const NdviValue({
    required this.value,
    required this.capturedAt,
    this.source,
  }) : assert(value >= -1 && value <= 1, 'NDVI must be between -1 and 1');

  /// Health category based on NDVI value
  NdviHealthCategory get category {
    if (value < 0) return NdviHealthCategory.nonVegetation;
    if (value < 0.2) return NdviHealthCategory.bareSoil;
    if (value < 0.4) return NdviHealthCategory.stressed;
    if (value < 0.6) return NdviHealthCategory.moderate;
    if (value < 0.8) return NdviHealthCategory.healthy;
    return NdviHealthCategory.veryHealthy;
  }

  /// Percentage representation (0-100)
  double get percentage => ((value + 1) / 2 * 100).clamp(0, 100);

  /// Normalized percentage for vegetation only (0-100 where 0.2=0%, 0.8=100%)
  double get vegetationPercentage {
    if (value < 0.2) return 0;
    if (value > 0.8) return 100;
    return ((value - 0.2) / 0.6 * 100);
  }

  /// Color representation for visualization
  Color get color => category.color;

  /// Arabic label
  String get labelAr => category.labelAr;

  /// English label
  String get labelEn => category.labelEn;

  @override
  String toString() => 'NDVI: ${value.toStringAsFixed(2)} (${category.labelEn})';
}

/// NDVI Health Categories
enum NdviHealthCategory {
  nonVegetation(
    minValue: -1.0,
    maxValue: 0.0,
    color: Color(0xFF1565C0), // Blue
    labelAr: 'غير نباتي',
    labelEn: 'Non-Vegetation',
    icon: Icons.water_drop,
  ),
  bareSoil(
    minValue: 0.0,
    maxValue: 0.2,
    color: Color(0xFF8D6E63), // Brown
    labelAr: 'تربة جرداء',
    labelEn: 'Bare Soil',
    icon: Icons.terrain,
  ),
  stressed(
    minValue: 0.2,
    maxValue: 0.4,
    color: Color(0xFFFF5722), // Deep Orange
    labelAr: 'إجهاد',
    labelEn: 'Stressed',
    icon: Icons.warning_amber,
  ),
  moderate(
    minValue: 0.4,
    maxValue: 0.6,
    color: Color(0xFFFFEB3B), // Yellow
    labelAr: 'متوسط',
    labelEn: 'Moderate',
    icon: Icons.trending_flat,
  ),
  healthy(
    minValue: 0.6,
    maxValue: 0.8,
    color: Color(0xFF8BC34A), // Light Green
    labelAr: 'صحي',
    labelEn: 'Healthy',
    icon: Icons.check_circle,
  ),
  veryHealthy(
    minValue: 0.8,
    maxValue: 1.0,
    color: Color(0xFF2E7D32), // Dark Green
    labelAr: 'ممتاز',
    labelEn: 'Very Healthy',
    icon: Icons.eco,
  );

  final double minValue;
  final double maxValue;
  final Color color;
  final String labelAr;
  final String labelEn;
  final IconData icon;

  const NdviHealthCategory({
    required this.minValue,
    required this.maxValue,
    required this.color,
    required this.labelAr,
    required this.labelEn,
    required this.icon,
  });

  /// Get category from NDVI value
  static NdviHealthCategory fromValue(double ndvi) {
    if (ndvi < 0) return nonVegetation;
    if (ndvi < 0.2) return bareSoil;
    if (ndvi < 0.4) return stressed;
    if (ndvi < 0.6) return moderate;
    if (ndvi < 0.8) return healthy;
    return veryHealthy;
  }
}

/// NDVI Time Series Entry
class NdviTimePoint {
  final DateTime date;
  final double value;
  final double? cloudCover; // Percentage of cloud cover

  const NdviTimePoint({
    required this.date,
    required this.value,
    this.cloudCover,
  });

  NdviValue toNdviValue() => NdviValue(
        value: value,
        capturedAt: date,
      );
}

/// NDVI Statistics for a field
class NdviStatistics {
  final double current;
  final double average;
  final double min;
  final double max;
  final double trend; // Change over period (-1 to 1)
  final List<NdviTimePoint> history;
  final DateTime lastUpdated;

  const NdviStatistics({
    required this.current,
    required this.average,
    required this.min,
    required this.max,
    required this.trend,
    required this.history,
    required this.lastUpdated,
  });

  /// Trend direction
  TrendDirection get trendDirection {
    if (trend > 0.05) return TrendDirection.improving;
    if (trend < -0.05) return TrendDirection.declining;
    return TrendDirection.stable;
  }

  /// Current health category
  NdviHealthCategory get currentCategory => NdviHealthCategory.fromValue(current);

  /// Days since last update
  int get daysSinceUpdate => DateTime.now().difference(lastUpdated).inDays;

  factory NdviStatistics.fromHistory(List<NdviTimePoint> history) {
    if (history.isEmpty) {
      return NdviStatistics(
        current: 0,
        average: 0,
        min: 0,
        max: 0,
        trend: 0,
        history: [],
        lastUpdated: DateTime.now(),
      );
    }

    final sorted = List<NdviTimePoint>.from(history)
      ..sort((a, b) => a.date.compareTo(b.date));

    final values = sorted.map((e) => e.value).toList();
    final current = sorted.last.value;
    final average = values.reduce((a, b) => a + b) / values.length;
    final min = values.reduce((a, b) => a < b ? a : b);
    final max = values.reduce((a, b) => a > b ? a : b);

    // Calculate trend (simple linear regression slope)
    double trend = 0;
    if (sorted.length >= 2) {
      final first = sorted.first.value;
      final last = sorted.last.value;
      trend = (last - first) / (sorted.length - 1);
    }

    return NdviStatistics(
      current: current,
      average: average,
      min: min,
      max: max,
      trend: trend.clamp(-1.0, 1.0),
      history: sorted,
      lastUpdated: sorted.last.date,
    );
  }
}

/// Trend direction enum
enum TrendDirection {
  improving(labelAr: 'تحسن', labelEn: 'Improving', icon: Icons.trending_up, color: Color(0xFF4CAF50)),
  stable(labelAr: 'مستقر', labelEn: 'Stable', icon: Icons.trending_flat, color: Color(0xFFFFC107)),
  declining(labelAr: 'تراجع', labelEn: 'Declining', icon: Icons.trending_down, color: Color(0xFFF44336));

  final String labelAr;
  final String labelEn;
  final IconData icon;
  final Color color;

  const TrendDirection({
    required this.labelAr,
    required this.labelEn,
    required this.icon,
    required this.color,
  });
}
