/// Database Encryption Tests - SQLCipher Integration
/// اختبارات تشفير قاعدة البيانات - تكامل SQLCipher
///
/// Tests for:
/// - Encryption key generation and validation
/// - Secure key storage (mocked)
/// - SQLCipher pragma generation
/// - Key rotation support
/// - Database encryption verification
///
/// Note: Full SQLCipher tests require native libraries.
/// These tests focus on the encryption key management logic.
import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

/// Mock secure storage for testing
class MockSecureStorage extends Mock {
  final Map<String, String> _storage = {};

  Future<String?> read({required String key}) async {
    return _storage[key];
  }

  Future<void> write({required String key, required String value}) async {
    _storage[key] = value;
  }

  Future<void> delete({required String key}) async {
    _storage.remove(key);
  }

  void clear() {
    _storage.clear();
  }

  bool containsKey(String key) {
    return _storage.containsKey(key);
  }
}

/// Database encryption key management for testing
/// (Simplified version of production DatabaseEncryption)
class DatabaseEncryptionTest {
  static const String _keyStorageKey = 'sahool_db_encryption_key';
  static const String _keyVersionKey = 'sahool_db_encryption_key_version';
  static const int _currentKeyVersion = 1;
  static const int _keyLengthBytes = 32; // 256 bits

  final MockSecureStorage _secureStorage;
  Completer<String>? _keyCreationLock;

  DatabaseEncryptionTest(this._secureStorage);

  /// Generate a new random encryption key (256-bit)
  String generateKey() {
    final random = Random.secure();
    final bytes = List<int>.generate(_keyLengthBytes, (_) => random.nextInt(256));
    return base64Url.encode(bytes);
  }

  /// Get or create the database encryption key
  /// Uses a Completer-based lock to handle concurrent calls safely
  Future<String> getOrCreateKey() async {
    // If another call is already creating a key, wait for it
    if (_keyCreationLock != null) {
      return _keyCreationLock!.future;
    }

    // Set lock synchronously BEFORE any await to prevent concurrent generation
    final completer = Completer<String>();
    _keyCreationLock = completer;

    try {
      String? existingKey = await _secureStorage.read(key: _keyStorageKey);

      if (existingKey != null && existingKey.isNotEmpty) {
        if (isValidKey(existingKey)) {
          completer.complete(existingKey);
          return existingKey;
        }
      }

      // Generate new key
      final newKey = generateKey();
      await _secureStorage.write(key: _keyStorageKey, value: newKey);
      await _secureStorage.write(
        key: _keyVersionKey,
        value: _currentKeyVersion.toString(),
      );

      completer.complete(newKey);
      return newKey;
    } catch (e) {
      completer.completeError(e);
      rethrow;
    } finally {
      _keyCreationLock = null;
    }
  }

  /// Check if an encryption key exists
  Future<bool> hasKey() async {
    final key = await _secureStorage.read(key: _keyStorageKey);
    return key != null && key.isNotEmpty && isValidKey(key);
  }

  /// Get the current key version
  Future<int> getKeyVersion() async {
    final version = await _secureStorage.read(key: _keyVersionKey);
    return version != null ? int.tryParse(version) ?? 1 : 1;
  }

  /// Rotate the encryption key
  Future<String> rotateKey() async {
    final currentVersion = await getKeyVersion();
    final newKey = generateKey();
    final newVersion = currentVersion + 1;

    await _secureStorage.write(key: _keyStorageKey, value: newKey);
    await _secureStorage.write(key: _keyVersionKey, value: newVersion.toString());

    return newKey;
  }

  /// Delete the encryption key
  Future<void> deleteKey() async {
    await _secureStorage.delete(key: _keyStorageKey);
    await _secureStorage.delete(key: _keyVersionKey);
  }

  /// Validate key format
  bool isValidKey(String key) {
    try {
      final decoded = base64Url.decode(key);
      return decoded.length == _keyLengthBytes;
    } catch (e) {
      return false;
    }
  }

  /// Get the SQLCipher PRAGMA key command
  String getSqlCipherPragma(String base64Key) {
    final keyBytes = base64Url.decode(base64Key);
    final hexKey = keyBytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return "PRAGMA key = \"x'$hexKey'\";";
  }

  /// Verify key can decrypt (mock implementation)
  Future<bool> verifyKeyForDatabase(String dbPath) async {
    return await hasKey();
  }
}

