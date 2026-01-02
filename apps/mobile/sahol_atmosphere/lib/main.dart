// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Mobile Application
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
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'theme/atmosphere_theme.dart';
import 'screens/dashboard_screen.dart';

void main() {
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
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(const SaholAtmosphereApp());
}

/// Main Application Widget
class SaholAtmosphereApp extends StatelessWidget {
  const SaholAtmosphereApp({super.key});

  @override
  Widget build(BuildContext context) {
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
        Locale('en', 'US'),
      ],

      // Home Screen
      home: const DashboardScreen(),
    );
  }
}
