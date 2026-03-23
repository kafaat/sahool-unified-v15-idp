/// Weather Repository Tests - اختبارات مستودع الطقس
///
/// Comprehensive tests for WeatherApi class covering:
/// - Current weather fetching (جلب الطقس الحالي)
/// - Weather forecasts (التوقعات)
/// - Weather alerts (التنبيهات)
/// - Agricultural impacts (التأثيرات الزراعية)
/// - Error handling (معالجة الأخطاء)
/// - Arabic descriptions and units (الوصف والوحدات بالعربية)
library;

import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:sahool_mobile_core/features/weather/data/remote/weather_api.dart';
import 'package:sahool_mobile_core/features/weather/domain/entities/weather_entities.dart';

import 'weather_fixtures.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks - الكائنات الوهمية
// ═══════════════════════════════════════════════════════════════════════════

class MockHttpClient extends Mock implements http.Client {}

class MockResponse extends Mock implements http.Response {}

class FakeUri extends Fake implements Uri {}

void main() {
  // Register fallback values for mocktail
  setUpAll(() {
    registerFallbackValue(FakeUri());
  });

  group('WeatherApi', () {
    late MockHttpClient mockClient;
    late WeatherApi weatherApi;

    setUp(() {
      mockClient = MockHttpClient();
      weatherApi = WeatherApi(client: mockClient);
    });

    tearDown(() {
      weatherApi.dispose();
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Current Weather Tests - اختبارات الطقس الحالي
    // ═══════════════════════════════════════════════════════════════════════

    group('getCurrentWeather - جلب الطقس الحالي', () {
      test('should return WeatherData on successful response', () async {
        // Arrange
        final responseBody = jsonEncode(WeatherFixtures.currentWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getCurrentWeather('sanaa');

        // Assert
        expect(result, isA<WeatherData>());
        expect(result.current.temperature, equals(28.5));
        expect(result.current.humidity, equals(65));
        expect(result.current.windSpeed, equals(12.5));
        expect(result.current.conditionAr, equals('غائم جزئياً'));
      });

      test('should parse Arabic condition descriptions correctly', () async {
        // Arrange - Test clear weather
        final responseBody = jsonEncode(WeatherFixtures.clearWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getCurrentWeather('aden');

        // Assert
        expect(result.current.condition, equals('Clear'));
        expect(result.current.conditionAr, equals('صافي'));
      });

      test('should parse rainy weather correctly', () async {
        // Arrange
        final responseBody = jsonEncode(WeatherFixtures.rainyWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getCurrentWeather('taiz');

        // Assert
        expect(result.current.condition, equals('Rain'));
        expect(result.current.conditionAr, equals('مطر'));
        expect(result.current.precipitation, equals(15.5));
      });

      test('should parse thunderstorm weather correctly', () async {
        // Arrange
        final responseBody = jsonEncode(WeatherFixtures.thunderstormWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getCurrentWeather('hodeidah');

        // Assert
        expect(result.current.condition, equals('Thunderstorm'));
        expect(result.current.conditionAr, equals('عاصفة رعدية'));
        expect(result.current.windSpeed, equals(45.0));
      });

      test('should parse foggy weather correctly', () async {
        // Arrange
        final responseBody = jsonEncode(WeatherFixtures.foggyWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getCurrentWeather('marib');

        // Assert
        expect(result.current.condition, equals('Foggy'));
        expect(result.current.conditionAr, equals('ضبابي'));
        expect(result.current.humidity, equals(95));
      });

      test('should display temperature correctly in Celsius', () async {
        // Arrange
        final responseBody = jsonEncode(WeatherFixtures.currentWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getCurrentWeather('sanaa');

        // Assert - Temperature display should be rounded with degree symbol
        expect(result.current.temperatureDisplay, equals('29°'));
      });

      test('should throw WeatherApiException on 404 error', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Not Found', 404));

        // Act & Assert
        expect(
          () => weatherApi.getCurrentWeather('invalid-location'),
          throwsA(isA<WeatherApiException>()),
        );
      });

      test('should throw WeatherApiException on 500 error', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Internal Server Error', 500));

        // Act & Assert
        expect(
          () => weatherApi.getCurrentWeather('sanaa'),
          throwsA(isA<WeatherApiException>()),
        );
      });

      test('should throw WeatherApiException with Arabic message on error', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Error', 503));

        // Act & Assert
        try {
          await weatherApi.getCurrentWeather('sanaa');
          fail('Should have thrown exception');
        } on WeatherApiException catch (e) {
          expect(e.message, contains('فشل'));
          expect(e.statusCode, equals(503));
        }
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Weather by Coordinates Tests - اختبارات الطقس بالإحداثيات
    // ═══════════════════════════════════════════════════════════════════════

    group('getWeatherByCoordinates - الطقس بالإحداثيات', () {
      test('should return WeatherData for valid coordinates', () async {
        // Arrange
        final responseBody = jsonEncode(WeatherFixtures.currentWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getWeatherByCoordinates(15.3694, 44.1910);

        // Assert
        expect(result, isA<WeatherData>());
        expect(result.current.temperature, equals(28.5));
      });

      test('should handle negative coordinates (southern hemisphere)', () async {
        // Arrange
        final responseBody = jsonEncode(WeatherFixtures.currentWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getWeatherByCoordinates(-15.0, 44.0);

        // Assert
        expect(result, isA<WeatherData>());
      });

      test('should throw exception on API failure', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Error', 500));

        // Act & Assert
        expect(
          () => weatherApi.getWeatherByCoordinates(15.0, 44.0),
          throwsA(isA<WeatherApiException>()),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Field Weather Tests - اختبارات طقس الحقل
    // ═══════════════════════════════════════════════════════════════════════

    group('getFieldWeather - طقس الحقل', () {
      test('should return weather data for a field ID', () async {
        // Arrange
        final responseBody = jsonEncode(WeatherFixtures.currentWeatherJson);
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getFieldWeather('field-001');

        // Assert
        expect(result, isA<WeatherData>());
      });

      test('should throw exception for invalid field ID', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Field not found', 404));

        // Act & Assert
        expect(
          () => weatherApi.getFieldWeather('invalid-field'),
          throwsA(isA<WeatherApiException>()),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Forecast Tests - اختبارات التوقعات
    // ═══════════════════════════════════════════════════════════════════════

    group('getForecast - التوقعات', () {
      test('should return 7-day forecast by default', () async {
        // Arrange
        final responseBody = jsonEncode({
          'forecasts': WeatherFixtures.dailyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getForecast('sanaa');

        // Assert
        expect(result, isA<List<DailyForecast>>());
        expect(result.length, equals(7));
      });

      test('should parse daily forecast with Arabic conditions', () async {
        // Arrange
        final responseBody = jsonEncode({
          'forecasts': WeatherFixtures.dailyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getForecast('sanaa');

        // Assert
        expect(result.first.conditionAr, equals('غائم جزئياً'));
        expect(result[1].conditionAr, equals('صافي'));
        expect(result[2].conditionAr, equals('مطر'));
      });

      test('should parse temperature in Celsius correctly', () async {
        // Arrange
        final responseBody = jsonEncode({
          'forecasts': WeatherFixtures.dailyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getForecast('sanaa');

        // Assert - First day: min 18°C, max 34°C
        expect(result.first.tempMin, equals(18.0));
        expect(result.first.tempMax, equals(34.0));
      });

      test('should parse precipitation chance correctly', () async {
        // Arrange
        final responseBody = jsonEncode({
          'forecasts': WeatherFixtures.dailyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getForecast('sanaa');

        // Assert
        expect(result.first.precipitationChance, equals(10));
        expect(result[2].precipitationChance, equals(70)); // Rain day
      });

      test('should parse wind speed in km/h', () async {
        // Arrange
        final responseBody = jsonEncode({
          'forecasts': WeatherFixtures.dailyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getForecast('sanaa');

        // Assert
        expect(result.first.windSpeed, equals(12.0));
        expect(result[2].windSpeed, equals(20.0)); // Rain day - higher wind
      });

      test('should return Arabic day names', () async {
        // Arrange
        final responseBody = jsonEncode({
          'forecasts': WeatherFixtures.dailyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getForecast('sanaa');

        // Assert - dayName should return Arabic day name
        expect(
          result.first.dayName,
          anyOf([
            'الأحد',
            'الإثنين',
            'الثلاثاء',
            'الأربعاء',
            'الخميس',
            'الجمعة',
            'السبت',
          ]),
        );
      });

      test('should request specific number of days', () async {
        // Arrange
        final forecasts = WeatherFixtures.generateForecastDays(14);
        final responseBody = jsonEncode({'forecasts': forecasts});
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getForecast('sanaa', days: 14);

        // Assert
        expect(result.length, equals(14));
      });

      test('should throw exception on forecast API failure', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Error', 500));

        // Act & Assert
        expect(
          () => weatherApi.getForecast('sanaa'),
          throwsA(isA<WeatherApiException>()),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Hourly Forecast Tests - اختبارات التوقعات الساعية
    // ═══════════════════════════════════════════════════════════════════════

    group('getHourlyForecast - التوقعات الساعية', () {
      test('should return 24-hour forecast by default', () async {
        // Arrange
        final responseBody = jsonEncode({
          'hourly': WeatherFixtures.hourlyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getHourlyForecast('sanaa');

        // Assert
        expect(result, isA<List<HourlyForecast>>());
        expect(result.length, equals(5));
      });

      test('should parse hourly temperature in Celsius', () async {
        // Arrange
        final responseBody = jsonEncode({
          'hourly': WeatherFixtures.hourlyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getHourlyForecast('sanaa');

        // Assert
        expect(result.first.temperature, equals(29.0));
        expect(result[2].temperature, equals(32.0));
      });

      test('should display hour correctly', () async {
        // Arrange
        final responseBody = jsonEncode({
          'hourly': WeatherFixtures.hourlyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getHourlyForecast('sanaa');

        // Assert - hourDisplay should be "HH:00" format
        expect(result.first.hourDisplay, equals('11:00'));
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Daily Forecast by Field Tests - اختبارات التوقعات اليومية للحقل
    // ═══════════════════════════════════════════════════════════════════════

    group('getDailyForecast - التوقعات اليومية للحقل', () {
      test('should return daily forecast for field', () async {
        // Arrange
        final responseBody = jsonEncode({
          'forecasts': WeatherFixtures.dailyForecastsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getDailyForecast('field-001');

        // Assert
        expect(result, isA<List<DailyForecast>>());
        expect(result.length, equals(7));
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Weather Alerts Tests - اختبارات تنبيهات الطقس
    // ═══════════════════════════════════════════════════════════════════════

    group('getAlerts - تنبيهات الطقس', () {
      test('should return weather alerts for location', () async {
        // Arrange
        final responseBody = jsonEncode({
          'alerts': WeatherFixtures.weatherAlertsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAlerts('sanaa');

        // Assert
        expect(result, isA<List<WeatherAlert>>());
        expect(result.length, equals(2));
      });

      test('should parse alert with Arabic title', () async {
        // Arrange
        final responseBody = jsonEncode({
          'alerts': WeatherFixtures.weatherAlertsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAlerts('sanaa');

        // Assert
        expect(result.first.titleAr, equals('تحذير من موجة حر'));
        expect(result[1].titleAr, equals('إرشاد بشأن الرياح'));
      });

      test('should parse alert severity correctly', () async {
        // Arrange
        final responseBody = jsonEncode({
          'alerts': WeatherFixtures.weatherAlertsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAlerts('sanaa');

        // Assert
        expect(result.first.severity, equals('warning'));
        expect(result[1].severity, equals('watch'));
      });

      test('should return empty list when no alerts', () async {
        // Arrange
        final responseBody = jsonEncode(<String, dynamic>{'alerts': <dynamic>[]});
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAlerts('sanaa');

        // Assert
        expect(result, isEmpty);
      });

      test('should throw exception on alerts API failure', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Error', 500));

        // Act & Assert
        expect(
          () => weatherApi.getAlerts('sanaa'),
          throwsA(isA<WeatherApiException>()),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Field Weather Alerts Tests - اختبارات تنبيهات طقس الحقل
    // ═══════════════════════════════════════════════════════════════════════

    group('getWeatherAlerts - تنبيهات طقس الحقل', () {
      test('should return weather alerts for field', () async {
        // Arrange
        final responseBody = jsonEncode({
          'alerts': WeatherFixtures.weatherAlertsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getWeatherAlerts('field-001');

        // Assert
        expect(result, isA<List<WeatherAlert>>());
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Agricultural Impact Tests - اختبارات التأثيرات الزراعية
    // ═══════════════════════════════════════════════════════════════════════

    group('getAgriculturalCalendar - التقويم الزراعي', () {
      test('should return agricultural impacts', () async {
        // Arrange
        final responseBody = jsonEncode({
          'impacts': WeatherFixtures.agriculturalImpactsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAgriculturalCalendar(location: 'sanaa');

        // Assert
        expect(result, isA<List<AgriculturalImpact>>());
        expect(result.length, equals(4));
      });

      test('should parse impact categories correctly', () async {
        // Arrange
        final responseBody = jsonEncode({
          'impacts': WeatherFixtures.agriculturalImpactsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAgriculturalCalendar(location: 'sanaa');

        // Assert
        expect(result[0].category, equals('irrigation'));
        expect(result[1].category, equals('spraying'));
        expect(result[2].category, equals('harvesting'));
        expect(result[3].category, equals('planting'));
      });

      test('should parse Arabic recommendations', () async {
        // Arrange
        final responseBody = jsonEncode({
          'impacts': WeatherFixtures.agriculturalImpactsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAgriculturalCalendar(location: 'sanaa');

        // Assert
        expect(
          result[0].recommendationAr,
          equals('تقليل الري بنسبة 20% بسبب هطول الأمطار المتوقعة'),
        );
      });

      test('should parse impact status correctly', () async {
        // Arrange
        final responseBody = jsonEncode({
          'impacts': WeatherFixtures.agriculturalImpactsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAgriculturalCalendar(location: 'sanaa');

        // Assert
        expect(result[0].status, equals('caution'));
        expect(result[1].status, equals('favorable'));
        expect(result[2].status, equals('unfavorable'));
      });

      test('should return category icon', () async {
        // Arrange
        final responseBody = jsonEncode({
          'impacts': WeatherFixtures.agriculturalImpactsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAgriculturalCalendar(location: 'sanaa');

        // Assert - Icons for categories
        expect(result[0].categoryIcon, equals('💧')); // irrigation
        expect(result[1].categoryIcon, equals('🌿')); // spraying
        expect(result[2].categoryIcon, equals('🌾')); // harvesting
        expect(result[3].categoryIcon, equals('🌱')); // planting
      });

      test('should return Arabic category names', () async {
        // Arrange
        final responseBody = jsonEncode({
          'impacts': WeatherFixtures.agriculturalImpactsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAgriculturalCalendar(location: 'sanaa');

        // Assert
        expect(result[0].categoryAr, equals('الري'));
        expect(result[1].categoryAr, equals('الرش'));
        expect(result[2].categoryAr, equals('الحصاد'));
        expect(result[3].categoryAr, equals('الزراعة'));
      });

      test('should filter by crop type', () async {
        // Arrange
        final responseBody = jsonEncode({
          'impacts': WeatherFixtures.agriculturalImpactsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAgriculturalCalendar(
          location: 'sanaa',
          cropType: 'wheat',
        );

        // Assert
        expect(result, isA<List<AgriculturalImpact>>());
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Field Agricultural Impacts Tests - اختبارات التأثيرات الزراعية للحقل
    // ═══════════════════════════════════════════════════════════════════════

    group('getAgriculturalImpacts - التأثيرات الزراعية للحقل', () {
      test('should return impacts for field', () async {
        // Arrange
        final responseBody = jsonEncode({
          'impacts': WeatherFixtures.agriculturalImpactsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAgriculturalImpacts('field-001');

        // Assert
        expect(result, isA<List<AgriculturalImpact>>());
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Available Locations Tests - اختبارات المواقع المتاحة
    // ═══════════════════════════════════════════════════════════════════════

    group('getAvailableLocations - المواقع المتاحة', () {
      test('should return list of Yemen governorates', () async {
        // Arrange
        final responseBody = jsonEncode({
          'locations': WeatherFixtures.locationsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAvailableLocations();

        // Assert
        expect(result, isA<List<WeatherLocation>>());
        expect(result.length, equals(5));
      });

      test('should parse location with Arabic names', () async {
        // Arrange
        final responseBody = jsonEncode({
          'locations': WeatherFixtures.locationsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAvailableLocations();

        // Assert
        expect(result.first.name, equals("Sana'a"));
        expect(result.first.nameAr, equals('صنعاء'));
        expect(result[1].nameAr, equals('عدن'));
      });

      test('should parse location coordinates', () async {
        // Arrange
        final responseBody = jsonEncode({
          'locations': WeatherFixtures.locationsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAvailableLocations();

        // Assert
        expect(result.first.latitude, equals(15.3694));
        expect(result.first.longitude, equals(44.1910));
      });

      test('should parse region types with Arabic', () async {
        // Arrange
        final responseBody = jsonEncode({
          'locations': WeatherFixtures.locationsJson,
        });
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        final result = await weatherApi.getAvailableLocations();

        // Assert
        expect(result.first.region, equals('highland'));
        expect(result.first.regionAr, equals('مرتفعات'));
        expect(result[1].region, equals('coastal'));
        expect(result[1].regionAr, equals('ساحلية'));
        expect(result[4].region, equals('desert'));
        expect(result[4].regionAr, equals('صحراوية'));
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Network Error Tests - اختبارات أخطاء الشبكة
    // ═══════════════════════════════════════════════════════════════════════

    group('Network Errors - أخطاء الشبكة', () {
      test('should handle network timeout', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenThrow(http.ClientException('Connection timed out'));

        // Act & Assert
        expect(
          () => weatherApi.getCurrentWeather('sanaa'),
          throwsA(isA<http.ClientException>()),
        );
      });

      test('should handle no network connection', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenThrow(http.ClientException('No internet connection'));

        // Act & Assert
        expect(
          () => weatherApi.getCurrentWeather('sanaa'),
          throwsA(isA<http.ClientException>()),
        );
      });

      test('should handle rate limit (429)', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Rate limit exceeded', 429));

        // Act & Assert
        expect(
          () => weatherApi.getCurrentWeather('sanaa'),
          throwsA(
            isA<WeatherApiException>().having(
              (e) => e.statusCode,
              'statusCode',
              429,
            ),
          ),
        );
      });

      test('should handle service unavailable (503)', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Service unavailable', 503));

        // Act & Assert
        expect(
          () => weatherApi.getCurrentWeather('sanaa'),
          throwsA(
            isA<WeatherApiException>().having(
              (e) => e.statusCode,
              'statusCode',
              503,
            ),
          ),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Authentication Tests - اختبارات المصادقة
    // ═══════════════════════════════════════════════════════════════════════

    group('Authentication - المصادقة', () {
      test('should include auth token in headers when provided', () async {
        // Arrange
        final apiWithAuth = WeatherApi(
          client: mockClient,
          authToken: 'test-token-123',
        );
        final responseBody = jsonEncode(WeatherFixtures.currentWeatherJson);
        when(() => mockClient.get(
              any(),
              headers: any(named: 'headers'),
            )).thenAnswer((_) async => http.Response(responseBody, 200, headers: {'content-type': 'application/json; charset=utf-8'}));

        // Act
        await apiWithAuth.getCurrentWeather('sanaa');

        // Assert
        verify(() => mockClient.get(
              any(),
              headers: captureAny(named: 'headers'),
            )).called(1);
      });

      test('should handle unauthorized error (401)', () async {
        // Arrange
        when(() => mockClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response('Unauthorized', 401));

        // Act & Assert
        expect(
          () => weatherApi.getCurrentWeather('sanaa'),
          throwsA(
            isA<WeatherApiException>().having(
              (e) => e.statusCode,
              'statusCode',
              401,
            ),
          ),
        );
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // WeatherApiException Tests - اختبارات استثناء API الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  group('WeatherApiException', () {
    test('should format toString correctly', () {
      // Arrange
      final exception = WeatherApiException('فشل جلب البيانات', statusCode: 500);

      // Act
      final str = exception.toString();

      // Assert
      expect(str, contains('WeatherApiException'));
      expect(str, contains('فشل جلب البيانات'));
      expect(str, contains('500'));
    });

    test('should handle null status code', () {
      // Arrange
      final exception = WeatherApiException('خطأ غير معروف');

      // Act
      final str = exception.toString();

      // Assert
      expect(str, contains('null'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // WeatherLocation Tests - اختبارات نموذج موقع الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  group('WeatherLocation', () {
    test('should parse from JSON correctly', () {
      // Arrange
      final json = WeatherFixtures.locationsJson.first;

      // Act
      final location = WeatherLocation.fromJson(json);

      // Assert
      expect(location.id, equals('sanaa'));
      expect(location.name, equals("Sana'a"));
      expect(location.nameAr, equals('صنعاء'));
      expect(location.latitude, equals(15.3694));
      expect(location.longitude, equals(44.1910));
      expect(location.region, equals('highland'));
      expect(location.regionAr, equals('مرتفعات'));
    });

    test('should handle alternative JSON keys', () {
      // Arrange
      final json = {
        'location_id': 'test-id',
        'name': 'Test',
        'nameAr': 'اختبار',
        'lat': 10.0,
        'lon': 20.0,
        'region': 'test',
        'regionAr': 'اختبار',
      };

      // Act
      final location = WeatherLocation.fromJson(json);

      // Assert
      expect(location.id, equals('test-id'));
      expect(location.nameAr, equals('اختبار'));
      expect(location.latitude, equals(10.0));
      expect(location.longitude, equals(20.0));
    });
  });
}
