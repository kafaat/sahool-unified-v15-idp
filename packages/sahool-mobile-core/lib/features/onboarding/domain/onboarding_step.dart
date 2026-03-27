/// SAHOOL Onboarding Step Model
/// نموذج خطوات الإعداد الأولي
///
/// Defines the different steps in the onboarding flow
/// يحدد الخطوات المختلفة في تدفق الإعداد الأولي
library;

/// Onboarding step types
/// أنواع خطوات الإعداد
enum OnboardingStepType {
  /// Welcome screen - شاشة الترحيب
  welcome,

  /// Features tour - جولة الميزات
  featuresTour,

  /// Permissions request - طلب الأذونات
  permissions,

  /// Profile setup - إعداد الملف الشخصي
  profileSetup,

  /// First field creation - إنشاء الحقل الأول
  firstField,

  /// Completion celebration - احتفال الانتهاء
  completion,
}

/// Feature item displayed in features tour
/// عنصر ميزة يُعرض في جولة الميزات
class OnboardingFeature {
  /// Feature identifier
  final String id;

  /// Feature title in Arabic
  final String titleAr;

  /// Feature title in English
  final String titleEn;

  /// Feature description in Arabic
  final String descriptionAr;

  /// Feature description in English
  final String descriptionEn;

  /// Icon for the feature
  final String iconAsset;

  /// Illustration asset path
  final String illustrationAsset;

  /// Primary color for the feature card
  final int colorValue;

  const OnboardingFeature({
    required this.id,
    required this.titleAr,
    required this.titleEn,
    required this.descriptionAr,
    required this.descriptionEn,
    required this.iconAsset,
    required this.illustrationAsset,
    required this.colorValue,
  });

  /// Get title based on locale
  String getTitle({bool isArabic = true}) => isArabic ? titleAr : titleEn;

  /// Get description based on locale
  String getDescription({bool isArabic = true}) =>
      isArabic ? descriptionAr : descriptionEn;
}

/// Permission item for permissions screen
/// عنصر إذن لشاشة الأذونات
class OnboardingPermission {
  /// Permission identifier
  final String id;

  /// Permission name in Arabic
  final String nameAr;

  /// Permission name in English
  final String nameEn;

  /// Permission description in Arabic
  final String descriptionAr;

  /// Permission description in English
  final String descriptionEn;

  /// Icon name for the permission
  final String iconName;

  /// Whether this permission is required
  final bool isRequired;

  /// Whether this permission has been granted
  final bool isGranted;

  const OnboardingPermission({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.descriptionAr,
    required this.descriptionEn,
    required this.iconName,
    this.isRequired = false,
    this.isGranted = false,
  });

  /// Get name based on locale
  String getName({bool isArabic = true}) => isArabic ? nameAr : nameEn;

  /// Get description based on locale
  String getDescription({bool isArabic = true}) =>
      isArabic ? descriptionAr : descriptionEn;

  /// Create a copy with updated granted status
  OnboardingPermission copyWith({bool? isGranted}) {
    return OnboardingPermission(
      id: id,
      nameAr: nameAr,
      nameEn: nameEn,
      descriptionAr: descriptionAr,
      descriptionEn: descriptionEn,
      iconName: iconName,
      isRequired: isRequired,
      isGranted: isGranted ?? this.isGranted,
    );
  }
}

/// Predefined features for the tour
/// الميزات المحددة مسبقاً للجولة
class OnboardingFeatures {
  static const List<OnboardingFeature> features = [
    OnboardingFeature(
      id: 'field_management',
      titleAr: 'إدارة الحقول',
      titleEn: 'Field Management',
      descriptionAr: 'ارسم حقولك على الخريطة وتتبع كل التفاصيل من مكان واحد',
      descriptionEn:
          'Draw your fields on the map and track all details from one place',
      iconAsset: 'assets/icons/field.svg',
      illustrationAsset: 'assets/illustrations/field_illustration.svg',
      colorValue: 0xFF4CAF50,
    ),
    OnboardingFeature(
      id: 'weather',
      titleAr: 'الطقس الزراعي',
      titleEn: 'Agricultural Weather',
      descriptionAr:
          'توقعات طقس دقيقة مخصصة لحقولك مع تنبيهات الصقيع والحرارة',
      descriptionEn:
          'Precise weather forecasts customized for your fields with frost and heat alerts',
      iconAsset: 'assets/icons/weather.svg',
      illustrationAsset: 'assets/illustrations/weather_illustration.svg',
      colorValue: 0xFF2196F3,
    ),
    OnboardingFeature(
      id: 'ndvi',
      titleAr: 'صحة المحصول',
      titleEn: 'Crop Health',
      descriptionAr: 'راقب صحة محاصيلك بالأقمار الصناعية واكتشف المشاكل مبكراً',
      descriptionEn:
          'Monitor your crop health via satellite and detect problems early',
      iconAsset: 'assets/icons/ndvi.svg',
      illustrationAsset: 'assets/illustrations/ndvi_illustration.svg',
      colorValue: 0xFF8BC34A,
    ),
    OnboardingFeature(
      id: 'irrigation',
      titleAr: 'الري الذكي',
      titleEn: 'Smart Irrigation',
      descriptionAr: 'احصل على توصيات ري دقيقة بناءً على رطوبة التربة والطقس',
      descriptionEn:
          'Get precise irrigation recommendations based on soil moisture and weather',
      iconAsset: 'assets/icons/irrigation.svg',
      illustrationAsset: 'assets/illustrations/irrigation_illustration.svg',
      colorValue: 0xFF00BCD4,
    ),
    OnboardingFeature(
      id: 'tasks',
      titleAr: 'المهام الزراعية',
      titleEn: 'Farm Tasks',
      descriptionAr: 'نظّم عملياتك الزراعية وتابع تنفيذها مع فريقك',
      descriptionEn:
          'Organize your farming operations and track execution with your team',
      iconAsset: 'assets/icons/tasks.svg',
      illustrationAsset: 'assets/illustrations/task_illustration.svg',
      colorValue: 0xFFFF9800,
    ),
  ];
}

/// Predefined permissions for the onboarding
/// الأذونات المحددة مسبقاً للإعداد
class OnboardingPermissions {
  static const List<OnboardingPermission> permissions = [
    OnboardingPermission(
      id: 'location',
      nameAr: 'الموقع الجغرافي',
      nameEn: 'Location',
      descriptionAr: 'لتحديد موقعك في الحقل ورسم الحدود بدقة',
      descriptionEn:
          'To determine your location in the field and draw boundaries accurately',
      iconName: 'location_on',
      isRequired: true,
    ),
    OnboardingPermission(
      id: 'notifications',
      nameAr: 'الإشعارات',
      nameEn: 'Notifications',
      descriptionAr: 'لتلقي تنبيهات الطقس والمهام والتوصيات المهمة',
      descriptionEn:
          'To receive weather alerts, tasks, and important recommendations',
      iconName: 'notifications',
      isRequired: false,
    ),
    OnboardingPermission(
      id: 'camera',
      nameAr: 'الكاميرا',
      nameEn: 'Camera',
      descriptionAr: 'لتصوير المحاصيل وتشخيص الأمراض والآفات',
      descriptionEn: 'To photograph crops and diagnose diseases and pests',
      iconName: 'camera_alt',
      isRequired: false,
    ),
  ];
}
