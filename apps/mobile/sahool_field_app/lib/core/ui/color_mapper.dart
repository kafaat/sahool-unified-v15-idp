import 'dart:ui';
import '../../features/weather/domain/value_objects/weather_color.dart';

/// UI Color Mapper - محول الألوان من Domain إلى Flutter
///
/// هذا الملف هو الجسر الوحيد بين Domain Colors و Flutter Colors
/// يُستخدم فقط في UI Layer

/// Extension لتحويل WeatherColor إلى Flutter Color
extension WeatherColorMapper on WeatherColor {
  /// تحويل إلى Flutter Color
  Color toFlutter() => Color(value);

  /// تحويل مع شفافية
  Color toFlutterWithOpacity(double opacity) => Color(value).withOpacity(opacity);
}

/// Helper functions للاستخدام في UI
class ColorMapper {
  ColorMapper._();

  /// تحويل WeatherColor إلى Flutter Color
  static Color fromWeather(WeatherColor weatherColor) => Color(weatherColor.value);

  /// تحويل قيمة int مباشرة
  static Color fromValue(int value) => Color(value);

  /// إنشاء WeatherColor من Flutter Color
  static WeatherColor toWeather(Color flutterColor) => WeatherColor(flutterColor.value);
}
