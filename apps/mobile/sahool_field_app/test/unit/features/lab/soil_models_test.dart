import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/lab/data/soil_analysis_api.dart';

void main() {
  group('SoilSampleModel', () {
    group('fromJson', () {
      test('should parse complete JSON correctly', () {
        final json = {
          'id': 'sample-001',
          'barcode': 'BC-2026-001',
          'type': 'soil',
          'status': 'analyzed',
          'experiment_name': 'تجربة القمح 2026',
          'plot_code': 'P-01',
          'collected_by': 'أحمد',
          'field_id': 'field-001',
          'notes': 'عينة من العمق 30 سم',
          'collected_at': '2026-02-15T08:00:00Z',
          'received_at': '2026-02-15T12:00:00Z',
          'analyzed_at': '2026-02-16T14:00:00Z',
          'results': {'pH': 7.2, 'nitrogen': 18},
          'metadata': {'depth_cm': 30},
        };

        final model = SoilSampleModel.fromJson(json);

        expect(model.id, 'sample-001');
        expect(model.barcode, 'BC-2026-001');
        expect(model.type, 'soil');
        expect(model.status, 'analyzed');
        expect(model.experimentName, 'تجربة القمح 2026');
        expect(model.plotCode, 'P-01');
        expect(model.collectedBy, 'أحمد');
        expect(model.fieldId, 'field-001');
        expect(model.notes, 'عينة من العمق 30 سم');
        expect(model.receivedAt, isNotNull);
        expect(model.analyzedAt, isNotNull);
        expect(model.results!['pH'], 7.2);
      });

      test('should handle missing optional fields', () {
        final json = <String, dynamic>{};

        final model = SoilSampleModel.fromJson(json);

        expect(model.id, '');
        expect(model.barcode, '');
        expect(model.type, 'soil');
        expect(model.status, 'pending');
        expect(model.fieldId, isNull);
        expect(model.notes, isNull);
        expect(model.receivedAt, isNull);
        expect(model.analyzedAt, isNull);
      });

      test('should parse alternative JSON keys', () {
        final json = {
          'id': 'sample-002',
          'barcode': 'BC-002',
          'experiment': 'تجربة 2', // alternative to 'experiment_name'
          'plot': 'P-02', // alternative to 'plot_code'
          'collected_at': '2026-02-16T08:00:00Z',
        };

        final model = SoilSampleModel.fromJson(json);

        expect(model.experimentName, 'تجربة 2');
        expect(model.plotCode, 'P-02');
      });
    });

    group('sampleStatus getter', () {
      test('should map pending status', () {
        final model = SoilSampleModel.fromJson(
            {'status': 'pending', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.sampleStatus, SampleStatus.pending);
      });

      test('should map in_transit status', () {
        final model = SoilSampleModel.fromJson(
            {'status': 'in_transit', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.sampleStatus, SampleStatus.inTransit);
      });

      test('should map received status', () {
        final model = SoilSampleModel.fromJson(
            {'status': 'received', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.sampleStatus, SampleStatus.received);
      });

      test('should map processing status', () {
        final model = SoilSampleModel.fromJson(
            {'status': 'processing', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.sampleStatus, SampleStatus.processing);
      });

      test('should map analyzed status', () {
        final model = SoilSampleModel.fromJson(
            {'status': 'analyzed', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.sampleStatus, SampleStatus.analyzed);
      });

      test('should default to pending for unknown status', () {
        final model = SoilSampleModel.fromJson(
            {'status': 'unknown', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.sampleStatus, SampleStatus.pending);
      });
    });

    group('typeAr getter', () {
      test('should return Arabic for soil type', () {
        final model = SoilSampleModel.fromJson(
            {'type': 'soil', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.typeAr, 'تربة');
      });

      test('should return Arabic for leaf type', () {
        final model = SoilSampleModel.fromJson(
            {'type': 'leaf', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.typeAr, 'أوراق');
      });

      test('should return Arabic for water type', () {
        final model = SoilSampleModel.fromJson(
            {'type': 'water', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.typeAr, 'ماء');
      });

      test('should return Arabic for fruit type', () {
        final model = SoilSampleModel.fromJson(
            {'type': 'fruit', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.typeAr, 'ثمار');
      });

      test('should return Arabic for seed type', () {
        final model = SoilSampleModel.fromJson(
            {'type': 'seed', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.typeAr, 'بذور');
      });

      test('should return raw type for unknown type', () {
        final model = SoilSampleModel.fromJson(
            {'type': 'custom', 'collected_at': '2026-01-01T00:00:00Z'});
        expect(model.typeAr, 'custom');
      });
    });
  });

  group('SamplesPageResponse', () {
    test('should parse samples key', () {
      final json = {
        'samples': [
          {'id': 's1', 'collected_at': '2026-01-01T00:00:00Z'},
          {'id': 's2', 'collected_at': '2026-01-01T00:00:00Z'},
        ],
        'total': 100,
        'page': 1,
        'limit': 50,
      };

      final page = SamplesPageResponse.fromJson(json);

      expect(page.samples.length, 2);
      expect(page.total, 100);
      expect(page.page, 1);
      expect(page.limit, 50);
    });

    test('should parse items key as fallback', () {
      final json = {
        'items': [
          {'id': 's1', 'collected_at': '2026-01-01T00:00:00Z'},
        ],
        'total': 1,
      };

      final page = SamplesPageResponse.fromJson(json);
      expect(page.samples.length, 1);
    });

    test('should parse data key as fallback', () {
      final json = {
        'data': [
          {'id': 's1', 'collected_at': '2026-01-01T00:00:00Z'},
        ],
        'total': 1,
      };

      final page = SamplesPageResponse.fromJson(json);
      expect(page.samples.length, 1);
    });

    test('should handle empty response', () {
      final page = SamplesPageResponse.fromJson(<String, dynamic>{});

      expect(page.samples, isEmpty);
      expect(page.total, 0);
      expect(page.page, 1);
      expect(page.limit, 50);
    });
  });

  group('AnalysisResultModel', () {
    test('should parse analysis result correctly', () {
      final json = {
        'sample_id': 'sample-001',
        'results': {
          'pH': 7.2,
          'nitrogen_ppm': 18,
          'phosphorus_ppm': 25,
          'potassium_ppm': 150,
          'organic_matter_pct': 2.5,
          'EC_dS_m': 1.2,
        },
        'interpretation': 'Nitrogen is below optimal range for wheat',
        'interpretation_ar': 'النيتروجين أقل من المدى المثالي للقمح',
        'recommendations': ['Apply urea at 46 kg/ha', 'Retest in 30 days'],
        'analyzed_at': '2026-02-16T14:00:00Z',
      };

      final result = AnalysisResultModel.fromJson(json);

      expect(result.sampleId, 'sample-001');
      expect(result.results['pH'], 7.2);
      expect(result.results['nitrogen_ppm'], 18);
      expect(result.interpretation, contains('Nitrogen'));
      expect(result.interpretationAr, contains('النيتروجين'));
      expect(result.recommendations.length, 2);
    });

    test('should handle missing optional fields', () {
      final result = AnalysisResultModel.fromJson(<String, dynamic>{});

      expect(result.sampleId, '');
      expect(result.results, isEmpty);
      expect(result.interpretation, isNull);
      expect(result.interpretationAr, isNull);
      expect(result.recommendations, isEmpty);
    });
  });

  group('LabStats', () {
    test('should parse lab statistics correctly', () {
      final json = {
        'total': 200,
        'pending': 30,
        'in_transit': 15,
        'processing': 25,
        'analyzed': 130,
        'avg_processing_days': 4.2,
      };

      final stats = LabStats.fromJson(json);

      expect(stats.totalSamples, 200);
      expect(stats.pendingSamples, 30);
      expect(stats.inTransitSamples, 15);
      expect(stats.processingSamples, 25);
      expect(stats.analyzedSamples, 130);
      expect(stats.averageProcessingDays, 4.2);
    });

    test('should parse total_samples alternative key', () {
      final json = {
        'total_samples': 50,
      };

      final stats = LabStats.fromJson(json);
      expect(stats.totalSamples, 50);
    });

    test('should handle missing fields with defaults', () {
      final stats = LabStats.fromJson(<String, dynamic>{});

      expect(stats.totalSamples, 0);
      expect(stats.pendingSamples, 0);
      expect(stats.inTransitSamples, 0);
      expect(stats.processingSamples, 0);
      expect(stats.analyzedSamples, 0);
      expect(stats.averageProcessingDays, 0.0);
    });
  });

  group('SampleStatus enum', () {
    test('should have all expected values', () {
      expect(SampleStatus.values, contains(SampleStatus.pending));
      expect(SampleStatus.values, contains(SampleStatus.inTransit));
      expect(SampleStatus.values, contains(SampleStatus.received));
      expect(SampleStatus.values, contains(SampleStatus.processing));
      expect(SampleStatus.values, contains(SampleStatus.analyzed));
      expect(SampleStatus.values.length, 5);
    });
  });
}
