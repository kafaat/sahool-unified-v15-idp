import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sahool_field_app/features/satellite/data/repositories/satellite_repository.dart';
import 'package:sahool_field_app/features/satellite/data/remote/satellite_api.dart';
import 'package:sahool_field_app/features/satellite/data/models/ndvi_data.dart';
import 'package:sahool_field_app/features/satellite/data/models/field_health.dart';
import 'package:sahool_field_app/features/satellite/data/models/weather_data.dart';
import 'package:sahool_field_app/features/satellite/data/models/phenology_data.dart';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

class MockSatelliteApi extends Mock implements SatelliteApi {}

// ---------------------------------------------------------------------------
// Sample Data Helpers
// ---------------------------------------------------------------------------

NdviAnalysis _sampleNdviAnalysis({String fieldId = 'field_001'}) {
  return NdviAnalysis(
    fieldId: fieldId,
    currentNdvi: 0.72,
    previousNdvi: 0.68,
    changeRate: 5.9,
    health: VegetationHealth.good,
    timeSeries: [
      NdviDataPoint(
        date: DateTime(2026, 2, 20),
        value: 0.68,
        source: 'sentinel-2',
        cloudCoverage: 10.0,
      ),
      NdviDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.72,
        source: 'sentinel-2',
        cloudCoverage: 5.0,
      ),
    ],
    analyzedAt: DateTime(2026, 2, 27, 10, 0),
    imageUrl: 'https://example.com/ndvi_map.png',
    indices: const {'NDVI': 0.72, 'NDWI': 0.35, 'EVI': 0.55},
  );
}

FieldHealth _sampleFieldHealth({String fieldId = 'field_001'}) {
  return FieldHealth(
    fieldId: fieldId,
    healthScore: 78.0,
    status: HealthStatus.good,
    ndvi: 0.72,
    ndwi: 0.35,
    evi: 0.55,
    soilMoisture: 42.0,
    alerts: [
      HealthAlert(
        id: 'ha_001',
        type: AlertType.waterStress,
        severity: AlertSeverity.warning,
        message: 'Low soil moisture detected in zone B',
        messageAr:
            '\u0631\u0637\u0648\u0628\u0629 \u062a\u0631\u0628\u0629 \u0645\u0646\u062e\u0641\u0636\u0629 \u0641\u064a \u0627\u0644\u0645\u0646\u0637\u0642\u0629 \u0628',
        detectedAt: DateTime(2026, 2, 26),
        affectedZone: 'zone_B',
      ),
    ],
    recommendations: const [
      Recommendation(
        id: 'rec_001',
        type: RecommendationType.irrigation,
        title: 'Increase irrigation in zone B',
        titleAr:
            '\u0632\u064a\u0627\u062f\u0629 \u0627\u0644\u0631\u064a \u0641\u064a \u0627\u0644\u0645\u0646\u0637\u0642\u0629 \u0628',
        description: 'Apply 25mm of irrigation within 48 hours',
        descriptionAr:
            '\u062a\u0637\u0628\u064a\u0642 25 \u0645\u0645 \u0631\u064a \u062e\u0644\u0627\u0644 48 \u0633\u0627\u0639\u0629',
        priority: RecommendationPriority.high,
      ),
    ],
    assessedAt: DateTime(2026, 2, 27, 8, 0),
    zoneScores: const {'zone_A': 85.0, 'zone_B': 62.0, 'zone_C': 80.0},
  );
}

PhenologyData _samplePhenologyData({String fieldId = 'field_001'}) {
  return PhenologyData(
    fieldId: fieldId,
    cropType: 'wheat',
    cropTypeAr: '\u0642\u0645\u062d',
    currentStage: GrowthStage.flowering,
    daysInCurrentStage: 8,
    daysToNextStage: 12,
    daysToHarvest: 45,
    plantingDate: DateTime(2025, 11, 15),
    expectedHarvestDate: DateTime(2026, 4, 12),
    stages: const [
      GrowthStageInfo(
        stage: GrowthStage.germination,
        name: 'Germination',
        nameAr: '\u0625\u0646\u0628\u0627\u062a',
        durationDays: 14,
        isCompleted: true,
        isCurrent: false,
      ),
      GrowthStageInfo(
        stage: GrowthStage.flowering,
        name: 'Flowering',
        nameAr: '\u0625\u0632\u0647\u0627\u0631',
        durationDays: 20,
        isCompleted: false,
        isCurrent: true,
      ),
    ],
    currentTasks: const ['Monitor pollination', 'Check for rust'],
    currentTasksAr: const [
      '\u0645\u0631\u0627\u0642\u0628\u0629 \u0627\u0644\u062a\u0644\u0642\u064a\u062d',
      '\u0641\u062d\u0635 \u0627\u0644\u0635\u062f\u0623',
    ],
    completionPercentage: 65.0,
    analyzedAt: DateTime(2026, 2, 27, 9, 0),
  );
}

