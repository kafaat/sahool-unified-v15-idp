/// SAHOOL Feature Gate Widget
/// ودجت بوابة الميزات
///
/// Widgets and utilities for conditionally showing/hiding UI based on feature flags.
///
/// Usage:
/// ```dart
/// // Using widget
/// FeatureGate(
///   flag: FeatureFlag.aiAdvisory,
///   child: AIAdvisoryButton(),
///   fallback: UpgradePrompt(),
/// )
///
/// // Using extension
/// Container().withFeature(FeatureFlag.marketplace)
///
/// // Using helper function
/// if (featureEnabled(context, FeatureFlag.voiceCommands)) {
///   showVoiceControls();
/// }
/// ```
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'feature_flag.dart';
import 'feature_flags_providers.dart';
import 'feature_flags_service.dart';

/// FeatureGate Widget
/// ودجت بوابة الميزات
///
/// Shows child widget only if the feature flag is enabled.
/// Optionally shows a fallback widget when disabled.
class FeatureGate extends ConsumerWidget {
  /// Single feature flag to check
  final FeatureFlag? flag;

  /// Multiple flags (all must be enabled)
  final List<FeatureFlag>? allFlags;

  /// Multiple flags (any must be enabled)
  final List<FeatureFlag>? anyFlags;

  /// Child widget to show when feature is enabled
  final Widget child;

  /// Fallback widget when feature is disabled (optional)
  final Widget? fallback;

  /// Whether to hide completely or show fallback
  final bool hideCompletely;

  /// Animation duration for transitions
  final Duration animationDuration;

  /// Enable animation between states
  final bool animate;

  const FeatureGate({
    super.key,
    this.flag,
    this.allFlags,
    this.anyFlags,
    required this.child,
    this.fallback,
    this.hideCompletely = true,
    this.animationDuration = const Duration(milliseconds: 200),
    this.animate = false,
  }) : assert(
          flag != null || allFlags != null || anyFlags != null,
          'At least one flag condition must be specified',
        );

  /// Create a FeatureGate that requires all flags
  factory FeatureGate.all({
    Key? key,
    required List<FeatureFlag> flags,
    required Widget child,
    Widget? fallback,
    bool hideCompletely = true,
  }) {
    return FeatureGate(
      key: key,
      allFlags: flags,
      fallback: fallback,
      hideCompletely: hideCompletely,
      child: child,
    );
  }

  /// Create a FeatureGate that requires any flag
  factory FeatureGate.any({
    Key? key,
    required List<FeatureFlag> flags,
    required Widget child,
    Widget? fallback,
    bool hideCompletely = true,
  }) {
    return FeatureGate(
      key: key,
      anyFlags: flags,
      fallback: fallback,
      hideCompletely: hideCompletely,
      child: child,
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final featureFlagsService = ref.watch(featureFlagsServiceProvider);

    final isEnabled = _checkEnabled(featureFlagsService);

    if (animate) {
      return AnimatedSwitcher(
        duration: animationDuration,
        child: isEnabled
            ? child
            : (hideCompletely
                ? const SizedBox.shrink()
                : fallback ?? const SizedBox.shrink()),
      );
    }

    if (isEnabled) {
      return child;
    }

    if (hideCompletely) {
      return const SizedBox.shrink();
    }

    return fallback ?? const SizedBox.shrink();
  }

  bool _checkEnabled(FeatureFlagsService service) {
    // Check single flag
    if (flag != null && !service.isEnabled(flag!)) {
      return false;
    }

    // Check all flags
    if (allFlags != null && !service.allEnabled(allFlags!)) {
      return false;
    }

    // Check any flags
    if (anyFlags != null && !service.anyEnabled(anyFlags!)) {
      return false;
    }

    return true;
  }
}

/// FeatureBuilder - More flexible builder pattern
/// ودجت بناء الميزات
class FeatureBuilder extends ConsumerWidget {
  /// Feature flag to check
  final FeatureFlag flag;

  /// Builder function that receives enabled state
  final Widget Function(BuildContext context, bool isEnabled) builder;

  const FeatureBuilder({
    super.key,
    required this.flag,
    required this.builder,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final featureFlagsService = ref.watch(featureFlagsServiceProvider);
    final isEnabled = featureFlagsService.isEnabled(flag);

    return builder(context, isEnabled);
  }
}

/// MultiFeatureBuilder - Builder for multiple flags
/// ودجت بناء متعدد الميزات
class MultiFeatureBuilder extends ConsumerWidget {
  /// List of feature flags to check
  final List<FeatureFlag> flags;

