import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/deeplink/deeplink_models.dart';

void main() {
  group('DeepLinkType', () {
    test('should have 8 types', () {
      expect(DeepLinkType.values.length, 8);
    });

    test('should include all expected types', () {
      expect(DeepLinkType.values, contains(DeepLinkType.resetPassword));
      expect(DeepLinkType.values, contains(DeepLinkType.verifyOtp));
      expect(DeepLinkType.values, contains(DeepLinkType.verifyEmail));
      expect(DeepLinkType.values, contains(DeepLinkType.activateAccount));
      expect(DeepLinkType.values, contains(DeepLinkType.fieldDetails));
      expect(DeepLinkType.values, contains(DeepLinkType.notification));
      expect(DeepLinkType.values, contains(DeepLinkType.invite));
      expect(DeepLinkType.values, contains(DeepLinkType.unknown));
    });

    test('should have Arabic display names', () {
      expect(
          DeepLinkType.resetPassword.displayNameAr, 'إعادة تعيين كلمة المرور');
      expect(DeepLinkType.verifyOtp.displayNameAr, 'التحقق من الرمز');
      expect(DeepLinkType.verifyEmail.displayNameAr,
          'التحقق من البريد الإلكتروني');
      expect(DeepLinkType.activateAccount.displayNameAr, 'تفعيل الحساب');
      expect(DeepLinkType.fieldDetails.displayNameAr, 'تفاصيل الحقل');
      expect(DeepLinkType.notification.displayNameAr, 'إشعار');
      expect(DeepLinkType.invite.displayNameAr, 'دعوة');
      expect(DeepLinkType.unknown.displayNameAr, 'رابط غير معروف');
    });

    test('should have English display names', () {
      expect(DeepLinkType.resetPassword.displayNameEn, 'Reset Password');
      expect(DeepLinkType.verifyOtp.displayNameEn, 'Verify OTP');
      expect(DeepLinkType.verifyEmail.displayNameEn, 'Verify Email');
      expect(DeepLinkType.activateAccount.displayNameEn, 'Activate Account');
      expect(DeepLinkType.fieldDetails.displayNameEn, 'Field Details');
      expect(DeepLinkType.notification.displayNameEn, 'Notification');
      expect(DeepLinkType.invite.displayNameEn, 'Invitation');
      expect(DeepLinkType.unknown.displayNameEn, 'Unknown Link');
    });
  });

  group('DeepLinkPaths', () {
    test('should have correct path values', () {
      expect(DeepLinkPaths.resetPassword, '/reset-password');
      expect(DeepLinkPaths.verifyOtp, '/verify-otp');
      expect(DeepLinkPaths.verifyEmail, '/verify-email');
      expect(DeepLinkPaths.activateAccount, '/activate-account');
      expect(DeepLinkPaths.fieldDetails, '/field');
      expect(DeepLinkPaths.notification, '/notification');
      expect(DeepLinkPaths.invite, '/invite');
    });
  });

  group('DeepLinkData', () {
    test('should create with required fields', () {
      final now = DateTime.now();
      final data = DeepLinkData(
        type: DeepLinkType.fieldDetails,
        uri: Uri.parse('sahool://field?id=123'),
        parameters: {'id': '123'},
        receivedAt: now,
      );

      expect(data.type, DeepLinkType.fieldDetails);
      expect(data.parameters['id'], '123');
      expect(data.receivedAt, now);
    });

    test('should get parameter by key', () {
      final data = DeepLinkData(
        type: DeepLinkType.notification,
        uri: Uri.parse('sahool://notification?id=456'),
        parameters: {'id': '456', 'type': 'weather'},
        receivedAt: DateTime.now(),
      );

      expect(data.getParameter('id'), '456');
      expect(data.getParameter('type'), 'weather');
      expect(data.getParameter('missing'), isNull);
    });

    test('should check if parameter exists', () {
      final data = DeepLinkData(
        type: DeepLinkType.invite,
        uri: Uri.parse('sahool://invite?code=ABC'),
        parameters: {'code': 'ABC'},
        receivedAt: DateTime.now(),
      );

      expect(data.hasParameter('code'), true);
      expect(data.hasParameter('missing'), false);
    });

    test('should have meaningful toString', () {
      final data = DeepLinkData(
        type: DeepLinkType.fieldDetails,
        uri: Uri.parse('sahool://field?id=123'),
        parameters: {'id': '123'},
        receivedAt: DateTime.now(),
      );

      final str = data.toString();
      expect(str, contains('DeepLinkData'));
      expect(str, contains('fieldDetails'));
    });

    test('should support equality', () {
      final now = DateTime.now();
      final uri = Uri.parse('sahool://field?id=123');
      final params = {'id': '123'};
      final data1 = DeepLinkData(
        type: DeepLinkType.fieldDetails,
        uri: uri,
        parameters: params,
        receivedAt: now,
      );
      final data2 = DeepLinkData(
        type: DeepLinkType.fieldDetails,
        uri: uri,
        parameters: params,
        receivedAt: now,
      );

      expect(data1, equals(data2));
    });
  });

  group('PasswordResetLinkData', () {
    test('should create with token', () {
      final data = PasswordResetLinkData(
        uri: Uri.parse('sahool://reset-password?token=abc123'),
        token: 'abc123',
        receivedAt: DateTime.now(),
      );

      expect(data.type, DeepLinkType.resetPassword);
      expect(data.token, 'abc123');
      expect(data.email, isNull);
      expect(data.parameters['token'], 'abc123');
    });

    test('should create with token and email', () {
      final data = PasswordResetLinkData(
        uri: Uri.parse(
            'sahool://reset-password?token=abc123&email=test@test.com'),
        token: 'abc123',
        email: 'test@test.com',
        receivedAt: DateTime.now(),
      );

      expect(data.token, 'abc123');
      expect(data.email, 'test@test.com');
      expect(data.parameters['email'], 'test@test.com');
    });

    test('should detect non-expired tokens', () {
      final data = PasswordResetLinkData(
        uri: Uri.parse('sahool://reset-password?token=abc123'),
        token: 'abc123',
        receivedAt: DateTime.now(), // Just now - not expired
      );

      expect(data.isExpired, false);
    });

    test('should detect expired tokens', () {
      final data = PasswordResetLinkData(
        uri: Uri.parse('sahool://reset-password?token=abc123'),
        token: 'abc123',
        receivedAt: DateTime.now().subtract(const Duration(hours: 2)),
      );

      expect(data.isExpired, true);
    });
  });

  group('OtpVerificationLinkData', () {
    test('should create with identifier and purpose', () {
      final data = OtpVerificationLinkData(
        uri: Uri.parse(
            'sahool://verify-otp?identifier=user@test.com&purpose=email_verification'),
        identifier: 'user@test.com',
        purpose: OtpPurpose.emailVerification,
        receivedAt: DateTime.now(),
      );

      expect(data.type, DeepLinkType.verifyOtp);
      expect(data.identifier, 'user@test.com');
      expect(data.purpose, OtpPurpose.emailVerification);
      expect(data.otp, isNull);
      expect(data.sessionId, isNull);
    });

    test('should create with optional fields', () {
      final data = OtpVerificationLinkData(
        uri: Uri.parse('sahool://verify-otp'),
        identifier: '+967123456789',
        purpose: OtpPurpose.phoneVerification,
        otp: '123456',
        sessionId: 'sess-abc-123',
        receivedAt: DateTime.now(),
      );

      expect(data.otp, '123456');
      expect(data.sessionId, 'sess-abc-123');
      expect(data.parameters['otp'], '123456');
      expect(data.parameters['session_id'], 'sess-abc-123');
    });
  });

  group('OtpPurpose', () {
    test('should have 7 purposes', () {
      expect(OtpPurpose.values.length, 7);
    });

    test('should parse from string', () {
      expect(OtpPurposeExtension.fromString('password_reset'),
          OtpPurpose.passwordReset);
      expect(OtpPurposeExtension.fromString('passwordreset'),
          OtpPurpose.passwordReset);
      expect(OtpPurposeExtension.fromString('reset_password'),
          OtpPurpose.passwordReset);
      expect(OtpPurposeExtension.fromString('phone_verification'),
          OtpPurpose.phoneVerification);
      expect(OtpPurposeExtension.fromString('email_verification'),
          OtpPurpose.emailVerification);
      expect(OtpPurposeExtension.fromString('two_factor_auth'),
          OtpPurpose.twoFactorAuth);
      expect(OtpPurposeExtension.fromString('2fa'), OtpPurpose.twoFactorAuth);
      expect(OtpPurposeExtension.fromString('account_activation'),
          OtpPurpose.accountActivation);
      expect(OtpPurposeExtension.fromString('transaction_verification'),
          OtpPurpose.transactionVerification);
    });

    test('should return unknown for unrecognized strings', () {
      expect(OtpPurposeExtension.fromString('garbage'), OtpPurpose.unknown);
      expect(OtpPurposeExtension.fromString(null), OtpPurpose.unknown);
    });

    test('should have Arabic display names', () {
      expect(OtpPurpose.passwordReset.displayNameAr, 'إعادة تعيين كلمة المرور');
      expect(
          OtpPurpose.phoneVerification.displayNameAr, 'التحقق من رقم الهاتف');
      expect(OtpPurpose.emailVerification.displayNameAr,
          'التحقق من البريد الإلكتروني');
      expect(OtpPurpose.twoFactorAuth.displayNameAr, 'المصادقة الثنائية');
      expect(OtpPurpose.accountActivation.displayNameAr, 'تفعيل الحساب');
      expect(OtpPurpose.transactionVerification.displayNameAr,
          'التحقق من المعاملة');
      expect(OtpPurpose.unknown.displayNameAr, 'غير معروف');
    });
  });

  group('DeepLinkState', () {
    test('should create with defaults', () {
      const state = DeepLinkState();
      expect(state.currentLink, isNull);
      expect(state.isInitialized, false);
      expect(state.hasPendingLink, false);
      expect(state.error, isNull);
      expect(state.linkHistory, isEmpty);
    });

    test('should copy with new values', () {
      const state = DeepLinkState();
      final newState = state.copyWith(
        isInitialized: true,
        hasPendingLink: true,
      );

      expect(newState.isInitialized, true);
      expect(newState.hasPendingLink, true);
    });

    test('should clear current link', () {
      final data = DeepLinkData(
        type: DeepLinkType.fieldDetails,
        uri: Uri.parse('sahool://field?id=1'),
        parameters: {'id': '1'},
        receivedAt: DateTime.now(),
      );
      final state = DeepLinkState(currentLink: data, hasPendingLink: true);
      final cleared = state.copyWith(clearCurrentLink: true);

      expect(cleared.currentLink, isNull);
    });

    test('should clear error', () {
      const state = DeepLinkState(error: 'Something went wrong');
      final cleared = state.copyWith(clearError: true);

      expect(cleared.error, isNull);
    });
  });

  group('Constants', () {
    test('should have correct scheme', () {
      expect(kSahoolScheme, 'sahool');
    });

    test('should have universal link hosts', () {
      expect(kUniversalLinkHosts, contains('sahool.app'));
      expect(kUniversalLinkHosts, contains('www.sahool.app'));
      expect(kUniversalLinkHosts, contains('app.sahool.app'));
    });
  });

  group('Helper Functions', () {
    group('buildPasswordResetLink', () {
      test('should build universal link with token', () {
        final link = buildPasswordResetLink(token: 'test-token-123');
        expect(link, contains('sahool.app'));
        expect(link, contains('/reset-password'));
        expect(link, contains('token=test-token-123'));
      });

      test('should build universal link with email', () {
        final link = buildPasswordResetLink(
          token: 'test-token',
          email: 'user@example.com',
        );
        expect(link, contains('email=user%40example.com'));
      });

      test('should build custom scheme link', () {
        final link = buildPasswordResetLink(
          token: 'test-token',
          useUniversalLink: false,
        );
        expect(link, contains('sahool:'));
        expect(link, contains('token=test-token'));
      });
    });

    group('buildOtpVerificationLink', () {
      test('should build universal link', () {
        final link = buildOtpVerificationLink(
          identifier: 'user@example.com',
          purpose: OtpPurpose.emailVerification,
        );
        expect(link, contains('sahool.app'));
        expect(link, contains('/verify-otp'));
        expect(link, contains('identifier=user%40example.com'));
        expect(link, contains('purpose=emailVerification'));
      });

      test('should build with optional params', () {
        final link = buildOtpVerificationLink(
          identifier: '+967123456789',
          purpose: OtpPurpose.phoneVerification,
          otp: '123456',
          sessionId: 'sess-id',
        );
        expect(link, contains('otp=123456'));
        expect(link, contains('session_id=sess-id'));
      });

      test('should build custom scheme link', () {
        final link = buildOtpVerificationLink(
          identifier: 'user@test.com',
          purpose: OtpPurpose.twoFactorAuth,
          useUniversalLink: false,
        );
        expect(link, contains('sahool:'));
      });
    });

    group('isValidTokenFormat', () {
      test('should accept valid tokens', () {
        expect(isValidTokenFormat('abcdefghijklmnopqrstuvwxyz123456'), true);
        expect(
            isValidTokenFormat('aBcDeFgHiJkLmNoPqRsTuVwXyZ-123456789'), true);
        expect(isValidTokenFormat('token_with_underscores_and-hyphens-1234'),
            true);
      });

      test('should reject short tokens', () {
        expect(isValidTokenFormat('short'), false);
        expect(isValidTokenFormat(''), false);
        expect(isValidTokenFormat('less-than-32-chars'), false);
      });

      test('should reject tokens with invalid characters', () {
        expect(
            isValidTokenFormat('token with spaces xxxxxxxxxxxxxxxxx'), false);
        expect(isValidTokenFormat('token!@#\$%^&*()xxxxxxxxxxxxxxxxx'), false);
      });
    });

    group('extractFieldIdFromPath', () {
      test('should extract field ID from /field/123', () {
        expect(extractFieldIdFromPath('/field/123'), '123');
      });

      test('should extract field ID from /fields/abc-def', () {
        expect(extractFieldIdFromPath('/fields/abc-def'), 'abc-def');
      });

      test('should extract field ID with underscores', () {
        expect(extractFieldIdFromPath('/field/field_001'), 'field_001');
      });

      test('should return null for invalid paths', () {
        expect(extractFieldIdFromPath('/user/123'), isNull);
        expect(extractFieldIdFromPath('/'), isNull);
      });
    });
  });
}
