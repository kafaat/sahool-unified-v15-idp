// ============================================
// SAHOOL Theme - نظام الثيم الكامل
// John Deere Inspired Design System
// ============================================

import 'package:flutter/material.dart';
import 'john_deere_colors.dart';

class SahoolTheme {
  SahoolTheme._();

  // ============================================
  // LIGHT THEME
  // ============================================
  
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    
    // Colors
    colorScheme: const ColorScheme.light(
      primary: JohnDeereColors.primary,
      primaryContainer: JohnDeereColors.primaryLight,
      secondary: JohnDeereColors.secondary,
      secondaryContainer: JohnDeereColors.secondaryLight,
      surface: JohnDeereColors.surface,
      background: JohnDeereColors.background,
      error: JohnDeereColors.error,
      onPrimary: JohnDeereColors.textOnPrimary,
      onSecondary: JohnDeereColors.textPrimary,
      onSurface: JohnDeereColors.textPrimary,
      onBackground: JohnDeereColors.textPrimary,
      onError: JohnDeereColors.textOnPrimary,
    ),
    
    // Scaffold
    scaffoldBackgroundColor: JohnDeereColors.background,
    
    // AppBar
    appBarTheme: const AppBarTheme(
      elevation: 0,
      centerTitle: true,
      backgroundColor: JohnDeereColors.primary,
      foregroundColor: JohnDeereColors.textOnPrimary,
      iconTheme: IconThemeData(color: JohnDeereColors.textOnPrimary),
      titleTextStyle: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: JohnDeereColors.textOnPrimary,
      ),
    ),
    
    // Card
    cardTheme: CardTheme(
      elevation: 2,
      color: JohnDeereColors.card,
      shadowColor: JohnDeereColors.primary.withOpacity(0.1),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
    ),
    
    // Elevated Button
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: JohnDeereColors.primary,
        foregroundColor: JohnDeereColors.textOnPrimary,
        elevation: 2,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),
    
    // Outlined Button
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: JohnDeereColors.primary,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        side: const BorderSide(color: JohnDeereColors.primary, width: 2),
        textStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    ),
    
    // Text Button
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: JohnDeereColors.primary,
        textStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    
    // Floating Action Button
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: JohnDeereColors.secondary,
      foregroundColor: JohnDeereColors.textPrimary,
      elevation: 4,
      shape: CircleBorder(),
    ),
    
    // Input Decoration
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: JohnDeereColors.card,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: JohnDeereColors.border),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: JohnDeereColors.border),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: JohnDeereColors.primary, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: JohnDeereColors.error),
      ),
      labelStyle: const TextStyle(
        fontFamily: 'Cairo',
        color: JohnDeereColors.textSecondary,
      ),
      hintStyle: const TextStyle(
        fontFamily: 'Cairo',
        color: JohnDeereColors.textDisabled,
      ),
      prefixIconColor: JohnDeereColors.primary,
      suffixIconColor: JohnDeereColors.textSecondary,
    ),
    
    // Bottom Navigation Bar
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: JohnDeereColors.card,
      selectedItemColor: JohnDeereColors.primary,
      unselectedItemColor: JohnDeereColors.textSecondary,
      type: BottomNavigationBarType.fixed,
      elevation: 8,
      selectedLabelStyle: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 12,
        fontWeight: FontWeight.bold,
      ),
      unselectedLabelStyle: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 12,
      ),
    ),
    
    // Navigation Bar (Material 3)
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: JohnDeereColors.card,
      indicatorColor: JohnDeereColors.primaryLight.withOpacity(0.3),
      iconTheme: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return const IconThemeData(color: JohnDeereColors.primary);
        }
        return const IconThemeData(color: JohnDeereColors.textSecondary);
      }),
      labelTextStyle: MaterialStateProperty.resolveWith((states) {
        if (states.contains(MaterialState.selected)) {
          return const TextStyle(
            fontFamily: 'Cairo',
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: JohnDeereColors.primary,
          );
        }
        return const TextStyle(
          fontFamily: 'Cairo',
          fontSize: 12,
          color: JohnDeereColors.textSecondary,
        );
      }),
    ),
    
    // Chip
    chipTheme: ChipThemeData(
      backgroundColor: JohnDeereColors.surface,
      selectedColor: JohnDeereColors.primaryLight,
      disabledColor: JohnDeereColors.divider,
      labelStyle: const TextStyle(
        fontFamily: 'Cairo',
        fontSize: 14,
        color: JohnDeereColors.textPrimary,
      ),
      secondaryLabelStyle: const TextStyle(
        fontFamily: 'Cairo',
        fontSize: 14,
        color: JohnDeereColors.textOnPrimary,
      ),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: JohnDeereColors.border),
      ),
    ),
    
    // Dialog
    dialogTheme: DialogTheme(
      backgroundColor: JohnDeereColors.card,
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      titleTextStyle: const TextStyle(
        fontFamily: 'Cairo',
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: JohnDeereColors.textPrimary,
      ),
      contentTextStyle: const TextStyle(
        fontFamily: 'Cairo',
        fontSize: 16,
        color: JohnDeereColors.textSecondary,
      ),
    ),
    
    // Bottom Sheet
    bottomSheetTheme: const BottomSheetThemeData(
      backgroundColor: JohnDeereColors.card,
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      dragHandleColor: JohnDeereColors.divider,
      dragHandleSize: Size(40, 4),
    ),
    
    // Snackbar
    snackBarTheme: SnackBarThemeData(
      backgroundColor: JohnDeereColors.textPrimary,
      contentTextStyle: const TextStyle(
        fontFamily: 'Cairo',
        fontSize: 14,
        color: JohnDeereColors.textOnPrimary,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      behavior: SnackBarBehavior.floating,
    ),
    
    // Divider
    dividerTheme: const DividerThemeData(
      color: JohnDeereColors.divider,
      thickness: 1,
      space: 1,
    ),
    
    // List Tile
    listTileTheme: const ListTileThemeData(
      contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      iconColor: JohnDeereColors.primary,
      textColor: JohnDeereColors.textPrimary,
      titleTextStyle: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: JohnDeereColors.textPrimary,
      ),
      subtitleTextStyle: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 14,
        color: JohnDeereColors.textSecondary,
      ),
    ),
    
    // Text Theme
    textTheme: const TextTheme(
      displayLarge: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 57,
        fontWeight: FontWeight.bold,
        color: JohnDeereColors.textPrimary,
      ),
      displayMedium: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 45,
        fontWeight: FontWeight.bold,
        color: JohnDeereColors.textPrimary,
      ),
      displaySmall: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 36,
        fontWeight: FontWeight.bold,
        color: JohnDeereColors.textPrimary,
      ),
      headlineLarge: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: JohnDeereColors.textPrimary,
      ),
      headlineMedium: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: JohnDeereColors.textPrimary,
      ),
      headlineSmall: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: JohnDeereColors.textPrimary,
      ),
      titleLarge: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 22,
        fontWeight: FontWeight.w600,
        color: JohnDeereColors.textPrimary,
      ),
      titleMedium: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: JohnDeereColors.textPrimary,
      ),
      titleSmall: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: JohnDeereColors.textPrimary,
      ),
      bodyLarge: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 16,
        color: JohnDeereColors.textPrimary,
      ),
      bodyMedium: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 14,
        color: JohnDeereColors.textPrimary,
      ),
      bodySmall: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 12,
        color: JohnDeereColors.textSecondary,
      ),
      labelLarge: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: JohnDeereColors.textPrimary,
      ),
      labelMedium: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 12,
        fontWeight: FontWeight.w600,
        color: JohnDeereColors.textSecondary,
      ),
      labelSmall: TextStyle(
        fontFamily: 'Cairo',
        fontSize: 11,
        color: JohnDeereColors.textSecondary,
      ),
    ),
    
    // Icon Theme
    iconTheme: const IconThemeData(
      color: JohnDeereColors.primary,
      size: 24,
    ),
    
    // Progress Indicator
    progressIndicatorTheme: const ProgressIndicatorThemeData(
      color: JohnDeereColors.primary,
      linearTrackColor: JohnDeereColors.divider,
      circularTrackColor: JohnDeereColors.divider,
    ),
  );

  // ============================================
  // DARK THEME
  // ============================================
  
  static ThemeData get dark => light.copyWith(
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: JohnDeereColors.primaryLight,
      primaryContainer: JohnDeereColors.primary,
      secondary: JohnDeereColors.secondary,
      secondaryContainer: JohnDeereColors.secondaryDark,
      surface: JohnDeereColors.darkSurface,
      background: JohnDeereColors.darkBackground,
      error: JohnDeereColors.error,
      onPrimary: JohnDeereColors.textPrimary,
      onSecondary: JohnDeereColors.textPrimary,
      onSurface: JohnDeereColors.darkTextPrimary,
      onBackground: JohnDeereColors.darkTextPrimary,
      onError: JohnDeereColors.textOnPrimary,
    ),
    scaffoldBackgroundColor: JohnDeereColors.darkBackground,
    cardTheme: CardTheme(
      elevation: 2,
      color: JohnDeereColors.darkCard,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
    ),
    appBarTheme: const AppBarTheme(
      elevation: 0,
      centerTitle: true,
      backgroundColor: JohnDeereColors.darkSurface,
      foregroundColor: JohnDeereColors.darkTextPrimary,
    ),
    dividerTheme: const DividerThemeData(
      color: JohnDeereColors.darkDivider,
    ),
  );
}
