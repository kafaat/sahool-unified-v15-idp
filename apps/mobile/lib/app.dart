import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'core/config/theme.dart';
import 'core/routes/app_router.dart';
import 'core/auth/auth_service.dart';
import 'generated/l10n/app_localizations.dart';

/// SAHOOL Field App - تطبيق سهول الميداني
///
/// Uses GoRouter (MaterialApp.router) with centralized route definitions
/// from [AppRouter]. Auth state is monitored reactively and redirects
/// to login when the user is unauthenticated.
class SahoolFieldApp extends ConsumerStatefulWidget {
  const SahoolFieldApp({super.key});

  @override
  ConsumerState<SahoolFieldApp> createState() => _SahoolFieldAppState();
}

class _SahoolFieldAppState extends ConsumerState<SahoolFieldApp> {
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
    ref.listen<AuthState>(authStateProvider, (previous, next) {
      _handleAuthStateChange(previous, next);
    });

    return MaterialApp.router(
      title: 'سهول',
      debugShowCheckedModeBanner: false,

      // Arabic RTL Support with generated localizations
      locale: const Locale('ar'),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: AppLocalizations.localizationsDelegates,

      // Theme
      theme: SahoolTheme.light,
      darkTheme: SahoolTheme.dark,
      themeMode: ThemeMode.system,

      // GoRouter - centralized routing from app_router.dart
      routerConfig: AppRouter.router,
    );
  }

  /// Handles auth state transitions:
  /// - When user becomes unauthenticated -> redirect to /login
  /// - When user becomes authenticated from login -> redirect to /home
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
