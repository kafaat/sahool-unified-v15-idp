/// Authentication Mocks
/// فئات وهمية للمصادقة للاختبارات
///
/// Provides mock implementations for authentication unit tests.
/// يوفر تطبيقات وهمية لاختبارات وحدة المصادقة
library;

import 'dart:async';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:local_auth/local_auth.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/auth/auth_service.dart';
import 'package:sahool_field_app/core/auth/biometric_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/core/auth/token_manager.dart';
import 'package:sahool_field_app/core/http/api_client.dart';

/// Mock SecureStorageService with in-memory storage
class MockSecureStorageService extends Mock implements SecureStorageService {
  final Map<String, String> _storage = {};

  /// Set up default behavior for all methods
  void setupDefaults() {
    // Token methods
    when(() => getAccessToken()).thenAnswer((_) async => _storage['access_token']);
    when(() => setAccessToken(any())).thenAnswer((invocation) async {
      _storage['access_token'] = invocation.positionalArguments[0] as String;
    });
    when(() => getRefreshToken()).thenAnswer((_) async => _storage['refresh_token']);
    when(() => setRefreshToken(any())).thenAnswer((invocation) async {
      _storage['refresh_token'] = invocation.positionalArguments[0] as String;
    });
    when(() => getTokenExpiry()).thenAnswer((_) async {
      final expiry = _storage['token_expiry'];
      return expiry != null ? DateTime.parse(expiry) : null;
    });
    when(() => setTokenExpiry(any())).thenAnswer((invocation) async {
      final expiry = invocation.positionalArguments[0] as DateTime;
      _storage['token_expiry'] = expiry.toIso8601String();
    });
    when(() => deleteTokens()).thenAnswer((_) async {
      _storage.remove('access_token');
      _storage.remove('refresh_token');
      _storage.remove('token_expiry');
    });

    // User data methods
    when(() => getUserData()).thenAnswer((_) async {
      final data = _storage['user_data'];
      if (data == null) return null;
      // Simple JSON parse simulation for tests
      return _parseSimpleJson(data);
    });
    when(() => setUserData(any())).thenAnswer((invocation) async {
      final data = invocation.positionalArguments[0] as Map<String, dynamic>;
      _storage['user_data'] = _simpleJsonEncode(data);
    });
    when(() => deleteUserData()).thenAnswer((_) async {
      _storage.remove('user_data');
    });

    // Biometric methods
    when(() => isBiometricEnabled()).thenAnswer((_) async {
      return _storage['biometric_enabled'] == 'true';
    });
    when(() => setBiometricEnabled(any())).thenAnswer((invocation) async {
      _storage['biometric_enabled'] = invocation.positionalArguments[0].toString();
    });

    // Tenant methods
    when(() => getTenantId()).thenAnswer((_) async => _storage['tenant_id']);
    when(() => setTenantId(any())).thenAnswer((invocation) async {
      _storage['tenant_id'] = invocation.positionalArguments[0] as String;
    });

    // Sync methods
    when(() => getLastSyncTime()).thenAnswer((_) async {
      final time = _storage['last_sync_time'];
      return time != null ? DateTime.parse(time) : null;
    });
    when(() => setLastSyncTime(any())).thenAnswer((invocation) async {
      final time = invocation.positionalArguments[0] as DateTime;
      _storage['last_sync_time'] = time.toIso8601String();
    });

    // Generic methods
    when(() => read(any())).thenAnswer((invocation) async {
      return _storage[invocation.positionalArguments[0] as String];
    });
    when(() => write(any(), any())).thenAnswer((invocation) async {
      _storage[invocation.positionalArguments[0] as String] =
          invocation.positionalArguments[1] as String;
    });
    when(() => delete(any())).thenAnswer((invocation) async {
      _storage.remove(invocation.positionalArguments[0] as String);
    });
    when(() => containsKey(any())).thenAnswer((invocation) async {
      return _storage.containsKey(invocation.positionalArguments[0] as String);
    });
    when(() => clearAll()).thenAnswer((_) async {
      _storage.clear();
    });
    when(() => getAllKeys()).thenAnswer((_) async => _storage.keys.toList());
  }

  /// Helper to set stored data for tests
  void setStoredData(String key, String value) {
    _storage[key] = value;
  }

  /// Helper to get current storage state
  Map<String, String> get currentStorage => Map.from(_storage);

  /// Clear storage between tests
  void clearStorage() {
    _storage.clear();
  }

  String _simpleJsonEncode(Map<String, dynamic> data) {
    return data.entries.map((e) => '${e.key}:${e.value}').join('|');
  }

  Map<String, dynamic>? _parseSimpleJson(String data) {
    final result = <String, dynamic>{};
    for (final entry in data.split('|')) {
      final parts = entry.split(':');
      if (parts.length == 2) {
        result[parts[0]] = parts[1];
      }
    }
    return result.isEmpty ? null : result;
  }
}

/// Mock BiometricService for testing
class MockBiometricService extends Mock implements BiometricService {
  bool _isAvailable = true;
  bool _isEnabled = false;
  bool _willAuthenticate = true;
  List<BiometricType> _availableBiometrics = [BiometricType.fingerprint];

  void setAvailable(bool available) {
    _isAvailable = available;
  }

  void setEnabled(bool enabled) {
    _isEnabled = enabled;
  }

