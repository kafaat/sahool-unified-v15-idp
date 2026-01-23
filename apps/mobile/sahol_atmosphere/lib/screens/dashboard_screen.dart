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
import 'fields_list_screen.dart';
import 'field_map_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
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
      default:
        setState(() => _currentIndex = index);
    }
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
                      IconButton(
                        icon: const Icon(Icons.notifications_outlined),
                        color: AtmosphereColors.textSecondary,
                        onPressed: () {
                          HapticFeedback.lightImpact();
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.person_outline),
                        color: AtmosphereColors.textSecondary,
                        onPressed: () {
                          HapticFeedback.lightImpact();
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
        Text(
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
    return Container(
      decoration: BoxDecoration(
        color: AtmosphereColors.bgSecondary,
        border: Border(
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
    return GestureDetector(
      onTap: () => _navigateToTab(index),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isActive ? AtmosphereColors.success : AtmosphereColors.textMuted,
            size: 24,
          ),
          const SizedBox(height: AtmosphereSpacing.xs),
          Text(
            label,
            style: AtmosphereTypography.bodySmall.copyWith(
              color: isActive ? AtmosphereColors.success : AtmosphereColors.textMuted,
            ),
          ),
        ],
      ),
    );
  }
}
