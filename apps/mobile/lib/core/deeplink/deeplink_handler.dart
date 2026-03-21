/// SAHOOL Deep Link Handler
/// معالج الروابط العميقة
///
/// Handles deep links for the SAHOOL app including field navigation,
/// weather, NDVI, tasks, alerts, and authentication flows.
///
/// Supports both custom URI scheme (sahool://) and universal links (https://sahool.app/).
///
/// Features:
/// - Cold start deep link handling (app launched via deep link)
/// - Warm start deep link handling (app already running)
/// - Authentication-required deep links with login redirect
/// - Invalid deep link parameter validation
/// - Riverpod integration for state management
/// - Full lifecycle management
///
/// Supported Deep Links:
/// - sahool://field/{fieldId} - Open specific field
/// - sahool://weather - Open weather screen
/// - sahool://ndvi/{fieldId} - Open NDVI for field
/// - sahool://task/{taskId} - Open specific task
/// - sahool://alert/{alertId} - Open alert details
/// - sahool://reset-password?token=xxx - Password reset
/// - sahool://verify-otp?identifier=xxx&purpose=xxx - OTP verification
library;

import 'dart:async';

import 'package:app_links/app_links.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../services/auth_service.dart';
import '../utils/app_logger.dart';
import 'deeplink_routes.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Re-export route constants for convenience
// ═══════════════════════════════════════════════════════════════════════════

/// Custom URI scheme for the SAHOOL app
const String kSahoolScheme = DeepLinkRoutes.scheme;

/// Universal link hosts for iOS and Android
const List<String> kUniversalLinkHosts = DeepLinkRoutes.universalLinkHosts;

/// Deep link paths (legacy compatibility)
class DeepLinkPaths {
  DeepLinkPaths._();

  static const String resetPassword = '/reset-password';
  static const String verifyOtp = '/verify-otp';
  static const String verifyEmail = '/verify-email';
  static const String activateAccount = '/activate-account';
  static const String fieldDetails = '/field';
  static const String notification = '/notification';
  static const String invite = '/invite';

  // New paths
  static const String weather = '/weather';
  static const String ndvi = '/ndvi';
  static const String task = '/task';
  static const String alert = '/alert';
  static const String tasks = '/tasks';
  static const String alerts = '/alerts';
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

  /// Weather screen deep link
  weather,

  /// NDVI analysis deep link
  ndvi,

  /// Task details deep link
  task,

  /// Alert details deep link
  alert,

  /// Tasks list deep link
  tasks,

  /// Alerts list deep link
  alerts,

  /// Unknown or unsupported deep link
  unknown,
}

