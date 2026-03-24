/// SAHOOL Accessibility Theme
/// ثيم الوصولية لسهول
///
/// Provides high-contrast colors and accessible text styles following WCAG 2.1 Level AA guidelines.
/// يوفر ألوان عالية التباين وأنماط نصية قابلة للوصول وفق إرشادات WCAG 2.1 المستوى AA
///
/// Features:
/// - High contrast color schemes | مخططات ألوان عالية التباين
/// - Accessible text styles with proper scaling | أنماط نصية قابلة للوصول مع تكبير مناسب
/// - Focus indicators | مؤشرات التركيز
/// - Touch target sizing | حجم أهداف اللمس
library;

import 'package:flutter/material.dart';

/// Minimum touch target size per WCAG 2.1 (48x48 dp)
const double kAccessibleTouchTarget = 48.0;

/// Minimum contrast ratio for normal text (WCAG AA)
const double kMinContrastRatioNormal = 4.5;

/// Minimum contrast ratio for large text (WCAG AA)
const double kMinContrastRatioLarge = 3.0;

/// Default focus indicator width
const double kFocusIndicatorWidth = 3.0;

/// SAHOOL Accessible Colors
/// ألوان سهول القابلة للوصول
class SahoolAccessibleColors {
  // ─────────────────────────────────────────────────────────────────────────
  // High Contrast Primary Colors - ألوان أساسية عالية التباين
  // These colors meet WCAG AA contrast requirements against white/black
  // ─────────────────────────────────────────────────────────────────────────

  /// Primary green - Contrast ratio 7.23:1 against white
  static const Color primary = Color(0xFF1B5E20);

  /// Primary dark - Contrast ratio 10.8:1 against white
  static const Color primaryDark = Color(0xFF0D3012);

  /// Primary light - Contrast ratio 4.7:1 against white
  static const Color primaryLight = Color(0xFF2E7D32);

  /// On primary (text on primary background)
  static const Color onPrimary = Color(0xFFFFFFFF);

  // ─────────────────────────────────────────────────────────────────────────
  // High Contrast Status Colors - ألوان حالة عالية التباين
  // ─────────────────────────────────────────────────────────────────────────

  /// Error color - Contrast ratio 5.9:1 against white
  static const Color error = Color(0xFFC62828);

  /// On error (text on error background)
  static const Color onError = Color(0xFFFFFFFF);

  /// Warning color - Contrast ratio 4.6:1 against black
  /// Note: Use black text on warning backgrounds
  static const Color warning = Color(0xFFFFA000);

  /// On warning (text on warning background)
  static const Color onWarning = Color(0xFF000000);

  /// Success color - Contrast ratio 4.5:1 against white
  static const Color success = Color(0xFF2E7D32);

  /// On success (text on success background)
  static const Color onSuccess = Color(0xFFFFFFFF);

  /// Info color - Contrast ratio 6.9:1 against white
  static const Color info = Color(0xFF1565C0);

  /// On info (text on info background)
  static const Color onInfo = Color(0xFFFFFFFF);

  // ─────────────────────────────────────────────────────────────────────────
  // High Contrast Text Colors - ألوان نصية عالية التباين
  // ─────────────────────────────────────────────────────────────────────────

  /// Primary text on light background - Contrast ratio 16.1:1
  static const Color textPrimaryLight = Color(0xFF121212);

  /// Secondary text on light background - Contrast ratio 7.0:1
  static const Color textSecondaryLight = Color(0xFF424242);

  /// Disabled text on light background - Contrast ratio 4.6:1
  static const Color textDisabledLight = Color(0xFF757575);

  /// Primary text on dark background - Contrast ratio 17.6:1
  static const Color textPrimaryDark = Color(0xFFFFFFFF);

  /// Secondary text on dark background - Contrast ratio 8.5:1
  static const Color textSecondaryDark = Color(0xFFB0BEC5);

  /// Disabled text on dark background - Contrast ratio 4.5:1
  static const Color textDisabledDark = Color(0xFF90A4AE);

  // ─────────────────────────────────────────────────────────────────────────
  // Background Colors - ألوان الخلفية
  // ─────────────────────────────────────────────────────────────────────────

  /// Light background
  static const Color backgroundLight = Color(0xFFFAFAFA);

