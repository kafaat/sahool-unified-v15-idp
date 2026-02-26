import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';
import 'package:sahool_field_app/features/lab/data/soil_analysis_api.dart';

import '../../../mocks/mock_kong_gateway.dart';

void main() {
  late MockKongGatewayClient mockGateway;
  late SoilAnalysisApi api;

  setUpAll(() {
    registerFallbackValue(FakeKongService());
  });

  setUp(() {
    mockGateway = MockKongGatewayClient();
    api = SoilAnalysisApi(gateway: mockGateway);
  });

  group('SoilAnalysisApi', () {
    group('getSamples', () {
      test('should return paginated samples on success', () async {
        // Arrange
        final responseData = {
          'samples': [
            sampleSoilJson(id: 's1'),
            sampleSoilJson(id: 's2', status: 'analyzed'),
          ],
          'total': 2,
          'page': 1,
          'limit': 50,
        };

        when(() => mockGateway.get<SamplesPageResponse>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as SamplesPageResponse Function(dynamic);
          return ApiResponse.success(fromJson(responseData));
        });

        // Act
        final result = await api.getSamples();

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.samples.length, 2);
        expect(result.data!.total, 2);
        expect(result.data!.samples[0].id, 's1');
        expect(result.data!.samples[1].status, 'analyzed');
      });

      test('should include filters in query params', () async {
        // Arrange
        when(() => mockGateway.get<SamplesPageResponse>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as SamplesPageResponse Function(dynamic);
          return ApiResponse.success(fromJson({
            'samples': [],
            'total': 0,
            'page': 2,
            'limit': 10,
          }));
        });

        // Act
        await api.getSamples(
          fieldId: 'field-001',
          status: 'pending',
          type: 'soil',
          page: 2,
          limit: 10,
        );

        // Assert
        verify(() => mockGateway.get<SamplesPageResponse>(
              KongServices.soilAnalysis,
              '/samples',
              queryParams: {
                'page': 2,
                'limit': 10,
                'field_id': 'field-001',
                'status': 'pending',
                'type': 'soil',
              },
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should handle API error', () async {
        // Arrange
        when(() => mockGateway.get<SamplesPageResponse>(
                  any(),
                  any(),
                  queryParams: any(named: 'queryParams'),
                  fromJson: any(named: 'fromJson'),
                  cancelToken: any(named: 'cancelToken'),
                ))
            .thenAnswer((_) async => errorResponse<SamplesPageResponse>(
                'NO_CONNECTION', 'لا يوجد اتصال'));

        // Act
        final result = await api.getSamples();

        // Assert
        expect(result.success, isFalse);
        expect(result.errorCode, 'NO_CONNECTION');
      });
    });

    group('getSample', () {
      test('should return single sample', () async {
        // Arrange
        when(() => mockGateway.get<SoilSampleModel>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as SoilSampleModel Function(dynamic);
          return ApiResponse.success(fromJson(sampleSoilJson()));
        });

        // Act
        final result = await api.getSample(sampleId: 'sample-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.id, 'sample-001');
        expect(result.data!.barcode, 'BC-2026-001');
      });
    });

    group('createSample', () {
      test('should create sample and return model', () async {
        // Arrange
        when(() => mockGateway.post<SoilSampleModel>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as SoilSampleModel Function(dynamic);
          return ApiResponse.success(
              fromJson(sampleSoilJson(id: 'new-sample')));
        });

        // Act
        final result = await api.createSample(
          type: 'soil',
          experimentName: 'تجربة القمح',
          plotCode: 'P-01',
          collectedBy: 'أحمد',
          fieldId: 'field-001',
          notes: 'ملاحظات اختبارية',
        );

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.id, 'new-sample');

        verify(() => mockGateway.post<SoilSampleModel>(
              KongServices.soilAnalysis,
              '/samples',
              data: {
                'type': 'soil',
                'experiment_name': 'تجربة القمح',
                'plot_code': 'P-01',
                'collected_by': 'أحمد',
                'field_id': 'field-001',
                'notes': 'ملاحظات اختبارية',
              },
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should create sample without optional fields', () async {
        // Arrange
        when(() => mockGateway.post<SoilSampleModel>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as SoilSampleModel Function(dynamic);
          return ApiResponse.success(fromJson(sampleSoilJson()));
        });

        // Act
        await api.createSample(
          type: 'soil',
          experimentName: 'تجربة',
          plotCode: 'P-01',
          collectedBy: 'أحمد',
        );

        // Assert - no field_id or notes in data
        verify(() => mockGateway.post<SoilSampleModel>(
              KongServices.soilAnalysis,
              '/samples',
              data: {
                'type': 'soil',
                'experiment_name': 'تجربة',
                'plot_code': 'P-01',
                'collected_by': 'أحمد',
              },
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });
    });

    group('updateSampleStatus', () {
      test('should update sample status', () async {
        // Arrange
        when(() => mockGateway.put<SoilSampleModel>(
              any(),
              any(),
              data: any(named: 'data'),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as SoilSampleModel Function(dynamic);
          return ApiResponse.success(
              fromJson(sampleSoilJson(status: 'in_transit')));
        });

        // Act
        final result = await api.updateSampleStatus(
          sampleId: 'sample-001',
          status: 'in_transit',
          userId: 'user-001',
        );

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.status, 'in_transit');
        expect(result.data!.sampleStatus, SampleStatus.inTransit);
      });
    });

    group('getAnalysisResults', () {
      test('should return analysis results', () async {
        // Arrange
        final analysisData = {
          'sample_id': 'sample-001',
          'results': {
            'pH': 7.2,
            'nitrogen_ppm': 18,
            'phosphorus_ppm': 25,
            'potassium_ppm': 150,
            'organic_matter_pct': 2.5,
          },
          'interpretation': 'Nitrogen is below optimal range',
          'interpretation_ar': 'النيتروجين أقل من المدى المثالي',
          'recommendations': ['Apply urea at 46 kg/ha', 'Retest after 30 days'],
          'analyzed_at': '2026-02-15T14:00:00Z',
        };

        when(() => mockGateway.get<AnalysisResultModel>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as AnalysisResultModel Function(dynamic);
          return ApiResponse.success(fromJson(analysisData));
        });

        // Act
        final result = await api.getAnalysisResults(sampleId: 'sample-001');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.sampleId, 'sample-001');
        expect(result.data!.results['pH'], 7.2);
        expect(result.data!.interpretation, contains('Nitrogen'));
        expect(result.data!.interpretationAr, contains('النيتروجين'));
        expect(result.data!.recommendations.length, 2);
      });
    });

    group('getLabStats', () {
      test('should return lab statistics', () async {
        // Arrange
        final statsData = {
          'total': 100,
          'pending': 20,
          'in_transit': 10,
          'processing': 15,
          'analyzed': 55,
          'avg_processing_days': 3.5,
        };

        when(() => mockGateway.get<LabStats>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as LabStats Function(dynamic);
          return ApiResponse.success(fromJson(statsData));
        });

        // Act
        final result = await api.getLabStats();

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.totalSamples, 100);
        expect(result.data!.pendingSamples, 20);
        expect(result.data!.inTransitSamples, 10);
        expect(result.data!.processingSamples, 15);
        expect(result.data!.analyzedSamples, 55);
        expect(result.data!.averageProcessingDays, 3.5);
      });
    });

    group('searchByBarcode', () {
      test('should find sample by barcode', () async {
        // Arrange
        when(() => mockGateway.get<SoilSampleModel>(
              any(),
              any(),
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).thenAnswer((_) async {
          final fromJson = _.namedArguments[const Symbol('fromJson')]
              as SoilSampleModel Function(dynamic);
          return ApiResponse.success(
              fromJson(sampleSoilJson(barcode: 'BC-2026-042')));
        });

        // Act
        final result = await api.searchByBarcode(barcode: 'BC-2026-042');

        // Assert
        expect(result.success, isTrue);
        expect(result.data!.barcode, 'BC-2026-042');

        verify(() => mockGateway.get<SoilSampleModel>(
              KongServices.soilAnalysis,
              '/samples/barcode/BC-2026-042',
              queryParams: any(named: 'queryParams'),
              fromJson: any(named: 'fromJson'),
              cancelToken: any(named: 'cancelToken'),
            )).called(1);
      });

      test('should return error when barcode not found', () async {
        // Arrange
        when(() => mockGateway.get<SoilSampleModel>(
                  any(),
                  any(),
                  queryParams: any(named: 'queryParams'),
                  fromJson: any(named: 'fromJson'),
                  cancelToken: any(named: 'cancelToken'),
                ))
            .thenAnswer((_) async => errorResponse<SoilSampleModel>(
                'NOT_FOUND', 'Sample not found'));

        // Act
        final result = await api.searchByBarcode(barcode: 'INVALID');

        // Assert
        expect(result.success, isFalse);
        expect(result.errorCode, 'NOT_FOUND');
      });
    });
  });
}
