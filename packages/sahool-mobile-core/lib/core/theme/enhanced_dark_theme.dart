import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// SAHOOL Enhanced Dark Theme System
/// نظام الثيم الداكن المحسن لسهول
///
/// Features:
/// - Deep dark mode (#0D0D0D background) | الوضع الداكن العميق
/// - AMOLED black option | خيار الأسود لشاشات AMOLED
/// - Multiple accent color variations | تنويعات ألوان مميزة
/// - High contrast mode | وضع التباين العالي
/// - Glass-optimized color schemes | مخططات ألوان محسنة للزجاج

// ═══════════════════════════════════════════════════════════════════════════
// Dark Theme Variants - أنواع الثيم الداكن
// ═══════════════════════════════════════════════════════════════════════════

/// Available dark theme variants
enum DarkThemeVariant {
  /// Standard dark theme (#1A1A1A)
  standard,

  /// Deep dark theme (#0D0D0D)
  deep,

  /// AMOLED pure black (#000000)
  amoled,

  /// Charcoal dark (#1F1F1F)
  charcoal,

  /// High contrast dark
  highContrast,

  /// Green tinted dark (SAHOOL brand)
  sahoolGreen,
}

/// Available accent colors for dark theme
enum DarkThemeAccent {
  /// SAHOOL Green (default)
  green,

  /// Ocean Blue
  blue,

  /// Harvest Gold
  gold,

  /// Sunset Orange
  orange,

  /// Aurora Purple
  purple,

  /// Neon Cyan
  cyan,

  /// Rose Pink
  rose,

  /// System (follows system accent)
  system,
}

// ═══════════════════════════════════════════════════════════════════════════
// Enhanced Dark Theme Colors
// ═══════════════════════════════════════════════════════════════════════════

/// Enhanced dark theme color definitions
class EnhancedDarkColors {
  EnhancedDarkColors._();

  // ─────────────────────────────────────────────────────────────────────────
  // Background Colors - ألوان الخلفية
  // ─────────────────────────────────────────────────────────────────────────

  /// Standard dark background
  static const Color backgroundStandard = Color(0xFF1A1A1A);

  /// Deep dark background
  static const Color backgroundDeep = Color(0xFF0D0D0D);

  /// AMOLED pure black
  static const Color backgroundAmoled = Color(0xFF000000);

  /// Charcoal dark
  static const Color backgroundCharcoal = Color(0xFF1F1F1F);

  /// High contrast dark
  static const Color backgroundHighContrast = Color(0xFF000000);

  /// SAHOOL green tinted dark
  static const Color backgroundSahoolGreen = Color(0xFF0A1A0A);

  // ─────────────────────────────────────────────────────────────────────────
  // Surface Colors - ألوان السطح
  // ─────────────────────────────────────────────────────────────────────────

  /// Standard surface
  static const Color surfaceStandard = Color(0xFF2D2D2D);

  /// Deep surface
  static const Color surfaceDeep = Color(0xFF1A1A1A);

  /// AMOLED surface
  static const Color surfaceAmoled = Color(0xFF0D0D0D);

  /// Charcoal surface
  static const Color surfaceCharcoal = Color(0xFF2A2A2A);

  /// High contrast surface
  static const Color surfaceHighContrast = Color(0xFF121212);

  /// Elevated surface (for cards, dialogs)
  static const Color surfaceElevated1 = Color(0xFF2D2D2D);
  static const Color surfaceElevated2 = Color(0xFF363636);
  static const Color surfaceElevated3 = Color(0xFF404040);

  // ─────────────────────────────────────────────────────────────────────────
  // Accent Colors - الألوان المميزة
  // ─────────────────────────────────────────────────────────────────────────

  /// SAHOOL Green
  static const Color accentGreen = Color(0xFF4CAF50);
  static const Color accentGreenLight = Color(0xFF81C784);
  static const Color accentGreenDark = Color(0xFF388E3C);

