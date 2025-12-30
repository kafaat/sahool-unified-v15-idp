import 'package:flutter/material.dart';
import 'modern_theme.dart';

/// SAHOOL Design System - Agri-Industrial Design Language
/// مصمم للاستخدام الميداني تحت أشعة الشمس وبالقفازات
///
/// Key Principles:
/// - High Contrast: للرؤية تحت ضوء الشمس الساطع
/// - Big Touch Targets: للاستخدام بالقفازات
/// - Glanceability: فهم الحالة في أجزاء من الثانية
/// - Modern Design: تصميم حديث مع تأثيرات زجاجية وتدرجات ناعمة

class SahoolColors {
  // ─────────────────────────────────────────────────────────────────────────
  // Primary Colors - الألوان الرئيسية
  // ─────────────────────────────────────────────────────────────────────────

  /// أخضر زراعي عميق (يوحي بالموثوقية)
  static const Color primary = Color(0xFF1B5E20);

  /// أخضر فاتح للحيوية
  static const Color secondary = Color(0xFF4CAF50);

  /// أخضر ساهول الأصلي
  static const Color sahoolGreen = Color(0xFF367C2B);

  // ─────────────────────────────────────────────────────────────────────────
  // Organic Colors - ألوان التصميم العضوي (Bento Grid)
  // ─────────────────────────────────────────────────────────────────────────

  /// أخضر الغابة العميق
  static const Color forestGreen = Color(0xFF2D5A3D);

  /// ذهبي الحصاد (للبطاقات المميزة)
  static const Color harvestGold = Color(0xFFD4A84B);

  /// زيتوني شاحب (للخلفيات)
  static const Color paleOlive = Color(0xFFE8E4D9);

  /// أخضر المريمية
  static const Color sageGreen = Color(0xFF87A878);

  /// كريمي دافئ
  static const Color warmCream = Color(0xFFFAF8F5);

  /// بني ترابي
  static const Color earthBrown = Color(0xFF8B7355);

  // ─────────────────────────────────────────────────────────────────────────
  // Status Colors - ألوان الحالة
  // ─────────────────────────────────────────────────────────────────────────

  /// أصفر للتحذيرات (واضح جداً في الشمس)
  static const Color warning = Color(0xFFFFD600);

  /// أحمر للخطر
  static const Color danger = Color(0xFFD32F2F);

  /// أزرق للمعلومات
  static const Color info = Color(0xFF1976D2);

  /// أخضر للنجاح
  static const Color success = Color(0xFF388E3C);

  // ─────────────────────────────────────────────────────────────────────────
  // Background Colors - ألوان الخلفية
  // ─────────────────────────────────────────────────────────────────────────

  /// أبيض مائل للرمادي (مريح للعين أكثر من الأبيض الناصع)
  static const Color background = Color(0xFFF5F7FA);

  /// خلفية داكنة
  static const Color backgroundDark = Color(0xFF1A1A1A);

  /// سطح أبيض
  static const Color surface = Color(0xFFFFFFFF);

  /// سطح داكن
  static const Color surfaceDark = Color(0xFF2D2D2D);

  // ─────────────────────────────────────────────────────────────────────────
  // Text Colors - ألوان النصوص
  // ─────────────────────────────────────────────────────────────────────────

  /// رمادي داكن للنصوص الرئيسية
  static const Color textDark = Color(0xFF263238);

  /// رمادي للنصوص الثانوية
  static const Color textSecondary = Color(0xFF607D8B);

  /// نص فاتح
  static const Color textLight = Color(0xFFFFFFFF);

  // ─────────────────────────────────────────────────────────────────────────
  // Health Colors - ألوان صحة المحصول
  // ─────────────────────────────────────────────────────────────────────────

  static const Color healthExcellent = Color(0xFF2E7D32);
  static const Color healthGood = Color(0xFF4CAF50);
  static const Color healthModerate = Color(0xFFFF9800);
  static const Color healthPoor = Color(0xFFF44336);
  static const Color healthCritical = Color(0xFFB71C1C);

