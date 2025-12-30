import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';

/// Deep Link Handler for Android App Links and Custom Schemes
///
/// Handles incoming deep links from:
/// - HTTPS URLs: https://sahool.app/field/{fieldId}
/// - Custom Scheme: sahool://open/{path}
///
/// Usage:
/// ```dart
/// final handler = DeepLinkHandler(router: AppRouter.router);
/// await handler.initialize();
/// ```
class DeepLinkHandler {
  final GoRouter router;
  static const _platform = MethodChannel('io.sahool.field/deep_links');

  StreamSubscription<String>? _linkSubscription;
  String? _initialLink;
  bool _initialized = false;

  DeepLinkHandler({required this.router});

  /// Initialize deep link handling
  ///
  /// This should be called once during app initialization.
  /// It will:
  /// 1. Get the initial deep link (if app was opened via deep link)
  /// 2. Listen for deep links while app is running
  Future<void> initialize() async {
    if (_initialized) {
      debugPrint('⚠️ DeepLinkHandler already initialized');
      return;
    }

    try {
      // Get initial deep link (when app is opened from closed state)
      _initialLink = await _getInitialLink();
      if (_initialLink != null) {
        debugPrint('📱 Initial deep link: $_initialLink');
        await _handleDeepLink(_initialLink!);
      }

      // Listen for deep links while app is running
      _startListening();

      _initialized = true;
      debugPrint('✅ DeepLinkHandler initialized');
    } catch (e) {
      debugPrint('❌ DeepLinkHandler initialization failed: $e');
    }
  }

  /// Get the initial deep link (if app was launched via deep link)
  Future<String?> _getInitialLink() async {
    try {
      final String? initialLink = await _platform.invokeMethod('getInitialLink');
      return initialLink;
    } on PlatformException catch (e) {
      debugPrint('⚠️ Failed to get initial link: ${e.message}');
      return null;
    }
  }

  /// Start listening for deep links while app is running
  void _startListening() {
    // Note: This requires implementing a MethodChannel on the native side
    // For now, we'll use a basic implementation
    // In production, you should use a package like uni_links or app_links
    debugPrint('📡 Listening for deep links...');
  }

  /// Handle incoming deep link
  Future<void> _handleDeepLink(String link) async {
    try {
      final uri = Uri.parse(link);
      debugPrint('🔗 Processing deep link: ${uri.toString()}');

      // Route based on the link
      final route = _parseDeepLink(uri);
      if (route != null) {
        debugPrint('🧭 Navigating to: $route');
        router.go(route);
      } else {
        debugPrint('⚠️ Unknown deep link pattern: $link');
        // Navigate to home if link is not recognized
        router.go('/map');
      }
    } catch (e) {
      debugPrint('❌ Error handling deep link: $e');
      // Navigate to home on error
      router.go('/map');
    }
  }

  /// Parse deep link URI and return the corresponding route
  String? _parseDeepLink(Uri uri) {
    // Handle HTTPS links: https://sahool.app/field/123
    if (uri.scheme == 'https' &&
        (uri.host == 'sahool.app' || uri.host == 'www.sahool.app')) {
      return _parseHttpsLink(uri);
    }

    // Handle custom scheme: sahool://open/field/123
    if (uri.scheme == 'sahool') {
      return _parseCustomSchemeLink(uri);
    }

    return null;
  }

