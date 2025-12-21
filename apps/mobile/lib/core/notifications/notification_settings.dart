import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// SAHOOL Notification Settings
/// إعدادات الإشعارات
///
/// Features:
/// - Per-type notification toggles
/// - Quiet hours configuration
/// - Sound and vibration settings

class NotificationSettings {
  static const String _prefix = 'notification_';

  final SharedPreferences _prefs;

  NotificationSettings(this._prefs);

  // ═══════════════════════════════════════════════════════════════════════════
  // إعدادات الإشعارات حسب النوع
  // ═══════════════════════════════════════════════════════════════════════════

  /// تنبيهات الري
  bool get irrigationAlertsEnabled =>
      _prefs.getBool('${_prefix}irrigation_enabled') ?? true;

  set irrigationAlertsEnabled(bool value) {
    _prefs.setBool('${_prefix}irrigation_enabled', value);
  }

  /// تنبيهات الطقس
  bool get weatherAlertsEnabled =>
      _prefs.getBool('${_prefix}weather_enabled') ?? true;

  set weatherAlertsEnabled(bool value) {
    _prefs.setBool('${_prefix}weather_enabled', value);
  }

  /// تذكيرات المهام
  bool get taskRemindersEnabled =>
      _prefs.getBool('${_prefix}tasks_enabled') ?? true;

  set taskRemindersEnabled(bool value) {
    _prefs.setBool('${_prefix}tasks_enabled', value);
  }

  /// تنبيهات الحساسات
  bool get sensorAlertsEnabled =>
      _prefs.getBool('${_prefix}sensors_enabled') ?? true;

  set sensorAlertsEnabled(bool value) {
    _prefs.setBool('${_prefix}sensors_enabled', value);
  }

  /// تنبيهات NDVI
  bool get ndviAlertsEnabled =>
      _prefs.getBool('${_prefix}ndvi_enabled') ?? true;

  set ndviAlertsEnabled(bool value) {
    _prefs.setBool('${_prefix}ndvi_enabled', value);
  }

  /// إشعارات النظام
  bool get systemNotificationsEnabled =>
      _prefs.getBool('${_prefix}system_enabled') ?? true;

