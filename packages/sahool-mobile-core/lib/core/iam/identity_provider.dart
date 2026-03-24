/// SAHOOL Identity Provider
/// مزودو الهوية
///
/// Support for multiple identity providers including:
/// - Local authentication | المصادقة المحلية
/// - OAuth 2.0 / OpenID Connect | OAuth 2.0 / OIDC
/// - Social login (Google, Apple) | تسجيل الدخول الاجتماعي
///
/// This module provides a unified interface for authentication
/// across different identity providers while maintaining security
/// and supporting offline-first architecture.
library;

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:crypto/crypto.dart';

import '../utils/app_logger.dart';
import 'models/iam_models.dart';

// =============================================================================
// Identity Provider Types
// أنواع مزودي الهوية
// =============================================================================

/// Supported identity provider types
/// أنواع مزودي الهوية المدعومة
enum IdentityProviderType {
  /// Local username/password authentication | المصادقة المحلية
  local('local', 'Local', 'محلي'),

  /// SAHOOL backend authentication | مصادقة خادم سهول
  sahool('sahool', 'SAHOOL', 'سهول'),

  /// OAuth 2.0 provider | مزود OAuth 2.0
  oauth2('oauth2', 'OAuth 2.0', 'OAuth 2.0'),

  /// OpenID Connect provider | مزود OIDC
  oidc('oidc', 'OpenID Connect', 'OpenID Connect'),

  /// Google Sign-In | تسجيل الدخول بجوجل
  google('google', 'Google', 'جوجل'),

  /// Apple Sign-In | تسجيل الدخول بأبل
  apple('apple', 'Apple', 'أبل'),

  /// Microsoft Azure AD | مايكروسوفت أزور
  azureAd('azure_ad', 'Microsoft', 'مايكروسوفت'),

  /// SAML 2.0 provider | مزود SAML 2.0
  saml('saml', 'SAML 2.0', 'SAML 2.0');

  final String code;
  final String label;
  final String labelAr;

  const IdentityProviderType(this.code, this.label, this.labelAr);

  String getLabel({String locale = 'ar'}) {
    return locale == 'ar' ? labelAr : label;
  }

  static IdentityProviderType fromCode(String code) {
    return IdentityProviderType.values.firstWhere(
      (t) => t.code == code,
      orElse: () => IdentityProviderType.local,
    );
  }
}

// =============================================================================
// OAuth 2.0 / OIDC Configuration
// إعدادات OAuth 2.0 / OIDC
// =============================================================================

/// OAuth 2.0 configuration
/// إعدادات OAuth 2.0
@immutable
class OAuth2Config {
  /// Authorization endpoint | نقطة نهاية التفويض
  final String authorizationEndpoint;

  /// Token endpoint | نقطة نهاية التوكن
  final String tokenEndpoint;

  /// User info endpoint | نقطة نهاية معلومات المستخدم
  final String? userInfoEndpoint;

  /// Revocation endpoint | نقطة نهاية الإلغاء
  final String? revocationEndpoint;

  /// End session endpoint | نقطة نهاية إنهاء الجلسة
  final String? endSessionEndpoint;

  /// Client ID | معرف العميل
  final String clientId;

  /// Client secret (optional for PKCE) | سر العميل
  final String? clientSecret;

  /// Redirect URI | عنوان إعادة التوجيه
  final String redirectUri;

  /// Scopes to request | النطاقات المطلوبة
  final List<String> scopes;

  /// Use PKCE (Proof Key for Code Exchange) | استخدام PKCE
  final bool usePKCE;

  /// Custom parameters | معلمات مخصصة
  final Map<String, String>? customParameters;

  const OAuth2Config({
    required this.authorizationEndpoint,
    required this.tokenEndpoint,
    this.userInfoEndpoint,
    this.revocationEndpoint,
    this.endSessionEndpoint,
    required this.clientId,
    this.clientSecret,
    required this.redirectUri,
    this.scopes = const ['openid', 'profile', 'email'],
    this.usePKCE = true,
    this.customParameters,
  });