  void setWillAuthenticate(bool willAuth) {
    _willAuthenticate = willAuth;
  }

  void setAvailableBiometrics(List<BiometricType> biometrics) {
    _availableBiometrics = biometrics;
  }

  void setupDefaults() {
    when(() => isAvailable()).thenAnswer((_) async => _isAvailable);
    when(() => isEnabled()).thenAnswer((_) async => _isEnabled);
    when(() => authenticate(reason: any(named: 'reason'), biometricOnly: any(named: 'biometricOnly')))
        .thenAnswer((_) async => _willAuthenticate);
    when(() => getAvailableBiometrics()).thenAnswer((_) async => _availableBiometrics);
    when(() => isFingerprintAvailable())
        .thenAnswer((_) async => _availableBiometrics.contains(BiometricType.fingerprint));
    when(() => isFaceIdAvailable())
        .thenAnswer((_) async => _availableBiometrics.contains(BiometricType.face));
    when(() => enable()).thenAnswer((_) async {
      _isEnabled = true;
      return true;
    });
    when(() => disable()).thenAnswer((_) async {
      _isEnabled = false;
    });
    when(() => cancelAuthentication()).thenAnswer((_) async {});
    when(() => getPrimaryBiometricName()).thenAnswer((_) async {
      if (_availableBiometrics.contains(BiometricType.face)) {
        return 'بصمة الوجه';
      } else if (_availableBiometrics.contains(BiometricType.fingerprint)) {
        return 'بصمة الإصبع';
      }
      return 'البصمة';
    });
    when(() => getBiometricIconName()).thenAnswer((_) async {
      if (_availableBiometrics.contains(BiometricType.face)) {
        return 'face';
      } else if (_availableBiometrics.contains(BiometricType.fingerprint)) {
        return 'fingerprint';
      }
      return 'security';
    });
  }
}

/// Mock ApiClient for testing
class MockApiClient extends Mock implements ApiClient {
  Map<String, dynamic>? _nextResponse;
  ApiException? _nextError;

  void setNextResponse(Map<String, dynamic> response) {
    _nextResponse = response;
    _nextError = null;
  }

  void setNextError(ApiException error) {
    _nextError = error;
    _nextResponse = null;
  }

  void setupDefaults() {
    when(() => post(any(), any(), queryParameters: any(named: 'queryParameters'), headers: any(named: 'headers')))
        .thenAnswer((_) async {
      if (_nextError != null) {
        throw _nextError!;
      }
      return _nextResponse;
    });
    when(() => get(any(), queryParameters: any(named: 'queryParameters')))
        .thenAnswer((_) async {
      if (_nextError != null) {
        throw _nextError!;
      }
      return _nextResponse;
    });
    when(() => setAuthToken(any())).thenReturn(null);
    when(() => setTenantId(any())).thenReturn(null);
    when(() => authToken).thenReturn(null);
    when(() => tenantId).thenReturn('tenant_1');
  }
}

/// Mock TokenManager for testing
class MockTokenManager extends Mock implements TokenManager {
  final _authStateController = StreamController<bool>.broadcast();

  void setupDefaults() {
    when(() => authStateStream).thenAnswer((_) => _authStateController.stream);
    when(() => setApiClient(any())).thenReturn(null);
    when(() => refreshToken()).thenAnswer((_) async {});
    when(() => logout()).thenAnswer((_) async {});
    when(() => dispose()).thenReturn(null);
    when(() => storeTokens(
      accessToken: any(named: 'accessToken'),
      refreshToken: any(named: 'refreshToken'),
      expiresIn: any(named: 'expiresIn'),
    )).thenAnswer((_) async {});
  }

  void emitAuthState(bool isAuthenticated) {
    _authStateController.add(isAuthenticated);
  }
}

/// Mock LocalAuthentication for direct platform testing
class MockLocalAuthentication extends Mock implements LocalAuthentication {}

/// Mock FlutterSecureStorage for direct storage testing
class MockFlutterSecureStorage extends Mock implements FlutterSecureStorage {}

/// Test doubles for AuthService
class FakeAuthService extends Fake implements AuthService {
  User? _currentUser;
  bool _isLoggedIn = false;
  String? _accessToken;

  void setLoggedInUser(User user, String token) {
    _currentUser = user;
    _isLoggedIn = true;
    _accessToken = token;
  }

  void setLoggedOut() {
    _currentUser = null;
    _isLoggedIn = false;
    _accessToken = null;
  }

  @override
  Future<bool> isLoggedIn() async => _isLoggedIn;

  @override
  Future<User?> getCurrentUser() async => _currentUser;

  @override
  Future<String?> getAccessToken() async => _accessToken;

  @override
  Future<void> logout() async {
    setLoggedOut();
  }

  @override
  Future<void> refreshToken() async {
    if (!_isLoggedIn) {
      throw AuthException('Not logged in');
    }
    _accessToken = 'refreshed_token_${DateTime.now().millisecondsSinceEpoch}';
  }
}

/// Fake ApiClient for fallback registration
class _FakeApiClient extends Fake implements ApiClient {}

/// Register fallback values for mocktail
void registerAuthFallbackValues() {
  registerFallbackValue(DateTime.now());
  registerFallbackValue(<String, dynamic>{});
  registerFallbackValue(_FakeApiClient());
}
