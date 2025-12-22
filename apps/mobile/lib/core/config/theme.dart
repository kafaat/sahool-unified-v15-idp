import 'package:flutter/material.dart';

/// SAHOOL Theme Configuration
/// تكوين ثيم سهول
class SahoolTheme {
  // Font Family Name (Local - faster loading)
  static const String fontFamily = 'IBMPlexSansArabic';
  // Brand Colors - ألوان العلامة التجارية
  static const Color primary = Color(0xFF367C2B);       // SAHOOL Green
  static const Color primaryLight = Color(0xFF4A9A3D);  // Light Green
  static const Color primaryDark = Color(0xFF2D6623);   // Dark Green

  static const Color secondary = Color(0xFF1E88E5);     // Blue
  static const Color accent = Color(0xFFFF9800);        // Orange

  // Background Colors
  static const Color backgroundLight = Color(0xFFF5F7F5);
  static const Color backgroundDark = Color(0xFF1A1A1A);
  static const Color surfaceLight = Colors.white;
  static const Color surfaceDark = Color(0xFF2D2D2D);

  // Status Colors - ألوان الحالة
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);

  // Priority Colors - ألوان الأولوية
  static const Color priorityP0 = Color(0xFFF44336);    // Critical - Red
  static const Color priorityP1 = Color(0xFFFF9800);    // High - Orange
  static const Color priorityP2 = Color(0xFF2196F3);    // Medium - Blue
  static const Color priorityP3 = Color(0xFF9E9E9E);    // Low - Grey

  // Crop Health Colors - ألوان صحة المحصول
  static const Color healthExcellent = Color(0xFF2E7D32);
  static const Color healthGood = Color(0xFF4CAF50);
  static const Color healthModerate = Color(0xFFFF9800);
  static const Color healthPoor = Color(0xFFF44336);

  // Light Theme
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    fontFamily: fontFamily,

    colorScheme: const ColorScheme.light(
      primary: primary,
      primaryContainer: primaryLight,
      secondary: secondary,
      secondaryContainer: Color(0xFFBBDEFB),
      surface: surfaceLight,
      error: error,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: Color(0xFF1A1A1A),
      onError: Colors.white,
    ),

    scaffoldBackgroundColor: backgroundLight,

    // AppBar
    appBarTheme: AppBarTheme(
      backgroundColor: primary,
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontFamily: fontFamily,
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: Colors.white,
      ),
    ),

    // Bottom Navigation
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Colors.white,
      selectedItemColor: primary,
      unselectedItemColor: Colors.grey,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
    ),

    // Card
    cardTheme: CardThemeData(
      elevation: 2,
      shadowColor: Colors.black.withOpacity(0.1),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    ),

    // Buttons
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primary,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: TextStyle(
          fontFamily: fontFamily,
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),

    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: primary,
        side: const BorderSide(color: primary, width: 2),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    ),

    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: primary,
        textStyle: TextStyle(
          fontFamily: fontFamily,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),

    // FAB
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: primary,
      foregroundColor: Colors.white,
      elevation: 4,
      shape: CircleBorder(),
    ),

    // Input
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.grey[100],
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
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
        borderSide: const BorderSide(color: primary, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: error, width: 2),
      ),
      labelStyle: TextStyle(color: Colors.grey[600]),
      hintStyle: TextStyle(color: Colors.grey[400]),
    ),

    // Chip
    chipTheme: ChipThemeData(
      backgroundColor: Colors.grey[200],
      selectedColor: primary.withOpacity(0.2),
      labelStyle: TextStyle(fontSize: 13, fontFamily: fontFamily),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
    ),

    // Divider
    dividerTheme: DividerThemeData(
      color: Colors.grey[200],
      thickness: 1,
      space: 24,
    ),

    // List Tile
    listTileTheme: const ListTileThemeData(
      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      horizontalTitleGap: 12,
    ),

    // Tab Bar
    tabBarTheme: TabBarThemeData(
      labelColor: Colors.white,
      unselectedLabelColor: Colors.white70,
      indicatorColor: Colors.white,
      labelStyle: TextStyle(fontFamily: fontFamily, fontWeight: FontWeight.bold),
    ),

    // Dialog
    dialogTheme: DialogThemeData(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      titleTextStyle: TextStyle(
        fontFamily: fontFamily,
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: const Color(0xFF1A1A1A),
      ),
    ),

    // SnackBar
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  );

  // Dark Theme
  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    fontFamily: fontFamily,

    colorScheme: const ColorScheme.dark(
      primary: primaryLight,
      primaryContainer: primary,
      secondary: secondary,
      surface: surfaceDark,
      error: error,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onSurface: Colors.white,
    ),

    scaffoldBackgroundColor: backgroundDark,

    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF2D2D2D),
      foregroundColor: Colors.white,
      elevation: 0,
      centerTitle: true,
    ),

    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: Color(0xFF2D2D2D),
      selectedItemColor: primaryLight,
      unselectedItemColor: Colors.grey,
      type: BottomNavigationBarType.fixed,
    ),

    cardTheme: CardThemeData(
      elevation: 2,
      color: surfaceDark,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
    ),

    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryLight,
        foregroundColor: Colors.white,
      ),
    ),
  );

  // Helper Methods

  /// Get priority color by level
  static Color getPriorityColor(String priority) {
    switch (priority.toUpperCase()) {
      case 'P0':
      case 'URGENT':
      case 'CRITICAL':
        return priorityP0;
      case 'P1':
      case 'HIGH':
        return priorityP1;
      case 'P2':
      case 'MEDIUM':
        return priorityP2;
      case 'P3':
      case 'LOW':
      default:
        return priorityP3;
    }
  }

  /// Get status color
  static Color getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'done':
      case 'completed':
      case 'success':
        return success;
      case 'in_progress':
      case 'active':
      case 'pending':
        return warning;
      case 'canceled':
      case 'failed':
      case 'error':
        return error;
      case 'open':
      case 'new':
      default:
        return info;
    }
  }

  /// Get health score color
  static Color getHealthColor(double score) {
    if (score >= 0.8) return healthExcellent;
    if (score >= 0.6) return healthGood;
    if (score >= 0.4) return healthModerate;
    return healthPoor;
  }

  /// Get health label in Arabic
  static String getHealthLabel(double score) {
    if (score >= 0.8) return 'ممتاز';
    if (score >= 0.6) return 'جيد';
    if (score >= 0.4) return 'متوسط';
    return 'ضعيف';
  }
}
