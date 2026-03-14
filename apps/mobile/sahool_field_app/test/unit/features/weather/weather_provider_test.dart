import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/weather/presentation/providers/weather_provider.dart';
import 'package:sahool_field_app/features/weather/data/repo/weather_repo.dart';
import 'package:sahool_field_app/features/weather/domain/entities/weather_entities.dart';

class MockWeatherRepository extends Mock implements WeatherRepository {}

void main() {
  group('WeatherState', () {
    test('default state has no loading, no data, no error', () {
      const state = WeatherState();
      expect(state.isLoading, false);
      expect(state.data, isNull);
      expect(state.error, isNull);
    });

    test('copyWith preserves values when not specified', () {
      const state = WeatherState(isLoading: true);
      final copied = state.copyWith();
      expect(copied.isLoading, true);
    });

    test('copyWith overrides isLoading', () {
      const state = WeatherState(isLoading: true);
      final copied = state.copyWith(isLoading: false);
      expect(copied.isLoading, false);
    });

    test('copyWith clears error when null is passed', () {
      const state = WeatherState(error: 'some error');
      final copied = state.copyWith(error: null);
      expect(copied.error, isNull);
    });
  });

  group('WeatherNotifier', () {
    late MockWeatherRepository mockRepo;
    late WeatherNotifier notifier;

    setUp(() {
      mockRepo = MockWeatherRepository();
      notifier = WeatherNotifier(mockRepo);
    });

    test('initial state is not loading', () {
      expect(notifier.state.isLoading, false);
      expect(notifier.state.data, isNull);
    });

    test('loadWeather sets loading then data on success', () async {
      final weatherData = WeatherData(
        current: CurrentWeather(
          temperature: 25.0,
          feelsLike: 27.0,
          humidity: 60,
          windSpeed: 10.0,
          windDirection: 'NW',
          condition: 'Sunny',
          conditionAr: 'مشمس',
          icon: '☀️',
          timestamp: DateTime(2026, 3, 14),
        ),
        hourly: [],
        daily: [],
        alerts: [],
        impacts: [],
      );

      when(() => mockRepo.getWeatherForField('field-1'))
          .thenAnswer((_) async => weatherData);

      final future = notifier.loadWeather('field-1');

      // Should be loading
      expect(notifier.state.isLoading, true);

      await future;

      expect(notifier.state.isLoading, false);
      expect(notifier.state.data, weatherData);
      expect(notifier.state.error, isNull);
    });

    test('loadWeather sets error on failure', () async {
      when(() => mockRepo.getWeatherForField('field-1'))
          .thenThrow(Exception('Network error'));

      await notifier.loadWeather('field-1');

      expect(notifier.state.isLoading, false);
      expect(notifier.state.data, isNull);
      expect(notifier.state.error, isNotNull);
    });

    test('loadWeatherByLocation works correctly', () async {
      final weatherData = WeatherData(
        current: CurrentWeather(
          temperature: 30.0,
          feelsLike: 32.0,
          humidity: 50,
          windSpeed: 5.0,
          windDirection: 'N',
          condition: 'Clear',
          conditionAr: 'صاف',
          icon: '☀️',
          timestamp: DateTime(2026, 3, 14),
        ),
        hourly: [],
        daily: [],
        alerts: [],
        impacts: [],
      );

      when(() => mockRepo.getWeatherByCoordinates(24.7, 46.7))
          .thenAnswer((_) async => weatherData);

      await notifier.loadWeatherByLocation(24.7, 46.7);

      expect(notifier.state.isLoading, false);
      expect(notifier.state.data, weatherData);
    });

    test('loadWeatherByLocation sets error on failure', () async {
      when(() => mockRepo.getWeatherByCoordinates(any(), any()))
          .thenThrow(Exception('Timeout'));

      await notifier.loadWeatherByLocation(24.7, 46.7);

      expect(notifier.state.isLoading, false);
      expect(notifier.state.error, isNotNull);
    });

    test('clearError clears the error', () async {
      when(() => mockRepo.getWeatherForField('field-1'))
          .thenThrow(Exception('Error'));

      await notifier.loadWeather('field-1');
      expect(notifier.state.error, isNotNull);

      notifier.clearError();
      expect(notifier.state.error, isNull);
    });
  });

  group('AlertsState', () {
    test('default state has empty alerts', () {
      const state = AlertsState();
      expect(state.alerts, isEmpty);
      expect(state.isLoading, false);
      expect(state.error, isNull);
    });

    test('activeAlerts counts only future alerts', () {
      final state = AlertsState(
        alerts: [
          WeatherAlert(
            id: 'alert-1',
            type: 'heat',
            title: 'Heat Wave',
            titleAr: 'موجة حر',
            description: 'desc',
            severity: 'warning',
            startTime: DateTime.now().subtract(const Duration(hours: 2)),
            endTime: DateTime.now().add(const Duration(hours: 2)),
          ),
          WeatherAlert(
            id: 'alert-2',
            type: 'wind',
            title: 'Old Alert',
            titleAr: 'تنبيه قديم',
            description: 'desc',
            severity: 'info',
            startTime: DateTime.now().subtract(const Duration(days: 2)),
            endTime: DateTime.now().subtract(const Duration(days: 1)),
          ),
        ],
      );
      expect(state.activeAlerts, 1);
    });

    test('hasWarnings returns true for active warning alerts', () {
      final state = AlertsState(
        alerts: [
          WeatherAlert(
            id: 'alert-1',
            type: 'wind',
            title: 'Warning',
            titleAr: 'تحذير',
            description: 'desc',
            severity: 'warning',
            startTime: DateTime.now().subtract(const Duration(hours: 1)),
            endTime: DateTime.now().add(const Duration(hours: 1)),
          ),
        ],
      );
      expect(state.hasWarnings, true);
    });

    test('hasWarnings returns false for expired warning', () {
      final state = AlertsState(
        alerts: [
          WeatherAlert(
            id: 'alert-1',
            type: 'wind',
            title: 'Warning',
            titleAr: 'تحذير',
            description: 'desc',
            severity: 'warning',
            startTime: DateTime.now().subtract(const Duration(days: 2)),
            endTime: DateTime.now().subtract(const Duration(days: 1)),
          ),
        ],
      );
      expect(state.hasWarnings, false);
    });

    test('copyWith works correctly', () {
      const state = AlertsState(isLoading: true);
      final copied = state.copyWith(isLoading: false, error: 'err');
      expect(copied.isLoading, false);
      expect(copied.error, 'err');
    });
  });

  group('AlertsNotifier', () {
    late MockWeatherRepository mockRepo;
    late AlertsNotifier notifier;

    setUp(() {
      mockRepo = MockWeatherRepository();
      notifier = AlertsNotifier(mockRepo);
    });

    test('loadAlerts success', () async {
      final alerts = [
        WeatherAlert(
          id: 'alert-1',
          type: 'heat',
          title: 'Heat',
          titleAr: 'حر',
          description: 'desc',
          severity: 'warning',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 6)),
        ),
      ];

      when(() => mockRepo.getAlertsForField('field-1'))
          .thenAnswer((_) async => alerts);

      await notifier.loadAlerts('field-1');

      expect(notifier.state.isLoading, false);
      expect(notifier.state.alerts.length, 1);
    });

    test('loadAlerts failure sets error', () async {
      when(() => mockRepo.getAlertsForField('field-1'))
          .thenThrow(Exception('API error'));

      await notifier.loadAlerts('field-1');

      expect(notifier.state.isLoading, false);
      expect(notifier.state.error, isNotNull);
    });
  });

  group('ImpactsState', () {
    test('default state has empty impacts', () {
      const state = ImpactsState();
      expect(state.impacts, isEmpty);
      expect(state.isLoading, false);
    });

    test('copyWith works', () {
      const state = ImpactsState(isLoading: true);
      final copied = state.copyWith(isLoading: false);
      expect(copied.isLoading, false);
    });
  });

  group('ImpactsNotifier', () {
    late MockWeatherRepository mockRepo;
    late ImpactsNotifier notifier;

    setUp(() {
      mockRepo = MockWeatherRepository();
      notifier = ImpactsNotifier(mockRepo);
    });

    test('loadImpacts success', () async {
      final impacts = [
        AgriculturalImpact(
          category: 'irrigation',
          recommendation: 'Irrigate now',
          recommendationAr: 'اروِ الآن',
          status: 'favorable',
          reasons: ['Low soil moisture'],
        ),
      ];

      when(() => mockRepo.getImpactsForField('field-1'))
          .thenAnswer((_) async => impacts);

      await notifier.loadImpacts('field-1');

      expect(notifier.state.isLoading, false);
      expect(notifier.state.impacts.length, 1);
    });

    test('loadImpacts failure sets error', () async {
      when(() => mockRepo.getImpactsForField('field-1'))
          .thenThrow(Exception('API error'));

      await notifier.loadImpacts('field-1');

      expect(notifier.state.isLoading, false);
      expect(notifier.state.error, isNotNull);
    });
  });
}
