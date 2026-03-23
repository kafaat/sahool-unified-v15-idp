import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/feature_card.dart';
import '../widgets/progress_dots.dart';
import '../../domain/onboarding_step.dart';
import '../../state/onboarding_providers.dart';

/// SAHOOL Features Tour Screen
/// شاشة جولة الميزات
///
/// Carousel showcasing key features of the app
/// دوار يعرض الميزات الرئيسية للتطبيق

class FeaturesTourScreen extends ConsumerStatefulWidget {
  /// Callback when tour is completed
  final VoidCallback? onComplete;

  /// Callback when user skips the tour
  final VoidCallback? onSkip;

  /// Callback when user goes back
  final VoidCallback? onBack;

  const FeaturesTourScreen({
    super.key,
    this.onComplete,
    this.onSkip,
    this.onBack,
  });

  @override
  ConsumerState<FeaturesTourScreen> createState() => _FeaturesTourScreenState();
}

class _FeaturesTourScreenState extends ConsumerState<FeaturesTourScreen> {
  late PageController _pageController;

  @override
  void initState() {
    super.initState();
    final currentPage = ref.read(featuresTourPageProvider);
    _pageController = PageController(initialPage: currentPage);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _onPageChanged(int page) {
    ref.read(onboardingControllerProvider.notifier).setFeaturesTourPage(page);
  }

  void _nextPage() {
    const features = OnboardingFeatures.features;
    final currentPage = ref.read(featuresTourPageProvider);

    if (currentPage < features.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    } else {
      // Last page - complete the tour
      widget.onComplete?.call();
    }
  }

  void _previousPage() {
    final currentPage = ref.read(featuresTourPageProvider);

    if (currentPage > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeInOut,
      );
    } else {
      // First page - go back
      widget.onBack?.call();
    }
  }

  @override
  Widget build(BuildContext context) {
    final features = ref.watch(onboardingFeaturesProvider);
    final currentPage = ref.watch(featuresTourPageProvider);
    final isLastPage = currentPage >= features.length - 1;
    final isFirstPage = currentPage <= 0;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: SafeArea(
          child: Column(
            children: [
              // Top bar
              _buildTopBar(isFirstPage),

              // Progress indicator
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: ProgressDots(
                  totalDots: features.length,
                  currentIndex: currentPage,
                  activeColor: SahoolColors.primary,
                  inactiveColor: Colors.grey[300],
                  onDotTapped: (index) {
                    _pageController.animateToPage(
                      index,
                      duration: const Duration(milliseconds: 400),
                      curve: Curves.easeInOut,
                    );
                  },
                ),
              ),

              const SizedBox(height: 24),

              // Feature carousel
              Expanded(
                child: FeatureCarousel(
                  features: features,
                  currentPage: currentPage,
                  onPageChanged: _onPageChanged,
                  controller: _pageController,
                  isArabic: true,
                ),
              ),

              // Bottom buttons
              _buildBottomButtons(isLastPage),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTopBar(bool isFirstPage) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Back button
          IconButton(
            icon: const Icon(Icons.arrow_forward_rounded),
            onPressed: _previousPage,
            tooltip: 'رجوع',
          ),

          // Page indicator text
          Consumer(
            builder: (context, ref, _) {
              final currentPage = ref.watch(featuresTourPageProvider);
              final total = OnboardingFeatures.features.length;
              return Text(
                '${currentPage + 1} / $total',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontWeight: FontWeight.w500,
                ),
              );
            },
          ),

          // Skip button
          TextButton(
            onPressed: widget.onSkip,
            child: Text(
              'تخطي',
              style: TextStyle(
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomButtons(bool isLastPage) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: Row(
        children: [
          // Previous button (only show if not first page)
          Consumer(
            builder: (context, ref, _) {
              final currentPage = ref.watch(featuresTourPageProvider);
              if (currentPage > 0) {
                return Expanded(
                  child: OutlinedButton(
                    onPressed: _previousPage,
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text('السابق'),
                  ),
                );
              }
              return const SizedBox.shrink();
            },
          ),

          Consumer(
            builder: (context, ref, _) {
              final currentPage = ref.watch(featuresTourPageProvider);
              if (currentPage > 0) {
                return const SizedBox(width: 16);
              }
              return const SizedBox.shrink();
            },
          ),

          // Next/Complete button
          Expanded(
            flex: 2,
            child: ElevatedButton(
              onPressed: _nextPage,
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    isLastPage ? 'متابعة' : 'التالي',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (!isLastPage) ...[
                    const SizedBox(width: 8),
                    const Icon(Icons.arrow_back_rounded, size: 20),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
