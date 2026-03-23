import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// App Settings State
/// حالة إعدادات التطبيق
class AppSettings {
  // Appearance | المظهر
  final ThemeMode themeMode;
  final String languageCode;
  final double fontSize;
  final bool reduceAnimations;

  // Notifications | الإشعارات
  final bool notificationsEnabled;
  final bool alertsEnabled;
  final bool weatherAlertsEnabled;
  final bool taskRemindersEnabled;
  final bool soundEnabled;
  final bool vibrationEnabled;
  final TimeOfDay? quietHoursStart;
  final TimeOfDay? quietHoursEnd;

  // Privacy | الخصوصية
  final bool analyticsEnabled;
  final bool crashReportingEnabled;
  final bool locationSharingEnabled;
  final bool dataCollectionEnabled;

  // Sync | المزامنة
  final bool autoSyncEnabled;
  final bool wifiOnlySyncEnabled;
  final int syncIntervalMinutes;
  final bool backgroundSyncEnabled;

  // Maps | الخرائط
  final String defaultMapView;
  final bool offlineMapsEnabled;
  final double defaultZoomLevel;

  // Units | الوحدات
  final String measurementSystem;
  final String dateFormat;
  final String timeFormat;
  final String currencyCode;

  const AppSettings({
    // Appearance
    this.themeMode = ThemeMode.system,
    this.languageCode = 'ar',
    this.fontSize = 1.0,
    this.reduceAnimations = false,
    // Notifications
    this.notificationsEnabled = true,
    this.alertsEnabled = true,
    this.weatherAlertsEnabled = true,
    this.taskRemindersEnabled = true,
    this.soundEnabled = true,
    this.vibrationEnabled = true,
    this.quietHoursStart,
    this.quietHoursEnd,
    // Privacy
    this.analyticsEnabled = true,
    this.crashReportingEnabled = true,
    this.locationSharingEnabled = false,
    this.dataCollectionEnabled = true,
    // Sync
    this.autoSyncEnabled = true,
    this.wifiOnlySyncEnabled = false,
    this.syncIntervalMinutes = 15,
    this.backgroundSyncEnabled = true,
    // Maps
    this.defaultMapView = 'satellite',
    this.offlineMapsEnabled = true,
    this.defaultZoomLevel = 15.0,
    // Units
    this.measurementSystem = 'metric',
    this.dateFormat = 'dd/MM/yyyy',
    this.timeFormat = '24h',
    this.currencyCode = 'YER',
  });

  AppSettings copyWith({
    ThemeMode? themeMode,
    String? languageCode,
    double? fontSize,
    bool? reduceAnimations,
    bool? notificationsEnabled,
    bool? alertsEnabled,
    bool? weatherAlertsEnabled,
    bool? taskRemindersEnabled,
    bool? soundEnabled,
    bool? vibrationEnabled,
    TimeOfDay? quietHoursStart,
    TimeOfDay? quietHoursEnd,
    bool? analyticsEnabled,
    bool? crashReportingEnabled,
    bool? locationSharingEnabled,
    bool? dataCollectionEnabled,
    bool? autoSyncEnabled,
    bool? wifiOnlySyncEnabled,
    int? syncIntervalMinutes,
    bool? backgroundSyncEnabled,
    String? defaultMapView,
    bool? offlineMapsEnabled,
    double? defaultZoomLevel,
    String? measurementSystem,
    String? dateFormat,
    String? timeFormat,
    String? currencyCode,
  }) {
    return AppSettings(
      themeMode: themeMode ?? this.themeMode,
      languageCode: languageCode ?? this.languageCode,
      fontSize: fontSize ?? this.fontSize,
      reduceAnimations: reduceAnimations ?? this.reduceAnimations,
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      alertsEnabled: alertsEnabled ?? this.alertsEnabled,
      weatherAlertsEnabled: weatherAlertsEnabled ?? this.weatherAlertsEnabled,
      taskRemindersEnabled: taskRemindersEnabled ?? this.taskRemindersEnabled,
      soundEnabled: soundEnabled ?? this.soundEnabled,
      vibrationEnabled: vibrationEnabled ?? this.vibrationEnabled,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
      analyticsEnabled: analyticsEnabled ?? this.analyticsEnabled,
      crashReportingEnabled: crashReportingEnabled ?? this.crashReportingEnabled,
      locationSharingEnabled: locationSharingEnabled ?? this.locationSharingEnabled,
      dataCollectionEnabled: dataCollectionEnabled ?? this.dataCollectionEnabled,
      autoSyncEnabled: autoSyncEnabled ?? this.autoSyncEnabled,
      wifiOnlySyncEnabled: wifiOnlySyncEnabled ?? this.wifiOnlySyncEnabled,
      syncIntervalMinutes: syncIntervalMinutes ?? this.syncIntervalMinutes,
      backgroundSyncEnabled: backgroundSyncEnabled ?? this.backgroundSyncEnabled,
      defaultMapView: defaultMapView ?? this.defaultMapView,
      offlineMapsEnabled: offlineMapsEnabled ?? this.offlineMapsEnabled,
      defaultZoomLevel: defaultZoomLevel ?? this.defaultZoomLevel,
      measurementSystem: measurementSystem ?? this.measurementSystem,
      dateFormat: dateFormat ?? this.dateFormat,
      timeFormat: timeFormat ?? this.timeFormat,
      currencyCode: currencyCode ?? this.currencyCode,
    );
  }

