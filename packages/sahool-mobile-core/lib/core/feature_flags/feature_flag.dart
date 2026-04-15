/// SAHOOL Feature Flags - Feature Flag Definitions
/// تعريفات أعلام الميزات
///
/// This file defines all feature flags available in the SAHOOL mobile app.
/// Each flag has English and Arabic names, descriptions, and default values.
library;

/// Feature flag categories for organization
/// فئات أعلام الميزات للتنظيم
enum FeatureFlagCategory {
  analytics('Analytics', 'التحليلات'),
  maps('Maps', 'الخرائط'),
  irrigation('Irrigation', 'الري'),
  advisory('Advisory', 'الاستشارات'),
  communication('Communication', 'التواصل'),
  operations('Operations', 'العمليات'),
  premium('Premium', 'المميزة');

  final String nameEn;
  final String nameAr;

  const FeatureFlagCategory(this.nameEn, this.nameAr);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;
}

/// All feature flags in SAHOOL mobile app
/// جميع أعلام الميزات في تطبيق سهول
enum FeatureFlag {
  // ═══════════════════════════════════════════════════════════════════════════
  // Analytics & Intelligence - التحليلات والذكاء
  // ═══════════════════════════════════════════════════════════════════════════

  /// NDVI vegetation analysis
  /// تحليل مؤشر الغطاء النباتي
  ndviAnalysis(
    key: 'ndvi_analysis',
    nameEn: 'NDVI Analysis',
    nameAr: 'تحليل NDVI',
    descriptionEn: 'Vegetation health analysis using satellite imagery',
    descriptionAr: 'تحليل صحة النباتات باستخدام صور الأقمار الصناعية',
    category: FeatureFlagCategory.analytics,
    defaultEnabled: true,
    starterEnabled: true,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Satellite imagery access
  /// الوصول لصور الأقمار الصناعية
  satelliteImagery(
    key: 'satellite_imagery',
    nameEn: 'Satellite Imagery',
    nameAr: 'صور الأقمار الصناعية',
    descriptionEn: 'Access to high-resolution satellite imagery',
    descriptionAr: 'الوصول إلى صور الأقمار الصناعية عالية الدقة',
    category: FeatureFlagCategory.analytics,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Advanced reports and analytics
  /// التقارير والتحليلات المتقدمة
  advancedReports(
    key: 'advanced_reports',
    nameEn: 'Advanced Reports',
    nameAr: 'التقارير المتقدمة',
    descriptionEn: 'Detailed analytics reports with export capabilities',
    descriptionAr: 'تقارير تحليلية مفصلة مع إمكانية التصدير',
    category: FeatureFlagCategory.analytics,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  // ═══════════════════════════════════════════════════════════════════════════
  // Maps & Location - الخرائط والموقع
  // ═══════════════════════════════════════════════════════════════════════════

  /// Offline maps download and usage
  /// تحميل واستخدام الخرائط بدون اتصال
  offlineMaps(
    key: 'offline_maps',
    nameEn: 'Offline Maps',
    nameAr: 'الخرائط بدون اتصال',
    descriptionEn: 'Download and use maps without internet connection',
    descriptionAr: 'تحميل واستخدام الخرائط بدون اتصال بالإنترنت',
    category: FeatureFlagCategory.maps,
    defaultEnabled: true,
    starterEnabled: true,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation - الري
  // ═══════════════════════════════════════════════════════════════════════════

  /// Pivot irrigation controls
  /// أدوات التحكم بري البيفوت
  pivotIrrigationControls(
    key: 'pivot_irrigation_controls',
    nameEn: 'Pivot Irrigation Controls',
    nameAr: 'التحكم بري البيفوت',
    descriptionEn: 'Remote control and monitoring of pivot irrigation systems',
    descriptionAr: 'التحكم والمراقبة عن بعد لأنظمة ري البيفوت',
    category: FeatureFlagCategory.irrigation,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Variable Rate Application (VRA)
  /// التطبيق بمعدل متغير
  variableRateApplication(
    key: 'vra',
    nameEn: 'Variable Rate Application',
    nameAr: 'التطبيق بمعدل متغير',
    descriptionEn: 'Precision application of inputs based on field variability',
    descriptionAr: 'التطبيق الدقيق للمدخلات بناءً على تباين الحقل',
    category: FeatureFlagCategory.irrigation,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: false,
    enterpriseEnabled: true,
  ),

  // ═══════════════════════════════════════════════════════════════════════════
  // Advisory & Intelligence - الاستشارات والذكاء
  // ═══════════════════════════════════════════════════════════════════════════

  /// AI-powered agricultural advisory
  /// الاستشارات الزراعية المدعومة بالذكاء الاصطناعي
  aiAdvisory(
    key: 'ai_advisory',
    nameEn: 'AI Advisory',
    nameAr: 'المستشار الذكي',
    descriptionEn: 'AI-powered crop recommendations and disease detection',
    descriptionAr: 'توصيات المحاصيل واكتشاف الأمراض المدعومة بالذكاء الاصطناعي',
    category: FeatureFlagCategory.advisory,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Weather alerts and notifications
  /// تنبيهات وإشعارات الطقس
  weatherAlerts(
    key: 'weather_alerts',
    nameEn: 'Weather Alerts',
    nameAr: 'تنبيهات الطقس',
    descriptionEn: 'Real-time weather alerts and forecasts',
    descriptionAr: 'تنبيهات الطقس والتوقعات في الوقت الفعلي',
    category: FeatureFlagCategory.advisory,
    defaultEnabled: true,
    starterEnabled: true,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  // ═══════════════════════════════════════════════════════════════════════════
  // Communication - التواصل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Voice commands for hands-free operation
  /// الأوامر الصوتية للتشغيل بدون استخدام اليدين
  voiceCommands(
    key: 'voice_commands',
    nameEn: 'Voice Commands',
    nameAr: 'الأوامر الصوتية',
    descriptionEn: 'Control the app using voice commands',
    descriptionAr: 'التحكم في التطبيق باستخدام الأوامر الصوتية',
    category: FeatureFlagCategory.communication,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Community chat and collaboration
  /// الدردشة والتعاون المجتمعي
  communityChat(
    key: 'community_chat',
    nameEn: 'Community Chat',
    nameAr: 'دردشة المجتمع',
    descriptionEn: 'Chat with other farmers and experts',
    descriptionAr: 'الدردشة مع المزارعين والخبراء الآخرين',
    category: FeatureFlagCategory.communication,
    defaultEnabled: true,
    starterEnabled: true,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  // ═══════════════════════════════════════════════════════════════════════════
  // Operations - العمليات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Agricultural marketplace
  /// السوق الزراعي
  marketplace(
    key: 'marketplace',
    nameEn: 'Marketplace',
    nameAr: 'السوق',
    descriptionEn: 'Buy and sell agricultural products and services',
    descriptionAr: 'شراء وبيع المنتجات والخدمات الزراعية',
    category: FeatureFlagCategory.operations,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Equipment tracking and management
  /// تتبع وإدارة المعدات
  equipmentTracking(
    key: 'equipment_tracking',
    nameEn: 'Equipment Tracking',
    nameAr: 'تتبع المعدات',
    descriptionEn: 'Track and manage farm equipment and machinery',
    descriptionAr: 'تتبع وإدارة المعدات والآلات الزراعية',
    category: FeatureFlagCategory.operations,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Task management
  /// إدارة المهام
  taskManagement(
    key: 'task_management',
    nameEn: 'Task Management',
    nameAr: 'إدارة المهام',
    descriptionEn: 'Create and manage farm tasks and assignments',
    descriptionAr: 'إنشاء وإدارة مهام المزرعة والتعيينات',
    category: FeatureFlagCategory.operations,
    defaultEnabled: true,
    starterEnabled: true,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Field boundary editing
  /// تعديل حدود الحقل
  fieldBoundaryEditing(
    key: 'field_boundary_editing',
    nameEn: 'Field Boundary Editing',
    nameAr: 'تعديل حدود الحقل',
    descriptionEn: 'Draw and edit field boundaries on the map',
    descriptionAr: 'رسم وتعديل حدود الحقل على الخريطة',
    category: FeatureFlagCategory.operations,
    defaultEnabled: true,
    starterEnabled: true,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  // ═══════════════════════════════════════════════════════════════════════════
  // Premium Features - الميزات المميزة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Yield prediction
  /// التنبؤ بالإنتاج
  yieldPrediction(
    key: 'yield_prediction',
    nameEn: 'Yield Prediction',
    nameAr: 'التنبؤ بالإنتاج',
    descriptionEn: 'AI-based crop yield predictions',
    descriptionAr: 'توقعات إنتاج المحاصيل المعتمدة على الذكاء الاصطناعي',
    category: FeatureFlagCategory.premium,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: false,
    enterpriseEnabled: true,
  ),

  /// IoT sensor integration
  /// تكامل أجهزة استشعار IoT
  iotIntegration(
    key: 'iot_integration',
    nameEn: 'IoT Integration',
    nameAr: 'تكامل أجهزة الاستشعار',
    descriptionEn: 'Connect and monitor IoT sensors in your fields',
    descriptionAr: 'ربط ومراقبة أجهزة الاستشعار في حقولك',
    category: FeatureFlagCategory.premium,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Multi-farm management
  /// إدارة مزارع متعددة
  multiFarmManagement(
    key: 'multi_farm_management',
    nameEn: 'Multi-Farm Management',
    nameAr: 'إدارة مزارع متعددة',
    descriptionEn: 'Manage multiple farms from a single account',
    descriptionAr: 'إدارة مزارع متعددة من حساب واحد',
    category: FeatureFlagCategory.premium,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: false,
    enterpriseEnabled: true,
  ),

  /// Team collaboration
  /// التعاون الجماعي
  teamCollaboration(
    key: 'team_collaboration',
    nameEn: 'Team Collaboration',
    nameAr: 'التعاون الجماعي',
    descriptionEn: 'Invite team members and collaborate on farm management',
    descriptionAr: 'دعوة أعضاء الفريق والتعاون في إدارة المزرعة',
    category: FeatureFlagCategory.premium,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: true,
    enterpriseEnabled: true,
  ),

  /// Beta features access
  /// الوصول للميزات التجريبية
  betaFeatures(
    key: 'beta_features',
    nameEn: 'Beta Features',
    nameAr: 'الميزات التجريبية',
    descriptionEn: 'Access to experimental features before release',
    descriptionAr: 'الوصول إلى الميزات التجريبية قبل الإصدار',
    category: FeatureFlagCategory.premium,
    defaultEnabled: false,
    starterEnabled: false,
    professionalEnabled: false,
    enterpriseEnabled: true,
  );

  /// Unique key for this feature flag
  final String key;

  /// English name
  final String nameEn;

  /// Arabic name
  final String nameAr;

  /// English description
  final String descriptionEn;

  /// Arabic description
  final String descriptionAr;

  /// Category for grouping
  final FeatureFlagCategory category;

  /// Default enabled state (when no config is available)
  final bool defaultEnabled;

  /// Enabled for Starter package
  final bool starterEnabled;

  /// Enabled for Professional package
  final bool professionalEnabled;

  /// Enabled for Enterprise package
  final bool enterpriseEnabled;

  const FeatureFlag({
    required this.key,
    required this.nameEn,
    required this.nameAr,
    required this.descriptionEn,
    required this.descriptionAr,
    required this.category,
    required this.defaultEnabled,
    required this.starterEnabled,
    required this.professionalEnabled,
    required this.enterpriseEnabled,
  });

  /// Get localized name based on locale
  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  /// Get localized description based on locale
  String getDescription(String locale) =>
      locale == 'ar' ? descriptionAr : descriptionEn;

  /// Get enabled state for a specific package
  bool isEnabledForPackage(SubscriptionPackage package) {
    switch (package) {
      case SubscriptionPackage.starter:
        return starterEnabled;
      case SubscriptionPackage.professional:
        return professionalEnabled;
      case SubscriptionPackage.enterprise:
        return enterpriseEnabled;
      case SubscriptionPackage.free:
        return defaultEnabled;
    }
  }

  /// Find a feature flag by its key
  static FeatureFlag? fromKey(String key) {
    for (final flag in FeatureFlag.values) {
      if (flag.key == key) {
        return flag;
      }
    }
    return null;
  }

  /// Get all feature flags in a category
  static List<FeatureFlag> byCategory(FeatureFlagCategory category) {
    return FeatureFlag.values.where((f) => f.category == category).toList();
  }
}

/// Subscription package levels
/// مستويات باقات الاشتراك
enum SubscriptionPackage {
  free('free', 'Free', 'مجاني'),
  starter('starter', 'Starter', 'الأساسية'),
  professional('professional', 'Professional', 'الاحترافية'),
  enterprise('enterprise', 'Enterprise', 'المؤسسية');

  final String value;
  final String nameEn;
  final String nameAr;

  const SubscriptionPackage(this.value, this.nameEn, this.nameAr);

  String getName(String locale) => locale == 'ar' ? nameAr : nameEn;

  static SubscriptionPackage fromString(String value) {
    return SubscriptionPackage.values.firstWhere(
      (p) => p.value == value,
      orElse: () => SubscriptionPackage.free,
    );
  }
}

/// Feature flag value with metadata
/// قيمة علم الميزة مع البيانات الوصفية
class FeatureFlagValue {
  final FeatureFlag flag;
  final bool enabled;
  final DateTime? lastUpdated;
  final String? source; // 'remote', 'local', 'override', 'default'

  const FeatureFlagValue({
    required this.flag,
    required this.enabled,
    this.lastUpdated,
    this.source,
  });

  FeatureFlagValue copyWith({
    bool? enabled,
    DateTime? lastUpdated,
    String? source,
  }) {
    return FeatureFlagValue(
      flag: flag,
      enabled: enabled ?? this.enabled,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      source: source ?? this.source,
    );
  }

  Map<String, dynamic> toJson() => {
        'key': flag.key,
        'enabled': enabled,
        'lastUpdated': lastUpdated?.toIso8601String(),
        'source': source,
      };

  factory FeatureFlagValue.fromJson(Map<String, dynamic> json) {
    final flag = FeatureFlag.fromKey(json['key'] as String);
    if (flag == null) {
      throw ArgumentError('Unknown feature flag key: ${json['key']}');
    }
    return FeatureFlagValue(
      flag: flag,
      enabled: json['enabled'] as bool,
      lastUpdated: json['lastUpdated'] != null
          ? DateTime.parse(json['lastUpdated'] as String)
          : null,
      source: json['source'] as String?,
    );
  }
}
