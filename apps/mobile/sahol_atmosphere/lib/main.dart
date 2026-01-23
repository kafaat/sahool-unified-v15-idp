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

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'theme/atmosphere_theme.dart';
import 'screens/dashboard_screen.dart';

/// Application entry point with proper async initialization
Future<void> main() async {
  // Ensure Flutter bindings are initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize system UI with error handling
  await _initializeSystemUI();

  // Run the application with error boundary
  runApp(const SaholAtmosphereApp());
}

/// Initialize system UI overlay style and orientation
/// Handles errors gracefully to prevent app crash on startup
Future<void> _initializeSystemUI() async {
  try {
    // Set system UI overlay style for immersive experience
    await SystemChrome.setSystemUIOverlayStyle(
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
  } catch (e) {
    // Log error but don't crash - system UI settings are non-critical
    if (kDebugMode) {
      debugPrint('Failed to initialize system UI: $e');
    }
  }
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

      // Accessibility: Show semantics debugger in debug mode if needed
      showSemanticsDebugger: false,

      // Error handling for widget build errors
      builder: (context, child) {
        // Apply text scaling limits for accessibility
        final mediaQueryData = MediaQuery.of(context);
        final constrainedTextScaleFactor = mediaQueryData.textScaler.clamp(
          minScaleFactor: 0.8,
          maxScaleFactor: 1.5,
        );

        return MediaQuery(
          data: mediaQueryData.copyWith(
            textScaler: constrainedTextScaleFactor,
          ),
          child: child ?? const SizedBox.shrink(),
        );
      },

      // Home Screen
      home: const DashboardScreen(),
    );
  }
}
