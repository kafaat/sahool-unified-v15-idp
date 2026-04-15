import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/app_logger.dart';

/// SAHOOL Secure Storage Wrapper
/// غلاف التخزين الآمن - يستخدم flutter_secure_storage
///
/// Provides token and queue management with platform-specific encryption.
/// يوفر إدارة الرموز والطوابير مع التشفير الخاص بالمنصة.
class SecureStorage {
  final FlutterSecureStorage _storage;

  // Storage keys
  static const _keyAccessToken = 'access_token';
  static const _keyRefreshToken = 'refresh_token';
  static const _keyTenantId = 'tenant_id';
  static const _keyQueuedRequests = 'queued_requests';

  SecureStorage()
      : _storage = const FlutterSecureStorage(
          aOptions: AndroidOptions(
            encryptedSharedPreferences: true,
            sharedPreferencesName: 'sahool_secure_prefs',
            preferencesKeyPrefix: 'sahool_',
            keyCipherAlgorithm: KeyCipherAlgorithm.RSA_ECB_OAEPwithSHA_256andMGF1Padding,
            storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
          ),
          iOptions: IOSOptions(
            accessibility: KeychainAccessibility.first_unlock_this_device,
            accountName: 'com.sahool.field',
          ),
        );

  // Token management

  Future<String?> getAccessToken() => _read(_keyAccessToken);

  Future<void> setAccessToken(String token) =>
      _write(_keyAccessToken, token);

  Future<String?> getRefreshToken() => _read(_keyRefreshToken);

  Future<void> setRefreshToken(String token) =>
      _write(_keyRefreshToken, token);

  Future<String?> getTenantId() => _read(_keyTenantId);

  Future<void> setTenantId(String tenantId) =>
      _write(_keyTenantId, tenantId);

  Future<void> clearTokens() async {
    await _delete(_keyAccessToken);
    await _delete(_keyRefreshToken);
  }

  // Queue management for offline requests

  Future<String?> getQueuedRequests() => _read(_keyQueuedRequests);

  Future<void> setQueuedRequests(String data) =>
      _write(_keyQueuedRequests, data);

  // Safe wrappers with error handling for platform exceptions

  Future<String?> _read(String key) async {
    try {
      return await _storage.read(key: key);
    } catch (e) {
      AppLogger.e('SecureStorage read failed for key "$key"',
          tag: 'SECURE_STORAGE', error: e);
      return null;
    }
  }

  Future<void> _write(String key, String value) async {
    try {
      await _storage.write(key: key, value: value);
    } catch (e) {
      AppLogger.e('SecureStorage write failed for key "$key"',
          tag: 'SECURE_STORAGE', error: e);
      rethrow;
    }
  }

  Future<void> _delete(String key) async {
    try {
      await _storage.delete(key: key);
    } catch (e) {
      AppLogger.e('SecureStorage delete failed for key "$key"',
          tag: 'SECURE_STORAGE', error: e);
    }
  }
}
