import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// SAHOOL Environment Configuration
/// تكوين البيئة - يدعم dart-define و dotenv
///
/// Priority: dart-define > .env file > default values
///
/// Usage in build:
/// flutter build apk --dart-define=API_URL=https://api.sahool.app
/// flutter build apk --dart-define=ENV=production

enum AppEnvironment { development, staging, production }

class EnvConfig {
  static bool _initialized = false;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Load environment configuration from .env file
  static Future<void> load() async {
    if (_initialized) return;

    try {
      await dotenv.load(fileName: '.env');
      if (kDebugMode) {
        print('✅ Environment configuration loaded from .env');
      }
    } catch (e) {
      if (kDebugMode) {
        print('⚠️ Could not load .env file. Using dart-define/defaults.');
      }
    }

    _initialized = true;

    if (kDebugMode) {
      printConfig();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper to get value with priority: dart-define > dotenv > default
  // ═══════════════════════════════════════════════════════════════════════════

  static String _getString(String key, String defaultValue) {
    // 1. Check dart-define first (using predefined constants)
    final dartDefine = _getDartDefine(key);
    if (dartDefine.isNotEmpty) return dartDefine;

    // 2. Check dotenv
    try {
      final dotenvValue = dotenv.maybeGet(key);
      if (dotenvValue != null && dotenvValue.isNotEmpty) return dotenvValue;
    } catch (_) {}

    // 3. Return default
    return defaultValue;
  }

  /// Get dart-define value for known keys (must be const at compile time)
  static String _getDartDefine(String key) {
    switch (key) {
      case 'ENV':
        return const String.fromEnvironment('ENV');
      case 'ENVIRONMENT':
        return const String.fromEnvironment('ENVIRONMENT');
      case 'API_URL':
        return const String.fromEnvironment('API_URL');
      case 'API_BASE_URL':
        return const String.fromEnvironment('API_BASE_URL');
      case 'WS_URL':
        return const String.fromEnvironment('WS_URL');
      case 'WS_GATEWAY_URL':
        return const String.fromEnvironment('WS_GATEWAY_URL');
      case 'MAPBOX_ACCESS_TOKEN':
        return const String.fromEnvironment('MAPBOX_ACCESS_TOKEN');
      case 'MAPBOX_STYLE_URL':
        return const String.fromEnvironment('MAPBOX_STYLE_URL');
      case 'MAP_TILE_URL':
        return const String.fromEnvironment('MAP_TILE_URL');
      case 'ENABLE_OFFLINE_MAPS':
        return const String.fromEnvironment('ENABLE_OFFLINE_MAPS');
      case 'ENABLE_OFFLINE_MODE':
        return const String.fromEnvironment('ENABLE_OFFLINE_MODE');
      case 'ENABLE_BACKGROUND_SYNC':
        return const String.fromEnvironment('ENABLE_BACKGROUND_SYNC');
      case 'ENABLE_CAMERA':
        return const String.fromEnvironment('ENABLE_CAMERA');
      case 'ENABLE_PUSH':
        return const String.fromEnvironment('ENABLE_PUSH');
      case 'ENABLE_ANALYTICS':
        return const String.fromEnvironment('ENABLE_ANALYTICS');
      case 'ENABLE_CRASH_REPORTING':
        return const String.fromEnvironment('ENABLE_CRASH_REPORTING');
      case 'ENABLE_EDGE_AI':
        return const String.fromEnvironment('ENABLE_EDGE_AI');
      case 'ENABLE_VOICE':
        return const String.fromEnvironment('ENABLE_VOICE');
      case 'ENABLE_AR':
        return const String.fromEnvironment('ENABLE_AR');
      case 'SYNC_INTERVAL_SECONDS':
        return const String.fromEnvironment('SYNC_INTERVAL_SECONDS');
      case 'BG_SYNC_INTERVAL_MINUTES':
        return const String.fromEnvironment('BG_SYNC_INTERVAL_MINUTES');
      case 'MAX_RETRY_COUNT':
        return const String.fromEnvironment('MAX_RETRY_COUNT');
      case 'OUTBOX_BATCH_SIZE':
        return const String.fromEnvironment('OUTBOX_BATCH_SIZE');
      case 'APP_NAME':
        return const String.fromEnvironment('APP_NAME');
      case 'APP_VERSION':
        return const String.fromEnvironment('APP_VERSION');
      case 'BUILD_NUMBER':
        return const String.fromEnvironment('BUILD_NUMBER');
      case 'DEFAULT_TENANT_ID':
        return const String.fromEnvironment('DEFAULT_TENANT_ID');
      case 'AI_SERVICE_URL':
        return const String.fromEnvironment('AI_SERVICE_URL');
      default:
        return '';
    }
  }

  static int _getInt(String key, int defaultValue) {
    final value = _getString(key, '');
    if (value.isEmpty) return defaultValue;
    return int.tryParse(value) ?? defaultValue;
  }

  static bool _getBool(String key, bool defaultValue) {
    final value = _getString(key, '').toLowerCase();
    if (value.isEmpty) return defaultValue;
    return value == 'true' || value == '1';
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Environment Detection
  // ═══════════════════════════════════════════════════════════════════════════

  static AppEnvironment get environment {
    final env = _getString('ENV', _getString('ENVIRONMENT', 'development'));
    switch (env.toLowerCase()) {
      case 'production':
      case 'prod':
        return AppEnvironment.production;
      case 'staging':
      case 'stage':
        return AppEnvironment.staging;
      default:
        return AppEnvironment.development;
    }
  }

  static bool get isProduction => environment == AppEnvironment.production;
  static bool get isStaging => environment == AppEnvironment.staging;
  static bool get isDevelopment => environment == AppEnvironment.development;
  static bool get isDebugMode => kDebugMode;

  // ═══════════════════════════════════════════════════════════════════════════
  // API Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static String get apiBaseUrl {
    final url = _getString('API_URL', _getString('API_BASE_URL', ''));
    if (url.isNotEmpty) return url;

    switch (environment) {
      case AppEnvironment.production:
        return 'https://api.sahool.app/api/v1';
      case AppEnvironment.staging:
        return 'https://api-staging.sahool.app/api/v1';
      case AppEnvironment.development:
        return 'http://10.0.2.2:8000/api/v1';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // WebSocket Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static String get wsBaseUrl {
    final url = _getString('WS_URL', _getString('WS_GATEWAY_URL', ''));
    if (url.isNotEmpty) return url;

    switch (environment) {
      case AppEnvironment.production:
        return 'wss://ws.sahool.app';
      case AppEnvironment.staging:
        return 'wss://ws-staging.sahool.app';
      case AppEnvironment.development:
        return 'ws://10.0.2.2:8090';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Maps Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static String get mapboxAccessToken =>
      _getString('MAPBOX_ACCESS_TOKEN', '');

  static String get mapboxStyleUrl => _getString(
        'MAPBOX_STYLE_URL',
        'mapbox://styles/mapbox/satellite-streets-v12',
      );

  static String get mapTileUrl => _getString(
        'MAP_TILE_URL',
        'https://tiles.sahool.app/{z}/{x}/{y}.png',
      );

  static bool get enableOfflineMaps => _getBool('ENABLE_OFFLINE_MAPS', true);

  // ═══════════════════════════════════════════════════════════════════════════
  // Feature Flags
  // ═══════════════════════════════════════════════════════════════════════════

  static bool get enableOfflineMode =>
      _getBool('ENABLE_OFFLINE_MODE', true);

  static bool get enableBackgroundSync =>
      _getBool('ENABLE_BACKGROUND_SYNC', true);

  static bool get enableCamera =>
      _getBool('ENABLE_CAMERA', true);

  static bool get enablePushNotifications {
    // Disabled in development to avoid FCM setup requirements
    if (isDevelopment) return false;
    // Enabled by default in production/staging
    return _getBool('ENABLE_PUSH', true);
  }

  static bool get enableAnalytics {
    if (!isProduction) return false;
    return _getBool('ENABLE_ANALYTICS', true);
  }

  static bool get enableCrashReporting {
    if (isDevelopment) return false;
    return _getBool('ENABLE_CRASH_REPORTING', true);
  }

  static bool get enableEdgeAI => _getBool('ENABLE_EDGE_AI', false);

  static bool get enableVoiceCommands => _getBool('ENABLE_VOICE', false);

  static bool get enableARFeatures => _getBool('ENABLE_AR', false);

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static Duration get syncInterval =>
      Duration(seconds: _getInt('SYNC_INTERVAL_SECONDS', 30));

  static Duration get backgroundSyncInterval =>
      Duration(minutes: _getInt('BG_SYNC_INTERVAL_MINUTES', 15));

  static int get maxRetryCount => _getInt('MAX_RETRY_COUNT', 5);

  static int get outboxBatchSize => _getInt('OUTBOX_BATCH_SIZE', 50);

  // ═══════════════════════════════════════════════════════════════════════════
  // Cache Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static Duration get cacheExpiry =>
      Duration(hours: _getInt('CACHE_EXPIRY_HOURS', 24));

  static Duration get imageCacheExpiry =>
      Duration(days: _getInt('IMAGE_CACHE_DAYS', 7));

  // ═══════════════════════════════════════════════════════════════════════════
  // Timeouts
  // ═══════════════════════════════════════════════════════════════════════════

  static Duration get connectTimeout =>
      Duration(seconds: _getInt('CONNECT_TIMEOUT_SECONDS', 10));

  static Duration get receiveTimeout =>
      Duration(seconds: _getInt('RECEIVE_TIMEOUT_SECONDS', 30));

  // ═══════════════════════════════════════════════════════════════════════════
  // App Info
  // ═══════════════════════════════════════════════════════════════════════════

  static String get appName => _getString('APP_NAME', 'SAHOOL Field');

  static String get appVersion => _getString('APP_VERSION', '15.4.0');

  static String get buildNumber => _getString('BUILD_NUMBER', '1');

  static String get fullVersion => '$appVersion+$buildNumber';

  // ═══════════════════════════════════════════════════════════════════════════
  // Tenant Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static String get defaultTenantId =>
      _getString('DEFAULT_TENANT_ID', 'sahool-demo');

  // ═══════════════════════════════════════════════════════════════════════════
  // AI/ML Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static String get aiServiceUrl {
    final url = _getString('AI_SERVICE_URL', '');
    if (url.isNotEmpty) return url;

    switch (environment) {
      case AppEnvironment.production:
        return 'https://ai.sahool.app';
      case AppEnvironment.staging:
        return 'https://ai-staging.sahool.app';
      default:
        return 'http://10.0.2.2:8085';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Debug Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  static Map<String, dynamic> toDebugMap() {
    return {
      'environment': environment.name,
      'apiBaseUrl': apiBaseUrl,
      'wsBaseUrl': wsBaseUrl,
      'appVersion': fullVersion,
      'features': {
        'offlineMode': enableOfflineMode,
        'backgroundSync': enableBackgroundSync,
        'pushNotifications': enablePushNotifications,
        'analytics': enableAnalytics,
        'crashReporting': enableCrashReporting,
        'offlineMaps': enableOfflineMaps,
        'edgeAI': enableEdgeAI,
        'voiceCommands': enableVoiceCommands,
        'arFeatures': enableARFeatures,
      },
      'sync': {
        'interval': '${syncInterval.inSeconds}s',
        'backgroundInterval': '${backgroundSyncInterval.inMinutes}m',
        'maxRetry': maxRetryCount,
        'batchSize': outboxBatchSize,
      },
      'timeouts': {
        'connect': '${connectTimeout.inSeconds}s',
        'receive': '${receiveTimeout.inSeconds}s',
      },
    };
  }

  static void printConfig() {
    if (!kDebugMode) return;

    print('');
    print('╔════════════════════════════════════════════════════════════╗');
    print('║           SAHOOL Environment Configuration                 ║');
    print('╠════════════════════════════════════════════════════════════╣');
    print('║ Environment: ${environment.name.padRight(45)}║');
    print('║ Version: ${fullVersion.padRight(49)}║');
    print('╠════════════════════════════════════════════════════════════╣');
    print('║ API: ${apiBaseUrl.padRight(52)}║');
    print('║ WS: ${wsBaseUrl.padRight(53)}║');
    print('╠════════════════════════════════════════════════════════════╣');
    print('║ Features:                                                  ║');
    print('║   Offline: ${(enableOfflineMode ? "✓" : "✗").padRight(47)}║');
    print('║   Push: ${(enablePushNotifications ? "✓" : "✗").padRight(50)}║');
    print('║   Analytics: ${(enableAnalytics ? "✓" : "✗").padRight(45)}║');
    print('╚════════════════════════════════════════════════════════════╝');
    print('');
  }
}
