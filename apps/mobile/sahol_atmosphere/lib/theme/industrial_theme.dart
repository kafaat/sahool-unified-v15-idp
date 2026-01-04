// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL INDUSTRIAL - John Deere Style Theme
// نظام تصميم ساهول الصناعي - نمط جون دير
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Philosophy: "Heavy Industry Design" - الصناعة الثقيلة
//
// Features:
// - High contrast for sunlight visibility
// - Rugged, professional appearance
// - Data-dense layouts
// - Machine gauge interfaces
//
// Inspired by: John Deere Operations Center
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';

/// Industrial Color Palette - لوحة الألوان الصناعية
class IndustrialColors {
  IndustrialColors._();

  // ─────────────────────────────────────────────────────────────────────────────
  // Primary Colors - John Deere Palette
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color primaryGreen = Color(0xFF008751);     // John Deere Green
  static const Color primaryGreenLight = Color(0xFF00A862);
  static const Color primaryGreenDark = Color(0xFF006B40);

  static const Color primaryYellow = Color(0xFFFFC107);    // John Deere Yellow
  static const Color primaryYellowLight = Color(0xFFFFD54F);
  static const Color primaryYellowDark = Color(0xFFFFB300);

  // ─────────────────────────────────────────────────────────────────────────────
  // Background Colors - High Contrast for Sunlight
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color bgPrimary = Color(0xFF121212);        // Deep Black
  static const Color bgSecondary = Color(0xFF1C1C1C);      // Charcoal
  static const Color bgTertiary = Color(0xFF252525);       // Dark Gray
  static const Color bgCard = Color(0xFF1E1E1E);

  // ─────────────────────────────────────────────────────────────────────────────
  // Status Colors - Industrial Safety Colors
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color statusActive = Color(0xFF00C853);     // Bright Green
  static const Color statusWarning = Color(0xFFFFC107);    // Amber (Safety)
  static const Color statusAlert = Color(0xFFFF5722);      // Deep Orange
  static const Color statusError = Color(0xFFD32F2F);      // Red
  static const Color statusInfo = Color(0xFF2196F3);       // Blue

  // ─────────────────────────────────────────────────────────────────────────────
  // Text Colors
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB0B0B0);
  static const Color textMuted = Color(0xFF757575);
  static const Color textOnPrimary = Color(0xFF000000);

  // ─────────────────────────────────────────────────────────────────────────────
  // UI Elements
  // ─────────────────────────────────────────────────────────────────────────────
  static const Color border = Color(0xFF333333);
  static const Color divider = Color(0xFF424242);
  static const Color surface = Color(0xFF2C2C2C);
}

/// Industrial Typography - الخطوط الصناعية
class IndustrialTypography {
  IndustrialTypography._();

  // Using Roboto Condensed for high density
  static const String fontPrimary = 'Roboto';
  static const String fontMono = 'RobotoMono';

  // Text Styles
  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 28,
    fontWeight: FontWeight.w700,
    letterSpacing: 1.5,
    color: IndustrialColors.textPrimary,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 22,
    fontWeight: FontWeight.w600,
    letterSpacing: 1.2,
    color: IndustrialColors.textPrimary,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    letterSpacing: 1.0,
    color: IndustrialColors.textPrimary,
  );

  static const TextStyle sectionHeader = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 12,
    fontWeight: FontWeight.w700,
    letterSpacing: 1.5,
    color: IndustrialColors.textMuted,
  );

  static const TextStyle gaugeValue = TextStyle(
    fontFamily: fontMono,
    fontSize: 24,
    fontWeight: FontWeight.w700,
    letterSpacing: 0,
    color: IndustrialColors.textPrimary,
  );

  static const TextStyle gaugeLabel = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 10,
    fontWeight: FontWeight.w500,
    letterSpacing: 1.0,
    color: IndustrialColors.textMuted,
  );

  static const TextStyle statValue = TextStyle(
    fontFamily: fontMono,
    fontSize: 16,
    fontWeight: FontWeight.w700,
    color: IndustrialColors.textPrimary,
  );

  static const TextStyle statLabel = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 10,
    fontWeight: FontWeight.w400,
    color: IndustrialColors.textMuted,
  );

  static const TextStyle buttonText = TextStyle(
    fontFamily: fontPrimary,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.5,
    color: IndustrialColors.textOnPrimary,
  );
}

/// Industrial Spacing
class IndustrialSpacing {
  IndustrialSpacing._();

  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double xxl = 32;
}

/// Industrial Radius
class IndustrialRadius {
  IndustrialRadius._();

  static const double none = 0;
  static const double sm = 2;
  static const double md = 4;
  static const double lg = 8;
}

/// Main Industrial Theme
class IndustrialTheme {
  IndustrialTheme._();

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,

      // Colors
      colorScheme: const ColorScheme.dark(
        primary: IndustrialColors.primaryGreen,
        secondary: IndustrialColors.primaryYellow,
        surface: IndustrialColors.bgSecondary,
        error: IndustrialColors.statusError,
        onPrimary: IndustrialColors.textOnPrimary,
        onSecondary: IndustrialColors.textOnPrimary,
        onSurface: IndustrialColors.textPrimary,
        onError: IndustrialColors.textPrimary,
      ),

      // Scaffold
      scaffoldBackgroundColor: IndustrialColors.bgPrimary,

      // AppBar
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.black,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: IndustrialColors.primaryGreen,
          fontSize: 16,
          fontWeight: FontWeight.w700,
          letterSpacing: 2,
        ),
        iconTheme: IconThemeData(color: IndustrialColors.textSecondary),
      ),

      // Cards
      cardTheme: CardTheme(
        color: IndustrialColors.bgCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(IndustrialRadius.md),
          side: const BorderSide(color: IndustrialColors.border),
        ),
      ),

      // Buttons
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: IndustrialColors.primaryGreen,
          foregroundColor: IndustrialColors.textOnPrimary,
          padding: const EdgeInsets.symmetric(
            horizontal: IndustrialSpacing.lg,
            vertical: IndustrialSpacing.md,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(IndustrialRadius.sm),
          ),
          textStyle: IndustrialTypography.buttonText,
        ),
      ),

      // Bottom Navigation
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.black,
        selectedItemColor: IndustrialColors.primaryGreen,
        unselectedItemColor: IndustrialColors.textMuted,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
        selectedLabelStyle: TextStyle(fontSize: 10, fontWeight: FontWeight.w600),
        unselectedLabelStyle: TextStyle(fontSize: 10),
      ),

      // Divider
      dividerTheme: const DividerThemeData(
        color: IndustrialColors.divider,
        thickness: 1,
      ),
    );
  }
}