  /// Dark background
  static const Color backgroundDark = Color(0xFF121212);

  /// Surface light
  static const Color surfaceLight = Color(0xFFFFFFFF);

  /// Surface dark
  static const Color surfaceDark = Color(0xFF1E1E1E);

  // ─────────────────────────────────────────────────────────────────────────
  // Focus and Selection Colors - ألوان التركيز والاختيار
  // ─────────────────────────────────────────────────────────────────────────

  /// Focus indicator color (high visibility)
  static const Color focusIndicator = Color(0xFF1565C0);

  /// Selection highlight
  static const Color selectionHighlight = Color(0xFF90CAF9);

  /// Focus overlay for dark backgrounds
  static const Color focusOverlayDark = Color(0x4D2196F3);

  /// Focus overlay for light backgrounds
  static const Color focusOverlayLight = Color(0x1F2196F3);

  // ─────────────────────────────────────────────────────────────────────────
  // Field Health Colors (High Contrast) - ألوان صحة الحقل عالية التباين
  // ─────────────────────────────────────────────────────────────────────────

  /// Excellent health - Contrast ratio 7.2:1 against white
  static const Color healthExcellent = Color(0xFF1B5E20);

  /// Good health - Contrast ratio 4.5:1 against white
  static const Color healthGood = Color(0xFF2E7D32);

  /// Moderate health - Contrast ratio 4.6:1 against black
  static const Color healthModerate = Color(0xFFF57C00);

  /// Poor health - Contrast ratio 5.9:1 against white
  static const Color healthPoor = Color(0xFFC62828);

  /// Critical health - Contrast ratio 8.5:1 against white
  static const Color healthCritical = Color(0xFF7B1FA2);

  // ─────────────────────────────────────────────────────────────────────────
  // Border Colors - ألوان الحدود
  // ─────────────────────────────────────────────────────────────────────────

  /// Input border - visible against light backgrounds
  static const Color inputBorder = Color(0xFF757575);

  /// Input border focused
  static const Color inputBorderFocused = Color(0xFF1565C0);

  /// Input border error
  static const Color inputBorderError = Color(0xFFC62828);

  /// Divider color - visible but subtle
  static const Color divider = Color(0xFFBDBDBD);
}

/// Accessible Text Styles
/// أنماط النصوص القابلة للوصول
class SahoolAccessibleTextStyles {
  static const String fontFamily = 'IBMPlexSansArabic';

  // ─────────────────────────────────────────────────────────────────────────
  // Display Styles (Large Headings) - أنماط العرض (عناوين كبيرة)
  // ─────────────────────────────────────────────────────────────────────────

  /// Display Large - minimum 14pt for WCAG large text
  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 57,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.25,
    height: 1.12,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 45,
    fontWeight: FontWeight.w400,
    letterSpacing: 0,
    height: 1.16,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 36,
    fontWeight: FontWeight.w400,
    letterSpacing: 0,
    height: 1.22,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Headline Styles - أنماط العناوين
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle headlineLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.w700,
    letterSpacing: 0,
    height: 1.25,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28,
    fontWeight: FontWeight.w700,
    letterSpacing: 0,
    height: 1.29,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.w700,
    letterSpacing: 0,
    height: 1.33,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Title Styles - أنماط الأقسام
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle titleLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 22,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.27,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.15,
    height: 1.33,
  );

  static const TextStyle titleSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.1,
    height: 1.37,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Body Styles - أنماط النص الأساسي
  // Minimum 16px (12pt) for body text per WCAG recommendations
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.5,
    height: 1.5,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.25,
    height: 1.5,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w400,
    letterSpacing: 0.4,
    height: 1.43,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Label Styles - أنماط التسميات
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle labelLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.1,
    height: 1.5,
  );

  static const TextStyle labelMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    height: 1.43,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    height: 1.33,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Button Styles - أنماط الأزرار
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle buttonLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18,
    fontWeight: FontWeight.w700,
    letterSpacing: 0.5,
    height: 1.33,
  );

  static const TextStyle buttonMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w700,
    letterSpacing: 0.5,
    height: 1.37,
  );

  static const TextStyle buttonSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w700,
    letterSpacing: 0.5,
    height: 1.43,
  );
}

