// AUTO-GENERATED - DO NOT EDIT MANUALLY
// Generated from: governance/design/design-tokens.yaml
// Purpose: SAHOOL Low-Code PoC token-fed Flutter ThemeData.

import 'dart:ui' show FontFeature;

import 'package:flutter/material.dart';

/// Token constants used by generated Low-Code PoC screens.
class SahoolGeneratedTokens {
  const SahoolGeneratedTokens._();

  static const primary50 = Color(0xFFE8F5E9);
  static const primary100 = Color(0xFFC8E6C9);
  static const primary200 = Color(0xFFA5D6A7);
  static const primary300 = Color(0xFF81C784);
  static const primary400 = Color(0xFF66BB6A);
  static const primary500 = Color(0xFF4CAF50);
  static const primary600 = Color(0xFF43A047);
  static const primary700 = Color(0xFF388E3C);
  static const primary800 = Color(0xFF2E7D32);
  static const primary900 = Color(0xFF1B5E20);
  static const secondary50 = Color(0xFFE3F2FD);
  static const secondary100 = Color(0xFFBBDEFB);
  static const secondary200 = Color(0xFF90CAF9);
  static const secondary300 = Color(0xFF64B5F6);
  static const secondary400 = Color(0xFF42A5F5);
  static const secondary500 = Color(0xFF2196F3);
  static const secondary600 = Color(0xFF1E88E5);
  static const secondary700 = Color(0xFF1976D2);
  static const secondary800 = Color(0xFF1565C0);
  static const secondary900 = Color(0xFF0D47A1);
  static const accent50 = Color(0xFFFFF3E0);
  static const accent100 = Color(0xFFFFE0B2);
  static const accent200 = Color(0xFFFFCC80);
  static const accent300 = Color(0xFFFFB74D);
  static const accent400 = Color(0xFFFFA726);
  static const accent500 = Color(0xFFFF9800);
  static const accent600 = Color(0xFFFB8C00);
  static const accent700 = Color(0xFFF57C00);
  static const accent800 = Color(0xFFEF6C00);
  static const accent900 = Color(0xFFE65100);
  static const successLight = Color(0xFF81C784);
  static const successMain = Color(0xFF4CAF50);
  static const successDark = Color(0xFF388E3C);
  static const warningLight = Color(0xFFFFB74D);
  static const warningMain = Color(0xFFFF9800);
  static const warningDark = Color(0xFFF57C00);
  static const errorLight = Color(0xFFE57373);
  static const errorMain = Color(0xFFF44336);
  static const errorDark = Color(0xFFD32F2F);
  static const infoLight = Color(0xFF64B5F6);
  static const infoMain = Color(0xFF2196F3);
  static const infoDark = Color(0xFF1976D2);
  static const neutral0 = Color(0xFFFFFFFF);
  static const neutral50 = Color(0xFFFAFAFA);
  static const neutral100 = Color(0xFFF5F5F5);
  static const neutral200 = Color(0xFFEEEEEE);
  static const neutral300 = Color(0xFFE0E0E0);
  static const neutral400 = Color(0xFFBDBDBD);
  static const neutral500 = Color(0xFF9E9E9E);
  static const neutral600 = Color(0xFF757575);
  static const neutral700 = Color(0xFF616161);
  static const neutral800 = Color(0xFF424242);
  static const neutral900 = Color(0xFF212121);
  static const neutral1000 = Color(0xFF000000);
  static const domainSoil = Color(0xFF8D6E63);
  static const domainWater = Color(0xFF29B6F6);
  static const domainSun = Color(0xFFFFEB3B);
  static const domainCropHealthy = Color(0xFF66BB6A);
  static const domainCropStressed = Color(0xFFFFA726);
  static const domainCropDiseased = Color(0xFFEF5350);
  static const domainNdviHigh = Color(0xFF1B5E20);
  static const domainNdviMedium = Color(0xFF81C784);
  static const domainNdviLow = Color(0xFFFFF176);
  static const domainNdviBare = Color(0xFFD7CCC8);
  static const stateSynced = Color(0xFF2E7D32);
  static const statePending = Color(0xFFBF360A);
  static const stateConflict = Color(0xFFC62828);
  static const stateStale = Color(0xFF616161);
  static const stateOffline = Color(0xFF424242);
  static const stateCached = Color(0xFF6A1B9A);
  static const stateFailed = Color(0xFFB71C1C);

  static const spacing0 = 0.0;
  static const spacing1 = 4.0;
  static const spacing2 = 8.0;
  static const spacing3 = 12.0;
  static const spacing4 = 16.0;
  static const spacing6 = 24.0;
  static const spacing8 = 32.0;
  static const spacing12 = 48.0;
  static const spacing16 = 64.0;

  static const radiusNone = 0.0;
  static const radiusSm = 4.0;
  static const radiusMd = 8.0;
  static const radiusLg = 12.0;
  static const radiusXl = 16.0;
  static const radius2xl = 24.0;
  static const radiusFull = 9999.0;
}

/// Flutter themes generated from SAHOOL governance design tokens.
class SahoolGeneratedTheme {
  const SahoolGeneratedTheme._();

  static ThemeData light() {
    final base = ThemeData.light(useMaterial3: true);
    return base.copyWith(
      colorScheme: ColorScheme.fromSeed(
        seedColor: SahoolGeneratedTokens.primary500,
        primary: SahoolGeneratedTokens.primary500,
        secondary: SahoolGeneratedTokens.secondary500,
        error: SahoolGeneratedTokens.errorMain,
        surface: SahoolGeneratedTokens.neutral0,
      ),
      fontFamily: 'IBMPlexSansArabic',
      textTheme: base.textTheme.apply(
        fontFamily: 'IBMPlexSansArabic',
        displayColor: SahoolGeneratedTokens.neutral900,
        bodyColor: SahoolGeneratedTokens.neutral900,
      ),
      cardTheme: CardThemeData(
        color: SahoolGeneratedTokens.neutral0,
        elevation: 1,
        margin: const EdgeInsets.all(SahoolGeneratedTokens.spacing4),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(SahoolGeneratedTokens.radiusLg),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(SahoolGeneratedTokens.radiusMd),
        ),
      ),
    );
  }

  static ThemeData dark() {
    final base = ThemeData.dark(useMaterial3: true);
    return base.copyWith(
      colorScheme: ColorScheme.fromSeed(
        brightness: Brightness.dark,
        seedColor: SahoolGeneratedTokens.primary300,
        primary: SahoolGeneratedTokens.primary300,
        secondary: SahoolGeneratedTokens.secondary300,
        error: SahoolGeneratedTokens.errorLight,
        surface: SahoolGeneratedTokens.neutral900,
      ),
      fontFamily: 'IBMPlexSansArabic',
      textTheme: base.textTheme.apply(
        fontFamily: 'IBMPlexSansArabic',
        displayColor: SahoolGeneratedTokens.neutral0,
        bodyColor: SahoolGeneratedTokens.neutral0,
      ),
    );
  }

  static TextStyle get monoMetric => const TextStyle(
    fontFamily: 'Inter',
    fontFeatures: [FontFeature.tabularFigures()],
  );
}
