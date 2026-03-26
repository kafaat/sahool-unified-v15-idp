/// SAHOOL Notification Categories
/// فئات الإشعارات
///
/// Defines all notification categories with bilingual labels
/// and associated icons and colors
library;

import 'package:flutter/material.dart';

/// Notification category enum
/// فئات الإشعارات
enum NotificationCategory {
  /// Alerts - تنبيهات
  /// Critical, weather, pest alerts
  alerts,

  /// Tasks - مهام
  /// Due, overdue, assigned tasks
  tasks,

  /// Irrigation - ري
  /// Scheduled, completed, issues
  irrigation,

  /// NDVI - مؤشر النبات
  /// Vegetation index changes and alerts
  ndvi,

  /// System - نظام
  /// Updates, maintenance notifications
  system,

  /// Advisory - استشارات
  /// Recommendations from the system
  advisory,
}

/// Extension for NotificationCategory
extension NotificationCategoryExtension on NotificationCategory {
  /// English label
  String get label {
    switch (this) {
      case NotificationCategory.alerts:
        return 'Alerts';
      case NotificationCategory.tasks:
        return 'Tasks';
      case NotificationCategory.irrigation:
        return 'Irrigation';
      case NotificationCategory.ndvi:
        return 'NDVI';
      case NotificationCategory.system:
        return 'System';
      case NotificationCategory.advisory:
        return 'Advisory';
    }
  }

  /// Arabic label
  String get labelAr {
    switch (this) {
      case NotificationCategory.alerts:
        return 'تنبيهات';
      case NotificationCategory.tasks:
        return 'مهام';
      case NotificationCategory.irrigation:
        return 'ري';
      case NotificationCategory.ndvi:
        return 'مؤشر النبات';
      case NotificationCategory.system:
        return 'نظام';
      case NotificationCategory.advisory:
        return 'استشارات';
    }
  }

  /// Description in English
  String get description {
    switch (this) {
      case NotificationCategory.alerts:
        return 'Critical alerts, weather warnings, pest detection';
      case NotificationCategory.tasks:
        return 'Task reminders and assignments';
      case NotificationCategory.irrigation:
        return 'Irrigation schedules and status';
      case NotificationCategory.ndvi:
        return 'Vegetation health monitoring';
      case NotificationCategory.system:
        return 'System updates and maintenance';
      case NotificationCategory.advisory:
        return 'AI-powered recommendations';
    }
  }

  /// Description in Arabic
  String get descriptionAr {
    switch (this) {
      case NotificationCategory.alerts:
        return 'تنبيهات حرجة، تحذيرات الطقس، اكتشاف الآفات';
      case NotificationCategory.tasks:
        return 'تذكيرات المهام والتكليفات';
      case NotificationCategory.irrigation:
        return 'جداول الري والحالة';
      case NotificationCategory.ndvi:
        return 'مراقبة صحة النباتات';
      case NotificationCategory.system:
        return 'تحديثات النظام والصيانة';
      case NotificationCategory.advisory:
        return 'توصيات الذكاء الاصطناعي';
    }
  }

  /// Icon for category
  IconData get icon {
    switch (this) {
      case NotificationCategory.alerts:
        return Icons.warning_amber_rounded;
      case NotificationCategory.tasks:
        return Icons.task_alt;
      case NotificationCategory.irrigation:
        return Icons.water_drop;
      case NotificationCategory.ndvi:
        return Icons.grass;
      case NotificationCategory.system:
        return Icons.settings;
      case NotificationCategory.advisory:
        return Icons.lightbulb_outline;
    }
  }

  /// Color for category
  Color get color {
    switch (this) {
      case NotificationCategory.alerts:
        return Colors.red;
      case NotificationCategory.tasks:
        return Colors.orange;
      case NotificationCategory.irrigation:
        return Colors.blue;
      case NotificationCategory.ndvi:
        return Colors.green;
      case NotificationCategory.system:
        return Colors.grey;
      case NotificationCategory.advisory:
        return Colors.purple;
    }
  }