/// Extension for DeepLinkType to get display names and auth requirements
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
      case DeepLinkType.weather:
        return 'الطقس';
      case DeepLinkType.ndvi:
        return 'تحليل NDVI';
      case DeepLinkType.task:
        return 'تفاصيل المهمة';
      case DeepLinkType.alert:
        return 'تفاصيل التنبيه';
      case DeepLinkType.tasks:
        return 'قائمة المهام';
      case DeepLinkType.alerts:
        return 'التنبيهات';
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
      case DeepLinkType.weather:
        return 'Weather';
      case DeepLinkType.ndvi:
        return 'NDVI Analysis';
      case DeepLinkType.task:
        return 'Task Details';
      case DeepLinkType.alert:
        return 'Alert Details';
      case DeepLinkType.tasks:
        return 'Tasks List';
      case DeepLinkType.alerts:
        return 'Alerts';
      case DeepLinkType.unknown:
        return 'Unknown Link';
    }
  }

  /// Whether this deep link type requires authentication
  bool get requiresAuth {
    switch (this) {
      case DeepLinkType.resetPassword:
      case DeepLinkType.verifyOtp:
      case DeepLinkType.verifyEmail:
      case DeepLinkType.activateAccount:
      case DeepLinkType.invite:
      case DeepLinkType.weather:
        return false;
      case DeepLinkType.fieldDetails:
      case DeepLinkType.notification:
      case DeepLinkType.ndvi:
      case DeepLinkType.task:
      case DeepLinkType.alert:
      case DeepLinkType.tasks:
      case DeepLinkType.alerts:
      case DeepLinkType.unknown:
        return true;
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

  /// Path parameters extracted from the URL
  final Map<String, String> pathParameters;

  /// Timestamp when the link was received
  final DateTime receivedAt;

  /// Whether this is from a cold start (app was not running)
  final bool isColdStart;

  const DeepLinkData({
    required this.type,
    required this.uri,
    required this.parameters,
    this.pathParameters = const {},
    required this.receivedAt,
    this.isColdStart = false,
  });

  /// Get a parameter value by key (checks both query and path params)
  String? getParameter(String key) =>
      parameters[key] ?? pathParameters[key];

  /// Check if a parameter exists
  bool hasParameter(String key) =>
      parameters.containsKey(key) || pathParameters.containsKey(key);

  /// Whether this link requires authentication
  bool get requiresAuth => type.requiresAuth;

  /// Get all parameters combined
  Map<String, String> get allParameters => {...pathParameters, ...parameters};

  @override
  String toString() {
    return 'DeepLinkData(type: $type, uri: $uri, parameters: $parameters, pathParameters: $pathParameters, isColdStart: $isColdStart)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is DeepLinkData &&
        other.type == type &&
        other.uri == uri &&
        mapEquals(other.parameters, parameters) &&
        mapEquals(other.pathParameters, pathParameters);
  }

  @override
  int get hashCode => Object.hash(type, uri, parameters, pathParameters);
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
    super.isColdStart,
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
    super.isColdStart,
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
  passwordReset,
  phoneVerification,
  emailVerification,
  twoFactorAuth,
  accountActivation,
  transactionVerification,
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
// Deep Link Handler State
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

  /// Pending link that requires authentication
  final DeepLinkData? pendingAuthLink;

  /// Error message if link parsing failed
  final String? error;

  /// Error message in Arabic
  final String? errorAr;

  /// History of handled deep links (for debugging)
  final List<DeepLinkData> linkHistory;

  const DeepLinkState({
    this.currentLink,
    this.isInitialized = false,
    this.hasPendingLink = false,
    this.pendingAuthLink,
    this.error,
    this.errorAr,
    this.linkHistory = const [],
  });

  DeepLinkState copyWith({
    DeepLinkData? currentLink,
    bool? isInitialized,
    bool? hasPendingLink,
    DeepLinkData? pendingAuthLink,
    String? error,
    String? errorAr,
    List<DeepLinkData>? linkHistory,
    bool clearCurrentLink = false,
    bool clearError = false,
    bool clearPendingAuthLink = false,
  }) {
    return DeepLinkState(
      currentLink: clearCurrentLink ? null : (currentLink ?? this.currentLink),
      isInitialized: isInitialized ?? this.isInitialized,
      hasPendingLink: hasPendingLink ?? this.hasPendingLink,
      pendingAuthLink: clearPendingAuthLink
          ? null
          : (pendingAuthLink ?? this.pendingAuthLink),
      error: clearError ? null : (error ?? this.error),
      errorAr: clearError ? null : (errorAr ?? this.errorAr),
      linkHistory: linkHistory ?? this.linkHistory,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Handler Notifier
// ═══════════════════════════════════════════════════════════════════════════

/// Riverpod notifier for managing deep link state
class DeepLinkNotifier extends StateNotifier<DeepLinkState> {
  final AppLinks _appLinks;
  StreamSubscription<Uri>? _linkSubscription;
  final GlobalKey<NavigatorState>? _navigatorKey;
  GoRouter? _router;
  final Ref _ref;

  DeepLinkNotifier({
    required Ref ref,
    GlobalKey<NavigatorState>? navigatorKey,
    GoRouter? router,
  })  : _appLinks = AppLinks(),
        _navigatorKey = navigatorKey,
        _router = router,
        _ref = ref,
        super(const DeepLinkState());

  /// Initialize the deep link handler
  Future<void> initialize() async {
    if (state.isInitialized) {
      AppLogger.w('Deep link handler already initialized', tag: 'DEEPLINK');
      return;
    }

    AppLogger.i('Initializing deep link handler...', tag: 'DEEPLINK');

    try {
      // Check for initial link (app opened via deep link - cold start)
      final initialLink = await _appLinks.getInitialLinkString();
      if (initialLink != null) {
        AppLogger.i(
          'Initial deep link found (cold start): $initialLink',
          tag: 'DEEPLINK',
        );
        _handleLinkString(initialLink, isInitial: true, isColdStart: true);
      }

      // Listen for incoming links while app is running (warm start)
      _linkSubscription = _appLinks.uriLinkStream.listen(
        (uri) => _handleUri(uri, isColdStart: false),
        onError: (Object error) {
          AppLogger.e(
            'Deep link stream error',
            tag: 'DEEPLINK',
            error: error,
          );
          state = state.copyWith(
            error: 'Failed to listen for deep links: $error',
            errorAr: 'فشل في الاستماع للروابط العميقة: $error',
          );
        },
      );

      state = state.copyWith(isInitialized: true);
      AppLogger.i('Deep link handler initialized successfully', tag: 'DEEPLINK');
    } catch (e, stackTrace) {
      AppLogger.e(
        'Failed to initialize deep link handler',
        tag: 'DEEPLINK',
        error: e,
        stackTrace: stackTrace,
      );
      state = state.copyWith(
        error: 'Initialization failed: $e',
        errorAr: 'فشل التهيئة: $e',
      );
    }
  }

  /// Set the router for navigation
  void setRouter(GoRouter router) {
    _router = router;
    AppLogger.d('Router set for deep link handler', tag: 'DEEPLINK');

    // Check if there's a pending auth link to handle after login
    _checkPendingAuthLink();
  }

  /// Check and handle pending auth link after user logs in
  void _checkPendingAuthLink() {
    if (state.pendingAuthLink != null) {
      try {
        final isLoggedIn = _ref.read(isLoggedInProvider);
        if (isLoggedIn) {
          AppLogger.i(
            'User logged in, handling pending auth link',
            tag: 'DEEPLINK',
          );
          _processUri(state.pendingAuthLink!.uri, isInitial: false);
          state = state.copyWith(clearPendingAuthLink: true);
        }
      } catch (_) {
        // Auth provider not available yet
      }
    }
  }

  /// Handle a URI link
  void _handleUri(Uri uri, {bool isColdStart = false}) {
    AppLogger.i(
      'Received deep link: $uri (coldStart: $isColdStart)',
      tag: 'DEEPLINK',
    );
    _processUri(uri, isInitial: false, isColdStart: isColdStart);
  }

  /// Handle a link string
  void _handleLinkString(
    String linkString, {
    bool isInitial = false,
    bool isColdStart = false,
  }) {
    try {
      final uri = Uri.parse(linkString);
      _processUri(uri, isInitial: isInitial, isColdStart: isColdStart);
    } catch (e) {
      AppLogger.e(
        'Failed to parse deep link string',
        tag: 'DEEPLINK',
        error: e,
        data: {'link': linkString},
      );
      state = state.copyWith(
        error: 'Invalid link format: $linkString',
        errorAr: 'تنسيق الرابط غير صالح: $linkString',
      );
    }
  }

  /// Process a URI and update state
  void _processUri(
    Uri uri, {
    bool isInitial = false,
    bool isColdStart = false,
  }) {
    // Use the new parser for validation
    final parseResult = DeepLinkParser.parse(uri);

    if (!parseResult.isValid) {
      AppLogger.w(
        'Invalid deep link: ${parseResult.errorMessage}',
        tag: 'DEEPLINK',
        data: {'uri': uri.toString()},
      );
      state = state.copyWith(
        error: parseResult.errorMessage,
        errorAr: parseResult.errorMessageAr,
      );
      return;
    }

    // Parse into DeepLinkData
    final deepLinkData = _parseUri(uri, isColdStart: isColdStart);

    if (deepLinkData == null) {
      AppLogger.w('Unsupported deep link: $uri', tag: 'DEEPLINK');
      state = state.copyWith(
        error: 'Unsupported link: $uri',
        errorAr: 'رابط غير مدعوم: $uri',
      );
      return;
    }

    // Check authentication requirement
    if (deepLinkData.requiresAuth) {
      try {
        final isLoggedIn = _ref.read(isLoggedInProvider);
        if (!isLoggedIn) {
          AppLogger.i(
            'Deep link requires auth, storing for later',
            tag: 'DEEPLINK',
            data: {'type': deepLinkData.type.name},
          );

          state = state.copyWith(
            pendingAuthLink: deepLinkData,
            hasPendingLink: false,
          );

          // Redirect to login
          _navigateToLogin(deepLinkData);
          return;
        }
      } catch (_) {
        // Auth provider not available, store link for later
        state = state.copyWith(pendingAuthLink: deepLinkData);
        return;
      }
    }

    // Add to history
    final newHistory = [...state.linkHistory, deepLinkData];
    if (newHistory.length > 50) {
      newHistory.removeRange(0, newHistory.length - 50);
    }

    state = state.copyWith(
      currentLink: deepLinkData,
      hasPendingLink: true,
      linkHistory: newHistory,
      clearError: true,
    );

    AppLogger.i(
      'Deep link parsed successfully',
      tag: 'DEEPLINK',
      data: {
        'type': deepLinkData.type.name,
        'isInitial': isInitial,
        'isColdStart': isColdStart,
        'requiresAuth': deepLinkData.requiresAuth,
      },
    );
  }

  /// Navigate to login screen with redirect info
  void _navigateToLogin(DeepLinkData pendingLink) {
    if (_router != null) {
      _router!.go('/login', extra: {
        'redirect': pendingLink.uri.toString(),
        'redirectType': pendingLink.type.name,
      });
      AppLogger.i('Redirected to login for auth-required link', tag: 'DEEPLINK');
    }
  }

  /// Parse a URI into DeepLinkData
  DeepLinkData? _parseUri(Uri uri, {bool isColdStart = false}) {
    // Check if it's a valid SAHOOL link
    if (!_isValidSahoolLink(uri)) {
      return null;
    }

    final path = _extractPath(uri).toLowerCase();
    final queryParams = uri.queryParameters;
    final receivedAt = DateTime.now();

    // Extract path parameters using regex patterns
    final pathParams = _extractPathParams(path);

    // Determine link type based on path
    final type = _determineType(path);

    // Create specialized data objects for certain types
    if (type == DeepLinkType.resetPassword) {
      return _parsePasswordResetLink(
        uri,
        queryParams,
        receivedAt,
        isColdStart,
      );
    }

    if (type == DeepLinkType.verifyOtp) {
      return _parseOtpVerificationLink(
        uri,
        queryParams,
        receivedAt,
        isColdStart,
      );
    }

    // Generic DeepLinkData for other types
    return DeepLinkData(
      type: type,
      uri: uri,
      parameters: queryParams,
      pathParameters: pathParams,
      receivedAt: receivedAt,
      isColdStart: isColdStart,
    );
  }

  /// Extract path from URI
  String _extractPath(Uri uri) {
    if (uri.scheme == kSahoolScheme) {
      // For custom scheme: sahool://field/123 -> /field/123
      if (uri.host.isNotEmpty) {
        return '/${uri.host}${uri.path}';
      }
      return uri.path;
    }
    return uri.path;
  }

  /// Extract path parameters from URL
  Map<String, String> _extractPathParams(String path) {
    final params = <String, String>{};

    // Field: /field/{fieldId}
    final fieldMatch = RegExp(r'/field/([a-zA-Z0-9\-_]+)').firstMatch(path);
    if (fieldMatch != null) {
      params['fieldId'] = fieldMatch.group(1)!;
      params['id'] = fieldMatch.group(1)!;
    }

    // NDVI: /ndvi/{fieldId}
    final ndviMatch = RegExp(r'/ndvi/([a-zA-Z0-9\-_]+)').firstMatch(path);
    if (ndviMatch != null) {
      params['fieldId'] = ndviMatch.group(1)!;
    }

    // Task: /task/{taskId}
    final taskMatch = RegExp(r'/task/([a-zA-Z0-9\-_]+)').firstMatch(path);
    if (taskMatch != null) {
      params['taskId'] = taskMatch.group(1)!;
      params['id'] = taskMatch.group(1)!;
    }

    // Alert: /alert/{alertId}
    final alertMatch = RegExp(r'/alert/([a-zA-Z0-9\-_]+)').firstMatch(path);
    if (alertMatch != null) {
      params['alertId'] = alertMatch.group(1)!;
      params['id'] = alertMatch.group(1)!;
    }

    return params;
  }

  /// Determine the DeepLinkType from path
  DeepLinkType _determineType(String path) {
    // Check specific patterns first
    if (RegExp(r'^/field/[a-zA-Z0-9\-_]+$').hasMatch(path)) {
      return DeepLinkType.fieldDetails;
    }
    if (RegExp(r'^/ndvi/[a-zA-Z0-9\-_]+$').hasMatch(path)) {
      return DeepLinkType.ndvi;
    }
    if (RegExp(r'^/task/[a-zA-Z0-9\-_]+$').hasMatch(path)) {
      return DeepLinkType.task;
    }
    if (RegExp(r'^/alert/[a-zA-Z0-9\-_]+$').hasMatch(path)) {
      return DeepLinkType.alert;
    }

    // Check base paths
    if (path == '/weather' || path.startsWith('/weather')) {
      return DeepLinkType.weather;
    }
    if (path == '/tasks' || path.startsWith('/tasks')) {
      return DeepLinkType.tasks;
    }
    if (path == '/alerts' || path.startsWith('/alerts')) {
      return DeepLinkType.alerts;
    }
    if (path == '/reset-password' || path.endsWith('/reset-password')) {
      return DeepLinkType.resetPassword;
    }
    if (path == '/verify-otp' || path.endsWith('/verify-otp')) {
      return DeepLinkType.verifyOtp;
    }
    if (path == '/verify-email' || path.endsWith('/verify-email')) {
      return DeepLinkType.verifyEmail;
    }
    if (path == '/activate-account' || path.endsWith('/activate-account')) {
      return DeepLinkType.activateAccount;
    }
    if (path.contains('/notification')) {
      return DeepLinkType.notification;
    }
    if (path == '/invite' || path.endsWith('/invite')) {
      return DeepLinkType.invite;
    }

    return DeepLinkType.unknown;
  }

  /// Check if the URI is a valid SAHOOL link
  bool _isValidSahoolLink(Uri uri) {
    // Check custom scheme
    if (uri.scheme == kSahoolScheme) {
      return true;
    }

    // Check universal link hosts
    if (uri.scheme == 'https' || uri.scheme == 'http') {
      final host = uri.host.toLowerCase();
      return kUniversalLinkHosts.any((h) => host == h || host.endsWith('.$h'));
    }

    return false;
  }

  /// Parse password reset link
  PasswordResetLinkData? _parsePasswordResetLink(
    Uri uri,
    Map<String, String> params,
    DateTime receivedAt,
    bool isColdStart,
  ) {
    final token = params['token'];
    if (token == null || token.isEmpty) {
      AppLogger.w(
        'Password reset link missing token',
        tag: 'DEEPLINK',
        data: {'uri': uri.toString()},
      );
      return null;
    }

    return PasswordResetLinkData(
      uri: uri,
      token: token,
      email: params['email'],
      receivedAt: receivedAt,
      isColdStart: isColdStart,
    );
  }

  /// Parse OTP verification link
  OtpVerificationLinkData? _parseOtpVerificationLink(
    Uri uri,
    Map<String, String> params,
    DateTime receivedAt,
    bool isColdStart,
  ) {
    final identifier = params['identifier'];
    if (identifier == null || identifier.isEmpty) {
      AppLogger.w(
        'OTP verification link missing identifier',
        tag: 'DEEPLINK',
        data: {'uri': uri.toString()},
      );
      return null;
    }

    final purposeString = params['purpose'];
    final purpose = OtpPurposeExtension.fromString(purposeString);

    return OtpVerificationLinkData(
      uri: uri,
      identifier: identifier,
      purpose: purpose,
      otp: params['otp'] ?? params['code'],
      sessionId: params['session_id'] ?? params['sid'],
      receivedAt: receivedAt,
      isColdStart: isColdStart,
    );
  }

  /// Navigate to the appropriate screen for the current deep link
  Future<bool> handleCurrentLink(BuildContext context) async {
    final link = state.currentLink;
    if (link == null) {
      AppLogger.d('No pending deep link to handle', tag: 'DEEPLINK');
      return false;
    }

    final success = await _navigateForLink(link, context);

    if (success) {
      // Clear the pending link
      state = state.copyWith(
        hasPendingLink: false,
        clearCurrentLink: true,
      );
    }

    return success;
  }

  /// Handle pending auth link after successful login
  Future<bool> handlePendingAuthLink(BuildContext context) async {
    final link = state.pendingAuthLink;
    if (link == null) {
      return false;
    }

    AppLogger.i(
      'Handling pending auth link after login',
      tag: 'DEEPLINK',
      data: {'type': link.type.name},
    );

    final success = await _navigateForLink(link, context);

    if (success) {
      state = state.copyWith(clearPendingAuthLink: true);
    }

    return success;
  }

  /// Navigate to the appropriate screen for a deep link
  Future<bool> _navigateForLink(
    DeepLinkData link,
    BuildContext context,
  ) async {
    AppLogger.i(
      'Handling deep link navigation',
      tag: 'DEEPLINK',
      data: {'type': link.type.name},
    );

    try {
      switch (link.type) {
        case DeepLinkType.resetPassword:
          return await _handlePasswordResetNavigation(link, context);

        case DeepLinkType.verifyOtp:
          return await _handleOtpVerificationNavigation(link, context);

        case DeepLinkType.verifyEmail:
          return _navigateToPath(
            '/verify-email',
            extra: link.parameters,
          );

        case DeepLinkType.activateAccount:
          return _navigateToPath(
            '/activate-account',
            extra: link.parameters,
          );

        case DeepLinkType.fieldDetails:
          final fieldId =
              link.pathParameters['fieldId'] ?? link.parameters['id'];
          if (fieldId != null) {
            return _navigateToPath('/field/$fieldId');
          }
          return false;

        case DeepLinkType.weather:
          final fieldId = link.parameters['fieldId'];
          return _navigateToPath(
            '/weather',
            extra: fieldId != null ? {'fieldId': fieldId} : null,
          );

        case DeepLinkType.ndvi:
          final fieldId = link.pathParameters['fieldId'];
          if (fieldId != null) {
            return _navigateToPath('/satellite/$fieldId');
          }
          return _navigateToPath('/satellite');

        case DeepLinkType.task:
          final taskId =
              link.pathParameters['taskId'] ?? link.parameters['id'];
          if (taskId != null) {
            return _navigateToPath('/task/$taskId');
          }
          return _navigateToPath('/tasks');

        case DeepLinkType.tasks:
          final fieldId = link.parameters['fieldId'];
          return _navigateToPath(
            '/tasks',
            extra: fieldId != null ? {'fieldId': fieldId} : null,
          );

        case DeepLinkType.alert:
          final alertId =
              link.pathParameters['alertId'] ?? link.parameters['id'];
          if (alertId != null) {
            return _navigateToPath(
              '/alerts',
              extra: {'alertId': alertId},
            );
          }
          return _navigateToPath('/alerts');

        case DeepLinkType.alerts:
          return _navigateToPath('/alerts');

        case DeepLinkType.notification:
          final notificationId =
              link.parameters['id'] ?? link.parameters['notification_id'];
          return _navigateToPath(
            '/notifications',
            extra: {'notificationId': notificationId},
          );

        case DeepLinkType.invite:
          return _navigateToPath(
            '/invite',
            extra: link.parameters,
          );

        case DeepLinkType.unknown:
          AppLogger.w(
            'Attempted to handle unknown deep link type',
            tag: 'DEEPLINK',
          );
          return false;
      }
    } catch (e, stackTrace) {
      AppLogger.e(
        'Deep link navigation failed',
        tag: 'DEEPLINK',
        error: e,
        stackTrace: stackTrace,
      );
      return false;
    }
  }

  /// Handle password reset navigation
  Future<bool> _handlePasswordResetNavigation(
    DeepLinkData link,
    BuildContext context,
  ) async {
    if (link is PasswordResetLinkData) {
      if (link.isExpired) {
        AppLogger.w('Password reset token may be expired', tag: 'DEEPLINK');
      }

      return _navigateToPath(
        '/reset-password',
        extra: {
          'token': link.token,
          'email': link.email,
        },
      );
    }

    final token = link.parameters['token'];
    if (token == null) {
      AppLogger.e('Password reset link missing token', tag: 'DEEPLINK');
      return false;
    }

    return _navigateToPath(
      '/reset-password',
      extra: link.parameters,
    );
  }

  /// Handle OTP verification navigation
  Future<bool> _handleOtpVerificationNavigation(
    DeepLinkData link,
    BuildContext context,
  ) async {
    if (link is OtpVerificationLinkData) {
      return _navigateToPath(
        '/verify-otp',
        extra: {
          'identifier': link.identifier,
          'purpose': link.purpose.name,
          'otp': link.otp,
          'sessionId': link.sessionId,
        },
      );
    }

    return _navigateToPath(
      '/verify-otp',
      extra: link.parameters,
    );
  }

  /// Navigate to a path using GoRouter or Navigator
  bool _navigateToPath(String path, {Map<String, dynamic>? extra}) {
    if (_router != null) {
      _router!.go(path, extra: extra);
      AppLogger.i('Navigated via GoRouter to: $path', tag: 'DEEPLINK');
      return true;
    }

    if (_navigatorKey?.currentState != null) {
      _navigatorKey!.currentState!.pushNamed(path, arguments: extra);
      AppLogger.i('Navigated via Navigator to: $path', tag: 'DEEPLINK');
      return true;
    }

    AppLogger.e('No navigation method available', tag: 'DEEPLINK');
    return false;
  }

  /// Manually process a deep link string
  void processLink(String linkString) {
    _handleLinkString(linkString, isInitial: false, isColdStart: false);
  }

  /// Manually process a URI
  void processUri(Uri uri) {
    _processUri(uri, isInitial: false, isColdStart: false);
  }

  /// Clear the current pending link
  void clearPendingLink() {
    state = state.copyWith(
      hasPendingLink: false,
      clearCurrentLink: true,
    );
  }

  /// Clear pending auth link
  void clearPendingAuthLink() {
    state = state.copyWith(clearPendingAuthLink: true);
  }

  /// Clear any errors
  void clearError() {
    state = state.copyWith(clearError: true);
  }

  /// Get link history (for debugging)
  List<DeepLinkData> getLinkHistory() {
    return List.unmodifiable(state.linkHistory);
  }

  @override
  void dispose() {
    _linkSubscription?.cancel();
    super.dispose();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for the GoRouter instance (should be overridden in app setup)
final goRouterProvider = Provider<GoRouter>((ref) {
  throw UnimplementedError(
    'goRouterProvider must be overridden with your GoRouter instance',
  );
});

/// Provider for the navigator key (should be overridden in app setup)
final navigatorKeyProvider = Provider<GlobalKey<NavigatorState>>((ref) {
  return GlobalKey<NavigatorState>(debugLabel: 'deeplink_navigator');
});

/// Provider for the DeepLinkNotifier
final deepLinkProvider =
    StateNotifierProvider<DeepLinkNotifier, DeepLinkState>((ref) {
  GoRouter? router;
  GlobalKey<NavigatorState>? navigatorKey;

  // Try to get router, but don't fail if not available
  try {
    router = ref.watch(goRouterProvider);
  } catch (_) {
    // Router not yet available
  }

  // Try to get navigator key
  try {
    navigatorKey = ref.watch(navigatorKeyProvider);
  } catch (_) {
    // Navigator key not yet available
  }

  final notifier = DeepLinkNotifier(
    ref: ref,
    navigatorKey: navigatorKey,
    router: router,
  );

  // Auto-initialize
  notifier.initialize();

  return notifier;
});

/// Provider for checking if there's a pending deep link
final hasPendingDeepLinkProvider = Provider<bool>((ref) {
  return ref.watch(deepLinkProvider).hasPendingLink;
});

/// Provider for the current deep link data
final currentDeepLinkProvider = Provider<DeepLinkData?>((ref) {
  return ref.watch(deepLinkProvider).currentLink;
});

/// Provider for deep link errors
final deepLinkErrorProvider = Provider<String?>((ref) {
  return ref.watch(deepLinkProvider).error;
});

/// Provider for pending auth link
final pendingAuthLinkProvider = Provider<DeepLinkData?>((ref) {
  return ref.watch(deepLinkProvider).pendingAuthLink;
});

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Handler Widget
// ═══════════════════════════════════════════════════════════════════════════

/// Widget that handles deep links and navigates accordingly
class DeepLinkHandler extends ConsumerStatefulWidget {
  /// Child widget to render
  final Widget child;

  /// Callback when a deep link is received
  final void Function(DeepLinkData link)? onLinkReceived;

  /// Callback when navigation is about to occur
  final bool Function(DeepLinkData link)? onBeforeNavigation;

  /// Whether to auto-handle links
  final bool autoHandle;

  const DeepLinkHandler({
    super.key,
    required this.child,
    this.onLinkReceived,
    this.onBeforeNavigation,
    this.autoHandle = true,
  });

  @override
  ConsumerState<DeepLinkHandler> createState() => _DeepLinkHandlerState();
}

class _DeepLinkHandlerState extends ConsumerState<DeepLinkHandler>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    // Handle any pending link after frame is built
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkPendingLink();
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      // Check for new links when app resumes
      _checkPendingLink();
    }
  }

  void _checkPendingLink() {
    final deepLinkState = ref.read(deepLinkProvider);

    if (deepLinkState.hasPendingLink && deepLinkState.currentLink != null) {
      final link = deepLinkState.currentLink!;

      // Notify callback
      widget.onLinkReceived?.call(link);

      // Check if navigation should proceed
      final shouldNavigate = widget.onBeforeNavigation?.call(link) ?? true;

      if (widget.autoHandle && shouldNavigate) {
        ref.read(deepLinkProvider.notifier).handleCurrentLink(context);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Listen for deep link changes
    ref.listen<DeepLinkState>(deepLinkProvider, (previous, next) {
      if (next.hasPendingLink && next.currentLink != null) {
        // New link received
        if (previous?.currentLink != next.currentLink) {
          _checkPendingLink();
        }
      }

      // Log errors
      if (next.error != null && next.error != previous?.error) {
        AppLogger.e(
          'Deep link error',
          tag: 'DEEPLINK',
          error: next.error,
        );
      }
    });

    // Listen for auth state changes to handle pending auth links
    ref.listen<AuthState>(authProvider, (previous, next) {
      if (!previous!.isLoggedIn && next.isLoggedIn) {
        // User just logged in, check for pending auth link
        final pendingLink = ref.read(pendingAuthLinkProvider);
        if (pendingLink != null) {
          AppLogger.i('User logged in, handling pending auth link', tag: 'DEEPLINK');
          ref.read(deepLinkProvider.notifier).handlePendingAuthLink(context);
        }
      }
    });

    return widget.child;
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
  return DeepLinkBuilder.passwordReset(
    token: token,
    email: email,
    useUniversalLink: useUniversalLink,
  );
}

/// Build an OTP verification deep link URL
String buildOtpVerificationLink({
  required String identifier,
  required OtpPurpose purpose,
  String? otp,
  String? sessionId,
  bool useUniversalLink = true,
}) {
  return DeepLinkBuilder.verifyOtp(
    identifier: identifier,
    purpose: purpose.name,
    otp: otp,
    sessionId: sessionId,
    useUniversalLink: useUniversalLink,
  );
}

/// Build a field deep link URL
String buildFieldLink({
  required String fieldId,
  bool useUniversalLink = false,
}) {
  return DeepLinkBuilder.field(fieldId, useUniversalLink: useUniversalLink);
}

/// Build a weather deep link URL
String buildWeatherLink({
  String? fieldId,
  bool useUniversalLink = false,
}) {
  return DeepLinkBuilder.weather(
    fieldId: fieldId,
    useUniversalLink: useUniversalLink,
  );
}

/// Build an NDVI deep link URL
String buildNdviLink({
  required String fieldId,
  bool useUniversalLink = false,
}) {
  return DeepLinkBuilder.ndvi(fieldId, useUniversalLink: useUniversalLink);
}

/// Build a task deep link URL
String buildTaskLink({
  required String taskId,
  bool useUniversalLink = false,
}) {
  return DeepLinkBuilder.task(taskId, useUniversalLink: useUniversalLink);
}

/// Build an alert deep link URL
String buildAlertLink({
  required String alertId,
  bool useUniversalLink = false,
}) {
  return DeepLinkBuilder.alert(alertId, useUniversalLink: useUniversalLink);
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