/// Accessible Theme Data Builder
/// منشئ بيانات الثيم القابل للوصول
class SahoolAccessibleTheme {
  /// Light theme with high contrast and accessibility features
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      fontFamily: SahoolAccessibleTextStyles.fontFamily,

      // Color Scheme
      colorScheme: const ColorScheme.light(
        primary: SahoolAccessibleColors.primary,
        primaryContainer: SahoolAccessibleColors.primaryLight,
        secondary: SahoolAccessibleColors.info,
        secondaryContainer: SahoolAccessibleColors.selectionHighlight,
        surface: SahoolAccessibleColors.surfaceLight,
        error: SahoolAccessibleColors.error,
        onPrimary: SahoolAccessibleColors.onPrimary,
        onSecondary: Colors.white,
        onSurface: SahoolAccessibleColors.textPrimaryLight,
        onError: SahoolAccessibleColors.onError,
        outline: SahoolAccessibleColors.inputBorder,
      ),

      scaffoldBackgroundColor: SahoolAccessibleColors.backgroundLight,

      // Text Theme
      textTheme: const TextTheme(
        displayLarge: SahoolAccessibleTextStyles.displayLarge,
        displayMedium: SahoolAccessibleTextStyles.displayMedium,
        displaySmall: SahoolAccessibleTextStyles.displaySmall,
        headlineLarge: SahoolAccessibleTextStyles.headlineLarge,
        headlineMedium: SahoolAccessibleTextStyles.headlineMedium,
        headlineSmall: SahoolAccessibleTextStyles.headlineSmall,
        titleLarge: SahoolAccessibleTextStyles.titleLarge,
        titleMedium: SahoolAccessibleTextStyles.titleMedium,
        titleSmall: SahoolAccessibleTextStyles.titleSmall,
        bodyLarge: SahoolAccessibleTextStyles.bodyLarge,
        bodyMedium: SahoolAccessibleTextStyles.bodyMedium,
        bodySmall: SahoolAccessibleTextStyles.bodySmall,
        labelLarge: SahoolAccessibleTextStyles.labelLarge,
        labelMedium: SahoolAccessibleTextStyles.labelMedium,
        labelSmall: SahoolAccessibleTextStyles.labelSmall,
      ).apply(
        fontFamily: SahoolAccessibleTextStyles.fontFamily,
        bodyColor: SahoolAccessibleColors.textPrimaryLight,
        displayColor: SahoolAccessibleColors.textPrimaryLight,
      ),

      // AppBar
      appBarTheme: const AppBarTheme(
        backgroundColor: SahoolAccessibleColors.surfaceLight,
        foregroundColor: SahoolAccessibleColors.textPrimaryLight,
        elevation: 2,
        centerTitle: true,
        iconTheme: IconThemeData(
          color: SahoolAccessibleColors.primary,
          size: 28,
        ),
        titleTextStyle: TextStyle(
          fontFamily: SahoolAccessibleTextStyles.fontFamily,
          fontSize: 22,
          fontWeight: FontWeight.w700,
          color: SahoolAccessibleColors.textPrimaryLight,
        ),
      ),

