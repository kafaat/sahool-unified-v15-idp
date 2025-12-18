// ============================================
// SAHOOL - John Deere Inspired Color Palette
// نظام الألوان المستوحى من جون ديري
// ============================================

import 'package:flutter/material.dart';

/// John Deere inspired color palette for SAHOOL
/// Combines agricultural green tones with modern design
class JohnDeereColors {
  JohnDeereColors._();

  // ============================================
  // PRIMARY COLORS - الألوان الأساسية
  // ============================================
  
  /// John Deere signature green
  static const Color primary = Color(0xFF367C2B);
  static const Color primaryLight = Color(0xFF4A9A3B);
  static const Color primaryDark = Color(0xFF255E1D);
  
  /// Primary color swatch
  static const MaterialColor primarySwatch = MaterialColor(
    0xFF367C2B,
    <int, Color>{
      50: Color(0xFFE7F5E5),
      100: Color(0xFFC3E6BF),
      200: Color(0xFF9BD694),
      300: Color(0xFF73C669),
      400: Color(0xFF55BA49),
      500: Color(0xFF367C2B), // Primary
      600: Color(0xFF309D25),
      700: Color(0xFF288D1F),
      800: Color(0xFF217E19),
      900: Color(0xFF14610F),
    },
  );

  // ============================================
  // SECONDARY COLORS - الألوان الثانوية
  // ============================================
  
  /// John Deere yellow accent
  static const Color secondary = Color(0xFFFFDE00);
  static const Color secondaryLight = Color(0xFFFFE74D);
  static const Color secondaryDark = Color(0xFFC9AF00);

  // ============================================
  // NEUTRAL COLORS - الألوان المحايدة
  // ============================================
  
  static const Color surface = Color(0xFFFAFAFA);
  static const Color background = Color(0xFFF5F5F5);
  static const Color card = Color(0xFFFFFFFF);
  
  static const Color textPrimary = Color(0xFF1A1A1A);
  static const Color textSecondary = Color(0xFF6B6B6B);
  static const Color textDisabled = Color(0xFF9E9E9E);
  static const Color textOnPrimary = Color(0xFFFFFFFF);
  
  static const Color divider = Color(0xFFE0E0E0);
  static const Color border = Color(0xFFD0D0D0);

  // ============================================
  // SEMANTIC COLORS - الألوان الدلالية
  // ============================================
  
  /// Success - healthy crops, positive results
  static const Color success = Color(0xFF4CAF50);
  static const Color successLight = Color(0xFFE8F5E9);
  
  /// Warning - attention needed
  static const Color warning = Color(0xFFFFC107);
  static const Color warningLight = Color(0xFFFFF8E1);
  
  /// Error - problems, diseases
  static const Color error = Color(0xFFF44336);
  static const Color errorLight = Color(0xFFFFEBEE);
  
  /// Info - neutral information
  static const Color info = Color(0xFF2196F3);
  static const Color infoLight = Color(0xFFE3F2FD);

  // ============================================
  // AGRICULTURAL COLORS - ألوان زراعية
  // ============================================
  
  /// Soil brown
  static const Color soil = Color(0xFF795548);
  static const Color soilLight = Color(0xFFA98274);
  static const Color soilDark = Color(0xFF4B2C20);
  
  /// Water blue
  static const Color water = Color(0xFF03A9F4);
  static const Color waterLight = Color(0xFF67DAFF);
  static const Color waterDark = Color(0xFF007AC1);
  
  /// Wheat gold
  static const Color wheat = Color(0xFFD4A574);
  static const Color wheatLight = Color(0xFFFFD7A4);
  static const Color wheatDark = Color(0xFFA17647);
  
  /// Sky blue for weather
  static const Color sky = Color(0xFF87CEEB);
  static const Color skyLight = Color(0xFFB3E5FC);
  static const Color skyDark = Color(0xFF4FC3F7);
  
  /// Sun yellow for radiation/heat
  static const Color sun = Color(0xFFFFB300);
  static const Color sunLight = Color(0xFFFFE54C);
  static const Color sunDark = Color(0xFFC68400);

  // ============================================
  // NDVI HEALTH COLORS - ألوان صحة النبات
  // ============================================
  
  /// Excellent vegetation (NDVI > 0.6)
  static const Color ndviExcellent = Color(0xFF1B5E20);
  
  /// Good vegetation (NDVI 0.4-0.6)
  static const Color ndviGood = Color(0xFF4CAF50);
  
  /// Moderate vegetation (NDVI 0.2-0.4)
  static const Color ndviModerate = Color(0xFFCDDC39);
  
  /// Poor vegetation (NDVI 0-0.2)
  static const Color ndviPoor = Color(0xFFFF9800);
  
  /// No vegetation (NDVI < 0)
  static const Color ndviNone = Color(0xFF795548);

  // ============================================
  // GRADIENTS - التدرجات اللونية
  // ============================================
  
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryLight, primary, primaryDark],
  );
  
  static const LinearGradient fieldGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [sky, primaryLight, primary],
  );
  
  static const LinearGradient sunsetGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [sun, secondary, warning],
  );

  // ============================================
  // DARK THEME COLORS - ألوان الوضع الداكن
  // ============================================
  
  static const Color darkSurface = Color(0xFF121212);
  static const Color darkBackground = Color(0xFF1E1E1E);
  static const Color darkCard = Color(0xFF2C2C2C);
  static const Color darkTextPrimary = Color(0xFFE0E0E0);
  static const Color darkTextSecondary = Color(0xFF9E9E9E);
  static const Color darkDivider = Color(0xFF424242);

  // ============================================
  // HELPER METHODS
  // ============================================
  
  /// Get NDVI color based on value
  static Color getNdviColor(double ndvi) {
    if (ndvi > 0.6) return ndviExcellent;
    if (ndvi > 0.4) return ndviGood;
    if (ndvi > 0.2) return ndviModerate;
    if (ndvi > 0) return ndviPoor;
    return ndviNone;
  }
  
  /// Get alert color based on severity
  static Color getAlertColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return error;
      case 'high':
        return warning;
      case 'medium':
        return info;
      default:
        return success;
    }
  }
  
  /// Get weather condition color
  static Color getWeatherColor(String condition) {
    switch (condition.toLowerCase()) {
      case 'sunny':
      case 'clear':
        return sun;
      case 'cloudy':
      case 'overcast':
        return textSecondary;
      case 'rainy':
      case 'rain':
        return water;
      case 'stormy':
        return error;
      default:
        return sky;
    }
  }
}
