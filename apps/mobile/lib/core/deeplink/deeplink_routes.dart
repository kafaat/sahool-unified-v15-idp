/// SAHOOL Deep Link Routes Configuration
/// تكوين مسارات الروابط العميقة
///
/// Defines all supported deep link routes, their patterns, and required parameters.
/// يعرف جميع مسارات الروابط العميقة المدعومة وأنماطها والمعاملات المطلوبة.
///
/// Supported Deep Links:
/// - sahool://field/{fieldId} - Open specific field
/// - sahool://weather - Open weather screen
/// - sahool://ndvi/{fieldId} - Open NDVI for field
/// - sahool://task/{taskId} - Open specific task
/// - sahool://alert/{alertId} - Open alert details
library;

import 'package:flutter/foundation.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Route Definitions
// ═══════════════════════════════════════════════════════════════════════════

/// All supported deep link routes with their configuration
class DeepLinkRoutes {
  DeepLinkRoutes._();

  /// Custom URI scheme for the SAHOOL app
  static const String scheme = 'sahool';

  /// Universal link hosts
  static const List<String> universalLinkHosts = [
    'sahool.app',
    'www.sahool.app',
    'app.sahool.app',
  ];

  // ─────────────────────────────────────────────────────────────────────────
  // Field Routes - مسارات الحقل
  // ─────────────────────────────────────────────────────────────────────────

