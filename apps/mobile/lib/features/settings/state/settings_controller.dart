import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'settings_providers.dart';

/// Settings Controller
/// متحكم الإعدادات - يوفر عمليات عالية المستوى
class SettingsController {
  final Ref _ref;

  SettingsController(this._ref);

  /// Get current settings
  AppSettings get settings => _ref.read(appSettingsProvider);

  /// Get current user profile
  UserProfile get profile => _ref.read(userProfileProvider);

  /// Get storage info
  StorageInfo get storageInfo => _ref.read(storageInfoProvider);

  /// Get sync status
  SyncStatus get syncStatus => _ref.read(syncStatusProvider);

  // ========== APPEARANCE ==========

  /// Set theme mode
  Future<void> setThemeMode(ThemeMode mode) async {
    await _ref.read(appSettingsProvider.notifier).setThemeMode(mode);
  }

  /// Set language
  Future<void> setLanguage(String code) async {
    await _ref.read(appSettingsProvider.notifier).setLanguage(code);
  }

  /// Set font size scale
  Future<void> setFontSize(double scale) async {
    await _ref.read(appSettingsProvider.notifier).setFontSize(scale);
  }

  /// Toggle reduce animations
  Future<void> toggleReduceAnimations() async {
    final current = settings.reduceAnimations;
    await _ref.read(appSettingsProvider.notifier).setReduceAnimations(!current);
  }

  // ========== NOTIFICATIONS ==========

  /// Toggle all notifications
  Future<void> toggleNotifications() async {
    final current = settings.notificationsEnabled;
    await _ref.read(appSettingsProvider.notifier).setNotificationsEnabled(!current);
  }

  /// Toggle alert notifications
  Future<void> toggleAlerts() async {
    final current = settings.alertsEnabled;
    await _ref.read(appSettingsProvider.notifier).setAlertsEnabled(!current);
  }

  /// Toggle weather alerts
  Future<void> toggleWeatherAlerts() async {
    final current = settings.weatherAlertsEnabled;
    await _ref.read(appSettingsProvider.notifier).setWeatherAlertsEnabled(!current);
  }

  /// Toggle task reminders
  Future<void> toggleTaskReminders() async {
    final current = settings.taskRemindersEnabled;
    await _ref.read(appSettingsProvider.notifier).setTaskRemindersEnabled(!current);
  }

  /// Toggle sound
  Future<void> toggleSound() async {
    final current = settings.soundEnabled;
    await _ref.read(appSettingsProvider.notifier).setSoundEnabled(!current);
  }

  /// Toggle vibration
  Future<void> toggleVibration() async {
    final current = settings.vibrationEnabled;
    await _ref.read(appSettingsProvider.notifier).setVibrationEnabled(!current);
  }

  /// Set quiet hours
  Future<void> setQuietHours(TimeOfDay? start, TimeOfDay? end) async {
    await _ref.read(appSettingsProvider.notifier).setQuietHours(start, end);
  }

  // ========== PRIVACY ==========

  /// Toggle analytics
  Future<void> toggleAnalytics() async {
    final current = settings.analyticsEnabled;
    await _ref.read(appSettingsProvider.notifier).setAnalyticsEnabled(!current);
  }

  /// Toggle crash reporting
  Future<void> toggleCrashReporting() async {
    final current = settings.crashReportingEnabled;
    await _ref.read(appSettingsProvider.notifier).setCrashReportingEnabled(!current);
  }

  /// Toggle location sharing
  Future<void> toggleLocationSharing() async {
    final current = settings.locationSharingEnabled;
    await _ref.read(appSettingsProvider.notifier).setLocationSharingEnabled(!current);
  }

  /// Toggle data collection
  Future<void> toggleDataCollection() async {
    final current = settings.dataCollectionEnabled;
    await _ref.read(appSettingsProvider.notifier).setDataCollectionEnabled(!current);
  }

  // ========== SYNC ==========

  /// Toggle auto sync
  Future<void> toggleAutoSync() async {
    final current = settings.autoSyncEnabled;
    await _ref.read(appSettingsProvider.notifier).setAutoSyncEnabled(!current);
  }

  /// Toggle WiFi only sync
  Future<void> toggleWifiOnlySync() async {
    final current = settings.wifiOnlySyncEnabled;
    await _ref.read(appSettingsProvider.notifier).setWifiOnlySyncEnabled(!current);
  }

  /// Set sync interval
  Future<void> setSyncInterval(int minutes) async {
    await _ref.read(appSettingsProvider.notifier).setSyncInterval(minutes);
  }

