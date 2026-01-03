import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../auth/secure_storage_service.dart';
import '../utils/app_logger.dart';

/// SAHOOL Signing Key Service
/// خدمة مفاتيح توقيع الطلبات
///
/// Features:
/// - Secure key generation and storage
/// - Key rotation support
/// - Device + user-based key derivation
/// - HMAC-SHA256 signing

final signingKeyServiceProvider = Provider<SigningKeyService>((ref) {
  final secureStorage = ref.read(secureStorageProvider);
  return SigningKeyService(secureStorage);
});

class SigningKeyService {
  final SecureStorageService _secureStorage;

  // Storage keys
  static const _keySigningKey = 'signing_key';
  static const _keySigningKeyVersion = 'signing_key_version';
  static const _keySigningKeyCreatedAt = 'signing_key_created_at';
  static const _keyDeviceId = 'device_id';

  // Key rotation settings
  static const int keyRotationDays = 90;
  static const int currentKeyVersion = 1;

  SigningKeyService(this._secureStorage);

  // ═══════════════════════════════════════════════════════════════════════════
  // Key Generation and Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get or generate signing key
  Future<String> getSigningKey() async {
    try {
      // Check if we need to rotate the key
      final shouldRotate = await _shouldRotateKey();

      if (shouldRotate) {
        AppLogger.i('Rotating signing key', tag: 'SigningKeyService');
        return await _generateAndStoreKey();
      }

      // Try to get existing key
      final existingKey = await _secureStorage.read(_keySigningKey);

      if (existingKey != null && existingKey.isNotEmpty) {
        return existingKey;
      }

      // Generate new key if none exists
      AppLogger.i('Generating new signing key', tag: 'SigningKeyService');
      return await _generateAndStoreKey();
    } catch (e) {
      AppLogger.e('Failed to get signing key', tag: 'SigningKeyService', error: e);
      rethrow;
    }
  }

  /// Generate and store a new signing key
  Future<String> _generateAndStoreKey() async {
    try {
      // Get device-specific information
      final deviceId = await _getOrCreateDeviceId();
      final userId = await _getUserId();

      // Generate a random base key
      final random = Random.secure();
      final baseKeyBytes = List<int>.generate(32, (_) => random.nextInt(256));
      final baseKey = base64Url.encode(baseKeyBytes);

      // Derive final key from base key + device ID + user ID
      final derivedKey = _deriveKey(baseKey, deviceId, userId);

      // Store the key
      await _secureStorage.write(_keySigningKey, derivedKey);
      await _secureStorage.write(
        _keySigningKeyVersion,
        currentKeyVersion.toString(),
      );
      await _secureStorage.write(
        _keySigningKeyCreatedAt,
        DateTime.now().toIso8601String(),
      );

      AppLogger.i(
        'Signing key generated and stored',
        tag: 'SigningKeyService',
        data: {
          'version': currentKeyVersion,
          'hasDeviceId': deviceId.isNotEmpty,
          'hasUserId': userId.isNotEmpty,
        },
      );

      return derivedKey;
    } catch (e) {
      AppLogger.e(
        'Failed to generate signing key',
        tag: 'SigningKeyService',
        error: e,
      );
      rethrow;
    }
  }

