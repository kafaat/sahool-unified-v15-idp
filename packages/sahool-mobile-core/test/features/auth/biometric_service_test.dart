/// Biometric Service Tests
/// اختبارات خدمة المصادقة البيومترية
///
/// Comprehensive tests for BiometricService covering:
/// - Availability checks
/// - Authentication flow
/// - Enable/Disable biometric
/// - Error handling
/// - Platform-specific behavior

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:local_auth/local_auth.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_mobile_core/core/auth/biometric_service.dart';
import 'package:sahool_mobile_core/core/auth/secure_storage_service.dart';

import 'auth_fixtures.dart';
import 'auth_mocks.dart';

/// Mock LocalAuthentication using mocktail (works with local_auth v2.3.0+)
class MockLocalAuthentication extends Mock implements LocalAuthentication {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late BiometricService biometricService;
  late MockSecureStorageService mockSecureStorage;
  late MockLocalAuthentication mockLocalAuth;

  setUpAll(() {
    registerAuthFallbackValues();
    registerFallbackValue(const AuthenticationOptions());
  });

  setUp(() {
    mockSecureStorage = MockSecureStorageService();
    mockSecureStorage.setupDefaults();

    mockLocalAuth = MockLocalAuthentication();

    // Default mock behavior
    when(() => mockLocalAuth.canCheckBiometrics).thenAnswer((_) async => true);
    when(() => mockLocalAuth.isDeviceSupported()).thenAnswer((_) async => true);
    when(() => mockLocalAuth.getAvailableBiometrics())
        .thenAnswer((_) async => [BiometricType.fingerprint]);
    when(() => mockLocalAuth.authenticate(
          localizedReason: any(named: 'localizedReason'),
          options: any(named: 'options'),
        )).thenAnswer((_) async => true);
    when(() => mockLocalAuth.stopAuthentication()).thenAnswer((_) async => true);

    biometricService = BiometricService(
      secureStorage: mockSecureStorage,
      localAuth: mockLocalAuth,
    );
  });

  tearDown(() {
    mockSecureStorage.clearStorage();
  });

  group('BiometricService', () {
    group('isAvailable', () {
      test('should return true when biometrics are available', () async {
        // Arrange - defaults already set to true/true

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return true when device supported but cannot check biometrics', () async {
        // Arrange
        when(() => mockLocalAuth.canCheckBiometrics).thenAnswer((_) async => false);
        when(() => mockLocalAuth.isDeviceSupported()).thenAnswer((_) async => true);

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return true when can check biometrics but device not supported', () async {
        // Arrange
        when(() => mockLocalAuth.canCheckBiometrics).thenAnswer((_) async => true);
        when(() => mockLocalAuth.isDeviceSupported()).thenAnswer((_) async => false);

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return false when neither is available', () async {
        // Arrange
        when(() => mockLocalAuth.canCheckBiometrics).thenAnswer((_) async => false);
        when(() => mockLocalAuth.isDeviceSupported()).thenAnswer((_) async => false);

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isFalse);
      });

      test('should return false on platform exception', () async {
        // Arrange
        when(() => mockLocalAuth.canCheckBiometrics)
            .thenThrow(PlatformException(code: 'ERROR', message: 'Platform error'));

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isFalse);
      });
    });

