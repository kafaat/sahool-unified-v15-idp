// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOOL ATMOSPHERE - Mobile Application
// تطبيق ساهول أتموسفير للموبايل
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Revolutionary UX Platform for Smart Agriculture
// منصة تجربة مستخدم ثورية للزراعة الذكية
//
// Features:
// - Holographic Field Cards with Gyroscope Parallax
// - Voice-First Interface (Arabic Support)
// - Bio-Luminescent Design Language
// - Haptic Feedback for Actions
// - Device Security Checks
//
// Version: 16.0.0
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'theme/atmosphere_theme.dart';
import 'screens/dashboard_screen.dart';
import 'core/security/device_security.dart';
import 'providers/theme_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Set system UI overlay style for immersive experience
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: AtmosphereColors.bgPrimary,
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  // Force portrait mode for optimal UX
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // Perform security check (non-blocking)
  // فحص الأمان (غير معطل)
  try {
    final securityService = DeviceSecurityService();
    final securityResult = await securityService.checkSecurity();

    if (kDebugMode) {
      debugPrint('🔒 Security Check: $securityResult');
    }

    // In production, handle compromised devices appropriately
    if (securityResult.isCompromised && !kDebugMode) {
      debugPrint('⚠️ Warning: Running on compromised device');
      // Log security event for monitoring
      // TODO: Integrate with analytics/logging service when available
      // Restrict sensitive features (e.g., offline data access, financial transactions)
    }

    if (securityResult.isEmulator && !kDebugMode) {
      debugPrint('⚠️ Warning: Running on emulator in non-debug mode');
    }
  } catch (e) {
    debugPrint('Security check failed: $e');
  }

  runApp(
    const ProviderScope(
      child: SahoolAtmosphereApp(),
    ),
  );
}

/// Main Application Widget
/// التطبيق الرئيسي
class SahoolAtmosphereApp extends ConsumerWidget {
  const SahoolAtmosphereApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch the theme mode provider
    // مراقبة مزود وضع الثيم
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp(
      title: 'ساهول أتموسفير',
      debugShowCheckedModeBanner: false,

      // Theme Configuration - supports light/dark/system
      // تكوين الثيم - يدعم النهاري/الليلي/النظام
      theme: AtmosphereTheme.lightTheme,
      darkTheme: AtmosphereTheme.darkTheme,
      themeMode: themeMode, // Follows user preference or system setting

      // Localization
      locale: const Locale('ar', 'SA'),
      supportedLocales: const [
        Locale('ar', 'SA'),
        Locale('ar', 'YE'),
        Locale('en', 'US'),
      ],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],

      // Home Screen
      home: const DashboardScreen(),
    );
  }
}
