import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';
import 'package:sahool_field_app/features/analytics/data/models/analytics_models.dart';
import 'package:sahool_field_app/features/analytics/data/repositories/analytics_repository.dart';
import '../../../mocks/mock_kong_gateway.dart';

void main() {
  late AnalyticsRepository repository;
  late MockKongGatewayClient mockGateway;

  setUpAll(() {
    registerFallbackValue(FakeKongService());
  });

  setUp(() {
    mockGateway = MockKongGatewayClient();
    repository = AnalyticsRepository(gateway: mockGateway);
  });

  tearDown(() {
    repository.dispose();
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // calculateFieldHealth Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('calculateFieldHealth', () {
    test('should return health score from API when online', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenAnswer((_) async => ApiResponse<Map<String, dynamic>>.success(
            {
              'overall_score': 78.5,
              'ndvi_score': 85.0,
              'soil_health_score': 70.0,
              'water_stress_score': 75.0,
              'pest_risk_score': 80.0,
              'nutrient_score': 72.0,
              'trend': 'improving',
              'calculated_at': '2026-02-27T10:00:00.000',
              'recommendations': [],
            },
            requestId: 'req-001',
          ));

      // Act
      final result = await repository.calculateFieldHealth(
        fieldId: 'field-001',
        fieldName: 'Wheat Field',
        ndvi: 0.72,
        soilMoisture: 45.0,
        temperature: 28.0,
        humidity: 55.0,
      );

      // Assert
      expect(result.fieldId, 'field-001');
      expect(result.fieldName, 'Wheat Field');
      expect(result.overallScore, 78.5);
      expect(result.ndviScore, 85.0);
      expect(result.trend, HealthTrend.improving);
    });

    test('should fall back to local computation when API fails', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Network error'));

      // Act
      final result = await repository.calculateFieldHealth(
        fieldId: 'field-001',
        fieldName: 'Test Field',
        ndvi: 0.65,
        soilMoisture: 50.0,
        temperature: 25.0,
        humidity: 60.0,
      );

      // Assert
      expect(result.fieldId, 'field-001');
      expect(result.fieldName, 'Test Field');
      expect(result.overallScore, greaterThan(0));
      expect(result.overallScore, lessThanOrEqualTo(100));
    });

    test('should fall back to local computation when API returns error response',
        () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenAnswer((_) async =>
              ApiResponse<Map<String, dynamic>>.error('ERROR', 'Server error'));

      // Act
      final result = await repository.calculateFieldHealth(
        fieldId: 'field-002',
        fieldName: 'Offline Field',
      );

      // Assert
      expect(result.fieldId, 'field-002');
      expect(result.overallScore, greaterThanOrEqualTo(0));
    });

    test('should compute local score with default values when no metrics provided',
        () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.calculateFieldHealth(
        fieldId: 'field-003',
        fieldName: 'Default Field',
      );

      // Assert
      expect(result.fieldId, 'field-003');
      expect(result.overallScore, greaterThan(0));
      expect(result.ndviScore, greaterThan(0));
      expect(result.soilHealthScore, greaterThan(0));
    });

    test('should generate recommendations when scores are low', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act - use values that produce low sub-scores
      final result = await repository.calculateFieldHealth(
        fieldId: 'field-004',
        fieldName: 'Stressed Field',
        ndvi: 0.1, // Very low NDVI -> low nutrient score
        soilMoisture: 10.0, // Very dry
        temperature: 42.0, // Very hot -> high pest risk conditions
        humidity: 85.0, // Very humid -> high pest risk
      );

      // Assert
      expect(result.recommendations, isNotEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // predictYield Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('predictYield', () {
    test('should return yield prediction from API when online', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenAnswer((_) async => ApiResponse<Map<String, dynamic>>.success(
            {
              'predicted_yield': 3200.0,
              'min_yield': 2800.0,
              'max_yield': 3600.0,
              'confidence': 0.88,
              'harvest_date': '2026-06-15T00:00:00.000',
              'revenue_estimate': 2560000.0,
              'crop_type_ar': 'قمح',
              'factors': [
                {
                  'name': 'NDVI Health',
                  'name_ar': 'صحة الغطاء النباتي',
                  'impact': 0.3,
                  'description': 'Good vegetation health',
                  'description_ar': 'صحة غطاء نباتي جيدة',
                },
              ],
              'calculated_at': '2026-02-27T00:00:00.000',
            },
            requestId: 'req-002',
          ));

      // Act
      final result = await repository.predictYield(
        fieldId: 'field-001',
        cropType: 'wheat',
        fieldAreaHectares: 5.0,
        ndvi: 0.72,
        soilMoisture: 50.0,
      );

      // Assert
      expect(result.fieldId, 'field-001');
      expect(result.cropType, 'wheat');
      expect(result.predictedYield, 3200.0);
      expect(result.confidence, 0.88);
      expect(result.factors.length, 1);
    });

    test('should fall back to local computation when API fails', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.predictYield(
        fieldId: 'field-001',
        cropType: 'wheat',
        fieldAreaHectares: 5.0,
        ndvi: 0.7,
        soilMoisture: 45.0,
      );

      // Assert
      expect(result.fieldId, 'field-001');
      expect(result.cropType, 'wheat');
      expect(result.cropTypeAr, 'قمح');
      expect(result.predictedYield, greaterThan(0));
      expect(result.minYield, lessThan(result.predictedYield));
      expect(result.maxYield, greaterThan(result.predictedYield));
      expect(result.confidence, greaterThan(0));
      expect(result.factors, isNotEmpty);
    });

    test('should use correct base yields for different crops', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final wheatResult = await repository.predictYield(
        fieldId: 'field-001',
        cropType: 'wheat',
        fieldAreaHectares: 1.0,
        ndvi: 0.7,
        soilMoisture: 50.0,
      );
      final tomatoResult = await repository.predictYield(
        fieldId: 'field-002',
        cropType: 'tomato',
        fieldAreaHectares: 1.0,
        ndvi: 0.7,
        soilMoisture: 50.0,
      );

      // Assert - tomato base yield (35000) is much higher than wheat (2500)
      expect(tomatoResult.predictedYield,
          greaterThan(wheatResult.predictedYield));
    });

    test('should compute Arabic crop names for known crops', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.predictYield(
        fieldId: 'field-001',
        cropType: 'date_palm',
        fieldAreaHectares: 2.0,
      );

      // Assert
      expect(result.cropTypeAr, 'نخيل');
    });

    test('should handle unknown crop types gracefully', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.predictYield(
        fieldId: 'field-001',
        cropType: 'unknown_crop',
        fieldAreaHectares: 3.0,
      );

      // Assert - should use default base yield (2000)
      expect(result.predictedYield, greaterThan(0));
      expect(result.cropTypeAr, 'unknown_crop');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // assessRisks Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('assessRisks', () {
    test('should return risk assessment from API when online', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenAnswer((_) async => ApiResponse<Map<String, dynamic>>.success(
            {
              'risks': [
                {
                  'id': 'risk-001',
                  'type': 'drought',
                  'name': 'Drought Risk',
                  'name_ar': 'خطر الجفاف',
                  'description': 'Low rainfall',
                  'description_ar': 'قلة الأمطار',
                  'level': 'high',
                  'probability': 0.7,
                  'potential_impact': 70.0,
                  'mitigation_steps': ['Irrigate more'],
                  'mitigation_steps_ar': ['زيادة الري'],
                },
              ],
              'overall_risk_score': 49.0,
              'assessed_at': '2026-02-27T10:00:00.000',
            },
            requestId: 'req-003',
          ));

      // Act
      final result = await repository.assessRisks(
        fieldId: 'field-001',
        temperature: 38.0,
        humidity: 30.0,
        rainfall: 5.0,
      );

      // Assert
      expect(result.fieldId, 'field-001');
      expect(result.risks.length, 1);
      expect(result.risks.first.type, RiskType.drought);
      expect(result.overallRiskScore, 49.0);
    });

    test('should fall back to local risk computation when API fails', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.assessRisks(
        fieldId: 'field-001',
        temperature: 42.0, // Heat wave
        humidity: 80.0, // High humidity -> pest risk
        rainfall: 5.0, // Low rainfall -> drought risk
        ndvi: 0.3, // Low NDVI -> nutrient risk
      );

      // Assert
      expect(result.fieldId, 'field-001');
      expect(result.risks, isNotEmpty);
      // Should detect drought (rainfall < 20), heat (temp > 35), pest (humidity > 70), nutrient (ndvi < 0.4)
      expect(result.risks.length, 4);
    });

    test('should detect drought risk when rainfall is low', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.assessRisks(
        fieldId: 'field-001',
        rainfall: 5.0,
      );

      // Assert
      final droughtRisks =
          result.risks.where((r) => r.type == RiskType.drought).toList();
      expect(droughtRisks, isNotEmpty);
      expect(droughtRisks.first.level, RiskLevel.high); // rainfall < 10
    });

    test('should detect heat stress when temperature is high', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.assessRisks(
        fieldId: 'field-001',
        temperature: 42.0,
      );

      // Assert
      final heatRisks =
          result.risks.where((r) => r.type == RiskType.heatWave).toList();
      expect(heatRisks, isNotEmpty);
      expect(heatRisks.first.level, RiskLevel.critical); // temp > 40
    });

    test('should detect pest risk when humidity is high', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.assessRisks(
        fieldId: 'field-001',
        humidity: 90.0,
      );

      // Assert
      final pestRisks =
          result.risks.where((r) => r.type == RiskType.pest).toList();
      expect(pestRisks, isNotEmpty);
      expect(pestRisks.first.level, RiskLevel.high); // humidity > 85
    });

    test('should detect nutrient deficiency when NDVI is low', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.assessRisks(
        fieldId: 'field-001',
        ndvi: 0.2,
      );

      // Assert
      final nutrientRisks = result.risks
          .where((r) => r.type == RiskType.nutrientDeficiency)
          .toList();
      expect(nutrientRisks, isNotEmpty);
      expect(nutrientRisks.first.level, RiskLevel.high); // ndvi < 0.25
    });

    test('should return low overall risk when no risk conditions present',
        () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act - mild conditions, no risk triggers
      final result = await repository.assessRisks(
        fieldId: 'field-001',
        temperature: 25.0, // Normal
        humidity: 50.0, // Normal
        rainfall: 30.0, // Adequate
        ndvi: 0.7, // Healthy
      );

      // Assert
      expect(result.risks, isEmpty);
      expect(result.overallRiskScore, 10.0); // Default when no risks
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // getAnalyticsSummary Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('getAnalyticsSummary', () {
    test('should return summary from API when online', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenAnswer((_) async => ApiResponse<Map<String, dynamic>>.success(
            {
              'total_fields': 5,
              'average_health_score': 72.0,
              'total_predicted_yield': 15000.0,
              'total_revenue_estimate': 9000000.0,
              'high_risk_fields': 1,
              'fields_needing_attention': 2,
              'generated_at': '2026-02-27T10:00:00.000',
            },
            requestId: 'req-004',
          ));

      // Act
      final result =
          await repository.getAnalyticsSummary(['f1', 'f2', 'f3', 'f4', 'f5']);

      // Assert
      expect(result.totalFields, 5);
      expect(result.averageHealthScore, 72.0);
      expect(result.totalPredictedYield, 15000.0);
      expect(result.highRiskFields, 1);
    });

    test('should fall back to local computation when API fails', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result =
          await repository.getAnalyticsSummary(['f1', 'f2', 'f3']);

      // Assert
      expect(result.totalFields, 3);
      expect(result.averageHealthScore, greaterThan(0));
      expect(result.totalPredictedYield, greaterThan(0));
      expect(result.totalRevenueEstimate, greaterThan(0));
    });

    test('should handle empty field list', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.getAnalyticsSummary([]);

      // Assert
      expect(result.totalFields, 0);
      expect(result.averageHealthScore, 0.0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // getHistoricalTrend Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('getHistoricalTrend', () {
    test('should return trend from API when online', () async {
      // Arrange
      when(() => mockGateway.get<Map<String, dynamic>>(
            any(),
            any(),
            queryParams: any(named: 'queryParams'),
            fromJson: any(named: 'fromJson'),
          )).thenAnswer((_) async => ApiResponse<Map<String, dynamic>>.success(
            {
              'data_points': [
                {'date': '2026-02-01T00:00:00.000', 'value': 0.60},
                {'date': '2026-02-15T00:00:00.000', 'value': 0.68},
                {'date': '2026-02-27T00:00:00.000', 'value': 0.72},
              ],
              'change_percent': 20.0,
              'trend': 'improving',
            },
            requestId: 'req-005',
          ));

      // Act
      final result = await repository.getHistoricalTrend(
        fieldId: 'field-001',
        metricName: 'ndvi',
        days: 30,
      );

      // Assert
      expect(result.metricName, 'ndvi');
      expect(result.metricNameAr, 'مؤشر الغطاء النباتي');
      expect(result.dataPoints.length, 3);
      expect(result.changePercent, 20.0);
      expect(result.trend, HealthTrend.improving);
    });

    test('should fall back to local trend computation when API fails', () async {
      // Arrange
      when(() => mockGateway.get<Map<String, dynamic>>(
            any(),
            any(),
            queryParams: any(named: 'queryParams'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.getHistoricalTrend(
        fieldId: 'field-001',
        metricName: 'soil_moisture',
        days: 14,
      );

      // Assert
      expect(result.metricName, 'soil_moisture');
      expect(result.metricNameAr, 'رطوبة التربة');
      expect(result.dataPoints.length, 15); // days + 1
      expect(result.dataPoints, isNotEmpty);
    });

    test('should provide Arabic metric name for known metrics', () async {
      // Arrange
      when(() => mockGateway.get<Map<String, dynamic>>(
            any(),
            any(),
            queryParams: any(named: 'queryParams'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act & Assert - known metrics should have Arabic names
      final ndviResult = await repository.getHistoricalTrend(
        fieldId: 'field-001',
        metricName: 'ndvi',
        days: 7,
      );
      expect(ndviResult.metricNameAr, 'مؤشر الغطاء النباتي');

      final healthResult = await repository.getHistoricalTrend(
        fieldId: 'field-001',
        metricName: 'health_score',
        days: 7,
      );
      expect(healthResult.metricNameAr, 'درجة الصحة');

      final yieldResult = await repository.getHistoricalTrend(
        fieldId: 'field-001',
        metricName: 'yield_estimate',
        days: 7,
      );
      expect(yieldResult.metricNameAr, 'تقدير الإنتاجية');
    });

    test('should fallback metric name for unknown metrics', () async {
      // Arrange
      when(() => mockGateway.get<Map<String, dynamic>>(
            any(),
            any(),
            queryParams: any(named: 'queryParams'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act
      final result = await repository.getHistoricalTrend(
        fieldId: 'field-001',
        metricName: 'custom_metric',
        days: 7,
      );

      // Assert
      expect(result.metricNameAr, 'custom_metric');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Error Handling Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('error handling', () {
    test('should handle API returning null data gracefully', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenAnswer((_) async => const ApiResponse<Map<String, dynamic>>(
            success: true,
            data: null,
          ));

      // Act - should fall through to local computation
      final result = await repository.calculateFieldHealth(
        fieldId: 'field-001',
        fieldName: 'Test',
      );

      // Assert - local computation should return valid data
      expect(result.fieldId, 'field-001');
      expect(result.overallScore, greaterThanOrEqualTo(0));
    });

    test('should handle concurrent API calls without interference', () async {
      // Arrange
      when(() => mockGateway.post<Map<String, dynamic>>(
            any(),
            any(),
            data: any(named: 'data'),
            fromJson: any(named: 'fromJson'),
          )).thenThrow(Exception('Offline'));

      // Act - run multiple computations in parallel
      final results = await Future.wait([
        repository.calculateFieldHealth(
          fieldId: 'field-001',
          fieldName: 'Field 1',
          ndvi: 0.8,
        ),
        repository.calculateFieldHealth(
          fieldId: 'field-002',
          fieldName: 'Field 2',
          ndvi: 0.3,
        ),
      ]);

      // Assert - each should return its own field data
      expect(results[0].fieldId, 'field-001');
      expect(results[1].fieldId, 'field-002');
      expect(results[0].overallScore, isNot(equals(results[1].overallScore)));
    });
  });
}