  /// Parse HTTPS deep links
  String? _parseHttpsLink(Uri uri) {
    final pathSegments = uri.pathSegments;

    if (pathSegments.isEmpty) {
      return '/map'; // Home screen
    }

    // Pattern: /field/{fieldId}
    if (pathSegments.length == 2 && pathSegments[0] == 'field') {
      final fieldId = pathSegments[1];
      return '/field/$fieldId';
    }

    // Pattern: /crop/{cropId}
    // Note: This route needs to be added to app_router.dart
    if (pathSegments.length == 2 && pathSegments[0] == 'crop') {
      final cropId = pathSegments[1];
      // TODO: Add crop route to app_router.dart
      debugPrint('⚠️ Crop route not implemented yet: /crop/$cropId');
      return '/map';
    }

    // Pattern: /task/{taskId}
    // Note: This route needs to be added to app_router.dart
    if (pathSegments.length == 2 && pathSegments[0] == 'task') {
      final taskId = pathSegments[1];
      // TODO: Add task route to app_router.dart
      debugPrint('⚠️ Task route not implemented yet: /task/$taskId');
      return '/map';
    }

    // Pattern: /field/{fieldId}/dashboard
    if (pathSegments.length == 3 &&
        pathSegments[0] == 'field' &&
        pathSegments[2] == 'dashboard') {
      final fieldId = pathSegments[1];
      return '/field/$fieldId/dashboard';
    }

    // Pattern: /field/{fieldId}/ecological
    if (pathSegments.length == 3 &&
        pathSegments[0] == 'field' &&
        pathSegments[2] == 'ecological') {
      final fieldId = pathSegments[1];
      return '/field/$fieldId/ecological';
    }

    return null;
  }

  /// Parse custom scheme deep links (sahool://open/{path})
  String? _parseCustomSchemeLink(Uri uri) {
    // Pattern: sahool://open/field/123
    if (uri.host == 'open') {
      final pathSegments = uri.pathSegments;

      if (pathSegments.isEmpty) {
        return '/map';
      }

      // Reconstruct the path and delegate to HTTPS parser
      final fakePath = pathSegments.join('/');
      final fakeUri = Uri.parse('https://sahool.app/$fakePath');
      return _parseHttpsLink(fakeUri);
    }

    return null;
  }

  /// Handle a deep link manually (useful for testing)
  Future<void> handleLink(String link) async {
    await _handleDeepLink(link);
  }

  /// Dispose resources
  void dispose() {
    _linkSubscription?.cancel();
    _initialized = false;
    debugPrint('🗑️ DeepLinkHandler disposed');
  }
}

/// Extension on GoRouter for deep link support
extension DeepLinkRouterExtension on GoRouter {
  /// Create a deep link handler for this router
  DeepLinkHandler createDeepLinkHandler() {
    return DeepLinkHandler(router: this);
  }
}

/// Deep Link Testing Utilities
///
/// Use these utilities to test deep links in development
class DeepLinkTester {
  /// Test various deep link patterns
  static void testDeepLinks(DeepLinkHandler handler) {
    if (!kDebugMode) return;

    debugPrint('🧪 Testing Deep Links...');

    final testLinks = [
      'https://sahool.app/field/123',
      'https://sahool.app/field/456/dashboard',
      'https://sahool.app/crop/789',
      'https://sahool.app/task/101112',
      'sahool://open/field/123',
      'sahool://open/field/456/ecological',
      'https://www.sahool.app/field/789',
    ];

    for (final link in testLinks) {
      try {
        final uri = Uri.parse(link);
        final route = handler._parseDeepLink(uri);
        debugPrint('  $link → ${route ?? "NOT MATCHED"}');
      } catch (e) {
        debugPrint('  $link → ERROR: $e');
      }
    }
  }

  /// Generate a test deep link
  static String generateFieldLink(String fieldId, {bool useCustomScheme = false}) {
    if (useCustomScheme) {
      return 'sahool://open/field/$fieldId';
    }
    return 'https://sahool.app/field/$fieldId';
  }

  /// Generate a test crop link
  static String generateCropLink(String cropId, {bool useCustomScheme = false}) {
    if (useCustomScheme) {
      return 'sahool://open/crop/$cropId';
    }
    return 'https://sahool.app/crop/$cropId';
  }

  /// Generate a test task link
  static String generateTaskLink(String taskId, {bool useCustomScheme = false}) {
    if (useCustomScheme) {
      return 'sahool://open/task/$taskId';
    }
    return 'https://sahool.app/task/$taskId';
  }
}
