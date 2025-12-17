import 'dart:async';
import '../storage/database.dart';

/// Selective Sync - User-configurable sync preferences
/// مزامنة انتقائية - تفضيلات المزامنة القابلة للتخصيص
class SelectiveSync {
  final AppDatabase database;

  static const String _prefsKey = 'selective_sync_prefs';

  SelectiveSync({required this.database});

  /// Default sync preferences
  static SyncPreferences get defaultPreferences => const SyncPreferences(
        syncTasks: true,
        syncFields: true,
        syncExperiments: true,
        syncLogs: true,
        syncSamples: true,
        syncWeather: true,
        syncMaps: false, // Maps are large, sync manually
        autoSyncOnWifi: true,
        autoSyncOnMobile: false,
        syncFrequencyMinutes: 15,
        maxOfflineDays: 30,
      );

  /// Load sync preferences
  Future<SyncPreferences> loadPreferences() async {
    try {
      final json = await database.getMetadata(_prefsKey);
      if (json != null) {
        return SyncPreferences.fromJson(json);
      }
    } catch (e) {
      // Return defaults on error
    }
    return defaultPreferences;
  }

  /// Save sync preferences
  Future<void> savePreferences(SyncPreferences prefs) async {
    await database.setMetadata(_prefsKey, prefs.toJson());
  }

  /// Check if entity type should sync
  Future<bool> shouldSync(String entityType) async {
    final prefs = await loadPreferences();
    return prefs.shouldSyncEntity(entityType);
  }

  /// Get sync filter for entity types
  Future<List<String>> getEnabledEntityTypes() async {
    final prefs = await loadPreferences();
    return prefs.enabledEntityTypes;
  }

  /// Check sync connectivity preference
  Future<SyncConnectivity> checkConnectivityPreference(bool isWifi) async {
    final prefs = await loadPreferences();

    if (isWifi && prefs.autoSyncOnWifi) {
      return SyncConnectivity.allowed;
    }

    if (!isWifi && prefs.autoSyncOnMobile) {
      return SyncConnectivity.allowed;
    }

    if (!isWifi && !prefs.autoSyncOnMobile) {
      return SyncConnectivity.mobileDisabled;
    }

    return SyncConnectivity.disabled;
  }

  /// Get sync frequency
  Future<Duration> getSyncFrequency() async {
    final prefs = await loadPreferences();
    return Duration(minutes: prefs.syncFrequencyMinutes);
  }

  /// Get max offline days for data retention
  Future<int> getMaxOfflineDays() async {
    final prefs = await loadPreferences();
    return prefs.maxOfflineDays;
  }

  /// Update single preference
  Future<void> updatePreference(String key, dynamic value) async {
    final prefs = await loadPreferences();
    final updated = prefs.copyWith(key: key, value: value);
    await savePreferences(updated);
  }

  /// Reset to defaults
  Future<void> resetToDefaults() async {
    await savePreferences(defaultPreferences);
  }
}

/// Sync preferences
class SyncPreferences {
  final bool syncTasks;
  final bool syncFields;
  final bool syncExperiments;
  final bool syncLogs;
  final bool syncSamples;
  final bool syncWeather;
  final bool syncMaps;
  final bool autoSyncOnWifi;
  final bool autoSyncOnMobile;
  final int syncFrequencyMinutes;
  final int maxOfflineDays;

  const SyncPreferences({
    required this.syncTasks,
    required this.syncFields,
    required this.syncExperiments,
    required this.syncLogs,
    required this.syncSamples,
    required this.syncWeather,
    required this.syncMaps,
    required this.autoSyncOnWifi,
    required this.autoSyncOnMobile,
    required this.syncFrequencyMinutes,
    required this.maxOfflineDays,
  });

  /// Check if entity type should sync
  bool shouldSyncEntity(String entityType) {
    switch (entityType) {
      case 'task':
        return syncTasks;
      case 'field':
        return syncFields;
      case 'experiment':
        return syncExperiments;
      case 'log':
        return syncLogs;
      case 'sample':
        return syncSamples;
      case 'weather':
        return syncWeather;
      case 'map':
        return syncMaps;
      default:
        return true;
    }
  }