  factory OAuth2Config.fromJson(Map<String, dynamic> json) {
    return OAuth2Config(
      authorizationEndpoint: json['authorization_endpoint'] as String,
      tokenEndpoint: json['token_endpoint'] as String,
      userInfoEndpoint: json['userinfo_endpoint'] as String?,
      revocationEndpoint: json['revocation_endpoint'] as String?,
      endSessionEndpoint: json['end_session_endpoint'] as String?,
      clientId: json['client_id'] as String,
      clientSecret: json['client_secret'] as String?,
      redirectUri: json['redirect_uri'] as String,
      scopes: (json['scopes'] as List<dynamic>?)?.cast<String>() ?? ['openid', 'profile', 'email'],
      usePKCE: json['use_pkce'] as bool? ?? true,
      customParameters: (json['custom_parameters'] as Map<String, dynamic>?)?.cast<String, String>(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'authorization_endpoint': authorizationEndpoint,
      'token_endpoint': tokenEndpoint,
      'userinfo_endpoint': userInfoEndpoint,
      'revocation_endpoint': revocationEndpoint,
      'end_session_endpoint': endSessionEndpoint,
      'client_id': clientId,
      'client_secret': clientSecret,
      'redirect_uri': redirectUri,
      'scopes': scopes,
      'use_pkce': usePKCE,
      'custom_parameters': customParameters,
    };
  }
}

/// OIDC configuration extends OAuth2 with discovery
/// إعدادات OIDC تمتد على OAuth2 مع الاكتشاف
@immutable
class OIDCConfig extends OAuth2Config {
  /// Issuer URL | عنوان المُصدر
  final String issuer;

  /// JWKS URI for token validation | عنوان JWKS للتحقق من التوكن
  final String? jwksUri;

  /// ID token signing algorithm | خوارزمية توقيع توكن الهوية
  final String idTokenSigningAlg;

  const OIDCConfig({
    required this.issuer,
    this.jwksUri,
    this.idTokenSigningAlg = 'RS256',
    required super.authorizationEndpoint,
    required super.tokenEndpoint,
    super.userInfoEndpoint,
    super.revocationEndpoint,
    super.endSessionEndpoint,
    required super.clientId,
    super.clientSecret,
    required super.redirectUri,
    super.scopes = const ['openid', 'profile', 'email'],
    super.usePKCE = true,
    super.customParameters,
  });

  factory OIDCConfig.fromJson(Map<String, dynamic> json) {
    return OIDCConfig(
      issuer: json['issuer'] as String,
      jwksUri: json['jwks_uri'] as String?,
      idTokenSigningAlg: json['id_token_signing_alg'] as String? ?? 'RS256',
      authorizationEndpoint: json['authorization_endpoint'] as String,
      tokenEndpoint: json['token_endpoint'] as String,
      userInfoEndpoint: json['userinfo_endpoint'] as String?,
      revocationEndpoint: json['revocation_endpoint'] as String?,
      endSessionEndpoint: json['end_session_endpoint'] as String?,
      clientId: json['client_id'] as String,
      clientSecret: json['client_secret'] as String?,
      redirectUri: json['redirect_uri'] as String,
      scopes: (json['scopes'] as List<dynamic>?)?.cast<String>() ?? ['openid', 'profile', 'email'],
      usePKCE: json['use_pkce'] as bool? ?? true,
      customParameters: (json['custom_parameters'] as Map<String, dynamic>?)?.cast<String, String>(),
    );
  }

  @override
  Map<String, dynamic> toJson() {
    return {
      ...super.toJson(),
      'issuer': issuer,
      'jwks_uri': jwksUri,
      'id_token_signing_alg': idTokenSigningAlg,
    };
  }
}

// =============================================================================
// Social Login Configuration
// إعدادات تسجيل الدخول الاجتماعي
// =============================================================================

/// Google Sign-In configuration
/// إعدادات تسجيل الدخول بجوجل
@immutable
class GoogleSignInConfig {
  /// iOS Client ID | معرف عميل iOS
  final String? iosClientId;