  /// Derive a key from multiple inputs using HMAC-SHA256
  String _deriveKey(String baseKey, String deviceId, String userId) {
    // Combine all inputs
    final data = '$baseKey:$deviceId:$userId:sahool_v1';

    // Use HMAC-SHA256 for key derivation
    final bytes = utf8.encode(data);
    final hmacKey = utf8.encode('sahool_signing_key_derivation');
    final hmac = Hmac(sha256, hmacKey);
    final digest = hmac.convert(bytes);

    return base64Url.encode(digest.bytes);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Device Identification
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get or create device ID
  Future<String> _getOrCreateDeviceId() async {
    try {
      // Try to get existing device ID
      final existingId = await _secureStorage.read(_keyDeviceId);
      if (existingId != null && existingId.isNotEmpty) {
        return existingId;
      }

      // Generate device ID from device info
      final deviceInfo = DeviceInfoPlugin();
      String deviceId;

      try {
        final androidInfo = await deviceInfo.androidInfo;
        deviceId = '${androidInfo.id}_${androidInfo.device}_${androidInfo.model}';
      } catch (_) {
        try {
          final iosInfo = await deviceInfo.iosInfo;
          deviceId = '${iosInfo.identifierForVendor}_${iosInfo.model}';
        } catch (_) {
          // Fallback: generate random device ID
          final random = Random.secure();
          final bytes = List<int>.generate(16, (_) => random.nextInt(256));
          deviceId = base64Url.encode(bytes);
        }
      }

      // Store device ID
      await _secureStorage.write(_keyDeviceId, deviceId);

      return deviceId;
    } catch (e) {
      AppLogger.e('Failed to get device ID', tag: 'SigningKeyService', error: e);
      // Return empty string as fallback
      return '';
    }
  }

  /// Get user ID for key derivation
  Future<String> _getUserId() async {
    try {
      final userData = await _secureStorage.getUserData();
      if (userData != null && userData['id'] != null) {
        return userData['id'].toString();
      }
      return '';
    } catch (e) {
      AppLogger.e('Failed to get user ID', tag: 'SigningKeyService', error: e);
      return '';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Key Rotation
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if key should be rotated
  Future<bool> _shouldRotateKey() async {
    try {
      // Check key version
      final versionStr = await _secureStorage.read(_keySigningKeyVersion);
      final version = versionStr != null ? int.tryParse(versionStr) : null;

      if (version == null || version < currentKeyVersion) {
        AppLogger.i(
          'Key rotation required: version mismatch',
          tag: 'SigningKeyService',
          data: {'currentVersion': version, 'requiredVersion': currentKeyVersion},
        );
        return true;
      }

      // Check key age
      final createdAtStr = await _secureStorage.read(_keySigningKeyCreatedAt);
      if (createdAtStr == null) {
        return true;
      }

      final createdAt = DateTime.parse(createdAtStr);
      final age = DateTime.now().difference(createdAt);

      if (age.inDays >= keyRotationDays) {
        AppLogger.i(
          'Key rotation required: key expired',
          tag: 'SigningKeyService',
          data: {'age': age.inDays, 'maxAge': keyRotationDays},
        );
        return true;
      }

      return false;
    } catch (e) {
      AppLogger.e(
        'Error checking key rotation',
        tag: 'SigningKeyService',
        error: e,
      );
      // On error, rotate to be safe
      return true;
    }
  }

  /// Force key rotation
  Future<void> rotateKey() async {
    AppLogger.i('Forcing key rotation', tag: 'SigningKeyService');
    await _generateAndStoreKey();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Key Information
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get current key version
  Future<int> getKeyVersion() async {
    try {
      final versionStr = await _secureStorage.read(_keySigningKeyVersion);
      return versionStr != null ? int.parse(versionStr) : 0;
    } catch (e) {
      return 0;
    }
  }

  /// Get key creation date
  Future<DateTime?> getKeyCreatedAt() async {
    try {
      final createdAtStr = await _secureStorage.read(_keySigningKeyCreatedAt);
      if (createdAtStr == null) return null;
      return DateTime.parse(createdAtStr);
    } catch (e) {
      return null;
    }
  }

  /// Get days until key rotation
  Future<int> getDaysUntilRotation() async {
    try {
      final createdAt = await getKeyCreatedAt();
      if (createdAt == null) return 0;

      final age = DateTime.now().difference(createdAt);
      final daysUntilRotation = keyRotationDays - age.inDays;

      return daysUntilRotation > 0 ? daysUntilRotation : 0;
    } catch (e) {
      return 0;
    }
  }

  /// Clear signing key (for logout)
  Future<void> clearKey() async {
    try {
      await Future.wait([
        _secureStorage.delete(_keySigningKey),
        _secureStorage.delete(_keySigningKeyVersion),
        _secureStorage.delete(_keySigningKeyCreatedAt),
      ]);
      AppLogger.i('Signing key cleared', tag: 'SigningKeyService');
    } catch (e) {
      AppLogger.e('Failed to clear signing key', tag: 'SigningKeyService', error: e);
      rethrow;
    }
  }
}
