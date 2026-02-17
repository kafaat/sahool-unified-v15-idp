import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sahool_field_app/core/notifications/notification_settings.dart';

void main() {
  late NotificationSettings settings;

  setUp(() async {
    // Set up SharedPreferences with test values
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    settings = NotificationSettings(prefs);
  });

  group('Default Values', () {
    test('should have all notification types enabled by default', () {
      expect(settings.irrigationAlertsEnabled, true);
      expect(settings.weatherAlertsEnabled, true);
      expect(settings.taskRemindersEnabled, true);
      expect(settings.sensorAlertsEnabled, true);
      expect(settings.ndviAlertsEnabled, true);
      expect(settings.systemNotificationsEnabled, true);
    });

    test('should have sound and vibration enabled by default', () {
      expect(settings.soundEnabled, true);
      expect(settings.vibrationEnabled, true);
    });

    test('should have quiet hours disabled by default', () {
      expect(settings.quietHoursEnabled, false);
    });

    test('should have default quiet hours 22:00-07:00', () {
      expect(settings.quietHoursStart, 22);
      expect(settings.quietHoursEnd, 7);
    });
  });

  group('Setting Values', () {
    test('should toggle irrigation alerts', () {
      settings.irrigationAlertsEnabled = false;
      expect(settings.irrigationAlertsEnabled, false);

      settings.irrigationAlertsEnabled = true;
      expect(settings.irrigationAlertsEnabled, true);
    });

    test('should toggle weather alerts', () {
      settings.weatherAlertsEnabled = false;
      expect(settings.weatherAlertsEnabled, false);
    });

    test('should toggle task reminders', () {
      settings.taskRemindersEnabled = false;
      expect(settings.taskRemindersEnabled, false);
    });

    test('should toggle sensor alerts', () {
      settings.sensorAlertsEnabled = false;
      expect(settings.sensorAlertsEnabled, false);
    });

    test('should toggle NDVI alerts', () {
      settings.ndviAlertsEnabled = false;
      expect(settings.ndviAlertsEnabled, false);
    });

    test('should toggle system notifications', () {
      settings.systemNotificationsEnabled = false;
      expect(settings.systemNotificationsEnabled, false);
    });

    test('should toggle sound', () {
      settings.soundEnabled = false;
      expect(settings.soundEnabled, false);
    });

    test('should toggle vibration', () {
      settings.vibrationEnabled = false;
      expect(settings.vibrationEnabled, false);
    });

    test('should set quiet hours', () {
      settings.quietHoursEnabled = true;
      settings.quietHoursStart = 23;
      settings.quietHoursEnd = 6;

      expect(settings.quietHoursEnabled, true);
      expect(settings.quietHoursStart, 23);
      expect(settings.quietHoursEnd, 6);
    });
  });

  group('isTypeEnabled', () {
    test('should return true for enabled types', () {
      expect(settings.isTypeEnabled('irrigation'), true);
      expect(settings.isTypeEnabled('weather'), true);
      expect(settings.isTypeEnabled('task'), true);
      expect(settings.isTypeEnabled('sensor'), true);
      expect(settings.isTypeEnabled('ndvi'), true);
      expect(settings.isTypeEnabled('system'), true);
    });

    test('should return false for disabled types', () {
      settings.irrigationAlertsEnabled = false;
      expect(settings.isTypeEnabled('irrigation'), false);

      settings.weatherAlertsEnabled = false;
      expect(settings.isTypeEnabled('weather'), false);
    });

    test('should always return true for critical type', () {
      expect(settings.isTypeEnabled('critical'), true);
    });

    test('should return true for unknown types', () {
      expect(settings.isTypeEnabled('some_unknown_type'), true);
    });
  });

  group('Quiet Hours Logic', () {
    test('should not be in quiet hours when disabled', () {
      settings.quietHoursEnabled = false;
      expect(settings.isInQuietHours, false);
    });
  });

  group('JSON Export/Import', () {
    test('should export settings to JSON', () {
      final json = settings.toJson();

      expect(json['irrigation_enabled'], true);
      expect(json['weather_enabled'], true);
      expect(json['tasks_enabled'], true);
      expect(json['sensors_enabled'], true);
      expect(json['ndvi_enabled'], true);
      expect(json['system_enabled'], true);
      expect(json['sound_enabled'], true);
      expect(json['vibration_enabled'], true);
      expect(json['quiet_hours_enabled'], false);
      expect(json['quiet_hours_start'], 22);
      expect(json['quiet_hours_end'], 7);
    });

    test('should import settings from JSON', () async {
      await settings.fromJson({
        'irrigation_enabled': false,
        'weather_enabled': false,
        'tasks_enabled': false,
        'sound_enabled': false,
        'quiet_hours_enabled': true,
        'quiet_hours_start': 20,
        'quiet_hours_end': 8,
      });

      expect(settings.irrigationAlertsEnabled, false);
      expect(settings.weatherAlertsEnabled, false);
      expect(settings.taskRemindersEnabled, false);
      expect(settings.soundEnabled, false);
      expect(settings.quietHoursEnabled, true);
      expect(settings.quietHoursStart, 20);
      expect(settings.quietHoursEnd, 8);
    });

    test('should handle partial JSON import', () async {
      settings.irrigationAlertsEnabled = false;
      await settings.fromJson({
        'weather_enabled': false,
      });

      // Only weather should change, irrigation stays as set
      expect(settings.irrigationAlertsEnabled, false);
      expect(settings.weatherAlertsEnabled, false);
      expect(settings.taskRemindersEnabled, true); // Unchanged
    });

    test('should round-trip export and import', () async {
      // Set custom values
      settings.irrigationAlertsEnabled = false;
      settings.soundEnabled = false;
      settings.quietHoursEnabled = true;
      settings.quietHoursStart = 21;
      settings.quietHoursEnd = 5;

      final json = settings.toJson();

      // Reset and reimport
      await settings.reset();

      // After reset, defaults should be back
      expect(settings.irrigationAlertsEnabled, true);

      // Re-import
      await settings.fromJson(json);

      expect(settings.irrigationAlertsEnabled, false);
      expect(settings.soundEnabled, false);
      expect(settings.quietHoursEnabled, true);
      expect(settings.quietHoursStart, 21);
      expect(settings.quietHoursEnd, 5);
    });
  });

  group('Reset', () {
    test('should reset all settings to defaults', () async {
      // Modify settings
      settings.irrigationAlertsEnabled = false;
      settings.weatherAlertsEnabled = false;
      settings.soundEnabled = false;
      settings.quietHoursEnabled = true;

      // Reset
      await settings.reset();

      // Verify defaults
      expect(settings.irrigationAlertsEnabled, true);
      expect(settings.weatherAlertsEnabled, true);
      expect(settings.soundEnabled, true);
      expect(settings.quietHoursEnabled, false);
    });
  });

  group('NotificationSettingsState', () {
    test('should create from settings', () {
      final state = NotificationSettingsState.fromSettings(settings);

      expect(state.irrigationAlertsEnabled, true);
      expect(state.weatherAlertsEnabled, true);
      expect(state.taskRemindersEnabled, true);
      expect(state.sensorAlertsEnabled, true);
      expect(state.ndviAlertsEnabled, true);
      expect(state.systemNotificationsEnabled, true);
      expect(state.soundEnabled, true);
      expect(state.vibrationEnabled, true);
      expect(state.quietHoursEnabled, false);
      expect(state.quietHoursStart, 22);
      expect(state.quietHoursEnd, 7);
    });

    test('should reflect changed settings', () {
      settings.irrigationAlertsEnabled = false;
      settings.soundEnabled = false;

      final state = NotificationSettingsState.fromSettings(settings);

      expect(state.irrigationAlertsEnabled, false);
      expect(state.soundEnabled, false);
    });
  });

  group('NotificationSettingsNotifier', () {
    test('should toggle irrigation alerts', () {
      final notifier = NotificationSettingsNotifier(settings);

      expect(notifier.state.irrigationAlertsEnabled, true);
      notifier.toggleIrrigationAlerts();
      expect(notifier.state.irrigationAlertsEnabled, false);
      notifier.toggleIrrigationAlerts();
      expect(notifier.state.irrigationAlertsEnabled, true);
    });

    test('should toggle weather alerts', () {
      final notifier = NotificationSettingsNotifier(settings);

      notifier.toggleWeatherAlerts();
      expect(notifier.state.weatherAlertsEnabled, false);
    });

    test('should toggle task reminders', () {
      final notifier = NotificationSettingsNotifier(settings);

      notifier.toggleTaskReminders();
      expect(notifier.state.taskRemindersEnabled, false);
    });

    test('should toggle sensor alerts', () {
      final notifier = NotificationSettingsNotifier(settings);

      notifier.toggleSensorAlerts();
      expect(notifier.state.sensorAlertsEnabled, false);
    });

    test('should toggle sound', () {
      final notifier = NotificationSettingsNotifier(settings);

      notifier.toggleSound();
      expect(notifier.state.soundEnabled, false);
    });

    test('should toggle vibration', () {
      final notifier = NotificationSettingsNotifier(settings);

      notifier.toggleVibration();
      expect(notifier.state.vibrationEnabled, false);
    });

    test('should toggle quiet hours', () {
      final notifier = NotificationSettingsNotifier(settings);

      notifier.toggleQuietHours();
      expect(notifier.state.quietHoursEnabled, true);
    });

    test('should set quiet hours range', () {
      final notifier = NotificationSettingsNotifier(settings);

      notifier.setQuietHours(23, 6);
      expect(notifier.state.quietHoursStart, 23);
      expect(notifier.state.quietHoursEnd, 6);
    });
  });
}
