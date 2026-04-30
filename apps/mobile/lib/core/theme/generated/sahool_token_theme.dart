// AUTO-GENERATED - DO NOT EDIT MANUALLY
// Generated from: governance/design/design-tokens.yaml
// Purpose: SAHOOL Low-Code PoC token-fed Flutter ThemeData.

import 'dart:ui' show FontFeature;

import 'package:flutter/material.dart';

/// Token constants used by generated Low-Code PoC screens.
class SahoolGeneratedTokens {
  const SahoolGeneratedTokens._();

  static const primary_50 = Color(0xFFE8F5E9);
  static const primary_100 = Color(0xFFC8E6C9);
  static const primary_200 = Color(0xFFA5D6A7);
  static const primary_300 = Color(0xFF81C784);
  static const primary_400 = Color(0xFF66BB6A);
  static const primary_500 = Color(0xFF4CAF50);
  static const primary_600 = Color(0xFF43A047);
  static const primary_700 = Color(0xFF388E3C);
  static const primary_800 = Color(0xFF2E7D32);
  static const primary_900 = Color(0xFF1B5E20);
  static const secondary_50 = Color(0xFFE3F2FD);
  static const secondary_100 = Color(0xFFBBDEFB);
  static const secondary_200 = Color(0xFF90CAF9);
  static const secondary_300 = Color(0xFF64B5F6);
  static const secondary_400 = Color(0xFF42A5F5);
  static const secondary_500 = Color(0xFF2196F3);
  static const secondary_600 = Color(0xFF1E88E5);
  static const secondary_700 = Color(0xFF1976D2);
  static const secondary_800 = Color(0xFF1565C0);
  static const secondary_900 = Color(0xFF0D47A1);
  static const accent_50 = Color(0xFFFFF3E0);
  static const accent_100 = Color(0xFFFFE0B2);
  static const accent_200 = Color(0xFFFFCC80);
  static const accent_300 = Color(0xFFFFB74D);
  static const accent_400 = Color(0xFFFFA726);
  static const accent_500 = Color(0xFFFF9800);
  static const accent_600 = Color(0xFFFB8C00);
  static const accent_700 = Color(0xFFF57C00);
  static const accent_800 = Color(0xFFEF6C00);
  static const accent_900 = Color(0xFFE65100);
  static const success_light = Color(0xFF81C784);
  static const success_main = Color(0xFF4CAF50);
  static const success_dark = Color(0xFF388E3C);
  static const warning_light = Color(0xFFFFB74D);
  static const warning_main = Color(0xFFFF9800);
  static const warning_dark = Color(0xFFF57C00);
  static const error_light = Color(0xFFE57373);
  static const error_main = Color(0xFFF44336);
  static const error_dark = Color(0xFFD32F2F);
  static const info_light = Color(0xFF64B5F6);
  static const info_main = Color(0xFF2196F3);
  static const info_dark = Color(0xFF1976D2);
  static const neutral_0 = Color(0xFFFFFFFF);
  static const neutral_50 = Color(0xFFFAFAFA);
  static const neutral_100 = Color(0xFFF5F5F5);
  static const neutral_200 = Color(0xFFEEEEEE);
  static const neutral_300 = Color(0xFFE0E0E0);
  static const neutral_400 = Color(0xFFBDBDBD);
  static const neutral_500 = Color(0xFF9E9E9E);
  static const neutral_600 = Color(0xFF757575);
  static const neutral_700 = Color(0xFF616161);
  static const neutral_800 = Color(0xFF424242);
  static const neutral_900 = Color(0xFF212121);
  static const neutral_1000 = Color(0xFF000000);
  static const domain_soil = Color(0xFF8D6E63);
  static const domain_water = Color(0xFF29B6F6);
  static const domain_sun = Color(0xFFFFEB3B);
  static const domain_crop_healthy = Color(0xFF66BB6A);
  static const domain_crop_stressed = Color(0xFFFFA726);
  static const domain_crop_diseased = Color(0xFFEF5350);
  static const domain_ndvi_high = Color(0xFF1B5E20);
  static const domain_ndvi_medium = Color(0xFF81C784);
  static const domain_ndvi_low = Color(0xFFFFF176);
  static const domain_ndvi_bare = Color(0xFFD7CCC8);
  static const state_synced = Color(0xFF2E7D32);
  static const state_pending = Color(0xFFBF360A);
  static const state_conflict = Color(0xFFC62828);
  static const state_stale = Color(0xFF616161);
  static const state_offline = Color(0xFF424242);
  static const state_cached = Color(0xFF6A1B9A);
  static const state_failed = Color(0xFFB71C1C);

  static const spacing_0 = 0.0;
  static const spacing_1 = 4.0;
  static const spacing_2 = 8.0;
  static const spacing_3 = 12.0;
  static const spacing_4 = 16.0;
  static const spacing_5 = 20.0;
  static const spacing_6 = 24.0;
  static const spacing_8 = 32.0;
  static const spacing_10 = 40.0;
  static const spacing_12 = 48.0;
  static const spacing_16 = 64.0;
  static const spacing_20 = 80.0;
  static const spacing_24 = 96.0;

  static const radius_none = 0.0;
  static const radius_sm = 4.0;
  static const radius_md = 8.0;
  static const radius_lg = 12.0;
  static const radius_xl = 16.0;
  static const radius_2xl = 24.0;
  static const radius_full = 9999.0;
}

/// Flutter themes generated from SAHOOL governance design tokens.
class SahoolGeneratedTheme {
  const SahoolGeneratedTheme._();

  static ThemeData light() {
    final base = ThemeData.light(useMaterial3: true);
    return base.copyWith(
      colorScheme: ColorScheme.fromSeed(
        seedColor: SahoolGeneratedTokens.primary_500,
        primary: SahoolGeneratedTokens.primary_500,
        secondary: SahoolGeneratedTokens.secondary_500,
        error: SahoolGeneratedTokens.error_main,
        surface: SahoolGeneratedTokens.neutral_0,
      ),
      fontFamily: 'IBMPlexSansArabic',
      textTheme: base.textTheme.apply(
        fontFamily: 'IBMPlexSansArabic',
        displayColor: SahoolGeneratedTokens.neutral_900,
        bodyColor: SahoolGeneratedTokens.neutral_900,
      ),
      cardTheme: CardThemeData(
        color: SahoolGeneratedTokens.neutral_0,
        elevation: 1,
        margin: const EdgeInsets.all(SahoolGeneratedTokens.spacing_4),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(SahoolGeneratedTokens.radius_lg),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(SahoolGeneratedTokens.radius_md),
        ),
      ),
    );
  }

  static ThemeData dark() {
    final base = ThemeData.dark(useMaterial3: true);
    return base.copyWith(
      colorScheme: ColorScheme.fromSeed(
        brightness: Brightness.dark,
        seedColor: SahoolGeneratedTokens.primary_300,
        primary: SahoolGeneratedTokens.primary_300,
        secondary: SahoolGeneratedTokens.secondary_300,
        error: SahoolGeneratedTokens.error_light,
        surface: SahoolGeneratedTokens.neutral_900,
      ),
      fontFamily: 'IBMPlexSansArabic',
      textTheme: base.textTheme.apply(
        fontFamily: 'IBMPlexSansArabic',
        displayColor: SahoolGeneratedTokens.neutral_0,
        bodyColor: SahoolGeneratedTokens.neutral_0,
      ),
    );
  }

  static TextStyle get monoMetric => const TextStyle(
    fontFamily: 'Inter',
    fontFeatures: [FontFeature.tabularFigures()],
  );
}
