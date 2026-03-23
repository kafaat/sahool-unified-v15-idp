import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/satellite/data/models/weather_data.dart';

void main() {
  group('WeatherAlertType', () {
    test('has 6 types', () {
      expect(WeatherAlertType.values, hasLength(6));
    });

    test('fromString parses valid values', () {
      expect(WeatherAlertType.fromString('frost'), WeatherAlertType.frost);
      expect(WeatherAlertType.fromString('heat'), WeatherAlertType.heat);
      expect(WeatherAlertType.fromString('drought'), WeatherAlertType.drought);
      expect(WeatherAlertType.fromString('heavy_rain'), WeatherAlertType.heavyRain);
      expect(WeatherAlertType.fromString('wind'), WeatherAlertType.wind);
    });

    test('fromString returns general for unknown', () {
      expect(WeatherAlertType.fromString('unknown'), WeatherAlertType.general);
    });

    test('has Arabic labels', () {
      expect(WeatherAlertType.frost.arabicLabel, 'صقيع');
      expect(WeatherAlertType.heat.arabicLabel, 'حرارة عالية');
      expect(WeatherAlertType.drought.arabicLabel, 'جفاف');
    });
  });

  group('DailyForecastSummary', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'date': '2026-03-15T00:00:00.000',
        'temp_min': 12.0,
        'temp_max': 28.0,
        'precipitation': 5.0,
        'condition': 'partly_cloudy',
        'condition_ar': 'غائم جزئياً',
        'icon': '02d',
      };

      final forecast = DailyForecastSummary.fromJson(json);
      expect(forecast.tempMin, 12.0);
      expect(forecast.tempMax, 28.0);
      expect(forecast.precipitation, 5.0);
      expect(forecast.condition, 'partly_cloudy');
      expect(forecast.conditionAr, 'غائم جزئياً');
      expect(forecast.icon, '02d');

      final exported = forecast.toJson();
      expect(exported['temp_min'], 12.0);
      expect(exported['condition'], 'partly_cloudy');
    });

    test('copyWith creates modified copy', () {
      final original = DailyForecastSummary(
        date: DateTime(2026, 3, 15),
        tempMin: 12.0,
        tempMax: 28.0,
        precipitation: 5.0,
        condition: 'cloudy',
        conditionAr: 'غائم',
      );

      final modified = original.copyWith(precipitation: 10.0);
      expect(modified.precipitation, 10.0);
      expect(modified.tempMin, 12.0);
    });
  });

  group('WeatherSummary', () {
    test('fromJson parses complete weather data', () {
      final json = {
        'field_id': 'field-001',
        'temperature': 25.0,
        'min_temp': 18.0,
        'max_temp': 32.0,
        'precipitation': 14.0,
        'humidity': 55.0,
        'et0': 5.5,
        'condition': 'sunny',
        'condition_ar': 'مشمس',
        'updated_at': '2026-03-15T12:00:00.000',
        'forecast': [
          {'date': '2026-03-16T00:00:00.000', 'temp_min': 17.0, 'temp_max': 30.0, 'precipitation': 0.0, 'condition': 'sunny', 'condition_ar': 'مشمس'},
        ],
      };

      final weather = WeatherSummary.fromJson(json);
      expect(weather.fieldId, 'field-001');
      expect(weather.temperature, 25.0);
      expect(weather.minTemp, 18.0);
      expect(weather.maxTemp, 32.0);
      expect(weather.precipitation, 14.0);
      expect(weather.humidity, 55.0);
      expect(weather.et0, 5.5);
      expect(weather.condition, 'sunny');
      expect(weather.conditionAr, 'مشمس');
      expect(weather.forecast, hasLength(1));
    });

    test('getIrrigationNeed calculates correctly', () {
      final weather = WeatherSummary(
        fieldId: 'f1',
        temperature: 25,
        minTemp: 18,
        maxTemp: 32,
        precipitation: 0.0,
        humidity: 40,
        et0: 5.5,
        condition: 'sunny',
        conditionAr: 'مشمس',
        updatedAt: DateTime(2026, 3, 15),
      );
      // No rain: irrigation need = et0
      expect(weather.getIrrigationNeed(), 5.5);
    });

    test('getIrrigationNeed reduces with rain', () {
      final weather = WeatherSummary(
        fieldId: 'f1',
        temperature: 25,
        minTemp: 18,
        maxTemp: 32,
        precipitation: 35.0, // 35mm over 7 days = 5mm/day
        humidity: 70,
        et0: 5.5,
        condition: 'rainy',
        conditionAr: 'ممطر',
        updatedAt: DateTime(2026, 3, 15),
      );
      // et0(5.5) - rain/7(5.0) = 0.5
      expect(weather.getIrrigationNeed(), closeTo(0.5, 0.01));
    });

    test('getIrrigationNeed clamps to 0 with heavy rain', () {
      final weather = WeatherSummary(
        fieldId: 'f1',
        temperature: 20,
        minTemp: 15,
        maxTemp: 25,
        precipitation: 100.0, // Heavy rain
        humidity: 90,
        et0: 3.0,
        condition: 'rainy',
        conditionAr: 'ممطر',
        updatedAt: DateTime(2026, 3, 15),
      );
      expect(weather.getIrrigationNeed(), 0.0);
    });

    test('toJson produces correct output', () {
      final weather = WeatherSummary(
        fieldId: 'f1',
        temperature: 25.0,
        minTemp: 18.0,
        maxTemp: 32.0,
        precipitation: 0.0,
        humidity: 40.0,
        et0: 5.5,
        condition: 'sunny',
        conditionAr: 'مشمس',
        updatedAt: DateTime(2026, 3, 15),
      );

      final json = weather.toJson();
      expect(json['field_id'], 'f1');
      expect(json['temperature'], 25.0);
      expect(json['et0'], 5.5);
    });

    test('copyWith creates modified copy', () {
      final original = WeatherSummary(
        fieldId: 'f1', temperature: 25, minTemp: 18, maxTemp: 32,
        precipitation: 0, humidity: 40, et0: 5.5,
        condition: 'sunny', conditionAr: 'مشمس',
        updatedAt: DateTime(2026, 3, 15),
      );

      final modified = original.copyWith(temperature: 30.0, humidity: 35.0);
      expect(modified.temperature, 30.0);
      expect(modified.humidity, 35.0);
      expect(modified.fieldId, 'f1');
    });
  });

  group('WeatherAlertSummary', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'id': 'wa-1',
        'type': 'frost',
        'severity': 'critical',
        'message': 'Frost warning tonight',
        'message_ar': 'تحذير صقيع الليلة',
        'starts_at': '2026-03-15T22:00:00.000',
        'ends_at': '2026-03-16T08:00:00.000',
      };

      final alert = WeatherAlertSummary.fromJson(json);
      expect(alert.id, 'wa-1');
      expect(alert.type, WeatherAlertType.frost);
      expect(alert.severity, 'critical');
      expect(alert.message, 'Frost warning tonight');
      expect(alert.messageAr, 'تحذير صقيع الليلة');
      expect(alert.endsAt, isNotNull);

      final exported = alert.toJson();
      expect(exported['type'], 'frost');
      expect(exported['severity'], 'critical');
    });

    test('handles missing endsAt', () {
      final json = {
        'id': 'wa-2',
        'type': 'heat',
        'severity': 'warning',
        'message': 'Heat wave',
        'message_ar': 'موجة حر',
        'starts_at': '2026-07-01T00:00:00.000',
      };

      final alert = WeatherAlertSummary.fromJson(json);
      expect(alert.endsAt, isNull);
    });

    test('copyWith creates modified copy', () {
      final original = WeatherAlertSummary(
        id: 'wa-3', type: WeatherAlertType.drought, severity: 'warning',
        message: 'Drought', messageAr: 'جفاف',
        startsAt: DateTime(2026, 7, 1),
      );

      final modified = original.copyWith(severity: 'critical');
      expect(modified.severity, 'critical');
      expect(modified.type, WeatherAlertType.drought);
    });
  });
}
