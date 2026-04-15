/// SAHOOL Feature Flags Configuration
/// إعدادات أعلام الميزات
///
/// Environment-specific and package-based configuration for feature flags.
library;

import 'feature_flag.dart';

/// Environment types
/// أنواع البيئات
enum FeatureFlagEnvironment {
  development('development', 'Development', 'التطوير'),
  staging('staging', 'Staging', 'الاختبار'),
  production('production', 'Production', 'الإنتاج');

  final String value;
  final String nameEn;
  final String nameAr;

  const FeatureFlagEnvironment(this.value, this.nameEn, this.nameAr);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static FeatureFlagEnvironment fromString(String value) {
    return FeatureFlagEnvironment.values.firstWhere(
      (e) => e.value == value,
      orElse: () => FeatureFlagEnvironment.development,
    );
  }
}

/// Feature flags configuration
/// إعدادات أعلام الميزات
class FeatureFlagsConfig {
  /// Current environment
  final FeatureFlagEnvironment environment;

  /// Remote config API endpoint
  final String? remoteConfigUrl;

  /// API key for remote config (if needed)
  final String? apiKey;

  /// Enable Firebase Remote Config
  final bool useFirebaseRemoteConfig;

  /// Fetch interval for remote flags
  final Duration fetchInterval;

  /// Cache expiry duration
  final Duration cacheExpiry;

  /// Enable debug mode (logs, developer tools)
  final bool debugMode;

  /// Enable analytics for flag usage
  final bool analyticsEnabled;

  /// Default package for new users
  final SubscriptionPackage defaultPackage;

  /// Environment-specific flag overrides
  final Map<String, bool> environmentOverrides;

  /// Role-based flag overrides
  final Map<String, Map<String, bool>> roleOverrides;

  /// Beta users list (user IDs that get beta features)
  final List<String> betaUserIds;

  /// A/B test configurations
  final Map<String, ABTestConfig> abTests;