  /// Field details route: sahool://field/{fieldId}
  static const DeepLinkRoute field = DeepLinkRoute(
    path: '/field',
    pathPattern: r'^/field/([a-zA-Z0-9\-_]+)$',
    parameterNames: ['fieldId'],
    requiresAuth: true,
    appRoute: '/field/:id',
    nameEn: 'Field Details',
    nameAr: 'تفاصيل الحقل',
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Weather Routes - مسارات الطقس
  // ─────────────────────────────────────────────────────────────────────────

  /// Weather screen route: sahool://weather or sahool://weather?fieldId={fieldId}
  static const DeepLinkRoute weather = DeepLinkRoute(
    path: '/weather',
    pathPattern: r'^/weather/?$',
    parameterNames: [],
    optionalQueryParams: ['fieldId'],
    requiresAuth: false,
    appRoute: '/weather',
    nameEn: 'Weather',
    nameAr: 'الطقس',
  );

  // ─────────────────────────────────────────────────────────────────────────
  // NDVI / Satellite Routes - مسارات NDVI / القمر الصناعي
  // ─────────────────────────────────────────────────────────────────────────

  /// NDVI details route: sahool://ndvi/{fieldId}
  static const DeepLinkRoute ndvi = DeepLinkRoute(
    path: '/ndvi',
    pathPattern: r'^/ndvi/([a-zA-Z0-9\-_]+)$',
    parameterNames: ['fieldId'],
    requiresAuth: true,
    appRoute: '/satellite/:fieldId',
    nameEn: 'NDVI Analysis',
    nameAr: 'تحليل NDVI',
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Task Routes - مسارات المهام
  // ─────────────────────────────────────────────────────────────────────────

  /// Task details route: sahool://task/{taskId}
  static const DeepLinkRoute task = DeepLinkRoute(
    path: '/task',
    pathPattern: r'^/task/([a-zA-Z0-9\-_]+)$',
    parameterNames: ['taskId'],
    requiresAuth: true,
    appRoute: '/task/:id',
    nameEn: 'Task Details',
    nameAr: 'تفاصيل المهمة',
  );

  /// Tasks list route: sahool://tasks or sahool://tasks?fieldId={fieldId}
  static const DeepLinkRoute tasks = DeepLinkRoute(
    path: '/tasks',
    pathPattern: r'^/tasks/?$',
    parameterNames: [],
    optionalQueryParams: ['fieldId'],
    requiresAuth: true,
    appRoute: '/tasks',
    nameEn: 'Tasks List',
    nameAr: 'قائمة المهام',
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Alert Routes - مسارات التنبيهات
  // ─────────────────────────────────────────────────────────────────────────

  /// Alert details route: sahool://alert/{alertId}
  static const DeepLinkRoute alert = DeepLinkRoute(
    path: '/alert',
    pathPattern: r'^/alert/([a-zA-Z0-9\-_]+)$',
    parameterNames: ['alertId'],
    requiresAuth: true,
    appRoute: '/alert/:id',
    nameEn: 'Alert Details',
    nameAr: 'تفاصيل التنبيه',
  );

  /// Alerts list route: sahool://alerts
  static const DeepLinkRoute alerts = DeepLinkRoute(
    path: '/alerts',
    pathPattern: r'^/alerts/?$',
    parameterNames: [],
    requiresAuth: true,
    appRoute: '/alerts',
    nameEn: 'Alerts',
    nameAr: 'التنبيهات',
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Auth Routes - مسارات المصادقة
  // ─────────────────────────────────────────────────────────────────────────

  /// Password reset route: sahool://reset-password?token={token}
  static const DeepLinkRoute resetPassword = DeepLinkRoute(
    path: '/reset-password',
    pathPattern: r'^/reset-password/?$',
    parameterNames: [],
    requiredQueryParams: ['token'],
    optionalQueryParams: ['email'],
    requiresAuth: false,
    appRoute: '/reset-password',
    nameEn: 'Reset Password',
    nameAr: 'إعادة تعيين كلمة المرور',
  );

  /// OTP verification route: sahool://verify-otp?identifier={identifier}&purpose={purpose}
  static const DeepLinkRoute verifyOtp = DeepLinkRoute(
    path: '/verify-otp',
    pathPattern: r'^/verify-otp/?$',
    parameterNames: [],
    requiredQueryParams: ['identifier', 'purpose'],
    optionalQueryParams: ['otp', 'session_id'],
    requiresAuth: false,
    appRoute: '/verify-otp',
    nameEn: 'Verify OTP',
    nameAr: 'التحقق من الرمز',
  );

  /// Login route: sahool://login
  static const DeepLinkRoute login = DeepLinkRoute(
    path: '/login',
    pathPattern: r'^/login/?$',
    parameterNames: [],
    optionalQueryParams: ['redirect'],
    requiresAuth: false,
    appRoute: '/login',
    nameEn: 'Login',
    nameAr: 'تسجيل الدخول',
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Other Routes - مسارات أخرى
  // ─────────────────────────────────────────────────────────────────────────

  /// Home route: sahool://home
  static const DeepLinkRoute home = DeepLinkRoute(
    path: '/home',
    pathPattern: r'^/home/?$',
    parameterNames: [],
    requiresAuth: false,
    appRoute: '/home',
    nameEn: 'Home',
    nameAr: 'الرئيسية',
  );

  /// Notifications route: sahool://notifications
  static const DeepLinkRoute notifications = DeepLinkRoute(
    path: '/notifications',
    pathPattern: r'^/notifications/?$',
    parameterNames: [],
    optionalQueryParams: ['notificationId'],
    requiresAuth: true,
    appRoute: '/notifications',
    nameEn: 'Notifications',
    nameAr: 'الإشعارات',
  );

  /// Satellite/monitoring route: sahool://satellite
  static const DeepLinkRoute satellite = DeepLinkRoute(
    path: '/satellite',
    pathPattern: r'^/satellite/?$',
    parameterNames: [],
    requiresAuth: true,
    appRoute: '/satellite',
    nameEn: 'Satellite Monitoring',
    nameAr: 'المراقبة الفضائية',
  );

  /// Advisor/chat route: sahool://advisor
  static const DeepLinkRoute advisor = DeepLinkRoute(
    path: '/advisor',
    pathPattern: r'^/advisor/?$',
    parameterNames: [],
    requiresAuth: true,
    appRoute: '/advisor',
    nameEn: 'AI Advisor',
    nameAr: 'المستشار الذكي',
  );

  // ─────────────────────────────────────────────────────────────────────────
  // All Routes List
  // ─────────────────────────────────────────────────────────────────────────

  /// All registered deep link routes
  static const List<DeepLinkRoute> allRoutes = [
    field,
    weather,
    ndvi,
    task,
    tasks,
    alert,
    alerts,
    resetPassword,
    verifyOtp,
    login,
    home,
    notifications,
    satellite,
    advisor,
  ];

  /// Routes that require authentication
  static List<DeepLinkRoute> get authRequiredRoutes =>
      allRoutes.where((r) => r.requiresAuth).toList();

  /// Routes that don't require authentication
  static List<DeepLinkRoute> get publicRoutes =>
      allRoutes.where((r) => !r.requiresAuth).toList();

  /// Find route matching a path
  static DeepLinkRoute? findMatchingRoute(String path) {
    for (final route in allRoutes) {
      if (route.matches(path)) {
        return route;
      }
    }
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Route Model
// ═══════════════════════════════════════════════════════════════════════════

/// Configuration for a single deep link route
@immutable
class DeepLinkRoute {
  /// The base path for this route (e.g., '/field')
  final String path;

  /// Regex pattern for matching the full path including parameters
  final String pathPattern;

  /// Names of path parameters extracted from the URL
  final List<String> parameterNames;

  /// Required query parameters for this route
  final List<String> requiredQueryParams;

  /// Optional query parameters for this route
  final List<String> optionalQueryParams;

  /// Whether this route requires user authentication
  final bool requiresAuth;

  /// The corresponding app route to navigate to
  final String appRoute;

  /// English name for display/logging
  final String nameEn;

  /// Arabic name for display/logging
  final String nameAr;

  const DeepLinkRoute({
    required this.path,
    required this.pathPattern,
    required this.parameterNames,
    this.requiredQueryParams = const [],
    this.optionalQueryParams = const [],
    required this.requiresAuth,
    required this.appRoute,
    required this.nameEn,
    required this.nameAr,
  });

  /// Check if a path matches this route
  bool matches(String path) {
    final regex = RegExp(pathPattern, caseSensitive: false);
    return regex.hasMatch(path);
  }

  /// Extract path parameters from a URL path
  Map<String, String> extractPathParams(String path) {
    final regex = RegExp(pathPattern, caseSensitive: false);
    final match = regex.firstMatch(path);

    if (match == null) return {};

    final params = <String, String>{};
    for (var i = 0; i < parameterNames.length; i++) {
      final groupIndex = i + 1;
      if (groupIndex <= match.groupCount) {
        final value = match.group(groupIndex);
        if (value != null) {
          params[parameterNames[i]] = value;
        }
      }
    }

    return params;
  }

  /// Validate query parameters against required params
  bool validateQueryParams(Map<String, String> queryParams) {
    for (final required in requiredQueryParams) {
      if (!queryParams.containsKey(required) ||
          queryParams[required]?.isEmpty == true) {
        return false;
      }
    }
    return true;
  }

  /// Get the app route with parameters substituted
  String buildAppRoute(Map<String, String> params) {
    var route = appRoute;

    // Replace path parameters
    for (final entry in params.entries) {
      route = route.replaceAll(':${entry.key}', entry.value);
      route = route.replaceAll(':id', entry.value);
    }

    return route;
  }

  /// Get list of missing required query parameters
  List<String> getMissingRequiredParams(Map<String, String> queryParams) {
    return requiredQueryParams
        .where((param) =>
            !queryParams.containsKey(param) ||
            queryParams[param]?.isEmpty == true)
        .toList();
  }

  @override
  String toString() => 'DeepLinkRoute($path, requiresAuth: $requiresAuth)';
}

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Parse Result
// ═══════════════════════════════════════════════════════════════════════════

/// Result of parsing a deep link URL
@immutable
class DeepLinkParseResult {
  /// The matched route (null if no match)
  final DeepLinkRoute? route;

  /// Original URI that was parsed
  final Uri uri;

  /// Extracted path parameters
  final Map<String, String> pathParams;

  /// Query parameters from the URL
  final Map<String, String> queryParams;

  /// Whether the parse was successful
  final bool isValid;

  /// Error message if parsing failed
  final String? errorMessage;

  /// Error message in Arabic
  final String? errorMessageAr;

  const DeepLinkParseResult({
    required this.route,
    required this.uri,
    required this.pathParams,
    required this.queryParams,
    required this.isValid,
    this.errorMessage,
    this.errorMessageAr,
  });

  /// Create a successful parse result
  factory DeepLinkParseResult.success({
    required DeepLinkRoute route,
    required Uri uri,
    required Map<String, String> pathParams,
    required Map<String, String> queryParams,
  }) {
    return DeepLinkParseResult(
      route: route,
      uri: uri,
      pathParams: pathParams,
      queryParams: queryParams,
      isValid: true,
    );
  }

  /// Create a failed parse result
  factory DeepLinkParseResult.failure({
    required Uri uri,
    required String errorMessage,
    required String errorMessageAr,
  }) {
    return DeepLinkParseResult(
      route: null,
      uri: uri,
      pathParams: const {},
      queryParams: uri.queryParameters,
      isValid: false,
      errorMessage: errorMessage,
      errorMessageAr: errorMessageAr,
    );
  }

  /// All parameters combined (path + query)
  Map<String, String> get allParams => {...pathParams, ...queryParams};

  /// Get the app route to navigate to
  String? get appRoute {
    if (route == null) return null;
    return route!.buildAppRoute(allParams);
  }

  /// Whether this route requires authentication
  bool get requiresAuth => route?.requiresAuth ?? false;

  @override
  String toString() {
    if (isValid) {
      return 'DeepLinkParseResult(route: ${route?.path}, params: $allParams)';
    }
    return 'DeepLinkParseResult(error: $errorMessage)';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Parser
// ═══════════════════════════════════════════════════════════════════════════

/// Utility class for parsing deep link URLs
class DeepLinkParser {
  DeepLinkParser._();

  /// Parse a URI into a DeepLinkParseResult
  static DeepLinkParseResult parse(Uri uri) {
    // Validate scheme
    if (!_isValidScheme(uri)) {
      return DeepLinkParseResult.failure(
        uri: uri,
        errorMessage: 'Invalid deep link scheme: ${uri.scheme}',
        errorMessageAr: 'نظام الرابط غير صالح: ${uri.scheme}',
      );
    }

    // Get the path (handle both custom scheme and universal links)
    final path = _extractPath(uri);

    // Find matching route
    final route = DeepLinkRoutes.findMatchingRoute(path);
    if (route == null) {
      return DeepLinkParseResult.failure(
        uri: uri,
        errorMessage: 'Unknown deep link path: $path',
        errorMessageAr: 'مسار الرابط غير معروف: $path',
      );
    }

    // Extract path parameters
    final pathParams = route.extractPathParams(path);

    // Validate required query parameters
    if (!route.validateQueryParams(uri.queryParameters)) {
      final missing = route.getMissingRequiredParams(uri.queryParameters);
      return DeepLinkParseResult.failure(
        uri: uri,
        errorMessage: 'Missing required parameters: ${missing.join(', ')}',
        errorMessageAr: 'معاملات مطلوبة مفقودة: ${missing.join(', ')}',
      );
    }

    return DeepLinkParseResult.success(
      route: route,
      uri: uri,
      pathParams: pathParams,
      queryParams: uri.queryParameters,
    );
  }

  /// Parse a string URL into a DeepLinkParseResult
  static DeepLinkParseResult parseString(String url) {
    try {
      final uri = Uri.parse(url);
      return parse(uri);
    } catch (e) {
      return DeepLinkParseResult.failure(
        uri: Uri(),
        errorMessage: 'Invalid URL format: $url',
        errorMessageAr: 'تنسيق الرابط غير صالح: $url',
      );
    }
  }

  /// Check if the URI scheme is valid for SAHOOL
  static bool _isValidScheme(Uri uri) {
    // Custom scheme
    if (uri.scheme == DeepLinkRoutes.scheme) {
      return true;
    }

    // Universal links (HTTPS)
    if (uri.scheme == 'https' || uri.scheme == 'http') {
      final host = uri.host.toLowerCase();
      return DeepLinkRoutes.universalLinkHosts
          .any((h) => host == h || host.endsWith('.$h'));
    }

    return false;
  }

  /// Extract the path from a URI (handling both custom scheme and universal links)
  static String _extractPath(Uri uri) {
    if (uri.scheme == DeepLinkRoutes.scheme) {
      // For custom scheme: sahool://field/123 -> /field/123
      // The host is actually the first path segment
      if (uri.host.isNotEmpty) {
        return '/${uri.host}${uri.path}';
      }
      return uri.path;
    }

    // For universal links, the path is already correct
    return uri.path;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Deep Link Builder
// ═══════════════════════════════════════════════════════════════════════════

/// Utility class for building deep link URLs
class DeepLinkBuilder {
  DeepLinkBuilder._();

  /// Build a field deep link
  static String field(String fieldId, {bool useUniversalLink = false}) {
    return _build(
      path: '/field/$fieldId',
      useUniversalLink: useUniversalLink,
    );
  }

  /// Build a weather deep link
  static String weather({String? fieldId, bool useUniversalLink = false}) {
    return _build(
      path: '/weather',
      queryParams: fieldId != null ? {'fieldId': fieldId} : null,
      useUniversalLink: useUniversalLink,
    );
  }

  /// Build an NDVI deep link
  static String ndvi(String fieldId, {bool useUniversalLink = false}) {
    return _build(
      path: '/ndvi/$fieldId',
      useUniversalLink: useUniversalLink,
    );
  }

  /// Build a task deep link
  static String task(String taskId, {bool useUniversalLink = false}) {
    return _build(
      path: '/task/$taskId',
      useUniversalLink: useUniversalLink,
    );
  }

  /// Build an alert deep link
  static String alert(String alertId, {bool useUniversalLink = false}) {
    return _build(
      path: '/alert/$alertId',
      useUniversalLink: useUniversalLink,
    );
  }

  /// Build a password reset deep link
  static String passwordReset({
    required String token,
    String? email,
    bool useUniversalLink = true,
  }) {
    return _build(
      path: '/reset-password',
      queryParams: {
        'token': token,
        if (email != null) 'email': email,
      },
      useUniversalLink: useUniversalLink,
    );
  }

  /// Build an OTP verification deep link
  static String verifyOtp({
    required String identifier,
    required String purpose,
    String? otp,
    String? sessionId,
    bool useUniversalLink = true,
  }) {
    return _build(
      path: '/verify-otp',
      queryParams: {
        'identifier': identifier,
        'purpose': purpose,
        if (otp != null) 'otp': otp,
        if (sessionId != null) 'session_id': sessionId,
      },
      useUniversalLink: useUniversalLink,
    );
  }

  /// Internal builder method
  static String _build({
    required String path,
    Map<String, String>? queryParams,
    bool useUniversalLink = false,
  }) {
    if (useUniversalLink) {
      return Uri.https(
        DeepLinkRoutes.universalLinkHosts.first,
        path,
        queryParams,
      ).toString();
    }

    // For custom scheme, we need to handle the format correctly
    // sahool://field/123 (not sahool:///field/123)
    final pathWithoutLeadingSlash =
        path.startsWith('/') ? path.substring(1) : path;
    final parts = pathWithoutLeadingSlash.split('/');
    final host = parts.isNotEmpty ? parts.first : '';
    final remainingPath = parts.length > 1 ? '/${parts.sublist(1).join('/')}' : '';

    final uri = Uri(
      scheme: DeepLinkRoutes.scheme,
      host: host,
      path: remainingPath,
      queryParameters: queryParams?.isNotEmpty == true ? queryParams : null,
    );

    return uri.toString();
  }
}
