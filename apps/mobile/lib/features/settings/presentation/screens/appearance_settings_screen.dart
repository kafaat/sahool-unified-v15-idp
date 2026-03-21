import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../../state/settings_providers.dart';
import '../widgets/widgets.dart';

/// Appearance Settings Screen
/// شاشة إعدادات المظهر
class AppearanceSettingsScreen extends ConsumerWidget {
  const AppearanceSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(appSettingsProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: isDark ? Colors.black : Colors.grey[100],
        appBar: AppBar(
          backgroundColor: isDark ? Colors.grey[900] : Colors.white,
          elevation: 0,
          title: Text(
            'المظهر',
            style: TextStyle(
              color: isDark ? Colors.white : Colors.black87,
              fontWeight: FontWeight.bold,
            ),
          ),
          centerTitle: true,
          leading: IconButton(
            icon: const Icon(Icons.arrow_forward_ios),
            color: isDark ? Colors.white : Colors.black87,
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.only(bottom: 32),
          children: [
            // Theme Section
            SettingsSection(
              title: 'Theme',
              titleAr: 'السمة',
              icon: Icons.brightness_6_outlined,
              children: [
                _ThemeSelector(
                  currentMode: settings.themeMode,
                  onChanged: (mode) {
                    ref.read(appSettingsProvider.notifier).setThemeMode(mode);
                  },
                ),
              ],
            ),

            // Language Section
            SettingsSection(
              title: 'Language',
              titleAr: 'اللغة',
              icon: Icons.language_outlined,
              children: [
                _LanguageSelector(
                  currentCode: settings.languageCode,
                  onChanged: (code) {
                    ref.read(appSettingsProvider.notifier).setLanguage(code);
                  },
                ),
              ],
            ),

            // Font Size Section
            SettingsSection(
              title: 'Font Size',
              titleAr: 'حجم الخط',
              icon: Icons.text_fields_outlined,
              children: [
                SliderSettingsTile(
                  title: 'Font Size',
                  titleAr: 'حجم الخط',
                  icon: Icons.format_size_rounded,
                  value: settings.fontSize,
                  min: 0.8,
                  max: 1.4,
                  divisions: 6,
                  showMinMaxLabels: true,
                  minLabel: 'صغير',
                  maxLabel: 'كبير',
                  labelFormatter: (value) {
                    if (value <= 0.85) return 'صغير';
                    if (value <= 0.95) return 'صغير+';
                    if (value <= 1.05) return 'متوسط';
                    if (value <= 1.15) return 'كبير-';
                    if (value <= 1.25) return 'كبير';
                    return 'كبير جداً';
                  },
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setFontSize(value);
                  },
                ),
                const SizedBox(height: 8),
                _FontPreview(fontSize: settings.fontSize),
              ],
            ),

            // Accessibility Section
            SettingsSection(
              title: 'Accessibility',
              titleAr: 'إمكانية الوصول',
              icon: Icons.accessibility_outlined,
              showDividers: true,
              children: [
                SwitchSettingsTile(
                  title: 'Reduce Animations',
                  titleAr: 'تقليل الحركة',
                  icon: Icons.animation_rounded,
                  value: settings.reduceAnimations,
                  subtitle: 'إيقاف الرسوم المتحركة',
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setReduceAnimations(value);
                  },
                ),
                SwitchSettingsTile(
                  title: 'High Contrast',
                  titleAr: 'تباين عالي',
                  icon: Icons.contrast_rounded,
                  value: false,
                  subtitle: 'زيادة تباين الألوان',
                  onChanged: (value) {
                    // Handle high contrast
                  },
                ),
                SwitchSettingsTile(
                  title: 'Bold Text',
                  titleAr: 'نص عريض',
                  icon: Icons.format_bold_rounded,
                  value: false,
                  subtitle: 'جعل كل النصوص عريضة',
                  onChanged: (value) {
                    // Handle bold text
                  },
                ),
              ],
            ),

            // App Icon Section (if applicable)
            SettingsSection(
              title: 'App Icon',
              titleAr: 'أيقونة التطبيق',
              icon: Icons.apps_outlined,
              children: [
                _AppIconSelector(),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Theme Selector Widget
class _ThemeSelector extends StatelessWidget {
  final ThemeMode currentMode;
  final ValueChanged<ThemeMode> onChanged;

  const _ThemeSelector({
    required this.currentMode,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: _ThemeOption(
              icon: Icons.brightness_auto,
              label: 'تلقائي',
              isSelected: currentMode == ThemeMode.system,
              onTap: () => onChanged(ThemeMode.system),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _ThemeOption(
              icon: Icons.light_mode,
              label: 'فاتح',
              isSelected: currentMode == ThemeMode.light,
              onTap: () => onChanged(ThemeMode.light),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _ThemeOption(
              icon: Icons.dark_mode,
              label: 'داكن',
              isSelected: currentMode == ThemeMode.dark,
              onTap: () => onChanged(ThemeMode.dark),
            ),
          ),
        ],
      ),
    );
  }
}

/// Theme Option Widget
class _ThemeOption extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _ThemeOption({
    required this.icon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected
              ? SahoolTheme.primary.withOpacity(0.1)
              : (isDark ? Colors.grey[800] : Colors.grey[200]),
          borderRadius: BorderRadius.circular(16),
          border: isSelected
              ? Border.all(color: SahoolTheme.primary, width: 2)
              : null,
        ),
        child: Column(
          children: [
            Icon(
              icon,
              size: 32,
              color: isSelected
                  ? SahoolTheme.primary
                  : (isDark ? Colors.white70 : Colors.grey[700]),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected
                    ? SahoolTheme.primary
                    : (isDark ? Colors.white : Colors.black87),
              ),
            ),
            if (isSelected) ...[
              const SizedBox(height: 4),
              const Icon(
                Icons.check_circle,
                size: 16,
                color: SahoolTheme.primary,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Language Selector Widget
class _LanguageSelector extends StatelessWidget {
  final String currentCode;
  final ValueChanged<String> onChanged;

  const _LanguageSelector({
    required this.currentCode,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: _LanguageOption(
              code: 'ar',
              label: 'العربية',
              flag: '🇾🇪',
              isSelected: currentCode == 'ar',
              onTap: () => onChanged('ar'),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _LanguageOption(
              code: 'en',
              label: 'English',
              flag: '🇬🇧',
              isSelected: currentCode == 'en',
              onTap: () => onChanged('en'),
            ),
          ),
        ],
      ),
    );
  }
}

/// Language Option Widget
class _LanguageOption extends StatelessWidget {
  final String code;
  final String label;
  final String flag;
  final bool isSelected;
  final VoidCallback onTap;

  const _LanguageOption({
    required this.code,
    required this.label,
    required this.flag,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected
              ? SahoolTheme.primary.withOpacity(0.1)
              : (isDark ? Colors.grey[800] : Colors.grey[200]),
          borderRadius: BorderRadius.circular(16),
          border: isSelected
              ? Border.all(color: SahoolTheme.primary, width: 2)
              : null,
        ),
        child: Column(
          children: [
            Text(
              flag,
              style: const TextStyle(fontSize: 32),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected
                    ? SahoolTheme.primary
                    : (isDark ? Colors.white : Colors.black87),
              ),
            ),
            if (isSelected) ...[
              const SizedBox(height: 4),
              const Icon(
                Icons.check_circle,
                size: 16,
                color: SahoolTheme.primary,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Font Preview Widget
class _FontPreview extends StatelessWidget {
  final double fontSize;

  const _FontPreview({required this.fontSize});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? Colors.grey[850] : Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isDark ? Colors.grey[700]! : Colors.grey[300]!,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'معاينة حجم الخط',
            style: TextStyle(
              fontSize: 12 * fontSize,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'مزرعة القمح - الحقل الأول',
            style: TextStyle(
              fontSize: 16 * fontSize,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'درجة الحرارة: 25° - الرطوبة: 65%',
            style: TextStyle(
              fontSize: 14 * fontSize,
            ),
          ),
        ],
      ),
    );
  }
}

/// App Icon Selector Widget
class _AppIconSelector extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _AppIconOption(
                color: SahoolTheme.primary,
                isSelected: true,
                label: 'الافتراضي',
              ),
              _AppIconOption(
                color: Colors.blue,
                isSelected: false,
                label: 'أزرق',
              ),
              _AppIconOption(
                color: Colors.orange,
                isSelected: false,
                label: 'برتقالي',
              ),
              _AppIconOption(
                color: Colors.purple,
                isSelected: false,
                label: 'بنفسجي',
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'تغيير أيقونة التطبيق قد يستغرق بضع ثوانٍ',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}

/// App Icon Option Widget
class _AppIconOption extends StatelessWidget {
  final Color color;
  final bool isSelected;
  final String label;

  const _AppIconOption({
    required this.color,
    required this.isSelected,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        // Change app icon
      },
      child: Column(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(14),
              border: isSelected
                  ? Border.all(color: Colors.white, width: 3)
                  : null,
              boxShadow: isSelected
                  ? [
                      BoxShadow(
                        color: color.withOpacity(0.5),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                    ]
                  : null,
            ),
            child: const Icon(
              Icons.grass,
              color: Colors.white,
              size: 28,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              color: isSelected ? color : Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}
