import 'package:flutter/material.dart';

/// Navigation constants for SAHOOL app
/// ثوابت التنقل لتطبيق سهول
class NavigationConstants {
  NavigationConstants._();

  // ═══════════════════════════════════════════════════════════════════════
  // Route Names
  // ═══════════════════════════════════════════════════════════════════════

  // Auth & Onboarding
  static const String splash = '/splash';
  static const String roleSelection = '/role-selection';
  static const String login = '/login';

  // Main Tabs
  static const String home = '/home';
  static const String fields = '/fields';
  static const String monitor = '/monitor';
  static const String market = '/market';
  static const String profile = '/profile';

  // VRA (Variable Rate Application)
  static const String vra = '/vra';
  static const String vraDetail = '/vra/:id';
  static const String vraCreate = '/vra/create';

  // GDD (Growing Degree Days)
  static const String gdd = '/gdd';
  static const String gddChart = '/gdd/:fieldId';
  static const String gddSettings = '/gdd/settings';

  // Spray Timing
  static const String spray = '/spray';
  static const String sprayCalendar = '/spray/calendar';
  static const String sprayLog = '/spray/log';

  // Crop Rotation
  static const String rotation = '/rotation';
  static const String rotationPlan = '/rotation/:fieldId';
  static const String rotationCompatibility = '/rotation/compatibility';

  // Profitability
  static const String profitability = '/profitability';
  static const String profitabilityDetail = '/profitability/:fieldId';
  static const String profitabilitySeason = '/profitability/season';

  // Inventory
  static const String inventory = '/inventory';
  static const String inventoryDetail = '/inventory/:id';
  static const String inventoryAdd = '/inventory/add';

  // Chat / AI Advisor
  static const String chat = '/chat';
  static const String chatConversation = '/chat/:conversationId';

  // Satellite Imagery
  static const String satellite = '/satellite';
  static const String satelliteField = '/satellite/:fieldId';
  static const String satelliteNdvi = '/satellite/ndvi';
  static const String satellitePhenology = '/satellite/phenology';
  static const String satelliteWeather = '/satellite/weather';

  // Field Management
  static const String fieldDetail = '/field/:id';
  static const String fieldDashboard = '/field/:id/dashboard';
  static const String fieldMap = '/map';

  // Other Features
  static const String alerts = '/alerts';
  static const String weather = '/weather';
  static const String tasks = '/tasks';
  static const String cropHealth = '/crop-health';
  static const String notifications = '/notifications';
  static const String settings = '/settings';
  static const String sync = '/sync';
  static const String advisor = '/advisor';
  static const String scanner = '/scanner';
  static const String scouting = '/scouting';

  // Utility Routes
  static const String help = '/help';
  static const String about = '/about';

  // ═══════════════════════════════════════════════════════════════════════
  // Arabic Labels
  // ═══════════════════════════════════════════════════════════════════════

  static const Map<String, String> arabicLabels = {
    // Main Navigation
    'home': 'الرئيسية',
    'fields': 'حقولي',
    'monitor': 'المراقبة',
    'market': 'السوق',
    'profile': 'حسابي',
    'more': 'المزيد',

    // Precision Agriculture Features
    'vra': 'التسميد المتغير',
    'vra_short': 'VRA',
    'gdd': 'درجات النمو',
    'gdd_short': 'GDD',
    'spray': 'الرش الذكي',
    'rotation': 'الدورة الزراعية',
    'profitability': 'الربحية',

    // Management Features
    'inventory': 'المخزون',
    'chat': 'المستشار الذكي',
    'satellite': 'الأقمار الصناعية',
    'weather': 'الطقس',
    'tasks': 'المهام',
    'crop_health': 'صحة المحاصيل',

    // Navigation Items
    'alerts': 'التنبيهات',
    'notifications': 'الإشعارات',
    'settings': 'الإعدادات',
    'help': 'المساعدة',
    'about': 'حول التطبيق',
    'logout': 'تسجيل الخروج',
    'sync': 'المزامنة',

    // Feature Categories
    'precision_agriculture': 'الزراعة الدقيقة',
    'field_management': 'إدارة الحقول',
    'monitoring': 'المراقبة والتحليل',
    'resources': 'الموارد',
    'ai_tools': 'أدوات الذكاء الاصطناعي',
    'utilities': 'أدوات مساعدة',

    // Feature Descriptions
    'vra_desc': 'تطبيق متغير للأسمدة حسب احتياج كل منطقة',
    'gdd_desc': 'تتبع درجات النمو الحرارية للمحاصيل',
    'spray_desc': 'جدولة الرش في الأوقات المثالية',
    'rotation_desc': 'تخطيط الدورة الزراعية',
    'profitability_desc': 'تحليل الربحية والتكاليف',
    'inventory_desc': 'إدارة المخزون والمدخلات',
    'chat_desc': 'استشارة ذكية فورية',
    'satellite_desc': 'صور الأقمار الصناعية والتحليل',

    // Common Actions
    'create': 'إنشاء',
    'view': 'عرض',
    'edit': 'تعديل',
    'delete': 'حذف',
    'save': 'حفظ',
    'cancel': 'إلغاء',
    'back': 'رجوع',
    'next': 'التالي',
    'done': 'تم',
  };

