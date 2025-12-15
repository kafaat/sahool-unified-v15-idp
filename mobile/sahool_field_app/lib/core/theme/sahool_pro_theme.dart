import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// SAHOOL Pro Colors - مستوحاة من John Deere Operations Center
/// ألوان صناعية زراعية للرؤية الواضحة تحت أشعة الشمس
class SahoolProColors {
  // الألوان الأساسية - Industrial Agricultural Colors
  static const Color johnGreen = Color(0xFF367C2B);      // الأخضر الصناعي (John Deere)
  static const Color deepJungle = Color(0xFF1B4D3E);     // للخلفيات الداكنة
  static const Color tractorYellow = Color(0xFFFFDE00);  // للتنبيهات (High Visibility)
  static const Color alertRed = Color(0xFFD32F2F);       // للخطر
  static const Color warningOrange = Color(0xFFFF9800);  // للتحذيرات
  static const Color soilBrown = Color(0xFF5D4037);      // للعناصر الأرضية

  // ألوان السطح - Surface Colors
  static const Color surfaceWhite = Color(0xFFFAFAFA);
  static const Color surfaceLight = Color(0xFFF5F5F5);
  static const Color cardWhite = Color(0xFFFFFFFF);

  // ألوان النصوص - Text Colors
  static const Color textDark = Color(0xFF212121);
  static const Color textMedium = Color(0xFF616161);
  static const Color textLight = Color(0xFF9E9E9E);

  // ألوان الحالة - Status Colors
  static const Color statusSynced = Color(0xFF4CAF50);
  static const Color statusPending = Color(0xFFFF9800);
  static const Color statusOffline = Color(0xFF9E9E9E);
  static const Color statusError = Color(0xFFF44336);

  // ألوان NDVI - Crop Health Colors
  static const Color ndviExcellent = Color(0xFF1B5E20);
  static const Color ndviGood = Color(0xFF4CAF50);
  static const Color ndviModerate = Color(0xFFFFEB3B);
  static const Color ndviPoor = Color(0xFFFF9800);
  static const Color ndviCritical = Color(0xFFF44336);
}

/// SAHOOL Pro Theme - تصميم صناعي زراعي احترافي
class SahoolProTheme {
  static ThemeData get theme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,

      // Color Scheme
      colorScheme: ColorScheme.fromSeed(
        seedColor: SahoolProColors.johnGreen,
        primary: SahoolProColors.johnGreen,
        secondary: SahoolProColors.tractorYellow,
        surface: SahoolProColors.surfaceWhite,
        error: SahoolProColors.alertRed,
        onPrimary: Colors.white,
        onSecondary: SahoolProColors.textDark,
      ),

      // الخط العربي الصناعي الواضح
      textTheme: GoogleFonts.almaraiTextTheme().apply(
        bodyColor: SahoolProColors.textDark,
        displayColor: SahoolProColors.deepJungle,
      ),

      // تصميم الكروت (حواف حادة قليلاً للطابع الصناعي)
      cardTheme: CardTheme(
        elevation: 4,
        color: SahoolProColors.cardWhite,
        shadowColor: Colors.black.withOpacity(0.15),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: Colors.grey.shade200, width: 1),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      ),

      // تصميم الأزرار العائمة (كبيرة وواضحة)
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: SahoolProColors.johnGreen,
        foregroundColor: Colors.white,
        elevation: 8,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        extendedPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      ),

      // تصميم الأزرار العادية
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: SahoolProColors.johnGreen,
          foregroundColor: Colors.white,
          elevation: 4,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          minimumSize: const Size(120, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),

      // تصميم حقول الإدخال
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: SahoolProColors.johnGreen, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: SahoolProColors.alertRed, width: 2),
        ),
      ),

      // تصميم شريط التطبيق
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.white,
        foregroundColor: SahoolProColors.textDark,
        elevation: 2,
        shadowColor: Colors.black.withOpacity(0.1),
        centerTitle: true,
        titleTextStyle: GoogleFonts.almarai(
          color: SahoolProColors.textDark,
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),

      // تصميم Bottom Navigation
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.white,
        selectedItemColor: SahoolProColors.johnGreen,
        unselectedItemColor: SahoolProColors.textLight,
        elevation: 8,
        type: BottomNavigationBarType.fixed,
      ),

      // تصميم الـ Chips
      chipTheme: ChipThemeData(
        backgroundColor: Colors.grey.shade100,
        selectedColor: SahoolProColors.johnGreen.withOpacity(0.2),
        labelStyle: const TextStyle(fontSize: 14),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
      ),

      // تصميم الـ SnackBar
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: SahoolProColors.textDark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),

      // تصميم الـ Dialog
      dialogTheme: DialogTheme(
        backgroundColor: Colors.white,
        elevation: 16,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
    );
  }

  /// Dark Theme للاستخدام الليلي
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,

      colorScheme: ColorScheme.fromSeed(
        seedColor: SahoolProColors.johnGreen,
        brightness: Brightness.dark,
        primary: SahoolProColors.johnGreen,
        secondary: SahoolProColors.tractorYellow,
        surface: const Color(0xFF1E1E1E),
        error: SahoolProColors.alertRed,
      ),

      textTheme: GoogleFonts.almaraiTextTheme(ThemeData.dark().textTheme),

      cardTheme: CardTheme(
        elevation: 4,
        color: const Color(0xFF2D2D2D),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }
}

/// ظلال جاهزة للاستخدام
class SahoolProShadows {
  static List<BoxShadow> get small => [
    BoxShadow(
      color: Colors.black.withOpacity(0.08),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
  ];

  static List<BoxShadow> get medium => [
    BoxShadow(
      color: Colors.black.withOpacity(0.12),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
  ];

  static List<BoxShadow> get large => [
    BoxShadow(
      color: Colors.black.withOpacity(0.16),
      blurRadius: 16,
      offset: const Offset(0, 8),
    ),
  ];

  static List<BoxShadow> elevated(Color color) => [
    BoxShadow(
      color: color.withOpacity(0.3),
      blurRadius: 12,
      offset: const Offset(0, 6),
    ),
  ];
}
