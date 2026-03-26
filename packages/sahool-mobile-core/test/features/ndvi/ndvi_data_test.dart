/// NDVI Data Tests - اختبارات بيانات NDVI
///
/// Comprehensive unit tests for:
/// - NdviDataPoint model
/// - NdviAnalysis model
/// - VegetationHealth enum
/// - VegetationIndex model
/// - JSON serialization/deserialization
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/features/satellite/data/models/ndvi_data.dart';

import 'ndvi_fixtures.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // NdviDataPoint Tests - اختبارات نقطة بيانات NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviDataPoint', () {
    group('constructor - المنشئ', () {
      test('should create with required fields', () {
        // Arrange & Act
        final point = NdviDataPoint(
          date: DateTime(2026, 1, 15),
          value: 0.65,
          source: 'sentinel-2',
        );

        // Assert
        expect(point.date, equals(DateTime(2026, 1, 15)));
        expect(point.value, equals(0.65));
        expect(point.source, equals('sentinel-2'));
        expect(point.cloudCoverage, equals(0.0));
      });

      test('should create with cloud coverage', () {
        // Arrange & Act
        final point = NdviDataPoint(
          date: DateTime(2026, 1, 15),
          value: 0.65,
          source: 'sentinel-2',
          cloudCoverage: 15.5,
        );

        // Assert
        expect(point.cloudCoverage, equals(15.5));
      });
    });

    group('fromJson - من JSON', () {
      test('should parse standard JSON', () {
        // Arrange
        final json = NdviFixtures.healthyDataPointJson;

        // Act
        final point = NdviDataPoint.fromJson(json);

        // Assert
        expect(point.value, equals(NdviFixtures.healthyNdvi));
        expect(point.source, equals('sentinel-2'));
        expect(point.cloudCoverage, equals(5.0));
      });

      test('should parse JSON with alternative keys', () {
        // Arrange
        final json = NdviFixtures.alternativeKeysDataPointJson;

        // Act
        final point = NdviDataPoint.fromJson(json);

        // Assert
        expect(point.value, equals(0.65));
        expect(point.cloudCoverage, equals(8.0));
      });

      test('should use default values for missing fields', () {
        // Arrange
        final json = {
          'date': '2026-01-15T10:00:00Z',
          'value': 0.5,
        };

        // Act
        final point = NdviDataPoint.fromJson(json);

        // Assert
        expect(point.source, equals('sentinel-2'));
        expect(point.cloudCoverage, equals(0.0));
      });

      test('should parse timestamp key as date', () {
        // Arrange
        final json = {
          'timestamp': '2026-01-15T10:00:00Z',
          'value': 0.5,
          'source': 'landsat-8',
        };

        // Act
        final point = NdviDataPoint.fromJson(json);

        // Assert
        expect(point.date, equals(DateTime.utc(2026, 1, 15, 10)));
      });

      test('should parse ndvi key as value', () {
        // Arrange
        final json = {
          'date': '2026-01-15T10:00:00Z',
          'ndvi': 0.72,
          'source': 'sentinel-2',
        };

        // Act
        final point = NdviDataPoint.fromJson(json);

        // Assert
        expect(point.value, equals(0.72));
      });
    });

    group('toJson - إلى JSON', () {
      test('should convert to JSON correctly', () {
        // Arrange
        final point = NdviDataPoint(
          date: DateTime.utc(2026, 1, 15, 10, 30),
          value: 0.65,
          source: 'sentinel-2',
          cloudCoverage: 12.5,
        );

        // Act
        final json = point.toJson();

        // Assert
        expect(json['date'], equals('2026-01-15T10:30:00.000Z'));
        expect(json['value'], equals(0.65));
        expect(json['source'], equals('sentinel-2'));
        expect(json['cloud_coverage'], equals(12.5));
      });
    });

    group('equality - التساوي', () {
      test('should be equal for same values', () {
        // Arrange
        final point1 = NdviDataPoint(
          date: DateTime(2026, 1, 15),
          value: 0.65,
          source: 'sentinel-2',
          cloudCoverage: 10.0,
        );
        final point2 = NdviDataPoint(
          date: DateTime(2026, 1, 15),
          value: 0.65,
          source: 'sentinel-2',
          cloudCoverage: 10.0,
        );

        // Assert
        expect(point1, equals(point2));
      });

      test('should not be equal for different values', () {
        // Arrange
        final point1 = NdviDataPoint(
          date: DateTime(2026, 1, 15),
          value: 0.65,
          source: 'sentinel-2',
        );
        final point2 = NdviDataPoint(
          date: DateTime(2026, 1, 15),
          value: 0.72,
          source: 'sentinel-2',
        );

        // Assert
        expect(point1, isNot(equals(point2)));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviAnalysis Tests - اختبارات تحليل NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviAnalysis', () {
    group('fromJson - من JSON', () {
      test('should parse healthy field analysis', () {
        // Arrange
        final json = NdviFixtures.healthyFieldAnalysisJson;

        // Act
        final analysis = NdviAnalysis.fromJson(json);

        // Assert
        expect(analysis.fieldId, equals('field-001'));
        expect(analysis.currentNdvi, equals(0.72));
        expect(analysis.previousNdvi, equals(0.65));
        expect(analysis.changeRate, equals(10.77));
        expect(analysis.health, equals(VegetationHealth.good));
        expect(analysis.timeSeries.length, equals(7));
        expect(analysis.imageUrl, isNotNull);
        expect(analysis.indices, isNotNull);
        expect(analysis.indices!['NDVI'], equals(0.72));
      });

      test('should parse stressed field analysis', () {
        // Arrange
        final json = NdviFixtures.stressedFieldAnalysisJson;

        // Act
        final analysis = NdviAnalysis.fromJson(json);

        // Assert
        expect(analysis.fieldId, equals('field-002'));
        expect(analysis.currentNdvi, equals(0.28));
        expect(analysis.health, equals(VegetationHealth.poor));
        expect(analysis.changeRate, lessThan(0));
      });

      test('should parse JSON with alternative keys', () {
        // Arrange
        final json = NdviFixtures.alternativeKeysAnalysisJson;

        // Act
        final analysis = NdviAnalysis.fromJson(json);

        // Assert
        expect(analysis.fieldId, equals('field-003'));
        expect(analysis.currentNdvi, equals(0.55));
        expect(analysis.health, equals(VegetationHealth.fair));
      });

      test('should handle empty time series', () {
        // Arrange
        final json = NdviFixtures.emptyTimeSeriesAnalysisJson;

        // Act
        final analysis = NdviAnalysis.fromJson(json);

        // Assert
        expect(analysis.timeSeries, isEmpty);
      });

      test('should handle null image URL', () {
        // Arrange
        final json = NdviFixtures.stressedFieldAnalysisJson;

        // Act
        final analysis = NdviAnalysis.fromJson(json);

        // Assert
        expect(analysis.imageUrl, isNull);
      });

      test('should handle null indices', () {
        // Arrange
        final json = NdviFixtures.emptyTimeSeriesAnalysisJson;

        // Act
        final analysis = NdviAnalysis.fromJson(json);

        // Assert
        expect(analysis.indices, isNull);
      });
    });

    group('toJson - إلى JSON', () {
      test('should convert to JSON correctly', () {
        // Arrange
        final analysis = NdviAnalysis.fromJson(NdviFixtures.healthyFieldAnalysisJson);

        // Act
        final json = analysis.toJson();

        // Assert
        expect(json['field_id'], equals('field-001'));
        expect(json['current_ndvi'], equals(0.72));
        expect(json['previous_ndvi'], equals(0.65));
        expect(json['change_rate'], equals(10.77));
        expect(json['health_status'], equals('good'));
        expect(json['time_series'], isA<List>());
      });
    });

    group('equality - التساوي', () {
      test('should be equal for same values', () {
        // Arrange
        final analysis1 = NdviAnalysis.fromJson(NdviFixtures.healthyFieldAnalysisJson);
        final analysis2 = NdviAnalysis.fromJson(NdviFixtures.healthyFieldAnalysisJson);

        // Assert
        expect(analysis1, equals(analysis2));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // VegetationHealth Tests - اختبارات صحة النباتات
  // ═══════════════════════════════════════════════════════════════════════════

  group('VegetationHealth', () {
    group('values - القيم', () {
      test('should have correct thresholds', () {
        expect(VegetationHealth.excellent.threshold, equals(0.8));
        expect(VegetationHealth.good.threshold, equals(0.6));
        expect(VegetationHealth.fair.threshold, equals(0.4));
        expect(VegetationHealth.poor.threshold, equals(0.2));
        expect(VegetationHealth.critical.threshold, equals(0.0));
      });

      test('should have Arabic labels', () {
        expect(VegetationHealth.excellent.arabicLabel, equals('ممتاز'));
        expect(VegetationHealth.good.arabicLabel, equals('جيد'));
        expect(VegetationHealth.fair.arabicLabel, equals('متوسط'));
        expect(VegetationHealth.poor.arabicLabel, equals('ضعيف'));
        expect(VegetationHealth.critical.arabicLabel, equals('حرج'));
        expect(VegetationHealth.unknown.arabicLabel, equals('غير معروف'));
      });
    });

    group('fromString - من النص', () {
      test('should parse excellent', () {
        expect(
          VegetationHealth.fromString('excellent'),
          equals(VegetationHealth.excellent),
        );
      });

      test('should parse good', () {
        expect(
          VegetationHealth.fromString('good'),
          equals(VegetationHealth.good),
        );
      });

      test('should parse fair', () {
        expect(
          VegetationHealth.fromString('fair'),
          equals(VegetationHealth.fair),
        );
      });

      test('should parse poor', () {
        expect(
          VegetationHealth.fromString('poor'),
          equals(VegetationHealth.poor),
        );
      });

      test('should parse critical', () {
        expect(
          VegetationHealth.fromString('critical'),
          equals(VegetationHealth.critical),
        );
      });

      test('should be case insensitive', () {
        expect(
          VegetationHealth.fromString('EXCELLENT'),
          equals(VegetationHealth.excellent),
        );
        expect(
          VegetationHealth.fromString('Good'),
          equals(VegetationHealth.good),
        );
      });

      test('should return unknown for invalid string', () {
        expect(
          VegetationHealth.fromString('invalid'),
          equals(VegetationHealth.unknown),
        );
      });
    });

    group('fromNdvi - من NDVI', () {
      test('should return excellent for NDVI >= 0.8', () {
        expect(VegetationHealth.fromNdvi(0.85), equals(VegetationHealth.excellent));
        expect(VegetationHealth.fromNdvi(0.80), equals(VegetationHealth.excellent));
        expect(VegetationHealth.fromNdvi(1.0), equals(VegetationHealth.excellent));
      });

      test('should return good for NDVI 0.6-0.8', () {
        expect(VegetationHealth.fromNdvi(0.72), equals(VegetationHealth.good));
        expect(VegetationHealth.fromNdvi(0.60), equals(VegetationHealth.good));
        expect(VegetationHealth.fromNdvi(0.79), equals(VegetationHealth.good));
      });

      test('should return fair for NDVI 0.4-0.6', () {
        expect(VegetationHealth.fromNdvi(0.45), equals(VegetationHealth.fair));
        expect(VegetationHealth.fromNdvi(0.40), equals(VegetationHealth.fair));
        expect(VegetationHealth.fromNdvi(0.59), equals(VegetationHealth.fair));
      });

      test('should return poor for NDVI 0.2-0.4', () {
        expect(VegetationHealth.fromNdvi(0.28), equals(VegetationHealth.poor));
        expect(VegetationHealth.fromNdvi(0.20), equals(VegetationHealth.poor));
        expect(VegetationHealth.fromNdvi(0.39), equals(VegetationHealth.poor));
      });

      test('should return critical for NDVI < 0.2', () {
        expect(VegetationHealth.fromNdvi(0.15), equals(VegetationHealth.critical));
        expect(VegetationHealth.fromNdvi(0.0), equals(VegetationHealth.critical));
        expect(VegetationHealth.fromNdvi(-0.5), equals(VegetationHealth.critical));
      });
    });

    group('getLabel - الحصول على التسمية', () {
      test('should return Arabic label when isArabic is true', () {
        expect(
          VegetationHealth.excellent.getLabel(true),
          equals('ممتاز'),
        );
      });

      test('should return English label when isArabic is false', () {
        expect(
          VegetationHealth.excellent.getLabel(false),
          equals('excellent'),
        );
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // VegetationIndex Tests - اختبارات مؤشر النباتات
  // ═══════════════════════════════════════════════════════════════════════════

  group('VegetationIndex', () {
    group('fromJson - من JSON', () {
      test('should parse NDVI index', () {
        // Arrange
        final json = NdviFixtures.ndviIndexJson;

        // Act
        final index = VegetationIndex.fromJson(json);

        // Assert
        expect(index.name, equals('Normalized Difference Vegetation Index'));
        expect(index.nameAr, equals('مؤشر الفرق المعياري للغطاء النباتي'));
        expect(index.code, equals('NDVI'));
        expect(index.value, equals(0.72));
      });

      test('should parse with alternative keys', () {
        // Arrange
        final json = NdviFixtures.ndwiIndexJson;

        // Act
        final index = VegetationIndex.fromJson(json);

        // Assert
        expect(index.nameAr, equals('مؤشر الفرق المعياري للمياه'));
        expect(index.descriptionAr, equals('يقيس محتوى الماء في النبات'));
      });

      test('should handle missing optional fields', () {
        // Arrange
        final json = {
          'name': 'Test Index',
          'code': 'TEST',
          'value': 0.5,
        };

        // Act
        final index = VegetationIndex.fromJson(json);

        // Assert
        expect(index.nameAr, equals(''));
        expect(index.unit, equals(''));
        expect(index.description, equals(''));
      });
    });

    group('toJson - إلى JSON', () {
      test('should convert to JSON correctly', () {
        // Arrange
        const index = VegetationIndex(
          name: 'NDVI',
          nameAr: 'مؤشر NDVI',
          code: 'NDVI',
          value: 0.72,
          unit: '',
          description: 'Vegetation health',
          descriptionAr: 'صحة النبات',
        );

        // Act
        final json = index.toJson();

        // Assert
        expect(json['name'], equals('NDVI'));
        expect(json['name_ar'], equals('مؤشر NDVI'));
        expect(json['code'], equals('NDVI'));
        expect(json['value'], equals(0.72));
      });
    });

    group('equality - التساوي', () {
      test('should be equal for same values', () {
        // Arrange
        const index1 = VegetationIndex(
          name: 'NDVI',
          nameAr: 'مؤشر NDVI',
          code: 'NDVI',
          value: 0.72,
        );
        const index2 = VegetationIndex(
          name: 'NDVI',
          nameAr: 'مؤشر NDVI',
          code: 'NDVI',
          value: 0.72,
        );

        // Assert
        expect(index1, equals(index2));
      });

      test('should not be equal for different values', () {
        // Arrange
        const index1 = VegetationIndex(
          name: 'NDVI',
          nameAr: 'مؤشر NDVI',
          code: 'NDVI',
          value: 0.72,
        );
        const index2 = VegetationIndex(
          name: 'NDWI',
          nameAr: 'مؤشر NDWI',
          code: 'NDWI',
          value: 0.35,
        );

        // Assert
        expect(index1, isNot(equals(index2)));
      });
    });
  });
}
