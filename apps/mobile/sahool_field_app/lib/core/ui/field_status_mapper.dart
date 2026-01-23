import 'dart:ui';
import 'package:flutter/material.dart';
import '../../features/field/domain/entities/field.dart';

/// Field Status Mapper - محول حالة الحقل إلى UI
///
/// يربط Domain FieldStatus بألوان ونصوص Flutter
/// هذا الملف هو الجسر الوحيد بين Domain و UI

extension FieldStatusMapper on FieldStatus {
  /// تحويل الحالة إلى لون Flutter
  Color toColor() {
    switch (this) {
      case FieldStatus.healthy:
        return const Color(0xFF2E7D32); // أخضر غامق
      case FieldStatus.stressed:
        return const Color(0xFFF9A825); // أصفر/برتقالي
      case FieldStatus.critical:
        return const Color(0xFFC62828); // أحمر
      case FieldStatus.unknown:
        return const Color(0xFF9E9E9E); // رمادي
    }
  }

  /// لون فاتح للخلفيات
  Color toLightColor() {
    switch (this) {
      case FieldStatus.healthy:
        return const Color(0xFFE8F5E9);
      case FieldStatus.stressed:
        return const Color(0xFFFFF8E1);
      case FieldStatus.critical:
        return const Color(0xFFFFEBEE);
      case FieldStatus.unknown:
        return const Color(0xFFF5F5F5);
    }
  }

  /// النص بالعربية
  String toText() {
    switch (this) {
      case FieldStatus.healthy:
        return 'ممتاز';
      case FieldStatus.stressed:
        return 'إجهاد';
      case FieldStatus.critical:
        return 'خطر';
      case FieldStatus.unknown:
        return 'غير معروف';
    }
  }

  /// النص بالإنجليزية
  String toTextEn() {
    switch (this) {
      case FieldStatus.healthy:
        return 'Healthy';
      case FieldStatus.stressed:
        return 'Stressed';
      case FieldStatus.critical:
        return 'Critical';
      case FieldStatus.unknown:
        return 'Unknown';
    }
  }

  /// أيقونة الحالة
  IconData toIcon() {
    switch (this) {
      case FieldStatus.healthy:
        return Icons.check_circle;
      case FieldStatus.stressed:
        return Icons.warning_amber;
      case FieldStatus.critical:
        return Icons.error;
      case FieldStatus.unknown:
        return Icons.help_outline;
    }
  }

  /// إيموجي الحالة
  String toEmoji() {
    switch (this) {
      case FieldStatus.healthy:
        return '✅';
      case FieldStatus.stressed:
        return '⚠️';
      case FieldStatus.critical:
        return '🚨';
      case FieldStatus.unknown:
        return '❓';
    }
  }
}

/// Extension للحقل نفسه
extension FieldUIExtension on Field {
  /// لون الحالة
  Color get statusColor => status.toColor();

  /// لون خلفية الحالة
  Color get statusBackgroundColor => status.toLightColor();

  /// نص الحالة
  String get statusText => status.toText();

  /// أيقونة الحالة
  IconData get statusIcon => status.toIcon();

  /// تنسيق المساحة
  String get areaFormatted => '${areaHa.toStringAsFixed(1)} هكتار';

  /// تنسيق NDVI
  String get ndviFormatted => ndvi.toStringAsFixed(2);

  /// تنسيق NDVI كنسبة مئوية
  String get ndviPercentage => '${healthPercentage}%';
}