  /// Android Client ID | معرف عميل أندرويد
  final String? androidClientId;

  /// Web Client ID | معرف عميل الويب
  final String? webClientId;

  /// Server Client ID for backend verification | معرف عميل الخادم
  final String serverClientId;

  /// Scopes to request | النطاقات المطلوبة
  final List<String> scopes;

  /// Request offline access (refresh token) | طلب الوصول بدون اتصال
  final bool requestOfflineAccess;

  const GoogleSignInConfig({
    this.iosClientId,
    this.androidClientId,
    this.webClientId,
    required this.serverClientId,
    this.scopes = const ['email', 'profile'],
    this.requestOfflineAccess = true,
  });

  factory GoogleSignInConfig.fromJson(Map<String, dynamic> json) {
    return GoogleSignInConfig(
      iosClientId: json['ios_client_id'] as String?,
      androidClientId: json['android_client_id'] as String?,
      webClientId: json['web_client_id'] as String?,
      serverClientId: json['server_client_id'] as String,
      scopes: (json['scopes'] as List<dynamic>?)?.cast<String>() ?? ['email', 'profile'],
      requestOfflineAccess: json['request_offline_access'] as bool? ?? true,
    );
  }
}

/// Apple Sign-In configuration
/// إعدادات تسجيل الدخول بأبل
@immutable
class AppleSignInConfig {
  /// Service ID | معرف الخدمة
  final String serviceId;

  /// Team ID | معرف الفريق
  final String teamId;

  /// Key ID | معرف المفتاح
  final String keyId;

  /// Redirect URI | عنوان إعادة التوجيه
  final String redirectUri;

  /// Scopes to request | النطاقات المطلوبة
  final List<String> scopes;

  const AppleSignInConfig({
    required this.serviceId,
    required this.teamId,
    required this.keyId,
    required this.redirectUri,
    this.scopes = const ['email', 'name'],
  });

  factory AppleSignInConfig.fromJson(Map<String, dynamic> json) {
    return AppleSignInConfig(
      serviceId: json['service_id'] as String,
      teamId: json['team_id'] as String,
      keyId: json['key_id'] as String,
      redirectUri: json['redirect_uri'] as String,
      scopes: (json['scopes'] as List<dynamic>?)?.cast<String>() ?? ['email', 'name'],
    );
  }
}

// =============================================================================
// Authentication Result
// نتيجة المصادقة
// =============================================================================

/// Authentication result from identity provider
/// نتيجة المصادقة من مزود الهوية
@immutable
class AuthenticationResult {
  /// Whether authentication was successful | هل نجحت المصادقة
  final bool success;

  /// Access token | توكن الوصول
  final String? accessToken;

  /// Refresh token | توكن التحديث
  final String? refreshToken;

  /// ID token (for OIDC) | توكن الهوية
  final String? idToken;

  /// Token expiry | انتهاء صلاحية التوكن
  final DateTime? expiresAt;

  /// User identity | هوية المستخدم
  final UserIdentity? user;

  /// Error message (if failed) | رسالة الخطأ
  final String? error;

  /// Error in Arabic | الخطأ بالعربية
  final String? errorAr;

  /// Identity provider type | نوع مزود الهوية
  final IdentityProviderType providerType;

  /// Raw provider response | استجابة المزود الخام
  final Map<String, dynamic>? rawResponse;

  /// Whether MFA is required | هل المصادقة الثنائية مطلوبة
  final bool mfaRequired;

  /// MFA challenge data | بيانات تحدي MFA
  final Map<String, dynamic>? mfaChallenge;

  const AuthenticationResult({
    required this.success,
    this.accessToken,
    this.refreshToken,
    this.idToken,
    this.expiresAt,
    this.user,
    this.error,
    this.errorAr,
    required this.providerType,
    this.rawResponse,
    this.mfaRequired = false,
    this.mfaChallenge,
  });

