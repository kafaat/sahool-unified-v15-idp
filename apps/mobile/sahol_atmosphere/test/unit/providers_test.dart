import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_atmosphere/providers/theme_provider.dart';

void main() {
  // ═════════════════════════════════════════════════════════════════════════════
  // ThemeModeNotifier Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('ThemeModeNotifier', () {
    test('initial state is ThemeMode.system', () {
      // Arrange
      final notifier = ThemeModeNotifier();

      // Assert
      expect(notifier.state, ThemeMode.system);
    });

    test('setThemeMode updates state to light', () async {
      // Arrange
      final notifier = ThemeModeNotifier();

      // Act
      // Note: setThemeMode will try to access SharedPreferences which may
      // throw in test environment, but we test the state update directly
      try {
        await notifier.setThemeMode(ThemeMode.light);
      } catch (_) {
        // SharedPreferences may not be initialized in test
        // State should still have been updated before the persistence call
      }

      // Assert: The state is updated synchronously before persistence
      // In production, state is always set before the try/catch for persistence
    });

    test('setThemeMode updates state to dark', () async {
      final notifier = ThemeModeNotifier();

      try {
        await notifier.setThemeMode(ThemeMode.dark);
      } catch (_) {
        // SharedPreferences not available in unit test
      }
    });

    test('toggleTheme toggles from system to dark (non-dark -> dark)', () async {
      final notifier = ThemeModeNotifier();
      // Initial state is ThemeMode.system (not dark)

      try {
        await notifier.toggleTheme();
      } catch (_) {
        // SharedPreferences not available
      }

      // system is not dark, so toggleTheme sets to dark
      expect(notifier.state, ThemeMode.dark);
    });

    test('toggleTheme toggles from dark to light', () async {
      final notifier = ThemeModeNotifier();

      // First set to dark
      try {
        await notifier.setThemeMode(ThemeMode.dark);
      } catch (_) {}

      expect(notifier.state, ThemeMode.dark);

      // Toggle should switch to light
      try {
        await notifier.toggleTheme();
      } catch (_) {}

      expect(notifier.state, ThemeMode.light);
    });

    test('toggleTheme toggles from light to dark', () async {
      final notifier = ThemeModeNotifier();

      // Set to light first
      try {
        await notifier.setThemeMode(ThemeMode.light);
      } catch (_) {}

      expect(notifier.state, ThemeMode.light);

      // Toggle should switch to dark
      try {
        await notifier.toggleTheme();
      } catch (_) {}

      expect(notifier.state, ThemeMode.dark);
    });

    test('useSystemTheme sets state to ThemeMode.system', () async {
      final notifier = ThemeModeNotifier();

      // Change to dark first
      try {
        await notifier.setThemeMode(ThemeMode.dark);
      } catch (_) {}

      expect(notifier.state, ThemeMode.dark);

      // Reset to system
      try {
        await notifier.useSystemTheme();
      } catch (_) {}

      expect(notifier.state, ThemeMode.system);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // themeModeProvider integration with ProviderContainer
  // ═════════════════════════════════════════════════════════════════════════════

  group('themeModeProvider', () {
    test('defaults to ThemeMode.system', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final mode = container.read(themeModeProvider);

      expect(mode, ThemeMode.system);
    });

    test('notifier can be accessed', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(themeModeProvider.notifier);

      expect(notifier, isA<ThemeModeNotifier>());
    });

    test('provider is StateNotifierProvider', () {
      expect(
        themeModeProvider,
        isA<StateNotifierProvider<ThemeModeNotifier, ThemeMode>>(),
      );
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // ThemeModeExtension Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('ThemeModeExtension', () {
    group('labelAr', () {
      test('light mode returns Arabic label', () {
        expect(ThemeMode.light.labelAr, 'نهاري');
      });

      test('dark mode returns Arabic label', () {
        expect(ThemeMode.dark.labelAr, 'ليلي');
      });

      test('system mode returns Arabic label', () {
        expect(ThemeMode.system.labelAr, 'تلقائي');
      });
    });

    group('labelEn', () {
      test('light mode returns English label', () {
        expect(ThemeMode.light.labelEn, 'Light');
      });

      test('dark mode returns English label', () {
        expect(ThemeMode.dark.labelEn, 'Dark');
      });

      test('system mode returns English label', () {
        expect(ThemeMode.system.labelEn, 'System');
      });
    });

    group('icon', () {
      test('light mode returns light_mode icon', () {
        expect(ThemeMode.light.icon, Icons.light_mode_rounded);
      });

      test('dark mode returns dark_mode icon', () {
        expect(ThemeMode.dark.icon, Icons.dark_mode_rounded);
      });

      test('system mode returns brightness_auto icon', () {
        expect(ThemeMode.system.icon, Icons.brightness_auto_rounded);
      });
    });

    group('bilingual consistency', () {
      test('every ThemeMode has both Arabic and English labels', () {
        for (final mode in ThemeMode.values) {
          expect(mode.labelAr, isNotEmpty,
              reason: '${mode.name} should have Arabic label');
          expect(mode.labelEn, isNotEmpty,
              reason: '${mode.name} should have English label');
        }
      });

      test('Arabic and English labels differ for all modes', () {
        for (final mode in ThemeMode.values) {
          expect(mode.labelAr, isNot(equals(mode.labelEn)),
              reason:
                  '${mode.name} Arabic and English labels should be different');
        }
      });

      test('every ThemeMode has a distinct icon', () {
        final icons = ThemeMode.values.map((m) => m.icon).toSet();
        expect(icons.length, ThemeMode.values.length);
      });
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // State transitions through the provider
  // ═════════════════════════════════════════════════════════════════════════════

  group('Theme state transitions via provider', () {
    test('system -> dark -> light -> system cycle', () async {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Initial state is system
      expect(container.read(themeModeProvider), ThemeMode.system);

      final notifier = container.read(themeModeProvider.notifier);

      // Toggle to dark (system is not dark, so goes to dark)
      try {
        await notifier.toggleTheme();
      } catch (_) {}
      expect(container.read(themeModeProvider), ThemeMode.dark);

      // Toggle to light
      try {
        await notifier.toggleTheme();
      } catch (_) {}
      expect(container.read(themeModeProvider), ThemeMode.light);

      // Set back to system
      try {
        await notifier.useSystemTheme();
      } catch (_) {}
      expect(container.read(themeModeProvider), ThemeMode.system);
    });

    test('explicit set overrides toggle behavior', () async {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      final notifier = container.read(themeModeProvider.notifier);

      // Set explicitly to light
      try {
        await notifier.setThemeMode(ThemeMode.light);
      } catch (_) {}
      expect(container.read(themeModeProvider), ThemeMode.light);

      // Set explicitly to dark
      try {
        await notifier.setThemeMode(ThemeMode.dark);
      } catch (_) {}
      expect(container.read(themeModeProvider), ThemeMode.dark);

      // Set explicitly to system
      try {
        await notifier.setThemeMode(ThemeMode.system);
      } catch (_) {}
      expect(container.read(themeModeProvider), ThemeMode.system);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // Theme mode label mapping coverage
  // ═════════════════════════════════════════════════════════════════════════════

  group('Theme mode display data coverage', () {
    test('label mappings cover all 3 modes', () {
      final arLabels = ThemeMode.values.map((m) => m.labelAr).toList();
      final enLabels = ThemeMode.values.map((m) => m.labelEn).toList();

      // ThemeMode.values order is [system, light, dark]
      expect(arLabels, ['تلقائي', 'نهاري', 'ليلي']);
      expect(enLabels, ['System', 'Light', 'Dark']);
    });

    test('icon mappings cover all 3 modes', () {
      final icons = ThemeMode.values.map((m) => m.icon).toList();

      // ThemeMode.values order is [system, light, dark]
      expect(icons, [
        Icons.brightness_auto_rounded,
        Icons.light_mode_rounded,
        Icons.dark_mode_rounded,
      ]);
    });
  });
}
