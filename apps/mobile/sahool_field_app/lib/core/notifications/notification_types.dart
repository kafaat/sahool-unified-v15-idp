library;

/// SAHOOL Notification Types
/// أنواع الإشعارات
///
/// Defines notification types, channels, and priorities for the SAHOOL platform.
/// يحدد أنواع الإشعارات والقنوات والأولويات لمنصة سهول.

// ═══════════════════════════════════════════════════════════════════════════
// Simple Notification Types (for local notifications)
// أنواع الإشعارات البسيطة (للإشعارات المحلية)
// ═══════════════════════════════════════════════════════════════════════════

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

// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL Notification Types (matches backend types)
// أنواع إشعارات سهول (تطابق أنواع الخادم)
// ═══════════════════════════════════════════════════════════════════════════

/// Notification types matching backend
/// أنواع الإشعارات المطابقة للخادم
enum SAHOOLNotificationType {
  weatherAlert('weather_alert'),
  lowStock('low_stock'),
  diseaseDetected('disease_detected'),
  sprayWindow('spray_window'),
  harvestReminder('harvest_reminder'),
  paymentDue('payment_due'),
  fieldUpdate('field_update'),
  satelliteReady('satellite_ready'),
  pestOutbreak('pest_outbreak'),
  irrigationReminder('irrigation_reminder'),
  marketPrice('market_price'),
  cropHealth('crop_health'),
  taskReminder('task_reminder'),
  system('system');

  final String value;
  const SAHOOLNotificationType(this.value);

  static SAHOOLNotificationType fromString(String value) {
    return SAHOOLNotificationType.values.firstWhere(
      (type) => type.value == value,
      orElse: () => SAHOOLNotificationType.system,
    );
  }

  /// Get notification channel ID for Android
  /// الحصول على معرف قناة الإشعار لأندرويد
  String get channelId {
    switch (this) {
      case SAHOOLNotificationType.weatherAlert:
      case SAHOOLNotificationType.diseaseDetected:
      case SAHOOLNotificationType.pestOutbreak:
        return 'sahool_alerts';
      case SAHOOLNotificationType.taskReminder:
      case SAHOOLNotificationType.harvestReminder:
      case SAHOOLNotificationType.irrigationReminder:
        return 'sahool_tasks';
      case SAHOOLNotificationType.fieldUpdate:
      case SAHOOLNotificationType.satelliteReady:
      case SAHOOLNotificationType.cropHealth:
        return 'sahool_field_updates';
      case SAHOOLNotificationType.paymentDue:
      case SAHOOLNotificationType.marketPrice:
        return 'sahool_financial';
      case SAHOOLNotificationType.sprayWindow:
        return 'sahool_operations';
      case SAHOOLNotificationType.lowStock:
        return 'sahool_inventory';
      default:
        return 'sahool_main';
    }
  }

  /// Get notification channel name (Arabic)
  /// الحصول على اسم قناة الإشعار (بالعربية)
  String get channelName {
    switch (this) {
      case SAHOOLNotificationType.weatherAlert:
      case SAHOOLNotificationType.diseaseDetected:
      case SAHOOLNotificationType.pestOutbreak:
        return 'التنبيهات العاجلة';
      case SAHOOLNotificationType.taskReminder:
      case SAHOOLNotificationType.harvestReminder:
      case SAHOOLNotificationType.irrigationReminder:
        return 'المهام والتذكيرات';
      case SAHOOLNotificationType.fieldUpdate:
      case SAHOOLNotificationType.satelliteReady:
      case SAHOOLNotificationType.cropHealth:
        return 'تحديثات الحقل';
      case SAHOOLNotificationType.paymentDue:
      case SAHOOLNotificationType.marketPrice:
        return 'المالية والأسواق';
      case SAHOOLNotificationType.sprayWindow:
        return 'العمليات الزراعية';
      case SAHOOLNotificationType.lowStock:
        return 'المخزون';
      default:
        return 'إشعارات سهول';
    }
  }