  /// Get theme mode display string in Arabic
  String get themeModeDisplayAr {
    switch (themeMode) {
      case ThemeMode.system:
        return 'تلقائي (حسب النظام)';
      case ThemeMode.light:
        return 'فاتح';
      case ThemeMode.dark:
        return 'داكن';
    }
  }

  /// Get language display string
  String get languageDisplayAr {
    switch (languageCode) {
      case 'ar':
        return 'العربية';
      case 'en':
        return 'English';
      default:
        return languageCode;
    }
  }

  /// Get measurement system display string in Arabic
  String get measurementSystemDisplayAr {
    switch (measurementSystem) {
      case 'metric':
        return 'متري (كم، هكتار)';
      case 'imperial':
        return 'إمبريالي (ميل، فدان)';
      default:
        return measurementSystem;
    }
  }
}

/// User Profile State
/// حالة الملف الشخصي للمستخدم
class UserProfile {
  final String id;
  final String name;
  final String? email;
  final String? phone;
  final String? farmName;
  final String? avatarUrl;
  final String tier;
  final bool isVerified;
  final bool biometricEnabled;

  const UserProfile({
    required this.id,
    required this.name,
    this.email,
    this.phone,
    this.farmName,
    this.avatarUrl,
    this.tier = 'starter',
    this.isVerified = false,
    this.biometricEnabled = false,
  });

  UserProfile copyWith({
    String? id,
    String? name,
    String? email,
    String? phone,
    String? farmName,
    String? avatarUrl,
    String? tier,
    bool? isVerified,
    bool? biometricEnabled,
  }) {
    return UserProfile(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      farmName: farmName ?? this.farmName,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      tier: tier ?? this.tier,
      isVerified: isVerified ?? this.isVerified,
      biometricEnabled: biometricEnabled ?? this.biometricEnabled,
    );
  }
}

/// Storage Info State
/// حالة معلومات التخزين
class StorageInfo {
  final int totalBytes;
  final int usedBytes;
  final int mapsBytes;
  final int imagesBytes;
  final int dataBytes;
  final int cacheBytes;

  const StorageInfo({
    this.totalBytes = 0,
    this.usedBytes = 0,
    this.mapsBytes = 0,
    this.imagesBytes = 0,
    this.dataBytes = 0,
    this.cacheBytes = 0,
  });

  double get usagePercent => totalBytes > 0 ? usedBytes / totalBytes : 0;

  String get totalFormatted => _formatBytes(totalBytes);
  String get usedFormatted => _formatBytes(usedBytes);
  String get mapsFormatted => _formatBytes(mapsBytes);
  String get imagesFormatted => _formatBytes(imagesBytes);
  String get dataFormatted => _formatBytes(dataBytes);
  String get cacheFormatted => _formatBytes(cacheBytes);
  String get availableFormatted => _formatBytes(totalBytes - usedBytes);

  String _formatBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(2)} GB';
  }
}

/// Sync Status State
/// حالة المزامنة
class SyncStatus {
  final DateTime? lastSyncTime;
  final int pendingOperations;
  final bool isSyncing;
  final String? error;

