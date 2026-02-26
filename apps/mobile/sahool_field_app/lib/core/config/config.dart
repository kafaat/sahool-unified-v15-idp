/// SAHOOL Field App Configuration
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
  static bool get enablePushNotifications =>
      env.EnvConfig.enablePushNotifications;
  static bool get enableBackgroundSync => env.EnvConfig.enableBackgroundSync;
  static bool get isDebug => env.EnvConfig.isDebugMode;
  static String get defaultTenantId => env.EnvConfig.defaultTenantId;
  static Duration get backgroundSyncInterval =>
      env.EnvConfig.backgroundSyncInterval;
  static const int backgroundSyncBatchSize = 25;
}
