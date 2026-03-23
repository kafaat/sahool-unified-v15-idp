import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// User Preferences Manager - Persists user preferences
/// مدير تفضيلات المستخدم - يحفظ تفضيلات المستخدم
///
/// Features:
/// - Theme mode (dark/light/system)
/// - Language preference (ar/en)
/// - Map type preference
/// - Notification settings
/// - Default farm/field selection
/// - Uses shared_preferences for simple data
/// - Uses flutter_secure_storage for sensitive data

// ============================================================
// Constants - Storage Keys
// ============================================================

// Non-sensitive preferences (shared_preferences)
const String _keyThemeMode = 'pref_theme_mode';
const String _keyLanguage = 'pref_language';
const String _keyMapType = 'pref_map_type';
const String _keyDefaultFarmId = 'pref_default_farm_id';
const String _keyDefaultFieldId = 'pref_default_field_id';
const String _keyMeasurementUnit = 'pref_measurement_unit';
const String _keyDateFormat = 'pref_date_format';
const String _keyShowTutorials = 'pref_show_tutorials';
const String _keyCompactMode = 'pref_compact_mode';
const String _keyAutoSync = 'pref_auto_sync';
const String _keySyncOnWifiOnly = 'pref_sync_wifi_only';
const String _keyDataSaverMode = 'pref_data_saver_mode';
const String _keyOfflineMapsEnabled = 'pref_offline_maps_enabled';

// Notification settings (shared_preferences)
const String _keyNotificationsEnabled = 'pref_notifications_enabled';
const String _keyTaskNotifications = 'pref_task_notifications';
const String _keyWeatherAlerts = 'pref_weather_alerts';
const String _keyCropHealthAlerts = 'pref_crop_health_alerts';
const String _keyMarketNotifications = 'pref_market_notifications';
const String _keyCommunityNotifications = 'pref_community_notifications';
const String _keyQuietHoursEnabled = 'pref_quiet_hours_enabled';
const String _keyQuietHoursStart = 'pref_quiet_hours_start';
const String _keyQuietHoursEnd = 'pref_quiet_hours_end';

// Sensitive preferences (flutter_secure_storage)
const String _keyApiEndpoint = 'secure_api_endpoint';
const String _keyUserPin = 'secure_user_pin';

// ============================================================
// Enums
// ============================================================

/// Map type preference
/// تفضيل نوع الخريطة
enum MapTypePreference {
  satellite, // قمر صناعي
  terrain, // تضاريس
  hybrid, // مختلط
  normal, // عادي
}

/// Measurement unit preference
/// تفضيل وحدة القياس
enum MeasurementUnit {
  metric, // متري (هكتار، كم)
  imperial, // إمبريالي (فدان، ميل)
  local, // محلي (دونم)
}

/// Date format preference
/// تفضيل تنسيق التاريخ
enum DateFormatPreference {
  gregorian, // ميلادي
  hijri, // هجري
  both, // كلاهما
}

// ============================================================
// Notification Settings Model
// ============================================================

/// Notification settings configuration
/// إعدادات الإشعارات
class NotificationSettings {
  final bool enabled;
  final bool taskNotifications;
  final bool weatherAlerts;
  final bool cropHealthAlerts;
  final bool marketNotifications;
  final bool communityNotifications;
  final bool quietHoursEnabled;
  final TimeOfDay quietHoursStart;
  final TimeOfDay quietHoursEnd;

  const NotificationSettings({
    this.enabled = true,
    this.taskNotifications = true,
    this.weatherAlerts = true,
    this.cropHealthAlerts = true,
    this.marketNotifications = true,
    this.communityNotifications = true,
    this.quietHoursEnabled = false,
    this.quietHoursStart = const TimeOfDay(hour: 22, minute: 0),
    this.quietHoursEnd = const TimeOfDay(hour: 7, minute: 0),
  });