  /// Builder function that receives map of flag states
  final Widget Function(
    BuildContext context,
    Map<FeatureFlag, bool> flagStates,
  ) builder;

  const MultiFeatureBuilder({
    super.key,
    required this.flags,
    required this.builder,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final featureFlagsService = ref.watch(featureFlagsServiceProvider);

    final flagStates = <FeatureFlag, bool>{};
    for (final flag in flags) {
      flagStates[flag] = featureFlagsService.isEnabled(flag);
    }

    return builder(context, flagStates);
  }
}

/// FeatureGateSliver - For use in CustomScrollView
/// ودجت بوابة الميزات للقوائم
class FeatureGateSliver extends ConsumerWidget {
  final FeatureFlag flag;
  final Widget sliver;
  final Widget? fallback;

  const FeatureGateSliver({
    super.key,
    required this.flag,
    required this.sliver,
    this.fallback,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isEnabled = ref.watch(featureEnabledProvider(flag));

    if (isEnabled) {
      return sliver;
    }

    return fallback ?? const SliverToBoxAdapter(child: SizedBox.shrink());
  }
}

/// Premium Feature Gate - Shows upgrade prompt for premium features
/// بوابة الميزات المميزة
class PremiumFeatureGate extends ConsumerWidget {
  final FeatureFlag flag;
  final Widget child;
  final String? upgradeTitle;
  final String? upgradeMessage;
  final VoidCallback? onUpgradeTap;

  const PremiumFeatureGate({
    super.key,
    required this.flag,
    required this.child,
    this.upgradeTitle,
    this.upgradeMessage,
    this.onUpgradeTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isEnabled = ref.watch(featureEnabledProvider(flag));
    final locale = Localizations.localeOf(context).languageCode;

    if (isEnabled) {
      return child;
    }

    // Show upgrade prompt
    return _UpgradePromptWidget(
      flag: flag,
      locale: locale,
      title: upgradeTitle,
      message: upgradeMessage,
      onUpgradeTap: onUpgradeTap,
    );
  }
}

/// Upgrade prompt widget
class _UpgradePromptWidget extends StatelessWidget {
  final FeatureFlag flag;
  final String locale;
  final String? title;
  final String? message;
  final VoidCallback? onUpgradeTap;

  const _UpgradePromptWidget({
    required this.flag,
    required this.locale,
    this.title,
    this.message,
    this.onUpgradeTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isArabic = locale == 'ar';

    final displayTitle = title ??
        (isArabic ? 'ميزة مميزة' : 'Premium Feature');
    final displayMessage = message ??
        (isArabic
            ? 'قم بالترقية للوصول إلى ${flag.nameAr}'
            : 'Upgrade to access ${flag.nameEn}');

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.outline.withValues(alpha: 0.2),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.lock_outline,
            size: 48,
            color: theme.colorScheme.primary,
          ),
          const SizedBox(height: 12),
          Text(
            displayTitle,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            displayMessage,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
          if (onUpgradeTap != null) ...[
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: onUpgradeTap,
              icon: const Icon(Icons.upgrade),
              label: Text(isArabic ? 'ترقية الآن' : 'Upgrade Now'),
            ),
          ],
        ],
      ),
    );
  }
}

/// Beta Feature Badge - Shows a badge for beta features
/// شارة الميزات التجريبية
class BetaFeatureBadge extends StatelessWidget {
  final Widget child;
  final bool showBadge;

