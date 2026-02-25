import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:sahool_field_app/core/storage/database_encryption.dart';

class MockFlutterSecureStorage extends Mock implements FlutterSecureStorage {}

void main() {
  group('DatabaseEncryption', () {
    late MockFlutterSecureStorage mockStorage;
    late DatabaseEncryption encryption;

    setUp(() {
      mockStorage = MockFlutterSecureStorage();
      encryption = DatabaseEncryption(secureStorage: mockStorage);
    });

    group('getOrCreateKey', () {
      test('should return existing key when valid key exists', () async {
        // Generate a valid 32-byte key encoded as base64url
        final validKey = base64Url.encode(List.generate(32, (i) => i));

        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => validKey);

        final result = await encryption.getOrCreateKey();
        expect(result, validKey);
      });

      test('should generate new key when no key exists', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.write(
              key: any(named: 'key'),
              value: any(named: 'value'),
            )).thenAnswer((_) async {});

        final result = await encryption.getOrCreateKey();

        // Verify key is valid base64url-encoded 32 bytes
        final decoded = base64Url.decode(result);
        expect(decoded.length, 32);

        // Verify it was stored
        verify(() => mockStorage.write(
              key: 'sahool_db_encryption_key',
              value: any(named: 'value'),
            )).called(1);
      });

      test('should generate new key when existing key is invalid', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => 'invalid_key');
        when(() => mockStorage.write(
              key: any(named: 'key'),
              value: any(named: 'value'),
            )).thenAnswer((_) async {});

        final result = await encryption.getOrCreateKey();

        // Verify key is valid
        final decoded = base64Url.decode(result);
        expect(decoded.length, 32);
      });

      test('should throw DatabaseEncryptionException on storage error',
          () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenThrow(Exception('Storage error'));

        expect(
          () => encryption.getOrCreateKey(),
          throwsA(isA<DatabaseEncryptionException>()),
        );
      });
    });

    group('hasKey', () {
      test('should return true when valid key exists', () async {
        final validKey = base64Url.encode(List.generate(32, (i) => i));
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => validKey);

        expect(await encryption.hasKey(), true);
      });

      test('should return false when no key exists', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => null);

        expect(await encryption.hasKey(), false);
      });

      test('should return false when key is empty', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => '');

        expect(await encryption.hasKey(), false);
      });

      test('should return false when key is invalid format', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => 'not_base64_key!!!');

        expect(await encryption.hasKey(), false);
      });

      test('should return false on storage error', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenThrow(Exception('Storage error'));

        expect(await encryption.hasKey(), false);
      });
    });

    group('getKeyVersion', () {
      test('should return stored version', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key_version'))
            .thenAnswer((_) async => '3');

        expect(await encryption.getKeyVersion(), 3);
      });

      test('should return 1 when no version stored', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key_version'))
            .thenAnswer((_) async => null);

        expect(await encryption.getKeyVersion(), 1);
      });

      test('should return 1 on error', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key_version'))
            .thenThrow(Exception('Error'));

        expect(await encryption.getKeyVersion(), 1);
      });
    });

    group('rotateKey', () {
      test('should generate and store new key', () async {
        when(() => mockStorage.write(
              key: any(named: 'key'),
              value: any(named: 'value'),
            )).thenAnswer((_) async {});

        final newKey = await encryption.rotateKey();

        // Verify key is valid
        final decoded = base64Url.decode(newKey);
        expect(decoded.length, 32);

        // Verify both key and version were stored
        verify(() => mockStorage.write(
              key: 'sahool_db_encryption_key',
              value: any(named: 'value'),
            )).called(1);
        verify(() => mockStorage.write(
              key: 'sahool_db_encryption_key_version',
              value: '2', // _currentKeyVersion + 1
            )).called(1);
      });

      test('should throw on storage error', () async {
        when(() => mockStorage.write(
              key: any(named: 'key'),
              value: any(named: 'value'),
            )).thenThrow(Exception('Storage error'));

        expect(
          () => encryption.rotateKey(),
          throwsA(isA<DatabaseEncryptionException>()),
        );
      });
    });

    group('deleteKey', () {
      test('should delete key and version', () async {
        when(() => mockStorage.delete(key: any(named: 'key')))
            .thenAnswer((_) async {});

        await encryption.deleteKey();

        verify(() => mockStorage.delete(key: 'sahool_db_encryption_key'))
            .called(1);
        verify(() =>
                mockStorage.delete(key: 'sahool_db_encryption_key_version'))
            .called(1);
      });

      test('should throw on storage error', () async {
        when(() => mockStorage.delete(key: any(named: 'key')))
            .thenThrow(Exception('Delete error'));

        expect(
          () => encryption.deleteKey(),
          throwsA(isA<DatabaseEncryptionException>()),
        );
      });
    });

    group('getSqlCipherPragma', () {
      test('should generate valid PRAGMA command', () {
        final key = base64Url.encode(List.generate(32, (i) => i));
        final pragma = encryption.getSqlCipherPragma(key);

        expect(pragma, startsWith('PRAGMA key = "x\''));
        expect(pragma, endsWith('\'";'));
        // Should contain 64 hex characters (32 bytes * 2)
        final hexMatch = RegExp(r"x'([0-9a-f]+)'");
        final match = hexMatch.firstMatch(pragma);
        expect(match, isNotNull);
        expect(match!.group(1)!.length, 64);
      });

      test('should throw on invalid key', () {
        expect(
          () => encryption.getSqlCipherPragma('invalid!!!'),
          throwsA(isA<DatabaseEncryptionException>()),
        );
      });
    });

    group('getHexKey', () {
      test('should convert base64 key to hex', () {
        final key = base64Url.encode(List.generate(32, (i) => i));
        final hex = encryption.getHexKey(key);

        // Should be 64 hex characters
        expect(hex.length, 64);
        expect(RegExp(r'^[0-9a-f]+$').hasMatch(hex), true);
      });

      test('should throw on invalid key', () {
        expect(
          () => encryption.getHexKey('invalid!!!'),
          throwsA(isA<DatabaseEncryptionException>()),
        );
      });

      test('hex should match PRAGMA hex', () {
        final key = base64Url.encode(List.generate(32, (i) => i));
        final hex = encryption.getHexKey(key);
        final pragma = encryption.getSqlCipherPragma(key);

        // PRAGMA should contain the same hex
        expect(pragma, contains(hex));
      });
    });

    group('verifyDatabaseAccess', () {
      test('should return true when valid key exists', () async {
        final validKey = base64Url.encode(List.generate(32, (i) => i));
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => validKey);

        expect(await encryption.verifyDatabaseAccess('/path/to/db'), true);
      });

      test('should return false when no key exists', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenAnswer((_) async => null);

        expect(await encryption.verifyDatabaseAccess('/path/to/db'), false);
      });

      test('should return false on error', () async {
        when(() => mockStorage.read(key: 'sahool_db_encryption_key'))
            .thenThrow(Exception('Error'));

        expect(await encryption.verifyDatabaseAccess('/path/to/db'), false);
      });
    });
  });

  group('DatabaseEncryptionException', () {
    test('should contain message', () {
      final ex = DatabaseEncryptionException('Test error');
      expect(ex.message, 'Test error');
      expect(ex.toString(), 'DatabaseEncryptionException: Test error');
    });
  });
}
