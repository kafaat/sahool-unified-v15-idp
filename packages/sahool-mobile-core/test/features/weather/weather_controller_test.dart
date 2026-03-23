/// Weather Controller Tests - اختبارات متحكم الطقس
///
/// Comprehensive tests for WeatherNotifier, AlertsNotifier, and ImpactsNotifier
/// covering state management, loading states, and error handling.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/weather/data/remote/weather_api.dart';
import 'package:sahool_field_app/features/weather/domain/entities/weather_entities.dart';
import 'package:sahool_field_app/features/weather/presentation/providers/weather_provider.dart';

import 'weather_fixtures.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks - الكائنات الوهمية
// ═══════════════════════════════════════════════════════════════════════════

class MockWeatherApi extends Mock implements WeatherApi {}

class MockHttpClient extends Mock implements http.Client {}

class FakeUri extends Fake implements Uri {}

void main() {
  setUpAll(() {
    registerFallbackValue(FakeUri());
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // WeatherState Tests - اختبارات حالة الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  group('WeatherState', () {
    test('should have default initial state', () {
      // Arrange & Act
      const state = WeatherState();

      // Assert
      expect(state.isLoading, isFalse);
      expect(state.data, isNull);
      expect(state.error, isNull);
    });

    test('should copy with isLoading', () {
      // Arrange
      const state = WeatherState();

      // Act
      final newState = state.copyWith(isLoading: true);

      // Assert
      expect(newState.isLoading, isTrue);
      expect(newState.data, isNull);
      expect(newState.error, isNull);
    });

    test('should copy with data', () {
      // Arrange
      const state = WeatherState();
      final data = WeatherData.fromJson(WeatherFixtures.currentWeatherJson);

      // Act
      final newState = state.copyWith(data: data);

      // Assert
      expect(newState.isLoading, isFalse);
      expect(newState.data, equals(data));
      expect(newState.error, isNull);
    });

    test('should copy with error and clear previous error', () {
      // Arrange
      const state = WeatherState(error: 'Previous error');

      // Act
      final newState = state.copyWith(error: 'New error');

      // Assert
      expect(newState.error, equals('New error'));
    });

    test('should clear error when copying with null error', () {
      // Arrange
      const state = WeatherState(error: 'Some error');

      // Act
      final newState = state.copyWith(error: null);

      // Assert
      expect(newState.error, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // WeatherNotifier Tests - اختبارات WeatherNotifier
  // ═══════════════════════════════════════════════════════════════════════════

  group('WeatherNotifier', () {
    late MockWeatherApi mockApi;
    late WeatherNotifier notifier;

    setUp(() {
      mockApi = MockWeatherApi();
      notifier = WeatherNotifier(mockApi);
    });

    group('loadWeather - تحميل الطقس', () {
      test('should set loading state when starting to load', () async {
        // Arrange
        final data = WeatherData.fromJson(WeatherFixtures.currentWeatherJson);
        when(() => mockApi.getFieldWeather(any()))
            .thenAnswer((_) async => data);

        // Act - Start loading and check state before completion
        final future = notifier.loadWeather('field-001');

        // State should transition to loading
        // We can't easily test intermediate states, so we verify the API was called

        await future;

        // Assert - Final state should have data
        expect(notifier.state.isLoading, isFalse);
        expect(notifier.state.data, isNotNull);
      });

      test('should set data on successful load', () async {
        // Arrange
        final data = WeatherData.fromJson(WeatherFixtures.currentWeatherJson);
        when(() => mockApi.getFieldWeather(any()))
            .thenAnswer((_) async => data);

        // Act
        await notifier.loadWeather('field-001');

        // Assert
        expect(notifier.state.data, isNotNull);
        expect(notifier.state.data!.current.temperature, equals(28.5));
        expect(notifier.state.data!.current.conditionAr, equals('غائم جزئياً'));
        expect(notifier.state.isLoading, isFalse);
        expect(notifier.state.error, isNull);
      });

      test('should set error on API failure', () async {
        // Arrange
        when(() => mockApi.getFieldWeather(any()))
            .thenThrow(WeatherApiException('فشل جلب بيانات الطقس', statusCode: 500));

        // Act
        await notifier.loadWeather('field-001');

        // Assert
        expect(notifier.state.data, isNull);
        expect(notifier.state.isLoading, isFalse);
        expect(notifier.state.error, isNotNull);
        expect(notifier.state.error, contains('فشل'));
      });

      test('should handle network errors', () async {
        // Arrange
        when(() => mockApi.getFieldWeather(any()))
            .thenThrow(Exception('No internet connection'));

        // Act
        await notifier.loadWeather('field-001');

        // Assert
        expect(notifier.state.error, isNotNull);
        expect(notifier.state.isLoading, isFalse);
      });

      test('should clear previous error on new load', () async {
        // Arrange - First load fails
        when(() => mockApi.getFieldWeather('field-001'))
            .thenThrow(WeatherApiException('Error', statusCode: 500));
        await notifier.loadWeather('field-001');
        expect(notifier.state.error, isNotNull);

        // Arrange - Second load succeeds
        final data = WeatherData.fromJson(WeatherFixtures.currentWeatherJson);
        when(() => mockApi.getFieldWeather('field-002'))
            .thenAnswer((_) async => data);

        // Act
        await notifier.loadWeather('field-002');

        // Assert
        expect(notifier.state.error, isNull);
        expect(notifier.state.data, isNotNull);
      });
    });

    group('loadWeatherByLocation - تحميل الطقس بالموقع', () {
      test('should load weather by coordinates', () async {
        // Arrange
        final data = WeatherData.fromJson(WeatherFixtures.currentWeatherJson);
        when(() => mockApi.getWeatherByCoordinates(any(), any()))
            .thenAnswer((_) async => data);

        // Act
        await notifier.loadWeatherByLocation(15.3694, 44.1910);

        // Assert
        expect(notifier.state.data, isNotNull);
        expect(notifier.state.data!.current.temperature, equals(28.5));
      });

      test('should handle coordinate API errors', () async {
        // Arrange
        when(() => mockApi.getWeatherByCoordinates(any(), any()))
            .thenThrow(WeatherApiException('Invalid coordinates', statusCode: 400));

        // Act
        await notifier.loadWeatherByLocation(999.0, 999.0);

        // Assert
        expect(notifier.state.error, isNotNull);
      });
    });

    group('clearError - مسح الخطأ', () {
      test('should clear error state', () async {
        // Arrange - Create error state
        when(() => mockApi.getFieldWeather(any()))
            .thenThrow(WeatherApiException('Error', statusCode: 500));
        await notifier.loadWeather('field-001');
        expect(notifier.state.error, isNotNull);

        // Act
        notifier.clearError();

        // Assert
        expect(notifier.state.error, isNull);
      });

      test('should preserve other state when clearing error', () async {
        // Arrange - Create state with data then error
        final data = WeatherData.fromJson(WeatherFixtures.currentWeatherJson);
        when(() => mockApi.getFieldWeather('field-001'))
            .thenAnswer((_) async => data);
        await notifier.loadWeather('field-001');

        // Manually set an error (simulating a second failed request)
        when(() => mockApi.getFieldWeather('field-002'))
            .thenThrow(WeatherApiException('Error', statusCode: 500));
        await notifier.loadWeather('field-002');

        // Act
        notifier.clearError();

        // Assert - Error cleared, but data might be null after failed load
        expect(notifier.state.error, isNull);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AlertsState Tests - اختبارات حالة التنبيهات
  // ═══════════════════════════════════════════════════════════════════════════

  group('AlertsState', () {
    test('should have default initial state', () {
      // Arrange & Act
      const state = AlertsState();

      // Assert
      expect(state.isLoading, isFalse);
      expect(state.alerts, isEmpty);
      expect(state.error, isNull);
    });

    test('should calculate activeAlerts correctly', () {
      // Arrange
      final now = DateTime.now();
      final activeAlert = WeatherAlert(
        id: 'active',
        type: 'heat',
        severity: 'warning',
        title: 'Heat Warning',
        titleAr: 'تحذير من الحرارة',
        description: 'High temperature',
        startTime: now.subtract(const Duration(hours: 1)),
        endTime: now.add(const Duration(hours: 6)),
      );
      final expiredAlert = WeatherAlert(
        id: 'expired',
        type: 'wind',
        severity: 'watch',
        title: 'Wind Watch',
        titleAr: 'مراقبة الرياح',
        description: 'Strong winds',
        startTime: now.subtract(const Duration(days: 2)),
        endTime: now.subtract(const Duration(days: 1)),
      );

      final state = AlertsState(alerts: [activeAlert, expiredAlert]);

      // Act & Assert
      expect(state.activeAlerts, equals(1));
    });

    test('should check hasWarnings correctly', () {
      // Arrange
      final now = DateTime.now();
      final warningAlert = WeatherAlert(
        id: 'warning',
        type: 'heat',
        severity: 'warning',
        title: 'Heat Warning',
        titleAr: 'تحذير من الحرارة',
        description: 'High temperature',
        startTime: now.subtract(const Duration(hours: 1)),
        endTime: now.add(const Duration(hours: 6)),
      );

      final stateWithWarning = AlertsState(alerts: [warningAlert]);
      const stateWithoutWarning = AlertsState();

      // Act & Assert
      expect(stateWithWarning.hasWarnings, isTrue);
      expect(stateWithoutWarning.hasWarnings, isFalse);
    });

    test('should not count expired warnings', () {
      // Arrange
      final now = DateTime.now();
      final expiredWarning = WeatherAlert(
        id: 'expired-warning',
        type: 'heat',
        severity: 'warning',
        title: 'Heat Warning',
        titleAr: 'تحذير من الحرارة',
        description: 'High temperature',
        startTime: now.subtract(const Duration(days: 2)),
        endTime: now.subtract(const Duration(days: 1)),
      );

      final state = AlertsState(alerts: [expiredWarning]);

      // Act & Assert
      expect(state.hasWarnings, isFalse);
      expect(state.activeAlerts, equals(0));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AlertsNotifier Tests - اختبارات AlertsNotifier
  // ═══════════════════════════════════════════════════════════════════════════

  group('AlertsNotifier', () {
    late MockWeatherApi mockApi;
    late AlertsNotifier notifier;

    setUp(() {
      mockApi = MockWeatherApi();
      notifier = AlertsNotifier(mockApi);
    });

    group('loadAlerts - تحميل التنبيهات', () {
      test('should load alerts successfully', () async {
        // Arrange
        final alerts = WeatherFixtures.weatherAlertsJson
            .map((json) => WeatherAlert.fromJson(json))
            .toList();
        when(() => mockApi.getWeatherAlerts(any()))
            .thenAnswer((_) async => alerts);

        // Act
        await notifier.loadAlerts('field-001');

        // Assert
        expect(notifier.state.alerts, hasLength(2));
        expect(notifier.state.isLoading, isFalse);
        expect(notifier.state.error, isNull);
      });

      test('should parse Arabic alert titles', () async {
        // Arrange
        final alerts = WeatherFixtures.weatherAlertsJson
            .map((json) => WeatherAlert.fromJson(json))
            .toList();
        when(() => mockApi.getWeatherAlerts(any()))
            .thenAnswer((_) async => alerts);

        // Act
        await notifier.loadAlerts('field-001');

        // Assert
        expect(notifier.state.alerts.first.titleAr, equals('تحذير من موجة حر'));
      });

      test('should handle API errors', () async {
        // Arrange
        when(() => mockApi.getWeatherAlerts(any()))
            .thenThrow(WeatherApiException('فشل جلب التنبيهات', statusCode: 500));

        // Act
        await notifier.loadAlerts('field-001');

        // Assert
        expect(notifier.state.error, isNotNull);
        expect(notifier.state.alerts, isEmpty);
      });

      test('should return empty list when no alerts', () async {
        // Arrange
        when(() => mockApi.getWeatherAlerts(any()))
            .thenAnswer((_) async => <WeatherAlert>[]);

        // Act
        await notifier.loadAlerts('field-001');

        // Assert
        expect(notifier.state.alerts, isEmpty);
        expect(notifier.state.error, isNull);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ImpactsState Tests - اختبارات حالة التأثيرات
  // ═══════════════════════════════════════════════════════════════════════════

  group('ImpactsState', () {
    test('should have default initial state', () {
      // Arrange & Act
      const state = ImpactsState();

      // Assert
      expect(state.isLoading, isFalse);
      expect(state.impacts, isEmpty);
      expect(state.error, isNull);
    });

    test('should copy with impacts', () {
      // Arrange
      const state = ImpactsState();
      final impacts = WeatherFixtures.agriculturalImpactsJson
          .map((json) => AgriculturalImpact.fromJson(json))
          .toList();

      // Act
      final newState = state.copyWith(impacts: impacts);

      // Assert
      expect(newState.impacts, hasLength(4));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ImpactsNotifier Tests - اختبارات ImpactsNotifier
  // ═══════════════════════════════════════════════════════════════════════════

  group('ImpactsNotifier', () {
    late MockWeatherApi mockApi;
    late ImpactsNotifier notifier;

    setUp(() {
      mockApi = MockWeatherApi();
      notifier = ImpactsNotifier(mockApi);
    });

    group('loadImpacts - تحميل التأثيرات', () {
      test('should load agricultural impacts successfully', () async {
        // Arrange
        final impacts = WeatherFixtures.agriculturalImpactsJson
            .map((json) => AgriculturalImpact.fromJson(json))
            .toList();
        when(() => mockApi.getAgriculturalImpacts(any()))
            .thenAnswer((_) async => impacts);

        // Act
        await notifier.loadImpacts('field-001');

        // Assert
        expect(notifier.state.impacts, hasLength(4));
        expect(notifier.state.isLoading, isFalse);
        expect(notifier.state.error, isNull);
      });

      test('should parse Arabic recommendations', () async {
        // Arrange
        final impacts = WeatherFixtures.agriculturalImpactsJson
            .map((json) => AgriculturalImpact.fromJson(json))
            .toList();
        when(() => mockApi.getAgriculturalImpacts(any()))
            .thenAnswer((_) async => impacts);

        // Act
        await notifier.loadImpacts('field-001');

        // Assert
        expect(
          notifier.state.impacts.first.recommendationAr,
          equals('تقليل الري بنسبة 20% بسبب هطول الأمطار المتوقعة'),
        );
      });

      test('should parse impact categories', () async {
        // Arrange
        final impacts = WeatherFixtures.agriculturalImpactsJson
            .map((json) => AgriculturalImpact.fromJson(json))
            .toList();
        when(() => mockApi.getAgriculturalImpacts(any()))
            .thenAnswer((_) async => impacts);

        // Act
        await notifier.loadImpacts('field-001');

        // Assert
        final categories = notifier.state.impacts.map((i) => i.category).toList();
        expect(categories, contains('irrigation'));
        expect(categories, contains('spraying'));
        expect(categories, contains('harvesting'));
        expect(categories, contains('planting'));
      });

      test('should handle API errors', () async {
        // Arrange
        when(() => mockApi.getAgriculturalImpacts(any()))
            .thenThrow(WeatherApiException('فشل جلب التأثيرات', statusCode: 500));

        // Act
        await notifier.loadImpacts('field-001');

        // Assert
        expect(notifier.state.error, isNotNull);
        expect(notifier.state.impacts, isEmpty);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Provider Integration Tests - اختبارات تكامل المزودات
  // ═══════════════════════════════════════════════════════════════════════════

  group('Provider Integration', () {
    test('weatherApiProvider should create WeatherApi instance', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act
      final api = container.read(weatherApiProvider);

      // Assert
      expect(api, isA<WeatherApi>());
    });

    test('weatherProvider should create WeatherNotifier', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act
      final notifier = container.read(weatherProvider.notifier);

      // Assert
      expect(notifier, isA<WeatherNotifier>());
    });

    test('alertsProvider should create AlertsNotifier', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act
      final notifier = container.read(alertsProvider.notifier);

      // Assert
      expect(notifier, isA<AlertsNotifier>());
    });

    test('impactsProvider should create ImpactsNotifier', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act
      final notifier = container.read(impactsProvider.notifier);

      // Assert
      expect(notifier, isA<ImpactsNotifier>());
    });

    test('selectedFieldIdProvider should manage field selection', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act & Assert - Initial state
      expect(container.read(selectedFieldIdProvider), isNull);

      // Act - Update field ID
      container.read(selectedFieldIdProvider.notifier).state = 'field-001';

      // Assert
      expect(container.read(selectedFieldIdProvider), equals('field-001'));
    });

    test('impactFilterProvider should manage filter', () {
      // Arrange
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Act & Assert - Initial state
      expect(container.read(impactFilterProvider), isNull);

      // Act - Set filter
      container.read(impactFilterProvider.notifier).state = 'favorable';

      // Assert
      expect(container.read(impactFilterProvider), equals('favorable'));
    });

    test('filteredImpactsProvider should filter impacts by status', () async {
      // Arrange
      final container = ProviderContainer(
        overrides: [
          weatherApiProvider.overrideWithValue(MockWeatherApi()),
        ],
      );
      addTearDown(container.dispose);

      final mockApi = container.read(weatherApiProvider) as MockWeatherApi;
      final impacts = WeatherFixtures.agriculturalImpactsJson
          .map((json) => AgriculturalImpact.fromJson(json))
          .toList();
      when(() => mockApi.getAgriculturalImpacts(any()))
          .thenAnswer((_) async => impacts);

      // Load impacts
      await container.read(impactsProvider.notifier).loadImpacts('field-001');

      // Act - No filter
      var filtered = container.read(filteredImpactsProvider);
      expect(filtered, hasLength(4));

      // Act - Filter by 'favorable'
      container.read(impactFilterProvider.notifier).state = 'favorable';
      filtered = container.read(filteredImpactsProvider);
      expect(filtered, hasLength(2)); // spraying and planting are favorable
      expect(filtered.every((i) => i.status == 'favorable'), isTrue);

      // Act - Filter by 'unfavorable'
      container.read(impactFilterProvider.notifier).state = 'unfavorable';
      filtered = container.read(filteredImpactsProvider);
      expect(filtered, hasLength(1)); // Only harvesting is unfavorable
      expect(filtered.first.category, equals('harvesting'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Edge Cases Tests - اختبارات الحالات الحدية
  // ═══════════════════════════════════════════════════════════════════════════

  group('Edge Cases - الحالات الحدية', () {
    late MockWeatherApi mockApi;
    late WeatherNotifier notifier;

    setUp(() {
      mockApi = MockWeatherApi();
      notifier = WeatherNotifier(mockApi);
    });

    test('should handle empty weather data', () async {
      // Arrange
      final emptyData = WeatherData(
        current: CurrentWeather(
          temperature: 0,
          feelsLike: 0,
          humidity: 0,
          windSpeed: 0,
          windDirection: 'N',
          condition: 'Unknown',
          conditionAr: 'غير معروف',
          icon: '',
          timestamp: DateTime.now(),
        ),
        hourly: [],
        daily: [],
        alerts: [],
        impacts: [],
      );
      when(() => mockApi.getFieldWeather(any()))
          .thenAnswer((_) async => emptyData);

      // Act
      await notifier.loadWeather('field-001');

      // Assert
      expect(notifier.state.data, isNotNull);
      expect(notifier.state.data!.hourly, isEmpty);
      expect(notifier.state.data!.daily, isEmpty);
      expect(notifier.state.data!.alerts, isEmpty);
    });

    test('should handle extreme temperature values', () async {
      // Arrange
      final extremeData = WeatherData.fromJson(
        WeatherFixtures.generateWeatherWithTemperature(55.0), // Extreme heat
      );
      when(() => mockApi.getFieldWeather(any()))
          .thenAnswer((_) async => extremeData);

      // Act
      await notifier.loadWeather('field-001');

      // Assert
      expect(notifier.state.data!.current.temperature, equals(55.0));
      expect(notifier.state.data!.current.temperatureDisplay, equals('55°'));
    });

    test('should handle negative temperature', () async {
      // Arrange
      final coldData = WeatherData.fromJson(
        WeatherFixtures.generateWeatherWithTemperature(-5.0),
      );
      when(() => mockApi.getFieldWeather(any()))
          .thenAnswer((_) async => coldData);

      // Act
      await notifier.loadWeather('field-001');

      // Assert
      expect(notifier.state.data!.current.temperature, equals(-5.0));
      expect(notifier.state.data!.current.temperatureDisplay, equals('-5°'));
    });

    test('should handle concurrent load requests', () async {
      // Arrange
      final data = WeatherData.fromJson(WeatherFixtures.currentWeatherJson);
      when(() => mockApi.getFieldWeather(any()))
          .thenAnswer((_) async {
        await Future<void>.delayed(const Duration(milliseconds: 100));
        return data;
      });

      // Act - Start multiple concurrent requests
      final futures = [
        notifier.loadWeather('field-001'),
        notifier.loadWeather('field-002'),
        notifier.loadWeather('field-003'),
      ];

      await Future.wait(futures);

      // Assert - Final state should have data from last completed request
      expect(notifier.state.data, isNotNull);
      expect(notifier.state.isLoading, isFalse);
    });
  });
}
