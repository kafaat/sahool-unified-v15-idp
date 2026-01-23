import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/http/api_client.dart';
import '../../../core/http/rate_limiter.dart';
import '../../../core/auth/secure_storage_service.dart';
import '../../../core/network/api_result.dart';
import '../../../core/di/providers.dart';
import '../../../core/utils/app_logger.dart';

// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL OTP Service
// خدمة التحقق من رمز OTP متعدد القنوات
// ═══════════════════════════════════════════════════════════════════════════

/// OTP delivery channels
enum OTPChannel {
  sms,
  whatsapp,
  telegram,
  email;

  String get apiValue {
    switch (this) {
      case OTPChannel.sms:
        return 'sms';
      case OTPChannel.whatsapp:
        return 'whatsapp';
      case OTPChannel.telegram:
        return 'telegram';
      case OTPChannel.email:
        return 'email';
    }
  }

  String get displayName {
    switch (this) {
      case OTPChannel.sms:
        return 'SMS';
      case OTPChannel.whatsapp:
        return 'WhatsApp';
      case OTPChannel.telegram:
        return 'Telegram';
      case OTPChannel.email:
        return 'Email';
    }
  }

  String get displayNameArabic {
    switch (this) {
      case OTPChannel.sms:
        return 'رسالة نصية SMS';
      case OTPChannel.whatsapp:
        return 'واتساب';
      case OTPChannel.telegram:
        return 'تيليجرام';
      case OTPChannel.email:
        return 'البريد الإلكتروني';
    }
  }
}

/// OTP purpose types
enum OTPPurpose {
  passwordReset,
  phoneVerification,
  twoFactor,
  accountRecovery;

