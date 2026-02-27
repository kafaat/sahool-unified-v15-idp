import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/http/api_client.dart';
import 'package:sahool_field_app/core/auth/secure_storage_service.dart';
import 'package:sahool_field_app/core/network/api_result.dart';
import 'package:sahool_field_app/features/auth/services/otp_service.dart';
import 'package:sahool_field_app/features/auth/config/otp_config.dart'
    hide OTPChannel;

// ═══════════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════════

class MockApiClient extends Mock implements ApiClient {}

class MockSecureStorageService extends Mock implements SecureStorageService {}

void main() {
  late MockApiClient mockApiClient;
  late MockSecureStorageService mockSecureStorage;
  late OTPService otpService;

  setUp(() {
    mockApiClient = MockApiClient();
    mockSecureStorage = MockSecureStorageService();
    otpService = OTPService(
      apiClient: mockApiClient,
      secureStorage: mockSecureStorage,
    );
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPChannel Enum Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPChannel', () {
    test('apiValue returns correct values for each channel', () {
      expect(OTPChannel.sms.apiValue, 'sms');
      expect(OTPChannel.whatsapp.apiValue, 'whatsapp');
      expect(OTPChannel.telegram.apiValue, 'telegram');
      expect(OTPChannel.email.apiValue, 'email');
    });

    test('displayName returns English names', () {
      expect(OTPChannel.sms.displayName, 'SMS');
      expect(OTPChannel.whatsapp.displayName, 'WhatsApp');
      expect(OTPChannel.telegram.displayName, 'Telegram');
      expect(OTPChannel.email.displayName, 'Email');
    });

    test('displayNameArabic returns Arabic names', () {
      expect(OTPChannel.sms.displayNameArabic, contains('SMS'));
      expect(OTPChannel.whatsapp.displayNameArabic, 'واتساب');
      expect(OTPChannel.telegram.displayNameArabic, 'تيليجرام');
      expect(OTPChannel.email.displayNameArabic, contains('الإلكتروني'));
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPPurpose Enum Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPPurpose', () {
    test('apiValue returns correct values for each purpose', () {
      expect(OTPPurpose.passwordReset.apiValue, 'password_reset');
      expect(OTPPurpose.phoneVerification.apiValue, 'phone_verification');
      expect(OTPPurpose.twoFactor.apiValue, 'two_factor');
      expect(OTPPurpose.accountRecovery.apiValue, 'account_recovery');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPState Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPState', () {
    test('default state has expected initial values', () {
      // Arrange & Act
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );

      // Assert
      expect(state.identifier, 'test@sahool.app');
      expect(state.channel, OTPChannel.sms);
      expect(state.purpose, OTPPurpose.passwordReset);
      expect(state.sendAttempts, 0);
      expect(state.verifyAttempts, 0);
      expect(state.isVerified, isFalse);
      expect(state.isLoading, isFalse);
      expect(state.cooldownSeconds, 0);
      expect(state.error, isNull);
      expect(state.resetToken, isNull);
    });

    test('isExpired returns true when expiresAt is null', () {
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        expiresAt: null,
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
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        cooldownSeconds: 0,
        isLoading: false,
      );

      expect(state.canResend, isTrue);
    });

    test('canResend returns false when cooldown is positive', () {
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        cooldownSeconds: 30,
        isLoading: false,
      );

      expect(state.canResend, isFalse);
    });

    test('canResend returns false when loading', () {
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        cooldownSeconds: 0,
        isLoading: true,
      );

      expect(state.canResend, isFalse);
    });

    test('isLocked returns true at max verify attempts', () {
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        verifyAttempts: OTPService.maxVerifyAttempts,
      );

      expect(state.isLocked, isTrue);
    });

    test('isLocked returns false below max verify attempts', () {
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        verifyAttempts: OTPService.maxVerifyAttempts - 1,
      );

      expect(state.isLocked, isFalse);
    });

    test('isSendLocked returns true at max send attempts', () {
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        sendAttempts: OTPService.maxSendAttempts,
      );

      expect(state.isSendLocked, isTrue);
    });

    test('remainingSeconds returns 0 when expiresAt is null', () {
      const state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );

      expect(state.remainingSeconds, 0);
    });

    test('remainingSeconds returns positive value for future expiry', () {
      final state = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        expiresAt: DateTime.now().add(const Duration(seconds: 120)),
      );

      expect(state.remainingSeconds, greaterThan(0));
      expect(state.remainingSeconds, lessThanOrEqualTo(120));
    });

    test('copyWith preserves unchanged values', () {
      const original = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        sendAttempts: 2,
      );

      final updated = original.copyWith(verifyAttempts: 1);

      expect(updated.identifier, 'test@sahool.app');
      expect(updated.sendAttempts, 2);
      expect(updated.verifyAttempts, 1);
    });

    test('copyWith clearError removes error', () {
      const original = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        error: 'Some error',
      );

      final updated = original.copyWith(clearError: true);

      expect(updated.error, isNull);
    });

    test('copyWith clearResetToken removes reset token', () {
      const original = OTPState(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
        resetToken: 'some-token',
      );

      final updated = original.copyWith(clearResetToken: true);

      expect(updated.resetToken, isNull);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SendOTPResponse Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('SendOTPResponse.fromJson', () {
    test('parses complete response', () {
      final json = {
        'success': true,
        'message': 'OTP sent',
        'expires_in': 300,
        'cooldown': 60,
        'masked_destination': '+966***4567',
      };

      final response = SendOTPResponse.fromJson(json);

      expect(response.success, isTrue);
      expect(response.message, 'OTP sent');
      expect(response.expiresInSeconds, 300);
      expect(response.cooldownSeconds, 60);
      expect(response.maskedDestination, '+966***4567');
    });

    test('handles alternate key names', () {
      final json = {
        'status': 'success',
        'expiresIn': 600,
        'resend_cooldown': 30,
        'maskedDestination': '+966***4567',
      };

      final response = SendOTPResponse.fromJson(json);

      expect(response.success, isTrue);
      expect(response.expiresInSeconds, 600);
      expect(response.cooldownSeconds, 30);
    });

    test('uses defaults for missing fields', () {
      final json = <String, dynamic>{
        'success': true,
      };

      final response = SendOTPResponse.fromJson(json);

      expect(response.success, isTrue);
      expect(response.expiresInSeconds, 300);
      expect(response.cooldownSeconds, 60);
      expect(response.message, isNull);
      expect(response.maskedDestination, isNull);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // VerifyOTPResponse Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('VerifyOTPResponse.fromJson', () {
    test('parses successful verification with reset token', () {
      final json = {
        'success': true,
        'message': 'OTP verified',
        'reset_token': 'abc-reset-token-123',
        'remaining_attempts': 3,
      };

      final response = VerifyOTPResponse.fromJson(json);

      expect(response.success, isTrue);
      expect(response.message, 'OTP verified');
      expect(response.resetToken, 'abc-reset-token-123');
      expect(response.remainingAttempts, 3);
    });

    test('handles alternate key names for reset token', () {
      final json = {
        'success': true,
        'token': 'fallback-token',
        'remainingAttempts': 2,
      };

      final response = VerifyOTPResponse.fromJson(json);

      expect(response.resetToken, 'fallback-token');
      expect(response.remainingAttempts, 2);
    });

    test('handles failed verification', () {
      final json = {
        'success': false,
        'message': 'Invalid OTP',
        'remaining_attempts': 2,
      };

      final response = VerifyOTPResponse.fromJson(json);

      expect(response.success, isFalse);
      expect(response.message, 'Invalid OTP');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPException Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPException', () {
    test('toString returns message', () {
      final exception = OTPException('Test error', code: 'TEST_001');

      expect(exception.toString(), 'Test error');
      expect(exception.code, 'TEST_001');
      expect(exception.isRateLimited, isFalse);
    });

    test('rate limited exception has correct properties', () {
      final exception = OTPException(
        'Rate limited',
        code: 'RATE_LIMIT',
        isRateLimited: true,
        retryAfterSeconds: 60,
      );

      expect(exception.isRateLimited, isTrue);
      expect(exception.retryAfterSeconds, 60);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPService Constants Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPService constants', () {
    test('has correct default values', () {
      expect(OTPService.maxSendAttempts, 5);
      expect(OTPService.maxVerifyAttempts, 5);
      expect(OTPService.defaultCooldownSeconds, 60);
      expect(OTPService.otpValiditySeconds, 300);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPConfig Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPConfig', () {
    test('defaults() creates config with standard values', () {
      // Act
      final config = OTPConfig.defaults();

      // Assert
      expect(config.version, 1);
      expect(config.otpLength, 6);
      expect(config.expirationSeconds, 300);
      expect(config.resendCooldownSeconds, 60);
      expect(config.maxAttempts, 3);
      expect(config.enableAutoVerify, isTrue);
      expect(config.enableBiometricFallback, isFalse);
    });

    test('defaults() has all 4 channels configured', () {
      final config = OTPConfig.defaults();

      expect(config.channels.length, 4);
      expect(config.channels.containsKey('sms'), isTrue);
      expect(config.channels.containsKey('whatsapp'), isTrue);
      expect(config.channels.containsKey('telegram'), isTrue);
      expect(config.channels.containsKey('email'), isTrue);
    });

    test('defaults() has SMS and WhatsApp as primary channels', () {
      final config = OTPConfig.defaults();

      final primaryChannels = config.getPrimaryChannels();
      expect(primaryChannels.length, 2);
      expect(primaryChannels[0].key, 'sms');
      expect(primaryChannels[1].key, 'whatsapp');
    });

    test('getEnabledChannels returns channels sorted by priority', () {
      final config = OTPConfig.defaults();

      final enabled = config.getEnabledChannels();

      // All 4 channels enabled by default, sorted by priority (1,2,3,4)
      expect(enabled.length, 4);
      expect(enabled[0].key, 'sms');
      expect(enabled[1].key, 'whatsapp');
      expect(enabled[2].key, 'telegram');
      expect(enabled[3].key, 'email');
    });

    test('getChannelConfig returns correct config via channels map', () {
      final config = OTPConfig.defaults();

      // Access via channels map directly (avoids cross-file OTPChannel type conflict)
      final smsConfig = config.channels['sms'];
      expect(smsConfig, isNotNull);
      expect(smsConfig!.enabled, isTrue);
      expect(smsConfig.displayName, 'SMS');
    });

    test('isFeatureEnabled returns false for unknown features', () {
      final config = OTPConfig.defaults();

      expect(config.isFeatureEnabled('nonexistent_feature'), isFalse);
    });

    test('isFeatureEnabled returns true for known features', () {
      final config = OTPConfig.defaults();

      expect(config.isFeatureEnabled('enable_multi_channel'), isTrue);
      expect(config.isFeatureEnabled('enable_geo_blocking'), isFalse);
    });

    test('expirationDuration returns correct Duration', () {
      final config = OTPConfig.defaults();

      expect(config.expirationDuration, const Duration(seconds: 300));
    });

    test('resendCooldownDuration returns correct Duration', () {
      final config = OTPConfig.defaults();

      expect(config.resendCooldownDuration, const Duration(seconds: 60));
    });

    test('fromJson and toJson are symmetric', () {
      // Arrange
      final original = OTPConfig.defaults();

      // Act
      final json = original.toJson();
      final restored = OTPConfig.fromJson(json);

      // Assert
      expect(restored.version, original.version);
      expect(restored.otpLength, original.otpLength);
      expect(restored.expirationSeconds, original.expirationSeconds);
      expect(restored.resendCooldownSeconds, original.resendCooldownSeconds);
      expect(restored.maxAttempts, original.maxAttempts);
      expect(restored.enableAutoVerify, original.enableAutoVerify);
      expect(restored.channels.length, original.channels.length);
    });

    test('copyWith modifies only specified fields', () {
      final original = OTPConfig.defaults();

      final modified = original.copyWith(
        otpLength: 8,
        maxAttempts: 5,
      );

      expect(modified.otpLength, 8);
      expect(modified.maxAttempts, 5);
      expect(modified.expirationSeconds, original.expirationSeconds);
      expect(modified.channels.length, original.channels.length);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPChannelConfig Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPChannelConfig', () {
    test('fromJson parses all fields', () {
      final json = {
        'enabled': true,
        'display_name': 'SMS',
        'display_name_ar': 'رسالة نصية',
        'priority': 1,
        'max_retries': 5,
        'delivery_timeout_seconds': 45,
        'show_as_primary': true,
        'provider_settings': {'provider': 'twilio'},
      };

      final config = OTPChannelConfig.fromJson(json);

      expect(config.enabled, isTrue);
      expect(config.displayName, 'SMS');
      expect(config.displayNameAr, 'رسالة نصية');
      expect(config.priority, 1);
      expect(config.maxRetries, 5);
      expect(config.deliveryTimeoutSeconds, 45);
      expect(config.showAsPrimary, isTrue);
      expect(config.providerSettings['provider'], 'twilio');
    });

    test('fromJson uses defaults for missing fields', () {
      final json = <String, dynamic>{};

      final config = OTPChannelConfig.fromJson(json);

      expect(config.enabled, isFalse);
      expect(config.displayName, '');
      expect(config.priority, 0);
      expect(config.maxRetries, 3);
      expect(config.deliveryTimeoutSeconds, 30);
      expect(config.showAsPrimary, isFalse);
    });

    test('toJson produces correct map', () {
      const config = OTPChannelConfig(
        enabled: true,
        displayName: 'Test',
        displayNameAr: 'اختبار',
        priority: 2,
      );

      final json = config.toJson();

      expect(json['enabled'], isTrue);
      expect(json['display_name'], 'Test');
      expect(json['display_name_ar'], 'اختبار');
      expect(json['priority'], 2);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPRateLimitConfig Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPRateLimitConfig', () {
    test('default values are correct', () {
      const config = OTPRateLimitConfig();

      expect(config.maxRequestsPerHour, 5);
      expect(config.maxRequestsPerDay, 10);
      expect(config.cooldownSeconds, 60);
      expect(config.progressiveDelayMultiplier, 1.5);
      expect(config.maxCooldownSeconds, 300);
      expect(config.lockoutThreshold, 5);
      expect(config.lockoutDurationMinutes, 30);
    });

    test('calculateCooldown returns base cooldown for first attempt', () {
      const config = OTPRateLimitConfig(cooldownSeconds: 60);

      expect(config.calculateCooldown(1), 60);
    });

    test('calculateCooldown applies progressive multiplier', () {
      const config = OTPRateLimitConfig(
        cooldownSeconds: 60,
        progressiveDelayMultiplier: 1.5,
      );

      final cooldown2 = config.calculateCooldown(2);
      expect(cooldown2, greaterThan(60));
    });

    test('calculateCooldown caps at maxCooldownSeconds', () {
      const config = OTPRateLimitConfig(
        cooldownSeconds: 60,
        progressiveDelayMultiplier: 10.0,
        maxCooldownSeconds: 300,
      );

      final cooldown = config.calculateCooldown(10);
      expect(cooldown, 300);
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
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // OTPStateParams Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('OTPStateParams', () {
    test('equality works correctly', () {
      const params1 = OTPStateParams(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );
      const params2 = OTPStateParams(
        identifier: 'test@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );
      const params3 = OTPStateParams(
        identifier: 'different@sahool.app',
        channel: OTPChannel.sms,
        purpose: OTPPurpose.passwordReset,
      );

      expect(params1, equals(params2));
      expect(params1, isNot(equals(params3)));
      expect(params1.hashCode, params2.hashCode);
    });
  });
}
