import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

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
          ),
          iOptions: IOSOptions(
            accessibility: KeychainAccessibility.first_unlock_this_device,
            accountName: 'com.sahool.field',
          ),
        );

  // Token management

  Future<String?> getAccessToken() => _storage.read(key: _keyAccessToken);

  Future<void> setAccessToken(String token) =>
      _storage.write(key: _keyAccessToken, value: token);

  Future<String?> getRefreshToken() => _storage.read(key: _keyRefreshToken);

  Future<void> setRefreshToken(String token) =>
      _storage.write(key: _keyRefreshToken, value: token);

  Future<String?> getTenantId() => _storage.read(key: _keyTenantId);

  Future<void> setTenantId(String tenantId) =>
      _storage.write(key: _keyTenantId, value: tenantId);

  Future<void> clearTokens() async {
    await _storage.delete(key: _keyAccessToken);
    await _storage.delete(key: _keyRefreshToken);
  }

  // Queue management for offline requests

  Future<String?> getQueuedRequests() =>
      _storage.read(key: _keyQueuedRequests);

  Future<void> setQueuedRequests(String data) =>
      _storage.write(key: _keyQueuedRequests, value: data);
}