  /// Get channel description (Arabic)
  /// الحصول على وصف القناة (بالعربية)
  String get channelDescription {
    switch (this) {
      case SAHOOLNotificationType.weatherAlert:
      case SAHOOLNotificationType.diseaseDetected:
      case SAHOOLNotificationType.pestOutbreak:
        return 'تنبيهات الطقس والأمراض والآفات';
      case SAHOOLNotificationType.taskReminder:
      case SAHOOLNotificationType.harvestReminder:
      case SAHOOLNotificationType.irrigationReminder:
        return 'تذكيرات المهام والحصاد والري';
      case SAHOOLNotificationType.fieldUpdate:
      case SAHOOLNotificationType.satelliteReady:
      case SAHOOLNotificationType.cropHealth:
        return 'تحديثات صحة المحصول وصور الأقمار';
      case SAHOOLNotificationType.paymentDue:
      case SAHOOLNotificationType.marketPrice:
        return 'الدفعات وأسعار الأسواق';
      case SAHOOLNotificationType.sprayWindow:
        return 'أوقات الرش والعمليات';
      case SAHOOLNotificationType.lowStock:
        return 'إشعارات المخزون';
      default:
        return 'إشعارات عامة';
    }
  }

  /// Check if notification is urgent
  /// التحقق إذا كان الإشعار عاجلاً
  bool get isUrgent {
    return this == SAHOOLNotificationType.weatherAlert ||
        this == SAHOOLNotificationType.diseaseDetected ||
        this == SAHOOLNotificationType.pestOutbreak ||
        this == SAHOOLNotificationType.sprayWindow;
  }

  /// Get notification icon
  /// الحصول على أيقونة الإشعار
  String get icon {
    switch (this) {
      case SAHOOLNotificationType.weatherAlert:
        return 'weather_alert';
      case SAHOOLNotificationType.diseaseDetected:
        return 'disease';
      case SAHOOLNotificationType.pestOutbreak:
        return 'pest';
      case SAHOOLNotificationType.sprayWindow:
        return 'spray';
      case SAHOOLNotificationType.harvestReminder:
        return 'harvest';
      case SAHOOLNotificationType.irrigationReminder:
        return 'irrigation';
      case SAHOOLNotificationType.satelliteReady:
        return 'satellite';
      case SAHOOLNotificationType.fieldUpdate:
        return 'field';
      case SAHOOLNotificationType.cropHealth:
        return 'crop_health';
      case SAHOOLNotificationType.marketPrice:
        return 'market';
      case SAHOOLNotificationType.paymentDue:
        return 'payment';
      case SAHOOLNotificationType.lowStock:
        return 'inventory';
      case SAHOOLNotificationType.taskReminder:
        return 'task';
      default:
        return 'notification';
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Notification Priority
// أولوية الإشعار
// ═══════════════════════════════════════════════════════════════════════════

/// Notification priority levels
/// مستويات أولوية الإشعارات
enum NotificationPriority {
  low,
  medium,
  high,
  critical;

  static NotificationPriority fromString(String? value) {
    switch (value) {
      case 'critical':
        return NotificationPriority.critical;
      case 'high':
        return NotificationPriority.high;
      case 'medium':
        return NotificationPriority.medium;
      case 'low':
        return NotificationPriority.low;
      default:
        return NotificationPriority.medium;
    }
  }

  /// Get Arabic label
  /// الحصول على التسمية العربية
  String get labelAr {
    switch (this) {
      case NotificationPriority.critical:
        return 'حرج';
      case NotificationPriority.high:
        return 'عالي';
      case NotificationPriority.medium:
        return 'متوسط';
      case NotificationPriority.low:
        return 'منخفض';
    }
  }

  /// Get English label
  /// الحصول على التسمية الإنجليزية
  String get labelEn {
    switch (this) {
      case NotificationPriority.critical:
        return 'Critical';
      case NotificationPriority.high:
        return 'High';
      case NotificationPriority.medium:
        return 'Medium';
      case NotificationPriority.low:
        return 'Low';
    }
  }
}