  // ═══════════════════════════════════════════════════════════════════════
  // Feature Icons
  // ═══════════════════════════════════════════════════════════════════════

  static const Map<String, IconData> featureIcons = {
    // Main Navigation
    'home': Icons.home_rounded,
    'fields': Icons.landscape_rounded,
    'monitor': Icons.analytics_rounded,
    'market': Icons.storefront_rounded,
    'profile': Icons.person_rounded,

    // Precision Agriculture
    'vra': Icons.grain_rounded,
    'gdd': Icons.thermostat_rounded,
    'spray': Icons.opacity_rounded,
    'rotation': Icons.cached_rounded,
    'profitability': Icons.trending_up_rounded,

    // Management
    'inventory': Icons.inventory_2_rounded,
    'chat': Icons.chat_bubble_rounded,
    'satellite': Icons.satellite_alt_rounded,
    'weather': Icons.wb_sunny_rounded,
    'tasks': Icons.checklist_rounded,
    'crop_health': Icons.eco_rounded,

    // Utilities
    'alerts': Icons.notifications_active_rounded,
    'notifications': Icons.notifications_rounded,
    'settings': Icons.settings_rounded,
    'help': Icons.help_rounded,
    'about': Icons.info_rounded,
    'logout': Icons.logout_rounded,
    'sync': Icons.sync_rounded,
    'map': Icons.map_rounded,
    'scanner': Icons.qr_code_scanner_rounded,
    'advisor': Icons.psychology_rounded,
    'scouting': Icons.visibility_rounded,
  };

  // ═══════════════════════════════════════════════════════════════════════
  // Feature Colors
  // ═══════════════════════════════════════════════════════════════════════

  static const Map<String, Color> featureColors = {
    'vra': Color(0xFF4CAF50), // Green
    'gdd': Color(0xFFFF9800), // Orange
    'spray': Color(0xFF2196F3), // Blue
    'rotation': Color(0xFF9C27B0), // Purple
    'profitability': Color(0xFF4CAF50), // Green
    'inventory': Color(0xFF607D8B), // Blue Grey
    'chat': Color(0xFF00BCD4), // Cyan
    'satellite': Color(0xFF3F51B5), // Indigo
    'weather': Color(0xFFFFC107), // Amber
    'tasks': Color(0xFFE91E63), // Pink
    'crop_health': Color(0xFF8BC34A), // Light Green
  };

  // ═══════════════════════════════════════════════════════════════════════
  // Feature Groups for Navigation Drawer
  // ═══════════════════════════════════════════════════════════════════════

  static const List<FeatureGroup> featureGroups = [
    FeatureGroup(
      title: 'precision_agriculture',
      icon: Icons.agriculture_rounded,
      features: ['vra', 'gdd', 'spray', 'rotation', 'profitability'],
    ),
    FeatureGroup(
      title: 'field_management',
      icon: Icons.landscape_rounded,
      features: ['fields', 'tasks', 'crop_health', 'satellite'],
    ),
    FeatureGroup(
      title: 'monitoring',
      icon: Icons.monitoring_rounded,
      features: ['weather', 'alerts', 'map'],
    ),
    FeatureGroup(
      title: 'resources',
      icon: Icons.business_center_rounded,
      features: ['inventory', 'market'],
    ),
    FeatureGroup(
      title: 'ai_tools',
      icon: Icons.psychology_rounded,
      features: ['chat', 'advisor', 'scanner', 'scouting'],
    ),
  ];

  // Helper method to get label
  static String getLabel(String key) => arabicLabels[key] ?? key;

  // Helper method to get icon
  static IconData getIcon(String key) => featureIcons[key] ?? Icons.circle;

  // Helper method to get color
  static Color getColor(String key) => featureColors[key] ?? const Color(0xFF2E7D32);
}

/// Feature Group for organizing features in drawer
class FeatureGroup {
  final String title;
  final IconData icon;
  final List<String> features;

  const FeatureGroup({
    required this.title,
    required this.icon,
    required this.features,
  });
}

/// Feature Item for grid and lists
class FeatureItem {
  final String key;
  final String route;
  final String? badge;

  const FeatureItem({
    required this.key,
    required this.route,
    this.badge,
  });

  String get label => NavigationConstants.getLabel(key);
  IconData get icon => NavigationConstants.getIcon(key);
  Color get color => NavigationConstants.getColor(key);
  String? get description => NavigationConstants.arabicLabels['${key}_desc'];
}