  /// Toggle background sync
  Future<void> toggleBackgroundSync() async {
    final current = settings.backgroundSyncEnabled;
    await _ref.read(appSettingsProvider.notifier).setBackgroundSyncEnabled(!current);
  }

  /// Trigger manual sync
  Future<void> triggerSync() async {
    await _ref.read(syncStatusProvider.notifier).triggerSync();
  }

  // ========== MAPS ==========

  /// Set default map view
  Future<void> setDefaultMapView(String view) async {
    await _ref.read(appSettingsProvider.notifier).setDefaultMapView(view);
  }

  /// Toggle offline maps
  Future<void> toggleOfflineMaps() async {
    final current = settings.offlineMapsEnabled;
    await _ref.read(appSettingsProvider.notifier).setOfflineMapsEnabled(!current);
  }

  /// Set default zoom level
  Future<void> setDefaultZoomLevel(double level) async {
    await _ref.read(appSettingsProvider.notifier).setDefaultZoomLevel(level);
  }

  // ========== UNITS ==========

  /// Set measurement system
  Future<void> setMeasurementSystem(String system) async {
    await _ref.read(appSettingsProvider.notifier).setMeasurementSystem(system);
  }

  /// Set date format
  Future<void> setDateFormat(String format) async {
    await _ref.read(appSettingsProvider.notifier).setDateFormat(format);
  }

  /// Set time format
  Future<void> setTimeFormat(String format) async {
    await _ref.read(appSettingsProvider.notifier).setTimeFormat(format);
  }

  /// Set currency code
  Future<void> setCurrencyCode(String code) async {
    await _ref.read(appSettingsProvider.notifier).setCurrencyCode(code);
  }

  // ========== STORAGE ==========

  /// Refresh storage info
  Future<void> refreshStorageInfo() async {
    await _ref.read(storageInfoProvider.notifier).refreshStorageInfo();
  }

  /// Clear cache
  Future<void> clearCache() async {
    await _ref.read(storageInfoProvider.notifier).clearCache();
  }

  /// Clear all offline data
  Future<void> clearOfflineData() async {
    // In real implementation, clear local database and files
    await refreshStorageInfo();
  }

  // ========== PROFILE ==========

  /// Update user profile
  void updateProfile({
    String? name,
    String? email,
    String? phone,
    String? farmName,
    String? avatarUrl,
  }) {
    final current = profile;
    _ref.read(userProfileProvider.notifier).updateProfile(
          current.copyWith(
            name: name ?? current.name,
            email: email ?? current.email,
            phone: phone ?? current.phone,
            farmName: farmName ?? current.farmName,
            avatarUrl: avatarUrl ?? current.avatarUrl,
          ),
        );
  }

  /// Toggle biometric authentication
  void toggleBiometric(bool enabled) {
    _ref.read(userProfileProvider.notifier).toggleBiometric(enabled);
  }

  // ========== EXPORT / IMPORT ==========

  /// Export settings to JSON
  Future<String?> exportSettings() async {
    try {
      final settingsMap = {
        'themeMode': settings.themeMode.index,
        'languageCode': settings.languageCode,
        'fontSize': settings.fontSize,
        'reduceAnimations': settings.reduceAnimations,
        'notificationsEnabled': settings.notificationsEnabled,
        'alertsEnabled': settings.alertsEnabled,
        'weatherAlertsEnabled': settings.weatherAlertsEnabled,
        'taskRemindersEnabled': settings.taskRemindersEnabled,
        'soundEnabled': settings.soundEnabled,
        'vibrationEnabled': settings.vibrationEnabled,
        'analyticsEnabled': settings.analyticsEnabled,
        'crashReportingEnabled': settings.crashReportingEnabled,
        'locationSharingEnabled': settings.locationSharingEnabled,
        'dataCollectionEnabled': settings.dataCollectionEnabled,
        'autoSyncEnabled': settings.autoSyncEnabled,
        'wifiOnlySyncEnabled': settings.wifiOnlySyncEnabled,
        'syncIntervalMinutes': settings.syncIntervalMinutes,
        'backgroundSyncEnabled': settings.backgroundSyncEnabled,
        'defaultMapView': settings.defaultMapView,
        'offlineMapsEnabled': settings.offlineMapsEnabled,
        'defaultZoomLevel': settings.defaultZoomLevel,
        'measurementSystem': settings.measurementSystem,
        'dateFormat': settings.dateFormat,
        'timeFormat': settings.timeFormat,
        'currencyCode': settings.currencyCode,
        'exportedAt': DateTime.now().toIso8601String(),
        'appVersion': '16.0.0',
      };

      final json = jsonEncode(settingsMap);

      // Save to file
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/sahool_settings.json');
      await file.writeAsString(json);

      return file.path;
    } catch (e) {
      return null;
    }
  }