  String get apiValue {
    switch (this) {
      case OTPPurpose.passwordReset:
        return 'password_reset';
      case OTPPurpose.phoneVerification:
        return 'phone_verification';
      case OTPPurpose.twoFactor:
        return 'two_factor';
      case OTPPurpose.accountRecovery:
        return 'account_recovery';
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// OTP State Management
// ═══════════════════════════════════════════════════════════════════════════

/// OTP session state - tracks a single OTP request
class OTPState {
  final String identifier;
  final OTPChannel channel;
  final OTPPurpose purpose;
  final DateTime? sentAt;
  final DateTime? expiresAt;
  final int sendAttempts;
  final int verifyAttempts;
  final bool isVerified;
  final String? resetToken;
  final String? error;
  final bool isLoading;
  final int cooldownSeconds;

  const OTPState({
    required this.identifier,
    required this.channel,
    required this.purpose,
    this.sentAt,
    this.expiresAt,
    this.sendAttempts = 0,
    this.verifyAttempts = 0,
    this.isVerified = false,
    this.resetToken,
    this.error,
    this.isLoading = false,
    this.cooldownSeconds = 0,
  });

  OTPState copyWith({
    String? identifier,
    OTPChannel? channel,
    OTPPurpose? purpose,
    DateTime? sentAt,
    DateTime? expiresAt,
    int? sendAttempts,
    int? verifyAttempts,
    bool? isVerified,
    String? resetToken,
    String? error,
    bool? isLoading,
    int? cooldownSeconds,
    bool clearError = false,
    bool clearResetToken = false,
  }) {
    return OTPState(
      identifier: identifier ?? this.identifier,
      channel: channel ?? this.channel,
      purpose: purpose ?? this.purpose,
      sentAt: sentAt ?? this.sentAt,
      expiresAt: expiresAt ?? this.expiresAt,
      sendAttempts: sendAttempts ?? this.sendAttempts,
      verifyAttempts: verifyAttempts ?? this.verifyAttempts,
      isVerified: isVerified ?? this.isVerified,
      resetToken: clearResetToken ? null : (resetToken ?? this.resetToken),
      error: clearError ? null : (error ?? this.error),
      isLoading: isLoading ?? this.isLoading,
      cooldownSeconds: cooldownSeconds ?? this.cooldownSeconds,
    );
  }

  /// Check if OTP has expired
  bool get isExpired {
    if (expiresAt == null) return true;
    return DateTime.now().isAfter(expiresAt!);
  }

  /// Check if user can resend OTP (cooldown period passed)
  bool get canResend => cooldownSeconds <= 0 && !isLoading;

  /// Remaining time until OTP expires (in seconds)
  int get remainingSeconds {
    if (expiresAt == null) return 0;
    final remaining = expiresAt!.difference(DateTime.now()).inSeconds;
    return remaining > 0 ? remaining : 0;
  }

  /// Check if max verification attempts exceeded
  bool get isLocked => verifyAttempts >= OTPService.maxVerifyAttempts;

  /// Check if max send attempts exceeded
  bool get isSendLocked => sendAttempts >= OTPService.maxSendAttempts;
}

// ═══════════════════════════════════════════════════════════════════════════
// OTP Response Models
// ═══════════════════════════════════════════════════════════════════════════

/// Response from send OTP API
class SendOTPResponse {
  final bool success;
  final String? message;
  final int? expiresInSeconds;
  final int? cooldownSeconds;
  final String? maskedDestination;

  const SendOTPResponse({
    required this.success,
    this.message,
    this.expiresInSeconds,
    this.cooldownSeconds,
    this.maskedDestination,
  });

  factory SendOTPResponse.fromJson(Map<String, dynamic> json) {
    return SendOTPResponse(
      success: json['success'] ?? json['status'] == 'success',
      message: json['message'] as String?,
      expiresInSeconds: json['expires_in'] ?? json['expiresIn'] ?? 300,
      cooldownSeconds: json['cooldown'] ?? json['resend_cooldown'] ?? 60,
      maskedDestination: json['masked_destination'] ?? json['maskedDestination'],
    );
  }
}

/// Response from verify OTP API
class VerifyOTPResponse {
  final bool success;
  final String? message;
  final String? resetToken;
  final int? remainingAttempts;

  const VerifyOTPResponse({
    required this.success,
    this.message,
    this.resetToken,
    this.remainingAttempts,
  });

  factory VerifyOTPResponse.fromJson(Map<String, dynamic> json) {
    return VerifyOTPResponse(
      success: json['success'] ?? json['status'] == 'success' ?? json['valid'] == true,
      message: json['message'] as String?,
      resetToken: json['reset_token'] ?? json['resetToken'] ?? json['token'],
      remainingAttempts: json['remaining_attempts'] ?? json['remainingAttempts'],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// OTP Service Exception
// ═══════════════════════════════════════════════════════════════════════════

/// OTP-specific exceptions
class OTPException implements Exception {
  final String message;
  final String? code;
  final bool isRateLimited;
  final int? retryAfterSeconds;

  OTPException(
    this.message, {
    this.code,
    this.isRateLimited = false,
    this.retryAfterSeconds,
  });

  @override
  String toString() => message;
}

// ═══════════════════════════════════════════════════════════════════════════
// Secure Storage Keys for OTP
// ═══════════════════════════════════════════════════════════════════════════

class _OTPStorageKeys {
  static const resetTokenKey = 'otp_reset_token';
  static const resetTokenExpiryKey = 'otp_reset_token_expiry';
  static const otpStateKey = 'otp_state';
  static const lastSendTimeKey = 'otp_last_send_time';
}

// ═══════════════════════════════════════════════════════════════════════════
// OTP Service
// ═══════════════════════════════════════════════════════════════════════════

/// SAHOOL OTP Service
/// خدمة إرسال والتحقق من رموز OTP
///
/// Features:
/// - Multi-channel support (SMS, WhatsApp, Telegram, Email)
/// - Rate limiting protection
/// - Secure token storage
/// - Automatic retry with exponential backoff
/// - Offline-aware error handling
class OTPService {
  final ApiClient apiClient;
  final SecureStorageService secureStorage;

  // Rate limiting configuration
  static const int maxSendAttempts = 5;
  static const int maxVerifyAttempts = 5;
  static const int defaultCooldownSeconds = 60;
  static const int otpValiditySeconds = 300; // 5 minutes

  // API endpoints
  static const String _sendOTPEndpoint = '/api/v1/auth/otp/send';
  static const String _verifyOTPEndpoint = '/api/v1/auth/otp/verify';
  static const String _resendOTPEndpoint = '/api/v1/auth/otp/resend';

  OTPService({
    required this.apiClient,
    required this.secureStorage,
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Send OTP
  // ═══════════════════════════════════════════════════════════════════════════

  /// Send OTP to the specified identifier via the chosen channel
  ///
  /// [identifier] - Email or phone number
  /// [channel] - Delivery channel (SMS, WhatsApp, Telegram, Email)
  /// [purpose] - Purpose of OTP (password reset, verification, 2FA)
  ///
  /// Returns [ApiResult] with [SendOTPResponse] on success
  Future<ApiResult<SendOTPResponse>> sendOTP({
    required String identifier,
    required OTPChannel channel,
    required OTPPurpose purpose,
  }) async {
    AppLogger.i('Sending OTP', tag: 'OTP', data: {
      'channel': channel.apiValue,
      'purpose': purpose.apiValue,
      // Identifier is PII - will be filtered by logger
    });

    try {
      // Check rate limit status before making request
      final rateLimitStatus = apiClient.getRateLimitStatus('auth');
      if (rateLimitStatus.availableTokens <= 0) {
        AppLogger.w('OTP send rate limited', tag: 'OTP', data: {
          'queuedRequests': rateLimitStatus.queuedRequests,
        });
      }

      final response = await apiClient.post(
        _sendOTPEndpoint,
        {
          'identifier': identifier,
          'channel': channel.apiValue,
          'purpose': purpose.apiValue,
        },
      );

      // Parse response
      final data = _parseResponse(response);
      final otpResponse = SendOTPResponse.fromJson(data);

      if (otpResponse.success) {
        AppLogger.i('OTP sent successfully', tag: 'OTP', data: {
          'channel': channel.apiValue,
          'expiresIn': otpResponse.expiresInSeconds,
        });

        // Store last send time for rate limiting
        await _storeLastSendTime(identifier, channel, purpose);

        return Success(otpResponse);
      } else {
        return Failure(
          otpResponse.message ?? 'فشل إرسال رمز التحقق',
          statusCode: 400,
        );
      }
    } on ApiException catch (e) {
      AppLogger.e('OTP send failed', tag: 'OTP', error: e);
      return _handleApiException<SendOTPResponse>(e);
    } on RateLimitException catch (e) {
      AppLogger.w('OTP send rate limited', tag: 'OTP', error: e);
      return Failure(
        'تم تجاوز الحد المسموح. حاول مرة أخرى بعد قليل',
        statusCode: 429,
      );
    } catch (e, stackTrace) {
      AppLogger.e('OTP send error', tag: 'OTP', error: e, stackTrace: stackTrace);
      return Failure('حدث خطأ غير متوقع');
    }
  }

  /// Resend OTP with the same parameters
  Future<ApiResult<SendOTPResponse>> resendOTP({
    required String identifier,
    required OTPChannel channel,
    required OTPPurpose purpose,
  }) async {
    AppLogger.i('Resending OTP', tag: 'OTP', data: {
      'channel': channel.apiValue,
      'purpose': purpose.apiValue,
    });

    try {
      final response = await apiClient.post(
        _resendOTPEndpoint,
        {
          'identifier': identifier,
          'channel': channel.apiValue,
          'purpose': purpose.apiValue,
        },
      );

      final data = _parseResponse(response);
      final otpResponse = SendOTPResponse.fromJson(data);

      if (otpResponse.success) {
        AppLogger.i('OTP resent successfully', tag: 'OTP');
        await _storeLastSendTime(identifier, channel, purpose);
        return Success(otpResponse);
      } else {
        return Failure(
          otpResponse.message ?? 'فشل إعادة إرسال رمز التحقق',
          statusCode: 400,
        );
      }
    } on ApiException catch (e) {
      return _handleApiException<SendOTPResponse>(e);
    } on RateLimitException {
      return Failure(
        'انتظر قليلاً قبل إعادة الإرسال',
        statusCode: 429,
      );
    } catch (e) {
      AppLogger.e('OTP resend error', tag: 'OTP', error: e);
      return Failure('حدث خطأ غير متوقع');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Verify OTP
  // ═══════════════════════════════════════════════════════════════════════════

  /// Verify the OTP code entered by the user
  ///
  /// [identifier] - Email or phone number used to send OTP
  /// [otp] - The 6-digit OTP code
  /// [purpose] - Purpose of OTP verification
  ///
  /// Returns [ApiResult] with [VerifyOTPResponse] containing reset token on success
  Future<ApiResult<VerifyOTPResponse>> verifyOTP({
    required String identifier,
    required String otp,
    required OTPPurpose purpose,
  }) async {
    AppLogger.i('Verifying OTP', tag: 'OTP', data: {
      'purpose': purpose.apiValue,
      // OTP code is sensitive - not logged
    });

    // Validate OTP format
    if (!_isValidOTPFormat(otp)) {
      return const Failure('رمز التحقق يجب أن يتكون من 6 أرقام', statusCode: 400);
    }

    try {
      final response = await apiClient.post(
        _verifyOTPEndpoint,
        {
          'identifier': identifier,
          'otp': otp,
          'purpose': purpose.apiValue,
        },
      );

      final data = _parseResponse(response);
      final verifyResponse = VerifyOTPResponse.fromJson(data);

      if (verifyResponse.success) {
        AppLogger.i('OTP verified successfully', tag: 'OTP');

        // Securely store reset token if provided (for password reset flow)
        if (verifyResponse.resetToken != null && purpose == OTPPurpose.passwordReset) {
          await _storeResetToken(verifyResponse.resetToken!);
        }

        return Success(verifyResponse);
      } else {
        final message = verifyResponse.message ?? 'رمز التحقق غير صحيح';
        final remainingAttemptsMsg = verifyResponse.remainingAttempts != null
            ? ' (${verifyResponse.remainingAttempts} محاولات متبقية)'
            : '';

        return Failure(
          '$message$remainingAttemptsMsg',
          statusCode: 400,
        );
      }
    } on ApiException catch (e) {
      AppLogger.e('OTP verification failed', tag: 'OTP', error: e);
      return _handleApiException<VerifyOTPResponse>(e);
    } on RateLimitException {
      return Failure(
        'تم تجاوز عدد المحاولات. حاول مرة أخرى لاحقاً',
        statusCode: 429,
      );
    } catch (e, stackTrace) {
      AppLogger.e('OTP verify error', tag: 'OTP', error: e, stackTrace: stackTrace);
      return Failure('حدث خطأ غير متوقع');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Reset Token Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Store reset token securely after OTP verification
  Future<void> _storeResetToken(String token) async {
    await secureStorage.write(_OTPStorageKeys.resetTokenKey, token);
    // Token expires in 15 minutes
    final expiry = DateTime.now().add(const Duration(minutes: 15));
    await secureStorage.write(
      _OTPStorageKeys.resetTokenExpiryKey,
      expiry.toIso8601String(),
    );
    AppLogger.d('Reset token stored securely', tag: 'OTP');
  }

  /// Get stored reset token if valid
  Future<String?> getResetToken() async {
    final token = await secureStorage.read(_OTPStorageKeys.resetTokenKey);
    if (token == null) return null;

    // Check expiry
    final expiryStr = await secureStorage.read(_OTPStorageKeys.resetTokenExpiryKey);
    if (expiryStr != null) {
      final expiry = DateTime.parse(expiryStr);
      if (DateTime.now().isAfter(expiry)) {
        // Token expired - clear it
        await clearResetToken();
        return null;
      }
    }

    return token;
  }

  /// Clear stored reset token
  Future<void> clearResetToken() async {
    await secureStorage.delete(_OTPStorageKeys.resetTokenKey);
    await secureStorage.delete(_OTPStorageKeys.resetTokenExpiryKey);
    AppLogger.d('Reset token cleared', tag: 'OTP');
  }

  /// Check if reset token is valid and not expired
  Future<bool> hasValidResetToken() async {
    final token = await getResetToken();
    return token != null;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Rate Limiting Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  /// Store last OTP send time for rate limiting
  Future<void> _storeLastSendTime(
    String identifier,
    OTPChannel channel,
    OTPPurpose purpose,
  ) async {
    final key = '${_OTPStorageKeys.lastSendTimeKey}_${channel.apiValue}_${purpose.apiValue}';
    await secureStorage.write(key, DateTime.now().toIso8601String());
  }

  /// Get cooldown remaining seconds
  Future<int> getCooldownRemaining(OTPChannel channel, OTPPurpose purpose) async {
    final key = '${_OTPStorageKeys.lastSendTimeKey}_${channel.apiValue}_${purpose.apiValue}';
    final lastSendStr = await secureStorage.read(key);

    if (lastSendStr == null) return 0;

    final lastSend = DateTime.parse(lastSendStr);
    final elapsed = DateTime.now().difference(lastSend).inSeconds;
    final remaining = defaultCooldownSeconds - elapsed;

    return remaining > 0 ? remaining : 0;
  }

  /// Check if OTP can be sent (cooldown passed)
  Future<bool> canSendOTP(OTPChannel channel, OTPPurpose purpose) async {
    final remaining = await getCooldownRemaining(channel, purpose);
    return remaining <= 0;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  /// Parse API response to Map
  Map<String, dynamic> _parseResponse(dynamic response) {
    if (response == null) {
      throw OTPException('استجابة فارغة من الخادم');
    }

    if (response is Map<String, dynamic>) {
      // Check for data wrapper
      if (response.containsKey('data') && response['data'] is Map) {
        return response['data'] as Map<String, dynamic>;
      }
      return response;
    }

    if (response is String) {
      try {
        return jsonDecode(response) as Map<String, dynamic>;
      } catch (e) {
        throw OTPException('استجابة غير صالحة من الخادم');
      }
    }

    throw OTPException('نوع استجابة غير متوقع');
  }

  /// Validate OTP format (6 digits)
  bool _isValidOTPFormat(String otp) {
    return RegExp(r'^\d{6}$').hasMatch(otp);
  }

  /// Handle API exceptions and convert to user-friendly messages
  ApiResult<T> _handleApiException<T>(ApiException e) {
    String message;
    int? statusCode = e.statusCode;

    if (e.isNetworkError) {
      message = 'لا يوجد اتصال بالإنترنت. تحقق من اتصالك وحاول مرة أخرى';
    } else if (e.statusCode == 429) {
      message = 'تم تجاوز الحد المسموح للمحاولات. حاول مرة أخرى بعد قليل';
    } else if (e.statusCode == 401) {
      message = 'انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى';
    } else if (e.statusCode == 400) {
      message = e.message.isNotEmpty ? e.message : 'بيانات غير صحيحة';
    } else if (e.statusCode != null && e.statusCode! >= 500) {
      message = 'خطأ في الخادم. حاول مرة أخرى لاحقاً';
    } else {
      message = e.message.isNotEmpty ? e.message : 'حدث خطأ غير متوقع';
    }

    return Failure(message, statusCode: statusCode);
  }

  /// Clear all OTP-related stored data
  Future<void> clearAllOTPData() async {
    await clearResetToken();
    // Clear any other OTP-related storage
    final keys = await secureStorage.getAllKeys();
    for (final key in keys) {
      if (key.startsWith('otp_')) {
        await secureStorage.delete(key);
      }
    }
    AppLogger.d('All OTP data cleared', tag: 'OTP');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════

/// OTP Service Provider
final otpServiceProvider = Provider<OTPService>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  final secureStorage = ref.watch(secureStorageProvider);

  return OTPService(
    apiClient: apiClient,
    secureStorage: secureStorage,
  );
});

/// OTP State Notifier Provider - manages OTP session state
final otpStateNotifierProvider = StateNotifierProvider.autoDispose
    .family<OTPStateNotifier, OTPState, OTPStateParams>((ref, params) {
  final otpService = ref.watch(otpServiceProvider);
  return OTPStateNotifier(
    otpService: otpService,
    identifier: params.identifier,
    channel: params.channel,
    purpose: params.purpose,
  );
});

/// Parameters for OTP state provider
class OTPStateParams {
  final String identifier;
  final OTPChannel channel;
  final OTPPurpose purpose;

  const OTPStateParams({
    required this.identifier,
    required this.channel,
    required this.purpose,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is OTPStateParams &&
          runtimeType == other.runtimeType &&
          identifier == other.identifier &&
          channel == other.channel &&
          purpose == other.purpose;

  @override
  int get hashCode => identifier.hashCode ^ channel.hashCode ^ purpose.hashCode;
}

/// OTP State Notifier - handles OTP flow state management
class OTPStateNotifier extends StateNotifier<OTPState> {
  final OTPService _otpService;
  Timer? _cooldownTimer;
  Timer? _expiryTimer;

  OTPStateNotifier({
    required OTPService otpService,
    required String identifier,
    required OTPChannel channel,
    required OTPPurpose purpose,
  })  : _otpService = otpService,
        super(OTPState(
          identifier: identifier,
          channel: channel,
          purpose: purpose,
        )) {
    // Initialize cooldown check
    _initializeCooldown();
  }

  @override
  void dispose() {
    _cooldownTimer?.cancel();
    _expiryTimer?.cancel();
    super.dispose();
  }

  /// Initialize cooldown state from storage
  Future<void> _initializeCooldown() async {
    final remaining = await _otpService.getCooldownRemaining(
      state.channel,
      state.purpose,
    );
    if (remaining > 0) {
      state = state.copyWith(cooldownSeconds: remaining);
      _startCooldownTimer();
    }
  }

  /// Send OTP to user
  Future<bool> sendOTP() async {
    if (state.isLoading || state.isSendLocked) return false;

    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _otpService.sendOTP(
      identifier: state.identifier,
      channel: state.channel,
      purpose: state.purpose,
    );

    return result.when(
      success: (response) {
        final expiresAt = DateTime.now().add(
          Duration(seconds: response.expiresInSeconds ?? OTPService.otpValiditySeconds),
        );

        state = state.copyWith(
          isLoading: false,
          sentAt: DateTime.now(),
          expiresAt: expiresAt,
          sendAttempts: state.sendAttempts + 1,
          cooldownSeconds: response.cooldownSeconds ?? OTPService.defaultCooldownSeconds,
          clearError: true,
        );

        _startCooldownTimer();
        _startExpiryTimer();

        return true;
      },
      failure: (message, statusCode) {
        state = state.copyWith(
          isLoading: false,
          error: message,
          sendAttempts: state.sendAttempts + 1,
        );
        return false;
      },
    );
  }

  /// Resend OTP
  Future<bool> resendOTP() async {
    if (!state.canResend || state.isSendLocked) return false;

    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _otpService.resendOTP(
      identifier: state.identifier,
      channel: state.channel,
      purpose: state.purpose,
    );

    return result.when(
      success: (response) {
        final expiresAt = DateTime.now().add(
          Duration(seconds: response.expiresInSeconds ?? OTPService.otpValiditySeconds),
        );

        state = state.copyWith(
          isLoading: false,
          sentAt: DateTime.now(),
          expiresAt: expiresAt,
          sendAttempts: state.sendAttempts + 1,
          verifyAttempts: 0, // Reset verify attempts on resend
          cooldownSeconds: response.cooldownSeconds ?? OTPService.defaultCooldownSeconds,
          clearError: true,
        );

        _startCooldownTimer();
        _startExpiryTimer();

        return true;
      },
      failure: (message, statusCode) {
        state = state.copyWith(
          isLoading: false,
          error: message,
        );
        return false;
      },
    );
  }

  /// Verify OTP code
  Future<bool> verifyOTP(String otp) async {
    if (state.isLoading || state.isLocked || state.isExpired) return false;

    state = state.copyWith(isLoading: true, clearError: true);

    final result = await _otpService.verifyOTP(
      identifier: state.identifier,
      otp: otp,
      purpose: state.purpose,
    );

    return result.when(
      success: (response) {
        state = state.copyWith(
          isLoading: false,
          isVerified: true,
          resetToken: response.resetToken,
          clearError: true,
        );

        // Cancel timers on successful verification
        _cooldownTimer?.cancel();
        _expiryTimer?.cancel();

        return true;
      },
      failure: (message, statusCode) {
        state = state.copyWith(
          isLoading: false,
          error: message,
          verifyAttempts: state.verifyAttempts + 1,
        );
        return false;
      },
    );
  }

  /// Change delivery channel
  void changeChannel(OTPChannel newChannel) {
    if (state.channel != newChannel) {
      state = state.copyWith(
        channel: newChannel,
        sendAttempts: 0,
        verifyAttempts: 0,
        clearError: true,
        clearResetToken: true,
      );
    }
  }

  /// Clear error state
  void clearError() {
    state = state.copyWith(clearError: true);
  }

  /// Start cooldown countdown timer
  void _startCooldownTimer() {
    _cooldownTimer?.cancel();
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (state.cooldownSeconds <= 0) {
        timer.cancel();
      } else {
        state = state.copyWith(cooldownSeconds: state.cooldownSeconds - 1);
      }
    });
  }

  /// Start OTP expiry countdown timer
  void _startExpiryTimer() {
    _expiryTimer?.cancel();
    if (state.expiresAt == null) return;

    final duration = state.expiresAt!.difference(DateTime.now());
    if (duration.isNegative) return;

    _expiryTimer = Timer(duration, () {
      // Trigger state update to reflect expiry
      state = state.copyWith(error: 'انتهت صلاحية رمز التحقق');
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Convenience Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider to check if reset token exists
final hasValidResetTokenProvider = FutureProvider<bool>((ref) async {
  final otpService = ref.watch(otpServiceProvider);
  return otpService.hasValidResetToken();
});

/// Provider to get stored reset token
final resetTokenProvider = FutureProvider<String?>((ref) async {
  final otpService = ref.watch(otpServiceProvider);
  return otpService.getResetToken();
});
