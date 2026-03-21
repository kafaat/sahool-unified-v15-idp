import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'sahool_theme.dart';
import 'sahool_pro_theme.dart';
import 'enhanced_dark_theme.dart';
import 'glass_colors.dart';

/// SAHOOL App Theme System
/// نظام ثيم تطبيق سهول
///
/// Central theme management integrating:
/// - Glassmorphism themes | ثيمات الزجاج
/// - Light/Dark modes | الأوضاع الفاتحة والداكنة
/// - Custom accent colors | ألوان مخصصة
/// - Glass theme variants | متغيرات ثيم الزجاج

// ═══════════════════════════════════════════════════════════════════════════
// Theme Mode Enum
// ═══════════════════════════════════════════════════════════════════════════

/// Available theme modes
enum AppThemeMode {
  /// System default
  system,

  /// Light mode
  light,

  /// Dark mode (standard)
  dark,

  /// Deep dark mode (#0D0D0D)
  deepDark,

  /// AMOLED black mode (#000000)
  amoled,

  /// High contrast mode
  highContrast,
}

/// Available theme styles
enum AppThemeStyle {
  /// Standard SAHOOL theme
  standard,

  /// Pro (John Deere inspired) theme
  pro,

  /// Glassmorphism theme
  glass,

  /// Organic/Bento theme
  organic,

  /// Accessibility-focused theme
  accessible,
}

// ═══════════════════════════════════════════════════════════════════════════
// App Theme Configuration
// ═══════════════════════════════════════════════════════════════════════════

/// Theme configuration class
class AppThemeConfig {
  final AppThemeMode mode;
  final AppThemeStyle style;
  final Color? customAccentColor;
  final DarkThemeAccent darkAccent;
  final bool useGlassEffects;
  final double glassBlurIntensity;
  final double glassOpacity;

  const AppThemeConfig({
    this.mode = AppThemeMode.system,
    this.style = AppThemeStyle.standard,
    this.customAccentColor,
    this.darkAccent = DarkThemeAccent.green,
    this.useGlassEffects = true,
    this.glassBlurIntensity = 10.0,
    this.glassOpacity = 0.1,
  });

