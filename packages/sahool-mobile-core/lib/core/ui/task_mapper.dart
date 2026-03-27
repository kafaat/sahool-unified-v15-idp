import 'package:flutter/material.dart';
import '../../features/tasks/domain/entities/field_task.dart';

/// Task Type Mapper - محول نوع المهمة إلى UI
///
/// يربط Domain TaskType بأيقونات وألوان Flutter
/// هذا الملف هو الجسر الوحيد بين Domain و UI للمهام

extension TaskTypeMapper on TaskType {
  /// أيقونة النوع
  IconData get icon {
    switch (this) {
      case TaskType.irrigation:
        return Icons.water_drop;
      case TaskType.fertilization:
        return Icons.grass;
      case TaskType.scouting:
        return Icons.search;
      case TaskType.harvest:
        return Icons.agriculture;
      case TaskType.other:
        return Icons.assignment;
    }
  }

  /// لون النوع
  Color get color {
    switch (this) {
      case TaskType.irrigation:
        return const Color(0xFF1976D2); // أزرق
      case TaskType.fertilization:
        return const Color(0xFF388E3C); // أخضر
      case TaskType.scouting:
        return const Color(0xFFF57C00); // برتقالي
      case TaskType.harvest:
        return const Color(0xFFFFA000); // ذهبي
      case TaskType.other:
        return const Color(0xFF757575); // رمادي
    }
  }

  /// لون فاتح للخلفية
  Color get lightColor {
    switch (this) {
      case TaskType.irrigation:
        return const Color(0xFFE3F2FD);
      case TaskType.fertilization:
        return const Color(0xFFE8F5E9);
      case TaskType.scouting:
        return const Color(0xFFFFF3E0);
      case TaskType.harvest:
        return const Color(0xFFFFF8E1);
      case TaskType.other:
        return const Color(0xFFF5F5F5);
    }
  }

  /// النص بالعربية
  String get textAr {
    switch (this) {
      case TaskType.irrigation:
        return 'ري';
      case TaskType.fertilization:
        return 'تسميد';
      case TaskType.scouting:
        return 'فحص';
      case TaskType.harvest:
        return 'حصاد';
      case TaskType.other:
        return 'أخرى';
    }
  }

  /// النص بالإنجليزية
  String get textEn {
    switch (this) {
      case TaskType.irrigation:
        return 'Irrigation';
      case TaskType.fertilization:
        return 'Fertilization';
      case TaskType.scouting:
        return 'Scouting';
      case TaskType.harvest:
        return 'Harvest';
      case TaskType.other:
        return 'Other';
    }
  }
}

/// Task Priority Mapper - محول أولوية المهمة
extension TaskPriorityMapper on TaskPriority {
  /// لون الأولوية
  Color get color {
    switch (this) {
      case TaskPriority.urgent:
        return const Color(0xFFC62828); // أحمر
      case TaskPriority.high:
        return const Color(0xFFF57C00); // برتقالي
      case TaskPriority.normal:
        return const Color(0xFF1976D2); // أزرق
      case TaskPriority.low:
        return const Color(0xFF757575); // رمادي
    }
  }

  /// أيقونة الأولوية
  IconData get icon {
    switch (this) {
      case TaskPriority.urgent:
        return Icons.priority_high;
      case TaskPriority.high:
        return Icons.arrow_upward;
      case TaskPriority.normal:
        return Icons.remove;
      case TaskPriority.low:
        return Icons.arrow_downward;
    }
  }

  /// النص بالعربية
  String get textAr {
    switch (this) {
      case TaskPriority.urgent:
        return 'عاجل';
      case TaskPriority.high:
        return 'عالي';
      case TaskPriority.normal:
        return 'عادي';
      case TaskPriority.low:
        return 'منخفض';
    }
  }
}

/// Field Task UI Extension
extension FieldTaskUIExtension on FieldTask {
  /// أيقونة نوع المهمة
  IconData get typeIcon => type.icon;

  /// لون نوع المهمة
  Color get typeColor => type.color;

  /// لون خلفية النوع
  Color get typeLightColor => type.lightColor;

  /// نص نوع المهمة
  String get typeText => type.textAr;

  /// لون الأولوية
  Color get priorityColor => priority.color;

  /// تنسيق وقت الاستحقاق
  String get dueTimeFormatted {
    final hour = dueTime.hour;
    final minute = dueTime.minute.toString().padLeft(2, '0');
    final period = hour >= 12 ? 'م' : 'ص';
    final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
    return '$displayHour:$minute $period';
  }

  /// تنسيق الوقت المتبقي
  String get timeRemainingFormatted {
    if (isCompleted) return 'مكتملة';
    if (isOverdue) return 'متأخرة';

    final remaining = timeRemaining;
    if (remaining.inMinutes < 60) {
      return 'خلال ${remaining.inMinutes} دقيقة';
    }
    if (remaining.inHours < 24) {
      return 'خلال ${remaining.inHours} ساعة';
    }
    return 'خلال ${remaining.inDays} يوم';
  }
}
