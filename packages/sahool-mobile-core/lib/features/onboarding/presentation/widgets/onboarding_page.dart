import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';

/// SAHOOL Onboarding Page Widget
/// ويدجت صفحة الإعداد الأولي
///
/// Base layout for onboarding screens with consistent styling
/// تخطيط أساسي لشاشات الإعداد مع تنسيق موحد

class OnboardingPage extends StatelessWidget {
  /// Main content of the page
  final Widget child;

  /// Title text (Arabic)
  final String? title;

  /// Subtitle text (Arabic)
  final String? subtitle;

  /// Header illustration widget
  final Widget? illustration;

  /// Primary action button text
  final String? primaryButtonText;

  /// Primary action callback
  final VoidCallback? onPrimaryAction;

  /// Secondary action button text
  final String? secondaryButtonText;

  /// Secondary action callback
  final VoidCallback? onSecondaryAction;

  /// Skip button text
  final String? skipText;

  /// Skip callback
  final VoidCallback? onSkip;

  /// Whether to show back button
  final bool showBackButton;

  /// Back button callback
  final VoidCallback? onBack;

  /// Progress indicator (0.0 - 1.0)
  final double? progress;

  /// Whether buttons are loading
  final bool isLoading;

  /// Background gradient colors
  final List<Color>? gradientColors;

  /// Padding for content area
  final EdgeInsets contentPadding;

  const OnboardingPage({
    super.key,
    required this.child,
    this.title,
    this.subtitle,
    this.illustration,
    this.primaryButtonText,
    this.onPrimaryAction,
    this.secondaryButtonText,
    this.onSecondaryAction,
    this.skipText,
    this.onSkip,
    this.showBackButton = false,
    this.onBack,
    this.progress,
    this.isLoading = false,
    this.gradientColors,
    this.contentPadding = const EdgeInsets.all(24),
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: DecoratedBox(
          decoration: BoxDecoration(
            gradient: gradientColors != null
                ? LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: gradientColors!,
                  )
                : null,
            color: gradientColors == null ? Colors.white : null,
          ),
          child: SafeArea(
            child: Column(
              children: [
                // Top bar with back and skip
                _buildTopBar(context),

                // Progress indicator
                if (progress != null) _buildProgressIndicator(),

                // Main content
                Expanded(
                  child: SingleChildScrollView(
                    padding: contentPadding,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Illustration
                        if (illustration != null) ...[
                          illustration!,
                          const SizedBox(height: 32),
                        ],

                        // Title
                        if (title != null) ...[
                          Text(
                            title!,
                            style: Theme.of(context)
                                .textTheme
                                .headlineMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: gradientColors != null
                                      ? Colors.white
                                      : SahoolColors.textDark,
                                ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 12),
                        ],

                        // Subtitle
                        if (subtitle != null) ...[
                          Text(
                            subtitle!,
                            style:
                                Theme.of(context).textTheme.bodyLarge?.copyWith(
                                      color: gradientColors != null
                                          ? Colors.white70
                                          : SahoolColors.textSecondary,
                                      height: 1.5,
                                    ),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 32),
                        ],

                        // Child content
                        child,
                      ],
                    ),
                  ),
                ),

                // Bottom buttons
                _buildBottomButtons(context),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTopBar(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Back button
          if (showBackButton)
            IconButton(
              icon: Icon(
                Icons.arrow_forward_rounded,
                color: gradientColors != null
                    ? Colors.white
                    : SahoolColors.textDark,
              ),
              onPressed: onBack,
              tooltip: 'رجوع',
            )
          else
            const SizedBox(width: 48),

          // Skip button
          if (skipText != null && onSkip != null)
            TextButton(
              onPressed: onSkip,
              child: Text(
                skipText!,
                style: TextStyle(
                  color: gradientColors != null
                      ? Colors.white70
                      : SahoolColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            )
          else
            const SizedBox(width: 48),
        ],
      ),
    );
  }

  Widget _buildProgressIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(4),
        child: LinearProgressIndicator(
          value: progress,
          backgroundColor: gradientColors != null
              ? Colors.white24
              : Colors.grey[200],
          valueColor: AlwaysStoppedAnimation<Color>(
            gradientColors != null ? Colors.white : SahoolColors.primary,
          ),
          minHeight: 4,
        ),
      ),
    );
  }

  Widget _buildBottomButtons(BuildContext context) {
    if (primaryButtonText == null && secondaryButtonText == null) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: gradientColors != null ? Colors.transparent : Colors.white,
        boxShadow: gradientColors == null
            ? [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -5),
                ),
              ]
            : null,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Primary button
          if (primaryButtonText != null)
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: isLoading ? null : onPrimaryAction,
                style: ElevatedButton.styleFrom(
                  backgroundColor: gradientColors != null
                      ? Colors.white
                      : SahoolColors.primary,
                  foregroundColor: gradientColors != null
                      ? SahoolColors.primary
                      : Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  elevation: gradientColors != null ? 0 : 4,
                ),
                child: isLoading
                    ? SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: gradientColors != null
                              ? SahoolColors.primary
                              : Colors.white,
                        ),
                      )
                    : Text(
                        primaryButtonText!,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),

          // Secondary button
          if (secondaryButtonText != null) ...[
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: TextButton(
                onPressed: isLoading ? null : onSecondaryAction,
                child: Text(
                  secondaryButtonText!,
                  style: TextStyle(
                    color: gradientColors != null
                        ? Colors.white
                        : SahoolColors.primary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
