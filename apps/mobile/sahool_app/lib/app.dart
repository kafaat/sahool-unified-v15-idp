import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_mobile_core/core/config/theme.dart';
import 'package:sahool_mobile_core/core/routes/app_router.dart';
import 'package:sahool_mobile_core/core/auth/auth_service.dart';
import 'package:sahool_mobile_core/generated/l10n/app_localizations.dart';

/// SAHOOL Unified App - تطبيق سهول الموحد
///
/// Uses GoRouter (MaterialApp.router) with centralized route definitions
/// from [AppRouter]. Auth state is monitored reactively and redirects
/// to login when the user is unauthenticated.
///
/// يستخدم GoRouter مع تعريفات المسارات المركزية من [AppRouter].
/// تتم مراقبة حالة المصادقة بشكل تفاعلي ويتم التوجيه
/// إلى تسجيل الدخول عندما يكون المستخدم غير مصادق.
class SahoolApp extends ConsumerStatefulWidget {
  const SahoolApp({super.key});

  @override
  ConsumerState<SahoolApp> createState() => _SahoolAppState();
}

class _SahoolAppState extends ConsumerState<SahoolApp> {
  @override
  void initState() {
    super.initState();
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Watch auth state for reactive redirects
    // مراقبة حالة المصادقة لإعادة التوجيه التفاعلي
    ref.listen<AuthState>(authStateProvider, (previous, next) {
      _handleAuthStateChange(previous, next);
    });

    return MaterialApp.router(
      title: 'سهول',
      debugShowCheckedModeBanner: false,

      // Arabic RTL Support with generated localizations
      // دعم العربية RTL مع الترجمات المولّدة
      locale: const Locale('ar'),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: AppLocalizations.localizationsDelegates,

      // Theme - السمة
      theme: SahoolTheme.light,
      darkTheme: SahoolTheme.dark,
      themeMode: ThemeMode.system,

      // GoRouter - centralized routing from app_router.dart
      // GoRouter - التوجيه المركزي من app_router.dart
      routerConfig: AppRouter.router,
    );
  }

  /// Handles auth state transitions:
  /// - When user becomes unauthenticated -> redirect to /login
  /// - When user becomes authenticated from login -> redirect to /home
  ///
  /// معالجة انتقالات حالة المصادقة:
  /// - عندما يصبح المستخدم غير مصادق -> التوجيه إلى /login
  /// - عندما يصبح المستخدم مصادقاً من تسجيل الدخول -> التوجيه إلى /home
  void _handleAuthStateChange(AuthState? previous, AuthState next) {
    final wasAuthenticated = previous?.isAuthenticated ?? false;
    final isAuthenticated = next.isAuthenticated;

    if (wasAuthenticated && !isAuthenticated) {
      // User logged out or session expired - go to login
      AppRouter.router.go('/login');
    } else if (!wasAuthenticated &&
        isAuthenticated &&
        previous?.status != AuthStatus.initial) {
      // User just logged in - go to home
      AppRouter.router.go('/home');
    }
  }
}
