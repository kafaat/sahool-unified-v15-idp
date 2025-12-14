import 'weather_color.dart';

/// AlertSeverity - شدة التنبيه
/// Domain Value Object مستقل عن Flutter
enum AlertSeverity {
  /// تحذير شديد - خطر
  warning,

  /// مراقبة - انتباه
  watch,

  /// إرشادي - معلومات
  advisory,

  /// عادي
  normal,
}

/// Extension لربط كل حالة بلون Domain
extension AlertSeverityColor on AlertSeverity {
  WeatherColor get color {
    switch (this) {
      case AlertSeverity.warning:
        return WeatherColor.red;
      case AlertSeverity.watch:
        return WeatherColor.orange;
      case AlertSeverity.advisory:
        return WeatherColor.blue;
      case AlertSeverity.normal:
        return WeatherColor.grey;
    }
  }

  String get labelAr {
    switch (this) {
      case AlertSeverity.warning:
        return 'تحذير';
      case AlertSeverity.watch:
        return 'مراقبة';
      case AlertSeverity.advisory:
        return 'إرشادي';
      case AlertSeverity.normal:
        return 'عادي';
    }
  }

  /// Parse from string
  static AlertSeverity fromString(String value) {
    switch (value.toLowerCase()) {
      case 'warning':
        return AlertSeverity.warning;
      case 'watch':
        return AlertSeverity.watch;
      case 'advisory':
        return AlertSeverity.advisory;
      default:
        return AlertSeverity.normal;
    }
  }
}