WeatherSummary _sampleWeatherSummary({String fieldId = 'field_001'}) {
  return WeatherSummary(
    fieldId: fieldId,
    temperature: 28.0,
    minTemp: 18.0,
    maxTemp: 33.0,
    precipitation: 0.0,
    humidity: 55.0,
    et0: 5.2,
    condition: 'Sunny',
    conditionAr: '\u0645\u0634\u0645\u0633',
    updatedAt: DateTime(2026, 2, 27, 10, 0),
    forecast: const [],
  );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  late MockSatelliteApi mockApi;
  late SharedPreferences prefs;

  setUp(() async {
    mockApi = MockSatelliteApi();
    SharedPreferences.setMockInitialValues({});
    prefs = await SharedPreferences.getInstance();
  });

  SatelliteRepository createRepo() {
    return SatelliteRepository(api: mockApi, prefs: prefs);
  }

  // =========================================================================
  // getNdviAnalysis
  // =========================================================================

  group('SatelliteRepository - getNdviAnalysis', () {
    test('should fetch from API and cache on first call', () async {
      // Arrange
      final analysis = _sampleNdviAnalysis();
      when(() => mockApi.getNdviAnalysis('field_001'))
          .thenAnswer((_) async => analysis);

      final repo = createRepo();

      // Act
      final result = await repo.getNdviAnalysis('field_001');

      // Assert
      expect(result.currentNdvi, 0.72);
      expect(result.fieldId, 'field_001');
      verify(() => mockApi.getNdviAnalysis('field_001')).called(1);

      // Verify it was cached
      final cachedJson = prefs.getString('ndvi_analysis_field_001');
      expect(cachedJson, isNotNull);
    });

    test('should return cached data on second call (within 24h TTL)',
        () async {
      // Arrange
      final analysis = _sampleNdviAnalysis();
      when(() => mockApi.getNdviAnalysis('field_001'))
          .thenAnswer((_) async => analysis);

      final repo = createRepo();

      // Act - first call
      await repo.getNdviAnalysis('field_001');

      // Act - second call should use cache
      final result = await repo.getNdviAnalysis('field_001');

      // Assert - only one API call
      expect(result.currentNdvi, 0.72);
      verify(() => mockApi.getNdviAnalysis('field_001')).called(1);
    });

    test('should force refresh when forceRefresh is true', () async {
      // Arrange
      final analysis = _sampleNdviAnalysis();
      when(() => mockApi.getNdviAnalysis('field_001'))
          .thenAnswer((_) async => analysis);

      final repo = createRepo();

      // Act - first call populates cache
      await repo.getNdviAnalysis('field_001');

      // Act - forced refresh
      final result =
          await repo.getNdviAnalysis('field_001', forceRefresh: true);

      // Assert - two API calls
      expect(result.currentNdvi, 0.72);
      verify(() => mockApi.getNdviAnalysis('field_001')).called(2);
    });

    test('should return stale cached data when API fails', () async {
      // Arrange - pre-populate cache
      final analysis = _sampleNdviAnalysis();
      await prefs.setString(
          'ndvi_analysis_field_001', jsonEncode(analysis.toJson()));
      await prefs.setInt('ndvi_analysis_field_001_timestamp',
          DateTime.now().millisecondsSinceEpoch);

      when(() => mockApi.getNdviAnalysis('field_001'))
          .thenThrow(SatelliteApiException('Server error', statusCode: 500));

      final repo = createRepo();

      // Act - forceRefresh triggers API, which fails, falls back to cache
      final result =
          await repo.getNdviAnalysis('field_001', forceRefresh: true);

      // Assert
      expect(result.currentNdvi, 0.72);
    });

    test('should rethrow when API fails and no cache exists', () async {
      // Arrange
      when(() => mockApi.getNdviAnalysis('field_missing'))
          .thenThrow(SatelliteApiException('Not found', statusCode: 404));

      final repo = createRepo();

      // Act & Assert
      expect(
        () => repo.getNdviAnalysis('field_missing'),
        throwsA(isA<SatelliteApiException>()),
      );
    });
  });

  // =========================================================================
  // getFieldHealth
  // =========================================================================

  group('SatelliteRepository - getFieldHealth', () {
    test('should fetch from API and cache', () async {
      // Arrange
      final health = _sampleFieldHealth();
      when(() => mockApi.getFieldHealth('field_001'))
          .thenAnswer((_) async => health);

      final repo = createRepo();

      // Act
      final result = await repo.getFieldHealth('field_001');

      // Assert
      expect(result.healthScore, 78.0);
      expect(result.status, HealthStatus.good);
      expect(result.alerts.length, 1);
      expect(result.recommendations.length, 1);
      verify(() => mockApi.getFieldHealth('field_001')).called(1);
    });

    test('should return cached data on second call', () async {
      // Arrange
      final health = _sampleFieldHealth();
      when(() => mockApi.getFieldHealth('field_001'))
          .thenAnswer((_) async => health);

      final repo = createRepo();

      // Act
      await repo.getFieldHealth('field_001');
      final result = await repo.getFieldHealth('field_001');

      // Assert
      expect(result.healthScore, 78.0);
      verify(() => mockApi.getFieldHealth('field_001')).called(1);
    });

    test('should return stale cache when API fails', () async {
      // Arrange - pre-populate cache
      final health = _sampleFieldHealth();
      await prefs.setString(
          'field_health_field_001', jsonEncode(health.toJson()));
      await prefs.setInt('field_health_field_001_timestamp',
          DateTime.now().millisecondsSinceEpoch);

      when(() => mockApi.getFieldHealth('field_001'))
          .thenThrow(SatelliteApiException('Timeout', statusCode: 504));

      final repo = createRepo();

      // Act - force refresh triggers API call, fails, returns stale cache
      final result =
          await repo.getFieldHealth('field_001', forceRefresh: true);

      // Assert
      expect(result.healthScore, 78.0);
    });

    test('should rethrow when API fails and no cache exists', () async {
      // Arrange
      when(() => mockApi.getFieldHealth('no_cache'))
          .thenThrow(SatelliteApiException('Error', statusCode: 500));

      final repo = createRepo();

      // Act & Assert
      expect(
        () => repo.getFieldHealth('no_cache'),
        throwsA(isA<SatelliteApiException>()),
      );
    });

    test('should bypass cache when forceRefresh is true', () async {
      // Arrange
      final health = _sampleFieldHealth();
      when(() => mockApi.getFieldHealth('field_001'))
          .thenAnswer((_) async => health);

      final repo = createRepo();

      // Populate cache
      await repo.getFieldHealth('field_001');

      // Force refresh
      await repo.getFieldHealth('field_001', forceRefresh: true);

      // Assert - two API calls
      verify(() => mockApi.getFieldHealth('field_001')).called(2);
    });
  });

  // =========================================================================
  // getPhenologyData
  // =========================================================================

  group('SatelliteRepository - getPhenologyData', () {
    test('should fetch phenology data and cache', () async {
      // Arrange
      final phenology = _samplePhenologyData();
      when(() => mockApi.getPhenologyData('field_001'))
          .thenAnswer((_) async => phenology);

      final repo = createRepo();

      // Act
      final result = await repo.getPhenologyData('field_001');

      // Assert
      expect(result.cropType, 'wheat');
      expect(result.currentStage, GrowthStage.flowering);
      expect(result.daysToHarvest, 45);
      expect(result.completionPercentage, 65.0);
      verify(() => mockApi.getPhenologyData('field_001')).called(1);
    });

    test('should return cached phenology data on second call', () async {
      // Arrange
      final phenology = _samplePhenologyData();
      when(() => mockApi.getPhenologyData('field_001'))
          .thenAnswer((_) async => phenology);

      final repo = createRepo();

      // Act
      await repo.getPhenologyData('field_001');
      final result = await repo.getPhenologyData('field_001');

      // Assert
      expect(result.currentStage, GrowthStage.flowering);
      verify(() => mockApi.getPhenologyData('field_001')).called(1);
    });

    test('should return stale cache when API fails', () async {
      // Arrange - pre-populate cache
      final phenology = _samplePhenologyData();
      await prefs.setString(
          'phenology_data_field_001', jsonEncode(phenology.toJson()));
      await prefs.setInt('phenology_data_field_001_timestamp',
          DateTime.now().millisecondsSinceEpoch);

      when(() => mockApi.getPhenologyData('field_001'))
          .thenThrow(SatelliteApiException('Error', statusCode: 500));

      final repo = createRepo();

      // Act
      final result =
          await repo.getPhenologyData('field_001', forceRefresh: true);

      // Assert
      expect(result.cropType, 'wheat');
    });

    test('should rethrow when API fails and no cache exists', () async {
      // Arrange
      when(() => mockApi.getPhenologyData('no_cache'))
          .thenThrow(SatelliteApiException('Not found', statusCode: 404));

      final repo = createRepo();

      // Act & Assert
      expect(
        () => repo.getPhenologyData('no_cache'),
        throwsA(isA<SatelliteApiException>()),
      );
    });
  });

  // =========================================================================
  // getNdviTimeSeries
  // =========================================================================

  group('SatelliteRepository - getNdviTimeSeries', () {
    test('should fetch time series from API', () async {
      // Arrange
      final timeSeries = [
        NdviDataPoint(
          date: DateTime(2026, 2, 1),
          value: 0.60,
          source: 'sentinel-2',
        ),
        NdviDataPoint(
          date: DateTime(2026, 2, 15),
          value: 0.68,
          source: 'sentinel-2',
        ),
        NdviDataPoint(
          date: DateTime(2026, 2, 27),
          value: 0.72,
          source: 'sentinel-2',
        ),
      ];

      when(() => mockApi.getNdviTimeSeries('field_001', days: 30))
          .thenAnswer((_) async => timeSeries);

      final repo = createRepo();

      // Act
      final result = await repo.getNdviTimeSeries('field_001');

      // Assert
      expect(result.length, 3);
      expect(result.last.value, 0.72);
      verify(() => mockApi.getNdviTimeSeries('field_001', days: 30)).called(1);
    });

    test('should cache time series and return on second call', () async {
      // Arrange
      final timeSeries = [
        NdviDataPoint(
          date: DateTime(2026, 2, 27),
          value: 0.72,
          source: 'sentinel-2',
        ),
      ];

      when(() => mockApi.getNdviTimeSeries('field_001', days: 30))
          .thenAnswer((_) async => timeSeries);

      final repo = createRepo();

      // Act
      await repo.getNdviTimeSeries('field_001');
      final result = await repo.getNdviTimeSeries('field_001');

      // Assert
      expect(result.length, 1);
      verify(() => mockApi.getNdviTimeSeries('field_001', days: 30)).called(1);
    });
  });

  // =========================================================================
  // getVegetationIndices
  // =========================================================================

  group('SatelliteRepository - getVegetationIndices', () {
    test('should fetch vegetation indices from API', () async {
      // Arrange
      final indices = {'NDVI': 0.72, 'NDWI': 0.35, 'EVI': 0.55, 'NDRE': 0.42};

      when(() => mockApi.getVegetationIndices('field_001'))
          .thenAnswer((_) async => indices);

      final repo = createRepo();

      // Act
      final result = await repo.getVegetationIndices('field_001');

      // Assert
      expect(result['NDVI'], 0.72);
      expect(result['NDWI'], 0.35);
      expect(result.length, 4);
    });

    test('should return cached indices on second call', () async {
      // Arrange
      final indices = {'NDVI': 0.72, 'NDWI': 0.35};

      when(() => mockApi.getVegetationIndices('field_001'))
          .thenAnswer((_) async => indices);

      final repo = createRepo();

      // Act
      await repo.getVegetationIndices('field_001');
      final result = await repo.getVegetationIndices('field_001');

      // Assert
      expect(result['NDVI'], 0.72);
      verify(() => mockApi.getVegetationIndices('field_001')).called(1);
    });
  });

  // =========================================================================
  // getWeatherForecast
  // =========================================================================

  group('SatelliteRepository - getWeatherForecast', () {
    test('should fetch weather summary from API', () async {
      // Arrange
      final weather = _sampleWeatherSummary();
      when(() => mockApi.getWeatherForecast('field_001'))
          .thenAnswer((_) async => weather);

      final repo = createRepo();

      // Act
      final result = await repo.getWeatherForecast('field_001');

      // Assert
      expect(result.temperature, 28.0);
      expect(result.et0, 5.2);
      verify(() => mockApi.getWeatherForecast('field_001')).called(1);
    });

    test('should return stale cache when API fails', () async {
      // Arrange - pre-populate cache
      final weather = _sampleWeatherSummary();
      await prefs.setString(
          'weather_forecast_field_001', jsonEncode(weather.toJson()));
      await prefs.setInt('weather_forecast_field_001_timestamp',
          DateTime.now().millisecondsSinceEpoch);

      when(() => mockApi.getWeatherForecast('field_001'))
          .thenThrow(SatelliteApiException('Error', statusCode: 500));

      final repo = createRepo();

      // Act
      final result =
          await repo.getWeatherForecast('field_001', forceRefresh: true);

      // Assert
      expect(result.temperature, 28.0);
    });
  });

  // =========================================================================
  // clearCache
  // =========================================================================

  group('SatelliteRepository - clearCache', () {
    test('should clear all satellite cache keys', () async {
      // Arrange
      final analysis = _sampleNdviAnalysis();
      when(() => mockApi.getNdviAnalysis('field_001'))
          .thenAnswer((_) async => analysis);

      final repo = createRepo();

      // Populate cache
      await repo.getNdviAnalysis('field_001');
      expect(prefs.getString('ndvi_analysis_field_001'), isNotNull);

      // Act
      await repo.clearCache();

      // Assert
      expect(prefs.getString('ndvi_analysis_field_001'), isNull);
    });
  });

  // =========================================================================
  // clearFieldCache
  // =========================================================================

  group('SatelliteRepository - clearFieldCache', () {
    test('should clear cache for specific field only', () async {
      // Arrange
      final analysis1 = _sampleNdviAnalysis(fieldId: 'field_001');
      final analysis2 = _sampleNdviAnalysis(fieldId: 'field_002');

      when(() => mockApi.getNdviAnalysis('field_001'))
          .thenAnswer((_) async => analysis1);
      when(() => mockApi.getNdviAnalysis('field_002'))
          .thenAnswer((_) async => analysis2);

      final repo = createRepo();

      // Populate cache for both fields
      await repo.getNdviAnalysis('field_001');
      await repo.getNdviAnalysis('field_002');

      // Act - clear only field_001
      await repo.clearFieldCache('field_001');

      // Assert - field_001 cache cleared, field_002 still present
      expect(prefs.getString('ndvi_analysis_field_001'), isNull);
      expect(prefs.getString('ndvi_analysis_field_002'), isNotNull);
    });
  });

  // =========================================================================
  // Cache expiration
  // =========================================================================

  group('SatelliteRepository - cache expiration', () {
    test('should refetch when cache timestamp is older than 24 hours',
        () async {
      // Arrange - set expired timestamp (25 hours ago)
      final analysis = _sampleNdviAnalysis();
      await prefs.setString(
          'ndvi_analysis_field_001', jsonEncode(analysis.toJson()));
      await prefs.setInt(
        'ndvi_analysis_field_001_timestamp',
        DateTime.now()
            .subtract(const Duration(hours: 25))
            .millisecondsSinceEpoch,
      );

      final freshAnalysis = _sampleNdviAnalysis();
      when(() => mockApi.getNdviAnalysis('field_001'))
          .thenAnswer((_) async => freshAnalysis);

      final repo = createRepo();

      // Act - cache is expired, should fetch from API
      final result = await repo.getNdviAnalysis('field_001');

      // Assert
      expect(result.currentNdvi, 0.72);
      verify(() => mockApi.getNdviAnalysis('field_001')).called(1);
    });

    test('should NOT refetch when cache is within 24 hour TTL', () async {
      // Arrange - set fresh timestamp (1 hour ago)
      final analysis = _sampleNdviAnalysis();
      await prefs.setString(
          'ndvi_analysis_field_001', jsonEncode(analysis.toJson()));
      await prefs.setInt(
        'ndvi_analysis_field_001_timestamp',
        DateTime.now()
            .subtract(const Duration(hours: 1))
            .millisecondsSinceEpoch,
      );

      final repo = createRepo();

      // Act
      final result = await repo.getNdviAnalysis('field_001');

      // Assert - no API call needed
      expect(result.currentNdvi, 0.72);
      verifyNever(() => mockApi.getNdviAnalysis(any()));
    });
  });
}
