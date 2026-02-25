import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/notifications/notification_types.dart';

void main() {
  group('NotificationType', () {
    test('should have correct channel IDs', () {
      expect(NotificationType.alertHigh.channelId, 'alerts');
      expect(NotificationType.alertMedium.channelId, 'alerts');
      expect(NotificationType.alertLow.channelId, 'alerts');
      expect(NotificationType.taskDue.channelId, 'tasks');
      expect(NotificationType.taskOverdue.channelId, 'tasks');
      expect(NotificationType.ndviDrop.channelId, 'ndvi');
      expect(NotificationType.ndviImprove.channelId, 'ndvi');
      expect(NotificationType.irrigationDue.channelId, 'irrigation');
      expect(NotificationType.weatherAlert.channelId, 'weather');
      expect(NotificationType.system.channelId, 'system');
    });

    test('should have Arabic channel names', () {
      expect(NotificationType.alertHigh.channelName, 'التنبيهات');
      expect(NotificationType.taskDue.channelName, 'المهام');
      expect(NotificationType.ndviDrop.channelName, 'NDVI');
      expect(NotificationType.irrigationDue.channelName, 'الري');
      expect(NotificationType.weatherAlert.channelName, 'الطقس');
      expect(NotificationType.system.channelName, 'النظام');
    });

    test('should correctly identify urgent types', () {
      expect(NotificationType.alertHigh.isUrgent, true);
      expect(NotificationType.taskOverdue.isUrgent, true);
      expect(NotificationType.weatherAlert.isUrgent, true);
      expect(NotificationType.alertMedium.isUrgent, false);
      expect(NotificationType.alertLow.isUrgent, false);
      expect(NotificationType.system.isUrgent, false);
      expect(NotificationType.ndviDrop.isUrgent, false);
      expect(NotificationType.irrigationDue.isUrgent, false);
    });

    test('should have all expected values', () {
      expect(NotificationType.values.length, 10);
    });
  });

  group('SAHOOLNotificationType', () {
    test('should parse from string correctly', () {
      expect(SAHOOLNotificationType.fromString('weather_alert'),
          SAHOOLNotificationType.weatherAlert);
      expect(SAHOOLNotificationType.fromString('disease_detected'),
          SAHOOLNotificationType.diseaseDetected);
      expect(SAHOOLNotificationType.fromString('pest_outbreak'),
          SAHOOLNotificationType.pestOutbreak);
      expect(SAHOOLNotificationType.fromString('spray_window'),
          SAHOOLNotificationType.sprayWindow);
      expect(SAHOOLNotificationType.fromString('harvest_reminder'),
          SAHOOLNotificationType.harvestReminder);
      expect(SAHOOLNotificationType.fromString('irrigation_reminder'),
          SAHOOLNotificationType.irrigationReminder);
      expect(SAHOOLNotificationType.fromString('task_reminder'),
          SAHOOLNotificationType.taskReminder);
      expect(SAHOOLNotificationType.fromString('field_update'),
          SAHOOLNotificationType.fieldUpdate);
      expect(SAHOOLNotificationType.fromString('satellite_ready'),
          SAHOOLNotificationType.satelliteReady);
      expect(SAHOOLNotificationType.fromString('crop_health'),
          SAHOOLNotificationType.cropHealth);
      expect(SAHOOLNotificationType.fromString('market_price'),
          SAHOOLNotificationType.marketPrice);
      expect(SAHOOLNotificationType.fromString('payment_due'),
          SAHOOLNotificationType.paymentDue);
      expect(SAHOOLNotificationType.fromString('low_stock'),
          SAHOOLNotificationType.lowStock);
      expect(SAHOOLNotificationType.fromString('system'),
          SAHOOLNotificationType.system);
    });

    test('should return system for unknown string', () {
      expect(SAHOOLNotificationType.fromString('unknown_type'),
          SAHOOLNotificationType.system);
      expect(
          SAHOOLNotificationType.fromString(''), SAHOOLNotificationType.system);
    });

    test('should map to correct Android channel IDs', () {
      expect(SAHOOLNotificationType.weatherAlert.channelId, 'sahool_alerts');
      expect(SAHOOLNotificationType.diseaseDetected.channelId, 'sahool_alerts');
      expect(SAHOOLNotificationType.pestOutbreak.channelId, 'sahool_alerts');
      expect(SAHOOLNotificationType.taskReminder.channelId, 'sahool_tasks');
      expect(SAHOOLNotificationType.harvestReminder.channelId, 'sahool_tasks');
      expect(
          SAHOOLNotificationType.irrigationReminder.channelId, 'sahool_tasks');
      expect(
          SAHOOLNotificationType.fieldUpdate.channelId, 'sahool_field_updates');
      expect(SAHOOLNotificationType.satelliteReady.channelId,
          'sahool_field_updates');
      expect(
          SAHOOLNotificationType.cropHealth.channelId, 'sahool_field_updates');
      expect(SAHOOLNotificationType.paymentDue.channelId, 'sahool_financial');
      expect(SAHOOLNotificationType.marketPrice.channelId, 'sahool_financial');
      expect(SAHOOLNotificationType.sprayWindow.channelId, 'sahool_operations');
      expect(SAHOOLNotificationType.lowStock.channelId, 'sahool_inventory');
      expect(SAHOOLNotificationType.system.channelId, 'sahool_main');
    });

    test('should correctly identify urgent types', () {
      expect(SAHOOLNotificationType.weatherAlert.isUrgent, true);
      expect(SAHOOLNotificationType.diseaseDetected.isUrgent, true);
      expect(SAHOOLNotificationType.pestOutbreak.isUrgent, true);
      expect(SAHOOLNotificationType.sprayWindow.isUrgent, true);
      expect(SAHOOLNotificationType.taskReminder.isUrgent, false);
      expect(SAHOOLNotificationType.system.isUrgent, false);
      expect(SAHOOLNotificationType.marketPrice.isUrgent, false);
    });

    test('should have Arabic channel names', () {
      expect(
          SAHOOLNotificationType.weatherAlert.channelName, 'التنبيهات العاجلة');
      expect(
          SAHOOLNotificationType.taskReminder.channelName, 'المهام والتذكيرات');
      expect(SAHOOLNotificationType.fieldUpdate.channelName, 'تحديثات الحقل');
      expect(SAHOOLNotificationType.paymentDue.channelName, 'المالية والأسواق');
      expect(
          SAHOOLNotificationType.sprayWindow.channelName, 'العمليات الزراعية');
      expect(SAHOOLNotificationType.lowStock.channelName, 'المخزون');
      expect(SAHOOLNotificationType.system.channelName, 'إشعارات سهول');
    });

    test('should have icon for each type', () {
      for (final type in SAHOOLNotificationType.values) {
        expect(type.icon, isNotEmpty);
      }
    });

    test('should have 14 notification types', () {
      expect(SAHOOLNotificationType.values.length, 14);
    });
  });

  group('NotificationPriority', () {
    test('should parse from string correctly', () {
      expect(NotificationPriority.fromString('critical'),
          NotificationPriority.critical);
      expect(
          NotificationPriority.fromString('high'), NotificationPriority.high);
      expect(NotificationPriority.fromString('medium'),
          NotificationPriority.medium);
      expect(NotificationPriority.fromString('low'), NotificationPriority.low);
    });

    test('should return medium for unknown string', () {
      expect(NotificationPriority.fromString('unknown'),
          NotificationPriority.medium);
      expect(
          NotificationPriority.fromString(null), NotificationPriority.medium);
    });

    test('should have Arabic labels', () {
      expect(NotificationPriority.critical.labelAr, 'حرج');
      expect(NotificationPriority.high.labelAr, 'عالي');
      expect(NotificationPriority.medium.labelAr, 'متوسط');
      expect(NotificationPriority.low.labelAr, 'منخفض');
    });

    test('should have English labels', () {
      expect(NotificationPriority.critical.labelEn, 'Critical');
      expect(NotificationPriority.high.labelEn, 'High');
      expect(NotificationPriority.medium.labelEn, 'Medium');
      expect(NotificationPriority.low.labelEn, 'Low');
    });

    test('should have 4 priority levels', () {
      expect(NotificationPriority.values.length, 4);
    });
  });
}
