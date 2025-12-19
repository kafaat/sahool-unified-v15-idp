import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Environment Configuration Loader
/// Loads configuration from .env file
class EnvConfig {
  // API Configuration
  static String get apiBaseUrl =>
      dotenv.get('API_BASE_URL', fallback: 'http://10.0.2.2:8000');
  static String get wsGatewayUrl =>
      dotenv.get('WS_GATEWAY_URL', fallback: 'ws://10.0.2.2:8090');

  // Mapbox Configuration
  static String get mapboxAccessToken =>
      dotenv.get('MAPBOX_ACCESS_TOKEN', fallback: '');
  static String get mapboxStyleUrl => dotenv.get('MAPBOX_STYLE_URL',
      fallback: 'mapbox://styles/mapbox/satellite-streets-v12');

  // Default Tenant
  static String get defaultTenantId =>
      dotenv.get('DEFAULT_TENANT_ID', fallback: 'sahool-demo');

  // App Configuration
  static String get appName =>
      dotenv.get('APP_NAME', fallback: 'SAHOOL Field App');
  static String get appVersion => dotenv.get('APP_VERSION', fallback: '15.3.0');
  static String get environment =>
      dotenv.get('ENVIRONMENT', fallback: 'development');

  // Feature Flags
  static bool get enableOfflineMode =>
      dotenv.get('ENABLE_OFFLINE_MODE', fallback: 'true') == 'true';
  static bool get enableBackgroundSync =>
      dotenv.get('ENABLE_BACKGROUND_SYNC', fallback: 'true') == 'true';
  static bool get enableCamera =>
      dotenv.get('ENABLE_CAMERA', fallback: 'true') == 'true';

  /// Load environment configuration
  static Future<void> load() async {
    try {
      await dotenv.load(fileName: '.env');
      print('✅ Environment configuration loaded successfully');
    } catch (e) {
      print(
          '⚠️ Warning: Could not load .env file. Using default configuration.');
      print('Error: $e');
    }
  }
}
