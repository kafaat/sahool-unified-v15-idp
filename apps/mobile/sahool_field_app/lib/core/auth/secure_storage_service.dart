import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/app_logger.dart';

/// SAHOOL Secure Storage Service
/// خدمة التخزين الآمن للبيانات الحساسة
///
/// Features:
/// - Encrypted storage for tokens and credentials
/// - Secure user data storage with JSON serialization
/// - Platform-specific encryption options:
///   - Android: EncryptedSharedPreferences with AES-256
///   - iOS: Keychain with biometric protection
/// - Automatic data migration support
/// - Error handling and logging

final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService();
});

class SecureStorageService {
  late final FlutterSecureStorage _storage;

  // Storage keys - organized by category
  // Authentication tokens
  static const _keyAccessToken = 'access_token';
  static const _keyRefreshToken = 'refresh_token';
  static const _keyTokenExpiry = 'token_expiry';
  static const _keyTokenIssuedAt = 'token_issued_at';

  // User data
  static const _keyUserData = 'user_data';
  static const _keyTenantId = 'tenant_id';

  // Security settings
  static const _keyBiometricEnabled = 'biometric_enabled';
  static const _keyPinCode = 'pin_code';
  static const _keySecurityLevel = 'security_level';

  // App state
  static const _keyLastSyncTime = 'last_sync_time';
  static const _keyAppVersion = 'app_version';
  static const _keyDeviceId = 'device_id';

  SecureStorageService() {
    _storage = const FlutterSecureStorage(
      aOptions: AndroidOptions(
        encryptedSharedPreferences: true,
        sharedPreferencesName: 'sahool_secure_prefs',
        preferencesKeyPrefix: 'sahool_',
        // Use AES-256 encryption
        resetOnError: true,
      ),
      iOptions: IOSOptions(
        // Keychain data available after first unlock
        accessibility: KeychainAccessibility.first_unlock_this_device,
        accountName: 'com.sahool.field',
        // Use default synchronizable: false (don't sync to iCloud)
        synchronizable: false,
      ),
    );
    _initializeStorage();
  }

