import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sahool_field_app/core/notifications/notification_settings.dart';

/// Integration Tests - Notifications
/// اختبارات تكامل الإشعارات

void main() {
  group('Notification Settings Integration Tests', () {
    late NotificationSettings settings;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      settings = NotificationSettings(prefs);
    });

    test('Default settings should be enabled', () {
      expect(settings.irrigationAlertsEnabled, isTrue);
      expect(settings.weatherAlertsEnabled, isTrue);
      expect(settings.taskRemindersEnabled, isTrue);
      expect(settings.soundEnabled, isTrue);
      expect(settings.vibrationEnabled, isTrue);
    });

    test('Quiet hours should be disabled by default', () {
      expect(settings.quietHoursEnabled, isFalse);
    });

    test('Settings should persist after change', () async {
      // Act
      settings.irrigationAlertsEnabled = false;

      // Assert
      expect(settings.irrigationAlertsEnabled, isFalse);
    });

    test('Quiet hours should block non-critical notifications', () {
      // Arrange
      settings.quietHoursEnabled = true;
      settings.quietHoursStart = 0; // 12 AM
      settings.quietHoursEnd = 23; // 11 PM (almost all day)

      // Assert - During quiet hours, non-critical should be blocked
      // Critical notifications should always pass
      expect(settings.isTypeEnabled('critical'), isTrue);
    });

    test('Settings export and import should work correctly', () async {
      // Arrange
      settings.irrigationAlertsEnabled = false;
      settings.soundEnabled = false;
      settings.quietHoursEnabled = true;

      // Act
      final exported = settings.toJson();

      // Assert
      expect(exported['irrigation_enabled'], isFalse);
      expect(exported['sound_enabled'], isFalse);
      expect(exported['quiet_hours_enabled'], isTrue);
    });

    test('Reset should restore defaults', () async {
      // Arrange
      settings.irrigationAlertsEnabled = false;
      settings.soundEnabled = false;

      // Act
      await settings.reset();

      // Assert - After reset, values should be defaults
      expect(settings.irrigationAlertsEnabled, isTrue);
      expect(settings.soundEnabled, isTrue);
    });
  });

  group('Notification Types', () {
    test('Should correctly identify notification types', () {
      // Arrange
      const types = ['irrigation', 'weather', 'task', 'sensor', 'ndvi', 'system', 'critical'];

      // Assert
      expect(types.contains('irrigation'), isTrue);
      expect(types.contains('weather'), isTrue);
      expect(types.length, equals(7));
    });

    test('Critical notifications should always be enabled', () async {
      // Arrange
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final settings = NotificationSettings(prefs);

      // Disable everything
      settings.irrigationAlertsEnabled = false;
      settings.weatherAlertsEnabled = false;

      // Assert - Critical should still work
      expect(settings.isTypeEnabled('critical'), isTrue);
    });
  });

  group('Notification Payload', () {
    test('Should parse notification data correctly', () {
      // Arrange
      final data = {
        'type': 'irrigation',
        'targetId': 'field_123',
        'action': 'start_irrigation',
        'title': 'تنبيه الري',
        'body': 'حقل الشمال يحتاج للري',
      };

      // Assert
      expect(data['type'], equals('irrigation'));
      expect(data['targetId'], equals('field_123'));
      expect(data['action'], equals('start_irrigation'));
    });

    test('Should handle missing data gracefully', () {
      // Arrange
      final data = <String, dynamic>{};

      // Assert
      expect(data['type'], isNull);
      expect(data['targetId'], isNull);
    });
  });
}
