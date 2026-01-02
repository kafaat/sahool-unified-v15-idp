// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Design System Theme
// نظام تصميم ساهول أتموسفير
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Philosophy: "Atmospheric & Spatial Design"
// الفلسفة: "التصميم المكاني والأتموسفيري"
//
// Colors: Deep Earthy Tones + Bio-Luminescent Accents
// الألوان: ألوان ترابية عميقة + لمسات نيون نباتية
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';

/// Atmosphere Color Palette - لوحة ألوان أتموسفير
class AtmosphereColors {
  AtmosphereColors._();

  // ─────────────────────────────────────────────────────────────────────────────
  // Deep Earthy Tones - الألوان الترابية العميقة
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color bgPrimary = Color(0xFF0F172A);
  static const Color bgSecondary = Color(0xFF1E293B);
  static const Color bgTertiary = Color(0xFF334155);
  static const Color bgCard = Color(0xFF1E293B);

  // ─────────────────────────────────────────────────────────────────────────────
  // Bio-Luminescent Accents - لمسات نيون نباتية
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color success = Color(0xFF4ADE80);      // Neon Green - حيوي
  static const Color successGlow = Color(0x4D4ADE80); // 30% opacity
  static const Color successLight = Color(0xFF86EFAC);

  static const Color warning = Color(0xFFFBBF24);      // Amber - شمس/حرارة
  static const Color warningGlow = Color(0x4DFBBF24);
  static const Color warningLight = Color(0xFFFCD34D);

  static const Color alert = Color(0xFFF87171);        // Soft Red - دافئ
  static const Color alertGlow = Color(0x4DF87171);
  static const Color alertLight = Color(0xFFFCA5A5);

  static const Color info = Color(0xFF60A5FA);         // Sky Blue - معلومات
  static const Color infoGlow = Color(0x4D60A5FA);
  static const Color infoLight = Color(0xFF93C5FD);

  // ─────────────────────────────────────────────────────────────────────────────
  // Text Colors - ألوان النصوص
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);
  static const Color textDisabled = Color(0xFF475569);

  // ─────────────────────────────────────────────────────────────────────────────
  // Glassmorphism - تأثير الزجاج
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color glassBg = Color(0x0DFFFFFF);        // 5% white
  static const Color glassBorder = Color(0x1AFFFFFF);    // 10% white
  static const Color glassHighlight = Color(0x14FFFFFF); // 8% white

  // ─────────────────────────────────────────────────────────────────────────────
  // Gradients - التدرجات
  // ─────────────────────────────────────────────────────────────────────────────
  static const LinearGradient successGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF4ADE80), Color(0xFF22C55E)],
  );

  static const LinearGradient glassGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0x1AFFFFFF), Color(0x05FFFFFF)],
  );

  static const LinearGradient bgGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0xFF0F172A), Color(0xFF1E293B)],
  );
}

/// Atmosphere Typography - الطباعة
class AtmosphereTypography {
  AtmosphereTypography._();

  // Display font for headlines
  static const String fontDisplay = 'SpaceGrotesk';

  // Body font for content
  static const String fontBody = 'Inter';

  // Text Styles
  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontDisplay,
    fontSize: 32,
    fontWeight: FontWeight.w700,
    letterSpacing: -0.5,
    color: AtmosphereColors.textPrimary,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: fontDisplay,
    fontSize: 24,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.25,
    color: AtmosphereColors.textPrimary,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: fontDisplay,
    fontSize: 20,
    fontWeight: FontWeight.w600,
    color: AtmosphereColors.textPrimary,
  );

  static const TextStyle headlineLarge = TextStyle(
    fontFamily: fontBody,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: AtmosphereColors.textPrimary,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontBody,
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: AtmosphereColors.textPrimary,
  );

  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontBody,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: AtmosphereColors.textPrimary,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontBody,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: AtmosphereColors.textSecondary,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontBody,
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: AtmosphereColors.textMuted,
  );

  static const TextStyle labelLarge = TextStyle(
    fontFamily: fontBody,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    color: AtmosphereColors.textPrimary,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: fontBody,
    fontSize: 11,
    fontWeight: FontWeight.w500,
    letterSpacing: 1.5,
    color: AtmosphereColors.textMuted,
  );
}

/// Atmosphere Spacing - المسافات
class AtmosphereSpacing {
  AtmosphereSpacing._();

  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;
}

