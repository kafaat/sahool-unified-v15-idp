// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Dashboard Screen
// شاشة لوحة التحكم الرئيسية
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/atmosphere_theme.dart';
import '../widgets/holographic_field_card.dart';
import '../widgets/voice_control_button.dart';
import '../widgets/stats_panel.dart';
import '../widgets/weather_widget.dart';
import '../providers/theme_provider.dart';
import 'fields_list_screen.dart';
import 'field_map_screen.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  int _currentIndex = 0;

  void _navigateToTab(int index) {
    HapticFeedback.lightImpact();
    if (index == _currentIndex) return;

    switch (index) {
      case 1: // Map
        Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => const FieldMapScreen()),
        );
        break;
      case 2: // Fields
        Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => const FieldsListScreen()),
        );
        break;
      case 3: // More - Show theme options
        _showThemeOptions();
        break;
      default:
        setState(() => _currentIndex = index);
    }
  }

  /// Show theme selection bottom sheet
  /// عرض خيارات الثيم
  void _showThemeOptions() {
    final currentTheme = ref.read(themeModeProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: BoxDecoration(
          color: Theme.of(context).scaffoldBackgroundColor,
          borderRadius: const BorderRadius.vertical(
            top: Radius.circular(AtmosphereRadius.xl),
          ),
        ),
        padding: const EdgeInsets.all(AtmosphereSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Handle bar
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: isDark
                    ? AtmosphereColors.textMuted
                    : AtmosphereLightColors.textMuted,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: AtmosphereSpacing.lg),

            // Title
            Text(
              'الوضع | Theme',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: AtmosphereSpacing.lg),

            // Theme options
            _buildThemeOption(
              icon: Icons.brightness_auto_rounded,
              titleAr: 'تلقائي (حسب النظام)',
              titleEn: 'System Default',
              isSelected: currentTheme == ThemeMode.system,
              onTap: () {
                ref.read(themeModeProvider.notifier).setThemeMode(ThemeMode.system);
                Navigator.pop(context);
              },
            ),
            _buildThemeOption(
              icon: Icons.light_mode_rounded,
              titleAr: 'الوضع النهاري',
              titleEn: 'Light Mode',
              isSelected: currentTheme == ThemeMode.light,
              onTap: () {
                ref.read(themeModeProvider.notifier).setThemeMode(ThemeMode.light);
                Navigator.pop(context);
              },
            ),
            _buildThemeOption(
              icon: Icons.dark_mode_rounded,
              titleAr: 'الوضع الليلي',
              titleEn: 'Dark Mode',
              isSelected: currentTheme == ThemeMode.dark,
              onTap: () {
                ref.read(themeModeProvider.notifier).setThemeMode(ThemeMode.dark);
                Navigator.pop(context);
              },
            ),

            const SizedBox(height: AtmosphereSpacing.lg),
          ],
        ),
      ),
    );
  }

  Widget _buildThemeOption({
    required IconData icon,
    required String titleAr,
    required String titleEn,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = isDark ? AtmosphereColors.success : AtmosphereLightColors.success;
    final textColor = isDark ? AtmosphereColors.textPrimary : AtmosphereLightColors.textPrimary;
    final mutedColor = isDark ? AtmosphereColors.textMuted : AtmosphereLightColors.textMuted;

    return ListTile(
      onTap: onTap,
      leading: Icon(
        icon,
        color: isSelected ? primaryColor : mutedColor,
      ),
      title: Text(
        titleAr,
        style: TextStyle(
          color: isSelected ? primaryColor : textColor,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
      subtitle: Text(
        titleEn,
        style: TextStyle(
          color: mutedColor,
          fontSize: 12,
        ),
      ),
      trailing: isSelected
          ? Icon(Icons.check_circle, color: primaryColor)
          : null,
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: isDark
              ? AtmosphereColors.bgGradient
              : const LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    AtmosphereLightColors.bgPrimary,
                    AtmosphereLightColors.bgSecondary,
                  ],
                ),
        ),
        child: SafeArea(
          child: Stack(
            children: [
              // Main Content
              CustomScrollView(
                physics: const BouncingScrollPhysics(),
                slivers: [
                  // App Bar
                  SliverAppBar(
                    floating: true,
                    backgroundColor: Colors.transparent,
                    title: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'ساهول أتموسفير',
                          style: AtmosphereTypography.displaySmall.copyWith(
                            fontWeight: FontWeight.w300,
                            letterSpacing: 2,
                          ),
                        ),
                        Text(
                          'SAHOL ATMOSPHERE',
                          style: AtmosphereTypography.labelSmall.copyWith(
                            color: AtmosphereColors.success,
                            letterSpacing: 3,
                          ),
                        ),
                      ],
                    ),
                    actions: [
                      // Theme Toggle Button
                      IconButton(
                        icon: Icon(
                          isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
                        ),
                        color: isDark
                            ? AtmosphereColors.textSecondary
                            : AtmosphereLightColors.textSecondary,
                        onPressed: () {
                          HapticFeedback.lightImpact();
                          ref.read(themeModeProvider.notifier).toggleTheme();
                        },
                        tooltip: isDark ? 'الوضع النهاري' : 'الوضع الليلي',
                      ),
                      IconButton(
                        icon: const Icon(Icons.notifications_outlined),
                        color: isDark
                            ? AtmosphereColors.textSecondary
                            : AtmosphereLightColors.textSecondary,
                        onPressed: () {
                          HapticFeedback.lightImpact();
                          // TODO(P1): Navigate to notifications screen
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('الإشعارات قيد التطوير | Notifications coming soon'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.person_outline),
                        color: isDark
                            ? AtmosphereColors.textSecondary
                            : AtmosphereLightColors.textSecondary,
                        onPressed: () {
                          HapticFeedback.lightImpact();
                          // TODO(P1): Navigate to profile/settings screen
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('الملف الشخصي قيد التطوير | Profile coming soon'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        },
                      ),
                    ],
                  ),

                  // Content
                  SliverPadding(
                    padding: const EdgeInsets.all(AtmosphereSpacing.md),
                    sliver: SliverList(
                      delegate: SliverChildListDelegate([
                        // Greeting
                        _buildGreeting(),
                        const SizedBox(height: AtmosphereSpacing.lg),

                        // Weather Widget
                        const WeatherWidget(),
                        const SizedBox(height: AtmosphereSpacing.lg),

                        // Stats Panel
                        const StatsPanel(),
                        const SizedBox(height: AtmosphereSpacing.lg),

                        // Active Fields Section
                        _buildSectionHeader('الحقول النشطة', 'Active Fields'),
                        const SizedBox(height: AtmosphereSpacing.md),

                        // Holographic Field Cards
                        const HolographicFieldCard(
                          fieldName: 'حقل رقم 04 - قمح',
                          fieldNameEn: 'Field #04 - Wheat',
                          moisture: 64,
                          temperature: 28,
                          sunlight: 85,
                          status: FieldStatus.active,
                        ),
                        const SizedBox(height: AtmosphereSpacing.md),

                        const HolographicFieldCard(
                          fieldName: 'حقل رقم 07 - طماطم',
                          fieldNameEn: 'Field #07 - Tomato',
                          moisture: 38,
                          temperature: 34,
                          sunlight: 92,
                          status: FieldStatus.warning,
                        ),
                        const SizedBox(height: AtmosphereSpacing.md),

                        const HolographicFieldCard(
                          fieldName: 'حقل رقم 12 - نخيل',
                          fieldNameEn: 'Field #12 - Palm',
                          moisture: 72,
                          temperature: 29,
                          sunlight: 78,
                          status: FieldStatus.active,
                        ),
                        const SizedBox(height: AtmosphereSpacing.md),

                        const HolographicFieldCard(
                          fieldName: 'حقل رقم 15 - خس',
                          fieldNameEn: 'Field #15 - Lettuce',
                          moisture: 25,
                          temperature: 36,
                          sunlight: 95,
                          status: FieldStatus.alert,
                        ),

                        // Bottom padding for voice button
                        const SizedBox(height: 100),
                      ]),
                    ),
                  ),
                ],
              ),

              // Voice Control Button (Floating)
              const Positioned(
                bottom: AtmosphereSpacing.xl,
                left: 0,
                right: 0,
                child: Center(child: VoiceControlButton()),
              ),
            ],
          ),
        ),
      ),

      // Bottom Navigation
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  Widget _buildGreeting() {
    final hour = DateTime.now().hour;
    String greeting;
    if (hour < 12) {
      greeting = 'صباح الخير';
    } else if (hour < 17) {
      greeting = 'مساء الخير';
    } else {
      greeting = 'مساء النور';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          greeting,
          style: AtmosphereTypography.bodyMedium,
        ),
        const SizedBox(height: AtmosphereSpacing.xs),
        const Text(
          'المزارع أحمد',
          style: AtmosphereTypography.displayMedium,
        ),
      ],
    );
  }

  Widget _buildSectionHeader(String titleAr, String titleEn) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              titleAr,
              style: AtmosphereTypography.headlineLarge,
            ),
            Text(
              titleEn.toUpperCase(),
              style: AtmosphereTypography.labelSmall.copyWith(
                color: AtmosphereColors.success,
                letterSpacing: 2,
              ),
            ),
          ],
        ),
        TextButton(
          onPressed: () {
            HapticFeedback.lightImpact();
            Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const FieldsListScreen()),
            );
          },
          child: Text(
            'عرض الكل',
            style: AtmosphereTypography.bodyMedium.copyWith(
              color: AtmosphereColors.success,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildBottomNav() {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: isDark
            ? AtmosphereColors.bgSecondary
            : AtmosphereLightColors.bgSecondary,
        border: Border(
          top: BorderSide(
            color: isDark
                ? AtmosphereColors.glassBorder
                : AtmosphereLightColors.border,
            width: 1,
          ),
        ),
        boxShadow: isDark
            ? null
            : [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: AtmosphereSpacing.sm),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(Icons.home_outlined, 'الرئيسية', 0),
              _buildNavItem(Icons.map_outlined, 'الخريطة', 1),
              const SizedBox(width: 56), // Space for voice button
              _buildNavItem(Icons.agriculture_outlined, 'الحقول', 2),
              _buildNavItem(Icons.menu, 'المزيد', 3),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, int index) {
    final isActive = _currentIndex == index;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final activeColor = isDark ? AtmosphereColors.success : AtmosphereLightColors.success;
    final inactiveColor = isDark ? AtmosphereColors.textMuted : AtmosphereLightColors.textMuted;

    return GestureDetector(
      onTap: () => _navigateToTab(index),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isActive ? activeColor : inactiveColor,
            size: 24,
          ),
          const SizedBox(height: AtmosphereSpacing.xs),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: isActive ? activeColor : inactiveColor,
            ),
          ),
        ],
      ),
    );
  }
}
