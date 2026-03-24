/// SAHOOL Feature Flags Providers
/// مزودات أعلام الميزات
///
/// Riverpod providers for feature flags management.
///
/// Usage:
/// ```dart
/// // Check if feature is enabled
/// final isEnabled = ref.watch(featureEnabledProvider(FeatureFlag.aiAdvisory));
///
/// // Get the service
/// final service = ref.watch(featureFlagsServiceProvider);
///
/// // Set override
/// ref.read(featureFlagsServiceProvider).setOverride(flag, true);
/// ```
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'feature_flag.dart';
import 'feature_flags_config.dart';
import 'feature_flags_service.dart';
import 'remote_config.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Configuration Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Feature flags configuration provider
/// مزود إعدادات أعلام الميزات
final featureFlagsConfigProvider = StateProvider<FeatureFlagsConfig>((ref) {
  // Default to development config
  // In production, this should be overridden based on environment
  return FeatureFlagsConfig.development();
});

/// Remote config service provider
/// مزود خدمة الإعدادات البعيدة
final remoteConfigServiceProvider = Provider<RemoteConfigService?>((ref) {
  final config = ref.watch(featureFlagsConfigProvider);
  if (config.remoteConfigUrl == null && !config.useFirebaseRemoteConfig) {
    return null;
  }
  return RemoteConfigFactory.create(config);
});

// ═══════════════════════════════════════════════════════════════════════════
// Main Service Provider
// ═══════════════════════════════════════════════════════════════════════════

/// Feature flags service provider (main entry point)
/// مزود خدمة أعلام الميزات (نقطة الدخول الرئيسية)
final featureFlagsServiceProvider =
    ChangeNotifierProvider<FeatureFlagsService>((ref) {
  final config = ref.watch(featureFlagsConfigProvider);
  final remoteConfig = ref.watch(remoteConfigServiceProvider);

  final service = FeatureFlagsService(
    remoteConfig: remoteConfig,
    config: config,
  );

  // Auto-initialize
  service.initialize();

  // Clean up on dispose
  ref.onDispose(() {
    service.dispose();
  });

  return service;
});

// ═══════════════════════════════════════════════════════════════════════════
// Flag State Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Check if a specific feature flag is enabled
/// التحقق مما إذا كان علم ميزة معين مفعلاً
final featureEnabledProvider = Provider.family<bool, FeatureFlag>((ref, flag) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.isEnabled(flag);
});

/// Check if feature is enabled by key string
/// التحقق مما إذا كانت الميزة مفعلة بواسطة المفتاح
final featureEnabledByKeyProvider =
    Provider.family<bool, String>((ref, key) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.isEnabledByKey(key);
});

/// Get feature flag value with metadata
/// الحصول على قيمة علم الميزة مع البيانات الوصفية
final featureFlagValueProvider =
    Provider.family<FeatureFlagValue?, FeatureFlag>((ref, flag) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.getFlagValue(flag);
});

/// All feature flags state
/// حالة جميع أعلام الميزات
final allFeatureFlagsProvider =
    Provider<Map<String, FeatureFlagValue>>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.allFlags;
});

/// Feature flags by category
/// أعلام الميزات حسب الفئة
final featureFlagsByCategoryProvider =
    Provider.family<List<FeatureFlag>, FeatureFlagCategory>((ref, category) {
  return FeatureFlag.byCategory(category);
});

/// Enabled features for current user
/// الميزات المفعلة للمستخدم الحالي
final enabledFeaturesProvider = Provider<List<FeatureFlag>>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return FeatureFlag.values.where((flag) => service.isEnabled(flag)).toList();
});

/// Disabled features for current user
/// الميزات المعطلة للمستخدم الحالي
final disabledFeaturesProvider = Provider<List<FeatureFlag>>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return FeatureFlag.values.where((flag) => !service.isEnabled(flag)).toList();
});

// ═══════════════════════════════════════════════════════════════════════════
// Package & Subscription Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Current subscription package
/// باقة الاشتراك الحالية
final currentPackageProvider = Provider<SubscriptionPackage>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.currentPackage;
});

/// Package limits for current subscription
/// حدود الباقة للاشتراك الحالي
final packageLimitsProvider = Provider<PackageLimits>((ref) {
  final package = ref.watch(currentPackageProvider);
  return FeatureFlagsConfig.getLimits(package);
});

/// Features available in current package
/// الميزات المتاحة في الباقة الحالية
final packageFeaturesProvider = Provider<Set<FeatureFlag>>((ref) {
  final package = ref.watch(currentPackageProvider);
  return FeatureFlagsConfig.getFlagsForPackage(package);
});

/// Upgrade path features (what you get if you upgrade)
/// ميزات مسار الترقية (ما ستحصل عليه إذا قمت بالترقية)
final upgradePathProvider = Provider.family<Set<FeatureFlag>, SubscriptionPackage>(
  (ref, targetPackage) {
    final currentPackage = ref.watch(currentPackageProvider);
    return FeatureFlagsConfig.getUpgradeFlags(currentPackage, targetPackage);
  },
);

// ═══════════════════════════════════════════════════════════════════════════
// Service State Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Service initialization state
/// حالة تهيئة الخدمة
final featureFlagsInitializedProvider = Provider<bool>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.isInitialized;
});

