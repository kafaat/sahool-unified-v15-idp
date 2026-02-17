/// SAHOOL Field App Configuration
<<<<<<< HEAD
/// @deprecated Use EnvConfig instead for environment-specific configuration
class AppConfig {
  // API Configuration (via Kong API Gateway on port 8000)
  // For development with Android Emulator, use 10.0.2.2 (host machine)
  // For iOS Simulator, use localhost
  // For real devices, set your machine's IP address
  /// @deprecated Use EnvConfig.apiBaseUrl instead
  static const String apiBaseUrl = 'http://192.168.8.205:8000/api/v1';
  /// @deprecated Use EnvConfig.wsBaseUrl instead
  static const String wsBaseUrl = 'ws://192.168.8.205:8081';

  // Sync Configuration
  static const Duration syncInterval = Duration(seconds: 20);
  static const int maxRetryCount = 5;
  static const int outboxBatchSize = 50;

  // Cache Configuration
  static const Duration cacheExpiry = Duration(hours: 24);

  // App Info
  static const String appVersion = '15.3.0';
  static const String appName = 'SAHOOL Field';

  // Feature Flags
  static const bool enableOfflineMode = true;
  static const bool enablePhotoCapture = true;
  static const bool enablePushNotifications = true; // Enabled for production
  static const bool enableBackgroundSync = true;

  // Debug Mode
  static const bool isDebug = bool.fromEnvironment('DEBUG', defaultValue: true);

  // Tenant (will be dynamic later)
  static const String defaultTenantId = 'tenant_1';

  // Background Sync Configuration
  static const Duration backgroundSyncInterval = Duration(minutes: 15);
  static const int backgroundSyncBatchSize = 25;
}

/// Environment Configuration
/// @deprecated Use core/config/env_config.dart instead
enum Environment { development, staging, production }

/// @deprecated Use core/config/env_config.dart EnvConfig instead
class EnvConfig {
  final Environment env;
  final String apiUrl;
  final String wsUrl;

  const EnvConfig({
    required this.env,
    required this.apiUrl,
    required this.wsUrl,
  });

  /// @deprecated Use core/config/env_config.dart instead
  static const development = EnvConfig(
    env: Environment.development,
    apiUrl: 'http://10.0.2.2:8000/api/v1', // Android emulator via Kong Gateway
    wsUrl: 'ws://10.0.2.2:8081', // WebSocket Gateway (ws-gateway)
  );

  /// @deprecated Use core/config/env_config.dart instead
  static const staging = EnvConfig(
    env: Environment.staging,
    apiUrl: 'https://api-staging.sahool.app/api/v1',
    wsUrl: 'wss://ws-staging.sahool.app',
  );

  /// @deprecated Use core/config/env_config.dart instead
  static const production = EnvConfig(
    env: Environment.production,
    apiUrl: 'https://api.sahool.app/api/v1',
    wsUrl: 'wss://ws.sahool.app',
  );
}
=======
/// @deprecated This file is deprecated. Use EnvConfig from env_config.dart instead.
/// All hardcoded URLs (192.168.8.205) have been removed.
/// Import 'env_config.dart' and use EnvConfig class directly.
library;

import 'env_config.dart' as env;

/// @deprecated Use EnvConfig from env_config.dart instead
class AppConfig {
  /// @deprecated Use EnvConfig.apiBaseUrl
  static String get apiBaseUrl => env.EnvConfig.apiBaseUrl;

  /// @deprecated Use EnvConfig.wsBaseUrl
  static String get wsBaseUrl => env.EnvConfig.wsBaseUrl;

  static Duration get syncInterval => env.EnvConfig.syncInterval;
  static int get maxRetryCount => env.EnvConfig.maxRetryCount;
  static int get outboxBatchSize => env.EnvConfig.outboxBatchSize;
  static Duration get cacheExpiry => env.EnvConfig.cacheExpiry;
  static String get appVersion => env.EnvConfig.appVersion;
  static String get appName => env.EnvConfig.appName;
  static bool get enableOfflineMode => env.EnvConfig.enableOfflineMode;
  static bool get enablePhotoCapture => env.EnvConfig.enableCamera;
  static bool get enablePushNotifications => env.EnvConfig.enablePushNotifications;
  static bool get enableBackgroundSync => env.EnvConfig.enableBackgroundSync;
  static bool get isDebug => env.EnvConfig.isDebugMode;
  static String get defaultTenantId => env.EnvConfig.defaultTenantId;
  static Duration get backgroundSyncInterval => env.EnvConfig.backgroundSyncInterval;
  static const int backgroundSyncBatchSize = 25;
}
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
