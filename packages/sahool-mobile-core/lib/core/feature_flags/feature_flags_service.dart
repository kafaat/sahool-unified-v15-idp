/// SAHOOL Feature Flags Service
/// خدمة أعلام الميزات
///
/// Manages feature flags with support for:
/// - Remote configuration from API
/// - Local caching for offline support
/// - Override flags for testing
/// - Flag change listeners
/// - Package-based defaults
library;

import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'feature_flag.dart';
import 'feature_flags_config.dart';
import 'remote_config.dart';
import '../utils/app_logger.dart';

/// Storage keys for feature flags
class FeatureFlagKeys {
  static const String flagsCache = 'sahool_feature_flags_cache';
  static const String flagsOverrides = 'sahool_feature_flags_overrides';
  static const String lastFetchTime = 'sahool_feature_flags_last_fetch';
  static const String userPackage = 'sahool_user_package';
}

/// Feature flag change event
class FeatureFlagChangeEvent {
  final FeatureFlag flag;
  final bool previousValue;
  final bool newValue;
  final String source;
  final DateTime timestamp;

  const FeatureFlagChangeEvent({
    required this.flag,
    required this.previousValue,
    required this.newValue,
    required this.source,
    required this.timestamp,
  });

  @override
  String toString() =>
      'FeatureFlagChangeEvent(${flag.key}: $previousValue -> $newValue, source: $source)';
}

/// Feature flags service
/// خدمة أعلام الميزات
class FeatureFlagsService extends ChangeNotifier {
  final RemoteConfigService? _remoteConfig;
  final FeatureFlagsConfig _config;

  /// Cached flag values
  final Map<String, FeatureFlagValue> _flagValues = {};

  /// Override flags (for testing/debugging)
  final Map<String, bool> _overrides = {};

  /// Flag change listeners
  final List<void Function(FeatureFlagChangeEvent)> _changeListeners = [];

  /// Last fetch timestamp
  DateTime? _lastFetchTime;

  /// Current user's subscription package
  SubscriptionPackage _currentPackage = SubscriptionPackage.free;

  /// User role for role-based flags
  String? _userRole;

  /// Is service initialized
  bool _isInitialized = false;

  /// Is fetching from remote
  bool _isFetching = false;

  FeatureFlagsService({
    RemoteConfigService? remoteConfig,
    FeatureFlagsConfig? config,
  })  : _remoteConfig = remoteConfig,
        _config = config ?? FeatureFlagsConfig.development();

  /// Get if service is initialized
  bool get isInitialized => _isInitialized;

  /// Get if currently fetching
  bool get isFetching => _isFetching;

  /// Get current subscription package
  SubscriptionPackage get currentPackage => _currentPackage;

  /// Get last fetch time
  DateTime? get lastFetchTime => _lastFetchTime;

  /// Get all flag values
  Map<String, FeatureFlagValue> get allFlags => Map.unmodifiable(_flagValues);

  /// Get all overrides
  Map<String, bool> get overrides => Map.unmodifiable(_overrides);

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the feature flags service
  /// تهيئة خدمة أعلام الميزات
  Future<void> initialize({
    SubscriptionPackage? package,
    String? userRole,
  }) async {
    if (_isInitialized) return;

    AppLogger.i('Initializing FeatureFlagsService', tag: 'FEATURE_FLAGS');

    try {
      // Set user package and role
      if (package != null) {
        _currentPackage = package;
      }
      if (userRole != null) {
        _userRole = userRole;
      }

      // Load cached values
      await _loadFromCache();

      // Load overrides
      await _loadOverrides();

      // Initialize defaults if no cache
      if (_flagValues.isEmpty) {
        _initializeDefaults();
      }

      _isInitialized = true;

      AppLogger.i(
        'FeatureFlagsService initialized with ${_flagValues.length} flags',
        tag: 'FEATURE_FLAGS',
      );

      notifyListeners();
    } catch (e, stack) {
      AppLogger.e(
        'Failed to initialize FeatureFlagsService',
        tag: 'FEATURE_FLAGS',
        error: e,
        stackTrace: stack,
      );
      // Initialize with defaults on error
      _initializeDefaults();
      _isInitialized = true;
    }
  }

  /// Initialize default flag values based on package
  void _initializeDefaults() {
    for (final flag in FeatureFlag.values) {
      _flagValues[flag.key] = FeatureFlagValue(
        flag: flag,
        enabled: _getPackageDefault(flag),
        lastUpdated: DateTime.now(),
        source: 'default',
      );
    }
  }