  const SyncStatus({
    this.lastSyncTime,
    this.pendingOperations = 0,
    this.isSyncing = false,
    this.error,
  });

  String get lastSyncDisplayAr {
    if (lastSyncTime == null) return 'لم تتم المزامنة بعد';
    final diff = DateTime.now().difference(lastSyncTime!);
    if (diff.inMinutes < 1) return 'الآن';
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }
}

/// Settings Notifier
/// مُدير حالة الإعدادات
class SettingsNotifier extends StateNotifier<AppSettings> {
  final SharedPreferences? _prefs;

  SettingsNotifier(this._prefs) : super(const AppSettings()) {
    _loadSettings();
  }

  void _loadSettings() {
    if (_prefs == null) return;

    state = state.copyWith(
      themeMode: ThemeMode.values[_prefs.getInt('themeMode') ?? 0],
      languageCode: _prefs.getString('languageCode') ?? 'ar',
      fontSize: _prefs.getDouble('fontSize') ?? 1.0,
      reduceAnimations: _prefs.getBool('reduceAnimations') ?? false,
      notificationsEnabled: _prefs.getBool('notificationsEnabled') ?? true,
      alertsEnabled: _prefs.getBool('alertsEnabled') ?? true,
      weatherAlertsEnabled: _prefs.getBool('weatherAlertsEnabled') ?? true,
      taskRemindersEnabled: _prefs.getBool('taskRemindersEnabled') ?? true,
      soundEnabled: _prefs.getBool('soundEnabled') ?? true,
      vibrationEnabled: _prefs.getBool('vibrationEnabled') ?? true,
      analyticsEnabled: _prefs.getBool('analyticsEnabled') ?? true,
      crashReportingEnabled: _prefs.getBool('crashReportingEnabled') ?? true,
      locationSharingEnabled: _prefs.getBool('locationSharingEnabled') ?? false,
      dataCollectionEnabled: _prefs.getBool('dataCollectionEnabled') ?? true,
      autoSyncEnabled: _prefs.getBool('autoSyncEnabled') ?? true,
      wifiOnlySyncEnabled: _prefs.getBool('wifiOnlySyncEnabled') ?? false,
      syncIntervalMinutes: _prefs.getInt('syncIntervalMinutes') ?? 15,
      backgroundSyncEnabled: _prefs.getBool('backgroundSyncEnabled') ?? true,
      defaultMapView: _prefs.getString('defaultMapView') ?? 'satellite',
      offlineMapsEnabled: _prefs.getBool('offlineMapsEnabled') ?? true,
      defaultZoomLevel: _prefs.getDouble('defaultZoomLevel') ?? 15.0,
      measurementSystem: _prefs.getString('measurementSystem') ?? 'metric',
      dateFormat: _prefs.getString('dateFormat') ?? 'dd/MM/yyyy',
      timeFormat: _prefs.getString('timeFormat') ?? '24h',
      currencyCode: _prefs.getString('currencyCode') ?? 'YER',
    );
  }

  Future<void> _saveSettings() async {
    if (_prefs == null) return;

    await _prefs.setInt('themeMode', state.themeMode.index);
    await _prefs.setString('languageCode', state.languageCode);
    await _prefs.setDouble('fontSize', state.fontSize);
    await _prefs.setBool('reduceAnimations', state.reduceAnimations);
    await _prefs.setBool('notificationsEnabled', state.notificationsEnabled);
    await _prefs.setBool('alertsEnabled', state.alertsEnabled);
    await _prefs.setBool('weatherAlertsEnabled', state.weatherAlertsEnabled);
    await _prefs.setBool('taskRemindersEnabled', state.taskRemindersEnabled);
    await _prefs.setBool('soundEnabled', state.soundEnabled);
    await _prefs.setBool('vibrationEnabled', state.vibrationEnabled);
    await _prefs.setBool('analyticsEnabled', state.analyticsEnabled);
    await _prefs.setBool('crashReportingEnabled', state.crashReportingEnabled);
    await _prefs.setBool('locationSharingEnabled', state.locationSharingEnabled);
    await _prefs.setBool('dataCollectionEnabled', state.dataCollectionEnabled);
    await _prefs.setBool('autoSyncEnabled', state.autoSyncEnabled);
    await _prefs.setBool('wifiOnlySyncEnabled', state.wifiOnlySyncEnabled);
    await _prefs.setInt('syncIntervalMinutes', state.syncIntervalMinutes);
    await _prefs.setBool('backgroundSyncEnabled', state.backgroundSyncEnabled);
    await _prefs.setString('defaultMapView', state.defaultMapView);
    await _prefs.setBool('offlineMapsEnabled', state.offlineMapsEnabled);
    await _prefs.setDouble('defaultZoomLevel', state.defaultZoomLevel);
    await _prefs.setString('measurementSystem', state.measurementSystem);
    await _prefs.setString('dateFormat', state.dateFormat);
    await _prefs.setString('timeFormat', state.timeFormat);
    await _prefs.setString('currencyCode', state.currencyCode);
  }

