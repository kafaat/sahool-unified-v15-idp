/// SAHOOL Remote Config Service
/// خدمة الإعدادات البعيدة
///
/// Fetches feature flags from remote sources:
/// - SAHOOL API
/// - Firebase Remote Config (optional)
///
/// Supports:
/// - Polling interval configuration
/// - Caching with TTL
/// - Graceful fallback on failure
/// - User/tenant-specific flags

import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import 'feature_flag.dart';
import 'feature_flags_config.dart';
import '../utils/app_logger.dart';

/// Remote config service interface
/// واجهة خدمة الإعدادات البعيدة
abstract class RemoteConfigService {
  /// Fetch feature flags from remote
  Future<Map<String, bool>> fetchFlags();

  /// Get a specific flag value
  Future<bool?> getFlag(String key);

  /// Activate fetched config
  Future<void> activate();

  /// Set user properties for personalized flags
  Future<void> setUserProperties(Map<String, String> properties);

  /// Dispose resources
  void dispose();
}

/// SAHOOL API Remote Config Implementation
/// تنفيذ الإعدادات البعيدة من API سهول
class SahoolRemoteConfig implements RemoteConfigService {
  final Dio _dio;
  final String _baseUrl;
  final String? _apiKey;
  final Duration _timeout;

  /// Cached flags
  Map<String, bool> _cachedFlags = {};

  /// User properties for personalized flags
  Map<String, String> _userProperties = {};

  /// Last successful fetch
  DateTime? _lastFetch;

  SahoolRemoteConfig({
    required String baseUrl,
    String? apiKey,
    Duration timeout = const Duration(seconds: 10),
    Dio? dio,
  })  : _baseUrl = baseUrl,
        _apiKey = apiKey,
        _timeout = timeout,
        _dio = dio ?? Dio();

  @override
  Future<Map<String, bool>> fetchFlags() async {
    try {
      AppLogger.i('Fetching feature flags from SAHOOL API', tag: 'REMOTE_CONFIG');

      final response = await _dio.get(
        _baseUrl,
        options: Options(
          headers: {
            if (_apiKey != null) 'Authorization': 'Bearer $_apiKey',
            'Content-Type': 'application/json',
            ..._userProperties.map((k, v) => MapEntry('X-User-$k', v)),
          },
          receiveTimeout: _timeout,
          sendTimeout: _timeout,
        ),
        queryParameters: _userProperties,
      );

      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final flags = <String, bool>{};

        // Parse flags from response
        // Expected format: { "flags": { "flag_key": true/false, ... } }
        // or: { "flag_key": true/false, ... }
        final flagsData = data['flags'] ?? data;

        if (flagsData is Map) {
          for (final entry in flagsData.entries) {
            if (entry.value is bool) {
              flags[entry.key as String] = entry.value as bool;
            }
          }
        }

        _cachedFlags = flags;
        _lastFetch = DateTime.now();

        AppLogger.i(
          'Fetched ${flags.length} flags from SAHOOL API',
          tag: 'REMOTE_CONFIG',
        );

        return flags;
      } else {
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          message: 'Unexpected status code: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      AppLogger.e(
        'Failed to fetch flags from SAHOOL API',
        tag: 'REMOTE_CONFIG',
        error: e,
      );
      // Return cached flags on error
      return _cachedFlags;
    } catch (e, stack) {
      AppLogger.e(
        'Error fetching feature flags',
        tag: 'REMOTE_CONFIG',
        error: e,
        stackTrace: stack,
      );
      return _cachedFlags;
    }
  }

  @override
  Future<bool?> getFlag(String key) async {
    // Return from cache if available
    if (_cachedFlags.containsKey(key)) {
      return _cachedFlags[key];
    }

    // Fetch if no cache
    await fetchFlags();
    return _cachedFlags[key];
  }

  @override
  Future<void> activate() async {
    // For SAHOOL API, flags are active immediately after fetch
    // This method is for Firebase Remote Config compatibility
  }

  @override
  Future<void> setUserProperties(Map<String, String> properties) async {
    _userProperties = properties;
  }

  @override
  void dispose() {
    _dio.close();
  }
}

