/// SAHOOL Field App Configuration
/// تكوين تطبيق سهول الميداني
///
/// For physical device development, set DEV_HOST via dart-define:
/// flutter run --dart-define=DEV_HOST=192.168.1.5
class AppConfig {
  // Development host - defaults to Android emulator localhost
  // للأجهزة الحقيقية: استخدم dart-define لتعيين DEV_HOST
  static const String _devHost = String.fromEnvironment('DEV_HOST', defaultValue: '10.0.2.2');

  // API Configuration (via Kong API Gateway)
  static const String apiBaseUrl = 'http://$_devHost:8000/api/v1';
  static const String wsBaseUrl = 'ws://$_devHost:8081'; // WebSocket Gateway port

  // Sync Configuration
  static const Duration syncInterval = Duration(seconds: 20);
  static const int maxRetryCount = 5;
  static const int outboxBatchSize = 50;

  // Cache Configuration
  static const Duration cacheExpiry = Duration(hours: 24);

  // App Info
  static const String appVersion = '15.5.0';
  static const String appName = 'SAHOOL Field';

  // Feature Flags
  static const bool enableOfflineMode = true;
  static const bool enablePhotoCapture = true;
  static const bool enablePushNotifications = false; // PR later
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
    apiUrl: 'http://10.0.2.2:8000/api/v1', // Android emulator via Kong
    wsUrl: 'ws://10.0.2.2:8081', // WebSocket Gateway port
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