    group('getAvailableBiometrics', () {
      test('should return list of available biometric types', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.fingerprint, BiometricType.face]);

        // Act
        final result = await biometricService.getAvailableBiometrics();

        // Assert
        expect(result, isA<List<BiometricType>>());
        expect(result.length, 2);
      });

      test('should return empty list on error', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenThrow(PlatformException(code: 'ERROR', message: 'Cannot get biometrics'));

        // Act
        final result = await biometricService.getAvailableBiometrics();

        // Assert
        expect(result, isEmpty);
      });

      test('should return empty list when no biometrics enrolled', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => []);

        // Act
        final result = await biometricService.getAvailableBiometrics();

        // Assert
        expect(result, isEmpty);
      });
    });

    group('isFingerprintAvailable', () {
      test('should return true when fingerprint is available', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.fingerprint]);

        // Act
        final result = await biometricService.isFingerprintAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return false when only face ID is available', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.face]);

        // Act
        final result = await biometricService.isFingerprintAvailable();

        // Assert
        expect(result, isFalse);
      });

      test('should return false when no biometrics available', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => []);

        // Act
        final result = await biometricService.isFingerprintAvailable();

        // Assert
        expect(result, isFalse);
      });
    });

    group('isFaceIdAvailable', () {
      test('should return true when face ID is available', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.face]);

        // Act
        final result = await biometricService.isFaceIdAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return false when only fingerprint is available', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.fingerprint]);

        // Act
        final result = await biometricService.isFaceIdAvailable();

        // Assert
        expect(result, isFalse);
      });
    });

    group('isEnabled', () {
      test('should return true when biometric is enabled in storage', () async {
        // Arrange
        when(() => mockSecureStorage.isBiometricEnabled())
            .thenAnswer((_) async => true);

        // Act
        final result = await biometricService.isEnabled();

        // Assert
        expect(result, isTrue);
        verify(() => mockSecureStorage.isBiometricEnabled()).called(1);
      });

      test('should return false when biometric is not enabled', () async {
        // Arrange
        when(() => mockSecureStorage.isBiometricEnabled())
            .thenAnswer((_) async => false);

        // Act
        final result = await biometricService.isEnabled();

        // Assert
        expect(result, isFalse);
      });
    });

    group('enable', () {
      test('should enable biometric when available and authenticated', () async {
        // Arrange - defaults already set: available=true, authenticate=true
        when(() => mockSecureStorage.setBiometricEnabled(true))
            .thenAnswer((_) async {});

        // Act
        final result = await biometricService.enable();

        // Assert
        expect(result, isTrue);
        verify(() => mockSecureStorage.setBiometricEnabled(true)).called(1);
      });

      test('should throw exception when biometric not available', () async {
        // Arrange
        when(() => mockLocalAuth.canCheckBiometrics).thenAnswer((_) async => false);
        when(() => mockLocalAuth.isDeviceSupported()).thenAnswer((_) async => false);

        // Act & Assert
        expect(
          () => biometricService.enable(),
          throwsA(isA<BiometricException>().having(
            (e) => e.message,
            'message',
            contains('غير متاحة'),
          )),
        );
      });

      test('should return false when authentication fails', () async {
        // Arrange
        when(() => mockLocalAuth.authenticate(
              localizedReason: any(named: 'localizedReason'),
              options: any(named: 'options'),
            )).thenAnswer((_) async => false);

        // Act
        final result = await biometricService.enable();

        // Assert
        expect(result, isFalse);
      });
    });

    group('disable', () {
      test('should disable biometric in storage', () async {
        // Arrange
        when(() => mockSecureStorage.setBiometricEnabled(false))
            .thenAnswer((_) async {});

        // Act
        await biometricService.disable();

        // Assert
        verify(() => mockSecureStorage.setBiometricEnabled(false)).called(1);
      });
    });

    group('authenticate', () {
      test('should return true on successful authentication', () async {
        // Arrange - default already returns true

        // Act
        final result = await biometricService.authenticate(
          reason: AuthFixtures.biometricReasonArabic,
        );

        // Assert
        expect(result, isTrue);
      });

      test('should return false when authentication cancelled', () async {
        // Arrange
        when(() => mockLocalAuth.authenticate(
              localizedReason: any(named: 'localizedReason'),
              options: any(named: 'options'),
            )).thenAnswer((_) async => false);

        // Act
        final result = await biometricService.authenticate(
          reason: AuthFixtures.biometricReasonArabic,
        );

        // Assert
        expect(result, isFalse);
      });

      test('should throw BiometricException on NotAvailable error', () async {
        // Arrange
        when(() => mockLocalAuth.authenticate(
              localizedReason: any(named: 'localizedReason'),
              options: any(named: 'options'),
            )).thenThrow(PlatformException(
          code: 'NotAvailable',
          message: 'Biometric authentication error',
        ));

        // Act & Assert
        expect(
          () => biometricService.authenticate(
            reason: AuthFixtures.biometricReasonArabic,
          ),
          throwsA(isA<BiometricException>().having(
            (e) => e.message,
            'message',
            equals('البصمة غير متاحة'),
          )),
        );
      });

      test('should throw BiometricException on NotEnrolled error', () async {
        // Arrange
        when(() => mockLocalAuth.authenticate(
              localizedReason: any(named: 'localizedReason'),
              options: any(named: 'options'),
            )).thenThrow(PlatformException(
          code: 'NotEnrolled',
          message: 'Biometric authentication error',
        ));

        // Act & Assert
        expect(
          () => biometricService.authenticate(
            reason: AuthFixtures.biometricReasonArabic,
          ),
          throwsA(isA<BiometricException>().having(
            (e) => e.message,
            'message',
            contains('لم يتم تسجيل بصمة'),
          )),
        );
      });

      test('should throw BiometricException on LockedOut error', () async {
        // Arrange
        when(() => mockLocalAuth.authenticate(
              localizedReason: any(named: 'localizedReason'),
              options: any(named: 'options'),
            )).thenThrow(PlatformException(
          code: 'LockedOut',
          message: 'Biometric authentication error',
        ));

        // Act & Assert
        expect(
          () => biometricService.authenticate(
            reason: AuthFixtures.biometricReasonArabic,
          ),
          throwsA(isA<BiometricException>().having(
            (e) => e.message,
            'message',
            contains('تم قفل البصمة'),
          )),
        );
      });

      test('should throw BiometricException on PermanentlyLockedOut error', () async {
        // Arrange
        when(() => mockLocalAuth.authenticate(
              localizedReason: any(named: 'localizedReason'),
              options: any(named: 'options'),
            )).thenThrow(PlatformException(
          code: 'PermanentlyLockedOut',
          message: 'Biometric authentication error',
        ));

        // Act & Assert
        expect(
          () => biometricService.authenticate(
            reason: AuthFixtures.biometricReasonArabic,
          ),
          throwsA(isA<BiometricException>().having(
            (e) => e.message,
            'message',
            contains('بشكل دائم'),
          )),
        );
      });

      test('should throw generic BiometricException on unknown error', () async {
        // Arrange
        when(() => mockLocalAuth.authenticate(
              localizedReason: any(named: 'localizedReason'),
              options: any(named: 'options'),
            )).thenThrow(PlatformException(
          code: 'UnknownError',
          message: 'Biometric authentication error',
        ));

        // Act & Assert
        expect(
          () => biometricService.authenticate(
            reason: AuthFixtures.biometricReasonArabic,
          ),
          throwsA(isA<BiometricException>().having(
            (e) => e.message,
            'message',
            contains('حدث خطأ'),
          )),
        );
      });

      test('should use biometricOnly option when specified', () async {
        // Arrange - default already returns true

        // Act
        final result = await biometricService.authenticate(
          reason: AuthFixtures.biometricReasonArabic,
          biometricOnly: true,
        );

        // Assert
        expect(result, isTrue);
      });
    });

    group('authenticateWithFallback', () {
      test('should call authenticate with biometricOnly false', () async {
        // Arrange - default already returns true

        // Act
        final result = await biometricService.authenticateWithFallback(
          reason: AuthFixtures.biometricReasonArabic,
        );

        // Assert
        expect(result, isTrue);
      });
    });

    group('cancelAuthentication', () {
      test('should complete without error', () async {
        // Act & Assert
        await expectLater(
          biometricService.cancelAuthentication(),
          completes,
        );
      });

      test('should handle errors gracefully', () async {
        // Arrange
        when(() => mockLocalAuth.stopAuthentication())
            .thenThrow(PlatformException(code: 'ERROR', message: 'Cannot stop'));

        // Act & Assert - should not throw
        await expectLater(
          biometricService.cancelAuthentication(),
          completes,
        );
      });
    });

    group('getBiometricTypeName', () {
      test('should return Arabic name for fingerprint', () {
        expect(biometricService.getBiometricTypeName(BiometricType.fingerprint), 'بصمة الإصبع');
      });

      test('should return Arabic name for face', () {
        expect(biometricService.getBiometricTypeName(BiometricType.face), 'بصمة الوجه');
      });

      test('should return Arabic name for iris', () {
        expect(biometricService.getBiometricTypeName(BiometricType.iris), 'بصمة العين');
      });

      test('should return Arabic name for strong biometric', () {
        expect(biometricService.getBiometricTypeName(BiometricType.strong), 'مصادقة قوية');
      });

      test('should return Arabic name for weak biometric', () {
        expect(biometricService.getBiometricTypeName(BiometricType.weak), 'مصادقة ضعيفة');
      });
    });

    group('getPrimaryBiometricName', () {
      test('should prioritize face ID over fingerprint', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.face, BiometricType.fingerprint]);

        // Act & Assert
        expect(await biometricService.getPrimaryBiometricName(), 'بصمة الوجه');
      });

      test('should return fingerprint when no face ID', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.fingerprint]);

        // Act & Assert
        expect(await biometricService.getPrimaryBiometricName(), 'بصمة الإصبع');
      });

      test('should return generic name when no biometrics available', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => []);

        // Act & Assert
        expect(await biometricService.getPrimaryBiometricName(), 'البصمة');
      });
    });

    group('getBiometricIconName', () {
      test('should return face icon for face ID', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.face]);

        // Act & Assert
        expect(await biometricService.getBiometricIconName(), 'face');
      });

      test('should return fingerprint icon for fingerprint', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => [BiometricType.fingerprint]);

        // Act & Assert
        expect(await biometricService.getBiometricIconName(), 'fingerprint');
      });

      test('should return security icon when no biometrics', () async {
        // Arrange
        when(() => mockLocalAuth.getAvailableBiometrics())
            .thenAnswer((_) async => []);

        // Act & Assert
        expect(await biometricService.getBiometricIconName(), 'security');
      });
    });
  });

  group('BiometricException', () {
    test('should create exception with message', () {
      final exception = BiometricException('Test error');
      expect(exception.message, 'Test error');
      expect(exception.code, isNull);
    });

    test('should create exception with message and code', () {
      final exception = BiometricException('Test error', code: 'TEST_CODE');
      expect(exception.message, 'Test error');
      expect(exception.code, 'TEST_CODE');
    });

    test('should have string representation', () {
      final exception = BiometricException('Test error message');
      expect(exception.toString(), 'Test error message');
    });
  });
}
