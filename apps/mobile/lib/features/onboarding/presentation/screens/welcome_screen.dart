import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/animated_illustration.dart';

/// SAHOOL Welcome Screen
/// شاشة الترحيب
///
/// First screen in the onboarding flow
/// الشاشة الأولى في تدفق الإعداد الأولي

class WelcomeScreen extends ConsumerWidget {
  /// Callback when user wants to start onboarding
  final VoidCallback? onGetStarted;

  /// Callback when user wants to skip onboarding
  final VoidCallback? onSkip;

  const WelcomeScreen({
    super.key,
    this.onGetStarted,
    this.onSkip,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: DecoratedBox(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                SahoolColors.primary,
                Color(0xFF1B4D1B),
              ],
            ),
          ),
          child: SafeArea(
            child: Column(
              children: [
                // Skip button
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Align(
                    alignment: Alignment.topLeft,
                    child: TextButton(
                      onPressed: onSkip,
                      child: const Text(
                        'تخطي',
                        style: TextStyle(
                          color: Colors.white70,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                ),

                // Main content
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // Animated logo illustration
                        const AnimatedIllustration(
                          type: IllustrationType.welcome,
                          size: 250,
                          primaryColor: Colors.white,
                        ),

                        const SizedBox(height: 48),

                        // Welcome text
                        Text(
                          'مرحباً بك في ساهول',
                          style: Theme.of(context)
                              .textTheme
                              .headlineMedium
                              ?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                          textAlign: TextAlign.center,
                        ),

                        const SizedBox(height: 16),

                        // Subtitle
                        Text(
                          'منصة الزراعة الذكية التي تساعدك على\nإدارة حقولك بكفاءة عالية',
                          style:
                              Theme.of(context).textTheme.bodyLarge?.copyWith(
                                    color: Colors.white70,
                                    height: 1.6,
                                  ),
                          textAlign: TextAlign.center,
                        ),

                        const SizedBox(height: 48),

                        // Feature highlights
                        _buildFeatureHighlights(),
                      ],
                    ),
                  ),
                ),

                // Bottom buttons
                Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      // Get started button
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: ElevatedButton(
                          onPressed: onGetStarted,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.white,
                            foregroundColor: SahoolColors.primary,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            elevation: 0,
                          ),
                          child: const Text(
                            'ابدأ الآن',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),

                      const SizedBox(height: 16),

                      // Already have account
                      TextButton(
                        onPressed: () {
                          // Navigate to login
                          Navigator.pushReplacementNamed(context, '/login');
                        },
                        child: const Text(
                          'لدي حساب بالفعل',
                          style: TextStyle(
                            color: Colors.white70,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureHighlights() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildFeatureItem(
          icon: Icons.landscape_rounded,
          label: 'إدارة الحقول',
        ),
        _buildFeatureItem(
          icon: Icons.cloud_rounded,
          label: 'توقعات الطقس',
        ),
        _buildFeatureItem(
          icon: Icons.eco_rounded,
          label: 'صحة المحصول',
        ),
      ],
    );
  }

  Widget _buildFeatureItem({
    required IconData icon,
    required String label,
  }) {
    return Column(
      children: [
        Container(
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.15),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Icon(
            icon,
            color: Colors.white,
            size: 28,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}
