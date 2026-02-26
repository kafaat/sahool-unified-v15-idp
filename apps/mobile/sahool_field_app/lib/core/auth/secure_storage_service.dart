import 'dart:convert';
import 'package:flutter/foundation.dart';
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
/// - Storage integrity validation
/// - Error recovery mechanisms

final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService();
});

/// Storage exception for handling storage-specific errors
class StorageException implements Exception {
  final String message;
  final String? code;
  final Object? originalError;

  StorageException(this.message, {this.code, this.originalError});

  @override
  String toString() => 'StorageException($code): $message';
}

class SecureStorageService {
  late final FlutterSecureStorage _storage;
  bool _isInitialized = false;
  bool _hasStorageError = false;

  // Storage keys
  static const _keyAccessToken = 'access_token';
  static const _keyRefreshToken = 'refresh_token';
  static const _keyTokenExpiry = 'token_expiry';
  static const _keyUserData = 'user_data';
  static const _keyBiometricEnabled = 'biometric_enabled';
  static const _keyTenantId = 'tenant_id';
  static const _keyLastSyncTime = 'last_sync_time';
  static const _keyStorageVersion = 'storage_version';
  static const _keyBiometricFailureCount = 'biometric_failure_count';
  static const _keyBiometricLockoutUntil = 'biometric_lockout_until';

  // Current storage version for migrations
  static const _currentStorageVersion = 1;

  // Biometric lockout configuration
  static const _maxBiometricFailures = 5;
  static const _biometricLockoutDuration = Duration(minutes: 30);

  SecureStorageService() {
    _storage = const FlutterSecureStorage(
      aOptions: AndroidOptions(
        encryptedSharedPreferences: true,
        sharedPreferencesName: 'sahool_secure_prefs',
        preferencesKeyPrefix: 'sahool_',
        // Reset on new install to prevent data corruption
        resetOnError: true,
      ),
      iOptions: IOSOptions(
        accessibility: KeychainAccessibility.first_unlock_this_device,
        accountName: 'com.sahool.field',
        // Synchronize with iCloud for backup
        synchronizable: false, // Keep tokens local only for security
      ),
    );
  }

  /// Initialize storage and check integrity
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Verify storage is accessible
      await _verifyStorageAccess();

      // Check and migrate storage version if needed
      await _migrateStorageIfNeeded();