  /// Import settings from JSON
  Future<bool> importSettings(String json) async {
    try {
      final map = jsonDecode(json) as Map<String, dynamic>;

      final notifier = _ref.read(appSettingsProvider.notifier);

      if (map.containsKey('themeMode')) {
        await notifier.setThemeMode(ThemeMode.values[map['themeMode'] as int]);
      }
      if (map.containsKey('languageCode')) {
        await notifier.setLanguage(map['languageCode'] as String);
      }
      if (map.containsKey('fontSize')) {
        await notifier.setFontSize((map['fontSize'] as num).toDouble());
      }
      if (map.containsKey('reduceAnimations')) {
        await notifier.setReduceAnimations(map['reduceAnimations'] as bool);
      }
      if (map.containsKey('notificationsEnabled')) {
        await notifier.setNotificationsEnabled(map['notificationsEnabled'] as bool);
      }
      if (map.containsKey('alertsEnabled')) {
        await notifier.setAlertsEnabled(map['alertsEnabled'] as bool);
      }
      if (map.containsKey('weatherAlertsEnabled')) {
        await notifier.setWeatherAlertsEnabled(map['weatherAlertsEnabled'] as bool);
      }
      if (map.containsKey('taskRemindersEnabled')) {
        await notifier.setTaskRemindersEnabled(map['taskRemindersEnabled'] as bool);
      }
      if (map.containsKey('soundEnabled')) {
        await notifier.setSoundEnabled(map['soundEnabled'] as bool);
      }
      if (map.containsKey('vibrationEnabled')) {
        await notifier.setVibrationEnabled(map['vibrationEnabled'] as bool);
      }
      if (map.containsKey('analyticsEnabled')) {
        await notifier.setAnalyticsEnabled(map['analyticsEnabled'] as bool);
      }
      if (map.containsKey('crashReportingEnabled')) {
        await notifier.setCrashReportingEnabled(map['crashReportingEnabled'] as bool);
      }
      if (map.containsKey('locationSharingEnabled')) {
        await notifier.setLocationSharingEnabled(map['locationSharingEnabled'] as bool);
      }
      if (map.containsKey('dataCollectionEnabled')) {
        await notifier.setDataCollectionEnabled(map['dataCollectionEnabled'] as bool);
      }
      if (map.containsKey('autoSyncEnabled')) {
        await notifier.setAutoSyncEnabled(map['autoSyncEnabled'] as bool);
      }
      if (map.containsKey('wifiOnlySyncEnabled')) {
        await notifier.setWifiOnlySyncEnabled(map['wifiOnlySyncEnabled'] as bool);
      }
      if (map.containsKey('syncIntervalMinutes')) {
        await notifier.setSyncInterval(map['syncIntervalMinutes'] as int);
      }
      if (map.containsKey('backgroundSyncEnabled')) {
        await notifier.setBackgroundSyncEnabled(map['backgroundSyncEnabled'] as bool);
      }
      if (map.containsKey('defaultMapView')) {
        await notifier.setDefaultMapView(map['defaultMapView'] as String);
      }
      if (map.containsKey('offlineMapsEnabled')) {
        await notifier.setOfflineMapsEnabled(map['offlineMapsEnabled'] as bool);
      }
      if (map.containsKey('defaultZoomLevel')) {
        await notifier.setDefaultZoomLevel((map['defaultZoomLevel'] as num).toDouble());
      }
      if (map.containsKey('measurementSystem')) {
        await notifier.setMeasurementSystem(map['measurementSystem'] as String);
      }
      if (map.containsKey('dateFormat')) {
        await notifier.setDateFormat(map['dateFormat'] as String);
      }
      if (map.containsKey('timeFormat')) {
        await notifier.setTimeFormat(map['timeFormat'] as String);
      }
      if (map.containsKey('currencyCode')) {
        await notifier.setCurrencyCode(map['currencyCode'] as String);
      }

      return true;
    } catch (e) {
      return false;
    }
  }

  /// Reset all settings to defaults
  Future<void> resetToDefaults() async {
    await _ref.read(appSettingsProvider.notifier).resetToDefaults();
  }
}

/// Settings Controller Provider
final settingsControllerProvider = Provider<SettingsController>((ref) {
  return SettingsController(ref);
});