  /// Create successful result
  factory AuthenticationResult.success({
    required String accessToken,
    String? refreshToken,
    String? idToken,
    required DateTime expiresAt,
    required UserIdentity user,
    required IdentityProviderType providerType,
    Map<String, dynamic>? rawResponse,
  }) {
    return AuthenticationResult(
      success: true,
      accessToken: accessToken,
      refreshToken: refreshToken,
      idToken: idToken,
      expiresAt: expiresAt,
      user: user,
      providerType: providerType,
      rawResponse: rawResponse,
    );
  }

  /// Create failed result
  factory AuthenticationResult.failure({
    required String error,
    String? errorAr,
    required IdentityProviderType providerType,
    Map<String, dynamic>? rawResponse,
  }) {
    return AuthenticationResult(
      success: false,
      error: error,
      errorAr: errorAr ?? error,
      providerType: providerType,
      rawResponse: rawResponse,
    );
  }

  /// Create MFA required result
  factory AuthenticationResult.mfaRequired({
    required IdentityProviderType providerType,
    required Map<String, dynamic> mfaChallenge,
  }) {
    return AuthenticationResult(
      success: false,
      providerType: providerType,
      mfaRequired: true,
      mfaChallenge: mfaChallenge,
    );
  }

  String getLocalizedError({String locale = 'ar'}) {
    return locale == 'ar' ? (errorAr ?? error ?? '') : (error ?? '');
  }
}

// =============================================================================
// Identity Provider Interface
// واجهة مزود الهوية
// =============================================================================

/// Abstract identity provider interface
/// واجهة مزود الهوية المجردة
abstract class IdentityProvider {
  /// Provider type | نوع المزود
  IdentityProviderType get type;

  /// Provider display name | اسم المزود المعروض
  String get displayName;

  /// Provider display name in Arabic | اسم المزود بالعربية
  String get displayNameAr;

  /// Whether provider is available | هل المزود متاح
  Future<bool> isAvailable();

  /// Authenticate with the provider | المصادقة مع المزود
  Future<AuthenticationResult> authenticate({
    Map<String, dynamic>? parameters,
  });

  /// Refresh access token | تحديث توكن الوصول
  Future<AuthenticationResult> refreshToken({
    required String refreshToken,
  });

  /// Sign out from the provider | تسجيل الخروج من المزود
  Future<void> signOut();

  /// Get user info | الحصول على معلومات المستخدم
  Future<UserIdentity?> getUserInfo({
    required String accessToken,
  });
}

// =============================================================================
// SAHOOL Identity Provider (Local Backend)
// مزود هوية سهول (الخادم المحلي)
// =============================================================================

/// SAHOOL backend identity provider
/// مزود هوية خادم سهول
class SahoolIdentityProvider implements IdentityProvider {
  /// API base URL | عنوان API الأساسي
  final String apiBaseUrl;

  /// HTTP client function | دالة عميل HTTP
  final Future<Map<String, dynamic>> Function(
    String method,
    String url,
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  ) httpClient;

  SahoolIdentityProvider({
    required this.apiBaseUrl,
    required this.httpClient,
  });

  @override
  IdentityProviderType get type => IdentityProviderType.sahool;

  @override
  String get displayName => 'SAHOOL';

  @override
  String get displayNameAr => 'سهول';

  @override
  Future<bool> isAvailable() async {
    try {
      final response = await httpClient(
        'GET',
        '$apiBaseUrl/health',
        null,
        null,
      );
      return response['status'] == 'ok';
    } catch (e) {
      AppLogger.e('SAHOOL provider availability check failed', tag: 'IDP', error: e);
      return false;
    }
  }

