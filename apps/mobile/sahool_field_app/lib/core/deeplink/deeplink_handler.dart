/// SAHOOL Deep Link Handler
/// معالج الروابط العميقة
///
/// Handles deep links for password reset, OTP verification, and app navigation.
/// Supports both custom URI scheme (sahool://) and universal links (https://sahool.app/).
///
/// Features:
/// - Password reset link handling
/// - OTP verification link handling
/// - Universal links for iOS
/// - App links for Android
/// - Riverpod integration
/// - Lifecycle management
///
/// Link Formats:
/// - Custom scheme: sahool://reset-password?token=xxx
/// - Custom scheme: sahool://verify-otp?identifier=xxx&purpose=xxx
/// - Universal link: https://sahool.app/reset-password?token=xxx
/// - Universal link: https://sahool.app/verify-otp?identifier=xxx&purpose=xxx
library;

import 'dart:async';

import 'package:app_links/app_links.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../utils/app_logger.dart';
// Re-export models for backward compatibility
export 'deeplink_models.dart';
import 'deeplink_models.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Handler Notifier
// ═══════════════════════════════════════════════════════════════════════════

/// Riverpod notifier for managing deep link state
class DeepLinkNotifier extends StateNotifier<DeepLinkState> {
  final AppLinks _appLinks;
  StreamSubscription<Uri>? _linkSubscription;
  final GlobalKey<NavigatorState>? _navigatorKey;
  GoRouter? _router;

  DeepLinkNotifier({
    GlobalKey<NavigatorState>? navigatorKey,
    GoRouter? router,
  })  : _appLinks = AppLinks(),
        _navigatorKey = navigatorKey,
        _router = router,
        super(const DeepLinkState());

  /// Initialize the deep link handler
  Future<void> initialize() async {
    if (state.isInitialized) {
      AppLogger.w('Deep link handler already initialized', tag: 'DEEPLINK');
      return;
    }

    AppLogger.i('Initializing deep link handler...', tag: 'DEEPLINK');

    try {
      // Check for initial link (app opened via deep link)
      final initialLink = await _appLinks.getInitialLinkString();
      if (initialLink != null) {
        AppLogger.i('Initial deep link found: $initialLink', tag: 'DEEPLINK');
        _handleLinkString(initialLink, isInitial: true);
      }

      // Listen for incoming links while app is running
      _linkSubscription = _appLinks.uriLinkStream.listen(
        _handleUri,
        onError: (Object error) {
          AppLogger.e(
            'Deep link stream error',
            tag: 'DEEPLINK',
            error: error,
          );
          state = state.copyWith(
            error: 'Failed to listen for deep links: $error',
          );
        },
      );

      state = state.copyWith(isInitialized: true);
      AppLogger.i('Deep link handler initialized successfully',
          tag: 'DEEPLINK');
    } catch (e, stackTrace) {
      AppLogger.e(
        'Failed to initialize deep link handler',
        tag: 'DEEPLINK',
        error: e,
        stackTrace: stackTrace,
      );
      state = state.copyWith(
        error: 'Initialization failed: $e',
      );
    }
  }

  /// Set the router for navigation
  void setRouter(GoRouter router) {
    _router = router;
    AppLogger.d('Router set for deep link handler', tag: 'DEEPLINK');
  }

  /// Handle a URI link
  void _handleUri(Uri uri) {
    AppLogger.i('Received deep link: $uri', tag: 'DEEPLINK');
    _processUri(uri, isInitial: false);
  }

  /// Handle a link string
  void _handleLinkString(String linkString, {bool isInitial = false}) {
    try {
      final uri = Uri.parse(linkString);
      _processUri(uri, isInitial: isInitial);
    } catch (e) {
      AppLogger.e(
        'Failed to parse deep link string',
        tag: 'DEEPLINK',
        error: e,
        data: {'link': linkString},
      );
      state = state.copyWith(error: 'Invalid link format: $linkString');
    }
  }