      // Buttons - Ensuring minimum touch target size
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: SahoolAccessibleColors.primary,
          foregroundColor: SahoolAccessibleColors.onPrimary,
          elevation: 2,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          minimumSize: const Size(kAccessibleTouchTarget, kAccessibleTouchTarget),
          textStyle: SahoolAccessibleTextStyles.buttonMedium,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: SahoolAccessibleColors.primary,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          minimumSize: const Size(kAccessibleTouchTarget, kAccessibleTouchTarget),
          textStyle: SahoolAccessibleTextStyles.buttonMedium,
          side: const BorderSide(
            color: SahoolAccessibleColors.primary,
            width: 2,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: SahoolAccessibleColors.primary,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          minimumSize: const Size(kAccessibleTouchTarget, kAccessibleTouchTarget),
          textStyle: SahoolAccessibleTextStyles.buttonMedium,
        ),
      ),

      // Icon Button with minimum size
      iconButtonTheme: IconButtonThemeData(
        style: IconButton.styleFrom(
          foregroundColor: SahoolAccessibleColors.primary,
          minimumSize: const Size(kAccessibleTouchTarget, kAccessibleTouchTarget),
          padding: const EdgeInsets.all(12),
        ),
      ),

      // FAB
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: SahoolAccessibleColors.primary,
        foregroundColor: SahoolAccessibleColors.onPrimary,
        elevation: 6,
        extendedPadding: EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        sizeConstraints: BoxConstraints(
          minWidth: 56,
          minHeight: 56,
        ),
      ),

      // Input Decoration - High contrast borders
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: SahoolAccessibleColors.surfaceLight,
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: SahoolAccessibleColors.inputBorder,
            width: 2,
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: SahoolAccessibleColors.inputBorder,
            width: 1.5,
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: SahoolAccessibleColors.inputBorderFocused,
            width: 3,
          ),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: SahoolAccessibleColors.inputBorderError,
            width: 2,
          ),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: SahoolAccessibleColors.inputBorderError,
            width: 3,
          ),
        ),
        labelStyle: const TextStyle(
          color: SahoolAccessibleColors.textSecondaryLight,
          fontSize: 16,
        ),
        hintStyle: const TextStyle(
          color: SahoolAccessibleColors.textDisabledLight,
          fontSize: 16,
        ),
        errorStyle: const TextStyle(
          color: SahoolAccessibleColors.error,
          fontSize: 14,
          fontWeight: FontWeight.w500,
        ),
      ),

      // Card with visible border
      cardTheme: CardThemeData(
        elevation: 2,
        color: SahoolAccessibleColors.surfaceLight,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(
            color: SahoolAccessibleColors.divider.withValues(alpha: 0.5),
            width: 1,
          ),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),

      // Chip with sufficient contrast
      chipTheme: ChipThemeData(
        backgroundColor: SahoolAccessibleColors.backgroundLight,
        selectedColor: SahoolAccessibleColors.selectionHighlight,
        labelStyle: SahoolAccessibleTextStyles.labelMedium.copyWith(
          color: SahoolAccessibleColors.textPrimaryLight,
        ),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(
            color: SahoolAccessibleColors.inputBorder,
            width: 1,
          ),
        ),
      ),

      // Divider
      dividerTheme: const DividerThemeData(
        color: SahoolAccessibleColors.divider,
        thickness: 1,
        space: 24,
      ),

      // Bottom Navigation with sufficient contrast
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: SahoolAccessibleColors.surfaceLight,
        selectedItemColor: SahoolAccessibleColors.primary,
        unselectedItemColor: SahoolAccessibleColors.textSecondaryLight,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        selectedLabelStyle: TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 14,
        ),
        unselectedLabelStyle: TextStyle(
          fontSize: 13,
        ),
      ),

      // Tab Bar
      tabBarTheme: const TabBarThemeData(
        labelColor: SahoolAccessibleColors.primary,
        unselectedLabelColor: SahoolAccessibleColors.textSecondaryLight,
        indicatorColor: SahoolAccessibleColors.primary,
        labelStyle: SahoolAccessibleTextStyles.labelLarge,
        unselectedLabelStyle: SahoolAccessibleTextStyles.labelMedium,
        indicatorSize: TabBarIndicatorSize.tab,
      ),

      // Dialog
      dialogTheme: DialogThemeData(
        backgroundColor: SahoolAccessibleColors.surfaceLight,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        titleTextStyle: SahoolAccessibleTextStyles.headlineSmall.copyWith(
          color: SahoolAccessibleColors.textPrimaryLight,
        ),
        contentTextStyle: SahoolAccessibleTextStyles.bodyMedium.copyWith(
          color: SahoolAccessibleColors.textPrimaryLight,
        ),
      ),

      // SnackBar with high contrast
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        backgroundColor: SahoolAccessibleColors.textPrimaryLight,
        contentTextStyle: SahoolAccessibleTextStyles.bodyMedium.copyWith(
          color: SahoolAccessibleColors.textPrimaryDark,
        ),
        actionTextColor: SahoolAccessibleColors.selectionHighlight,
      ),

      // List Tile
      listTileTheme: const ListTileThemeData(
        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        horizontalTitleGap: 16,
        minVerticalPadding: 12,
        minLeadingWidth: kAccessibleTouchTarget,
      ),

      // Switch with visible track
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return SahoolAccessibleColors.primary;
          }
          return SahoolAccessibleColors.textDisabledLight;
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return SahoolAccessibleColors.primaryLight.withValues(alpha: 0.5);
          }
          return SahoolAccessibleColors.divider;
        }),
        trackOutlineColor: WidgetStateProperty.all(SahoolAccessibleColors.inputBorder),
      ),

      // Checkbox with visible border
      checkboxTheme: CheckboxThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return SahoolAccessibleColors.primary;
          }
          return Colors.transparent;
        }),
        checkColor: WidgetStateProperty.all(SahoolAccessibleColors.onPrimary),
        side: const BorderSide(
          color: SahoolAccessibleColors.inputBorder,
          width: 2,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
        ),
      ),

      // Radio with visible border
      radioTheme: RadioThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return SahoolAccessibleColors.primary;
          }
          return SahoolAccessibleColors.inputBorder;
        }),
      ),

      // Slider with visible track
      sliderTheme: SliderThemeData(
        activeTrackColor: SahoolAccessibleColors.primary,
        inactiveTrackColor: SahoolAccessibleColors.divider,
        thumbColor: SahoolAccessibleColors.primary,
        overlayColor: SahoolAccessibleColors.focusOverlayLight,
        valueIndicatorColor: SahoolAccessibleColors.primary,
        valueIndicatorTextStyle: SahoolAccessibleTextStyles.labelMedium.copyWith(
          color: SahoolAccessibleColors.onPrimary,
        ),
      ),

      // Progress Indicator
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: SahoolAccessibleColors.primary,
        linearTrackColor: SahoolAccessibleColors.divider,
        circularTrackColor: SahoolAccessibleColors.divider,
      ),

      // Focus
      focusColor: SahoolAccessibleColors.focusIndicator.withValues(alpha: 0.2),
      hoverColor: SahoolAccessibleColors.primary.withValues(alpha: 0.1),
      highlightColor: SahoolAccessibleColors.primary.withValues(alpha: 0.1),
      splashColor: SahoolAccessibleColors.primary.withValues(alpha: 0.2),
    );
  }

  /// Dark theme with high contrast and accessibility features
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      fontFamily: SahoolAccessibleTextStyles.fontFamily,

      colorScheme: const ColorScheme.dark(
        primary: SahoolAccessibleColors.primaryLight,
        primaryContainer: SahoolAccessibleColors.primary,
        secondary: SahoolAccessibleColors.selectionHighlight,
        surface: SahoolAccessibleColors.surfaceDark,
        error: Color(0xFFEF5350), // Lighter red for dark mode
        onPrimary: SahoolAccessibleColors.onPrimary,
        onSecondary: Colors.black,
        onSurface: SahoolAccessibleColors.textPrimaryDark,
        onError: Colors.white,
      ),

      scaffoldBackgroundColor: SahoolAccessibleColors.backgroundDark,

      textTheme: const TextTheme(
        displayLarge: SahoolAccessibleTextStyles.displayLarge,
        displayMedium: SahoolAccessibleTextStyles.displayMedium,
        displaySmall: SahoolAccessibleTextStyles.displaySmall,
        headlineLarge: SahoolAccessibleTextStyles.headlineLarge,
        headlineMedium: SahoolAccessibleTextStyles.headlineMedium,
        headlineSmall: SahoolAccessibleTextStyles.headlineSmall,
        titleLarge: SahoolAccessibleTextStyles.titleLarge,
        titleMedium: SahoolAccessibleTextStyles.titleMedium,
        titleSmall: SahoolAccessibleTextStyles.titleSmall,
        bodyLarge: SahoolAccessibleTextStyles.bodyLarge,
        bodyMedium: SahoolAccessibleTextStyles.bodyMedium,
        bodySmall: SahoolAccessibleTextStyles.bodySmall,
        labelLarge: SahoolAccessibleTextStyles.labelLarge,
        labelMedium: SahoolAccessibleTextStyles.labelMedium,
        labelSmall: SahoolAccessibleTextStyles.labelSmall,
      ).apply(
        fontFamily: SahoolAccessibleTextStyles.fontFamily,
        bodyColor: SahoolAccessibleColors.textPrimaryDark,
        displayColor: SahoolAccessibleColors.textPrimaryDark,
      ),

      appBarTheme: const AppBarTheme(
        backgroundColor: SahoolAccessibleColors.surfaceDark,
        foregroundColor: SahoolAccessibleColors.textPrimaryDark,
        elevation: 2,
        centerTitle: true,
      ),

      cardTheme: CardThemeData(
        elevation: 4,
        color: SahoolAccessibleColors.surfaceDark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: BorderSide(
            color: Colors.white.withValues(alpha: 0.1),
            width: 1,
          ),
        ),
      ),

      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: SahoolAccessibleColors.primaryLight,
          foregroundColor: SahoolAccessibleColors.onPrimary,
          minimumSize: const Size(kAccessibleTouchTarget, kAccessibleTouchTarget),
        ),
      ),

      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: SahoolAccessibleColors.surfaceDark,
        selectedItemColor: SahoolAccessibleColors.primaryLight,
        unselectedItemColor: SahoolAccessibleColors.textSecondaryDark,
      ),
    );
  }
}

