/// Secure Storage Service Tests
/// اختبارات خدمة التخزين الآمن
///
/// Comprehensive tests for SecureStorageService covering:
/// - Token storage operations
/// - User data management
/// - Biometric settings
/// - Tenant management
/// - Generic storage operations
/// - Error handling

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:sahool_mobile_core/core/auth/secure_storage_service.dart';

import 'auth_fixtures.dart';

/// Platform channel mock for FlutterSecureStorage
class MockSecureStorageChannel {
  static const MethodChannel channel =
      MethodChannel('plugins.it_nomads.com/flutter_secure_storage');

  final Map<String, String> _storage = {};
  bool shouldThrowError = false;
  String? errorMessage;

  void setupMockChannel() {
    TestWidgetsFlutterBinding.ensureInitialized();

    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (MethodCall methodCall) async {
      if (shouldThrowError) {
        throw PlatformException(
          code: 'ERROR',
          message: errorMessage ?? 'Storage error',
        );
      }

      switch (methodCall.method) {
        case 'read':
          final key = methodCall.arguments['key'] as String;
          return _storage[key];
        case 'write':
          final key = methodCall.arguments['key'] as String;
          final value = methodCall.arguments['value'] as String;
          _storage[key] = value;
          return null;
        case 'delete':
          final key = methodCall.arguments['key'] as String;
          _storage.remove(key);
          return null;
        case 'deleteAll':
          _storage.clear();
          return null;
        case 'containsKey':
          final key = methodCall.arguments['key'] as String;
          return _storage.containsKey(key);
        case 'readAll':
          return Map<String, String>.from(_storage);
        default:
          return null;
      }
    });
  }

  void setStoredValue(String key, String value) {
    _storage[key] = value;
  }

  String? getStoredValue(String key) {
    return _storage[key];
  }

  void clearStorage() {
    _storage.clear();
  }

  void setError(String message) {
    shouldThrowError = true;
    errorMessage = message;
  }

  void clearError() {
    shouldThrowError = false;
    errorMessage = null;
  }

  void tearDown() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, null);
    _storage.clear();
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late SecureStorageService storageService;
  late MockSecureStorageChannel mockChannel;

  setUp(() {
    mockChannel = MockSecureStorageChannel();
    mockChannel.setupMockChannel();
    storageService = SecureStorageService();
  });

  tearDown(() {
    mockChannel.tearDown();
  });

  group('SecureStorageService', () {
    group('Token Management', () {
      group('getAccessToken', () {
        test('should return stored access token', () async {
          // Arrange
          mockChannel.setStoredValue('access_token', AuthFixtures.validAccessToken);

          // Act
          final token = await storageService.getAccessToken();

          // Assert
          expect(token, AuthFixtures.validAccessToken);
        });

        test('should return null when no token exists', () async {
          // Act
          final token = await storageService.getAccessToken();

          // Assert
          expect(token, isNull);
        });

        test('should handle storage errors gracefully', () async {
          // Arrange
          mockChannel.setError('Read error');

          // Act
          final token = await storageService.getAccessToken();

          // Assert
          expect(token, isNull);
        });
      });

      group('setAccessToken', () {
        test('should store access token', () async {
          // Act
          await storageService.setAccessToken(AuthFixtures.validAccessToken);

          // Assert
          expect(
            mockChannel.getStoredValue('access_token'),
            AuthFixtures.validAccessToken,
          );
        });

        test('should throw on storage error', () async {
          // Arrange
          mockChannel.setError('Write error');

          // Act & Assert
          expect(
            () => storageService.setAccessToken(AuthFixtures.validAccessToken),
            throwsA(isA<PlatformException>()),
          );
        });
      });

      group('getRefreshToken', () {
        test('should return stored refresh token', () async {
          // Arrange
          mockChannel.setStoredValue('refresh_token', AuthFixtures.validRefreshToken);

          // Act
          final token = await storageService.getRefreshToken();

          // Assert
          expect(token, AuthFixtures.validRefreshToken);
        });

        test('should return null when no token exists', () async {
          // Act
          final token = await storageService.getRefreshToken();

          // Assert
          expect(token, isNull);
        });
      });

      group('setRefreshToken', () {
        test('should store refresh token', () async {
          // Act
          await storageService.setRefreshToken(AuthFixtures.validRefreshToken);

          // Assert
          expect(
            mockChannel.getStoredValue('refresh_token'),
            AuthFixtures.validRefreshToken,
          );
        });
      });

      group('getTokenExpiry', () {
        test('should return stored token expiry', () async {
          // Arrange
          final expiry = DateTime.now().add(const Duration(hours: 1));
          mockChannel.setStoredValue('token_expiry', expiry.toIso8601String());

          // Act
          final result = await storageService.getTokenExpiry();

          // Assert
          expect(result, isNotNull);
          expect(result!.difference(expiry).inSeconds.abs(), lessThan(2));
        });

        test('should return null when no expiry exists', () async {
          // Act
          final result = await storageService.getTokenExpiry();

          // Assert
          expect(result, isNull);
        });

        test('should handle invalid date format gracefully', () async {
          // Arrange
          mockChannel.setStoredValue('token_expiry', 'invalid_date');

          // Act
          final result = await storageService.getTokenExpiry();

          // Assert
          expect(result, isNull);
        });
      });

      group('setTokenExpiry', () {
        test('should store token expiry as ISO string', () async {
          // Arrange
          final expiry = DateTime(2024, 6, 15, 12, 30, 0);

          // Act
          await storageService.setTokenExpiry(expiry);

          // Assert
          final stored = mockChannel.getStoredValue('token_expiry');
          expect(stored, expiry.toIso8601String());
        });
      });

      group('deleteTokens', () {
        test('should delete all token-related keys', () async {
          // Arrange
          mockChannel.setStoredValue('access_token', 'token');
          mockChannel.setStoredValue('refresh_token', 'refresh');
          mockChannel.setStoredValue('token_expiry', 'expiry');

          // Act
          await storageService.deleteTokens();

          // Assert
          expect(mockChannel.getStoredValue('access_token'), isNull);
          expect(mockChannel.getStoredValue('refresh_token'), isNull);
          expect(mockChannel.getStoredValue('token_expiry'), isNull);
        });
      });
    });

    group('User Data Management', () {
      group('getUserData', () {
        test('should return stored user data as map', () async {
          // Arrange
          const jsonString =
              '{"id":"user_001","email":"test@sahool.com","name":"Test User","role":"farmer","tenant_id":"tenant_1"}';
          mockChannel.setStoredValue('user_data', jsonString);

          // Act
          final result = await storageService.getUserData();

          // Assert
          expect(result, isNotNull);
          expect(result!['id'], 'user_001');
          expect(result['email'], 'test@sahool.com');
        });

        test('should return null when no user data exists', () async {
          // Act
          final result = await storageService.getUserData();

          // Assert
          expect(result, isNull);
        });

        test('should handle invalid JSON gracefully', () async {
          // Arrange
          mockChannel.setStoredValue('user_data', 'invalid json');

          // Act
          final result = await storageService.getUserData();

          // Assert
          expect(result, isNull);
        });
      });

      group('setUserData', () {
        test('should store user data as JSON string', () async {
          // Arrange
          final userData = {
            'id': 'user_001',
            'email': 'test@sahool.com',
            'name': 'Test User',
          };

          // Act
          await storageService.setUserData(userData);

          // Assert
          final stored = mockChannel.getStoredValue('user_data');
          expect(stored, isNotNull);
          expect(stored, contains('user_001'));
          expect(stored, contains('test@sahool.com'));
        });
      });

      group('deleteUserData', () {
        test('should delete user data', () async {
          // Arrange
          mockChannel.setStoredValue('user_data', '{"id":"user_001"}');

          // Act
          await storageService.deleteUserData();

          // Assert
          expect(mockChannel.getStoredValue('user_data'), isNull);
        });
      });
    });

    group('Biometric Settings', () {
      group('isBiometricEnabled', () {
        test('should return true when biometric is enabled', () async {
          // Arrange
          mockChannel.setStoredValue('biometric_enabled', 'true');

          // Act
          final result = await storageService.isBiometricEnabled();

          // Assert
          expect(result, isTrue);
        });

        test('should return false when biometric is disabled', () async {
          // Arrange
          mockChannel.setStoredValue('biometric_enabled', 'false');

          // Act
          final result = await storageService.isBiometricEnabled();

          // Assert
          expect(result, isFalse);
        });

        test('should return false when not set', () async {
          // Act
          final result = await storageService.isBiometricEnabled();

          // Assert
          expect(result, isFalse);
        });

        test('should return false on error', () async {
          // Arrange
          mockChannel.setError('Read error');

          // Act
          final result = await storageService.isBiometricEnabled();

          // Assert
          expect(result, isFalse);
        });
      });

      group('setBiometricEnabled', () {
        test('should store true value', () async {
          // Act
          await storageService.setBiometricEnabled(true);

          // Assert
          expect(mockChannel.getStoredValue('biometric_enabled'), 'true');
        });

        test('should store false value', () async {
          // Act
          await storageService.setBiometricEnabled(false);

          // Assert
          expect(mockChannel.getStoredValue('biometric_enabled'), 'false');
        });
      });
    });

    group('Tenant Management', () {
      group('getTenantId', () {
        test('should return stored tenant ID', () async {
          // Arrange
          mockChannel.setStoredValue('tenant_id', 'tenant_001');

          // Act
          final result = await storageService.getTenantId();

          // Assert
          expect(result, 'tenant_001');
        });

        test('should return null when not set', () async {
          // Act
          final result = await storageService.getTenantId();

          // Assert
          expect(result, isNull);
        });
      });

      group('setTenantId', () {
        test('should store tenant ID', () async {
          // Act
          await storageService.setTenantId('tenant_001');

          // Assert
          expect(mockChannel.getStoredValue('tenant_id'), 'tenant_001');
        });
      });
    });

    group('Sync Management', () {
      group('getLastSyncTime', () {
        test('should return stored sync time', () async {
          // Arrange
          final syncTime = DateTime.now();
          mockChannel.setStoredValue('last_sync_time', syncTime.toIso8601String());

          // Act
          final result = await storageService.getLastSyncTime();

          // Assert
          expect(result, isNotNull);
          expect(result!.difference(syncTime).inSeconds.abs(), lessThan(2));
        });

        test('should return null when not set', () async {
          // Act
          final result = await storageService.getLastSyncTime();

          // Assert
          expect(result, isNull);
        });
      });

      group('setLastSyncTime', () {
        test('should store sync time as ISO string', () async {
          // Arrange
          final syncTime = DateTime(2024, 6, 15, 10, 30, 0);

          // Act
          await storageService.setLastSyncTime(syncTime);

          // Assert
          expect(
            mockChannel.getStoredValue('last_sync_time'),
            syncTime.toIso8601String(),
          );
        });
      });
    });

    group('Generic Methods', () {
      group('read', () {
        test('should read stored value', () async {
          // Arrange
          mockChannel.setStoredValue('custom_key', 'custom_value');

          // Act
          final result = await storageService.read('custom_key');

          // Assert
          expect(result, 'custom_value');
        });

        test('should return null for non-existent key', () async {
          // Act
          final result = await storageService.read('non_existent');

          // Assert
          expect(result, isNull);
        });
      });

      group('write', () {
        test('should write value', () async {
          // Act
          await storageService.write('custom_key', 'custom_value');

          // Assert
          expect(mockChannel.getStoredValue('custom_key'), 'custom_value');
        });
      });

      group('delete', () {
        test('should delete stored value', () async {
          // Arrange
          mockChannel.setStoredValue('custom_key', 'custom_value');

          // Act
          await storageService.delete('custom_key');

          // Assert
          expect(mockChannel.getStoredValue('custom_key'), isNull);
        });
      });

      group('containsKey', () {
        test('should return true when key exists', () async {
          // Arrange
          mockChannel.setStoredValue('existing_key', 'value');

          // Act
          final result = await storageService.containsKey('existing_key');

          // Assert
          expect(result, isTrue);
        });

        test('should return false when key does not exist', () async {
          // Act
          final result = await storageService.containsKey('non_existent');

          // Assert
          expect(result, isFalse);
        });

        test('should return false on error', () async {
          // Arrange
          mockChannel.setError('Error');

          // Act
          final result = await storageService.containsKey('any_key');

          // Assert
          expect(result, isFalse);
        });
      });

      group('clearAll', () {
        test('should clear all stored data', () async {
          // Arrange
          mockChannel.setStoredValue('key1', 'value1');
          mockChannel.setStoredValue('key2', 'value2');
          mockChannel.setStoredValue('key3', 'value3');

          // Act
          await storageService.clearAll();

          // Assert
          expect(mockChannel.getStoredValue('key1'), isNull);
          expect(mockChannel.getStoredValue('key2'), isNull);
          expect(mockChannel.getStoredValue('key3'), isNull);
        });
      });

      group('getAllKeys', () {
        test('should return all stored keys', () async {
          // Arrange
          mockChannel.setStoredValue('key1', 'value1');
          mockChannel.setStoredValue('key2', 'value2');

          // Act
          final keys = await storageService.getAllKeys();

          // Assert
          expect(keys, contains('key1'));
          expect(keys, contains('key2'));
        });

        test('should return empty list when no keys', () async {
          // Act
          final keys = await storageService.getAllKeys();

          // Assert
          expect(keys, isEmpty);
        });

        test('should return empty list on error', () async {
          // Arrange
          mockChannel.setError('Error');

          // Act
          final keys = await storageService.getAllKeys();

          // Assert
          expect(keys, isEmpty);
        });
      });
    });
  });
}