  /// Ocean Blue
  static const Color accentBlue = Color(0xFF42A5F5);
  static const Color accentBlueLight = Color(0xFF90CAF9);
  static const Color accentBlueDark = Color(0xFF1976D2);

  /// Harvest Gold
  static const Color accentGold = Color(0xFFFFD54F);
  static const Color accentGoldLight = Color(0xFFFFE082);
  static const Color accentGoldDark = Color(0xFFFFC107);

  /// Sunset Orange
  static const Color accentOrange = Color(0xFFFF9800);
  static const Color accentOrangeLight = Color(0xFFFFB74D);
  static const Color accentOrangeDark = Color(0xFFF57C00);

  /// Aurora Purple
  static const Color accentPurple = Color(0xFFAB47BC);
  static const Color accentPurpleLight = Color(0xFFCE93D8);
  static const Color accentPurpleDark = Color(0xFF7B1FA2);

  /// Neon Cyan
  static const Color accentCyan = Color(0xFF00E5FF);
  static const Color accentCyanLight = Color(0xFF84FFFF);
  static const Color accentCyanDark = Color(0xFF00B8D4);

  /// Rose Pink
  static const Color accentRose = Color(0xFFEC407A);
  static const Color accentRoseLight = Color(0xFFF48FB1);
  static const Color accentRoseDark = Color(0xFFC2185B);

  // ─────────────────────────────────────────────────────────────────────────
  // Text Colors - ألوان النص
  // ─────────────────────────────────────────────────────────────────────────

  /// Primary text
  static const Color textPrimary = Color(0xFFFFFFFF);

  /// Secondary text
  static const Color textSecondary = Color(0xFFB0BEC5);

  /// Disabled text
  static const Color textDisabled = Color(0xFF757575);

  /// High contrast primary text
  static const Color textPrimaryHighContrast = Color(0xFFFFFFFF);

  /// High contrast secondary text
  static const Color textSecondaryHighContrast = Color(0xFFE0E0E0);

  // ─────────────────────────────────────────────────────────────────────────
  // Status Colors (Dark Mode Optimized) - ألوان الحالة
  // ─────────────────────────────────────────────────────────────────────────

  /// Success
  static const Color success = Color(0xFF66BB6A);
  static const Color onSuccess = Color(0xFF000000);

  /// Warning
  static const Color warning = Color(0xFFFFA726);
  static const Color onWarning = Color(0xFF000000);

  /// Error
  static const Color error = Color(0xFFEF5350);
  static const Color onError = Color(0xFFFFFFFF);

  /// Info
  static const Color info = Color(0xFF42A5F5);
  static const Color onInfo = Color(0xFF000000);

  // ─────────────────────────────────────────────────────────────────────────
  // Border & Divider Colors - ألوان الحدود والفواصل
  // ─────────────────────────────────────────────────────────────────────────

  /// Border
  static const Color border = Color(0xFF424242);

  /// Border subtle
  static const Color borderSubtle = Color(0xFF303030);

  /// Divider
  static const Color divider = Color(0xFF424242);

  /// Focus border
  static const Color focusBorder = Color(0xFF90CAF9);
}

// ═══════════════════════════════════════════════════════════════════════════
// Enhanced Dark Theme Builder
// ═══════════════════════════════════════════════════════════════════════════

/// Builder for enhanced dark themes
class EnhancedDarkTheme {
  EnhancedDarkTheme._();

  static const String _fontFamily = 'IBMPlexSansArabic';

