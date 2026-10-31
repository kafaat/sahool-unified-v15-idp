import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/weather/data/remote/weather_api.dart';
import 'package:sahool_field_app/features/weather/domain/entities/weather_entities.dart';
import 'package:sahool_field_app/features/weather/presentation/providers/weather_provider.dart';

import 'weather_fixtures.dart';

class MockWeatherApi extends Mock implements WeatherApi {}

void main() {
  for (final kind in ['field', 'coordinates', 'alerts', 'impacts']) {
    for (final fail in [false, true]) {
      test('$kind ignores ${fail ? 'error' : 'success'} after disposal',
          () async {
        final api = MockWeatherApi();
        final weather = Completer<WeatherData>();
        final alerts = Completer<List<WeatherAlert>>();
        final impacts = Completer<List<AgriculturalImpact>>();
        when(() => api.getFieldWeather(any()))
            .thenAnswer((_) => weather.future);
        when(() => api.getWeatherByCoordinates(any(), any()))
            .thenAnswer((_) => weather.future);
        when(() => api.getWeatherAlerts(any()))
            .thenAnswer((_) => alerts.future);
        when(() => api.getAgriculturalImpacts(any()))
            .thenAnswer((_) => impacts.future);
        final notifier = (switch (kind) {
          'alerts' => AlertsNotifier(api),
          'impacts' => ImpactsNotifier(api),
          _ => WeatherNotifier(api),
        }) as StateNotifier<dynamic>;
        Future<void> request() => switch (kind) {
              'field' => (notifier as WeatherNotifier).loadWeather('field-001'),
              'coordinates' =>
                (notifier as WeatherNotifier).loadWeatherByLocation(15, 44),
              'alerts' => (notifier as AlertsNotifier).loadAlerts('field-001'),
              _ => (notifier as ImpactsNotifier).loadImpacts('field-001'),
            };
        final events = <dynamic>[];
        notifier.addListener(events.add, fireImmediately: false);
        final pending = request();
        expect(events, hasLength(1));
        notifier.dispose();
        switch (kind) {
          case 'alerts':
            fail
                ? alerts.completeError(Exception('failed'))
                : alerts.complete([]);
          case 'impacts':
            fail
                ? impacts.completeError(Exception('failed'))
                : impacts.complete([]);
          default:
            fail
                ? weather.completeError(Exception('failed'))
                : weather.complete(
                    WeatherData.fromJson(WeatherFixtures.currentWeatherJson));
        }
        await pending;
        // A stale caller must neither read state nor start another API request.
        await request();
        expect(events, hasLength(1));
        switch (kind) {
          case 'field':
            verify(() => api.getFieldWeather('field-001')).called(1);
          case 'coordinates':
            verify(() => api.getWeatherByCoordinates(15, 44)).called(1);
          case 'alerts':
            verify(() => api.getWeatherAlerts('field-001')).called(1);
          default:
            verify(() => api.getAgriculturalImpacts('field-001')).called(1);
        }
      });
    }
  }

  test('token dependency replacement safely retires an in-flight notifier',
      () async {
    final api = MockWeatherApi();
    final response = Completer<List<AgriculturalImpact>>();
    final refreshedApi = Completer<WeatherApi>();
    var reads = 0;
    when(() => api.getAgriculturalImpacts('field-001'))
        .thenAnswer((_) => response.future);
    final container = ProviderContainer(overrides: [
      weatherApiWithTokenProvider.overrideWith((ref) {
        return reads++ == 0 ? Future.value(api) : refreshedApi.future;
      }),
    ]);
    addTearDown(container.dispose);
    await container.read(weatherApiWithTokenProvider.future);
    final original = container.read(impactsProvider.notifier);
    final pending = original.loadImpacts('field-001');

    container.invalidate(weatherApiWithTokenProvider);
    final replacementReady = container.read(weatherApiWithTokenProvider.future);
    refreshedApi.complete(MockWeatherApi());
    await replacementReady;
    final replacement = container.read(impactsProvider.notifier);
    expect(identical(original, replacement), isFalse);
    response.complete([]);
    await pending;
    await original.loadImpacts('field-001');
    verify(() => api.getAgriculturalImpacts('field-001')).called(1);
    expect(container.read(impactsProvider).impacts, isEmpty);
    expect(container.read(impactsProvider).isLoading, isFalse);
  });
}