/// Exception for encryption errors
class DatabaseEncryptionException implements Exception {
  final String message;
  DatabaseEncryptionException(this.message);

  @override
  String toString() => 'DatabaseEncryptionException: $message';
}

void main() {
  group('Key Generation', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    test('should generate valid 256-bit key', () {
      final key = encryption.generateKey();

      expect(key, isNotEmpty);
      expect(encryption.isValidKey(key), isTrue);

      final decoded = base64Url.decode(key);
      expect(decoded.length, equals(32)); // 256 bits = 32 bytes
    });

    test('should generate unique keys', () {
      final keys = <String>{};

      for (int i = 0; i < 100; i++) {
        final key = encryption.generateKey();
        expect(keys.contains(key), isFalse, reason: 'Duplicate key generated');
        keys.add(key);
      }
    });

    test('should generate cryptographically random keys', () {
      // Generate multiple keys and check they're not similar
      final key1 = encryption.generateKey();
      final key2 = encryption.generateKey();

      expect(key1, isNot(equals(key2)));

      // Check byte distribution (simple entropy check)
      final bytes1 = base64Url.decode(key1);
      final bytes2 = base64Url.decode(key2);

      // Keys should differ significantly
      int differentBytes = 0;
      for (int i = 0; i < bytes1.length; i++) {
        if (bytes1[i] != bytes2[i]) differentBytes++;
      }

      // Most bytes should be different
      expect(differentBytes, greaterThan(bytes1.length ~/ 2));
    });
  });

  group('Key Validation', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    test('should validate correct key format', () {
      final key = encryption.generateKey();
      expect(encryption.isValidKey(key), isTrue);
    });

    test('should reject empty key', () {
      expect(encryption.isValidKey(''), isFalse);
    });

    test('should reject key with wrong length', () {
      // 16 bytes instead of 32
      final shortKey = base64Url.encode(List<int>.generate(16, (i) => i));
      expect(encryption.isValidKey(shortKey), isFalse);

      // 64 bytes instead of 32
      final longKey = base64Url.encode(List<int>.generate(64, (i) => i));
      expect(encryption.isValidKey(longKey), isFalse);
    });

    test('should reject invalid base64', () {
      expect(encryption.isValidKey('not-valid-base64!!!'), isFalse);
      expect(encryption.isValidKey('====='), isFalse);
    });

    test('should accept base64url encoded keys', () {
      // Base64url uses - and _ instead of + and /
      final bytes = List<int>.generate(32, (i) => i * 8); // Will produce - and _
      final key = base64Url.encode(bytes);
      expect(encryption.isValidKey(key), isTrue);
    });
  });

  group('Key Storage', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    tearDown(() {
      storage.clear();
    });

    test('should create new key when none exists', () async {
      expect(await encryption.hasKey(), isFalse);

      final key = await encryption.getOrCreateKey();

      expect(key, isNotEmpty);
      expect(encryption.isValidKey(key), isTrue);
      expect(await encryption.hasKey(), isTrue);
    });

    test('should return existing key on subsequent calls', () async {
      final key1 = await encryption.getOrCreateKey();
      final key2 = await encryption.getOrCreateKey();

      expect(key1, equals(key2));
    });

    test('should store key version', () async {
      await encryption.getOrCreateKey();

      final version = await encryption.getKeyVersion();
      expect(version, equals(1));
    });

    test('should delete key', () async {
      await encryption.getOrCreateKey();
      expect(await encryption.hasKey(), isTrue);

      await encryption.deleteKey();
      expect(await encryption.hasKey(), isFalse);
    });

    test('should regenerate key after deletion', () async {
      final originalKey = await encryption.getOrCreateKey();
      await encryption.deleteKey();
      final newKey = await encryption.getOrCreateKey();

      expect(newKey, isNot(equals(originalKey)));
    });
  });

  group('Key Rotation', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() async {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
      await encryption.getOrCreateKey(); // Initialize with first key
    });

    tearDown(() {
      storage.clear();
    });

    test('should rotate key', () async {
      final originalKey = await encryption.getOrCreateKey();
      final newKey = await encryption.rotateKey();

      expect(newKey, isNot(equals(originalKey)));
      expect(encryption.isValidKey(newKey), isTrue);
    });

    test('should increment version on rotation', () async {
      expect(await encryption.getKeyVersion(), equals(1));

      await encryption.rotateKey();
      expect(await encryption.getKeyVersion(), equals(2));

      await encryption.rotateKey();
      expect(await encryption.getKeyVersion(), equals(3));
    });

    test('should persist rotated key', () async {
      final rotatedKey = await encryption.rotateKey();
      final retrievedKey = await encryption.getOrCreateKey();

      expect(retrievedKey, equals(rotatedKey));
    });
  });

  group('SQLCipher PRAGMA Generation', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    test('should generate valid PRAGMA command', () {
      final key = encryption.generateKey();
      final pragma = encryption.getSqlCipherPragma(key);

      expect(pragma, startsWith("PRAGMA key = \"x'"));
      expect(pragma, endsWith("'\";"));
    });

    test('should convert to correct hex format', () {
      // Use known bytes for predictable hex output
      final bytes = List<int>.generate(32, (i) => i);
      final key = base64Url.encode(bytes);
      final pragma = encryption.getSqlCipherPragma(key);

      // First few bytes should be 00, 01, 02, etc.
      expect(pragma, contains('000102030405'));
    });

    test('should produce consistent PRAGMA for same key', () {
      final key = encryption.generateKey();
      final pragma1 = encryption.getSqlCipherPragma(key);
      final pragma2 = encryption.getSqlCipherPragma(key);

      expect(pragma1, equals(pragma2));
    });

    test('should produce different PRAGMA for different keys', () {
      final key1 = encryption.generateKey();
      final key2 = encryption.generateKey();
      final pragma1 = encryption.getSqlCipherPragma(key1);
      final pragma2 = encryption.getSqlCipherPragma(key2);

      expect(pragma1, isNot(equals(pragma2)));
    });

    test('PRAGMA hex key should be 64 characters', () {
      final key = encryption.generateKey();
      final pragma = encryption.getSqlCipherPragma(key);

      // Extract hex key from PRAGMA
      final match = RegExp(r"x'([a-f0-9]+)'").firstMatch(pragma);
      expect(match, isNotNull);

      final hexKey = match!.group(1)!;
      expect(hexKey.length, equals(64)); // 32 bytes * 2 hex chars per byte
    });
  });

  group('Error Handling', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    test('should handle invalid stored key gracefully', () async {
      // Manually store invalid key
      await storage.write(key: 'sahool_db_encryption_key', value: 'invalid');

      // Should generate new key instead of returning invalid one
      final key = await encryption.getOrCreateKey();
      expect(encryption.isValidKey(key), isTrue);
    });

    test('should handle corrupted key version', () async {
      await storage.write(key: 'sahool_db_encryption_key_version', value: 'not_a_number');

      final version = await encryption.getKeyVersion();
      expect(version, equals(1)); // Default fallback
    });
  });

  group('Security Properties', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    test('key should have sufficient entropy', () {
      // Generate multiple keys and check byte distribution
      for (int i = 0; i < 10; i++) {
        final key = encryption.generateKey();
        final bytes = base64Url.decode(key);

        // Check that we have a reasonable distribution of values
        final uniqueBytes = bytes.toSet();
        expect(
          uniqueBytes.length,
          greaterThan(15), // At least 15 unique bytes out of 32
          reason: 'Key should have good entropy',
        );
      }
    });

    test('key generation should be non-deterministic', () {
      // Create new encryption instance and generate key
      final encryption1 = DatabaseEncryptionTest(MockSecureStorage());
      final encryption2 = DatabaseEncryptionTest(MockSecureStorage());

      final key1 = encryption1.generateKey();
      final key2 = encryption2.generateKey();

      expect(key1, isNot(equals(key2)));
    });

    test('PRAGMA should properly escape key', () {
      final key = encryption.generateKey();
      final pragma = encryption.getSqlCipherPragma(key);

      // Check proper escaping
      expect(pragma, contains("\"x'"));
      expect(pragma, contains("'\""));

      // Should not contain dangerous characters outside quotes
      final hexPart = pragma.substring(
        pragma.indexOf("x'") + 2,
        pragma.lastIndexOf("'"),
      );
      expect(hexPart, matches(RegExp(r'^[a-f0-9]+$')));
    });
  });

  group('Migration Support', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() async {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    test('should support checking if key exists before migration', () async {
      expect(await encryption.hasKey(), isFalse);

      // Simulate migration scenario where we check before creating
      if (!await encryption.hasKey()) {
        await encryption.getOrCreateKey();
      }

      expect(await encryption.hasKey(), isTrue);
    });

    test('should verify key for database', () async {
      await encryption.getOrCreateKey();

      final isValid = await encryption.verifyKeyForDatabase('/path/to/db');
      expect(isValid, isTrue);
    });

    test('should fail verification if no key exists', () async {
      final isValid = await encryption.verifyKeyForDatabase('/path/to/db');
      expect(isValid, isFalse);
    });
  });

  group('Concurrent Access', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    test('should handle concurrent getOrCreateKey calls', () async {
      // Simulate multiple concurrent calls
      final futures = List.generate(
        10,
        (_) => encryption.getOrCreateKey(),
      );

      final results = await Future.wait(futures);

      // All results should be the same key
      final firstKey = results.first;
      expect(results.every((k) => k == firstKey), isTrue);
    });
  });

  group('Key Format Compatibility', () {
    test('should use base64url encoding (URL-safe)', () {
      final storage = MockSecureStorage();
      final encryption = DatabaseEncryptionTest(storage);

      for (int i = 0; i < 100; i++) {
        final key = encryption.generateKey();

        // Base64url should not contain + or /
        expect(key.contains('+'), isFalse);
        expect(key.contains('/'), isFalse);

        // Should be valid base64url
        expect(() => base64Url.decode(key), returnsNormally);
      }
    });

    test('should handle padding correctly', () {
      final storage = MockSecureStorage();
      final encryption = DatabaseEncryptionTest(storage);

      final key = encryption.generateKey();

      // Base64 of 32 bytes should be 43 chars without padding (32 * 8 / 6 = 42.67)
      // With padding it would be 44 chars
      // base64Url.encode handles this automatically
      expect(encryption.isValidKey(key), isTrue);
    });
  });

  group('DatabaseEncryptionException', () {
    test('should create exception with message', () {
      final exception = DatabaseEncryptionException('Test error');
      expect(exception.message, equals('Test error'));
      expect(exception.toString(), contains('Test error'));
    });
  });
}

