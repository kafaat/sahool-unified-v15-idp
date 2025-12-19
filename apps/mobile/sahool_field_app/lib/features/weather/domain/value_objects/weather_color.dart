/// WeatherColor - Domain Value Object
/// لون مستقل عن Flutter (DDD Clean)
///
/// هذا الكلاس لا يعتمد على dart:ui أو Flutter
/// يُستخدم فقط في Domain Layer
class WeatherColor {
  final int value;

  const WeatherColor(this.value);

  /// ألوان محددة مسبقاً للاستخدام في Domain
  static const WeatherColor green = WeatherColor(0xFF2E7D32);
  static const WeatherColor orange = WeatherColor(0xFFF9A825);
  static const WeatherColor red = WeatherColor(0xFFC62828);
  static const WeatherColor blue = WeatherColor(0xFF1976D2);
  static const WeatherColor grey = WeatherColor(0xFF6B7280);
  static const WeatherColor yellow = WeatherColor(0xFFFBC02D);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WeatherColor && runtimeType == other.runtimeType && value == other.value;

  @override
  int get hashCode => value.hashCode;

  @override
  String toString() => 'WeatherColor(0x${value.toRadixString(16).padLeft(8, '0').toUpperCase()})';
}