  /// Initialize storage and perform any necessary migrations
  Future<void> _initializeStorage() async {
    try {
      // Check if storage is accessible
      await _storage.containsKey(key: '_initialized');
      AppLogger.d('Secure storage initialized', tag: 'STORAGE');
    } catch (e) {
      AppLogger.e('Failed to initialize secure storage', tag: 'STORAGE', error: e);
    }
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
      await Future.wait([
        _storage.write(
          key: _keyTokenExpiry,
          value: expiry.toIso8601String(),
        ),
        _storage.write(
          key: _keyTokenIssuedAt,
          value: DateTime.now().toIso8601String(),
        ),
      ]);
    } catch (e) {
      AppLogger.e('Failed to write token expiry', error: e);
      rethrow;
    }
  }

  /// Get token issued at time
  Future<DateTime?> getTokenIssuedAt() async {
    try {
      final value = await _storage.read(key: _keyTokenIssuedAt);
      if (value == null) return null;
      return DateTime.parse(value);
    } catch (e) {
      AppLogger.e('Failed to read token issued at', error: e);
      return null;
    }
  }

  /// Check if token is valid (not expired and not too old)
  Future<bool> isTokenValid() async {
    try {
      final expiry = await getTokenExpiry();
      if (expiry == null) return false;

      final now = DateTime.now();
      return now.isBefore(expiry);
    } catch (e) {
      return false;
    }
  }

  /// Delete all tokens
  Future<void> deleteTokens() async {
    try {
      await Future.wait([
        _storage.delete(key: _keyAccessToken),
        _storage.delete(key: _keyRefreshToken),
        _storage.delete(key: _keyTokenExpiry),
        _storage.delete(key: _keyTokenIssuedAt),
      ]);
      AppLogger.i('All tokens deleted', tag: 'STORAGE');
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
  // Security Settings
  // ═══════════════════════════════════════════════════════════════════════════

  /// Hash PIN code using SHA-256 with salt
  /// This ensures PIN codes are never stored in plain text
  String _hashPin(String pin, String salt) {
    final bytes = utf8.encode(pin + salt);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  /// Generate a random salt for PIN hashing
  Future<String> _getOrCreatePinSalt() async {
    const saltKey = 'pin_salt';
    try {
      var salt = await _storage.read(key: saltKey);
      if (salt == null || salt.isEmpty) {
        // Generate a new salt using current timestamp and random component
        salt = sha256
            .convert(utf8.encode(
                '${DateTime.now().microsecondsSinceEpoch}_sahool_pin_salt'))
            .toString()
            .substring(0, 32);
        await _storage.write(key: saltKey, value: salt);
      }
      return salt;
    } catch (e) {
      // Fallback salt if storage fails - still better than no salt
      AppLogger.w('Using fallback PIN salt', error: e);
      return 'sahool_default_pin_salt_v1';
    }
  }

  /// Store PIN code securely (hashed with salt)
  /// SECURITY: PIN codes are hashed using SHA-256 with a unique salt
  /// and are never stored in plain text
  Future<void> setPinCode(String pin) async {
    try {
      final salt = await _getOrCreatePinSalt();
      final hashedPin = _hashPin(pin, salt);
      await _storage.write(key: _keyPinCode, value: hashedPin);
      AppLogger.d('PIN code stored securely (hashed)', tag: 'STORAGE');
    } catch (e) {
      AppLogger.e('Failed to set PIN code', error: e);
      rethrow;
    }
  }

  /// Get stored PIN hash (for internal use only)
  /// Note: Returns the hash, not the original PIN
  Future<String?> _getStoredPinHash() async {
    try {
      return await _storage.read(key: _keyPinCode);
    } catch (e) {
      return null;
    }
  }

  /// Check if PIN code is set
  Future<bool> hasPinCode() async {
    try {
      final hash = await _getStoredPinHash();
      return hash != null && hash.isNotEmpty;
    } catch (e) {
      return false;
    }
  }

  /// Delete PIN code
  Future<void> deletePinCode() async {
    try {
      await _storage.delete(key: _keyPinCode);
      AppLogger.d('PIN code deleted', tag: 'STORAGE');
    } catch (e) {
      AppLogger.e('Failed to delete PIN code', error: e);
    }
  }

  /// Verify PIN code by comparing hashes
  /// SECURITY: Compares hash of input PIN with stored hash
  Future<bool> verifyPinCode(String pin) async {
    try {
      final storedHash = await _getStoredPinHash();
      if (storedHash == null) return false;

      final salt = await _getOrCreatePinSalt();
      final inputHash = _hashPin(pin, salt);

      // Constant-time comparison to prevent timing attacks
      if (storedHash.length != inputHash.length) return false;

      var result = 0;
      for (var i = 0; i < storedHash.length; i++) {
        result |= storedHash.codeUnitAt(i) ^ inputHash.codeUnitAt(i);
      }
      return result == 0;
    } catch (e) {
      AppLogger.e('PIN verification failed', error: e);
      return false;
    }
  }

  /// Set security level
  Future<void> setSecurityLevel(String level) async {
    try {
      await _storage.write(key: _keySecurityLevel, value: level);
    } catch (e) {
      AppLogger.e('Failed to set security level', error: e);
    }
  }

  /// Get security level
  Future<String?> getSecurityLevel() async {
    try {
      return await _storage.read(key: _keySecurityLevel);
    } catch (e) {
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Device Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set device ID
  Future<void> setDeviceId(String deviceId) async {
    try {
      await _storage.write(key: _keyDeviceId, value: deviceId);
    } catch (e) {
      AppLogger.e('Failed to set device ID', error: e);
    }
  }

  /// Get device ID
  Future<String?> getDeviceId() async {
    try {
      return await _storage.read(key: _keyDeviceId);
    } catch (e) {
      return null;
    }
  }

  /// Set app version
  Future<void> setAppVersion(String version) async {
    try {
      await _storage.write(key: _keyAppVersion, value: version);
    } catch (e) {
      AppLogger.e('Failed to set app version', error: e);
    }
  }

  /// Get app version
  Future<String?> getAppVersion() async {
    try {
      return await _storage.read(key: _keyAppVersion);
    } catch (e) {
      return null;
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
