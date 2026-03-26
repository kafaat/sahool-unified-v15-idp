import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/auth/data/auth_service.dart';
import 'package:sahool_field_app/features/auth/services/otp_service.dart';
import 'package:sahool_field_app/features/auth/config/otp_config.dart';

void main() {
  // ===========================================================================
  // RegisterRequest Tests
  // ===========================================================================
  group('RegisterRequest', () {
    test('should create with required fields', () {
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'Pass1234!',
        firstName: 'Ahmed',
        lastName: 'Ali',
      );

      expect(request.email, 'test@sahool.app');
      expect(request.password, 'Pass1234!');
      expect(request.firstName, 'Ahmed');
      expect(request.lastName, 'Ali');
      expect(request.phone, isNull);
    });

    test('should create with optional phone', () {
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'Pass1234!',
        firstName: 'Ahmed',
        lastName: 'Ali',
        phone: '+967771234567',
      );

      expect(request.phone, '+967771234567');
    });

    test('toJson includes all required fields', () {
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'Pass1234!',
        firstName: 'Ahmed',
        lastName: 'Ali',
      );

      final json = request.toJson();
      expect(json['email'], 'test@sahool.app');
      expect(json['password'], 'Pass1234!');
      expect(json['firstName'], 'Ahmed');
      expect(json['lastName'], 'Ali');
      expect(json.containsKey('phone'), isFalse);
    });

    test('toJson includes phone when not null and not empty', () {
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'Pass1234!',
        firstName: 'Ahmed',
        lastName: 'Ali',
        phone: '+967771234567',
      );

      final json = request.toJson();
      expect(json['phone'], '+967771234567');
    });

    test('toJson excludes phone when empty string', () {
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'Pass1234!',
        firstName: 'Ahmed',
        lastName: 'Ali',
        phone: '',
      );

      final json = request.toJson();
      expect(json.containsKey('phone'), isFalse);
    });

    test('toJson excludes phone when null', () {
      final request = RegisterRequest(
        email: 'test@sahool.app',
        password: 'Pass1234!',
        firstName: 'Ahmed',
        lastName: 'Ali',
        phone: null,
      );

      final json = request.toJson();
      expect(json.containsKey('phone'), isFalse);
    });
  });

  // ===========================================================================
  // UserInfo Tests
  // ===========================================================================
  group('UserInfo', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 'user-001',
        'email': 'farmer@sahool.app',
        'first_name': 'Ahmed',
        'last_name': 'Ali',
        'phone': '+967771234567',
        'tenant_id': 'tenant-001',
      };

      final user = UserInfo.fromJson(json);
      expect(user.id, 'user-001');
      expect(user.email, 'farmer@sahool.app');
      expect(user.firstName, 'Ahmed');
      expect(user.lastName, 'Ali');
      expect(user.phone, '+967771234567');
      expect(user.tenantId, 'tenant-001');
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'id': 'user-001',
        'email': 'farmer@sahool.app',
      };

      final user = UserInfo.fromJson(json);
      expect(user.firstName, '');
      expect(user.lastName, '');
      expect(user.phone, isNull);
      expect(user.tenantId, isNull);
    });

    test('toJson produces correct keys', () {
      final user = UserInfo(
        id: 'user-001',
        email: 'farmer@sahool.app',
        firstName: 'Ahmed',
        lastName: 'Ali',
        phone: '+967771234567',
        tenantId: 'tenant-001',
      );

      final json = user.toJson();
      expect(json['id'], 'user-001');
      expect(json['email'], 'farmer@sahool.app');
      expect(json['first_name'], 'Ahmed');
      expect(json['last_name'], 'Ali');
      expect(json['phone'], '+967771234567');
      expect(json['tenant_id'], 'tenant-001');
    });

    test('fullName combines first and last name', () {
      final user = UserInfo(
        id: 'u1',
        email: 'a@b.com',
        firstName: 'Ahmed',
        lastName: 'Ali',
      );
      expect(user.fullName, 'Ahmed Ali');
    });

    test('fullName trims when lastName is empty', () {
      final user = UserInfo(
        id: 'u1',
        email: 'a@b.com',
        firstName: 'Ahmed',
        lastName: '',
      );
      expect(user.fullName, 'Ahmed');
    });

    test('fullName trims when firstName is empty', () {
      final user = UserInfo(
        id: 'u1',
        email: 'a@b.com',
        firstName: '',
        lastName: 'Ali',
      );
      expect(user.fullName, 'Ali');
    });

    test('fullName is empty string when both names empty', () {
      final user = UserInfo(
        id: 'u1',
        email: 'a@b.com',
        firstName: '',
        lastName: '',
      );
      expect(user.fullName, '');
    });

    test('roundtrip fromJson/toJson preserves data', () {
      final original = UserInfo(
        id: 'user-abc',
        email: 'test@sahool.app',
        firstName: 'Salem',
        lastName: 'Mohammed',
        phone: '+967770000000',
        tenantId: 'tenant-xyz',
      );

      final json = original.toJson();
      final restored = UserInfo.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.email, original.email);
      expect(restored.firstName, original.firstName);
      expect(restored.lastName, original.lastName);
      expect(restored.phone, original.phone);
      expect(restored.tenantId, original.tenantId);
    });
  });

  // ===========================================================================
  // AuthResponse Tests
  // ===========================================================================
  group('AuthResponse', () {
    test('fromJson parses complete response', () {
      final json = {
        'access_token': 'jwt-token-123',
        'refresh_token': 'refresh-456',
        'expires_at': '2026-04-01T12:00:00.000Z',
        'user': {
          'id': 'user-001',
          'email': 'test@sahool.app',
          'first_name': 'Ahmed',
          'last_name': 'Ali',
        },
      };

      final response = AuthResponse.fromJson(json);
      expect(response.accessToken, 'jwt-token-123');
      expect(response.refreshToken, 'refresh-456');
      expect(response.expiresAt, isNotNull);
      expect(response.expiresAt!.year, 2026);
      expect(response.user.email, 'test@sahool.app');
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'access_token': 'jwt-token-123',
        'user': {
          'id': 'user-001',
          'email': 'test@sahool.app',
        },
      };

      final response = AuthResponse.fromJson(json);
      expect(response.refreshToken, isNull);
      expect(response.expiresAt, isNull);
    });
  });

  // ===========================================================================
  // AuthResult Tests
  // ===========================================================================
  group('AuthResult', () {
    test('success factory creates successful result', () {
      final authResponse = AuthResponse(
        accessToken: 'token',
        user: UserInfo(id: 'u1', email: 'a@b.com', firstName: 'A', lastName: 'B'),
      );

      final result = AuthResult.success(authResponse);
      expect(result.success, isTrue);
      expect(result.response, isNotNull);
      expect(result.errorMessage, isNull);
      expect(result.errorMessageAr, isNull);
    });

    test('failure factory creates failed result', () {
      final result = AuthResult.failure(
        message: 'Invalid credentials',
        messageAr: 'بيانات الدخول غير صحيحة',
      );

      expect(result.success, isFalse);
      expect(result.response, isNull);
      expect(result.errorMessage, 'Invalid credentials');
      expect(result.errorMessageAr, 'بيانات الدخول غير صحيحة');
    });

    test('success result has response object', () {
      final user = UserInfo(id: 'u1', email: 'a@b.com', firstName: 'A', lastName: 'B');
      final authResponse = AuthResponse(accessToken: 'tok', user: user);
      final result = AuthResult.success(authResponse);

      expect(result.response!.accessToken, 'tok');
      expect(result.response!.user.id, 'u1');
    });
  });

  // ===========================================================================
  // OTPChannel Enum Tests
  // ===========================================================================
  group('OTPChannel', () {
    test('all values have correct apiValue', () {
      expect(OTPChannel.sms.apiValue, 'sms');
      expect(OTPChannel.whatsapp.apiValue, 'whatsapp');
      expect(OTPChannel.telegram.apiValue, 'telegram');
      expect(OTPChannel.email.apiValue, 'email');
    });

    test('all values have correct displayName', () {
      expect(OTPChannel.sms.displayName, 'SMS');
      expect(OTPChannel.whatsapp.displayName, 'WhatsApp');
      expect(OTPChannel.telegram.displayName, 'Telegram');
      expect(OTPChannel.email.displayName, 'Email');
    });

    test('all values have correct displayNameArabic', () {
      expect(OTPChannel.sms.displayNameArabic, 'رسالة نصية SMS');
      expect(OTPChannel.whatsapp.displayNameArabic, 'واتساب');
      expect(OTPChannel.telegram.displayNameArabic, 'تيليجرام');
      expect(OTPChannel.email.displayNameArabic, 'البريد الإلكتروني');
    });

    test('values list has 4 entries', () {
      expect(OTPChannel.values.length, 4);
    });
  });

  // ===========================================================================
  // OTPPurpose Enum Tests
  // ===========================================================================
  group('OTPPurpose', () {
    test('all values have correct apiValue', () {
      expect(OTPPurpose.passwordReset.apiValue, 'password_reset');
      expect(OTPPurpose.phoneVerification.apiValue, 'phone_verification');
      expect(OTPPurpose.twoFactor.apiValue, 'two_factor');
      expect(OTPPurpose.accountRecovery.apiValue, 'account_recovery');
    });

    test('values list has 4 entries', () {
      expect(OTPPurpose.values.length, 4);
    });
  });

  // ===========================================================================
  // OTPState Tests
  // ===========================================================================
  group('OTPState', () {
    test('default construction has correct defaults', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );

      expect(state.sendAttempts, 0);
      expect(state.verifyAttempts, 0);
      expect(state.isVerified, isFalse);
      expect(state.isLoading, isFalse);
      expect(state.cooldownSeconds, 0);
      expect(state.error, isNull);
      expect(state.resetToken, isNull);
      expect(state.sentAt, isNull);
      expect(state.expiresAt, isNull);
    });

    test('isExpired returns true when expiresAt is null', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );
      expect(state.isExpired, isTrue);
    });

    test('isExpired returns true when expiresAt is in the past', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        expiresAt: DateTime.now().subtract(const Duration(minutes: 1)),
      );
      expect(state.isExpired, isTrue);
    });

    test('isExpired returns false when expiresAt is in the future', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        expiresAt: DateTime.now().add(const Duration(minutes: 5)),
      );
      expect(state.isExpired, isFalse);
    });

    test('canResend returns true when cooldown is 0 and not loading', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        cooldownSeconds: 0,
        isLoading: false,
      );
      expect(state.canResend, isTrue);
    });

    test('canResend returns false when cooldown is positive', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        cooldownSeconds: 30,
      );
      expect(state.canResend, isFalse);
    });

    test('canResend returns false when loading', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        isLoading: true,
      );
      expect(state.canResend, isFalse);
    });

    test('remainingSeconds returns 0 when expiresAt is null', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );
      expect(state.remainingSeconds, 0);
    });

    test('remainingSeconds returns 0 when expired', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        expiresAt: DateTime.now().subtract(const Duration(seconds: 10)),
      );
      expect(state.remainingSeconds, 0);
    });

    test('remainingSeconds returns positive when not expired', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        expiresAt: DateTime.now().add(const Duration(seconds: 120)),
      );
      expect(state.remainingSeconds, greaterThan(0));
      expect(state.remainingSeconds, lessThanOrEqualTo(120));
    });

    test('isLocked returns true at max verify attempts', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        verifyAttempts: OTPService.maxVerifyAttempts,
      );
      expect(state.isLocked, isTrue);
    });

    test('isLocked returns false below max verify attempts', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        verifyAttempts: 1,
      );
      expect(state.isLocked, isFalse);
    });

    test('isSendLocked returns true at max send attempts', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        sendAttempts: OTPService.maxSendAttempts,
      );
      expect(state.isSendLocked, isTrue);
    });

    test('isSendLocked returns false below max send attempts', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        sendAttempts: 2,
      );
      expect(state.isSendLocked, isFalse);
    });

    test('copyWith preserves unchanged fields', () {
      final original = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        sendAttempts: 3,
        verifyAttempts: 1,
      );

      final copied = original.copyWith(sendAttempts: 4);
      expect(copied.identifier, 'test@sahool.app');
      expect(copied.channel, OTPChannel.sms);
      expect(copied.sendAttempts, 4);
      expect(copied.verifyAttempts, 1);
    });

    test('copyWith clearError removes error', () {
      final state = OTPState(
        identifier: 'x',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.twoFactor,
        error: 'Some error',
      );

      final cleared = state.copyWith(clearError: true);
      expect(cleared.error, isNull);
    });

    test('copyWith clearResetToken removes resetToken', () {
      final state = OTPState(
        identifier: 'x',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        resetToken: 'token-123',
      );

      final cleared = state.copyWith(clearResetToken: true);
      expect(cleared.resetToken, isNull);
    });
  });

  // ===========================================================================
  // SendOTPResponse Tests
  // ===========================================================================
  group('SendOTPResponse', () {
    test('fromJson parses success response', () {
      final json = {
        'success': true,
        'message': 'OTP sent',
        'expires_in': 300,
        'cooldown': 60,
        'masked_destination': '****1234',
      };

      final response = SendOTPResponse.fromJson(json);
      expect(response.success, isTrue);
      expect(response.message, 'OTP sent');
      expect(response.expiresInSeconds, 300);
      expect(response.cooldownSeconds, 60);
      expect(response.maskedDestination, '****1234');
    });

    test('fromJson handles alternative key names', () {
      final json = {
        'status': 'success',
        'expiresIn': 600,
        'resend_cooldown': 90,
        'maskedDestination': '***5678',
      };

      final response = SendOTPResponse.fromJson(json);
      expect(response.success, isTrue);
      expect(response.expiresInSeconds, 600);
      expect(response.cooldownSeconds, 90);
      expect(response.maskedDestination, '***5678');
    });

    test('fromJson uses defaults for missing fields', () {
      final json = <String, dynamic>{
        'success': true,
      };

      final response = SendOTPResponse.fromJson(json);
      expect(response.expiresInSeconds, 300);
      expect(response.cooldownSeconds, 60);
      expect(response.maskedDestination, isNull);
    });
  });

  // ===========================================================================
  // VerifyOTPResponse Tests
  // ===========================================================================
  group('VerifyOTPResponse', () {
    test('fromJson parses success response', () {
      final json = {
        'success': true,
        'message': 'Verified',
        'reset_token': 'reset-tok-123',
        'remaining_attempts': 3,
      };

      final response = VerifyOTPResponse.fromJson(json);
      expect(response.success, isTrue);
      expect(response.message, 'Verified');
      expect(response.resetToken, 'reset-tok-123');
      expect(response.remainingAttempts, 3);
    });

    test('fromJson handles alternative key names', () {
      final json = {
        'valid': true,
        'resetToken': 'alt-token',
        'remainingAttempts': 2,
      };

      final response = VerifyOTPResponse.fromJson(json);
      expect(response.resetToken, 'alt-token');
      expect(response.remainingAttempts, 2);
    });

    test('fromJson handles token key variant', () {
      final json = {
        'success': true,
        'token': 'token-variant',
      };

      final response = VerifyOTPResponse.fromJson(json);
      expect(response.resetToken, 'token-variant');
    });
  });

  // ===========================================================================
  // OTPException Tests
  // ===========================================================================
  group('OTPException', () {
    test('basic construction', () {
      final exception = OTPException('Test error');
      expect(exception.message, 'Test error');
      expect(exception.code, isNull);
      expect(exception.isRateLimited, isFalse);
      expect(exception.retryAfterSeconds, isNull);
    });

    test('construction with all parameters', () {
      final exception = OTPException(
        'Rate limited',
        code: 'E6001',
        isRateLimited: true,
        retryAfterSeconds: 60,
      );
      expect(exception.message, 'Rate limited');
      expect(exception.code, 'E6001');
      expect(exception.isRateLimited, isTrue);
      expect(exception.retryAfterSeconds, 60);
    });

    test('toString returns message', () {
      final exception = OTPException('My error message');
      expect(exception.toString(), 'My error message');
    });

    test('implements Exception', () {
      final exception = OTPException('test');
      expect(exception, isA<Exception>());
    });
  });

  // ===========================================================================
  // OTPStateParams Tests
  // ===========================================================================
  group('OTPStateParams', () {
    test('equality works for same values', () {
      const a = OTPStateParams(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );
      const b = OTPStateParams(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );

      expect(a, equals(b));
      expect(a.hashCode, equals(b.hashCode));
    });

    test('inequality for different identifier', () {
      const a = OTPStateParams(
        identifier: 'a@b.com',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );
      const b = OTPStateParams(
        identifier: 'c@d.com',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );

      expect(a, isNot(equals(b)));
    });

    test('inequality for different channel', () {
      const a = OTPStateParams(
        identifier: 'a@b.com',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );
      const b = OTPStateParams(
        identifier: 'a@b.com',
        channel: OTPChannel.email,
        purpose: OTPPurpose.passwordReset,
      );

      expect(a, isNot(equals(b)));
    });

    test('inequality for different purpose', () {
      const a = OTPStateParams(
        identifier: 'a@b.com',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );
      const b = OTPStateParams(
        identifier: 'a@b.com',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.twoFactor,
      );

      expect(a, isNot(equals(b)));
    });
  });

  // ===========================================================================
  // OTPChannelConfig Tests
  // ===========================================================================
  group('OTPChannelConfig', () {
    test('fromJson parses all fields', () {
      final json = {
        'enabled': true,
        'display_name': 'SMS',
        'display_name_ar': 'رسالة نصية',
        'priority': 1,
        'provider_settings': {'provider': 'twilio'},
        'max_retries': 5,
        'delivery_timeout_seconds': 45,
        'show_as_primary': true,
      };

      final config = OTPChannelConfig.fromJson(json);
      expect(config.enabled, isTrue);
      expect(config.displayName, 'SMS');
      expect(config.displayNameAr, 'رسالة نصية');
      expect(config.priority, 1);
      expect(config.providerSettings['provider'], 'twilio');
      expect(config.maxRetries, 5);
      expect(config.deliveryTimeoutSeconds, 45);
      expect(config.showAsPrimary, isTrue);
    });

    test('fromJson uses defaults for missing fields', () {
      final config = OTPChannelConfig.fromJson({});
      expect(config.enabled, isFalse);
      expect(config.displayName, '');
      expect(config.displayNameAr, '');
      expect(config.priority, 0);
      expect(config.providerSettings, isEmpty);
      expect(config.maxRetries, 3);
      expect(config.deliveryTimeoutSeconds, 30);
      expect(config.showAsPrimary, isFalse);
    });

    test('toJson produces correct output', () {
      const config = OTPChannelConfig(
        enabled: true,
        displayName: 'Email',
        displayNameAr: 'البريد',
        priority: 4,
        maxRetries: 2,
        deliveryTimeoutSeconds: 60,
        showAsPrimary: false,
      );

      final json = config.toJson();
      expect(json['enabled'], isTrue);
      expect(json['display_name'], 'Email');
      expect(json['display_name_ar'], 'البريد');
      expect(json['priority'], 4);
      expect(json['max_retries'], 2);
      expect(json['delivery_timeout_seconds'], 60);
      expect(json['show_as_primary'], isFalse);
    });

    test('copyWith modifies specified fields', () {
      const original = OTPChannelConfig(
        enabled: true,
        displayName: 'SMS',
        displayNameAr: 'رسالة',
      );

      final modified = original.copyWith(enabled: false, maxRetries: 10);
      expect(modified.enabled, isFalse);
      expect(modified.displayName, 'SMS');
      expect(modified.maxRetries, 10);
    });

    test('toString includes key info', () {
      const config = OTPChannelConfig(
        enabled: true,
        displayName: 'SMS',
        displayNameAr: 'رسالة',
        priority: 1,
      );

      expect(config.toString(), contains('SMS'));
      expect(config.toString(), contains('enabled: true'));
    });

    test('roundtrip fromJson/toJson preserves data', () {
      const original = OTPChannelConfig(
        enabled: true,
        displayName: 'WhatsApp',
        displayNameAr: 'واتساب',
        priority: 2,
        maxRetries: 4,
        deliveryTimeoutSeconds: 50,
        showAsPrimary: true,
      );

      final restored = OTPChannelConfig.fromJson(original.toJson());
      expect(restored.enabled, original.enabled);
      expect(restored.displayName, original.displayName);
      expect(restored.displayNameAr, original.displayNameAr);
      expect(restored.priority, original.priority);
      expect(restored.maxRetries, original.maxRetries);
      expect(restored.deliveryTimeoutSeconds, original.deliveryTimeoutSeconds);
      expect(restored.showAsPrimary, original.showAsPrimary);
    });
  });

  // ===========================================================================
  // OTPRateLimitConfig Tests
  // ===========================================================================
  group('OTPRateLimitConfig', () {
    test('default values', () {
      const config = OTPRateLimitConfig();
      expect(config.maxRequestsPerHour, 5);
      expect(config.maxRequestsPerDay, 10);
      expect(config.cooldownSeconds, 60);
      expect(config.progressiveDelayMultiplier, 1.5);
      expect(config.maxCooldownSeconds, 300);
      expect(config.lockoutThreshold, 5);
      expect(config.lockoutDurationMinutes, 30);
    });

    test('fromJson parses all fields', () {
      final json = {
        'max_requests_per_hour': 10,
        'max_requests_per_day': 20,
        'cooldown_seconds': 30,
        'progressive_delay_multiplier': 2.0,
        'max_cooldown_seconds': 600,
        'lockout_threshold': 3,
        'lockout_duration_minutes': 60,
      };

      final config = OTPRateLimitConfig.fromJson(json);
      expect(config.maxRequestsPerHour, 10);
      expect(config.maxRequestsPerDay, 20);
      expect(config.cooldownSeconds, 30);
      expect(config.progressiveDelayMultiplier, 2.0);
      expect(config.maxCooldownSeconds, 600);
      expect(config.lockoutThreshold, 3);
      expect(config.lockoutDurationMinutes, 60);
    });

    test('toJson produces correct output', () {
      const config = OTPRateLimitConfig(
        maxRequestsPerHour: 7,
        cooldownSeconds: 45,
      );

      final json = config.toJson();
      expect(json['max_requests_per_hour'], 7);
      expect(json['cooldown_seconds'], 45);
    });

    test('calculateCooldown returns base cooldown for attempt 1', () {
      const config = OTPRateLimitConfig(cooldownSeconds: 60);
      expect(config.calculateCooldown(1), 60);
    });

    test('calculateCooldown applies progressive delay for attempt 2', () {
      const config = OTPRateLimitConfig(
        cooldownSeconds: 60,
        progressiveDelayMultiplier: 1.5,
      );
      // attempt 2: 60 * (1.5 * (2-1)) = 60 * 1.5 = 90
      expect(config.calculateCooldown(2), 90);
    });

    test('calculateCooldown caps at maxCooldownSeconds', () {
      const config = OTPRateLimitConfig(
        cooldownSeconds: 60,
        progressiveDelayMultiplier: 2.0,
        maxCooldownSeconds: 300,
      );
      // attempt 10: 60 * (2.0 * 9) = 60 * 18 = 1080 > 300
      expect(config.calculateCooldown(10), 300);
    });

    test('toString includes key info', () {
      const config = OTPRateLimitConfig(maxRequestsPerHour: 5, cooldownSeconds: 60);
      expect(config.toString(), contains('maxRequestsPerHour: 5'));
      expect(config.toString(), contains('cooldownSeconds: 60'));
    });
  });

  // ===========================================================================
  // OTPConfig Tests
  // ===========================================================================
  group('OTPConfig', () {
    test('defaults factory creates config with channels', () {
      final config = OTPConfig.defaults();
      expect(config.version, 1);
      expect(config.otpLength, 6);
      expect(config.expirationSeconds, 300);
      expect(config.resendCooldownSeconds, 60);
      expect(config.maxAttempts, 3);
      expect(config.enableAutoVerify, isTrue);
      expect(config.enableBiometricFallback, isFalse);
      expect(config.channels.length, 4);
      expect(config.channels.containsKey('sms'), isTrue);
      expect(config.channels.containsKey('whatsapp'), isTrue);
      expect(config.channels.containsKey('telegram'), isTrue);
      expect(config.channels.containsKey('email'), isTrue);
    });

    test('getEnabledChannels returns sorted by priority', () {
      final config = OTPConfig.defaults();
      final enabled = config.getEnabledChannels();
      expect(enabled.isNotEmpty, isTrue);
      // SMS has priority 1, should be first
      expect(enabled.first.key, 'sms');
    });

    test('getPrimaryChannels filters by showAsPrimary', () {
      final config = OTPConfig.defaults();
      final primary = config.getPrimaryChannels();
      // SMS and WhatsApp are primary in defaults
      expect(primary.length, 2);
      final keys = primary.map((e) => e.key).toList();
      expect(keys, contains('sms'));
      expect(keys, contains('whatsapp'));
    });

    test('getChannelConfig returns config for valid channel', () {
      final config = OTPConfig.defaults();
      final smsConfig = config.getChannelConfig(OTPChannel.sms);
      expect(smsConfig, isNotNull);
      expect(smsConfig!.enabled, isTrue);
    });

    test('isFeatureEnabled returns true for enabled feature', () {
      final config = OTPConfig.defaults();
      expect(config.isFeatureEnabled('enable_multi_channel'), isTrue);
    });

    test('isFeatureEnabled returns false for disabled feature', () {
      final config = OTPConfig.defaults();
      expect(config.isFeatureEnabled('enable_geo_blocking'), isFalse);
    });

    test('isFeatureEnabled returns false for unknown feature', () {
      final config = OTPConfig.defaults();
      expect(config.isFeatureEnabled('nonexistent_feature'), isFalse);
    });

    test('getProviderConfig returns config for known provider', () {
      final config = OTPConfig.defaults();
      final twilioConfig = config.getProviderConfig('twilio');
      expect(twilioConfig, isNotNull);
      expect(twilioConfig!.containsKey('fallback_enabled'), isTrue);
    });

    test('getProviderConfig returns null for unknown provider', () {
      final config = OTPConfig.defaults();
      expect(config.getProviderConfig('nonexistent'), isNull);
    });

    test('expirationDuration returns correct duration', () {
      final config = OTPConfig(
        lastUpdated: DateTime.now(),
        expirationSeconds: 300,
      );
      expect(config.expirationDuration, const Duration(seconds: 300));
    });

    test('resendCooldownDuration returns correct duration', () {
      final config = OTPConfig(
        lastUpdated: DateTime.now(),
        resendCooldownSeconds: 90,
      );
      expect(config.resendCooldownDuration, const Duration(seconds: 90));
    });

    test('fromJson parses full configuration', () {
      final json = {
        'version': 2,
        'last_updated': '2026-03-01T00:00:00.000Z',
        'otp_length': 4,
        'expiration_seconds': 180,
        'resend_cooldown_seconds': 30,
        'max_attempts': 5,
        'enable_auto_verify': false,
        'enable_biometric_fallback': true,
        'channels': {
          'sms': {
            'enabled': true,
            'display_name': 'SMS',
            'display_name_ar': 'رسالة',
            'priority': 1,
          },
        },
        'rate_limit': {
          'max_requests_per_hour': 8,
        },
        'provider_configs': {
          'twilio': {'sid': '123'},
        },
        'feature_flags': {
          'enable_multi_channel': false,
        },
      };

      final config = OTPConfig.fromJson(json);
      expect(config.version, 2);
      expect(config.otpLength, 4);
      expect(config.expirationSeconds, 180);
      expect(config.maxAttempts, 5);
      expect(config.enableAutoVerify, isFalse);
      expect(config.enableBiometricFallback, isTrue);
      expect(config.channels.length, 1);
      expect(config.rateLimit.maxRequestsPerHour, 8);
      expect(config.providerConfigs['twilio']?['sid'], '123');
      expect(config.featureFlags['enable_multi_channel'], isFalse);
    });

    test('copyWith modifies specified fields', () {
      final original = OTPConfig(
        lastUpdated: DateTime.now(),
        otpLength: 6,
        maxAttempts: 3,
      );

      final modified = original.copyWith(otpLength: 8, maxAttempts: 5);
      expect(modified.otpLength, 8);
      expect(modified.maxAttempts, 5);
      expect(modified.version, original.version);
    });

    test('toString includes key info', () {
      final config = OTPConfig(
        lastUpdated: DateTime.now(),
        version: 2,
        otpLength: 6,
      );

      expect(config.toString(), contains('version: 2'));
      expect(config.toString(), contains('otpLength: 6'));
    });
  });

  // ===========================================================================
  // OTPService Constants Tests
  // ===========================================================================
  group('OTPService constants', () {
    test('maxSendAttempts is 5', () {
      expect(OTPService.maxSendAttempts, 5);
    });

    test('maxVerifyAttempts is 5', () {
      expect(OTPService.maxVerifyAttempts, 5);
    });

    test('defaultCooldownSeconds is 60', () {
      expect(OTPService.defaultCooldownSeconds, 60);
    });

    test('otpValiditySeconds is 300', () {
      expect(OTPService.otpValiditySeconds, 300);
    });
  });
}