/// Integration-like tests for encryption workflow
void encryptionWorkflowTests() {
  group('Encryption Workflow', () {
    late MockSecureStorage storage;
    late DatabaseEncryptionTest encryption;

    setUp(() {
      storage = MockSecureStorage();
      encryption = DatabaseEncryptionTest(storage);
    });

    test('complete workflow: create, use, rotate, verify', () async {
      // Step 1: First-time setup (no key exists)
      expect(await encryption.hasKey(), isFalse);

      // Step 2: Create key for new database
      final initialKey = await encryption.getOrCreateKey();
      expect(encryption.isValidKey(initialKey), isTrue);
      expect(await encryption.getKeyVersion(), equals(1));

      // Step 3: Use key for database operations
      final pragma = encryption.getSqlCipherPragma(initialKey);
      expect(pragma, isNotEmpty);

      // Step 4: Simulate app restart - key should persist
      final retrievedKey = await encryption.getOrCreateKey();
      expect(retrievedKey, equals(initialKey));

      // Step 5: Key rotation (e.g., security policy)
      final rotatedKey = await encryption.rotateKey();
      expect(rotatedKey, isNot(equals(initialKey)));
      expect(await encryption.getKeyVersion(), equals(2));

      // Step 6: Verify new key works
      expect(encryption.isValidKey(rotatedKey), isTrue);
      final newPragma = encryption.getSqlCipherPragma(rotatedKey);
      expect(newPragma, isNot(equals(pragma)));
    });

    test('workflow: logout and data reset', () async {
      // Setup: User has active encrypted database
      await encryption.getOrCreateKey();
      expect(await encryption.hasKey(), isTrue);

      // Logout: Clear encryption key (database becomes inaccessible)
      await encryption.deleteKey();
      expect(await encryption.hasKey(), isFalse);

      // New session: Fresh key for new data
      final newKey = await encryption.getOrCreateKey();
      expect(encryption.isValidKey(newKey), isTrue);
    });

    test('workflow: migration from unencrypted database', () async {
      // Step 1: Check if migration is needed (no key = old unencrypted db)
      final needsMigration = !await encryption.hasKey();
      expect(needsMigration, isTrue);

      // Step 2: Generate key for encryption
      final key = await encryption.getOrCreateKey();

      // Step 3: Build migration PRAGMA
      // In real scenario: ATTACH new encrypted db, copy data, verify
      final encryptPragma = encryption.getSqlCipherPragma(key);
      expect(encryptPragma, contains("PRAGMA key"));

      // Step 4: Migration complete - key is now stored
      expect(await encryption.hasKey(), isTrue);
    });
  });
}