  /// Get default value based on package
  bool _getPackageDefault(FeatureFlag flag) {
    return flag.isEnabledForPackage(_currentPackage);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Flag Checking
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if a feature is enabled
  /// التحقق مما إذا كانت الميزة مفعلة
  bool isEnabled(FeatureFlag flag) {
    // Check overrides first (highest priority)
    if (_overrides.containsKey(flag.key)) {
      return _overrides[flag.key]!;
    }

    // Check cached value
    final cached = _flagValues[flag.key];
    if (cached != null) {
      return cached.enabled;
    }

    // Fall back to package default
    return _getPackageDefault(flag);
  }

  /// Check if a feature is enabled by key
  /// التحقق مما إذا كانت الميزة مفعلة بالمفتاح
  bool isEnabledByKey(String key) {
    final flag = FeatureFlag.fromKey(key);
    if (flag == null) {
      AppLogger.w('Unknown feature flag key: $key', tag: 'FEATURE_FLAGS');
      return false;
    }
    return isEnabled(flag);
  }

  /// Get feature flag value with metadata
  FeatureFlagValue? getFlagValue(FeatureFlag flag) {
    return _flagValues[flag.key];
  }

  /// Check multiple flags (all must be enabled)
  bool allEnabled(List<FeatureFlag> flags) {
    return flags.every(isEnabled);
  }

  /// Check multiple flags (any must be enabled)
  bool anyEnabled(List<FeatureFlag> flags) {
    return flags.any(isEnabled);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Remote Fetching
  // ═══════════════════════════════════════════════════════════════════════════

  /// Fetch flags from remote config
  /// جلب الأعلام من الإعدادات البعيدة
  Future<bool> fetchFromRemote({bool force = false}) async {
    if (_remoteConfig == null) {
      AppLogger.d('No remote config service configured', tag: 'FEATURE_FLAGS');
      return false;
    }

    // Check if we should fetch
    if (!force && _lastFetchTime != null) {
      final timeSinceFetch = DateTime.now().difference(_lastFetchTime!);
      if (timeSinceFetch < _config.fetchInterval) {
        AppLogger.d(
          'Skipping fetch, last fetch was ${timeSinceFetch.inMinutes} minutes ago',
          tag: 'FEATURE_FLAGS',
        );
        return false;
      }
    }

    if (_isFetching) {
      AppLogger.d('Already fetching flags', tag: 'FEATURE_FLAGS');
      return false;
    }

    _isFetching = true;
    notifyListeners();

    try {
      AppLogger.i('Fetching feature flags from remote', tag: 'FEATURE_FLAGS');

      final remoteFlags = await _remoteConfig.fetchFlags();

      if (remoteFlags.isNotEmpty) {
        await _applyRemoteFlags(remoteFlags);
        _lastFetchTime = DateTime.now();
        await _saveToCache();

        AppLogger.i(
          'Fetched ${remoteFlags.length} flags from remote',
          tag: 'FEATURE_FLAGS',
        );
        return true;
      }
    } catch (e, stack) {
      AppLogger.e(
        'Failed to fetch feature flags from remote',
        tag: 'FEATURE_FLAGS',
        error: e,
        stackTrace: stack,
      );
    } finally {
      _isFetching = false;
      notifyListeners();
    }

    return false;
  }

  /// Apply remote flags
  Future<void> _applyRemoteFlags(Map<String, bool> remoteFlags) async {
    for (final entry in remoteFlags.entries) {
      final flag = FeatureFlag.fromKey(entry.key);
      if (flag == null) continue;

      final previousValue = isEnabled(flag);
      final newValue = entry.value;

      _flagValues[flag.key] = FeatureFlagValue(
        flag: flag,
        enabled: newValue,
        lastUpdated: DateTime.now(),
        source: 'remote',
      );

      // Notify listeners if value changed
      if (previousValue != newValue) {
        _notifyFlagChange(FeatureFlagChangeEvent(
          flag: flag,
          previousValue: previousValue,
          newValue: newValue,
          source: 'remote',
          timestamp: DateTime.now(),
        ));
      }
    }
    notifyListeners();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Overrides (Testing/Debugging)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set an override for a feature flag
  /// تعيين تجاوز لعلم ميزة
  Future<void> setOverride(FeatureFlag flag, bool enabled) async {
    final previousValue = isEnabled(flag);
    _overrides[flag.key] = enabled;
    await _saveOverrides();

    if (previousValue != enabled) {
      _notifyFlagChange(FeatureFlagChangeEvent(
        flag: flag,
        previousValue: previousValue,
        newValue: enabled,
        source: 'override',
        timestamp: DateTime.now(),
      ));
    }

    notifyListeners();

    AppLogger.i(
      'Override set: ${flag.key} = $enabled',
      tag: 'FEATURE_FLAGS',
    );
  }

  /// Remove an override for a feature flag
  /// إزالة تجاوز لعلم ميزة
  Future<void> removeOverride(FeatureFlag flag) async {
    if (!_overrides.containsKey(flag.key)) return;

    final previousValue = _overrides[flag.key]!;
    _overrides.remove(flag.key);
    await _saveOverrides();

    final newValue = isEnabled(flag);
    if (previousValue != newValue) {
      _notifyFlagChange(FeatureFlagChangeEvent(
        flag: flag,
        previousValue: previousValue,
        newValue: newValue,
        source: 'override_removed',
        timestamp: DateTime.now(),
      ));
    }

    notifyListeners();

    AppLogger.i(
      'Override removed: ${flag.key}',
      tag: 'FEATURE_FLAGS',
    );
  }

  /// Clear all overrides
  /// مسح جميع التجاوزات
  Future<void> clearAllOverrides() async {
    final previousOverrides = Map<String, bool>.from(_overrides);
    _overrides.clear();
    await _saveOverrides();

    for (final entry in previousOverrides.entries) {
      final flag = FeatureFlag.fromKey(entry.key);
      if (flag == null) continue;

      final newValue = isEnabled(flag);
      if (entry.value != newValue) {
        _notifyFlagChange(FeatureFlagChangeEvent(
          flag: flag,
          previousValue: entry.value,
          newValue: newValue,
          source: 'override_cleared',
          timestamp: DateTime.now(),
        ));
      }
    }

    notifyListeners();

    AppLogger.i('All overrides cleared', tag: 'FEATURE_FLAGS');
  }

  /// Check if a flag has an override
  bool hasOverride(FeatureFlag flag) => _overrides.containsKey(flag.key);

  // ═══════════════════════════════════════════════════════════════════════════
  // Package Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Update user's subscription package
  /// تحديث باقة اشتراك المستخدم
  Future<void> updatePackage(SubscriptionPackage package) async {
    if (_currentPackage == package) return;

    final previousPackage = _currentPackage;
    _currentPackage = package;

    // Update flags that depend on package
    for (final flag in FeatureFlag.values) {
      final previousValue = flag.isEnabledForPackage(previousPackage);
      final newValue = flag.isEnabledForPackage(package);

      // Only update if not overridden and not from remote
      final cached = _flagValues[flag.key];
      if (cached?.source != 'remote' && !_overrides.containsKey(flag.key)) {
        if (previousValue != newValue) {
          _flagValues[flag.key] = FeatureFlagValue(
            flag: flag,
            enabled: newValue,
            lastUpdated: DateTime.now(),
            source: 'package',
          );

          _notifyFlagChange(FeatureFlagChangeEvent(
            flag: flag,
            previousValue: previousValue,
            newValue: newValue,
            source: 'package_change',
            timestamp: DateTime.now(),
          ));
        }
      }
    }

    await _saveToCache();
    notifyListeners();

    AppLogger.i(
      'Package updated: ${previousPackage.value} -> ${package.value}',
      tag: 'FEATURE_FLAGS',
    );
  }

  /// Update user role
  Future<void> updateUserRole(String role) async {
    _userRole = role;
    notifyListeners();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Change Listeners
  // ═══════════════════════════════════════════════════════════════════════════

  /// Add a flag change listener
  /// إضافة مستمع لتغييرات الأعلام
  void addFlagChangeListener(void Function(FeatureFlagChangeEvent) listener) {
    _changeListeners.add(listener);
  }

  /// Remove a flag change listener
  /// إزالة مستمع لتغييرات الأعلام
  void removeFlagChangeListener(
      void Function(FeatureFlagChangeEvent) listener) {
    _changeListeners.remove(listener);
  }

  /// Notify all change listeners
  void _notifyFlagChange(FeatureFlagChangeEvent event) {
    AppLogger.d('Flag changed: $event', tag: 'FEATURE_FLAGS');
    for (final listener in _changeListeners) {
      try {
        listener(event);
      } catch (e) {
        AppLogger.e(
          'Error in flag change listener',
          tag: 'FEATURE_FLAGS',
          error: e,
        );
      }
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Persistence
  // ═══════════════════════════════════════════════════════════════════════════

  /// Load flags from local cache
  Future<void> _loadFromCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Load package
      final packageStr = prefs.getString(FeatureFlagKeys.userPackage);
      if (packageStr != null) {
        _currentPackage = SubscriptionPackage.fromString(packageStr);
      }

      // Load last fetch time
      final lastFetchStr = prefs.getString(FeatureFlagKeys.lastFetchTime);
      if (lastFetchStr != null) {
        _lastFetchTime = DateTime.parse(lastFetchStr);
      }

      // Load cached flags
      final cacheStr = prefs.getString(FeatureFlagKeys.flagsCache);
      if (cacheStr != null) {
        final cacheData = jsonDecode(cacheStr) as Map<String, dynamic>;
        for (final entry in cacheData.entries) {
          try {
            final value = FeatureFlagValue.fromJson(
              entry.value as Map<String, dynamic>,
            );
            _flagValues[entry.key] = value;
          } catch (e) {
            AppLogger.w(
              'Failed to parse cached flag: ${entry.key}',
              tag: 'FEATURE_FLAGS',
            );
          }
        }
      }

      AppLogger.d(
        'Loaded ${_flagValues.length} flags from cache',
        tag: 'FEATURE_FLAGS',
      );
    } catch (e, stack) {
      AppLogger.e(
        'Failed to load flags from cache',
        tag: 'FEATURE_FLAGS',
        error: e,
        stackTrace: stack,
      );
    }
  }

  /// Save flags to local cache
  Future<void> _saveToCache() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Save package
      await prefs.setString(FeatureFlagKeys.userPackage, _currentPackage.value);

      // Save last fetch time
      if (_lastFetchTime != null) {
        await prefs.setString(
          FeatureFlagKeys.lastFetchTime,
          _lastFetchTime!.toIso8601String(),
        );
      }

      // Save flags
      final cacheData = <String, dynamic>{};
      for (final entry in _flagValues.entries) {
        cacheData[entry.key] = entry.value.toJson();
      }
      await prefs.setString(FeatureFlagKeys.flagsCache, jsonEncode(cacheData));

      AppLogger.d(
        'Saved ${_flagValues.length} flags to cache',
        tag: 'FEATURE_FLAGS',
      );
    } catch (e, stack) {
      AppLogger.e(
        'Failed to save flags to cache',
        tag: 'FEATURE_FLAGS',
        error: e,
        stackTrace: stack,
      );
    }
  }

  /// Load overrides from storage
  Future<void> _loadOverrides() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final overridesStr = prefs.getString(FeatureFlagKeys.flagsOverrides);
      if (overridesStr != null) {
        final overridesData = jsonDecode(overridesStr) as Map<String, dynamic>;
        _overrides.clear();
        for (final entry in overridesData.entries) {
          _overrides[entry.key] = entry.value as bool;
        }
      }

      AppLogger.d(
        'Loaded ${_overrides.length} overrides',
        tag: 'FEATURE_FLAGS',
      );
    } catch (e) {
      AppLogger.e(
        'Failed to load overrides',
        tag: 'FEATURE_FLAGS',
        error: e,
      );
    }
  }