  AppThemeConfig copyWith({
    AppThemeMode? mode,
    AppThemeStyle? style,
    Color? customAccentColor,
    DarkThemeAccent? darkAccent,
    bool? useGlassEffects,
    double? glassBlurIntensity,
    double? glassOpacity,
  }) {
    return AppThemeConfig(
      mode: mode ?? this.mode,
      style: style ?? this.style,
      customAccentColor: customAccentColor ?? this.customAccentColor,
      darkAccent: darkAccent ?? this.darkAccent,
      useGlassEffects: useGlassEffects ?? this.useGlassEffects,
      glassBlurIntensity: glassBlurIntensity ?? this.glassBlurIntensity,
      glassOpacity: glassOpacity ?? this.glassOpacity,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// App Theme Builder
// ═══════════════════════════════════════════════════════════════════════════

/// Main theme builder for SAHOOL app
class AppTheme {
  AppTheme._();

  static const String fontFamily = 'IBMPlexSansArabic';

  // ─────────────────────────────────────────────────────────────────────────
  // Primary Colors
  // ─────────────────────────────────────────────────────────────────────────

  /// SAHOOL brand green
  static const Color primaryGreen = Color(0xFF367C2B);

  /// Light green variant
  static const Color primaryGreenLight = Color(0xFF4CAF50);

  /// Dark green variant
  static const Color primaryGreenDark = Color(0xFF1B5E20);

  /// Harvest gold accent
  static const Color accentGold = Color(0xFFD4A84B);

  /// Info blue
  static const Color infoBlue = Color(0xFF2196F3);

  /// Warning orange
  static const Color warningOrange = Color(0xFFFF9800);

  /// Error red
  static const Color errorRed = Color(0xFFF44336);

  /// Success green
  static const Color successGreen = Color(0xFF4CAF50);

  // ─────────────────────────────────────────────────────────────────────────
  // Build Theme
  // ─────────────────────────────────────────────────────────────────────────

  /// Build theme from configuration
  static ThemeData build({
    required AppThemeConfig config,
    required Brightness brightness,
  }) {
    final isDark = brightness == Brightness.dark ||
        config.mode == AppThemeMode.dark ||
        config.mode == AppThemeMode.deepDark ||
        config.mode == AppThemeMode.amoled;

    // Get base theme based on style
    ThemeData baseTheme;

    switch (config.style) {
      case AppThemeStyle.standard:
        baseTheme = isDark ? SahoolTheme.darkTheme : SahoolTheme.lightTheme;
        break;
      case AppThemeStyle.pro:
        baseTheme = isDark ? SahoolProTheme.darkTheme : SahoolProTheme.theme;
        break;
      case AppThemeStyle.glass:
        baseTheme = isDark
            ? _buildGlassDarkTheme(config)
            : _buildGlassLightTheme(config);
        break;
      case AppThemeStyle.organic:
        baseTheme = isDark ? SahoolTheme.darkTheme : SahoolTheme.lightTheme;
        break;
      case AppThemeStyle.accessible:
        baseTheme = isDark ? SahoolTheme.darkTheme : SahoolTheme.lightTheme;
        break;
    }

    // Apply dark mode variant if needed
    if (isDark) {
      switch (config.mode) {
        case AppThemeMode.deepDark:
          baseTheme = EnhancedDarkTheme.build(
            variant: DarkThemeVariant.deep,
            accent: config.darkAccent,
          );
          break;
        case AppThemeMode.amoled:
          baseTheme = EnhancedDarkTheme.build(
            variant: DarkThemeVariant.amoled,
            accent: config.darkAccent,
          );
          break;
        case AppThemeMode.highContrast:
          baseTheme = EnhancedDarkTheme.build(
            variant: DarkThemeVariant.highContrast,
            accent: config.darkAccent,
          );
          break;
        default:
          break;
      }
    }

    // Apply custom accent color if provided
    if (config.customAccentColor != null) {
      baseTheme = _applyCustomAccent(baseTheme, config.customAccentColor!);
    }

    return baseTheme;
  }

  /// Get light theme
  static ThemeData light({AppThemeConfig? config}) {
    return build(
      config: config ?? const AppThemeConfig(),
      brightness: Brightness.light,
    );
  }

  /// Get dark theme
  static ThemeData dark({AppThemeConfig? config}) {
    return build(
      config: config ?? const AppThemeConfig(mode: AppThemeMode.dark),
      brightness: Brightness.dark,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Glass Theme Builders
  // ─────────────────────────────────────────────────────────────────────────

  /// Build glassmorphism light theme
  static ThemeData _buildGlassLightTheme(AppThemeConfig config) {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      fontFamily: fontFamily,

      // Color Scheme
      colorScheme: ColorScheme.light(
        primary: primaryGreen,
        primaryContainer: primaryGreenLight,
        secondary: accentGold,
        secondaryContainer: accentGold.withOpacity(0.3),
        surface: const Color(0xFFFAFAFA),
        error: errorRed,
        onPrimary: Colors.white,
        onSecondary: Colors.black87,
        onSurface: const Color(0xFF1A1A1A),
        outline: Colors.black12,
      ),

      scaffoldBackgroundColor: const Color(0xFFF5F7FA),

      // AppBar - Glass style
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.white.withOpacity(config.glassOpacity),
        foregroundColor: const Color(0xFF1A1A1A),
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        systemOverlayStyle: SystemUiOverlayStyle.dark.copyWith(
          statusBarColor: Colors.transparent,
        ),
        titleTextStyle: const TextStyle(
          fontFamily: fontFamily,
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: Color(0xFF1A1A1A),
        ),
        iconTheme: const IconThemeData(
          color: primaryGreen,
          size: 24,
        ),
      ),

      // Card Theme - Glass style
      cardTheme: CardTheme(
        elevation: 0,
        color: Colors.white.withOpacity(0.8),
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(
            color: Colors.white.withOpacity(0.3),
            width: 1,
          ),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),

      // Bottom Navigation - Glass style
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: Colors.white.withOpacity(0.8),
        selectedItemColor: primaryGreen,
        unselectedItemColor: Colors.black54,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
        selectedLabelStyle: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),

      // Elevated Button
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryGreen,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          minimumSize: const Size(120, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: const TextStyle(
            fontFamily: fontFamily,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // Input Decoration - Glass style
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white.withOpacity(0.5),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.black.withOpacity(0.1)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.black.withOpacity(0.1)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: primaryGreen, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: errorRed, width: 2),
        ),
        labelStyle: const TextStyle(color: Colors.black54),
        hintStyle: const TextStyle(color: Colors.black38),
      ),

      // FAB - Glass style
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: primaryGreen.withOpacity(0.9),
        foregroundColor: Colors.white,
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),

      // Dialog - Glass style
      dialogTheme: DialogTheme(
        backgroundColor: Colors.white.withOpacity(0.95),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: BorderSide(color: Colors.white.withOpacity(0.3)),
        ),
      ),

      // Bottom Sheet - Glass style
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: Colors.white.withOpacity(0.95),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
        ),
      ),

      // Chip Theme
      chipTheme: ChipThemeData(
        backgroundColor: Colors.white.withOpacity(0.6),
        selectedColor: primaryGreen.withOpacity(0.2),
        labelStyle: const TextStyle(fontFamily: fontFamily, fontSize: 14),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(color: Colors.black.withOpacity(0.1)),
        ),
      ),

      // Divider
      dividerTheme: const DividerThemeData(
        color: Colors.black12,
        thickness: 1,
        space: 24,
      ),

      // Snackbar
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: const Color(0xFF1A1A1A).withOpacity(0.9),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),

      // Highlight and Splash
      highlightColor: primaryGreen.withOpacity(0.1),
      splashColor: primaryGreen.withOpacity(0.2),
      focusColor: primaryGreen.withOpacity(0.15),
      hoverColor: primaryGreen.withOpacity(0.08),
    );
  }

  /// Build glassmorphism dark theme
  static ThemeData _buildGlassDarkTheme(AppThemeConfig config) {
    const glassColors = GlassColors.dark;

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      fontFamily: fontFamily,

      // Color Scheme
      colorScheme: ColorScheme.dark(
        primary: primaryGreenLight,
        primaryContainer: primaryGreen,
        secondary: accentGold,
        secondaryContainer: accentGold.withOpacity(0.3),
        surface: const Color(0xFF1E1E1E),
        error: const Color(0xFFEF5350),
        onPrimary: Colors.black,
        onSecondary: Colors.black,
        onSurface: Colors.white,
        outline: Colors.white12,
      ),

      scaffoldBackgroundColor: const Color(0xFF121212),

      // AppBar - Glass style
      appBarTheme: AppBarTheme(
        backgroundColor: glassColors.glassDark.withOpacity(config.glassOpacity),
        foregroundColor: Colors.white,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        systemOverlayStyle: SystemUiOverlayStyle.light.copyWith(
          statusBarColor: Colors.transparent,
        ),
        titleTextStyle: const TextStyle(
          fontFamily: fontFamily,
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
        iconTheme: const IconThemeData(
          color: primaryGreenLight,
          size: 24,
        ),
      ),

      // Card Theme - Glass style
      cardTheme: CardTheme(
        elevation: 0,
        color: glassColors.glassDark.withOpacity(0.8),
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(
            color: glassColors.borderDark,
            width: 1,
          ),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),

      // Bottom Navigation - Glass style
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: glassColors.glassDark.withOpacity(0.8),
        selectedItemColor: primaryGreenLight,
        unselectedItemColor: Colors.white54,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
        selectedLabelStyle: const TextStyle(
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),

      // Elevated Button
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryGreenLight,
          foregroundColor: Colors.black,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          minimumSize: const Size(120, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: const TextStyle(
            fontFamily: fontFamily,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // Input Decoration - Glass style
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: glassColors.glassDark.withOpacity(0.5),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: glassColors.borderDark),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: glassColors.borderDark),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: primaryGreenLight, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFEF5350), width: 2),
        ),
        labelStyle: const TextStyle(color: Colors.white70),
        hintStyle: const TextStyle(color: Colors.white38),
      ),

      // FAB - Glass style
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: primaryGreenLight.withOpacity(0.9),
        foregroundColor: Colors.black,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),

      // Dialog - Glass style
      dialogTheme: DialogTheme(
        backgroundColor: glassColors.glassDark.withOpacity(0.95),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: BorderSide(color: glassColors.borderDark),
        ),
      ),

      // Bottom Sheet - Glass style
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: glassColors.glassDark.withOpacity(0.95),
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
        ),
      ),

      // Chip Theme
      chipTheme: ChipThemeData(
        backgroundColor: glassColors.glassDark.withOpacity(0.6),
        selectedColor: primaryGreenLight.withOpacity(0.2),
        labelStyle: const TextStyle(fontFamily: fontFamily, fontSize: 14),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(color: glassColors.borderDark),
        ),
      ),

      // Divider
      dividerTheme: DividerThemeData(
        color: glassColors.borderDark,
        thickness: 1,
        space: 24,
      ),

      // Snackbar
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: const Color(0xFF2D2D2D).withOpacity(0.95),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),

      // Highlight and Splash
      highlightColor: primaryGreenLight.withOpacity(0.1),
      splashColor: primaryGreenLight.withOpacity(0.2),
      focusColor: primaryGreenLight.withOpacity(0.15),
      hoverColor: primaryGreenLight.withOpacity(0.08),
    );
  }

  /// Apply custom accent color to theme
  static ThemeData _applyCustomAccent(ThemeData theme, Color accent) {
    final onAccent = accent.computeLuminance() > 0.5 ? Colors.black : Colors.white;

    return theme.copyWith(
      colorScheme: theme.colorScheme.copyWith(
        primary: accent,
        onPrimary: onAccent,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: theme.elevatedButtonTheme.style?.copyWith(
          backgroundColor: WidgetStateProperty.all(accent),
          foregroundColor: WidgetStateProperty.all(onAccent),
        ),
      ),
      floatingActionButtonTheme: theme.floatingActionButtonTheme.copyWith(
        backgroundColor: accent,
        foregroundColor: onAccent,
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: accent,
      ),
      sliderTheme: SliderThemeData(
        activeTrackColor: accent,
        thumbColor: accent,
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Preset Themes
  // ─────────────────────────────────────────────────────────────────────────

  /// Standard light theme
  static ThemeData get standardLight => light();

  /// Standard dark theme
  static ThemeData get standardDark => dark();

  /// Glass light theme
  static ThemeData get glassLight => light(
    config: const AppThemeConfig(style: AppThemeStyle.glass),
  );

  /// Glass dark theme
  static ThemeData get glassDark => dark(
    config: const AppThemeConfig(
      mode: AppThemeMode.dark,
      style: AppThemeStyle.glass,
    ),
  );

  /// Glass AMOLED theme
  static ThemeData get glassAmoled => dark(
    config: const AppThemeConfig(
      mode: AppThemeMode.amoled,
      style: AppThemeStyle.glass,
    ),
  );

  /// Glass deep dark theme
  static ThemeData get glassDeepDark => dark(
    config: const AppThemeConfig(
      mode: AppThemeMode.deepDark,
      style: AppThemeStyle.glass,
    ),
  );

  /// Pro light theme
  static ThemeData get proLight => light(
    config: const AppThemeConfig(style: AppThemeStyle.pro),
  );

  /// Pro dark theme
  static ThemeData get proDark => dark(
    config: const AppThemeConfig(
      mode: AppThemeMode.dark,
      style: AppThemeStyle.pro,
    ),
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Theme Extensions
  // ─────────────────────────────────────────────────────────────────────────

  /// Glass configuration extension data
  static GlassThemeExtension glassExtension({
    double blurIntensity = 10.0,
    double opacity = 0.1,
    double borderRadius = 20.0,
  }) {
    return GlassThemeExtension(
      blurIntensity: blurIntensity,
      opacity: opacity,
      borderRadius: borderRadius,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Theme Extension
// ═══════════════════════════════════════════════════════════════════════════

/// Extension for glass-specific theme data
class GlassThemeExtension extends ThemeExtension<GlassThemeExtension> {
  final double blurIntensity;
  final double opacity;
  final double borderRadius;

  const GlassThemeExtension({
    this.blurIntensity = 10.0,
    this.opacity = 0.1,
    this.borderRadius = 20.0,
  });

  @override
  GlassThemeExtension copyWith({
    double? blurIntensity,
    double? opacity,
    double? borderRadius,
  }) {
    return GlassThemeExtension(
      blurIntensity: blurIntensity ?? this.blurIntensity,
      opacity: opacity ?? this.opacity,
      borderRadius: borderRadius ?? this.borderRadius,
    );
  }

  @override
  GlassThemeExtension lerp(ThemeExtension<GlassThemeExtension>? other, double t) {
    if (other is! GlassThemeExtension) return this;
    return GlassThemeExtension(
      blurIntensity: blurIntensity + (other.blurIntensity - blurIntensity) * t,
      opacity: opacity + (other.opacity - opacity) * t,
      borderRadius: borderRadius + (other.borderRadius - borderRadius) * t,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Context Extension
// ═══════════════════════════════════════════════════════════════════════════

extension AppThemeExtension on BuildContext {
  /// Get glass theme extension
  GlassThemeExtension? get glassTheme =>
      Theme.of(this).extension<GlassThemeExtension>();

  /// Check if using glass theme
  bool get isGlassTheme => glassTheme != null;

  /// Get blur intensity
  double get glassBlur => glassTheme?.blurIntensity ?? 10.0;

  /// Get glass opacity
  double get glassOpacity => glassTheme?.opacity ?? 0.1;

  /// Get glass border radius
  double get glassBorderRadius => glassTheme?.borderRadius ?? 20.0;
}