  @override
  Future<AuthenticationResult> authenticate({
    Map<String, dynamic>? parameters,
  }) async {
    try {
      final username = parameters?['username'] as String?;
      final password = parameters?['password'] as String?;
      final tenantId = parameters?['tenant_id'] as String?;

      if (username == null || password == null) {
        return AuthenticationResult.failure(
          error: 'Username and password are required',
          errorAr: 'اسم المستخدم وكلمة المرور مطلوبان',
          providerType: type,
        );
      }

      final response = await httpClient(
        'POST',
        '$apiBaseUrl/auth/login',
        {
          'username': username,
          'password': password,
          if (tenantId != null) 'tenant_id': tenantId,
        },
        {'Content-Type': 'application/json'},
      );

      // Check for MFA requirement
      if (response['mfa_required'] == true) {
        return AuthenticationResult.mfaRequired(
          providerType: type,
          mfaChallenge: response['mfa_challenge'] as Map<String, dynamic>? ?? {},
        );
      }

      final accessToken = response['access_token'] as String?;
      final refreshToken = response['refresh_token'] as String?;
      final expiresIn = response['expires_in'] as int? ?? 900;
      final userData = response['user'] as Map<String, dynamic>?;

      if (accessToken == null || userData == null) {
        return AuthenticationResult.failure(
          error: response['error'] as String? ?? 'Authentication failed',
          errorAr: response['error_ar'] as String? ?? 'فشلت المصادقة',
          providerType: type,
          rawResponse: response,
        );
      }

      final user = UserIdentity.fromJson(userData);
      final expiresAt = DateTime.now().add(Duration(seconds: expiresIn));

      AppLogger.i('SAHOOL authentication successful for user: ${user.id}', tag: 'IDP');

      return AuthenticationResult.success(
        accessToken: accessToken,
        refreshToken: refreshToken,
        expiresAt: expiresAt,
        user: user,
        providerType: type,
        rawResponse: response,
      );
    } catch (e, stack) {
      AppLogger.e('SAHOOL authentication failed', tag: 'IDP', error: e, stackTrace: stack);
      return AuthenticationResult.failure(
        error: 'Authentication error: ${e.toString()}',
        errorAr: 'خطأ في المصادقة',
        providerType: type,
      );
    }
  }

  @override
  Future<AuthenticationResult> refreshToken({
    required String refreshToken,
  }) async {
    try {
      final response = await httpClient(
        'POST',
        '$apiBaseUrl/auth/refresh',
        {'refresh_token': refreshToken},
        {'Content-Type': 'application/json'},
      );

      final accessToken = response['access_token'] as String?;
      final newRefreshToken = response['refresh_token'] as String? ?? refreshToken;
      final expiresIn = response['expires_in'] as int? ?? 900;

      if (accessToken == null) {
        return AuthenticationResult.failure(
          error: 'Token refresh failed',
          errorAr: 'فشل تحديث التوكن',
          providerType: type,
          rawResponse: response,
        );
      }

      final expiresAt = DateTime.now().add(Duration(seconds: expiresIn));

      AppLogger.i('SAHOOL token refresh successful', tag: 'IDP');

      return AuthenticationResult(
        success: true,
        accessToken: accessToken,
        refreshToken: newRefreshToken,
        expiresAt: expiresAt,
        providerType: type,
        rawResponse: response,
      );
    } catch (e, stack) {
      AppLogger.e('SAHOOL token refresh failed', tag: 'IDP', error: e, stackTrace: stack);
      return AuthenticationResult.failure(
        error: 'Token refresh error',
        errorAr: 'خطأ في تحديث التوكن',
        providerType: type,
      );
    }
  }

  @override
  Future<void> signOut() async {
    // SAHOOL backend handles token revocation
    AppLogger.i('SAHOOL sign out completed', tag: 'IDP');
  }

