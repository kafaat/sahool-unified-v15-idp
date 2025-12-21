/// SAHOOL Notification Types
/// أنواع الإشعارات

enum NotificationType {
  alertHigh,
  alertMedium,
  alertLow,
  taskDue,
  taskOverdue,
  ndviDrop,
  ndviImprove,
  irrigationDue,
  weatherAlert,
  system,
}

extension NotificationTypeExtension on NotificationType {
  String get channelId {
    switch (this) {
      case NotificationType.alertHigh:
      case NotificationType.alertMedium:
      case NotificationType.alertLow:
        return 'alerts';
      case NotificationType.taskDue:
      case NotificationType.taskOverdue:
        return 'tasks';
      case NotificationType.ndviDrop:
      case NotificationType.ndviImprove:
        return 'ndvi';
      case NotificationType.irrigationDue:
        return 'irrigation';
      case NotificationType.weatherAlert:
        return 'weather';
      case NotificationType.system:
        return 'system';
    }
  }

  String get channelName {
    switch (this) {
      case NotificationType.alertHigh:
      case NotificationType.alertMedium:
      case NotificationType.alertLow:
        return 'التنبيهات';
      case NotificationType.taskDue:
      case NotificationType.taskOverdue:
        return 'المهام';
      case NotificationType.ndviDrop:
      case NotificationType.ndviImprove:
        return 'NDVI';
      case NotificationType.irrigationDue:
        return 'الري';
      case NotificationType.weatherAlert:
        return 'الطقس';
      case NotificationType.system:
        return 'النظام';
    }
  }

  String get channelDescription {
    switch (this) {
      case NotificationType.alertHigh:
      case NotificationType.alertMedium:
      case NotificationType.alertLow:
        return 'تنبيهات المزرعة';
      case NotificationType.taskDue:
      case NotificationType.taskOverdue:
        return 'إشعارات المهام';
      case NotificationType.ndviDrop:
      case NotificationType.ndviImprove:
        return 'تغييرات مؤشر NDVI';
      case NotificationType.irrigationDue:
        return 'جدولة الري';
      case NotificationType.weatherAlert:
        return 'تحذيرات الطقس';
      case NotificationType.system:
        return 'إشعارات النظام';
    }
  }

  bool get isUrgent {
    return this == NotificationType.alertHigh ||
        this == NotificationType.taskOverdue ||
        this == NotificationType.weatherAlert;
  }
}