/// Atmosphere Border Radius - الحواف
class AtmosphereRadius {
  AtmosphereRadius._();

  static const double sm = 8;
  static const double md = 12;
  static const double lg = 20;
  static const double xl = 28;
  static const double full = 9999;
}

/// Atmosphere Shadows - الظلال
class AtmosphereShadows {
  AtmosphereShadows._();

  static List<BoxShadow> glowSuccess = [
    BoxShadow(
      color: AtmosphereColors.successGlow,
      blurRadius: 20,
      spreadRadius: 2,
    ),
  ];

  static List<BoxShadow> glowWarning = [
    BoxShadow(
      color: AtmosphereColors.warningGlow,
      blurRadius: 20,
      spreadRadius: 2,
    ),
  ];

  static List<BoxShadow> glowAlert = [
    BoxShadow(
      color: AtmosphereColors.alertGlow,
      blurRadius: 20,
      spreadRadius: 2,
    ),
  ];

  static List<BoxShadow> cardShadow = [
    const BoxShadow(
      color: Color(0x40000000),
      blurRadius: 10,
      offset: Offset(0, 4),
    ),
  ];
}

/// Main Theme Class
class AtmosphereTheme {
  AtmosphereTheme._();

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,

      // Colors
      colorScheme: const ColorScheme.dark(
        primary: AtmosphereColors.success,
        secondary: AtmosphereColors.info,
        surface: AtmosphereColors.bgSecondary,
        error: AtmosphereColors.alert,
        onPrimary: AtmosphereColors.bgPrimary,
        onSecondary: AtmosphereColors.textPrimary,
        onSurface: AtmosphereColors.textPrimary,
        onError: AtmosphereColors.textPrimary,
      ),

      // Scaffold
      scaffoldBackgroundColor: AtmosphereColors.bgPrimary,

      // AppBar
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: AtmosphereTypography.displaySmall,
        iconTheme: IconThemeData(color: AtmosphereColors.textPrimary),
      ),

      // Cards
      cardTheme: CardTheme(
        color: AtmosphereColors.bgCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
          side: const BorderSide(color: AtmosphereColors.glassBorder),
        ),
      ),

      // Buttons
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AtmosphereColors.success,
          foregroundColor: AtmosphereColors.bgPrimary,
          padding: const EdgeInsets.symmetric(
            horizontal: AtmosphereSpacing.lg,
            vertical: AtmosphereSpacing.md,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AtmosphereRadius.md),
          ),
          textStyle: AtmosphereTypography.labelLarge,
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AtmosphereColors.success,
          side: const BorderSide(color: AtmosphereColors.success),
          padding: const EdgeInsets.symmetric(
            horizontal: AtmosphereSpacing.lg,
            vertical: AtmosphereSpacing.md,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AtmosphereRadius.md),
          ),
          textStyle: AtmosphereTypography.labelLarge,
        ),
      ),

      // Text
      textTheme: const TextTheme(
        displayLarge: AtmosphereTypography.displayLarge,
        displayMedium: AtmosphereTypography.displayMedium,
        displaySmall: AtmosphereTypography.displaySmall,
        headlineLarge: AtmosphereTypography.headlineLarge,
        headlineMedium: AtmosphereTypography.headlineMedium,
        bodyLarge: AtmosphereTypography.bodyLarge,
        bodyMedium: AtmosphereTypography.bodyMedium,
        bodySmall: AtmosphereTypography.bodySmall,
        labelLarge: AtmosphereTypography.labelLarge,
        labelSmall: AtmosphereTypography.labelSmall,
      ),

      // Input Decoration
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AtmosphereColors.glassBg,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AtmosphereRadius.md),
          borderSide: const BorderSide(color: AtmosphereColors.glassBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AtmosphereRadius.md),
          borderSide: const BorderSide(color: AtmosphereColors.glassBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AtmosphereRadius.md),
          borderSide: const BorderSide(color: AtmosphereColors.success),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: AtmosphereSpacing.md,
          vertical: AtmosphereSpacing.md,
        ),
        hintStyle: AtmosphereTypography.bodyMedium,
      ),

      // Divider
      dividerTheme: const DividerThemeData(
        color: AtmosphereColors.glassBorder,
        thickness: 1,
      ),

      // Bottom Navigation
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AtmosphereColors.bgSecondary,
        selectedItemColor: AtmosphereColors.success,
        unselectedItemColor: AtmosphereColors.textMuted,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
      ),
    );
  }
}