  NotificationSettings copyWith({
    bool? enabled,
    bool? taskNotifications,
    bool? weatherAlerts,
    bool? cropHealthAlerts,
    bool? marketNotifications,
    bool? communityNotifications,
    bool? quietHoursEnabled,
    TimeOfDay? quietHoursStart,
    TimeOfDay? quietHoursEnd,
  }) {
    return NotificationSettings(
      enabled: enabled ?? this.enabled,
      taskNotifications: taskNotifications ?? this.taskNotifications,
      weatherAlerts: weatherAlerts ?? this.weatherAlerts,
      cropHealthAlerts: cropHealthAlerts ?? this.cropHealthAlerts,
      marketNotifications: marketNotifications ?? this.marketNotifications,
      communityNotifications: communityNotifications ?? this.communityNotifications,
      quietHoursEnabled: quietHoursEnabled ?? this.quietHoursEnabled,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
    );
  }

  Map<String, dynamic> toJson() => {
        'enabled': enabled,
        'taskNotifications': taskNotifications,
        'weatherAlerts': weatherAlerts,
        'cropHealthAlerts': cropHealthAlerts,
        'marketNotifications': marketNotifications,
        'communityNotifications': communityNotifications,
        'quietHoursEnabled': quietHoursEnabled,
        'quietHoursStart': '${quietHoursStart.hour}:${quietHoursStart.minute}',
        'quietHoursEnd': '${quietHoursEnd.hour}:${quietHoursEnd.minute}',
      };

  factory NotificationSettings.fromJson(Map<String, dynamic> json) {
    TimeOfDay parseTime(String? str, TimeOfDay defaultValue) {
      if (str == null) return defaultValue;
      final parts = str.split(':');
      if (parts.length != 2) return defaultValue;
      return TimeOfDay(
        hour: int.tryParse(parts[0]) ?? defaultValue.hour,
        minute: int.tryParse(parts[1]) ?? defaultValue.minute,
      );
    }

    return NotificationSettings(
      enabled: json['enabled'] as bool? ?? true,
      taskNotifications: json['taskNotifications'] as bool? ?? true,
      weatherAlerts: json['weatherAlerts'] as bool? ?? true,
      cropHealthAlerts: json['cropHealthAlerts'] as bool? ?? true,
      marketNotifications: json['marketNotifications'] as bool? ?? true,
      communityNotifications: json['communityNotifications'] as bool? ?? true,
      quietHoursEnabled: json['quietHoursEnabled'] as bool? ?? false,
      quietHoursStart: parseTime(
        json['quietHoursStart'] as String?,
        const TimeOfDay(hour: 22, minute: 0),
      ),
      quietHoursEnd: parseTime(
        json['quietHoursEnd'] as String?,
        const TimeOfDay(hour: 7, minute: 0),
      ),
    );
  }
}

// ============================================================
// User Preferences Model
// ============================================================

/// Complete user preferences state
/// حالة تفضيلات المستخدم الكاملة
class UserPreferences {
  final ThemeMode themeMode;
  final Locale language;
  final MapTypePreference mapType;
  final String? defaultFarmId;
  final String? defaultFieldId;
  final MeasurementUnit measurementUnit;
  final DateFormatPreference dateFormat;
  final bool showTutorials;
  final bool compactMode;
  final bool autoSync;
  final bool syncOnWifiOnly;
  final bool dataSaverMode;
  final bool offlineMapsEnabled;
  final NotificationSettings notifications;

  const UserPreferences({
    this.themeMode = ThemeMode.system,
    this.language = const Locale('ar'),
    this.mapType = MapTypePreference.satellite,
    this.defaultFarmId,
    this.defaultFieldId,
    this.measurementUnit = MeasurementUnit.metric,
    this.dateFormat = DateFormatPreference.both,
    this.showTutorials = true,
    this.compactMode = false,
    this.autoSync = true,
    this.syncOnWifiOnly = false,
    this.dataSaverMode = false,
    this.offlineMapsEnabled = true,
    this.notifications = const NotificationSettings(),
  });