  /// Save overrides to storage
  Future<void> _saveOverrides() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
        FeatureFlagKeys.flagsOverrides,
        jsonEncode(_overrides),
      );
    } catch (e) {
      AppLogger.e(
        'Failed to save overrides',
        tag: 'FEATURE_FLAGS',
        error: e,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Debug & Testing
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get debug info
  Map<String, dynamic> getDebugInfo() {
    return {
      'isInitialized': _isInitialized,
      'isFetching': _isFetching,
      'currentPackage': _currentPackage.value,
      'userRole': _userRole,
      'lastFetchTime': _lastFetchTime?.toIso8601String(),
      'flagCount': _flagValues.length,
      'overrideCount': _overrides.length,
      'flags': _flagValues.map((k, v) => MapEntry(k, v.toJson())),
      'overrides': _overrides,
    };
  }

  /// Reset service state (for testing)
  @visibleForTesting
  Future<void> reset() async {
    _flagValues.clear();
    _overrides.clear();
    _changeListeners.clear();
    _lastFetchTime = null;
    _currentPackage = SubscriptionPackage.free;
    _userRole = null;
    _isInitialized = false;
    _isFetching = false;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(FeatureFlagKeys.flagsCache);
    await prefs.remove(FeatureFlagKeys.flagsOverrides);
    await prefs.remove(FeatureFlagKeys.lastFetchTime);
    await prefs.remove(FeatureFlagKeys.userPackage);

    notifyListeners();
  }

  @override
  void dispose() {
    _changeListeners.clear();
    super.dispose();
  }
}
