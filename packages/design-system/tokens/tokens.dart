// AUTO-GENERATED - DO NOT EDIT MANUALLY
// Generated from: governance/design/design-tokens.yaml
// Generated at: 2025-12-19T13:47:58.610985

import 'package:flutter/material.dart';

/// SAHOOL Design Tokens
class SahoolTokens {
  SahoolTokens._();

  // ─────────────────────────────────────────────────────────────────────
  // Colors
  // ─────────────────────────────────────────────────────────────────────
  static const Color primary50 = Color(0xFFE8F5E9);
  static const Color primary100 = Color(0xFFC8E6C9);
  static const Color primary200 = Color(0xFFA5D6A7);
  static const Color primary300 = Color(0xFF81C784);
  static const Color primary400 = Color(0xFF66BB6A);
  static const Color primary500 = Color(0xFF4CAF50);
  static const Color primary600 = Color(0xFF43A047);
  static const Color primary700 = Color(0xFF388E3C);
  static const Color primary800 = Color(0xFF2E7D32);
  static const Color primary900 = Color(0xFF1B5E20);
  static const Color secondary50 = Color(0xFFE3F2FD);
  static const Color secondary100 = Color(0xFFBBDEFB);
  static const Color secondary200 = Color(0xFF90CAF9);
  static const Color secondary300 = Color(0xFF64B5F6);
  static const Color secondary400 = Color(0xFF42A5F5);
  static const Color secondary500 = Color(0xFF2196F3);
  static const Color secondary600 = Color(0xFF1E88E5);
  static const Color secondary700 = Color(0xFF1976D2);
  static const Color secondary800 = Color(0xFF1565C0);
  static const Color secondary900 = Color(0xFF0D47A1);
  static const Color accent50 = Color(0xFFFFF3E0);
  static const Color accent100 = Color(0xFFFFE0B2);
  static const Color accent200 = Color(0xFFFFCC80);
  static const Color accent300 = Color(0xFFFFB74D);
  static const Color accent400 = Color(0xFFFFA726);
  static const Color accent500 = Color(0xFFFF9800);
  static const Color accent600 = Color(0xFFFB8C00);
  static const Color accent700 = Color(0xFFF57C00);
  static const Color accent800 = Color(0xFFEF6C00);
  static const Color accent900 = Color(0xFFE65100);
  static const Color successlight = Color(0xFF81C784);
  static const Color successmain = Color(0xFF4CAF50);
  static const Color successdark = Color(0xFF388E3C);
  static const Color warninglight = Color(0xFFFFB74D);
  static const Color warningmain = Color(0xFFFF9800);
  static const Color warningdark = Color(0xFFF57C00);
  static const Color errorlight = Color(0xFFE57373);
  static const Color errormain = Color(0xFFF44336);
  static const Color errordark = Color(0xFFD32F2F);
  static const Color infolight = Color(0xFF64B5F6);
  static const Color infomain = Color(0xFF2196F3);
  static const Color infodark = Color(0xFF1976D2);
  static const Color neutral0 = Color(0xFFFFFFFF);
  static const Color neutral50 = Color(0xFFFAFAFA);
  static const Color neutral100 = Color(0xFFF5F5F5);
  static const Color neutral200 = Color(0xFFEEEEEE);
  static const Color neutral300 = Color(0xFFE0E0E0);
  static const Color neutral400 = Color(0xFFBDBDBD);
  static const Color neutral500 = Color(0xFF9E9E9E);
  static const Color neutral600 = Color(0xFF757575);
  static const Color neutral700 = Color(0xFF616161);
  static const Color neutral800 = Color(0xFF424242);
  static const Color neutral900 = Color(0xFF212121);
  static const Color neutral1000 = Color(0xFF000000);
  static const Color domainsoil = Color(0xFF8D6E63);
  static const Color domainwater = Color(0xFF29B6F6);
  static const Color domainsun = Color(0xFFFFEB3B);
  static const Color domaincrop_healthy = Color(0xFF66BB6A);
  static const Color domaincrop_stressed = Color(0xFFFFA726);
  static const Color domaincrop_diseased = Color(0xFFEF5350);
  static const Color domainndvi_high = Color(0xFF1B5E20);
  static const Color domainndvi_medium = Color(0xFF81C784);
  static const Color domainndvi_low = Color(0xFFFFF176);
  static const Color domainndvi_bare = Color(0xFFD7CCC8);

  // ─────────────────────────────────────────────────────────────────────
  // Spacing
  // ─────────────────────────────────────────────────────────────────────
  static const double spacing1 = 4.0;
  static const double spacing2 = 8.0;
  static const double spacing3 = 12.0;
  static const double spacing4 = 16.0;
  static const double spacing5 = 20.0;
  static const double spacing6 = 24.0;
  static const double spacing8 = 32.0;
  static const double spacing10 = 40.0;
  static const double spacing12 = 48.0;
  static const double spacing16 = 64.0;
  static const double spacing20 = 80.0;
  static const double spacing24 = 96.0;

  // ─────────────────────────────────────────────────────────────────────
  // Border Radius
  // ─────────────────────────────────────────────────────────────────────
  static const double radiusSm = 4.0;
  static const double radiusMd = 8.0;
  static const double radiusLg = 12.0;
  static const double radiusXl = 16.0;
  static const double radius2xl = 24.0;

  // ─────────────────────────────────────────────────────────────────────
  // Typography
  // ─────────────────────────────────────────────────────────────────────
  static const double fontSizeXs = 12.0;
  static const double fontSizeSm = 14.0;
  static const double fontSizeBase = 16.0;
  static const double fontSizeLg = 18.0;
  static const double fontSizeXl = 20.0;
  static const double fontSize2xl = 24.0;
  static const double fontSize3xl = 30.0;
  static const double fontSize4xl = 36.0;
  static const double fontSize5xl = 48.0;
}

/// SAHOOL Theme Data
class SahoolTheme {
  static ThemeData get light => ThemeData(
    primaryColor: SahoolTokens.primary500,
    colorScheme: ColorScheme.light(
      primary: SahoolTokens.primary500,
      secondary: SahoolTokens.secondary500,
      surface: SahoolTokens.neutral0,
      error: SahoolTokens.errormain ?? SahoolTokens.primary500,
    ),
    fontFamily: 'IBMPlexSansArabic',
  );

  static ThemeData get dark => ThemeData(
    primaryColor: SahoolTokens.primary400,
    colorScheme: ColorScheme.dark(
      primary: SahoolTokens.primary400,
      secondary: SahoolTokens.secondary400,
      surface: SahoolTokens.neutral900,
    ),
    fontFamily: 'IBMPlexSansArabic',
  );
}