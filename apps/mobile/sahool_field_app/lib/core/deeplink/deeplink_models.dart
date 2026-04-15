library;

/// SAHOOL Deep Link Models
/// نماذج الروابط العميقة
///
/// Data models, enums, and helper functions for deep links.
/// Separated from handler to allow testing without platform dependencies.

import 'package:flutter/foundation.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

/// Custom URI scheme for the SAHOOL app
const String kSahoolScheme = 'sahool';

/// Universal link hosts for iOS and Android
const List<String> kUniversalLinkHosts = [
  'sahool.app',
  'www.sahool.app',
  'app.sahool.app',
];

/// Deep link paths
class DeepLinkPaths {
  DeepLinkPaths._();

  /// Password reset path
  static const String resetPassword = '/reset-password';

  /// OTP verification path
  static const String verifyOtp = '/verify-otp';

  /// Email verification path
  static const String verifyEmail = '/verify-email';

  /// Account activation path
  static const String activateAccount = '/activate-account';

  /// Field details path
  static const String fieldDetails = '/field';

  /// Notification path
  static const String notification = '/notification';

  /// Invite path
  static const String invite = '/invite';
}

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Types
// ═══════════════════════════════════════════════════════════════════════════

/// Enum representing different types of deep links
enum DeepLinkType {
  /// Password reset deep link
  resetPassword,

  /// OTP verification deep link
  verifyOtp,

  /// Email verification deep link
  verifyEmail,

  /// Account activation deep link
  activateAccount,

  /// Field details deep link
  fieldDetails,

  /// Notification deep link
  notification,

  /// Invite/referral deep link
  invite,

  /// Unknown or unsupported deep link
  unknown,
}

/// Extension for DeepLinkType to get display names
extension DeepLinkTypeExtension on DeepLinkType {
  /// Arabic display name
  String get displayNameAr {
    switch (this) {
      case DeepLinkType.resetPassword:
        return 'إعادة تعيين كلمة المرور';
      case DeepLinkType.verifyOtp:
        return 'التحقق من الرمز';
      case DeepLinkType.verifyEmail:
        return 'التحقق من البريد الإلكتروني';
      case DeepLinkType.activateAccount:
        return 'تفعيل الحساب';
      case DeepLinkType.fieldDetails:
        return 'تفاصيل الحقل';
      case DeepLinkType.notification:
        return 'إشعار';
      case DeepLinkType.invite:
        return 'دعوة';
      case DeepLinkType.unknown:
        return 'رابط غير معروف';
    }
  }