  // Appearance methods
  Future<void> setThemeMode(ThemeMode mode) async {
    state = state.copyWith(themeMode: mode);
    await _saveSettings();
  }

  Future<void> setLanguage(String code) async {
    state = state.copyWith(languageCode: code);
    await _saveSettings();
  }

  Future<void> setFontSize(double size) async {
    state = state.copyWith(fontSize: size);
    await _saveSettings();
  }

  Future<void> setReduceAnimations(bool value) async {
    state = state.copyWith(reduceAnimations: value);
    await _saveSettings();
  }

  // Notification methods
  Future<void> setNotificationsEnabled(bool value) async {
    state = state.copyWith(notificationsEnabled: value);
    await _saveSettings();
  }

  Future<void> setAlertsEnabled(bool value) async {
    state = state.copyWith(alertsEnabled: value);
    await _saveSettings();
  }

  Future<void> setWeatherAlertsEnabled(bool value) async {
    state = state.copyWith(weatherAlertsEnabled: value);
    await _saveSettings();
  }

  Future<void> setTaskRemindersEnabled(bool value) async {
    state = state.copyWith(taskRemindersEnabled: value);
    await _saveSettings();
  }

  Future<void> setSoundEnabled(bool value) async {
    state = state.copyWith(soundEnabled: value);
    await _saveSettings();
  }

  Future<void> setVibrationEnabled(bool value) async {
    state = state.copyWith(vibrationEnabled: value);
    await _saveSettings();
  }

  Future<void> setQuietHours(TimeOfDay? start, TimeOfDay? end) async {
    state = state.copyWith(quietHoursStart: start, quietHoursEnd: end);
    await _saveSettings();
  }

  // Privacy methods
  Future<void> setAnalyticsEnabled(bool value) async {
    state = state.copyWith(analyticsEnabled: value);
    await _saveSettings();
  }

  Future<void> setCrashReportingEnabled(bool value) async {
    state = state.copyWith(crashReportingEnabled: value);
    await _saveSettings();
  }

  Future<void> setLocationSharingEnabled(bool value) async {
    state = state.copyWith(locationSharingEnabled: value);
    await _saveSettings();
  }

  Future<void> setDataCollectionEnabled(bool value) async {
    state = state.copyWith(dataCollectionEnabled: value);
    await _saveSettings();
  }

  // Sync methods
  Future<void> setAutoSyncEnabled(bool value) async {
    state = state.copyWith(autoSyncEnabled: value);
    await _saveSettings();
  }

  Future<void> setWifiOnlySyncEnabled(bool value) async {
    state = state.copyWith(wifiOnlySyncEnabled: value);
    await _saveSettings();
  }

  Future<void> setSyncInterval(int minutes) async {
    state = state.copyWith(syncIntervalMinutes: minutes);
    await _saveSettings();
  }

  Future<void> setBackgroundSyncEnabled(bool value) async {
    state = state.copyWith(backgroundSyncEnabled: value);
    await _saveSettings();
  }

  // Maps methods
  Future<void> setDefaultMapView(String view) async {
    state = state.copyWith(defaultMapView: view);
    await _saveSettings();
  }

  Future<void> setOfflineMapsEnabled(bool value) async {
    state = state.copyWith(offlineMapsEnabled: value);
    await _saveSettings();
  }

  Future<void> setDefaultZoomLevel(double level) async {
    state = state.copyWith(defaultZoomLevel: level);
    await _saveSettings();
  }