  UserPreferences copyWith({
    ThemeMode? themeMode,
    Locale? language,
    MapTypePreference? mapType,
    String? defaultFarmId,
    String? defaultFieldId,
    MeasurementUnit? measurementUnit,
    DateFormatPreference? dateFormat,
    bool? showTutorials,
    bool? compactMode,
    bool? autoSync,
    bool? syncOnWifiOnly,
    bool? dataSaverMode,
    bool? offlineMapsEnabled,
    NotificationSettings? notifications,
  }) {
    return UserPreferences(
      themeMode: themeMode ?? this.themeMode,
      language: language ?? this.language,
      mapType: mapType ?? this.mapType,
      defaultFarmId: defaultFarmId ?? this.defaultFarmId,
      defaultFieldId: defaultFieldId ?? this.defaultFieldId,
      measurementUnit: measurementUnit ?? this.measurementUnit,
      dateFormat: dateFormat ?? this.dateFormat,
      showTutorials: showTutorials ?? this.showTutorials,
      compactMode: compactMode ?? this.compactMode,
      autoSync: autoSync ?? this.autoSync,
      syncOnWifiOnly: syncOnWifiOnly ?? this.syncOnWifiOnly,
      dataSaverMode: dataSaverMode ?? this.dataSaverMode,
      offlineMapsEnabled: offlineMapsEnabled ?? this.offlineMapsEnabled,
      notifications: notifications ?? this.notifications,
    );
  }
}

// ============================================================
// Preferences Manager Service
// ============================================================

/// Service for managing user preferences
/// خدمة إدارة تفضيلات المستخدم
class PreferencesManager {
  late SharedPreferences _prefs;
  late FlutterSecureStorage _secureStorage;
  bool _isInitialized = false;

