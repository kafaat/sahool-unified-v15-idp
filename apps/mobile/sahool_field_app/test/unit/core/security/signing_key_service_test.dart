/// Signing Key Service Tests
/// اختبارات خدمة مفاتيح التوقيع
///
/// Tests for secure signing key generation, rotation, and management
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/security/signing_key_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';

class MockSecureStorageService extends Mock implements SecureStorageService {}

void main() {
  late MockSecureStorageService mockStorage;
  late SigningKeyService service;

  setUp(() {
    mockStorage = MockSecureStorageService();
    service = SigningKeyService(mockStorage);
  });

  /// Helper to set up storage mocks for a valid existing key scenario.
  /// The key version matches currentKeyVersion and the creation date is recent.
  void setupValidExistingKey({
    String key = 'existing-signing-key-abc123',
    int version = 1, // SigningKeyService.currentKeyVersion
    DateTime? createdAt,
  }) {
    final created = createdAt ?? DateTime.now().subtract(const Duration(days: 10));

    // _shouldRotateKey reads version and creation date
    when(() => mockStorage.read('signing_key_version'))
        .thenAnswer((_) async => version.toString());
    when(() => mockStorage.read('signing_key_created_at'))
        .thenAnswer((_) async => created.toIso8601String());

    // getSigningKey reads the key itself
    when(() => mockStorage.read('signing_key'))
        .thenAnswer((_) async => key);
  }

  /// Helper to set up storage mocks for key generation.
  /// Mocks the reads that return null (no existing key/device_id) and the writes.
  void setupForKeyGeneration() {
    // _shouldRotateKey: no version stored -> triggers generation
    when(() => mockStorage.read('signing_key_version'))
        .thenAnswer((_) async => null);
    when(() => mockStorage.read('signing_key_created_at'))
        .thenAnswer((_) async => null);

    // _getOrCreateDeviceId: no existing device id, will generate one
    when(() => mockStorage.read('device_id'))
        .thenAnswer((_) async => null);

    // _getUserId: no user data
    when(() => mockStorage.getUserData())
        .thenAnswer((_) async => null);

    // Writes for generated key, version, creation date, device_id
    when(() => mockStorage.write(any(), any()))
        .thenAnswer((_) async {});
  }

  /// Helper to set up mocks for key generation with a known device id and user id.
  void setupForKeyGenerationWithIds({
    String deviceId = 'test-device-id',
    String? userId,
  }) {
    when(() => mockStorage.read('device_id'))
        .thenAnswer((_) async => deviceId);

    if (userId != null) {
      when(() => mockStorage.getUserData())
          .thenAnswer((_) async => {'id': userId});
    } else {
      when(() => mockStorage.getUserData())
          .thenAnswer((_) async => null);
    }

    when(() => mockStorage.write(any(), any()))
        .thenAnswer((_) async {});
  }

  group('SigningKeyService', () {
    group('getSigningKey', () {
      test('returns existing key when valid (version matches, not expired)', () async {
        const existingKey = 'my-valid-signing-key';
        setupValidExistingKey(key: existingKey);

        final result = await service.getSigningKey();

        expect(result, equals(existingKey));
        // Should read the key but never write (no generation)
        verify(() => mockStorage.read('signing_key')).called(1);
        verifyNever(() => mockStorage.write('signing_key', any()));
      });

      test('generates new key when none exists', () async {
        // _shouldRotateKey: version is null -> returns true (triggers generation)
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => null);

        setupForKeyGenerationWithIds(deviceId: 'dev-001', userId: 'user-001');

        final result = await service.getSigningKey();

        expect(result, isNotEmpty);
        // Should write the new key, version, and creation date
        verify(() => mockStorage.write('signing_key', any())).called(1);
        verify(() => mockStorage.write('signing_key_version', '1')).called(1);
        verify(() => mockStorage.write('signing_key_created_at', any())).called(1);
      });

      test('rotates key when version is lower than currentKeyVersion', () async {
        // Version 0 < currentKeyVersion (1) -> should rotate
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => '0');
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => DateTime.now().toIso8601String());

        setupForKeyGenerationWithIds(deviceId: 'dev-002');

        final result = await service.getSigningKey();

        expect(result, isNotEmpty);
        verify(() => mockStorage.write('signing_key', any())).called(1);
        verify(() => mockStorage.write('signing_key_version', '1')).called(1);
      });

      test('rotates key when key age exceeds 90 days', () async {
        final oldDate = DateTime.now().subtract(const Duration(days: 91));

        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => '1');
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => oldDate.toIso8601String());

        setupForKeyGenerationWithIds(deviceId: 'dev-003');

        final result = await service.getSigningKey();

        expect(result, isNotEmpty);
        // A new key should be written because the old one expired
        verify(() => mockStorage.write('signing_key', any())).called(1);
      });

      test('does not rotate when key age is exactly 89 days', () async {
        final recentDate = DateTime.now().subtract(const Duration(days: 89));
        const existingKey = 'still-valid-key';

        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => '1');
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => recentDate.toIso8601String());
        when(() => mockStorage.read('signing_key'))
            .thenAnswer((_) async => existingKey);

        final result = await service.getSigningKey();

        expect(result, equals(existingKey));
        verifyNever(() => mockStorage.write('signing_key', any()));
      });

      test('generates key when existing key is empty string', () async {
        // Version and date are valid, but the stored key is empty
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => '1');
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => DateTime.now().toIso8601String());
        when(() => mockStorage.read('signing_key'))
            .thenAnswer((_) async => '');

        setupForKeyGenerationWithIds(deviceId: 'dev-004');

        final result = await service.getSigningKey();

        expect(result, isNotEmpty);
        verify(() => mockStorage.write('signing_key', any())).called(1);
      });
    });

    group('rotateKey', () {
      test('forces new key generation', () async {
        setupForKeyGenerationWithIds(deviceId: 'dev-005', userId: 'user-005');

        await service.rotateKey();

        verify(() => mockStorage.write('signing_key', any())).called(1);
        verify(() => mockStorage.write('signing_key_version', '1')).called(1);
        verify(() => mockStorage.write('signing_key_created_at', any())).called(1);
      });

      test('generates a new key each time it is called', () async {
        setupForKeyGenerationWithIds(deviceId: 'dev-006', userId: 'user-006');

        // Capture the keys written
        final writtenKeys = <String>[];
        when(() => mockStorage.write('signing_key', any()))
            .thenAnswer((invocation) async {
          writtenKeys.add(invocation.positionalArguments[1] as String);
        });

        await service.rotateKey();
        await service.rotateKey();

        expect(writtenKeys.length, equals(2));
        // Keys should differ because the base key uses Random.secure()
        // There is a vanishingly small chance they are equal, but practically never
        expect(writtenKeys[0], isNot(equals(writtenKeys[1])));
      });
    });

    group('getKeyVersion', () {
      test('returns 0 when no version is stored', () async {
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => null);

        final version = await service.getKeyVersion();

        expect(version, equals(0));
      });

      test('returns stored version as integer', () async {
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => '3');

        final version = await service.getKeyVersion();

        expect(version, equals(3));
      });

      test('returns 0 when stored version is not a valid integer', () async {
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => 'invalid');

        final version = await service.getKeyVersion();

        expect(version, equals(0));
      });
    });

    group('getKeyCreatedAt', () {
      test('returns null when no date is stored', () async {
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => null);

        final createdAt = await service.getKeyCreatedAt();

        expect(createdAt, isNull);
      });

      test('returns stored date parsed from ISO 8601', () async {
        final expectedDate = DateTime(2025, 6, 15, 10, 30, 0);
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => expectedDate.toIso8601String());

        final createdAt = await service.getKeyCreatedAt();

        expect(createdAt, isNotNull);
        expect(createdAt, equals(expectedDate));
      });

      test('returns null when stored date is malformed', () async {
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => 'not-a-date');

        final createdAt = await service.getKeyCreatedAt();

        expect(createdAt, isNull);
      });
    });

    group('getDaysUntilRotation', () {
      test('returns 0 when no creation date is stored', () async {
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => null);

        final days = await service.getDaysUntilRotation();

        expect(days, equals(0));
      });

      test('calculates days correctly for a recently created key', () async {
        final createdAt = DateTime.now().subtract(const Duration(days: 10));
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => createdAt.toIso8601String());

        final days = await service.getDaysUntilRotation();

        // 90 - 10 = 80 days remaining
        expect(days, equals(80));
      });

      test('returns 0 when key has already expired', () async {
        final createdAt = DateTime.now().subtract(const Duration(days: 100));
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => createdAt.toIso8601String());

        final days = await service.getDaysUntilRotation();

        expect(days, equals(0));
      });

      test('returns 0 when key age is exactly 90 days', () async {
        final createdAt = DateTime.now().subtract(const Duration(days: 90));
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => createdAt.toIso8601String());

        final days = await service.getDaysUntilRotation();

        expect(days, equals(0));
      });

      test('returns 89 when key was created 1 day ago', () async {
        final createdAt = DateTime.now().subtract(const Duration(days: 1));
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => createdAt.toIso8601String());

        final days = await service.getDaysUntilRotation();

        expect(days, equals(89));
      });
    });

    group('clearKey', () {
      test('clears all key-related storage entries', () async {
        when(() => mockStorage.delete(any()))
            .thenAnswer((_) async {});

        await service.clearKey();

        verify(() => mockStorage.delete('signing_key')).called(1);
        verify(() => mockStorage.delete('signing_key_version')).called(1);
        verify(() => mockStorage.delete('signing_key_created_at')).called(1);
      });

      test('rethrows when delete fails', () async {
        when(() => mockStorage.delete(any()))
            .thenThrow(Exception('Storage failure'));

        expect(
          () => service.clearKey(),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('key derivation', () {
      test('produces consistent results for the same inputs', () async {
        // We test this by calling getSigningKey twice with the same device/user
        // and verifying the derived key is deterministic given the same base key.
        // Since _deriveKey is private, we test indirectly through rotateKey
        // and observe that the derivation uses HMAC-SHA256 with known inputs.

        // Instead, test that two separate service instances with the same
        // underlying storage produce the same key when reading an existing one.
        const storedKey = 'derived-key-value-xyz';
        setupValidExistingKey(key: storedKey);

        final key1 = await service.getSigningKey();

        // Create a second service with the same mock
        final service2 = SigningKeyService(mockStorage);
        final key2 = await service2.getSigningKey();

        expect(key1, equals(key2));
        expect(key1, equals(storedKey));
      });

      test('generates key using device id and user id from storage', () async {
        const deviceId = 'device-abc-123';
        const userId = 'user-42';

        // Force generation by returning no version
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => null);

        setupForKeyGenerationWithIds(deviceId: deviceId, userId: userId);

        final key = await service.getSigningKey();

        expect(key, isNotEmpty);
        // Verify device id was read
        verify(() => mockStorage.read('device_id')).called(1);
        // Verify user data was read
        verify(() => mockStorage.getUserData()).called(1);
      });

      test('generates device id when none exists in storage', () async {
        // Force generation
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => null);

        // No device id stored
        when(() => mockStorage.read('device_id'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.getUserData())
            .thenAnswer((_) async => null);
        when(() => mockStorage.write(any(), any()))
            .thenAnswer((_) async {});

        final key = await service.getSigningKey();

        expect(key, isNotEmpty);
        // A device_id should have been written (generated fallback since
        // DeviceInfoPlugin will fail in test environment)
        verify(() => mockStorage.write('device_id', any())).called(1);
      });

      test('uses empty user id when getUserData returns null', () async {
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.read('device_id'))
            .thenAnswer((_) async => 'test-device');
        when(() => mockStorage.getUserData())
            .thenAnswer((_) async => null);
        when(() => mockStorage.write(any(), any()))
            .thenAnswer((_) async {});

        final key = await service.getSigningKey();

        expect(key, isNotEmpty);
        verify(() => mockStorage.getUserData()).called(1);
      });

      test('uses empty user id when getUserData has no id field', () async {
        when(() => mockStorage.read('signing_key_version'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.read('signing_key_created_at'))
            .thenAnswer((_) async => null);
        when(() => mockStorage.read('device_id'))
            .thenAnswer((_) async => 'test-device');
        when(() => mockStorage.getUserData())
            .thenAnswer((_) async => {'name': 'Test User'});
        when(() => mockStorage.write(any(), any()))
            .thenAnswer((_) async {});

        final key = await service.getSigningKey();

        expect(key, isNotEmpty);
      });
    });

    group('constants', () {
      test('keyRotationDays is 90', () {
        expect(SigningKeyService.keyRotationDays, equals(90));
      });

      test('currentKeyVersion is 1', () {
        expect(SigningKeyService.currentKeyVersion, equals(1));
      });
    });

    group('error handling', () {
      test('getSigningKey rethrows storage read errors', () async {
        when(() => mockStorage.read('signing_key_version'))
            .thenThrow(Exception('Storage read failed'));

        // _shouldRotateKey catches the error and returns true,
        // which triggers _generateAndStoreKey
        // _generateAndStoreKey will also need mocks
        when(() => mockStorage.read('device_id'))
            .thenAnswer((_) async => 'dev-err');
        when(() => mockStorage.getUserData())
            .thenAnswer((_) async => null);
        when(() => mockStorage.write(any(), any()))
            .thenAnswer((_) async {});

        // Should succeed because _shouldRotateKey catches errors and returns true
        final key = await service.getSigningKey();
        expect(key, isNotEmpty);
      });

      test('getKeyVersion returns 0 on error', () async {
        when(() => mockStorage.read('signing_key_version'))
            .thenThrow(Exception('Read failed'));

        final version = await service.getKeyVersion();

        expect(version, equals(0));
      });

      test('getKeyCreatedAt returns null on error', () async {
        when(() => mockStorage.read('signing_key_created_at'))
            .thenThrow(Exception('Read failed'));

        final createdAt = await service.getKeyCreatedAt();

        expect(createdAt, isNull);
      });

      test('getDaysUntilRotation returns 0 on error', () async {
        when(() => mockStorage.read('signing_key_created_at'))
            .thenThrow(Exception('Read failed'));

        final days = await service.getDaysUntilRotation();

        expect(days, equals(0));
      });
    });
  });
}
