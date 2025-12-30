import 'package:flutter/material.dart';

/// SAHOOL Design System - Agri-Industrial Design Language
/// مصمم للاستخدام الميداني تحت أشعة الشمس وبالقفازات
///
/// Key Principles:
/// - High Contrast: للرؤية تحت ضوء الشمس الساطع
/// - Big Touch Targets: للاستخدام بالقفازات
/// - Glanceability: فهم الحالة في أجزاء من الثانية

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
      textTheme: const TextTheme().apply(
        fontFamily: 'IBMPlexSansArabic',
        bodyColor: SahoolColors.textDark,
        displayColor: SahoolColors.textDark,
      ),

      // تحسين الكروت لتكون بارزة
      cardTheme: CardThemeData(
        elevation: 4,
        shadowColor: Colors.black.withOpacity(0.1),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        color: Colors.white,
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),

      // تحسين الأزرار لتكون ضخمة وواضحة (للقفازات)
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
          elevation: 6,
          shadowColor: SahoolColors.primary.withOpacity(0.4),
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          minimumSize: const Size(120, 56), // حجم أدنى كبير
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // أزرار ثانوية
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: SahoolColors.primary,
          side: const BorderSide(color: SahoolColors.primary, width: 2),
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          minimumSize: const Size(120, 56),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),

      // أزرار نصية
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: SahoolColors.primary,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          textStyle: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ),

      // تحسين شريط التطبيق
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        iconTheme: IconThemeData(color: SahoolColors.primary, size: 28),
        titleTextStyle: TextStyle(
          fontFamily: 'IBMPlexSansArabic',
          color: SahoolColors.textDark,
          fontSize: 20,
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

      // حقول الإدخال
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.grey[100],
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: SahoolColors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: SahoolColors.danger, width: 2),
        ),
        labelStyle: const TextStyle(color: SahoolColors.textSecondary),
        hintStyle: TextStyle(color: Colors.grey[400]),
      ),

      // Chips
      chipTheme: ChipThemeData(
        backgroundColor: Colors.grey[200],
        selectedColor: SahoolColors.primary.withOpacity(0.2),
        labelStyle: const TextStyle(fontSize: 14),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),

      // Divider
      dividerTheme: DividerThemeData(
        color: Colors.grey[200],
        thickness: 1,
        space: 24,
      ),

      // SnackBar
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        backgroundColor: SahoolColors.textDark,
      ),

      // Dialog
      dialogTheme: DialogThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        titleTextStyle: const TextStyle(
          fontFamily: 'IBMPlexSansArabic',
          fontSize: 20,
          fontWeight: FontWeight.bold,
          color: SahoolColors.textDark,
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
      textTheme: ThemeData.dark().textTheme.apply(
        fontFamily: 'IBMPlexSansArabic',
      ),

      cardTheme: CardThemeData(
        elevation: 4,
        color: SahoolColors.surfaceDark,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),

      appBarTheme: const AppBarTheme(
        backgroundColor: SahoolColors.surfaceDark,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontFamily: 'IBMPlexSansArabic',
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

/// Shadow Presets - ظلال جاهزة
class SahoolShadows {
  static List<BoxShadow> get small => [
    BoxShadow(
      color: Colors.black.withOpacity(0.08),
      blurRadius: 8,
      offset: const Offset(0, 2),
    ),
  ];

  static List<BoxShadow> get medium => [
    BoxShadow(
      color: Colors.black.withOpacity(0.12),
      blurRadius: 16,
      offset: const Offset(0, 4),
    ),
  ];

  static List<BoxShadow> get large => [
    BoxShadow(
      color: Colors.black.withOpacity(0.16),
      blurRadius: 24,
      offset: const Offset(0, 8),
    ),
  ];

  static List<BoxShadow> colored(Color color) => [
    BoxShadow(
      color: color.withOpacity(0.3),
      blurRadius: 12,
      offset: const Offset(0, 6),
    ),
  ];
}

/// Border Radius Presets - زوايا جاهزة
class SahoolRadius {
  static const double small = 8.0;
  static const double medium = 12.0;
  static const double large = 16.0;
  static const double xlarge = 20.0;
  static const double circular = 100.0;

  static BorderRadius get smallRadius => BorderRadius.circular(small);
  static BorderRadius get mediumRadius => BorderRadius.circular(medium);
  static BorderRadius get largeRadius => BorderRadius.circular(large);
  static BorderRadius get xlargeRadius => BorderRadius.circular(xlarge);
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