  /// Initialize the preferences manager
  /// تهيئة مدير التفضيلات
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      _prefs = await SharedPreferences.getInstance();
      _secureStorage = const FlutterSecureStorage(
        aOptions: AndroidOptions(
          encryptedSharedPreferences: true,
          sharedPreferencesName: 'sahool_prefs_secure',
          preferencesKeyPrefix: 'sahool_pref_',
        ),
        iOptions: IOSOptions(
          accessibility: KeychainAccessibility.first_unlock_this_device,
          accountName: 'com.sahool.field.prefs',
        ),
      );
      _isInitialized = true;
      AppLogger.i('PreferencesManager initialized', tag: 'Preferences');
    } catch (e) {
      AppLogger.e('Failed to initialize PreferencesManager', tag: 'Preferences', error: e);
      rethrow;
    }
  }

  void _ensureInitialized() {
    if (!_isInitialized) {
      throw StateError('PreferencesManager not initialized. Call initialize() first.');
    }
  }

  // ============================================================
  // Theme Preferences
  // ============================================================

  /// Get theme mode preference
  /// الحصول على تفضيل وضع السمة
  ThemeMode getThemeMode() {
    _ensureInitialized();
    final value = _prefs.getString(_keyThemeMode);
    switch (value) {
      case 'light':
        return ThemeMode.light;
      case 'dark':
        return ThemeMode.dark;
      default:
        return ThemeMode.system;
    }
  }

  /// Set theme mode preference
  /// تعيين تفضيل وضع السمة
  Future<void> setThemeMode(ThemeMode mode) async {
    _ensureInitialized();
    String value;
    switch (mode) {
      case ThemeMode.light:
        value = 'light';
        break;
      case ThemeMode.dark:
        value = 'dark';
        break;
      case ThemeMode.system:
        value = 'system';
        break;
    }
    await _prefs.setString(_keyThemeMode, value);
    AppLogger.d('Theme mode set to: $value', tag: 'Preferences');
  }

  // ============================================================
  // Language Preferences
  // ============================================================

  /// Get language preference
  /// الحصول على تفضيل اللغة
  Locale getLanguage() {
    _ensureInitialized();
    final value = _prefs.getString(_keyLanguage);
    if (value == 'en') {
      return const Locale('en');
    }
    return const Locale('ar'); // Default to Arabic
  }

  /// Set language preference
  /// تعيين تفضيل اللغة
  Future<void> setLanguage(Locale locale) async {
    _ensureInitialized();
    await _prefs.setString(_keyLanguage, locale.languageCode);
    AppLogger.d('Language set to: ${locale.languageCode}', tag: 'Preferences');
  }

  // ============================================================
  // Map Preferences
  // ============================================================

  /// Get map type preference
  /// الحصول على تفضيل نوع الخريطة
  MapTypePreference getMapType() {
    _ensureInitialized();
    final value = _prefs.getString(_keyMapType);
    switch (value) {
      case 'terrain':
        return MapTypePreference.terrain;
      case 'hybrid':
        return MapTypePreference.hybrid;
      case 'normal':
        return MapTypePreference.normal;
      default:
        return MapTypePreference.satellite;
    }
  }

  /// Set map type preference
  /// تعيين تفضيل نوع الخريطة
  Future<void> setMapType(MapTypePreference type) async {
    _ensureInitialized();
    await _prefs.setString(_keyMapType, type.name);
    AppLogger.d('Map type set to: ${type.name}', tag: 'Preferences');
  }

  /// Get offline maps enabled
  /// الحصول على حالة تمكين الخرائط دون اتصال
  bool getOfflineMapsEnabled() {
    _ensureInitialized();
    return _prefs.getBool(_keyOfflineMapsEnabled) ?? true;
  }

  /// Set offline maps enabled
  /// تعيين حالة تمكين الخرائط دون اتصال
  Future<void> setOfflineMapsEnabled(bool enabled) async {
    _ensureInitialized();
    await _prefs.setBool(_keyOfflineMapsEnabled, enabled);
    AppLogger.d('Offline maps enabled: $enabled', tag: 'Preferences');
  }

  // ============================================================
  // Default Farm/Field Preferences
  // ============================================================

  /// Get default farm ID
  /// الحصول على معرف المزرعة الافتراضي
  String? getDefaultFarmId() {
    _ensureInitialized();
    return _prefs.getString(_keyDefaultFarmId);
  }

  /// Set default farm ID
  /// تعيين معرف المزرعة الافتراضي
  Future<void> setDefaultFarmId(String? farmId) async {
    _ensureInitialized();
    if (farmId == null) {
      await _prefs.remove(_keyDefaultFarmId);
    } else {
      await _prefs.setString(_keyDefaultFarmId, farmId);
    }
    AppLogger.d('Default farm ID set to: $farmId', tag: 'Preferences');
  }

  /// Get default field ID
  /// الحصول على معرف الحقل الافتراضي
  String? getDefaultFieldId() {
    _ensureInitialized();
    return _prefs.getString(_keyDefaultFieldId);
  }

  /// Set default field ID
  /// تعيين معرف الحقل الافتراضي
  Future<void> setDefaultFieldId(String? fieldId) async {
    _ensureInitialized();
    if (fieldId == null) {
      await _prefs.remove(_keyDefaultFieldId);
    } else {
      await _prefs.setString(_keyDefaultFieldId, fieldId);
    }
    AppLogger.d('Default field ID set to: $fieldId', tag: 'Preferences');
  }

  // ============================================================
  // Measurement & Display Preferences
  // ============================================================

  /// Get measurement unit preference
  /// الحصول على تفضيل وحدة القياس
  MeasurementUnit getMeasurementUnit() {
    _ensureInitialized();
    final value = _prefs.getString(_keyMeasurementUnit);
    switch (value) {
      case 'imperial':
        return MeasurementUnit.imperial;
      case 'local':
        return MeasurementUnit.local;
      default:
        return MeasurementUnit.metric;
    }
  }

  /// Set measurement unit preference
  /// تعيين تفضيل وحدة القياس
  Future<void> setMeasurementUnit(MeasurementUnit unit) async {
    _ensureInitialized();
    await _prefs.setString(_keyMeasurementUnit, unit.name);
    AppLogger.d('Measurement unit set to: ${unit.name}', tag: 'Preferences');
  }

  /// Get date format preference
  /// الحصول على تفضيل تنسيق التاريخ
  DateFormatPreference getDateFormat() {
    _ensureInitialized();
    final value = _prefs.getString(_keyDateFormat);
    switch (value) {
      case 'gregorian':
        return DateFormatPreference.gregorian;
      case 'hijri':
        return DateFormatPreference.hijri;
      default:
        return DateFormatPreference.both;
    }
  }

  /// Set date format preference
  /// تعيين تفضيل تنسيق التاريخ
  Future<void> setDateFormat(DateFormatPreference format) async {
    _ensureInitialized();
    await _prefs.setString(_keyDateFormat, format.name);
    AppLogger.d('Date format set to: ${format.name}', tag: 'Preferences');
  }

  // ============================================================
  // UI Preferences
  // ============================================================

  /// Get show tutorials preference
  /// الحصول على تفضيل عرض الدروس
  bool getShowTutorials() {
    _ensureInitialized();
    return _prefs.getBool(_keyShowTutorials) ?? true;
  }

  /// Set show tutorials preference
  /// تعيين تفضيل عرض الدروس
  Future<void> setShowTutorials(bool show) async {
    _ensureInitialized();
    await _prefs.setBool(_keyShowTutorials, show);
  }

  /// Get compact mode preference
  /// الحصول على تفضيل الوضع المدمج
  bool getCompactMode() {
    _ensureInitialized();
    return _prefs.getBool(_keyCompactMode) ?? false;
  }

  /// Set compact mode preference
  /// تعيين تفضيل الوضع المدمج
  Future<void> setCompactMode(bool compact) async {
    _ensureInitialized();
    await _prefs.setBool(_keyCompactMode, compact);
  }

  // ============================================================
  // Sync Preferences
  // ============================================================

  /// Get auto sync preference
  /// الحصول على تفضيل المزامنة التلقائية
  bool getAutoSync() {
    _ensureInitialized();
    return _prefs.getBool(_keyAutoSync) ?? true;
  }

  /// Set auto sync preference
  /// تعيين تفضيل المزامنة التلقائية
  Future<void> setAutoSync(bool enabled) async {
    _ensureInitialized();
    await _prefs.setBool(_keyAutoSync, enabled);
  }

  /// Get sync on wifi only preference
  /// الحصول على تفضيل المزامنة عبر الواي فاي فقط
  bool getSyncOnWifiOnly() {
    _ensureInitialized();
    return _prefs.getBool(_keySyncOnWifiOnly) ?? false;
  }

  /// Set sync on wifi only preference
  /// تعيين تفضيل المزامنة عبر الواي فاي فقط
  Future<void> setSyncOnWifiOnly(bool wifiOnly) async {
    _ensureInitialized();
    await _prefs.setBool(_keySyncOnWifiOnly, wifiOnly);
  }

  /// Get data saver mode preference
  /// الحصول على تفضيل وضع توفير البيانات
  bool getDataSaverMode() {
    _ensureInitialized();
    return _prefs.getBool(_keyDataSaverMode) ?? false;
  }

  /// Set data saver mode preference
  /// تعيين تفضيل وضع توفير البيانات
  Future<void> setDataSaverMode(bool enabled) async {
    _ensureInitialized();
    await _prefs.setBool(_keyDataSaverMode, enabled);
  }

  // ============================================================
  // Notification Preferences
  // ============================================================

  /// Get notification settings
  /// الحصول على إعدادات الإشعارات
  NotificationSettings getNotificationSettings() {
    _ensureInitialized();

    return NotificationSettings(
      enabled: _prefs.getBool(_keyNotificationsEnabled) ?? true,
      taskNotifications: _prefs.getBool(_keyTaskNotifications) ?? true,
      weatherAlerts: _prefs.getBool(_keyWeatherAlerts) ?? true,
      cropHealthAlerts: _prefs.getBool(_keyCropHealthAlerts) ?? true,
      marketNotifications: _prefs.getBool(_keyMarketNotifications) ?? true,
      communityNotifications: _prefs.getBool(_keyCommunityNotifications) ?? true,
      quietHoursEnabled: _prefs.getBool(_keyQuietHoursEnabled) ?? false,
      quietHoursStart: _parseTimeOfDay(
        _prefs.getString(_keyQuietHoursStart),
        const TimeOfDay(hour: 22, minute: 0),
      ),
      quietHoursEnd: _parseTimeOfDay(
        _prefs.getString(_keyQuietHoursEnd),
        const TimeOfDay(hour: 7, minute: 0),
      ),
    );
  }

  /// Set notification settings
  /// تعيين إعدادات الإشعارات
  Future<void> setNotificationSettings(NotificationSettings settings) async {
    _ensureInitialized();

    await Future.wait([
      _prefs.setBool(_keyNotificationsEnabled, settings.enabled),
      _prefs.setBool(_keyTaskNotifications, settings.taskNotifications),
      _prefs.setBool(_keyWeatherAlerts, settings.weatherAlerts),
      _prefs.setBool(_keyCropHealthAlerts, settings.cropHealthAlerts),
      _prefs.setBool(_keyMarketNotifications, settings.marketNotifications),
      _prefs.setBool(_keyCommunityNotifications, settings.communityNotifications),
      _prefs.setBool(_keyQuietHoursEnabled, settings.quietHoursEnabled),
      _prefs.setString(
        _keyQuietHoursStart,
        '${settings.quietHoursStart.hour}:${settings.quietHoursStart.minute}',
      ),
      _prefs.setString(
        _keyQuietHoursEnd,
        '${settings.quietHoursEnd.hour}:${settings.quietHoursEnd.minute}',
      ),
    ]);

    AppLogger.d('Notification settings updated', tag: 'Preferences');
  }

  TimeOfDay _parseTimeOfDay(String? value, TimeOfDay defaultValue) {
    if (value == null) return defaultValue;
    final parts = value.split(':');
    if (parts.length != 2) return defaultValue;
    return TimeOfDay(
      hour: int.tryParse(parts[0]) ?? defaultValue.hour,
      minute: int.tryParse(parts[1]) ?? defaultValue.minute,
    );
  }

  // ============================================================
  // Secure Preferences
  // ============================================================

  /// Get custom API endpoint (secure)
  /// الحصول على نقطة نهاية API مخصصة (آمن)
  Future<String?> getApiEndpoint() async {
    _ensureInitialized();
    try {
      return await _secureStorage.read(key: _keyApiEndpoint);
    } catch (e) {
      AppLogger.e('Failed to read API endpoint', tag: 'Preferences', error: e);
      return null;
    }
  }

  /// Set custom API endpoint (secure)
  /// تعيين نقطة نهاية API مخصصة (آمن)
  Future<void> setApiEndpoint(String? endpoint) async {
    _ensureInitialized();
    try {
      if (endpoint == null) {
        await _secureStorage.delete(key: _keyApiEndpoint);
      } else {
        await _secureStorage.write(key: _keyApiEndpoint, value: endpoint);
      }
    } catch (e) {
      AppLogger.e('Failed to set API endpoint', tag: 'Preferences', error: e);
      rethrow;
    }
  }

  /// Check if user has set a PIN
  /// التحقق مما إذا كان المستخدم قد عيّن رقم PIN
  Future<bool> hasUserPin() async {
    _ensureInitialized();
    try {
      final pin = await _secureStorage.read(key: _keyUserPin);
      return pin != null && pin.isNotEmpty;
    } catch (e) {
      return false;
    }
  }

  /// Set user PIN (secure)
  /// تعيين رقم PIN للمستخدم (آمن)
  Future<void> setUserPin(String pin) async {
    _ensureInitialized();
    try {
      await _secureStorage.write(key: _keyUserPin, value: pin);
      AppLogger.i('User PIN set', tag: 'Preferences');
    } catch (e) {
      AppLogger.e('Failed to set user PIN', tag: 'Preferences', error: e);
      rethrow;
    }
  }

  /// Verify user PIN
  /// التحقق من رقم PIN للمستخدم
  Future<bool> verifyUserPin(String pin) async {
    _ensureInitialized();
    try {
      final storedPin = await _secureStorage.read(key: _keyUserPin);
      return storedPin == pin;
    } catch (e) {
      AppLogger.e('Failed to verify user PIN', tag: 'Preferences', error: e);
      return false;
    }
  }

  /// Clear user PIN
  /// مسح رقم PIN للمستخدم
  Future<void> clearUserPin() async {
    _ensureInitialized();
    try {
      await _secureStorage.delete(key: _keyUserPin);
      AppLogger.i('User PIN cleared', tag: 'Preferences');
    } catch (e) {
      AppLogger.e('Failed to clear user PIN', tag: 'Preferences', error: e);
    }
  }

  // ============================================================
  // Batch Operations
  // ============================================================

  /// Get all user preferences as a single object
  /// الحصول على جميع تفضيلات المستخدم ككائن واحد
  UserPreferences getAllPreferences() {
    _ensureInitialized();
    return UserPreferences(
      themeMode: getThemeMode(),
      language: getLanguage(),
      mapType: getMapType(),
      defaultFarmId: getDefaultFarmId(),
      defaultFieldId: getDefaultFieldId(),
      measurementUnit: getMeasurementUnit(),
      dateFormat: getDateFormat(),
      showTutorials: getShowTutorials(),
      compactMode: getCompactMode(),
      autoSync: getAutoSync(),
      syncOnWifiOnly: getSyncOnWifiOnly(),
      dataSaverMode: getDataSaverMode(),
      offlineMapsEnabled: getOfflineMapsEnabled(),
      notifications: getNotificationSettings(),
    );
  }

  /// Save all user preferences
  /// حفظ جميع تفضيلات المستخدم
  Future<void> saveAllPreferences(UserPreferences prefs) async {
    _ensureInitialized();

    await Future.wait([
      setThemeMode(prefs.themeMode),
      setLanguage(prefs.language),
      setMapType(prefs.mapType),
      setDefaultFarmId(prefs.defaultFarmId),
      setDefaultFieldId(prefs.defaultFieldId),
      setMeasurementUnit(prefs.measurementUnit),
      setDateFormat(prefs.dateFormat),
      setShowTutorials(prefs.showTutorials),
      setCompactMode(prefs.compactMode),
      setAutoSync(prefs.autoSync),
      setSyncOnWifiOnly(prefs.syncOnWifiOnly),
      setDataSaverMode(prefs.dataSaverMode),
      setOfflineMapsEnabled(prefs.offlineMapsEnabled),
      setNotificationSettings(prefs.notifications),
    ]);

    AppLogger.i('All preferences saved', tag: 'Preferences');
  }

  /// Reset all preferences to defaults
  /// إعادة تعيين جميع التفضيلات إلى الافتراضيات
  Future<void> resetToDefaults() async {
    _ensureInitialized();

    final keys = [
      _keyThemeMode,
      _keyLanguage,
      _keyMapType,
      _keyDefaultFarmId,
      _keyDefaultFieldId,
      _keyMeasurementUnit,
      _keyDateFormat,
      _keyShowTutorials,
      _keyCompactMode,
      _keyAutoSync,
      _keySyncOnWifiOnly,
      _keyDataSaverMode,
      _keyOfflineMapsEnabled,
      _keyNotificationsEnabled,
      _keyTaskNotifications,
      _keyWeatherAlerts,
      _keyCropHealthAlerts,
      _keyMarketNotifications,
      _keyCommunityNotifications,
      _keyQuietHoursEnabled,
      _keyQuietHoursStart,
      _keyQuietHoursEnd,
    ];

    await Future.wait(keys.map((key) => _prefs.remove(key)));

    AppLogger.i('Preferences reset to defaults', tag: 'Preferences');
  }

  /// Export preferences to JSON (for backup)
  /// تصدير التفضيلات إلى JSON (للنسخ الاحتياطي)
  String exportToJson() {
    _ensureInitialized();

    final prefs = getAllPreferences();
    final map = {
      'themeMode': prefs.themeMode.name,
      'language': prefs.language.languageCode,
      'mapType': prefs.mapType.name,
      'defaultFarmId': prefs.defaultFarmId,
      'defaultFieldId': prefs.defaultFieldId,
      'measurementUnit': prefs.measurementUnit.name,
      'dateFormat': prefs.dateFormat.name,
      'showTutorials': prefs.showTutorials,
      'compactMode': prefs.compactMode,
      'autoSync': prefs.autoSync,
      'syncOnWifiOnly': prefs.syncOnWifiOnly,
      'dataSaverMode': prefs.dataSaverMode,
      'offlineMapsEnabled': prefs.offlineMapsEnabled,
      'notifications': prefs.notifications.toJson(),
      'exportedAt': DateTime.now().toIso8601String(),
    };

    return jsonEncode(map);
  }

  /// Import preferences from JSON (for restore)
  /// استيراد التفضيلات من JSON (للاستعادة)
  Future<void> importFromJson(String jsonString) async {
    _ensureInitialized();

    try {
      final map = jsonDecode(jsonString) as Map<String, dynamic>;

      // Parse theme mode
      ThemeMode themeMode = ThemeMode.system;
      if (map['themeMode'] == 'light') themeMode = ThemeMode.light;
      if (map['themeMode'] == 'dark') themeMode = ThemeMode.dark;

      // Parse map type
      MapTypePreference mapType = MapTypePreference.satellite;
      try {
        mapType = MapTypePreference.values.byName(map['mapType'] as String);
      } catch (e) {
        AppLogger.w('Failed to parse mapType preference: ${map['mapType']}', tag: 'Preferences');
      }

      // Parse measurement unit
      MeasurementUnit measurementUnit = MeasurementUnit.metric;
      try {
        measurementUnit = MeasurementUnit.values.byName(map['measurementUnit'] as String);
      } catch (e) {
        AppLogger.w('Failed to parse measurementUnit preference: ${map['measurementUnit']}', tag: 'Preferences');
      }

      // Parse date format
      DateFormatPreference dateFormat = DateFormatPreference.both;
      try {
        dateFormat = DateFormatPreference.values.byName(map['dateFormat'] as String);
      } catch (e) {
        AppLogger.w('Failed to parse dateFormat preference: ${map['dateFormat']}', tag: 'Preferences');
      }

      final prefs = UserPreferences(
        themeMode: themeMode,
        language: Locale(map['language'] as String? ?? 'ar'),
        mapType: mapType,
        defaultFarmId: map['defaultFarmId'] as String?,
        defaultFieldId: map['defaultFieldId'] as String?,
        measurementUnit: measurementUnit,
        dateFormat: dateFormat,
        showTutorials: map['showTutorials'] as bool? ?? true,
        compactMode: map['compactMode'] as bool? ?? false,
        autoSync: map['autoSync'] as bool? ?? true,
        syncOnWifiOnly: map['syncOnWifiOnly'] as bool? ?? false,
        dataSaverMode: map['dataSaverMode'] as bool? ?? false,
        offlineMapsEnabled: map['offlineMapsEnabled'] as bool? ?? true,
        notifications: map['notifications'] != null
            ? NotificationSettings.fromJson(map['notifications'] as Map<String, dynamic>)
            : const NotificationSettings(),
      );

      await saveAllPreferences(prefs);
      AppLogger.i('Preferences imported from JSON', tag: 'Preferences');
    } catch (e) {
      AppLogger.e('Failed to import preferences', tag: 'Preferences', error: e);
      rethrow;
    }
  }
}

