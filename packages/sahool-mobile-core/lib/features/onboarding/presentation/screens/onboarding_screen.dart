import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/animated_illustration.dart';
import '../../domain/onboarding_step.dart';
import '../../state/onboarding_providers.dart';
import 'welcome_screen.dart';
import 'features_tour_screen.dart';
import 'permissions_screen.dart';
import 'setup_profile_screen.dart';
import 'first_field_screen.dart';

/// SAHOOL Onboarding Screen
/// شاشة الإعداد الأولي الرئيسية
///
/// Main orchestrator for the onboarding flow
/// المنسق الرئيسي لتدفق الإعداد الأولي

class OnboardingScreen extends ConsumerWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentStep = ref.watch(currentOnboardingStepProvider);
    final controller = ref.read(onboardingControllerProvider.notifier);

    switch (currentStep) {
      case OnboardingStepType.welcome:
        return WelcomeScreen(
          onGetStarted: () => controller.nextStep(),
          onSkip: () => _confirmSkip(context, ref),
        );

      case OnboardingStepType.featuresTour:
        return FeaturesTourScreen(
          onComplete: () => controller.nextStep(),
          onSkip: () => controller.skipFeaturesTour(),
          onBack: () => controller.previousStep(),
        );

      case OnboardingStepType.permissions:
        return PermissionsScreen(
          onComplete: () => controller.nextStep(),
          onBack: () => controller.previousStep(),
        );

      case OnboardingStepType.profileSetup:
        return SetupProfileScreen(
          onComplete: () => controller.nextStep(),
          onBack: () => controller.previousStep(),
        );

      case OnboardingStepType.firstField:
        return FirstFieldScreen(
          onComplete: () => controller.nextStep(),
          onBack: () => controller.previousStep(),
        );

      case OnboardingStepType.completion:
        return _CompletionScreen(
          onComplete: () => _completeOnboarding(context, ref),
        );
    }
  }

  void _confirmSkip(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text('تخطي الإعداد؟'),
          content: const Text(
            'هل أنت متأكد من تخطي الإعداد الأولي؟ يمكنك الوصول لجميع الإعدادات لاحقاً.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إلغاء'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                ref.read(onboardingControllerProvider.notifier).skipOnboarding();
                Navigator.pushReplacementNamed(context, '/');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.warning,
              ),
              child: const Text('تخطي'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _completeOnboarding(BuildContext context, WidgetRef ref) async {
    await ref.read(onboardingControllerProvider.notifier).completeOnboarding();
    if (context.mounted) {
      Navigator.pushReplacementNamed(context, '/');
    }
  }
}

/// Completion celebration screen
/// شاشة احتفال الانتهاء
class _CompletionScreen extends StatelessWidget {
  final VoidCallback? onComplete;

  const _CompletionScreen({this.onComplete});

  @override
  Widget build(BuildContext context) {
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
                const Spacer(),

                // Celebration animation
                const AnimatedIllustration(
                  type: IllustrationType.completion,
                  size: 250,
                  primaryColor: Colors.white,
                ),

                const SizedBox(height: 48),

                // Congratulations text
                Text(
                  'تهانينا!',
                  style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                ),

                const SizedBox(height: 16),

                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 32),
                  child: Text(
                    'أنت جاهز للبدء في استخدام ساهول\nلإدارة حقولك بذكاء',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: Colors.white70,
                          height: 1.6,
                        ),
                    textAlign: TextAlign.center,
                  ),
                ),

                const SizedBox(height: 40),

                // Summary stats (if applicable)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 32),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _buildStatItem(
                        icon: Icons.check_circle_rounded,
                        value: 'تم',
                        label: 'الملف الشخصي',
                      ),
                      _buildStatItem(
                        icon: Icons.security_rounded,
                        value: 'تم',
                        label: 'الأذونات',
                      ),
                      _buildStatItem(
                        icon: Icons.landscape_rounded,
                        value: 'جاهز',
                        label: 'إضافة حقول',
                      ),
                    ],
                  ),
                ),

                const Spacer(),

                // Start button
                Padding(
                  padding: const EdgeInsets.all(24),
                  child: SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: onComplete,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: SahoolColors.primary,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                        elevation: 0,
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'ابدأ الاستخدام',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(width: 8),
                          Icon(Icons.arrow_back_rounded),
                        ],
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String value,
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
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 11,
          ),
        ),
      ],
    );
  }
}