  const BetaFeatureBadge({
    super.key,
    required this.child,
    this.showBadge = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!showBadge) return child;

    return Stack(
      clipBehavior: Clip.none,
      children: [
        child,
        Positioned(
          top: -4,
          right: -4,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: Colors.orange,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text(
              'BETA',
              style: TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Extension Methods
// ═══════════════════════════════════════════════════════════════════════════

/// Extension to add feature gating to any widget
extension FeatureGateExtension on Widget {
  /// Wrap widget with feature gate
  /// تغليف الودجت ببوابة الميزات
  Widget withFeature(
    FeatureFlag flag, {
    Widget? fallback,
    bool hideCompletely = true,
  }) {
    return FeatureGate(
      flag: flag,
      hideCompletely: hideCompletely,
      fallback: fallback,
      child: this,
    );
  }

  /// Wrap widget requiring all features
  Widget withAllFeatures(
    List<FeatureFlag> flags, {
    Widget? fallback,
    bool hideCompletely = true,
  }) {
    return FeatureGate.all(
      flags: flags,
      hideCompletely: hideCompletely,
      fallback: fallback,
      child: this,
    );
  }

  /// Wrap widget requiring any feature
  Widget withAnyFeature(
    List<FeatureFlag> flags, {
    Widget? fallback,
    bool hideCompletely = true,
  }) {
    return FeatureGate.any(
      flags: flags,
      hideCompletely: hideCompletely,
      fallback: fallback,
      child: this,
    );
  }

  /// Wrap with premium feature gate
  Widget withPremiumFeature(
    FeatureFlag flag, {
    String? upgradeTitle,
    String? upgradeMessage,
    VoidCallback? onUpgradeTap,
  }) {
    return PremiumFeatureGate(
      flag: flag,
      upgradeTitle: upgradeTitle,
      upgradeMessage: upgradeMessage,
      onUpgradeTap: onUpgradeTap,
      child: this,
    );
  }

  /// Add beta badge if feature is beta
  Widget withBetaBadge(bool isBeta) {
    return BetaFeatureBadge(
      showBadge: isBeta,
      child: this,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/// Check if a feature is enabled using provider ref
/// التحقق مما إذا كانت الميزة مفعلة
bool featureEnabled(WidgetRef ref, FeatureFlag flag) {
  return ref.read(featureEnabledProvider(flag));
}

/// Check if all features are enabled
bool allFeaturesEnabled(WidgetRef ref, List<FeatureFlag> flags) {
  final service = ref.read(featureFlagsServiceProvider);
  return service.allEnabled(flags);
}

/// Check if any feature is enabled
bool anyFeatureEnabled(WidgetRef ref, List<FeatureFlag> flags) {
  final service = ref.read(featureFlagsServiceProvider);
  return service.anyEnabled(flags);
}

/// Execute callback only if feature is enabled
/// تنفيذ الدالة فقط إذا كانت الميزة مفعلة
void ifFeatureEnabled(
  WidgetRef ref,
  FeatureFlag flag,
  VoidCallback callback, {
  VoidCallback? onDisabled,
}) {
  if (featureEnabled(ref, flag)) {
    callback();
  } else {
    onDisabled?.call();
  }
}

/// Get feature flag info for display
/// الحصول على معلومات علم الميزة للعرض
FeatureFlagDisplayInfo getFeatureInfo(FeatureFlag flag, String locale) {
  return FeatureFlagDisplayInfo(
    name: flag.getName(locale),
    description: flag.getDescription(locale),
    category: flag.category.getName(locale),
    icon: _getFeatureIcon(flag),
  );
}

/// Get icon for feature flag
IconData _getFeatureIcon(FeatureFlag flag) {
  switch (flag) {
    case FeatureFlag.ndviAnalysis:
      return Icons.grass;
    case FeatureFlag.satelliteImagery:
      return Icons.satellite_alt;
    case FeatureFlag.advancedReports:
      return Icons.analytics;
    case FeatureFlag.offlineMaps:
      return Icons.map_outlined;
    case FeatureFlag.pivotIrrigationControls:
      return Icons.water_drop;
    case FeatureFlag.variableRateApplication:
      return Icons.tune;
    case FeatureFlag.aiAdvisory:
      return Icons.psychology;
    case FeatureFlag.weatherAlerts:
      return Icons.cloud;
    case FeatureFlag.voiceCommands:
      return Icons.mic;
    case FeatureFlag.communityChat:
      return Icons.forum;
    case FeatureFlag.marketplace:
      return Icons.store;
    case FeatureFlag.equipmentTracking:
      return Icons.agriculture;
    case FeatureFlag.taskManagement:
      return Icons.task_alt;
    case FeatureFlag.fieldBoundaryEditing:
      return Icons.edit_location_alt;
    case FeatureFlag.yieldPrediction:
      return Icons.trending_up;
    case FeatureFlag.iotIntegration:
      return Icons.sensors;
    case FeatureFlag.multiFarmManagement:
      return Icons.business;
    case FeatureFlag.teamCollaboration:
      return Icons.groups;
    case FeatureFlag.betaFeatures:
      return Icons.science;
  }
}

/// Feature flag display information
class FeatureFlagDisplayInfo {
  final String name;
  final String description;
  final String category;
  final IconData icon;

  const FeatureFlagDisplayInfo({
    required this.name,
    required this.description,
    required this.category,
    required this.icon,
  });
}