// ============================================================
// Riverpod Providers
// ============================================================

/// Provider for PreferencesManager
final preferencesManagerProvider = Provider<PreferencesManager>((ref) {
  return PreferencesManager();
});

/// Provider for user preferences state
final userPreferencesProvider = StateNotifierProvider<UserPreferencesNotifier, UserPreferences>((ref) {
  final manager = ref.watch(preferencesManagerProvider);
  return UserPreferencesNotifier(manager);
});

/// State notifier for user preferences
class UserPreferencesNotifier extends StateNotifier<UserPreferences> {
  final PreferencesManager _manager;
  bool _isInitialized = false;

  UserPreferencesNotifier(this._manager) : super(const UserPreferences());

  /// Initialize and load preferences
  Future<void> initialize() async {
    if (_isInitialized) return;

    await _manager.initialize();
    state = _manager.getAllPreferences();
    _isInitialized = true;
  }

  /// Update theme mode
  Future<void> setThemeMode(ThemeMode mode) async {
    await _manager.setThemeMode(mode);
    state = state.copyWith(themeMode: mode);
  }

  /// Update language
  Future<void> setLanguage(Locale locale) async {
    await _manager.setLanguage(locale);
    state = state.copyWith(language: locale);
  }

  /// Update map type
  Future<void> setMapType(MapTypePreference type) async {
    await _manager.setMapType(type);
    state = state.copyWith(mapType: type);
  }

  /// Update default farm
  Future<void> setDefaultFarm(String? farmId) async {
    await _manager.setDefaultFarmId(farmId);
    state = state.copyWith(defaultFarmId: farmId);
  }

  /// Update default field
  Future<void> setDefaultField(String? fieldId) async {
    await _manager.setDefaultFieldId(fieldId);
    state = state.copyWith(defaultFieldId: fieldId);
  }

  /// Update notification settings
  Future<void> setNotificationSettings(NotificationSettings settings) async {
    await _manager.setNotificationSettings(settings);
    state = state.copyWith(notifications: settings);
  }

  /// Reset to defaults
  Future<void> resetToDefaults() async {
    await _manager.resetToDefaults();
    state = const UserPreferences();
  }
}

/// Provider for theme mode (convenience)
final themeModeProvider = Provider<ThemeMode>((ref) {
  return ref.watch(userPreferencesProvider).themeMode;
});

/// Provider for locale (convenience)
final localeProvider = Provider<Locale>((ref) {
  return ref.watch(userPreferencesProvider).language;
});

/// Provider for notification settings (convenience)
final notificationSettingsProvider = Provider<NotificationSettings>((ref) {
  return ref.watch(userPreferencesProvider).notifications;
});