  /// English display name
  String get displayNameEn {
    switch (this) {
      case DeepLinkType.resetPassword:
        return 'Reset Password';
      case DeepLinkType.verifyOtp:
        return 'Verify OTP';
      case DeepLinkType.verifyEmail:
        return 'Verify Email';
      case DeepLinkType.activateAccount:
        return 'Activate Account';
      case DeepLinkType.fieldDetails:
        return 'Field Details';
      case DeepLinkType.notification:
        return 'Notification';
      case DeepLinkType.invite:
        return 'Invitation';
      case DeepLinkType.unknown:
        return 'Unknown Link';
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Data Models
// ═══════════════════════════════════════════════════════════════════════════

/// Parsed deep link data
@immutable
class DeepLinkData {
  /// The type of deep link
  final DeepLinkType type;

  /// The original URI
  final Uri uri;

  /// Query parameters from the link
  final Map<String, String> parameters;

  /// Timestamp when the link was received
  final DateTime receivedAt;

  const DeepLinkData({
    required this.type,
    required this.uri,
    required this.parameters,
    required this.receivedAt,
  });

  /// Get a parameter value by key
  String? getParameter(String key) => parameters[key];

  /// Check if a parameter exists
  bool hasParameter(String key) => parameters.containsKey(key);

  @override
  String toString() {
    return 'DeepLinkData(type: $type, uri: $uri, parameters: $parameters)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is DeepLinkData &&
        other.type == type &&
        other.uri == uri &&
        mapEquals(other.parameters, parameters);
  }

  @override
  int get hashCode => Object.hash(type, uri, parameters);
}

/// Password reset deep link data
@immutable
class PasswordResetLinkData extends DeepLinkData {
  /// The reset token
  final String token;

  /// Optional email address
  final String? email;

  PasswordResetLinkData({
    required super.uri,
    required this.token,
    this.email,
    required super.receivedAt,
  }) : super(
          type: DeepLinkType.resetPassword,
          parameters: {
            'token': token,
            if (email != null) 'email': email,
          },
        );

  /// Check if the token is expired (tokens expire after 1 hour typically)
  bool get isExpired {
    const expirationDuration = Duration(hours: 1);
    return DateTime.now().difference(receivedAt) > expirationDuration;
  }
}

/// OTP verification deep link data
@immutable
class OtpVerificationLinkData extends DeepLinkData {
  /// The identifier (email or phone)
  final String identifier;

  /// The purpose of OTP verification
  final OtpPurpose purpose;

  /// Optional pre-filled OTP code
  final String? otp;

  /// Session ID for tracking
  final String? sessionId;

  OtpVerificationLinkData({
    required super.uri,
    required this.identifier,
    required this.purpose,
    this.otp,
    this.sessionId,
    required super.receivedAt,
  }) : super(
          type: DeepLinkType.verifyOtp,
          parameters: {
            'identifier': identifier,
            'purpose': purpose.name,
            if (otp != null) 'otp': otp,
            if (sessionId != null) 'session_id': sessionId,
          },
        );
}

/// OTP verification purposes
enum OtpPurpose {
  /// Password reset verification
  passwordReset,

  /// Phone number verification
  phoneVerification,

  /// Email verification
  emailVerification,

  /// Two-factor authentication
  twoFactorAuth,

  /// Account activation
  accountActivation,

  /// Transaction verification
  transactionVerification,

  /// Unknown purpose
  unknown,
}

/// Extension for OtpPurpose
extension OtpPurposeExtension on OtpPurpose {
  /// Create from string
  static OtpPurpose fromString(String? value) {
    if (value == null) return OtpPurpose.unknown;

    switch (value.toLowerCase()) {
      case 'password_reset':
      case 'passwordreset':
      case 'reset_password':
        return OtpPurpose.passwordReset;
      case 'phone_verification':
      case 'phoneverification':
      case 'verify_phone':
        return OtpPurpose.phoneVerification;
      case 'email_verification':
      case 'emailverification':
      case 'verify_email':
        return OtpPurpose.emailVerification;
      case 'two_factor_auth':
      case 'twofactorauth':
      case '2fa':
        return OtpPurpose.twoFactorAuth;
      case 'account_activation':
      case 'accountactivation':
      case 'activate_account':
        return OtpPurpose.accountActivation;
      case 'transaction_verification':
      case 'transactionverification':
      case 'verify_transaction':
        return OtpPurpose.transactionVerification;
      default:
        return OtpPurpose.unknown;
    }
  }

  /// Arabic display name
  String get displayNameAr {
    switch (this) {
      case OtpPurpose.passwordReset:
        return 'إعادة تعيين كلمة المرور';
      case OtpPurpose.phoneVerification:
        return 'التحقق من رقم الهاتف';
      case OtpPurpose.emailVerification:
        return 'التحقق من البريد الإلكتروني';
      case OtpPurpose.twoFactorAuth:
        return 'المصادقة الثنائية';
      case OtpPurpose.accountActivation:
        return 'تفعيل الحساب';
      case OtpPurpose.transactionVerification:
        return 'التحقق من المعاملة';
      case OtpPurpose.unknown:
        return 'غير معروف';
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link State
// ═══════════════════════════════════════════════════════════════════════════

/// State for the deep link handler
@immutable
class DeepLinkState {
  /// The current deep link data (null if no pending link)
  final DeepLinkData? currentLink;

  /// Whether the handler is initialized
  final bool isInitialized;

  /// Whether there's a pending link waiting to be handled
  final bool hasPendingLink;

  /// Error message if link parsing failed
  final String? error;

  /// History of handled deep links (for debugging)
  final List<DeepLinkData> linkHistory;

  const DeepLinkState({
    this.currentLink,
    this.isInitialized = false,
    this.hasPendingLink = false,
    this.error,
    this.linkHistory = const [],
  });

  DeepLinkState copyWith({
    DeepLinkData? currentLink,
    bool? isInitialized,
    bool? hasPendingLink,
    String? error,
    List<DeepLinkData>? linkHistory,
    bool clearCurrentLink = false,
    bool clearError = false,
  }) {
    return DeepLinkState(
      currentLink: clearCurrentLink ? null : (currentLink ?? this.currentLink),
      isInitialized: isInitialized ?? this.isInitialized,
      hasPendingLink: hasPendingLink ?? this.hasPendingLink,
      error: clearError ? null : (error ?? this.error),
      linkHistory: linkHistory ?? this.linkHistory,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/// Build a password reset deep link URL
String buildPasswordResetLink({
  required String token,
  String? email,
  bool useUniversalLink = true,
}) {
  final params = <String, String>{
    'token': token,
    if (email != null) 'email': email,
  };

  if (useUniversalLink) {
    return Uri.https(
      kUniversalLinkHosts.first,
      DeepLinkPaths.resetPassword,
      params,
    ).toString();
  }

  return Uri(
    scheme: kSahoolScheme,
    host: '',
    path: DeepLinkPaths.resetPassword,
    queryParameters: params,
  ).toString();
}

/// Build an OTP verification deep link URL
String buildOtpVerificationLink({
  required String identifier,
  required OtpPurpose purpose,
  String? otp,
  String? sessionId,
  bool useUniversalLink = true,
}) {
  final params = <String, String>{
    'identifier': identifier,
    'purpose': purpose.name,
    if (otp != null) 'otp': otp,
    if (sessionId != null) 'session_id': sessionId,
  };

  if (useUniversalLink) {
    return Uri.https(
      kUniversalLinkHosts.first,
      DeepLinkPaths.verifyOtp,
      params,
    ).toString();
  }

  return Uri(
    scheme: kSahoolScheme,
    host: '',
    path: DeepLinkPaths.verifyOtp,
    queryParameters: params,
  ).toString();
}

/// Validate a deep link token format (basic validation)
bool isValidTokenFormat(String token) {
  if (token.length < 32) return false;

  final validPattern = RegExp(r'^[a-zA-Z0-9\-_]+$');
  return validPattern.hasMatch(token);
}

/// Extract field ID from a deep link path
String? extractFieldIdFromPath(String path) {
  final pattern = RegExp(r'/fields?/([a-zA-Z0-9\-_]+)');
  final match = pattern.firstMatch(path);
  return match?.group(1);
}