/// Focus Indicator Widget
/// ودجت مؤشر التركيز
class FocusIndicator extends StatelessWidget {
  final Widget child;
  final bool isFocused;
  final Color? focusColor;
  final double borderRadius;
  final double width;

  const FocusIndicator({
    super.key,
    required this.child,
    required this.isFocused,
    this.focusColor,
    this.borderRadius = 8,
    this.width = kFocusIndicatorWidth,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        border: isFocused
            ? Border.all(
                color: focusColor ?? SahoolAccessibleColors.focusIndicator,
                width: width,
              )
            : null,
      ),
      child: child,
    );
  }
}

/// Accessible Touch Target Wrapper
/// غلاف هدف اللمس القابل للوصول
class AccessibleTouchTarget extends StatelessWidget {
  final Widget child;
  final VoidCallback? onTap;
  final double minSize;

  const AccessibleTouchTarget({
    super.key,
    required this.child,
    this.onTap,
    this.minSize = kAccessibleTouchTarget,
  });

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: BoxConstraints(
        minWidth: minSize,
        minHeight: minSize,
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(minSize / 4),
        child: Center(child: child),
      ),
    );
  }
}

/// Text with Accessible Styling Extension
extension AccessibleTextExtension on Text {
  /// Ensure text meets minimum size requirements
  Text withAccessibleSize({double minSize = 14.0}) {
    final currentStyle = style ?? const TextStyle();
    final currentSize = currentStyle.fontSize ?? 14.0;
    return Text(
      data ?? '',
      style: currentStyle.copyWith(
        fontSize: currentSize < minSize ? minSize : currentSize,
      ),
      textAlign: textAlign,
      maxLines: maxLines,
      overflow: overflow,
    );
  }

