/// SAHOOL Authentication Service
/// خدمة التوثيق والمصادقة
///
/// Handles user authentication, token storage, and logout

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// مفاتيح التخزين
class AuthKeys {
  static const String accessToken = 'sahool_access_token';
  static const String refreshToken = 'sahool_refresh_token';
  static const String userId = 'sahool_user_id';
  static const String userName = 'sahool_user_name';
  static const String userEmail = 'sahool_user_email';
  static const String userRole = 'sahool_user_role';
  static const String tenantId = 'sahool_tenant_id';
  static const String isLoggedIn = 'sahool_is_logged_in';
}

/// حالة المستخدم
class AuthState {
  final bool isLoggedIn;
  final String? userId;
  final String? userName;
  final String? userEmail;
  final String? accessToken;
  final String? tenantId;

  const AuthState({
    this.isLoggedIn = false,
    this.userId,
    this.userName,
    this.userEmail,
    this.accessToken,
    this.tenantId,
  });

  AuthState copyWith({
    bool? isLoggedIn,
    String? userId,
    String? userName,
    String? userEmail,
    String? accessToken,
    String? tenantId,
  }) {
    return AuthState(
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      userId: userId ?? this.userId,
      userName: userName ?? this.userName,
      userEmail: userEmail ?? this.userEmail,
      accessToken: accessToken ?? this.accessToken,
      tenantId: tenantId ?? this.tenantId,
    );
  }

  static const AuthState initial = AuthState();
}

/// مزود حالة المصادقة
class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(AuthState.initial) {
    _loadStoredAuth();
  }

  /// تحميل بيانات المصادقة المخزنة
  Future<void> _loadStoredAuth() async {
    final prefs = await SharedPreferences.getInstance();

    final isLoggedIn = prefs.getBool(AuthKeys.isLoggedIn) ?? false;

    if (isLoggedIn) {
      state = AuthState(
        isLoggedIn: true,
        userId: prefs.getString(AuthKeys.userId),
        userName: prefs.getString(AuthKeys.userName),
        userEmail: prefs.getString(AuthKeys.userEmail),
        accessToken: prefs.getString(AuthKeys.accessToken),
        tenantId: prefs.getString(AuthKeys.tenantId),
      );
    }
  }

  /// تسجيل الدخول
  Future<void> login({
    required String accessToken,
    String? refreshToken,
    required String userId,
    required String userName,
    String? userEmail,
    String? tenantId,
  }) async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.setString(AuthKeys.accessToken, accessToken);
    if (refreshToken != null) {
      await prefs.setString(AuthKeys.refreshToken, refreshToken);
    }
    await prefs.setString(AuthKeys.userId, userId);
    await prefs.setString(AuthKeys.userName, userName);
    if (userEmail != null) {
      await prefs.setString(AuthKeys.userEmail, userEmail);
    }
    if (tenantId != null) {
      await prefs.setString(AuthKeys.tenantId, tenantId);
    }
    await prefs.setBool(AuthKeys.isLoggedIn, true);

    state = AuthState(
      isLoggedIn: true,
      userId: userId,
      userName: userName,
      userEmail: userEmail,
      accessToken: accessToken,
      tenantId: tenantId,
    );
  }

  /// تسجيل الخروج
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();

    // مسح جميع بيانات المصادقة
    await prefs.remove(AuthKeys.accessToken);
    await prefs.remove(AuthKeys.refreshToken);
    await prefs.remove(AuthKeys.userId);
    await prefs.remove(AuthKeys.userName);
    await prefs.remove(AuthKeys.userEmail);
    await prefs.remove(AuthKeys.userRole);
    await prefs.remove(AuthKeys.tenantId);
    await prefs.setBool(AuthKeys.isLoggedIn, false);

    state = AuthState.initial;
  }

  /// الحصول على التوكن
  String? get accessToken => state.accessToken;

  /// التحقق من حالة تسجيل الدخول
  bool get isLoggedIn => state.isLoggedIn;
}

/// مزود المصادقة
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});

/// مزود حالة تسجيل الدخول
final isLoggedInProvider = Provider<bool>((ref) {
  return ref.watch(authProvider).isLoggedIn;
});

/// مزود اسم المستخدم
final currentUserNameProvider = Provider<String?>((ref) {
  return ref.watch(authProvider).userName;
});
