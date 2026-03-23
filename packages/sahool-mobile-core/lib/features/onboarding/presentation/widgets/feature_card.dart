import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/onboarding_step.dart';

/// SAHOOL Feature Card Widget
/// ويدجت بطاقة الميزة
///
/// Displays a feature in the onboarding tour with illustration and description
/// يعرض ميزة في جولة الإعداد مع رسم توضيحي ووصف

class FeatureCard extends StatelessWidget {
  /// Feature data
  final OnboardingFeature feature;

  /// Whether to use Arabic text
  final bool isArabic;

  /// Card width
  final double? width;

  /// Card height
  final double? height;

  /// Whether this card is currently active
  final bool isActive;

  /// Animation offset (for parallax effect)
  final double animationOffset;

  const FeatureCard({
    super.key,
    required this.feature,
    this.isArabic = true,
    this.width,
    this.height,
    this.isActive = true,
    this.animationOffset = 0.0,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 300),
        opacity: isActive ? 1.0 : 0.7,
        child: AnimatedScale(
          duration: const Duration(milliseconds: 300),
          scale: isActive ? 1.0 : 0.95,
          child: Container(
            width: width,
            height: height,
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Illustration
                _buildIllustration(context),
                const SizedBox(height: 40),

                // Title
                AnimatedSlide(
                  duration: const Duration(milliseconds: 400),
                  offset: Offset(animationOffset * 0.1, 0),
                  child: Text(
                    feature.getTitle(isArabic: isArabic),
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: SahoolColors.textDark,
                        ),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 16),

                // Description
                AnimatedSlide(
                  duration: const Duration(milliseconds: 500),
                  offset: Offset(animationOffset * 0.15, 0),
                  child: Text(
                    feature.getDescription(isArabic: isArabic),
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: SahoolColors.textSecondary,
                          height: 1.6,
                        ),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildIllustration(BuildContext context) {
    // Create a colorful illustration placeholder with icon
    return AnimatedSlide(
      duration: const Duration(milliseconds: 300),
      offset: Offset(animationOffset * 0.05, 0),
      child: Container(
        width: 220,
        height: 220,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(feature.colorValue).withOpacity(0.1),
              Color(feature.colorValue).withOpacity(0.2),
            ],
          ),
          borderRadius: BorderRadius.circular(32),
          boxShadow: [
            BoxShadow(
              color: Color(feature.colorValue).withOpacity(0.2),
              blurRadius: 30,
              spreadRadius: 10,
            ),
          ],
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Background decoration
            Positioned(
              top: 20,
              right: 20,
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Color(feature.colorValue).withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
              ),
            ),
            Positioned(
              bottom: 30,
              left: 30,
              child: Container(
                width: 24,
                height: 24,
                decoration: BoxDecoration(
                  color: Color(feature.colorValue).withOpacity(0.3),
                  shape: BoxShape.circle,
                ),
              ),
            ),

            // Main icon
            Icon(
              _getIconForFeature(feature.id),
              size: 100,
              color: Color(feature.colorValue),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getIconForFeature(String featureId) {
    switch (featureId) {
      case 'field_management':
        return Icons.landscape_rounded;
      case 'weather':
        return Icons.cloud_rounded;
      case 'ndvi':
        return Icons.satellite_alt_rounded;
      case 'irrigation':
        return Icons.water_drop_rounded;
      case 'tasks':
        return Icons.assignment_rounded;
      default:
        return Icons.eco_rounded;
    }
  }
}

/// Feature carousel for onboarding tour
/// دوار الميزات لجولة الإعداد
class FeatureCarousel extends StatefulWidget {
  /// List of features to display
  final List<OnboardingFeature> features;

  /// Current page index
  final int currentPage;

  /// Callback when page changes
  final ValueChanged<int>? onPageChanged;

  /// Whether to use Arabic text
  final bool isArabic;

  /// Page controller
  final PageController? controller;

  const FeatureCarousel({
    super.key,
    required this.features,
    required this.currentPage,
    this.onPageChanged,
    this.isArabic = true,
    this.controller,
  });

  @override
  State<FeatureCarousel> createState() => _FeatureCarouselState();
}

class _FeatureCarouselState extends State<FeatureCarousel> {
  late PageController _pageController;
  double _currentPageValue = 0.0;

  @override
  void initState() {
    super.initState();
    _pageController = widget.controller ??
        PageController(
          initialPage: widget.currentPage,
          viewportFraction: 1.0,
        );
    _pageController.addListener(_onPageScroll);
    _currentPageValue = widget.currentPage.toDouble();
  }

  @override
  void dispose() {
    _pageController.removeListener(_onPageScroll);
    if (widget.controller == null) {
      _pageController.dispose();
    }
    super.dispose();
  }

  void _onPageScroll() {
    setState(() {
      _currentPageValue = _pageController.page ?? 0.0;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: PageView.builder(
        controller: _pageController,
        itemCount: widget.features.length,
        onPageChanged: widget.onPageChanged,
        physics: const BouncingScrollPhysics(),
        itemBuilder: (context, index) {
          final feature = widget.features[index];
          final isActive = index == widget.currentPage;
          final offset = _currentPageValue - index;

          return FeatureCard(
            feature: feature,
            isArabic: widget.isArabic,
            isActive: isActive,
            animationOffset: offset,
          );
        },
      ),
    );
  }
}

/// Small feature preview card for mini carousel
/// بطاقة معاينة ميزة صغيرة للدوار الصغير
class FeaturePreviewCard extends StatelessWidget {
  /// Feature data
  final OnboardingFeature feature;

  /// Whether this card is selected
  final bool isSelected;

  /// Callback when card is tapped
  final VoidCallback? onTap;

  const FeaturePreviewCard({
    super.key,
    required this.feature,
    this.isSelected = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 80,
        height: 80,
        margin: const EdgeInsets.symmetric(horizontal: 4),
        decoration: BoxDecoration(
          color: isSelected
              ? Color(feature.colorValue).withOpacity(0.2)
              : Colors.grey[100],
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? Color(feature.colorValue) : Colors.transparent,
            width: 2,
          ),
        ),
        child: Icon(
          _getIconForFeature(feature.id),
          color: isSelected ? Color(feature.colorValue) : Colors.grey,
          size: 32,
        ),
      ),
    );
  }

  IconData _getIconForFeature(String featureId) {
    switch (featureId) {
      case 'field_management':
        return Icons.landscape_rounded;
      case 'weather':
        return Icons.cloud_rounded;
      case 'ndvi':
        return Icons.satellite_alt_rounded;
      case 'irrigation':
        return Icons.water_drop_rounded;
      case 'tasks':
        return Icons.assignment_rounded;
      default:
        return Icons.eco_rounded;
    }
  }
}