  @override
  Future<UserIdentity?> getUserInfo({
    required String accessToken,
  }) async {
    try {
      final response = await httpClient(
        'GET',
        '$apiBaseUrl/auth/me',
        null,
        {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );

      return UserIdentity.fromJson(response);
    } catch (e) {
      AppLogger.e('Failed to get user info', tag: 'IDP', error: e);
      return null;
    }
  }

  /// Complete MFA challenge | إكمال تحدي MFA
  Future<AuthenticationResult> completeMfaChallenge({
    required String challengeId,
    required String code,
  }) async {
    try {
      final response = await httpClient(
        'POST',
        '$apiBaseUrl/auth/mfa/verify',
        {
          'challenge_id': challengeId,
          'code': code,
        },
        {'Content-Type': 'application/json'},
      );

      final accessToken = response['access_token'] as String?;
      final refreshToken = response['refresh_token'] as String?;
      final expiresIn = response['expires_in'] as int? ?? 900;
      final userData = response['user'] as Map<String, dynamic>?;

      if (accessToken == null || userData == null) {
        return AuthenticationResult.failure(
          error: response['error'] as String? ?? 'MFA verification failed',
          errorAr: response['error_ar'] as String? ?? 'فشل التحقق من MFA',
          providerType: type,
          rawResponse: response,
        );
      }

      final user = UserIdentity.fromJson(userData);
      final expiresAt = DateTime.now().add(Duration(seconds: expiresIn));

      return AuthenticationResult.success(
        accessToken: accessToken,
        refreshToken: refreshToken,
        expiresAt: expiresAt,
        user: user,
        providerType: type,
        rawResponse: response,
      );
    } catch (e) {
      AppLogger.e('MFA verification failed', tag: 'IDP', error: e);
      return AuthenticationResult.failure(
        error: 'MFA verification error',
        errorAr: 'خطأ في التحقق من MFA',
        providerType: type,
      );
    }
  }
}

// =============================================================================
// OAuth 2.0 Identity Provider
// مزود هوية OAuth 2.0
// =============================================================================

/// Generic OAuth 2.0 identity provider
/// مزود هوية OAuth 2.0 العام
class OAuth2IdentityProvider implements IdentityProvider {
  final OAuth2Config config;
  final String providerName;
  final String providerNameAr;

  /// PKCE code verifier (temporary, for current auth flow)
  String? _codeVerifier;

  OAuth2IdentityProvider({
    required this.config,
    this.providerName = 'OAuth 2.0',
    this.providerNameAr = 'OAuth 2.0',
  });

  @override
  IdentityProviderType get type => IdentityProviderType.oauth2;

  @override
  String get displayName => providerName;

  @override
  String get displayNameAr => providerNameAr;

  @override
  Future<bool> isAvailable() async {
    // OAuth providers are generally always available
    return true;
  }

  /// Generate authorization URL | إنشاء رابط التفويض
  String generateAuthorizationUrl({String? state, String? nonce}) {
    final params = <String, String>{
      'response_type': 'code',
      'client_id': config.clientId,
      'redirect_uri': config.redirectUri,
      'scope': config.scopes.join(' '),
    };

    if (state != null) {
      params['state'] = state;
    }

    if (config.usePKCE) {
      _codeVerifier = _generateCodeVerifier();
      params['code_challenge'] = _generateCodeChallenge(_codeVerifier!);
      params['code_challenge_method'] = 'S256';
    }

    if (config.customParameters != null) {
      params.addAll(config.customParameters!);
    }

    final queryString = params.entries.map((e) => '${e.key}=${Uri.encodeComponent(e.value)}').join('&');

    return '${config.authorizationEndpoint}?$queryString';
  }

  @override
  Future<AuthenticationResult> authenticate({
    Map<String, dynamic>? parameters,
  }) async {
    // OAuth2 authentication is typically handled via redirect
    // This method would be called after receiving the authorization code
    final authorizationCode = parameters?['code'] as String?;

    if (authorizationCode == null) {
      return AuthenticationResult.failure(
        error: 'Authorization code is required',
        errorAr: 'رمز التفويض مطلوب',
        providerType: type,
      );
    }

    return exchangeCodeForTokens(authorizationCode);
  }