  set systemNotificationsEnabled(bool value) {
    _prefs.setBool('${_prefix}system_enabled', value);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // إعدادات الصوت والاهتزاز
  // ═══════════════════════════════════════════════════════════════════════════

  /// تفعيل الصوت
  bool get soundEnabled => _prefs.getBool('${_prefix}sound_enabled') ?? true;

  set soundEnabled(bool value) {
    _prefs.setBool('${_prefix}sound_enabled', value);
  }

  /// تفعيل الاهتزاز
  bool get vibrationEnabled =>
      _prefs.getBool('${_prefix}vibration_enabled') ?? true;

  set vibrationEnabled(bool value) {
    _prefs.setBool('${_prefix}vibration_enabled', value);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // ساعات الهدوء
  // ═══════════════════════════════════════════════════════════════════════════

  /// تفعيل ساعات الهدوء
  bool get quietHoursEnabled =>
      _prefs.getBool('${_prefix}quiet_hours_enabled') ?? false;

  set quietHoursEnabled(bool value) {
    _prefs.setBool('${_prefix}quiet_hours_enabled', value);
  }

  /// بداية ساعات الهدوء (بالساعة)
  int get quietHoursStart =>
      _prefs.getInt('${_prefix}quiet_hours_start') ?? 22;

  set quietHoursStart(int value) {
    _prefs.setInt('${_prefix}quiet_hours_start', value);
  }

  /// نهاية ساعات الهدوء (بالساعة)
  int get quietHoursEnd => _prefs.getInt('${_prefix}quiet_hours_end') ?? 7;

  set quietHoursEnd(int value) {
    _prefs.setInt('${_prefix}quiet_hours_end', value);
  }

  /// التحقق إذا كنا في ساعات الهدوء
  bool get isInQuietHours {
    if (!quietHoursEnabled) return false;

    final now = DateTime.now().hour;

    if (quietHoursStart < quietHoursEnd) {
      // مثال: من 22 إلى 7 (يمتد عبر منتصف الليل)
      return now >= quietHoursStart || now < quietHoursEnd;
    } else {
      // مثال: من 14 إلى 16 (في نفس اليوم)
      return now >= quietHoursStart && now < quietHoursEnd;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التحقق من إمكانية عرض الإشعار
  // ═══════════════════════════════════════════════════════════════════════════

  /// التحقق إذا كان نوع الإشعار مفعلاً
  bool isTypeEnabled(String type) {
    // Don't show notifications during quiet hours (except critical)
    if (isInQuietHours && type != 'critical') {
      return false;
    }

    switch (type) {
      case 'irrigation':
        return irrigationAlertsEnabled;
      case 'weather':
        return weatherAlertsEnabled;
      case 'task':
        return taskRemindersEnabled;
      case 'sensor':
        return sensorAlertsEnabled;
      case 'ndvi':
        return ndviAlertsEnabled;
      case 'system':
        return systemNotificationsEnabled;
      case 'critical':
        return true; // Always show critical notifications
      default:
        return true;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // التصدير والاستيراد
  // ═══════════════════════════════════════════════════════════════════════════

  /// تصدير الإعدادات
  Map<String, dynamic> toJson() => {
        'irrigation_enabled': irrigationAlertsEnabled,
        'weather_enabled': weatherAlertsEnabled,
        'tasks_enabled': taskRemindersEnabled,
        'sensors_enabled': sensorAlertsEnabled,
        'ndvi_enabled': ndviAlertsEnabled,
        'system_enabled': systemNotificationsEnabled,
        'sound_enabled': soundEnabled,
        'vibration_enabled': vibrationEnabled,
        'quiet_hours_enabled': quietHoursEnabled,
        'quiet_hours_start': quietHoursStart,
        'quiet_hours_end': quietHoursEnd,
      };

  /// استيراد الإعدادات
  Future<void> fromJson(Map<String, dynamic> json) async {
    if (json['irrigation_enabled'] != null) {
      irrigationAlertsEnabled = json['irrigation_enabled'] as bool;
    }
    if (json['weather_enabled'] != null) {
      weatherAlertsEnabled = json['weather_enabled'] as bool;
    }
    if (json['tasks_enabled'] != null) {
      taskRemindersEnabled = json['tasks_enabled'] as bool;
    }
    if (json['sensors_enabled'] != null) {
      sensorAlertsEnabled = json['sensors_enabled'] as bool;
    }
    if (json['ndvi_enabled'] != null) {
      ndviAlertsEnabled = json['ndvi_enabled'] as bool;
    }
    if (json['system_enabled'] != null) {
      systemNotificationsEnabled = json['system_enabled'] as bool;
    }
    if (json['sound_enabled'] != null) {
      soundEnabled = json['sound_enabled'] as bool;
    }
    if (json['vibration_enabled'] != null) {
      vibrationEnabled = json['vibration_enabled'] as bool;
    }
    if (json['quiet_hours_enabled'] != null) {
      quietHoursEnabled = json['quiet_hours_enabled'] as bool;
    }
    if (json['quiet_hours_start'] != null) {
      quietHoursStart = json['quiet_hours_start'] as int;
    }
    if (json['quiet_hours_end'] != null) {
      quietHoursEnd = json['quiet_hours_end'] as int;
    }

    AppLogger.i('Notification settings imported', tag: 'NOTIFICATIONS');
  }

  /// إعادة الإعدادات للافتراضي
  Future<void> reset() async {
    final keys = _prefs.getKeys().where((k) => k.startsWith(_prefix)).toList();
    for (final key in keys) {
      await _prefs.remove(key);
    }
    AppLogger.i('Notification settings reset to defaults', tag: 'NOTIFICATIONS');
  }
}

/// Provider للإعدادات
final notificationSettingsProvider = FutureProvider<NotificationSettings>((ref) async {
  final prefs = await SharedPreferences.getInstance();
  return NotificationSettings(prefs);
});

/// Notifier للتحكم في الإعدادات
class NotificationSettingsNotifier extends StateNotifier<NotificationSettingsState> {
  final NotificationSettings _settings;

  NotificationSettingsNotifier(this._settings)
      : super(NotificationSettingsState.fromSettings(_settings));

  void toggleIrrigationAlerts() {
    _settings.irrigationAlertsEnabled = !_settings.irrigationAlertsEnabled;
    state = NotificationSettingsState.fromSettings(_settings);
  }

  void toggleWeatherAlerts() {
    _settings.weatherAlertsEnabled = !_settings.weatherAlertsEnabled;
    state = NotificationSettingsState.fromSettings(_settings);
  }

  void toggleTaskReminders() {
    _settings.taskRemindersEnabled = !_settings.taskRemindersEnabled;
    state = NotificationSettingsState.fromSettings(_settings);
  }

  void toggleSensorAlerts() {
    _settings.sensorAlertsEnabled = !_settings.sensorAlertsEnabled;
    state = NotificationSettingsState.fromSettings(_settings);
  }

  void toggleSound() {
    _settings.soundEnabled = !_settings.soundEnabled;
    state = NotificationSettingsState.fromSettings(_settings);
  }

  void toggleVibration() {
    _settings.vibrationEnabled = !_settings.vibrationEnabled;
    state = NotificationSettingsState.fromSettings(_settings);
  }

  void toggleQuietHours() {
    _settings.quietHoursEnabled = !_settings.quietHoursEnabled;
    state = NotificationSettingsState.fromSettings(_settings);
  }

  void setQuietHours(int start, int end) {
    _settings.quietHoursStart = start;
    _settings.quietHoursEnd = end;
    state = NotificationSettingsState.fromSettings(_settings);
  }
}

/// حالة الإعدادات
class NotificationSettingsState {
  final bool irrigationAlertsEnabled;
  final bool weatherAlertsEnabled;
  final bool taskRemindersEnabled;
  final bool sensorAlertsEnabled;
  final bool ndviAlertsEnabled;
  final bool systemNotificationsEnabled;
  final bool soundEnabled;
  final bool vibrationEnabled;
  final bool quietHoursEnabled;
  final int quietHoursStart;
  final int quietHoursEnd;

  const NotificationSettingsState({
    required this.irrigationAlertsEnabled,
    required this.weatherAlertsEnabled,
    required this.taskRemindersEnabled,
    required this.sensorAlertsEnabled,
    required this.ndviAlertsEnabled,
    required this.systemNotificationsEnabled,
    required this.soundEnabled,
    required this.vibrationEnabled,
    required this.quietHoursEnabled,
    required this.quietHoursStart,
    required this.quietHoursEnd,
  });

  factory NotificationSettingsState.fromSettings(NotificationSettings settings) {
    return NotificationSettingsState(
      irrigationAlertsEnabled: settings.irrigationAlertsEnabled,
      weatherAlertsEnabled: settings.weatherAlertsEnabled,
      taskRemindersEnabled: settings.taskRemindersEnabled,
      sensorAlertsEnabled: settings.sensorAlertsEnabled,
      ndviAlertsEnabled: settings.ndviAlertsEnabled,
      systemNotificationsEnabled: settings.systemNotificationsEnabled,
      soundEnabled: settings.soundEnabled,
      vibrationEnabled: settings.vibrationEnabled,
      quietHoursEnabled: settings.quietHoursEnabled,
      quietHoursStart: settings.quietHoursStart,
      quietHoursEnd: settings.quietHoursEnd,
    );
  }
}
