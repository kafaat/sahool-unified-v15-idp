import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../utils/app_logger.dart';

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
        AppLogger.i('Environment configuration loaded from .env', tag: 'EnvConfig');
      }
    } catch (e) {
      if (kDebugMode) {
        AppLogger.w('Could not load .env file. Using dart-define/defaults.', tag: 'EnvConfig');
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
      // Host Configuration
      case 'DEV_HOST':
        return const String.fromEnvironment('DEV_HOST');
      case 'PROD_HOST':
        return const String.fromEnvironment('PROD_HOST');
      case 'STAGING_HOST':
        return const String.fromEnvironment('STAGING_HOST');
      // Service Ports
      case 'FIELD_CORE_PORT':
        return const String.fromEnvironment('FIELD_CORE_PORT');
      case 'MARKETPLACE_PORT':
        return const String.fromEnvironment('MARKETPLACE_PORT');
      case 'CHAT_PORT':
        return const String.fromEnvironment('CHAT_PORT');
      case 'SATELLITE_PORT':
        return const String.fromEnvironment('SATELLITE_PORT');
      case 'INDICATORS_PORT':
        return const String.fromEnvironment('INDICATORS_PORT');
      case 'WEATHER_PORT':
        return const String.fromEnvironment('WEATHER_PORT');
      case 'FERTILIZER_PORT':
        return const String.fromEnvironment('FERTILIZER_PORT');
      case 'IRRIGATION_PORT':
        return const String.fromEnvironment('IRRIGATION_PORT');
      case 'CROP_HEALTH_PORT':
        return const String.fromEnvironment('CROP_HEALTH_PORT');
      case 'VIRTUAL_SENSORS_PORT':
        return const String.fromEnvironment('VIRTUAL_SENSORS_PORT');
      case 'COMMUNITY_CHAT_PORT':
        return const String.fromEnvironment('COMMUNITY_CHAT_PORT');
      case 'SPRAY_PORT':
        return const String.fromEnvironment('SPRAY_PORT');
      case 'EQUIPMENT_PORT':
        return const String.fromEnvironment('EQUIPMENT_PORT');
      case 'INVENTORY_PORT':
        return const String.fromEnvironment('INVENTORY_PORT');
      case 'NOTIFICATIONS_PORT':
        return const String.fromEnvironment('NOTIFICATIONS_PORT');
      case 'GATEWAY_PORT':
        return const String.fromEnvironment('GATEWAY_PORT');
      // Service URL Overrides
      case 'MARKETPLACE_URL':
        return const String.fromEnvironment('MARKETPLACE_URL');
      // Maps Configuration
      case 'MAPBOX_ACCESS_TOKEN':
        return const String.fromEnvironment('MAPBOX_ACCESS_TOKEN');
      case 'MAPBOX_STYLE_URL':
        return const String.fromEnvironment('MAPBOX_STYLE_URL');
      case 'MAP_TILE_URL':
        return const String.fromEnvironment('MAP_TILE_URL');
      case 'ENABLE_OFFLINE_MAPS':
        return const String.fromEnvironment('ENABLE_OFFLINE_MAPS');
      // Feature Flags
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
      // Sync Configuration
      case 'SYNC_INTERVAL_SECONDS':
        return const String.fromEnvironment('SYNC_INTERVAL_SECONDS');
      case 'BG_SYNC_INTERVAL_MINUTES':
        return const String.fromEnvironment('BG_SYNC_INTERVAL_MINUTES');
      case 'MAX_RETRY_COUNT':
        return const String.fromEnvironment('MAX_RETRY_COUNT');
      case 'OUTBOX_BATCH_SIZE':
        return const String.fromEnvironment('OUTBOX_BATCH_SIZE');
      // App Info
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

  /// Development host configuration
  /// For Android Emulator: 10.0.2.2
  /// For iOS Simulator: localhost
  /// For Physical Devices: Set your machine's IP (e.g., 192.168.1.5)
  static String get developmentHost {
    return _getString('DEV_HOST', '10.0.2.2');
  }

  /// Production host
  static String get productionHost {
    return _getString('PROD_HOST', 'api.sahool.io');
  }

  /// Staging host
  static String get stagingHost {
    return _getString('STAGING_HOST', 'api-staging.sahool.app');
  }

  /// Get current host based on environment
  static String get apiHost {
    switch (environment) {
      case AppEnvironment.production:
        return productionHost;
      case AppEnvironment.staging:
        return stagingHost;
      case AppEnvironment.development:
        return developmentHost;
    }
  }

  /// Get protocol (https for production/staging, http for development)
  static String get apiProtocol {
    return isProduction || isStaging ? 'https' : 'http';
  }

  static String get apiBaseUrl {
    final url = _getString('API_URL', _getString('API_BASE_URL', ''));
    if (url.isNotEmpty) return url;

    switch (environment) {
      case AppEnvironment.production:
        return 'https://api.sahool.app/api/v1';
      case AppEnvironment.staging:
        return 'https://api-staging.sahool.app/api/v1';
      case AppEnvironment.development:
        return 'http://$developmentHost:8000/api/v1';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Service Ports Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  static int get fieldCorePort => _getInt('FIELD_CORE_PORT', 3000);
  static int get marketplacePort => _getInt('MARKETPLACE_PORT', 3010);
  static int get chatPort => _getInt('CHAT_PORT', 3011);
  static int get satellitePort => _getInt('SATELLITE_PORT', 8090);
  static int get indicatorsPort => _getInt('INDICATORS_PORT', 8091);
  static int get weatherPort => _getInt('WEATHER_PORT', 8092);
  static int get fertilizerPort => _getInt('FERTILIZER_PORT', 8093);
  static int get irrigationPort => _getInt('IRRIGATION_PORT', 8094);
  static int get cropHealthPort => _getInt('CROP_HEALTH_PORT', 8095);
  static int get virtualSensorsPort => _getInt('VIRTUAL_SENSORS_PORT', 8096);
  static int get communityChatPort => _getInt('COMMUNITY_CHAT_PORT', 8097);
  static int get sprayPort => _getInt('SPRAY_PORT', 8098);
  static int get equipmentPort => _getInt('EQUIPMENT_PORT', 8101);
  static int get inventoryPort => _getInt('INVENTORY_PORT', 8102);
  static int get notificationsPort => _getInt('NOTIFICATIONS_PORT', 8110);
  static int get gatewayPort => _getInt('GATEWAY_PORT', 8000);

  // ═══════════════════════════════════════════════════════════════════════════
  // Service URLs
  // ═══════════════════════════════════════════════════════════════════════════

  /// Base URL for field-core service
  static String get fieldCoreUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$fieldCorePort';
  }

  /// Gateway URL (Kong API Gateway)
  static String get gatewayUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$gatewayPort';
  }

  /// Marketplace service URL
  static String get marketplaceUrl {
    final override = _getString('MARKETPLACE_URL', '');
    if (override.isNotEmpty) return override;

    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$marketplacePort';
  }

  /// Chat service URL
  static String get chatUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$chatPort';
  }

  /// Satellite service URL
  static String get satelliteUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$satellitePort';
  }

  /// Indicators service URL
  static String get indicatorsUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$indicatorsPort';
  }

  /// Weather service URL
  static String get weatherUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$weatherPort';
  }

  /// Fertilizer service URL
  static String get fertilizerUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$fertilizerPort';
  }

  /// Irrigation service URL
  static String get irrigationUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$irrigationPort';
  }

  /// Crop health service URL
  static String get cropHealthUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$cropHealthPort';
  }

  /// Virtual sensors service URL
  static String get virtualSensorsUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$virtualSensorsPort';
  }

  /// Community chat service URL
  static String get communityChatUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$communityChatPort';
  }

  /// Spray service URL
  static String get sprayUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$sprayPort';
  }

  /// Equipment service URL
  static String get equipmentUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$equipmentPort';
  }

  /// Inventory service URL
  static String get inventoryUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$inventoryPort';
  }

  /// Notifications service URL
  static String get notificationsUrl {
    if (isProduction || isStaging) {
      return '$apiProtocol://$apiHost';
    }
    return 'http://$developmentHost:$notificationsPort';
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
        return 'ws://10.0.2.2:8081';
    }
  }

  /// WebSocket Gateway URL (alias for wsBaseUrl)
  /// عنوان بوابة WebSocket
  static String get wsGatewayUrl => wsBaseUrl;

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

    final configOutput = '''

╔════════════════════════════════════════════════════════════╗
║           SAHOOL Environment Configuration                 ║
╠════════════════════════════════════════════════════════════╣
║ Environment: ${environment.name.padRight(45)}║
║ Version: ${fullVersion.padRight(49)}║
╠════════════════════════════════════════════════════════════╣
║ API: ${apiBaseUrl.padRight(52)}║
║ WS: ${wsBaseUrl.padRight(53)}║
╠════════════════════════════════════════════════════════════╣
║ Features:                                                  ║
║   Offline: ${(enableOfflineMode ? "✓" : "✗").padRight(47)}║
║   Push: ${(enablePushNotifications ? "✓" : "✗").padRight(50)}║
║   Analytics: ${(enableAnalytics ? "✓" : "✗").padRight(45)}║
╚════════════════════════════════════════════════════════════╝
''';

    AppLogger.d(configOutput, tag: 'EnvConfig');
  }
}
