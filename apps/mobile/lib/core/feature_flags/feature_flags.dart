/// SAHOOL Feature Flags Module
/// وحدة أعلام الميزات
///
/// Comprehensive feature flags system for the SAHOOL mobile app.
///
/// Features:
/// - Dynamic feature flag management
/// - Package-based feature access (Starter, Professional, Enterprise)
/// - Remote configuration from API or Firebase
/// - Offline caching for offline-first support
/// - Override flags for testing
/// - Widget-based feature gating
/// - Riverpod state management
///
/// Usage:
/// ```dart
/// import 'package:sahool_field_app/core/feature_flags/feature_flags.dart';
///
/// // Check if feature is enabled
/// final isEnabled = ref.watch(featureEnabledProvider(FeatureFlag.aiAdvisory));
///
/// // Use FeatureGate widget
/// FeatureGate(
///   flag: FeatureFlag.marketplace,
///   child: MarketplaceScreen(),
///   fallback: UpgradePrompt(),
/// )
///
/// // Use extension method
/// MyWidget().withFeature(FeatureFlag.voiceCommands)
///
/// // Override for testing
/// ref.read(featureFlagsServiceProvider).setOverride(flag, true);
/// ```

library;

// Feature flag definitions
export 'feature_flag.dart';

// Configuration
export 'feature_flags_config.dart';

// Service
export 'feature_flags_service.dart';

// Remote config
export 'remote_config.dart';

// Widgets and helpers
export 'feature_gate.dart';

// Riverpod providers
export 'feature_flags_providers.dart';