  /// Get dark theme with specified variant and accent
  static ThemeData build({
    DarkThemeVariant variant = DarkThemeVariant.deep,
    DarkThemeAccent accent = DarkThemeAccent.green,
  }) {
    final colors = _getColors(variant);
    final accentColors = _getAccentColors(accent);

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      fontFamily: _fontFamily,

      // Color Scheme
      colorScheme: ColorScheme.dark(
        primary: accentColors.primary,
        primaryContainer: accentColors.dark,
        onPrimary: accentColors.onPrimary,
        secondary: accentColors.secondary,
        secondaryContainer: accentColors.dark.withOpacity(0.3),
        onSecondary: accentColors.onSecondary,
        surface: colors.surface,
        onSurface: colors.onSurface,
        surfaceContainerHighest: colors.surfaceElevated,
        error: EnhancedDarkColors.error,
        onError: EnhancedDarkColors.onError,
        outline: colors.border,
        outlineVariant: colors.borderSubtle,
      ),

      scaffoldBackgroundColor: colors.background,
      canvasColor: colors.background,
      cardColor: colors.surface,
      dividerColor: colors.divider,

      // Text Theme
      textTheme: _buildTextTheme(colors),

      // AppBar Theme
      appBarTheme: AppBarTheme(
        backgroundColor: colors.surface,
        foregroundColor: colors.onSurface,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        systemOverlayStyle: variant == DarkThemeVariant.amoled
            ? SystemUiOverlayStyle.light.copyWith(
                statusBarColor: Colors.transparent,
                systemNavigationBarColor: EnhancedDarkColors.backgroundAmoled,
              )
            : SystemUiOverlayStyle.light.copyWith(
                statusBarColor: Colors.transparent,
                systemNavigationBarColor: colors.background,
              ),
        titleTextStyle: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: colors.onSurface,
        ),
        iconTheme: IconThemeData(
          color: accentColors.primary,
          size: 24,
        ),
      ),

      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: colors.surface,
        selectedItemColor: accentColors.primary,
        unselectedItemColor: EnhancedDarkColors.textSecondary,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        selectedLabelStyle: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),

      // Navigation Bar Theme (Material 3)
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: colors.surface,
        indicatorColor: accentColors.primary.withOpacity(0.2),
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return TextStyle(
              fontFamily: _fontFamily,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: accentColors.primary,
            );
          }
          return const TextStyle(
            fontFamily: _fontFamily,
            fontSize: 12,
            color: EnhancedDarkColors.textSecondary,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return IconThemeData(color: accentColors.primary);
          }
          return const IconThemeData(color: EnhancedDarkColors.textSecondary);
        }),
      ),

      // Card Theme
      cardTheme: CardTheme(
        elevation: variant == DarkThemeVariant.amoled ? 0 : 2,
        color: colors.surface,
        surfaceTintColor: Colors.transparent,
        shadowColor: Colors.black.withOpacity(0.4),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: variant == DarkThemeVariant.amoled
              ? BorderSide(color: colors.border.withOpacity(0.3))
              : BorderSide.none,
        ),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),

      // Elevated Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accentColors.primary,
          foregroundColor: accentColors.onPrimary,
          elevation: variant == DarkThemeVariant.amoled ? 0 : 4,
          shadowColor: accentColors.primary.withOpacity(0.3),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          minimumSize: const Size(120, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontFamily: _fontFamily,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // Outlined Button Theme
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: accentColors.primary,
          side: BorderSide(color: accentColors.primary, width: 2),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          minimumSize: const Size(120, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontFamily: _fontFamily,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // Text Button Theme
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: accentColors.primary,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          textStyle: const TextStyle(
            fontFamily: _fontFamily,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // Icon Button Theme
      iconButtonTheme: IconButtonThemeData(
        style: IconButton.styleFrom(
          foregroundColor: accentColors.primary,
          minimumSize: const Size(48, 48),
          padding: const EdgeInsets.all(12),
        ),
      ),

      // Floating Action Button Theme
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: accentColors.primary,
        foregroundColor: accentColors.onPrimary,
        elevation: variant == DarkThemeVariant.amoled ? 0 : 6,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        extendedPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      ),

      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colors.surfaceElevated.withOpacity(0.5),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colors.border),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: colors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: accentColors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: EnhancedDarkColors.error, width: 2),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: EnhancedDarkColors.error, width: 2),
        ),
        labelStyle: const TextStyle(color: EnhancedDarkColors.textSecondary),
        hintStyle: const TextStyle(color: EnhancedDarkColors.textDisabled),
        errorStyle: const TextStyle(color: EnhancedDarkColors.error),
        prefixIconColor: EnhancedDarkColors.textSecondary,
        suffixIconColor: EnhancedDarkColors.textSecondary,
      ),

      // Chip Theme
      chipTheme: ChipThemeData(
        backgroundColor: colors.surfaceElevated,
        selectedColor: accentColors.primary.withOpacity(0.2),
        disabledColor: colors.surfaceElevated.withOpacity(0.5),
        labelStyle: const TextStyle(
          fontFamily: _fontFamily,
          fontSize: 14,
        ),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(color: colors.border),
        ),
      ),

      // Dialog Theme
      dialogTheme: DialogTheme(
        backgroundColor: colors.surface,
        surfaceTintColor: Colors.transparent,
        elevation: variant == DarkThemeVariant.amoled ? 0 : 16,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: variant == DarkThemeVariant.amoled
              ? BorderSide(color: colors.border)
              : BorderSide.none,
        ),
        titleTextStyle: TextStyle(
          fontFamily: _fontFamily,
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: colors.onSurface,
        ),
        contentTextStyle: const TextStyle(
          fontFamily: _fontFamily,
          fontSize: 16,
          color: EnhancedDarkColors.textSecondary,
        ),
      ),

      // Bottom Sheet Theme
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: colors.surface,
        surfaceTintColor: Colors.transparent,
        elevation: variant == DarkThemeVariant.amoled ? 0 : 8,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
        ),
        dragHandleColor: colors.border,
        dragHandleSize: const Size(40, 4),
      ),

      // Snack Bar Theme
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: colors.surfaceElevated,
        contentTextStyle: TextStyle(
          fontFamily: _fontFamily,
          color: colors.onSurface,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        actionTextColor: accentColors.primary,
      ),

      // List Tile Theme
      listTileTheme: ListTileThemeData(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        horizontalTitleGap: 16,
        minVerticalPadding: 12,
        iconColor: accentColors.primary,
        textColor: colors.onSurface,
        tileColor: Colors.transparent,
        selectedTileColor: accentColors.primary.withOpacity(0.1),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),

      // Switch Theme
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return accentColors.primary;
          }
          return EnhancedDarkColors.textDisabled;
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return accentColors.primary.withOpacity(0.5);
          }
          return colors.border;
        }),
        trackOutlineColor: WidgetStateProperty.all(colors.border),
      ),

      // Checkbox Theme
      checkboxTheme: CheckboxThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return accentColors.primary;
          }
          return Colors.transparent;
        }),
        checkColor: WidgetStateProperty.all(accentColors.onPrimary),
        side: BorderSide(color: colors.border, width: 2),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
        ),
      ),

      // Radio Theme
      radioTheme: RadioThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return accentColors.primary;
          }
          return colors.border;
        }),
      ),

      // Slider Theme
      sliderTheme: SliderThemeData(
        activeTrackColor: accentColors.primary,
        inactiveTrackColor: colors.border,
        thumbColor: accentColors.primary,
        overlayColor: accentColors.primary.withOpacity(0.2),
        valueIndicatorColor: accentColors.primary,
        valueIndicatorTextStyle: TextStyle(
          fontFamily: _fontFamily,
          color: accentColors.onPrimary,
          fontWeight: FontWeight.bold,
        ),
      ),

      // Progress Indicator Theme
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: accentColors.primary,
        linearTrackColor: colors.border,
        circularTrackColor: colors.border,
      ),

      // Tab Bar Theme
      tabBarTheme: TabBarTheme(
        labelColor: accentColors.primary,
        unselectedLabelColor: EnhancedDarkColors.textSecondary,
        indicatorColor: accentColors.primary,
        labelStyle: const TextStyle(
          fontFamily: _fontFamily,
          fontWeight: FontWeight.bold,
        ),
        unselectedLabelStyle: const TextStyle(
          fontFamily: _fontFamily,
        ),
        indicatorSize: TabBarIndicatorSize.tab,
        dividerColor: colors.border,
      ),

      // Divider Theme
      dividerTheme: DividerThemeData(
        color: colors.divider,
        thickness: 1,
        space: 24,
      ),

      // Popup Menu Theme
      popupMenuTheme: PopupMenuThemeData(
        color: colors.surface,
        surfaceTintColor: Colors.transparent,
        elevation: variant == DarkThemeVariant.amoled ? 0 : 8,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: variant == DarkThemeVariant.amoled
              ? BorderSide(color: colors.border)
              : BorderSide.none,
        ),
        textStyle: TextStyle(
          fontFamily: _fontFamily,
          color: colors.onSurface,
        ),
      ),

      // Tooltip Theme
      tooltipTheme: TooltipThemeData(
        decoration: BoxDecoration(
          color: colors.surfaceElevated,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: colors.border),
        ),
        textStyle: TextStyle(
          fontFamily: _fontFamily,
          color: colors.onSurface,
          fontSize: 12,
        ),
      ),

      // Highlight and Splash Colors
      highlightColor: accentColors.primary.withOpacity(0.1),
      splashColor: accentColors.primary.withOpacity(0.2),
      focusColor: accentColors.primary.withOpacity(0.15),
      hoverColor: accentColors.primary.withOpacity(0.08),
    );
  }

  /// Get color configuration for variant
  static _DarkColorConfig _getColors(DarkThemeVariant variant) {
    switch (variant) {
      case DarkThemeVariant.standard:
        return const _DarkColorConfig(
          background: EnhancedDarkColors.backgroundStandard,
          surface: EnhancedDarkColors.surfaceStandard,
          surfaceElevated: EnhancedDarkColors.surfaceElevated1,
          onSurface: EnhancedDarkColors.textPrimary,
          border: EnhancedDarkColors.border,
          borderSubtle: EnhancedDarkColors.borderSubtle,
          divider: EnhancedDarkColors.divider,
        );
      case DarkThemeVariant.deep:
        return const _DarkColorConfig(
          background: EnhancedDarkColors.backgroundDeep,
          surface: EnhancedDarkColors.surfaceDeep,
          surfaceElevated: EnhancedDarkColors.surfaceStandard,
          onSurface: EnhancedDarkColors.textPrimary,
          border: EnhancedDarkColors.border,
          borderSubtle: EnhancedDarkColors.borderSubtle,
          divider: EnhancedDarkColors.borderSubtle,
        );
      case DarkThemeVariant.amoled:
        return const _DarkColorConfig(
          background: EnhancedDarkColors.backgroundAmoled,
          surface: EnhancedDarkColors.surfaceAmoled,
          surfaceElevated: EnhancedDarkColors.surfaceDeep,
          onSurface: EnhancedDarkColors.textPrimary,
          border: Color(0xFF2A2A2A),
          borderSubtle: Color(0xFF1A1A1A),
          divider: Color(0xFF2A2A2A),
        );
      case DarkThemeVariant.charcoal:
        return const _DarkColorConfig(
          background: EnhancedDarkColors.backgroundCharcoal,
          surface: EnhancedDarkColors.surfaceCharcoal,
          surfaceElevated: EnhancedDarkColors.surfaceElevated2,
          onSurface: EnhancedDarkColors.textPrimary,
          border: EnhancedDarkColors.border,
          borderSubtle: EnhancedDarkColors.borderSubtle,
          divider: EnhancedDarkColors.divider,
        );
      case DarkThemeVariant.highContrast:
        return const _DarkColorConfig(
          background: EnhancedDarkColors.backgroundHighContrast,
          surface: EnhancedDarkColors.surfaceHighContrast,
          surfaceElevated: EnhancedDarkColors.surfaceDeep,
          onSurface: EnhancedDarkColors.textPrimaryHighContrast,
          border: Color(0xFF666666),
          borderSubtle: Color(0xFF444444),
          divider: Color(0xFF666666),
        );
      case DarkThemeVariant.sahoolGreen:
        return const _DarkColorConfig(
          background: EnhancedDarkColors.backgroundSahoolGreen,
          surface: Color(0xFF0F1F0F),
          surfaceElevated: Color(0xFF152515),
          onSurface: EnhancedDarkColors.textPrimary,
          border: Color(0xFF1A3A1A),
          borderSubtle: Color(0xFF0F2A0F),
          divider: Color(0xFF1A3A1A),
        );
    }
  }

  /// Get accent color configuration
  static _AccentColorConfig _getAccentColors(DarkThemeAccent accent) {
    switch (accent) {
      case DarkThemeAccent.green:
        return const _AccentColorConfig(
          primary: EnhancedDarkColors.accentGreen,
          secondary: EnhancedDarkColors.accentGreenLight,
          dark: EnhancedDarkColors.accentGreenDark,
          onPrimary: Colors.black,
          onSecondary: Colors.black,
        );
      case DarkThemeAccent.blue:
        return const _AccentColorConfig(
          primary: EnhancedDarkColors.accentBlue,
          secondary: EnhancedDarkColors.accentBlueLight,
          dark: EnhancedDarkColors.accentBlueDark,
          onPrimary: Colors.black,
          onSecondary: Colors.black,
        );
      case DarkThemeAccent.gold:
        return const _AccentColorConfig(
          primary: EnhancedDarkColors.accentGold,
          secondary: EnhancedDarkColors.accentGoldLight,
          dark: EnhancedDarkColors.accentGoldDark,
          onPrimary: Colors.black,
          onSecondary: Colors.black,
        );
      case DarkThemeAccent.orange:
        return const _AccentColorConfig(
          primary: EnhancedDarkColors.accentOrange,
          secondary: EnhancedDarkColors.accentOrangeLight,
          dark: EnhancedDarkColors.accentOrangeDark,
          onPrimary: Colors.black,
          onSecondary: Colors.black,
        );
      case DarkThemeAccent.purple:
        return const _AccentColorConfig(
          primary: EnhancedDarkColors.accentPurple,
          secondary: EnhancedDarkColors.accentPurpleLight,
          dark: EnhancedDarkColors.accentPurpleDark,
          onPrimary: Colors.white,
          onSecondary: Colors.black,
        );
      case DarkThemeAccent.cyan:
        return const _AccentColorConfig(
          primary: EnhancedDarkColors.accentCyan,
          secondary: EnhancedDarkColors.accentCyanLight,
          dark: EnhancedDarkColors.accentCyanDark,
          onPrimary: Colors.black,
          onSecondary: Colors.black,
        );
      case DarkThemeAccent.rose:
        return const _AccentColorConfig(
          primary: EnhancedDarkColors.accentRose,
          secondary: EnhancedDarkColors.accentRoseLight,
          dark: EnhancedDarkColors.accentRoseDark,
          onPrimary: Colors.white,
          onSecondary: Colors.black,
        );
      case DarkThemeAccent.system:
        // Default to green for system
        return const _AccentColorConfig(
          primary: EnhancedDarkColors.accentGreen,
          secondary: EnhancedDarkColors.accentGreenLight,
          dark: EnhancedDarkColors.accentGreenDark,
          onPrimary: Colors.black,
          onSecondary: Colors.black,
        );
    }
  }

  /// Build text theme
  static TextTheme _buildTextTheme(_DarkColorConfig colors) {
    return TextTheme(
      displayLarge: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 57,
        fontWeight: FontWeight.w400,
        color: colors.onSurface,
      ),
      displayMedium: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 45,
        fontWeight: FontWeight.w400,
        color: colors.onSurface,
      ),
      displaySmall: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 36,
        fontWeight: FontWeight.w400,
        color: colors.onSurface,
      ),
      headlineLarge: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 32,
        fontWeight: FontWeight.w700,
        color: colors.onSurface,
      ),
      headlineMedium: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 28,
        fontWeight: FontWeight.w700,
        color: colors.onSurface,
      ),
      headlineSmall: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 24,
        fontWeight: FontWeight.w700,
        color: colors.onSurface,
      ),
      titleLarge: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 22,
        fontWeight: FontWeight.w600,
        color: colors.onSurface,
      ),
      titleMedium: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: colors.onSurface,
      ),
      titleSmall: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: colors.onSurface,
      ),
      bodyLarge: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: colors.onSurface,
      ),
      bodyMedium: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: colors.onSurface,
      ),
      bodySmall: const TextStyle(
        fontFamily: _fontFamily,
        fontSize: 12,
        fontWeight: FontWeight.w400,
        color: EnhancedDarkColors.textSecondary,
      ),
      labelLarge: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: colors.onSurface,
      ),
      labelMedium: TextStyle(
        fontFamily: _fontFamily,
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: colors.onSurface,
      ),
      labelSmall: const TextStyle(
        fontFamily: _fontFamily,
        fontSize: 11,
        fontWeight: FontWeight.w500,
        color: EnhancedDarkColors.textSecondary,
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Preset Themes - ثيمات معدة مسبقاً
  // ─────────────────────────────────────────────────────────────────────────

  /// Standard dark theme
  static ThemeData get standard => build(variant: DarkThemeVariant.standard);

  /// Deep dark theme (#0D0D0D)
  static ThemeData get deep => build(variant: DarkThemeVariant.deep);

  /// AMOLED black theme (#000000)
  static ThemeData get amoled => build(variant: DarkThemeVariant.amoled);

  /// Charcoal dark theme
  static ThemeData get charcoal => build(variant: DarkThemeVariant.charcoal);

  /// High contrast dark theme
  static ThemeData get highContrast => build(variant: DarkThemeVariant.highContrast);

  /// SAHOOL branded green-tinted dark theme
  static ThemeData get sahoolGreen => build(variant: DarkThemeVariant.sahoolGreen);

  /// AMOLED with blue accent
  static ThemeData get amoledBlue => build(
    variant: DarkThemeVariant.amoled,
    accent: DarkThemeAccent.blue,
  );

  /// AMOLED with purple accent
  static ThemeData get amoledPurple => build(
    variant: DarkThemeVariant.amoled,
    accent: DarkThemeAccent.purple,
  );

  /// Deep dark with cyan accent
  static ThemeData get deepCyan => build(
    variant: DarkThemeVariant.deep,
    accent: DarkThemeAccent.cyan,
  );

  /// Deep dark with gold accent
  static ThemeData get deepGold => build(
    variant: DarkThemeVariant.deep,
    accent: DarkThemeAccent.gold,
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Classes
// ═══════════════════════════════════════════════════════════════════════════

class _DarkColorConfig {
  final Color background;
  final Color surface;
  final Color surfaceElevated;
  final Color onSurface;
  final Color border;
  final Color borderSubtle;
  final Color divider;

  const _DarkColorConfig({
    required this.background,
    required this.surface,
    required this.surfaceElevated,
    required this.onSurface,
    required this.border,
    required this.borderSubtle,
    required this.divider,
  });
}

class _AccentColorConfig {
  final Color primary;
  final Color secondary;
  final Color dark;
  final Color onPrimary;
  final Color onSecondary;

  const _AccentColorConfig({
    required this.primary,
    required this.secondary,
    required this.dark,
    required this.onPrimary,
    required this.onSecondary,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Extension for Theme Access
// ═══════════════════════════════════════════════════════════════════════════

extension DarkThemeExtension on BuildContext {
  /// Check if current theme is dark
  bool get isDarkMode => Theme.of(this).brightness == Brightness.dark;

  /// Check if current theme is AMOLED dark
  bool get isAmoledDark =>
      isDarkMode &&
      Theme.of(this).scaffoldBackgroundColor == EnhancedDarkColors.backgroundAmoled;

  /// Check if current theme is deep dark
  bool get isDeepDark =>
      isDarkMode &&
      Theme.of(this).scaffoldBackgroundColor == EnhancedDarkColors.backgroundDeep;
}