      _isInitialized = true;
      _hasStorageError = false;
      AppLogger.i('Secure storage initialized', tag: 'STORAGE');
    } catch (e) {
      AppLogger.e('Secure storage initialization failed',
          error: e, tag: 'STORAGE');
      _hasStorageError = true;
      rethrow;
    }
  }

  /// Verify storage is accessible
  Future<void> _verifyStorageAccess() async {
    try {
      // Try to write and read a test value
      const testKey = '_storage_test';
      const testValue = 'test_${1234}';

      await _storage.write(key: testKey, value: testValue);
      final readValue = await _storage.read(key: testKey);
      await _storage.delete(key: testKey);

      if (readValue != testValue) {
        throw StorageException(
          'Storage verification failed - read value mismatch',
          code: 'STORAGE_VERIFICATION_FAILED',
        );
      }
    } catch (e) {
      if (e is StorageException) rethrow;
      throw StorageException(
        'Storage not accessible',
        code: 'STORAGE_NOT_ACCESSIBLE',
        originalError: e,
      );
    }
  }

  /// Migrate storage if version changed
  Future<void> _migrateStorageIfNeeded() async {
    try {
      final versionStr = await _storage.read(key: _keyStorageVersion);
      final currentVersion =
          versionStr != null ? int.tryParse(versionStr) ?? 0 : 0;

      if (currentVersion < _currentStorageVersion) {
        AppLogger.i(
            'Migrating storage from version $currentVersion to $_currentStorageVersion',
            tag: 'STORAGE');
        // Add migration logic here as needed
        await _storage.write(
            key: _keyStorageVersion, value: _currentStorageVersion.toString());
      }
    } catch (e) {
      AppLogger.e('Storage migration failed', error: e, tag: 'STORAGE');
      // Don't fail - just continue with current state
    }
  }

  /// Check if storage has encountered errors
  bool get hasStorageError => _hasStorageError;

  // ═══════════════════════════════════════════════════════════════════════════
  // Token Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get access token
  Future<String?> getAccessToken() async {
    try {
      final token = await _storage.read(key: _keyAccessToken);
      // Validate token format (basic sanity check)
      if (token != null && token.isEmpty) {
        AppLogger.w('Empty access token found, treating as null',
            tag: 'STORAGE');
        return null;
      }
      return token;
    } catch (e) {
      AppLogger.e('Failed to read access token', error: e, tag: 'STORAGE');
      _hasStorageError = true;
      return null;
    }
  }

  /// Set access token
  Future<void> setAccessToken(String token) async {
    if (token.isEmpty) {
      throw StorageException('Cannot store empty access token',
          code: 'INVALID_TOKEN');
    }
    try {
      await _storage.write(key: _keyAccessToken, value: token);
      _hasStorageError = false;
    } catch (e) {
      AppLogger.e('Failed to write access token', error: e, tag: 'STORAGE');
      _hasStorageError = true;
      rethrow;
    }
  }

  /// Get refresh token
  Future<String?> getRefreshToken() async {
    try {
      final token = await _storage.read(key: _keyRefreshToken);
      // Validate token format (basic sanity check)
      if (token != null && token.isEmpty) {
        AppLogger.w('Empty refresh token found, treating as null',
            tag: 'STORAGE');
        return null;
      }
      return token;
    } catch (e) {
      AppLogger.e('Failed to read refresh token', error: e, tag: 'STORAGE');
      _hasStorageError = true;
      return null;
    }
  }

  /// Set refresh token
  Future<void> setRefreshToken(String token) async {
    if (token.isEmpty) {
      throw StorageException('Cannot store empty refresh token',
          code: 'INVALID_TOKEN');
    }
    try {
      await _storage.write(key: _keyRefreshToken, value: token);
      _hasStorageError = false;
    } catch (e) {
      AppLogger.e('Failed to write refresh token', error: e, tag: 'STORAGE');
      _hasStorageError = true;
      rethrow;
    }
  }

  /// Get token expiry
  Future<DateTime?> getTokenExpiry() async {
    try {
      final value = await _storage.read(key: _keyTokenExpiry);
      if (value == null) return null;
      final expiry = DateTime.tryParse(value);
      if (expiry == null) {
        AppLogger.w('Invalid token expiry format, treating as null',
            tag: 'STORAGE');
        return null;
      }
      return expiry;
    } catch (e) {
      AppLogger.e('Failed to read token expiry', error: e, tag: 'STORAGE');
      _hasStorageError = true;
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
      _hasStorageError = false;
    } catch (e) {
      AppLogger.e('Failed to write token expiry', error: e, tag: 'STORAGE');
      _hasStorageError = true;
      rethrow;
    }
  }

  /// Check if tokens exist and are potentially valid
  Future<bool> hasValidTokens() async {
    try {
      final accessToken = await getAccessToken();
      final refreshToken = await getRefreshToken();
      final expiry = await getTokenExpiry();

      // Must have at least refresh token for session recovery
      if (refreshToken == null) return false;

      // If we have access token but it's expired, we can still refresh
      if (accessToken != null && expiry != null) {
        return true; // Has tokens, can check/refresh if expired
      }

      // Has refresh token, can try to get new access token
      return refreshToken.isNotEmpty;
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
      ]);
      AppLogger.d('Tokens deleted', tag: 'STORAGE');
    } catch (e) {
      AppLogger.e('Failed to delete tokens', error: e, tag: 'STORAGE');
      _hasStorageError = true;
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
      final data = jsonDecode(value);
      if (data is! Map<String, dynamic>) {
        AppLogger.w('Invalid user data format', tag: 'STORAGE');
        return null;
      }
      return data;
    } catch (e) {
      AppLogger.e('Failed to read user data', error: e, tag: 'STORAGE');
      _hasStorageError = true;
      return null;
    }
  }

  /// Set user data
  Future<void> setUserData(Map<String, dynamic> data) async {
    // Validate required fields
    if (!data.containsKey('id') || !data.containsKey('email')) {
      throw StorageException('Invalid user data - missing required fields',
          code: 'INVALID_USER_DATA');
    }
    try {
      await _storage.write(
        key: _keyUserData,
        value: jsonEncode(data),
      );
      _hasStorageError = false;
    } catch (e) {
      AppLogger.e('Failed to write user data', error: e, tag: 'STORAGE');
      _hasStorageError = true;
      rethrow;
    }
  }

  /// Delete user data
  Future<void> deleteUserData() async {
    try {
      await _storage.delete(key: _keyUserData);
      AppLogger.d('User data deleted', tag: 'STORAGE');
    } catch (e) {
      AppLogger.e('Failed to delete user data', error: e, tag: 'STORAGE');
      _hasStorageError = true;
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
      // Reset failure count when enabling/disabling biometric
      if (enabled) {
        await _resetBiometricFailureCount();
      }
    } catch (e) {
      AppLogger.e('Failed to set biometric enabled', error: e, tag: 'STORAGE');
      rethrow;
    }
  }

  /// Record a biometric failure for lockout tracking
  Future<int> recordBiometricFailure() async {
    try {
      final currentCount = await getBiometricFailureCount();
      final newCount = currentCount + 1;

      await _storage.write(
        key: _keyBiometricFailureCount,
        value: newCount.toString(),
      );

      // Check if we should lock out
      if (newCount >= _maxBiometricFailures) {
        final lockoutUntil = DateTime.now().add(_biometricLockoutDuration);
        await _storage.write(
          key: _keyBiometricLockoutUntil,
          value: lockoutUntil.toIso8601String(),
        );
        AppLogger.w('Biometric locked out until $lockoutUntil', tag: 'STORAGE');
      }

      return newCount;
    } catch (e) {
      AppLogger.e('Failed to record biometric failure',
          error: e, tag: 'STORAGE');
      return 0;
    }
  }

  /// Get current biometric failure count
  Future<int> getBiometricFailureCount() async {
    try {
      final value = await _storage.read(key: _keyBiometricFailureCount);
      return value != null ? int.tryParse(value) ?? 0 : 0;
    } catch (e) {
      return 0;
    }
  }

  /// Check if biometric is locked out
  Future<bool> isBiometricLockedOut() async {
    try {
      final lockoutUntilStr =
          await _storage.read(key: _keyBiometricLockoutUntil);
      if (lockoutUntilStr == null) return false;

      final lockoutUntil = DateTime.tryParse(lockoutUntilStr);
      if (lockoutUntil == null) return false;

      if (DateTime.now().isAfter(lockoutUntil)) {
        // Lockout expired, reset
        await _resetBiometricFailureCount();
        return false;
      }

      return true;
    } catch (e) {
      return false;
    }
  }

  /// Get time remaining for biometric lockout
  Future<Duration?> getBiometricLockoutRemaining() async {
    try {
      final lockoutUntilStr =
          await _storage.read(key: _keyBiometricLockoutUntil);
      if (lockoutUntilStr == null) return null;

      final lockoutUntil = DateTime.tryParse(lockoutUntilStr);
      if (lockoutUntil == null) return null;

      final remaining = lockoutUntil.difference(DateTime.now());
      return remaining.isNegative ? null : remaining;
    } catch (e) {
      return null;
    }
  }

  /// Reset biometric failure count and lockout
  Future<void> _resetBiometricFailureCount() async {
    try {
      await _storage.delete(key: _keyBiometricFailureCount);
      await _storage.delete(key: _keyBiometricLockoutUntil);
    } catch (e) {
      AppLogger.e('Failed to reset biometric failure count',
          error: e, tag: 'STORAGE');
    }
  }

  /// Reset biometric lockout (e.g., after successful password login)
  Future<void> resetBiometricLockout() async {
    await _resetBiometricFailureCount();
    AppLogger.i('Biometric lockout reset', tag: 'STORAGE');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Tenant Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get current tenant ID
  Future<String?> getTenantId() async {
    try {
      return await _storage.read(key: _keyTenantId);
    } catch (e) {
      AppLogger.e('Failed to read tenant ID', error: e, tag: 'STORAGE');
      return null;
    }
  }

  /// Set current tenant ID
  Future<void> setTenantId(String tenantId) async {
    if (tenantId.isEmpty) {
      throw StorageException('Cannot store empty tenant ID',
          code: 'INVALID_TENANT_ID');
    }
    try {
      await _storage.write(key: _keyTenantId, value: tenantId);
    } catch (e) {
      AppLogger.e('Failed to set tenant ID', error: e, tag: 'STORAGE');
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
      return DateTime.tryParse(value);
    } catch (e) {
      AppLogger.e('Failed to read last sync time', error: e, tag: 'STORAGE');
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
      AppLogger.e('Failed to set last sync time', error: e, tag: 'STORAGE');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Generic Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Read a value
  Future<String?> read(String key) async {
    _validateKey(key);
    try {
      return await _storage.read(key: key);
    } catch (e) {
      AppLogger.e('Failed to read key: $key', error: e, tag: 'STORAGE');
      return null;
    }
  }

  /// Write a value
  Future<void> write(String key, String value) async {
    _validateKey(key);
    try {
      await _storage.write(key: key, value: value);
    } catch (e) {
      AppLogger.e('Failed to write key: $key', error: e, tag: 'STORAGE');
      rethrow;
    }
  }

  /// Delete a value
  Future<void> delete(String key) async {
    _validateKey(key);
    try {
      await _storage.delete(key: key);
    } catch (e) {
      AppLogger.e('Failed to delete key: $key', error: e, tag: 'STORAGE');
      rethrow;
    }
  }

  /// Check if key exists
  Future<bool> containsKey(String key) async {
    _validateKey(key);
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
      _hasStorageError = false;
      AppLogger.i('Cleared all secure storage', tag: 'STORAGE');
    } catch (e) {
      AppLogger.e('Failed to clear all storage', error: e, tag: 'STORAGE');
      _hasStorageError = true;
      rethrow;
    }
  }

  /// Clear all auth-related data (tokens, user data, session)
  /// Preserves settings like biometric enabled
  Future<void> clearAuthData() async {
    try {
      await Future.wait([
        _storage.delete(key: _keyAccessToken),
        _storage.delete(key: _keyRefreshToken),
        _storage.delete(key: _keyTokenExpiry),
        _storage.delete(key: _keyUserData),
        _storage.delete(key: _keyTenantId),
      ]);
      AppLogger.i('Cleared auth data from secure storage', tag: 'STORAGE');
    } catch (e) {
      AppLogger.e('Failed to clear auth data', error: e, tag: 'STORAGE');
      rethrow;
    }
  }

  /// Get all keys
  Future<List<String>> getAllKeys() async {
    try {
      final all = await _storage.readAll();
      return all.keys.toList();
    } catch (e) {
      AppLogger.e('Failed to get all keys', error: e, tag: 'STORAGE');
      return [];
    }
  }

  /// Validate key format
  void _validateKey(String key) {
    if (key.isEmpty) {
      throw StorageException('Storage key cannot be empty',
          code: 'INVALID_KEY');
    }
    // Prevent potential injection by limiting key characters
    if (!RegExp(r'^[a-zA-Z0-9_-]+$').hasMatch(key)) {
      throw StorageException('Invalid storage key format',
          code: 'INVALID_KEY_FORMAT');
    }
  }

  /// Debug method to print storage info (only in debug mode)
  Future<void> debugPrintStorageInfo() async {
    if (!kDebugMode) return;

    try {
      final keys = await getAllKeys();
      AppLogger.d('Secure storage contains ${keys.length} keys',
          tag: 'STORAGE');
      for (final key in keys) {
        // Don't print actual values for security
        final hasValue = await containsKey(key);
        AppLogger.d('  - $key: ${hasValue ? "has value" : "empty"}',
            tag: 'STORAGE');
      }
    } catch (e) {
      AppLogger.e('Failed to print storage info', error: e, tag: 'STORAGE');
    }
  }
}
