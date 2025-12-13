/// SAHOOL Field App Configuration
class AppConfig {
  // API Configuration
  static const String apiBaseUrl = 'http://localhost:8080/api/v1';
  static const String wsBaseUrl = 'ws://localhost:8081';

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
  static const bool enablePushNotifications = false; // PR later

  // Tenant (will be dynamic later)
  static const String defaultTenantId = 'tenant_1';
}

/// Environment Configuration
enum Environment { development, staging, production }

class EnvConfig {
  final Environment env;
  final String apiUrl;
  final String wsUrl;

  const EnvConfig({
    required this.env,
    required this.apiUrl,
    required this.wsUrl,
  });

  static const development = EnvConfig(
    env: Environment.development,
    apiUrl: 'http://10.0.2.2:8080/api/v1', // Android emulator localhost
    wsUrl: 'ws://10.0.2.2:8081',
  );

  static const staging = EnvConfig(
    env: Environment.staging,
    apiUrl: 'https://api-staging.sahool.app/api/v1',
    wsUrl: 'wss://ws-staging.sahool.app',
  );

  static const production = EnvConfig(
    env: Environment.production,
    apiUrl: 'https://api.sahool.app/api/v1',
    wsUrl: 'wss://ws.sahool.app',
  );
}