  /// Get list of enabled entity types
  List<String> get enabledEntityTypes {
    final types = <String>[];
    if (syncTasks) types.add('task');
    if (syncFields) types.add('field');
    if (syncExperiments) types.add('experiment');
    if (syncLogs) types.add('log');
    if (syncSamples) types.add('sample');
    if (syncWeather) types.add('weather');
    if (syncMaps) types.add('map');
    return types;
  }

  /// Copy with single key update
  SyncPreferences copyWith({required String key, required dynamic value}) {
    return SyncPreferences(
      syncTasks: key == 'syncTasks' ? value as bool : syncTasks,
      syncFields: key == 'syncFields' ? value as bool : syncFields,
      syncExperiments: key == 'syncExperiments' ? value as bool : syncExperiments,
      syncLogs: key == 'syncLogs' ? value as bool : syncLogs,
      syncSamples: key == 'syncSamples' ? value as bool : syncSamples,
      syncWeather: key == 'syncWeather' ? value as bool : syncWeather,
      syncMaps: key == 'syncMaps' ? value as bool : syncMaps,
      autoSyncOnWifi: key == 'autoSyncOnWifi' ? value as bool : autoSyncOnWifi,
      autoSyncOnMobile: key == 'autoSyncOnMobile' ? value as bool : autoSyncOnMobile,
      syncFrequencyMinutes: key == 'syncFrequencyMinutes' ? value as int : syncFrequencyMinutes,
      maxOfflineDays: key == 'maxOfflineDays' ? value as int : maxOfflineDays,
    );
  }

  /// To JSON string
  String toJson() {
    return '{"syncTasks":$syncTasks,"syncFields":$syncFields,"syncExperiments":$syncExperiments,'
        '"syncLogs":$syncLogs,"syncSamples":$syncSamples,"syncWeather":$syncWeather,'
        '"syncMaps":$syncMaps,"autoSyncOnWifi":$autoSyncOnWifi,"autoSyncOnMobile":$autoSyncOnMobile,'
        '"syncFrequencyMinutes":$syncFrequencyMinutes,"maxOfflineDays":$maxOfflineDays}';
  }

  /// From JSON string
  factory SyncPreferences.fromJson(String json) {
    try {
      // Simple JSON parsing without importing dart:convert
      bool getBool(String key) {
        final pattern = RegExp('"$key":(true|false)');
        final match = pattern.firstMatch(json);
        return match?.group(1) == 'true';
      }

      int getInt(String key) {
        final pattern = RegExp('"$key":(\\d+)');
        final match = pattern.firstMatch(json);
        return int.tryParse(match?.group(1) ?? '0') ?? 0;
      }

      return SyncPreferences(
        syncTasks: getBool('syncTasks'),
        syncFields: getBool('syncFields'),
        syncExperiments: getBool('syncExperiments'),
        syncLogs: getBool('syncLogs'),
        syncSamples: getBool('syncSamples'),
        syncWeather: getBool('syncWeather'),
        syncMaps: getBool('syncMaps'),
        autoSyncOnWifi: getBool('autoSyncOnWifi'),
        autoSyncOnMobile: getBool('autoSyncOnMobile'),
        syncFrequencyMinutes: getInt('syncFrequencyMinutes'),
        maxOfflineDays: getInt('maxOfflineDays'),
      );
    } catch (e) {
      return SelectiveSync.defaultPreferences;
    }
  }
}

/// Sync connectivity status
enum SyncConnectivity {
  allowed,
  mobileDisabled,
  disabled,
}

/// Extension for Arabic messages
extension SyncConnectivityExtension on SyncConnectivity {
  String get messageAr {
    switch (this) {
      case SyncConnectivity.allowed:
        return 'المزامنة متاحة';
      case SyncConnectivity.mobileDisabled:
        return 'المزامنة معطلة على بيانات الجوال';
      case SyncConnectivity.disabled:
        return 'المزامنة التلقائية معطلة';
    }
  }

  String get messageEn {
    switch (this) {
      case SyncConnectivity.allowed:
        return 'Sync allowed';
      case SyncConnectivity.mobileDisabled:
        return 'Sync disabled on mobile data';
      case SyncConnectivity.disabled:
        return 'Auto-sync disabled';
    }
  }
}
