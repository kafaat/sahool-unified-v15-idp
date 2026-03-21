import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'core/config/theme.dart';
import 'core/routes/app_router.dart';
import 'core/auth/auth_service.dart';
import 'generated/l10n/app_localizations.dart';

/// SAHOOL Field App
/// تطبيق سهول الميداني
class SahoolFieldApp extends ConsumerStatefulWidget {
  const SahoolFieldApp({super.key});

  @override
  ConsumerState<SahoolFieldApp> createState() => _SahoolFieldAppState();
}

class _SahoolFieldAppState extends ConsumerState<SahoolFieldApp> {
  @override
  void initState() {
    super.initState();
    // Set system UI overlay style
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
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

      // GoRouter configuration - uses centralized router from app_router.dart
      routerConfig: AppRouter.router,
    );
  }
}

/// Auth Guard Widget
/// يتحقق من حالة المصادقة ويعيد التوجيه للدخول عند الحاجة
///
/// Wrap the root of the app widget tree (in main.dart) or use as a
/// top-level wrapper inside the router to enforce authentication.
class AuthGuard extends ConsumerWidget {
  final Widget child;

  const AuthGuard({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authStateProvider);

    // Still initializing - show splash
    if (authState.status == AuthStatus.initial ||
        authState.status == AuthStatus.loading) {
      return const _SplashScreen();
    }

    // Not authenticated - redirect to login
    if (!authState.isAuthenticated) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (context.mounted) {
          context.go('/login');
        }
      });
      return const _SplashScreen();
    }

    return child;
  }
}

/// Splash Screen while checking auth/onboarding status
/// شاشة البداية أثناء التحقق من حالة المصادقة
class _SplashScreen extends StatelessWidget {
  const _SplashScreen();

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                SahoolTheme.primary,
                Color(0xFF1B4D1B),
              ],
            ),
          ),
          child: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.eco_rounded,
                  size: 80,
                  color: Colors.white,
                ),
                SizedBox(height: 24),
                Text(
                  'سهول',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: 48),
                CircularProgressIndicator(
                  color: Colors.white,
                  strokeWidth: 2,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
