// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Dashboard Screen
// شاشة لوحة التحكم الرئيسية
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/atmosphere_theme.dart';
import '../widgets/holographic_field_card.dart';
import '../widgets/voice_control_button.dart';
import '../widgets/stats_panel.dart';
import '../widgets/weather_widget.dart';

/// Dashboard screen displaying farm overview, weather, and field status
///
/// This is the main screen of the SAHOOL Atmosphere app, providing:
/// - Weather information
/// - Farm statistics
/// - Active field status cards
/// - Voice control interface
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedNavIndex = 0;

  /// Handle bottom navigation item tap
  void _onNavItemTapped(int index) {
    HapticFeedback.selectionClick();
    setState(() {
      _selectedNavIndex = index;
    });
    // Navigation logic would be implemented here
    // For now, we stay on the dashboard
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AtmosphereColors.bgGradient,
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
                      Semantics(
                        label: 'الإشعارات',
                        hint: 'اضغط لعرض الإشعارات',
                        button: true,
                        child: IconButton(
                          icon: const Icon(Icons.notifications_outlined),
                          color: AtmosphereColors.textSecondary,
                          tooltip: 'الإشعارات',
                          onPressed: () {
                            HapticFeedback.lightImpact();
                            // TODO: Navigate to notifications screen
                          },
                        ),
                      ),
                      Semantics(
                        label: 'الملف الشخصي',
                        hint: 'اضغط لعرض الملف الشخصي',
                        button: true,
                        child: IconButton(
                          icon: const Icon(Icons.person_outline),
                          color: AtmosphereColors.textSecondary,
                          tooltip: 'الملف الشخصي',
                          onPressed: () {
                            HapticFeedback.lightImpact();
                            // TODO: Navigate to profile screen
                          },
                        ),
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

  /// Builds the greeting section based on time of day
  Widget _buildGreeting() {
    final hour = DateTime.now().hour;
    final String greeting;
    final String greetingEn;

    if (hour < 12) {
      greeting = 'صباح الخير';
      greetingEn = 'Good morning';
    } else if (hour < 17) {
      greeting = 'مساء الخير';
      greetingEn = 'Good afternoon';
    } else {
      greeting = 'مساء النور';
      greetingEn = 'Good evening';
    }

    const String farmerName = 'المزارع أحمد';

    return Semantics(
      label: '$greetingEn, Farmer Ahmed',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            greeting,
            style: AtmosphereTypography.bodyMedium,
          ),
          const SizedBox(height: AtmosphereSpacing.xs),
          Text(
            farmerName,
            style: AtmosphereTypography.displayMedium,
          ),
        ],
      ),
    );
  }

  /// Builds a section header with Arabic and English titles
  Widget _buildSectionHeader(String titleAr, String titleEn) {
    return Semantics(
      header: true,
      label: titleEn,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
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
          ),
          Semantics(
            label: 'عرض جميع $titleEn',
            hint: 'اضغط لعرض جميع العناصر',
            button: true,
            child: TextButton(
              onPressed: () {
                HapticFeedback.selectionClick();
                // TODO: Navigate to full list view
              },
              child: Text(
                'عرض الكل',
                style: AtmosphereTypography.bodyMedium.copyWith(
                  color: AtmosphereColors.success,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Builds the bottom navigation bar
  Widget _buildBottomNav() {
    return Container(
      decoration: BoxDecoration(
        color: AtmosphereColors.bgSecondary,
        border: const Border(
          top: BorderSide(
            color: AtmosphereColors.glassBorder,
            width: 1,
          ),
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: AtmosphereSpacing.sm),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildNavItem(
                index: 0,
                icon: Icons.home_outlined,
                activeIcon: Icons.home,
                label: 'الرئيسية',
                labelEn: 'Home',
              ),
              _buildNavItem(
                index: 1,
                icon: Icons.map_outlined,
                activeIcon: Icons.map,
                label: 'الخريطة',
                labelEn: 'Map',
              ),
              const SizedBox(width: 56), // Space for voice button
              _buildNavItem(
                index: 2,
                icon: Icons.agriculture_outlined,
                activeIcon: Icons.agriculture,
                label: 'المحاصيل',
                labelEn: 'Crops',
              ),
              _buildNavItem(
                index: 3,
                icon: Icons.menu,
                activeIcon: Icons.menu,
                label: 'المزيد',
                labelEn: 'More',
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Builds a single navigation item with accessibility support
  Widget _buildNavItem({
    required int index,
    required IconData icon,
    required IconData activeIcon,
    required String label,
    required String labelEn,
  }) {
    final bool isActive = _selectedNavIndex == index;

    return Semantics(
      label: labelEn,
      hint: isActive ? 'Selected' : 'Double tap to select',
      button: true,
      selected: isActive,
      child: InkWell(
        onTap: () => _onNavItemTapped(index),
        borderRadius: BorderRadius.circular(AtmosphereRadius.sm),
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AtmosphereSpacing.sm,
            vertical: AtmosphereSpacing.xs,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isActive ? activeIcon : icon,
                color: isActive
                    ? AtmosphereColors.success
                    : AtmosphereColors.textMuted,
                size: 24,
              ),
              const SizedBox(height: AtmosphereSpacing.xs),
              Text(
                label,
                style: AtmosphereTypography.bodySmall.copyWith(
                  color: isActive
                      ? AtmosphereColors.success
                      : AtmosphereColors.textMuted,
                  fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
