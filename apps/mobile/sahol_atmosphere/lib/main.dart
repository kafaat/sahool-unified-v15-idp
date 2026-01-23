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

    // In production, you might want to handle compromised devices
    if (securityResult.isCompromised && !kDebugMode) {
      debugPrint('⚠️ Warning: Running on compromised device');
      // Optionally show warning or restrict features
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
    return MaterialApp(
      title: 'ساهول أتموسفير',
      debugShowCheckedModeBanner: false,

      // Theme Configuration
      theme: AtmosphereTheme.darkTheme,
      darkTheme: AtmosphereTheme.darkTheme,
      themeMode: ThemeMode.dark, // Always dark for battery saving in sunlight

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