  /// Process a URI and update state
  void _processUri(Uri uri, {bool isInitial = false}) {
    final deepLinkData = _parseUri(uri);

    if (deepLinkData == null) {
      AppLogger.w('Unsupported deep link: $uri', tag: 'DEEPLINK');
      state = state.copyWith(error: 'Unsupported link: $uri');
      return;
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
      },
    );
  }

  /// Parse a URI into DeepLinkData
  DeepLinkData? _parseUri(Uri uri) {
    // Check if it's a valid SAHOOL deep link
    if (!_isValidSahoolLink(uri)) {
      return null;
    }

    final path = uri.path.toLowerCase();
    final queryParams = uri.queryParameters;
    final receivedAt = DateTime.now();

    // Parse based on path
    if (path == DeepLinkPaths.resetPassword ||
        path.endsWith(DeepLinkPaths.resetPassword)) {
      return _parsePasswordResetLink(uri, queryParams, receivedAt);
    }

    if (path == DeepLinkPaths.verifyOtp ||
        path.endsWith(DeepLinkPaths.verifyOtp)) {
      return _parseOtpVerificationLink(uri, queryParams, receivedAt);
    }

    if (path == DeepLinkPaths.verifyEmail ||
        path.endsWith(DeepLinkPaths.verifyEmail)) {
      return DeepLinkData(
        type: DeepLinkType.verifyEmail,
        uri: uri,
        parameters: queryParams,
        receivedAt: receivedAt,
      );
    }

    if (path == DeepLinkPaths.activateAccount ||
        path.endsWith(DeepLinkPaths.activateAccount)) {
      return DeepLinkData(
        type: DeepLinkType.activateAccount,
        uri: uri,
        parameters: queryParams,
        receivedAt: receivedAt,
      );
    }

    if (path.startsWith(DeepLinkPaths.fieldDetails) ||
        path.contains(DeepLinkPaths.fieldDetails)) {
      return DeepLinkData(
        type: DeepLinkType.fieldDetails,
        uri: uri,
        parameters: queryParams,
        receivedAt: receivedAt,
      );
    }

    if (path == DeepLinkPaths.notification ||
        path.endsWith(DeepLinkPaths.notification)) {
      return DeepLinkData(
        type: DeepLinkType.notification,
        uri: uri,
        parameters: queryParams,
        receivedAt: receivedAt,
      );
    }

    if (path == DeepLinkPaths.invite || path.endsWith(DeepLinkPaths.invite)) {
      return DeepLinkData(
        type: DeepLinkType.invite,
        uri: uri,
        parameters: queryParams,
        receivedAt: receivedAt,
      );
    }

    // Unknown link type
    return DeepLinkData(
      type: DeepLinkType.unknown,
      uri: uri,
      parameters: queryParams,
      receivedAt: receivedAt,
    );
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
    );
  }

  /// Parse OTP verification link
  OtpVerificationLinkData? _parseOtpVerificationLink(
    Uri uri,
    Map<String, String> params,
    DateTime receivedAt,
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

  /// Navigate to the appropriate screen for a deep link
  Future<bool> _navigateForLink(DeepLinkData link, BuildContext context) async {
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
          final fieldId = link.parameters['id'] ?? link.parameters['field_id'];
          if (fieldId != null) {
            return _navigateToPath('/field/$fieldId');
          }
          return false;

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
      // Check if token might be expired (client-side check only)
      if (link.isExpired) {
        AppLogger.w('Password reset token may be expired', tag: 'DEEPLINK');
        // Still navigate, let server validate
      }

      return _navigateToPath(
        '/reset-password',
        extra: {
          'token': link.token,
          'email': link.email,
        },
      );
    }

    // Fallback for generic DeepLinkData
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

    // Fallback for generic DeepLinkData
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
    _handleLinkString(linkString, isInitial: false);
  }

  /// Manually process a URI
  void processUri(Uri uri) {
    _processUri(uri, isInitial: false);
  }

  /// Clear the current pending link
  void clearPendingLink() {
    state = state.copyWith(
      hasPendingLink: false,
      clearCurrentLink: true,
    );
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

/// Provider for the GoRouter instance
/// This provider gets the router from the appRouterProvider defined in app.dart
/// If accessed before app.dart initializes, it will return null and use fallback
final goRouterProvider = Provider<GoRouter?>((ref) {
  // This is a placeholder - the actual router is set via setRouter() method
  // in the DeepLinkNotifier when the app initializes
  return null;
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
  // The router will be set later via setRouter() when app.dart initializes
  router = ref.watch(goRouterProvider);

  // Try to get navigator key
  try {
    navigatorKey = ref.watch(navigatorKeyProvider);
  } catch (_) {
    // Navigator key not yet available
  }

  final notifier = DeepLinkNotifier(
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
  // Basic validation - token should be at least 32 characters
  // and contain only alphanumeric characters and hyphens
  if (token.length < 32) return false;

  final validPattern = RegExp(r'^[a-zA-Z0-9\-_]+$');
  return validPattern.hasMatch(token);
}

/// Extract field ID from a deep link path
String? extractFieldIdFromPath(String path) {
  // Match patterns like /field/123 or /fields/abc-def
  final pattern = RegExp(r'/fields?/([a-zA-Z0-9\-_]+)');
  final match = pattern.firstMatch(path);
  return match?.group(1);
}
