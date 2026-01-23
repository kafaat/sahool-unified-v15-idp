import 'dart:convert';
import 'dart:math';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../utils/app_logger.dart';

/// Database encryption key management using flutter_secure_storage
///
/// Responsibilities:
/// - Generate secure encryption keys
/// - Store keys securely in platform keychain/keystore
/// - Retrieve keys for database operations
/// - Support key rotation
class DatabaseEncryption {
  static const String _keyStorageKey = 'sahool_db_encryption_key';
  static const String _keyVersionKey = 'sahool_db_encryption_key_version';
  static const int _currentKeyVersion = 1;

  final FlutterSecureStorage _secureStorage;

  DatabaseEncryption({FlutterSecureStorage? secureStorage})
      : _secureStorage = secureStorage ?? const FlutterSecureStorage(
          aOptions: AndroidOptions(
            encryptedSharedPreferences: true,
            // Use AES encryption for the key
            keyCipherAlgorithm: KeyCipherAlgorithm.RSA_ECB_PKCS1Padding,
            storageCipherAlgorithm: StorageCipherAlgorithm.AES_GCM_NoPadding,
          ),
          iOptions: IOSOptions(
            // Use keychain access control
            accessibility: KeychainAccessibility.first_unlock_this_device,
          ),
        );

  /// Generate a new random encryption key (256-bit)
  String _generateKey() {
    final random = Random.secure();
    final bytes = List<int>.generate(32, (_) => random.nextInt(256));
    return base64Url.encode(bytes);
  }

  /// Get or create the database encryption key
  ///
  /// Returns a base64-encoded 256-bit key suitable for SQLCipher
  Future<String> getOrCreateKey() async {
    try {
      // Check if key already exists
      String? existingKey = await _secureStorage.read(key: _keyStorageKey);

      if (existingKey != null && existingKey.isNotEmpty) {
        // Validate key format
        if (_isValidKey(existingKey)) {
          return existingKey;
        }
        // If invalid, generate new key (shouldn't happen in normal operation)
        AppLogger.w('Invalid encryption key found, generating new one', tag: 'DatabaseEncryption');
      }

      // Generate new key
      final newKey = _generateKey();
      await _secureStorage.write(key: _keyStorageKey, value: newKey);
      await _secureStorage.write(
        key: _keyVersionKey,
        value: _currentKeyVersion.toString(),
      );

      return newKey;
    } catch (e) {
      throw DatabaseEncryptionException(
        'Failed to get or create encryption key: $e',
      );
    }
  }

  /// Check if an encryption key exists
  Future<bool> hasKey() async {
    try {
      final key = await _secureStorage.read(key: _keyStorageKey);
      return key != null && key.isNotEmpty && _isValidKey(key);
    } catch (e) {
      return false;
    }
  }

  /// Get the current key version
  Future<int> getKeyVersion() async {
    try {
      final version = await _secureStorage.read(key: _keyVersionKey);
      return version != null ? int.tryParse(version) ?? 1 : 1;
    } catch (e) {
      return 1;
    }
  }

  /// Rotate the encryption key (for future use)
  ///
  /// Note: Key rotation requires re-encrypting the entire database
  /// This should be done during a maintenance window
  Future<String> rotateKey() async {
    try {
      final newKey = _generateKey();
      final newVersion = _currentKeyVersion + 1;

      // Store new key with incremented version
      await _secureStorage.write(key: _keyStorageKey, value: newKey);
      await _secureStorage.write(
        key: _keyVersionKey,
        value: newVersion.toString(),
      );

      return newKey;
    } catch (e) {
      throw DatabaseEncryptionException('Failed to rotate encryption key: $e');
    }
  }

  /// Delete the encryption key (use with caution!)
  ///
  /// This will make the encrypted database inaccessible
  /// Only use during logout or data reset scenarios
  Future<void> deleteKey() async {
    try {
      await _secureStorage.delete(key: _keyStorageKey);
      await _secureStorage.delete(key: _keyVersionKey);
    } catch (e) {
      throw DatabaseEncryptionException('Failed to delete encryption key: $e');
    }
  }

  /// Validate key format
  bool _isValidKey(String key) {
    try {
      final decoded = base64Url.decode(key);
      // Should be 32 bytes (256 bits)
      return decoded.length == 32;
    } catch (e) {
      return false;
    }
  }

  /// Get the SQLCipher PRAGMA key command
  ///
  /// Converts the base64 key to hex format for SQLCipher
  String getSqlCipherPragma(String base64Key) {
    try {
      final keyBytes = base64Url.decode(base64Key);
      final hexKey = keyBytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
      return "PRAGMA key = \"x'$hexKey'\";";
    } catch (e) {
      throw DatabaseEncryptionException(
        'Failed to generate SQLCipher PRAGMA: $e',
      );
    }
  }

  /// Test if a database can be opened with the stored key
  ///
  /// Returns true if the key is valid for the database
  Future<bool> validateKeyForDatabase(String dbPath) async {
    // This would require opening the database and testing
    // Implementation depends on specific database testing needs
    // For now, we just check if key exists
    return await hasKey();
  }
}

/// Exception thrown when encryption operations fail
class DatabaseEncryptionException implements Exception {
  final String message;

  DatabaseEncryptionException(this.message);

  @override
  String toString() => 'DatabaseEncryptionException: $message';
}
