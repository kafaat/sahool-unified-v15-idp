import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/config/env_config.dart';

void main() {
  group('EnvConfig', () {
    group('Environment Detection', () {
      test('should default to development environment', () {
        // Default environment should be development
        expect(EnvConfig.isDevelopment, isTrue);
      });

      test('should correctly identify development mode', () {
        expect(EnvConfig.environment, equals(AppEnvironment.development));
      });

      test('isDebugMode should reflect debug build', () {
        // In tests, we're typically in debug mode
        expect(EnvConfig.isDebugMode, isTrue);
      });
    });

    group('API Configuration', () {
      test('should have valid API base URL', () {
        final apiUrl = EnvConfig.apiBaseUrl;

        expect(apiUrl, isNotEmpty);
        expect(
          apiUrl.startsWith('http://') || apiUrl.startsWith('https://'),
          isTrue,
          reason: 'API URL should start with http:// or https://',
        );
      });

      test('should have valid WebSocket URL', () {
        final wsUrl = EnvConfig.wsBaseUrl;

        expect(wsUrl, isNotEmpty);
        expect(
          wsUrl.startsWith('ws://') || wsUrl.startsWith('wss://'),
          isTrue,
          reason: 'WebSocket URL should start with ws:// or wss://',
        );
      });
    });

    group('Feature Flags', () {
      test('offline mode should be enabled by default', () {
        expect(EnvConfig.enableOfflineMode, isTrue);
      });

      test('background sync should be enabled by default', () {
        expect(EnvConfig.enableBackgroundSync, isTrue);
      });

      test('camera should be enabled by default', () {
        expect(EnvConfig.enableCamera, isTrue);
      });

      test('push notifications should be disabled in development', () {
        // Push notifications are disabled in development
        if (EnvConfig.isDevelopment) {
          expect(EnvConfig.enablePushNotifications, isFalse);
        }
      });

      test('analytics should be disabled in non-production', () {
        if (!EnvConfig.isProduction) {
          expect(EnvConfig.enableAnalytics, isFalse);
        }
      });

      test('crash reporting should be disabled in development', () {
        if (EnvConfig.isDevelopment) {
          expect(EnvConfig.enableCrashReporting, isFalse);
        }
      });
    });

    group('Sync Configuration', () {
      test('sync interval should be positive', () {
        expect(EnvConfig.syncInterval.inSeconds, greaterThan(0));
      });

      test('background sync interval should be at least 1 minute', () {
        expect(EnvConfig.backgroundSyncInterval.inMinutes, greaterThanOrEqualTo(1));
      });

      test('max retry count should be positive', () {
        expect(EnvConfig.maxRetryCount, greaterThan(0));
      });

      test('outbox batch size should be positive', () {
        expect(EnvConfig.outboxBatchSize, greaterThan(0));
      });
    });

    group('Cache Configuration', () {
      test('cache expiry should be at least 1 hour', () {
        expect(EnvConfig.cacheExpiry.inHours, greaterThanOrEqualTo(1));
      });

      test('image cache expiry should be at least 1 day', () {
        expect(EnvConfig.imageCacheExpiry.inDays, greaterThanOrEqualTo(1));
      });
    });

    group('Timeout Configuration', () {
      test('connect timeout should be reasonable', () {
        final timeout = EnvConfig.connectTimeout;
        expect(timeout.inSeconds, greaterThan(0));
        expect(timeout.inSeconds, lessThanOrEqualTo(60));
      });

      test('receive timeout should be reasonable', () {
        final timeout = EnvConfig.receiveTimeout;
        expect(timeout.inSeconds, greaterThan(0));
        expect(timeout.inSeconds, lessThanOrEqualTo(120));
      });
    });

    group('App Info', () {
      test('app name should not be empty', () {
        expect(EnvConfig.appName, isNotEmpty);
      });

      test('app version should follow semantic versioning', () {
        final version = EnvConfig.appVersion;
        expect(version, isNotEmpty);

        // Basic semver pattern check
        final semverPattern = RegExp(r'^\d+\.\d+\.\d+');
        expect(semverPattern.hasMatch(version), isTrue);
      });

      test('full version should contain version and build number', () {
        final fullVersion = EnvConfig.fullVersion;
        expect(fullVersion, contains(EnvConfig.appVersion));
        expect(fullVersion, contains('+'));
      });
    });

    group('Tenant Configuration', () {
      test('default tenant ID should not be empty', () {
        expect(EnvConfig.defaultTenantId, isNotEmpty);
      });
    });

    group('Debug Helpers', () {
      test('toDebugMap should return valid map', () {
        final debugMap = EnvConfig.toDebugMap();

        expect(debugMap, isA<Map<String, dynamic>>());
        expect(debugMap.containsKey('environment'), isTrue);
        expect(debugMap.containsKey('apiBaseUrl'), isTrue);
        expect(debugMap.containsKey('features'), isTrue);
        expect(debugMap.containsKey('sync'), isTrue);
      });

      test('debug map features should be a map', () {
        final debugMap = EnvConfig.toDebugMap();
        final features = debugMap['features'];

        expect(features, isA<Map<String, dynamic>>());
        expect(features.containsKey('offlineMode'), isTrue);
        expect(features.containsKey('pushNotifications'), isTrue);
      });
    });
  });
}