  /// Exchange authorization code for tokens | استبدال رمز التفويض بالتوكنات
  Future<AuthenticationResult> exchangeCodeForTokens(String code) async {
    try {
      final body = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': config.clientId,
        'redirect_uri': config.redirectUri,
      };

      if (config.clientSecret != null) {
        body['client_secret'] = config.clientSecret!;
      }

      if (config.usePKCE && _codeVerifier != null) {
        body['code_verifier'] = _codeVerifier!;
      }

      // This would need an actual HTTP client implementation
      // For now, returning a placeholder
      AppLogger.i('OAuth2 code exchange initiated', tag: 'IDP');

      // Clear code verifier after use
      _codeVerifier = null;

      return AuthenticationResult.failure(
        error: 'OAuth2 flow requires redirect handling',
        errorAr: 'تدفق OAuth2 يتطلب معالجة إعادة التوجيه',
        providerType: type,
      );
    } catch (e) {
      AppLogger.e('OAuth2 token exchange failed', tag: 'IDP', error: e);
      return AuthenticationResult.failure(
        error: 'Token exchange failed',
        errorAr: 'فشل استبدال التوكن',
        providerType: type,
      );
    }
  }

  @override
  Future<AuthenticationResult> refreshToken({
    required String refreshToken,
  }) async {
    try {
      AppLogger.i('OAuth2 token refresh initiated', tag: 'IDP');

      // Would make actual HTTP request to token endpoint
      return AuthenticationResult.failure(
        error: 'Token refresh not implemented',
        errorAr: 'تحديث التوكن غير مُنفذ',
        providerType: type,
      );
    } catch (e) {
      return AuthenticationResult.failure(
        error: 'Token refresh failed',
        errorAr: 'فشل تحديث التوكن',
        providerType: type,
      );
    }
  }

  @override
  Future<void> signOut() async {
    if (config.endSessionEndpoint != null) {
      AppLogger.i('OAuth2 end session initiated', tag: 'IDP');
    }
  }

  @override
  Future<UserIdentity?> getUserInfo({
    required String accessToken,
  }) async {
    if (config.userInfoEndpoint == null) {
      return null;
    }

    try {
      AppLogger.i('Fetching user info from OAuth2 provider', tag: 'IDP');
      // Would make actual HTTP request
      return null;
    } catch (e) {
      AppLogger.e('Failed to get OAuth2 user info', tag: 'IDP', error: e);
      return null;
    }
  }

  /// Generate PKCE code verifier
  String _generateCodeVerifier() {
    final bytes = List<int>.generate(32, (i) => DateTime.now().microsecond % 256);
    return base64UrlEncode(bytes).replaceAll('=', '');
  }

  /// Generate PKCE code challenge
  String _generateCodeChallenge(String verifier) {
    final bytes = utf8.encode(verifier);
    final digest = sha256.convert(bytes);
    return base64UrlEncode(digest.bytes).replaceAll('=', '');
  }
}

// =============================================================================
// Social Login Providers (Stubs)
// مزودو تسجيل الدخول الاجتماعي (أساسات)
// =============================================================================

/// Google Sign-In provider (stub - requires google_sign_in package)
/// مزود تسجيل الدخول بجوجل (أساس - يتطلب حزمة google_sign_in)
class GoogleIdentityProvider implements IdentityProvider {
  final GoogleSignInConfig config;

  GoogleIdentityProvider({required this.config});

  @override
  IdentityProviderType get type => IdentityProviderType.google;

  @override
  String get displayName => 'Google';

  @override
  String get displayNameAr => 'جوجل';

  @override
  Future<bool> isAvailable() async {
    // Would check if Google Play Services are available
    return true;
  }

  @override
  Future<AuthenticationResult> authenticate({
    Map<String, dynamic>? parameters,
  }) async {
    // Implementation would use google_sign_in package
    AppLogger.i('Google Sign-In initiated', tag: 'IDP');
    return AuthenticationResult.failure(
      error: 'Google Sign-In requires google_sign_in package',
      errorAr: 'تسجيل الدخول بجوجل يتطلب حزمة google_sign_in',
      providerType: type,
    );
  }

  @override
  Future<AuthenticationResult> refreshToken({required String refreshToken}) async {
    return AuthenticationResult.failure(
      error: 'Not implemented',
      errorAr: 'غير مُنفذ',
      providerType: type,
    );
  }

