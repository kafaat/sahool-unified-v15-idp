import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';

/// SAHOOL Progress Dots Widget
/// ويدجت نقاط التقدم
///
/// Pagination dots for onboarding carousel/pages
/// نقاط الترقيم لصفحات الإعداد

class ProgressDots extends StatelessWidget {
  /// Total number of dots
  final int totalDots;

  /// Current active dot index
  final int currentIndex;

  /// Active dot color
  final Color? activeColor;

  /// Inactive dot color
  final Color? inactiveColor;

  /// Dot size
  final double dotSize;

  /// Active dot width (for pill shape)
  final double activeDotWidth;

  /// Spacing between dots
  final double spacing;

  /// Animation duration
  final Duration animationDuration;

  /// Callback when a dot is tapped
  final ValueChanged<int>? onDotTapped;

  const ProgressDots({
    super.key,
    required this.totalDots,
    required this.currentIndex,
    this.activeColor,
    this.inactiveColor,
    this.dotSize = 8,
    this.activeDotWidth = 24,
    this.spacing = 8,
    this.animationDuration = const Duration(milliseconds: 300),
    this.onDotTapped,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: List.generate(totalDots, (index) {
          final isActive = index == currentIndex;

          return GestureDetector(
            onTap: onDotTapped != null ? () => onDotTapped!(index) : null,
            child: AnimatedContainer(
              duration: animationDuration,
              curve: Curves.easeInOut,
              margin: EdgeInsets.symmetric(horizontal: spacing / 2),
              height: dotSize,
              width: isActive ? activeDotWidth : dotSize,
              decoration: BoxDecoration(
                color: isActive
                    ? (activeColor ?? SahoolColors.primary)
                    : (inactiveColor ?? Colors.grey[300]),
                borderRadius: BorderRadius.circular(dotSize / 2),
              ),
            ),
          );
        }),
      ),
    );
  }
}

/// Animated progress dots with scale effect
/// نقاط تقدم متحركة مع تأثير التكبير
class AnimatedProgressDots extends StatelessWidget {
  /// Total number of dots
  final int totalDots;

  /// Current active dot index
  final int currentIndex;

  /// Active dot color
  final Color? activeColor;

  /// Inactive dot color
  final Color? inactiveColor;

  /// Base dot size
  final double dotSize;

  /// Scale factor for active dot
  final double activeScale;

  /// Spacing between dots
  final double spacing;

  /// Animation duration
  final Duration animationDuration;

  /// Callback when a dot is tapped
  final ValueChanged<int>? onDotTapped;

  const AnimatedProgressDots({
    super.key,
    required this.totalDots,
    required this.currentIndex,
    this.activeColor,
    this.inactiveColor,
    this.dotSize = 10,
    this.activeScale = 1.4,
    this.spacing = 12,
    this.animationDuration = const Duration(milliseconds: 300),
    this.onDotTapped,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: List.generate(totalDots, (index) {
          final isActive = index == currentIndex;

          return GestureDetector(
            onTap: onDotTapped != null ? () => onDotTapped!(index) : null,
            child: Container(
              margin: EdgeInsets.symmetric(horizontal: spacing / 2),
              child: AnimatedScale(
                scale: isActive ? activeScale : 1.0,
                duration: animationDuration,
                curve: Curves.elasticOut,
                child: AnimatedContainer(
                  duration: animationDuration,
                  curve: Curves.easeInOut,
                  height: dotSize,
                  width: dotSize,
                  decoration: BoxDecoration(
                    color: isActive
                        ? (activeColor ?? SahoolColors.primary)
                        : (inactiveColor ?? Colors.grey[300]),
                    shape: BoxShape.circle,
                    boxShadow: isActive
                        ? [
                            BoxShadow(
                              color: (activeColor ?? SahoolColors.primary)
                                  .withValues(alpha: 0.4),
                              blurRadius: 8,
                              spreadRadius: 2,
                            ),
                          ]
                        : null,
                  ),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
}

/// Step progress indicator with numbers
/// مؤشر تقدم الخطوات مع الأرقام
class StepProgressIndicator extends StatelessWidget {
  /// Total number of steps
  final int totalSteps;

  /// Current step (1-indexed for display)
  final int currentStep;

  /// Step labels (optional)
  final List<String>? stepLabels;

  /// Active color
  final Color? activeColor;

  /// Completed color
  final Color? completedColor;

  /// Inactive color
  final Color? inactiveColor;

  /// Step size
  final double stepSize;

  /// Line thickness
  final double lineThickness;

  const StepProgressIndicator({
    super.key,
    required this.totalSteps,
    required this.currentStep,
    this.stepLabels,
    this.activeColor,
    this.completedColor,
    this.inactiveColor,
    this.stepSize = 32,
    this.lineThickness = 2,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: List.generate(totalSteps * 2 - 1, (index) {
          // Even indices are steps, odd indices are lines
          if (index.isEven) {
            final stepIndex = index ~/ 2;
            final stepNumber = stepIndex + 1;
            final isCompleted = stepNumber < currentStep;
            final isActive = stepNumber == currentStep;

            return _buildStep(
              context,
              stepNumber: stepNumber,
              isCompleted: isCompleted,
              isActive: isActive,
              label: stepLabels != null && stepIndex < stepLabels!.length
                  ? stepLabels![stepIndex]
                  : null,
            );
          } else {
            final lineIndex = index ~/ 2;
            final isCompleted = lineIndex + 1 < currentStep;

            return _buildLine(isCompleted);
          }
        }),
      ),
    );
  }

  Widget _buildStep(
    BuildContext context, {
    required int stepNumber,
    required bool isCompleted,
    required bool isActive,
    String? label,
  }) {
    Color backgroundColor;
    Color textColor;

    if (isCompleted) {
      backgroundColor = completedColor ?? SahoolColors.success;
      textColor = Colors.white;
    } else if (isActive) {
      backgroundColor = activeColor ?? SahoolColors.primary;
      textColor = Colors.white;
    } else {
      backgroundColor = inactiveColor ?? Colors.grey[200]!;
      textColor = Colors.grey;
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
          width: stepSize,
          height: stepSize,
          decoration: BoxDecoration(
            color: backgroundColor,
            shape: BoxShape.circle,
            boxShadow: isActive
                ? [
                    BoxShadow(
                      color: backgroundColor.withValues(alpha: 0.4),
                      blurRadius: 8,
                      spreadRadius: 2,
                    ),
                  ]
                : null,
          ),
          child: Center(
            child: isCompleted
                ? Icon(
                    Icons.check_rounded,
                    color: textColor,
                    size: stepSize * 0.5,
                  )
                : Text(
                    stepNumber.toString(),
                    style: TextStyle(
                      color: textColor,
                      fontWeight: FontWeight.bold,
                      fontSize: stepSize * 0.4,
                    ),
                  ),
          ),
        ),
        if (label != null) ...[
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: isActive
                  ? (activeColor ?? SahoolColors.primary)
                  : Colors.grey,
              fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildLine(bool isCompleted) {
    return Expanded(
      child: Container(
        height: lineThickness,
        margin: const EdgeInsets.symmetric(horizontal: 8),
        decoration: BoxDecoration(
          color: isCompleted
              ? (completedColor ?? SahoolColors.success)
              : (inactiveColor ?? Colors.grey[200]),
          borderRadius: BorderRadius.circular(lineThickness / 2),
        ),
      ),
    );
  }
}
