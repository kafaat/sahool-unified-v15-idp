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
import 'package:sahool_field_app/core/auth/biometric_service.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';

import 'auth_fixtures.dart';
import 'auth_mocks.dart';

/// Platform channel mock for LocalAuthentication
class MockLocalAuthenticationChannel {
  static const MethodChannel channel = MethodChannel('plugins.flutter.io/local_auth');

  bool canCheckBiometrics = true;
  bool isDeviceSupported = true;
  List<String> availableBiometrics = ['fingerprint'];
  bool authenticateSuccess = true;
  String? authenticationError;

  void setupMockChannel() {
    TestWidgetsFlutterBinding.ensureInitialized();

    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, (MethodCall methodCall) async {
      switch (methodCall.method) {
        case 'canCheckBiometrics':
          return canCheckBiometrics;
        case 'isDeviceSupported':
          return isDeviceSupported;
        case 'getAvailableBiometrics':
          return availableBiometrics;
        case 'authenticate':
          if (authenticationError != null) {
            throw PlatformException(
              code: authenticationError!,
              message: 'Biometric authentication error',
            );
          }
          return authenticateSuccess;
        case 'stopAuthentication':
          return true;
        default:
          return null;
      }
    });
  }

  void reset() {
    canCheckBiometrics = true;
    isDeviceSupported = true;
    availableBiometrics = ['fingerprint'];
    authenticateSuccess = true;
    authenticationError = null;
  }

  void tearDown() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(channel, null);
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late BiometricService biometricService;
  late MockSecureStorageService mockSecureStorage;
  late MockLocalAuthenticationChannel mockChannel;

  setUpAll(() {
    registerAuthFallbackValues();
  });

  setUp(() {
    mockSecureStorage = MockSecureStorageService();
    mockSecureStorage.setupDefaults();

    mockChannel = MockLocalAuthenticationChannel();
    mockChannel.setupMockChannel();

    biometricService = BiometricService(
      secureStorage: mockSecureStorage,
    );
  });

  tearDown(() {
    mockChannel.tearDown();
    mockSecureStorage.clearStorage();
  });

  group('BiometricService', () {
    group('isAvailable', () {
      test('should return true when biometrics are available', () async {
        // Arrange
        mockChannel.canCheckBiometrics = true;
        mockChannel.isDeviceSupported = true;
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return true when device supported but cannot check biometrics', () async {
        // Arrange
        mockChannel.canCheckBiometrics = false;
        mockChannel.isDeviceSupported = true;
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return true when can check biometrics but device not supported', () async {
        // Arrange
        mockChannel.canCheckBiometrics = true;
        mockChannel.isDeviceSupported = false;
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return false when neither is available', () async {
        // Arrange
        mockChannel.canCheckBiometrics = false;
        mockChannel.isDeviceSupported = false;
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isFalse);
      });

      test('should return false on platform exception', () async {
        // Arrange - setup to throw exception
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(
          MockLocalAuthenticationChannel.channel,
          (MethodCall methodCall) async {
            if (methodCall.method == 'canCheckBiometrics' ||
                methodCall.method == 'isDeviceSupported') {
              throw PlatformException(
                code: 'ERROR',
                message: 'Platform error',
              );
            }
            return null;
          },
        );

        // Act
        final result = await biometricService.isAvailable();

        // Assert
        expect(result, isFalse);
      });
    });

    group('getAvailableBiometrics', () {
      test('should return list of available biometric types', () async {
        // Arrange
        mockChannel.availableBiometrics = ['fingerprint', 'face'];
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.getAvailableBiometrics();

        // Assert
        expect(result, isA<List<BiometricType>>());
        expect(result.length, 2);
      });

      test('should return empty list on error', () async {
        // Arrange
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(
          MockLocalAuthenticationChannel.channel,
          (MethodCall methodCall) async {
            if (methodCall.method == 'getAvailableBiometrics') {
              throw PlatformException(
                code: 'ERROR',
                message: 'Cannot get biometrics',
              );
            }
            return null;
          },
        );

        // Act
        final result = await biometricService.getAvailableBiometrics();

        // Assert
        expect(result, isEmpty);
      });

      test('should return empty list when no biometrics enrolled', () async {
        // Arrange
        mockChannel.availableBiometrics = [];
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.getAvailableBiometrics();

        // Assert
        expect(result, isEmpty);
      });
    });

    group('isFingerprintAvailable', () {
      test('should return true when fingerprint is available', () async {
        // Arrange
        mockChannel.availableBiometrics = ['fingerprint'];
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.isFingerprintAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return false when only face ID is available', () async {
        // Arrange
        mockChannel.availableBiometrics = ['face'];
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.isFingerprintAvailable();

        // Assert
        expect(result, isFalse);
      });

      test('should return false when no biometrics available', () async {
        // Arrange
        mockChannel.availableBiometrics = [];
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.isFingerprintAvailable();

        // Assert
        expect(result, isFalse);
      });
    });

    group('isFaceIdAvailable', () {
      test('should return true when face ID is available', () async {
        // Arrange
        mockChannel.availableBiometrics = ['face'];
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.isFaceIdAvailable();

        // Assert
        expect(result, isTrue);
      });

      test('should return false when only fingerprint is available', () async {
        // Arrange
        mockChannel.availableBiometrics = ['fingerprint'];
        mockChannel.setupMockChannel();

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
        // Arrange
        mockChannel.canCheckBiometrics = true;
        mockChannel.isDeviceSupported = true;
        mockChannel.authenticateSuccess = true;
        mockChannel.setupMockChannel();

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
        mockChannel.canCheckBiometrics = false;
        mockChannel.isDeviceSupported = false;
        mockChannel.setupMockChannel();

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
        mockChannel.canCheckBiometrics = true;
        mockChannel.isDeviceSupported = true;
        mockChannel.authenticateSuccess = false;
        mockChannel.setupMockChannel();

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
        // Arrange
        mockChannel.authenticateSuccess = true;
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.authenticate(
          reason: AuthFixtures.biometricReasonArabic,
        );

        // Assert
        expect(result, isTrue);
      });

      test('should return false when authentication cancelled', () async {
        // Arrange
        mockChannel.authenticateSuccess = false;
        mockChannel.setupMockChannel();

        // Act
        final result = await biometricService.authenticate(
          reason: AuthFixtures.biometricReasonArabic,
        );

        // Assert
        expect(result, isFalse);
      });

      test('should throw BiometricException on NotAvailable error', () async {
        // Arrange
        mockChannel.authenticationError = 'NotAvailable';
        mockChannel.setupMockChannel();

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
        mockChannel.authenticationError = 'NotEnrolled';
        mockChannel.setupMockChannel();

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
        mockChannel.authenticationError = 'LockedOut';
        mockChannel.setupMockChannel();

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
        mockChannel.authenticationError = 'PermanentlyLockedOut';
        mockChannel.setupMockChannel();

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
        mockChannel.authenticationError = 'UnknownError';
        mockChannel.setupMockChannel();

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
        // Arrange
        mockChannel.authenticateSuccess = true;
        mockChannel.setupMockChannel();

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
        // Arrange
        mockChannel.authenticateSuccess = true;
        mockChannel.setupMockChannel();

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
        // Arrange
        mockChannel.setupMockChannel();

        // Act & Assert
        await expectLater(
          biometricService.cancelAuthentication(),
          completes,
        );
      });

      test('should handle errors gracefully', () async {
        // Arrange
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(
          MockLocalAuthenticationChannel.channel,
          (MethodCall methodCall) async {
            if (methodCall.method == 'stopAuthentication') {
              throw PlatformException(
                code: 'ERROR',
                message: 'Cannot stop',
              );
            }
            return null;
          },
        );

        // Act & Assert - should not throw
        await expectLater(
          biometricService.cancelAuthentication(),
          completes,
        );
      });
    });

    group('getBiometricTypeName', () {
      test('should return Arabic name for fingerprint', () {
        // Act
        final name = biometricService.getBiometricTypeName(BiometricType.fingerprint);

        // Assert
        expect(name, 'بصمة الإصبع');
      });

      test('should return Arabic name for face', () {
        // Act
        final name = biometricService.getBiometricTypeName(BiometricType.face);

        // Assert
        expect(name, 'بصمة الوجه');
      });

      test('should return Arabic name for iris', () {
        // Act
        final name = biometricService.getBiometricTypeName(BiometricType.iris);

        // Assert
        expect(name, 'بصمة العين');
      });

      test('should return Arabic name for strong biometric', () {
        // Act
        final name = biometricService.getBiometricTypeName(BiometricType.strong);

        // Assert
        expect(name, 'مصادقة قوية');
      });

      test('should return Arabic name for weak biometric', () {
        // Act
        final name = biometricService.getBiometricTypeName(BiometricType.weak);

        // Assert
        expect(name, 'مصادقة ضعيفة');
      });
    });

    group('getPrimaryBiometricName', () {
      test('should prioritize face ID over fingerprint', () async {
        // Arrange
        mockChannel.availableBiometrics = ['face', 'fingerprint'];
        mockChannel.setupMockChannel();

        // Act
        final name = await biometricService.getPrimaryBiometricName();

        // Assert
        expect(name, 'بصمة الوجه');
      });

      test('should return fingerprint when no face ID', () async {
        // Arrange
        mockChannel.availableBiometrics = ['fingerprint'];
        mockChannel.setupMockChannel();

        // Act
        final name = await biometricService.getPrimaryBiometricName();

        // Assert
        expect(name, 'بصمة الإصبع');
      });

      test('should return generic name when no biometrics available', () async {
        // Arrange
        mockChannel.availableBiometrics = [];
        mockChannel.setupMockChannel();

        // Act
        final name = await biometricService.getPrimaryBiometricName();

        // Assert
        expect(name, 'البصمة');
      });
    });

    group('getBiometricIconName', () {
      test('should return face icon for face ID', () async {
        // Arrange
        mockChannel.availableBiometrics = ['face'];
        mockChannel.setupMockChannel();

        // Act
        final iconName = await biometricService.getBiometricIconName();

        // Assert
        expect(iconName, 'face');
      });

      test('should return fingerprint icon for fingerprint', () async {
        // Arrange
        mockChannel.availableBiometrics = ['fingerprint'];
        mockChannel.setupMockChannel();

        // Act
        final iconName = await biometricService.getBiometricIconName();

        // Assert
        expect(iconName, 'fingerprint');
      });

      test('should return security icon when no biometrics', () async {
        // Arrange
        mockChannel.availableBiometrics = [];
        mockChannel.setupMockChannel();

        // Act
        final iconName = await biometricService.getBiometricIconName();

        // Assert
        expect(iconName, 'security');
      });
    });
  });

  group('BiometricException', () {
    test('should create exception with message', () {
      // Act
      final exception = BiometricException('Test error');

      // Assert
      expect(exception.message, 'Test error');
      expect(exception.code, isNull);
    });

    test('should create exception with message and code', () {
      // Act
      final exception = BiometricException('Test error', code: 'TEST_CODE');

      // Assert
      expect(exception.message, 'Test error');
      expect(exception.code, 'TEST_CODE');
    });

    test('should have string representation', () {
      // Act
      final exception = BiometricException('Test error message');

      // Assert
      expect(exception.toString(), 'Test error message');
    });
  });
}
