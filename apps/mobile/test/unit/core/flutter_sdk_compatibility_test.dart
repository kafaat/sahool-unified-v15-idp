import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/app.dart';
import 'package:sahool_field_app/core/core.dart' as core;
import 'package:sahool_field_app/core/theme/app_theme.dart';
import 'package:sahool_field_app/core/theme/enhanced_dark_theme.dart';

void main() {
  test('native app entry point and core exports compile together', () {
    // Import the real app and its route graph; do not start platform services.
    expect(const SahoolFieldApp(), isA<Widget>());
    expect(core.EnvConfig.appVersion, isNotEmpty);
  });

  test('custom component styling survives the ThemeData API migration', () {
    final themes = <ThemeData>[
      AppTheme.glassLight,
      AppTheme.glassDark,
      EnhancedDarkTheme.standard,
    ];
    for (final theme in themes) {
      expect(theme.cardTheme.shape, isA<RoundedRectangleBorder>());
      expect(theme.dialogTheme.shape, isA<RoundedRectangleBorder>());
      expect(theme.cardTheme.surfaceTintColor, Colors.transparent);
      expect(theme.dialogTheme.surfaceTintColor, Colors.transparent);
    }
    expect(EnhancedDarkTheme.standard.tabBarTheme.labelStyle, isNotNull);
  });
}
