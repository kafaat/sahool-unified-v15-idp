import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/app_logger.dart';

/// SAHOOL Secure Storage Service
/// خدمة التخزين الآمن للبيانات الحساسة
///
/// Features:
/// - Encrypted storage for tokens
/// - Secure user data storage
/// - Platform-specific security options

final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService();
});

class SecureStorageService {
  late final FlutterSecureStorage _storage;

  // Storage keys
  static const _keyAccessToken = 'access_token';
  static const _keyRefreshToken = 'refresh_token';
  static const _keyTokenExpiry = 'token_expiry';
  static const _keyUserData = 'user_data';
  static const _keyBiometricEnabled = 'biometric_enabled';
  static const _keyTenantId = 'tenant_id';
  static const _keyLastSyncTime = 'last_sync_time';

  SecureStorageService() {
    _storage = const FlutterSecureStorage(
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
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Token Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get access token
  Future<String?> getAccessToken() async {
    try {
      return await _storage.read(key: _keyAccessToken);
    } catch (e) {
      AppLogger.e('Failed to read access token', error: e);
      return null;
    }
  }

  /// Set access token
  Future<void> setAccessToken(String token) async {
    try {
      await _storage.write(key: _keyAccessToken, value: token);
    } catch (e) {
      AppLogger.e('Failed to write access token', error: e);
      rethrow;
    }
  }

  /// Get refresh token
  Future<String?> getRefreshToken() async {
    try {
      return await _storage.read(key: _keyRefreshToken);
    } catch (e) {
      AppLogger.e('Failed to read refresh token', error: e);
      return null;
    }
  }

  /// Set refresh token
  Future<void> setRefreshToken(String token) async {
    try {
      await _storage.write(key: _keyRefreshToken, value: token);
    } catch (e) {
      AppLogger.e('Failed to write refresh token', error: e);
      rethrow;
    }
  }

  /// Get token expiry
  Future<DateTime?> getTokenExpiry() async {
    try {
      final value = await _storage.read(key: _keyTokenExpiry);
      if (value == null) return null;
      return DateTime.parse(value);
    } catch (e) {
      AppLogger.e('Failed to read token expiry', error: e);
      return null;
    }
  }

  /// Set token expiry
  Future<void> setTokenExpiry(DateTime expiry) async {
    try {
      await _storage.write(
        key: _keyTokenExpiry,
        value: expiry.toIso8601String(),
      );
    } catch (e) {
      AppLogger.e('Failed to write token expiry', error: e);
      rethrow;
    }
  }

  /// Delete all tokens
  Future<void> deleteTokens() async {
    try {
      await Future.wait([
        _storage.delete(key: _keyAccessToken),
        _storage.delete(key: _keyRefreshToken),
        _storage.delete(key: _keyTokenExpiry),
      ]);
    } catch (e) {
      AppLogger.e('Failed to delete tokens', error: e);
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // User Data
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get user data
  Future<Map<String, dynamic>?> getUserData() async {
    try {
      final value = await _storage.read(key: _keyUserData);
      if (value == null) return null;
      return jsonDecode(value) as Map<String, dynamic>;
    } catch (e) {
      AppLogger.e('Failed to read user data', error: e);
      return null;
    }
  }

  /// Set user data
  Future<void> setUserData(Map<String, dynamic> data) async {
    try {
      await _storage.write(
        key: _keyUserData,
        value: jsonEncode(data),
      );
    } catch (e) {
      AppLogger.e('Failed to write user data', error: e);
      rethrow;
    }
  }

  /// Delete user data
  Future<void> deleteUserData() async {
    try {
      await _storage.delete(key: _keyUserData);
    } catch (e) {
      AppLogger.e('Failed to delete user data', error: e);
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Biometric Settings
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if biometric is enabled
  Future<bool> isBiometricEnabled() async {
    try {
      final value = await _storage.read(key: _keyBiometricEnabled);
      return value == 'true';
    } catch (e) {
      return false;
    }
  }

  /// Set biometric enabled
  Future<void> setBiometricEnabled(bool enabled) async {
    try {
      await _storage.write(
        key: _keyBiometricEnabled,
        value: enabled.toString(),
      );
    } catch (e) {
      AppLogger.e('Failed to set biometric enabled', error: e);
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Tenant Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get current tenant ID
  Future<String?> getTenantId() async {
    try {
      return await _storage.read(key: _keyTenantId);
    } catch (e) {
      return null;
    }
  }

  /// Set current tenant ID
  Future<void> setTenantId(String tenantId) async {
    try {
      await _storage.write(key: _keyTenantId, value: tenantId);
    } catch (e) {
      AppLogger.e('Failed to set tenant ID', error: e);
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get last sync time
  Future<DateTime?> getLastSyncTime() async {
    try {
      final value = await _storage.read(key: _keyLastSyncTime);
      if (value == null) return null;
      return DateTime.parse(value);
    } catch (e) {
      return null;
    }
  }

  /// Set last sync time
  Future<void> setLastSyncTime(DateTime time) async {
    try {
      await _storage.write(
        key: _keyLastSyncTime,
        value: time.toIso8601String(),
      );
    } catch (e) {
      AppLogger.e('Failed to set last sync time', error: e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Generic Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Read a value
  Future<String?> read(String key) async {
    try {
      return await _storage.read(key: key);
    } catch (e) {
      AppLogger.e('Failed to read key: $key', error: e);
      return null;
    }
  }

  /// Write a value
  Future<void> write(String key, String value) async {
    try {
      await _storage.write(key: key, value: value);
    } catch (e) {
      AppLogger.e('Failed to write key: $key', error: e);
      rethrow;
    }
  }

  /// Delete a value
  Future<void> delete(String key) async {
    try {
      await _storage.delete(key: key);
    } catch (e) {
      AppLogger.e('Failed to delete key: $key', error: e);
      rethrow;
    }
  }

  /// Check if key exists
  Future<bool> containsKey(String key) async {
    try {
      return await _storage.containsKey(key: key);
    } catch (e) {
      return false;
    }
  }

  /// Clear all stored data
  Future<void> clearAll() async {
    try {
      await _storage.deleteAll();
      AppLogger.i('Cleared all secure storage');
    } catch (e) {
      AppLogger.e('Failed to clear all storage', error: e);
      rethrow;
    }
  }

  /// Get all keys
  Future<List<String>> getAllKeys() async {
    try {
      final all = await _storage.readAll();
      return all.keys.toList();
    } catch (e) {
      return [];
    }
  }
}
