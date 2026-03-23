/// NDVI Test Fixtures - بيانات اختبار NDVI
///
/// Comprehensive test fixtures for NDVI feature testing including:
/// - Mock NDVI data points with realistic values (0.0-1.0)
/// - Time series data for trend analysis
/// - Edge cases (cloud cover, no data)
/// - JSON response fixtures
library;

/// NDVI Fixtures for unit tests
class NdviFixtures {
  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Value Fixtures - قيم NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  /// Healthy vegetation NDVI value (صحي)
  static const double healthyNdvi = 0.72;

  /// Very healthy vegetation NDVI value (ممتاز)
  static const double veryHealthyNdvi = 0.85;

  /// Moderate vegetation NDVI value (متوسط)
  static const double moderateNdvi = 0.45;

  /// Stressed vegetation NDVI value (إجهاد)
  static const double stressedNdvi = 0.28;

  /// Bare soil NDVI value (تربة جرداء)
  static const double bareSoilNdvi = 0.12;

  /// Water/non-vegetation NDVI value (مياه/غير نباتي)
  static const double waterNdvi = -0.35;

  /// Minimum valid NDVI
  static const double minNdvi = -1.0;

  /// Maximum valid NDVI
  static const double maxNdvi = 1.0;

  // ═══════════════════════════════════════════════════════════════════════════
  // Category Boundary Values - قيم حدود الفئات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Non-vegetation threshold
  static const double nonVegetationThreshold = 0.0;

  /// Bare soil threshold
  static const double bareSoilThreshold = 0.2;

  /// Stressed threshold
  static const double stressedThreshold = 0.4;

  /// Moderate threshold
  static const double moderateThreshold = 0.6;

  /// Healthy threshold
  static const double healthyThreshold = 0.8;

  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Data Point JSON Fixtures
  // ═══════════════════════════════════════════════════════════════════════════

  /// Single healthy NDVI data point JSON
  static Map<String, dynamic> get healthyDataPointJson => {
        'date': '2026-01-15T10:30:00Z',
        'value': healthyNdvi,
        'source': 'sentinel-2',
        'cloud_coverage': 5.0,
      };

  /// Single stressed NDVI data point JSON
  static Map<String, dynamic> get stressedDataPointJson => {
        'date': '2026-01-10T10:30:00Z',
        'value': stressedNdvi,
        'source': 'sentinel-2',
        'cloud_coverage': 10.0,
      };

  /// Data point with high cloud coverage
  static Map<String, dynamic> get cloudyDataPointJson => {
        'date': '2026-01-12T10:30:00Z',
        'value': 0.5,
        'source': 'landsat-8',
        'cloud_coverage': 85.0,
      };