/// Firebase Remote Config Implementation (Optional)
/// تنفيذ Firebase Remote Config (اختياري)
///
/// This is a wrapper that can be used when Firebase is configured.
/// Requires firebase_remote_config package.
class FirebaseRemoteConfigWrapper implements RemoteConfigService {
  final dynamic _firebaseRemoteConfig; // FirebaseRemoteConfig instance
  final Duration _fetchTimeout;
  final Duration _minimumFetchInterval;

  FirebaseRemoteConfigWrapper({
    required dynamic firebaseRemoteConfig,
    Duration fetchTimeout = const Duration(seconds: 10),
    Duration minimumFetchInterval = const Duration(hours: 1),
  })  : _firebaseRemoteConfig = firebaseRemoteConfig,
        _fetchTimeout = fetchTimeout,
        _minimumFetchInterval = minimumFetchInterval;

  @override
  Future<Map<String, bool>> fetchFlags() async {
    try {
      // This would be:
      // await _firebaseRemoteConfig.setConfigSettings(RemoteConfigSettings(
      //   fetchTimeout: _fetchTimeout,
      //   minimumFetchInterval: _minimumFetchInterval,
      // ));
      // await _firebaseRemoteConfig.fetchAndActivate();

      // Get all boolean parameters
      // final parameters = _firebaseRemoteConfig.getAll();
      // return parameters.map((key, value) => MapEntry(key, value.asBool()));

      AppLogger.w(
        'Firebase Remote Config not implemented. Add firebase_remote_config package.',
        tag: 'REMOTE_CONFIG',
      );
      return {};
    } catch (e) {
      AppLogger.e(
        'Failed to fetch Firebase Remote Config',
        tag: 'REMOTE_CONFIG',
        error: e,
      );
      return {};
    }
  }

  @override
  Future<bool?> getFlag(String key) async {
    // Would be: return _firebaseRemoteConfig.getBool(key);
    return null;
  }

  @override
  Future<void> activate() async {
    // Would be: await _firebaseRemoteConfig.activate();
  }

  @override
  Future<void> setUserProperties(Map<String, String> properties) async {
    // Firebase doesn't support user properties in Remote Config directly
    // Use Firebase Analytics for user properties instead
  }

  @override
  void dispose() {
    // Firebase Remote Config doesn't need disposal
  }
}

/// Combined Remote Config Service
/// خدمة الإعدادات البعيدة المجمعة
///
/// Combines multiple remote config sources with fallback logic
class CombinedRemoteConfig implements RemoteConfigService {
  final List<RemoteConfigService> _sources;
  final Duration _pollingInterval;

  Timer? _pollingTimer;
  final List<void Function(Map<String, bool>)> _listeners = [];

  CombinedRemoteConfig({
    required List<RemoteConfigService> sources,
    Duration pollingInterval = const Duration(hours: 1),
  })  : _sources = sources,
        _pollingInterval = pollingInterval;

