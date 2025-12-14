import 'weather_color.dart';

/// WeatherSeverity - حالة شدة الطقس
/// Domain Value Object مستقل عن Flutter
enum WeatherSeverity {
  /// ظروف مواتية - مناسبة للعمل الزراعي
  favorable,

  /// تحذير - يجب الحذر
  caution,

  /// غير مواتية - تجنب العمل
  unfavorable,
}

/// Extension لربط كل حالة بلون Domain
extension WeatherSeverityColor on WeatherSeverity {
  WeatherColor get color {
    switch (this) {
      case WeatherSeverity.favorable:
        return WeatherColor.green;
      case WeatherSeverity.caution:
        return WeatherColor.orange;
      case WeatherSeverity.unfavorable:
        return WeatherColor.red;
    }
  }

  String get labelAr {
    switch (this) {
      case WeatherSeverity.favorable:
        return 'مناسب';
      case WeatherSeverity.caution:
        return 'تحذير';
      case WeatherSeverity.unfavorable:
        return 'غير مناسب';
    }
  }

  String get icon {
    switch (this) {
      case WeatherSeverity.favorable:
        return '✅';
      case WeatherSeverity.caution:
        return '⚠️';
      case WeatherSeverity.unfavorable:
        return '🚫';
    }
  }
}