/// Service fetching state
/// حالة جلب الخدمة
final featureFlagsFetchingProvider = Provider<bool>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.isFetching;
});

/// Last fetch time
/// وقت آخر جلب
final lastFlagsFetchTimeProvider = Provider<DateTime?>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.lastFetchTime;
});

/// Active overrides
/// التجاوزات النشطة
final featureFlagsOverridesProvider = Provider<Map<String, bool>>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.overrides;
});

/// Check if a flag has an override
/// التحقق مما إذا كان للعلم تجاوز
final hasOverrideProvider = Provider.family<bool, FeatureFlag>((ref, flag) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.hasOverride(flag);
});

// ═══════════════════════════════════════════════════════════════════════════
// Debug & Analytics Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Debug info for feature flags
/// معلومات التصحيح لأعلام الميزات
final featureFlagsDebugInfoProvider = Provider<Map<String, dynamic>>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  return service.getDebugInfo();
});

/// Feature flag analytics data
/// بيانات تحليلات أعلام الميزات
final featureFlagAnalyticsProvider = Provider<FeatureFlagAnalytics>((ref) {
  final service = ref.watch(featureFlagsServiceProvider);
  final config = ref.watch(featureFlagsConfigProvider);

  final enabledCount = FeatureFlag.values
      .where((flag) => service.isEnabled(flag))
      .length;

  return FeatureFlagAnalytics(
    totalFlags: FeatureFlag.values.length,
    enabledFlags: enabledCount,
    disabledFlags: FeatureFlag.values.length - enabledCount,
    overrideCount: service.overrides.length,
    package: service.currentPackage,
    environment: config.environment,
    lastFetch: service.lastFetchTime,
  );
});

// ═══════════════════════════════════════════════════════════════════════════
// Helper Extension on WidgetRef
// ═══════════════════════════════════════════════════════════════════════════

/// Extension for easy feature flag access
/// إضافة للوصول السهل لأعلام الميزات
extension FeatureFlagsRefExtension on WidgetRef {
  /// Get feature flags service
  FeatureFlagsService get featureFlags => read(featureFlagsServiceProvider);

  /// Check if feature is enabled
  bool isFeatureEnabled(FeatureFlag flag) {
    return watch(featureEnabledProvider(flag));
  }

  /// Set feature override
  Future<void> setFeatureOverride(FeatureFlag flag, bool enabled) {
    return read(featureFlagsServiceProvider).setOverride(flag, enabled);
  }

  /// Remove feature override
  Future<void> removeFeatureOverride(FeatureFlag flag) {
    return read(featureFlagsServiceProvider).removeOverride(flag);
  }

  /// Fetch flags from remote
  Future<bool> fetchFeatureFlags({bool force = false}) {
    return read(featureFlagsServiceProvider).fetchFromRemote(force: force);
  }

  /// Get current package
  SubscriptionPackage get currentPackage {
    return read(currentPackageProvider);
  }

  /// Update subscription package
  Future<void> updatePackage(SubscriptionPackage package) {
    return read(featureFlagsServiceProvider).updatePackage(package);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Analytics Model
// ═══════════════════════════════════════════════════════════════════════════

/// Feature flag analytics data
/// بيانات تحليلات أعلام الميزات
class FeatureFlagAnalytics {
  final int totalFlags;
  final int enabledFlags;
  final int disabledFlags;
  final int overrideCount;
  final SubscriptionPackage package;
  final FeatureFlagEnvironment environment;
  final DateTime? lastFetch;

  const FeatureFlagAnalytics({
    required this.totalFlags,
    required this.enabledFlags,
    required this.disabledFlags,
    required this.overrideCount,
    required this.package,
    required this.environment,
    this.lastFetch,
  });

  double get enabledPercentage =>
      totalFlags > 0 ? enabledFlags / totalFlags * 100 : 0;

  Map<String, dynamic> toJson() => {
        'total_flags': totalFlags,
        'enabled_flags': enabledFlags,
        'disabled_flags': disabledFlags,
        'override_count': overrideCount,
        'enabled_percentage': enabledPercentage,
        'package': package.value,
        'environment': environment.value,
        'last_fetch': lastFetch?.toIso8601String(),
      };
}

// ═══════════════════════════════════════════════════════════════════════════
// Initialization Helper
// ═══════════════════════════════════════════════════════════════════════════

/// Initialize feature flags with configuration
/// تهيئة أعلام الميزات مع الإعدادات
Future<void> initializeFeatureFlags(
  ProviderContainer container, {
  required String environment,
  SubscriptionPackage? package,
  String? userRole,
  String? userId,
}) async {
  // Set configuration based on environment
  final config = FeatureFlagsConfig.fromEnvironment(environment);
  container.read(featureFlagsConfigProvider.notifier).state = config;

  // Initialize service
  final service = container.read(featureFlagsServiceProvider);
  await service.initialize(
    package: package,
    userRole: userRole,
  );

  // Fetch from remote if configured
  if (config.remoteConfigUrl != null || config.useFirebaseRemoteConfig) {
    await service.fetchFromRemote();
  }
}
