import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/config/theme.dart';
import 'core/routes/app_router.dart';
import 'features/settings/state/settings_providers.dart';
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
    final router = ref.watch(appRouterProvider);

    return MaterialApp.router(
      title: 'سهول',
      debugShowCheckedModeBanner: false,

      // Arabic RTL Support with generated localizations
      locale: const Locale('ar'),
      supportedLocales: AppLocalizations.supportedLocales,
      localizationsDelegates: AppLocalizations.localizationsDelegates,

      // Theme — reactive to user setting, defaults to dark
      theme: SahoolTheme.light,
      darkTheme: SahoolTheme.dark,
      themeMode: ref.watch(themeModeProvider),

      // GoRouter - centralized routing with auth redirect from app_router.dart
      routerConfig: router,
    );
  }
}
