/// Notification Preferences Tests
/// اختبارات تفضيلات الإشعارات
///
/// Tests for NotificationPreferences model, Riverpod provider, and filtering logic

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/notifications/notification_preferences.dart';
import 'package:sahool_field_app/core/notifications/firebase_messaging_service.dart';

void main() {
  group('NotificationPreferences model', () {
    test('should have sensible defaults', () {
      const prefs = NotificationPreferences();

      expect(prefs.weatherAlerts, isTrue);
      expect(prefs.diseaseDetection, isTrue);
      expect(prefs.pestOutbreak, isTrue);
      expect(prefs.lowStock, isFalse); // Intentionally off by default
      expect(prefs.enableQuietHours, isFalse);
      expect(prefs.enableSound, isTrue);
      expect(prefs.enableVibration, isTrue);
      expect(prefs.minimumPriority, NotificationPriority.low);
      expect(prefs.showBadge, isTrue);
    });

    test('should be immutable (const)', () {
      const prefs1 = NotificationPreferences();
      const prefs2 = NotificationPreferences();

      // Both should be valid const instances
      expect(prefs1.weatherAlerts, prefs2.weatherAlerts);
    });

    test('copyWith should create modified copy without mutating original', () {
      const original = NotificationPreferences();
      final modified = original.copyWith(
        weatherAlerts: false,
        enableQuietHours: true,
      );

      expect(original.weatherAlerts, isTrue);
      expect(modified.weatherAlerts, isFalse);
      expect(original.enableQuietHours, isFalse);
      expect(modified.enableQuietHours, isTrue);
      // Unmodified fields preserved
      expect(modified.diseaseDetection, isTrue);
      expect(modified.enableSound, isTrue);
    });

    test('copyWith with no arguments should preserve all values', () {
      const original = NotificationPreferences(
        weatherAlerts: false,
        enableQuietHours: true,
        minimumPriority: NotificationPriority.high,
      );
      final copy = original.copyWith();

      expect(copy.weatherAlerts, isFalse);
      expect(copy.enableQuietHours, isTrue);
      expect(copy.minimumPriority, NotificationPriority.high);
    });
  });

  group('NotificationPreferences JSON serialization', () {
    test('should round-trip through toJson/fromJson', () {
      const original = NotificationPreferences(
        weatherAlerts: false,
        diseaseDetection: true,
        enableQuietHours: true,
        quietHoursStart: TimeOfDay(hour: 23, minute: 30),
        quietHoursEnd: TimeOfDay(hour: 5, minute: 0),
        minimumPriority: NotificationPriority.high,
        enableSound: false,
      );

      final json = original.toJson();
      final restored = NotificationPreferences.fromJson(json);

      expect(restored.weatherAlerts, isFalse);
      expect(restored.diseaseDetection, isTrue);
      expect(restored.enableQuietHours, isTrue);
      expect(restored.quietHoursStart.hour, 23);
      expect(restored.quietHoursStart.minute, 30);
      expect(restored.quietHoursEnd.hour, 5);
      expect(restored.quietHoursEnd.minute, 0);
      expect(restored.minimumPriority, NotificationPriority.high);
      expect(restored.enableSound, isFalse);
    });

    test('fromJson should use defaults for missing keys', () {
      final prefs = NotificationPreferences.fromJson({});

      expect(prefs.weatherAlerts, isTrue);
      expect(prefs.diseaseDetection, isTrue);
      expect(prefs.lowStock, isFalse);
      expect(prefs.enableQuietHours, isFalse);
      expect(prefs.minimumPriority, NotificationPriority.low);
    });

    test('fromJson should handle invalid priority gracefully', () {
      final prefs = NotificationPreferences.fromJson({
        'minimumPriority': 'invalid_value',
      });

      expect(prefs.minimumPriority, NotificationPriority.low); // fallback
    });
  });

  group('NotificationPreferences isTypeEnabled', () {
    test('should return correct values for each type', () {
      const prefs = NotificationPreferences(
        weatherAlerts: true,
        diseaseDetection: false,
        pestOutbreak: true,
      );

      expect(prefs.isTypeEnabled(SAHOOLNotificationType.weatherAlert), isTrue);
      expect(prefs.isTypeEnabled(SAHOOLNotificationType.diseaseDetected), isFalse);
      expect(prefs.isTypeEnabled(SAHOOLNotificationType.pestOutbreak), isTrue);
    });
  });

  group('NotificationPreferences priority filtering', () {
    test('low minimum should allow all priorities', () {
      const prefs = NotificationPreferences(
        minimumPriority: NotificationPriority.low,
      );

      expect(prefs.meetsPriorityThreshold(NotificationPriority.low), isTrue);
      expect(prefs.meetsPriorityThreshold(NotificationPriority.medium), isTrue);
      expect(prefs.meetsPriorityThreshold(NotificationPriority.high), isTrue);
      expect(prefs.meetsPriorityThreshold(NotificationPriority.critical), isTrue);
    });

    test('high minimum should block low and medium', () {
      const prefs = NotificationPreferences(
        minimumPriority: NotificationPriority.high,
      );

      expect(prefs.meetsPriorityThreshold(NotificationPriority.low), isFalse);
      expect(prefs.meetsPriorityThreshold(NotificationPriority.medium), isFalse);
      expect(prefs.meetsPriorityThreshold(NotificationPriority.high), isTrue);
      expect(prefs.meetsPriorityThreshold(NotificationPriority.critical), isTrue);
    });
  });

  group('NotificationPreferences shouldShowNotification', () {
    test('should block disabled types', () {
      const prefs = NotificationPreferences(weatherAlerts: false);

      expect(
        prefs.shouldShowNotification(
          SAHOOLNotificationType.weatherAlert,
          NotificationPriority.high,
        ),
        isFalse,
      );
    });

    test('should block below-priority notifications', () {
      const prefs = NotificationPreferences(
        minimumPriority: NotificationPriority.high,
        weatherAlerts: true,
      );

      expect(
        prefs.shouldShowNotification(
          SAHOOLNotificationType.weatherAlert,
          NotificationPriority.low,
        ),
        isFalse,
      );
    });

    test('should allow enabled type with sufficient priority', () {
      const prefs = NotificationPreferences(
        weatherAlerts: true,
        minimumPriority: NotificationPriority.low,
      );

      expect(
        prefs.shouldShowNotification(
          SAHOOLNotificationType.weatherAlert,
          NotificationPriority.medium,
        ),
        isTrue,
      );
    });
  });
}