  /// Start polling for updates
  void startPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(_pollingInterval, (_) {
      fetchFlags();
    });
    AppLogger.i(
      'Started polling with interval: ${_pollingInterval.inMinutes} minutes',
      tag: 'REMOTE_CONFIG',
    );
  }

  /// Stop polling
  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
    AppLogger.i('Stopped polling', tag: 'REMOTE_CONFIG');
  }

  /// Add listener for flag updates
  void addListener(void Function(Map<String, bool>) listener) {
    _listeners.add(listener);
  }

  /// Remove listener
  void removeListener(void Function(Map<String, bool>) listener) {
    _listeners.remove(listener);
  }

  @override
  Future<Map<String, bool>> fetchFlags() async {
    final combinedFlags = <String, bool>{};

    // Fetch from all sources, later sources override earlier
    for (final source in _sources) {
      try {
        final flags = await source.fetchFlags();
        combinedFlags.addAll(flags);
      } catch (e) {
        AppLogger.w(
          'Failed to fetch from source: ${source.runtimeType}',
          tag: 'REMOTE_CONFIG',
        );
      }
    }

    // Notify listeners
    for (final listener in _listeners) {
      try {
        listener(combinedFlags);
      } catch (e) {
        AppLogger.e(
          'Error in remote config listener',
          tag: 'REMOTE_CONFIG',
          error: e,
        );
      }
    }

    return combinedFlags;
  }

  @override
  Future<bool?> getFlag(String key) async {
    // Try sources in reverse order (priority)
    for (final source in _sources.reversed) {
      final value = await source.getFlag(key);
      if (value != null) return value;
    }
    return null;
  }

  @override
  Future<void> activate() async {
    for (final source in _sources) {
      await source.activate();
    }
  }

  @override
  Future<void> setUserProperties(Map<String, String> properties) async {
    for (final source in _sources) {
      await source.setUserProperties(properties);
    }
  }

  @override
  void dispose() {
    stopPolling();
    _listeners.clear();
    for (final source in _sources) {
      source.dispose();
    }
  }
}

/// Remote Config Factory
/// مصنع الإعدادات البعيدة
class RemoteConfigFactory {
  /// Create remote config service based on configuration
  static RemoteConfigService create(FeatureFlagsConfig config, {Dio? dio}) {
    final sources = <RemoteConfigService>[];

    // Add SAHOOL API source if configured
    if (config.remoteConfigUrl != null) {
      sources.add(SahoolRemoteConfig(
        baseUrl: config.remoteConfigUrl!,
        apiKey: config.apiKey,
        dio: dio,
      ));
    }

    // Add Firebase Remote Config if enabled
    // Note: Requires firebase_remote_config package to be added
    if (config.useFirebaseRemoteConfig) {
      // This would require:
      // import 'package:firebase_remote_config/firebase_remote_config.dart';
      // sources.add(FirebaseRemoteConfigWrapper(
      //   firebaseRemoteConfig: FirebaseRemoteConfig.instance,
      // ));
      AppLogger.w(
        'Firebase Remote Config enabled but not implemented',
        tag: 'REMOTE_CONFIG',
      );
    }

    if (sources.isEmpty) {
      // Return a no-op service if no sources configured
      return _NoOpRemoteConfig();
    }

    if (sources.length == 1) {
      return sources.first;
    }

    return CombinedRemoteConfig(
      sources: sources,
      pollingInterval: config.fetchInterval,
    );
  }
}

/// No-op Remote Config (for when no remote config is configured)
/// خدمة الإعدادات البعيدة الفارغة
class _NoOpRemoteConfig implements RemoteConfigService {
  @override
  Future<Map<String, bool>> fetchFlags() async => {};

  @override
  Future<bool?> getFlag(String key) async => null;

  @override
  Future<void> activate() async {}

  @override
  Future<void> setUserProperties(Map<String, String> properties) async {}

  @override
  void dispose() {}
}

/// Remote config response model
/// نموذج استجابة الإعدادات البعيدة
class RemoteConfigResponse {
  final Map<String, bool> flags;
  final DateTime fetchedAt;
  final String? version;
  final Map<String, dynamic>? metadata;

  const RemoteConfigResponse({
    required this.flags,
    required this.fetchedAt,
    this.version,
    this.metadata,
  });

  factory RemoteConfigResponse.fromJson(Map<String, dynamic> json) {
    final flagsData = json['flags'] ?? json;
    final flags = <String, bool>{};

    if (flagsData is Map) {
      for (final entry in flagsData.entries) {
        if (entry.value is bool) {
          flags[entry.key as String] = entry.value as bool;
        }
      }
    }

    return RemoteConfigResponse(
      flags: flags,
      fetchedAt: json['fetched_at'] != null
          ? DateTime.parse(json['fetched_at'] as String)
          : DateTime.now(),
      version: json['version'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'flags': flags,
        'fetched_at': fetchedAt.toIso8601String(),
        if (version != null) 'version': version,
        if (metadata != null) 'metadata': metadata,
      };
}
