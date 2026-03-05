/// Weather Alerts Tests - اختبارات تنبيهات الطقس
///
/// Comprehensive tests for WeatherAlert entity, AlertSeverity, and WeatherSeverity
/// covering alert parsing, severity colors, and Arabic translations.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/weather/domain/entities/weather_entities.dart';
import 'package:sahool_field_app/features/weather/domain/value_objects/alert_severity.dart';
import 'package:sahool_field_app/features/weather/domain/value_objects/weather_severity.dart';
import 'package:sahool_field_app/features/weather/domain/value_objects/weather_color.dart';

import 'weather_fixtures.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // WeatherAlert Entity Tests - اختبارات كيان تنبيه الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  group('WeatherAlert Entity', () {
    group('fromJson - التحليل من JSON', () {
      test('should parse all fields correctly', () {
        // Arrange
        final json = WeatherFixtures.weatherAlertsJson.first;

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.id, equals('alert-001'));
        expect(alert.type, equals('heat'));
        expect(alert.severity, equals('warning'));
        expect(alert.title, equals('Heat Wave Warning'));
        expect(alert.titleAr, equals('تحذير من موجة حر'));
        expect(alert.description, isNotEmpty);
      });

      test('should parse Arabic title correctly', () {
        // Arrange
        final json = {
          'id': 'test-alert',
          'type': 'rain',
          'severity': 'warning',
          'title': 'Heavy Rain Warning',
          'title_ar': 'تحذير من أمطار غزيرة',
          'description': 'Heavy rainfall expected',
          'start_time': '2026-01-23T10:00:00Z',
          'end_time': '2026-01-24T10:00:00Z',
        };

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.titleAr, equals('تحذير من أمطار غزيرة'));
      });

      test('should fallback to English title when Arabic missing', () {
        // Arrange
        final json = {
          'id': 'test-alert',
          'type': 'wind',
          'severity': 'watch',
          'title': 'Wind Advisory',
          'description': 'Strong winds expected',
          'start_time': '2026-01-23T10:00:00Z',
          'end_time': '2026-01-24T10:00:00Z',
        };

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.titleAr, equals('Wind Advisory'));
      });

      test('should parse start and end times correctly', () {
        // Arrange
        final json = WeatherFixtures.weatherAlertsJson.first;

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.startTime.year, equals(2026));
        expect(alert.startTime.month, equals(1));
        expect(alert.endTime.isAfter(alert.startTime), isTrue);
      });
    });

    group('alertSeverity - شدة التنبيه', () {
      test('should return warning severity', () {
        // Arrange
        final alert = WeatherAlert(
          id: 'test',
          type: 'heat',
          severity: 'warning',
          title: 'Heat Warning',
          titleAr: 'تحذير من الحرارة',
          description: 'High temperature',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 6)),
        );

        // Act & Assert
        expect(alert.alertSeverity, equals(AlertSeverity.warning));
      });

      test('should return watch severity', () {
        // Arrange
        final alert = WeatherAlert(
          id: 'test',
          type: 'wind',
          severity: 'watch',
          title: 'Wind Watch',
          titleAr: 'مراقبة الرياح',
          description: 'Strong winds',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 6)),
        );

        // Act & Assert
        expect(alert.alertSeverity, equals(AlertSeverity.watch));
      });

      test('should return advisory severity', () {
        // Arrange
        final alert = WeatherAlert(
          id: 'test',
          type: 'frost',
          severity: 'advisory',
          title: 'Frost Advisory',
          titleAr: 'إرشاد بشأن الصقيع',
          description: 'Freezing temperatures',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 6)),
        );

        // Act & Assert
        expect(alert.alertSeverity, equals(AlertSeverity.advisory));
      });

      test('should return normal for unknown severity', () {
        // Arrange
        final alert = WeatherAlert(
          id: 'test',
          type: 'info',
          severity: 'unknown',
          title: 'Info',
          titleAr: 'معلومات',
          description: 'Information',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 6)),
        );

        // Act & Assert
        expect(alert.alertSeverity, equals(AlertSeverity.normal));
      });
    });

    group('severityColor - لون الشدة', () {
      test('warning should be red', () {
        // Arrange
        final alert = WeatherAlert(
          id: 'test',
          type: 'heat',
          severity: 'warning',
          title: 'Warning',
          titleAr: 'تحذير',
          description: 'Description',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 6)),
        );

        // Act & Assert
        expect(alert.severityColor, equals(WeatherColor.red));
      });

      test('watch should be orange', () {
        // Arrange
        final alert = WeatherAlert(
          id: 'test',
          type: 'wind',
          severity: 'watch',
          title: 'Watch',
          titleAr: 'مراقبة',
          description: 'Description',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 6)),
        );

        // Act & Assert
        expect(alert.severityColor, equals(WeatherColor.orange));
      });

      test('advisory should be blue', () {
        // Arrange
        final alert = WeatherAlert(
          id: 'test',
          type: 'frost',
          severity: 'advisory',
          title: 'Advisory',
          titleAr: 'إرشادي',
          description: 'Description',
          startTime: DateTime.now(),
          endTime: DateTime.now().add(const Duration(hours: 6)),
        );

        // Act & Assert
        expect(alert.severityColor, equals(WeatherColor.blue));
      });
    });

    group('Alert Types - أنواع التنبيهات', () {
      test('should handle heat wave alert', () {
        // Arrange
        final json = WeatherFixtures.generateAlert(
          severity: 'warning',
          type: 'heat',
          isActive: true,
        );

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.type, equals('heat'));
        expect(alert.severity, equals('warning'));
      });

      test('should handle dust storm alert', () {
        // Arrange
        final json = WeatherFixtures.activeAlertJson;

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.type, equals('dust'));
        expect(alert.titleAr, contains('عاصفة رملية'));
      });

      test('should handle frost alert', () {
        // Arrange
        final json = WeatherFixtures.expiredAlertJson;

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.type, equals('frost'));
        expect(alert.titleAr, contains('الصقيع'));
      });

      test('should handle rain alert', () {
        // Arrange
        final json = (WeatherFixtures.rainyWeatherJson['alerts'] as List)[0] as Map<String, dynamic>;

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.type, equals('rain'));
        expect(alert.titleAr, contains('أمطار'));
      });

      test('should handle thunderstorm alert', () {
        // Arrange
        final json = (WeatherFixtures.thunderstormWeatherJson['alerts'] as List)[0] as Map<String, dynamic>;

        // Act
        final alert = WeatherAlert.fromJson(json);

        // Assert
        expect(alert.type, equals('thunderstorm'));
        expect(alert.titleAr, contains('عاصفة رعدية'));
      });
    });

    group('Active/Expired Alerts - التنبيهات النشطة/المنتهية', () {
      test('should identify active alert', () {
        // Arrange
        final now = DateTime.now();
        final alert = WeatherAlert(
          id: 'active',
          type: 'heat',
          severity: 'warning',
          title: 'Active Alert',
          titleAr: 'تنبيه نشط',
          description: 'Description',
          startTime: now.subtract(const Duration(hours: 1)),
          endTime: now.add(const Duration(hours: 6)),
        );

        // Act
        final isActive = alert.endTime.isAfter(DateTime.now());

        // Assert
        expect(isActive, isTrue);
      });

      test('should identify expired alert', () {
        // Arrange
        final now = DateTime.now();
        final alert = WeatherAlert(
          id: 'expired',
          type: 'frost',
          severity: 'advisory',
          title: 'Expired Alert',
          titleAr: 'تنبيه منتهي',
          description: 'Description',
          startTime: now.subtract(const Duration(days: 2)),
          endTime: now.subtract(const Duration(days: 1)),
        );

        // Act
        final isActive = alert.endTime.isAfter(DateTime.now());

        // Assert
        expect(isActive, isFalse);
      });

      test('should parse active alert from fixture', () {
        // Arrange
        final json = WeatherFixtures.activeAlertJson;

        // Act
        final alert = WeatherAlert.fromJson(json);
        final isActive = alert.endTime.isAfter(DateTime.now());

        // Assert
        expect(isActive, isTrue);
      });

      test('should parse expired alert from fixture', () {
        // Arrange
        final json = WeatherFixtures.expiredAlertJson;

        // Act
        final alert = WeatherAlert.fromJson(json);
        final isActive = alert.endTime.isAfter(DateTime.now());

        // Assert
        expect(isActive, isFalse);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AlertSeverity Tests - اختبارات شدة التنبيه
  // ═══════════════════════════════════════════════════════════════════════════

  group('AlertSeverity', () {
    group('values - القيم', () {
      test('should have all severity levels', () {
        expect(AlertSeverity.values, hasLength(4));
        expect(AlertSeverity.values, contains(AlertSeverity.warning));
        expect(AlertSeverity.values, contains(AlertSeverity.watch));
        expect(AlertSeverity.values, contains(AlertSeverity.advisory));
        expect(AlertSeverity.values, contains(AlertSeverity.normal));
      });
    });

    group('color - الألوان', () {
      test('warning should have red color', () {
        expect(AlertSeverity.warning.color, equals(WeatherColor.red));
      });

      test('watch should have orange color', () {
        expect(AlertSeverity.watch.color, equals(WeatherColor.orange));
      });

      test('advisory should have blue color', () {
        expect(AlertSeverity.advisory.color, equals(WeatherColor.blue));
      });

      test('normal should have grey color', () {
        expect(AlertSeverity.normal.color, equals(WeatherColor.grey));
      });
    });

    group('labelAr - التسمية بالعربية', () {
      test('warning should be تحذير', () {
        expect(AlertSeverity.warning.labelAr, equals('تحذير'));
      });

      test('watch should be مراقبة', () {
        expect(AlertSeverity.watch.labelAr, equals('مراقبة'));
      });

      test('advisory should be إرشادي', () {
        expect(AlertSeverity.advisory.labelAr, equals('إرشادي'));
      });

      test('normal should be عادي', () {
        expect(AlertSeverity.normal.labelAr, equals('عادي'));
      });
    });

    group('fromString - التحويل من نص', () {
      test('should parse warning', () {
        expect(AlertSeverityColor.fromString('warning'), equals(AlertSeverity.warning));
      });

      test('should parse Warning (case insensitive)', () {
        expect(AlertSeverityColor.fromString('WARNING'), equals(AlertSeverity.warning));
      });

      test('should parse watch', () {
        expect(AlertSeverityColor.fromString('watch'), equals(AlertSeverity.watch));
      });

      test('should parse advisory', () {
        expect(AlertSeverityColor.fromString('advisory'), equals(AlertSeverity.advisory));
      });

      test('should default to normal for unknown', () {
        expect(AlertSeverityColor.fromString('unknown'), equals(AlertSeverity.normal));
        expect(AlertSeverityColor.fromString(''), equals(AlertSeverity.normal));
        expect(AlertSeverityColor.fromString('invalid'), equals(AlertSeverity.normal));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // WeatherSeverity Tests - اختبارات شدة الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  group('WeatherSeverity', () {
    group('values - القيم', () {
      test('should have all severity levels', () {
        expect(WeatherSeverity.values, hasLength(3));
        expect(WeatherSeverity.values, contains(WeatherSeverity.favorable));
        expect(WeatherSeverity.values, contains(WeatherSeverity.caution));
        expect(WeatherSeverity.values, contains(WeatherSeverity.unfavorable));
      });
    });

    group('color - الألوان', () {
      test('favorable should have green color', () {
        expect(WeatherSeverity.favorable.color, equals(WeatherColor.green));
      });

      test('caution should have orange color', () {
        expect(WeatherSeverity.caution.color, equals(WeatherColor.orange));
      });

      test('unfavorable should have red color', () {
        expect(WeatherSeverity.unfavorable.color, equals(WeatherColor.red));
      });
    });

    group('labelAr - التسمية بالعربية', () {
      test('favorable should be مناسب', () {
        expect(WeatherSeverity.favorable.labelAr, equals('مناسب'));
      });

      test('caution should be تحذير', () {
        expect(WeatherSeverity.caution.labelAr, equals('تحذير'));
      });

      test('unfavorable should be غير مناسب', () {
        expect(WeatherSeverity.unfavorable.labelAr, equals('غير مناسب'));
      });
    });

    group('icon - الأيقونات', () {
      test('favorable should have checkmark icon', () {
        expect(WeatherSeverity.favorable.icon, equals('✅'));
      });

      test('caution should have warning icon', () {
        expect(WeatherSeverity.caution.icon, equals('⚠️'));
      });

      test('unfavorable should have stop icon', () {
        expect(WeatherSeverity.unfavorable.icon, equals('🚫'));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // WeatherColor Tests - اختبارات ألوان الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  group('WeatherColor', () {
    group('predefined colors - الألوان المحددة مسبقاً', () {
      test('green should have correct hex value', () {
        expect(WeatherColor.green.value, equals(0xFF2E7D32));
      });

      test('orange should have correct hex value', () {
        expect(WeatherColor.orange.value, equals(0xFFF9A825));
      });

      test('red should have correct hex value', () {
        expect(WeatherColor.red.value, equals(0xFFC62828));
      });

      test('blue should have correct hex value', () {
        expect(WeatherColor.blue.value, equals(0xFF1976D2));
      });

      test('grey should have correct hex value', () {
        expect(WeatherColor.grey.value, equals(0xFF6B7280));
      });

      test('yellow should have correct hex value', () {
        expect(WeatherColor.yellow.value, equals(0xFFFBC02D));
      });
    });

    group('equality - المساواة', () {
      test('same colors should be equal', () {
        const color1 = WeatherColor(0xFF2E7D32);
        const color2 = WeatherColor(0xFF2E7D32);
        expect(color1, equals(color2));
      });

      test('different colors should not be equal', () {
        expect(WeatherColor.green, isNot(equals(WeatherColor.red)));
      });

      test('predefined color should equal same value', () {
        const customGreen = WeatherColor(0xFF2E7D32);
        expect(WeatherColor.green, equals(customGreen));
      });
    });

    group('hashCode - رمز التجزئة', () {
      test('same colors should have same hashCode', () {
        const color1 = WeatherColor(0xFF2E7D32);
        const color2 = WeatherColor(0xFF2E7D32);
        expect(color1.hashCode, equals(color2.hashCode));
      });
    });

    group('toString - التحويل لنص', () {
      test('should format as hex string', () {
        expect(
          WeatherColor.green.toString(),
          equals('WeatherColor(0xFF2E7D32)'),
        );
      });

      test('should pad with zeros', () {
        const color = WeatherColor(0x00FF0000);
        expect(color.toString(), equals('WeatherColor(0x00FF0000)'));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AgriculturalImpact Tests - اختبارات التأثيرات الزراعية
  // ═══════════════════════════════════════════════════════════════════════════

  group('AgriculturalImpact', () {
    group('fromJson - التحليل من JSON', () {
      test('should parse all fields correctly', () {
        // Arrange
        final json = WeatherFixtures.agriculturalImpactsJson.first;

        // Act
        final impact = AgriculturalImpact.fromJson(json);

        // Assert
        expect(impact.category, equals('irrigation'));
        expect(impact.recommendation, isNotEmpty);
        expect(impact.recommendationAr, isNotEmpty);
        expect(impact.status, equals('caution'));
        expect(impact.reasons, isNotEmpty);
      });

      test('should parse Arabic recommendation', () {
        // Arrange
        final json = WeatherFixtures.agriculturalImpactsJson.first;

        // Act
        final impact = AgriculturalImpact.fromJson(json);

        // Assert
        expect(
          impact.recommendationAr,
          equals('تقليل الري بنسبة 20% بسبب هطول الأمطار المتوقعة'),
        );
      });

      test('should parse reasons list', () {
        // Arrange
        final json = WeatherFixtures.agriculturalImpactsJson.first;

        // Act
        final impact = AgriculturalImpact.fromJson(json);

        // Assert
        expect(impact.reasons, hasLength(2));
        expect(impact.reasons, contains('Expected rainfall 15mm'));
      });

      test('should handle empty reasons', () {
        // Arrange
        final json = {
          'category': 'irrigation',
          'recommendation': 'Test',
          'recommendation_ar': 'اختبار',
          'status': 'favorable',
        };

        // Act
        final impact = AgriculturalImpact.fromJson(json);

        // Assert
        expect(impact.reasons, isEmpty);
      });
    });

    group('weatherSeverity - شدة الطقس', () {
      test('favorable status should return favorable severity', () {
        // Arrange
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[1], // spraying - favorable
        );

        // Assert
        expect(impact.weatherSeverity, equals(WeatherSeverity.favorable));
      });

      test('caution status should return caution severity', () {
        // Arrange
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[0], // irrigation - caution
        );

        // Assert
        expect(impact.weatherSeverity, equals(WeatherSeverity.caution));
      });

      test('unfavorable status should return unfavorable severity', () {
        // Arrange
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[2], // harvesting - unfavorable
        );

        // Assert
        expect(impact.weatherSeverity, equals(WeatherSeverity.unfavorable));
      });

      test('unknown status should default to caution', () {
        // Arrange
        final json = {
          'category': 'irrigation',
          'recommendation': 'Test',
          'recommendation_ar': 'اختبار',
          'status': 'unknown_status',
          'reasons': <dynamic>[],
        };
        final impact = AgriculturalImpact.fromJson(json);

        // Assert
        expect(impact.weatherSeverity, equals(WeatherSeverity.caution));
      });
    });

    group('statusColor - لون الحالة', () {
      test('favorable should be green', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[1],
        );
        expect(impact.statusColor, equals(WeatherColor.green));
      });

      test('caution should be orange', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[0],
        );
        expect(impact.statusColor, equals(WeatherColor.orange));
      });

      test('unfavorable should be red', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[2],
        );
        expect(impact.statusColor, equals(WeatherColor.red));
      });
    });

    group('categoryIcon - أيقونة الفئة', () {
      test('irrigation should have water icon', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[0],
        );
        expect(impact.categoryIcon, equals('💧'));
      });

      test('spraying should have plant icon', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[1],
        );
        expect(impact.categoryIcon, equals('🌿'));
      });

      test('harvesting should have wheat icon', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[2],
        );
        expect(impact.categoryIcon, equals('🌾'));
      });

      test('planting should have seedling icon', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[3],
        );
        expect(impact.categoryIcon, equals('🌱'));
      });

      test('unknown category should have thermometer icon', () {
        final json = {
          'category': 'unknown',
          'recommendation': 'Test',
          'recommendation_ar': 'اختبار',
          'status': 'favorable',
          'reasons': <dynamic>[],
        };
        final impact = AgriculturalImpact.fromJson(json);
        expect(impact.categoryIcon, equals('🌡️'));
      });
    });

    group('categoryAr - الفئة بالعربية', () {
      test('irrigation should be الري', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[0],
        );
        expect(impact.categoryAr, equals('الري'));
      });

      test('spraying should be الرش', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[1],
        );
        expect(impact.categoryAr, equals('الرش'));
      });

      test('harvesting should be الحصاد', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[2],
        );
        expect(impact.categoryAr, equals('الحصاد'));
      });

      test('planting should be الزراعة', () {
        final impact = AgriculturalImpact.fromJson(
          WeatherFixtures.agriculturalImpactsJson[3],
        );
        expect(impact.categoryAr, equals('الزراعة'));
      });

      test('unknown category should return original', () {
        final json = {
          'category': 'fertilizing',
          'recommendation': 'Test',
          'recommendation_ar': 'اختبار',
          'status': 'favorable',
          'reasons': <dynamic>[],
        };
        final impact = AgriculturalImpact.fromJson(json);
        expect(impact.categoryAr, equals('fertilizing'));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CurrentWeather Tests - اختبارات الطقس الحالي
  // ═══════════════════════════════════════════════════════════════════════════

  group('CurrentWeather', () {
    group('fromJson - التحليل من JSON', () {
      test('should parse temperature in Celsius', () {
        // Arrange
        final json = WeatherFixtures.currentWeatherJson['current'] as Map<String, dynamic>;

        // Act
        final weather = CurrentWeather.fromJson(json);

        // Assert
        expect(weather.temperature, equals(28.5));
      });

      test('should parse wind speed in km/h', () {
        // Arrange
        final json = WeatherFixtures.currentWeatherJson['current'] as Map<String, dynamic>;

        // Act
        final weather = CurrentWeather.fromJson(json);

        // Assert
        expect(weather.windSpeed, equals(12.5));
      });

      test('should parse Arabic condition', () {
        // Arrange
        final json = WeatherFixtures.currentWeatherJson['current'] as Map<String, dynamic>;

        // Act
        final weather = CurrentWeather.fromJson(json);

        // Assert
        expect(weather.conditionAr, equals('غائم جزئياً'));
      });

      test('should fallback conditionAr to condition when missing', () {
        // Arrange
        final json = {
          'temperature': 25.0,
          'feels_like': 26.0,
          'humidity': 50,
          'wind_speed': 10.0,
          'wind_direction': 'N',
          'condition': 'Clear',
          'icon': '☀️',
          'timestamp': '2026-01-23T10:00:00Z',
        };

        // Act
        final weather = CurrentWeather.fromJson(json);

        // Assert
        expect(weather.conditionAr, equals('Clear'));
      });

      test('should parse humidity as percentage', () {
        // Arrange
        final json = WeatherFixtures.currentWeatherJson['current'] as Map<String, dynamic>;

        // Act
        final weather = CurrentWeather.fromJson(json);

        // Assert
        expect(weather.humidity, equals(65));
      });
    });

    group('temperatureDisplay - عرض درجة الحرارة', () {
      test('should round and format with degree symbol', () {
        // Arrange
        final json = WeatherFixtures.currentWeatherJson['current'] as Map<String, dynamic>;
        final weather = CurrentWeather.fromJson(json);

        // Assert - 28.5 rounds to 29
        expect(weather.temperatureDisplay, equals('29°'));
      });

      test('should handle negative temperatures', () {
        // Arrange
        final json = {
          'temperature': -5.4,
          'feels_like': -7.0,
          'humidity': 80,
          'wind_speed': 15.0,
          'wind_direction': 'N',
          'condition': 'Cold',
          'condition_ar': 'بارد',
          'icon': '❄️',
          'timestamp': '2026-01-23T06:00:00Z',
        };
        final weather = CurrentWeather.fromJson(json);

        // Assert - -5.4 rounds to -5
        expect(weather.temperatureDisplay, equals('-5°'));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DailyForecast Tests - اختبارات التوقعات اليومية
  // ═══════════════════════════════════════════════════════════════════════════

  group('DailyForecast', () {
    group('dayName - اسم اليوم', () {
      test('should return Arabic day name', () {
        // Test various days - the exact day depends on the date
        final forecast = DailyForecast.fromJson(
          WeatherFixtures.dailyForecastsJson.first,
        );

        // dayName should return one of the Arabic day names
        final arabicDays = [
          'الأحد',
          'الإثنين',
          'الثلاثاء',
          'الأربعاء',
          'الخميس',
          'الجمعة',
          'السبت',
        ];
        expect(arabicDays, contains(forecast.dayName));
      });

      test('should handle all weekdays', () {
        // Create forecasts for 7 days to cover all weekdays
        final forecasts = WeatherFixtures.generateForecastDays(7);
        final dayNames = forecasts
            .map((json) => DailyForecast.fromJson(json).dayName)
            .toSet();

        // Should have 7 different day names
        expect(dayNames.length, equals(7));

        // All should be Arabic day names
        final arabicDays = [
          'الأحد',
          'الإثنين',
          'الثلاثاء',
          'الأربعاء',
          'الخميس',
          'الجمعة',
          'السبت',
        ];
        for (final name in dayNames) {
          expect(arabicDays, contains(name));
        }
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // HourlyForecast Tests - اختبارات التوقعات الساعية
  // ═══════════════════════════════════════════════════════════════════════════

  group('HourlyForecast', () {
    group('hourDisplay - عرض الساعة', () {
      test('should format as HH:00', () {
        // Arrange
        final json = WeatherFixtures.hourlyForecastsJson.first;

        // Act
        final forecast = HourlyForecast.fromJson(json);

        // Assert
        expect(forecast.hourDisplay, equals('11:00'));
      });

      test('should handle midnight', () {
        // Arrange
        final json = {
          'time': '2026-01-24T00:00:00Z',
          'temperature': 18.0,
          'condition': 'Clear',
          'icon': '🌙',
          'precipitation_chance': 0,
          'humidity': 60,
        };

        // Act
        final forecast = HourlyForecast.fromJson(json);

        // Assert
        expect(forecast.hourDisplay, equals('0:00'));
      });
    });
  });
}