  /// Ensure text has sufficient contrast
  Text withHighContrast({required bool isDarkMode}) {
    final currentStyle = style ?? const TextStyle();
    return Text(
      data ?? '',
      style: currentStyle.copyWith(
        color: isDarkMode
            ? SahoolAccessibleColors.textPrimaryDark
            : SahoolAccessibleColors.textPrimaryLight,
      ),
      textAlign: textAlign,
      maxLines: maxLines,
      overflow: overflow,
    );
  }
}

/// Health Color Helper with Accessible Colors
class AccessibleHealthColors {
  /// Get accessible health color based on score
  static Color getColor(double score) {
    if (score >= 0.8) return SahoolAccessibleColors.healthExcellent;
    if (score >= 0.6) return SahoolAccessibleColors.healthGood;
    if (score >= 0.4) return SahoolAccessibleColors.healthModerate;
    if (score >= 0.2) return SahoolAccessibleColors.healthPoor;
    return SahoolAccessibleColors.healthCritical;
  }

  /// Get accessible text color for health background
  static Color getTextColor(double score) {
    if (score >= 0.4 && score < 0.6) {
      // Yellow/Orange background needs dark text
      return Colors.black;
    }
    return Colors.white;
  }

  /// Get health label
  static String getLabel(double score, {bool isArabic = true}) {
    if (score >= 0.8) return isArabic ? 'ممتاز' : 'Excellent';
    if (score >= 0.6) return isArabic ? 'جيد' : 'Good';
    if (score >= 0.4) return isArabic ? 'متوسط' : 'Moderate';
    if (score >= 0.2) return isArabic ? 'ضعيف' : 'Poor';
    return isArabic ? 'حرج' : 'Critical';
  }
}