  @override
  Future<void> signOut() async {
    AppLogger.i('Google Sign-Out', tag: 'IDP');
  }

  @override
  Future<UserIdentity?> getUserInfo({required String accessToken}) async {
    return null;
  }
}

/// Apple Sign-In provider (stub - requires sign_in_with_apple package)
/// مزود تسجيل الدخول بأبل (أساس - يتطلب حزمة sign_in_with_apple)
class AppleIdentityProvider implements IdentityProvider {
  final AppleSignInConfig config;

  AppleIdentityProvider({required this.config});

  @override
  IdentityProviderType get type => IdentityProviderType.apple;

  @override
  String get displayName => 'Apple';

  @override
  String get displayNameAr => 'أبل';

  @override
  Future<bool> isAvailable() async {
    // Would check platform and iOS version
    return true;
  }

  @override
  Future<AuthenticationResult> authenticate({
    Map<String, dynamic>? parameters,
  }) async {
    // Implementation would use sign_in_with_apple package
    AppLogger.i('Apple Sign-In initiated', tag: 'IDP');
    return AuthenticationResult.failure(
      error: 'Apple Sign-In requires sign_in_with_apple package',
      errorAr: 'تسجيل الدخول بأبل يتطلب حزمة sign_in_with_apple',
      providerType: type,
    );
  }

  @override
  Future<AuthenticationResult> refreshToken({required String refreshToken}) async {
    return AuthenticationResult.failure(
      error: 'Apple does not support token refresh',
      errorAr: 'أبل لا يدعم تحديث التوكن',
      providerType: type,
    );
  }

  @override
  Future<void> signOut() async {
    AppLogger.i('Apple Sign-Out', tag: 'IDP');
  }

  @override
  Future<UserIdentity?> getUserInfo({required String accessToken}) async {
    return null;
  }
}

// =============================================================================
// Identity Provider Registry
// سجل مزودي الهوية
// =============================================================================

/// Registry for managing multiple identity providers
/// سجل لإدارة مزودي هوية متعددين
class IdentityProviderRegistry {
  final Map<IdentityProviderType, IdentityProvider> _providers = {};

  /// Default provider type | نوع المزود الافتراضي
  IdentityProviderType _defaultProviderType = IdentityProviderType.sahool;

  /// Register an identity provider | تسجيل مزود هوية
  void register(IdentityProvider provider) {
    _providers[provider.type] = provider;
    AppLogger.i('Registered identity provider: ${provider.type.code}', tag: 'IDP');
  }

  /// Unregister an identity provider | إلغاء تسجيل مزود هوية
  void unregister(IdentityProviderType type) {
    _providers.remove(type);
    AppLogger.i('Unregistered identity provider: ${type.code}', tag: 'IDP');
  }

  /// Get provider by type | الحصول على المزود حسب النوع
  IdentityProvider? getProvider(IdentityProviderType type) {
    return _providers[type];
  }

  /// Get default provider | الحصول على المزود الافتراضي
  IdentityProvider? get defaultProvider => _providers[_defaultProviderType];

  /// Set default provider type | تعيين نوع المزود الافتراضي
  void setDefaultProvider(IdentityProviderType type) {
    if (_providers.containsKey(type)) {
      _defaultProviderType = type;
    }
  }

  /// Get all registered providers | الحصول على جميع المزودين المسجلين
  List<IdentityProvider> get allProviders => _providers.values.toList();

  /// Get available providers | الحصول على المزودين المتاحين
  Future<List<IdentityProvider>> getAvailableProviders() async {
    final available = <IdentityProvider>[];
    for (final provider in _providers.values) {
      if (await provider.isAvailable()) {
        available.add(provider);
      }
    }
    return available;
  }

  /// Check if provider is registered | التحقق مما إذا كان المزود مسجلاً
  bool hasProvider(IdentityProviderType type) {
    return _providers.containsKey(type);
  }
}