  const FeatureFlagsConfig({
    required this.environment,
    this.remoteConfigUrl,
    this.apiKey,
    this.useFirebaseRemoteConfig = false,
    this.fetchInterval = const Duration(hours: 1),
    this.cacheExpiry = const Duration(days: 7),
    this.debugMode = false,
    this.analyticsEnabled = true,
    this.defaultPackage = SubscriptionPackage.free,
    this.environmentOverrides = const {},
    this.roleOverrides = const {},
    this.betaUserIds = const [],
    this.abTests = const {},
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Factory Constructors for Each Environment
  // ═══════════════════════════════════════════════════════════════════════════

  /// Development configuration
  /// إعدادات التطوير
  factory FeatureFlagsConfig.development() {
    return FeatureFlagsConfig(
      environment: FeatureFlagEnvironment.development,
      remoteConfigUrl: 'http://10.0.2.2:8000/api/v1/feature-flags',
      useFirebaseRemoteConfig: false,
      fetchInterval: const Duration(minutes: 5),
      cacheExpiry: const Duration(hours: 1),
      debugMode: true,
      analyticsEnabled: false,
      defaultPackage: SubscriptionPackage.enterprise, // All features in dev
      environmentOverrides: {
        // Enable all features in development
        FeatureFlag.betaFeatures.key: true,
        FeatureFlag.variableRateApplication.key: true,
        FeatureFlag.yieldPrediction.key: true,
        FeatureFlag.multiFarmManagement.key: true,
      },
    );
  }

  /// Staging configuration
  /// إعدادات الاختبار
  factory FeatureFlagsConfig.staging() {
    return FeatureFlagsConfig(
      environment: FeatureFlagEnvironment.staging,
      remoteConfigUrl: 'https://api-staging.sahool.app/api/v1/feature-flags',
      useFirebaseRemoteConfig: true,
      fetchInterval: const Duration(minutes: 15),
      cacheExpiry: const Duration(days: 1),
      debugMode: true,
      analyticsEnabled: true,
      defaultPackage: SubscriptionPackage.professional,
      environmentOverrides: {
        // Beta features available in staging
        FeatureFlag.betaFeatures.key: true,
      },
    );
  }

  /// Production configuration
  /// إعدادات الإنتاج
  factory FeatureFlagsConfig.production() {
    return const FeatureFlagsConfig(
      environment: FeatureFlagEnvironment.production,
      remoteConfigUrl: 'https://api.sahool.app/api/v1/feature-flags',
      useFirebaseRemoteConfig: true,
      fetchInterval: Duration(hours: 1),
      cacheExpiry: Duration(days: 7),
      debugMode: false,
      analyticsEnabled: true,
      defaultPackage: SubscriptionPackage.free,
      environmentOverrides: {},
    );
  }

  /// Create config from environment string
  factory FeatureFlagsConfig.fromEnvironment(String env) {
    switch (env.toLowerCase()) {
      case 'development':
      case 'dev':
        return FeatureFlagsConfig.development();
      case 'staging':
      case 'stage':
        return FeatureFlagsConfig.staging();
      case 'production':
      case 'prod':
        return FeatureFlagsConfig.production();
      default:
        return FeatureFlagsConfig.development();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Package Configurations
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all flags enabled for a specific package
  static Set<FeatureFlag> getFlagsForPackage(SubscriptionPackage package) {
    return FeatureFlag.values
        .where((flag) => flag.isEnabledForPackage(package))
        .toSet();
  }

  /// Get flags that differ between two packages (upgrade path)
  static Set<FeatureFlag> getUpgradeFlags(
    SubscriptionPackage from,
    SubscriptionPackage to,
  ) {
    final fromFlags = getFlagsForPackage(from);
    final toFlags = getFlagsForPackage(to);
    return toFlags.difference(fromFlags);
  }

  /// Package feature limits
  static PackageLimits getLimits(SubscriptionPackage package) {
    switch (package) {
      case SubscriptionPackage.free:
        return const PackageLimits(
          maxFields: 3,
          maxFarms: 1,
          maxTeamMembers: 1,
          maxStorageMb: 100,
          ndviUpdatesPerMonth: 2,
          supportLevel: SupportLevel.community,
        );
      case SubscriptionPackage.starter:
        return const PackageLimits(
          maxFields: 10,
          maxFarms: 2,
          maxTeamMembers: 3,
          maxStorageMb: 500,
          ndviUpdatesPerMonth: 4,
          supportLevel: SupportLevel.email,
        );
      case SubscriptionPackage.professional:
        return const PackageLimits(
          maxFields: 50,
          maxFarms: 5,
          maxTeamMembers: 10,
          maxStorageMb: 2000,
          ndviUpdatesPerMonth: 12,
          supportLevel: SupportLevel.priority,
        );
      case SubscriptionPackage.enterprise:
        return const PackageLimits(
          maxFields: -1, // Unlimited
          maxFarms: -1,
          maxTeamMembers: -1,
          maxStorageMb: -1,
          ndviUpdatesPerMonth: -1,
          supportLevel: SupportLevel.dedicated,
        );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Role-Based Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get flag override for a specific role
  bool? getRoleOverride(String role, FeatureFlag flag) {
    return roleOverrides[role]?[flag.key];
  }

  /// Check if user is a beta tester
  bool isBetaUser(String userId) {
    return betaUserIds.contains(userId);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // A/B Testing
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get A/B test configuration for a flag
  ABTestConfig? getABTest(String flagKey) {
    return abTests[flagKey];
  }

  /// Determine if user is in treatment group for A/B test
  bool isInTreatmentGroup(String userId, String flagKey) {
    final abTest = abTests[flagKey];
    if (abTest == null || !abTest.isActive) return false;

    // Simple hash-based bucketing
    final hash = userId.hashCode.abs();
    final bucket = hash % 100;
    return bucket < (abTest.treatmentPercentage * 100);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Utility Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Copy with modifications
  FeatureFlagsConfig copyWith({
    FeatureFlagEnvironment? environment,
    String? remoteConfigUrl,
    String? apiKey,
    bool? useFirebaseRemoteConfig,
    Duration? fetchInterval,
    Duration? cacheExpiry,
    bool? debugMode,
    bool? analyticsEnabled,
    SubscriptionPackage? defaultPackage,
    Map<String, bool>? environmentOverrides,
    Map<String, Map<String, bool>>? roleOverrides,
    List<String>? betaUserIds,
    Map<String, ABTestConfig>? abTests,
  }) {
    return FeatureFlagsConfig(
      environment: environment ?? this.environment,
      remoteConfigUrl: remoteConfigUrl ?? this.remoteConfigUrl,
      apiKey: apiKey ?? this.apiKey,
      useFirebaseRemoteConfig:
          useFirebaseRemoteConfig ?? this.useFirebaseRemoteConfig,
      fetchInterval: fetchInterval ?? this.fetchInterval,
      cacheExpiry: cacheExpiry ?? this.cacheExpiry,
      debugMode: debugMode ?? this.debugMode,
      analyticsEnabled: analyticsEnabled ?? this.analyticsEnabled,
      defaultPackage: defaultPackage ?? this.defaultPackage,
      environmentOverrides: environmentOverrides ?? this.environmentOverrides,
      roleOverrides: roleOverrides ?? this.roleOverrides,
      betaUserIds: betaUserIds ?? this.betaUserIds,
      abTests: abTests ?? this.abTests,
    );
  }

  Map<String, dynamic> toJson() => {
        'environment': environment.value,
        'remoteConfigUrl': remoteConfigUrl,
        'useFirebaseRemoteConfig': useFirebaseRemoteConfig,
        'fetchInterval': fetchInterval.inSeconds,
        'cacheExpiry': cacheExpiry.inSeconds,
        'debugMode': debugMode,
        'analyticsEnabled': analyticsEnabled,
        'defaultPackage': defaultPackage.value,
        'environmentOverrides': environmentOverrides,
        'betaUserIds': betaUserIds,
      };
}

/// Package limits configuration
/// إعدادات حدود الباقة
class PackageLimits {
  /// Maximum number of fields (-1 for unlimited)
  final int maxFields;

  /// Maximum number of farms (-1 for unlimited)
  final int maxFarms;

  /// Maximum number of team members (-1 for unlimited)
  final int maxTeamMembers;

  /// Maximum storage in MB (-1 for unlimited)
  final int maxStorageMb;

  /// NDVI updates per month (-1 for unlimited)
  final int ndviUpdatesPerMonth;

  /// Support level
  final SupportLevel supportLevel;

  const PackageLimits({
    required this.maxFields,
    required this.maxFarms,
    required this.maxTeamMembers,
    required this.maxStorageMb,
    required this.ndviUpdatesPerMonth,
    required this.supportLevel,
  });

  /// Check if a limit is unlimited
  bool isUnlimited(int limit) => limit == -1;

  /// Check if fields limit is reached
  bool canAddField(int currentCount) =>
      isUnlimited(maxFields) || currentCount < maxFields;

  /// Check if farms limit is reached
  bool canAddFarm(int currentCount) =>
      isUnlimited(maxFarms) || currentCount < maxFarms;

  /// Check if team members limit is reached
  bool canAddTeamMember(int currentCount) =>
      isUnlimited(maxTeamMembers) || currentCount < maxTeamMembers;

  Map<String, dynamic> toJson() => {
        'maxFields': maxFields,
        'maxFarms': maxFarms,
        'maxTeamMembers': maxTeamMembers,
        'maxStorageMb': maxStorageMb,
        'ndviUpdatesPerMonth': ndviUpdatesPerMonth,
        'supportLevel': supportLevel.value,
      };
}

/// Support level enum
/// مستوى الدعم
enum SupportLevel {
  community('community', 'Community', 'المجتمع'),
  email('email', 'Email Support', 'دعم البريد الإلكتروني'),
  priority('priority', 'Priority Support', 'الدعم الأولوي'),
  dedicated('dedicated', 'Dedicated Support', 'الدعم المخصص');

  final String value;
  final String nameEn;
  final String nameAr;

  const SupportLevel(this.value, this.nameEn, this.nameAr);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;
}

/// A/B test configuration
/// إعدادات اختبار A/B
class ABTestConfig {
  /// Test name
  final String name;

  /// Flag key being tested
  final String flagKey;

  /// Percentage of users in treatment group (0.0 to 1.0)
  final double treatmentPercentage;

  /// Test start date
  final DateTime startDate;

  /// Test end date (null if ongoing)
  final DateTime? endDate;

  /// Is test active
  final bool isActive;

  /// Test description
  final String? description;

  const ABTestConfig({
    required this.name,
    required this.flagKey,
    required this.treatmentPercentage,
    required this.startDate,
    this.endDate,
    this.isActive = true,
    this.description,
  });

  /// Check if test is currently running
  bool get isRunning {
    if (!isActive) return false;
    final now = DateTime.now();
    if (now.isBefore(startDate)) return false;
    if (endDate != null && now.isAfter(endDate!)) return false;
    return true;
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'flagKey': flagKey,
        'treatmentPercentage': treatmentPercentage,
        'startDate': startDate.toIso8601String(),
        'endDate': endDate?.toIso8601String(),
        'isActive': isActive,
        'description': description,
      };

  factory ABTestConfig.fromJson(Map<String, dynamic> json) {
    return ABTestConfig(
      name: json['name'] as String,
      flagKey: json['flagKey'] as String,
      treatmentPercentage: (json['treatmentPercentage'] as num).toDouble(),
      startDate: DateTime.tryParse(json['startDate'] as String) ?? DateTime.now(),
      endDate: json['endDate'] != null
          ? DateTime.tryParse(json['endDate'] as String) ?? DateTime.now()
          : null,
      isActive: json['isActive'] as bool? ?? true,
      description: json['description'] as String?,
    );
  }
}
