import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/satellite/data/models/ndvi_data.dart';

void main() {
  group('NdviDataPoint', () {
    test('fromJson parses standard format', () {
      final json = {
        'date': '2026-01-15T00:00:00.000',
        'value': 0.72,
        'source': 'sentinel-2',
        'cloud_coverage': 10.5,
      };

      final point = NdviDataPoint.fromJson(json);
      expect(point.value, 0.72);
      expect(point.source, 'sentinel-2');
      expect(point.cloudCoverage, 10.5);
    });

    test('fromJson handles alternative key names', () {
      final json = {
        'timestamp': '2026-02-01T00:00:00.000',
        'ndvi': 0.65,
        'source': 'landsat-8',
        'cloudCoverage': 5.0,
      };

      final point = NdviDataPoint.fromJson(json);
      expect(point.value, 0.65);
      expect(point.cloudCoverage, 5.0);
    });

    test('fromJson defaults cloud coverage to 0', () {
      final json = {
        'date': '2026-01-01T00:00:00.000',
        'value': 0.5,
        'source': 'sentinel-2',
      };
      final point = NdviDataPoint.fromJson(json);
      expect(point.cloudCoverage, 0.0);
    });

    test('toJson produces correct format', () {
      final point = NdviDataPoint(
        date: DateTime(2026, 3, 1),
        value: 0.8,
        source: 'sentinel-2',
        cloudCoverage: 15.0,
      );

      final json = point.toJson();
      expect(json['value'], 0.8);
      expect(json['source'], 'sentinel-2');
      expect(json['cloud_coverage'], 15.0);
    });

    test('equality works with Equatable', () {
      final a = NdviDataPoint(
        date: DateTime(2026, 1, 1),
        value: 0.5,
        source: 'sentinel-2',
      );
      final b = NdviDataPoint(
        date: DateTime(2026, 1, 1),
        value: 0.5,
        source: 'sentinel-2',
      );
      expect(a, equals(b));
    });

    test('copyWith creates modified copy', () {
      final original = NdviDataPoint(
        date: DateTime(2026, 1, 1),
        value: 0.5,
        source: 'sentinel-2',
      );
      final copy = original.copyWith(value: 0.8);
      expect(copy.value, 0.8);
      expect(copy.source, 'sentinel-2');
    });
  });

  group('VegetationHealth', () {
    test('fromNdvi classifies correctly', () {
      expect(VegetationHealth.fromNdvi(0.9), VegetationHealth.excellent);
      expect(VegetationHealth.fromNdvi(0.7), VegetationHealth.good);
      expect(VegetationHealth.fromNdvi(0.5), VegetationHealth.fair);
      expect(VegetationHealth.fromNdvi(0.3), VegetationHealth.poor);
      expect(VegetationHealth.fromNdvi(0.1), VegetationHealth.critical);
    });

    test('fromString parses health status strings', () {
      expect(VegetationHealth.fromString('excellent'), VegetationHealth.excellent);
      expect(VegetationHealth.fromString('good'), VegetationHealth.good);
      expect(VegetationHealth.fromString('fair'), VegetationHealth.fair);
      expect(VegetationHealth.fromString('poor'), VegetationHealth.poor);
      expect(VegetationHealth.fromString('critical'), VegetationHealth.critical);
    });

    test('fromString returns unknown for invalid input', () {
      expect(VegetationHealth.fromString('invalid'), VegetationHealth.unknown);
    });

    test('fromString is case insensitive', () {
      expect(VegetationHealth.fromString('EXCELLENT'), VegetationHealth.excellent);
      expect(VegetationHealth.fromString('Good'), VegetationHealth.good);
    });

    test('has Arabic labels', () {
      expect(VegetationHealth.excellent.arabicLabel, 'ممتاز');
      expect(VegetationHealth.good.arabicLabel, 'جيد');
      expect(VegetationHealth.fair.arabicLabel, 'متوسط');
      expect(VegetationHealth.poor.arabicLabel, 'ضعيف');
      expect(VegetationHealth.critical.arabicLabel, 'حرج');
    });

    test('getLabel returns correct language', () {
      expect(VegetationHealth.good.getLabel(true), 'جيد');
      expect(VegetationHealth.good.getLabel(false), 'good');
    });
  });

  group('NdviAnalysis', () {
    test('fromJson parses complete analysis', () {
      final json = {
        'field_id': 'field-001',
        'current_ndvi': 0.72,
        'previous_ndvi': 0.65,
        'change_rate': 10.77,
        'health_status': 'good',
        'time_series': [
          {'date': '2026-01-01T00:00:00.000', 'value': 0.65, 'source': 'sentinel-2'},
          {'date': '2026-02-01T00:00:00.000', 'value': 0.72, 'source': 'sentinel-2'},
        ],
        'analyzed_at': '2026-03-01T00:00:00.000',
        'indices': {'NDVI': 0.72, 'NDWI': 0.35, 'EVI': 0.55},
      };

      final analysis = NdviAnalysis.fromJson(json);
      expect(analysis.fieldId, 'field-001');
      expect(analysis.currentNdvi, 0.72);
      expect(analysis.previousNdvi, 0.65);
      expect(analysis.changeRate, 10.77);
      expect(analysis.health, VegetationHealth.good);
      expect(analysis.timeSeries, hasLength(2));
      expect(analysis.indices!['NDVI'], 0.72);
      expect(analysis.indices!['EVI'], 0.55);
    });

    test('fromJson handles camelCase keys', () {
      final json = {
        'fieldId': 'field-002',
        'currentNdvi': 0.5,
        'previousNdvi': 0.4,
        'changeRate': 25.0,
        'healthStatus': 'fair',
        'timeSeries': [],
        'analyzedAt': '2026-01-01T00:00:00.000',
      };

      final analysis = NdviAnalysis.fromJson(json);
      expect(analysis.fieldId, 'field-002');
      expect(analysis.currentNdvi, 0.5);
      expect(analysis.health, VegetationHealth.fair);
    });

    test('toJson produces correct format', () {
      final analysis = NdviAnalysis(
        fieldId: 'field-003',
        currentNdvi: 0.8,
        previousNdvi: 0.7,
        changeRate: 14.3,
        health: VegetationHealth.excellent,
        timeSeries: [],
        analyzedAt: DateTime(2026, 3, 1),
      );

      final json = analysis.toJson();
      expect(json['field_id'], 'field-003');
      expect(json['current_ndvi'], 0.8);
      expect(json['health_status'], 'excellent');
    });

    test('equality works with Equatable', () {
      final a = NdviAnalysis(
        fieldId: 'f1',
        currentNdvi: 0.5,
        previousNdvi: 0.4,
        changeRate: 25.0,
        health: VegetationHealth.fair,
        timeSeries: [],
        analyzedAt: DateTime(2026, 1, 1),
      );
      final b = NdviAnalysis(
        fieldId: 'f1',
        currentNdvi: 0.5,
        previousNdvi: 0.4,
        changeRate: 25.0,
        health: VegetationHealth.fair,
        timeSeries: [],
        analyzedAt: DateTime(2026, 1, 1),
      );
      expect(a, equals(b));
    });
  });

  group('VegetationIndex', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'name': 'Vegetation Index',
        'name_ar': 'مؤشر الغطاء النباتي',
        'code': 'NDVI',
        'value': 0.72,
        'unit': '',
        'description': 'Normalized Difference Vegetation Index',
        'description_ar': 'مؤشر الاختلاف الطبيعي للنباتات',
      };

      final index = VegetationIndex.fromJson(json);
      expect(index.code, 'NDVI');
      expect(index.value, 0.72);
      expect(index.nameAr, 'مؤشر الغطاء النباتي');

      final exported = index.toJson();
      expect(exported['code'], 'NDVI');
    });

    test('equality works with Equatable', () {
      const a = VegetationIndex(
        name: 'NDVI',
        nameAr: 'م.غ.ن',
        code: 'NDVI',
        value: 0.5,
      );
      const b = VegetationIndex(
        name: 'NDVI',
        nameAr: 'م.غ.ن',
        code: 'NDVI',
        value: 0.5,
      );
      expect(a, equals(b));
    });
  });
}