  // ─────────────────────────────────────────────────────────────────────────
  // Gradient Presets - التدرجات اللونية
  // ─────────────────────────────────────────────────────────────────────────

  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primary, secondary],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient healthGradient = LinearGradient(
    colors: [healthExcellent, healthGood],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient warningGradient = LinearGradient(
    colors: [Color(0xFFFF8F00), warning],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Modern gradient presets
  static const LinearGradient organicGradient = LinearGradient(
    colors: [forestGreen, sageGreen, paleOlive],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient sunriseGradient = LinearGradient(
    colors: [harvestGold, Color(0xFFFFE082)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient earthGradient = LinearGradient(
    colors: [earthBrown, harvestGold],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Soft overlay gradients for glassmorphism
  static LinearGradient glassOverlay = LinearGradient(
    colors: [
      Colors.white.withOpacity(0.2),
      Colors.white.withOpacity(0.1),
    ],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}

/// SAHOOL Theme Configuration
class SahoolTheme {
  /// Light Theme - الثيم الفاتح
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: SahoolColors.background,
      primaryColor: SahoolColors.primary,

      // Color Scheme
      colorScheme: const ColorScheme.light(
        primary: SahoolColors.primary,
        secondary: SahoolColors.secondary,
        surface: SahoolColors.surface,
        error: SahoolColors.danger,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: SahoolColors.textDark,
      ),

      // الخط العربي: IBM Plex Sans Arabic (محلي - أسرع تحميل)
      fontFamily: 'IBMPlexSansArabic',
      textTheme: TextTheme(
        displayLarge: ModernTypography.displayLarge.copyWith(color: SahoolColors.textDark),
        displayMedium: ModernTypography.displayMedium.copyWith(color: SahoolColors.textDark),
        displaySmall: ModernTypography.displaySmall.copyWith(color: SahoolColors.textDark),
        headlineLarge: ModernTypography.headlineLarge.copyWith(color: SahoolColors.textDark),
        headlineMedium: ModernTypography.headlineMedium.copyWith(color: SahoolColors.textDark),
        headlineSmall: ModernTypography.headlineSmall.copyWith(color: SahoolColors.textDark),
        titleLarge: ModernTypography.titleLarge.copyWith(color: SahoolColors.textDark),
        titleMedium: ModernTypography.titleMedium.copyWith(color: SahoolColors.textDark),
        titleSmall: ModernTypography.titleSmall.copyWith(color: SahoolColors.textDark),
        bodyLarge: ModernTypography.bodyLarge.copyWith(color: SahoolColors.textDark),
        bodyMedium: ModernTypography.bodyMedium.copyWith(color: SahoolColors.textDark),
        bodySmall: ModernTypography.bodySmall.copyWith(color: SahoolColors.textDark),
        labelLarge: ModernTypography.labelLarge.copyWith(color: SahoolColors.textDark),
        labelMedium: ModernTypography.labelMedium.copyWith(color: SahoolColors.textDark),
        labelSmall: ModernTypography.labelSmall.copyWith(color: SahoolColors.textDark),
      ),

      // تحسين الكروت لتكون بارزة مع ظلال حديثة
      cardTheme: CardThemeData(
        elevation: 0,
        shadowColor: Colors.transparent,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        color: Colors.white,
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),

      // تحسين الأزرار لتكون ضخمة وواضحة (للقفازات) مع ظلال ملونة
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          shadowColor: Colors.transparent,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
          minimumSize: const Size(120, 56), // حجم أدنى كبير
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: ModernTypography.labelLarge.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // أزرار ثانوية
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: SahoolColors.primary,
          side: const BorderSide(color: SahoolColors.primary, width: 2),
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
          minimumSize: const Size(120, 56),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: ModernTypography.labelLarge.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // أزرار نصية
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: SahoolColors.primary,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          textStyle: ModernTypography.labelLarge.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // تحسين شريط التطبيق
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        iconTheme: const IconThemeData(color: SahoolColors.primary, size: 28),
        titleTextStyle: ModernTypography.titleLarge.copyWith(
          color: SahoolColors.textDark,
          fontWeight: FontWeight.bold,
        ),
      ),

      // شريط التنقل السفلي
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.white,
        selectedItemColor: SahoolColors.primary,
        unselectedItemColor: SahoolColors.textSecondary,
        type: BottomNavigationBarType.fixed,
        elevation: 12,
        selectedLabelStyle: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
      ),

      // FAB كبير
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: SahoolColors.primary,
        foregroundColor: Colors.white,
        elevation: 8,
        extendedPadding: EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      ),

      // حقول الإدخال مع تصميم حديث
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.grey[50],
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.grey[300]!, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: SahoolColors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: SahoolColors.danger, width: 1.5),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: SahoolColors.danger, width: 2),
        ),
        labelStyle: ModernTypography.bodyMedium.copyWith(
          color: SahoolColors.textSecondary,
        ),
        hintStyle: ModernTypography.bodyMedium.copyWith(
          color: Colors.grey[400],
        ),
      ),

      // Chips مع تصميم حديث
      chipTheme: ChipThemeData(
        backgroundColor: Colors.grey[100],
        selectedColor: SahoolColors.primary.withOpacity(0.15),
        labelStyle: ModernTypography.labelMedium,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        side: BorderSide(color: Colors.grey[300]!, width: 1),
      ),

      // Divider
      dividerTheme: DividerThemeData(
        color: Colors.grey[200],
        thickness: 1,
        space: 24,
      ),

      // SnackBar مع تصميم حديث
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        backgroundColor: SahoolColors.textDark,
        contentTextStyle: ModernTypography.bodyMedium.copyWith(
          color: Colors.white,
        ),
      ),

      // Dialog مع تصميم حديث
      dialogTheme: DialogThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        titleTextStyle: ModernTypography.headlineSmall.copyWith(
          color: SahoolColors.textDark,
          fontWeight: FontWeight.bold,
        ),
        contentTextStyle: ModernTypography.bodyMedium.copyWith(
          color: SahoolColors.textSecondary,
        ),
      ),
    );
  }

  /// Dark Theme - الثيم الداكن
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: SahoolColors.backgroundDark,
      primaryColor: SahoolColors.secondary,

      colorScheme: const ColorScheme.dark(
        primary: SahoolColors.secondary,
        secondary: SahoolColors.primary,
        surface: SahoolColors.surfaceDark,
        error: SahoolColors.danger,
      ),

      fontFamily: 'IBMPlexSansArabic',
      textTheme: TextTheme(
        displayLarge: ModernTypography.displayLarge.copyWith(color: Colors.white),
        displayMedium: ModernTypography.displayMedium.copyWith(color: Colors.white),
        displaySmall: ModernTypography.displaySmall.copyWith(color: Colors.white),
        headlineLarge: ModernTypography.headlineLarge.copyWith(color: Colors.white),
        headlineMedium: ModernTypography.headlineMedium.copyWith(color: Colors.white),
        headlineSmall: ModernTypography.headlineSmall.copyWith(color: Colors.white),
        titleLarge: ModernTypography.titleLarge.copyWith(color: Colors.white),
        titleMedium: ModernTypography.titleMedium.copyWith(color: Colors.white),
        titleSmall: ModernTypography.titleSmall.copyWith(color: Colors.white),
        bodyLarge: ModernTypography.bodyLarge.copyWith(color: Colors.white70),
        bodyMedium: ModernTypography.bodyMedium.copyWith(color: Colors.white70),
        bodySmall: ModernTypography.bodySmall.copyWith(color: Colors.white70),
        labelLarge: ModernTypography.labelLarge.copyWith(color: Colors.white),
        labelMedium: ModernTypography.labelMedium.copyWith(color: Colors.white),
        labelSmall: ModernTypography.labelSmall.copyWith(color: Colors.white),
      ),

      cardTheme: CardThemeData(
        elevation: 0,
        color: SahoolColors.surfaceDark,
        shadowColor: Colors.transparent,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),

      appBarTheme: AppBarTheme(
        backgroundColor: SahoolColors.surfaceDark,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: ModernTypography.titleLarge.copyWith(
          color: Colors.white,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

/// Shadow Presets - ظلال جاهزة (Modern Shadow System)
class SahoolShadows {
  // Soft shadows
  static List<BoxShadow> get small => ModernShadows.soft1;
  static List<BoxShadow> get medium => ModernShadows.soft3;
  static List<BoxShadow> get large => ModernShadows.soft4;

  // Layered shadows for depth
  static List<BoxShadow> get soft => ModernShadows.soft2;
  static List<BoxShadow> get layered => ModernShadows.layered2;
  static List<BoxShadow> get elevated => ModernShadows.layered3;

  // Colored shadows
  static List<BoxShadow> colored(Color color, {double intensity = 0.3}) =>
      ModernShadows.coloredShadow(color, intensity: intensity);

  // Special glow effects
  static List<BoxShadow> get greenGlow => ModernShadows.greenGlow;
  static List<BoxShadow> get blueGlow => ModernShadows.blueGlow;

  // Primary colored shadow
  static List<BoxShadow> get primaryShadow => colored(SahoolColors.primary, intensity: 0.25);
  static List<BoxShadow> get secondaryShadow => colored(SahoolColors.secondary, intensity: 0.25);
  static List<BoxShadow> get successShadow => colored(SahoolColors.success, intensity: 0.25);
  static List<BoxShadow> get warningShadow => colored(SahoolColors.warning, intensity: 0.25);
  static List<BoxShadow> get dangerShadow => colored(SahoolColors.danger, intensity: 0.25);
}

/// Border Radius Presets - زوايا جاهزة (Modern Radius System)
class SahoolRadius {
  static const double xs = 4.0;
  static const double small = 8.0;
  static const double medium = 12.0;
  static const double large = 16.0;
  static const double xlarge = 20.0;
  static const double xxlarge = 24.0;
  static const double circular = 100.0;

  static BorderRadius get xsRadius => BorderRadius.circular(xs);
  static BorderRadius get smallRadius => BorderRadius.circular(small);
  static BorderRadius get mediumRadius => BorderRadius.circular(medium);
  static BorderRadius get largeRadius => BorderRadius.circular(large);
  static BorderRadius get xlargeRadius => BorderRadius.circular(xlarge);
  static BorderRadius get xxlargeRadius => BorderRadius.circular(xxlarge);
  static BorderRadius get circularRadius => BorderRadius.circular(circular);

  // Asymmetric radius for modern cards
  static BorderRadius get modernCard => const BorderRadius.only(
    topLeft: Radius.circular(24),
    topRight: Radius.circular(24),
    bottomLeft: Radius.circular(12),
    bottomRight: Radius.circular(12),
  );

  // Soft modern radius
  static BorderRadius get softCard => BorderRadius.circular(20);
}

/// Spacing Presets - مسافات جاهزة
class SahoolSpacing {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
}