  // Units methods
  Future<void> setMeasurementSystem(String system) async {
    state = state.copyWith(measurementSystem: system);
    await _saveSettings();
  }

  Future<void> setDateFormat(String format) async {
    state = state.copyWith(dateFormat: format);
    await _saveSettings();
  }

  Future<void> setTimeFormat(String format) async {
    state = state.copyWith(timeFormat: format);
    await _saveSettings();
  }

  Future<void> setCurrencyCode(String code) async {
    state = state.copyWith(currencyCode: code);
    await _saveSettings();
  }

  // Reset to defaults
  Future<void> resetToDefaults() async {
    state = const AppSettings();
    await _saveSettings();
  }
}

/// User Profile Notifier
class UserProfileNotifier extends StateNotifier<UserProfile> {
  UserProfileNotifier()
      : super(const UserProfile(
          id: 'demo-user',
          name: 'أحمد المزارع',
          email: 'ahmed@example.com',
          farmName: 'مزرعة الخير',
          tier: 'مبتدئ',
          isVerified: true,
        ));

  void updateProfile(UserProfile profile) {
    state = profile;
  }

  void toggleBiometric(bool enabled) {
    state = state.copyWith(biometricEnabled: enabled);
  }
}

/// Storage Info Notifier
class StorageInfoNotifier extends StateNotifier<StorageInfo> {
  StorageInfoNotifier()
      : super(const StorageInfo(
          totalBytes: 2 * 1024 * 1024 * 1024, // 2 GB
          usedBytes: 320 * 1024 * 1024, // 320 MB
          mapsBytes: 150 * 1024 * 1024, // 150 MB
          imagesBytes: 100 * 1024 * 1024, // 100 MB
          dataBytes: 50 * 1024 * 1024, // 50 MB
          cacheBytes: 20 * 1024 * 1024, // 20 MB
        ));

  Future<void> refreshStorageInfo() async {
    // In real implementation, calculate actual storage usage
    // This is placeholder data
  }

  Future<void> clearCache() async {
    state = StorageInfo(
      totalBytes: state.totalBytes,
      usedBytes: state.usedBytes - state.cacheBytes,
      mapsBytes: state.mapsBytes,
      imagesBytes: state.imagesBytes,
      dataBytes: state.dataBytes,
      cacheBytes: 0,
    );
  }
}

/// Sync Status Notifier
class SyncStatusNotifier extends StateNotifier<SyncStatus> {
  SyncStatusNotifier()
      : super(SyncStatus(
          lastSyncTime: DateTime.now().subtract(const Duration(minutes: 5)),
          pendingOperations: 0,
        ));

  Future<void> triggerSync() async {
    state = SyncStatus(
      lastSyncTime: state.lastSyncTime,
      pendingOperations: state.pendingOperations,
      isSyncing: true,
    );

    // Simulate sync
    await Future.delayed(const Duration(seconds: 2));

    state = SyncStatus(
      lastSyncTime: DateTime.now(),
      pendingOperations: 0,
      isSyncing: false,
    );
  }
}

// ========== PROVIDERS ==========

/// SharedPreferences provider
final sharedPreferencesProvider = Provider<SharedPreferences?>((ref) => null);

/// App settings provider
final appSettingsProvider =
    StateNotifierProvider<SettingsNotifier, AppSettings>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return SettingsNotifier(prefs);
});

/// User profile provider
final userProfileProvider =
    StateNotifierProvider<UserProfileNotifier, UserProfile>((ref) {
  return UserProfileNotifier();
});

/// Storage info provider
final storageInfoProvider =
    StateNotifierProvider<StorageInfoNotifier, StorageInfo>((ref) {
  return StorageInfoNotifier();
});

/// Sync status provider
final syncStatusProvider =
    StateNotifierProvider<SyncStatusNotifier, SyncStatus>((ref) {
  return SyncStatusNotifier();
});

/// Theme mode provider (convenience)
final themeModeProvider = Provider<ThemeMode>((ref) {
  return ref.watch(appSettingsProvider).themeMode;
});

/// Language code provider (convenience)
final languageCodeProvider = Provider<String>((ref) {
  return ref.watch(appSettingsProvider).languageCode;
});

/// Settings search query provider
final settingsSearchQueryProvider = StateProvider<String>((ref) => '');
