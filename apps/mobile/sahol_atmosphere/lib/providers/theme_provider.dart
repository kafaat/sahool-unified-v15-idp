// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Theme Provider
// مزود الثيم لساهول أتموسفير
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Manages theme mode (light/dark/system) with persistence
// إدارة وضع الثيم (نهاري/ليلي/نظام) مع الحفظ
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Theme mode storage key
const String _themeModeKey = 'atmosphere_theme_mode';

/// Theme Mode Provider
/// مزود وضع الثيم
final themeModeProvider = StateNotifierProvider<ThemeModeNotifier, ThemeMode>(
  (ref) => ThemeModeNotifier(),
);

/// Theme Mode Notifier
/// مدير حالة وضع الثيم
class ThemeModeNotifier extends StateNotifier<ThemeMode> {
  ThemeModeNotifier() : super(ThemeMode.system) {
    _loadThemeMode();
  }

  /// Load saved theme mode from SharedPreferences
  /// تحميل وضع الثيم المحفوظ
  Future<void> _loadThemeMode() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedMode = prefs.getString(_themeModeKey);

      if (savedMode != null) {
        switch (savedMode) {
          case 'light':
            state = ThemeMode.light;
            break;
          case 'dark':
            state = ThemeMode.dark;
            break;
          default:
            state = ThemeMode.system;
        }
      }
    } catch (e) {
      debugPrint('Failed to load theme mode: $e');
    }
  }

  /// Set theme mode and save to SharedPreferences
  /// تعيين وضع الثيم وحفظه
  Future<void> setThemeMode(ThemeMode mode) async {
    state = mode;

    try {
      final prefs = await SharedPreferences.getInstance();
      String modeString;
      switch (mode) {
        case ThemeMode.light:
          modeString = 'light';
          break;
        case ThemeMode.dark:
          modeString = 'dark';
          break;
        default:
          modeString = 'system';
      }
      await prefs.setString(_themeModeKey, modeString);
    } catch (e) {
      debugPrint('Failed to save theme mode: $e');
    }
  }

  /// Toggle between light and dark mode
  /// التبديل بين الوضع النهاري والليلي
  Future<void> toggleTheme() async {
    final newMode = state == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    await setThemeMode(newMode);
  }

  /// Set to system default
  /// العودة لإعدادات النظام
  Future<void> useSystemTheme() async {
    await setThemeMode(ThemeMode.system);
  }
}

/// Helper extension for ThemeMode
/// دالة مساعدة لوضع الثيم
extension ThemeModeExtension on ThemeMode {
  /// Get Arabic label for the theme mode
  /// الحصول على التسمية العربية لوضع الثيم
  String get labelAr {
    switch (this) {
      case ThemeMode.light:
        return 'نهاري';
      case ThemeMode.dark:
        return 'ليلي';
      case ThemeMode.system:
        return 'تلقائي';
    }
  }

  /// Get English label for the theme mode
  /// الحصول على التسمية الإنجليزية لوضع الثيم
  String get labelEn {
    switch (this) {
      case ThemeMode.light:
        return 'Light';
      case ThemeMode.dark:
        return 'Dark';
      case ThemeMode.system:
        return 'System';
    }
  }

  /// Get icon for the theme mode
  /// الحصول على الأيقونة لوضع الثيم
  IconData get icon {
    switch (this) {
      case ThemeMode.light:
        return Icons.light_mode_rounded;
      case ThemeMode.dark:
        return Icons.dark_mode_rounded;
      case ThemeMode.system:
        return Icons.brightness_auto_rounded;
    }
  }
}