  /// Light color for backgrounds
  Color get lightColor {
    switch (this) {
      case NotificationCategory.alerts:
        return Colors.red.shade50;
      case NotificationCategory.tasks:
        return Colors.orange.shade50;
      case NotificationCategory.irrigation:
        return Colors.blue.shade50;
      case NotificationCategory.ndvi:
        return Colors.green.shade50;
      case NotificationCategory.system:
        return Colors.grey.shade100;
      case NotificationCategory.advisory:
        return Colors.purple.shade50;
    }
  }

  /// Channel ID for push notifications
  String get channelId {
    switch (this) {
      case NotificationCategory.alerts:
        return 'alerts';
      case NotificationCategory.tasks:
        return 'tasks';
      case NotificationCategory.irrigation:
        return 'irrigation';
      case NotificationCategory.ndvi:
        return 'ndvi';
      case NotificationCategory.system:
        return 'system';
      case NotificationCategory.advisory:
        return 'advisory';
    }
  }

  /// Default priority (higher = more important)
  int get defaultPriority {
    switch (this) {
      case NotificationCategory.alerts:
        return 100;
      case NotificationCategory.tasks:
        return 80;
      case NotificationCategory.irrigation:
        return 70;
      case NotificationCategory.ndvi:
        return 60;
      case NotificationCategory.advisory:
        return 50;
      case NotificationCategory.system:
        return 40;
    }
  }

  /// Whether this category can be snoozed
  bool get canSnooze {
    switch (this) {
      case NotificationCategory.alerts:
        return false; // Critical alerts should not be snoozed
      case NotificationCategory.tasks:
        return true;
      case NotificationCategory.irrigation:
        return true;
      case NotificationCategory.ndvi:
        return true;
      case NotificationCategory.system:
        return true;
      case NotificationCategory.advisory:
        return true;
    }
  }

  /// Parse from string
  static NotificationCategory? fromString(String? value) {
    if (value == null) return null;
    switch (value.toLowerCase()) {
      case 'alerts':
        return NotificationCategory.alerts;
      case 'tasks':
        return NotificationCategory.tasks;
      case 'irrigation':
        return NotificationCategory.irrigation;
      case 'ndvi':
        return NotificationCategory.ndvi;
      case 'system':
        return NotificationCategory.system;
      case 'advisory':
        return NotificationCategory.advisory;
      default:
        return null;
    }
  }
}

/// Priority levels for notifications
enum NotificationPriority {
  /// Low priority - informational
  low,

  /// Normal priority
  normal,

  /// High priority - requires attention
  high,

  /// Critical priority - immediate action required
  critical,
}

extension NotificationPriorityExtension on NotificationPriority {
  String get label {
    switch (this) {
      case NotificationPriority.low:
        return 'Low';
      case NotificationPriority.normal:
        return 'Normal';
      case NotificationPriority.high:
        return 'High';
      case NotificationPriority.critical:
        return 'Critical';
    }
  }

  String get labelAr {
    switch (this) {
      case NotificationPriority.low:
        return 'منخفض';
      case NotificationPriority.normal:
        return 'عادي';
      case NotificationPriority.high:
        return 'مرتفع';
      case NotificationPriority.critical:
        return 'حرج';
    }
  }

  Color get color {
    switch (this) {
      case NotificationPriority.low:
        return Colors.grey;
      case NotificationPriority.normal:
        return Colors.blue;
      case NotificationPriority.high:
        return Colors.orange;
      case NotificationPriority.critical:
        return Colors.red;
    }
  }

  int get value {
    switch (this) {
      case NotificationPriority.low:
        return 1;
      case NotificationPriority.normal:
        return 2;
      case NotificationPriority.high:
        return 3;
      case NotificationPriority.critical:
        return 4;
    }
  }

  static NotificationPriority fromValue(int value) {
    switch (value) {
      case 1:
        return NotificationPriority.low;
      case 2:
        return NotificationPriority.normal;
      case 3:
        return NotificationPriority.high;
      case 4:
        return NotificationPriority.critical;
      default:
        return NotificationPriority.normal;
    }
  }
}