  /// Data point with alternative JSON keys
  static Map<String, dynamic> get alternativeKeysDataPointJson => {
        'timestamp': '2026-01-15T10:30:00Z',
        'ndvi': 0.65,
        'source': 'sentinel-2',
        'cloudCoverage': 8.0,
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Time Series Fixtures - سلسلة زمنية
  // ═══════════════════════════════════════════════════════════════════════════

  /// Improving trend time series (7 days, increasing NDVI)
  static List<Map<String, dynamic>> get improvingTrendJson => [
        {'date': '2026-01-01T10:00:00Z', 'value': 0.35, 'source': 'sentinel-2', 'cloud_coverage': 5.0},
        {'date': '2026-01-03T10:00:00Z', 'value': 0.42, 'source': 'sentinel-2', 'cloud_coverage': 8.0},
        {'date': '2026-01-05T10:00:00Z', 'value': 0.48, 'source': 'sentinel-2', 'cloud_coverage': 3.0},
        {'date': '2026-01-07T10:00:00Z', 'value': 0.55, 'source': 'sentinel-2', 'cloud_coverage': 12.0},
        {'date': '2026-01-09T10:00:00Z', 'value': 0.62, 'source': 'sentinel-2', 'cloud_coverage': 7.0},
        {'date': '2026-01-11T10:00:00Z', 'value': 0.68, 'source': 'sentinel-2', 'cloud_coverage': 4.0},
        {'date': '2026-01-13T10:00:00Z', 'value': 0.72, 'source': 'sentinel-2', 'cloud_coverage': 6.0},
      ];

  /// Declining trend time series (7 days, decreasing NDVI)
  static List<Map<String, dynamic>> get decliningTrendJson => [
        {'date': '2026-01-01T10:00:00Z', 'value': 0.75, 'source': 'sentinel-2', 'cloud_coverage': 5.0},
        {'date': '2026-01-03T10:00:00Z', 'value': 0.68, 'source': 'sentinel-2', 'cloud_coverage': 8.0},
        {'date': '2026-01-05T10:00:00Z', 'value': 0.60, 'source': 'sentinel-2', 'cloud_coverage': 3.0},
        {'date': '2026-01-07T10:00:00Z', 'value': 0.52, 'source': 'sentinel-2', 'cloud_coverage': 12.0},
        {'date': '2026-01-09T10:00:00Z', 'value': 0.45, 'source': 'sentinel-2', 'cloud_coverage': 7.0},
        {'date': '2026-01-11T10:00:00Z', 'value': 0.38, 'source': 'sentinel-2', 'cloud_coverage': 4.0},
        {'date': '2026-01-13T10:00:00Z', 'value': 0.30, 'source': 'sentinel-2', 'cloud_coverage': 6.0},
      ];

  /// Stable trend time series (7 days, minimal change)
  static List<Map<String, dynamic>> get stableTrendJson => [
        {'date': '2026-01-01T10:00:00Z', 'value': 0.58, 'source': 'sentinel-2', 'cloud_coverage': 5.0},
        {'date': '2026-01-03T10:00:00Z', 'value': 0.56, 'source': 'sentinel-2', 'cloud_coverage': 8.0},
        {'date': '2026-01-05T10:00:00Z', 'value': 0.59, 'source': 'sentinel-2', 'cloud_coverage': 3.0},
        {'date': '2026-01-07T10:00:00Z', 'value': 0.57, 'source': 'sentinel-2', 'cloud_coverage': 12.0},
        {'date': '2026-01-09T10:00:00Z', 'value': 0.58, 'source': 'sentinel-2', 'cloud_coverage': 7.0},
        {'date': '2026-01-11T10:00:00Z', 'value': 0.60, 'source': 'sentinel-2', 'cloud_coverage': 4.0},
        {'date': '2026-01-13T10:00:00Z', 'value': 0.58, 'source': 'sentinel-2', 'cloud_coverage': 6.0},
      ];

  /// Empty time series
  static List<Map<String, dynamic>> get emptyTimeSeriesJson => [];

  /// Single point time series
  static List<Map<String, dynamic>> get singlePointTimeSeriesJson => [
        {'date': '2026-01-15T10:00:00Z', 'value': 0.65, 'source': 'sentinel-2', 'cloud_coverage': 5.0},
      ];

  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Analysis Fixtures - تحليل NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  /// Complete NDVI analysis JSON for healthy field
  static Map<String, dynamic> get healthyFieldAnalysisJson => {
        'field_id': 'field-001',
        'current_ndvi': 0.72,
        'previous_ndvi': 0.65,
        'change_rate': 10.77,
        'health_status': 'good',
        'time_series': improvingTrendJson,
        'analyzed_at': '2026-01-15T12:00:00Z',
        'image_url': 'https://api.sahool.io/ndvi/field-001/image.png',
        'indices': {
          'NDVI': 0.72,
          'NDWI': 0.35,
          'EVI': 0.45,
          'NDRE': 0.28,
        },
      };

  /// NDVI analysis JSON for stressed field
  static Map<String, dynamic> get stressedFieldAnalysisJson => {
        'field_id': 'field-002',
        'current_ndvi': 0.28,
        'previous_ndvi': 0.45,
        'change_rate': -37.78,
        'health_status': 'poor',
        'time_series': decliningTrendJson,
        'analyzed_at': '2026-01-15T12:00:00Z',
        'image_url': null,
        'indices': {
          'NDVI': 0.28,
          'NDWI': 0.15,
          'EVI': 0.22,
          'NDRE': 0.12,
        },
      };

  /// NDVI analysis with alternative JSON keys
  static Map<String, dynamic> get alternativeKeysAnalysisJson => {
        'fieldId': 'field-003',
        'currentNdvi': 0.55,
        'previousNdvi': 0.52,
        'changeRate': 5.77,
        'healthStatus': 'fair',
        'timeSeries': stableTrendJson,
        'analyzedAt': '2026-01-15T12:00:00Z',
        'imageUrl': 'https://api.sahool.io/ndvi/field-003/image.png',
      };

  /// NDVI analysis with empty time series
  static Map<String, dynamic> get emptyTimeSeriesAnalysisJson => {
        'field_id': 'field-004',
        'current_ndvi': 0.5,
        'previous_ndvi': 0.5,
        'change_rate': 0.0,
        'health_status': 'unknown',
        'time_series': [],
        'analyzed_at': '2026-01-15T12:00:00Z',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Vegetation Index Fixtures - مؤشرات نباتية
  // ═══════════════════════════════════════════════════════════════════════════

  /// NDVI vegetation index JSON
  static Map<String, dynamic> get ndviIndexJson => {
        'name': 'Normalized Difference Vegetation Index',
        'name_ar': 'مؤشر الفرق المعياري للغطاء النباتي',
        'code': 'NDVI',
        'value': 0.72,
        'unit': '',
        'description': 'Measures vegetation health using red and near-infrared reflectance',
        'description_ar': 'يقيس صحة النبات باستخدام انعكاس الأحمر والأشعة تحت الحمراء القريبة',
      };

  /// NDWI vegetation index JSON
  static Map<String, dynamic> get ndwiIndexJson => {
        'name': 'Normalized Difference Water Index',
        'nameAr': 'مؤشر الفرق المعياري للمياه',
        'code': 'NDWI',
        'value': 0.35,
        'unit': '',
        'description': 'Measures water content in vegetation',
        'descriptionAr': 'يقيس محتوى الماء في النبات',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Alert Fixtures - تنبيهات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Low vegetation alert (critical)
  static Map<String, dynamic> get lowVegetationAlertJson => {
        'id': 'alert-001',
        'type': 'ndvi_critical',
        'severity': 'critical',
        'field_id': 'field-002',
        'title': 'Critical Vegetation Health',
        'title_ar': 'صحة النبات حرجة',
        'message': 'NDVI dropped below 0.3 threshold',
        'message_ar': 'انخفض مؤشر NDVI تحت عتبة 0.3',
        'ndvi_value': 0.25,
        'threshold': 0.3,
        'created_at': '2026-01-15T08:00:00Z',
      };

  /// Declining trend alert (warning)
  static Map<String, dynamic> get decliningTrendAlertJson => {
        'id': 'alert-002',
        'type': 'ndvi_declining',
        'severity': 'warning',
        'field_id': 'field-003',
        'title': 'Declining Vegetation Trend',
        'title_ar': 'اتجاه تراجعي في صحة النبات',
        'message': 'NDVI has been declining for 2 weeks',
        'message_ar': 'مؤشر NDVI في تراجع منذ أسبوعين',
        'ndvi_value': 0.45,
        'change_rate': -15.0,
        'created_at': '2026-01-15T08:00:00Z',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Edge Cases - حالات خاصة
  // ═══════════════════════════════════════════════════════════════════════════

  /// NDVI value at exact boundary (0.0)
  static const double boundaryZeroNdvi = 0.0;

  /// NDVI value just below boundary
  static const double justBelowHealthyNdvi = 0.599;

  /// NDVI value just above boundary
  static const double justAboveHealthyNdvi = 0.601;

  /// No data value (used in raster processing)
  static const double noDataValue = -999.0;

  /// Invalid NDVI (out of range)
  static const double invalidNdviHigh = 1.5;

  /// Invalid NDVI (out of range)
  static const double invalidNdviLow = -1.5;

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods - طرق مساعدة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate time series with specific length and trend
  static List<Map<String, dynamic>> generateTimeSeries({
    required int days,
    required double startValue,
    required double endValue,
    double cloudCoverage = 10.0,
    String source = 'sentinel-2',
  }) {
    final result = <Map<String, dynamic>>[];
    final increment = (endValue - startValue) / (days - 1);

    for (int i = 0; i < days; i++) {
      final date = DateTime(2026, 1, 1).add(Duration(days: i * 2));
      final value = (startValue + increment * i).clamp(-1.0, 1.0);

      result.add({
        'date': date.toIso8601String(),
        'value': value,
        'source': source,
        'cloud_coverage': cloudCoverage,
      });
    }

    return result;
  }

  /// Generate NDVI raster data array
  static List<double> generateRasterData({
    int width = 10,
    int height = 10,
    double baseValue = 0.5,
    double variation = 0.1,
    bool includeNoData = false,
  }) {
    final result = <double>[];

    for (int i = 0; i < width * height; i++) {
      if (includeNoData && i % 17 == 0) {
        result.add(noDataValue);
      } else {
        // Simple variation pattern
        final offset = (i % 5 - 2) * variation / 2;
        result.add((baseValue + offset).clamp(-1.0, 1.0));
      }
    }

    return result;
  }

  /// Create NdviRecord-compatible data for testing
  static List<Map<String, dynamic>> generateNdviRecords({
    required int count,
    required double startValue,
    required double endValue,
  }) {
    final result = <Map<String, dynamic>>[];
    final increment = count > 1 ? (endValue - startValue) / (count - 1) : 0.0;

    for (int i = 0; i < count; i++) {
      final date = DateTime(2026, 1, 1).add(Duration(days: i * 2));
      final value = (startValue + increment * i).clamp(0.0, 1.0);

      result.add({
        'date': date.toIso8601String(),
        'value': value,
      });
    }

    return result;
  }
}
