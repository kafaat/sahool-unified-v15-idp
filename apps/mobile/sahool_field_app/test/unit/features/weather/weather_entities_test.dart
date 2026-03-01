import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/weather/domain/entities/weather_entities.dart';
import 'package:sahool_field_app/features/weather/domain/value_objects/alert_severity.dart';
import 'package:sahool_field_app/features/weather/domain/value_objects/weather_severity.dart';
import 'package:sahool_field_app/features/weather/domain/value_objects/weather_color.dart';

void main() {
  // =========================================================================
  // CurrentWeather
  // =========================================================================

  group('CurrentWeather', () {
    test('should create instance with required parameters', () {
      // Arrange & Act
      final weather = CurrentWeather(
        temperature: 28.5,
        feelsLike: 30.0,
        humidity: 65,
        windSpeed: 12.0,
        windDirection: 'NW',
        condition: 'Partly Cloudy',
        conditionAr: '\u063a\u0627\u0626\u0645 \u062c\u0632\u0626\u064a\u0627',
        icon: '\u26c5',
        precipitation: 0.5,
        uvIndex: 7.0,
        timestamp: DateTime(2026, 2, 27, 10, 30),
      );

      // Assert
      expect(weather.temperature, 28.5);
      expect(weather.feelsLike, 30.0);
      expect(weather.humidity, 65);
      expect(weather.windSpeed, 12.0);
      expect(weather.windDirection, 'NW');
      expect(weather.condition, 'Partly Cloudy');
      expect(weather.precipitation, 0.5);
      expect(weather.uvIndex, 7.0);
    });

    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final weather = CurrentWeather(
        temperature: 28.5,
        feelsLike: 30.0,
        humidity: 65,
        windSpeed: 12.0,
        windDirection: 'NW',
        condition: 'Sunny',
        conditionAr: '\u0645\u0634\u0645\u0633',
        icon: '\u2600\ufe0f',
        precipitation: 0.0,
        uvIndex: 8.5,
        timestamp: DateTime(2026, 2, 27, 10, 30),
      );

      // Act
      final json = weather.toJson();
      final restored = CurrentWeather.fromJson(json);

      // Assert
      expect(restored.temperature, weather.temperature);
      expect(restored.feelsLike, weather.feelsLike);
      expect(restored.humidity, weather.humidity);
      expect(restored.windSpeed, weather.windSpeed);
      expect(restored.windDirection, weather.windDirection);
      expect(restored.condition, weather.condition);
      expect(restored.conditionAr, weather.conditionAr);
      expect(restored.icon, weather.icon);
      expect(restored.precipitation, weather.precipitation);
      expect(restored.uvIndex, weather.uvIndex);
      expect(restored.timestamp, weather.timestamp);
    });

    test('fromJson should handle null optional fields', () {
      // Arrange
      final json = {
        'temperature': 25,
        'feels_like': 27,
        'humidity': 50,
        'wind_speed': 10,
        'wind_direction': 'N',
        'condition': 'Clear',
        'timestamp': '2026-02-27T10:00:00.000',
      };

      // Act
      final weather = CurrentWeather.fromJson(json);

      // Assert
      expect(weather.precipitation, isNull);
      expect(weather.uvIndex, isNull);
      expect(weather.conditionAr, 'Clear'); // fallback to condition
      expect(weather.icon, '\u2600\ufe0f'); // default icon
    });

    test('temperatureDisplay should round to nearest integer', () {
      // Arrange
      final weather = CurrentWeather(
        temperature: 28.7,
        feelsLike: 30.0,
        humidity: 65,
        windSpeed: 12.0,
        windDirection: 'NW',
        condition: 'Sunny',
        conditionAr: '\u0645\u0634\u0645\u0633',
        icon: '\u2600\ufe0f',
        timestamp: DateTime(2026, 2, 27),
      );

      // Act & Assert
      expect(weather.temperatureDisplay, '29\u00b0');
    });

    test('copyWith should override specified fields only', () {
      // Arrange
      final original = CurrentWeather(
        temperature: 28.0,
        feelsLike: 30.0,
        humidity: 65,
        windSpeed: 12.0,
        windDirection: 'NW',
        condition: 'Sunny',
        conditionAr: '\u0645\u0634\u0645\u0633',
        icon: '\u2600\ufe0f',
        timestamp: DateTime(2026, 2, 27),
      );

      // Act
      final modified = original.copyWith(temperature: 35.0, humidity: 80);

      // Assert
      expect(modified.temperature, 35.0);
      expect(modified.humidity, 80);
      expect(modified.windSpeed, 12.0); // unchanged
      expect(modified.condition, 'Sunny'); // unchanged
    });
  });

  // =========================================================================
  // DailyForecast
  // =========================================================================

  group('DailyForecast', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final forecast = DailyForecast(
        date: DateTime(2026, 2, 28),
        tempMin: 15.0,
        tempMax: 32.0,
        condition: 'Cloudy',
        conditionAr: '\u063a\u0627\u0626\u0645',
        icon: '\u2601\ufe0f',
        precipitationChance: 30,
        precipitationAmount: 2.5,
        humidity: 55,
        windSpeed: 18.0,
      );

      // Act
      final json = forecast.toJson();
      final restored = DailyForecast.fromJson(json);

      // Assert
      expect(restored.date, forecast.date);
      expect(restored.tempMin, forecast.tempMin);
      expect(restored.tempMax, forecast.tempMax);
      expect(restored.condition, forecast.condition);
      expect(restored.conditionAr, forecast.conditionAr);
      expect(restored.precipitationChance, forecast.precipitationChance);
      expect(restored.precipitationAmount, forecast.precipitationAmount);
      expect(restored.humidity, forecast.humidity);
      expect(restored.windSpeed, forecast.windSpeed);
    });

    test('fromJson should handle missing optional fields', () {
      // Arrange
      final json = {
        'date': '2026-02-28T00:00:00.000',
        'temp_min': 15,
        'temp_max': 32,
        'condition': 'Clear',
      };

      // Act
      final forecast = DailyForecast.fromJson(json);

      // Assert
      expect(forecast.precipitationChance, 0);
      expect(forecast.precipitationAmount, isNull);
      expect(forecast.humidity, 0);
      expect(forecast.windSpeed, 0.0);
    });

    test('dayName should return Arabic day name', () {
      // Arrange - 2026-02-27 is a Friday
      final forecast = DailyForecast(
        date: DateTime(2026, 2, 27),
        tempMin: 15.0,
        tempMax: 30.0,
        condition: 'Sunny',
        conditionAr: '\u0645\u0634\u0645\u0633',
        icon: '\u2600\ufe0f',
        precipitationChance: 0,
        humidity: 50,
        windSpeed: 10.0,
      );

      // Act
      final name = forecast.dayName;

      // Assert - should be a valid Arabic day name
      expect(
        [
          '\u0627\u0644\u0623\u062d\u062f',
          '\u0627\u0644\u0625\u062b\u0646\u064a\u0646',
          '\u0627\u0644\u062b\u0644\u0627\u062b\u0627\u0621',
          '\u0627\u0644\u0623\u0631\u0628\u0639\u0627\u0621',
          '\u0627\u0644\u062e\u0645\u064a\u0633',
          '\u0627\u0644\u062c\u0645\u0639\u0629',
          '\u0627\u0644\u0633\u0628\u062a',
        ],
        contains(name),
      );
    });

    test('should handle list of DailyForecast from JSON array', () {
      // Arrange
      final jsonList = List.generate(
        7,
        (i) => {
          'date': DateTime(2026, 2, 27)
              .add(Duration(days: i))
              .toIso8601String(),
          'temp_min': 15.0 + i,
          'temp_max': 30.0 + i,
          'condition': 'Sunny',
          'condition_ar': '\u0645\u0634\u0645\u0633',
          'icon': '\u2600\ufe0f',
          'precipitation_chance': 5 * i,
          'humidity': 50,
          'wind_speed': 10.0,
        },
      );

      // Act
      final forecasts =
          jsonList.map((j) => DailyForecast.fromJson(j)).toList();

      // Assert
      expect(forecasts.length, 7);
      expect(forecasts.first.tempMin, 15.0);
      expect(forecasts.last.tempMin, 21.0);
    });
  });

  // =========================================================================
  // HourlyForecast
  // =========================================================================

  group('HourlyForecast', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final hourly = HourlyForecast(
        time: DateTime(2026, 2, 27, 14, 0),
        temperature: 31.0,
        condition: 'Sunny',
        icon: '\u2600\ufe0f',
        precipitationChance: 5,
        humidity: 40,
      );

      // Act
      final json = hourly.toJson();
      final restored = HourlyForecast.fromJson(json);

      // Assert
      expect(restored.time, hourly.time);
      expect(restored.temperature, hourly.temperature);
      expect(restored.condition, hourly.condition);
      expect(restored.precipitationChance, hourly.precipitationChance);
      expect(restored.humidity, hourly.humidity);
    });

    test('hourDisplay should format as HH:00', () {
      // Arrange
      final hourly = HourlyForecast(
        time: DateTime(2026, 2, 27, 14, 0),
        temperature: 31.0,
        condition: 'Sunny',
        icon: '\u2600\ufe0f',
        precipitationChance: 0,
        humidity: 40,
      );

      // Act & Assert
      expect(hourly.hourDisplay, '14:00');
    });

    test('copyWith should override specified fields only', () {
      // Arrange
      final original = HourlyForecast(
        time: DateTime(2026, 2, 27, 10, 0),
        temperature: 25.0,
        condition: 'Cloudy',
        icon: '\u2601\ufe0f',
        precipitationChance: 20,
        humidity: 60,
      );

      // Act
      final modified = original.copyWith(temperature: 30.0);

      // Assert
      expect(modified.temperature, 30.0);
      expect(modified.condition, 'Cloudy'); // unchanged
      expect(modified.humidity, 60); // unchanged
    });
  });

  // =========================================================================
  // WeatherAlert
  // =========================================================================

  group('WeatherAlert', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final alert = WeatherAlert(
        id: 'alert_001',
        type: 'heat',
        severity: 'warning',
        title: 'Heat Wave Warning',
        titleAr: '\u062a\u062d\u0630\u064a\u0631 \u0645\u0648\u062c\u0629 \u062d\u0631',
        description: 'Extreme heat above 45C expected',
        startTime: DateTime(2026, 2, 27, 6, 0),
        endTime: DateTime(2026, 2, 28, 18, 0),
      );

      // Act
      final json = alert.toJson();
      final restored = WeatherAlert.fromJson(json);

      // Assert
      expect(restored.id, alert.id);
      expect(restored.type, alert.type);
      expect(restored.severity, alert.severity);
      expect(restored.title, alert.title);
      expect(restored.titleAr, alert.titleAr);
      expect(restored.description, alert.description);
      expect(restored.startTime, alert.startTime);
      expect(restored.endTime, alert.endTime);
    });

    test('alertSeverity should map string to AlertSeverity enum', () {
      // Arrange
      final warningAlert = WeatherAlert(
        id: 'a1',
        type: 'heat',
        severity: 'warning',
        title: 'Warning',
        titleAr: '\u062a\u062d\u0630\u064a\u0631',
        description: '',
        startTime: DateTime(2026, 2, 27),
        endTime: DateTime(2026, 2, 28),
      );

      final watchAlert = warningAlert.copyWith(severity: 'watch');
      final advisoryAlert = warningAlert.copyWith(severity: 'advisory');
      final normalAlert = warningAlert.copyWith(severity: 'normal');

      // Act & Assert
      expect(warningAlert.alertSeverity, AlertSeverity.warning);
      expect(watchAlert.alertSeverity, AlertSeverity.watch);
      expect(advisoryAlert.alertSeverity, AlertSeverity.advisory);
      expect(normalAlert.alertSeverity, AlertSeverity.normal);
    });

    test('severityColor should return appropriate WeatherColor', () {
      // Arrange
      final alert = WeatherAlert(
        id: 'a1',
        type: 'heat',
        severity: 'warning',
        title: 'Warning',
        titleAr: '\u062a\u062d\u0630\u064a\u0631',
        description: '',
        startTime: DateTime(2026, 2, 27),
        endTime: DateTime(2026, 2, 28),
      );

      // Act & Assert
      expect(alert.severityColor, WeatherColor.red);
    });

    test('copyWith should create modified copy', () {
      // Arrange
      final original = WeatherAlert(
        id: 'a1',
        type: 'heat',
        severity: 'warning',
        title: 'Heat Wave',
        titleAr: '\u0645\u0648\u062c\u0629 \u062d\u0631',
        description: 'High temperatures',
        startTime: DateTime(2026, 2, 27),
        endTime: DateTime(2026, 2, 28),
      );

      // Act
      final modified = original.copyWith(severity: 'advisory', type: 'wind');

      // Assert
      expect(modified.severity, 'advisory');
      expect(modified.type, 'wind');
      expect(modified.title, 'Heat Wave'); // unchanged
    });
  });

  // =========================================================================
  // AgriculturalImpact
  // =========================================================================

  group('AgriculturalImpact', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      const impact = AgriculturalImpact(
        category: 'irrigation',
        recommendation: 'Optimal conditions for irrigation',
        recommendationAr: '\u0638\u0631\u0648\u0641 \u0645\u062b\u0627\u0644\u064a\u0629 \u0644\u0644\u0631\u064a',
        status: 'favorable',
        reasons: ['Low wind speed', 'No rain expected'],
      );

      // Act
      final json = impact.toJson();
      final restored = AgriculturalImpact.fromJson(json);

      // Assert
      expect(restored.category, impact.category);
      expect(restored.recommendation, impact.recommendation);
      expect(restored.recommendationAr, impact.recommendationAr);
      expect(restored.status, impact.status);
      expect(restored.reasons, impact.reasons);
    });

    test('weatherSeverity should map status string to enum', () {
      // Arrange
      const favorable = AgriculturalImpact(
        category: 'irrigation',
        recommendation: '',
        recommendationAr: '',
        status: 'favorable',
        reasons: [],
      );
      const caution = AgriculturalImpact(
        category: 'spraying',
        recommendation: '',
        recommendationAr: '',
        status: 'caution',
        reasons: [],
      );
      const unfavorable = AgriculturalImpact(
        category: 'harvesting',
        recommendation: '',
        recommendationAr: '',
        status: 'unfavorable',
        reasons: [],
      );
      const unknown = AgriculturalImpact(
        category: 'other',
        recommendation: '',
        recommendationAr: '',
        status: 'unknown_status',
        reasons: [],
      );

      // Act & Assert
      expect(favorable.weatherSeverity, WeatherSeverity.favorable);
      expect(caution.weatherSeverity, WeatherSeverity.caution);
      expect(unfavorable.weatherSeverity, WeatherSeverity.unfavorable);
      expect(unknown.weatherSeverity, WeatherSeverity.caution); // default
    });

    test('statusColor should return correct WeatherColor', () {
      // Arrange
      const favorable = AgriculturalImpact(
        category: 'irrigation',
        recommendation: '',
        recommendationAr: '',
        status: 'favorable',
        reasons: [],
      );

      // Act & Assert
      expect(favorable.statusColor, WeatherColor.green);
    });

    test('categoryIcon should return correct emoji per category', () {
      const irrigation = AgriculturalImpact(
        category: 'irrigation',
        recommendation: '',
        recommendationAr: '',
        status: 'favorable',
        reasons: [],
      );
      const spraying = AgriculturalImpact(
        category: 'spraying',
        recommendation: '',
        recommendationAr: '',
        status: 'favorable',
        reasons: [],
      );
      const harvesting = AgriculturalImpact(
        category: 'harvesting',
        recommendation: '',
        recommendationAr: '',
        status: 'favorable',
        reasons: [],
      );
      const planting = AgriculturalImpact(
        category: 'planting',
        recommendation: '',
        recommendationAr: '',
        status: 'favorable',
        reasons: [],
      );

      expect(irrigation.categoryIcon, '\ud83d\udca7');
      expect(spraying.categoryIcon, '\ud83c\udf3f');
      expect(harvesting.categoryIcon, '\ud83c\udf3e');
      expect(planting.categoryIcon, '\ud83c\udf31');
    });

    test('categoryAr should return Arabic category name', () {
      const irrigation = AgriculturalImpact(
        category: 'irrigation',
        recommendation: '',
        recommendationAr: '',
        status: 'favorable',
        reasons: [],
      );

      expect(irrigation.categoryAr, '\u0627\u0644\u0631\u064a');
    });

    test('fromJson should handle missing reasons list', () {
      // Arrange
      final json = {
        'category': 'irrigation',
        'recommendation': 'Water the field',
        'status': 'favorable',
      };

      // Act
      final impact = AgriculturalImpact.fromJson(json);

      // Assert
      expect(impact.reasons, isEmpty);
      expect(impact.recommendationAr, 'Water the field'); // fallback
    });
  });

  // =========================================================================
  // WeatherData (composite)
  // =========================================================================

  group('WeatherData', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final data = WeatherData(
        current: CurrentWeather(
          temperature: 28.0,
          feelsLike: 30.0,
          humidity: 60,
          windSpeed: 10.0,
          windDirection: 'NW',
          condition: 'Sunny',
          conditionAr: '\u0645\u0634\u0645\u0633',
          icon: '\u2600\ufe0f',
          precipitation: 0.0,
          uvIndex: 7.0,
          timestamp: DateTime(2026, 2, 27, 10, 0),
        ),
        hourly: [
          HourlyForecast(
            time: DateTime(2026, 2, 27, 11, 0),
            temperature: 29.0,
            condition: 'Sunny',
            icon: '\u2600\ufe0f',
            precipitationChance: 0,
            humidity: 55,
          ),
        ],
        daily: [
          DailyForecast(
            date: DateTime(2026, 2, 27),
            tempMin: 18.0,
            tempMax: 32.0,
            condition: 'Sunny',
            conditionAr: '\u0645\u0634\u0645\u0633',
            icon: '\u2600\ufe0f',
            precipitationChance: 5,
            humidity: 50,
            windSpeed: 10.0,
          ),
        ],
        alerts: [
          WeatherAlert(
            id: 'a1',
            type: 'heat',
            severity: 'warning',
            title: 'Heat Warning',
            titleAr: '\u062a\u062d\u0630\u064a\u0631',
            description: 'Extreme heat',
            startTime: DateTime(2026, 2, 27),
            endTime: DateTime(2026, 2, 28),
          ),
        ],
        impacts: [
          const AgriculturalImpact(
            category: 'irrigation',
            recommendation: 'Good',
            recommendationAr: '\u062c\u064a\u062f',
            status: 'favorable',
            reasons: [],
          ),
        ],
      );

      // Act
      final json = data.toJson();
      final restored = WeatherData.fromJson(json);

      // Assert
      expect(restored.current.temperature, 28.0);
      expect(restored.hourly.length, 1);
      expect(restored.daily.length, 1);
      expect(restored.alerts.length, 1);
      expect(restored.impacts.length, 1);
    });

    test('fromJson should handle missing list fields', () {
      // Arrange
      final json = {
        'current': {
          'temperature': 25,
          'feels_like': 27,
          'humidity': 50,
          'wind_speed': 8,
          'wind_direction': 'E',
          'condition': 'Clear',
          'timestamp': '2026-02-27T10:00:00.000',
        },
      };

      // Act
      final data = WeatherData.fromJson(json);

      // Assert
      expect(data.hourly, isEmpty);
      expect(data.daily, isEmpty);
      expect(data.alerts, isEmpty);
      expect(data.impacts, isEmpty);
    });

    test('copyWith should override only specified fields', () {
      // Arrange
      final original = WeatherData(
        current: CurrentWeather(
          temperature: 28.0,
          feelsLike: 30.0,
          humidity: 60,
          windSpeed: 10.0,
          windDirection: 'NW',
          condition: 'Sunny',
          conditionAr: '\u0645\u0634\u0645\u0633',
          icon: '\u2600\ufe0f',
          timestamp: DateTime(2026, 2, 27),
        ),
        hourly: [],
        daily: [],
        alerts: [],
        impacts: [],
      );

      // Act
      final modified = original.copyWith(
        alerts: [
          WeatherAlert(
            id: 'new_alert',
            type: 'wind',
            severity: 'advisory',
            title: 'Wind',
            titleAr: '\u0631\u064a\u0627\u062d',
            description: 'Strong wind',
            startTime: DateTime(2026, 2, 27),
            endTime: DateTime(2026, 2, 28),
          ),
        ],
      );

      // Assert
      expect(modified.alerts.length, 1);
      expect(modified.current.temperature, 28.0); // unchanged
      expect(modified.hourly, isEmpty); // unchanged
    });
  });
}
